# JX0 build guide

JX0 is 25 printed parts (plus 40 thin horn shims), 17 Feetech STS3215 servos (every joint, like the reference robot), a
Raspberry Pi and a handful of small modules. Everything is in the [parts list](../bom/jx0_bom.csv): ₹57,878 from
Indian online stores and a local fastener supplier, with prices checked 2026-10-04. Budget two weekends for printing
and one for assembly and bring-up.

Order of work: **buy → print → servo IDs → assemble → wire → bring-up → software**.

## Fitted to the real servo

Every part is built around the STS3215 as it really is, not a box. The CAD's servo model is the larger of two
measured models: Feetech's own factory model (the STEP Waveshare distributes) and TheRobotStudio's SO-ARM100 model,
which thousands of SO-101 arms are printed against. It includes:

- the 45.4 × 24.8 mm case and the pad on its rear face that the cage presses on;
- the raised label block on that rear face;
- the opening of the two cable sockets;
- the passive horn on its Ø6 rear boss;
- the raised strip on the output face;
- the drive horn, with the head of its centre screw.

`python jx0/verify/verify_fit.py` checks, before anything is printed:

- **The servo in its place:** each of the 17 servos, as both models, against every printed part, including the cables
  leaving each servo.
- **Every screw** (182 of them): the plate under its head, the thread length it gets in the horn, case or insert, that
  it doesn't bottom out, that it lines up with a real hole, and that its head has room.
- **The assembly order below:** every servo sliding into its cage, every bracket sliding onto its servo, and a
  screwdriver reaching every screw at the step where it goes in.

`jx0/verify/verify_cad.py` then checks the same servo shape, its cables and every screw head through all the gaits and
every joint's full range ([verification](../results/verification.md)).

What the CAD cannot know is your servos' exact horn height: the two models and the datasheet differ by up to 0.65 mm.
**Measure it** (step 2) and use the printed 0.4 mm shims.

## How the legs are built (v0.4)

Every leg pitch and roll joint is **double-sided**, like the reference robot. The STS3215 is a dual-shaft servo
(Evelta sells it as "ST3215-C018 … Dual Shaft"): the drive horn on one face and a passive horn, on the Ø6 rear boss,
on the other.

- The servo's **body sits in a cage** on one part: four walls, and a plate the case is screwed to. The plate has a
  window over the label block and the cable sockets. The cables are plugged in first and lie flat along the rear face,
  out through the far end of the cage.
- The **next part is a U-bracket** that bolts to both horns: 4 × M3 × 6 into the drive horn, and 4 × M3 × 8 through
  a 3.2 mm boss into the passive horn. The boss carries the arm over the cage's plate, its screw heads and the cables.

So the joint's load goes through both ends of the servo instead of bending its output shaft. FEA check:
[verification](../results/verification.md).

The **hip yaw** cannot be a U-bracket: its servo stands under the body with the hip-roll servo right below it. Instead
the pelvis holds the yaw disc from both sides:
- a **thrust ring** above it, part of the pelvis. Under the yaw servo's case it is a separate printed **yaw ring
  insert**, because the servo goes into the pelvis from below. The disc's inboard side, where the gaits push hardest,
  bears through the insert onto the servo's case.
- a **keeper** below it, a small printed C-shaped part whose lip runs under the disc's 3 mm flange. Four screws clamp
  it to a boss on the pelvis.

So the leg's bending goes from the disc into the pelvis, and the yaw servo's shaft is left with almost none of it. The
hip yaw turns ±12°, more than twice what the gaits use.

## 1. Print

STL files: `jx0/cad/stl/` (millimetres). The parametric SolidWorks parts are in `jx0/cad/parts/`. All the geometry is
generated from `jx0/cad/geometry.py`, so a change there rebuilds every part. To see a change before rebuilding it in
SolidWorks, run `python jx0/cad/preview.py`.

**Leg parts and pelvis: PETG, near-solid.** These carry every step:
- 0.2 mm layers, **6 walls, 6 top and 6 bottom layers, 40 % gyroid**, so their 2–5 mm plates print solid, as the
  strength check assumes;
- 235–245 °C nozzle, 75–85 °C bed;
- print each U-bracket lying on one of its arms, with tree supports under the other arm.

**Body, head and arms: PLA.** The reference robot's pastel green is closest to eSun PLA-Matte Mint Green. Use
0.2 mm layers, 3 walls, 25 % gyroid, 205–215 °C nozzle and a 60 °C bed.

**Print one shin first** (the smallest U-bracket with a cage), before anything else, and fit a servo to it:
- the servo must slide up into its cage;
- its two far case screws must pull it flat onto the plate;
- the shin must slide onto a second servo's horns and sit flat on both.

If your printer prints holes or pockets small, set its hole compensation now, before printing the rest.

| Part | Qty | Printed mass | Size (mm) | Material, print tip |
|---|---|---|---|---|
| JX0_Pelvis (two hip-yaw cages, thrust rings, keeper bosses) | 1 | 73.0 g | 52 × 139 × 39 | PETG near-solid; top plate down |
| JX0_YawRing_L / _R (thrust ring insert under each yaw servo) | 1 + 1 | 0.7 g each | 26 × 30 × 3 | PETG near-solid; flat |
| JX0_YawKeeper_L / _R | 1 + 1 | 3.4 g each | 39 × 42 × 9 | PETG near-solid; flat top down |
| JX0_HipYawBracket_L / _R | 1 + 1 | 51.2 g each | 74 × 58 × 46 | PETG near-solid; disc face down, supports in the groove |
| JX0_HipRollBracket_L / _R | 1 + 1 | 30.5 g each | 98 × 56 × 31 | PETG near-solid; rear arm down |
| JX0_Thigh_L / _R | 1 + 1 | 54.2 g each | 52 × 49 × 122 | PETG near-solid; outer arm down |
| JX0_Shin_L / _R | 1 + 1 | 31.9 g each | 31 × 49 × 113 | PETG near-solid; outer arm down |
| JX0_AnkleBracket_L / _R | 1 + 1 | 37.8 g each | 74 × 62 × 39 | PETG near-solid; outer arm down |
| JX0_Foot | 2 | 50.7 g each | 124 × 70 × 46 | PETG near-solid; sole down |
| JX0_HornShim (0.4 mm, under a horn arm) | 40 | 0.1 g each | Ø19.6 | PETG; two 0.2 mm layers, flat |
| JX0_Torso (lower shell with the skirt, the camera window and shelves) | 1 | 132.0 g | 84 × 120 × 162 | PLA (white); floor down |
| JX0_ChestCap | 1 | 45.3 g | 84 × 126 × 42 | PLA (white); upside down (top face on the bed), chamfers 45° |
| JX0_Head (two pockets for the WS2812 12-LED ring eyes, wire slots behind them, ear pods) | 1 | 157.4 g | 70 × 124 × 70 | PLA (white); upright on the flat rim of its open bottom, tree supports inside the top |
| JX0_EyeLens (over each LED ring, flush with the face) | 2 | 1.6 g each | Ø50.4 × 1.2 | PETG, **transparent**; flat |
| JX0_CamClamp (holds the chest webcam on its shelves) | 1 | 8.6 g | 4 × 69 × 48 | PLA (white); flat, countersinks up |
| JX0_NeckHub (on the neck horn, the head slides over it) | 1 | 10.7 g | 52 × 48 × 12 | PLA (white); flat plate down |
| JX0_UpperArm_L / _R (shoulder hood + elbow box) | 1 + 1 | 21.7 g each | 54 × 35 × 85 | PLA (white); inner side (the shoulder horn's) down: on the outer plate it would tip |
| JX0_ArmBlade_L / _R | 1 + 1 | 17.3 g each | 36 × 8 × 136 | PLA (white); lying flat |
| **Total** | **28 + 40 shims** | **1035 g** | | 599 g PETG (pelvis and legs, red) + 435 g PLA (body, head, arms, white; the lenses clear PETG) |

## Joint stops

Each joint is stopped three ways, so no two parts ever run into each other (`jx0/results/verify_stops.json`):

1. **Software limits.** The robot program clamps every command to the limits in `config.yaml`. It also clamps each hip's sideways roll to a range that shrinks as the leg swings far forward: there, the thigh would otherwise reach the hip-yaw keeper.
2. **Servo limits.** `python -m jx0bot.calibrate limits` (bring-up step 4) writes each joint's range, 1° wider, into its servo. The servo then refuses any position outside it, whatever the Pi sends.
3. **Printed stops.** Past that, the first contact is always printed bracket on printed bracket, 2–15° further, never a screw head, a cable or a servo case:
   - **Ankle pitch:** the block on top of the ankle bracket's arms meets the bottom of the shin's plates, 3° past the limit.
   - **Ankle roll:** the ankle bracket meets the foot's U, after 2° (inward) or 4° (outward); the recess on the foot's arms keeps the shin clear.
   - **Elbow:** the post beside the shoulder servo's plugs stops the blade 8° past the limit, before it can reach the plugs.
   - **Knee, hip pitch and hip roll:** the U-brackets meet each other.
   - **Hip yaw:** the keeper's lip meets the end of its groove.

Inside the limits, 2,170 poses were checked: hip yaw × pitch × roll, ankle pitch × roll, and shoulder × elbow. None has a contact.

## 2. Before assembly: servo IDs, centring, horn height

Every STS3215 ships as ID 1. Set the IDs one servo at a time and write each on its case. The table is in
[wiring.md](wiring.md): legs 1–12, arms 13–16, neck 17. Then chain the servos, run
`python -m jx0bot.calibrate center`, and fit every horn and bracket while the servos hold mid-travel.
[bringup.md](bringup.md) has the commands.

**Horn height, every servo.**
1. Put the drive horn on its spline and the passive horn on the rear boss.
2. Measure across the two horn faces with calipers.
3. The brackets are built for 36.55 mm. Put the right number of 0.4 mm shims (JX0_HornShim) between the drive horn and
   whatever bolts to it:

| Measured across both horns | Shims under the drive horn's arm |
|---|---|
| 36.35 mm or more | none |
| 35.95 – 36.35 mm | 1 |
| less than 35.95 mm | 2 |

Use the same count on the chest pads, the blades and the neck hub. The hip-yaw discs are the exception: they hang
under the pelvis's ring, so their shims are set by feel (step 3). The passive horn needs no screw of its own: it sits
on the rear boss and the bracket's 4 screws hold it.

**Cables first.** Plug both of a servo's cables in before it goes into its cage. Bend the wires flat against the rear
face, toward the far end of the case (away from the horn). They lie in the cage plate's window and come out past the
cage's end wall. Leave a loop at every joint for its full range.

## 3. Assemble

Rules at every leg joint:
- **Each servo goes into its cage the way the step says**, and its M2 × 6 CSK case screws go in through the cage's plate.
  The heads sink flush.
- **A U-bracket slides onto its servo from below.** Its boss glides over the cage's thin strip onto the passive horn,
  and a groove in the boss lets the rear boss's tip through. The drive horn sits on its spline *without* its centre
  screw while the bracket goes on. Then:
  1. the shims;
  2. 4 × M3 × 6 into the drive horn (the small screws from the servo's bag);
  3. the horn's centre screw (M3 × 6, from the servo's bag) through the arm's centre hole;
  4. 4 × M3 × 8 pan heads through the boss into the passive horn.

All three hip axes meet at the hip centre and both ankle axes at the ankle centre, as the walking model assumes.

**The hips, on the robot (both sides before the lower legs).** Left side shown; the right is the mirror image.

1. **Pelvis.**
   - Press the 4 M3 heat-set inserts into the plate's 4.0 mm holes, flush with the top (soldering iron at about
     220 °C).
   - Fit each hip-yaw servo's drive horn with its centre screw. No passive horn on the yaw servos.
   - Push the servo up into its cage from below, with its cables plugged in and fed up through the plate's window.
   - Screw it through the top plate: 4 × M2 × 6 CSK, the heads sink below the surface.
2. **Yaw ring insert.** Push it up around the yaw horn into the gap under the case, straight edges between the ends
   of the pelvis's ring. Put one layer of PTFE tape on its underside.
3. **Hip-yaw bracket.**
   - On the bench, slide the hip-roll servo into the bracket's cage from the front, horn side first. Both horns go on
     first, the drive horn without its centre screw.
   - Screw it through the back plate: 3 × M2 × 6 CSK.
   - Put one layer of PTFE tape on the top of the disc and one under its flange (the rim above the groove).
   - Bolt the disc to the yaw horn from below with one shim, 4 × M3 × 6 through the sunk holes. It must turn freely
     just under the pelvis's ring and the insert: if it rubs, add a shim (up to 3). Up to 0.5 mm of gap is fine; the
     PTFE tape takes it up.
4. **Keeper.**
   - Slide it in sideways from the outer front of the hip, its lip into the groove under the disc's flange.
   - Clamp it flat against the pelvis's boss with 5 × M2 × 10 CSK from below.
   - Turn the leg by hand: it must turn freely through ±12° with no up-and-down wobble at the disc's rim. The lip
     sits up to 0.5 mm under the flange: add layers of PTFE tape under the flange (and on the insert's top) until the
     wobble is gone; if it binds, take one off.
5. **Hip-roll bracket** onto the hip-roll servo from below (the rules above). The 4 roll-horn screws go in from inside
   its empty pitch cage: a long PH1 screwdriver through the 4 holes in the cage's front wall. Their heads sink into
   the arm, 0.5 mm from where the pitch servo will sit, so they must be no taller than 2.4 mm: measure one of the
   servo bag's screws first.
6. **Hip-pitch servo** into the hip-roll bracket's pitch cage from the outer side, horn side first, both horns on (no
   centre screw yet). Screw it through the inner plate: 3 × M2 × 6 CSK. On the second leg the first leg is in the
   way: a PH1 bit turned by hand (50 mm of room).

**Each lower leg on the bench, then onto its hip.**

7. **Thigh and knee servo.**
   - Slide the knee servo into the thigh's knee cage from the front, both horns off.
   - Screw it with 3 × M2 × 6 CSK: the near one through the inner plate, the two far ones through the holes in the inner
     arm.
   - Fit the passive horn from the inner side, through the plate's hole, and the drive horn (no centre screw yet).
8. **Shin and ankle-pitch servo.**
   - Slide the ankle-pitch servo up into the shin's cage from below, drive horn on with its centre screw, no passive
     horn. Its label block runs up the slot in the plate.
   - Screw it with 2 × M2 × 6 CSK, the far ones, through the holes in the inner arm. The near ones would break into the
     slot, so there are none.
   - Fit the passive horn through the plate's slot. Take the drive horn's centre screw out again before the next
     bracket.
   - Slide the shin onto the knee servo from below (the rules above).
9. **Ankle bracket and foot.**
   - Slide the ankle-roll servo into the ankle bracket's cage from the inboard end, both horns off.
   - Screw it through the back plate: 3 × M2 × 6 CSK.
   - Fit its passive horn from behind and its drive horn.
   - Slide the foot onto it from below (the rules above).
   - Glue the 1 mm rubber sheet under the sole (contact cement) and trim it flush.
   - Then slide the ankle bracket, with the foot, onto the ankle-pitch servo from below (the rules above).
10. **Lower leg onto the hip-pitch servo** from below (the rules above). The 4 hub screws on the inside of the leg
    face the other leg: a PH2 bit turned by hand or with a small spanner (40–45 mm of room).

Body, arms and head:

11. **Lower torso** onto the pelvis:
    - Feed the hip-yaw servos' cables up through the two openings in the floor and the leg cables through the rear
      slot.
    - Screw it down with 4 × M3 × 8 socket heads into the inserts (their tips go on into the holes in the pelvis's ribs).

    Inside:
    - the Raspberry Pi on the back-wall standoffs (4 × M2 × 8 CSK, cutting their own thread);
    - the battery on the floor, with the servo driver and the UBEC beside it;
    - the push-to-talk button in the back wall.
12. **Arms**, each side, on the bench:
    - Shoulder servo into the hood from the chest side, horn side first. Its cables go out through the window in the
      outer plate. Screw it to the outer plate: 4 × M2 × 6 CSK.
    - Elbow servo into the box below from the outer side, horn side first. Its cables run along the inner plate to the
      front. Screw it to the inner plate: 4 × M2 × 6 CSK.
    - Blade onto the elbow horn: shims, 4 × M3 × 6 from the servo bag, heads down in the boss.
13. **Chest cap**:
    - Stand the **neck servo** on the top, its cables down through the window under it. Screw it from inside the cap:
      4 × M2 × 6 CSK into the 0.5 mm pads.
    - Fit the speaker under the round grille.
    - Bolt each **shoulder horn** to its pad on the cap's side wall from inside the cap: shims, 4 × M3 × 6, the
      shoulder horn's centre screw through the pad's centre hole. The arm now hangs from the pad.
    - Slide the cap over the torso lip and fix it with 4 × M2 × 8 CSK through the cap wall, front and back (they cut
      their own thread in the lip's 1.8 mm holes; do not overtighten).
13b. **Chest camera** (a USB webcam head, about 85 × 35 × 25 mm: measure yours first):
    - Take the webcam off its clip so only the head and its cable are left.
    - From inside the torso, slide the head between the two shelves behind the front wall, lens in the round window,
      cable down through the gap in the bottom shelf.
    - Put the clamp plate over the shelves' back ends and fix it with 4 × M2 × 10 CSK; it presses the head against the
      wall. If the head is thinner than 25 mm, add foam tape behind it.
    - Plug the cable into one of the Raspberry Pi's USB ports.
14. **Head**:
    - Fit the neck horn's centre screw first.
    - Bolt the **neck hub** to the neck horn from above: shims, then 4 × M3 × 8 pan heads, a normal screwdriver.
    - Glue the microphone behind the three holes between the eyes and take its cable down through the hole in the hub,
      with slack for ±80° of head turn.
    - **Eyes** (two WS2812 12-LED rings, 50 mm): solder three wires to each ring's back pads first (5 V, GND, and
      data in; on the left ring also data out). Measure the ring's hole: the pupil boss is 33 mm, for a hole of about
      35 mm. Feed the wires through the slot under each eye pocket from the front, turn the ring so its pads sit over
      the slot, and press it onto the pupil, LEDs out. Inside the head, chain left DO → right DI and join the two 5 V
      and the two GND; the three wires (5 V, GND, data) go down the hub's cable hole with the microphone's. Nothing
      shows in front.
    - Press a clear **eye lens** over each ring, flush with the face; a few dots of clear silicone at the rim (not CA:
      it fogs clear PETG).
    - Slide the head down over the hub and fix it with 2 × M2 × 10 CSK through the back wall into the hub.

Look at `jx0/cad/JX0_Robot.SLDASM` in SolidWorks, or the pictures in [../README.md](../README.md), whenever a
part's orientation is unclear.

## 4. Wire, bring up, install the software

- [wiring.md](wiring.md): power, the servo bus chains and IDs, where every servo's cables go, the GPIO map.
- [bringup.md](bringup.md): IDs, centring, zero pose, directions, stiffness, first stand and first steps.
- [software_setup.md](software_setup.md): Raspberry Pi OS, audio, voice models, the Claude API key, start on boot.

## Fasteners, tools and small parts

Every screw below was checked against the servo's real holes (verify_fit): the plate under its head, its thread,
that it doesn't bottom out. These are the screws bought on 2026-10-15; nothing else is needed.

| Item | Where | Notes |
|---|---|---|
| M2 × 6 CSK (56 of the 70 bought) | every servo case screw | the head bears on the hole's edge in the plate's recess, 2.2 mm into the case's Ø1.6 × 2.9 mm holes |
| M2 × 10 CSK (16 of 70) | hip-yaw keepers (10), head into the neck hub (2), camera clamp (4) | into 1.8 mm printed pilots |
| M2 × 8 CSK (8 of 40) | Raspberry Pi (4), chest cap into the torso lip (4) | into 1.8 mm printed pilots |
| M3 × 6 horn screws from the servo bags (64) | U-bracket horn arms (40), hip-yaw discs (8), shoulder pads (8), arm blades (8) | 3.0 mm into the POM drive horn; on the hip-roll arms the heads must be 2.4 mm high or less |
| M3 × 8 pan head (44 of 45) | through each U-bracket's boss into the passive horn (40), neck hub onto the neck horn (4) | 2.3 mm into the passive horn |
| M3 × 8 socket head (4 of 10) | torso floor into the pelvis's inserts | the tips go on into holes in the ribs below |
| M3 × 4 brass heat-set inserts (4) | the pelvis plate's four 4.0 mm holes | press in with a soldering iron at about 220 °C |
| Nuts, washers | none needed | every screw goes into a servo hole, an insert or a printed hole |
| 0.4 mm horn shims (40, printed) | between a drive horn and its arm | count from the horn-height table (step 2) |
| PTFE thread-seal tape | top of each hip-yaw disc, under its flange and the yaw ring insert: layers set the play | (or silicone grease) |
| 1 mm rubber sheet | foot soles | any thin anti-slip mat works |
| Servo cables, 5264 3-pin, 30 cm (4) | hip-yaw servo down to the hip-roll servo, driver to the right leg, arms into the chest | the STS3215's sockets are 5264, not JR/Dupont |
| Hot glue, zip ties, double-sided foam tape | microphone, battery, wiring | |

**Tools:**
- PH1 and PH2 screwdrivers, and a long PH1 (the roll-horn screws, through the pitch cage);
- PH1 and PH2 bits (25 mm), turned by hand or with a small spanner, for the screws on the inside of the hips;
- a 2.5 mm hex key (the 4 torso screws);
- calipers (horn height);
- a soldering iron (inserts).
