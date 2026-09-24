"""Learning curves of a training run (rl/runs/<run>/metrics.csv, optionally several runs chained) -> PNG.

Usage: rl/.venv/Scripts/python rl/plot_training.py --runs rl/runs/a rl/runs/b --out rl/policies/jx1_walk_flat/training.png
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


def load(run: Path):
    rows = list(csv.DictReader(open(run / "metrics.csv", encoding="utf-8")))

    def col(k):
        return [float(r[k]) if r.get(k) not in (None, "") else float("nan") for r in rows]
    d = {k: col(k) for k in ("iteration", "reward_per_step", "ep_length_s", "ep_tracking_lin_vel", "ep_tracking_ang_vel", "std")
         if k in rows[0]}
    if "ep_length_s" not in d and (run / "train.log").exists():
        # runs started before the CSV carried episode columns: take them from the console log (every 10 iterations)
        pat = re.compile(r"it\s+(\d+) \|.*?ep len\s+([\d.]+) s \| track v ([\d.]+) w ([\d.]+)")
        ep = {int(m.group(1)): tuple(map(float, m.groups()[1:])) for m in map(pat.match, open(run / "train.log", encoding="utf-8",
                                                                                             errors="ignore")) if m}
        ep = {k: v for k, v in ep.items() if v[0] > 0.0}          # "ep len 0.0" = no episode ended in that iteration
        nan = (float("nan"),) * 3
        d["ep_length_s"], d["ep_tracking_lin_vel"], d["ep_tracking_ang_vel"] = (list(x) for x in zip(*[ep.get(int(i), nan) for i in d["iteration"]]))
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    fig, ax = plt.subplots(1, 3, figsize=(14, 3.8))
    offset = 0
    for run in map(Path, a.runs):
        d = load(run)
        it = [i + offset for i in range(len(d["iteration"]))]
        ax[0].plot(it, d["reward_per_step"], lw=0.8, label=run.name)
        def clean(ys):
            pts = [(x, y) for x, y in zip(it, ys) if y == y]
            return ([p[0] for p in pts], [p[1] for p in pts]) if pts else ([], [])
        if "ep_length_s" in d:
            ax[1].plot(*clean(d["ep_length_s"]), lw=0.8, label=run.name)
        if "ep_tracking_lin_vel" in d:
            ax[2].plot(*clean(d["ep_tracking_lin_vel"]), lw=0.8, label=f"{run.name} lin")
            ax[2].plot(*clean(d["ep_tracking_ang_vel"]), lw=0.8, ls="--", label=f"{run.name} yaw")
        offset += len(it)
    for x, t in zip(ax, ("mean reward per policy step", "episode length at reset (s)", "velocity tracking reward (per s, max 1.0 / 0.5)")):
        x.set_title(t, fontsize=10)
        x.set_xlabel("PPO iteration")
        x.grid(alpha=0.3)
        x.legend(fontsize=7)
    fig.tight_layout()
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(a.out, dpi=120)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
