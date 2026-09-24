"""Isaac Sim + ROS 2 bridge for JX1 (sim-to-sim target for the ROS 2 policy node), UNVERIFIED: no Isaac Sim here.

Loads simulation/isaac/jx1.usd (simulation/isaac/import_jx1.py; PD drive gains from import_config.yaml), adds a ground
plane and a pelvis IMU, and builds an action graph that speaks the same topics as the MuJoCo node (jx1_sim):
  publishes /clock, /jx1/joint_states, /jx1/imu      subscribes /jx1/joint_command (position targets)
Run with Isaac Sim's python (4.5 / 5.x node names):  ./python.sh simulation/isaac/isaaclab/scripts/ros2_bridge.py
then:  ros2 launch jx1_bringup isaac_sim.launch.py
"""
import sys
from pathlib import Path

from isaacsim import SimulationApp

app = SimulationApp({"headless": "--headless" in sys.argv})

import omni.graph.core as og  # noqa: E402
from isaacsim.core.api import World  # noqa: E402
from isaacsim.core.utils.extensions import enable_extension  # noqa: E402
from isaacsim.core.utils.stage import add_reference_to_stage  # noqa: E402

enable_extension("isaacsim.ros2.bridge")
app.update()
from isaacsim.sensors.physics import IMUSensor  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jx1_isaaclab import task_config  # noqa: E402

TC = task_config.load()
ROBOT = "/World/jx1"
world = World(stage_units_in_meters=1.0, physics_dt=TC["raw"]["model"]["timestep"], rendering_dt=0.02)
world.scene.add_default_ground_plane()
add_reference_to_stage(usd_path=str(task_config.USD), prim_path=ROBOT)
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
        ],
        K.CONNECT: [
            ("tick.outputs:tick", "clock.inputs:execIn"), ("tick.outputs:tick", "joint_states.inputs:execIn"),
            ("tick.outputs:tick", "joint_command.inputs:execIn"), ("tick.outputs:tick", "articulation.inputs:execIn"),
            ("tick.outputs:tick", "read_imu.inputs:execIn"), ("read_imu.outputs:execOut", "imu.inputs:execIn"),
            ("context.outputs:context", "clock.inputs:context"), ("context.outputs:context", "joint_states.inputs:context"),
            ("context.outputs:context", "joint_command.inputs:context"), ("context.outputs:context", "imu.inputs:context"),
            ("sim_time.outputs:simulationTime", "clock.inputs:timeStamp"), ("sim_time.outputs:simulationTime", "joint_states.inputs:timeStamp"),
            ("sim_time.outputs:simulationTime", "imu.inputs:timeStamp"),
            ("joint_command.outputs:jointNames", "articulation.inputs:jointNames"),
            ("joint_command.outputs:positionCommand", "articulation.inputs:positionCommand"),
            ("read_imu.outputs:angVel", "imu.inputs:angularVelocity"), ("read_imu.outputs:linAcc", "imu.inputs:linearAcceleration"),
            ("read_imu.outputs:orientation", "imu.inputs:orientation"),
        ],
        K.SET_VALUES: [
            ("joint_states.inputs:topicName", "/jx1/joint_states"), ("joint_states.inputs:targetPrim", ROBOT),
            ("joint_command.inputs:topicName", "/jx1/joint_command"), ("articulation.inputs:robotPath", ROBOT),
            ("read_imu.inputs:imuPrim", f"{ROBOT}/pelvis/imu"), ("read_imu.inputs:readGravity", True),
            ("imu.inputs:topicName", "/jx1/imu"), ("imu.inputs:frameId", "imu_link"),
        ],
    },
)
world.reset()
robot = world.stage.GetPrimAtPath(ROBOT)
print(f"JX1 ROS 2 bridge running ({robot.GetPath()}); start: ros2 launch jx1_bringup isaac_sim.launch.py")
while app.is_running():
    world.step(render=True)
app.close()
