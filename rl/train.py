"""Train the JX1 walking policy in MuJoCo (CPU-batched physics, PPO on the GPU if available).

Usage: rl/.venv/Scripts/python rl/train.py [--config rl/config/jx1_walk.yaml] [--num-envs 1024] [--iterations 3000]
                                         [--run NAME] [--resume rl/runs/NAME/model_XXXX.pt] [--seed 0] [--threads N]
Writes rl/runs/<run>/: model_<it>.pt checkpoints, metrics.csv, config copy. Export with rl/export.py.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jx1_rl import RL_DIR, config  # noqa: E402
from jx1_rl.env import JX1Env  # noqa: E402
from jx1_rl.ppo import PPO, ActorCritic, Storage  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(RL_DIR / "config" / "jx1_walk.yaml"))
    ap.add_argument("--num-envs", type=int)
    ap.add_argument("--iterations", type=int)
    ap.add_argument("--run", default=None)
    ap.add_argument("--resume", default=None)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--threads", type=int, default=None)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    a = ap.parse_args()
    cfg = config.load(a.config)
    pc = cfg["ppo"]
    N = a.num_envs or pc["num_envs"]
    iters = a.iterations or pc["max_iterations"]
    run = a.run or time.strftime(f"{cfg['name']}_%Y%m%d_%H%M%S")
    out = RL_DIR / "runs" / run
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy(a.config, out / "config.yaml")
    torch.manual_seed(a.seed)
    dev = torch.device(a.device)

    env = JX1Env(cfg, N, nthread=a.threads, seed=a.seed)
    ac = ActorCritic(cfg.num_obs, cfg.num_privileged_obs, cfg.num_actions, pc["actor_hidden"], pc["critic_hidden"],
                     pc["activation"], pc["init_noise_std"]).to(dev)
    ppo = PPO(ac, pc, dev)
    start = 0
    if a.resume:
        ck = torch.load(a.resume, map_location=dev)
        ac.load_state_dict(ck["model"])
        ppo.opt.load_state_dict(ck["optimizer"])
        ppo.lr = ck.get("lr", ppo.lr)
        start = ck["iteration"] + 1
    T = pc["num_steps_per_env"]
    st = Storage(T, N, cfg.num_obs, cfg.num_privileged_obs, cfg.num_actions, dev)
    (out / "run.json").write_text(json.dumps({"num_envs": N, "iterations": iters, "device": str(dev), "threads": env.nthread,
                                              "model_mass_kg": env.info["mass_kg"], "base_height_m": env.base_height_target,
                                              "policy_dt": env.dt, "variants": len(env.variants), "seed": a.seed}, indent=1))
    obs, priv = env.reset()
    obs_t, priv_t = torch.from_numpy(obs).to(dev), torch.from_numpy(priv).to(dev)
    metrics_f = open(out / "metrics.csv", "a", newline="", encoding="utf-8")
    ep_keys = [f"ep_{k}" for k, w in cfg["rewards"].items() if k not in ("tracking_sigma", "soft_torque_limit") and w != 0.0] + ["ep_length_s"]
    fields = ["iteration", "time_s", "fps", "collect_s", "update_s", "reward_per_step", "value_loss", "surrogate", "entropy", "kl", "lr",
              "std"] + ep_keys + ["unstable_resets"]
    writer = csv.DictWriter(metrics_f, fieldnames=fields, extrasaction="ignore")
    if metrics_f.tell() == 0:
        writer.writeheader()
    ep_hist = []
    t_start = time.time()
    for it in range(start, iters):
        t0 = time.time()
        ep_infos = []
        rew_sum = 0.0
        with torch.inference_mode():
            for _ in range(T):
                ac.obs_norm.update(obs_t)
                ac.priv_norm.update(priv_t)
                on, pn = ac.obs_norm(obs_t), ac.priv_norm(priv_t)
                dist = ac.distribution(on)
                act = dist.sample()
                logp = dist.log_prob(act).sum(-1)
                val = ac.value(pn)
                obs, priv, rew, done, info = env.step(act.cpu().numpy().astype(np.float64))
                r = torch.from_numpy(rew).to(dev)
                r += pc["gamma"] * val * torch.from_numpy(info["time_outs"]).to(dev)
                st.add(on, pn, act, r, torch.from_numpy(done).to(dev), val, logp, dist.mean, dist.stddev)
                obs_t, priv_t = torch.from_numpy(obs).to(dev), torch.from_numpy(priv).to(dev)
                rew_sum += float(rew.mean())
                if "episode" in info:
                    ep_infos.append(info["episode"])
            last_v = ac.value(ac.priv_norm(priv_t))
        st.compute_returns(last_v, pc["gamma"], pc["lam"])
        t_collect = time.time() - t0
        stats = ppo.update(st)
        t_iter = time.time() - t0
        ep = {k: float(np.mean([e[k] for e in ep_infos if k in e])) for k in (ep_infos[0] if ep_infos else {})}
        ep_hist.append(ep.get("length_s", 0.0))
        row = {"iteration": it, "time_s": round(time.time() - t_start, 1), "fps": round(T * N / t_iter),
               "collect_s": round(t_collect, 2), "update_s": round(t_iter - t_collect, 2), "reward_per_step": round(rew_sum / T, 5),
               **{k: round(v, 5) for k, v in stats.items()}, **{f"ep_{k}": round(v, 5) for k, v in ep.items()},
               "unstable_resets": env.unstable_resets}
        writer.writerow(row)
        metrics_f.flush()
        if it % 10 == 0 or it == iters - 1:
            print(f"it {it:5d} | {row['fps']:6d} sps | rew/step {row['reward_per_step']:+.4f} | ep len {ep.get('length_s', 0):5.1f} s | "
                  f"track v {ep.get('tracking_lin_vel', 0):.3f} w {ep.get('tracking_ang_vel', 0):.3f} | std {stats['std']:.3f} | "
                  f"lr {stats['lr']:.1e} | kl {stats['kl']:.4f} | {row['time_s']:.0f} s", flush=True)
        if (it + 1) % pc["save_interval"] == 0 or it == iters - 1:
            ck = {"model": ac.state_dict(), "optimizer": ppo.opt.state_dict(), "iteration": it, "lr": ppo.lr,
                  "config": str(Path(a.config).resolve()), "num_obs": cfg.num_obs, "num_privileged_obs": cfg.num_privileged_obs,
                  "num_actions": cfg.num_actions}
            torch.save(ck, out / f"model_{it + 1:05d}.pt")
            torch.save(ck, out / "model_latest.pt")
    metrics_f.close()
    print("done:", out)


if __name__ == "__main__":
    main()
