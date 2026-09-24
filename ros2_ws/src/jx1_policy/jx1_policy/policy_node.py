"""ROS 2 node: runs the exported JX1 walking policy at the trained control rate.

Subscribes  /jx1/joint_states (sensor_msgs/JointState), /jx1/imu (sensor_msgs/Imu, pelvis-fixed IMU), /cmd_vel (Twist)
Publishes   /jx1/joint_command (sensor_msgs/JointState, position targets for every actuated joint; the simulator or the
            CAN hub applies the policy_io.yaml PD gains) — or, with output:=ros2_control, a Float64MultiArray for the
            forward position controller of jx1_bringup/config/controllers.yaml.
States      WAIT (no fresh state) -> RAMP (2 s interpolation to the default pose) -> WALK (policy) ; stale state -> HOLD.
"""
from __future__ import annotations

import numpy as np
import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import Imu, JointState
from std_msgs.msg import Float64MultiArray, String

from .runner import PolicyRunner


class PolicyNode(Node):
    def __init__(self):
        super().__init__("jx1_policy")
        self.declare_parameter("policy_dir", "")
        self.declare_parameter("output", "direct")                 # direct | ros2_control
        self.declare_parameter("state_timeout_s", 0.1)
        self.declare_parameter("cmd_timeout_s", 0.5)
        self.declare_parameter("ramp_s", 2.0)
        self.declare_parameter("max_cmd", [0.8, 0.3, 0.6])
        pdir = self.get_parameter("policy_dir").value
        if not pdir:
            from ament_index_python.packages import get_package_share_directory
            pdir = f"{get_package_share_directory('jx1_policy')}/policies/jx1_walk_rough"
        self.runner = PolicyRunner(pdir)
        self.get_logger().info(f"policy {pdir}: {len(self.runner.policy_joints)} joints, {1 / self.runner.dt:.0f} Hz")
        self.joint_pos, self.joint_vel, self.stamp_js = {}, {}, None
        self.quat, self.gyro, self.stamp_imu = None, None, None
        self.cmd, self.stamp_cmd = np.zeros(3), None
        self.state, self.t_state = "WAIT", self.now()
        self.ramp_from = {}
        self.create_subscription(JointState, "/jx1/joint_states", self.on_js, 10)
        self.create_subscription(Imu, "/jx1/imu", self.on_imu, 10)
        self.create_subscription(Twist, "/cmd_vel", self.on_cmd, 10)
        self.pub_cmd = self.create_publisher(JointState, "/jx1/joint_command", 10)
        self.pub_fwd = self.create_publisher(Float64MultiArray, "/jx1_position_controller/commands", 10)
        self.pub_state = self.create_publisher(String, "/jx1/policy_state", 10)
        self.create_timer(self.runner.dt, self.tick)

    def now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def on_js(self, msg):
        for i, n in enumerate(msg.name):
            if i < len(msg.position):
                self.joint_pos[n] = msg.position[i]
            if i < len(msg.velocity):
                self.joint_vel[n] = msg.velocity[i]
        self.stamp_js = self.now()

    def on_imu(self, msg):
        o, w = msg.orientation, msg.angular_velocity
        self.quat = np.array([o.w, o.x, o.y, o.z])
        self.gyro = np.array([w.x, w.y, w.z])
        self.stamp_imu = self.now()

    def on_cmd(self, msg):
        lim = np.array(self.get_parameter("max_cmd").value, dtype=float)
        self.cmd = np.clip([msg.linear.x, msg.linear.y, msg.angular.z], -lim, lim)
        self.stamp_cmd = self.now()

    def fresh(self, t):
        to = self.get_parameter("state_timeout_s").value
        # only the policy joints must be reported: held joints without feedback (e.g. the neck servos, not on the CAN hubs)
        # keep their default targets
        return (self.stamp_js is not None and self.stamp_imu is not None and t - self.stamp_js < to and t - self.stamp_imu < to
                and all(j in self.joint_pos for j in self.runner.policy_joints))

    def publish(self, targets: dict):
        names = self.runner.all_joints
        if self.get_parameter("output").value == "ros2_control":
            self.pub_fwd.publish(Float64MultiArray(data=[float(targets[j]) for j in names]))
        else:
            msg = JointState()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.name = names
            msg.position = [float(targets[j]) for j in names]
            self.pub_cmd.publish(msg)

    def tick(self):
        t = self.now()
        if not self.fresh(t):
            if self.state in ("RAMP", "WALK"):
                self.get_logger().warn("state stale: holding position")
                self.publish({j: self.joint_pos.get(j, self.runner.default_all[j]) for j in self.runner.all_joints})
            self.state, self.t_state = "WAIT", t
        elif self.state == "WAIT":
            self.state, self.t_state = "RAMP", t
            self.ramp_from = {j: self.joint_pos.get(j, self.runner.default_all[j]) for j in self.runner.all_joints}
        if self.state == "RAMP":
            a = min(1.0, (t - self.t_state) / self.get_parameter("ramp_s").value)
            self.publish({j: (1 - a) * self.ramp_from[j] + a * self.runner.default_all[j] for j in self.runner.all_joints})
            if a >= 1.0:
                self.state, self.t_state = "WALK", t
                self.runner.reset()
        elif self.state == "WALK":
            cmd = self.cmd if (self.stamp_cmd is not None and t - self.stamp_cmd < self.get_parameter("cmd_timeout_s").value) else np.zeros(3)
            q = [self.joint_pos[j] for j in self.runner.policy_joints]
            dq = [self.joint_vel.get(j, 0.0) for j in self.runner.policy_joints]
            self.publish(self.runner.step(self.quat, self.gyro, q, dq, cmd, t - self.t_state))
        self.pub_state.publish(String(data=self.state))


def main():
    rclpy.init()
    node = PolicyNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
