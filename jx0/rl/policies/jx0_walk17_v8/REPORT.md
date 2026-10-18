# jx0_walk17_v8: JX0 v0.5 (55 cm, two-eye head) whole-body walking policy - PASSES the test suite and the parts clearance check

| | |
|---|---|
| Robot | JX0 v0.5: 54.6 cm, 3.05 kg, legs 1.5x v0.4's (thigh 93 mm, shin 87 mm), a 157 g head with two WS2812 ring eyes |
| Policy | 17 joint corrections at 50 Hz on top of the reference gait: target = q_ref(phase, command) + 0.25 × output |
| Inputs | 176 observations: 3 frames of body rate, gravity, joint angles, speeds and last outputs, plus the command and the gait clock |
| Training | `rl/train.py --config jx0/rl/config/jx0_walk17.yaml` (MuJoCo, 1024 robots) v7 (from scratch to 3000, then 1000 more after the side-step reference was relabelled) fine-tuned 1000 iterations for the heavier two-eye head; about 125 min in all on the design laptop |
| Reference gait | `jx0/rl/config/jx0_gait_reference.json`, blended from the robot's verified gaits (v0.5 side steps: the foot on that side steps out 30 mm, the other closes) |

## What changed from v0.4's policy (v5)

- v5 on the v0.5 robot passes 5 of 11 speeds: it walks 1.5x too fast on the longer legs and falls side-stepping right.
- The first v0.5 policies (v6) passed the MuJoCo suite but were wrong on the real parts. The training model's simplified leg collision shapes let them stand with the legs pressed together, at the hip-roll servos' stall torque (2.94 N·m), and the test model, which has no leg-on-leg contact, let the feet pass into each other (46 mm apart). Fixed in training: `model.legs_collide: false` plus `rewards.feet_distance` (a penalty below 85 mm of sideways foot spacing). Fixed in testing: `jx0/rl/policy_clearance.py`, which checks the policy's poses on the SolidWorks parts.
- The old side gait brought the feet to 72 mm, where the ankle brackets clash (verify_cad). The v0.5 side gait leads with the foot on that side (`GaitParams.lead = "side"`): spacing 90-120 mm, hip roll up to 16.3° (limit 18°). That limits side steps to 0.02 m/s (v0.4 tested 0.03).

Test suite: `jx0/rl/sim2sim_jx0.py`, the verified JX0 model at 1 kHz with the STS3215's torque-speed limit, goals on a 100 Hz bus and the robot's own clamps.

Overall: **PASS** {'speeds': True, 'pushes': True, 'endurance': True, 'latency': True}; clearance **PASS** (1700 poses, no contact between parts)

## Speeds

10 s each, the average of the last 7 s in the robot's frame (vx m/s, vy m/s, wz rad/s).

| Test | Command | Achieved | Peak torque / stall | |
|---|---|---|---|---|
| stand | (0.0, 0.0, 0.0) | (-0.0, -0.0, 0.002) | 0.87 | pass |
| forward_0.03 | (0.03, 0.0, 0.0) | (0.033, 0.002, -0.007) | 1.0 | pass |
| forward_0.06 | (0.06, 0.0, 0.0) | (0.062, 0.003, -0.007) | 1.0 | pass |
| forward_0.08 | (0.08, 0.0, 0.0) | (0.082, 0.003, -0.008) | 1.0 | pass |
| forward_0.10 | (0.1, 0.0, 0.0) | (0.093, 0.003, 0.068) | 1.0 | pass |
| backward_0.04 | (-0.04, 0.0, 0.0) | (-0.047, -0.0, -0.008) | 1.0 | pass |
| left_0.02 | (0.0, 0.02, 0.0) | (-0.001, 0.026, -0.021) | 1.0 | pass |
| right_0.02 | (0.0, -0.02, 0.0) | (-0.0, -0.022, -0.014) | 0.92 | pass |
| turn_left_0.3 | (0.0, 0.0, 0.3) | (-0.002, 0.001, 0.285) | 0.96 | pass |
| turn_right_0.3 | (0.0, 0.0, -0.3) | (-0.003, 0.002, -0.303) | 0.96 | pass |
| forward_turn | (0.06, 0.0, 0.2) | (0.058, 0.002, 0.195) | 1.0 | pass |

## Pushes

Horizontal shoves on the torso: 0.1 s pulses from the front, back, left and right, at 4 moments of the gait.

- walking 0.24 N·s: stayed up 16/16
- walking 0.48 N·s: stayed up 16/16
- walking 0.72 N·s: stayed up 16/16
- standing 0.24 N·s: stayed up 16/16
- standing 0.48 N·s: stayed up 16/16
- standing 0.72 N·s: stayed up 16/16

## 60 s endurance

12 commands, 5 s each, with a 0.24 N·s push every 7 s:
- stayed up the whole 60.0 s and walked 2.24 m;
- at most 0.0° past a commanded limit, 0 ms at a printed stop;
- worst servo mean torque 0.582 N·m (left_hip_roll_joint), under the rated 0.98 N·m; the peaks reach the stall torque.

## Latency

6 ms more sensing delay and 6 ms more actuation delay. Pass means each axis within 50 %.

| Test | Command | Achieved | |
|---|---|---|---|
| forward_0.06 | (0.06, 0.0, 0.0) | (0.064, 0.004, 0.001) | pass |
| left_0.02 | (0.0, 0.02, 0.0) | (0.002, 0.03, -0.0) | pass |
| turn_left_0.3 | (0.0, 0.0, 0.3) | (-0.004, 0.002, 0.287) | pass |

## Not tested

- On the real robot (`python -m jx0bot.policy --bundle ../rl/policies/jx0_walk17_v8`).
- In Isaac Sim: the same task (`Isaac-Velocity-Flat-JX0-Full-v0`) has not been run here.

Video: `media/jx0_rl_walk17_v8.mp4` (the endurance run). Drive it live:

```bash
rl/.venv/Scripts/python jx0/rl/play_jx0.py --policy jx0/rl/policies/jx0_walk17_v8
```
