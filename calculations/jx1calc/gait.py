"""Walking-pattern synthesis: footsteps -> ZMP reference -> LIPM CoM -> whole-body joint trajectory."""
from __future__ import annotations

from dataclasses import dataclass, field

import mujoco
import numpy as np

from .design import Design, LEG_JOINTS
from .kinematics import leg_ik, rz
from .lipm import PreviewController


@dataclass
class GaitParams:
    name: str
    step_length: float = 0.20      # forward advance per step (m)
    step_width: float = None       # lateral distance between feet centres (m); default hip spacing
    step_time: float = 0.45        # s per step (double + single support)
    ds_ratio: float = 0.2
    step_height: float = 0.05
    n_steps: int = 8
    hip_height: float = 0.54       # nominal hip-centre height above ground (m)
    zmp_offset_x: float = 0.015    # ZMP reference ahead of the ankle projection during single support
    lateral_step: float = 0.0      # sideways advance per step (m)
    turn_per_step_deg: float = 0.0
    dt: float = 0.005
    t_start: float = 0.8
    t_end: float = 1.2
    pelvis_height_profile: object = None   # optional callable t -> hip-height override (squats etc.)


@dataclass
class Plan:
    t: np.ndarray
    zmp_ref: np.ndarray            # (T,2)
    feet: dict                     # side -> (T,3) ankle-projection-on-ground positions (x,y,z of ankle centre)
    feet_yaw: dict                 # side -> (T,)
    contact: np.ndarray            # (T,2) bool [left, right]
    phase: list = field(default_factory=list)


def min_jerk(s):
    s = np.clip(s, 0, 1)
    return 10 * s ** 3 - 15 * s ** 4 + 6 * s ** 5


def plan_steps(d: Design, g: GaitParams) -> Plan:
    w = g.step_width if g.step_width is not None else d.hip_spacing
    dt = g.dt
    T_ds = g.step_time * g.ds_ratio
    total = g.t_start + g.n_steps * g.step_time + T_ds + g.t_end
    t = np.arange(0, total, dt)
    n = len(t)
    ankle_z = d.sole_to_ankle
    pos = {"l": np.array([0.0, w / 2]), "r": np.array([0.0, -w / 2])}
    yaw = {"l": 0.0, "r": 0.0}
    heading = 0.0
    turn = np.radians(g.turn_per_step_deg)
    zmp_keys = []   # (t0, t1, from, to): linear ZMP transfer during double support
    events = []     # (t0, t1, swing side, p0, p1, yaw0, yaw1): single-support swing
    tk = g.t_start
    prev_zmp = (pos["l"] + pos["r"]) / 2
    swing = "r"
    for k in range(1, g.n_steps + 1):
        stance = "l" if swing == "r" else "r"
        last = k == g.n_steps
        new_heading = heading if last else heading + turn
        side = 1 if swing == "l" else -1
        fwd = np.array([np.cos(new_heading), np.sin(new_heading)])
        lat = np.array([-np.sin(new_heading), np.cos(new_heading)])
        if last:
            target = pos[stance] + lat * side * w
        else:
            advance = g.step_length / 2 if k == 1 else g.step_length
            target = pos[stance] + fwd * advance + lat * side * w + lat * g.lateral_step
        stance_zmp = pos[stance] + np.array([np.cos(yaw[stance]), np.sin(yaw[stance])]) * g.zmp_offset_x
        zmp_keys.append((tk, tk + T_ds, prev_zmp.copy(), stance_zmp.copy()))
        events.append((tk + T_ds, tk + g.step_time, swing, pos[swing].copy(), target.copy(), yaw[swing], new_heading))
        pos[swing], yaw[swing] = target, new_heading
        heading, prev_zmp = new_heading, stance_zmp
        tk += g.step_time
        swing = stance
    zmp_keys.append((tk, tk + T_ds, prev_zmp.copy(), (pos["l"] + pos["r"]) / 2))

    feet = {s: np.zeros((n, 3)) for s in "lr"}
    feet_yaw = {s: np.zeros(n) for s in "lr"}
    contact = np.ones((n, 2), bool)
    zmp = np.zeros((n, 2))
    phase = ["ds"] * n
    for i, ti in enumerate(t):
        z = np.zeros(2)
        for (a, b, p0, p1) in zmp_keys:
            if ti >= b:
                z = p1
            elif ti >= a:
                z = p0 + (p1 - p0) * (ti - a) / (b - a)
                break
            else:
                break
        zmp[i] = z
        cur = {"l": np.array([0.0, w / 2]), "r": np.array([0.0, -w / 2])}
        cyaw = {"l": 0.0, "r": 0.0}
        zlift = {"l": 0.0, "r": 0.0}
        for (a, b, sw, p0, p1, y0, y1) in events:
            if ti >= b:
                cur[sw], cyaw[sw] = p1, y1
            elif ti >= a:
                s = (ti - a) / (b - a)
                m = min_jerk(s)
                cur[sw] = p0 + (p1 - p0) * m
                cyaw[sw] = y0 + (y1 - y0) * m
                zlift[sw] = 64 * g.step_height * s ** 3 * (1 - s) ** 3
                contact[i, 0 if sw == "l" else 1] = False
                phase[i] = "ss_l" if sw == "r" else "ss_r"
                break
            else:
                break
        for s in "lr":
            feet[s][i] = [cur[s][0], cur[s][1], ankle_z + zlift[s]]
            feet_yaw[s][i] = cyaw[s]
    return Plan(t=t, zmp_ref=zmp, feet=feet, feet_yaw=feet_yaw, contact=contact, phase=phase)


class WholeBody:
    """Helper around the analysis MuJoCo model for FK/COM/IK."""

    def __init__(self, model: mujoco.MjModel, design: Design):
        self.m, self.d = model, mujoco.MjData(model)
        self.design = design
        self.pelvis_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, "pelvis")
        self.qadr = {}
        for s in "lr":
            for j in LEG_JOINTS:
                jid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, f"{s}_{j}")
                self.qadr[f"{s}_{j}"] = model.jnt_qposadr[jid]
        self.leg_qadr = {s: [self.qadr[f"{s}_{j}"] for j in LEG_JOINTS] for s in "lr"}

    def set_state(self, p_pelvis, yaw, q_legs):
        qpos = np.zeros(self.m.nq)
        qpos[:3] = p_pelvis
        qpos[3:7] = [np.cos(yaw / 2), 0, 0, np.sin(yaw / 2)]
        for s in "lr":
            qpos[self.leg_qadr[s]] = q_legs[s]
        return qpos

    def com(self, qpos):
        self.d.qpos[:] = qpos
        mujoco.mj_kinematics(self.m, self.d)
        mujoco.mj_comPos(self.m, self.d)
        return self.d.subtree_com[self.pelvis_id].copy()

    def ik(self, p_pelvis, yaw, feet_pos, feet_yaw):
        d = self.design
        R = rz(yaw)
        q = {}
        for s, sgn in (("l", 1), ("r", -1)):
            hip = p_pelvis + R @ np.array([0, sgn * d.hip_spacing / 2, 0])
            q[s] = leg_ik(hip, R, feet_pos[s], rz(feet_yaw[s]), d.thigh, d.shin)
        return q


def _build_trajectory(wb, design, g, plan, cx, cy, zc, offset0, com_iters):
    n = len(plan.t)
    qpos = np.zeros((n, wb.m.nq))
    offset = offset0.copy()
    for i in range(n):
        yaw = 0.5 * (plan.feet_yaw["l"][i] + plan.feet_yaw["r"][i])
        hh = g.hip_height if g.pelvis_height_profile is None else g.pelvis_height_profile(plan.t[i])
        target_com = np.array([cx[i], cy[i], zc - (g.hip_height - hh)])
        feet = {s: plan.feet[s][i] for s in "lr"}
        fy = {s: plan.feet_yaw[s][i] for s in "lr"}
        off = offset.copy()
        for _ in range(com_iters):
            p = target_com - off
            p[2] = hh  # height is prescribed directly by the hip-height profile
            q = wb.ik(p, yaw, feet, fy)
            qp = wb.set_state(p, yaw, q)
            c = wb.com(qp)
            off = c - p
        offset = off
        qpos[i] = qp
    return qpos


def synthesize(model, design: Design, g: GaitParams, plan: Plan | None = None, com_iters=4, zmp_iters=3):
    """Two-stage preview control (Kajita et al. 2003, sec. IV): LIPM CoM from the ZMP reference, then
    iterative CoM corrections from the multibody ZMP error so the full rigid-body trajectory keeps its
    ZMP on the reference (i.e. inside the support polygon). Returns qpos trajectory and diagnostics."""
    from .invdyn import finite_diff, inverse_dynamics
    plan = plan or plan_steps(design, g)
    wb = WholeBody(model, design)
    feet0 = {s: plan.feet[s][0] for s in "lr"}
    p0 = np.array([0.0, 0.0, g.hip_height])
    q0 = wb.ik(p0, 0.0, feet0, {s: 0.0 for s in "lr"})
    c0 = wb.com(wb.set_state(p0, 0.0, q0))
    zc = c0[2]
    pc = PreviewController(zc=zc, dt=g.dt)
    cx, _, _, zx = pc.run(plan.zmp_ref[:, 0])
    cy, _, _, zy = pc.run(plan.zmp_ref[:, 1])
    corr = np.zeros((len(plan.t), 2))
    history = []
    for it in range(zmp_iters + 1):
        qpos = _build_trajectory(wb, design, g, plan, cx + corr[:, 0], cy + corr[:, 1], zc, c0 - p0, com_iters)
        qvel, qacc = finite_diff(model, qpos, g.dt)
        idr = inverse_dynamics(model, qpos, qvel, qacc, plan.contact)
        err = idr["zmp"] - plan.zmp_ref
        err = np.nan_to_num(err)
        history.append(float(np.abs(err).max()))
        if it == zmp_iters:
            break
        corr[:, 0] += pc.run(-err[:, 0])[0]
        corr[:, 1] += pc.run(-err[:, 1])[0]
    return {"t": plan.t, "qpos": qpos, "qvel": qvel, "qacc": qacc, "idr": idr, "com_ref": np.c_[cx + corr[:, 0], cy + corr[:, 1]],
            "zmp_lipm": np.c_[zx, zy], "plan": plan, "zc": zc, "zmp_error_history_m": history}
