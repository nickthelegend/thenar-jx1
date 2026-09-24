"""JX1 through ros2_control: controller_manager with topic-based hardware (talks to jx1_sim, Isaac Sim or a hardware
bridge on /jx1/joint_command + /jx1/joint_states), joint_state_broadcaster, forward position controller, and the walking
policy writing to that controller.
  ros2 launch jx1_bringup ros2_control.launch.py [hardware:=topic|mock] [sim:=mujoco|none]
"""
import sys
from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import default_policy_dir, repo_root, robot_description  # noqa: E402


def setup(context):
    def get(k):
        return LaunchConfiguration(k).perform(context)
    description = robot_description("jx1_system.urdf.xacro", hardware=get("hardware"), collision="none")
    controllers = str(Path(get_package_share_directory("jx1_bringup")) / "config" / "controllers.yaml")
    policy_dir = get("policy_dir") or default_policy_dir()
    use_sim_time = get("sim") != "none"
    nodes = [
        Node(package="controller_manager", executable="ros2_control_node", output="screen",
             parameters=[{"robot_description": description, "use_sim_time": use_sim_time}, controllers]),
        Node(package="robot_state_publisher", executable="robot_state_publisher",
             parameters=[{"robot_description": description, "use_sim_time": use_sim_time}]),
        Node(package="controller_manager", executable="spawner", arguments=["joint_state_broadcaster"]),
        Node(package="controller_manager", executable="spawner", arguments=["jx1_position_controller"]),
        Node(package="jx1_policy", executable="policy_node", output="screen",
             parameters=[{"policy_dir": policy_dir, "output": "ros2_control", "use_sim_time": use_sim_time}],
             remappings=[("/jx1/joint_states", "/joint_states")]),
    ]
    if get("sim") == "mujoco":
        repo = get("repo") or repo_root()
        nodes.append(Node(package="jx1_sim", executable="mujoco_node", output="screen",
                          parameters=[{"model_path": str(Path(repo) / "simulation" / "mujoco" / "jx1.xml"),
                                       "policy_io": str(Path(policy_dir) / "policy_io.yaml")}]))
    return nodes


def generate_launch_description():
    return LaunchDescription([DeclareLaunchArgument("hardware", default_value="topic"), DeclareLaunchArgument("sim", default_value="mujoco"),
                              DeclareLaunchArgument("repo", default_value=""), DeclareLaunchArgument("policy_dir", default_value=""),
                              OpaqueFunction(function=setup)])
