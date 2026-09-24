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

        # buffers
        N, n = num_envs, len(self.joints)
        self.state = np.tile(self.home_state, (N, 1))
        self._state_out = np.zeros((N, self.decimation, self.nstate))
        self._sens_out = np.zeros((N, self.decimation, m.nsensordata))
        self.ctrl = np.tile(self.ctrl_hold, (N, 1))
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
        self.rw = {k: v for k, v in cfg["rewards"].items() if k != "tracking_sigma"}
        self.sigma = cfg["rewards"]["tracking_sigma"]
        g = cfg["gait"]
        self.period, self.offset, self.stance, self.swing_h = g["period_s"], g["offset"], g["stance_fraction"], g["swing_height_m"]
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
        c[np.linalg.norm(c[:, :2], axis=1) < 0.1, :2] = 0.0
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
        self.resample_commands(ids)

    # ------------------------------------------------------------------ observations
    def _base(self):
        qp, qv = self.qpos(), self.qvel()
        quat = qp[:, 3:7]
        lin_b = policy_io.quat_rotate_inverse(quat, qv[:, 0:3])
        ang_b = qv[:, 3:6].copy()                           # free-joint angular velocity is already in the body frame
        grav_b = policy_io.projected_gravity(quat)
        return qp, qv, lin_b, ang_b, grav_b

    def phase(self):
        return policy_io.gait_phase(self.state[:, 0], self.period)

    def observations(self, noise=True):
        qp, qv, lin_b, ang_b, grav_b = self._base()
        q_rel = qp[:, self.qadr] - self.default
        dq = qv[:, self.dadr]
        ph = self.phase()
        nz = self.cfg["observation"]["noise"] if (noise and self.randomize) else None

        def u(scale, shape):
            return self.rng.uniform(-scale, scale, shape) if nz else 0.0
        obs = policy_io.build_observation(ang_b + u(nz and nz["ang_vel"], ang_b.shape), grav_b + u(nz and nz["gravity"], grav_b.shape),
                                          self.commands, q_rel + u(nz and nz["dof_pos"], q_rel.shape), dq + u(nz and nz["dof_vel"], dq.shape),
                                          self.actions, ph, self.obs_scales, self.cfg["observation"]["clip"])
        clean = policy_io.build_observation(ang_b, grav_b, self.commands, q_rel, dq, self.actions, ph, self.obs_scales,
                                            self.cfg["observation"]["clip"]) if nz else obs
        contact = (self.foot_force > 1.0).astype(np.float64)
        priv = np.concatenate([clean, lin_b * self.obs_scales["lin_vel"], (qp[:, 2:3] - self.base_height_target) * 5.0, contact,
                               self.foot_pos[:, :, 2] * 10.0], axis=1)
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
        self.ctrl[:, self.act] = targets
        control = np.repeat(self.ctrl[:, None, :], self.decimation, axis=1)
        self.pool.rollout(self.model_list, self.datas, self.state, control, nstep=self.decimation,
                          state=self._state_out, sensordata=self._sens_out, skip_checks=True)
        self.state[:] = self._state_out[:, -1, :]
        self._sense(self._sens_out)
        self.episode_step += 1
        self.global_step += 1

        bad = ~np.all(np.isfinite(self.state), axis=1) | (np.abs(self.qvel()).max(axis=1) > 1e3)
        if bad.any():
            self.unstable_resets += int(bad.sum())
            self.state[bad] = self.home_state
            self._sens_out[bad] = 0.0
            self._sense(self._sens_out)

        qp, qv, lin_b, ang_b, grav_b = self._base()
        q = qp[:, self.qadr]
        dq = qv[:, self.dadr]
        tilt_limit = -np.cos(np.radians(self.cfg["termination"]["max_tilt_deg"]))
        terminated = (qp[:, 2] < self.cfg["termination"]["min_base_height_m"]) | (grav_b[:, 2] > tilt_limit) | bad
        time_out = self.episode_step >= self.max_episode_steps

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
    def _rewards(self, qp, q, dq, lin_b, ang_b, grav_b, died):
        w, dt = self.rw, self.dt
        contact = self.foot_force > 1.0
        ph = self.phase()
        leg_phase = np.stack([ph, np.mod(ph + self.offset, 1.0)], axis=1)
        stance = leg_phase < self.stance
        standing = np.linalg.norm(self.commands, axis=1) < 0.1
        dof_err = np.abs(q - self.default).sum(axis=1)
        terms = {
            "tracking_lin_vel": np.exp(-np.sum((self.commands[:, :2] - lin_b[:, :2]) ** 2, axis=1) / self.sigma),
            "tracking_ang_vel": np.exp(-(self.commands[:, 2] - ang_b[:, 2]) ** 2 / self.sigma),
            "lin_vel_z": lin_b[:, 2] ** 2,
            "ang_vel_xy": np.sum(ang_b[:, :2] ** 2, axis=1),
            "orientation": np.sum(grav_b[:, :2] ** 2, axis=1),
            "base_height": (qp[:, 2] - self.base_height_target) ** 2,
            "torques": np.sum(self.tau ** 2, axis=1),
            "dof_vel": np.sum(dq ** 2, axis=1),
            "dof_acc": np.sum(((dq - self.last_dq) / dt) ** 2, axis=1),
            "action_rate": np.sum((self.actions - self.last_actions) ** 2, axis=1),
            "dof_pos_limits": np.sum(np.clip(self.soft_lower - q, 0, None) + np.clip(q - self.soft_upper, 0, None), axis=1)
                              + policy_io.ankle_polygon_violation(q, self.joints, self.cfg.ankle_polygons),
            "alive": np.ones(self.N),
            "hip_pos": np.sum(q[:, self.hip_idx] ** 2, axis=1),
            "contact": np.sum(contact == stance, axis=1).astype(np.float64),
            "feet_swing_height": np.sum(((self.foot_pos[:, :, 2] - self.swing_h) ** 2) * ~contact, axis=1),
            "contact_no_vel": np.sum(np.sum(self.foot_vel ** 2, axis=2) * contact, axis=1),
            "stand_still": dof_err * standing,
            "termination": died.astype(np.float64),
        }
        terms = {k: v * w[k] * dt for k, v in terms.items() if w.get(k, 0.0) != 0.0}
        return sum(terms.values()), terms
