"""Parallel two-push-rod ankle: exact closed-form crank angles and joint<->motor Jacobian.

Geometry (shin frame, origin at the ankle centre, zero pose, left leg):
  motor i crank axis parallel to y through (0, y_i, h); crank of radius r points backwards (-x) at phi=0
  crank end  C_i(phi) = (-r cos phi, y_i, h + r sin phi)
  foot attachment F_i(q) = R_y(pitch) R_x(roll) (-a, y_i, 0)   (ball joint behind the ankle)
  rod length L = |C_i(0) - F_i(0)| = h  (rods vertical at zero)
Motor A is on +y (lateral for the left leg), motor B on -y.
"""
from __future__ import annotations

import numpy as np

from .kinematics import rx, ry


class ParallelAnkle:
    def __init__(self, crank_r, foot_lever, half_spacing, height):
        self.r, self.a, self.w, self.h = crank_r, foot_lever, half_spacing, height
        self.ys = (+half_spacing, -half_spacing)
        self.L = height  # vertical rods at the zero pose

    def attach(self, pitch, roll, y):
        return ry(pitch) @ rx(roll) @ np.array([-self.a, y, 0.0])

    def crank_angles(self, pitch, roll):
        phis = []
        for y in self.ys:
            F = self.attach(pitch, roll, y)
            # |(-r cos p - Fx, y - Fy, h + r sin p - Fz)|^2 = L^2  ->  a cos p + b sin p = c
            dz = self.h - F[2]
            a = 2 * self.r * F[0]
            b = 2 * self.r * dz
            c = self.L ** 2 - F[0] ** 2 - self.r ** 2 - (y - F[1]) ** 2 - dz ** 2
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
