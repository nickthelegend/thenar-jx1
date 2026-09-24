"""Can JX0 walk on hobby servos? Closed-loop MuJoCo test of the planned gait through a servo model.

1. Plan: the JX1 gait pipeline (footsteps -> ZMP preview control -> whole-body IK) on the JX0 model (jx0_model.py).
2. Simulate: every joint is a hobby position servo (ServoModel): the goal position arrives at 50 Hz (the bus rate the
   Raspberry Pi sends), the servo applies stiffness * error - damping * speed, limited by its torque-speed line
   (stall torque at rest, zero at the no-load speed). No feed-forward torque: hobby servos cannot take one.
3. Balance: the pelvis IMU tilts the stance ankle and hip goals (same stabiliser law as JX1, in the software too).
Pass: no fall, final position within 5 cm + 10 % of the planned distance, heading within 10 deg.
Outputs jx0/results/walking.json, jx0/results/images/walk_*.png and walk.gif, and jx0/software/jx0bot/gaits/*.json
(the verified joint trajectories the robot plays).
Usage: .venv/Scripts/python jx0/sim/walk_jx0.py [--gait all|forward|turn_left|...] [--no-render] [--kp 60]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "calculations"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from jx1calc.design import Design, LEG_JOINTS  # noqa: E402
from jx1calc.gait import GaitParams, synthesize  # noqa: E402
from jx0_model import ARM_JOINTS, DESIGN, SMALL_SERVO_STALL, build  # noqa: E402

OUT = ROOT / "jx0" / "results"
IMG = OUT / "images"
GAIT_DIR = ROOT / "jx0" / "software" / "jx0bot" / "gaits"
H = 0.222
COMMON = dict(zmp_offset_x=0.005, hip_height=H, ds_ratio=0.25, step_height=0.015, t_start=0.8, t_end=1.0)
GAITS = {
    "forward": dict(step_length=0.040, step_time=0.60, n_steps=10),
    "forward_slow": dict(step_length=0.030, step_time=0.60, n_steps=8),
    "backward": dict(step_length=-0.025, step_time=0.60, n_steps=8),
    "turn_left": dict(step_length=0.0, step_time=0.60, n_steps=8, turn_per_step_deg=10.0),
    "turn_right": dict(step_length=0.0, step_time=0.60, n_steps=8, turn_per_step_deg=-10.0),
    "side_left": dict(step_length=0.0, step_time=0.60, n_steps=6, lateral_step=0.015),
}
ARM_POSE = {"l_shoulder_roll": np.radians(6), "r_shoulder_roll": np.radians(-6), "l_elbow": np.radians(-25), "r_elbow": np.radians(-25)}
K_ANKLE, D_ANKLE, K_HIP = 0.6, 0.05, 0.3          # stabiliser (rad per rad of tilt, per rad/s) — as JX1


def rpy(q):
    w, x, y, z = q
    return np.array([np.arctan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y)), np.arcsin(np.clip(2 * (w * y - z * x), -1, 1)),
                     np.arctan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))])


class ServoModel:
    """Hobby position servo: tau = kp (goal - q) - kd qdot, inside the torque-speed line; goal refreshed at bus_hz."""

    def __init__(self, stall, no_load, kp, kd):
        self.stall, self.w0, self.kp, self.kd = stall, no_load, kp, kd

    def torque(self, goal, q, qd):
        tau = self.kp * (goal - q) - self.kd * qd
        lim = self.stall * max(0.0, 1.0 - abs(qd) / self.w0) if tau * qd > 0 else self.stall   # motoring vs braking
        return float(np.clip(tau, -lim, lim))


def plan(model, design, name):
    g = GaitParams(name, **{**COMMON, **GAITS[name]})
    return g, synthesize(model, design, g)


def run(name, kp=60.0, kd=0.6, bus_hz=50.0, stabiliser=True, render=False):
    design = Design(DESIGN)
    servo_leg = design.act_classes["ST"]
    m = mujoco.MjModel.from_xml_string(build(design))
    d = mujoco.MjData(m)
    g, res = plan(m, design, name)
    t_ref, q_ref, contact = res["t"], res["qpos"], res["plan"].contact
    jnames = [f"{s}_{j}" for s in "lr" for j in LEG_JOINTS] + [f"{s}_{j}" for s in "lr" for j in ARM_JOINTS] + ["neck_yaw"]
    adr = {n: (m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)],
               m.jnt_dofadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)]) for n in jnames}
    act = {n: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, n) for n in jnames}
    leg_servo = ServoModel(servo_leg["stall_torque_nm"], servo_leg["no_load_speed_rad_s"], kp, kd)
    arm_servo = ServoModel(SMALL_SERVO_STALL, 6.0, kp * 0.25, kd * 0.25)
    # start in the first planned pose, arms in the walking pose
    d.qpos[:] = q_ref[0]
    for n, v in ARM_POSE.items():
        d.qpos[adr[n][0]] = v
    d.qpos[2] += 0.002
    mujoco.mj_forward(m, d)

    dt, T = m.opt.timestep, float(t_ref[-1])
    period = max(1, int(round(1.0 / (bus_hz * dt))))
    goal = {n: float(d.qpos[adr[n][0]]) for n in jnames}
    peak = {n: 0.0 for n in jnames}
    sat = {n: 0 for n in jnames}
    hist, frames, fell, trk = [], [], False, []
    renderer = None
    if render:
        renderer = mujoco.Renderer(m, 480, 640)
        cam = mujoco.MjvCamera()
        cam.distance, cam.azimuth, cam.elevation = 1.0, 135, -14
    n_steps = int(T / dt)
    for k in range(n_steps):
        t = k * dt
        i = min(int(round(t / g.dt)), len(t_ref) - 1)
        roll, pitch, yaw = rpy(d.qpos[3:7])
        if k % period == 0:                                   # a new goal packet on the bus
            st = contact[min(i, len(contact) - 1)]
            corr = {}
            if stabiliser:
                wx, wy = d.qvel[3], d.qvel[4]
                for s, on in (("l", st[0]), ("r", st[1])):
                    if on:
                        corr[f"{s}_ankle_pitch"] = K_ANKLE * pitch + D_ANKLE * wy
                        corr[f"{s}_ankle_roll"] = K_ANKLE * roll + D_ANKLE * wx
                        corr[f"{s}_hip_pitch"] = K_HIP * pitch
                        corr[f"{s}_hip_roll"] = K_HIP * roll
            for n in jnames:
                base = q_ref[i, adr[n][0]] if n.split("_", 1)[1] in LEG_JOINTS else ARM_POSE.get(n, 0.0)
                goal[n] = float(base + corr.get(n, 0.0))
        for n in jnames:
            qa, da = adr[n]
            sv = leg_servo if n.split("_", 1)[1] in LEG_JOINTS else arm_servo
            u = sv.torque(goal[n], d.qpos[qa], d.qvel[da])
            d.ctrl[act[n]] = u
            peak[n] = max(peak[n], abs(u))
            if abs(u) >= 0.98 * sv.stall:
                sat[n] += 1
            if n.split("_", 1)[1] in LEG_JOINTS:
                trk.append(abs(goal[n] - d.qpos[qa]))
        mujoco.mj_step(m, d)
        if k % 10 == 0:
            tilt = float(np.degrees(np.hypot(roll, pitch)))
            hist.append((t, *d.qpos[:3], *q_ref[i, :3], tilt, yaw, rpy(q_ref[i, 3:7])[2]))
            if d.qpos[2] < 0.13 or tilt > 30:
                fell = True
                break
        if renderer is not None and k % int(0.05 / dt) == 0:
            cam.lookat[:] = [d.qpos[0], d.qpos[1], 0.2]
            renderer.update_scene(d, cam)
            frames.append(renderer.render().copy())
    h = np.array(hist)
    dist_plan = float(np.linalg.norm(q_ref[-1, :2] - q_ref[0, :2]))
    dist_sim = float(np.linalg.norm(h[-1, 1:3] - h[0, 1:3]))
    pos_err = float(np.linalg.norm(h[-1, 1:3] - h[-1, 4:6]))
    yaw_plan = float(np.degrees(rpy(q_ref[-1, 3:7])[2]))
    head_err = float(np.degrees((h[-1, 8] - h[-1, 9] + np.pi) % (2 * np.pi) - np.pi))
    leg = [n for n in jnames if n.split("_", 1)[1] in LEG_JOINTS]
    out = {"gait": name, "params": {k: v for k, v in vars(g).items() if isinstance(v, (int, float, str))},
           "speed_m_s": round(abs(g.step_length) / g.step_time, 3),
           "servo_model": {"kp_nm_per_rad": kp, "kd_nm_s_per_rad": kd, "bus_hz": bus_hz, "stall_nm": leg_servo.stall,
                           "no_load_rad_s": leg_servo.w0, "label": "ASSUMED servo stiffness; datasheet stall/speed"},
           "stabiliser": {"k_ankle": K_ANKLE, "d_ankle": D_ANKLE, "k_hip": K_HIP} if stabiliser else None,
           "fell": fell, "duration_s": round(float(h[-1, 0]), 2), "planned_duration_s": round(T, 2),
           "distance_m": {"plan": round(dist_plan, 3), "sim": round(dist_sim, 3)}, "final_position_error_m": round(pos_err, 3),
           "heading_deg": {"plan": round(yaw_plan, 1), "error": round(head_err, 1)}, "max_tilt_deg": round(float(h[:, 7].max()), 1),
           "tracking_error_deg": {"rms": round(float(np.degrees(np.sqrt(np.mean(np.square(trk))))), 2),
                                  "max": round(float(np.degrees(np.max(trk))), 1)},
           "peak_torque_fraction_of_stall": {n: round(peak[n] / leg_servo.stall, 2) for n in leg},
           "saturated_fraction": {n: round(sat[n] / max(1, len(h) * 10), 3) for n in leg if sat[n]}}
    out["pass"] = bool(not fell and pos_err <= 0.05 + 0.10 * dist_plan and abs(head_err) < 10.0)
    return out, frames, (g, res, adr)


def export_gait(name, g, res, adr):
    """The planned leg trajectory at 50 Hz in joint names/radians, for the robot (jx0bot.gait plays it)."""
    t, q, c = res["t"], res["qpos"], res["plan"].contact
    step = max(1, int(round(0.02 / g.dt)))
    joints = [f"{s}_{j}" for s in "lr" for j in LEG_JOINTS]
    data = {"name": name, "dt": round(step * g.dt, 4), "hip_height_m": g.hip_height, "step_length_m": g.step_length,
            "step_time_s": g.step_time, "turn_per_step_deg": g.turn_per_step_deg, "lateral_step_m": g.lateral_step,
            "joints": joints, "q": [[round(float(q[i, adr[j][0]]), 5) for j in joints] for i in range(0, len(t), step)],
            "stance": [[bool(c[i, 0]), bool(c[i, 1])] for i in range(0, len(t), step)],
            "source": "jx0/sim/walk_jx0.py (ZMP preview control on the JX0 model, verified through the servo model)"}
    GAIT_DIR.mkdir(parents=True, exist_ok=True)
    (GAIT_DIR / f"{name}.json").write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gait", default="all", choices=["all"] + list(GAITS))
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--kp", type=float, default=60.0)
    ap.add_argument("--no-stabiliser", action="store_true")
    a = ap.parse_args()
    names = list(GAITS) if a.gait == "all" else [a.gait]
    results = {}
    for name in names:
        out, frames, (g, res, adr) = run(name, kp=a.kp, stabiliser=not a.no_stabiliser,
                                         render=not a.no_render and name in ("forward", "turn_left"))
        results[name] = out
        if out["pass"]:
            export_gait(name, g, res, adr)
        if frames:
            import PIL.Image
            IMG.mkdir(parents=True, exist_ok=True)
            ims = [PIL.Image.fromarray(f) for f in frames]
            ims[0].save(IMG / f"walk_{name}.gif", save_all=True, append_images=ims[1::2], duration=100, loop=0, optimize=True)
            for tag, f in (("start", frames[0]), ("mid", frames[len(frames) // 2]), ("end", frames[-1])):
                PIL.Image.fromarray(f).save(IMG / f"walk_{name}_{tag}.png")
        worst = max(out["peak_torque_fraction_of_stall"].items(), key=lambda kv: kv[1])
        print(f"{name:13s} {out['speed_m_s']:.3f} m/s fell {out['fell']!s:5s} dist {out['distance_m']['sim']:.3f}/{out['distance_m']['plan']:.3f} m "
              f"pos err {out['final_position_error_m']:.3f} heading {out['heading_deg']['error']:+.1f} tilt {out['max_tilt_deg']:.1f} "
              f"track rms {out['tracking_error_deg']['rms']:.1f} deg peak {worst[0]} {worst[1]:.0%} -> {'PASS' if out['pass'] else 'FAIL'}",
              flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    summary = {"generated_by": "jx0/sim/walk_jx0.py", "label": "CALCULATED (MuJoCo, servo model ASSUMED)", "gaits": results,
               "pass": all(r["pass"] for r in results.values())}
    if a.gait == "all":
        (OUT / "walking.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print("walking:", "PASS" if summary["pass"] else "FAIL", f"({sum(r['pass'] for r in results.values())}/{len(results)})")


if __name__ == "__main__":
    main()
