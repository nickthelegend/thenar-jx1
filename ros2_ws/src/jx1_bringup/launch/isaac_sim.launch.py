"""JX1 in Isaac Sim under ROS 2 with the walking policy.

Start Isaac Sim with the JX1 ROS 2 bridge first (simulation/isaac/isaaclab/scripts/ros2_bridge.py: publishes /clock,
/jx1/joint_states, /jx1/imu and applies /jx1/joint_command), then:
  ros2 launch jx1_bringup isaac_sim.launch.py [rviz:=true]
"""
import sys
from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import default_policy_dir, robot_description, state_publisher  # noqa: E402


def setup(context):
    def get(k):
        return LaunchConfiguration(k).perform(context)
    policy_dir = get("policy_dir") or default_policy_dir()
    nodes = [state_publisher(robot_description(collision="none")),
             Node(package="jx1_policy", executable="policy_node", output="screen",
                  parameters=[{"policy_dir": policy_dir, "use_sim_time": True}])]
    if get("rviz") == "true":
        nodes.append(Node(package="rviz2", executable="rviz2", parameters=[{"use_sim_time": True}]))
    return nodes


def generate_launch_description():
    return LaunchDescription([DeclareLaunchArgument("policy_dir", default_value=""), DeclareLaunchArgument("rviz", default_value="false"),
                              OpaqueFunction(function=setup)])
