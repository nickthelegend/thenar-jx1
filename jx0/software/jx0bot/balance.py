"""JX0 balance controller, shared by the robot (robot.py), the gait checks (jx0/sim/walk_jx0.py) and the robustness
tests (jx0/verify/robustness.py), so what is verified is exactly what runs.

Runs once per 50 Hz frame on top of a verified gait trajectory, from the IMU's pelvis roll/pitch and their rates:
- stance leg(s): ankle and hip corrections against the tilt (the ankle strategy and hip strategy);
- swing leg: a stepping reflex. The swing foot is moved toward the side the body is falling to (hip roll / hip pitch
  offset, the ankle counter-rotated so the foot stays flat), the way a person catches a shove by stepping. After the
  foot lands the offset is eased back to zero.
Angles in radians, rates in rad/s. Sign conventions follow the simulation (x forward, y left, z up, right-hand rule).
"""
from __future__ import annotations

import math

# tuned by jx0/verify/robustness.py (see jx0/results/verify_robustness.json)
GAINS = {"ka": 0.6, "da": 0.05, "kh": 0.3,          # stance: ankle P, ankle D, hip P
         "sr": 0.0, "srd": 0.0,                     # swing: hip-roll step per rad of roll, per rad/s of roll rate
         "sp": 0.0, "spd": 0.0,                     # swing: hip-pitch step per rad of pitch, per rad/s of pitch rate
         "limit": 0.30, "decay_s": 0.4,             # max step offset (rad), time to ease it out after landing
         "lead_s": 0.0}                             # predict the tilt this far ahead (tilt + rate x lead): cancels latency


class Balance:
    def __init__(self, gains: dict | None = None, dt: float = 0.02):
        self.g = {**GAINS, **(gains or {})}
        self.dt = dt
        self.off = {"l": [0.0, 0.0], "r": [0.0, 0.0]}      # per leg: hip roll, hip pitch step offsets

    def update(self, roll, pitch, wx, wy, stance) -> dict:
        g, corr = self.g, {}
        roll, pitch = roll + g["lead_s"] * wx, pitch + g["lead_s"] * wy
        single = stance[0] != stance[1]
        for s, on in (("l", stance[0]), ("r", stance[1])):
            off = self.off[s]
            if on:
                corr[f"{s}_ankle_pitch"] = g["ka"] * pitch + g["da"] * wy
                corr[f"{s}_ankle_roll"] = g["ka"] * roll + g["da"] * wx
                corr[f"{s}_hip_pitch"] = g["kh"] * pitch
                corr[f"{s}_hip_roll"] = g["kh"] * roll
                k = math.exp(-self.dt / max(1e-3, g["decay_s"]))        # ease the landed step back to the plan
                off[0] *= k
                off[1] *= k
            elif single:
                lim = g["limit"]
                off[0] = max(-lim, min(lim, g["sr"] * roll + g["srd"] * wx))
                off[1] = max(-lim, min(lim, g["sp"] * pitch + g["spd"] * wy))
            dr, dp = off
            if dr or dp:                                                   # foot kept parallel to the ground
                corr[f"{s}_hip_roll"] = corr.get(f"{s}_hip_roll", 0.0) + dr
                corr[f"{s}_ankle_roll"] = corr.get(f"{s}_ankle_roll", 0.0) - dr
                corr[f"{s}_hip_pitch"] = corr.get(f"{s}_hip_pitch", 0.0) + dp
                corr[f"{s}_ankle_pitch"] = corr.get(f"{s}_ankle_pitch", 0.0) - dp
        return corr
