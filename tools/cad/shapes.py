"""Geometry helpers for JX1 structural parts (all coordinates metres, in the part's robot link frame)."""
from __future__ import annotations

import math

from swlib.part import Part

NORMAL = {"x": ("Right Plane", "YZ"), "y": ("Top Plane", "XZ"), "z": ("Front Plane", "XY")}
SIDE = [1]   # +1 left leg (as designed), -1 right leg: every helper mirrors y -> -y


def set_side(sy):
    SIDE[0] = 1 if sy >= 0 else -1


def my(y):
    return SIDE[0] * y


def _m3(p3):
    return (p3[0], SIDE[0] * p3[1], p3[2])


def _span(normal, a0, a1):
    if normal == "y" and SIDE[0] < 0:
        return min(-a0, -a1), max(-a0, -a1)
    return a0, a1


def uv(axis_normal, p3):
    """Model (x,y,z) -> sketch (u,v) for a plane with the given normal ('x','y','z')."""
    x, y, z = p3
    if axis_normal == "z":
        return (x, y)
    if axis_normal == "y":
        return (x, -z)
    return (-z, y)


def chamfer_rect(a0, b0, a1, b1, c):
    """Octagon (rectangle with 45° chamfered corners) in 2D coordinates (a, b)."""
    c = min(c, (a1 - a0) / 2 - 1e-4, (b1 - b0) / 2 - 1e-4)
    return [(a0 + c, b0), (a1 - c, b0), (a1, b0 + c), (a1, b1 - c), (a1 - c, b1), (a0 + c, b1), (a0, b1 - c), (a0, b0 + c)]


def ngon(ca, cb, r, n=8, start=22.5):
    return [(ca + r * math.cos(math.radians(start + 360 * k / n)), cb + r * math.sin(math.radians(start + 360 * k / n))) for k in range(n)]


def _plane(p: Part, normal, offset, tag):
    base, _ = NORMAL[normal]
    if abs(offset) < 1e-12:
        return base
    name = f"PL_{tag}"
    if name not in p.features:
        p.ref_plane_offset(base, abs(offset), name, flip=offset < 0)
    return name


def plate(p: Part, name, normal, a0, a1, outline_model, holes=(), merge=True):
    """Extruded plate between a0 < a1 along `normal`. outline_model: list of 3D points (only the in-plane
    coordinates matter); holes: list of (point3d, diameter). Returns the feature name. Mirrored for SIDE = -1."""
    a0, a1 = _span(normal, a0, a1)
    outline_model = [_m3(q) for q in outline_model]
    holes = [(_m3(q), d) for q, d in holes]
    plane = _plane(p, normal, a0, f"{name}_base")
    key = NORMAL[normal][1]
    with p.sketch(key, f"SK_{name}", plane_name=plane) as sk:
        sk.polygon([uv(normal, q) for q in outline_model])
        for q, d in holes:
            u, v = uv(normal, q)
            sk.circle(u, v, d / 2)
    p.extrude(f"SK_{name}", a1 - a0, name, merge=merge)
    return name


def plate2d(p: Part, name, normal, a0, a1, outline_uv, holes_uv=(), merge=True):
    """Same as plate() but with outline/holes already in sketch (u, v) coordinates (v = y for normals x and z)."""
    a0, a1 = _span(normal, a0, a1)
    if normal in ("x", "z") and SIDE[0] < 0:
        outline_uv = [(u, -v) for (u, v) in outline_uv]
        holes_uv = [(u, -v, d) for (u, v, d) in holes_uv]
    plane = _plane(p, normal, a0, f"{name}_base")
    key = NORMAL[normal][1]
    with p.sketch(key, f"SK_{name}", plane_name=plane) as sk:
        sk.polygon(list(outline_uv))
        for (u, v, d) in holes_uv:
            sk.circle(u, v, d / 2)
    p.extrude(f"SK_{name}", a1 - a0, name, merge=merge)
    return name


def circle_cut(p: Part, name, normal, at, center_model, diameter, depth, into_positive=True):
    """Blind circular recess/hole starting on the plane normal=at, going +normal (into_positive) or -normal."""
    center_model = _m3(center_model)
    if normal == "y" and SIDE[0] < 0:
        at, into_positive = -at, not into_positive
    plane = _plane(p, normal, at, f"{name}_base")
    key = NORMAL[normal][1]
    with p.sketch(key, f"SK_{name}", plane_name=plane) as sk:
        u, v = uv(normal, center_model)
        sk.circle(u, v, diameter / 2)
    p.cut(f"SK_{name}", depth, name, reverse=not into_positive)
    return name


def bolt_holes(center_uv, pcd, n, d, start_deg=0.0):
    cu, cv = center_uv
    return [(cu + pcd / 2 * math.cos(math.radians(start_deg + 360 * k / n)),
             cv + pcd / 2 * math.sin(math.radians(start_deg + 360 * k / n)), d) for k in range(n)]
