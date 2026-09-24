"""Push recovery of an EXPORTED policy on the full CAD model (same method as simulation/mujoco/push_jx1.py for the
model-based ZMP controller, so the two are comparable).

The policy walks at 0.5 m/s (or stands with --stand); after 4 s a horizontal 0.1 s force pulse hits the torso COM
(pelvis if the model has no torso body). The largest impulse (N s) survived without falling for the following 4 s is
found by bisection for pushes forward, backward, left and right. Deployment path: rl/sim2sim.Runner (ONNX +
policy_io.yaml), hub-style target ramp.
Output: <policy>/push_test.json
Usage: rl/.venv/Scripts/python rl/push_test.py [--policy rl/policies/jx1_walk_flat] [--stand]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import mujoco
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jx1_rl import RL_DIR, policy_io  # noqa: E402
from sim2sim import Runner, load_cad_model  # noqa: E402

DUR, T_PUSH, T_AFTER = 0.10, 4.0, 4.0
DIRECTIONS = {"forward": (1, 0, 0), "backward": (-1, 0, 0), "left": (0, 1, 0), "right": (0, -1, 0)}


def trial(rn, m, act_of, cmd, direction, impulse):
    io = rn.io
    d = mujoco.MjData(m)
    sole = [mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, f"{s}_sole") for s in ("left", "right")]
    jq = {j: m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, j)] for j in act_of}
    jd = {j: m.jnt_dofadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, j)] for j in act_of}
    for j, a in act_of.items():
        d.qpos[jq[j]] = d.ctrl[a] = io["default_joint_pos"].get(j, 0.0)
    d.qpos[2] = 1.0
    mujoco.mj_kinematics(m, d)
    d.qpos[2] = 1.0 - min(d.site_xpos[s][2] for s in sole) + 0.002
    mujoco.mj_forward(m, d)
    body = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "torso_link")
    body = body if body >= 0 else mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "pelvis")
    pol_q = np.array([jq[j] for j in rn.joints])
    pol_d = np.array([jd[j] for j in rn.joints])
    pol_a = np.array([act_of[j] for j in rn.joints])
    dt_pol = io["control"]["policy_dt_s"]
    dec = int(round(dt_pol / m.opt.timestep))
    rn.last_action[:] = 0.0
    force = np.array(direction, float) * impulse / DUR
    for _ in range(int((T_PUSH + T_AFTER) / dt_pol)):
        tgt = rn.targets(d.qpos[3:7].copy(), d.qvel[3:6].copy(), d.qpos[pol_q], d.qvel[pol_d], cmd, d.time)
        prev = d.ctrl[pol_a].copy()
        for i in range(dec):
            d.ctrl[pol_a] = prev + (i + 1) / dec * (tgt - prev)
            d.xfrc_applied[body, :3] = force if T_PUSH <= d.time < T_PUSH + DUR else 0.0
            mujoco.mj_step(m, d)
        g = policy_io.projected_gravity(d.qpos[3:7])
        if d.qpos[2] < 0.35 or -g[2] < np.cos(np.radians(60)):
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default=str(RL_DIR / "policies" / "jx1_walk_flat"))
    ap.add_argument("--stand", action="store_true")
    a = ap.parse_args()
    pdir = Path(a.policy)
    rn = Runner(pdir)
    m, act_of = load_cad_model(rn.io)
    cmd = (0.0, 0.0, 0.0) if a.stand else (0.5, 0.0, 0.0)
    res = {"policy": str(pdir), "command": cmd, "push_duration_s": DUR, "push_time_s": T_PUSH, "max_survived_impulse_Ns": {},
           "baseline_upright": trial(rn, m, act_of, cmd, (1, 0, 0), 0.0)}
    for tag, dvec in DIRECTIONS.items():
        lo, hi = 0.0, 60.0
        if trial(rn, m, act_of, cmd, dvec, hi):
            lo = hi
        while hi - lo > 0.5:
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if trial(rn, m, act_of, cmd, dvec, mid) else (lo, mid)
        res["max_survived_impulse_Ns"][tag] = round(lo, 2)
        print(f"{tag:8s} survives {lo:5.2f} N s", flush=True)
    mass = float(sum(m.body_mass))
    res["robot_mass_kg"] = round(mass, 2)
    res["equivalent_com_velocity_change_m_s"] = {k: round(v / mass, 3) for k, v in res["max_survived_impulse_Ns"].items()}
    (pdir / ("push_test_stand.json" if a.stand else "push_test.json")).write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(json.dumps(res["max_survived_impulse_Ns"]), "mass", res["robot_mass_kg"])


if __name__ == "__main__":
    main()
