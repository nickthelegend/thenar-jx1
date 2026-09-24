"""JX0 printable-part geometry (millimetres, each part in its robot link frame: x forward, y left, z up).

Single source of truth for the SolidWorks builder (build_cad.py), the STL export and the simulation model. Every part is
a list of primitives:
    ("box",  (x0, x1), (y0, y1), (z0, z1))                 boss (axis-aligned block)
    ("cut",  (x0, x1), (y0, y1), (z0, z1))                 pocket
    ("cyl",  axis, (c0, c1), r, (s0, s1))                  boss cylinder along axis; c = the other two coords in xyz order
    ("hole", axis, (c0, c1), d, (s0, s1))                  cylindrical cut
Servo interface: Waveshare / Feetech ST3215 (research/raw/jx0_india_sourcing_raw.md, Waveshare 2D drawing): case 45.22 x
24.72 x 32 mm between the two horn faces, Ø19.2 horn on both faces (37.25 across them), output axis 10.11 mm from the
case end, horn holes 4 x Ø2.5 on a 14 mm circle, case mounting holes on the connector (rear) face 24.45 x 20.5 mm, first
row 18.41 mm from the output end. Screw sizes are not published: holes are Ø2.2 (M2 self-tapping) — ASSUMED, fit-check.
Arm and neck servos: MG90S (PWM) — dimensions ASSUMED (common datasheet values), fit-check.

Joints are single-sided: each servo's case is screwed to one link through its rear face, the next link bolts to its
output horn. All three hip axes meet at the hip centre and both ankle axes at the ankle centre (the gait model assumes it).
"""
from __future__ import annotations

# ------------------------------------------------------------------------------------------------ interface parameters
ST = dict(L=45.22, W=24.72, CASE=32.0, ENV=35.0, HORN_D=19.2, HORN_FACE=18.625, LA=10.11, LB=35.11,
          PCD=14.0, HORN_HOLE=2.7, MOUNT_L=(8.30, 32.75), MOUNT_W=10.25, SCREW=2.2, DISC_CLEAR=22.0)
MG = dict(L=22.8, W=12.2, H=28.4, LA=5.8, LB=17.0, SPLINE=4.0, TAB_SPAN=28.0, SCREW=2.2)   # MG90S, ASSUMED
T = 3.0            # plate thickness (PETG)
C = 0.4            # clearance
ZY = 30.0          # hip-yaw horn face above the hip centre
THIGH, SHIN = 100.0, 100.0
HIP_Y = 45.0       # half hip spacing
XR = -15.0         # hip-roll horn face (servo behind the hip centre, horn facing +x)
XA = -18.0         # ankle-roll horn face (servo behind the ankle centre, horn facing +x)
SOLE_TO_ANKLE, FOOT_X, FOOT_W = 35.0, (-62.0, 58.0), 70.0
TORSO = dict(x=(-40.0, 40.0), y=(-66.0, 66.0), z=(68.625, 196.0), wall=2.5)
SHOULDER = (0.0, 66.0, 176.0)
NECK_Z = 196.0


def horn_holes(axis, c, s, pcd=ST["PCD"], d=ST["HORN_HOLE"], centre=6.0):
    """4 horn screw holes on a circle + a centre clearance hole, through the plate range s along axis."""
    import math
    out = [("hole", axis, c, centre, s)] if centre else []
    for k in range(4):
        a = math.radians(45 + 90 * k)
        out.append(("hole", axis, (c[0] + pcd / 2 * math.cos(a), c[1] + pcd / 2 * math.sin(a)), d, s))
    return out


def rear_face_mount(axis, shaft_c, l_dir, w_dir, s):
    """ST3215 rear-face holder features on a plate: disc clearance + 4 case screw holes.
    shaft_c = shaft position in the plate's 2 other coords; l_dir / w_dir = unit direction (+-1, index 0/1) of the case
    length (from the shaft toward the long end) and width in those coords."""
    out = [("hole", axis, shaft_c, ST["DISC_CLEAR"], s)]
    li, ls = l_dir
    wi, _ = w_dir
    for lo in ST["MOUNT_L"]:
        for wo in (-ST["MOUNT_W"], ST["MOUNT_W"]):
            c = list(shaft_c)
            c[li] += ls * lo
            c[wi] += wo
            out.append(("hole", axis, tuple(c), ST["SCREW"], s))
    return out


def mirror_y(prims):
    """Right-side copy of a left-side part (y -> -y)."""
    out = []
    for p in prims:
        if p[0] in ("box", "cut"):
            out.append((p[0], p[1], (-p[2][1], -p[2][0]), p[3]))
        else:
            kind, axis, c, r, s = p
            if axis == "y":
                out.append((kind, axis, c, r, (-s[1], -s[0])))
            elif axis == "x":
                out.append((kind, axis, (-c[0], c[1]), r, s))
            else:
                out.append((kind, axis, (c[0], -c[1]), r, s))
    return out


# ------------------------------------------------------------------------------------------------ legs (left side)
def pelvis():
    zr = ZY + (ST["HORN_FACE"] - ST["CASE"] / 2) + ST["CASE"]          # yaw servo rear (connector) face = 64.625
    p = [("box", (-13.0, 38.0), (-62.0, 62.0), (zr, zr + 4.0)),                           # pelvis plate
         ("box", (-13.0, -10.6), (-62.0, 62.0), (zr - 14.0, zr + 0.5)),                   # rear rib
         ("box", (35.6, 38.0), (-62.0, 62.0), (zr - 14.0, zr + 0.5))]                     # front rib
    for sy in (1, -1):
        p += rear_face_mount("z", (0.0, sy * HIP_Y), (0, 1), (1, 1), (zr - 0.1, zr + 4.1))
    for x in (0.0, 28.0):
        for y in (-25.0, 25.0):
            p.append(("hole", "z", (x, y), 3.2, (zr - 0.1, zr + 4.1)))                   # torso bolts
    return p


def hip_yaw_bracket():
    """Bolts to the hip-yaw horn (above) and holds the hip-roll servo (axis x, behind the hip centre) by its rear face."""
    xr_rear = XR - (ST["HORN_FACE"] - ST["CASE"] / 2) - ST["CASE"]                     # roll servo rear face = -49.625
    p = [("box", (xr_rear - T, 12.0), (-16.0, 16.0), (ZY - T, ZY)),                     # plate on the yaw horn
         ("box", (xr_rear - T, xr_rear), (-38.0, 13.0), (-15.0, ZY)),                    # rear plate (servo mount)
         ("box", (xr_rear - 0.5, -24.0), (10.5, 13.5), (ZY - 12.0, ZY - 0.5)),          # gusset
         ("box", (xr_rear - 0.5, -24.0), (-16.0, -13.0), (ZY - 12.0, ZY - 0.5))]        # gusset
    p += horn_holes("z", (0.0, 0.0), (ZY - T - 0.1, ZY + 0.1))
    p += rear_face_mount("x", (0.0, 0.0), (0, -1), (1, 1), (xr_rear - T - 0.1, xr_rear + 0.1))
    return p


def hip_roll_bracket():
    """Bolts to the hip-roll horn (x = XR) and holds the hip-pitch servo (axis y, case forward) by its rear face (-y)."""
    yr = -(ST["HORN_FACE"] - (ST["HORN_FACE"] - ST["CASE"] / 2))                         # pitch servo rear face = -16
    p = [("box", (XR, XR + T), (-17.5, 17.5), (-15.0, 15.0)),                            # plate on the roll horn (clears the thigh)
         ("box", (XR + 0.5, 38.0), (yr - T, yr), (-15.0, 15.0)),                         # rear plate of the pitch servo
         ("box", (XR + 0.5, XR + 12.0), (yr - T + 0.5, -2.0), (-15.0, -12.0))]           # gusset
    p += horn_holes("x", (0.0, 0.0), (XR - 0.1, XR + T + 0.1))
    p += rear_face_mount("y", (0.0, 0.0), (0, 1), (1, 1), (yr - T - 0.1, yr + 0.1))
    return p


def thigh():
    """Bolts to the hip-pitch horn (outside, +y) and carries the knee servo on its inner face (case up, horn -y)."""
    y0 = ST["HORN_FACE"]
    p = [("box", (-15.0, 15.0), (y0, y0 + 4.0), (-THIGH - 15.0, 14.0)),                  # 4 mm side plate
         ("box", (-15.0, -11.0), (y0 + 3.5, y0 + 9.0), (-THIGH + 20.0, -5.0)),           # rear flange (stiffener)
         ("box", (11.0, 15.0), (y0 + 3.5, y0 + 9.0), (-THIGH + 20.0, -5.0))]             # front flange
    p += horn_holes("y", (0.0, 0.0), (y0 - 0.1, y0 + 4.1))
    p += rear_face_mount("y", (0.0, -THIGH), (1, 1), (0, 1), (y0 - 0.1, y0 + 4.1))
    return p


def shin():
    """Bolts to the knee horn (inside, -y) and carries the ankle-pitch servo on its outer face (case up, horn +y).
    The knee servo's rear face sits on the thigh plate at y = +18.625, so its horn face is at 18.625 - 32 - 2.625 = -16."""
    y1 = ST["HORN_FACE"] - ST["CASE"] - (ST["HORN_FACE"] - ST["CASE"] / 2)
    p = [("box", (-15.0, 15.0), (y1 - 4.0, y1), (-SHIN - 12.0, 13.0)),
         ("box", (-15.0, -11.0), (y1 - 9.0, y1 - 3.5), (-SHIN + 22.0, -15.0)),
         ("box", (11.0, 15.0), (y1 - 9.0, y1 - 3.5), (-SHIN + 22.0, -15.0))]
    p += horn_holes("y", (0.0, 0.0), (y1 - 4.1, y1 + 0.1))
    # ankle-pitch servo: rear face on the plate's inner side at y = -16 (horn outward at +18.625)
    p += rear_face_mount("y", (0.0, -SHIN), (1, 1), (0, 1), (y1 - 4.1, y1 + 0.1))
    return p


def ankle_bracket():
    """Bolts to the ankle-pitch horn (+y) and holds the ankle-roll servo (axis x, behind the ankle) by its rear face."""
    y0 = ST["HORN_FACE"]
    xa_rear = XA - (ST["HORN_FACE"] - ST["CASE"] / 2) - ST["CASE"]                     # roll servo rear face = -52.625
    p = [("box", (xa_rear - T, 14.0), (y0, y0 + T), (-15.0, 15.0)),                     # side plate on the pitch horn
         ("box", (xa_rear - T, xa_rear), (-38.0, y0 + 0.5), (-15.0, 15.0)),              # rear plate (roll servo mount)
         ("box", (xa_rear - 0.5, -24.0), (y0 - 3.0, y0 + 0.5), (-15.0, -12.0))]          # gusset
    p += horn_holes("y", (0.0, 0.0), (y0 - 0.1, y0 + T + 0.1))
    p += rear_face_mount("x", (0.0, 0.0), (0, -1), (1, 1), (xa_rear - T - 0.1, xa_rear + 0.1))
    return p


def foot():
    """Sole plate + an upright that bolts to the ankle-roll horn (x = XA). Symmetric: one part for both feet."""
    zs = -SOLE_TO_ANKLE
    p = [("box", FOOT_X, (-FOOT_W / 2, FOOT_W / 2), (zs, zs + 6.0)),                     # sole plate
         ("box", (XA, XA + T), (-15.0, 15.0), (zs + 5.5, 12.0)),                         # upright on the roll horn
         ("box", (XA + 2.5, XA + 6.0), (-15.0, 15.0), (zs + 5.5, -20.0))]                # heel block
    p += horn_holes("x", (0.0, 0.0), (XA - 0.1, XA + T + 0.1))
    for x in (-50.0, -20.0, 20.0, 45.0):
        p.append(("hole", "z", (x, 0.0), 12.0, (zs - 0.1, zs + 6.1)))                   # lightening
    return p


# ------------------------------------------------------------------------------------------------ upper body
def torso():
    x0, x1 = TORSO["x"]
    y0, y1 = TORSO["y"]
    z0, z1 = TORSO["z"]
    w = TORSO["wall"]
    p = [("box", (x0, x1), (y0, y1), (z0, z1)),
         ("cut", (x0 - 1.0, x1 - w), (y0 + w, y1 - w), (z0 + w, z1 - w))]                # open back
    for x in (0.0, 28.0):
        for y in (-25.0, 25.0):
            p.append(("hole", "z", (x, y), 3.2, (z0 - 0.1, z0 + w + 0.1)))
    for y in (-12.0, -6.0, 0.0, 6.0, 12.0):                                              # speaker grille
        for z in (86.0, 93.0):
            p.append(("hole", "x", (y, z), 3.0, (x1 - w - 0.1, x1 + 0.1)))
    p.append(("hole", "x", (0.0, 104.0), 12.0, (x1 - w - 0.1, x1 + 0.1)))                # push-to-talk button
    for y in (-29.0, 29.0):                                                              # Raspberry Pi standoffs
        for z in (115.5, 164.5):
            p.append(("cyl", "x", (y, z), 3.0, (x1 - w - 7.0, x1 - w + 0.5)))
            p.append(("hole", "x", (y, z), 2.2, (x1 - w - 7.1, x1 - w + 0.6)))
    # shoulder-pitch MG90S holders (horn out through the side walls) and the neck MG90S holder (horn up)
    sx, _, sz = SHOULDER
    for sgn in (1, -1):
        yin, yout = sgn * (y1 - w - 20.0), sgn * (y1 - w + 0.5)
        p.append(("box", (sx - MG["LA"] - C - 2.0, sx + MG["LB"] + C + 2.0), tuple(sorted((yin, yout))), (sz - 8.5, sz + 8.5)))
        p.append(("cut", (sx - MG["LA"] - C, sx + MG["LB"] + C), tuple(sorted((yin - sgn * 0.1, yout))), (sz - MG["W"] / 2 - C, sz + MG["W"] / 2 + C)))
        p.append(("hole", "y", (sx, sz), 11.0, tuple(sorted((sgn * (y1 - w - 0.1), sgn * (y1 + 0.1))))))
    p.append(("box", (-MG["LB"] - C - 2.0, MG["LA"] + C + 2.0), (-8.5, 8.5), (z1 - w - 22.0, z1 - w + 0.5)))
    p.append(("cut", (-MG["LB"] - C, MG["LA"] + C), (-MG["W"] / 2 - C, MG["W"] / 2 + C), (z1 - w - 22.1, z1 - w + 0.1)))
    p.append(("hole", "z", (0.0, 0.0), 11.0, (z1 - w - 0.1, z1 + 0.1)))
    return p


def head():
    """Head shell (frame: neck horn top, 1.5 mm above the torso top): round 1.28" display window in the face."""
    p = [("box", (-35.0, 35.0), (-40.0, 40.0), (0.0, 72.0)),
         ("cut", (-36.0, 32.5), (-37.5, 37.5), (2.5, 69.5)),
         ("hole", "x", (0.0, 38.0), 33.0, (32.4, 35.1)),                                 # GC9A01 active area Ø32.4
         ("hole", "z", (0.0, 0.0), 3.0, (-0.1, 2.6))]
    for x, y in ((0.0, 7.0), (0.0, -7.0)):
        p.append(("hole", "z", (x, y), 1.6, (-0.1, 2.6)))                               # MG90S horn screws
    return p


def shoulder_bracket():
    """Arm link 1 (frame at the shoulder-pitch axis on the torso side wall; y outward): holds the shoulder-roll MG90S."""
    yc, zc = 10.0, -16.0
    p = [("box", (-10.0, 10.0), (1.5, 4.0), (-34.0, 8.0)),
         ("box", (-MG["H"] + 11.4 - 2.0, 11.4), (yc - MG["W"] / 2 - C - 2.0, yc + MG["W"] / 2 + C + 2.0), (zc - MG["LB"] - C - 2.0, zc + MG["LA"] + C + 2.0)),
         ("cut", (-MG["H"] + 11.4 - 2.1, 11.5), (yc - MG["W"] / 2 - C, yc + MG["W"] / 2 + C), (zc - MG["LB"] - C, zc + MG["LA"] + C)),
         ("hole", "y", (0.0, 0.0), 3.0, (1.4, 4.1))]
    return p


def upper_arm():
    """Arm link 2 (frame at the shoulder-roll axis): hangs from the roll horn, holds the elbow MG90S (axis y)."""
    ze = -55.0
    p = [("box", (15.4, 17.9), (-7.0, 7.0), (ze - 8.0, 8.0)),
         ("box", (-0.5, 16.5), (-MG["H"] / 2, MG["H"] / 2), (ze - MG["LA"] - C - 2.0, ze + MG["LB"] + C + 2.0)),
         ("cut", (1.5, 14.5), (-MG["H"] / 2 - 0.1, MG["H"] / 2 + 0.1), (ze - MG["LA"] - C, ze + MG["LB"] + C)),
         ("hole", "x", (0.0, 0.0), 3.0, (15.3, 18.0))]
    return p


def forearm():
    """Arm link 3 (frame at the elbow axis): plate on the elbow horn and a hand block."""
    y0 = MG["H"] / 2 + MG["SPLINE"]
    return [("box", (-9.0, 9.0), (y0, y0 + 2.5), (-72.0, 8.0)),
            ("box", (-10.0, 10.0), (y0 - 14.0, y0 + 0.5), (-88.0, -70.0)),
            ("hole", "y", (0.0, 0.0), 3.0, (y0 - 0.1, y0 + 2.6))]


# ------------------------------------------------------------------------------------------------ catalogue
# name -> (primitives, colour, quantity, mirrored-from). Right-side parts are generated by mirroring the left ones.
PARTS = {
    "JX0_Pelvis": (pelvis(), "white", 1),
    "JX0_HipYawBracket_L": (hip_yaw_bracket(), "white", 1),
    "JX0_HipYawBracket_R": (mirror_y(hip_yaw_bracket()), "white", 1),
    "JX0_HipRollBracket_L": (hip_roll_bracket(), "white", 1),
    "JX0_HipRollBracket_R": (mirror_y(hip_roll_bracket()), "white", 1),
    "JX0_Thigh_L": (thigh(), "white", 1),
    "JX0_Thigh_R": (mirror_y(thigh()), "white", 1),
    "JX0_Shin_L": (shin(), "white", 1),
    "JX0_Shin_R": (mirror_y(shin()), "white", 1),
    "JX0_AnkleBracket_L": (ankle_bracket(), "white", 1),
    "JX0_AnkleBracket_R": (mirror_y(ankle_bracket()), "white", 1),
    "JX0_Foot": (foot(), "white", 2),
    "JX0_Torso": (torso(), "white", 1),
    "JX0_Head": (head(), "orange", 1),
    "JX0_ShoulderBracket_L": (shoulder_bracket(), "white", 1),
    "JX0_ShoulderBracket_R": (mirror_y(shoulder_bracket()), "white", 1),
    "JX0_UpperArm": (upper_arm(), "white", 2),
    "JX0_Forearm_L": (forearm(), "white", 1),
    "JX0_Forearm_R": (mirror_y(forearm()), "white", 1),
}


def servo_st():
    """ST3215 stand-in (frame: shaft axis = z, output horn face at z = +HORN_FACE, case length toward +x)."""
    hf, case = ST["HORN_FACE"], ST["CASE"]
    return [("box", (-ST["LA"], ST["LB"]), (-ST["W"] / 2, ST["W"] / 2), (-case / 2, case / 2)),
            ("cyl", "z", (0.0, 0.0), ST["HORN_D"] / 2, (case / 2 - 0.5, hf)),
            ("cyl", "z", (0.0, 0.0), ST["HORN_D"] / 2, (-hf, -case / 2 + 0.5))] + horn_holes("z", (0.0, 0.0), (hf - 1.0, hf + 0.1), centre=0)


def servo_mg():
    """MG90S stand-in (frame: shaft axis = z, spline top at z = 0; case length toward +x)."""
    return [("box", (-MG["LA"], MG["LB"]), (-MG["W"] / 2, MG["W"] / 2), (-MG["H"] - MG["SPLINE"], -MG["SPLINE"])),
            ("box", (-MG["LA"] - 5.0, MG["LB"] + 5.0), (-MG["W"] / 2, MG["W"] / 2), (-MG["SPLINE"] - 10.0, -MG["SPLINE"] - 7.5)),
            ("cyl", "z", (0.0, 0.0), 2.4, (-MG["SPLINE"] - 0.5, 0.0))]


SERVOS = {"JX0_Servo_ST3215": (servo_st(), "black", 12), "JX0_Servo_MG90S": (servo_mg(), "blue", 7)}


def bbox(prims):
    """Expected bounding box of the bosses (mm) for the CAD check."""
    lo, hi = [1e9] * 3, [-1e9] * 3
    for p in prims:
        if p[0] == "box":
            for k in range(3):
                lo[k], hi[k] = min(lo[k], p[k + 1][0]), max(hi[k], p[k + 1][1])
        elif p[0] == "cyl":
            _, axis, c, r, s = p
            ia = "xyz".index(axis)
            others = [i for i in range(3) if i != ia]
            lo[ia], hi[ia] = min(lo[ia], s[0]), max(hi[ia], s[1])
            for i, cv in zip(others, c):
                lo[i], hi[i] = min(lo[i], cv - r), max(hi[i], cv + r)
    return lo, hi
