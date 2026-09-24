# JX0 bring-up: from a box of servos to the first steps

Go slowly: the leg servos are strong enough to break printed parts or pinch fingers. Keep the robot on a stand (legs
hanging free) until step 6, and keep a hand on the power switch.

All commands run on the Pi from `jx0/software` (see [software_setup.md](software_setup.md)):

```bash
cd ~/thenar-jx1/jx0/software && source ~/jx0env/bin/activate
```

## 1. Give every leg servo its ID (before assembly)

New ST3215s all ship as ID 1. Connect **one servo at a time** to the driver:

```bash
python -m jx0bot.calibrate scan          # should list one servo at id 1, with 11-12.6 V
python -m jx0bot.calibrate set-id 1 5    # e.g. this one becomes the left ankle pitch
```

Write the ID on the servo with a marker. The ID table is in [wiring.md](wiring.md).

## 2. Centre everything, then fit horns and links

With all 12 servos chained and the MG90S plugged in:

```bash
python -m jx0bot.calibrate center
```

Every leg servo goes to mid-travel (2048 ticks) and every MG90S to 1500 µs (0°). While they hold, fit the horns and
printed links so each joint is as close to its zero pose as the horn splines allow: legs straight, feet flat, arms
hanging, head facing forward, **each gripper finger just touching its palm**. Then press Enter to release.

## 3. Record the exact zero pose

```bash
python -m jx0bot.calibrate zero
```

Torque goes off. Hold the legs in the zero pose (a small set square against the pelvis, thigh and shin plates helps)
and press Enter. The encoder readings are written into `config.yaml` as `zero_ticks`.

## 4. Check every joint's direction

```bash
python -m jx0bot.calibrate directions
```

Each joint moves +10° and back, and the tool asks whether it moved the way the simulation expects (for example "the knee
BENDS"). Answer y/n; the `direction` values in config.yaml are updated. **Do not skip this**: one reversed joint makes
the balance loop push the wrong way.

For the small servos, run `python -m jx0bot.main --sim --text` on a PC first to see what "wave" and "take" should look
like, then fix any reversed MG90S by setting its `direction: -1` in config.yaml.

## 5. Check the stiffness

The walking was verified with servos that give way about 0.5° under a 0.5 N·m load (60 N·m/rad):

```bash
python -m jx0bot.calibrate stiffness l_knee
```

Hang 0.5 kg from a string 10 cm from the knee axis (0.49 N·m), press Enter, and read the stiffness. Much softer than 60
means the position gain is low: raise the servo's P coefficient with Feetech's FD debugging software (Windows) or the
Waveshare servo tool, then measure again. This mapping from servo gains to stiffness is **UNVERIFIED**: it is the first
thing to measure on real hardware.

## 6. First stand, first steps

1. On the stand: `python -m jx0bot.main --text`. The robot moves smoothly into its walking stance (knees bent). Type
   "wave" and "open your right hand" to test the arms.
2. Hold the robot on the floor by a strap on the torso (like a baby-walker, the strap slack) and power up again.
3. Type "walk forward two steps". The gait blocks are the ones that passed the simulation check; the IMU balance loop
   runs on the stance leg.
4. If it tips, the program stops the gait by itself past 25° of tilt. Check the direction table and the IMU mounting
   (`imu.mount`) before trying again.

## Face check

With the display connected:

```bash
python -m jx0bot.face --test
```

You should see red, green, blue and white bars (left to right) on black, a white arrow pointing up and an orange ring.
If red and blue are swapped, set `face.bgr: false`. If the colours look like a photo negative, set
`face.invert: false`. If the arrow points sideways, set `face.rotate` (1, 2 or 3 quarter turns). These are config.yaml
settings, so no code changes are needed.
