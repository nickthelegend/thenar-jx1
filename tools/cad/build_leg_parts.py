"""Build the JX1 pelvis and left-leg structural parts as native parametric SolidWorks parts.

Each part is modelled in its robot link frame (see simulation/joint_map.yaml):
  JX1_Pelvis            pelvis frame (origin midway between hip centres)
  JX1_HipYawBracket_L   hip_yaw_link frame (left hip centre)
  JX1_HipRollBracket_L  hip_roll_link frame (left hip centre)
  JX1_Thigh_L           thigh_link frame (left hip centre)
  JX1_Shin_L            shin_link frame (knee centre)
  JX1_AnkleCross        ankle_cross_link frame (ankle centre)
  JX1_Foot_L            foot_link frame (ankle centre)
  JX1_AnkleCrank        crank frame = motor output mounting face centre, +Z along motor axis
  JX1_AnkleRod_A/_B     rod frame = upper ball centre, rod along -Z
Packaging values live in tools/cad/params.py (PKG) and are verified by interference checks.

Usage: .venv/Scripts/python tools/cad/build_leg_parts.py [part ...]
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from swlib.core import Session  # noqa: E402
from swlib.part import Part  # noqa: E402
from cad.params import ACT, PKG, ROOT, THIGH, SHIN, HIP_Y, SOLE_TO_ANKLE, FOOT_L, FOOT_W, FOOT_HEEL, CRANK_R, FOOT_LEVER  # noqa: E402
from cad.shapes import plate, plate2d, circle_cut, chamfer_rect, bolt_holes, uv, set_side, my, SIDE  # noqa: E402

CADDIR = ROOT / "CAD"
PRINT_RGB = (0.16, 0.16, 0.17)      # PA-CF printed
ALU_RGB = (0.80, 0.81, 0.83)        # 6061 plate
ACCENT_RGB = (0.95, 0.42, 0.10)     # JX1 orange (covers / feet)
STEEL_RGB = (0.60, 0.61, 0.63)

L, M = ACT["L"], ACT["M"]
PC, KC = ACT[PKG["pitch_class"]], ACT[PKG["knee_class"]]   # hip-pitch and knee actuator classes
CLR_M4, CLR_M3, CLR_M5 = 0.0045, 0.0034, 0.0055
T = PKG["plate_t"]


def mm(x):
    return round(x * 1000, 4)


def SUF():
    return "L" if SIDE[0] > 0 else "R"


def finish(p: Part, rgb, role, material_note):
    p.color(rgb)
    p.prop("JX1_Role", role)
    p.prop("Manufacturing", material_note)
    return p.save(close=False)


# ------------------------------------------------------------------------------------------------ pelvis
def pelvis(s):
    p = Part(s, "JX1_Pelvis", CADDIR / "Pelvis" / "JX1_Pelvis.SLDPRT")
    yaw_top = PKG["yaw_out_z"] + M["T_OUT"] + M["L_HOUSING"]          # housing rear face height
    z0, z1 = yaw_top, yaw_top + T
    W, D = HIP_Y + M["D"] / 2 + 0.011, 0.075                          # half-width (y) clears the yaw housings, half-depth (x)
    p.gv("Hip_spacing", mm(2 * HIP_Y)); p.gv("Pelvis_half_width", mm(W)); p.gv("Pelvis_half_depth", mm(D))
    top_holes = []
    for sy in (1, -1):
        top_holes += [(u, v, CLR_M3) for (u, v, _) in bolt_holes((0, sy * HIP_Y), M["PCD_REAR"], M["N_REAR"], CLR_M3)]
        top_holes.append((0, sy * HIP_Y, 0.024))                       # cable pass-through over each hip
    top_holes += [(u, v, CLR_M3) for (u, v, _) in bolt_holes((0, 0), M["PCD_REAR"], M["N_REAR"], CLR_M3, 30)]  # waist yaw interface
    top_holes += [(0, 0, 0.030)]
    plate2d(p, "Top_Plate", "z", z0, z1, chamfer_rect(-D, -W, D, W, 0.025), top_holes)
    wall_z0 = PKG["yaw_out_z"] + M["T_OUT"] + 0.004                     # stay above the hip-yaw bracket sweep
    # front/back walls (normal x), side walls (normal y)
    for tag, x0 in (("Front_Wall", D - T), ("Back_Wall", -D)):
        plate(p, tag, "x", x0, x0 + T, [(0, -W + 0.02, wall_z0), (0, W - 0.02, wall_z0), (0, W - 0.02, z0), (0, -W + 0.02, z0)])
    for tag, y0 in (("Left_Wall", W - T), ("Right_Wall", -W)):
        plate(p, tag, "y", y0, y0 + T, [(-D + 0.02, 0, wall_z0), (D - 0.02, 0, wall_z0), (D - 0.02, 0, z0), (-D + 0.02, 0, z0)])
    # bottom plate with clearance bores around both yaw housings -> closed torsion box
    bot = [(0, sy * HIP_Y, M["D"] + 0.006) for sy in (1, -1)] + [(0.0, 0.0, 0.040)]
    plate2d(p, "Bottom_Plate", "z", wall_z0, wall_z0 + 0.005, chamfer_rect(-D, -W, D, W, 0.025), bot)
    return finish(p, PRINT_RGB, "pelvis torsion box; carries both hip-yaw actuators and the waist interface",
                  "FDM PA-CF (P1S, 4 walls, 40% gyroid) with M3 heat-set inserts; ASSUMED")


# ------------------------------------------------------------------------------------------------ hip yaw bracket
def hip_yaw_bracket(s):
    p = Part(s, f"JX1_HipYawBracket_{SUF()}", CADDIR / "Hip" / f"JX1_HipYawBracket_{SUF()}.SLDPRT")
    zt = PKG["yaw_out_z"]                     # mounting face (top of plate)
    x_back = PKG["roll_out_x"] - L["T_OUT"] - L["L_HOUSING"]   # roll housing rear face
    p.gv("Yaw_face_z", mm(zt)); p.gv("Roll_rear_x", mm(x_back))
    holes = [(u, v, CLR_M3) for (u, v, _) in bolt_holes((0, 0), M["PCD_OUT"], M["N_OUT"], CLR_M3)]
    holes.append((0, 0, 0.012))
    top = chamfer_rect(x_back - T, -0.045, 0.036, 0.045, 0.018)
    plate2d(p, "Top_Plate", "z", zt - 0.010, zt, top, holes)
    circle_cut(p, "Yaw_Pilot_Recess", "z", zt, (0, 0, zt), M["PILOT_D"] + 0.0003, M["PILOT_H"] + 0.0002, into_positive=False)
    # back plate carrying the hip-roll housing rear face
    back_holes = [(u, v, CLR_M4) for (u, v, _) in bolt_holes(uv("x", (0, 0, 0)), L["PCD_REAR"], L["N_REAR"], CLR_M4, 22.5)]
    back_holes.append((*uv("x", (0, 0, 0)), 0.026))
    outline = [(0, -0.050, -0.050), (0, 0.050, -0.050), (0, 0.050, zt), (0, -0.050, zt)]
    plate(p, "Back_Plate", "x", x_back - T, x_back, outline, [((0, y, z), d) for (y, z, d) in
          [(v_, -u_, d_) for (u_, v_, d_) in back_holes]])
    # central rib above the roll housing
    plate(p, "Rib", "y", -0.004, 0.004, [(x_back - T, 0, 0.052), (-0.030, 0, zt - 0.010), (x_back - T, 0, zt - 0.010)])
    return finish(p, PRINT_RGB, "hip yaw output -> hip roll housing", "FDM PA-CF, M4/M3 through-bolts; ASSUMED")


# ------------------------------------------------------------------------------------------------ hip roll bracket
def hip_roll_bracket(s):
    p = Part(s, f"JX1_HipRollBracket_{SUF()}", CADDIR / "Hip" / f"JX1_HipRollBracket_{SUF()}.SLDPRT")
    xf = PKG["roll_out_x"]                      # roll output mounting face (faces +X)
    y_med = PKG["pitch_out_y"] - PC["T_OUT"] - PC["L_HOUSING"]   # pitch housing rear face (medial)
    p.gv("Roll_face_x", mm(xf)); p.gv("Pitch_rear_y", mm(y_med))
    bh = [(0, y, z, d) for (y, z, d) in [(v_, -u_, d_) for (u_, v_, d_) in bolt_holes(uv("x", (0, 0, 0)), L["PCD_OUT"], L["N_OUT"], CLR_M4, 22.5)]]
    y_lat = PKG["pitch_out_y"] - 0.002       # stop 2 mm short of the thigh plate plane
    y_in = min(y_med - T, -L["D_OUT"] / 2 - 0.002)  # cover the whole roll output flange on the medial side
    plate(p, "Back_Plate", "x", xf, xf + T, [(0, y_in, -0.045), (0, y_lat, -0.045), (0, y_lat, 0.045), (0, y_in, 0.045)],
          [((0, y, z), d) for (_, y, z, d) in bh] + [((0, 0, 0), 0.012)])
    circle_cut(p, "Roll_Pilot_Recess", "x", xf, (xf, 0, 0), L["PILOT_D"] + 0.0003, L["PILOT_H"] + 0.0002, into_positive=True)
    rm = PC["PCD_REAR"] / 2 + 0.006
    mh = [((x, 0, z), d) for (x, z, d) in [(u_, -v_, d_) for (u_, v_, d_) in bolt_holes((0, 0), PC["PCD_REAR"], PC["N_REAR"], CLR_M5, 22.5)]]
    mh.append(((0, 0, 0), 0.026))
    x0m = xf + T                              # start behind the back plate: keeps clear of the roll output pilot boss
    plate(p, "Medial_Plate", "y", y_med - T, y_med, [(x0m, 0, -rm), (0.030, 0, -rm), (rm, 0, -0.030), (rm, 0, 0.030),
                                                      (0.030, 0, rm), (x0m, 0, rm)], mh)
    return finish(p, PRINT_RGB, "hip roll output -> hip pitch housing", "FDM PA-CF; ASSUMED")


# ------------------------------------------------------------------------------------------------ thigh
def thigh(s):
    p = Part(s, f"JX1_Thigh_{SUF()}", CADDIR / "Thigh" / f"JX1_Thigh_{SUF()}.SLDPRT")
    y0 = PKG["pitch_out_y"]
    p.gv("Thigh_length", mm(THIGH)); p.gv("Thigh_plate_t", mm(T))
    Lt = THIGH
    rk = PKG["thigh_knee_r"]                            # knee-end radius (clears ankle motor A up to 120 deg knee)
    knee_arc = [(rk * math.cos(math.radians(a)), 0, -Lt + rk * math.sin(math.radians(a))) for a in range(0, -181, -22)][1:-1]
    knee_arc = [(rk * math.cos(math.radians(a)), 0, -Lt + rk * math.sin(math.radians(a))) for a in (-11.25, -33.75, -56.25, -78.75, -101.25, -123.75, -146.25, -168.75)]
    rt = PC["PCD_OUT"] / 2 + 0.008                      # top boss radius around the hip-pitch output pattern
    outline = [(-rt * 0.8, 0, rt), (rt * 0.8, 0, rt), (rt + 0.004, 0, 0.0), (0.030, 0, -0.110), (0.048, 0, -Lt + 0.056)] + \
              knee_arc + [(-0.048, 0, -Lt + 0.056), (-0.030, 0, -0.110), (-rt - 0.004, 0, 0.0)]
    holes = [((x, 0, z), CLR_M5) for (x, z, _) in [(u_, -v_, d_) for (u_, v_, d_) in bolt_holes((0, 0), PC["PCD_OUT"], PC["N_OUT"], CLR_M5, 22.5)]]
    holes += [((x, 0, z), CLR_M5) for (x, z, _) in [(u_, -v_, d_) for (u_, v_, d_) in bolt_holes((0, Lt), KC["PCD_REAR"], KC["N_REAR"], CLR_M5, 22.5)]]
    holes += [((0, 0, 0), 0.012), ((0, 0, -Lt), 0.026), ((0, 0, -0.085), 0.022), ((0, 0, -0.140), 0.022), ((0, 0, -0.195), 0.020)]
    plate(p, "Thigh_Plate", "y", y0, y0 + T, outline, holes)
    circle_cut(p, "Pitch_Pilot_Recess", "y", y0, (0, y0, 0), PC["PILOT_D"] + 0.0003, PC["PILOT_H"] + 0.0002, into_positive=True)
    # C-channel flanges (medial) between the actuators for bending stiffness
    for tag, x0 in (("Front_Flange", 0.022), ("Back_Flange", -0.030)):
        plate(p, tag, "x", x0, x0 + 0.008, [(0, y0 - 0.020, -0.215), (0, y0, -0.215), (0, y0, -0.100), (0, y0 - 0.020, -0.100)])
    p.ref_axis("Front Plane", "Right Plane", "AX_PitchY")
    p.ref_plane_angle("Front Plane", "AX_PitchY", 40.0, "PL_PitchRef")   # hip-pitch limit reference (window offset 50 deg)
    return finish(p, ALU_RGB, "thigh: hip pitch output -> knee housing (coplanar faces)", "6061-T6 8 mm plate, CNC/waterjet + flanges; ASSUMED")


# ------------------------------------------------------------------------------------------------ shin (frame at knee centre)
def shin(s):
    p = Part(s, f"JX1_Shin_{SUF()}", CADDIR / "Shin" / f"JX1_Shin_{SUF()}.SLDPRT")
    y_out = -(PKG["knee_rear_y"] - L["L_HOUSING"]) - L["T_OUT"] + 0.0   # knee output face (medial), = -0.028
    y_out = PKG["knee_rear_y"] - KC["L_HOUSING"] - KC["T_OUT"]
    zA, zB, Ls = PKG["ankle_A_z"], PKG["ankle_B_z"], SHIN
    web = PKG["shin_web_t"] if "shin_web_t" in PKG else 0.010
    p.gv("Shin_length", mm(Ls)); p.gv("AnkleA_z", mm(zA)); p.gv("AnkleB_z", mm(zB))
    # top plate on the knee output (medial face y_out)
    top_holes = [((x, 0, z), CLR_M5) for (x, z, _) in [(u_, -v_, d_) for (u_, v_, d_) in bolt_holes((0, 0), KC["PCD_OUT"], KC["N_OUT"], CLR_M5, 22.5)]]
    top_holes.append(((0, 0, 0), 0.012))
    rk = KC["PCD_OUT"] / 2 + 0.008
    plate(p, "Knee_Plate", "y", y_out - T, y_out, [(-rk * 0.85, 0, rk), (rk * 0.85, 0, rk), (rk + 0.004, 0, 0.0), (0.036, 0, -0.084),
                                                    (-0.036, 0, -0.084), (-rk - 0.004, 0, 0.0)], top_holes)
    circle_cut(p, "Knee_Pilot_Recess", "y", y_out, (0, y_out, 0), KC["PILOT_D"] + 0.0003, KC["PILOT_H"] + 0.0002, into_positive=False)
    # joggle block from the knee plate to the central web (outside the knee housing radius)
    plate(p, "Joggle", "z", -0.084, -0.066, [(-0.034, y_out - T, 0), (0.034, y_out - T, 0), (0.034, web / 2, 0), (-0.034, web / 2, 0)])
    # central web with both ankle-motor bolt patterns (A upper: housing on +Y side; B lower: housing on -Y side)
    web_outline = [(-0.034, 0, -0.066), (0.034, 0, -0.066), (0.048, 0, zA + 0.030), (0.048, 0, zB - 0.030), (0.030, 0, -Ls + 0.036),
                   (-0.030, 0, -Ls + 0.036), (-0.048, 0, zB - 0.030), (-0.048, 0, zA + 0.030)]
    AK = ACT[PKG["ankle_class"]]
    wh = [((x, 0, z), CLR_M3) for (x, z, _) in [(u_, -v_, d_) for (u_, v_, d_) in bolt_holes((0, -zA), AK["PCD_REAR"], AK["N_REAR"], CLR_M3)]]
    wh += [((x, 0, z), CLR_M3) for (x, z, _) in [(u_, -v_, d_) for (u_, v_, d_) in bolt_holes((0, -zB), AK["PCD_REAR"], AK["N_REAR"], CLR_M3)]]
    wh += [((0, 0, zA), 0.022), ((0, 0, zB), 0.022), ((0, 0, (zA + zB) / 2), 0.016)]
    plate(p, "Web", "y", -web / 2, web / 2, web_outline, wh)
    # ankle pitch fork: crossbar + two tines around the cross block, pin hole on the ankle pitch axis
    za = -Ls
    plate(p, "Fork_Bar", "z", za + 0.030, za + 0.040, [(-0.030, -0.027, 0), (0.030, -0.027, 0), (0.030, 0.027, 0), (-0.030, 0.027, 0)])
    for tag, y0 in (("Tine_Lat", 0.018), ("Tine_Med", -0.027)):
        plate(p, tag, "y", y0, y0 + 0.009, [(-0.016, 0, za + 0.040), (0.016, 0, za + 0.040), (0.016, 0, za - 0.008), (0.008, 0, za - 0.018),
                                             (-0.008, 0, za - 0.018), (-0.016, 0, za - 0.008)], [((0, 0, za), 0.008)])
    p.ref_plane_offset("Front Plane", Ls, "PL_AnkleZ", flip=True)
    p.ref_axis("PL_AnkleZ", "Right Plane", "AX_AnklePitch")
    p.ref_axis("Front Plane", "Right Plane", "AX_KneeY")
    p.ref_plane_angle("Front Plane", "AX_KneeY", 67.5, "PL_KneeRef")    # knee limit reference (window offset 22.5 deg)
    return finish(p, PRINT_RGB, "shin: knee output -> ankle fork, carries ankle motors A (upper, +Y) and B (lower, -Y)",
                  "FDM PA-CF with Al knee plate insert option; ASSUMED")


# ------------------------------------------------------------------------------------------------ ankle cross (spider)
def ankle_cross(s):
    p = Part(s, "JX1_AnkleCross", CADDIR / "Ankle" / "JX1_AnkleCross.SLDPRT")
    p.gv("Cross_size", 32)
    plate(p, "Block", "z", -0.013, 0.013, [(-0.016, -0.0165, 0), (0.016, -0.0165, 0), (0.016, 0.0165, 0), (-0.016, 0.0165, 0)])
    # pitch pin bore (along Y) and roll pin bore (along X)
    circle_cut(p, "Pitch_Bore", "y", -0.020, (0, -0.020, 0), 0.008, 0.040, into_positive=True)
    circle_cut(p, "Roll_Bore", "x", -0.020, (-0.020, 0, 0), 0.008, 0.040, into_positive=True)
    p.ref_axis("Front Plane", "Right Plane", "AX_Pitch")
    p.ref_axis("Front Plane", "Top Plane", "AX_Roll")
    return finish(p, STEEL_RGB, "ankle universal-joint spider (pitch pin Y, roll pin X)", "EN8/EN24 steel, turned + drilled; ASSUMED")


# ------------------------------------------------------------------------------------------------ foot
def foot(s):
    p = Part(s, f"JX1_Foot_{SUF()}", CADDIR / "Foot" / f"JX1_Foot_{SUF()}.SLDPRT")
    zs = -SOLE_TO_ANKLE
    toe, heel, hw = FOOT_L - FOOT_HEEL, -FOOT_HEEL, FOOT_W / 2
    p.gv("Foot_length", mm(FOOT_L)); p.gv("Foot_width", mm(FOOT_W)); p.gv("Ankle_height", mm(SOLE_TO_ANKLE))
    outline = [(heel + 0.015, -hw), (toe - 0.028, -hw), (toe, -hw + 0.022), (toe, hw - 0.022), (toe - 0.028, hw), (heel + 0.015, hw),
               (heel, hw - 0.015), (heel, -hw + 0.015)]
    plate2d(p, "Sole_Plate", "z", zs, zs + 0.010, outline, [(0.070, 0.0, 0.020), (0.030, 0.0, 0.016)])
    # roll clevis tines (normal X) either side of the cross block
    for tag, x0 in (("Clevis_Front", 0.0175), ("Clevis_Back", -0.0255)):
        plate(p, tag, "x", x0, x0 + 0.008, [(0, -0.013, zs + 0.010), (0, 0.013, zs + 0.010), (0, 0.013, 0.003), (0, 0.008, 0.010),
                                             (0, -0.008, 0.010), (0, -0.013, 0.003)], [((0, 0, 0), 0.008)])
    # push-rod ball posts behind the ankle (rod ends at ankle-centre height)
    wf = PKG.get("rod_foot_w", 0.045)
    for tag, sy in (("Post_Lat", 1), ("Post_Med", -1)):
        plate(p, tag, "z", zs + 0.010, -0.004, [(-FOOT_LEVER - 0.007, sy * wf - 0.007, 0), (-FOOT_LEVER + 0.007, sy * wf - 0.007, 0),
                                                (-FOOT_LEVER + 0.007, sy * wf + 0.007, 0), (-FOOT_LEVER - 0.007, sy * wf + 0.007, 0)])
    p.ref_axis("Front Plane", "Top Plane", "AX_Roll")
    p.ref_points_sketch("XY", "SK_RodBalls", [(-FOOT_LEVER, my(wf)), (-FOOT_LEVER, my(-wf))])   # [0] lateral (rod A), [1] medial (rod B)
    return finish(p, ACCENT_RGB, "foot: sole plate, roll clevis, rod-end posts", "FDM PA-CF + 3 mm TPU/rubber sole pad; ASSUMED")


# ------------------------------------------------------------------------------------------------ ankle crank & rods
def ankle_crank(s):
    p = Part(s, "JX1_AnkleCrank", CADDIR / "Ankle" / "JX1_AnkleCrank.SLDPRT")
    AK = ACT[PKG["ankle_class"]]
    p.gv("Crank_radius", mm(CRANK_R))
    holes = [(u, v, CLR_M3) for (u, v, _) in bolt_holes((0, 0), AK["PCD_OUT"], AK["N_OUT"], CLR_M3)]
    holes += [(-CRANK_R, 0, 0.005)]
    ro = AK["D_OUT"] / 2
    outline = [(-CRANK_R - 0.009, -0.009), (-ro * 0.7, -ro), (ro * 0.7, -ro), (ro, 0.0), (ro * 0.7, ro), (-ro * 0.7, ro), (-CRANK_R - 0.009, 0.009)]
    plate2d(p, "Crank_Plate", "z", 0.0, 0.006, outline, holes)
    circle_cut(p, "Pilot_Recess", "z", 0.0, (0, 0, 0), AK["PILOT_D"] + 0.0003, AK["PILOT_H"] + 0.0002, into_positive=True)
    p.ref_plane_offset("Front Plane", 0.003, "PL_BallMid")
    p.ref_points_sketch("XY", "SK_Ball", [(-CRANK_R, 0.0)], plane_name="PL_BallMid")
    p.ref_axis("Top Plane", "Right Plane", "AX_Joint")
    return finish(p, ALU_RGB, "ankle crank (M output -> rod end)", "6061 plate 6 mm; ASSUMED")


def ankle_rod(s, tag, length):
    p = Part(s, f"JX1_AnkleRod_{tag}", CADDIR / "Ankle" / f"JX1_AnkleRod_{tag}.SLDPRT")
    p.gv("Rod_length", mm(length))
    with p.sketch("XZ", "SK_Rod") as sk:  # revolve profile about the z axis (u = x = radius, v = -z)
        sk.centerline(0, -0.010, 0, length + 0.010)
        r_ball, r_rod = 0.007, 0.004
        pts = [(0, -r_ball), (r_ball, -r_ball), (r_ball, r_ball), (r_rod, r_ball), (r_rod, length - r_ball), (r_ball, length - r_ball),
               (r_ball, length + r_ball), (0, length + r_ball)]
        sk.polygon(pts)
    p.revolve("SK_Rod", "Rod_Body")
    p.ref_points_sketch("XZ", "SK_Ends", [(0.0, 0.0), (0.0, length)])
    return finish(p, STEEL_RGB, f"ankle push rod {tag} with M5 rod-end envelopes", "M5 threaded rod + 2x rod-end bearings; ASSUMED")


BUILDERS = {"pelvis": pelvis, "hip_yaw": hip_yaw_bracket, "hip_roll": hip_roll_bracket, "thigh": thigh, "shin": shin,
            "cross": ankle_cross, "foot": foot, "crank": ankle_crank}


SIDED = {"hip_yaw", "hip_roll", "thigh", "shin", "foot"}


def main():
    args = sys.argv[1:]
    side = "L"
    if args and args[0] in ("--side", "-s"):
        side, args = args[1], args[2:]
    set_side(1 if side == "L" else -1)
    names = args or list(BUILDERS) + ["rods"]
    if side == "R":
        names = [n for n in names if n in SIDED]   # crank, cross, rods and actuators are shared by both legs
    s = Session()
    report = {}
    for n in names:
        if n == "rods":
            hA = SHIN + PKG["ankle_A_z"]  # motor A height above ankle
            hB = SHIN + PKG["ankle_B_z"]
            wf, wc = PKG.get("rod_foot_w", 0.045), PKG.get("rod_crank_w", 0.060)
            for tag, h in (("A", hA), ("B", hB)):
                Lr = math.sqrt(h ** 2 + (wc - wf) ** 2 + (CRANK_R - FOOT_LEVER) ** 2)  # exact zero-pose ball-centre distance
                info = ankle_rod(s, tag, Lr)
                report[Path(info["path"]).stem] = {k: info[k] for k in ("bodies", "errors", "sketch_status", "refpoints")}
                print(Path(info["path"]).stem, info["bodies"], info["errors"], info["sketch_status"], flush=True)
            continue
        info = BUILDERS[n](s)
        report[Path(info["path"]).stem] = {k: info[k] for k in ("bodies", "errors", "sketch_status", "refpoints")}
        bad = {k: v for k, v in info["sketch_status"].items() if v != 3}
        print(Path(info["path"]).stem, "bodies", info["bodies"], "errors", info["errors"], "underdefined", bad, flush=True)
    ev = ROOT / "verification" / "cad_build_leg_parts.json"
    old = json.loads(ev.read_text()) if ev.exists() else {}
    old.update(report)
    ev.write_text(json.dumps(old, indent=2, default=str))


if __name__ == "__main__":
    main()
