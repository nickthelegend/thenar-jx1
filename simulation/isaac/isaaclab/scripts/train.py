"""Train JX1 in Isaac Lab with rsl_rl (offline-checked against Isaac Lab 2.3.2 by offline_check.py; not run in Isaac Sim here).

  <IsaacLab>/isaaclab.sh -p simulation/isaac/isaaclab/scripts/train.py --task Isaac-Velocity-Flat-JX1-v0 --headless [--num_envs 4096]
Logs and checkpoints: simulation/isaac/isaaclab/logs/jx1_flat/<time>/model_<it>.pt
Deployment bundle: scripts/export_offline.py --checkpoint <model.pt> --out rl/policies/<name> (no Isaac Sim needed)
"""
import argparse
import sys
import time
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Train JX1 with rsl_rl")
parser.add_argument("--task", default="Isaac-Velocity-Flat-JX1-v0")
parser.add_argument("--num_envs", type=int, default=None)
parser.add_argument("--max_iterations", type=int, default=None)
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--resume", default=None, help="checkpoint to continue from")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
app = AppLauncher(args).app

import gymnasium as gym  # noqa: E402
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper  # noqa: E402
from isaaclab_tasks.utils import parse_env_cfg  # noqa: E402
from isaaclab_tasks.utils.parse_cfg import load_cfg_from_registry  # noqa: E402
from rsl_rl.runners import OnPolicyRunner  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import jx1_isaaclab  # noqa: E402,F401  (registers the JX1 tasks)


def main():
    env_cfg = parse_env_cfg(args.task, device=args.device, num_envs=args.num_envs)
    agent_cfg = load_cfg_from_registry(args.task, "rsl_rl_cfg_entry_point")
    if args.max_iterations:
        agent_cfg.max_iterations = args.max_iterations
    agent_cfg.seed = env_cfg.seed = args.seed
    agent_cfg.device = args.device
    log_dir = Path(__file__).resolve().parents[1] / "logs" / agent_cfg.experiment_name / time.strftime("%Y-%m-%d_%H-%M-%S")
    env = RslRlVecEnvWrapper(gym.make(args.task, cfg=env_cfg), clip_actions=agent_cfg.clip_actions)
    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=str(log_dir), device=agent_cfg.device)
    if args.resume:
        runner.load(args.resume)
    runner.learn(num_learning_iterations=agent_cfg.max_iterations, init_at_random_ep_len=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()
