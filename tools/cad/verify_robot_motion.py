"""Verify the complete articulated JX1 robot (JX1_Robot.SLDASM): legs + upper body driven together.

Leg joints use the verified leg calibration (tools/cad/verify_leg_motion.Verifier: limit mates incl. the parallel-ankle
motor angles), upper-body joints the upper calibration (tools/cad/build_upper_assembly.add_upper). For every whole-body
pose: component transforms vs both analytic models, mate errors, interference detection (rod-end envelopes whitelisted).
Outputs verification/robot_motion_verification.{json,csv} and images in verification/images/robot/.
Usage: .venv/Scripts/python tools/cad/verify_robot_motion.py [--images]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from swlib.core import C, typed, set_view  # noqa: E402
from cad.params import ROOT  # noqa: E402
from cad.build_leg_assembly import from_sw  # noqa: E402
from cad.verify_leg_motion import Verifier  # noqa: E402
from cad.upper_kinematics import UpperCAD, ACTUATED  # noqa: E402

NAME = "JX1_Robot"


def arms(pitch=0.0, roll=0.0, yaw=0.0, elbow=0.0, left=None, right=None):
    """Symmetric arm pose (right roll/yaw mirrored); left/right dicts override individual joints (robot convention)."""
    q = {}
    for s, sg in (("left", 1), ("right", -1)):
        q.update({f"{s}_shoulder_pitch": pitch, f"{s}_shoulder_roll": sg * roll, f"{s}_shoulder_yaw": sg * yaw, f"{s}_elbow": elbow})
    for s, d in (("left", left), ("right", right)):
        for k, v in (d or {}).items():
            q[f"{s}_{k}"] = v
    return q


STAND = {"hip_pitch": -18, "knee": 36, "ankle_pitch": -18}
CROUCH = {"hip_pitch": -30, "knee": 58, "ankle_pitch": -28}
SWING = {"hip_pitch": -40, "knee": 70, "ankle_pitch": -20}
POSES = [
    ("zero", {}, {}, {}),
    ("stand_arms_relaxed", STAND, STAND, arms(roll=8, elbow=-10)),
    ("walk_left_stance", CROUCH, SWING, arms(roll=8, elbow=-20, left={"shoulder_pitch": 25}, right={"shoulder_pitch": -25})),
    ("walk_right_stance", SWING, CROUCH, arms(roll=8, elbow=-20, left={"shoulder_pitch": -25}, right={"shoulder_pitch": 25})),
    ("deep_squat_arms_forward", {"hip_pitch": -70, "knee": 120, "ankle_pitch": -50}, {"hip_pitch": -70, "knee": 120, "ankle_pitch": -50},
     arms(pitch=-90)),
    ("sit_hands_on_lap", {"hip_pitch": -90, "knee": 90}, {"hip_pitch": -90, "knee": 90}, arms(pitch=-40, roll=5, elbow=-60)),
    # one-leg stance within the inter-leg limit (OI-7: stance adduction <= 8 deg): stance foot 25 mm from the pelvis centre line,
    # inside the 95 mm sole; swing leg abducted 6 deg (right-leg abduction is negative roll)
    ("single_leg_T_pose", {"hip_pitch": -31, "knee": 55, "ankle_pitch": -24, "hip_roll": -8, "ankle_roll": 8},
     {"hip_pitch": -45, "knee": 90, "ankle_pitch": -20, "hip_roll": -6}, arms(roll=90)),
    # negative test: 14 deg stance adduction + adducted swing leg crosses the legs (outside OI-7)
    ("single_leg_overshift", {"hip_pitch": -31, "knee": 55, "ankle_pitch": -24, "hip_roll": -14, "ankle_roll": 14},
     {"hip_pitch": -45, "knee": 90, "ankle_pitch": -20, "hip_roll": 5}, arms(roll=90)),
    ("leg_forward_arms_back", {"hip_pitch": -60, "knee": 20}, STAND, arms(pitch=60, roll=8)),
    ("abduction_arms_down", {"hip_roll": 30, "ankle_roll": -20}, {}, {}),
    ("abduction_arms_relaxed", {"hip_roll": 30, "ankle_roll": -20}, {}, arms(roll=8)),
    ("waist_turn_carry", STAND, STAND, {**arms(pitch=-30, roll=15, elbow=-90), "waist_yaw": 45}),
    ("head_scan", STAND, STAND, {**arms(roll=8), "neck_yaw": 60, "neck_pitch": 30}),
    # OI-24 hip-yaw toe-out: the learned controller's largest toe-out sum is 22.9 deg (rl/policies/jx1_walk_rough, spinning at
    # 0.9 rad/s); MuJoCo hulls first touch at 21 deg each (sum 42 > the 40 deg controller limit) -> negative test
    ("toe_out_learned_gait", {**STAND, "hip_yaw": 11.5}, {**STAND, "hip_yaw": -11.5}, arms(roll=8)),
    ("toe_out_21_each", {**STAND, "hip_yaw": 21}, {**STAND, "hip_yaw": -21}, arms(roll=8)),
]
# poses that deliberately violate a documented controller constraint: contact is the expected result
OUTSIDE_LIMITS = {"single_leg_overshift": "OI-7: stance hip adduction > 8 deg with the swing leg adducted crosses the legs",
                  "abduction_arms_down": "OI-18: arms hanging straight + 30 deg hip abduction; walking posture keeps shoulder roll >= 8 deg",
                  "toe_out_21_each": "OI-24: hip-yaw toe-out sum 42 deg > the 40 deg controller limit (MuJoCo hulls touch here)"}


class RobotVerifier(Verifier):
    def __init__(self):
        super().__init__(NAME)
        self.upper = UpperCAD()

    def set_upper(self, q_deg):
        for joint, *_ in ACTUATED:
            m = f"{joint}_LIMIT"
            c = self.calib[m]
            val = math.radians(c["zero_deg"] + c["sign"] * q_deg.get(joint, 0.0))
            d = typed(typed(self.mates[m].GetFirstDisplayDimension(), "IDisplayDimension").GetDimension2(0), "IDimension")
            d.SetSystemValue3(val, C.swSetValue_InThisConfiguration, None)

    def pose(self, qL, qR, qU):
        self.set_upper(qU)
        # leg setter rebuilds; set the left leg without rebuild side effects first, the right leg rebuilds everything
        self.set_joints("L", qL)
        self.set_joints("R", qR)

    def drift_upper(self, qU):
        fk = self.upper.component_poses({k: math.radians(v) for k, v in qU.items()})
        worst = (0.0, 0.0, None)
        for key, M4 in fk.items():
            if key not in self.comp or key == "Pelvis":
                continue
            A_ = from_sw(self.comp[key].Transform2)
            dp = float(np.linalg.norm(A_[:3, 3] - M4[:3, 3])) * 1000
            dr = float(np.degrees(np.arccos(np.clip((np.trace(A_[:3, :3].T @ M4[:3, :3]) - 1) / 2, -1, 1))))
            if dp > worst[0] or dr > worst[1]:
                worst = (max(worst[0], dp), max(worst[1], dr), key)
        return worst

    def image_views(self, stem):
        out = ROOT / "verification" / "images" / "robot"
        out.mkdir(parents=True, exist_ok=True)
        for eye, tag in (((1.0, 0.75, 0.55), "iso"), ((1.0, 0.0, 0.0), "front"), ((0.0, 1.0, 0.0), "side")):
            set_view(self.s.app, self.doc, eye=eye)                      # Z-up camera (SolidWorks named views are Y-up)
            self.ext.SaveAs3(str(out / f"{stem}_{tag}.png"), 0, 1, None, None, 0, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", action="store_true")
    a = ap.parse_args()
    v = RobotVerifier()
    rows = []
    for name, qL, qR, qU in POSES:
        v.pose(qL, qR, qU)
        (dpl, drl, wl), _, _ = v.drift("L", qL)
        (dpr, drr, wr), _, _ = v.drift("R", qR)
        dpu, dru, wu = v.drift_upper(qU)
        ints = [i for i in v.interferences() if not v.whitelisted(i["components"])]
        errs = v.mate_errors()
        dp, dr = max(dpl, dpr, dpu), max(drl, drr, dru)
        rows.append({"pose": name, "left_leg_deg": qL, "right_leg_deg": qR, "upper_deg": qU, "max_pos_err_mm": round(dp, 4),
                     "max_rot_err_deg": round(dr, 4), "mate_errors": errs, "interferences": ints,
                     "kinematics_pass": dp < 0.05 and dr < 0.05 and not errs, "collision_free": not ints,
                     "outside_documented_limits": OUTSIDE_LIMITS.get(name)})
        print(f"{name:26s} kin {'OK ' if rows[-1]['kinematics_pass'] else 'BAD'} err {dp:8.4f} mm {dr:7.4f} deg  collisions {len(ints)} "
              f"{[(i['components'][0], i['components'][1], i['volume_mm3']) for i in ints][:4]}", flush=True)
        if a.images and name in ("zero", "walk_left_stance", "deep_squat_arms_forward", "single_leg_T_pose", "waist_turn_carry"):
            v.image_views(f"JX1_{name}")
    v.pose({}, {}, {})
    (ROOT / "verification" / "robot_motion_verification.json").write_text(json.dumps(rows, indent=1, default=str))
    with open(ROOT / "verification" / "robot_motion_verification.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["pose", "max_pos_err_mm", "max_rot_err_deg", "kinematics_pass", "collisions", "collision_pairs"])
        for r in rows:
            w.writerow([r["pose"], r["max_pos_err_mm"], r["max_rot_err_deg"], r["kinematics_pass"], len(r["interferences"]),
                        "; ".join(f"{i['components'][0]}|{i['components'][1]}|{i['volume_mm3']}" for i in r["interferences"])])
    inside = [r for r in rows if not r["outside_documented_limits"]]
    neg = ", ".join(f"{r['pose']} {'contact' if not r['collision_free'] else 'NO contact'}" for r in rows if r["outside_documented_limits"])
    print(f"\nkinematics pass {sum(r['kinematics_pass'] for r in rows)}/{len(rows)}, collision-free {sum(r['collision_free'] for r in rows)}/{len(rows)}; "
          f"within the documented limits collision-free {sum(r['collision_free'] for r in inside)}/{len(inside)} "
          f"({len(rows) - len(inside)} negative test(s): {neg})")


if __name__ == "__main__":
    main()
