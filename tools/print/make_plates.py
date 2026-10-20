"""Print plates for JX0 on the builder's two printers, sliced and ready to send:

    Bambu Lab P1S (256 x 256 mm, Bambu Studio)      -> jx0/print/P1S/<plate>.gcode.3mf
    Creality SPARKX i7 (260 x 260 mm, Creality Print) -> jx0/print/i7/<plate>.gcode (+ .3mf project)

Every part is the SolidWorks STL with its lettering (jx0/cad/stl_engraved, from jx0/cad/engrave.py), turned to the side the build guide prints it on. The slicer arranges
each plate. Settings are the printer's own system profiles (inheritance resolved here, because the slicers' command
lines do not resolve it) with the build guide's on top:
    PETG (pelvis, leg parts, shims): 0.2 mm layers, 6 walls, 6 top and 6 bottom layers, 40 % gyroid, 240 C / 80 C
    PETG-body (body, head, arms):    0.2 mm layers, 3 walls, 25 % gyroid, 240 C / 80 C (PLA: the same at 210 C / 60 C)
    tree supports wherever the part overhangs, a brim on PETG plates.

    python tools/print/make_plates.py            (all plates)
    python tools/print/make_plates.py P1S-0      (one plate)
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
STL = ROOT / "jx0" / "cad" / "stl_engraved"          # the SolidWorks STLs with the lettering (jx0/cad/engrave.py)
OUT = ROOT / "jx0" / "print"
BAMBU = Path(r"D:\Program Files\Bambu Studio")
CREALITY = Path(r"C:\Program Files\Creality\Creality Print 7.3")

# the side each part goes down on (a unit vector in the part's own frame), from the build guide's print table
DOWN = {"JX0_Pelvis": (0, 0, 1), "JX0_YawKeeper_L": (0, 0, 1), "JX0_YawKeeper_R": (0, 0, 1),
        "JX0_YawRing_L": (0, 0, -1), "JX0_YawRing_R": (0, 0, -1),
        "JX0_HipYawBracket_L": (0, 0, 1), "JX0_HipYawBracket_R": (0, 0, 1),
        "JX0_HipRollBracket_L": (-1, 0, 0), "JX0_HipRollBracket_R": (-1, 0, 0),
        "JX0_Thigh_L": (0, 1, 0), "JX0_Thigh_R": (0, -1, 0), "JX0_Shin_L": (0, 1, 0), "JX0_Shin_R": (0, -1, 0),
        "JX0_AnkleBracket_L": (0, 1, 0), "JX0_AnkleBracket_R": (0, -1, 0), "JX0_Foot": (0, 0, -1),
        "JX0_HornShim": (0, 0, -1), "JX0_Torso": (0, 0, -1), "JX0_ChestCap": (0, 0, 1), "JX0_Head": (0, 0, -1), "JX0_EyeLens": (-1, 0, 0), "JX0_CamClamp": (-1, 0, 0),
        "JX0_NeckHub": (0, 0, -1), "JX0_UpperArm_L": (0, -1, 0), "JX0_UpperArm_R": (0, 1, 0),
        "JX0_ArmBlade_L": (0, -1, 0), "JX0_ArmBlade_R": (0, 1, 0)}

# plate -> (printer, material, [(part, count)])
PLATES = {
    # i7: red PETG - the pelvis and every leg part (strength: verify_fea's PETG)
    "i7-1_pelvis_hip_yaw": ("i7", "PETG", [("JX0_Pelvis", 1), ("JX0_HipYawBracket_L", 1), ("JX0_HipYawBracket_R", 1),
                                           ("JX0_YawKeeper_L", 1), ("JX0_YawKeeper_R", 1), ("JX0_YawRing_L", 1),
                                           ("JX0_YawRing_R", 1), ("JX0_Shin_L", 1), ("JX0_Shin_R", 1)]),   # + both shins
    "i7-2_legs": ("i7", "PETG", [("JX0_Thigh_L", 1), ("JX0_Thigh_R", 1), ("JX0_AnkleBracket_L", 1),
                                 ("JX0_AnkleBracket_R", 1), ("JX0_Foot", 2), ("JX0_HipRollBracket_L", 1),
                                 ("JX0_HipRollBracket_R", 1)]),                  # every red part left, one plate
    "i7-3_eye_lenses": ("i7", "PETG-body", [("JX0_EyeLens", 2)]),             # clear PETG: swap the filament for it
    "i7-4_shims_optional": ("i7", "PETG", [("JX0_HornShim", 40)]),   # only if a bracket sits loose on its horn
    # P1S: white PLA - the body, head and arms
    "P1S-1_torso_head": ("P1S", "PLA", [("JX0_Torso", 1), ("JX0_Head", 1), ("JX0_NeckHub", 1), ("JX0_CamClamp", 1)]),
    "P1S-2_chest_arms": ("P1S", "PLA", [("JX0_ChestCap", 1), ("JX0_UpperArm_L", 1), ("JX0_UpperArm_R", 1),
                                        ("JX0_ArmBlade_L", 1), ("JX0_ArmBlade_R", 1)]),   # printed 2026-10-20 (its flat camera
    #                                                                       clamp is replaced by the cradle on P1S-1)
}

PROFILES = {
    "P1S": dict(dir=BAMBU / "resources" / "profiles" / "BBL", machine="machine/Bambu Lab P1S 0.4 nozzle.json",
                process="process/0.20mm Standard @BBL X1C.json",
                filament={"PETG": "filament/Generic PETG.json", "PLA": "filament/Generic PLA.json"}),
    # the i7 is sliced in Bambu Studio on its Klipper Creality base (K1C), with the i7's bed, G-code and limits copied
    # from Creality Print's own SPARKX i7 profile (I7_FROM)
    "i7": dict(dir=BAMBU / "resources" / "profiles" / "Creality", machine="machine/Creality K1C 0.4 nozzle.json",
               process="process/0.20mm Standard @Creality Ender3V3KE.json",
               filament={"PETG": "filament/Generic PETG @Creality.json", "PLA": "filament/Generic PLA @Creality.json"}),
}
I7_PROFILE = CREALITY / "resources" / "profiles" / "Creality" / "machine"
# the i7's start / end G-code from its Creality Print profile, with the placeholders Bambu Studio does not know replaced by
# fixed values (one filament: slot 1 if the CFS is fitted); START_PRINT / END_PRINT are the i7's own Klipper macros
I7_START = """M140 S0
M104 S0
START_PRINT EXTRUDER_TEMP=[nozzle_temperature_initial_layer] BED_TEMP=[bed_temperature_initial_layer_single]
M83
M8200 P S0
M220 S100
SET_VELOCITY_LIMIT ACCEL=5000 ACCEL_TO_DECEL=5000
G0 X267 F18000
G0 X278 F2400
M104 S[nozzle_temperature_initial_layer]
M106 S0
T0
M8200 O
M204 S2000
G1 Z3 F600
M83
G1 Y0 F12000
G1 X150 F30000
G1 Z0.2 F600
G1 X120 Y0 E15 F240
G1 X115 E.3742 F1000
G1 X110 E.3742 F4000
G1 X105 E.3742 F1000
G1 X100 E.3742 F4000
G1 X95 E.3742 F1000
G91
G1 X-1 Z-0.3
G1 X-4
G90
G92 E0
"""
I7_END = """G1 E-0.8 F2400 ; retract
G91
G1 Z3 F600 ; lift
G90
G92 E0
G1 X0 Y180 F8000
END_PRINT
"""
I7_FROM = ("printable_area", "printable_height", "gcode_flavor",
           "machine_max_speed_x", "machine_max_speed_y", "machine_max_speed_z", "machine_max_speed_e",
           "machine_max_acceleration_x", "machine_max_acceleration_y", "machine_max_acceleration_z",
           "machine_max_acceleration_e", "machine_max_acceleration_extruding", "machine_max_acceleration_retracting",
           "retraction_length", "retraction_speed", "deretraction_speed", "z_hop", "nozzle_diameter")
PROCESS = {
    "PETG": {"layer_height": "0.2", "wall_loops": "6", "top_shell_layers": "6", "bottom_shell_layers": "6",
             "sparse_infill_density": "40%", "sparse_infill_pattern": "gyroid", "brim_type": "auto_brim"},
    "PLA": {"layer_height": "0.2", "wall_loops": "3", "top_shell_layers": "4", "bottom_shell_layers": "4",
            "sparse_infill_density": "25%", "sparse_infill_pattern": "gyroid"},
}
# body parts (torso, head, chest, arms, lenses) in PETG: the PLA shell (3 walls, 25 %) at PETG's temperatures
PROCESS["PETG-body"] = {**PROCESS["PLA"], "brim_type": "auto_brim"}
SUPPORT = {"enable_support": "1", "support_type": "tree(auto)", "support_threshold_angle": "40",
           "support_on_build_plate_only": "0"}
FILAMENT = {"PETG": {"nozzle_temperature": ["240"], "nozzle_temperature_initial_layer": ["240"],
                     "cool_plate_temp": ["80"], "cool_plate_temp_initial_layer": ["80"],
                     "hot_plate_temp": ["80"], "hot_plate_temp_initial_layer": ["80"],
                     "textured_plate_temp": ["80"], "textured_plate_temp_initial_layer": ["80"]},
            "PLA": {"nozzle_temperature": ["210"], "nozzle_temperature_initial_layer": ["215"],
                    "cool_plate_temp": ["60"], "cool_plate_temp_initial_layer": ["60"],
                    "hot_plate_temp": ["60"], "hot_plate_temp_initial_layer": ["60"],
                    "textured_plate_temp": ["60"], "textured_plate_temp_initial_layer": ["60"]}}
FILAMENT["PETG-body"] = FILAMENT["PETG"]


def resolve(path: Path, kind_dir: Path) -> dict:
    """A system profile with its whole 'inherits' chain merged (the parent first), then its 'include' templates (the
    Bambu printers' real start / end / layer-change G-code lives in those), then its own keys."""
    d = json.loads(path.read_text(encoding="utf-8"))
    parent = d.get("inherits")
    base = resolve(kind_dir / f"{parent}.json", kind_dir) if parent else {}
    for inc in d.get("include", []):
        base.update({k: v for k, v in resolve(kind_dir / f"{inc}.json", kind_dir).items()
                     if k not in ("name", "instantiation")})
    base.update({k: v for k, v in d.items() if k not in ("inherits", "include")})
    return base


def settings(printer, material, work: Path, plate=""):
    """Resolved machine / process / filament JSONs for the slicer command line."""
    pr = PROFILES[printer]
    mach = resolve(pr["dir"] / pr["machine"], pr["dir"] / "machine")
    if printer == "i7":
        i7 = resolve(I7_PROFILE / "SPARKX i7 0.4 nozzle.json", I7_PROFILE)
        mach.update({k: i7[k] for k in I7_FROM if k in i7})
        mach["machine_start_gcode"], mach["machine_end_gcode"] = I7_START, I7_END
        mach["name"] = "SPARKX i7 0.4 nozzle (from Creality Print 7.3)"
    proc = resolve(pr["dir"] / pr["process"], pr["dir"] / "process")
    fil = resolve(pr["dir"] / pr["filament"][material.split("-")[0]], pr["dir"] / "filament")
    proc.update(PROCESS[material])
    proc.update(SUPPORT)
    proc["curr_bed_type"] = "Textured PEI Plate"                     # the PEI plates both printers ship with
    if any(part == "JX0_HornShim" for part, _ in PLATES[plate][2]):
        proc["brim_type"] = "no_brim"                                # (0.4 mm discs: a brim would only crowd them)
    fil.update(FILAMENT[material])
    names = (mach.get("name", "machine"), proc.get("name", "process"), fil.get("name", "filament"))
    proc["compatible_printers"], fil["compatible_printers"] = [names[0]], [names[0]]
    files = []
    for d, kind in ((mach, "machine"), (proc, "process"), (fil, "filament")):
        f = work / f"{kind}.json"
        f.write_text(json.dumps(d, indent=1), encoding="utf-8")
        files.append(f)
    return files


def oriented(part):
    """The part's STL turned so its print face is down, sitting on z = 0."""
    m = trimesh.load(STL / f"{part}.stl")
    down = np.asarray(DOWN[part], float)
    R = trimesh.geometry.align_vectors(down, [0.0, 0.0, -1.0])
    m.apply_transform(R)
    m.apply_translation(-m.bounds[0])
    return m


BED = {"P1S": 256.0, "i7": 260.0}
GAP, MARGIN = 8.0, 6.0                                               # between parts (brims) and from the bed's edge


def pack(meshes, bed):
    """Shelf packing (below); when that does not fit, bottom-left packing (pack_bl). Raises if neither fits."""
    try:
        return pack_shelf([(n, m.copy()) for n, m in meshes], bed)
    except ValueError:
        return pack_bl(meshes, bed)


def pack_bl(meshes, bed):
    """Bottom-left packing of the parts' footprints: each part, in turn and turned 0 or 90 deg, goes to the lowest then
    leftmost free spot next to the parts already placed; several part orders are tried."""
    usable = bed - 2 * MARGIN
    orders = [lambda e: -(e[0] * e[1]), lambda e: -max(e), lambda e: -e[1], lambda e: -e[0]]
    for key in orders:
        items = sorted(meshes, key=lambda nm: key(nm[1].extents[:2]))
        placed, out, ok = [], [], True
        for name, m in items:
            best = None
            for turn in (False, True):
                w, d = (m.extents[1], m.extents[0]) if turn else (m.extents[0], m.extents[1])
                cands = [(0.0, 0.0)] + [(x + pw + GAP, y) for x, y, pw, pd in placed] +                         [(x, y + pd + GAP) for x, y, pw, pd in placed]
                for cx, cy in cands:
                    if cx + w > usable + 1e-6 or cy + d > usable + 1e-6:
                        continue
                    if any(cx < x + pw + GAP - 1e-6 and x < cx + w + GAP - 1e-6 and cy < y + pd + GAP - 1e-6 and
                           y < cy + d + GAP - 1e-6 for x, y, pw, pd in placed):
                        continue
                    if best is None or (cy, cx) < (best[1], best[0]):
                        best = (cx, cy, w, d, turn)
            if best is None:
                ok = False
                break
            cx, cy, w, d, turn = best
            mm = m.copy()
            if turn:
                mm.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 0, 1]))
            mm.apply_translation([MARGIN + cx - mm.bounds[0][0], MARGIN + cy - mm.bounds[0][1], -mm.bounds[0][2]])
            placed.append((cx, cy, w, d))
            out.append((name, mm))
        if ok:
            return out
    raise ValueError(f"{', '.join(n for n, _ in meshes)} do not fit the {bed:.0f} mm bed together")


def pack_shelf(meshes, bed):
    """Shelf packing, largest footprint first: rows along x, each part turned 90 deg if that fits the row better.
    Returns the meshes moved into place; raises if the plate does not fit the bed."""
    usable = bed - 2 * MARGIN
    items = sorted(meshes, key=lambda nm: -(nm[1].extents[0] * nm[1].extents[1]))
    x = y = row_h = 0.0
    out = []
    for name, m in items:
        w, d = m.extents[0], m.extents[1]
        if (w > usable or x + w > usable) and d <= usable and x + d <= usable and w <= usable:
            pass
        if x + w > usable and x + d <= usable and w <= row_h + 1e-6:      # fits the row turned
            m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 0, 1]))
            w, d = d, w
        if x + w > usable:                                                # next row
            x, y, row_h = 0.0, y + row_h + GAP, 0.0
        if x + w > usable or y + d > usable:
            raise ValueError(f"{name} does not fit the {bed:.0f} mm bed")
        m.apply_translation([MARGIN + x - m.bounds[0][0], MARGIN + y - m.bounds[0][1], -m.bounds[0][2]])
        out.append((name, m))
        x += w + GAP
        row_h = max(row_h, d)
    return out


def make_plate(name):
    printer, material, items = PLATES[name]
    work = OUT / printer / name
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True, exist_ok=True)
    meshes = []
    for part, n in items:
        m = oriented(part)
        meshes += [(f"{part}{'' if n == 1 else f'_{k + 1:02d}'}", m.copy()) for k in range(n)]
    layout = pack(meshes, BED[printer])
    plate = trimesh.util.concatenate([m for _, m in layout])
    c = (plate.bounds[0] + plate.bounds[1]) / 2                     # centred on the bed
    plate.apply_translation([BED[printer] / 2 - c[0], BED[printer] / 2 - c[1], 0.0])
    stl = work / f"{name}.stl"                                       # the whole plate, laid out, as one object
    plate.export(stl)
    stls = [stl]
    mach, proc, fil = settings(printer, material, work, name)
    exe = BAMBU / "bambu-studio.exe"          # Creality Print 7.3 has no command-line slicer: the i7 plates are sliced
    out = work / f"{name}.gcode.3mf"         # by Bambu Studio with the i7's own Creality Print profiles
    cmd = [str(exe), "--load-settings", f"{mach};{proc}", "--load-filaments", str(fil), "--arrange", "0",
           "--allow-rotations", "--orient", "0", "--slice", "0", "--export-3mf", out.name, "--outputdir", str(work)] + [str(s) for s in stls]
    r = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=1800)
    res = work / "result.json"
    info = json.loads(res.read_text(encoding="utf-8")) if res.exists() else {"error_string": f"no result (exit {r.returncode})"}
    for f in (mach, proc, fil):
        f.unlink()
    g = work / "plate_1.gcode"                                       # plain G-code, for the i7 (USB or Creality Print)
    if g.exists():
        g.replace(work / f"{name}.gcode")
    return info


def summary(name, info):
    plates = info.get("sliced_plates") or []
    t = sum(p.get("total_predication", 0) for p in plates) / 3600
    g = sum(f.get("total_used_g", 0) for p in plates for f in p.get("filaments", []))
    warn = "; ".join(p.get("warning_message", "") for p in plates if p.get("warning_message"))
    return f"{name:24s} {info.get('error_string', '?'):10s} {t:5.1f} h  {g:6.1f} g  {warn}"


def main():
    names = sys.argv[1:] or list(PLATES)
    for n in names:
        info = make_plate(n)
        print(summary(n, info), flush=True)


if __name__ == "__main__":
    main()
