# JX0 servo sizing (CALCULATED (servo data and masses ASSUMED until measured))

Design `jx0/design_point.yaml`, total mass 2.43 kg, walking hip height 0.215 m. Servo: Feetech STS3215 12 V serial bus servo (ST3215-C018 / Waveshare ST3215; 30 kg·cm stall, 10 kg·cm rated at 12 V); stall 2.94 N·m, rated 0.98 N·m (assumed 1/3 of stall), no-load 4.72 rad/s.
Checks: 1.5 x dynamic peak (1.25 x static) <= stall; 1.3 x walking RMS <= rated; 1.5 x torque within the linear torque-speed line at every sample.

| Joint | Dynamic peak N·m (scenario) | Static peak N·m (case) | Required peak | Peak margin | Walking RMS | Continuous margin | Peak speed rad/s | Torque-speed use | Pass |
|---|---|---|---|---|---|---|---|---|---|
| hip_yaw | 0.096 (turn_10deg_per_step) | 0.0 (stand_deep_squat) | 0.143 | 20.49 | 0.024 | 31.81 | 0.73 | 5 % (turn_10deg_per_step) | yes |
| hip_roll | 1.151 (walk_nominal_0.067ms) | 1.353 (single_leg_cop_outer_edge) | 1.727 | 1.7 | 0.574 | 1.31 | 1.44 | 66 % (walk_nominal_0.067ms) | yes |
| hip_pitch | 0.292 (walk_fast_0.073ms) | 0.225 (single_leg_cop_heel) | 0.438 | 6.71 | 0.099 | 7.61 | 2.75 | 21 % (walk_fast_0.073ms) | yes |
| knee | 0.902 (turn_10deg_per_step) | 1.022 (single_leg_bent) | 1.354 | 2.17 | 0.511 | 1.47 | 3.02 | 51 % (turn_10deg_per_step) | yes |
| ankle_pitch | 0.197 (walk_fast_0.073ms) | 1.29 (single_leg_cop_heel) | 1.613 | 1.82 | 0.084 | 8.93 | 2.65 | 12 % (walk_fast_0.073ms) | yes |
| ankle_roll | 0.114 (turn_10deg_per_step) | 0.715 (single_leg_cop_inner_edge) | 0.894 | 3.29 | 0.027 | 27.9 | 1.44 | 8 % (turn_10deg_per_step) | yes |

| Scenario | ZMP tracking error (mm) |
|---|---|
| walk_slow_0.05ms | 5.32 |
| walk_nominal_0.067ms | 5.32 |
| walk_fast_0.073ms | 5.33 |
| turn_10deg_per_step | 5.32 |
| squat_4.5cm_1.6s | 5.31 |

![sizing](sizing.png)
