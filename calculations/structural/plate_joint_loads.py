"""Design loads of the bolted plate joints (OI-17): section wrenches where the FEA assumed bonded plates.

The voxel FEA (run_structural.py) treats every part as one solid. Two leg parts are made of plates joined by bolts and
dowels (tools/cad/build_leg_parts.py notes), and their joints carry the whole leg load:
  hip_roll_corner  JX1_HipRollBracket: medial plate (hip-pitch RS04 housing) -> corner joint -> back plate (hip-roll RS03
                   output). Section at the corner line x = roll face + back plate, y = medial plate mid-plane, z = middle
                   of the plate overlap; hip_roll link frame (x forward, y lateral for the left leg, z up)
  shin_joggle      JX1_Shin: knee plate (knee output) -> joggle block -> central web (ankle motors, fork). Section at the
                   block centre; shin frame (origin at the knee centre)
Loads: calculations/structural/leg_loads.py at the final CAD mass (LC1: 3 BW ground reactions capped at the actuator
peaks; LC2: fast walk, nominal walk and turning time series), transported to each section point.
Output: calculations/results/structural/plate_joint_loads.json (max |component| per case; the sample with the largest
moment resultant). Joint layouts (bolt count, size, dowels) are decided in the CAD; these are the loads they must carry.
Usage: .venv/Scripts/python calculations/structural/plate_joint_loads.py [--mass 33.61]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools"))
import leg_loads as L  # noqa: E402
from cad.params import ACT, CRANK_R, PKG, SHIN  # noqa: E402


def sections():
    pc, kc = ACT[PKG["pitch_class"]], ACT[PKG["knee_class"]]
    y_med = PKG["pitch_out_y"] - pc["T_OUT"] - pc["L_HOUSING"]            # hip-pitch housing rear face (medial plate)
    rm = pc["PCD_REAR"] / 2 + 0.006
    z0, z1 = max(-rm, PKG["roll_back_bottom_z"]), min(rm, 0.045)          # medial / back plate overlap (build_leg_parts)
    corner = np.array([PKG["roll_out_x"] + PKG["plate_t"], y_med - PKG["roll_plate_t"] / 2, (z0 + z1) / 2])
    y_out = PKG["knee_rear_y"] - kc["L_HOUSING"] - kc["T_OUT"]
    zj0, zj1 = PKG["shin_joggle_z"]
    joggle = np.array([0.0, (PKG["shin_web_t"] / 2 + y_out - PKG["shin_knee_t"]) / 2, (zj0 + zj1) / 2])
    return corner, joggle


def hip_roll_corner(lc, corner):
    w = lc[("hip_roll", "leg")]                                             # distal leg about the hip centre (frame origin)
    return np.concatenate([w[..., :3], w[..., 3:] - np.cross(corner, w[..., :3])], axis=-1)


def shin_joggle(lc, joggle):
    pts = {"fork": np.array([0.0, 0.0, -SHIN]),                            # ankle pitch pin; rods about their zero-pose pins
           "rodA": np.array([-CRANK_R, PKG["rod_crank_w"], PKG["ankle_A_z"]]),
           "rodB": np.array([-CRANK_R, -PKG["rod_crank_w"], PKG["ankle_B_z"]])}
    tot = 0.0
    for k, p in pts.items():
        w = lc[("shin", k)]
        tot = tot + np.concatenate([w[..., :3], w[..., 3:] + np.cross(p - joggle, w[..., :3])], axis=-1)
    return tot


def summary(W):
    W = np.asarray(W)
    k = int(np.argmax(np.linalg.norm(W[:, 3:], axis=1)))
    return {"max_abs_F_N": np.abs(W[:, :3]).max(0).round(0).tolist(), "max_abs_M_Nm": np.abs(W[:, 3:]).max(0).round(1).tolist(),
            "worst_moment_sample": {"F_N": W[k, :3].round(0).tolist(), "M_Nm": W[k, 3:].round(1).tolist()}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mass", type=float, default=33.61)
    a = ap.parse_args()
    corner, joggle = sections()
    lc1, summ = L.lc1_samples(a.mass)
    lc2 = L.lc2_series()
    n2 = len(lc2[("shin", "fork")])
    out = {"mass_kg": a.mass, "LC1": {"samples": summ["samples"], "scaled_to_actuator_peaks": summ["scaled"]},
           "LC2": "fast walk 0.79 m/s, nominal walk 0.52 m/s, 15 deg/step turning (calculations/results/iter1_B_*)",
           "joints": {}}
    for name, pt, fn in (("hip_roll_corner", corner, hip_roll_corner), ("shin_joggle", joggle, shin_joggle)):
        s2 = np.concatenate([fn({k: v[i] for k, v in lc2.items()}, pt) for i in range(n2)])
        out["joints"][name] = {"section_point_m": pt.round(4).tolist(), "LC1": summary(fn(lc1, pt)), "LC2": summary(s2)}
        j = out["joints"][name]
        print(f"{name:16s} LC1 |F| {j['LC1']['max_abs_F_N']} N |M| {j['LC1']['max_abs_M_Nm']} N m   "
              f"LC2 |F| {j['LC2']['max_abs_F_N']} N |M| {j['LC2']['max_abs_M_Nm']} N m")
    res = ROOT / "calculations" / "results" / "structural" / "plate_joint_loads.json"
    res.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("wrote", res.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
