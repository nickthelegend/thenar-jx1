"""Build the JX1 ROS 2 packages with colcon into a workspace outside the repository.

  pixi run --manifest-path rl/ros2_env/pixi.toml python rl/ros2_env/build_ws.py --ws <dir>      # -> <dir>/install

jx1_policy, jx1_sim, jx1_hw and jx1_bringup are ament_python packages. jx1_description is ament_cmake, but its only
rule is install(DIRECTORY urdf meshes launch config). colcon builds it wherever a C++ toolchain exists, as on the Jetson
or Ubuntu. On Windows without MSVC (RoboStack), CMake cannot configure it, so this script replicates that install rule:
share/jx1_description/<dirs>, package.xml and the ament index marker. Launch files then find the package the usual way.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "ros2_ws" / "src"


def have_cxx_toolchain() -> bool:
    if sys.platform != "win32":
        return shutil.which("c++") is not None or shutil.which("g++") is not None or shutil.which("clang++") is not None
    return shutil.which("cl") is not None


def install_directories_only(pkg: Path, install: Path, dirs=("urdf", "meshes", "launch", "config")):
    share = install / "share" / pkg.name
    share.mkdir(parents=True, exist_ok=True)
    for d in dirs:
        if (pkg / d).is_dir():
            shutil.copytree(pkg / d, share / d, dirs_exist_ok=True)
    shutil.copy2(pkg / "package.xml", share / "package.xml")
    marker = install / "share" / "ament_index" / "resource_index" / "packages" / pkg.name
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.touch()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ws", type=Path, required=True, help="workspace directory for build/, install/ and log/")
    a = ap.parse_args()
    ws = a.ws.resolve()
    ws.mkdir(parents=True, exist_ok=True)
    cxx = have_cxx_toolchain()
    cmd = ["colcon", "--log-base", str(ws / "log"), "build", "--base-paths", str(SRC), "--build-base", str(ws / "build"),
           "--install-base", str(ws / "install"), "--merge-install"]
    if not cxx:
        cmd += ["--packages-ignore", "jx1_description"]
    print(" ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=ws, shell=sys.platform == "win32")
    if not cxx:
        install_directories_only(SRC / "jx1_description", ws / "install")
        print("jx1_description: no C++ toolchain, replicated its install(DIRECTORY ...) rule")
    print("install space:", ws / "install")


if __name__ == "__main__":
    main()
