"""Premium studio renders of JX0: light-grey matte shell (PLA body, head, arms), graphite legs (PETG), black servos,
the red neon ring glowing round the face, lettering tone on tone, on a dark studio floor.

    python tools/media/hero_jx0.py         -> media/jx0_hero.png (4 views) + media/jx0_hero_<view>.png
"""
from __future__ import annotations

import math
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STL = ROOT / "jx0" / "cad" / "stl_engraved"
os.environ["JX0_STL_DIR"] = str(STL)
sys.path.insert(0, str(ROOT / "jx0" / "sim"))
sys.path.insert(0, str(ROOT / "jx0" / "cad"))
sys.path.insert(0, str(ROOT / "jx0" / "software"))
sys.path.insert(0, str(ROOT / "calculations"))

import mujoco  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from manifold3d import Manifold  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import geometry as G  # noqa: E402
from jx0_model import build  # noqa: E402
from jx1calc.design import Design  # noqa: E402

OUT = ROOT / "media"
TMP = ROOT / "media" / "jx0_promo_build"
SHELL, GRAPHITE, SERVO, NEON = ".86 .87 .88 1", ".17 .18 .20 1", ".07 .07 .08 1", "1 .015 .01 1"
LEGS = ("Pelvis", "YawKeeper", "YawRing", "HipYawBracket", "HipRollBracket", "Thigh", "Shin", "AnkleBracket", "Foot")
W, H = 1000, 1300
FONT = "C:/Windows/Fonts/segoeuil.ttf"


def neon_mesh() -> Path:
    """The neon strip in its channel, head frame (mm): the ring, NEON_DEPTH deep, its face flush with the head's."""
    from preview import solid
    hx = 33.0
    w, cz, h, r = G.NEON
    e = G.NEON_WIDTH / 2 - 0.2
    ring = solid(("prism", "x", G.neon_rect(w / 2 + e, h / 2 + e, r + e, cz), (hx - G.NEON_DEPTH + 0.2, hx - 0.05))) - \
        solid(("prism", "x", G.neon_rect(w / 2 - e, h / 2 - e, r - e, cz), (hx - G.NEON_DEPTH, hx + 0.1)))
    mm = ring.to_mesh()
    TMP.mkdir(parents=True, exist_ok=True)
    f = TMP / "neon.stl"
    trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts)).export(f)
    return f


def fine_head() -> Path:
    """The head rebuilt from geometry.py with fine arcs (96 segments): the exported STL's coarse fillets show as facets
    in close-ups. Same frame as the STL (the head carries no lettering)."""
    import preview
    coarse = preview._section
    preview._section = lambda path: preview.CrossSection([q if _ccw(q) else q[::-1] for q in
                                                          [[tuple(map(float, v)) for v in G.path_points(path, 96)]]],
                                                         preview.FillRule.NonZero)
    try:
        mm = preview.build(G.head()).to_mesh()
    finally:
        preview._section = coarse
    TMP.mkdir(parents=True, exist_ok=True)
    f = TMP / "head_fine.stl"
    trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts)).export(f)
    return f


def _ccw(q):
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(q, q[1:] + q[:1])) > 0


def bloom(img: Image.Image) -> Image.Image:
    """Neon glow: the strip's bright red pixels, blurred at two sizes and added back (screen) - a lit diffuser bleeds
    light round itself; the render alone paints it flat."""
    from PIL import ImageFilter
    a = np.asarray(img).astype(np.float32) / 255
    mask = ((a[..., 0] > 0.75) & (a[..., 1] < 0.45) & (a[..., 2] < 0.45)).astype(np.float32)
    k = np.zeros(a.shape[:2], np.float32)
    for radius, gain in ((W / 300, 0.75), (W / 70, 0.5)):
        k += gain * np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius))) / 255
    k = np.clip(k, 0, 0.85)[..., None] * (1 - mask[..., None])     # the light it throws: tints the shell, lights the dark
    lum = a.mean(axis=2, keepdims=True)
    lit = np.concatenate([np.maximum(lum * 1.1, 0.95), lum * 0.3, lum * 0.25], axis=2)   # red light on it
    out = a * (1 - k) + lit * k
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


def visor_mesh() -> Path:
    """The face inside the ring, painted gloss black like a visor (a thin skin on the flat face, for the renders)."""
    from preview import solid
    hx = 33.0
    w, cz, h, r = G.NEON
    e = G.NEON_WIDTH / 2
    face = solid(("prism", "x", G.neon_rect(w / 2 - e, h / 2 - e, r - e, cz), (hx - 0.05, hx + 0.08)))
    for yc, zc in ((0.0, cz + 7.0), (7.0, cz), (-7.0, cz), (0.0, cz - 7.0)):
        face = face - solid(("cyl", "x", (yc, zc), 2.5, (hx - 1.0, hx + 1.0)))
    mm = face.to_mesh()
    f = TMP / "visor.stl"
    trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts)).export(f)
    return f


def scene() -> str:
    xml = build(Design(ROOT / "jx0" / "design_point.yaml"))
    xml = re.sub(r"<visual>.*?</visual>", '<visual><global offwidth="1920" offheight="1920"/><quality shadowsize="8192" '
                 'offsamples="16"/><headlight ambient=".18 .18 .2" diffuse=".25 .25 .27" specular=".05 .05 .05"/>'
                 '<map znear="0.002" zfar="30" haze=".4"/></visual>', xml, count=1, flags=re.S)
    assets = f'''<texture name="grid" type="2d" builtin="flat" rgb1=".11 .115 .125" width="64" height="64"/>
    <material name="grid" texture="grid" reflectance=".28"/>
    <texture name="sky" type="skybox" builtin="gradient" rgb1=".16 .17 .19" rgb2=".03 .03 .035" width="64" height="512"/>
    <material name="shell" rgba="{SHELL}" specular=".18" shininess=".25"/>
    <material name="graphite" rgba="{GRAPHITE}" specular=".35" shininess=".5"/>
    <material name="servo" rgba="{SERVO}" specular=".5" shininess=".7"/>
    <material name="neon" rgba="{NEON}" emission="3"/>
    <material name="visor" rgba=".03 .03 .035 1" specular=".6" shininess=".9"/>'''
    xml = re.sub(r'<texture name="grid"[^>]*/>\s*<material name="grid"[^>]*/>', assets, xml, count=1)
    xml = xml.replace('rgba=".12 .12 .14 1"', 'material="servo"')

    def colour(m):
        part = m.group(1)
        mat = "graphite" if any(part.startswith(f"JX0_{k}") for k in LEGS) else "shell"
        return m.group(0).replace('rgba=".74 .86 .58 1"', f'material="{mat}"')
    xml = re.sub(r'<geom type="mesh" mesh="m_(JX0_\w+)"[^>]*/>', colour, xml)
    xml = re.sub(r'(<mesh name="m_JX0_Head" file=")[^"]*"', lambda m: m.group(1) + fine_head().as_posix() + '"', xml)
    f, v = neon_mesh(), visor_mesh()
    xml = xml.replace("</asset>", f'<mesh name="neon" file="{f.as_posix()}" scale=".001 .001 .001"/>'
                      f'<mesh name="visor" file="{v.as_posix()}" scale=".001 .001 .001"/>\n  </asset>', 1)
    xml = re.sub(r'(<geom type="mesh" mesh="m_JX0_Head" (pos="[^"]*" quat="[^"]*") [^>]*/>)',
                 r'\1<geom type="mesh" mesh="neon" \2 material="neon" contype="0" conaffinity="0" mass="0"/>'
                 r'<geom type="mesh" mesh="visor" \2 material="visor" contype="0" conaffinity="0" mass="0"/>', xml)
    lights = '''
    <light name="key" directional="true" pos="0.8 -0.6 1.6" dir="-0.5 0.35 -1" diffuse=".75 .74 .72" specular=".3 .3 .3" castshadow="true"/>
    <light name="rim" directional="true" pos="-1 0.8 0.8" dir="0.8 -0.6 -0.25" diffuse=".35 .38 .45" specular=".4 .4 .45" castshadow="false"/>
    <light name="back" directional="true" pos="-1.2 0.3 1.0" dir="1 -0.25 -0.8" diffuse=".35 .35 .36" specular=".1 .1 .1" castshadow="false"/>'''
    return xml.replace("</worldbody>", lights + "\n  </worldbody>", 1)


def main():
    from jx0bot.robot import REST_ARMS, load_config  # noqa: F401
    import json
    m = mujoco.MjModel.from_xml_string(scene())
    d = mujoco.MjData(m)
    g = json.loads((ROOT / "jx0" / "software" / "jx0bot" / "gaits" / "forward_2.json").read_text(encoding="utf-8"))
    for name, v in zip(g["joints"], g["q"][0]):
        jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, name)
        if jid >= 0:
            d.qpos[m.jnt_qposadr[jid]] = v
    mujoco.mj_forward(m, d)
    sole = min(d.site_xpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, s)][2] for s in ("l_sole", "r_sole"))
    d.qpos[2] -= sole
    mujoco.mj_forward(m, d)
    pel = d.xpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "pelvis")].copy()
    head = d.xpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "head")].copy()
    r = mujoco.Renderer(m, H, W)
    font, small = ImageFont.truetype(FONT, 44), ImageFont.truetype(FONT, 26)
    views = [("hero", pel + [0, 0, 0.07], 212.0, -7.0, 1.0), ("front", pel + [0, 0, 0.07], 180.0, -3.0, 1.0),
             ("back", pel + [0, 0, 0.07], 0.0, -4.0, 1.0), ("face", head + [0, 0, 0.03], 196.0, -4.0, 0.24)]
    shots = []
    for name, look, az, el, dist in views:
        cam = mujoco.MjvCamera()
        cam.lookat[:], cam.azimuth, cam.elevation, cam.distance = look, az, el, dist
        r.update_scene(d, camera=cam)
        img = bloom(Image.fromarray(r.render()))
        dr = ImageDraw.Draw(img)
        dr.text((44, 40), "JX0", font=font, fill=(235, 236, 238))
        dr.text((46, 96), name.upper(), font=small, fill=(150, 153, 158))
        img.save(OUT / f"jx0_hero_{name}.png")
        shots.append(img)
    sheet = Image.new("RGB", (W * len(shots), H))
    for i, im in enumerate(shots):
        sheet.paste(im, (W * i, 0))
    sheet.save(OUT / "jx0_hero.png")
    print("media/jx0_hero.png")


if __name__ == "__main__":
    main()
