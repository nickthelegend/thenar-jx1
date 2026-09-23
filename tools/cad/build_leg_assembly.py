"""Assemble the JX1 pelvis + leg(s) in SolidWorks with real mates.

Mates per leg:
  * LOCK between bolted parts (bracket <-> actuator housing, output <-> child link ...)
  * revolute actuator joints: coincident axes (AX_Joint) + coincident interface planes + LIMIT angle mate
  * passive ankle pitch/roll (universal joint) with limit angle mates
  * parallel ankle: motor rotors (axis + plane), crank LOCKed to rotor, push rods with ball-joint (point) mates
Limit-mate signs are calibrated: each joint is posed at +0.1 rad through analytic FK, SolidWorks re-solves,
and the measured mate angle sign decides whether [lo, hi] or [-hi, -lo] is applied.

Usage: .venv/Scripts/python tools/cad/build_leg_assembly.py [--sides L] [--name JX1_LowerBody]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from swlib.core import C, Session, save_as, set_mmgs, typed, var_array  # noqa: E402
from cad.params import ROOT, DP  # noqa: E402
from cad.leg_kinematics import LegCAD, CLOCK  # noqa: E402

CAD = ROOT / "CAD"
PARTS = {
    "Pelvis": CAD / "Pelvis/JX1_Pelvis.SLDPRT",
    "ACT_XL_Housing": CAD / "Actuators/JX1_ACT_XL_Housing.SLDPRT", "ACT_XL_Output": CAD / "Actuators/JX1_ACT_XL_Output.SLDPRT",
    "ACT_L_Housing": CAD / "Actuators/JX1_ACT_L_Housing.SLDPRT", "ACT_L_Output": CAD / "Actuators/JX1_ACT_L_Output.SLDPRT",
    "ACT_M_Housing": CAD / "Actuators/JX1_ACT_M_Housing.SLDPRT", "ACT_M_Output": CAD / "Actuators/JX1_ACT_M_Output.SLDPRT",
    "ACT_S_Housing": CAD / "Actuators/JX1_ACT_S_Housing.SLDPRT", "ACT_S_Output": CAD / "Actuators/JX1_ACT_S_Output.SLDPRT",
    "HipYawBracket": CAD / "Hip/JX1_HipYawBracket_{S}.SLDPRT", "HipRollBracket": CAD / "Hip/JX1_HipRollBracket_{S}.SLDPRT",
    "Thigh": CAD / "Thigh/JX1_Thigh_{S}.SLDPRT", "Shin": CAD / "Shin/JX1_Shin_{S}.SLDPRT", "Foot": CAD / "Foot/JX1_Foot_{S}.SLDPRT",
    "AnkleCrank": CAD / "Ankle/JX1_AnkleCrank.SLDPRT", "AnkleCross": CAD / "Ankle/JX1_AnkleCross.SLDPRT",
    "RodA": CAD / "Ankle/JX1_AnkleRod_A.SLDPRT", "RodB": CAD / "Ankle/JX1_AnkleRod_B.SLDPRT",
}
JR = DP["joint_ranges_deg"]


def refpoint(part_stem, sketch, index):
    """Real SolidWorks selection name of a reference sketch point (recorded when the part was built)."""
    rp = json.loads((ROOT / "verification" / "cad_build_leg_parts.json").read_text())
    return rp[part_stem]["refpoints"][sketch][index]


def sw_transform(s, M4):
    """4x4 homogeneous -> SolidWorks MathTransform (rotation block stored column-major)."""
    R, p = M4[:3, :3], M4[:3, 3]
    arr = list(R.T.flatten()) + list(p) + [1.0, 0.0, 0.0, 0.0]
    return s.math.CreateTransform(var_array(arr))


def from_sw(xf):
    a = np.array(typed(xf, "IMathTransform").ArrayData)
    M4 = np.eye(4)
    M4[:3, :3] = a[:9].reshape(3, 3).T
    M4[:3, 3] = a[9:12]
    return M4


class Assembly:
    def __init__(self, s: Session, path: Path):
        self.s = s
        self.path = Path(path)
        self.doc = s.new_doc("assembly")
        set_mmgs(self.doc)
        save_as(self.doc, self.path)
        self.A = typed(self.doc, "IAssemblyDoc")
        self.ext = typed(self.doc.Extension, "IModelDocExtension")
        self.title = self.path.stem
        self.comp = {}      # key -> IComponent2
        self.names = {}     # key -> Name2
        self.mates = []     # (name, kind, entities, result)
        self.limit_defs = {}  # limit-mate name -> (k1, e1, k2, e2, ref)

    def insert(self, key, part_path, M4):
        part_path = Path(part_path).resolve()
        self.s.open_doc(part_path)
        self.s.activate(self.doc)
        c = self.A.AddComponent5(str(part_path), 0, "", False, "", float(M4[0, 3]), float(M4[1, 3]), float(M4[2, 3]))
        if c is None:
            raise RuntimeError(f"AddComponent5 failed for {part_path}")
        c = typed(c, "IComponent2")
        c.Transform2 = sw_transform(self.s, M4)
        self.comp[key], self.names[key] = c, c.Name2
        return c

    def _sel(self, key, entity, kind, append, mark=1):
        full = f"{entity}@{self.names[key]}@{self.title}"
        ok = self.ext.SelectByID2(full, kind, 0, 0, 0, append, mark, None, 0)
        if not ok and kind == "EXTSKETCHPOINT":
            ok = self.ext.SelectByID2(full, "SKETCHPOINT", 0, 0, 0, append, mark, None, 0)
        if not ok:
            raise RuntimeError(f"cannot select {full} ({kind})")

    def _add(self, name, kind, align=None, angle=0.0, amax=0.0, amin=0.0):
        align = C.swMateAlignCLOSEST if align is None else align
        res = self.A.AddMate5(kind, align, False, 0, 0, 0, 1, 1, angle, amax, amin, False, False, 0)
        obj, err = res if isinstance(res, tuple) else (res, None)
        self.doc.ClearSelection2(True)
        if obj is None or err not in (0, 1, None):
            raise RuntimeError(f"mate {name} failed (err={err})")
        feat = None
        try:
            feat = typed(obj, "IFeature")
            feat.Name = name
        except Exception:
            last = list(self.mate_features().values())[-1]
            last.Name = name
            feat = last
        self.mates.append(name)
        return feat

    def lock(self, k1, k2, name):
        self.doc.ClearSelection2(True)
        self.comp[k1].Select4(False, None, False)
        self.comp[k2].Select4(True, None, False)
        return self._add(name, C.swMateLOCK)

    def coincident(self, k1, e1, t1, k2, e2, t2, name):
        self.doc.ClearSelection2(True)
        self._sel(k1, e1, t1, False)
        self._sel(k2, e2, t2, True)
        return self._add(name, C.swMateCOINCIDENT)

    def _get(self, key, entity, kind):
        self.doc.ClearSelection2(True)
        self._sel(key, entity, kind, False)
        obj = typed(self.doc.SelectionManager, "ISelectionMgr").GetSelectedObject6(1, -1)
        self.doc.ClearSelection2(True)
        return obj

    def limit_angle(self, k1, e1, k2, e2, lo_deg, hi_deg, name, nominal_deg=90.0, ref=None):
        """Limit angle mate between two planes that both contain the joint axis. ref=(key, axis) sets the
        reference direction so the angle is signed; windows must lie inside (0, 180) deg."""
        import pythoncom
        import win32com.client as com
        data = typed(self.A.CreateMateData(C.swMateANGLE), "IAngleMateFeatureData")
        data.EntitiesToMate = com.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH,
                                          [self._get(k1, e1, "PLANE"), self._get(k2, e2, "PLANE")])
        if ref is not None:
            data.ReferenceEntity = self._get(ref[0], ref[1], "AXIS")
        data.Angle = math.radians(nominal_deg)
        data.MinimumAngle = math.radians(lo_deg)
        data.MaximumAngle = math.radians(hi_deg)
        f = self.A.CreateMate(data)
        if f is None:
            raise RuntimeError(f"CreateMate failed for {name}")
        f = typed(f, "IFeature")
        f.Name = name
        self.mates.append(name)
        self.limit_defs[name] = (k1, e1, k2, e2, ref)
        return f

    def delete_feature(self, name):
        self.doc.ClearSelection2(True)
        if self.ext.SelectByID2(name, "MATE", 0, 0, 0, False, 0, None, 0):
            self.doc.EditDelete()
        self.doc.ClearSelection2(True)
        if name in self.mates:
            self.mates.remove(name)

    def mate_features(self):
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

    def mate_errors(self):
        errs = []
        for n, f in self.mate_features().items():
            code = f.GetErrorCode2()
            e = code[0] if isinstance(code, tuple) else code
            if e not in (0, None):
                errs.append((n, e))
        return errs

    def mate_angle_deg(self, name):
        f = self.mate_features()[name]
        dd = f.GetFirstDisplayDimension()
        if dd is None:
            return None
        d = typed(typed(dd, "IDisplayDimension").GetDimension2(0), "IDimension")
        return math.degrees(d.SystemValue)

    def _dim(self, name):
        f = self.mate_features()[name]
        return typed(typed(f.GetFirstDisplayDimension(), "IDisplayDimension").GetDimension2(0), "IDimension")

    def mate_value(self, name):
        return self._dim(name).SystemValue

    def set_mate_value(self, name, rad, rebuild=True):
        self._dim(name).SetSystemValue3(float(rad), C.swSetValue_InThisConfiguration, None)
        if rebuild:
            self.doc.EditRebuild3()

    def set_limits(self, name, lo_deg, hi_deg):
        k1, e1, k2, e2, ref = self.limit_defs[name]
        nominal = math.degrees(self.mate_value(name))
        self.delete_feature(name)
        self.limit_angle(k1, e1, k2, e2, lo_deg, hi_deg, name, nominal_deg=nominal, ref=ref)
        self.doc.EditRebuild3()

    def world(self, key):
        return from_sw(self.comp[key].Transform2)

    def relative(self, parent_key, child_key):
        return np.linalg.inv(self.world(parent_key)) @ self.world(child_key)

    def set_pose(self, poses: dict):
        for key, M4 in poses.items():
            if key in self.comp:
                self.comp[key].Transform2 = sw_transform(self.s, M4)
        self.doc.EditRebuild3()

    def pose_drift(self, poses: dict):
        worst_p, worst_r, who = 0.0, 0.0, None
        for key, M4 in poses.items():
            if key not in self.comp:
                continue
            A_ = from_sw(self.comp[key].Transform2)
            dp = float(np.linalg.norm(A_[:3, 3] - M4[:3, 3]))
            dr = float(np.degrees(np.arccos(np.clip((np.trace(A_[:3, :3].T @ M4[:3, :3]) - 1) / 2, -1, 1))))
            if dp > worst_p or dr > worst_r:
                who = key
            worst_p, worst_r = max(worst_p, dp), max(worst_r, dr)
        return worst_p, worst_r, who


def part_path(key, side):
    return Path(str(PARTS[key]).replace("{S}", "L" if side > 0 else "R"))


# limit-mate plane pairs (parent entity, child entity) and nominal zero-pose angle (deg); both planes contain the joint axis
LIMIT_PLANES = {
    "hip_yaw": ("YawH", "Right Plane", "HipYawBr", "Top Plane", 90.0),
    "hip_roll": ("RollH", "Top Plane", "HipRollBr", "Front Plane", 90.0),
    "hip_pitch": ("PitchH", "Right Plane", "Thigh", "PL_PitchRef", 50.0),
    "knee": ("KneeH", "Right Plane", "Shin", "PL_KneeRef", 22.5),
    "ankle_pitch": ("Shin", "PL_AnkleZ", "Cross", "Right Plane", 90.0),
    "ankle_roll": ("Cross", "Front Plane", "Foot", "Top Plane", 90.0),
}

# actuated joints with limit mates: housing key, output key, robot joint axis (world, zero pose)
ACT_LIMITS = {"hip_yaw": ("YawH", "YawO", np.array([0, 0, 1.0])), "hip_roll": ("RollH", "RollO", np.array([1.0, 0, 0])),
              "hip_pitch": ("PitchH", "PitchO", np.array([0, 1.0, 0])), "knee": ("KneeH", "KneeO", np.array([0, 1.0, 0])),
              "ankle_motorA": ("AnkAH", "AnkAO", np.array([0, 1.0, 0])), "ankle_motorB": ("AnkBH", "AnkBO", np.array([0, 1.0, 0]))}

# reference direction (joint axis in the parent side) for each limit mate
LIMIT_REF = {"hip_yaw": ("YawH", "AX_Joint"), "hip_roll": ("RollH", "AX_Joint"), "hip_pitch": ("PitchH", "AX_Joint"),
             "knee": ("KneeH", "AX_Joint"), "ankle_pitch": ("Shin", "AX_AnklePitch"), "ankle_roll": ("Cross", "AX_Roll")}

JOINT_MATES = [  # joint, housing key, output key
    ("hip_yaw", "YawH", "YawO"), ("hip_roll", "RollH", "RollO"), ("hip_pitch", "PitchH", "PitchO"), ("knee", "KneeH", "KneeO"),
]


def build(sides=("L",), name="JX1_LowerBody"):
    s = Session()
    for d in s.open_documents():
        if d.GetType() == C.swDocASSEMBLY:
            s.close(d)
    asm = Assembly(s, CAD / "Assemblies" / f"{name}.SLDASM")
    asm.insert("Pelvis", PARTS["Pelvis"], np.eye(4))
    legs = {}
    calib_all = {}
    for sd in sides:
        sgn = 1 if sd == "L" else -1
        leg = LegCAD(sgn)
        legs[sd] = leg
        poses = leg.component_poses({})
        for key, (part, link, Tl) in leg.comps.items():
            asm.insert(f"{sd}_{key}", part_path(part, sgn), poses[key])
        for rod in ("RodA", "RodB"):
            asm.insert(f"{sd}_{rod}", part_path(rod, sgn), poses[rod])
        P = lambda k: f"{sd}_{k}"  # noqa: E731
        locks = [("Pelvis", P("YawH")), (P("YawO"), P("HipYawBr")), (P("HipYawBr"), P("RollH")), (P("RollO"), P("HipRollBr")),
                 (P("HipRollBr"), P("PitchH")), (P("PitchO"), P("Thigh")), (P("Thigh"), P("KneeH")), (P("KneeO"), P("Shin")),
                 (P("Shin"), P("AnkAH")), (P("Shin"), P("AnkBH")), (P("AnkAO"), P("CrankA")), (P("AnkBO"), P("CrankB"))]
        for a, b in locks:
            asm.lock(a, b, f"LOCK_{a}_{b}")
        for joint, h, o in JOINT_MATES:
            asm.coincident(P(h), "AX_Joint", "AXIS", P(o), "AX_Joint", "AXIS", f"{sd}_{joint}_AXIS")
            asm.coincident(P(h), "Front Plane", "PLANE", P(o), "Front Plane", "PLANE", f"{sd}_{joint}_FACE")
            pass
        for m, h, o in (("ankle_motorA", "AnkAH", "AnkAO"), ("ankle_motorB", "AnkBH", "AnkBO")):
            asm.coincident(P(h), "AX_Joint", "AXIS", P(o), "AX_Joint", "AXIS", f"{sd}_{m}_AXIS")
            asm.coincident(P(h), "Front Plane", "PLANE", P(o), "Front Plane", "PLANE", f"{sd}_{m}_FACE")
        # passive universal joint at the ankle
        asm.coincident(P("Shin"), "AX_AnklePitch", "AXIS", P("Cross"), "AX_Pitch", "AXIS", f"{sd}_ankle_pitch_AXIS")
        asm.coincident(P("Shin"), "Top Plane", "PLANE", P("Cross"), "Top Plane", "PLANE", f"{sd}_ankle_pitch_MID")
        pass
        asm.coincident(P("Cross"), "AX_Roll", "AXIS", P("Foot"), "AX_Roll", "AXIS", f"{sd}_ankle_roll_AXIS")
        asm.coincident(P("Cross"), "Right Plane", "PLANE", P("Foot"), "Right Plane", "PLANE", f"{sd}_ankle_roll_MID")
        pass
        # push rods: ball joints at both ends
        foot_stem = part_path("Foot", sgn).stem
        for rod, crank, fi in (("RodA", "CrankA", 0), ("RodB", "CrankB", 1)):
            rstem = part_path(rod, sgn).stem
            asm.coincident(P(crank), refpoint("JX1_AnkleCrank", "SK_Ball", 0), "EXTSKETCHPOINT", P(rod), refpoint(rstem, "SK_Ends", 0),
                           "EXTSKETCHPOINT", f"{sd}_{rod}_TOP_BALL")
            asm.coincident(P(rod), refpoint(rstem, "SK_Ends", 1), "EXTSKETCHPOINT", P("Foot"), refpoint(foot_stem, "SK_RodBalls", fi),
                           "EXTSKETCHPOINT", f"{sd}_{rod}_FOOT_BALL")
        # deterministic limit mates: housing Right Plane vs output Top Plane, reference = housing axis.
        # Verified behaviour (tools probe 2026-09-24): SolidWorks value = 90 deg + rotation of the output about +Z_housing.
        zero = leg.component_poses({})
        for joint, (hk, ok_, axis_world) in ACT_LIMITS.items():
            hz = zero[hk][:3, 2]
            sgn = 1 if float(np.dot(hz, axis_world)) > 0 else -1
            kappa = math.degrees(leg.clock.get(ok_, 0.0))
            if joint.startswith("ankle_motor"):
                lo, hi = -75.0, 75.0
            else:
                lo, hi = JR[joint]["min"], JR[joint]["max"]
                if sd == "R" and joint in ("hip_yaw", "hip_roll"):
                    lo, hi = -hi, -lo
            a, b = 90 + kappa + sgn * lo, 90 + kappa + sgn * hi
            win = (min(a, b) - 0.5, max(a, b) + 0.5)          # 0.5 deg margin: commanded limits are not rejected on the boundary
            if win[0] <= 0.5 or win[1] >= 179.5:
                raise RuntimeError(f"{sd} {joint}: window {win} outside (0, 180)")
            asm.limit_angle(P(hk), "Right Plane", P(ok_), "Top Plane", win[0], win[1], f"{sd}_{joint}_LIMIT",
                            nominal_deg=90 + kappa, ref=(P(hk), "AX_Joint"))
            calib_all[f"{sd}_{joint}_LIMIT"] = {"zero_deg": 90 + kappa, "sign": sgn, "sw_limits_deg": win, "robot_limits_deg": (lo, hi)}
    asm.doc.EditRebuild3()
    report = {"assembly": str(asm.path), "components": len(asm.comp), "mates": len(asm.mates), "mate_errors_initial": asm.mate_errors()}
    # ---------------------------------------------------------------- sign check: +0.1 rad robot motion must match the mate model
    calib = calib_all
    check_axes = {"hip_yaw": ("YawH", "YawO", np.array([0, 0, 1.0])), "hip_roll": ("RollH", "RollO", np.array([1.0, 0, 0])),
                  "hip_pitch": ("PitchH", "PitchO", np.array([0, 1.0, 0])), "knee": ("KneeH", "KneeO", np.array([0, 1.0, 0])),
                  "ankle_motorA": ("AnkAH", "AnkAO", np.array([0, 1.0, 0])), "ankle_motorB": ("AnkBH", "AnkBO", np.array([0, 1.0, 0]))}
    for sd in legs:
        for joint, (pk, ck, axis) in check_axes.items():
            mname = f"{sd}_{joint}_LIMIT"
            c = calib[mname]
            R0 = asm.relative(f"{sd}_{pk}", f"{sd}_{ck}")
            asm.set_mate_value(mname, math.radians(c["zero_deg"] + c["sign"] * math.degrees(0.1)))
            R1 = asm.relative(f"{sd}_{pk}", f"{sd}_{ck}")
            asm.set_mate_value(mname, math.radians(c["zero_deg"]))
            dR = R0[:3, :3].T @ R1[:3, :3]
            Rp = asm.world(f"{sd}_{pk}")[:3, :3]
            w = Rp @ np.array([dR[2, 1] - dR[1, 2], dR[0, 2] - dR[2, 0], dR[1, 0] - dR[0, 1]]) / 2.0
            about = float(np.dot(w, axis))
            c["measured_sin_for_+0.1rad"] = about
            c["sign_check_pass"] = abs(about - math.sin(0.1)) < 1e-3
            print(f"CHECK {mname}: +0.1 rad robot -> measured {about:+.5f} (expect +0.09983) {'OK' if c['sign_check_pass'] else 'FAIL'}", flush=True)
    report["limit_calibration"] = calib
    asm.doc.EditRebuild3()
    report["mate_errors_final"] = asm.mate_errors()
    asm.doc.ShowNamedView2("*Isometric", 7)
    asm.doc.ViewZoomtofit2()
    save_as(asm.doc, asm.path)
    report["names"] = asm.names
    (ROOT / "verification" / f"{name}_build.json").write_text(json.dumps(report, indent=2, default=str))
    return asm, legs, report


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sides", default="L")
    ap.add_argument("--name", default="JX1_LowerBody")
    a = ap.parse_args()
    t0 = time.time()
    asm, legs, rep = build(tuple(a.sides), a.name)
    print(json.dumps({k: v for k, v in rep.items() if k not in ("names",)}, indent=1, default=str)[:4000])
    print(f"built in {time.time() - t0:.0f} s")
