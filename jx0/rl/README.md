# JX0: training a walking policy (MuJoCo or Isaac Lab)

JX0 trains on JX1's reinforcement-learning stack, so both robots share the same environment, PPO and export code:
- the MuJoCo environment and PPO in `rl/`;
- the Isaac Lab tasks in `simulation/isaac/isaaclab`.

What is specific to JX0 lives here:

| File | What it is |
|---|---|
| `build_description.py` | Writes `description/` from the verified JX0 model (`jx0/sim/jx0_model.py`) and the robot's own `config.yaml` |
| `description/jx0.xml` | Training MJCF. Joints `left_hip_yaw_joint` … `neck_yaw_joint`; the 17 STS3215 servos as position actuators (60 N·m/rad, 0.6 N·m·s/rad, ±2.94 N·m); thigh, shin, pelvis and torso meshes for the collision fit |
| `description/joint_map.yaml` | Joint frames, axes and limits (the commanded limits, see `verify_stops.py`), actuator data, sole frames, coupled limits |
| `description/urdf/jx0.urdf` | For Isaac Sim's URDF importer. CAD inertias, mesh visuals, sole boxes, convex hulls on the legs |
| `config/jx0_walk.yaml` | The task: 12 leg joints, the walking stance as default pose, 50 Hz policy, rewards, randomisation and PPO, all scaled for a 2.9 kg, 0.33 m robot |

Regenerate the description after any CAD or `config.yaml` change:

```bash
python jx0/rl/build_description.py
```

## Option 1: MuJoCo on this PC

The environment runs on the CPU and the PPO update on the GPU. A 6 GB RTX 3050 is enough.

```bash
rl/.venv/Scripts/python rl/train.py --config jx0/rl/config/jx0_walk.yaml --run jx0_walk_v1
```

```bash
rl/.venv/Scripts/python rl/export.py --checkpoint rl/runs/jx0_walk_v1/model_2999.pt --out jx0/rl/policies/jx0_walk_v1
```

Checkpoints and `metrics.csv` go to `rl/runs/<run>/`. The export writes `policy.onnx`, `policy.pt` and `policy_io.yaml`, the same bundle format as JX1's.

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
