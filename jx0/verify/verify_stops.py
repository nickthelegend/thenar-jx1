"""JX0 joint stops: what stops each joint, and that nothing touches inside the commanded range.

The robot has three layers of joint stops:
1. robot.py clamps every command to config.yaml's limits, and each hip's roll to a range that shrinks as the hip
   flexes (couple_hips);
2. every servo stores its joint's limits, 1 deg wider, in its own EEPROM (calibrate.py limits) and refuses goals
   outside them, whatever the Pi sends;
3. printed stops: past that, the first contact is between two printed brackets (in the plates of the U-brackets,
   like the reference robot's integrated joint stops), never a screw head, a cable or a servo case.

Checks, on the exact CAD solids (verify_cad.Robot), left limb (the right one is its mirror image):
- range: the whole commanded box is contact-free: hip yaw x roll x pitch (with the hip coupling), ankle pitch x roll,
  shoulder x elbow, each joint at 2-4 deg steps;
- stops: each joint driven past its EEPROM limit, in 1 deg steps up to 45 deg, with the coupled joint at several
  angles: the first contact is at least MARGIN deg past the EEPROM limit, and it is printed part on printed part.

    python jx0/verify/verify_stops.py      -> jx0/results/verify_stops.json
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "software"))
import verify_cad as V  # noqa: E402
from jx0bot.robot import couple_hips  # noqa: E402

OUT = V.ROOT / "jx0" / "results" / "verify_stops.json"
EEPROM_DEG = 1.0                  # calibrate.LIMIT_MARGIN_DEG
MARGIN = 2.0                      # the first contact must be this far past the EEPROM limit
FRAGILE = ("screws:", "cables:", "servo_")
LIMB = {"leg": lambda k: k.endswith("_L") or k in ("pelvis", "torso"),
        "arm": lambda k: k.endswith("_L") or k in ("torso", "chest_cap", "pelvis")}


class Limb:
    def __init__(self, rb, which):
        keep = LIMB[which]
        self.rb = rb
        self.items = [it for it in rb.items if keep(it[0]) or keep(rb.owner.get(it[0], "-"))]

    def clashes(self, q):
        full = self.rb.items
        self.rb.items = self.items
        try:
            return self.rb.clashes(self.rb.pose(q))
        finally:
            self.rb.items = full


def frange(a, b, step):
    n = int(math.floor((b - a) / step + 1e-9))
    return [a + step * i for i in range(n + 1)] + ([b] if a + step * n < b - 1e-9 else [])


def main():
    t0 = time.time()
    rb = V.Robot()
    leg, arm = Limb(rb, "leg"), Limb(rb, "arm")
    stand = dict(next(V.gait_frames())[2])
    cfg = yaml.safe_load(V.CONFIG.read_text(encoding="utf-8"))
    lim = {k: v["limits_deg"] for k, v in {**cfg["leg_servos"], **cfg["arm_servos"]}.items()}
    rad = math.radians
    result = {"eeprom_margin_deg": EEPROM_DEG, "required_stop_margin_deg": MARGIN}

    # 1. the commanded range is contact-free
    boxes = []
    hip = []
    for yaw in (lim["l_hip_yaw"][0], 0.0, lim["l_hip_yaw"][1]):
        for pitch in frange(*lim["l_hip_pitch"], 4.0):
            for roll in frange(*lim["l_hip_roll"], 2.0):
                q = couple_hips({**stand, "l_hip_yaw": rad(yaw), "l_hip_pitch": rad(pitch), "l_hip_roll": rad(roll)})
                if abs(math.degrees(q["l_hip_roll"]) - roll) > 1e-6:
                    continue                                          # outside the coupled range: never commanded
                c = leg.clashes(q)
                hip.append(1)
                if c:
                    boxes.append(dict(box="hip", yaw=yaw, pitch=pitch, roll=roll, contacts=c[:3]))
    ank = []
    for pitch in frange(*lim["l_ankle_pitch"], 2.5):
        for roll in frange(*lim["l_ankle_roll"], 2.5):
            c = leg.clashes({**stand, "l_ankle_pitch": rad(pitch), "l_ankle_roll": rad(roll)})
            ank.append(1)
            if c:
                boxes.append(dict(box="ankle", pitch=pitch, roll=roll, contacts=c[:3]))
    sho = []
    for sp in frange(*lim["l_shoulder_pitch"], 7.5):
        for el in frange(*lim["l_elbow"], 7.5):
            c = arm.clashes({**stand, "l_shoulder_pitch": rad(sp), "l_elbow": rad(el)})
            sho.append(1)
            if c:
                boxes.append(dict(box="arm", shoulder=sp, elbow=el, contacts=c[:3]))
    result["range"] = {"poses": {"hip (yaw x pitch x coupled roll)": len(hip), "ankle (pitch x roll)": len(ank),
                                 "arm (shoulder x elbow)": len(sho)}, "contacts": boxes}
    print(f"range: {len(hip)} hip, {len(ank)} ankle, {len(sho)} arm poses inside the limits -> {len(boxes)} with contact",
          flush=True)
    for b in boxes[:10]:
        print("   ", b)

    # 2. the stops: past the EEPROM limit
    cases = [("l_hip_yaw", leg, {}), ("l_hip_pitch", leg, {"l_hip_roll": [-12.0, 0.0, 10.0]}),
             ("l_hip_roll", leg, {"l_hip_pitch": [-30.0, -10.0, 8.0]}), ("l_knee", leg, {}),
             ("l_ankle_pitch", leg, {"l_ankle_roll": [lim["l_ankle_roll"][0], 0.0, lim["l_ankle_roll"][1]]}),
             ("l_ankle_roll", leg, {"l_ankle_pitch": [lim["l_ankle_pitch"][0], -40.0, -27.0, -15.0, lim["l_ankle_pitch"][1]]}),
             ("l_shoulder_pitch", arm, {}), ("l_elbow", arm, {"l_shoulder_pitch": [-90.0, 0.0, 45.0]}), ("neck_yaw", arm, {})]
    stops, problems = [], []
    for joint, limb, others in cases:
        variants = [{}] if not others else [{k: rad(v)} for k, vs in others.items() for v in vs]
        for end, sgn in ((lim[joint][0], -1), (lim[joint][1], +1)):
            e = end + sgn * EEPROM_DEG
            for var in variants:
                first = None
                for k in range(1, 46):
                    deg = e + sgn * k
                    c = [x for x in limb.clashes({**stand, **var, joint: rad(deg)})]
                    if c:
                        first = (deg, c[:3])
                        break
                row = dict(joint=joint, end="low" if sgn < 0 else "high", eeprom_deg=e,
                           with_={k: round(math.degrees(v), 1) for k, v in var.items()},
                           first_contact_deg=first[0] if first else None,
                           past_eeprom_deg=abs(first[0] - e) if first else None,
                           contacts=first[1] if first else [])
                bad = []
                if first and row["past_eeprom_deg"] < MARGIN:
                    bad.append(f"first contact only {row['past_eeprom_deg']:.0f} deg past the servo's limit")
                if first and any(any(f in c[0] or f in c[1] for f in FRAGILE) for c in first[1]):
                    bad.append(f"the first contact is not printed part on printed part: {first[1]}")
                row["problems"] = bad
                stops.append(row)
                problems += [f"{joint} {row['end']} {row['with_']}: {b}" for b in bad]
                what = (f"stops at {first[0]:+.0f} ({row['past_eeprom_deg']:.0f} past): "
                        f"{', '.join(f'{a} / {b}' for a, b, _ in first[1][:2])}" if first else "free for 45 deg")
                print(f"{joint:17s} {row['end']:4s} servo limit {e:+5.0f}  {str(row['with_']):24s} {what}"
                      f"{'   <-- ' + '; '.join(bad) if bad else ''}", flush=True)
    result["stops"] = stops
    result["problems"] = problems + [f"contact inside the range: {b}" for b in boxes]
    result["seconds"] = round(time.time() - t0, 1)
    result["pass"] = not result["problems"]
    OUT.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(f"joint stops: {'PASS' if result['pass'] else 'FAIL'} ({len(result['problems'])} problems, {result['seconds']} s)"
          f" -> {OUT.relative_to(V.ROOT)}")
    sys.exit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
