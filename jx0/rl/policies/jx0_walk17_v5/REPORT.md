# jx0_walk17_v5: JX0 whole-body walking policy - PASSES the test suite

| | |
|---|---|
| Policy | 17 joint corrections at 50 Hz on top of the reference gait: target = q_ref(phase, command) + 0.25 × output |
| Inputs | 176 observations: 3 frames of body rate, gravity, joint angles, speeds and last outputs, plus the command and the gait clock |
| Training | `rl/train.py --config jx0/rl/config/jx0_walk17.yaml` (MuJoCo, 1024 robots), iteration 1500, about 40 min on the design laptop |
| Reference gait | `jx0/rl/config/jx0_gait_reference.json`, blended from the robot's verified gaits (`jx0/rl/gait_reference.py`) |

Test suite: `jx0/rl/sim2sim_jx0.py`. It runs the verified JX0 model, not the training model, at 1 kHz:
- each servo modelled with the STS3215's torque-speed limit;
- goals sent on a 100 Hz bus;
- the robot's own clamps applied (joint limits, couple_hips).

Overall: **PASS** {'speeds': True, 'pushes': True, 'endurance': True, 'latency': True}

## Speeds

10 s each, the average of the last 7 s in the robot's frame (vx m/s, vy m/s, wz rad/s).

| Test | Command | Achieved | |
|---|---|---|---|
| stand | (0.0, 0.0, 0.0) | (0.0, 0.0, -0.0) | pass |
| forward_0.03 | (0.03, 0.0, 0.0) | (0.036, -0.0, -0.008) | pass |
| forward_0.06 | (0.06, 0.0, 0.0) | (0.062, -0.0, -0.011) | pass |
| forward_0.08 | (0.08, 0.0, 0.0) | (0.079, -0.0, -0.012) | pass |
| forward_0.10 | (0.1, 0.0, 0.0) | (0.096, 0.0, -0.009) | pass |
| backward_0.04 | (-0.04, 0.0, 0.0) | (-0.04, 0.001, -0.003) | pass |
| left_0.03 | (0.0, 0.03, 0.0) | (-0.001, 0.026, -0.024) | pass |
| right_0.03 | (0.0, -0.03, 0.0) | (-0.002, -0.025, 0.013) | pass |
| turn_left_0.3 | (0.0, 0.0, 0.3) | (0.003, 0.002, 0.281) | pass |
| turn_right_0.3 | (0.0, 0.0, -0.3) | (0.002, -0.003, -0.304) | pass |
| forward_turn | (0.06, 0.0, 0.2) | (0.056, 0.003, 0.197) | pass |

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
- stayed up the whole 60.0 s and walked 2.12 m;
- at most 1.82 ° past a commanded limit (a servo flexing under load), so it never reached a printed stop;
- worst servo mean torque 0.684 N·m (left_hip_roll_joint), under the rated 0.98 N·m;
- the run simulated 2.13× faster than real time.

## Latency

6 ms more sensing delay and 6 ms more actuation delay. Pass means each axis within 50 %.

| Test | Command | Achieved | |
|---|---|---|---|
| forward_0.06 | (0.06, 0.0, 0.0) | (0.063, 0.003, -0.046) | pass |
| left_0.03 | (0.0, 0.03, 0.0) | (-0.002, 0.026, -0.038) | pass |
| turn_left_0.3 | (0.0, 0.0, 0.3) | (0.006, 0.003, 0.163) | pass |

## Not tested

- On the real robot: there is no jx0bot runner for the policy yet.
- In Isaac Sim: the same task is ready (`Isaac-Velocity-Flat-JX0-Full-v0`) but has not been run.

Video: `media/jx0_rl_walk17_v5.mp4` (the endurance run). Drive it live:

```bash
rl/.venv/Scripts/python jx0/rl/play_jx0.py --policy jx0/rl/policies/jx0_walk17_v5
```
