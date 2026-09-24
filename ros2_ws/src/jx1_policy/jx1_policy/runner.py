"""ROS-independent policy runner for JX1: exported ONNX policy + policy_io.yaml -> joint position targets.

Implements the conventions of rl/jx1_rl/policy_io.py (observation layout and scales, gait clock, action scaling, joint
limits, ankle pitch/roll polygon) from the exported policy_io.yaml only, so it runs on the Jetson without the training
code. rl/tests/test_policy_io.py checks that this module and the training environment produce identical observations.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import yaml


def quat_rotate_inverse(q_wxyz, v):
    w = q_wxyz[..., :1]
    u = q_wxyz[..., 1:4]
    return v * (2.0 * w * w - 1.0) - np.cross(u, v) * w * 2.0 + u * np.sum(u * v, axis=-1, keepdims=True) * 2.0


def project_to_polygon(p, poly):
    """Closest point of the convex polygon poly (k, 2) to p (2,); p itself when inside."""
    a, b = poly, np.roll(poly, -1, axis=0)
    e = b - a
    area = 0.5 * np.sum(a[:, 0] * b[:, 1] - b[:, 0] * a[:, 1])
    s = 1.0 if area >= 0 else -1.0
    d = p - a
    if np.all(s * (e[:, 0] * d[:, 1] - e[:, 1] * d[:, 0]) >= -1e-12):
        return p
    t = np.clip(np.sum(d * e, axis=1) / np.sum(e * e, axis=1), 0.0, 1.0)
    c = a + t[:, None] * e
    return c[np.argmin(np.sum((c - p) ** 2, axis=1))]


class PolicyRunner:
    def __init__(self, policy_dir: str | Path, providers=None):
        import onnxruntime as ort
        policy_dir = Path(policy_dir)
        self.io = yaml.safe_load((policy_dir / "policy_io.yaml").read_text(encoding="utf-8"))
        io = self.io
        self.session = ort.InferenceSession(str(policy_dir / io["policy"]["onnx"]), providers=providers or ["CPUExecutionProvider"])
        self.policy_joints = list(io["joints"]["policy"])
        self.held_joints = list(io["joints"]["held"])
        self.all_joints = self.policy_joints + self.held_joints
        self.default = np.array([io["default_joint_pos"][j] for j in self.policy_joints])
        self.default_all = {j: io["default_joint_pos"][j] for j in self.all_joints}
        lim = io["joint_limits_rad"]
        self.lower = np.array([lim[j][0] for j in self.policy_joints])
        self.upper = np.array([lim[j][1] for j in self.policy_joints])
        self.scales = io["observation"]["scales"]
        self.clip = io["observation"]["clip"]
        self.period = io["gait"]["period_s"]
        self.action_scale = io["action_scale"]
        self.dt = io["control"]["policy_dt_s"]
        self.ankles = []
        for side, poly in io.get("ankle_polygons_rad", {}).items():
            if f"{side}_ankle_pitch_joint" in self.policy_joints:
                self.ankles.append((self.policy_joints.index(f"{side}_ankle_pitch_joint"),
                                    self.policy_joints.index(f"{side}_ankle_roll_joint"), np.array(poly)))
        self.last_action = np.zeros(len(self.policy_joints))
        # hip-yaw toe-out coupling (left_hip_yaw - right_hip_yaw <= max): the bracket tails touch beyond it (OI-24)
        self.toe_out_max = io.get("hip_yaw_toe_out_max_rad")
        self.yaw_ids = ((self.policy_joints.index("left_hip_yaw_joint"), self.policy_joints.index("right_hip_yaw_joint"))
                        if {"left_hip_yaw_joint", "right_hip_yaw_joint"} <= set(self.policy_joints) else None)

    def reset(self):
        self.last_action[:] = 0.0

    def observation(self, quat_wxyz, ang_vel_body, q, dq, command, phase_time):
        """q, dq: policy-joint positions/velocities (policy order); command (vx, vy, wz); phase_time: s since start."""
        g = quat_rotate_inverse(np.asarray(quat_wxyz, float), np.array([0.0, 0.0, -1.0]))
        phase = np.mod(phase_time / self.period, 1.0)
        # stand mode (policy_io gait.stand_command_threshold): the clock reads 0 when the command is (nearly) zero
        thr = self.io["gait"].get("stand_command_threshold")
        mv = 1.0 if thr is None or np.linalg.norm(np.asarray(command, float)) >= thr else 0.0
        obs = np.concatenate([np.asarray(ang_vel_body, float) * self.scales["ang_vel"], g,
                              np.asarray(command, float) * np.asarray(self.scales["commands"], float),
                              (np.asarray(q, float) - self.default) * self.scales["dof_pos"], np.asarray(dq, float) * self.scales["dof_vel"],
                              self.last_action, [mv * np.sin(2 * np.pi * phase), mv * np.cos(2 * np.pi * phase)]])
        return np.clip(obs, -self.clip, self.clip)

    def step(self, quat_wxyz, ang_vel_body, q, dq, command, phase_time):
        """One policy tick -> dict joint -> position target (policy joints + held joints)."""
        obs = self.observation(quat_wxyz, ang_vel_body, q, dq, command, phase_time)
        act = self.session.run([self.io["policy"]["output"]], {self.io["policy"]["input"]: obs[None].astype(np.float32)})[0][0]
        self.last_action = act.astype(float)
        tgt = np.clip(self.default + self.action_scale * self.last_action, self.lower, self.upper)
        for ip, ir, poly in self.ankles:
            tgt[ip], tgt[ir] = project_to_polygon(np.array([tgt[ip], tgt[ir]]), poly)
        if self.toe_out_max is not None and self.yaw_ids:
            il, ir = self.yaw_ids
            excess = max(tgt[il] - tgt[ir] - self.toe_out_max, 0.0)
            tgt[il] -= 0.5 * excess
            tgt[ir] += 0.5 * excess
        out = dict(zip(self.policy_joints, tgt.tolist()))
        out.update({j: self.default_all[j] for j in self.held_joints})
        return out
