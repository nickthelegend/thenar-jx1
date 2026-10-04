"""Are JX0's joints strong enough? Loads from the simulation, simple beam models, single-sided (v0.3) and double-sided
(v0.4) joints compared on the same loads.

Loads: the peak load every leg joint carries (MuJoCo joint reaction, robustness.trial(..., loads=True)) over the 14
verified gaits, 48 mid-walk sideways pushes of 0.96 N·s (24 moments x 2 directions) and 42 walks with random model
errors (robustness.sample, latency 0-20 ms): torque about the joint axis (what the servo drives), bending moment about
the other two axes (what the joint's structure carries), axial and radial force.
Models (beam formulas; PETG strengths ASSUMED: 50 MPa along the print layers, 25 MPa across them, fatigue at 10^6
cycles ~15 MPa ~ 30 % of static; JX0 walks ~1,500 steps an hour):
  single-sided joint (v0.3): the next link is one plate on the output horn. The whole bending moment at the horn face
    bends that plate out of its plane, sigma = 6 M / (b t^2), and bends the servo's output shaft;
  double-sided joint (v0.4 U-bracket): the arms on the horn and on the rear hub, d = 42.75 mm apart, carry the moment
    as a force couple F = M / d, in the plane of each arm: sigma = F / (b t), plus half the radial force bending the arm
    over its length L, sigma = 6 (F_r / 2) L / (t b^2). The output shaft carries radial force only, no bending moment;
  hip yaw (v0.4): single-sided on the yaw horn, plus the thrust ring under the pelvis. The ring carries the axial force,
    and the bending moment up to (axial force x ring radius) while the leg presses the disc into it; the yaw servo's
    shaft takes the rest (yaw_shaft_residual_nm, tracked instant by instant).
The STS3215's output bearing ratings are not published: the shaft numbers are compared, not checked against a rating.

    python jx0/verify/verify_strength.py      -> jx0/results/verify_strength.json
"""
from __future__ import annotations

import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "jx0" / "verify"))
sys.path.insert(0, str(ROOT / "jx0" / "cad"))
import robustness as RB  # noqa: E402
import geometry as G  # noqa: E402

OUT = ROOT / "jx0" / "results" / "verify_strength.json"
STRENGTH = {"along_layers_mpa": 50.0, "across_layers_mpa": 25.0, "fatigue_1e6_mpa": 15.0}
# v0.3 single-sided plates on each horn (the CAD of commit f0ba0c9): (width b, thickness t) mm
V03_PLATE = {"hip_yaw": (32.0, 3.0), "hip_roll": (35.0, 3.0), "hip_pitch": (30.0, 4.0), "knee": (30.0, 4.0),
             "ankle_pitch": (30.0, 3.0), "ankle_roll": (24.0, 3.0)}
# v0.4 U-bracket arms: width at the boss b, thickness t, length L to where the arm meets its cage / bridge (mm)
V04_ARM = {"hip_roll": (26.0, G.TU, 30.0), "hip_pitch": (26.0, G.TU, 50.0), "knee": (18.0, G.TU, 22.0),
           "ankle_pitch": (26.0, G.TU, 40.0), "ankle_roll": (26.0, G.TU, 30.0)}
YAW_DISC = (38.0, G.YAW_DISC_T)                                              # v0.4 hip-yaw disc: width, thickness (mm)
ARM_D = (G.HF + G.TU / 2) + (G.HF + G.BOSS_H + G.TU / 2)                     # 42.75 mm between the arms' mid-planes
JOINTS = ("hip_yaw", "hip_roll", "hip_pitch", "knee", "ankle_pitch", "ankle_roll")


def specs():
    gaits = RB.MC_GAITS + ["forward_2", "forward_slow", "backward", "turn_left", "turn_right", "side_left", "backward_2"]
    out = [{"gait": g, "scenario": RB.nominal(), "loads": True} for g in gaits]
    out += [{**s, "loads": True} for s in RB.push_specs((8.0,), timings=24)]
    out += [{**s, "loads": True} for s in RB.model_error_specs(42, 7, None, (0, 1))]
    return out


def _peaks(results):
    peaks = {}
    for r in results:
        for n, v in r["loads"].items():
            p = peaks.setdefault(n, {k: 0.0 for k in v})
            for k, x in v.items():
                p[k] = max(p[k], x)
    return {j: {k: max(peaks[f"{s}_{j}"][k] for s in "lr") for k in peaks[f"l_{j}"]} for j in JOINTS}


def _stress(j, pk):
    """(v0.3 single-sided plate stress, v0.3 shaft bending, v0.4 stress, v0.4 shaft bending, extras) for peak loads pk."""
    m_h, m_c, fr = pk["bending_horn_nm"] * 1000, pk["bending_centre_nm"] * 1000, pk["radial_n"]   # N·mm, N
    b3, t3 = V03_PLATE[j]
    s3 = 6 * m_h / (b3 * t3 ** 2)
    if j == "hip_yaw":
        b4, t4 = YAW_DISC
        res = pk["yaw_shaft_residual_nm"] * 1000
        return s3, m_h / 1000, 6 * res / (b4 * t4 ** 2), res / 1000, {}
    b, t, L = V04_ARM[j]
    fc = m_c / ARM_D
    s4 = fc / (b * t) + 6 * (fr / 2) * L / (t * b ** 2)
    return s3, m_h / 1000, s4, 0.0, {"couple_n": round(fc, 1), "shaft_radial_n": round(fc + fr / 2, 1)}


def evaluate(walk, push):
    """Fatigue from the walking loads (every step, ~10^6 cycles over the robot's life: the gaits on the nominal robot
    and on the 42 randomly wrong ones, which is conservative), static strength from the worst of walking and the
    pushes."""
    rows = {}
    for j in JOINTS:
        w3, ws3, w4, ws4, wx = _stress(j, walk[j])
        worst = {k: max(walk[j][k], push[j][k]) for k in walk[j]}
        p3, ps3, p4, ps4, px = _stress(j, worst)
        rows[j] = {"loads_walking": {k: round(v, 3) for k, v in walk[j].items()},
                   "loads_worst_with_pushes": {k: round(v, 3) for k, v in worst.items()},
                   "v03_single_sided": {"walking_mpa": round(w3, 1), "worst_mpa": round(p3, 1),
                                        "shaft_bending_walking_nm": round(ws3, 2), "shaft_bending_worst_nm": round(ps3, 2),
                                        "fatigue_safety": round(STRENGTH["fatigue_1e6_mpa"] / w3, 2),
                                        "static_safety": round(STRENGTH["along_layers_mpa"] / p3, 2)},
                   "v04": {"design": "single-sided + thrust ring" if j == "hip_yaw" else "double-sided U-bracket",
                           "walking_mpa": round(w4, 1), "worst_mpa": round(p4, 1),
                           "shaft_bending_walking_nm": round(ws4, 2), "shaft_bending_worst_nm": round(ps4, 2),
                           "fatigue_safety": round(STRENGTH["fatigue_1e6_mpa"] / max(w4, 1e-6), 1),
                           "static_safety": round(STRENGTH["along_layers_mpa"] / max(p4, 1e-6), 1), **px}}
    return rows


def main():
    t0 = time.time()
    sp = specs()
    with Pool(os.cpu_count()) as pool:
        res = pool.map(RB.trial, sp, chunksize=1)
    ok = [(s, r) for s, r in zip(sp, res) if not r["fell"]]
    walk = _peaks([r for s, r in ok if s.get("push") is None])
    push = _peaks([r for s, r in ok if s.get("push") is not None])
    nominal = _peaks([r for s, r in ok if s.get("push") is None and "seed" not in s])
    rows = evaluate(walk, push)
    rows["hip_yaw"]["v04"]["shaft_bending_nominal_walking_nm"] = round(nominal["hip_yaw"]["yaw_shaft_residual_nm"], 2)
    ok = [r for s, r in ok]
    fell = len(res) - len(ok)
    out = {"generated_by": "jx0/verify/verify_strength.py",
           "label": "CALCULATED (MuJoCo loads, beam formulas, PETG strength ASSUMED)",
           "load_cases": {"gaits": 14, "pushes_0.96_Ns": 48, "model_error_walks": 42, "runs_that_fell_excluded": fell,
                          "note": "falls are excluded: the model has no body collisions, so a fall's impact is not simulated"},
           "petg_strength": STRENGTH, "u_bracket_arm_spacing_mm": round(ARM_D, 2), "joints": rows,
           "seconds": round(time.time() - t0, 1)}
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"{'joint':12s} | v0.3 single-sided: walk MPa  worst MPa  fatigue SF  static SF  shaft N.m | "
          f"v0.4: walk MPa  worst MPa  fatigue SF  static SF  shaft N.m (worst)")
    for j, r in rows.items():
        a, b = r["v03_single_sided"], r["v04"]
        print(f"{j:12s} | {a['walking_mpa']:22.1f} {a['worst_mpa']:10.1f} {a['fatigue_safety']:11.2f} {a['static_safety']:10.2f} "
              f"{a['shaft_bending_worst_nm']:10.2f} | {b['walking_mpa']:14.1f} {b['worst_mpa']:10.1f} {b['fatigue_safety']:11.1f} "
              f"{b['static_safety']:10.1f} {b['shaft_bending_worst_nm']:10.2f}")
    print(f"{fell} of {len(res)} runs fell;  {time.time() - t0:.0f} s -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
