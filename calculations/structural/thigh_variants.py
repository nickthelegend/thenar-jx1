"""Thigh redesign study (OI-4): evaluate structural variants directly in voxel space before changing the CAD.

Variants add material to the voxelised baseline thigh (whole-millimetre grid, h = 2 mm):
  V0  baseline CAD: 8 mm lateral plate + 8 mm flanges only between z = -100 and the knee housing
  V1  flanges extended up to the hip-pitch housing clearance circle (r = 64 mm)
  V2  V1 + 4 mm medial closing plate bolted to the flange edges -> closed torsion box between the actuators
  V3  V2 + lateral base plate 12 mm (thickened outward, actuator interface plane unchanged)
  V4  V3 + 8 mm closing plate (stiffest practical box)
  V5  flanges with a gradual run-out toward the hip (6 mm deep inside the r = 64 mm hip-housing clearance circle, where
      only the co-rotating pitch output disc sits, 20 mm deep outside it) + 12 mm lateral plate, no closing plate
  V6  V5 + 4 mm closing plate
  V7  V5 with the 8 mm lateral plate (run-out alone)
  V9  V5 with a 10 mm lateral plate
Same load cases and allowables as run_structural.py. Output: calculations/results/structural/thigh_variants.json
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

Y0, T, LT = rs.PKG["pitch_out_y"], rs.PKG["plate_t"], rs.THIGH
Z_TOP = -0.064                                   # clear of the hip-pitch housing (r 60 mm + 4 mm)
Z_BOT = -LT + rs.KC["D"] / 2 + 0.004             # clear of the knee housing


def add_box(model, x0, x1, y0, y1, z0, z1):
    c = model.origin + (np.argwhere(np.ones(model.occ.shape, bool)) + 0.5) * model.h
    m = (c[:, 0] > x0) & (c[:, 0] < x1) & (c[:, 1] > y0) & (c[:, 1] < y1) & (c[:, 2] > z0) & (c[:, 2] < z1)
    model.occ |= m.reshape(model.occ.shape)


def add_runout_flanges(model, z_top=-0.030):
    """Flanges x in [0.022, 0.030] and [-0.030, -0.022]: 20 mm deep where r >= 64 mm from the hip-pitch axis, else 6 mm
    (inside the pitch-output-disc layer y in [0.030, 0.036]) as long as r >= 41 mm (clear of the output disc rim)."""
    c = model.origin + (np.argwhere(np.ones(model.occ.shape, bool)) + 0.5) * model.h
    x, y, z = c[:, 0], c[:, 1], c[:, 2]
    r = np.hypot(x, z)
    inx = ((x > 0.022) & (x < 0.030)) | ((x > -0.030) & (x < -0.022))
    inz = (z > Z_BOT) & (z < z_top)
    deep = (r >= 0.064) & (y > Y0 - 0.020) & (y < Y0)
    shallow = (r >= 0.041) & (y > Y0 - 0.006) & (y < Y0)
    model.occ |= (inx & inz & (deep | shallow)).reshape(model.occ.shape)


def thicken_plate(m, layers=2):
    occ = m.occ
    j_in = int(round((Y0 + T - m.origin[1]) / m.h))              # first voxel layer outside the 8 mm plate
    for k in range(layers):
        occ[:, j_in + k, :] |= occ[:, j_in - 1, :]


def variant(base, name):
    m = VoxelModel(base.occ.copy(), base.origin, base.h, base.D)
    if name == "V0":
        return m
    if name in ("V5", "V6", "V7", "V9"):
        add_runout_flanges(m)
        if name == "V6":
            add_box(m, -0.030, 0.030, Y0 - 0.024, Y0 - 0.020, Z_BOT, Z_TOP)
        if name in ("V5", "V6"):
            thicken_plate(m)
        if name == "V9":
            thicken_plate(m, layers=1)
        return m
    for x0 in (0.022, -0.030):                                   # flanges over the full free length
        add_box(m, x0, x0 + 0.008, Y0 - 0.020, Y0, Z_BOT, Z_TOP)
    if name == "V1":
        return m
    t_close = 0.008 if name == "V4" else 0.004
    add_box(m, -0.030, 0.030, Y0 - 0.020 - t_close, Y0 - 0.020, Z_BOT, Z_TOP)
    if name == "V2":
        return m
    # thicken the lateral plate outward to 12 mm over its whole outline (copy the plate footprint)
    occ = m.occ
    j_in = int(round((Y0 + T - m.origin[1]) / m.h))              # first voxel layer outside the 8 mm plate
    j_src = j_in - 1
    for k in range(2):
        occ[:, j_in + k, :] |= occ[:, j_src, :]
    return m


def mass_kg(model):
    return float(model.occ.sum() * model.h ** 3 * 2700)


def main():
    d = rs.thigh_def()
    mesh = trimesh.load(rs.MESH / f"{d['stl']}.STL", force="mesh")
    mesh.apply_scale(0.001)
    mat = d["materials"]["6061-T6"]
    base = VoxelModel.from_mesh(mesh, d["h"], mat["D"])
    base.occ = np.pad(base.occ, 3)                                 # room to add material outside the CAD envelope
    base.origin = base.origin - 3 * base.h
    out = {}
    names = sys.argv[1:] or ["V0", "V1", "V2", "V3", "V4", "V5", "V6", "V7"]
    old = json.loads((rs.OUT / "thigh_variants.json").read_text()) if (rs.OUT / "thigh_variants.json").exists() else {}
    out.update(old)
    for name in names:
        m = variant(base, name).build()
        for sname, sel, dofs in d["supports"]:
            m.fix(sel(m), dofs)
        m.factorize()
        fi1, fi2, excl, comp = rs.evaluate_part(m, d, "thigh", mat)
        s1, far = rs.summarise(m, fi1, excl)
        s2, _ = rs.summarise(m, fi2, excl)
        n0 = d["sample_groups"][0][1](m)
        pt = np.asarray(d["sample_groups"][0][2], float)
        fit = m.rigid_fit(m.solve(m.wrench_loads(n0, pt)), n0, pt)
        out[name] = {"mass_kg_6061": round(mass_kg(m), 3), "SF_LC1": round(1 / s1["p99_9"], 2), "SF_LC2": round(1 / s2["p99_9"], 2),
                     "worst_LC1_at_mm": s1["max_at_mm"],
                     "knee_lateral_mm_per_kN": round(fit[1, 1] * 1e6, 2), "knee_roll_deg_per_100Nm": round(np.degrees(fit[3, 3]) * 100, 3),
                     "knee_yaw_deg_per_100Nm": round(np.degrees(fit[5, 5]) * 100, 3), "knee_pitch_deg_per_100Nm": round(np.degrees(fit[4, 4]) * 100, 3)}
        rs.image(m, fi1, far, f"JX1 thigh variant {name} — LC1 (SF {out[name]['SF_LC1']}, LC2 SF {out[name]['SF_LC2']})",
                 rs.OUT / f"thigh_variant_{name}.png", mat["sf_static"])
        print(name, out[name], flush=True)
    (rs.OUT / "thigh_variants.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
