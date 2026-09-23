"""ZMP preview control on the linear inverted pendulum (Kajita et al., ICRA 2003).

State per horizontal axis: x = [c, c_dot, c_ddot], input u = CoM jerk, output ZMP p = c - (zc/g) c_ddot.
u_k = -K x_k + sum_{j=1..N} f_j p_ref[k+j]
"""
from __future__ import annotations

import numpy as np
from scipy.linalg import solve_discrete_are

G = 9.81


class PreviewController:
    def __init__(self, zc, dt=0.005, preview_s=1.6, q=1.0, r=1e-6):
        self.zc, self.dt = zc, dt
        self.N = int(round(preview_s / dt))
        A = np.array([[1, dt, dt * dt / 2], [0, 1, dt], [0, 0, 1]])
        B = np.array([[dt ** 3 / 6], [dt * dt / 2], [dt]])
        C = np.array([[1, 0, -zc / G]])
        Q = C.T @ C * q
        R = np.array([[r]])
        P = solve_discrete_are(A, B, Q, R)
        S = R + B.T @ P @ B
        K = np.linalg.solve(S, B.T @ P @ A)
        Ac = A - B @ K
        f = np.zeros(self.N)
        X = C.T * q
        for j in range(self.N):
            f[j] = np.linalg.solve(S, B.T @ X).item()
            X = Ac.T @ X
        self.A, self.B, self.C, self.K, self.f = A, B, C, K, f

    def run(self, zmp_ref, x0=None):
        """zmp_ref: (T,) reference; returns CoM pos, vel, acc and the achieved ZMP (T,)."""
        T = len(zmp_ref)
        pad = np.concatenate([zmp_ref, np.full(self.N + 1, zmp_ref[-1])])
        x = np.zeros((3, 1)) if x0 is None else np.asarray(x0, float).reshape(3, 1)
        out = np.zeros((T, 3))
        zmp = np.zeros(T)
        for k in range(T):
            out[k] = x[:, 0]
            zmp[k] = (self.C @ x).item()
            u = -(self.K @ x).item() + float(self.f @ pad[k + 1:k + 1 + self.N])
            x = self.A @ x + self.B * u
        return out[:, 0], out[:, 1], out[:, 2], zmp
