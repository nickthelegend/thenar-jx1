"""Walk JX0 with a trained policy (jx0/rl: MuJoCo or Isaac Lab) instead of the gait files - on the robot or in the
simulator, through the same Robot and I/O as every other action:

    python -m jx0bot.policy --bundle <policy folder> [--sim] [--vx 0.05] [--vy 0] [--wz 0] [--seconds 20]

The bundle is what rl/export.py or export_offline.py writes: policy.onnx, policy_io.yaml (inputs, outputs, gains,
limits, gait clock) and, for a policy that corrects the reference gait, gait_reference.json. Every 20 ms (50 Hz):
read the IMU (body rate, gravity direction) and the servo positions, build the policy's observation exactly as in
training (policy_io's layout, with history), run the network, add its corrections to the reference gait (or the
stance), and send the goals ramped over two 100 Hz bus packets. The goals go through Robot._send, so the joint limits
and the hip coupling apply, and each servo's own EEPROM limits stay in front of it all.
Needs numpy, PyYAML and onnxruntime (pip install onnxruntime; there are wheels for the Raspberry Pi's ARM64).
"""
from __future__ import annotations

import argparse
import json
import math
import time
from collections import deque
from pathlib import Path

import numpy as np
import yaml

from .robot import HERE, REST_ARMS, Robot, load_config

ROOT = HERE.parents[2]
FLIP = ("roll", "yaw")


def short(j: str) -> str:
    """left_knee_joint -> l_knee."""
    j = j[:-len("_joint")] if j.endswith("_joint") else j
    for side, s in (("left_", "l_"), ("right_", "r_")):
        if j.startswith(side):
            return s + j[len(side):]
    return j


def gravity_body(roll: float, pitch: float) -> np.ndarray:
    """Unit gravity in the body frame from the IMU's roll and pitch (yaw does not matter)."""
    return np.array([math.sin(pitch), -math.sin(roll) * math.cos(pitch), -math.cos(roll) * math.cos(pitch)])


class Reference:
    """The reference gait (jx0/rl/gait_reference.py's table), numpy, one robot."""

    def __init__(self, table: dict, joints, stand_threshold):
        cols = [table["joints"].index(j) for j in joints]
        self.stance = np.array(table["stance"])[cols]
        self.S = np.array(table["step"])[:, cols]
        self.E = {k: np.array(v["table"])[:, cols] for k, v in table["directions"].items()}
        self.v = {k: v["speed"] for k, v in table["directions"].items()}
        self.sf, self.thr = table["stance_fraction"], stand_threshold

    def __call__(self, phase: float, cmd) -> np.ndarray:
        vx, vy, wz = cmd
        P = self.S.shape[0]
        k = ((phase - self.sf) % 1.0) * P
        i0 = int(math.floor(k)) % P
        i1, a = (i0 + 1) % P, k - math.floor(k)

        def at(T):
            return T[i0] * (1 - a) + T[i1] * a
        w = {"forward": max(vx, 0) / self.v["forward"], "backward": max(-vx, 0) / self.v["backward"],
             "left": max(vy, 0) / self.v["left"], "right": max(-vy, 0) / self.v["right"],
             "turn_left": max(wz, 0) / self.v["turn_left"], "turn_right": max(-wz, 0) / self.v["turn_right"]}
        dev = at(self.S) + sum(wk * at(self.E[k]) for k, wk in w.items())
        moving = self.thr is None or math.sqrt(vx * vx + vy * vy + wz * wz) >= self.thr
        return self.stance + (dev if moving else 0.0)


class PolicyWalker:
    def __init__(self, robot: Robot, bundle: Path):
        import onnxruntime as ort
        self.robot, self.bundle = robot, Path(bundle)
        io = self.io = yaml.safe_load((self.bundle / "policy_io.yaml").read_text(encoding="utf-8"))
        self.sess = ort.InferenceSession(str(self.bundle / io["policy"]["onnx"]))
        self.pj = io["joints"]["policy"]
        self.names = [short(j) for j in self.pj]
        self.default = np.array([io["default_joint_pos"][j] for j in self.pj])
        self.lo = np.array([io["joint_limits_rad"][j][0] for j in self.pj])
        self.hi = np.array([io["joint_limits_rad"][j][1] for j in self.pj])
        ob = io["observation"]
        self.scales, self.clip, self.H = ob["scales"], ob["clip"], int(ob.get("history_length", 1))
        g = io["gait"]
        self.period, self.thr = g["period_s"], g.get("stand_command_threshold")
        self.dt = io["control"]["policy_dt_s"]
        self.polys = {s: np.asarray(p) for s, p in io.get("ankle_polygons_rad", {}).items()}
        self.ref = None
        table = self.bundle / "gait_reference.json"
        if not table.exists() and io.get("action_reference"):
            table = ROOT / io["action_reference"]
        if io.get("action_reference") or table.exists():
            self.ref = Reference(json.loads(table.read_text(encoding="utf-8")), self.pj, self.thr)

    def observation(self, frames, cmd, t):
        f = list(frames)
        flat = lambda k, s=1.0: np.concatenate([x[k] * s for x in f])  # noqa: E731
        moving = 1.0 if self.thr is None or np.linalg.norm(cmd) >= self.thr else 0.0
        ph = (t / self.period) % 1.0
        obs = np.concatenate([flat(0, self.scales["ang_vel"]), flat(1), np.asarray(cmd) * np.asarray(self.scales["commands"]),
                              flat(2, self.scales["dof_pos"]), flat(3, self.scales["dof_vel"]), flat(4),
                              [math.sin(2 * math.pi * ph) * moving, math.cos(2 * math.pi * ph) * moving]])
        return np.clip(obs, -self.clip, self.clip).astype(np.float32)

    def targets(self, action, cmd, t):
        base = self.default if self.ref is None else self.ref((t / self.period) % 1.0, cmd)
        q = np.clip(base + self.io["action_scale"] * action, self.lo, self.hi)
        for side, poly in self.polys.items():                      # serial ankle: the polygon is the limits' box
            ip, ir = self.pj.index(f"{side}_ankle_pitch_joint"), self.pj.index(f"{side}_ankle_roll_joint")
            q[ip] = np.clip(q[ip], poly[:, 0].min(), poly[:, 0].max())
            q[ir] = np.clip(q[ir], poly[:, 1].min(), poly[:, 1].max())
        return {n: float(v) for n, v in zip(self.names, q)}

    def walk(self, cmd=(0.0, 0.0, 0.0), seconds=10.0, command_at=None):
        """Walk for `seconds` (command_at(t) -> (vx, vy, wz) overrides cmd). Returns the time it ran."""
        io, robot = self.robot.io, self.robot
        frames, last = None, np.zeros(len(self.pj))
        q_prev, goal_prev = None, {n: robot.q[n] for n in self.names}
        t = 0.0
        bus = int(round(self.dt / 0.01))
        while t < seconds:
            c = np.asarray(command_at(t) if command_at else cmd, dtype=np.float64)
            pose = io.read_pose()
            q = np.array([pose[n] for n in self.names])
            dq = np.zeros_like(q) if q_prev is None else (q - q_prev) / self.dt
            q_prev = q
            roll, pitch, _, rate = io.attitude()
            frame = (np.asarray(rate, dtype=np.float64), gravity_body(roll, pitch), q - self.default, dq, last.copy())
            frames = deque([frame] * self.H, maxlen=self.H) if frames is None else (frames.append(frame) or frames)
            a = self.sess.run(["actions"], {"obs": self.observation(frames, c, t)[None]})[0][0].astype(np.float64)
            last = a
            goal = self.targets(a, c, t)
            for k in range(1, bus + 1):                            # ramp over the policy period (as in training)
                s = k / bus
                robot._send({n: goal_prev[n] + s * (goal[n] - goal_prev[n]) for n in self.names})
                io.tick(self.dt / bus)
            goal_prev = goal
            t += self.dt
        return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--sim", action="store_true", help="jx0bot's MuJoCo simulator instead of the robot")
    ap.add_argument("--no-viewer", action="store_true")
    ap.add_argument("--vx", type=float, default=0.05)
    ap.add_argument("--vy", type=float, default=0.0)
    ap.add_argument("--wz", type=float, default=0.0)
    ap.add_argument("--seconds", type=float, default=20.0)
    a = ap.parse_args()
    cfg = load_config()
    if a.sim:
        from .robot import SimIO
        io = SimIO(cfg, viewer=not a.no_viewer)
    else:
        from .robot import HardwareIO
        io = HardwareIO(cfg)
    robot = Robot(io, cfg)
    walker = PolicyWalker(robot, Path(a.bundle))
    if a.sim:
        io.settle({**{n: walker.io["default_joint_pos"][j] for n, j in zip(walker.names, walker.pj)}, **REST_ARMS})
    try:
        io.torque(True)
        robot.stand(1.5)                                           # from wherever the joints are into the stance
        x0 = getattr(io, "d", None) and io.d.qpos[:2].copy()
        t0 = time.perf_counter()
        walker.walk((a.vx, a.vy, a.wz), a.seconds)
        msg = f"walked {a.seconds:.0f} s at command ({a.vx}, {a.vy}, {a.wz}) in {time.perf_counter() - t0:.1f} s"
        if x0 is not None:
            msg += f"; moved {np.linalg.norm(io.d.qpos[:2] - x0):.2f} m"
        print(msg)
        robot.stand(1.0)
    finally:
        io.close()


if __name__ == "__main__":
    main()
