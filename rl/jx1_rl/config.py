"""Task configuration (rl/config/*.yaml) + robot facts from simulation/joint_map.yaml, resolved per joint."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import yaml

from . import REPO, RL_DIR


def joint_type(joint_name: str) -> str:
    """'left_hip_pitch_joint' -> 'hip_pitch'."""
    base = joint_name[:-len("_joint")] if joint_name.endswith("_joint") else joint_name
    for side in ("left_", "right_"):
        if base.startswith(side):
            return base[len(side):]
    return base


@dataclass
class TaskConfig:
    raw: dict
    joint_map: dict
    all_joints: list = field(default_factory=list)          # every actuated joint, joint_map order
    policy_joints: list = field(default_factory=list)
    default_pos: dict = field(default_factory=dict)          # joint -> rad (all joints)
    gains: dict = field(default_factory=dict)                # joint -> (kp, kd)
    limits: dict = field(default_factory=dict)               # joint -> (lower, upper) rad
    ankle_polygons: dict = field(default_factory=dict)       # 'left'/'right' -> (k, 2) rad (pitch, roll)
    hip_yaw_toe_out_max: float | None = None                 # rad: left_hip_yaw - right_hip_yaw <= this (OI-24)

    def __getitem__(self, k):
        return self.raw[k]

    @property
    def policy_dt(self) -> float:
        return self.raw["model"]["timestep"] * self.raw["model"]["decimation"]

    @property
    def num_actions(self) -> int:
        return len(self.policy_joints)

    @property
    def num_obs(self) -> int:
        return 9 + 3 * self.num_actions + 2

    @property
    def num_privileged_obs(self) -> int:
        return self.num_obs + 3 + 1 + 2 + 2          # + base lin vel, base height, foot contacts, foot heights

    def default_vector(self, joints=None) -> np.ndarray:
        return np.array([self.default_pos[j] for j in (joints or self.policy_joints)], dtype=np.float64)


def _merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in over.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_raw(path: str | Path) -> dict:
    """Task YAML; a `base: <file>` key inherits another task file (relative to this one) and deep-merges the rest."""
    path = Path(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if "base" in raw:
        raw = _merge(load_raw(path.parent / raw.pop("base")), raw)
    return raw


def load(path: str | Path = RL_DIR / "config" / "jx1_walk.yaml") -> TaskConfig:
    raw = load_raw(path)
    jm = yaml.safe_load((REPO / "simulation" / "joint_map.yaml").read_text(encoding="utf-8"))
    cfg = TaskConfig(raw=raw, joint_map=jm)
    cfg.all_joints = [j["name"] for j in jm["joints"]]
    cfg.policy_joints = list(raw["policy_joints"])
    unknown = [j for j in cfg.policy_joints if j not in cfg.all_joints]
    if unknown:
        raise ValueError(f"policy joints not in joint_map: {unknown}")
    for j in jm["joints"]:
        name = j["name"]
        cfg.limits[name] = (float(j["lower_rad"]), float(j["upper_rad"]))
        cfg.default_pos[name] = float(raw["default_joint_pos"].get(name, 0.0))
        kp, kd = raw["pd_gains"][joint_type(name)]
        cfg.gains[name] = (float(kp), float(kd))
        lo, hi = cfg.limits[name]
        if not lo <= cfg.default_pos[name] <= hi:
            raise ValueError(f"default position of {name} outside its limits")
    cl = jm.get("coupled_limits", {}).get("ankle_pitch_roll")
    if cl:
        for side in ("left", "right"):
            cfg.ankle_polygons[side] = np.radians(np.array(cl[f"{side}_polygon_deg"], dtype=np.float64))
    ty = jm.get("coupled_limits", {}).get("hip_yaw_toe_out")
    if ty:
        cfg.hip_yaw_toe_out_max = float(np.radians(ty["toe_out_sum_max_deg"]))
    return cfg
