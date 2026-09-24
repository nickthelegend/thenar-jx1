"""JX1 articulation for Isaac Lab (offline-checked by scripts/offline_check.py; Isaac Sim is not installed on the design machine).

Asset: simulation/isaac/jx1.usd when it exists (simulation/isaac/import_jx1.py), otherwise the CAD-derived URDF with
absolute mesh paths. Actuators are implicit PD drives with the deployment gains of rl/config/jx1_walk.yaml, the effort
and velocity limits of the actuator classes (URDF <limit>) and the rotor armature of the MJCF - the same numbers the
MuJoCo training uses.
"""
from __future__ import annotations

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg

from . import task_config

TC = task_config.load()
BASE_HEIGHT = TC["base_height"]
GROUPS = {"legs": ("hip_", "knee", "ankle_"), "waist": ("waist",), "arms": ("shoulder", "elbow"), "neck": ("neck",)}


def _spawn():
    rigid = sim_utils.RigidBodyPropertiesCfg(disable_gravity=False, retain_accelerations=False, linear_damping=0.0, angular_damping=0.0,
                                             max_linear_velocity=1000.0, max_angular_velocity=1000.0, max_depenetration_velocity=1.0)
    art = sim_utils.ArticulationRootPropertiesCfg(enabled_self_collisions=True, solver_position_iteration_count=8,
                                                  solver_velocity_iteration_count=4)
    if task_config.USD.exists():
        return sim_utils.UsdFileCfg(usd_path=str(task_config.USD), activate_contact_sensors=True, rigid_props=rigid, articulation_props=art)
    drive = sim_utils.UrdfConverterCfg.JointDriveCfg(gains=sim_utils.UrdfConverterCfg.JointDriveCfg.PDGainsCfg(stiffness=0.0, damping=0.0))
    return sim_utils.UrdfFileCfg(asset_path=str(task_config.urdf_with_absolute_meshes()), fix_base=False, merge_fixed_joints=True,
                                 make_instanceable=False, activate_contact_sensors=True, rigid_props=rigid, articulation_props=art,
                                 joint_drive=drive)


def _actuators():
    out = {}
    for group, keys in GROUPS.items():
        js = [j for j in TC["present"] if any(k in j for k in keys)]
        if not js:
            continue
        out[group] = ImplicitActuatorCfg(
            joint_names_expr=js,
            effort_limit_sim={j: TC["effort"].get(j, 100.0) for j in js},
            velocity_limit_sim={j: TC["velocity"].get(j, 20.0) for j in js},
            stiffness={j: TC["gains"][j][0] for j in js},
            damping={j: TC["gains"][j][1] for j in js},
            armature={j: TC["armature"].get(j, 0.01) for j in js},
        )
    return out


JX1_CFG = ArticulationCfg(
    spawn=_spawn(),
    init_state=ArticulationCfg.InitialStateCfg(pos=(0.0, 0.0, BASE_HEIGHT + 0.01),
                                               joint_pos={j: TC["default_pos"][j] for j in TC["present"]},
                                               joint_vel={".*": 0.0}),
    soft_joint_pos_limit_factor=0.9,
    actuators=_actuators(),
)
