"""Test an exported JX0 policy on the verified JX0 model (not the training model): speeds, pushes, a 60 s endurance run
and latency, with pass / fail criteria.

    rl/.venv/Scripts/python jx0/rl/sim2sim_jx0.py --policy jx0/rl/policies/<name>            -> <policy>/sim2sim.json
    rl/.venv/Scripts/python jx0/rl/sim2sim_jx0.py --policy ... --only speeds|pushes|endurance|latency
    rl/.venv/Scripts/python jx0/rl/sim2sim_jx0.py --policy ... --video walk.mp4                (the endurance run, filmed)

The robot: jx0/sim/jx0_model.py at 1 kHz, each servo the STS3215 model of walk_jx0.py (tau = kp (goal - q) - kd qdot
inside the torque-speed line: stall 2.94 N m, no-load 4.72 rad/s) - which the training model does not have. The
policy runs at its 50 Hz on the observation of policy_io.yaml (with history when the policy has it); its goals go
through jx0bot's clamps (joint limits, couple_hips) and reach the servos at 100 Hz, ramped over the policy period.
Pushes are horizontal force pulses (0.1 s) on the torso.

Criteria (all must hold for PASS):
- speeds: 11 commands (stand; forward 0.03-0.12 m/s; back; sideways; turns; forward + turn), 10 s each, measured over
  the last 7 s: no fall; each commanded axis within max(35 %, 0.012 m/s | 0.06 rad/s); drift on the others under
  0.02 m/s / 0.10 rad/s;
- pushes: walking (0.06 m/s) and standing, 0.24 / 0.48 / 0.72 N s from the front, back, left and right, at 4 moments
  of the gait: every push up to 0.48 N s survived (0.72 N s reported);
- endurance: 60 s through 12 commands with a 0.24 N s push every 7 s: no fall, no joint past its servo limit, every
  servo's mean |torque| under its rated 0.98 N m;
- latency: forward, turn and side-step with 12 ms more delay (6 ms sensing + 6 ms actuation): no fall, axes within 50 %.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
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
EEPROM_DEG = 1.0
SPEEDS = [("stand", (0.0, 0.0, 0.0)), ("forward_0.03", (0.03, 0.0, 0.0)), ("forward_0.06", (0.06, 0.0, 0.0)),
          ("forward_0.09", (0.09, 0.0, 0.0)), ("forward_0.12", (0.12, 0.0, 0.0)), ("backward_0.04", (-0.04, 0.0, 0.0)),
          ("left_0.04", (0.0, 0.04, 0.0)), ("right_0.04", (0.0, -0.04, 0.0)), ("turn_left_0.3", (0.0, 0.0, 0.3)),
          ("turn_right_0.3", (0.0, 0.0, -0.3)), ("forward_turn", (0.06, 0.0, 0.2))]
ENDURANCE = [(0.0, 0.0, 0.0), (0.06, 0.0, 0.0), (0.0, 0.0, 0.3), (0.10, 0.0, 0.0), (0.0, 0.04, 0.0), (-0.04, 0.0, 0.0),
             (0.0, 0.0, -0.3), (0.0, -0.04, 0.0), (0.03, 0.0, 0.0), (0.06, 0.0, 0.2), (0.0, 0.0, 0.0), (0.12, 0.0, 0.0)]
PUSH_DIRS = {"front": (-1.0, 0.0), "back": (1.0, 0.0), "left": (0.0, -1.0), "right": (0.0, 1.0)}   # push FROM the side


class ServoModel:
    """jx0/sim/walk_jx0.py's STS3215 (copied: that module needs scipy, which rl/.venv does not have): tau = kp (goal -
    q) - kd qdot, limited by the torque-speed line while motoring, by the stall torque while braking."""

    def __init__(self, stall, no_load, kp, kd):
        self.stall, self.w0, self.kp, self.kd = stall, no_load, kp, kd

    def torque(self, goal, q, qd):
        tau = self.kp * (goal - q) - self.kd * qd
        lim = self.stall * max(0.0, 1.0 - abs(qd) / self.w0) if tau * qd > 0 else self.stall
        return float(np.clip(tau, -lim, lim))


def short(j: str) -> str:
    """left_knee_joint -> l_knee (jx0bot / jx0_model names)."""
    j = j[:-len("_joint")]
    for side, s in (("left_", "l_"), ("right_", "r_")):
        if j.startswith(side):
            return s + j[len(side):]
    return j


def heading(q):
    w, x, y, z = q
    return math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))


class Policy:
    def __init__(self, folder: Path):
        import onnxruntime as ort
        self.io = yaml.safe_load((folder / "policy_io.yaml").read_text(encoding="utf-8"))
        self.sess = ort.InferenceSession(str(folder / self.io["policy"]["onnx"]))

    def __call__(self, obs):
        return self.sess.run(["actions"], {"obs": obs[None].astype(np.float32)})[0][0].astype(np.float64)


class JX0Sim:
    """The verified JX0 model driven by the policy the way the robot would run it."""

    def __init__(self, policy: Policy, obs_delay_ms=0.0, act_delay_ms=0.0, xml=None):
        self.pol, io = policy, policy.io
        self.io = io
        design = Design(ROOT / "jx0" / "design_point.yaml")
        self.st = st = design.act_classes["ST"]
        m = self.m = mujoco.MjModel.from_xml_string(xml or build(design))
        d = self.d = mujoco.MjData(m)
        self.pj = io["joints"]["policy"]
        self.allj = list(io["default_joint_pos"])
        self.sj = {j: short(j) for j in self.allj}
        jid = {j: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, self.sj[j]) for j in self.allj}
        self.qa = {j: m.jnt_qposadr[jid[j]] for j in self.allj}
        self.da = {j: m.jnt_dofadr[jid[j]] for j in self.allj}
        self.act = {j: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, self.sj[j]) for j in self.allj}
        self.servo = {j: ServoModel(st["stall_torque_nm"], st["no_load_speed_rad_s"], *io["pd_gains"][j]) for j in self.allj}
        self.default = np.array([io["default_joint_pos"][j] for j in self.pj])
        self.lo = np.array([io["joint_limits_rad"][j][0] for j in self.pj])
        self.hi = np.array([io["joint_limits_rad"][j][1] for j in self.pj])
        self.lim_all = {j: io["joint_limits_rad"][j] for j in self.allj}
        self.polys = {s: np.asarray(p) for s, p in io["ankle_polygons_rad"].items()}
        ob = io["observation"]
        self.scales, self.clip, self.H = ob["scales"], ob["clip"], int(ob.get("history_length", 1))
        self.period, self.thr = io["gait"]["period_s"], io["gait"].get("stand_command_threshold")
        self.ref = None                                                     # corrections on the reference gait
        if io.get("action_reference"):
            sys.path.insert(0, str(ROOT / "jx0" / "rl"))
            import gait_reference
            self.ref = gait_reference.load(ROOT / io["action_reference"], joints=self.pj, stand_threshold=self.thr)
        self.sub = int(round(io["control"]["policy_dt_s"] / m.opt.timestep))
        self.bus_every = int(round(1.0 / BUS_HZ / m.opt.timestep))
        self.pelvis = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "pelvis")
        self.torso = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "torso")
        self.obs_delay = int(round(obs_delay_ms / 1000.0 / m.opt.timestep))
        self.act_delay = int(round(act_delay_ms / 1000.0 / m.opt.timestep))
        # start in the default pose, soles on the floor
        goal = {j: io["default_joint_pos"][j] for j in self.allj}
        for j in self.allj:
            d.qpos[self.qa[j]] = goal[j]
        mujoco.mj_forward(m, d)
        sole = min(d.site_xpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, s)][2] for s in ("l_sole", "r_sole"))
        d.qpos[2] -= sole - 0.0005
        mujoco.mj_forward(m, d)
        self.sens = deque(maxlen=self.obs_delay + 1)
        self.goals = deque(maxlen=self.act_delay + 1)
        self.frames = None
        self.last_action = np.zeros(len(self.pj))
        self.prev_goal, self.next_goal = dict(goal), dict(goal)
        self.k = 0
        self.i = 0
        self.push_until, self.push_f = -1.0, np.zeros(2)
        self.fell = False
        self.peak_tau = 0.0
        self.peak_speed = 0.0
        self.abs_tau = {j: 0.0 for j in self.allj}
        self.n_tau = 0
        self.limit_hits = 0

    # ---- the robot's sensors and its 50 Hz loop
    def _snapshot(self):
        d = self.d
        q = np.array([d.qpos[self.qa[j]] for j in self.pj])
        dq = np.array([d.qvel[self.da[j]] for j in self.pj])
        return d.qvel[3:6].copy(), pio.projected_gravity(d.qpos[3:7].copy()), q - self.default, dq

    def _policy(self, cmd):
        ang, grav, q_rel, dq = self.sens[0]
        frame = (ang, grav, q_rel, dq, self.last_action.copy())
        if self.frames is None:
            self.frames = deque([frame] * self.H, maxlen=self.H)          # as Isaac Lab / the training env after a reset
        else:
            self.frames.append(frame)
        f = list(self.frames)
        moving = pio.gait_moving(cmd, self.thr)
        obs = pio.build_observation_history(np.array([x[0] for x in f]), np.array([x[1] for x in f]), cmd,
                                            np.array([x[2] for x in f]), np.array([x[3] for x in f]),
                                            np.array([x[4] for x in f]), pio.gait_phase(np.array(self.d.time), self.period),
                                            self.scales, self.clip, moving)
        a = self.pol(obs)
        self.last_action = a
        base = self.default if self.ref is None else self.ref(np.array([pio.gait_phase(np.array(self.d.time), self.period)]), cmd[None])[0]
        tgt = pio.actions_to_targets(a, base, self.io["action_scale"], self.lo, self.hi)
        tgt = pio.clip_ankle_targets(tgt, self.pj, self.polys)
        full = couple_hips({self.sj[j]: float(v) for j, v in zip(self.pj, tgt)})
        self.prev_goal = dict(self.next_goal)
        self.next_goal = {**self.next_goal, **{j: full[self.sj[j]] for j in self.pj}}
        self.k = 0

    def push(self, impulse_ns, direction, seconds=0.1):
        """A horizontal shove on the torso: impulse (N s) over `seconds`, direction in the robot's heading frame."""
        h = heading(self.d.qpos[3:7])
        dx, dy = direction
        f = impulse_ns / seconds * np.array([math.cos(h) * dx - math.sin(h) * dy, math.sin(h) * dx + math.cos(h) * dy])
        self.push_until, self.push_f = self.d.time + seconds, f

    def step(self, cmd):
        """One physics step (1 ms)."""
        m, d = self.m, self.d
        self.sens.append(self._snapshot())
        if self.i % self.sub == 0:
            self._policy(np.asarray(cmd, dtype=np.float64))
        if self.i % self.bus_every == 0:                                    # the Pi's 100 Hz goal packets, ramped
            s = min(1.0, (self.k + self.bus_every) / self.sub)
            self.goals.append({j: self.prev_goal[j] + s * (self.next_goal[j] - self.prev_goal[j]) for j in self.allj})
        self.k += 1
        g = self.goals[0]
        for j in self.allj:
            q, qd = d.qpos[self.qa[j]], d.qvel[self.da[j]]
            tau = self.servo[j].torque(g[j], q, qd)
            d.ctrl[self.act[j]] = tau
            self.peak_tau = max(self.peak_tau, abs(tau))
            self.peak_speed = max(self.peak_speed, abs(qd))
            self.abs_tau[j] += abs(tau)
            lo, hi = self.lim_all[j]
            if q < lo - math.radians(EEPROM_DEG) or q > hi + math.radians(EEPROM_DEG):
                self.limit_hits += 1
        self.n_tau += 1
        d.xfrc_applied[self.torso, :] = 0.0
        if d.time < self.push_until:
            d.xfrc_applied[self.torso, :2] = self.push_f
        mujoco.mj_step(m, d)
        self.i += 1
        if d.xpos[self.pelvis][2] < 0.08 or pio.projected_gravity(d.qpos[3:7])[2] > -0.5:     # down, or tilted > 60 deg
            self.fell = True

    def pose(self):
        return self.d.xpos[self.pelvis][:2].copy(), heading(self.d.qpos[3:7]), self.d.time

    def run(self, cmd, seconds, frame=None, frame_hz=30):
        every = int(round(1.0 / frame_hz / self.m.opt.timestep))
        for _ in range(int(round(seconds / self.m.opt.timestep))):
            if frame and self.i % every == 0:
                frame(self, cmd)
            self.step(cmd)
            if self.fell:
                return False
        return True


def velocity(p0, h0, t0, p1, h1, t1):
    T = t1 - t0
    dp = p1 - p0
    c, s = math.cos(h0), math.sin(h0)
    return np.array([(c * dp[0] + s * dp[1]) / T, (-s * dp[0] + c * dp[1]) / T,
                     ((h1 - h0 + math.pi) % (2 * math.pi) - math.pi) / T])


def tracked(cmd, v, rel=0.35):
    """Every commanded axis within max(rel, floor); the others under the drift limits."""
    out = []
    for k, (c, x) in enumerate(zip(cmd, v)):
        floor, drift = (0.012, 0.02) if k < 2 else (0.06, 0.10)
        out.append(abs(x - c) <= max(rel * abs(c), floor) if c != 0 else abs(x) <= drift)
    return all(out)


def speeds(pol, obs_ms=0.0, act_ms=0.0, cases=SPEEDS, rel=0.35, seconds=10.0, settle=3.0):
    res = {}
    for name, cmd in cases:
        sim = JX0Sim(pol, obs_ms, act_ms)
        up = sim.run(cmd, settle)
        p0, h0, t0 = sim.pose()
        up = up and sim.run(cmd, seconds - settle)
        p1, h1, t1 = sim.pose()
        v = velocity(p0, h0, t0, p1, h1, t1) if up else None
        ok = bool(up and tracked(cmd, v, rel))
        res[name] = {"command": list(cmd), "fell": not up, "achieved": None if v is None else [round(float(x), 3) for x in v],
                     "peak_torque_of_stall": round(sim.peak_tau / sim.st["stall_torque_nm"], 2),
                     "peak_speed_of_no_load": round(sim.peak_speed / sim.st["no_load_speed_rad_s"], 2), "pass": ok}
        print(f"  {name:15s} cmd {cmd} -> {'FELL' if not up else str(res[name]['achieved'])}  {'ok' if ok else 'FAIL'}", flush=True)
    return res


def pushes(pol):
    res, period = [], pol.io["gait"]["period_s"]
    for mode, cmd in (("walking", (0.06, 0.0, 0.0)), ("standing", (0.0, 0.0, 0.0))):
        for J in (0.24, 0.48, 0.72):
            for dname, direction in PUSH_DIRS.items():
                for k in range(4):
                    sim = JX0Sim(pol)
                    t_push = 4.0 + k * period / 4
                    up = sim.run(cmd, t_push)
                    sim.push(J, direction)
                    up = up and sim.run(cmd, 4.0)
                    res.append({"mode": mode, "impulse_ns": J, "from": dname, "at_s": round(t_push, 2), "stayed_up": bool(up)})
            n = [r for r in res if r["mode"] == mode and r["impulse_ns"] == J]
            print(f"  {mode:8s} {J:.2f} N s: stayed up {sum(r['stayed_up'] for r in n)}/{len(n)}", flush=True)
    return res


def endurance(pol, frame=None):
    sim = JX0Sim(pol)
    t0 = time.perf_counter()
    up, walked = True, 0.0
    last_push = 0.0
    for i, cmd in enumerate(ENDURANCE):
        p0, _, _ = sim.pose()
        for _ in range(5):                                                   # 5 s per command, a push every 7 s
            if sim.d.time - last_push >= 7.0:
                sim.push(0.24, list(PUSH_DIRS.values())[int(sim.d.time // 7) % 4])
                last_push = sim.d.time
            up = sim.run(cmd, 1.0, frame=frame)
            if not up:
                break
        walked += float(np.linalg.norm(sim.pose()[0] - p0))
        if not up:
            break
    wall = time.perf_counter() - t0
    mean_tau = {j: sim.abs_tau[j] / max(sim.n_tau, 1) for j in sim.allj}
    worst = max(mean_tau, key=mean_tau.get)
    ok = bool(up and sim.limit_hits == 0 and mean_tau[worst] < sim.st["rated_torque_nm"])
    out = {"seconds": round(sim.d.time, 1), "fell": not up, "distance_walked_m": round(walked, 2),
           "limit_violations_ms": sim.limit_hits, "worst_mean_torque_nm": round(mean_tau[worst], 3), "worst_joint": worst,
           "rated_torque_nm": sim.st["rated_torque_nm"], "peak_torque_of_stall": round(sim.peak_tau / sim.st["stall_torque_nm"], 2),
           "real_time_factor": round(sim.d.time / wall, 2), "pass": ok}
    print(f"  60 s: {'FELL at ' + str(out['seconds']) + ' s' if not up else 'stayed up'}, walked {out['distance_walked_m']} m, "
          f"limit hits {sim.limit_hits}, worst mean torque {out['worst_mean_torque_nm']} N m ({worst}), "
          f"{out['real_time_factor']}x real time  {'ok' if ok else 'FAIL'}", flush=True)
    return out


def video(pol: Policy, out: Path):
    """The endurance run filmed (1280 x 720, 30 fps; needs ffmpeg)."""
    import re
    import subprocess
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1280, 720
    ff = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
    font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 30)
    state = {}

    def frame(sim, cmd):
        if "r" not in state:
            xml = build(Design(ROOT / "jx0" / "design_point.yaml"))
            state["r"] = mujoco.Renderer(sim.m, H, W)
            state["cam"] = mujoco.MjvCamera()
            state["cam"].azimuth, state["cam"].elevation, state["cam"].distance = 140.0, -15.0, 0.9
            state["look"] = sim.d.xpos[1].copy()
        cam = state["cam"]
        state["look"] += 0.05 * (sim.d.xpos[1] - state["look"])
        cam.lookat[:] = state["look"]
        state["r"].update_scene(sim.d, camera=cam)
        img = Image.fromarray(state["r"].render())
        vx, vy, wz = cmd
        text = ("stand" if not any(cmd) else ", ".join(t for t in (f"forward {vx:+.2f} m/s" if vx else "", f"side {vy:+.2f} m/s" if vy else "",
                                                                    f"turn {wz:+.1f} rad/s" if wz else "") if t))
        dr = ImageDraw.Draw(img)
        dr.rectangle([0, 0, W, 56], fill=(245, 246, 247))
        dr.text((24, 12), f"JX0 · learned policy · t {sim.d.time:4.1f} s · {text}" + ("  · PUSH" if sim.d.time < sim.push_until + 0.2 else ""),
                font=font, fill=(25, 28, 30))
        ff.stdin.write(img.tobytes())
    r = endurance(pol, frame=frame)
    ff.stdin.close()
    ff.wait()
    print(f"video {out}")
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", required=True)
    ap.add_argument("--only", choices=["speeds", "pushes", "endurance", "latency"])
    ap.add_argument("--video", default=None)
    a = ap.parse_args()
    folder = Path(a.policy)
    pol = Policy(folder)
    if a.video:
        video(pol, Path(a.video))
        return
    res = {"model": "jx0/sim/jx0_model.py, 1 kHz, STS3215 torque-speed line, 100 Hz bus, jx0bot clamps",
           "policy": folder.name, "num_obs": pol.io["policy"]["num_obs"], "joints": len(pol.io["joints"]["policy"])}
    t0 = time.perf_counter()
    if a.only in (None, "speeds"):
        print("speeds")
        res["speeds"] = speeds(pol)
    if a.only in (None, "pushes"):
        print("pushes")
        res["pushes"] = pushes(pol)
    if a.only in (None, "endurance"):
        print("endurance")
        res["endurance"] = endurance(pol)
    if a.only in (None, "latency"):
        print("latency (+6 ms sensing, +6 ms actuation)")
        res["latency"] = speeds(pol, 6.0, 6.0, [c for c in SPEEDS if c[0] in ("forward_0.06", "turn_left_0.3", "left_0.04")], rel=0.5)
    verdict = {}
    if "speeds" in res:
        verdict["speeds"] = all(r["pass"] for r in res["speeds"].values())
    if "pushes" in res:
        verdict["pushes"] = all(r["stayed_up"] for r in res["pushes"] if r["impulse_ns"] <= 0.48)
        res["push_rates"] = {f"{m} {J}": f"{sum(r['stayed_up'] for r in res['pushes'] if r['mode'] == m and r['impulse_ns'] == J)}/16"
                             for m in ("walking", "standing") for J in (0.24, 0.48, 0.72)}
    if "endurance" in res:
        verdict["endurance"] = res["endurance"]["pass"]
    if "latency" in res:
        verdict["latency"] = all(r["pass"] for r in res["latency"].values())
    res["verdict"], res["pass"] = verdict, all(verdict.values())
    res["wall_s"] = round(time.perf_counter() - t0, 1)
    name = f"sim2sim{'_' + a.only if a.only else ''}.json"
    (folder / name).write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"{'PASS' if res['pass'] else 'FAIL'}: {verdict}  ({res['wall_s']} s) -> {folder / name}")


if __name__ == "__main__":
    main()
