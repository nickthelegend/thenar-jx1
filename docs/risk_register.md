# JX1 risk register (v0.3, 2026-09-24)

Likelihood (L) and impact (I) on a 1–5 scale; score = L × I.

| ID | Risk | L | I | Score | Mitigation | Owner / status |
|---|---|---|---|---|---|---|
| R1 | Actuator import: customs delay, duty higher than the 32.3 % assumed, courier damage | 3 | 4 | 12 | order one of each class first for bench tests; China-distributor quote in parallel; 2 spares of RS04/RS06 | Procurement / OPEN |
| R2 | Hip-yaw torque 3 % under policy peak (RS06 36 vs 37.3 N·m) | 3 | 2 | 6 | cap yaw torque in controller, or upgrade hip yaw to RS03 (+0.26 kg/leg, +₹2k each) | Design / OPEN (OI-2) |
| R3 | Printed PA-CF brackets creep/crack under RS04 120 N·m peaks | 3 | 4 | 12 | FEA + printed test coupons; aluminium fallback for hip-roll bracket and shin knee plate; heat-set inserts rated for torque | Design / OPEN (OI-4) |
| R4 | MAI bolt patterns ASSUMED — parts won't bolt to real RobStride housings | 4 | 3 | 12 | dimension vendor STEP/drawings before release; everything is parametric (`tools/cad/params.py`) | Design / OPEN (OI-1) |
| R5 | Knee range 120° limits get-up / kneeling behaviours | 3 | 2 | 6 | V2: knee actuator on the thigh top with push-rod (−24 % hip-pitch torque, frees the knee envelope) | V2 |
| R6 | Ankle corner (+30° plantarflexion with −20° roll): rod B touches motor B | 4 | 2 | 8 | firmware pitch–roll limit polygon; V2 crank offset angle | Controls / OPEN (OI-3) |
| R7 | Jetson Nano software end-of-life (Ubuntu 18.04, JetPack 4.6.6 final, no CAN) | 4 | 2 | 8 | USB CAN hubs isolate the computer; ROS 2 in container; Orin Nano drop-in upgrade (₹50k) | Architecture / MITIGATED |
| R8 | Classic CAN bandwidth for 21 joints at 500 Hz | 2 | 3 | 6 | 6 buses (≤ 3 leg joints per bus → 45 % load) | Architecture / MITIGATED |
| R9 | Sim-to-real gap (masses, friction, backlash, actuator curves unmeasured) | 4 | 3 | 12 | bench sys-ID of each actuator class; weigh printed parts; update URDF/MJCF from measurements | Test / OPEN |
| R10 | Li-ion pack (468 Wh) fire during charge/fall | 2 | 5 | 10 | smart BMS, 58 V fuses, printed pack enclosure + FR liner, charge outside robot, no charging unattended | Safety / DESIGNED |
| R11 | Falls during bring-up destroy actuators/structure | 4 | 4 | 16 | gantry + harness for all early tests; soft covers on knees/hips; fall-detection damping | Test / PLANNED |
| R12 | Leg–leg self-collision in adduction (> ≈ 8°) | 3 | 2 | 6 | controller self-collision checks; collision meshes in sim | Controls / OPEN |
| R13 | Cost overrun — actuators are 78 % of the BOM | 3 | 3 | 9 | China-distributor route (−₹1.87 lakh); V2 DIY actuator localisation; negotiate bulk | Cost / OPEN |
| R14 | Thermal: RS04 rated torque assumes a 345 × 345 mm Al heat sink; printed mounts sink less heat | 3 | 3 | 9 | aluminium thigh plate on the knee housing; thermal monitoring; RMS utilisation ≤ 61 % in analysis | Design / PARTLY MITIGATED |
| R15 | Single supplier (RobStride) for all 21 joints | 2 | 4 | 8 | MAI envelopes accept Damiao / SteadyWin alternatives; protocol abstraction in hub firmware | Architecture / MITIGATED |
| R16 | Walking performance unproven — analysis is ZMP-based, not a physical or RL-sim demonstration | 5 | 3 | 15 | MuJoCo validation (standing, squat, swing), then RL training in Isaac Lab before hardware | Sim / OPEN |
