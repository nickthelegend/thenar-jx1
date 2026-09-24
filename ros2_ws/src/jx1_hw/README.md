# jx1_hw: JX1 on the real robot

The Jetson runs four processes:
- `hw_node`: joint space ↔ the two Teensy 4.1 CAN hubs over USB serial.
- `imu_node`: BNO085 → `/jx1/imu`.
- `policy_node`: from `jx1_policy`.
- `robot_state_publisher`.

The hubs close the RobStride MIT loops at 500 Hz. The policy sends joint targets at 50 Hz. The hubs ramp each target
over the next 20 ms and apply the PD gains from `policy_io.yaml`. `hw_node` forwards each policy command to the hubs as
soon as it arrives. It used to send on its own 50 Hz timer, which added a random 0–20 ms delay. In the
hardware-in-the-loop run, removing that delay raised forward tracking at 0.3 m/s from 82 % to 93 % and turn tracking
from 62 % to 73 %.

**Status.** The following are verified without hardware:
- The byte protocol is checked against the firmware headers (CRC-16/MODBUS test).
- The parallel-ankle IK/FK/Jacobians round-trip (test).
- The whole chain runs against a digital twin of the hub firmware on the CAD model, both from Python and via
  `ros2 launch jx1_hw hardware.launch.py hil:=true` (`rl/hw_loop_check.py [--launch]`).

`imu_node` is **not verified**. It was written against the Adafruit BNO08x driver API and never run on a chip.

## 1. Jetson setup

The stack is tested with ROS 2 Jazzy (RoboStack) and uses only standard rclpy, launch and ros2_control APIs. JetPack 6
(Ubuntu 22.04) ships ROS 2 Humble, which these packages should also run on; that is untested.

```bash
sudo apt install ros-$ROS_DISTRO-robot-state-publisher ros-$ROS_DISTRO-xacro ros-$ROS_DISTRO-teleop-twist-keyboard
pip install onnxruntime pyserial pyyaml numpy adafruit-circuitpython-bno08x adafruit-blinka
cd ros2_ws && colcon build && source install/setup.bash
```

Give the hubs stable device names. A Teensy's USB serial is VID `16c0`, PID `0483`, and each board has its own serial
number (read it with `udevadm info /dev/ttyACM0 | grep SERIAL`). In `/etc/udev/rules.d/99-jx1.rules`:

```text
SUBSYSTEM=="tty", ATTRS{idVendor}=="16c0", ATTRS{idProduct}=="0483", ATTRS{serial}=="<hub A serial>", SYMLINK+="jx1_hub_a"
SUBSYSTEM=="tty", ATTRS{idVendor}=="16c0", ATTRS{idProduct}=="0483", ATTRS{serial}=="<hub B serial>", SYMLINK+="jx1_hub_b"
```

Hub A carries the left leg, the left arm and the waist, and hub B the right leg and the right arm. The neck servos
are not on the hubs. See `config/hw.yaml`, generated from the firmware configs by `scripts/gen_config.py`. The BNO085 goes on I2C bus 7 of the 40-pin header at
address 0x4A. `mount_rpy_deg` rotates the chip axes into the pelvis frame (x forward, y left, z up).

## 2. Before the first RUN

1. **Motor zeros.** `zero` in `config/hw.yaml` must be the motor reading at joint angle 0 (the URDF pose). Set each
   RobStride's mechanical zero in the calibration pose, or measure the offsets and put them in the firmware config.
   Then regenerate `hw.yaml`.
2. **Directions.** Launch the stack below. The hubs stay in DAMPING (kd only). Move every joint by hand and watch the
   model in RViz (`robot_state_publisher` on `/jx1/joint_states`). The model must follow your hand. If a joint mirrors,
   fix its `sign`.
3. **IMU.** Tilt the pelvis forward and check `/jx1/imu`: the orientation pitches nose-down and the angular velocity
   y is positive. Correct `mount_rpy_deg` if not.
4. **Ankles.** Pitch and roll are driven through the two crank motors (`jx1_hw/ankle.py`). With the foot moved by
   hand, `/jx1/joint_states` must show pitch and roll, never motor angles.

## 3. Bring-up sequence (robot in the gantry, E-stop in hand)

```bash
ros2 launch jx1_hw hardware.launch.py port_a:=/dev/jx1_hub_a port_b:=/dev/jx1_hub_b [policy_dir:=<bundle>]
ros2 topic echo /jx1/hw/status          # both hubs present, mode 1 (DAMPING), no fault, no E-stop
ros2 topic echo /jx1/policy_state       # WAIT -> RAMP -> WALK once joint states and IMU are fresh
ros2 service call /jx1/hw/run std_srvs/srv/Trigger     # hubs track the policy targets (mode 2)
```

1. Enable RUN with the feet just touching the floor. At zero command the policy balances in place.
2. Lower the gantry until the feet carry the weight. Keep slack in the rope, not tension.
3. Drive gently with `ros2 run teleop_twist_keyboard teleop_twist_keyboard`. The node clips commands to 0.8 m/s,
   0.3 m/s and 0.6 rad/s (parameter `max_cmd`).
4. Stop with `ros2 service call /jx1/hw/damp std_srvs/srv/Trigger` or the E-stop.

## 4. What protects the robot

| layer | behaviour |
|---|---|
| E-stop | hardware line into both hubs; RUN is refused while it is pressed |
| hub watchdog | no host frame for 50 ms → DAMPING |
| hub limits | targets clamped to the joint limits minus a soft margin; torque capped at 80 % of the motor peak; temperature derating |
| fall guard (`hw_node`) | pelvis tilt above 50° (`fall_tilt_deg`) latches DAMPING until the next `/jx1/hw/run` |
| policy node | holds the measured pose and drops to WAIT when joint states or the IMU are older than 0.1 s |

## 5. Rehearse in simulation first

```bash
pixi run --manifest-path rl/ros2_env/pixi.toml python rl/ros2_env/build_ws.py --ws <ws>
pixi run --manifest-path rl/ros2_env/pixi.toml python rl/hw_loop_check.py --policy rl/policies/jx1_walk_flat --launch <ws>/install
```

This runs the same launch file with `hil:=true`, and the hub-firmware twin replaces the hubs. The script follows the
procedure above: DAMPING, then WALK, then `/jx1/hw/run`, then gantry release and a `/cmd_vel` scenario. The measured
tracking through this chain is lower than in plain MuJoCo because of latency. The policy card of each bundle
(`REPORT.md`) has the numbers.
