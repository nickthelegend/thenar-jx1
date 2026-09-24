"""Parallel push-rod ankle for the Jetson side: crank angles <-> ankle pitch/roll and the PD-gain mapping.

Same model as calculations/jx1calc/ankle.py (closed-form inverse kinematics; rl/tests check the two agree), plus:
  forward kinematics (Newton on the closed-form IK)   motor feedback -> joint state for the policy
  joint <-> motor velocity/torque maps via J = d(phi_A, phi_B)/d(pitch, roll)
  motor-space PD gains realising the joint-space ankle gains (per-motor MIT loops can only realise the diagonal of
  J^-T K_q J^-1; the pitch stiffness is matched and the resulting roll stiffness is reported)
Left leg geometry; the right leg is its mirror image: right(pitch, roll) == left(pitch, -roll) with the same crank signs.
"""
from __future__ import annotations

import math

import numpy as np


def _rx(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def _ry(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


class ParallelAnkle:
    def __init__(self, crank_r, foot_lever, rod_half_spacing, heights, crank_half_spacing, mirror=False):
        self.r, self.a = crank_r, foot_lever
        self.h = tuple(heights)
        self.yc = (+crank_half_spacing, -crank_half_spacing)
        self.yf = (+rod_half_spacing, -rod_half_spacing)
        self.mirror = mirror
        self.L = tuple(float(np.linalg.norm(np.array([-self.r, self.yc[i], self.h[i]]) - np.array([-self.a, self.yf[i], 0.0])))
                       for i in range(2))

    @classmethod
    def from_params(cls, p: dict, side: str):
        return cls(p["crank_radius_m"], p["foot_lever_m"], p["rod_half_spacing_m"], (p["motor_A_height_m"], p["motor_B_height_m"]),
                   p["crank_half_spacing_m"], mirror=(side == "right"))

    def _left_ik(self, pitch, roll):
        out = []
        for i in range(2):
            F = _ry(pitch) @ _rx(roll) @ np.array([-self.a, self.yf[i], 0.0])
            dz, dy = self.h[i] - F[2], self.yc[i] - F[1]
            a, b = 2 * self.r * F[0], 2 * self.r * dz
            c = self.L[i] ** 2 - F[0] ** 2 - self.r ** 2 - dy ** 2 - dz ** 2
            rho = math.hypot(a, b)
            if abs(c) > rho:
                raise ValueError("ankle linkage cannot reach this pose")
            base = math.atan2(b, a)
            cand = [(base + s * math.acos(c / rho) + math.pi) % (2 * math.pi) - math.pi for s in (1, -1)]
            out.append(min(cand, key=abs))
        return np.array(out)

    def crank_angles(self, pitch, roll):
        """Joint (pitch, roll) -> motor crank angles (phi_A, phi_B), rad."""
        return self._left_ik(pitch, -roll if self.mirror else roll)

    def jacobian(self, pitch, roll, eps=1e-6):
        """J = d(phi_A, phi_B) / d(pitch, roll)."""
        J = np.zeros((2, 2))
        for k, (dp, dr) in enumerate(((eps, 0.0), (0.0, eps))):
            J[:, k] = (self.crank_angles(pitch + dp, roll + dr) - self.crank_angles(pitch - dp, roll - dr)) / (2 * eps)
        return J

    def joint_angles(self, phi_a, phi_b, guess=(0.0, 0.0), tol=1e-10, iters=20):
        """Motor crank angles -> joint (pitch, roll) by Newton iteration on the inverse kinematics."""
        x = np.array(guess, dtype=float)
        target = np.array([phi_a, phi_b], dtype=float)
        for _ in range(iters):
            err = self.crank_angles(*x) - target
            if np.max(np.abs(err)) < tol:
                break
            x -= np.linalg.solve(self.jacobian(*x), err)
        return x

    def joint_velocity(self, pitch, roll, dphi_a, dphi_b):
        return np.linalg.solve(self.jacobian(pitch, roll), np.array([dphi_a, dphi_b]))

    def joint_torque(self, pitch, roll, tau_a, tau_b):
        """Static duality tau_q = J^T tau_m."""
        return self.jacobian(pitch, roll).T @ np.array([tau_a, tau_b])

    def motor_torque(self, pitch, roll, tau_pitch, tau_roll):
        return np.linalg.solve(self.jacobian(pitch, roll).T, np.array([tau_pitch, tau_roll]))

    def motor_gains(self, pitch, roll, kq, dq):
        """Per-motor (kp, kd) arrays for motors A, B realising the joint-space ankle PD with independent motor MIT loops.

        Two equal motor loops k give a joint stiffness J^T diag(k, k) J; near the symmetric pose its diagonal is
        k (J00^2 + J10^2) for pitch and k (J01^2 + J11^2) for roll, so the roll/pitch ratio is fixed by the linkage (1.27 for
        JX1). The pitch stiffness is matched exactly (rl/config/jx1_walk.yaml uses realisable pitch/roll pairs); returns
        ((kp_m, kd_m), realised joint stiffness matrix)."""
        J = self.jacobian(pitch, roll)
        wp = J[0, 0] ** 2 + J[1, 0] ** 2
        kp_m = np.full(2, kq[0] / wp)
        kd_m = np.full(2, dq[0] / wp)
        return (kp_m, kd_m), J.T @ np.diag(kp_m) @ J
