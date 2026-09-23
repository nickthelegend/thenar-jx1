# Reference humanoid study — what JX1 learned from 29 robots

**Date:** 2026-09-24. **Evidence:** 43 official URDF/MJCF files parsed with our own forward kinematics, plus official product pages and papers.
Full per-robot sections, per-file extraction tables and every source URL are in [`raw/reference_robots_raw.md`](raw/reference_robots_raw.md) (235 kB).
Labels: **VERIFIED** = read on an official page/file; **ESTIMATED** = derived by us (method in the raw file); **UNVERIFIED** = secondary source.

## 1. Closest-size references (1.14–1.40 m)

| Robot | Height | Mass | Leg DOF | Hip order | Ankle | Knee actuator | Price | Label |
|---|---|---|---|---|---|---|---|---|
| **Menlo Asimov 1** (open source) | 1.20 m | 35 kg | 6 | pitch-roll-yaw | parallel (RSU bars) | Encos 75 N·m | US$20k kit | VERIFIED |
| **Unitree R1** | 1.23 m | 27–29 kg | 6 | pitch-roll-yaw (pitch tilted 25°) | parallel, 2 × 33 N·m | 60 N·m @ 18.8 rad/s | US$4.9–5.9k | VERIFIED |
| **Booster T1** | 1.18 m | 30 kg | 6 | pitch-roll-yaw | parallel, 2 × 43 N·m | 130.5 N·m (model) | n/a | VERIFIED |
| **Unitree G1** | 1.32 m | 35 kg | 6 | pitch-roll-yaw (roll/yaw tilted 10°) | parallel A/B | 90/120 N·m official (139 in URDF) | US$13.5k | VERIFIED |
| **K-Scale K-Bot** (open) | 1.40 m | 34 kg | 5 | pitch-roll-yaw | pitch only | **RobStride RS04 120 N·m** | US$9–11k | VERIFIED |
| Fourier N1 | 1.25–1.30 m | 38–39 kg | 6 | pitch-roll-yaw | parallel | — | — | VERIFIED |
| AgiBot X1 / X2 | 1.30 m | 33–35 kg | 6 | pitch-roll-yaw | parallel (2 × PowerFlow R52) | — | — | VERIFIED |
| Roboparty Roboto Origin (open) | 1.25 m* | 34 kg* | 6 | yaw-roll-pitch | parallel rods | Damiao DM-J10010L | BOM CNY 49,713 | VERIFIED / *UNVERIFIED |
| Berkeley Humanoid Lite (open) | 0.80 m | 16 kg | 6 | tilted ±45° roll/yaw → pitch | serial | printed cycloid 15:1 | BOM US$4,312 | VERIFIED |
| ToddlerBot 2.0 (open) | 0.56 m | 3.4 kg | 6 | pitch-roll-yaw | serial | Dynamixel XM430 | US$5.7–7.3k | VERIFIED |
| Poppy Humanoid (open) | 0.83 m | 3.5 kg | 5 | roll-yaw-pitch | pitch only | Dynamixel MX-64 | — | VERIFIED |

## 2. Leg geometry for a 1.2 m robot vs JX1

Median (p25–p75) over 11 robots of 1.14–1.40 m, scaled to 1.20 m (ESTIMATED):

| Quantity | Reference | JX1 v0.3 | Comment |
|---|---|---|---|
| Thigh (hip centre → knee) | 0.28 m (0.24–0.29) | **0.270 m** | within band |
| Shin (knee → ankle pitch) | 0.27 m (0.265–0.29) | **0.300 m** | +0.03: needed to stack RS04 knee + two RS06 ankle motors + fork (G1 uses 0.300) |
| Ankle pitch → sole | ≈ 0.05 m (0.038–0.058) | **0.050 m** | within band |
| Hip → sole | 0.60–0.63 m | **0.620 m** | within band |
| Foot-centre spacing | 0.19–0.22 m (18 % of H) | **0.200 m** | within band; gives 60 mm between medial ankle motors |
| Foot | 0.18–0.22 × 0.06–0.10 m | **0.210 × 0.095 m** | within band |
| Shank+foot mass share | 8–10 % (G1, T1, R1, Asimov) | **≈ 7.6 %** (mass model) | G1-class, ankle motors high in the shank |

## 3. Peak-torque benchmarks scaled to JX1 (ESTIMATED)

Scaled from 15 RL-walking robots with τ* = τ/(M·g·L), L = 0.54 m; ranges are median–p75. Ankle values are
serial-equivalent (each motor of a parallel ankle carries roughly half, geometry-dependent).

| JX1 mass | Knee | Hip pitch | Hip roll | Hip yaw | Ankle pitch | Ankle roll |
|---|---|---|---|---|---|---|
| 25 kg | 71–94 N·m | 77–86 | 65–79 | 56–63 | 33–53 | 26–43 |
| 30 kg | 86–113 N·m | 93–104 | 78–94 | 67–76 | 39–64 | 32–51 |
| **JX1 selected (27.5 kg)** | **RS04 120** | **RS04 120** | **RS03 60** | **RS06 36** | **2 × RS06 → 46–58 (linkage)** | **51–65 (linkage)** |

Speed: median ≈ 13 rad/s at the joint, upper quartile ≈ 20 rad/s (G1 20–32). All JX1 leg classes reach 20–50 rad/s no-load at 48 V.

Our own physics-based requirement (`calculations/results/iter1_B_knee_and_pitch_RS04/report.md`) gives lower demands than the
reference field (e.g. hip roll 50 N·m vs 65–79 field) because it analyses ZMP walking up to 0.79 m/s with a 1.5 × margin; the
field sizes for falls, get-up and running. Where the two disagree JX1 follows the physics analysis but documents the gap
(hip roll and hip yaw are below field medians — see `docs/risk_register.md`).

## 4. Architecture lessons adopted, adapted or rejected

| Lesson (source) | JX1 decision | Why |
|---|---|---|
| Pitch-first hip dominates (15/27 robots) — heavy pitch motor on pelvis, huge flexion range | **Adapted: yaw-first (Y-R-P) with intersecting axes** (as H1, OP3, Roboto Origin) | Intersecting axes → closed-form IK, clean joint map; RS04 pitch actuator sits on the hip centre; flexion −115° achieved. Pitch-first is recorded as the V2 option (get-up/sit behaviours need > 135° flexion). |
| Two-motor parallel ankle, motors high in the shank (G1, R1, T1, K1, X1, Asimov) | **Adopted** | Cuts distal mass, shares pitch load across two motors. JX1 motors at 118/206 mm below the knee (R1 96/163, T1 96/156, X1 110/165). |
| Size the ankle linkage for workspace corners, not neutral (Booster T1/K1 analysis) | **Adopted** | JX1 sweep: pitch capacity 46–58 N·m and roll 51–65 N·m across −55°…+30° (`calculations/`), cond(J) ≤ 1.17. |
| Knee flexion ≥ 135° for get-up/kneel | **Partly**: 120° | Limited by thigh-disc / ankle-motor-A clearance in CAD; squat analysis needs 117°. V2: knee motor on the thigh top (−24 % hip-pitch torque in our sensitivity study). |
| Direct-drive knee (G1-class) vs linkage (Berkeley/Duke) | **Adopted direct drive** for V1 | Simplicity; thigh-mounted knee drive is the documented V2 improvement. |
| Orthogonal, untilted axes (Asimov 1 returned to them) | **Adopted** | Simplifies CAD, calibration, URDF and RL. |
| 48 V-class quick-swap battery, 200–500 Wh (R1: 33 V/199 Wh; G1: 13S/≈421 Wh) | **Adopted: 13S (48 V)** | Halves current vs 24 V (≈70 A vs 152 A at 3 kW); RobStride actuators are 48 V nominal. |
| Per-limb CAN buses | **Adopted** | RobStride uses classic CAN 1 Mbps: 6 joints/bus at 500 Hz ≈ 67–81 % load → legs get one bus each at ≤ 400–500 Hz (see `docs/electrical_architecture.md`). |
| Low-ratio planetary QDD actuators (7–25:1) | **Adopted (RobStride 9:1 / 7.75:1 / 10:1)** | Backdrivable, torque-controllable for sim-to-real. |
| Actuators are > 60 % of open-source BOMs (Roboto Origin 63 %) | **Confirmed** for JX1 | Drives the cost-reduction loop and the DIY V2 actuator path. |

## 5. What the four robots named in the brief teach

- **Unitree G1** — the product benchmark: parallel ankle, 13S battery, two-stage planetary PMSM actuators (N7520 at 14.3:1/22.5:1, N5020 ankle). Its model torque limits (88–139 N·m) are ≈ 1.5–2 × JX1's analysis demand; JX1 accepts a lower ceiling in exchange for cost.
- **Berkeley Humanoid Lite** — proof that 3-D-printed cycloidal actuators can walk a 16 kg robot, but it walks with legs capped at 6 N·m and its actuators cost US$94–188 each — **not** cheaper per N·m than RobStride/Damiao at JX1's scale (`research/raw/actuator_technology_raw.md` §3).
- **ToddlerBot** — shows the value of a sim-first, sys-ID'd model (fitted actuator curves) and of simplifying linkages away; informs JX1's MuJoCo/actuator-model pipeline.
- **Poppy** — an early open-source humanoid; its serial Dynamixel legs illustrate why modern designs moved to QDD actuators for walking.

## 6. Where this is used

- `requirements/robot_requirements.yaml` — dimensions, DOF, ranges and torque/speed targets cite this document.
- `calculations/design_point.yaml` — geometry values and their CALCULATED/ASSUMED labels.
- `actuators/actuator_selection.md` — class choice versus the τ* benchmarks above.
