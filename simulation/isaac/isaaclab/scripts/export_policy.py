"""Export an Isaac Lab-trained JX1 policy to the deployment bundle (policy.onnx + policy_io.yaml) from inside Isaac Sim.

export_offline.py does the same from the checkpoint alone (no Isaac Sim) and is the checked path; this script is the
Isaac Lab-native alternative (isaaclab_rl exporter).

  <IsaacLab>/isaaclab.sh -p simulation/isaac/isaaclab/scripts/export_policy.py --checkpoint logs/jx1_flat/<run>/model_3000.pt \
      --out rl/policies/jx1_walk_flat_isaac --headless
The bundle has the same schema as rl/export.py, so rl/sim2sim.py and the ROS 2 node (jx1_policy) run it unchanged.
"""
import argparse
import sys
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--task", default="Isaac-Velocity-Flat-JX1-Play-v0")
parser.add_argument("--checkpoint", required=True)
parser.add_argument("--out", required=True)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
app = AppLauncher(args).app

import gymnasium as gym  # noqa: E402
import yaml  # noqa: E402
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper, export_policy_as_onnx  # noqa: E402
from isaaclab_tasks.utils import parse_env_cfg  # noqa: E402
from isaaclab_tasks.utils.parse_cfg import load_cfg_from_registry  # noqa: E402
from rsl_rl.runners import OnPolicyRunner  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import jx1_isaaclab  # noqa: E402,F401
from jx1_isaaclab import task_config  # noqa: E402


def main():
    env_cfg = parse_env_cfg(args.task, device=args.device, num_envs=1)
    agent_cfg = load_cfg_from_registry(args.task, "rsl_rl_cfg_entry_point")
    env = RslRlVecEnvWrapper(gym.make(args.task, cfg=env_cfg))
    runner = OnPolicyRunner(env, agent_cfg.to_dict(), log_dir=None, device=args.device)
    runner.load(args.checkpoint)
    alg = runner.alg
    policy = getattr(alg, "policy", None) or getattr(alg, "actor_critic")        # rsl_rl >= 2.3 / older
    # observation normaliser: inside the policy for rsl_rl >= 3 (Isaac Lab >= 2.3), in the runner before. Exporting
    # without it would feed raw observations to a network trained on normalised ones.
    normalizer = getattr(policy, "actor_obs_normalizer", None) or getattr(runner, "obs_normalizer", None)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    export_policy_as_onnx(policy, normalizer=normalizer, path=str(out), filename="policy.onnx")
    meta = {"checkpoint": Path(args.checkpoint).name, "run": Path(args.checkpoint).parent.name, "trainer": "Isaac Lab + rsl_rl",
            "task": args.task, "source_urdf": task_config.URDF.relative_to(task_config.REPO).as_posix()}
    (out / "policy_io.yaml").write_text(yaml.safe_dump(task_config.policy_io(task_config.load(), meta), sort_keys=False, width=140),
                                        encoding="utf-8")
    print("exported", out)
    env.close()


if __name__ == "__main__":
    main()
    app.close()
