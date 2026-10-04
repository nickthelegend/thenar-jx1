"""Quick look at the robot without SolidWorks: builds every part from geometry.py with manifold3d (the same primitives
and build order as build_cad.py), places them with layout.py and renders the assembly with MuJoCo.

    python jx0/cad/preview.py [--out preview.png] [--stl-dir DIR]

Masses printed here use the same PETG density and print-fill factor as build_cad.py, so they are a fast estimate of
what the SolidWorks build will report.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

import numpy as np
from manifold3d import CrossSection, FillRule, Manifold

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import geometry as G  # noqa: E402
from layout import components  # noqa: E402

PETG, FILL = 1.27, 0.55          # g/cm^3, printed / solid (as build_cad.py)
RGBA = {"sage": "0.74 0.86 0.58 1", "black": "0.1 0.1 0.11 1", "white": "0.92 0.92 0.94 1", "orange": "0.95 0.42 0.11 1"}
# extrusion of a (u, v) profile by w along each axis, as proper rotations (no mirroring): rows map (u, v, w) -> (x, y, z)
AXIS_MAP = {"z": np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], float),
            "x": np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], float),
            "y": np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], float)}


def _place(m: Manifold, axis, s0, s1):
    R = AXIS_MAP[axis]
    off = {"z": (0, 0, s0), "x": (s0, 0, 0), "y": (0, s1, 0)}[axis]
    return m.transform(np.column_stack([R, off]).tolist())


def _section(pts):
    pts = [tuple(map(float, q)) for q in pts]
    area = sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(pts, pts[1:] + pts[:1]))
    return CrossSection([pts if area > 0 else pts[::-1]], FillRule.NonZero)


def solid(prim) -> Manifold:
    k = G.base_kind(prim[0])
    if k in ("box", "cut"):
        (x0, x1), (y0, y1), (z0, z1) = prim[1], prim[2], prim[3]
        return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])
    if k in ("cyl", "hole"):
        _, axis, c, r, (s0, s1) = prim
        rad = r if k == "cyl" else r / 2
        return _place(CrossSection.circle(rad, 48).translate(list(c)).extrude(s1 - s0), axis, s0, s1)
    _, axis, pts, (s0, s1) = prim
    return _place(_section(pts).extrude(s1 - s0), axis, s0, s1)


def build(prims) -> Manifold:
    body = Manifold()
    for prim in sorted(prims, key=G.phase):
        m = solid(prim)
        body = body - m if G.base_kind(prim[0]) in G.CUTS else body + m
    return body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "images" / "preview.png"))
    ap.add_argument("--stl-dir", default=None)
    ap.add_argument("--view", default="front", choices=["front", "back", "side"])
    a = ap.parse_args()
    import mujoco
    import trimesh
    stl = Path(a.stl_dir) if a.stl_dir else Path(tempfile.mkdtemp())
    stl.mkdir(parents=True, exist_ok=True)
    catalogue = {**G.PARTS, **G.SERVOS}
    total = 0.0
    for name, (prims, colour, qty) in catalogue.items():
        mesh = build(prims).to_mesh()
        tm = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts))
        tm.export(stl / f"{name}.stl")
        g = tm.volume / 1000 * PETG * FILL
        if name in G.PARTS:
            total += g * qty
            print(f"{name:22s} x{qty}  {g:6.1f} g printed (est.)  watertight {tm.is_watertight}")
    print(f"printed parts total {total:.0f} g")
    geoms, assets = [], set()
    for key, part, M in components():
        q = np.zeros(4)
        mujoco.mju_mat2Quat(q, np.ascontiguousarray(M[:3, :3]).flatten())
        assets.add(part)
        geoms.append(f'<geom type="mesh" mesh="{part}" pos="{" ".join(map(str, M[:3, 3]))}" quat="{" ".join(map(str, q))}" '
                     f'rgba="{RGBA[catalogue[part][1]]}"/>')
    xml = f"""<mujoco><visual><global offwidth="1600" offheight="1200"/><headlight ambient=".45 .45 .45" diffuse=".5 .5 .5"/></visual>
<asset>{"".join(f'<mesh name="{p}" file="{(stl / (p + ".stl")).as_posix()}" scale=".001 .001 .001"/>' for p in assets)}</asset>
<worldbody><light pos="0.6 -0.6 1.5" dir="-0.3 0.3 -1"/><body pos="0 0 0.237">{"".join(geoms)}</body></worldbody></mujoco>"""
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    mujoco.mj_forward(m, d)
    r = mujoco.Renderer(m, 1200, 900)
    cam = mujoco.MjvCamera()
    cam.lookat[:] = [0, 0, 0.27]
    cam.distance, cam.elevation = 1.05, -8
    cam.azimuth = {"front": 150, "back": 330, "side": 90}[a.view]
    r.update_scene(d, camera=cam)
    from PIL import Image
    Image.fromarray(r.render()).save(a.out)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
