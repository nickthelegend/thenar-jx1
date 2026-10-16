"""Drive a JX0 policy in real time in the MuJoCo viewer, on the verified model of sim2sim_jx0.py (1 kHz, STS3215
torque-speed line, 100 Hz bus, jx0bot clamps).

    rl/.venv/Scripts/python jx0/rl/play_jx0.py --policy jx0/rl/policies/<name>

Keys (click the viewer window first):  Up / Down  forward / back speed     Left / Right  turn
                                       J / L      side-step left / right   K  stop (stand)
                                       P          push it (0.48 N s from a random side)
The window title shows the command; the terminal prints the speed it reaches and how close to real time it runs.
"""
from __future__ import annotations

import argparse
import random
import sys
import time
from pathlib import Path

import mujoco
import mujoco.viewer
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sim2sim_jx0 import PUSH_DIRS, JX0Sim, Policy  # noqa: E402

KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT = 265, 264, 263, 262


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", required=True)
    ap.add_argument("--seconds", type=float, default=600.0)
    a = ap.parse_args()
    pol = Policy(Path(a.policy))
    sim = JX0Sim(pol)
    rng = pol.io["commands"]
    cmd = np.zeros(3)
    pushes = []

    def key(k):
        if k == KEY_UP:
            cmd[0] = min(cmd[0] + 0.02, rng["lin_vel_x"][1])
        elif k == KEY_DOWN:
            cmd[0] = max(cmd[0] - 0.02, rng["lin_vel_x"][0])
        elif k == KEY_LEFT:
            cmd[2] = min(cmd[2] + 0.1, rng["ang_vel_yaw"][1])
        elif k == KEY_RIGHT:
            cmd[2] = max(cmd[2] - 0.1, rng["ang_vel_yaw"][0])
        elif k == ord("J"):
            cmd[1] = min(cmd[1] + 0.02, rng["lin_vel_y"][1])
        elif k == ord("L"):
            cmd[1] = max(cmd[1] - 0.02, rng["lin_vel_y"][0])
        elif k == ord("K"):
            cmd[:] = 0.0
        elif k == ord("P"):
            pushes.append(random.choice(list(PUSH_DIRS)))
        print(f"command vx {cmd[0]:+.2f} m/s  vy {cmd[1]:+.2f} m/s  wz {cmd[2]:+.2f} rad/s", flush=True)

    dt = sim.m.opt.timestep
    view_m, view_d = sim.m, sim.d
    with mujoco.viewer.launch_passive(view_m, view_d, key_callback=key) as v:
        v.cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
        v.cam.trackbodyid = sim.pelvis
        v.cam.distance, v.cam.elevation, v.cam.azimuth = 1.0, -15.0, 140.0
        t_wall0, t_sim0 = time.perf_counter(), sim.d.time
        last_report, p_last, t_last = time.perf_counter(), sim.pose()[0], sim.d.time
        while v.is_running() and sim.d.time < a.seconds:
            if pushes:
                side = pushes.pop()
                sim.push(0.48, PUSH_DIRS[side])
                print(f"push 0.48 N s from the {side}", flush=True)
            for _ in range(16):                                              # 16 ms of physics per viewer frame
                sim.step(cmd)
            if sim.fell:                                                     # stand it up again, same window
                print("fell - restarting", flush=True)
                fresh = JX0Sim(pol)
                mujoco.mj_copyData(view_d, view_m, fresh.d)
                fresh.m, fresh.d = view_m, view_d
                sim = fresh
                t_wall0, t_sim0 = time.perf_counter(), sim.d.time
            v.sync()
            lag = (sim.d.time - t_sim0) - (time.perf_counter() - t_wall0)    # keep pace with the wall clock
            if lag > 0:
                time.sleep(lag)
            if time.perf_counter() - last_report > 2.0:
                p, h, t = sim.pose()
                speed = np.linalg.norm(p - p_last) / max(t - t_last, 1e-9)
                rtf = (sim.d.time - t_sim0) / (time.perf_counter() - t_wall0)
                print(f"t {t:6.1f} s  speed {speed:.3f} m/s  real-time factor {rtf:.2f}", flush=True)
                last_report, p_last, t_last = time.perf_counter(), p, t


if __name__ == "__main__":
    main()
