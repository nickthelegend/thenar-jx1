"""JX0 component layout at the zero pose (no SolidWorks dependency): which part / servo stand-in sits where.

Used by the SolidWorks assembly (build_assembly.py) and the simulation model (jx0/sim/jx0_model.py), so both place the
same meshes at the same poses. Poses are 4x4 in the pelvis frame, metres.
"""
from __future__ import annotations

import numpy as np

import geometry as G

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
    head = pose(p=(0, 0, G.NECK_Z + 1.5))
    comps = [("pelvis", "JX0_Pelvis", pose()), ("torso", "JX0_Torso", pose()),
             ("head", "JX0_Head", head), ("display", "JX0_Display_GC9A01", head), ("screen_face", "JX0_Screen_Face", head)]
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
        ua = sh + [0, sg * G.ARM_Y, -16.0]
        fa = ua + [8.0, 0, -55.0]
        comps += [(f"shoulder_{side}", f"JX0_ShoulderBracket_{side}", pose(p=sh)),
                  (f"upper_arm_{side}", "JX0_UpperArm", pose(p=ua)),
                  (f"forearm_{side}", f"JX0_Forearm_{side}", pose(p=fa)),
                  (f"finger_{side}", f"JX0_Finger_{side}", pose(p=fa + [0, sg * G.GRIP_Y, G.GRIP_Z]))]
        mg = "JX0_Servo_MG90S"
        spline = G.MG["H"] / 2 + G.MG["SPLINE"]
        comps += [
            (f"servo_shoulder_pitch_{side}", mg, pose(servo_axes((1, 0, 0), (0, sg, 0)), sh + [0, sg * 1.5, 0])),
            (f"servo_shoulder_roll_{side}", mg, pose(servo_axes((0, 0, -1), (1, 0, 0)), ua + [15.4, 0, 0])),
            (f"servo_elbow_{side}", mg, pose(servo_axes((0, 0, 1), (0, sg, 0)), fa + [0, sg * spline, 0])),
            (f"servo_grip_{side}", mg, pose(servo_axes((0, 0, 1), (0, -sg, 0)), fa + [0, sg * G.GRIP_Y, G.GRIP_Z])),
        ]
    comps.append(("servo_neck", "JX0_Servo_MG90S", pose(servo_axes((-1, 0, 0), (0, 0, 1)), (0, 0, G.NECK_Z + 1.5))))
    return comps




# link (MuJoCo body) of every component and that link's origin in the pelvis frame at the zero pose (mm)
def link_of(key):
    side = key[-1] if key[-2:] in ("_L", "_R") else ""
    sg = 1 if side == "L" else -1
    s = side.lower()
    hip = np.array([0.0, sg * G.HIP_Y, 0.0])
    knee, ankle = hip + [0, 0, -G.THIGH], hip + [0, 0, -G.THIGH - G.SHIN]
    sh = np.array([G.SHOULDER[0], sg * G.SHOULDER[1], G.SHOULDER[2]])
    ua = sh + [0, sg * G.ARM_Y, -16.0]
    fa = ua + [8.0, 0, -55.0]
    base = key[:-2] if side else key
    table = {"pelvis": ("pelvis", (0, 0, 0)), "torso": ("torso", (0, 0, 0)), "head": ("head", (0, 0, G.NECK_Z + 1.5)),
             "servo_neck": ("torso", (0, 0, 0)), "servo_hip_yaw": ("pelvis", (0, 0, 0)),
             "hip_yaw": (f"{s}_hip_yaw_link", hip), "servo_hip_roll": (f"{s}_hip_yaw_link", hip),
             "hip_roll": (f"{s}_hip_roll_link", hip), "servo_hip_pitch": (f"{s}_hip_roll_link", hip),
             "thigh": (f"{s}_thigh", hip), "servo_knee": (f"{s}_thigh", hip),
             "shin": (f"{s}_shin", knee), "servo_ankle_pitch": (f"{s}_shin", knee),
             "ankle": (f"{s}_ankle_cross", ankle), "servo_ankle_roll": (f"{s}_ankle_cross", ankle),
             "foot": (f"{s}_foot", ankle),
             "servo_shoulder_pitch": ("torso", (0, 0, 0)), "shoulder": (f"{s}_shoulder", sh),
             "servo_shoulder_roll": (f"{s}_shoulder", sh), "upper_arm": (f"{s}_upper_arm", ua),
             "servo_elbow": (f"{s}_upper_arm", ua), "forearm": (f"{s}_forearm", fa),
             "servo_grip": (f"{s}_forearm", fa), "finger": (f"{s}_finger", fa + [0, sg * G.GRIP_Y, G.GRIP_Z]),
             "display": ("head", (0, 0, G.NECK_Z + 1.5)), "screen_face": ("head", (0, 0, G.NECK_Z + 1.5))}
    link, origin = table[base]
    return link, np.asarray(origin, float)
