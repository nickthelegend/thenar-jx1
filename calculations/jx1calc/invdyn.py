"""Floating-base inverse dynamics with contact-wrench distribution between the feet.

For each sample: qfrc = M(q) qacc + c(q, qdot) (MuJoCo mj_inverse, contacts & constraints disabled).
The 6 floating-base rows must be supplied by the foot wrenches w_i (force + moment at each sole site):
    qfrc[0:6] = sum_i J_i[:, 0:6]^T w_i
Single support: 6x6 solve. Double support: weighted least-norm with moments penalised (feet share load
by the lever rule, ankle moments minimised). Joint torques: tau = qfrc[6:] - sum_i J_i[:, 6:]^T w_i.
"""
from __future__ import annotations

import mujoco
import numpy as np


def finite_diff(model, qpos, dt):
    n = len(qpos)
    qvel = np.zeros((n, model.nv))
    for i in range(n):
        a, b = max(i - 1, 0), min(i + 1, n - 1)
        v = np.zeros(model.nv)
        mujoco.mj_differentiatePos(model, v, (b - a) * dt, qpos[a], qpos[b])
        qvel[i] = v
    qacc = np.zeros_like(qvel)
    for i in range(n):
        a, b = max(i - 1, 0), min(i + 1, n - 1)
        qacc[i] = (qvel[b] - qvel[a]) / ((b - a) * dt)
    return qvel, qacc


def inverse_dynamics(model, qpos, qvel, qacc, contact, moment_weight=1.0e4, cop_min_load_fraction=0.10):
    data = mujoco.MjData(model)
    model.opt.disableflags |= int(mujoco.mjtDisableBit.mjDSBL_CONTACT) | int(mujoco.mjtDisableBit.mjDSBL_CONSTRAINT)
    sites = [mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, f"{s}_sole") for s in "lr"]
    n = len(qpos)
    nj = model.nv - 6
    tau = np.zeros((n, nj))
    wrench = np.zeros((n, 2, 6))
    cop = np.full((n, 2, 2), np.nan)       # CoP in each sole frame (x,y) relative to the sole site
    friction = np.full((n, 2), np.nan)
    site_pos = np.zeros((n, 2, 3))
    zmp = np.full((n, 2), np.nan)
    jacp = np.zeros((3, model.nv))
    jacr = np.zeros((3, model.nv))
    Wdiag = np.array([1, 1, 1, moment_weight, moment_weight, moment_weight], float)
    weight = float(sum(model.body_mass)) * 9.81
    fz_min = cop_min_load_fraction * weight  # CoP of a nearly unloaded foot is numerically meaningless
    for i in range(n):
        data.qpos[:] = qpos[i]
        data.qvel[:] = qvel[i]
        data.qacc[:] = qacc[i]
        mujoco.mj_inverse(model, data)
        qf = data.qfrc_inverse.copy()
        J = []
        for sid in sites:
            mujoco.mj_jacSite(model, data, jacp, jacr, sid)
            J.append(np.vstack([jacp, jacr]).copy())  # 6 x nv  (force rows, moment rows)
        active = [k for k in range(2) if contact[i, k]]
        w = np.zeros((2, 6))
        if len(active) == 1:
            k = active[0]
            w[k] = np.linalg.solve(J[k][:, :6].T, qf[:6])
        else:
            # Double support. 1) any exact solution for the total wrench (least-norm), 2) redistribute by
            # the lever rule: each foot's share of force follows the ZMP position along the segment between
            # the two sole points, so load transfers continuously and the lifting foot unloads to zero.
            A = np.hstack([J[0][:, :6].T, J[1][:, :6].T])  # 6 x 12
            Winv = np.diag(1.0 / np.tile(Wdiag, 2))
            x = Winv @ A.T @ np.linalg.solve(A @ Winv @ A.T, qf[:6])
            w0 = np.array([x[:6], x[6:]])
            sp = np.array([data.site_xpos[sid].copy() for sid in sites])
            F = w0[0, :3] + w0[1, :3]
            M = w0[0, 3:] + w0[1, 3:] + np.cross(sp[0], w0[0, :3]) + np.cross(sp[1], w0[1, :3])
            zmp_xy = np.array([-M[1] / F[2], M[0] / F[2]]) if F[2] > 1e-6 else sp[:, :2].mean(axis=0)
            seg = sp[0, :2] - sp[1, :2]
            alpha = float(np.clip(np.dot(zmp_xy - sp[1, :2], seg) / max(np.dot(seg, seg), 1e-12), 0.0, 1.0))
            share = np.array([alpha, 1.0 - alpha])
            f = [share[k] * F for k in range(2)]
            m_res = M - np.cross(sp[0], f[0]) - np.cross(sp[1], f[1])
            w = np.array([np.r_[f[k], share[k] * m_res] for k in range(2)])
        gen = sum(J[k].T @ w[k] for k in range(2))
        sp = np.array([data.site_xpos[sid].copy() for sid in sites])
        site_pos[i] = sp
        F = w[0, :3] + w[1, :3]
        M = w[0, 3:] + w[1, 3:] + np.cross(sp[0], w[0, :3]) + np.cross(sp[1], w[1, :3])
        if F[2] > 1e-6:  # whole-robot ZMP on the ground plane z = 0
            zmp[i] = [-M[1] / F[2], M[0] / F[2]]
        tau[i] = qf[6:] - gen[6:]
        wrench[i] = w
        for k in range(2):
            if contact[i, k] and w[k, 2] > fz_min:
                data_site_R = data.site_xmat[sites[k]].reshape(3, 3)
                f_loc = data_site_R.T @ w[k, :3]
                m_loc = data_site_R.T @ w[k, 3:]
                cop[i, k] = [-m_loc[1] / f_loc[2], m_loc[0] / f_loc[2]]
                friction[i, k] = np.hypot(f_loc[0], f_loc[1]) / f_loc[2]
    model.opt.disableflags = 0
    return {"tau": tau, "wrench": wrench, "cop": cop, "friction": friction, "site_pos": site_pos, "zmp": zmp}
