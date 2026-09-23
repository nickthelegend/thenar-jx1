"""Upper-body joint torque/speed requirements (arms, waist, neck) — quasi-static + prescribed-motion dynamics.

Arm chain per side: shoulder_pitch (y) -> shoulder_roll (x) -> shoulder_yaw (z) -> elbow (y) -> simple gripper.
Masses are ASSUMED placeholders until actuator selection; results are CALCULATED from them.

Usage: .venv/Scripts/python calculations/run_upper_body_requirements.py [--tag iter0]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import yaml

HERE = Path(__file__).resolve().parent
G = 9.81

ARM = {  # ASSUMED placeholders (iteration 0)
    "upper_arm_m": 0.20, "forearm_m": 0.18, "hand_m": 0.08,
    "m_shoulder_roll_act": 0.35, "m_shoulder_yaw_act": 0.30, "m_elbow_act": 0.30,
    "m_upper_arm_struct": 0.18, "m_forearm_struct": 0.15, "m_gripper": 0.25,
    "payload_kg": 0.5,
}
TORSO = {"m_torso_above_waist": 9.5, "Izz_torso_kgm2": 0.16, "head_kg": 0.6, "head_com_offset_m": 0.05}
POLICY = {"dynamic_factor": 1.5, "static_factor": 1.3, "continuous_factor": 1.3, "speed_floor_rad_s": 6.0}


def arm_masses():
    a = ARM
    # point masses along a straight arm (distance from shoulder axis)
    return [
        (a["m_shoulder_roll_act"], 0.02),                       # sits at the shoulder
        (a["m_shoulder_yaw_act"], 0.06),
        (a["m_upper_arm_struct"], a["upper_arm_m"] / 2),
        (a["m_elbow_act"], a["upper_arm_m"]),
        (a["m_forearm_struct"], a["upper_arm_m"] + a["forearm_m"] / 2),
        (a["m_gripper"], a["upper_arm_m"] + a["forearm_m"] + a["hand_m"] / 2),
        (a["payload_kg"], a["upper_arm_m"] + a["forearm_m"] + a["hand_m"]),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="iter0")
    args = ap.parse_args()
    out = HERE / "results" / args.tag
    out.mkdir(parents=True, exist_ok=True)
    pm = arm_masses()
    m_arm = sum(m for m, _ in pm)
    # static: arm horizontal (worst gravity moment) with payload
    tau_sh_static = sum(m * G * r for m, r in pm)
    elbow_pm = [(m, r - ARM["upper_arm_m"]) for m, r in pm if r > ARM["upper_arm_m"]]
    tau_el_static = sum(m * G * r for m, r in elbow_pm)
    I_sh = sum(m * r * r for m, r in pm) + 0.002
    I_el = sum(m * r * r for m, r in elbow_pm) + 0.0005
    # dynamic: reach/swing profile peaking at 6 rad/s, 40 rad/s^2 while horizontal
    acc, speed = 40.0, 6.0
    tau_sh_dyn = tau_sh_static + I_sh * acc
    tau_el_dyn = tau_el_static + I_el * acc
    # walking arm swing +-25 deg at 1.2 Hz (continuous duty): gravity at 25 deg + inertia
    w = 2 * np.pi * 1.2
    amp = np.radians(25)
    tau_swing = sum(m * G * r for m, r in pm if m != ARM["payload_kg"]) * np.sin(amp) + (I_sh - ARM["payload_kg"] * pm[-1][1] ** 2) * amp * w * w
    # waist yaw: torso yaw acceleration 25 rad/s^2 + counter-rotation of walking yaw moments (~10 N·m ASSUMED from leg analysis)
    tau_waist = TORSO["Izz_torso_kgm2"] * 25.0 + 10.0
    # neck: head COM offset, 20 rad/s^2 small inertia
    tau_neck = TORSO["head_kg"] * G * TORSO["head_com_offset_m"] + 0.004 * 20
    req = {
        "shoulder_pitch": {"static_Nm": tau_sh_static, "dynamic_Nm": tau_sh_dyn, "continuous_Nm": tau_swing},
        "shoulder_roll": {"static_Nm": tau_sh_static, "dynamic_Nm": tau_sh_dyn, "continuous_Nm": tau_swing},
        "shoulder_yaw": {"static_Nm": 0.3 * tau_sh_static, "dynamic_Nm": 0.5 * tau_sh_dyn, "continuous_Nm": 0.2 * tau_swing},
        "elbow": {"static_Nm": tau_el_static, "dynamic_Nm": tau_el_dyn, "continuous_Nm": 0.5 * tau_el_static},
        "waist_yaw": {"static_Nm": 2.0, "dynamic_Nm": tau_waist, "continuous_Nm": 5.0},
        "neck_yaw": {"static_Nm": 0.05, "dynamic_Nm": 0.2, "continuous_Nm": 0.1},
        "neck_pitch": {"static_Nm": tau_neck, "dynamic_Nm": tau_neck * 1.3, "continuous_Nm": tau_neck},
    }
    rows = {}
    for j, r in req.items():
        rows[j] = {k: round(float(v), 2) for k, v in r.items()}
        rows[j]["REQ_peak_torque_Nm"] = round(float(max(POLICY["dynamic_factor"] * r["dynamic_Nm"], POLICY["static_factor"] * r["static_Nm"])), 1)
        rows[j]["REQ_continuous_torque_Nm"] = round(float(POLICY["continuous_factor"] * r["continuous_Nm"]), 1)
        rows[j]["REQ_speed_rad_s"] = POLICY["speed_floor_rad_s"] if j not in ("neck_yaw", "neck_pitch") else 4.0
        rows[j]["label"] = "CALCULATED from ASSUMED masses (iteration " + args.tag + ")"
    res = {"arm_assumptions": ARM, "torso_assumptions": TORSO, "policy": POLICY, "arm_mass_incl_payload_kg": round(m_arm, 3),
           "shoulder_inertia_kgm2": round(I_sh, 4), "elbow_inertia_kgm2": round(I_el, 4), "requirements": rows}
    (out / "upper_body_requirements.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    (out / "upper_body_requirements.yaml").write_text(yaml.safe_dump(res, sort_keys=False), encoding="utf-8")
    print(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
