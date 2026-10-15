# JX0 verification report

Generated 2026-10-15 by `jx0/verify/run_all.py` from the CAD geometry, the MuJoCo model and the robot software in this repository (design v0.4: double-sided legs like the reference robot, every part fitted to the real STS3215). Everything here is simulation and analysis: the physical robot is not built yet, so the numbers say the design should work, not that it has been seen working.

## Summary

| Check | Result |
|---|---|
| Servo sizing (every leg joint, 5 gaits + 8 static cases, 1.25–1.5x margins) | **ALL PASS** |
| The 14 robot gaits, closed loop on the servo model (100 Hz) | **14/14 pass**, peak servo load 55% of stall |
| The real STS3215 (Feetech factory model and SO-ARM100 model) and its cables at all 17 joints, against every printed part | 0 clashes |
| Every screw (182): plate under the head, thread in the horn / case / insert, tip clear, on a real hole, head room | 0 problems |
| Assembly in the build guide's order: 42 slide-in steps, a screwdriver on all 182 screws | 0 slides blocked, 0 screws unreachable (11 need a PH bit by hand) |
| Parts, servos, cables and screw heads colliding, standing (all 3321 pairs) | 0 clashes |
| Parts colliding in motion (1373 poses: every gait frame + every action) | 0 clashes |
| Joint limits inside the collision-free range | 17/17 joints |
| Leg joints: single-sided (v0.3) vs double-sided (v0.4), beam model, fatigue safety factor | v0.3 0.23–0.49 (**would break**) → v0.4 **5.0–8.4** |
| Printed leg brackets, voxel FEA under the simulated loads, worst bracket | fatigue SF **2.1**, strength SF **2.9** |
| Walking with realistic model errors (latency 0–20 ms), all gaits | **139/140 (99 %)** |
| Same, stress test with 40 ms latency | 125/140 (89 %) |
| Sideways push of 0.24 N.s mid-walk (24 moments × 2 directions): stayed up | 48/48 (100 %) |
| Sideways push of 0.48 N.s mid-walk (24 moments × 2 directions): stayed up | 48/48 (100 %) |
| Sideways push of 0.72 N.s mid-walk (24 moments × 2 directions): stayed up | 48/48 (100 %) |
| Sideways push of 0.96 N.s mid-walk (24 moments × 2 directions): stayed up | 48/48 (100 %) |
| Sideways push of 1.20 N.s mid-walk (24 moments × 2 directions): stayed up | 43/48 (90 %) |
| Sideways push of 1.44 N.s mid-walk (24 moments × 2 directions): stayed up | 21/48 (44 %) |
| Whole robot program, 8-step mission, random realistic errors | **24/24 (100 %)** |
| Battery current walking (servos + Pi) | 1.45 A average, 2.52 A peak → about 73 min walking per charge |
| 100 Hz control loop on a Raspberry Pi 4 (estimated) | 1.79 ms of 10 ms |
| Software unit tests | Ran 21 tests in 5.877s: OK |

## Leg joints: why double-sided

Every leg joint's load from the simulation (14 gaits, 42 walks with model errors, 48 pushes of 0.96 N·s), and what it does to a single-sided joint (v0.3: one plate on the servo's horn) and to a U-bracket on both faces (v0.4). The servo only *drives* the torque about its axis; the bending moment about the other two axes is what the structure carries. On a single-sided joint it all goes through one printed plate and the servo's output shaft. In a U-bracket it becomes a pair of forces in the two arms, 44.25 mm apart, and the output shaft sees no bending at all. The hip-yaw disc is held by the pelvis from both sides instead (thrust ring above, keeper below): its stresses are in the finite-element table. PETG ASSUMED: 50 MPa static, 15 MPa fatigue (10^6 cycles, about 700 hours of walking).

| Joint | Torque N·m | Bending at the horn N·m | v0.3 plate MPa (fatigue SF) | v0.4 MPa (fatigue SF) | Servo shaft bending N·m, v0.3 → v0.4 |
|---|---|---|---|---|---|
| hip yaw | 1.10 | 3.06 | 54.4 (0.28) | ring + keeper: 120 / 100 N pushes on the disc rim (FEA below) | 3.06 → 2.66 (ring only) → 0.49 |
| hip roll | 2.79 | 2.33 | 30.6 (0.49) | 1.8 (8.4) | 2.33 → 0.0 |
| hip pitch | 1.84 | 3.80 | 40.4 (0.37) | 2.9 (5.1) | 3.8 → 0.0 |
| knee | 2.50 | 3.35 | 34.4 (0.44) | 3.0 (5.0) | 3.35 → 0.0 |
| ankle pitch | 2.40 | 3.12 | 50.7 (0.3) | 2.5 (5.9) | 3.12 → 0.0 |
| ankle roll | 1.84 | 3.56 | 66.1 (0.23) | 2.3 (6.4) | 3.56 → 0.0 |

## Printed leg brackets: finite elements

Voxel FEA (`calculations/structural/voxel_fea.py`, 0.7 mm hexahedra with bending modes). Each bracket is held where it bolts to the servo above it (drive horn and passive horn) and loaded where the next servo is screwed into its cage, with that joint's actual 6-axis load every 10 ms of the simulation (all components at the same instant). Stress = 99.9th percentile of each element's worst von Mises, away from the bolted faces.

| Bracket | Elements | Walking MPa (fatigue SF) | Worst with pushes MPa (strength SF) |
|---|---|---|---|
| pelvis | 213,378 | 6.4 (2.3) | 10.88 (4.6) |
| yaw keeper | 8,142 | 6.78 (2.2) | 10.4 (4.8) |
| hip yaw bracket | 150,640 | 7.11 (2.1) | 17.24 (2.9) |
| hip roll bracket | 90,818 | 4.12 (3.6) | 9.96 (5.0) |
| thigh | 117,401 | 5.31 (2.8) | 13.09 (3.8) |
| shin | 70,022 | 5.49 (2.7) | 16.03 (3.1) |
| ankle bracket | 108,986 | 6.94 (2.2) | 16.65 (3.0) |
| foot | 143,464 | 3.19 (4.7) | 7.83 (6.4) |

Stress maps: `images/fea_*.png`.

## What the verification found and fixed

### v0.4 fitted to the real servo (2026-10-15)

- **The CAD's servo was a box; the real STS3215 is not.** Measured on Feetech's factory model and the SO-ARM100 model, its rear face has a 2.2 mm raised label block, the passive horn on a Ø6 boss whose tip stands 0.6 mm proud, and the opening of the two cable sockets, whose wires come straight out of that face. Its output face has a raised strip 1.55 mm high. Every cage collided with it (400–750 mm³ each) and 16 of the 17 left no way out for the cables. Each cage plate now has a window over the label and the sockets that runs out past the case's far end, the cables lie flat in it, and every plate over an output face clears the strip.
- **The screws were wrong.** The horn holes are Ø2.5 for M3 (not M2), and the case holes are Ø1.6 × 2.9 mm deep, so an M2 × 6 through a 2.4 mm plate would have bottomed out. Now, with the screws bought for it: M2 × 6 CSK with 3 mm of plate under the point where the head bears (2.2 mm of thread), M3 × 6 into the drive horn (3 mm), M3 × 8 through a 3.2 mm boss into the passive horn (2.3 mm). Every screw is listed with its part and measured against the real holes (`verify_fit.py`). The torso's M3 × 8 would have hit the ribs under the pelvis plate: the ribs now have holes for their tips.
- **Assembly would have jammed.** The hip-yaw servo could not go into the pelvis: the thrust ring under it blocks the case. Under the case the ring is now a separate insert, pushed up after the servo; the gaits push hardest on exactly that side (up to 90 N), and the insert bears on the servo's case. The brackets could not slide onto their servos: each boss now has a groove for the rear boss's tip, and the drive horn's centre screw goes in last. The servos that slide in lengthwise needed the label window and the strip pocket out to the cage's end, and the shin a slot for the label block. In the old order some screws were out of reach: the lower legs are now built on the bench, the roll horn screws have holes through the pitch cage's front wall, the head slides over a neck hub bolted on first, and 11 screws (the inside of the hips) need a PH bit turned by hand.
- **Horn heights differ by 0.65 mm** between the two models and the datasheet: brackets are built for the deepest horn, with 0.4 mm printed shims for the rest. The hip-yaw keeper's lip now sits 0.45 mm under the disc's flange (PTFE tape takes the play) so no servo can jam it.
- **Strength after the changes** (voxel FEA): the cage windows and the passive-horn screw pockets first left the thigh and shin at fatigue SF 0.6 (their horn-side arms had come loose from the cages by 0.2 mm: every part is now checked to be one solid piece), then the shin at 1.8 and the ankle bracket at 1.5. The shin's back wall now comes down to 10 mm above the ankle axis (the ankle can toe down 5° instead of 15°; the gaits never toe down), and the ankle bracket's arms rise 6 mm above the roll cage: every leg part is back at fatigue SF 2.1 or more.
- **Cables in motion**: the knee cage's back corner was rounded off (the shin's top and its ankle servo's cables swing past it), and the ankle-roll servos' cables leave at the back, because in side steps the other foot passes their inboard end. The hip-yaw and neck servos' cables go straight through the plates they stand on.

### v0.4 (double-sided legs, 2026-10-05)

- **Single-sided joints would break** (the builder's own call, confirmed): with v0.4's loads, a v0.3-style joint's printed plate sees 31–66 MPa every step, above PETG's fatigue strength at every leg joint, and the servo's output shaft carries up to 3.8 N·m of bending. Every leg pitch and roll joint is now a U-bracket on the servo's horn and rear hub, the servo body screwed into a cage, like the reference robot.
- **The first U-brackets had weak joints between the arms and the next servo's cage** (voxel FEA): the shin's arms met the ankle cage through two 18 × 3 mm tabs, the ankle bracket through 2.5 mm bands, the hip-yaw disc through a thin plate. Solid plates now join each arm to its cage over the whole overlap; cage rear plates went from 2.4 to 4 mm (screw heads counterbored), arms from 3.5 to 4.5 mm; the hip-yaw bracket got a 7 mm disc, a keel and a solid block; the hip-roll bracket a 10 × 16 mm bridge.
- **The final masses (2.85 kg) raised the loads by about a tenth**, and two spots fell below a safety factor of 2: the shin's back plate beside the ankle servo's hub hole (strength 1.9: a screw counterbore 0.1 mm from the hole, no side wall at that corner) and the ankle bracket's inboard arm where it meets the roll cage (fatigue 1.8). The shin's plate is now 4 mm everywhere the ankle bracket's boss does not slide, with a 20 mm hub hole and that one screw left out; the ankle bracket's inboard arm reaches 4.5 mm lower (the foot's bracket only comes within 12 mm below the axis there): shin 2.5 / 3.2, ankle bracket 2.4 / 3.0.
- **The hip-yaw servo's shaft still carried the leg's bending** (the builder asked for the retainer lip): a thrust ring alone left it 1.2 N·m in normal walking and 2.7 N·m in the hardest pushes. Now the pelvis holds the yaw disc from both sides: a printed keeper (one per leg, 4 M2 screws into a new boss on the pelvis) puts a lip under the disc's 3 mm flange on the arc where the load needs it. The first keeper failed its own check (fatigue SF 0.5: a 2.2 mm lip, then notches at its ends), so it became a solid C-section clamped to the boss; the pelvis's yaw cages got 5 mm front and back walls to carry its pull (SF 1.3 → 2.5). The hip-yaw range is now ±12° (the gaits use ±5°): over ±30° the hip-roll bracket would reach the keeper, and the legs touched each other beyond 18°.
- **Assembly**: plates that cover a cage would have locked the servo out. The knee cage is open at the front and the ankle cage at the bottom (the servos slide in there), with screwdriver holes through the arms for the far case screws.
- **Shorter legs swayed 26° sideways and pushed the ankle-roll servo against its stop** (100 % of stall): the gaits now keep the zero-moment point 20 mm inside each foot (planner option `zmp_offset_y`, chosen by Monte Carlo over 0–20 mm and 0.45–0.6 s steps): 15° at most, 50 % peak load.
- **Knee speed**: with 62/58 mm leg links the knee swings faster; 0.5 s steps reach the servo's no-load speed. The gaits keep 0.6 s steps (sizing: 69% of the torque-speed line at 0.55 s).
- **Collision ranges re-measured** for every joint; limits set inside them (left leg: hip roll −20…22°, hip pitch −70…8°, knee 0…84°, ankle roll ±20°; every range the gaits use is inside).

### v0.3 (2026-10-04)

- Shoulder servos inside the chest cap; a hip gusset into the hip-pitch servo; the foot grazing the ankle-pitch servo; ankle brackets touching in side-steps; limits allowing collisions — all fixed then. Walking robustness: 100 Hz control, a lower stance, 2- and 4-step blocks. An over-claimed push result (one lucky timing) and a wrong battery estimate were corrected.

## Honest limits

- **Pushes**: 0.24 N.s stays up 100 %, 0.48 N.s stays up 100 %, 0.72 N.s stays up 100 %, 0.96 N.s stays up 100 %, 1.20 N.s stays up 90 %, 1.44 N.s stays up 44 % of 48 timed pushes mid-walk. Harder shoves need a step to a new place; the gait player does not re-plan its steps (a capture-point stepper is in `jx0bot/stepper.py`, not yet enabled).
- **The hip-yaw keeper only works without play**: the analysis assumes the ring and the keeper's lip touch the yaw disc (PTFE tape on the flange, added until the leg turns freely with no wobble). With the keeper, the yaw servo's shaft is left about 0.10 N·m in normal walking and 0.49 N·m in the hardest pushes (ring alone: 1.2 / 2.7); if the play is left in, the shaft takes the bending until it closes. Feetech publishes no bending rating for the STS3215. The yaw range is ±12°.
- **Material and servo data are assumed**: PETG strengths (50 / 15 MPa) and the servo stiffness (60 N·m/rad, 0.6–1.4x tested). The servo's shape comes from two models that differ by up to 0.65 mm (horn height) and 0.3 mm (its rear cover): the fit check uses the larger of them, the shims and PTFE tape take up the rest. The cables are assumed to bend flat within 4 mm of the rear face. Printers make holes and pockets a little small: print the shin first and fit a servo to it (build guide); measure the servo stiffness (bringup.md step 5).
- **Speed**: about 5 cm/s. The short legs make the knee the speed limit of the STS3215 at 12 V.
- **Latency**: the robot needs its control loop to react within about 20 ms (estimate on the Pi: about 8 ms). At 40 ms, long walks often fail; 2- and 4-step blocks mostly survive.
- **Not tested here**: falls (the model has no body collisions, so a fall's impact on the brackets is not simulated), carpet or very slippery floors (friction below 0.5), stairs, the I2S audio overlay on the Pi, long-term servo heating.

## Re-run

```bash
python jx0/verify/run_all.py
```

Detailed results in this folder: `walking.json`, `verify_fit.json`, `verify_cad.json`, `verify_robustness.json`, `verify_strength.json`, `verify_fea.json`, `verify_power.json`, `sizing.json`.
