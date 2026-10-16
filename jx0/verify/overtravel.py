"""What a joint hits first when it goes PAST its configured limit (a bad command, a glitch at power-up, a fall): each
joint of the left leg, the left arm and the neck (the right side mirrors them), driven from the walking stance beyond
each end of config.yaml's limits in 2 deg steps, up to 90 deg past the limit, reporting the first contact inside the
same limb and its parts. This is where integrated joint stops would go.

    python jx0/verify/overtravel.py      -> jx0/results/overtravel.json
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_cad as V  # noqa: E402

OUT = V.ROOT / "jx0" / "results" / "overtravel.json"
JOINTS = ["l_hip_yaw", "l_hip_roll", "l_hip_pitch", "l_knee", "l_ankle_pitch", "l_ankle_roll", "l_shoulder_pitch",
          "l_elbow", "neck_yaw"]


def side(k):
    return k[-1] if k[-2:] in ("_L", "_R") else None


def main():
    rb = V.Robot()
    stand = dict(next(V.gait_frames())[2])
    cfg = yaml.safe_load(V.CONFIG.read_text(encoding="utf-8"))
    limits = {**cfg["leg_servos"], **cfg["arm_servos"]}
    out = {}
    for joint in JOINTS:
        lo, hi = limits[joint]["limits_deg"]
        res = {}
        for end, sgn in ((lo, -1), (hi, +1)):
            first = None
            for k in range(1, 46):
                deg = end + sgn * 2.0 * k
                own = [c for c in rb.clashes(rb.pose({**stand, joint: math.radians(deg)}))
                       if not (side(c[0]) and side(c[1]) and side(c[0]) != side(c[1]))]
                if own:
                    first = dict(deg=deg, past_limit_deg=2.0 * k, contacts=own[:4])
                    break
            res["low" if sgn < 0 else "high"] = first
            what = ("clear to 90 deg past" if not first else
                    f"first contact at {first['deg']:.0f} deg ({first['past_limit_deg']:.0f} past): {first['contacts'][:2]}")
            print(f"{joint:17s} {'below' if sgn < 0 else 'above'} {end:5.0f}: {what}", flush=True)
        out[joint] = dict(limits_deg=[lo, hi], **res)
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
