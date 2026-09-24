"""Left/right mirror augmentation for rsl_rl's symmetry loss (RslRlSymmetryCfg.data_augmentation_func).

Same maps as the MuJoCo training (rl/jx1_rl/symmetry.py, loaded from the repository so both stacks mirror identically):
the policy group (47) and the critic group (55, the MuJoCo privileged layout) and the 12 leg actions. rsl_rl expects
[original; mirrored] along the batch dimension.
"""
from __future__ import annotations

import importlib.util

import torch

from .task_config import REPO, load

_MIRROR = None


def _mirror():
    global _MIRROR
    if _MIRROR is None:
        spec = importlib.util.spec_from_file_location("jx1_rl_symmetry", REPO / "rl" / "jx1_rl" / "symmetry.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        tc = load()
        n = len(tc["policy_joints"])
        _MIRROR = mod.Mirror(tc["policy_joints"], 9 + 3 * n + 2 + 8)
    return _MIRROR


def mirror_augmentation(env=None, obs=None, actions=None):
    m = _mirror()
    out_obs = out_act = None
    if obs is not None:
        mo = {k: (m.obs(v) if k == "policy" else m.priv(v) if k == "critic" else v) for k, v in obs.items()}
        if hasattr(obs, "batch_size"):                                         # tensordict.TensorDict (rsl_rl >= 3)
            out_obs = torch.cat([obs, type(obs)(mo, batch_size=obs.batch_size, device=obs.device)], dim=0)
        else:
            out_obs = {k: torch.cat([obs[k], mo[k]], dim=0) for k in obs.keys()}
    if actions is not None:
        out_act = torch.cat([actions, m.act(actions)], dim=0)
    return out_obs, out_act
