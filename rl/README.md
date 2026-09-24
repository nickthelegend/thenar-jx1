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
| `rl/sim2sim.py` | exported policy on the **full CAD model** (mesh hulls, 500 Hz, no DR), 7 command scenarios; optional sensing/actuation delay; per scenario: tracking, torque/speed margins, foot lift-offs, self-contact between robot bodies | tested |
| `rl/envelope.py`, `rl/push_test.py`, `rl/latency_test.py`, `rl/power_test.py` | command envelope (vx × wz, vx × vy grids, incl. self-contact), push recovery (walking and standing), latency sensitivity, electrical power / battery current / actuator thermal load, all on the CAD model | tested |
| `rl/report.py`, `rl/compare_policies.py`, `rl/play.py` | `REPORT.md` policy card per bundle, side-by-side comparison, keyboard driving in the MuJoCo viewer | tested (viewer: headless path) |
| `rl/tests/test_rl.py` | quaternion maths vs MuJoCo, ankle-polygon projection (numpy/ROS/torch), env determinism, training-vs-deployment observation parity, latency, hub ramp, MuJoCo/Isaac `policy_io` parity, hardware protocol/bridge/IMU, rough terrain, GAE/normaliser, ros2_control xacro, mirror maps vs MuJoCo physics, stand-mode clock gating | 15/15 pass |
| `simulation/isaac/isaaclab/` | Isaac Lab tasks `Isaac-Velocity-{Flat,Rough}-JX1-v0` (+ `-Play`), same obs/actions/rewards/DR; rsl_rl config, train and export scripts, offline API check, Isaac Sim ROS 2 bridge | offline-checked against Isaac Lab 2.3.2 + rsl_rl 3.1.2 and the bridge and USD import against Isaac Sim 5.1 sources (89/89); **not run in Isaac Sim** |
| `ros2_ws/src/jx1_policy` | ONNX policy runner (no training code) + ROS 2 node (WAIT → RAMP → WALK, HOLD on stale state) | runner tested; node see below |
| `ros2_ws/src/jx1_sim` | MuJoCo ROS 2 node: `/clock`, `/jx1/joint_states`, `/jx1/imu`, `/jx1/odom`, TF; applies `/jx1/joint_command` | see below |
| `ros2_ws/src/jx1_bringup` | `mujoco_sim.launch.py`, `isaac_sim.launch.py`, `ros2_control.launch.py`, controllers | see below |
| `tools/sim/gen_ros2_control.py` | `jx1.ros2_control.xacro` (mock / topic_based_ros2_control), `jx1_system.urdf.xacro`, `controllers.yaml` | generated |
| `ros2_ws/src/jx1_hw` | Jetson ↔ CAN-hub bridge (firmware USB protocol, parallel-ankle IK/FK, motor gains), hub-firmware digital twin, `hardware.launch.py` | protocol + bridge tested; HIL run on the emulator |
| `rl/ros2_check.py`, `rl/hw_loop_check.py`, `rl/ros2_env/build_ws.py` | end-to-end checks over real ROS 2 (sim node / hardware bridge + emulated hubs), from the source tree or with `--launch` from a colcon install (`mujoco_sim.launch.py`, `ros2_control.launch.py`, `hardware.launch.py hil:=true`) | run on this machine (RoboStack Jazzy) |

## Trained policies (final CAD model, 33.61 kg)

Each bundle in `rl/policies/` has `policy.onnx`, `policy.pt`, `policy_io.yaml` and every check result, summarised in its
`REPORT.md`. A copy for ROS 2 lives in `ros2_ws/src/jx1_policy/policies/`. The **default is `jx1_walk_rough`** for the
ROS 2 policy node, the launch files, the hardware launch, the Isaac Sim bridge and the rl tools (`jx1_rl.DEFAULT_POLICY`).

<!-- policies:start -->
| | `jx1_walk_flat` | `jx1_walk_rough` | `jx1_walk_stand` | `jx1_walk_stand_sym` | `jx1_walk_sym_latency` |
|---|---|---|---|---|---|
| trained | walk_v2_final it 3000 | walk_v3_rough it 4000 | walk_v5_stand it 4800 | walk_v6_stand_sym it 5600 | walk_v4_sym_latency it 5000 |
| sim2sim flat | 7/7 upright; 0.5 m/s -> 0.50, turn 0.5 -> 0.47 rad/s, peak torque 90% | 8/8 upright; 0.5 m/s -> 0.52, turn 0.5 -> 0.49 rad/s, peak torque 81% | 8/8 upright; 0.5 m/s -> 0.52, turn 0.5 -> 0.46 rad/s, peak torque 83% | 8/8 upright; 0.5 m/s -> 0.49, turn 0.5 -> 0.42 rad/s, peak torque 74% | 7/7 upright; 0.5 m/s -> 0.51, turn 0.5 -> 0.49 rad/s, peak torque 70% |
| sim2sim rough | 7/7 upright; 0.5 m/s -> 0.50, turn 0.5 -> 0.47 rad/s, peak torque 95% | 8/8 upright; 0.5 m/s -> 0.53, turn 0.5 -> 0.49 rad/s, peak torque 79% | 8/8 upright; 0.5 m/s -> 0.53, turn 0.5 -> 0.47 rad/s, peak torque 86% | 8/8 upright; 0.5 m/s -> 0.50, turn 0.5 -> 0.43 rad/s, peak torque 76% | 7/7 upright; 0.5 m/s -> 0.52, turn 0.5 -> 0.50 rad/s, peak torque 72% |
| envelope flat | 99/130 tracked, 0 falls; fwd +1.13, back -0.59, yaw +0.85/-0.82 | 109/130 tracked, 0 falls; fwd +1.08, back -0.57, yaw +0.84/-0.86 | 98/130 tracked, 0 falls; fwd +1.12, back -0.62, yaw +0.83/-0.86 | 117/130 tracked, 0 falls; fwd +1.09, back -0.59, yaw +0.78/-0.86 | 102/130 tracked, 0 falls; fwd +1.05, back -0.58, yaw +0.89/-0.92 |
| push (N s) | 12.7-21.6 (fwd 21.6, back 14.5, left 12.7, right 17.8) | 15.9-44.1 (fwd 32.8, back 35.6, left 15.9, right 44.1) | 22.5-55.8 (fwd 36.1, back 38.4, left 22.5, right 55.8) | 29.5-57.7 (fwd 44.1, back 46.4, left 29.5, right 57.7) | 11.7-39.8 (fwd 39.8, back 26.7, left 11.7, right 28.1) |
| HIL (hub twin) | fwd 95% of 0.3 m/s, turn 74% of 0.3 rad/s | fwd 95% of 0.3 m/s, turn 88% of 0.3 rad/s | fwd 97% of 0.3 m/s, turn 75% of 0.3 rad/s | fwd 88% of 0.3 m/s, turn 71% of 0.3 rad/s | fwd 95% of 0.3 m/s, turn 72% of 0.3 rad/s |
| turn 0.3 tracking | 85% (no delay), 70% (20 + 10 ms) | 101% (no delay), 94% (20 + 10 ms) | 83% (no delay), 75% (20 + 10 ms) | 80% (no delay), 73% (20 + 10 ms) | 84% (no delay), 74% (20 + 10 ms) |
| self-contact, envelope flat | - | 3/130 commands (1 in the trained range): left_shin_link|right_shin_link (2), left_foot_link|right_foot_link (1) | 0/130 commands (0 in the trained range): none | 0/130 commands (0 in the trained range): none | - |
| self-contact, envelope rough | - | 3/130 commands (1 in the trained range): left_shin_link|right_shin_link (2), left_foot_link|right_foot_link (1) | 0/130 commands (0 in the trained range): none | 0/130 commands (0 in the trained range): none | - |
| envelope rough | - | 108/130 tracked, 0 falls; fwd +1.09, back -0.56, yaw +0.84/-0.86 | 94/130 tracked, 0 falls; fwd +1.13, back -0.61, yaw +0.83/-0.86 | 117/130 tracked, 0 falls; fwd +1.11, back -0.59, yaw +0.78/-0.87 | 98/130 tracked, 0 falls; fwd +1.07, back -0.58, yaw +0.89/-0.93 |
| stand -> walk 0.5 -> stand | - | upright, 2.50 foot lift-offs/s in the last 2 s | upright, 0.00 foot lift-offs/s in the last 2 s | upright, 0.00 foot lift-offs/s in the last 2 s | - |
| stand (zero command) | - | 2.51 foot lift-offs/s, drift 0.05 m, 163 W | 0.00 foot lift-offs/s, drift 0.00 m, 79 W | 0.00 foot lift-offs/s, drift 0.00 m, 79 W | - |
| power 0.5 / 0.8 m/s | - | 283 W / 368 W | 313 W / 382 W | 284 W / 363 W | - |
| push standing (N s) | - | 19.2-36.1 | 27.7-47.8 | 11.7-51.6 | - |
| HIL 0.8 m/s | - | 0.70 m/s, upright | 0.70 m/s, upright | 0.70 m/s, upright | - |
<!-- policies:end -->

- `jx1_walk_flat`: 1500 iterations on the placeholder model, then 1500 on the final CAD model (flat floor).
- `jx1_walk_rough`: `jx1_walk_flat` fine-tuned for 1000 iterations on the rough heightfield. It is better on flat ground
  too. It leaves more torque headroom (peaks at 71–73 % against the hubs' 80 % cap), takes about twice the push
  impulse, has no yaw drift and tolerates latency.
- `jx1_walk_sym_latency` (experiment): `jx1_walk_rough` + 1000 iterations with the left/right mirror loss, 0–15 ms
  sensing / 0–10 ms actuation latency and half the entropy bonus. It came out slightly worse: 102 vs 109 commands
  tracked, 72 vs 88 % turn tracking through the HIL chain, 11.7 N·s vs 15.9 N·s worst push, and back to 84 %
  tracking of 0.3 rad/s turns. The rough policy had already lost the yaw drift and tolerates 40 ms + 20 ms latency, so
  it stays the default. Kept for reference; not installed with the ROS 2 package.
- `jx1_walk_stand` (experiment, OI-27): `jx1_walk_rough` + 800 iterations with the stand mode (clock features 0 below a
  command norm of 0.1, both feet down, no swing target) and 20 % zero commands. It really stands: 0 foot lift-offs/s
  instead of 2.5, 79 W instead of 163 W (4.7 h instead of 2.3 h on the pack), and it settles within 2 s after walking.
  It also takes larger pushes (22.5–55.8 N·s walking, 27.7–47.8 N·s standing) and has no leg self-contact over the
  envelope. But it tracks leftward side-steps and slow turns worse: 98 vs 109 commands, 0.3 rad/s turns at 83 % vs
  101 %, HIL turn 75 % vs 88 %. So `jx1_walk_rough` stays the default until a stand-mode policy matches its tracking.
- `jx1_walk_stand_sym` (experiment): `jx1_walk_stand` + 800 iterations with 10 % zero commands and a mild mirror loss
  (0.2). It keeps the stand mode (79 W, settles after walking) and has the widest envelope so far: 117/130 on flat and on
  rough ground, symmetric side-steps (±0.36 m/s), 29.5–57.7 N·s walking pushes and no self-contact. Its weak points:
  slow turns at 80 %, HIL 88 % forward / 71 % turn, −0.03 rad/s yaw drift while walking, and only 11.7 N·s forward push
  while standing, because the both-feet-down contact reward penalised recovery steps. `walk_v7` drops that stand-mode
  contact target (`gait.stand_contact_reward: none`) and weights yaw tracking 0.8.
- Every bundle's `policy_io.yaml` carries the hip-yaw toe-out coupling (`hip_yaw_toe_out_max_rad`, OI-24), applied by
  every runner. The learned gaits never reach it (22.9° max toe-out sum against the 40° limit).
- Table generated by `rl/compare_policies.py <bundles>`. "HIL" is the hardware-in-the-loop run through `hw_node` and the
  hub-firmware twin.

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
- `rl/power_test.py`: battery power, current and actuator RMS current vs rated for standing and walking, with the
  electrical model of `calculations/run_power_budget.py` (ankle motors through the linkage), plus foot lift-offs.
- Stand and self-contact metrics (every `sim2sim.py` / `envelope.py` rollout): foot lift-offs per second, swing fraction
  and base travel (stepping in place, OI-27), and every contact between two robot bodies on the CAD hulls (leg-leg OI-7,
  hip-yaw brackets OI-24, arm-thigh OI-18). The detector reports the hip-yaw bracket contact at 22° toe-out per hip, as
  the OI-24 sweep found.
- `rl/report.py`: gathers every check of a bundle (training curves, sim-to-sim, envelope, pushes, power, ROS 2, HIL)
  into the bundle's `REPORT.md`.

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
  - `walk_v4` then trained with 0–15 ms sensing and 0–10 ms actuation latency and came out worse
    (`jx1_walk_sym_latency`), while `jx1_walk_rough`, trained with 0–5 ms each, still tracks 0.3 rad/s turns at 89 % under
    40 ms + 20 ms added delay, so the task randomises 0–5 ms each;
- at zero command the free policy drifted −0.03 rad/s in yaw (+0.3 rad/s turns at 85 %, −0.3 at 109 %), although the
  robot is symmetric to 0.2 mm. PPO has a left/right mirror loss (`ppo.symmetry_coef`, mirror maps checked against
  MuJoCo physics); it is off by default because the rough fine-tune had already removed the drift and the mirrored
  `walk_v4` was worse.

## Conventions (policy_io.yaml)

- **Action**: 12 leg joints (left hip yaw, roll, pitch, knee, ankle pitch, roll; then right), `target = clip(default +
  0.25 * action, limits)`; ankle (pitch, roll) targets projected into the SolidWorks collision-free polygon
  (`joint_map.yaml` → `coupled_limits`). Waist, arms and neck hold the default walking posture.
- **Observation (47)**: body angular velocity × 0.25, projected gravity, command × (2, 2, 0.25), joint position −
  default, joint velocity × 0.05, last action, sin/cos of the 0.8 s gait clock (phase starts when walking starts).
  **Stand mode** (`gait.stand_command_threshold`, 0.1): below that command norm the clock features are 0, and in
  training the contact reward wants both feet down with no swing-height target (OI-27). Every runner (training env,
  `sim2sim.py`, the ROS 2 runner, Isaac Lab) applies the same rule; bundles without the key run the clock always.
- **Control**: 50 Hz policy; trained with 200 Hz physics (MuJoCo) — sim-to-sim runs the CAD model at 500 Hz.
- The parallel ankle is abstracted as serial pitch/roll joints with the linkage's capability limits (46/51 N·m);
  converting ankle targets to the two ankle motors is done by the hub (`calculations/jx1calc/ankle.py`).
