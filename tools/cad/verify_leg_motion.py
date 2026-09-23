"""Verify the articulated JX1 leg in SolidWorks: every joint to min / zero / max, then multi-joint poses.

For each pose the joint LIMIT mates are driven (SolidWorks solves the chain and the closed ankle linkage), then:
  1. every component transform is compared with the analytic forward kinematics (tools/cad/leg_kinematics.py) —
     this checks axes, origins, signs and the parallel-ankle model against the SolidWorks solution;
  2. mate errors are collected;
  3. SolidWorks interference detection runs (coincident faces are not interference).
Outputs verification/leg_motion_verification.{json,csv} and pose images in verification/images/poses/.

Usage: .venv/Scripts/python tools/cad/verify_leg_motion.py [--name JX1_LowerBody] [--images]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from swlib.core import C, Session, typed  # noqa: E402
from cad.params import ROOT, DP  # noqa: E402
from cad.leg_kinematics import LegCAD  # noqa: E402
from cad.build_leg_assembly import from_sw  # noqa: E402

JR = DP["joint_ranges_deg"]
LEG_JOINTS = ["hip_yaw", "hip_roll", "hip_pitch", "knee", "ankle_pitch", "ankle_roll"]
# rod-end ball envelopes intentionally overlap their studs (crank pin / foot post) — physical parts are coaxial pins
WHITELIST = [("RodA", "CrankA"), ("RodB", "CrankB"), ("RodA", "Foot"), ("RodB", "Foot")]


def poses_to_test():
    P = [("zero", {})]
    for j in LEG_JOINTS:
        P.append((f"{j}_min", {j: JR[j]["min"]}))
        P.append((f"{j}_max", {j: JR[j]["max"]}))
    P += [
        ("stand_bent", {"hip_pitch": -18, "knee": 36, "ankle_pitch": -18}),
        ("walk_crouch", {"hip_pitch": -30, "knee": 58, "ankle_pitch": -28}),
        ("deep_squat", {"hip_pitch": -70, "knee": 120, "ankle_pitch": -50}),
        ("leg_forward", {"hip_pitch": -60, "knee": 20}),
        ("leg_backward", {"hip_pitch": 30, "knee": 30, "ankle_pitch": -15}),
        ("wide_stance", {"hip_roll": 30, "ankle_roll": -20}),
        ("single_leg_lift", {"hip_pitch": -45, "knee": 90, "ankle_pitch": -20, "hip_roll": 5}),
        ("toe_out_step", {"hip_yaw": 40, "hip_pitch": -20, "knee": 40, "ankle_pitch": -20}),
        ("toe_in_step", {"hip_yaw": -35, "hip_pitch": -20, "knee": 40, "ankle_pitch": -20}),
        ("sit", {"hip_pitch": -90, "knee": 90}),
        ("ankle_corner_1", {"ankle_pitch": -55, "ankle_roll": 20, "knee": 60, "hip_pitch": -30}),
        ("ankle_corner_2", {"ankle_pitch": 35, "ankle_roll": -20}),
    ]
    return P


class Verifier:
    def __init__(self, name):
        self.s = Session()
        path = (ROOT / "CAD" / "Assemblies" / f"{name}.SLDASM").resolve()
        docs = [d for d in self.s.open_documents() if d.GetPathName().lower() == str(path).lower()]
        self.doc = docs[0] if docs else self.s.open_doc(path)
        self.s.activate(self.doc)
        self.A = typed(self.doc, "IAssemblyDoc")
        self.ext = typed(self.doc.Extension, "IModelDocExtension")
        build = json.loads((ROOT / "verification" / f"{name}_build.json").read_text())
        self.calib = build["limit_calibration"]
        self.names = build["names"]
        byname = {typed(c, "IComponent2").Name2: typed(c, "IComponent2") for c in self.A.GetComponents(True)}
        self.comp = {k: byname[n] for k, n in self.names.items() if n in byname}
        self.key_by_name = {n: k for k, n in self.names.items()}
        self.mates = self._mates()

    def _mates(self):
        out = {}
        f = self.doc.FirstFeature()
        while f is not None:
            f = typed(f, "IFeature")
            if f.GetTypeName2() == "MateGroup":
                sub = f.GetFirstSubFeature()
                while sub is not None:
                    sub = typed(sub, "IFeature")
                    out[sub.Name] = sub
                    sub = sub.GetNextSubFeature()
            f = f.GetNextFeature()
        return out

    def set_joints(self, side, q_deg):
        leg = LegCAD(1 if side == "L" else -1)
        sgn = 1 if side == "L" else -1
        phi = leg.ankle.crank_angles(math.radians(q_deg.get("ankle_pitch", 0.0)), sgn * math.radians(q_deg.get("ankle_roll", 0.0)))
        targets = {j: q_deg.get(j, 0.0) for j in ("hip_yaw", "hip_roll", "hip_pitch", "knee")}
        targets["ankle_motorA"], targets["ankle_motorB"] = math.degrees(phi[0]), math.degrees(phi[1])
        for j, qd in targets.items():
            m = f"{side}_{j}_LIMIT"
            c = self.calib[m]
            val = math.radians(c["zero_deg"] + c["sign"] * qd)
            f = self.mates[m]
            d = typed(typed(f.GetFirstDisplayDimension(), "IDisplayDimension").GetDimension2(0), "IDimension")
            d.SetSystemValue3(val, C.swSetValue_InThisConfiguration, None)
        self.doc.EditRebuild3()

    def mate_errors(self):
        errs = []
        for n, f in self.mates.items():
            code = f.GetErrorCode2()
            e = code[0] if isinstance(code, tuple) else code
            if e not in (0, None):
                errs.append((n, e))
        return errs

    def drift(self, side, q_deg):
        leg = LegCAD(1 if side == "L" else -1)
        q = {k: math.radians(v) for k, v in q_deg.items()}
        fk = leg.component_poses(q)
        worst = (0.0, 0.0, None)
        per = {}
        for key, M4 in fk.items():
            if key.endswith("_len"):
                continue
            ck = f"{side}_{key}"
            if ck not in self.comp:
                continue
            A_ = from_sw(self.comp[ck].Transform2)
            dp = float(np.linalg.norm(A_[:3, 3] - M4[:3, 3])) * 1000
            if key.startswith("Rod"):  # rods have a free spin about their own axis: compare the axis only
                dr = float(np.degrees(np.arccos(np.clip(np.dot(A_[:3, 2], M4[:3, 2]), -1, 1))))
            else:
                dr = float(np.degrees(np.arccos(np.clip((np.trace(A_[:3, :3].T @ M4[:3, :3]) - 1) / 2, -1, 1))))
            per[key] = (round(dp, 4), round(dr, 4))
            if dp > worst[0] or dr > worst[1]:
                worst = (max(worst[0], dp), max(worst[1], dr), key)
        return worst, per, leg.phi

    def interferences(self):
        idm = typed(self.A.InterferenceDetectionManager, "IInterferenceDetectionMgr")
        idm.TreatCoincidenceAsInterference = False
        idm.TreatSubAssembliesAsComponents = True
        idm.IncludeMultibodyPartInterferences = False
        idm.MakeInterferingPartsTransparent = False
        idm.CreateFastenersFolder = False
        idm.IgnoreHiddenBodies = True
        idm.ShowIgnoredInterferences = False
        idm.UseTransform = True
        out = []
        ints = idm.GetInterferences() or []
        for it in ints:
            it = typed(it, "IInterference")
            comps = [self.key_by_name.get(typed(c, "IComponent2").Name2, typed(c, "IComponent2").Name2) for c in (it.Components or [])]
            out.append({"components": comps, "volume_mm3": round(it.Volume * 1e9, 3)})
        idm.Done()
        return out

    @staticmethod
    def whitelisted(pair):
        keys = [c.split("_", 1)[1] if c[:2] in ("L_", "R_") else c for c in pair]
        return any(set(keys) == set(w) for w in WHITELIST)

    def image(self, path):
        self.doc.ShowNamedView2("*Isometric", 7)
        self.doc.ViewZoomtofit2()
        self.ext.SaveAs3(str(path), 0, 1, None, None, 0, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="JX1_LowerBody")
    ap.add_argument("--side", default="L")
    ap.add_argument("--images", action="store_true")
    a = ap.parse_args()
    v = Verifier(a.name)
    imgdir = ROOT / "verification" / "images" / "poses"
    imgdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, q in poses_to_test():
        v.set_joints(a.side, q)
        (dp, dr, who), per, phi = v.drift(a.side, q)
        errs = v.mate_errors()
        ints = v.interferences()
        real = [i for i in ints if not v.whitelisted(i["components"])]
        row = {"pose": name, "joints_deg": q, "max_pos_err_mm": round(dp, 4), "max_rot_err_deg": round(dr, 4), "worst_component": who,
               "ankle_motor_deg": [round(float(np.degrees(x)), 2) for x in phi], "mate_errors": errs,
               "interferences": real, "whitelisted_contacts": len(ints) - len(real),
               "kinematics_pass": dp < 0.05 and dr < 0.05 and not errs, "collision_free": not real}
        rows.append(row)
        print(f"{name:18s} kin {'OK ' if row['kinematics_pass'] else 'BAD'} err {dp:8.4f} mm {dr:7.4f} deg ({who})  "
              f"collisions {len(real)} {[tuple(i['components']) + (i['volume_mm3'],) for i in real][:3]}", flush=True)
        if a.images and name in ("zero", "stand_bent", "deep_squat", "leg_forward", "leg_backward", "wide_stance", "single_leg_lift", "sit"):
            v.image((imgdir / f"{a.name}_{name}.png").resolve())
    v.set_joints(a.side, {})
    out = ROOT / "verification" / "leg_motion_verification.json"
    out.write_text(json.dumps(rows, indent=2, default=str))
    with open(ROOT / "verification" / "leg_motion_verification.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["pose", "joints_deg", "max_pos_err_mm", "max_rot_err_deg", "kinematics_pass", "collision_free", "collisions"])
        for r in rows:
            w.writerow([r["pose"], json.dumps(r["joints_deg"]), r["max_pos_err_mm"], r["max_rot_err_deg"], r["kinematics_pass"],
                        r["collision_free"], "; ".join(f"{'/'.join(i['components'])}:{i['volume_mm3']}mm3" for i in r["interferences"])])
    npass = sum(r["kinematics_pass"] for r in rows)
    nfree = sum(r["collision_free"] for r in rows)
    print(f"\nkinematics pass {npass}/{len(rows)}, collision-free {nfree}/{len(rows)}")


if __name__ == "__main__":
    main()
