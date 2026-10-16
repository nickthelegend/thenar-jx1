"""Sim-to-sim check of an exported JX0 walking policy on the verified JX0 model (not the training model):

    rl/.venv/Scripts/python jx0/rl/sim2sim_jx0.py --policy jx0/rl/policies/<name> [--latency-ms 10] [--seconds 10]
        -> <policy>/sim2sim.json

The robot is jx0/sim/jx0_model.py at 1 kHz with the STS3215 model of walk_jx0.py: tau = kp (goal - q) - kd qdot inside
the servo's torque-speed line (stall 2.94 N m, no-load 4.72 rad/s) - which the training model does not have. The
policy runs at its 50 Hz on the observation of rl/jx1_rl/policy_io.py; its goals go through jx0bot's clamps (limits,
couple_hips) and reach the servos at 100 Hz, ramped over the policy period, optionally with a sensing and an actuation
delay. Scenarios: stand, walk forward (two speeds), backward, sideways both ways, turn both ways. Per scenario: fell or
not, the speed achieved vs commanded, peak torque and speed vs the servo's limits.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import deque
from pathlib import Path

import mujoco
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "rl"))
sys.path.insert(0, str(ROOT / "jx0" / "sim"))
sys.path.insert(0, str(ROOT / "jx0" / "software"))
sys.path.insert(0, str(ROOT / "calculations"))
from jx1_rl import policy_io as pio  # noqa: E402
from jx0_model import build  # noqa: E402
from jx1calc.design import Design  # noqa: E402
from jx0bot.robot import couple_hips  # noqa: E402

BUS_HZ = 100


class ServoModel:
    """jx0/sim/walk_jx0.py's STS3215 (copied: that module needs scipy, which rl/.venv does not have): tau = kp (goal -
    q) - kd qdot, limited by the torque-speed line while motoring, by the stall torque while braking."""

    def __init__(self, stall, no_load, kp, kd):
        self.stall, self.w0, self.kp, self.kd = stall, no_load, kp, kd

    def torque(self, goal, q, qd):
        tau = self.kp * (goal - q) - self.kd * qd
        lim = self.stall * max(0.0, 1.0 - abs(qd) / self.w0) if tau * qd > 0 else self.stall
        return float(np.clip(tau, -lim, lim))
SCENARIOS = [("stand", (0.0, 0.0, 0.0)), ("forward", (0.05, 0.0, 0.0)), ("forward_fast", (0.10, 0.0, 0.0)),
             ("backward", (-0.04, 0.0, 0.0)), ("left", (0.0, 0.04, 0.0)), ("right", (0.0, -0.04, 0.0)),
             ("turn_left", (0.0, 0.0, 0.3)), ("turn_right", (0.0, 0.0, -0.3))]


def short(j: str) -> str:
    """left_knee_joint -> l_knee (jx0bot / jx0_model names)."""
    j = j[:-len("_joint")]
    for side, s in (("left_", "l_"), ("right_", "r_")):
        if j.startswith(side):
            return s + j[len(side):]
    return j


class Policy:
    def __init__(self, folder: Path):
        import onnxruntime as ort
        self.io = yaml.safe_load((folder / "policy_io.yaml").read_text(encoding="utf-8"))
        self.sess = ort.InferenceSession(str(folder / self.io["policy"]["onnx"]))

    def __call__(self, obs):
        return self.sess.run(["actions"], {"obs": obs[None].astype(np.float32)})[0][0].astype(np.float64)


def run(policy: Policy, command, seconds, latency_ms=0.0, schedule=None, frame=None, xml=None):
    """schedule: [(t_end s, command), ...] in place of one command; frame(m, d, command): called at 30 Hz (video)."""
    io = policy.io
    design = Design(ROOT / "jx0" / "design_point.yaml")
    st = design.act_classes["ST"]
    m = mujoco.MjModel.from_xml_string(xml or build(design))
    d = mujoco.MjData(m)
    pj = io["joints"]["policy"]
    allj = list(io["default_joint_pos"])
    sj = {j: short(j) for j in allj}
    adr = {j: (m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, sj[j])],
               m.jnt_dofadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, sj[j])]) for j in allj}
    act = {j: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, sj[j]) for j in allj}
    kp = {j: io["pd_gains"][j][0] for j in allj}
    kd = {j: io["pd_gains"][j][1] for j in allj}
    servo = {j: ServoModel(st["stall_torque_nm"], st["no_load_speed_rad_s"], kp[j], kd[j]) for j in allj}
    default = np.array([io["default_joint_pos"][j] for j in pj])
    lo = np.array([io["joint_limits_rad"][j][0] for j in pj])
    hi = np.array([io["joint_limits_rad"][j][1] for j in pj])
    scales, clip = io["observation"]["scales"], io["observation"]["clip"]
    period, thr = io["gait"]["period_s"], io["gait"].get("stand_command_threshold")
    dt_pol = io["control"]["policy_dt_s"]
    sub = int(round(dt_pol / m.opt.timestep))
    bus_every = int(round(1.0 / BUS_HZ / m.opt.timestep))
    pelvis = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "pelvis")

    # start in the default pose, soles on the floor
    goal = {j: io["default_joint_pos"][j] for j in allj}
    for j in allj:
        d.qpos[adr[j][0]] = goal[j]
    mujoco.mj_forward(m, d)
    sole = min(d.site_xpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, s)][2] for s in ("l_sole", "r_sole"))
    d.qpos[2] -= sole - 0.0005
    mujoco.mj_forward(m, d)

    delay = int(round(latency_ms / 1000.0 / m.opt.timestep))
    obs_hist = deque(maxlen=delay + 1)
    goal_hist = deque(maxlen=delay + 1)
    cmd = np.asarray(command, dtype=np.float64)
    last_action = np.zeros(len(pj))
    prev_goal, next_goal = dict(goal), dict(goal)
    peak_tau, peak_speed, fell, k = 0.0, 0.0, False, 0
    t_start_xy = None
    n_steps = int(round(seconds / m.opt.timestep))
    frame_every = int(round(1.0 / 30 / m.opt.timestep))
    for i in range(n_steps):
        if schedule:
            cmd = np.asarray(next((c for t, c in schedule if d.time < t), schedule[-1][1]), dtype=np.float64)
        if frame and i % frame_every == 0:
            frame(m, d, cmd)
        # sensing (possibly delayed)
        q = np.array([d.qpos[adr[j][0]] for j in pj])
        dq = np.array([d.qvel[adr[j][1]] for j in pj])
        quat = d.qpos[3:7].copy()
        ang_b = d.qvel[3:6].copy()                       # MuJoCo free joint: angular velocity in the body frame
        obs_hist.append((q, dq, quat, ang_b))
        if i % sub == 0:
            qs, dqs, qts, angs = obs_hist[0]
            phase = pio.gait_phase(np.array(d.time), period)
            moving = pio.gait_moving(cmd, thr)
            obs = pio.build_observation(angs, pio.projected_gravity(qts), cmd, qs - default, dqs, last_action, phase,
                                        scales, clip, moving)
            a = policy(obs)
            last_action = a
            tgt = pio.actions_to_targets(a, default, io["action_scale"], lo, hi)
            tgt = pio.clip_ankle_targets(tgt, pj, {s: np.asarray(p) for s, p in io["ankle_polygons_rad"].items()})
            full = {sj[j]: float(v) for j, v in zip(pj, tgt)}
            full = couple_hips(full)
            prev_goal = dict(next_goal)
            next_goal = {**next_goal, **{j: full[sj[j]] for j in pj}}
            k = 0
        # the Pi sends goals at 100 Hz, ramped over the policy period (first-order hold)
        if i % bus_every == 0:
            s = min(1.0, (k + bus_every) / sub)
            goal_hist.append({j: prev_goal[j] + s * (next_goal[j] - prev_goal[j]) for j in allj})
        k += 1
        g = goal_hist[0]
        for j in allj:
            qa, da = adr[j]
            tau = servo[j].torque(g[j], d.qpos[qa], d.qvel[da])
            d.ctrl[act[j]] = tau
            peak_tau = max(peak_tau, abs(tau))
            peak_speed = max(peak_speed, abs(d.qvel[da]))
        mujoco.mj_step(m, d)
        if d.time >= 2.0 and t_start_xy is None:          # measure after a 2 s start
            t_start_xy = (d.time, d.xpos[pelvis][:2].copy(), heading(d.qpos[3:7]))
        up = pio.projected_gravity(d.qpos[3:7])[2]
        if d.xpos[pelvis][2] < 0.08 or up > -0.5:          # pelvis down or tilted past 60 deg
            fell = True
            break
    out = {"command": list(cmd), "fell": fell, "seconds": round(d.time, 2),
           "peak_torque_of_stall": round(peak_tau / st["stall_torque_nm"], 2),
           "peak_speed_of_no_load": round(peak_speed / st["no_load_speed_rad_s"], 2)}
    if t_start_xy and not fell:
        t0, p0, h0 = t_start_xy
        T = d.time - t0
        dp = d.xpos[pelvis][:2] - p0
        h = heading(d.qpos[3:7])
        c, s_ = math.cos(h0), math.sin(h0)
        vx, vy = (c * dp[0] + s_ * dp[1]) / T, (-s_ * dp[0] + c * dp[1]) / T
        wz = wrap(h - h0) / T
        out.update({"achieved": [round(vx, 3), round(vy, 3), round(wz, 3)]})
    return out


def heading(q):
    w, x, y, z = q
    return math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


VIDEO = [(2.0, (0.0, 0.0, 0.0)), (9.0, (0.08, 0.0, 0.0)), (14.0, (0.0, 0.0, 0.3)), (19.0, (0.0, 0.04, 0.0)),
         (24.0, (-0.04, 0.0, 0.0)), (26.0, (0.0, 0.0, 0.0))]


def video(pol: Policy, out: Path, latency_ms: float):
    """The policy walking through VIDEO's commands, followed by the camera (1280 x 720, 30 fps; needs ffmpeg)."""
    import re
    import subprocess
    from PIL import Image, ImageDraw, ImageFont
    xml = build(Design(ROOT / "jx0" / "design_point.yaml"))
    xml = re.sub(r'<texture name="grid"[^>]*/>', '<texture name="grid" type="2d" builtin="checker" rgb1=".93 .93 .92" '
                 'rgb2=".86 .86 .85" width="512" height="512"/><texture type="skybox" builtin="gradient" '
                 'rgb1=".98 .98 .98" rgb2=".84 .86 .88" width="64" height="512"/>', xml, count=1)
    W, H = 1280, 720
    ff = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
    state = {}
    font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 34)

    def frame(m, d, cmd):
        if "r" not in state:
            state["r"] = mujoco.Renderer(m, H, W)
            state["cam"] = mujoco.MjvCamera()
            state["cam"].azimuth, state["cam"].elevation, state["cam"].distance = 140.0, -15.0, 0.9
            state["look"] = d.xpos[1].copy()
        cam = state["cam"]
        state["look"] += 0.05 * (d.xpos[1] - state["look"])
        cam.lookat[:] = state["look"]
        state["r"].update_scene(d, camera=cam)
        img = Image.fromarray(state["r"].render())
        vx, vy, wz = cmd
        text = ("stand" if not any(cmd) else f"walk {vx:+.2f} m/s" if vx else f"side {vy:+.2f} m/s" if vy else f"turn {wz:+.1f} rad/s")
        ImageDraw.Draw(img).text((40, 30), f"JX0 · learned policy · {text}", font=font, fill=(25, 28, 30))
        ff.stdin.write(img.tobytes())

    r = run(pol, VIDEO[0][1], VIDEO[-1][0], latency_ms, schedule=VIDEO, frame=frame, xml=xml)
    ff.stdin.close()
    ff.wait()
    print(f"video {out}: {'FELL at ' + str(r['seconds']) + ' s' if r['fell'] else 'stayed up'} over {VIDEO[-1][0]:.0f} s")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", required=True)
    ap.add_argument("--seconds", type=float, default=10.0)
    ap.add_argument("--latency-ms", type=float, default=0.0)
    ap.add_argument("--video", default=None, help="write an mp4 of the policy walking through stand / walk / turn / side / back")
    a = ap.parse_args()
    folder = Path(a.policy)
    pol = Policy(folder)
    if a.video:
        video(pol, Path(a.video), a.latency_ms)
        return
    res = {}
    for name, cmd in SCENARIOS:
        r = run(pol, cmd, a.seconds, a.latency_ms)
        res[name] = r
        print(f"{name:13s} cmd {cmd}  -> {'FELL at ' + str(r['seconds']) + ' s' if r['fell'] else 'achieved ' + str(r.get('achieved'))}"
              f"  peak torque {r['peak_torque_of_stall']:.0%} of stall, speed {r['peak_speed_of_no_load']:.0%} of no-load", flush=True)
    summary = {"latency_ms": a.latency_ms, "seconds": a.seconds, "servo_model": "walk_jx0.ServoModel (torque-speed line)",
               "physics_hz": 1000, "bus_hz": BUS_HZ, "scenarios": res,
               "stayed_up": sum(not r["fell"] for r in res.values()), "of": len(res)}
    (folder / f"sim2sim{'_lat%d' % a.latency_ms if a.latency_ms else ''}.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(f"stayed up in {summary['stayed_up']}/{summary['of']} scenarios")


if __name__ == "__main__":
    main()
