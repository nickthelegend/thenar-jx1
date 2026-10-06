"""Does JX0 really walk? Robustness of the verified gaits + the robot's balance controller (jx0bot/balance.py) when the
real robot differs from the model, and when it is pushed.

Model-error trials: each trial walks a gait in MuJoCo with randomly wrong "reality":
  servo stiffness x0.6-1.4 and damping x0.5-1.5, servo torque/speed x0.85-1.0 (battery sag), bus latency 0-40 ms,
  gear backlash 0-0.6 deg, IMU noise (0.3 deg, 0.02 rad/s) and bias +-1 deg, upper-body mass x0.9-1.1 with its centre
  of mass off by up to 8 mm (x) / 4 mm (y), floor friction 0.5-1.0, floor slope up to +-2 deg in both directions.
Push trials: a sideways shove on the torso (0.12 s) at 24 moments of a 10-step walk, both directions.

    python jx0/verify/robustness.py baseline        # evaluate the current balance gains
    python jx0/verify/robustness.py tune            # random search for better gains, then evaluate them
    -> jx0/results/verify_robustness.json
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from collections import deque
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "jx0" / "sim"))           # module level: Windows worker processes re-import this file
sys.path.insert(0, str(ROOT / "jx0" / "software"))
os.environ["JX0_STL_DIR"] = str(ROOT / "nonexistent")   # physics only: plain box visuals load faster
OUT = ROOT / "jx0" / "results" / "verify_robustness.json"
MC_GAITS = ["forward", "forward_4", "backward_4", "turn_left_2", "turn_right_2", "side_left_2", "side_right_2"]
_CACHE = {}


def _setup(gait, overrides=None):
    key = (gait, json.dumps(overrides or {}, sort_keys=True))
    if key not in _CACHE:
        os.environ["JX0_STL_DIR"] = str(ROOT / "nonexistent")       # physics only: plain box visuals load faster
        sys.path.insert(0, str(ROOT / "jx0" / "sim"))
        sys.path.insert(0, str(ROOT / "jx0" / "software"))
        import mujoco
        import walk_jx0 as W
        from jx1calc.design import Design
        design = Design(W.DESIGN)
        xml = W.build(design)
        m = mujoco.MjModel.from_xml_string(xml)
        saved, saved_g = dict(W.COMMON), dict(W.GAITS[gait])
        ov = dict(overrides or {})
        if "step_time" in ov:                                        # per-gait parameter
            W.GAITS[gait]["step_time"] = ov.pop("step_time")
        W.COMMON.update(ov)
        try:
            g, res = W.plan(m, design, gait)
        finally:
            W.COMMON.clear()
            W.COMMON.update(saved)
            W.GAITS[gait] = saved_g
        _CACHE[key] = (xml, g, res, design.act_classes["ST"])
    return _CACHE[key]


def nominal():
    return {"kp": 1.0, "kd": 1.0, "stall": 1.0, "latency": 0, "backlash_deg": 0.0, "imu_deg": 0.0, "gyro": 0.0,
            "bias_deg": [0.0, 0.0], "mass": 1.0, "com_mm": [0.0, 0.0], "mu": 0.9, "slope_deg": [0.0, 0.0]}


def sample(rng, latencies=(0, 1, 2)):
    return {"kp": rng.uniform(0.6, 1.4), "kd": rng.uniform(0.5, 1.5), "stall": rng.uniform(0.85, 1.0),
            "latency": int(rng.choice(latencies)), "backlash_deg": rng.uniform(0.0, 0.6), "imu_deg": 0.3, "gyro": 0.02,
            "bias_deg": list(rng.uniform(-1.0, 1.0, 2)), "mass": rng.uniform(0.9, 1.1),
            "com_mm": [rng.uniform(-8, 8), rng.uniform(-4, 4)], "mu": rng.uniform(0.5, 1.0),
            "slope_deg": list(rng.uniform(-2.0, 2.0, 2))}


GAIT_DIR = ROOT / "jx0" / "software" / "jx0bot" / "gaits"
ENC = 2 * math.pi / 4096                                   # STS3215 encoder step: what the robot reads back


def trial(spec):
    """One walk. spec: gait, scenario, gains (balance.py overrides), push (t, N toward +y, s) or None, seed;
    capture: True plays the gait through jx0bot.stepper (capture-point stepping, as the robot does), with `params`."""
    import mujoco
    import walk_jx0 as W
    from jx0bot.balance import Balance
    from jx0bot.stepper import CaptureStepper
    xml, g, res, st = _setup(spec["gait"], spec.get("gait_overrides"))
    sc, rng = spec["scenario"], np.random.default_rng(spec.get("seed", 0))
    m = mujoco.MjModel.from_xml_string(xml)
    oid = lambda kind, n: mujoco.mj_name2id(m, kind, n)  # noqa: E731
    torso = oid(mujoco.mjtObj.mjOBJ_BODY, "torso")
    m.body_mass[torso] *= sc["mass"]
    m.body_ipos[torso][:2] += np.array(sc["com_mm"]) * 1e-3
    for gname in ("l_foot_geom", "r_foot_geom", "floor"):
        m.geom_friction[oid(mujoco.mjtObj.mjOBJ_GEOM, gname)][0] = sc["mu"]
    ax, ay = (math.radians(v) for v in sc["slope_deg"])
    m.opt.gravity[:] = 9.81 * np.array([math.sin(ay) * math.cos(ax), -math.sin(ax), -math.cos(ax) * math.cos(ay)])
    d = mujoco.MjData(m)

    t_ref, q_ref, contact = res["t"], res["qpos"], res["plan"].contact
    names = [f"{s}_{j}" for s in "lr" for j in W.LEG_JOINTS] + [f"{s}_{j}" for s in "lr" for j in W.ARM_JOINTS] + ["neck_yaw"]
    adr = {n: (m.jnt_qposadr[oid(mujoco.mjtObj.mjOBJ_JOINT, n)], m.jnt_dofadr[oid(mujoco.mjtObj.mjOBJ_JOINT, n)]) for n in names}
    act = {n: oid(mujoco.mjtObj.mjOBJ_ACTUATOR, n) for n in names}
    servo = W.ServoModel(st["stall_torque_nm"] * sc["stall"], st["no_load_speed_rad_s"] * sc["stall"], 60.0 * sc["kp"], 0.6 * sc["kd"])
    d.qpos[:] = q_ref[0]
    for n, v in W.arm_goals(q_ref[0], q_ref[0], adr).items():
        d.qpos[adr[n][0]] = v
    d.qpos[2] += 0.002
    mujoco.mj_forward(m, d)
    dt, T = m.opt.timestep, float(t_ref[-1])
    frame = 1.0 / spec.get("bus_hz", W.BUS_HZ)
    period = int(round(frame / dt))
    goal = {n: float(d.qpos[adr[n][0]]) for n in names}
    lag = int(round(sc["latency"] * 0.02 / frame))                 # latency is given in 20 ms units
    pipe = deque([dict(goal)] * (lag + 1), maxlen=lag + 1)
    bal = Balance(spec.get("gains"), dt=frame)
    stepper = None
    if spec.get("capture"):
        stepper = CaptureStepper(json.loads((GAIT_DIR / f"{spec['gait']}.json").read_text(encoding="utf-8")),
                                 spec.get("gains"), spec.get("params"))
        stepper.start()
    bl = math.radians(sc["backlash_deg"]) / 2
    bias = [math.radians(v) for v in sc["bias_deg"]]
    fell, max_tilt, hist = False, 0.0, []
    loads = {} if spec.get("loads") else None
    series = {} if spec.get("series") else None
    for k in range(int(T / dt)):
        t = k * dt
        i = min(int(round(t / g.dt)), len(t_ref) - 1)
        roll, pitch, yaw = W.rpy(d.qpos[3:7])
        if k % period == 0:
            n_deg = math.radians(sc["imu_deg"])
            r_m, p_m = roll + bias[0] + rng.normal(0, n_deg), pitch + bias[1] + rng.normal(0, n_deg)
            wx, wy = d.qvel[3] + rng.normal(0, sc["gyro"]), d.qvel[4] + rng.normal(0, sc["gyro"])
            if stepper is not None:
                q_enc = {n: round(float(d.qpos[adr[n][0]]) / ENC) * ENC for n in names}
                new = {**goal, **stepper.frame(min(int(round(t / frame)), stepper.n - 1), q_enc, r_m, p_m, wx, wy)}
            else:
                corr = bal.update(r_m, p_m, wx, wy, contact[min(i, len(contact) - 1)])
                arms = W.arm_goals(q_ref[i], q_ref[0], adr)
                new = {n: float((q_ref[i, adr[n][0]] if n.split("_", 1)[1] in W.LEG_JOINTS else arms.get(n, 0.0)) + corr.get(n, 0.0))
                       for n in names}
            pipe.append(new)
            goal = pipe[0]                                  # what the servos act on, `latency` frames late
        for n in names:
            qa, da = adr[n]
            err = goal[n] - d.qpos[qa]
            err = 0.0 if abs(err) < bl else err - math.copysign(bl, err)       # gear backlash
            d.ctrl[act[n]] = servo.torque(d.qpos[qa] + err, d.qpos[qa], d.qvel[da])
        if spec.get("push") is not None:
            tp, f, dur = spec["push"][:3]
            d.xfrc_applied[torso, spec["push"][3] if len(spec["push"]) > 3 else 1] = f if tp <= t < tp + dur else 0.0
        mujoco.mj_step(m, d)
        if loads is not None and k % 2 == 0:
            joint_loads(m, d, loads)
        if series is not None and k % 10 == 0:
            joint_wrench_series(m, d, series)
        if k % 10 == 0:
            tilt = math.degrees(math.hypot(roll, pitch))
            max_tilt = max(max_tilt, tilt)
            hist.append((*d.qpos[:2], *q_ref[i, :2], yaw, W.rpy(q_ref[i, 3:7])[2], roll, pitch, t))
            if d.qpos[2] < 0.13 or tilt > 30:
                fell = True
                break
    h = np.array(hist)
    dist_plan = float(np.linalg.norm(q_ref[-1, :2] - q_ref[0, :2]))
    pos_err = float(np.linalg.norm(h[-1, 0:2] - h[-1, 2:4]))
    head_err = math.degrees((h[-1, 4] - h[-1, 5] + math.pi) % (2 * math.pi) - math.pi)
    ok = (not fell) and pos_err <= 0.05 + 0.10 * dist_plan and abs(head_err) < 10.0
    return {"gait": spec["gait"], "fell": fell, "pass": bool(ok), "pos_err_m": round(pos_err, 3),
            "heading_err_deg": round(head_err, 1), "max_tilt_deg": round(max_tilt, 1), "push": spec.get("push"),
            "end_roll_deg": round(math.degrees(h[-1, 6]), 1), "end_pitch_deg": round(math.degrees(h[-1, 7]), 1),
            "end_t_s": round(float(h[-1, 8]), 2), **({"loads": loads} if loads is not None else {}),
            **({"series": series} if series is not None else {})}


LOAD_JOINTS = [f"{s}_{j}" for s in "lr" for j in ("hip_yaw", "hip_roll", "hip_pitch", "knee", "ankle_pitch", "ankle_roll")]


def _servo_points():
    """Per leg joint: offsets along the joint axis (m, left leg; the right mirrors the y-axis joints) from the joint's
    anchor to the servo's output horn face and to the servo's centre (the middle of a U-bracket's two arms)."""
    sys.path.insert(0, str(ROOT / "jx0" / "cad"))
    import geometry as G
    hf = G.HF / 1000
    return {"hip_yaw": (G.ZY / 1000, (G.ZY + G.HF) / 1000), "hip_roll": (G.XR / 1000, (G.XR - G.HF) / 1000),
            "hip_pitch": (hf, 0.0), "knee": (hf, 0.0), "ankle_pitch": (hf, 0.0),
            "ankle_roll": (G.XA / 1000, (G.XA - G.HF) / 1000)}


_SP = None


def joint_wrench_series(m, d, series):
    """Left-leg joints: the 6-axis load (force N, moment N m about the servo's centre) the joint passes between its two
    links, expressed in the parent link's frame and in the child link's frame (verify_fea superposes per instant)."""
    import mujoco
    global _SP
    _SP = _SP or _servo_points()
    mujoco.mj_rnePostConstraint(m, d)
    c = d.subtree_com[0]
    for n in LOAD_JOINTS[:6]:
        j = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
        b = m.jnt_bodyid[j]
        a, p = d.xaxis[j], d.xanchor[j]
        tau_c, f = d.cfrc_int[b][:3], d.cfrc_int[b][3:]
        q = p + a * _SP[n[2:]][1]
        tq = tau_c + np.cross(c - q, f)
        Rp, Rc = d.xmat[m.body_parentid[b]].reshape(3, 3), d.xmat[b].reshape(3, 3)
        e = series.setdefault(n, {"parent": [], "child": []})
        e["parent"].append([round(float(v), 4) for v in np.concatenate([Rp.T @ f, Rp.T @ tq])])
        e["child"].append([round(float(v), 4) for v in np.concatenate([Rc.T @ f, Rc.T @ tq])])


YAW_RING_R = 0.016           # m: effective radius of the hip-yaw thrust ring's contact (11.5..19 mm ring)
KEEP_R, KEEP_CAP = 0.0175, 100.0   # m: radius of the ring's and the keeper lip's contact on the disc rim; N: the most the
                                   # keeper's lip is designed for (verify_fea); beyond it the yaw servo's shaft takes the rest


def keeper_arc(side):
    """The keeper's arc (degrees, pelvis frame) for the left ('l') or right ('r') leg."""
    sys.path.insert(0, str(ROOT / "jx0" / "cad"))
    import geometry as G
    a0, a1 = G.KEEP_ARC
    return (a0, a1) if side == "l" else (-a1, -a0)


def keeper_split(M, C, arc, cap=KEEP_CAP, R=KEEP_R, n=49):
    """How the hip-yaw disc's load is shared, instant by instant (vectorised over T instants).
    M (T, 2): bending moment the pelvis passes to the leg at the disc (N m, pelvis frame); C (T,): the disc's
    compression into the thrust ring (N, minus the axial force). The thrust ring (a full circle) can only push the disc
    down, the keeper's lip (only on its arc) only up. Least-force contact pair that carries C and M; if none exists
    within `cap`, the yaw servo's shaft takes the smallest leftover bending.
    Returns lip force L, ring force N (T,), shaft bending (T,) N m, lip angle, ring angle (T,) degrees."""
    M = np.atleast_2d(np.asarray(M, float))
    C = np.atleast_1d(np.asarray(C, float))
    th = np.radians(np.linspace(arc[0], arc[1], n))
    v = np.stack([np.sin(th), -np.cos(th)], 1)                # moment direction of a lip push at each arc point
    a = M / R
    m = np.linalg.norm(a, axis=1)
    den = a @ v.T + C[:, None]
    with np.errstate(divide="ignore", invalid="ignore"):
        L = (m[:, None] ** 2 - C[:, None] ** 2) / (2 * den)
    N = C[:, None] + L
    good = (den > 1e-9) & (L >= 0) & (N >= 0) & (L <= cap)
    score = np.where(good, np.maximum(L, N), np.inf)
    k = score.argmin(1)
    feasible = np.isfinite(score.min(1))
    ring_only = (C > 0) & (m <= C)
    # no contact pair within the cap (mostly the swing leg hanging from the disc): the least lip force that leaves the
    # shaft within 0.01 N m of the smallest bending it can be left with
    idx = np.arange(len(C))
    Lc, kc, shaft_c = np.zeros(len(C)), np.zeros(len(C), int), np.zeros(len(C))
    bad = np.nonzero(~feasible & ~ring_only)[0]
    if len(bad):
        Ls = np.array([0.0, 2.0, 5.0, 10.0, 20.0, 35.0, 50.0, 70.0, cap])
        ab = a[bad][:, None, None, :]
        lv = Ls[None, :, None, None] * v[None, None, :, :]
        lift = np.maximum(0.0, Ls[None, :, None] + C[bad][:, None, None])            # the ring cannot pull
        ex = np.maximum(0.0, np.linalg.norm(ab - lv, axis=3) - lift) * R               # (nb, nL, ntheta)
        best_th = ex.argmin(2)
        ex_l = np.take_along_axis(ex, best_th[:, :, None], 2)[:, :, 0]                # (nb, nL)
        pick = (ex_l <= ex_l.min(1, keepdims=True) + 0.01).argmax(1)
        Lc[bad], kc[bad] = Ls[pick], best_th[np.arange(len(bad)), pick]
        shaft_c[bad] = ex_l[np.arange(len(bad)), pick]
    k = np.where(feasible, k, kc)
    Lk = np.where(ring_only, 0.0, np.where(feasible, L[idx, k], Lc))
    Nk = np.where(ring_only, np.maximum(C, 0.0), np.maximum(C + Lk, 0.0))
    shaft = np.where(ring_only | feasible, 0.0, shaft_c)
    th_l = np.degrees(th[k])
    u = a - Lk[:, None] * v[k]                                  # ring force direction: N u_N = M/R - L v_L
    th_n = np.degrees(np.arctan2(-u[:, 0], u[:, 1]))
    return Lk, Nk, shaft, th_l, th_n


def joint_loads(m, d, peaks):
    """Peak loads each leg joint transmits (the parent link on the child): torque about the axis (what the servo drives),
    bending moment about the other two axes at the servo's horn face (what a single-sided joint's output shaft carries)
    and at the servo's centre (what a U-bracket's two arms carry as a force couple), axial and radial force."""
    import mujoco
    global _SP
    _SP = _SP or _servo_points()
    mujoco.mj_rnePostConstraint(m, d)
    c = d.subtree_com[0]
    for n in LOAD_JOINTS:
        j = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
        b = m.jnt_bodyid[j]
        a, p = d.xaxis[j], d.xanchor[j]
        tau_c, f = d.cfrc_int[b][:3], d.cfrc_int[b][3:]
        t_ax, f_ax = float((tau_c + np.cross(c - p, f)) @ a), float(f @ a)
        horn, centre = _SP[n[2:]]
        sg = -1.0 if (n[0] == "r" and n[2:] in ("hip_pitch", "knee", "ankle_pitch")) else 1.0

        def bend(off):
            q = p + a * sg * off
            tq = tau_c + np.cross(c - q, f)
            return float(np.linalg.norm(tq - (tq @ a) * a))
        vals = {"torque_nm": abs(t_ax), "bending_horn_nm": bend(horn), "bending_centre_nm": bend(centre),
                "axial_n": abs(f_ax), "radial_n": float(np.linalg.norm(f - f_ax * a))}
        if n.endswith("hip_yaw"):
            # the thrust ring alone (v0.4 before the keeper): it takes the bending only while the leg presses the disc
            # up into it; with the keeper, the ring and the keeper's lip hold the disc from both sides
            vals["yaw_shaft_ring_only_nm"] = max(0.0, vals["bending_horn_nm"] - max(0.0, -f_ax) * YAW_RING_R)
            Rp = d.xmat[m.body_parentid[b]].reshape(3, 3)
            q = p + a * horn
            Mp, fp = Rp.T @ (tau_c + np.cross(c - q, f)), Rp.T @ f
            L, N, shaft, _, _ = keeper_split(Mp[None, :2], np.array([-fp[2]]), keeper_arc(n[0]))
            vals.update({"yaw_shaft_residual_nm": float(shaft[0]), "yaw_keeper_lip_n": float(L[0]),
                         "yaw_ring_n": float(N[0])})
        pk = peaks.setdefault(n, {k: 0.0 for k in vals})
        for k, v in vals.items():
            pk[k] = max(pk[k], v)


class PerturbedWorld:
    """The robot program's I/O (send / tick / sleep / attitude / read_pose) on a randomly wrong physical robot: the
    same perturbations as trial(), but driven by jx0bot.robot.Robot itself, so whole missions can be tested."""

    def __init__(self, sc, seed):
        import mujoco
        import walk_jx0 as W
        from jx1calc.design import Design
        self.mj, self.W, self.sc, self.rng = mujoco, W, sc, np.random.default_rng(seed)
        design = Design(W.DESIGN)
        m = mujoco.MjModel.from_xml_string(W.build(design))
        oid = lambda kind, n: mujoco.mj_name2id(m, kind, n)  # noqa: E731
        torso = oid(mujoco.mjtObj.mjOBJ_BODY, "torso")
        m.body_mass[torso] *= sc["mass"]
        m.body_ipos[torso][:2] += np.array(sc["com_mm"]) * 1e-3
        for gname in ("l_foot_geom", "r_foot_geom", "floor"):
            m.geom_friction[oid(mujoco.mjtObj.mjOBJ_GEOM, gname)][0] = sc["mu"]
        ax, ay = (math.radians(v) for v in sc["slope_deg"])
        m.opt.gravity[:] = 9.81 * np.array([math.sin(ay) * math.cos(ax), -math.sin(ax), -math.cos(ax) * math.cos(ay)])
        self.m, self.d = m, mujoco.MjData(m)
        st = design.act_classes["ST"]
        self.servo = W.ServoModel(st["stall_torque_nm"] * sc["stall"], st["no_load_speed_rad_s"] * sc["stall"], 60.0 * sc["kp"], 0.6 * sc["kd"])
        from jx0bot.robot import ARM_JOINTS, LEG_JOINTS
        self.names = LEG_JOINTS + ARM_JOINTS
        self.adr = {n: (m.jnt_qposadr[oid(mujoco.mjtObj.mjOBJ_JOINT, n)], m.jnt_dofadr[oid(mujoco.mjtObj.mjOBJ_JOINT, n)]) for n in self.names}
        self.act = {n: oid(mujoco.mjtObj.mjOBJ_ACTUATOR, n) for n in self.names}
        self.goal = {n: 0.0 for n in self.names}
        self.lag = int(round(sc["latency"] * 0.02 / (1.0 / W.BUS_HZ)))
        self.pipe = deque(maxlen=self.lag + 1)
        self.bl = math.radians(sc["backlash_deg"]) / 2
        self.bias = [math.radians(v) for v in sc["bias_deg"]]
        self.fell, self.max_tilt = False, 0.0

    def settle(self, q0):
        mj, d = self.mj, self.d
        for n, v in q0.items():
            d.qpos[self.adr[n][0]] = v
            self.goal[n] = v
        mj.mj_forward(self.m, d)
        sole = min(d.site_xpos[mj.mj_name2id(self.m, mj.mjtObj.mjOBJ_SITE, s)][2] for s in ("l_sole", "r_sole"))
        d.qpos[2] -= sole - 0.001
        mj.mj_forward(self.m, d)
        self.pipe.extend([dict(self.goal)] * (self.lag + 1))

    def send(self, q):
        self.pipe.append({**self.goal, **q})
        self.goal_now = self.pipe[0]

    def read_pose(self):
        return {n: float(self.d.qpos[qa]) for n, (qa, _) in self.adr.items()}

    def attitude(self):
        r, p, y = self.W.rpy(self.d.qpos[3:7])
        n = math.radians(self.sc["imu_deg"])
        g = self.sc["gyro"]
        return (r + self.bias[0] + self.rng.normal(0, n), p + self.bias[1] + self.rng.normal(0, n), y,
                (self.d.qvel[3] + self.rng.normal(0, g), self.d.qvel[4] + self.rng.normal(0, g), self.d.qvel[5]))

    def tick(self, dt):
        self.advance(dt)

    def sleep(self, seconds):
        self.advance(seconds)

    def advance(self, seconds):
        goal = getattr(self, "goal_now", self.goal)
        for _ in range(int(round(seconds / self.m.opt.timestep))):
            for n in self.names:
                qa, da = self.adr[n]
                err = goal[n] - self.d.qpos[qa]
                err = 0.0 if abs(err) < self.bl else err - math.copysign(self.bl, err)
                self.d.ctrl[self.act[n]] = self.servo.torque(self.d.qpos[qa] + err, self.d.qpos[qa], self.d.qvel[da])
            self.mj.mj_step(self.m, self.d)
            r, p, _ = self.W.rpy(self.d.qpos[3:7])
            self.max_tilt = max(self.max_tilt, math.degrees(max(abs(r), abs(p))))
            if self.d.qpos[2] < 0.13 or self.max_tilt > 30:
                self.fell = True
                raise RuntimeError("fell")


MISSION = [("walk", {"steps": 8, "direction": "forward"}), ("turn", {"degrees": 40}), ("walk", {"steps": 4, "direction": "forward"}),
           ("walk", {"steps": 2, "direction": "left"}), ("walk", {"steps": 2, "direction": "backward"}),
           ("wave", {"arm": "right"}), ("nod", {"kind": "yes"}), ("look", {"direction": "left"})]


def mission(spec):
    """The robot program (jx0bot.robot.Robot) runs MISSION on a perturbed robot. Pass = it never falls."""
    from jx0bot.robot import REST_ARMS, Robot, load_config
    world = PerturbedWorld(spec["scenario"], spec.get("seed", 0))
    robot = Robot(world, load_config())
    world.settle({**robot.stand_pose, **REST_ARMS})
    done = []
    try:
        robot.stand(1.0)
        for name, args in MISSION:
            robot.act(name, args)
            done.append(name)
    except RuntimeError:
        pass
    return {"pass": not world.fell and len(done) == len(MISSION), "completed": done, "max_tilt_deg": round(world.max_tilt, 1),
            "distance_m": round(float(np.hypot(*world.d.qpos[:2])), 2), "latency_ms": spec["scenario"]["latency"] * 20}


def model_error_specs(n, seed, gains=None, latencies=(0, 1, 2)):
    rng = np.random.default_rng(seed)
    return [{"gait": MC_GAITS[k % len(MC_GAITS)], "scenario": sample(rng, latencies), "gains": gains, "seed": seed * 1000 + k}
            for k in range(n)]


def push_specs(forces, gains=None, timings=24):
    ts = np.linspace(3.0, 4.8, timings)
    return [{"gait": "forward", "scenario": nominal(), "gains": gains, "push": (float(t), d * f, 0.12)}
            for f in forces for d in (1, -1) for t in ts]


def run_all(specs, pool):
    return pool.map(trial, specs, chunksize=1)


def summarise(results, key=None):
    n = len(results)
    ok = sum(r["pass"] for r in results)
    up = sum(not r.get("fell", not r["pass"]) for r in results)
    return {"trials": n, "passed": ok, "rate": round(ok / max(1, n), 3), "stayed_up": up, "stayed_up_rate": round(up / max(1, n), 3)}


def evaluate(gains, pool, n_mc=140, forces=(2.0, 4.0, 6.0, 8.0, 10.0, 12.0)):
    """Held-out scenarios (seed 7 / 8, not used for tuning). Latency 0-20 ms is the realistic set (the robot's loop:
    IMU filter ~5 ms + bus 1.3 ms + compute < 1 ms); 40 ms is a stress test."""
    out = {"gains": gains}
    for label, seed, lats in (("model_errors_latency_0_20ms", 7, (0, 1)), ("model_errors_latency_40ms_stress", 8, (2,))):
        mc = run_all(model_error_specs(n_mc, seed, gains, lats), pool)
        out[label] = {**summarise(mc), "per_gait": {g: summarise([r for r in mc if r["gait"] == g]) for g in MC_GAITS},
                      "failures": [r for r in mc if not r["pass"]][:8]}
    pu = run_all(push_specs(forces, gains), pool)
    out["pushes_mid_walk"] = {f"{f * 0.12:.2f} N.s": summarise([r for r in pu if abs(abs(r["push"][1]) - f) < 1e-9]) for f in forces}
    return out


def tune(pool, n_cand=48, seed=11):
    """Random search around the current gains; score = pushes survived (0.72 N.s) + model-error trials passed."""
    rng = np.random.default_rng(seed)
    from jx0bot.balance import GAINS
    cands = [dict(GAINS)]
    for _ in range(n_cand):
        cands.append({**GAINS, "ka": rng.uniform(0.3, 1.0), "da": rng.uniform(0.0, 0.15), "kh": rng.uniform(0.0, 0.6),
                      "sr": rng.uniform(-1.5, 1.5), "srd": rng.uniform(-0.3, 0.3),
                      "sp": rng.uniform(-1.0, 1.0), "spd": rng.uniform(-0.2, 0.2), "decay_s": rng.uniform(0.2, 0.8)})
    specs, owner = [], []
    for ci, gns in enumerate(cands):
        for s in push_specs((6.0,), gns, timings=12) + model_error_specs(14, 3, gns):
            specs.append(s)
            owner.append(ci)
    res = run_all(specs, pool)
    score = np.zeros(len(cands))
    for ci, r in zip(owner, res):
        score[ci] += r["pass"]
    order = np.argsort(-score)
    board = [{"rank": int(k + 1), "score": int(score[ci]), "of": len(specs) // len(cands), "gains": cands[ci]} for k, ci in enumerate(order[:5])]
    return cands[order[0]], board


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "jx0" / "software"))
    out = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    with Pool(os.cpu_count()) as pool:
        if mode == "baseline":
            out["baseline"] = evaluate(None, pool)
            print(json.dumps({k: v for k, v in out["baseline"].items() if k != "gains"}, indent=1)[:3000])
        elif mode == "tune":
            best, board = tune(pool)
            out["tuning"] = {"method": "random search, 49 candidates x (24 pushes at 0.72 N.s + 14 model-error walks)", "top": board}
            print("leaderboard:", json.dumps(board, indent=1)[:2500])
            out["tuned"] = evaluate(best, pool)
            print(json.dumps({k: v for k, v in out["tuned"].items() if k != "gains"}, indent=1)[:3000])
        elif mode == "mission":                # the whole robot program, realistic latency, held-out scenarios
            rng = np.random.default_rng(99)
            specs = [{"scenario": sample(rng, (0, 1)), "seed": k} for k in range(24)]
            res = pool.map(mission, specs, chunksize=1)
            out["mission"] = {"steps": [f"{n} {a}" for n, a in MISSION], **summarise(res), "results": res}
            print(json.dumps({k: v for k, v in out["mission"].items() if k != "results"}))
            for r in res:
                if not r["pass"]:
                    print("  failed after", r["completed"], "tilt", r["max_tilt_deg"], "latency", r["latency_ms"], "ms")
        elif mode == "final":                  # the gains now in balance.py, gaits and rate as in walk_jx0.py
            out = {"final": evaluate(None, pool), **({"mission": out["mission"]} if "mission" in out else {})}
            for k, v in out["final"].items():
                if k != "gains":
                    print(k, json.dumps({kk: vv for kk, vv in v.items() if kk != "failures"}) if isinstance(v, dict) else v)
    out["generated_by"] = "jx0/verify/robustness.py"
    out["seconds_" + mode] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"{mode}: {time.time() - t0:.0f} s -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
