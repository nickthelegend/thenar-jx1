"""JX1 on hardware (Jetson): CAN-hub bridge + walking policy + robot_state_publisher.

  ros2 launch jx1_hw hardware.launch.py port_a:=/dev/ttyACM0 port_b:=/dev/ttyACM1
  ros2 service call /jx1/hw/run std_srvs/srv/Trigger          # enable (robot on the gantry!), hubs leave DAMPING
  ros2 service call /jx1/hw/damp std_srvs/srv/Trigger         # back to damping
The pelvis IMU (BNO085) is read by jx1_hw imu_node (imu:=true, default) and published on /jx1/imu.
hil:=true starts the MuJoCo hub emulator instead of real hubs (no hardware); the emulator publishes /jx1/imu itself.
"""
from pathlib import Path

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def setup(context):
    def get(k):
        return LaunchConfiguration(k).perform(context)
    policy_dir = get("policy_dir") or str(Path(get_package_share_directory("jx1_policy")) / "policies" / "jx1_walk_flat")
    hw_cfg = str(Path(get_package_share_directory("jx1_hw")) / "config" / "hw.yaml")
    io = str(Path(policy_dir) / "policy_io.yaml")
    urdf = xacro.process_file(str(Path(get_package_share_directory("jx1_description")) / "urdf" / "jx1.urdf.xacro"),
                              mappings={"collision": "none"}).toxml()
    hil = get("hil") == "true"
    port_a, port_b = ("socket://127.0.0.1:5555", "socket://127.0.0.1:5556") if hil else (get("port_a"), get("port_b"))
    nodes = [
        Node(package="jx1_hw", executable="hw_node", output="screen",
             parameters=[{"port_a": port_a, "port_b": port_b, "policy_io": io, "hw_config": hw_cfg}]),
        Node(package="robot_state_publisher", executable="robot_state_publisher", parameters=[{"robot_description": urdf}],
             remappings=[("/joint_states", "/jx1/joint_states")]),
        Node(package="jx1_policy", executable="policy_node", output="screen", parameters=[{"policy_dir": policy_dir, "use_sim_time": hil}]),
    ]
    if not hil and get("imu") == "true":
        nodes.append(Node(package="jx1_hw", executable="imu_node", output="screen"))
    if hil:
        import os
        repo = get("repo") or os.environ.get("JX1_REPO", "")
        nodes.insert(0, Node(package="jx1_hw", executable="fake_hub", output="screen",
                             parameters=[{"model_path": str(Path(repo) / "simulation" / "mujoco" / "jx1.xml"), "hw_config": hw_cfg,
                                          "policy_io": io}]))
    return nodes


def generate_launch_description():
    return LaunchDescription([DeclareLaunchArgument("port_a", default_value="/dev/ttyACM0"),
                              DeclareLaunchArgument("port_b", default_value="/dev/ttyACM1"),
                              DeclareLaunchArgument("policy_dir", default_value=""), DeclareLaunchArgument("hil", default_value="false"),
                              DeclareLaunchArgument("repo", default_value=""), DeclareLaunchArgument("imu", default_value="true"),
                              OpaqueFunction(function=setup)])
