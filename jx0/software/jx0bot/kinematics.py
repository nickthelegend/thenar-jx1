"""JX0 leg kinematics: forward and closed-form inverse, in the pelvis frame (x forward, y left, z up; metres, radians).

Chain per leg (the simulation model and the CAD agree): hip centre at (0, +-HIP_Y, 0); hip yaw (z), hip roll (x), hip
pitch (y) all through the hip centre; knee (y) THIGH below; ankle pitch (y) and ankle roll (x) through the ankle
centre SHIN below the knee; sole SOLE below the ankle. Knee + = flexion, ankle pitch + = toes down.
"""
from __future__ import annotations

import math

import numpy as np

HIP_Y, THIGH, SHIN, SOLE = 0.045, 0.062, 0.058, 0.033   # v0.4 (jx0/design_point.yaml)
FOOT_X = (-0.068, 0.056)           # heel and toe, relative to the ankle
FOOT_HALF_W = 0.035
LEG = ("hip_yaw", "hip_roll", "hip_pitch", "knee", "ankle_pitch", "ankle_roll")


def rx(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def ry(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def hip(side):
    return np.array([0.0, HIP_Y if side == "l" else -HIP_Y, 0.0])


def fk(q, side):
    """q = (hip yaw, hip roll, hip pitch, knee, ankle pitch, ankle roll) -> (ankle centre, foot rotation) in the pelvis frame."""
    yw, rl, pt, kn, ap, ar = q
    R_hip = rz(yw) @ rx(rl) @ ry(pt)
    p_knee = hip(side) + R_hip @ np.array([0.0, 0.0, -THIGH])
    R_knee = R_hip @ ry(kn)
    p_ankle = p_knee + R_knee @ np.array([0.0, 0.0, -SHIN])
    return p_ankle, R_knee @ ry(ap) @ rx(ar)


def ik(p_ankle, R_foot, side):
    """Ankle centre and foot rotation (pelvis frame) -> the 6 joint angles. Raises ValueError if out of reach."""
    r = R_foot.T @ (hip(side) - np.asarray(p_ankle, float))        # ankle -> hip, in the foot frame
    c = float(np.linalg.norm(r))
    cos_k = (c * c - THIGH * THIGH - SHIN * SHIN) / (2 * THIGH * SHIN)
    if cos_k > 1.0 + 1e-9:
        raise ValueError(f"leg over-stretched ({c * 1000:.1f} mm)")
    knee = math.acos(max(-1.0, min(1.0, cos_k)))
    ar = math.atan2(r[1], r[2])
    vx, vz = -THIGH * math.sin(knee), SHIN + THIGH * math.cos(knee)       # hip seen from the ankle, before the ankle joints
    ap = math.atan2(vx, vz) - math.atan2(r[0], math.hypot(r[1], r[2]))
    R_hip = R_foot @ rx(-ar) @ ry(-(ap + knee))
    roll = math.asin(max(-1.0, min(1.0, R_hip[2, 1])))
    pitch = math.atan2(-R_hip[2, 0], R_hip[2, 2])
    yaw = math.atan2(-R_hip[0, 1], R_hip[1, 1])
    return np.array([yaw, roll, pitch, knee, ap, ar])


def leg_dict(q, side):
    return {f"{side}_{j}": float(v) for j, v in zip(LEG, q)}


# masses (kg) and centres of mass (left leg link frames, m) from jx0/design_point.yaml via jx0/sim/jx0_model.py (v0.4;
# checked against the MuJoCo model by tests/test_jx0bot.py). The legs are a third of the robot, so the centre of mass
# moves with every step and is computed from both legs' joint angles.
UPPER_MASS, UPPER_COM = 1.4230, np.array([0.0084, 0.0, 0.1361])   # pelvis + torso + head + arms (arms at rest)
LINKS = {
    "hip_yaw_link": (0.1450, (-0.0308, -0.0115, 0.0058)),
    "hip_roll_link": (0.1220, (0.0059, 0.0019, 0.0005)),
    "thigh": (0.1370, (0.0123, -0.0007, -0.0553)),
    "shin": (0.1180, (0.0005, -0.0007, -0.0405)),
    "ankle_cross": (0.1290, (-0.0376, -0.0083, 0.0000)),
    "foot": (0.0610, (-0.0140, 0.0000, -0.0260)),
}
LEG_MASS = sum(m for m, _ in LINKS.values())


def com(q_l, q_r):
    """Whole-robot centre of mass in the pelvis frame from both legs' joint angles -> (com, total mass)."""
    s = UPPER_MASS * UPPER_COM
    for q, side in ((q_l, "l"), (q_r, "r")):
        sg = np.array([1.0, 1.0 if side == "l" else -1.0, 1.0])
        yw, rl, pt, kn, ap, ar = q
        h = hip(side)
        R_yaw = rz(yw)
        R_roll = R_yaw @ rx(rl)
        R_hip = R_roll @ ry(pt)
        knee = h + R_hip @ np.array([0.0, 0.0, -THIGH])
        R_knee = R_hip @ ry(kn)
        ankle = knee + R_knee @ np.array([0.0, 0.0, -SHIN])
        R_cross = R_knee @ ry(ap)
        frames = {"hip_yaw_link": (h, R_yaw), "hip_roll_link": (h, R_roll), "thigh": (h, R_hip), "shin": (knee, R_knee),
                  "ankle_cross": (ankle, R_cross), "foot": (ankle, R_cross @ rx(ar))}
        for name, (m, c) in LINKS.items():
            o, R = frames[name]
            s = s + m * (o + R @ (np.array(c) * sg))
    m = UPPER_MASS + 2 * LEG_MASS
    return s / m, m
