"""Isaac Sim + ROS 2 bridge for JX1 (sim-to-sim target for the ROS 2 policy node). Node types, attribute names/types and
the Python calls are checked against the Isaac Sim 5.1 sources by offline_check.py --isaacsim; never run (no Isaac Sim here).

Loads simulation/isaac/jx1.usd (simulation/isaac/import_jx1.py) standing at the default pose and sets the drive gains
of the policy bundle (policy_io.yaml pd_gains, the deployment gains). It adds a ground plane with the MuJoCo floor
friction and a pelvis IMU, and builds an action graph that speaks the same topics as the MuJoCo node (jx1_sim):
  publishes /clock, /jx1/joint_states, /jx1/imu, /jx1/odom (IsaacComputeOdometry)
  subscribes /jx1/joint_command (position targets by joint name)
Run with Isaac Sim's python:  ./python.sh simulation/isaac/isaaclab/scripts/ros2_bridge.py [--headless] [--policy <bundle>]
then:  ros2 launch jx1_bringup isaac_sim.launch.py
"""
import argparse
import sys
from pathlib import Path

from isaacsim import SimulationApp

parser = argparse.ArgumentParser()
parser.add_argument("--headless", action="store_true")
parser.add_argument("--policy", default=str(Path(__file__).resolve().parents[4] / "rl" / "policies" / "jx1_walk_stand_v7"))
args, _ = parser.parse_known_args()
app = SimulationApp({"headless": args.headless})

import numpy as np  # noqa: E402
import omni.graph.core as og  # noqa: E402
import usdrt.Sdf  # noqa: E402
import yaml  # noqa: E402
from isaacsim.core.api import World  # noqa: E402
from isaacsim.core.prims import SingleArticulation  # noqa: E402
from isaacsim.core.utils.extensions import enable_extension  # noqa: E402
from isaacsim.core.utils.stage import add_reference_to_stage  # noqa: E402

enable_extension("isaacsim.ros2.bridge")
app.update()
from isaacsim.sensors.physics import IMUSensor  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jx1_isaaclab import task_config  # noqa: E402

TC = task_config.load()
IO = yaml.safe_load((Path(args.policy) / "policy_io.yaml").read_text(encoding="utf-8"))
ROBOT = "/World/jx1"
world = World(stage_units_in_meters=1.0, physics_dt=TC["raw"]["model"]["timestep"], rendering_dt=0.02)
world.scene.add_default_ground_plane(static_friction=1.0, dynamic_friction=1.0, restitution=0.0)   # MuJoCo floor: mu 1, no bounce
add_reference_to_stage(usd_path=str(task_config.USD), prim_path=ROBOT)
robot = world.scene.add(SingleArticulation(prim_path=ROBOT, name="jx1", position=[0.0, 0.0, TC["base_height"] + 0.01]))
IMUSensor(prim_path=f"{ROBOT}/pelvis/imu", name="imu", translation=[0.0, 0.0, 0.05])

K = og.Controller.Keys
og.Controller.edit(
    {"graph_path": "/JX1Ros2", "evaluator_name": "execution"},
    {
        K.CREATE_NODES: [
            ("tick", "omni.graph.action.OnPlaybackTick"),
            ("context", "isaacsim.ros2.bridge.ROS2Context"),
            ("sim_time", "isaacsim.core.nodes.IsaacReadSimulationTime"),
            ("clock", "isaacsim.ros2.bridge.ROS2PublishClock"),
            ("joint_states", "isaacsim.ros2.bridge.ROS2PublishJointState"),
            ("joint_command", "isaacsim.ros2.bridge.ROS2SubscribeJointState"),
            ("articulation", "isaacsim.core.nodes.IsaacArticulationController"),
            ("read_imu", "isaacsim.sensors.physics.IsaacReadIMU"),
            ("imu", "isaacsim.ros2.bridge.ROS2PublishImu"),
            ("odometry", "isaacsim.core.nodes.IsaacComputeOdometry"),
            ("odom", "isaacsim.ros2.bridge.ROS2PublishOdometry"),
        ],
        K.CONNECT: [
            ("tick.outputs:tick", "clock.inputs:execIn"), ("tick.outputs:tick", "joint_states.inputs:execIn"),
            ("tick.outputs:tick", "joint_command.inputs:execIn"), ("tick.outputs:tick", "articulation.inputs:execIn"),
            ("tick.outputs:tick", "read_imu.inputs:execIn"), ("read_imu.outputs:execOut", "imu.inputs:execIn"),
            ("tick.outputs:tick", "odometry.inputs:execIn"), ("odometry.outputs:execOut", "odom.inputs:execIn"),
            ("context.outputs:context", "clock.inputs:context"), ("context.outputs:context", "joint_states.inputs:context"),
            ("context.outputs:context", "joint_command.inputs:context"), ("context.outputs:context", "imu.inputs:context"),
            ("context.outputs:context", "odom.inputs:context"),
            ("sim_time.outputs:simulationTime", "clock.inputs:timeStamp"), ("sim_time.outputs:simulationTime", "joint_states.inputs:timeStamp"),
            ("sim_time.outputs:simulationTime", "imu.inputs:timeStamp"), ("sim_time.outputs:simulationTime", "odom.inputs:timeStamp"),
            ("joint_command.outputs:jointNames", "articulation.inputs:jointNames"),
            ("joint_command.outputs:positionCommand", "articulation.inputs:positionCommand"),
            ("read_imu.outputs:angVel", "imu.inputs:angularVelocity"), ("read_imu.outputs:linAcc", "imu.inputs:linearAcceleration"),
            ("read_imu.outputs:orientation", "imu.inputs:orientation"),
            ("odometry.outputs:position", "odom.inputs:position"), ("odometry.outputs:orientation", "odom.inputs:orientation"),
            ("odometry.outputs:linearVelocity", "odom.inputs:linearVelocity"), ("odometry.outputs:angularVelocity", "odom.inputs:angularVelocity"),
        ],
        K.SET_VALUES: [
            # "target" inputs take a list of usdrt paths (Isaac Sim >= 4.5), not a string
            ("joint_states.inputs:topicName", "/jx1/joint_states"), ("joint_states.inputs:targetPrim", [usdrt.Sdf.Path(ROBOT)]),
            ("joint_command.inputs:topicName", "/jx1/joint_command"), ("articulation.inputs:robotPath", ROBOT),
            ("read_imu.inputs:imuPrim", [usdrt.Sdf.Path(f"{ROBOT}/pelvis/imu")]), ("read_imu.inputs:readGravity", True),
            ("imu.inputs:topicName", "/jx1/imu"), ("imu.inputs:frameId", "imu_link"),
            ("odometry.inputs:chassisPrim", [usdrt.Sdf.Path(f"{ROBOT}/pelvis")]),
            ("odom.inputs:topicName", "/jx1/odom"), ("odom.inputs:odomFrameId", "odom"), ("odom.inputs:chassisFrameId", "pelvis"),
        ],
    },
)
world.reset()
# stand at the default pose with the deployment PD gains (tensor API: SI units, N m/rad and N m s/rad)
names = robot.dof_names
default = np.array([IO["default_joint_pos"].get(n, 0.0) for n in names])
robot.set_joints_default_state(positions=default)
robot.set_joint_positions(default)
robot.get_articulation_controller().set_gains(kps=np.array([IO["pd_gains"][n][0] for n in names]),
                                              kds=np.array([IO["pd_gains"][n][1] for n in names]))
print(f"JX1 ROS 2 bridge running ({len(names)} joints, gains from {args.policy}); start: ros2 launch jx1_bringup isaac_sim.launch.py")
while app.is_running():
    world.step(render=not args.headless)
app.close()
