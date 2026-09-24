"""Isaac Lab rough-ground task for JX1 = rl/config/jx1_walk_rough.yaml (UNVERIFIED: no Isaac Sim on the design machine).

Same blind observation, actions (incl. ankle polygon and hub ramp), rewards and randomisation as the flat task; the
ground is Isaac Lab's terrain generator with sub-terrains matching the MuJoCo tiles: flat, uneven floor (+-noise_m),
pyramid slopes up to max_slope_deg and random boxes/steps up to max_step_m.
"""
from __future__ import annotations

import math

import isaaclab.terrains as terrain_gen
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


@configclass
class JX1RoughEnvCfg(JX1FlatEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.terrain.terrain_type = "generator"
        self.scene.terrain.terrain_generator = JX1_TERRAINS
        self.scene.terrain.max_init_terrain_level = None
        self.rewards.base_height_l2 = None           # absolute-height reward is wrong on terrain (MuJoCo uses height above ground)


@configclass
class JX1RoughEnvCfg_PLAY(JX1RoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.num_envs = 32
        self.observations.policy.enable_corruption = False
        self.events.push_robot = None
        self.events.base_external_force_torque = None
