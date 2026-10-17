"""Do a trained policy's poses collide on the real parts? The MuJoCo test model (sim2sim_jx0.py) has no leg-on-leg
contact, so a policy could pass it with its feet or ankle brackets running into each other. This runs the policy on
the verified model for every speed test and the 60 s endurance sequence, records the joint angles every 0.1 s and
checks each pose with the CAD interference check (jx0/verify/verify_cad.py: the SolidWorks parts, the real servo, its
cables and every screw head).

    rl/.venv/Scripts/python jx0/rl/policy_clearance.py --policy jx0/rl/policies/<name>      -> <policy>/clearance.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "jx0" / "verify"))
import sim2sim_jx0 as T  # noqa: E402


def record(pol, cmd_seq, every_s=0.1):
    """[(tag, {short joint name: angle})] while the policy follows cmd_seq [(name, cmd, seconds)]."""
    sim = T.JX0Sim(pol)
    every = int(round(every_s / sim.m.opt.timestep))
    poses = []
    for name, cmd, seconds in cmd_seq:
        def frame(s, c, name=name):
            poses.append((f"{name}@{s.i * s.m.opt.timestep:.1f}s", {s.sj[j]: float(s.d.qpos[s.qa[j]]) for j in s.allj}))
        if not sim.run(cmd, seconds, frame=frame, frame_hz=1.0 / every_s):
            poses.append((f"{name}: FELL", None))
            break
    return poses


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", required=True)
    a = ap.parse_args()
    t0 = time.time()
    folder = Path(a.policy)
    pol = T.Policy(folder)
    import verify_cad as V
    rb = V.Robot()
    runs = {name: [(name, cmd, 10.0)] for name, cmd in T.SPEEDS}
    runs["endurance"] = [(f"endurance_{k}", cmd, 5.0) for k, cmd in enumerate(T.ENDURANCE)]
    out, n, worst = {}, 0, []
    for run, seq in runs.items():
        clashes = []
        for tag, q in record(pol, seq):
            if q is None:
                clashes.append({"pose": tag})
                continue
            n += 1
            for ka, kb, v in rb.clashes(rb.pose(q)):
                clashes.append({"pose": tag, "a": ka, "b": kb, "mm3": v})
        out[run] = clashes
        print(f"  {run:15s} {len(clashes)} clashes {clashes[:2]}", flush=True)
        worst += clashes
    res = {"policy": str(folder).replace("\\", "/"), "poses_checked": n, "clashes": out, "pass": not worst,
           "wall_s": round(time.time() - t0, 1)}
    (folder / "clearance.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"{'PASS' if not worst else 'FAIL'}: {n} poses, {len(worst)} clashes -> {folder / 'clearance.json'}")
    sys.exit(0 if not worst else 1)


if __name__ == "__main__":
    main()
