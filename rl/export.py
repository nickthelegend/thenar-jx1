"""Export a trained JX1 policy for deployment: TorchScript + ONNX (normaliser baked in) + policy_io.yaml.

policy_io.yaml carries every convention the runtime needs (joint order, default pose, PD gains, effort/joint limits,
ankle polygon, action scale, observation layout/scales, gait clock, control rate), so the ROS 2 node, the sim-to-sim
check and Isaac Lab play-back need nothing from the training code.
Usage: rl/.venv/Scripts/python rl/export.py --checkpoint rl/runs/<run>/model_latest.pt [--out rl/policies/jx1_walk_flat]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import mujoco
import numpy as np
import torch
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jx1_rl import REPO, RL_DIR, config  # noqa: E402
from jx1_rl.ppo import ActorCritic  # noqa: E402

OBS_LAYOUT = ["base_ang_vel_body x3 (rad/s) * scales.ang_vel", "projected_gravity_body x3", "command (vx m/s, vy m/s, wz rad/s) * scales.commands",
              "joint_pos - default (policy joints) * scales.dof_pos", "joint_vel (policy joints) * scales.dof_vel",
              "last_action (raw policy output)", "sin(2 pi phase)", "cos(2 pi phase)"]


class DeployPolicy(torch.nn.Module):
    def __init__(self, ac: ActorCritic):
        super().__init__()
        self.norm = ac.obs_norm
        self.actor = ac.actor

    def forward(self, obs):
        return self.actor(self.norm(obs))


# peak torque (N m) by joint_map actuator_class when a joint is not in the exported MJCF (ankle = linkage capability)
CLASS_EFFORT = {"XL": 120.0, "L": 60.0, "M": 36.0, "S": 17.0, "XS": 14.0, "servo": 1.9}
ANKLE_EFFORT = {"ankle_pitch": 46.0, "ankle_roll": 51.0}


def class_effort(cfg, joint):
    jt = config.joint_type(joint)
    if jt in ANKLE_EFFORT:
        return ANKLE_EFFORT[jt]
    cls = next(j["actuator_class"] for j in cfg.joint_map["joints"] if j["name"] == joint)
    return CLASS_EFFORT[cls.split()[0]]


def policy_io(cfg, meta):
    """The deployment contract describes the whole robot (all joint_map joints), whatever the exported MJCF models."""
    src = REPO / cfg["model"]["source_mjcf"]
    m = mujoco.MjModel.from_xml_path(str(src))
    effort = {}
    for a in range(m.nu):
        j = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, m.actuator_trnid[a, 0])
        effort[j] = float(m.actuator_forcerange[a, 1])
    present = list(cfg.all_joints)
    for j in present:
        effort.setdefault(j, class_effort(cfg, j))
    return {
        "format": "jx1-policy-io/1",
        "policy": {"onnx": "policy.onnx", "torchscript": "policy.pt", "input": "obs", "output": "actions",
                   "num_obs": cfg.num_obs, "num_actions": cfg.num_actions},
        "control": {"policy_dt_s": cfg.policy_dt, "trained_physics_dt_s": cfg["model"]["timestep"], "trained_decimation": cfg["model"]["decimation"]},
        "joints": {"policy": cfg.policy_joints, "held": [j for j in present if j not in cfg.policy_joints]},
        "default_joint_pos": {j: cfg.default_pos[j] for j in present},
        "action_scale": cfg["action_scale"],
        "pd_gains": {j: list(cfg.gains[j]) for j in present},
        "effort_limits_Nm": {j: effort[j] for j in present},
        "joint_limits_rad": {j: list(cfg.limits[j]) for j in present},
        "ankle_polygons_rad": {s: np.round(p, 6).tolist() for s, p in cfg.ankle_polygons.items()},
        "observation": {"size": cfg.num_obs, "layout": OBS_LAYOUT, "scales": cfg["observation"]["scales"], "clip": cfg["observation"]["clip"]},
        "gait": cfg["gait"],
        "commands": cfg["commands"]["ranges"],
        "targets": "q_target = clip(default + action_scale * action, joint limits); ankle (pitch, roll) targets projected into ankle_polygons_rad",
        "trained": meta,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--out", default=str(RL_DIR / "policies" / "jx1_walk_flat"))
    a = ap.parse_args()
    ck = torch.load(a.checkpoint, map_location="cpu")
    snapshot = Path(a.checkpoint).parent / "config.yaml"          # the task config the run was trained with
    cfg = config.load(snapshot if snapshot.exists() else (ck.get("config") or RL_DIR / "config" / "jx1_walk.yaml"))
    pc = cfg["ppo"]
    ac = ActorCritic(ck["num_obs"], ck["num_privileged_obs"], ck["num_actions"], pc["actor_hidden"], pc["critic_hidden"], pc["activation"])
    ac.load_state_dict(ck["model"])
    ac.eval()
    pol = DeployPolicy(ac).eval()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    dummy = torch.zeros(1, ck["num_obs"])
    torch.jit.script(pol).save(str(out / "policy.pt"))
    torch.onnx.export(pol, (dummy,), str(out / "policy.onnx"), input_names=["obs"], output_names=["actions"],
                      dynamic_axes={"obs": {0: "batch"}, "actions": {0: "batch"}}, opset_version=18, dynamo=False)
    # numerical check: torch vs onnxruntime vs torchscript
    import onnxruntime as ort
    x = torch.randn(64, ck["num_obs"])
    with torch.no_grad():
        y = pol(x).numpy()
    y_onnx = ort.InferenceSession(str(out / "policy.onnx")).run(["actions"], {"obs": x.numpy()})[0]
    y_ts = torch.jit.load(str(out / "policy.pt"))(x).detach().numpy()
    err = {"onnx_max_abs_diff": float(np.abs(y - y_onnx).max()), "torchscript_max_abs_diff": float(np.abs(y - y_ts).max())}
    src = REPO / cfg["model"]["source_mjcf"]
    meta = {"checkpoint": Path(a.checkpoint).name, "run": Path(a.checkpoint).parent.name, "iteration": ck["iteration"] + 1,
            "task_config": "run snapshot (config.yaml next to the checkpoint)" if snapshot.exists() else "rl/config (no run snapshot)",
            "source_mjcf": cfg["model"]["source_mjcf"], "source_mjcf_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
            "export_check": err}
    (out / "policy_io.yaml").write_text(yaml.safe_dump(policy_io(cfg, meta), sort_keys=False, width=140), encoding="utf-8")
    print(json.dumps(err), "->", out)
    if max(err.values()) > 1e-4:
        sys.exit("exported policy does not match the checkpoint")


if __name__ == "__main__":
    main()
