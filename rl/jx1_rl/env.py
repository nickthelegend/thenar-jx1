"""Batched MuJoCo environment for JX1 velocity-tracking locomotion.

N environments are advanced together with mujoco.rollout (C++ thread pool, no Python per-env loop): each policy step
runs `decimation` physics steps with the position targets held (the MJCF position actuators are the joint PD loops).
Observations, rewards and resets are vectorised numpy. Per-env physics variants give domain randomisation; pushes are
velocity kicks on the base; commands are resampled per env.
Conventions (observation layout, scales, gait clock, joint order, action scale, ankle polygon) come from
rl/config/*.yaml via jx1_rl.config and jx1_rl.policy_io — the same code paths are used by export, sim-to-sim and ROS 2.
"""
from __future__ import annotations

import os

import mujoco
import numpy as np
from mujoco import rollout

from . import assets, policy_io
from .config import TaskConfig, joint_type

STATE_SPEC = mujoco.mjtState.mjSTATE_FULLPHYSICS


class JX1Env:
    def __init__(self, cfg: TaskConfig, num_envs: int, nthread: int | None = None, seed: int = 0, randomize: bool = True):
        self.cfg, self.N = cfg, num_envs
        self.rng = np.random.default_rng(seed)
        self.model, self.info = assets.build(cfg)
        m = self.model
        k = cfg["randomization"]["model_variants"] if randomize else 1
        self.variants = assets.make_variants(m, cfg, k, self.rng) if randomize else [m]
        self.env_variant = self.rng.integers(len(self.variants), size=num_envs)
        self.model_list = [self.variants[i] for i in self.env_variant]
        self.nthread = nthread or max(1, (os.cpu_count() or 2) - 1)
        self.datas = [mujoco.MjData(m) for _ in range(self.nthread)]
        self.pool = rollout.Rollout(nthread=self.nthread)
        self.randomize = randomize

        self.dt = cfg.policy_dt
        self.decimation = cfg["model"]["decimation"]
        self.max_episode_steps = int(round(cfg["episode_s"] / self.dt))
        self.nq, self.nv, self.nu = m.nq, m.nv, m.nu
        self.nstate = mujoco.mj_stateSize(m, STATE_SPEC)

        # joint / actuator bookkeeping
        self.joints = cfg.policy_joints
        jid = [mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, j) for j in self.joints]
        if min(jid) < 0:
            raise ValueError("policy joint missing from the model")
        self.qadr = np.array([m.jnt_qposadr[i] for i in jid])
        self.dadr = np.array([m.jnt_dofadr[i] for i in jid])
        act_of_joint = {int(m.actuator_trnid[a, 0]): a for a in range(m.nu)}
        self.act = np.array([act_of_joint[i] for i in jid])
        self.default = cfg.default_vector()
        self.lower = np.array([cfg.limits[j][0] for j in self.joints])
        self.upper = np.array([cfg.limits[j][1] for j in self.joints])
        mid, half = (self.lower + self.upper) / 2, (self.upper - self.lower) / 2
        self.soft_lower, self.soft_upper = mid - 0.9 * half, mid + 0.9 * half
        self.hip_idx = np.array([i for i, j in enumerate(self.joints) if joint_type(j) in ("hip_roll", "hip_yaw")])
        self.tau_limit = np.array([m.actuator_forcerange[a, 1] for a in self.act])     # actuator-class peak torque
        self.soft_torque = cfg["rewards"].get("soft_torque_limit", 0.85)
        # joint speed limits from the joint map when it states them (JX0's servos: no-load speed); dof_vel_limits
        # penalises speed above soft_dof_vel x that (weight 0 / absent for JX1)
        vmax = {j["name"]: j.get("velocity_rad_s") for j in cfg.joint_map["joints"]}
        self.vel_limit = np.array([vmax.get(j) or np.inf for j in self.joints])
        self.soft_vel = cfg["rewards"].get("soft_dof_vel", 0.9)
        self.action_scale = cfg["action_scale"]
        self.ctrl_hold = m.key("home").ctrl.copy()           # non-policy joints hold the default pose

        def sadr(name):
            sid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SENSOR, name)
            return slice(m.sensor_adr[sid], m.sensor_adr[sid] + m.sensor_dim[sid])
        self.s_force = [sadr(f"{s}_foot_force") for s in ("left", "right")]
        self.s_fpos = [sadr(f"{s}_foot_pos") for s in ("left", "right")]
        self.s_fvel = [sadr(f"{s}_foot_vel") for s in ("left", "right")]
        self.s_tau = [sadr(f"{mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, a)}_torque") for a in self.act]

        # state template (home keyframe)
        d = mujoco.MjData(m)
        mujoco.mj_resetDataKeyframe(m, d, m.key("home").id)
        self.home_state = np.zeros(self.nstate)
        mujoco.mj_getState(m, d, self.home_state, STATE_SPEC)
        self.base_height_target = self.info["base_height"]
        self.terrain = self.info.get("terrain")               # None on flat ground

        # buffers
        N, n = num_envs, len(self.joints)
        self.state = np.tile(self.home_state, (N, 1))
        self._state_out = np.zeros((N, self.decimation, self.nstate))
        self._sens_out = np.zeros((N, self.decimation, m.nsensordata))
        self._ws0 = np.zeros((N, m.nv))
        self.ctrl = np.tile(self.ctrl_hold, (N, 1))
        self.prev_ctrl = self.ctrl.copy()
        rr = cfg["randomization"]
        self.act_delay_range = rr.get("action_delay_substeps", [0, 0]) if randomize else [0, 0]
        self.obs_delay_range = rr.get("obs_delay_substeps", [0, 0]) if randomize else [0, 0]
        if max(self.act_delay_range[1], self.obs_delay_range[1]) >= self.decimation:
            raise ValueError(f"latency randomisation is limited to decimation - 1 = {self.decimation - 1} substeps")
        self.hub_interp = bool(cfg["model"].get("hub_interpolation", False))
        self.act_delay = np.zeros(N, dtype=np.int64)          # physics substeps before new targets reach the motors
        self.obs_delay = np.zeros(N, dtype=np.int64)          # substeps by which the actor's sensor data is old
        self.obs_src = self.state.copy()                      # (possibly delayed) state the actor observation is built from
        self.actions = np.zeros((N, n))
        self.last_actions = np.zeros((N, n))
        self.last_dq = np.zeros((N, n))
        self.commands = np.zeros((N, 3))
        self.episode_step = np.zeros(N, dtype=np.int64)
        self.global_step = 0
        self.episode_sums = {}
        self.completed = {"episodes": 0}
        self.unstable_resets = 0
        self.obs_scales = cfg["observation"]["scales"]
        self.rw = {k: v for k, v in cfg["rewards"].items() if k not in ("tracking_sigma", "tracking_sigma_ang", "tracking_lin_scale", "soft_torque_limit", "soft_dof_vel")}
        self.sigma = cfg["rewards"]["tracking_sigma"]
        self.sigma_ang = cfg["rewards"].get("tracking_sigma_ang", self.sigma)     # yaw-rate tolerance (JX1: the same)
        g = cfg["gait"]
        self.period, self.offset, self.stance, self.swing_h = g["period_s"], g["offset"], g["stance_fraction"], g["swing_height_m"]
        self.stand_thr = g.get("stand_command_threshold")
        # stand-mode contact reward: "both_down" (walk_v5/v6: both feet down, which penalises recovery steps) or "none"
        self.stand_contact = g.get("stand_contact_reward", "both_down")
        # actor observation history (observation.history_length frames, Isaac Lab's layout): raw noisy frames
        # [ang_vel, gravity, q - q0, dq, action] and their noise-free twins for the critic; a reset fills all H frames
        self.H = cfg.history
        nf = 6 + 3 * n
        self.hist, self.hist_clean = np.zeros((N, self.H, nf)), np.zeros((N, self.H, nf))
        self._fresh = np.ones(N, dtype=bool)
        self._advance = False
        self.upper_idx = np.array([i for i, j in enumerate(self.joints)
                                   if joint_type(j) in ("shoulder_pitch", "shoulder_roll", "shoulder_yaw", "elbow", "neck_yaw", "neck_pitch")],
                                  dtype=np.int64)
        self.track_scale = np.asarray(cfg["rewards"].get("tracking_lin_scale", [1.0, 1.0]), dtype=np.float64)
        # reference stepping (rewards.ref_joint_pos, gait.ref_amplitude_rad; humanoid-gym): while walking, each leg in
        # swing bends hip pitch -A, knee +2A, ankle pitch -A (foot kept parallel) along sin(pi * swing progress)
        self.ref_amp = float(cfg["gait"].get("ref_amplitude_rad", 0.0))
        self.ref_cols = {}
        for side, li in (("left", 0), ("right", 1)):
            for jt, k in (("hip_pitch", -1.0), ("knee", 2.0), ("ankle_pitch", -1.0)):
                j = f"{side}_{jt}_joint"
                if j in self.joints:
                    self.ref_cols.setdefault(li, []).append((self.joints.index(j), k))
        self.leg_idx = np.array([i for i, j in enumerate(self.joints) if j.startswith(("left_", "right_"))
                                 and joint_type(j) in ("hip_yaw", "hip_roll", "hip_pitch", "knee", "ankle_pitch", "ankle_roll")])
        self._sense(self._sens_out)                           # placeholders
        self.reset_envs(np.arange(N))

    # ------------------------------------------------------------------ state access
    def qpos(self):
        return self.state[:, 1:1 + self.nq]

    def qvel(self):
        return self.state[:, 1 + self.nq:1 + self.nq + self.nv]

    def _sense(self, sens):
        last = sens[:, -1, :]
        self.foot_force = np.stack([sens[:, :, s].max(axis=(1, 2)) for s in self.s_force], axis=1)
        self.foot_pos = np.stack([last[:, s] for s in self.s_fpos], axis=1)
        self.foot_vel = np.stack([last[:, s] for s in self.s_fvel], axis=1)
        self.tau = np.concatenate([last[:, s] for s in self.s_tau], axis=1)

    # ------------------------------------------------------------------ commands / resets
    def resample_commands(self, ids):
        if len(ids) == 0:
            return
        r = self.cfg["commands"]["ranges"]
        c = np.stack([self.rng.uniform(*r["lin_vel_x"], size=len(ids)), self.rng.uniform(*r["lin_vel_y"], size=len(ids)),
                      self.rng.uniform(*r["ang_vel_yaw"], size=len(ids))], axis=1)
        # walking commands below commands.min_lin_vel are zeroed (JX1: 0.1 m/s; a 0.33 m robot walks slower than that)
        c[np.linalg.norm(c[:, :2], axis=1) < self.cfg["commands"].get("min_lin_vel", 0.1), :2] = 0.0
        c[self.rng.random(len(ids)) < self.cfg["commands"]["zero_fraction"]] = 0.0
        self.commands[ids] = c

    def reset_envs(self, ids):
        if len(ids) == 0:
            return
        r = self.cfg["randomization"]
        s = np.tile(self.home_state, (len(ids), 1))
        qp = s[:, 1:1 + self.nq]
        qv = s[:, 1 + self.nq:1 + self.nq + self.nv]
        noise = r["init_joint_noise"] if self.randomize else 0.0
        qp[:, self.qadr] = np.clip(self.default + self.rng.uniform(-noise, noise, (len(ids), len(self.joints))), self.lower, self.upper)
        if self.terrain is not None:                          # random spawn on the map, standing on the local ground
            half = self.terrain.size / 2 - 1.5
            xy = self.rng.uniform(-half, half, (len(ids), 2))
            qp[:, 0:2] = xy
            qp[:, 2] += self.terrain.height(xy[:, 0], xy[:, 1])
        yaw = self.rng.uniform(-np.pi, np.pi, len(ids)) if self.randomize else np.zeros(len(ids))
        qp[:, 3:7] = np.stack([np.cos(yaw / 2), np.zeros_like(yaw), np.zeros_like(yaw), np.sin(yaw / 2)], axis=1)
        if self.randomize:
            qv[:, :6] = self.rng.uniform(-r["init_base_vel"], r["init_base_vel"], (len(ids), 6))
        s[:, 0] = 0.0
        self.state[ids] = s
        if self.randomize and len(self.variants) > 1:
            self.env_variant[ids] = self.rng.integers(len(self.variants), size=len(ids))
            for i in ids:
                self.model_list[i] = self.variants[self.env_variant[i]]
        self.actions[ids] = 0.0
        self.last_actions[ids] = 0.0
        self.last_dq[ids] = 0.0
        self.episode_step[ids] = 0
        self.act_delay[ids] = self.rng.integers(self.act_delay_range[0], self.act_delay_range[1] + 1, size=len(ids))
        self.obs_delay[ids] = self.rng.integers(self.obs_delay_range[0], self.obs_delay_range[1] + 1, size=len(ids))
        self.prev_ctrl[ids] = self.ctrl_hold
        self.obs_src[ids] = s
        self._fresh[ids] = True
        self.resample_commands(ids)

    # ------------------------------------------------------------------ observations
    def _base(self, rows=None):
        st = self.state if rows is None else rows
        qp, qv = st[:, 1:1 + self.nq], st[:, 1 + self.nq:1 + self.nq + self.nv]
        quat = qp[:, 3:7]
        lin_b = policy_io.quat_rotate_inverse(quat, qv[:, 0:3])
        ang_b = qv[:, 3:6].copy()                           # free-joint angular velocity is already in the body frame
        grav_b = policy_io.projected_gravity(quat)
        return qp, qv, lin_b, ang_b, grav_b

    def ground(self, x, y):
        return np.zeros_like(x) if self.terrain is None else self.terrain.height(x, y)

    def phase(self):
        return policy_io.gait_phase(self.state[:, 0], self.period)

    def observations(self, noise=True):
        qp, qv, lin_b, ang_b, grav_b = self._base(self.obs_src)                 # what the robot's sensors report (delayed)
        q_rel = qp[:, self.qadr] - self.default
        dq = qv[:, self.dadr]
        ph = self.phase()
        mv = policy_io.gait_moving(self.commands, self.stand_thr)
        nz = self.cfg["observation"]["noise"] if (noise and self.randomize) else None

        def u(scale, shape):
            return self.rng.uniform(-scale, scale, shape) if nz else 0.0
        frame = np.concatenate([ang_b + u(nz and nz["ang_vel"], ang_b.shape), grav_b + u(nz and nz["gravity"], grav_b.shape),
                                q_rel + u(nz and nz["dof_pos"], q_rel.shape), dq + u(nz and nz["dof_vel"], dq.shape), self.actions], axis=1)
        frame_clean = np.concatenate([ang_b, grav_b, q_rel, dq, self.actions], axis=1) if nz else frame
        if self._advance:                                                   # one new frame per policy step
            self.hist[:, :-1], self.hist_clean[:, :-1] = self.hist[:, 1:].copy(), self.hist_clean[:, 1:].copy()
            self._advance = False
        self.hist[:, -1], self.hist_clean[:, -1] = frame, frame_clean      # the newest frame: this call's
        f = self._fresh
        if f.any():                                                         # after a reset: every frame = the first one
            self.hist[f] = frame[f][:, None, :]
            self.hist_clean[f] = frame_clean[f][:, None, :]
            self._fresh[:] = False
        n = len(self.joints)

        def build(h):
            return policy_io.build_observation_history(h[..., 0:3], h[..., 3:6], self.commands, h[..., 6:6 + n], h[..., 6 + n:6 + 2 * n],
                                                       h[..., 6 + 2 * n:], ph, self.obs_scales, self.cfg["observation"]["clip"], moving=mv)
        clean = build(self.hist_clean)
        obs = build(self.hist) if nz else clean
        qp, qv, lin_b, _, _ = self._base()                                   # critic: true current state
        contact = (self.foot_force > 1.0).astype(np.float64)
        h_base = qp[:, 2:3] - self.ground(qp[:, 0:1], qp[:, 1:2])
        h_feet = self.foot_pos[:, :, 2] - self.ground(self.foot_pos[:, :, 0], self.foot_pos[:, :, 1])
        priv = np.concatenate([clean, lin_b * self.obs_scales["lin_vel"], (h_base - self.base_height_target) * 5.0, contact,
                               h_feet * 10.0], axis=1)
        return obs.astype(np.float32), priv.astype(np.float32)

    def reset(self):
        self.reset_envs(np.arange(self.N))
        self._sens_out[:] = 0.0
        self._sense(self._sens_out)
        return self.observations()

    # ------------------------------------------------------------------ step
    def step(self, actions: np.ndarray):
        self.last_actions[:] = self.actions
        self.actions[:] = np.clip(actions, -100.0, 100.0)
        targets = policy_io.actions_to_targets(self.actions, self.default, self.action_scale, self.lower, self.upper)
        targets = policy_io.clip_ankle_targets(targets, self.joints, self.cfg.ankle_polygons)
        targets = policy_io.clip_hip_yaw_toe_out(targets, self.joints, self.cfg.hip_yaw_toe_out_max)
        self.ctrl[:, self.act] = targets
        if self.hub_interp:
            # the CAN hubs ramp each new host target linearly over the next host period (firmware command_for(): alpha)
            ramp = (np.arange(1, self.decimation + 1) / self.decimation)[None, :, None]
            control = self.prev_ctrl[:, None, :] + ramp * (self.ctrl - self.prev_ctrl)[:, None, :]
        else:
            control = np.repeat(self.ctrl[:, None, :], self.decimation, axis=1)
        for d in range(1, min(self.decimation, self.act_delay_range[1] + 1)):
            late = self.act_delay >= d                         # substep d-1 still runs on the previous targets
            control[late, d - 1, :] = self.prev_ctrl[late]
        self.prev_ctrl[:] = self.ctrl
        # explicit zero solver warm start: otherwise each thread's MjData carries the warm start of whichever env it ran
        # last, which depends on thread scheduling and makes rollouts non-reproducible (no measurable speed cost)
        self.pool.rollout(self.model_list, self.datas, self.state, control, nstep=self.decimation, initial_warmstart=self._ws0,
                          state=self._state_out, sensordata=self._sens_out, skip_checks=True)
        self.state[:] = self._state_out[:, -1, :]
        self.obs_src[:] = self._state_out[np.arange(self.N), self.decimation - 1 - self.obs_delay, :]
        self._sense(self._sens_out)
        self.episode_step += 1
        self.global_step += 1
        self._advance = True

        bad = ~np.all(np.isfinite(self.state), axis=1) | (np.abs(self.qvel()).max(axis=1) > 1e3)
        if bad.any():
            self.unstable_resets += int(bad.sum())
            self.state[bad] = self.home_state
            self.obs_src[bad] = self.home_state
            self._sens_out[bad] = 0.0
            self._sense(self._sens_out)

        qp, qv, lin_b, ang_b, grav_b = self._base()
        q = qp[:, self.qadr]
        dq = qv[:, self.dadr]
        tilt_limit = -np.cos(np.radians(self.cfg["termination"]["max_tilt_deg"]))
        h_base = qp[:, 2] - self.ground(qp[:, 0], qp[:, 1])
        terminated = (h_base < self.cfg["termination"]["min_base_height_m"]) | (grav_b[:, 2] > tilt_limit) | bad
        time_out = self.episode_step >= self.max_episode_steps
        if self.terrain is not None:                          # leaving the map ends the episode without penalty
            time_out |= np.max(np.abs(qp[:, 0:2]), axis=1) > self.terrain.size / 2 - 0.5

        rew, terms = self._rewards(qp, q, dq, lin_b, ang_b, grav_b, terminated & ~time_out)
        self.last_dq[:] = dq
        for k, v in terms.items():
            self.episode_sums[k] = self.episode_sums.get(k, np.zeros(self.N)) + v

        # pushes and command resampling
        r = self.cfg["randomization"]
        if self.randomize and self.global_step % max(1, int(r["push_interval_s"] / self.dt)) == 0:
            self.state[:, 1 + self.nq:1 + self.nq + 2] += self.rng.uniform(-r["push_velocity_m_s"], r["push_velocity_m_s"], (self.N, 2))
        resample = np.nonzero(self.episode_step % max(1, int(self.cfg["commands"]["resample_s"] / self.dt)) == 0)[0]
        self.resample_commands(resample)

        done = terminated | time_out
        info = {"time_outs": time_out.astype(np.float32)}
        ids = np.nonzero(done)[0]
        if len(ids):
            info["episode"] = {k: float(np.mean(v[ids]) / self.cfg["episode_s"]) for k, v in self.episode_sums.items()}
            info["episode"]["length_s"] = float(np.mean(self.episode_step[ids]) * self.dt)
            for v in self.episode_sums.values():
                v[ids] = 0.0
            self.completed["episodes"] += len(ids)
            self.reset_envs(ids)
        obs, priv = self.observations()
        return obs, priv, rew.astype(np.float32), done.astype(np.float32), info

    # ------------------------------------------------------------------ rewards
    def ref_targets(self, leg_phase, moving):
        """Reference leg angles (N, n): the default pose, plus the swing bend while walking (rewards.ref_joint_pos)."""
        ref = np.tile(self.default, (self.N, 1))
        swing = np.clip((leg_phase - self.stance) / (1.0 - self.stance), 0.0, 1.0)            # (N, 2)
        lift = np.sin(np.pi * swing) * (leg_phase >= self.stance) * moving[:, None]
        for li, cols in self.ref_cols.items():
            for c, k in cols:
                ref[:, c] += k * self.ref_amp * lift[:, li]
        return ref

    def _ref_reward(self, q, leg_phase, moving):
        if self.ref_amp == 0.0 or self.rw.get("ref_joint_pos", 0.0) == 0.0:
            return np.zeros(self.N)
        diff = np.linalg.norm((q - self.ref_targets(leg_phase, moving))[:, self.leg_idx], axis=1)
        return np.exp(-2.0 * diff) - 0.2 * np.minimum(diff, 0.5)

    def _rewards(self, qp, q, dq, lin_b, ang_b, grav_b, died):
        w, dt = self.rw, self.dt
        contact = self.foot_force > 1.0
        ph = self.phase()
        leg_phase = np.stack([ph, np.mod(ph + self.offset, 1.0)], axis=1)
        moving = policy_io.gait_moving(self.commands, self.stand_thr) > 0.5
        stance = np.where(moving[:, None], leg_phase < self.stance, True)      # stand mode: both feet down
        standing = ~moving if self.stand_thr is not None else np.linalg.norm(self.commands, axis=1) < 0.1
        dof_err = np.abs(q - self.default).sum(axis=1)
        terms = {
            # rewards.tracking_lin_scale [sx, sy] (default 1, 1): the x / y errors in those units, so a small sideways
            # command counts as much as a large forward one
            "tracking_lin_vel": np.exp(-np.sum(((self.commands[:, :2] - lin_b[:, :2]) / self.track_scale) ** 2, axis=1) / self.sigma),
            "tracking_ang_vel": np.exp(-(self.commands[:, 2] - ang_b[:, 2]) ** 2 / self.sigma_ang),
            "lin_vel_z": lin_b[:, 2] ** 2,
            "ang_vel_xy": np.sum(ang_b[:, :2] ** 2, axis=1),
            "orientation": np.sum(grav_b[:, :2] ** 2, axis=1),
            "base_height": (qp[:, 2] - self.ground(qp[:, 0], qp[:, 1]) - self.base_height_target) ** 2,
            "torques": np.sum(self.tau ** 2, axis=1),
            "torque_limits": np.sum(np.clip(np.abs(self.tau) - self.soft_torque * self.tau_limit, 0, None), axis=1),
            "dof_vel": np.sum(dq ** 2, axis=1),
            "dof_vel_limits": np.sum(np.clip(np.abs(dq) - self.soft_vel * self.vel_limit, 0, None), axis=1),
            "dof_acc": np.sum(((dq - self.last_dq) / dt) ** 2, axis=1),
            "action_rate": np.sum((self.actions - self.last_actions) ** 2, axis=1),
            "dof_pos_limits": np.sum(np.clip(self.soft_lower - q, 0, None) + np.clip(q - self.soft_upper, 0, None), axis=1)
                              + policy_io.ankle_polygon_violation(q, self.joints, self.cfg.ankle_polygons),
            "alive": np.ones(self.N),
            "hip_pos": np.sum(q[:, self.hip_idx] ** 2, axis=1),
            "upper_body_pos": np.sum((q[:, self.upper_idx] - self.default[self.upper_idx]) ** 2, axis=1),
            "ref_joint_pos": self._ref_reward(q, leg_phase, moving),
            "contact": np.sum(contact == stance, axis=1).astype(np.float64) * (moving | (self.stand_contact == "both_down")),
            "feet_swing_height": np.sum(((self.foot_pos[:, :, 2] - self.ground(self.foot_pos[:, :, 0], self.foot_pos[:, :, 1])
                                          - self.swing_h) ** 2) * ~contact, axis=1) * moving,
            "contact_no_vel": np.sum(np.sum(self.foot_vel ** 2, axis=2) * contact, axis=1),
            "stand_still": dof_err * standing,
            "termination": died.astype(np.float64),
        }
        terms = {k: v * w[k] * dt for k, v in terms.items() if w.get(k, 0.0) != 0.0}
        return sum(terms.values()), terms
