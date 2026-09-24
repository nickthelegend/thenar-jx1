from setuptools import setup

package_name = "jx1_sim"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[("share/ament_index/resource_index/packages", ["resource/" + package_name]),
                (f"share/{package_name}", ["package.xml"])],
    install_requires=["setuptools", "numpy", "pyyaml", "mujoco"],
    zip_safe=True,
    maintainer="JX1 project",
    maintainer_email="maintainer@jx1.invalid",
    description="MuJoCo simulator node for JX1",
    license="Apache-2.0",
    entry_points={"console_scripts": ["mujoco_node = jx1_sim.mujoco_node:main"]},
)
