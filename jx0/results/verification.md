# JX0 verification report

Generated 2026-10-04 by `jx0/verify/run_all.py` from the CAD geometry, the MuJoCo model and the robot software in this repository. Everything here is simulation and analysis: the physical robot is not built yet, so the numbers say the design should work, not that it has been seen working.

## Summary

| Check | Result |
|---|---|
| Servo sizing (every leg joint, 5 gaits + static cases) | **ALL PASS** |
| The 14 robot gaits, closed loop on the servo model (100 Hz) | **14/14 pass** |
| Parts and servos colliding, standing (all 666 pairs) | 0 clashes |
| Parts colliding in motion (1373 poses: every gait frame + every action) | 0 clashes |
| Joint limits inside the collision-free range | 17/17 joints |
| Walking with realistic model errors (latency 0–20 ms), all gaits | **136/140 (97 %)** |
| Same, stress test with 40 ms latency | 120/140 (86 %) |
| Sideways push of 0.24 N.s mid-walk (24 moments × 2 directions) | 48/48 (100 %) |
| Sideways push of 0.48 N.s mid-walk (24 moments × 2 directions) | 30/48 (62 %) |
| Sideways push of 0.72 N.s mid-walk (24 moments × 2 directions) | 24/48 (50 %) |
| Whole robot program, 8-step mission, random realistic errors | **24/24 (100 %)** |
| Battery current walking (servos + Pi) | 1.51 A average, 2.13 A peak → about 70 min walking per charge |
| 100 Hz control loop on a Raspberry Pi 4 (estimated) | 1.98 ms of 10 ms |
| Software unit tests | Ran 19 tests in 0.137s: OK |

## What the verification found and fixed

The first run of these checks failed in several places. All of these were fixed in the design before the numbers above:

- **Shoulder servos 4 mm inside the chest cap** (696 mm³ overlap): the thickened wall under the cap's top chamfer hit the top of each shoulder servo. The cap is now 5 mm taller (neck and head 5 mm higher).
- **Hip-roll bracket gusset into the hip-pitch servo** (36 mm³, there since v0.1): the gusset now stops 0.4 mm clear.
- **Foot grazing the ankle-pitch servo while walking** (341 of 699 poses): the servo case corner is 16.0 mm from the ankle axis but the foot upright was 15 mm away. The ankle-roll horn face moved 2 mm back (XA −18 → −20).
- **Ankle roll hitting the ankle bracket above ~14°**: the foot upright and heel block are now 24 mm wide instead of 30.
- **Left and right ankle brackets touching in side-steps** (86 mm³): the brackets' inboard plates end 2.5 mm sooner.
- **A sole lightening hole cut under the moved upright** (found by the SolidWorks rebuild): the holes were respaced.
- **Joint limits allowing collisions**: knee 130 → 120°, ankle pitch −60…45 → −55…15°, ankle roll ±25 → ±20°.
- **Walking fell too often with realistic errors** (long walk 4/12, pushes ~50 %): command latency was the main cause. Control now runs at 100 Hz instead of 50 Hz, the walking stance is a little lower (hip 222 → 215 mm), and walks are chained from 2- and 4-step blocks that each end standing. Long walks with realistic errors went from 4/12 to 18/20, the robot program's missions pass 24/24, and peak servo load dropped from 78 % to 56 % of stall.
- **An over-claimed push result**: one lucky push timing had passed at 1.1 N·s. Pushes are now tested at 24 moments in both directions, and the README states the real envelope.
- **A wrong battery estimate**: servo current is now modelled as copper loss + mechanical power. It predicts 0.45 A standing and 1.06 A walking for the servos; the reference robot's bench supply read 0.58 A and 0.6–1.5 A.

## Honest limits

- **Pushes**: a light tap (0.24 N·s, about 2 N for a moment) never knocks it over. A firmer shove (0.48 N·s) knocks it over about a third of the time, depending on when in the step it lands. A shove that hard moves the point it would have to step to about 3.5 cm sideways, half the foot's width, and the controller does not re-plan its steps yet. A stepping reflex was tried and did not help in this form; online step re-planning is the next controller upgrade.
- **Latency**: the robot needs its control loop to react within about 20 ms. The estimate for the Pi is about 8 ms (IMU filter 5 ms, bus 1.3 ms, compute < 1 ms). At 40 ms, long walks fail more than half the time.
- **The servo model is assumed**: stiffness 60 N·m/rad and damping 0.6 N·m·s/rad, with 0.6–1.4× of each tested. Measuring the real STS3215 stiffness (bringup.md step 5) is the first thing to check on hardware.
- **Not tested here**: carpet or very slippery floors (friction below 0.5), stairs or steps, the I2S audio overlay on the Pi, screw fit in the printed holes, long-term servo heating.

## Re-run

```bash
python jx0/verify/run_all.py
```

Detailed results: `walking.json`, `verify_cad.json`, `verify_robustness.json`, `verify_power.json`, `sizing.json` in this folder.
