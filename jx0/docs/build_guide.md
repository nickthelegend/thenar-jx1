# JX0 build guide

JX0 is 20 printed parts, 17 Feetech STS3215 servos (every joint, like the reference robot), a Raspberry Pi and a
handful of small modules. Everything is in the [parts list](../bom/jx0_bom.csv): ₹58,548 from Indian online stores,
with prices checked 2026-10-04. Budget two weekends for printing and one for assembly and bring-up.

Order of work: **buy → print → servo IDs → assemble → wire → bring-up → software**.

## 1. Print

STL files: `jx0/cad/stl/` (millimetres). The parametric SolidWorks parts are in `jx0/cad/parts/`. All the geometry is
generated from `jx0/cad/geometry.py`, so a change there rebuilds every part. To see a change before rebuilding it in
SolidWorks, run `python jx0/cad/preview.py`.

**Filament:** the reference robot's pastel green is closest to eSun PLA-Matte Mint Green. PLA prints easily and looks
right, but it softens around 55–60 °C. If your leg servos run hot (long walks, holding a crouch), print the leg brackets
in PETG instead.

**Settings (0.4 mm nozzle):** 0.2 mm layers, 3 walls, 25 % gyroid infill, and a brim on the tall thin parts (thighs,
shins, blades). For PLA, use 205–215 °C nozzle and a 60 °C bed; for PETG, 235–245 °C nozzle and a 75–85 °C bed.

Print one leg's brackets first and check how a servo fits. The servo screw holes are sized for M2 self-tapping screws,
and that size is ASSUMED: it is not published for the STS3215.

| Part | Qty | Printed mass | Size (mm) | Print tip |
|---|---|---|---|---|
| JX0_Pelvis | 1 | 21.2 g | 51 × 124 × 18 | plate face down |
| JX0_HipYawBracket_L / _R | 1 + 1 | 9.0 g each | 65 × 54 × 45 | horn plate down |
| JX0_HipRollBracket_L / _R | 1 + 1 | 4.7 g each | 53 × 36 × 30 | horn plate down |
| JX0_Thigh_L / _R | 1 + 1 | 11.2 g each | 30 × 9 × 130 | lying flat |
| JX0_Shin_L / _R | 1 + 1 | 10.9 g each | 30 × 9 × 130 | lying flat |
| JX0_AnkleBracket_L / _R | 1 + 1 | 7.2 g each | 72 × 57 × 30 | horn plate down |
| JX0_Foot | 2 | 35.7 g each | 120 × 70 × 47 | sole down |
| JX0_Torso (lower shell) | 1 | 83.0 g | 84 × 120 × 104 | floor down; the standoffs and the lip print upright |
| JX0_ChestCap | 1 | 52.1 g | 84 × 120 × 42 | upside down (top face on the bed); the chamfers are 45° |
| JX0_Head | 1 | 66.8 g | 66 × 78 × 62 | upright on its floor, tree supports inside the rounded top |
| JX0_UpperArm_L / _R (shoulder cradles) | 1 + 1 | 8.1 g each | 32 × 20 × 84 | plate down |
| JX0_ArmBlade_L / _R | 1 + 1 | 11.2 g each | 34 × 5 × 116 | lying flat |
| **Total** | **20** | **419 g** | | one 1 kg spool; the second is for fit-checks and reprints |

## 2. Before assembly: servo IDs and centring

Every STS3215 ships as ID 1. Set the IDs one servo at a time and write each on its case. The table is in
[wiring.md](wiring.md): legs 1–12, arms 13–16, neck 17. Then chain the servos, run
`python -m jx0bot.calibrate center`, and fit every horn and link while the servos hold mid-travel.
[bringup.md](bringup.md) has the commands.

## 3. Assemble

The design rule is the same at every joint: **the servo's case is screwed to one link through its rear face, and the
next link bolts to its output horn** (4 screws in a cross on a 14 mm circle, like the reference robot). The three hip
axes meet at the hip centre and the two ankle axes at the ankle centre, as the walking model assumes.

Legs, top down:

1. **Pelvis.** Screw the two hip-yaw servos to the pelvis plate by their rear faces, horns pointing down.
2. **Hip-yaw bracket** onto each yaw horn. It carries the **hip-roll servo** behind the hip centre, horn forward.
3. **Hip-roll bracket** onto the roll horn. It carries the **hip-pitch servo**, horn pointing outward.
4. **Thigh** onto the hip-pitch horn (outside). The **knee servo** goes on the thigh's inner face at the bottom, case
   up, horn inward.
5. **Shin** onto the knee horn. The **ankle-pitch servo** goes on its outer face at the bottom, case up, horn outward.
6. **Ankle bracket** onto the ankle-pitch horn. It carries the **ankle-roll servo** behind the ankle, horn forward.
7. **Foot** onto the ankle-roll horn. Glue the 1 mm rubber sheet under the sole (contact cement) and trim it flush.

Body, arms and head:

8. **Lower torso** onto the pelvis: 4 × M3 × 8 into heat-set inserts pressed into the pelvis (soldering iron at about
   220 °C). Fit the Raspberry Pi on the back-wall standoffs, the battery on the floor, the servo driver and the UBEC
   beside it, and the push-to-talk button in the back wall.
9. **Chest cap**: screw both **shoulder servos** to the inner plates by their rear faces, so the horns come out through
   the side-wall holes. Screw the **neck servo** onto the top by its rear face, horn up. Fit the speaker under the round
   grille. Slide the cap over the torso lip and fix it with 4 screws through the cap wall, front and back.
10. **Arms**, each side:
    - Screw the **elbow servo** into the shoulder cradle first: rear face on the cradle plate, horn outward, case up.
    - Bolt the **cradle** onto the shoulder horn (the 4 cross-pattern screws are reachable from outside).
    - Bolt the **blade** onto the elbow horn, hanging straight down.
11. **Head** onto the neck horn (centre screw + 4 horn screws). Glue the microphone behind the four face holes and take
    its cable down through the hole in the head floor, with slack for ±80° of head turn.

Look at `jx0/cad/JX0_Robot.SLDASM` in SolidWorks, or the pictures in [../README.md](../README.md), whenever a
part's orientation is unclear.

## 4. Wire, bring up, install the software

- [wiring.md](wiring.md): power, the servo bus chains and IDs, the GPIO map.
- [bringup.md](bringup.md): IDs, centring, zero pose, directions, stiffness, first stand and first steps.
- [software_setup.md](software_setup.md): Raspberry Pi OS, audio, voice models, the Claude API key, start on boot.

## Fasteners and small parts

| Item | Where | Notes |
|---|---|---|
| M2 × 6 socket screws (140) | servo horns and servo cases, 8 per servo | size ASSUMED: fit-check on the first bracket |
| M3 × 8 socket screws (8) + M3 heat-set inserts | torso to pelvis, chest cap to torso | |
| 1 mm rubber sheet | foot soles | any thin anti-slip mat works |
| Hot glue, zip ties, double-sided foam tape | microphone, battery, wiring | |
