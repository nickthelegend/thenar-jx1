# JX0 bring-up: from a box of servos to the first steps

Go slowly: the STS3215s are strong enough to break printed parts or pinch fingers. Keep the robot on a stand (legs
hanging free) until step 6, and keep a hand on the power switch. A 12.6 V bench supply with a 3 A current limit is the
gentlest way to power it during bring-up.

All commands run on the Pi from `jx0/software` (see [software_setup.md](software_setup.md)):

```bash
cd ~/thenar-jx1/jx0/software && source ~/jx0env/bin/activate
```

## 1. Give every servo its ID (before assembly)

All 17 STS3215s ship as ID 1. Connect **one servo at a time** to the driver:

```bash
python -m jx0bot.calibrate scan
```

It should list one servo at ID 1, at 11–12.6 V. Then give it its ID, for example the left ankle pitch:

```bash
python -m jx0bot.calibrate set-id 1 5
```

Write the ID on the servo with a marker. The ID table is in [wiring.md](wiring.md): legs 1–12, left shoulder 13,
left elbow 14, right shoulder 15, right elbow 16, neck 17.

## 2. Centre everything, then fit horns and links

With all 17 servos chained:

```bash
python -m jx0bot.calibrate center
```

Every servo goes to mid-travel (2048 ticks). While they hold, fit the horns and printed links so each joint is as close
to its zero pose as the horn splines allow: legs straight, feet flat, shoulder cradles and blades hanging straight down,
head facing forward. Then press Enter to release.

## 3. Record the exact zero pose

```bash
python -m jx0bot.calibrate zero
```

Torque goes off. Hold the robot in the zero pose (a small set square against the pelvis, thigh and shin plates helps)
and press Enter. All 17 encoder readings are written into `config.yaml` as `zero_ticks`.

## 4. Check every joint's direction

```bash
python -m jx0bot.calibrate directions
```

Each joint moves +10° and back. The tool asks whether it moved the way the simulation expects ("the knee BENDS", "the
arm swings BACKWARD", "the head turns to the robot's LEFT"). Answer y/n and the `direction` values in config.yaml are
updated. **Don't skip this**: one reversed leg joint makes the balance loop push the wrong way.

## 5. Check the stiffness

The walking was verified with servos that give way about 0.5° under a 0.5 N·m load (60 N·m/rad):

```bash
python -m jx0bot.calibrate stiffness l_knee
```

Hang 0.5 kg from a string 10 cm from the knee axis (0.49 N·m), press Enter, and read the stiffness. If it is much softer
than 60, the position gain is too low. Raise the servo's P coefficient with Feetech's FD debugging software (Windows) or
the Waveshare servo tool, then measure again. How the servo's gain register maps to stiffness is **UNVERIFIED**: it is
the first thing to measure on real hardware.

## 6. First stand, first steps

1. On the stand, run `python -m jx0bot.main --text`. The robot moves smoothly from wherever its joints are into its
   walking stance (knees bent). Type "wave" to test the arms.
2. Hold the robot on the floor by a strap on the torso, like a baby walker with the strap slack, and power it up again.
3. Type "walk forward two steps". It plays the gait blocks that passed the simulation check, arms swinging, with the IMU
   balance loop on the stance leg.
4. If it tips, the program stops the gait by itself past 25° of tilt. Check the direction table and the IMU mounting
   (`imu.mount`) before trying again.
5. When it walks reliably, try what the reference video shows: a gentle push from the side while it walks. In the
   simulation it shrugs off a 1.1 N·s shove, which is about a firm tap.
