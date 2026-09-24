"""Visualise JX1 in RViz with joint sliders:  ros2 launch jx1_description display.launch.py [collision:=visual] [limit_margin_deg:=2]

The robot description is expanded from urdf/jx1.urdf.xacro (default arguments reproduce urdf/jx1.urdf).
"""
from pathlib import Path

import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

ARGS = {"collision": "hulls", "limit_margin_deg": "0"}


def nodes(context):
    share = Path(get_package_share_directory("jx1_description"))
    mappings = {k: LaunchConfiguration(k).perform(context) for k in ARGS}
    urdf = xacro.process_file(str(share / "urdf" / "jx1.urdf.xacro"), mappings=mappings).toxml()
    return [
        Node(package="robot_state_publisher", executable="robot_state_publisher", parameters=[{"robot_description": urdf}]),
        Node(package="joint_state_publisher_gui", executable="joint_state_publisher_gui"),
        Node(package="rviz2", executable="rviz2"),
    ]


def generate_launch_description():
    return LaunchDescription([DeclareLaunchArgument(k, default_value=v) for k, v in ARGS.items()] + [OpaqueFunction(function=nodes)])
