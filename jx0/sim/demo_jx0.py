"""JX0 demo film from the simulation: the real robot program (jx0bot.robot.Robot, the same code that runs on the Pi)
drives the CAD robot in MuJoCo frame by frame, and the camera follows the action: wave, look, take and give with the
gripper hands, nod, walk, turn.

    python jx0/sim/demo_jx0.py      -> jx0/results/images/jx0_demo.mp4 and jx0_demo.webp (preview); needs ffmpeg on PATH
"""
from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

import mujoco
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "jx0" / "software"))
from jx0_model import SMALL_SERVO_STALL, build  # noqa: E402  (also puts calculations/ on the path)
from walk_jx0 import ServoModel  # noqa: E402
from jx1calc.design import Design  # noqa: E402
from jx0bot.robot import ARM_JOINTS, LEG_JOINTS, REST_ARMS, Robot, load_config  # noqa: E402

OUT = ROOT / "jx0" / "results" / "images"
W, H, FPS = 1280, 720, 30
STILLS = {"wave": 3.0, "take": 10.6}               # clean frames (no caption) saved as jx0_demo_<name>.png


class StepIO:
    """SimIO's interface, but the physics only advances while the robot program waits (tick / sleep): deterministic,
    faster than real time, and every 1/FPS s of robot time becomes one film frame."""

    def __init__(self, cfg, sink):
        design = Design(ROOT / "jx0" / "design_point.yaml")
        self.m = mujoco.MjModel.from_xml_string(build(design))
        self.d = mujoco.MjData(self.m)
        st, b = design.act_classes["ST"], cfg["bus"]
        self.leg = ServoModel(st["stall_torque_nm"], st["no_load_speed_rad_s"], b["stiffness_nm_per_rad"], b["damping_nm_s_per_rad"])
        self.arm = ServoModel(SMALL_SERVO_STALL, 6.0, 15.0, 0.15)
        jid = lambda n: mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_JOINT, n)  # noqa: E731
        self.adr = {n: (self.m.jnt_qposadr[jid(n)], self.m.jnt_dofadr[jid(n)]) for n in LEG_JOINTS + ARM_JOINTS}
        self.act = {n: mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_ACTUATOR, n) for n in self.adr}
        self.goal = {n: 0.0 for n in self.adr}
        self.renderer = mujoco.Renderer(self.m, H, W)
        self.cam = mujoco.MjvCamera()
        self.cam.azimuth, self.cam.elevation, self.cam.distance = 155.0, -6.0, 0.95
        self.lookat, self.focus, self.caption = None, "pelvis", ""
        self.sink, self.next_frame, self.n_frames = sink, 0.0, 0
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

    # ---- physics + film
    def advance(self, seconds):
        for _ in range(int(round(seconds / self.m.opt.timestep))):
            for n, g in self.goal.items():
                qa, da = self.adr[n]
                sv = self.leg if n in LEG_JOINTS else self.arm
                self.d.ctrl[self.act[n]] = sv.torque(g, self.d.qpos[qa], self.d.qvel[da])
            mujoco.mj_step(self.m, self.d)
            r, p, _, _ = self.attitude()
            self.max_tilt = max(self.max_tilt, math.degrees(max(abs(r), abs(p))))
            if self.d.time >= self.next_frame:
                self.frame()
                self.next_frame += 1.0 / FPS

    def frame(self):
        if self.focus == "pelvis":
            target = self.d.xpos[mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_BODY, "pelvis")] + [0, 0, 0.02]
            dist = 0.95
        else:
            target = self.d.site_xpos[mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_SITE, self.focus)].copy()
            dist = 0.5
        self.lookat = target.copy() if self.lookat is None else self.lookat + 0.06 * (target - self.lookat)
        self.cam.lookat[:] = self.lookat
        self.cam.distance += 0.06 * (dist - self.cam.distance)
        self.renderer.update_scene(self.d, camera=self.cam)
        img = Image.fromarray(self.renderer.render())
        for name, t in STILLS.items():
            if abs(self.d.time - t) <= 0.5 / FPS:
                img.save(OUT / f"jx0_demo_{name}.png")
        if self.caption:
            dr = ImageDraw.Draw(img)
            tw = dr.textlength(self.caption, font=self.font)
            dr.rounded_rectangle([40, H - 100, 40 + tw + 40, H - 40], radius=14, fill=(0, 0, 0))
            dr.text((60, H - 94), self.caption, font=self.font, fill=(120, 230, 255))
        self.sink(img)
        self.n_frames += 1


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    mp4 = OUT / "jx0_demo.mp4"
    ff = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
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

    def scene(caption, action, focus="pelvis"):
        io.caption, io.focus = caption, focus
        out = action()
        print(f"{caption:45s} -> {out}  (t = {io.d.time:.1f} s, tilt {math.degrees(max(map(abs, io.attitude()[:2]))):.1f} deg)", flush=True)

    scene("Hi, I'm JX0", lambda: (robot.stand(1.0), io.sleep(0.5))[0])       # the program's pose = the settled pose
    scene("wave", lambda: robot.wave("right"))
    scene("look around", lambda: (robot.look("left"), robot.look("right"), robot.look("center"))[-1])
    scene("take: hand out, open ... grip", lambda: robot.hand("right", "take"), focus="r_hand")
    scene("give: hand out ... let go", lambda: robot.hand("right", "give"), focus="r_hand")
    scene("open and close the left hand",
          lambda: (robot.hand("left", "open"), io.sleep(0.4), robot.hand("left", "close"), io.sleep(0.4), robot.hand("left", "open"),
                   io.sleep(0.4), robot.move_to({"l_grip": REST_ARMS["l_grip"]}, 0.4))[0], focus="l_hand")
    scene("nod yes", lambda: robot.nod("yes"))
    scene("walk 4 steps", lambda: robot.walk(4, "forward"))
    scene("turn left", lambda: robot.turn(20))
    scene("", lambda: io.sleep(1.0))
    ff.stdin.close()
    ff.wait()
    webp = OUT / "jx0_demo.webp"
    preview[0].save(webp, save_all=True, append_images=preview[1:], duration=int(3000 / FPS), loop=0, quality=65, method=6)
    print(f"{mp4.relative_to(ROOT)}: {io.n_frames} frames ({io.n_frames / FPS:.1f} s); preview {webp.relative_to(ROOT)} "
          f"({webp.stat().st_size / 1e6:.1f} MB); max tilt over the film {io.max_tilt:.1f} deg")


if __name__ == "__main__":
    main()
