"""Exact zero-pose placement and forward kinematics for every component of the JX1 CAD leg.

Used by the assembly builder (initial placement) and the pose verifier (drive poses by component transforms,
then check that SolidWorks' mate solver leaves them unchanged — i.e. CAD mates == analytic kinematics).
All transforms are 4x4 homogeneous matrices in metres, in the assembly (= pelvis) frame.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "calculations"))
from jx1calc.ankle import ParallelAnkle  # noqa: E402
from cad.params import ACT, PKG, THIGH, SHIN, HIP_Y, CRANK_R, FOOT_LEVER  # noqa: E402

L, M = ACT["L"], ACT["M"]
PC, KC = ACT[PKG["pitch_class"]], ACT[PKG["knee_class"]]
AK = ACT[PKG["ankle_class"]]
WEB = PKG["shin_web_t"]


def rx(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def ry(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def T(R=None, p=(0, 0, 0)):
    m = np.eye(4)
    if R is not None:
        m[:3, :3] = R
    m[:3, 3] = p
    return m


RX90, RXm90, RY90, RX180 = rx(np.pi / 2), rx(-np.pi / 2), ry(np.pi / 2), rx(np.pi)
# Output flanges of long-range joints are clocked 45 deg about their own axis (8-bolt pattern -> holes still align) so the
# SolidWorks limit-mate window (housing Right Plane vs output Top Plane = 90 deg + rotation) stays inside (0, 180) deg.
CLOCK = {"PitchO": np.radians(45.0), "KneeO": np.radians(45.0)}
# Connector zones (local +Y of every housing) are clocked to face backwards (-X) for cable routing and clearance;
# the matching output is clocked by the same angle so joint zero and limit windows are unchanged.
CONN = rz(np.pi / 2)


def ankle_model():
    hA = SHIN + PKG["ankle_A_z"]
    hB = SHIN + PKG["ankle_B_z"]
    return ParallelAnkle(CRANK_R, FOOT_LEVER, PKG["rod_foot_w"], (hA, hB), PKG["rod_crank_w"])


class LegCAD:
    """Component layout of one leg. side = +1 (left) / -1 (right). Component keys map to part files."""

    def __init__(self, side=+1):
        self.sy = side
        s = side
        hip = np.array([0.0, s * HIP_Y, 0.0])
        self.hip = hip
        yA, yB = WEB / 2 + AK["L_HOUSING"], -(WEB / 2 + AK["L_HOUSING"])
        # component: (part key, link, transform in the LINK frame at zero pose)
        # link frames at zero pose sit at: pelvis origin, hip centre (yaw/roll/thigh), knee (shin), ankle (cross/foot)
        c = {}
        c["YawH"] = ("ACT_M_Housing", "pelvis", T(RX180 @ CONN, hip + [0, 0, PKG["yaw_out_z"] + M["T_OUT"]]))
        c["YawO"] = ("ACT_M_Output", "hip_yaw", T(RX180 @ CONN, [0, 0, PKG["yaw_out_z"] + M["T_OUT"]]))
        c["HipYawBr"] = ("HipYawBracket", "hip_yaw", T())
        c["RollH"] = ("ACT_L_Housing", "hip_yaw", T(RY90, [PKG["roll_out_x"] - L["T_OUT"], 0, 0]))
        c["RollO"] = ("ACT_L_Output", "hip_roll", T(RY90, [PKG["roll_out_x"] - L["T_OUT"], 0, 0]))
        c["HipRollBr"] = ("HipRollBracket", "hip_roll", T())
        c["PitchH"] = ("ACT_" + PKG["pitch_class"] + "_Housing", "hip_roll", T((RXm90 if s > 0 else RX90) @ CONN, [0, s * (PKG["pitch_out_y"] - PC["T_OUT"]), 0]))
        self.clock = {k: v * s for k, v in CLOCK.items()}   # clocking mirrors with the side (actuators face the other way)
        c["PitchO"] = ("ACT_" + PKG["pitch_class"] + "_Output", "thigh", T((RXm90 if s > 0 else RX90) @ CONN @ rz(self.clock["PitchO"]), [0, s * (PKG["pitch_out_y"] - PC["T_OUT"]), 0]))
        c["Thigh"] = ("Thigh", "thigh", T())
        kh_y = PKG["knee_rear_y"] - KC["L_HOUSING"]
        c["KneeH"] = ("ACT_" + PKG["knee_class"] + "_Housing", "thigh", T((RX90 if s > 0 else RXm90) @ CONN, [0, s * kh_y, -THIGH]))
        c["KneeO"] = ("ACT_" + PKG["knee_class"] + "_Output", "shin", T((RX90 if s > 0 else RXm90) @ CONN @ rz(self.clock["KneeO"]), [0, s * kh_y, 0]))
        c["Shin"] = ("Shin", "shin", T())
        # ankle motors: A upper (output lateral), B lower (output medial); rotors rotate by phi about the shin +y axis
        c["AnkAH"] = ("ACT_" + PKG["ankle_class"] + "_Housing", "shin", T((RXm90 if s > 0 else RX90) @ CONN, [0, s * yA, PKG["ankle_A_z"]]))
        c["AnkBH"] = ("ACT_" + PKG["ankle_class"] + "_Housing", "shin", T((RX90 if s > 0 else RXm90) @ CONN, [0, s * yB, PKG["ankle_B_z"]]))
        c["AnkAO"] = ("ACT_" + PKG["ankle_class"] + "_Output", "rotorA", T((RXm90 if s > 0 else RX90) @ CONN, [0, s * yA, 0]))
        c["AnkBO"] = ("ACT_" + PKG["ankle_class"] + "_Output", "rotorB", T((RX90 if s > 0 else RXm90) @ CONN, [0, s * yB, 0]))
        c["CrankA"] = ("AnkleCrank", "rotorA", T(RXm90 if s > 0 else RX90, [0, s * (yA + AK["T_OUT"]), 0]))
        c["CrankB"] = ("AnkleCrank", "rotorB", T(RX90 if s > 0 else RXm90, [0, s * (yB - AK["T_OUT"]), 0]))
        c["Cross"] = ("AnkleCross", "ankle_cross", T())
        c["Foot"] = ("Foot", "foot", T())
        self.comps = c
        self.ankle = ankle_model()
        self.rotor_axis_z = {"rotorA": PKG["ankle_A_z"], "rotorB": PKG["ankle_B_z"]}

    # ---------------------------------------------------------------- forward kinematics
    def links(self, q):
        """q: dict joint -> angle (rad) in the robot convention (joint_map.yaml)."""
        g = lambda k: q.get(k, 0.0)  # noqa: E731
        W = {"pelvis": T()}
        W["hip_yaw"] = T(rz(g("hip_yaw")), self.hip)
        W["hip_roll"] = W["hip_yaw"] @ T(rx(g("hip_roll")))
        W["thigh"] = W["hip_roll"] @ T(ry(g("hip_pitch")))
        W["shin"] = W["thigh"] @ T(None, [0, 0, -THIGH]) @ T(ry(g("knee")))
        W["ankle_cross"] = W["shin"] @ T(None, [0, 0, -SHIN]) @ T(ry(g("ankle_pitch")))
        W["foot"] = W["ankle_cross"] @ T(rx(g("ankle_roll")))
        # parallel-ankle motor angles (left-leg model; mirror roll for the right leg)
        phi = self.ankle.crank_angles(g("ankle_pitch"), self.sy * g("ankle_roll"))
        for key, ph, z in (("rotorA", phi[0], PKG["ankle_A_z"]), ("rotorB", phi[1], PKG["ankle_B_z"])):
            W[key] = W["shin"] @ T(None, [0, 0, z]) @ T(ry(ph))
        self.phi = phi
        return W

    def component_poses(self, q):
        W = self.links(q)
        out = {k: W[link] @ Tl for k, (part, link, Tl) in self.comps.items()}
        # rods from crank ball to foot ball
        for tag, crank, i in (("RodA", "CrankA", 0), ("RodB", "CrankB", 1)):
            top = (out[crank] @ np.array([-CRANK_R, 0, 0.003, 1.0]))[:3]
            fb = np.array([-FOOT_LEVER, self.sy * PKG["rod_foot_w"] * (1 if i == 0 else -1), 0.0, 1.0])
            bot = (W["foot"] @ fb)[:3]
            d = bot - top
            ez = -d / np.linalg.norm(d)
            ex = np.cross([0, 1.0, 0], ez)
            ex /= np.linalg.norm(ex)
            ey = np.cross(ez, ex)
            out[tag] = T(np.c_[ex, ey, ez], top)
            out[tag + "_len"] = np.linalg.norm(d)
        return out
