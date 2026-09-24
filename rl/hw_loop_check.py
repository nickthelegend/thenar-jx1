"""Hardware-in-the-loop check without hardware: policy -> jx1_hw bridge -> hub byte protocol -> emulated hubs (firmware
control law) -> MuJoCo CAD model -> hub state frames -> bridge (ankle FK) -> policy, all as separate ROS 2 processes.

  jx1_hw fake_hub   : two TCP "serial" hubs (firmware protocol + MIT law at 500 Hz, soft/torque limits, DAMPING until RUN,
                      host watchdog), push-rod ankle, MuJoCo physics; publishes /clock, /jx1/imu, /jx1/odom
  jx1_hw hw_node    : the real bridge node, connected to the emulator with pyserial socket:// URLs instead of /dev/ttyACM*
  jx1_policy        : the ONNX walking policy
Procedure like a bring-up: gantry holds the robot, hubs in DAMPING -> policy reaches WALK -> /jx1/hw/run -> gantry release
-> /cmd_vel scenario (stand, forward 0.3 m/s, turn 0.3 rad/s, stop). Writes <policy>/hw_loop_check.json.
Run in the ROS 2 environment:  pixi run python rl/hw_loop_check.py --policy rl/policies/jx1_walk_rough
With --launch <colcon install space> the chain is started as on the robot, `ros2 launch jx1_hw hardware.launch.py hil:=true`
(writes hw_loop_launch_check.json).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import rclpy
from std_msgs.msg import String
from std_srvs.srv import Trigger

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ros2_check import Probe, clean, spin_until, start_launch, stop  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
SCRIPT = [("stand", (0.0, 0.0, 0.0), 4.0), ("forward", (0.3, 0.0, 0.0), 10.0), ("turn", (0.0, 0.0, 0.3), 6.0), ("stop", (0.0, 0.0, 0.0), 4.0)]
# --fast: the top of the trained speed range through the hub torque caps (80 % of peak; the ankle motors reach it at 0.8 m/s)
SCRIPT_FAST = [("stand", (0.0, 0.0, 0.0), 4.0), ("fast", (0.8, 0.0, 0.0), 8.0), ("stop", (0.0, 0.0, 0.0), 4.0)]


def wait_port(port, timeout=30.0):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.3)
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default=str(REPO / "rl" / "policies" / "jx1_walk_rough"))
    ap.add_argument("--launch", type=Path, default=None, help="colcon install space: ros2 launch jx1_hw hardware.launch.py hil:=true")
    ap.add_argument("--fast", action="store_true", help="stand, 0.8 m/s for 8 s, stop -> hw_loop_fast_check.json")
    a = ap.parse_args()
    policy = Path(a.policy).resolve()
    io = policy / "policy_io.yaml"
    hw = REPO / "ros2_ws" / "src" / "jx1_hw" / "config" / "hw.yaml"
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(str(REPO / "ros2_ws" / "src" / p) for p in ("jx1_hw", "jx1_policy")) + os.pathsep + env.get("PYTHONPATH", "")
    run = lambda *args: subprocess.Popen([sys.executable, "-m", *args], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)  # noqa: E731
    if a.launch:
        procs = [start_launch(a.launch.resolve(), policy, "hardware.launch.py", package="jx1_hw", extra=["hil:=true"])]
        tags = ("launch",)
    else:
        procs = [run("jx1_hw.fake_hub", "--ros-args", "-p", f"model_path:={REPO / 'simulation' / 'mujoco' / 'jx1.xml'}", "-p",
                     f"hw_config:={hw}", "-p", f"policy_io:={io}", "-p", "port_a:=5555", "-p", "port_b:=5556")]
        tags = ("fake_hub", "hw_node", "policy")
    result = {"policy": policy.relative_to(REPO).as_posix() if policy.is_relative_to(REPO) else policy.name,
              "chain": "jx1_policy -> jx1_hw hw_node -> hub protocol over TCP -> fake_hub (firmware law) -> MuJoCo",
              "started_by": "ros2 launch jx1_hw hardware.launch.py hil:=true (colcon install)" if a.launch else "python -m (source tree)",
              "phases": {}}
    rclpy.init()
    probe = Probe()
    status = {}
    probe.create_subscription(String, "/jx1/hw/status", lambda m: status.update(json.loads(m.data)), 10)
    try:
        if not (wait_port(5555) and wait_port(5556)):
            raise RuntimeError("hub emulator did not open its ports")
        if not a.launch:
            procs.append(run("jx1_hw.hw_node", "--ros-args", "-p", "port_a:=socket://127.0.0.1:5555", "-p",
                             "port_b:=socket://127.0.0.1:5556", "-p", f"policy_io:={io}", "-p", f"hw_config:={hw}"))
            procs.append(run("jx1_policy.policy_node", "--ros-args", "-p", f"policy_dir:={policy}", "-p", "use_sim_time:=true"))
        result["reached_walk_state"] = spin_until(probe, lambda: probe.state == "WALK", 120.0)
        if not result["reached_walk_state"]:
            raise RuntimeError(f"policy never reached WALK (state {probe.state})")
        cli = probe.create_client(Trigger, "/jx1/hw/run")
        cli.wait_for_service(timeout_sec=10.0)
        fut = cli.call_async(Trigger.Request())
        spin_until(probe, fut.done, 10.0)
        result["run_accepted"] = bool(fut.result() and fut.result().success)
        spin_until(probe, lambda: all(h.get("mode") == 2 for h in status.get("hubs", {}).values()) and len(status.get("hubs", {})) == 2, 10.0)
        result["hub_modes_after_run"] = {h: v.get("mode") for h, v in status.get("hubs", {}).items()}
        for name, cmd, dur in (SCRIPT_FAST if a.fast else SCRIPT):
            start, i0 = probe.sim_time(), len(probe.log)
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
        result["hub_status_end"] = status
    except Exception as e:                      # keep the process logs for diagnosis
        result["error"] = f"{type(e).__name__}: {e}"
    finally:
        probe.destroy_node()
        rclpy.try_shutdown()
        outs = {tag: stop(p) for p, tag in reversed(list(zip(procs, tags)))}
        for tag in tags:
            result[f"{tag}_log_tail"] = clean(outs[tag].strip().splitlines())[-(25 if a.launch else 12):]
    out = "hw_loop_fast_check.json" if a.fast else ("hw_loop_launch_check.json" if a.launch else "hw_loop_check.json")
    (policy / out).write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if not k.endswith("log_tail")}, indent=1))
    if "error" in result:
        for k, v in result.items():
            if k.endswith("log_tail"):
                print(f"== {k}")
                print("\n".join(v))
        sys.exit(1)


if __name__ == "__main__":
    main()
