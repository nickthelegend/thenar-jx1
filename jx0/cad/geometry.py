"""JX0 printable-part geometry (millimetres, each part in its robot link frame: x forward, y left, z up).

Single source of truth for the SolidWorks builder (build_cad.py), the STL export and the simulation model. Every part is
a list of primitives:
    ("box",  (x0, x1), (y0, y1), (z0, z1))                 boss (axis-aligned block)
    ("cut",  (x0, x1), (y0, y1), (z0, z1))                 pocket
    ("cyl",  axis, (c0, c1), r, (s0, s1))                  boss cylinder along axis; c = the other two coords in xyz order
    ("hole", axis, (c0, c1), d, (s0, s1))                  cylindrical cut
    ("prism"/"pcut", axis, profile, (s0, s1))              extruded profile (true arcs allowed, see path_points)
and every screw is listed with its part (SCREWS): where its head sits, which way it points, its size and length, and
what it screws into (verify_fit checks each one against the real servo).

Servo interface: the Feetech STS3215 12 V (ST-3215-C018) as it really is, measured on the Feetech factory model that
Waveshare distributes (ST3215 STEP), the SO-ARM100 servo model and the Feetech datasheet drawing, taking the larger of
the models wherever they differ (servo frame: shaft = z, output horn toward +z, case toward +x, shaft at the origin):
- case 45.4 x 24.8 (x -10.2..35.2, y +-12.4); full footprint z -14.4..15.9; the rear face the cage plate presses on is
  a pad at z -15.6 (x 5.3..35.2), with a raised label block on it (x 16.7..29.9, y +-9.2, to z -17.85) and, between the
  passive horn and the label, the opening of the two 5264 cable sockets (x 11.4..16.7): the plugs sit inside the case
  and the wires come straight out of the rear face, so they are bent flat along it to the case's far end;
- output side: a raised strip x 8.6..35, y +-7 up to z 17.45 and the Ø20 POM drive horn, its face at z 18.1 (datasheet)
  to 18.75 (SO-ARM100); the horn screw (M3 x 6) head stands 1.5 proud of it;
- rear side: the Ø20 passive horn on the Ø6 rear boss, its face at z -17.75 (the boss tip 0.6 beyond it);
- horn holes: 4 x Ø2.5 on a 14 mm circle on both horns, for M3 screws (SO-101 uses M3 x 6); case holes on the rear face
  at x 8.3 / 32.75, y +-10.25: Ø1.6, 2.9 mm deep, for M2 self-tapping screws.
Every joint (12 leg, 4 arm, 1 neck) is the same 12 V STS3215.

Each horn interface is built for the deepest real horn (face at HF = 18.8); 0.4 mm printed shims (JX0_HornShim) under
the horn arm make up the difference on a servo whose horn sits lower (verify_fit; build guide: measure across the two
horns, 36.55 mm with no shim).

v0.4 — legs like the reference robot (media/reference.mp4): every leg pitch and roll joint is DOUBLE-SIDED. The servo's
case sits in a cage on one link (four walls + a rear plate screwed to the case); the next link is a U-bracket that grabs
the servo on both sides, the output horn and the passive horn, so the joint's load passes through both faces instead of
bending the output shaft. The hip-yaw disc is held by the pelvis from both sides: a thrust ring above it and a printed
keeper whose lip runs in a groove under the disc's rim, so the leg's bending reaches the pelvis without going through
the yaw servo's shaft. Short legs (62 mm
thigh, 58 mm shin, ankle 33 mm above the floor, as measured on the reference) under a tall torso whose skirt hides the
hip-yaw servos; the knee servo lies forward, which gives the thigh the reference's dog-leg plate. Arms: the shoulder
servo hangs outside the chest in a hood (its horn bolted to a pad on the chest wall), the elbow servo in a box under it,
and a thick paddle blade, as on the reference robot.
All three hip axes meet at the hip centre and both ankle axes at the ankle centre (the gait model assumes it).
"""
from __future__ import annotations

# ------------------------------------------------------------------------------------------------ the real STS3215
ST = dict(LA=10.2, LB=35.2, W=24.8,                 # case footprint: x -LA..LB, y +-W/2
          REAR=15.6,                                # rear-face pad (x 5.3..LB) the cage plate presses on: z = -REAR
          BAND=(-14.4, 15.9),                       # full-footprint band of the case
          STRIP=(8.6, 35.0, 7.0, 17.45),            # raised strip on the output face: x range, |y| <=, top z
          HORN_D=20.0, HORN_REAL=(18.1, 18.75),     # drive horn: Ø, face z (Feetech datasheet .. SO-ARM100 model)
          HORN_T=2.5, HORN_FREE=1.5,                # drive horn disc thickness; free space behind its screw holes
          IDLER=17.75, IDLER_D=20.0,                # passive horn: face z = -IDLER, Ø; on the Ø6 rear boss
          IDLER_T=2.15, IDLER_FREE=1.2,             # its thickness; free space behind its screw holes
          BOSS_TIP=18.35,                           # Ø6 rear boss tip, inside the passive horn's Ø7 bore
          LABEL=(16.7, 29.9, 9.2, 17.85),           # raised label block on the rear face: x range, |y| <=, z
          SOCKET=(11.4, 16.7, 10.0),                # the cable sockets' opening in the rear face: x range, |y| <=
          PCD=14.0, HORN_HOLE=2.5,                  # 4 horn holes (both horns) on a 14 mm circle, Ø2.5 (M3)
          MOUNT_L=(8.30, 32.75), MOUNT_W=10.25,     # rear-face case holes: x, |y|
          MOUNT_D=1.6, MOUNT_DEPTH=2.9)             # Ø1.6 x 2.9 deep (M2 self-tapping)
HF = 18.8          # horn arm face: the deepest real horn's face (18.75) + 0.05; shallower horns: shims
HI = ST["IDLER"]   # passive horn face (the U-bracket's boss sits on it)
HR = ST["REAR"]    # rear-face pad (the cage plate's inner face)
HO = ST["BAND"][1]  # output-side band top
HW = ST["W"] / 2
ST["HORN_FACE"] = HF
SHIM = 0.4         # printed horn shim (JX0_HornShim): 0, 1 or 2 under each horn arm
# fasteners: (head Ø, head height) as the largest of cheese / pan / socket heads; clearance hole; counterbore
M2 = dict(head=(4.0, 1.6), hole=2.2, cbore=4.6)
M3 = dict(head=(5.6, 3.0), hole=3.4, cbore=6.4)
HUB_UNDER = 5.7    # M3 x 8 into the passive horn: 5.7 mm of boss and arm under the head (2.3 mm of thread)
CASE_UNDER = 3.0   # M2 x 6 CSK case screws: 3.0 mm of plate under the point where the head bears on the hole's edge,
CSK = dict(head=(3.8, 0.8))   # 2.2 mm into the case's 2.9 mm hole. A 90° CSK head (Ø3.8) in a Ø2.2 hole bears on its
                              # edge 0.8 mm below the head's top: an M2 x 6 CSK reaches 5.2 mm past that

T = 3.0            # plate thickness (PETG)
C = 0.5            # clearance around the case
WALL = 2.5         # servo cage wall
RP = 4.6           # cage rear plate (z -15.6..-20.2): the U-bracket's hub arm passes 0.75 mm over it; 1.9 mm thick along
RP_THIN = HI - 0.25 - HR   # the path its boss slides in on when the bracket is fitted (the boss passes 0.25 over it)
TU = 4.5           # U-bracket arm plate (verify_fea)
BOSS_H, BOSS_R = 3.2, 9.5     # U-bracket boss on the passive horn: the arm passes over the cage's plate, its case-screw
HUB = HI + BOSS_H              # heads and the cables; HUB = the hub arm's inner face (20.95)
WIN_W = ST["LABEL"][2] + 0.5   # rear-plate window over the label block and the cables (|w| <=)
OUT_C = 0.6        # plates over a case's output side stand this far off its band (a servo may sit 0.3 mm out of its
                   # cage: SO-ARM100's rear cover lip)
ZY = 30.0          # hip-yaw horn face above the hip centre
YAW_DISC_T = 9.0   # hip-yaw bracket disc on the yaw horn (rides under the thrust ring); 9 mm: verify_fea
YAW_SEAT = 0.3     # the yaw servo hangs 0.3 mm higher than nominal: the disc under its horn sits at ZY on the deepest
                   # real servo (rear cover lip 0.3 deeper, SO-ARM100 model); on any other the horn shims make it up
# hip-yaw keeper: the pelvis holds the yaw disc from above (thrust ring, 0.1 mm over the disc) and below (a printed
# keeper's lip under the disc's 3 mm flange, 0.05 mm below it; the keeper is clamped flat against a boss on the pelvis
# by 4 screws). The play left is taken up with PTFE tape on the flange. Arc (left leg, pelvis frame, degrees from +x
# toward +y): where the lip is needed (verify_strength), clear of the hip-yaw bracket and the hip-roll bracket over the
# whole hip-yaw range (+-12 deg; the gaits use +-5)
YAW_LIMIT = 12.0
KEEP_ARC = (-45.0, 125.0)              # v0.5: to 125 (from 104): the swinging longer leg tilts the disc past 104 deg
KEEP_R = (15.6, 19.6, 26.0)            # lip inner radius, wall inner radius, outer radius (v0.5: 26, from 24.6)
KEEP_Z = (24.6, 26.55, 30.2)           # wall bottom, lip top (0.45 under the flange: the disc's height varies with the
KEEP_LIP = (21.6, 23.9)                # servo, PTFE tape takes up the play), top (clamped to the boss); the keeper is
                                       # solid from z 21.6 up out to r 23.9: a C round the disc's rim
KEEP_SCREWS, KEEP_SCREW_R = (-35.0, 5.0, 45.0, 85.0, 115.0), 22.0
KEEP_BOSS_TO = 150.0                   # the pelvis boss wraps round the cage's outboard end to its back wall
FLANGE_Z, GROOVE = 27.0, (15.3, 20.9)  # disc flange bottom; under it (the lip's room): inner radius, bottom
BOSS_TOP = 36.6                        # pelvis boss the keeper screws into (the torso skirt starts above it)
THIGH, SHIN = 93.0, 87.0   # v0.5: 1.5 x v0.4's (62, 58), for a ~55 cm robot (jx0/analysis/sizing.py)
SHIN_BACK = 10.0   # the shin cage's back wall comes down to this height above the ankle axis (verify_fea)
HIP_Y = 45.0       # half hip spacing
XR = -15.9         # hip-roll horn face (servo behind the hip centre, horn facing +x); its U-bracket's front arm is the
TU_ROLL = 5.2      # back wall of the hip-pitch cage, 5.2 mm so the roll horn screws' heads sink into it
XA = -22.0         # ankle-roll horn face (servo behind the ankle centre, horn facing +x)
ELBOW_STOP = (13.0, -17.0, 3.5)            # elbow stop post: (x, z) on the upper arm, radius
ANKLE_STOP_X, ANKLE_STOP_H = -14.0, 0.9   # ankle pitch stop block: front end (x) and height over the top plate
FOOT_RECESS = 1.0                          # mm off the foot's horn arm face where the shin passes (ankle roll stop)
ANKLE_TOP = 6.0    # the ankle bracket's arms rise this far above the roll cage's top wall (verify_fea)
SOLE_TO_ANKLE, SOLE_T, FOOT_X, FOOT_W = 33.0, 5.0, (-68.0, 56.0), 70.0
# torso: octagonal prism, half depth TD (x) and half width TW (y), vertical edges chamfered TCH, split at TZS into the
# lower shell and the chest cap; walls TWALL. TZB: bottom of the skirt that hides the hip-yaw servos; TZ0: the floor
TD, TW, TCH, TWALL = 42.0, 60.0, 16.0, 2.5
TZB, TZ0, TZS, TZT, TOP_CH = 37.0, 68.925, 194.0, 236.0, 8.0   # v0.5: 26 mm taller
# shoulder pitch: the servo hangs outside the chest; its horn bolts to a pad on the chest side wall (horn face y = 63)
SHOULDER = (12.5, TW + 3.0, 212.0)
UA_L = 52.0                                                         # shoulder pitch axis to elbow axis
ELBOW_Y = 41.0                                                      # elbow horn face, outboard of the shoulder horn face
                                                                    # (the blade clears the shoulder's case screws)
BLADE_L, BLADE_T = 120.0, 6.0
# printed mass / solid mass. Body parts: 3 walls + 25 % gyroid. Pelvis and leg brackets (PETG): 6 walls, 6 top and
# bottom layers, 40 % gyroid, so their 2.4-4.5 mm plates print solid, as the finite-element check assumes (verify_fea)
FILL_BODY, FILL_LEG = 0.55, 0.80
LEG_PARTS = ("JX0_Pelvis", "JX0_YawKeeper", "JX0_YawRing", "JX0_HipYawBracket", "JX0_HipRollBracket", "JX0_Thigh", "JX0_Shin",
             "JX0_AnkleBracket", "JX0_Foot")


def fill(name):
    return FILL_LEG if name.startswith(LEG_PARTS) else FILL_BODY


NECK_Z = TZT + HR + HF                                              # neck horn face (head origin): 270.4

# ------------------------------------------------------------------------------------------------ screws
_SINK = None                                   # the screws of the part being built (see _build)


def screw(axis, c, seat, sense, size, length, into, note="", head=None, nominal=None):
    """Register a screw of the part being built: on axis through c (its two other coords, xyz order), the head's bearing
    face at seat (axis coordinate), pointing sense (+-1 along axis, head to tip). into: 'drive' / 'idler' (the servo's
    horns), 'case' (its rear-face case holes), 'printed' (a pilot hole in another printed part), 'insert' (heat-set)."""
    if _SINK is not None:
        _SINK.append(dict(axis=axis, c=tuple(round(float(v), 4) for v in c), seat=round(float(seat), 4),
                          sense=int(sense), size=size, length=float(length), into=into, note=note, head=head,
                          nominal=float(nominal or length)))


def mirror_screw(s):
    s = dict(s)
    if s["axis"] == "y":
        s["seat"], s["sense"] = -s["seat"], -s["sense"]
    else:
        s["c"] = (-s["c"][0], s["c"][1]) if s["axis"] == "x" else (s["c"][0], -s["c"][1])
    return s


def pcd_points(c, pcd=ST["PCD"]):
    import math
    return [(round(c[0] + pcd / 2 * math.cos(math.radians(90 * k)), 6), round(c[1] + pcd / 2 * math.sin(math.radians(90 * k)), 6))
            for k in range(4)]


def horn_holes(axis, c, s, pcd=ST["PCD"], d=M3["hole"], centre=7.0):
    """4 horn screw holes (M3 clearance) on the horn's circle + a centre hole (the horn screw's head / the rear boss),
    through the plate range s along axis."""
    out = [("hole", axis, c, centre, s)] if centre else []
    return out + [("hole", axis, q, d, s) for q in pcd_points(c, pcd)]


def horn_seats(axis, c, seat, top):
    """Counterbores for the 4 M3 heads, from the head seat out past the plate's outer face top."""
    if abs(top - seat) < 0.05:
        return []
    r = _rng(seat, top + (0.1 if top > seat else -0.1))
    return [("hole", axis, q, M3["cbore"], r) for q in pcd_points(c)]


def horn_screws(axis, c, seat, sense, length, into, note=""):
    for q in pcd_points(c):
        screw(axis, q, seat, sense, "M3", length, into, note)


def drive_seat(face, sense_out, length=6.0, thread=3.0):
    """Head seat of an M3 horn screw on the drive horn: thread mm of it in the horn with no shim (0.8 less with two), so
    length - thread of plate under the head; face = the horn arm's horn-side face, sense_out = from the horn outward."""
    return face + sense_out * (length - thread)


def rear_face_mount(axis, shaft_c, l_dir, w_dir, top, sense):
    """STS3215 standing on a plate by its rear face (the neck on the chest cap): rear boss hole, the window over the label
    block and the cable sockets (the cables go straight down through it) and the 4 case screws from below.
    shaft_c = shaft position in the plate's 2 other coords; l_dir / w_dir = (index 0/1, +-1) of the case length (from
    the shaft toward the long end) and width in those coords; top = the plate's top face (the servo's rear face on it),
    sense = +1 if the servo stands toward +axis. Plates thinner than CASE_UNDER get a pad under each screw head."""
    li, ls = l_dir
    wi, _ = w_dir
    s = _rng(top + sense * 0.1, top - sense * 6.0)
    out = [("lhole", axis, shaft_c, ST["IDLER_D"] + 1.0, s)]                # the rear boss (and a passive horn, if fitted)
    a, b = shaft_c[li] + ls * (ST["SOCKET"][0] - 0.5), shaft_c[li] + ls * (ST["LABEL"][1] + 0.5)
    rng = {li: _rng(a, b), 1 - li: (shaft_c[1 - li] - WIN_W, shaft_c[1 - li] + WIN_W)}
    o = _others(axis)
    out.append(("lcut",) + _cutbox({axis: s, o[0]: rng[0], o[1]: rng[1]})[1:])
    seat = top - sense * CASE_UNDER
    for lo in ST["MOUNT_L"]:
        for wo in (-ST["MOUNT_W"], ST["MOUNT_W"]):
            c = list(shaft_c)
            c[li] += ls * lo
            c[wi] += wo
            out += [("lcyl", axis, tuple(c), 2.5, _rng(top - sense * 1.0, seat)),
                    ("lhole", axis, tuple(c), M2["hole"], _rng(top + sense * 0.1, seat - sense * 0.1))]
            screw(axis, c, seat, sense, "M2", 6.0 - CSK["head"][1], "case", "M2 x 6 CSK", "csk", 6.0)
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


def _cutbox(r):
    return ("cut", _rng(*r["x"]), _rng(*r["y"]), _rng(*r["z"]))


def _others(axis):
    return [k for k in "xyz" if k != axis]


class Servo:
    """An STS3215 placed in a part frame: c = centre (the shaft, at the servo frame's origin), a = shaft axis, hs = +-1
    the side of the output horn along a, l = (axis, +-1) from the shaft toward the case's long end; w = the third axis."""

    def __init__(self, c, a, hs, l):
        self.c = dict(zip("xyz", map(float, c)))
        self.a, self.hs = a, hs
        self.l, self.ls = l
        self.w = next(k for k in "xyz" if k not in (a, self.l))

    def l_range(self, grow=0.0):
        lo, hi = (-ST["LA"], ST["LB"]) if self.ls > 0 else (-ST["LB"], ST["LA"])
        return self.c[self.l] + lo - grow, self.c[self.l] + hi + grow

    def at(self, l=0.0, w=0.0, a=0.0):
        """Part-frame point of the servo-frame point (x = l along the case, y = w across it, z = a along the shaft)."""
        p = dict(self.c)
        p[self.l] += self.ls * l
        p[self.w] += w
        p[self.a] += self.hs * a
        return p

    def shaft2(self):
        return tuple(self.c[k] for k in _others(self.a))


def cage(S, rp=RP, wall=WALL, skip=(), thin=None, ext=0.0, omit=None, slide=None, under=CASE_UNDER, lengthwise=False):
    """The case holder of servo S: a rear plate the case is screwed to (it presses on the rear-face pad) and four walls
    around the case, open on the horn side (the servo slides in from there). In the plate: a Ø21 hole the passive horn
    (and the U-bracket's boss) turns in, and a window over the label block and the cable sockets that runs out through
    the plate's far end: the cables are bent flat along the rear face and leave past the case's far end.
    thin = {wall: thickness} overrides; skip = walls left out ('l0' / 'l1' the case ends, 'w0' / 'w1' its sides);
    ext = walls reach this far past the case's horn-side band. slide = ('w' or 'l', +-1): the side the U-bracket's boss
    comes in from when the bracket is fitted (default: the omit side of the width axis); along its path the plate is
    RP_THIN thick and the walls stop at it. omit = -1 / +1 leaves out the near case screw on that side of the width axis
    (in the boss's way), "both" both near ones. under = plate under each case screw's head (M2 x 6 CSK: 5.2 - under into the
    case). lengthwise: the servo slides in along its length from the cage's open far end, so the window stays as wide
    as the label block out to that end (the far screws' heads then bear on 2.5 of their 4 mm)."""
    thin = thin or {}
    t = {k: thin.get(k, wall) for k in ("l0", "l1", "w0", "w1")}
    a0, hs = S.c[S.a], S.hs
    rear_in, rear_out = a0 - hs * HR, a0 - hs * (HR + rp)
    A = _rng(rear_out, a0 + hs * (HO + ext))
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
    out.append(("hole", S.a, sc, ST["IDLER_D"] + 1.0, span))
    # window: label block + cable sockets, out through the far end (narrower past the label, clear of the screw heads)
    ls, wc = S.ls, S.c[S.w]
    far_t = t["l1"] if ls > 0 else t["l0"]
    s0 = S.c[S.l] + ls * (ST["SOCKET"][0] - 0.5)
    s1 = S.c[S.l] + ls * (ST["LABEL"][1] + 0.5)
    s2 = S.c[S.l] + ls * (ST["LB"] + C + far_t + 0.5)
    wa = _rng(a0 - hs * (HR - 0.05), rear_out - hs * 0.1)
    out += [_cutbox({S.a: wa, S.l: (s0, s1), S.w: (wc - WIN_W, wc + WIN_W)}),
            _cutbox({S.a: wa, S.l: (s1, s2), S.w: (wc - (WIN_W if lengthwise else 8.2), wc + (WIN_W if lengthwise else 8.2))}),
            _cutbox({S.a: wa, S.l: (S.c[S.l], s0 + 0.1 * ls), S.w: (wc - 3.5, wc + 3.5)})]   # the rear boss's way in
    if slide is None and omit is not None:
        slide = ("w", omit)
    if slide is not None:
        ax, sg = slide
        key, other = (S.w, S.l) if ax == "w" else (S.l, S.w)
        if ax == "w":
            reach = HW + C + max(t["w0"], t["w1"])
        else:
            reach = (ST["LB"] if sg == S.ls else ST["LA"]) + C + max(t["l0"], t["l1"])
        out.append(_cutbox({S.a: _rng(a0 - hs * (HR + RP_THIN), rear_out - hs * 0.2),
                            key: _rng(S.c[key], S.c[key] + sg * (reach + 0.5)),
                            other: (S.c[other] - BOSS_R - 0.5, S.c[other] + BOSS_R + 0.5)}))
    seat = a0 - hs * (HR + under)
    for lo in ST["MOUNT_L"]:
        for ws in (-1, 1):
            if omit in (ws, "both") and lo == ST["MOUNT_L"][0]:
                continue
            c = list(sc)
            c[o.index(S.l)] += S.ls * lo
            c[o.index(S.w)] += ws * ST["MOUNT_W"]
            out.append(("hole", S.a, tuple(c), M2["hole"], span))
            if rp > under + 0.05:
                out.append(("hole", S.a, tuple(c), M2["cbore"], _rng(seat, rear_out - hs * 0.1)))
            screw(S.a, c, seat, hs, "M2", 6.0 - CSK["head"][1], "case", "M2 x 6 CSK", "csk", 6.0)
    return out


def u_arms(S, prof_horn, prof_hub=None, extra_horn=(), extra_hub=(), tu_horn=TU, horn_len=6.0, horn_thread=3.0,
           horn_note="", slide=("z", +1)):
    """U-bracket around servo S: one arm on the output horn, one on the passive horn (a BOSS_H boss carries that arm over
    the cage's rear plate, its screw heads and the cables), each an extrusion of its (u, v) profile (the two coords
    other than the shaft axis, xyz order), with the horns' 4-screw pattern: M3 x horn_len into the drive horn (heads
    sunk so 3 mm of thread is in the horn) and M3 x 8 through the boss into the passive horn (2.3 mm in it).
    extra_* = more profiles fused to each arm (same thickness). slide = (axis, +-1): the bracket is fitted by sliding
    it along -axis*sign onto the servo (+z: from below), so the servo's rear boss tip (0.6 mm proud of the passive horn)
    comes in along a groove in the boss face from that edge; the drive horn's centre screw goes in after, through the
    arm's centre hole."""
    prof_hub = prof_hub or prof_horn
    a0, sc, hs = S.c[S.a], S.shaft2(), S.hs
    h = _rng(a0 + hs * HF, a0 + hs * (HF + tu_horn))
    b = _rng(a0 - hs * HI, a0 - hs * HUB)
    p = _rng(a0 - hs * HUB, a0 - hs * (HUB + TU))
    out = [("prism", S.a, prof_horn, h), ("cyl", S.a, sc, BOSS_R, b), ("prism", S.a, prof_hub, p)]
    out += [("prism", S.a, e, h) for e in extra_horn] + [("prism", S.a, e, p) for e in extra_hub]
    out += horn_holes(S.a, sc, (h[0] - 0.1, h[1] + 0.1))
    seat = drive_seat(a0 + hs * HF, hs, horn_len, horn_thread)
    out += horn_seats(S.a, sc, seat, a0 + hs * (HF + tu_horn))
    horn_screws(S.a, sc, seat, -hs, horn_len, "drive", horn_note)
    out += horn_holes(S.a, sc, (min(b[0], p[0]) - 0.1, max(b[1], p[1]) + 0.1))
    hub_seat = a0 - hs * (HI + HUB_UNDER)                       # M3 x 8 socket head, 2.3 mm into the passive horn
    out += horn_seats(S.a, sc, hub_seat, a0 - hs * (HUB + TU))
    horn_screws(S.a, sc, hub_seat, hs, 8.0, "idler", "M3 x 8 socket head")
    ax, sg = slide
    g = {S.a: _rng(a0 - hs * (HI - 0.1), a0 - hs * (ST["BOSS_TIP"] + 0.3))}
    for k in _others(S.a):
        g[k] = _rng(S.c[k], S.c[k] + sg * (BOSS_R + 0.5)) if k == ax else (S.c[k] - 3.4, S.c[k] + 3.4)
    out.append(_cutbox(g))
    return out


def rect(u0, u1, v0, v1, r=0.0):
    pts = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
    return rounded_polygon(pts, [r] * 4) if r > 0 else pts


def polar(r, deg, c=(0.0, 0.0)):
    import math
    return (c[0] + r * math.cos(math.radians(deg)), c[1] + r * math.sin(math.radians(deg)))


def sector(r_in, r_out, a0, a1, c=(0.0, 0.0)):
    """Annular sector profile from angle a0 to a1 (degrees, a0 < a1, less than 360 apart) around c, true arcs."""
    am = (a0 + a1) / 2
    return [polar(r_out, a0, c), ("arc", polar(r_out, am, c)), polar(r_out, a1, c),
            polar(r_in, a1, c), ("arc", polar(r_in, am, c)), polar(r_in, a0, c)]


# ------------------------------------------------------------------------------------------------ the servos (left leg)
def yaw_servo(sy=1):                       # pelvis frame: horn down, case toward the robot's middle
    return Servo((0.0, sy * HIP_Y, ZY + HF + YAW_SEAT), "z", -1, ("y", -sy))


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
    thrust ring under it and, around the cage's outboard end and front, a boss the yaw keeper screws into. The hip-yaw
    disc rides 0.1 mm under the ring and the keeper's lip under its rim, so the leg's load and bending go into the
    pelvis through the ring and the keeper, not through the yaw servo's output shaft (PTFE tape on both faces). The yaw
    servos' cables go straight up through the plate's windows and the torso floor."""
    zr = ZY + HF + YAW_SEAT + HR                                              # yaw case's rear face = 64.7
    plate = [(28.0, -50.0), (28.0, 50.0), (21.0, 57.0), (-24.0, 57.0), (-24.0, -57.0), (21.0, -57.0)]
    p = [("prism", "z", plate, (zr, TZ0)),
         ("box", (24.5, 28.0), (-45.0, 45.0), (zr - 14.0, zr + 0.5)),                       # front rib
         ("box", (-24.0, -20.5), (-45.0, 45.0), (zr - 14.0, zr + 0.5))]                     # rear rib
    x0s, x1s, ws, zs = ST["STRIP"]
    for sy in (1, -1):
        # outboard end wall 1.2 mm (inside the skirt); front and back walls 5 mm: they carry the keeper's pull up to
        # the plate (verify_fea). Case screws M2 x 6 CSK with their heads sunk in the 4.2 mm plate
        S = yaw_servo(sy)
        p += cage(S, rp=TZ0 - zr, thin={"l1" if sy > 0 else "l0": 1.2, "w0": 5.0, "w1": 5.0},
                  under=CASE_UNDER)
        c = (0.0, sy * HIP_Y)
        a0, a1 = (KEEP_ARC[0] - 4.0, KEEP_BOSS_TO) if sy > 0 else (-KEEP_BOSS_TO, 4.0 - KEEP_ARC[0])
        y_case = sorted((sy * (HIP_Y - ST["LB"] - C), sy * (HIP_Y + ST["LA"] + C)))          # the case's space
        zb = S.c["z"] - HO                                                                  # the case's output band
        p += [("cyl", "z", c, 19.0, (ZY + 0.1, zb - 0.5)),                                 # thrust ring
              ("prism", "z", sector(11.0, KEEP_R[2], a0, a1, c), (ZY + 0.2, BOSS_TOP)),   # keeper boss
              ("cut", (-HW - C, HW + C), tuple(y_case), (ZY + 0.05, BOSS_TOP + 0.1)),        # (the servo goes in
              # from below; under its case the thrust ring is the separate yaw ring insert)
              ("hole", "z", c, 23.0, (ZY + 0.1, zb + 0.1))]
        for a in KEEP_SCREWS:                                                               # keeper screws (M2 x 10)
            p.append(("hole", "z", polar(KEEP_SCREW_R, sy * a, c), 1.8, (ZY + 0.1, BOSS_TOP - 0.8)))
    for x in (-20.0, 24.0):                                                                 # the torso floor's 4 M3 x 8
        for y in (-25.0, 25.0):                                                             # screws: M3 x 4 heat-set
            p += [("hole", "z", (x, y), 4.0, (zr - 0.1, TZ0 + 0.1)),                       # inserts in the 4.2 mm plate,
                  ("hole", "z", (x, y), 3.4, (zr - 4.0, zr + 0.1))]                        # the tip on into the rib
    return p


def hip_yaw_bracket():
    """A 7 mm disc on the hip-yaw horn (it rides under the thrust ring; a groove under its rim takes the keeper's lip,
    leaving a 3 mm flange), a keel under its centre, and a solid block down onto the cage of the hip-roll servo behind
    the hip (verify_fea: the load path from the disc to the cage)."""
    zd = ZY - YAW_DISC_T                                     # the roll bracket's top corners swing up to z 20.7
    xc = (19.0 ** 2 - 11.0 ** 2) ** 0.5
    middle = [(-xc, -11.0), (xc, -11.0), ("arc", (19.0, 0.0)), (xc, 11.0), (-xc, 11.0), ("arc", (-19.0, 0.0))]
    R = roll_servo()
    x_plate = R.c["x"] - HR - RP + 0.9                       # the block starts over the cage's rear plate
    p = [("cyl", "z", (0.0, 0.0), 19.0, (ZY - 7.0, ZY)),                                   # disc on the yaw horn: 7 mm,
         ("prism", "z", middle, (zd, ZY - 6.9)),                                            # 9 across the middle (the
         # thigh's arms swing under its sides when the hip rolls)
         ("box", (-14.2, 14.0), (-5.0, 5.0), (19.6, zd + 0.1)),                            # keel (clear of the roll
         ("box", (x_plate, XR - 0.5), (-35.0, 12.0), (HW + C + 3.0 - 0.1, ZY)),            # bracket); solid block
         # v0.5 fillets in the two inside corners that took the peak stress (verify_fea): the middle's sides into the
         # disc's underside, and the middle's underside into the block
         ("prism", "x", [(-11.0, zd + 0.05), (12.0, zd + 0.05), (15.0, ZY - 6.9), (-12.5, ZY - 6.9)], (-11.5, 11.5)),
         ("prism", "y", [(XR - 0.55, zd + 0.1), (XR - 0.55, zd - 1.1), (XR + 1.1, zd + 0.1)], (-11.0, 11.0))]
    p += cage(R, wall=3.0, omit=-1)                            # (the roll U slides on from below)
    # room under the disc's rim for the keeper's lip: the keeper's arc + the yaw range + 2 deg
    p.append(("pcut", "z", sector(GROOVE[0], 19.6, KEEP_ARC[0] - YAW_LIMIT - 2.0, KEEP_ARC[1] + YAW_LIMIT + 2.0),
              (GROOVE[1], FLANGE_Z)))
    p += horn_holes("z", (0.0, 0.0), (19.5, ZY + 0.1))
    seat = drive_seat(ZY, -1)                                 # M3 x 6 into the yaw horn from below, heads sunk
    p += horn_seats("z", (0.0, 0.0), seat, 19.5)
    horn_screws("z", (0.0, 0.0), seat, +1, 6.0, "drive")
    return p


def yaw_keeper():
    """The hip-yaw keeper (frame: the yaw axis at the origin, pelvis z): a C-section ring segment round the yaw disc's
    rim; its 4.95 mm lip slides sideways under the disc's flange, and 5 M2 x 10 screws from below clamp its top flat
    against the pelvis's boss. Outer bottom edge stepped: clear of the hip-roll bracket's arm at full roll."""
    a0, a1 = KEEP_ARC
    r_lip, r_wall, r_out = KEEP_R
    zb, zl, zt = KEEP_Z
    p = [("prism", "z", sector(r_wall, r_out, a0, a1), (zb, zt)),
         ("prism", "z", sector(r_lip, KEEP_LIP[1], a0 + 0.07, a1 - 0.07), (KEEP_LIP[0], zl)),
         ("pcut", "z", sector(KEEP_LIP[1], r_out + 0.2, a0 - 1.0, a1 + 1.0), (zb - 0.1, zb + 1.0)),
         ("pcut", "z", sector(r_lip - 0.1, r_lip + 1.4, a0 - 1.0, a1 + 1.0), (KEEP_LIP[0] - 0.1, KEEP_LIP[0] + 1.0)),
         ("pcut", "z", sector(r_lip - 0.1, r_lip + 2.6, 60.0, a1 + 1.0), (KEEP_LIP[0] - 0.1, KEEP_LIP[0] + 1.0)),
         ("pcut", "z", sector(r_lip - 0.1, r_lip + 3.6, a0 - 1.0, -15.0), (KEEP_LIP[0] - 0.1, KEEP_LIP[0] + 1.0)),
         ("pcut", "z", sector(20.3, r_out + 0.2, a0 - 1.0, -15.0), (KEEP_LIP[0] - 0.1, KEEP_LIP[0] + 1.6)),
         ("pcut", "z", sector(20.3, r_out + 0.2, 60.0, a1 + 1.0), (KEEP_LIP[0] - 0.1, KEEP_LIP[0] + 1.6)),
         ("pcut", "z", sector(20.3, r_out + 0.2, 105.0, a1 + 1.0), (KEEP_LIP[0] - 0.1, zb - 1.2)),
         ("pcut", "z", sector(21.3, r_out + 0.2, 112.0, a1 + 1.0), (KEEP_LIP[0] - 0.1, zb - 0.2))]
    # (the lip's inner bottom corner stepped back: clear of the thigh's arm at full hip roll; its outer bottom corner
    # too, and more past 105 deg: the hip-roll bracket's arm at full roll and yaw, 2 deg past the servo limits)
    for a in KEEP_SCREWS:
        cxy = polar(KEEP_SCREW_R, a)
        p += [("hole", "z", cxy, M2["hole"] + 0.2, (KEEP_LIP[0] - 0.1, zt + 0.1)),
              ("hole", "z", cxy, M2["cbore"], (KEEP_LIP[0] - 0.1, zb))]
        screw("z", cxy, zb, +1, "M2", 10.0 - (CSK["head"][0] - M2["hole"] - 0.2) / 2, "printed",
              "M2 x 10 CSK, into the pelvis boss's 1.8 mm pilot", "csk", 10.0)
    return p


def yaw_ring():
    """The left thrust ring's inboard part (frame: the yaw axis at the origin, pelvis z): the hip-yaw servo goes up into
    its cage from below, so under its case the thrust ring is this separate C-shaped insert, pushed up around the yaw
    horn after the servo. The disc's inboard side (where the gaits push hardest) bears up through it onto the case's
    output face; its straight edges sit against the pelvis's ring, so it cannot turn. Built for the deepest servo (its
    case 0.3 mm lower): PTFE tape layers on top take up the rest."""
    S = yaw_servo(1)
    dz = -S.c["y"]                                              # pelvis y -> this frame
    zt = S.c["z"] - HO - YAW_SEAT - 0.05
    x0s, x1s, ws, zs = ST["STRIP"]
    y_out = HIP_Y + ST["LA"] + C - 0.15 + dz
    return [("cyl", "z", (0.0, 0.0), 19.0, (ZY + 0.1, zt)),
            ("hole", "z", (0.0, 0.0), 23.0, (ZY, zt + 0.1)),
            ("cut", (HW + C - 0.15, 20.0), (-20.0, 20.0), (ZY, zt + 0.1)),
            ("cut", (-20.0, -HW - C + 0.15), (-20.0, 20.0), (ZY, zt + 0.1)),
            ("cut", (-20.0, 20.0), (y_out, 20.0), (ZY, zt + 0.1)),
            ("cut", (-ws - 0.5, ws + 0.5), (-20.0, -x0s + 0.5), (S.c["z"] - zs - YAW_SEAT - 0.05, zt + 0.1))]   # strip


def hip_roll_bracket():
    """U-bracket on both faces of the hip-roll servo (front arm on the horn, rear arm on the passive horn, joined by a
    stiff bridge outboard of the thigh) carrying the hip-pitch servo's cage; the front arm is the cage's back wall, so
    the roll horn screws go in from inside the empty pitch cage, heads sunk in the 5.2 mm arm."""
    R, P = roll_servo(), pitch_servo()
    front = rect(-18.45, 16.05, -HW - C - WALL - 0.05, HW + C + WALL + 0.05)                 # (y, z)
    rear = rect(-15.0, 35.5, -11.0, 15.0, 6.0)                                               # (short below: the knee)
    p = u_arms(R, front, rear, tu_horn=TU_ROLL, horn_thread=3.4,
               horn_note="pan or cheese head (2.4 mm at most): sunk in the arm, the pitch case is 0.5 mm behind it")
    p += cage(P, omit=-1)                                       # (the thigh slides on from below)
    xw = ST["LB"] + C                                                                       # the pitch cage's front wall:
    p += [("hole", "x", q, 6.5, (xw - 0.1, xw + WALL + 0.1)) for q in pcd_points((0.0, 0.0))]   # screwdriver to the roll
    xb = XR - HF - HUB - TU                                                                 # horn screws; rear arm's back
    yb = HF + 3.0 + M3["head"][1] + 0.5                                                     # thigh arm + its screw heads
    x1 = XR + TU_ROLL
    p += [("box", (XR, x1), (16.0, yb + 0.5), (9.0, 14.0)),                               # front arm out to the bridge
          ("box", (XR, x1), (yb, yb + 10.0), (-2.0, 14.0)),                               # (through the thigh's band
          ("box", (xb, x1), (yb + 0.4, yb + 10.0), (-2.0, 14.0))]                         # only above its boss); bridge
    return p


def thigh():
    """The reference robot's dog-leg thigh: U-bracket arms on both faces of the hip-pitch servo, running down and
    forward around the knee servo's cage (the knee servo lies forward). Solid plates join each arm to the cage over
    their whole overlap, outside the shin's reach around the knee (verify_fea); on the horn side they stand clear of
    the knee case's output band and its raised strip. The cage is open at the front: the knee servo slides in from
    there (horn off), its cables leave there, and its two far case screws go in through holes in the inner arm."""
    K = knee_servo()
    z = -THIGH
    xk = 16.0                                                   # the arms and plates stay in front of the shin's arms
    arm = rounded_polygon([(-13.0, 13.0), (13.0, 13.0), (21.0, -10.0), (39.0, z + 22.0), (39.0, z - 16.5),
                           (xk, z - 16.5), (xk, z + 14.5), (-13.0, z + 14.5)],
                          [12.9, 12.9, 8.0, 8.0, 5.0, 3.0, 0.0, 3.0])
    p = u_arms(pitch_servo(), arm)
    p += cage(K, skip=("l1",), ext=OUT_C + 0.1, omit=-1, lengthwise=True)   # (the shin slides on from below)
    xf = ST["LB"] + C + WALL                                                                  # front of the cage
    zt, zb = z + HW + C + WALL, z - HW - C - WALL
    for ys in ((HO + OUT_C, HF + 0.1), (-HUB - 0.1, -HR - RP + 0.1)):
        p += [("box", (xk, xf - 0.07), ys, (zb + 0.07, zt - 0.07)),                          # in front of the knee
              ("box", (-ST["LA"] - C - WALL + 0.07, xk + 0.03), ys, (z + 13.5, zt - 0.07))]  # and above it
    x0s, x1s, ws, zs = ST["STRIP"]
    p.append(("cut", (x0s - 0.5, xf + 0.5), (HO + 0.3, zs + 0.3), (z - ws - 0.5, z + ws + 0.5)))   # the knee case's
    #                                                                     strip, out to the front: it slides in from there
    for dz in (-ST["MOUNT_W"], ST["MOUNT_W"]):                                                # screwdriver access
        p.append(("hole", "y", (ST["MOUNT_L"][1], z + dz), 5.0, (-HUB - TU - 0.1, -HR - RP - 0.05)))
    # the cage's lower back corner, rounded off round the knee axis: the top of the shin swings round behind it as the
    # knee bends (r 18.5), and beside the plate (r 16.3) the ankle-pitch servo's cables leave the top of the shin
    for r, ys in ((16.3, (-HR - RP - 0.2, -HR + 0.1)), (18.5, (-HR, HO + 0.5))):
        corner = [(-r, z), ("arc", (-r * 0.7071, z - r * 0.7071)), (0.5, z - r - 0.008), (0.5, z - 20.0),
                  (-20.0, z - 20.0), (-20.0, z)]
        p.append(("pcut", "y", corner, ys))
    return p


def shin():
    """U-bracket arms on both faces of the knee servo, widening into solid plates over the top of the ankle-pitch
    servo's cage (case up) below. The cage is open at the bottom: the servo slides up into it, the ankle bracket's boss
    slides up along the plate onto the passive horn, and the foot's roll bracket passes under the cage's lower back
    corner when the toes point down; the cables leave at the top; the far case screws go in through the arm."""
    A = ankle_pitch_servo()
    w = HW + C + WALL
    zc = -SHIN + 23.0                                                                          # arms reach down to here
    arm = rounded_polygon([(-13.0, -2.0), (-w, -13.0), (-w, zc), (w, zc), (w, -13.0), (13.0, -2.0), (13.0, 13.0),
                           (-13.0, 13.0)], [0.0, 2.0, 3.0, 3.0, 2.0, 0.0, 12.9, 12.9])
    p = u_arms(knee_servo(0.0), arm)
    # the servo slides up into the cage, so its label block needs a slot up the middle of the plate to the window: the
    # plate is two rails, joined by the hub arm above zc; the two far case screws hold the case (the near ones would
    # break into the slot)
    p += cage(A, skip=("w0", "l0"), ext=OUT_C + 0.1, omit="both", slide=("l", -1))
    top = -SHIN + ST["LB"] + C + WALL
    zb = -SHIN - ST["LA"] - C                                                                 # the case's bottom end
    p += [("cut", (-w - 0.1, w + 0.1), (-HR - RP - 0.1, -HR + 0.1), (zb - WALL - 0.1, zb)),  # nothing below the case
          ("cut", (-ST["LABEL"][2] - 0.3, ST["LABEL"][2] + 0.3), (-HR - RP - 0.1, -HR + 0.05),
           (zb - 0.1, -SHIN + ST["SOCKET"][0])),                                            # the label block's slot
          ("box", (-w, -HW - C), (-HR - RP, HO + OUT_C + 0.1), (-SHIN + SHIN_BACK, top)),  # upper part of the back wall
          ("box", (-w + 0.07, w - 0.07), (HO + OUT_C, HF + 0.1), (zc + 0.07, top - 0.07)),  # solid plates: arms onto
          ("box", (-w + 0.07, w - 0.07), (-HUB - 0.1, -HR - RP + 0.1), (zc + 0.07, top - 0.07))]   # the cage
    x0s, x1s, ws, zs = ST["STRIP"]
    p.append(("cut", (-ws - 0.5, ws + 0.5), (HO + 0.3, zs + 0.3), (-SHIN + x0s - 0.5, -SHIN + x1s + 0.5)))   # strip
    for dx in (-ST["MOUNT_W"], ST["MOUNT_W"]):                                                # screwdriver access
        p.append(("hole", "y", (dx, -SHIN + ST["MOUNT_L"][1]), 5.0, (-HUB - TU - 0.1, -HR - RP - 0.05)))
    return p


def ankle_bracket():
    """U-bracket on both faces of the ankle-pitch servo. Its arms are full-height side plates back to the ankle-roll
    servo's cage (behind the ankle): outboard a solid plate over the whole cage side; inboard (the roll servo's case
    is there) over the cage's top and onto a rim that closes the cage's horn side around the horn, so arms and cage
    are one box (verify_fea). The roll servo slides into the cage from the inboard end, horn off; its cables leave
    there. Below the ankle axis the plates leave room for the foot's roll bracket, which swings there."""
    R = ankle_roll_servo()
    zt = HW + C + WALL
    x_back = XA - HF - HR - RP
    x_case = XA - HF + HO                                                                       # roll case's horn side
    xf = XA + TU + 0.6                                                                          # clear of the foot's arm
    front = rounded_polygon([(13.0, -18.0), (13.0, 13.0), (xf, zt + 0.05), (xf, -18.0)], [8.0, 12.9, 0.0, 0.0])
    slab = rect(x_case + OUT_C, xf + 0.1, -6.5, zt + 0.05)                                    # over the foot bracket
    slab_hub = rect(x_case + OUT_C, xf + 0.1, -11.0, zt + 0.05)                               # (inboard: verify_fea)
    # (at the +-20 deg roll limit the foot's roll bracket reaches the horn arm's plane only below z -7.5, the hub
    # arm's plane only below z -12)
    top = rect(x_back, xf + 0.1, zt - WALL - 0.05, zt + ANKLE_TOP)                            # on the cage's top wall
    # joint stop: with the toes ANKLE_STOP_DEG past the limit pointing down, this block's top meets the bottom of the
    # shin's arm plates (both arms, coplanar), before the foot's horn screw heads reach the shin (verify_stops)
    stop = rect(xf - 0.5, ANKLE_STOP_X, zt - 1.0, zt + ANKLE_TOP + ANKLE_STOP_H)
    side = rect(x_back, x_case + 0.3, -zt - 0.05, zt + 0.05)                                  # outboard: whole cage side
    p = u_arms(ankle_pitch_servo(0.0), front, extra_horn=[slab, top, side, stop], extra_hub=[slab_hub, top, stop])
    p += cage(R, skip=("l0",), omit=-1, lengthwise=True)      # the roll servo slides in from the inboard end;
    #                                                                         the foot slides on from below
    x0s, x1s, ws, zs = ST["STRIP"]
    p += [("box", (x_case + OUT_C, XA - 0.4), (-ST["LB"] - C - WALL, HW + C + WALL - 0.1 + 0.6), (-zt, zt)),  # rim over
          ("hole", "x", (0.0, 0.0), 22.0, (x_case - 0.1, XA - 0.3)),                        # the case's horn side
          ("cut", (x_case, XA - HF + zs + 0.3), (-ST["LB"] - C - WALL - 0.5, -x0s + 0.5), (-ws - 0.5, ws + 0.5))]   # the
    #                         case's strip, out to the inboard end (the servo slides in from there)
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
    # with the ankle pitched back and rolled past its limit, the shin's lower back corner reaches the horn arm's side
    # edges: a shallow recess there, so the ankle bracket (the roll joint's own stop) touches the foot first
    xh = XA + TU                                                                                # horn arm's front face
    for sy in (1, -1):
        p.append(("cut", (xh - FOOT_RECESS, xh + 0.1), tuple(sorted((sy * 12.5, sy * 17.0))), (-16.0, 0.0)))
    return p


# ------------------------------------------------------------------------------------------------ upper body
def torso():
    """Lower torso shell (pelvis frame): the reference robot's octagonal body. Its floor bolts onto the pelvis; below the
    floor a skirt hides the hip-yaw servos, so the legs come straight out from under the body. Inside: Raspberry Pi on
    the back wall, battery, servo driver, power. A lip around the top takes the chest cap (4 screws through the cap).
    The hip-yaw servos' cables come up through the two openings over their sockets, the legs' through the rear slot."""
    w = TWALL
    p = [("prism", "z", octagon(TD, TW, TCH), (TZB, TZS)),
         ("pcut", "z", oct_inset(w), (TZ0 + w, TZS + 0.1)),
         ("pcut", "z", oct_inset(w), (TZB - 0.1, TZ0)),                                          # the skirt (open below)
         ("cut", (-34.0, -26.0), (-14.0, 14.0), (TZ0 - 0.1, TZ0 + w + 0.1)),                    # leg cables up
         ("hole", "x", (0.0, 88.0), 12.0, (-TD - 0.1, -TD + w + 0.1))]                          # push-to-talk button
    for sy in (1, -1):                                                                          # yaw servos' cables up
        ys = sorted((sy * (HIP_Y - ST["SOCKET"][0] + 0.5), sy * (HIP_Y - ST["SOCKET"][1] - 0.5)))
        p.append(("cut", (-WIN_W, WIN_W), tuple(ys), (TZ0 - 0.1, TZ0 + w + 0.1)))
    for x in (-20.0, 24.0):
        for y in (-25.0, 25.0):
            p.append(("hole", "z", (x, y), 3.4, (TZ0 - 0.1, TZ0 + w + 0.1)))                  # bolts to the pelvis
            screw("z", (x, y), TZ0 + w, -1, "M3", 8.0, "insert", "M3 x 8 socket head, into the pelvis plate's M3 x 4 "
                  "heat-set insert; its tip goes on into the hole through the rib below")
    p += [("lprism", "z", oct_inset(w - 0.5), (TZS - 6.0, TZS)),                               # lip, fused to the wall
          ("lprism", "z", oct_inset(w + 0.2), (TZS - 0.1, TZS + 5.0)),                         # lip above the seam
          ("lpcut", "z", oct_inset(w + 2.2), (TZS - 6.1, TZS + 5.1))]
    for x in (TD, -TD):
        sgn = 1 if x > 0 else -1
        for y in (-15.0, 15.0):
            p.append(("lhole", "x", (y, TZS + 2.5), 1.8, tuple(sorted((sgn * (TD - w - 2.4), sgn * (TD - w + 0.3))))))
    for y in (-29.0, 29.0):                                                                     # Raspberry Pi standoffs
        for z in (96.0, 145.0):                                                                 # (M2 x 8 CSK through the
            p.append(("lcyl", "x", (y, z), 3.2, (-TD + w - 0.5, -TD + w + 6.0)))               # board's 2.7 mm holes)
            p.append(("lhole", "x", (y, z), 1.8, (-TD + 1.4, -TD + w + 6.1)))
    p += webcam_mount()
    return p


# the chest camera: a USB webcam head (Lapcare Lapcam HD 720M P: about 85 x 35 x 25 mm, a pill with the lens in the
# middle; measure yours) behind a window in the torso's front wall, under the lettering. CAM = (width y, height z,
# depth x, centre height z, lens window diameter)
CAM = (85.0, 35.0, 25.0, 150.0, 20.0)
CAM_SHELF_T, CAM_GAP = 6.0, 0.3


def webcam_mount():
    """Inside the torso's front wall: a shelf under and over the webcam's head, its face against the wall and its lens
    at the window; the clamp plate (JX0_CamClamp) screws onto the shelves' back ends with 4 M2 x 10 CSK and holds it
    there. The bottom shelf is split in the middle for the USB cable (take the webcam off its clip; the cable goes
    down to the Raspberry Pi)."""
    W, H, D, zc, lens = CAM
    xf = TD - TWALL                                                  # inner face of the front wall
    xb = xf - CAM_GAP - D                                            # the webcam's back = the clamp plate's front
    hw = W / 2 - 8.0                                                 # the shelves stay on the wall's flat front
    zlo, zhi = zc - H / 2 - CAM_GAP, zc + H / 2 + CAM_GAP
    p = [("lhole", "x", (0.0, zc), lens, (xf - 0.5, TD + 0.1)),                              # the lens window
         ("lbox", (xb, xf + 0.5), (-hw, -7.0), (zlo - CAM_SHELF_T, zlo)),                   # bottom shelf, split for
         ("lbox", (xb, xf + 0.5), (7.0, hw), (zlo - CAM_SHELF_T, zlo)),                     # the cable
         ("lbox", (xb, xf + 0.5), (-hw, hw), (zhi, zhi + CAM_SHELF_T))]                     # top shelf
    for y, z in cam_screws():
        p.append(("lhole", "x", (y, z), 1.8, (xb - 0.1, xb + 9.0)))                         # M2 pilots, 9 mm deep
    return p


def cam_screws():
    W, H, D, zc, lens = CAM
    zlo, zhi = zc - H / 2 - CAM_GAP, zc + H / 2 + CAM_GAP
    return [(y, z) for y in (-22.0, 22.0) for z in (zlo - CAM_SHELF_T / 2, zhi + CAM_SHELF_T / 2)]


def cam_clamp():
    """The webcam's clamp plate (torso frame): 4 mm, over the shelves' back ends and the webcam's back, a notch at the
    bottom for its cable; 4 M2 x 10 CSK through it into the shelves."""
    W, H, D, zc, lens = CAM
    xb = TD - TWALL - CAM_GAP - D
    hw = W / 2 - 8.0
    zlo, zhi = zc - H / 2 - CAM_GAP, zc + H / 2 + CAM_GAP
    t = 4.0
    p = [("box", (xb - t, xb), (-hw, hw), (zlo - CAM_SHELF_T, zhi + CAM_SHELF_T)),
         ("cut", (xb - t - 0.1, xb + 0.1), (-7.0, 7.0), (zlo - CAM_SHELF_T - 0.1, zlo + 6.0))]   # the cable's notch
    for y, z in cam_screws():
        p += [("hole", "x", (y, z), M2["hole"] + 0.2, (xb - t - 0.1, xb + 0.1)),
              ("hole", "x", (y, z), M2["cbore"], (xb - t - 0.1, xb - t + 1.3))]
        screw("x", (y, z), xb - t + 1.3, +1, "M2", 10.0 - (CSK["head"][0] - M2["hole"] - 0.2) / 2, "printed",
              "M2 x 10 CSK through the camera clamp into the torso's camera shelf", "csk", 10.0)
    return p


def webcam_envelope():
    """The webcam head's room (torso frame), a keep-out for the fit and interference checks."""
    W, H, D, zc, lens = CAM
    xf = TD - TWALL
    return [("box", (xf - CAM_GAP - D + 0.2, xf - 0.2), (-W / 2 + 0.5, W / 2 - 0.5), (zc - H / 2 + 0.2, zc + H / 2 - 0.2))]


def chest_cap():
    """Chest cap (pelvis frame): top of the octagonal torso with chamfered top edges, vent slots and a speaker grille,
    the neck STS3215 standing on top (its cables go down through the window under it), and on each side wall the pad
    the shoulder servo's horn bolts to (from inside)."""
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
        y_in = sgn * (TW - w - 0.5)
        ys = tuple(sorted((y_in, sgn * sy)))
        p.append(("lcyl", "y", (sx, sz), 12.5, ys))                                            # shoulder pad
        p += late(horn_holes("y", (sx, sz), (ys[0] - 0.1, ys[1] + 0.1)))
        seat = drive_seat(sgn * sy, -sgn)                                                       # M3 x 6 from inside
        p += late(horn_seats("y", (sx, sz), seat, y_in))
        horn_screws("y", (sx, sz), seat, sgn, 6.0, "drive")
        for xc in (-15.0, -9.0, -3.0, 3.0, 9.0, 15.0):                                         # vent slots
            p.append(("cut", (xc - 1.25, xc + 1.25), tuple(sorted((sgn * 36.0, sgn * 48.0))), (TZT - w - 0.1, TZT + 0.1)))
        for y in (-15.0, 15.0):                                                                # screws into the lip
            p.append(("hole", "x", (y, TZS + 2.5), 2.4, tuple(sorted((sgn * (TD - w - 0.1), sgn * (TD + 0.1))))))
    for x in (TD, -TD):
        sgn = 1 if x > 0 else -1
        for y in (-15.0, 15.0):
            screw("x", (y, TZS + 2.5), x, -sgn, "M2", 8.0 - (CSK["head"][0] - 2.4) / 2, "printed",
                  "M2 x 8 CSK, cuts its thread in the torso lip's 1.8 mm hole", "csk", 8.0)
    for x in (18.0, 24.0, 30.0):                                                               # speaker grille
        for y in (-12.0, -6.0, 0.0, 6.0, 12.0):
            p.append(("hole", "z", (x, y), 3.5, (TZT - w - 0.1, TZT + 0.1)))
    p += rear_face_mount("z", (0.0, 0.0), (1, 1), (0, 1), TZT, +1)                            # neck servo on top
    return p


def head():
    """Head (frame: neck horn face, z up), v0.5: a wide head with two LED-ring eyes. Each eye is a WS2812 12-LED ring
    (50 mm outside, about 35 mm inside, black PCB, LEDs on the front, solder pads on the back) in a pocket in the face:
    a boss in the middle centres the ring by its hole and is the pupil; a 1.2 mm clear PETG lens (JX0_EyeLens) covers
    it flush with the face. Behind each ring a slot takes its wires into the head (turn the ring so its pads sit over
    the slot); inside, the two rings are chained and three wires (5 V, GND, data) go down the neck hub's cable hole
    with the microphone's, so no wire shows in front. The microphone listens through the holes between the eyes. Ear
    pods on the sides. Hollow (walls >= 2.5 mm under every fillet), back window for the wiring, open underneath: it
    slides down over the neck hub (bolted to the neck horn first) and 2 M2 x 10 CSK through its back wall hold it
    there; the hub's shape carries the turning."""
    xb, xf, hy, hz = HEAD_BOX
    front = rounded_polygon([(-hy, 0.0), (hy, 0.0), (hy, hz), (-hy, hz)], [6.0, 6.0, 14.0, 14.0])
    p = [("prism", "x", front, (xb, xf))]
    # front edges small (the eyes fill the face), back edges soft; the chin and bottom-corner radii leave a wide flat
    # rim on the open bottom for the head to print standing on
    for xc, zc, du, dv, r in ((xf, hz, -1, -1, 9.0), (xb, hz, 1, -1, 18.0), (xf, 0.0, -1, 1, 5.0), (xb, 0.0, 1, 1, 5.0)):
        p.append(("pcut", "y", corner_cut((xc, zc), (du, dv), r), (-hy - 1.0, hy + 1.0)))
    for xc, yc, du, dv, r in ((xf, hy, -1, -1, 6.0), (xf, -hy, -1, 1, 6.0), (xb, hy, 1, -1, 12.0), (xb, -hy, 1, 1, 12.0)):
        p.append(("pcut", "z", corner_cut((xc, yc), (du, dv), r), (-0.1, hz + 0.1)))       # rounded vertical edges
    p += [("cut", (-26.0, 26.0), (-24.0, 24.0), (-0.1, 16.1)),                               # the neck hub's plate
          ("cut", (-26.0, 30.0), (-hy + 5.0, hy - 5.0), (16.0, 62.0)),                       # hollow
          ("cut", (xb - 0.1, -25.9), (-16.0, 16.0), (16.0, 44.0))]                           # back window
    ey, ez, d, depth = EYE
    floor = xf - depth
    for yc in (-ey, ey):
        p += [("hole", "x", (yc, ez), d, (floor, xf + 0.1)),                                 # the ring's pocket
              ("cut", (29.9, floor + 0.1), (yc - 6.0, yc + 6.0), (ez - 25.0, ez - 17.0)),    # its wires, into the head
              ("lcyl", "x", (yc, ez), PUPIL / 2, (floor - 0.05, xf - LENS_T - 0.05))]        # pupil: centres the ring
    for zc in (ez - 6.0, ez, ez + 6.0):                                                      # microphone, between the
        p.append(("hole", "x", (0.0, zc), 2.0, (29.9, xf + 0.1)))                            # eyes
    ex, ez2, eh, er = EAR
    for sy in (1, -1):                                                                       # ear pods: a raised disc
        g = tuple(sorted((sy * (hy + eh - 0.6), sy * (hy + eh + 0.1))))                       # with a groove ring
        p += [("cyl", "y", (ex, ez2), er, tuple(sorted((sy * (hy - 0.5), sy * (hy + eh))))),
              ("hole", "y", (ex, ez2), 2 * (er - 3.0), g), ("lcyl", "y", (ex, ez2), er - 4.0, g)]
    for y in (-HEAD_PIN_Y, HEAD_PIN_Y):                                                      # into the hub's back
        seat = -26.0 - 0.1 - 5.0
        p += [("hole", "x", (y, HEAD_PIN_Z), M2["hole"] + 0.2, (xb - 0.1, -25.9)),
              ("hole", "x", (y, HEAD_PIN_Z), M2["cbore"], (xb - 0.1, seat))]
        screw("x", (y, HEAD_PIN_Z), seat, +1, "M2", 10.0 - (CSK["head"][0] - M2["hole"] - 0.2) / 2, "printed",
              "M2 x 10 CSK through the head's back wall into the neck hub", "csk", 10.0)
    return p


def eye_lens():
    """Eye lens (frame: its back face on x = 0, the eye's axis): a 1.2 mm clear PETG disc that covers the LED ring
    flush with the face, resting on the LEDs and the pupil; a few dots of clear silicone at the rim hold it. Printed
    flat, it diffuses the LEDs into a glowing ring."""
    return [("cyl", "x", (0.0, 0.0), LENS_D / 2, (0.0, LENS_T - 0.05))]


HEAD_PIN_Y, HEAD_PIN_Z = 10.0, 8.0
HEAD_BOX = (-33.0, 37.0, 60.0, 70.0)       # back x, front x, half width, height (v0.4: +-33, 39, 62)
EAR = (0.0, 36.0, 2.0, 14.0)               # ear pod: x, z, height off the side, radius
# the eyes: WS2812 12-LED rings, 50 mm outside (robocraze "WS2812 12 Bit RGB LED (round)"; the inside, about 35 mm,
# is read off the photo: measure yours). EYE = (centre y, centre z, pocket diameter, pocket depth = the ring's
# ~3.4 mm (1.6 mm PCB + 1.6 mm LEDs) + the lens)
EYE = (28.0, 35.0, 50.8, 4.6)
PUPIL = 33.0                               # the boss in the ring's ~35 mm hole
LENS_T, LENS_D = 1.2, 50.4


def neck_hub():
    """Neck hub (head frame: on the neck horn face, z up): bolted to the neck horn from above with 4 M3 x 8 pan heads
    (straight screwdriver, before the head goes on). The head slides down over it; its rectangular plate fills the
    head's opening, so it turns the head, and 2 M2 x 10 CSK through the head's back wall go into its back block."""
    c = 0.1                                                                                   # clearance in the head
    p = [("box", (-26.0 + c, 26.0 - c), (-24.0 + c, 24.0 - c), (0.0, 4.0)),
         ("cyl", "z", (0.0, 0.0), 15.0, (3.9, 12.0)),
         ("box", (-26.0 + c, -18.0), (-HEAD_PIN_Y - 4.0, HEAD_PIN_Y + 4.0), (3.9, 12.0)),
         ("hole", "z", (-18.0, 0.0), 8.0, (-0.1, 12.1))]                                    # microphone cable down
    p += horn_holes("z", (0.0, 0.0), (-0.1, 12.1))
    seat = drive_seat(0.0, +1, 8.0)
    p += horn_seats("z", (0.0, 0.0), seat, 12.0)
    horn_screws("z", (0.0, 0.0), seat, -1, 8.0, "drive", "M3 x 8 pan head, from above before the head goes on")
    for y in (-HEAD_PIN_Y, HEAD_PIN_Y):
        p.append(("hole", "x", (y, HEAD_PIN_Z), 1.8, (-26.0 + c - 0.1, -26.0 + c + 6.0)))
    return p


def shoulder_servo():                      # arm frame (shoulder axis on the horn face, y outward): case down
    return Servo((0.0, HF, 0.0), "y", -1, ("z", -1))


def elbow_servo():                         # arm frame: under the shoulder servo, lying forward, horn outward
    return Servo((0.0, ELBOW_Y - HF, -UA_L), "y", +1, ("x", +1))


def upper_arm():
    """Arm link 1 (frame: shoulder-pitch axis on the shoulder horn face, y outward), the reference robot's shoulder: the
    shoulder STS3215 hangs outside the chest (its horn bolted to the chest pad) in a hood, and the elbow STS3215 lies in
    a box under it, horn outward. Both are single-sided: 3 mm rear plates, the case screws' heads on their faces."""
    S = shoulder_servo()
    top = ST["LA"] + C + WALL
    p = cage(S, rp=CASE_UNDER) + cage(elbow_servo(), rp=CASE_UNDER)
    hw = HW + C + WALL + 0.05
    hood = rounded_polygon([(-hw, top - WALL + 0.05), (hw, top - WALL + 0.05), (hw, top + 4.0), (-hw, top + 4.0)],
                           [0.0, 0.0, 6.0, 6.0])                                                # (x, z) rounded hood
    p.append(("prism", "y", hood, (HF - HO, HF + HR + CASE_UNDER)))
    # elbow stop: a post out of the shoulder cage's side into the blade's plane, beside the shoulder servo's plugs;
    # the blade, swung forward past its limit, hits the post before it reaches the plugs (verify_stops)
    x, z, r = ELBOW_STOP
    p.append(("cyl", "y", (x, z), r, (36.5, ELBOW_Y + 3.2)))
    return p


def arm_blade():
    """Arm link 2 (frame: elbow axis on the elbow horn face, y outward): the reference robot's thick paddle blade with a
    raised boss on the horn (M3 x 8 through both, heads sunk in the boss)."""
    prof = rounded_polygon([(-17.0, 16.0), (17.0, 16.0), (19.0, -30.0), (13.0, -BLADE_L), (-11.0, -BLADE_L), (-17.0, -30.0)],
                           [16.0, 16.0, 40.0, 12.0, 12.0, 40.0])
    p = [("prism", "y", prof, (0.0, BLADE_T)), ("cyl", "y", (0.0, 0.0), 12.5, (BLADE_T, BLADE_T + 2.0))]
    p += horn_holes("y", (0.0, 0.0), (-0.1, BLADE_T + 2.1))
    seat = drive_seat(0.0, +1, 6.0)
    p += horn_seats("y", (0.0, 0.0), seat, BLADE_T + 2.0)
    horn_screws("y", (0.0, 0.0), seat, -1, 6.0, "drive", "the servo bag's M3 x 6, heads 5 mm down in the boss")
    return p


def horn_shim():
    """0.4 mm shim between a horn and its arm (frame: horn axis z, on the horn face): on a servo whose drive horn sits
    lower than the deepest real horn, 1 or 2 of them under each horn arm make the U-bracket's span exact."""
    return [("cyl", "z", (0.0, 0.0), 9.8, (0.0, SHIM))] + horn_holes("z", (0.0, 0.0), (-0.1, SHIM + 0.1))


# ------------------------------------------------------------------------------------------------ catalogue
def _build(fn, mirror=False):
    """(primitives, screws) of a part builder; mirror = the right-side copy (y -> -y)."""
    global _SINK
    _SINK = []
    try:
        prims, sc = fn(), _SINK
    finally:
        _SINK = None
    return (mirror_y(prims), [mirror_screw(s) for s in sc]) if mirror else (prims, sc)


# name -> builder, mirrored (the right side of a left part), quantity
_CATALOGUE = [("JX0_Pelvis", pelvis, False, 1), ("JX0_YawKeeper_L", yaw_keeper, False, 1),
              ("JX0_YawKeeper_R", yaw_keeper, True, 1), ("JX0_YawRing_L", yaw_ring, False, 1),
              ("JX0_YawRing_R", yaw_ring, True, 1), ("JX0_HipYawBracket_L", hip_yaw_bracket, False, 1),
              ("JX0_HipYawBracket_R", hip_yaw_bracket, True, 1), ("JX0_HipRollBracket_L", hip_roll_bracket, False, 1),
              ("JX0_HipRollBracket_R", hip_roll_bracket, True, 1), ("JX0_Thigh_L", thigh, False, 1),
              ("JX0_Thigh_R", thigh, True, 1), ("JX0_Shin_L", shin, False, 1), ("JX0_Shin_R", shin, True, 1),
              ("JX0_AnkleBracket_L", ankle_bracket, False, 1), ("JX0_AnkleBracket_R", ankle_bracket, True, 1),
              ("JX0_Foot", foot, False, 2), ("JX0_Torso", torso, False, 1), ("JX0_ChestCap", chest_cap, False, 1),
              ("JX0_Head", head, False, 1), ("JX0_EyeLens", eye_lens, False, 2), ("JX0_CamClamp", cam_clamp, False, 1), ("JX0_NeckHub", neck_hub, False, 1),
              ("JX0_UpperArm_L", upper_arm, False, 1),
              ("JX0_UpperArm_R", upper_arm, True, 1), ("JX0_ArmBlade_L", arm_blade, False, 1),
              ("JX0_ArmBlade_R", arm_blade, True, 1), ("JX0_HornShim", horn_shim, False, 40)]
# name -> (primitives, colour, quantity); name -> the screws whose heads sit on that part (screw())
PARTS, SCREWS = {}, {}
for _name, _fn, _mir, _q in _CATALOGUE:
    PARTS[_name], SCREWS[_name] = (lambda b: ((b[0], "sage", _q), b[1]))(_build(_fn, _mir))


# ------------------------------------------------------------------------------------------------ the servo
def servo_st(drive=True, idler=True, screw_head=True):
    """The real STS3215 (servo frame, see ST; the larger of the factory and SO-ARM100 models): case band, rear pad with
    the label block, the passive horn on its boss, the output strip, the drive horn (its face at the deepest real
    horn's) with the horn screw's head, the 8 horn holes and the 4 rear case holes. drive / idler = False: without
    that horn (a servo slid into its cage before its horns go on); screw_head = False: the drive horn on its spline
    before its centre screw (a U-bracket slides on over it)."""
    la, lb = ST["LA"], ST["LB"]
    b0, b1 = ST["BAND"]
    x0s, x1s, ws, zs = ST["STRIP"]
    x0l, x1l, wl, zl = ST["LABEL"]
    hd = ST["HORN_REAL"][1]
    p = [("box", (-la, lb), (-HW, HW), (b0, b1)),
         ("box", (5.3, lb), (-HW, HW), (-HR, b0 + 0.1)),                                     # rear pad
         ("box", (x0l, x1l), (-wl, wl), (-zl, -HR + 0.1)),                                   # label block
         ("cyl", "z", (0.0, 0.0), 3.0, (-ST["BOSS_TIP"], b0 + 0.1)),                         # rear boss
         ("box", (x0s, x1s), (-ws, ws), (b1 - 0.1, zs)),                                     # output strip
         ("cyl", "z", (0.0, 0.0), 5.3, (b1 - 0.1, b1 + 0.5))]                                # output spline boss
    if idler:
        p += [("cyl", "z", (0.0, 0.0), ST["IDLER_D"] / 2, (-HI, -HR + 0.05))]               # passive horn
        p += horn_holes("z", (0.0, 0.0), (-HI - 0.1, -HI + ST["IDLER_T"]), d=ST["HORN_HOLE"], centre=0)
    if drive:
        p += [("cyl", "z", (0.0, 0.0), ST["HORN_D"] / 2, (b1 - 0.1, hd))]                   # drive horn
        if screw_head:
            p += [("cyl", "z", (0.0, 0.0), 2.8, (hd - 0.1, hd + 1.55))]                      # horn screw head
        p += horn_holes("z", (0.0, 0.0), (hd - ST["HORN_T"], hd + 0.1), d=ST["HORN_HOLE"], centre=0)
    p += [("hole", "z", (x, y), ST["MOUNT_D"], (-HR - 0.1, -HR + ST["MOUNT_DEPTH"]))
          for x in ST["MOUNT_L"] for y in (-ST["MOUNT_W"], ST["MOUNT_W"])]
    return p


def servo_cables(mode="bent"):
    """Keep-out of a servo's two cables (servo frame; not built: verify_cad and verify_fit check nothing enters it).
    The plugs sit inside the case and the wires come straight out of the rear face over the sockets. "bent": the wires
    lie bent along the rear face, over the label block (4 mm deep), out past the case's far end and the cage's end
    wall. "straight": they go straight on through the plate the servo stands on (12 mm). "back": bent along the rear
    face over the label block, then out through the cage plate's window (12 mm) past its far half."""
    s0, s1, _ = ST["SOCKET"]
    if mode == "straight":
        return [("box", (s0 + 0.3, s1 - 0.3), (-9.0, 9.0), (-HR - 12.0, -HR))]
    x1l = ST["LABEL"][1]
    z = (-HR - 4.0, -HR)
    if mode == "back":
        return [("box", (s0 + 0.3, x1l + 0.5), (-9.0, 9.0), z), ("box", (20.0, x1l + 0.5), (-9.0, 9.0), (-HR - 12.0, -HR))]
    return [("box", (s0 + 0.3, x1l + 0.5), (-9.0, 9.0), z), ("box", (x1l + 0.5, ST["LB"] + C + WALL + 3.0), (-7.9, 7.9), z)]


def screw_head(s):
    """The head of screw s (a SCREWS entry) as a cylinder in its part's frame, from its seat outward."""
    d, k = (CSK if s.get("head") == "csk" else M3 if s["size"] == "M3" else M2)["head"]
    return [("cyl", s["axis"], s["c"], d / 2, _rng(s["seat"], s["seat"] - s["sense"] * k))]


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
