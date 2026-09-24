# JX1 risk register (v0.4, 2026-09-24)

Likelihood (L) and impact (I) on a 1–5 scale; score = L × I.

| ID | Risk | L | I | Score | Mitigation | Owner / status |
|---|---|---|---|---|---|---|
| R1 | Actuator import: customs delay, duty higher than the 32.3 % assumed, courier damage | 3 | 4 | 12 | order one of each class first for bench tests; China-distributor quote in parallel; 2 spares of RS04/RS06 | Procurement / OPEN |
| R2 | Hip-yaw torque margin (RS06 36 N·m vs 37.3 N·m policy peak, growing with the aluminium structure) | 4 | 2 | 8 | iteration-2 analysis with CAD masses (OI-15); controller torque cap or RS03 hip yaw (+0.26 kg/leg) | Design / OPEN (OI-2) |
| R3 | Printed PA-CF brackets fail under RS04-class loads | 5 | 4 | — | **materialised in analysis** (FEA SF 0.07–0.89): primary leg load path redesigned in 6061/7075 plate; printed parts kept only for low-load items (neck bracket, head, gripper, covers) | Design / MITIGATED (design); residual → R20 |
| R4 | MAI bolt patterns ASSUMED — parts won't bolt to real RobStride housings | 4 | 3 | 12 | dimension vendor STEP files before release; everything is parametric (`tools/cad/params.py`) | Design / OPEN (OI-1) |
| R5 | Knee range 120° limits get-up / kneeling behaviours | 3 | 2 | 6 | V2: knee actuator on the thigh top with push-rod | V2 |
| R6 | Ankle corner (plantarflexion + inversion): rod B touches motor B | 2 | 2 | 4 | CAD-derived coupled pitch/roll limit polygon in `joint_map.yaml`, enforced by the controller | Controls / MITIGATED (OI-3) |
| R7 | Jetson Nano software end-of-life (Ubuntu 18.04, JetPack 4.6.6 final, no CAN) | 4 | 2 | 8 | USB CAN hubs isolate the computer; ROS 2 in container; Orin Nano drop-in upgrade (₹50k) | Architecture / MITIGATED |
| R8 | Classic CAN bandwidth for 21 joints at 500 Hz | 2 | 3 | 6 | 6 buses (≤ 3 leg joints per bus → 45 % load) | Architecture / MITIGATED |
| R9 | Sim-to-real gap (masses, friction, backlash, actuator curves unmeasured) | 4 | 3 | 12 | bench sys-ID of each actuator class; weigh parts; update URDF/MJCF from measurements | Test / OPEN |
| R10 | Li-ion pack (468 Wh) fire during charge/fall | 2 | 5 | 10 | smart BMS, 58 V fuses, pack enclosure + FR liner, charge outside robot, no unattended charging | Safety / DESIGNED |
| R11 | Falls during bring-up destroy actuators/structure | 4 | 4 | 16 | gantry + harness for all early tests; soft covers on knees/hips; fall-detection damping | Test / PLANNED |
| R12 | Leg–leg self-collision in adduction (> ≈ 8°) | 3 | 2 | 6 | controller self-collision checks; collision meshes in sim | Controls / OPEN |
| R13 | Cost overrun — actuators are ≈ 76 % of the BOM; CNC/laser prices unquoted | 3 | 3 | 9 | China-distributor route (−₹1.87 lakh); quotes with the DXF/STEP set; V2 DIY actuator localisation | Cost / OPEN |
| R14 | Thermal: RS04 rated torque assumes a large Al heat sink | 2 | 3 | 6 | aluminium thigh/shin/hip brackets now sink heat; thermal monitoring; RMS utilisation ≤ 61 % in analysis | Design / MITIGATED |
| R15 | Single supplier (RobStride) for all 21 joints | 2 | 4 | 8 | MAI envelopes accept Damiao / SteadyWin alternatives; protocol abstraction in hub firmware | Architecture / MITIGATED |
| R16 | Walking performance unproven — ZMP analysis, not a physical or RL-sim demonstration | 5 | 3 | 15 | MuJoCo validation (standing, squat, swing) on the CAD-derived model, then RL training in Isaac Lab before hardware | Sim / OPEN |
| R17 | RobStride output-bearing tilting-moment capacity unpublished; hip-yaw RS06 carries the leg's pitch/roll moments | 3 | 4 | 12 | request ratings from RobStride; provision a yaw support bearing (pelvis ↔ yaw bracket) | Design / OPEN (OI-14) |
| R18 | Mass growth (aluminium structure, real upper body) erodes actuator margins (hip yaw, hip roll, ankle) | 4 | 3 | 12 | CAD-mass iteration-2 analysis (OI-15); lightening pockets in the 7075/6061 parts; RS03 hip-yaw option | Design / OPEN |
| R19 | Arm–thigh contact with arms hanging straight during hip abduction | 3 | 2 | 6 | shoulder-roll ≥ 8° posture while walking (controller constraint) or wider shoulders | Controls / OPEN (OI-18) |
| R20 | Bolted aluminium plate joints slip or loosen (FEA assumes monolithic parts) | 3 | 3 | 9 | dowel pins at every plate joint, 12.9 bolts at 70 % proof preload with thread-locker, retorque after first hours | Design / OPEN (OI-17) |
