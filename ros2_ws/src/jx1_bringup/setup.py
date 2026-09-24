from glob import glob

from setuptools import setup

package_name = "jx1_bringup"

# launch files and configuration only (ament_python: builds without a C++ toolchain, e.g. RoboStack on Windows)
setup(
    name=package_name,
    version="0.1.0",
    packages=[],
    data_files=[("share/ament_index/resource_index/packages", ["resource/" + package_name]),
                (f"share/{package_name}", ["package.xml"]),
                (f"share/{package_name}/launch", glob("launch/*.py")),
                (f"share/{package_name}/config", glob("config/*.yaml"))],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="JX1 project",
    maintainer_email="maintainer@jx1.invalid",
    description="Launch files for JX1: MuJoCo or Isaac Sim simulation + walking policy, ros2_control, RViz",
    license="Apache-2.0",
)
