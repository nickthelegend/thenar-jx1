"""Studio stills of the current JX0 (engraved print meshes, letters painted), standing in its walking stance:

    python tools/media/stills_jx0.py            -> media/jx0_stills.png (front 3/4, front, side, back) + one PNG each
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "media"))
import promo_jx0 as P  # noqa: E402  (sets JX0_STL_DIR to the engraved meshes, the studio scene)

import mujoco  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

VIEWS = [("front 3/4", 205.0, -8.0), ("front", 180.0, -4.0), ("side", 90.0, -4.0), ("back", 0.0, -6.0)]
W, H = 900, 1200


def main():
    from jx0bot.robot import REST_ARMS, Robot, load_config
    cfg = load_config()
    film = P.Film(lambda img: None)
    io = P.PromoIO(cfg, film)
    robot = Robot(io, cfg)
    io.settle({**robot.stand_pose, **REST_ARMS})
    mujoco.mj_forward(io.m, io.d)
    r = mujoco.Renderer(io.m, H, W)
    cam = mujoco.MjvCamera()
    pel = io.d.xpos[io.pelvis].copy()
    font = ImageFont.truetype(P.FONT_SANS, 34)
    shots = []
    for name, az, el in VIEWS:
        cam.lookat[:] = pel + [0.0, 0.0, 0.07]
        cam.azimuth, cam.elevation, cam.distance = az, el, 0.95
        r.update_scene(io.d, camera=cam)
        img = Image.fromarray(r.render())
        ImageDraw.Draw(img).text((30, 24), f"JX0 · {name}", font=font, fill=(25, 28, 30))
        img.save(ROOT / "media" / f"jx0_still_{name.replace(' ', '_').replace('/', '-')}.png")
        shots.append(img)
    sheet = Image.new("RGB", (W * len(shots), H), "white")
    for i, im in enumerate(shots):
        sheet.paste(im, (W * i, 0))
    sheet.save(ROOT / "media" / "jx0_stills.png")
    print("media/jx0_stills.png")


if __name__ == "__main__":
    main()
