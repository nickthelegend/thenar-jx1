"""End-to-end ROS 2 check: the jx1_sim MuJoCo node and the jx1_policy node as separate ROS 2 processes, driven over
/cmd_vel and measured from /jx1/odom - the deployment path, not a unit test.

Run inside a ROS 2 (Jazzy) Python environment that also has mujoco==3.14.0 and onnxruntime, e.g. the RoboStack/pixi
environment used on the design machine:
  <pixi> run python rl/ros2_check.py --policy rl/policies/jx1_walk_rough
  <pixi> run python rl/ros2_check.py --policy rl/policies/jx1_walk_rough --launch <ws>/install    # packaged: colcon + ros2 launch
Scenario: stand (ramp) -> 0.4 m/s forward 10 s -> turn 0.4 rad/s 6 s -> stop 4 s. Writes <policy>/ros2_check.json
(ros2_launch_check.json with --launch; the install space comes from rl/ros2_env/build_ws.py).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import String

REPO = Path(__file__).resolve().parents[1]
SCRIPT = [("forward", (0.4, 0.0, 0.0), 10.0), ("turn", (0.0, 0.0, 0.4), 6.0), ("stop", (0.0, 0.0, 0.0), 4.0)]


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


class Probe(Node):
    def __init__(self):
        super().__init__("jx1_ros2_check", parameter_overrides=[rclpy.parameter.Parameter("use_sim_time", value=True)])
        self.odom, self.state, self.log = None, None, []
        self.create_subscription(Odometry, "/jx1/odom", self.on_odom, 10)
        self.create_subscription(String, "/jx1/policy_state", lambda m: setattr(self, "state", m.data), 10)
        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)

    def on_odom(self, m):
        self.odom = m
        p, q = m.pose.pose.position, m.pose.pose.orientation
        tilt = math.degrees(math.acos(max(-1.0, min(1.0, 1.0 - 2.0 * (q.x * q.x + q.y * q.y)))))     # body z vs world z (no yaw)
        self.log.append((m.header.stamp.sec + m.header.stamp.nanosec * 1e-9, p.x, p.y, p.z, yaw_of(q), tilt))

    def sim_time(self):
        return self.log[-1][0] if self.log else 0.0

    def send(self, cmd):
        t = Twist()
        t.linear.x, t.linear.y, t.angular.z = cmd
        self.pub.publish(t)


def spin_until(node, cond, timeout_s):
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        rclpy.spin_once(node, timeout_sec=0.05)
        if cond():
            return True
    return False


def start_launch(install: Path, policy: Path, launch_file: str, package: str = "jx1_bringup", extra=()):
    """`ros2 launch <package> <launch_file>` from a colcon install space (rl/ros2_env/build_ws.py)."""
    args = ["ros2", "launch", package, launch_file, f"repo:={REPO}", f"policy_dir:={policy}", *extra]
    if launch_file == "ros2_control.launch.py":
        args += ["hardware:=topic", "sim:=mujoco"]
    if sys.platform == "win32":
        cmd = f'call "{install / "setup.bat"}" >NUL && ' + " ".join(f'"{x}"' if " " in x else x for x in args)
        # one command-line string: a list would have its inner quotes escaped (\"), which cmd.exe does not understand
        return subprocess.Popen(f'cmd /d /s /c "{cmd}"', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    cmd = f'. "{install / "setup.sh"}" && exec ' + " ".join(f"'{x}'" for x in args)
    return subprocess.Popen(["bash", "-c", cmd], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)


def clean(lines):
    """Log lines without the machine-specific log directory (host name, user home)."""
    home = str(Path.home())
    return [ln.replace(home, "~") for ln in lines if "All log files can be found" not in ln]


def stop(p):
    """Stop a process and everything it started (ros2 launch spawns the nodes as children)."""
    if p.poll() is None:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
        else:
            p.terminate()
    try:
        return p.communicate(timeout=15)[0]
    except subprocess.TimeoutExpired:
        p.kill()
        return p.communicate()[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default=str(REPO / "rl" / "policies" / "jx1_walk_rough"))
    ap.add_argument("--launch", type=Path, default=None,
                    help="colcon install space: start the stack with `ros2 launch jx1_bringup mujoco_sim.launch.py` from it "
                         "instead of running the two nodes from the source tree (writes ros2_launch_check.json)")
    ap.add_argument("--launch-file", default="mujoco_sim.launch.py", choices=["mujoco_sim.launch.py", "ros2_control.launch.py"],
                    help="ros2_control.launch.py: controller_manager + topic_based_ros2_control hardware between the policy and "
                         "the MuJoCo node (writes ros2_control_check.json)")
    a = ap.parse_args()
    out_name = "ros2_check.json" if not a.launch else ("ros2_control_check.json" if a.launch_file == "ros2_control.launch.py"
                                                         else "ros2_launch_check.json")
    policy = Path(a.policy).resolve()
    if a.launch:
        procs = {"launch": start_launch(a.launch.resolve(), policy, a.launch_file)}
    else:
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join([str(REPO / "ros2_ws" / "src" / "jx1_sim"), str(REPO / "ros2_ws" / "src" / "jx1_policy"),
                                             env.get("PYTHONPATH", "")])
        procs = {"sim": subprocess.Popen([sys.executable, "-m", "jx1_sim.mujoco_node", "--ros-args", "-p",
                                          f"model_path:={REPO / 'simulation' / 'mujoco' / 'jx1.xml'}", "-p",
                                          f"policy_io:={policy / 'policy_io.yaml'}"],
                                         env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True),
                 "policy": subprocess.Popen([sys.executable, "-m", "jx1_policy.policy_node", "--ros-args", "-p", f"policy_dir:={policy}",
                                             "-p", "use_sim_time:=true"], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)}
    rclpy.init()
    probe = Probe()
    result = {"policy": policy.relative_to(REPO).as_posix() if policy.is_relative_to(REPO) else policy.name, "ros_distro": os.environ.get("ROS_DISTRO", "?"),
              "started_by": f"ros2 launch jx1_bringup {a.launch_file} (colcon install)" if a.launch else "python -m (source tree)",
              "phases": {}}
    try:
        ok = spin_until(probe, lambda: probe.state == "WALK", 90.0)
        result["reached_walk_state"] = ok
        if not ok:
            raise RuntimeError(f"policy node never reached WALK (state {probe.state}, odom {'yes' if probe.log else 'no'})")
        for name, cmd, dur in SCRIPT:
            start = probe.sim_time()
            i0 = len(probe.log)
            while probe.sim_time() - start < dur:
                probe.send(cmd)
                rclpy.spin_once(probe, timeout_sec=0.02)
            seg = probe.log[i0:]
            t, x, y, z, yaw, tilt = zip(*seg)
            dist = math.hypot(x[-1] - x[0], y[-1] - y[0])
            dyaw = math.atan2(math.sin(yaw[-1] - yaw[0]), math.cos(yaw[-1] - yaw[0]))
            result["phases"][name] = {"command": cmd, "sim_duration_s": round(t[-1] - t[0], 2), "distance_m": round(dist, 3),
                                      "mean_speed_m_s": round(dist / max(t[-1] - t[0], 1e-6), 3), "yaw_change_deg": round(math.degrees(dyaw), 1),
                                      "min_pelvis_z_m": round(min(z), 3), "max_tilt_deg": round(max(tilt), 2)}
            print(name, result["phases"][name], flush=True)
        result["upright"] = all(p["min_pelvis_z_m"] > 0.4 for p in result["phases"].values())
    except Exception as e:                                     # keep the report (and the process logs) on failure
        result["error"] = f"{type(e).__name__}: {e}"
    finally:
        probe.destroy_node()
        rclpy.try_shutdown()
        for tag, p in procs.items():
            result[f"{tag}_log_tail"] = clean(stop(p).strip().splitlines())[-(25 if a.launch else 5):]
    (policy / out_name).write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if not k.endswith("log_tail") or "error" in result}, indent=1))
    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
