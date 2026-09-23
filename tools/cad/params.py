"""Shared CAD parameters (metres) derived from calculations/design_point.yaml plus CAD-only packaging values.

Every CAD script reads from here so SolidWorks global variables, the analysis model and the joint map
stay consistent. Values tagged PKG are packaging decisions made in CAD (ASSUMED until verified by
interference checks in verification/).
"""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DP = yaml.safe_load((ROOT / "calculations" / "design_point.yaml").read_text(encoding="utf-8"))


def v(x):
    return x["value"] if isinstance(x, dict) and "value" in x else x


G = DP["geometry"]
THIGH = v(G["thigh_m"])
SHIN = v(G["shin_m"])
HIP_SPACING = v(G["hip_spacing_m"])
HIP_Y = HIP_SPACING / 2
SOLE_TO_ANKLE = v(G["sole_to_ankle_m"])
FOOT_L = v(G["foot"]["length_m"])
FOOT_W = v(G["foot"]["width_m"])
FOOT_HEEL = v(G["foot"]["ankle_from_heel_m"])
FOOT_T = v(G["foot"]["thickness_m"])
AL = DP["ankle_linkage"]
CRANK_R = v(AL["crank_radius_m"])
FOOT_LEVER = v(AL["foot_lever_m"])
ROD_W = v(AL["rod_half_spacing_m"])

# ---------------------------------------------------------------- JX1 Modular Actuator Interface (MAI) classes
# Frame: +Z = joint axis pointing out of the output face; output mounting face at z = T_OUT (after the output disc);
# housing occupies z in [-L_HOUSING, 0]; connector zone on the +Y side at the rear.
ACT = {
    # L = RobStride RS03 envelope (106 x 56 mm, 0.88 kg, 60 N·m peak) — dims VERIFIED (official), bolt patterns ASSUMED
    "L": {"D": 0.106, "L_HOUSING": 0.050, "T_OUT": 0.006, "D_OUT": 0.068, "PILOT_D": 0.044, "PILOT_H": 0.002,
          "PCD_OUT": 0.056, "N_OUT": 8, "HOLE_OUT": 0.0033, "PCD_REAR": 0.086, "N_REAR": 8, "HOLE_REAR": 0.0033,
          "BOLT": "M4", "CONN": (0.024, 0.010, 0.018), "PRODUCT": "RobStride RS03", "MASS": 0.880},
    # M = RobStride RS06 envelope (88 x 49 mm, 0.621 kg, 36 N·m peak)
    "M": {"D": 0.088, "L_HOUSING": 0.044, "T_OUT": 0.005, "D_OUT": 0.056, "PILOT_D": 0.034, "PILOT_H": 0.002,
          "PCD_OUT": 0.046, "N_OUT": 6, "HOLE_OUT": 0.0025, "PCD_REAR": 0.074, "N_REAR": 6, "HOLE_REAR": 0.0025,
          "BOLT": "M3", "CONN": (0.020, 0.009, 0.016), "PRODUCT": "RobStride RS06", "MASS": 0.621},
    # S = RobStride RS02 envelope (78.5 x 45.5 mm, 0.405 kg, 17 N·m peak)
    "S": {"D": 0.0785, "L_HOUSING": 0.0405, "T_OUT": 0.005, "D_OUT": 0.050, "PILOT_D": 0.030, "PILOT_H": 0.002,
          "PCD_OUT": 0.040, "N_OUT": 6, "HOLE_OUT": 0.0025, "PCD_REAR": 0.066, "N_REAR": 6, "HOLE_REAR": 0.0025,
          "BOLT": "M3", "CONN": (0.018, 0.008, 0.014), "PRODUCT": "RobStride RS02", "MASS": 0.405},
    # XS = RobStride RS00 envelope (57 x 51 mm, 0.310 kg, 14 N·m peak)
    "XS": {"D": 0.057, "L_HOUSING": 0.046, "T_OUT": 0.005, "D_OUT": 0.040, "PILOT_D": 0.024, "PILOT_H": 0.002,
           "PCD_OUT": 0.032, "N_OUT": 6, "HOLE_OUT": 0.0025, "PCD_REAR": 0.046, "N_REAR": 4, "HOLE_REAR": 0.0025,
           "BOLT": "M3", "CONN": (0.016, 0.008, 0.012), "PRODUCT": "RobStride RS00", "MASS": 0.310},
}

# ---------------------------------------------------------------- leg packaging (PKG, leg frame = hip centre, left leg)
PKG = {
    "yaw_out_z": 0.075,          # hip-yaw output mounting face height above hip centre (faces -Z)
    "roll_out_x": -0.070,        # hip-roll output mounting face x (faces +X); housing behind it
    "pitch_out_y": 0.036,        # hip-pitch output mounting face y (faces +Y, lateral); housing medial of it
    "knee_rear_y": 0.036,        # knee housing rear face y (lateral, bolted to thigh plate)
    "plate_t": 0.008,            # structural plate thickness (thigh/brackets)
    "shin_beam_w": 0.048,        # shin beam width in y (motor pockets pass through it)
    "shin_beam_d": 0.050,        # shin beam depth in x
    "ankle_A_z": -0.110,         # ankle motor A axis below the knee axis (upper motor, output lateral +Y)
    "ankle_B_z": -0.200,         # ankle motor B axis below the knee axis (lower motor, output medial -Y); 105 mm above ankle
    "shin_web_t": 0.010,         # central shin web thickness; motor rear faces bolt to either side
    "rod_foot_w": 0.045,         # lateral offset of the foot rod-end posts (ankle frame)
    "rod_crank_w": 0.057,        # lateral offset of the crank ball studs (web/2 + M housing+output + crank/2)
    "ankle_class": "M",          # ankle motor class (RS06); crank 50 / foot lever 40 (reach-driven)
    "crank_r": 0.050,            # crank radius
    "foot_lever": 0.040,         # rod-end posts behind the ankle axis
}
