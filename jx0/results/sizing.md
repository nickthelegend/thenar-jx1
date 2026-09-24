# JX0 servo sizing (CALCULATED (servo data and masses ASSUMED until measured))

Design `jx0/design_point.yaml`, total mass 1.81 kg, walking hip height 0.222 m. Servo: Waveshare ST3215 serial bus servo (19.5 kg·cm = 1.91 N·m stall at 7.4 V); stall 1.91 N·m, rated 0.64 N·m (assumed 1/3 of stall), no-load 4.72 rad/s.
Checks: 1.5 x dynamic peak (1.25 x static) <= stall; 1.3 x walking RMS <= rated; 1.5 x torque within the linear torque-speed line at every sample.

| Joint | Dynamic peak N·m (scenario) | Static peak N·m (case) | Required peak | Peak margin | Walking RMS | Continuous margin | Peak speed rad/s | Torque-speed use | Pass |
|---|---|---|---|---|---|---|---|---|---|
| hip_yaw | 0.084 (turn_10deg_per_step) | 0.0 (stand_double) | 0.125 | 15.22 | 0.018 | 27.16 | 0.73 | 7 % (turn_10deg_per_step) | yes |
| hip_roll | 0.906 (walk_nominal_0.067ms) | 1.012 (single_leg_cop_outer_edge) | 1.358 | 1.41 | 0.463 | 1.06 | 1.48 | 84 % (walk_nominal_0.067ms) | yes |
| hip_pitch | 0.322 (walk_fast_0.073ms) | 0.157 (single_leg_cop_heel) | 0.483 | 3.96 | 0.092 | 5.37 | 2.92 | 34 % (walk_fast_0.073ms) | yes |
| knee | 0.56 (walk_nominal_0.067ms) | 0.751 (single_leg_bent) | 0.938 | 2.04 | 0.311 | 1.58 | 3.6 | 53 % (walk_fast_0.073ms) | yes |
| ankle_pitch | 0.23 (walk_fast_0.073ms) | 1.082 (single_leg_cop_toe) | 1.353 | 1.41 | 0.079 | 6.25 | 2.78 | 22 % (walk_fast_0.073ms) | yes |
| ankle_roll | 0.084 (turn_10deg_per_step) | 0.532 (single_leg_cop_inner_edge) | 0.664 | 2.87 | 0.021 | 23.26 | 1.48 | 9 % (turn_10deg_per_step) | yes |

| Scenario | ZMP tracking error (mm) |
|---|---|
| walk_slow_0.05ms | 4.89 |
| walk_nominal_0.067ms | 4.89 |
| walk_fast_0.073ms | 4.89 |
| turn_10deg_per_step | 4.89 |
| squat_4.5cm_1.6s | 4.88 |

![sizing](sizing.png)
