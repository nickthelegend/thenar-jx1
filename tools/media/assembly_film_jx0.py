"""Animated assembly film of JX0, rendered from its SolidWorks part meshes (jx0/cad/stl), like the JX1 film
(tools/media/assembly_film.py).

Every one of the 39 components (22 printed parts, the 2 feet included, and 17 STS3215 servos) is the exported
SolidWorks mesh, placed with the same layout as the SolidWorks assembly and the simulation (jx0/cad/layout.py). The film:
  intro   : the finished robot on a turntable, then it explodes into parts
  steps   : 13 assembly steps in the order of the build guide (jx0/docs/build_guide.md); each step's parts fly in from
            an exploded position, glow while they land, then settle to their colour; the camera frames the area built
  finale  : the complete robot, then it walks (replay of the verified MuJoCo gait, jx0/sim/walk_jx0.py 'forward', on
            the same servo model and balance controller as the walking checks)
Outputs: media/jx0_assembly/footage.mp4 + timeline.json (the titles: tools/media/build_assembly_composition_jx0.py),
jx0/docs/images/jx0_assembly_*.png stills, jx0/docs/assembly/step_XX.png (one still per step for the build guide).
Usage: .venv/Scripts/python tools/media/assembly_film_jx0.py [--preview] [--no-walk] [--stills-only]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "jx0" / "cad"))
sys.path.insert(0, str(ROOT / "jx0" / "sim"))
os.environ.setdefault("JX0_STL_DIR", str(ROOT / "nonexistent"))      # the walking model: plain boxes load faster
import geometry as G  # noqa: E402
from layout import components as layout_components, link_of  # noqa: E402

STL = ROOT / "jx0" / "cad" / "stl"
OUT = ROOT / "media" / "jx0_assembly"
IMG = ROOT / "jx0" / "docs" / "images"
STEPS_DIR = ROOT / "jx0" / "docs" / "assembly"
FPS = 30

LOOK = {  # rgba, specular, shininess, reflectance
    "petg": ((0.70, 0.85, 0.56, 1), 0.30, 0.45, 0.0),      # pelvis and leg parts: green PETG, a touch glossier
    "pla": ((0.76, 0.87, 0.62, 1), 0.12, 0.20, 0.0),       # body, head, arms: matte pastel-green PLA
    "servo": ((0.07, 0.07, 0.08, 1), 0.35, 0.50, 0.0),
}
GLOW = np.array([0.18, 0.78, 1.0, 1.0])                    # highlight while a part is arriving (as the JX1 film)
EXPLODE_K = 1.5


def category(part):
    if part == "JX0_Servo_STS3215":
        return "servo"
    return "petg" if part.startswith(G.LEG_PARTS) else "pla"


def components():
    """[{id, part, link, T}] with T the component pose in its simulation link frame (as jx0_model.cad_visuals)."""
    out = []
    for key, part, M in layout_components():
        link, origin = link_of(key)
        T = M.copy()
        T[:3, 3] = M[:3, 3] - origin * 1e-3
        out.append({"id": key, "part": part, "link": link, "T": T})
    return out


# ------------------------------------------------------------------------------------------------ assembly sequence
def side_of(cid):
    return 1 if cid.endswith("_L") else (-1 if cid.endswith("_R") else 0)


DIRS = {"up": lambda s: (0, 0, 1), "down": lambda s: (0, 0, -1), "back": lambda s: (-1, 0, 0), "front": lambda s: (1, 0, 0),
        "out": lambda s: (0, s, 0), "out_down": lambda s: (0, 0.7 * s, -0.7), "out_up": lambda s: (0, 0.7 * s, 0.7),
        "back_down": lambda s: (-0.7, 0, -0.7)}
CAM = {  # lookat z, distance, elevation (deg); JX0 stands 0.46 m tall, its hip 0.155 m above the floor
    "pelvis": (0.19, 0.42, -26), "hip": (0.16, 0.46, -18), "leg": (0.12, 0.58, -12), "knee": (0.10, 0.48, -10),
    "shin": (0.08, 0.45, -10), "foot": (0.04, 0.42, -14), "torso": (0.25, 0.70, -16), "arm": (0.27, 0.74, -12),
    "head": (0.36, 0.56, -14), "full": (0.23, 1.12, -8), "explode": (0.28, 1.75, -7),
}
LR = lambda *keys: [f"{k}_{s}" for s in ("L", "R") for k in keys]  # noqa: E731
STEPS = [
    ("Pelvis + hip-yaw servos", "PETG, printed near-solid · 2 × STS3215 in cages · thrust rings + keeper bosses",
     ["pelvis"] + LR("servo_hip_yaw"), "up", 0.10, "pelvis"),
    ("Hip-yaw discs + keepers", "disc on the yaw horn · keeper lip under its rim · held from both sides",
     LR("hip_yaw", "keeper"), "out_down", 0.10, "hip"),
    ("Hip-roll servos", "2 × STS3215 · caged behind the hip", LR("servo_hip_roll"), "back", 0.10, "hip"),
    ("Hip-roll U-brackets", "on the horn and the rear hub · double-sided", LR("hip_roll"), "front", 0.10, "hip"),
    ("Hip-pitch servos", "2 × STS3215 · axis through the hip centre", LR("servo_hip_pitch"), "out", 0.10, "hip"),
    ("Thighs + knee servos", "dog-leg U-bracket · knee servo lying forward", LR("thigh", "servo_knee"), "out_down", 0.12, "leg"),
    ("Shins + ankle-pitch servos", "U-bracket on the knee · ankle servo caged below", LR("shin", "servo_ankle_pitch"),
     "out", 0.11, "knee"),
    ("Ankle brackets + roll servos", "U-bracket on the ankle-pitch servo · roll cage behind the ankle",
     LR("ankle", "servo_ankle_roll"), "back", 0.10, "shin"),
    ("Feet", "chamfered 124 × 70 mm soles · U-bracket on the roll servo", LR("foot"), "down", 0.09, "foot"),
    ("Torso", "octagonal shell · skirt over the hip-yaw servos · Pi 4, battery, servo driver inside", ["torso"], "up",
     0.16, "torso"),
    ("Arms", "shoulder servo in a hood · elbow servo below · 6 mm paddle blades",
     LR("upper_arm", "servo_shoulder_pitch", "servo_elbow", "blade"), "out", 0.12, "arm"),
    ("Chest cap + neck servo", "speaker grille · vents · neck STS3215 on top", ["chest_cap", "servo_neck"], "up", 0.12, "torso"),
    ("Head", "soft rounded head · four holes for the microphone", ["head"], "up", 0.10, "head"),
]
STEP_AZ = [200, 160, 330, 200, 240, 215, 190, 320, 200, 160, 230, 200, 170]   # 180 = in front of the robot
AZ_DRIFT = 2.0
T_INTRO, T_EXPLODE, T_STEP, T_FLY, T_FINALE, T_CROUCH, T_END = 5.0, 2.8, 3.4, 1.5, 4.0, 1.2, 1.5


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------------------------------------ scene
def scene_xml(parts, w, h, samples):
    stems = sorted({p["part"] for p in parts})
    meshes = "\n".join(f'    <mesh name="m_{s}" file="{(STL / (s + ".stl")).as_posix()}" scale="0.001 0.001 0.001"/>' for s in stems)
    mats, bodies = [], []
    for i, p in enumerate(parts):
        rgba, spec, shin, refl = LOOK[category(p["part"])]
        mats.append(f'    <material name="mat{i}" rgba="{rgba[0]} {rgba[1]} {rgba[2]} 1" specular="{spec}" shininess="{shin}" reflectance="{refl}"/>')
        bodies.append(f'    <body name="c{i}" mocap="true" pos="0 0 -50"><geom type="mesh" mesh="m_{p["part"]}" material="mat{i}" '
                      f'contype="0" conaffinity="0"/></body>')
    return f"""<mujoco model="jx0_assembly_film">
  <visual>
    <global offwidth="{w}" offheight="{h}" fovy="30"/>
    <quality shadowsize="8192" offsamples="{samples}"/>
    <headlight ambient="0.30 0.30 0.32" diffuse="0.30 0.30 0.30" specular="0.08 0.08 0.08"/>
    <map znear="0.005" zfar="15" haze="0.35" shadowclip="0.5" shadowscale="0.6"/>
    <rgba haze="0.07 0.08 0.10 1"/>
  </visual>
  <statistic center="0 0 0.23" extent="0.4"/>
  <asset>
    <texture name="sky" type="skybox" builtin="gradient" rgb1="0.17 0.20 0.26" rgb2="0.02 0.03 0.05" width="512" height="3072"/>
    <texture name="grid" type="2d" builtin="checker" rgb1="0.11 0.12 0.14" rgb2="0.13 0.14 0.16" width="512" height="512"
             mark="edge" markrgb="0.20 0.22 0.26"/>
    <material name="floor" texture="grid" texrepeat="40 40" reflectance="0.22"/>
{meshes}
{chr(10).join(mats)}
  </asset>
  <worldbody>
    <light directional="true" pos="0.6 0.5 1.6" dir="-0.35 -0.30 -0.89" diffuse="0.78 0.76 0.74" specular="0.35 0.35 0.35" castshadow="true"/>
    <light directional="true" pos="-0.8 -0.6 1.2" dir="0.55 0.45 -0.70" diffuse="0.22 0.25 0.32" specular="0.1 0.1 0.1" castshadow="false"/>
    <light directional="true" pos="-0.4 0.8 0.6" dir="0.3 -0.8 -0.5" diffuse="0.18 0.18 0.20" specular="0.2 0.2 0.2" castshadow="false"/>
    <geom name="floor" type="plane" size="0 0 0.05" material="floor"/>
{chr(10).join(bodies)}
  </worldbody>
</mujoco>"""


class Kinematics:
    """Link poses of the walking model (jx0/sim/walk_jx0.py) for a given qpos."""

    def __init__(self):
        import walk_jx0 as W
        from jx1calc.design import Design
        self.m = mujoco.MjModel.from_xml_string(W.build(Design(W.DESIGN)))
        self.d = mujoco.MjData(self.m)
        self.body = {mujoco.mj_id2name(self.m, mujoco.mjtObj.mjOBJ_BODY, i): i for i in range(self.m.nbody)}
        self.q0 = self.m.qpos0.copy()               # the zero pose: legs straight, soles on the floor, arms down

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


def walk_trajectory(gait="forward"):
    """qpos samples (30 fps) of the verified walking simulation (walk_jx0.run, the forward gait, nominal robot)."""
    import walk_jx0 as W
    rec = []
    orig = mujoco.mj_step

    def step(m, d):
        orig(m, d)
        rec.append((d.time, d.qpos.copy()))

    mujoco.mj_step = step
    try:
        r = W.run(gait, render=False)[0]
    finally:
        mujoco.mj_step = orig
    assert not r["fell"], "the walk fell"
    times = np.array([t for t, _ in rec])
    return [rec[int(np.argmin(np.abs(times - tf)))][1] for tf in np.arange(0, times[-1], 1 / FPS)], r


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
        self.mat = [mujoco.mj_name2id(self.m, mujoco.mjtObj.mjOBJ_MATERIAL, f"mat{i}") for i in range(len(self.parts))]
        self.base_rgba = self.m.mat_rgba.copy()
        self.zero_links = self.kin.links(self.kin.q0)
        self.walk, self.walk_result = walk_trajectory() if walk else ([], None)
        self.step_of, self.offset = {}, {}
        for k, (_, _, ids, dname, dist, _) in enumerate(STEPS):
            for cid in ids:
                i = self.idx[cid]
                v = np.array(DIRS[dname](side_of(cid)), float)
                self.step_of[i] = k
                self.offset[i] = v / np.linalg.norm(v) * dist
        missing = [p["id"] for i, p in enumerate(self.parts) if i not in self.step_of]
        assert not missing, f"parts without an assembly step: {missing}"
        self.t_steps0 = T_INTRO + T_EXPLODE
        self.t_finale0 = self.t_steps0 + len(STEPS) * T_STEP
        self.t_walk0 = self.t_finale0 + T_FINALE + T_CROUCH
        self.duration = self.t_walk0 + len(self.walk) / FPS + T_END

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
        intro_az = lambda tt: 150 + 12.0 * tt  # noqa: E731
        if t < T_INTRO:
            z, dist, el = CAM["full"]
            return (0, 0, z), dist, intro_az(t), el
        if t < self.t_steps0:
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
        if t < self.t_walk0 - T_CROUCH:
            last = CAM[STEPS[-1][5]]
            a = smooth(tf / 1.8)
            z, dist, el = (last[j] + (CAM["full"][j] - last[j]) * a for j in range(3))
            return (0, 0, z), dist, az_last + 22.0 * tf, el
        az_walk = az_last + 22.0 * (self.t_walk0 - T_CROUCH - self.t_finale0)
        tw = t - (self.t_walk0 - T_CROUCH)
        px = links["pelvis"][0, 3]
        a = smooth(tw / 1.5)
        return (px + 0.05, 0, 0.22), 1.05, lerp_az(az_walk, 215, a) + 1.5 * tw * a, -7

    def links_at(self, t):
        if t < self.t_walk0 - T_CROUCH or not self.walk:
            return self.zero_links
        if t < self.t_walk0:
            a = smooth((t - (self.t_walk0 - T_CROUCH)) / T_CROUCH)
            q = (1 - a) * self.kin.q0 + a * self.walk[0]
            q[3:7] /= np.linalg.norm(q[3:7])
            return self.kin.links(q)
        k = min(int((t - self.t_walk0) * FPS), len(self.walk) - 1)
        return self.kin.links(self.walk[k])

    def part_state(self, i, t):
        """(visible, offset vector, glow 0..1, alpha)."""
        if t < T_INTRO:
            return True, None, 0.0, 1.0
        if t < self.t_steps0:
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
        self.m.stat.center[0] = links["pelvis"][0, 3]
        mujoco.mj_forward(self.m, self.d)
        (lx, ly, lz), dist, az, el = camera or self.camera_at(t, links)
        self.cam.lookat[:] = (lx, ly, lz)
        self.cam.distance, self.cam.azimuth, self.cam.elevation = dist, az, el
        self.r.update_scene(self.d, self.cam)
        return self.r.render()

    def timeline(self):
        n_parts = len(self.parts)
        seg = [{"kind": "intro", "start": 0.0, "end": T_INTRO, "title": "JX0",
                "subtitle": "the walking, talking STS3215 humanoid you can build at home"},
               {"kind": "explode", "start": T_INTRO, "end": self.t_steps0, "title": f"{n_parts} parts",
                "subtitle": "let's put it together"}]
        for k, (title, sub, ids, *_rest) in enumerate(STEPS):
            s = self.t_steps0 + k * T_STEP
            seg.append({"kind": "step", "step": k + 1, "of": len(STEPS), "start": round(s, 3), "end": round(s + T_STEP, 3),
                        "title": title, "subtitle": sub, "parts": len(ids)})
        mass = float(self.kin.m.body_subtreemass[1])
        seg.append({"kind": "finale", "start": self.t_finale0, "end": self.t_walk0 - T_CROUCH, "title": "JX0 assembled",
                    "subtitle": f"46 cm · {mass:.2f} kg · 17 STS3215 joints"})
        if self.walk:
            v = self.walk_result["speed_m_s"]
            seg.append({"kind": "walk", "start": self.t_walk0 - T_CROUCH, "end": self.duration, "title": "and it walks",
                        "subtitle": f"MuJoCo simulation of the CAD model · {v:.2f} m/s"})
        return {"fps": FPS, "duration": round(self.duration, 3), "parts": n_parts, "mass_kg": round(mass, 3), "segments": seg}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true", help="960x540, fewer samples")
    ap.add_argument("--no-walk", action="store_true")
    ap.add_argument("--stills-only", action="store_true")
    a = ap.parse_args()
    w, h, samples = (960, 540, 4) if a.preview else (1920, 1080, 8)
    film = Film(w, h, samples, walk=not a.no_walk)
    for d in (OUT, IMG, STEPS_DIR):
        d.mkdir(parents=True, exist_ok=True)
    (OUT / "timeline.json").write_text(json.dumps(film.timeline(), indent=1), encoding="utf-8")
    import PIL.Image
    stills = {"jx0_assembly_front.png": 2.4, "jx0_assembly_exploded.png": T_INTRO + 1.7,
              "jx0_assembly_done.png": film.t_finale0 + 3.0}
    if film.walk:
        stills["jx0_assembly_walking.png"] = film.t_walk0 + 2.0
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
                           "-g", str(FPS), "-keyint_min", str(FPS), "-movflags", "+faststart", str(out)],
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
