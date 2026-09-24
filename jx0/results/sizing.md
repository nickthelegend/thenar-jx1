# JX0 servo sizing (CALCULATED (servo data and masses ASSUMED until measured))

Design `jx0/design_point.yaml`, total mass 2.07 kg, walking hip height 0.222 m. Servo: Feetech ST3215-C018 / Waveshare ST3215 12 V serial bus servo (30 kg·cm stall, 10 kg·cm rated at 12 V); stall 2.94 N·m, rated 0.98 N·m (assumed 1/3 of stall), no-load 4.72 rad/s.
Checks: 1.5 x dynamic peak (1.25 x static) <= stall; 1.3 x walking RMS <= rated; 1.5 x torque within the linear torque-speed line at every sample.

| Joint | Dynamic peak N·m (scenario) | Static peak N·m (case) | Required peak | Peak margin | Walking RMS | Continuous margin | Peak speed rad/s | Torque-speed use | Pass |
|---|---|---|---|---|---|---|---|---|---|
| hip_yaw | 0.095 (turn_10deg_per_step) | 0.0 (stand_deep_squat) | 0.142 | 20.71 | 0.025 | 29.83 | 0.73 | 5 % (turn_10deg_per_step) | yes |
| hip_roll | 1.038 (walk_nominal_0.067ms) | 1.211 (single_leg_cop_outer_edge) | 1.557 | 1.89 | 0.519 | 1.45 | 1.51 | 61 % (walk_nominal_0.067ms) | yes |
| hip_pitch | 0.334 (walk_fast_0.073ms) | 0.231 (single_leg_cop_heel) | 0.502 | 5.86 | 0.099 | 7.62 | 2.95 | 24 % (walk_fast_0.073ms) | yes |
| knee | 0.633 (walk_nominal_0.067ms) | 0.825 (single_leg_cop_inner_edge) | 1.031 | 2.85 | 0.345 | 2.19 | 3.65 | 39 % (walk_fast_0.073ms) | yes |
| ankle_pitch | 0.23 (walk_fast_0.073ms) | 1.094 (single_leg_cop_heel) | 1.367 | 2.15 | 0.084 | 8.97 | 2.78 | 15 % (walk_fast_0.073ms) | yes |
| ankle_roll | 0.094 (turn_10deg_per_step) | 0.61 (single_leg_cop_inner_edge) | 0.762 | 3.86 | 0.023 | 32.21 | 1.51 | 6 % (walk_nominal_0.067ms) | yes |

| Scenario | ZMP tracking error (mm) |
|---|---|
| walk_slow_0.05ms | 8.16 |
| walk_nominal_0.067ms | 8.16 |
| walk_fast_0.073ms | 8.16 |
| turn_10deg_per_step | 8.16 |
| squat_4.5cm_1.6s | 8.15 |

![sizing](sizing.png)
