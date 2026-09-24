"""JX1 in MuJoCo under ROS 2 with the walking policy.

  export JX1_REPO=/path/to/thenar-jx1
  ros2 launch jx1_bringup mujoco_sim.launch.py [viewer:=true] [rviz:=true] [policy_dir:=...]
  ros2 run teleop_twist_keyboard teleop_twist_keyboard        # drive with /cmd_vel
"""
import sys
from pathlib import Path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import default_policy_dir, repo_root, robot_description, state_publisher  # noqa: E402


def setup(context):
    def get(k):
        return LaunchConfiguration(k).perform(context)
    repo = get("repo") or repo_root()
    if not repo:
        raise RuntimeError("set JX1_REPO (or repo:=...) to the thenar-jx1 repository")
    policy_dir = get("policy_dir") or default_policy_dir()
    nodes = [
        Node(package="jx1_sim", executable="mujoco_node", output="screen",
             parameters=[{"model_path": str(Path(repo) / "simulation" / "mujoco" / "jx1.xml"),
                          "policy_io": str(Path(policy_dir) / "policy_io.yaml"),
                          "viewer": get("viewer") == "true", "real_time_factor": float(get("rtf"))}]),
        state_publisher(robot_description(collision="none")),
        Node(package="jx1_policy", executable="policy_node", output="screen",
             parameters=[{"policy_dir": policy_dir, "use_sim_time": True}]),
    ]
    if get("rviz") == "true":
        nodes.append(Node(package="rviz2", executable="rviz2", parameters=[{"use_sim_time": True}]))
    return nodes


def generate_launch_description():
    return LaunchDescription([DeclareLaunchArgument("repo", default_value=""), DeclareLaunchArgument("policy_dir", default_value=""),
                              DeclareLaunchArgument("viewer", default_value="false"), DeclareLaunchArgument("rviz", default_value="false"),
                              DeclareLaunchArgument("rtf", default_value="1.0"), OpaqueFunction(function=setup)])
