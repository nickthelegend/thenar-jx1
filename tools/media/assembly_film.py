"""Animated assembly film of JX1, rendered from the CAD part meshes.

Every one of the 87 components is the exported SolidWorks part mesh (simulation/meshes/source_mm), placed with the same
link transforms as the verified URDF/MJCF (tools/sim/build_robot_description.py). The film:
  intro   : the finished robot on a turntable, then it explodes into parts
  steps   : 22 assembly steps in build order; each step's parts fly in from an exploded position, glow while they land,
            then settle to their material colour; the camera frames the area being built
  finale  : the complete robot, then it crouches and walks (replay of the MuJoCo gait simulation, walk_jx1.py nominal)
Outputs: media/assembly/footage.mp4 (+ timeline.json for the HyperFrames titles), docs/images/*.png stills,
docs/assembly/step_XX.png (one still per step for the written guide).
--hero renders only the README cover shots of the finished robot (docs/images/jx1_hero*.png, 1600x1100).
Usage: .venv/Scripts/python tools/media/assembly_film.py [--preview] [--no-walk] [--stills-only] [--hero]
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "sim"))
sys.path.insert(0, str(ROOT / "simulation" / "mujoco"))
from cad.leg_kinematics import LegCAD  # noqa: E402
from cad.upper_kinematics import UpperCAD  # noqa: E402
import build_robot_description as B  # noqa: E402
from validate_jx1 import load as load_sim  # noqa: E402

SRC = ROOT / "simulation" / "meshes" / "source_mm"
OUT = ROOT / "media" / "assembly"
IMG = ROOT / "docs" / "images"
STEPS_DIR = ROOT / "docs" / "assembly"
FPS = 30
HIP_Z = 0.62                               # pelvis origin height with straight legs (thigh 0.27 + shin 0.30 + sole 0.05)

# ------------------------------------------------------------------------------------------------ parts
LOOK = {  # rgba, specular, shininess, reflectance
    "alu": ((0.74, 0.76, 0.79, 1), 0.55, 0.75, 0.04),
    "actuator": ((0.10, 0.11, 0.12, 1), 0.35, 0.50, 0.0),
    "actuator_out": ((0.46, 0.48, 0.51, 1), 0.60, 0.80, 0.02),
    "steel": ((0.63, 0.64, 0.66, 1), 0.75, 0.90, 0.03),
    "accent": ((0.95, 0.42, 0.10, 1), 0.30, 0.40, 0.0),
    "print": ((0.15, 0.15, 0.16, 1), 0.20, 0.30, 0.0),
    "battery": ((0.13, 0.25, 0.62, 1), 0.30, 0.40, 0.0),
    "pcb": ((0.05, 0.40, 0.21, 1), 0.30, 0.40, 0.0),
    "grey": ((0.55, 0.56, 0.58, 1), 0.40, 0.50, 0.0),
    "dark": ((0.20, 0.20, 0.21, 1), 0.30, 0.40, 0.0),
    "red": ((0.85, 0.07, 0.06, 1), 0.40, 0.50, 0.0),
    "servo": ((0.07, 0.07, 0.08, 1), 0.30, 0.40, 0.0),
    "horn": ((0.86, 0.86, 0.88, 1), 0.50, 0.60, 0.0),
}
GLOW = np.array([0.18, 0.78, 1.0, 1.0])  # highlight while a part is arriving
EXPLODE_K = 1.9                            # exploded-view scale of each part's fly-in offset


def category(stem):
    if stem.startswith("JX1_ACT_"):
        return "actuator_out" if stem.endswith("Output") else "actuator"
    table = {"Servo_ST3215_Body": "servo", "Servo_ST3215_Horn": "horn", "AnkleCross": "steel", "AnkleRod": "steel",
             "Head": "accent", "Gripper": "print", "NeckBracket": "print", "BatteryPack": "battery", "JetsonNano": "pcb",
             "HubBoard": "pcb", "StereoCamera": "pcb", "DCDC5V": "grey", "PowerSwitch": "dark", "EStop": "red"}
    return next((v for k, v in table.items() if k in stem), "alu")


def components():
    """[{id, stem, link, T}] with T the component pose in its URDF link frame (as build_robot_description.build_links)."""
    out = [{"id": "Pelvis", "stem": "JX1_Pelvis", "link": "pelvis", "T": np.eye(4)}]
    for s, side, name in ((1, "L", "left"), (-1, "R", "right")):
        leg = LegCAD(s)
        W = leg.links({})
        comp = leg.component_poses({})
        for key, (part, _link, _) in leg.comps.items():
            lk = B.LINK_OF[key]
            out.append({"id": f"{side}_{key}", "stem": B.part_stem(part, s), "link": B.URDF_LINK[lk].format(s=name),
                        "T": np.linalg.inv(W[lk if lk in W else "pelvis"]) @ comp[key]})
        for rod in ("RodA", "RodB"):
            out.append({"id": f"{side}_{rod}", "stem": B.part_stem(rod, s), "link": B.URDF_LINK["shin"].format(s=name),
                        "T": np.linalg.inv(W["shin"]) @ comp[rod]})
    uc = UpperCAD()
    W = uc.links({})
    comp = uc.component_poses({})
    for key, (part, link, _) in uc.comps.items():
        if key == "Pelvis":
            continue
        frame = {"L_hand": "L_forearm", "R_hand": "R_forearm"}.get(link, link)
        out.append({"id": key, "stem": B.upper_stem(key, part), "link": B.UPPER_LINK[link], "T": np.linalg.inv(W[frame]) @ comp[key]})
    return out


# ------------------------------------------------------------------------------------------------ assembly sequence
def side_of(cid):
    return 1 if cid.startswith("L_") else (-1 if cid.startswith("R_") else 0)


DIRS = {"up": lambda s: (0, 0, 1), "down": lambda s: (0, 0, -1), "back": lambda s: (-1, 0, 0), "front": lambda s: (1, 0, 0),
        "out": lambda s: (0, s, 0), "out_down": lambda s: (0, 0.7 * s, -0.7), "out_up": lambda s: (0, 0.7 * s, 0.7),
        "back_down": lambda s: (-0.7, 0, -0.7)}
CAM = {  # lookat z, distance, elevation (deg)
    "pelvis": (0.66, 1.05, -24), "hip": (0.60, 1.15, -18), "leg": (0.42, 1.60, -12), "knee": (0.36, 1.30, -10),
    "shin": (0.24, 1.25, -8), "foot": (0.12, 1.15, -12), "waist": (0.80, 1.35, -20), "torso": (0.88, 1.60, -14),
    "shoulder": (0.98, 1.50, -14), "arm": (0.86, 1.75, -10), "head": (1.08, 1.30, -12), "full": (0.63, 2.95, -8),
    "explode": (0.80, 4.10, -7),
}
LEG2 = lambda *keys: [f"{s}_{k}" for s in ("L", "R") for k in keys]  # noqa: E731
STEPS = [
    ("Pelvis torsion box", "6061-T6 laser-cut plates · top 6 mm, walls 4 mm · FEA SF 2.90", ["Pelvis"], "up", 0.35, "pelvis"),
    ("Hip-yaw actuators", "2 × RobStride RS06 · 36 N·m peak · vertical axis", LEG2("YawH", "YawO"), "down", 0.30, "pelvis"),
    ("Hip-yaw brackets", "7075-T6, CNC from 25 mm plate · FEA SF 1.77", LEG2("HipYawBr"), "down", 0.32, "hip"),
    ("Hip-roll actuators", "2 × RobStride RS03 · 60 N·m · axis pointing forward", LEG2("RollH", "RollO"), "back", 0.32, "hip"),
    ("Hip-roll brackets", "6061-T6 8 + 10 mm plates · FEA SF 2.76", LEG2("HipRollBr"), "front", 0.30, "hip"),
    ("Hip-pitch actuators", "2 × RobStride RS04 · 120 N·m", LEG2("PitchH", "PitchO"), "out", 0.30, "hip"),
    ("Thighs", "6061-T6 10 mm plate with run-out flanges · 0.27 m", LEG2("Thigh"), "out_down", 0.36, "leg"),
    ("Knee actuators", "2 × RobStride RS04 · 120 N·m · 0–120° knee", LEG2("KneeH", "KneeO"), "front", 0.30, "knee"),
    ("Shins", "6061-T6 14 mm knee plate + web · 0.30 m", LEG2("Shin"), "down", 0.34, "leg"),
    ("Ankle motors + cranks", "4 × RobStride RS06 · 50 mm cranks · parallel ankle",
     LEG2("AnkAH", "AnkAO", "AnkBH", "AnkBO", "CrankA", "CrankB"), "back", 0.30, "shin"),
    ("Ankle cross + feet", "steel U-joint on needle bearings · 6061-T6 feet, 210 × 95 mm", LEG2("Cross", "Foot"), "down", 0.28, "foot"),
    ("Push-rods", "Ø8 steel rods + M5 rod ends · pitch −55…+30°, roll ±20°", LEG2("RodA", "RodB"), "back_down", 0.26, "foot"),
    ("Waist actuator", "RobStride RS06 · waist yaw", ["WaistH", "WaistO"], "up", 0.30, "waist"),
    ("Torso frame", "6061-T6 plates + 4 × 2020 extrusion · FEA SF 4.44", ["Torso"], "up", 0.45, "torso"),
    ("Battery + electronics", "13S2P 468 Wh · Jetson Nano · 2 × Teensy 4.1 CAN hubs · DC-DC · E-stop",
     ["BatteryPack", "JetsonNano", "HubBoard", "DCDC5V", "PowerSwitch", "EStop"], "front", 0.40, "torso"),
    ("Shoulder-pitch actuators", "2 × RobStride RS02 · 17 N·m", ["L_SPH", "L_SPO", "R_SPH", "R_SPO"], "out", 0.32, "shoulder"),
    ("Shoulder brackets + roll actuators", "6061-T6 U-brackets · 2 × RobStride RS02",
     ["L_ShPitchBr", "R_ShPitchBr", "L_SRH", "L_SRO", "R_SRH", "R_SRO"], "out", 0.34, "shoulder"),
    ("Shoulder-yaw actuators", "6061-T6 L-brackets · 2 × RobStride RS00 · 14 N·m",
     ["L_ShRollBr", "R_ShRollBr", "L_SYH", "L_SYO", "R_SYH", "R_SYO"], "out_down", 0.32, "shoulder"),
    ("Upper arms + elbows", "6061-T6 10 / 8 mm plates + gussets · 2 × RobStride RS00",
     ["L_UpperArm", "R_UpperArm", "L_ElH", "L_ElO", "R_ElH", "R_ElO"], "down", 0.32, "arm"),
    ("Forearms + grippers", "6061-T6 6 mm · PA-CF grippers", ["L_Forearm", "R_Forearm", "L_Gripper", "R_Gripper"], "down", 0.34, "arm"),
    ("Neck", "2 × Waveshare ST3215 bus servos · yaw + pitch", ["NeckYawS", "NeckYawH", "NeckBr", "NeckPitchS", "NeckPitchH"],
     "up", 0.28, "head"),
    ("Head + stereo camera", "PETG-CF shell · IMX219-83 stereo camera", ["Head", "Camera"], "up", 0.34, "head"),
]
# camera azimuth per step (MuJoCo: 180 = in front of the robot, 0 = behind, 270 = its left side)
STEP_AZ = [200, 160, 200, 330, 200, 240, 215, 190, 160, 320, 200, 330, 200, 160, 190, 230, 250, 210, 160, 200, 170, 195]
# README cover shots of the finished robot: (lookat, distance, azimuth, elevation)
HERO_SHOTS = {"jx1_hero.png": ((0.0, 0.0, 0.63), 2.75, 212, -9),
              "jx1_hero_back.png": ((0.0, 0.0, 0.63), 2.75, 328, -9)}
AZ_DRIFT = 2.0                             # deg/s slow orbit inside a step
T_INTRO, T_EXPLODE, T_STEP, T_FLY, T_FINALE, T_CROUCH, T_END = 5.0, 2.8, 3.4, 1.5, 4.0, 1.2, 1.5


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------------------------------------ scene
def scene_xml(parts, w, h, samples):
    stems = sorted({p["stem"] for p in parts})
    meshes = "\n".join(f'    <mesh name="m_{s}" file="{(SRC / (s + ".STL")).as_posix()}" scale="0.001 0.001 0.001"/>' for s in stems)
    mats, bodies = [], []
    for i, p in enumerate(parts):
        rgba, spec, shin, refl = LOOK[category(p["stem"])]
        mats.append(f'    <material name="mat{i}" rgba="{rgba[0]} {rgba[1]} {rgba[2]} 1" specular="{spec}" shininess="{shin}" reflectance="{refl}"/>')
        bodies.append(f'    <body name="c{i}" mocap="true" pos="0 0 -50"><geom type="mesh" mesh="m_{p["stem"]}" material="mat{i}" '
                      f'contype="0" conaffinity="0"/></body>')
    return f"""<mujoco model="jx1_assembly_film">
  <visual>
    <global offwidth="{w}" offheight="{h}" fovy="30"/>
    <quality shadowsize="8192" offsamples="{samples}"/>
    <headlight ambient="0.28 0.28 0.30" diffuse="0.30 0.30 0.30" specular="0.08 0.08 0.08"/>
    <map znear="0.01" zfar="40" haze="0.35" shadowclip="1.3" shadowscale="0.6"/>
    <rgba haze="0.07 0.08 0.10 1"/>
  </visual>
  <statistic center="0 0 0.62" extent="1.0"/>
  <asset>
    <texture name="sky" type="skybox" builtin="gradient" rgb1="0.17 0.20 0.26" rgb2="0.02 0.03 0.05" width="512" height="3072"/>
    <texture name="grid" type="2d" builtin="checker" rgb1="0.11 0.12 0.14" rgb2="0.13 0.14 0.16" width="512" height="512"
             mark="edge" markrgb="0.20 0.22 0.26"/>
    <material name="floor" texture="grid" texrepeat="14 14" reflectance="0.22"/>
{meshes}
{chr(10).join(mats)}
  </asset>
  <worldbody>
    <light directional="true" pos="1.5 1.2 4" dir="-0.35 -0.30 -0.89" diffuse="0.78 0.76 0.74" specular="0.35 0.35 0.35" castshadow="true"/>
    <light directional="true" pos="-2 -1.5 3" dir="0.55 0.45 -0.70" diffuse="0.22 0.25 0.32" specular="0.1 0.1 0.1" castshadow="false"/>
    <light directional="true" pos="-1 2 1.5" dir="0.3 -0.8 -0.5" diffuse="0.18 0.18 0.20" specular="0.2 0.2 0.2" castshadow="false"/>
    <geom name="floor" type="plane" size="0 0 0.05" material="floor"/>
{chr(10).join(bodies)}
  </worldbody>
</mujoco>"""


class Kinematics:
    """Link poses of the simulation model (simulation/mujoco/jx1.xml) for a given qpos."""

    def __init__(self):
        self.m = load_sim()
        self.d = mujoco.MjData(self.m)
        self.body = {mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_BODY, i): i for i in range(self.m.nbody)}

    def zero_qpos(self):
        q = np.zeros(self.m.nq)
        q[2], q[3] = HIP_Z, 1.0
        return q

    def links(self, qpos):
        self.d.qpos[:] = qpos
        mujoco.mj_kinematics(self.m, self.d)
        out = {}
        for name, i in self.body.items():
            T = np.eye(4)
            T[:3, :3] = self.d.xmat[i].reshape(3, 3)
            T[:3, 3] = self.d.xpos[i]
            out[name] = T
        return out


def walk_trajectory():
    """qpos samples (30 fps) of the MuJoCo walking simulation (simulation/mujoco/walk_jx1.py, nominal gait)."""
    import walk_jx1 as W
    rec = []
    orig = mujoco.mj_step

    def step(m, d):
        orig(m, d)
        rec.append((id(m), d.time, d.qpos.copy()))

    mujoco.mj_step = step
    try:
        W.run("nominal", stabiliser=True, render=False)
    finally:
        mujoco.mj_step = orig
    last = rec[-1][0]
    rec = [(t, q) for (mid, t, q) in rec if mid == last]
    times = np.array([t for t, _ in rec])
    out = []
    for tf in np.arange(0, times[-1], 1 / FPS):
        out.append(rec[int(np.argmin(np.abs(times - tf)))][1])
    return out


# ------------------------------------------------------------------------------------------------ film
class Film:
    def __init__(self, w, h, samples, walk=True):
        self.parts = components()
        self.idx = {p["id"]: i for i, p in enumerate(self.parts)}
        self.m = mujoco.MjModel.from_xml_string(scene_xml(self.parts, w, h, samples))
        self.d = mujoco.MjData(self.m)
        self.r = mujoco.Renderer(self.m, h, w)
        self.cam = mujoco.MjvCamera()
        self.kin = Kinematics()
        # material of part i (the floor material comes first, so ids are looked up by name)
        self.mat = [mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_MATERIAL, f"mat{i}") for i in range(len(self.parts))]
        self.base_rgba = self.m.mat_rgba.copy()
        self.zero_links = self.kin.links(self.kin.zero_qpos())
        self.walk = walk_trajectory() if walk else []
        # step of each part, and its exploded offset
        self.step_of, self.offset = {}, {}
        for k, (_, _, ids, dname, dist, _) in enumerate(STEPS):
            for cid in ids:
                i = self.idx[cid]
                v = np.array(DIRS[dname](side_of(cid)), float)
                self.step_of[i] = k
                self.offset[i] = v / np.linalg.norm(v) * dist
        missing = [p["id"] for i, p in enumerate(self.parts) if i not in self.step_of]
        assert not missing, f"parts without an assembly step: {missing}"
        # timeline
        self.t_steps0 = T_INTRO + T_EXPLODE
        self.t_finale0 = self.t_steps0 + len(STEPS) * T_STEP
        self.t_walk0 = self.t_finale0 + T_FINALE + T_CROUCH
        self.duration = self.t_walk0 + len(self.walk) / FPS + T_END

    # ---------------------------------------------------------------- per-frame state
    def pose(self, i, links, extra=None):
        p = self.parts[i]
        T = links[p["link"]] @ p["T"]
        if extra is not None:
            T = T.copy()
            T[:3, 3] += extra
        return T

    def camera_at(self, t, links):
        """(lookat, distance, azimuth, elevation): per-step framing, blended at each step start, slow drift inside steps."""
        def lerp_az(a0, a1, x):
            dlt = (a1 - a0 + 180) % 360 - 180
            return a0 + dlt * x
        intro_az = lambda tt: 150 + 12.0 * tt  # noqa: E731  (turntable during the intro and explode)
        if t < T_INTRO:
            z, dist, el = CAM["full"]
            return (0, 0, z), dist, intro_az(t), el
        if t < self.t_steps0:                    # widen to frame the exploded view
            a = smooth((t - T_INTRO) / 1.3)
            z, dist, el = (CAM["full"][j] + (CAM["explode"][j] - CAM["full"][j]) * a for j in range(3))
            return (0, 0, z), dist, intro_az(t), el
        if t < self.t_finale0:
            k = int((t - self.t_steps0) // T_STEP)
            ts = t - self.t_steps0 - k * T_STEP
            cur = CAM[STEPS[k][5]]
            prev = CAM[STEPS[k - 1][5]] if k > 0 else CAM["explode"]
            az_prev = STEP_AZ[k - 1] + AZ_DRIFT * T_STEP if k > 0 else intro_az(self.t_steps0)
            a = smooth(ts / 1.2)
            z, dist, el = (prev[j] + (cur[j] - prev[j]) * a for j in range(3))
            return (0, 0, z), dist, lerp_az(az_prev, STEP_AZ[k], a) + AZ_DRIFT * ts * a, el
        tf = t - self.t_finale0
        az_last = STEP_AZ[-1] + AZ_DRIFT * T_STEP
        if t < self.t_walk0 - T_CROUCH:          # finale: pull back to the full robot and orbit
            last = CAM[STEPS[-1][5]]
            a = smooth(tf / 1.8)
            z, dist, el = (last[j] + (CAM["full"][j] - last[j]) * a for j in range(3))
            return (0, 0, z), dist, az_last + 22.0 * tf, el
        az_walk = az_last + 22.0 * (self.t_walk0 - T_CROUCH - self.t_finale0)
        tw = t - (self.t_walk0 - T_CROUCH)       # crouch + walk: follow the pelvis, settle to a three-quarter view
        px = links["pelvis"][0, 3]
        a = smooth(tw / 1.5)
        return (px + 0.15, 0, 0.60), 2.7, lerp_az(az_walk, 215, a) + 1.5 * tw * a, -7

    def links_at(self, t):
        if t < self.t_walk0 - T_CROUCH or not self.walk:
            return self.zero_links
        if t < self.t_walk0:
            a = smooth((t - (self.t_walk0 - T_CROUCH)) / T_CROUCH)
            q = (1 - a) * self.kin.zero_qpos() + a * self.walk[0]
            q[3:7] /= np.linalg.norm(q[3:7])
            return self.kin.links(q)
        k = min(int((t - self.t_walk0) * FPS), len(self.walk) - 1)
        return self.kin.links(self.walk[k])

    def part_state(self, i, t):
        """(visible, offset vector, glow 0..1, alpha)."""
        if t < T_INTRO:
            return True, None, 0.0, 1.0
        if t < self.t_steps0:  # explode: all parts burst out together, hold as an exploded view, then fade
            te = t - T_INTRO
            out = smooth(te / 1.3)
            fade = smooth((te - 2.0) / 0.7)
            if fade >= 1.0:
                return False, None, 0.0, 0.0
            return True, self.offset[i] * EXPLODE_K * out, 0.0, 1.0 - fade
        if t >= self.t_finale0:
            return True, None, 0.0, 1.0
        ts = t - (self.t_steps0 + self.step_of[i] * T_STEP)
        if ts < 0:
            return False, None, 0.0, 0.0
        fly = ease_out((ts - 0.1) / T_FLY)
        alpha = smooth(ts / 0.35)
        glow = 1.0 if ts < T_FLY + 0.3 else max(0.0, 1.0 - (ts - T_FLY - 0.3) / 0.7)
        return True, self.offset[i] * (1 - fly), glow, alpha

    def render(self, t, camera=None):
        """Frame at film time t; camera = (lookat, distance, azimuth, elevation) overrides the film's framing."""
        links = self.links_at(t)
        quat = np.zeros(4)
        for i in range(len(self.parts)):
            vis, off, glow, alpha = self.part_state(i, t)
            if not vis or alpha <= 0.01:
                self.d.mocap_pos[i] = (0, 0, -50)
                continue
            T = self.pose(i, links, off)
            mujoco.mju_mat2Quat(quat, T[:3, :3].flatten())
            self.d.mocap_pos[i] = T[:3, 3]
            self.d.mocap_quat[i] = quat
            base = self.base_rgba[self.mat[i]]
            rgba = base * (1 - 0.75 * glow) + GLOW * 0.75 * glow
            rgba[3] = alpha
            self.m.mat_rgba[self.mat[i]] = rgba
        self.m.stat.center[0] = links["pelvis"][0, 3]   # keep the shadow frustum on the robot while it walks
        mujoco.mj_forward(self.m, self.d)
        (lx, ly, lz), dist, az, el = camera or self.camera_at(t, links)
        self.cam.lookat[:] = (lx, ly, lz)
        self.cam.distance, self.cam.azimuth, self.cam.elevation = dist, az, el
        self.r.update_scene(self.d, self.cam)
        return self.r.render()

    def timeline(self):
        seg = [{"kind": "intro", "start": 0.0, "end": T_INTRO, "title": "JX1", "subtitle": "a 1.23 m humanoid you can build in India"},
               {"kind": "explode", "start": T_INTRO, "end": self.t_steps0, "title": "87 parts", "subtitle": "let's put it together"}]
        for k, (title, sub, ids, *_rest) in enumerate(STEPS):
            s = self.t_steps0 + k * T_STEP
            seg.append({"kind": "step", "step": k + 1, "of": len(STEPS), "start": round(s, 3), "end": round(s + T_STEP, 3),
                        "title": title, "subtitle": sub, "parts": len(ids)})
        seg.append({"kind": "finale", "start": self.t_finale0, "end": self.t_walk0 - T_CROUCH, "title": "JX1 assembled",
                    "subtitle": "1.23 m · 33.6 kg · 23 DOF"})
        if self.walk:
            seg.append({"kind": "walk", "start": self.t_walk0 - T_CROUCH, "end": self.duration, "title": "and it walks",
                        "subtitle": "MuJoCo simulation of the CAD model · 0.52 m/s"})
        return {"fps": FPS, "duration": round(self.duration, 3), "segments": seg}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true", help="960x540, fewer samples")
    ap.add_argument("--no-walk", action="store_true")
    ap.add_argument("--stills-only", action="store_true")
    ap.add_argument("--hero", action="store_true", help="README cover shots only")
    a = ap.parse_args()
    if a.hero:
        import PIL.Image
        film = Film(1600, 1100, 8, walk=False)
        t = film.t_finale0 + 0.5 * T_FINALE          # finished robot, zero pose, no glow
        for name, cam in HERO_SHOTS.items():
            PIL.Image.fromarray(film.render(t, cam)).save(IMG / name)
            print("wrote", IMG / name, flush=True)
        return
    w, h, samples = (960, 540, 4) if a.preview else (1920, 1080, 8)
    film = Film(w, h, samples, walk=not a.no_walk)
    OUT.mkdir(parents=True, exist_ok=True)
    IMG.mkdir(parents=True, exist_ok=True)
    STEPS_DIR.mkdir(parents=True, exist_ok=True)
    (OUT / "timeline.json").write_text(json.dumps(film.timeline(), indent=1), encoding="utf-8")
    import PIL.Image
    stills = {"jx1_front.png": 2.4, "jx1_exploded.png": T_INTRO + 1.7, "jx1_assembled.png": film.t_finale0 + 3.0}
    if film.walk:
        stills["jx1_walking.png"] = film.t_walk0 + 2.0
    for name, t in stills.items():
        PIL.Image.fromarray(film.render(t)).save(IMG / name)
    for k in range(len(STEPS)):
        t = film.t_steps0 + (k + 1) * T_STEP - 0.05
        PIL.Image.fromarray(film.render(t)).save(STEPS_DIR / f"step_{k + 1:02d}.png")
    print("stills written", flush=True)
    if a.stills_only:
        return
    n = int(round(film.duration * FPS))
    out = OUT / ("footage_preview.mp4" if a.preview else "footage.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
                           "-g", str(FPS), "-keyint_min", str(FPS), "-movflags", "+faststart", str(out)],  # 1 s GOP: seekable in HyperFrames
                          stdin=subprocess.PIPE)
    for f in range(n):
        ff.stdin.write(film.render(f / FPS).tobytes())
        if f % 300 == 0:
            print(f"frame {f}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()
    print(f"wrote {out} ({film.duration:.1f} s, {n} frames)")


if __name__ == "__main__":
    main()
