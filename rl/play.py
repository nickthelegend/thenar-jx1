"""Drive an exported policy on the full CAD model in the MuJoCo viewer with the keyboard.

  rl/.venv/Scripts/python rl/play.py [--policy rl/policies/jx1_walk] [--terrain rl/config/jx1_walk_rough.yaml]

Keys (viewer window focused):  Up / Down  vx +- 0.1 m/s    Left / Right  wz +- 0.1 rad/s    , / .  vy +- 0.05 m/s
                               Space  stop (zero command)   Backspace  reset to the stand pose
Commands are clipped to the policy's training ranges (policy_io.yaml -> commands). Same execution as rl/sim2sim.py:
50 Hz policy, CAN-hub target ramp, PD in the drives, CAD mesh-hull collisions.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import mujoco
import mujoco.viewer
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jx1_rl import RL_DIR  # noqa: E402
from sim2sim import CadSim  # noqa: E402

KEY_UP, KEY_DOWN, KEY_LEFT, KEY_RIGHT, KEY_SPACE, KEY_BACKSPACE = 265, 264, 263, 262, 32, 259


class Teleop:
    def __init__(self, ranges):
        self.cmd = np.zeros(3)
        self.lo = np.array([ranges["lin_vel_x"][0], ranges["lin_vel_y"][0], ranges["ang_vel_yaw"][0]])
        self.hi = np.array([ranges["lin_vel_x"][1], ranges["lin_vel_y"][1], ranges["ang_vel_yaw"][1]])
        self.reset_requested = False

    def key(self, keycode):
        step = {KEY_UP: (0, 0.1), KEY_DOWN: (0, -0.1), KEY_LEFT: (2, 0.1), KEY_RIGHT: (2, -0.1), ord(","): (1, 0.05), ord("."): (1, -0.05)}
        if keycode in step:
            i, dv = step[keycode]
            self.cmd[i] = float(np.clip(round(self.cmd[i] + dv, 3), self.lo[i], self.hi[i]))
        elif keycode == KEY_SPACE:
            self.cmd[:] = 0.0
        elif keycode == KEY_BACKSPACE:
            self.reset_requested = True
        print(f"command vx {self.cmd[0]:+.2f} m/s  vy {self.cmd[1]:+.2f} m/s  wz {self.cmd[2]:+.2f} rad/s", flush=True)


def run(policy: Path, terrain=None, steps=None):
    sim = CadSim(policy, terrain)
    tele = Teleop(sim.io["commands"])
    d = sim.reset()
    m, rn, dec = sim.m, sim.rn, sim.dec

    def policy_step(d):
        tgt = rn.targets(d.qpos[3:7].copy(), d.qvel[3:6].copy(), d.qpos[sim.pol_q], d.qvel[sim.pol_d], tele.cmd, d.time)
        prev = d.ctrl[sim.pol_a].copy()
        for i in range(dec):
            d.ctrl[sim.pol_a] = prev + (i + 1) / dec * (tgt - prev)
            mujoco.mj_step(m, d)

    if steps is not None:                                   # headless smoke test
        for _ in range(steps):
            policy_step(d)
        return d
    with mujoco.viewer.launch_passive(m, d, key_callback=tele.key) as viewer:
        viewer.cam.distance, viewer.cam.elevation = 2.8, -15
        while viewer.is_running():
            t0 = time.perf_counter()
            with viewer.lock():                                 # the viewer renders d from its own thread
                if tele.reset_requested:
                    tele.reset_requested = False
                    fresh = sim.reset()
                    d.qpos[:], d.qvel[:], d.ctrl[:], d.time = fresh.qpos, fresh.qvel, fresh.ctrl, 0.0
                    mujoco.mj_forward(m, d)
                policy_step(d)
                viewer.cam.lookat[:] = [d.qpos[0], d.qpos[1], 0.6]
            viewer.sync()
            time.sleep(max(0.0, sim.dt_pol - (time.perf_counter() - t0)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default=str(RL_DIR / "policies" / "jx1_walk_flat"))
    ap.add_argument("--terrain", default=None)
    ap.add_argument("--headless-steps", type=int, default=None, help="run N policy steps without a window (smoke test)")
    a = ap.parse_args()
    d = run(Path(a.policy), a.terrain, a.headless_steps)
    if a.headless_steps is not None:
        print(f"headless: {a.headless_steps} policy steps, pelvis height {d.qpos[2]:.3f} m")


if __name__ == "__main__":
    main()
