"""Isaac Lab flat-ground velocity task for JX1 = the MuJoCo task of rl/config/jx1_walk.yaml (UNVERIFIED here).

Observation layout, scales and noise, gait clock, actions (scale, default offset, ankle polygon), PD gains, rewards and
weights, terminations, commands and domain randomisation are all taken from rl/config/jx1_walk.yaml, so a policy trained
here runs through the same policy_io.yaml / ROS 2 node as the MuJoCo-trained one.
"""
from __future__ import annotations

import math

import isaaclab_tasks.manager_based.locomotion.velocity.mdp as mdp
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.utils import configclass
from isaaclab.utils.noise import AdditiveUniformNoiseCfg as Unoise
from isaaclab_tasks.manager_based.locomotion.velocity.velocity_env_cfg import LocomotionVelocityRoughEnvCfg

from . import mdp as jx1
from .robot import BASE_HEIGHT, JX1_CFG, TC

R = TC["raw"]
S, NZ, G, W, RND = R["observation"]["scales"], R["observation"]["noise"], R["gait"], R["rewards"], R["randomization"]
POLICY = TC["policy_joints"]
HELD = [j for j in TC["present"] if j not in POLICY]
FEET = ["left_foot_link", "right_foot_link"]
TRUNK = "torso_link" if "torso_link" in TC["links"] else "pelvis"
POLYGONS = {s: [[math.radians(a), math.radians(b)] for a, b in p] for s, p in TC["polygons_deg"].items()}
SOLE_OFFSET = 0.05          # foot-link origin (ankle roll axis) to sole, joint_map fixed frame left_sole_fixed
SIGMA = math.sqrt(W["tracking_sigma"])     # exp(-err^2 / sigma) in MuJoCo == exp(-err^2 / std^2) in Isaac Lab


def robot(joints=None, bodies=None):
    kw = {"preserve_order": True}
    if joints is not None:
        kw["joint_names"] = joints
    if bodies is not None:
        kw["body_names"] = bodies
    return SceneEntityCfg("robot", **kw)


@configclass
class JX1Observations:
    @configclass
    class PolicyCfg(ObsGroup):
        base_ang_vel = ObsTerm(func=mdp.base_ang_vel, scale=S["ang_vel"], noise=Unoise(n_min=-NZ["ang_vel"], n_max=NZ["ang_vel"]))
        projected_gravity = ObsTerm(func=mdp.projected_gravity, noise=Unoise(n_min=-NZ["gravity"], n_max=NZ["gravity"]))
        velocity_commands = ObsTerm(func=mdp.generated_commands, params={"command_name": "base_velocity"}, scale=tuple(S["commands"]))
        joint_pos = ObsTerm(func=mdp.joint_pos_rel, params={"asset_cfg": robot(POLICY)}, scale=S["dof_pos"],
                            noise=Unoise(n_min=-NZ["dof_pos"], n_max=NZ["dof_pos"]))
        joint_vel = ObsTerm(func=mdp.joint_vel_rel, params={"asset_cfg": robot(POLICY)}, scale=S["dof_vel"],
                            noise=Unoise(n_min=-NZ["dof_vel"], n_max=NZ["dof_vel"]))
        actions = ObsTerm(func=mdp.last_action)
        gait_phase = ObsTerm(func=jx1.gait_phase, params={"period": G["period_s"]})

        def __post_init__(self):
            self.enable_corruption = True
            self.concatenate_terms = True

    @configclass
    class CriticCfg(ObsGroup):
        base_ang_vel = ObsTerm(func=mdp.base_ang_vel, scale=S["ang_vel"])
        projected_gravity = ObsTerm(func=mdp.projected_gravity)
        velocity_commands = ObsTerm(func=mdp.generated_commands, params={"command_name": "base_velocity"}, scale=tuple(S["commands"]))
        joint_pos = ObsTerm(func=mdp.joint_pos_rel, params={"asset_cfg": robot(POLICY)}, scale=S["dof_pos"])
        joint_vel = ObsTerm(func=mdp.joint_vel_rel, params={"asset_cfg": robot(POLICY)}, scale=S["dof_vel"])
        actions = ObsTerm(func=mdp.last_action)
        gait_phase = ObsTerm(func=jx1.gait_phase, params={"period": G["period_s"]})
        base_lin_vel = ObsTerm(func=mdp.base_lin_vel, scale=S["lin_vel"])

        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = True

    policy: PolicyCfg = PolicyCfg()
    critic: CriticCfg = CriticCfg()


@configclass
class JX1Actions:
    joint_pos = jx1.PolygonClippedJointPositionActionCfg(asset_name="robot", joint_names=POLICY, scale=R["action_scale"],
                                                         use_default_offset=True, preserve_order=True, polygons_rad=POLYGONS)


@configclass
class JX1Rewards:
    track_lin_vel_xy_exp = RewTerm(func=mdp.track_lin_vel_xy_exp, weight=W["tracking_lin_vel"], params={"command_name": "base_velocity", "std": SIGMA})
    track_ang_vel_z_exp = RewTerm(func=mdp.track_ang_vel_z_exp, weight=W["tracking_ang_vel"], params={"command_name": "base_velocity", "std": SIGMA})
    lin_vel_z_l2 = RewTerm(func=mdp.lin_vel_z_l2, weight=W["lin_vel_z"])
    ang_vel_xy_l2 = RewTerm(func=mdp.ang_vel_xy_l2, weight=W["ang_vel_xy"])
    flat_orientation_l2 = RewTerm(func=mdp.flat_orientation_l2, weight=W["orientation"])
    base_height_l2 = RewTerm(func=mdp.base_height_l2, weight=W["base_height"], params={"target_height": BASE_HEIGHT})
    dof_torques_l2 = RewTerm(func=mdp.joint_torques_l2, weight=W["torques"], params={"asset_cfg": robot(POLICY)})
    torque_limits = RewTerm(func=jx1.torque_limits, weight=W.get("torque_limits", 0.0),
                            params={"soft_ratio": W.get("soft_torque_limit", 0.85), "asset_cfg": robot(POLICY)})
    dof_vel_l2 = RewTerm(func=mdp.joint_vel_l2, weight=W["dof_vel"], params={"asset_cfg": robot(POLICY)})
    dof_acc_l2 = RewTerm(func=mdp.joint_acc_l2, weight=W["dof_acc"], params={"asset_cfg": robot(POLICY)})
    action_rate_l2 = RewTerm(func=mdp.action_rate_l2, weight=W["action_rate"])
    dof_pos_limits = RewTerm(func=mdp.joint_pos_limits, weight=W["dof_pos_limits"], params={"asset_cfg": robot(POLICY)})
    ankle_polygon = RewTerm(func=jx1.ankle_polygon_violation, weight=W["dof_pos_limits"], params={"polygons_rad": POLYGONS, "asset_cfg": robot()})
    alive = RewTerm(func=mdp.is_alive, weight=W["alive"])
    hip_pos = RewTerm(func=jx1.joint_deviation_l2, weight=W["hip_pos"],
                      params={"asset_cfg": robot([j for j in POLICY if "hip_roll" in j or "hip_yaw" in j])})
    contact = RewTerm(func=jx1.contact_phase_match, weight=W["contact"],
                      params={"period": G["period_s"], "offset": G["offset"], "stance_fraction": G["stance_fraction"],
                              "sensor_cfg": SceneEntityCfg("contact_forces", body_names=FEET, preserve_order=True)})
    feet_swing_height = RewTerm(func=jx1.feet_swing_height, weight=W["feet_swing_height"],
                                params={"target_height": G["swing_height_m"], "sole_offset": SOLE_OFFSET,
                                        "sensor_cfg": SceneEntityCfg("contact_forces", body_names=FEET, preserve_order=True),
                                        "asset_cfg": robot(bodies=FEET)})
    contact_no_vel = RewTerm(func=jx1.feet_contact_velocity, weight=W["contact_no_vel"],
                             params={"sensor_cfg": SceneEntityCfg("contact_forces", body_names=FEET, preserve_order=True),
                                     "asset_cfg": robot(bodies=FEET)})
    stand_still = RewTerm(func=jx1.stand_still_deviation, weight=W["stand_still"], params={"command_name": "base_velocity", "asset_cfg": robot(POLICY)})
    termination = RewTerm(func=mdp.is_terminated, weight=W["termination"])


@configclass
class JX1Terminations:
    time_out = DoneTerm(func=mdp.time_out, time_out=True)
    base_height = DoneTerm(func=mdp.root_height_below_minimum, params={"minimum_height": R["termination"]["min_base_height_m"]})
    bad_orientation = DoneTerm(func=mdp.bad_orientation, params={"limit_angle": math.radians(R["termination"]["max_tilt_deg"])})


@configclass
class JX1FlatEnvCfg(LocomotionVelocityRoughEnvCfg):
    observations: JX1Observations = JX1Observations()
    actions: JX1Actions = JX1Actions()
    rewards: JX1Rewards = JX1Rewards()
    terminations: JX1Terminations = JX1Terminations()

    def __post_init__(self):
        super().__post_init__()
        self.scene.robot = JX1_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
        self.scene.terrain.terrain_type = "plane"
        self.scene.terrain.terrain_generator = None
        self.scene.height_scanner = None
        self.curriculum.terrain_levels = None
        self.sim.dt = R["model"]["timestep"]
        self.decimation = R["model"]["decimation"]
        self.sim.render_interval = self.decimation
        self.episode_length_s = R["episode_s"]
        self.scene.contact_forces.update_period = self.sim.dt
        # commands
        c, rng = self.commands.base_velocity, R["commands"]["ranges"]
        c.resampling_time_range = (R["commands"]["resample_s"], R["commands"]["resample_s"])
        c.rel_standing_envs = R["commands"]["zero_fraction"]
        c.heading_command = False
        c.rel_heading_envs = 0.0
        c.ranges.lin_vel_x, c.ranges.lin_vel_y, c.ranges.ang_vel_z = tuple(rng["lin_vel_x"]), tuple(rng["lin_vel_y"]), tuple(rng["ang_vel_yaw"])
        # domain randomisation (rl/config randomization)
        ev = self.events
        ev.physics_material.params["static_friction_range"] = tuple(RND["friction"])
        ev.physics_material.params["dynamic_friction_range"] = tuple(RND["friction"])
        ev.add_base_mass.params["asset_cfg"] = SceneEntityCfg("robot", body_names=TRUNK)
        ev.add_base_mass.params["mass_distribution_params"] = tuple(RND["added_base_mass_kg"])
        if hasattr(ev, "base_com") and ev.base_com is not None:
            o = RND["base_com_offset_m"]
            ev.base_com.params["asset_cfg"] = SceneEntityCfg("robot", body_names=TRUNK)
            ev.base_com.params["com_range"] = {"x": (-o, o), "y": (-o, o), "z": (-o, o)}
        ev.base_external_force_torque.params["asset_cfg"] = SceneEntityCfg("robot", body_names="pelvis")
        ev.reset_base.params = {"pose_range": {"x": (-0.5, 0.5), "y": (-0.5, 0.5), "yaw": (-math.pi, math.pi)},
                                "velocity_range": {k: (-RND["init_base_vel"], RND["init_base_vel"]) for k in ("x", "y", "z", "roll", "pitch", "yaw")}}
        ev.reset_robot_joints = EventTerm(func=mdp.reset_joints_by_offset, mode="reset",
                                          params={"position_range": (-RND["init_joint_noise"], RND["init_joint_noise"]), "velocity_range": (0.0, 0.0),
                                                  "asset_cfg": robot(POLICY)})
        ev.push_robot.interval_range_s = (RND["push_interval_s"], RND["push_interval_s"])
        v = RND["push_velocity_m_s"]
        ev.push_robot.params = {"velocity_range": {"x": (-v, v), "y": (-v, v)}}
        ev.actuator_gains = EventTerm(func=mdp.randomize_actuator_gains, mode="reset",
                                      params={"asset_cfg": robot(POLICY), "stiffness_distribution_params": tuple(RND["kp_scale"]),
                                              "damping_distribution_params": tuple(RND["kd_scale"]), "operation": "scale"})
        ev.link_masses = EventTerm(func=mdp.randomize_rigid_body_mass, mode="startup",
                                   params={"asset_cfg": SceneEntityCfg("robot", body_names=".*"),
                                           "mass_distribution_params": tuple(RND["link_mass_scale"]), "operation": "scale"})
        if HELD:
            ev.hold_default_pose = EventTerm(func=jx1.hold_default_pose, mode="reset", params={"asset_cfg": robot(HELD)})


@configclass
class JX1FlatEnvCfg_PLAY(JX1FlatEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.scene.num_envs = 32
        self.scene.env_spacing = 2.5
        self.observations.policy.enable_corruption = False
        self.events.push_robot = None
        self.events.base_external_force_torque = None
