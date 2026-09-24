from glob import glob

from setuptools import setup

package_name = "jx1_hw"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[("share/ament_index/resource_index/packages", ["resource/" + package_name]),
                (f"share/{package_name}", ["package.xml"]),
                (f"share/{package_name}/config", glob("config/*.yaml")),
                (f"share/{package_name}/launch", glob("launch/*.py"))],
    install_requires=["setuptools", "numpy", "pyyaml", "pyserial"],
    zip_safe=True,
    maintainer="JX1 project",
    maintainer_email="maintainer@jx1.invalid",
    description="JX1 hardware bridge and hub emulator",
    license="Apache-2.0",
    entry_points={"console_scripts": ["hw_node = jx1_hw.hw_node:main", "fake_hub = jx1_hw.fake_hub:main",
                                  "imu_node = jx1_hw.imu_node:main"]},
)
