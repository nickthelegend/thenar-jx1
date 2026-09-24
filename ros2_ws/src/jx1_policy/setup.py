from glob import glob
from pathlib import Path

from setuptools import setup

package_name = "jx1_policy"
policy_files = [(f"share/{package_name}/{p.parent.as_posix()}", [p.as_posix()]) for p in Path("policies").rglob("*") if p.is_file()]

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[("share/ament_index/resource_index/packages", ["resource/" + package_name]),
                (f"share/{package_name}", ["package.xml"])] + policy_files,
    install_requires=["setuptools", "numpy", "pyyaml", "onnxruntime"],
    zip_safe=True,
    maintainer="JX1 project",
    maintainer_email="maintainer@jx1.invalid",
    description="JX1 walking-policy runtime and ROS 2 node",
    license="Apache-2.0",
    entry_points={"console_scripts": ["policy_node = jx1_policy.policy_node:main"]},
)
