# JX0 build guide

JX0 is 23 PETG prints, 12 bus servos, 9 micro servos, a Raspberry Pi and a handful of modules. Everything is in the
[parts list](../bom/jx0_bom.csv) (₹47,106 with Indian suppliers, checked 2026-09-24). Budget two weekends for
printing and one for assembly and bring-up.

Order of work: **buy → print → servo IDs → assemble → wire → bring-up → software**.

## 1. Print

STL files: `jx0/cad/stl/` (millimetres). The parametric SolidWorks parts are in `jx0/cad/parts/`, and all the geometry
is generated from `jx0/cad/geometry.py`, so a change there rebuilds every part.

**Settings (PETG, 0.4 mm nozzle):** 0.2 mm layers, 3 walls, 25 % gyroid infill, 235–245 °C nozzle, 75–85 °C bed,
fan 30–50 %, a brim on the tall thin parts (thighs, shins, forearms). Print one leg's brackets first and check the servo
fit before printing the rest: the servo screw holes are sized for M2 self-tapping screws, and that screw size is
ASSUMED because it is not published for the ST3215.

| Part | Qty | Printed mass | Size (mm) | Print tip |
|---|---|---|---|---|
| JX0_Pelvis | 1 | 21.2 g | 51 × 124 × 18 | plate face down |
| JX0_HipYawBracket_L / _R | 1 + 1 | 9.0 g each | 65 × 54 × 45 | horn plate down |
| JX0_HipRollBracket_L / _R | 1 + 1 | 4.8 g each | 53 × 36 × 30 | horn plate down |
| JX0_Thigh_L / _R | 1 + 1 | 11.7 g each | 30 × 9 × 129 | lying flat |
| JX0_Shin_L / _R | 1 + 1 | 11.0 g each | 30 × 9 × 125 | lying flat |
| JX0_AnkleBracket_L / _R | 1 + 1 | 7.2 g each | 70 × 60 × 30 | horn plate down |
| JX0_Foot | 2 | 36.3 g each | 120 × 70 × 47 | sole down |
| JX0_Torso | 1 | 97.2 g | 80 × 132 × 127 | front wall down, supports for the servo holders |
| JX0_Head | 1 | 47.7 g | 66 × 90 × 84 | upright on its floor, tree supports inside the rounded top |
| JX0_ShoulderBracket_L / _R | 1 + 1 | 6.6 g each | 30 × 24 × 43 | horn plate down |
| JX0_UpperArm | 2 | 4.7 g each | 18 × 28 × 71 | lying on the horn plate |
| JX0_Forearm_L / _R (the hands) | 1 + 1 | 10.5 g each | 19 × 39 × 96 | lying on the outer plate |
| JX0_Finger_L / _R (gripper claws) | 1 + 1 | 4.8 g each | 8 × 36 × 48 | lying flat |
| **Total** | **23** | **379 g** | | one 1 kg spool; the second is for fit-checks and reprints |

## 2. Before assembly: servo IDs and centring

Every ST3215 ships as ID 1. Set the IDs one servo at a time and write each on its case (table in
[wiring.md](wiring.md)). Then chain them, run `python -m jx0bot.calibrate center`, and fit every horn and link while
the servos hold mid-travel. [bringup.md](bringup.md) has the commands.

## 3. Assemble

The design rule is the same at every joint: **the servo's case is screwed to one link through its rear face, and the
next link bolts to its output horn** (4 screws on a 14 mm circle). The three hip axes meet at the hip centre and the
two ankle axes at the ankle centre, as the walking model assumes. Build each leg from the top down:

1. **Pelvis.** Screw the two hip-yaw servos to the pelvis plate by their rear faces, horns pointing down.
2. **Hip-yaw bracket** onto each yaw horn. It carries the **hip-roll servo** behind the hip centre, horn forward.
3. **Hip-roll bracket** onto the roll horn. It carries the **hip-pitch servo**, horn pointing outward.
4. **Thigh** onto the hip-pitch horn (outside). The **knee servo** goes on the thigh's inner face at the bottom, case
   up, horn inward.
5. **Shin** onto the knee horn. The **ankle-pitch servo** goes on its outer face at the bottom, case up, horn outward.
6. **Ankle bracket** onto the ankle-pitch horn. It carries the **ankle-roll servo** behind the ankle, horn forward.
7. **Foot** onto the ankle-roll horn. Glue the 1 mm rubber sheet under the sole (contact cement), and trim it flush.
8. **Torso** onto the pelvis: 4 × M3 × 8 into heat-set inserts pressed into the pelvis (a soldering iron at about
   220 °C). Inside: the Pi on its standoffs, a shoulder-pitch MG90S in each side-wall holder (horn out through the
   wall), and the neck MG90S in the top holder (horn up).
9. **Arms**, each side:
   - The **shoulder bracket** goes on the shoulder-pitch horn and holds the shoulder-roll MG90S.
   - The **upper arm** hangs from the roll horn and holds the elbow MG90S.
   - The **forearm (hand)** goes on the elbow horn. Slide the gripper MG90S into the hand's sleeve until its tabs sit
     on the sleeve end, and fix it with 2 screws through the tabs.
   - Screw the **finger** onto the gripper horn with the servo at 1500 µs and the claw just touching the palm. It
     opens forward, up to about 45 mm.
10. **Head** onto the neck horn (centre screw + 2 horn screws). Hot-glue the round display's PCB edge behind the face
    window, the camera behind the lens hole above it, and the microphone behind the left ear vents. Loop the cables
    down through the neck with slack for ±80° of head turn.

Look at `jx0/cad/JX0_Robot.SLDASM` (46 components) in SolidWorks, or the pictures in [../README.md](../README.md),
whenever the orientation of a part is unclear.

## 4. Wire, bring up, install the software

- [wiring.md](wiring.md): power tree, servo chains, the GPIO map.
- [bringup.md](bringup.md): IDs, centring, zero pose, directions, stiffness, first stand and first steps, display test.
- [software_setup.md](software_setup.md): Raspberry Pi OS, audio, voice models, the Claude API key, start on boot.

## Fasteners and small parts

| Item | Where | Notes |
|---|---|---|
| M2 × 6 socket screws (100) | servo horns, servo cases, finger | size ASSUMED: fit-check on the first bracket |
| M3 × 8 socket screws (4) + M3 heat-set inserts | torso to pelvis | |
| MG90S screws (in the servo bag) | arm, gripper and neck horns, gripper tabs | |
| 1 mm rubber sheet | foot soles | any thin anti-slip mat works |
| Hot glue, zip ties, double-sided foam tape | display, camera, mic, battery, wiring | |
