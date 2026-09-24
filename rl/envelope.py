"""Command envelope of an exported policy on the full CAD model: which (vx, vy, wz) commands it tracks without falling.

Two slices of constant-command walks (rl/sim2sim.py CadSim: mesh-hull collisions, 500 Hz, hub ramp), each command held
for --duration seconds with tracking measured after 2 s:
  vx x wz (vy = 0) and vx x vy (wz = 0), from inside the training ranges to beyond them.
A command counts as tracked when the robot stays up and each mean velocity is within max(0.1, 20 %) of the command
(0.15 rad/s for wz). Outputs <policy>/envelope.json and <policy>/envelope.png.

Usage: rl/.venv/Scripts/python rl/envelope.py [--policy rl/policies/jx1_walk_flat] [--workers 4] [--duration 6]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jx1_rl import RL_DIR  # noqa: E402

VX = [-0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2]
WZ = [-0.9, -0.6, -0.3, 0.0, 0.3, 0.6, 0.9]
VY = [-0.45, -0.3, -0.15, 0.0, 0.15, 0.3, 0.45]
_SIM = None


def _init(policy_dir, terrain):
    global _SIM
    from sim2sim import CadSim
    _SIM = CadSim(Path(policy_dir), terrain)


def _walk(args):
    cmd, T = args
    r = _SIM.rollout(cmd, T)
    return cmd, r


def tracked(cmd, r):
    if r["fell"]:
        return False
    v = np.array(r["mean_velocity_b"])
    tol = np.array([max(0.1, 0.2 * abs(cmd[0])), max(0.1, 0.2 * abs(cmd[1])), max(0.15, 0.2 * abs(cmd[2]))])
    return bool(np.all(np.abs(v - np.array(cmd)) <= tol))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default=str(RL_DIR / "policies" / "jx1_walk_flat"))
    ap.add_argument("--terrain", default=None)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--duration", type=float, default=6.0)
    a = ap.parse_args()
    policy = Path(a.policy)
    cmds = sorted({(vx, 0.0, wz) for vx in VX for wz in WZ} | {(vx, vy, 0.0) for vx in VX for vy in VY})
    t0 = time.time()
    with Pool(a.workers, initializer=_init, initargs=(str(policy), a.terrain)) as pool:
        out = dict(pool.map(_walk, [(c, a.duration) for c in cmds], chunksize=1))
    res = {f"{c[0]:+.2f},{c[1]:+.2f},{c[2]:+.2f}": {**r, "tracked": tracked(c, r)} for c, r in out.items()}

    def best(axis, sign, fixed):
        """Largest tracked pure command along one axis: the command, the achieved mean velocity and the torque margin."""
        ok = [c for c, r in out.items() if tracked(c, r) and all(c[i] == 0.0 for i in fixed) and np.sign(c[axis]) == sign]
        if not ok:
            return None
        c = max(ok, key=lambda c: abs(c[axis]))
        return {"command": c[axis], "achieved": out[c]["mean_velocity_b"][axis], "peak_torque_fraction": out[c]["peak_torque_fraction"]}

    summary = {"forward": best(0, 1, (1, 2)), "backward": best(0, -1, (1, 2)), "left": best(1, 1, (0, 2)), "right": best(1, -1, (0, 2)),
               "yaw_left": best(2, 1, (0, 1)), "yaw_right": best(2, -1, (0, 1)),
               "tracked": sum(r["tracked"] for r in res.values()), "commands": len(res),
               "falls": sum(r["fell"] for r in res.values())}
    io_trained = __import__("yaml").safe_load((policy / "policy_io.yaml").read_text(encoding="utf-8"))["commands"]
    doc = {"policy": policy.as_posix(), "terrain": a.terrain or "flat", "duration_s": a.duration, "settle_s": 2.0,
           "criterion": "upright and |mean v - cmd| <= max(0.1, 20%) per axis (wz: max(0.15, 20%))", "training_ranges": io_trained,
           "summary": summary, "results": res, "wall_time_s": round(time.time() - t0, 1)}
    tag = "" if not a.terrain else "_" + Path(a.terrain).stem.replace("jx1_walk_", "")
    (policy / f"envelope{tag}.json").write_text(json.dumps(doc, indent=1), encoding="utf-8")
    plot(out, policy / f"envelope{tag}.png", io_trained, summary)
    print(json.dumps(summary), f"({doc['wall_time_s']} s)")


def plot(out, path, ranges, summary):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for ax, (ylabel, ys, axis, key) in zip(axes, [("wz command (rad/s)", WZ, 2, "ang_vel_yaw"), ("vy command (m/s)", VY, 1, "lin_vel_y")]):
        err = np.full((len(ys), len(VX)), np.nan)
        for i, y in enumerate(ys):
            for j, vx in enumerate(VX):
                c = (vx, 0.0, y) if axis == 2 else (vx, y, 0.0)
                r = out[c]
                if not r["fell"]:
                    v = np.array(r["mean_velocity_b"])
                    err[i, j] = float(np.linalg.norm((v - np.array(c))[[0, axis]]))
        def edges(v):
            v = np.asarray(v, dtype=float)
            mid = (v[1:] + v[:-1]) / 2
            return np.concatenate([[v[0] - (mid[0] - v[0])], mid, [v[-1] + (v[-1] - mid[-1])]])

        im = ax.pcolormesh(edges(VX), edges(ys), err, cmap="viridis_r", vmin=0, vmax=0.4)
        for i, y in enumerate(ys):
            for j, vx in enumerate(VX):
                c = (vx, 0.0, y) if axis == 2 else (vx, y, 0.0)
                ax.text(vx, y, "X" if out[c]["fell"] else ("" if tracked(c, out[c]) else "~"), ha="center", va="center",
                        color="red" if out[c]["fell"] else "black", fontsize=12, fontweight="bold")
        rx, ry = ranges["lin_vel_x"], ranges[key]
        ax.add_patch(plt.Rectangle((rx[0], ry[0]), rx[1] - rx[0], ry[1] - ry[0], fill=False, ec="white", ls="--", lw=1.5))
        ax.set_xlabel("vx command (m/s)")
        ax.set_ylabel(ylabel)
        fig.colorbar(im, ax=ax, label="tracking error |v - cmd| (X = fell, ~ = outside tolerance)")
    def fmt(key, unit):
        s = summary[key]
        return f"{key} {s['achieved']:+.2f} {unit}" if s else f"{key} -"

    fig.suptitle("Command envelope on the CAD model (dashed: training ranges). Best tracked: " +
                 ", ".join([fmt("forward", "m/s"), fmt("backward", "m/s"), fmt("left", "m/s"), fmt("right", "m/s"),
                            fmt("yaw_left", "rad/s"), fmt("yaw_right", "rad/s")]), fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=110)


if __name__ == "__main__":
    main()
