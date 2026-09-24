"""Build the articulated JX1 upper-body assembly (phase 2) in SolidWorks: JX1_UpperBody.SLDASM.

Frame = pelvis frame, so the assembly drops into JX1_Robot.SLDASM next to JX1_LowerBody.SLDASM with an identity
transform. The pelvis is included (fixed) so that arm-to-pelvis contacts are caught by the interference checks.
Joints (11): waist yaw, 2 x (shoulder pitch/roll/yaw, elbow), neck yaw/pitch — each is axis + face coincident mates
between actuator housing and output plus a limit-angle mate (housing Right Plane vs output Top Plane, reference = housing
axis). Calibration (same verified convention as the legs): mate value = 90 deg + output clocking + sign * joint angle,
checked by commanding +0.1 rad on every joint and measuring the rotation about the robot joint axis.
Usage: .venv/Scripts/python tools/cad/build_upper_assembly.py
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from swlib.core import C, Session, save_as  # noqa: E402
from cad.params import ROOT  # noqa: E402
from cad.build_leg_assembly import Assembly  # noqa: E402
from cad.upper_kinematics import UpperCAD, ACTUATED, cad_limits_deg  # noqa: E402

CAD = ROOT / "CAD"
FILES = {"Pelvis": CAD / "Pelvis" / "JX1_Pelvis.SLDPRT", "Torso": CAD / "Torso" / "JX1_Torso.SLDPRT",
         "Gripper": CAD / "Arms" / "JX1_Gripper.SLDPRT", "NeckBracket": CAD / "Head" / "JX1_NeckBracket.SLDPRT",
         "Head": CAD / "Head" / "JX1_Head.SLDPRT", "StereoCamera": CAD / "Head" / "JX1_StereoCamera.SLDPRT",
         "Servo_ST3215_Body": CAD / "Head" / "JX1_Servo_ST3215_Body.SLDPRT", "Servo_ST3215_Horn": CAD / "Head" / "JX1_Servo_ST3215_Horn.SLDPRT"}
for _e in ("BatteryPack", "JetsonNano", "HubBoard", "DCDC5V", "EStop", "PowerSwitch"):
    FILES[_e] = CAD / "Electronics" / f"JX1_{_e}.SLDPRT"


def part_file(key, part):
    if part.startswith("ACT_"):
        return CAD / "Actuators" / f"JX1_{part}.SLDPRT"
    if part in ("ShoulderPitchBracket", "ShoulderRollBracket", "UpperArm", "Forearm"):
        return CAD / "Arms" / f"JX1_{part}_{key[0]}.SLDPRT"
    return FILES[part]


LOCKS = [("Pelvis", "WaistH"), ("WaistO", "Torso"), ("Torso", "NeckYawS"), ("NeckYawH", "NeckBr"), ("NeckBr", "NeckPitchS"),
         ("NeckPitchH", "Head"), ("Head", "Camera")]
LOCKS += [("Torso", e) for e in ("BatteryPack", "JetsonNano", "HubBoard", "DCDC5V", "EStop", "PowerSwitch")]
for _s in ("L", "R"):
    LOCKS += [("Torso", f"{_s}_SPH"), (f"{_s}_SPO", f"{_s}_ShPitchBr"), (f"{_s}_ShPitchBr", f"{_s}_SRH"), (f"{_s}_SRO", f"{_s}_ShRollBr"),
              (f"{_s}_ShRollBr", f"{_s}_SYH"), (f"{_s}_SYO", f"{_s}_UpperArm"), (f"{_s}_UpperArm", f"{_s}_ElH"), (f"{_s}_ElO", f"{_s}_Forearm"),
              (f"{_s}_Forearm", f"{_s}_Gripper")]


def add_upper(asm, include_pelvis=True, tag=""):
    """Insert and mate the upper body into an open Assembly (pelvis frame). Returns the limit calibration dict."""
    uc = UpperCAD()
    poses = uc.component_poses({})
    if include_pelvis:
        asm.insert("Pelvis", FILES["Pelvis"], np.eye(4))
    for key, (part, link, _) in uc.comps.items():
        if key != "Pelvis":
            asm.insert(key, part_file(key, part), poses[key])
    for a, b in LOCKS:
        asm.lock(a, b, f"LOCK_{a}_{b}")
    calib = {}
    W0 = uc.links({})
    for joint, hk, ok, axis in ACTUATED:
        asm.coincident(hk, "AX_Joint", "AXIS", ok, "AX_Joint", "AXIS", f"{joint}_AXIS")
        asm.coincident(hk, "Front Plane", "PLANE", ok, "Front Plane", "PLANE", f"{joint}_FACE")
        parent = uc.comps[hk][1]
        hz = poses[hk][:3, 2]
        ax = W0[parent][:3, :3] @ np.array(axis, float)
        sgn = 1 if float(hz @ ax) > 0 else -1
        kappa = math.degrees(uc.clock[ok])
        lo, hi = cad_limits_deg(joint)
        a_, b_ = 90 + kappa + sgn * lo, 90 + kappa + sgn * hi
        win = (min(a_, b_) - 0.5, max(a_, b_) + 0.5)
        if win[0] <= 0.5 or win[1] >= 179.5:
            raise RuntimeError(f"{joint}: window {win} outside (0, 180)")
        asm.limit_angle(hk, "Right Plane", ok, "Top Plane", win[0], win[1], f"{joint}_LIMIT", nominal_deg=90 + kappa, ref=(hk, "AX_Joint"))
        calib[f"{joint}_LIMIT"] = {"joint": joint, "housing": hk, "output": ok, "axis_parent": list(axis), "zero_deg": 90 + kappa,
                                   "sign": sgn, "sw_limits_deg": win, "cad_limits_deg": (lo, hi), "parent_link": parent}
    asm.doc.EditRebuild3()
    # sign check: +0.1 rad in the robot convention must rotate the output by +0.1 rad about the robot joint axis
    for mname, c in calib.items():
        hk, ok = c["housing"], c["output"]
        R0 = asm.relative(hk, ok)
        asm.set_mate_value(mname, math.radians(c["zero_deg"] + c["sign"] * math.degrees(0.1)))
        R1 = asm.relative(hk, ok)
        asm.set_mate_value(mname, math.radians(c["zero_deg"]))
        dR = R0[:3, :3].T @ R1[:3, :3]
        Rh = asm.world(hk)[:3, :3]
        w = Rh @ np.array([dR[2, 1] - dR[1, 2], dR[0, 2] - dR[2, 0], dR[1, 0] - dR[0, 1]]) / 2.0
        ax_world = W0[c["parent_link"]][:3, :3] @ np.array(c["axis_parent"], float)
        about = float(np.dot(w, ax_world))
        c["measured_sin_for_+0.1rad"] = about
        c["sign_check_pass"] = abs(about - math.sin(0.1)) < 1e-3
        print(f"CHECK {mname}: +0.1 rad robot -> measured {about:+.5f} (expect +0.09983) {'OK' if c['sign_check_pass'] else 'FAIL'}", flush=True)
    asm.doc.EditRebuild3()
    return calib


def build(name="JX1_UpperBody"):
    s = Session()
    for d in s.open_documents():
        if d.GetType() == C.swDocASSEMBLY:
            s.close(d)
    asm = Assembly(s, CAD / "Assemblies" / f"{name}.SLDASM")
    calib = add_upper(asm, include_pelvis=True)
    report = {"assembly": str(asm.path), "components": len(asm.comp), "mates": len(asm.mates), "limit_calibration": calib,
              "mate_errors_final": asm.mate_errors()}
    asm.doc.ShowNamedView2("*Isometric", 7)
    asm.doc.ViewZoomtofit2()
    save_as(asm.doc, asm.path)
    report["names"] = asm.names
    (ROOT / "verification" / f"{name}_build.json").write_text(json.dumps(report, indent=2, default=str))
    return asm, report


if __name__ == "__main__":
    asm, rep = build()
    ok = all(c["sign_check_pass"] for c in rep["limit_calibration"].values())
    print(f"components {rep['components']}, mates {rep['mates']}, mate errors {rep['mate_errors_final']}, sign checks {'ALL OK' if ok else 'FAILED'}")
