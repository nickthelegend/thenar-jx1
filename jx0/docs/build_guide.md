# JX0 build guide

JX0 is 20 printed parts, 17 Feetech STS3215 servos (every joint, like the reference robot), a Raspberry Pi and a
handful of small modules. Everything is in the [parts list](../bom/jx0_bom.csv): ₹58,234 from Indian online stores,
with prices checked 2026-10-04. Budget two weekends for printing and one for assembly and bring-up.

Order of work: **buy → print → servo IDs → assemble → wire → bring-up → software**.

## How the legs are built (v0.4)

Every leg pitch and roll joint is **double-sided**, like the reference robot. The STS3215 is a dual-shaft servo
(Evelta sells it as "ST3215-C018 … Dual Shaft"): the output horn on one face and a passive hub on the other.

- The servo's **body sits in a cage** on one part (four walls and a plate the case is screwed to).
- The **next part is a U-bracket** that bolts to both faces: 4 screws into the horn, and 4 screws through a raised
  boss into the rear hub.

So the joint's load goes through both ends of the servo instead of bending its output shaft. With the simulated
walking loads, a one-plate joint (v0.3) would stress its plate past PETG's fatigue strength at every leg joint; the
U-brackets keep every printed leg part at a fatigue safety factor of 2.3 or more (finite elements:
[verification](../results/verification.md)). The hip-yaw joint is the one that stays single-sided: a thrust ring
under the pelvis carries the leg's weight there.

## 1. Print

STL files: `jx0/cad/stl/` (millimetres). The parametric SolidWorks parts are in `jx0/cad/parts/`. All the geometry is
generated from `jx0/cad/geometry.py`, so a change there rebuilds every part. To see a change before rebuilding it in
SolidWorks, run `python jx0/cad/preview.py`.

**Leg parts and pelvis: PETG, near-solid.** These carry every step:
- 0.2 mm layers, **6 walls, 6 top and 6 bottom layers, 40 % gyroid**, so their 2.4–4.5 mm plates print solid, as
  the strength check assumes;
- 235–245 °C nozzle, 75–85 °C bed;
- print each U-bracket lying on one of its arms, with tree supports under the other arm.

**Body, head and arms: PLA.** The reference robot's pastel green is closest to eSun PLA-Matte Mint Green. Use
0.2 mm layers, 3 walls, 25 % gyroid, 205–215 °C nozzle and a 60 °C bed.

**Print one U-bracket first** (a shin is the smallest) and fit a servo:
- the horn and hub must sit flat on the bracket's arms;
- the boss must slide over the cage's plate.

The screw holes are sized for M2 self-tapping screws, and the hub's 4-hole pattern is ASSUMED equal to the horn's.
Neither is published for the STS3215.

| Part | Qty | Printed mass | Size (mm) | Material, print tip |
|---|---|---|---|---|
| JX0_Pelvis (two hip-yaw cages, thrust rings) | 1 | 55.0 g | 52 × 128 × 38 | PETG near-solid; top plate down |
| JX0_HipYawBracket_L / _R | 1 + 1 | 51.0 g each | 70 × 58 × 46 | PETG near-solid; disc face down |
| JX0_HipRollBracket_L / _R | 1 + 1 | 29.0 g each | 96 × 54 × 31 | PETG near-solid; rear arm down |
| JX0_Thigh_L / _R | 1 + 1 | 44.3 g each | 52 × 48 × 92 | PETG near-solid; outer arm down |
| JX0_Shin_L / _R | 1 + 1 | 25.2 g each | 31 × 48 × 84 | PETG near-solid; outer arm down |
| JX0_AnkleBracket_L / _R | 1 + 1 | 35.9 g each | 72 × 61 × 33 | PETG near-solid; outer arm down |
| JX0_Foot | 2 | 51.1 g each | 124 × 70 × 46 | PETG near-solid; sole down |
| JX0_Torso (lower shell with the skirt) | 1 | 105.9 g | 84 × 120 × 140 | PLA; floor down |
| JX0_ChestCap | 1 | 46.4 g | 84 × 126 × 42 | PLA; upside down (top face on the bed), chamfers 45° |
| JX0_Head | 1 | 66.8 g | 66 × 78 × 62 | PLA; upright on its floor, tree supports inside the rounded top |
| JX0_UpperArm_L / _R (shoulder hood + elbow box) | 1 + 1 | 22.7 g each | 53 × 35 × 84 | PLA; outer plate down |
| JX0_ArmBlade_L / _R | 1 + 1 | 15.3 g each | 36 × 8 × 116 | PLA; lying flat |
| **Total** | **20** | **823 g** | | 528 g PETG + 295 g PLA |

## 2. Before assembly: servo IDs and centring

Every STS3215 ships as ID 1. Set the IDs one servo at a time and write each on its case. The table is in
[wiring.md](wiring.md): legs 1–12, arms 13–16, neck 17. Then chain the servos, run
`python -m jx0bot.calibrate center`, and fit every horn and bracket while the servos hold mid-travel.
[bringup.md](bringup.md) has the commands.

## 3. Assemble

Two rules at every leg joint:
- **The servo goes into its cage from the open side** (with its horn off where a plate covers that side), and its
  case screws go in through the cage's plate. The holes in a bracket's arm let a screwdriver reach the far ones.
- **The U-bracket slides onto the servo from below**, its boss gliding over the cage's plate onto the rear hub. The
  near case screw on that side is left out on purpose, so the boss can pass; three screws and the cage walls hold the
  case. Then 4 screws go into the horn and 4 through the boss into the hub.

All three hip axes meet at the hip centre and both ankle axes at the ankle centre, as the walking model assumes.

Legs, top down (left shown; the right is the mirror image):

1. **Pelvis.** Slide each hip-yaw servo into its pelvis cage from below, horn end down, and screw it through the top
   plate (4 × M2 × 6, heads sunk). Fit the yaw horn.
2. **Hip-yaw bracket.** Slide the hip-roll servo into the bracket's cage from the front, horn off, and screw it through
   the back plate. Put one layer of PTFE tape on the top of the disc. Bolt the disc to the yaw horn from below
   (4 × M2 × 10 through the sunk holes). The disc now rides 0.3 mm under the pelvis's thrust ring.
3. **Hip-roll bracket.** First fit it to the hip-roll servo, horn on:
   - slide it on from below, rear boss over the cage's back plate;
   - put the 4 horn screws in from inside its empty pitch cage (heads sunk), then 4 × M2 × 10 into the hub.

   Then slide the hip-pitch servo into the pitch cage from the outer side and screw it through the inner plate.
4. **Thigh.**
   - Slide the knee servo into the thigh's knee cage from the front (horn off). Put in its near case screw through the
     inner plate, and the two far ones through the holes in the inner arm. Fit the knee horn.
   - Slide the thigh onto the hip-pitch servo from below: 4 × M2 × 8 into the horn, 4 × M2 × 10 into the hub.
5. **Shin.**
   - Slide the ankle-pitch servo up into the shin's cage from below. The front near screw goes in sunk (the rear
     one is left out on purpose: that corner has no side wall, and a hole there would weaken the plate beside the
     hub); the far ones go through the holes in the inner arm.
   - Slide the shin onto the knee servo from below.
6. **Ankle bracket.**
   - Slide the ankle-roll servo into its cage from the inboard end (horn off) and screw it through the back plate.
   - Fit the roll horn through the rim's hole.
   - Slide the bracket onto the ankle-pitch servo from below.
7. **Foot** onto the ankle-roll servo from below, heel arm over the cage's back plate. Glue the 1 mm rubber sheet
   under the sole (contact cement) and trim it flush.

Body, arms and head:

8. **Lower torso** onto the pelvis: 4 × M3 × 8 into heat-set inserts pressed into the pelvis (soldering iron at about
   220 °C). Its skirt comes down around the two hip-yaw servos. Inside:
   - the Raspberry Pi on the back-wall standoffs;
   - the battery on the floor, with the servo driver and the UBEC beside it;
   - the push-to-talk button in the back wall.

   The leg cables come up through the slot in the floor.
9. **Arms**, each side:
   - Shoulder servo into the hood, case down, screwed to the outer plate.
   - Elbow servo into the box below, horn outward, screwed to the inner plate.
   - Blade onto the elbow horn (4 × M2 × 12).
10. **Chest cap**:
    - Screw the **neck servo** onto the top by its rear face, horn up.
    - Fit the speaker under the round grille.
    - Bolt each **shoulder horn** to its pad on the cap's side wall from inside the cap (4 × M2 × 10); the arm now
      hangs from the pad.
    - Slide the cap over the torso lip and fix it with 4 screws through the cap wall, front and back.
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
| M2 × 6 socket screws (66) | servo cases (3 or 4 per servo), hip-roll horns | size ASSUMED: fit-check on the first bracket |
| M2 × 8 (36) | U-bracket horn arms, head | |
| M2 × 10 (56) | U-bracket hub arms through the boss, hip-yaw discs, shoulder pads | |
| M2 × 12 (8) | arm blades | |
| M3 × 8 socket screws (8) + M3 heat-set inserts | torso to pelvis, chest cap to torso | |
| PTFE thread-seal tape | top of each hip-yaw disc (or silicone grease) | |
| 1 mm rubber sheet | foot soles | any thin anti-slip mat works |
| Hot glue, zip ties, double-sided foam tape | microphone, battery, wiring | |
