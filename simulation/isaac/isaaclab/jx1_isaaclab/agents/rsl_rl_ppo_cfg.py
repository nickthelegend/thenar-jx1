"""rsl_rl PPO settings for JX1 = rl/config/jx1_walk.yaml 'ppo' (same algorithm and hyperparameters as rl/train.py)."""
from isaaclab.utils import configclass
from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg, RslRlPpoActorCriticCfg, RslRlPpoAlgorithmCfg

from ..symmetry import mirror_augmentation
from ..task_config import load

try:
    from isaaclab_rl.rsl_rl import RslRlSymmetryCfg
except ImportError:                                  # Isaac Lab < 2.2
    RslRlSymmetryCfg = None

P = load()["raw"]["ppo"]


@configclass
class JX1FlatPPORunnerCfg(RslRlOnPolicyRunnerCfg):
    num_steps_per_env = P["num_steps_per_env"]
    max_iterations = P["max_iterations"]
    save_interval = P["save_interval"]
    experiment_name = "jx1_flat"
    obs_groups = {"policy": ["policy"], "critic": ["critic"]}      # asymmetric actor-critic (rl/train.py: obs / privileged obs)
    clip_actions = 100.0                                           # rl/jx1_rl/env.py clips raw actions to +-100
    empirical_normalization = True
    policy = RslRlPpoActorCriticCfg(init_noise_std=P["init_noise_std"], actor_hidden_dims=P["actor_hidden"],
                                    critic_hidden_dims=P["critic_hidden"], activation=P["activation"])
    algorithm = RslRlPpoAlgorithmCfg(value_loss_coef=P["value_loss_coef"], use_clipped_value_loss=True, clip_param=P["clip_param"],
                                     entropy_coef=P["entropy_coef"], num_learning_epochs=P["num_learning_epochs"],
                                     num_mini_batches=P["num_mini_batches"], learning_rate=P["learning_rate"], schedule=P["schedule"],
                                     gamma=P["gamma"], lam=P["lam"], desired_kl=P["desired_kl"], max_grad_norm=P["max_grad_norm"])

    def __post_init__(self):
        # Isaac Lab >= 2.3 (rsl_rl >= 3) normalises observations inside the policy; the runner flag is deprecated there.
        # Older Isaac Lab (rsl_rl 2.x) has no policy-side flags and uses the runner's empirical_normalization.
        if hasattr(self.policy, "actor_obs_normalization"):
            self.policy.actor_obs_normalization = True
            self.policy.critic_obs_normalization = True
            self.empirical_normalization = None
        # left/right mirror loss, as rl/train.py (ppo.symmetry_coef); rsl_rl >= 2.3 symmetry support
        if P.get("symmetry_coef", 0.0) > 0 and RslRlSymmetryCfg is not None and hasattr(self.algorithm, "symmetry_cfg"):
            self.algorithm.symmetry_cfg = RslRlSymmetryCfg(use_data_augmentation=False, use_mirror_loss=True,
                                                           mirror_loss_coeff=P["symmetry_coef"], data_augmentation_func=mirror_augmentation)


@configclass
class JX1RoughPPORunnerCfg(JX1FlatPPORunnerCfg):
    experiment_name = "jx1_rough"
