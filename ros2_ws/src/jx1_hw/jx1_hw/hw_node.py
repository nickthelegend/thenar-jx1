"""ROS 2 hardware bridge: JX1 joint space <-> the two Teensy 4.1 CAN hubs over USB serial (firmware/hub/jx1_hub).

Subscribes  /jx1/joint_command (sensor_msgs/JointState position targets, e.g. from jx1_policy)
Publishes   /jx1/joint_states (joint space, ankle pitch/roll from the crank motors), /jx1/hw/status (JSON)
Services    /jx1/hw/run (Trigger): request RUN (hubs refuse while the E-stop is pressed or a fault is latched)
            /jx1/hw/damp (Trigger): back to DAMPING
Fall guard  /jx1/imu tilt above fall_tilt_deg (50) latches DAMPING until the next /jx1/hw/run
Parameters  port_a / port_b: serial devices (e.g. /dev/ttyACM0) or pyserial URLs (socket://localhost:5555 for the emulator)
            policy_io: policy_io.yaml (PD gains, default pose); hw_config: config/hw.yaml; rate_hz: command rate (50)
The hubs interpolate between host commands at 500 Hz, apply soft limits, temperature derating and watchdogs; this node
only converts spaces and keeps the stream going. Each /jx1/joint_command is forwarded at once, so the hub ramp starts on
the policy's clock; a timer only keeps the stream alive (hub watchdog 50 ms) while no command arrives. A free-running
50 Hz send timer added a random 0-20 ms phase delay (hardware-in-the-loop measurement). Starts in DAMPING; RUN must be
requested explicitly.
"""
from __future__ import annotations

import json
import math
import threading
import time
from pathlib import Path

import rclpy
import serial
import yaml
from rclpy.node import Node
from sensor_msgs.msg import Imu, JointState
from std_msgs.msg import String
from std_srvs.srv import Trigger

from . import protocol as P
from .bridge import Bridge


class HwNode(Node):
    def __init__(self):
        super().__init__("jx1_hw")
        self.declare_parameter("port_a", "/dev/ttyACM0")
        self.declare_parameter("port_b", "/dev/ttyACM1")
        self.declare_parameter("policy_io", "")
        self.declare_parameter("hw_config", "")
        self.declare_parameter("rate_hz", 50.0)
        self.declare_parameter("fall_tilt_deg", 50.0)
        hw_cfg = self.get_parameter("hw_config").value
        if not hw_cfg:
            from ament_index_python.packages import get_package_share_directory
            hw_cfg = str(Path(get_package_share_directory("jx1_hw")) / "config" / "hw.yaml")
        self.cfg = yaml.safe_load(Path(hw_cfg).read_text(encoding="utf-8"))
        io = yaml.safe_load(Path(self.get_parameter("policy_io").value).read_text(encoding="utf-8"))
        self.bridge = Bridge(self.cfg, io)
        self.lock = threading.Lock()
        self.targets = {}
        self.mode = P.DAMPING
        self.seq = 0
        self.states = {}
        self.ports = {h: self.open_port(self.get_parameter(f"port_{h}").value) for h in ("a", "b")}
        self.pub_js = self.create_publisher(JointState, "/jx1/joint_states", 10)
        self.pub_status = self.create_publisher(String, "/jx1/hw/status", 10)
        self.create_subscription(JointState, "/jx1/joint_command", self.on_cmd, 10)
        self.create_subscription(Imu, "/jx1/imu", self.on_imu, 10)
        self.fall_latched = False
        self.create_service(Trigger, "/jx1/hw/run", self.on_run)
        self.create_service(Trigger, "/jx1/hw/damp", self.on_damp)
        self.last_send = -1.0
        self.create_timer(1.0 / self.get_parameter("rate_hz").value, self.tick)
        self.running = True
        self.readers = [threading.Thread(target=self.read_loop, args=(h,), daemon=True) for h in self.ports]
        for t in self.readers:
            t.start()
        self.get_logger().info(f"hubs a={self.get_parameter('port_a').value} b={self.get_parameter('port_b').value}; DAMPING until /jx1/hw/run")

    def open_port(self, url, attempts=60):
        """USB hubs can enumerate late (and the emulator may still be starting): retry for up to 30 s."""
        for k in range(attempts):
            try:
                return serial.serial_for_url(url, baudrate=2_000_000, timeout=0.01)
            except (serial.SerialException, OSError) as e:
                if k % 10 == 0:
                    self.get_logger().warn(f"cannot open {url} ({e}); retrying")
                time.sleep(0.5)
        raise RuntimeError(f"hub port {url} not available")

    def on_cmd(self, msg: JointState):
        with self.lock:
            self.targets.update(dict(zip(msg.name, msg.position)))
        self.send()

    def on_imu(self, msg: Imu):
        q = msg.orientation
        tilt = math.degrees(math.acos(max(-1.0, min(1.0, 1.0 - 2.0 * (q.x * q.x + q.y * q.y)))))
        if self.mode == P.RUN and tilt > self.get_parameter("fall_tilt_deg").value:
            self.mode, self.fall_latched = P.DAMPING, True
            self.get_logger().error(f"fall detected (tilt {tilt:.0f} deg): hubs -> DAMPING until /jx1/hw/run")

    def on_run(self, req, res):
        self.fall_latched = False
        self.mode = P.RUN
        res.success, res.message = True, "RUN requested (hubs stay in DAMPING while E-stop pressed / fault latched)"
        return res

    def on_damp(self, req, res):
        self.mode = P.DAMPING
        res.success, res.message = True, "DAMPING"
        return res

    def send(self):
        with self.lock:
            rows = self.bridge.commands(self.targets)
        self.seq += 1
        for h, port in self.ports.items():
            port.write(P.pack_command(self.seq, self.mode, rows[h]))
        self.last_send = time.monotonic()

    def tick(self):
        if time.monotonic() - self.last_send > 1.5 / self.get_parameter("rate_hz").value:
            self.send()                                  # keepalive: no policy command in the last period
        st = {h: {"mode": s.mode, "estop": s.estop, "fault": s.fault, "stale": [n for n, x in zip(self.bridge.hubs[h], s.stale) if x]}
              for h, s in self.states.items()}
        self.pub_status.publish(String(data=json.dumps({"requested": self.mode, "fall_latched": self.fall_latched, "hubs": st})))

    def read_loop(self, h):
        nj = len(self.bridge.hubs[h])
        reader = P.FrameReader(P.STATE_HEAD, P.state_size(nj))
        port = self.ports[h]
        while self.running and rclpy.ok():
            data = port.read(4096)
            for frame in reader.feed(data):
                self.states[h] = P.unpack_state(frame, nj)
                if h == "a" and len(self.states) == len(self.ports):
                    self.publish_joint_states()

    def publish_joint_states(self):
        js = self.bridge.decode(dict(self.states))
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(js)
        msg.position = [v[0] for v in js.values()]
        msg.velocity = [v[1] for v in js.values()]
        msg.effort = [v[2] for v in js.values()]
        self.pub_js.publish(msg)

    def destroy_node(self):
        self.running = False
        rows = self.bridge.commands({})
        for h, port in self.ports.items():          # leave the hubs in DAMPING (their watchdog would do it after 50 ms anyway)
            try:
                port.write(P.pack_command(self.seq + 1, P.DAMPING, rows[h]))
                port.close()
            except Exception:
                pass
        super().destroy_node()


def main():
    rclpy.init()
    node = HwNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
