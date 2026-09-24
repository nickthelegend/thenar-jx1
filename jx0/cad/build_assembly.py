"""Assemble JX0 in SolidWorks at its zero pose: every printed part in its link frame and a servo stand-in at every joint.

The link frames are those of the simulation model (jx0/sim/jx0_model.py): hip centres at y = +-45 mm, knee 100 mm
and ankle 200 mm below them; arms and head from jx0/cad/geometry.py. Components are placed by transform (no mates yet)
and the assembly is checked for interferences between parts that are not bolted together.
Output: jx0/cad/JX0_Robot.SLDASM, jx0/cad/assembly.json (component poses, interference report), images.
Usage: .venv/Scripts/python jx0/cad/build_assembly.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "cad"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from swlib.core import Session, save_as, set_mmgs, set_view, typed  # noqa: E402
from build_leg_assembly import sw_transform  # noqa: E402
import geometry as G  # noqa: E402

PARTS = ROOT / "jx0" / "cad" / "parts"
OUT = ROOT / "jx0" / "cad" / "JX0_Robot.SLDASM"
MM = 1e-3


def pose(R=None, p=(0, 0, 0)):
    M = np.eye(4)
    if R is not None:
        M[:3, :3] = np.column_stack(R)          # columns = child axes in the parent frame
    M[:3, 3] = np.asarray(p, float) * MM
    return M


def servo_axes(x_dir, z_dir):
    """Rotation whose columns are the servo x (case length), y and z (horn) axes in the parent frame."""
    x, z = np.asarray(x_dir, float), np.asarray(z_dir, float)
    return (x, np.cross(z, x), z)


def components():
    """(key, part file, 4x4 pose in the pelvis frame) at the zero pose."""
    hf = G.ST["HORN_FACE"]
    comps = [("pelvis", "JX0_Pelvis", pose()), ("torso", "JX0_Torso", pose()),
             ("head", "JX0_Head", pose(p=(0, 0, G.NECK_Z + 1.5)))]
    for side, sg in (("L", 1), ("R", -1)):
        hip = np.array([0.0, sg * G.HIP_Y, 0.0])
        knee, ankle = hip + [0, 0, -G.THIGH], hip + [0, 0, -G.THIGH - G.SHIN]
        comps += [(f"hip_yaw_{side}", f"JX0_HipYawBracket_{side}", pose(p=hip)),
                  (f"hip_roll_{side}", f"JX0_HipRollBracket_{side}", pose(p=hip)),
                  (f"thigh_{side}", f"JX0_Thigh_{side}", pose(p=hip)),
                  (f"shin_{side}", f"JX0_Shin_{side}", pose(p=knee)),
                  (f"ankle_{side}", f"JX0_AnkleBracket_{side}", pose(p=ankle)),
                  (f"foot_{side}", "JX0_Foot", pose(p=ankle))]
        st = "JX0_Servo_ST3215"
        comps += [
            (f"servo_hip_yaw_{side}", st, pose(servo_axes((1, 0, 0), (0, 0, -1)), hip + [0, 0, G.ZY + hf])),
            (f"servo_hip_roll_{side}", st, pose(servo_axes((0, -sg, 0), (1, 0, 0)), hip + [G.XR - hf, 0, 0])),
            (f"servo_hip_pitch_{side}", st, pose(servo_axes((1, 0, 0), (0, sg, 0)), hip)),
            (f"servo_knee_{side}", st, pose(servo_axes((0, 0, 1), (0, -sg, 0)), knee + [0, sg * (-16.0 + hf) * 1, 0])),
            (f"servo_ankle_pitch_{side}", st, pose(servo_axes((0, 0, 1), (0, sg, 0)), ankle)),
            (f"servo_ankle_roll_{side}", st, pose(servo_axes((0, -sg, 0), (1, 0, 0)), ankle + [G.XA - hf, 0, 0])),
        ]
        sh = np.array([G.SHOULDER[0], sg * G.SHOULDER[1], G.SHOULDER[2]])
        ua = sh + [0, sg * 10.0, -16.0]
        fa = ua + [8.0, 0, -55.0]
        comps += [(f"shoulder_{side}", f"JX0_ShoulderBracket_{side}", pose(p=sh)),
                  (f"upper_arm_{side}", "JX0_UpperArm", pose(p=ua)),
                  (f"forearm_{side}", f"JX0_Forearm_{side}", pose(p=fa))]
        mg = "JX0_Servo_MG90S"
        spline = G.MG["H"] / 2 + G.MG["SPLINE"]
        comps += [
            (f"servo_shoulder_pitch_{side}", mg, pose(servo_axes((1, 0, 0), (0, sg, 0)), sh + [0, sg * 1.5, 0])),
            (f"servo_shoulder_roll_{side}", mg, pose(servo_axes((0, 0, -1), (1, 0, 0)), ua + [15.4, 0, 0])),
            (f"servo_elbow_{side}", mg, pose(servo_axes((0, 0, 1), (0, sg, 0)), fa + [0, sg * spline, 0])),
        ]
    comps.append(("servo_neck", "JX0_Servo_MG90S", pose(servo_axes((-1, 0, 0), (0, 0, 1)), (0, 0, G.NECK_Z + 1.5))))
    return comps


def main():
    s = Session()
    doc = s.new_doc("assembly")
    set_mmgs(doc)
    save_as(doc, OUT)
    A = typed(doc, "IAssemblyDoc")
    placed = []
    for key, part, M in components():
        path = (PARTS / f"{part}.SLDPRT").resolve()
        s.open_doc(path)
        s.activate(doc)
        c = A.AddComponent5(str(path), 0, "", False, "", float(M[0, 3]), float(M[1, 3]), float(M[2, 3]))
        if c is None:
            raise RuntimeError(f"AddComponent5 failed for {part}")
        c = typed(c, "IComponent2")
        c.Transform2 = sw_transform(s, M)
        placed.append({"key": key, "part": part, "name": c.Name2, "pose_mm": (M[:3, 3] / MM).round(3).tolist(),
                       "R": M[:3, :3].round(6).tolist()})
        s.close(path.name)
        print(f"placed {key:26s} {part}", flush=True)
        if len(placed) % 6 == 0:
            set_view(s.app, doc, eye=(1.0, -0.8, 0.45))
    doc.ForceRebuild3(False)
    set_view(s.app, doc, eye=(1.0, -0.8, 0.45))
    save_as(doc, OUT)
    (ROOT / "jx0" / "cad" / "assembly.json").write_text(json.dumps({"assembly": str(OUT.relative_to(ROOT)).replace("\\", "/"),
                                                                     "components": placed}, indent=1), encoding="utf-8")
    print(f"saved {OUT.relative_to(ROOT)} with {len(placed)} components")


if __name__ == "__main__":
    main()
