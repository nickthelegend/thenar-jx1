"""Shared pieces of the JX1 launch files."""
import os
from pathlib import Path

import xacro
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node


def robot_description(xacro_file="jx1.urdf.xacro", **mappings):
    path = Path(get_package_share_directory("jx1_description")) / "urdf" / xacro_file
    return xacro.process_file(str(path), mappings={k: str(v) for k, v in mappings.items()}).toxml()


def default_policy_dir():
    return str(Path(get_package_share_directory("jx1_policy")) / "policies" / "jx1_walk_flat")


def repo_root():
    """The JX1 repository (the MuJoCo model and its meshes live there): $JX1_REPO."""
    return os.environ.get("JX1_REPO", "")


def state_publisher(description, use_sim_time=True):
    return Node(package="robot_state_publisher", executable="robot_state_publisher",
                parameters=[{"robot_description": description, "use_sim_time": use_sim_time}],
                remappings=[("/joint_states", "/jx1/joint_states")])
