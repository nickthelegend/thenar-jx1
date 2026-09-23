"""Map the collision-free ankle pitch/roll workspace of the SolidWorks leg (open issue OI-3).

Drives the two ankle motors through the verified parallel-ankle model for a pitch x roll grid (other joints at a
walking crouch), runs SolidWorks interference detection per pose, and records which component pairs touch.
Outputs verification/ankle_workspace_<side>.json and verification/images/ankle_workspace_<side>.png.

Usage: .venv/Scripts/python tools/cad/ankle_workspace.py [--side L] [--step-pitch 5] [--step-roll 5]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cad.verify_leg_motion import Verifier, ROOT  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="JX1_LowerBody")
    ap.add_argument("--side", default="L")
    ap.add_argument("--step-pitch", type=float, default=5.0)
    ap.add_argument("--step-roll", type=float, default=5.0)
    a = ap.parse_args()
    v = Verifier(a.name)
    pitches = np.arange(-55.0, 30.0 + 1e-6, a.step_pitch)
    rolls = np.arange(-20.0, 20.0 + 1e-6, a.step_roll)
    grid, rows = np.zeros((len(pitches), len(rolls))), []
    for i, p in enumerate(pitches):
        for k, r in enumerate(rolls):
            q = {"hip_pitch": -20.0, "knee": 40.0, "ankle_pitch": float(p), "ankle_roll": float(r)}
            v.set_joints(a.side, q)
            (dp, dr, who), _, phi = v.drift(a.side, q)
            ints = [i_ for i_ in v.interferences() if not v.whitelisted(i_["components"])]
            own = [i_ for i_ in ints if all(c.startswith(a.side + "_") for c in i_["components"])]
            vol = sum(i_["volume_mm3"] for i_ in own)
            grid[i, k] = vol
            rows.append({"pitch_deg": float(p), "roll_deg": float(r), "crank_deg": [round(float(np.degrees(x)), 2) for x in phi],
                         "kinematic_error_mm": round(dp, 4), "collisions": own})
            print(f"pitch {p:6.1f} roll {r:6.1f}  crank {np.degrees(phi).round(1)}  collision {vol:8.1f} mm3 "
                  f"{[tuple(c['components']) for c in own][:2]}", flush=True)
    v.set_joints(a.side, {})
    free = [(r["pitch_deg"], r["roll_deg"]) for r in rows if not r["collisions"]]
    out = {"side": a.side, "pitch_grid_deg": pitches.tolist(), "roll_grid_deg": rolls.tolist(), "collision_volume_mm3": grid.tolist(),
           "collision_free_fraction": round(len(free) / len(rows), 3), "poses": rows,
           "note": "other joints at hip_pitch -20, knee 40 (walking crouch); rod-end/stud envelope contacts whitelisted"}
    (ROOT / "verification" / f"ankle_workspace_{a.side}.json").write_text(json.dumps(out, indent=2))
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(7, 5))
        im = ax.imshow(np.where(grid > 0, 1, 0).T, origin="lower", cmap="RdYlGn_r", vmin=0, vmax=1, aspect="auto",
                       extent=[pitches[0] - a.step_pitch / 2, pitches[-1] + a.step_pitch / 2, rolls[0] - a.step_roll / 2, rolls[-1] + a.step_roll / 2])
        ax.set_xlabel("ankle pitch [deg] (+ = plantarflexion)")
        ax.set_ylabel("ankle roll [deg]")
        ax.set_title(f"JX1 {a.side} ankle workspace — SolidWorks interference (green = free)")
        fig.tight_layout()
        fig.savefig(ROOT / "verification" / "images" / f"ankle_workspace_{a.side}.png", dpi=110)
    except Exception as e:  # pragma: no cover
        print("plot skipped", e)
    print(f"collision-free fraction {out['collision_free_fraction']}")


if __name__ == "__main__":
    main()
