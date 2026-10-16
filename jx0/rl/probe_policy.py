"""Quick look at a JX0 checkpoint in the training environment (no noise, no randomisation): the velocity it actually
reaches for each test command, rather than the tracking reward that train.py prints (standing still scores ~0.5 there).

    rl/.venv/Scripts/python jx0/rl/probe_policy.py rl/runs/<run>/model_latest.pt
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "rl"))
from jx1_rl import config  # noqa: E402
from jx1_rl.env import JX1Env  # noqa: E402
from jx1_rl.ppo import ActorCritic  # noqa: E402

CMDS = np.array([[0.0, 0.0, 0.0], [0.05, 0.0, 0.0], [0.10, 0.0, 0.0], [-0.04, 0.0, 0.0], [0.0, 0.04, 0.0],
                 [0.0, -0.04, 0.0], [0.0, 0.0, 0.3], [0.0, 0.0, -0.3]])


def main():
    ck = torch.load(sys.argv[1], map_location="cpu")
    snap = Path(sys.argv[1]).parent / "config.yaml"
    cfg = config.load(snap if snap.exists() else ROOT / "jx0" / "rl" / "config" / "jx0_walk.yaml")
    pc = cfg["ppo"]
    ac = ActorCritic(ck["num_obs"], ck["num_privileged_obs"], ck["num_actions"], pc["actor_hidden"], pc["critic_hidden"], pc["activation"])
    ac.load_state_dict(ck["model"])
    ac.eval()
    n = len(CMDS)
    env = JX1Env(cfg, n, seed=0, randomize=False, nthread=4)
    env.reset_envs(np.arange(n))
    obs, _ = env.observations(noise=False)
    steps = int(8.0 / env.dt)
    for i in range(steps):
        env.commands[:] = CMDS
        with torch.no_grad():
            a = ac.actor(ac.obs_norm(torch.as_tensor(obs))).numpy()
        obs, _, _, done, _ = env.step(a)
        if i == int(2.0 / env.dt):
            p1, t1, h1 = env.qpos()[:, :2].copy(), env.state[:, 0].copy(), heading(env.qpos()[:, 3:7])
    p2, t2, h2 = env.qpos()[:, :2], env.state[:, 0], heading(env.qpos()[:, 3:7])
    T = (t2 - t1)
    d = p2 - p1
    vx = (np.cos(h1) * d[:, 0] + np.sin(h1) * d[:, 1]) / T
    vy = (-np.sin(h1) * d[:, 0] + np.cos(h1) * d[:, 1]) / T
    wz = np.angle(np.exp(1j * (h2 - h1))) / T
    print(f"iteration {ck['iteration'] + 1}")
    for c, x, y, w in zip(CMDS, vx, vy, wz):
        print(f"  cmd {c}  ->  vx {x:+.3f}  vy {y:+.3f}  wz {w:+.3f}")


def heading(q):
    w, x, y, z = q.T
    return np.arctan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))


if __name__ == "__main__":
    main()
