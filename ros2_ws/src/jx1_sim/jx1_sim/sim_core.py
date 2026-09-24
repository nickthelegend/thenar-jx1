"""ROS-independent MuJoCo core of the JX1 simulator node: model loading, PD gains, reset to the stand pose, stepping with
position targets, and the state a robot would report (joint positions/velocities/torques, pelvis IMU, ground-truth base).
"""
from __future__ import annotations

from pathlib import Path

import mujoco
import numpy as np
import yaml


class MujocoSim:
    def __init__(self, model_path: str | Path, policy_io_path: str | Path | None = None):
        self.m = mujoco.MjModel.from_xml_path(str(model_path))
        self.d = mujoco.MjData(self.m)
        self.io = yaml.safe_load(Path(policy_io_path).read_text(encoding="utf-8")) if policy_io_path else None
        m = self.m
        self.joints, self.act = [], {}
        for a in range(m.nu):
            j = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, m.actuator_trnid[a, 0])
            self.joints.append(j)
            self.act[j] = a
            if self.io and j in self.io["pd_gains"]:
                kp, kd = self.io["pd_gains"][j]
                m.actuator_gainprm[a, 0] = kp
                m.actuator_biasprm[a, 1] = -kp
                m.actuator_biasprm[a, 2] = -kd
        jid = [mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, j) for j in self.joints]
        self.qadr = np.array([m.jnt_qposadr[i] for i in jid])
        self.dadr = np.array([m.jnt_dofadr[i] for i in jid])
        self.aadr = np.array([self.act[j] for j in self.joints])

        def sensor(name):
            sid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SENSOR, name)
            return slice(m.sensor_adr[sid], m.sensor_adr[sid] + m.sensor_dim[sid]) if sid >= 0 else None
        self.s_gyro, self.s_acc = sensor("imu_gyro"), sensor("imu_acc")
        self.soles = [mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, f"{s}_sole") for s in ("left", "right")]
        self.reset()

    @property
    def dt(self):
        return self.m.opt.timestep

    def default_pose(self):
        return {j: (self.io["default_joint_pos"].get(j, 0.0) if self.io else 0.0) for j in self.joints}

    def reset(self, base_xy=(0.0, 0.0)):
        m, d = self.m, self.d
        mujoco.mj_resetData(m, d)
        pose = self.default_pose()
        for j, a in self.act.items():
            d.qpos[self.qadr[self.joints.index(j)]] = pose[j]
            d.ctrl[a] = pose[j]
        d.qpos[0:2] = base_xy
        d.qpos[2] = 1.0
        mujoco.mj_kinematics(m, d)
        d.qpos[2] = 1.0 - min(d.site_xpos[s][2] for s in self.soles) + 0.002
        mujoco.mj_forward(m, d)

    def set_targets(self, targets: dict):
        for j, v in targets.items():
            a = self.act.get(j)
            if a is not None:
                self.d.ctrl[a] = v

    def step(self, n=1):
        for _ in range(n):
            mujoco.mj_step(self.m, self.d)

    def joint_state(self):
        d = self.d
        return self.joints, d.qpos[self.qadr].copy(), d.qvel[self.dadr].copy(), d.actuator_force[self.aadr].copy()

    def imu(self):
        """Pelvis IMU: orientation (w, x, y, z), angular velocity and linear acceleration in the IMU frame."""
        d = self.d
        gyro = d.sensordata[self.s_gyro].copy() if self.s_gyro else d.qvel[3:6].copy()
        acc = d.sensordata[self.s_acc].copy() if self.s_acc else np.array([0.0, 0.0, 9.81])
        return d.qpos[3:7].copy(), gyro, acc

    def base(self):
        """Ground truth: position, orientation (w, x, y, z), linear velocity (world), angular velocity (body)."""
        d = self.d
        return d.qpos[0:3].copy(), d.qpos[3:7].copy(), d.qvel[0:3].copy(), d.qvel[3:6].copy()
