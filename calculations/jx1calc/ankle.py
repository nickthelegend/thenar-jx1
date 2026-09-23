"""Parallel two-push-rod ankle: exact closed-form crank angles and joint<->motor Jacobian.

Geometry (shin frame, origin at the ankle centre, zero pose, left leg):
  motor i crank axis parallel to y through (0, yc_i, h_i); crank of radius r points backwards (-x) at phi = 0
  crank end  C_i(phi) = (-r cos phi, yc_i, h_i + r sin phi)
  foot attachment F_i(q) = R_y(pitch) R_x(roll) (-a, yf_i, 0)   (ball joint behind the ankle)
  rod length L_i = |C_i(0) - F_i(0)|   (rods may lean in the frontal plane when yc_i != yf_i)
Motor A is on +y (lateral for the left leg, upper), motor B on -y (medial, lower).
"""
from __future__ import annotations

import numpy as np

from .kinematics import rx, ry


class ParallelAnkle:
    def __init__(self, crank_r, foot_lever, foot_half_spacing, heights, crank_half_spacing=None):
        self.r, self.a = crank_r, foot_lever
        hA, hB = (heights, heights) if np.isscalar(heights) else heights
        wc = foot_half_spacing if crank_half_spacing is None else crank_half_spacing
        self.h = (hA, hB)
        self.yc = (+wc, -wc)
        self.yf = (+foot_half_spacing, -foot_half_spacing)
        self.L = tuple(float(np.linalg.norm(np.array([-self.r, self.yc[i], self.h[i]]) - np.array([-self.a, self.yf[i], 0.0])))
                       for i in range(2))

    def attach(self, pitch, roll, i):
        return ry(pitch) @ rx(roll) @ np.array([-self.a, self.yf[i], 0.0])

    def crank_angles(self, pitch, roll):
        phis = []
        for i in range(2):
            F = self.attach(pitch, roll, i)
            dz = self.h[i] - F[2]
            dy = self.yc[i] - F[1]
            a = 2 * self.r * F[0]
            b = 2 * self.r * dz
            c = self.L[i] ** 2 - F[0] ** 2 - self.r ** 2 - dy ** 2 - dz ** 2
            rho = np.hypot(a, b)
            if abs(c) > rho:
                raise ValueError("ankle linkage cannot reach this pose")
            base = np.arctan2(b, a)
            cand = [base + np.arccos(c / rho), base - np.arccos(c / rho)]
            cand = [(p + np.pi) % (2 * np.pi) - np.pi for p in cand]
            phis.append(min(cand, key=abs))
        return np.array(phis)

    def jacobian(self, pitch, roll, eps=1e-6):
        """J = d(phi_A, phi_B)/d(pitch, roll)."""
        J = np.zeros((2, 2))
        for k, (dp, dr) in enumerate([(eps, 0), (0, eps)]):
            J[:, k] = (self.crank_angles(pitch + dp, roll + dr) - self.crank_angles(pitch - dp, roll - dr)) / (2 * eps)
        return J

    def motor_torques(self, pitch, roll, tau_pitch, tau_roll):
        """Static duality: tau_q = J^T tau_m  ->  tau_m = J^-T tau_q."""
        J = self.jacobian(pitch, roll)
        return np.linalg.solve(J.T, np.array([tau_pitch, tau_roll]))

    def motor_speeds(self, pitch, roll, dpitch, droll):
        return self.jacobian(pitch, roll) @ np.array([dpitch, droll])


def from_design(d):
    return ParallelAnkle(d.crank_r, d.foot_lever, d.rod_half_spacing, (d.ankle_hA, d.ankle_hB), d.crank_half_spacing)
