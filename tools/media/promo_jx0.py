"""'Meet JX0': a vertical (1080 x 1920) promo film, rendered from the engraved print meshes (jx0/cad/stl_engraved).

    python tools/media/promo_jx0.py            -> media/jx0_promo.mp4 (about 60 s, 30 fps; needs ffmpeg on PATH)
    python tools/media/promo_jx0.py --stills   -> a few frames only, media/jx0_promo_still_<n>.png

The robot is the real one: the robot program (jx0bot.robot.Robot, the code that runs on the Pi) drives the CAD robot in
MuJoCo with the servo model, as in jx0/sim/demo_jx0.py: it stands, walks, turns, takes a shove, waves, looks around
and nods. A studio scene (light cyclorama, soft shadows) and two-line captions; the parts flat-lay shows every printed
part the way it lies on the print bed. The engraved letters are shown filled with dark paint.
"""
from __future__ import annotations

import math
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.environ["JX0_STL_DIR"] = str(ROOT / "jx0" / "cad" / "stl_engraved")
sys.path.insert(0, str(ROOT / "jx0" / "sim"))
sys.path.insert(0, str(ROOT / "tools" / "print"))

import mujoco  # noqa: E402
import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter, ImageFont  # noqa: E402

import demo_jx0 as demo  # noqa: E402
import make_plates as mp  # noqa: E402
from jx0bot.robot import REST_ARMS, Robot, load_config  # noqa: E402

W, H, FPS = 1080, 1920, 30
STL = ROOT / "jx0" / "cad" / "stl_engraved"
OUT = ROOT / "media" / "jx0_promo.mp4"
TMP = ROOT / "media" / "jx0_promo_build"
SHELL, SERVO, PAINT = ".74 .86 .58 1", ".10 .10 .11 1", ".07 .08 .09 1"
INK, GREEN = (20, 22, 24), (46, 160, 82)
LIFT = 0.12                                 # aim this far (x the camera distance) below the subject
FONT_SANS = "C:/Windows/Fonts/segoeuib.ttf"
FONT_SERIF = "C:/Windows/Fonts/segoeuii.ttf"     # (Georgia's old-style figures turn JX0 into JXo)

STUDIO_ASSETS = f"""
    <texture name="grid" type="2d" builtin="flat" rgb1=".955 .955 .95" width="64" height="64"/>
    <material name="grid" texture="grid" reflectance=".10"/>
    <texture name="sky" type="skybox" builtin="gradient" rgb1=".99 .99 .99" rgb2=".955 .955 .95" width="64" height="512"/>
    <material name="shell" rgba="{SHELL}" specular=".35" shininess=".45"/>
    <material name="servo" rgba="{SERVO}" specular=".55" shininess=".75"/>
    <material name="paint" rgba="{PAINT}" specular=".15" shininess=".2"/>"""
STUDIO_VISUAL = ('<visual><global offwidth="1920" offheight="1920"/><quality shadowsize="8192" offsamples="8"/>'
                 '<headlight ambient=".40 .40 .42" diffuse=".30 .30 .30" specular=".05 .05 .05"/>'
                 '<map znear="0.002" zfar="30" haze=".6"/></visual>')
STUDIO_LIGHTS = """
    <light name="key" directional="true" pos="0.6 -0.8 2.0" dir="-0.35 0.45 -1" diffuse=".62 .62 .60" specular=".25 .25 .25" castshadow="true"/>
    <light name="fill" directional="true" pos="-1 1 1.2" dir="0.6 -0.5 -0.5" diffuse=".22 .23 .25" specular="0 0 0" castshadow="false"/>"""


def studio(xml: str) -> str:
    """The robot model in a light studio, its parts in plastic materials and the engraved letters painted."""
    xml = xml.replace('rgba=".74 .86 .58 1"', 'material="shell"').replace('rgba=".12 .12 .14 1"', 'material="servo"')
    xml = re.sub(r"<visual>.*?</visual>", STUDIO_VISUAL, xml, count=1, flags=re.S)
    xml = re.sub(r'<texture name="grid"[^>]*/>\s*<material name="grid"[^>]*/>', STUDIO_ASSETS, xml, count=1)
    inlays = sorted(p.stem for p in (STL / "inlay").glob("*.stl"))
    xml = xml.replace("</asset>", "".join(f'\n<mesh name="i_{n}" file="{(STL / "inlay" / f"{n}.stl").as_posix()}" '
                                          f'scale="0.001 0.001 0.001"/>' for n in inlays) + "\n  </asset>", 1)
    for n in inlays:
        xml = re.sub(rf'(<geom type="mesh" mesh="m_{n}" (pos="[^"]*" quat="[^"]*") [^>]*/>)',
                     rf'\1<geom type="mesh" mesh="i_{n}" \2 material="paint" contype="0" conaffinity="0" mass="0"/>', xml)
    return xml.replace("</worldbody>", STUDIO_LIGHTS + "\n  </worldbody>", 1)


demo.scene_xml = studio                     # StepIO builds the robot in this scene


def fonts(size_sans, size_serif):
    return ImageFont.truetype(FONT_SANS, size_sans), ImageFont.truetype(FONT_SERIF, size_serif)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


class Captions:
    """Two lines, centred in the lower third: a bold sans line in ink and an italic serif line in green, each sliding
    up and fading in, the second a little later; out with a fade."""

    def __init__(self):
        self.a, self.b, self.f0, self.small = "", "", 0, ""
        self.sans, self.serif = fonts(118, 112)
        self.tiny = ImageFont.truetype(FONT_SANS, 34)

    def set(self, a, b, frame, small=""):
        self.a, self.b, self.f0, self.small = a, b, frame, small

    def draw(self, img, frame, fade_out=1.0):
        if not (self.a or self.b):
            return img
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        y0 = int(H * 0.755)
        for i, (text, font, colour) in enumerate(((self.a, self.sans, INK), (self.b, self.serif, GREEN))):
            if not text:
                continue
            k = ease((frame - self.f0 - 5 * i) / 12.0) * fade_out
            w = d.textlength(text, font=font)
            y = y0 + i * 128 + int(40 * (1 - k))
            d.text(((W - w) / 2, y), text, font=font, fill=colour + (int(255 * k),))
        if self.small:
            k = ease((frame - self.f0 - 14) / 12.0) * fade_out
            w = d.textlength(self.small, font=self.tiny)
            d.text(((W - w) / 2, y0 + 290), self.small, font=self.tiny, fill=(90, 96, 102, int(255 * k)))
        glow = layer.filter(ImageFilter.GaussianBlur(14))                 # a soft light halo keeps them readable
        halo = Image.new("RGBA", img.size, (255, 255, 255, 0))
        halo.putalpha(glow.getchannel("A").point(lambda v: int(v * 0.55)))
        out = img.convert("RGBA")
        out.alpha_composite(halo)
        out.alpha_composite(layer)
        return out.convert("RGB")


class Badge:
    """The small mark at the top: JX0 · thenar.io."""

    def __init__(self):
        self.font = ImageFont.truetype(FONT_SANS, 36)

    def draw(self, img):
        d = ImageDraw.Draw(img)
        d.text((60, 70), "JX0", font=self.font, fill=INK)
        d.text((60 + d.textlength("JX0 ", font=self.font), 70), "· thenar.io", font=self.font, fill=(110, 116, 122))
        return img


class Film:
    def __init__(self, sink):
        self.sink, self.frame_no, self.last = sink, 0, None
        self.fade_from, self.fade_n = None, 0
        self.caps, self.badge = Captions(), Badge()
        self.cap_out = None

    def cut(self, n=8):
        self.fade_from, self.fade_n = self.last, n

    def emit(self, img):
        img = self.caps.draw(img, self.frame_no, 1.0 if self.cap_out is None else
                             max(0.0, 1.0 - (self.frame_no - self.cap_out) / 8.0))
        img = self.badge.draw(img)
        if self.fade_from is not None and self.fade_n > 0:
            k = self.fade_n / 9.0
            img = Image.blend(img, self.fade_from, k)
            self.fade_n -= 1
        self.last = img
        self.sink(img)
        self.frame_no += 1


class PromoIO(demo.StepIO):
    """The demo's stepping IO with a director's camera in place of the follow camera."""

    def __init__(self, cfg, film):
        super().__init__(cfg, sink=None, scene=True)
        self.renderer.close()
        self.renderer = mujoco.Renderer(self.m, H, W)
        self.film = film
        self.shot = None
        self.t_shot = 0.0
        self.pelvis = mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_BODY, "pelvis")
        self.cam.type = mujoco.mjtCamera.mjCAMERA_FREE

    def set_shot(self, az, el, dist, look=(0.0, 0.0, 0.0), orbit=0.0, follow=0.08, cut=True, lift=LIFT):
        """az / el in degrees, dist in m; look = offset of the aim point from the pelvis (world frame); orbit deg/s."""
        self.shot = dict(az=az, el=el, dist=dist, look=np.asarray(look, float), orbit=orbit, follow=follow, lift=lift)
        self.t_shot = self.d.time
        if cut:
            self.cam.azimuth, self.cam.elevation, self.cam.distance = az, el, dist
            self.lookat = self.d.xpos[self.pelvis] + self.shot["look"] - [0.0, 0.0, lift * dist]
            self.film.cut()

    def frame(self):
        s = self.shot
        target = self.d.xpos[self.pelvis] + s["look"]
        target[2] -= s["lift"] * self.cam.distance                 # the robot in the upper part of the frame, the captions below
        self.lookat = target.copy() if self.lookat is None else self.lookat + s["follow"] * (target - self.lookat)
        self.cam.lookat[:] = self.lookat
        az = s["az"] + s["orbit"] * (self.d.time - self.t_shot)
        self.cam.azimuth += 0.08 * (az - self.cam.azimuth)
        self.cam.elevation += 0.08 * (s["el"] - self.cam.elevation)
        self.cam.distance += 0.08 * (s["dist"] - self.cam.distance)
        self.renderer.update_scene(self.d, camera=self.cam)
        self.film.emit(Image.fromarray(self.renderer.render()))
        self.n_frames += 1


# ------------------------------------------------------------------------------------------------ the parts flat-lay
def flatlay_model():
    """Every printed part lying the way it prints (make_plates orientation), in rows on the studio floor, and the 17
    servos in a row in front of them."""
    TMP.mkdir(parents=True, exist_ok=True)
    items = []
    for _, (_, _, parts) in mp.PLATES.items():
        for part, n in parts:
            items += [part] * (min(n, 6) if part == "JX0_HornShim" else n)
    meshes = []
    for part in items:
        m = trimesh.load(STL / f"{part}.stl")
        R = trimesh.geometry.align_vectors(np.asarray(mp.DOWN[part], float), [0.0, 0.0, -1.0])
        m.apply_transform(R)
        lo = m.bounds[0].copy()
        m.apply_translation(-lo)
        inlay = None
        if (STL / "inlay" / f"{part}.stl").exists():
            inlay = trimesh.load(STL / "inlay" / f"{part}.stl")
            inlay.apply_transform(R)
            inlay.apply_translation(-lo)
        meshes.append((part, m, inlay))
    # rows by size, largest first, centred
    meshes.sort(key=lambda t: -t[1].extents[0] * t[1].extents[1])
    rows, row, x, gap, width = [], [], 0.0, 22.0, 520.0
    for t in meshes:
        w = t[1].extents[0]
        if row and x + w > width:
            rows.append(row)
            row, x = [], 0.0
        row.append(t)
        x += w + gap
    rows.append(row)
    assets, geoms, y = [], [], 0.0
    for r_i, row in enumerate(rows):
        depth = max(t[1].extents[1] for t in row)
        total = sum(t[1].extents[0] for t in row) + gap * (len(row) - 1)
        x = -total / 2
        for k, (part, m, inlay) in enumerate(row):
            name = f"p{r_i}_{k}"
            f = TMP / f"{name}.stl"
            m.export(f)
            assets.append(f'<mesh name="{name}" file="{f.as_posix()}" scale="0.001 0.001 0.001"/>')
            pos = f"{x / 1000:.4f} {-(y + (depth - m.extents[1]) / 2) / 1000 - m.extents[1] / 1000:.4f} 0"
            geoms.append(f'<geom type="mesh" mesh="{name}" pos="{pos}" material="shell"/>')
            if inlay is not None:
                fi = TMP / f"{name}_i.stl"
                inlay.export(fi)
                assets.append(f'<mesh name="{name}_i" file="{fi.as_posix()}" scale="0.001 0.001 0.001"/>')
                geoms.append(f'<geom type="mesh" mesh="{name}_i" pos="{pos}" material="paint"/>')
            x += m.extents[0] + gap
        y += depth + gap
    # the servos: on their side, in a row in front (+y) of the parts
    s = trimesh.load(STL / "JX0_Servo_STS3215.stl")
    s.apply_translation(-s.bounds[0])
    fs = TMP / "servo.stl"
    s.export(fs)
    assets.append(f'<mesh name="servo" file="{fs.as_posix()}" scale="0.001 0.001 0.001"/>')
    sw = s.extents[0] + 8.0
    for i in range(17):
        cols = 9 if i < 9 else 8
        k = i if i < 9 else i - 9
        xx = (k - (cols - 1) / 2) * sw - s.extents[0] / 2
        yy = 40.0 + (0 if i < 9 else s.extents[1] + 10.0)
        geoms.append(f'<geom type="mesh" mesh="servo" pos="{xx / 1000:.4f} {yy / 1000:.4f} 0" material="servo"/>')
    xml = f"""<mujoco model="flatlay">
  {STUDIO_VISUAL}
  <asset>{STUDIO_ASSETS}
    {chr(10).join(assets)}
  </asset>
  <worldbody>
    <geom name="floor" type="plane" size="3 3 0.05" material="grid"/>
    {chr(10).join(geoms)}
    {STUDIO_LIGHTS}
  </worldbody>
</mujoco>"""
    model = mujoco.MjModel.from_xml_string(xml)
    return model, -y / 1000                            # y extent of the parts (the servos are at +y)


def flatlay(film, seconds_parts, seconds_servos):
    m, y_far = flatlay_model()
    d = mujoco.MjData(m)
    mujoco.mj_forward(m, d)
    r = mujoco.Renderer(m, H, W)
    cam = mujoco.MjvCamera()
    film.cut()
    film.caps.set("25 printed parts", "two desktop printers", film.frame_no, "PETG legs · PLA body · 0.6 mm engraving")
    n1 = int(seconds_parts * FPS)
    for i in range(n1):
        k = i / max(n1 - 1, 1)
        cam.lookat[:] = (0.0, y_far / 2 + 0.02 * k, 0.0)
        cam.azimuth, cam.elevation = 90.0 + 12.0 * (k - 0.5), -62.0 + 6.0 * k
        cam.distance = 0.95 - 0.12 * k
        r.update_scene(d, camera=cam)
        film.emit(Image.fromarray(r.render()))
    film.cut()
    film.caps.set("17 STS3215", "smart servos", film.frame_no, "12 in the legs · 4 in the arms · 1 in the neck")
    n2 = int(seconds_servos * FPS)
    for i in range(n2):
        k = i / max(n2 - 1, 1)
        cam.lookat[:] = (0.0, 0.065, 0.01)
        cam.azimuth, cam.elevation, cam.distance = 70.0 + 30.0 * k, -32.0, 0.62 - 0.08 * k
        r.update_scene(d, camera=cam)
        film.emit(Image.fromarray(r.render()))
    r.close()


# ------------------------------------------------------------------------------------------------ the film
def main():
    stills = "--stills" in sys.argv
    OUT.parent.mkdir(exist_ok=True)
    frames_kept = []
    ff = None
    if not stills:
        ff = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "19", "-preset", "slow",
                               "-pix_fmt", "yuv420p", "-g", str(FPS), "-movflags", "+faststart", str(OUT)], stdin=subprocess.PIPE)

    def sink(img):
        if ff:
            ff.stdin.write(img.tobytes())
        if film.frame_no % 45 == 20:
            frames_kept.append(img)

    film = Film(sink)
    cfg = load_config()
    io = PromoIO(cfg, film)
    robot = Robot(io, cfg)
    io.settle({**robot.stand_pose, **REST_ARMS})
    io.next_frame = io.d.time
    caps = film.caps

    def shot(a, b, small, **cam):
        io.set_shot(**cam)
        caps.set(a, b, film.frame_no, small)
        film.cap_out = None

    def end_caption(frames_before_end=8):
        film.cap_out = film.frame_no

    # 1. hero: low orbit
    io.set_shot(az=215.0, el=-4.0, dist=1.15, look=(0.0, 0.0, 0.08), orbit=-9.0)
    caps.set("Meet", "JX0", film.frame_no, "JNTUH's 1st Humanoid Robot")
    robot.stand(1.0)
    io.sleep(3.8)
    if stills:
        frames_kept.append(film.last)
    # 2. the engraving, close
    shot("JNTUH's first", "humanoid robot", "made by students · thenar.io", az=180.0, el=-2.0, dist=0.42,
         look=(0.04, 0.0, 0.10), orbit=4.0, lift=0.20)
    io.sleep(3.6)
    if stills:
        frames_kept.append(film.last)
        film.last.save(ROOT / "media" / "jx0_promo_still_engraving.png")
    # 3-4. the parts and the servos
    flatlay(film, 4.5 if not stills else 0.6, 3.8 if not stills else 0.6)
    if stills:
        frames_kept.append(film.last)
    # 5. walking, side tracking
    shot("It walks", "on its own legs", "14 gaits, verified closed-loop in simulation", az=95.0, el=-6.0, dist=1.15,
         look=(0.05, 0.0, 0.08), follow=0.06)
    robot.busy.acquire()
    try:
        robot.play("forward_4")
        # 6. the legs, close
        shot("Double-sided", "leg joints", "every leg servo held from both faces", az=135.0, el=-8.0, dist=0.55,
             look=(0.02, 0.0, -0.06), follow=0.08, lift=0.16)
        robot.play("forward_4")
        if stills:
            frames_kept.append(film.last)
    finally:
        robot.busy.release()
    # 7. turn
    shot("Turns", "on the spot", "", az=160.0, el=-10.0, dist=1.12, look=(0.0, 0.0, 0.08), orbit=-6.0)
    robot.turn(-30)
    # 8. the shove
    shot("Push it", "it stays up", "a 0.96 N·s shove mid-walk: 48 of 48 stay up", az=110.0, el=-8.0, dist=1.2,
         look=(0.05, 0.0, 0.08), follow=0.06)
    robot.busy.acquire()
    try:
        robot.play("forward_2")
        io.push(demo.PUSH_N, demo.PUSH_S)
        robot.play("forward_4")
    finally:
        robot.busy.release()
    if stills:
        frames_kept.append(film.last)
    # 9. wave
    shot("Says", "hello", "", az=200.0, el=-4.0, dist=1.0, look=(0.0, 0.0, 0.13), orbit=-5.0)
    robot.wave("right")
    if stills:
        frames_kept.append(film.last)
    # 10. look around, nod
    shot("A Raspberry Pi", "brain", "listens, talks, plans its steps", az=175.0, el=-3.0, dist=0.62,
         look=(0.0, 0.0, 0.22), orbit=3.0, lift=0.10)
    robot.look("left")
    io.sleep(0.4)
    robot.look("right")
    io.sleep(0.4)
    robot.look("center")
    robot.nod("yes")
    # 11. end card
    shot("JX0", "thenar.io", "JNTUH's 1st Humanoid Robot", az=205.0, el=-6.0, dist=1.15, look=(0.0, 0.0, 0.08),
         orbit=-7.0)
    io.sleep(4.5)
    end_caption()
    io.sleep(0.3)
    if stills:
        for i, im in enumerate(frames_kept[-8:]):
            im.save(ROOT / "media" / f"jx0_promo_still_{i}.png")
        print(f"{len(frames_kept)} stills; max tilt {io.max_tilt:.1f} deg")
        return
    ff.stdin.close()
    ff.wait()
    print(f"{OUT.relative_to(ROOT)}: {film.frame_no} frames ({film.frame_no / FPS:.1f} s), max robot tilt {io.max_tilt:.1f} deg")


if __name__ == "__main__":
    main()
