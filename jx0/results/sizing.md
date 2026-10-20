# JX0 servo sizing (CALCULATED (servo data and masses ASSUMED until measured))

Design `jx0/design_point.yaml`, total mass 3.10 kg, walking hip height 0.19 m. Servo: Feetech STS3215 12 V serial bus servo (ST3215-C018 / Waveshare ST3215; 30 kg·cm stall, 10 kg·cm rated at 12 V); stall 2.94 N·m, rated 0.98 N·m (assumed 1/3 of stall), no-load 4.72 rad/s.
Checks: 1.5 x dynamic peak (1.25 x static) <= stall; 1.3 x walking RMS <= rated; 1.5 x torque within the linear torque-speed line at every sample.

| Joint | Dynamic peak N·m (scenario) | Static peak N·m (case) | Required peak | Peak margin | Walking RMS | Continuous margin | Peak speed rad/s | Torque-speed use | Pass |
|---|---|---|---|---|---|---|---|---|---|
| hip_yaw | 0.103 (turn_10deg_per_step) | 0.0 (stand_double) | 0.154 | 19.09 | 0.017 | 44.16 | 0.73 | 6 % (turn_10deg_per_step) | yes |
| hip_roll | 1.412 (walk_nominal_0.05ms) | 1.712 (single_leg_cop_outer_edge) | 2.14 | 1.37 | 0.704 | 1.07 | 0.94 | 77 % (walk_brisk_0.055ms) | yes |
| hip_pitch | 0.209 (walk_brisk_0.055ms) | 0.237 (single_leg_cop_heel) | 0.314 | 9.37 | 0.091 | 8.31 | 2.23 | 14 % (walk_brisk_0.055ms) | yes |
| knee | 1.199 (turn_10deg_per_step) | 1.997 (single_leg_cop_inner_edge) | 2.497 | 1.18 | 0.676 | 1.11 | 2.39 | 63 % (turn_10deg_per_step) | yes |
| ankle_pitch | 0.174 (walk_brisk_0.055ms) | 1.441 (single_leg_cop_heel) | 1.802 | 1.63 | 0.073 | 10.36 | 2.33 | 12 % (walk_brisk_0.055ms) | yes |
| ankle_roll | 0.695 (turn_10deg_per_step) | 0.914 (single_leg_cop_inner_edge) | 1.142 | 2.57 | 0.332 | 2.27 | 0.94 | 42 % (turn_10deg_per_step) | yes |

| Scenario | ZMP tracking error (mm) |
|---|---|
| walk_slow_0.042ms | 2.53 |
| walk_nominal_0.05ms | 2.53 |
| walk_brisk_0.055ms | 2.53 |
| turn_10deg_per_step | 2.53 |
| squat_2.5cm_1.6s | 2.53 |

![sizing](sizing.png)
