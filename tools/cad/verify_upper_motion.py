"""Verify the articulated JX1 upper body in SolidWorks (same method as tools/cad/verify_leg_motion.py).

For each pose the limit mates are driven, SolidWorks solves the assembly, every component transform is compared with
the analytic model (tools/cad/upper_kinematics.py), mate errors are collected and interference detection runs.
Outputs verification/upper_motion_verification.{json,csv} and pose images in verification/images/poses/.
Usage: .venv/Scripts/python tools/cad/verify_upper_motion.py [--images]
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
from swlib.core import C, Session, typed, set_view  # noqa: E402
from cad.params import ROOT  # noqa: E402
from cad.build_leg_assembly import from_sw  # noqa: E402
from cad.upper_kinematics import UpperCAD, ACTUATED, cad_limits_deg  # noqa: E402

NAME = "JX1_UpperBody"
WHITELIST = []          # no intentional overlaps in the upper body


def poses_to_test():
    P = [("zero", {})]
    for joint, *_ in ACTUATED:
        lo, hi = cad_limits_deg(joint)
        P.append((f"{joint}_min", {joint: lo}))
        P.append((f"{joint}_max", {joint: hi}))
    both = lambda **kw: {f"{s}_{k}": (v if not (s == "right" and k in ("shoulder_roll", "shoulder_yaw")) else -v)  # noqa: E731
                         for s in ("left", "right") for k, v in kw.items()}
    P += [
        ("t_pose", both(shoulder_roll=90)),
        ("arms_forward", both(shoulder_pitch=-90)),
        ("reach_up_cad_max", both(shoulder_pitch=-115, elbow=0)),
        ("arms_back", both(shoulder_pitch=60, elbow=-20)),
        ("hands_together_front", both(shoulder_pitch=-60, shoulder_roll=10, shoulder_yaw=-30, elbow=-90)),
        ("carry_box", both(shoulder_pitch=-30, shoulder_roll=15, elbow=-90)),
        ("elbows_flexed_down", both(elbow=-135)),
        ("arms_adducted", both(shoulder_roll=-10)),
        ("walk_swing_front", {**both(shoulder_roll=8), "left_shoulder_pitch": -30, "right_shoulder_pitch": 30, "left_elbow": -30, "right_elbow": -30}),
        ("waist_twist_left", {"waist_yaw": 60, **both(shoulder_roll=8)}),
        ("head_left_down", {"neck_yaw": 70, "neck_pitch": 45}),
        ("head_right_up", {"neck_yaw": -70, "neck_pitch": -30}),
        ("wave_left", {"left_shoulder_pitch": -20, "left_shoulder_roll": 140, "left_elbow": -90, "right_shoulder_roll": -8}),
    ]
    return P


class UpperVerifier:
    def __init__(self):
        self.s = Session()
        path = (ROOT / "CAD" / "Assemblies" / f"{NAME}.SLDASM").resolve()
        docs = [d for d in self.s.open_documents() if d.GetPathName().lower() == str(path).lower()]
        self.doc = docs[0] if docs else self.s.open_doc(path)
        self.s.activate(self.doc)
        self.A = typed(self.doc, "IAssemblyDoc")
        self.ext = typed(self.doc.Extension, "IModelDocExtension")
        build = json.loads((ROOT / "verification" / f"{NAME}_build.json").read_text())
        self.calib = build["limit_calibration"]
        self.names = build["names"]
        byname = {typed(c, "IComponent2").Name2: typed(c, "IComponent2") for c in self.A.GetComponents(True)}
        self.comp = {k: byname[n] for k, n in self.names.items() if n in byname}
        self.key_by_name = {n: k for k, n in self.names.items()}
        self.mates = {}
        f = self.doc.FirstFeature()
        while f is not None:
            f = typed(f, "IFeature")
            if f.GetTypeName2() == "MateGroup":
                sub = f.GetFirstSubFeature()
                while sub is not None:
                    sub = typed(sub, "IFeature")
                    self.mates[sub.Name] = sub
                    sub = sub.GetNextSubFeature()
            f = f.GetNextFeature()
        self.model = UpperCAD()

    def set_joints(self, q_deg):
        for joint, *_ in ACTUATED:
            m = f"{joint}_LIMIT"
            c = self.calib[m]
            val = math.radians(c["zero_deg"] + c["sign"] * q_deg.get(joint, 0.0))
            d = typed(typed(self.mates[m].GetFirstDisplayDimension(), "IDisplayDimension").GetDimension2(0), "IDimension")
            d.SetSystemValue3(val, C.swSetValue_InThisConfiguration, None)
        self.doc.EditRebuild3()

    def drift(self, q_deg):
        fk = self.model.component_poses({k: math.radians(v) for k, v in q_deg.items()})
        worst, per = (0.0, 0.0, None), {}
        for key, M4 in fk.items():
            if key not in self.comp:
                continue
            A_ = from_sw(self.comp[key].Transform2)
            dp = float(np.linalg.norm(A_[:3, 3] - M4[:3, 3])) * 1000
            dr = float(np.degrees(np.arccos(np.clip((np.trace(A_[:3, :3].T @ M4[:3, :3]) - 1) / 2, -1, 1))))
            per[key] = (round(dp, 4), round(dr, 4))
            if dp > worst[0] or dr > worst[1]:
                worst = (max(worst[0], dp), max(worst[1], dr), key)
        return worst, per

    def mate_errors(self):
        errs = []
        for n, f in self.mates.items():
            code = f.GetErrorCode2()
            e = code[0] if isinstance(code, tuple) else code
            if e not in (0, None):
                errs.append((n, e))
        return errs

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
        for it in idm.GetInterferences() or []:
            it = typed(it, "IInterference")
            comps = [self.key_by_name.get(typed(c, "IComponent2").Name2, typed(c, "IComponent2").Name2) for c in (it.Components or [])]
            out.append({"components": comps, "volume_mm3": round(it.Volume * 1e9, 3)})
        idm.Done()
        return out

    def image(self, path):
        set_view(self.s.app, self.doc)                                    # Z-up camera (SolidWorks named views are Y-up)
        self.ext.SaveAs3(str(path), 0, 1, None, None, 0, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", action="store_true")
    a = ap.parse_args()
    v = UpperVerifier()
    img = ROOT / "verification" / "images" / "poses"
    img.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, q in poses_to_test():
        v.set_joints(q)
        (dp, dr, who), per = v.drift(q)
        ints = [i for i in v.interferences() if not any(set(i["components"]) == set(w) for w in WHITELIST)]
        errs = v.mate_errors()
        rows.append({"pose": name, "joints_deg": q, "max_pos_err_mm": round(dp, 4), "max_rot_err_deg": round(dr, 4), "worst_component": who,
                     "mate_errors": errs, "interferences": ints, "kinematics_pass": dp < 0.05 and dr < 0.05 and not errs,
                     "collision_free": not ints})
        print(f"{name:26s} kin {'OK ' if rows[-1]['kinematics_pass'] else 'BAD'} err {dp:8.4f} mm {dr:7.4f} deg ({who})  "
              f"collisions {len(ints)} {[(i['components'][0], i['components'][1], i['volume_mm3']) for i in ints][:3]}", flush=True)
        if a.images and name in ("zero", "t_pose", "arms_forward", "hands_together_front", "wave_left", "waist_twist_left", "head_left_down"):
            v.image(img / f"{NAME}_{name}.png")
    v.set_joints({})
    (ROOT / "verification" / "upper_motion_verification.json").write_text(json.dumps(rows, indent=1, default=str))
    with open(ROOT / "verification" / "upper_motion_verification.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["pose", "max_pos_err_mm", "max_rot_err_deg", "kinematics_pass", "collisions", "collision_pairs"])
        for r in rows:
            w.writerow([r["pose"], r["max_pos_err_mm"], r["max_rot_err_deg"], r["kinematics_pass"], len(r["interferences"]),
                        "; ".join(f"{i['components'][0]}|{i['components'][1]}|{i['volume_mm3']}" for i in r["interferences"])])
    kin = sum(r["kinematics_pass"] for r in rows)
    free = sum(r["collision_free"] for r in rows)
    print(f"\nkinematics pass {kin}/{len(rows)}, collision-free {free}/{len(rows)}")


if __name__ == "__main__":
    main()
