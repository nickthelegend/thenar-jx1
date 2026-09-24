"""Sim-to-sim check: run an EXPORTED policy (ONNX + policy_io.yaml) on the full CAD MuJoCo model.

The training model uses fitted capsules, 200 Hz physics and domain randomisation; this check uses the CAD model as
generated (simulation/mujoco/jx1.xml: CoACD mesh-hull collisions, 500 Hz physics, nominal masses) and only the exported
artefacts — the same inputs the ROS 2 node gets. Scenarios: stand, walk forward/backward, side-step, turn, and a
velocity sweep; each reports fall, mean velocity tracking error, max tilt, peak torque vs effort limit and foot slip.
Outputs <policy>/sim2sim.json and <policy>/sim2sim_walk.gif.
Usage: rl/.venv/Scripts/python rl/sim2sim.py [--policy rl/policies/jx1_walk_flat] [--no-render]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import mujoco
import numpy as np
import onnxruntime as ort
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jx1_rl import REPO, RL_DIR, policy_io  # noqa: E402

SCENARIOS = [("stand", (0.0, 0.0, 0.0), 6.0), ("forward_0.5", (0.5, 0.0, 0.0), 10.0), ("forward_0.8", (0.8, 0.0, 0.0), 10.0),
             ("backward_0.3", (-0.3, 0.0, 0.0), 8.0), ("sidestep_0.2", (0.0, 0.2, 0.0), 8.0), ("turn_0.5", (0.0, 0.0, 0.5), 8.0),
             ("walk_turn", (0.4, 0.0, 0.3), 10.0)]


class Runner:
    """Deployment-side policy runner: builds observations from robot state, returns joint targets (policy_io.yaml)."""

    def __init__(self, policy_dir: Path):
        self.io = yaml.safe_load((policy_dir / "policy_io.yaml").read_text(encoding="utf-8"))
        self.sess = ort.InferenceSession(str(policy_dir / self.io["policy"]["onnx"]))
        self.joints = self.io["joints"]["policy"]
        self.default = np.array([self.io["default_joint_pos"][j] for j in self.joints])
        lim = self.io["joint_limits_rad"]
        self.lower = np.array([lim[j][0] for j in self.joints])
        self.upper = np.array([lim[j][1] for j in self.joints])
        self.polys = {s: np.array(p) for s, p in self.io["ankle_polygons_rad"].items()}
        self.last_action = np.zeros(len(self.joints))

    def targets(self, quat_wxyz, ang_vel_b, q, dq, command, t):
        grav = policy_io.projected_gravity(np.asarray(quat_wxyz, dtype=np.float64))
        ph = policy_io.gait_phase(np.asarray(t, dtype=np.float64), self.io["gait"]["period_s"])
        obs = policy_io.build_observation(np.asarray(ang_vel_b), grav, np.asarray(command, dtype=np.float64), q - self.default, dq,
                                          self.last_action, ph, self.io["observation"]["scales"], self.io["observation"]["clip"])
        act = self.sess.run([self.io["policy"]["output"]], {self.io["policy"]["input"]: obs[None].astype(np.float32)})[0][0]
        self.last_action = act.astype(np.float64)
        tgt = policy_io.actions_to_targets(self.last_action, self.default, self.io["action_scale"], self.lower, self.upper)
        return policy_io.clip_ankle_targets(tgt, self.joints, self.polys)


def load_cad_model(io):
    m = mujoco.MjModel.from_xml_path(str(REPO / io["trained"]["source_mjcf"]))
    act_of = {}
    for a in range(m.nu):
        j = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, m.actuator_trnid[a, 0])
        act_of[j] = a
        if j in io["pd_gains"]:
            kp, kd = io["pd_gains"][j]
            m.actuator_gainprm[a, 0] = kp
            m.actuator_biasprm[a, 1] = -kp
            m.actuator_biasprm[a, 2] = -kd
    return m, act_of


def run(policy_dir: Path, render=True):
    rn = Runner(policy_dir)
    io = rn.io
    m, act_of = load_cad_model(io)
    dt_pol = io["control"]["policy_dt_s"]
    dec = int(round(dt_pol / m.opt.timestep))
    jq = {j: m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, j)] for j in act_of}
    jd = {j: m.jnt_dofadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, j)] for j in act_of}
    pol_q = np.array([jq[j] for j in rn.joints])
    pol_d = np.array([jd[j] for j in rn.joints])
    pol_a = np.array([act_of[j] for j in rn.joints])
    sole = [mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, f"{s}_sole") for s in ("left", "right")]
    renderer = None
    if render:
        try:
            renderer = mujoco.Renderer(m, 240, 320)
        except Exception as e:  # pragma: no cover
            print("render disabled:", e)
    results, frames = {}, []
    for name, cmd, T in SCENARIOS:
        d = mujoco.MjData(m)
        for j, a in act_of.items():
            d.qpos[jq[j]] = io["default_joint_pos"].get(j, 0.0)
            d.ctrl[a] = io["default_joint_pos"].get(j, 0.0)
        d.qpos[2] = 1.0
        mujoco.mj_kinematics(m, d)
        d.qpos[2] = 1.0 - min(d.site_xpos[s][2] for s in sole) + 0.002
        mujoco.mj_forward(m, d)
        rn.last_action[:] = 0.0
        vel_err, tilt_max, peak = [], 0.0, np.zeros(m.nu)
        slip, fell = [], False
        cam = mujoco.MjvCamera()
        cam.distance, cam.azimuth, cam.elevation = 2.4, 130, -12
        for k in range(int(T / dt_pol)):
            quat = d.qpos[3:7].copy()
            ang_b = d.qvel[3:6].copy()
            tgt = rn.targets(quat, ang_b, d.qpos[pol_q], d.qvel[pol_d], cmd, d.time)
            d.ctrl[pol_a] = tgt
            for _ in range(dec):
                mujoco.mj_step(m, d)
                peak = np.maximum(peak, np.abs(d.actuator_force))
            v_b = policy_io.quat_rotate_inverse(d.qpos[3:7], d.qvel[0:3])
            if k * dt_pol > 2.0:                                   # after the start transient
                vel_err.append([v_b[0] - cmd[0], v_b[1] - cmd[1], d.qvel[5] - cmd[2]])
            g = policy_io.projected_gravity(d.qpos[3:7])
            tilt_max = max(tilt_max, float(np.degrees(np.arccos(np.clip(-g[2], -1, 1)))))
            for s in sole:
                if d.site_xpos[s][2] < 0.003:
                    vel = np.zeros(6)
                    mujoco.mj_objectVelocity(m, d, mujoco.mjtObj.mjOBJ_SITE, s, vel, 0)
                    slip.append(float(np.linalg.norm(vel[3:5])))
            if d.qpos[2] < 0.35 or tilt_max > 60:
                fell = True
                break
            if renderer is not None and name == "forward_0.5" and k % 4 == 0:
                cam.lookat[:] = [d.qpos[0], d.qpos[1], 0.55]
                renderer.update_scene(d, cam)
                frames.append(renderer.render().copy())
        e = np.array(vel_err) if vel_err else np.zeros((1, 3))
        lim = np.array([io["effort_limits_Nm"].get(mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, m.actuator_trnid[a, 0]), np.inf)
                        for a in range(m.nu)])
        worst = int(np.argmax(peak / lim))
        results[name] = {"command": list(cmd), "duration_s": T, "fell": fell, "time_survived_s": round(float(d.time), 2),
                         "mean_velocity_b": np.round(e.mean(axis=0) + np.array(cmd), 3).tolist(),
                         "velocity_rmse": np.round(np.sqrt((e ** 2).mean(axis=0)), 3).tolist(),
                         "max_tilt_deg": round(tilt_max, 2), "stance_foot_slip_m_s_p95": round(float(np.percentile(slip, 95)), 3) if slip else None,
                         "peak_torque_fraction": round(float(peak[worst] / lim[worst]), 3),
                         "peak_torque_joint": mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, worst)}
        r = results[name]
        print(f"{name:13s} cmd {cmd} -> {'FELL' if fell else 'ok  '} v_mean {r['mean_velocity_b']} rmse {r['velocity_rmse']} "
              f"tilt {r['max_tilt_deg']:5.1f} deg peak {r['peak_torque_joint']} {r['peak_torque_fraction']:.0%}", flush=True)
    summary = {"policy": (policy_dir.resolve().relative_to(REPO).as_posix() if policy_dir.resolve().is_relative_to(REPO) else str(policy_dir)), "model": io["trained"]["source_mjcf"], "physics_dt_s": m.opt.timestep,
               "decimation": dec, "scenarios": results, "all_upright": not any(r["fell"] for r in results.values())}
    (policy_dir / "sim2sim.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    if frames:
        import PIL.Image
        ims = [PIL.Image.fromarray(f) for f in frames]
        ims[0].save(policy_dir / "sim2sim_walk.gif", save_all=True, append_images=ims[1:], duration=80, loop=0, optimize=True)
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default=str(RL_DIR / "policies" / "jx1_walk_flat"))
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    s = run(Path(a.policy), render=not a.no_render)
    print("all upright:", s["all_upright"])


if __name__ == "__main__":
    main()
