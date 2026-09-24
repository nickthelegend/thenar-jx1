"""Export an Isaac Lab (rsl_rl) JX1 checkpoint to the deployment bundle without Isaac Sim: policy.onnx, policy.pt and
policy_io.yaml (schema jx1-policy-io/1, same as rl/export.py). A policy trained on any Isaac Lab machine then runs
unchanged in rl/sim2sim.py (MuJoCo CAD model) and in the ROS 2 node (jx1_policy).

  rl/.venv/Scripts/python simulation/isaac/isaaclab/scripts/export_offline.py \
      --checkpoint simulation/isaac/isaaclab/logs/jx1_flat/<run>/model_2999.pt --out rl/policies/jx1_walk_flat_isaac [--task rough]

Both checkpoint layouts are read:
  - rsl_rl >= 3 (Isaac Lab >= 2.3): the normaliser is inside the policy (model_state_dict actor_obs_normalizer.*).
  - rsl_rl 2.x (Isaac Lab <= 2.2): the runner normaliser is in obs_norm_state_dict.
The actor is rebuilt from the state dict: Linear layers with the configured activation between them. The normaliser is
rsl_rl's EmpiricalNormalization, (x - mean) / (std + eps) with eps = 1e-2. Only torch, onnx and onnxruntime are needed
(rl/.venv).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jx1_isaaclab import task_config  # noqa: E402  (plain Python: YAML/URDF only)

ACTIVATIONS = {"elu": torch.nn.ELU, "selu": torch.nn.SELU, "relu": torch.nn.ReLU, "lrelu": torch.nn.LeakyReLU, "tanh": torch.nn.Tanh,
               "sigmoid": torch.nn.Sigmoid, "softsign": torch.nn.Softsign, "identity": torch.nn.Identity}
RSL_RL_EPS = 1e-2                                            # rsl_rl EmpiricalNormalization default


class RslRlDeployPolicy(torch.nn.Module):
    """obs -> rsl_rl EmpiricalNormalization -> actor MLP -> action mean."""

    def __init__(self, layers, activation: str, mean: torch.Tensor, std: torch.Tensor, eps: float):
        super().__init__()
        mods = []
        for i, (w, b) in enumerate(layers):
            lin = torch.nn.Linear(w.shape[1], w.shape[0])
            with torch.no_grad():
                lin.weight.copy_(w)
                lin.bias.copy_(b)
            mods.append(lin)
            if i < len(layers) - 1:
                mods.append(ACTIVATIONS[activation]())
        self.actor = torch.nn.Sequential(*mods)
        self.register_buffer("mean", mean.reshape(1, -1).float())
        self.register_buffer("std", std.reshape(1, -1).float())
        self.eps = float(eps)

    def forward(self, obs):
        return self.actor((obs - self.mean) / (self.std + self.eps))


def load_policy(checkpoint: Path, num_actions: int, activation: str) -> tuple[RslRlDeployPolicy, dict]:
    ck = torch.load(checkpoint, map_location="cpu", weights_only=False)      # the user's own training output
    sd = ck["model_state_dict"]
    ids = sorted({int(k.split(".")[1]) for k in sd if k.startswith("actor.") and k.endswith(".weight")})
    if not ids:
        raise ValueError(f"{checkpoint}: no actor.*.weight in model_state_dict (not an rsl_rl ActorCritic checkpoint)")
    layers = [(sd[f"actor.{i}.weight"], sd[f"actor.{i}.bias"]) for i in ids]
    w, b = layers[-1]
    if w.shape[0] == 2 * num_actions:                                        # state-dependent std: rows = [mean, std]
        layers[-1] = (w[:num_actions], b[:num_actions])
    elif w.shape[0] != num_actions:
        raise ValueError(f"actor output {w.shape[0]} != {num_actions} policy joints")
    n_obs = layers[0][0].shape[1]
    if "actor_obs_normalizer._mean" in sd:
        mean, std, eps, fmt = sd["actor_obs_normalizer._mean"], sd["actor_obs_normalizer._std"], RSL_RL_EPS, "rsl_rl>=3 (policy normaliser)"
    elif ck.get("obs_norm_state_dict"):
        n = ck["obs_norm_state_dict"]
        mean, std, eps, fmt = n["_mean"], n["_std"], RSL_RL_EPS, "rsl_rl 2.x (runner normaliser)"
    else:
        mean, std, eps, fmt = torch.zeros(n_obs), torch.ones(n_obs), 0.0, "no observation normaliser"
    info = {"format": fmt, "iteration": ck.get("iter"), "num_obs": n_obs, "hidden": [int(x[0].shape[0]) for x in layers[:-1]]}
    return RslRlDeployPolicy(layers, activation, mean, std, eps).eval(), info


def export(checkpoint: Path, out: Path, task: str = "flat", task_id: str | None = None) -> dict:
    cfg_file = task_config.REPO / "rl" / "config" / ("jx1_walk_rough.yaml" if task == "rough" else "jx1_walk.yaml")
    tc = task_config.load(cfg_file)
    n = len(tc["policy_joints"])
    ppo = tc["raw"]["ppo"]
    pol, info = load_policy(checkpoint, n, ppo["activation"])
    if info["num_obs"] != 9 + 3 * n + 2:
        raise ValueError(f"checkpoint takes {info['num_obs']} observations, the JX1 task has {9 + 3 * n + 2}")
    out.mkdir(parents=True, exist_ok=True)
    dummy = torch.zeros(1, info["num_obs"])
    torch.jit.script(pol).save(str(out / "policy.pt"))
    torch.onnx.export(pol, (dummy,), str(out / "policy.onnx"), input_names=["obs"], output_names=["actions"],
                      dynamic_axes={"obs": {0: "batch"}, "actions": {0: "batch"}}, opset_version=18, dynamo=False)
    import onnxruntime as ort
    x = torch.randn(64, info["num_obs"]) * 2.0
    with torch.no_grad():
        y = pol(x).numpy()
    y_onnx = ort.InferenceSession(str(out / "policy.onnx")).run(["actions"], {"obs": x.numpy()})[0]
    y_ts = torch.jit.load(str(out / "policy.pt"))(x).detach().numpy()
    err = {"onnx_max_abs_diff": float(np.abs(y - y_onnx).max()), "torchscript_max_abs_diff": float(np.abs(y - y_ts).max())}
    meta = {"checkpoint": checkpoint.name, "run": checkpoint.parent.name, "trainer": "Isaac Lab + rsl_rl",
            "task": task_id or f"Isaac-Velocity-{task.capitalize()}-JX1-v0", "iteration": info["iteration"],
            "checkpoint_format": info["format"], "actor_hidden": info["hidden"],
            "task_config": cfg_file.relative_to(task_config.REPO).as_posix(),
            "source_urdf": task_config.URDF.relative_to(task_config.REPO).as_posix(), "export_check": err}
    io = task_config.policy_io(tc, meta)
    io["policy"]["torchscript"] = "policy.pt"
    (out / "policy_io.yaml").write_text(yaml.safe_dump(io, sort_keys=False, width=140), encoding="utf-8")
    if max(err.values()) > 1e-4:
        raise RuntimeError(f"exported policy does not match the checkpoint: {err}")
    return {"out": out.as_posix(), **info, **err}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--task", choices=["flat", "rough"], default="flat")
    a = ap.parse_args()
    print(json.dumps(export(a.checkpoint, a.out, a.task), indent=1))


if __name__ == "__main__":
    main()
