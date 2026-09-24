"""Build the JX1 upper-body parts (phase 2) as native parametric SolidWorks parts, each in its robot link frame.

  JX1_Torso                 torso_link frame: origin at the waist RS06 output face; 6061 bottom plate, four 2020 posts,
                            side plates carrying the shoulder-pitch RS02 housings, deck, back plate (E-stop), electronics tray
  JX1_BatteryPack .. JX1_PowerSwitch   electronics envelopes placed directly in the torso frame
  JX1_ShoulderPitchBracket_L/R   shoulder_pitch_link: U-bracket around the RS02 shoulder-roll actuator
  JX1_ShoulderRollBracket_L/R    shoulder_roll_link: roll output -> RS00 shoulder-yaw housing
  JX1_UpperArm_L/R          upper_arm_link: yaw output -> RS00 elbow housing
  JX1_Forearm_L/R           forearm_link: elbow output -> gripper mount
  JX1_Gripper               hand_link: parallel-jaw gripper envelope (ST3215-driven)
  JX1_Servo_ST3215_Body/Horn  Waveshare ST3215 envelope (servo frame: +Z = output axis, horn on z >= 0)
  JX1_NeckBracket           neck_link: yaw-servo horn -> pitch-servo body
  JX1_Head, JX1_StereoCamera  head_link: head shell (open bottom), IMX219-83 stereo camera
Usage: .venv/Scripts/python tools/cad/build_upper_parts.py [--side L|R] [part ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from swlib.core import Session  # noqa: E402
from swlib.part import Part  # noqa: E402
from cad.params import ACT, ROOT  # noqa: E402
from cad.shapes import plate, plate2d, circle_cut, chamfer_rect, bolt_holes, ngon, set_side, SIDE  # noqa: E402
from cad.upper_kinematics import SH_O, SR_OFF, SY_OFF, EL_OFF, HAND_OFF, NP_OFF, UPK  # noqa: E402

CAD = ROOT / "CAD"
ALU_RGB = (0.80, 0.81, 0.83)
PRINT_RGB = (0.16, 0.16, 0.17)
ACCENT_RGB = (0.95, 0.42, 0.10)
PCB_RGB = (0.05, 0.35, 0.18)
BATT_RGB = (0.12, 0.22, 0.55)
RED_RGB = (0.80, 0.05, 0.05)
SERVO_RGB = (0.10, 0.10, 0.11)
S, XS, M = ACT["S"], ACT["XS"], ACT["M"]
CLR_M3, CLR_M4 = 0.0034, 0.0045

# torso packaging (torso frame, metres) — PKG-style values verified by interference checks
TOR = {
    "half_d": 0.070,            # x half-depth of the frame
    "side_y": 0.1045,           # outer face of the side plates = shoulder-pitch housing rear face (SH_O.y - T_OUT - L_HOUSING)
    "side_t": 0.004,
    "bottom_t": 0.005,
    "deck_z": 0.214,            # deck plate (shoulder axis height), 4 mm
    "deck_t": 0.004,
    "top_z": 0.262,             # top of side plates / back plate
    "post": 0.020,              # 2020 aluminium extrusion posts
    "tray_z": 0.095,            # electronics tray (3 mm) above the battery
    "back_x": -0.074,           # back plate outer face (E-stop panel), 4 mm
}


def mm(x):
    return round(x * 1000, 4)


def SUF():
    return "L" if SIDE[0] > 0 else "R"


def finish(p: Part, rgb, role, material_note, mass_note=None):
    p.color(rgb)
    p.prop("JX1_Role", role)
    p.prop("Manufacturing", material_note)
    if mass_note:
        p.prop("Mass_note", mass_note)
    return p.save(close=False)


# ------------------------------------------------------------------------------------------------ torso
def torso(s):
    p = Part(s, "JX1_Torso", CAD / "Torso" / "JX1_Torso.SLDPRT")
    hd, sy, st, bt, dz, dt, tz, po = (TOR[k] for k in ("half_d", "side_y", "side_t", "bottom_t", "deck_z", "deck_t", "top_z", "post"))
    p.gv("Torso_half_depth", mm(hd)); p.gv("Side_plate_y", mm(sy)); p.gv("Shoulder_z", mm(SH_O[2])); p.gv("Deck_z", mm(dz))
    yi = sy - st                                        # side plate inner face
    e = 0.0005                                          # 0.5 mm volumetric overlap at every join: SolidWorks rejects merges whose
                                                        # start plane coincides with an existing face (tested 2026-09-24)
    # bottom plate on the waist output (RS06 PCD 46, 6x M3) + pilot recess + cable hole + post screws
    holes = [(u, v, CLR_M3) for (u, v, _) in bolt_holes((0, 0), M["PCD_OUT"], M["N_OUT"], CLR_M3)] + [(0, 0, 0.014)]
    pc = [(sx * (hd - po / 2), sy_ * (yi - po / 2)) for sx in (1, -1) for sy_ in (1, -1)]
    holes += [(u, v, 0.0055) for (u, v) in pc]
    plate2d(p, "Bottom_Plate", "z", 0.0, bt, chamfer_rect(-hd, -yi, hd, yi, 0.015), holes)
    circle_cut(p, "Waist_Pilot_Recess", "z", 0.0, (0, 0, 0), M["PILOT_D"] + 0.0003, M["PILOT_H"] + 0.0002, into_positive=True)
    # side plates: shoulder-pitch RS02 rear pattern (PCD 66, 6x M3) around (x 0, z shoulder), cable hole
    for tag, y0 in (("Side_Left", yi), ("Side_Right", -sy)):
        sh = [((x, 0, z), CLR_M3) for (x, z, _) in [(u_, -v_, d_) for (u_, v_, d_) in bolt_holes((0, -SH_O[2]), S["PCD_REAR"], S["N_REAR"], CLR_M3)]]
        sh.append(((0, 0, SH_O[2]), 0.018))
        plate(p, tag, "y", y0, y0 + st, [(-hd, 0, bt), (hd, 0, bt), (hd, 0, tz), (-hd, 0, tz)], sh)
    # deck at shoulder height (neck-yaw servo sits on it) and electronics tray above the battery
    plate2d(p, "Deck", "z", dz, dz + dt, chamfer_rect(-hd, -yi - e, hd, yi + e, 0.010), [(0.0, 0.0, 0.020)])
    plate2d(p, "Tray", "z", TOR["tray_z"], TOR["tray_z"] + 0.003, [(-hd + po - e, -yi - e), (hd - po + e, -yi - e), (hd - po + e, yi + e),
                                                                     (-hd + po - e, yi + e)], [(0, 0, 0.025)])
    # back plate with the E-stop 22 mm mounting hole
    bx = TOR["back_x"]
    plate(p, "Back_Plate", "x", bx, bx + 0.004 + e, [(0, -sy, 0.100), (0, sy, 0.100), (0, sy, tz), (0, -sy, tz)], [((0, 0, 0.235), 0.0223)])
    # four 2020 extrusion posts: separate bodies (bolted in reality; merging them fails on SolidWorks' coplanar corner booleans)
    for k, (u, v) in enumerate(pc):
        plate2d(p, f"Post_{k}", "z", bt, dz, [(u - po / 2, v - po / 2), (u + po / 2, v - po / 2), (u + po / 2, v + po / 2), (u - po / 2, v + po / 2)],
                merge=False)
    return finish(p, ALU_RGB, "torso frame: waist output -> shoulder-pitch housings, neck, electronics bay",
                  "6061-T6 laser-cut plates (bottom 5, sides/deck/back 4 mm) + 4x EasyMech 2020 extrusion posts; FEA SF 4.44/3.59 (PA-CF print fails 0.70/0.42)")


# ------------------------------------------------------------------------------------------------ electronics envelopes (torso frame)
def box_part(s, name, sub, boxes, rgb, role, note):
    p = Part(s, name, CAD / sub / f"{name}.SLDPRT")
    for k, (x0, x1, y0, y1, z0, z1) in enumerate(boxes):
        plate2d(p, f"Box_{k}", "z", z0, z1, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    return finish(p, rgb, role, note)


def electronics(s):
    out = {}
    out["BatteryPack"] = box_part(s, "JX1_BatteryPack", "Electronics", [(-0.0435, 0.0435, -0.076, 0.076, 0.008, 0.090)], BATT_RGB,
                                  "13S2P Samsung INR21700-50S pack (4x7 grid) + JBD BMS on top, 468 Wh",
                                  "envelope 87 x 152 x 82 mm; 26 cells x 69 g + BMS/wiring ~0.25 kg = 2.05 kg (CALCULATED)")
    out["JetsonNano"] = box_part(s, "JX1_JetsonNano", "Electronics", [(-0.068, 0.028, -0.040, 0.040, 0.098, 0.138)], PCB_RGB,
                                 "Jetson Nano 4 GB dev kit (Waveshare) with fan", "envelope 100 x 80 x 40 mm, 0.25 kg (BOM)")
    out["HubBoard"] = box_part(s, "JX1_HubBoard", "Electronics", [(0.032, 0.046, -0.050, 0.050, 0.100, 0.200)], PCB_RGB,
                               "JX1 CAN hub board: 2x Teensy 4.1 + 6x TJA1462 + E-stop input", "envelope 100 x 100 x 14 mm (PCB + Teensys), 0.08 kg")
    out["DCDC5V"] = box_part(s, "JX1_DCDC5V", "Electronics", [(-0.066, -0.010, 0.046, 0.078, 0.100, 0.193)], (0.55, 0.56, 0.58),
                             "Mean Well DDR-60L-5 (18-75 V -> 5 V 10.8 A)", "envelope 56 x 32 x 93 mm ASSUMED from DIN-rail series outline, 0.2 kg")
    out["PowerSwitch"] = box_part(s, "JX1_PowerSwitch", "Electronics", [(-0.046, -0.002, -0.080, -0.042, 0.100, 0.119)], (0.2, 0.2, 0.2),
                                  "Flipsky anti-spark switch 300 A (motor bus, E-stop controlled)", "envelope 44 x 43 x 19 mm ASSUMED, 0.12 kg")
    bx = TOR["back_x"]
    p = Part(s, "JX1_EStop", CAD / "Electronics" / "JX1_EStop.SLDPRT")
    plate2d(p, "Head", "z", 0.215, 0.255, [(bx - 0.020, -0.020), (bx, -0.020), (bx, 0.020), (bx - 0.020, 0.020)])
    # M22 bushing through the 22.3 mm back-plate hole, modelled as a 21 mm 16-gon so it clears the hole wall; it joins the head
    # (outside) and the contact block (inside, 0.5 mm clear of the plate) into one body
    plate(p, "Bushing", "x", bx - 0.0005, bx + 0.0055, [(0, a, b) for (a, b) in ngon(0.0, 0.235, 0.0105, n=16)])
    plate2d(p, "Contact_Block", "z", 0.220, 0.250, [(bx + 0.005, -0.015), (bx + 0.049, -0.015), (bx + 0.049, 0.015), (bx + 0.005, 0.015)])
    out["EStop"] = finish(p, RED_RGB, "Schneider XB2BS8442C 40 mm mushroom E-stop, 1 NC", "head outside the back plate, contact block inside")
    return out


# ------------------------------------------------------------------------------------------------ arms (left modelled, right mirrored)
def shoulder_pitch_bracket(s):
    """shoulder_pitch_link: U-bracket from the pitch output (plane y = 0) around the RS02 roll actuator (axis x at y = 45 mm)."""
    p = Part(s, f"JX1_ShoulderPitchBracket_{SUF()}", CAD / "Arms" / f"JX1_ShoulderPitchBracket_{SUF()}.SLDPRT")
    yr = SR_OFF[1]                                            # roll axis offset (45 mm)
    xo = UPK["roll_out_x"] - S["T_OUT"]                       # roll housing front (output disc base)
    xr = xo - S["L_HOUSING"]                                   # roll housing rear face
    t, h = 0.005, S["D"] / 2 + 0.0025                         # plate thickness, half-height clear of the roll housing
    p.gv("Roll_axis_y", mm(yr)); p.gv("Roll_rear_x", mm(xr))
    ho = [((x, 0, z), CLR_M3) for (x, z, _) in [(u_, -v_, d_) for (u_, v_, d_) in bolt_holes((0, 0), S["PCD_OUT"], S["N_OUT"], CLR_M3)]]
    ho.append(((0, 0, 0), 0.010))
    plate(p, "Output_Plate", "y", 0.0, t, [(xr - t, 0, -h - t), (0.030, 0, -h - t), (0.030, 0, h + t), (xr - t, 0, h + t)], ho)
    circle_cut(p, "Pitch_Pilot_Recess", "y", 0.0, (0, 0, 0), S["PILOT_D"] + 0.0003, S["PILOT_H"] + 0.0002, into_positive=True)
    hr = [((0, y, z), CLR_M3) for (y, z, _) in [(v_, -u_, d_) for (u_, v_, d_) in bolt_holes((-0.0, yr), S["PCD_REAR"], S["N_REAR"], CLR_M3)]]
    plate(p, "Rear_Plate", "x", xr - t, xr, [(0, 0, -h - t), (0, yr + h, -h - t), (0, yr + h, h + t), (0, 0, h + t)],
          [((0, yr, 0), 0.016)] + [((0, y, z), d) for (_, y, z), d in hr])
    for tag, z0 in (("Top_Plate", h), ("Bottom_Plate", -h - t)):
        plate(p, tag, "z", z0, z0 + t, [(xr - t, 0, 0), (xo, 0, 0), (xo, yr + h, 0), (xr - t, yr + h, 0)])
    return finish(p, ALU_RGB, "shoulder pitch output -> shoulder roll housing (U-bracket)", "6061-T6 5 mm laser-cut plates, bolted; FEA SF 2.17/1.75")


def shoulder_roll_bracket(s):
    """shoulder_roll_link: roll output (plane x = roll_out_x) -> RS00 shoulder-yaw housing rear face (plane z = -19 mm)."""
    p = Part(s, f"JX1_ShoulderRollBracket_{SUF()}", CAD / "Arms" / f"JX1_ShoulderRollBracket_{SUF()}.SLDPRT")
    xf = UPK["roll_out_x"]
    zr = SY_OFF[2] + XS["T_OUT"] + XS["L_HOUSING"]            # yaw housing rear face (top)
    t = 0.006
    p.gv("Roll_face_x", mm(xf)); p.gv("Yaw_rear_z", mm(zr))
    ho = [((0, y, z), CLR_M3) for (y, z, _) in [(v_, -u_, d_) for (u_, v_, d_) in bolt_holes((0, 0), S["PCD_OUT"], S["N_OUT"], CLR_M3)]]
    # octagon (circumradius 36 mm) over the whole RS02 output flange: stays inside the 40 mm clearance to the
    # shoulder-pitch bracket output plate for every roll angle
    plate(p, "Roll_Plate", "x", xf, xf + t, [(0, a, b) for (a, b) in ngon(0.0, 0.0, 0.036)], ho + [((0, 0, 0), 0.010)])
    hy = [(u, v, CLR_M3) for (u, v, _) in bolt_holes((0, 0), XS["PCD_REAR"], XS["N_REAR"], CLR_M3, 45)] + [(0, 0, 0.014)]
    plate2d(p, "Yaw_Plate", "z", zr, zr + t, [(xf, -0.032), (0.032, -0.032), (0.032, 0.032), (xf, 0.032)], hy)
    # recess last: the yaw plate starts on the output-face plane and would otherwise re-fill part of it (pilot boss clash)
    circle_cut(p, "Roll_Pilot_Recess", "x", xf, (xf, 0, 0), S["PILOT_D"] + 0.0003, S["PILOT_H"] + 0.0002, into_positive=True)
    return finish(p, ALU_RGB, "shoulder roll output -> shoulder yaw housing (L-bracket)", "6061-T6 6 mm plates, bolted; FEA SF 2.05/1.66")


def upper_arm(s):
    """upper_arm_link: yaw output face (z = 0, facing down) -> RS00 elbow housing rear face (y = -elbow_face_y)."""
    p = Part(s, f"JX1_UpperArm_{SUF()}", CAD / "Arms" / f"JX1_UpperArm_{SUF()}.SLDPRT")
    yb = -UPK["elbow_face_y"]                                  # elbow housing rear face (medial)
    ze = EL_OFF[2]
    # structural variant U3 (calculations/structural/part_variants.py upper_arm): 6 mm plates failed (SF 1.34 / 1.08, L-corner);
    # elbow plate 10 mm (added medially), yaw plate 8 mm, two 6 mm gussets above the elbow housing -> variant SF 3.12 / 2.52,
    # final CAD 5.99 / 4.84 (run_structural)
    te, ty, tg, e = 0.010, 0.008, 0.006, 0.0005
    z_gus = -0.085                                             # gusset tip, 16 mm above the RS00 elbow housing
    p.gv("Elbow_z", mm(ze)); p.gv("Elbow_plate_t", mm(te)); p.gv("Yaw_plate_t", mm(ty))
    hy = [(u, v, CLR_M3) for (u, v, _) in bolt_holes((0, 0), XS["PCD_OUT"], XS["N_OUT"], CLR_M3)] + [(0, 0, 0.008)]
    plate2d(p, "Yaw_Plate", "z", -ty, 0.0, [(-0.025, yb - te), (0.025, yb - te), (0.025, 0.025), (-0.025, 0.025)], hy)
    circle_cut(p, "Yaw_Pilot_Recess", "z", 0.0, (0, 0, 0), XS["PILOT_D"] + 0.0003, XS["PILOT_H"] + 0.0002, into_positive=False)
    he = [((x, 0, z), CLR_M3) for (x, z, _) in [(u_, -v_, d_) for (u_, v_, d_) in bolt_holes((0, -ze), XS["PCD_REAR"], XS["N_REAR"], CLR_M3, 45)]]
    plate(p, "Elbow_Plate", "y", yb - te, yb, [(-0.030, 0, -ty), (0.030, 0, -ty), (0.030, 0, ze - 0.030), (-0.030, 0, ze - 0.030)],
          he + [((0, 0, ze), 0.014)])
    # gussets (normal x) inset 0.5 mm from the yaw-plate edges and overlapping both plates by 0.5 mm: coplanar start faces fail to merge
    for tag, x0 in (("Gusset_Front", 0.0185), ("Gusset_Back", -0.0245)):
        plate(p, tag, "x", x0, x0 + tg, [(0, yb - e, -ty + e), (0, 0.020, -ty + e), (0, yb - e, z_gus)])
    return finish(p, ALU_RGB, "shoulder yaw output -> elbow housing",
                  "6061-T6: elbow plate 10 mm, yaw plate 8 mm, 2x 6 mm gussets (laser-cut, bolted/welded); FEA SF 5.99/4.84")


def forearm(s):
    """forearm_link: elbow output face (y = +elbow_face_y, facing out) -> gripper mount at the hand frame (z = -180 mm)."""
    p = Part(s, f"JX1_Forearm_{SUF()}", CAD / "Arms" / f"JX1_Forearm_{SUF()}.SLDPRT")
    yo = UPK["elbow_face_y"]
    zh = HAND_OFF[2]
    t = 0.006
    p.gv("Forearm_length", mm(-zh))
    ho = [((x, 0, z), CLR_M3) for (x, z, _) in [(u_, -v_, d_) for (u_, v_, d_) in bolt_holes((0, 0), XS["PCD_OUT"], XS["N_OUT"], CLR_M3)]]
    plate(p, "Forearm_Plate", "y", yo, yo + t, [(-0.024, 0, 0.028), (0.024, 0, 0.028), (0.024, 0, zh), (-0.024, 0, zh)], ho + [((0, 0, 0), 0.008)])
    circle_cut(p, "Elbow_Pilot_Recess", "y", yo, (0, yo, 0), XS["PILOT_D"] + 0.0003, XS["PILOT_H"] + 0.0002, into_positive=True)
    plate2d(p, "Hand_Plate", "z", zh - t, zh, [(-0.024, -0.022), (0.024, -0.022), (0.024, yo + t), (-0.024, yo + t)], [(0, 0, 0.006)])
    return finish(p, ALU_RGB, "elbow output -> gripper mount", "6061-T6 6 mm plates, bolted; FEA SF 3.27/2.65")


def gripper(s):
    p = Part(s, "JX1_Gripper", CAD / "Arms" / "JX1_Gripper.SLDPRT")
    plate2d(p, "Body", "z", -0.066, -0.006, chamfer_rect(-0.030, -0.022, 0.030, 0.022, 0.006))
    for tag, y0 in (("Finger_A", 0.006), ("Finger_B", -0.016)):
        plate2d(p, tag, "z", -0.120, -0.066, [(-0.010, y0), (0.010, y0), (0.010, y0 + 0.010), (-0.010, y0 + 0.010)])
    return finish(p, PRINT_RGB, "parallel-jaw gripper (ST3215 + rack), envelope", "FDM PA-CF body + TPU finger pads; ASSUMED, 0.25 kg (BOM)")


# ------------------------------------------------------------------------------------------------ neck & head
def servo(s):
    L, W, H = UPK["servo_body"]
    a = UPK["servo_axis_from_end"]
    p = Part(s, "JX1_Servo_ST3215_Body", CAD / "Head" / "JX1_Servo_ST3215_Body.SLDPRT")
    plate2d(p, "Body", "z", -H, 0.0, [(-a, -W / 2), (L - a, -W / 2), (L - a, W / 2), (-a, W / 2)])
    p.ref_axis("Top Plane", "Right Plane", "AX_Joint")
    info = finish(p, SERVO_RGB, "Waveshare ST3215 serial bus servo body (servo frame: +Z output axis)",
                  "45.22 x 24.72 x 35 mm (VERIFIED waveshare.com), ~55 g")
    q = Part(s, "JX1_Servo_ST3215_Horn", CAD / "Head" / "JX1_Servo_ST3215_Horn.SLDPRT")
    with q.sketch("XY", "SK_Horn") as sk:
        sk.circle(0, 0, UPK["horn_d"] / 2)
    q.extrude("SK_Horn", UPK["horn_t"], "Horn")
    q.ref_axis("Top Plane", "Right Plane", "AX_Joint")
    finish(q, (0.7, 0.7, 0.72), "ST3215 output horn (aluminium disc)", "Ø20 x 3 mm")
    return info


def neck_bracket(s):
    p = Part(s, "JX1_NeckBracket", CAD / "Head" / "JX1_NeckBracket.SLDPRT")
    ht = UPK["horn_t"]
    L, W, H = UPK["servo_body"]
    zp = NP_OFF[2]
    yb = -H / 2                                                # pitch-servo body back face (servo spans y +-17.5 mm)
    plate2d(p, "Horn_Plate", "z", ht, ht + 0.004, [(-0.020, yb - 0.004), (0.040, yb - 0.004), (0.040, 0.012), (-0.020, 0.012)], [(0, 0, 0.004)])
    plate(p, "Servo_Plate", "y", yb - 0.004, yb, [(-0.020, 0, ht), (0.040, 0, ht), (0.040, 0, zp + W / 2 + 0.004), (-0.020, 0, zp + W / 2 + 0.004)])
    return finish(p, PRINT_RGB, "neck: yaw horn -> pitch servo body", "FDM PA-CF 4 mm; ASSUMED")


def head(s):
    p = Part(s, "JX1_Head", CAD / "Head" / "JX1_Head.SLDPRT")
    x0, x1, hy, z0, z1, t = -0.055, 0.070, 0.070, -0.015, 0.130, 0.003
    yh = UPK["neck_pitch_face_y"] + UPK["horn_t"]              # horn face: internal head plate starts here
    p.gv("Head_top_z", mm(z1))
    plate(p, "Front", "x", x1 - t, x1, [(0, -hy, z0), (0, hy, z0), (0, hy, z1), (0, -hy, z1)], [((0, 0.030, 0.042), 0.012), ((0, -0.030, 0.042), 0.012)])
    # rear-bottom chamfer: looking up (pitch -30 deg) with the neck yawed toward the back swings the rear-bottom corner over the
    # back plate / E-stop (top z 0.262 torso frame; interference 128 mm3 found by verify_upper_motion 2026-09-24). With the corner cut
    # from (x0, zc) to (xc, z0) every shell point outside r = 69.5 mm stays >= 6 mm above the back plate for pitch -30..+45 deg.
    xc, zc = -0.025, 0.003
    p.gv("Head_chamfer_x", mm(xc)); p.gv("Head_chamfer_z", mm(zc))
    plate(p, "Back", "x", x0, x0 + t, [(0, -hy, zc), (0, hy, zc), (0, hy, z1), (0, -hy, z1)])
    plate2d(p, "Top", "z", z1 - t, z1, [(x0, -hy), (x1, -hy), (x1, hy), (x0, hy)])
    for tag, y0 in (("Side_L", hy - t), ("Side_R", -hy)):
        plate(p, tag, "y", y0, y0 + t, [(xc, 0, z0), (x1, 0, z0), (x1, 0, z1), (x0, 0, z1), (x0, 0, zc)])
    plate(p, "Horn_Plate", "y", yh, yh + 0.004, [(-0.020, 0, -0.012), (0.040, 0, -0.012), (0.040, 0, z1), (-0.020, 0, z1)], [((0, 0, 0), 0.004)])
    info = finish(p, ACCENT_RGB, "head shell (open bottom) on the neck-pitch horn", "FDM PETG-CF 3 mm shell; ASSUMED, ~0.3 kg (BOM)")
    q = Part(s, "JX1_StereoCamera", CAD / "Head" / "JX1_StereoCamera.SLDPRT")
    plate2d(q, "Board", "z", 0.030, 0.054, [(x1 - t - 0.012, -0.0425), (x1 - t, -0.0425), (x1 - t, 0.0425), (x1 - t - 0.012, 0.0425)])
    finish(q, PCB_RGB, "Waveshare IMX219-83 stereo camera (2x 8 MP, 83 deg)", "board envelope 85 x 24 x 12 mm")
    return info


BUILDERS = {"torso": torso, "electronics": electronics, "shoulder_pitch": shoulder_pitch_bracket, "shoulder_roll": shoulder_roll_bracket,
            "upper_arm": upper_arm, "forearm": forearm, "gripper": gripper, "servo": servo, "neck": neck_bracket, "head": head}
SIDED = {"shoulder_pitch", "shoulder_roll", "upper_arm", "forearm"}


def main():
    args = sys.argv[1:]
    side = "L"
    if args and args[0] in ("--side", "-s"):
        side, args = args[1], args[2:]
    set_side(1 if side == "L" else -1)
    names = args or list(BUILDERS)
    if side == "R":
        names = [n for n in names if n in SIDED]
    s = Session()
    report = {}
    for n in names:
        info = BUILDERS[n](s)
        infos = info.values() if isinstance(info, dict) and "path" not in info else [info]
        for inf in infos:
            report[Path(inf["path"]).stem] = {k: inf[k] for k in ("bodies", "errors", "sketch_status")}
            bad = {k: v for k, v in inf["sketch_status"].items() if v != 3}
            print(Path(inf["path"]).stem, "bodies", inf["bodies"], "errors", inf["errors"], "underdefined", bad, flush=True)
    ev = ROOT / "verification" / "cad_build_upper_parts.json"
    old = json.loads(ev.read_text()) if ev.exists() else {}
    old.update(report)
    ev.write_text(json.dumps(old, indent=2, default=str))


if __name__ == "__main__":
    main()
