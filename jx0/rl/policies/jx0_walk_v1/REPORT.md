# jx0_walk_v1: first learned JX0 policy (MuJoCo, rl/train.py, 1000 iterations)

Trained with `jx0/rl/config/jx0_walk.yaml` as it was then: one tracking tolerance (0.01) for speed and yaw rate. Tested
on the verified JX0 model (`sim2sim_jx0.py`: 1 kHz, STS3215 torque-speed line, 100 Hz bus, jx0bot clamps), 10 s each:

| Command | Achieved |
|---|---|
| stand | stands (8/8 scenarios stayed up) |
| forward 0.05 m/s | 0.059 m/s |
| forward 0.10 m/s | 0.091 m/s |
| backward 0.04 m/s | 0.014 m/s |
| sideways 0.04 m/s | ~0 (not learned) |
| turn 0.3 rad/s | ~0 (not learned) |

Peak torque reaches the servos' stall torque and peak speed 85-92 % of no-load: it uses the whole servo. Status:
walks forward, stands, does not turn or side-step yet. Not for the robot: the verified gait files remain the way JX0
walks. Video: `media/jx0_rl_walk_v1.mp4`.
