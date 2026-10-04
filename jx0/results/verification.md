# JX0 verification report

Generated 2026-10-05 by `jx0/verify/run_all.py` from the CAD geometry, the MuJoCo model and the robot software in this repository (design v0.4: double-sided legs like the reference robot). Everything here is simulation and analysis: the physical robot is not built yet, so the numbers say the design should work, not that it has been seen working.

## Summary

| Check | Result |
|---|---|
| Servo sizing (every leg joint, 5 gaits + 8 static cases, 1.25–1.5x margins) | **ALL PASS** |
| The 14 robot gaits, closed loop on the servo model (100 Hz) | **14/14 pass**, peak servo load 55% of stall |
| Parts and servos colliding, standing (all 666 pairs) | 0 clashes |
| Parts colliding in motion (1373 poses: every gait frame + every action) | 0 clashes |
| Joint limits inside the collision-free range | 17/17 joints |
| Leg joints: single-sided (v0.3) vs double-sided (v0.4), beam model, fatigue safety factor | v0.3 0.18–0.51 (**would break**) → v0.4 **4.7–8.0** |
| Printed leg brackets, voxel FEA under the simulated loads, worst bracket | fatigue SF **2.3**, strength SF **3.0** |
| Walking with realistic model errors (latency 0–20 ms), all gaits | **139/140 (99 %)** |
| Same, stress test with 40 ms latency | 121/140 (86 %) |
| Sideways push of 0.24 N.s mid-walk (24 moments × 2 directions): stayed up | 48/48 (100 %) |
| Sideways push of 0.48 N.s mid-walk (24 moments × 2 directions): stayed up | 48/48 (100 %) |
| Sideways push of 0.72 N.s mid-walk (24 moments × 2 directions): stayed up | 48/48 (100 %) |
| Sideways push of 0.96 N.s mid-walk (24 moments × 2 directions): stayed up | 48/48 (100 %) |
| Sideways push of 1.20 N.s mid-walk (24 moments × 2 directions): stayed up | 42/48 (88 %) |
| Sideways push of 1.44 N.s mid-walk (24 moments × 2 directions): stayed up | 21/48 (44 %) |
| Whole robot program, 8-step mission, random realistic errors | **24/24 (100 %)** |
| Battery current walking (servos + Pi) | 1.44 A average, 2.5 A peak → about 73 min walking per charge |
| 100 Hz control loop on a Raspberry Pi 4 (estimated) | 1.79 ms of 10 ms |
| Software unit tests | Ran 21 tests in 5.690s: OK |

## Leg joints: why double-sided

Every leg joint's load from the simulation (14 gaits, 42 walks with model errors, 48 pushes of 0.96 N·s), and what it does to a single-sided joint (v0.3: one plate on the servo's horn) and to a U-bracket on both faces (v0.4). The servo only *drives* the torque about its axis; the bending moment about the other two axes is what the structure carries. On a single-sided joint it all goes through one printed plate and the servo's output shaft. In a U-bracket it becomes a pair of forces in the two arms, 42.75 mm apart, and the output shaft sees no bending at all. PETG ASSUMED: 50 MPa static, 15 MPa fatigue (10^6 cycles, about 700 hours of walking).

| Joint | Torque N·m | Bending at the horn N·m | v0.3 plate MPa (fatigue SF) | v0.4 MPa (fatigue SF) | Servo shaft bending N·m, v0.3 → v0.4 |
|---|---|---|---|---|---|
| hip yaw | 1.03 | 2.97 | 54.1 (0.28) | 4.5 (3.3) — single-sided + thrust ring | 2.97 → 2.63 |
| hip roll | 2.77 | 2.33 | 29.5 (0.51) | 1.9 (8.0) | 2.33 → 0.0 |
| hip pitch | 1.85 | 3.63 | 40.1 (0.37) | 3.1 (4.8) | 3.63 → 0.0 |
| knee | 2.49 | 3.17 | 34.1 (0.44) | 3.2 (4.7) | 3.17 → 0.0 |
| ankle pitch | 2.37 | 2.81 | 50.0 (0.3) | 2.7 (5.5) | 2.81 → 0.0 |
| ankle roll | 1.75 | 3.53 | 84.8 (0.18) | 2.6 (5.7) | 3.53 → 0.0 |

## Printed leg brackets: finite elements

Voxel FEA (`calculations/structural/voxel_fea.py`, 0.7 mm hexahedra with bending modes). Each bracket is held where it bolts to the servo above it (horn and rear hub) and loaded where the next servo is screwed into its cage, with that joint's actual 6-axis load every 10 ms of the simulation (all components at the same instant). Stress = 99.9th percentile of each element's worst von Mises, away from the bolted faces.

| Bracket | Elements | Walking MPa (fatigue SF) | Worst with pushes MPa (strength SF) |
|---|---|---|---|
| pelvis | 168,724 | 2.18 (6.9) | 4.54 (11.0) |
| hip yaw bracket | 149,405 | 4.47 (3.4) | 10.1 (5.0) |
| hip roll bracket | 84,757 | 5.57 (2.7) | 12.75 (3.9) |
| thigh | 124,302 | 6.58 (2.3) | 14.78 (3.4) |
| shin | 73,504 | 5.97 (2.5) | 15.48 (3.2) |
| ankle bracket | 104,758 | 6.17 (2.4) | 16.54 (3.0) |
| foot | 142,492 | 3.11 (4.8) | 7.61 (6.6) |

Stress maps: `images/fea_*.png`.

## What the verification found and fixed

### v0.4 (double-sided legs, 2026-10-05)

- **Single-sided joints would break** (the builder's own call, confirmed): with v0.4's loads, a v0.3-style joint's printed plate sees 30–85 MPa every step, above PETG's fatigue strength at every leg joint, and the servo's output shaft carries up to 3.6 N·m of bending. Every leg pitch and roll joint is now a U-bracket on the servo's horn and rear hub, the servo body screwed into a cage, like the reference robot.
- **The first U-brackets had weak joints between the arms and the next servo's cage** (voxel FEA): the shin's arms met the ankle cage through two 18 × 3 mm tabs, the ankle bracket through 2.5 mm bands, the hip-yaw disc through a thin plate. Solid plates now join each arm to its cage over the whole overlap; cage rear plates went from 2.4 to 4 mm (screw heads counterbored), arms from 3.5 to 4.5 mm; the hip-yaw bracket got a 7 mm disc, a keel and a solid block; the hip-roll bracket a 10 × 16 mm bridge.
- **The final masses (2.85 kg) raised the loads by about a tenth**, and two spots fell below a safety factor of 2: the shin's back plate beside the ankle servo's hub hole (strength 1.9: a screw counterbore 0.1 mm from the hole, no side wall at that corner) and the ankle bracket's inboard arm where it meets the roll cage (fatigue 1.8). The shin's plate is now 4 mm everywhere the ankle bracket's boss does not slide, with a 20 mm hub hole and that one screw left out; the ankle bracket's inboard arm reaches 4.5 mm lower (the foot's bracket only comes within 12 mm below the axis there): shin 2.5 / 3.2, ankle bracket 2.4 / 3.0.
- **Assembly**: plates that cover a cage would have locked the servo out. The knee cage is open at the front and the ankle cage at the bottom (the servos slide in there), with screwdriver holes through the arms for the far case screws.
- **Shorter legs swayed 26° sideways and pushed the ankle-roll servo against its stop** (100 % of stall): the gaits now keep the zero-moment point 20 mm inside each foot (planner option `zmp_offset_y`, chosen by Monte Carlo over 0–20 mm and 0.45–0.6 s steps): 15° at most, 50 % peak load.
- **Knee speed**: with 62/58 mm leg links the knee swings faster; 0.5 s steps reach the servo's no-load speed. The gaits keep 0.6 s steps (sizing: 68% of the torque-speed line at 0.55 s).
- **Collision ranges re-measured** for every joint; limits set inside them (left leg: hip roll −20…22°, hip pitch −70…8°, knee 0…84°, ankle roll ±20°; every range the gaits use is inside).

### v0.3 (2026-10-04)

- Shoulder servos inside the chest cap; a hip gusset into the hip-pitch servo; the foot grazing the ankle-pitch servo; ankle brackets touching in side-steps; limits allowing collisions — all fixed then. Walking robustness: 100 Hz control, a lower stance, 2- and 4-step blocks. An over-claimed push result (one lucky timing) and a wrong battery estimate were corrected.

## Honest limits

- **Pushes**: 0.24 N.s stays up 100 %, 0.48 N.s stays up 100 %, 0.72 N.s stays up 100 %, 0.96 N.s stays up 100 %, 1.20 N.s stays up 88 %, 1.44 N.s stays up 44 % of 48 timed pushes mid-walk. Harder shoves need a step to a new place; the gait player does not re-plan its steps (a capture-point stepper is in `jx0bot/stepper.py`, not yet enabled).
- **The hip-yaw joint is still single-sided**, as on the reference robot (its yaw servo stands under the body): there is no room for a second support between the yaw servo and the hip-roll servo. A thrust ring under the pelvis carries the leg's axial load and part of the bending; the yaw servo's output shaft and its two bearings carry the rest: about 1.2 N·m in normal walking, 2.3 N·m on a randomly wrong robot, 2.6 N·m in the hardest pushes (Feetech publishes no rating for it). Check the yaw horns for play after the first hours of walking; a retainer lip under the yaw disc (so the pelvis holds it from above and below) is the upgrade path.
- **Material and servo data are assumed**: PETG strengths (50 / 15 MPa), the STS3215's rear hub screw pattern (assumed equal to the horn's), and the servo stiffness (60 N·m/rad, 0.6–1.4x tested). Print a test U-bracket and fit-check a servo before printing the rest; measure the servo stiffness (bringup.md step 5).
- **Speed**: about 5 cm/s. The short legs make the knee the speed limit of the STS3215 at 12 V.
- **Latency**: the robot needs its control loop to react within about 20 ms (estimate on the Pi: about 8 ms). At 40 ms, long walks often fail; 2- and 4-step blocks mostly survive.
- **Not tested here**: falls (the model has no body collisions, so a fall's impact on the brackets is not simulated), carpet or very slippery floors (friction below 0.5), stairs, the I2S audio overlay on the Pi, screw fit in the printed holes, long-term servo heating.

## Re-run

```bash
python jx0/verify/run_all.py
```

Detailed results in this folder: `walking.json`, `verify_cad.json`, `verify_robustness.json`, `verify_strength.json`, `verify_fea.json`, `verify_power.json`, `sizing.json`.
