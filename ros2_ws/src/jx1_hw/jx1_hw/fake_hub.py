"""JX1 hub emulator: the two CAN hubs' host protocol and control law on the MuJoCo CAD model (hardware-in-the-loop
without hardware), for testing jx1_hw + jx1_policy end to end.

Two TCP servers (hub A, hub B) speak the USB-serial protocol of firmware/hub/jx1_hub/jx1_hub.ino. Every 2 ms (the
firmware bus period) each hub joint runs the RobStride MIT law  tau = kp (q* - q) + kd (dq* - dq) + tau_ff  on host
targets interpolated between frames, clamped to the soft limits and the hub torque limit; DAMPING (kd only) until the
host requests RUN and whenever host frames stop for longer than HOST_TIMEOUT. Ankle motors act through the push-rod
linkage (crank angles by IK from the ankle joints, torques mapped with J^T). State frames go back every STATE_DIV bus
periods. Like a bring-up gantry, the base is held in place until the first RUN. The node also publishes /clock,
/jx1/imu and /jx1/odom (on the robot the IMU is read by the Jetson, not by the hubs).
Parameters: model_path (CAD MJCF), hw_config (config/hw.yaml), port_a (5555), port_b (5556), real_time_factor (1.0).
"""
from __future__ import annotations

import socket
import threading
import time
from pathlib import Path

import mujoco
import numpy as np
import rclpy
import yaml
from builtin_interfaces.msg import Time
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rosgraph_msgs.msg import Clock
from sensor_msgs.msg import Imu

from . import protocol as P
from .ankle import ParallelAnkle


def stamp(t):
    s = int(t)
    return Time(sec=s, nanosec=int((t - s) * 1e9))


class HubEmu:
    """One hub: host frames in, MIT torques out (hub joint space)."""

    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.nj = len(cfg["joints"])
        self.lo = np.array([j["q_min"] for j in cfg["joints"]]) + cfg["soft_margin_rad"]
        self.hi = np.array([j["q_max"] for j in cfg["joints"]]) - cfg["soft_margin_rad"]
        self.tau_lim = np.array([j["tau_limit"] for j in cfg["joints"]])
        self.prev = np.zeros((self.nj, 5))
        self.next = np.zeros((self.nj, 5))
        self.host_last, self.host_period = -1.0, 0.02
        self.mode, self.seq = P.DAMPING, 0
        self.ever_run = False
        self.reader = P.FrameReader(P.CMD_HEAD, P.command_size(self.nj))

    def on_frame(self, frame: bytes, t: float):
        seq, mode, rows = P.unpack_command(frame, self.nj)
        self.prev, self.next = self.next, np.array(rows)
        if self.host_last >= 0:
            self.host_period = float(np.clip(t - self.host_last, 0.005, 0.04))
        self.host_last, self.seq = t, seq
        if mode == P.RUN:
            self.mode, self.ever_run = P.RUN, True
        elif mode == P.DAMPING:
            self.mode = P.DAMPING

    def torques(self, t, q, dq):
        if self.host_last < 0 or t - self.host_last > self.cfg["host_timeout_us"] * 1e-6:
            self.mode = P.DAMPING
        a = np.clip((t - self.host_last) / self.host_period, 0.0, 1.0)
        q_des = np.clip(self.prev[:, 0] + a * (self.next[:, 0] - self.prev[:, 0]), self.lo, self.hi)
        dq_des, kp, kd, tff = self.next[:, 1], self.next[:, 2], self.next[:, 3], self.next[:, 4]
        if self.mode != P.RUN:
            return np.clip(-self.cfg["damping_kd"] * dq, -self.tau_lim, self.tau_lim)
        return np.clip(kp * (q_des - q) + kd * (dq_des - dq) + tff, -self.tau_lim, self.tau_lim)


class FakeHubNode(Node):
    def __init__(self):
        super().__init__("jx1_fake_hubs")
        self.declare_parameter("model_path", "")
        self.declare_parameter("hw_config", "")
        self.declare_parameter("policy_io", "")
        self.declare_parameter("port_a", 5555)
        self.declare_parameter("port_b", 5556)
        self.declare_parameter("real_time_factor", 1.0)
        cfg = yaml.safe_load(Path(self.get_parameter("hw_config").value).read_text(encoding="utf-8"))
        io = yaml.safe_load(Path(self.get_parameter("policy_io").value).read_text(encoding="utf-8"))
        m = self.m = mujoco.MjModel.from_xml_path(self.get_parameter("model_path").value)
        self.d = mujoco.MjData(m)
        m.actuator_gainprm[:, 0] = 1.0                     # MJCF position actuators -> torque motors (ctrl = N m)
        m.actuator_biasprm[:, :] = 0.0
        m.actuator_ctrllimited[:] = 0
        self.act = {mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, m.actuator_trnid[a, 0]): a for a in range(m.nu)}
        self.qadr = {j: m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, j)] for j in self.act}
        self.dadr = {j: m.jnt_dofadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, j)] for j in self.act}
        self.hubs = {h: HubEmu(c) for h, c in cfg["hubs"].items()}
        self.names = {h: [j["name"] for j in c["joints"]] for h, c in cfg["hubs"].items()}
        self.ankle = {s: ParallelAnkle.from_params(cfg["ankle"], s) for s in ("left", "right")}
        on_hub = {f"{n}_joint" for ns in self.names.values() for n in ns} | {f"{s}_ankle_{a}_joint" for s in ("left", "right") for a in ("pitch", "roll")}
        self.servo = [j for j in self.act if j not in on_hub]        # neck servos: held at the default pose
        self.default = io["default_joint_pos"]
        # stand pose on the floor, base held by the "gantry" until RUN
        for j, a in self.act.items():
            self.d.qpos[self.qadr[j]] = self.default.get(j, 0.0)
        soles = [mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, f"{s}_sole") for s in ("left", "right")]
        self.d.qpos[2] = 1.0
        mujoco.mj_kinematics(m, self.d)
        self.d.qpos[2] = 1.0 - min(self.d.site_xpos[s][2] for s in soles) + 0.002
        mujoco.mj_forward(m, self.d)
        self.gantry = self.d.qpos[:7].copy()
        g = lambda n: slice(m.sensor_adr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SENSOR, n)],  # noqa: E731
                            m.sensor_adr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SENSOR, n)] + 3)
        self.s_gyro, self.s_acc = g("imu_gyro"), g("imu_acc")
        self.pub_clock = self.create_publisher(Clock, "/clock", 10)
        self.pub_imu = self.create_publisher(Imu, "/jx1/imu", 10)
        self.pub_odom = self.create_publisher(Odometry, "/jx1/odom", 10)
        self.servers = {}
        for h in self.hubs:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("127.0.0.1", int(self.get_parameter(f"port_{h}").value)))
            s.listen(1)
            s.setblocking(False)
            self.servers[h] = [s, None]
        self.running = True
        threading.Thread(target=self.loop, daemon=True).start()
        self.get_logger().info(f"hub emulator on ports {[self.get_parameter(f'port_{h}').value for h in self.hubs]}; gantry holds the base until RUN")

    # -------------------------------------------------------------- hub joint space <-> MuJoCo
    def hub_q(self, h):
        d, q, dq = self.d, [], []
        for n in self.names[h]:
            if "ankle_motor" in n:
                s = "left" if n.startswith("left_") else "right"
                p, r = d.qpos[self.qadr[f"{s}_ankle_pitch_joint"]], d.qpos[self.qadr[f"{s}_ankle_roll_joint"]]
                dp, dr = d.qvel[self.dadr[f"{s}_ankle_pitch_joint"]], d.qvel[self.dadr[f"{s}_ankle_roll_joint"]]
                i = 0 if n.endswith("A") else 1
                q.append(self.ankle[s].crank_angles(p, r)[i])
                dq.append((self.ankle[s].jacobian(p, r) @ np.array([dp, dr]))[i])
            elif f"{n}_joint" in self.qadr:
                q.append(d.qpos[self.qadr[f"{n}_joint"]])
                dq.append(d.qvel[self.dadr[f"{n}_joint"]])
            else:                               # hub joint not in this MJCF (e.g. arms on the placeholder-torso model): ideal joint
                hub = self.hubs[h]
                q.append(hub.next[self.names[h].index(n), 0] if hub.host_last >= 0 else self.default.get(f"{n}_joint", 0.0))
                dq.append(0.0)
        return np.array(q), np.array(dq)

    def apply(self, h, tau):
        d = self.d
        motors = {"left": np.zeros(2), "right": np.zeros(2)}
        for k, n in enumerate(self.names[h]):
            if "ankle_motor" in n:
                motors["left" if n.startswith("left_") else "right"][0 if n.endswith("A") else 1] = tau[k]
            elif f"{n}_joint" in self.act:
                d.ctrl[self.act[f"{n}_joint"]] = tau[k]
        for s, tm in motors.items():
            if any(f"{s}_ankle_motor" in n for n in self.names[h]):
                p, r = d.qpos[self.qadr[f"{s}_ankle_pitch_joint"]], d.qpos[self.qadr[f"{s}_ankle_roll_joint"]]
                tq = self.ankle[s].joint_torque(p, r, *tm)
                d.ctrl[self.act[f"{s}_ankle_pitch_joint"]] = tq[0]
                d.ctrl[self.act[f"{s}_ankle_roll_joint"]] = tq[1]

    # -------------------------------------------------------------- I/O
    def poll(self, t):
        for h, sv in self.servers.items():
            srv, cli = sv
            if cli is None:
                try:
                    cli, _ = srv.accept()
                    cli.setblocking(False)
                    cli.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                    sv[1] = cli
                except BlockingIOError:
                    continue
            try:
                data = cli.recv(65536)
                if data == b"":
                    sv[1] = None
                    continue
                for frame in self.hubs[h].reader.feed(data):
                    self.hubs[h].on_frame(frame, t)
            except BlockingIOError:
                pass
            except OSError:
                sv[1] = None

    def send_states(self):
        for h, (srv, cli) in self.servers.items():
            if cli is None:
                continue
            q, dq = self.hub_q(h)
            hub = self.hubs[h]
            tau = hub.last_tau if hasattr(hub, "last_tau") else np.zeros(hub.nj)
            st = P.HubState(seq=hub.seq, estop=False, fault=False, mode=hub.mode, q=list(q), dq=list(dq), tau=list(tau),
                            temp=[40.0] * hub.nj, faults=[0] * hub.nj)
            try:
                cli.sendall(P.pack_state(st))
            except OSError:
                self.servers[h][1] = None

    def publish(self):
        d = self.d
        t = stamp(d.time)
        self.pub_clock.publish(Clock(clock=t))
        imu = Imu()
        imu.header.stamp, imu.header.frame_id = t, "imu_link"
        imu.orientation.w, imu.orientation.x, imu.orientation.y, imu.orientation.z = map(float, d.qpos[3:7])
        imu.angular_velocity.x, imu.angular_velocity.y, imu.angular_velocity.z = map(float, d.sensordata[self.s_gyro])
        imu.linear_acceleration.x, imu.linear_acceleration.y, imu.linear_acceleration.z = map(float, d.sensordata[self.s_acc])
        self.pub_imu.publish(imu)
        od = Odometry()
        od.header.stamp, od.header.frame_id, od.child_frame_id = t, "odom", "pelvis"
        od.pose.pose.position.x, od.pose.pose.position.y, od.pose.pose.position.z = map(float, d.qpos[0:3])
        od.pose.pose.orientation.w, od.pose.pose.orientation.x, od.pose.pose.orientation.y, od.pose.pose.orientation.z = map(float, d.qpos[3:7])
        od.twist.twist.linear.x, od.twist.twist.linear.y, od.twist.twist.linear.z = map(float, d.qvel[0:3])
        self.pub_odom.publish(od)

    def loop(self):
        m, d = self.m, self.d
        rtf = float(self.get_parameter("real_time_factor").value)
        div = next(iter(self.hubs.values())).cfg["state_div"]
        wall0, k = time.perf_counter(), 0
        while self.running and rclpy.ok():
            t = d.time
            self.poll(t)
            for h, hub in self.hubs.items():
                q, dq = self.hub_q(h)
                hub.last_tau = hub.torques(t, q, dq)
                self.apply(h, hub.last_tau)
            for j in self.servo:
                d.ctrl[self.act[j]] = 5.0 * (self.default.get(j, 0.0) - d.qpos[self.qadr[j]]) - 0.1 * d.qvel[self.dadr[j]]
            if not any(h.ever_run for h in self.hubs.values()):
                d.qpos[:7], d.qvel[:6] = self.gantry, 0.0               # bring-up gantry
            mujoco.mj_step(m, d)
            k += 1
            if k % div == 0:
                self.send_states()
            if k % 5 == 0:
                self.publish()
            if rtf > 0:
                ahead = d.time / rtf - (time.perf_counter() - wall0)
                if ahead > 0:
                    time.sleep(ahead)


def main():
    rclpy.init()
    node = FakeHubNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.running = False
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
