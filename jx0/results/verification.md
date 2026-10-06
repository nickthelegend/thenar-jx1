# JX0 verification report

Generated 2026-10-06 by `jx0/verify/run_all.py` from the CAD geometry, the MuJoCo model and the robot software in this repository (design v0.4: double-sided legs like the reference robot). Everything here is simulation and analysis: the physical robot is not built yet, so the numbers say the design should work, not that it has been seen working.

## Summary

| Check | Result |
|---|---|
| Servo sizing (every leg joint, 5 gaits + 8 static cases, 1.25–1.5x margins) | **ALL PASS** |
| The 14 robot gaits, closed loop on the servo model (100 Hz) | **14/14 pass**, peak servo load 55% of stall |
| Parts and servos colliding, standing (all 741 pairs) | 0 clashes |
| Parts colliding in motion (1373 poses: every gait frame + every action) | 0 clashes |
| Joint limits inside the collision-free range | 17/17 joints |
| Leg joints: single-sided (v0.3) vs double-sided (v0.4), beam model, fatigue safety factor | v0.3 0.21–0.48 (**would break**) → v0.4 **4.4–7.5** |
| Printed leg brackets, voxel FEA under the simulated loads, worst bracket | fatigue SF **2.1**, strength SF **3.0** |
| Walking with realistic model errors (latency 0–20 ms), all gaits | **138/140 (99 %)** |
| Same, stress test with 40 ms latency | 123/140 (88 %) |
| Sideways push of 0.24 N.s mid-walk (24 moments × 2 directions): stayed up | 48/48 (100 %) |
| Sideways push of 0.48 N.s mid-walk (24 moments × 2 directions): stayed up | 48/48 (100 %) |
| Sideways push of 0.72 N.s mid-walk (24 moments × 2 directions): stayed up | 48/48 (100 %) |
| Sideways push of 0.96 N.s mid-walk (24 moments × 2 directions): stayed up | 48/48 (100 %) |
| Sideways push of 1.20 N.s mid-walk (24 moments × 2 directions): stayed up | 43/48 (90 %) |
| Sideways push of 1.44 N.s mid-walk (24 moments × 2 directions): stayed up | 21/48 (44 %) |
| Whole robot program, 8-step mission, random realistic errors | **24/24 (100 %)** |
| Battery current walking (servos + Pi) | 1.45 A average, 2.52 A peak → about 73 min walking per charge |
| 100 Hz control loop on a Raspberry Pi 4 (estimated) | 1.8 ms of 10 ms |
| Software unit tests | Ran 21 tests in 5.663s: OK |

## Leg joints: why double-sided

Every leg joint's load from the simulation (14 gaits, 42 walks with model errors, 48 pushes of 0.96 N·s), and what it does to a single-sided joint (v0.3: one plate on the servo's horn) and to a U-bracket on both faces (v0.4). The servo only *drives* the torque about its axis; the bending moment about the other two axes is what the structure carries. On a single-sided joint it all goes through one printed plate and the servo's output shaft. In a U-bracket it becomes a pair of forces in the two arms, 42.75 mm apart, and the output shaft sees no bending at all. The hip-yaw disc is held by the pelvis from both sides instead (thrust ring above, keeper below): its stresses are in the finite-element table. PETG ASSUMED: 50 MPa static, 15 MPa fatigue (10^6 cycles, about 700 hours of walking).

| Joint | Torque N·m | Bending at the horn N·m | v0.3 plate MPa (fatigue SF) | v0.4 MPa (fatigue SF) | Servo shaft bending N·m, v0.3 → v0.4 |
|---|---|---|---|---|---|
| hip yaw | 1.08 | 3.03 | 55.0 (0.27) | ring + keeper: 120 / 100 N pushes on the disc rim (FEA below) | 3.03 → 2.6 (ring only) → 0.55 |
| hip roll | 2.80 | 2.40 | 31.3 (0.48) | 2.0 (7.5) | 2.4 → 0.0 |
| hip pitch | 1.90 | 3.79 | 39.7 (0.38) | 3.3 (4.5) | 3.79 → 0.0 |
| knee | 2.50 | 3.36 | 33.7 (0.45) | 3.4 (4.4) | 3.36 → 0.0 |
| ankle pitch | 2.44 | 3.14 | 49.4 (0.3) | 2.9 (5.2) | 3.14 → 0.0 |
| ankle roll | 1.85 | 3.59 | 70.9 (0.21) | 2.8 (5.4) | 3.59 → 0.0 |

## Printed leg brackets: finite elements

Voxel FEA (`calculations/structural/voxel_fea.py`, 0.7 mm hexahedra with bending modes). Each bracket is held where it bolts to the servo above it (horn and rear hub) and loaded where the next servo is screwed into its cage, with that joint's actual 6-axis load every 10 ms of the simulation (all components at the same instant). Stress = 99.9th percentile of each element's worst von Mises, away from the bolted faces.

| Bracket | Elements | Walking MPa (fatigue SF) | Worst with pushes MPa (strength SF) |
|---|---|---|---|
| pelvis | 224,820 | 6.21 (2.4) | 9.77 (5.1) |
| yaw keeper | 8,022 | 7.07 (2.1) | 9.59 (5.2) |
| hip yaw bracket | 146,407 | 6.19 (2.4) | 13.76 (3.6) |
| hip roll bracket | 84,757 | 5.62 (2.7) | 13.4 (3.7) |
| thigh | 124,302 | 6.65 (2.3) | 14.83 (3.4) |
| shin | 73,504 | 6.06 (2.5) | 16.2 (3.1) |
| ankle bracket | 104,758 | 6.23 (2.4) | 16.68 (3.0) |
| foot | 142,492 | 3.13 (4.8) | 7.74 (6.5) |

Stress maps: `images/fea_*.png`.

## What the verification found and fixed

### v0.4 (double-sided legs, 2026-10-05)

- **Single-sided joints would break** (the builder's own call, confirmed): with v0.4's loads, a v0.3-style joint's printed plate sees 31–71 MPa every step, above PETG's fatigue strength at every leg joint, and the servo's output shaft carries up to 3.8 N·m of bending. Every leg pitch and roll joint is now a U-bracket on the servo's horn and rear hub, the servo body screwed into a cage, like the reference robot.
- **The first U-brackets had weak joints between the arms and the next servo's cage** (voxel FEA): the shin's arms met the ankle cage through two 18 × 3 mm tabs, the ankle bracket through 2.5 mm bands, the hip-yaw disc through a thin plate. Solid plates now join each arm to its cage over the whole overlap; cage rear plates went from 2.4 to 4 mm (screw heads counterbored), arms from 3.5 to 4.5 mm; the hip-yaw bracket got a 7 mm disc, a keel and a solid block; the hip-roll bracket a 10 × 16 mm bridge.
- **The final masses (2.85 kg) raised the loads by about a tenth**, and two spots fell below a safety factor of 2: the shin's back plate beside the ankle servo's hub hole (strength 1.9: a screw counterbore 0.1 mm from the hole, no side wall at that corner) and the ankle bracket's inboard arm where it meets the roll cage (fatigue 1.8). The shin's plate is now 4 mm everywhere the ankle bracket's boss does not slide, with a 20 mm hub hole and that one screw left out; the ankle bracket's inboard arm reaches 4.5 mm lower (the foot's bracket only comes within 12 mm below the axis there): shin 2.5 / 3.2, ankle bracket 2.4 / 3.0.
- **The hip-yaw servo's shaft still carried the leg's bending** (the builder asked for the retainer lip): a thrust ring alone left it 1.2 N·m in normal walking and 2.6 N·m in the hardest pushes. Now the pelvis holds the yaw disc from both sides: a printed keeper (one per leg, 4 M2 screws into a new boss on the pelvis) puts a lip under the disc's 3 mm flange on the arc where the load needs it. The first keeper failed its own check (fatigue SF 0.5: a 2.2 mm lip, then notches at its ends), so it became a solid C-section clamped to the boss; the pelvis's yaw cages got 5 mm front and back walls to carry its pull (SF 1.3 → 2.5). The hip-yaw range is now ±12° (the gaits use ±5°): over ±30° the hip-roll bracket would reach the keeper, and the legs touched each other beyond 18°.
- **Assembly**: plates that cover a cage would have locked the servo out. The knee cage is open at the front and the ankle cage at the bottom (the servos slide in there), with screwdriver holes through the arms for the far case screws.
- **Shorter legs swayed 26° sideways and pushed the ankle-roll servo against its stop** (100 % of stall): the gaits now keep the zero-moment point 20 mm inside each foot (planner option `zmp_offset_y`, chosen by Monte Carlo over 0–20 mm and 0.45–0.6 s steps): 15° at most, 50 % peak load.
- **Knee speed**: with 62/58 mm leg links the knee swings faster; 0.5 s steps reach the servo's no-load speed. The gaits keep 0.6 s steps (sizing: 68% of the torque-speed line at 0.55 s).
- **Collision ranges re-measured** for every joint; limits set inside them (left leg: hip roll −20…22°, hip pitch −70…8°, knee 0…84°, ankle roll ±20°; every range the gaits use is inside).

### v0.3 (2026-10-04)

- Shoulder servos inside the chest cap; a hip gusset into the hip-pitch servo; the foot grazing the ankle-pitch servo; ankle brackets touching in side-steps; limits allowing collisions — all fixed then. Walking robustness: 100 Hz control, a lower stance, 2- and 4-step blocks. An over-claimed push result (one lucky timing) and a wrong battery estimate were corrected.

## Honest limits

- **Pushes**: 0.24 N.s stays up 100 %, 0.48 N.s stays up 100 %, 0.72 N.s stays up 100 %, 0.96 N.s stays up 100 %, 1.20 N.s stays up 90 %, 1.44 N.s stays up 44 % of 48 timed pushes mid-walk. Harder shoves need a step to a new place; the gait player does not re-plan its steps (a capture-point stepper is in `jx0bot/stepper.py`, not yet enabled).
- **The hip-yaw keeper only works without play**: the analysis assumes the ring and the keeper's lip touch the yaw disc (PTFE tape on the flange, added until the leg turns freely with no wobble). With the keeper, the yaw servo's shaft is left about 0.10 N·m in normal walking and 0.55 N·m in the hardest pushes (ring alone: 1.2 / 2.6); if the play is left in, the shaft takes the bending until it closes. Feetech publishes no bending rating for the STS3215. The yaw range is ±12°.
- **Material and servo data are assumed**: PETG strengths (50 / 15 MPa), the STS3215's rear hub screw pattern (assumed equal to the horn's), and the servo stiffness (60 N·m/rad, 0.6–1.4x tested). Print a test U-bracket and fit-check a servo before printing the rest; measure the servo stiffness (bringup.md step 5).
- **Speed**: about 5 cm/s. The short legs make the knee the speed limit of the STS3215 at 12 V.
- **Latency**: the robot needs its control loop to react within about 20 ms (estimate on the Pi: about 8 ms). At 40 ms, long walks often fail; 2- and 4-step blocks mostly survive.
- **Not tested here**: falls (the model has no body collisions, so a fall's impact on the brackets is not simulated), carpet or very slippery floors (friction below 0.5), stairs, the I2S audio overlay on the Pi, screw fit in the printed holes, long-term servo heating.

## Re-run

```bash
python jx0/verify/run_all.py
```

Detailed results in this folder: `walking.json`, `verify_cad.json`, `verify_robustness.json`, `verify_strength.json`, `verify_fea.json`, `verify_power.json`, `sizing.json`.
