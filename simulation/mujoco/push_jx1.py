"""Push-recovery test of the JX1 walking controller on the CAD-derived MuJoCo model.

Uses simulation/mujoco/walk_jx1.py unchanged (gait planned on the CAD model, PD + inverse-dynamics feedforward, ankle + hip
tilt stabiliser, fixed footsteps). A horizontal force pulse of 0.1 s hits the torso COM in mid single support of step 4; the
largest impulse (N s) the controller survives without falling until the end of the walk is found by bisection for pushes
forward, backward, left and right. There is no step adjustment, so these are conservative numbers.
Output: verification/mujoco_push.json.
Usage: .venv/Scripts/python simulation/mujoco/push_jx1.py [--gait nominal|slow|fast|turn]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import mujoco

sys.path.insert(0, str(Path(__file__).resolve().parent))
import walk_jx1 as W  # noqa: E402

DUR = 0.10                      # push duration (s)
SEARCH_MAX = 40.0               # N s
TOL = 0.5                       # N s
DIRECTIONS = {"forward": (1, 0, 0), "backward": (-1, 0, 0), "left": (0, 1, 0), "right": (0, -1, 0)}


class Pusher:
    """Wraps mujoco.mj_step so walk_jx1.run() sees an external force on the torso during the push window."""

    def __init__(self):
        self.force, self.t0, self.body = None, 0.0, None
        self._step = mujoco.mj_step
        mujoco.mj_step = self.step

    def step(self, m, d):
        if self.body is None:
            name = "torso_link" if mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "torso_link") >= 0 else "pelvis"
            self.body = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, name)
        on = self.force is not None and self.t0 <= d.time < self.t0 + DUR
        d.xfrc_applied[self.body, :3] = self.force if on else 0.0
        self._step(m, d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gait", default="nominal", choices=list(W.GAITS))
    a = ap.parse_args()
    plans = {}
    plan = W.plan
    W.plan = lambda g: plans[g] if g in plans else plans.setdefault(g, plan(g))   # plan once, reuse for every trial
    pusher = Pusher()
    g = W.GaitParams(a.gait, **W.GAITS[a.gait])
    pusher.t0 = g.t_start + 3 * g.step_time + g.step_time * g.ds_ratio + 0.5 * g.step_time * (1 - g.ds_ratio) - DUR / 2

    def fell(direction, impulse):
        pusher.force, pusher.body = [c * impulse / DUR for c in direction], None
        return W.run(a.gait, stabiliser=True, render=False)[0]["fell"]

    base = fell((1, 0, 0), 0.0)
    res = {"generated_by": "simulation/mujoco/push_jx1.py", "gait": a.gait, "push_duration_s": DUR, "push_time_s": round(pusher.t0, 3),
           "applied_to": "torso_link COM", "controller": "walk_jx1.py (fixed footsteps, ankle + hip strategy)",
           "baseline_fell": base, "max_survived_impulse_Ns": {}}
    for tag, dvec in DIRECTIONS.items():
        lo, hi = 0.0, SEARCH_MAX
        if not fell(dvec, hi):
            lo = hi
        while hi - lo > TOL:
            mid = 0.5 * (lo + hi)
            lo, hi = (lo, mid) if fell(dvec, mid) else (mid, hi)
        res["max_survived_impulse_Ns"][tag] = round(lo, 2)
        print(f"{tag:8s} survives {lo:5.2f} N s", flush=True)
    mass = float(sum(W.load().body_mass))
    res["robot_mass_kg"] = round(mass, 2)
    res["equivalent_com_velocity_change_m_s"] = {k: round(v / mass, 3) for k, v in res["max_survived_impulse_Ns"].items()}
    (W.OUT / "mujoco_push.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("min survived impulse", min(res["max_survived_impulse_Ns"].values()), "N s ->", W.OUT / "mujoco_push.json")


if __name__ == "__main__":
    main()
