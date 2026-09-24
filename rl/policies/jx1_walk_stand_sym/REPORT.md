# JX1 walking policy: `jx1_walk_stand_sym`

| | |
|---|---|
| trainer | rl/train.py (MuJoCo, rsl_rl-style PPO) |
| checkpoint | walk_v6_stand_sym/model_latest.pt, iteration 5600 |
| task config | run snapshot (config.yaml next to the checkpoint) |
| robot model | `simulation/mujoco/jx1.xml` (sha256 13e00221a0d0…), 33.61 kg |
| interface | 47 observations → 12 leg joint targets at 50 Hz; 11 joints held at the default pose |
| export check | ONNX max abs diff 2.9e-06 |

## Training

![training curves](training.png)

## Sim-to-sim on the full CAD model, flat floor

`simulation/mujoco/jx1.xml` as generated: CoACD mesh-hull collisions, 2 ms physics, nominal masses, CAN-hub target ramp on. All scenarios upright.

| scenario | command (vx, vy, wz) | result | mean velocity | RMSE | max tilt | peak torque / limit | peak speed / limit | foot lift-offs |
|---|---|---|---|---|---|---|---|---|
| stand | (+0.0, +0.0, +0.0) | upright | (-0.00, -0.00, -0.00) | (+0.00, +0.00, +0.00) | 2.0° | 16% right_knee | 8% right_ankle_pitch_joint | 0.00/s |
| forward_0.5 | (+0.5, +0.0, +0.0) | upright | (+0.49, -0.01, -0.03) | (+0.02, +0.03, +0.07) | 5.9° | 59% left_ankle_pitch | 26% right_knee_joint | 2.51/s |
| forward_0.8 | (+0.8, +0.0, +0.0) | upright | (+0.77, -0.01, -0.03) | (+0.04, +0.03, +0.13) | 6.6° | 74% left_ankle_pitch | 28% right_knee_joint | 2.51/s |
| backward_0.3 | (-0.3, +0.0, +0.0) | upright | (-0.32, -0.03, +0.01) | (+0.02, +0.03, +0.05) | 7.0° | 42% right_hip_roll | 24% right_ankle_roll_joint | 2.51/s |
| sidestep_0.2 | (+0.0, +0.2, +0.0) | upright | (-0.01, +0.14, -0.01) | (+0.02, +0.06, +0.04) | 5.4° | 47% right_hip_roll | 24% right_ankle_pitch_joint | 2.51/s |
| turn_0.5 | (+0.0, +0.0, +0.5) | upright | (-0.02, -0.01, +0.42) | (+0.03, +0.02, +0.12) | 5.4° | 44% left_hip_roll | 25% right_ankle_pitch_joint | 2.51/s |
| walk_turn | (+0.4, +0.0, +0.3) | upright | (+0.40, +0.01, +0.22) | (+0.02, +0.03, +0.11) | 5.9° | 50% left_ankle_pitch | 28% right_ankle_pitch_joint | 2.51/s |
| stand_walk_stand | (+0.0, +0.0, +0.0) at 0 s → (+0.5, +0.0, +0.0) at 3 s → (+0.0, +0.0, +0.0) at 7 s | upright | (+0.21, -0.00, -0.02) | (+0.09, +0.03, +0.07) | 8.5° | 71% left_ankle_pitch | 24% left_ankle_pitch_joint | 1.22/s (last 2 s: 0.00/s) |

Self-contact between robot bodies (CoACD hulls, whole rollout): none.

![walking at 0.5 m/s on the CAD model](sim2sim_walk.gif)

## Sim-to-sim on the full CAD model, rough ground (rl/config/jx1_walk_rough.yaml heightfield)

`simulation/mujoco/jx1.xml` as generated: CoACD mesh-hull collisions, 2 ms physics, nominal masses, CAN-hub target ramp on. All scenarios upright.

| scenario | command (vx, vy, wz) | result | mean velocity | RMSE | max tilt | peak torque / limit | peak speed / limit | foot lift-offs |
|---|---|---|---|---|---|---|---|---|
| stand | (+0.0, +0.0, +0.0) | upright | (-0.00, -0.00, -0.00) | (+0.00, +0.00, +0.00) | 2.0° | 16% right_knee | 7% right_ankle_pitch_joint | 0.00/s |
| forward_0.5 | (+0.5, +0.0, +0.0) | upright | (+0.50, -0.01, -0.03) | (+0.02, +0.03, +0.07) | 6.2° | 62% left_ankle_pitch | 29% right_ankle_pitch_joint | 2.51/s |
| forward_0.8 | (+0.8, +0.0, +0.0) | upright | (+0.77, -0.01, -0.03) | (+0.04, +0.03, +0.11) | 6.6° | 76% left_ankle_pitch | 32% right_ankle_pitch_joint | 2.51/s |
| backward_0.3 | (-0.3, +0.0, +0.0) | upright | (-0.32, -0.03, +0.01) | (+0.02, +0.03, +0.06) | 7.1° | 42% right_hip_roll | 25% right_ankle_roll_joint | 2.51/s |
| sidestep_0.2 | (+0.0, +0.2, +0.0) | upright | (-0.01, +0.14, -0.01) | (+0.02, +0.06, +0.04) | 5.4° | 46% right_hip_roll | 23% left_knee_joint | 2.51/s |
| turn_0.5 | (+0.0, +0.0, +0.5) | upright | (-0.03, -0.01, +0.43) | (+0.03, +0.02, +0.11) | 5.4° | 44% left_hip_roll | 25% right_ankle_pitch_joint | 2.68/s |
| walk_turn | (+0.4, +0.0, +0.3) | upright | (+0.40, +0.01, +0.23) | (+0.03, +0.03, +0.11) | 6.8° | 56% left_ankle_pitch | 26% right_ankle_pitch_joint | 2.51/s |
| stand_walk_stand | (+0.0, +0.0, +0.0) at 0 s → (+0.5, +0.0, +0.0) at 3 s → (+0.0, +0.0, +0.0) at 7 s | upright | (+0.21, -0.00, -0.02) | (+0.09, +0.03, +0.07) | 8.6° | 71% left_ankle_pitch | 24% left_ankle_pitch_joint | 1.22/s (last 2 s: 0.00/s) |

Self-contact between robot bodies (CoACD hulls, whole rollout): none.

## Command envelope

117/130 commands tracked, 0 falls (upright and |mean v - cmd| <= max(0.1, 20%) per axis (wz: max(0.15, 20%)); 6 s per command). Best tracked pure commands:

- forward +1.09 m/s (command +1.20, peak torque 73%), backward -0.59 m/s (command -0.60, peak torque 71%)
- left +0.36 m/s (command +0.45, peak torque 63%), right -0.37 m/s (command -0.45, peak torque 59%)
- yaw left +0.78 rad/s (command +0.90, peak torque 42%), yaw right -0.86 rad/s (command -0.90, peak torque 43%)

![command envelope](envelope.png)

Self-contact on the CAD hulls: 0/130 commands (0 inside the trained ranges).

## Command envelope (rough ground)

117/130 commands tracked, 0 falls (upright and |mean v - cmd| <= max(0.1, 20%) per axis (wz: max(0.15, 20%)); 6 s per command). Best tracked pure commands:

- forward +1.11 m/s (command +1.20, peak torque 74%), backward -0.59 m/s (command -0.60, peak torque 70%)
- left +0.36 m/s (command +0.45, peak torque 64%), right -0.36 m/s (command -0.45, peak torque 60%)
- yaw left +0.78 rad/s (command +0.90, peak torque 42%), yaw right -0.87 rad/s (command -0.90, peak torque 44%)

![command envelope](envelope_rough.png)

Self-contact on the CAD hulls: 0/130 commands (0 inside the trained ranges).

## Latency sensitivity (CAD model, added sensing / actuation delay)

| sensing delay | actuation delay | turn 0.3 rad/s tracked | forward 0.3 m/s tracked |
|---|---|---|---|
| 0 ms | 0 ms | 80% | 98% |
| 10 ms | 0 ms | 77% | 94% |
| 20 ms | 0 ms | 75% | 88% |
| 0 ms | 10 ms | 77% | 94% |
| 10 ms | 10 ms | 75% | 88% |
| 20 ms | 10 ms | 73% | 85% |
| 30 ms | 10 ms | 69% | 81% |
| 40 ms | 20 ms | 67% | 77% |

## Push recovery (0.1 s torso pulse while walking at 0.5 m/s, CAD model)

| direction | largest survived impulse | CoM velocity change |
|---|---|---|
| forward | 44.1 N·s | 1.31 m/s |
| backward | 46.4 N·s | 1.38 m/s |
| left | 29.5 N·s | 0.88 m/s |
| right | 57.7 N·s | 1.72 m/s |

Standing (zero command), largest survived impulse: forward 11.7 N·s, backward 18.3 N·s, left 46.4 N·s, right 51.6 N·s.

## Power (CAD model; electrical model of calculations/run_power_budget.py, no regeneration)

| scenario | command | mean | peak | mean current (nominal V) | runtime, 13S2P 50S (80 %) | foot lift-offs |
|---|---|---|---|---|---|---|
| stand | (+0.0, +0.0, +0.0) | 79 W | 79 W | 1.7 A | 4.72 h | 0.00/s |
| walk_0.3 | (+0.3, +0.0, +0.0) | 236 W | 294 W | 5.0 A | 1.59 h | 2.51/s |
| walk_0.5 | (+0.5, +0.0, +0.0) | 284 W | 376 W | 6.1 A | 1.32 h | 2.51/s |
| walk_0.8 | (+0.8, +0.0, +0.0) | 363 W | 504 W | 7.8 A | 1.03 h | 2.51/s |
| turn_0.5 | (+0.0, +0.0, +0.5) | 208 W | 292 W | 4.4 A | 1.80 h | 2.51/s |

Worst actuator RMS current vs rated: hip_yaw 29% (walk_0.8), hip_roll 71% (walk_0.8), hip_pitch 34% (walk_0.8), knee 59% (walk_0.8), ankle_motor 79% (walk_0.8)

Torque-speed envelope (|tau| / (peak torque * (1 - |omega| / no-load speed at 41.6 V)), linear stall-to-no-load line (conservative: the real curve is flat up to its corner speed); worst point per actuator): hip_yaw 25% (8.9 N·m at 0.2 rad/s, turn_0.5), hip_roll 49% (29.3 N·m at 0.1 rad/s, walk_0.8), hip_pitch 33% (38.2 N·m at 0.8 rad/s, walk_0.8), knee 38% (41.8 N·m at 1.7 rad/s, walk_0.8), ankle_motor 88% (30.1 N·m at 2.0 rad/s, walk_0.8).

## ROS 2 jazzy: separate node processes driven over `/cmd_vel`, measured from `/jx1/odom`

Same script on every path: forward 0.4 m/s for 10 s, turn 0.4 rad/s for 6 s (137.5° commanded), stop.

| started by | forward speed | turn | max tilt | upright |
|---|---|---|---|---|
| python -m (source tree) | 0.38 m/s | 108° | 5.8° | True |
| ros2 launch jx1_bringup mujoco_sim.launch.py (colcon install) | 0.38 m/s | 108° | 5.8° | True |
| ros2 launch jx1_bringup ros2_control.launch.py (colcon install) | 0.34 m/s | 103° | 5.4° | True |

| phase | command | distance | mean speed | yaw change | min pelvis z | max tilt |
|---|---|---|---|---|---|---|
| forward | (+0.4, +0.0, +0.0) | 3.77 m | 0.38 m/s | -17.6° | 0.568 m | 5.8° |
| turn | (+0.0, +0.0, +0.4) | 0.17 m | 0.03 m/s | +108.5° | 0.569 m | 4.9° |
| stop | (+0.0, +0.0, +0.0) | 0.01 m | 0.00 m/s | -0.8° | 0.573 m | 2.5° |

## Hardware-in-the-loop: policy → `hw_node` → hub protocol → hub-firmware twin → physics

`jx1_policy -> jx1_hw hw_node -> hub protocol over TCP -> fake_hub (firmware law) -> MuJoCo`. RUN accepted: True, upright: True, hub faults at the end: none.

| phase | command | distance | mean speed | yaw change | min pelvis z | max tilt |
|---|---|---|---|---|---|---|
| stand | (+0.0, +0.0, +0.0) | 0.00 m | 0.00 m/s | -0.6° | 0.585 m | 2.0° |
| forward | (+0.3, +0.0, +0.0) | 2.63 m | 0.26 m/s | -12.3° | 0.566 m | 5.8° |
| turn | (+0.0, +0.0, +0.3) | 0.19 m | 0.03 m/s | +73.0° | 0.568 m | 5.0° |
| stop | (+0.0, +0.0, +0.0) | 0.01 m | 0.00 m/s | -0.1° | 0.572 m | 3.2° |

At the top trained speed through the same chain (`hw_loop_check.py --fast`, hub torque caps 80 % of peak): 0.8 m/s commanded -> 0.70 m/s, max tilt 7.2°, upright True.

Started as on the robot, `ros2 launch jx1_hw hardware.launch.py hil:=true (colcon install)`: forward 0.26 m/s at 0.3, turn 74° of 103° commanded, upright True, RUN accepted True.
