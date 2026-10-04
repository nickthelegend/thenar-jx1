"""JX0 demo film from the simulation, staged like the reference video (media/reference.mp4): the robot walks on a
wooden floor with its arms swinging, waves, gets shoved from the side while walking and keeps going, and bumps a
plastic bottle out of its way. The real robot program (jx0bot.robot.Robot, the same code that runs on the Pi) drives the
CAD robot in MuJoCo frame by frame; the push and the bottle are plain physics.

    python jx0/sim/demo_jx0.py      -> jx0/results/images/jx0_demo.mp4 and jx0_demo.webp (preview); needs ffmpeg on PATH
"""
from __future__ import annotations

import math
import re
import subprocess
import sys
from pathlib import Path

import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "jx0" / "software"))
from jx0_model import build  # noqa: E402  (also puts calculations/ on the path)
from walk_jx0 import ServoModel  # noqa: E402
from jx1calc.design import Design  # noqa: E402
from jx0bot.robot import ARM_JOINTS, LEG_JOINTS, REST_ARMS, Robot, load_config  # noqa: E402

OUT = ROOT / "jx0" / "results" / "images"
ASSETS = HERE / "assets"
W, H, FPS = 1280, 720, 30
STILLS = {"wave": 3.4, "walk": 9.0, "kick": 16.6}   # clean frames (no caption) saved as jx0_demo_<name>.png
BOTTLE_AT = (0.24, -0.045)                           # in the right leg's path, about 7 steps ahead
PUSH_N, PUSH_S = 8.0, 0.12                          # sideways shove on the torso: 8 N for 0.12 s (0.96 N·s: it stays up in
                                                    # all 48 timings of such a shove mid-walk, verification.md)


def wood_texture(path: Path, size=1024, seed=3):
    """Oak-plank floor like the room in the reference video (procedural, so nothing is downloaded)."""
    rng = np.random.default_rng(seed)
    img = Image.new("RGB", (size, size))
    d = ImageDraw.Draw(img)
    y = 0
    while y < size:
        h = int(rng.integers(70, 110))
        x = -int(rng.integers(0, 400))
        while x < size:
            L = int(rng.integers(300, 600))
            base = np.array([178, 156, 128]) + rng.integers(-14, 14, 3)
            d.rectangle([x, y, x + L, y + h], fill=tuple(int(v) for v in base))
            for _ in range(10):                                         # grain
                gy = y + int(rng.integers(0, h))
                c = tuple(int(v) for v in base - rng.integers(10, 30))
                d.line([(x, gy), (x + L, gy + int(rng.integers(-4, 4)))], fill=c, width=1)
            d.line([(x, y), (x, y + h)], fill=(95, 70, 45), width=2)     # plank ends
            x += L
        d.line([(0, y), (size, y)], fill=(95, 70, 45), width=2)
        y += h
    img.filter(ImageFilter.GaussianBlur(0.6)).save(path)


def scene_xml(xml: str) -> str:
    """The robot model plus the room: wood floor, wall, filament box, a bottle that the shins and feet can hit."""
    ASSETS.mkdir(exist_ok=True)
    tex = ASSETS / "wood_floor.png"
    if not tex.exists():
        wood_texture(tex)
    xml = xml.replace('<texture name="grid" type="2d" builtin="checker" rgb1=".2 .22 .26" rgb2=".26 .28 .32" width="512" height="512"/>',
                      f'<texture name="grid" type="2d" file="{tex.as_posix()}"/>')
    xml = xml.replace('<material name="grid" texture="grid" texrepeat="8 8" reflectance=".15"/>',
                      '<material name="grid" texture="grid" texrepeat="3 3" reflectance=".05"/>')
    bx, by = BOTTLE_AT
    room = f"""
    <geom name="wall" type="box" size="0.02 3 0.6" pos="-0.9 0 0.6" rgba=".93 .93 .91 1"/>
    <geom name="wall2" type="box" size="3 0.02 0.6" pos="0 1.2 0.6" rgba=".9 .9 .88 1"/>
    <geom name="skirting" type="box" size="0.025 3 0.03" pos="-0.88 0 0.03" rgba="1 1 1 1"/>
    <geom name="skirting2" type="box" size="3 0.025 0.03" pos="0 1.18 0.03" rgba="1 1 1 1"/>
    <body name="filament_box" pos="0.15 0.42 0.105"><freejoint/>
      <geom type="box" size="0.105 0.04 0.105" rgba=".97 .97 .97 1" mass="0.35" contype="1" conaffinity="3"/>
      <geom type="cylinder" size="0.04 0.0005" pos="0 -0.0405 0.01" euler="90 0 0" rgba=".25 .45 .25 1" contype="0" conaffinity="0"/></body>
    <body name="bottle" pos="{bx} {by} 0.0855"><freejoint/>
      <geom type="cylinder" size="0.033 0.085" rgba=".55 .9 .45 .55" mass="0.04" friction="0.6 0.01 0.001" contype="1" conaffinity="3"/>
      <geom type="cylinder" size="0.034 0.03" pos="0 0 -0.02" rgba=".2 .55 .25 .9" mass="0" contype="0" conaffinity="0"/>
      <geom type="cylinder" size="0.014 0.012" pos="0 0 0.097" rgba=".55 .9 .45 .55" mass="0" contype="1" conaffinity="3"/>
      <geom type="cylinder" size="0.0145 0.007" pos="0 0 0.112" rgba=".98 .85 .1 1" mass="0.002" contype="1" conaffinity="3"/></body>
    <light pos="0.4 0.4 1.6" dir="0 -0.3 -1" diffuse=".35 .35 .33"/>"""
    xml = xml.replace("</worldbody>", room + "\n  </worldbody>", 1)        # after the robot: its freejoint stays qpos[0:7]
    # shins and feet can hit the bottle and the box (contype 2), nothing else on the robot collides with them
    shin = float(re.search(r'<body name="l_ankle_cross" pos="0 0 (-[0-9.]+)"', xml).group(1))
    for s in "lr":
        head = re.search(rf'<body name="{s}_shin" pos="[^"]*">', xml).group(0)
        xml = xml.replace(head, head + f'\n<geom type="capsule" fromto="0 0 -0.01 0 0 {shin + 0.008:.3f}" size="0.022" '
                          f'contype="2" conaffinity="0" rgba="0 0 0 0" mass="0"/>', 1)
    return xml


class StepIO:
    """SimIO's interface, but the physics only advances while the robot program waits (tick / sleep): deterministic,
    faster than real time, and every 1/FPS s of robot time becomes one film frame."""

    def __init__(self, cfg, sink, scene=True):
        design = Design(ROOT / "jx0" / "design_point.yaml")
        xml = build(design)
        self.m = mujoco.MjModel.from_xml_string(scene_xml(xml) if scene else xml)
        self.d = mujoco.MjData(self.m)
        st, b = design.act_classes["ST"], cfg["bus"]
        self.servo = ServoModel(st["stall_torque_nm"], st["no_load_speed_rad_s"], b["stiffness_nm_per_rad"], b["damping_nm_s_per_rad"])
        jid = lambda n: mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_JOINT, n)  # noqa: E731
        self.adr = {n: (self.m.jnt_qposadr[jid(n)], self.m.jnt_dofadr[jid(n)]) for n in LEG_JOINTS + ARM_JOINTS}
        self.act = {n: mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_ACTUATOR, n) for n in self.adr}
        self.goal = {n: 0.0 for n in self.adr}
        self.torso = mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_BODY, "torso")
        self.renderer = mujoco.Renderer(self.m, H, W)
        self.cam = mujoco.MjvCamera()
        self.cam.azimuth, self.cam.elevation, self.cam.distance = 150.0, -12.0, 1.05
        self.lookat, self.caption, self.cam_goal = None, "", (150.0, -12.0, 1.05)
        self.sink, self.next_frame, self.n_frames = sink, 0.0, 0
        self.push_until, self.push_n = -1.0, 0.0
        self.max_tilt = 0.0                               # deg, over the whole film
        try:
            self.font = ImageFont.truetype("arial.ttf", 38)
        except OSError:
            self.font = ImageFont.load_default()

    # ---- the SimIO interface the Robot uses
    def settle(self, q0):
        for n, v in q0.items():
            self.d.qpos[self.adr[n][0]] = v
            self.goal[n] = v
        mujoco.mj_forward(self.m, self.d)
        sole = min(self.d.site_xpos[mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_SITE, s)][2] for s in ("l_sole", "r_sole"))
        self.d.qpos[2] -= sole - 0.001
        mujoco.mj_forward(self.m, self.d)

    def send(self, q):
        self.goal.update(q)

    def read_pose(self):
        return {n: float(self.d.qpos[qa]) for n, (qa, _) in self.adr.items()}

    def attitude(self):
        w, x, y, z = self.d.qpos[3:7]
        roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
        pitch = math.asin(max(-1.0, min(1.0, 2 * (w * y - z * x))))
        yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
        return roll, pitch, yaw, self.d.qvel[3:6].copy()

    def tick(self, dt):
        self.advance(dt)

    def sleep(self, seconds):
        self.advance(seconds)

    def torque(self, on):
        pass

    def close(self):
        pass

    def push(self, newtons, seconds):
        """A sideways shove on the torso (+ = toward the robot's left), like the hand in the reference video."""
        self.push_until, self.push_n = self.d.time + seconds, newtons

    # ---- physics + film
    def advance(self, seconds):
        for _ in range(int(round(seconds / self.m.opt.timestep))):
            for n, g in self.goal.items():
                qa, da = self.adr[n]
                self.d.ctrl[self.act[n]] = self.servo.torque(g, self.d.qpos[qa], self.d.qvel[da])
            self.d.xfrc_applied[self.torso, :] = 0.0
            if self.d.time < self.push_until:
                yaw = self.attitude()[2]
                self.d.xfrc_applied[self.torso, :2] = self.push_n * np.array([-math.sin(yaw), math.cos(yaw)])
            mujoco.mj_step(self.m, self.d)
            r, p, _, _ = self.attitude()
            self.max_tilt = max(self.max_tilt, math.degrees(max(abs(r), abs(p))))
            if self.d.time >= self.next_frame:
                self.frame()
                self.next_frame += 1.0 / FPS

    def frame(self):
        target = self.d.xpos[mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_BODY, "pelvis")] + [0.02, 0, 0.0]
        self.lookat = target.copy() if self.lookat is None else self.lookat + 0.05 * (target - self.lookat)
        self.cam.lookat[:] = self.lookat
        az, el, dist = self.cam_goal
        self.cam.azimuth += 0.04 * (az - self.cam.azimuth)
        self.cam.elevation += 0.04 * (el - self.cam.elevation)
        self.cam.distance += 0.04 * (dist - self.cam.distance)
        self.renderer.update_scene(self.d, camera=self.cam)
        img = Image.fromarray(self.renderer.render())
        for name, t in STILLS.items():
            if abs(self.d.time - t) <= 0.5 / FPS:
                img.save(OUT / f"jx0_demo_{name}.png")
        if self.caption:
            dr = ImageDraw.Draw(img)
            tw = dr.textlength(self.caption, font=self.font)
            dr.rounded_rectangle([40, H - 100, 40 + tw + 40, H - 40], radius=14, fill=(20, 26, 18))
            dr.text((60, H - 94), self.caption, font=self.font, fill=(196, 230, 150))
        if self.d.time < self.push_until + 0.3:                       # the push, drawn as an arrow at the torso
            dr = ImageDraw.Draw(img)
            dr.text((W - 330, 60), "push ->", font=self.font, fill=(255, 120, 60))
        self.sink(img)
        self.n_frames += 1


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    test = "--test" in sys.argv                      # physics only, no film
    mp4 = OUT / "jx0_demo.mp4"
    ff = None if test else subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "20", "-preset", "slow",
                           "-pix_fmt", "yuv420p", "-g", str(FPS), "-movflags", "+faststart", str(mp4)], stdin=subprocess.PIPE)
    preview = []

    def sink(img):
        ff.stdin.write(img.tobytes())
        if io.n_frames % 3 == 0:
            preview.append(img.resize((640, 360), Image.LANCZOS))

    cfg = load_config()
    io = StepIO(cfg, sink)
    robot = Robot(io, cfg)
    io.settle({**robot.stand_pose, **REST_ARMS})
    bottle = mujoco.mj_name2id(io.m, mujoco.mjtObj.mjOBJ_BODY, "bottle")
    if test:
        x0, hit = float(io.d.xpos[bottle][0]), []

        def track():
            if not hit and io.d.xpos[bottle][0] > x0 + 0.002:
                hit.append(io.d.time)
                print(f"    the bottle starts moving at t = {io.d.time:.2f} s", flush=True)
        io.frame = track

    def bottle_tilt():
        w, x, y, z = io.d.xquat[bottle]
        return math.degrees(math.acos(max(-1.0, min(1.0, 1 - 2 * (x * x + y * y)))))

    def scene(caption, action, cam=None):
        io.caption = caption
        if cam:
            io.cam_goal = cam
        out = action()
        print(f"{caption:42s} -> {out}  (t = {io.d.time:.1f} s, robot x {io.d.qpos[0]:+.2f} y {io.d.qpos[1]:+.2f}, "
              f"tilt {math.degrees(max(map(abs, io.attitude()[:2]))):.1f} deg, bottle tilt {bottle_tilt():.0f} deg)", flush=True)

    def walk_with_push():
        robot.busy.acquire()
        try:
            robot.play("forward_4")
            io.push(PUSH_N, PUSH_S)
            robot.play("forward_4")
        finally:
            robot.busy.release()
        return "walked 8 steps, pushed half way"

    scene("JX0: every joint an STS3215", lambda: (robot.stand(1.0), io.sleep(0.8))[0])
    scene("wave", lambda: robot.wave("right"), cam=(165.0, -8.0, 0.95))
    scene("walk, arms swinging ... push!", walk_with_push, cam=(125.0, -14.0, 1.15))
    scene("keep walking ... oops, the bottle", lambda: robot.walk(4, "forward"), cam=(115.0, -16.0, 1.15))
    scene("turn", lambda: robot.turn(-30), cam=(160.0, -10.0, 1.05))
    scene("look around", lambda: (robot.look("left"), io.sleep(0.4), robot.look("right"), io.sleep(0.4), robot.look("center"))[-1])
    scene("nod yes", lambda: robot.nod("yes"))
    scene("", lambda: io.sleep(1.0))
    if test:
        print(f"max robot tilt {io.max_tilt:.1f} deg, bottle tilt {bottle_tilt():.0f} deg")
        return
    ff.stdin.close()
    ff.wait()
    webp = OUT / "jx0_demo.webp"
    preview[0].save(webp, save_all=True, append_images=preview[1:], duration=int(3000 / FPS), loop=0, quality=65, method=6)
    print(f"{mp4.relative_to(ROOT)}: {io.n_frames} frames ({io.n_frames / FPS:.1f} s); preview {webp.relative_to(ROOT)} "
          f"({webp.stat().st_size / 1e6:.1f} MB); max robot tilt over the film {io.max_tilt:.1f} deg; "
          f"bottle tilt {bottle_tilt():.0f} deg")


if __name__ == "__main__":
    main()
