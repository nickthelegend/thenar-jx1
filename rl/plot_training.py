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

        def smooth(axis, ys, **kw):
            # episode statistics are per iteration: between the synchronised 20 s time-outs only the (short) falls end,
            # so the raw series spikes; draw it faint and a 50-iteration rolling mean on top
            x, y = clean(ys)
            if not x:
                return
            line, = axis.plot(x, y, lw=0.5, alpha=0.25, **{k: v for k, v in kw.items() if k != "label"})
            w = 50
            ym = [sum(y[max(0, i - w + 1):i + 1]) / len(y[max(0, i - w + 1):i + 1]) for i in range(len(y))]
            axis.plot(x, ym, lw=1.4, color=line.get_color(), **kw)
        if "ep_length_s" in d:
            smooth(ax[1], d["ep_length_s"], label=run.name)
        if "ep_tracking_lin_vel" in d:
            smooth(ax[2], d["ep_tracking_lin_vel"], label=f"{run.name} lin")
            smooth(ax[2], d["ep_tracking_ang_vel"], ls="--", label=f"{run.name} yaw")
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
