"""BNO085 pelvis IMU -> /jx1/imu (sensor_msgs/Imu) on the Jetson - UNVERIFIED: written against the Adafruit
CircuitPython BNO08x driver API, not run on hardware.

The policy needs orientation (only its gravity direction is used, so the game rotation vector with free yaw is enough)
and body angular velocity, in the pelvis frame. `mount_rpy_deg` rotates the chip axes into the pelvis frame (x forward,
y left, z up); default = chip mounted flat with its x axis forward. 200 Hz.
Install on the Jetson: pip install adafruit-circuitpython-bno08x adafruit-blinka  (I2C bus 7 on the 40-pin header).
"""
from __future__ import annotations

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu

from .rotations import matrix_to_quat, quat_to_matrix, rpy_matrix


class ImuNode(Node):
    def __init__(self):
        super().__init__("jx1_imu")
        self.declare_parameter("i2c_address", 0x4A)
        self.declare_parameter("rate_hz", 200.0)
        self.declare_parameter("mount_rpy_deg", [0.0, 0.0, 0.0])
        import board
        import busio
        from adafruit_bno08x import BNO_REPORT_ACCELEROMETER, BNO_REPORT_GAME_ROTATION_VECTOR, BNO_REPORT_GYROSCOPE
        from adafruit_bno08x.i2c import BNO08X_I2C
        i2c = busio.I2C(board.SCL, board.SDA, frequency=400_000)
        self.bno = BNO08X_I2C(i2c, address=self.get_parameter("i2c_address").value)
        for report in (BNO_REPORT_GAME_ROTATION_VECTOR, BNO_REPORT_GYROSCOPE, BNO_REPORT_ACCELEROMETER):
            self.bno.enable_feature(report)
        self.R_mount = rpy_matrix(*np.radians(self.get_parameter("mount_rpy_deg").value))      # chip -> pelvis
        self.pub = self.create_publisher(Imu, "/jx1/imu", 10)
        self.create_timer(1.0 / self.get_parameter("rate_hz").value, self.tick)

    def tick(self):
        qi, qj, qk, qr = self.bno.game_quaternion                  # world <- chip
        R = quat_to_matrix(qr, qi, qj, qk) @ self.R_mount.T         # world <- pelvis
        w, x, y, z = matrix_to_quat(R)
        gyro = self.R_mount @ np.array(self.bno.gyro)               # rad/s in the pelvis frame
        acc = self.R_mount @ np.array(self.bno.acceleration)
        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "imu_link"
        msg.orientation.w, msg.orientation.x, msg.orientation.y, msg.orientation.z = w, x, y, z
        msg.angular_velocity.x, msg.angular_velocity.y, msg.angular_velocity.z = map(float, gyro)
        msg.linear_acceleration.x, msg.linear_acceleration.y, msg.linear_acceleration.z = map(float, acc)
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = ImuNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == "__main__":
    main()
