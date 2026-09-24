"""JX1 Isaac Lab tasks. Importing this package registers:
  Isaac-Velocity-Flat-JX1-v0        training (4096 envs by default of the locomotion base config)
  Isaac-Velocity-Flat-JX1-Play-v0   evaluation (32 envs, no noise/pushes)
Import it after the Isaac Sim app is launched (see scripts/train.py).
"""
import gymnasium as gym

gym.register(
    id="Isaac-Velocity-Flat-JX1-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point": f"{__name__}.flat_env_cfg:JX1FlatEnvCfg",
            "rsl_rl_cfg_entry_point": f"{__name__}.agents.rsl_rl_ppo_cfg:JX1FlatPPORunnerCfg"},
)
gym.register(
    id="Isaac-Velocity-Flat-JX1-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point": f"{__name__}.flat_env_cfg:JX1FlatEnvCfg_PLAY",
            "rsl_rl_cfg_entry_point": f"{__name__}.agents.rsl_rl_ppo_cfg:JX1FlatPPORunnerCfg"},
)
