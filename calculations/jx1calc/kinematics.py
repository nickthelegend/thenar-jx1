"""Closed-form inverse kinematics for a 6-DOF leg with a spherical hip.

Chain (from pelvis): hip_yaw(z) -> hip_roll(x) -> hip_pitch(y) -> knee(y) -> ankle_pitch(y) -> ankle_roll(x).
Hip axes intersect at the hip centre; ankle pitch/roll axes intersect at the ankle centre.
Method follows Kajita et al., "Introduction to Humanoid Robotics" (2014), sec. 2.5 (analytical IK
for HRP-type legs), adapted to this repository's sign conventions and verified numerically
against MuJoCo forward kinematics in tests/test_kinematics.py.
"""
from __future__ import annotations

import numpy as np


def rx(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def ry(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def rpy_to_matrix(roll, pitch, yaw):
    return rz(yaw) @ ry(pitch) @ rx(roll)


def leg_fk(q, thigh, shin):
    """Ankle-centre position and foot orientation relative to the hip centre (pelvis-aligned frame)."""
    qy, qr, qp, qk, qap, qar = q
    R_hip = rz(qy) @ rx(qr) @ ry(qp)
    p_knee = R_hip @ np.array([0, 0, -thigh])
    R_knee = R_hip @ ry(qk)
    p_ankle = p_knee + R_knee @ np.array([0, 0, -shin])
    R_foot = R_knee @ ry(qap) @ rx(qar)
    return p_ankle, R_foot


def leg_ik(p_hip, R_pelvis, p_ankle, R_foot, thigh, shin):
    """Joint angles [yaw, roll, pitch, knee, ankle_pitch, ankle_roll] placing the ankle centre at
    p_ankle with foot orientation R_foot, given hip centre p_hip and pelvis orientation R_pelvis
    (all in world frame). Raises ValueError when the target is unreachable."""
    A, B = thigh, shin
    # vector from ankle to hip, expressed in the foot frame
    r = R_foot.T @ (p_hip - p_ankle)
    C = np.linalg.norm(r)
    if C > A + B + 1e-6:
        raise ValueError(f"leg over-extended: |r|={C:.4f} > {A + B:.4f}")
    if C < abs(A - B) + 1e-9:
        raise ValueError("leg over-folded")
    c5 = (C * C - A * A - B * B) / (2 * A * B)
    q_knee = np.arccos(np.clip(c5, -1, 1))  # knee flexion is positive
    # ankle pitch/roll from the hip position seen from the foot
    q_aroll = np.arctan2(r[1], r[2])
    if q_aroll > np.pi / 2:
        q_aroll -= np.pi
    elif q_aroll < -np.pi / 2:
        q_aroll += np.pi
    alpha = np.arcsin(np.clip(A * np.sin(np.pi - q_knee) / C, -1, 1))
    q_apitch = -np.arctan2(r[0], np.sign(r[2]) * np.sqrt(r[1] ** 2 + r[2] ** 2)) - alpha
    # hip rotation: R_pelvis * Rz(y) Rx(r) Ry(p) = R_foot * Rx(-ar) Ry(-ap - k)
    R = R_pelvis.T @ R_foot @ rx(-q_aroll) @ ry(-q_apitch - q_knee)
    q_yaw = np.arctan2(-R[0, 1], R[1, 1])
    cy, sy = np.cos(q_yaw), np.sin(q_yaw)
    q_roll = np.arctan2(R[2, 1], -R[0, 1] * sy + R[1, 1] * cy)
    q_pitch = np.arctan2(-R[2, 0], R[2, 2])
    return np.array([q_yaw, q_roll, q_pitch, q_knee, q_apitch, q_aroll])
