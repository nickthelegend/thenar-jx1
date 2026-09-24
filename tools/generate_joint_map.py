"""Generate simulation/joint_map.yaml — the single kinematic contract for CAD, URDF, MuJoCo, Isaac and firmware.

Source of numbers: calculations/design_point.yaml (iteration tag recorded). Once the SolidWorks assembly
exists, tools/cad_joint_extract.py overwrites origins with CAD-measured values and marks them MEASURED-CAD.

Usage: .venv/Scripts/python tools/generate_joint_map.py
"""
from __future__ import annotations

import math
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DP = yaml.safe_load((ROOT / "calculations" / "design_point.yaml").read_text(encoding="utf-8"))


class _Dumper(yaml.SafeDumper):
    """No anchors/aliases; short numeric lists in flow style."""
    def ignore_aliases(self, data):
        return True


def _repr_list(dumper, data):
    flow = all(isinstance(x, (int, float)) for x in data) and len(data) <= 6
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=flow)


_Dumper.add_representer(list, _repr_list)


def dump(doc):
    return yaml.dump(doc, Dumper=_Dumper, sort_keys=False, width=140, allow_unicode=True)


def v(x):
    return x["value"] if isinstance(x, dict) and "value" in x else x


AXIS = {"yaw": [0, 0, 1], "roll": [1, 0, 0], "pitch": [0, 1, 0]}
MIRROR_NEG = {"hip_yaw", "hip_roll", "ankle_roll", "shoulder_roll", "shoulder_yaw", "neck_yaw_never"}


def rng(name, table, side):
    lo, hi = table[name]["min"], table[name]["max"]
    if side == "right" and name in MIRROR_NEG:
        lo, hi = -hi, -lo
    return lo, hi


def joint(name, parent, child, origin, axis, lo_deg, hi_deg, act, note, sign):
    return {
        "name": name, "type": "revolute", "parent": parent, "child": child,
        "origin_xyz_m": [round(float(c), 6) for c in origin], "origin_rpy_rad": [0.0, 0.0, 0.0],
        "axis": axis,
        "lower_rad": round(math.radians(lo_deg), 6), "upper_rad": round(math.radians(hi_deg), 6),
        "lower_deg": lo_deg, "upper_deg": hi_deg,
        "zero": "see zero_pose", "sign": sign, "actuator_class": act, "note": note,
        "origin_label": "ASSUMED (design_point " + DP["meta"]["version"] + ")",
    }


def main():
    g = DP["geometry"]
    ub = DP["upper_body_geometry"]
    jr = DP["joint_ranges_deg"]
    ur = DP["upper_body_joint_ranges_deg"]
    assign = DP["leg_actuator_assignment"]
    hs = v(g["hip_spacing_m"]) / 2
    thigh, shin = v(g["thigh_m"]), v(g["shin_m"])
    joints = []
    for side, s in (("left", 1), ("right", -1)):
        p = side
        joints += [
            joint(f"{p}_hip_yaw_joint", "pelvis", f"{p}_hip_yaw_link", [0, s * hs, 0], AXIS["yaw"], *rng("hip_yaw", jr, side), assign["hip_yaw"],
                  "hip centre; yaw/roll/pitch axes intersect", "+ rotates toes to +y (left): external rotation for left leg"),
            joint(f"{p}_hip_roll_joint", f"{p}_hip_yaw_link", f"{p}_hip_roll_link", [0, 0, 0], AXIS["roll"], *rng("hip_roll", jr, side), assign["hip_roll"],
                  "", "+ moves foot to +y: abduction for left leg, adduction for right"),
            joint(f"{p}_hip_pitch_joint", f"{p}_hip_roll_link", f"{p}_thigh_link", [0, 0, 0], AXIS["pitch"], *rng("hip_pitch", jr, side), assign["hip_pitch"],
                  "", "- = flexion (leg swings forward)"),
            joint(f"{p}_knee_joint", f"{p}_thigh_link", f"{p}_shin_link", [0, 0, -thigh], AXIS["pitch"], *rng("knee", jr, side), assign["knee"],
                  "", "+ = flexion"),
            joint(f"{p}_ankle_pitch_joint", f"{p}_shin_link", f"{p}_ankle_cross_link", [0, 0, -shin], AXIS["pitch"], *rng("ankle_pitch", jr, side),
                  f"{assign['ankle_A']}x2 via parallel push-rods", "virtual serial joint; physical motors A/B map through jx1calc.ankle.ParallelAnkle",
                  "+ = plantarflexion (toes down)"),
            joint(f"{p}_ankle_roll_joint", f"{p}_ankle_cross_link", f"{p}_foot_link", [0, 0, 0], AXIS["roll"], *rng("ankle_roll", jr, side),
                  f"{assign['ankle_A']}x2 via parallel push-rods", "virtual serial joint (parallel linkage)", "+ lifts the +y edge of the sole"),
        ]
    joints.append(joint("waist_yaw_joint", "pelvis", "torso_link", v(ub["waist_yaw_origin"]), AXIS["yaw"], ur["waist_yaw"]["min"], ur["waist_yaw"]["max"],
                        "M", "", "+ turns torso to the left"))
    for side, s in (("left", 1), ("right", -1)):
        p = side
        o = v(ub["shoulder_pitch_origin"])
        joints += [
            joint(f"{p}_shoulder_pitch_joint", "torso_link", f"{p}_shoulder_pitch_link", [o[0], s * o[1], o[2]], AXIS["pitch"], *rng("shoulder_pitch", ur, side), "S", "", "- raises the arm forward"),
            joint(f"{p}_shoulder_roll_joint", f"{p}_shoulder_pitch_link", f"{p}_shoulder_roll_link", [0, s * v(ub["shoulder_roll_offset"])[1], 0], AXIS["roll"], *rng("shoulder_roll", ur, side), "S", "", "+ moves arm to +y"),
            joint(f"{p}_shoulder_yaw_joint", f"{p}_shoulder_roll_link", f"{p}_upper_arm_link", v(ub["shoulder_yaw_offset"]), AXIS["yaw"], *rng("shoulder_yaw", ur, side), "XS", "", "+ rotates arm about its long axis toward +y"),
            joint(f"{p}_elbow_joint", f"{p}_upper_arm_link", f"{p}_forearm_link", v(ub["elbow_offset"]), AXIS["pitch"], *rng("elbow", ur, side), "XS", "", "- = flexion"),
        ]
    joints += [
        joint("neck_yaw_joint", "torso_link", "neck_link", v(ub["neck_yaw_origin"]), AXIS["yaw"], ur["neck_yaw"]["min"], ur["neck_yaw"]["max"], "servo", "", "+ looks left"),
        joint("neck_pitch_joint", "neck_link", "head_link", v(ub["neck_pitch_offset"]), AXIS["pitch"], ur["neck_pitch"]["min"], ur["neck_pitch"]["max"], "servo", "", "+ looks down"),
    ]
    fixed = [
        {"name": f"{p}_hand_fixed", "type": "fixed", "parent": f"{p}_forearm_link", "child": f"{p}_hand_link",
         "origin_xyz_m": v(ub["hand_offset"]), "origin_rpy_rad": [0, 0, 0]} for p in ("left", "right")
    ] + [
        {"name": f"{p}_sole_fixed", "type": "fixed", "parent": f"{p}_foot_link", "child": f"{p}_sole_link",
         "origin_xyz_m": [0, 0, -v(g["sole_to_ankle_m"])], "origin_rpy_rad": [0, 0, 0]} for p in ("left", "right")
    ] + [
        {"name": "imu_fixed", "type": "fixed", "parent": "pelvis", "child": "imu_link", "origin_xyz_m": [0, 0, 0.05], "origin_rpy_rad": [0, 0, 0]},
    ]
    doc = {
        "robot": "JX1",
        "version": DP["meta"]["version"],
        "generated_by": "tools/generate_joint_map.py",
        "conventions": {
            "frames": DP["frames"]["convention"],
            "base_link": "pelvis — origin at the midpoint between the hip centres",
            "zero_pose": "all joints 0: legs straight and vertical, feet flat and parallel, arms hanging straight down beside the torso, head level",
            "units": "metres, radians (degrees given for readability)",
            "mirroring": "right-side roll/yaw joints use the same +x/+z axes as the left, so their numeric limits are mirrored",
            "ankle": "ankle_pitch/ankle_roll are virtual serial joints; hardware uses two motors per ankle and parallel push-rods",
        },
        "dof": {"legs": 12, "waist": 1, "arms": 8, "neck": 2, "total_actuated": 23},
        "joints": joints,
        "coupled_limits": {
            "ankle_pitch_roll": {
                "joints": ["ankle_pitch", "ankle_roll"],
                "left_polygon_deg": DP["ankle_linkage"]["coupled_limit_polygon_deg"]["value"],
                "right_polygon_deg": [[p_, -r_] for p_, r_ in DP["ankle_linkage"]["coupled_limit_polygon_deg"]["value"]],
                "enforced_by": "high-level controller / RL action clipping on the Jetson (the CAN hubs enforce per-motor crank limits)",
                "evidence": DP["ankle_linkage"]["coupled_limit_polygon_deg"]["note"],
            },
            "hip_yaw_toe_out": {
                "joints": ["left_hip_yaw", "right_hip_yaw"],
                "rule": "left_hip_yaw - right_hip_yaw <= toe_out_sum_max_deg (sum of both toe-out angles)",
                "toe_out_sum_max_deg": DP["hip_yaw_coupling"]["toe_out_sum_max_deg"]["value"],
                "enforced_by": "high-level controller / RL action clipping on the Jetson",
                "evidence": DP["hip_yaw_coupling"]["toe_out_sum_max_deg"]["note"],
            },
        },
        "fixed_frames": fixed,
    }
    out = ROOT / "simulation" / "joint_map.yaml"
    out.write_text("# JX1 joint map — generated, do not hand-edit (edit design_point.yaml and regenerate)\n" +
                   dump(doc), encoding="utf-8")
    print(f"wrote {out} with {len(joints)} actuated joints")


if __name__ == "__main__":
    main()
