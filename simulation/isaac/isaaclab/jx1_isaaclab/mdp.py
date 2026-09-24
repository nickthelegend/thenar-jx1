"""JX1-specific Isaac Lab MDP terms, mirroring rl/jx1_rl/env.py (UNVERIFIED: no Isaac Sim on the design machine).

gait_phase (observation), contact/clock agreement, swing height, foot sliding, hip deviation, stand-still, ankle polygon
(rewards), a joint-position action that projects ankle targets into the collision-free polygon, and an event that holds
the non-policy joints at the default pose.
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


def contact_phase_match(env, period: float, offset: float, stance_fraction: float, sensor_cfg: SceneEntityCfg) -> torch.Tensor:
    stance = _leg_phase(env, period, offset) < stance_fraction
    return (_contact(env, sensor_cfg) == stance).float().sum(dim=1)


def feet_swing_height(env, target_height: float, sole_offset: float, sensor_cfg: SceneEntityCfg, asset_cfg: SceneEntityCfg) -> torch.Tensor:
    asset: Articulation = env.scene[asset_cfg.name]
    z = asset.data.body_pos_w[:, asset_cfg.body_ids, 2] - sole_offset
    return (((z - target_height) ** 2) * (~_contact(env, sensor_cfg)).float()).sum(dim=1)


def feet_contact_velocity(env, sensor_cfg: SceneEntityCfg, asset_cfg: SceneEntityCfg) -> torch.Tensor:
    asset: Articulation = env.scene[asset_cfg.name]
    v = asset.data.body_lin_vel_w[:, asset_cfg.body_ids, :]
    return ((v ** 2).sum(dim=-1) * _contact(env, sensor_cfg).float()).sum(dim=1)


def joint_deviation_l2(env, asset_cfg: SceneEntityCfg) -> torch.Tensor:
    asset: Articulation = env.scene[asset_cfg.name]
    d = asset.data.joint_pos[:, asset_cfg.joint_ids] - asset.data.default_joint_pos[:, asset_cfg.joint_ids]
    return (d ** 2).sum(dim=1)


def stand_still_deviation(env, command_name: str, asset_cfg: SceneEntityCfg) -> torch.Tensor:
    asset: Articulation = env.scene[asset_cfg.name]
    d = (asset.data.joint_pos[:, asset_cfg.joint_ids] - asset.data.default_joint_pos[:, asset_cfg.joint_ids]).abs().sum(dim=1)
    return d * (env.command_manager.get_command(command_name).norm(dim=1) < 0.1).float()


def ankle_polygon_violation(env, polygons_rad: dict, asset_cfg: SceneEntityCfg) -> torch.Tensor:
    asset: Articulation = env.scene[asset_cfg.name]
    names = asset.joint_names
    out = torch.zeros(env.num_envs, device=env.device)
    for side, poly in polygons_rad.items():
        ip, ir = names.index(f"{side}_ankle_pitch_joint"), names.index(f"{side}_ankle_roll_joint")
        p = asset.data.joint_pos[:, [ip, ir]]
        out += (p - project_to_polygon(p, torch.tensor(poly, device=env.device, dtype=p.dtype))).norm(dim=1)
    return out


def hold_default_pose(env, env_ids, asset_cfg: SceneEntityCfg):
    """Joints outside the policy keep their default position targets (the action term only writes the policy joints)."""
    asset: Articulation = env.scene[asset_cfg.name]
    ids = env_ids if env_ids is not None else slice(None)
    asset.set_joint_position_target(asset.data.default_joint_pos[ids][:, asset_cfg.joint_ids], joint_ids=asset_cfg.joint_ids, env_ids=env_ids)


class PolygonClippedJointPositionAction(JointPositionAction):
    """JointPositionAction + joint-limit clamp + ankle (pitch, roll) projection into the coupled polygon."""

    cfg: "PolygonClippedJointPositionActionCfg"

    def __init__(self, cfg, env):
        super().__init__(cfg, env)
        limits = self._asset.data.joint_pos_limits[0, self._joint_ids]
        self._lo, self._hi = limits[:, 0], limits[:, 1]
        names = list(self._joint_names)
        self._ankles = [(names.index(f"{s}_ankle_pitch_joint"), names.index(f"{s}_ankle_roll_joint"),
                         torch.tensor(p, device=self.device, dtype=torch.float32)) for s, p in cfg.polygons_rad.items()
                        if f"{s}_ankle_pitch_joint" in names]

    def process_actions(self, actions: torch.Tensor):
        super().process_actions(actions)
        p = torch.clamp(self._processed_actions, self._lo, self._hi)
        for ip, ir, poly in self._ankles:
            p[:, [ip, ir]] = project_to_polygon(p[:, [ip, ir]], poly)
        self._processed_actions = p


@configclass
class PolygonClippedJointPositionActionCfg(JointPositionActionCfg):
    class_type: type = PolygonClippedJointPositionAction
    polygons_rad: dict = {}
