"""Sensitivity of leg torque/speed demand to walking height, segment length and mass.

Usage: .venv/Scripts/python calculations/run_sensitivity.py [--tag iter0]
"""
from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

import mujoco
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from jx1calc.design import Design, LEG_JOINTS  # noqa: E402
from jx1calc.mjcf import build_mjcf  # noqa: E402
from jx1calc.gait import GaitParams, synthesize  # noqa: E402


def run(design_over, hip_h, gait):
    d = Design(overrides=design_over)
    m = mujoco.MjModel.from_xml_string(build_mjcf(d, with_actuators=False))
    kw = dict(gait)
    kw["hip_height"] = hip_h + kw.pop("dh", 0.0)
    res = synthesize(m, d, GaitParams(**kw))
    tau = res["idr"]["tau"]
    qv = res["qvel"][:, 6:]
    q = res["qpos"][:, 7:]
    row = {"mass_kg": round(d.total_mass, 2)}
    for k, j in enumerate(LEG_JOINTS):
        row[f"{j}_pk"] = round(float(np.abs(np.r_[tau[:, k], tau[:, k + 6]]).max()), 1)
        row[f"{j}_w"] = round(float(np.abs(np.r_[qv[:, k], qv[:, k + 6]]).max()), 1)
    row["knee_max_deg"] = round(float(np.degrees(q[:, 3]).max()), 1)
    row["ankle_min_deg"] = round(float(np.degrees(q[:, 4]).min()), 1)
    row["zmp_err_mm"] = round(1000 * res["zmp_error_history_m"][-1], 1)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="iter0")
    args = ap.parse_args()
    out = HERE / "results" / args.tag
    out.mkdir(parents=True, exist_ok=True)
    gaits = {
        "nominal": dict(name="nominal", step_length=0.22, step_time=0.42, step_height=0.05, n_steps=8),
        "fast": dict(name="fast", step_length=0.30, step_time=0.38, step_height=0.06, n_steps=8, dh=-0.02),
    }
    rows = []
    base_leg = Design().thigh
    # 1) walking height (knee bend) at the baseline geometry
    for h in (0.50, 0.52, 0.54, 0.56):
        for gn, g in gaits.items():
            rows.append({"study": "hip_height", "value": h, "gait": gn, **run({}, h, g)})
    # 2) segment length, with hip height scaled to keep the same knee bend
    for L in (0.25, 0.28, 0.31):
        over = {"geometry": {"thigh_m": {"value": L}, "shin_m": {"value": L}}}
        h = 0.54 * (2 * L + 0.05) / (2 * base_leg + 0.05)
        for gn, g in gaits.items():
            rows.append({"study": "segment_length", "value": L, "gait": gn, **run(over, h, g)})
    # 3) upper-body mass
    for mu in (9.0, 12.0, 15.0):
        over = {"mass_budget": {"upper_body": {"mass_kg": {"value": mu}}}}
        for gn, g in gaits.items():
            rows.append({"study": "upper_body_mass", "value": mu, "gait": gn, **run(over, 0.54, g)})
    # 4) knee actuator placement: coaxial at the knee vs. high on the thigh driving the knee by linkage
    for z in (-0.28, -0.14, -0.06):
        over = {"geometry": {"knee_actuator_z_m": {"value": z}}}
        for gn, g in gaits.items():
            rows.append({"study": "knee_actuator_z", "value": z, "gait": gn, **run(over, 0.54, g)})
    df = pd.DataFrame(rows)
    df.to_csv(out / "sensitivity.csv", index=False)
    cols = ["study", "value", "gait", "mass_kg", "hip_roll_pk", "hip_pitch_pk", "knee_pk", "ankle_pitch_pk",
            "hip_pitch_w", "knee_w", "knee_max_deg", "ankle_min_deg", "zmp_err_mm"]
    txt = df[cols].to_markdown(index=False)
    (out / "sensitivity.md").write_text("# Sensitivity study (" + args.tag + ")\n\nPeak |torque| N·m (`_pk`) and peak |speed| rad/s (`_w`), left+right legs. CALCULATED.\n\n" + txt + "\n", encoding="utf-8")
    print(txt)


if __name__ == "__main__":
    main()
