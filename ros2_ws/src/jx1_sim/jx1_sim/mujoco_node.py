"""ROS 2 MuJoCo simulator for JX1 (sim-to-sim target for the walking policy and for ros2_control).

Steps the CAD MJCF (simulation/mujoco/jx1.xml) in scaled real time on its own thread and publishes
  /clock (rosgraph_msgs/Clock)            sim time — run the other nodes with use_sim_time:=true
  /jx1/joint_states (sensor_msgs/JointState)   every actuated joint: position, velocity, effort
  /jx1/imu (sensor_msgs/Imu)                    pelvis IMU: orientation, angular velocity, linear acceleration
  /jx1/odom (nav_msgs/Odometry) + TF odom -> pelvis   ground truth
and applies /jx1/joint_command (sensor_msgs/JointState, position targets by joint name) through the MJCF position
actuators with the PD gains of policy_io.yaml. Service /jx1/reset (std_srvs/Trigger) puts the robot back on its feet.
"""
from __future__ import annotations

import threading
import time

import rclpy
from builtin_interfaces.msg import Time
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rosgraph_msgs.msg import Clock
from sensor_msgs.msg import Imu, JointState
from std_srvs.srv import Trigger
from tf2_ros import TransformBroadcaster

from .sim_core import MujocoSim


def stamp(t: float) -> Time:
    s = int(t)
    return Time(sec=s, nanosec=int((t - s) * 1e9))


class MujocoNode(Node):
    def __init__(self):
        super().__init__("jx1_mujoco")
        self.declare_parameter("model_path", "")
        self.declare_parameter("policy_io", "")
        self.declare_parameter("publish_rate_hz", 200.0)
        self.declare_parameter("real_time_factor", 1.0)
        self.declare_parameter("viewer", False)
        model = self.get_parameter("model_path").value
        if not model:
            raise RuntimeError("parameter model_path is required (repo/simulation/mujoco/jx1.xml)")
        self.sim = MujocoSim(model, self.get_parameter("policy_io").value or None)
        self.lock = threading.Lock()
        self.pub_clock = self.create_publisher(Clock, "/clock", 10)
        self.pub_js = self.create_publisher(JointState, "/jx1/joint_states", 10)
        self.pub_imu = self.create_publisher(Imu, "/jx1/imu", 10)
        self.pub_odom = self.create_publisher(Odometry, "/jx1/odom", 10)
        self.tf = TransformBroadcaster(self)
        self.create_subscription(JointState, "/jx1/joint_command", self.on_cmd, 10)
        self.create_service(Trigger, "/jx1/reset", self.on_reset)
        self.viewer = None
        if self.get_parameter("viewer").value:
            import mujoco.viewer
            self.viewer = mujoco.viewer.launch_passive(self.sim.m, self.sim.d)
        self.running = True
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()
        self.get_logger().info(f"MuJoCo {model}: {len(self.sim.joints)} actuated joints, dt {self.sim.dt} s")

    def on_cmd(self, msg: JointState):
        with self.lock:
            self.sim.set_targets(dict(zip(msg.name, msg.position)))

    def on_reset(self, req, res):
        with self.lock:
            self.sim.reset()
        res.success, res.message = True, "reset to the stand pose"
        return res

    def loop(self):
        n = max(1, int(round(1.0 / (self.get_parameter("publish_rate_hz").value * self.sim.dt))))
        rtf = self.get_parameter("real_time_factor").value
        wall0, sim0 = time.perf_counter(), self.sim.d.time
        while self.running and rclpy.ok():
            with self.lock:
                self.sim.step(n)
                self.publish()
            if self.viewer is not None:
                self.viewer.sync()
            if rtf > 0:
                ahead = (self.sim.d.time - sim0) / rtf - (time.perf_counter() - wall0)
                if ahead > 0:
                    time.sleep(ahead)

    def publish(self):
        t = stamp(self.sim.d.time)
        self.pub_clock.publish(Clock(clock=t))
        names, q, dq, tau = self.sim.joint_state()
        js = JointState()
        js.header.stamp = t
        js.name, js.position, js.velocity, js.effort = names, q.tolist(), dq.tolist(), tau.tolist()
        self.pub_js.publish(js)
        quat, gyro, acc = self.sim.imu()
        imu = Imu()
        imu.header.stamp, imu.header.frame_id = t, "imu_link"
        imu.orientation.w, imu.orientation.x, imu.orientation.y, imu.orientation.z = map(float, quat)
        imu.angular_velocity.x, imu.angular_velocity.y, imu.angular_velocity.z = map(float, gyro)
        imu.linear_acceleration.x, imu.linear_acceleration.y, imu.linear_acceleration.z = map(float, acc)
        self.pub_imu.publish(imu)
        p, qb, v, w = self.sim.base()
        od = Odometry()
        od.header.stamp, od.header.frame_id, od.child_frame_id = t, "odom", "pelvis"
        od.pose.pose.position.x, od.pose.pose.position.y, od.pose.pose.position.z = map(float, p)
        od.pose.pose.orientation.w, od.pose.pose.orientation.x, od.pose.pose.orientation.y, od.pose.pose.orientation.z = map(float, qb)
        od.twist.twist.linear.x, od.twist.twist.linear.y, od.twist.twist.linear.z = map(float, v)
        od.twist.twist.angular.x, od.twist.twist.angular.y, od.twist.twist.angular.z = map(float, w)
        self.pub_odom.publish(od)
        tf = TransformStamped()
        tf.header.stamp, tf.header.frame_id, tf.child_frame_id = t, "odom", "pelvis"
        tf.transform.translation.x, tf.transform.translation.y, tf.transform.translation.z = map(float, p)
        tf.transform.rotation = od.pose.pose.orientation
        self.tf.sendTransform(tf)

    def destroy_node(self):
        self.running = False
        if self.viewer is not None:
            self.viewer.close()
        super().destroy_node()


def main():
    rclpy.init()
    node = MujocoNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
