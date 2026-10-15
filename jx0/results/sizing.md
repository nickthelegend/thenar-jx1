# JX0 servo sizing (CALCULATED (servo data and masses ASSUMED until measured))

Design `jx0/design_point.yaml`, total mass 2.88 kg, walking hip height 0.14 m. Servo: Feetech STS3215 12 V serial bus servo (ST3215-C018 / Waveshare ST3215; 30 kg·cm stall, 10 kg·cm rated at 12 V); stall 2.94 N·m, rated 0.98 N·m (assumed 1/3 of stall), no-load 4.72 rad/s.
Checks: 1.5 x dynamic peak (1.25 x static) <= stall; 1.3 x walking RMS <= rated; 1.5 x torque within the linear torque-speed line at every sample.

| Joint | Dynamic peak N·m (scenario) | Static peak N·m (case) | Required peak | Peak margin | Walking RMS | Continuous margin | Peak speed rad/s | Torque-speed use | Pass |
|---|---|---|---|---|---|---|---|---|---|
| hip_yaw | 0.095 (turn_10deg_per_step) | 0.0 (stand_double) | 0.142 | 20.73 | 0.017 | 45.38 | 0.73 | 5 % (turn_10deg_per_step) | yes |
| hip_roll | 1.331 (turn_10deg_per_step) | 1.609 (single_leg_cop_outer_edge) | 2.012 | 1.46 | 0.667 | 1.13 | 1.59 | 83 % (walk_brisk_0.055ms) | yes |
| hip_pitch | 0.245 (walk_brisk_0.055ms) | 0.19 (single_leg_cop_toe) | 0.368 | 7.99 | 0.093 | 8.08 | 3.52 | 19 % (walk_brisk_0.055ms) | yes |
| knee | 0.707 (turn_10deg_per_step) | 1.059 (single_leg_cop_inner_edge) | 1.324 | 2.22 | 0.387 | 1.95 | 4.03 | 69 % (walk_brisk_0.055ms) | yes |
| ankle_pitch | 0.26 (walk_brisk_0.055ms) | 1.29 (single_leg_cop_heel) | 1.613 | 1.82 | 0.093 | 8.06 | 3.57 | 25 % (walk_brisk_0.055ms) | yes |
| ankle_roll | 0.646 (turn_10deg_per_step) | 0.846 (single_leg_cop_inner_edge) | 1.058 | 2.78 | 0.304 | 2.48 | 1.59 | 45 % (turn_10deg_per_step) | yes |

| Scenario | ZMP tracking error (mm) |
|---|---|
| walk_slow_0.042ms | 2.04 |
| walk_nominal_0.05ms | 2.15 |
| walk_brisk_0.055ms | 2.3 |
| turn_10deg_per_step | 2.32 |
| squat_2.5cm_1.6s | 0.78 |

![sizing](sizing.png)
