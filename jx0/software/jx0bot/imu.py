"""MPU6050 IMU on the Pi's I2C bus: pelvis roll/pitch (complementary filter) and body rates for the balance loop.

Registers from the InvenSense MPU-6000/6050 register map: PWR_MGMT_1 0x6B, CONFIG 0x1A (DLPF), GYRO_CONFIG 0x1B,
ACCEL_CONFIG 0x1C, ACCEL_XOUT_H 0x3B (14 bytes: accel xyz, temperature, gyro xyz, big-endian signed).
Axes: the sensor is mounted so x points forward, y left, z up (`mount` in config.yaml rotates otherwise).
"""
from __future__ import annotations

import math
import time

import numpy as np

ACC_SCALE = 16384.0        # LSB/g at +-2 g
GYRO_SCALE = 65.5          # LSB/(deg/s) at +-500 deg/s


class MPU6050:
    def __init__(self, bus: int = 1, address: int = 0x68, mount=None, alpha: float = 0.98):
        from smbus2 import SMBus
        self.bus, self.addr, self.alpha = SMBus(bus), address, alpha
        self.R = np.eye(3) if mount in (None, "identity") else np.asarray(mount, float)
        self.bus.write_byte_data(self.addr, 0x6B, 0x00)      # wake up, internal clock
        self.bus.write_byte_data(self.addr, 0x1A, 0x03)      # DLPF ~44 Hz
        self.bus.write_byte_data(self.addr, 0x1B, 0x08)      # gyro +-500 deg/s
        self.bus.write_byte_data(self.addr, 0x1C, 0x00)      # accel +-2 g
        time.sleep(0.05)
        self.bias = np.zeros(3)
        self.roll = self.pitch = self.yaw = 0.0
        self.rate = np.zeros(3)
        self.t = time.time()

    def _raw(self):
        d = self.bus.read_i2c_block_data(self.addr, 0x3B, 14)
        v = [int.from_bytes(bytes(d[i:i + 2]), "big", signed=True) for i in range(0, 14, 2)]
        acc = self.R @ (np.array(v[0:3]) / ACC_SCALE)                  # g
        gyro = self.R @ np.radians(np.array(v[4:7]) / GYRO_SCALE)      # rad/s
        return acc, gyro

    def calibrate(self, seconds: float = 2.0):
        """Gyro bias with the robot standing still; also initialises roll/pitch from gravity."""
        samples, t0 = [], time.time()
        while time.time() - t0 < seconds:
            samples.append(self._raw()[1])
            time.sleep(0.005)
        self.bias = np.mean(samples, axis=0)
        acc, _ = self._raw()
        self.roll, self.pitch = self._tilt(acc)
        self.t = time.time()

    @staticmethod
    def _tilt(acc):
        ax, ay, az = acc
        return math.atan2(ay, az), math.atan2(-ax, math.hypot(ay, az))

    def update(self):
        """Returns (roll, pitch, yaw, rates[3]) in rad and rad/s."""
        acc, gyro = self._raw()
        gyro = gyro - self.bias
        now = time.time()
        dt = min(0.05, now - self.t)
        self.t = now
        ar, ap = self._tilt(acc)
        a = self.alpha if 0.7 < np.linalg.norm(acc) < 1.3 else 1.0     # ignore the accelerometer during impacts
        self.roll = a * (self.roll + gyro[0] * dt) + (1 - a) * ar
        self.pitch = a * (self.pitch + gyro[1] * dt) + (1 - a) * ap
        self.yaw += gyro[2] * dt
        self.rate = gyro
        return self.roll, self.pitch, self.yaw, gyro
