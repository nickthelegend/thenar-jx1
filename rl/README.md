# JX1 — trainable model (MuJoCo · Isaac Lab · ROS 2)

Phase 3 of JX1: the CAD-derived robot as a **reinforcement-learning-ready model** with one policy format that runs in
MuJoCo, Isaac Lab and ROS 2. The walking task, its conventions and the deployment gains live in one file,
[`config/jx1_walk.yaml`](config/jx1_walk.yaml); every other piece reads it.

```text
 SolidWorks CAD ──► tools/sim/build_robot_description.py ──► simulation/mujoco/jx1.xml   ros2_ws/.../jx1.urdf(.xacro)
                                                                   │                          │
            rl/config/jx1_walk.yaml (joints, default pose,         ▼                          ▼
            PD gains, obs/action layout, rewards, DR, PPO)   rl/ (MuJoCo, CPU-batched)   simulation/isaac/isaaclab (Isaac Lab)
                                                                   │  train.py → export.py    │  scripts/train.py → export_policy.py
                                                                   ▼                          ▼
                                             policy bundle: policy.onnx + policy.pt + policy_io.yaml
                                                                   │
                        ┌──────────────────────────────────────────┼───────────────────────────────┐
                        ▼                                          ▼                               ▼
              rl/sim2sim.py (full CAD MuJoCo,         ros2_ws: jx1_policy node  ◄──►  jx1_sim (MuJoCo node) / Isaac Sim ROS 2
              500 Hz, mesh-hull collisions)           /jx1/joint_states /jx1/imu /cmd_vel → /jx1/joint_command (or ros2_control)
```

## What is where

| Path | Contents | Status |
|---|---|---|
| `rl/config/jx1_walk.yaml` | task definition: 12 policy joints, default pose, deployment PD gains, action scale 0.25, 47-D observation, gait clock, commands, rewards, domain randomisation, PPO | source of truth |
| `rl/jx1_rl/assets.py` | CAD MJCF → training model (capsules/boxes fitted to the CoACD hulls, collision groups, gains, sensors, `home` keyframe) | tested |
| `rl/jx1_rl/env.py` | batched MuJoCo environment on `mujoco.rollout` (C++ thread pool), rewards, DR, pushes, resets | tested, ~20k policy steps/s on 8–11 threads |
| `rl/jx1_rl/ppo.py`, `rl/train.py` | PPO (rsl_rl algorithm: asymmetric actor-critic, running normalisers, GAE, adaptive LR), GPU update | tested |
| `rl/export.py` | TorchScript + ONNX (normaliser baked in) + `policy_io.yaml`, checked against the checkpoint | tested |
| `rl/sim2sim.py` | exported policy on the **full CAD model** (mesh hulls, 500 Hz, no DR), 7 command scenarios | tested |
| `rl/tests/test_rl.py` | quaternion maths vs MuJoCo, ankle-polygon projection (numpy/ROS/torch), env determinism, training-vs-deployment observation parity, MuJoCo/Isaac `policy_io` parity, GAE/normaliser, ros2_control xacro | 7/7 pass |
| `simulation/isaac/isaaclab/` | Isaac Lab task `Isaac-Velocity-Flat-JX1-v0` (same obs/actions/rewards/DR), rsl_rl config, train/export scripts, Isaac Sim ROS 2 bridge | **UNVERIFIED** (no Isaac Sim on the design machine) |
| `ros2_ws/src/jx1_policy` | ONNX policy runner (no training code) + ROS 2 node (WAIT → RAMP → WALK, HOLD on stale state) | runner tested; node see below |
| `ros2_ws/src/jx1_sim` | MuJoCo ROS 2 node: `/clock`, `/jx1/joint_states`, `/jx1/imu`, `/jx1/odom`, TF; applies `/jx1/joint_command` | see below |
| `ros2_ws/src/jx1_bringup` | `mujoco_sim.launch.py`, `isaac_sim.launch.py`, `ros2_control.launch.py`, controllers | see below |
| `tools/sim/gen_ros2_control.py` | `jx1.ros2_control.xacro` (mock / topic_based_ros2_control), `jx1_system.urdf.xacro`, `controllers.yaml` | generated |
| `ros2_ws/src/jx1_hw` | Jetson ↔ CAN-hub bridge (firmware USB protocol, parallel-ankle IK/FK, motor gains), hub-firmware digital twin, `hardware.launch.py` | protocol + bridge tested; HIL run on the emulator |
| `rl/ros2_check.py`, `rl/hw_loop_check.py` | end-to-end checks over real ROS 2 (sim node / hardware bridge + emulated hubs) | run on this machine (RoboStack Jazzy) |

## Train in MuJoCo (this machine: Windows, RTX 3050 6 GB, i5-13420H)

```bash
py -3.13 -m venv rl/.venv
rl/.venv/Scripts/python -m pip install torch==2.14.0 --index-url https://download.pytorch.org/whl/cu126
rl/.venv/Scripts/python -m pip install -r rl/requirements.txt
rl/.venv/Scripts/python rl/tests/test_rl.py
rl/.venv/Scripts/python rl/train.py --num-envs 1024 --iterations 3000 --run my_run        # rl/runs/my_run/
rl/.venv/Scripts/python rl/export.py --checkpoint rl/runs/my_run/model_latest.pt           # rl/policies/jx1_walk_flat/
rl/.venv/Scripts/python rl/sim2sim.py                                                      # full CAD model check + GIF
```

Resume or fine-tune on a regenerated CAD model with `--resume rl/runs/<run>/model_latest.pt`.

**Numerical note (MEASURED):** with the Newton solver's line search capped at 10 iterations the model injected energy
after falls (robots launched to hundreds of metres, 5/6 seeds); `ls_iterations >= 20` fixed it with no speed cost, so
the task uses 50/50.

### Rough ground

`rl/config/jx1_walk_rough.yaml` inherits the flat task (`base:` key) and replaces the floor with a 16 m heightfield of
2 m tiles: flat, ±2 cm uneven floor, domes/bowls up to 8°, and ±2 cm step strips (thresholds, cable covers). Every
non-step tile returns to zero at its edges, so the only discontinuities are the step edges (≤ 4 cm). Robots spawn over
the whole map; base height, foot clearance and the fall check are measured above the local ground; leaving the map ends
the episode without penalty. The observation stays blind (same 47-D vector), so the rough policy fine-tunes from the flat
one and deploys through the same `policy_io.yaml`, ROS 2 node and hardware bridge.

```bash
rl/.venv/Scripts/python rl/train.py --config rl/config/jx1_walk_rough.yaml --resume rl/runs/<flat run>/model_latest.pt --iterations <n>
rl/.venv/Scripts/python rl/sim2sim.py --policy rl/policies/jx1_walk_rough --terrain rl/config/jx1_walk_rough.yaml
```

### Robustness checks

- `rl/sim2sim.py [--terrain ...]`: 7 command scenarios on the full CAD model (mesh hulls, 500 Hz, hub target ramp);
  velocity tracking, tilt, peak torque / effort limit and peak joint speed / speed limit per scenario.
- `rl/push_test.py`: 0.1 s torso force pulse while walking at 0.5 m/s, bisection of the largest survived impulse per
  direction (same method as `simulation/mujoco/push_jx1.py` for the model-based controller). Interim policy on the
  placeholder-torso model: 11.7–23.4 N·s, vs 6.6–7.8 N·s for the fixed-footstep ZMP controller.

## Train in Isaac Lab (UNVERIFIED)

```bash
cd <IsaacLab> && ./isaaclab.sh -p -m pip install -e <repo>/simulation/isaac/isaaclab
./isaaclab.sh -p <repo>/simulation/isaac/isaaclab/scripts/train.py --task Isaac-Velocity-Flat-JX1-v0 --headless --num_envs 4096
./isaaclab.sh -p <repo>/simulation/isaac/isaaclab/scripts/train.py --task Isaac-Velocity-Rough-JX1-v0 --headless   # terrain generator
./isaaclab.sh -p <repo>/simulation/isaac/isaaclab/scripts/export_policy.py --checkpoint <log>/model_3000.pt --out <repo>/rl/policies/jx1_walk_flat_isaac --headless
```

Asset: `simulation/isaac/jx1.usd` from `simulation/isaac/import_jx1.py` if present, else the URDF (mesh URIs made
absolute). The action term clamps to joint limits and projects the ankle targets into the collision-free polygon, as in
MuJoCo, so exported policies share the `policy_io.yaml` contract.

## Run on ROS 2

```bash
export JX1_REPO=<repo>
colcon build --packages-select jx1_description jx1_policy jx1_sim jx1_bringup && source install/setup.bash
pip install mujoco==3.14.0 onnxruntime
ros2 launch jx1_bringup mujoco_sim.launch.py viewer:=true         # MuJoCo + policy (direct /jx1/joint_command)
ros2 run teleop_twist_keyboard teleop_twist_keyboard              # /cmd_vel
ros2 launch jx1_bringup ros2_control.launch.py                    # same through ros2_control (topic_based_ros2_control)
ros2 launch jx1_bringup isaac_sim.launch.py                       # with simulation/isaac/isaaclab/scripts/ros2_bridge.py running
```

**Verified on the design machine (Windows 11, no system ROS):** ROS 2 Jazzy from RoboStack in a pixi environment
([`ros2_env/pixi.toml`](ros2_env/pixi.toml) + lock file), then the end-to-end check, which starts `jx1_sim` and
`jx1_policy` as separate ROS 2 processes, drives `/cmd_vel` and measures the walk from `/jx1/odom`:

```bash
pixi install --manifest-path rl/ros2_env/pixi.toml
pixi run --manifest-path rl/ros2_env/pixi.toml python rl/ros2_check.py --policy rl/policies/jx1_walk_flat
```

Topics (sim and hardware alike): `/jx1/joint_states` (JointState, all actuated joints), `/jx1/imu` (pelvis IMU),
`/cmd_vel` (vx, vy, wz) → `/jx1/joint_command` (JointState position targets). PD gains are applied downstream (MuJoCo
position actuators, PhysX drives, RobStride MIT mode) from `policy_io.yaml` → `pd_gains`.

## Real robot: hardware bridge and hardware-in-the-loop (`ros2_ws/src/jx1_hw`)

`hw_node` runs on the Jetson: `/jx1/joint_command` (joint space) → the two Teensy 4.1 CAN hubs over USB serial, in the
byte format of `firmware/hub/jx1_hub/jx1_hub.ino` (CRC-16/MODBUS frames, hub joint order/signs/limits generated from the
firmware configs into `config/hw.yaml`), and hub feedback → `/jx1/joint_states`. The ankle is driven as its two crank
motors: closed-form IK (identical to `calculations/jx1calc/ankle.py`), Newton FK for the feedback, J⁻¹ velocities,
Jᵀ torques. The hubs start in DAMPING; `ros2 service call /jx1/hw/run std_srvs/srv/Trigger` enables them (robot on the
gantry), `/jx1/hw/damp` goes back.

`fake_hub` is a digital twin of the hub firmware on the MuJoCo CAD model: the same protocol over TCP, the RobStride MIT
law at the 500 Hz bus rate with soft limits, the hub torque caps, the 20 ms target ramp, DAMPING/RUN and the host
watchdog, the push-rod ankle, and a bring-up gantry. `rl/hw_loop_check.py` runs policy → hw_node → "serial" → emulated
hubs → physics → back as separate ROS 2 processes and walks the robot over `/cmd_vel`:

```bash
pixi run --manifest-path rl/ros2_env/pixi.toml python rl/hw_loop_check.py --policy rl/policies/jx1_walk_flat
ros2 launch jx1_hw hardware.launch.py hil:=true            # the same chain from a launch file
ros2 launch jx1_hw hardware.launch.py port_a:=/dev/ttyACM0 port_b:=/dev/ttyACM1   # the real robot (+ IMU driver on /jx1/imu)
```

**What the hardware-in-the-loop run changed in training (MEASURED on the emulator, then modelled):**
- the hubs ramp each 50 Hz host target over the next 20 ms (first-order hold, ≈10 ms effective lag): now reproduced in
  the training environment, `sim2sim.py`, the `jx1_sim` node and the Isaac Lab action term;
- the two ankle motors run independent MIT loops, so the realisable joint-space roll/pitch stiffness ratio is fixed by the
  linkage (1.27): the task's ankle gains are now the realisable pair 51.2 / 64.8 N·m/rad (motor kp 40, kd 1.5);
- 0–5 ms actuation and 0–5 ms sensing latency are randomised per episode; torques above 85 % of the actuator peak are
  penalised (the hubs cap at 80 %).

## Conventions (policy_io.yaml)

- **Action**: 12 leg joints (left hip yaw, roll, pitch, knee, ankle pitch, roll; then right), `target = clip(default +
  0.25 * action, limits)`; ankle (pitch, roll) targets projected into the SolidWorks collision-free polygon
  (`joint_map.yaml` → `coupled_limits`). Waist, arms and neck hold the default walking posture.
- **Observation (47)**: body angular velocity × 0.25, projected gravity, command × (2, 2, 0.25), joint position −
  default, joint velocity × 0.05, last action, sin/cos of the 0.8 s gait clock (phase starts when walking starts).
- **Control**: 50 Hz policy; trained with 200 Hz physics (MuJoCo) — sim-to-sim runs the CAD model at 500 Hz.
- The parallel ankle is abstracted as serial pitch/roll joints with the linkage's capability limits (46/51 N·m);
  converting ankle targets to the two ankle motors is done by the hub (`calculations/jx1calc/ankle.py`).
