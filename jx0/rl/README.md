# JX0: training a walking policy (MuJoCo or Isaac Lab)

JX0 trains on JX1's reinforcement-learning stack, so both robots share the same environment, PPO and export code:
- the MuJoCo environment and PPO in `rl/`;
- the Isaac Lab tasks in `simulation/isaac/isaaclab`.

What is specific to JX0 lives here:

| File | What it is |
|---|---|
| `../description/` | The robot description (its own folder now): `build_description.py` writes it from the verified model, `check_description.py` checks it (see below) |
| `../description/jx0.xml` | Training MJCF. Joints `left_hip_yaw_joint` … `neck_yaw_joint`; the 17 STS3215 servos as position actuators (60 N·m/rad, 0.6 N·m·s/rad, ±2.94 N·m); thigh, shin, pelvis and torso meshes for the collision fit |
| `../description/joint_map.yaml` | Joint frames, axes and limits (the commanded limits, see `verify_stops.py`), actuator data, sole frames, coupled limits |
| `../description/urdf/jx0.urdf` | For Isaac Sim's URDF importer. CAD inertias, mesh visuals, sole boxes, convex hulls on the legs |
| `config/jx0_walk17.yaml` | **The whole-body task, for Isaac Lab:** all 17 servos at 50 Hz from 176 observations (3 frames of history). Isaac Lab task `Isaac-Velocity-Flat-JX0-Full-v0`; on a lab PC, `jx0\setup\setup_isaac.bat` then `train_isaac.bat` ([setup/README.md](../setup/README.md)) |
| `sim2sim_jx0.py` | The test suite on the verified model: speeds, pushes, 60 s endurance, latency, PASS / FAIL (see below) |
| `play_jx0.py` | Drive a policy in real time in the MuJoCo viewer: arrows walk and turn, J/L side-step, K stop, P push |
| `config/jx0_walk.yaml` | The 12-leg-joint task: 12 leg joints, the walking stance as default pose, 50 Hz policy, rewards, randomisation and PPO, all scaled for a 2.9 kg, 0.33 m robot |

Regenerate the description after any CAD or `config.yaml` change:

```bash
python jx0/description/build_description.py
```

## Option 1: MuJoCo on this PC

The environment runs on the CPU and the PPO update on the GPU. A 6 GB RTX 3050 is enough.

```bash
rl/.venv/Scripts/python rl/train.py --config jx0/rl/config/jx0_walk.yaml --run jx0_walk_v1
```

```bash
rl/.venv/Scripts/python rl/export.py --checkpoint rl/runs/jx0_walk_v1/model_2999.pt --out jx0/rl/policies/jx0_walk_v1
```

Check the exported policy on the verified JX0 model rather than the training model. That model runs at 1 kHz with the STS3215's torque-speed line, the 100 Hz bus and jx0bot's clamps. Add `--latency-ms 10` to test with delay, or `--video walk.mp4` to film it:

```bash
rl/.venv/Scripts/python jx0/rl/sim2sim_jx0.py --policy jx0/rl/policies/jx0_walk_v1
```

Checkpoints and `metrics.csv` go to `rl/runs/<run>/`. The export writes `policy.onnx`, `policy.pt` and `policy_io.yaml`, the same bundle format as JX1's.

## Result: jx0_walk17_v5 passes the test suite

The policy is 17 joint corrections at 50 Hz from 176 observations. On the verified model (servo torque-speed limit, 100 Hz bus) it passes:
- **speeds:** 11/11 (forward 0.03–0.10 m/s, backward, sideways, turning, forward + turn);
- **pushes:** 96/96, up to 0.72 N·s;
- **endurance:** the 60 s run with pushes;
- **latency:** 12 ms of extra delay.

The robot's own gait program passes the same kind of tests in `jx0/verify` (walking, pushes, 60 s endurance on 12 robots with model errors). See `policies/jx0_walk17_v5/REPORT.md`.

What made it work is the reference gait. Without one (runs v1–v3), the policies stood still or stepped in place. With the verified gaits as the reference and near-zero initial corrections, the robot walks from the first iteration, and the policy only learns balance, push recovery and the speeds in between.

## Training history (2026-10-16)

| Run | Change | Result |
|---|---|---|
| `jx0_walk_v1` | first run | Walks forward and stands on the full model (sim2sim). Does not turn or side-step: one tracking tolerance gave turns no signal (`policies/jx0_walk_v1`) |
| `jx0_walk_v2` | separate yaw tolerance, tighter speed tolerance, strong penalty above 70 % of no-load speed | Learned to stand still |
| `jx0_walk_v3` | v1's speed tolerance, gentle speed penalty | At 1000 iterations, weaker than v1 forward; turns at 15–25 % |

Turning and side-stepping still need reward work. One likely cause: with tolerance 0.01, standing still earns 85 % of the reward for a 0.04 m/s side-step command.

## Option 2: Isaac Lab on a GPU machine

Isaac Sim needs an RTX GPU with at least 8 GB, so it does not run on this PC. Use a lab PC or a rented cloud GPU with Isaac Sim 5.1 and Isaac Lab 2.3.

```bash
<IsaacLab>/isaaclab.sh -p simulation/isaac/isaaclab/scripts/train.py --task Isaac-Velocity-Flat-JX0-v0 --headless --num_envs 4096
```

```bash
rl/.venv/Scripts/python simulation/isaac/isaaclab/scripts/export_offline.py --checkpoint <model.pt> --out jx0/rl/policies/jx0_walk_isaac
```

When the task name contains `-JX0`, `train.py` loads JX0's task file through `JX_TASK_CONFIG`. To export a JX0 checkpoint offline, set `JX_TASK_CONFIG=jx0/rl/config/jx0_walk.yaml` before the export command. Isaac Lab converts the URDF to USD at launch.

The tasks are offline-checked against the Isaac Lab 2.3.2, rsl_rl 3.1.2 and Isaac Sim 5.1 sources: **49/49 checks pass** (`isaac_offline_check.json`). They have **not been run in Isaac Sim**.

```bash
JX_TASK_CONFIG=jx0/rl/config/jx0_walk.yaml rl/.venv/Scripts/python simulation/isaac/isaaclab/scripts/offline_check.py --isaaclab D:/jx1-deps/IsaacLab-2.3.2 --rsl-rl D:/jx1-deps/rsl_rl_src --isaacsim D:/jx1-deps/IsaacSim-5.1.0
```

## On the robot

**Not written yet:** a jx0bot runner for the policy. The robot walks with its verified gait files today.

A policy would need no new hardware: on the Pi it reads the IMU and the servo positions and sends goals at 50 Hz. The same safety layers would stay in front of it:
- `couple_hips` and the clamps in `jx0bot.robot`;
- each servo's own EEPROM limits;
- the printed joint stops.

What is assumed: the servo stiffness (60 N·m/rad, randomised 0.6–1.4×), the bus and servo latency (4–16 ms, randomised), and the floor friction.
