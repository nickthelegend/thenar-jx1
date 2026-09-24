"""JX1-specific Isaac Lab MDP terms, mirroring rl/jx1_rl/env.py. Checked offline by scripts/offline_check.py against
the Isaac Lab sources; never run in Isaac Sim (not installed on the design machine).

Observations: gait phase; critic-only base height, foot contact and sole heights.
Rewards: contact/clock agreement, swing height, foot sliding, hip deviation, stand-still, torque headroom, ankle polygon,
base height.
Termination: base height.
Action: joint position targets clamped to the joint limits, with the ankle (pitch, roll) projected into the
collision-free polygon, ramped over the policy period like the CAN hubs, with 0-1 substep transport delay.
Event: hold the non-policy joints at the default pose.

Heights are measured from the ground under the point. On flat ground that is z = 0. On rough ground it is the nearest
hit of the pelvis height scanner (ground_cfg), which matches the terrain-relative heights of the MuJoCo rough task.
"""
from __future__ import annotations

import math

import torch
from isaaclab.assets import Articulation
from isaaclab.envs.mdp.actions.actions_cfg import JointPositionActionCfg
from isaaclab.envs.mdp.actions.joint_actions import JointPositionAction
from isaaclab.managers import SceneEntityCfg
from isaaclab.sensors import ContactSensor
from isaaclab.utils import configclass
from isaaclab.utils.math import quat_apply

from .geometry import project_to_polygon


def _time(env):
    return env.episode_length_buf.float() * env.step_dt


def gait_phase(env, period: float) -> torch.Tensor:
    ph = torch.remainder(_time(env) / period, 1.0)
    return torch.stack([torch.sin(2 * math.pi * ph), torch.cos(2 * math.pi * ph)], dim=-1)


def _leg_phase(env, period, offset):
    ph = torch.remainder(_time(env) / period, 1.0)
    return torch.stack([ph, torch.remainder(ph + offset, 1.0)], dim=-1)


def _contact(env, sensor_cfg: SceneEntityCfg):
    sensor: ContactSensor = env.scene.sensors[sensor_cfg.name]
    return sensor.data.net_forces_w[:, sensor_cfg.body_ids, :].norm(dim=-1) > 1.0


def _ground_z(env, xy: torch.Tensor, ground_cfg: SceneEntityCfg | None) -> torch.Tensor:
    """Ground height under the points xy (N, P, 2): 0 without a height scanner, else its nearest ray hit."""
    if ground_cfg is None:
        return torch.zeros(xy.shape[:-1], device=xy.device)
    hits = env.scene.sensors[ground_cfg.name].data.ray_hits_w                      # (N, R, 3); inf where a ray missed
    hxy = torch.nan_to_num(hits[..., :2], nan=1e6, posinf=1e6, neginf=1e6)
    nearest = torch.cdist(xy, hxy).argmin(dim=-1)                                  # (N, P)
    z = torch.gather(hits[..., 2], 1, nearest)
    return torch.nan_to_num(z, nan=0.0, posinf=0.0, neginf=0.0)


def _sole_pos(asset: Articulation, body_ids, sole_offset) -> torch.Tensor:
    """World position of the sole points: foot link origin + foot rotation * sole offset (joint_map left_sole_fixed)."""
    pos, quat = asset.data.body_pos_w[:, body_ids], asset.data.body_quat_w[:, body_ids]
    off = torch.as_tensor(sole_offset, dtype=pos.dtype, device=pos.device).expand_as(pos)
    return pos + quat_apply(quat.reshape(-1, 4), off.reshape(-1, 3)).reshape(pos.shape)


def _base_height(env, asset_cfg: SceneEntityCfg, ground_cfg: SceneEntityCfg | None) -> torch.Tensor:
    asset: Articulation = env.scene[asset_cfg.name]
    root = asset.data.root_pos_w
    return root[:, 2] - _ground_z(env, root[:, None, :2], ground_cfg)[:, 0]


# ------------------------------------------------------------------------------------------------ observations
def base_height_above_target(env, target_height: float, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
                             ground_cfg: SceneEntityCfg | None = None) -> torch.Tensor:
    """Critic: base height above the ground minus the standing height (MuJoCo privileged obs, scale 5)."""
    return (_base_height(env, asset_cfg, ground_cfg) - target_height)[:, None]


def feet_contact_state(env, sensor_cfg: SceneEntityCfg) -> torch.Tensor:
    """Critic: foot contact flags (net force > 1 N, like the MuJoCo touch sensors)."""
    return _contact(env, sensor_cfg).float()


def feet_height(env, sole_offset, asset_cfg: SceneEntityCfg, ground_cfg: SceneEntityCfg | None = None) -> torch.Tensor:
    """Critic: sole heights above the ground (MuJoCo privileged obs, scale 10)."""
    sole = _sole_pos(env.scene[asset_cfg.name], asset_cfg.body_ids, sole_offset)
    return sole[..., 2] - _ground_z(env, sole[..., :2], ground_cfg)


# ------------------------------------------------------------------------------------------------ rewards
def contact_phase_match(env, period: float, offset: float, stance_fraction: float, sensor_cfg: SceneEntityCfg) -> torch.Tensor:
    stance = _leg_phase(env, period, offset) < stance_fraction
    return (_contact(env, sensor_cfg) == stance).float().sum(dim=1)


def feet_swing_height(env, target_height: float, sole_offset, sensor_cfg: SceneEntityCfg, asset_cfg: SceneEntityCfg,
                      ground_cfg: SceneEntityCfg | None = None) -> torch.Tensor:
    h = feet_height(env, sole_offset, asset_cfg, ground_cfg)
    return (((h - target_height) ** 2) * (~_contact(env, sensor_cfg)).float()).sum(dim=1)


def feet_contact_velocity(env, sensor_cfg: SceneEntityCfg, asset_cfg: SceneEntityCfg) -> torch.Tensor:
    asset: Articulation = env.scene[asset_cfg.name]
    v = asset.data.body_lin_vel_w[:, asset_cfg.body_ids, :]
    return ((v ** 2).sum(dim=-1) * _contact(env, sensor_cfg).float()).sum(dim=1)


def base_height_error(env, target_height: float, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
                      ground_cfg: SceneEntityCfg | None = None) -> torch.Tensor:
    return (_base_height(env, asset_cfg, ground_cfg) - target_height) ** 2


def joint_deviation_l2(env, asset_cfg: SceneEntityCfg) -> torch.Tensor:
    asset: Articulation = env.scene[asset_cfg.name]
    d = asset.data.joint_pos[:, asset_cfg.joint_ids] - asset.data.default_joint_pos[:, asset_cfg.joint_ids]
    return (d ** 2).sum(dim=1)


def stand_still_deviation(env, command_name: str, asset_cfg: SceneEntityCfg) -> torch.Tensor:
    asset: Articulation = env.scene[asset_cfg.name]
    d = (asset.data.joint_pos[:, asset_cfg.joint_ids] - asset.data.default_joint_pos[:, asset_cfg.joint_ids]).abs().sum(dim=1)
    return d * (env.command_manager.get_command(command_name).norm(dim=1) < 0.1).float()


def torque_limits(env, soft_ratio: float, asset_cfg: SceneEntityCfg) -> torch.Tensor:
    """Sum of |applied torque| above soft_ratio x effort limit (rl/jx1_rl/env.py 'torque_limits')."""
    asset: Articulation = env.scene[asset_cfg.name]
    tau = asset.data.applied_torque[:, asset_cfg.joint_ids].abs()
    lim = asset.data.joint_effort_limits[:, asset_cfg.joint_ids]
    return torch.clamp(tau - soft_ratio * lim, min=0.0).sum(dim=1)


def ankle_polygon_violation(env, polygons_rad: dict, asset_cfg: SceneEntityCfg) -> torch.Tensor:
    asset: Articulation = env.scene[asset_cfg.name]
    names = asset.joint_names
    out = torch.zeros(env.num_envs, device=env.device)
    for side, poly in polygons_rad.items():
        ip, ir = names.index(f"{side}_ankle_pitch_joint"), names.index(f"{side}_ankle_roll_joint")
        p = asset.data.joint_pos[:, [ip, ir]]
        out += (p - project_to_polygon(p, torch.tensor(poly, device=env.device, dtype=p.dtype))).norm(dim=1)
    return out


# ------------------------------------------------------------------------------------------------ terminations
def base_height_below(env, minimum_height: float, asset_cfg: SceneEntityCfg = SceneEntityCfg("robot"),
                      ground_cfg: SceneEntityCfg | None = None) -> torch.Tensor:
    return _base_height(env, asset_cfg, ground_cfg) < minimum_height


# ------------------------------------------------------------------------------------------------ events
def hold_default_pose(env, env_ids, asset_cfg: SceneEntityCfg):
    """Joints outside the policy keep their default position targets (the action term only writes the policy joints)."""
    asset: Articulation = env.scene[asset_cfg.name]
    ids = env_ids if env_ids is not None else slice(None)
    asset.set_joint_position_target(asset.data.default_joint_pos[ids][:, asset_cfg.joint_ids], joint_ids=asset_cfg.joint_ids, env_ids=env_ids)


# ------------------------------------------------------------------------------------------------ action
class PolygonClippedJointPositionAction(JointPositionAction):
    """JointPositionAction + joint-limit clamp + ankle (pitch, roll) projection into the coupled polygon, applied like
    the hardware: each new target ramps linearly from the previous one over the policy period (CAN hub first-order
    hold, firmware alpha). A per-env transport delay of d substeps holds the previous target for the first d
    substeps. After a reset the ramp starts from the default pose. This is the same pipeline as rl/jx1_rl/env.py step()."""

    cfg: "PolygonClippedJointPositionActionCfg"

    def __init__(self, cfg, env):
        super().__init__(cfg, env)
        limits = self._asset.data.joint_pos_limits[0, self._joint_ids]
        self._lo, self._hi = limits[:, 0], limits[:, 1]
        names = list(self._joint_names)
        self._ankles = [(names.index(f"{s}_ankle_pitch_joint"), names.index(f"{s}_ankle_roll_joint"),
                         torch.tensor(p, device=self.device, dtype=torch.float32)) for s, p in cfg.polygons_rad.items()
                        if f"{s}_ankle_pitch_joint" in names]
        self._hold = self._asset.data.default_joint_pos[:, self._joint_ids].clone()
        self._applied = self._hold.clone()
        self._from = self._hold.clone()
        self._substep = 0
        self._delay = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)

    def process_actions(self, actions: torch.Tensor):
        super().process_actions(actions)
        p = torch.clamp(self._processed_actions, self._lo, self._hi)
        for ip, ir, poly in self._ankles:
            p[:, [ip, ir]] = project_to_polygon(p[:, [ip, ir]], poly)
        self._processed_actions = p
        self._from = self._applied.clone()
        self._substep = 0

    def apply_actions(self):
        self._substep += 1
        alpha = min(1.0, self._substep / self._env.cfg.decimation) if self.cfg.hub_interpolation else 1.0
        ramp = self._from + alpha * (self._processed_actions - self._from)
        late = (self._delay >= self._substep)[:, None]
        self._applied = torch.where(late, self._from, ramp)
        self._asset.set_joint_position_target(self._applied, joint_ids=self._joint_ids)

    def reset(self, env_ids=None):
        super().reset(env_ids)
        ids = slice(None) if env_ids is None else env_ids
        self._applied[ids] = self._hold[ids]
        lo, hi = self.cfg.action_delay_substeps
        n = self.num_envs if env_ids is None else len(env_ids)
        self._delay[ids] = torch.randint(lo, hi + 1, (n,), device=self.device)


@configclass
class PolygonClippedJointPositionActionCfg(JointPositionActionCfg):
    class_type: type = PolygonClippedJointPositionAction
    polygons_rad: dict = {}
    hub_interpolation: bool = True
    action_delay_substeps: tuple = (0, 0)
