"""JX0 body: joint I/O (real hardware or the MuJoCo model), verified gait playback with IMU balance, and the actions
the brain can call (wave, nod, look, walk, turn).

Every joint is a Feetech STS3215 12 V serial bus servo (12 legs, 2 per arm, the neck), all on one bus, so both back
ends take the same joint targets (radians, the simulation's sign convention):
- HardwareIO: the 17 servos through the serial bus servo driver (servo_bus.py), MPU6050 IMU.
- SimIO: the JX0 MuJoCo model (jx0/sim/jx0_model.py) with the same servo model the gaits were verified with; runs on a
  PC (python -m jx0bot.main --sim) so the whole robot, voice included, can be tried before it is built.
Gaits (gaits/*.json) are 50 Hz trajectories (legs plus the arm swing) exported by jx0/sim/walk_jx0.py after passing
the closed-loop test.
"""
from __future__ import annotations

import json
import math
import threading
import time
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
LEG = ["hip_yaw", "hip_roll", "hip_pitch", "knee", "ankle_pitch", "ankle_roll"]
LEG_JOINTS = [f"{s}_{j}" for s in "lr" for j in LEG]
ARM_JOINTS = [f"{s}_{j}" for s in "lr" for j in ("shoulder_pitch", "elbow")] + ["neck_yaw"]
REST_ARMS = {"l_shoulder_pitch": 0.0, "r_shoulder_pitch": 0.0, "l_elbow": math.radians(-20), "r_elbow": math.radians(-20)}


def load_config(path: Path = HERE / "config.yaml") -> dict:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


# ------------------------------------------------------------------------------------------------ back ends
class RealTime:
    """Frame pacing for the real-time back ends: tick(dt) returns at the next frame boundary (50 Hz bus packets)."""
    _t_next = None

    def tick(self, dt):
        now = time.perf_counter()
        if self._t_next is None or now - self._t_next > 0.1:          # first frame, or fell behind: restart the clock
            self._t_next = now
        self._t_next += dt
        time.sleep(max(0.0, self._t_next - time.perf_counter()))

    def sleep(self, seconds):
        time.sleep(seconds)


class HardwareIO(RealTime):
    """The real robot. Joint angle -> servo ticks: zero_ticks + direction * angle * 4096 / 2 pi, clamped to the limits."""

    def __init__(self, cfg: dict):
        from .imu import MPU6050
        from .servo_bus import ServoBus, TICKS_PER_REV
        self.cfg, self.tpr = cfg, TICKS_PER_REV
        b = cfg["bus"]
        self.bus = ServoBus(b["port"], b["baud"])
        self.servos = {**cfg["leg_servos"], **cfg["arm_servos"]}
        im = cfg["imu"]
        self.imu = MPU6050(im["i2c_bus"], im["address"], im.get("mount"))
        self.imu.calibrate()

    def torque(self, on: bool):
        for s in self.servos.values():
            self.bus.torque(s["id"], on)

    def send(self, q: dict):
        ticks = {}
        for name, s in self.servos.items():
            if name in q:
                lo, hi = (math.radians(v) for v in s["limits_deg"])
                a = min(max(q[name], lo), hi)
                ticks[s["id"]] = int(round(s["zero_ticks"] + s["direction"] * a * self.tpr / (2 * math.pi)))
        self.bus.set_positions(ticks)

    def attitude(self):
        roll, pitch, yaw, rate = self.imu.update()
        return roll, pitch, yaw, rate

    def read_pose(self) -> dict:
        """Every joint angle from the servo encoders."""
        return {name: s["direction"] * (self.bus.position(s["id"]) - s["zero_ticks"]) * 2 * math.pi / self.tpr
                for name, s in self.servos.items()}

    def close(self):
        self.torque(False)


class SimIO(RealTime):
    """JX0 in MuJoCo with the servo model (physics in a background thread, real time, optional viewer)."""

    def __init__(self, cfg: dict, viewer: bool = True):
        import sys
        import mujoco
        import mujoco.viewer
        root = HERE.parents[2]
        sys.path.insert(0, str(root / "jx0" / "sim"))
        from jx0_model import build
        from walk_jx0 import ServoModel
        from jx1calc.design import Design
        self.mj = mujoco
        design = Design(root / "jx0" / "design_point.yaml")
        self.m = mujoco.MjModel.from_xml_string(build(design))
        self.d = mujoco.MjData(self.m)
        st, b = design.act_classes["ST"], cfg["bus"]
        self.servo = ServoModel(st["stall_torque_nm"], st["no_load_speed_rad_s"], b["stiffness_nm_per_rad"], b["damping_nm_s_per_rad"])
        names = LEG_JOINTS + ARM_JOINTS
        self.adr = {n: (self.m.jnt_qposadr[mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_JOINT, n)],
                        self.m.jnt_dofadr[mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_JOINT, n)]) for n in names}
        self.act = {n: mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_ACTUATOR, n) for n in names}
        self.goal = {n: 0.0 for n in names}
        self.lock = threading.Lock()
        self.running = True
        self.viewer = mujoco.viewer.launch_passive(self.m, self.d) if viewer else None
        threading.Thread(target=self._physics, daemon=True).start()

    def settle(self, q0: dict):
        """Put the robot in a pose on the floor before the physics runs."""
        with self.lock:
            for n, v in q0.items():
                self.d.qpos[self.adr[n][0]] = v
                self.goal[n] = v
            self.mj.mj_forward(self.m, self.d)
            sole = min(self.d.site_xpos[self.mj.mj_name2id(self.m, self.mj.mjtObj.mjOBJ_SITE, s)][2] for s in ("l_sole", "r_sole"))
            self.d.qpos[2] -= sole - 0.001
            self.mj.mj_forward(self.m, self.d)

    def _physics(self):
        dt = self.m.opt.timestep
        t_wall = time.perf_counter()
        while self.running:
            with self.lock:
                for n, g in self.goal.items():
                    qa, da = self.adr[n]
                    self.d.ctrl[self.act[n]] = self.servo.torque(g, self.d.qpos[qa], self.d.qvel[da])
                self.mj.mj_step(self.m, self.d)
            t_wall += dt
            ahead = t_wall - time.perf_counter()
            if ahead > 0:
                time.sleep(ahead)
            if self.viewer is not None and int(self.d.time / dt) % 16 == 0:
                self.viewer.sync()

    def torque(self, on):
        pass

    def read_pose(self) -> dict:
        with self.lock:
            return {n: float(self.d.qpos[qa]) for n, (qa, _) in self.adr.items()}

    def send(self, q: dict):
        with self.lock:
            self.goal.update(q)

    def attitude(self):
        with self.lock:
            w, x, y, z = self.d.qpos[3:7]
            rate = self.d.qvel[3:6].copy()
        roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
        pitch = math.asin(max(-1.0, min(1.0, 2 * (w * y - z * x))))
        yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
        return roll, pitch, yaw, rate

    def close(self):
        self.running = False


# ------------------------------------------------------------------------------------------------ the robot
class Robot:
    def __init__(self, io, cfg: dict):
        self.io, self.cfg = io, cfg
        self.gaits = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (HERE / "gaits").glob("*.json")}
        f = self.gaits["forward_2"]
        self.stand_pose = {k: v for k, v in zip(f["joints"], f["q"][0]) if k in LEG_JOINTS}   # walking stance, knees bent
        self.q = {**{j: 0.0 for j in LEG_JOINTS + ARM_JOINTS}, **REST_ARMS}
        self.bal = cfg["balance"]
        self.dt = 1.0 / cfg["bus"]["rate_hz"]
        self.busy = threading.Lock()

    # ---------------------------------------------------------------- low level
    def _send(self, q: dict):
        self.q.update(q)
        self.io.send(self.q)

    def move_to(self, target: dict, seconds: float):
        """Smooth (cosine) move of some joints to target angles."""
        start = {k: self.q[k] for k in target}
        n = max(1, int(seconds / self.dt))
        for i in range(1, n + 1):
            s = 0.5 - 0.5 * math.cos(math.pi * i / n)
            self._send({k: start[k] + (v - start[k]) * s for k, v in target.items()})
            self.io.tick(self.dt)

    def stand(self, seconds: float = 1.5):
        """Smoothly into the walking stance, starting from where the joints really are (encoders / simulation)."""
        if hasattr(self.io, "read_pose"):
            self.q.update(self.io.read_pose())
        self.move_to({**self.stand_pose, **REST_ARMS, "neck_yaw": 0.0}, seconds)

    def play(self, name: str):
        """Play one verified gait (legs and arm swing) at 50 Hz with the IMU stabiliser on the stance leg(s)."""
        g = self.gaits[name]
        joints, k_a, d_a, k_h = g["joints"], self.bal["k_ankle"], self.bal["d_ankle"], self.bal["k_hip"]
        for frame, stance in zip(g["q"], g["stance"]):
            roll, pitch, _, rate = self.io.attitude()
            q = dict(zip(joints, frame))
            for side, on in (("l", stance[0]), ("r", stance[1])):
                if on:
                    q[f"{side}_ankle_pitch"] += k_a * pitch + d_a * rate[1]
                    q[f"{side}_ankle_roll"] += k_a * roll + d_a * rate[0]
                    q[f"{side}_hip_pitch"] += k_h * pitch
                    q[f"{side}_hip_roll"] += k_h * roll
            self._send(q)
            if abs(roll) > math.radians(25) or abs(pitch) > math.radians(25):
                raise RuntimeError("tipping over: stopped the gait")
            self.io.tick(self.dt)

    # ---------------------------------------------------------------- actions (the brain's tools)
    def walk(self, steps: int, direction: str = "forward") -> str:
        steps = max(1, min(10, int(steps)))
        if direction == "forward":             # verified blocks: forward (10 steps), forward_4, forward_2
            plan = ["forward"] if steps >= 10 else ["forward_4"] * (steps // 4) + ["forward_2"] * ((steps % 4 + 1) // 2)
        elif direction == "backward":
            plan = ["backward_4"] * (steps // 4) + ["backward_2"] * ((steps % 4 + 1) // 2)
        else:                                  # side-steps come in pairs
            plan = [f"side_{direction}_2"] * ((steps + 1) // 2)
        with self.busy:
            for g in plan:
                self.play(g)
            self.stand(0.5)
        return f"walked {steps} steps {direction}"

    def turn(self, degrees: int) -> str:
        """Repeat the 2-step turn block (~10 deg: the first step of a block only shifts weight) until the IMU yaw says we
        are there. Closing the loop on the measured yaw (gyro-integrated on the robot) also absorbs foot slip."""
        g = "turn_left_2" if degrees > 0 else "turn_right_2"
        yaw0 = self.io.attitude()[2]
        turned = 0.0
        with self.busy:
            for _ in range(24):
                if abs(degrees) - abs(turned) < 5.0:
                    break
                self.play(g)
                turned = math.degrees(math.remainder(self.io.attitude()[2] - yaw0, 2 * math.pi))
            self.stand(0.5)
        return f"turned {turned:.0f} degrees"

    def wave(self, arm: str = "right") -> str:
        """Raise the arm up in front and wag the blade at the elbow."""
        s = "l" if arm == "left" else "r"
        with self.busy:
            self.move_to({f"{s}_shoulder_pitch": math.radians(-150), f"{s}_elbow": math.radians(-30)}, 0.8)
            for _ in range(3):
                self.move_to({f"{s}_elbow": math.radians(10)}, 0.25)
                self.move_to({f"{s}_elbow": math.radians(-50)}, 0.25)
            self.move_to({f"{s}_shoulder_pitch": REST_ARMS[f"{s}_shoulder_pitch"], f"{s}_elbow": REST_ARMS[f"{s}_elbow"]}, 0.8)
        return f"waved the {arm} arm"

    def nod(self, kind: str = "yes") -> str:
        with self.busy:
            if kind == "no":                                   # shake the head
                for _ in range(2):
                    self.move_to({"neck_yaw": math.radians(30)}, 0.2)
                    self.move_to({"neck_yaw": math.radians(-30)}, 0.25)
                self.move_to({"neck_yaw": 0.0}, 0.2)
            else:                                              # a small bow from the hips (JX0 has no neck pitch)
                base = {k: self.stand_pose[k] for k in ("l_hip_pitch", "r_hip_pitch")}
                for _ in range(2):
                    self.move_to({k: v - math.radians(8) for k, v in base.items()}, 0.3)
                    self.move_to(base, 0.3)
        return "nodded " + kind

    def look(self, direction: str = "center") -> str:
        target = {"left": 45.0, "right": -45.0}.get(direction, 0.0)
        with self.busy:
            self.move_to({"neck_yaw": math.radians(target)}, 0.4)
        return f"looking {direction}"

    def act(self, name: str, args: dict) -> str:
        """Entry point for the brain's validated tool calls."""
        if name == "wave":
            return self.wave(args["arm"])
        if name == "nod":
            return self.nod(args["kind"])
        if name == "look":
            return self.look(args["direction"])
        if name == "walk":
            return self.walk(args["steps"], args["direction"])
        if name == "turn":
            return self.turn(args["degrees"])
        raise ValueError(f"unknown action {name}")
