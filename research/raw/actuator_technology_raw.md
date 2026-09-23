# JX1 — Actuator technology survey (RAW)

- Project: JX1 low-cost compact humanoid (≈1.2 m, 20–30 kg target, 6-DOF legs), to be built in India.
- Compiled: 2026-09-24 by the actuator-research agent (with parallel sub-searches; every number below was read from the cited page on 2026-09-24 unless marked otherwise).
- Status: RAW research notes — not a design decision. Torque requirements are NOT fixed; the working classes used here are: **Large** (hip pitch/roll, knee) ≈ 40–90 N·m peak; **Medium** (hip yaw, ankle, shoulder) ≈ 15–40 N·m peak; **Small** (elbow, wrist, neck) ≈ 3–15 N·m peak; leg joint speed ≈ 8–20 rad/s.

## Contents
- A. Executive summary: best candidates per torque class, consolidated shortlist tables, illustrative roll-ups
- 0. Labels, conventions and caveats
- 1A. Integrated actuators: RobStride (= Lingzu 灵足时代), Damiao, Unitree, HighTorque, DEEP Robotics, Encos, Xiaomi CyberGear
- 1B. Integrated actuators: CubeMars, MyActuator RMD-X, SteadyWin GIM, LK-Tech MG
- 2. Bus servos (Feetech STS/HLS/SCS/SM, ROBOTIS Dynamixel, Hiwonder)
- 3. DIY actuators (Berkeley Humanoid Lite, ODRI/Solo, Doggo, mjbots, Urs et al., Roozing, OpenTorque, Aaed Musa, COMPAct, James Bruton, Paul Gould …) and printed-reducer failure modes
- 4. Hobby BLDC motor data (T-Motor, SunnySky, MAD, Eaglepower, iFlight, Tarot, Flipsky, Maytech, ODrive, Rctimer)
- 5. Motor drivers with CAN (B-G431B-ESC1/Recoil, ODrive, clones, moteus, VESC, SimpleFOC, Tinymovr, MAB, CubeMars/Damiao/SteadyWin boards, mini-cheetah)
- 6. Actuators used by Unitree G1/H1/R1, Berkeley Humanoid Lite, ToddlerBot, K-Scale K-Bot/Zeroth, Booster T1/K1, Poppy, AGILOped and others, with lessons and JX1 sizing data
- 7. India availability leads
- 8. Process notes, conflicts and gaps

Sections 1B–6 keep their own internal numbering (e.g. "1. Master table") under their top-level heading, and each restates its label conventions.

## A. Executive summary: best candidates per torque class

All ranking numbers in this part are **ESTIMATED**: USD per peak N·m = price ÷ peak, N·m/kg = peak ÷ mass, rad/s = rpm × 2π/60. The inputs are labelled in the detailed sections. Prices are single-unit list prices without shipping or Indian duty/GST.

### A.1 Headline findings

1. **Buying integrated quasi-direct-drive (QDD) CAN actuators is cheaper per N·m than DIY at every torque class we care about.**
   - RobStride RS04 is **$2.12 per peak N·m**: $255, 120 N·m, 1.42 kg, 20.9 rad/s no-load at 48 V (VERIFIED on robstride.com).
   - Damiao DM-J10010L-2EC is **$2.21 per peak N·m** at a reseller price: $265, 120 N·m, 1.37 kg, 20.9 rad/s.
   - The best documented DIY printed-reducer large joint is Roozing's 11:1 printed cycloid (PLA 2022 / PA6-CF 2024): 36.4 N·m nominal, ≈$353–391 including half a dual-axis ODrive, i.e. ≈$9.7–10.7 per N·m (ESTIMATED, §3).
   - DIY stays interesting only for small joints, or if local machining and labour in India are much cheaper than import cost. Section 3 shows **no published life test of a printed reducer longer than ~60 h or above ~50% of rated torque**.
2. **The China-domestic list prices are ≈32–47% below the USD export prices for the same RobStride part.** RobStride publishes both on its own site (the CN-locale page shows ¥, the EN page shows $):
   - RS04: ¥1,199 vs $255
   - RS03: ¥999 vs $225
   - RS02: ¥699 vs $145
   - RS00: ¥598 vs $125
   - At 1 USD = 7.1 CNY, RS04 would be $169, i.e. **$1.41 per N·m** (ESTIMATED).
   - A third-party open-source humanoid BOM (Roboto Origin) lists Damiao DM-4340P (48 V) at ¥949 and DM-10010L at ¥1,989 via Taobao (UNVERIFIED as an official price).
   - Sourcing through a Chinese distributor or agent is worth pricing (another agent owns India/import checks).
3. **Speed prunes the "cheapest per N·m" lists hard.** High-ratio actuators are the most torque-dense and cheapest per N·m, but they are too slow for knees and hips at 8–20 rad/s. Examples:
   - SteadyWin GIM8108-48: $1.63/N·m, 4.2 rad/s
   - SteadyWin GIM8108-36: 6.3 rad/s
   - Damiao DM-J6248P: 97 N·m in 628 g but 6.3 rad/s
   - CubeMars AKH70-48: 3.7 rad/s
   - HighTorque HTDW 35–36:1 modules: 6–8 rad/s
   
   Single-stage 7.75–10:1 QDDs are what reach ≥20 rad/s: RobStride RS03/RS04, Damiao J10010L/J8009P, SteadyWin 8108-8/8115-9, CubeMars AK/AKE.
4. **Peak torque numbers are not comparable across vendors.**
   - Definitions differ: SteadyWin quotes stall torque; Unitree splits "opposing" and "same-direction" torque; RobStride rates continuous torque on a 90×85 mm to 345×345 mm aluminium heat-sink plate.
   - Section 6 shows Unitree publishing 90 / 120 / 111 / 131 / 139 N·m for the same G1 knee.
   - Specify JX1 actuators by T-N curve plus continuous torque, and bench-test them.
5. **Sizing anchor from Section 6** (ESTIMATED from VERIFIED URDFs):
   - The Unitree R1 (1.23 m, 27–29 kg, $4,900–5,900) runs every hip and knee joint at 60 N·m @ 18.8 rad/s.
   - Booster T1 (1.18 m, 30 kg) trains walking with a 60 N·m knee.
   - A JX1 knee of **≈50–60 N·m minimum, 60–90 N·m with headroom** at ≥15–20 rad/s no-load is consistent with the field.
6. **Bus servos stop at the small class.** Best value is Hiwonder HTD-85H (8.34 N·m stall, $39.99 → $4.80 per stall N·m) or Feetech STS3250 (4.9 N·m stall / 1.57 N·m rated, ~$43). Continuous torque is only ~20–33% of stall, feedback is position-oriented, and K-Scale abandoned STS3215 legs as too slow. Use them only for neck, wrist or grippers (see §2).
7. **Bus planning.** Classic 1 Mbps CAN carries only ≈5–6 joints per bus at 500 Hz (ESTIMATED, §1A). RobStride uses 29-bit extended frames, Damiao 11-bit standard frames, and the newer Damiao J6216/J6248/J10422 use CAN-FD up to 5 Mbps. Unitree uses RS-485 at 4–6 Mbps. Plan 4–5 CAN buses for ~20–24 joints at 500 Hz (Berkeley Humanoid Lite used 4 buses at 250 Hz).

### A.2 Consolidated shortlist tables (integrated actuators; sorted by USD per peak N·m)

Columns: "China list ¥" is RobStride's own CN-locale retail price (VERIFIED) or, for Damiao, the Taobao price in the Roboto Origin BOM (UNVERIFIED). Both are converted at 1 USD = 7.1 CNY (ESTIMATED). USD/rated N·m uses the maker's rated/continuous torque, which is usually measured on a heat-sink plate. Damiao listings (reseller and Taobao BOM) do not state the hardware revision: DM-J4340 V1.0 is 27 N·m peak and V1.1 is 40 N·m. The USD/N·m values for the 4340 rows assume V1.1; for V1.0 multiply by 40/27 ≈ 1.48.

#### LARGE (hip pitch/roll, knee; ~40–90 N·m peak)

| Actuator | Peak / rated N·m | Mass g | Ratio | No-load rad/s | Interface | Price USD (basis) | USD/peak N·m | USD/rated N·m | N·m/kg | China list ¥ → USD @7.1 → USD/peak N·m | Label |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RobStride RS04 | 120.0 / 40.0 | 1420 | 9:1 planetary | 20.9 @48 V | CAN 1M (29-bit ext.) | $255.00 (official) | 2.12 | 6.38 | 84.5 | ¥1199 → $169 → 1.41 | V |
| Damiao DM-J10010L-2EC | 120.0 / 40.0 | 1372 | 10:1 planetary | 20.9 @48 V | CAN 1M (11-bit) | $265.00 (AIFITLAB (U)) | 2.21 | 6.62 | 87.5 | ¥1989 → $280 → 2.33 | V specs / U price |
| Damiao DM-J10010-2EC | 150.0 / 40.0 | 1485 | 10:1 planetary | 15.7 @48 V | CAN 1M | $455.00 (AIFITLAB (U)) | 3.03 | 11.38 | 101.0 | — | V specs / U price |
| SteadyWin GIM10015-9 + GDS810 (48 V) | 104.0 / 32.6 | 1372 | 9:1 planetary | 11.0 @48 V (max) | CAN & RS485 | $355.80 (official) | 3.42 | 10.91 | 75.8 | — | V |
| RobStride RS03 | 60.0 / 20.0 | 880 | 9:1 planetary | 20.4 @48 V | CAN 1M | $225.00 (official) | 3.75 | 11.25 | 68.2 | ¥999 → $141 → 2.35 | V |
| CubeMars AKE90-8 + AK80-4830 board | 170.0 / 55.0 | 1400 | 8:1 planetary | 22.0  | CAN (board) | $643.80 (official (motor $483.90 + board $159.90)) | 3.79 | 11.71 | 121.4 | — | V (mass excl. board) |
| SteadyWin GIM8115-9 + GDS810 (48 V) | 46.0 / 13.8 | 705 | 9:1 planetary | 15.3 @48 V (max) | CAN & RS485 | $213.80 (official) | 4.65 | 15.49 | 65.2 | — | V |
| MyActuator RMD-X8-120 V4 | 120.0 / 43.0 | 1400 | 19.6:1 planetary | 16.5  | CAN / EtherCAT | $645.00 (AIFITLAB (U)) | 5.38 | 15.00 | 85.7 | — | V specs / U price |
| MyActuator RMD-X6-60 V4 | 60.0 / 20.0 | 820 | 19.6:1 planetary | 18.4  | CAN / EtherCAT | $490.00 (AIFITLAB (U)) | 8.17 | 24.50 | 73.2 | — | V specs / U price |
| Encos EC-A8112-P1-18 | 90.0 / 30.0 | 868 | 18:1 | 16.4 peak speed | CAN 1M | $1000.00 (AIFITLAB (U)) | 11.11 | 33.33 | 103.7 | — | U |
| CubeMars AK10-9 V3 KV60 | 53.0 / 18.0 | 940 | 9:1 planetary | 33.5 @48 V | CAN 1M | $798.90 (official) | 15.07 | 44.38 | 56.4 | — | V |
| DEEP Robotics J80-27P | 84.0 / 28.0 | 1480 | ~27 (name) | 17.0 @72 V | n/s | n/a (contact sales) | n/a | n/a | 56.8 | — | V |

#### MEDIUM (hip yaw, ankle, shoulder; ~15–40 N·m)

| Actuator | Peak / rated N·m | Mass g | Ratio | No-load rad/s | Interface | Price USD (basis) | USD/peak N·m | USD/rated N·m | N·m/kg | China list ¥ → USD @7.1 → USD/peak N·m | Label |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Damiao DM-J4340-2EC V1.1 | 40.0 / 12.0 | 362 | 40:1 | 11.7 @48 V | CAN 1M | $155.00 (AIFITLAB (U; revision not stated)) | 3.88 | 12.92 | 110.5 | — | V specs / U price |
| Damiao DM-J4340P-2EC (48 V) | 40.0 / 12.0 | 381 | 40:1, crossed-roller | 11.7 @48 V | CAN 1M | $175.00 (Seeed/AIFITLAB (U)) | 4.38 | 14.58 | 105.0 | ¥949 → $134 → 3.34 | V specs / U price |
| RobStride RS10P | 42.0 / 14.0 | 460 | 25:1 planetary | 13.1 @48 V | CAN 1M | $215.00 (official) | 5.12 | 15.36 | 91.3 | ¥859 → $121 → 2.88 | V |
| RobStride RS06 | 36.0 / 11.0 | 621 | 9:1 planetary | 50.3 @48 V | CAN 1M | $210.00 (official) | 5.83 | 19.09 | 58.0 | ¥849 → $120 → 3.32 | V |
| SteadyWin GIM8108-8 + GDS68 | 22.0 / 7.5 | 396 | 8:1 planetary | 33.5 @48 V (max) | CAN (+USB-C) | $129.20 (official) | 5.87 | 17.23 | 55.6 | — | V |
| SteadyWin GIM8108-9 + GDS810 (48 V) | 27.4 / 8.2 | 567 | 9:1 planetary | 25.3 @48 V (max) | CAN & RS485 | $189.60 (official) | 6.92 | 23.15 | 48.3 | — | V |
| Unitree IM6014 (list) | 34.4 / n/p | 535 | 12.66:1 | 54.2 @60 V | RS-485 4–6 Mbps | $269.00 (official) | 7.82 | n/a | 64.3 | — | V |
| LK MG8016E-i6v3 | 37.0 / 12.0 | 759 | 6:1 | 31.4  | CAN 1M / RS485 | $330.00 (AIFITLAB V2 price (U)) | 8.92 | 27.50 | 48.7 | — | V specs / U price |
| Damiao DM-J8009P-2EC | 40.0 / 20.0 | 963 | 9:1, crossed-roller | 35.1 @48 V | CAN 1M | $395.00 (AIFITLAB (U)) | 9.88 | 19.75 | 41.5 | — | V specs / U price |
| MyActuator RMD-X4-36 V4 | 34.0 / 10.5 | 360 | 36:1 | 11.6  | CAN / EtherCAT | $400.00 (AIFITLAB (U)) | 11.76 | 38.10 | 94.4 | — | V specs / U price |
| CubeMars AK70-9 V3 | 29.2 / 8.5 | 540 | 9:1 | 33.5 @48 V | CAN 1M | $498.90 (official) | 17.09 | 58.69 | 54.1 | — | V |
| Damiao DM-J6216P-2EC | 48.0 / 10.0 | 740 | 16:1, crossed-roller | 27.2 (V not stated) | CAN-FD ≤5 Mbps | n/a (not found) | n/a | n/a | 64.9 | — | V |
| DEEP Robotics J60-10 | 30.5 / n/p | 540 | ~10 (name) | 15.5 @24 V | CAN 1M | n/a (contact sales) | n/a | n/a | 56.5 | — | V |

#### SMALL (elbow, wrist, neck; ~3–15 N·m)

| Actuator | Peak / rated N·m | Mass g | Ratio | No-load rad/s | Interface | Price USD (basis) | USD/peak N·m | USD/rated N·m | N·m/kg | China list ¥ → USD @7.1 → USD/peak N·m | Label |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RobStride RS01 | 17.0 / 6.0 | 380 | 7.75:1 | 33.0 @36 V | CAN 1M | $130.00 (official) | 7.65 | 21.67 | 44.7 | ¥599 → $84 → 4.96 | V |
| RobStride RS02 | 17.0 / 6.0 | 405 | 7.75:1 | 42.9 @48 V | CAN 1M | $145.00 (official) | 8.53 | 24.17 | 42.0 | ¥699 → $98 → 5.79 | V |
| SteadyWin GIM6010-8 + GDS68 (24 V) | 11.0 / 5.0 | 388 | 8:1 | 44.0 @24 V (max) | CAN | $93.88 (official) | 8.53 | 18.78 | 28.4 | — | V |
| RobStride RS00 | 14.0 / 5.0 | 310 | 10:1 | 33.0 @48 V | CAN 1M | $125.00 (official) | 8.93 | 25.00 | 45.2 | ¥598 → $84 → 6.02 | V |
| SteadyWin GIM4315-8 + GDK468 | 10.2 / 3.1 | 369 | 8:1 | 20.8 @24 V (max) | CAN | $117.20 (official) | 11.51 | 38.30 | 27.6 | — | V (GDK specs unpublished) |
| LK MG6012E-i8v3 | 16.0 / 6.0 | 430 | 8:1 | 32.5  | CAN 1M / RS485 | $190.00 (AIFITLAB V2 price (U)) | 11.88 | 31.67 | 37.2 | — | V specs / U price |
| Damiao DM-J4310P-2EC | 12.5 / 3.5 | 330 | 10:1, crossed-roller | 47.1 @48 V | CAN 1M | $155.00 (AIFITLAB (U)) | 12.40 | 44.29 | 37.9 | — | V specs / U price |
| RobStride EduLite 05 | 6.0 / 1.8 | 242 | 9:1 (PM gears) | 45.0 @48 V | CAN 1M | $80.00 (official) | 13.33 | 44.44 | 24.8 | ¥299 → $42 → 7.02 | V |
| CubeMars AK45-10 V3 | 7.0 / 2.5 | 262 | 10:1 | 18.8 @24 V | CAN 1M | $155.90 (official) | 22.27 | 62.36 | 26.7 | — | V |
| MyActuator RMD-X4-10 V4 | 10.0 / 4.0 | 330 | 12.5:1 | 33.2  | CAN / EtherCAT | $345.00 (AIFITLAB (U)) | 34.50 | 86.25 | 30.3 | — | V specs / U price |
| Damiao DM-J4310-2EC V1.2 | 12.5 / 3.5 | 306 | 10:1 | 47.1 @48 V | CAN 1M | n/a (not found (V1.1 listing $125 U)) | n/a | n/a | 40.8 | — | V |

### A.3 Small joints: bus servos and DIY (stall or "peak" as published; see §2 and §3)

| Option | Peak/stall N·m (rated) | Mass g | Price USD (basis) | USD per peak/stall N·m (E) | N·m/kg (E) | Caveat | Label |
|---|---|---|---|---|---|---|---|
| Hiwonder HTD-85H | 8.34 @11.1 V (rated not published) | 153 | $39.99 (hiwonder.com official) | 4.80 | 54.5 | 240° potentiometer; 115200 baud; no independent test data | V spec/price; E |
| Hiwonder HTD-45H | 4.41 @11.1 V | 64 | $24.99 (official) | 5.66 | 69.0 | same | V; E |
| Hiwonder HX-65HM | 6.37 @12.6 V | 143.5 | $49.99 (official) | 7.84 | 44.4 | 12-bit magnetic encoder over 360° | V; E |
| Feetech STS3250 | 4.90 (1.57 rated) @12 V | 74.5 | ~$43 (WowRobo, reseller) | 8.77 (27.40 per rated N·m) | 65.8 | third-party test: 70 °C cutoff in ~8 min at 40% of stall | V spec; U price; E |
| Feetech STS3095 | 10.30 (3.43 rated) @8.4 V | 194.5 | ~$133 (reseller) | 12.92 | 52.9 | — | V spec; U price |
| Feetech SM105B (RS-485, brushless) | 14.71 (4.90 rated) | 200 | ~$188 (reseller) | 12.78 | 73.5 | test voltage not stated | V spec; U price |
| ROBOTIS XM540-W270 | 10.6 @12 V (ROBOTIS store: rated ≈20% of stall) | 165 | $482.89 (robotis.us) | 45.56 | 64.2 | ~10× Hiwonder/Feetech per N·m | V; E |
| DIY BHL "5010" (MAD 5010 110 KV + 15:1 PLA cycloid + B-G431B-ESC1) | peak not published; deployed limit 4–6 | n/p | $94 (CN BOM) / $136 (US BOM) | ~16–34 at the deployed 4–6 N·m (E) | n/p | 110 KV motor reported out of stock | V BOM; E |
| DIY BHL "6512" (MAD M6C12 150 KV + 15:1 PLA cycloid + ESC1) | ≥20 applied in test; ~25–28 ceiling (E) | printed parts 164 g + motor | $157 (CN) / $188 (US) | 7.9–9.4 at 20 N·m (E) | n/p | 60 h life test only at ~2.5 N·m | V; E |

### A.4 Best candidates by class (for picking 2–4 standard actuator classes later)

**By cost per peak N·m** (price basis in brackets):
- **Large, 40–90 N·m, needs ≥~15–20 rad/s:**
  - RobStride RS04: $2.12 (official)
  - Damiao DM-J10010L: $2.21 (reseller) / $2.33 (Taobao ¥1,989 via BOM)
  - Damiao DM-J10010: $3.03 (reseller; 15.7 rad/s)
  - SteadyWin GIM10015-9: $3.42 (official; only 11 rad/s)
  - RobStride RS03: $3.75 (official; 60 N·m, 0.88 kg)
- **Medium, 15–40 N·m:**
  - Damiao DM-J4340 V1.1 / DM-J4340P: $3.88–4.38 (reseller; 40 N·m, 0.36–0.38 kg, only 11.7 rad/s)
  - RobStride RS10P: $5.12 (42 N·m, 13.1 rad/s)
  - RobStride RS06: $5.83 (36 N·m, 50 rad/s)
  - SteadyWin GIM8108-8: $5.87 (22 N·m, 33.5 rad/s)
  - SteadyWin GIM8115-9: $4.65 (46 N·m, ~15 rad/s; listed under Large)
  - Unitree IM6014: $7.82 list / $4.36 intro offer (34.4 N·m; RS-485, not CAN)
- **Small, 3–15 N·m:**
  - Servos are cheapest per stall N·m: Hiwonder HTD-85H $4.80, HTD-45H $5.66.
  - Among backdrivable CAN QDDs: RobStride RS01 $7.65 (17 N·m; single motor-side encoder), RS02 $8.53, SteadyWin GIM6010-8 $8.53 (11 N·m), RS00 $8.93 (14 N·m).

**By torque density** (peak N·m/kg, only models that reach ≥8 rad/s no-load):
- **Large:**
  - CubeMars AKE90-8: 121 N·m/kg (motor only; plus a separate $159.90 board; 22 rad/s)
  - Encos EC-A8112-P1-18: 104 (reseller data; ~$1,000)
  - Damiao DM-J10010: 101 (15.7 rad/s)
  - Damiao DM-J10010L: 87.5 (20.9 rad/s)
  - MyActuator X8-120 V4: 85.7 (16.5 rad/s)
  - RobStride RS04: 84.5 (20.9 rad/s)
- **Medium:**
  - Damiao DM-J4340 V1.1: 110.5 (11.7 rad/s)
  - MyActuator X4-36 V4: 94.4 (11.6 rad/s)
  - RobStride RS10P: 91.3 (13.1 rad/s)
  - Damiao DM-J6216P: 64.9 (27 rad/s; new, price not found)
  - Unitree IM6014: 64.3
  - RobStride RS06: 58.0
- **Small:**
  - RobStride RS00: 45.2; RS01: 44.7; RS02: 42.0
  - Damiao DM-J4310 V1.2: 40.8
  - Servos (stall basis): Feetech SM80BL 80.5; Hiwonder HTD-45H 69.0; Feetech STS3250 65.8

### A.5 Illustrative actuator roll-ups (ESTIMATED; to inform class selection, not a decision)

Official RobStride prices, 21 actuators: 12 leg, 1 waist, 8 arm. Neck/wrist servos are excluded.

- **Option A (max headroom)**
  - Mix: 4× RS04 (knees and hip pitch), 5× RS03 (hip roll/yaw and waist), 4× RS06 (parallel-ankle pairs), 4× RS02 and 4× RS00 (arms).
  - Cost: **$4,065** at USD list, or ¥18,375 ≈ $2,588 at 7.1.
  - Actuator mass: **15.4 kg**. That is too heavy for a 20–30 kg robot. For comparison, K-Bot's comparable set is ≈15.8 kg in a 34–37 kg robot.
- **Option B (JX1-scale)**
  - Mix: 4× RS03 (knees and hip pitch, 60 N·m), 5× RS06 (hip roll/yaw and waist, 36 N·m), 4× RS02 (ankle pairs), 8× RS00 (arms).
  - Cost: **$3,530** at USD list, or ¥15,821 ≈ $2,228.
  - Actuator mass: **10.7 kg**. Average price per actuator: $168 (USD list) or $106 (CNY list).
- Arithmetic:
  - A: 4×255 + 5×225 + 4×210 + 4×145 + 4×125 = 4,065. Mass: 4×1.42 + 5×0.88 + 4×0.621 + 4×0.405 + 4×0.31 = 15.4 kg.
  - B: 4×225 + 5×210 + 4×145 + 8×125 = 3,530. Mass: 4×0.88 + 5×0.621 + 4×0.405 + 8×0.31 = 10.7 kg.
- Section 6 lesson 7 targets roughly **$150–200 per actuator** to undercut the Unitree R1 AIR ($4,900 retail). Option B meets that at USD list and beats it at CNY list.
- Option B's 60 N·m knee is at the floor of the Section 6 envelope (≈50–60 N·m at 25–30 kg). A knee linkage or a Damiao J10010L/RS04 knee would add headroom.

### A.6 Preliminary shortlist for 3 standard classes (to be confirmed after torque study and bench tests)

| Class | Candidate 1 (cost) | Candidate 2 (density/speed) | Alternates | Why |
|---|---|---|---|---|
| L (knee, hip pitch; 60–120 N·m) | RobStride RS03 (60 N·m, 0.88 kg, $225 / ¥999) if JX1 ≤ ~25 kg; else RS04 (120 N·m, 1.42 kg, $255 / ¥1,199) | Damiao DM-J10010L-2EC (120 N·m, 1.37 kg, 20.9 rad/s, ~$265 / ¥1,989) | SteadyWin GIM8115-9 (46 N·m, $213.80, ships to India); CubeMars AKE90-8 | Cheapest per N·m with ≥20 rad/s no-load; dual encoders (Damiao: output-shaft single-turn absolute, VERIFIED; RobStride: 2 × 14-bit "absolute turn", output placement not stated); CAN 1 Mbps; K-Bot precedent (RS04/RS03) |
| M (hip roll/yaw, waist, shoulder; 30–60 N·m) | RobStride RS06 (36 N·m, 621 g, $210 / ¥849, 50 rad/s) | Damiao DM-J6216P (48 N·m, 740 g, CAN-FD; price TBD) or RS10P (42 N·m, 460 g, $215 / ¥859, 13 rad/s) | SteadyWin GIM8108-8 (22 N·m, $129.20); Damiao DM-J4340P (40 N·m, 381 g, slow) | Keep one CAN protocol family if possible; RS06 and RS10P are two ends of the speed/torque trade |
| S (arms, ankle pairs, neck; 10–17 N·m) | RobStride RS00 (14 N·m, 310 g, $125 / ¥598) or RS02 (17 N·m, 405 g, $145 / ¥699) | Damiao DM-J4310-2EC V1.2 (12.5 N·m, 306 g, 16-bit dual encoder) | SteadyWin GIM6010-8 (11 N·m, $93.88); servos (Feetech STS3250 / HLS, Hiwonder HTD-85H) for neck, wrist, gripper | Backdrivable CAN QDD for sim-to-real; servos only where impact and torque control matter less |

## 0. Labels, conventions and caveats

| Label | Meaning |
|---|---|
| **VERIFIED** | Read today on an official/primary source: manufacturer web page or official store, official manual/datasheet (incl. the maker's own GitHub/Gitee), the paper/official repo for open-source designs. |
| **ESTIMATED** | Derived by us; the arithmetic is shown next to the number or in the section's calc note. |
| **UNVERIFIED** | Reseller listing, forum/video/blog, news article, or a value we could not trace to a primary page. |

Conventions:
- **Torque density** = peak torque ÷ mass (N·m/kg). **Cost per peak N·m** = unit price (USD) ÷ peak torque. Both are ESTIMATED by construction. For servos the "peak" is the manufacturer's **stall** torque.
- rad/s = rpm × 2π/60. 1 kg·cm = 0.0980665 N·m. Where only CNY is published, **1 USD = 7.1 CNY** (stated where used).
- Prices are single-unit list prices for reference only (no shipping, Indian customs duty/IGST, or volume discount). "Official" = manufacturer's own store/site; otherwise the reseller is named and the price is UNVERIFIED.
- **Peak torque is not comparable 1:1 across brands**: some quote a short-duration dynamic peak, some a locked-rotor (stall) value, some the torque "opposite to the rotation direction" (Unitree IM6014: 34.4 N·m opposing vs 31.7 N·m in the direction of motion). Rated/continuous torque is usually measured on a large aluminium heat-sink plate (e.g. RobStride RS04: 40 N·m on 345×345 mm, 35 N·m on 220×200 mm) — inside a humanoid limb expect lower continuous torque.
- "Backdrivability" is rarely published; unless a source is quoted it is ESTIMATED from reducer type/ratio (single-stage planetary ≤10:1 = high; 16–25:1 = medium; 36–48:1 two-stage = low–medium; harmonic/worm = very low).
- India availability: only leads are noted (another agent is checking Indian stores).

## 1A. Integrated low-cost CAN / RS-485 actuators: RobStride (= Lingzu 灵足时代), Damiao, Unitree, HighTorque, DEEP Robotics, Encos, Xiaomi

Conventions for this section: "Peak" = manufacturer's peak/maximum torque (HighTorque = "locked-rotor torque"; Unitree = "maximum torque"). No-load speed is at 48 V unless stated. rad/s = rpm × 2π/60. N·m/kg = peak torque ÷ mass. USD/N·m = unit price ÷ peak torque. CNY→USD not needed here (RobStride publishes both). All derived columns are **ESTIMATED** (arithmetic shown in the calc note at the end of this section).

### 1A.1 Master table

| Brand / model | Dia × L (mm) | Mass g | Ratio / reducer | Rated N·m | Peak N·m | Rated rpm | No-load rpm (rad/s) | V nom (range) | Rated / peak phase A | Encoder | Interface | Driver | Backdrivability | Price (official unless noted) | N·m/kg | USD/peak N·m | Label |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RobStride EduLite 05 | 46×46×44 | 242 | 9:1 planetary, powder-metallurgy gears | 1.8 | 6 | 100 | 430 (45.0) | 48 (15–60) | 2.6 / 11 Apk | 2 × 14-bit magnetic | CAN 1 Mbps | Yes | High (QDD, 9:1) — ESTIMATED | $80 / ¥299 | 24.8 | 13.33 | VERIFIED |
| RobStride 05 | 46×46×44 | 191 | 7.75:1 planetary, machined steel | 1.6 | 5.5 | 100 | 480 (50.3) | 48 (15–60) | 2.4 / 11 Apk | 2 × 14-bit (single-turn abs.) | CAN 1 Mbps | Yes | High — ESTIMATED | $110 / ¥499 | 28.8 | 20.00 | VERIFIED |
| RobStride 00 | 57×57×51 | 310 | 10:1 planetary, machined steel | 5 | 14 | 100 | 315 (33.0) | 48 (24–60) | 4.7 / 15.5 Apk | 2 × 14-bit (single-turn abs.) | CAN 1 Mbps | Yes | High — ESTIMATED | $125 / ¥598 | 45.2 | 8.93 | VERIFIED |
| RobStride 01 | 78.5×78.5×40 | 380 | 7.75:1 planetary | 6 | 17 | 100 | 315 (33.0) @36 V | 36 (24–48) | 7 / 23 Apk | **1** × 14-bit (motor side only) | CAN 1 Mbps | Yes | High — ESTIMATED | $130 / ¥599 | 44.7 | 7.65 | VERIFIED |
| RobStride 02 | 78.5×78.5×45.5 | 405 | 7.75:1 planetary | 6 | 17 | 100 | 410 (42.9) | 48 (24–60) | 7 / 23 Apk | 2 × 14-bit | CAN 1 Mbps | Yes | High — ESTIMATED | $145 / ¥699 | 42.0 | 8.53 | VERIFIED |
| RobStride 02 IP67 | (site lists 60×60×27 — looks like a copy error) | 490 | 7.75:1 | 6 | 17 | 100 | 410 (42.9) | 48 (24–60) | 7 / 23 Apk | 2 × 14-bit | CAN 1 Mbps | Yes | High — ESTIMATED | $240 / ¥999 | 34.7 | 14.12 | VERIFIED (size doubtful) |
| RobStride 06 | 88×88×49 | 621 | 9:1 planetary | 11 | 36 | 100 | 480 (50.3) | 48 (15–60) | 14.3 / 57 Apk | 2 × 14-bit | CAN 1 Mbps | Yes | High — ESTIMATED | $210 / ¥849 | 58.0 | 5.83 | VERIFIED |
| RobStride 10P | not published | 460 | 25:1 planetary (steel) | 14 (rotating) / 10 (stall) | 42 | 100 | 125 (13.1) | 48 (15–60) | 5.3 / 19 Apk | 2 × encoders | CAN 1 Mbps | Yes | Medium (25:1) — ESTIMATED | $215 / ¥859 | 91.3 | 5.12 | VERIFIED |
| RobStride 03 | 106×106×56 | 880 | 9:1 planetary | 20 | 60 | 100 | 195 (20.4) | 48 (15–60) | 12 / 43 Apk | 2 × 14-bit | CAN 1 Mbps | Yes | High — ESTIMATED | $225 / ¥999 | 68.2 | 3.75 | VERIFIED |
| RobStride 04 | 120×120×56 | 1420 | 9:1 planetary | 40 (345×345 mm heat sink) / 35 (220×200 mm) | 120 | 50 (site) / "tested at 100 rpm" (manual) | 200 (20.9) | 48 (15–60 site; 24–60 manual) | 27 / 90 Apk | 2 × 14-bit (single-turn abs.) | CAN 1 Mbps; private, CANopen & MIT protocols | Yes | High — ESTIMATED | $255 / ¥1199 | 84.5 | 2.12 | VERIFIED |
| Damiao DM-J3507-2EC | 46×37.9 | 150 | 7:1 planetary | 0.8 | 3 | 150 | 460 @24 V / 910 @48 V (95.3) | 24 or 48 | 3.0 / 8.3 | 2 × 14-bit, output single-turn abs. | CAN (handbook: CAN/CAN-FD) | Yes | High — ESTIMATED | $120 (AIFITLAB) | 20.0 | 40.00 | Specs VERIFIED; price UNVERIFIED |
| Damiao DM-J4310-2EC V1.1 | 57×46 | ~306 (handbook 300) | 10:1 planetary | 3 | 7 | 120 | 200 @24 V / 400 @48 V (41.9) | 24 or 48 | 2.5 / 7.5 (manual); 3.7 / 7.2 (handbook) | 2 × 14-bit, output single-turn abs. | CAN 1 Mbps | Yes | High — ESTIMATED | $125 (AIFITLAB) | 22.9 | 17.86 | Specs VERIFIED; price UNVERIFIED |
| Damiao DM-J4310-2EC V1.2 | 57×46 | ~306 | 10:1 planetary | 3.5 | 12.5 | 120 | 200 @24 V / 450 @48 V (47.1) | 24 or 48 | 4.9 / 20 | 2 × 16-bit, output single-turn abs. | CAN 1 Mbps | Yes | High — ESTIMATED | not found | 40.8 | n/a | VERIFIED |
| Damiao DM-J4310P-2EC | 57×49.05 | ~330 | 10:1, crossed-roller output | 3.5 | 12.5 | 120 | 200 / 450 (47.1) | 24 or 48 | 4.9 / 20 | 2 × 16-bit | CAN 1 Mbps | Yes | High — ESTIMATED | $155 (AIFITLAB) | 37.9 | 12.40 | Specs VERIFIED; price UNVERIFIED |
| Damiao DM-J4340-2EC (V1.0) | 57×53.3 | ~362 | 40:1 (2-stage planetary — ESTIMATED from ratio) | 9 | 27 | 36 | 52.5 @24 V / 100 @48 V (10.5) | 24 or 48 | 3 / 8 (24 V); 2.5 / 9 (48 V) | 2 × 14-bit | CAN 1 Mbps | Yes | Low–medium (40:1) — ESTIMATED | $155 (AIFITLAB; version not stated) | 74.6 | 5.74 | Specs VERIFIED; price UNVERIFIED |
| Damiao DM-J4340-2EC V1.1 | 57×53.3 | ~362 | 40:1 | 12 | 40 | 36 | 56 @24 V / 112 @48 V (11.7) | 24 or 48 | 4.11 / 19.85 | 2 × 16-bit, output single-turn abs. | CAN 1 Mbps | Yes | Low–medium — ESTIMATED | $155 (AIFITLAB; version not stated) | 110.5 | 3.88 | Specs VERIFIED; price UNVERIFIED |
| Damiao DM-J4340P-2EC V1.1 | 57×56.5 | ~381 | 40:1, crossed-roller | 12 | 40 | 36 | 56 / 112 (11.7) | 24 or 48 | 4.11 / 19.85 | 2 × 16-bit, output single-turn abs. | CAN 1 Mbps | Yes | Low–medium — ESTIMATED | $175 (Seeed & AIFITLAB; version not stated) | 105.0 | 4.38 | Specs VERIFIED; price UNVERIFIED (reseller) |
| Damiao DM-J6006-2EC | 76×36.5 | ~335 | 6:1 planetary | 4 | 11 | 150 | 240 (manual) / 226 @24 V, 408 @48 V (handbook) (42.7) | 24 (24–48) | 4 / 13 (manual); 5.96 / 17.6 (handbook) | 2 × 14-bit | CAN 1 Mbps | Yes | High — ESTIMATED | $150 (AIFITLAB) | 32.8 | 13.64 | Specs VERIFIED (sources disagree); price UNVERIFIED |
| Damiao DM-J8006-2EC V1.1 | 96×40 | ~559 | 6:1 planetary | 8 | 20 | 120 | 194 @24 V / 393 @48 V (41.1) | 24 (24–48) | 9 / 21 | 2 × 14-bit | CAN 1 Mbps | Yes | High — ESTIMATED | $210 (AIFITLAB) | 35.8 | 10.50 | Specs VERIFIED; price UNVERIFIED |
| Damiao DM-J8009-2EC | 98×61.7 | ~896 | 9:1, thin-section deep-groove output bearing | 20 | 40 | 100 @24 V / 200 @48 V | 160–168 @24 V / 320–335 @48 V (35.1) | 24 (24–48) | 20 / 50 (manual); 18.6 / 40 (handbook) | 2 × 14-bit, output single-turn abs. | CAN 1 Mbps | Yes | High — ESTIMATED | $470 (AIFITLAB) | 44.6 | 11.75 | Specs VERIFIED; price UNVERIFIED |
| Damiao DM-J8009P-2EC | 98×61.7 | ~963 (manual V1.3); 921 (handbook); V1.1 ~950 | 9:1, crossed-roller output | 20 | 40 | 100 @24 V / 200 @48 V | 168 @24 V / 335 @48 V (35.1) | 24 (24–48) | 20 / 40 | 2 × 14-bit (V1.1: 16-bit) | CAN 1 Mbps | Yes | High — ESTIMATED | $395 (AIFITLAB) | 41.5 | 9.88 | Specs VERIFIED; price UNVERIFIED |
| Damiao DM-J6216L-2EC (new 2026) | 67×62.5 | ~740 | 16:1 | 10 | 45 | 200 | 260 (27.2) | 24 (24–48) | 7.48 / 39.5 @24 V; 27 A @48 V as printed | 2 × 15-bit (±0.09°), output single-turn abs. | **CAN-FD up to 5 Mbps** | Yes | Medium–high (16:1) — ESTIMATED | not found | 60.8 | n/a | VERIFIED |
| Damiao DM-J6216P-2EC (new 2026) | 67×62.5 | ~740 | 16:1, crossed-roller | 10 | 48 | 200 | 260 (27.2) | 24 (24–48) | 7.45 / 36 @24 V; 7.6 / 70 @48 V | 2 × 15-bit, output single-turn abs. | CAN-FD up to 5 Mbps | Yes | Medium–high — ESTIMATED | not found | 64.9 | n/a | VERIFIED |
| Damiao DM-J6248P-2EC | 76×62.5 | ~628 | 48:1, crossed-roller | 30 | 97 | 40 | 60 (6.3) | 24 (24–48) | 11.3 / 38.7 | 2 × 16-bit | CAN-FD up to 5 Mbps | Yes | Low (48:1) — ESTIMATED | $265 (AIFITLAB) | 154.5 | 2.73 | Specs VERIFIED; price UNVERIFIED |
| Damiao DM-J10010L-2EC | 120×53 | ~1372 | 10:1 planetary | 40 | 120 | 70 @24 V / 100 @48 V | 100 @24 V / 200 @48 V (20.9) | 48 (24–48) | 23.5 / 95 | 2 × 14-bit, output single-turn abs. | CAN 1 Mbps | Yes | High — ESTIMATED | $265 (AIFITLAB) | 87.5 | 2.21 | Specs VERIFIED; price UNVERIFIED |
| Damiao DM-J10010-2EC | 112 (120 max) × 62 | ~1485 | 10:1 planetary | 40 | 150 | 100 | 150 (15.7) | 48 | 20 / 70 (manual); 18.4 / 80.2 (handbook) | 2 × 14-bit | CAN 1 Mbps | Yes | High — ESTIMATED | $455 (AIFITLAB) | 101.0 | 3.03 | Specs VERIFIED; price UNVERIFIED |
| Damiao DM-J10422P-2EC | 110×89.9, 12 mm bore | ~2700 | 22:1, crossed-roller | 100 | 400 | 100 | 120 (12.6) | 48 | 44.5 / 165 | 2 × 17-bit (±0.03°) | CAN-FD up to 5 Mbps | Yes | Medium — ESTIMATED | $480 (AIFITLAB) | 148.1 | 1.20 | Specs VERIFIED; price UNVERIFIED |
| Damiao DM-J8520P-2EC (launched WRC Aug 2026) | — | — | "hollow, high-torque"; name convention suggests ~20:1 (ESTIMATED from DM naming, e.g. J6216 = 16:1, J6248 = 48:1) | — | — | — | — | — | — | 2 encoders ("2EC") | — | Yes | — | — | — | — | Existence VERIFIED; specs not retrievable (Gitee manual login-gated) |
| Damiao DM-JH11-51/101-2EC (harmonic) | 52×60, 8.5 mm bore | ~345 | 51:1 / 101:1 harmonic | 3.2 / 4.8 | 7.8 / 10.5 | 40 / 20 | max 60 / 30 (6.3 / 3.1) | 24 (24–48) | 2.23 / 4.26; 2.3 / 3.6 | 2 × 17-bit | CAN-FD 5 Mbps | Yes | Very low (harmonic) — ESTIMATED | $325 (AIFITLAB) | 30.4 (101:1) | 30.95 | Specs VERIFIED; price UNVERIFIED |
| Damiao DM-JH14-51/101-2EC (harmonic) | 70×70, 13 mm bore | ~775 | 51:1 / 101:1 harmonic | 5.4 / 7.8 | 18 / 28 | 40 / 20 | 60 / 30 | 24 (24–48) | 4.89 / 13.7; 4.12 / 10.97 | 2 × 17-bit | CAN-FD 5 Mbps | Yes | Very low — ESTIMATED | $410 (AIFITLAB) | 36.1 (101:1) | 14.64 | Specs VERIFIED; price UNVERIFIED |
| Unitree GO-M8010-6 | 96.5×92.5×42.3 | ~530 | 6.33:1 planetary | — | 23.7 | — | 30 rad/s @24 V | 24 (12–30) | max 40 A | 15-bit rotor encoder | **RS-485 4 Mbps** | Yes | High — ESTIMATED | $369 | 44.7 | 15.57 | VERIFIED |
| Unitree A1 motor | — | 605 | planetary, crossed-roller | — | 33.5 | — | 21 rad/s | 20–40 | — | 15-bit | RS-485 | Yes | High — ESTIMATED | $500 | 55.4 | 14.93 | VERIFIED |
| Unitree IM6014 (N6014B-12.6, 2026) | φ65×60 | 535 | 12.66:1 ("3:38") metal gears | — | 34.4 (opposing) / 31.7 (same direction) | — | 54.2 rad/s @60 V | 24–75 | max line 40 A | Dual absolute (rotor 15-bit + output) | RS-485 6/4 Mbps, daisy-chain | Yes | Medium–high — ESTIMATED | $269 list; $150 intro (limit 2); $90 student | 64.3 | 7.82 (list) / 4.36 (intro) | VERIFIED |
| Unitree J288 / S288 servo | 20×34×26 | 19.5 | 288.35:1 spur | — | 1.5 / 0.6 (stall) | — | 35 rad/s @25.2 V / 16.5 rad/s @12 V | 6.4–12.6 (S288) | — | Dual absolute, 15-bit rotor | TTL bus 6 Mbps | Yes | Claimed backdrivable | $60 / $29 | — | — | VERIFIED (too small for JX1 except hands) |
| HighTorque HTDW-4438-30-NE | 44×43.4 | 237 | 30:1 planetary | 2 | 10 (locked rotor) | 40 | 160 (16.8) | — | — | Dual encoder (series claim) | CAN/FD-CAN (series docs; not checked for this model — UNVERIFIED) | Yes | Medium — ESTIMATED | "purchase enquiry" | 42.2 | n/a | VERIFIED (interface UNVERIFIED) |
| HighTorque HTDW-5022-02-DNE | 50×47.4 | 322 | 22:1 | 3.5 | 13 (locked) | 82 | 123 (12.9) | — | — | Dual | FD-CAN (product page lists an "fdcan Protocol" document) | Yes | Medium — ESTIMATED | enquiry | 40.4 | n/a | VERIFIED |
| HighTorque HTDW-5036-02-CNE | 50×47.4 | 345 | 36:1 | 6 | 21 (locked) | 50 | 75 (7.9) | — | — | Dual | FD-CAN | Yes | Low–medium — ESTIMATED | enquiry | 60.9 | n/a | VERIFIED |
| HighTorque HTDW-6036-02-CNE | 60×56 | 570 | 36:1 | 10 | 36 (locked) | 50 | 60 (6.3) | — | — | Dual | FD-CAN | Yes | Low–medium — ESTIMATED | enquiry | 63.2 | n/a | VERIFIED |
| HighTorque HTDW-7535-02-CNE | 75×56 | 850 | 35:1 | 18 | 60 (locked) | 50 | 60 (6.3) | — | — | Dual | FD-CAN | Yes | Low–medium — ESTIMATED | enquiry | 70.6 | n/a | VERIFIED |
| HighTorque HTPW-7507-02-DNE | 75×35 | 390 | 7:1 | 4 | 12 (locked) | 250 | 270 (28.3) | — | — | Dual (series claim) | CAN/FD-CAN (not checked for this model — UNVERIFIED) | Yes | High — ESTIMATED | enquiry | 30.8 | n/a | VERIFIED (interface UNVERIFIED) |
| Encos EC-A4310-P2-36 | 56×60.5 | 382 | 36:1 planetary | 12 | 36 | 75 | 89 (9.3) | 24 (48 support) | 7.8 / 30 | Dual | CAN 1 Mbps | Yes | Low–medium | $700 (AIFITLAB) | 94.2 | 19.44 | UNVERIFIED (reseller) |
| Encos EC-A8112-P1-18 | 105×53 | 868 | 18:1 | 30 | 90 | 155 | 157 (16.4) | 48 | 15.9 / 60 | Dual | CAN 1 Mbps | Yes | Medium | $1000 (AIFITLAB) | 103.7 | 11.11 | UNVERIFIED (reseller) |
| Encos EC-A10020-P1-12 | 124×60 | 1373 | 12:1 | 50 | 150 | 127 | 140 (14.7) | 48 | 21 / 70 | Dual | CAN 1 Mbps | Yes | Medium–high | $1250 (AIFITLAB) | 109.2 | 8.33 | UNVERIFIED (reseller) |
| Xiaomi CyberGear (EOL) | — | 317 | 7.75:1 | 4 | 12 | 240 | 296 (31.0) | 24 (16–28) | 6.5 / 23 Apk | 1 × AS5047P (motor side) | CAN 1 Mbps | Yes | High | launch ¥499; now $179.90 (OpenELAB, EOL) | 37.9 | 14.99 | UNVERIFIED (reseller/news) |
| DEEP Robotics J60-6 | 76.5×63 | 480 | "-6" (ratio implied by name — ESTIMATED) | — | 19.94 | — | peak speed 24.18 rad/s | 24 (18–36) | max phase 30 A | 14-bit absolute | CAN 1 Mbps (+ serial), 1 kHz | Yes | High — ESTIMATED | "Contact Sales" | 41.5 | n/a | VERIFIED |
| DEEP Robotics J60-10 | 76.5×72.5 | 540 | "-10" (ESTIMATED from name) | — | 30.50 | — | 15.49 rad/s | 24 (18–36) | max phase 30 A | 14-bit absolute | CAN 1 Mbps | Yes | Medium–high — ESTIMATED | "Contact Sales" | 56.5 | n/a | VERIFIED |
| DEEP Robotics J80-27P | 105×85.5 | 1480 | "-27" (ESTIMATED from name) | 28 | 84 | — | max 17 rad/s @72 V | 72 (28–95) | 14 / 55 A rms | Multi-turn absolute (17-bit single-turn + 16-bit multi-turn) | not shown on page | Yes | Medium — ESTIMATED | "Contact Sales" | 56.8 | n/a | VERIFIED (72 V class — slower on a 48 V bus, ESTIMATED) |

### 1A.2 Per-product notes and sources

**RobStride Dynamics (= 灵足时代 "Lingzu Shidai") — Beijing.**
- Identity: robstride.com HTML meta keywords read "RobStride, 灵足时代, 电机, 机器人" → the "Lingzu" brand in our brief is RobStride (VERIFIED, https://robstride.com/).
- Specs and retail prices: embedded in the official site's product pages (https://robstride.com/products/robStride00, …/robStride01, …/robStride02, …/robStride02Ip67, …/robStride03, …/robStride04, …/robStride05, …/robStride06, …/robStride10P, …/eduLite05). The page data were read from the site bundle https://robstride.com/assets/index-f063c142.js on 2026-09-24 (VERIFIED). Snippets: RS04 `Peak Torque 120N.m, Torque density 85.71N.m/Kg, Torque value density 0.43N.m/USD`, `price:"255"`; CN locale `price:"1199"`. RS03 `price:"225"` / `"999"`. RS02 `price:"145"` / `"699"`. RS00 `price:"125"` / `"598"`. RS05 `price:"110"`/`"499"`. RS06 `price:"210"`/`"849"`. RS10P `price:"215"`/`"859"`. EduLite05 `price:"80"`/`"299"`.
- Cross-check: Seeed Studio (linked from robstride.com as the "Order Now" channel) lists RS02 $145, RS03 $225, RS04 $255 (VERIFIED, https://www.seeedstudio.com/Robostride-02-Actuator-p-6665.html, https://www.seeedstudio.com/Robostride-03-Actuator-p-6774.html, https://www.seeedstudio.com/Robostride-04-Actuator-p-6775.html).
- RS04 manual (https://github.com/RobStride/Product_Information — `Product Literature/RS04/RS04User Manual260713.pdf`, VERIFIED): "Rated load (CW): 40 N.m (Heat sink dimensions: 345mm×345mm) 35 N.m (Heat sink dimensions: 220mm×200mm)"; "Winding Limit Temperature: 145℃"; "CAN bus bit rate 1Mbps"; "encoder resolution 14bit (absolute turn)"; manual chapters cover the private protocol, CANopen (DS402) and an "MIT Communication Protocol". → Rated torques are heat-sink-dependent; inside a humanoid limb expect lower continuous torque (ESTIMATED).
- **Rated torque is always quoted on a large aluminium heat-sink plate** (English manuals 260713/260907 in the same repo, VERIFIED): RS00 5 N·m on 90×85 mm; RS02 6 N·m on 260×280 mm; RS03 20 N·m on 215×220 mm; RS04 40 N·m on 345×345 mm (35 N·m on 220×200 mm); RS06 11 N·m on 130×160 mm; RS10P 14 N·m on 210×210 mm (winding limit 135 °C). Each manual says "Reduced heat sink size, lower rated torque". The RS02 manual gives "Weight: 380g±3g" whereas the web page gives 405 g (discrepancy, probably copied from RS01).
- RS01 has only one encoder (motor side): after power-up the output angle is ambiguous within 1/7.75 rev → needs homing or an external joint encoder (ESTIMATED from "Magnetic Encoder x 1").
- RS02 IP67 page lists "60 x 60 x 27 mm" although the part is 490 g and the same 7.75:1 unit — treat as a site copy error (UNVERIFIED).
- RobStride GitHub (https://github.com/RobStride) has manuals, STEP files, ROS samples, OTA tools; a CANopen EDS file is provided.
- Official order channels (from the site bundle): Seeed Studio product pages, Amazon.com ASINs (e.g. RS02 https://www.amazon.com/dp/B0H2HMVHK3, RS04 https://www.amazon.com/dp/B0H2HCMYR7), AliExpress store https://www.aliexpress.com/store/1103506059, Taobao. India: no Indian distributor seen in the official data; Seeed/AliExpress/Amazon.com ship internationally (lead only).

**Damiao 达妙科技 (Shenzhen) — DM-J series (all integrated FOC driver, MIT/position/speed modes).**
- Product list with rated/peak torques: https://www.damiaokeji.com/index.php?c=category&id=22 (VERIFIED). Product pages show spec tables only as images.
- Specs taken from Damiao's official manuals (Gitee https://gitee.com/kit-miao/<model> and GitHub mirror https://github.com/dmBots/<model>, read 2026-09-24, VERIFIED) and the official "2025年产品选型手册" (https://www.worldrobotconference.com/profile/robot/download/2025/06/30/达妙科技DAMIAO%20-%202025年产品选型手册_20250630192546A441.pdf, VERIFIED). Where manual and handbook disagree both are shown.
- Naming rule (from DM-J4340 V1.1 manual p.6): "2EC" = dual encoder "(输出轴单圈绝对位置)" = output-shaft single-turn absolute; suffix "P" = crossed-roller output bearing, default = deep-groove ball bearing; "L" = Lite; "C = CAN通信, E = EtherCAT通信".
- Key snippets: DM-J10010L manual p.11 "额定扭矩 40NM 峰值扭矩 120NM … 空载最大转速 100rpm@24V 200rpm@48V … 电机重量 约1372g … CAN@1Mbps". DM-J4340 V1.1 manual "额定扭矩 12NM 峰值扭矩 40NM … 减速比 40: 1 … 约 362g". DM-J6216P manual "峰值扭矩 48Nm … 减速比 1:16 … 约740g … CAN@5Mbps(Max)" and features "支持CAN FD，最大波特率5Mbps". DM-J6248P "峰值扭矩 97NM … 空载最大转速 60rpm … 减速比 48: 1 … 约628g". DM-J10422P "峰值扭矩 400.0Nm … 减速比 1:22 … 约2700g". DM-J8009P "DM-J8009P-2EC 输出轴是交叉滚子轴承，DM-J8009-2EC 输出轴是薄壁深沟球轴承".
- Protection defaults (all manuals): driver over-temp 120 °C, motor over-temp recommended ≤100 °C, CAN-loss timeout, UART@921600 tuning port.
- DM-J8520P-2EC was launched at WRC 2026 as a "中空大扭矩关节电机" (hollow high-torque) together with the DM-J6216 series (VERIFIED, https://www.damiaokeji.com/index.php?c=show&id=140). Its manual (Gitee, 2026-09-22) is login-gated (>10 MB), so no numbers.
- Prices: Damiao's own retail is Taobao (not machine-readable). Reseller prices used for USD/N·m: AIFITLAB Shopify feed https://aifitlab.com/collections/damiao (e.g. DM-J10010L $265, DM-J8009P $395, DM-J4340 $155, DM-J4340P $175, DM-J6248P $265, DM-J10422P $480; UNVERIFIED) and Seeed DM4340P $175 (https://www.seeedstudio.com/DM4340P-Actuator-p-6663.html; reseller). Reseller listings do not always say which hardware revision (V1.0 vs V1.1) is shipped — confirm before ordering.
- China price reference: the open-source humanoid Roboto Origin "ATOM 01" BOM lists "DM 4340P (48V)" ×14 at ¥949 and "DM 10010L" ×9 at ¥1989, each linked to a Taobao item (https://github.com/Roboparty/roboto_origin/blob/HEAD/assets/BOM_EN.md, read 2026-09-24; BOM content VERIFIED, price UNVERIFIED as an official Damiao price; the Taobao snapshot date is not stated). At 7.1 CNY/USD that is ≈$134 and ≈$280 (ESTIMATED). The same project describes itself as buildable entirely from Taobao parts and uses only these two Damiao models for all 23 joints.
- Damiao also sells stand-alone drivers (see §5): DM40-2E (4 A cont./10 A peak, 24 V), DM60-2E (10/20 A, 4S–12S), DM80-2E (20/40 A), DM100-2E (40/80 A); Cortex-M4 200 MHz, CAN, dual-encoder support (handbook p.25, VERIFIED).

**Unitree (Hangzhou) — RS-485 actuators.** Official pages: https://www.unitree.com/mobile/IM6014/, https://www.unitree.com/mobile/go1/motor/, https://www.unitree.com/mobile/a1/motor/, https://www.unitree.com/mobile/DigitalServo/ ; prices from the official Shopify store JSON (https://shop.unitree.com/products/unitree-im6014-motor, …/go1-motor, …/unitree-a1-motor, …/brushless-digital-servo, …/b1-motor = $3000) (all VERIFIED 2026-09-24). Snippets: IM6014 "Maximum Torque … 34.4N.m", "Weight 535g", "Input Voltage 24v~75v", "Baud Rate 6000000bps/4000000bps", "Rotor, output end, dual absolute value encoder"; GO-M8010-6 "Maximum Torque 23.7NM", "Communication Mode RS-485", "Torque Constant 0.63895Nm/A". Interface is RS-485, **not CAN** — would need RS-485 masters (Unitree sells a USB-to-4-channel-485 module, $30). IM6014 "Warranty 3 month".

**HighTorque Robotics 高擎机电 (Shenzhen) — HTDW planetary / HTPU flat / HTCP cycloidal modules.** Specs from https://www.hightorquerobotics.com/product and product pages ?id=73, 75, 76, 477, 482, 486, 489, 501, 505, 760 (VERIFIED). The site states HTDW modules have "dual absolute encoders" and documents a "fdcan Protocol"; their 7-channel main control box lists "FDCAN Baud Rate 5Mbps". Prices are "Purchase enquiry" only. Note: each product page also shows a generic Chinese reducer table (额定扭矩 12Nm / 峰值扭矩 24Nm for every model) that contradicts the headline numbers — treat those tables as template text (UNVERIFIED). High ratios (22–36:1) give no-load speeds of 60–160 rpm (6–17 rad/s), i.e. too slow for JX1 knees/hips; they suit small humanoids (Mini Pi) and arms.

**Encos (encos.cn) — premium reference.** Specs/prices only from reseller AIFITLAB (https://aifitlab.com/collections/encos-motor, UNVERIFIED): very high torque density (EC-A8112-P1-18: 90 N·m, 868 g) but $625–$2,370 per unit → 3–5× RobStride/Damiao per N·m. Not a low-cost candidate.

**DEEP Robotics 云深处 (Hangzhou) — J60 / J80 / J100 joints.** Official pages https://www.deeprobotics.cn/en/index/j60.html and https://www.deeprobotics.cn/en/index/j80j100.html (VERIFIED). J60 snippets: "Peak Torque | 19.94Nm | Peak Speed | 24.18rad/s" (J60-6, 480 g) and "Peak Torque | 30.50Nm | Peak Speed | 15.49rad/s" (J60-10, 540 g); "Comm Method | CAN | Comm Baud Rate | 1Mbps"; used in the Lite3 quadruped. J80-27P: 1.48 kg, 84 N·m peak, 28 N·m rated, 17 rad/s at 72 V rated, absolute multi-turn encoder (the page's table labels are shifted by one row — values read by position). No public prices ("Contact Sales").

**Xiaomi CyberGear — EOL.** OpenELAB lists "Xiaomi CyberGear Micromotor Intelligent Motor (EOL)" at $179.90 with 12 N·m peak, 4 N·m rated, 317 g, 7.75:1, AS5047P encoder, CAN (https://openelab.io/products/xiaomi-cybergear-micromotor-intelligent-motor, UNVERIFIED). Launch price ¥499 (https://www.smzdm.com/p/87938777/, UNVERIFIED). Same 7.75:1 / 28-pole / 187–339 µH inductance as RobStride 01/02 (compare robstride.com specs) — RS01/02 are the de-facto successors (ESTIMATED from matching specs). Do not design around CyberGear.

**Bus protocol facts relevant to wiring ~20–24 joints.**
- RobStride private protocol: "The motor communication is the CAN 2.0 communication interface, the baud rate is 1Mbps, and the extended frame format is adopted … 29-bit ID 8Byte data field" (RS04 manual p.43, VERIFIED). CANopen DS402 and MIT-style frames are also documented.
- Damiao: "控制使用CAN 标准帧格式，默认波特率为1Mbps" (standard 11-bit frames, 1 Mbps default; DM-J10010L manual p.7, VERIFIED); selectable 125k–1M (DM-J8006 manual); newer DM-J6216/J6248/J10422/JH models support CAN-FD up to 5 Mbps (VERIFIED, manuals).
- Unitree IM6014/GO-M8010-6: RS-485 at 4–6 Mbps (VERIFIED).
- Bus-budget estimate (ESTIMATED): an 8-byte classic-CAN frame is 111 bits (11-bit ID) or 131 bits (29-bit ID) before bit-stuffing, i.e. ≈7,600–9,000 frames/s at 1 Mbps (≈6,250–7,400 with worst-case stuffing). With one command + one reply per joint per cycle and ≤70 % bus load: ≈5–6 joints per bus at 500 Hz, ≈10–12 at 250 Hz, ≈2.5–3 at 1 kHz. → A 20–24-joint JX1 on 1 Mbps CAN needs ≈4–5 buses at 500 Hz (or CAN-FD / RS-485 at higher bit-rates).

### 1A.3 Calc note (ESTIMATED)
N·m/kg = peak ÷ (mass/1000); e.g. RobStride 04: 120 ÷ 1.420 = 84.5. USD/N·m = price ÷ peak; e.g. RS04: 255 ÷ 120 = 2.12; Damiao DM-J10010L: 265 ÷ 120 = 2.21; Unitree IM6014: 269 ÷ 34.4 = 7.82. Speed: RS03 195 rpm × 2π/60 = 20.4 rad/s; DM-J4340 V1.1 112 rpm → 11.7 rad/s; DM-J6216P 260 rpm → 27.2 rad/s. Unitree speeds are published in rad/s (converted to rpm only for the calc table).

## 1B. Integrated CAN actuators: CubeMars, MyActuator (RMD-X), SteadyWin (GIM), LK-Tech (MG)


Project: JX1 low-cost compact humanoid (≈1.2 m, 20–30 kg, 6-DOF legs), India build. Survey date: **2026-09-24** (all pages read today).
Author: actuator research sub-agent (Section 1b). Method: curl (desktop UA) on official pages / official Shopify JSON / official price endpoints; WebFetch for images & PDFs (then read locally from the WebFetch cache). No accounts, no forms, no ZIP/STEP/XLSX downloads.

**Labels.** VERIFIED (V) = read today on a manufacturer page, official store, or official datasheet/manual (incl. official spec images embedded in the maker's product page).
ESTIMATED (E) = derived by me; the arithmetic is shown. UNVERIFIED (U) = reseller, forum, or secondary source.
Where official sources disagree, both values are recorded.

**Derived-column conventions (all E).**
- Torque density = peak torque / actuator mass (kg). SteadyWin uses its "with driver" mass; CubeMars AKE uses its motor-only mass, because the AKE has no driver.
- USD per peak N·m = price / peak torque. The price includes a driver unless noted; for AKE the separately sold driver board is added. MyActuator and LK have no official price, so they use reseller prices, flagged [U price].
- No CNY prices were needed, because every price found was in USD. The 1 USD = 7.1 CNY rule was therefore not applied.
- Speed conversion: rad/s = rpm × 2π/60. So 8 rad/s = 76.4 rpm and 20 rad/s = 191.0 rpm at the output.
  - "No-load" (NL) is the ceiling, and real speed at load is lower. For SteadyWin, "Max Speed after reduce" is used as NL. For LK, "Max Speed (空载转速)" is used. For MyActuator V2/V3, the NL comes from the "(No_Load)" row of the official test table.
- Torque classes (by peak torque): small 3–15, medium 15–40, large 40–90, >90 = above the large class.
- "n/p" = not published; "n/s" = not stated.

**Abbreviations.** NL = no-load speed; rms = phase current RMS; w/ drv = with driver board; GDS/GDZ/GDM/GDK = SteadyWin driver boards; DG = LK driver.


### 1. Master table (57 models)

| Brand | Model | Dia mm | Len mm | Mass g | Ratio | Reducer | Rated N·m | Peak N·m | Rated rpm | No-load rpm | V | Rated A | Peak A | Encoder (type/res, single/dual, abs output?) | Interface | Driver built-in | Backdrivability | Official price (USD/CNY, date) | India leads | N·m/kg (peak) | USD/peak N·m | Label(s) | Output speed vs 8–20 rad/s (E) | Torque-class fit (E) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CubeMars | AK40-10 V3.0 KV170 | 53 | 40.2 | 190 | 10:1 | planetary (stage count n/s; 1-stage E) | 1.3 | 4.1 | 370 | 435 | 24 | 2.7 | 7.3 | Dual MT6835 16-bit (in+out); 1-turn abs kept at power-off | CAN (1 Mbps per AK V3 manual) + UART | Yes (std package) | 0.06 N·m back-drive (V) → very high (E) | $135.90 incl. driver (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 21.6 (E: 4.1/0.19) | 33.15 (E: 135.90/4.1) | V; E derived | NL 45.6 rad/s; rated 38.7 rad/s → ≥20: full range | small (3–15) |
| CubeMars | AK45-10 V3.0 KV75 | 53 | 45.2 | 262 | 10:1 | planetary (stage n/s; 1-stage E) | 2.5 | 7 | 120 | 180 | 24 | 1.9 | 5 | Dual MT6835 16-bit (in+out); 1-turn abs kept | CAN + UART | Yes (std package) | 0.1 N·m (V) → very high (E) | $155.90 incl. driver (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 26.7 (E: 7/0.262) | 22.27 (E: 155.90/7) | V; E derived | NL 18.8 rad/s; rated 12.6 rad/s → 8–20: partial | small (3–15) |
| CubeMars | AK45-36 V3.0 KV80 | 55 | 56.5 | 349 | 36:1 | planetary (stage n/s; ≥2-stage E) | 8 | 24 | 40 | 52 | 24 | 2 | 6.5 | Dual MT6835 16-bit (in+out); 1-turn abs kept | CAN + UART | Yes (std package) | 0.8 N·m (V) → moderate (E) | $185.90 incl. driver (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 68.8 (E: 24/0.349) | 7.75 (E: 185.90/24) | V; E derived | NL 5.4 rad/s; rated 4.2 rad/s → <8: too slow | medium (15–40) |
| CubeMars | AK60-6 V3.0 KV80 | 79 | 43 | 380 | 6:1 | planetary 6:1 (1-stage E) | 3 | 9 | 233/490 | 320/640 | 24/48 | 3.8 | 10.3/11.2 | Single, magnetic 21-bit (motor side) | CAN 1 Mbps (manual) + UART | Yes (NO-driver option exists) | 0.2 N·m (V) → high (E) | $298.90 w/ driver; $229.90 w/o (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 23.7 (E: 9/0.38) | 33.21 (E: 298.90/9) | V; E derived | NL 33.5/67.0 rad/s; rated 24.4/51.3 rad/s → ≥20: full range | small (3–15) |
| CubeMars | AK60-39 V3.0 KV80 | 79 | 67 | 750 | 39:1 | two-stage planetary (V) | 24 | 72 | 70 | 98 | 48 | 4.5 | 17 | Dual MT6835 21-bit (in+out); 1-turn abs | CAN + UART | Yes | 1.4 N·m (V) → low-moderate (E) | $448.90 (single SKU, incl. driver) (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 96.0 (E: 72/0.75) | 6.23 (E: 448.90/72) | V; E derived | NL 10.3 rad/s; rated 7.3 rad/s → 8–20: partial | large (40–90) |
| CubeMars | AK70-9 V3.0 KV60 | 89 | 49 | 540 | 9:1 | planetary 9:1 (1-stage E) | 8.5 | 29.2 | 260 | 320 | 48 | 6.25 | 23.8 | Dual magnetic 21-bit (in+out) | CAN + UART | Yes (NO-driver option exists) | 0.8 N·m (V) → moderate-high (E) | $498.90 w/ driver; $398.90 w/o (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 54.1 (E: 29.2/0.54) | 17.09 (E: 498.90/29.2) | V; E derived | NL 33.5 rad/s; rated 27.2 rad/s → ≥20: full range | medium (15–40) |
| CubeMars | AK70-10 KV100 | 89 | 50.25 | 621 | 10:1 | planetary 10:1 (1-stage E) | 8.3 | 24.8 | 148/310 | 240/480 | 24/48 | 7.2 | 23.2 | Single magnetic 14-bit (motor) | CAN 1 Mbps (V2 manual) + UART | Yes (NO-driver option) | 0.48 N·m (V) → high (E) | $498.90 w/ driver; $398.90 w/o (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 39.9 (E: 24.8/0.621) | 20.12 (E: 498.90/24.8) | V; E derived | NL 25.1/50.3 rad/s; rated 15.5/32.5 rad/s → ≥20: full range | medium (15–40) |
| CubeMars | AK80-6 KV100 | 98 | 38.5 | 485 | 6:1 | planetary 6:1 (1-stage E) | 6 | 12 | 603 | 800 | 48 | 9.7 | 20 | Single magnetic 14-bit (motor) | CAN 1 Mbps (V2 manual) + UART | Yes (NO-driver option) | 0.36 N·m (V) → high (E) | $569.90 w/ driver; $469.90 w/o (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 24.7 (E: 12/0.485) | 47.49 (E: 569.90/12) | V; E derived | NL 83.8 rad/s; rated 63.1 rad/s → ≥20: full range | small (3–15) |
| CubeMars | AK80-8 KV60 | 98 | 43.9 | 570 | 8:1 | planetary 8:1 (1-stage E) | 10 | 25 | 243 | 360 | 48 | 6.9 | 21 | Dual: 14-bit inner + 15-bit outer (magnetic) | CAN 1 Mbps (V2 manual) + UART | Yes (NO-driver option) | 0.75 N·m (V) → moderate-high (E) | $569.90 w/ driver; $469.90 w/o (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 43.9 (E: 25/0.57) | 22.80 (E: 569.90/25) | V; E derived | NL 37.7 rad/s; rated 25.4 rad/s → ≥20: full range | medium (15–40) |
| CubeMars | AK80-9 V3.0 KV100 | 98 | 38.5 | 490 | 9:1 | planetary 9:1 (1-stage E) | 9 | 22 | 390 | 570 | 48 | 12 | 28 | Single magnetic 16-bit (motor) | CAN 1 Mbps (manual) + UART | Yes (NO-driver option) | 0.51 N·m (V) → high (E) | $579.90 w/ driver; $479.90 w/o (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 44.9 (E: 22/0.49) | 26.36 (E: 579.90/22) | V; E derived | NL 59.7 rad/s; rated 40.8 rad/s → ≥20: full range | medium (15–40) |
| CubeMars | AK80-64 KV80 | 98 | 61.9 | 850 | 64:1 | planetary (stage n/s; ≥2-stage E) | 48 | 120 | 23/48 | 37/75 | 24/48 | 7 | 19 | Single magnetic 14-bit (motor) | CAN 1 Mbps (V2 manual) + UART | Yes (NO-driver option) | 4.7 N·m (V) → low (E) | $989.90 w/ driver; $889.90 w/o (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 141.2 (E: 120/0.85) | 8.25 (E: 989.90/120) | V; E derived | NL 3.9/7.9 rad/s; rated 2.4/5.0 rad/s → <8: too slow | >90: above large (oversized) |
| CubeMars | AK10-9 V3.0 KV60 | 98 | 61.7 | 940 | 9:1 | planetary 9:1 (1-stage E) | 18 | 53 | 235 | 320 | 48 | 10.7 | 31.9 | Dual: 21-bit inner + 15-bit outer (magnetic) | CAN 1 Mbps (manual) + UART | Yes (NO-driver option) | n/p for V3 (V2.0 page: 0.8 N·m) → moderate-high (E) | $798.90 w/ driver; $698.90 w/o (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 56.4 (E: 53/0.94) | 15.07 (E: 798.90/53) | V; E derived; bd U(V2 value) | NL 33.5 rad/s; rated 24.6 rad/s → ≥20: full range | large (40–90) |
| CubeMars | AKA60-6 KV80 | 80 | 51.2 | 460 | 6:1 | planetary 6:1 (1-stage E); high radial load | 3 | 9 | 200/400 | 320/640 | 24/48 | 4 | 11.2 | Single (comparison table); res. n/p | CAN + UART (2+5-pin plug) | Yes (comparison table) | n/p → high (E, 6:1) | $298.90 (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 19.6 (E: 9/0.46) | 33.21 (E: 298.90/9) | V; E derived+bd | NL 33.5/67.0 rad/s; rated 20.9/41.9 rad/s → ≥20: full range | small (3–15) |
| CubeMars | AKA10-9 KV60 | 100 | 70 | 1060 | 9:1 | planetary 9:1 (1-stage E); high radial load | 18 | 53 | 109 | 280 (table) / 320 (core data) | 48 | 10.6 | 32 | Outer-ring magnetic 16-bit listed (comparison says Single) — conflict | CAN (isolated) + UART | Yes | 0.8 N·m (V) → moderate-high (E) | $798.90 (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 50.0 (E: 53/1.06) | 15.07 (E: 798.90/53) | V (conflicts noted); E derived | NL 29.3/33.5 rad/s; rated 11.4 rad/s → ≥20: full range | large (40–90) |
| CubeMars | AKE60-8 KV80 | 69 | 25 | 260 (no driver) | 8:1 | planetary QDD 8:1 | 5 | 12.5 | 180 | 240 | 24 | 4.8 | 12 | None listed (driver board sold separately) | via separate AK driver board (CAN) | NO (board $79.90 extra) | n/p → high (E, 8:1 QDD; backlash 9′ V) | $218.90 motor only; +$79.90 board (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 48.1 (E: 12.5/0.26) motor-only mass | 23.90 (E: 298.80/12.5) | V; E derived (price = motor+board sum) | NL 25.1 rad/s; rated 18.8 rad/s → ≥20: full range | small (3–15) |
| CubeMars | AKE80-8 KV30 | 87 | 32 | 570 (no driver) | 8:1 | planetary QDD 8:1 | 12 | 30 | 150 | 195 | 48 | 4.8 | 12 | None listed (separate board) | via separate driver board (CAN) | NO (board $129.90 extra) | n/p → high (E, 8:1 QDD) | $339.90 motor only; +$129.90 board (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 52.6 (E: 30/0.57) motor-only mass | 15.66 (E: 469.80/30) | V; E derived (motor+board) | NL 20.4 rad/s; rated 15.7 rad/s → ≥20: full range | medium (15–40) |
| CubeMars | AKE90-8 KV35 | 107.5 | 43.5 | 1400 (no driver) | 8:1 | planetary 8:1 ("5-stage gear structure" per page) | 55 | 170 | 120 | 210 | 48 | 21 | 72 | None listed (separate board) | via separate AK80-4830 driver (CAN 1 Mbps, manual) | NO (board $159.90 extra) | n/p → high-moderate (E, 8:1) | $483.90 motor only; +$159.90 board (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 121.4 (E: 170/1.4) motor-only mass | 3.79 (E: 643.80/170) | V; E derived (motor+board) | NL 22.0 rad/s; rated 12.6 rad/s → ≥20: full range | >90: above large (oversized) |
| CubeMars | AKH70-16 V1.0 KV41 | 90 | 60.5 | 879 | 16:1 | two-stage planetary (V); 7 mm hollow bore | 26 | 78 | 90 | 105 | 48 | 6.5 | 19.5 | Dual 21-bit magnetic (motor + output) | Dual CAN (daisy-chain) + UART | Yes (onboard) | 0.78 N·m (V) → moderate (E) | $598.90 cubemars.com / $598.00 store (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 88.7 (E: 78/0.879) | 7.68 (E: 598.90/78) | V; E derived | NL 11.0 rad/s; rated 9.4 rad/s → 8–20: partial | large (40–90) |
| CubeMars | AKH70-48 V1.0 KV41 | 90 | 81.5 | 1396 | 48:1 | three-stage planetary (V); 7 mm hollow | 74 | 222 | 28 | 35 | 48 | 6 | 18 (page) / 21 (comparison) | Dual 21-bit magnetic (motor + output) | Dual CAN + UART | Yes (onboard) | 2.22 N·m (V) → low (E) | $698.90 cubemars.com / $698.00 store (2026-09-24) | Robokits: CubeMars R60 frameless only (no AK) (U); ThinkRobotics: none; Robu: not checked | 159.0 (E: 222/1.396) | 3.15 (E: 698.90/222) | V (peak-A conflict); E derived | NL 3.7 rad/s; rated 2.9 rad/s → <8: too slow | >90: above large (oversized) |
| MyActuator | RMD-X2-7 (X2-P28-7-E) V4 | 44 | 63.5 | 260 | 28.17 | planetary (stages n/s; ≥2-stage E) | 2.5 | 7 | 142 | 178 | 24 (20–55) | 3 | 8.1 | Dual abs: ABS-17BIT in / 18BIT out | EtherCAT & CAN BUS | Yes | 0.4 N·m (V) → high-moderate (E) | No official price; AIFITLAB $345 (U, 2026-09-24) | Amazon.in: legacy RMD-X8 S2/H V3 listings (U); MyActuator USA LLC (V) | 26.9 (E: 7/0.26) | 49.29 (E: 345.00/7) [U price] | V specs; U price; E derived | NL 18.6 rad/s; rated 14.9 rad/s → 8–20: partial | small (3–15) |
| MyActuator | RMD-X4-10 (X4-P12.5-10-C/E) V4 | 55 | 55.5 | 330 | 12.5 | planetary (stages n/s) | 4 | 10 | 238 | 317 | 24 (20–55) | 7.8 rms | 19.5 rms | Dual abs: ABS-17BIT in / 18BIT out | EtherCAT & CAN BUS (-C = CAN, -E = EtherCAT) | Yes | 0.8 N·m (V) → moderate (E) | No official price; AIFITLAB $345 (U) | Amazon.in: legacy RMD-X8 S2/H V3 listings (U); MyActuator USA LLC (V) | 30.3 (E: 10/0.33) | 34.50 (E: 345.00/10) [U price] | V specs; U price; E derived | NL 33.2 rad/s; rated 24.9 rad/s → ≥20: full range | small (3–15) |
| MyActuator | RMD-X4-36 (X4-P36-36-C/E) V4 | 55 | 61 | 360 | 36 | planetary (stages n/s; ≥2-stage E) | 10.5 | 34 | 83 | 111 | 24 (20–55) | 6.1 rms | 21.5 rms | Dual abs: ABS-17BIT in / 18BIT out | EtherCAT & CAN BUS | Yes | 1.14 N·m (V) → low-moderate (E) | No official price; AIFITLAB $400 (U) | Amazon.in: legacy RMD-X8 S2/H V3 listings (U); MyActuator USA LLC (V) | 94.4 (E: 34/0.36) | 11.76 (E: 400.00/34) [U price] | V specs; U price; E derived | NL 11.6 rad/s; rated 8.7 rad/s → 8–20: partial | medium (15–40) |
| MyActuator | RMD-X4-36-L (X4-P36-36-E-L) V4.1 | 55 | 61 | 360 | 36 | planetary (stages n/s; ≥2-stage E); XRBT305 bearing | 10.5 | 30 (stall 36) | 83 | 111 | 24 (20–55) | 6.1 rms | 21.2 rms (stall) | Dual ABS 17BIT/18BIT | EtherCAT / CAN BUS | Yes | 0.2 N·m (V) → high (E) | No price found | Amazon.in: legacy RMD-X8 S2/H V3 listings (U); MyActuator USA LLC (V) | 83.3 (E: 30/0.36) | n/a (no price) | V specs; E derived | NL 11.6 rad/s; rated 8.7 rad/s → 8–20: partial | medium (15–40) |
| MyActuator | RMD-X6-60 (X6-P20-60-C/E) V4 | 80 | 67.5 | 820 | 19.612 | planetary (stages n/s) | 20 | 60 | 153 | 176 | 48 (20–55) | 9.5 rms | 29.1 rms | Dual abs: ABS-17BIT in / 17BIT out | EtherCAT & CAN BUS | Yes | 1.6 N·m (V) → low-moderate (E) | No official price; AIFITLAB $490 (U) | Amazon.in: legacy RMD-X8 S2/H V3 listings (U); MyActuator USA LLC (V) | 73.2 (E: 60/0.82) | 8.17 (E: 490.00/60) [U price] | V specs; U price; E derived | NL 18.4 rad/s; rated 16.0 rad/s → 8–20: partial | large (40–90) |
| MyActuator | RMD-X8-32 (X8-P9-32-R) V4 | 96 | 41.2 | 530 | 9 | planetary 9 (1-stage E) | 8 | 32 | 244 | 277 | 24 | 6.2 rms | 30 rms | Single ABS-18BIT | RS485 only (no CAN) | Yes | 0.8 N·m (V) → moderate-high (E) | No official price; AIFITLAB $645 (U) | Amazon.in: legacy RMD-X8 S2/H V3 listings (U); MyActuator USA LLC (V) | 60.4 (E: 32/0.53) | 20.16 (E: 645.00/32) [U price] | V specs; U price; E derived | NL 29.0 rad/s; rated 25.6 rad/s → ≥20: full range | medium (15–40) |
| MyActuator | RMD-X8-120 (X8-P20-120-C/E) V4 | 96 | 76 | 1400 | 19.61 | planetary (stages n/s); crossed-roller output | 43 | 120 | 127 | 158 | 48 (20–55) | 17.6 rms | 43.8 rms | Dual abs: ABS-17BIT in / 17BIT out | CAN BUS / EtherCAT | Yes | 1.5 N·m (V) → low-moderate (E) | No official price; AIFITLAB $645 (U) | Amazon.in: legacy RMD-X8 S2/H V3 listings (U); MyActuator USA LLC (V) | 85.7 (E: 120/1.4) | 5.38 (E: 645.00/120) [U price] | V specs; U price; E derived | NL 16.5 rad/s; rated 13.3 rad/s → 8–20: partial | >90: above large (oversized) |
| MyActuator | RMD-X8-150 (X8-P20-150-E) V4.1 | 96 | 71 | 1330 | 19.612 | planetary (stages n/s); 12.6 mm hollow; CRBT655 | 43 | 120 (stall 150) | 127 | 158 | 48 (20–55) | 17.6 rms | 67.18 rms (stall) | Dual ABS-17BIT / ABS-19BIT | EtherCAT / CAN BUS | Yes | 0.34 N·m (V) → high (E) | No price found | Amazon.in: legacy RMD-X8 S2/H V3 listings (U); MyActuator USA LLC (V) | 90.2 (E: 120/1.33) | n/a (no price) | V specs; E derived | NL 16.5 rad/s; rated 13.3 rad/s → 8–20: partial | >90: above large (oversized) |
| MyActuator | RMD-X10-200 (X10-P20-200-E) V4.1 | 124 | 63.5 | 1640 | 20 | planetary (stages n/s); 12 mm hollow; CRBT805 | 60 | 170 (stall 200) | 74 | 80 | 48 (20–55) | 12.7 rms | 56.6 rms (stall) | Dual ABS-17BIT / ABS-19BIT | EtherCAT / CAN BUS | Yes | 1 N·m (V) → moderate (E) | No official price; AIFITLAB $800 (U) | Amazon.in: legacy RMD-X8 S2/H V3 listings (U); MyActuator USA LLC (V) | 103.7 (E: 170/1.64) | 4.71 (E: 800.00/170) [U price] | V specs; U price; E derived | NL 8.4 rad/s; rated 7.7 rad/s → 8–20: partial | >90: above large (oversized) |
| MyActuator | RMD-X12-320 (X12-P20-320-E) V4 | 124 | 85 | 2370 | 20 | planetary (stages n/s); crossed-roller | 85 | 320 | 100 | 125 | 48 (range 20–70; note says 55 max) | 30 rms | 100 rms | Dual abs: ABS-17BIT in / 17BIT out | EtherCAT & CAN BUS | Yes | 3.8 N·m (V) → low (E) | No official price; AIFITLAB $1090 (U) | Amazon.in: legacy RMD-X8 S2/H V3 listings (U); MyActuator USA LLC (V) | 135.0 (E: 320/2.37) | 3.41 (E: 1090.00/320) [U price] | V specs (V-range conflict); U price; E derived | NL 13.1 rad/s; rated 10.5 rad/s → 8–20: partial | >90: above large (oversized) |
| MyActuator | RMD-X15-450 (X15-P20-450-E) V4 | 166 | 69 (+18 boss) | 3500 | 20.25 | planetary (stages n/s); crossed-roller | 145 | 450 | 98 | 108 | 72 (20–80) | 25 rms | 69.2 rms | Dual abs: ABS-17BIT in / 17BIT out | EtherCAT & CAN BUS | Yes | 4 N·m (V) → low (E) | No official price; AIFITLAB $1515 (U) | Amazon.in: legacy RMD-X8 S2/H V3 listings (U); MyActuator USA LLC (V) | 128.6 (E: 450/3.5) | 3.37 (E: 1515.00/450) [U price] | V specs; U price; E derived | NL 11.3 rad/s; rated 10.3 rad/s → 8–20: partial | >90: above large (oversized) |
| MyActuator | RMD-X6-7 (X6-P6-7-C-N) V2 | 76 | 38 | 350 | 6 | planetary 6 (1-stage E) | 3.5 | 7 | 400 | 670 (test @48.13 V) | 48 | 4 | 9 | Single 18-bit | CAN 1M / RS485 (115.2k–2.5M) | Yes (CAN/RS485 versions; "without driver" SKU exists) | anti-force 0.08 N·m (V) → very high (E) | No official price; AIFITLAB $250 CAN (U) | Amazon.in: legacy RMD-X8 S2/H V3 listings (U); MyActuator USA LLC (V) | 20.0 (E: 7/0.35) | 35.71 (E: 250.00/7) [U price] | V specs; U price; E derived | NL 70.2 rad/s; rated 41.9 rad/s → ≥20: full range | small (3–15) |
| MyActuator | RMD-X6-8 (X6-P8-8-C-N) V3 | 79 | 44.5 | 490 | 8 | planetary 8 (1-stage E) | 4.5 | 8 | 310 | 368 (test @48.05 V) | 48 | 3.6 | 7.2 | Dual 14/14-bit | CAN 1M / RS485 | Yes (CAN/RS485 SKUs) | anti-force 0.1 N·m (V) → very high (E) | No official price; AIFITLAB $375 CAN (U; "discontinue soon") | Amazon.in: legacy RMD-X8 S2/H V3 listings (U); MyActuator USA LLC (V) | 16.3 (E: 8/0.49) | 46.88 (E: 375.00/8) [U price] | V specs; U price; E derived | NL 38.5 rad/s; rated 32.5 rad/s → ≥20: full range | small (3–15) |
| MyActuator | RMD-X6-40 (X6-P36-40-C-N) V2 | 76 | 60.5 | 590 | 36 | planetary (≥2-stage E) | 18 | 40 | 90 | 109.9 (test @48.02 V) | 48 | 5.2 | 10.5 | Single 18-bit | CAN 1M / RS485 | Yes (CAN/RS485 SKUs) | anti-force 0.91 N·m (V) → moderate (E) | No official price; AIFITLAB $655 CAN (U) | Amazon.in: legacy RMD-X8 S2/H V3 listings (U); MyActuator USA LLC (V) | 67.8 (E: 40/0.59) | 16.38 (E: 655.00/40) [U price] | V specs; U price; E derived | NL 11.5 rad/s; rated 9.4 rad/s → 8–20: partial | large (40–90) |
| MyActuator | RMD-X8-25 (X8-P9-25-C-N) V2 (ex "X8-Pro 1:9") | 98 | 51 | 710 | 9 | planetary 9 (1-stage E) | 10 | 25 | 110 | 254.3 (test @48.14 V) | 48 | 3.2 | 8 | Single 18-bit | CAN 1M / RS485 | Yes (CAN/RS485 SKUs) | anti-force 0.61 N·m (V) → high (E) | No official price; AIFITLAB $470 CAN (U) | Amazon.in: legacy RMD-X8 S2/H V3 listings (U); MyActuator USA LLC (V) | 35.2 (E: 25/0.71) | 18.80 (E: 470.00/25) [U price] | V specs; U price; E derived | NL 26.6 rad/s; rated 11.5 rad/s → ≥20: full range | medium (15–40) |
| MyActuator | RMD-X10-40 (X10-P7-40-C-N) V3 | 122 | 53 | 1150 | 7 | planetary 7 (1-stage E) | 15 | 40 | 165 | 186.4 (test @48.09 V) | 48 | 6.5 | 15 | Dual 14/14-bit | CAN 1M / RS485 | Yes (CAN/RS485 SKUs) | anti-force 0.62 N·m (V) → high (E) | No official price; AIFITLAB $645 CAN (U) | Amazon.in: legacy RMD-X8 S2/H V3 listings (U); MyActuator USA LLC (V) | 34.8 (E: 40/1.15) | 16.12 (E: 645.00/40) [U price] | V specs; U price; E derived | NL 19.5 rad/s; rated 17.3 rad/s → 8–20: partial | large (40–90) |
| MyActuator | RMD-X10-100 (X10-P35-100-C-N) V3 | 122 | 74 | 1700 | 35 | planetary (≥2-stage E) | 50 | 100 | 50 | 53.6 (test @47.99 V) | 48 | 6.7 | 13.5 | Dual 14/14-bit | CAN 1M / RS485 | Yes | anti-force 2.88 N·m (V) → low (E) | No price found | Amazon.in: legacy RMD-X8 S2/H V3 listings (U); MyActuator USA LLC (V) | 58.8 (E: 100/1.7) | n/a (no price) | V specs; E derived | NL 5.6 rad/s; rated 5.2 rad/s → <8: too slow | >90: above large (oversized) |
| SteadyWin | GIM4310-10 (GDS34 spec) | 53 | 38 w/ drv (32 w/o) | 227 w/ drv (217 w/o) | 10:1 | planetary, steel gears (1-stage E) | 2.05 | 5.60 | 150 | 228 (max) | 24 (12–48) | 2.3 | 6.80 | Driver encoder 14-bit; 2nd (output) encoder NOT supported | CAN (GDS34) | Optional (sold w/ or w/o board) | n/p → high (E, 10:1) | $151.80 w/ GDS34 (sold out); $126.90 w/ GDK34; $82 motor only (2026-09-24) | Official store ships to India ("Shipping Cost-India" line) (V) | 24.7 (E: 5.6/0.227) | 27.11 (E: 151.80/5.6); 22.66 w/ GDK (E: 126.90/5.6) | V; E derived+bd | NL 23.9 rad/s; rated 15.7 rad/s → ≥20: full range | small (3–15) |
| SteadyWin | GIM4315-8 (GDZ468 spec) | 57.5 | 52 w/ drv (51 w/o) | 369.3 w/ drv (342.7 w/o) | 8:1 | planetary, steel (1-stage E) | 3.06 | 10.18 | 152 | 199 (max) | 24 (12–40) | 2.7 | 10.70 | 14-bit on driver; optional 2nd output encoder (1-turn memory) | CAN (GDZ: CAN/485/Modbus) | Optional | n/p → high (E, 8:1) | $135.80 w/ GDZ468 (sold out); $117.20 w/ GDK468; $69.80 motor only | Official store ships to India ("Shipping Cost-India" line) (V) | 27.6 (E: 10.18/0.3693) | 13.34 (E: 135.80/10.18); 11.51 w/ GDK (E: 117.20/10.18) | V; E derived+bd | NL 20.8 rad/s; rated 15.9 rad/s → ≥20: full range | small (3–15) |
| SteadyWin | GIM4310-36 (GDS34 spec) | 55 | 47 w/ drv (40 w/o) | 310 w/ drv (300 w/o) | 36:1 | planetary, steel (≥2-stage E) | 7.38 | 20.16 | 41 | 63 (max) | 24 (12–48) | 2.3 | 6.80 | 14-bit on driver; 2nd encoder NOT supported | CAN (GDS34) | Optional | n/p → low (E, 36:1) | $169.80 w/ GDS34 (sold out); $146.10 w/ GDK34; $100 motor only | Official store ships to India ("Shipping Cost-India" line) (V) | 65.0 (E: 20.16/0.31) | 8.42 (E: 169.80/20.16); 7.25 w/ GDK (E: 146.10/20.16) | V; E derived+bd | NL 6.6 rad/s; rated 4.3 rad/s → <8: too slow | medium (15–40) |
| SteadyWin | GIM6010-8 (24 V GDS68 / 48 V GDZ468H) | 80 | 40 w/ drv (29.5 w/o) | 388 w/ drv (370 w/o) | 8:1 | planetary, steel (1-stage E) | 5.00 / 4.20 | 11.00 / 11.27 | 120 / 220 | 420 / 554 (max) | 24 (12–56) / 48 (12–48) | 10.50 / 2.87 | 23.40 / 20.02 | 16-bit on driver; optional 2nd output encoder | CAN (GDS68) / CAN & 485 (GDZ468H) | Optional | n/p → high (E, 8:1) | $93.88 w/ GDS68; $112.20 w/ GDK468; $70.35 motor only | Official store ships to India ("Shipping Cost-India" line) (V) | 28.4 (E: 11/0.388) | 8.53 (E: 93.88/11) | V; E derived+bd | NL 44.0/58.0 rad/s; rated 12.6/23.0 rad/s → ≥20: full range | small (3–15) |
| SteadyWin | GIM8108-8 (GDS68 spec) | 92 | 55 w/ drv (44 w/o) | 396 w/ drv (378 w/o) | 8:1 | planetary, steel (1-stage E) | 7.50 | 22.00 | 110 | 320 (max) | 48 (12–56) | 7 | 22.00 | 16-bit on driver; optional 2nd output encoder | CAN & Type-C (GDS68) | Optional | n/p → high (E, 8:1) | $129.20 w/ GDS68; $93.89 motor only | Official store ships to India ("Shipping Cost-India" line) (V) | 55.6 (E: 22/0.396) | 5.87 (E: 129.20/22) | V; E derived+bd | NL 33.5 rad/s; rated 11.5 rad/s → ≥20: full range | medium (15–40) |
| SteadyWin | GIM8108-9 (48 V GDS810 / 24 V GDM810) | 96 | 41.5 w/ drv (34 w/o) | 567 w/ drv (525 w/o) | 9:1 | planetary, steel (1-stage E) | 8.19 / 8.78 | 27.38 / 25.73 | 207 / 195 | 242 / 227 (max) | 48 / 24 (12–48) | 4 / 9.2 | 19.80 / 34.10 | 14-bit on driver; optional 2nd output encoder | CAN & 485 (GDS810 per table) / CAN MIT (GDM810) | Optional | n/p → high (E, 9:1) | $189.60 w/ GDS810/GDM810; $119.80 motor only | Official store ships to India ("Shipping Cost-India" line) (V) | 48.3 (E: 27.38/0.567) | 6.92 (E: 189.60/27.38) | V; E derived+bd | NL 25.3/23.8 rad/s; rated 21.7/20.4 rad/s → ≥20: full range | medium (15–40) |
| SteadyWin | GIM8115-9 (GDS810 24/48 V; GDM810) | 96 | 48.5 w/ drv (41 w/o) | 705 w/ drv (660 w/o) | 9:1 | planetary, steel (1-stage E) | 13.00/13.80 (GDS) 12.90/13.50 (GDM) | 40/46 (GDS) 45/39 (GDM) | 100/118 (GDS) | 129/146 (GDS) 143/160 (GDM) | 24/48 (12–48) | 7.9 / 4.6 (GDS) | 24.69 / 16.55 (GDS) | 14-bit on driver; optional 2nd output encoder | CAN & 485 (GDS810 table) / CAN (GDM810) | Optional | n/p → high (E, 9:1) | $213.80 w/ GDS810/GDM810; $144 motor only | Official store ships to India ("Shipping Cost-India" line) (V) | 65.2 (E: 46/0.705) | 4.65 (E: 213.80/46) | V; E derived+bd | NL 13.5/15.3/15.0/16.8 rad/s; rated 10.5/12.4 rad/s → 8–20: partial | large (40–90) |
| SteadyWin | GIM6010-36 (48 V GDS6 / 24 V GDM6) | 76 | 56.5 w/ drv (45.5 w/o) | 574 w/ drv (546 w/o) | 36:1 | two-stage planetary (V, title), steel | 18 / 18 | 41 / 45 | 85 / 50 | 97 / 90 (max) | 48 (12–48) / 24 (12–36) | 4.6 / 4 | 9.30 / 66.18 (as printed) | 14-bit on driver; optional 2nd output encoder | CAN & 485 (GDS6) / CAN (GDM6) | Optional | n/p → low (E, 36:1) | $221.80 w/ GDS6; $207.80 w/ GDZ468 (no spec); $152 motor only | Official store ships to India ("Shipping Cost-India" line) (V) | 71.4 (E: 41/0.574) | 5.41 (E: 221.80/41) | V (odd peak-A); E derived+bd | NL 10.2/9.4 rad/s; rated 8.9/5.2 rad/s → 8–20: partial | large (40–90) |
| SteadyWin | GIM6010-48 (24 V GDS68 / 24 V GDZ468) | 80 | 67.5 w/ drv (56.5 w/o) | 776.9 w/ drv (758.9 w/o) | 48:1 | two-stage planetary (V, title), steel | 30 / 27 | 66.00 / 55.90 | 20 / 38 | 70 / 49 (max) | 24 (12–56) / 24 (12–36) | 10.5 / 6.5 | 23.40 / 13.50 | 16-bit (GDS68) / 14-bit (GDZ468); optional 2nd output encoder | CAN & Type-C | Optional | n/p → low (E, 48:1) | $170.00 w/ GDS68; $136 motor only | Official store ships to India ("Shipping Cost-India" line) (V) | 85.0 (E: 66/0.7769) | 2.58 (E: 170.00/66) | V; E derived+bd | NL 7.3/5.1 rad/s; rated 2.1/4.0 rad/s → <8: too slow | large (40–90) |
| SteadyWin | GIM8108-36 (48 V GDS810 / 24 V GDM810) | 96 | 57 w/ drv (44.5 w/o) | 760 w/ drv (720 w/o) | 36:1 | planetary, steel (≥2-stage E) | 32.76 / 35.10 | 109.50 / 102.90 | 51 / 48 | 60 / 56 (max) | 48 / 24 (12–48) | 4 / 9.2 | 19.80 / 34.10 | 14-bit on driver; optional 2nd output encoder | CAN & 485 (GDS810) / CAN (GDM810) | Optional | n/p → low (E, 36:1) | $239.80 w/ GDS810/GDM810; $170 motor only | Official store ships to India ("Shipping Cost-India" line) (V) | 144.1 (E: 109.5/0.76) | 2.19 (E: 239.80/109.5) | V; E derived+bd | NL 6.3/5.9 rad/s; rated 5.3/5.0 rad/s → <8: too slow | >90: above large (oversized) |
| SteadyWin | GIM8108-48 (GDZ468 36 V spec) | 92 | 73 w/ drv (62 w/o) | 780.4 w/ drv (762.4 w/o) | 48:1 | planetary, steel (≥2-stage E) | 45.00 | 131.60 | 32 | 40 (max) | 36 (12–36) | 5.3 | 20.90 | 14-bit on driver; optional 2nd output encoder | CAN & Type-C (per table) | Optional | n/p → low (E, 48:1) | $214.80 w/ GDZ468; $193.00 w/ GDS68 (no spec); $159 motor only | Official store ships to India ("Shipping Cost-India" line) (V) | 168.6 (E: 131.6/0.7804) | 1.63 (E: 214.80/131.6) | V; E derived+bd | NL 4.2 rad/s; rated 3.4 rad/s → <8: too slow | >90: above large (oversized) |
| SteadyWin | GIM10015-9 (GDS810 24/48 V) | 122 w/ drv (120 w/o) | 57.5 w/ drv (45 w/o) | 1372 w/ drv (1325 w/o) | 9:1 | planetary, steel (1-stage E); crossed-roller bearing | 30.00 / 32.60 | 62.10 / 104.00 | 67 / 77.4 | 104 / 105 (max) | 24 / 48 (12–48) | 14.2 / 8.2 | 30.20 / 30.30 | 14-bit on driver; 2nd encoder: table YES vs page "not supported" (conflict) | CAN & 485 (GDS810) | Optional | n/p → high-moderate (E, 9:1) | $355.80 w/ GDS810/GDZ810; $286 motor only | Official store ships to India ("Shipping Cost-India" line) (V) | 75.8 (E: 104/1.372) | 3.42 (E: 355.80/104) | V (encoder conflict); E derived+bd | NL 10.9/11.0 rad/s; rated 7.0/8.1 rad/s → 8–20: partial | >90: above large (oversized) |
| LK-Tech | MG4010E-i10v3 | 53 | 41 | 250 | 1:10 (PG4210) | planetary (stage n/s; 1-stage E) | 2.5 | 4.5 | 260 | 320 | 24 (drive DG40: 7.4–32) | 3.5 | n/p | Dual: 18-bit motor + 14-bit reducer (output) magnetic | RS485 or CAN (CAN 1 Mbps; 100k–1M) | Yes (E = integrated; DG40) | n/p → high (E, 10:1; backlash ≤8′ V) | No official price; AIFITLAB $165 (U) | none found (U) | 18.0 (E: 4.5/0.25) | 36.67 (E: 165.00/4.5) [U price] | V specs; U price; E derived+bd | NL 33.5 rad/s; rated 27.2 rad/s → ≥20: full range | small (3–15) |
| LK-Tech | MG5010E-i10v3 | 63 | 41.5 | 420 | 1:10 (PG5110) | planetary (1-stage E) | 4 | 7 | 235 | 320 | 24 (DG50: 12–40) | 4.4 | n/p | Single 18-bit magnetic | RS485 or CAN (1 Mbps) | Yes (DG50) | n/p → high (E, 10:1) | No official price; AIFITLAB $165 (U) | none found (U) | 16.7 (E: 7/0.42) | 23.57 (E: 165.00/7) [U price] | V specs; U price; E derived+bd | NL 33.5 rad/s; rated 24.6 rad/s → ≥20: full range | small (3–15) |
| LK-Tech | MG6010E-i6v3 | 76 | 38.5 | 343 | 1:6 (PG4106) | planetary (1-stage E) | 5 / 5 | 10 / 10 | 170 / 391 | 251 / 505 | 24 / 48 (DG60Ev2: 12–60) | 5.5 / 5.3 | n/p | Dual: 18-bit motor + 14-bit reducer | RS485 or CAN (1 Mbps) | Yes (DG60Ev2) | n/p → very high (E, 6:1; backlash ≤6′) | No price found | none found (U) | 29.2 (E: 10/0.343) | n/a (no price) | V specs; E derived+bd | NL 26.3/52.9 rad/s; rated 17.8/40.9 rad/s → ≥20: full range | small (3–15) |
| LK-Tech | MG6012E-i8v3 | 80 | 44.5 | 430 | 1:8 (PG4108) | planetary (1-stage E) | 6 | 16 | 256 | 310 | 48 (DG60Ev2: 12–60) | 3.5 | n/p | Single 18-bit magnetic (dual-encoder SKU at reseller) | RS485 or CAN (1 Mbps) | Yes (DG60Ev2) | n/p → high (E, 8:1; ≤6′) | No official price; AIFITLAB $190 (V2 model, U) | none found (U) | 37.2 (E: 16/0.43) | 11.88 (E: 190.00/16) [U price] | V specs; U price (V2); E derived+bd | NL 32.5 rad/s; rated 26.8 rad/s → ≥20: full range | medium (15–40) |
| LK-Tech | MG6012-i36v3 | 80 | 51 | 503 | 1:36 (PG4136) | planetary (≥2-stage E) | 25 / 25 | 40 / 40 | 45 / 74 | 33 (as printed) / 88 | 24 / 48 (DG80v3: 12–60) | 4 / 4.8 | n/p | Single 18-bit magnetic | RS485 or CAN (1 Mbps) | Unclear (no "E"; rec. drive DG80v3) | n/p → low (E, 36:1) | No official price; AIFITLAB $410 (U) | none found (U) | 79.5 (E: 40/0.503) | 10.25 (E: 410.00/40) [U price] | V specs (speed typo?); U price; E derived+bd | NL 3.5/9.2 rad/s; rated 4.7/7.7 rad/s → 8–20: partial | large (40–90) |
| LK-Tech | MG8008E-i9v3 | 98 | 41 | 570 | 1:9 (PG5509) | planetary (1-stage E) | 9 / 10 | 20 / 20 | 78 / 178 | 112 / 220 | 24 / 48 (DG80Ev2: 12–60) | 4.6 / 4.9 | n/p | Dual: 18-bit motor + 14-bit reducer | RS485 or CAN (1 Mbps) | Yes (DG80Ev2) | n/p → high (E, 9:1; ≤6′) | No official price; AIFITLAB $260 (U) | none found (U) | 35.1 (E: 20/0.57) | 13.00 (E: 260.00/20) [U price] | V specs; U price; E derived+bd | NL 11.7/23.0 rad/s; rated 8.2/18.6 rad/s → ≥20: full range | medium (15–40) |
| LK-Tech | MG8016E-i6v3 | 99 | 50.5 | 759 | 1:6 (PG5506) | planetary (1-stage E) | 12 | 37 | 258 | 300 | 48 (DG80Ev2: 12–60) | 8.4 | n/p | Single 18-bit magnetic | RS485 or CAN (1 Mbps) | Yes (DG80Ev2) | n/p → very high (E, 6:1; ≤6′) | No official price; AIFITLAB $330 (V2 model, U) | none found (U) | 48.7 (E: 37/0.759) | 8.92 (E: 330.00/37) [U price] | V specs; U price (V2); E derived+bd | NL 31.4 rad/s; rated 27.0 rad/s → ≥20: full range | medium (15–40) |
| LK-Tech | MG8010-i36v2 | 99 | ≈53.5 (2+39+12.5, E) | 860 | 1:36 (PG5536) | planetary (≥2-stage E) | 35 | 45 | 68 | 80 | 48 (DG80v2: 12–60) | 6.9 | n/p | Single 18-bit magnetic | RS485 or CAN (1 Mbps) | Unclear (no "E"; rec. DG80v2) | n/p → low (E, 36:1) | No official price; AIFITLAB $460 (U) | none found (U) | 52.3 (E: 45/0.86) | 10.22 (E: 460.00/45) [U price] | V specs; U price; E derived+bd | NL 8.4 rad/s; rated 7.1 rad/s → 8–20: partial | large (40–90) |
| LK-Tech | MG10015E-i10 (v3) | 120 | 48.2 (51.2 w/ X-roller) | 1210 | 1:10 (PG7407) | planetary (1-stage E); optional crossed-roller | 25 | 45 | 150 | 185 | 48 (DG60Ev2: 12–60) | 11.5 | n/p | Dual: 18-bit motor + 14-bit reducer | RS485 or CAN (1 Mbps) | Yes (DG60Ev2) | n/p → high-moderate (E, 10:1; ≤8′) | No official price; AIFITLAB $370 (V2 model, U) | none found (U) | 37.2 (E: 45/1.21) | 8.22 (E: 370.00/45) [U price] | V specs; U price (V2); E derived+bd | NL 19.4 rad/s; rated 15.7 rad/s → 8–20: partial | large (40–90) |

### 1b. Derived rankings

**Cheapest USD per peak N·m (ESTIMATED; all prices incl. a driver unless noted)**

| # | Brand | Model | Value | Peak N·m | NL rad/s | Price basis |
|---|---|---|---|---|---|---|
| 1 | SteadyWin | GIM8108-48 (GDZ468 36 V spec) | 1.63 USD/N·m | 131.6 | 4.2 | official |
| 2 | SteadyWin | GIM8108-36 (48 V GDS810 / 24 V GDM810) | 2.19 USD/N·m | 109.5 | 6.3 | official |
| 3 | SteadyWin | GIM6010-48 (24 V GDS68 / 24 V GDZ468) | 2.58 USD/N·m | 66 | 7.3 | official |
| 4 | CubeMars | AKH70-48 V1.0 KV41 | 3.15 USD/N·m | 222 | 3.7 | official |
| 5 | MyActuator | RMD-X15-450 (X15-P20-450-E) V4 | 3.37 USD/N·m | 450 | 11.3 | reseller (U) |
| 6 | MyActuator | RMD-X12-320 (X12-P20-320-E) V4 | 3.41 USD/N·m | 320 | 13.1 | reseller (U) |
| 7 | SteadyWin | GIM10015-9 (GDS810 24/48 V) | 3.42 USD/N·m | 104 | 11.0 | official |
| 8 | CubeMars | AKE90-8 KV35 | 3.79 USD/N·m | 170 | 22.0 | official |
| 9 | SteadyWin | GIM8115-9 (GDS810 24/48 V; GDM810) | 4.65 USD/N·m | 46 | 16.8 | official |
| 10 | MyActuator | RMD-X10-200 (X10-P20-200-E) V4.1 | 4.71 USD/N·m | 170 | 8.4 | reseller (U) |

**Highest peak torque density N·m/kg (ESTIMATED)**

| # | Brand | Model | Value | Peak N·m | NL rad/s | Price basis |
|---|---|---|---|---|---|---|
| 1 | SteadyWin | GIM8108-48 (GDZ468 36 V spec) | 168.6 N·m/kg | 131.6 | 4.2 | official |
| 2 | CubeMars | AKH70-48 V1.0 KV41 | 159.0 N·m/kg | 222 | 3.7 | official |
| 3 | SteadyWin | GIM8108-36 (48 V GDS810 / 24 V GDM810) | 144.1 N·m/kg | 109.5 | 6.3 | official |
| 4 | CubeMars | AK80-64 KV80 | 141.2 N·m/kg | 120 | 7.9 | official |
| 5 | MyActuator | RMD-X12-320 (X12-P20-320-E) V4 | 135.0 N·m/kg | 320 | 13.1 | reseller (U) |
| 6 | MyActuator | RMD-X15-450 (X15-P20-450-E) V4 | 128.6 N·m/kg | 450 | 11.3 | reseller (U) |
| 7 | CubeMars | AKE90-8 KV35 | 121.4 N·m/kg | 170 | 22.0 | official |
| 8 | MyActuator | RMD-X10-200 (X10-P20-200-E) V4.1 | 103.7 N·m/kg | 170 | 8.4 | reseller (U) |
| 9 | CubeMars | AK60-39 V3.0 KV80 | 96.0 N·m/kg | 72 | 10.3 | official |
| 10 | MyActuator | RMD-X4-36 (X4-P36-36-C/E) V4 | 94.4 N·m/kg | 34 | 11.6 | reseller (U) |

**Cheapest USD/peak N·m among models with peak ≥15 N·m AND no-load ≥8 rad/s (ESTIMATED)**

| # | Brand | Model | Value | Peak N·m | NL rad/s | Price basis |
|---|---|---|---|---|---|---|
| 1 | MyActuator | RMD-X15-450 (X15-P20-450-E) V4 | 3.37 USD/N·m | 450 | 11.3 | reseller (U) |
| 2 | MyActuator | RMD-X12-320 (X12-P20-320-E) V4 | 3.41 USD/N·m | 320 | 13.1 | reseller (U) |
| 3 | SteadyWin | GIM10015-9 (GDS810 24/48 V) | 3.42 USD/N·m | 104 | 11.0 | official |
| 4 | CubeMars | AKE90-8 KV35 | 3.79 USD/N·m | 170 | 22.0 | official |
| 5 | SteadyWin | GIM8115-9 (GDS810 24/48 V; GDM810) | 4.65 USD/N·m | 46 | 16.8 | official |
| 6 | MyActuator | RMD-X10-200 (X10-P20-200-E) V4.1 | 4.71 USD/N·m | 170 | 8.4 | reseller (U) |
| 7 | MyActuator | RMD-X8-120 (X8-P20-120-C/E) V4 | 5.38 USD/N·m | 120 | 16.5 | reseller (U) |
| 8 | SteadyWin | GIM6010-36 (48 V GDS6 / 24 V GDM6) | 5.41 USD/N·m | 41 | 10.2 | official |
| 9 | SteadyWin | GIM8108-8 (GDS68 spec) | 5.87 USD/N·m | 22 | 33.5 | official |
| 10 | CubeMars | AK60-39 V3.0 KV80 | 6.23 USD/N·m | 72 | 10.3 | official |

### 2. Per-product notes — sources and verbatim snippets (≤15 words each)

Snippets are copied as they appear in the source. Some come from HTML tables. For image sources, the snippet is transcribed from the official spec image and tagged *img*. Every number in the master table traces to one of these snippets or to an E formula in the table.

#### 2.1 CubeMars (all specs VERIFIED unless marked)

**Common sources**
- AK series category page (lists AK/AKA/AKE/AKH): https://www.cubemars.com/categorys/ak-series-robotic-actuator
- Official price endpoint, used per SKU/attribute (JSON field `result`): `https://www.cubemars.com/goods.php?act=price&id=<id>&attr=<attr>&number=1`. The product page shows only the "NO driver" price, so this endpoint is needed.
- Official Shopify store JSON: https://store.cubemars.com/products.json?limit=250. It has 68 products, and every variant price matches the cubemars.com "with driver" price.
  - Exceptions: the AKH store prices are $598.00/$698.00 vs $598.90/$698.90 on cubemars.com.
- AK V3 product manual: https://www.cubemars.com/data/cms/202602/ak-series-prodcut-manual-v3-2-0-for-ak-3-0-robotic-actuator.pdf
  - "CAN bus bitrate 1Mbps"
  - "Allowable working voltage range 18-52V"
  - "Inner-loop encoder resolution … 21bit（singl-loop absolute value）"
  - "Optional 15-bit (single-loop absolute)" (outer loop, dual-encoder models)
  - Drivers AK54-4810 / AK60-4820 / AK80-4830 compatible with "AK60-6、AKE60-8", "AK70-9、AK80-9、AK10-9、AKE80-8", "AKE90-8"
  - "Maximum output current（AP） 30A 60A 90A"
- AK 2.0 driver manual v1.0.18: https://www.cubemars.com/data/cms/202605/ak-series-driver-manual-v1-0-18-for-ak-2-0-robotic-actuator.pdf
  - "CAN bus bit rate 1Mbps(No change recommended）"
  - "Allowable working voltage 18-52V" (AK-DRV-V2.1)
  - "Allowable working voltage 18-28V" (V2.2)
  - "Encoder precision 14bit（single turn absolute）"
- India (U): Robokits lists only a CubeMars frameless motor, "T-motor CubeMars R60 KV115 … Robot joint Motor". URL: https://robokits.co.in/automation-control-cnc/robot-joint-brushless-motors/t-motor-cubemars-r60-kv115-brushless-dc-outer-runner-robot-joint-motor
  - ThinkRobotics search (suggest.json, "cubemars") returned no actuator.
  - Robu.in search returned a Cloudflare challenge (403) and was not checked.

**AK40-10 V3.0 KV170** — https://www.cubemars.com/product/ak40-10-v3-0-kv170-robotic-actuator.html
- Size and mass: "Size mm φ53*40.2"; "Weight g 190"
- Ratio and reducer: "Reduction Ratio 10:1"; "features a 10:1 planetary gear reduction"
- Interface: "Communication Method CAN"
- Encoders:
  - "Inner Loop Encoder Type Magnetic Encoder MT6835"
  - "Inner Loop Encoder Resolution 16bit"; "Outer Loop Encoder Resolution 16bit"; "Number of Encoders 2"
  - "Single-turn absolute position is retained even after power loss"
- Torque: "Rated Torque N·m 1.3"; "Peak Torque N·m 4.1"
- Speed: "Rated Speed RPM 370"; "No-Load Speed RPM 435"
- Current: "Rated Current A 2.7"; "Peak Current A 7.3"
- Voltage: the page prints "Rated Power V 24" (sic); the comparison row gives "AK40-10 V3.0 KV170 | 24 |"
- Backdrive and backlash: "Backdrivable Torque N·m 0.06"; "Backlash arcmin 18"
- Driver: "standard package includes driver board"
- Price: price id 1225 → `"result":"$135.90"`; store "AK40-10 V3.0 KV170" "price":"135.90"
- Legacy V1 AK40-10 KV170: "Weight (g) 185", "Inner ring encoder resolution 14bit", "Number of encoder 1". Price NO $99.90 / YES $135.90. URL: https://www.cubemars.com/product/ak40-10-robotic-actuator.html

**AK45-10 V3.0 KV75** — https://www.cubemars.com/product/ak45-10-v3-0-kv75-robotic-actuator.html
- Size and mass: "Size mm φ53*45.2"; "Weight g 262"
- Ratio: "Reduction Ratio 10:1"
- Torque: "Rated Torque N·m 2.5"; "Peak Torque N·m 7"
- Speed: "Rated Speed RPM 120"; "No-Load Speed RPM 180"
- Current: "Rated Current A 1.9"; "Peak Current A 5"
- Backdrive and backlash: "Backdrivable Torque N·m 0.1"; "Backlash arcmin 18"
- Encoders: "Outer Loop Encoder Type Magnetic Encoder MT6835"; "Number of Encoders 2"
- Price: id 1226 → `"$155.90"` (store 155.90)
- Legacy AK45-10 KV75 (V1): "Weight (g) 260", "Inner ring encoder resolution 14bit", "Number of encoder 1". Price id 1198: YES `"$155.90"` / NO `"$119.90"`. URL: https://www.cubemars.com/product/AK45-10-robotic-actuatuor.html

**AK45-36 V3.0 KV80** — https://www.cubemars.com/product/ak45-36-v3-0-kv80-robotic-actuator.html
- Size and mass: "Size mm φ55*56.5"; "Weight g 349"
- Ratio and reducer: "Reduction Ratio 36:1"; "features a 36:1 planetary gear reduction". The stage count is not stated.
- Torque: "Rated Torque N·m 8"; "Peak Torque N·m 24"
- Speed: "Rated Speed RPM 40"; "No-Load Speed RPM 52"
- Current: "Rated Current A 2"; "Peak Current A 6.5"
- Backdrive and backlash: "Backdrivable Torque N·m 0.8"; "Backlash arcmin 12"
- Price: id 1227 → `"$185.90"`
- Legacy V1 AK45-36 KV80: "Weight (g) 340", "Back drive (Nm) 0.8", "Number of encoder 1". Price Yes $185.90 / No $149.90. URL: https://www.cubemars.com/product/AK45-36.html

**AK60-6 V3.0 KV80** — https://www.cubemars.com/product/ak60-6-v3-0-kv80-robotic-actuator.html
- Size and mass: "Motor Dimensions Ф79*43mm"; "Motor Weight (g) 380"
- Ratio and reducer: "Reduction Ratio 6∶1"; "6:1 planetary gearbox with low backlash"
- Voltage: "Rated Voltage (v) 24/48"
- Speed: "No-load speed (rpm) 320/640"; "Rated Speed (rpm) 233/490"
- Torque: "Rated Torque (Nm) 3"; "Peak Torque (Nm) 9"
- Current: "Rated Current (ADC) 3.8"; "Peak Current (ADC) 10.3/11.2"
- Backdrive: "Back-drive Torque (Nm) 0.2"
- Encoder: "Inner Ring Encoder Resolution 21bit"; the comparison row says "Yes | Single"
- Price: id 1174 attr 6082,6200 → `"$298.90"` (YES driver); attr 6082,6201 → `"$229.90"` (NO)
- Legacy AK60-6 V1.1 KV140 ($298.90): "Weight (g) 368", "Rated voltage (V) 24", "Inner ring encoder resolution 14bit"

**AK60-39 V3.0 KV80** — https://www.cubemars.com/product/ak60-39-v3-0-kv80-robotic-actuator.html
- Size and mass: "Motor Dimensions Ф79*67mm"; "Weight (g) 750"
- Ratio and reducer: "Reduction Ratio 39:1"; "two-stage planetary gearbox"
- Voltage: "Rated voltage (V) 48"
- Torque: "Rated torque (Nm) 24"; "Peak torque (Nm) 72"
- Speed: "Rated speed (rpm) 70"; "No-load speed (rpm) 98"
- Current: "Rated current (ADC) 4.5"; "Peak current (ADC) 17"
- Backdrive and backlash: "Back drive (Nm) 1.4"; "Backlash (arcmin) 15"
- Encoders: "Inner ring encoder resolution 21bit"; "Outer ring encoder resolution 21bit"; "Number of encoder 2"
- Price: id 1203 → `"$448.90"`
- Note: the table labels the connectors as "CAN connector A1257WR-S-3P / UART connector XT30PW-M". These labels look swapped compared with the other models.

**AK70-9 V3.0 KV60** — https://www.cubemars.com/product/ak70-9-v3-0-kv60-robotic-actuator.html
- Size and mass: "Motor Dimensions Ф89*49mm"; "Weight (g) 540"
- Ratio and reducer: "Reduction Ratio 9:1"; "9:1 planetary gearbox"
- Voltage: "Rated Voltage (V) 48"
- Torque: "Rated Torque (N·m) 8.5"; "Peak Torque (N·m) 29.2"
- Speed: "Rated Speed (RPM) 260"; "No-Load Speed (RPM) 320"
- Current: "Rated Current (ADC) 6.25"; "Peak Current (ADC) 23.8"
- Backdrive and backlash: "Back Drive (N·m) 0.8"; "Backlash (arcmin) 18"
- Encoders: "Inner Loop Encoder Resolution 21bit"; "Number of Encoder 2"
- Price: id 1222 attr 6363 → `"$498.90"` (YES); 6364 → `"$398.90"` (NO)
- Legacy: store "AK70-9 KV60" is $498.90. No page for it was found in the category.

**AK70-10 KV100** — https://www.cubemars.com/product/ak70-10-kv100-robotic-actuator.html
- Size and mass: "Motor Dimensions Ф89*50.25mm"; "Weight (g) 621"
- Ratio: "Reduction ratio 10:01"
- Voltage: "Rated voltage (V) 24/48"
- Torque: "Rated torque (Nm) 8.3"; "Peak torque (Nm) 24.8"
- Speed:
  - "Rated speed (rpm) 148/310"
  - No-load is not in the page table. The comparison row gives "240/480", and the core data gives "No-load Speed 480rpm".
- Current: "Rated current (ADC) 7.2"; "Peak current (ADC) 23.2"
- Backdrive and backlash: "Back drive(Nm) 0.48"; "Backlash (°) 0.2"
- Encoder: "Inner ring encoder resolution 14bit"; "Number of encoder 1"
- Price: id 1031 attr 5249 → `"$498.90"`; 5248 → `"$398.90"`

**AK80-6 KV100** — https://www.cubemars.com/product/ak80-6-kv100-robotic-actuator.html
- Size and mass: "Motor Dimensions Ф98*38.5mm"; "Weight (g) 485"
- Ratio: "Reduction ratio 6:01"
- Voltage: "Rated voltage (V) 48"
- Torque: "Rated torque (Nm) 6"; "Peak torque (Nm) 12"
- Speed: "Rated speed (rpm) 603"; "No-load Speed 800rpm"
- Current: "Rated current (ADC) 9.7"; "Peak current (ADC) 20"
- Backdrive: "Back drive(Nm) 0.36"
- Encoder: "Inner ring encoder resolution 14bit"
- Price: id 981 → YES `"$569.90"` / NO `"$469.90"`. Not in the Shopify store.

**AK80-8 KV60** — https://www.cubemars.com/product/ak80-8-kv60-robotic-actuator.html
- Size and mass: "Motor Dimensions Ф98*43.9mm"; "Weight (g) 570"
- Ratio: "Reduction ratio 8:01"
- Voltage: "Rated voltage (V) 48"
- Torque: "Rated torque (Nm) 10"; "Peak torque (Nm) 25"
- Speed: "Rated speed (rpm) 243"; "No-load Speed 360rpm"
- Current: "Rated current (ADC) 6.9"; "Peak current (ADC) 21"
- Backdrive and backlash: "Back drive(Nm) 0.75"; "Backlash (°) 0.38"
- Encoders: "Inner ring encoder resolution 14bit"; "Outer ring encoder resolution 15bit"; "Number of encoder 2"
- Price: id 1151 → YES `"$569.90"` / NO `"$469.90"`

**AK80-9 V3.0 KV100** — https://www.cubemars.com/product/ak80-9-v3-0-robotic-actuator.html
- Size and mass: "Motor Dimensions Ф98*38.5mm"; "Weight (g) 490"
- Ratio and reducer: "Reduction Ratio 9:1"; "9:1 planetary gearbox"
- Voltage: "Rated voltage (V) 48"
- Torque: "Rated torque (Nm) 9"; "Peak torque (Nm) 22"
- Speed: "Rated speed (rpm) 390"; "No-load speed (rpm) 570"
- Current: "Rated current (ADC) 12"; "Peak current (ADC) 28"
- Backdrive and backlash: "Back drive (Nm) 0.51"; "Backlash (arcmin) 15"
- Encoder: "Inner ring encoder resolution 16bit"; "Number of encoder 1"
- Price: id 1195 attr 6123,6199 → `"$579.90"`; 6123,6198 → `"$479.90"`
- Legacy store listing "AK80-9 KV100": NO 479.90 / YES 579.90.

**AK80-64 KV80** — https://www.cubemars.com/product/ak80-64-kv80-robotic-actuator.html
- Size and mass: "Motor Dimensions Ф98*61.9mm"; "Weight (g) 850"
- Ratio and reducer: "Reduction ratio 64:1"; "proprietary planetary gearbox". The stage count is not stated.
- Voltage: "Rated voltage (V) 24/48"
- Torque: "Rated torque (Nm) 48"; "Peak torque (Nm) 120"
- Speed: "Rated speed (rpm) 23/48"; the comparison row gives no-load "37/75"
- Current: "Rated current (ADC) 7"; "Peak current (ADC) 19"
- Backdrive and backlash: "Back drive(Nm) 4.7"; "Backlash (°) 0.18"
- Encoder: "Inner ring encoder resolution 14bit"
- Price: id 1143 → YES `"$989.90"` / NO `"$889.90"`

**AK10-9 V3.0 KV60** — https://www.cubemars.com/product/ak10-9-v3-0-kv60-robotic-actuator.html
- Size and mass: "Motor Dimensions Ф98*61.7mm"; "Motor Weight (g) 940"
- Ratio and reducer: "Reduction Ratio 9∶1"; "Equipped with a 9:1 planetary reducer"
- Voltage: "Rated Voltage (v) 48"
- Torque: "Rated Torque (Nm) 18"; "Peak Torque (Nm) 53"
- Speed: "Rated Speed (rpm) 235"; "No-load speed (rpm) 320"
- Current: "Rated Current (ADC) 10.7"; "Peak Current (ADC) 31.9"
- Encoders: "Inner Ring Encoder Resolution 21bit"; "Outer Ring Encoder Resolution 15bit"; "Number of Encoder 2"
- Price: id 1175 attr 5377,6202 → `"$798.90"`; 5377,6203 → `"$698.90"`
- Back-drive torque is not in the V3 table. The V2.0 page (https://www.cubemars.com/product/ak10-9-v2-0-kv60-robotic-actuator.html) has "Back drive(Nm) 0.8", "Weight (g) 960" and "Peak torque (Nm) 48".
- **KV100 V3 was not found.** The site offers only KV60 for V3. "AK10-9 V2.0 KV100" appears only in the store driver-board flash list.

**AKA60-6 KV80** — https://www.cubemars.com/product/aka60-6-kv80-robotic-actuator.html
- Mass and ratio: "Weight 460g"; "Reduction Ratio 6∶1"
- Voltage: "Rated Voltage 24/48V"
- Speed: "No-Load Speed 320/640rpm"; "Rated Speed 200/400rpm"
- Torque: "Rated Torque 3Nm"; "Peak Torque 9Nm"
- Current: "Rated Current 4ADC"; "Peak Current 11.2ADC"
- Radial load: "Rated Radial Load 18kg"
- Comparison row: "AKA60-6 KV80 … Ф80*51.2 | Yes | Single"
- Price: id 1181 → `"$298.90"`

**AKA10-9 KV60** — https://www.cubemars.com/product/aka10-9-kv60-robotic-actuator.html
- Size and mass: "Motor Dimensions ∅100*70mm"; "Weight 1060g"
- Ratio: "Reduction Ratio 9∶1"
- Voltage: "Rated Voltage 48V"
- **No-load speed conflict:** the table gives "No-Load Speed 280rpm", but the core data and the comparison row give "No-load Speed 320rpm".
- Torque: "Rated Torque 18Nm"; "Peak Torque 53Nm"
- Speed: "Rated Speed 109rpm"
- Current: "Rated Current 10.6ADC"; "Peak Current 32ADC"
- Backdrive and backlash: "Back drive 0.8 Nm"; "Backlash 0.15°"
- **Encoder conflict:** the page lists "Outer ring encoder resolution 16bit", but the comparison row says "Single".
- Interface: "Isolated CAN port for stable communication"
- Price: id 1189 → `"$798.90"`

**AKE60-8 KV80 (QDD, no driver)** — https://www.cubemars.com/product/ake60-8-kv80-quasi-direct-drive-actuator.html
- Size and mass: "Motor Dimensions φ69*25mm"; "Weight (g) 260"
- Ratio and reducer: "Reduction Ratio 8:1"; "brushless DC motor with a planetary gearbox"
- Voltage: "Rated voltage (V) 24"
- Torque: "Rated torque (Nm) 5"; "Peak torque (Nm) 12.5"
- Speed: "Rated speed (rpm) 180"; "No-load speed (rpm) 240"
- Current: "Rated current (ADC) 4.8"; "Peak current (ADC) 12"
- Backlash: "Backlash (arcmin) 9"
- Driver: the comparison row says "Driver Board … No"
- Price: id 1173 → `"$218.90"`. The store "Driver Board for AKE Series" costs AKE60-8 "79.90" (product-page variant "Driver board" "79.99").
- Total with board: E = 218.90 + 79.90 = 298.80.

**AKE80-8 KV30** — https://www.cubemars.com/product/ake80-8-kv30-quasi-direct-drive-actuator.html
- Size and mass: "Motor Dimensions Ф87*32mm"; "Weight (g) 570"
- Ratio: "Reduction Ratio 8:1"
- Voltage: "Rated voltage (V) 48"
- Torque: "Rated torque (Nm) 12"; "Peak torque (Nm) 30"
- Speed: "Rated speed (rpm) 150"; "No-load speed (rpm) 195"
- Current: "Rated current (ADC) 4.8"; "Peak current (ADC) 12"
- Backlash: "Backlash (arcmin) 9"
- Price: id 1165 → `"$339.90"`; the store driver board costs AKE80-8 "129.90"
- Total with board: E = 469.80.

**AKE90-8 KV35** — https://www.cubemars.com/product/ake90-8-kv35-quasi-direct-drive-actuator.html
- Size and mass: "Motor Dimensions Ф107.5*43.5mm"; "Weight (g) 1400"
- Ratio and reducer: "Reduction Ratio 8:1"; "The gearbox features a 5-stage gear structure" (odd for 8:1; recorded as-is)
- Voltage: "Rated voltage (V) 48"
- Torque: "Rated torque (Nm) 55"; "Peak torque (Nm) 170"
- Speed: "Rated speed (rpm) 120"; "No-load speed (rpm) 210"
- Current: "Rated current (ADC) 21"; "Peak current (ADC) 72"
- Backlash: "Backlash (arcmin) 9"
- Torque density: "Maximum torque weight ratio (Nm/kg) 121.4"
- Price: id 1176 → `"$483.90"`; the store driver board costs AKE90-8 "159.90"
- Total with board: E = 643.80. The manual pairs this model with the AK80-4830 driver (90 A max).

**AKH70-16 V1.0 KV41 (hollow)** — https://www.cubemars.com/product/akh70-16-v-1-0-kv41-hollow-shaft-planetary-actuator.html
- Size and bore: "Actuator Size Ф90*60.5mm"; "Hollow Bore Diameter 7mm"
- Mass: "Weight (g) 879"
- Ratio and reducer: "Reduction Ratio 16:1"; "a two-stage 16:1 planetary gearbox"
- Voltage: "Rated Voltage (V) 48"
- Torque: "Rated Torque (N·m) 26"; "Peak Torque (N·m) 78"
- Speed: "Rated Speed (RPM) 90"; "No-Load Speed (RPM) 105"
- Current: "Rated Current (ADC) 6.5"; "Peak Current (ADC) 19.5"
- Backdrive and backlash: "Back Drive (N·m) 0.78"; "Backlash (arcmin) 12"
- Encoders: "Integrated dual 21-bit magnetic encoders (motor-side and output-side)"
- Interface: "Dual CAN Interfaces for Multi-Actuator Daisy-Chain Configurations"
- Price: id 1220 → `"$598.90"`; store "598.00"

**AKH70-48 V1.0 KV41 (hollow)** — https://www.cubemars.com/product/akh70-48-v-1-0-kv41-hollow-shaft-planetary-actuator.html
- Size and mass: "Actuator Size Ф90*81.5mm"; "Weight (g) 1396"
- Ratio and reducer: "Reduction Ratio 48:1"; "a three-stage 48:1 planetary gearbox"
- Torque: "Rated Torque (N·m) 74"; "Peak Torque (N·m) 222"
- Speed: "Rated Speed (RPM) 28"; "No-Load Speed (RPM) 35"
- Current:
  - "Rated Current (ADC) 6"
  - **Peak current conflict:** the page has "Peak Current (ADC) 18", but the comparison row has "222 | 21".
- Backdrive and backlash: "Back Drive (N·m) 2.22"; "Backlash (arcmin) 12"
- Price: id 1221 → `"$698.90"`; store "698.00"

**Other CubeMars items found but out of scope:**
- RO/RI series (e.g. "RO40 KV140 Lite" $51.90, "RI20 KV600" $42.90, published 2026-06/08) are **frameless torque motors**, not integrated actuators.
- TW-40A/80A are ESCs.
- No other 2025–26 integrated humanoid actuators exist beyond AKA/AKE/AKH/AK V3.

#### 2.2 MyActuator RMD-X (specs VERIFIED from official spec images; prices UNVERIFIED)

**Common sources**
- X-series overview: https://www.myactuator.com/rmd-x-planetarymotor. It lists:
  - "(V4.1-Special Series For Robot)": X4-36-L, X8-150, X10-200
  - "(V4-Special Series For Robot)": X2-7, X4-10, X4-36, X6-60, X8-32, X8-120, X12-320, X15-450
  - "(V3-Dual encoder)": X6-8, X10-40, X10-100
  - "(V2-Single encoder)": X6-7, X6-40, X8-25
- Downloads page: https://www.myactuator.com/downloads-xseries. Old-name mapping:
  - "X8-25 || RMD-X8-Pro 1:9"
  - "X6-40 || RMD-X6-S2 1:36"
  - "X10-100 || RMD-X10 S2 1:35"
  - "X10-40 || RMD-X10 1:7"
  - "X6-8 || RMD-X6 1:8"
  - "X6-7 || RMD-X6 1:6"
  - The manuals and protocols are only in ZIPs, which were not downloaded.
- Official manual "User Manual for X Series Products V1.1" (MyActuator document, hosted by Seeed): https://files.seeedstudio.com/products/Myactuator/User_Manual_X_Series_Products_V1.1.pdf
  - "integrates a frameless torque motor, absolute encoder, servo driver and planetary reducer"
  - "The module is controlled by double absolute encoders"
  - "the multi-turn encoder is powered by a specific battery"
  - "48VDC have a maximum withstand voltage of 55VDC"
  - "72VDC have a maximum withstand voltage of 90VDC"
- (U) Seeed wiki CAN setup: "sudo ip link set can0 type can bitrate 1000000", which implies 1 Mbps. URL: https://wiki.seeedstudio.com/myactuator_series/
- **Prices (U):** myactuator.com has no web store.
  - The Alibaba store myactuator.en.alibaba.com hit a captcha, which was not bypassed.
  - RobotShop returned a Cloudflare 403.
  - Prices were therefore taken from reseller AIFITLAB's Shopify JSON (https://aifitlab.com/collections/myactuator/products.json, updated 2026-09-24).
- India (U): Amazon.in "MyActuator RMD-X8 S2 V3 1:36 …" https://www.amazon.in/MyActuator-RMD-X8-S2-V3-Exoskeleton/dp/B0CD1ZS9N6
  - Also "MyActuator RMD-X8 H V3 1:6 …" https://www.amazon.in/MyActuator-RMD-X8-Brushless-Quadruped-Exoskeleton/dp/B0CD22Q6GV
  - Official US contact: "MyActuator USA LLC … Fremont, CA" (https://www.myactuator.com/globaldistributor)

**X2-7 (RMD-X2-P28-7-E), V4** — page https://www.myactuator.com/x2-7details
- Spec image: https://static.wixstatic.com/media/cab28a_69718eb4718e4228bfe7b55d904b6b27~mv2.jpg
- Model and interface (*img*): "RMD-X2-P28-7-E N (without brake) EtherCAT & CAN BUS"
- Ratio: "Reduction Ratio — 28.17"
- Voltage: "Rated Voltage V 24"; "Voltage Range V 20-55"
- Speed: "No-Load Speed RPM 178"; "Rated Speed RPM 142"
- Torque: "Rated Torque N.m 2.5"; "Peak Torque N.m 7"
- Current: "Rated Current A 3"; "Peak Current A 8.1"
- Backdrive and backlash: "Backdrive Torque N.m 0.4"; "Backlash Arcmin ≤15"
- Encoder: "Dual Encoder ABS-17BIT(Input) / 18BIT(Output)"
- Mass and size: "Weight Kg 0.26"; drawing "Ø44" and "63.5 ±0.5"
- Price (U): "RMD-X2-7 (CAN BUS) / NOT Include 345.00" https://aifitlab.com/products/myactuator-rmd-x2-7-motor

**X4-10 (RMD-X4-P12.5-10-C/-E), V4** — https://www.myactuator.com/x4-10details
- Spec image: https://static.wixstatic.com/media/cab28a_2b2f7baa22b54695b5fca3156d882392~mv2.jpg
- Variants (*img*): "RMD-X4-P12.5-10-C … CAN BUS"; "RMD-X4-P12.5-10-E … EtherCAT"
- Ratio: "Reduction Ratio — 12.5"
- Voltage: "Rated Voltage V 24"; "Voltage Range V 20-55"
- Speed: "No-Load Speed RPM 317"; "Rated Speed RPM 238"
- Torque: "Rated Torque N.m 4"; "Peak Torque N.m 10"
- Current: "Rated Phase Current A(rms) 7.8"; "Peak Phase Current A(rms) 19.5"
- Backdrive and backlash: "Backdrive Torque N.m 0.8"; "Backlash Arcmin ≤15"
- Encoder: "Dual Encoder ABS-17BIT (Input) / 18BIT(Output)"
- Mass and size: "Weight Kg 0.33"; "Ø55 ±0.1"; "55.5 ±0.5"
- Price (U): $345 https://aifitlab.com/products/myactuator-rmd-x4-10-motor

**X4-36 (RMD-X4-P36-36-C/-E), V4** — https://www.myactuator.com/x4-36details
- Spec image: https://static.wixstatic.com/media/cab28a_87f995ec4597465793b24e7423fe124a~mv2.jpg
- Ratio (*img*): "Reduction Ratio — 36"
- Voltage: "Input Voltage V 24"; "Voltage Range V 20-55"
- Speed: "No-Load Speed RPM 111"; "Rated Speed RPM 83"
- Torque: "Rated Torque N.m 10.5"; "Peak Torque N.m 34"
- Current: "Rated Phase Current A(rms) 6.1"; "Peak Phase Current A(rms) 21.5"
- Backdrive and backlash: "Backdrive Torque N.m 1.14"; "Backlash Arcmin ≤15"
- Encoder: "Dual Encoder ABS-17BIT (Input) / 18BIT (Output)"
- Mass and size: "Weight Kg 0.36"; "Ø55 ±0.1"; "61 ±0.5"
- Price (U): $400 https://aifitlab.com/products/myactuator-rmd-x4-36-motor

**X4-36-L (RMD-X4-P36-36-E-L), V4.1** — https://www.myactuator.com/x4-36-l-details
- Spec image: https://static.wixstatic.com/media/cab28a_d8a8e0059f92437fa9865849c288f823~mv2.jpg
- Model and interface (*img*): "RMD-X4-P36-36-E-L … EtherCAT / CAN BUS"
- Ratio: "Reduction Ratio — 36"
- Voltage: "Input Voltage V 24"; "Voltage Range V 20-55"
- Speed: "No-load Speed RPM 111"; "Rated Speed RPM 83"
- Torque: "Rated Torque N.m 10.5"; "Peak Torque N.m 30"; "Stall Torque N.m 36"
- Current: "Rated Phase Current A(rms) 6.1"; "Stall Phase Current A(rms) 21.2"
- Backdrive and backlash: "Backdrive Torque N.m 0.2"; "Backlash Arcmin 15"
- Encoder: "Dual Encoder ABS 17BIT/18BIT"
- Mass and size: "Weight Kg 0.36"; "Dimensions mm 55x61"
- Price: none found.

**X6-60 (RMD-X6-P20-60-C/-E), V4** — https://www.myactuator.com/x6-60details
- Spec image: https://static.wixstatic.com/media/cab28a_e1bfa52ed5ae4315b776f8945bf57dcb~mv2.jpg
- Ratio (*img*): "Reduction Ratio — 19.612"
- Voltage: "Input Voltage V 48"; "Voltage Range V 20-55"
- Speed: "No-Load Speed RPM 176"; "Rated Speed RPM 153"
- Torque: "Rated Torque N.m 20"; "Peak Torque N.m 60"
- Current: "Rated Phase Current A(rms) 9.5"; "Peak Phase Current A(rms) 29.1"
- Backdrive and backlash: "Backdrive Torque N.m 1.6"; "Backlash Arcmin ≤15"
- Encoder: "Dual Encoder ABS-17BIT(Input) / 17BIT(Output)"
- Mass and size: "Weight Kg 0.82"; "Ø80 ±0.1"; "67.5 ±0.5"
- Price (U): $490 https://aifitlab.com/products/myactuator-rmd-x6-60-motor

**X8-32 (RMD-X8-P9-32-R), V4, RS485 only** — https://www.myactuator.com/x8-32-details
- Spec image: https://static.wixstatic.com/media/cab28a_a1f54c5a271f41b6b9f9a2bcec85f8da~mv2.jpg
- Model and interface (*img*): "Single Encoder"; "RMD-X8-P9-32-R N (without Brake) RS485"
- Ratio: "Reduction Ratio — 9"
- Voltage: "Rated Voltage V 24"
- Speed: "No-Load Speed RPM 277"; "Rated Speed RPM 244"
- Torque: "Rated Torque N.m 8"; "Peak Torque N.m 32"
- Current: "Rated Current A(rms) 6.2"; "Peak Current A(rms) 30"
- Backdrive and backlash: "Backdrive Torque N.m 0.8"; "Backlash Arcmin ≤10"
- Encoder: "Single Encoder ABS-18BIT"
- Mass and size: "Weight Kg 0.53"; "Ø96 ±0.1"; "41.2 ±0.5"
- Price (U): $645 https://aifitlab.com/products/myactuator-rmd-x8-32-motor
- **Not CAN.**

**X8-120 (RMD-X8-P20-120-C/-E), V4** — https://www.myactuator.com/x8-120details
- Spec image: https://static.wixstatic.com/media/cab28a_381ded42ea7d4e328e473c8cb73b2e06~mv2.jpg
- Variant (*img*): "RMD-X8-P20-120-C N (without brake) CAN BUS"
- Ratio: "Reduction Ratio — 19.61"
- Voltage: "Input Voltage V 48"; "Voltage Range V 20-55"
- Speed: "No-Load Speed RPM 158"; "Rated Speed RPM 127"
- Torque: "Rated Torque N.m 43"; "Peak Torque N.m 120"
- Current: "Rated Phase Current A(rms) 17.6"; "Peak Phase Current A(rms) 43.8"
- Backdrive and backlash: "Backdrive Torque N.m 1.5"; "Backlash Arcmin ≤15"
- Encoder: "Dual Encoder ABS-17BIT (Input) / 17BIT (Output)"
- Interface: "Communication Interface — CAN BUS / EtherCAT"
- Mass and size: "Weight Kg 1.40"; "Ø96"; "76 ±0.5"
- Price (U): $645 https://aifitlab.com/products/myactuator-rmd-x8-120-motor

**X8-150 (RMD-X8-P20-150-E), V4.1** — https://www.myactuator.com/x8-150-details
- Spec image: https://static.wixstatic.com/media/cab28a_856ade5d6f3047c4b292fcec951e2434~mv2.jpg
- Model and interface (*img*): "RMD-X8-P20-150-E … EtherCAT / CAN BUS"
- Ratio: "Reduction Ratio — 19.612"
- Voltage: "Input Voltage V 48"
- Speed: "No-load Speed RPM 158"; "Rated Speed RPM 127"
- Torque: "Rated Torque N.m 43"; "Peak Torque N.m 120"; "Stall Torque N.m 150"
- Current: "Stall Phase Current A(rms) 67.18"
- Backdrive: "Backdrive Torque N.m 0.34"
- Encoder: "Dual Encoder ABS-17BIT/ABS-19BIT"
- Mass and size: "Weight Kg 1.33"; "Dimensions mm 96x71"; "Hollow Shaft Diameter mm 12.6"
- Price: none found.

**X10-200 (RMD-X10-P20-200-E), V4.1** — https://www.myactuator.com/x10-200-details
- Spec image: https://static.wixstatic.com/media/cab28a_0c5c1e55fa1e431786fd4f3269c3b1f7~mv2.jpg
- Ratio (*img*): "Gear Ratio — 20"
- Voltage: "Input Voltage V 48"
- Speed: "No-load Speed RPM 80"; "Rated Speed RPM 74"
- Torque: "Rated Torque N.m 60"; "Peak Torque N.m 170"; "Stall Torque N.m 200"
- Current: "Rated Phase Current A(rms) 12.7"; "Stall Phase Current A(rms) 56.6"
- Backdrive: "Backdrive Torque N.m 1"
- Encoder: "Dual Encoder ABS-17BIT/ABS-19BIT"
- Mass and size: "Weight Kg 1.64"; "Dimensions mm 124x63.5"; "Hollow Shaft Diameter mm 12"
- Price (U): $800 https://aifitlab.com/products/myactuator-rmd-x10-200-motor

**X12-320 (RMD-X12-P20-320-E), V4** — https://www.myactuator.com/x12-320-details
- Spec image: https://static.wixstatic.com/media/cab28a_8a7a81c696f9428882ab98f45930d4f1~mv2.jpg
- Ratio (*img*): "Reduction Ratio — 20"
- Voltage:
  - "Input Voltage V 48"; "Voltage Range V 20-70"
  - The same sheet also says "The maximum operating voltage of the motor is 55V" (conflict).
- Speed: "No-Load Speed RPM 125"; "Rated Speed RPM 100"
- Torque: "Rated Torque N.m 85"; "Peak Torque N.m 320"
- Current: "Rated Phase Current A(rms) 30"; "Peak Phase Current A(rms) 100"
- Backdrive: "Backdrive Torque N.m 3.8"
- Mass and size: "Weight Kg 2.37"; "Ø124 ±0.1"; "85 ±0.5"
- Price (U): $1090

**X15-450 (RMD-X15-P20-450-E), V4** — https://www.myactuator.com/x15-450-details
- Spec image: https://static.wixstatic.com/media/cab28a_fca90a59b56d4ec7adc81dd6756c2679~mv2.jpg
- Ratio (*img*): "Reduction Ratio — 20.25"
- Voltage: "Input Voltage V 72"; "Voltage Range V 20-80"
- Speed: "No-Load Speed RPM 108"; "Rated Speed RPM 98"
- Torque: "Rated Torque N.m 145"; "Peak Torque N.m 450"
- Current: "Rated Phase Current A(rms) 25"; "Peak Phase Current A(rms) 69.2"
- Backdrive: "Backdrive Torque N.m 4"
- Mass and size: "Weight Kg 3.50"; "Ø166 ±0.1"; "69 ±0.5"
- Price (U): $1515

**X6-7 (RMD-X6-P6-7-C-N), V2** — https://www.myactuator.com/x6-7-details
- Spec image: https://static.wixstatic.com/media/cab28a_e0316306b6464088a860aefc28ae1f53~mv2.jpg
- Ratio (*img*): "Gear ratio 6"
- Voltage: "Input Voltage V 48"
- Speed: "Rated Speed RPM 400"; test row "(No_Load) 0.028 670 1.96 48.13"
- Torque: "Rated Torque N.m 3.5"; "Peak Torque N.m 7"
- Current: "Rated Current A 4"; "Peak Current A 9"
- Backdrive and backlash: "Anti-Force Torque N.m 0.08"; "Backlash Arcmin 10"
- Encoder: "Encoder Type bit 18"
- Interface: "CAN:1M/RS485:115200/500K/1M/2.5M"
- Mass and size: "Weight kg 0.35"; "Ø76"; "38"
- Price (U): "RMD-X6 1:6 V2 CAN V3 / NOT Include 250.00"

**X6-8 (RMD-X6-P8-8-C-N), V3** — https://www.myactuator.com/x6-8-details
- Spec image: https://static.wixstatic.com/media/cab28a_b479c75a00994e8b977efef976d2be37~mv2.jpg
- Ratio (*img*): "Gear ratio 8"
- Voltage: "Input Voltage V 48"
- Speed: "Rated Speed RPM 310"; "(No_Load) 0.227 368 8.73 48.05"
- Torque: "Rated Torque N.m 4.5"; "Peak Torque N.m 8"
- Current: "Rated Current A 3.6"; "Peak Current A 7.2"
- Backdrive and backlash: "Anti-Force Torque N.m 0.1"; "Backlash Arcmin 10"
- Encoder: "Encoder Type bit 14 / 14"
- Mass and size: "Weight kg 0.49"; "Ø79"; "44.50"
- Price (U): "RMD-X6 1:8 V3 CAN (discontinue soon) … 375.00"

**X6-40 (RMD-X6-P36-40-C-N), V2** — https://www.myactuator.com/x6-40-details
- Spec image: https://static.wixstatic.com/media/cab28a_100e949de2dd410c8e40087a4c9df1e2~mv2.jpg
- Ratio (*img*): "Gear ratio 36"
- Speed: "Rated Speed RPM 90"; "(No_Load) 0.01 109.9 0.13 48.02"
- Torque: "Rated Torque N.m 18"; "Peak Torque N.m 40"
- Current: "Rated Current A 5.2"; "Peak Current A 10.5"
- Backdrive and backlash: "Anti-Force Torque N.m 0.91"; "Backlash Arcmin 15"
- Encoder: "Encoder Type bit 18"
- Mass and size: "Weight kg 0.59"; "Ø76"; "60.50"
- Price (U): "RMD-X6-40 V2 CAN V3 / NOT Include 655.00"

**X8-25 (RMD-X8-P9-25-C-N), V2, ex-"RMD-X8-Pro 1:9"** — https://www.myactuator.com/x8-25-details
- Spec image: https://static.wixstatic.com/media/cab28a_6f8e8ce41b4b46889c2e5b29056a3871~mv2.jpg
- Ratio (*img*): "Gear ratio 9"
- Speed: "Rated Speed RPM 110"; "(No_Load) 0.04 254.3 1.16 48.14"
- Torque: "Rated Torque N.m 10"; "Peak Torque N.m 25"
- Current: "Rated Current A 3.2"; "Peak Current A 8"
- Backdrive and backlash: "Anti-Force Torque N.m 0.61"; "Backlash Arcmin 10"
- Encoder: "Encoder Type bit 18"
- Mass and size: "Weight kg 0.71"; "Ø98"; "51"
- Price (U): "RMD-X8-25 1:9 V2 CAN V3 / NOT Include 470.00"

**X10-40 (RMD-X10-P7-40-C-N), V3** — https://www.myactuator.com/x10-40-details
- Spec image: https://static.wixstatic.com/media/cab28a_8588d1a5e70a4a219f72da812d61a6ec~mv2.jpg
- Ratio (*img*): "Gear ratio 7"
- Speed: "Rated Speed RPM 165"; "(No_Load) 0.13 186.4 2.49 48.09"
- Torque: "Rated Torque N.m 15"; "Peak Torque N.m 40"
- Current: "Rated Current A 6.5"; "Peak Current A 15"
- Backdrive and backlash: "Anti-Force Torque N.m 0.62"; "Backlash Arcmin 10"
- Encoder: "Encoder Type bit 14 / 14"
- Mass and size: "Weight kg 1.15"; "Ø122"; "53"
- Price (U): "RMD-X10 V3 CAN Dual Encoder / NOT Include 645.00"

**X10-100 (RMD-X10-P35-100-C-N), V3** — https://www.myactuator.com/x10-100-details
- Spec image: https://static.wixstatic.com/media/cab28a_11c0665d415b4a68be8ea13cae44b5f0~mv2.jpg
- Ratio (*img*): "Gear ratio 35"
- Speed: "Rated Speed RPM 50"; "(No_Load) 0.24 53.6 1.34 47.99"
- Torque: "Rated Torque N.m 50"; "Peak Torque N.m 100"
- Current: "Rated Current A 6.7"; "Peak Current A 13.5"
- Backdrive and backlash: "Anti-Force Torque N.m 2.88"; "Backlash Arcmin 15"
- Encoder: "Encoder Type bit 14 / 14"
- Mass and size: "Weight kg 1.7"; "Ø122"; "74"
- Price: none found.

**Other MyActuator lines seen but not surveyed:**
- RH harmonic actuators, e.g. "RH-17-100 (EtherCAT & CAN Compatible+Dual Encoder)" (U) $945 at AIFITLAB.
- CEM cycloid actuators, e.g. "EPS-CEM-15-E-N" (U) $975.
- RMD-H/L direct-drive motors.
- Harmonic and cycloid reducers are normally not backdrivable (E), and these are costly for JX1.

#### 2.3 SteadyWin GIM (specs and prices VERIFIED on the official store steadywin-motor.com)

**Common sources**
- Official store: https://steadywin-motor.com/. Its product pages say "please visit: http://steadywin.cn/" and give "Email：info@steadywin-motor.com".
  - steadywin.cn did not resolve (DNS) from this machine.
- Store JSON with all variants and prices (2026-09-24): https://steadywin-motor.com/products.json?limit=250
- Q&A snippets from the product pages:
  - "GDZ468 driver supports three communication protocols: CAN, 485, and Modbus"
  - "the GDS68 drive board supports CAN communication"
  - "the GDM810 driver is MIT driver"
  - "secondary encoder is to remember the single-turn position after a power loss"
  - "GDZ and GDS series driver boards will be phased out"
  - "Dual encoder support is not available for models … GIM4310-10, GIM4310-36 and GIM10015-9"
- The selection tables and driver manuals are XLSX/ZIP (islandcloud.co → Backblaze) and were **not downloaded**. CAN bitrate is therefore not verified.
- India (V): the store has a product "Price Difference- PO# 1264 Shipping Cost-India" (https://steadywin-motor.com/products/price-difference-po-1264-shipping-cost-india), which shows direct shipping to India.

**GIM4310-10** — https://steadywin-motor.com/products/built-in-planetary-reduction-motor-aloha-accessories-quadruped-robot-joint-module-1
- Parameter image: https://steadywin-motor.com/cdn/shop/files/4310-10.jpg?v=1749547302
- Driver (*img*): "Driver board model GDS34(SDC101)"
- Voltage: "Rated voltage V 24"; "Voltage Range V 12~48"
- Torque: "Rated torque N.M 2.05"; "Peak torque N.M 5.60"
- Speed: "Rated Speed after reduce RPM 150"; "Max Speed after reduce RPM 228"
- Current: "Rated current A 2.3"; "Peak current A 6.80"
- Gearing: "Gear Rate 10:1"; "Gear type Planetary"; "Reducer gear backlash arcmin 15"
- Mass: "Motor weight without driver g 217"; "Motor weight with driver g 227"
- Size: "Size without Driver mm Ø53*32"; "Size with Driver mm Ø53*38"
- Interface and encoder: "Communication CAN"; "second encoder on the output shaft NO"; "encoder on the driver Bit 14bit"
- Prices (JSON):
  - "GIM4310-10 V1.1 / with GDK34 Driver | 126.90"
  - "with GDS34 Driver | 151.80" (available: false)
  - "Only Motor (without driver) | 82.00"

**GIM4315-8** — https://steadywin-motor.com/products/small-robot-joint-module-built-in-communication-driver-dual-encoder-aloha-motor
- Parameter image: https://steadywin-motor.com/cdn/shop/files/4315-8-1.jpg?v=1749522786
- Driver (*img*): "GDZ468"
- Voltage: "Rated voltage 24"; "Voltage Range 12~40"
- Torque: "Rated torque 3.06"; "Peak torque 10.18"
- Speed: "Rated Speed after reduce 152"; "Max Speed after reduce 199"
- Current: "Rated current 2.7"; "Peak current 10.70"
- Gearing: "Gear Rate 8:1"
- Mass: "342.7" (w/o driver); "369.3" (with driver)
- Size: "Ø57.5*51"; "Ø57.5*52"
- Interface and encoder: "Communication CAN"; second encoder "YES"; "14bit"
- Prices:
  - "with GDK468 Driver | 117.20"
  - "with GDZ468 Driver (12-40V) | 135.80" (sold out)
  - "whitout driver | 69.80" (sic)

**GIM4310-36** — https://steadywin-motor.com/products/built-in-planetary-reduction-high-torque-small-volume-quadruped-robot-motor-joint-servo-motor
- Parameter image: https://steadywin-motor.com/cdn/shop/files/GIM4310-36.jpg?v=1749540276
- Driver (*img*): "GDS34(SDC101)"
- Voltage: "24"; "12~48"
- Torque: "Rated torque 7.38"; "Peak torque 20.16"
- Speed: "Rated Speed … 41"; "Max Speed … 63"
- Current: "Rated current 2.3"; "Peak current 6.80"
- Gearing: "Gear Rate 36:1"
- Mass: "300"; "310"
- Size: "Ø55*40"; "Ø55*47"
- Encoder: second encoder "NO"; "14bit"
- Prices:
  - "with GDK34 Driver | 146.10"
  - "with GDS34 Driver | 169.80" (sold out)
  - "without Driver | 100.00"

**GIM6010-8** — https://steadywin-motor.com/products/built-in-star-gear-motor-motor-robot-joint-driver-actuator-controller-motor
- Parameter image: https://steadywin-motor.com/cdn/shop/files/Parameters_of_GIM6010-8_b0a97b30-dde5-4ff4-964f-883f11068221.png?v=1758686407
- Voltage and driver (*img*): "Rated voltage V 24 48"; "Driver board model / GDS68(SDC104) GDZ468H"; "Voltage Range V 12~56 12~48"
- Torque: "Rated torque N.M 5.00 4.20"; "Peak torque N.M 11.00 11.27"
- Speed: "Rated Speed after reduce RPM 120 220"; "Max Speed after reduce RPM 420 554"
- Current: "Rated current A 10.50 2.87"; "Peak current A 23.40 20.02"
- Gearing: "Gear Rate / 8:1 8:1"
- Mass: "Motor weight without driver g 370.0"; "with driver g 388.0"
- Size: "Ø80*29.5"; "Ø80*40"
- Interface and encoder: "Communication / CAN CAN & 485"; second encoder "YES"; "16bit"
- Prices:
  - "Standard Version / 24V / with GDS68 Driver | 93.88"
  - "with GDK468 Driver | 112.20"
  - "without Driver | 70.35"

**GIM8108-8** — https://steadywin-motor.com/products/planetary-reduction-motor-robot-dog-humanoid-robot-joint-module-flat-thin-large-torque
- Parameter image: https://steadywin-motor.com/cdn/shop/files/8108-8.jpg?v=1749546475
- Driver (*img*): "Driver board model GDS68(SDC104)"
- Voltage and power: "Rated voltage 48"; "Voltage Range 12~56"; "Rated Power W 336"
- Torque: "Rated torque 7.50"; "Peak torque 22.00"
- Speed: "Rated Speed after reduce 110"; "Max Speed after reduce 320"
- Current: "Rated current 7"; "Peak current 22.00"
- Gearing: "Gear Rate 8:1"; "backlash 15"
- Mass: "378" (w/o); "396" (with driver)
- Size: "Ø92*44"; "Ø92*55"
- Interface and encoder: "CAN & Type-C"; "YES"; "16bit"
- Prices: "GIM8108-8 Standard Version / with GDS68 driver | 129.20"; "without driver | 93.89"

**GIM8108-9** — https://steadywin-motor.com/products/bipedal-wheeled-high-torque-mechanical-dog-assisted-rehabilitation-exoskeleton-system-high-precision-driver
- Parameter image: https://steadywin-motor.com/cdn/shop/files/8108-9.jpg?v=1750055451
- Drivers (*img*): "GDS810(SDC103) GDM810(SDC303)"
- Voltage: "Rated voltage 48 24"; "12~48"
- Torque: "Rated torque 8.19 8.78"; "Peak torque 27.38 25.73"
- Speed: "Rated Speed 207 195"; "Max Speed 242 227"
- Current: "Rated current 4 9.2"; "Peak current 19.80 34.10"
- Gearing: "9:1"
- Mass: "525"; "567"
- Size: "Ø96*34"; "Ø96*41.5"
- Interface: "CAN & 485 / CAN"
- Price: "with GDS810 Driver / 48V | 189.60"

**GIM8115-9** — https://steadywin-motor.com/products/biped-wheeled-large-torque-mechanical-dog-joint-actuator-high-performance-built-in-driver-1
- Parameter image: https://steadywin-motor.com/cdn/shop/files/8115-9.jpg?v=1749700674
- Drivers (*img*): "GDS810(SDC103) GDM810(SDC303)"
- Voltage: "Rated voltage 24 48 24 48"
- Torque: "Rated torque 13.00 13.80 12.90 13.50"; "Peak torque 40.00 46.00 45.00 39.00"
- Speed: "Rated Speed 100 118 117 136"; "Max Speed 129 146 143 160"
- Current: "Rated current 7.9 4.6 8.4 5.1"; "Peak current 24.69 16.55 16.00 15.79"
- Gearing: "9:1"
- Mass: "660"; "705"
- Size: "Ø96*41"; "Ø96*48.5"
- Encoder: "14bit"
- Price: "with GDS810 Driver / 48V | 213.80"

**GIM6010-36** — https://steadywin-motor.com/products/planetary-torque-motor-1-36-bipolar-reduction-joint-module-servo-motor-robot
- Parameter image: https://steadywin-motor.com/cdn/shop/files/6010-36.jpg?v=1750063793
- Reducer: title "Planetary Torque Motor 1:36 Two-stage Gear Reducer"
- Drivers (*img*): "GDS6(SDC102) GDM6(SDC301)"
- Voltage: "48 24"; "12~48 12~36"
- Torque: "Rated torque 18.00 18.00"; "Peak torque 41.00 45.00"
- Speed: "Rated Speed 85 50"; "Max Speed 97 90"
- Current:
  - "Rated current 4.6 4"
  - "Peak current 9.30 66.18". The 66.18 A is implausible as printed and is flagged.
- Gearing: "36:1"
- Mass: "546"; "574"
- Size: "Ø76*45.50"; "Ø76*56.50"
- Prices: "with GDS6 Driver | 221.80"; "with GDZ468 Driver (12-40V) | 207.80"

**GIM6010-48** — https://steadywin-motor.com/products/planetary-reduction-motor-robot-joint-module-industrial-robot-arm-high-torque-motor
- Parameter image: https://steadywin-motor.com/cdn/shop/files/6010-48.jpg?v=1749872385
- Reducer: title "Two-stage Planetary Gear Reducer"
- Drivers (*img*): "GDS68(SDC104) GDZ468"
- Voltage: "24 24"; "12~56 12~36"
- Torque: "Rated torque 30.00 27.00"; "Peak torque 66.00 55.90"
- Speed: "Rated Speed 20 38"; "Max Speed 70 49"
- Current: "Rated current 10.5 6.5"; "Peak current 23.40 13.50"
- Gearing: "48:1"
- Mass: "758.9"; "776.9"
- Size: "Ø80*56.5"; "Ø80*67.5"
- Interface and encoder: "CAN & Type-C"; "16bit 14bit"
- Price: "with GDS68 Driver | 170.00"

**GIM8108-36** — https://steadywin-motor.com/products/biped-wheeled-large-torque-mechanical-dog-joint-actuator-high-performance-built-in-driver
- Parameter image: https://steadywin-motor.com/cdn/shop/files/8108-36.jpg?v=1749695966
- Drivers (*img*): "GDS810(SDC103) GDM810(SDC303)"
- Voltage: "48 24"
- Torque: "Rated torque 32.76 35.10"; "Peak torque 109.50 102.90"
- Speed: "Rated Speed 51 48"; "Max Speed 60 56"
- Current: "Rated current 4 9.2"; "Peak current 19.80 34.10"
- Gearing: "36:1"
- Mass: "720"; "760"
- Size: "Ø96*44.5"; "Ø96*57"
- Noise: "<65"
- Price: "with GDS810 Driver / 48V | 239.80"

**GIM8108-48** — https://steadywin-motor.com/products/joint-module-high-torque-planetary-reduction-motor-precision-control-servo-drive
- Parameter image: https://steadywin-motor.com/cdn/shop/files/8108-48.jpg?v=1749537296
- Driver (*img*): "GDZ468"
- Voltage and power: "Rated voltage 36"; "Voltage Range 12~36"; "Rated Power 191"
- Torque: "Rated torque 45.00"; "Peak torque 131.60"
- Speed: "Rated Speed 32"; "Max Speed 40"
- Current: "Rated current 5.3"; "Peak current 20.90"
- Gearing: "48:1"
- Mass: "762.4"; "780.4"
- Size: "Ø92*62"; "Ø92*73"
- Interface: "CAN & Type-C"
- Prices:
  - "with GDZ68 Driver | 214.80" (SKU "GIM8108-48+GDZ468")
  - "with GDS68 Driver | 193.00"
  - "without driver | 159.00"

**GIM10015-9** — https://steadywin-motor.com/products/bipedal-wheeled-brushless-servo-arm-with-high-torque-joint-actuator-and-built-in-driver
- Parameter image: https://steadywin-motor.com/cdn/shop/files/10015-9.jpg?v=1749783040
- Driver (*img*): "GDS810(SDC103)"
- Voltage: "24 48"; "12~48"
- Torque: "Rated torque 30.00 32.60"; "Peak torque 62.10 104.00"
- Speed: "Rated Speed 67 77.4"; "Max Speed 104 105"
- Current: "Rated current 14.2 8.2"; "Peak current 30.20 30.30"
- Gearing: "9:1"
- Mass: "1325"; "1372"
- Size: "Ø120*45"; "Ø122*57.5"
- Interface: "CAN & 485"
- **Second-encoder conflict:** the image table says "second encoder … YES", but the page says "For GIM10015-9 motor, dual encoders not supported".
- Bearings: "GIM10015-9 motor uses crossed roller bearings"
- Price: "with GDS810 Driver / 48V | 355.80"

**Other SteadyWin integrated models in the store, not tabulated:**
- Priced without a driver:
  - GIM3505-8 ($56–125.80), GIM3505-36 ($96.88–150.80), GIM3510-8 ($76–145.80), GIM3510-64 ($110–179.80) — Aloha/OpenArm size
  - GIM4305-10 ($68–128), GIM4310-40 ($89.80–182.60), GIM4315-40 ($145.20–213.80)
  - GIM6010-6 ($104–199.80), GIM8108-6 ($119.80–199.60), GIM8115-6 ($144–223.80), GIM8115-36 ($190–269.80)
  - WGG exoskeleton motors ($59.80–123)
- The GIM8115-36 page shows no parameter image. Specs for these were not collected.

#### 2.4 LK-Tech / Lingkong MG (specs VERIFIED from lkmotor.cn official parameter images; prices UNVERIFIED)

**Common sources**
- Official MG list (Chinese site): http://www.lkmotor.cn/Product.aspx?TypeID=18 lists:
  - MG10015-i10v3, MG8016E-i6v3, MG6012E-i8v3, MG8010-i36v2, MG6010-i6v3, MG8008-i9v3
  - MG6010E-i6v3, MG8008E-i9v3, MG6012-i36v3, MG4005E-i10v3, MG4010E-i10v3, MG5010E-i10v3
- The English site http://en.lkmotor.cn/Product.aspx?TypeID=18 still lists older v2 items (e.g. "MG6012E-i8v2", "MG8016E-i6v2").
- lkmotor.cn serves HTTP only. Its TLS certificate is for "antaxtech.com", so WebFetch failed.
  - The official image files were therefore read through the HTTPS image proxy `https://images.weserv.nl/?url=www.lkmotor.cn/<same path>`. The content is unmodified official artwork.
  - Official URLs are given below.
- Company line on the site: "Shanghai LingKong Technology Co., Ltd". Sales contacts: "AliExpress:fannie@lkmotor.cn Alibaba:sales@lkmotor". No official price is published, and the "Buy now" link is empty.
- Prices (U): reseller AIFITLAB Shopify, 2026-09-24.
  - Examples: "MG4010E-i10-V3 (CAN) | 165.0"; "MG6012-i36-V3 (Single Encoder) / CAN | 410.0"
  - The "B" SKUs, e.g. "MG6012E-i8B-V3" $580 and "MG8016E-i6B-V3" $580, are brake versions (listing mentions ~1.5 W brake power).
- India: no lead found. ThinkRobotics had none, Robu was blocked, and the web-search budget was exhausted.

**MG4010E-i10v3** — http://www.lkmotor.cn/ProDetail.aspx?ProId=248
- Table image: http://www.lkmotor.cn/upload/image/20230901/6382918075085506822699792.jpg
- Drawing: .../20230901/6382918075092341189442363.jpg
- Voltage and speed (*img*): "Rated Voltage V 24"; "Max Speed rpm 320"; "Rated Speed rpm 260"
- Torque: "Rated Torque N.m 2.5"; "Max Torque N.m 4.5"
- Current: "Rated Current A 3.5"
- Reducer: "Reducer Type PG4210"; "Reduction Ratio N 1:10"; "Backlash arcmin ≤8"
- Mass: "Motor Weight g 250"
- Driver: "Recommend Drive DG40"; "Drive Input Voltage V 7.4~32"
- Interface: "Communication RS485 OR CAN"; "CAN:2KHz(1Mbps)"; "Baudrate（CAN） 100K，125K，250K，500K，1M"
- Encoder: "18bit(motor)+14bit(reducer) Magnetic Encoder"
- Drawing: "Ø53 -0.05"; "41 ±0.1"
- Table typo: "Phase Resistance Ω 604" (surely mΩ)
- Price (U): https://aifitlab.com/products/lkmtech-mg4010e-i10-v3-motor

**MG5010E-i10v3** — http://www.lkmotor.cn/ProDetail.aspx?ProId=249
- Table image: .../20230825/6382857391114041726500144.jpg
- Drawing: .../20230825/6382857391119654405715298.jpg
- Voltage and speed (*img*): "Rated Voltage V 24"; "Max Speed rpm 320"; "Rated Speed rpm 235"
- Torque: "Rated Torque N.m 4"; "Max Torque N.m 7"
- Current: "Rated Current A 4.4"
- Reducer: "PG5110"; "1:10"; "≤8"
- Mass: "Motor Weight g 420"
- Driver: "DG50"; "12~40"
- Encoder and interface: "18 bit Magnetic Encoder"; "Baudrate（CAN） 1M"
- Drawing: "Ø63 -0.1"; "41.5 ±0.1"
- Price (U): $165 https://aifitlab.com/products/lkmtech-mg5010e-i10-v3-motor

**MG6010E-i6v3** — http://www.lkmotor.cn/ProDetail.aspx?ProId=224
- Table image: .../20230220/6381248689340903221796537.jpg
- Drawing: .../20230220/6381248689338832067567291.jpg
- Voltage and speed (*img*): "Rated Voltage (V) 24 48"; "Max Speed (rpm) 251 505"; "Rated Speed (rpm) 170 391"
- Torque: "Rated Torque (N.m) 5 5"; "Max Torque (N.m) 10 10"
- Current: "Rated Current (A) 5.5 5.3"
- Reducer: "PG4106"; "Gear Ratio 1:6"; "Backlash (arcmin) ≤6"
- Mass: "Motor Weight (g) 343"
- Driver: "DG60Ev2"; "Drive Input Voltage (V) 12~60"
- Encoder: "18 bit(Motor) & 14 bit(Reducer) Magnetic Encoder"
- Drawing: "Ø76 -0.1"; "38.5"
- Price: none found; the "MG6010" reseller search returned nothing.

**MG6012E-i8v3** — http://www.lkmotor.cn/ProDetail.aspx?ProId=200
- Interface image: .../20241014/6386449469050943605963832.jpg
- Drawing and table: .../20241014/6386449470307194128026831.jpg
- Interface (*img*): "A/H RS485-A Or CAN-H"
- Voltage and speed: "Rated Voltage (V) 48"; "Max Speed (rpm) 310"; "Rated Speed (rpm) 256"
- Torque: "Rated Torque (N.m) 6"; "Max Torque (N.m) 16"
- Current: "Rated Current (A) 3.5"
- Reducer: "PG4108"; "Gear Ratio 1:8"; "Backlash (arcmin) ≤6"
- Mass: "Motor Weight (g) 430"
- Driver: "DG60Ev2"; "12~60"
- Encoder: "18 bit Magnetic Encoder"
- Drawing: "Ø80 -0.05"; "44.5"
- Price (U): V2 "MG6012E-i8-V2 (Single Encoder) / CAN | 190.0" https://aifitlab.com/products/lkmtech-mg6012e-i8-v2-motor. This is the V2, not the V3.

**MG6012-i36v3** — http://www.lkmotor.cn/ProDetail.aspx?ProId=246
- Table image: .../20230706/6382426315423735527949538.jpg
- Drawing: .../20230706/6382426315436037481678017.jpg
- Voltage (*img*): "Rated Voltage (V) 24 48"
- Speed:
  - "Max Speed (rpm) 33 88"; "Rated Speed (rpm) 45 74"
  - A no-load speed of 33 is lower than the rated 45, so it is probably a typo. The 24 V curve ends near 1600 motor-rpm, i.e. ≈44 rpm at the output (E).
- Torque: "Rated Torque (N.m) 25 25"; "Max Torque (N.m) 40 40"
- Current: "Rated Current (A) 4 4.8"
- Reducer: "PG4136"; "Gear Ratio 1:36"; "Backlash (arcmin) ≤8"
- Mass: "Motor Weight (g) 503"
- Driver: "DG80v3"; "12~60"
- Encoder: "18 bitMagnetic Encoder"
- Drawing: "Ø80 -0.10"; "51"
- Price (U): $410
- Note: no "MG6012**E**-i36" exists on the official site.

**MG8008E-i9v3** — http://www.lkmotor.cn/ProDetail.aspx?ProId=225
- Table image: .../20230220/6381248698146442404860528.jpg
- Drawing: .../20230220/6381248698152301815144608.jpg
- Voltage and speed (*img*): "Rated Voltage (V) 24 48"; "Max Speed (rpm) 112 220"; "Rated Speed (rpm) 78 178"
- Torque: "Rated Torque (N.m) 9 10"; "Max Torque (N.m) 20 20"
- Current: "Rated Current (A) 4.6 4.9"
- Reducer: "PG5509"; "1:9"; "≤6"
- Mass: "Motor Weight (g) 570"
- Driver: "DG80Ev2"
- Encoder: "18 bit(Motor) & 14 bit(Reducer)"
- Drawing: "Ø98 -0.1"; "41"
- Price (U): $260 https://aifitlab.com/products/lkmtech-mg8008e-i9-v3-motor

**MG8016E-i6v3** — http://www.lkmotor.cn/ProDetail.aspx?ProId=198
- Drawing and table image: .../20241014/6386449460711871285541280.jpg
- Voltage and speed (*img*): "Rated Voltage (V) 48"; "Max Speed (rpm) 300"; "Rated Speed (rpm) 258"
- Torque: "Rated Torque (N.m) 12"; "Max Torque (N.m) 37"
- Current and power: "Rated Current (A) 8.4"; "Max Power (W) 670"
- Reducer: "PG5506"; "Gear Ratio 1:6"; "Backlash (arcmin) ≤6"
- Mass: "Motor Weight (g) 759"
- Driver: "DG80Ev2"
- Encoder: "18 bit Magnetic Encoder"
- Drawing: "Ø99"; "50.5"
- Price (U): V2 "MG8016E-i6-V2 (Single Encoder) / CAN | 330.0"

**MG8010-i36v2** — http://www.lkmotor.cn/ProDetail.aspx?ProId=203
- Table image: .../20230219/6381243932472498546574097.jpg
- Drawing: .../20230219/6381243932477511042560005.jpg
- Voltage and speed (*img*): "Rated Voltage (V) 48"; "Max Speed (rpm) 80"; "Rated Speed (rpm) 68"
- Torque: "Rated Torque (N.m) 35"; "Max Torque (N.m) 45"
- Current and power: "Rated Current (A) 6.9"; "Max Power (W) 800"
- Reducer: "PG5536"; "1:36"; "≤8"
- Mass: "Motor Weight (g) 860"
- Driver: "DG80v2"
- Encoder: "18 bit Magnetic Encoder"
- Drawing: "Ø99"; axial segments "2", "39", "12.5". Length E = 2 + 39 + 12.5 = 53.5.
- Price (U): $460 https://aifitlab.com/products/lkmtech-mg8010-i36v2-motor

**MG10015E-i10 (v3; listed as "MG10015-i10v3")** — http://www.lkmotor.cn/ProDetail.aspx?ProId=199
- Drawing: .../20241014/6386449443572774235568062.jpg
- Table image: .../20241014/6386449444457151728533370.jpg
- Voltage and speed (*img*): "Rated Voltage (V) 48"; "Max Speed (rpm) 185"; "Rated Speed (rpm) 150"
- Torque: "Rated Torque (N.m) 25"; "Max Torque (N.m) 45"
- Current and power: "Rated Current (A) 11.5"; "Max Power (W) 1200"
- Reducer: "PG7407"; "Gear Ratio 1:10"; "Backlash (arcmin) ≤8"
- Mass: "Motor Weight (g) 1210"
- Driver: "DG60Ev2"
- Encoder: "18 bit(Motor) & 14 bit(Reducer)"
- Drawing: "Ø120"; "48.2"; with crossed-roller bearing "51.2"
- Price (U): V2 "MG10015E-i10-V2 (Single Encoder) / CAN | 370.0"

**LK variants seen only at the reseller (U), not on the official site:**
- MG4010E-i36-V3 ($290)
- MG5010E-i36-V3 ($240)
- MG10015E-i36-V3 ($620)
- MG8016E-i24B-V3 ($580)
- MG8015E-i9-V3 ($340)


### 3. Gaps and uncertainties

#### Prices
1. **MyActuator and LK have no official prices.**
   - Neither site has a web store.
   - The MyActuator Alibaba store (myactuator.en.alibaba.com) returned a captcha, which was not bypassed.
   - RobotShop returned a Cloudflare 403.
   - All MyActuator and LK USD/N·m values therefore use AIFITLAB reseller prices (U). For MG6012E-i8, MG8016E-i6 and MG10015E-i10, only **V2** prices were found, although the specs are V3.
   - No CNY prices were used.
2. **MyActuator V4 details not verified.**
   - The CAN bitrate and CAN-FD support are not on the V4 spec sheets. The protocol/manual ZIPs were not downloaded, per the rules. 1 Mbps appears only in the Seeed wiki (U).
   - Reducer stage counts are not published for any RMD-X model.
3. **Legacy MyActuator models are not on the current official site.**
   - Missing: X4-24, X8 Pro/X8-20/X8-90 and X12-150.
   - The official downloads page maps "X8-25 = RMD-X8-Pro 1:9" and "X6-40 = RMD-X6-S2 1:36".
   - "RMD-X8 S2 V3 1:36" appears only at resellers and on Amazon.in (U).

#### Conflicts inside official sources
4. MyActuator:
   - X12-320: "Voltage Range 20-70" vs the note "maximum operating voltage … 55V".
   - X15-450: 72 V input vs the same boilerplate 55 V note. The manual says 72 V models withstand 90 V.
   - The manual V1.1 (2025) lists backlash of 10–12′ and an X4 ratio of 12.6. The current sheets say "≤15" and 12.5, and the current sheets were used.
5. CubeMars:
   - AKA10-9 no-load: 280 (table) vs 320 (core data).
   - AKA10-9 encoder: 16-bit outer encoder vs "Single" in the comparison row.
   - AKH70-48 peak current: 18 (page) vs 21 (comparison).
   - AK10-9 V3 back-drive torque is not published; 0.8 N·m comes from the V2.0 page.
   - AK10-9 V3 **KV100 was not found**; only KV60 exists.
   - AKE90-8 claims a "5-stage gear structure" for 8:1, which is unexplained.
   - The allowable voltage range for AK40-10/AK45-10/AK45-36 V3 is not verified: their driver AK48-2405 is not in the manual's table.
6. SteadyWin:
   - GIM10015-9 second encoder: YES in the table vs "not supported" on the page.
   - GIM6010-36 GDM6 peak current 66.18 A is implausible.
   - GIM6010-8 48 V rated current of 2.87 A looks odd.
   - GIM6010-48 rated speed of 20 rpm vs a max of 70 rpm looks odd.
   - Some tables say GDS810 is "CAN & 485", while the Q&A says GDS is CAN-only.
   - The specs are per driver variant, and the new **GDK** drivers (cheaper, "pre-order") have no published specs.
   - GDZ/GDS drivers are "phased out".
7. LK:
   - MG6012-i36v3 lists 33 rpm no-load at 24 V, below its 45 rpm rated speed, so it is probably a typo.
   - MG4010E-i10v3 prints "604 Ω", which should be mΩ.
   - The meaning of the "E" suffix (integrated driver) is inferred (E). For non-E MG6012-i36v3 and MG8010-i36v2, whether the driver is included is unclear.
   - Peak current is not published for any MG model.

#### Unpublished data
8. **Backdrivability** is published as a torque only by CubeMars (back-drive N·m) and MyActuator (Backdrive/Anti-Force torque). SteadyWin and LK labels are ESTIMATED from ratio only. No brand publishes efficiency-based backdrive data at load.
9. **Encoders:**
   - "Absolute at output" is single-turn for CubeMars (manual: "single-loop absolute") and for the SteadyWin secondary encoder (memory of the single-turn position).
   - MyActuator V4 has dual absolute encoders plus a battery-backed multi-turn count.
   - The LK "reducer-side 14-bit" encoder is not described further.

#### Definitions differ between vendors
10. **"Peak" is not defined the same way by each vendor.**
    - SteadyWin "Peak torque (堵转扭矩)" is stall torque.
    - MyActuator V4.1 separates "Peak" from "Stall" (e.g. X10-200: 170 / 200). The table uses Peak.
    - LK "Max Torque (峰值扭矩)" has no stated duration.
    - Only MyActuator publishes stall-time tables.
    - Cross-brand N·m/kg and USD/N·m values are therefore indicative only.
11. Mass basis:
    - SteadyWin masses are "with driver".
    - CubeMars AKE masses exclude the driver board.
    - For LK "Motor Weight", it is not stated whether the integrated driver is included.

#### Speeds
12. **Speeds are no-load/max ceilings.** Several high-torque-density models are too slow for 8 rad/s at the output:
    - GIM8108-48: 4.2 rad/s
    - AKH70-48: 3.7 rad/s
    - GIM8108-36: 6.3 rad/s
    - GIM6010-48: 7.3 rad/s
    - AK80-64: 7.9 rad/s at 48 V
    - X10-100: 5.6 rad/s
    - LK MG8010-i36 is marginal at 8.4 rad/s.
    - The "cheapest per N·m" leaders are therefore mostly speed-limited. See ranking 3 in §1b for models that meet ≥8 rad/s.

#### India availability and scope
13. **India availability is thin.**
    - Robu.in returned a Cloudflare 403 and was not checked.
    - The shared web-search budget ran out mid-task, so there were no further Indian reseller searches.
    - ThinkRobotics search (suggest.json) found none of these brands.
    - Robokits lists only a CubeMars frameless R60.
    - SteadyWin clearly ships to India (a store line item).
    - All leads are (U) and need a follow-up check.
14. **Not covered in detail:**
    - SteadyWin GIM3505/3510/4305/4310-40/4315-40/6010-6/8108-6/8115-6/8115-36 and WGG (prices only).
    - LK MG4005E-i10 and non-E MG6010/MG8008.
    - MyActuator RH/CEM/RMD-H/L.
    - CubeMars legacy V1/V2 AK variants (notes only).

#### Tool side effects
15. WebFetch automatically cached the fetched PDFs and images in the Claude tool-results folder (C:\Users\testi\.claude\projects\…\tool-results\). I did not save anything else outside the allowed paths. My temporary curl/HTML/JSON files and generator scripts are in scratchpad\r2\s1b\.

## 2. Bus servos for the upper body and small joints (Feetech, ROBOTIS Dynamixel, Hiwonder)


**Scope:** smart bus servos from Feetech (STS/HLS/SCS TTL and SM RS-485), ROBOTIS DYNAMIXEL X-series and Hiwonder (LX/HTD/HTS/HX). The target is JX1: height ~1.2 m, mass 20–30 kg, low cost, built in India. Its small joints (elbow, wrist, neck, possibly shoulder) need about **3–15 N·m peak**.
**Research date:** 2026-09-24. All official pages were read on this date with curl (desktop UA) or WebFetch. No browser, logins or forms were used, and I made no binary downloads myself. The harness did auto-save one PDF (see §4).

**Labels:** **[V] VERIFIED** means read today on the manufacturer's own site, official e-manual or official store. **[E] ESTIMATED** means derived by me, with the arithmetic shown in §1b. **[U] UNVERIFIED** means a reseller, forum, third-party test or secondary claim.
Conversion: **1 kg·cm = 0.0980665 N·m**. Speed: rpm = 60°/t × 60 s ÷ 360° = **10 ÷ t**, where t is seconds per 60°. There were no current CNY prices to convert. The only CNY figure is Feetech's 2020 launch price of ¥99, which is ≈ $13.94 at 1 USD = 7.1 CNY [E] and is shown only for context.
**Price basis for the USD/N·m columns:**
- Dynamixel uses robotis.us, ROBOTIS's US store [V]. The prices look like round list prices plus about 15%, e.g. $89.90 × 1.15 = $103.39. That is my hypothesis only [U].
- Hiwonder uses hiwonder.com, the official Shopify store [V].
- **Feetech's official stores could not be read.** The AliExpress "Feetech Official Store" (id 1101516264) and the Feetech Taobao shops linked from feetech.cn render prices with JavaScript. Alibaba returned a bot-challenge page, which was **not** bypassed. So every current Feetech price here is a **reseller price [U]**. I used the lowest one found and name the reseller.
- The only official Feetech price is the 2020 STS3215 launch price: $15 overseas, ¥99 domestic.

**Rated/continuous torque:**
- **Feetech publishes a rated torque for nearly every model [V].** STS/SCS/SM rated is ≈ 1/3 of stall. HLS "rated load" is ≈ 1/4 of stall.
- **ROBOTIS publishes no rated torque in its e-manual.** Its US store lists an "Estimated rated torque … calculated at 20% of stall torque". I show that number as published by ROBOTIS, but it is itself an estimate.
- **Hiwonder publishes no rated torque.** The exceptions are HX-65HM (a published "rated" value at 77% of stall, which is implausible), HX-35H/HX-35HM ("rotation torque") and HX-08LC ("dynamic torque"). For the others I give 1/5–1/3 of stall [E].
- **2-axis units** (2XL430, 2XC430): stall torque is per axis. Price and mass are for the whole 2-axis unit, and the density and $/N·m columns use 2 × per-axis torque.

### 0. Summary and best-value picks for 3–15 N·m joints (details in §1–§4)

- **Cheapest per stall N·m with an official price: Hiwonder.**
  - HTD-85H: 8.34 N·m @11.1 V, 153 g, $39.99 → **$4.80/N·m**, 54.5 N·m/kg.
  - HTD-45H: 4.41 N·m @11.1 V, 64 g, $24.99 → **$5.66/N·m**, 69.0 N·m/kg.
  - HX-35H: 3.43 N·m, 52 g, $18.99 → $5.53/N·m.
  - Caveats: potentiometer feedback limited to 240° (except the HX-..HM models, which have a 12-bit magnetic encoder over 360°), 115200 baud, no published gear ratio, no rated torque, and no independent test data found.
  - Magnetic-encoder options: **HX-65HM** (6.37 N·m @12.6 V, 143.5 g, $49.99 → $7.84/N·m) and **HX-35HM** (3.43 N·m, $35.99).
- **Best documented value: Feetech.** Feetech publishes rated torque and current, uses 12-bit magnetic encoders and runs at up to 1 Mbps.
  - STS3250: 4.90 N·m stall / 1.57 N·m rated @12 V, 74.5 g → 65.8 N·m/kg. About $43 [U] → $8.77 per stall N·m and $27.40 per rated N·m.
  - STS3095: 10.30 N·m stall / 3.43 N·m rated @8.4 V, 194.5 g, about $133 [U] → $12.92/N·m.
  - SM105B (RS-485, brushless): 14.71 N·m stall / 4.90 N·m rated, 200 g → **73.5 N·m/kg**. About $188 [U] → $12.78/N·m. The voltage for the torque figures is not stated.
  - SM80BL (RS-485, brushless): 7.85 N·m, 97.5 g → **80.5 N·m/kg**, the densest model inside the 3–15 N·m band. $185 [U]. (Outside the band, STS3200 at 19.6 N·m reaches 93.4 N·m/kg.)
  - SM70BL: 6.86 N·m @24 V, 91.6 g → 74.9 N·m/kg. No price found.
  - HLS "constant-force" models (current/torque mode): HLS3950/3955/3960, 4.9–6.6 N·m at about $83–116 [U]. They cost more per N·m but are the only Feetech line with explicit torque control.
  - STS3215 (the 12 V version is 2.94 N·m, $15.99 [U]) is **below the 3 N·m band**. It fits a neck or wrist only.
- **Dynamixel costs about 5–20× more per stall N·m [E], and small X-series units cannot reach 3 N·m.** For example, XM540-W270 at $45.56 is 9.5× HTD-85H's $4.80, and XM430-W350 at $75.70 is 8.6× STS3250's $8.77.
  - Only XM430-W210/W350 (3.0/4.1 N·m, $310.39) and the X540 family (7.1–10.6 N·m, $482.89–$620.89) reach the band.
  - The best Dynamixel value is XM540-W270 at $45.56 per stall N·m.
  - XC330, XC430, 2XC430 and XL430 (0.6–1.9 N·m) are toddler-scale. ToddlerBot, which uses them, is 0.56 m and 3.4 kg.
- **Size to the continuous rating, not stall.** Independent tests [U] show the STS3250 reaching its 70 °C protection in about 8 min at 40% of stall. ToddlerBot's system-identified maximum torques are 54–76% of the 12 V stall ratings (§3).

### 1. Master table

| Brand | Model (part no.) | Stall N·m (@V) | Rated/cont. N·m | V range | No-load rpm (@V) | Mass g | Dims mm | Gear (material/ratio) | Sensor (type/res/abs) | Interface/baud | Stall/rated A | Official price (USD/CNY, date) | India leads | Stall N·m/kg | USD/stall N·m | USD/rated N·m | Label(s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Feetech | STS3215 7.4V (ST-3215-C001) | 1.91 @6V (page table) / @7.4V (2020 official article) ⟨19.5 kg·cm [V]; conv [E]⟩ | 0.64 @6V ⟨6.5 kg·cm [V]; conv [E]⟩ | 6–7.4 V [V] | 42.0 @6V [E: 10÷0.238 s/60°]; 52 rpm @7.4V (2020 article 'Stall Speed') | 55 [V] | 45.2×24.7×35 [V] | Copper; 1:345 (2020 article) | 12-bit magnetic, 4096/360°, absolute single-turn (±7-turn mode, turns lost at power-off) | TTL half-duplex async, 38.4 kbps–1 Mbps; Feetech STS protocol | Stall 2.0 A @6V; rated n/p [V] | Official: $15 / ¥99 launch price (2020-05-13, dated) [V]; today reseller WowRobo $15.99, Seeed $20.00, ZennixTek $22 [U] | Evelta (STS3215 7.4V listing); ThinkRobotics (SO-101 kits) [U, search only] | 34.8 [E] | 8.36 [E] | 25.09 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E; NOTE: Page conflict: 16.5 kg·cm@6V on listing; table says aluminium/coreless vs text plastic/core motor |
| Feetech | STS3215 12V (ST-3215-C018) | 2.94 @12V ⟨30 kg·cm [V]; conv [E]⟩ | 0.98 @12V ⟨10 kg·cm [V]; conv [E]⟩ | 4–14 V [V] | 45.0 @12V [E: 10÷0.222 s/60°] | 55 [V] | 45.2×24.7×35 [V] | Steel; 1:345 [U: Seeed wiki/Robo9] | 12-bit magnetic, 4096/360°, absolute | TTL half-duplex, 38.4 kbps–1 Mbps | Stall 2.7 A @12V; no-load 0.18 A [V] | Official n/a; WowRobo $15.99, ZennixTek $25 [U] (2026-09-24) | Evelta (STS3215 7.4V listing); ThinkRobotics (SO-101 kits) [U, search only] | 53.5 [E] | 5.44 [E] | 16.31 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | STS3235 (ST-3235-C001) | 2.94 @12V ⟨30 kg·cm [V]; conv [E]⟩ | 0.98 @12V ⟨10 kg·cm [V]; conv [E]⟩ | 6–12 V [V] | 45.0 @12V [E: 10÷0.222 s/60°] | 70.5 [V] | 45.22×24.72×35 [V] | Steel; alu case; core motor | 12-bit magnetic, 4096/360° | TTL half-duplex, 38.4 kbps–1 Mbps | Stall 2.7 A @12V [V] | Official n/a; ZennixTek $55 [U] | Evelta (Feetech brand page; model not checked) [U] | 41.7 [E] | 18.69 [E] | 56.08 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | STS3250 (ST-3250-C001) | 4.90 @12V ⟨50 kg·cm [V]; conv [E]⟩ | 1.57 @12V ⟨16 kg·cm [V]; conv [E]⟩ | 6–12 V [V] | 75.2 @12V [E: 10÷0.133 s/60°]; 77.6 rpm measured [U Robo9] | 74.5 [V] | 45.22×24.72×35 [V] | Steel; 1/345 [U reseller]; coreless | 12-bit magnetic, 4096/360° | TTL half-duplex, 38.4 kbps–1 Mbps | Stall 4.2 A @12V; no-load 0.28 A [V] | Official n/a; WowRobo $43 (C002), ZennixTek $95 (C001+bracket) [U] | Evelta (Feetech brand page; model not checked) [U] | 65.8 [E] | 8.77 [E] | 27.40 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | STS3035 (ST-3035-C001) | 3.43 @12V ⟨35 kg·cm [V]; conv [E]⟩ | 1.14 @12V ⟨11.6 kg·cm [V]; conv [E]⟩ | 9–12 V [V] | 45 @12V [V] | 62.5 [V] | 40.2×20.2×40 [V] | Copper; core motor | 12-bit magnetic (360°/4095) | TTL half-duplex, 38.4 kbps–1 Mbps | Stall 2.7 A; rated 0.9 A @12V [V] | Official n/a; ZennixTek $29 [U] | Evelta (Feetech brand page; model not checked) [U] | 54.9 [E] | 8.45 [E] | 25.49 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | STS3046 (ST-3046-C001) | 3.92 @7.4V (listing says @6V) ⟨40 kg·cm [V]; conv [E]⟩ | 1.30 @7.4V ⟨13.3 kg·cm [V]; conv [E]⟩ | 6–7.4 V [V] | 45.5 @7.4V [E: 10÷0.22 s/60°] | 89 [V] | 40×20×43.05 [V] | Steel; coreless; alu case | 12-bit magnetic, 4096/360° | TTL half-duplex, 38.4 kbps–1 Mbps | Stall 3.1 A @7.4V [V] | Official n/a; ZennixTek $90 [U] | Evelta (Feetech brand page; model not checked) [U] | 44.1 [E] | 22.94 [E] | 69.00 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | STS3025BL-40 (brushless) (ST-3025-C002) | 3.92 @12V ⟨40 kg·cm [V]; conv [E]⟩ | 0.98 @12V ⟨10 kg·cm [V]; conv [E]⟩ | 12 V [V] | 85 @12V [V] | 89 [V] | 40×20×40 [V] | Steel; brushless motor | 12-bit magnetic, 4096/360° | TTL half-duplex, 38.4 kbps–1 Mbps | Stall 4.4 A @12V [V] | Official n/a; ZennixTek $109 [U] | Evelta (Feetech brand page; model not checked) [U] | 44.1 [E] | 27.79 [E] | 111.15 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | STS3095 (ST-3095-C001) | 10.30 @8.4V ⟨105 kg·cm [V]; conv [E]⟩ | 3.43 @8.4V ⟨35 kg·cm [V]; conv [E]⟩ | 6–12 V [V] | 40.0 @8.4V [E: 10÷0.25 s/60°] | 194.5 [V] | 30×65×48 [V] | Steel; core motor; 15T spline | 12-bit magnetic, 4096/360° | TTL half-duplex, 38.4 kbps–1 Mbps | Stall 10.5 A @8.4V; no-load 0.8 A [V] | Official n/a; ZennixTek $133 (C001) / $139 (12V C002) [U] | Evelta (Feetech brand page; model not checked) [U] | 52.9 [E] | 12.92 [E] | 38.75 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | STS3120 (ST-3120-C001) | 11.77 @12V ⟨120 kg·cm [V]; conv [E]⟩ | 3.92 @12V ⟨40 kg·cm [V]; conv [E]⟩ | 9–12 V [V] | 22 @12V [V] | 210 [V] | 30×65×48 [V] | Steel; coreless | magnetic, 360° (0~4096) | TTL half-duplex, 38.4 kbps–1 Mbps | Stall 4.7 A @12V [V] | Official n/a; AIFITLAB $188 [U] | Evelta (Feetech brand page; model not checked) [U] | 56.0 [E] | 15.98 [E] | 47.93 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | STS3200 (ST-3200-C001) | 19.61 @12V ⟨200 kg·cm [V]; conv [E]⟩ | 6.54 @12V ⟨66.7 kg·cm [V]; conv [E]⟩ | 9–12 V [V] | 38 @12V [V] | 210 [V] | 30×65×48 [V] | Steel; brushless (name says coreless) | magnetic, 360° (0~4096) | TTL half-duplex, 38.4 kbps–1 Mbps | Stall 11.3 A @12V [V] | Official n/a; AIFITLAB $348 [U] | Evelta (Feetech brand page; model not checked) [U] | 93.4 [E] | 17.74 [E] | 53.20 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | STS3032 (ST-3032-C001 / -C036) | 0.44 @6V ⟨4.5 kg·cm [V]; conv [E]⟩ | 0.15 @6V ⟨1.5 kg·cm [V]; conv [E]⟩ | 4.8–6 V [V] | 111.1 @6V [E: 10÷0.09 s/60°] | 20 [V] | 32×12×27.5 (listing C001: 23.2×12.1×28.5) [V] | Metal (C001) / copper+steel (C036); coreless | 12-bit magnetic per text; C001 table says 'Potentiometer(360°/4096)' (conflict) | TTL half-duplex, 38.4 kbps–1 Mbps | Stall 1.2 A @6V [V] | Official n/a; ZennixTek $39 [U] | Evelta (Feetech brand page; model not checked) [U] | 22.1 [E] | 88.38 [E] | 265.13 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | HLS3930 (HL-3930-C001) | 3.43 @12V ⟨35 kg·cm [V]; conv [E]⟩ | 0.85 (rated load, 0.8 A) ⟨8.7 kg·cm [V]; conv [E]⟩ | 9–12.6 V [V] | 45 @12V [V] | 70.5 [V] | 45.22×24.72×35 [V] | Steel 1/345; core motor | 12-bit magnetic, 4096/360° (0.088°) | TTL half-duplex, 38.4 kbps–1 Mbps (default 1 Mbps); torque/current mode | Stall 2.8 A; rated 0.8 A @12V [V] | Official n/a; ZennixTek $75 [U] | Evelta (Feetech brand page; model not checked) [U] | 48.7 [E] | 21.85 [E] | 87.91 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | HLS3935 (HL-3935-C001) | 3.43 @12V ⟨35 kg·cm [V]; conv [E]⟩ | 0.83 (rated load, 0.8 A) ⟨8.5 kg·cm [V]; conv [E]⟩ | 9–12.6 V [V] | 85 @12V [V] | 85 [V] | 40×20×40 [V] | Steel 1/378; coreless | 12-bit magnetic, 4096/360° (0.088°) | TTL half-duplex, 38.4 kbps–1 Mbps (default 1 Mbps); torque/current mode | Stall 3.1 A; rated 0.8 A @12V [V] | Official n/a; ZennixTek $89 [U] | Evelta (Feetech brand page; model not checked) [U] | 40.4 [E] | 25.93 [E] | 106.77 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | HLS3950 (HL-3950-C001) | 4.90 @12V ⟨50 kg·cm [V]; conv [E]⟩ | 1.23 (rated load, 0.6 A) ⟨12.5 kg·cm [V]; conv [E]⟩ | 9–12.6 V [V] | 75 @12V [V] | 74.5 [V] | 45.22×24.72×35 [V] | Steel 1/345; coreless | 12-bit magnetic, 4096/360° (0.088°) | TTL half-duplex, 38.4 kbps–1 Mbps (default 1 Mbps); torque/current mode | Stall 2.4 A; rated 0.6 A @12V [V] | Official n/a; ZennixTek $83 [U] | Evelta (Feetech brand page; model not checked) [U] | 65.8 [E] | 16.93 [E] | 67.71 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E; NOTE: Listing speed 0.117 s/60° vs detail 75 rpm |
| Feetech | HLS3955 (HL-3955-C001) | 5.39 @12V ⟨55 kg·cm [V]; conv [E]⟩ | 1.32 (rated load, 0.8 A) ⟨13.5 kg·cm [V]; conv [E]⟩ | 9–12.6 V [V] | 55 @12V [V] | 85 [V] | 40×20×40 [V] | Steel 1/378; coreless | 12-bit magnetic, 4096/360° (0.088°) | TTL half-duplex, 38.4 kbps–1 Mbps (default 1 Mbps); torque/current mode | Stall 3.0 A; rated 0.8 A @12V [V] | Official n/a; ZennixTek $89 [U] | Evelta (Feetech brand page; model not checked) [U] | 63.5 [E] | 16.50 [E] | 67.23 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | HLS3960 (HL-3960-C001) | 6.55 @12V (listing: 60) ⟨66.8 kg·cm [V]; conv [E]⟩ | 2.26 (rated load, 1.5 A) ⟨23 kg·cm [V]; conv [E]⟩ | 9–12 V [V] | 60 @12V [V] | 103.2 [V] | 45×24.4×35.5 [V] | Metal 1/358; backlash ≤0.5°; coreless | 12-bit magnetic, 4096/360° (0.088°) | TTL half-duplex, 38.4 kbps–1 Mbps (default 1 Mbps); torque/current mode | Stall 4.5 A; rated 1.5 A @12V [V] | Official n/a; AIFITLAB $116, ZennixTek $129 [U] | Evelta (Feetech brand page; model not checked) [U] | 63.5 [E] | 17.71 [E] | 51.43 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E; NOTE: Listing 60 kg·cm & 0.137 s/60° vs detail 66.8 & 60 rpm |
| Feetech | HLS3625 (HL-3625-C001) | 2.45 @7.4V ⟨25 kg·cm [V]; conv [E]⟩ | 0.61 (rated load, 0.75 A) ⟨6.2 kg·cm [V]; conv [E]⟩ | 5–8.4 V [V] | 52 @7.4V [V] | 55 [V] | 45.2×24.7×35 [V] | Copper 1/345; core; PA66+GF case | 12-bit magnetic, 4096/360° (0.088°) | TTL half-duplex, 38.4 kbps–1 Mbps (default 1 Mbps); torque/current mode | Stall 3.0 A; rated 0.75 A @7.4V [V] | Official n/a; ZennixTek $29 [U] | Evelta (Feetech brand page; model not checked) [U] | 44.6 [E] | 11.83 [E] | 47.70 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | HLS3925 (HL-3925-C001) | 2.45 @12V ⟨25 kg·cm [V]; conv [E]⟩ | 0.47 (rated load, 0.65 A) ⟨4.8 kg·cm [V]; conv [E]⟩ | 9–12.6 V [V] | 55 @12V [V] | 61.7 [V] | 40.2×20.2×40 [V] | Copper 1/275; core | 12-bit magnetic, 4096/360° (0.088°) | TTL half-duplex, 38.4 kbps–1 Mbps (default 1 Mbps); torque/current mode | Stall 2.7 A; rated 0.65 A @12V [V] | Official n/a; ZennixTek $33 [U] | Evelta (Feetech brand page; model not checked) [U] | 39.7 [E] | 13.46 [E] | 70.11 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | HLS3620 (HL-3620-C001/-C002) | 2.50 @8.4V ⟨25.5 kg·cm [V]; conv [E]⟩ | 0.63 (rated load, 0.85 A) ⟨6.4 kg·cm [V]; conv [E]⟩ | 6–8.4 V [V] | 74 @8.4V [V] | 61.7 [V] | 40.2×20.2×40 [V] | Copper 1/275; core | 12-bit magnetic, 4096/360° (0.088°) | TTL half-duplex, 38.4 kbps–1 Mbps (default 1 Mbps); torque/current mode | Stall 3.3 A; rated 0.85 A @8.4V [V] | Official n/a; ZennixTek $39 [U] | Evelta (Feetech brand page; model not checked) [U] | 40.5 [E] | 15.60 [E] | 62.14 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | HLS3640 (HL-3640-C001) | 3.92 @7.4V ⟨40 kg·cm [V]; conv [E]⟩ | 0.98 (rated load, 0.85 A) ⟨10 kg·cm [V]; conv [E]⟩ | 5–8.4 V [V] | 45 @7.4V [V] | 89 [V] | 40×20×43.05 [V] | Steel 1/378; coreless | 12-bit magnetic, 4096/360° (0.088°) | TTL half-duplex, 38.4 kbps–1 Mbps (default 1 Mbps); torque/current mode | Stall 3.3 A; rated 0.85 A @7.4V [V] | Official n/a; ZennixTek $93 [U] | Evelta (Feetech brand page; model not checked) [U] | 44.1 [E] | 23.71 [E] | 94.83 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | HLS3915 (HL-3915-C001) | 1.39 @12V ⟨14.2 kg·cm [V]; conv [E]⟩ | 0.44 (rated load, 0.5 A) ⟨4.5 kg·cm [V]; conv [E]⟩ | 4–14 V [V] | 100 @12V [V] | 35.8 [V] | 20×34×23 [V] | Metal 1/320; coreless; alu | 12-bit magnetic, 4096/360° (0.088°) | TTL half-duplex, 38.4 kbps–1 Mbps (default 1 Mbps); torque/current mode | Stall 1.5 A; rated 0.5 A @12V [V] | Official n/a; ZennixTek $49 [U] | Evelta (Feetech brand page; model not checked) [U] | 38.9 [E] | 35.19 [E] | 111.04 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | HLS2915 (HL-2915-C001) | 1.39 @12V ⟨14.2 kg·cm [V]; conv [E]⟩ | 0.44 (rated load, 0.5 A) ⟨4.5 kg·cm [V]; conv [E]⟩ | 9–14 V [V] | 110 @12V [V] | 27.8 [V] | 34×20×23 [V] | Metal 1/320; backlash ≤1°; PA+fiber | 12-bit magnetic, 4096/360° (0.088°) | TTL half-duplex, 38.4 kbps–1 Mbps (default 1 Mbps); torque/current mode | Stall 1.5 A; rated 0.5 A @12V [V] | Official n/a; AIFITLAB $38 [U] | Evelta (Feetech brand page; model not checked) [U] | 50.1 [E] | 27.29 [E] | 86.11 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | SCS0009 (SC-0090-C001) | 0.23 @6V ⟨2.3 kg·cm [V]; conv [E]⟩ | 0.07 @6V ⟨0.7 kg·cm [V]; conv [E]⟩ | 4–7.4 V [V] | 100.0 @6V [E: 10÷0.1 s/60°] | 13.2 [V] | 23.2×12.1×25.25 [V] | Copper+steel; core; no bearing | Potentiometer, 300°/1024 (0.293°) | TTL half-duplex, 38.4 kbps–1 Mbps | Stall 1.0 A @6V [V] | Official n/a; ZennixTek $13 [U] | Evelta (Feetech brand page; model not checked) [U] | 17.1 [E] | 57.64 [E] | 189.38 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E; NOTE: Listing: 0.07 s/60°, 12.5 g |
| Feetech | SCS15 (SC-1500-C022) | 1.53 @7.4V (listing: @6V) ⟨15.6 kg·cm [V]; conv [E]⟩ | 0.51 @7.4V ⟨5.2 kg·cm [V]; conv [E]⟩ | 4–8.4 V [V] | 64.1 @7.4V [E: 10÷0.156 s/60°] | 58.2 [V] | 40.2×20.2×40 [V] | Copper; core | Potentiometer, 220°/1023 (0.215°) | TTL half-duplex, 38.4 kbps–1 Mbps | Stall 2.5 A @7.4V [V] | Official n/a; ZennixTek $19 [U] | Evelta (Feetech brand page; model not checked) [U] | 26.3 [E] | 12.42 [E] | 37.26 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | SCS215 (SCS225 = dual-axis variant, reseller-only) (SC-2150-C001) | 1.86 @7.4V ⟨19 kg·cm [V]; conv [E]⟩ | 0.62 @7.4V ⟨6.3 kg·cm [V]; conv [E]⟩ | 4–7.4 V [V] | 52.1 @7.4V [E: 10÷0.192 s/60°] | 55 [V] | 45.23×24.73×35 [V] | Copper; core; PA+GF | Potentiometer, 300° (0.322°/step) | TTL half-duplex, 38.4 kbps–1 Mbps | Stall 2.5 A @6V [V] | Official n/a; ZennixTek $29 [U] | Evelta (Feetech brand page; model not checked) [U] | 33.9 [E] | 15.56 [E] | 46.94 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | SCS40 (SC-4000-C001) | 4.17 @8.4V (listing: 38.6@6V) ⟨42.5 kg·cm [V]; conv [E]⟩ | 1.26 @8.4V ⟨12.8 kg·cm [V]; conv [E]⟩ | 6–8.4 V [V] | 83 @8.4V [V] | 70 [V] | 40.5×20.5×36 [V] | Metal; coreless; ABS case | Potentiometer, 300°/1024 | TTL half-duplex, 38.4 kbps–1 Mbps | Stall 1.8 A @8.4V [V] | Official n/a; ZennixTek $89 [U] | Evelta (Feetech brand page; model not checked) [U] | 59.5 [E] | 21.35 [E] | 70.90 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | SCS 7.4V 40kg (SC-4600) (SC-4600-C001) | 3.97 @7.4V ⟨40.5 kg·cm [V]; conv [E]⟩ | 1.32 @7.4V (unit missing on page) ⟨13.5 kg·cm [V]; conv [E]⟩ | 6–7.4 V [V] | 45.5 @7.4V [E: 10÷0.22 s/60°] | 89 [V] | 40×20×43.05 [V] | Steel; coreless; alu case | Potentiometer (text), 300°/1024 (0.293°) | TTL half-duplex, 38.4 kbps–1 Mbps | Stall '4.4mA' (page typo) [V] | Not found | Evelta (Feetech brand page; model not checked) [U] | 44.6 [E] | — | — | Specs V (feetechrc.com); N·m conv E; price not found; derived E |
| Feetech | SM40BL (SM-40BL-C001) | 3.92 @12V ⟨40 kg·cm [V]; conv [E]⟩ | 1.18 ≤ @12V ⟨12 kg·cm [V]; conv [E]⟩ | 12 V [V] | 65 @12V [V] | 100 [V] | 46.5×28.5×34 [V] | Steel 353:1; brushless | 12-bit magnetic, 4096/360° | RS-485 half-duplex, 38.4 kbps–1 Mbps | Stall 2.5 A; rated '800mm≤' (typo) [V] | Official n/a; ZennixTek $139 [U] | Evelta (Feetech brand page; model not checked) [U] | 39.2 [E] | 35.44 [E] | 118.12 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | SM45BL (SM-45BL-C001) | 4.41 @24V ⟨45 kg·cm [V]; conv [E]⟩ | 1.47 @24V ⟨15 kg·cm [V]; conv [E]⟩ | 24 V (text says 12V) [V] | 70 @24V (listing: 35) [V] | 100 [V] | 46.5×28.5×34 [V] | Steel 353:1; brushless | 12-bit magnetic, 4096/360° | RS-485 half-duplex, 38.4 kbps–1 Mbps | Stall 2.3 A @24V [V] | Official n/a; ZennixTek $139 [U] | Evelta (Feetech brand page; model not checked) [U] | 44.1 [E] | 31.50 [E] | 94.49 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E; NOTE: Listing 0.285 s/60° 35 RPM vs detail 0.142 s/60° 70 RPM |
| Feetech | SM60CL (SM-60CL-C001) | 5.88 @12V ⟨60 kg·cm [V]; conv [E]⟩ | 1.96 @12V ⟨20 kg·cm [V]; conv [E]⟩ | 12 V [V] | 35 @12V [V] | 180 [V] | 62×34×40 [V] | Steel; coreless | 12-bit magnetic, 4096/360° | RS-485 half-duplex, 38.4 kbps–1 Mbps | Stall 2.6 A; rated ≤0.8 A [V] | Official n/a; ZennixTek $165 [U] | Evelta (Feetech brand page; model not checked) [U] | 32.7 [E] | 28.04 [E] | 84.13 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | SM70BL (SM-70BL-C001) | 6.86 @24V (listing) ⟨70 kg·cm [V]; conv [E]⟩ | 1.72 @24V ⟨17.5 kg·cm [V]; conv [E]⟩ | 16.8–25.2 V [V] | 78 @24V [V] | 91.6 [V] | 40×20×47.8 [V] | Steel; brushless (text) | 12-bit magnetic, 4096/360° | RS-485 half-duplex, 38.4 kbps–1 Mbps | Stall 3.5 A; rated 0.87 A @24V [V] | Not found | Evelta (Feetech brand page; model not checked) [U] | 74.9 [E] | — | — | Specs V (feetechrc.com); N·m conv E; price not found; derived E |
| Feetech | SM80BL (12V) (SM-80BL-C001) | 7.85 @12V ⟨80 kg·cm [V]; conv [E]⟩ | 1.96 ≤ @12V ⟨20 kg·cm [V]; conv [E]⟩ | 12 V [V] | 62 @12V [V] | 97.5 [V] | 46.5×28.5×34 [V] | Steel; 4-pole brushless | 12-bit magnetic, 4096/360° | RS-485 half-duplex, 38.4 kbps–1 Mbps | Stall 5.9 A; rated 1.475 A [V] | Official n/a; ZennixTek $185 [U] | Evelta (Feetech brand page; model not checked) [U] | 80.5 [E] | 23.58 [E] | 94.32 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | SM8512BL (SM-8512-C001) | 8.34 @12V ⟨85 kg·cm [V]; conv [E]⟩ | 2.75 @12V ⟨28 kg·cm [V]; conv [E]⟩ | 12 V [V] | 59.9 @12V [E: 10÷0.167 s/60°] | 215 [V] | 62×34×47 [V] | Steel; brushless; 15T spline | 12-bit magnetic, 4096/360° | RS-485 half-duplex, 38.4 kbps–1 Mbps | Stall 7.9 A @12V [V] | Official n/a; ZennixTek $209 [U] | Evelta (Feetech brand page; model not checked) [U] | 38.8 [E] | 25.07 [E] | 76.11 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | SM85CL (SM-85CL-C001) | 8.34 @12V ⟨85 kg·cm [V]; conv [E]⟩ | 2.75 @12V ⟨28 kg·cm [V]; conv [E]⟩ | 12 V [V] | 37 @12V [V] | 215 [V] | 62×34×47 [V] | Steel; coreless | 12-bit magnetic, 4096/360° | RS-485 half-duplex, 38.4 kbps–1 Mbps | Stall 3.2 A @12V [V] | Official n/a; ZennixTek $209 [U] | Evelta (Feetech brand page; model not checked) [U] | 38.8 [E] | 25.07 [E] | 76.11 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | SM120BL (SM-120B-C001) | 11.77 @24V ⟨120 kg·cm [V]; conv [E]⟩ | 3.14 ≤ (rated load) ⟨32 kg·cm [V]; conv [E]⟩ | 24 V [V] | 50 @24V [V] | 485 [V] | 78×43×65.5 [V] | Steel 232:1; brushless; 7075 alu | 12-bit magnetic, 4096/360° | RS-485 half-duplex, 38.4 kbps–1 Mbps | Stall 4 A; rated ≤1 A [V] | Official n/a; ZennixTek $379 [U] | Evelta (Feetech brand page; model not checked) [U] | 24.3 [E] | 32.21 [E] | 120.77 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| Feetech | SM105B (SM-105B-C002 (-C001 = 12V)) | 14.71 (V not stated) ⟨150 kg·cm [V]; conv [E]⟩ | 4.90 (V not stated) ⟨50 kg·cm [V]; conv [E]⟩ | 9–24 V [V] | 60  [V] | 200 [V] | 58.5×33.5×44 [V] | Steel; backlash ≤0.5°; brushless | 12-bit magnetic, 4096/360° | RS-485 half-duplex, 38.4 kbps–1 Mbps | Stall 6.3 A [V] | Official n/a; AIFITLAB $188 [U] | Evelta (Feetech brand page; model not checked) [U] | 73.5 [E] | 12.78 [E] | 38.34 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E; NOTE: Torque voltage not stated on page read |
| Feetech | SM160B (SM-160B-C001) | 15.69 @24V ⟨160 kg·cm [V]; conv [E]⟩ | 3.92 @24V ⟨40 kg·cm [V]; conv [E]⟩ | 16.8–25.2 V [V] | 55.2 @24V [E: 10÷0.181 s/60°] | 211 [V] | 62×34×47 [V] | Steel; backlash ≤0.5°; 4-pole brushless | 12-bit magnetic, 4096/360° | RS-485 half-duplex, 38.4 kbps–1 Mbps | Stall 9 A @24V [V] | Official n/a; AIFITLAB $385 [U] | Evelta (Feetech brand page; model not checked) [U] | 74.4 [E] | 24.54 [E] | 98.15 [E] | Specs V (feetechrc.com); N·m conv E; price U (reseller); derived E |
| ROBOTIS | XC330-M181-T | 0.60 @5.0V [V] | 0.12 (robotis.us: 20% of stall) [V as published; itself an estimate] | 3.7–6.0 V (rec 5.0) [V] | 129 @5V [V] | 23 [V] | 20×34×26 [V] | Full metal 180.62:1; coreless | AS5601 contactless abs. 12-bit, 360° | TTL 3.3V (5V-tol.), 9.6k–4 Mbps; Protocol 2.0 (+SBUS/iBUS/RC-PWM) | 1.80 A @5V [V] | $103.39 robotis.us (2026-09-24) | MG Super Labs (ROBOTIS India reseller; model not checked) [U] | 26.1 [E] | 172.32 [E] | 861.58 [E] | Specs V (e-manual); rated = robotis.us published 20% estimate; price V (robotis.us); derived E |
| ROBOTIS | XC330-M288-T | 0.93 @5.0V [V] | 0.19 (robotis.us: 20% of stall) [V as published; itself an estimate] | 3.7–6.0 V (rec 5.0) [V] | 81 @5V (store: 65) [V] | 23 [V] | 20×34×26 [V] | Full metal 288.35:1; coreless | AS5601 contactless abs. 12-bit, 360° | TTL 3.3V (5V-tol.), 9.6k–4 Mbps; Protocol 2.0 | 1.80 A @5V [V] | $103.39 robotis.us (2026-09-24) | MG Super Labs (ROBOTIS India reseller; model not checked) [U] | 40.4 [E] | 111.17 [E] | 555.86 [E] | Specs V (e-manual); rated = robotis.us published 20% estimate; price V (robotis.us); derived E |
| ROBOTIS | XC330-T181-T | 0.76 @11.1V (0.80@12V) [V] | 0.15 (robotis.us: 20% of stall) [V as published; itself an estimate] | 6.5–12 V (rec 11.1) [V] | 104 @11.1V [V] | 23 [V] | 20×34×26 [V] | Full metal 180.62:1; coreless | AS5601 contactless abs. 12-bit, 360° | TTL 5V, 9.6k–4 Mbps; Protocol 2.0 | 0.80 A @11.1V [V] | $103.39 robotis.us (2026-09-24) | MG Super Labs (ROBOTIS India reseller; model not checked) [U] | 33.0 [E] | 136.04 [E] | 680.20 [E] | Specs V (e-manual); rated = robotis.us published 20% estimate; price V (robotis.us); derived E |
| ROBOTIS | XC330-T288-T | 0.92 @11.1V (1.00@12V) [V] | 0.18 (robotis.us: 20% of stall) [V as published; itself an estimate] | 6.5–12 V (rec 11.1) [V] | 65 @11.1V [V] | 23 [V] | 20×34×26 [V] | Full metal 288.35:1; coreless | AS5601 contactless abs. 12-bit, 360° | TTL 5V, 9.6k–4 Mbps; Protocol 2.0 | 0.80 A @11.1V [V] | $103.39 robotis.us (2026-09-24) | MG Super Labs (ROBOTIS India reseller; model not checked) [U] | 40.0 [E] | 112.38 [E] | 561.90 [E] | Specs V (e-manual); rated = robotis.us published 20% estimate; price V (robotis.us); derived E |
| ROBOTIS | XL330-M077-T (no XC330-M077 exists) | 0.21 @5.0V [V] | n/p; 1/5–1/3 stall = 0.04–0.07 [E] | 3.7–6.0 V [V] | 383 @5V [V] | 18 [V] | 20×34×26 [V] | Plastic 77.5:1; cored | AS5601 contactless abs. 12-bit, 360° | TTL 3.3V, 9.6k–4 Mbps; Protocol 2.0 | 1.47 A @5V [V] | $27.49 robotis.us (2026-09-24) | MG Super Labs (ROBOTIS India reseller; model not checked) [U] | 11.9 [E] | 127.86 [E] | 383.58–639.30 (on 1/3–1/5 stall) [E] | Specs V (e-manual); rated E (1/5–1/3 stall); price V (robotis.us); derived E |
| ROBOTIS | XL430-W250-T | 1.40 @11.1V (1.5@12V) [V] | 0.28 (robotis.us: 20% of stall) [V as published; itself an estimate] | 6.5–12 V (rec 11.1) [V] | 57 @11.1V [V] | 57.2 [V] | 28.5×46.5×34 [V] | Engineering plastic 258.5:1; cored | AS5601 contactless abs. 12-bit, 360° | TTL 5V, 9.6k–4.5 Mbps; Protocol 2.0/1.0 | 1.3 A @11.1V [V] | $27.50 robotis.us ('New pricing: Effective June 20th') (2026-09-24) | MG Super Labs (mgsuperlabs.co.in/mgsl.in); Thingbits (XL430) [U, search only] | 24.5 [E] | 19.64 [E] | 98.21 [E] | Specs V (e-manual); rated = robotis.us published 20% estimate; price V (robotis.us); derived E; NOTE: Store lists 65 g vs e-manual 57.2 g |
| ROBOTIS | 2XL430-W250-T (2 axes) | 1.40 @11.1V per axis [V] | 0.28 (robotis.us: 20% of stall) [V as published; itself an estimate] | 6.5–12 V (rec 11.1) [V] | 57 @11.1V [V] | 98.2 [V] | 36×46.5×36 [V] | Full metal 257.4:1; cored | AS5601 contactless abs. 12-bit, 360° | TTL, 9.6k–4.5 Mbps; Protocol 2.0 | 1.3 A @11.1V [V] | $149.39 robotis.us (2026-09-24) | MG Super Labs (mgsuperlabs.co.in/mgsl.in); Thingbits (XL430) [U, search only] | 28.5 [E] | 53.35 [E] | 266.77 [E] | Specs V (e-manual); rated = robotis.us published 20% estimate; price V (robotis.us); derived E |
| ROBOTIS | XC430-W150-T (=T150BB) | 1.60 @12V (1.4@11.1V) [V] | 0.32 (robotis.us: 20% of stall) [V as published; itself an estimate] | 6.5–14.8 V (rec 12) [V] | 106 @12V [V] | 65 [V] | 28.5×46.5×34 [V] | Full metal 159.59:1; coreless | AS5601 contactless abs. 12-bit, 360° | TTL, 9.6k–4.5 Mbps; Protocol 2.0/1.0 | 1.4 A @12V [V] | $137.89 robotis.us (2026-09-24) | MG Super Labs (ROBOTIS India reseller; model not checked) [U] | 24.6 [E] | 86.18 [E] | 430.91 [E] | Specs V (e-manual); rated = robotis.us published 20% estimate; price V (robotis.us); derived E |
| ROBOTIS | XC430-W240-T (=T240BB) | 1.90 @12V (1.7@11.1V) [V] | 0.38 (robotis.us: 20% of stall) [V as published; itself an estimate] | 6.5–14.8 V (rec 12) [V] | 70 @12V [V] | 65 [V] | 28.5×46.5×34 [V] | Full metal 245.22:1; coreless | AS5601 contactless abs. 12-bit, 360° | TTL, 9.6k–4.5 Mbps; Protocol 2.0/1.0 | 1.4 A @12V [V] | $137.89 robotis.us (2026-09-24) | MG Super Labs (ROBOTIS India reseller; model not checked) [U] | 29.2 [E] | 72.57 [E] | 362.87 [E] | Specs V (e-manual); rated = robotis.us published 20% estimate; price V (robotis.us); derived E |
| ROBOTIS | 2XC430-W250-T (2 axes) | 1.80 @12V per axis [V] | 0.36 (ESTIMATED 20% of stall) [E] | 6.5–14.8 V (rec 12) [V] | 64 @12V [V] | 102 [V] | 36×46.5×36 [V] | Full metal 257.4:1; coreless | AS5601 contactless abs. 12-bit, 360° | TTL, 9.6k–4.5 Mbps; Protocol 2.0 | 1.4 A @12V [V] | $298.89 robotis.us (2026-09-24) | MG Super Labs (mgsuperlabs.co.in/mgsl.in); Thingbits (XL430) [U, search only] | 35.3 [E] | 83.02 [E] | 415.12 [E] | Specs V (e-manual); rated E (0.20 × stall; store value looks copied); price V (robotis.us); derived E; NOTE: Store metafields (0.32 N·m, 65 g, 28.5×46.5×34) look copied from XC430-W150 |
| ROBOTIS | XM430-W210-T/-R | 3.00 @12V (3.7@14.8V) [V] | 0.60 (robotis.us: 20% of stall) [V as published; itself an estimate] | 10–14.8 V (rec 12) [V] | 77 @12V [V] | 82 [V] | 28.5×46.5×34 [V] | Full metal 212.6:1; backlash 0.25°; coreless | AS5045 contactless abs. 12-bit, 360° | TTL (-T) or RS-485 (-R), 9.6k–4.5 Mbps; Protocol 2.0/1.0 | 2.3 A @12V [V] | $310.39 (-T) / $333.39 (-R) robotis.us (2026-09-24) | MG Super Labs (mgsuperlabs.co.in/mgsl.in); Thingbits (XL430) [U, search only] | 36.6 [E] | 103.46 [E] | 517.32 [E] | Specs V (e-manual); rated = robotis.us published 20% estimate; price V (robotis.us); derived E |
| ROBOTIS | XM430-W350-T/-R | 4.10 @12V (4.8@14.8V) [V] | 0.82 (robotis.us: 20% of stall) [V as published; itself an estimate] | 10–14.8 V (rec 12) [V] | 46 @12V [V] | 82 [V] | 28.5×46.5×34 [V] | Full metal 353.5:1; backlash 0.25°; coreless | AS5045 contactless abs. 12-bit, 360° | TTL (-T) or RS-485 (-R), 9.6k–4.5 Mbps; Protocol 2.0/1.0 | 2.3 A @12V [V] | $310.39 (-T) / $333.39 (-R) robotis.us (2026-09-24) | MG Super Labs (mgsuperlabs.co.in/mgsl.in); Thingbits (XL430) [U, search only] | 50.0 [E] | 75.70 [E] | 378.52 [E] | Specs V (e-manual); rated = robotis.us published 20% estimate; price V (robotis.us); derived E |
| ROBOTIS | XH540-W150-T/-R | 7.10 @12V (8.5@14.8V) [V] | 1.42 (robotis.us: 20% of stall) [V as published; itself an estimate] | 10–14.8 V (rec 12) [V] | 70 @12V [V] | 165 [V] | 33.5×58.5×44 [V] | Full metal 152.3:1; backlash 0.25°; Maxon coreless | AS5045 contactless abs. 12-bit, 360° | TTL (-T) or RS-485 (-R), 9.6k–4.5 Mbps; Protocol 2.0/1.0 | 4.9 A @12V [V] | $620.89 (-T) / $632.39 (-R) robotis.us (2026-09-24) | MG Super Labs (ROBOTIS India reseller; model not checked) [U] | 43.0 [E] | 87.45 [E] | 437.25 [E] | Specs V (e-manual); rated = robotis.us published 20% estimate; price V (robotis.us); derived E |
| ROBOTIS | XH540-W270-T/-R | 9.90 @12V (11.7@14.8V) [V] | 1.98 (robotis.us: 20% of stall) [V as published; itself an estimate] | 10–14.8 V (rec 12) [V] | 39 @12V [V] | 165 [V] | 33.5×58.5×44 [V] | Full metal 272.5:1; backlash 0.25°; Maxon coreless | AS5045 contactless abs. 12-bit, 360° | TTL (-T) or RS-485 (-R), 9.6k–4.5 Mbps; Protocol 2.0/1.0 | 4.9 A @12V [V] | $620.89 (-T) / $632.39 (-R) robotis.us (2026-09-24) | MG Super Labs (ROBOTIS India reseller; model not checked) [U] | 60.0 [E] | 62.72 [E] | 313.58 [E] | Specs V (e-manual); rated = robotis.us published 20% estimate; price V (robotis.us); derived E |
| ROBOTIS | XM540-W150-T/-R | 7.30 @12V (8.9@14.8V) [V] | 1.46 (robotis.us: 20% of stall) [V as published; itself an estimate] | 10–14.8 V (rec 12) [V] | 53 @12V [V] | 165 [V] | 33.5×58.5×44 [V] | Full metal 152.3:1; backlash 0.25°; coreless | AS5045 contactless abs. 12-bit, 360° | TTL (-T) or RS-485 (-R), 9.6k–4.5 Mbps; Protocol 2.0/1.0 | 4.4 A @12V [V] | $482.89 (-T) / $494.39 (-R) robotis.us (2026-09-24) | MG Super Labs (ROBOTIS India reseller; model not checked) [U] | 44.2 [E] | 66.15 [E] | 330.75 [E] | Specs V (e-manual); rated = robotis.us published 20% estimate; price V (robotis.us); derived E |
| ROBOTIS | XM540-W270-T/-R | 10.60 @12V (12.9@14.8V) [V] | 2.12 (robotis.us: 20% of stall) [V as published; itself an estimate] | 10–14.8 V (rec 12) [V] | 30 @12V [V] | 165 [V] | 33.5×58.5×44 [V] | Full metal 272.5:1; backlash 0.25°; coreless | AS5045 contactless abs. 12-bit, 360° | TTL (-T) or RS-485 (-R), 9.6k–4.5 Mbps; Protocol 2.0/1.0 | 4.4 A @12V [V] | $482.89 (-T) / $494.39 (-R) robotis.us (2026-09-24) | MG Super Labs (ROBOTIS India reseller; model not checked) [U] | 64.2 [E] | 45.56 [E] | 227.78 [E] | Specs V (e-manual); rated = robotis.us published 20% estimate; price V (robotis.us); derived E |
| Hiwonder | LX-824 | 1.67 @7.4V ⟨17 kg·cm [V]; conv [E]⟩ | n/p; 1/5–1/3 stall = 0.33–0.56 [E] | 6–8.4 V [V] | 50.0 @7.4V [E: 10÷0.2 s/60°] | 57 [V] | 40×20.14×51.1 [V] | Not stated on page | Potentiometer; 0–1000 = 0–240° (0.3°) | UART single-bus (TTL half-duplex), 115200 | Stall 2.4–3 A [V] | $13.99 hiwonder.com (2026-09-24) | ThinkRobotics (Hiwonder collection); Robu.in (Hiwonder category) [U, model not checked] | 29.2 [E] | 8.39 [E] | 25.17–41.96 (on 1/3–1/5 stall) [E] | Specs V (hiwonder.com); N·m conv E; price V (hiwonder.com); rated not published → E range; derived E |
| Hiwonder | LX-824HV | 1.67 @11.1V ⟨17 kg·cm [V]; conv [E]⟩ | n/p; 1/5–1/3 stall = 0.33–0.56 [E] | 9–12.6 V [V] | 50.0 @11.1V [E: 10÷0.2 s/60°] | 57 [V] | 40×20.14×51.1 [V] | Not stated on page | Potentiometer; 0–1000 = 0–240° (0.3°) | UART single-bus (TTL half-duplex), 115200 | Stall 1.7–2 A [V] | $17.99 hiwonder.com (2026-09-24) | ThinkRobotics (Hiwonder collection); Robu.in (Hiwonder category) [U, model not checked] | 29.2 [E] | 10.79 [E] | 32.37–53.95 (on 1/3–1/5 stall) [E] | Specs V (hiwonder.com); N·m conv E; price V (hiwonder.com); rated not published → E range; derived E |
| Hiwonder | LX-224 | 1.96 @7.4V ⟨20 kg·cm [V]; conv [E]⟩ | n/p; 1/5–1/3 stall = 0.39–0.65 [E] | 6–8.4 V [V] | 50.0 @7.4V [E: 10÷0.2 s/60°] | 63 [V] | 40×20.14×51.1 [V] | Metal | Potentiometer; 0–1000 = 0–240° (0.3°) | UART single-bus (TTL half-duplex), 115200 | Stall 2.4–3 A [V] | $15.99 hiwonder.com (2026-09-24) | ThinkRobotics (Hiwonder collection); Robu.in (Hiwonder category) [U, model not checked] | 31.1 [E] | 8.15 [E] | 24.46–40.76 (on 1/3–1/5 stall) [E] | Specs V (hiwonder.com); N·m conv E; price V (hiwonder.com); rated not published → E range; derived E |
| Hiwonder | LX-224HV | 1.96 @11.1V ⟨20 kg·cm [V]; conv [E]⟩ | n/p; 1/5–1/3 stall = 0.39–0.65 [E] | 9–12.6 V [V] | 55.6 @11.1V [E: 10÷0.18 s/60°] | 62 [V] | 40×20.14×51.1 [V] | Not stated on page | Potentiometer; 0–1000 = 0–240° (0.24°) | UART single-bus (TTL half-duplex), 115200 | Stall 1.7–2 A [V] | $19.99 hiwonder.com (2026-09-24) | ThinkRobotics (Hiwonder collection); Robu.in (Hiwonder category) [U, model not checked] | 31.6 [E] | 10.19 [E] | 30.58–50.96 (on 1/3–1/5 stall) [E] | Specs V (hiwonder.com); N·m conv E; price V (hiwonder.com); rated not published → E range; derived E |
| Hiwonder | LX-225 | 2.45 @7.4V ⟨25 kg·cm [V]; conv [E]⟩ | n/p; 1/5–1/3 stall = 0.49–0.82 [E] | 6–8.4 V [V] | 50.0 @7.4V [E: 10÷0.2 s/60°] | 63 [V] | 40×20.14×51.1 [V] | Metal | Potentiometer; 0–1000 = 0–240° (0.3°) | UART single-bus (TTL half-duplex), 115200 | Stall 4 A [V] | $17.99 hiwonder.com (2026-09-24) | ThinkRobotics (Hiwonder collection); Robu.in (Hiwonder category) [U, model not checked] | 38.9 [E] | 7.34 [E] | 22.01–36.69 (on 1/3–1/5 stall) [E] | Specs V (hiwonder.com); N·m conv E; price V (hiwonder.com); rated not published → E range; derived E |
| Hiwonder | HTD-30H | 2.94 @12.6V ⟨30 kg·cm [V]; conv [E]⟩ | n/p; 1/5–1/3 stall = 0.59–0.98 [E] | 9–12.6 V [V] | 83.3 @12.6V [E: 10÷0.12 s/60°] | 63 [V] | 40.0×20.1×51.1 [V] | Metal; 'strong magnetic core motor' | Potentiometer; 0–1000 = 0–240° | UART single-bus (TTL half-duplex), 115200 | Stall 3.2 A [V] | $19.99 hiwonder.com (2026-09-24) | ThinkRobotics (Hiwonder collection); Robu.in (Hiwonder category) [U, model not checked] | 46.7 [E] | 6.79 [E] | 20.38–33.97 (on 1/3–1/5 stall) [E] | Specs V (hiwonder.com); N·m conv E; price V (hiwonder.com); rated not published → E range; derived E |
| Hiwonder | HTD-35H | 3.43 @11.1V ⟨35 kg·cm [V]; conv [E]⟩ | n/p; 1/5–1/3 stall = 0.69–1.14 [E] | 9–12.6 V [V] | 55.6 @11.1V [E: 10÷0.18 s/60°] | 64 [V] | 51.1×20.14×40 [V] | Metal; iron-core motor | Potentiometer; 0–1000 = 0–240° (0.2°) | UART single-bus (TTL half-duplex), 115200 | Stall 3 A [V] | $22.99 hiwonder.com (2026-09-24) | ThinkRobotics (Hiwonder collection); Robu.in (Hiwonder category) [U, model not checked] | 53.6 [E] | 6.70 [E] | 20.09–33.49 (on 1/3–1/5 stall) [E] | Specs V (hiwonder.com); N·m conv E; price V (hiwonder.com); rated not published → E range; derived E |
| Hiwonder | HTD-45H | 4.41 @11.1V ⟨45 kg·cm [V]; conv [E]⟩ | n/p; 1/5–1/3 stall = 0.88–1.47 [E] | 9–12.6 V [V] | 55.6 @11.1V [E: 10÷0.18 s/60°] | 64 [V] | 51.1×20.14×40 [V] | Metal | Potentiometer; 0–1000 = 0–240° (0.2°) | UART single-bus (TTL half-duplex), 115200 | Stall 3 A [V] | $24.99 hiwonder.com (2026-09-24) | ThinkRobotics (Hiwonder collection); Robu.in (Hiwonder category) [U, model not checked] | 69.0 [E] | 5.66 [E] | 16.99–28.31 (on 1/3–1/5 stall) [E] | Specs V (hiwonder.com); N·m conv E; price V (hiwonder.com); rated not published → E range; derived E |
| Hiwonder | HTD-85H | 8.34 @11.1V ⟨85 kg·cm [V]; conv [E]⟩ | n/p; 1/5–1/3 stall = 1.67–2.78 [E] | 9–14.8 V [V] | 50.0 @11.1V [E: 10÷0.2 s/60°] | 153 [V] | 65.01×30.00×62.20 [V] | Stainless steel; metal mid-case | Not stated (0–240°) | UART single-bus (TTL half-duplex), 115200 | Stall 5 A; no-load 0.4 A [V] | $39.99 hiwonder.com (2026-09-24) | ThinkRobotics (Hiwonder collection); Robu.in (Hiwonder category) [U, model not checked] | 54.5 [E] | 4.80 [E] | 14.39–23.99 (on 1/3–1/5 stall) [E] | Specs V (hiwonder.com); N·m conv E; price V (hiwonder.com); rated not published → E range; derived E |
| Hiwonder | HTS-35H | 3.43 @11.1V ⟨35 kg·cm [V]; conv [E]⟩ | n/p; 1/5–1/3 stall = 0.69–1.14 [E] | 9–12.6 V [V] | 55.6 @11.1V [E: 10÷0.18 s/60°] | 64 [V] | 40×20×40.5 [V] | Metal | Potentiometer; 0–1000 = 0–240° (0.2°) | UART single-bus (TTL half-duplex), 115200 | Stall 3 A [V] | $21.99 hiwonder.com (2026-09-24) | ThinkRobotics (Hiwonder collection); Robu.in (Hiwonder category) [U, model not checked] | 53.6 [E] | 6.41 [E] | 19.22–32.03 (on 1/3–1/5 stall) [E] | Specs V (hiwonder.com); N·m conv E; price V (hiwonder.com); rated not published → E range; derived E |
| Hiwonder | HTS-30HS | 2.94 @12V ⟨30 kg·cm [V]; conv [E]⟩ | n/p; 1/5–1/3 stall = 0.59–0.98 [E] | 9–12.6 V [V] | 100.0 @12V [E: 10÷0.1 s/60°] | 64 [V] | 40.0×20.0×40.5 [V] | Stainless steel | Potentiometer; 0–1000 = 0–240° | UART single-bus (TTL half-duplex), 115200 | Stall 3.2 A [V] | $45.99 hiwonder.com (2026-09-24) | ThinkRobotics (Hiwonder collection); Robu.in (Hiwonder category) [U, model not checked] | 46.0 [E] | 15.63 [E] | 46.90–78.16 (on 1/3–1/5 stall) [E] | Specs V (hiwonder.com); N·m conv E; price V (hiwonder.com); rated not published → E range; derived E |
| Hiwonder | HX-35H | 3.43 @11.1V ('static max') ⟨35 kg·cm [V]; conv [E]⟩ | 2.45 'rotation torque' @11.1V (not a continuous rating) ⟨25 kg·cm [V]⟩; typical 1/5–1/3 stall = 0.69–1.14 [E] | 9–12.6 V [V] | 55.6 @11.1V [E: 10÷0.18 s/60°] | 52 [V] | 45.2×24.7×35 [V] | Metal | Potentiometer; 0–1000 = 0–240° | UART single-bus (TTL half-duplex), 115200 | Stall 3 A [V] | $18.99 (compare-at $21.99) hiwonder.com (2026-09-24) | ThinkRobotics (Hiwonder collection); Robu.in (Hiwonder category) [U, model not checked] | 66.0 [E] | 5.53 [E] | 16.60–27.66 (on 1/3–1/5 stall) [E] | Specs V (hiwonder.com); N·m conv E; price V (hiwonder.com); rated V as published (non-standard term) + E range; derived E |
| Hiwonder | HX-35HM | 3.43 @11.1V ('static max') ⟨35 kg·cm [V]; conv [E]⟩ | 2.45 'rotation torque' @11.1V (not a continuous rating) ⟨25 kg·cm [V]⟩; typical 1/5–1/3 stall = 0.69–1.14 [E] | 9–12.6 V [V] | 52.6 @11.1V [E: 10÷0.19 s/60°] | 71 [V] | 45.2×24.7×35 [V] | Metal | 12-bit magnetic, 360° (control 0–1500) | UART single-bus (TTL half-duplex), 115200 | Stall 3 A [V] | $35.99 hiwonder.com (2026-09-24) | ThinkRobotics (Hiwonder collection); Robu.in (Hiwonder category) [U, model not checked] | 48.3 [E] | 10.49 [E] | 31.46–52.43 (on 1/3–1/5 stall) [E] | Specs V (hiwonder.com); N·m conv E; price V (hiwonder.com); rated V as published (non-standard term) + E range; derived E |
| Hiwonder | HX-30HM | 2.94 @11.1V ⟨30 kg·cm [V]; conv [E]⟩ | n/p; 1/5–1/3 stall = 0.59–0.98 [E] | 9–12.6 V [V] | 52.6 @11.1V [E: 10÷0.19 s/60°] | 52 [V] | 45.2×24.7×35 [V] | Not stated (table misaligned) | 12-bit magnetic, 0–4095 = 360° | UART single-bus, default 1,000,000 baud | Stall 3 A [V] | $19.99 hiwonder.com (2026-09-24) | ThinkRobotics (Hiwonder collection); Robu.in (Hiwonder category) [U, model not checked] | 56.6 [E] | 6.79 [E] | 20.38–33.97 (on 1/3–1/5 stall) [E] | Specs V (hiwonder.com); N·m conv E; price V (hiwonder.com); rated not published → E range; derived E; NOTE: Spec table rows misaligned; text copied from HX-10HM |
| Hiwonder | HX-10HM | 0.98 @11.1V ⟨10 kg·cm [V]; conv [E]⟩ | n/p; 1/5–1/3 stall = 0.20–0.33 [E] | 9–12.6 V [V] | 100.0 @11.1V [E: 10÷0.1 s/60°] | 52 [V] | 45.2×24.7×35 [V] | Not stated (table misaligned) | 12-bit magnetic, 0–4095 = 360° | UART single-bus, default 1,000,000 baud | Stall 3 A [V] | $17.99 hiwonder.com (2026-09-24) | ThinkRobotics (Hiwonder collection); Robu.in (Hiwonder category) [U, model not checked] | 18.9 [E] | 18.34 [E] | 55.03–91.72 (on 1/3–1/5 stall) [E] | Specs V (hiwonder.com); N·m conv E; price V (hiwonder.com); rated not published → E range; derived E |
| Hiwonder | HX-65HM (dual-motor) | 6.37 @12.6V (50@9.6V) ⟨65 kg·cm [V]; conv [E]⟩ | 4.90 'Rated' @12.6V as published (77% of stall; implausible) ⟨50 kg·cm [V]⟩; typical 1/5–1/3 stall = 1.27–2.12 [E] | 9–12.6 V [V] | 52.6 @11.1V [E: 10÷0.19 s/60°] | 143.5 [V] | 45×25×70 [V] | Metal; 2 motors | 12-bit magnetic, 360° (control 0–1500) | UART single-bus (TTL half-duplex), 115200 | Stall 5 A [V] | $49.99 hiwonder.com (2026-09-24) | ThinkRobotics (Hiwonder collection); Robu.in (Hiwonder category) [U, model not checked] | 44.4 [E] | 7.84 [E] | 23.53–39.21 (on 1/3–1/5 stall) [E] | Specs V (hiwonder.com); N·m conv E; price V (hiwonder.com); rated V as published (non-standard term) + E range; derived E |
| Hiwonder | HX-08LC (coreless micro) | 0.78 @7.4V ⟨8 kg·cm [V]; conv [E]⟩ | 0.29 'Dynamic torque' @7.4V ⟨3 kg·cm [V]⟩; typical 1/5–1/3 stall = 0.16–0.26 [E] | 6–8.4 V [V] | 166.7 @7.4V [E: 10÷0.06 s/60°] | 26 [V] | 23×20×38 [V] | Metal | Potentiometer; 0–1000 = 0–240° | TTL single-wire serial, 115200 | Stall ≤4 A [V] | $34.99 hiwonder.com (2026-09-24) | ThinkRobotics (Hiwonder collection); Robu.in (Hiwonder category) [U, model not checked] | 30.2 [E] | 44.60 [E] | 133.80–223.00 (on 1/3–1/5 stall) [E] | Specs V (hiwonder.com); N·m conv E; price V (hiwonder.com); rated V as published (non-standard term) + E range; derived E |

#### 1b. Arithmetic behind every ESTIMATED column (1 kg·cm = 0.0980665 N·m; rpm = 10 ÷ (s per 60°); no CNY conversions were needed except the 2020 ¥99 note)

- **Feetech STS3215 7.4V (ST-3215-C001)**: stall 19.5 kg·cm × 0.0980665 = 1.912 N·m; rated 6.5 kg·cm × 0.0980665 = 0.637 N·m; speed 10 ÷ 0.238 s/60° = 42.0 rpm; density 1.912 ÷ 0.055 kg = 34.8 N·m/kg; $15.99 ÷ 1.912 = $8.36 per stall N·m; $15.99 ÷ 0.637 = $25.09 per rated N·m; with the 2020 official launch price: $15 ÷ 1.912 = $7.84 per stall N·m; ¥99 ÷ 7.1 = $13.94
- **Feetech STS3215 12V (ST-3215-C018)**: stall 30 kg·cm × 0.0980665 = 2.942 N·m; rated 10 kg·cm × 0.0980665 = 0.981 N·m; speed 10 ÷ 0.222 s/60° = 45.0 rpm; density 2.942 ÷ 0.055 kg = 53.5 N·m/kg; $15.99 ÷ 2.942 = $5.44 per stall N·m; $15.99 ÷ 0.981 = $16.31 per rated N·m
- **Feetech STS3235 (ST-3235-C001)**: stall 30 kg·cm × 0.0980665 = 2.942 N·m; rated 10 kg·cm × 0.0980665 = 0.981 N·m; speed 10 ÷ 0.222 s/60° = 45.0 rpm; density 2.942 ÷ 0.0705 kg = 41.7 N·m/kg; $55 ÷ 2.942 = $18.69 per stall N·m; $55 ÷ 0.981 = $56.08 per rated N·m
- **Feetech STS3250 (ST-3250-C001)**: stall 50 kg·cm × 0.0980665 = 4.903 N·m; rated 16 kg·cm × 0.0980665 = 1.569 N·m; speed 10 ÷ 0.133 s/60° = 75.2 rpm; density 4.903 ÷ 0.0745 kg = 65.8 N·m/kg; $43 ÷ 4.903 = $8.77 per stall N·m; $43 ÷ 1.569 = $27.40 per rated N·m
- **Feetech STS3035 (ST-3035-C001)**: stall 35 kg·cm × 0.0980665 = 3.432 N·m; rated 11.6 kg·cm × 0.0980665 = 1.138 N·m; density 3.432 ÷ 0.0625 kg = 54.9 N·m/kg; $29 ÷ 3.432 = $8.45 per stall N·m; $29 ÷ 1.138 = $25.49 per rated N·m
- **Feetech STS3046 (ST-3046-C001)**: stall 40 kg·cm × 0.0980665 = 3.923 N·m; rated 13.3 kg·cm × 0.0980665 = 1.304 N·m; speed 10 ÷ 0.22 s/60° = 45.5 rpm; density 3.923 ÷ 0.089 kg = 44.1 N·m/kg; $90 ÷ 3.923 = $22.94 per stall N·m; $90 ÷ 1.304 = $69.00 per rated N·m
- **Feetech STS3025BL-40 (brushless) (ST-3025-C002)**: stall 40 kg·cm × 0.0980665 = 3.923 N·m; rated 10 kg·cm × 0.0980665 = 0.981 N·m; density 3.923 ÷ 0.089 kg = 44.1 N·m/kg; $109 ÷ 3.923 = $27.79 per stall N·m; $109 ÷ 0.981 = $111.15 per rated N·m
- **Feetech STS3095 (ST-3095-C001)**: stall 105 kg·cm × 0.0980665 = 10.297 N·m; rated 35 kg·cm × 0.0980665 = 3.432 N·m; speed 10 ÷ 0.25 s/60° = 40.0 rpm; density 10.297 ÷ 0.1945 kg = 52.9 N·m/kg; $133 ÷ 10.297 = $12.92 per stall N·m; $133 ÷ 3.432 = $38.75 per rated N·m
- **Feetech STS3120 (ST-3120-C001)**: stall 120 kg·cm × 0.0980665 = 11.768 N·m; rated 40 kg·cm × 0.0980665 = 3.923 N·m; density 11.768 ÷ 0.21 kg = 56.0 N·m/kg; $188 ÷ 11.768 = $15.98 per stall N·m; $188 ÷ 3.923 = $47.93 per rated N·m
- **Feetech STS3200 (ST-3200-C001)**: stall 200 kg·cm × 0.0980665 = 19.613 N·m; rated 66.7 kg·cm × 0.0980665 = 6.541 N·m; density 19.613 ÷ 0.21 kg = 93.4 N·m/kg; $348 ÷ 19.613 = $17.74 per stall N·m; $348 ÷ 6.541 = $53.20 per rated N·m
- **Feetech STS3032 (ST-3032-C001 / -C036)**: stall 4.5 kg·cm × 0.0980665 = 0.441 N·m; rated 1.5 kg·cm × 0.0980665 = 0.147 N·m; speed 10 ÷ 0.09 s/60° = 111.1 rpm; density 0.441 ÷ 0.02 kg = 22.1 N·m/kg; $39 ÷ 0.441 = $88.38 per stall N·m; $39 ÷ 0.147 = $265.13 per rated N·m
- **Feetech HLS3930 (HL-3930-C001)**: stall 35 kg·cm × 0.0980665 = 3.432 N·m; rated 8.7 kg·cm × 0.0980665 = 0.853 N·m; density 3.432 ÷ 0.0705 kg = 48.7 N·m/kg; $75 ÷ 3.432 = $21.85 per stall N·m; $75 ÷ 0.853 = $87.91 per rated N·m
- **Feetech HLS3935 (HL-3935-C001)**: stall 35 kg·cm × 0.0980665 = 3.432 N·m; rated 8.5 kg·cm × 0.0980665 = 0.834 N·m; density 3.432 ÷ 0.085 kg = 40.4 N·m/kg; $89 ÷ 3.432 = $25.93 per stall N·m; $89 ÷ 0.834 = $106.77 per rated N·m
- **Feetech HLS3950 (HL-3950-C001)**: stall 50 kg·cm × 0.0980665 = 4.903 N·m; rated 12.5 kg·cm × 0.0980665 = 1.226 N·m; density 4.903 ÷ 0.0745 kg = 65.8 N·m/kg; $83 ÷ 4.903 = $16.93 per stall N·m; $83 ÷ 1.226 = $67.71 per rated N·m
- **Feetech HLS3955 (HL-3955-C001)**: stall 55 kg·cm × 0.0980665 = 5.394 N·m; rated 13.5 kg·cm × 0.0980665 = 1.324 N·m; density 5.394 ÷ 0.085 kg = 63.5 N·m/kg; $89 ÷ 5.394 = $16.50 per stall N·m; $89 ÷ 1.324 = $67.23 per rated N·m
- **Feetech HLS3960 (HL-3960-C001)**: stall 66.8 kg·cm × 0.0980665 = 6.551 N·m; rated 23 kg·cm × 0.0980665 = 2.256 N·m; density 6.551 ÷ 0.1032 kg = 63.5 N·m/kg; $116 ÷ 6.551 = $17.71 per stall N·m; $116 ÷ 2.256 = $51.43 per rated N·m
- **Feetech HLS3625 (HL-3625-C001)**: stall 25 kg·cm × 0.0980665 = 2.452 N·m; rated 6.2 kg·cm × 0.0980665 = 0.608 N·m; density 2.452 ÷ 0.055 kg = 44.6 N·m/kg; $29 ÷ 2.452 = $11.83 per stall N·m; $29 ÷ 0.608 = $47.70 per rated N·m
- **Feetech HLS3925 (HL-3925-C001)**: stall 25 kg·cm × 0.0980665 = 2.452 N·m; rated 4.8 kg·cm × 0.0980665 = 0.471 N·m; density 2.452 ÷ 0.0617 kg = 39.7 N·m/kg; $33 ÷ 2.452 = $13.46 per stall N·m; $33 ÷ 0.471 = $70.11 per rated N·m
- **Feetech HLS3620 (HL-3620-C001/-C002)**: stall 25.5 kg·cm × 0.0980665 = 2.501 N·m; rated 6.4 kg·cm × 0.0980665 = 0.628 N·m; density 2.501 ÷ 0.0617 kg = 40.5 N·m/kg; $39 ÷ 2.501 = $15.60 per stall N·m; $39 ÷ 0.628 = $62.14 per rated N·m
- **Feetech HLS3640 (HL-3640-C001)**: stall 40 kg·cm × 0.0980665 = 3.923 N·m; rated 10 kg·cm × 0.0980665 = 0.981 N·m; density 3.923 ÷ 0.089 kg = 44.1 N·m/kg; $93 ÷ 3.923 = $23.71 per stall N·m; $93 ÷ 0.981 = $94.83 per rated N·m
- **Feetech HLS3915 (HL-3915-C001)**: stall 14.2 kg·cm × 0.0980665 = 1.393 N·m; rated 4.5 kg·cm × 0.0980665 = 0.441 N·m; density 1.393 ÷ 0.0358 kg = 38.9 N·m/kg; $49 ÷ 1.393 = $35.19 per stall N·m; $49 ÷ 0.441 = $111.04 per rated N·m
- **Feetech HLS2915 (HL-2915-C001)**: stall 14.2 kg·cm × 0.0980665 = 1.393 N·m; rated 4.5 kg·cm × 0.0980665 = 0.441 N·m; density 1.393 ÷ 0.0278 kg = 50.1 N·m/kg; $38 ÷ 1.393 = $27.29 per stall N·m; $38 ÷ 0.441 = $86.11 per rated N·m
- **Feetech SCS0009 (SC-0090-C001)**: stall 2.3 kg·cm × 0.0980665 = 0.226 N·m; rated 0.7 kg·cm × 0.0980665 = 0.069 N·m; speed 10 ÷ 0.1 s/60° = 100.0 rpm; density 0.226 ÷ 0.0132 kg = 17.1 N·m/kg; $13 ÷ 0.226 = $57.64 per stall N·m; $13 ÷ 0.069 = $189.38 per rated N·m
- **Feetech SCS15 (SC-1500-C022)**: stall 15.6 kg·cm × 0.0980665 = 1.530 N·m; rated 5.2 kg·cm × 0.0980665 = 0.510 N·m; speed 10 ÷ 0.156 s/60° = 64.1 rpm; density 1.530 ÷ 0.0582 kg = 26.3 N·m/kg; $19 ÷ 1.530 = $12.42 per stall N·m; $19 ÷ 0.510 = $37.26 per rated N·m
- **Feetech SCS215 (SCS225 = dual-axis variant, reseller-only) (SC-2150-C001)**: stall 19 kg·cm × 0.0980665 = 1.863 N·m; rated 6.3 kg·cm × 0.0980665 = 0.618 N·m; speed 10 ÷ 0.192 s/60° = 52.1 rpm; density 1.863 ÷ 0.055 kg = 33.9 N·m/kg; $29 ÷ 1.863 = $15.56 per stall N·m; $29 ÷ 0.618 = $46.94 per rated N·m
- **Feetech SCS40 (SC-4000-C001)**: stall 42.5 kg·cm × 0.0980665 = 4.168 N·m; rated 12.8 kg·cm × 0.0980665 = 1.255 N·m; density 4.168 ÷ 0.07 kg = 59.5 N·m/kg; $89 ÷ 4.168 = $21.35 per stall N·m; $89 ÷ 1.255 = $70.90 per rated N·m
- **Feetech SCS 7.4V 40kg (SC-4600) (SC-4600-C001)**: stall 40.5 kg·cm × 0.0980665 = 3.972 N·m; rated 13.5 kg·cm (unit assumed kg·cm; missing on page) × 0.0980665 = 1.324 N·m; speed 10 ÷ 0.22 s/60° = 45.5 rpm; density 3.972 ÷ 0.089 kg = 44.6 N·m/kg
- **Feetech SM40BL (SM-40BL-C001)**: stall 40 kg·cm × 0.0980665 = 3.923 N·m; rated 12 kg·cm × 0.0980665 = 1.177 N·m; density 3.923 ÷ 0.1 kg = 39.2 N·m/kg; $139 ÷ 3.923 = $35.44 per stall N·m; $139 ÷ 1.177 = $118.12 per rated N·m
- **Feetech SM45BL (SM-45BL-C001)**: stall 45 kg·cm × 0.0980665 = 4.413 N·m; rated 15 kg·cm × 0.0980665 = 1.471 N·m; density 4.413 ÷ 0.1 kg = 44.1 N·m/kg; $139 ÷ 4.413 = $31.50 per stall N·m; $139 ÷ 1.471 = $94.49 per rated N·m
- **Feetech SM60CL (SM-60CL-C001)**: stall 60 kg·cm × 0.0980665 = 5.884 N·m; rated 20 kg·cm × 0.0980665 = 1.961 N·m; density 5.884 ÷ 0.18 kg = 32.7 N·m/kg; $165 ÷ 5.884 = $28.04 per stall N·m; $165 ÷ 1.961 = $84.13 per rated N·m
- **Feetech SM70BL (SM-70BL-C001)**: stall 70 kg·cm × 0.0980665 = 6.865 N·m; rated 17.5 kg·cm × 0.0980665 = 1.716 N·m; density 6.865 ÷ 0.0916 kg = 74.9 N·m/kg
- **Feetech SM80BL (12V) (SM-80BL-C001)**: stall 80 kg·cm × 0.0980665 = 7.845 N·m; rated 20 kg·cm × 0.0980665 = 1.961 N·m; density 7.845 ÷ 0.0975 kg = 80.5 N·m/kg; $185 ÷ 7.845 = $23.58 per stall N·m; $185 ÷ 1.961 = $94.32 per rated N·m
- **Feetech SM8512BL (SM-8512-C001)**: stall 85 kg·cm × 0.0980665 = 8.336 N·m; rated 28 kg·cm × 0.0980665 = 2.746 N·m; speed 10 ÷ 0.167 s/60° = 59.9 rpm; density 8.336 ÷ 0.215 kg = 38.8 N·m/kg; $209 ÷ 8.336 = $25.07 per stall N·m; $209 ÷ 2.746 = $76.11 per rated N·m
- **Feetech SM85CL (SM-85CL-C001)**: stall 85 kg·cm × 0.0980665 = 8.336 N·m; rated 28 kg·cm × 0.0980665 = 2.746 N·m; density 8.336 ÷ 0.215 kg = 38.8 N·m/kg; $209 ÷ 8.336 = $25.07 per stall N·m; $209 ÷ 2.746 = $76.11 per rated N·m
- **Feetech SM120BL (SM-120B-C001)**: stall 120 kg·cm × 0.0980665 = 11.768 N·m; rated 32 kg·cm × 0.0980665 = 3.138 N·m; density 11.768 ÷ 0.485 kg = 24.3 N·m/kg; $379 ÷ 11.768 = $32.21 per stall N·m; $379 ÷ 3.138 = $120.77 per rated N·m
- **Feetech SM105B (SM-105B-C002 (-C001 = 12V))**: stall 150 kg·cm × 0.0980665 = 14.710 N·m; rated 50 kg·cm × 0.0980665 = 4.903 N·m; density 14.710 ÷ 0.2 kg = 73.5 N·m/kg; $188 ÷ 14.710 = $12.78 per stall N·m; $188 ÷ 4.903 = $38.34 per rated N·m
- **Feetech SM160B (SM-160B-C001)**: stall 160 kg·cm × 0.0980665 = 15.691 N·m; rated 40 kg·cm × 0.0980665 = 3.923 N·m; speed 10 ÷ 0.181 s/60° = 55.2 rpm; density 15.691 ÷ 0.211 kg = 74.4 N·m/kg; $385 ÷ 15.691 = $24.54 per stall N·m; $385 ÷ 3.923 = $98.15 per rated N·m
- **ROBOTIS XC330-M181-T**: density 0.600 ÷ 0.023 kg = 26.1 N·m/kg; $103.39 ÷ 0.600 = $172.32 per stall N·m; $103.39 ÷ 0.120 = $861.58 per rated N·m
- **ROBOTIS XC330-M288-T**: density 0.930 ÷ 0.023 kg = 40.4 N·m/kg; $103.39 ÷ 0.930 = $111.17 per stall N·m; $103.39 ÷ 0.186 = $555.86 per rated N·m
- **ROBOTIS XC330-T181-T**: density 0.760 ÷ 0.023 kg = 33.0 N·m/kg; $103.39 ÷ 0.760 = $136.04 per stall N·m; $103.39 ÷ 0.152 = $680.20 per rated N·m
- **ROBOTIS XC330-T288-T**: density 0.920 ÷ 0.023 kg = 40.0 N·m/kg; $103.39 ÷ 0.920 = $112.38 per stall N·m; $103.39 ÷ 0.184 = $561.90 per rated N·m
- **ROBOTIS XL330-M077-T (no XC330-M077 exists)**: density 0.215 ÷ 0.018 kg = 11.9 N·m/kg; $27.49 ÷ 0.215 = $127.86 per stall N·m; rated range E: 0.215 ÷ 5 = 0.043 to 0.215 ÷ 3 = 0.072 N·m → $383.58–$639.30 per rated N·m
- **ROBOTIS XL430-W250-T**: density 1.400 ÷ 0.0572 kg = 24.5 N·m/kg; $27.5 ÷ 1.400 = $19.64 per stall N·m; $27.5 ÷ 0.280 = $98.21 per rated N·m
- **ROBOTIS 2XL430-W250-T (2 axes)**: density 1.400 N·m × 2 axes ÷ 0.0982 kg = 28.5 N·m/kg; $149.39 ÷ (2 × 1.400) = $53.35 per stall N·m; $149.39 ÷ (2 × 0.280) = $266.77 per rated N·m
- **ROBOTIS XC430-W150-T (=T150BB)**: density 1.600 ÷ 0.065 kg = 24.6 N·m/kg; $137.89 ÷ 1.600 = $86.18 per stall N·m; $137.89 ÷ 0.320 = $430.91 per rated N·m
- **ROBOTIS XC430-W240-T (=T240BB)**: density 1.900 ÷ 0.065 kg = 29.2 N·m/kg; $137.89 ÷ 1.900 = $72.57 per stall N·m; $137.89 ÷ 0.380 = $362.87 per rated N·m
- **ROBOTIS 2XC430-W250-T (2 axes)**: density 1.800 N·m × 2 axes ÷ 0.102 kg = 35.3 N·m/kg; $298.89 ÷ (2 × 1.800) = $83.02 per stall N·m; $298.89 ÷ (2 × 0.360) = $415.12 per rated N·m; rated est. 0.20 × 1.800 = 0.360 N·m
- **ROBOTIS XM430-W210-T/-R**: density 3.000 ÷ 0.082 kg = 36.6 N·m/kg; $310.39 ÷ 3.000 = $103.46 per stall N·m; $310.39 ÷ 0.600 = $517.32 per rated N·m
- **ROBOTIS XM430-W350-T/-R**: density 4.100 ÷ 0.082 kg = 50.0 N·m/kg; $310.39 ÷ 4.100 = $75.70 per stall N·m; $310.39 ÷ 0.820 = $378.52 per rated N·m
- **ROBOTIS XH540-W150-T/-R**: density 7.100 ÷ 0.165 kg = 43.0 N·m/kg; $620.89 ÷ 7.100 = $87.45 per stall N·m; $620.89 ÷ 1.420 = $437.25 per rated N·m
- **ROBOTIS XH540-W270-T/-R**: density 9.900 ÷ 0.165 kg = 60.0 N·m/kg; $620.89 ÷ 9.900 = $62.72 per stall N·m; $620.89 ÷ 1.980 = $313.58 per rated N·m
- **ROBOTIS XM540-W150-T/-R**: density 7.300 ÷ 0.165 kg = 44.2 N·m/kg; $482.89 ÷ 7.300 = $66.15 per stall N·m; $482.89 ÷ 1.460 = $330.75 per rated N·m
- **ROBOTIS XM540-W270-T/-R**: density 10.600 ÷ 0.165 kg = 64.2 N·m/kg; $482.89 ÷ 10.600 = $45.56 per stall N·m; $482.89 ÷ 2.120 = $227.78 per rated N·m
- **Hiwonder LX-824**: stall 17 kg·cm × 0.0980665 = 1.667 N·m; speed 10 ÷ 0.2 s/60° = 50.0 rpm; density 1.667 ÷ 0.057 kg = 29.2 N·m/kg; $13.99 ÷ 1.667 = $8.39 per stall N·m; rated range E: 1.667 ÷ 5 = 0.333 to 1.667 ÷ 3 = 0.556 N·m → $25.17–$41.96 per rated N·m
- **Hiwonder LX-824HV**: stall 17 kg·cm × 0.0980665 = 1.667 N·m; speed 10 ÷ 0.2 s/60° = 50.0 rpm; density 1.667 ÷ 0.057 kg = 29.2 N·m/kg; $17.99 ÷ 1.667 = $10.79 per stall N·m; rated range E: 1.667 ÷ 5 = 0.333 to 1.667 ÷ 3 = 0.556 N·m → $32.37–$53.95 per rated N·m
- **Hiwonder LX-224**: stall 20 kg·cm × 0.0980665 = 1.961 N·m; speed 10 ÷ 0.2 s/60° = 50.0 rpm; density 1.961 ÷ 0.063 kg = 31.1 N·m/kg; $15.99 ÷ 1.961 = $8.15 per stall N·m; rated range E: 1.961 ÷ 5 = 0.392 to 1.961 ÷ 3 = 0.654 N·m → $24.46–$40.76 per rated N·m
- **Hiwonder LX-224HV**: stall 20 kg·cm × 0.0980665 = 1.961 N·m; speed 10 ÷ 0.18 s/60° = 55.6 rpm; density 1.961 ÷ 0.062 kg = 31.6 N·m/kg; $19.99 ÷ 1.961 = $10.19 per stall N·m; rated range E: 1.961 ÷ 5 = 0.392 to 1.961 ÷ 3 = 0.654 N·m → $30.58–$50.96 per rated N·m
- **Hiwonder LX-225**: stall 25 kg·cm × 0.0980665 = 2.452 N·m; speed 10 ÷ 0.2 s/60° = 50.0 rpm; density 2.452 ÷ 0.063 kg = 38.9 N·m/kg; $17.99 ÷ 2.452 = $7.34 per stall N·m; rated range E: 2.452 ÷ 5 = 0.490 to 2.452 ÷ 3 = 0.817 N·m → $22.01–$36.69 per rated N·m
- **Hiwonder HTD-30H**: stall 30 kg·cm × 0.0980665 = 2.942 N·m; speed 10 ÷ 0.12 s/60° = 83.3 rpm; density 2.942 ÷ 0.063 kg = 46.7 N·m/kg; $19.99 ÷ 2.942 = $6.79 per stall N·m; rated range E: 2.942 ÷ 5 = 0.588 to 2.942 ÷ 3 = 0.981 N·m → $20.38–$33.97 per rated N·m
- **Hiwonder HTD-35H**: stall 35 kg·cm × 0.0980665 = 3.432 N·m; speed 10 ÷ 0.18 s/60° = 55.6 rpm; density 3.432 ÷ 0.064 kg = 53.6 N·m/kg; $22.99 ÷ 3.432 = $6.70 per stall N·m; rated range E: 3.432 ÷ 5 = 0.686 to 3.432 ÷ 3 = 1.144 N·m → $20.09–$33.49 per rated N·m
- **Hiwonder HTD-45H**: stall 45 kg·cm × 0.0980665 = 4.413 N·m; speed 10 ÷ 0.18 s/60° = 55.6 rpm; density 4.413 ÷ 0.064 kg = 69.0 N·m/kg; $24.99 ÷ 4.413 = $5.66 per stall N·m; rated range E: 4.413 ÷ 5 = 0.883 to 4.413 ÷ 3 = 1.471 N·m → $16.99–$28.31 per rated N·m
- **Hiwonder HTD-85H**: stall 85 kg·cm × 0.0980665 = 8.336 N·m; speed 10 ÷ 0.2 s/60° = 50.0 rpm; density 8.336 ÷ 0.153 kg = 54.5 N·m/kg; $39.99 ÷ 8.336 = $4.80 per stall N·m; rated range E: 8.336 ÷ 5 = 1.667 to 8.336 ÷ 3 = 2.779 N·m → $14.39–$23.99 per rated N·m
- **Hiwonder HTS-35H**: stall 35 kg·cm × 0.0980665 = 3.432 N·m; speed 10 ÷ 0.18 s/60° = 55.6 rpm; density 3.432 ÷ 0.064 kg = 53.6 N·m/kg; $21.99 ÷ 3.432 = $6.41 per stall N·m; rated range E: 3.432 ÷ 5 = 0.686 to 3.432 ÷ 3 = 1.144 N·m → $19.22–$32.03 per rated N·m
- **Hiwonder HTS-30HS**: stall 30 kg·cm × 0.0980665 = 2.942 N·m; speed 10 ÷ 0.1 s/60° = 100.0 rpm; density 2.942 ÷ 0.064 kg = 46.0 N·m/kg; $45.99 ÷ 2.942 = $15.63 per stall N·m; rated range E: 2.942 ÷ 5 = 0.588 to 2.942 ÷ 3 = 0.981 N·m → $46.90–$78.16 per rated N·m
- **Hiwonder HX-35H**: stall 35 kg·cm × 0.0980665 = 3.432 N·m; published 'rotation torque' value 25 kg·cm × 0.0980665 = 2.452 N·m; speed 10 ÷ 0.18 s/60° = 55.6 rpm; density 3.432 ÷ 0.052 kg = 66.0 N·m/kg; $18.99 ÷ 3.432 = $5.53 per stall N·m; rated range E: 3.432 ÷ 5 = 0.686 to 3.432 ÷ 3 = 1.144 N·m → $16.60–$27.66 per rated N·m
- **Hiwonder HX-35HM**: stall 35 kg·cm × 0.0980665 = 3.432 N·m; published 'rotation torque' value 25 kg·cm × 0.0980665 = 2.452 N·m; speed 10 ÷ 0.19 s/60° = 52.6 rpm; density 3.432 ÷ 0.071 kg = 48.3 N·m/kg; $35.99 ÷ 3.432 = $10.49 per stall N·m; rated range E: 3.432 ÷ 5 = 0.686 to 3.432 ÷ 3 = 1.144 N·m → $31.46–$52.43 per rated N·m
- **Hiwonder HX-30HM**: stall 30 kg·cm × 0.0980665 = 2.942 N·m; speed 10 ÷ 0.19 s/60° = 52.6 rpm; density 2.942 ÷ 0.052 kg = 56.6 N·m/kg; $19.99 ÷ 2.942 = $6.79 per stall N·m; rated range E: 2.942 ÷ 5 = 0.588 to 2.942 ÷ 3 = 0.981 N·m → $20.38–$33.97 per rated N·m
- **Hiwonder HX-10HM**: stall 10 kg·cm × 0.0980665 = 0.981 N·m; speed 10 ÷ 0.1 s/60° = 100.0 rpm; density 0.981 ÷ 0.052 kg = 18.9 N·m/kg; $17.99 ÷ 0.981 = $18.34 per stall N·m; rated range E: 0.981 ÷ 5 = 0.196 to 0.981 ÷ 3 = 0.327 N·m → $55.03–$91.72 per rated N·m
- **Hiwonder HX-65HM (dual-motor)**: stall 65 kg·cm × 0.0980665 = 6.374 N·m; published 'Rated' value 50 kg·cm × 0.0980665 = 4.903 N·m; speed 10 ÷ 0.19 s/60° = 52.6 rpm; density 6.374 ÷ 0.1435 kg = 44.4 N·m/kg; $49.99 ÷ 6.374 = $7.84 per stall N·m; rated range E: 6.374 ÷ 5 = 1.275 to 6.374 ÷ 3 = 2.125 N·m → $23.53–$39.21 per rated N·m
- **Hiwonder HX-08LC (coreless micro)**: stall 8 kg·cm × 0.0980665 = 0.785 N·m; published 'Dynamic torque' value 3 kg·cm × 0.0980665 = 0.294 N·m; speed 10 ÷ 0.06 s/60° = 166.7 rpm; density 0.785 ÷ 0.026 kg = 30.2 N·m/kg; $34.99 ÷ 0.785 = $44.60 per stall N·m; rated range E: 0.785 ÷ 5 = 0.157 to 0.785 ÷ 3 = 0.262 N·m → $133.80–$223.00 per rated N·m

### 2. Per-product notes: sources and verbatim snippets (≤15 words each)

Every snippet was read on 2026-09-24. Feetech detail pages give each parameter in Chinese and English. The snippets keep the English part, trimmed.

#### 2.1 Feetech: what exists (official listing pages) [V]

- **STS (TTL, magnetic)**
  - Page 1, https://www.feetechrc.com/sts_ttl_series%20servo.html: ST-3200-C001, ST-3120-C001, ST-3095-C001, ST-3009-C001, ST-3250-C001, ST-3235-C001, ST-5420-C001, ST-3046-C001, ST-3025-C002, ST-3025-C001, ST-S3045-C001, ST-3035-C001.
  - Page 2, https://www.feetechrc.com/products/sts_ttl_series%20servo-page-2: ST-2000-C001, ST-3020-C001, ST-3215-C018, ST-3215-C001, ST-3036-C001/-C002, ST-3032-C036, ST-3032-C001.
  - Other STS3215 variants are sold by resellers but are not on the official listing (Seeed wiki, [U]): C047 is 12 V 1:345; C044 is 7.4 V 1:191; C046 is 7.4 V 1:147. "2x ST-3215-C044 (7.4V) motors with 1:191 gear ratio" (https://wiki.seeedstudio.com/lerobot_so100m_new/).
- **HLS (TTL, "constant force", which means current/torque control)**
  - Page 1, https://www.feetechrc.com/hl%E6%81%92%E5%8A%9B%E7%B3%BB%E5%88%97%E8%88%B5%E6%9C%BA.html: HL-3960, HL-3955, HL-3935, HL-3930, HL-3950, HL-3625, HL-3925, HL-3620-C001/-C002, HL-3640, HL-3915, HL-2915.
  - Page 2: HD-1910-C001 ("4.8V 9kg.cm Servo for Open Source Duck Robot"), HL-2909-C001 (8.9 kg·cm@12V), HL-3612-C001 (15 kg·cm@6V), HL-3606-C001/-C002 (6 kg·cm@6V), HL-3604-C001 (4.4 kg·cm@6V).
- **SCS (TTL, potentiometer)**
  - Page 1, https://www.feetechrc.com/scs_ttl_Servo: SC-4000-C001/-C003, SC-4600-C001/-C005, SC-1250-C001, SC-2150-C001 (= SCS215), SC-1500-C022 (= SCS15), SC-1025-C001, SC-0018-C001, SC-0017-C001, SC-2332-C001, SC-2304-C001.
  - Page 2: SC-0090-C013/-C001 (= SCS0009), SC-0005, SC-0043, SC-0037, SC-0002.
  - **"SCS225" does not appear on the official listing.** It is sold by resellers as "SCS225-C006", a 19 kg dual-axis variant of SCS215 [U], e.g. https://www.amazon.com/RCmall-Feetech-SCS225-C006-Programmable-Robotics/dp/B0FX8BG773.
- **SMS (RS-485)**
  - Page 1, https://www.feetechrc.com/sms_rs485_series%20servo: SM-260B, SM-120B, SM-105B-C002/-C001, SM-160B, SM-8512, SM-85CL, SM-8524, SM-60CL, SM-45BL, SM-80BL-C002/-C001.
  - Page 2: SM-40BL, SM-2930-C002/-C001, SM-30BL, SM-2924, SM-2912, SM-70BL, SM-24BL, SM-2924BL-C012, SM-24BL-C015, SM-1500, SM-1000.
  - Name mapping: **"SM85BL" is not an official name.** The official parts are SM-8512-C001 and SM-8524-C001 (brushless, 85 kg·cm) and SM-85CL-C001 (coreless); resellers call the brushless ones SM8512BL/SM8524BL. **"SM120BL" is officially SM-120B-C001.**
- **Protocol**
  - Official 2020 article: "TTL communication level , half duplex asynchronous communication" (https://www.feetechrc.com/2020-05-13_56655.html) [V].
  - The packet format is FF FF | ID | LEN | INSTR | params | checksum, similar to DYNAMIXEL Protocol 1.0. This comes from the Feetech "Communication Protocol User Manual" hosted by Waveshare/Seeed; I saw it only in search results and did not read it [U]: https://files.waveshare.com/upload/2/27/Communication_Protocol_User_Manual-EN(191218-0923).pdf
  - Resellers sell SMS parts in "MODBUS-RTU" or "Custom Protocol" variants (ZennixTek variant names) [U].
- **Protection behaviour (official 2020 article)** [V]: "the unloading force lasts for 2S (20% of the default blocking force)". It also lists "overload, overcurrent, overvoltage, overheating" protection.

#### 2.2 Feetech STS

- **STS3215 7.4 V (ST-3215-C001)**
  - Official page: https://www.feetechrc.com/74v-19-kgcm-plastic-case-metal-tooth-magnetic-code-double-axis-ttl-series-steering-gear [V]
    - Torque, voltage, speed: "Peak stall torque: 19.5kg.cm@6V"; "Rated torque: 6.5kg.cm@6V"; "Operating Voltage Range: 6-7.4V"; "No load speed: 0.238sec/60°@6V".
    - Mass, size, gear: "Weight: 55± 1g"; "A：45.2mm B：24.7mm C：35mm"; "Gear type: 铜Copper".
    - Sensor, bus, current: "12 bit high precision magnetic coding sensor"; "Communication Speed: 38400bps ~ 1 Mbps"; "Stall current: 2000mA@6V".
    - **Conflicts on the same page:** the text says "adopt plastic case、core motor、metal gearbox", but the table says "Case: aluminium alloy" and "Motor: Coreless motor".
  - Official listing: https://www.feetechrc.com/products/sts_ttl_series%20servo-page-2 [V]. It gives "The Stall Torque：16.5kg.cm@6V", which disagrees with the table's 19.5.
  - Official 2020 launch article: https://www.feetechrc.com/2020-05-13_56655.html [V]
    - "Stall Torque ： 19.5kg.cm@7.4V"; "Stall Speed ： 52RPM@7.4V". I read the latter as no-load speed.
    - "The servo gear adopts 1:345 copper Gear combination"; "360 degree absolute position 4096 bit precision".
    - Multi-turn: "absolute position control can be plus or minus 7 turns" and "the number of power cycles is not saved".
    - **Price:** "The domestic retail price is ￥ 99(tax free)"; "the oversea price is $15 US dollars". This is the 2020 launch price, not a current one.
  - Resellers today [U]:
    - WowRobo, "Single Piece(15.99/pcs)": https://shop.wowrobo.com/products/feetech-sts3215-c001-servo-7-4v-19-5kg-high-torque-servo-for-so-arm100-101
    - Seeed, JSON `"price":"20.00"`: https://www.seeedstudio.com/STS3215-19kg-cm-7-4V-Serial-Servo-p-6338.html
    - ZennixTek, `"price":"22.00"`: https://www.zennixtek.com/products/feetech-st-3215-c001-servo-motor
  - Seeed wiki [U]: the SO-ARM100 leader arm uses "12x ST-3215- C001 (7.4V) motors with 1:345 gear ratio". Power warning: "otherwise you might burn your motors!"
  - India [U, search only]:
    - Evelta: https://evelta.com/sts3215-7-4v-19kg-dual-axis-ttl-string-servo-motor/ and https://evelta.com/feetech/
    - ThinkRobotics (SO-101 kits): https://thinkrobotics.com/blogs/product-reviews-buying-guides/thinkrobotics-lerobot-so-101-6-axis-robotic-arm-review-ai-ready-open-source-and-built-for-learning
- **STS3215 12 V (ST-3215-C018)**
  - Official page: https://www.feetechrc.com/525603.html [V]
    - Torque, voltage, speed: "Peak stall torque: 30kg.cm@12V"; "Rated torque: 10kg.cm@12V"; "Operating Voltage Range: 4-14V"; "No load speed: 0.222sec/60°@12V".
    - Mass, size, gear: "Weight: 55± 1g"; "A：45.2mm B：24.7mm C：35mm"; "Gear type: 钢齿steel Gear".
    - Sensor, bus, current: "12 bit high precision magnetic coding sensor"; "38400bps ~ 1 Mbps"; "Stall current: 2.7A@12V"; "Runnig current(at no load) : 180 mA@12V".
  - Gear ratio [U]: Seeed wiki says "ST-3215-C018/ST-3215-C047 (12V) motors with 1:345 gear ratio".
  - Independent test, Robo9 [U]: https://robonine.com/testing-of-feetech-sts3215-servomotor-backlash-repeatability-and-torque/
    - Backlash: "angular backlash of 0.0151 radians (≈ 0.87°)" against the datasheet's "≤ 0.5°".
    - Static torque: "Static load: approximately 3.5 kg (≈ 35 kg·cm of torque)".
    - Sustained load: "At 2 kg load: servo entered overload protection after several operating cycles". "Performance remained consistent up to roughly 15 kg·cm".
    - Heating: "increased to 71 °C after ~110 min, resulting in overheating".
  - Prices [U]: WowRobo "Single Piece(15.99/pcs)" at https://shop.wowrobo.com/products/feetech-sts3215-servo-12v-30kg-high-torque-servo-for-so-arm100; ZennixTek `"price":"25.00"` at https://www.zennixtek.com/products/feetech-st-3215-c018-servo-motor
- **STS3235 (ST-3235-C001)**
  - Official page: https://www.feetechrc.com/12v-30kg-metal-shell-metal-tooth-iron-core-motor-magnetic-coding-double-shaft-ttl-series-steering-gear [V]
    - "Peak stall torque: 30kg.cm@12V"; "Rated torque: 10kg.cm@12V"; "Operating Voltage Range: 6-12V"; "No load speed: 0.222sec/60°@12V".
    - "Weight: 70.5± 1g"; "A：45.22mm B：24.72mm C：35mm"; "Gear type: 钢齿steel Gear"; "Case: Aluminium"; "Motor: Core Motor"; "Stall current: 2.7A@12V".
  - Price [U]: ZennixTek "ST-3235-C001 (12V30KG)" $55, https://www.zennixtek.com/products/feetech-sts3235-servo-motor
- **STS3250 (ST-3250-C001)**
  - Official page: https://www.feetechrc.com/562636 [V]
    - "Peak stall torque: 50kg.cm@12V"; "Rated torque: 16kg.cm@12V"; "Operating Voltage Range: 6-12V"; "No load speed: 0.133sec/60°@12V"; "Runnig current(at no load) : 280mA@12V".
    - "Weight: 74.5± 1g"; "A：45.22mm B：24.72mm C：35mm"; "Gear type: 钢齿steel Gear"; "Motor: Coreless Motor"; "Stall current: 4.2A@12V".
  - Independent test, Robo9 [U]: https://robonine.com/feetech-sts3250-smart-actuator-evaluation-of-accuracy-torque-and-backlash/
    - Speed and backlash: "achieves 77.6 RPM no-load speed"; "mechanical backlash of 0.43° (within 0.5° limit)".
    - Thermal limit: "20 kg·cm (40% of rated stall torque)" and "This threshold was reached at the 8-minute mark". The threshold is 70 °C.
    - Stiffness: "Torsional stiffness: 1.96 / 0.0215 = 91.2 N·m/rad".
  - Prices [U]:
    - WowRobo "Feetech STS3250 C002 Servo – 12V 50KG 1/345 Servo", $43.00: https://shop.wowrobo.com/products/feetech-sts3250-c002-servo-12v-50kg-1-345-servo
    - ZennixTek "ST-3250-C001 Motor (With Bracket)", $95.00: https://www.zennixtek.com/products/feetech-sts3250-servo-motor
    - C002 is not on Feetech's listing, so the difference between C001 and C002 is unknown.
- **STS3035 (ST-3035-C001)**
  - Official page: https://www.feetechrc.com/611721 [V]
    - "Peak stall torque: 35kg.cm@12V"; "Rated torque: 11.6kg.cm@12V"; "Operating Voltage Range: 9V-12V"; "No load speed: 0.22sec/60°(45RPM)@12V".
    - "Weight: 62.5±2g"; "A: 40.2mm B: 20.2mm C: 40mm"; "Gear type: 铜 Copper"; "12Bits Magnetic Coding(360° /4095）".
    - "Stall current: 2.7A@12V"; "Rated Current: 900mA@12V".
  - Price [U]: ZennixTek "ST-3035-C001 (12V35KG)" $29, https://www.zennixtek.com/products/feetech-st3035-servo-motor
- **STS3046 (ST-3046-C001)**
  - Official page: https://www.feetechrc.com/74v-40-kgcm-metal-shell-steel-teeth-360-degree-magnetic-code-single-shaft-ttl-serial-port-steering-gear [V]
    - "Peak stall torque: 40kg.cm@7.4V"; "Rated torque: 13.3kg.cm@7.4V"; "Operating Voltage Range: 6-7.4V"; "No load speed: 0.22sec/60°@7.4V".
    - "Weight: 89± 1g"; "A：40mm B：20mm C：43.05mm"; "Gear type: 钢 Steel"; "Stall current: 3.1A@7.4V".
  - The listing disagrees on voltage: "The Stall Torque：40kg.cm@6V".
  - Price [U]: ZennixTek $90, https://www.zennixtek.com/products/feetech-sts3046-servo-motor
- **STS3025BL-40 (ST-3025-C002)**
  - Official page: https://www.feetechrc.com/12v-40kg-metal-tooth-large-torque-brushless-motor-magnetic-coding-double-shaft-ttl-series-steering-gear [V]
    - "Peak stall torque: 40kg.cm@12V"; "Rated torque: 10kg.cm@12V"; "No load speed: 0.117sec/60°（ 85RPM ）@12V".
    - "Weight: 89± 1g"; "A：40mm B：20mm C：40mm"; "Motor: 无刷马达Brushless Motor"; "Stall current: 4.4A@12V".
    - The page text says "The stall torque is 20kg.cm" (copy error). The 20 kg·cm, 170 rpm sibling is ST-3025-C001: "0.059sec/60°（ 170RPM ）@12V".
  - Price [U]: ZennixTek $109, https://www.zennixtek.com/products/feetech-sts3025bl-servo-motor
- **STS3095 (ST-3095-C001)**
  - Official page: https://www.feetechrc.com/555959 [V]
    - "Peak stall torque: 105kg.cm@8.4V"; "Rated torque: 35kg.cm@8.4V"; "Operating Voltage Range: 6V-12V"; "No load speed: 0.25sec/60°@8.4V".
    - "Weight: 194.5± 1g"; "A：30mm B：65mm C：48mm"; "Horn gear spline: 15T/OD7.6mm".
    - "Stall current: 10.5A@8.4V"; "Runnig current(at no load) : 800mA@8.4V".
  - Price [U]: ZennixTek "ST-3095-C001 (7.4V95KG)" $133, https://www.zennixtek.com/products/feetech-sts3095-servo-motor
- **STS3120 (ST-3120-C001)**
  - Official page: https://www.feetechrc.com/570220 [V]
    - "Peak stall torque: 120kg.cm@12V"; "Rated torque: 40kg.cm@12V"; "No load speed: 0.454sec/60 °(22RPM)@12V".
    - "Weight: 210± 5g"; "Motor: Coreless Motor"; "Stall current: 4.7A@12V".
  - Price [U]: AIFITLAB "ST-3120-C001" $188, https://aifitlab.com/products/feetech-st3120-st3200-servo-motor
- **STS3200 (ST-3200-C001)**
  - Official page: https://www.feetechrc.com/519352 [V]
    - "Peak stall torque: 200kg.cm@12V"; "Rated torque: 66.7kg.cm@12V"; "0.263sec/60 °(38RPM)@12V".
    - "Weight: 210± 5g"; "Motor: Brushless Motor"; "Stall current: 11.3A@12V".
    - The Chinese product name says "空芯杯电机" (coreless), which conflicts with the table.
  - Price [U]: AIFITLAB "ST-3200-C001" $348 (same URL as STS3120).
- **STS3032 (ST-3032-C001 / -C036)**
  - Official pages [V]: https://www.feetechrc.com/6v-45kg-magnetic-code-360-degree-serial-bus-steering-gear and https://www.feetechrc.com/568388
    - "Peak stall torque: 4.5kg.cm@6V"; "Rated torque: 1.5kg.cm@6V"; "Operating Voltage Range: 4.8-6V"; "No load speed: 0.09sec/60°@6V".
    - "Weight: 20g" (C001) and "20.6± 1g" (C036); "A：32mm B：12mm C：27.5mm"; "Stall current: 1200mA@6V".
  - **Conflicts:**
    - C001 dimensions: the listing gives "23.2*12.1*28.5mm", the table 32×12×27.5.
    - C001 sensor: the table says "Potentiometer(360°/4096)", but the text says "12 位高精度磁编码传感器". C036 gives "0.088°(360°/4096)".
  - Price [U]: ZennixTek $39, https://www.zennixtek.com/products/feetech-sts-3032-c001-servo-motor

#### 2.3 Feetech HLS ("constant force" = torque/current mode)

All HLS pages give the same three facts:
- Torque mode: "Mode 2: Motor constant current mode".
- Resolution: "0.088°(360°/4096)".
- Bus: "38400bps ~ 1 Mbps". Most pages add "默认出厂波特率为1000000".

- **HLS3930 (HL-3930-C001)**
  - Official page: https://www.feetechrc.com/705193 [V]
    - "Peak stall torque: 35kg.cm@12V"; "额定负载Rated Load： 8.7kg. cm@12V"; "额定电流Rated current： 800mA@12V"; "Rated Input Voltage： 9V-12.6V".
    - "0.222sec/60°(45RPM)@12V"; "Weight: 70.5± 1g"; "A：45.22mm B：24.72mm C：35mm".
    - "钢齿steel Gear"; "减速比Gear Ratio： 1/345"; "Motor: Core Motor".
    - "Stall current: 2.8A@12V"; "KT常数 12.5kg. cm/A".
  - Price [U]: ZennixTek "HL-3930-C001 (12V35KG)" $75, https://www.zennixtek.com/products/feetech-hl-3930-servo-motor
- **HLS3935 (HL-3935-C001)**
  - Official page: https://www.feetechrc.com/531930 [V]
    - "Peak stall torque: 35kg.cm@12V"; "Rated Load： 8.5kg. cm@12V"; "0.117sec/60°( 85RPM )@12V".
    - "Weight: 85± 1g"; "Gear Ratio： 1/378"; "Coreless Motor"; "Stall current: 3.1A@12V".
  - Price [U]: ZennixTek $89, https://www.zennixtek.com/products/feetech-hl-3935-servo-motor
- **HLS3950 (HL-3950-C001)**
  - Official page: https://www.feetechrc.com/563788 [V]
    - "Peak stall torque: 50kg.cm@12V"; "Rated Load： 12.5kg. cm@12V"; "Rated current： 600mA@12V"; "0.133sec/60°(75RPM)@12V".
    - "Weight: 74.5± 1g"; "Gear Ratio： 1/345"; "Stall current: 2.4A@12V".
  - The listing disagrees on speed: "The Maximum Speed：0.117sec/60°@12V".
  - Price [U]: ZennixTek $83, https://www.zennixtek.com/products/feetech-hl-3950-c001-servo-motor
- **HLS3955 (HL-3955-C001)**
  - Official page: https://www.feetechrc.com/560655 [V]
    - "Peak stall torque: 55kg.cm@12V"; "Rated Load： 13.5kg. cm@12V"; "0.182sec/60°(55RPM)@12V".
    - "Weight: 85± 1g"; "Gear Ratio： 1/378"; "Stall current: 3.0A@12V".
  - Price [U]: ZennixTek $89, https://www.zennixtek.com/products/feetech-hl-3955-servo-motor
- **HLS3960 (HL-3960-C001)**
  - Official page: https://www.feetechrc.com/839851 [V]
    - "Peak stall torque: 66.8kg.cm@12V"; "Rated Load： 23kg. cm@12V"; "Rated current： 1500mA@12V"; "0.167sec/60° (60rpm)@12V".
    - "Weight: 103.2±2g"; "A：45mm B：24.4mm C：35.5mm"; "Gear Ratio： 1/358"; "Back Lash： ≦0.5°"; "Stall current: 4.5A@12V".
  - The listing disagrees on torque and speed: "The Stall Torque：60kg.cm@12V"; "The Maximum Speed：0.137sec/60°@12V".
  - Prices [U]: AIFITLAB "HLS-3960-C001" $116, https://aifitlab.com/products/feetech-hls3960-servo-motor; ZennixTek $129.
- **HLS3625 (HL-3625-C001)**
  - Official page: https://www.feetechrc.com/811177 [V]
    - "Peak stall torque: 25kg.cm@7.4V"; "Rated Load： 6.2kg. cm@7.4V"; "Rated Input Voltage： 5V-8.4V"; "0.192sec/60°(52RPM)@7.4V".
    - "Weight: 55± 1g"; "A：45.2mm B：24.7mm C：35mm" (the listing says 40.5*24.7*35); "Gear type: 铜 Copper"; "Gear Ratio： 1/345".
    - "Stall current: 3.0A@7.4V".
  - Price [U]: ZennixTek $29, https://www.zennixtek.com/products/feetech-hl-3625-servo-motor
- **HLS3925 (HL-3925-C001)**
  - Official page: https://www.feetechrc.com/515669 [V]
    - "Peak stall torque: 25kg.cm@12V"; "Rated Load： 4.8kg. cm@12V"; "0.182sec/60°(55RPM)@12V".
    - "Weight: 61.7± 1g"; "Gear type: 铜 Copper"; "Gear Ratio： 1/275"; "Stall current: 2.7A@12V".
  - Price [U]: ZennixTek $33, https://www.zennixtek.com/products/feetech-hl-3925-servo-motor
- **HLS3620 (HL-3620-C001; single-shaft C002 at https://www.feetechrc.com/533623)**
  - Official page: https://www.feetechrc.com/572022 [V]
    - "Peak stall torque: 25.5kg.cm@8.4V"; "Rated Load： 6.4kg. cm@8.4V"; "Rated Input Voltage： 6V-8.4V"; "0.135sec/60°(74RPM)@8.4V".
    - "Weight: 61.7± 1g"; "Gear Ratio： 1/275"; "Stall current: 3.3A@8.4V".
  - Price [U]: ZennixTek $39, https://www.zennixtek.com/products/feetech-hl-3620-c001-servo-motor
- **HLS3640 (HL-3640-C001)**
  - Official page: https://www.feetechrc.com/556986 [V]
    - "Peak stall torque: 40kg.cm@7.4V"; "Rated Load： 10kg. cm@7.4V"; "0.22sec/60°(45RPM)@7.4V".
    - "Weight: 89± 1g"; "Gear type: 钢 Steel"; "Gear Ratio： 1/378"; "Stall current: 3.3A@7.4V".
  - Price [U]: ZennixTek $93, https://www.zennixtek.com/products/feetech-hl-3640-servo-motor
- **HLS3915 (HL-3915-C001)**
  - Official page: https://www.feetechrc.com/532111 [V]
    - "Peak stall torque: 14.2kg.cm@12V"; "Rated Load： 4.5kg. cm@12V"; "Rated Input Voltage： 4V-14V"; "0.1sec/60°(100RPM)@12V".
    - "Weight: 35.8±2g"; "A：20mm B：34mm C：23mm"; "Gear Ratio： 1/320"; "Stall current: 1.5A@12V".
  - Price [U]: ZennixTek $49, https://www.zennixtek.com/products/feetech-hl-3915-c001-servo-motor
- **HLS2915 (HL-2915-C001)**
  - Official page: https://www.feetechrc.com/585239 [V]
    - "Peak stall torque: 14.2kg.cm@12V"; "Rated Load： 4.5kg. cm@12V"; "Rated Input Voltage： 9V-14V"; "0.09sec/60°(110RPM)@12V".
    - "Weight: 27.8±2g"; "Gear Ratio： 1/320"; "齿轮虚位Back Lash ≦1°"; "Case: PA+Fiber".
  - Price [U]: AIFITLAB "HL-2915-C001" $38, https://aifitlab.com/products/feetech-hl2915-servo-motor

#### 2.4 Feetech SCS (potentiometer)

- **SCS0009 (SC-0090-C001)**
  - Official page: https://www.feetechrc.com/6v-23kg-serial-bus-steering-gear_65522 [V]
    - "Peak stall torque: 2.3kg.cm@6V"; "Rated torque: 0.7kg.cm@6V"; "Operating Voltage Range: 4-7.4V"; "No load speed: 0.1sec/60°@6V".
    - "Weight: 13.2± 1g"; "A：23.2mm B：12.1mm C：25.25mm"; "Gear type: 铜Copper+钢Steel".
    - "Position Sensor Resolution: 0.293°(300°/1024)"; "high quality potentiometer"; "Stall current: 1.0A@6V".
  - The listing (page 2) disagrees for C001: "0.07sec/60degree@6V" and "12.5g ±0.2".
  - Price [U]: ZennixTek "SC-0090-C001 (6V 2.3kg·cm Single-Axis)" $13, https://www.zennixtek.com/products/feetech-scs0009-servo-motor
- **SCS15 (SC-1500-C022)**
  - Official page: https://www.feetechrc.com/6v-15kg-digital-robot-steering-gear [V]
    - "Peak stall torque: 15.6kg.cm@7.4V" (the listing says "15.6kg.cm@6V"); "Rated torque: 5.2kg.cm@7.4V"; "No load speed: 0.156sec/60°@7.4V".
    - "Weight: 58.2± 1g"; "0.215°(220°/1023)"; "Stall current: 2.5A@7.4V".
  - Price [U]: ZennixTek $19, https://www.zennixtek.com/products/feetech-scs15-servo-motor
- **SCS215 (SC-2150-C001)**
  - Official page: https://www.feetechrc.com/74v18kg-serial-bus-steering-gear [V]
    - "Peak stall torque: 19kg.cm@7.4V"; "Rated torque: 6.3kg.cm@7.4V"; "No load speed: 0.192sec/60°@7.4V".
    - "Weight: 55± 1g"; "A：45.23mm B：24.73mm C：35mm"; "0.322°(330°/1024)"; "Stall current: 2.5A@6V".
  - Price [U]: ZennixTek $29, https://www.zennixtek.com/products/feetech-scs215-servo-motor
- **SCS40 (SC-4000-C001)**
  - Official page: https://www.feetechrc.com/84v40kg-serial-bus-steering-gear [V]
    - "Peak stall torque: 42.5kg.cm@8.4V"; "Rated torque: 12.8kg.cm@8.4V"; "No load speed: 0.12sec/60°@8.4V 83RPM".
    - "Weight: 70g 士0.2"; "Case: ABS"; "Potentiometer(300°/1024)士5"; "Stall current: 1800mA@8.4V".
  - The listing disagrees: "The Stall Torque：38.6kg.cm@6V".
  - Price [U]: ZennixTek "SC-4000-C001" $89, https://www.zennixtek.com/products/feetech-scs40-servo-motor
- **SC-4600-C001**
  - Official page: https://www.feetechrc.com/74v40kg-serial-bus-steering-gear [V]
    - "Peak stall torque: 40.5kg.cm@7.4V"; "Rated torque: 13.5@7.4V" (no unit on the page); "0.22sec/60°@7.4V"; "Weight: 89± 1g".
    - "Stall current: 4.4mA@7.4V" is an obvious page typo.
  - Price not found.

#### 2.5 Feetech SMS (RS-485, 12-bit magnetic)

- **SM40BL (SM-40BL-C001)**
  - Official page: https://www.feetechrc.com/12v-40kg-rs485-serial-bus-steering-gear [V]
    - "Peak stall torque: 40kg.cm@12V"; "Rated torque: 12kg.cm≤@12V"; "0. 153sec/ 60degree 65RPM".
    - "Weight: 100g"; "Steel Gear (Gear Ratio 353:1 )"; "Stall current: 2500mA@12V"; "Bus Packet Communication RS485".
  - Price [U]: ZennixTek $139, https://www.zennixtek.com/products/feetech-sm40bl-c001-servo-motor
- **SM45BL (SM-45BL-C001)**
  - Official page: https://www.feetechrc.com/24v-45kgcm-rs485%E4%B8%B2%E5%8F%A3%E6%80%BB%E7%BA%BF%E8%88%B5%E6%9C%BA [V]
    - "Peak stall torque: 45kg.cm@24V"; "Rated torque: 15kg.cm@24V"; "0.142sec/ 60degree 70RPM".
    - "Weight: 100g"; "A：46.5mm B：28.5mm C：34mm"; "Steel Gear (Gear Ratio 353:1 )"; "Stall current: 2300mA@24V".
    - "12Bits Magnetic Coding(360° /4096)".
  - **Conflicts:** the listing says "0.285sec/60degree 35RPM", and the page text says "SM-45BL-C001 is 12V serial port smart bus servo".
  - Price [U]: ZennixTek $139, https://www.zennixtek.com/products/feetech-sm45bl-c001-servo-motor
- **SM60CL (SM-60CL-C001)**
  - Official page: https://www.feetechrc.com/12v-60kg-rs485-serial-bus-steering-gear [V]
    - "Peak stall torque: 60kg.cm@12V"; "Rated torque: 20kg.cm@12V"; "0.286sec/60degree 35RPM@12V".
    - "Weight: 180g"; "A：62mm B：34mm C：40mm"; "Stall current: 2600mA@12V".
  - Price [U]: ZennixTek $165, https://www.zennixtek.com/products/feetech-sm60cl-c001-servo-motor
- **SM70BL (SM-70BL-C001)**
  - Official page: https://www.feetechrc.com/713228 [V]
    - "Stall Torque (at locked)： 70Kg.cm"; "Rated Torgue： 17.5kg.cm@24V"; "Input Voltage： 16.8V-25.2V"; "0.13sec/60°(78RPM)@24V".
    - "Weight: 91.6±1g"; "A：40mm B：20mm C：47.8mm"; "Stall Current (at locked)： 3.5A@24V".
  - The listing gives the torque voltage: "The Stall Torque：70kg.cm@24V".
  - No price found.
- **SM80BL 12 V (SM-80BL-C001)**
  - Official page: https://www.feetechrc.com/552209 [V]
    - "Peak stall torque: 80kg.cm@12V"; "Rated torque: 20kg.cm≤@12V"; "Rated current: 1475mA@12V"; "0. 161sec/ 60° （62RPM）@12V".
    - "Weight: 97.5±1g"; "4 Pole Brushless motor"; "Stall current: 5.9A@12V".
  - The 24 V variant C002 is on the listing: "The Stall Torque：85kg.cm@24V".
  - Price [U]: ZennixTek $185, https://www.zennixtek.com/products/feetech-sm80bl-c001-servo-motor
- **SM8512BL (SM-8512-C001)**
  - Official page: https://www.feetechrc.com/12v-85-kgcm-serial-rs485-bus-steering-gear [V]
    - "Peak stall torque: 85kg.cm@12V"; "Rated torque: 28kg.cm@12V"; "0.167sec/60degree@12V".
    - "Weight: 215± 1g"; "Brushless Motor"; "Stall current: 7.9A@12V".
  - Price [U]: ZennixTek $209, https://www.zennixtek.com/products/feetech-sm8512bl-servo-motor
- **SM85CL (SM-85CL-C001)**
  - Official page: https://www.feetechrc.com/12v-85kg-serial-rs485-bus-steering-gear [V]
    - "Peak stall torque: 85kg.cm@12V"; "Rated torque: 28kg.cm@12V"; "0.27sec/60degree@12V 37RPM"; "Stall current: 3200 mA12V".
  - Price [U]: ZennixTek $209, https://www.zennixtek.com/products/feetech-sm85cl-c001-servo-motor
- **SM120BL (SM-120B-C001)**
  - Official page: https://www.feetechrc.com/24v-120kg-rs485-serial-bus-steering-gear [V]
    - "Peak stall torque: 120kg.cm@24V"; "Rated Load 32kg. cm≤"; "0.2sec/ 60degree 50RPM@24V".
    - "Weight: 485g"; "Steel Gear ( Gear Ratio 232:1 )"; "Stall current: 4A@24V".
  - Price [U]: ZennixTek $379, https://www.zennixtek.com/products/feetech-sm120bl-servo-motor
- **SM105B (page shows SM-105B-C002)**
  - Official page: https://www.feetechrc.com/935171 [V]
    - "Peak stall torque: 150kg.cm"; "Rated torque: 50kg.cm"; "Operating Voltage Range: 9V-24V"; "0.167sec/60°(60RPM)".
    - "Weight: 200± 3g"; "Back Lash: ≦0.5°"; "Stall current: 6.3A".
    - **The page does not state the torque voltage.** The C001 (12 V) page, https://www.feetechrc.com/861651, was not read.
  - Price [U]: AIFITLAB "SM-105B-C001 (12V150KG)" $188, https://aifitlab.com/products/feetech-sm105b-servo-motor
- **SM160B (SM-160B-C001)**
  - Official page: https://www.feetechrc.com/721026 [V]
    - "Peak stall torque: 160kg.cm@24V"; "Rated torque: 40kg.cm@24V"; "Operating Voltage Range: 16.8V-25.2V"; "0.181sec/60°@24V".
    - "Weight: 211± 3g"; "Back Lash: ≦0.5°"; "Stall current: 9A@24V".
  - Price [U]: AIFITLAB $385, https://aifitlab.com/products/feetech-sm160b-servo-motor

#### 2.6 ROBOTIS DYNAMIXEL

**Sources and rules that apply to every model:**
- Specs [V] come from e-manual pages at https://emanual.robotis.com/docs/en/dxl/x/<model>/. Prices [V] come from https://robotis.us/products/dynamixel-<model>-t (Shopify product JSON and HTML).
- The e-manual says rated and stall torque differ: "Stall torque is the maximum momentary torque output the servo is capable of". It also says "The given Stall torque rating … is different from it's continuous output rating".
- robotis.us disclosure on every product: "This is an estimated value for continuous torque, calculated at 20% of stall torque."
- Protection: when an error bit is enabled in Shutdown(63), "Torque Enable(64) will be set to ‘0’ (Torque OFF)" (XM430/XC330 pages).
- Temperature limit defaults: XL430 "Temperature Limit RW 72"; XM430 "Temperature Limit RW 80"; XC330 "Temperature Limit RW 70".
- Protocol:
  - XL430 control table: "1 DYNAMIXEL Protocol 1.0" and "2(default) DYNAMIXEL Protocol 2.0".
  - XC330: "2(default) DYNAMIXEL Protocol 2.0", with "20 Experimental S.BUS", "21 Experimental iBUS" and "22 RC-PWM".

- **XC330-M181-T**
  - e-manual: https://emanual.robotis.com/docs/en/dxl/x/xc330-m181/
    - Torque, voltage, speed: "0.60 [N.m] (at 5.0 [V], 1.80 [A], 0.333 [Nm/A])"; "3.7 ~ 6.0 [V] (Recommended : 5.0 [V])"; "129 [rev/min] (at 5.0 [V])".
    - Mass, size, gearbox: "Weight 23 [g]"; "20.0 x 34.0 x 26.0 [mm]"; "Gear Ratio 180.62 : 1"; "Full Metal Gear, 2 Bearing".
    - Sensor and bus: "Contactless absolute encoder (12Bit, 360 [°])"; "TTL Multidrop Bus (3.3V Logic, 5V Compatible)"; "9,600 [bps] ~ 4 [Mbps]".
  - Store: "Estimated rated torque: 0.12Nm"; "$103.39".
- **XC330-M288-T**
  - e-manual: https://emanual.robotis.com/docs/en/dxl/x/xc330-m288/
    - "0.93 [N.m] (at 5.0 [V], 1.80 [A], 0.517 [Nm/A])"; "81 [rev/min] (at 5.0 [V])"; "Gear Ratio 288.35 : 1".
  - Store: "0.186Nm"; "$103.39". The store's "No load rpm: 65RPM" conflicts with the e-manual.
- **XC330-T181-T**
  - e-manual: https://emanual.robotis.com/docs/en/dxl/x/xc330-t181/
    - "0.76 [N.m] (at 11.1 [V], 0.80 [A], 0.950 [Nm/A])"; "6.5 ~ 12.0 [V] (Recommended : 11.1 [V])"; "104 [rev/min] (at 11.1 [V])"; "TTL Multidrop Bus (5V Logic)".
  - Store: "0.152Nm"; "$103.39".
- **XC330-T288-T**
  - e-manual: https://emanual.robotis.com/docs/en/dxl/x/xc330-t288/
    - "0.92 [N.m] (at 11.1 [V], 0.80 [A], 1.150 [Nm/A])"; "1.00 [N.m] (at 12.0 [V], 0.88 [A]"; "65 [rev/min] (at 11.1 [V])".
  - Store: "0.184Nm"; "$103.39".
- **"XC330-M077" does not exist.**
  - The e-manual's own "same form factor" table lists only XC330-T288/T181/M288/M181. The URL https://emanual.robotis.com/docs/en/dxl/x/xc330-m077/ returned HTTP 404, and robotis.us has no such product.
  - The nearest part is **XL330-M077-T**: "0.215 [N.m] (at 5.0 [V], 1.47 [A]"; "383 [rev/min] (at 5.0 [V])"; "Weight 18 [g]"; "Gear Ratio 77.5 : 1"; plastic gears. robotis.us price $27.49. e-manual: https://emanual.robotis.com/docs/en/dxl/x/xl330-m077/
- **XL430-W250-T**
  - e-manual: https://emanual.robotis.com/docs/en/dxl/x/xl430-w250/
    - Torque, voltage, speed: "1.4 [N.m] (at 11.1 [V], 1.3 [A], 1.077 [Nm/A])"; "1.5 [N.m] (at 12.0 [V], 1.4 [A]"; "6.5 ~ 12.0 [V] (Recommended : 11.1 [V])"; "57 [rev/min] (at 11.1 [V])".
    - Mass, size, gearbox: "Weight 57.2 [g]"; "28.5 x 46.5 x 34 [mm]"; "Gear Ratio 258.5 : 1"; "Gear Material Engineering Plastic"; "Motor Cored".
  - Store (https://robotis.us/products/dynamixel-xl430-w250-t): "Regular price $27.50"; "New pricing: Effective June 20th"; "Estimated rated torque: 0.28Nm". The store also says "Weight: 65g", which conflicts with the e-manual.
  - India [U]: https://www.mgsuperlabs.co.in/estore/DYNAMIXEL-XL430-W250-T ; https://www.thingbits.in/products/xl430-w250-t-dynamixel-smart-servo-motor
- **2XL430-W250-T**
  - e-manual: https://emanual.robotis.com/docs/en/dxl/x/2xl430-w250/
    - "1.4 [N.m] (at 11.1 [V], 1.3 [A], 1.077 [Nm/A])"; "Weight 98.2 [g]"; "36 x 46.5 x 36 [mm]"; "Gear Ratio 257.4 : 1"; "Gear Material Full Metal Gear".
  - Store: "$149.39".
  - India [U]: https://www.mgsuperlabs.co.in/estore/2XL430-W250-T
- **XC430-W150-T** (the XC430-T150BB e-manual gives the same electrical specs)
  - e-manual: https://emanual.robotis.com/docs/en/dxl/x/xc430-w150/
    - "1.6 [N.m] (at 12.0 [V], 1.4 [A], 1.143 [Nm/A])"; "6.5 ~ 14.8 [V] (Recommended : 12.0 [V])"; "106 [rev/min] (at 12.0 [V])".
    - "Weight 65 [g]"; "Gear Ratio 159.59 : 1"; "Full Metal Gear".
  - Store: "0.32Nm"; "$137.89". The T150BB-T variant is also $137.89.
- **XC430-W240-T** (same specs as T240BB, which ToddlerBot uses)
  - e-manual: https://emanual.robotis.com/docs/en/dxl/x/xc430-w240/
    - "1.9 [N.m] (at 12.0 [V], 1.4 [A], 1.357 [Nm/A])"; "70 [rev/min] (at 12.0 [V])"; "Gear Ratio 245.22 : 1".
  - Store: "estimated rated torque: 0.38Nm"; "$137.89".
- **2XC430-W250-T**
  - e-manual: https://emanual.robotis.com/docs/en/dxl/x/2xc430-w250/
    - "1.8 [N.m] (at 12.0 [V], 1.4 [A], 1.286 [Nm/A])"; "64 [rev/min] (at 12.0 [V])"; "Weight 102 [g]"; "36 x 46.5 x 36 [mm]"; "Gear Ratio 257.4 : 1".
  - Store: "$298.89". The store's metafields "Dimensions: 28.5x46.5x34mm", "Weight: 65g" and "Estimated rated torque: 0.32Nm" look copied from XC430-W150, so I used 0.20 × 1.8 = 0.36 N·m [E] instead.
  - India [U]: https://www.mgsuperlabs.co.in/estore/DYNAMIXEL-2XC430-W250-T
- **XM430-W210-T/-R**
  - e-manual: https://emanual.robotis.com/docs/en/dxl/x/xm430-w210/
    - Torque, voltage, speed: "3.0 [N.m] (at 12.0 [V], 2.3 [A], 1.304 [Nm/A])"; "3.7 [N.m] (at 14.8 [V], 2.7 [A]"; "10.0 ~ 14.8 [V] (Recommended : 12.0 [V])"; "77 [rev/min] (at 12.0 [V])".
    - Mass, gearbox, loads: "Weight 82 [g]"; "Gear Ratio 212.6 : 1"; "Backlash 15 [arcmin] (0.25 [°])"; "Radial Load 40 [N] (10 [mm] away from the horn)".
    - Sensor and bus: "Part No : AS5045"; "RS-485 / TTL Multidrop Bus".
  - Store: "Estimated rated torque: 0.6Nm"; -T "$310.39"; -R $333.39 (JSON).
- **XM430-W350-T/-R**
  - e-manual: https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/
    - "4.1 [N.m] (at 12.0 [V], 2.3 [A], 1.783 [Nm/A])"; "4.8 [N.m] (at 14.8 [V], 2.7 [A]"; "46 [rev/min] (at 12.0 [V])"; "Gear Ratio 353.5 : 1".
  - Store: "0.82Nm"; -T "$310.39"; -R "$333.39".
  - India [U]: https://www.mgsuperlabs.co.in/estore/DYNAMIXEL-XM430-W350-T ; https://www.mgsuperlabs.co.in/estore/DYNAMIXEL-XM430-W350-R
- **XH540-W150-T/-R**
  - e-manual: https://emanual.robotis.com/docs/en/dxl/x/xh540-w150/
    - "7.1 [N.m] (at 12.0 [V], 4.9 [A], 1.449 [Nm/A])"; "8.5 [N.m] (at 14.8 [V], 5.9 [A]"; "70 [rev/min] (at 12.0 [V])".
    - "Weight 165 [g]"; "33.5 x 58.5 x 44 [mm]"; "Gear Ratio 152.3 : 1"; "Coreless(Maxon)".
  - Store: "1.42Nm"; -T "$620.89"; -R $632.39.
- **XH540-W270-T/-R**
  - e-manual: https://emanual.robotis.com/docs/en/dxl/x/xh540-w270/
    - "9.9 [N.m] (at 12.0 [V], 4.9 [A], 2.020 [Nm/A])"; "11.7 [N.m] (at 14.8 [V], 5.9 [A]"; "39 [rev/min] (at 12.0 [V])"; "Gear Ratio 272.5 : 1".
  - Store: "1.98Nm"; -T "$620.89"; -R $632.39.
- **XM540-W150-T/-R**
  - e-manual: https://emanual.robotis.com/docs/en/dxl/x/xm540-w150/
    - "7.3 [N.m] (at 12.0 [V], 4.4 [A], 1.659 [Nm/A])"; "8.9 [N.m] (at 14.8 [V], 5.5 [A]"; "53 [rev/min] (at 12.0 [V])"; "Gear Ratio 152.3 : 1".
  - Store: "1.46Nm"; -T "$482.89"; -R $494.39.
- **XM540-W270-T/-R**
  - e-manual: https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/
    - "10.6 [N.m] (at 12.0 [V], 4.4 [A], 2.409 [Nm/A])"; "12.9 [N.m] (at 14.8 [V], 5.5 [A]"; "30 [rev/min] (at 12.0 [V])"; "Gear Ratio 272.5 : 1".
  - Store: "2.12Nm"; -T "$482.89"; -R $494.39.
- **ToddlerBot reference** (arXiv 2502.00893, https://arxiv.org/html/2502.00893; a peer-reviewable preprint, [U] as a secondary source)
  - Robot size: "compact size ( 0.56 m , 3.4 kg )".
  - Motor choice: "We choose Dynamixel motors because of their robustness, reliability, and accessibility".
  - Assignments (Table 2):
    - "XC330-T288 1.0 Neck PY (b) , Waist RY, Hip Y, Gripper"
    - "XC430-T240BB 1.9 Shoulder P, Ankle R"
    - "XM430-W210 3.0 Knee P, Ankle P"
    - "2XL430-W250 1.5 Shoulder RY, Elbow RY, Wrist RP"
    - "2XC430-W250 1.8 Hip RP"
  - System-identified maximum torque, Table 3: "τ max 0.94 0.76 1.32 1.09 1.61" N·m, in the order 2XL430, XC330, XC430, 2XC430, XM430-W210.
  - Gearbox efficiency: "gearbox torque efficiency around 58%".
  - Thermal: "increased motor temperatures gradually pushed it outside the policy’s training distribution".

#### 2.7 Hiwonder

**Sources and rules that apply to every model:**
- Official store product pages are at https://www.hiwonder.com/products/<handle>. Specs and prices were read from the store's Shopify catalogue at https://www.hiwonder.com/products.json on 2026-09-24 [V].
- Every page gives "UART serial command" and "Communication baud rate 115200". The exceptions are HX-30HM and HX-10HM ("Default: 1000000") and HX-08LC ("TTL single-wire serial commands").
- The servo-level packet format (0x55 0x55 header, half-duplex UART) comes from a Hiwonder LX-16A manual hosted by RobotShop. I saw it only in search results and did not read it [U]: https://cdn.robotshop.com/rbm/a5e9ab51-86bc-497b-adac-003de3088fb7/9/92896585-5e83-4c7c-a663-650b81e5978b/67e9729b_lx-16a-serial-bus-servo-user-manual.pdf
- docs.hiwonder.com describes the **controller's** protocol, not the servo's.
- No Hiwonder page publishes a gear ratio.

- **LX-824** (https://www.hiwonder.com/products/lx-824)
  - "Torque | 17 kg·cm (236 oz·in) @7.4V"; "Working Voltage | 6-8.4V"; "Speed | 0.20sec/60°(7.4V)".
  - "Weight | 57g(2.02OZ)"; "40.00mm*20.14mm*51.10mm"; "Stall Current | 2.4~3A"; "0~1000 correspond to 0°~240°".
  - "Use high-precision potentiometer to feedback the angle position"; price $13.99.
- **LX-824HV** (…/lx-824hv)
  - "Torque | 17kg.cm/11.1V(LX-824HV)"; "Working Voltage | 9-12.6V"; "Speed | 0.20sec/60°(11.1V)".
  - "Weight | 57g（LX-824HV）"; "Stall Current | 1.7~2A"; price $17.99.
- **LX-224** (…/lx-224)
  - "Torque | 20kg.cm 7.4V"; "Working voltage | 6-8.4V"; "Speed | 0.20sec/60°7.4V".
  - "Weight | 63g"; "Size | 40*20.14*51.1mm"; "Stall Current | 2.4~3A"; "Gear | Metal".
  - "The servo adopts a high-precision potentiometer"; price $15.99.
- **LX-224HV** (…/lx-224hv)
  - "Torque | 20kg.cm/11.1V"; "Speed | 0.18sec/60°(11.1V)"; "Weight | 62g"; "Accuracy | 0.24°"; "Stall Current | 1.7~2A"; price $19.99.
- **LX-225** (…/lx-225)
  - "Torque | 25kg.cm 7.4V"; "Working voltage | 6-8.4V"; "Speed | 0.20sec/60°7.4V".
  - "Weight | 63g"; "Stall Current | 4A"; "Gear | Metal"; price $17.99.
- **HTD-30H** (…/htd-30h)
  - "Stalled rotor torque | 30kg.cm 12.6V"; "Rotation speed | 0.12sec/ 60° 12.6V".
  - "Weight | 63g"; "Size | 40.0*20.1*51.1mm"; "Locked rotor current | 3.2A".
  - "imported high-precision potentiometer as angle feedback"; price $19.99.
  - The HTD comparison table on this page gives the housing: "Plastic Top and Bottom Shells with CNC-Machined Metal Middle Shell".
- **HTD-35H** (…/htd-35h)
  - "Torque | 35kg.cm 11.1V"; "Working voltage | 9-12.6V"; "Speed | 0.18sec/60°11.1V".
  - "Weight | 64g"; "Size | 51.1*20.14*40mm"; "Stall Current | 3A"; potentiometer; price $22.99.
- **HTD-45H** (…/htd-45h)
  - "Locked torque: | 45kg.cm 11.1V"; "Static maximum torque: | 45kg.cm 11.1V"; "Working voltage: | 9-12.6V"; "Rotation speed: | 0.18sec/60°11.1V".
  - "Weight: | 64g"; "Dimension: | 51.1×20.14×40mm"; "Stall current: | 3A"; "Gear type: | Metal gear".
  - "High-precision potentiometer for more stable operation"; price $24.99.
  - Other markets [U]: RobotShop https://www.robotshop.com/products/hiwonder-hiwonder-htd-45h-high-voltage-serial-bus-servo-w-45kg-torque-three-connectors-data-feedback and Amazon.com https://www.amazon.com/Hiwonder-HTD-45H-Voltage-Connectors-Feedback/dp/B0CB3T1P7Y
- **HTD-85H** (…/htd-85h)
  - "stall torque of up to 85 kg·cm at 11.1V"; "Working voltage | 9-14.8V"; "Rotation speed | 0.2sec /60° 11.1V".
  - "Weight | 153g"; "Size | 65.01mm x 30.00mm x 62.20mm"; "Stall current | 5A".
  - "Equipped with stainless-steel gears"; "Rotation range | 0°~240°". **The page does not state the angle sensor type.** Price $39.99.
- **HTS-35H** (…/hts-35h)
  - "Torque | 35kg.cm 11.1V"; "Speed | 0.18sec/60°11.1V"; "Weight | 64g"; "Size | 40*20*40.5mm"; "Servo accuracy | 0.2°"; price $21.99.
- **HTS-30HS** (…/hts-30hs)
  - "Stalled rotor torque | 30kg.cm 12V"; "Rotation speed | 0.10sec/ 60°12V"; "Weight | 64g"; "Locked rotor current | 3.2A".
  - "The gears are made of stainless steel"; price $45.99.
- **HX-35H** (…/hx-35h)
  - "Static maximum torque | 35kg.cm 11.1v"; "Rotation torque | 25kg.cm 11.1v"; "Rotation speed | 0.18sec / 60° 11.1v".
  - "Weight | 52g"; "Dimension | 45.2 x 24.7 x 35mm"; "high-accuracy potentiometer and metal gear".
  - Price $18.99 (compare-at $21.99).
- **HX-35HM** (…/hx-35hm)
  - "Static maximum torque | 35kg.cm 11.1V"; "Rotation torque | 25kg.cm 11.1V"; "Rotation speed | 0.19sec/60°11.1V".
  - "Weight | 71g"; "Controllable angle range | 0~1500, corresponding to 0~360°"; "12-bit high precision angle magnetic encoder".
  - Price $35.99.
- **HX-30HM** (…/hx-30hm)
  - **The spec table rows are shifted by one:** the value "30 kg·cm at 11.1 V" sits under "Protection".
  - "Rotation speed | 0.19 sec/60° at 11.1 V"; "Weight | 52 g"; "Size | 45.2 x 24.7 x 35 mm"; "0~4095, corresponding to 0~360°"; "Default: 1000000".
  - The page text is copied from HX-10HM: "HX-10HM servo adopts an advanced 360° magnetic encoder".
  - Price $19.99.
- **HX-10HM** (…/hx-10hm): "10 kg·cm at 11.1 V" (same shifted table); "Rotation speed | 0.10 sec/60° at 11.1 V"; price $17.99.
- **HX-65HM** (…/hx-65hm)
  - "Stall Torque | 65KG@12.6V, 50KG@9.6V"; "Rated Torque | 50KG@12.6V, 35KG@9.6V"; "Rotation speed | 0.19sec/60°11.1V".
  - "Weight | 143.5g"; "Size | 45mm x 25mm x 70mm"; "Stall current | 5A".
  - "equipped with two high-quality magnetic motors"; "built-in 12-bit high-precision magnetic angle sensor". Price $49.99.
- **HX-08LC** (…/hx-08lc)
  - "Stall torque | 8 kg·cm @ 7.4 V"; "Dynamic torque | 3 kg·cm @ 7.4 V"; "Speed | 0.06 s / 60° @ 7.4 V".
  - "Weight | 26 g"; "A high-precision potentiometer delivers real-time angle readback"; price $34.99.
- India [U, search only]:
  - ThinkRobotics' Hiwonder collection, https://thinkrobotics.com/collections/hiwonder. The search snippet calls it Hiwonder's "official and largest distributor"; this was not checked.
  - Robu.in's Hiwonder category, https://robu.in/product-category/hiwonder-servo-motor-and-accessories/

### 3. Known failure modes and limits

1. **Stall torque is not usable torque.**
   - ROBOTIS itself says stall is "the maximum momentary torque" [V]. Its store uses 20% of stall as the continuous estimate [V].
   - Feetech rated torque is ≈ 33% of stall (STS/SCS/SM) or ≈ 25% (HLS) [V].
   - Independent tests [U]:
     - STS3250: at 40% of stall (20 kg·cm), it reached the 70 °C thermal cut-off in about 8 min.
     - STS3215 C018: stable at 15 kg·cm (+15 °C in 10 min), but hit overload protection at 20 kg·cm after a few cycles. It reached 71 °C, "resulting in overheating", after ~110 min of ±90° oscillation.
     - ToddlerBot's system-identified τmax is 54–76% of the 12 V stall rating: XC330 0.76/1.0, XM430-W210 1.61/3.0.
   - **Design rule for JX1:** pick servos whose *rated* torque covers the continuous gravity and holding load of the arm pose, and treat stall as the short-burst limit.
2. **Protection trips make the joint go limp.**
   - Feetech overload protection drops output to 20% for 2 s [V, 2020 article].
   - Dynamixel sets Torque Enable to 0 on overheating or overload when that error is configured in Shutdown [V].
   - For a standing or walking humanoid, the controller must poll temperature and load and derate before either trip happens.
   - Hello Robot's Stretch team says it is possible for "Stretch Dynamixel servos to become overloaded or overheated during normal operation" (https://forum.hello-robot.com/t/handling-dynamixel-servo-overload-errors/613) [U].
3. **Backlash and stiffness.**
   - Specs [V]: XM/XH/X540 are 15 arcmin (0.25°). HLS3960, SM105B and SM160B are ≤0.5°. HLS2915 is ≤1°.
   - Measured [U]: STS3215 C018 was 0.87°, worse than its ≤0.5° datasheet value. STS3250 was 0.43°.
   - STS3250 torsional stiffness was ~91 N·m/rad [U]. At the end of a 0.3 m arm that is about 1 mm of deflection per 0.3 N·m [E: 0.3 ÷ 91.2 = 3.3 mrad; × 0.3 m ≈ 1.0 mm].
4. **Gear material.**
   - XL430-W250 uses engineering-plastic gears and XL330 uses plastic [V]. They are risky under humanoid falls. I found no specific stripping reports in a quick search, so this is a qualitative caution.
   - STS3215 7.4 V, STS3035, SCS15/215 and HLS3625/3925/3620 use copper gears [V]. The STS/HLS 12 V and larger models use steel [V]. HTD-85H and HTS-30HS use stainless steel [V].
   - ToddlerBot "withstands up to 7 falls before breaking". Those were printed parts, not servos [U].
5. **Potentiometer vs magnetic sensing.**
   - SCS, LX, HTD, HTS, HX-35H and HX-08LC use potentiometers with a limited range (Hiwonder 240°, SCS 220–300°) [V]. They wear and lose linearity over time; that is general knowledge, not a sourced claim.
   - STS, HLS, SM, Dynamixel and Hiwonder HX-..HM use 12-bit magnetic encoders over 360°. Multi-turn position is not retained after power-off on Feetech (±7 turns) [V].
6. **Supply voltage mistakes.**
   - Seeed/LeRobot warns that mixing 7.4 V and 12 V STS3215 supplies can "burn your motors" [U].
   - Many parts come in LV and HV variants with the same body: STS3215 C001/C018, LX-224/LX-224HV, LX-824/LX-824HV. Label the harnesses clearly.
7. **Communication robustness.**
   - LeRobot GitHub issues "Feetech sts3215 serial servos read failure" (#526) and "Cannot set up servo sts3215" (#1244) [U; titles seen in search results only] (https://github.com/huggingface/lerobot/issues/526 , https://github.com/huggingface/lerobot/issues/1244).
   - TTL half-duplex buses need short, well-grounded cables. For long humanoid limb runs, prefer the RS-485 variants (Feetech SM, Dynamixel -R).
8. **Datasheet inconsistencies are common on Feetech and Hiwonder pages** (listed per model in §2), for example:
   - STS3215 7.4 V: stall is 16.5 vs 19.5 kg·cm, and the voltage is given as 6 V or 7.4 V.
   - HLS3960: 60 vs 66.8 kg·cm.
   - SM45BL: 35 vs 70 rpm.
   - HX-30HM: shifted table rows.
   - Treat any single Feetech or Hiwonder number as ±15% until bench-tested.

### 4. Gaps and follow-ups

- **Current official Feetech prices** (AliExpress official store and Taobao) could not be read without JavaScript or an anti-bot bypass, so all Feetech $/N·m figures rest on reseller prices [U].
  - Follow-up: ask Feetech sales for an INR/CNY quote on 50–200 pcs of STS3250, HLS3950, STS3095 and SM80BL/SM105B. Contact listed on their site: aaron@feetechrc.com.cn, +86 755 89335266. This needs the user's go-ahead.
- **Feetech detailed PDF datasheets** (torque–speed curves, life test) were not read because binary downloads are not allowed.
  - WebFetch could not parse the Seeed-hosted Feetech protocol PDF. The harness auto-saved a copy under the session's tool-results folder; it was not opened or used.
- **ROBOTIS rated torque** is only the store's 20% rule. The e-manual performance-graph images (N–T curves) were not digitised.
- **Hiwonder:**
  - No gear ratios, no rated torque (apart from marketing claims), no measurement-voltage conditions for stall current, and no sensor type for HTD-85H.
  - No independent torque or thermal tests were found for any Hiwonder model. That matters, because Hiwonder has the best $/N·m, so these servos should be bench-tested first: stall and hold torque at 11.1 V, a thermal soak at 30–40% of stall, and backlash.
- **Not found:** SM70BL price; SM-105B-C001 (12 V) page; confirmation of what STS3250 "C002" is.
- **India:** resellers noted from search results only (Evelta, ThinkRobotics, Robu.in, MG Super Labs, Thingbits). Nothing was checked for INR price, stock or GST. No Robokits listing turned up in these searches.
- **2-axis Dynamixel:** the store's metafields are wrong for 2XC430 (copied from XC430-W150). I used e-manual values.
- **Reliability evidence** is thin and mostly from tests and forums [U]. No field MTBF numbers exist for any brand.

## 3. DIY actuators: hobby BLDC plus printed or machined reducer (open designs, numbers, failure modes)


Research date: 2026-09-24. Scope: concrete open-source DIY actuator designs, with numbers, for JX1 (humanoid about 1.2 m tall, 20–30 kg, 6-DOF legs). Torque classes are large 40–90 N·m, medium 15–40 N·m and small 3–15 N·m, at 8–20 rad/s.

**Labels**
- **VERIFIED (V):** I read it today on the primary source: the paper, the official repo, README or BOM, the official docs or store, or the author's own site, project page or video description.
- **ESTIMATED (E):** I derived it; the arithmetic is shown in §1b.
- **UNVERIFIED (U):** it comes from a forum, a secondary article, a reseller, a third-party page or a reader comment.

**Evidence fragments.** `ev:` marks a short fragment (15 words or fewer) copied from the source so the number can be audited. Fragments are kept to the minimum data needed.

**Exchange rates, used only for conversions (V).** ECB euro reference rates dated 2026-09-23 (https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml):
- 1 EUR = 1.1411 USD, 7.6538 CNY and 109.25 INR.
- Derived (E): 1 USD = 7.6538 / 1.1411 = 6.707 CNY, and 1 USD = 109.25 / 1.1411 = 95.74 INR.
- BOM prices stay in the currency and year the source gave. Conversions are indicative only and exclude shipping, import duty and GST.

---

### 1. Master table

**Abbreviations**
- n/p: not published in the sources read.
- n/s: not stated.
- Peak and Cont.: output-side torques as the source defines them. Qualifiers are in brackets.
- N·m/kg and USD per peak N·m are (E) unless marked otherwise. Arithmetic is in §1b.

#### 1a. DIY and open-source designs

| # | Design (org, year) | Motor (model / KV / size) | Reducer type & ratio | Reducer material & bearings | Peak N·m | Cont. N·m | Mass g | BOM cost (currency, year) | Driver / controller | Encoder | Interface | License | N·m/kg | USD / peak N·m | Label(s) | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | **Berkeley Humanoid Lite "6512"** (UC Berkeley, 2025) | MAD Components M6C12 (EEE) 150 KV; 72 mm OD class; 14 pole pairs; Kt 0.0919 N·m/A | Cycloidal, 15:1 (16 housing rollers), dual disks | PLA (FDM, Bambu X1C profile); brass hex standoff in input shaft; through-screws; 6811ZZ main bearing | n/p. At least 20 applied in stiffness test (V); about 24.8–27.6 current-limited ceiling (E) | n/p (sim/robot limit 6) | n/p (printed PLA parts 164 g) | US$188 (US) / US$157 (China), 2025 | ST B-G431B-ESC1 (STM32G431CB) running "Recoil" firmware | AS5600 12-bit magnetic, I2C, motor side | CAN 2.0 classic, 1 Mbps | Code MIT; hardware CC BY-SA 4.0; print files CC BY | n/p | 9.4 (US, at 20) / 7.9 (CN, at 20) | V + E | arxiv.org/abs/2504.17249; github.com/HybridRobotics/Berkeley-Humanoid-Lite; berkeley-humanoid-lite.gitbook.io/docs |
| 2 | **Berkeley Humanoid Lite "5010"** (2025) | MAD 5010 110 KV; Kt 0.1176 N·m/A; 14 pole pairs | Cycloidal, 15:1 | PLA (FDM) | n/p (sim limit 6 ankles, 4 arms) | n/p | n/p | US$136 (US) / US$94 (China), 2025 | B-G431B-ESC1 + Recoil | AS5600 | CAN 2.0, 1 Mbps | as #1 | n/p | n/p | V | as #1 |
| 3 | **ODRI / Solo-8 / Solo-12 module** (MPI-IS / NYU, 2019–20) | T-Motor Antigravity 4004 300 KV; 53 g; 12 pole pairs; 45 mm rotor | 2-stage timing belt (Conti Synchroflex AT3 GEN III), 3:1 × 3:1 = 9:1 | Printed pulleys (SLA/Multijet); T10 motor & center pulleys machined aluminium; shells SLS Duraform HST or FDM PC-ABS; EZO stainless bearings | 2.7 at 12 A (paper) / 2.5 at 12 A (repo) | n/p | 150 (incl. 160 mm segment shell) | n/p (µDriver parts ~€50 per 2-motor board) | MPI Micro-Driver (TMS320F28069M + 2× DRV8305), dual-axis | Optical Broadcom AEDT-9810 / AEDM-5810, 5000 CPR code wheel | SPI to ESP32 master board (1 kHz); CAN port present; master board to PC via Ethernet/WiFi | BSD-3 (hardware), BSD-2 (master board) | 18.0 (paper) / 16.7 (repo) | n/p | V + E | arxiv.org/abs/1910.00093; github.com/open-dynamic-robot-initiative/open_robot_actuator_hardware |
| 4 | **Stanford Doggo** (Stanford Student Robotics, 2019) | T-Motor MN5212 KV340 | 1-stage GT2 3 mm belt, 16T→48T = 3:1 | Printed pulleys (SLS, Xometry); printed bearing block; waterjet Al tension bracket | 4.8 | 1.51 (to 125 °C winding, no cooling) | 270 (motor + transmission) | US$120 per actuator (paper); robot BOM US$2,971, 2018–19 | ODrive v3.5 (dual-axis) | AS5047, 2000 CPR (incremental) | UART 500 kbaud from Teensy 3.5 | MIT | 17.8 (paper) | 25.0 | V + E | arxiv.org/abs/1905.04254; github.com/Nate711/StanfordDoggoProject |
| 5 | **Urs et al. 7.5:1** (U-Michigan EMBiR, 2022) | T-Motor RI50 (inner-rotor, *not* outrunner); Kt 0.105 N·m/A; 193 g; US$62 | Single-stage planetary 7.5:1, 30° pressure angle | Transmission FDM PLA; motor housing & rotor-sun gear SLA High-Temp resin (Form 3); steel dowel pins | 19.1 (2 s) / 7.5 (20 s), thermally predicted | 4.4 (with 2 fans) | 482 | US$193.78 (BOM sheet), 2022 | mjbots moteus (r4.5 in paper; r4.8 in BOM), US$84 | moteus on-board magnetic encoder (magnet on rotor-sun gear) | CAN-FD (moteus family; version-specific spec not re-read) | Paper CC BY 4.0; repo: no license file found | 39.6 (2 s) / 15.6 (20 s) | 10.1 (2 s) / 25.8 (20 s) | V + E (U for interface) | arxiv.org/abs/2202.12395; github.com/EMBiRLab/3DP-Actuator |
| 6 | **Urs et al. 15:1 Wolfrom** (2022) | T-Motor RI50 | Wolfrom compound planetary 15.04:1 | as #5 | 38.2 (2 s) / 15 (20 s), thermally predicted | 8.8 | 536 | US$197.46 (BOM sheet), 2022 | moteus | as #5 | as #5 | as #5 | 71.3 (2 s) / 28.0 (20 s) | 5.2 (2 s) / 13.2 (20 s) | V + E | as #5 |
| 7 | **Roozing & Roozing 2022, pinwheel cycloid** (U Twente) | T-Motor Antigravity 8012 (KV n/s) | Cycloidal 11:1, 2 disks, 12 rollers + 6 output pins, all on ball bearings | PLA (Prusa MK3S+); 36 small bearings on shoulder screws; 4-point thin-section output bearing | 36.4 nominal (40 A, thermally limited); 44 tested static | n/p | 372 gearbox; **809 total** (incl. motor & cooling) | Gearbox €98; motor €123; ODrive €179; encoders €32 (2022) | ODrive v3.6 56 V (dual-axis) | 2× AS5048A (motor + output) | USB/serial (Python) in tests | MIT | 45.0 (36.4) / 54.4 (44) | 10.7 (half-ODrive share) | V + E | ris.utwente.nl/ws/portalfiles/portal/295490006/…; github.com/geez0x1/2022-cycloidal-drive |
| 8 | **Roozing & Roozing 2024, PA6-CF non-pinwheel** (and pinwheel) | T-Motor Antigravity 8012 | Cycloidal 11:1; non-pinwheel internal cycloid profile (or pinwheel) | PA6-CF (Fibertree F3 PA-CF Pro, 15% CF), FDM Prusa MK3S+ | 36.4 nominal (40 A) | n/p | 360 gearbox (non-pinwheel) / 377 (pinwheel) | Gearbox €65 (non-pin) / €98 (pin), 2023–24 | ODrive v3.6 at 40 V | CUI AMT23 14-bit (motor) + AS5048A (output) | USB/serial | MIT | ≈45.7 (E, mass assumed) | ≈9.7 (E) | V + E | ICRA 2024 paper (read via mirror, see §2.8); github.com/geez0x1/2023-cycloidal-drive-nonpinwheel |
| 9 | **OpenTorque v2** (Gabrael Levine, 2018–19) | Herlea X8318S KV100 ("Multistar 9235") | Planetary 8:1 | Nylon (Taulman Alloy 910) sun & planets; v2 single cross-roller bearing | 80 "theoretical" (a reader estimated ~40, U) | n/p | 1150 | ~US$150 (2018–19; driver apparently not included) | ODrive v3.x | AS5048A | via ODrive (Blackbird used CAN through MCP2515) | CC BY-SA 4.0 | 69.6 theoretical | 1.9 theoretical | V (claims) + E + U (performance) | hackaday.io/project/159404-opentorque-actuator; github.com/G-Levine/OpenTorque-Actuator |
| 10 | **Aaed Musa OpenQDD V1** (2023) | Eagle Power 90 KV (CARA pages name the 8308) | Planetary 9:1, helical | 3D printed (material n/s); 13 printed parts | 16.36 "peak holding" | n/p | 935 | US$247 total (2023) | ODrive S1 (US$150 per CARA 2.0 page) | ODrive S1 on-board | ODrive S1 (bus not stated on page) | none found in repo root | 17.5 | 15.1 | V + E | aaedmusa.com/projects/openqdd; github.com/aaedmusa/OpenQDD-V1 |
| 11 | **Aaed Musa internal cycloidal** (2024) | Custom 10010 stator (36N42P), hand-wound; steel-1045 rotor | Cycloidal 8:1 inside stator bore | Roller-pin ring machined Al 6061; other parts printed | 16.17 | n/p | 1023 | US$384 (2024) | ODrive S1 | ODrive S1 on-board | n/s | none found | 15.8 | 23.7 | V + E | aaedmusa.com/projects/internalcycloidalactuator |
| 12 | **Aaed Musa CARA 1.0 capstan** (2025) | Eagle Power 8308, 90 KV; 340 g; stall 1.67 N·m (author-measured) | Capstan (rope) 8:1, 2 mm Dyneema DM20 | Small drums PET-CF (100% infill); structure PC | n/p (ideal 13.4, E) | n/p | n/p | ≈US$250 per actuator (author) | ODrive S1 | ODrive S1 on-board | CAN to Teensy 4.1 | none found | n/p | ≈18.7 (at ideal 13.4) | V + E | aaedmusa.com/projects/cara; aaedmusa.com/projects/cara2 |
| 13 | **Aaed Musa CARA 2.0 capstan joint** (2026) | TYI 5008, rewound 335→90 KV; 160 g; stall 1.274 N·m; US$18 | Capstan 9.6:1 | Printed (material n/s on page); pre-stretched rope | 12 | n/p | 470 (joint) | Motor US$18 + driver US$41 (2026) | MKS XDrive Mini (ODrive 3.6 clone) | on-board | UART worked; CAN needed custom community firmware | none found | 25.5 | ≥4.9 (motor + driver only) | V + E | aaedmusa.com/projects/cara2 |
| 14 | **James Bruton openDog V3 cycloid** (2021) | n/p in text sources (only in video / BOM.ods) | Cycloidal, 2 disks; ≈10:1 (E, from code) | PLA; cycloid internals 4 perimeters, 30–40% infill; "a lot of bearings" | n/p | n/p | n/p | Robot ≈US$2,000 (U) | ODrive v3.x (6 boards for 12 axes); current_lim 20 A | AS5047 (absolute mode) | UART from Teensy 4.1 | MIT | n/p | n/p | V + E + U | github.com/XRobots/openDogV3; github.com/XRobots/CycloidalDrive; YouTube descriptions |
| 15 | **Paul Gould cycloid** (2018–21) | Multistar Elite outrunner; later Gartt ML5010 300 KV | Cycloidal 25:1 with rolling elements, dual input/output shafts | ABS (FDM) + bearings | Target 20; tested ~10 (author comments) | n/p | n/p | ≈US$150 (author comment) | Custom PSoC4 (CY8C4247) + DRV8305, 100 A-class FETs | 2× AS5147 (motor + joint) | CAN + UART | n/s ("open source" project) | n/p | 15 (at 10 tested) | V (author comments) + E | hackaday.io/project/157812-3d-printed-robot-actuator |
| 16 | **Skyentific stepper compound planetary** (2021–24) | NEMA stepper (not BLDC) | Compound planetary 1:84 (US$32 version); ~1:100; "Callisto" 4 × 28 = 1:112 | Printed, including 3D-printed cross-roller bearings | n/p in descriptions | n/p | n/p | US$32 joint (2021); CAD files US$21.60 | Stepper driver | n/p | n/p | Paid files (Patreon / store) | n/p | n/p | V | YouTube a1sZSIDxpfg, BTzkSg_l70M; skyentific.com |
| 17 | **COMPAct SSPG** (IISc Bengaluru + IIT Roorkee, 2025–26) | T-Motor MN8014 (87.8 mm OD) | Single-stage planetary 7.2:1 | PLA, 100% infill, Bambu X1C; bolt-reinforced sun shaft; through-bolt skeleton | Tested to 18 (efficiency) and ±20 (stiffness) | n/p | n/p | n/p | ODrive Pro or moteus | n/s | n/s | MIT (code); paper CC BY 4.0 | n/p | n/p | V | arxiv.org/abs/2510.07197; github.com/singhaman1750/COMPAct |
| 18 | **COMPAct CPG** (2025–26) | MAD M6C12 (72 mm OD) | Compound planetary 14:1 | PLA as #17 | as #17 | n/p | n/p | n/p | as #17 | n/s | n/s | as #17 | n/p | n/p | V | as #17 |
| 19 | **QLAUN** quadruped actuator (LAU, 2024; arXiv 2026) | mjbots MJ5208 330 KV (193 g, 1.7 N·m motor peak per mjbots) | Printed 8:1 helical planetary, plus 4:1 belt at hip/knee (32:1 at joint) | PLA | "up to 5" at 40% power (actuator) | n/p | n/p | n/p | ODrive Pro; 20 V, ≤30 A | AMT103-V, 2048 PPR incremental | n/s | arXiv license only | n/p | n/p | V | arxiv.org/abs/2609.03623 |
| 20 | **mjbots qdd100 beta 3** (metal reference) | Motor n/s on store page (the matching 6x gearset "fits inside the stator of 8108 and larger" motors) | Steel planetary 6:1 (100T ring / 20T sun / 40T planets) | 42CrMo / C40Cr steel, HRC 25; needle-bearing planets | 16 (<1 s); 10 for 60 s; 6 for 400 s | 3.3 indefinite | 507 | US$879 (store; **not stocked, MOQ 50**) | Integrated moteus | on-board | 5 Mbps CAN-FD | moteus firmware Apache-2.0 | 31.6 | 54.9 | V + E | mjbots.com/products/qdd100-beta-3 |

#### 1a-ref. Non-DIY benchmarks (for cost and performance comparison only)

| # | Reference | Motor / reducer | Peak N·m | Cont. N·m | Mass g | Cost | Driver / interface | N·m/kg | USD/N·m | Label | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | UCLA C-QDD (machined 4140-steel cycloid, 2024) | BLDC with 10:1 non-pinwheel steel cycloid inside stator | 89.9 (120 expected; driver current-limited) | 37.5 | 1400 | n/p | CubeMars Driver Board V2.1 | 64.2 (paper) | n/p | V | arxiv.org/abs/2410.16591 |
| R2 | Open Source Leg v2 (UMich) | Dephy actuator (9:1 planetary) + 4.61:1 belt = 41.5:1 | ~145.25 instantaneous (25 A) | ~29 (5 A) | 5,400 knee + ankle system | US$23,100 per leg build (actuators + batteries US$12,630) | Dephy | n/a | ≈43.5 per joint (E) | V + E | opensourceleg.org/hardware/ |
| R3 | Skyentific "AK10-9 + moteus" | CubeMars AK10-9, 9:1 | 48 | 18 (rated) | 960 | US$1,512 | moteus, CAN | 50.0 | 31.5 | V + E | skyentific.com/products/p10-planetary-qdd-actuator |
| R4 | Stanford Pupper v3 | "4005 brushless motor" + 10:1 planetary | ~3.5 | ~1.0 (air cooled) | n/p | Robot "about $2000" | n/s | n/p | n/p | V | pupper-v3-documentation.readthedocs.io/en/latest/learn_more/tech_specs.html |
| R5 | Roboto Origin "ATOM 01" (RoboParty, 2025–26) | Commercial Damiao DM4340P ×14 (¥949 each) and DM10010L ×9 (¥1,989 each) | n/p | n/p | n/p | Robot BOM ¥49,713 (≈US$7,412, E) | CAN via USB-CAN | n/p | n/p | V + E | github.com/Roboparty/roboto_origin (assets/BOM_EN.md) |
| R6 | Duke Humanoid (2024) | Motorevo planetary actuators: 18:1 "72 N·m rated", 20:1 "80 N·m rated", 10:1 "40 N·m rated" | n/p | 72 / 80 / 40 rated | n/p | n/p | EtherCAT 2 kHz | n/p | n/p | V | arxiv.org/abs/2409.19795 |

Other projects checked and excluded:
- K-Scale Zeroth Bot: Feetech servos, "BoM starts at $350", MIT license (github.com/kscalelabs/zeroth-bot). Servo-based, so excluded.
- USC HECTOR: 16 kg, 0.85 m, QDD plus timing belt; knee amplified by a 1.55:1 belt to 51.93 N·m (arxiv.org/abs/2312.11868). Uses commercial QDD actuators.
- AGILOped: "off-the-shelf backdrivable actuators", 110 cm, 14.5 kg (arxiv.org/abs/2509.09364).

#### 1b. How the ESTIMATED (E) numbers were derived

- **BHL 6512 current-limited ceiling.**
  - Ideal torque = Kt × I_limit × N = 0.0919 N·m/A × 20 A × 15 = 27.57 N·m.
  - With the firmware's active Kt of 0.08958: 26.87 N·m.
  - Applying the paper's ~90% mechanical efficiency: 27.57 × 0.9 = 24.8 N·m.
  - This is a ceiling, not a rating. The only torque the paper documents being applied is the 0–20 N·m stiffness ramp.
  - Cost: US$188 / 20 N·m = 9.40 US$/N·m (US BOM); US$157 / 20 = 7.85 (China BOM). Against the 27.57 ceiling: 6.82 (US) and 5.69 (China).
- **BHL 5010.** Kt × I × N = 0.1176 × 20 × 15 = 35.3 N·m. This is **not a meaningful rating**: the gearbox is smaller, the winding resistance is 0.62 Ω, and it was never tested. Shown only as a warning against naive calculation.
- **BHL durability-test load.** A 0.5 kg pendulum at 0.5 m gives a maximum gravity torque of 0.5 × 9.81 × 0.5 = 2.45 N·m, about 9–12% of the 20–27.6 N·m capability. Cycles: 60 h × 3600 s/h × 0.5 Hz = 108,000 cycles.
- **ODRI:** 2.7 N·m / 0.150 kg = 18.0 N·m/kg (repo figure 2.5 / 0.150 = 16.7). Check: k_i × i × N = 0.025 × 12 × 9 = 2.70 N·m, matching the paper.
- **Doggo:** 4.8 / 0.27 = 17.8 N·m/kg (matches the paper's own 17.8). US$120 / 4.8 N·m = 25.0 US$/N·m.
- **qdd100:** 16 / 0.507 = 31.6 N·m/kg; US$879 / 16 = 54.9 US$/N·m.
- **Urs 7.5:1:**
  - 19.1 / 0.482 = 39.6 and 7.5 / 0.482 = 15.6 N·m/kg.
  - US$193.78 / 19.1 = 10.15; US$193.78 / 7.5 = 25.8.
  - The paper's rounded BOM check: 62 + 84 + 3.5 + 16 + 15 + 8 + 10 = US$198.5, consistent with "<$200".
- **Urs 15:1:** 38.2 / 0.536 = 71.3 and 15 / 0.536 = 28.0 N·m/kg. US$197.46 / 38.2 = 5.17 and US$197.46 / 15 = 13.2 US$/N·m.
- **Roozing 2022:**
  - Density: 36.4 / 0.809 = 45.0 N·m/kg; 44 / 0.809 = 54.4 N·m/kg.
  - Cost with half of a dual-axis ODrive: €98 + €123 + €32 + €179/2 = €342.5 × 1.1411 = US$391. Divided by 36.4 N·m = 10.7 US$/N·m.
  - With the full ODrive: €432 → US$493 → 13.5 US$/N·m.
  - Gearbox alone: €98 → US$112 → 3.07 US$/N·m.
- **Roozing 2024 non-pinwheel:**
  - Mass: the paper gives only gearbox mass. I assumed the motor-plus-cooling mass equals 2022's (809 − 372 = 437 g). Total ≈ 360 + 437 = 797 g, so 36.4 / 0.797 = 45.7 N·m/kg.
  - Cost: €65 + €123 + €32 + €89.5 = €309.5 → US$353 → 9.7 US$/N·m.
- **OpenTorque:** 80 / 1.150 = 69.6 N·m/kg; US$150 / 80 = 1.88 US$/N·m. Both use the *theoretical* torque and a cost that apparently excludes the driver. At the reader's ~40 N·m estimate: 34.8 N·m/kg and 3.75 US$/N·m.
- **Aaed Musa:**
  - OpenQDD: 16.36 / 0.935 = 17.5 N·m/kg; 247 / 16.36 = 15.1 US$/N·m.
  - Internal cycloid: 16.17 / 1.023 = 15.8 N·m/kg; 384 / 16.17 = 23.7 US$/N·m; 209 rpm × 2π / 60 = 21.9 rad/s.
  - CARA 2.0 joint: 12 / 0.470 = 25.5 N·m/kg; (18 + 41) / 12 = 4.9 US$/N·m. This covers motor and driver only; printed parts, rope and bearings are excluded.
  - CARA 1.0: ideal 8 × 1.67 N·m stall = 13.4 N·m; US$250 / 13.4 = 18.7 US$/N·m.
- **James Bruton ratio.** The code converts 0.02777… motor turns per degree, i.e. 1/36 turn per degree → 10 motor turns per 360° of joint → ≈10:1. This assumes the ODrive position units are motor turns, which is the ODrive convention.
- **Paul Gould:** US$150 / 10 N·m (tested) = 15; US$150 / 20 N·m (target) = 7.5 US$/N·m. Backlash of 0.3 mm at 200 mm = 1.5 mrad; 1 mm at 200 mm = 5 mrad.
- **References:**
  - C-QDD: 89.9 / 1.40 = 64.2 N·m/kg.
  - AK10-9: 48 / 0.96 = 50.0 N·m/kg; 1512 / 48 = 31.5 US$/N·m.
  - OSL: 12,630 / 2 joints / 145.25 = 43.5 US$/N·m. This includes batteries and uses a calculated, not measured, peak.
  - Roboto BOM: 49,713 / 6.707 = US$7,412; DM4340P ¥949 ≈ US$141; DM10010L ¥1,989 ≈ US$297.
- **INR equivalents (indicative, E):**
  - BHL 6512 at the China BOM: 157 × 95.74 = ₹15,031. At the US BOM: 188 × 95.74 = ₹17,999.
  - BHL 5010 (China): 94 × 95.74 = ₹9,000.
  - Urs 7.5:1: 193.78 × 95.74 = ₹18,552.
  - Roozing-class large joint: US$353–391 → ₹33,796–37,434.
- **Scaling BHL leg torque to JX1 (E, crude).** Joint torque scales roughly with m·g·h. (25 kg / 16 kg) × (1.2 m / 0.8 m) = 2.34× (range 1.87× at 20 kg to 2.81× at 30 kg). This ignores gait and speed differences.

---

### 2. Per-design notes (all sources read 2026-09-24)

#### 2.1 Berkeley Humanoid Lite (BHL): 6512 and 5010 actuators

Sources:
- [B1] Paper, arXiv 2504.17249v1 (24 Apr 2025, RSS 2025): https://arxiv.org/abs/2504.17249 and https://arxiv.org/html/2504.17249v1
- [B2] Project site: https://lite.berkeley-humanoid.org/
- [B3] Docs (GitBook .md pages): https://berkeley-humanoid-lite.gitbook.io/docs/releases.md, …/getting-started-with-hardware/building-the-actuator.md, …/flashing-the-motor-controllers.md, …/in-depth-contents/motor-characterization.md, …/in-depth-contents/can-communication.md, …/getting-started-with-hardware/materials-and-parts-bom.md
- [B4] Repo: https://github.com/HybridRobotics/Berkeley-Humanoid-Lite (README, motor_configuration.json)
- [B5] Low-level repo: https://github.com/HybridRobotics/Berkeley-Humanoid-Lite-Lowlevel (robot_configuration.backup.json)
- [B6] Assets repo: https://github.com/HybridRobotics/Berkeley-Humanoid-Lite-Assets (berkeley_humanoid_lite_assets/robots/berkeley_humanoid_lite.py)
- [B7] Firmware: https://github.com/T-K-233/recoil-motor-controller-besc (motor_profiles.h, main.c, current_controller.c)
- [B8] Official MakerWorld upload: https://makerworld.com/en/models/1220823-6512-cycloidal-gear-actuator
- [B9] Author's notes: https://tk233.gitbook.io/notes/mechanical/mad-cycloidal-actuator.md

**Robot**
- (V) 16 kg, 0.8 m. ev: "The robot weighs 16 kg and stands 0.8 m tall" [B1]
- (V) 22 actuators: 10× 6512 and 12× 5010 [B1 Table III].
- (V) Total BOM US$4,312 (US) / US$3,236 (China) [B1 Table III].
- (V) 6S 4000 mAh battery, about 30 min [B1].
- (V) Four CAN buses at 250 Hz, one per limb. ev: "1 Mbps CAN 2.0 bus" [B1]

**Motor (6512)**
- (V) ev: "M6C12 150KV BLDC drone motor from MAD Components" [B1]
- (V) MAD store price today is US$129 for M6C12 EEE 150 KV (store.mad-motor.com products.json), matching Table I.
- (V) 72 mm OD, per COMPAct [C1].
- (V) Phase R 0.1886 Ω, L 0.0325 mH, delta winding, Kt 0.0919 N·m/A [B3 motor-characterization].
- (V) The firmware's active profile uses Kt 0.08958 [B7 motor_profiles.h].

**Motor (5010)**
- (V) Firmware profile MAD_5010_110KV, Kt 0.1176, R 0.6193 Ω [B7], [B3].
- (U) Supply risk, GitHub issue #1: ev: "MAD Components 5010 110KV' is now out of stock". Consistent with this (V), the MAD store today lists the 5010 EEE V2.0 only in 200/240/310/370 KV at US$84. The firmware also contains a 5010 200KV profile (Kt 0.06588) [B7].

**Reducer**
- (V) ev: "This is a 15:1 cycloidal gear actuator" [B8, official upload]
- (V) Ratio 15 in the robot config for all 22 joints. ev: "gear_ratio": -15.0 [B4], [B5]
- (V) Dual disks [B1: "the cycloidal disks"].
- (V, 2023 author notes, may predate the final design) M6C12 profile has housing radius 36 mm, 4 mm roller radius, N = 16 rollers, eccentricity 2 mm. The 5010 profile has 29 mm, 2.5 mm, N = 16, 1.25 mm [B9]. 16 rollers gives 15:1.

**Material and construction**
- (V) PLA. ev: "Polylactic Acid (PLA) is selected as the filament material" [B1]
- (V) ev: "housing, cycloidal gear, input shaft, and output shaft are all 3D printed" [B1]
- (V) Brass hex stand embedded in the input shaft; through-screws. ev: "prevent failures along layer boundaries" [B1]
- (V) 6811ZZ main bearing defines the actuator size [B1].
- (V) Every part fits a 200 mm cube build volume [B1].
- (V) Print profiles: housing plate 136 g PLA (0.2 mm layers, 4 walls, 15% infill); shaft/disk plate 28 g PLA (5 walls, 80% infill) [B8 profile data].

**Torque and speed**
- (V) The paper gives no peak or continuous torque figure.
- (V) Stiffness test ramped 0 → 20 N·m → 0 in both directions [B1].
- (V) Robot and sim limits: legs torque_limit 6.0 N·m and i_limit 20 A [B5]; sim effort_limit 6 (legs) and 4 (arms), velocity_limit 10.0 [B6].
- (V) ev: "utilized only 30% of the actuator's torque limit" (RL walking) [B1]
- (E) See §1b for the current-limited ceiling.

**Measured performance (V, [B1])**
- Gearbox mechanical efficiency about 90% over most of the operating range.
- Stiffness 319.49 N·m/rad (linear fit over 4–10 N·m).
- Backlash on six fresh actuators: maximum 0.0229 rad (1.31°), SD 0.0042 rad.
- Torque error within ±0.5 N·m across six units printed on two printers.
- 5-DOF arm repeatability: SD 3.433 mm over 100 repetitions.

**Durability (V, [B1])**
- 60-hour test lifting a 0.5 kg, 0.5 m pendulum from −45° to +90° at 0.5 Hz.
- Efficiency and backlash were checked hourly for the first 12 h, then every 12 h.
- Efficiency first declined, then recovered. ev: "backlash increased slightly as the 3D-printed parts experienced wear"
- The backlash-growth figure is in Fig. 10 as an image only (GAP).
- (E) The load was only about 2.45 N·m, roughly 108,000 cycles.

**Limitation stated by the authors (V)**
- ev: "insufficient study of thermal effects on the 3D-printed structure" [B1]

**"Recoil" controller: what it actually is**
- (V) In BHL, "Recoil" is **firmware** (`Recoil-Motor-Controller-BESC`, MIT license) running on ST's **B-G431B-ESC1** discovery board [B3 releases page], [B7]. It is not a separate BHL board.
- (V) The MCU is an STM32G431CB. The firmware's startup file is `startup_stm32g431cbux` (uncertainty-cc/Recoil-Motor-Controller tree).
- (V) Board price in the BHL BOM: US$19 (US) / US$23 (China) [B1 Tables I–II].
- (V) The firmware's default current limit is 20 A. ev: "controller->i_limit = 20.f;" [B7]
- (V) CAN runs in **classic CAN 2.0 at 1 Mbps, not CAN-FD**, even though the STM32G4 has an FDCAN peripheral. ev: "FrameFormat = FDCAN_FRAME_CLASSIC" [B7 main.c]; "BitRateSwitch = FDCAN_BRS_OFF" [B7 can.c]
- (V) The protocol mimics CANopen (NMT/SDO/PDO frames) [B3 can-communication].
- (U) The board is rated about 40 A peak and 6S. That comes from search summaries of ST/Mouser/Digikey; st.com timed out and Mouser/Digikey returned bot-blocks. A third-party hackaday.io page repeats "6S Lipo (40A peak)" and notes the ESC "becomes hot very fast" (U).
- (V) Build note: ev: "CAN port solder pads on the ECS are very fragile" [B3]
- (V) The AS5600 encoder needs a resistor modification [B3].
- (V) The paper cross-validated its firmware against an off-the-shelf moteus controller [B1].
- (V) USB-CAN adapters cost US$68 for 4 in the BOM [B1 Table III] (E: about US$17 each).

**License (V)**
- ev: "code in this repository is licensed under MIT License" [B4]. Other assets are CC BY-SA 4.0 [B4].
- The MakerWorld 6512 files are CC BY [B8].

**Derivative design (V, author README, low maturity)**
- github.com/LittleMooMooDingDingCow/3D-Printed-Cycloidal-Robotic-Actuator (MIT): 17:1 and 25:1 cycloids using the B-G431B-ESC1 with BHL firmware.
- The author notes the 17:1's "torque-weight ratio is too low".

#### 2.2 ODRI actuator module (Solo-8 / Solo-12 / Bolt)

Sources:
- [O1] Grimminger et al., RA-L 5(2) 2020, arXiv 1910.00093v2: https://arxiv.org/html/1910.00093v2
- [O2] https://github.com/open-dynamic-robot-initiative/open_robot_actuator_hardware (actuator_module_v1/README.md, actuator_module_v1.1.md, details_3d_printed_parts.md, micro_driver_electronics/README.md, quadruped_robot_12dof_v1/README.md)
- [O3] https://github.com/open-dynamic-robot-initiative/master-board

**Motor and reducer**
- (V) ev: "T-Motor Antigravity 4004, 300KV), a 9:1 dual-stage timing belt" [O1]
- (V) ev: "3:1 gear reduction on each stage" [O2]
- (V) Motor: 53 g, 12 pole pairs, 45 mm rotor diameter [O2].
- (V) Belts: AT3 GEN III; 50T/4 mm first stage, 67T/6 mm second stage [O2].

**Torque, mass and encoder**
- (V) ev: "tau_max = 2.7 N m joint torque at 12 A" [O1]
- (V) The repo says ev: "weighs 150g and outputs 2,5Nm at 12A" [O2]. The paper and repo disagree (2.7 vs 2.5 N·m); both are V.
- (V) ev: "k_i = 0.025 N m/A" [O1]
- (V) ev: "The module weighs 150 g for a segment length of 160 mm" [O1]
- (V) Core components weigh 95 g [O2].
- (V) Encoder: optical, 5000 CPR code wheel, 20,000 counts/rev at the MCU [O1], [O2].

**Printed versus metal parts**
- (V) T30 pulleys: "use SLA, Polyjet or Multijet printer" [O2].
- (V) Motor shaft plus T10 motor and center pulleys ev: "need to be machined from metal" [O2].
- (V) Shells: SLS Duraform HST (3D Systems) or FDM PC-ABS (Fortus). Print orientation is critical; bearing seats are the critical tolerance [O2 details_3d_printed_parts].
- (V) An optional "ODRI Encoder Kit" from PWB supplies the machined parts pre-assembled [O2 v1.1].

**Electronics**
- (V) MPI Micro-Driver: TMS320F28069M plus two DRV8305, dual motor, 10 kHz torque control. Voltage is ev: "up to 40 V" per the paper [O1], but "5V - 32V (we operate our robots at 24V)" per the repo [O2]. 13 g, 51 × 50 mm [O2].
- (V) ev: "component price was around 50€ per board" (2-motor board, components only) [O2]
- (V) Master board: ESP32; SPI to up to 8 µDrivers; Ethernet round trip 0.2 ms; WiFi ESP-NOW round trip 1.2 ms; BSD-2 [O3].

**Robot, cost and license**
- (V) Solo-8: 2.2 kg [O1]. Solo-12: 2.5 kg [O2].
- (V) Solo-12 is sold commercially by PAL Robotics, assembled or as a kit (price not on page) [O2].
- (V) Per-actuator cost is **not published** (GAP).
- (V) License BSD-3 [O2].

#### 2.3 Stanford Doggo (and Pupper)

Sources:
- [D1] Kau et al., ICRA 2019, arXiv 1905.04254v1 (PDF read via WebFetch)
- [D2] https://github.com/Nate711/StanfordDoggoProject (README, MIT license)
- [D3] Official BOM sheet linked from README, CSV export: docs.google.com/spreadsheets/d/1MQRoZCfsMdJhHQ-ht6YvhzNvye6xDXO8vhWQql2HtlI
- [D4] Pupper v3 docs: https://pupper-v3-documentation.readthedocs.io/en/latest/learn_more/tech_specs.html

**Motor and reducer**
- (V) ev: "T-Motor MN5212, 3:1" [D1 Table I]
- (V) The BOM row reads "T-motor 5212 KV340" at US$82.92 [D3].
- (V) GT2 belt, 3 mm pitch, 6 mm wide; 16T → 48T pulleys [D2].
- (V) ev: "The pulleys are easily fabricated on a 3D printer" [D1]
- (V) The README says pulleys were printed by Xometry SLS and must be printed "up" [D2].

**Performance (V, [D1] Table I)**
- Cost US$120; mass 0.27 kg; continuous 1.51 N·m; peak 4.8 N·m; 840 W maximum continuous power.
- Continuous torque is defined at 125 °C winding temperature, 22 °C ambient, no cooling [D1].
- ev: "torque density of 17.8 Nm/kg" [D1]

**Electronics**
- (V) ODrive: README ev: "four v3.5, 48V ODrives" [D2]; the BOM says "ODrive 24V, no connectors", US$119 ×4 [D3].
- (V) Teensy 3.5; UART at 500,000 baud [D2].
- (V) AS5047 encoders at 2000 CPR, incremental [D1], [D2].

**Robot**
- (V) 4.8 kg [D1 Table II].
- (V) Cost ev: "costs less than $3000" [D1]; BOM total US$2,971.02 [D3].
- (V) README carries an end-of-life notice (superseded by Pupper v3) [D2].
- (V) Coaxial belt drive ev: "It has also been the most troublesome." Details are in §3.

**Pupper v3 (reference)**
- (V) ev: "4005 brushless motor", "10:1 planetary gearbox", "~ 3.5 Nm peak torque"
- (V) ~1.0 N·m continuous with air cooling; ~30 rad/s [D4].
- (V) Build cost "about $2000" (docs home); README says "Roughly $1000 BOM" [D2]. The two sources differ.

#### 2.4 mjbots: qdd100 and moteus-based planetary builds

Source: [M1] official store product JSON, https://mjbots.com/products.json (fields taken from each product's body_html).

**qdd100 beta 3**
- (V) US$879. ev: "NOT CURRENTLY STOCKED, MINIMUM ORDER QTY 50"
- (V) ev: "Peak: 16 Nm (< 1s) 10 Nm - 60s 6 Nm - 400s 3.3 Nm - Indefinite"
- (V) Backlash ±0.25°; weight 507 g; 100 mm OD × 44 mm thick; 10–44 V; 500 W peak; 5 Mbps CAN-FD.
- (V) Peak speed 3,600 °/s at 36 V (E: 62.8 rad/s).
- (V) Ratio: the store's "M0.5 6x Reduction Planetary Gearset" (US$30) is described as ev: "gearset for a 6x planetary gearbox, like used in the qdd100". It has a 100T ring, 20T sun and 3× 40T planets with HK0608 needle bearings, in 42CrMo / C40Cr steel at HRC 25. It fits inside 8108-and-larger stators and requires lubrication.
- It is metal, not printed. It is included as the reference for a moteus-plus-planetary QDD.

**Controllers (V, store)**

| Controller | Price | Supply | Peak phase current | Continuous (without / with thermal management) | Mass |
|---|---|---|---|---|---|
| moteus-c1 | US$69 | 10–51 V | 20 A | 5 / 14 A | 8.9 g |
| moteus-n1 | US$149 | 10–54 V | 100 A | 9 / 26 A | 14.6 g |
| moteus r4.11 | US$94 | 10–44 V | 100 A | 12 / 32 A | 14.2 g |
| moteus-x1 | US$175 | 10–54 V | 120 A | 25 / 62 A | 23.7 g |

- All four use 5 Mbps CAN-FD, and the firmware is Apache 2.0.
- Motor mj5208: US$74, 1.7 N·m peak, 193 g, 330 KV.
- mjcanfd-usb-1x adapter: US$39.

**moteus-based printed planetary examples**
- Urs et al. (§2.5) used moteus with printed planetary and Wolfrom reducers.
- COMPAct (§2.9) used moteus or ODrive Pro with printed planetaries.
- JeongSeoJin/Quasi-Direct-Drive-Actuator (§2.12) used moteus-c1 with a cycloid.

#### 2.5 Urs, Enninful Adu, Rouse, Moore: 3D-printed QDD actuators (U-Michigan EMBiR)

Sources:
- [U1] arXiv 2202.12395 (v1, 24 Feb 2022; paper license CC BY 4.0): https://arxiv.org/html/2202.12395. Venue per the BHL paper's reference list: IROS 2022, pp. 1957–1964 (V).
- [U2] https://github.com/EMBiRLab/3DP-Actuator (README; "*_hitemp.stl" in Hi-Temp resin)
- [U3] BOM sheet linked in the README (CSV export): docs.google.com/spreadsheets/d/1bmRzfv3GVEB19bbNFnGRmMcz0FWW6z87bu-cz9VUHL8

**Motor, reducers and cost**
- (V) T-Motor RI50 (inner rotor, so not a hobby outrunner): US$62, Kt 0.105 N·m/A, KM 0.118, 193 g, R 705 mΩ, L 2559 µH [U1].
- (V) Reducers: ev: "planetary 7.5:1, and bilateral drive 15.04:1". The 15:1 is a Wolfrom compound planetary [U1].
- (V) Gears use a 30° pressure-angle involute [U1].
- (V) ev: "less than $200 USD each" [U1]. BOM totals are US$193.78 (7.5:1) and US$197.46 (15:1) [U3].
- (V) BOM lines: RI50 $62; "mjbots moteus r4.8 Motor Driver" $84; 2 fans $10; Hi-Temp resin 72 g/$14.40 or 80 g/$16.00; PLA 112 g/$2.80 or 140 g/$3.50.
- (V) Bearings: 6702ZZ, 6810ZZ, 605ZZ×6, 688ZZ, 6804ZZ for the 7.5:1; 6704ZZ×2 and 105ZZ×6 in the 15:1 [U3].

**Materials**
- (V) ev: "temperatures near the motor can exceed the glass transition temperature of PLA"
- (V) So the motor housing and rotor-sun gear are SLA High-Temp resin (Formlabs Form 3), and the transmission is FDM PLA (Hatchbox, Prusa MK3S+) [U1].
- (V) ev: "A full actuator can be printed in 14 hours" [U1]

**Table 2 performance (V, [U1])**

| Ratio | Peak (20 s) | Peak (2 s) | Continuous | Mass | Size | Max speed |
|---|---|---|---|---|---|---|
| 7.5:1 | 7.5 N·m | 19.1 N·m | 4.4 N·m | 482 g | 90 × 70 mm | 21 rad/s |
| 15:1 | 15 N·m | 38.2 N·m | 8.8 N·m | 536 g | 90 × 90 mm | 11 rad/s |

- (V) Caveat: ev: "Peak torques are thermally driven; maximum tested torques are lower" [U1]
- (V) Thermal: two 30 × 10 mm fans give a "3.5×" cooling advantage. The winding limit is 100 °C. The 7.5:1 can sustain 9.2 A for 20 s or 22 A for 2 s [U1].
- (V) Current-loop bandwidth 102 Hz [U1].

**Lifecycle (V, [U1])**
- ev: "57 hours with no failures" (two 7.5:1 actuators, about 420,000 Mini-Cheetah strides of gait playback).
- Efficiency dropped 3.5% over the first 8–10 h, then rebounded. The abstract says "only a 2% reduction".
- Fine plastic dust built up in the transmission.
- Backlash-plus-flex grew from 56 to 82 mrad, i.e. 26 mrad, or 13 mrad per actuator. ev: "250±30 µrad/hr per actuator"

#### 2.6 Roozing & Roozing: 3D-printed cycloidal gearing (University of Twente)

Sources:
- [R1] "3D-printable low-reduction cycloidal gearing for robotics", IROS 2022 (UT repository PDF, read via WebFetch): https://ris.utwente.nl/ws/portalfiles/portal/295490006/3D_printable_low_reduction_cycloidal_gearing_for_robotics.pdf
- [R2] "Experimental comparison of pinwheel and non-pinwheel designs of 3D-printed cycloidal gearing for robotics", ICRA 2024. Read via a third-party mirror, https://energiazero.org/cartelle/meccanica/riduttori/2023_cycloidal_drive_nonpinwheel.pdf, because ResearchGate returned 403 and IEEE is paywalled. The text is the authors' paper, but the host is not primary.
- [R3] https://github.com/geez0x1/2022-cycloidal-drive (MIT) and [R4] https://github.com/geez0x1/2023-cycloidal-drive-nonpinwheel (MIT). ev: "Everything is under the MIT license"

**2022 PLA design (V, [R1])**
- ev: "An open-source design of a 11:1 cycloidal gearbox"
- Geometry: R 41.5 mm; 12 rollers; 6 output pins; roller and pin bearings of 4.5 mm radius; eccentricity 2.025 mm.
- Performance: ev: "36.4 Nm Nominal torque (at 40 A, thermally limited)"; 52.8 rad/s peak at 48 V.
- Mass and size: gearbox 372 g; 809 g total including motor and cooling; 23 mm thick; 104 mm diameter.
- BOM (€98 total): roller/pin bearings (36×) €15; eccentric bearings €5; input bearing €1; output bearing €27; shoulder screws (18×) €37; misc steel €7; PLA €6.
- Other parts: ev: "T-Motor Antigravity 8012 €123"; "ODrive Robotics v3.6 (56 V version) €179"; AS5048A ×2 €32.
- Measured:
  - Stiffness 633 N·m/rad (pendulum to 28.5 N·m).
  - Worst-case play ~0.35° (other prototypes 0° and 0.7°).
  - Coulomb friction ~0.4 N·m.
  - Gear-ratio variation ~9%; transmission error 0.92° RMS, 1.8° max.
- ev: "tested with up to 44 Nm static loads" and impacts above 6600 rad/s², "without failure".

**2024 PA6-CF designs (V, [R2])**
- Why they left PLA: ev: "relatively low strength, wear resistance, and temperature resistance"
- Material: ev: "PA6-CF (Fibertree F3 PA-CF Pro, 15% carbon fibre)". An SLS prototype showed no benefit over FDM on a Prusa MK3S+.
- Cost: ev: "€98 and €65 (-33%) for the pinwheel and non-pinwheel"
- Ratio 11; 36.4 N·m nominal (40 A); 28 rad/s peak; gearbox 377 g (pinwheel) / 360 g (non-pinwheel).
- Encoders: CUI AMT23 plus AS5048A.
- Stiffness 1271 (pinwheel) / 1468 (non-pinwheel) N·m/rad, more than double 2022's.
- Play typically 0.20–0.25°, maximum 0.35 / 0.30°.
- Coulomb friction 0.62 / 0.53 N·m.
- Transmission error 0.38 / 0.56° RMS; ratio variation ~5%.
- Run-in: 90 min at 8 rad/s; most of the change happened in the first 30 min.
- Endurance: 10 h, 1390 cycles each, at more than 15 N·m and 3 rad/s. Afterwards play increased about 2× (details in §3).

#### 2.7 OpenTorque (Gabrael Levine) and the Blackbird biped

Sources:
- [T1] Author's project page: https://hackaday.io/project/159404-opentorque-actuator
- [T2] https://github.com/G-Levine/OpenTorque-Actuator (LICENSE is CC BY-SA 4.0)
- [T3] Blackbird: https://hackaday.io/project/160882-blackbird-bipedal-robot

**Actuator**
- (V, as the author's claims) ev: "Peak torque (theoretical): 80 Nm"; "Weight: 1150 g"; "Gear ratio: 8:1"; "Cost: ~$150"; "Passively cooled" [T1]
- (V) Motor "Herlea X8318S KV100 (Multistar 9235)"; encoder AS5048A-TS_EK_AB [T1].
- (V) ev: "Nylon is the recommended material for the sun and planet gears." The author used Taulman Alloy 910 [T1].
- (V) v2 replaced two thin-section bearings with a single cross-roller bearing and raised the ratio to 8:1 [T1 log 2018-11-17].
- (V) Thermal: ev: "Three minutes of sustained 60A current caused a temperature rise of less than 20 degrees" [T1]
- (V) ev: "The FETs on the ODrive board heat up quickly" [T1]
- (U) Reader comments on [T1]: one reader estimates about 40 N·m peak from the motor's rating; another says the RA8008 cross-roller bearing "currently being sold for $150", which suggests the ~US$150 cost excludes it.

**Blackbird biped (V, project page claims)**
- ev: "Blackbird stands 1.2 meters tall and weighs roughly 15 kg" — the same height as JX1.
- ev: "total BoM cost is less than $3000"
- 10 OpenTorque actuators, 5 ODrive 3.x boards, MCP2515 SPI-CAN, 13× 1 kg PLA rolls.
- Standing draw: ev: "only 15A per actuator"; 37 W per leg.
- ~30 Hz control bandwidth claimed.
- Caveat: many project logs show controller development in simulation or with legs in the air. I did not verify sustained free walking (U).

#### 2.8 Aaed Musa (author's own site aaedmusa.com, plus GitHub)

**OpenQDD V1 (06/21/2023)** — https://www.aaedmusa.com/projects/openqdd; https://github.com/aaedmusa/OpenQDD-V1
- (V) ev: "9:1 Planetary Gear Set with Helical Gears"; "Peak Holding Torque: 16.36 Nm"; "Total Mass: 935g"; "Total Cost: $247"
- (V) ODrive S1 with on-board encoder; Eagle Power 90 KV motor; air vents for passive cooling.
- No LICENSE file at the repo root (checked via raw.githubusercontent.com).

**Internal Cycloidal Actuator (02/14/2024)** — https://www.aaedmusa.com/projects/internalcycloidalactuator
- (V) ev: "Total Mass: 1023g"; "Total Cost: $384"; "Speed: 209RPM @ 22.2V"; "Torque: 16.17Nm"
- (V) Custom 10010 stator, 36 slots / 42 poles, 6 × 26 AWG strands, 6 turns per slot.
- (V) Mild-steel 1045 rotor (machined by PCBWay) with 42 N52 magnets.
- (V) 8:1 cycloid; roller-pin ring machined from Al 6061; ODrive S1.
- (V) Issue: ev: "3D-printed parts slightly warping due to the heat from the coils"

**Capstan Drive (05/31/2024)** — https://www.aaedmusa.com/projects/capstandrive; https://github.com/aaedmusa/Capstan-Drive
- (V) Test stand printed in PLA; 852 g; 120° rotation; ev: "8.55:1 reduction (quasi-direct drive)"; ODrive S1; Eagle Power 90 KV.
- (V) Steel-wire rope failure: ev: "After 4 short hours later, the wire broke"; ev: "None of the trials lasted more than 5 hours". The author attributes it to the D/d ratio.

**CARA 1.0 quadruped (07/11/2025)** — https://www.aaedmusa.com/projects/cara
- (V) ev: "8:1 capstan drive using 2 mm Dyneema DM20 Rope"
- (V) Eaglepower 90 KV; ODrive S1 over CAN to a Teensy 4.1; 24 V 3 Ah battery.
- (V) Small drums in PET-CF, structure in PC; drums and feet at 100% infill, other parts 25% gyroid.
- (V) ev: "CARA weighs 31.41 lbs (14.25 kg)"; "total cost for CARA is approximately $3,300"
- (V) ev: "Some parts did break on multiple legs during testing"; TPU feet "wore down quickly" on concrete.

**CARA 2.0 (05/01/2026)** — https://www.aaedmusa.com/projects/cara2
- (V) ev: "each actuator on CARA 1.0 costs approximately $250"
- (V) Eagle Power 8308: US$80, 340 g, 90 KV, 36N40P, stall 1.67 N·m. ODrive S1: US$150, 55 g.
- (V) TYI 5008: US$18, 160 g, 335 KV, stall 0.421 N·m. Rewound (40 turns per slot) to 90 KV, giving stall 1.274 N·m.
- (V) MKS XDrive Mini: US$41. It worked over UART but not CAN; it needed a community firmware (github.com/shazib2t/MKS_ODrive_MINI_custom_firmware).
- (V) Capstan joint: ev: "weighs 470 g (1 lb), features a 9.6:1 reduction, produces 12 Nm"
- (V) Robot: ev: "Cost: $1,450"; 8.26 kg; 6.8 kg payload; 0.55 m/s.

#### 2.9 COMPAct (IISc Bengaluru / IIT Roorkee; ARTPARK-funded): printed planetaries

Sources:
- [C1] arXiv 2510.07197v2 (CC BY 4.0), https://arxiv.org/html/2510.07197v2
- [C2] https://github.com/singhaman1750/COMPAct (MIT, © 2026 Aman Singh)

**Hardware (V)**
- Two printed actuators, SSPG 7.2:1 with a T-Motor MN8014 (87.8 mm OD) and CPG 14:1 with a MAD M6C12 (72 mm OD). ev: "100% infill density on a Bambu Lab X1C printer"
- PLA (the paper contrasts "carbon-fiber–reinforced polyamide versus PLA in our prototypes").
- Sun shaft reinforced with a central bolt; through-bolts act as a structural skeleton.
- Drivers: ODrive Pro and moteus.

**Results (V)**

| Actuator | Mechanical efficiency | No-load backlash | Stiffness |
|---|---|---|---|
| SSPG 7.2:1 | 60–80% | 0.010 rad (0.59°) | 242.7 N·m/rad |
| CPG 14:1 | ~60% | 0.046 rad (2.6°) | 201.6 N·m/rad |

- The optimizer had predicted 96% (SSPG) and 93.8% (CPG) efficiency. The shortfall is attributed to printed tooth-profile deviations.
- Tested to 18 N·m (efficiency) and ±20 N·m (stiffness).
- Endurance and peak-torque tests are listed as future work (GAP).
- Design-space result: CPG is the lowest-cost option between 7.2:1 and 15:1 for the M6C12; single-stage planetary tops out at 7.2:1.
- Relevance: an Indian lab (IISc) built the same M6C12 class as BHL with PLA.

#### 2.10 James Bruton (XRobots): 3D-printed cycloidal drives and openDog V3

Sources:
- [J1] https://github.com/XRobots/openDogV3 (README, LICENSE MIT © 2021, Code/openDogV3/kinematics.ino, ODriveInit.ino)
- [J2] https://github.com/XRobots/CycloidalDrive (MIT)
- [J3] Author's YouTube descriptions: pWMB5VbLb6w (2021-03-15), tgEOpl880KM (2021-03-29), IVpYtyS5Q-k (2021-07-26), ts2l_Em7fpI (2021-10-25), eKZIJwJBjEs (2021-12-13), dYgCxZjdNUU (2022-03-28)

**Construction (V)**
- ev: "The parts are all printed in PLA" [J1]
- Cycloid internals: 4 perimeters, 30–40% infill; larger parts 15% infill, 3 perimeters, 0.3 mm layers [J1].
- Twelve cycloidal drives, each with ev: "two cycloidal discs and a lot of bearings" [J3 dYgCxZjdNUU]
- Six ODrives drive 12 axes, commanded over UART (Serial1–6) from a Teensy 4.1; current_lim 20 A [J1], [J3].
- AS5047 encoders in absolute mode [J1].

**Development history (V, video descriptions [J3])**
- V1: ev: "the cam snapped off under load and it vibrated a lot"
- V2 fix: two discs 180° out of phase, and an M4 bolt through the cam.
- V3: "nylon bushings" to cut weight and cost.
- Later: ev: "Cycloidal Drives have held out fairly well so far"

**Ratio (E):** ≈10:1 from the code conversion factor (see §1b). The motor model and torque are GAP; they appear only in the videos and in BOM.ods, which I did not download (binary file).

**Secondary reports (U)**
- 3D Printing Industry quotes the author: ev: "push me on a skateboard for a few miles with no visible wear". The same article gives robot mass as about 20 kg, expected to reach 25 kg.
- Hackaday: "around $2000 all in".

#### 2.11 Paul Gould: "3D Printed Robot Actuator"

Source: [G1] author's project page and comments, https://hackaday.io/project/157812-3d-printed-robot-actuator (created 05/03/2018; HaD Prize 2018 semifinalist).

**Design (V)**
- Cycloidal gearbox with rolling elements, bearings, and dual input and output shafts.
- Motors: Multistar Elite, later Gartt ML5010 300 KV.
- Dual absolute magnetic encoders (AS5147).
- Custom PCB: PSoC4 CY8C4247 plus DRV8305 plus SIR638ADP MOSFETs plus an MCP2557FD CAN transceiver; CAN and UART commands.
- Three gearbox sizes: 44, 60 and 78 mm diameter.

**Author comments (V as claims)**
- ev: "the cycloidal gearbox is 25:1 reduction. The cost is about $150"
- ev: "The aim is 20Nm (200kg-cm)"
- ev: "only really be testing at about 10Nm max"
- ev: "It is 3D printed ABS, don't expect too much."
- Backlash across 6 units: ev: "Most have about 0.3mm @ 200mm". One unit had 0 mm and one had 1 mm (E: 1.5–5 mrad).
- A later log mentions a "41:1 Dual Disk, Single stage 27mm x 102dia QM4208 motor" variant.

**Gaps:** mass and license are not stated.

#### 2.12 Other small or hobby designs (V from author READMEs; low maturity)

- **JeongSeoJin/Quasi-Direct-Drive-Actuator (2025–26).**
  - Custom 8110 stator (36N42P, hand-wound); 10:1 dual-disc cycloid, with the prototype's gears, shafts and rotor in CNC aluminium; moteus-c1.
  - ev: "Maximum Torque: 8.8Nm, Maximum Velocity: 22rad/s" at 24 V.
  - Self-reported weaknesses: no rotor back-iron, low copper fill.
  - Argues that 3D-printed planetaries are "prone to catastrophic failure" under shock, which is why it uses a cycloid.
- **QLAUN (arXiv 2609.03623; LAU, Lebanon).**
  - ev: "mjbots MJ5208, 330KV, 600W), a 3D-printed 8:1 planetary gearbox"
  - ODrive Pro; 20 V; ≤30 A.
  - ev: "torques of up to 5N.m while limited to 40%"
  - Belts give 4:1, for 32:1 at the joint. PLA. The robot is about 15 kg. Aimed at low-budget MENA labs.
- **Skyentific.**
  - Stepper-driven compound planetaries: ev: "only 32$ ... reduction ratio (1:84)"; "overall reduction ratio around 100"; Callisto 1:112 with 3D-printed cross-roller bearings.
  - His current store sells commercial actuators instead: AK10-9 + moteus at US$1,512; harmonic actuators at US$1,296–2,052. His biped SN2 uses "MyActuator quasi direct drive actuators".
  - Stepper, high-ratio designs are **not backdrivable QDDs**, so they are a poor match for dynamic legs (E judgement).
- **Open Source Leg (UMich; opensourceleg.org/hardware, V).** This is a machined and commercial-actuator design, **not low-cost**.
  - "approximately $10,500 to $23,000"; 41.5:1 total (9:1 planetary in the Dephy actuator plus a 4.61:1 belt).
  - ~145.25 N·m instantaneous at 25 A; ~29 N·m continuous at 5 A.
  - Peak speed **6.13 rad/s**, below JX1's 8–20 rad/s.
  - v2 moved from a 3-stage to a single-stage belt.
- **SimpleFOC ecosystem (docs.simplefoc.com/boards, V).**
  - Official boards are low-current:
    - Mini v1.1: "Max current: 2.5A per phase", 8–35 V, €7–15.
    - Shield v3.2: gimbal motors, "Max current: 3A", 35 V, €15–30.
    - Drive v1.0: "20A continuous (peak 30A - measured)", ≤30 V, €25–40, "will be available".
    - Power Shield: "development abandoned"; its BTN8982 half-bridges have slow switching.
  - I found no SimpleFOC-driven legged actuator with published torque or life numbers. The search budget was exhausted, so I used only GitHub repo search.
  - Hobby examples (U-level maturity):
    - RedFeatherXO/Cycloidal_gearbox (MIT): ev: "I got 1 Nm of torque but only with a standard ESC, my simpleFOC Mini didnt work"
    - JorgeMaker/NautilusController (MIT): SimpleFOC-based STM32F405 + DRV8305 board, CAN "not implemented yet".
    - mohammad-askari/stm32-esc: SimpleFOC on the B-G431B-ESC1.
- **Split-ring compound planetary.** I found no legged actuator with published numbers. Only design tools turned up (github.com/Ocanath/srcp-optimization; github.com/Juan-Gg/Differential-planetary-gearbox-calculator) and an arm gearbox (RR1, github.com/surynek/RR1; herringbone printed planetary shown in an assembly video) (GAP).

---

### 3. Failure modes of 3D-printed reducers (reported), with quantitative data where available

| # | Failure mode | Where observed | Quantitative data | Label | Source |
|---|---|---|---|---|---|
| F1 | **Backlash growth from wear** (PLA cycloid) | BHL 6512 | 60 h, 0.5 Hz (E: ~108k cycles), load only ~2.45 N·m (E, ~10% of capability). Backlash "increased slightly", within limits. Fresh units up to 0.0229 rad (1.31°). The growth curve is in Fig. 10 only. | V + E | arxiv.org/html/2504.17249v1 §IV-C, IV-E |
| F2 | **Backlash growth from wear** (PLA planetary, SLA sun) | Urs 7.5:1 | 57 h (~420k strides) of Mini-Cheetah gait playback, 2 actuators, **no failures**. Backlash +26 mrad total (13 mrad each ≈ 0.74°). **250 ± 30 µrad/h per actuator**, roughly linear. | V | arxiv.org/html/2202.12395 §4.5 |
| F3 | **Play doubles after short endurance run** (edge wear from "elephant's foot" print defect) | Roozing 2024 PA6-CF cycloids, both variants | 10 h, 1390 cycles, >15 N·m, >3 rad/s. Play about **2×** afterwards; microscope showed uneven wear on disk outer surfaces and housing cycloid. The authors blame print calibration plus insufficient run-in. | V | ICRA 2024 paper [R2] §IV-E, V |
| F4 | **Efficiency drop from debris / run-in, then recovery** | Urs; BHL | Urs: −3.5% over the first 8–10 h, then rebound, with "fine plastic dust" in the transmission (the abstract says 2%). BHL: efficiency first declined, then returned near its original level. Roozing: most run-in change within 30 min at 8 rad/s. | V | [U1] §4.5; [B1] §IV-C; [R2] §IV-A |
| F5 | **Heat softening / warping near the motor** (PLA and other printed parts) | Urs; Aaed Musa internal cycloid; BHL | Urs: temperatures near the motor can exceed PLA's glass transition, so hot-zone parts were moved to SLA High-Temp resin; winding limit 100 °C. Aaed Musa: printed parts "slightly warping" from coil heat; he recommends an all-metal gearbox. BHL: thermal effects on printed parts "insufficient[ly]" studied. Prusament PLA "temperature resistance" is 55 °C and it "lose[s] mechanical strength at temperatures over 60 °C". | V | [U1] §2.2; aaedmusa.com/projects/internalcycloidalactuator; [B1] §VI; prusament.com/materials/pla/ |
| F6 | **Thermal tooth bending of printed nylon gears** under continuous running | Zhang et al. 2020 (gear test rig; module 2, 30 teeth, 15 mm face, 60% infill, 1000 rpm) | Cycles to failure or run-out: **Nylon 618** 2.4 M at 5 and 7 N·m; 1.5 M at 10 N·m; 0.012 M at 15 N·m. **Onyx** 2.4 M at 5; 0.96 M at 7; 0.006 M at 10 N·m ("failed instantly after any load beyond 10 Nm"). **Alloy 910** 0.0078 M at 5 N·m; Nylon 645 0.014 M; Markforged nylon 0.018 M. Injection-moulded Nylon 66 (literature): 2.4 M at 5 and 7; 1 M at 10; 0.08 M at 15 N·m. Most failures were thermal bending after ~40% tooth-thickness wear; Nylon 618 failed at the tooth root. The 12 N·m row is ambiguous in the extracted text and omitted. | V (author accepted manuscript) | wrap.warwick.ac.uk/126011/ (Tribology Int. 141:105953) |
| F7 | **Wrong polymer choice** | OpenTorque author; Zhang | OpenTorque author: no wear or increased backlash seen, but "use nylon and not ABS" (qualitative, no hours given). Contrast: in Zhang's rig, Alloy 910 (the filament OpenTorque recommends) failed in under 1 h at 5 N·m. Different geometry and duty cycle, so indicative only. | V (author comment) / V | hackaday.io/project/159404; [F6 source] |
| F8 | **Eccentric cam / input-shaft fracture and vibration** (single-disc cycloid) | James Bruton V1 | "cam snapped off under load and it vibrated a lot". Fix: two discs 180° out of phase, plus an M4 bolt through the cam. No hours or torque given. | V (author video description) | youtube.com/watch?v=tgEOpl880KM |
| F9 | **Layer delamination / shear in printed shafts and carriers** (design countermeasures) | Urs; BHL; COMPAct; ODRI | Urs: metal pins where loads leave the XY plane; carrier halves compression-preloaded with screws; captive metal nuts preferred; heat-set inserts warp parts near edges. BHL: through-screws and an embedded brass hex standoff "to prevent failures along layer boundaries". COMPAct: central bolt in the sun shaft and a through-bolt skeleton. No failure counts reported. | V | [U1] §2.2; [B1] §III-C2; [C1] §IV-1 |
| F10 | **Print-orientation and tolerance defects** | Doggo; ODRI; Roozing | Doggo: SLS pulleys printed at an angle had distorted teeth; they must be printed "up". ODRI: shell print orientation "critical"; bearing-seat diameters vary between suppliers and orders; if seats are too large, bearings are not held securely. Roozing 2022: ~9% ratio variation and 1.8° maximum transmission error attributed to pin/hole tolerances. | V | github.com/Nate711/StanfordDoggoProject README; ODRI details_3d_printed_parts.md; [R1] |
| F11 | **Bearing-seat creep / loosening** | — | No quantitative creep data found in any project. Only design mitigations: shoulder screws plus embedded nuts to locate bearings (Roozing); interference fits (JeongSeoJin uses 0.02 mm on aluminium parts with JB Weld); tolerance adjustment by reaming (ODRI). | GAP | — |
| F12 | **Belt skipping vs friction trade-off** (printed pulleys) | Stanford Doggo | An aluminium bracket keeps tension to prevent skipping at high torque. Center distance had to be **+0.5 mm** over nominal because of slop. Higher tension raised friction and hurt tracking and touchdown sensitivity. The coaxial belt assembly was "the most troublesome". | V | Doggo README |
| F13 | **Tension-member (rope) fatigue** | Aaed Musa capstan | Stainless wire broke after ~4 h; 3 trials, none longer than 5 h (D/d-ratio cause). Switched to 2 mm Dyneema DM20 ("essentially zero creep") and now pre-stretches the rope. | V (author) | aaedmusa.com/projects/capstandrive, /cara, /cara2 |
| F14 | **Structural printed-part breakage in legs; foot wear** | CARA 1.0 | "Some parts did break on multiple legs during testing" (redesigned). TPU 95A feet wore down quickly on concrete. No counts. | V (author) | aaedmusa.com/projects/cara |
| F15 | **Low torsional stiffness of printed transmissions** | BHL, Roozing, COMPAct | PLA cycloid: 319 N·m/rad (BHL), 633 (Roozing 2022). PA6-CF cycloid: 1271–1468 (Roozing 2024). PLA planetary: 243 (SSPG) and 202 (CPG) (COMPAct). Printed planetary backlash 0.59° (SSPG) to 2.6° (CPG). Mechanical efficiency 60–80% versus a predicted 94–96%. | V | [B1]; [R1]; [R2]; [C1] |
| F16 | **Driver and electronics failure points** seen in these builds | BHL; OpenTorque; CARA 2.0; hobby | BHL docs: ESC CAN solder pads "very fragile". OpenTorque author: "FETs on the ODrive board heat up quickly". XDrive Mini (US$41 ODrive clone): CAN unstable until custom firmware. The B-G431B-ESC1 "becomes hot very fast"; a third-party firmware caps it at about 70 °C (U, hackaday.io/project/177578). SimpleFOC Mini failed to drive a 360 KV cycloid (U, hobby repo). | V / U | BHL docs building-the-actuator.md; [T1]; aaedmusa.com/projects/cara2 |
| F17 | **Supply-chain failure** (motor discontinued) | BHL 5010 | Issue #1 (2025-04-26): the 110 KV 5010 is "out of stock" (U). MAD store today lists the 5010 EEE only at 200–370 KV (V). | U + V | github.com/HybridRobotics/berkeley-humanoid-lite/issues/1; store.mad-motor.com |
| F18 | **Impact / overload survival** (positive results) | Roozing 2022; Urs; James Bruton | Roozing: 44 N·m static and impacts at >6600 rad/s² motor acceleration without failure. Urs: 57 h without failure. James Bruton: drives "held out fairly well" (qualitative). The skateboard-towing claim ("few miles ... no visible wear", PLA) is secondhand. | V / U | [R1] §VI; [U1]; YouTube eKZIJwJBjEs; 3dprintingindustry.com (U) |

**Summary of quantitative life evidence**
- Only three published printed-reducer life tests exist: BHL 60 h, Urs 57 h and Roozing 10 h.
- All of them ran at low-to-moderate load: BHL ~2.5 N·m (E); Urs at Mini-Cheetah gait torques; Roozing above 15 N·m (≈40% of the 36.4 N·m nominal).
- **No source reports a life test above ~100 h, or at more than 50% of rated torque, for a printed humanoid or leg reducer.** This is the biggest risk gap for a 20–30 kg JX1.

---

### 4. Lessons for a low-cost India build (JX1)

1. **Torque class fit.** These are the only open designs with published numbers that reach JX1's large-joint class (40–90 N·m):
   - Roozing 11:1 printed cycloid: 36.4 N·m nominal, 44 N·m tested static, 809 g, about US$350–390 (E) including an ODrive share. PA6-CF version: €65 gearbox, 1468 N·m/rad.
   - Urs 15:1 printed Wolfrom: 38.2 N·m for 2 s, thermally predicted rather than tested; only 11 rad/s.
   - OpenTorque 8:1 nylon planetary: 80 N·m is theoretical only.
   - UCLA C-QDD (machined steel, 89.9 N·m) shows the metal route.
   - BHL 6512 (≥20 N·m applied, ~25–28 N·m ceiling (E), US$157–188) fits JX1's **medium** class. The 5010, Pupper-class and ODRI modules fit the **small** class.
   - The crude m·g·h scaling (E, §1b) suggests JX1 leg torques about 1.9–2.8× BHL's, so BHL's 6512 as-is would be marginal for JX1 hip and knee.
   - For comparison, the 30 kg Duke Humanoid uses 72–80 N·m-rated hip and knee joints and 40 N·m ankles (V).
2. **Speed.** Designs that meet 8–20 rad/s at the joint:
   - Roozing 2024: 28 rad/s at 40–48 V.
   - Urs 7.5:1: 21 rad/s.
   - Aaed Musa internal cycloid: ≈21.9 rad/s (E) at 22.2 V.
   - JeongSeoJin: 22 rad/s at 24 V.
   - Urs 15:1 (11 rad/s) is borderline, and the Open Source Leg (6.13 rad/s) is too slow.
   - Higher ratio (15–25:1) trades speed for torque. BHL's 15:1 at 24 V was configured with a 20 A current limit.
3. **Materials that survived.** PLA passed every published test so far, but only at modest loads and temperatures:
   - BHL: 60 h at ~2.5 N·m (E).
   - Urs: 57 h, with high-temp resin at the motor.
   - Roozing 2022: 44 N·m static, duration unknown.
   Guidance from these results:
   - Keep PLA out of the motor's heat path. Prusament rates PLA at 55 °C, PETG 68 °C, ASA 93 °C, PC-Blend-CF 114 °C and PA11-CF 190 °C "temperature resistance" (V, manufacturer).
   - Move to PA-CF (stiffness roughly 2× in Roozing 2024) or PC-CF for disks and housings. Calibrate against elephant's foot and do a run-in, or play can double within 10 h (F3).
   - Printed nylon gears fail by thermal tooth bending under continuous running. Filament grade matters: at 5 N·m in Zhang's rig, Nylon 618 reached the 2.4 M-cycle run-out while Alloy 910 failed at 0.0078 M cycles, a ≥300× difference (V data, E ratio; F6).
4. **Metal parts every successful design kept:**
   - Rolling-element bearings on rollers and output pins. Roozing uses 36 small bearings on steel shoulder screws. Bearings plus shoulder screws total €15 + €5 + €1 + €27 + €37 = €85 of the €98 gearbox, about 87% (E); PLA is only €6.
   - A robust output bearing: BHL 6811ZZ; Roozing's 4-point thin-section bearing at €27; OpenTorque's cross-roller.
   - Steel dowels or bolts through printed shafts and cams (Urs, COMPAct, James Bruton's M4, BHL's brass standoff).
   - Machined pulleys or rings where tooth or pin precision matters (ODRI T10 pulleys; Aaed Musa's Al 6061 roller ring).
   - India-specific availability and prices of these parts were **not researched here** (GAP).
5. **Reducer type for FDM.** Cycloids are favoured for FDM:
   - BHL ~90% efficiency and 319 N·m/rad (PLA).
   - Roozing 633 N·m/rad (PLA) and 1468 N·m/rad (PA-CF).
   - Printed planetaries measured lower efficiency (60–80%) and higher backlash (0.6–2.6°) in COMPAct, although Urs's 30°-pressure-angle PLA planetary with an SLA sun survived 57 h.
   - A capstan (Aaed Musa, 12 N·m in 470 g) gives zero backlash but only 120° range of motion and a rope-life concern (F13).
   - Belts (ODRI, Doggo) need precise or machined pulleys and tension management.
6. **Driver options by cost** (V prices unless marked):
   - B-G431B-ESC1: US$19–23 in the BHL BOM, run at 20 A with CAN 2.0 at 1 Mbps. Cheapest proven path; watch heating (U) and the fragile CAN pads.
   - moteus-c1: US$69; 20 A peak; CAN-FD.
   - moteus-n1: US$149; 100 A peak.
   - ODrive S1: US$150 per Aaed Musa.
   - ODrive v3.6 56 V: €179 for two axes, driven at 40 A in Roozing's tests.
   - Cheap ODrive clones (XDrive Mini, US$41) had CAN problems.
   - SimpleFOC official boards (2.5–3 A) are too small for leg joints; its 20 A board is not yet sold.
   - Large-joint torque (≥40 N·m at 11:1 with an 8012-class motor) needed about 40 A in Roozing's work, which is beyond BHL's 20 A ESC configuration.
7. **Test protocol worth copying:**
   - Run-in: 90 min at 8 rad/s (Roozing).
   - Efficiency and backlash checkpoints: hourly for 12 h, then every 12 h (BHL).
   - Gait-trace playback on a dynamometer: 57 h (Urs).
   - Thermal identification using the winding as a thermistor, with a limit around 100 °C (Urs).
   - JX1 should add a **long test at 50–80% of rated torque**, which no source has published.
8. **Indicative cost in India** (E, ECB rate 1 USD = 95.74 INR, excluding duty, shipping and GST):
   - BHL 6512 at the China BOM ≈ ₹15,000 per joint; 5010 ≈ ₹9,000.
   - Urs 7.5:1 ≈ ₹18,550.
   - Roozing-class large joint ≈ ₹33,800–37,400.
   - For comparison, Roboto Origin's commercial Damiao actuators are ¥949 (DM4340P) and ¥1,989 (DM10010L), E: US$141 and US$297, and qdd100 is US$879.

---

### 5. Gaps and open items

- **BHL:** actuator mass, peak and continuous torque ratings, thermal data and the backlash-growth values are not published (Fig. 10 is an image only). The M6C12 motor mass is not verified because the MAD product specs are images. B-G431B-ESC1 official ratings are unconfirmed (st.com timed out; distributors blocked bots).
- **ODRI:** per-actuator cost is not published, and the continuous torque is not given.
- **openDog V3:** motor model, torque and actuator mass are GAP. They exist only in the videos and in BOM.ods, which was not downloaded under the no-binary rule. The ≈10:1 ratio is inferred from code (E).
- **OpenTorque:** no measured torque (80 N·m is theoretical). It is unclear whether the ~US$150 cost includes the cross-roller bearing or a driver. Blackbird's untethered walking was not verified.
- **Aaed Musa:** gear material for OpenQDD is not stated, no life tests are published, and no license file was found.
- **Paul Gould:** mass, measured peak torque and license are not given.
- **Skyentific:** torque values are only in videos, the files are paid, and the design is stepper-based.
- **Roozing 2024:** read from a third-party mirror of the paper, not the IEEE or UT host. The total actuator mass was estimated (E).
- **Urs et al.:** interface stated as CAN-FD by moteus family, not re-read for r4.5/r4.8. The repo has no license file.
- **Printed reducers generally:** no quantitative bearing-seat creep data exist in any source (F11), nor do life tests beyond ~60 h or above ~50% of rated torque.
- **SimpleFOC:** no legged actuator with published numbers was found. The WebSearch budget was exhausted mid-task (200/200), so later discovery relied on GitHub repo search and known primary URLs.
- **"Split-ring compound planetary" legged actuators:** none with numbers found; only design tools.
- **India specifics:** local availability and prices of motors (MAD, T-Motor, Eaglepower), bearings (6811ZZ, thin-section, cross-roller), filament (PA-CF, PC-CF) and import duty were not researched in this section.
- **Duplicate-check for the other sections:** Duke Humanoid, AGILOped, HECTOR, Roboto Origin and Zeroth use commercial actuators or servos and were only noted.

---

### Source index (primary unless marked)

1. BHL paper: https://arxiv.org/abs/2504.17249 ; HTML https://arxiv.org/html/2504.17249v1 ; site https://lite.berkeley-humanoid.org/
2. BHL docs: https://berkeley-humanoid-lite.gitbook.io/docs/llms.txt (index; pages read as .md)
3. BHL repos: https://github.com/HybridRobotics/Berkeley-Humanoid-Lite ; …-Lowlevel ; …-Assets ; issues/1
4. Recoil firmware: https://github.com/T-K-233/recoil-motor-controller-besc ; https://github.com/uncertainty-cc/Recoil-Motor-Controller ; author notes https://tk233.gitbook.io/notes/mechanical/mad-cycloidal-actuator.md
5. BHL 6512 MakerWorld: https://makerworld.com/en/models/1220823-6512-cycloidal-gear-actuator
6. MAD store JSON: https://store.mad-motor.com/products.json
7. ODRI: https://arxiv.org/html/1910.00093v2 ; https://github.com/open-dynamic-robot-initiative/open_robot_actuator_hardware ; https://github.com/open-dynamic-robot-initiative/master-board
8. Stanford Doggo: https://arxiv.org/abs/1905.04254 ; https://github.com/Nate711/StanfordDoggoProject ; BOM https://docs.google.com/spreadsheets/d/1MQRoZCfsMdJhHQ-ht6YvhzNvye6xDXO8vhWQql2HtlI
9. Pupper v3: https://pupper-v3-documentation.readthedocs.io/en/latest/learn_more/tech_specs.html
10. mjbots: https://mjbots.com/products.json (qdd100-beta-3, m05-6x-planetary-gearset, moteus-c1/n1/r4-11/x1, mj5208)
11. Urs et al.: https://arxiv.org/html/2202.12395 ; https://github.com/EMBiRLab/3DP-Actuator ; BOM https://docs.google.com/spreadsheets/d/1bmRzfv3GVEB19bbNFnGRmMcz0FWW6z87bu-cz9VUHL8
12. Roozing 2022: https://ris.utwente.nl/ws/portalfiles/portal/295490006/3D_printable_low_reduction_cycloidal_gearing_for_robotics.pdf ; https://github.com/geez0x1/2022-cycloidal-drive
13. Roozing 2024 (mirror): https://energiazero.org/cartelle/meccanica/riduttori/2023_cycloidal_drive_nonpinwheel.pdf ; https://github.com/geez0x1/2023-cycloidal-drive-nonpinwheel
14. OpenTorque: https://hackaday.io/project/159404-opentorque-actuator ; https://github.com/G-Levine/OpenTorque-Actuator ; Blackbird https://hackaday.io/project/160882-blackbird-bipedal-robot
15. Aaed Musa: https://www.aaedmusa.com/projects/openqdd ; /internalcycloidalactuator ; /capstandrive ; /cara ; /cara2 ; GitHub aaedmusa/OpenQDD-V1, Internal-Cycloidal-Actuator, Capstan-Drive
16. James Bruton: https://github.com/XRobots/openDogV3 ; https://github.com/XRobots/CycloidalDrive ; YouTube descriptions of IDs pWMB5VbLb6w, tgEOpl880KM, IVpYtyS5Q-k, ts2l_Em7fpI, eKZIJwJBjEs, dYgCxZjdNUU ; secondary (U) https://3dprintingindustry.com/news/james-bruton-begins-work-on-v3-of-his-open-source-3d-printed-robotic-dog-196644/ and https://hackaday.com/2021/12/18/opendog-version-3-is-ready-to-go-walkies/
17. Paul Gould: https://hackaday.io/project/157812-3d-printed-robot-actuator
18. Skyentific: https://skyentific.com/products.json ; YouTube a1sZSIDxpfg, BTzkSg_l70M
19. COMPAct: https://arxiv.org/html/2510.07197v2 ; https://github.com/singhaman1750/COMPAct
20. QLAUN: https://arxiv.org/html/2609.03623v1
21. UCLA C-QDD: https://arxiv.org/html/2410.16591v2
22. Open Source Leg: https://opensourceleg.org/hardware/
23. SimpleFOC boards: https://docs.simplefoc.com/boards ; hobby repos RedFeatherXO/Cycloidal_gearbox, JorgeMaker/NautilusController, mohammad-askari/stm32-esc, LittleMooMooDingDingCow/3D-Printed-Cycloidal-Robotic-Actuator, JeongSeoJin/Quasi-Direct-Drive-Actuator
24. Zhang et al. 2020 (nylon gears): http://wrap.warwick.ac.uk/126011/1/WRAP-physical-investigation-wear-thermal-characteristics-Zhang-2019.pdf (DOI 10.1016/j.triboint.2019.105953)
25. Prusament material pages: https://prusament.com/materials/pla/ , /prusament-petg/ , /prusament-asa/ , /prusament-pc-blend-carbon-fiber/ , /prusament-pa11-nylon-carbon-fiber/
26. Reference robots: Duke https://arxiv.org/html/2409.19795v2 ; AGILOped https://arxiv.org/abs/2509.09364 ; HECTOR https://arxiv.org/html/2312.11868v1 ; Roboto Origin https://github.com/Roboparty/roboto_origin (assets/BOM_EN.md) ; Zeroth https://github.com/kscalelabs/zeroth-bot
27. B-G431B-ESC1 third-party (U): https://hackaday.io/project/177578-b-g431b-esc-brushless-servo-controller
28. FX: https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml (2026-09-23)

## 4. Hobby BLDC motor data for DIY actuators


**Date of research:** 2026-09-24. **Scope:** 40xx–50xx (small), 52xx–63xx and 81xx (medium), 8308/8318/8325 (large) outrunners, plus 41xx/52xx gimbal motors, for DIY actuators with printed or machined reducers of about 6:1 to 20:1.
**Method:** Official product pages and store JSON were read with curl (desktop UA) or WebFetch. No logins, no forms, no binaries were saved.

### 0. Labels, conventions and how to read the numbers

- **VERIFIED (V):** read today on the manufacturer's own site, official store or official datasheet. For robot-usage claims, the project's own page counts.
- **ESTIMATED (E):** derived by me. The arithmetic is shown in the per-motor notes (Section 2).
- **UNVERIFIED (U):** from a reseller, a secondary source or a third-party measurement. Berkeley Humanoid Lite (BHL) lab measurements are counted as U because they are not the maker's data.
- **Kt estimate:** Kt ≈ 8.27 / KV (N·m/A), labelled E. I sanity-checked the rule against ODrive, which publishes Kt:
  - M8325s 100KV: 0.083 published vs 8.27/100 = 0.0827.
  - D6374 150KV: 0.055 vs 0.0551.
  - D5065 270KV: 0.031 vs 0.0306.
  - All three agree within about 1%. ODrive's convention is "voltage units are line-line amplitude" and "current units are phase amplitude".
  - BHL's *measured* Kt values are 1.1–1.7× higher than 8.27/KV. They use a delta-phase-current basis, so do not mix them with 8.27/KV numbers.
- **Output torque:** T_out = Kt × I × N × 0.85 (85% reducer efficiency, as briefed). Everything is shown at 9:1 and 12:1.
- **Stated current (I):**
  - I use the maker's own maximum or peak current and give its duration (e.g., 180 s, 60 s, 30 s or 3 s).
  - Drone ratings assume propeller airflow. In a closed actuator housing the continuous capability is lower (see Section 3).
  - Where no current rating is published, I use a current I chose and mark it **ASSUMED**.
- **Resistance (R):** given exactly as published. Most drone makers do not say whether it is line-to-line or phase resistance.
  - For copper-loss estimates I assume line-to-line: P ≈ 0.75·I²·R_ll. If R is really per-phase (wye), the loss doubles.
  - ODrive publishes phase-neutral R, so for ODrive P = 1.5·I²·R_ph.
- **Prices:** USD from the official store on 2026-09-24, for reference only. INR prices are Indian retailer "leads" and were not converted, because I read no FX rate source.
- **Snippet notation:** `"A" ¦ "B"` means adjacent table cells, both quoted verbatim.

---

### 1. Master table

Abbreviations: pp = pole pairs; ll = line-to-line; p-n = phase-neutral; "—" = not published / not found; OOS = out of stock.

| Brand | Model | Size class | KV | Kt N·m/A (pub or est) | R mΩ (as pub.; phase/line) | L µH | Mass g | Dia×Len mm | Config (NnPp) | Cont. A | Max A / W (duration) | Max V | Shaft (hollow?) | Official price USD (2026-09-24) | India leads | Motor peak N·m @ I (E) | Out. peak @9:1 / @12:1, 85% (E) | Label(s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T-Motor | Antigravity MN4004 KV300 (ODRI/Solo motor) | 40xx flat | 300 | 0.0276 E | 452 (conv. n/s) | — | 53 (incl. cable) | Φ44.35×19 | 18N24P | — | 9 A / 216 W (180 s) | 4–6S | "40mm" as published (likely typo); no external shaft | 145.90 per 2-pc set (=72.95/motor E) | none found | 0.25 @9 A | 1.9 / 2.5 (ODRI measured 2.5 N·m @12 A, 9:1) | V spec/price; E |
| T-Motor | Antigravity MN5008 KV170 | 50×08 class | 170 | 0.0486 E | 270 | — | 128 | Φ55.6×32 | 24N28P | — | 15 A / 720 W (180 s) | 6–12S | "IN：6mm" (internal) | 89.99 | Robokits: MN5008 340/400KV ₹8,413 | 0.73 @15 A | 5.6 / 7.4 | V; E |
| T-Motor | Antigravity MN5008 KV340 | 50×08 class | 340 | 0.0243 E | 55 | — | 135 | Φ55.6×32 | 24N28P | — | 35 A / 760 W (180 s) | 6S | IN 6 mm | 89.99 | Robokits ₹8,413 | 0.85 @35 A | 6.5 / 8.7 | V; E |
| T-Motor | MN5212 KV340 (Stanford Doggo motor) | 52×12 | 340 | 0.0243 E | 69 | — | 205 excl. / 249 incl. cable | Φ59×33.5 (stator 52×12) | 24N22P | 35 A (180 s) | — / 840 W (180 s) | 4–8S | 4 mm solid | 109.90 | none found | 0.85 @35 A | 6.5 / 8.7 | V; E |
| T-Motor | MN501-S KV240 (IP45) | 50xx | 240 | 0.0345 E | 85 | — | 170 | Φ55.6×33.9 | 24N28P | — | 25 A / 1200 W (180 s) | 6–12S | IN 6 / OUT 4 mm | 99.90 | Robokits: MN501-S 300KV ₹9,180 | 0.86 @25 A | 6.6 / 8.8 | V; E |
| T-Motor | Antigravity MN6007 II KV160 | 60×07 class | 160 | 0.0517 E | 178 | — | 159 | Φ67.2×26.1 | 24N28P | — | 23.7 A / 1120 W (180 s) | 12S | IN 6 / OUT 4 mm | 129.99 | Robokits: MN6007-II 320KV ₹13,464 | 1.23 @23.7 A | 9.4 / 12.5 | V; E |
| T-Motor | U8 Lite KV100 | 8xxx pancake (Φ87.1) | 100 | 0.0827 E | 170±5 | — | 238 | Φ87.1×27.05 | 36N42P | — | 29.3 A / 1406.4 W (180 s) | 12S | 15 mm | 299.99 | none found | 2.42 @29.3 A | 18.5 / 24.7 | V; E |
| T-Motor | Antigravity MN8014 KV100 | 80xx pancake | 100 | 0.0827 E | 65 | — | 392 | Φ87.8×31.5 | 36N42P | — | 52 A / 2423 W (180 s) | 12S | IN 12 mm | 279.90 | none found | 4.30 @52 A | 32.9 / 43.9 | V; E |
| T-Motor | Antigravity MN8017 KV120 | 80xx pancake | 120 | 0.0689 E | 45 | — | 453 | Φ87.8×34.5 | 36N42P | — | 68.6 A / 3180 W (180 s) | 12S | IN 12 mm | 289.90 | none found | 4.73 @68.6 A | 36.2 / 48.2 | V; E |
| T-Motor | MN805-S KV120 (IP45) | 80xx | 120 | 0.0689 E | 48 | — | 620 | Φ89×44.4 | 24N28P | — | 65 A / 3200 W (180 s) | 6–12S | IN 12 / OUT 8 mm | 269.99 | none found | 4.48 @65 A | 34.3 / 45.7 | V; E |
| T-Motor | GB4106 gimbal KV53 | 41xx gimbal | 53 | 0.156 E | 15,300 (15.3 Ω) | — | 70 | ø47.75×20 | 12N14P | — | torque pub. 0.2 N·m | 3–6S | hollow, "Hole Size 5.6mm" | 45.90 | Robokits ₹4,284 | 0.2 (published) | 1.5 / 2.0 | V; E |
| T-Motor | GB54-2 gimbal KV26 (5208-class) | 54xx gimbal | 26 | 0.318 E | 15,000 (15 Ω) | — | 156 | ø60.7×25 | 12N14P | — | torque pub. 0.45 N·m | 3–6S | hollow, "Hole Size 12.7mm" | 74.90 | Robokits ₹6,579 | 0.45 (published) | 3.4 / 4.6 | V; E |
| SunnySky | X5212S KV340 | 52×12 | 340 | 0.0243 E | 67 (USA store) / 28 (maker) | — | 260 (USA) / 234 (maker) | Φ59×37.5 (USA) / φ59×35 (maker) | 24N22P (USA) / 24N28P (maker) | 46.5 A/30 s (USA) / 92 A/30 s (maker) | 1032 W (USA) / 2300 W (maker) | 6S | 4 mm | 69.99 (SunnySky USA) | none found | 1.13 @46.5 A (2.24 @92 A) | 8.7 / 11.5 (17.1 / 22.8) | V (two official sources conflict); E |
| SunnySky | X6212S KV180 | 62×12 | 180 | 0.0459 E | 102 (USA) / 73 (maker) | — | 323 / 302 | Φ69.3×40 | 24N28P | 38 A/30 s (USA) / 44 A/30 s (maker) | 1680 W (USA) / 1100 W (maker) | 12S | 4 mm (USA) / 8.0 mm (maker) | 74.99 | none found | 1.75 @38 A (2.02 @44 A) | 13.4 / 17.8 (15.5 / 20.6) | V (conflict); E |
| SunnySky | V8110 KV100 | 81×10 | 100 | 0.0827 E | 98 | — | 337 | 89.5 (dia.) × 30 (length), as tabulated | 36N42P | 45 A/30 s | 2160 W | 12S | not clearly stated | 185.99 | none found | 3.72 @45 A | 28.5 / 38.0 | V; E |
| SunnySky | X8318S KV100 | 83×18 | 100 | 0.0827 E | 54 (USA) / 49 (maker) | — | 635 (USA) / 645 (maker) | Φ91.6×46.5 | 36N42P | 50 A/30 s (USA) / 59 A/30 s (maker) | 2500 W (USA) / 2832 W (maker) | 12S | 15 mm | 159.99 | none found | 4.14 @50 A (4.88 @59 A) | 31.6 / 42.2 (37.3 / 49.8) | V (conflict); E |
| MAD | 5010 EEE V2.0 **110KV** (BHL 5010 actuator motor) | 50×10 | 110 | 0.0752 E (BHL meas. 0.1176, delta basis, U) | BHL meas.: R_ll 413; R_phase(delta) 619 (U) | 85 per phase (BHL, U) | 162 | D56×32.7 | 14 pp (slots n/s) | — | not published for 110KV | 6S; 8S; 12S (family) | IN 5 mm | 84.00 | none found | 1.13 @15 A (ASSUMED I) | 8.6 / 11.5 (BHL-style 15:1 @0.9: 15.2) | V (official); U (BHL); E |
| MAD | 5010 200KV (legacy EEE/IPE page) | 50×10 | 200 | 0.0414 E | 176 | — | 155 EEE / 170 IPE | 56×27.9 EEE / 56×27.5 IPE | 24N28P | 300 W (60 min) | 23 A / 520 W (60 s) EEE; 22 A / 500 W (15 s) IPE | 6–8S | EEE 6 mm; IPE hollow OD 15 / ID 13 mm | legacy MSRP 79 (EEE) / 89 (IPE); current store 84 (EEE V2.0) / 88 (IPE V3.0) | none found | 0.95 @23 A | 7.3 / 9.7 | V (legacy site); E |
| MAD | 5012 160KV (legacy IPE page) | 50×12 | 160 | 0.0517 E | 161 | — | 180 | 56×29.5 | 24N28P | 200 W (60 min) | 14 A / 400 W (180 s) | thrust quoted at 8S (current V3: "4S;6S") | hollow OD 15 / ID 13 mm (legacy); V3.0 "IN: 6 mm" | legacy 99; current 5012 IPE V3.0 = 98 | none found | 0.72 @14 A | 5.5 / 7.4 | V; E |
| MAD | 5015 320KV (legacy IPE page) | 50×15 | 320 | 0.0258 E | 51 | — | 230 | 56×32.5 | 24N28P | 350 W (60 min) | 45 A / 1000 W (60 s) | thrust quoted at 6S | hollow OD 15 / ID 13 mm (legacy); V3.0 IN 6 mm | legacy 109; current 5015 IPE V3.0 = 108 (150–420KV) | none found | 1.16 @45 A | 8.9 / 11.9 | V; E |
| MAD | M6C12 150KV (BHL 6512 actuator motor) | 64×12 | 150 | 0.0551 E (BHL meas. 0.0919, U) | 135 (legacy page); BHL R_ll 125.7 (U) | 32.5 per phase (BHL, U) | 257 (EEE V3) / 260 (legacy) | D72×33.4 (EEE V3) / 72×29.5 (legacy) | legacy "24N22P" vs V3 "14" pp (conflict) | 1000 W (60 min, legacy) | 35 A / 1800 W (60 s, legacy) | 12S (150KV) | IN 6 mm | 129 (EEE) / 146 (IPE V3) | none found | 1.93 @35 A | 14.8 / 19.7 (15:1 @0.9: 26.1) | V; U; E |
| MAD | 8108 100KV (legacy) → today's M8S C08 (8108) EEE 100KV | 81×8 | 100 | 0.0827 E | 186 (legacy) | — | 250 (legacy EEE); M8S C08 283 or 252 (both on page) | 86.8×27.5 (legacy); D87.3×26.75 (M8S) | 36N42P (legacy); 21 pp (M8S) | 350 W (60 min) | 24 A / 750 W (60 s) | 6–12S (legacy thrust); M8S "100KV/12S" | hollow OD 15 / ID 13 mm (legacy); M8S IN 12 mm | legacy 208 (EEE); current M8S C08 = 269 | none found | 1.98 @24 A | 15.2 / 20.2 | V; E |
| MAD | 8118 80KV (legacy) | 81×18 | 80 | 0.1034 E | 93 | — | 500 | 88.6×38 | 36N40P | 800 W (60 min) | 33 A / 1500 W (180 s) | 12S (thrust) | 10 mm | legacy 249; current 8118 IPE 80/100KV = 267 | none found | 3.41 @33 A | 26.1 / 34.8 | V; E |
| MAD | 8318 IPE 100KV | 83×18 | 100 | 0.0827 E | 36 (reseller, U) | — | 660 / 639 (reseller, U) | D91.5×41 (official) | 21 pp (official) = 36N42P (reseller) | — | 68 A / 3224 W (reseller, no duration, U) | 12S (reseller) | IN 15 mm | 198 (black) / 197 (silver) | none found | 5.62 @68 A (U current) | 43.0 / 57.4 | V dims/price; U elec.; E |
| Eaglepower | LA8308 KV90 (likely OpenQDD motor) | 83×08 | 90 | 0.0919 E | 186 (0.186 Ω, reseller) | — | 336 (reseller; same site's blog "~325 g") | 92×28.5 | — | 22 A (reseller; blog "~40-45A") | 900 W peak (reseller) | 6–12S | 6 mm (reseller blog) | no official store price found | Technobotix ₹10,999; TNT e-Comp ₹10,260; The Engineer Store ₹11,738 (OOS) | 2.02 @22 A | 15.5 / 20.6 (OpenQDD: 16.36 N·m @9:1, V) | U; E |
| Eaglepower | EA95 8318 KV100 | 83×18 | 100 | 0.0827 E | 55 (0.055 Ω, reseller) | — | 695 | Φ92×40 | — | 58 A (reseller) | 2900 W cont. (reseller) | 8–14S | — | none official; ArrisHobby 99.00 (U) | none found | 4.80 @58 A | 36.7 / 48.9 | U; E |
| iFlight | iPower GM4108H-120T gimbal | 41xx gimbal | ≈27 E (513–567 rpm @20 V) | 0.306 E from KV, **but** published load torque implies 0.078–0.118 | 11,100 (11.1 Ω ±5%) | — | 124 | Ф47 × 22.7 (height as published) | 24N22P | — | "Maximum power: ≤25W" | 3–5S | **hollow OD 10 / ID 8 mm** | 35.90 | none found | 0.12–0.18 @1.5 A (published) | 1.35 / 1.80 | V; E |
| iFlight | iPower GM5208-12 gimbal | 52xx gimbal | ≈24 E | 0.345 E from KV; published 0.18–0.25 N·m @1 A | 15,200 | — | 195 | Ф63 × 22.7 | 12N14P | — | "≤40W" | 3–5S | **hollow OD 15 / ID 12 mm** | 39.90 | none found | 0.18–0.25 @1 A (published) | 1.87 / 2.50 | V; E |
| iFlight | XING 8108 87KV | 81×08 | 87 | 0.0951 E | 220 (0.22 Ω) | — | 260 | Φ87.2×25 | 36N42P | — | 21.7 A / 1050 W (180 s) | 6–12S | 15 mm | 239.00 | none found | 2.06 @21.7 A | 15.8 / 21.0 | V; E |
| iFlight | eX8108 105KV | 81xx | 105 | 0.0788 E | 186 (printed "186MΩ") | — | 228.6 | Φ87×24.5 | — | — | 24 A / 750 W (180 s) | 6–12S | — | 99.99 (sold out) | none found | 1.89 @24 A | 14.5 / 19.3 | V; E |
| Tarot | 5008 340KV (TL96020) | 50×8 | 340 | 0.0243 E | — | — | 168 | 58.5 ("Diameter of stator", sic) × 38.5 | 12N14P | — | 40 A / 700 W (no duration) | (3–6S per resellers, U) | 4 mm | 235 RMB (official page, listing dated 2013-08-03) | Robokits ₹3,378 (search result) | 0.97 @40 A | 7.4 / 9.9 | V; E |
| Tarot | 4108 380KV (TL68P07), multirotor, not gimbal | 41×08 | 380 | 0.0218 E | 135 ("Impedence", reseller) | — | 93 | 46×24 | 24N22P | — | — | 6S | 4 mm | official page now empty; ArrisHobby 29.99 (U) | indianrobostore.com (search result) | 0.33 @15 A (ASSUMED I) | 2.5 / 3.3 | U; E |
| Flipsky | 6374 190KV 3250 W (sensored) | 63×74 e-skate | 190 | 0.0435 E | 50 (0.05 Ohm) | — | 860 | 63×74 | 14 poles (7 pp) | — | 85 A / 3250 W (no duration) | 12S | 8 mm keyed, 32 mm long | 99.00 (no pulley) | generic 6374 listings only (Robokits, Amazon.com; not product-matched) | 3.70 @85 A | 28.3 / 37.7 | V; E |
| Flipsky | 6374 Battle Hardened 140KV 3500 W | 63×74 | 140 | 0.0591 E | 50 | — | 980 | — | 14 poles | — | 85 A / 3500 W (no duration) | 3–12S | 8 or 10 mm | 87.00 (no pulley) | — | 5.02 @85 A | 38.4 / 51.2 | V; E |
| Flipsky | 6354 Battle Hardened 140KV 2450 W | 63×54 | 140 | 0.0591 E | 53 | — | — | 63×54 | 14 poles | — | 65 A / 2450 W | 4–14S | 8 mm round / 10 mm D | 71.00 | — | 3.84 @65 A | 29.4 / 39.2 | V; E |
| Flipsky | 6384 Battle Hardened 140KV 4000 W | 63×84 | 140 | 0.0591 E | 50 | — | 1300 | 63×84 | 14 poles | — | 95 A / 4000 W | 4–14S | 8 mm | 113.00 (no pulley) | — | 5.61 @95 A | 42.9 / 57.2 | V; E |
| Flipsky | 5065 200KV 1800 W (sensored) | 50×65 | 200 | 0.0414 E | — | — | 475 | 49×63.5 | 12N14P | 21 A rated (1000 W rated) | 38 A / 1800 W | 6–12S | 8 mm D | 56.80 | — | 1.57 @38 A | 12.0 / 16.0 | V; E |
| Maytech | MTO6374-170-HA-C (sealed, sensored) | 63×74 | 170 (±5–10% per maker) | 0.0486 E | — | — | — | — | — | 60 A rated | 65 A / 3550 W | 3–12S (12–50 V) | 8 mm, 26 mm long | 82.40 | — | 3.16 @65 A | 24.2 / 32.3 | V; E |
| ODrive | D5065 270KV | 50×65 | 270 | **0.031 V** | 39 p-n | 16 | — | — | 12N14P (7 pp) | 45 free air / 65 forced air | 85 A (3 s) | — | 8 mm + 8 mm rear shaft (AMT encoder) | 89.00 | none found | 2.64 @85 A | 20.2 / 26.9 | V; E |
| ODrive | D6374 150KV | 63×74 | 150 | **0.055 V** | 39 p-n | 24 | — | — | 12N14P (7 pp) | 50 free air / 70 forced air | 90 A (3 s) | — | 10 mm + 8 mm rear shaft (AMT encoder) | 119.00 | none found | 4.95 @90 A | 37.9 / 50.5 | V; E |
| ODrive | M8325s 100KV | 83×25 pancake | 100 | **0.083 V** | 24 p-n | 9.9 | 840 | Ø92 × 46.5 (mount plane to top) | 20 pp | 40 free air / 60 forced air | 80 A (3 s) | — | encoder magnet included on shaft | 149.00 | none found | 6.64 @80 A (3.32 @40 A cont.) | 50.8 / 67.7 (cont. 25.4 / 33.9) | V; E |
| Rctimer | 5010-14 360KV (the "generic 5010 360KV") | 50×10 | 360 | 0.0230 E | — | — | 92 | Φ50×26 | 12N14P | — | — | (2–6S per resellers, U) | out 4 / in 5 mm | 12.99 (list 18.18; page shows "MOQ: 500") | Robu.in "5010 360KV High Torque" (search result; page behind Cloudflare) | 0.46 @20 A (ASSUMED I) | 3.5 / 4.7 | V; E |

**Per-mass figures (E):** Kt/m in N·m/A/kg and motor peak torque/m in N·m/kg, using the currents stated above.

| Motor | Kt/m | T_peak/m |
|---|---|---|
| MN4004 | 0.520 | 4.68 |
| MN5008-170 | 0.380 | 5.70 |
| MN5008-340 | 0.180 | 6.31 |
| MN5212 | 0.119 | 4.15 |
| MN501-S | 0.203 | 5.07 |
| MN6007 II | 0.325 | 7.70 |
| U8 Lite | 0.347 | 10.18 |
| MN8014 | 0.211 | 10.97 |
| MN8017 | 0.152 | 10.44 |
| MN805-S | 0.111 | 7.23 |
| X5212S (USA) | 0.094 | 4.35 |
| X6212S (USA) | 0.142 | 5.41 |
| V8110 | 0.245 | 11.04 |
| X8318S (maker) | 0.128 | 7.56 |
| MAD 5010-110 | 0.464 | 6.96 |
| MAD 5010-200 | 0.267 | 6.14 |
| MAD 5012 | 0.287 | 4.02 |
| MAD 5015 | 0.112 | 5.06 |
| M6C12 | 0.215 | 7.51 |
| MAD 8108 | 0.331 | 7.94 |
| MAD 8118 | 0.207 | 6.82 |
| MAD 8318 | 0.125 | 8.52 |
| LA8308 | 0.273 | 6.02 |
| EA95 8318 | 0.119 | 6.90 |
| XING 8108 | 0.366 | 7.93 |
| eX8108 | 0.345 | 8.27 |
| Tarot 5008 | 0.145 | 5.79 |
| Flipsky 6374-190 | 0.051 | 4.30 |
| Flipsky 6374 BH-140 | 0.060 | 5.12 |
| Flipsky 6384-140 | 0.045 | 4.32 |
| Flipsky 5065 | 0.087 | 3.31 |
| M8325s | 0.099 | 7.90 |
| Rctimer 5010 | 0.250 | 4.99 |

---

### 2. Per-motor notes: sources, verbatim snippets (≤15 words) and arithmetic

#### T-Motor (official store store.tmotor.com; all V unless noted)

**MN4004 KV300 (Antigravity)**
- URL: https://store.tmotor.com/product/mn4004-kv300-motor-antigravity-type.html
- Title and price: "MN4004 Antigravity Type 4-6S UAV Motor KV300 - 2PCS/SET" ¦ "$145.90".
- Specs: "Weight (Incl. Cable)" ¦ "53g"; "Motor Dimensions" ¦ "Φ44.35×19mm"; "Internal Resistance" ¦ "452mΩ"; "Configuration" ¦ "18N24P".
- Shaft: "Shaft Diameter" ¦ "40mm". This is implausible for a 44 mm motor; flagged as a likely typo.
- Ratings: "Rated Voltage(Lipo)" ¦ "4-6S"; "Peak Current(180s)" ¦ "9A"; "Max Power (180S)" ¦ "216W".
- Also listed on the same page, KV400: "359mΩ", "12A", "300W".
- Robot use (V, ODRI project pages):
  - https://github.com/open-dynamic-robot-initiative/open_robot_actuator_hardware/blob/master/mechanics/actuator_module_v1/actuator_module_v1.1.md: "T-Motor Antigravity 4004 300kV"; "24 magnets / 12 pole pairs / 18 slots"; "weighs 150g and outputs 2,5Nm at 12A"; "The total gear reduction is 9:1."
  - Solo link: https://open-dynamic-robot-initiative.github.io/ says "the actuator module, the one legged-robot, the quadruped Solo".
- E:
  - Kt = 8.27/300 = 0.0276; T = 0.0276×9 = 0.248 N·m; 9:1 → 0.248×9×0.85 = 1.90; 12:1 → 2.53 N·m.
  - **Cross-check:** 0.0276×12 A×9×0.85 = 2.53 N·m, against ODRI's measured "2,5Nm at 12A". The method is validated.
  - Note that ODRI runs 12 A on a motor that T-Motor rates at 9 A (180 s), i.e., short bursts above the drone rating.
  - Price per motor: 145.90/2 = 72.95. Copper loss at 9 A: 0.75×81×0.452 = 27 W.

**MN5008 KV170 / KV340 (Antigravity)**
- URLs: https://store.tmotor.com/product/mn5008-kv170-motor-antigravity-type.html and …/mn5008-kv340-motor-antigravity-type.html
- Price on both pages: "$89.99".
- Common specs: "Motor Size" ¦ "Φ55.6*32mm"; "Configuration" ¦ "24N28P"; "Shaft Diameter" ¦ "IN：6mm".
- KV170: "Rated Voltage（Lipo）" ¦ "6-12S"; "Peak Current（180s）" ¦ "15A"; "Max. Power（180s）" ¦ "720W"; "Motor Weight（Incl. Cable）" ¦ "128g"; "Internal Resistance" ¦ "270mΩ".
- KV340: "6S"; "35A"; "760W"; "135g"; "55mΩ".
- E, KV170: Kt 0.0486; ×15 A = 0.73 N·m → 5.6 / 7.4 N·m.
- E, KV340: Kt 0.0243; ×35 A = 0.851 → 6.5 / 8.7 N·m.
- India lead: Robokits lists "T-Motor Antigravity MN5008 340KV" ₹8,413.00 and "MN5008 400KV" ₹8,413.00 (https://robokits.co.in/t-motor-parts/t-motor-motor?limit=100, listing read, not deep-checked).

**MN5212 KV340 (Navigator)**
- URL: https://store.tmotor.com/product/mn5212-kv340-motor-navigator-type.html
- Price: "$109.90".
- Electrical: "Internal Resistance" ¦ "69mΩ"; "Configuration" ¦ "24N22P".
- Geometry: "Shaft Diameter" ¦ "4mm"; "Motor Dimensions" ¦ "Φ59×33.5mm"; "Stator Diameter" ¦ "52mm"; "Stator Height" ¦ "12mm".
- Mass: "Weight Excluding Cables" ¦ "205g"; "Weight Including Cables" ¦ "249g".
- Ratings: "No.of Cells(Lipo)" ¦ "4-8S"; "Max Power (180S)" ¦ "840W"; "Max Continuous Current 180S" ¦ "35A". The KV420 variant is listed at "60A", "1440W".
- Robot use (V): Stanford Doggo README https://raw.githubusercontent.com/Nate711/StanfordDoggoProject/master/README.md says "two TMotor MN5212 motors mounted on the carbon fiber side panel" and "between a 16T pulley and a 48T pulley". Ratio 48/16 = 3:1 (E).
- E: 0.0243×35 = 0.851 N·m → 6.5 / 8.7 N·m. Copper loss 0.75×35²×0.069 = 63 W.

**MN501-S KV240 (IP45)**
- URL: https://store.tmotor.com/product/mn501-s-kv240-motor-navigator-type.html
- Price: "$99.90".
- Geometry: "Motor Size" ¦ "Φ55.6*33.9mm"; "Configuration" ¦ "24N28P"; "Shaft Diameter" ¦ "IN：6mm，OUT：4mm".
- Ratings: "Peak Current（180s）" ¦ "25A"; "Max.Power（180s）" ¦ "1200W"; "Motor Weight (indl. Cable)" ¦ "170g"; "Internal Resistance" ¦ "85mΩ".
- Other KVs on the page: KV300 "63mΩ", "40A"; KV360 "45mΩ", "40A".
- E: 8.27/240 = 0.0345; ×25 = 0.861 → 6.6 / 8.8 N·m.
- India lead: Robokits "T-Motor Navigator Waterproof MN501-S 300KV" ₹9,180.00.

**MN6007 II KV160 (Antigravity)**
- URL: https://store.tmotor.com/product/mn6007-v2-motor-antigravity-type.html
- Price: "$129.99".
- Geometry: "Motor Size" ¦ "Φ67.2*26.1mm"; "Configuration" ¦ "24N28P"; "Shaft Diameter" ¦ "IN:6" ¦ "OUT:4".
- KV160: "Internal Resistance" ¦ "178mΩ"; "Rated Voltage(Lipo)" ¦ "12S"; "Peak Current（180s）" ¦ "23.7A"; "Motor Weight（Incl. Cable）" ¦ "159g"; "Max. Power（180s）" ¦ "1120W".
- KV320: "47.5mΩ", "44.2A".
- E: 8.27/160 = 0.0517; ×23.7 = 1.225 N·m → 9.4 / 12.5 N·m. Copper loss 0.75×23.7²×0.178 = 75 W.
- India lead: Robokits "T-Motor Antigravity MN6007-II 320KV" ₹13,464.00.

**U8 Lite KV100 (and siblings)**
- URLs: https://store.tmotor.com/product/u8-lite-kv100-u-efficiency.html (the KV150 and KV190 pages carry the same table)
- Price: "$299.99".
- Geometry: "Diameter" ¦ "87.1mm"; "Configuration" ¦ "36N42P"; "Height" ¦ "27.05mm"; "Shaft Diameter" ¦ "15mm".
- KV100: "Motor Weight (Incl. Cable)" ¦ "238g"; "Internal Resistance" ¦ "170±5mΩ"; "Peak Current（180s）" ¦ "29.3A"; "Max. Power（180s）" ¦ "1406.4W".
- Other KVs: KV150 "85±5mΩ", "29.7A / 26.5A"; KV190 "48±3mΩ", "43.7A".
- U8 II Lite (https://store.tmotor.com/product/u8-v2-lite-u-efficiency.html, "$299.90"): "Internal Resistance" ¦ "134-141mΩ"; "Peak Current(180s)" ¦ "31A"; "253g/256g net version"; "Shaft Diameter" ¦ "IN：12mm".
- E: 0.0827×29.3 = 2.42 N·m → 18.5 / 24.7 N·m. Copper loss 0.75×29.3²×0.170 = 109 W.
- Context (V, Ben Katz blog https://build-its-inprogress.blogspot.com/search?q=U8): "my T-Motor U8's and U8 knock-offs". His motor-data page https://build-its.blogspot.com/p/motor-characterization.html lists "EX-8 105 Kv (T-Motor U-8 clone), 22V, 40A" and "T-Motor U-8 Pro 100 Kv".

**MN8014 KV100 / MN8017 KV120 / MN8012 KV100 (Antigravity 80xx)**
- URLs: https://store.tmotor.com/product/mn8014-motor-antigravity-type.html, …/mn8017-motor-antigravity-type.html, …/mn8012-motor-antigravity-type.html
- MN8014: "$279.90"; "Motor Size" ¦ "Φ87.8*31.5mm"; "Configuration" ¦ "36N42P"; "Shaft Diameter" ¦ "IN：12mm"; "Internal Resistance" ¦ "65mΩ"; "Peak Current（180s）" ¦ "52A"; "Weight (Incl. Cable)" ¦ "392g"; "Max. Power （180s）" ¦ "2423W"; "Rated Voltage(Lipo)" ¦ "12S".
- MN8017: "$289.90"; "Φ87.8*34.5mm"; "KV" ¦ "120"; "45mΩ"; "68.6A"; "453g"; "3180W".
- MN8012 (notes only): "$269.90"; "Φ87.8*29mm"; "85mΩ"; "40A"; "351g".
- E, MN8014: 0.0827×52 = 4.30 N·m → 32.9 / 43.9; 16:1 → 58.5; 20:1 → 73.1 N·m. Copper loss 0.75×52²×0.065 = 132 W.
- E, MN8017: 8.27/120 = 0.0689; ×68.6 = 4.73 → 36.2 / 48.2 N·m.

**MN805-S KV120 / MN801-S KV120 (IP45 Navigator 80xx)**
- URLs: https://store.tmotor.com/product/mn805-s-kv120-motor-navigator-type.html, …/mn801-s-kv120-motor-navigator-type.html
- MN805-S: "$269.99"; "Motor Size" ¦ "Φ89*44.4mm"; "Configuration" ¦ "24N28P"; "Shaft Diameter" ¦ "IN：12mm，OUT：8mm"; "Peak Current（180s）" ¦ "65A"; "Max.Power（180s）" ¦ "3200W"; "Motor Weight (indl. Cable)" ¦ "620g"; "Internal Resistance" ¦ "48mΩ".
- MN801-S KV120 (notes only): "$249.99"; "Φ89*39.4mm"; "45A"; "2200W"; "470g"; "80mΩ".
- E, MN805-S: 0.0689×65 = 4.48 → 34.3 / 45.7 N·m.
- E, MN801-S: 0.0689×45 = 3.10 → 23.7 / 31.6 N·m.

**GB4106 / GB54-1 / GB54-2 gimbal motors**
- URLs: https://store.tmotor.com/product/gb4106-gimbal-type.html, …/gb54-1-gimbal-type.html, …/gb54-2-gimbal-type.html
- GB4106: "$45.90"; "KV" ¦ "53"; "Motor Dimensions" ¦ "ø47.75*20mm"; "Motor Weight(Incl. Cable)" ¦ "70g"; "Hole Size" ¦ "5.6mm"; "Configuration" ¦ "12N14P"; "Internal Resistance" ¦ "15.3Ω"; "Motor's Torsion" ¦ "（Nm）" ¦ "0.2"; "Rated Voltage (Lipo)" ¦ "3-6S".
- GB54-2: "$74.90"; "KV" ¦ "26"; "ø60.7*25mm"; "156g"; "Hole Size" ¦ "12.7mm"; "12N14P"; "15Ω"; "Motor's Torsion（Nm）" ¦ "0.45".
- GB54-1: "$69.90"; KV 33; "137g"; "15.6Ω"; "0.33".
- E:
  - GB4106: Kt 8.27/53 = 0.156. Stall current at 24 V if R is line-to-line: 1.155×24/15.3 = 1.81 A → 0.28 N·m, the same order as the published 0.2 N·m.
  - Outputs with the published torque: GB4106 0.2×9×0.85 = 1.53 and ×12 → 2.04 N·m; GB54-2 0.45 → 3.44 / 4.59 N·m.
- India leads: Robokits (https://robokits.co.in/t-motor-parts/t-motor-gimbal?limit=100): "Tiger Gimbal Motor GB54-2 26KV" ₹6,579.00; GB54-1 ₹6,426.00; GB4106 ₹4,284.00.

#### SunnySky (maker site en.rcsunnysky.com and "Official SunnySky USA Store" sunnyskyusa.com)

The two official sources publish **different** numbers. Both are recorded as V, and the conflict is flagged. The maker pages look like a newer revision (for example, the X5212S is now 24N28P).

**X5212S KV340**
- USA store: https://sunnyskyusa.com/products/x5212s (read via .js JSON). Price: variant "340" = 69.99.
  - Geometry: "Stator Diameter" ¦ "52mm"; "Rotor Diameter" ¦ "59mm"; "Stator Thickness" ¦ "12mm"; "Shaft Diameter" ¦ "4mm"; "No.of Stator Slots" ¦ "24"; "No.of Rotor Poles" ¦ "22"; "Body Length" ¦ "37.5mm".
  - Ratings: "Max Lipo Cell" ¦ "6S"; "Motor Resistance" ¦ "67mΩ"; "Max Continuous Current" ¦ "46.5A/30s"; "Max Continuous Power" ¦ "1032W"; "Weight" ¦ "260g".
- Maker: http://en.rcsunnysky.com/xs-multi-rotorpowered/1089.html
  - "X5212S/ KV340"; "Stator/Rotor Poles" ¦ "24N28P"; "Internal resistance" (KV340 column) ¦ "28mΩ"; "Motor size" ¦ "φ59.0*35mm"; "Shaft diameter" ¦ "4.0mm"; "234g"; "2300W"; "92A/30s".
- E: 0.0243×46.5 = 1.13 → 8.7 / 11.5 N·m. With the maker's 92 A: 2.24 → 17.1 / 22.8 N·m.

**X6212S KV180**
- USA store: https://sunnyskyusa.com/products/x6212s. Price 74.99.
  - "Stator Diameter" ¦ "62mm"; "Rotor Diameter" ¦ "69.3mm"; "Stator Thickness" ¦ "12mm"; "Shaft Diameter" ¦ "4mm"; "No.of Rotor Poles" ¦ "28"; "Body Length" ¦ "40mm".
  - "Max Lipo Cell" ¦ "12S"; "Motor Resistance" ¦ "102mΩ"; "Max Continuous Current" ¦ "38A/30s"; "Max Continuous Power" ¦ "1680W"; "Weight" ¦ "323g".
- Maker: http://en.rcsunnysky.com/xs-multi-rotorpowered/1090.html: "X6212S/ KV180"; "24N28P"; "73mΩ"; "φ69.3*40.0mm"; "Shaft diameter" ¦ "8.0mm"; "302g"; "12S"; "1100W"; "44A/30s".
- E: 8.27/180 = 0.0459; ×38 = 1.75 → 13.4 / 17.8 N·m. With 44 A: 2.02 → 15.5 / 20.6 N·m.

**V8110 KV100**
- Maker: http://en.rcsunnysky.com/v-multi-rotorefficiencytype/1171.html
  - "V8110/KV100"; "Stator/Rotor Poles" ¦ "36N42P"; "Internal resistance" ¦ "98MΩ" (sic, means mΩ); "Motor length: 30mm"; "89.5mm" (tabulated under "Shaft diameter", evidently the motor diameter); "337g"; "12s"; "2160W"; "45A/30s".
  - KV90: "114MΩ", "42A/30s"; KV120: "78mΩ", "58A/30s".
- Price: USA store JSON, "SunnySky V8110 High Efficiency Brushless Motors", variant "100" = 185.99 (https://sunnyskyusa.com/products/sunnysky-v8110-motors).
- E: 0.0827×45 = 3.72 → 28.5 / 38.0 N·m. Copper loss 0.75×45²×0.098 = 149 W (burst only).

**X8318S KV100 (KV120)**
- USA store: https://sunnyskyusa.com/products/x8318s. Price 159.99.
  - "Stator Diameter" ¦ "83mm"; "Rotor Diameter" ¦ "91.6mm"; "Stator Thickness" ¦ "18mm"; "Shaft Diameter" ¦ "15mm"; "No.of Stator Slots" ¦ "36"; "No.of Rotor Poles" ¦ "42"; "Body Length" ¦ "46.5mm".
  - "Max Lipo Cell" ¦ "12S"; "Motor Resistance" ¦ "54mΩ"; "Max Continuous Current" ¦ "50A/30s"; "Max Continuous Power" ¦ "2500W"; "Weight" ¦ "635g".
  - KV120: "37mΩ", "64A/30s".
- Maker: http://en.rcsunnysky.com/xs-multi-rotorpowered/1096.html
  - "X8318S/ KV100"; "36N42P"; "Internal resistance" ¦ "49mΩ" ¦ "33mΩ"; "Motor size" ¦ "φ91.6*46.5mm"; "Shaft diameter" ¦ "15.0mm"; "645g" ¦ "676g"; "Maximum continuous current" ¦ "59A/30s" ¦ "80A/30s"; "2832W" ¦ "3840W".
- E: 0.0827×50 = 4.14 → 31.6 / 42.2 N·m. With 59 A: 4.88 → 37.3 / 49.8; 16:1 → 66.4; 20:1 → 82.9 N·m. Copper loss at 59 A: 0.75×59²×0.049 = 128 W.
- Not found at SunnySky: no "V5010" exists in the maker's V-series listing (V3508, V4010, V5208, V5210, V8110, V8117 seen) or in the USA store catalogue.

#### MAD Components (current: mad-motor.com and store.mad-motor.com; legacy official site: madcomponents.co, footer "Copyright 2016-2023")

- The current store pages carry KV-specific electrical data only as images, which I did not download.
- The legacy official pages carry full text specs. Those are V but may describe older revisions.
- Current prices come from the Shopify JSON at https://store.mad-motor.com/products.json:
  - "MAD 5010 EEE V2.0 Drone Motor" 84.00; "MAD 5010 IPE V3.0" 88.00; "MAD 5012 IPE V3.0" 98.00; "MAD 5015 IPE V3.0 eVTOL" 108.00.
  - "MAD M6C12 EEE" 129.00; "MAD M6C12 IPE V3" 146.00; "MAD M8S C08 (8108) EEE V1" 269.00; "MAD 8118 IPE" 267.00; "MAD 8318 IPE" 198.00 (black) / 197.00 (silver).

**5010 EEE V2.0 110KV**
- Official: https://mad-motor.com/products/mad-components-5010-eee
  - "KV Option:" ¦ "110KV" ¦ "200KV" ¦ "240KV" ¦ "310KV" ¦ "370KV"; "Weight:" ¦ "162g"; "$84.00".
  - "Number of pole pairs" ¦ "14"; "Motor Size" ¦ "D:56 × 32.7 mm"; "Shaft Diameter" ¦ "IN: 5 mm"; "Support voltage:" ¦ "6S; 8S; 12S".
- BHL measurements (U, third-party; https://berkeley-humanoid-lite.gitbook.io/docs/in-depth-contents/motor-characterization):
  - "both motors are using delta winding"; line-to-line R 0.4129 Ω (1.00 V, ~2.4 A).
  - "Thus, the torque constant of the 5010 motor is 0.1176 Nm / A"; phase inductance "5010 Motor = 0.0850 mH".
  - Summary table rows: "5010 110KV" ¦ "0.6193" ¦ "0.0850" ¦ "0.1176"; "5010 140KV" ¦ "0.3939" ¦ "0.0433" ¦ "0.0913"; "5010 310KV" ¦ "0.1462" ¦ "0.0023" ¦ "0.0298".
- Robot use (V, BHL paper https://arxiv.org/html/2504.17249):
  - BOM "5010 BLDC Drone Motor" ¦ "$84" ¦ "$62"; "5010 Actuators (12x)"; driver "B-G431B-ESC1"; encoder "AS5600".
  - Reducer ratio 15:1 is *inferred* from BHL's reflected-inertia formula "× 15^2" (U/E).
- E:
  - Kt = 8.27/110 = 0.0752. BHL's measured 0.1176 is 1.56× that, a basis difference.
  - At 15 A (ASSUMED): 1.128 N·m → 8.6 / 11.5 N·m; BHL-style 15:1 at 0.9 → 15.2 N·m.
  - Copper loss at 15 A with R_ll 0.413 Ω: 0.75×225×0.413 = 70 W (burst only).
  - BHL-measured KV: 112.465 rad/s ÷ (0.5×21.6 V) = 99.4 rpm/V, against the 110 label.

**5010 200KV / 240KV / 310KV / 370KV (legacy pages)**
- URLs: http://madcomponents.co/index.php/mad5010-200kv/ (also …-240kv/, …-310kv/, …-370kv/)
- 200KV:
  - Prices: "MAD5010 200KV EEE" "$79.00"; "IPE" "$89.00".
  - Specs: "Configuration" ¦ "24N28P"; "Stator Size" ¦ "50 x 10 mm"; "Motor Dimensions" ¦ "56 x 27.9 mm"; "Continuous Power (60 mins)" ¦ "300 W"; "Maximum Power (60 secs)" ¦ "520 W"; "Maximum Current (60 secs)" ¦ "23 A"; "Internal Resistance" ¦ "176 mΩ"; "Motor Weight" ¦ "155 g".
  - IPE: "Shaft Diameter" ¦ "OD: 15 mm, ID: 13 mm"; "Peak Current (15 secs)" ¦ "22A"; "170 g".
- 310KV: "Maximum Current (60 secs)" ¦ "24 A"; "Internal Resistance" ¦ "102 mΩ". **The 240KV page is identical** (102 mΩ, 24 A), probably a copy error on MAD's side.
- 370KV: "30 A"; "66 mΩ".
- E, 200KV: 8.27/200 = 0.0414; ×23 = 0.951 → 7.3 / 9.7 N·m.
- E, 310KV: 0.0267×24 = 0.640 → 4.9 / 6.5 N·m.

**5012 160KV (legacy) and 5012 IPE V3.0 (current)**
- Legacy: http://madcomponents.co/index.php/mad5012-160kv/ — "MSRP" "$99.00"; "Stator Size" ¦ "50 x 12 mm"; "56 x 29.5 mm"; "OD: 15 mm, ID: 13 mm"; "Maximum Current (180 secs)" ¦ "14 A"; "Maximum Power (180 secs)" ¦ "400 W"; "161 mΩ"; "180 g".
- Current: https://mad-motor.com/products/mad-components-5012-ipe-v3 — "$98.00"; "D:56 × 33.3 mm"; "IN: 6 mm"; "Weight:" ¦ "189~200g"; "Support voltage:" ¦ "4S;6S".
- E: 0.0517×14 = 0.724 → 5.5 / 7.4 N·m.

**5015 320KV (legacy) and 5015 IPE V3.0 (current)**
- Legacy: http://madcomponents.co/index.php/mad5015-320kv/ — "$109.00"; "50 x 15 mm"; "56 x 32.5 mm"; "OD: 15 mm, ID: 13 mm"; "Maximum Current (60 secs)" ¦ "45 A"; "1000 W"; "Internal Resistance" ¦ "51 mΩ"; "230 g".
- The 380KV page gives "26 mΩ" and "51 A".
- Current: https://mad-motor.com/products/mad-components-5015-ipe-v3 — "$108.00"; KV options 150–420KV; "D:56 × 36.3 mm"; "220-230g".
- E: 8.27/320 = 0.0258; ×45 = 1.163 → 8.9 / 11.9 N·m.

**M6C12 150KV**
- Current: https://mad-motor.com/products/mad-components-m6c12-eee-industrial-drone-motor — "$129.00"; "257g, 255g, 256g, 268g"; "Number of pole pairs" ¦ "14"; "Motor Size" ¦ "D:72 × 33.4 mm"; "IN: 6 mm"; "150KV/12S".
- IPE V3: https://mad-motor.com/products/mad-components-m6c12-ipe-v3-waterproof-drone-brushless-motor — "$146.00"; "D:72 × 35.4 mm".
- Legacy: http://madcomponents.co/index.php/m6-code12-150kv/ — "Configuration" ¦ "24N22P" (**conflicts** with 14 pp now); "Stator Size" ¦ "64 x 12 mm"; "72 x 29.5 mm"; "Continuous Power (60 mins)" ¦ "1000 W"; "Maximum Current (60 secs)" ¦ "35 A"; "Internal Resistance" ¦ "135 mΩ"; "260 g"; "$115.00".
- BHL (U): R_ll 0.1257 Ω; "The phase resistance of the M6C12 motor is 0.1886 Ω."; "M6C12 Motor = 0.0325 mH"; "the torque constant of the M6C12 motor is 0.0919 Nm / A". Their measured KV is 154.51 rad/s ÷ 11.6 V = 127 rpm/V (E), against the 150 label.
- BHL paper (V): "The M6C12 150KV BLDC drone motor from MAD Components is used"; BOM "M6C12 BLDC Drone Motor" ¦ "$129"; "6512 Actuators (10x)"; stiffness "approximately 319.49 Nm / rad"; gearbox "approximately 90% across most operating conditions".
- E: 0.0551×35 = 1.93 N·m → 14.8 / 19.7 N·m; 15:1 at 0.9 → 26.1 N·m. Copper loss 0.75×35²×0.135 = 124 W.

**8108 100KV/170KV (legacy) and M8S C08 (8108) EEE (current)**
- Legacy: http://madcomponents.co/index.php/mad8108-100kv/
  - "MAD8108 100KV EEE" "$208.00"; "Configuration" ¦ "36N42P"; "Stator Size" ¦ "81 x 8 mm"; "86.8 x 27.5 mm"; "Shaft Diameter" ¦ "OD: 15 mm, ID: 13 mm".
  - "Maximum Current (60 secs)" ¦ "24 A"; "750 W"; "Internal Resistance" ¦ "186 mΩ"; "Motor Weight" ¦ "250 g".
  - The 170KV page gives "89 mΩ", "35 A".
- Current: https://mad-motor.com/products/m8s-c08-eee-brushless-drone-motor — "$269.00"; "Weight:" ¦ "283g" but the body text says "Lightweight at 252g" (conflict on the same page); "21" pp; "D:87.3 × 26.75 mm"; "IN: 12 mm".
- E: 0.0827×24 = 1.985 → 15.2 / 20.2 N·m.

**8118 80KV (legacy)**
- URL: http://madcomponents.co/index.php/mad8118-80kv/
- "$249.00"; "Configuration" ¦ "36N40P"; "Stator Size" ¦ "81 x 18 mm"; "88.6 x 38 mm"; "Shaft Diameter" ¦ "10 mm"; "Maximum Current (180 secs)" ¦ "33 A"; "1500 W"; "93 mΩ"; "500 g".
- E: 8.27/80 = 0.1034; ×33 = 3.41 → 26.1 / 34.8 N·m.

**8318 IPE 100KV**
- Official: https://mad-motor.com/products/mad-components-8318-ipe-for-agriculture-drone-motor — "$198.00"; "Number of pole pairs" ¦ "21"; "Motor Size" ¦ "D:91.5 × 41 mm"; "Shaft Diameter" ¦ "IN: 15 mm"; "Bearing" ¦ "6802ZZ*2". The silver version page shows "$197.00".
- Reseller (U, https://rcdrone.top/products/mad-8318-ipe-kv100-kv120-brushless-motor, price 260.84):
  - "Configuration: 36N42P"; "Internal resistance" ¦ "36mΩ"; "Motor Weight" ¦ "660 g" (also "Motor Weight: 639g"); "Maximum Current" ¦ "68 A"; "Maximum Power" ¦ "3224W"; "D:91.5 × 38 mm".
  - KV120: "29mΩ", "80 A".
- E: 0.0827×68 = 5.62 → 43.0 / 57.4 N·m.

#### Eaglepower (all electrical data U)

The official site http://en.rc-eaglepower.com/products/ shows specs only as images. It lists "UA80 … 8108" but no LA8308/EA95 text. No "EA90" model was found.

**LA8308 KV90**
- Technobotix (India): https://www.technobotix.in/products/eagle-powor-la-8308-kv90-motor/1781252000000073016 — "₹10,999.00"; "maximum continuous current of 22A and a peak power output of 900W"; "internal resistance of 0.186 ohms"; "Measuring 92×28.5 mm and weighing 336 grams".
- The same site's blog gives different figures: "Max Current" ¦ "~40-45A"; "Motor Weight" ¦ "~325 g"; "Shaft Diameter" ¦ "6 mm".
- Other India leads (U): TNT e-Comp / Thansiv JSON price 10260.0 (https://www.tntecomp.com/products/eaglepower-la-8308-kv90-motor); The Engineer Store 11738.12, available=false (https://www.theengineerstore.in/products/eaglepower-la-8308-kv90-motor).
- Robot use (V, https://www.aaedmusa.com/projects/openqdd): "90KV Eagle Power BLDC Motor"; "9:1 Planetary Gear Set with Helical Gears"; "Peak Holding Torque: 16.36 Nm"; "Total Mass: 935g"; "Total Cost: $247". The motor size is not named on the page, so "8308" is an inference (U).
- E:
  - 8.27/90 = 0.0919; ×22 = 2.02 → 15.5 / 20.6 N·m.
  - OpenQDD cross-check: 16.36/(9×0.85) = 2.14 N·m of motor torque → ≈23 A at Kt 0.0919. That is consistent.
  - The 0.186 Ω value is identical to MAD 8108 100KV's 186 mΩ, a possible copy.

**EA95 8318 KV100**
- ArrisHobby (U): https://www.arrishobby.com/products/eaglepower-ea95-8318-100kv-8-14s-brushless-motor-for-uav-drones-agriculture-drones-1066 — "$99.00"; "Motor Size(mm): Φ92x40"; "Weight:695g"; "No-load Current:1.7A"; "Battery Cells:8-14S Lipo"; "Max Continuous Cureent：58A"; "Max Continuous Power:2900"; "Internal Resistance:0.055Ω".
- E: 0.0827×58 = 4.80 → 36.7 / 48.9; 20:1 → 81.5 N·m. Copper loss 0.75×58²×0.055 = 139 W.

#### iFlight (official shop shop.iflight.com; V)

**GM4108H-120T gimbal**
- URL: https://shop.iflight.com/ipower-motor-gm4108h-120t-brushless-gimbal-motor-pro217
- Price and geometry: "$35.90"; "Motor Out Diameter: Ф47±0.05mm"; "Configuration: 24N/22P"; "Motor Height: 22.7±0.2mm".
- Hollow shaft: "Hollow Shaft(OD): Ф10-0.008/-0.012mm"; "Hollow Shaft(ID): 8+0.05/0mm"; "Motor Weight: 124±0.5g".
- Test data: "No-load volts: 20V"; "No-load Rpm: 513~567 RPM"; "Load current: 1.5A"; "Load torque(g·cm): 1200-1800".
- "Motor internal resistance: 11.1Ω±5%"; "Maximum power: ≤25W"; "Working current: 3-5S" (sic).
- Conflict: a third-party doc says height 32.3 mm (U).
- E:
  - KV ≈ 513/20 to 567/20 = 25.7–28.4 rpm/V; Kt from KV ≈ 0.306.
  - The published load torque is 1200–1800 g·cm = 0.118–0.177 N·m at 1.5 A, i.e., 0.078–0.118 N·m/A. The KV-based Kt overstates it, so trust the published torque.
  - Output with 0.177 N·m: 1.35 / 1.80 N·m.

**GM5208-12 / GM5208-24 gimbal**
- URLs: https://shop.iflight.com/ipower-motor-gm5208-12-brushless-gimbal-motor-pro279 and …-gm5208-24-…-pro1347
- -12: "$39.90"; "Ф63±0.05mm"; "12N/14P"; "Hollow Shaft(OD): Ф15"; "(ID): Ф12"; "195±0.5g"; "No-load Rpm: 456~504 RPM" at "20V"; "Load torque(g·cm): 1800-2500" at 1 A; "15.2Ω±5%"; "≤40W".
- -24: "$42.99"; "Ф59.5±0.05mm"; "24N/22P"; ID "Ф12.6"; "204±0.5g"; "396~436 RPM"; "13.7Ω±5%".
- E: 1800–2500 g·cm = 0.177–0.245 N·m; outputs 0.245×9×0.85 = 1.87 and ×12 → 2.50 N·m.

**XING 8108 87KV**
- URL: https://shop.iflight.com/xing-8108-87kv-multi-rotor-brushless-motor-pro1161
- "$239.00"; "KV:87"; "Configu-ration: 36N42P"; "Stator Diamter:81mm"; "Stator Length:08mm"; "Shaft Diameter:15mm"; "Φ87.2*25mm"; "Weight(g): 260".
- Ratings: "No.of Cells(Lipo): 6~12S"; "Max Continuous Power(W)180S: 1050"; "Internal Resistance: 0.22Ω"; "Max Current(180S): 21.7A".
- E: 8.27/87 = 0.0951; ×21.7 = 2.06 → 15.8 / 21.0 N·m.

**eX8108 105KV**
- URL: https://shop.iflight.com/ex8108-105kv-brushless-motor-pro959
- "$99.99" (Sold Out); "KV: 105RPM/V"; "Max watts: 750W/180S"; "Max Amps: 24A/180S"; "Resistance: 186MΩ" (sic); "Φ87x24.50mm"; "Weight: 228.6g"; "6-12S".
- Ben Katz characterized an "EX-8 105 Kv (T-Motor U-8 clone)" (V, his page, see U8 note).
- E: 8.27/105 = 0.0788; ×24 = 1.89 → 14.5 / 19.3 N·m.

#### Tarot

**5008 340KV (TL96020)**
- Official, V: http://www.tarotrc.com/Product/Detail.aspx?Lang=en&Id=a7511719-2bad-4be0-aa8d-8cef61c38509
- Listing: "Price：" ¦ "235 RMB"; "Date：" ¦ "2013-08-03".
- Specs: "Stator Diameter: 50.0mm"; "Stator thickness: 8.0mm"; "Slot number: 12N"; "Pole number: 14P"; "Outer diameter of gear shaft: 4.0mm"; "Length of motor: 38.5mm"; "Diameter of stator: 58.50mm" (evidently the outer diameter); "Motor weight: 168G"; "Max Power:700W"; "Max current: 40A".
- India lead (search result title): Robokits "Tarot TL96020 5008 340KV … ₹3,378.00" (https://robokits.co.in/multirotor-spare-parts/brushless-motor-propeller-esc/brushless-motor/tarot-tl96020-5008-340kv-high-power-brushless-motor).
- E: 0.0243×40 = 0.973 → 7.4 / 9.9 N·m.

**4108 380KV (TL68P07)**
- The official page http://www.tarotrc.com/Product/Detail.aspx?Lang=en&Id=29c43b2f-b8c9-415e-a1ed-deb668749166 now renders empty.
- ArrisHobby (U, https://www.arrishobby.com/products/tarot-4108-380kv-6s-brushless-motor-for-rc-drones-tl68p07): "$29.99"; "Motor diameter: 46MM"; "stator dia:40.6MM"; "Stator thickness: 8MM"; "stator terminal:24"; "Motor pole: 22P"; "Gear install diameter: ￠4MM"; "Motor height: :24.0MM"; "Net weight : 93G"; "Impedence:135 mΩ".
- India lead (search result): https://indianrobostore.com/product/tarot-tl68p07-6s-380kv-4108-brushless-motor-for-multi-rotor
- This is not a gimbal motor. I did not find a Tarot 4108 gimbal motor.
- Also V, Tarot 6008 285KV TL60P08 (http://www.tarotrc.com/Product/Detail.aspx?Lang=en&Id=6817ae5f-893a-4c56-a9fe-10fe7c9eecbb): "18N"; "24P"; "Φ68 × 29.8mm"; "Weight: 177g"; "Maximum continuous current (A): 29.37"; "Internal resistance: 86mΩ"; "365 RMB". E: 8.27/285 = 0.0290 × 29.37 = 0.85 N·m → 6.5 / 8.7 N·m.

#### Flipsky (official store flipsky.net, Shopify JSON; V)

| Product (URL) | Price | Verbatim snippets | E |
|---|---|---|---|
| 6374 190KV 3250 W (https://flipsky.net/products/bldc-belt-motor-6374-190kv-3250w-for-electric-skateboard) | without pulley 99.0 | "Max Current: 85A"; "Max Volts: 12S"; "Motor Resistance: 0.05Ohm"; "Weight: 1.9 lb / 0.86 kg"; "The motor length:74mm"; "The motor diameter: 63mm"; "SHAFT: Diameter 8mm, 32mm length"; "The number of pole: 14"; "Internal PCB with 120 Degree Hall Effect Sensors." | 8.27/190 = 0.0435 × 85 = 3.70 → 28.3 / 37.7 N·m |
| 6374 Battle Hardened (https://flipsky.net/products/flipsky-bldc-belt-motor-battle-hardened-6374-140kv-170kv-190kv-3500w-f) | 8mm / 140KV / Without Pulley = 87.0 | "Voltage range: 3-12S"; "Max Current: 85A"; "Motor Resistance: 0.050hm" (sic); "Weight：0.98kg" | 140KV: 0.0591 × 85 = 5.02 → 38.4 / 51.2 N·m |
| 6354 Battle Hardened (https://flipsky.net/products/flipsky-bldc-belt-motor-battle-hardened-6354-140kv-190kv-2450w-for-ele) | 71.0 | "Voltage range: 4-14S"; "Max Current: 65A"; "Motor Resistance: 0.053Ohm"; "The motor length:54mm" | 0.0591 × 65 = 3.84 → 29.4 / 39.2 N·m |
| 6384 Battle Hardened (https://flipsky.net/products/flipsky-bldc-belt-motor-battle-hardened-6384-140kv-170kv-190kv-4000w-f) | 140KV without pulley 113.0 (with pulley 119.0) | "Max Current: 95A"; "Weight：1.3kg"; "The motor length:84mm" | 0.0591 × 95 = 5.61 → 42.9 / 57.2 N·m |
| 5065 200KV (https://flipsky.net/products/flipsky-sensored-outrunner-brushless-dc-motor-battle-hardened-5065-200) | 56.8 | "Max Current: 38A；Rated Current: 21A"; "Number of slots & poles: 12N/14P"; "Diameter *Length (mm): 49*63.5"; "Weight：0.475kg" | 0.0414 × 38 = 1.57 → 12.0 / 16.0 N·m |

None of the Flipsky "Max Current" figures has a stated duration. At 85 A and 0.05 Ω, copper loss is 0.75×85²×0.05 = 271 W, so these are clearly short-burst figures.

#### Maytech (official store maytech.cn; V)

**MTO6374-170-HA-C**
- URL: https://maytech.cn/products/brushless-hall-sensor-motor-mto6374-170-ha-c (JSON)
- Price: variant "170KV" = 82.4; "Customized KV 110KV" = 94.5.
- Snippets: "Idle Current" ¦ "0.8A"; "Max Current" ¦ "65A"; "Inpur Voltage" ¦ "3-12s Lipo (12-50V)"; "Rated Current" ¦ "60A"; "Max Output Watt" ¦ "3550W"; "Shaft Dia" ¦ "8mm"; "Output Shaft Length" ¦ "26mm".
- KV tolerance: "each motor might has ±5%-10% tolerance".
- Mass and resistance are not in the text.
- E: 8.27/170 = 0.0486 × 65 = 3.16 → 24.2 / 32.3 N·m.
- Sensorless MTO6374 170/200/330KV is 86.80 (https://maytech.cn/products/brushless-sensorless-motor-mto6374-190-g).

#### ODrive Robotics (docs + shop; V)

- Docs: https://docs.odriverobotics.com/v/latest/hardware/odrive-motors.html. Footnotes: "All voltage units are line-line amplitude" and "All current units are phase amplitude".
- M8325s 100KV:
  - Docs: "Torque Constant" ¦ "0.083" ¦ "Nm/A"; "Pole Pairs" ¦ "20"; "Phase Resistance" ¦ "24" ¦ "mΩ" ¦ "Phase-neutral"; "Phase Inductance" ¦ "9.9"; "Continuous Current" ¦ "40" ¦ "60" ("Free Air" ¦ "Forced Air"); "Peak Current" ¦ "80" ¦ "3-second".
  - Shop https://shop.odriverobotics.com/products/m8325s: price 149.00; "KV: 100, Diameter: 92mm, Weight: 840g"; "Mounting plane to top plane: 46.5mm"; "the included shaft magnet allows for easy integration with any magnetic encoder".
- D6374 150KV:
  - Docs: "0.055" Nm/A; "Phase Resistance" ¦ "39"; "Phase Inductance" ¦ "24"; continuous "50" ¦ "70"; "Peak Current" ¦ "90".
  - Shop https://shop.odriverobotics.com/products/odrive-custom-motor-d6374-150kv: 119.00; "10mm primary shaft with flat and keyseat"; "8mm secondary shaft, for possible use with" "CUI AMT-212 encoder"; "7 pole pairs and 12 stator slots (12n14p)".
- D5065 270KV:
  - Docs: "0.031"; "39" mΩ; "16" µH; continuous "45" ¦ "65"; peak "85".
  - Shop: 89.00; "8mm primary shaft with flat"; "8mm secondary shaft".
- E:
  - M8325s: 0.083×80 = 6.64 → 50.8 / 67.7 N·m; 16:1 → 90.3 N·m. Continuous: 0.083×40 = 3.32 → 25.4 / 33.9 N·m.
  - M8325s copper loss (phase-neutral): 1.5×40²×0.024 = 57.6 W continuous in free air; 1.5×80²×0.024 = 230 W for 3 s.
  - D6374: 0.055×90 = 4.95 → 37.9 / 50.5 N·m. D5065: 0.031×85 = 2.64 → 20.2 / 26.9 N·m.
  - ODrive-published Kt matches 8.27/KV within about 1%.

#### Rctimer 5010-14 360KV (the common "5010 360KV")

- Official Rctimer store, V: https://rctimer.com/rctimer-5010-360kv-multicopter-brushless-motor-p0233.html
- "$12.99" (struck "$18.18"); "MOQ: 500"; "KV: 360"; "Configu-ration: 12N14P"; "Shaft Diameter(out size): 4mm"; "Shaft Diameter(inside size): 5mm"; "Motor Dimension(Dia.*Len): Φ50х26"; "Weight(g): 92g".
- No resistance or current rating is published.
- India lead (search result only, page is behind Cloudflare): https://robu.in/product/5010-360kv-high-torque-brushless-motors-multicopter-quadcopter-multi-axis-aircraft/
- E: 8.27/360 = 0.0230; at 20 A (ASSUMED) → 0.46 N·m → 3.5 / 4.7 N·m.

#### Other India leads read today (not deep-checked)

- Robokits "Robot Joint Brushless Motors" (https://robokits.co.in/motors/robot-joint-brushless-motors) sells T-Motor CubeMars joint motors. These are out of hobby scope:
  - "RI50 KV100" ₹8,245.00; "RI60 KV120" ₹12,208.00; "RI70 KV95" ₹14,885.00; "RI80 KV75" ₹19,327.00; "RI100 KV105" ₹15,539.00; "R100 KV90" ₹44,834.00.

---

### 3. Guidance by torque class (all ESTIMATED unless marked)

**Assumptions:**
- T_out = Kt × I × N × 0.85.
- No-load output speed ω_nl = KV × V_bus × 2π/60 ÷ N. Loaded top speed is lower.
- Copper loss P ≈ 0.75·I²·R (R assumed line-to-line), or 1.5·I²·R_ph for ODrive.
- Checks that support the method:
  - ODRI measured 2.5 N·m at 12 A with 9:1; the estimate gives 2.53 N·m.
  - OpenQDD's 16.36 N·m at 9:1 implies ≈23 A on an 8308 90KV, close to its 22 A spec.

#### A. Small joints, 3–15 N·m

| Pick | Why | Arithmetic |
|---|---|---|
| **MAD 5010 EEE 110KV + 12–15:1** (US$84, 162 g) | Proven in BHL (12 actuators per robot, 15:1 printed cycloid). Low KV means high Kt. | 0.0752 × 15 A (assumed) = 1.13 N·m → 12:1: 11.5 N·m; 15:1: 14.4 N·m. Speed at 24 V: 12:1 → 23.0 rad/s, 15:1 → 18.4 rad/s (48 V doubles these). |
| **T-Motor MN6007 II KV160 + 9–12:1** (US$129.99, 159 g) | Official 180 s rating of 23.7 A. Lots of speed headroom. | 0.0517 × 23.7 = 1.225 N·m → 9:1: 9.4; 12:1: 12.5; 15:1: 15.6 N·m. Speed at 24 V: 12:1 → 33.5 rad/s. |
| Budget: T-Motor MN5008 KV170 (US$89.99, 128 g; Robokits sells the 340/400KV variants) | Verified specs and available in India. | 0.0486 × 15 = 0.73 N·m → 12:1: 7.4; 20:1: 12.4 N·m. |

Avoid for the legs:
- Gimbal motors (GB4106, GB54-2, GM4108H, GM5208) give only 0.2–0.45 N·m published, i.e., 1.5–4.6 N·m at 9–12:1. They are limited to 25–40 W. Keep them for head, neck or wrist.
- 5010 360KV-type motors have low Kt (0.023). At an assumed 20 A you would need about 20:1 for 7.8 N·m.

#### B. Medium joints, 15–40 N·m

| Pick | Why | Arithmetic |
|---|---|---|
| **SunnySky V8110 KV100 + 9–12:1** (US$185.99, 337 g) | Best verified torque/mass in class (11.0 N·m/kg). | 0.0827 × 45 A (30 s) = 3.72 N·m → 9:1: 28.5; 12:1: 38.0 N·m. Speed: 24 V → 27.9 / 20.9 rad/s; 48 V → 55.9 / 41.9 rad/s. |
| **Eaglepower LA8308 KV90 + 9–15:1** (₹10,260–10,999 in India; specs U) | Cheapest locally available; used by OpenQDD. | 0.0919 × 22 A = 2.02 N·m → 9:1: 15.5; 12:1: 20.6; 15:1: 25.8 N·m. OpenQDD measured 16.36 N·m at 9:1 (V). 24 V, 12:1 → 18.8 rad/s. |
| **MAD M6C12 150KV + 12–15:1** (US$129) | BHL 6512 actuator. | 0.0551 × 35 A (60 s) = 1.93 N·m → 12:1: 19.7; 15:1: 24.6 N·m (26.1 at BHL's ~90%). 24 V, 15:1 → 25.1 rad/s. |
| Alt: ODrive D6374 150KV + 9:1 (US$119, Kt V) | Official Kt and current ratings; e-skate motors are heavy (Flipsky 6374: 0.86–0.98 kg). | 0.055 × 90 A (3 s) = 4.95 N·m → 37.9 N·m; continuous 50 A → 21.0 N·m. |

#### C. Large joints, 40–90 N·m

| Pick | Why | Arithmetic |
|---|---|---|
| **ODrive M8325s 100KV + 12–16:1** (US$149, 840 g, encoder magnet included) | The only large motor with official Kt, continuous and peak ratings. | 0.083 × 80 A (3 s) = 6.64 N·m → 12:1: 67.7; 16:1: 90.3 N·m. Continuous 40 A → 12:1: 33.9; 16:1: 45.2 N·m. |
| **SunnySky X8318S KV100 + 12–20:1** (US$159.99, 635–645 g) | Verified 8318 specs from two official sources; 15 mm shaft (hollow not stated). | 0.0827 × 59 A (30 s) = 4.88 N·m → 12:1: 49.8; 16:1: 66.4; 20:1: 82.9 N·m. |
| Lowest cost: **Eaglepower EA95 8318 KV100** (≈US$99 reseller; specs U) | Cheapest 8318 found. | 0.0827 × 58 A = 4.80 N·m → 12:1: 48.9; 20:1: 81.5 N·m. |
| Lightest: T-Motor MN8014 KV100 (392 g, US$279.90) | Highest torque density in class. | 0.0827 × 52 = 4.30 N·m → 12:1: 43.9; 20:1: 73.1 N·m. |

**Reaching 90 N·m** with Kt ≈ 0.083 needs I = 90/(0.083 × N × 0.85):
- 12:1 needs ≈106 A, which is beyond every published rating.
- 16:1 needs ≈80 A (M8325s 3-s peak).
- 20:1 needs ≈64 A. The X8318S KV100 maker rating of 59 A/30 s gives 82.9 N·m.
- X8318S **KV120** at its maker rating of 80 A/30 s: 8.27/120 = 0.0689 × 80 × 20 × 0.85 = 93.7 N·m. No-load speed at 48 V, 20:1 = 30.2 rad/s.
- So: use 16–20:1 for 90 N·m, or accept about 50–68 N·m peak at 12:1.

**Speed check (8318/8325 at KV100):**
- No-load: 24 V gives 20.9 rad/s at 12:1 and 12.6 rad/s at 20:1. 48 V gives 41.9 rad/s at 12:1 and 25.1 rad/s at 20:1.
- For 8–20 rad/s legs at 16–20:1, plan a **12S (48 V) bus**, or pick KV120.

#### Thermal caveats (ESTIMATED unless marked)

1. **Drone ratings are not robot ratings.**
   - The 180 s / 60 s / 30 s figures assume propeller airflow.
   - ODrive's own ratings (V) show how much cooling matters: M8325s is 40 A continuous in free air vs 60 A forced air, with an 80 A peak for 3 s.
   - Implied free-air copper loss: 1.5×40²×0.024 = 57.6 W. Plan about 30–60 W continuous per 80-mm-class motor in an enclosed printed housing.
   - Continuous current (R assumed line-to-line):
     - X8318S: √(30…60 / (0.75×0.049)) = 28.6–40.4 A → 12:1 continuous 24.1–34.1 N·m.
     - LA8308: 14.7–20.7 A.
     - M6C12: 17.2–24.3 A.
     - MAD 5010 110KV: 9.8–13.9 A → about 7.5–10.6 N·m at 12:1.
   - These drive the *continuous* stance torque; the peak figures above are bursts only.
2. **Burst overcurrent is common but must be duty-limited.** ODRI runs 12 A on a 4004 that T-Motor rates at 9 A (180 s). Watch magnet temperature limits:
   - T-Motor: "Magnet Level" 150–180 ℃.
   - MAD: "Magnet Degree" 150°C.
3. **Printed gearboxes near hot motors.** BHL (V) states an "insufficient study of thermal effects on the 3D-printed structure". Isolate the motor with an aluminium mount or heat spreader.
4. **Resistance convention is unknown for most drone motors.** If R is per-phase rather than line-to-line, every copper-loss number above doubles and the continuous currents drop by 1/√2.
5. **Encoders.**
   - Hollow or through-bore options: legacy MAD IPE 5010/5012/5015/8108 ("OD: 15 mm, ID: 13 mm"), iFlight GM4108H (OD 10 / ID 8) and GM5208 (OD 15 / ID 12), T-Motor GB gimbals (holes of 5.6 and 12.7 mm).
   - The ODrive M8325s ships with an encoder magnet; the D5065/D6374 have 8 mm rear shafts for AMT encoders.
   - Antigravity/Navigator "IN" shafts are internal, so a magnet adapter is needed. BHL uses an AS5600 on-axis encoder.

---

### 4. Gaps and open items

- **Search budget:** the web-search budget ran out late in the pass. These were not checked:
  - iPower GBM6208 and any 6012/6208 gimbal motors.
  - The MIT Mini Cheetah motor identity; I found no primary source for an "MIT 8318".
  - Amazon.in and ThinkRobotics stock.
  - Robu.in pages, which are behind Cloudflare.
- **Mini Cheetah lineage (U, inference only):** Ben Katz's pages show he used "T-Motor U8's and U8 knock-offs" (V) and characterized an EX-8 105 Kv. Clone actuators are sold as "GIM8108" per an AliExpress title seen in search (U). Neither establishes an "MIT 8318".
- **Not published or not found in text:**
  - MAD current V2/V3 KV-specific R and current (images only); 5010 110KV max current.
  - ODrive D5065/D6374 mass.
  - Maytech 6374 mass and R.
  - Flipsky 6354 mass; durations for all Flipsky max currents.
  - Tarot 5008 R.
  - Eaglepower official electrical specs (images only). No "EA90" found.
  - Inductance for almost all motors (only ODrive and BHL give it).
- **Conflicts to resolve by measurement:**
  - SunnySky maker vs USA store (X5212S 28 vs 67 mΩ and 24N28P vs 24N22P; X6212S 73 vs 102 mΩ; X8318S 49 vs 54 mΩ).
  - MAD M6C12 legacy "24N22P" vs V3 "14" pole pairs.
  - MAD legacy 5010 240KV and 310KV pages are identical.
  - MAD M8S C08: 283 g vs 252 g on the same page.
  - MAD 8318: official 41 mm length vs reseller 38 mm, and 639 vs 660 g.
  - iFlight GM4108H height: 22.7 mm official vs 32.3 mm third-party.
  - Eaglepower LA8308: 22 A / 336 g vs ~40–45 A / ~325 g on the same Indian site.
  - T-Motor MN4004 "Shaft Diameter 40mm" (typo).
  - The GM4108H KV-derived Kt disagrees with its published load torque.
- **Label caveats:**
  - BHL Kt and R values are measurements on a delta basis (U) and are not comparable with 8.27/KV.
  - The BHL 15:1 ratio is inferred from its inertia formula.
  - The 8308 size of the OpenQDD motor is inferred.
- **Prices:** Tarot prices are old RMB listings (2013 and 2016). INR→USD was not converted. Official prices are 2026-09-24 snapshots and exclude shipping and import duty to India.
- **Recommended next step:** bench-measure R_ll, Kt (back-EMF) and thermal rise inside the printed housing for the 2–3 shortlisted motors. Candidates: MAD 5010 110KV or MN6007 II; V8110 or LA8308; X8318S or M8325s.

## 5. Motor drivers with CAN for DIY joints


Scope: compact FOC drivers for DIY joints (hobby BLDC plus reducer) on a 24–48 V bus, ~20–40 A phase current per leg joint, CAN to the host.

**Legend.** [V] VERIFIED = read today (2026-09-24) on the official or primary page (manufacturer site, official shop, official docs or official GitHub). [U] UNVERIFIED = reseller, forum, secondary source or search-result snippet. [E] ESTIMATED = derived value, with the arithmetic shown. n/f = not found. "Cont." = continuous phase current. Prices are for reference only.

**FX used for [E] conversions.** 1 USD = 0.87635 EUR = 0.75322 GBP = 6.7074 CNY = 95.74 INR. Source: ECB reference rates via https://api.frankfurter.app/latest?from=USD&to=EUR,GBP,CNY,INR, dated 2026-09-23. The snippet is `"rates":{"CNY":6.7074,"EUR":0.87635,"GBP":0.75322,"INR":95.74}`.

---

### 1. Master table

| Driver | Cont. A | Peak A | V range | MCU | CAN type | Other I/F | Encoder (onboard / ext / dual?) | Size mm | Mass g | Control modes | Open-source (HW/FW license) | Official price USD (date) | Availability | India leads | Label(s) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **ST B-G431B-ESC1** | Not rated by ST [n/f] | 40, tested with propeller forced-air cooling [V] | 3S–6S LiPo [V]. ≈11.1–25.2 V [E]. Digikey: 11.1–22.2 VDC [U] | STM32G431CB, Cortex-M4 170 MHz [V] | STM32 FDCAN plus onboard TI TCAN330 transceiver [V], rated ≤1 Mbps [V TI]. 120 Ω termination switchable in FW [V] | UART, PWM in, SWD, USB via detachable ST-LINK, pot, button, 5 V BEC [V] | None onboard. J8 Hall/encoder pads with 5 V [V]. Dual not in stock FW [U] | 30×41 [V] | 9.2 [V] | ST MCSDK: sensorless or sensored FOC, 6-step [V] | ST reference design, schematics published (not OSHW); MCSDK under ST license [U] | **$39.26** ST eStore (2026-09-24) [V] | In stock [V] | Evelta ₹2,365 ex-GST (≈$24.70 [E]) / ₹2,790.70 incl., ships from Mumbai [U] | V/U/E |
| **Berkeley "Recoil" = B-G431B-ESC1 + Recoil FW** (Berkeley Humanoid Lite) | As ESC1 (not rated) | 40 (ESC1) [V] | BHL runs a 6S LiPo [V paper] | STM32G431CB [V] | FDCAN set to 1 Mbps nominal (classic frames), CANopen-style NMT/SDO [V code]. BHL: "1 Mbps CAN 2.0" [V] | As ESC1 | AS5600 over I2C (BHL BOM $3.30) [V] | 30×41 | 9.2 | current / torque / velocity / position; PD position loop with position_kp, velocity_kp, torque limit [V] | FW MIT [V]; HW = ST ESC1 | Board $39.26 [V]. BHL BOM (older): $18.97 Digikey / ¥165 Taobao [U]. Paper: $19 US / $23 CN [V] | ST in stock [V] | As ESC1 | V/U |
| **ODrive S1** | 20 free-air / 40 with heat-spreader plate [V] | 40–80, depends on bus voltage [V] | 12–50.5 V (typ. 16–48) [V] | STM32H7 family (docs flash with stm32h7x.cfg) [V]; exact part n/f | CAN 2.0B @ 1 Mbps [V]. CAN-FD since FW 0.6.10 (shop still says "experimental") [V]. HW max 8 Mbit/s [V] | USB, isolated UART, isolated STEP/DIR, analog, PWM, GPIO, brake-resistor output, thermistor [V] | MA702 onboard [V]. Ext: quadrature, Hall, SPI, RS485 (RS485 and SPI mutually exclusive) [V]. Dual absolute ✓ [V] | 66×50 [V] | 35 (55 with screw terminals) [V] | pos/vel/torque. Set_Input_Pos carries Vel_FF and Torque_FF; gains via Set_Pos_Gain / Set_Vel_Gains [V] | Closed FW ("not publicly available") [V]. HW not published [U] | **$149** qty 1 ($143 @ 100) [V]. Heat-spreader plate +$12 [V] | US shop in stock. WW shop: screw-terminal in stock, solder-pad OOS [V] | ThinkRobotics product search: no hit [U] | V/U |
| **ODrive Pro** | 20 free-air / 80 active cooling (datasheet) [V]. Shop and comparison table say 70 [V, conflicting] | 100 for 3 s max (datasheet/shop) vs 120 (comparison) [V, conflicting] | 15–58 V [V] | STM32H7 family [V] | CAN 2.0B 1 Mbps plus CAN-FD. Isolated CAN. HW max 12 Mbit/s [V] | USB, isolated UART / STEP-DIR / PWM, analog, fan output. No brake-resistor driver [V] | MA702 onboard. Ext: quad, Hall, SPI, SSI, RS485; BiSS-C experimental. Dual ✓ [V] | 51×64×17.5 [V] | 32 bare / 72 with spreader / 140 full case [V] (shop lists 35/55, likely a copy error) | As S1 [V] | Closed [V] | **$229** ($209 @ 100) [V] | In stock [V] | None found | V |
| **ODrive Micro** | 3.5 [V] | 7 [V] | 10–31 V (typ. 12–24; comparison table: 28 V recommended max) [V] | STM32H725RGV6 [V schematic] | CAN 2.0B 1 Mbps plus CAN-FD (comparison ✓; shop says "coming soon"). MCP2542FD transceiver; HW max 8 Mbit/s [V] | Control over CAN only (USB for config) [V] | MA702GQ onboard. Ext: quad, Hall, SPI (no MOSI). Multiple-encoder feedback ✓ [V] | 32×32×7 [V] | 6.8 bare [V] | As S1 | Closed FW; schematic PDF published [V] | **$89** ($79 @ 100) [V] | In stock [V] | None | V |
| **ODrive v3.6 (NRND)** 2-axis | 40 nominal (comparison table) [V]; shop: "depends on cooling" | 120 per motor [V] | 12–56 V (56 V version) [V] | STM32F405 [V FW] | Classic CAN (CANSimple) [V/U] | USB, UART, PWM, STEP/DIR, analog, GPIO [V] | No onboard encoder. Ext ABI, Hall, SPI absolute. No multi-encoder [V] | 135×50 [V] | 80 [V] | position / velocity / current [V] | FW MIT (repo frozen); HW MIT (ODriveHardware) [V] | $259 per 2-axis board = **$129.50/axis** [V/E] | 56 V without connectors in stock; with connectors sold out [V] | None | V/E |
| **Flipsky ODESC V4.2** (ODrive-3.6 derivative) | 70 (vendor claim) [V-claim] | 120 (vendor claim) [V-claim] | 8–24 V (24 V version) / 8–56 V (56 V version) [V] | STM32F405RGT6 [V] | Classic CAN, ODrive 0.5.x-compatible [U] | USB, PWM, UART, CAN, analog, step/dir, GPIO [U] | None onboard. Ext ABI, SPI absolute, Hall, AMT102/103, TLE5012, AS5047P [U] | 63×58×30 [U] | 70 [U] | speed / position / current / torque / trajectory [U] | Based on open ODrive 3.6 (MIT upstream); vendor changes unverified [U] | **$34.99 (24 V) / $43.99 (56 V)** incl. heat sink [V] | Available [V] | Technobotix ₹7,799; page shows OUT OF STOCK [U] | V/U |
| **Flipsky ODESC 3.6** single / dual | 50 [V] | 120 [V] | Single page text: 8–24 V; dual: 8–56 V [V] | STM32F405 (ODrive 3.6 base) [U] | Classic CAN listed [V] | USB, UART, PWM, STEP/DIR, GPIO, CAN, analog [V] | Ext: incremental, absolute, Hall, AMT102/103, TLE5012, AS5047 [V] | n/f | n/f | speed / torque / current / position / trajectory [V] | ODrive-based [U] | Single $69 (24 V) / $85 (56 V). Dual 56 V $59.99 (= $30/axis [E]) [V] | Available [V] | None | V/U/E |
| **Makerbase MKS XDrive Mini** (ODrive-3.6 clone) | 60 (reseller claim) [U] | 120 [U] | 12–56 V [U] | STM32F405RGT6 [U] | Classic CAN via SN65HVD230, with a known RS-pin resistor flaw; guide uses 500 kbps [U] | USB, UART, PWM, CAN, step/dir [U] | AS5047P onboard [V product title] | n/f | n/f | ODrive FW v0.5.1: pos/vel/torque [U] | ODrive-derived; ships modified 0.5.1 FW [U] | **$40.99** (list $42.99) or $42.69 variant, makerbase3d.com [V brand store]. XDrive-S $49.65, XDrive $69, MKS ODrive3.6 $89.99 [V] | In stock [V] | None found | V/U |
| **mjbots moteus r4.11** | 12 uncooled / 32 with thermal management [V] | 100 [V] | 10–44 V (≤10S) [V] | STM32G4 170 MHz [V] | CAN-FD 5 Mbps; requires 1/5 Mbps FD timing. 2× JST PH-3 daisy-chain [V] | AUX1/ENC and AUX2/ABS: SPI, I2C, ADC/sin-cos, quadrature, Hall [V] | AS5047P onboard [V]. Ext SPI (AS5047, MA600, MA732, AksIM-2), I2C AS5600, quad, sin/cos, Hall. Dual ✓ [V] | 46×53 [V] | 14.2 [V] | position/velocity/torque; per-command kp/kd scale and FF torque (MIT-like) [V] | HW + FW Apache-2.0 [V] | **$94** (+$29 heat spreader) [V] | Available [V] | None found | V |
| **moteus c1** | 5 / 14 [V] | 20 [V] | 10–51 V (≤12S) [V] | STM32G4 [V] | CAN-FD 5 Mbps [V] | AUX2 (GH7): SPI, UART, GPIO, ADC, quadrature, Hall, I2C [V] | Onboard absolute magnetic. Ext via AUX2. Dual ✓ (MA600 guide) [V] | 38×38×9 [V] | 8.9 [V] | As r4.11 | Apache-2.0 [V] | **$69** (+$19 spreader) [V] | Available [V] | None | V |
| **moteus n1** | 9 / 26 [V] | 100 [V] | 10–54 V (≤12S) [V] | STM32G4 [V] | CAN-FD 5 Mbps [V] | AUX1/AUX2, RS422 [V] | Onboard plus ext. Dual ✓ [V] | 46×46×8 [V] | 14.6 [V] | As r4.11 | Apache-2.0 [V] | **$149** (+$29) [V] | Available [V] | None | V |
| **moteus x1** | 25 / 62 [V] | 120 [V] | 10–54 V (≤12S) [V] | STM32G4 [V] | CAN-FD 5 Mbps [V] | AUX1/AUX2, RS422, 12 V fan [V] | Onboard plus ext. Dual ✓ [V] | 56×56×10 [V] | 23.7 (README says 23.8) [V] | As r4.11 | Apache-2.0 [V] | **$175** (+$29) [V] | Available [V] | None | V |
| **Trampa VESC 6 MkVI** | 80 [V] | 120 [V] | 11.1–60 V (3S–12S) [V] | STM32F4 (VESC FW target) [V]; F405 [U] | Classic CAN ≤1 Mbps (FW enum tops at CAN_BAUD_1M), UAVCAN [V] | USB, 2× UART, SPI, I²C, PPM, ADC, NRF [V] | No onboard encoder. ABI, Hall, AS5047 and others [V] | 75×70×18 boxed [V] | 232 (with box and cables) [V] | DC/BLDC/FOC; current / duty / speed / position [V] | FW GPLv3 [V]. VESC6 schematic CC BY-SA 4.0 [U] | £200 + tax (RRP £185) ≈ **$265.53** ex-tax [V/E] | Listed for sale [V] | None | V/E/U |
| **Flipsky FSESC 4.12 50A** (VESC 4.12 clone) | 50 [V] | 240 "instantaneous" [V] | 8–60 V (3–13S; safe to 12S) [V] | STM32F4 [U] | Classic CAN (VESC) [U] | USB, PPM; UART/CAN per VESC 4.12 [U] | Hall/ABI via VESC sensor port [U] | 120×56×20 [V] | 80 [V] | VESC modes [V FW] | VESC 4.12 HW CC BY-SA 4.0 [V]; FW GPLv3 [V] | **$70** (no case) / $82 (case) [V] | Available [V] | None | V/U |
| **Flipsky Mini FSESC4.20 50A** (VESC 4.12-based) | 50 [V] | 150 [V] | 8–60 V (3–13S) [V] | STM32F4 [U] | Classic CAN [U] | Micro-USB, PWM in [V] | VESC sensor wire (Hall/ABI) [V/U] | PCB 39×46×17.4; 67×39×18.3 with heat sink [V] | 80 [V] | VESC modes [V FW] | VESC-based [U] | **$56** [V] | Available [V] | None | V/U |
| **Flipsky Mini FSESC6.7 PRO 70A** (VESC 6.6-based); Mini V6 MK5 | 70 [V] | 200 [V] | 14–60 V (4–13S; safe to 12S) [V] | STM32F4 [U] | Classic CAN [V listed] | USB, CAN, UART, SPI, IIC; PPM/ADC/NRF inputs [V] | ABI, HALL, AS5047, AS5048A [V] | 67×39×18.7 with heat sink [V] | 130 [V] | current / duty / speed / position [V] | VESC-based [U] | **$57**; Mini V6 MK5 $67 [V] | Available [V] | ThinkRobotics lists only a Flipsky antispark switch [U] | V/U |
| **SimpleFOC Shield v2/v3** (driver only) | Up to 5 [V] | n/f | 8–24 V [V] | None (L6234 driver shield) [V] | None | Arduino UNO header; encoder/I2C pull-ups [V] | Ext via host MCU | Shield | n/f | Via SimpleFOC library: torque / velocity / angle [V] | Open HW; library MIT [V] | v2 €20 ≈ $22.82, v3 €23 ≈ $26.25 [V/E] | OOS [V] | None | V/E |
| **SimpleFOC Mini v1.1 / v2.3** (driver only) | 2.5 per phase [V] | n/f | 8–35 V (Mini page) / 8–30 V (docs table) [V] | None (DRV8313) [V] | None | 3PWM + EN header [V] | Ext via MCU | 26×21 [V] | n/f | Via library | Open (EasyEDA / GitHub) [V] | v2.3 €6.90 ≈ $7.87; v1.1 €12 [V/E] | v2.3 in stock; v1.1 OOS [V] | None | V/E |
| **SimpleFOC microspora v1.7** (CAN-capable) | 8 max [V] | n/f | 5–35 V [V] | STM32G431CBU6 [V] | CAN on JST 3-pin daisy-chain; transceiver part and bitrate n/f [V] | SPI JST, I2C/encoder/GPIO JST, Qwiic-style [V] | MT6701 onboard support; SPI/I2C ext [V] | 33×34 [V] | n/f | SimpleFOC library; example FW [V] | Open HW (OSHWLab); library MIT [V] | €26.80 ≈ **$30.58** [V/E] | In stock [V] | None | V/E |
| **SimpleFOC Drive v1.8** (driver shield) | 20 [V docs] | 30 [V docs] | 8–30 V [V docs] | None (3PWM shield) [V] | None | Arduino shield [V] | Ext via MCU | n/f | n/f | Via library | Open (GitHub) [U] | €26.80 ≈ $30.58 [V/E] | In stock [V] | None | V/E |
| **Dagor Controller** (ESP32, SimpleFOC) | n/f | "Up to 40A" peak rms [V] | 5–24 V [V] | ESP32 [V] | None; RS-485 protocol "in progress", wireless [V] | Wi-Fi/BT [V] | 14-bit magnetic onboard [V] | 44×44 [V] | 12 [V] | position / velocity / torque [V] | GitHub (license not checked) [U] | €39 ≈ $44.50 [V/E] | OOS [V] | None | V/E/U |
| **Makerbase MKS ESP32 FOC V1 / Dual FOC 3.1** | n/f | n/f | n/f | ESP32 [V title] | CAN not listed [U] | n/f | n/f | n/f | n/f | SimpleFOC-based [V] | Test code on GitHub [V] | $25.99; Dual FOC from $24.99 [V] | Dual FOC OOS [V] | None | V/U |
| **Tinymovr R5.3** (CAN-native, extra) | 25, depends on cooling [V] | n/f | 12–38 V [V] | Qorvo PAC5527 (Cortex-M4F) [V] | CAN 1 Mbps, 2× JST-GH [V] | UART, SPI, AUX/Hall [V] | Onboard high-res absolute (chip not named) [V]. Ext SPI and Hall [V] | 36×40 [V] | 10 [V] | position / velocity / torque [V] | HW MIT and FW MIT up to v3.0.0; v3.1+ proprietary binaries [V] | **$88** (sold out). R5.4 starter kit $124; R5.3 + GIM6010 bracket $98 [V] | R5.3 standalone sold out; kit and bundle available [V] | ThinkRobotics: no hit [U] | V |
| **Tinymovr X5 / M5.2** | 6 [V] | n/f | 12–38 V (X5) [V] | PAC5527-class [U] | CAN 1 Mbps (X5) [V] | UART, SPI [V] | X5: dual onboard absolute sensors ✓. M5.2: single [V] | 30×38 (X5) / 29.5×29.5 (M5.2) [V] | 8 (X5) [V] | pos / vel / torque [V] | As above | X5 $109; M5.2 $88 [V] | Available [V] | None | V/U |
| **MAB MD80 v3.0** (MD20; MD80 60 V) | 20 without cooling (MD20: 4.5) [V] | 80 for 2 s (MD20: 20) [V] | 10–48 V max, 24–42 V nominal; a 60 V variant exists [V] | n/f | CAN-FD 1/2/5/8 Mbps plus CANopen; SW termination [V] | USB via CANdle; SPI/RS422 ext encoder [V] | Built-in 14-bit absolute; output encoders ✓ [V] | Ø55 (MD20 Ø35) [V] | 16 [V] | position PID, velocity PID, impedance (40 kHz), profile pos/vel [V] | Proprietary (no source found) [U] | €220 ≈ **$251.04** (MD20 €169 ≈ $192.85; 60 V €269 ≈ $306.95) [V/E] | In stock [V] | None | V/E/U |
| **CubeMars Driver Board V2.1** (V2.2; AK-series boards) | 40 rated (V2.2: 10) [V] | 60 max (V2.2: 30 max, but text also says "peak current of 10A") [V, conflicting] | 48 V rated, 52 V max (V2.2: 24 V / 28 V) [V] | n/f | CAN, bitrate n/f [V] | Serial port, R-link tool [V] | Onboard 14-bit single-turn absolute [V]; dual n/f | 62×58 (V2.2: 54×50) [V] | n/f | Servo mode and MIT mode; pos/vel/torque, pos-vel loop [V] | Proprietary [U] | **$129.90** (V2.2 $79.90; AK boards $59.99–$129.90) [V] | Available [V] | ThinkRobotics: no hit [U] | V/U |
| **Damiao DM40/60/80/100-2E** | 4 / 10 / 20 / 40 [V catalog] | 10 / 20 / 40 / 80 [V] | DM40: 24 V (4S–6S), abs max 32 V. DM60/80/100: 24 V (4S–12S), abs max printed as 85 V [V] | Cortex-M4 @ 200 MHz, part not named [V] | CAN; UART for tuning [V] | UART [V] | Magnetic: dual magnetic or single + Hall; dual ✓ [V] | n/f | n/f | MIT / velocity / position [V] | Proprietary [U] | n/f | Official site lists DM60 (10 A / 20 A, 24 V) [V]; none at Western resellers [U] | None | V/U |
| **SteadyWin GDZ/GDS/GDM/GDK drivers** (sold only as motor options) | n/f | n/f (GIM8108-6 motor stall 19.8 A) [U] | Variant names: GDZ468 12–40 V; GDZ468H 12–52 V [U] | n/f | CAN (RS485 on some) [U] | n/f | GDS810: 16-bit, second encoder YES [U] | n/f | GDS810 adds ≈42 g (567 − 525) [E] | "MIT GDM810 (SDC303)" option [U] | Proprietary [U] | Not sold alone. Bundle deltas range +$30 to +$150 (see notes) [E] | Resellers in stock [U] | None | U/E |
| **Ben Katz mini-cheetah driver** (open design) and MIT-protocol clones | n/f | n/f | FW soft limit 40 V, fault at 43 V [V code] | STM32F446 [V] | Classic CAN 1 Mbps (bxCAN 3 × 15 TQ) [V code / E] | SPI (DRV8323), UART | SPI encoder, 65536 CPR config [V] | n/f | n/f | MIT impedance: p, v, kp 0–500, kd 0–100, t_ff [V] | HW + FW MIT [V] | No official store; clones exist (e.g. SteadyWin "MIT GDM810") [U] | n/f | None | V/U/E |

---

### 2. Per-driver notes (sources and verbatim snippets ≤15 words)

#### 2.1 ST B-G431B-ESC1

**ST eStore** https://estore.st.com/en/b-g431b-esc1-cpn.html [V]
- The official product page https://www.st.com/en/evaluation-tools/b-g431b-esc1.html timed out and reset the connection.
- Price: `data-custom-price="$39.26"`. The qty-5 tier is also 39.26. Stock: "In stock".
- Peak current: "Output peak motor current (… tested with propeller … air-forced cooling): 40 A".
- Voltage: "Designed for drones with up to 6S LiPo battery pack".
- Power stage: "discrete N-channel 60 V, 120 A STripFET F7 power MOSFETs".
- MCU: "STM32G431CB Arm® Cortex®-M4 32-bit MCU, 213 DMIPS, 128 Kbytes of Flash".
- Interfaces: "ESC ready for communication with any standard flight control unit (FCU): PWM/CAN/UART".
- Sensors: "Support for motor sensors (Hall or encoder)".
- Size: "Dimensions (including the daughterboard with ST-LINK part): 30 mm × 41 mm".
- Mass: "Weight (including the daughterboard with ST-LINK part): 9.2 g".

**UM2516 Rev 1** (official ST manual) [V, primary document via mirror]
- Read via mirror https://datasheet.octopart.com/B-G431B-ESC1-STMicroelectronics-datasheet-137913821.pdf. The st.com copy timed out.
- Supply: "LiPo battery power input (3S-6S)" and "DC power supply: min 3S - max 6S".
- CAN transceiver: "The CAN interface is provided with transceiver on board".
- Termination: "terminator resistor (120 Ω) and it is manageable by firmware".
- Transceiver part in the schematic: "TCAN330DCNT".
- Encoder input: "J8 for motor sensor (Hall or encoder)" and "supply voltage line is provided with 5 V and GND".

**TI TCAN330** https://www.ti.com/product/TCAN330 [V]
- "TCAN330, TCAN332, TCAN334 and TCAN337 are specified for data rates up to 1Mbps."
- Consequence: the bus is limited to ≤1 Mbps even though the MCU has FDCAN [E].

**Digikey reference design** https://www.digikey.co.uk/reference-designs/en/motor-control/motor-control/2840 [U]
- "Voltage In: 11.1 ~ 22.2 VDC"
- "Power / Current Out: 40 A (Peak)"

**SimpleFOC docs** https://docs.simplefoc.com/bldc_drivers [U, secondary]
- Lists the board as "30V/40A" at "16€".

**Evelta (India)** https://evelta.com/b-g431b-esc1-esc-with-stm32g431cb-mcu-pwm-can-uart/ [U, light check]
- Price: "₹2,365.00" without tax and "₹2,790.70" with tax.
- Shipping: "Shipped in 24 Hours from Mumbai Warehouse".
- Conversion [E]: 2365 / 95.74 = $24.70; 2790.70 / 95.74 = $29.15.

**Continuous current: not rated by ST.** The only official current figure is the 40 A peak with forced-air cooling.

#### 2.2 Berkeley "Recoil" motor controller

Recoil is firmware for the B-G431B-ESC1. No separate Recoil PCB was found.

**Recoil firmware repo** https://github.com/T-K-233/Recoil-Motor-Controller-BESC [V]
- README: "Recoil Motor Controller Firmware for B-G431B-ESC1". The GitHub license field is `"spdxId":"MIT"`.
- CAN rate, in `…/Recoil-Motor-Controller-B-G431B-ESC1.ioc`: "FDCAN1.CalculateBaudRateNominal=1000000".
- Modes, in `Core/Inc/motor_controller_conf.h`: "MODE_TORQUE = 0x11U", "MODE_POSITION = 0x13U", "PARAM_POSITION_CONTROLLER_POSITION_KP".
- Encoder, in `Core/Inc/encoder.h`: "#define AS5600_I2C_ADDR 0x36U".
- CANopen-style handling, in `Core/Inc/motor_controller.h`: "MotorController_handleNMT", "MotorController_handleSDO".

**Berkeley Humanoid Lite paper** https://arxiv.org/html/2504.17249 [V]
- Driver choice: "we opted for the B-G431B-ESC1 as the motor driver, favoring its affordability".
- Bus: "connected via a 1 Mbps CAN 2.0 bus".
- Loop rate: "configured to be 250 Hz".
- Battery: "onboard 6S 4000 mAh Lithium Polymer (LiPo) battery".
- BOM line: "B-G431B-ESC1 Motor Driver $19 $23".
- Adapters: "USB-CAN Adapters (4x) $68 $43". That is $17 per adapter [E].

**BHL actuator BOM** (Google Sheet linked from https://berkeley-humanoid-lite.gitbook.io/docs/getting-started-with-hardware/materials-and-parts-bom; CSV export of sheet 1AQEHcH_nPkXYfor2-h7bwNIUMmsePtAm53epnsWgZXc) [U, project BOM]
- "B-G431B-ESC1,Motor controller,1,$18.97" (links to Digikey) and "¥165.00".
- "AS5600,I2C position encoder,1,$3.30".

**Project page** https://lite.berkeley-humanoid.org/ [V]
- "keeping the total hardware cost under $5,000".

#### 2.3 ODrive (S1, Pro, Micro, v3.6)

**Prices and stock.** Shopify JSON and .js at https://shop.odriverobotics.com/products/odrive-s1.js (also `odrive-pro`, `odrive-micro`, `odrive-v36`) and the worldwide shop https://wwshop.odriverobotics.com/products/odrive-s1.js [V]
- Prices: S1 "149.00", Pro "229.00", Micro "89.00", v3.6 "259.00".
- Volume tiers from the body text: "1 - $ 149.00", "100 - $ 143.00"; Pro "100 - $ 209.00"; Micro "100 - $ 79.00".
- v3.6: "56V / Yes - $259.00 - Sold out56V / No - $259.00".
- WW shop: S1 solder-pad variant unavailable; heat-spreader plate unavailable.
- The US shop now has tariff-surcharge line items: "A tariff surcharge now applies to some products on our US shop".
- Accessories: heat-spreader plate $12; USB-CAN adapter $37.

**S1 datasheet** https://docs.odriverobotics.com/v/latest/hardware/s1-datasheet.html [V]
- DC voltage row: "12 | 16-48 | 50.5 | V".
- Current row: "20 40 40-80 … Free air … Heat spreader plate … Peak".
- "CAN baudrate … 8 Mbit/s".
- "The RS485 and SPI feedback interfaces are mutually exclusive on S1".

**S1 shop page** https://shop.odriverobotics.com/products/odrive-s1 [V]
- "40A Continuous (with heat spreader, recommended)".
- "CAN 2.0B @ 1Mbps Control (5Mbit/s CAN-FD, experimental)".
- "On-board magnetic encoder: MA702".
- "Dual absolute encoder support allows for precise load positioning and instant cold starts".
- "Mass - 35g (no screw terminal) | 55g (screw terminals present)".
- "Board Perimeter - 66mm x 50mm".
- "Comes with a 2ohm 50W power resistor."

**Pro datasheet** https://docs.odriverobotics.com/v/latest/hardware/pro-datasheet.html [V]
- DC voltage row: "15 | | 58 | V".
- Current row: "20 80 100 … Free air … Active cooling … Peak (3 second max)".
- Mass row: "Mass | 140 72 32 | g | Full Case Heat Spreader Bare Board".
- Dimensions row: "51 64 17.5 | mm".
- "CAN baudrate … 12 Mbit/s".

**Pro shop page** https://shop.odriverobotics.com/products/odrive-pro [V]
- "Up to 70A continuous, 100A peak current with heatsink and fan".
- "CAN 2.0B @ 1Mbps Control (10Mbit/s CAN-FD, experimental)".
- "Supports offboard quadrature, hall, SPI, SSI, and RS485 encoders".

**Micro datasheet** https://docs.odriverobotics.com/v/latest/hardware/micro-datasheet.html [V]
- DC voltage row: "10 | 12-24 | 31 | V".
- Current row: "3.5 7 | A | Free air … Peak".
- Mass row: "Mass | 11.7 8.1 6.8 | g".
- Dimensions row: "32 32 7 | mm".
- "A 120-ohm CAN termination resistor can be enabled by bridging…".

**Micro shop page** https://shop.odriverobotics.com/products/odrive-micro [V]
- "CAN 2.0B @ 1Mbps with simple protocol (CAN-FD Firmware Coming Soon)".

**Micro schematic** https://odriverobotics.com/s/ODrive-Micro-rev-A2.PDF [V]
- Parts read from the schematic: "STM32H725RGV6", "MCP2542FDT", "MA702GQ", "DRV8316CRRGFR".
- Read via WebFetch; the tool auto-cached the PDF (see §4).

**Comparison table** https://docs.odriverobotics.com/v/latest/hardware/odrive-comparison.html [V]
- Current row: "70A / 120A [1] | 40A / 80A [2] | 3.5A / 7A | 40A / 120A".
- Recommended max voltage row: "58V | 50.5V | 28V | 48V".
- Mass row: "34g | 35g | 6.8g | 80g".
- Dimensions row: "135 mm x 50 mm" (v3.6).
- CAN-FD footnote: "[5] Available since firmware version 0.6.10".

**CAN protocol** https://docs.odriverobotics.com/v/latest/manual/can-protocol.html [V]
- "Set_Input_Pos Host → ODrive Input_Pos Vel_FF Torque_FF".
- Gain messages "Set_Pos_Gain" and "Set_Vel_Gains".
- "ODrive Pro, S1 and Micro support CAN-FD".
- "Supported baudrates for autodetection: 40kbps, 125kbps, 250kbps, 500kbps, 1Mbps."

**MCU family for Pro/S1** https://docs.odriverobotics.com/v/latest/guides/legacy-dfu.html [V]
- "Debug IO connector ( Pro , S1 )" together with "target/stm32h7x.cfg".

**Open-source status** [V]
- GitHub https://github.com/odriverobotics/ODrive: new-generation firmware source "is currently not publicly available".
- v3 firmware license (LICENSE.md): "MIT License".
- v3 MCU (`Firmware/Tupfile.lua`): "-DSTM32F405xx".
- v3 hardware license (https://github.com/odriverobotics/ODriveHardware LICENSE): "The MIT License (MIT)".

**v3.6 shop page** https://shop.odriverobotics.com/products/odrive-v36 [V]
- "56V version: 12V to 56V."
- "Peak current 120A per motor."
- "ODrive v3.6 is Not Recommended for New Designs (NRND)."
- "Position, Velocity, and Current control modes."

#### 2.4 ODrive clones: Flipsky ODESC and Makerbase (MKS)

**Flipsky catalog** https://flipsky.net/products.json (official Flipsky Shopify store) [V]

**ODESC V4.2** https://flipsky.net/products/odesc-v4-2-single-drive-high-current-high-precision-brushless-servo-motor-controller-based-on-odrive3-6-upgrade-software-configuration-compatible-with-odrivetool-foc-bldc [V]
- Prices "34.99" (24 V) and "43.99" (56 V), both available.
- "Microprocessor:STM32F405RGT6".
- "Maximum current:120A" and "Continuous current:70A". These are vendor claims.
- "Working voltage: 8-56V (for ODESC_V4.2_56V)".

**ODESC V4.2 at Sequre** https://sequremall.com/products/odesc-v4-2-single-drive-high-current-high-precision-brushless-servo-motor-controller-based-on-odrive3-6-upgrade-software-configuration-compatible-with-odrivetool-foc-bldc [U]
- "Product Size: 63*58*30mm" and "Net Weight Of Product: 70g".
- "Communication interface: USB, PWM, UART, CAN, Analog Input, Step & Direction".

**ODESC 3.6 single** https://flipsky.net/products/odesc3-6-single-drive-controller-with-heat-sink-optimization-of-high-performance-brushless-motor-high-power-foc-bldc-based-on-odrive [V]
- Prices "69.00" (24 V) and "85.00" (56 V).
- "Current Parameter:50A continuous/120A peak".
- "Applicable Voltage:8-24V". The page text lists only this range, although a 56 V variant is sold.

**ODESC 3.6 dual** https://flipsky.net/products/odesc3-6-dual-drive-controller-56v-with-heat-sink-optimizes-high-performance-brushless-motor-high-power-foc-bldc-based-on-odrive [V]
- Price "59.99".
- "Applicable Voltage: 8-56V".

**India lead for ODESC V4.2** https://www.technobotix.in/products/odesc-v4-2-56v-/1781252000001361097 [U]
- "₹7,799.00" and "OUT OF STOCK". Conversion: 7799 / 95.74 ≈ $81.46 [E].

**Makerbase3D store pages** [V brand store]
- Store identity: the site says "Makerbase is a professional 3D printing solution provider". The domain was not independently confirmed as official.
- XDrive Mini https://makerbase3d.com/product/makerbase-xdrive-mini-high-precision-brushless-servo-motor-controller-based-on-odrive3-6-with-as5047p-on-board/: "$42.99 Original price was … $40.99 Current price". Title: "…Based On ODrive3.6 with AS5047P on board".
- XDrive3.6 variants https://makerbase3d.com/product/makerbase-xdrive3-6-56v-high-precision-brushless-servo-motor-controllerbased-on-odrive3-6-upgrade/: MKS XDRIVE-S 49.65, MKS XDRIVE MINI 42.69, MKS XDRIVE 69, all in stock.
- MKS ODrive 3.6 56 V https://makerbase3d.com/product/makerbase-odrive3-6-56v-with-mks-x2212-motor-foc-bldc-agv-servo-dual-motor-controller-board-odrive-3-6/: "MKS ODRIVE" 89.99, in stock.

**MKS XDrive Mini specs and issues** [U]
- Specs from search snippets (robotics.org.za and an Amazon HanOaki listing): "working current of 60A and a peak current of 120A"; "12V to 56V"; "STM32F405RGT6".
- Community guide https://hackaday.io/project/204985-mks-xdrive-mini-guide-set-up-tuning-arduino/details: "runs legacy ODrive v3.6 firmware (v0.5.1)"; "SN65HVD230 CAN module"; "the RS pin resistor value is too high"; "500k baud rate".
- https://github.com/justlovescience/MKS-XDRIVE-MINI: "acts like a dual-axis ODrive. This causes CAN ID conflicts".

#### 2.5 mjbots moteus (r4.11, c1, n1, x1)

**Shop** https://mjbots.com/products.json and https://mjbots.com/products/moteus-r4-11 (also `moteus-c1`, `moteus-n1`, `moteus-x1`) [V]

Prices (all available):
- r4.11 "94.00", c1 "69.00", n1 "149.00", x1 "175.00".
- Heat spreaders: r4 29.00, n1 29.00, c1 19.00, x1 29.00.
- Host adapters: mjcanfd-usb-1x 39.00; pi3hat r4.5 149.00; fdcanusb 89.00 (unavailable).

r4.11:
- "Voltage Input: 10-44V (<=10S)"
- "Peak Phase Current: 100A"
- "Continuous phase current: 12A / 32A (w/o and w/ thermal management)"
- "Mass: 14.2g"
- "Dimensions: 46x53mm"
- "Communications: 5Mbps CAN-FD"
- "170 MHz 32 bit STM32G4 microcroprocessor"
- "Open source firmware (Apache 2.0)"

c1:
- "Voltage Input: 10-51V (<=12S)"
- "Peak phase current: 20A"
- "Continuous phase current: 5A / 14A"
- "Mass: 8.9g"
- "Dimensions: 38x38x9mm"
- AUX: "SPI, UART, GPIO, ADC, Quadrature, Hall, and I2C support"

n1:
- "Voltage Input: 10-54V (<=12S)"
- "Peak phase current: 100A"
- "Continuous phase current: 9A / 26A"
- "Mass: 14.6g"
- "Dimensions: 46x46x8mm"
- "RS422 connector (JST GH6)"

x1:
- "Voltage Input: 10-54V (<=12S)"
- "Peak phase current: 120A"
- "Continuous phase current: 25A / 62A"
- "Mass: 23.7g"
- "Dimensions: 56x56x10mm"

**README** https://github.com/mjbots/moteus (raw README.md) [V]
- "available under an Apache 2.0 License".
- "controller/ - PCB design for moteus-r4.11", plus c1/, n1/, x1/.
- Discrepancies with the shop: README lists x1 as "1kW @ 36V" and "23.8g"; the shop lists 1.3 kW and 23.7 g. README lists n1 as "1.3kW @ 36V"; the shop lists 2 kW.

**Docs** [V]
- https://mjbots.github.io/moteus/reference/encoders/: "the onboard magnetic encoder (AS5047P) is assumed to sense the rotor".
- https://mjbots.github.io/moteus/guides/dual-encoders/: "Onboard + 8x reducer + MA600 on-axis - Disambiguation".
- https://mjbots.github.io/moteus/integration/can-fd/: "Moteus requires 1Mbps/5Mbps CAN-FD timing, a sample point of 0.666".
- https://mjbots.github.io/moteus/guides/control-modes/: "kp scale: Scale the proportional constant by this factor" and "Feedforward torque: Give this much extra torque".
- https://mjbots.github.io/moteus/reference/hardware/ power limits at 30 kHz PWM:
  - r4: "<= 30V 900W … >= 38V 400W"
  - n1: "<= 36V 2000W … >= 44V 1000W"
  - c1: "<= 28V 250W … >= 41V 150W"

#### 2.6 VESC family

**Trampa VESC 6 MkVI** https://trampaboards.com/1-x-vesc-6-mkv--170-tax-each-p-27529.html (official Trampa shop) [V]
- Price: "1 x VESC 6 MkVI - £200 Each", "RRP £185", "= £200+ Tax". Conversion: 200 / 0.75322 = $265.53 [E].
- "Voltage: 11.1V – 60V (Safe for 3S to 12S LiPo)."
- "Current: Continuous 80A, peak 120A."
- "Communication ports: USB, CAN,UAVCAN, 2x UART, SPI, I²C".
- "Supported sensors: ABI, HALL, AS5047 and other encoders".
- "VESC Box Length 75mm" (width 70 mm, height 18 mm).
- "Weight: 232g".
- "GPL V3 licensed VESC Firmware will come pre-installed".

**VESC firmware** https://github.com/vedderb/bldc [V]
- `datatypes.h`: "CAN_BAUD_1M" is the fastest enum value. Also "CAN_PACKET_SET_POS = 4" and "CONTROL_MODE_POS".
- README: "released under the GNU General Public License version 3.0".
- Makefile: "target/stm32f4x.cfg".

**VESC 4.12 hardware** https://github.com/vedderb/bldc-hardware [V]
- "VESC Hardware is licensed under the Creative Commons Attribution-ShareAlike 4.0".
- VESC 6 schematic license (CC BY-SA) comes from search snippets only [U].

**Flipsky VESC-based boards** (official Flipsky store) [V]
- FSESC 4.12 https://flipsky.net/products/fsesc-4-12-50a-based-on-vesc%C2%AE-4-12-with-without-aluminum-case:
  - "Amps: 50A continuous, instantaneous current 240A."
  - "Voltage: 8V-60V"
  - "Weight: 80g"
  - "Size: 120x56x20mm"
  - "It is recommended to keep firmware 5.2 from factory ship"
- Mini FSESC4.20 https://flipsky.net/products/mini-fsesc4-20-50a-base-on-vesc%C2%AE-4-12-with-aluminum-anodized-heat-sink:
  - "Amps: 50A continuous / 150A peak"
  - "PCB Size: 39x46x17.4mm"
  - "Weight: 80g"
- Mini FSESC6.7 PRO https://flipsky.net/products/mini-fsesc6-7-pro-70a:
  - "Continuous current: 70A; instantaneous current: 200A"
  - "Voltage: 14V-60V"
  - "Control Interface Ports:USB,CAN,UART, SPI, IIC"
  - "Weight: 130g"
  - "Support four control modes: Current/Dutycycle/Speed /Position control mode."
- Mini V6 MK5 https://flipsky.net/products/flipsky-mini-v6-mk5-with-power-button-base-on-vesc_6_mk5-with-aluminum-anodized-heat-sink: "67.00".

**Suitability for position control [E].**
- Position mode exists in the firmware (`CONTROL_MODE_POS`, `CAN_PACKET_SET_POS`), and CAN is classic, ≤1 Mbps.
- There is no per-message kp/kd impedance command, and the boards are ESC-sized (67×39 mm up to 120×56 mm).
- Usable for slow position servoing. Less suited than moteus, ODrive or MIT-protocol drivers to torque/impedance-controlled legged joints.

#### 2.7 SimpleFOC ecosystem boards

**Official shop** https://simplefoc.com/shop [V]
- "microspora v1.7 €26.80 In Stock"
- "Drive v1.8 €26.80 In Stock"
- "Mini v2.3 € 6.90 In Stock"
- "Mini v1.1 € 12.00 Out of Stock"
- "Shield v3 € 23.00 Out of Stock"
- "Shield v2 € 20.00 Out of Stock"
- "Dagor Controller € 39.00 Out of Stock"

**microspora** https://github.com/simplefoc/SimpleFOC-microspora (raw README) [V]
- "MCU: STM32G431CBU6"
- "Power supply: 5-35V"
- "Max current: 8A"
- "MT6701 magnetic encoder support"
- "CAN JST connector with daisy-chain support"
- "Compact form factor: 33mm x 34mm"

**Mini** https://docs.simplefoc.com/simplefocmini [V]
- "Power supply: 8-35V"
- "Max current: 2.5A per phase"
- "Small size: 26x21 mm"

**Driver table** https://docs.simplefoc.com/bldc_drivers [V]
- Mini v1: "8-30V".
- SimpleFOCDrive: "8-30V", "20A (30A peak)".
- Shield v2: "8-24V", "up to 5 Amps".
- Docs footer: "Distributed by an MIT license".

**Dagor** https://github.com/byDagor/Dagor-Brushless-Controller (raw README) [V]
- "Dimensions | 44 x 44mm"
- "Mass | 12g"
- "Power source voltage | 5-24V"
- "Peak rms current | up to 40A"
- "Finish RS-485-based protocol" is still unchecked on the roadmap.

**Makerbase ESP32 FOC pages** https://makerbase3d.com/product/esp32-foc/ and https://makerbase3d.com/product/makerbase-simplefoc-dual-brushless-micro-foc-3-1-servo-with-current-loop-for-bldc-motor-compatible-with-esp32/ [V]
- Prices "$ 25.99" and "From: $ 24.99". The Dual FOC 3.1 is "Out of stock".
- CAN is not stated [U].

**Not applicable.** Makerbase "MKS SERVO" boards are closed-loop *stepper* drivers: "SERVO42D NEMA17 closed loop stepper motor driver" (makerbase3d.com) [V].

#### 2.8 Tinymovr (CAN-native compact driver; added)

**R5.3** https://tinymovr.com/products/tinymovr-r5 [V]
- "Input Voltage: 12.0–38.0V"
- "Max Continuous Phase Current (depending on cooling): 25.0 A"
- "CAN Bus interface 1Mbps with 2x JST-GH 4-pin sockets"
- "Dimensions: 36 mm x 40 mm"
- "Weight: 10 g"
- JSON price "88.00", available=false.

**X5** https://tinymovr.com/products/x5-motor-controller [V]
- "Max Continuous Phase Current (depending on cooling): 6.0 A"
- "Dual onboard Absolute Angle Sensors"
- "Dimensions: 30 mm x 38 mm"
- "Weight: 8 g"
- Price $109.

**Catalog** https://tinymovr.com/products.json [V]
- R5.4 starter kit "124.00", available.
- R5.3 + GIM6010 bracket bundle "98.00", available.
- M5.2 "88.00".
- CANine USB-CAN "34.50".

**GitHub** https://github.com/tinymovr/Tinymovr (now motionlayer/Tinymovr) [V]
- "Firmware for the PAC5527 MCU in Tinymovr".
- Licenses are per directory, "hardware/ … MIT" and "firmware/ … MIT", as of v3.0.0.
- "Releases from v3.1 onward are distributed … as proprietary binaries".

#### 2.9 MAB Robotics MD series (standalone drivers)

**Shop** [V]
- https://www.mabrobotics.pl/product-page/md80-motor-controller: "220,00 €", schema.org InStock.
- https://www.mabrobotics.pl/product-page/md20-motor-controller: "169,00 €".
- MD80 60VDC: €269, from the category page JSON.

**MD series page** https://www.mabrobotics.pl/md-series [V]
- MD80: "Peak current: 80A", "Size: ∅55mm", "Weight: 16g".
- MD20: "Size: ∅35 mm".
- "CAN-FD and CANopen".
- "Support for additional output encoders".

**MD80 docs** https://mabrobotics.github.io/MD80-x-CANdle-Documentation/MD/MD80.html [V]
- "Nominal Input Voltage Range | 24 - 42 VDC"
- "Maximum Input Voltage Range | 10 - 48 VDC"
- "Max Continuous Phase Current w/o cooling | 20 A"
- "Max Peak Phase Current (t = 2 s) | 80 A"
- "FDCAN Baudrate (adjustable) | 1/2/5/8 Mbps"
- "Impedance Controller Execution Frequency | 40 kHz"
- MD20.html: "Max Continuous Phase Current w/o cooling | 4.5 A".

**Conversions [E].** 220 / 0.87635 = $251.04; 169 / 0.87635 = $192.85; 269 / 0.87635 = $306.95.

#### 2.10 CubeMars driver boards (sold separately)

**Official store catalog** https://store.cubemars.com/products.json [V]

**Driver Board V2.1** https://store.cubemars.com/products/driver-board-v2-1 [V]
- Price "129.90", available.
- "Rated Operating Voltage: 48V DC"
- "Maximum Allowable Voltage: 52V DC"
- "Rated Operating Current: 40A DC"
- "Maximum Allowable Motor Current: 60A DC"
- "Dimensions: 62*58 mm"
- "Communication Interface: CAN, Serial Port"
- "supports servo mode and MIT motion control mode"

**Driver Board V2.2** https://store.cubemars.com/products/driver-board-v2-2 [V]
- Price "79.90".
- "Rated Operating Voltage: 24V DC"
- "Maximum Allowable Voltage: 28V DC"
- "Maximum Allowable Motor Current: 30A DC"
- "Dimensions: 54*50 mm"
- Conflicting text elsewhere on the page: "peak current of 10A".

**Driver Board for AK Series** https://store.cubemars.com/products/driver-board [V]
- Variants run from AK40-10 "59.99" to AK10-9 "129.90".
- These boards are matched to AK motor models. Use with other motors is not documented [U].

#### 2.11 Damiao standalone drivers

**2025 product selection catalog** (official Damiao PDF hosted by WRC) https://www.worldrobotconference.com/profile/robot/download/2025/06/30/%E8%BE%BE%E5%A6%99%E7%A7%91%E6%8A%80DAMIAO%20-%202025%E5%B9%B4%E4%BA%A7%E5%93%81%E9%80%89%E5%9E%8B%E6%89%8B%E5%86%8C_20250630192546A441.pdf, page 25 "驱动器" [V]
- DM40-2E supply: "24V（4S-6S）绝对最大值不超过32V".
- DM60/80/100-2E supply: "24V（4S-12S）绝对最大值不超过85V" (as printed).
- Continuous current ("最大持续电流"): 4A / 10A / 20A / 40A.
- Peak current ("峰值电流"): 10A / 20A / 40A / 80A.
- MCU: "Cortex®-M4", "200MHz".
- Communication: "CAN（UART调参）".
- Control modes: "MIT、速度、位置".
- Encoders: "支持双编码器".

**Official site** https://www.mdmbot.com/ [V]
- "已推出DM40、DM60、DM80、DM100等多款驱动器".
- DM60 page https://www.mdmbot.com/index.php?c=show&id=98: "持续最大电流10A；峰值电流20A；供电24V".

**Price: n/f.** None was found at aifitlab, rcdrone or openelab [U].

#### 2.12 SteadyWin drivers (only as motor options)

- The official site https://www.steadywin.cn/ gave nothing usable: the TLS certificate failed verification and the page is JS-rendered.

**GIM8108-6 at aifitlab** https://aifitlab.com/products/steadywin-gim8108-6-planetary-reducer-motor [U]
- Spec rows: "Driver Model | GDS810", "Communication | CAN", "Second Encoder | YES", "Encoder Resolution | 16 Bit".
- Mass rows: "Motor Weight (without Driver) | 525 g" and "(with Driver) | 567 g". The driver therefore adds about 42 g [E].
- Price options: "ONLY Motor" $135 versus "Include MIT GDM810 (SDC303)" $220, so the driver option costs about +$85 [E].

**GWK8108-8 at aifitlab** https://aifitlab.com/products/steadywin-gwk8108-8-motor [U]
- Motor alone $90.
- With GDK100: $125, i.e. +$35 [E].
- With GDS68: $150, i.e. +$60 [E].
- With "GDZ468(12-40V)": $220, i.e. +$130 [E].
- With "GDZ468H(12-52V)": $240, i.e. +$150 [E].

**GIM3510-8 at rcdrone** https://rcdrone.top/products/small-robot-joint-module-with-built-in-communication-driver-dual-encoder-aloha-motor [U]
- "without driver" $109 versus "with driver GDZ34" $195, i.e. +$86 [E].

#### 2.13 Ben Katz mini-cheetah driver (MIT) and clones

**Hardware repo** https://github.com/bgkatz/3phase_integrated [V]
- "3-phase motor controller with integrated position sensor".
- LICENSE: "MIT License … Copyright (c) 2020 Ben Katz".

**Firmware repo** https://github.com/bgkatz/motorcontrol [V]
- Makefile: "-DSTM32F446xx".
- `Core/Inc/hw_config.h`: "#define V_BUS_MAX 40.0f // max drive voltage".
- `Core/Src/can.c`: "hcan1.Init.Prescaler = 3;" with "CAN_BS1_12TQ" and "CAN_BS2_2TQ". Also "/// 12 bit kp, between 0 and 500 N-m/rad".
- Bit-rate estimate [E]: assuming a 45 MHz APB1 clock, 45e6 / (3 × (1+12+2)) = 1.0 Mbps.

**Clones.** No official seller of Katz-design boards was verified. The SteadyWin "MIT GDM810 (SDC303)" option is an MIT-protocol driver sold with motors [U].

---

### 3. Guidance for JX1 (24–48 V bus, ~20–40 A phase per leg joint, CAN, lowest practical cost)

#### 3.1 Choose the bus voltage first; it prunes the list [E]

Li-ion full-charge voltage at 4.2 V/cell: 6S = 25.2 V, 7S = 29.4 V, 10S = 42.0 V, 12S = 50.4 V, 13S = 54.6 V.

- **≤25.2 V (6S):** B-G431B-ESC1 / Recoil (3S–6S only) and CubeMars V2.2 (28 V max) fit. So do moteus r4.11 and Tinymovr. The r4.11 keeps its full 900 W at ≤30 V (§2.5).
- **10S (42 V):** moteus r4.11 (44 V max) fits but derates to 400 W above 38 V at 30 kHz PWM. Tinymovr (38 V max) does not fit at full charge.
- **12S "48 V" (50.4 V full):**
  - moteus n1/x1 (54 V), ODrive Pro (58 V), CubeMars V2.1 (52 V), ODESC-56 V and VESC (60 V) all fit.
  - ODrive S1 (50.5 V) has almost no headroom, so a brake resistor is essential (one is included).
  - moteus n1 derates to 1000 W at ≥44 V.
- **13S (54.6 V):** exceeds S1, n1/x1 and CubeMars V2.1.

#### 3.2 Drivers that genuinely meet 20–40 A continuous with CAN

- **Verified continuous ratings:**
  - moteus x1: 62 A cooled.
  - ODrive Pro: 80 A active cooling (70 A per the shop).
  - ODrive S1: 40 A with plate.
  - CubeMars V2.1: 40 A rated.
  - moteus r4.11: 32 A cooled.
  - moteus n1: 26 A cooled.
  - Tinymovr R5.3: 25 A, cooling-dependent.
  - MAB MD80: 20 A without cooling.
  - Damiao DM80-2E / DM100-2E: 20 / 40 A.
  - VESC-class: 50–80 A, but bulky and with weaker servo protocols.
- **Vendor or reseller claims, test before relying on them:** ODESC V4.2 (70 A); MKS XDrive Mini (60 A).
- **Peak only:** B-G431B-ESC1 is rated 40 A peak with propeller forced-air cooling and has no continuous rating.

#### 3.3 Cost per axis for 12 leg joints (6 DOF × 2), sorted cheapest first [E; arithmetic = unit price × 12]

| Driver | Unit USD | ×12 | Notes |
|---|---|---|---|
| B-G431B-ESC1, Evelta ex-GST (₹2,365 / 95.74) | 24.70 | 296.43 | ₹2,790.70 incl. GST = $29.15 → $349.78; 6S only; ESC1-row [U] |
| ODESC V4.2 24 V | 34.99 | 419.88 | Not a 48 V option |
| B-G431B-ESC1, ST eStore | 39.26 | 471.12 | With AS5600 (+$3.30): $42.56 → $510.72 |
| MKS XDrive Mini | 40.99 | 491.88 | $42.69 variant → $512.28; specs [U] |
| **ODESC V4.2 56 V** | **43.99** | **527.88** | Cheapest 48 V-capable CAN option; claims [V-claim] |
| Flipsky Mini FSESC4.20 50A | 56.00 | 672.00 | VESC, classic CAN |
| Flipsky Mini FSESC6.7 PRO | 57.00 | 684.00 | VESC |
| Tinymovr R5.3 | 88.00 | 1,056.00 | Sold out standalone; $98 bundle → $1,176 |
| **moteus r4.11** | **94.00** | **1,128.00** | +$29 spreader: $123 → $1,476 |
| ODrive v3.6 (2-axis board / 2) | 129.50 | 1,554.00 | NRND |
| CubeMars V2.1 | 129.90 | 1,558.80 | AK-matched board |
| **ODrive S1** | **149.00** | **1,788.00** | +$12 plate: $161 → $1,932 |
| moteus n1 | 149.00 | 1,788.00 | +$29: $178 → $2,136 |
| moteus x1 | 175.00 | 2,100.00 | +$29: $204 → $2,448 |
| ODrive Pro | 229.00 | 2,748.00 | |
| MAB MD80 (€220 / 0.87635) | 251.04 | 3,012.50 | |
| Trampa VESC 6 MkVI (£200 / 0.75322, ex-tax) | 265.53 | 3,186.32 | |

**Dollars per verified continuous amp [E]:**
- moteus x1: 175 / 62 = $2.82
- ODrive Pro: 229 / 80 = $2.86
- moteus r4.11: 94 / 32 = $2.94
- CubeMars V2.1: 129.90 / 40 = $3.25
- ODrive v3.6: 129.50 / 40 = $3.24
- Tinymovr R5.3: 88 / 25 = $3.52
- ODrive S1: 149 / 40 = $3.73
- moteus n1: 149 / 26 = $5.73
- MAB MD80: 251.04 / 20 = $12.55

**Add CAN host adapters per bus:**
- CANine $34.50, ODrive USB-CAN $37 (classic CAN).
- mjcanfd-usb-1x $39 or pi3hat $149 (CAN-FD; moteus needs FD).
- Berkeley Humanoid Lite paid $68 for 4 adapters.

#### 3.4 Bus planning for classic 1 Mbps CAN [E]

- **Frame length.** An 8-byte standard frame is 44 overhead + 64 data bits = 108 bits. Adding 3 bits of interframe space gives 111 bits. Worst-case bit stuffing brings it to about 135 bits.
- **Throughput.** That is 7,407–9,009 frames/s. At 50% bus load, 3,704–4,505 frames/s are usable.
- **Per joint.** One command plus one reply per cycle, i.e. 2 frames per joint per cycle:
  - 500 Hz: ≈3.7–4.5 joints per bus, so 12 leg joints need 3–4 buses.
  - 250 Hz, as in Berkeley Humanoid Lite: ≈7–9 joints per bus.
- **CAN-FD** (moteus, MAB, ODrive new generation) removes most of this limit.

#### 3.5 Top picks

1. **mjbots moteus r4.11: best open, torque-dense option for a ≤30–42 V bus.**
   - $94 [V]: 32 A cooled / 100 A peak, 10–44 V, CAN-FD 5 Mbps, onboard AS5047P plus dual-encoder support.
   - Per-command kp/kd/feed-forward torque. Apache-2.0 hardware and firmware, so it could legally be built locally in India [E]. The "moteus" name is trademarked (https://mjbots.com/trademark-policy).
   - 12 legs: $1,128 ($1,476 with heat spreaders) [E].
   - For a 12S bus, move to n1 ($149, 26 A cooled) or x1 ($175, 62 A cooled).
2. **ODrive S1: best off-the-shelf 48 V-class option with 40 A continuous.**
   - $149 (+$12 plate) [V]: 12–50.5 V, 40 A continuous / 80 A peak.
   - CAN 2.0B 1 Mbps, with CAN-FD from firmware 0.6.10. MA702 onboard plus RS485/SPI absolute encoder for output sensing. Brake-resistor driver.
   - 12 legs: $1,788 ($1,932 with plates) [E].
   - Closed firmware. 66×50 mm footprint.
3. **B-G431B-ESC1 + Recoil firmware: lowest cost, proven on a humanoid.**
   - $39.26 at ST [V], or ₹2,365 ex-GST (≈$24.70) at Evelta [U/E].
   - 40 A peak (forced air), 3S–6S only, CAN ≤1 Mbps via TCAN330.
   - Needs an external encoder: AS5600 at $3.30, or an ABZ/SPI encoder.
   - Berkeley Humanoid Lite used it at 6S on four 1 Mbps CAN 2.0 buses at 250 Hz [V].
   - 12 legs: $471 (ST) or ≈$296 (Evelta ex-GST) [E].
   - Risks: no continuous rating; thermal behaviour at 20–40 A continuous must be tested; bus fixed near 24 V.

**Worth prototyping in parallel:**
- Flipsky ODESC V4.2 56 V ($43.99, 8–56 V, vendor claim 70 A continuous): cheapest 12S-capable path, but it runs legacy ODrive 0.5.x-class firmware and its specs are unverified.
- CubeMars V2.1 ($129.90, 48 V / 40 A, MIT mode): if the joint motors are AK-compatible.
- For arms, neck and hands: moteus c1 ($69), ODrive Micro ($89), SimpleFOC microspora (≈$30.58, CAN, 8 A) and Tinymovr X5 ($109, dual encoder).

---

### 4. Gaps and caveats

- **B-G431B-ESC1:**
  - The st.com product page and PDFs were unreachable (timeout or connection reset). I used the ST eStore and UM2516 Rev 1 through an Octopart mirror.
  - ST gives no continuous-current rating.
  - The newest UM2516 revision (Rev 4) was not read.
  - Digikey's current US price could not be read (403). The $18.97 in the BHL BOM is historical.
- **ODrive S1/Pro:** the exact MCU part is not published (STM32H7 family only). Pro current figures conflict between datasheet, shop and comparison table (70 vs 80 A continuous; 100 vs 120 A peak). The Pro mass on the shop page looks copied from the S1.
- **Flipsky ODESC and Makerbase XDrive:**
  - No official datasheets. Current ratings are vendor or reseller claims, and board size and mass came from a reseller.
  - Vendor firmware modifications and their source availability are unverified.
  - The XDrive Mini CAN transceiver issue is reported by the community only.
  - makerbase3d.com's status as Makerbase's official store was not independently confirmed.
- **VESC:** the VESC 6 hardware license is from secondary sources only. The Flipsky boards' MCU and CAN transceiver were not confirmed from primary schematics.
- **SimpleFOC:**
  - For microspora, the CAN transceiver part and bitrate and the board mass were not found.
  - Specs for SimpleFOC Mini v2.3 (the current shop version) were not read.
  - "FOCstation", "Lolin" and Storm32 CAN boards were not found or checked (search budget exhausted).
- **Damiao:** DM40/60/80/100-2E prices, sizes and outside-China availability were not found. The "85V" absolute maximum is quoted as printed and looks inconsistent with 4S–12S.
- **SteadyWin:** no standalone driver datasheets or prices. Only reseller bundle deltas are available ([U]/[E]). The official site was unreadable.
- **Not checked** (the WebSearch session limit of 200 calls was reached mid-task): T-Motor and Xiaomi standalone drivers, and mini-cheetah clone sellers other than SteadyWin.
- **MAB, CubeMars:** MCU parts not published. Open-source status assumed proprietary [U].
- **Tinymovr:** the onboard encoder chip model is not stated on the product page. The R5.3 standalone is sold out.
- **India leads** were only lightly checked:
  - Evelta: ESC1 in stock, per page.
  - Technobotix: ODESC V4.2, page shows OUT OF STOCK.
  - ThinkRobotics: no hits for ODrive, VESC, moteus, G431, SimpleFOC, Tinymovr, Damiao, SteadyWin or CubeMars.
  - Robu.in blocked scripted access (403).
  - Robokits, element14 India, Digikey India, Mouser India and Amazon.in were not checked.
  - Import duty and GST on direct imports are not included anywhere.
- **Process notes:**
  - WebFetch automatically cached four PDFs I read into the tool-results folder `C:\Users\testi\.claude\projects\D--Project-thenar-jx1\d251889a-7aed-444b-a917-29048e0309a9\tool-results\`: UM2516, the ODrive Micro schematic, the BHL RSS paper and the Damiao catalog. I did not save them deliberately and did not delete them.
  - Text was extracted from them locally.
  - Temporary HTML and JSON files are in `scratchpad\r2\s5\`.

## 6. Actuators used by reference robots, and lessons for JX1

> Editor's note (2026-09-24): §6 records RobStride values from K-Scale's documentation because robstride.com looked JS-only. §1A later read the RobStride specs and prices directly from the official site bundle and the official manuals (github.com/RobStride/Product_Information). They agree with K-Scale's table, except that RS02 is 405 g on the web page vs 380 g in K-Scale's table and the RS02 manual.


Prepared 2026-09-24 (actuator research sub-agent, Section 6). Scope: Unitree G1/G1 EDU, H1/H1-2, R1; Berkeley Humanoid Lite; ToddlerBot; K-Scale K-Bot and Zeroth; Booster T1/K1; Poppy; plus AGILOped, HighTorque Mini Pi+, AgiBot X2, EngineAI PM01, Fourier N1, Noetix N2/Bumi.

### 0. Labels and conventions

- **[V] VERIFIED**: read today (2026-09-24) on a primary source. That means the maker's official product page or spec sheet, the robot's own paper, or the maker's official GitHub or docs.
- **[E] ESTIMATED**: derived by me. The arithmetic is shown.
- **[U] UNVERIFIED**: secondary source, such as news, a reseller, a forum or a teardown blog. A number that one robot's paper reports about a *different* robot also counts as [U].
- Snippets are verbatim and at most 15 words, in quotes. For URDF and code values, the snippet is the verbatim XML or Python text.
- "URDF effort" is the joint torque limit written in the maker's robot-description file. It is often a simulation or RL limit, not a guaranteed actuator peak. Where a maker publishes several "peak" numbers, all of them are listed.
- Units: N·m, rad/s, kg, m. Prices are in USD unless stated.

---

### 1. Summary table

| Robot | Height m | Mass kg | DOF | Leg actuators (model, peak N·m) | Arm actuators | Reducer types | Price | Label(s) | Source |
|---|---|---|---|---|---|---|---|---|---|
| **Unitree G1 / G1 EDU** | 1.32 | ~35 / "35+" | 23 / 23–43 | N7520-14.3 (hip pitch/yaw; URDF 88; T-N model 71 motoring/83.3 braking); N7520-22.5 (hip roll, knee; URDF 139; T-N 111/131); 2× N5020-16 parallel ankle (URDF 35). Web knee max: **90 (G1) / 120 (EDU)** | N5020-16 (URDF 25; T-N 24.8/31.9); W4010-25 wrist pitch/yaw on EDU (5) | 2-stage gearing (code comment); stage form 1+Zr/Zs suggests planetary [E]. Crossed-roller output bearing, dual encoder, hollow routing | $13.5K; EDU "Contact sales" | V; E (ratios); U (EDU price) | unitree.com/g1; github unitree_rl_lab, unitree_ros |
| **Unitree H1 / H1-2** | ~1.80 / ~1.78 | ~47 / ~70 | H1 5/leg, 4/arm; H1-2 27 | M107 joint motor: knee ~360, hip ~220 (web); URDF knee 300, hip 200; ankle ~59 (H1), 75×2 (H1-2) | H1 ~75; H1-2 shoulder/elbow ~120, wrist ~30 | PMSM + crossed-roller bearing. M107-24 T-N 240/292.5; M107-15 150/182.8 | not on page ($70–90K per [U] tables) | V; U | unitree.com/h1; unitree_rl_lab; unitree_ros |
| **Unitree R1 AIR / R1 / EDU** | 1.23 | ~27 / ~29 | 20 / 26 / 26–40 | motor models not published; URDF hip×3 + knee **60 @18.8 rad/s**; ankle 50 @30 | URDF shoulder P/R 60; yaw/elbow/wrist 33 | not published; "Crossed roller bearings, Double Hook Ball Bearings"; "Dual + single encoder" | **$4,900 / $5,900** / contact | V | unitree.com/R1; unitree_ros R1.urdf |
| **Berkeley Humanoid Lite** | 0.8 | 16 | 22 (5/arm, 6/leg) | "6512" = MAD M6C12 150KV + 15:1 printed cycloidal (hip×3, knee); "5010" = 5010 110KV + 15:1 (ankle×2). Peak not published; ~25–28 upper bound [E]; deployed limits 4–6 | 6512 at shoulder pitch; 5010 elsewhere | 3D-printed PLA cycloidal 15:1 | BOM $4,312 US / $3,236 CN | V; E (joint map, peak) | arXiv 2504.17249; gitbook docs; GitHub HybridRobotics |
| **ToddlerBot (v1; v2.0 2025-08)** | 0.56 | 3.4 | 30 active | Dynamixel 2XC430-W250 hip roll+pitch (1.8 stall); XC330-T288 hip yaw (1.0); XM430-W210 knee and ankle pitch (3.0); XC430-T240BB ankle roll (1.9); v2.0 option 2XM430-W350 hips | 2XL430-W250 (1.5); XC430-T240BB shoulder pitch | hobby-servo spur gearboxes; printed spur/bevel transmissions | <$6,000 | V | arXiv 2502.00893 v4; github hshi74/toddlerbot |
| **K-Scale K-Bot** (company shut Nov 2025) | 1.4 [U] | 34 [U]; URDF sum 36.7 [E] | 20 (5/leg, 5/arm) | Robstride RS04 hip pitch and knee (**120 peak / 40 rated**, 9:1); RS03 hip roll/yaw (60/20, 9:1); RS02 ankle (17/6, 7.75:1) | RS03 shoulder P/R; RS02 shoulder yaw, elbow; RS00 wrist (14/5, 10:1) | QDD, 7.75–10:1 | $8,999 Founder's Ed. [U] | V (docs repo, URDF); U (size, price, status) | github kscalelabs/docs, kbot-models; DesignSpark; Humanoids Daily |
| **K-Scale Zeroth-01 / Z-Bot** | 0.48 [U] | 3.6 [U]; Z-Bot URDF 3.75 [E] | 16 servos (Zeroth-01); Z-Bot URDF 18 incl. grippers | Feetech STS3250 ×16 (50 kg·cm@12 V ≈ 4.9 N·m [E]); STS3215 too slow for legs | same | servo, steel gear | "BoM starts at $350" | V; U | github kscalelabs/zeroth-bot, docs; feetechrc.com |
| **Booster T1** | 1.18 | ~30 | 23 (6/leg, 4/arm, 1 waist, 2 head) | not disclosed. Web "Max Peak Torque: 130N·m". booster_assets URDF: knee 130.5, hip pitch 98.8, hip roll/yaw 68, ankle pitch 73.1 / roll 17.2. booster_gym (RL) URDF: knee **60**, hip pitch 45 | 38.3 (assets) / 18 (gym) | not disclosed; "Dual Encoder" | not published; ~$34K [U] | V; U | booster.tech/booster-t1; github BoosterRobotics |
| **Booster K1** | 0.95 | ~19.5 | 22 | not disclosed. Web "Max Peak Torque: 60N·m". booster_assets URDF knee 112 (conflicts with web), hip pitch 68, hip roll 43, yaw/ankle 38.3 | 14 | not disclosed; dual encoder | $4,999+ [U] | V; U | booster.tech/booster-k1; docs.booster.tech; Humanoids Daily |
| **Poppy Humanoid (INRIA)** | 0.83–0.84 | 3.5 | 25 (5/leg, 4/arm, 5 trunk, 2 head) | Dynamixel MX-28 (hip roll/yaw, knee, ankle; **2.5 stall @12 V**); MX-64 hip pitch (6.0) | MX-28 | servo metal spur gearbox 193:1 / 200:1 | €7,500 (2014); $8,000–9,000 (README) | V | poppy-project.org; github poppy-project; Humanoids 2014 paper; emanual.robotis.com |
| **AGILOped (Bonn, 2025)** | 1.10 | 14.5 | 12 joints / 10 actuators | MyActuator RMD X6-40 (**40 peak / 18 rated**, 1:36); knee up to 80 via parallelogram; passive ankle | 1-DoF arms, X6-40 | 2-stage planetary | $6,380 (10×$545 actuators) | V | arXiv 2509.09364 |
| **HighTorque Mini Pi+** | 0.756 | 15 | 23/27 | HighTorque servos, "Peak Torque 21Nm with Dual Encoders" | same | vendor family "ratio 7-36" | not captured | V | hightorquerobotics.com/mini-pi |
| **AgiBot X2 / X2 Ultra** | 1.31 | ~35 / ~39 | 25 / 30 (6/leg) | not disclosed; "Peak Joint Torque 120N·m" | — | not disclosed | not on page | V | agibot.com/products/X2 |
| **EngineAI PM01 (2026 edu)** | 1.40 | ~44.5 | 24 (6/leg) | self-developed joint modules; max torque 164 (spec table); "peak torque up to 130N·m" (intro) | — | crossed-roller bearing; inner-rotor PMSM | not verified | V; U | engineai.com.cn/product-pm01.html |
| **Fourier N1** | 1.3 | 38 | not verified | FSA actuators [U]; torque not verified | — | — | not finalized | U | Humanoids Daily |
| **Noetix N2 / Bumi** | N2 1.3 [U, conflicting]; Bumi 0.94 | N2 20 [U, conflicting]; Bumi 12 | N2 18 | N2 "up to 120 Nm" [U] | — | — | N2 ¥39,000 (~$6,200); Bumi < $1,400 [U] | U | mikekalil.com; Humanoids Daily |

---

### 2. Per-robot detail

#### 2.1 Unitree G1 and G1 EDU

**Robot-level facts [V]** (https://www.unitree.com/g1/, read 2026-09-24):
- Size 1.32 m × 0.45 m × 0.20 m: "1320x450x200mm". Mass: "About 35kg About 35kg+" (G1 / EDU). DOF: "23 23 - 43"; 6 per leg ("Single Leg Degrees of Freedom 6 6").
- Knee: "Maximum Torque of Knee Joint【1】 90N.m 120N.m". Footnote: "This is the maximum torque of the largest joint motor among them."
- Motor: "Low inertia high-speed internal rotor PMSM". Bearing: "Industrial grade crossed roller bearings (high precision, high load capacity)".
- "Full Joint Hollow Electrical Routing YES YES"; "Joint Encoder Dual encoder Dual encoder"; "Cooling System Local air cooling".
- Leg length: "Calf + Thigh Length 0.6M". Battery: "13 string lithium battery", "9000mAh", "About 2h".
- Price: "Price(Tax and Shipping cost excluded) US $13.5K Contact sales".
- Secondary price reports [U]: AGILOped paper Table I gives "16K (non-programmable) -35K (for developers)" (arXiv 2509.09364). The ToddlerBot paper Table 1 lists G1 at "57K" (arXiv 2502.00893).

**Per-joint actuators [V]**, from Unitree's own RL code (https://github.com/unitreerobotics/unitree_rl_lab, files `assets/robots/unitree.py` and `unitree_actuators.py`, main branch) and URDF (https://github.com/unitreerobotics/unitree_ros, `robots/g1_description/g1_29dof_rev_1_0.urdf`):

| Joint (per side) | Unitree actuator (code name) | URDF effort N·m / vel rad/s | Actuator T-N model (code): Y1 motoring peak / Y2 braking peak N·m; X1 knee point / X2 no-load rad/s | Gear stages in code comment → ratio [E] |
|---|---|---|---|---|
| Hip pitch | N7520-14.3 | 88 / 32 | 71 / 83.3; 22.63 / 35.52 | 4.5 × (48/22+1) = 14.32 |
| Hip roll | N7520-22.5 | 139 / 20 | 111 / 131; 14.5 / 22.7 | 4.5 × 5.0 = 22.5 |
| Hip yaw | N7520-14.3 | 88 / 32 | as hip pitch | 14.32 |
| Knee | N7520-22.5 | 139 / 20 | 111 / 131; 14.5 / 22.7 | 22.5 |
| Ankle pitch + roll | 2× N5020-16 in parallel linkage ("N5020-16-parallel") | 35 / 30 (URDF); 50 / 37 (mimic cfg, 2× armature) | per motor 24.8 / 31.9; 30.86 / 40.13 | (46/18+1) × (56/16+1) = 16.0 |
| Waist yaw | N7520-14.3 | 88 / 32 | — | 14.32 |
| Waist roll/pitch (EDU) | N5020-16 | 35 / 30 | — | 16.0 |
| Shoulder ×3, elbow, wrist roll | N5020-16 | 25 / 37 | 24.8 / 31.9 | 16.0 |
| Wrist pitch/yaw (EDU 29-DOF) | W4010-25 | 5 / 22 | 4.8 / 8.6; 15.3 / 24.76 | 5 × 5 = 25 |

Code and URDF snippets [V]:
- `"N7520-22.5": ImplicitActuatorCfg(joint_names_expr=[".*_hip_roll_.*", ".*_knee_.*"]`
- `"N5020-16-parallel": ImplicitActuatorCfg(joint_names_expr=[".*ankle.*"]`
- N7520_22p5 class: `Y1 = 111.0`, `Y2 = 131.0`, `X1 = 14.5`, `X2 = 22.7`; comment `| gear_1 | ... | ratio | 4.5` and `| gear_2 | ... | ratio | 5.0`
- N7520_14p3 class: `Y1 = 71`, `Y2 = 83.3`; comment `| gear_2 | 0.533e-4 kg·m² | ratio | 48/22+1`
- N5020_16 class: `Y1 = 24.8`, `Y2 = 31.9`; comments `ratio | 46/18+1` and `ratio | 56/16+1`
- W4010_25 class: `Y1 = 4.8`, `Y2 = 8.6`
- URDF knee: `<limit lower="-0.087267" upper="2.8798" effort="139" velocity="20"/>`; hip pitch: `effort="88" velocity="32"`; ankle pitch: `effort="35" velocity="30"`
- Mimic cfg feet: `effort_limit_sim=50.0` with `armature=2.0 * ARMATURE_5020`

Other derived facts:
- URDF total link mass [E]: 33.34 kg (29-DOF), 32.11 kg (23-DOF). The web page says ~35 kg.
- Reducer type [E/U]: the second-stage ratio is written as "48/22+1", which is the planetary 1+Zring/Zsun form. That suggests planetary stages but is an inference. A teardown article [U] (https://humanoid.guide/unitree-g1-teardown-reveals-actuator-and-cooling-tradeoffs/, dated 2026-09-13, based on Munro Live) also describes two-stage planetary gearboxes. It says knee heat pipes move heat that "vaporizes at the hot end and condenses against cooler aluminum section".
- Anecdote [U] (Hacker News, https://news.ycombinator.com/item?id=44023680): "The motors in the humanoid (G1) overheat after shaking hands a few times".

**Why Unitree chose this (stated rationale) [V]:** the page's own parentheticals say "better response speed and heat dissipation" for the inner-rotor PMSM, and "high precision, high load capacity" for the crossed-roller bearings.

**Inconsistency to note:** the knee has four different "maximum" values in Unitree's own sources:
- 90 N·m (G1 web)
- 120 N·m (EDU web)
- 111 N·m motoring / 131 N·m braking (T-N model)
- 139 N·m (URDF)

JX1 should compare actuators on T-N curves, not on "max torque".

#### 2.2 Unitree H1 / H1-2 (full-size reference)

[V] https://www.unitree.com/h1/ (read 2026-09-24):
- H1: "Height about 180CM Weight about 47kg"; "Peak Torque Density 189N.m/Kg"; "Unitree M107 Joint Motor".
- H1 legs: "5（Hip × 3 + Knee × 1 + Ankle × 1）". H1-2 legs: "6（Hip x 3 + Knee x 1 + Ankle x 2）". H1-2: "Height about 178CM Weight about 70kg"; 27 DOF.
- H1 torques: "Knee Torque About 360N.m，Hip Joint Torque About 220N.m"; "Ankle Torque About 59N.m，Arm Joint Torque About 75N.m".
- H1-2 torques: "Waist Joint About 220N.m, Ankle Joint About 75x2N.m"; arms "Shoulder: About 120N.m, Elbow: About 120N.m Wrist: About 30N.m".

| Joint | Web "ultimate" torque | URDF H1 effort/vel [V] | URDF H1-2 effort/vel [V] | unitree_rl_lab sim group [V] |
|---|---|---|---|---|
| Knee | ~360 | 300 / 14 | 300 / 14 | "M107-24-1" effort 300, vel 14 |
| Hip ×3 | ~220 | 200 / 23 | 200 / 23 | "M107-24-2" effort 200, vel 23 |
| Torso | ~220 (H1-2) | 200 / 23 | 200 / 23 | M107-24-2 |
| Ankle | ~59 (H1); ~75×2 (H1-2) | 40 / 9 | pitch 60 / 9; roll 40 / 9 | "GO2HV-1" 40 / 9 |
| Shoulder P/R | ~75 / ~120 | 40 / 9 | 40 / 9 | GO2HV-1 |
| Shoulder Y, elbow | ~75 / ~120 | 18 / 20 | 18 / 20 | "GO2HV-2" 18 / 20 |

- M107 T-N classes [V]: `UnitreeActuatorCfg_M107_24`: `Y1 = 240`, `Y2 = 292.5`, `X1 = 8.8`, `X2 = 16`. `M107_15`: `Y1 = 150.0`, `Y2 = 182.8`.
- M107 mass [E]: 360 / 189 = 1.9 kg, if the 189 N·m/kg density refers to the 360 N·m motor.
- The H1-2 URDF arm limits (40/18) are far below the web figure (~120). The URDF is probably outdated [E].

#### 2.3 Unitree R1 (closest commercial analogue to JX1)

[V] https://www.unitree.com/R1 (read 2026-09-24):
- Price: "R1 AIR $4,900 R1 $5,900 R1 EDU Contact Sales".
- Size and mass: "1230x357x190mm"; "About 27kg About 29kg About 29kg".
- DOF: "20 26 26-40"; "Single Leg Degrees of Freedom 6 6 6".
- Bearings: "Crossed roller bearings, Double Hook Ball Bearings". Encoders: "Dual + single encoder". Routing: "Hollow + Internal Routing".
- Range: "Knee Joint：-10°~+139°". Leg: "Calf + Thigh Length 600" (mm). Battery: "Battery Life About 1h".

URDF [V] (https://github.com/unitreerobotics/unitree_ros `robots/r1_description/R1.urdf` and `r1_air_description/R1_AIR.urdf`):

| Joint (per side) | URDF effort N·m / vel rad/s | Snippet |
|---|---|---|
| Hip pitch, hip roll, hip yaw | 60 / 18.8 | hip pitch: `effort="60" velocity="18.8"` |
| Knee | 60 / 18.8 | `<limit lower="-0.174532925" upper="2.42600766" effort="60" velocity="18.8"/>` |
| Ankle pitch, ankle roll | 50 / 30 | `upper="0.57596" effort="50" velocity="30"` |
| Waist roll, yaw (R1, EDU) | 60 / 18.8 | — |
| Shoulder pitch, roll | 60 / 18.8 | — |
| Shoulder yaw, elbow, wrist roll | 33 / 33.4 | — |
| Head pitch/yaw | 33 / 33.4 | — |

- URDF link-mass sums [E]: R1 28.84 kg, R1 AIR 26.68 kg. These match the web values of 29 and 27 kg.
- Motor names, gear ratios and actuator peak curves for R1 are **not published** (GAP).
- Interpretation [E]: the R1 mixes crossed-roller and "double hook" (deep-groove) ball bearings, and dual and single encoders. It appears to have been cost-reduced relative to the G1, which has crossed-roller bearings and dual encoders on every joint.

#### 2.4 Berkeley Humanoid Lite (UC Berkeley, RSS 2025, arXiv 2504.17249)

Primary sources: paper https://arxiv.org/html/2504.17249 (v1, 24 Apr 2025); docs https://berkeley-humanoid-lite.gitbook.io/docs; code https://github.com/HybridRobotics/berkeley-humanoid-lite (plus `-assets` and `-lowlevel`); firmware https://github.com/T-K-233/Recoil-Motor-Controller-BESC. All read 2026-09-24.

**Robot [V]:**
- "The robot weighs 16 kg and stands 0.8 m tall."
- "keeping the total hardware cost under $5,000"
- "An Intel N95 mini PC"; "1 Mbps CAN 2.0 bus"; "four buses"; "configured to be 250 Hz"
- "6S 4000 mAh Lithium Polymer (LiPo) battery", "approximately 30 minutes"
- 22 joints: 10 arm and 12 leg (docs "Joint ID Mapping"; `policy_humanoid.yaml`: `num_joints: 22`).

**Actuators [V]:**
- 6512 actuator: "M6C12 150KV BLDC drone motor from MAD Components" + "B-G431B-ESC1 as the motor driver" + AS5600 encoder. BOM "Total $188 $157" (US/China).
- 5010 actuator: 5010 drone motor; BOM "Total $136 $94".
- Robot BOM: "6512 Actuators (10x) $1,880 $1,563 5010 Actuators (12x) $1,632 $1,130"; "Total $4,312 $3,236".
- Gear ratio 15:1. motor_configuration.json has `"gear_ratio": -15.0`; the docs compute reflected inertia with "× 15^2".
- Motor constants (docs "Motor Characterization"): M6C12 Kt 0.0919 N·m/A, 5010 110KV Kt 0.1176 N·m/A. Reflected rotor inertia: "0.0224" and "0.00743" kg·m².
- Firmware: Recoil ("Recoil Motor Controller Firmware for B-G431B-ESC1"). The joint torque limit is applied at the output: current = `torque_setpoint / controller->motor.torque_constant / controller->position_controller.gear_ratio`.

**Per-joint mapping [E]**: inferred from the per-joint torque constants in `robot_configuration.backup.json`. Joints with Kt 0.0919 use M6C12/6512; joints with Kt 0.1176 use 5010. The result matches the BOM counts of 10× 6512 and 12× 5010.

| Joint (per side) | Actuator | Deployed joint torque limit (N·m) [V] | Range (docs) [V] |
|---|---|---|---|
| Hip roll, hip yaw, hip pitch | 6512 | 6.0 (`"torque_limit": 6.0`) | hip pitch [-108.75, 56.25]° |
| Knee pitch | 6512 | 6.0 | "[0, 140]" |
| Ankle pitch, ankle roll | 5010 | 6.0 | [-45, 45], [-15, 15]° |
| Shoulder pitch | 6512 | 1.0–2.0 | — |
| Shoulder roll, shoulder yaw, elbow, wrist/elbow-yaw | 5010 | 1.0–2.0 | — |

- The Isaac Lab training config uses `effort_limit=6, velocity_limit=10.0` for legs and `effort_limit=4` for arms [V].
- The released low-level code sets `self.torque_limit[:] = 4` in `enter_damping` [V].
- Firmware current limit: `"i_limit": 20.0` [V].
- **Actuator peak torque is not published** (GAP). Upper bounds from the current limit [E]:
  - 6512: 0.0919 N·m/A × 20 A × 15 = 27.6 N·m ideal; ×0.9 efficiency ≈ 24.8 N·m.
  - 5010: 0.1176 × 20 × 15 = 35.3 N·m ideal. Thermal capacity of a 5010 drone motor at 20 A was not characterized.
- A "20 Nm peak" figure appears in search-engine summaries but could not be found in any source; treat it as unconfirmed.

**Test results [V]:**
- "mechanical efficiency of approximately 90% across most operating conditions"
- "stiffness of approximately 319.49 Nm/rad". A PA-CF printed reducer by Roozing measured "about 1468 Nm/rad".
- "60-hour durability test": backlash "progressively increases due to wear". "The maximum observed backlash was 0.0229 rad".
- Torque tracking "within ±0.5 N m" across six units from two printers.
- Walking: "utilized only 30% of the actuator's torque limit".

**Why they chose printed cycloidal [V]:**
- Cycloids "distribute loads over multiple teeth and accommodate the limited resolution of desktop 3D printers" better than planetary gears.
- On servos: they "typically lack backdrivability and exhibit high reflected inertia".
- On the driver: B-G431B-ESC1 was chosen "favoring its affordability and ready availability".

**What went wrong or is open [V]:**
- "insufficient study of thermal effects on the 3D-printed structure"
- Docs warning: "The CAN port solder pads on the ECS are *very fragile*".

#### 2.5 ToddlerBot (Stanford, arXiv 2502.00893 v4; v2.0 released 2025-08-25)

Robot [V] (https://arxiv.org/html/2502.00893v4):
- "compact size ( 0.56 m, 3.4 kg )"
- "total cost under 6,000 USD"
- "90% of the cost is for motors and computers"
- 30 active DoFs: "7 per arm, 6 per leg, a 2 on neck, and a 2 on waist". Compute: Jetson Orin NX 16GB.

Per-joint motors [V] (paper Table 2 stall torque at 12 V; Table 3 system-ID values):

| Joint | Dynamixel model | Stall torque N·m (Table 2) | SysID τmax N·m (Table 3) | SysID q̇max rad/s |
|---|---|---|---|---|
| Neck pitch/yaw, waist roll/yaw, hip yaw, gripper | XC330-T288 | 1.0 | 0.76 | 6.50 |
| Hip roll + pitch (dual-axis unit) | 2XC430-W250 | 1.8 | 1.09 | 6.78 |
| Knee pitch, ankle pitch | XM430-W210 | 3.0 | 1.61 | 7.63 |
| Ankle roll, shoulder pitch | XC430-T240BB | 1.9 | 1.32 | 7.00 |
| Shoulder roll+yaw, elbow roll+yaw, wrist roll+pitch | 2XL430-W250 | 1.5 | 0.94 | 5.97 |

- Table 2 snippets: "XM430-W210 3.0 Knee P, Ankle P"; "2XC430-W250 1.8 Hip RP"; "XC330-T288 1.0 Neck PY".
- Table 3 snippet: "τ max 0.94 0.76 1.32 1.09 1.61".
- Their torque requirement estimate [V]: "estimated height of 0.5 m and weight of 3.1 kg". Knee = 2.35, ankle pitch = 2.66, hip pitch = 1.77 N·m.
- Usable torque vs stall [E]: 1.61/3.0 = 54% (XM430), 76% (XC330), 69% (XC430), 61% (2XC430), 63% (2XL430). The knee's usable 1.61 N·m is below the 2.35 N·m requirement they estimated for the most demanding tasks.

Rationale [V]:
- "We choose Dynamixel motors because of their robustness, reliability, and accessibility."
- "Brushless Direct Drive (BLDC) motors are not a viable option" at their 30-DoF, 0.56 m size.
- Linear actuators were rejected for "insufficient power density and low control frequency".
- "XM430 is the only option that provides sufficient torque for the knee".
- The waist uses two XC330 through bevel gears because "a single Dynamixel XC330 lacks the power to drive the entire upper body".
- Backlash "about 0.25°, on par with most QDD joints".

Limitations and failures [V]:
- Endurance best streak was 19 minutes. "increased motor temperatures gradually pushed it outside the policy's training distribution".
- "ToddlerBot withstands up to 7 falls before breaking"; a repair took 21 min of printing plus 14 min of assembly.
- "passive-active ratio to be 3, equating gearbox torque efficiency around 58%"
- Agility is "constrained by the off-the-shelf motors' max speed, max torque, and communication speed".
- Sensing: "Dynamixel motors lack an absolute zero point", so calibration jigs are needed.

v2.0 changes [V] (https://github.com/hshi74/toddlerbot CHANGELOG.md):
- "Dual hip motor options (2XC430 or 2XM430-W350)"; "`toddlerbot_2xm`: Upgraded hip and arm motors"
- "Control frequency: 50Hz → **200Hz**" (C++ rewrite)
- "Simplified knee design (removed parallel links)"

#### 2.6 K-Scale Labs K-Bot

Actuators [V] (https://github.com/kscalelabs/docs, `docs/robots/k-bot/mechanical.md`, master; the rendered site docs.kscale.dev no longer resolves). The docs table:

| Robstride model | Count | Rated | Peak (10 s) | Mass | Ratio | Snippet |
|---|---|---|---|---|---|---|
| RS00 | 2 | 5 | 14 | 0.31 kg | 10:1 | "Robstride RS00 \| 2 \| 5 Nm \| 14 Nm \| 0.31 kg \| 10:1" |
| RS02 | 6 | 6 | 17 | 0.38 kg | 7.75:1 | "Robstride RS02 \| 6 \| 6 Nm \| 17 Nm \| 0.38 kg \| 7.75:1" |
| RS03 | 8 | 20 | 60 | 0.88 kg | 9:1 | "Robstride RS03 \| 8 \| 20 Nm \| 60 Nm \| 0.88 kg \| 9:1" |
| RS04 | 4 | 40 | 120 | 1.42 kg | 9:1 | "Robstride RS04 \| 4 \| 40 Nm \| 120 Nm \| 1.42 kg \| 9:1" |

- Torque density [E]: RS04 120/1.42 = 84.5 N·m/kg; RS03 68.2; RS02 44.7; RS00 45.2.
- Peak-to-rated ratio is about 3:1 for all four models.

Per-joint [V] (URDF https://github.com/kscalelabs/kbot-models `kbot/robot.urdf` and `kbot/metadata.json`, master):

| Joint (per side) | Model | URDF effort / vel | Soft torque limit (metadata) |
|---|---|---|---|
| Hip pitch | RS04 | 120 / 17.488 | 84.0 |
| Knee | RS04 | 120 / 17.488 (`<limit effort="120" velocity="17.488" lower="0" upper="2.705260"/>`) | 84.0 |
| Hip roll, hip yaw | RS03 | 60 / 18.849 | 42.0 |
| Ankle (pitch only; legs are 5-DOF) | RS02 | 17 / 37.699 | 11.9 |
| Shoulder pitch, roll | RS03 | 60 / 18.849 | 42.0 |
| Shoulder yaw, elbow | RS02 | 17 / 37.699 | 11.9 |
| Wrist | RS00 | 14 / 27.227 | 9.8 |

- Soft limits are exactly 70% of peak [E: 84/120, 42/60, 11.9/17, 9.8/14].
- The docs joint list names the ankle "dof_left_ankle_00", but the URDF and metadata say `robstride_02`. The count table (RS02 ×6) supports RS02 [E].
- Robstride command ranges in K-Scale's driver [V] (https://github.com/kscalelabs/robstride `src/actuator_types.rs`):

  | Model | Torque range N·m | Velocity range rad/s |
  |---|---|---|
  | RS00 | ±14 | ±33 |
  | RS02 | ±17 | ±44 |
  | RS03 | ±60 | ±20 |
  | RS04 | ±120 | ±15 |

  RS04 snippet: `torque: Range { min: -120.0, max: 120.0 }`.
- Docs: "uses a specific motor ID mapping for its 20 degrees of freedom".
- Power: 48 V CAN harness; "12 AH NCM battery"; BMS limit 50 A.
- URDF link-mass sum [E]: 36.7 kg.

Size, price and status [U]:
- DesignSpark: "about 4 feet 7 inches (1.4 m) tall", "77 pounds (34 kg)", "$8,999 for the first 100 units".
- Shutdown: Humanoids Daily (https://www.humanoidsdaily.com/news/k-scale-labs-cancels-k-bot-orders-open-sources-all-ip-after-funding-fails) says orders were cancelled and refunded, with CEO quote "I have not been able to find a lead investor".
- IP release: "all of K-Scale's proprietary IP, including the hardware and software for the K-Bot". Licenses: "hardware under CERN-OHL-S-2.0, software under MIT".
- The announcement was in early November 2025 [U].

Lessons stated by K-Scale [V]:
- Wiring harness: "it is still the least reliable part of the robot".
- They customized "the RS03 and RS04 actuators as we find the default CAN plug to be unsuitable".
- On Hacker News [U], K-Scale's founder wrote: "Vast majority of BOM is actuators".

#### 2.7 K-Scale Zeroth-01 / Z-Bot

- Zeroth-01 BOM [V] (https://github.com/kscalelabs/docs `docs/robots/zeroth-01/bom.md`): "STS3250 50KG Serial Bus Servo" × "x16".
- Lesson [V]: "The STS3215 45RPM servos are no longer sufficient for the speed requirements of the legs."
- README [V] (https://github.com/kscalelabs/zeroth-bot): "BoM starts at $350".
- Feetech official specs [V] (https://www.feetechrc.com/products/serial-port-series-steering-gear-page-3 and page-4):
  - STS3250: "The Stall Torque：50kg.cm@12V" ≈ 4.90 N·m [E: 50 × 0.0981]; "The Maximum Speed：0.133sec/60°@12V" ≈ 7.9 rad/s ≈ 75 rpm [E]; "Product Weight：74.5± 1g".
  - STS3215-C018: "The Stall Torque：30kg.cm@12V" ≈ 2.94 N·m [E]; "0.222sec/60°@12V" ≈ 45 rpm [E].
- Z-Bot URDF [V] (https://github.com/kscalelabs/kscale-assets `zbot/robot.urdf`): 18 joints (5/leg: hip yaw/roll/pitch, knee, ankle; 4/arm incl. gripper). Link-mass sum 3.75 kg [E]. URDF efforts are placeholders (`effort=2`).
- Size [U] (ToddlerBot paper Table 1, secondary): "Zeroth [24] 0.48 3.6 0.01 16 ... 1.4K".

#### 2.8 Booster Robotics T1

Official page [V] (https://www.booster.tech/booster-t1/, read 2026-09-24):
- "Dimensions: 118×47×23 cm", "Leg Length: 57cm", "Weight: ~30kg"
- "Total DoFs: 23", "DoFs per Leg: 6", "Waist DoF: 1", "DoFs per Arm: 4 (extensible)", "Head DoFs: 2"
- "Knee: 0°~123°"
- "Max Peak Torque: 130N·m", "Joint Encoder: Dual Encoder"
- "Battery: 10.5Ah"
- Marketed as the "2025 RoboCup "AdultSize" Category Champion Model!"

The official store page is only an inquiry form; no price is published [V]. Price [U]: ToddlerBot Table 1 "Booster T1 [14] 1.18 30.0 3.33 23 ... 34K"; AGILOped Table I "Booster T1 ... 120 30 34K". Other listings disagree:
- botinfo.ai search-result title: "Buy Booster T1 Robot - $33,949"
- humanoid.guide lists "75 000 USD"

Actuator supplier and model: **not disclosed** anywhere I could read (GAP). A RoboCup team spec sheet [U] says only "High-torque Brushless DC Motors" and "Dual-encoder (Absolute + Incremental)".

Per-joint torque limits [V] from two official Booster repos. Both are main branch, read 2026-09-24: https://github.com/BoosterRobotics/booster_assets `robots/T1/T1_23dof.urdf` and https://github.com/BoosterRobotics/booster_gym `resources/T1/T1_serial.urdf`.

| Joint (per side) | booster_assets effort / vel | booster_gym (RL) effort / vel |
|---|---|---|
| Hip pitch | 98.8 / 15.29 | 45 / 12.5 |
| Hip roll | 68 / 14.66 | 30 / 10.9 |
| Hip yaw | 68 / 14.66 | 30 / 10.9 |
| Knee | **130.5 / 14.76** (`effort="130.5" velocity="14.76"`) | **60 / 11.7** (`effort="60" velocity="11.7"`) |
| Ankle pitch | 73.1 / 12.57 | 20 / 18.8 (serial); 24 (locomotion URDF) |
| Ankle roll | 17.2 / 12.57 | 15 / 12.4 |
| Waist yaw | 68 / 14.66 | 30 / 10.88 |
| Shoulder P/R, elbow P/Y | 38.3 / 17.59 | 18 / 18.84 |
| Head yaw/pitch | 7 / 41.89 | 7 / 12.56 |

- URDF link-mass sums [E]: 31.7 kg (assets) and 31.6 kg (gym).
- The assets repo ships `T1_23dof_parallel.xml`, which suggests a parallel-linkage ankle [E].
- The effort values fall into about four torque classes (≈17, 38, 68, 99–131 N·m). This suggests a small family of actuator sizes [E].

#### 2.9 Booster Robotics K1

Official [V]:
- https://www.booster.tech/booster-k1/: "Weighs only 19.5 kg, stands 95 cm tall"; "Total DoFs: 22"; "Max Peak Torque: 60N·m"; "Joint Encoder: Dual Encoder"; "RoboCup 2025 KidSize champion".
- Manual (https://docs.booster.tech/docs/product-manual/k1/getting-started/specifications/): "Walking Speed 1.1m/s"; battery "20min（1.1m/s）" (2 Ah) / "1h10min（1.1m/s）" (5 Ah); safety "Low Battery Alert, Joint Overheat Alert". The ankle is listed as "Left Ankle Up Joint" / "Left Ankle Down Joint", which suggests a parallel ankle [E].
- booster_assets `robots/K1/K1_22dof.urdf` [V]:
  - Knee `effort="112.0" velocity="12.57"`
  - Hip pitch 68 / 14.66; hip roll 43 / 12.57; hip yaw 38.3 / 17.59
  - Ankle pitch/roll 38.3 / 17.59
  - Arms 14 / 33.51; head 6 / 7.85
  - Link-mass sum 19.67 kg [E]
- **Conflict**: the URDF knee value of 112 N·m exceeds the web "Max Peak Torque: 60N·m". A knee linkage ratio could explain it, but that is unconfirmed (GAP).
- Price [U] (Humanoids Daily, 2025-10-21): "$4,999 USD" starting price.

#### 2.10 Poppy Humanoid (INRIA Flowers / Poppy Project)

Robot [V]:
- Website https://www.poppy-project.org/en/robots/poppy-humanoid/: "Poppy Humanoid v1.0.2 Size: 83cm Mass: 3.5kg"; "25 actuators".
- README https://github.com/poppy-project/poppy-humanoid: "costs $8000-9000 with about 60% for buying the 25 Robotis Dynamixel actuators".
- Paper, Lapeyre et al., Humanoids 2014 (https://flowers.inria.fr/PoppyHumanoids2014.pdf): v0.1 "21 x MX-28 - 2 x MX-64 - 2 x AX-12", "7500 €", "light structure with 3.5kg for 84cm height".

Per-joint [V] (current software config `software/poppy_humanoid/configuration/poppy_humanoid.json`, master). Counts: 19× MX-28, 4× MX-64, 2× AX-12.

| Joint | Motor | Stall torque @12 V; no-load speed; ratio (Robotis e-manual) [V] |
|---|---|---|
| Hip roll (hip_x), hip yaw (hip_z), knee (knee_y), ankle pitch (ankle_y) | MX-28 | "2.5 [N.m] (at 12 [V], 1.4 [A]"; "55 [rev/min] (at 12 [V])" ≈ 5.8 rad/s [E]; "Gear Ratio 193 : 1" |
| Hip pitch (hip_y) | MX-64 | "6.0 [N.m] (at 12 [V], 4.1 [A]"; 63 rpm; "Gear Ratio 200 : 1" |
| Abdomen abs_x, abs_y | MX-64 | as above |
| abs_z, bust_x, bust_y; all arm joints (shoulder_y/x, arm_z, elbow_y) | MX-28 | as above |
| Head yaw/pitch | AX-12 | "1.5 [N.m] (at 12 [V], 1.5 [A])"; "Gear Ratio 254 : 1" |

- Legs are 5-DOF (no ankle roll). Config snippets: `"l_knee_y"` → `"type": "MX-28"`; `"l_hip_y"` → `"type": "MX-64"`.
- Stated design choices [V]:
  - It is "slightly under-actuated, prevents it from destructing itself if wrong moves occur".
  - "initial design of Poppy's feet only had one degree of freedom".
  - A passive spring ankle roll behaved better than an active 2-DOF ankle in a stepping test.
  - Experiments used a safety "slack strap on a fixed gantry".
- Outcome [V] (arXiv 2608.26505, Chen et al., 27 Aug 2026): the authors are "unaware of any published methodology that achieves reliable, unassisted bipedal locomotion" on standard Poppy hardware.

#### 2.11 AGILOped (University of Bonn, arXiv 2509.09364, Sept 2025)

Primary source [V]: https://arxiv.org/html/2509.09364.
- "With a height of 110 cm and weighing only 14.5 kg"
- "10 × MyActuator RMD X6-40": "18 Nm (Rated), 40 Nm (Peak)"; "No load speed (48V) 11.5 rad/s"
- "X6-40 compensates for this by a 1:36 planetary gearbox" (two-stage)
- Cost: "Actuators 10 × 545"; "Total 6,380". Actuators are 85% of the total [E: 5,450/6,380].

Architecture [V]:
- "With only 10 actuators controlling 12 joints".
- Legs: "four collocated actuators: three at the hip (yaw, roll, pitch) and one at the knee". Double 4-bar parallelograms give a passive ankle and a knee torque shared by two actuators.
- Table I: "AGILOped (ours) 110 14.5 6.5K ... 40 80" (max hip / knee N·m).

Rationale [V]:
- Unitree A1 actuators' "cost is roughly double that of the X6-40". They give "only 80 % of its peak torque".
- The motors "have absolute position encoders only on the motor shaft", so a calibration pose is needed.
- Performance limit: "we can reliably achieve jumps of only about 10 cm".

#### 2.12 Optional robots at 0.75–1.4 m (quick scan)

- **HighTorque Mini Pi+** [V] (https://www.hightorquerobotics.com/mini-pi): "75.6 cm tall, 15 kg"; "21 Nm peak torque, 23/27 DOF"; "Motors: Peak Torque 21Nm with Dual Encoders". Vendor range: "11 servo variants (2-20 Nm, ratio 7-36)".
- **AgiBot X2** [V] (https://www.agibot.com/products/X2): "Height Approx.1.31 m"; "Weight Approx.35kg Approx.39kg"; "Total Degrees of Freedom 25 30"; "Leg DOF (per leg) 6 6"; "Peak Joint Torque 120N·m". Actuators and price not disclosed.
- **EngineAI PM01, 2026 edu** [V] (https://www.engineai.com.cn/product-pm01.html, Chinese page):
  - "1400(H) x 540(W) x 295(D)mm"; "约44.5kg"; "总自由度(关节电机数） 24"
  - "最大力矩[1] 164 N·m"; "峰值扭矩密度[1] 145 Nm/kg"
  - "工业级高精度交叉滚子轴承" (crossed-roller bearing); intro "峰值扭矩高达130N·m"
  - The homepage gives "138CM" for an earlier spec. Price not verified; The Robot Report [U] gave 1.38 m, "about 40 kg" in Dec 2024.
- **Fourier N1** [U] (https://www.humanoidsdaily.com/news/fourier-intelligence-launches-n1-humanoid-robot-with-open-source-strategy): "1.3 meters tall and weighs 38 kilograms". Joint torques not verified; the official page is JS-only.
- **Noetix N2** [U] (https://mikekalil.com/blog/noetix-robotics-n2/): "Standing 1.3 meters", "It weighs 20 kg", "18 degrees of freedom", "up to 120 Nm of peak torque", "starting at 39,000 yuan ($6,200)". Other listings seen in search give 1.18 m / 30 kg / 150 N·m; conflicting and not fetched.
- **Noetix Bumi** [U] (https://www.humanoidsdaily.com/news/chinas-noetix-robotics-prices-bumi-humanoid-under-1400): "94 cm tall", "12 kg"; headline "Under $1,400". No actuator data.

---

### 3. Lessons for JX1: why teams chose what they chose, and what went wrong

1. **The real price and spec anchor is Unitree R1.** It is 1.23 m, 27–29 kg, 20–26 joints, and sells for $4,900–$5,900 [V].
   - Its URDF gives every hip and knee joint **60 N·m @ 18.8 rad/s** and the ankles 50 N·m @ 30 rad/s [V].
   - That is knee ≈ 0.17–0.18 × m·g·h [E: 60/(29·9.81·1.23) = 0.171].
   - Booster T1 (1.18 m, 30 kg) trains its RL walking policy with the same **60 N·m knee** limit in booster_gym [V]. The ratio is 0.173 [E].
   - For JX1, 60 N·m-class knees are the proven floor for a ~30 kg, ~1.2 m RL-walking robot. At 25 kg the same ratio gives ~50 N·m [E].

2. **Commercial robots carry 1.5–2.2× headroom above the RL-walking floor.** It is used for get-up, pushes and dynamic motions.
   - G1 knee: 90 (web) / 120 (EDU) / 139 (URDF) N·m, i.e. 0.20–0.31 m·g·h [E].
   - Booster T1: 130 N·m (web) = 0.37 [E].
   - K-Bot: 120 N·m (RS04) = 0.26 [E]; it only commands 84 N·m (70% soft limit) [V].
   - Robstride peak:rated is about 3:1 (RS03 60/20, RS04 40/120) [V].
   - For JX1, specify both a peak (0.2–0.3 m·g·h ≈ 60–90 N·m at 25–30 kg) and a continuous rating (≈ one third of peak) [E].

3. **Hobby servos do not scale to a walking ~1 m robot; BLDC plus a low-ratio reducer does.**
   - Poppy (84 cm, 3.5 kg, MX-28 knee at 2.5 N·m stall) still has no published reliable unassisted walking after about 12 years [V, arXiv 2608.26505].
   - K-Scale had to replace STS3215 (45 rpm) with STS3250 because the legs were too slow [V].
   - ToddlerBot's knee XM430 delivers only 1.61 N·m usable against the 2.35 N·m it needed, and v2.0 upgraded the hip motors [V].
   - BHL says servos "lack backdrivability and exhibit high reflected inertia" [V].
   - Every ≥0.8 m robot here that walks under RL uses BLDC with a low ratio:
     - Unitree 14.3–25:1, two-stage
     - Robstride 7.75–10:1
     - BHL 15:1 cycloidal
     - AGILOped 36:1 planetary

4. **Derate every datasheet "peak".** The same actuator shows 54–76% usable torque in system-ID tests, and makers publish several "max" numbers for one joint.
   - ToddlerBot's system ID found usable τmax of only 54–76% of Dynamixel stall torque. The effective gearbox efficiency was ~58% [V/E].
   - Unitree's own knee motor model gives 111 N·m motoring and 131 N·m braking, while its URDF says 139 and its web page says 90 or 120 [V].
   - Buy and compare JX1 actuators on a **T-N curve**, not a single number. Unitree's code uses this format:
     - Y1 motoring peak at speed
     - Y2 braking peak
     - X1 full-torque knee-point speed
     - X2 no-load speed
   - Add a continuous (thermal) torque rating to that comparison.

5. **Heat, not peak torque, limits low-cost robots in practice.**
   - ToddlerBot's best endurance was 19 min, and rising motor temperature pushed the policy out of distribution [V].
   - BHL lists thermal effects as unstudied [V].
   - Booster K1 ships a "Joint Overheat Alert" [V]. G1 uses local air cooling [V], with reported knee heat pipes and fans [U] and user reports of overheating [U].
   - Size JX1 knees and hips on RMS or continuous torque over a gait cycle, and design heat paths (aluminium housings, airflow) from day one.

6. **Printed-plastic cycloidal is proven only at small scale.**
   - The BHL 15:1 PLA cycloid gives ~90% mechanical efficiency, 319 N·m/rad stiffness, ≤0.0229 rad backlash, 60 h durability, at $94–188 per actuator [V].
   - But the robot walked with joint limits of only 4–6 N·m, at 30% utilization [V].
   - The theoretical output is ≤ ~25–28 N·m [E].
   - A 60–90 N·m JX1 knee is about 2–4× the theoretical maximum of the BHL 6512 and 10–15× its deployed limit [E: 60/28 ≈ 2.1, 90/25 = 3.6; 60/6 = 10, 90/6 = 15]. JX1 knees and hips should use metal gearing, or at least PA-CF printed parts: a PA-CF reducer measured ~1468 N·m/rad versus 319 for PLA [V, cited in BHL]. Printed cycloids remain a candidate for arms, neck and ankles.

7. **The actuators are the robot's cost.**
   - Share of total cost or BOM:
     - BHL: 81% US / 83% CN [E from V BOM]
     - AGILOped: 85% [E]
     - ToddlerBot: 90% for motors plus computer [V]
     - Poppy: ~60% [V]
     - K-Scale: "Vast majority of BOM is actuators" [U]
   - To undercut the R1 AIR's $4,900 retail with ~20 joints, JX1 actuators must average roughly **$150–200** each. [E: 0.8 × $4,000 BOM / 20 = $160]
   - Reference points: BHL China cost $94–157 per actuator; AGILOped's X6-40 cost $545 [V].

8. **Use linkages and a small actuator family to save cost.**
   - G1 drives each ankle with two 25 N·m N5020-16 motors in parallel (35–50 N·m) [V].
   - T1 and K1 appear to use parallel ankles [E].
   - AGILOped runs 12 joints on 10 actuators and gets an 80 N·m knee from two 40 N·m units [V].
   - ToddlerBot couples two XC330s through a bevel waist [V].
   - G1 (4 SKUs), K-Bot (4 SKUs) and Booster (about 4 torque classes in the URDF) all standardize on 3–4 actuator sizes [V/E].
   - Suggestion for JX1 [E]:
     - L: ~60–90 N·m, for knee and hip pitch
     - M: ~30–60 N·m, for hip roll/yaw and waist
     - S: ~15–25 N·m, for arms and the parallel-ankle pairs

9. **Leg DOF.**
   - K-Bot (single ankle pitch, RS02 at 17 N·m), Poppy and H1 used 5-DOF legs [V].
   - H1-2 moved to 6 DOF with a 75×2 N·m ankle [V].
   - The RL-era compact robots (G1, R1, T1, K1, BHL, X2, PM01) all use 6-DOF legs [V].
   - JX1's 6-DOF spec is consistent with the field.

10. **Encoders and calibration.**
    - Unitree G1, Booster T1/K1 and HighTorque use dual encoders [V]. The R1 uses "Dual + single" [V].
    - Single motor-side encoders force a calibration pose or jig at every power-up or reassembly. AGILOped and ToddlerBot both describe this [V].
    - For JX1, an output-side absolute encoder on at least the leg joints removes homing jigs.

11. **Integration fails before actuators do.**
    - K-Scale: the wiring harness is "the least reliable part of the robot", and they re-plugged RS03/RS04 CAN connectors [V].
    - BHL: ESC CAN pads are "very fragile" [V].
    - ToddlerBot's bus and host software capped control at 50 Hz until a C++ rewrite reached 200 Hz [V].
    - BHL splits the robot across 4 CAN buses at 1 Mbps and 250 Hz [V].

12. **Business lesson.** K-Scale's Robstride-based K-Bot was priced at $8,999 [U] against vertically integrated Unitree, which sells the R1 at $4,900 [V]. K-Scale failed to raise funding and shut down in November 2025, open-sourcing all IP [U]. JX1's cost plan cannot assume retail-priced imported actuators plus margin.

---

### 4. Published torque/speed requirement data usable for sizing JX1 (1.0–1.4 m)

#### 4.1 Human biomechanics (the reference ToddlerBot itself used)

Source [V]: Grimmer, Elshamanhory, Beckerle 2020, Front. Robot. AI 7:13, https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2020.00013/full
- Daily-life joint moments: "a maximum moment of 2.4 Nm/kg for the hip, 1.5 Nm/kg for the knee" and 1.9 N·m/kg for the ankle.
- Power: "A maximum power of 5.8 W/kg, 4.1 W/kg, and 4.3 W/kg" (hip, knee, ankle).
- Speed: "maximum angular velocities of 500°/s for the hip, 550°/s for the knee" and 300°/s for the ankle. That is 8.7 / 9.6 / 5.2 rad/s [E].
- Sportive tasks: "requirements increase with up to 3.1 Nm/kg and 13.8 W/kg at the ankle".

#### 4.2 ToddlerBot scaling law, applied to JX1

Formula [V]: τ_robot = (h_robot·m_robot)/(h_human·m_human) · τ_human, with human reference 1.73 m, 70.9 kg.

ToddlerBot's own result [V] (0.5 m, 3.1 kg): knee 2.35, ankle pitch 2.66, hip pitch 1.77 N·m. The implied human values are 186 / 210 / 140 N·m [E: ÷ (0.5·3.1)/(1.73·70.9) = 0.01264].

JX1 at h = 1.2 m [E: multiply by (1.2·m)/(0.5·3.1)]:

| Joint | m = 20 kg | m = 25 kg | m = 30 kg |
|---|---|---|---|
| Knee | 36.4 | 45.5 | 54.6 |
| Ankle pitch | 41.2 | 51.5 | 61.8 |
| Hip pitch | 27.4 | 34.3 | 41.1 |

Grimmer's per-kg values applied to JX1 [E]:

| Joint | Mass-only scaling (20 / 25 / 30 kg) | With height factor 1.2/1.73 (20 / 25 / 30 kg) |
|---|---|---|
| Hip | 48 / 60 / 72 | 33 / 42 / 50 |
| Knee | 30 / 37.5 / 45 | 21 / 26 / 31 |
| Ankle | 38 / 47.5 / 57 | 26 / 33 / 40 |

These biomechanics-based values sit **below** what commercial robots of JX1's size actually fit (§4.3). Robots carry heavier distal masses, walk with bent knees and need fall recovery.

Speed at equal Froude number [E]: human knee 9.6 rad/s × √(1.73/1.2) = 11.5 rad/s.

#### 4.3 What comparable robots actually fit (normalized)

All ratios [E] = τ / (m·g·h). Source values are [V] unless marked.

| Robot (source of τ) | m kg | h m | m·g·h | Knee N·m | Knee ratio | Hip pitch N·m | Hip ratio | Knee vel rad/s |
|---|---|---|---|---|---|---|---|---|
| Unitree R1 (URDF) | 29 | 1.23 | 349.9 | 60 | 0.171 | 60 | 0.171 | 18.8 |
| Unitree R1 AIR (URDF) | 27 | 1.23 | 325.8 | 60 | 0.184 | 60 | 0.184 | 18.8 |
| Booster T1 (booster_gym RL URDF) | 30 | 1.18 | 347.3 | 60 | 0.173 | 45 | 0.130 | 11.7 |
| Booster T1 (booster_assets URDF) | 30 | 1.18 | 347.3 | 130.5 | 0.376 | 98.8 | 0.285 | 14.76 |
| Booster K1 (web max) | 19.5 | 0.95 | 181.7 | 60 | 0.330 | — | — | — |
| Booster K1 (assets URDF) | 19.5 | 0.95 | 181.7 | 112 | 0.616 | 68 | 0.374 | 12.57 |
| Unitree G1 (web G1 / EDU) | 35 | 1.32 | 453.2 | 90 / 120 | 0.199 / 0.265 | — | — | — |
| Unitree G1 (T-N Y1 model) | 35 | 1.32 | 453.2 | 111 | 0.245 | 71 | 0.157 | 14.5 (knee pt) / 22.7 (no-load) |
| Unitree G1 (URDF) | 35 | 1.32 | 453.2 | 139 | 0.307 | 88 | 0.194 | 20 |
| K-Bot (URDF; m, h [U]) | 34 | 1.40 | 467.0 | 120 (84 soft) | 0.257 (0.180) | 120 | 0.257 | 17.5 |
| AGILOped (paper) | 14.5 | 1.10 | 156.5 | 80 | 0.511 | 40 | 0.256 | 11.5 no-load |
| BHL (deployed/sim limit) | 16 | 0.80 | 125.6 | 6 | 0.048 | 6 | 0.048 | 10 (sim) |
| Unitree H1 (web) | 47 | 1.80 | 829.9 | 360 | 0.434 | 220 | 0.265 | 14 (URDF) |

Other joints (URDF, N·m) for context:

| Joint | Unitree R1 | Unitree G1 | Booster T1 (gym / assets) | K-Bot |
|---|---|---|---|---|
| Hip roll | 60 | 139 | 30 / 68 | 60 |
| Hip yaw | 60 | 88 | 30 / 68 | 60 |
| Ankle | 50 | 35 (2× N5020-16) | pitch 20–24 / 73.1; roll 15 / 17.2 | 17 (pitch only) |
| Arms | 33–60 | 25 | 18 / 38.3 | 11.9–60 |

BHL walked slowly on flat ground under RL with 4–6 N·m limits (ratio 0.048) [V]. So flat walking alone needs far less than the installed peak. The installed headroom is for robustness and whole-body motions.

#### 4.4 Resulting JX1 starting envelope [E]

JX1 knee peak = ratio × m·g·h, at h = 1.2 m:

| Mass | m·g·h | 0.17 (R1 / T1-RL floor) | 0.20 (G1 web) | 0.26 (G1 EDU, K-Bot) | 0.31 (G1 URDF) |
|---|---|---|---|---|---|
| 20 kg | 235 | 40 | 47 | 61 | 73 |
| 25 kg | 294 | 50 | 59 | 77 | 91 |
| 30 kg | 353 | 60 | 71 | 92 | 110 |

Suggested first-pass targets, all [E] and to be refined by JX1's own RL and trajectory study:

| Joint | Peak torque N·m | Other targets | Basis |
|---|---|---|---|
| Knee | 60–90 | continuous ≥ 20–30 N·m; no-load ≥ 15–20 rad/s; full-torque knee-point ≥ 10–12 rad/s | R1 18.8 rad/s, G1 X1 14.5 / X2 22.7, Froude-scaled human 11.5 |
| Hip pitch | 45–90 | — | — |
| Hip roll/yaw | 30–60 | — | — |
| Ankle | 25–50 | two ~20–25 N·m units in a parallel linkage | G1 style |
| Arms | 10–25 | — | — |

---

### 5. Gaps and open items

- **BHL actuator peak torque**: not stated in the paper, docs or repos. Only the 15:1 ratio, Kt, a 20 A current limit and 4–6 N·m deployed limits are published. The "20 Nm" figure seen in search summaries could not be sourced. MakerWorld actuator pages were blocked (Cloudflare 403).
- **Unitree G1 vs EDU knee (90 vs 120 N·m)**: the hardware difference (motor, ratio or firmware) is not published. The URDF (139) and T-N model (111/131) differ from both. The per-joint motor mapping comes from Unitree's RL code, not a spec sheet.
- **Unitree R1 motor models, gear ratios and T-N curves**: not published. Only URDF limits are available. No R1 entry exists in unitree_rl_lab.
- **Booster T1/K1**: actuator supplier and models are undisclosed. The two official URDF sets disagree (T1 knee 60 vs 130.5; K1 knee 112 vs web 60). No official price.
- **K-Bot**: height and mass come only from the press. docs.kscale.dev, kscale.dev and docs.zeroth.bot did not resolve (DNS) on 2026-09-24; the docs were read from the GitHub source. The price and shutdown date are [U].
- **Zeroth-01 size and mass**: only from the ToddlerBot paper table [U].
- **Robstride official datasheets** (robstride.com is JS-only, not readable): RS values come from K-Scale's docs and driver, not from Robstride directly.
- **Fourier N1, Noetix N2/Bumi, EngineAI SA01**: per-joint torques are unverified. N2 secondary specs conflict. PM01 price not verified.
- **Teardown data** (G1 two-stage planetary, heat pipes) is [U]. No verbatim ratio was captured, so none is reported.
- **Poppy**: the IROS 2013 leg-design paper (semi-passive knee) was not read.
- **Access notes**: the GitHub REST API rate limit was hit, so raw.githubusercontent.com and github.com HTML were used instead. WebFetch cached two PDFs it read (a Booster T1 RoboCup team spec sheet and the Poppy 2014 paper) under the Claude tool-results folder as part of normal PDF reading. No other binaries were saved. No browser tools, logins or forms were used.

---

### 6. Source list (all accessed 2026-09-24)

Primary [V]:
- https://www.unitree.com/g1/ · https://www.unitree.com/h1/ · https://www.unitree.com/R1
- https://github.com/unitreerobotics/unitree_rl_lab (`source/unitree_rl_lab/unitree_rl_lab/assets/robots/unitree_actuators.py`, `unitree.py`)
- https://github.com/unitreerobotics/unitree_ros (`robots/g1_description/g1_29dof_rev_1_0.urdf`, `g1_23dof_rev_1_0.urdf`, `h1_description/urdf/h1.urdf`, `h1_2_description/h1_2.urdf`, `r1_description/R1.urdf`, `r1_air_description/R1_AIR.urdf`)
- https://arxiv.org/abs/2504.17249 · https://arxiv.org/html/2504.17249 · https://lite.berkeley-humanoid.org/ · https://berkeley-humanoid-lite.gitbook.io/docs (releases, motor-characterization, joint-id-mapping, building-the-actuator)
- https://github.com/HybridRobotics/berkeley-humanoid-lite (`motor_configuration.json`, `configs/policy_humanoid.yaml`) · https://github.com/HybridRobotics/berkeley-humanoid-lite-assets (`berkeley_humanoid_lite_assets/robots/berkeley_humanoid_lite.py`, URDF) · https://github.com/HybridRobotics/berkeley-humanoid-lite-lowlevel (`robot_configuration.backup.json`, `robot/humanoid.py`) · https://github.com/T-K-233/Recoil-Motor-Controller-BESC (`Core/Src/motor_controller.c`, `position_controller.c`)
- https://arxiv.org/abs/2502.00893 · https://arxiv.org/html/2502.00893v4 · https://github.com/hshi74/toddlerbot (README, CHANGELOG.md)
- https://github.com/kscalelabs/docs (`docs/robots/k-bot/mechanical.md`, `motor-id-mapping.md`, `electrical.md`, `docs/robots/zeroth-01/bom.md`) · https://github.com/kscalelabs/kbot-models (`kbot/robot.urdf`, `kbot/metadata.json`) · https://github.com/kscalelabs/robstride (`src/actuator_types.rs`) · https://github.com/kscalelabs/kscale-assets (`zbot/robot.urdf`, `actuators/feetech_sts3250.json`) · https://github.com/kscalelabs/zeroth-bot · https://github.com/kscalelabs/kbot
- https://www.feetechrc.com/products/serial-port-series-steering-gear-page-3 and page-4
- https://www.booster.tech/booster-t1/ · https://www.booster.tech/booster-k1/ · https://www.booster.tech/store · https://docs.booster.tech/docs/product-manual/k1/getting-started/specifications/ · https://github.com/BoosterRobotics/booster_assets (`robots/T1/T1_23dof.urdf`, `robots/K1/K1_22dof.urdf`) · https://github.com/BoosterRobotics/booster_gym (`resources/T1/T1_serial.urdf`, `T1_locomotion.urdf`)
- https://www.poppy-project.org/en/robots/poppy-humanoid/ · https://github.com/poppy-project/poppy-humanoid (README, `software/poppy_humanoid/configuration/poppy_humanoid.json`) · https://flowers.inria.fr/PoppyHumanoids2014.pdf · https://arxiv.org/abs/2608.26505
- https://emanual.robotis.com/docs/en/dxl/mx/mx-28/ · https://emanual.robotis.com/docs/en/dxl/mx/mx-64/ · https://emanual.robotis.com/docs/en/dxl/ax/ax-12a/
- https://arxiv.org/html/2509.09364 (AGILOped)
- https://www.hightorquerobotics.com/mini-pi · https://www.agibot.com/products/X2 · https://www.engineai.com.cn/product-pm01.html · https://www.engineai.com.cn/
- https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2020.00013/full (Grimmer et al. 2020)

Secondary [U]:
- https://www.rs-online.com/designspark/k-scale-labs-launches-k-bot-americas-first-open-source-humanoid-robot
- https://www.humanoidsdaily.com/news/k-scale-labs-cancels-k-bot-orders-open-sources-all-ip-after-funding-fails
- https://news.ycombinator.com/item?id=44023680
- https://humanoid.guide/unitree-g1-teardown-reveals-actuator-and-cooling-tradeoffs/
- https://www.humanoidsdaily.com/news/booster-robotics-launches-k1-robocup-champion-platform
- https://hsl.robocup.org/wp-content/uploads/2026/03/large_Robotedge-specs-698021eff19c7.pdf
- https://www.humanoidsdaily.com/news/fourier-intelligence-launches-n1-humanoid-robot-with-open-source-strategy
- https://mikekalil.com/blog/noetix-robotics-n2/
- https://www.humanoidsdaily.com/news/chinas-noetix-robotics-prices-bumi-humanoid-under-1400
- https://www.therobotreport.com/engineai-releases-pm01-humanoid-robot-for-commercial-educational-use/
- https://www.rdworldonline.com/berkeley-debuts-5000-open-source-humanoid-built-with-desktop-3d-printers/
- https://interestingengineering.com/ai-robotics/new-3d-printed-berkeley-humanoid-lite
- https://hackaday.com/2026/08/30/lower-cost-humanoid-robot-leverages-diy-actuators/

## 7. India availability: leads collected in this survey

These are leads only, all UNVERIFIED unless marked. Another agent is checking Indian stores in depth. Nothing here was checked for INR price, stock, GST or warranty.

| Item | Lead | Source / note |
|---|---|---|
| SteadyWin GIM actuators (official store) | The official store sells a "Price Difference- PO# 1264 Shipping Cost-India" item, so it ships direct to India (VERIFIED that the line item exists) | https://steadywin-motor.com/products/price-difference-po-1264-shipping-cost-india (§1B) |
| RobStride RS00–RS06, 10P, EduLite | No Indian distributor in the official data. The official site links Seeed Studio, Amazon.com ASINs, AliExpress store 1103506059 and Taobao | robstride.com bundle (§1A) |
| Damiao DM-J series | International resellers (Seeed, AIFITLAB, Foxtech, OpenELAB); Taobao in China. No Indian listing seen | §1A |
| Unitree IM6014 / GO-M8010-6 / A1 | Official Shopify store (shop.unitree.com); India shipping not checked | §1A |
| ST B-G431B-ESC1 (Recoil-capable driver) | Evelta, ₹2,365 ex-GST (₹2,790.70 incl.), ships from Mumbai | §5 |
| Flipsky ODESC V4.2 | Technobotix ₹7,799, page showed OUT OF STOCK | §5 |
| Feetech STS3215 and other Feetech servos | Evelta product and brand pages; ThinkRobotics (SO-101 kits) | §2 |
| Hiwonder servos | ThinkRobotics Hiwonder collection; Robu.in Hiwonder category | §2 |
| ROBOTIS Dynamixel | MG Super Labs; Thingbits (XL430) | §2 |
| T-Motor MN5008 / MN501-S / MN6007-II / gimbal motors | Robokits: MN5008 ₹8,413; MN501-S ₹9,180; MN6007-II ₹13,464; GB54-2 ₹6,579 | §4 (listing read, not deep-checked) |
| CubeMars RI-series frameless motors (not the AK actuators) | Robokits "Robot Joint Brushless Motors": RI50 ₹8,245 … RI80 ₹19,327 | §4, §1B |
| Eaglepower LA8308 KV90 (OpenQDD motor) | Technobotix ₹10,999; TNT e-Comp ₹10,260; The Engineer Store ₹11,738 (OOS) | §4 |
| MyActuator RMD-X8 (legacy V3) | Amazon.in listings | §1B |
| Blocked, not checked | Robu.in (Cloudflare 403) for most items; ThinkRobotics product search found no ODrive, moteus, Damiao, SteadyWin or CubeMars | §1B, §5 |

## 8. Process notes, conflicts and gaps (whole survey)

**Process and rule compliance**
- **Tools and sites.**
  - No in-app browser, logins, forms or captcha/anti-bot bypass were used.
  - Sites that blocked scripted access were **not** bypassed: Robu.in and RobotShop (Cloudflare 403), Alibaba (captcha), large Gitee files (login-gated).
- **Search budget.** The shared WebSearch budget (200 calls per session) ran out mid-survey. Later lookups used WebFetch, curl on official URLs, the GitHub API (`gh`) and the Gitee API.
- **PDF handling.**
  - Manufacturer PDF manuals (Damiao, RobStride) were streamed into memory with curl → PyMuPDF for text extraction. No PDF was written to disk by the survey scripts.
  - However, the **WebFetch tool automatically cached some PDFs and images it read**: one Damiao manual in the main thread, plus datasheets, papers and spec images in the sub-searches. They sit under `C:\Users\testi\.claude\projects\D--Project-thenar-jx1\d251889a-7aed-444b-a917-29048e0309a9\tool-results\`. Nothing was written under `D:\Project\thenar-jx1` except this file.
  - No CAD, ZIP, XLSX or EXE files were downloaded. That is why SteadyWin selection tables, MyActuator V4 protocol ZIPs, Feetech datasheet PDFs and James Bruton's BOM.ods were not read.
- **Indirect reads.**
  - LK-Tech (lkmotor.cn) is HTTP-only; its official spec images were read through an HTTPS image proxy (§1B).
  - The Roozing 2024 paper was read from a third-party mirror (§3).
  - ST's UM2516 was read through an Octopart mirror (§5).
- Scratch and working files are in the session scratchpad `…\scratchpad\r2\`.

**Key cross-section conflicts to resolve before purchase**
- **RobStride RS02 mass:** 405 g on robstride.com vs 380 g in the RS02 manual and K-Scale docs. The RS02 IP67 web size (60×60×27 mm) looks like a copy error.
- **RobStride rated torque depends on the heat-sink plate** (§1A). RS04 is 40 N·m on 345×345 mm and 35 N·m on 220×200 mm.
- **Damiao handbook vs manuals.**
  - DM-J6006: rated/peak current 4/13 A vs 5.96/17.6 A.
  - DM-J8009: peak current 50 A vs 40 A.
  - DM-J8009P: mass 921 g vs 963 g.
  - Reseller listings rarely state the hardware revision (DM-J4340 V1.0 is 27 N·m peak; V1.1 is 40 N·m).
- **Other vendor conflicts.**
  - SteadyWin: GIM10015-9 second-encoder support is contradictory; GDZ/GDS drivers are being phased out in favour of the GDK driver, which has no published specs.
  - Several CubeMars, MyActuator and LK internal conflicts are listed in §1B.
  - Feetech and Hiwonder pages often contradict themselves; treat values as ±15% until bench-tested (§2).
- **Section 6 note.** It says RobStride datasheets could not be read from robstride.com. They were later read directly in §1A (site bundle and official manuals on github.com/RobStride), and the values match K-Scale's docs apart from the RS02 mass.

**Main gaps**
- **Damiao:** no official (Taobao) prices; DM-J6216L/P and DM-J8520P prices not found; DM-J8520P specs not retrievable.
- **No public prices:** HighTorque, DEEP Robotics J60/J80, MyActuator, LK-Tech (only reseller prices).
- **No independent measurements** of any actuator's T-N curve, continuous torque inside a closed limb, backlash growth or thermal time constant were found for the low-cost brands.
  - Recommended next step: bench-test 1–2 candidates per class (RS03/RS04 or DM-J10010L; RS06 or DM-J6216P; RS00/RS02 or DM-J4310 V1.2). Measure torque-speed at 48 V, thermal soak at 30–50% of peak, backlash, CAN timing and fall/impact survival.
- **Printed reducers:** no life data beyond ~60 h, or at more than ~50% of rated torque (§3).
- **Not covered in depth:** India import duty/GST and landed cost; Xiaomi CyberGear replacements beyond RobStride; T-Motor/Xiaomi standalone drivers; Unitree R1 motor models (not published).
