"""Isaac Lab rough-ground task for JX1 = rl/config/jx1_walk_rough.yaml (checked offline, never run in Isaac Sim).

Same blind observation, actions (incl. ankle polygon, hub ramp and delay), rewards and randomisation as the flat task.
The ground is Isaac Lab's terrain generator with sub-terrains matching the MuJoCo tiles: flat, uneven floor
(+-noise_m), pyramid slopes up to max_slope_deg, and random boxes/steps up to max_step_m. A pelvis height scanner gives
the local ground height, so the base-height reward and termination, the swing-height reward and the critic's heights
are measured from the ground under the robot, as in the MuJoCo rough task. The policy never sees the scanner.
"""
from __future__ import annotations

import math

import isaaclab.terrains as terrain_gen
from isaaclab.managers import SceneEntityCfg
from isaaclab.sensors import RayCasterCfg, patterns
from isaaclab.terrains import TerrainGeneratorCfg
from isaaclab.utils import configclass

from .flat_env_cfg import JX1FlatEnvCfg
from .task_config import REPO, load

T = load(REPO / "rl" / "config" / "jx1_walk_rough.yaml")["raw"]["terrain"]

JX1_TERRAINS = TerrainGeneratorCfg(
    size=(T["tile_m"] * 4, T["tile_m"] * 4),
    border_width=10.0,
    num_rows=8,
    num_cols=8,
    horizontal_scale=T["resolution_m"],
    vertical_scale=0.005,
    slope_threshold=0.75,
    use_cache=False,
    sub_terrains={
        "flat": terrain_gen.MeshPlaneTerrainCfg(proportion=0.25),
        "uneven": terrain_gen.HfRandomUniformTerrainCfg(proportion=0.25, noise_range=(-T["noise_m"], T["noise_m"]), noise_step=0.005,
                                                        border_width=0.25),
        "slopes": terrain_gen.HfPyramidSlopedTerrainCfg(proportion=0.25, slope_range=(0.0, math.tan(math.radians(T["max_slope_deg"]))),
                                                        platform_width=2.0, border_width=0.25),
        "steps": terrain_gen.MeshRandomGridTerrainCfg(proportion=0.25, grid_width=0.4, grid_height_range=(0.0, T["max_step_m"]),
                                                      platform_width=2.0),
    },
)

GROUND = SceneEntityCfg("height_scanner")


@configclass
class JX1RoughEnvCfg(JX1FlatEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.terrain.terrain_type = "generator"
        self.scene.terrain.terrain_generator = JX1_TERRAINS
        self.scene.terrain.max_init_terrain_level = None
        # local ground under the pelvis and feet: 13 x 13 rays over 0.6 m, yaw-aligned (critic and rewards only)
        self.scene.height_scanner = RayCasterCfg(prim_path="{ENV_REGEX_NS}/Robot/pelvis", offset=RayCasterCfg.OffsetCfg(pos=(0.0, 0.0, 20.0)),
                                                 ray_alignment="yaw", pattern_cfg=patterns.GridPatternCfg(resolution=0.05, size=[0.6, 0.6]),
                                                 debug_vis=False, mesh_prim_paths=["/World/ground"])
        self.scene.height_scanner.update_period = self.decimation * self.sim.dt
        for term in (self.rewards.base_height_l2, self.rewards.feet_swing_height, self.terminations.base_height,
                     self.observations.critic.base_height, self.observations.critic.feet_height):
            term.params["ground_cfg"] = GROUND


@configclass
class JX1RoughEnvCfg_PLAY(JX1RoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.num_envs = 32
        self.observations.policy.enable_corruption = False
        self.events.push_robot = None
        self.events.base_external_force_torque = None
