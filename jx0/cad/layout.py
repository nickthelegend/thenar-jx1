"""JX0 component layout at the zero pose (no SolidWorks dependency): which part / servo stand-in sits where.

Used by the SolidWorks assembly (build_assembly.py), the simulation model (jx0/sim/jx0_model.py) and preview.py, so all
three place the same meshes at the same poses. Poses are 4x4 in the pelvis frame, metres. Every joint is an STS3215.
"""
from __future__ import annotations

import numpy as np

import geometry as G

MM = 1e-3
ST = "JX0_Servo_STS3215"


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


def arm_points(sg):
    """Shoulder-pitch horn face and elbow horn face (mm, pelvis frame) of one arm; sg = +1 left, -1 right."""
    sx, sy, sz = G.SHOULDER
    return np.array([sx, sg * sy, sz]), np.array([sx, sg * (sy + G.ELBOW_Y), sz - G.UA_L])


def components():
    """(key, part file, 4x4 pose in the pelvis frame) at the zero pose."""
    hf = G.ST["HORN_FACE"]
    comps = [("pelvis", "JX0_Pelvis", pose()), ("torso", "JX0_Torso", pose()), ("chest_cap", "JX0_ChestCap", pose()),
             ("head", "JX0_Head", pose(p=(0, 0, G.NECK_Z))),
             ("lens_L", "JX0_EyeLens", pose(p=(G.HEAD_BOX[1] - G.LENS_T, G.EYE[0], G.NECK_Z + G.EYE[1]))),
             ("lens_R", "JX0_EyeLens", pose(p=(G.HEAD_BOX[1] - G.LENS_T, -G.EYE[0], G.NECK_Z + G.EYE[1]))),
             ("neck_hub", "JX0_NeckHub", pose(p=(0, 0, G.NECK_Z))),
             ("servo_neck", ST, pose(servo_axes((0, 1, 0), (0, 0, 1)), (0, 0, G.NECK_Z - hf)))]
    for side, sg in (("L", 1), ("R", -1)):
        hip = np.array([0.0, sg * G.HIP_Y, 0.0])
        knee, ankle = hip + [0, 0, -G.THIGH], hip + [0, 0, -G.THIGH - G.SHIN]
        comps += [(f"keeper_{side}", f"JX0_YawKeeper_{side}", pose(p=hip)),
                  (f"yaw_ring_{side}", f"JX0_YawRing_{side}", pose(p=hip)),
                  (f"hip_yaw_{side}", f"JX0_HipYawBracket_{side}", pose(p=hip)),
                  (f"hip_roll_{side}", f"JX0_HipRollBracket_{side}", pose(p=hip)),
                  (f"thigh_{side}", f"JX0_Thigh_{side}", pose(p=hip)),
                  (f"shin_{side}", f"JX0_Shin_{side}", pose(p=knee)),
                  (f"ankle_{side}", f"JX0_AnkleBracket_{side}", pose(p=ankle)),
                  (f"foot_{side}", "JX0_Foot", pose(p=ankle))]
        comps += [
            (f"servo_hip_yaw_{side}", ST, pose(servo_axes((0, -sg, 0), (0, 0, -1)), hip + [0, 0, G.ZY + hf + G.YAW_SEAT])),
            (f"servo_hip_roll_{side}", ST, pose(servo_axes((0, -sg, 0), (1, 0, 0)), hip + [G.XR - hf, 0, 0])),
            (f"servo_hip_pitch_{side}", ST, pose(servo_axes((1, 0, 0), (0, sg, 0)), hip)),
            (f"servo_knee_{side}", ST, pose(servo_axes((1, 0, 0), (0, sg, 0)), knee)),          # lying forward
            (f"servo_ankle_pitch_{side}", ST, pose(servo_axes((0, 0, 1), (0, sg, 0)), ankle)),
            (f"servo_ankle_roll_{side}", ST, pose(servo_axes((0, -sg, 0), (1, 0, 0)), ankle + [G.XA - hf, 0, 0])),
        ]
        sh, el = arm_points(sg)
        comps += [(f"upper_arm_{side}", f"JX0_UpperArm_{side}", pose(p=sh)),
                  (f"blade_{side}", f"JX0_ArmBlade_{side}", pose(p=el)),
                  # shoulder pitch: outside the chest in the arm's hood, horn on the chest pad, case down
                  (f"servo_shoulder_pitch_{side}", ST, pose(servo_axes((0, 0, -1), (0, -sg, 0)), sh + [0, sg * hf, 0])),
                  # elbow: in the box under the shoulder servo, lying forward, horn outward
                  (f"servo_elbow_{side}", ST, pose(servo_axes((1, 0, 0), (0, sg, 0)), el - [0, sg * hf, 0]))]
    return comps


# link (MuJoCo body) of every component and that link's origin in the pelvis frame at the zero pose (mm)
def link_of(key):
    side = key[-1] if key[-2:] in ("_L", "_R") else ""
    sg = 1 if side == "L" else -1
    s = side.lower()
    hip = np.array([0.0, sg * G.HIP_Y, 0.0])
    knee, ankle = hip + [0, 0, -G.THIGH], hip + [0, 0, -G.THIGH - G.SHIN]
    sh, el = arm_points(sg)
    base = key[:-2] if side else key
    table = {"pelvis": ("pelvis", (0, 0, 0)), "torso": ("torso", (0, 0, 0)), "chest_cap": ("torso", (0, 0, 0)),
             "servo_neck": ("torso", (0, 0, 0)), "head": ("head", (0, 0, G.NECK_Z)), "lens": ("head", (0, 0, G.NECK_Z)), "neck_hub": ("head", (0, 0, G.NECK_Z)),
             "servo_hip_yaw": ("pelvis", (0, 0, 0)), "keeper": ("pelvis", (0, 0, 0)), "yaw_ring": ("pelvis", (0, 0, 0)),
             "hip_yaw": (f"{s}_hip_yaw_link", hip), "servo_hip_roll": (f"{s}_hip_yaw_link", hip),
             "hip_roll": (f"{s}_hip_roll_link", hip), "servo_hip_pitch": (f"{s}_hip_roll_link", hip),
             "thigh": (f"{s}_thigh", hip), "servo_knee": (f"{s}_thigh", hip),
             "shin": (f"{s}_shin", knee), "servo_ankle_pitch": (f"{s}_shin", knee),
             "ankle": (f"{s}_ankle_cross", ankle), "servo_ankle_roll": (f"{s}_ankle_cross", ankle),
             "foot": (f"{s}_foot", ankle),
             "servo_shoulder_pitch": (f"{s}_upper_arm", sh), "upper_arm": (f"{s}_upper_arm", sh),
             "servo_elbow": (f"{s}_upper_arm", sh), "blade": (f"{s}_forearm", el)}
    link, origin = table[base]
    return link, np.asarray(origin, float)


# how each servo's cables leave it (geometry.servo_cables): "straight" out of the rear face through the plate it stands
# on (the hip-yaw servos up through the pelvis plate and the torso floor, the neck servo down into the chest, the
# shoulder servos out through the arm's outer plate); "back": bent along the rear face over the label block, then out
# through the cage plate's window (the ankle-roll servos: the other foot passes their inboard end in side steps);
# every other servo's cables are bent flat along its rear face and leave past the far end of its cage ("bent")
CABLE_MODE = {"servo_hip_yaw": "straight", "servo_neck": "straight", "servo_shoulder_pitch": "straight",
              "servo_ankle_roll": "back"}


def cable_mode(key):
    return CABLE_MODE.get(base(key), "bent")


# the part bolted to each servo's horns (the next link); the servo's case sits in a cage on its own link
HORN_PART = {"servo_hip_yaw": "hip_yaw", "servo_hip_roll": "hip_roll", "servo_hip_pitch": "thigh", "servo_knee": "shin",
             "servo_ankle_pitch": "ankle", "servo_ankle_roll": "foot", "servo_shoulder_pitch": "chest_cap",
             "servo_elbow": "blade", "servo_neck": "neck_hub"}


def base(key):
    return key[:-2] if key[-2:] in ("_L", "_R") else key


def keepouts():
    """Volumes that must stay free (not built, checked by verify_cad / verify_fit): (key, primitives, 4x4 pose in the
    pelvis frame (m), the component they move with). Each servo's cables, and the head of every screw."""
    out = []
    comps = components()
    for key, part, M in comps:
        if part == ST:
            out.append((f"cables:{key}", G.servo_cables(cable_mode(key)), M, key))
        elif G.SCREWS.get(part):
            out.append((f"screws:{key}", [q for s in G.SCREWS[part] for q in G.screw_head(s)], M, key))
    return out
