"""JX0 mechanical verification on the exact CAD geometry (geometry.py built with manifold3d, the same solids SolidWorks
builds), no SolidWorks needed:

1. static interference: every pair of the 39 components (22 printed parts + 17 STS3215) at the zero pose and in the
   walking stance, as an intersection volume;
2. motion interference: the robot posed at every 0.1 s of all 14 verified gaits (legs + arm swing, as exported to the
   robot) and through every action (wave, nod, look), checking every pair of components on different links;
3. joint range sweep: each joint driven through its configured limits (config.yaml) from the walking stance, 2° steps,
   reporting where it first touches something.

Volumes above 1 mm³ count as a clash (touching faces, e.g. a horn on its bracket, give ~0).

    python jx0/verify/verify_cad.py      -> jx0/results/verify_cad.json
"""
from __future__ import annotations

import itertools
import json
import math
import sys
import time
from pathlib import Path

import mujoco
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "jx0" / "cad"))
sys.path.insert(0, str(ROOT / "jx0" / "sim"))
import geometry as G  # noqa: E402
from layout import components, link_of  # noqa: E402
from preview import build as build_solid  # noqa: E402
from jx0_model import build as build_model  # noqa: E402
from jx1calc.design import Design  # noqa: E402

OUT = ROOT / "jx0" / "results" / "verify_cad.json"
GAITS = ROOT / "jx0" / "software" / "jx0bot" / "gaits"
CONFIG = ROOT / "jx0" / "software" / "jx0bot" / "config.yaml"
CLASH_MM3 = 1.0


class Robot:
    """Component solids placed on the MuJoCo links; pose(q) moves them with the joints."""

    def __init__(self):
        catalogue = {**G.PARTS, **G.SERVOS}
        solids = {name: build_solid(prims) for name, (prims, _, _) in catalogue.items()}
        self.m = mujoco.MjModel.from_xml_string(build_model(Design(ROOT / "jx0" / "design_point.yaml")))
        self.d = mujoco.MjData(self.m)
        self.items = []                                     # (key, link body id, local 4x4 in mm, solid)
        for key, part, M in components():
            link, origin = link_of(key)
            local = np.eye(4)
            local[:3, :3] = M[:3, :3]
            local[:3, 3] = M[:3, 3] * 1000 - origin
            self.items.append((key, mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_BODY, link), local, solids[part]))
        self.jadr = {mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_JOINT, j): self.m.jnt_qposadr[j]
                     for j in range(self.m.njnt) if self.m.jnt_type[j] != mujoco.mjtJoint.mjJNT_FREE}

    def pose(self, q: dict):
        self.d.qpos[:] = 0
        self.d.qpos[3] = 1.0
        for n, v in q.items():
            if n in self.jadr:
                self.d.qpos[self.jadr[n]] = v
        mujoco.mj_kinematics(self.m, self.d)
        placed = []
        for key, body, local, solid in self.items:
            W = np.eye(4)
            W[:3, :3] = self.d.xmat[body].reshape(3, 3)
            W[:3, 3] = self.d.xpos[body] * 1000
            T = W @ local
            s = solid.transform(T[:3, :].tolist())
            lo, hi = s.bounding_box()[:3], s.bounding_box()[3:]
            placed.append((key, body, s, np.array(lo), np.array(hi)))
        return placed

    @staticmethod
    def clashes(placed, cross_link_only=True, skip=()):
        out = []
        for (ka, ba, sa, loa, hia), (kb, bb, sb, lob, hib) in itertools.combinations(placed, 2):
            if cross_link_only and ba == bb:
                continue
            if (ka, kb) in skip or (kb, ka) in skip:
                continue
            if np.any(hia < lob) or np.any(hib < loa):          # bounding boxes apart
                continue
            v = (sa ^ sb).volume()
            if v > CLASH_MM3:
                out.append((ka, kb, round(v, 1)))
        return out


def gait_frames(step=5):
    for p in sorted(GAITS.glob("*.json")):
        g = json.loads(p.read_text(encoding="utf-8"))
        for i in range(0, len(g["q"]), step):
            yield p.stem, i * g["dt"], dict(zip(g["joints"], g["q"][i]))


def main():
    t0 = time.time()
    rb = Robot()
    stand = dict(next(gait_frames())[2])
    result = {"clash_threshold_mm3": CLASH_MM3}

    # 1. static: every pair, zero pose and stance
    for name, q in (("zero_pose", {}), ("walking_stance", stand)):
        c = rb.clashes(rb.pose(q), cross_link_only=False)
        result[f"static_{name}"] = {"pairs_checked": math.comb(len(rb.items), 2), "clashes": c}
        print(f"static {name:15s}: {len(c)} clashes {c[:6]}", flush=True)

    # 2. motion: all gait frames + actions
    actions = []
    for s, sg in (("l", 1), ("r", -1)):
        for sp, el in ((-150, -30), (-150, 10), (-150, -50)):          # wave
            actions.append((f"wave_{s}", {**stand, f"{s}_shoulder_pitch": math.radians(sp), f"{s}_elbow": math.radians(el)}))
    for ny in (-45, -30, 30, 45):                                          # look / shake
        actions.append((f"neck_{ny}", {**stand, "neck_yaw": math.radians(ny)}))
    bow = {**stand, "l_hip_pitch": stand["l_hip_pitch"] - math.radians(8), "r_hip_pitch": stand["r_hip_pitch"] - math.radians(8)}
    actions.append(("nod_yes_bow", bow))
    frames = [(f"{g}@{t:.1f}s", q) for g, t, q in gait_frames()] + actions
    motion = []
    for tag, q in frames:
        for a, b, v in rb.clashes(rb.pose(q)):
            motion.append({"pose": tag, "a": a, "b": b, "mm3": v})
    result["motion"] = {"poses_checked": len(frames), "clashes": motion}
    print(f"motion: {len(frames)} poses, {len(motion)} clashes", flush=True)
    for c in motion[:12]:
        print("   ", c)

    # 3. joint range sweeps from the stance: the collision-free interval around the stance angle, split into contacts
    # inside the same limb (a real range limit: config.yaml must stay inside it) and contacts with the other leg
    # (depend on where that leg is: covered by the motion check above)
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    limits = {**cfg["leg_servos"], **cfg["arm_servos"]}
    used = {}
    for g, t, q in gait_frames(step=1):
        for n, v in q.items():
            lo_u, hi_u = used.get(n, (v, v))
            used[n] = (min(lo_u, v), max(hi_u, v))
    sweeps = {}

    def side(k):
        return k[-1] if k[-2:] in ("_L", "_R") else None
    for joint, s_ in limits.items():
        lo, hi = s_["limits_deg"]
        q0 = math.degrees(stand.get(joint, 0.0))
        angles = [float(a) for a in np.arange(lo, hi + 0.01, 2.0)]
        own = {}
        other = {}
        for deg in angles:
            for a, b, v in rb.clashes(rb.pose({**stand, joint: math.radians(deg)})):
                (other if side(a) and side(b) and side(a) != side(b) else own).setdefault(deg, (a, b, v))
        i = min(range(len(angles)), key=lambda k: abs(angles[k] - q0))
        a_lo = a_hi = i
        while a_lo > 0 and angles[a_lo - 1] not in own:
            a_lo -= 1
        while a_hi < len(angles) - 1 and angles[a_hi + 1] not in own:
            a_hi += 1
        clear = [angles[a_lo], angles[a_hi]]
        u = [round(math.degrees(x), 1) for x in used.get(joint, (stand.get(joint, 0.0),) * 2)]
        sweeps[joint] = {"limits_deg": [lo, hi], "stance_deg": round(q0, 1), "own_limb_clear_deg": clear,
                         "gaits_use_deg": u, "own_limb_contacts": {str(k): v for k, v in sorted(own.items())},
                         "other_leg_contacts_from_stance": {str(k): v for k, v in sorted(other.items())},
                         "ok": clear[0] <= lo and clear[1] >= hi}
        print(f"sweep {joint:17s} limits {lo:5.0f}..{hi:4.0f}  own-limb clear {clear[0]:6.1f}..{clear[1]:6.1f}  gaits use {u[0]:6.1f}..{u[1]:6.1f}"
              f"  other-leg contact at {sorted(other)[:1] + sorted(other)[-1:] if other else 'none'}", flush=True)
    result["joint_sweeps"] = sweeps
    result["seconds"] = round(time.time() - t0, 1)
    result["pass"] = (not result["static_zero_pose"]["clashes"] and not result["static_walking_stance"]["clashes"]
                      and not motion and all(v["ok"] for v in sweeps.values()))
    OUT.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(f"CAD verification: {'PASS' if result['pass'] else 'FAIL'} ({result['seconds']} s) -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
