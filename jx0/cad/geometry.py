"""JX0 printable-part geometry (millimetres, each part in its robot link frame: x forward, y left, z up).

Single source of truth for the SolidWorks builder (build_cad.py), the STL export and the simulation model. Every part is
a list of primitives:
    ("box",  (x0, x1), (y0, y1), (z0, z1))                 boss (axis-aligned block)
    ("cut",  (x0, x1), (y0, y1), (z0, z1))                 pocket
    ("cyl",  axis, (c0, c1), r, (s0, s1))                  boss cylinder along axis; c = the other two coords in xyz order
    ("hole", axis, (c0, c1), d, (s0, s1))                  cylindrical cut
    ("prism"/"pcut", axis, profile, (s0, s1))              extruded profile (true arcs allowed, see path_points)
Servo interface: Feetech STS3215 12 V (Waveshare ST3215; research/raw/jx0_india_sourcing_raw.md, Waveshare 2D drawing): case 45.22 x
24.72 x 32 mm between the two horn faces, Ø19.2 horn on both faces (37.25 across them): the output horn on one face and
a passive hub on the rear face, output axis 10.11 mm from the case end, horn holes 4 x Ø2.5 on a 14 mm circle, case
mounting holes on the rear face 20.5 mm apart along the case and 24.45 mm across, first row 18.41 mm from the output
end. Screw sizes are not published: holes are Ø2.2 (M2 self-tapping) — ASSUMED, fit-check. The rear hub's screw
pattern is ASSUMED equal to the horn's (fit-check; if it has only a centre hole, the U-bracket arm takes one M3 screw).
Every joint (12 leg, 4 arm, 1 neck) is the same 12 V STS3215.

v0.4 — legs like the reference robot (media/reference.mp4): every leg pitch and roll joint is DOUBLE-SIDED. The servo's
case sits in a cage on one link (four walls + a rear plate screwed to the case); the next link is a U-bracket that grabs
the servo on both sides, the output horn and the rear hub, so the joint's load passes through both faces instead of
bending the output shaft. Each hip-yaw servo carries its leg through a thrust ring under the pelvis. Short legs (62 mm
thigh, 58 mm shin, ankle 33 mm above the floor, as measured on the reference) under a tall torso whose skirt hides the
hip-yaw servos; the knee servo lies forward, which gives the thigh the reference's dog-leg plate. Arms: the shoulder
servo hangs outside the chest in a hood (its horn bolted to a pad on the chest wall), the elbow servo in a box under it,
and a thick paddle blade, as on the reference robot.
All three hip axes meet at the hip centre and both ankle axes at the ankle centre (the gait model assumes it).
"""
from __future__ import annotations

# ------------------------------------------------------------------------------------------------ interface parameters
ST = dict(L=45.22, W=24.72, CASE=32.0, ENV=35.0, HORN_D=19.2, HORN_FACE=18.625, LA=10.11, LB=35.11,
          PCD=14.0, HORN_HOLE=2.7, MOUNT_L=(8.30, 32.75), MOUNT_W=10.25, SCREW=2.2, DISC_CLEAR=22.0)
T = 3.0            # plate thickness (PETG)
C = 0.4            # clearance
HF, HC, HW = ST["HORN_FACE"], ST["CASE"] / 2, ST["W"] / 2      # horn face, case half thickness, case half width
WALL = 2.5         # servo cage wall
RP = 2.4           # cage rear plate: the case screws through it; the rear hub stands 0.2 mm proud of it, so a
                   # U-bracket's boss slides over it onto the hub when the bracket is fitted (assembly)
TU = 4.5           # U-bracket arm plate (verify_fea)
BOSS_H, BOSS_R = 2.0, 9.0     # U-bracket boss on the rear hub (keeps the arm 2 mm clear of the cage's rear plate)
ZY = 30.0          # hip-yaw horn face above the hip centre
YAW_DISC_T = 9.0   # hip-yaw bracket disc on the yaw horn (rides under the thrust ring); 9 mm: verify_fea
THIGH, SHIN = 62.0, 58.0
HIP_Y = 45.0       # half hip spacing
XR = -14.01        # hip-roll horn face (servo behind the hip centre, horn facing +x); its U-bracket's front arm is the
                   # back wall of the hip-pitch cage
XA = -22.0         # ankle-roll horn face (servo behind the ankle centre, horn facing +x)
SOLE_TO_ANKLE, SOLE_T, FOOT_X, FOOT_W = 33.0, 5.0, (-68.0, 56.0), 70.0
# torso: octagonal prism, half depth TD (x) and half width TW (y), vertical edges chamfered TCH, split at TZS into the
# lower shell and the chest cap; walls TWALL. TZB: bottom of the skirt that hides the hip-yaw servos; TZ0: the floor
TD, TW, TCH, TWALL = 42.0, 60.0, 16.0, 2.5
TZB, TZ0, TZS, TZT, TOP_CH = 33.0, 68.625, 168.0, 210.0, 8.0
# shoulder pitch: the servo hangs outside the chest; its horn bolts to a pad on the chest side wall (horn face y = 63)
SHOULDER = (12.5, TW + 3.0, 186.0)
UA_L = 52.0                                                         # shoulder pitch axis to elbow axis
ELBOW_Y = 39.25                                                     # elbow horn face, outboard of the shoulder horn face
BLADE_L, BLADE_T = 100.0, 6.0
# printed mass / solid mass. Body parts: 3 walls + 25 % gyroid. Pelvis and leg brackets (PETG): 6 walls, 6 top and
# bottom layers, 40 % gyroid, so their 2.4-4.5 mm plates print solid, as the finite-element check assumes (verify_fea)
FILL_BODY, FILL_LEG = 0.55, 0.80
LEG_PARTS = ("JX0_Pelvis", "JX0_HipYawBracket", "JX0_HipRollBracket", "JX0_Thigh", "JX0_Shin", "JX0_AnkleBracket", "JX0_Foot")


def fill(name):
    return FILL_LEG if name.startswith(LEG_PARTS) else FILL_BODY
NECK_Z = TZT + ST["CASE"] + (HF - HC)                               # neck horn face (head origin): 244.625


def horn_holes(axis, c, s, pcd=ST["PCD"], d=ST["HORN_HOLE"], centre=6.0):
    """4 horn screw holes on a circle + a centre clearance hole, through the plate range s along axis."""
    import math
    out = [("hole", axis, c, centre, s)] if centre else []
    for k in range(4):
        a = math.radians(90 * k)
        out.append(("hole", axis, (c[0] + pcd / 2 * math.cos(a), c[1] + pcd / 2 * math.sin(a)), d, s))
    return out


def rear_face_mount(axis, shaft_c, l_dir, w_dir, s):
    """STS3215 rear-face holder features on a plate: disc clearance + 4 case screw holes.
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


BOSSES, CUTS = ("box", "cyl", "prism"), ("cut", "hole", "pcut")


def base_kind(kind):
    """"lbox" -> "box": the "l" (late) variants are applied after the ordinary cuts, e.g. mounts inside a hollow shell."""
    return kind[1:] if kind.startswith("l") and kind[1:] in BOSSES + CUTS else kind


def phase(prim):
    """Build order: 0 bosses, 1 cuts, 2 late bosses, 3 late cuts."""
    k = prim[0]
    return (2 if base_kind(k) != k else 0) + (1 if base_kind(k) in CUTS else 0)


def mirror_y(prims):
    """Right-side copy of a left-side part (y -> -y)."""
    out = []
    for p in prims:
        k = base_kind(p[0])
        if k in ("box", "cut"):
            out.append((p[0], p[1], (-p[2][1], -p[2][0]), p[3]))
        elif k in ("prism", "pcut"):
            kind, axis, pts, s = p
            if axis == "y":
                out.append((kind, axis, pts, (-s[1], -s[0])))
            else:
                f = (lambda a, b: (-a, b)) if axis == "x" else (lambda a, b: (a, -b))
                out.append((kind, axis, [("arc", f(*e[1])) if is_arc(e) else f(*e) for e in pts], s))
        else:
            kind, axis, c, r, s = p
            if axis == "y":
                out.append((kind, axis, c, r, (-s[1], -s[0])))
            elif axis == "x":
                out.append((kind, axis, (-c[0], c[1]), r, s))
            else:
                out.append((kind, axis, (c[0], -c[1]), r, s))
    return out


# ------------------------------------------------------------------------------------------------ profile helpers
def _unit(u, v):
    import math
    n = math.hypot(u, v)
    return u / n, v / n


# Profiles are lists of vertices (u, v) with optional ("arc", (um, vm)) entries between two vertices: a true arc from the
# previous vertex through (um, vm) to the next. SolidWorks gets real arcs (smooth surfaces); path_points() traces them
# for the preview, the bounding-box check and anything else that needs a plain polygon.
def is_arc(e):
    return isinstance(e, tuple) and len(e) == 2 and e[0] == "arc"


def path_points(path, n=16):
    """The profile as a plain polygon, each arc traced with n segments."""
    import math
    verts = [e for e in path if not is_arc(e)]
    mids, k = {}, -1
    for e in path:
        if is_arc(e):
            mids[k] = e[1]
        else:
            k += 1
    out = []
    for i, a in enumerate(verts):
        out.append(a)
        if i in mids:
            b, mpt = verts[(i + 1) % len(verts)], mids[i]
            ax, ay, bx, by, mx, my = a[0], a[1], b[0], b[1], mpt[0], mpt[1]
            d = 2 * (ax * (my - by) + mx * (by - ay) + bx * (ay - my))
            cx = ((ax * ax + ay * ay) * (my - by) + (mx * mx + my * my) * (by - ay) + (bx * bx + by * by) * (ay - my)) / d
            cy = ((ax * ax + ay * ay) * (bx - mx) + (mx * mx + my * my) * (ax - bx) + (bx * bx + by * by) * (mx - ax)) / d
            r = math.hypot(ax - cx, ay - cy)
            t0, tm, t1 = (math.atan2(p[1] - cy, p[0] - cx) for p in (a, mpt, b))
            sweep = (t1 - t0) % (2 * math.pi)
            if not (0 < (tm - t0) % (2 * math.pi) < sweep):          # the arc runs the other way round
                sweep -= 2 * math.pi
            out += [(cx + r * math.cos(t0 + sweep * j / n), cy + r * math.sin(t0 + sweep * j / n)) for j in range(1, n)]
    return out


def rounded_polygon(corners, radii):
    """Convex polygon (u, v) with each corner filleted by a true arc (radius 0, or a corner that barely turns, = sharp)."""
    import math
    out, m = [], len(corners)
    for i, (P, r) in enumerate(zip(corners, radii)):
        A, B = corners[i - 1], corners[(i + 1) % m]
        u1, u2 = _unit(A[0] - P[0], A[1] - P[1]), _unit(B[0] - P[0], B[1] - P[1])
        half = math.acos(max(-1.0, min(1.0, u1[0] * u2[0] + u1[1] * u2[1]))) / 2
        if r <= 0 or math.pi - 2 * half < math.radians(8):
            out.append(P)
            continue
        d, bis = r / math.tan(half), _unit(u1[0] + u2[0], u1[1] + u2[1])
        cu, cv = P[0] + bis[0] * r / math.sin(half), P[1] + bis[1] * r / math.sin(half)
        t1 = (round(P[0] + u1[0] * d, 4), round(P[1] + u1[1] * d, 4))
        t2 = (round(P[0] + u2[0] * d, 4), round(P[1] + u2[1] * d, 4))
        mid = (round(cu - bis[0] * r, 4), round(cv - bis[1] * r, 4))
        out += [t1, ("arc", mid), t2]
    return out


def corner_cut(c, inward, r, e=0.6):
    """Profile of the material outside a fillet of radius r at the solid's corner c; inward = (+-1, +-1) into the solid."""
    import math
    (uc, vc), (du, dv) = c, inward
    cu, cv = uc + du * r, vc + dv * r
    mid = (round(cu - du * r * math.sin(math.pi / 4), 4), round(cv - dv * r * math.cos(math.pi / 4), 4))
    return [(uc - du * e, vc - dv * e), (uc + du * r, vc - dv * e), (uc + du * r, vc), ("arc", mid), (uc, vc + dv * r),
            (uc - du * e, vc + dv * r)]


def chamfer_cut(c, inward, ch, e=0.6):
    """Triangle removing a 45° chamfer of leg ch at the solid's corner c (inward as in corner_cut)."""
    (uc, vc), (du, dv) = c, inward
    return [(uc - du * e, vc - dv * e), (uc + du * (ch + e), vc - dv * e), (uc - du * e, vc + dv * (ch + e))]


def octagon(hx, hy, c):
    """Rectangle +-hx, +-hy with its 4 corners chamfered by c, as (x, y) points."""
    return [(hx, -hy + c), (hx, hy - c), (hx - c, hy), (-hx + c, hy), (-hx, hy - c), (-hx, -hy + c), (-hx + c, -hy), (hx - c, -hy)]


def oct_inset(d):
    """The torso octagon inset by d (the 45° faces move in by d too)."""
    return octagon(TD - d, TW - d, TCH - d * (2 - 2 ** 0.5))


def late(prims):
    """The same features, built after the ordinary cuts (for mounts inside a hollow shell)."""
    return [("l" + q[0],) + tuple(q[1:]) for q in prims]


# ------------------------------------------------------------------------------------------------ servo cage + U-bracket
def _rng(a, b):
    return (min(a, b), max(a, b))


def _box(r):
    """r = {'x': (a, b), 'y': ..., 'z': ...} -> box primitive."""
    return ("box", _rng(*r["x"]), _rng(*r["y"]), _rng(*r["z"]))


def _others(axis):
    return [k for k in "xyz" if k != axis]


class Servo:
    """An STS3215 placed in a part frame: c = centre (the shaft, on the case's mid-plane), a = shaft axis, hs = +-1 the
    side of the output horn along a, l = (axis, +-1) from the shaft toward the case's long end; w = the third axis."""

    def __init__(self, c, a, hs, l):
        self.c = dict(zip("xyz", map(float, c)))
        self.a, self.hs = a, hs
        self.l, self.ls = l
        self.w = next(k for k in "xyz" if k not in (a, self.l))

    def l_range(self, grow=0.0):
        lo, hi = (-ST["LA"], ST["LB"]) if self.ls > 0 else (-ST["LB"], ST["LA"])
        return self.c[self.l] + lo - grow, self.c[self.l] + hi + grow

    def shaft2(self):
        return tuple(self.c[k] for k in _others(self.a))


def cage(S, rp=RP, wall=WALL, skip=(), thin=None, ext=0.0, omit=None, counterbore=False):
    """The case holder of servo S: a rear plate (case screws, the rear hub's clearance hole) and four walls around the
    case, open on the horn side (the servo slides in from there). thin = {wall: thickness} overrides; skip = walls left
    out ('l0' / 'l1' the case ends, 'w0' / 'w1' its sides); ext = walls reach this far past the case's horn-side face
    (for plates that join the cage to a U-bracket arm there). The plate is 2.4 mm so the rear hub stands 0.2 mm proud
    of it: the U-bracket's boss slides over the plate onto the hub when the bracket is fitted; omit = -1 / +1 leaves
    out the near case screw on that side of the width axis, the one in the boss's way (three screws + the walls hold
    the case). counterbore: screw heads sunk 2 mm (thick plates only)."""
    thin = thin or {}
    t = {k: thin.get(k, wall) for k in ("l0", "l1", "w0", "w1")}
    a0 = S.c[S.a]
    rear_in, rear_out = a0 - S.hs * HC, a0 - S.hs * (HC + rp)
    A = _rng(rear_out, a0 + S.hs * (HC + ext))
    l0, l1 = S.l_range(C)
    w0, w1 = S.c[S.w] - HW - C, S.c[S.w] + HW + C
    L, W = (l0 - t["l0"], l1 + t["l1"]), (w0 - t["w0"], w1 + t["w1"])
    walls = {"l0": ((l0 - t["l0"], l0), W), "l1": ((l1, l1 + t["l1"]), W),
             "w0": (L, (w0 - t["w0"], w0)), "w1": (L, (w1, w1 + t["w1"]))}
    out = [_box({S.a: A, S.l: lr, S.w: wr}) for k, (lr, wr) in walls.items() if k not in skip]
    pr = _rng(rear_in, rear_out)
    out.append(_box({S.a: pr, S.l: L, S.w: W}))
    o = _others(S.a)
    sc = S.shaft2()
    span = (pr[0] - 0.1, pr[1] + 0.1)
    out.append(("hole", S.a, sc, ST["DISC_CLEAR"], span))
    cb = _rng(rear_out, rear_out + S.hs * 2.0)
    cb = (cb[0] - 0.1, cb[1]) if rear_out < rear_in else (cb[0], cb[1] + 0.1)
    for lo in ST["MOUNT_L"]:
        for ws in (-1, 1):
            if omit == ws and lo == ST["MOUNT_L"][0]:
                continue
            c = list(sc)
            c[o.index(S.l)] += S.ls * lo
            c[o.index(S.w)] += ws * ST["MOUNT_W"]
            out.append(("hole", S.a, tuple(c), ST["SCREW"], span))
            if counterbore:
                out.append(("hole", S.a, tuple(c), 4.2, cb))
    return out


def u_arms(S, prof_horn, prof_hub=None, extra_horn=(), extra_hub=(), tu_horn=TU):
    """U-bracket around servo S: one arm on the output horn, one on the rear hub (a 2 mm boss keeps that arm clear of the
    cage's rear plate), each an extrusion of its (u, v) profile (the two coords other than the shaft axis, xyz order),
    with the horn's 4-screw cross pattern. extra_* = more profiles fused to each arm (same thickness)."""
    prof_hub = prof_hub or prof_horn
    a0, sc = S.c[S.a], S.shaft2()
    h = _rng(a0 + S.hs * HF, a0 + S.hs * (HF + tu_horn))
    b = _rng(a0 - S.hs * HF, a0 - S.hs * (HF + BOSS_H))
    p = _rng(a0 - S.hs * (HF + BOSS_H), a0 - S.hs * (HF + BOSS_H + TU))
    out = [("prism", S.a, prof_horn, h), ("cyl", S.a, sc, BOSS_R, b), ("prism", S.a, prof_hub, p)]
    out += [("prism", S.a, e, h) for e in extra_horn] + [("prism", S.a, e, p) for e in extra_hub]
    out += horn_holes(S.a, sc, (h[0] - 0.1, h[1] + 0.1))
    out += horn_holes(S.a, sc, (min(b[0], p[0]) - 0.1, max(b[1], p[1]) + 0.1))
    return out


def rect(u0, u1, v0, v1, r=0.0):
    pts = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    return rounded_polygon(pts, [r] * 4) if r > 0 else pts


# ------------------------------------------------------------------------------------------------ the servos (left leg)
def yaw_servo(sy=1):                       # pelvis frame: horn down, case toward the robot's middle
    return Servo((0.0, sy * HIP_Y, ZY + HF), "z", -1, ("y", -sy))


def roll_servo():                          # hip frame: behind the hip centre, horn forward, case toward the middle
    return Servo((XR - HF, 0.0, 0.0), "x", +1, ("y", -1))


def pitch_servo():                         # hip frame: on the hip centre, horn outward, case forward
    return Servo((0.0, 0.0, 0.0), "y", +1, ("x", +1))


def knee_servo(z=-THIGH):                  # hip frame (thigh): lying forward, horn outward
    return Servo((0.0, 0.0, z), "y", +1, ("x", +1))


def ankle_pitch_servo(z=-SHIN):            # knee frame (shin): standing up, horn outward
    return Servo((0.0, 0.0, z), "y", +1, ("z", +1))


def ankle_roll_servo():                    # ankle frame: behind the ankle centre, horn forward, case toward the middle
    return Servo((XA - HF, 0.0, 0.0), "x", +1, ("y", -1))


# ------------------------------------------------------------------------------------------------ legs (left side)
def pelvis():
    """Inside the torso skirt: the two hip-yaw servo cages hang from a plate bolted under the torso floor, each with a
    thrust ring under it. The hip-yaw bracket rides 0.3 mm under the ring, so the leg's load in stance goes into the
    pelvis through the ring, not through the yaw servo's output shaft (PTFE tape or grease on the ring)."""
    zr = ZY + HF + HC                                                         # yaw case top (rear face) = 64.625
    plate = [(28.0, -50.0), (28.0, 50.0), (21.0, 57.0), (-24.0, 57.0), (-24.0, -57.0), (21.0, -57.0)]
    p = [("prism", "z", plate, (zr, TZ0)),
         ("box", (24.5, 28.0), (-45.0, 45.0), (zr - 14.0, zr + 0.5)),                       # front rib
         ("box", (-24.0, -20.5), (-45.0, 45.0), (zr - 14.0, zr + 0.5))]                     # rear rib
    for sy in (1, -1):
        p += cage(yaw_servo(sy), rp=TZ0 - zr, thin={"l1": 1.2} if sy > 0 else {"l0": 1.2}, counterbore=True)
        p += [("cyl", "z", (0.0, sy * HIP_Y), 19.0, (ZY + 0.3, ZY + HF - HC)),             # thrust ring
              ("hole", "z", (0.0, sy * HIP_Y), 23.0, (ZY + 0.2, ZY + HF - HC + 0.1))]
    for x in (-20.0, 24.0):                                                                 # bolts to the torso floor
        for y in (-25.0, 25.0):
            p.append(("hole", "z", (x, y), 3.2, (zr - 0.1, TZ0 + 0.1)))
    return p


def hip_yaw_bracket():
    """A 7 mm disc on the hip-yaw horn (it rides under the thrust ring), a keel under its centre, and a solid block
    down onto the cage of the hip-roll servo behind the hip (verify_fea: the load path from the disc to the cage)."""
    zd = ZY - YAW_DISC_T                                     # the roll bracket's top corners swing up to z 20.7
    xc = (19.0 ** 2 - 11.0 ** 2) ** 0.5
    middle = [(-xc, -11.0), (xc, -11.0), ("arc", (19.0, 0.0)), (xc, 11.0), (-xc, 11.0), ("arc", (-19.0, 0.0))]
    p = [("cyl", "z", (0.0, 0.0), 19.0, (ZY - 7.0, ZY)),                                   # disc on the yaw horn: 7 mm,
         ("prism", "z", middle, (zd, ZY - 6.9)),                                            # 9 across the middle (the
         # thigh's arms swing under its sides when the hip rolls)
         ("box", (-14.5, 14.0), (-5.0, 5.0), (19.6, zd + 0.1)),                            # keel (clear of the roll
         ("box", (-50.0, -14.6), (-35.0, 12.0), (HW + C + 3.0 - 0.1, ZY))]                 # bracket); solid block
    p += cage(roll_servo(), wall=3.0, omit=-1)                 # (the roll U slides on from below)
    p += horn_holes("z", (0.0, 0.0), (19.5, ZY + 0.1))
    for k in range(4):                                                                      # counterbores from below:
        import math                                                                         # M2 x 10 horn screws
        a = math.radians(90 * k)
        p.append(("hole", "z", (7.0 * math.cos(a), 7.0 * math.sin(a)), 4.6, (19.5, ZY - 6.0)))
    return p


def hip_roll_bracket():
    """U-bracket on both faces of the hip-roll servo (front arm on the horn, rear arm on the hub, joined by a stiff
    bridge outboard of the thigh) carrying the hip-pitch servo's cage; the front arm is the cage's back wall."""
    R, P = roll_servo(), pitch_servo()
    front = rect(-18.45, 16.05, -HW - C - WALL - 0.05, HW + C + WALL + 0.05)                 # (y, z)
    rear = rect(-15.0, 35.5, -11.0, 15.0, 6.0)                                               # (short below: the knee)
    p = u_arms(R, front, rear, tu_horn=3.5)                                                  # (the pitch case is behind it)
    p += cage(P, omit=-1)                                       # (the thigh slides on from below)
    xb = XR - 37.25 - BOSS_H - TU
    yb = HF + TU + 2.1                                                                      # thigh arm + its screw heads
    p += [("box", (XR, XR + 3.5), (16.0, yb + 0.5), (9.0, 14.0)),                         # front arm out to the bridge
          ("box", (XR, XR + 3.5), (yb, yb + 10.0), (-2.0, 14.0)),                         # (through the thigh's band
          ("box", (xb, XR + 3.5), (yb + 0.4, yb + 10.0), (-2.0, 14.0))]                   # only above its boss); bridge
    for k in range(4):                                                                      # counterbores: roll horn screw
        import math                                                                         # heads inside the pitch cage
        a = math.radians(90 * k)
        p.append(("hole", "x", (7.0 * math.cos(a), 7.0 * math.sin(a)), 4.6, (XR + 1.5, XR + 3.6)))
    return p


def thigh():
    """The reference robot's dog-leg thigh: U-bracket arms on both faces of the hip-pitch servo, running down and
    forward around the knee servo's cage (the knee servo lies forward). Solid plates join each arm to the cage over
    their whole overlap, outside the shin's reach around the knee (verify_fea). The cage is open at the front: the knee
    servo slides in from there (horn off), and its two far case screws go in through holes in the inner arm."""
    K = knee_servo()
    z = -THIGH
    arm = rounded_polygon([(-13.0, 13.0), (13.0, 13.0), (21.0, -10.0), (39.0, z + 22.0), (39.0, z - 16.5),
                           (15.5, z - 16.5), (15.5, z + 14.5), (-13.0, z + 14.5)],
                          [12.9, 12.9, 8.0, 8.0, 5.0, 3.0, 0.0, 3.0])
    p = u_arms(pitch_servo(), arm)
    p += cage(K, skip=("l1",), ext=0.4, omit=-1)               # (the shin slides on from below)
    xf = ST["LB"] + C + WALL                                                                  # front of the cage
    zt, zb = z + HW + C + WALL, z - HW - C - WALL
    for ys in ((HC + 0.05, HF + 0.1), (-HF - BOSS_H - 0.1, -HC - RP + 0.1)):
        p += [("box", (15.5, xf - 0.07), ys, (zb + 0.07, zt - 0.07)),                        # in front of the knee
              ("box", (-ST["LA"] - C - WALL + 0.07, 15.53), ys, (z + 13.5, zt - 0.07))]      # and above it
    for dz in (-ST["MOUNT_W"], ST["MOUNT_W"]):                                                # screwdriver access
        p.append(("hole", "y", (ST["MOUNT_L"][1], z + dz), 5.0, (-HF - BOSS_H - TU - 0.1, -HC - RP - 0.05)))
    return p


def shin():
    """U-bracket arms on both faces of the knee servo, widening into solid plates over the top of the ankle-pitch
    servo's cage (case up) below. The cage is open at the bottom: the servo slides up into it, and the foot's roll
    bracket passes under its lower back corner when the toes point down; the far case screws go in through the arm."""
    A = ankle_pitch_servo()
    w = HW + C + WALL
    zc = -SHIN + 23.0                                                                          # arms reach down to here
    arm = rounded_polygon([(-13.0, -2.0), (-w, -13.0), (-w, zc), (w, zc), (w, -13.0), (13.0, -2.0), (13.0, 13.0),
                           (-13.0, 13.0)], [0.0, 2.0, 3.0, 3.0, 2.0, 0.0, 12.9, 12.9])
    p = u_arms(knee_servo(0.0), arm)
    p += cage(A, skip=("w0", "l0"), ext=0.4, omit=-1)           # (no near screw beside the hub hole at the back:
    top = -SHIN + ST["LB"] + C + WALL                           # that corner has no side wall; verify_fea)
    p += [("cut", (-w - 0.1, w + 0.1), (-HC - RP - 0.1, -HC + 0.1),                          # rear plate: nothing below
           (-SHIN - ST["LA"] - C - WALL - 0.1, -SHIN - ST["LA"] - C)),                     # the case (foot bracket)
          ("box", (-w, -HW - C), (-HC - RP, HC + 0.4), (-SHIN + 20.0, top)),               # upper part of the back wall
          ("box", (-w + 0.07, w - 0.07), (HC + 0.05, HF + 0.1), (zc + 0.07, top - 0.07)),  # solid plates: arms onto
          ("box", (-w + 0.07, w - 0.07), (-HF - BOSS_H - 0.1, -HC - RP + 0.1), (zc + 0.07, top - 0.07))]   # the cage
    for dx in (-ST["MOUNT_W"], ST["MOUNT_W"]):                                                # screwdriver access
        p.append(("hole", "y", (dx, -SHIN + ST["MOUNT_L"][1]), 5.0, (-HF - BOSS_H - TU - 0.1, -HC - RP - 1.65)))
    # the rear plate is 4 mm thick (verify_fea) except where the ankle bracket's boss slides up along it to the hub
    # (|x| < 9.6 below the axis); around the hub a 20 mm hole clears the hub (19.2) and the boss (18)
    yo = -HC - RP
    zb = -SHIN - ST["LA"] - C                                                                 # the plate's bottom
    p += [("box", (-w + 0.07, w - 0.07), (yo - 1.6, yo + 0.05), (-SHIN, top - 0.07)),
          ("box", (-w + 0.07, -9.6), (yo - 1.6, yo + 0.05), (zb + 0.07, -SHIN + 0.1)),
          ("box", (9.6, w - 0.07), (yo - 1.6, yo + 0.05), (zb + 0.07, -SHIN + 0.1)),
          ("hole", "y", (0.0, -SHIN), 20.0, (yo - 1.7, yo + 0.1))]
    for lo in ST["MOUNT_L"]:
        for dx in (-ST["MOUNT_W"], ST["MOUNT_W"]):
            if dx < 0 and lo == ST["MOUNT_L"][0]:
                continue
            p += [("hole", "y", (dx, -SHIN + lo), ST["SCREW"], (yo - 1.7, yo + 0.1)),
                  ("hole", "y", (dx, -SHIN + lo), 4.2, (yo - 1.7, yo - 0.0))]               # heads sunk in
    return p


def ankle_bracket():
    """U-bracket on both faces of the ankle-pitch servo. Its arms are full-height side plates back to the ankle-roll
    servo's cage (behind the ankle): outboard a solid plate over the whole cage side; inboard (the roll servo's case
    is there) over the cage's top and onto a rim that closes the cage's horn face around the horn, so arms and cage
    are one box (verify_fea). The roll servo slides into the cage from the inboard end, horn off. Below the ankle axis
    the plates leave room for the foot's roll bracket, which swings there."""
    R = ankle_roll_servo()
    zt = HW + C + WALL
    x_back = XA - HF - HC - RP
    x_case = XA - HF + HC                                                                       # roll case's horn face
    xf = XA + TU + 0.6                                                                          # clear of the foot's arm
    front = rounded_polygon([(13.0, -18.0), (13.0, 13.0), (xf, zt + 0.05), (xf, -18.0)], [8.0, 12.9, 0.0, 0.0])
    slab = rect(x_case + 0.05, xf + 0.1, -6.5, zt + 0.05)                                     # over the foot bracket
    slab_hub = rect(x_case + 0.05, xf + 0.1, -11.0, zt + 0.05)                                # (inboard: verify_fea)
    # (at the +-20 deg roll limit the foot's roll bracket reaches the horn arm's plane only below z -7.5, the hub
    # arm's plane only below z -12)
    top = rect(x_back, xf + 0.1, zt - WALL - 0.05, zt + 0.05)                                 # on the cage's top wall
    side = rect(x_back, x_case + 0.3, -zt - 0.05, zt + 0.05)                                  # outboard: whole cage side
    p = u_arms(ankle_pitch_servo(0.0), front, extra_horn=[slab, top, side], extra_hub=[slab_hub, top])
    p += cage(R, skip=("l0",), omit=-1)                       # the roll servo slides in from the inboard end;
    #                                                                         the foot slides on from below
    p += [("box", (x_case, XA - 0.4), (-ST["LB"] - C - WALL, HW + C + WALL - 0.1 + 0.6), (-zt, zt)),   # rim over the
          ("hole", "x", (0.0, 0.0), 22.0, (x_case - 0.1, XA - 0.3))]                        # case's horn face: a box
    p.append(("pcut", "x", chamfer_cut((-ST["LB"] - C - WALL, -zt), (1, 1), 9.0), (x_back - 0.1, x_case + 0.1)))
    p.append(("box", (x_back + 0.07, x_case + 0.23), (12.9, HF + 0.1), (-zt + 0.02, zt - 0.02)))   # outboard: arm onto cage
    return p


def foot():
    """Sole plate (45° chamfered corners like the reference robot's) and a U-bracket on both faces of the ankle-roll
    servo. Symmetric: one part for both feet."""
    zs = -SOLE_TO_ANKLE
    x0, x1, hw = FOOT_X[0], FOOT_X[1], FOOT_W / 2
    sole = [(x1, -hw + 14.0), (x1, hw - 14.0), (x1 - 14.0, hw), (x0 + 10.0, hw), (x0, hw - 10.0), (x0, -hw + 10.0),
            (x0 + 10.0, -hw), (x1 - 14.0, -hw)]
    p = [("prism", "z", sole, (zs, zs + SOLE_T))]
    arm = rounded_polygon([(-16.0, zs + SOLE_T - 0.5), (16.0, zs + SOLE_T - 0.5), (13.0, 13.0), (-13.0, 13.0)],
                          [0.0, 0.0, 12.9, 12.9])                                               # (y, z)
    p += u_arms(ankle_roll_servo(), arm)
    for x in (-40.0, 14.0, 36.0):                                                               # lightening holes
        p.append(("hole", "z", (x, 0.0), 12.0, (zs - 0.1, zs + SOLE_T + 0.1)))
    return p


# ------------------------------------------------------------------------------------------------ upper body
def torso():
    """Lower torso shell (pelvis frame): the reference robot's octagonal body. Its floor bolts onto the pelvis; below the
    floor a skirt hides the hip-yaw servos, so the legs come straight out from under the body. Inside: Raspberry Pi on
    the back wall, battery, servo driver, power. A lip around the top takes the chest cap (4 screws through the cap)."""
    w = TWALL
    p = [("prism", "z", octagon(TD, TW, TCH), (TZB, TZS)),
         ("pcut", "z", oct_inset(w), (TZ0 + w, TZS + 0.1)),
         ("pcut", "z", oct_inset(w), (TZB - 0.1, TZ0)),                                          # the skirt (open below)
         ("cut", (-34.0, -26.0), (-14.0, 14.0), (TZ0 - 0.1, TZ0 + w + 0.1)),                    # leg cables up
         ("hole", "x", (0.0, 88.0), 12.0, (-TD - 0.1, -TD + w + 0.1))]                          # push-to-talk button
    for x in (-20.0, 24.0):
        for y in (-25.0, 25.0):
            p.append(("hole", "z", (x, y), 3.2, (TZ0 - 0.1, TZ0 + w + 0.1)))                  # bolts to the pelvis
    p += [("lprism", "z", oct_inset(w - 0.5), (TZS - 6.0, TZS)),                               # lip, fused to the wall
          ("lprism", "z", oct_inset(w + 0.2), (TZS - 0.1, TZS + 5.0)),                         # lip above the seam
          ("lpcut", "z", oct_inset(w + 2.2), (TZS - 6.1, TZS + 5.1))]
    for x in (TD, -TD):
        sgn = 1 if x > 0 else -1
        for y in (-15.0, 15.0):
            p.append(("lhole", "x", (y, TZS + 2.5), 2.5, tuple(sorted((sgn * (TD - w - 2.4), sgn * (TD - w + 0.3))))))
    for y in (-29.0, 29.0):                                                                     # Raspberry Pi standoffs
        for z in (96.0, 145.0):
            p.append(("lcyl", "x", (y, z), 3.2, (-TD + w - 0.5, -TD + w + 6.0)))
            p.append(("lhole", "x", (y, z), 2.5, (-TD + w, -TD + w + 6.1)))
    return p


def chest_cap():
    """Chest cap (pelvis frame): top of the octagonal torso with chamfered top edges, vent slots and a speaker grille,
    the neck STS3215 standing on top, and on each side wall the pad the shoulder servo's horn bolts to (from inside)."""
    w, ch = TWALL, TOP_CH
    p = [("prism", "z", octagon(TD, TW, TCH), (TZS, TZT)),
         ("pcut", "x", chamfer_cut((TW, TZT), (-1, -1), ch), (-TD - 1.0, TD + 1.0)),
         ("pcut", "x", chamfer_cut((-TW, TZT), (1, -1), ch), (-TD - 1.0, TD + 1.0)),
         ("pcut", "y", chamfer_cut((TD, TZT), (-1, -1), ch), (-TW - 1.0, TW + 1.0)),
         ("pcut", "y", chamfer_cut((-TD, TZT), (1, -1), ch), (-TW - 1.0, TW + 1.0)),
         ("pcut", "z", oct_inset(w), (TZS - 0.1, TZT - ch - w)),
         ("pcut", "z", oct_inset(w + ch / 2), (TZT - ch - w - 0.1, TZT - ch / 2 - w)),
         ("pcut", "z", oct_inset(w + ch), (TZT - ch / 2 - w - 0.1, TZT - w))]
    sx, sy, sz = SHOULDER
    for sgn in (1, -1):
        ys = tuple(sorted((sgn * (TW - w - 0.5), sgn * sy)))
        p.append(("lcyl", "y", (sx, sz), 12.5, ys))                                            # shoulder pad
        p += late(horn_holes("y", (sx, sz), (ys[0] - 0.1, ys[1] + 0.1)))
        for xc in (-15.0, -9.0, -3.0, 3.0, 9.0, 15.0):                                         # vent slots
            p.append(("cut", (xc - 1.25, xc + 1.25), tuple(sorted((sgn * 36.0, sgn * 48.0))), (TZT - w - 0.1, TZT + 0.1)))
        for y in (-15.0, 15.0):                                                                # screws into the lip
            p.append(("hole", "x", (y, TZS + 2.5), 3.4, tuple(sorted((sgn * (TD - w - 0.1), sgn * (TD + 0.1))))))
    for x in (18.0, 24.0, 30.0):                                                               # speaker grille
        for y in (-12.0, -6.0, 0.0, 6.0, 12.0):
            p.append(("hole", "z", (x, y), 3.5, (TZT - w - 0.1, TZT + 0.1)))
    p += rear_face_mount("z", (0.0, 0.0), (1, 1), (0, 1), (TZT - w - 0.1, TZT + 0.1))         # neck servo on top
    return p


def head():
    """Head (frame: neck horn face, z up): the reference robot's soft rounded block, narrower at the chin, with four
    holes in a diamond on the face (the microphone listens through them). Hollow (walls >= 2.5 mm under every fillet),
    back window for the wiring."""
    hx, hy, hz = 33.0, 39.0, 62.0
    front = rounded_polygon([(-28.0, 0.0), (28.0, 0.0), (hy, 36.0), (hy, hz), (-hy, hz), (-hy, 36.0)],
                            [10.0, 10.0, 26.0, 20.0, 20.0, 26.0])
    p = [("prism", "x", front, (-hx, hx))]
    for xc, zc, du, dv, r in ((hx, hz, -1, -1, 22.0), (-hx, hz, 1, -1, 22.0), (hx, 0.0, -1, 1, 12.0), (-hx, 0.0, 1, 1, 12.0)):
        p.append(("pcut", "y", corner_cut((xc, zc), (du, dv), r), (-hy - 1.0, hy + 1.0)))   # rounded top / chin edges
    for xc, yc, du, dv in ((hx, hy, -1, -1), (hx, -hy, -1, 1), (-hx, hy, 1, -1), (-hx, -hy, 1, 1)):
        p.append(("pcut", "z", corner_cut((xc, yc), (du, dv), 20.0), (-0.1, hz + 0.1)))     # rounded vertical edges
    p += [("cut", (-26.0, 26.0), (-24.0, 24.0), (4.0, 16.1)),                                # hollow, in steps
          ("cut", (-26.0, 26.0), (-30.0, 30.0), (16.0, 52.0)),
          ("cut", (-18.0, 18.0), (-24.0, 24.0), (51.9, 58.0)),
          ("cut", (-hx - 0.1, -25.9), (-16.0, 16.0), (16.0, 44.0)),                          # back window
          ("hole", "z", (-18.0, 0.0), 8.0, (-0.1, 4.1))]                                    # mic cable down
    for yc, zc in ((0.0, 49.0), (7.0, 42.0), (-7.0, 42.0), (0.0, 35.0)):                    # the four face holes
        p.append(("hole", "x", (yc, zc), 5.0, (25.9, hx + 0.1)))
    p += horn_holes("z", (0.0, 0.0), (-0.1, 4.1))
    return p


def shoulder_servo():                      # arm frame (shoulder axis on the horn face, y outward): case down
    return Servo((0.0, HF, 0.0), "y", -1, ("z", -1))


def elbow_servo():                         # arm frame: under the shoulder servo, lying forward, horn outward
    return Servo((0.0, ELBOW_Y - HF, -UA_L), "y", +1, ("x", +1))


def upper_arm():
    """Arm link 1 (frame: shoulder-pitch axis on the shoulder horn face, y outward), the reference robot's shoulder: the
    shoulder STS3215 hangs outside the chest (its horn bolted to the chest pad) in a hood, and the elbow STS3215 lies in
    a box under it, horn outward."""
    S = shoulder_servo()
    top = ST["LA"] + C + WALL
    p = cage(S) + cage(elbow_servo())
    hw = HW + C + WALL + 0.05
    hood = rounded_polygon([(-hw, top - WALL + 0.05), (hw, top - WALL + 0.05), (hw, top + 4.0), (-hw, top + 4.0)],
                           [0.0, 0.0, 6.0, 6.0])                                                # (x, z) rounded hood
    p.append(("prism", "y", hood, (HF - HC, HF + HC + RP)))
    return p


def arm_blade():
    """Arm link 2 (frame: elbow axis on the elbow horn face, y outward): the reference robot's thick paddle blade with a
    raised boss on the horn."""
    prof = rounded_polygon([(-17.0, 16.0), (17.0, 16.0), (19.0, -30.0), (13.0, -BLADE_L), (-11.0, -BLADE_L), (-17.0, -30.0)],
                           [16.0, 16.0, 40.0, 12.0, 12.0, 40.0])
    return [("prism", "y", prof, (0.0, BLADE_T)), ("cyl", "y", (0.0, 0.0), 12.5, (BLADE_T, BLADE_T + 2.0))] + \
        horn_holes("y", (0.0, 0.0), (-0.1, BLADE_T + 2.1))


# ------------------------------------------------------------------------------------------------ catalogue
# name -> (primitives, colour, quantity). Right-side parts are generated by mirroring the left ones.
PARTS = {
    "JX0_Pelvis": (pelvis(), "sage", 1),
    "JX0_HipYawBracket_L": (hip_yaw_bracket(), "sage", 1),
    "JX0_HipYawBracket_R": (mirror_y(hip_yaw_bracket()), "sage", 1),
    "JX0_HipRollBracket_L": (hip_roll_bracket(), "sage", 1),
    "JX0_HipRollBracket_R": (mirror_y(hip_roll_bracket()), "sage", 1),
    "JX0_Thigh_L": (thigh(), "sage", 1),
    "JX0_Thigh_R": (mirror_y(thigh()), "sage", 1),
    "JX0_Shin_L": (shin(), "sage", 1),
    "JX0_Shin_R": (mirror_y(shin()), "sage", 1),
    "JX0_AnkleBracket_L": (ankle_bracket(), "sage", 1),
    "JX0_AnkleBracket_R": (mirror_y(ankle_bracket()), "sage", 1),
    "JX0_Foot": (foot(), "sage", 2),
    "JX0_Torso": (torso(), "sage", 1),
    "JX0_ChestCap": (chest_cap(), "sage", 1),
    "JX0_Head": (head(), "sage", 1),
    "JX0_UpperArm_L": (upper_arm(), "sage", 1),
    "JX0_UpperArm_R": (mirror_y(upper_arm()), "sage", 1),
    "JX0_ArmBlade_L": (arm_blade(), "sage", 1),
    "JX0_ArmBlade_R": (mirror_y(arm_blade()), "sage", 1),
}


# ------------------------------------------------------------------------------------------------ servo stand-in
def servo_st():
    """STS3215 stand-in (frame: shaft axis = z, output horn face at z = +HORN_FACE, case length toward +x)."""
    hf, case = ST["HORN_FACE"], ST["CASE"]
    return [("box", (-ST["LA"], ST["LB"]), (-ST["W"] / 2, ST["W"] / 2), (-case / 2, case / 2)),
            ("cyl", "z", (0.0, 0.0), ST["HORN_D"] / 2, (case / 2 - 0.5, hf)),
            ("cyl", "z", (0.0, 0.0), ST["HORN_D"] / 2, (-hf, -case / 2 + 0.5))] + horn_holes("z", (0.0, 0.0), (hf - 1.0, hf + 0.1), centre=0)


SERVOS = {"JX0_Servo_STS3215": (servo_st(), "black", 17)}


def bbox(prims):
    """Expected bounding box of the bosses (mm) for the CAD check."""
    lo, hi = [1e9] * 3, [-1e9] * 3
    for p in prims:
        k0 = base_kind(p[0])
        if k0 == "box":
            for k in range(3):
                lo[k], hi[k] = min(lo[k], p[k + 1][0]), max(hi[k], p[k + 1][1])
        elif k0 == "prism":
            _, axis, pts, s = p
            ia = "xyz".index(axis)
            others = [i for i in range(3) if i != ia]
            lo[ia], hi[ia] = min(lo[ia], s[0]), max(hi[ia], s[1])
            for j, i in enumerate(others):
                vals = [q[j] for q in path_points(pts, 64)]
                lo[i], hi[i] = min(lo[i], min(vals)), max(hi[i], max(vals))
        elif k0 == "cyl":
            _, axis, c, r, s = p
            ia = "xyz".index(axis)
            others = [i for i in range(3) if i != ia]
            lo[ia], hi[ia] = min(lo[ia], s[0]), max(hi[ia], s[1])
            for i, cv in zip(others, c):
                lo[i], hi[i] = min(lo[i], cv - r), max(hi[i], cv + r)
    return lo, hi
