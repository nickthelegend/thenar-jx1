# JX1 actuator selection (V1 baseline) and trade study

**Status:** SELECTED for V1 prototype, 2026-09-24. Datasheet values: [`actuator_catalog.yaml`](actuator_catalog.yaml) (VERIFIED, official
RobStride manuals). Requirements: [`../requirements/robot_requirements.yaml`](../requirements/robot_requirements.yaml) (CALCULATED).

## 1. Decision

| Class | Product | Peak / rated | Mass | Joints | Qty | Landed ₹ each (ESTIMATED) |
|---|---|---|---|---|---:|---:|
| **XL** | RobStride RS04 | 120 / 40 N·m, 20.9 rad/s | 1.42 kg | hip pitch, knee | 4 | 34,634 |
| **L** | RobStride RS03 | 60 / 20 N·m, 20.9 rad/s | 0.88 kg | hip roll | 2 | 30,560 |
| **M** | RobStride RS06 | 36 / 11 N·m, 50.3 rad/s | 0.62 kg | hip yaw, ankle A/B, waist yaw | 7 | 28,522 |
| **S** | RobStride RS02 | 17 / 6 N·m, 42.9 rad/s | 0.38 kg | shoulder pitch/roll | 4 | 19,694 |
| **XS** | RobStride RS00 | 14 / 5 N·m, 33.0 rad/s | 0.31 kg | shoulder yaw, elbow | 4 | 16,978 |
| servo | Waveshare ST3215 | 1.9 N·m stall | 0.055 kg | neck yaw/pitch | 2 | 2,159 (Robu, in stock) |

All RobStride classes share one electrical/software interface: **48 V, classic CAN 2.0B 1 Mbit/s, 14-bit absolute encoder,
XT30 power + GH1.25 CAN connectors, private/CANopen/MIT protocols** — one driver stack for 21 joints.

## 2. Why these (requirement check, iteration 1-B, 27.5 kg robot)

| Joint | Required peak / cont. / speed | Selected capability | Margin |
|---|---|---|---|
| hip pitch | 85.4 N·m / 25.9 N·m / 12.1 rad/s | RS04 120 / 40 / 20.9 | 1.41 / 1.54 / 1.73 |
| knee | 71.0 / 29.5 / 12.2 | RS04 120 / 40 / 20.9 | 1.69 / 1.36 / 1.71 |
| hip roll | 50.0 / 17.3 / 6.0 | RS03 60 / 20 / 20.9 | 1.20 / 1.16 / 3.5 |
| hip yaw | 37.3 / 8.0 / 6.0 | RS06 36 / 11 / 50.3 | **0.97** / 1.38 / 8.4 |
| ankle motor | 32.0 / 3.4 / 8.8 | RS06 36 / 11 / 50.3 | 1.13 / 3.2 / 5.7 |
| ankle pitch (joint, via linkage) | 40.5 N·m | 46–58 N·m over −55…+30° | ≥ 1.13 |
| ankle roll (joint, via linkage) | 12.6 N·m | 51–65 N·m | ≥ 4 |

Requirement policy: peak = max(1.5 × dynamic peak over walking 0.30/0.52/0.79 m/s, turning and squat; 1.25 × static worst case incl.
single-leg toe/heel/edge stands); continuous = 1.3 × max(walking RMS, standing); speed = max(1.3 × peak, floor).
Thermal: worst RMS phase current ≤ 61 % of rated for every leg actuator (`calculations/run_power_budget.py`).

**Hip yaw is 3 % under the policy peak.** The dynamic peak (24.9 N·m) occurs only in the 0.79 m/s gait; options are (a) accept and cap
yaw torque use in the controller, (b) RS03 on hip yaw (+0.26 kg per leg, +₹2,040 each) — recorded as open issue OI-2.

## 3. Trade study (what was rejected and why)

Evidence: [`../research/raw/actuator_technology_raw.md`](../research/raw/actuator_technology_raw.md) (≈110 actuators),
[`../research/raw/india_robu_browser_sourcing_raw.md`](../research/raw/india_robu_browser_sourcing_raw.md).

| Option | Cost per peak N·m | Result |
|---|---|---|
| **Indian-stocked integrated actuators** — CubeMars AK10-9 ₹1,04,809, AK80-9 ₹79,739, AK60-6 ₹33,919 (Robu); xTerra QDD A2 ₹94,400; MyActuator X8 ₹85,475 (Amazon.in) | ₹2,200–7,900 / N·m | **Rejected**: 3–8× the import route; most out of stock |
| **RobStride (selected)** — official store, import | ₹290 (RS04) – ₹1,210 (RS00) / N·m landed | Best cost per N·m with ≥ 20 rad/s; single protocol family; K-Scale K-Bot precedent |
| Damiao DM-J10010L / DM-J4340P / DM-J8009P | similar to RobStride (reseller prices) | Kept as **alternative** (DM-J4340P: 40 N·m at 381 g, but 11.7 rad/s); mixing vendors doubles firmware work |
| SteadyWin GIM8108-8 / GIM8115-9 (ships to India) | ~$5–6 / N·m | Alternative for M class; 22 N·m too low for ankle pairs |
| **DIY** (drone BLDC from Robu + printed/laser-cut cycloid + FOC driver) — MAD 8318 ₹14,479, Eaglepower 8308 ₹11,579, Tarot 6012 ₹7,249; drivers: NDrive Z1 ₹13,999, ODESC ₹7,350; B-G431B-ESC1 sold out in India | ≥ ₹22,000 per 50–60 N·m joint before development/testing | **Deferred to V2 localisation**: not cheaper than import at JX1 scale (Berkeley Humanoid Lite DIY units cost US$94–188 and walk at 6 N·m caps); no published printed-reducer life data above ~60 h |
| Hobby/bus servos (Feetech STS3215, Waveshare ST3215 ₹2,159, Hiwonder) | cheap | Only for the **neck** (position-controlled, low torque) |

## 4. Procurement notes

- Landed cost = USD list × ₹95.96 × 1.3228 (HS 8501 effective duty) × 1.07 shipping (ESTIMATED). China-distributor route
  (CNY list, e.g. RS04 ¥1,199) is ≈ 34 % cheaper: ₹3.59 lakh vs ₹5.46 lakh for all 21 actuators.
- Buy **2 spares** of RS04 and RS06 for the leg bring-up (not in BOM total; see open issues).
- Bench-test one of each class before the full order: torque–speed at 48 V, thermal soak at 30–50 % peak, backlash, CAN timing.

## 5. V2 localisation path (DIY joint module)

The [Modular Actuator Interface](modular_actuator_interface.md) keeps the leg structure independent of the actuator make. A
locally built module (Indian BLDC + laser-cut steel cycloid + STM32G431 FOC board, ₹572 MCU at Evelta) must match the MAI
envelope, bolt patterns, 48 V / CAN protocol and the torque–speed table above to be a drop-in replacement.
