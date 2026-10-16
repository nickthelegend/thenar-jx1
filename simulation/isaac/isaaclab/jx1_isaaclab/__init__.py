"""JX1 / JX0 Isaac Lab tasks. Importing this package registers, for the robot of the active task config
(task_config.TASK_CONFIG: JX1 by default, JX0 with JX_TASK_CONFIG=jx0/rl/config/jx0_walk.yaml - scripts/train.py sets it
from the task name):
  Isaac-Velocity-Flat-JX1-v0 / -Play-v0, Isaac-Velocity-Rough-JX1-v0 / -Play-v0      (JX1)
  Isaac-Velocity-Flat-JX0-v0 / -Play-v0                                              (JX0, flat ground)
Import it after the Isaac Sim app is launched (see scripts/train.py).
"""
import gymnasium as gym

from .task_config import ROBOT

_TASKS = [("Flat", "flat_env_cfg", "FlatEnvCfg", "FlatPPORunnerCfg")]
if ROBOT == "jx1":
    _TASKS.append(("Rough", "rough_env_cfg", "RoughEnvCfg", "RoughPPORunnerCfg"))
for ground, module, env_cls, ppo_cls in _TASKS:
    for suffix, play in (("", ""), ("-Play", "_PLAY")):
        gym.register(
            id=f"Isaac-Velocity-{ground}-{ROBOT.upper()}{suffix}-v0",
            entry_point="isaaclab.envs:ManagerBasedRLEnv",
            disable_env_checker=True,
            kwargs={"env_cfg_entry_point": f"{__name__}.{module}:JX1{env_cls}{play}",
                    "rsl_rl_cfg_entry_point": f"{__name__}.agents.rsl_rl_ppo_cfg:JX1{ppo_cls}"},
        )
