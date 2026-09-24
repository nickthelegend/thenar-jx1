"""Arm range of motion against the CAD collision hulls in MuJoCo, incl. the shoulder-pitch overhead range (OI-16).

SolidWorks verified the arms only inside tools/cad/upper_kinematics.py CAD_WINDOW (shoulder pitch -115...+60 deg:
angle-mate windows must lie in 0...180 deg), so the overhead part of the joint_map range (-170...-115 deg) had no check.
Here the CAD MJCF (simulation/mujoco/jx1.xml: CoACD convex hulls, the collision model of the RL sim-to-sim) is posed
kinematically with the base fixed and every contact between two robot bodies is recorded:

  1. method check: the 13 whole-robot and 36 upper-body SolidWorks poses (verification/robot_motion_verification.json,
     upper_motion_verification.json: exact geometry) are re-posed here and the verdicts compared
  2. per arm, a grid over the whole joint_map range: shoulder pitch -170...+60 (5 deg) x shoulder roll (abduction)
     x shoulder yaw x elbow, the other arm relaxed (roll 8 deg), legs at the RL stance default, waist and neck at 0
  3. the overhead poses (pitch <= -115 deg) again with the neck turned and nodded over its range

Hulls fill concavities, so a hull contact is a candidate clash; the method check shows how conservative that is.
The model excludes adjacent body pairs (torso-shoulder links, shoulder links, upper arm-forearm), whose hulls overlap at
the joints. Results -> verification/mujoco_arm_range.json, overhead images -> verification/images/mujoco/.
Usage: .venv/Scripts/python simulation/mujoco/verify_arm_range.py [--no-render]      (about 10 s)
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import mujoco
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
XML = ROOT / "simulation" / "mujoco" / "jx1.xml"
OUT = ROOT / "verification"
IMG = OUT / "images" / "mujoco"
JM = yaml.safe_load((ROOT / "simulation" / "joint_map.yaml").read_text(encoding="utf-8"))
LIMITS = {j["name"]: (np.degrees(j["lower_rad"]), np.degrees(j["upper_rad"])) for j in JM["joints"]}
STANCE = yaml.safe_load((ROOT / "rl" / "config" / "jx1_walk.yaml").read_text(encoding="utf-8"))["default_joint_pos"]

PITCH = list(range(-170, 61, 5))
ROLL = [-10, 0, 8, 20, 45, 90, 150]          # abduction (left roll = +a, right roll = -a)
YAW = [-90, -45, 0, 45, 90]                  # left yaw = +y, right yaw = -y (mirror)
ELBOW = [-135, -90, -45, 0, 5]
OVERHEAD = [p for p in PITCH if p <= -115]
NECK_YAW, NECK_PITCH = [-80, -40, 0, 40, 80], [-30, 0, 45]
RELAXED_ROLL = 8


def load_fixed():
    xml = XML.read_text(encoding="utf-8")
    xml = xml.replace('<freejoint name="root"/>', "").replace('<body name="pelvis" pos="0 0 0.64">', '<body name="pelvis" pos="0 0 1.2">')
    return mujoco.MjModel.from_xml_string(xml.replace('meshdir="../../', f'meshdir="{ROOT.as_posix()}/'))


class Poser:
    def __init__(self):
        self.m = m = load_fixed()
        self.d = mujoco.MjData(m)
        self.qadr = {mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j): m.jnt_qposadr[j] for j in range(m.njnt)}
        self.bname = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, b) for b in range(m.nbody)]

    def contacts(self, deg: dict, base: str = "stance") -> dict:
        """deg: {joint name (with or without _joint): degrees}; the other joints at the RL stance default (base="stance")
        or at 0 (base="zero", the SolidWorks convention). -> {"body_a|body_b": hull overlap mm}."""
        d = self.d
        d.qpos[:] = 0.0
        for j, v in (STANCE.items() if base == "stance" else ()):
            if j in self.qadr:
                d.qpos[self.qadr[j]] = v
        for j, v in deg.items():
            d.qpos[self.qadr[j if j.endswith("_joint") else j + "_joint"]] = np.radians(v)
        mujoco.mj_fwdPosition(self.m, d)
        out = {}
        for c in d.contact[:d.ncon]:
            b1, b2 = self.m.geom_bodyid[c.geom1], self.m.geom_bodyid[c.geom2]
            if b1 and b2:
                k = "|".join(sorted((self.bname[b1], self.bname[b2])))
                out[k] = max(out.get(k, 0.0), round(-1000 * float(c.dist), 1))
        return out


def arm(side: str, pitch, roll, yaw, elbow) -> dict:
    s = 1 if side == "left" else -1
    other = "right" if side == "left" else "left"
    return {f"{side}_shoulder_pitch": pitch, f"{side}_shoulder_roll": s * roll, f"{side}_shoulder_yaw": s * yaw,
            f"{side}_elbow": elbow, f"{other}_shoulder_roll": -s * RELAXED_ROLL}


def method_check(ps: Poser) -> dict:
    """SolidWorks (exact geometry) vs MuJoCo hulls on the same poses (unset joints at 0 as in SolidWorks). The upper-body
    assembly (verification/JX1_UpperBody_build.json) has pelvis, torso, arms, neck and head but no legs, so contacts with
    leg links are left out of that comparison."""
    rows = []
    robot = json.loads((OUT / "robot_motion_verification.json").read_text(encoding="utf-8"))
    for p in robot:
        deg = {f"{side}_{j}": v for side in ("left", "right") for j, v in p[f"{side}_leg_deg"].items()}
        deg.update(p["upper_deg"])
        rows.append(("robot", p["pose"], deg, p["collision_free"], sorted({"|".join(sorted(i["components"])) for i in p["interferences"]})))
    upper = json.loads((OUT / "upper_motion_verification.json").read_text(encoding="utf-8"))
    for p in upper:
        rows.append(("upper", p["pose"], p["joints_deg"], p["collision_free"], sorted({"|".join(sorted(i["components"])) for i in p["interferences"]})))
    out, agree = [], 0
    legs = ("hip_", "thigh", "shin", "ankle", "foot")
    for src, name, deg, sw_free, sw_pairs in rows:
        c = ps.contacts(deg, base="zero")
        if src == "upper":
            c = {k: v for k, v in c.items() if not any(t in k for t in legs)}
        ok = (not c) == bool(sw_free)
        agree += ok
        out.append({"set": src, "pose": name, "solidworks_collision_free": bool(sw_free), "solidworks_interferences": sw_pairs,
                    "mujoco_collision_free": not c, "mujoco_contacts": c, "agree": ok})
    return {"poses": len(out), "agree": agree, "rows": out}


def sweep(ps: Poser, side: str) -> dict:
    by_pitch, pairs = {}, {}
    for pitch, roll, yaw, elbow in itertools.product(PITCH, ROLL, YAW, ELBOW):
        c = ps.contacts(arm(side, pitch, roll, yaw, elbow))
        b = by_pitch.setdefault(pitch, {"poses": 0, "clash": 0, "pairs": set()})
        b["poses"] += 1
        if c:
            b["clash"] += 1
            b["pairs"] |= set(c)
            for k in c:
                w = pairs.setdefault(k, {"poses": 0, "example": {"pitch": pitch, "roll": roll, "yaw": yaw, "elbow": elbow}})
                w["poses"] += 1
    reach_up = {p: sorted(ps.contacts(arm(side, p, RELAXED_ROLL, 0, 0))) for p in PITCH}
    reach_up_bent = {p: sorted(ps.contacts(arm(side, p, RELAXED_ROLL, 0, -90))) for p in PITCH}
    free_overhead = {}
    for p in OVERHEAD:
        free = [(r, y, e) for r, y, e in itertools.product(ROLL, YAW, ELBOW) if not ps.contacts(arm(side, p, r, y, e))]
        free_overhead[p] = {"free": len(free), "of": len(ROLL) * len(YAW) * len(ELBOW),
                            "roll_range_free_at_yaw0_elbow0": [r for r, y, e in free if y == 0 and e == 0]}
    neck = {"poses": 0, "clash": 0, "pairs": set()}
    for p, r, e, ny, npi in itertools.product(OVERHEAD, [0, RELAXED_ROLL, 20], [0, -45], NECK_YAW, NECK_PITCH):
        c = ps.contacts({**arm(side, p, r, 0, e), "neck_yaw": ny, "neck_pitch": npi})
        neck["poses"] += 1
        if c:
            neck["clash"] += 1
            neck["pairs"] |= set(c)
    return {"by_pitch": {str(p): {**v, "pairs": sorted(v["pairs"])} for p, v in by_pitch.items()},
            "pairs": dict(sorted(pairs.items(), key=lambda kv: -kv[1]["poses"])),
            "reach_up_roll8_yaw0_elbow0_clash_at": {str(p): v for p, v in reach_up.items() if v},
            "reach_up_roll8_yaw0_elbow-90_clash_at": {str(p): v for p, v in reach_up_bent.items() if v},
            "overhead_free_postures": {str(p): v for p, v in free_overhead.items()},
            "overhead_with_neck": {**neck, "pairs": sorted(neck["pairs"])}}


def render(ps: Poser, deg: dict, path: Path, azimuth: float, elevation: float = -10):
    ps.contacts(deg)
    mujoco.mj_forward(ps.m, ps.d)
    r = mujoco.Renderer(ps.m, 480, 400)                                # height, width (offscreen buffer 480)
    cam = mujoco.MjvCamera()
    top = max(ps.d.geom_xpos[g][2] for g in range(ps.m.ngeom) if ps.m.geom_bodyid[g])
    cam.lookat[:] = [0.0, 0.0, (top + 0.9) / 2]                       # the upper body from the hips to the raised hands
    cam.distance, cam.azimuth, cam.elevation = 1.1 + 1.1 * (top - 0.9), azimuth, elevation
    r.update_scene(ps.d, cam)
    import PIL.Image
    PIL.Image.fromarray(r.render()).save(path)
    r.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    ps = Poser()
    for j in ("left_shoulder_pitch_joint", "left_shoulder_roll_joint", "left_shoulder_yaw_joint", "left_elbow_joint"):
        lo, hi = LIMITS[j]
        print(f"{j}: joint_map {lo:.0f}...{hi:.0f} deg")
    mc = method_check(ps)
    print(f"method check: MuJoCo hulls agree with SolidWorks on {mc['agree']}/{mc['poses']} poses")
    for r in mc["rows"]:
        if not r["agree"]:
            print("  differs:", r["set"], r["pose"], "SW free" if r["solidworks_collision_free"] else "SW clash", r["mujoco_contacts"])
    res = {"model": XML.relative_to(ROOT).as_posix(), "model_sha256": hashlib.sha256(XML.read_bytes()).hexdigest(),
           "method": "kinematic posing, fixed base, contacts between robot bodies on the CoACD convex hulls (adjacent pairs excluded "
                     "by the model); hull overlap depths are not physical penetrations",
           "grid_deg": {"shoulder_pitch": PITCH, "shoulder_roll_abduction": ROLL, "shoulder_yaw": YAW, "elbow": ELBOW,
                        "other_arm_roll": RELAXED_ROLL, "legs": "rl/config/jx1_walk.yaml default_joint_pos",
                        "neck_sub_sweep": {"yaw": NECK_YAW, "pitch": NECK_PITCH, "at_shoulder_pitch": OVERHEAD}},
           "method_check": mc, "arms": {}}
    for side in ("left", "right"):
        s = res["arms"][side] = sweep(ps, side)
        tot = sum(v["poses"] for v in s["by_pitch"].values())
        cl = sum(v["clash"] for v in s["by_pitch"].values())
        ov = s["overhead_free_postures"]
        print(f"{side}: {cl}/{tot} grid poses with a hull contact; pairs {list(s['pairs'])}")
        print(f"  reach-up (roll 8, yaw 0, elbow 0) clashes at pitch {list(s['reach_up_roll8_yaw0_elbow0_clash_at'])}")
        print("  overhead free postures:", {p: f"{v['free']}/{v['of']}" for p, v in ov.items()})
        print(f"  overhead with the neck moving: {s['overhead_with_neck']['clash']}/{s['overhead_with_neck']['poses']} "
              f"clash {s['overhead_with_neck']['pairs']}")
    res["summary"] = {"method_check": f"{mc['agree']}/{mc['poses']} poses agree with SolidWorks (exact geometry)"}
    for side, s in res["arms"].items():
        ov = s["overhead_free_postures"].values()
        res["summary"][side] = {
            "grid_poses_with_contact": f"{sum(v['clash'] for v in s['by_pitch'].values())}/{sum(v['poses'] for v in s['by_pitch'].values())}",
            "reach_up_straight_arm_clear_to_-170": not s["reach_up_roll8_yaw0_elbow0_clash_at"],
            "reach_up_elbow_-90_clear_to_-170": not s["reach_up_roll8_yaw0_elbow-90_clash_at"],
            "overhead_straight_arm_clear_at_every_roll": all(len(v["roll_range_free_at_yaw0_elbow0"]) == len(ROLL) for v in ov),
            "overhead_min_free_postures": "{free}/{of}".format(**min(ov, key=lambda v: v["free"])),
            "overhead_with_neck_moving": f"{s['overhead_with_neck']['clash']}/{s['overhead_with_neck']['poses']} with contact",
            "contact_pairs": {k: w["poses"] for k, w in s["pairs"].items()}}
    (OUT / "mujoco_arm_range.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("wrote", OUT / "mujoco_arm_range.json")
    if not a.no_render:
        IMG.mkdir(parents=True, exist_ok=True)
        up = {**arm("left", -170, RELAXED_ROLL, 0, 0), **{k: v for k, v in arm("right", -170, RELAXED_ROLL, 0, 0).items() if k.startswith("right")}}
        render(ps, up, IMG / "arms_overhead_front.png", azimuth=180)
        render(ps, up, IMG / "arms_overhead_side.png", azimuth=90)
        print("wrote", IMG / "arms_overhead_front.png", IMG / "arms_overhead_side.png")


if __name__ == "__main__":
    main()
