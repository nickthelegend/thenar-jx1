"""Generic structural redesign study in voxel space (OI-4): start from a part's voxelised CAD, add material with simple
geometric primitives, switch material, and re-evaluate the same load cases as run_structural.py.

Variants are declared in VARIANTS below as (part key, variant name, material, list of feature ops). Feature ops:
  ("box", x0, x1, y0, y1, z0, z1)                 add a box
  ("box_if", x0, x1, y0, y1, z0, z1, pred)        add a box where pred(x, y, z) is true (clearance zones)
  ("grow", axis, side, layers)                     thicken every plate face normal to `axis` on `side` (+1/-1) by `layers`
Results: calculations/results/structural/variants_<part>.json + images.
Usage: .venv/Scripts/python calculations/structural/part_variants.py hip_roll [variant ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_structural as rs  # noqa: E402
from voxel_fea import VoxelModel  # noqa: E402

PKG, ACT = rs.PKG, rs.ACT
PC, L_ = rs.PC, rs.L_
XF = PKG["roll_out_x"]                                   # roll output face (hip roll bracket back plate at [XF, XF+T])
YMED = PKG["pitch_out_y"] - PC["T_OUT"] - PC["L_HOUSING"]  # pitch housing rear face (medial plate at [YMED-T, YMED])
T = PKG["plate_t"]
R_PITCH_CLR = PC["D"] / 2 + 0.004                        # pitch housing clearance radius around the hip-pitch (y) axis
YOUT = PKG["knee_rear_y"] - rs.KC["L_HOUSING"] - rs.KC["T_OUT"]   # knee output face (shin knee plate at [YOUT-T, YOUT])
ZT = PKG["yaw_out_z"]                                    # hip-yaw output face (yaw bracket top plate at [ZT-10, ZT])
XBACK = PKG["roll_out_x"] - L_["T_OUT"] - L_["L_HOUSING"]  # roll housing rear face (yaw bracket back plate at [XBACK-8, XBACK])


def outside_pitch_housing(x, y, z):
    """True where material cannot hit the (stationary-relative) pitch housing: medial of its rear face, or radially clear."""
    return (y < YMED) | (np.hypot(x, z) >= R_PITCH_CLR)


def centres(m):
    return m.origin + (np.argwhere(np.ones(m.occ.shape, bool)) + 0.5) * m.h


def apply(m, ops):
    c = centres(m)
    x, y, z = c[:, 0], c[:, 1], c[:, 2]
    for op in ops:
        if op[0] in ("box", "box_if"):
            x0, x1, y0, y1, z0, z1 = op[1:7]
            sel = (x > x0) & (x < x1) & (y > y0) & (y < y1) & (z > z0) & (z < z1)
            if op[0] == "box_if":
                sel &= op[7](x, y, z)
            m.occ |= sel.reshape(m.occ.shape)
        elif op[0] == "grow":
            _, axis, side, layers = op
            occ = m.occ
            for _ in range(layers):
                sh = np.roll(occ, side, axis=axis)
                occ = occ | sh
            m.occ = occ
    return m


def al_or_pacf(name):
    if name == "6061-T6":
        return rs.al()
    if name == "7075-T6":
        return rs.al7075()
    return rs.pacf({"x": 0, "y": 1, "z": 2}[name[-1]])


# hip roll bracket: back plate x in [XF, XF+8], medial plate y in [YMED-8, YMED], rm = 56 mm
RM = PC["PCD_REAR"] / 2 + 0.006
VARIANTS = {
    "hip_roll": {
        "R0_pacf": ("PA-CF build y", []),
        "R1_al": ("6061-T6", []),
        "R2_al_12mm": ("6061-T6", [("box", XF + T, RM, YMED - 0.012, YMED - T, -RM, RM), ("box", XF, XF + 0.012, -0.036, 0.034, -0.045, 0.045)]),
        # R3: R2 + medial ribs (top/bottom flanges on the medial face of the medial plate, 24 mm deep, 8 mm thick)
        "R3_al_ribs": ("6061-T6", [("box", XF + T, RM, YMED - 0.012, YMED - T, -RM, RM), ("box", XF, XF + 0.012, -0.056, 0.034, -0.045, 0.045),
                                   ("box", XF + T, 0.040, YMED - 0.036, YMED - 0.012, RM - 0.008, RM),
                                   ("box", XF + T, 0.040, YMED - 0.036, YMED - 0.012, -RM, -RM + 0.008)]),
        # R4: R3 + corner gussets between back plate and medial plate (normal z) at z = +-20 mm, outside the pitch housing
        "R4_al_ribs_gussets": ("6061-T6", [("box", XF + T, RM, YMED - 0.012, YMED - T, -RM, RM), ("box", XF, XF + 0.012, -0.056, 0.034, -0.045, 0.045),
                                           ("box", XF + T, 0.040, YMED - 0.036, YMED - 0.012, RM - 0.008, RM),
                                           ("box", XF + T, 0.040, YMED - 0.036, YMED - 0.012, -RM, -RM + 0.008),
                                           ("box_if", XF + 0.012, XF + 0.050, YMED - 0.036, 0.030, 0.034, 0.042, outside_pitch_housing),
                                           ("box_if", XF + 0.012, XF + 0.050, YMED - 0.036, 0.030, -0.042, -0.034, outside_pitch_housing)]),
    },
    "hip_yaw": {
        "Y0_pacf": ("PA-CF build z", []),
        "Y1_al": ("6061-T6", []),
        "Y1_7075": ("7075-T6", []),
        # Y12: 7075, back plate 12 mm (grown backward), top plate extended over it
        "Y12_7075_back12": ("7075-T6", [("box", XBACK - 0.012, XBACK - T, -0.050, 0.050, -0.050, ZT), ("box", XBACK - 0.012, XBACK, -0.045, 0.045, ZT - 0.010, ZT)]),
        # Y13: Y12 + 12 mm keel under the top plate above the roll housing (behind the roll-bracket sweep, x <= -86 mm)
        "Y13_7075_back12_keel": ("7075-T6", [("box", XBACK - 0.012, XBACK - T, -0.050, 0.050, -0.050, ZT), ("box", XBACK - 0.012, XBACK, -0.045, 0.045, ZT - 0.010, ZT),
                                             ("box", XBACK - 0.012, -0.086, -0.006, 0.006, 0.057, ZT)]),
        # Y2: back plate 16 mm (grown backward) with the top plate extended over it
        "Y2_al_back16": ("6061-T6", [("box", XBACK - 0.016, XBACK - T, -0.050, 0.050, -0.050, ZT), ("box", XBACK - 0.016, XBACK, -0.045, 0.045, ZT - 0.010, ZT)]),
        # Y3: Y2 + side walls boxing the roll housing's rear half (|y| 58-66 mm, x <= -86 mm: clear of the roll-bracket sweep
        #     cylinder and of the thigh), top plate widened over them
        "Y3_al_box": ("6061-T6", [("box", XBACK - 0.016, XBACK - T, -0.050, 0.050, -0.050, ZT), ("box", XBACK - 0.016, XBACK, -0.045, 0.045, ZT - 0.010, ZT),
                                  ("box", XBACK - 0.016, -0.086, 0.058, 0.066, -0.050, ZT), ("box", XBACK - 0.016, -0.086, -0.066, -0.058, -0.050, ZT),
                                  ("box", XBACK - 0.016, -0.086, -0.066, 0.066, ZT - 0.010, ZT)]),
        # Y4: Y3 + deeper keel above the roll housing (z >= 57 mm behind x = -86 mm) and a 16 mm top plate behind the sweep
        # Y6: yaw output raised 18 mm (PKG yaw_out_z 0.082 -> 0.100, CAD-only) -> 28 mm deep box top: 6 mm top skin, existing
        #     10 mm plate as bottom skin, 8 mm side webs, hub block around the yaw flange, back plate + walls carried up
        "Y6_al_raised_box": ("6061-T6", [("pkg", {"yaw_out_z": 0.100}),
                                         ("box", XBACK - 0.016, XBACK - T, -0.050, 0.050, -0.050, 0.100), ("box", XBACK - 0.016, XBACK, -0.045, 0.045, ZT - 0.010, 0.100),
                                         ("box", XBACK - 0.016, -0.086, 0.058, 0.066, -0.050, 0.100), ("box", XBACK - 0.016, -0.086, -0.066, -0.058, -0.050, 0.100),
                                         ("box", XBACK - 0.016, -0.086, -0.066, 0.066, ZT - 0.016, 0.100),
                                         ("box", XBACK - 0.016, -0.086, -0.006, 0.006, 0.057, ZT),
                                         ("box", XBACK - 0.016, 0.036, -0.045, 0.045, 0.094, 0.100),
                                         ("box", XBACK - 0.016, 0.036, 0.037, 0.045, ZT, 0.100), ("box", XBACK - 0.016, 0.036, -0.045, -0.037, ZT, 0.100),
                                         ("box_if", -0.036, 0.036, -0.036, 0.036, ZT, 0.100, lambda x, y, z: np.hypot(x, y) <= 0.034)]),
        # Y7: raised box top only (5 mm top skin + existing 10 mm plate, 6 mm webs, hub), back plate 12 mm carried up; no side walls
        "Y7_al_raised_light": ("6061-T6", [("pkg", {"yaw_out_z": 0.100}),
                                           ("box", XBACK - 0.012, XBACK - T, -0.050, 0.050, -0.050, 0.100), ("box", XBACK - 0.012, XBACK, -0.045, 0.045, ZT - 0.010, 0.100),
                                           ("box", XBACK - 0.012, 0.036, -0.045, 0.045, 0.095, 0.100),
                                           ("box", XBACK - 0.012, 0.036, 0.039, 0.045, ZT, 0.100), ("box", XBACK - 0.012, 0.036, -0.045, -0.039, ZT, 0.100),
                                           ("box_if", -0.036, 0.036, -0.036, 0.036, ZT, 0.100, lambda x, y, z: np.hypot(x, y) <= 0.034)]),
        # Y8: Y7 + 6 mm side walls boxing the roll housing's rear half (behind the roll-bracket sweep)
        "Y8_al_raised_walls": ("6061-T6", [("pkg", {"yaw_out_z": 0.100}),
                                           ("box", XBACK - 0.012, XBACK - T, -0.050, 0.050, -0.050, 0.100), ("box", XBACK - 0.012, XBACK, -0.045, 0.045, ZT - 0.010, 0.100),
                                           ("box", XBACK - 0.012, 0.036, -0.045, 0.045, 0.095, 0.100),
                                           ("box", XBACK - 0.012, 0.036, 0.039, 0.045, ZT, 0.100), ("box", XBACK - 0.012, 0.036, -0.045, -0.039, ZT, 0.100),
                                           ("box_if", -0.036, 0.036, -0.036, 0.036, ZT, 0.100, lambda x, y, z: np.hypot(x, y) <= 0.034),
                                           ("box", XBACK - 0.012, -0.086, 0.058, 0.064, -0.030, 0.100), ("box", XBACK - 0.012, -0.086, -0.064, -0.058, -0.030, 0.100),
                                           ("box", XBACK - 0.012, -0.086, -0.064, 0.064, 0.090, 0.100)]),
        "Y4_al_box_keel": ("6061-T6", [("box", XBACK - 0.016, XBACK - T, -0.050, 0.050, -0.050, ZT), ("box", XBACK - 0.016, XBACK, -0.045, 0.045, ZT - 0.010, ZT),
                                       ("box", XBACK - 0.016, -0.086, 0.058, 0.066, -0.050, ZT), ("box", XBACK - 0.016, -0.086, -0.066, -0.058, -0.050, ZT),
                                       ("box", XBACK - 0.016, -0.086, -0.066, 0.066, ZT - 0.016, ZT),
                                       ("box", XBACK - 0.016, -0.086, -0.006, 0.006, 0.057, ZT)]),
    },
    "shin": {
        "S0_pacf": ("PA-CF build y", []),
        "S1_al": ("6061-T6", []),
        # S2: joggle block deepened from z in [-84, -66] to [-110, -66] mm (medial side of the web, clear of motor A on +Y)
        "S2_al_deep_joggle": ("6061-T6", [("box", -0.034, 0.034, YOUT - T, 0.005, -0.110, -0.066)]),
        # S3: S2 + knee plate 14 mm (grown medially)
        "S3_al_knee14": ("6061-T6", [("box", -0.034, 0.034, YOUT - T, 0.005, -0.110, -0.066),
                                     ("box", -0.040, 0.040, YOUT - 0.014, YOUT - T, -0.110, 0.000)]),
        # S4: S3 + edge flanges on the knee plate inside the co-rotating output-disc layer (y in [-20, -15] mm, r >= 41 mm)
        "S4_al_knee14_flanges": ("6061-T6", [("box", -0.034, 0.034, YOUT - T, 0.005, -0.110, -0.066),
                                             ("box", -0.040, 0.040, YOUT - 0.014, YOUT - T, -0.110, 0.000),
                                             ("box_if", 0.030, 0.040, YOUT, YOUT + 0.005, -0.110, -0.020, lambda x, y, z: np.hypot(x, z) >= 0.041),
                                             ("box_if", -0.040, -0.030, YOUT, YOUT + 0.005, -0.110, -0.020, lambda x, y, z: np.hypot(x, z) >= 0.041)]),
    },
    "pelvis": {
        "P0_pacf": ("PA-CF build z", []),
        "P1_al": ("6061-T6", []),
    },
    "foot": {
        "F0_pacf": ("PA-CF build z", []),
        "F1_al": ("6061-T6", []),
    },
}

# upper arm (L-bracket: yaw plate z in [-6, 0] mm, elbow plate y in [YB-6, YB] mm down to the elbow at ZE): the 6 mm version
# fails (SF 1.34 / 1.08, run_structural 2026-09-24). Material is added medially (away from the elbow housing) and as gussets
# above the housing (its top is at ZE + 28.5 mm).
_UB = rs._ub()
YB, ZE = -_UB[5]["elbow_face_y"], _UB[3][2]
Z_GUS = -0.085                                           # gusset tip, 16 mm above the RS00 elbow housing


def gusset(x0, x1, y_tip=0.020, z_top=-0.006):
    """Triangular web (normal x) from the yaw plate down the elbow plate: (YB, z_top) - (y_tip, z_top) - (YB, Z_GUS)."""
    return ("box_if", x0, x1, YB, y_tip, Z_GUS, z_top,
            lambda x, y, z: (y - YB) / (y_tip - YB) <= (z - Z_GUS) / (z_top - Z_GUS))


ARM_EL10 = [("box", -0.030, 0.030, YB - 0.010, YB - 0.006, ZE - 0.030, -0.006),      # elbow plate 6 -> 10 mm (medial side)
            ("box", -0.025, 0.025, YB - 0.010, YB - 0.006, -0.006, 0.0)]           # yaw plate follows
ARM_GUSSETS = [gusset(0.019, 0.025), gusset(-0.025, -0.019)]
ARM_YAW8 = [("box", -0.025, 0.025, YB - 0.010, 0.025, -0.008, -0.006)]             # yaw plate 6 -> 8 mm
VARIANTS["upper_arm"] = {
    "U0_al": ("6061-T6", []),
    "U1_al_elbow10": ("6061-T6", ARM_EL10),
    "U2_al_elbow10_gussets": ("6061-T6", ARM_EL10 + ARM_GUSSETS),
    "U3_al_elbow10_gussets_yaw8": ("6061-T6", ARM_EL10 + ARM_GUSSETS + ARM_YAW8),
    "U4_7075_elbow10_gussets": ("7075-T6", ARM_EL10 + ARM_GUSSETS),
}


def main():
    key = sys.argv[1]
    names = sys.argv[2:] or list(VARIANTS[key])
    d = rs.PARTS[key]()
    mesh = trimesh.load(rs.MESH / f"{d['stl']}.STL", force="mesh")
    mesh.apply_scale(0.001)
    base = VoxelModel.from_mesh(mesh, d["h"], rs.iso_D(1e9, 0.3), d.get("offset", (0, 0, 0)))
    base.occ = np.pad(base.occ, 12)                        # room for added material (e.g. raised interfaces)
    base.origin = base.origin - 12 * base.h
    path = rs.OUT / f"variants_{key}.json"
    out = json.loads(path.read_text()) if path.exists() else {}
    for name in names:
        mname, ops = VARIANTS[key][name]
        mat = al_or_pacf(mname)
        saved = dict(PKG)
        for op in ops:
            if op[0] == "pkg":
                PKG.update(op[1])
        d = rs.PARTS[key]()                                  # supports/loads at the (possibly overridden) interface positions
        m = apply(VoxelModel(base.occ.copy(), base.origin, base.h, mat["D"]), [o for o in ops if o[0] != "pkg"]).build()
        PKG.clear()
        PKG.update(saved)
        for sname, sel, dofs in d["supports"]:
            m.fix(sel(m), dofs)
        m.factorize()
        fi1, fi2, excl, comp = rs.evaluate_part(m, d, key, mat)
        s1, far = rs.summarise(m, fi1, excl)
        s2, _ = rs.summarise(m, fi2, excl)
        dens = {"6061-T6": 2700, "7075-T6": 2810}.get(mname, 1240)
        out[name] = {"material": mname, "mass_kg_solid": round(float(m.occ.sum() * m.h ** 3 * dens), 3),
                     "SF_LC1": round(1 / s1["p99_9"], 2), "SF_LC2": round(1 / s2["p99_9"], 2), "required": [mat["sf_static"], mat["sf_fatigue"]],
                     "worst_LC1_at_mm": s1["max_at_mm"], "interface_compliance": comp}
        rs.image(m, fi1, far, f"JX1 {key} variant {name} ({mname}) — LC1 SF {out[name]['SF_LC1']}, LC2 SF {out[name]['SF_LC2']}",
                 rs.OUT / f"variant_{key}_{name}.png", mat["sf_static"])
        print(name, out[name], flush=True)
        path.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
