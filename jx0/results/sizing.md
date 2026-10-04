# JX0 servo sizing (CALCULATED (servo data and masses ASSUMED until measured))

Design `jx0/design_point.yaml`, total mass 2.44 kg, walking hip height 0.222 m. Servo: Feetech ST3215-C018 / Waveshare ST3215 12 V serial bus servo (30 kg·cm stall, 10 kg·cm rated at 12 V); stall 2.94 N·m, rated 0.98 N·m (assumed 1/3 of stall), no-load 4.72 rad/s.
Checks: 1.5 x dynamic peak (1.25 x static) <= stall; 1.3 x walking RMS <= rated; 1.5 x torque within the linear torque-speed line at every sample.

| Joint | Dynamic peak N·m (scenario) | Static peak N·m (case) | Required peak | Peak margin | Walking RMS | Continuous margin | Peak speed rad/s | Torque-speed use | Pass |
|---|---|---|---|---|---|---|---|---|---|
| hip_yaw | 0.097 (turn_10deg_per_step) | 0.0 (stand_double) | 0.146 | 20.19 | 0.024 | 31.05 | 0.73 | 5 % (turn_10deg_per_step) | yes |
| hip_roll | 1.152 (walk_nominal_0.067ms) | 1.355 (single_leg_cop_outer_edge) | 1.728 | 1.7 | 0.574 | 1.31 | 1.37 | 65 % (walk_nominal_0.067ms) | yes |
| hip_pitch | 0.323 (walk_fast_0.073ms) | 0.224 (single_leg_cop_heel) | 0.484 | 6.07 | 0.104 | 7.25 | 2.9 | 23 % (walk_fast_0.073ms) | yes |
| knee | 0.743 (turn_10deg_per_step) | 1.024 (single_leg_bent) | 1.28 | 2.3 | 0.413 | 1.82 | 3.62 | 43 % (turn_10deg_per_step) | yes |
| ankle_pitch | 0.222 (walk_fast_0.073ms) | 1.292 (single_leg_cop_heel) | 1.615 | 1.82 | 0.089 | 8.44 | 2.75 | 14 % (walk_fast_0.073ms) | yes |
| ankle_roll | 0.113 (walk_nominal_0.067ms) | 0.717 (single_leg_cop_inner_edge) | 0.896 | 3.28 | 0.027 | 28.08 | 1.37 | 8 % (walk_nominal_0.067ms) | yes |

| Scenario | ZMP tracking error (mm) |
|---|---|
| walk_slow_0.05ms | 3.96 |
| walk_nominal_0.067ms | 3.96 |
| walk_fast_0.073ms | 3.97 |
| turn_10deg_per_step | 3.96 |
| squat_4.5cm_1.6s | 3.95 |

![sizing](sizing.png)
