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
| `rl/jx1_rl/ppo.py`, `rl/train.py` | PPO (rsl_rl algorithm: asymmetric actor-critic, running normalisers, GAE, adaptive LR), GPU update, left/right mirror loss (`jx1_rl/symmetry.py`) | tested |
| `rl/export.py` | TorchScript + ONNX (normaliser baked in) + `policy_io.yaml`, checked against the checkpoint | tested |
| `rl/sim2sim.py` | exported policy on the **full CAD model** (mesh hulls, 500 Hz, no DR), 7 command scenarios; optional sensing/actuation delay | tested |
| `rl/envelope.py`, `rl/push_test.py`, `rl/latency_test.py` | command envelope (vx × wz, vx × vy grids), push recovery, latency sensitivity, all on the CAD model | tested |
| `rl/report.py`, `rl/compare_policies.py`, `rl/play.py` | `REPORT.md` policy card per bundle, side-by-side comparison, keyboard driving in the MuJoCo viewer | tested (viewer: headless path) |
| `rl/tests/test_rl.py` | quaternion maths vs MuJoCo, ankle-polygon projection (numpy/ROS/torch), env determinism, training-vs-deployment observation parity, latency, hub ramp, MuJoCo/Isaac `policy_io` parity, hardware protocol/bridge/IMU, rough terrain, GAE/normaliser, ros2_control xacro, mirror maps vs MuJoCo physics | 14/14 pass |
| `simulation/isaac/isaaclab/` | Isaac Lab tasks `Isaac-Velocity-{Flat,Rough}-JX1-v0` (+ `-Play`), same obs/actions/rewards/DR; rsl_rl config, train and export scripts, offline API check, Isaac Sim ROS 2 bridge | offline-checked against Isaac Lab 2.3.2 + rsl_rl 3.1.2 and the bridge and USD import against Isaac Sim 5.1 sources (89/89); **not run in Isaac Sim** |
| `ros2_ws/src/jx1_policy` | ONNX policy runner (no training code) + ROS 2 node (WAIT → RAMP → WALK, HOLD on stale state) | runner tested; node see below |
| `ros2_ws/src/jx1_sim` | MuJoCo ROS 2 node: `/clock`, `/jx1/joint_states`, `/jx1/imu`, `/jx1/odom`, TF; applies `/jx1/joint_command` | see below |
| `ros2_ws/src/jx1_bringup` | `mujoco_sim.launch.py`, `isaac_sim.launch.py`, `ros2_control.launch.py`, controllers | see below |
| `tools/sim/gen_ros2_control.py` | `jx1.ros2_control.xacro` (mock / topic_based_ros2_control), `jx1_system.urdf.xacro`, `controllers.yaml` | generated |
| `ros2_ws/src/jx1_hw` | Jetson ↔ CAN-hub bridge (firmware USB protocol, parallel-ankle IK/FK, motor gains), hub-firmware digital twin, `hardware.launch.py` | protocol + bridge tested; HIL run on the emulator |
| `rl/ros2_check.py`, `rl/hw_loop_check.py`, `rl/ros2_env/build_ws.py` | end-to-end checks over real ROS 2 (sim node / hardware bridge + emulated hubs), from the source tree or with `--launch` from a colcon install (`mujoco_sim.launch.py`, `ros2_control.launch.py`, `hardware.launch.py hil:=true`) | run on this machine (RoboStack Jazzy) |

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
- `rl/envelope.py`: constant-command walks over a vx × wz and a vx × vy grid, from inside the training ranges to beyond
  them. For each command it records falls, tracking and torque margin, and writes `envelope.json` and `envelope.png`. The
  whole grid takes about a minute on 4 processes.
- `rl/report.py`: gathers every check of a bundle (training curves, sim-to-sim, envelope, pushes, ROS 2, HIL) into the
  bundle's `REPORT.md`.

## Train in Isaac Lab (offline-checked, not yet run in Isaac Sim)

```bash
cd <IsaacLab> && ./isaaclab.sh -p -m pip install -e <repo>/simulation/isaac/isaaclab
./isaaclab.sh -p <repo>/simulation/isaac/isaaclab/scripts/train.py --task Isaac-Velocity-Flat-JX1-v0 --headless --num_envs 4096
./isaaclab.sh -p <repo>/simulation/isaac/isaaclab/scripts/train.py --task Isaac-Velocity-Rough-JX1-v0 --headless   # terrain generator
# deployment bundle straight from the checkpoint, on any machine with rl/.venv (no Isaac Sim needed):
rl/.venv/Scripts/python simulation/isaac/isaaclab/scripts/export_offline.py --checkpoint <log>/model_2999.pt --out rl/policies/jx1_walk_flat_isaac
rl/.venv/Scripts/python rl/sim2sim.py --policy rl/policies/jx1_walk_flat_isaac     # the Isaac-trained policy on the MuJoCo CAD model
```

Isaac Sim does not fit the design machine (RTX 3050 6 GB, 24 GB RAM, full system drive), so these tasks have not been
run. They are **checked offline against the Isaac Lab 2.3.2 sources and rsl_rl 3.1.2**:

```bash
git clone --depth 1 --branch v2.3.2 https://github.com/isaac-sim/IsaacLab.git <dir>/IsaacLab-2.3.2
rl/.venv/Scripts/python -m pip download rsl-rl-lib==3.1.2 --no-deps -d <dir>      # unzip the wheel to <dir>/rsl_rl_src
rl/.venv/Scripts/python simulation/isaac/isaaclab/scripts/offline_check.py --isaaclab <dir>/IsaacLab-2.3.2 --rsl-rl <dir>/rsl_rl_src
```

`offline_check.py` mocks the Omniverse modules (as Isaac Lab's own docs build does) and imports the real Isaac Lab code.
It checks all four tasks (89/89 pass, report in
[`offline_check.json`](../simulation/isaac/isaaclab/offline_check.json)):
- Every env and runner config instantiates, and `validate()` passes.
- Every manager term resolves as Isaac Lab resolves it at start-up (signature, scene entities against the robot the URDF
  importer builds).
- Every observation, reward and termination term runs on a fake scene whose attribute names are checked against the
  real data classes.
- Policy and critic observations equal the MuJoCo task's (47 and 55 values).
- The action term produces the MuJoCo targets on every physics substep: clamp, ankle polygon, hub ramp, delay, reset.
- Actuators cover all 23 joints with the task gains.
- The scripts' imports and keyword arguments match the library signatures.
- The offline exporter matches `rsl_rl`'s `ActorCritic.act_inference`.
- With `--isaacsim <sparse clone of isaac-sim/IsaacSim v5.1.0>`, it checks the Isaac Sim ROS 2 bridge
  (`scripts/ros2_bridge.py`). Every OmniGraph node type must exist as an `.ogn` definition, every connected or set
  attribute must exist with matching types, "target" inputs must be set as path lists, and every Isaac Sim Python call
  must match its source signature. `simulation/isaac/import_jx1.py` (URDF → USD) is checked the same way against the URDF
  importer: its import-config fields, command names and arguments.

What the check found and what was fixed:
- **Deployment bug:** under rsl_rl ≥ 3 (Isaac Lab ≥ 2.3) the observation normaliser moved into the policy. The export
  script therefore wrote an ONNX without it, and the deployed policy would have received raw observations.
  `export_policy.py` is fixed. `export_offline.py` reads both checkpoint layouts.
- **Runner config:** `obs_groups` is now set, so the critic gets the privileged group. The deprecated
  `empirical_normalization` is dropped on ≥ 2.3. Actions are clipped at ±100, as in MuJoCo.
- **Action term:** after a reset the ramp started from the previous episode's last target. It now starts from the
  default pose, and a 0–1 substep transport delay was added, both as in `env.py`.
- **Critic:** it lacked the MuJoCo privileged terms (base height, foot contact, sole heights). It now matches the 55 values.
- **Rough task:** the base-height reward was off, and the fall check and swing height used world z. They are now
  measured from the ground under the robot, via a pelvis height scanner that only the critic and rewards see.
- **Randomisation:** friction pairs are consistent, armature is randomised, and gains are randomised on all joints,
  as in MuJoCo.
- **Symmetry:** the MuJoCo trainer's left/right mirror loss (`ppo.symmetry_coef`, `rl/jx1_rl/symmetry.py`) is wired
  into rsl_rl's `RslRlSymmetryCfg`. It uses the same mirror maps, loaded from the repository.
- **Isaac Sim bridge:** the joint-state publisher and the IMU reader had their "target" inputs set with strings.
  Isaac Sim ≥ 4.5 needs `[usdrt.Sdf.Path(...)]` there, so both nodes would have published nothing. The robot also
  spawned at the origin with the importer's drive gains. It now stands at the default pose, 1 cm above the floor, and
  gets the policy's deployment PD gains. The ground has the MuJoCo floor friction (μ 1, no restitution; the default
  plane bounces with 0.8). `/jx1/odom` is published for the ROS 2 checks.

- **Sensing latency:** Isaac Lab observes only the latest physics state. The action term now snapshots the robot state
  at every physics substep, and the `delayed_*` observation terms serve each env its randomised 0–15 ms old state,
  indexed like MuJoCo's `obs_src` (checked substep by substep).

Still different from MuJoCo:
- No joint friction torque: PhysX joint friction is a coefficient, while MuJoCo uses `frictionloss`.
- PhysX contacts instead of MuJoCo soft contacts. Running an Isaac-trained bundle through `rl/sim2sim.py` on the CAD model
  measures exactly this gap.

Asset: `simulation/isaac/jx1.usd` from `simulation/isaac/import_jx1.py` if it exists, otherwise the URDF with absolute
mesh URIs.

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

The packaged path is verified the same way. `rl/ros2_env/build_ws.py` runs `colcon build` on `ros2_ws/src` into a
workspace outside the repository. `ros2_check.py --launch` then starts everything with
`ros2 launch jx1_bringup mujoco_sim.launch.py` from that install space: the MuJoCo node, `robot_state_publisher` on the
xacro description, and the policy node. It drives the robot and writes `ros2_launch_check.json`.

```bash
pixi run --manifest-path rl/ros2_env/pixi.toml python rl/ros2_env/build_ws.py --ws <ws>
pixi run --manifest-path rl/ros2_env/pixi.toml python rl/ros2_check.py --policy rl/policies/jx1_walk_flat --launch <ws>/install
```

`jx1_bringup` is an ament_python package, so it builds without a C++ toolchain. `jx1_description` is ament_cmake and
only installs directories. On Windows without MSVC, `build_ws.py` replicates that install rule. On the Jetson or Ubuntu,
plain `colcon build` builds all five packages.

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
- torques above 85 % of the actuator peak are penalised (the hubs cap at 80 %);
- the final flat policy tracked a 0.3 rad/s turn at 62 % through the chain vs 85 % in MuJoCo. `sim2sim.py` with added
  delay (`rl/latency_test.py`) reproduces that at about 30 ms of sensing plus 10 ms of actuation latency. Two fixes:
  - `hw_node` sent hub frames on its own 50 Hz timer, which added a random 0–20 ms delay after each policy output. It
    now forwards every command at once, which alone gave 73 % turn and 95 % forward tracking;
  - training now randomises 0–15 ms sensing and 0–10 ms actuation latency (was 0–5 ms each);
- at zero command the free policy drifted −0.03 rad/s in yaw (+0.3 rad/s turns at 85 %, −0.3 at 109 %), although the
  robot is symmetric to 0.2 mm. PPO now has a left/right mirror loss (`ppo.symmetry_coef`), with the mirror maps
  checked against MuJoCo physics.

## Conventions (policy_io.yaml)

- **Action**: 12 leg joints (left hip yaw, roll, pitch, knee, ankle pitch, roll; then right), `target = clip(default +
  0.25 * action, limits)`; ankle (pitch, roll) targets projected into the SolidWorks collision-free polygon
  (`joint_map.yaml` → `coupled_limits`). Waist, arms and neck hold the default walking posture.
- **Observation (47)**: body angular velocity × 0.25, projected gravity, command × (2, 2, 0.25), joint position −
  default, joint velocity × 0.05, last action, sin/cos of the 0.8 s gait clock (phase starts when walking starts).
- **Control**: 50 Hz policy; trained with 200 Hz physics (MuJoCo) — sim-to-sim runs the CAD model at 500 Hz.
- The parallel ankle is abstracted as serial pitch/roll joints with the linkage's capability limits (46/51 N·m);
  converting ankle targets to the two ankle motors is done by the hub (`calculations/jx1calc/ankle.py`).
