"""JX0 printable-part geometry (millimetres, each part in its robot link frame: x forward, y left, z up).

Single source of truth for the SolidWorks builder (build_cad.py), the STL export and the simulation model. Every part is
a list of primitives:
    ("box",  (x0, x1), (y0, y1), (z0, z1))                 boss (axis-aligned block)
    ("cut",  (x0, x1), (y0, y1), (z0, z1))                 pocket
    ("cyl",  axis, (c0, c1), r, (s0, s1))                  boss cylinder along axis; c = the other two coords in xyz order
    ("hole", axis, (c0, c1), d, (s0, s1))                  cylindrical cut
Servo interface: Feetech STS3215 12 V (Waveshare ST3215; research/raw/jx0_india_sourcing_raw.md, Waveshare 2D drawing): case 45.22 x
24.72 x 32 mm between the two horn faces, Ø19.2 horn on both faces (37.25 across them), output axis 10.11 mm from the
case end, horn holes 4 x Ø2.5 on a 14 mm circle, case mounting holes on the connector (rear) face 24.45 x 20.5 mm, first
row 18.41 mm from the output end. Screw sizes are not published: holes are Ø2.2 (M2 self-tapping) — ASSUMED, fit-check.
Every joint (12 leg, 4 arm, 1 neck) is the same 12 V STS3215. The style follows the reference robot in
media/reference.mp4: faceted octagonal torso with a vented chest cap, the neck servo exposed under a soft rounded head
with four holes, arms that are a shoulder cradle plus a flat blade, round-ended leg plates, cross-pattern horn screws.

Joints are single-sided: each servo's case is screwed to one link through its rear face, the next link bolts to its
output horn. All three hip axes meet at the hip centre and both ankle axes at the ankle centre (the gait model assumes it).
"""
from __future__ import annotations

# ------------------------------------------------------------------------------------------------ interface parameters
ST = dict(L=45.22, W=24.72, CASE=32.0, ENV=35.0, HORN_D=19.2, HORN_FACE=18.625, LA=10.11, LB=35.11,
          PCD=14.0, HORN_HOLE=2.7, MOUNT_L=(8.30, 32.75), MOUNT_W=10.25, SCREW=2.2, DISC_CLEAR=22.0)
T = 3.0            # plate thickness (PETG)
C = 0.4            # clearance
ZY = 30.0          # hip-yaw horn face above the hip centre
THIGH, SHIN = 100.0, 100.0
HIP_Y = 45.0       # half hip spacing
XR = -15.0         # hip-roll horn face (servo behind the hip centre, horn facing +x)
XA = -20.0         # ankle-roll horn face (servo behind the ankle centre, horn facing +x); the foot upright on it keeps
                   # 1 mm clear of the ankle-pitch servo's case corner (r 16.0 mm) at every toes-up angle (verify_cad)
SOLE_TO_ANKLE, FOOT_X, FOOT_W = 35.0, (-62.0, 58.0), 70.0
# torso: octagonal prism, half depth TD (x) and half width TW (y), vertical edges chamfered TCH, split at TZS into the
# lower shell and the chest cap; walls TWALL
TD, TW, TCH, TWALL = 42.0, 60.0, 16.0, 2.5
TZ0, TZS, TZT, TOP_CH = 68.625, 168.0, 210.0, 8.0     # cap tall enough that the thickened wall under the top chamfer
                                                     # clears the shoulder servos (verify_cad)
# shoulder pitch: horn face just proud of the torso side wall, axis 12.5 mm forward of the torso centre
SHOULDER = (12.5, TW - TWALL + (ST["HORN_FACE"] - ST["CASE"] / 2), 186.0)
UA_L = 52.0                                                         # shoulder pitch axis to elbow axis
UA_PLATE = (1.0, 4.0)                                               # cradle plate (y, outward from the pitch horn face)
ELBOW_Y = UA_PLATE[1] + ST["CASE"] + (ST["HORN_FACE"] - ST["CASE"] / 2)   # elbow horn face: 38.625 outboard
BLADE_L, BLADE_T = 100.0, 5.0
NECK_Z = TZT + ST["CASE"] + (ST["HORN_FACE"] - ST["CASE"] / 2)     # neck horn face (head origin): 239.625


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
         ("box", (XR + 0.5, XR + 12.0), (yr - T + 0.5, -2.0), (-15.0, -12.8))]           # gusset (clear of the pitch servo case)
    p += horn_holes("x", (0.0, 0.0), (XR - 0.1, XR + T + 0.1))
    p += rear_face_mount("y", (0.0, 0.0), (0, 1), (1, 1), (yr - T - 0.1, yr + 0.1))
    return p


def thigh():
    """Bolts to the hip-pitch horn (outside, +y) and carries the knee servo on its inner face (case up, horn -y)."""
    y0 = ST["HORN_FACE"]
    p = [("prism", "y", rounded_polygon([(-15, 15), (15, 15), (15, -THIGH - 15), (-15, -THIGH - 15)], [14.9] * 4),
          (y0, y0 + 4.0)),                                                                  # 4 mm round-ended side plate
         ("box", (-15.0, -11.0), (y0 + 3.5, y0 + 9.0), (-THIGH + 20.0, -5.0)),           # rear flange (stiffener)
         ("box", (11.0, 15.0), (y0 + 3.5, y0 + 9.0), (-THIGH + 20.0, -5.0))]             # front flange
    p += horn_holes("y", (0.0, 0.0), (y0 - 0.1, y0 + 4.1))
    p += rear_face_mount("y", (0.0, -THIGH), (1, 1), (0, 1), (y0 - 0.1, y0 + 4.1))
    return p


def shin():
    """Bolts to the knee horn (inside, -y) and carries the ankle-pitch servo on its outer face (case up, horn +y).
    The knee servo's rear face sits on the thigh plate at y = +18.625, so its horn face is at 18.625 - 32 - 2.625 = -16."""
    y1 = ST["HORN_FACE"] - ST["CASE"] - (ST["HORN_FACE"] - ST["CASE"] / 2)
    p = [("prism", "y", rounded_polygon([(-15, 15), (15, 15), (15, -SHIN - 15), (-15, -SHIN - 15)], [14.9] * 4),
          (y1 - 4.0, y1)),
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
         ("box", (xa_rear - T, xa_rear), (-35.5, y0 + 0.5), (-15.0, 15.0)),              # rear plate (roll servo mount; short
                                                                                          # inboard end: clears the other ankle)
         ("box", (xa_rear - 0.5, -24.0), (y0 - 3.0, y0 + 0.5), (-15.0, -12.0))]          # gusset
    p += horn_holes("y", (0.0, 0.0), (y0 - 0.1, y0 + T + 0.1))
    p += rear_face_mount("x", (0.0, 0.0), (0, -1), (1, 1), (xa_rear - T - 0.1, xa_rear + 0.1))
    return p


def foot():
    """Sole plate + an upright that bolts to the ankle-roll horn (x = XA). Symmetric: one part for both feet."""
    zs = -SOLE_TO_ANKLE
    p = [("box", FOOT_X, (-FOOT_W / 2, FOOT_W / 2), (zs, zs + 6.0)),                     # sole plate
         ("box", (XA, XA + T), (-12.0, 12.0), (zs + 5.5, 12.0)),                         # upright on the roll horn (24 wide:
         ("box", (XA + 2.5, XA + 6.0), (-12.0, 12.0), (zs + 5.5, -20.0))]                # heel block   clears the ankle bracket to ~24 deg roll)
    p += horn_holes("x", (0.0, 0.0), (XA - 0.1, XA + T + 0.1))
    for x in (-42.0, 10.0, 36.0):                                                        # lightening, clear of the upright
        p.append(("hole", "z", (x, 0.0), 12.0, (zs - 0.1, zs + 6.1)))
    for xc, yc, du, dv in ((FOOT_X[1], FOOT_W / 2, -1, -1), (FOOT_X[1], -FOOT_W / 2, -1, 1),
                           (FOOT_X[0], FOOT_W / 2, 1, -1), (FOOT_X[0], -FOOT_W / 2, 1, 1)):
        p.append(("pcut", "z", corner_cut((xc, yc), (du, dv), 12.0), (zs - 0.1, zs + 6.1)))   # rounded corners
    return p


# ------------------------------------------------------------------------------------------------ upper body
def torso():
    """Lower torso shell (pelvis frame): the reference robot's octagonal body, floor bolted to the pelvis, open top that
    the chest cap closes. Inside: Raspberry Pi on the back wall, battery, servo driver, power. A lip around the top
    takes the cap (4 screws through the cap wall)."""
    w = TWALL
    p = [("prism", "z", octagon(TD, TW, TCH), (TZ0, TZS)),
         ("pcut", "z", oct_inset(w), (TZ0 + w, TZS + 0.1)),
         ("cut", (-TD - 0.1, -TD + w + 0.1), (-16.0, 16.0), (TZ0 + w, TZ0 + w + 14.0)),      # leg cables in
         ("hole", "x", (0.0, 88.0), 12.0, (-TD - 0.1, -TD + w + 0.1))]                      # push-to-talk button
    for x in (0.0, 28.0):
        for y in (-25.0, 25.0):
            p.append(("hole", "z", (x, y), 3.2, (TZ0 - 0.1, TZ0 + w + 0.1)))              # bolts to the pelvis
    p += [("lprism", "z", oct_inset(w - 0.5), (TZS - 6.0, TZS)),                           # lip, fused to the wall
          ("lprism", "z", oct_inset(w + 0.2), (TZS - 0.1, TZS + 5.0)),                     # lip above the seam
          ("lpcut", "z", oct_inset(w + 2.2), (TZS - 6.1, TZS + 5.1))]
    for x in (TD, -TD):
        sgn = 1 if x > 0 else -1
        for y in (-15.0, 15.0):
            p.append(("lhole", "x", (y, TZS + 2.5), 2.5, tuple(sorted((sgn * (TD - w - 2.4), sgn * (TD - w + 0.3))))))
    for y in (-29.0, 29.0):                                                                 # Raspberry Pi standoffs
        for z in (96.0, 145.0):
            p.append(("lcyl", "x", (y, z), 3.2, (-TD + w - 0.5, -TD + w + 6.0)))
            p.append(("lhole", "x", (y, z), 2.5, (-TD + w, -TD + w + 6.1)))
    return p


def chest_cap():
    """Chest cap (pelvis frame): top of the octagonal torso with chamfered top edges, vent slots over the shoulder servos
    and a speaker grille, the neck STS3215 standing on top, and the two shoulder-pitch STS3215 inside (horns out through
    the side walls)."""
    w, ch = TWALL, TOP_CH
    p = [("prism", "z", octagon(TD, TW, TCH), (TZS, TZT)),
         ("pcut", "x", chamfer_cut((TW, TZT), (-1, -1), ch), (-TD - 1.0, TD + 1.0)),
         ("pcut", "x", chamfer_cut((-TW, TZT), (1, -1), ch), (-TD - 1.0, TD + 1.0)),
         ("pcut", "y", chamfer_cut((TD, TZT), (-1, -1), ch), (-TW - 1.0, TW + 1.0)),
         ("pcut", "y", chamfer_cut((-TD, TZT), (1, -1), ch), (-TW - 1.0, TW + 1.0)),
         # hollow, open below, stepped under the chamfers so the wall stays >= 2.5 mm
         ("pcut", "z", oct_inset(w), (TZS - 0.1, TZT - ch - w)),
         ("pcut", "z", oct_inset(w + ch / 2), (TZT - ch - w - 0.1, TZT - ch / 2 - w)),
         ("pcut", "z", oct_inset(w + ch), (TZT - ch / 2 - w - 0.1, TZT - w))]
    sx, _, sz = SHOULDER
    for sgn in (1, -1):
        p.append(("hole", "y", (sx, sz), 22.0, tuple(sorted((sgn * (TW - w - 0.1), sgn * (TW + 0.1))))))   # pitch horns
        for xc in (-15.0, -9.0, -3.0, 3.0, 9.0, 15.0):                                         # vent slots
            p.append(("cut", (xc - 1.25, xc + 1.25), tuple(sorted((sgn * 36.0, sgn * 48.0))), (TZT - w - 0.1, TZT + 0.1)))
        for y in (-15.0, 15.0):                                                                # screws into the lip
            p.append(("hole", "x", (y, TZS + 2.5), 3.4, tuple(sorted((sgn * (TD - w - 0.1), sgn * (TD + 0.1))))))
    for x in (18.0, 24.0, 30.0):                                                               # speaker grille
        for y in (-12.0, -6.0, 0.0, 6.0, 12.0):
            p.append(("hole", "z", (x, y), 3.5, (TZT - w - 0.1, TZT + 0.1)))
    p += rear_face_mount("z", (0.0, 0.0), (1, 1), (0, 1), (TZT - w - 0.1, TZT + 0.1))         # neck servo on top
    # shoulder-pitch servo plates inside (case behind the shaft, rear face toward the middle)
    yr = TW - w - ST["CASE"]
    for sgn in (1, -1):
        ys = tuple(sorted((sgn * (yr - 3.0), sgn * yr)))
        p.append(("lbox", (-(TD - w) - 0.5, TD - w + 0.5), ys, (TZS + 6.5, TZT - w + 0.5)))
        p += late(rear_face_mount("y", (sx, sz), (0, -1), (1, 1), (ys[0] - 0.1, ys[1] + 0.1)))
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


def upper_arm():
    """Arm link 1 (frame: shoulder-pitch axis on the pitch horn face, y outward), the reference robot's shoulder cradle:
    a round-ended plate on the pitch horn and a cradle around the elbow STS3215 (axis y, horn outward) 52 mm below."""
    wx = ST["W"] / 2 + C
    z_top = -UA_L + ST["LB"] + C
    prof = rounded_polygon([(-16.0, 16.0), (16.0, 16.0), (16.0, -UA_L - 16.0), (-16.0, -UA_L - 16.0)], [15.9] * 4)
    p = [("cyl", "y", (0.0, 0.0), 11.0, (0.0, UA_PLATE[0] + 0.1)),                        # pad on the horn
         ("prism", "y", prof, UA_PLATE),
         ("box", (wx, wx + 2.5), (UA_PLATE[1] - 0.5, 20.0), (-UA_L - 14.0, z_top + 2.5)),   # cradle: front wall
         ("box", (-wx - 2.5, -wx), (UA_PLATE[1] - 0.5, 20.0), (-UA_L - 14.0, z_top + 2.5)), # back wall
         ("box", (-wx - 2.5, wx + 2.5), (UA_PLATE[1] - 0.5, 20.0), (z_top, z_top + 2.5))]   # top
    p += horn_holes("y", (0.0, 0.0), (-0.1, UA_PLATE[1] + 0.1))
    p += rear_face_mount("y", (0.0, -UA_L), (1, 1), (0, 1), (UA_PLATE[0] - 0.1, UA_PLATE[1] + 0.1))
    return p


def arm_blade():
    """Arm link 2 (frame: elbow axis on the elbow horn face, y outward): the flat tapered blade of the reference robot."""
    prof = rounded_polygon([(-17.0, 16.0), (17.0, 16.0), (17.0, -12.0), (12.0, -BLADE_L), (-10.0, -BLADE_L), (-17.0, -12.0)],
                           [16.0, 16.0, 40.0, 10.0, 10.0, 40.0])
    return [("prism", "y", prof, (0.0, BLADE_T))] + horn_holes("y", (0.0, 0.0), (-0.1, BLADE_T + 0.1))


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
