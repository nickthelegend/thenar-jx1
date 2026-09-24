"""Latency sensitivity of an exported policy on the CAD model: velocity tracking with added sensing / actuation delay.

The robot chain adds delay the plain simulation does not have (IMU and joint feedback age, ROS hops, USB, CAN). The
hardware-in-the-loop run showed its effect first (turn tracking 62 % through the hub twin vs 85 % in MuJoCo), and
rl/sim2sim.py CadSim(obs_delay_s, act_delay_s) reproduces it. Scenarios: turn 0.3 rad/s and forward 0.3 m/s for 8 s at
each (sensing, actuation) delay. Writes <policy>/latency.json.
Usage: rl/.venv/Scripts/python rl/latency_test.py [--policy rl/policies/jx1_walk]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jx1_rl import DEFAULT_POLICY, RL_DIR  # noqa: E402
from sim2sim import CadSim  # noqa: E402

DELAYS_MS = [(0, 0), (10, 0), (20, 0), (0, 10), (10, 10), (20, 10), (30, 10), (40, 20)]
SCENARIOS = [("turn_0.3", (0.0, 0.0, 0.3), 2), ("forward_0.3", (0.3, 0.0, 0.0), 0)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default=str(DEFAULT_POLICY))
    a = ap.parse_args()
    policy = Path(a.policy)
    rows = []
    for obs_ms, act_ms in DELAYS_MS:
        sim = CadSim(policy, obs_delay_s=obs_ms / 1000, act_delay_s=act_ms / 1000)
        row = {"obs_delay_ms": obs_ms, "act_delay_ms": act_ms}
        for name, cmd, axis in SCENARIOS:
            r = sim.rollout(cmd, 8.0)
            row[name] = {"fell": r["fell"], "achieved": r["mean_velocity_b"][axis], "fraction": round(r["mean_velocity_b"][axis] / cmd[axis], 3)}
        rows.append(row)
        cells = [f"{n} FELL" if row[n]["fell"] else f"{n} {row[n]['fraction']:.0%}" for n, _, _ in SCENARIOS]
        print(f"sensing {obs_ms:3d} ms  actuation {act_ms:3d} ms  " + "  ".join(cells), flush=True)
    (policy / "latency.json").write_text(json.dumps({"policy": policy.name, "rows": rows}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
