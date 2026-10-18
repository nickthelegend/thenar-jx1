"""Check the sliced JX0 print plates before printing (run after make_plates.py):

    python tools/print/verify_plates.py      -> jx0/print/verify_plates.json

- every printed part of the build guide's table is on a plate, in the guide's quantity, and in the material it says;
- each part lies on a flat face (enough area on the bed, its centre of mass over that area) and its supported area;
- each plate fits its bed and no two parts touch;
- the G-code: material, temperatures, layer height, walls / infill / supports, every extruding move inside the bed,
  height inside the printer, and every part printed from its first layer to its top (nothing dropped by the slicer);
- the P1S G-code starts with Bambu's own P1S start G-code and its .gcode.3mf holds the same G-code; the i7 G-code uses
  its own START_PRINT / END_PRINT macros and no Bambu-only commands.
"""
from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import MultiPoint

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_plates as mp  # noqa: E402

GUIDE = ROOT / "jx0" / "docs" / "build_guide.md"
SUPPORT_ANGLE = 40.0           # the slicer's tree-support threshold, degrees from horizontal
MIN_CONTACT = 50.0             # mm^2 on the bed (the shims are 300 mm^2)


def guide_parts():
    """{part: (quantity, material)} from the build guide's print table."""
    out = {}
    for line in GUIDE.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| (JX0_\w+)( / _R)?[^|]*\| ([\d +]+) \|[^|]*\|[^|]*\| (PETG|PLA)", line)
        if not m:
            continue
        name, pair, qty, mat = m.group(1), m.group(2), m.group(3), m.group(4)
        n = sum(int(x) for x in qty.split("+"))
        if pair:
            base = name[:-2]
            out[base + "_L"], out[base + "_R"] = (n // 2, mat), (n // 2, mat)
        else:
            out[name] = (n, mat)
    return out


def orientation(part):
    """Area on the bed, centre of mass over it, and the area that needs support, for the plate's orientation."""
    m = mp.oriented(part)
    n, a, c = m.face_normals, m.area_faces, m.triangles_center
    on_bed = (n[:, 2] < -0.999) & (c[:, 2] < 0.05)
    contact = float(a[on_bed].sum())
    pts = m.triangles[on_bed].reshape(-1, 3)[:, :2]
    hull = MultiPoint([tuple(p) for p in pts]).convex_hull if len(pts) >= 3 else None
    com = m.center_mass if m.is_watertight else m.centroid
    stable = bool(hull is not None and hull.buffer(0.01).contains(MultiPoint([tuple(com[:2])]).centroid))
    down = (n[:, 2] < -np.sin(np.radians(SUPPORT_ANGLE))) & ~on_bed
    return dict(contact_mm2=round(contact, 1), com_over_contact=stable, supported_mm2=round(float(a[down].sum()), 1),
                height_mm=round(float(m.extents[2]), 2), watertight=bool(m.is_watertight),
                volume_cm3=round(float(m.volume) / 1000, 2))


def bodies(stl):
    m = trimesh.load(stl)
    parts = m.split(only_watertight=False)
    return sorted(parts, key=lambda b: (round(b.bounds[0][1]), round(b.bounds[0][0])))


def footprint(b):
    return MultiPoint([tuple(p) for p in b.vertices[:, :2]]).convex_hull


def parse_gcode(path):
    """Extruding moves (x, y, z), commands and the config block of a Bambu Studio G-code file."""
    cfg, xyz, cmds = {}, [], []
    x = y = z = 0.0
    e_rel = True
    absolute = True
    in_cfg = False
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith(";"):
                if "MACHINE_START_GCODE_END" in line:
                    cmds.append("#START_GCODE_END")
                if "CONFIG_BLOCK_START" in line:
                    in_cfg = True
                elif "CONFIG_BLOCK_END" in line:
                    in_cfg = False
                elif in_cfg and " = " in line:
                    k, v = line[2:].rstrip("\n").split(" = ", 1)
                    cfg[k] = v
                continue
            code = line.split(";", 1)[0].strip()
            if not code:
                continue
            w = code.split()
            c = w[0]
            if c == "G90":
                absolute = True
            elif c == "G91":
                absolute = False
            elif c in ("G0", "G1", "G2", "G3"):
                v = {t[0]: float(t[1:]) for t in w[1:] if t[0] in "XYZEF" and len(t) > 1}
                if absolute:
                    x, y, z = v.get("X", x), v.get("Y", y), v.get("Z", z)
                else:
                    x, y, z = x + v.get("X", 0), y + v.get("Y", 0), z + v.get("Z", 0)
                if v.get("E", 0) > 0 and ("X" in v or "Y" in v):
                    xyz.append((x, y, z))
            else:
                cmds.append(code)
    return cfg, np.array(xyz), cmds


def temps(cmds):
    """Temperatures the part prints at: the setpoints in effect when the start G-code ends and every one after it (the
    printer's own warm-up, probing and flush temperatures inside the start G-code are left out)."""
    out = {"nozzle": set(), "bed": set()}
    last = {"nozzle": None, "bed": None}
    started = "#START_GCODE_END" not in cmds
    for c in cmds:
        if c == "#START_GCODE_END":
            started = True
            out = {k: ({v} if v else set()) for k, v in last.items()}
            continue
        w = c.split()
        s = {t[0]: t[1:] for t in w[1:] if t}
        for key, codes in (("nozzle", ("M104", "M109")), ("bed", ("M140", "M190"))):
            if w[0] in codes and "S" in s:
                v = float(s["S"].rstrip(";"))
                if v > 0:
                    last[key] = v
                    if started:
                        out[key].add(v)
        if w[0] == "START_PRINT":
            kv = dict(t.split("=") for t in w[1:] if "=" in t)
            last["nozzle"], last["bed"] = float(kv["EXTRUDER_TEMP"]), float(kv["BED_TEMP"])
    return {k: sorted(v) for k, v in out.items()}


EXPECT = {"PETG": dict(nozzle=240.0, bed=80.0, filament_type="PETG", wall_loops="6", top_shell_layers="6",
                       bottom_shell_layers="6", sparse_infill_density="40%"),
          "PLA": dict(nozzle=210.0, bed=60.0, filament_type="PLA", wall_loops="3", top_shell_layers="4",
                      bottom_shell_layers="4", sparse_infill_density="25%")}
EXPECT["PETG-body"] = {**EXPECT["PLA"], "nozzle": 240.0, "bed": 80.0, "filament_type": "PETG"}


def check_plate(name):
    printer, material, items = mp.PLATES[name]
    work = mp.OUT / printer / name
    bed = mp.BED[printer]
    prob = []
    expected = []
    for part, n in items:
        expected += [part] * n
    bs = bodies(work / f"{name}.stl")
    if len(bs) != len(expected):
        prob.append(f"{len(bs)} bodies in the plate, {len(expected)} parts expected")
    lo = min(b.bounds[0][0] for b in bs), min(b.bounds[0][1] for b in bs)
    hi = max(b.bounds[1][0] for b in bs), max(b.bounds[1][1] for b in bs)
    brim = 5.0
    edge = min(lo[0], lo[1], bed - hi[0], bed - hi[1])
    if edge < brim:
        prob.append(f"a part {edge:.1f} mm from the bed's edge (brim {brim} mm)")
    fps = [footprint(b) for b in bs]
    gap = min((fps[i].distance(fps[j]) for i in range(len(fps)) for j in range(i + 1, len(fps))), default=99.0)
    if gap < 2.0:
        prob.append(f"two parts {gap:.1f} mm apart")
    stl_h = max(b.bounds[1][2] for b in bs)

    gc = work / f"{name}.gcode"
    cfg, xyz, cmds = parse_gcode(gc)
    exp = EXPECT[material]
    t = temps(cmds)
    if t["nozzle"] and max(t["nozzle"]) not in (exp["nozzle"], exp["nozzle"] + 5):
        prob.append(f"nozzle {t['nozzle']} (expected {exp['nozzle']})")
    if not t["nozzle"]:
        prob.append("no nozzle temperature set")
    if t["bed"] != [exp["bed"]]:
        prob.append(f"bed {t['bed']} (expected {exp['bed']})")
    for k in ("filament_type", "wall_loops", "top_shell_layers", "bottom_shell_layers", "sparse_infill_density"):
        if cfg.get(k) != exp[k]:
            prob.append(f"{k} = {cfg.get(k)} (expected {exp[k]})")
    for k, v in (("layer_height", "0.2"), ("initial_layer_print_height", "0.2"), ("enable_support", "1"),
                 ("curr_bed_type", "Textured PEI Plate"), ("sparse_infill_pattern", "gyroid")):
        if cfg.get(k) != v:
            prob.append(f"{k} = {cfg.get(k)} (expected {v})")
    area = [tuple(map(float, p.split("x"))) for p in cfg.get("printable_area", "").split(",") if p]
    ax, ay = max(p[0] for p in area), max(p[1] for p in area)
    if (ax, ay) != (bed, bed):
        prob.append(f"printable area {ax} x {ay}, bed {bed}")
    # the part of the print after the purge line: everything above the first layer, or on it but off the purge row
    body_moves = xyz[(xyz[:, 1] > 1.0)] if len(xyz) else xyz
    if len(body_moves):
        bx = body_moves[:, 0].min(), body_moves[:, 0].max()
        by = body_moves[:, 1].min(), body_moves[:, 1].max()
        if bx[0] < 0 or by[0] < 0 or bx[1] > bed or by[1] > bed:
            prob.append(f"extrusion outside the bed: x {bx[0]:.1f}..{bx[1]:.1f}, y {by[0]:.1f}..{by[1]:.1f}")
    zmax = float(xyz[:, 2].max()) if len(xyz) else 0.0
    if zmax > float(cfg.get("printable_height", "0")):
        prob.append(f"prints to z {zmax:.1f}, above the printer's {cfg.get('printable_height')}")
    if abs(zmax - stl_h) > 0.3:
        prob.append(f"G-code tops out at z {zmax:.2f}, the plate is {stl_h:.2f} tall")
    # every part printed: first-layer extrusion inside its footprint, and extrusion up to its top
    missing = []
    for b, fp, part in zip(bs, fps, expected):
        x0, y0 = b.bounds[0][:2]
        x1, y1 = b.bounds[1][:2]
        sel = xyz[(xyz[:, 0] > x0 - 0.5) & (xyz[:, 0] < x1 + 0.5) & (xyz[:, 1] > y0 - 0.5) & (xyz[:, 1] < y1 + 0.5)]
        if not len(sel) or sel[:, 2].min() > 0.25 or sel[:, 2].max() < b.bounds[1][2] - 0.3:
            missing.append(part)
    if missing:
        prob.append(f"not printed fully: {sorted(set(missing))}")
    if printer == "i7":
        names = [c.split()[0] for c in cmds]
        for m in ("START_PRINT", "END_PRINT"):
            if names.count(m) != 1:
                prob.append(f"{m} appears {names.count(m)} times")
        bambu_only = sorted({n for n in names if n in ("M620", "M621", "M622", "M623", "M1002", "M991", "M971",
                                                       "M981", "M973", "M960")})
        if bambu_only:
            prob.append(f"Bambu-only commands in the i7 file: {bambu_only}")
    else:
        if not any(c.startswith("M1002") for c in cmds) or ";===== machine: P1S" not in gc.read_text(errors="replace")[:400000]:
            prob.append("not Bambu's own P1S start G-code")
        with zipfile.ZipFile(work / f"{name}.gcode.3mf") as z:
            inner = z.read("Metadata/plate_1.gcode")
        if inner != gc.read_bytes():
            prob.append("the .gcode.3mf holds a different G-code from the .gcode")
    head = ""
    with open(gc, encoding="utf-8", errors="replace") as f:
        for line in f:
            head += line
            if "HEADER_BLOCK_END" in line:
                break
    tm = re.search(r"(?:total estimated time|estimated printing time \(normal mode\))\s*[:=]\s*([\dhms ]+)", head)
    gm = re.search(r"total filament weight \[g\] : ([\d.]+)", head)
    return dict(printer=printer, material=material, parts=len(expected), bodies=len(bs),
                time=tm.group(1).strip() if tm else "?", grams=float(gm.group(1)) if gm else 0.0,
                nozzle=t["nozzle"], bed=t["bed"], height_mm=round(zmax, 2), min_gap_mm=round(gap, 1),
                min_edge_mm=round(edge, 1), problems=prob)


def main():
    guide = guide_parts()
    on_plates = {}
    for name, (printer, material, items) in mp.PLATES.items():
        for part, n in items:
            q, mats = on_plates.get(part, (0, set()))
            on_plates[part] = (q + n, mats | {material.split("-")[0]})
    cover = []
    for part, (n, mat) in guide.items():
        q, mats = on_plates.get(part, (0, set()))
        if q != n or mats != {mat}:
            cover.append(f"{part}: guide {n} x {mat}, plates {q} x {sorted(mats)}")
    for part in set(on_plates) - set(guide):
        cover.append(f"{part} is on a plate but not in the guide")
    stls = {p.stem for p in mp.STL.glob("JX0_*.stl")} - {"JX0_Servo_STS3215"}
    for part in stls - set(on_plates):
        cover.append(f"{part}.stl is on no plate")
    print(f"coverage: {len(guide)} part types, {sum(n for n, _ in guide.values())} pieces in the guide; "
          f"{'OK' if not cover else cover}")

    orient = {}
    for part in sorted(on_plates):
        o = orientation(part)
        o["problems"] = ([] if o["contact_mm2"] >= MIN_CONTACT else [f"only {o['contact_mm2']} mm^2 on the bed"]) + \
                        ([] if o["com_over_contact"] else ["centre of mass not over its bed face (it would tip)"]) + \
                        ([] if o["watertight"] else ["mesh not watertight"])
        orient[part] = o
        print(f"  {part:22s} bed {o['contact_mm2']:7.1f} mm2  supported {o['supported_mm2']:7.1f} mm2  "
              f"h {o['height_mm']:6.2f}  {'; '.join(o['problems']) or 'OK'}")

    plates = {}
    for name in mp.PLATES:
        r = check_plate(name)
        plates[name] = r
        print(f"{name:24s} {r['printer']:3s} {r['material']:4s} {r['bodies']:2d}/{r['parts']:2d} parts  {r['time']:>12s}  "
              f"{r['grams']:6.1f} g  nozzle {r['nozzle']} bed {r['bed']}  h {r['height_mm']:.1f}  gap {r['min_gap_mm']}  "
              f"edge {r['min_edge_mm']}  {'; '.join(r['problems']) or 'OK'}")
    tot = {}
    for r in plates.values():
        tot[r["material"]] = round(tot.get(r["material"], 0) + r["grams"], 1)
    n_prob = len(cover) + sum(len(o["problems"]) for o in orient.values()) + sum(len(r["problems"]) for r in plates.values())
    out = dict(coverage_problems=cover, orientation=orient, plates=plates, filament_g=tot, problems=n_prob)
    (mp.OUT / "verify_plates.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"filament: {tot};  problems: {n_prob}")
    sys.exit(1 if n_prob else 0)


if __name__ == "__main__":
    main()
