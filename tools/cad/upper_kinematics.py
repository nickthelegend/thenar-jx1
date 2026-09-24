"""JX1 upper-body CAD kinematics: link frames and component poses in the pelvis frame (mirrors simulation/joint_map.yaml).

Actuator frames follow the Modular Actuator Interface convention (tools/cad/params.py): +Z = joint axis out of the
output face, output mounting face at z = T_OUT, housing in z in [-L_HOUSING, 0]. Placement decisions (UPK below) are
packaging values verified by interference checks (tools/cad/verify_upper_motion.py).
"""
from __future__ import annotations

import numpy as np

from cad.leg_kinematics import T, rx, ry, rz
from cad.params import ACT, DP, PKG

UB = DP["upper_body_geometry"]
UR = DP["upper_body_joint_ranges_deg"]


def _v(key):
    return np.array(UB[key]["value"], float)


WAIST_O = _v("waist_yaw_origin")
SH_O = _v("shoulder_pitch_origin")          # left; right mirrors y
SR_OFF = _v("shoulder_roll_offset")
SY_OFF = _v("shoulder_yaw_offset")
EL_OFF = _v("elbow_offset")
HAND_OFF = _v("hand_offset")
NY_O = _v("neck_yaw_origin")
NP_OFF = _v("neck_pitch_offset")
S, XS, M = ACT["S"], ACT["XS"], ACT["M"]

# packaging (PKG-style, CAD only)
UPK = {
    "roll_out_x": -0.040,        # shoulder-roll output face x in the roll frame (actuator behind the shoulder centre, faces +x);
                                 # -40 mm keeps the roll plate 5.5 mm behind the RS00 shoulder-yaw housing (r 28.5 mm)
    "servo_body": (0.04522, 0.02472, 0.035),   # Waveshare ST3215 envelope L x W x H (VERIFIED: waveshare.com)
    "servo_axis_from_end": 0.0125,             # output spline centre from the short end (ASSUMED from drawings)
    "horn_d": 0.020, "horn_t": 0.003,
    "neck_pitch_face_y": 0.0175,               # pitch-servo horn face y (body centred on the neck axis)
    "elbow_face_y": 0.0255,                    # elbow (RS00) output face |y| in the upper-arm frame: housing centred on the arm
}

JOINTS = ["waist_yaw", "neck_yaw", "neck_pitch"] + [f"{s}_{j}" for s in ("left", "right")
                                                  for j in ("shoulder_pitch", "shoulder_roll", "shoulder_yaw", "elbow")]


def limits_deg(joint):
    """Robot joint limits (deg) in the joint_map convention; right-arm roll mirrors the left."""
    base = joint.split("_", 1)[1] if joint.startswith(("left_", "right_")) else joint
    lo, hi = UR[base]["min"], UR[base]["max"]
    if joint.startswith("right_") and base == "shoulder_roll":
        lo, hi = -hi, -lo
    return lo, hi


# SolidWorks limit-angle mates only accept windows inside (0, 180) deg: the CAD window for the shoulder pitch (230 deg robot
# range) is limited to CAD_WINDOW; every other joint uses its full robot range (yaw/waist trimmed to +-88 deg)
CAD_WINDOW = {"shoulder_pitch": (-115.0, 60.0), "shoulder_yaw": (-88.0, 88.0), "waist_yaw": (-88.0, 88.0)}


def cad_limits_deg(joint):
    base = joint.split("_", 1)[1] if joint.startswith(("left_", "right_")) else joint
    lo, hi = limits_deg(joint)
    if base in CAD_WINDOW:
        wlo, whi = CAD_WINDOW[base]
        lo, hi = max(lo, wlo), min(hi, whi)
    return lo, hi


class UpperCAD:
    def __init__(self):
        self.comps = {}          # key -> (part name, link, local 4x4)
        self.clock = {}          # output key -> clocking about its own +Z (rad): centres each limit-mate window on 90 deg
        wz = M["T_OUT"]
        self.comps["Pelvis"] = ("Pelvis", "pelvis", T())
        self.comps["WaistH"] = ("ACT_M_Housing", "pelvis", T(None, WAIST_O - [0, 0, wz]))
        self.comps["WaistO"] = ("ACT_M_Output", "torso", T(None, [0, 0, -wz]))
        self.comps["Torso"] = ("Torso", "torso", T())
        for e in ("BatteryPack", "JetsonNano", "HubBoard", "DCDC5V", "EStop", "PowerSwitch"):
            self.comps[e] = (e, "torso", T())
        for side, s in (("L", 1), ("R", -1)):
            R_out = rx(-np.pi / 2) if s > 0 else rx(np.pi / 2)          # +Z_act pointing laterally outward
            self.comps[f"{side}_SPH"] = ("ACT_S_Housing", "torso", T(R_out, SH_O * [1, s, 1] - [0, s * S["T_OUT"], 0]))
            self.comps[f"{side}_SPO"] = ("ACT_S_Output", f"{side}_shoulder_pitch", T(R_out, [0, -s * S["T_OUT"], 0]))
            self.comps[f"{side}_ShPitchBr"] = ("ShoulderPitchBracket", f"{side}_shoulder_pitch", T())
            xr = UPK["roll_out_x"] - S["T_OUT"]
            self.comps[f"{side}_SRH"] = ("ACT_S_Housing", f"{side}_shoulder_pitch", T(ry(np.pi / 2), [xr, s * SR_OFF[1], 0]))
            self.comps[f"{side}_SRO"] = ("ACT_S_Output", f"{side}_shoulder_roll", T(ry(np.pi / 2), [xr, 0, 0]))
            self.comps[f"{side}_ShRollBr"] = ("ShoulderRollBracket", f"{side}_shoulder_roll", T())
            zy = SY_OFF[2] + XS["T_OUT"]
            self.comps[f"{side}_SYH"] = ("ACT_XS_Housing", f"{side}_shoulder_roll", T(rx(np.pi), [0, 0, zy]))
            self.comps[f"{side}_SYO"] = ("ACT_XS_Output", f"{side}_upper_arm", T(rx(np.pi), [0, 0, XS["T_OUT"]]))
            self.comps[f"{side}_UpperArm"] = ("UpperArm", f"{side}_upper_arm", T())
            ye = s * (UPK["elbow_face_y"] - XS["T_OUT"])
            self.comps[f"{side}_ElH"] = ("ACT_XS_Housing", f"{side}_upper_arm", T(R_out, [0, ye, EL_OFF[2]]))
            self.comps[f"{side}_ElO"] = ("ACT_XS_Output", f"{side}_forearm", T(R_out, [0, ye, 0]))
            self.comps[f"{side}_Forearm"] = ("Forearm", f"{side}_forearm", T())
            self.comps[f"{side}_Gripper"] = ("Gripper", f"{side}_hand", T())
        self.comps["NeckYawS"] = ("Servo_ST3215_Body", "torso", T(None, NY_O))
        self.comps["NeckYawH"] = ("Servo_ST3215_Horn", "neck", T())
        self.comps["NeckBr"] = ("NeckBracket", "neck", T())
        yf = UPK["neck_pitch_face_y"]
        self.comps["NeckPitchS"] = ("Servo_ST3215_Body", "neck", T(rx(-np.pi / 2), [0, yf, NP_OFF[2]]))
        self.comps["NeckPitchH"] = ("Servo_ST3215_Horn", "head", T(rx(-np.pi / 2), [0, yf, 0]))
        self.comps["Head"] = ("Head", "head", T())
        self.comps["Camera"] = ("StereoCamera", "head", T())

        # output clocking: kappa = -sign * (window centre); sign = +1 when the actuator +Z is along the robot joint axis
        W0 = self.links({})
        for joint, hk, ok, axis in ACTUATED:
            parent = self.comps[hk][1]
            hz = (W0[parent] @ self.comps[hk][2])[:3, 2]
            ax = W0[parent][:3, :3] @ np.array(axis, float)
            sgn = 1.0 if float(hz @ ax) > 0 else -1.0
            lo, hi = cad_limits_deg(joint)
            kappa = -sgn * np.radians((lo + hi) / 2)
            part, link, Tl = self.comps[ok]
            self.comps[ok] = (part, link, Tl @ T(rz(kappa)))
            self.clock[ok] = kappa

    def links(self, q):
        """q: dict joint -> angle (rad) in the joint_map convention (keys as in JOINTS)."""
        g = lambda k: q.get(k, 0.0)  # noqa: E731
        W = {"pelvis": T()}
        W["torso"] = T(rz(g("waist_yaw")), WAIST_O)
        for side, s, name in (("L", 1, "left"), ("R", -1, "right")):
            W[f"{side}_shoulder_pitch"] = W["torso"] @ T(ry(g(f"{name}_shoulder_pitch")), SH_O * [1, s, 1])
            W[f"{side}_shoulder_roll"] = W[f"{side}_shoulder_pitch"] @ T(rx(g(f"{name}_shoulder_roll")), SR_OFF * [1, s, 1])
            W[f"{side}_upper_arm"] = W[f"{side}_shoulder_roll"] @ T(rz(g(f"{name}_shoulder_yaw")), SY_OFF)
            W[f"{side}_forearm"] = W[f"{side}_upper_arm"] @ T(ry(g(f"{name}_elbow")), EL_OFF)
            W[f"{side}_hand"] = W[f"{side}_forearm"] @ T(None, HAND_OFF)
        W["neck"] = W["torso"] @ T(rz(g("neck_yaw")), NY_O)
        W["head"] = W["neck"] @ T(ry(g("neck_pitch")), NP_OFF)
        return W

    def component_poses(self, q):
        W = self.links(q)
        return {k: W[link] @ Tl for k, (part, link, Tl) in self.comps.items()}


# actuated joints: (joint, housing key, output key, joint axis in the parent link frame)
ACTUATED = [("waist_yaw", "WaistH", "WaistO", (0, 0, 1))]
for _side, _name in (("L", "left"), ("R", "right")):
    ACTUATED += [(f"{_name}_shoulder_pitch", f"{_side}_SPH", f"{_side}_SPO", (0, 1, 0)),
                 (f"{_name}_shoulder_roll", f"{_side}_SRH", f"{_side}_SRO", (1, 0, 0)),
                 (f"{_name}_shoulder_yaw", f"{_side}_SYH", f"{_side}_SYO", (0, 0, 1)),
                 (f"{_name}_elbow", f"{_side}_ElH", f"{_side}_ElO", (0, 1, 0))]
ACTUATED += [("neck_yaw", "NeckYawS", "NeckYawH", (0, 0, 1)), ("neck_pitch", "NeckPitchS", "NeckPitchH", (0, 1, 0))]
