"""JX0 bring-up for the 17 STS3215 servos (legs, arms, neck): IDs, zero pose, joint directions, and a stiffness check.
Run on the Pi with the legs hanging free (robot on a stand) and 12 V on the servo driver (3S battery or a bench supply).

    python -m jx0bot.calibrate scan                      # which IDs answer, with voltage and temperature
    python -m jx0bot.calibrate set-id 1 7                # ONE servo on the bus: change its ID from 1 to 7
    python -m jx0bot.calibrate center                    # all 17 servos to mid-travel, BEFORE fitting horns and links
    python -m jx0bot.calibrate zero                      # torque off, pose the robot in the zero pose, press Enter
    python -m jx0bot.calibrate directions                # moves each joint +10 deg; you answer y/n
    python -m jx0bot.calibrate stiffness l_knee          # holds a joint; push on it and read the stiffness

zero and directions write their results into config.yaml (the rest of the file, comments included, is kept).
"""
from __future__ import annotations

import argparse
import math
import re
import time

from .robot import HERE, load_config
from .servo_bus import TICKS_PER_REV, ServoBus

CONFIG = HERE / "config.yaml"

# What +10 deg looks like for each joint (the simulation's sign convention: x forward, y left, z up)
POSITIVE = {
    "hip_yaw": "toes turn to the robot's LEFT",
    "hip_roll": "the leg swings toward the robot's LEFT",
    "hip_pitch": "the leg swings BACKWARD",
    "knee": "the knee BENDS (shin swings backward)",
    "ankle_pitch": "the toes point DOWN",
    "ankle_roll": "the foot's LEFT edge goes UP",
    "shoulder_pitch": "the arm swings BACKWARD",
    "elbow": "the blade swings BACKWARD",
    "yaw": "the head turns to the robot's LEFT",
}

ZERO_POSE = """Zero pose (all joint angles 0): legs straight down and parallel, feet flat and pointing forward, soles level
with each other, hip-yaw and hip-roll brackets square to the pelvis, shoulder cradles and blades hanging straight down,
head facing forward. The printed parts are square at zero, so use a small set square against the pelvis, thigh and shin
plates."""


def all_servos(cfg: dict) -> dict:
    return {**cfg["leg_servos"], **cfg["arm_servos"]}


def set_field(joint: str, field: str, value) -> None:
    """Rewrite one `field: value` inside the joint's line in config.yaml, keeping everything else."""
    text = CONFIG.read_text(encoding="utf-8")
    pat = re.compile(rf"^(\s*{joint}:\s*\{{.*?\b{field}:\s*)(-?\d+)", re.M)
    text, n = pat.subn(lambda m: f"{m.group(1)}{value}", text)
    if n != 1:
        raise RuntimeError(f"could not find {joint}.{field} in {CONFIG}")
    CONFIG.write_text(text, encoding="utf-8")


def scan(bus: ServoBus, ids=range(1, 21)):
    found = []
    for i in ids:
        if bus.ping(i):
            s = bus.status(i)
            found.append(i)
            print(f"id {i:2d}: position {s['position']:5d}  {s['voltage_v']:.1f} V  {s['temperature_c']} C")
    print(f"{len(found)} servo(s) found" + ("" if found else " - check power (12 V on the driver) and the baud rate"))
    return found


def center(bus: ServoBus, cfg: dict):
    """Every servo to 2048 ticks (mid-travel), so every horn goes on near the joint's zero."""
    ids = scan(bus)
    bus.set_positions({i: 2048 for i in ids})
    for i in ids:
        bus.torque(i, True)
    input("Servos holding mid-travel. Fit the horns and links now (legs straight, cradles and blades hanging down, "
          "head forward), then press Enter to release... ")
    for i in ids:
        bus.torque(i, False)


def zero(bus: ServoBus, cfg: dict):
    servos = all_servos(cfg)
    for s in servos.values():
        bus.torque(s["id"], False)
    print(ZERO_POSE)
    input("Torque is off. Put the robot in the zero pose, hold it there, and press Enter... ")
    for name, s in servos.items():
        p = bus.position(s["id"])
        set_field(name, "zero_ticks", p)
        print(f"{name:14s} id {s['id']:2d}  zero_ticks {p}")
    print(f"written to {CONFIG}")


def directions(bus: ServoBus, cfg: dict):
    step = int(round(math.radians(10) * TICKS_PER_REV / (2 * math.pi)))
    input("Robot on a stand, legs hanging free. Press Enter to start; each joint moves 10 deg and back... ")
    for name, s in all_servos(cfg).items():
        joint = name.split("_", 1)[1]
        z = s["zero_ticks"]
        bus.set_positions({s["id"]: z})
        bus.torque(s["id"], True)
        time.sleep(0.5)
        bus.set_positions({s["id"]: z + step})
        time.sleep(0.8)
        ans = input(f"{name}: did {POSITIVE[joint]}? [y/n] ").strip().lower()
        bus.set_positions({s["id"]: z})
        time.sleep(0.5)
        bus.torque(s["id"], False)
        d = 1 if ans.startswith("y") else -1
        set_field(name, "direction", d)
        print(f"  direction {d}")
    print(f"written to {CONFIG}")


def stiffness(bus: ServoBus, cfg: dict, joint: str):
    """Hold the joint at zero and print the deflection. Hang a known weight on a known lever (e.g. 0.5 kg at 10 cm =
    0.49 N·m): the walking gaits need about 60 N·m/rad, i.e. ~0.5 deg (5-6 ticks) of sag for that load."""
    s = all_servos(cfg)[joint]
    z = s["zero_ticks"]
    bus.set_positions({s["id"]: z})
    bus.torque(s["id"], True)
    torque = float(input("Load torque you will apply, N·m (e.g. 0.49): ") or 0.49)
    input("Apply it and press Enter... ")
    samples = []
    for _ in range(20):
        samples.append(bus.position(s["id"]) - z)
        time.sleep(0.05)
    bus.torque(s["id"], False)
    ticks = abs(sum(samples) / len(samples))
    rad = ticks * 2 * math.pi / TICKS_PER_REV
    k = torque / rad if rad > 0 else float("inf")
    print(f"deflection {ticks:.1f} ticks = {math.degrees(rad):.2f} deg -> stiffness {k:.0f} N·m/rad (target ~60)")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scan")
    p = sub.add_parser("set-id")
    p.add_argument("old", type=int)
    p.add_argument("new", type=int)
    sub.add_parser("center")
    sub.add_parser("zero")
    sub.add_parser("directions")
    p = sub.add_parser("stiffness")
    p.add_argument("joint")
    a = ap.parse_args()
    cfg = load_config()
    bus = ServoBus(cfg["bus"]["port"], cfg["bus"]["baud"])
    if a.cmd == "scan":
        scan(bus)
    elif a.cmd == "set-id":
        if not bus.ping(a.old):
            raise SystemExit(f"no servo answers at id {a.old}")
        bus.change_id(a.old, a.new)
        print(f"id {a.old} -> {a.new}: " + ("ok" if bus.ping(a.new) else "no answer at the new id"))
    elif a.cmd == "center":
        center(bus, cfg)
    elif a.cmd == "zero":
        zero(bus, cfg)
    elif a.cmd == "directions":
        directions(bus, cfg)
    elif a.cmd == "stiffness":
        stiffness(bus, cfg, a.joint)


if __name__ == "__main__":
    main()
