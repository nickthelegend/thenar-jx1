# Actuator project: full handoff (everything discussed and decided so far)

> **For the assistant reading this:** this document is the complete context of a long working session between a student builder
> and an AI assistant (Claude, working inside the `thenar-jx1` GitHub repository). Read all of it before answering. It tells you
> who the user is, how to talk to them, what was researched, what was designed (with numbers), what files exist, and what happens
> next. Section 16 lists the open questions you should ask the user first. All numbers are **CALCULATED** (from our models) or
> **ESTIMATED** (from cited price listings, Sep–Oct 2026) unless marked otherwise. **Nothing has been physically built or measured
> yet.**

---

## 0. Contents

1. The user and how to work with them
2. Project background: JX1 humanoid and its actuators
3. What happened in the session, step by step
4. Physics lesson given to the user (teeth, magnets, windings, torque)
5. Market survey: what actuators exist and what is inside them
6. How much torque humanoids need
7. The JXA family: three in-house actuator designs (research paper)
8. Winding procedure (how to wind the stator)
9. Making the other parts, plus casting and moulding
10. Cost: make in India vs buy from China
11. How Chinese makers do it (economics)
12. Business report: is an actuator company a good business?
13. JXC-5010: the 3D-printed cycloidal actuator (ready to build)
14. JXC-8308: the 90 KV motor actuator (next design, waiting on user data)
15. Recommended roadmap
16. Open questions and data still needed from the user
17. Files in the repository and how to regenerate them
18. Key equations reference
19. Key sources
20. Honesty rules and caveats

---

## 1. The user and how to work with them

- **Who:** a computer-science student in India (12th CBSE physics/electronics background; knows voltage, current, basic
  circuits, magnetic force on a wire, electromagnetic induction). Not a mechanical or electrical engineering student. Builds
  robots and actuators for fun and wants to turn it into a serious capability or business.
- **Location/currency:** India. Use **INR (₹)**, Indian suppliers (Robu.in, Evelta, IndustryBuying, bearinghouse.in, IndiaMART,
  Amazon.in), Indian job shops. Imports carry duty: our model uses a landed factor of **1.3228 (duty) × 1.07 (freight) ≈ 1.415**.
  Exchange rates used: **₹95.96 per US$**, **₹13.52 per CNY**.
- **Communication style they asked for:**
  - Plain English, step by step, assume 12th-grade physics. Do **not** use computer-science analogies.
  - Do not over-simplify either: explain the real relationships and formulas.
  - Be honest about what is hard, expensive or not worth doing.
  - They speak quickly and informally (voice input); infer the intent.
- **Document preference:** they like **research-paper-style PDFs** (IEEE two-column, LaTeX, numbered equations, tables,
  references). Three such PDFs exist (Section 17).
- **What they want to achieve:**
  1. Understand how actuators and motors work: copper windings, magnets, torque.
  2. Build actuators in-house, eventually competing with RobStride.
  3. Prototype by 3D printing first.
  4. Possibly build a business making actuators in India.

---

## 2. Project background: JX1 humanoid and its actuators

- **Repository:** `github.com/nickthelegend/thenar-jx1`. Work branch: `ccr-44731d06-gibsk7`.
- **JX1:** a 1.2 m, about 27.5–33.6 kg, 23-joint humanoid designed to be buildable in India, about ₹7.1 lakh in parts.
  - It is designed and simulated: CAD, finite-element checks, MuJoCo walking simulation, a reinforcement-learning walking controller, ROS 2.
  - It is **not built yet**.
- **JX1 actuators today (bought from RobStride, China):**

| Class | Product | Peak / rated torque | Speed | Mass | Joints | Landed price (USD route) |
|---|---|---|---|---|---|---|
| XL | RobStride RS04 | 120 / 40 N·m | 20.9 rad/s | 1.42 kg | hip pitch, knee (×4) | ₹34,634 |
| L | RobStride RS03 | 60 / 20 N·m | 20.9 rad/s | 0.88 kg | hip roll (×2) | ₹30,560 |
| M | RobStride RS06 | 36 / 11 N·m | 50.3 rad/s | 0.62 kg | hip yaw, ankle ×4, waist (×7) | ₹28,522 |
| S | RobStride RS02 | 17 / 6 N·m | 42.9 rad/s | 0.38 kg | shoulders (×4) | ₹19,694 |
| XS | RobStride RS00 | 14 / 5 N·m | 33 rad/s | 0.31 kg | shoulder yaw, elbow (×4) | ₹16,978 |

  - Via a China distributor (CNY list price + 5 % agent fee + duty), an RS04 lands at about **₹24,000**.
  - **Actuators are 77 % of JX1's parts cost.** That is why the user wants to make their own.
- **JX0:** a smaller 46 cm robot using Feetech STS3215 servos (₹58k). Not part of this actuator work.

---

## 3. What happened in the session, step by step

1. **First request:** research actuators (RobStride and others) and learn how motors, copper windings and magnetism work. Find
   the torque needed for big humanoids, work out how to build actuators in-house with few tools, and compare costs with Chinese
   manufacturers. Write a research paper/PDF that includes winding instructions.
   → Research agents surveyed actuator internals, Indian material prices and Chinese manufacturing economics. An analytic
   motor and gearbox design tool and a cost model were built, and the **JXA in-house actuator research paper** was written (Sections 4–11).
2. **Casting and moulding:** the user asked about moulds (silicone, cement, injection moulding) to make casings cheaply.
   → Explained the methods. Molten aluminium cannot go into silicone or cement (Section 9). A casting/moulding section and a
   housing-route cost model were added to the paper.
3. **Business:** is an actuator company a good business? The user also asked about the 2030 outlook (coding vs robots), copper
   prices, a "1 % of a trillion dollars = $10 bn" idea, Indian actuator makers, capital needed and a go-to-market plan.
   → Researched and written up as the **business paper** (Section 12).
4. **Format:** "build a research-paper-style PDF". Both PDFs were rebuilt in LaTeX IEEE style.
5. **Concrete build:** the user proposed a 5010 360KV drone motor (Robu, ₹2,239) and a SimpleFOCmini driver (Robu, ₹729),
   with a gearbox chosen from cycloidal, harmonic or planetary, prototyped by 3D printing.
   → Designed **JXC-5010** (Section 13). The SimpleFOCmini was rejected (2.5 A is too little). A cycloidal gearbox was
   chosen. Print files (STL/DXF) and a 4-page build plan were produced.
6. **Lesson:** the user asked to learn teeth, magnets, windings and torque from scratch → Section 4.
7. **Two approaches:** (A) take a **90 KV BLDC motor** and make a high-torque actuator to compete with RobStride;
   (B) 3D-print a small actuator end to end.
   → Plan given (Sections 13–15). Recommendation: build B (JXC-5010) first because it is cheap and ready, then A (JXC-8308).
   The JXC-8308 design is waiting on the user's motor data.
8. **This document:** handoff so another assistant can continue.

---

## 4. Physics lesson given to the user (teeth, magnets, windings, torque)

**Inside a BLDC/PMSM motor:**
- **Stator:** stack of thin insulated silicon-steel sheets with teeth; copper coils are wound around each tooth.
- **Rotor:** steel ring ("bell") carrying neodymium magnets alternating N, S, N, S.
- **"12N14P"** means 12 teeth/slots and 14 magnet poles. The user's 5010 360KV is 12N14P.
- **Air gap:** 0.3–1 mm between the tooth tips and the magnets. All torque is made there.

**Where torque comes from:**
- Lorentz force on each wire: **F = B·I·L**. Torque = F × r, summed over every wire side in the gap.
- Torque ≈ (wire sides in the gap) × B × I × L × r.
- Compact form: **T = (π/2)·σ·D²·L**, where σ is the air-gap shear stress, D the gap diameter and L the stack length.
  - Typical σ: 5–15 kPa continuous, 30–60 kPa for seconds.
  - Torque grows with **D²** but only **L**, which is why robot motors are flat "pancakes" with outer rotors.
  - Check: 5010 at 20 A gives about 0.46 N·m, i.e. σ ≈ 12 kPa.
- **Field-oriented control (FOC):** the driver switches coil currents so the stator field stays 90 electrical degrees ahead of the
  magnets. This needs an encoder.

**Teeth and magnets:**
- 3 phases (A, B, C), so the tooth count is a multiple of 3. Magnets come in pairs, so the pole count is even.
- Good combinations have nearly equal counts: 12N14P, 24N28P, 36N40P, 36N42P, 48N44P.
- **Winding factor kw ≈ 0.93–0.95** for these; it measures how much of the copper produces useful torque.
- Smoothness (cogging) is better when the least common multiple of slots and poles is large (12N14P → 84).
- **More poles (p = pole pairs):** thinner iron (lighter) and more torque per kg at low speed. Cost: higher electrical frequency
  (p × rev/s) and more iron loss at high speed. Robot motors use 28–42 poles.
- **Coil pattern:** found by the "star of slots" method. Example for 12N14P: `A a c C B b a A C c b B`
  (capital = wind clockwise, small = anticlockwise, seen from the tooth tip).

**Turns don't add torque (key idea):**
- Torque depends on **ampere-turns**. 10 turns × 20 A = 20 turns × 10 A = the same torque and the same heat, if the slot is full
  of copper either way.
- More turns: higher **Kt** (torque per amp) and lower **KV** (rpm per volt), so a lower top speed but less current needed.
- Rule of thumb: **Kt ≈ 8.27 / KV** N·m/A. For the 5010 360KV: Kt ≈ 0.023 N·m/A.
- Summary: turns set the speed-vs-current trade-off; copper, magnets and size set the torque.

**Heat is the real limit:**
- Copper loss **P = I²R** (about 1.5·I²·R_line-to-line for a 3-phase motor). Double the torque means 4× the heat.
- **Motor constant Km = T/√P** (N·m per √W) is the true figure of merit. It does **not** depend on turns. It depends on copper
  fill (hand-wound 35–45 %), magnet strength, air gap and size.
- Enamel survives 180–200 °C; keep the winding below about 120 °C.

**Neodymium magnets:**
- Grade N35–N52 means remanence Br ≈ 1.2–1.45 T.
- The suffix is the heat rating: plain N about 80 °C, H about 120 °C, **SH about 150 °C (use H/SH in motors)**.
- Gap flux: **B_gap ≈ Br × h_m/(h_m + g)**, where h_m is magnet thickness and g the gap. Thicker magnets give diminishing
  returns; a smaller gap helps a lot. Magnets cover 80–90 % of the circle.

**Iron:**
- Saturates at about 1.6–1.8 T. Wider teeth carry more flux but leave less copper room.
- Saturation is why peak torque is about 10 % below Kt × peak current (RS04 data).
- Laminations 0.2–0.35 mm thick stop eddy currents.

**Gearbox:**
- **T_out = T_motor × G × η**; output speed = motor speed / G.
- Reflected inertia grows with G². Legs use 6–10:1 ("quasi-direct drive", QDD): back-drivable and impact-tolerant.

**Cheat sheet:**

| Factor | Effect on torque | Trade-off |
|---|---|---|
| Diameter D | ∝ D² (biggest lever) | size, weight |
| Stack length L | ∝ L | weight |
| Current I | ∝ I | heat ∝ I², driver size |
| Turns | more torque per amp only | lower KV and speed |
| Copper fill | more continuous torque (Km) | winding skill |
| Magnet grade, thickness | ∝ B_gap | cost, heat rating |
| Air gap | smaller is much better | precision |
| Slot/pole combination | kw 0.93–0.95, smoothness | — |
| Poles | torque per kg at low speed | iron loss at high speed |
| Tooth width | avoids saturation | less copper room |
| Cooling | continuous torque | — |
| Gear ratio | × G | speed / G, back-drivability |

**Hands-on exercises suggested:**
1. Count the 5010's teeth and magnets.
2. Measure KV by spinning it with a drill and reading the voltage.
3. Measure resistance.
4. Feel the cogging (84 notches per revolution for 12N14P).
5. Rewind a cheap drone stator with more turns and confirm KV drops proportionally.

---

## 5. Market survey: what actuators exist and what is inside them

| Actuator | Peak / rated (N·m) | No-load (rad/s) | Mass (g) | Reducer | Price |
|---|---|---|---|---|---|
| RobStride RS00 / RS02 / RS06 | 14 / 5; 17 / 6; 36 / 11 | 33 / 43 / 50 | 310 / 405 / 621 | 10 / 7.75 / 9:1 planetary | US$125 / 145 / 210 (CN ¥598 / 699 / 849) |
| RobStride RS03 / RS04 | 60 / 20; 120 / 40 | 20.4 / 20.9 | 880 / 1,420 | 9:1 planetary, 42 poles | US$225 / 255 (¥999 / 1,199) |
| Damiao DM-J10010L / J10422P | 120 / 40; 400 / 100 | 20.9 / 12.6 | 1,372 / 2,700 | 10:1 / 22:1 | US$265 / 480 (reseller) |
| Unitree Go2 motor | 23.7 peak | 30 | 530 | 6.22:1 (9/19/47 teeth) | — (outer rotor 36N42P, teardown) |
| Unitree G1 knee / H1 knee | 90–139 / 360 | ~20 / 14 | — | G1: 2-stage 22.5:1 | not sold |
| CubeMars AK80-9 / AK10-9 | 18 / 9; 48 / 18 | – / 10.5 | 485 / 960 | 9:1, 36N42P Ø98 | ₹79,739 / ₹1,04,809 at Robu |
| MIT Humanoid U10 / U12 module | 33.6 / 68 | 55 / 45 | 619 / 1,174 | 6:1 | research |
| Berkeley Humanoid Lite (BHL) 6512 / 5010 | ~20–28 / ~4–6 used | — | — | 15:1 printed PLA cycloid | US$157–188 / ~94–136 |
| Tesla Optimus rotary | 20 / 110 / 180 | — | — | strain wave + clutch | in-house (plus linear 0.5–8 kN) |

- **RobStride:** Beijing, "灵足时代", founded Nov 2023 by Xiaomi's former CyberGear team.
  - Volume: over 50k joints by Sep 2025; guides 300k units in 2026 at an average of about ¥1,000.
  - **No teardown exists.** Site data give RS04: 42 poles, 9:1 machined-steel planetary, Kt 2.10 N·m/A rms, back-EMF
    16.9 V rms/krpm, line resistance 0.16 Ω, line inductance 0.211 mH, 90 A peak.
  - It is probably 36N42P like the others.
- **No RobStride model above 120 N·m.**
- **In India:** no volume maker of RobStride-class actuators. xTerra sells a 12 N·m QDD for ₹94,400.
- **DIY reference:** Berkeley Humanoid Lite uses a MAD 5010 110KV + printed PLA 15:1 cycloid + B-G431B-ESC1 driver.
  - Measured: about 90 % efficiency, 1.31° max backlash, 319 N·m/rad stiffness, 60 h life test.
  - Robot torque limits: 6 N·m (legs), 20 A.
- Roozing's 11:1 printed cycloid: 36.4 N·m nominal, 44 N·m static (PA-CF version stiffer).

---

## 6. How much torque humanoids need

- **JX1 (1.2 m, 27.5 kg), calculated with a 1.5× dynamic margin:**
  - hip pitch 85 / 26 N·m (peak / continuous), 12 rad/s
  - knee 71 / 30 N·m, 12 rad/s
  - hip roll 50 / 17 N·m
  - hip yaw 37 / 8 N·m (RS06 is 3 % short)
  - ankle motors 32 / 3.4 N·m each (two per ankle, parallel linkage)
  - waist about 30 N·m; shoulders and elbows ≤ 17 N·m
- **Full-size humanoids (1.6–1.9 m, 50–70 kg):**
  - Unitree H1/H1-2: knee 360, hip 220, ankle 59 / 2×75 N·m; knee 14 rad/s
  - Fourier GR-2/GR-3: knee and hip 366
  - UBTech Walker S2: 225 peak / 75 rated
  - AgiBot A2: 270
  - Fourier GR-1T2: 135
  - Knee torque per robot mass ranges from 2.1 to 7.7 N·m/kg.
- **Human data (N·m/kg):**
  - knee: walking 0.5–1.3, rising from a chair up to 2.0, running at 3.5 m/s 3.1, sprinting 3.6
  - A 70 kg robot that runs or gets up needs **200–360 N·m at the knee**.
- **Three classes defined:**
  - JXA-40 (RS06 class)
  - JXA-120 (RS04 class)
  - JXA-360 (H1 knee class; nobody sells it cheaply)

---

## 7. The JXA family: three in-house actuator designs

**Concept:**
- Outer-rotor surface-PM motor, double-layer tooth-concentrated windings.
- Single-stage planetary (sun in, ring fixed, carrier out).
- Two magnetic encoders, 48 V FOC driver on the back cover.

**Model** (`actuators/inhouse/qdd_design.py`):
- magnet circuit → B_gap → flux linkage → Kt and Ke
- slot geometry → copper fill (target 0.42 bare) → resistance → Km
- inductance → torque–speed at 48 V
- lumped thermal resistance → continuous torque (winding limit 120 °C)
- Lewis bending and Hertz contact → gear safety factors
- volumes → mass
- Turns are chosen from the speed target with 12 % headroom; saturation is calibrated on RS04.

| | JXA-40 | JXA-120 | JXA-360 |
|---|---|---|---|
| Benchmark | RS06 | RS04 | Unitree H1 knee |
| Slots/poles | 24N28P | 36N40P | 48N44P |
| Stator OD × stack | 72 × 14 mm | 100 × 20 mm | 140 × 28 mm |
| Air gap / magnet | 0.5 / 2.5 mm | 0.55 / 3.0 mm | 0.6 / 3.5 mm (N42SH) |
| Turns/tooth, wire, parallel paths | 7, 2 × 0.63 mm, 1 | 19, 1 × 0.60 mm, 4 | 4, 3 × 0.85 mm, 2 |
| Winding factor | 0.933 | 0.945 | 0.949 |
| Coil pattern (one repeat) | `A a c C B b a A C c b B` ×2 | `A a c C c b B b a` ×4 | `A a b B b B C c C c a A a A B b B b c C c C A a` ×2 |
| Wire per stator | 16 m / 45 g | 41 m / 104 g | 45 m / 230 g |
| Gear sun/planet/ring, module | 12/42/96, m0.7 | 12/42/96, m1.0 | 12/48/108, m1.25 |
| Ratio | 9:1 | 9:1 | 10:1 |
| **Peak torque** | **41 N·m** (59 A) | **125 N·m** (86 A) | **371 N·m** (206 A) |
| **Continuous torque** | **13 N·m** | **46 N·m** | **147 N·m** |
| **No-load speed at 48 V** | **47.7 rad/s** | **23.1 rad/s** | **18.6 rad/s** |
| Kt at output | 1.11 N·m/A rms | 2.31 N·m/A rms | 2.86 N·m/A rms |
| Phase R (20 °C) / L | 69 mΩ / 72 µH | 48 mΩ / 85 µH | 12 mΩ / 24 µH |
| Envelope | Ø90 × 58 mm | Ø119 × 67 mm | Ø161 × 83 mm |
| **Mass (estimated)** | **0.88 kg** | **1.91 kg** | **4.27 kg** |

- **Validation:** the JXA-120 model vs the RS04 datasheet:

| Quantity | RS04 | JXA-120 model |
|---|---|---|
| Kt (output) | 2.10 | 2.31 |
| Ke | 16.9 | 16.3 |
| Phase L | ≈105 µH | 85 µH |
| Peak current | 90 A | 86 A |
| No-load speed | 20.9 rad/s | 23.1 rad/s |

  Agreement is within 3–20 %. JXA-40's Kt (1.11) matches RS06 (1.10). This is the main evidence the designs are realistic.
- **Weaknesses:**
  - JXA-120 is about 34 % heavier than RS04 (solid planets, thick housings).
  - Peak current density of 60–95 A/mm² is sustainable for only 1.5–4 s, so the controller needs an I²t limit.
  - The 12-tooth sun needs a +0.3 profile shift and must be case-hardened (about 1,400 MPa contact stress).
  - The JXA-360 needs a 200 A driver at 48 V; a 72 V bus is better.
- **Prototype shortcut:** buy bare Chinese stator cores and wind them.
  - "10020" core (100 × 20 mm, 36N42P, US$19–31): 124 N·m peak / 44 N·m continuous / 23.8 rad/s, with 14 turns of 3 × 0.40 mm in 3 parallel paths.
  - Three stacked "13710" cores (137 × 30 mm, US$74 each): 372 / 147 N·m / 18 rad/s.

---

## 8. Winding procedure (how to wind the stator)

**Tools and materials:**
- Class-200 dual-coat enamelled copper wire.
- Epoxy powder coat on the stator (0.2–0.3 mm), or Nomex/DMD slot liners. Never wind on bare steel.
- Winding jig with a turn counter; plastic or brass tamping tool; wire tensioner.
- Class-H varnish; an oven reaching 150 °C.
- Milliohm/LCR meter; 500 V–1 kV insulation tester.

**Steps:**
1. Deburr and insulate the stack; check it holds 500 V.
2. Mark tooth 1 and number the teeth clockwise. Write the pattern on a card.
3. Wind each phase group as one continuous wire. Capital letter = clockwise, small letter = anticlockwise. Don't cut the wire
   between teeth of the same phase.
4. Lay the first layer tight from the slot bottom outwards at about 10–15 % of the wire's breaking load (about 15 N for 0.6 mm).
   Each tooth's coil fills only **half** of each slot.
5. Count turns exactly. Tamp the turns down.
6. Terminate: strip the enamel (solder pot at 450 °C or stripping cream), join the star point, sleeve it, lace the end turns.
7. **Test before varnish:**
   - phase resistances equal within ±2 %
   - insulation over 100 MΩ at 500 V
   - inductances equal within ±5 % (a coil wound the wrong way shows up here)
   - with the rotor fitted: three equal back-EMF sine waves
8. Varnish: preheat to 100 °C, dip or trickle, cure about 2 h at 150 °C. Re-test.

**Time per JXA-120 stator:**
- by hand: 3–5 h
- manual needle winder: 20–40 min (machine ₹2–7 lakh)
- CNC multi-spindle winder: 1–3 min (₹15–30 lakh)

Local motor-rewinding shops (ceiling-fan, pump and e-rickshaw rewinders) can do job work for about ₹800–2,000 per stator.
Practise first on cheap drone stators.

---

## 9. Making the other parts, plus casting and moulding

**Parts and how to make them:**

| Part | Material | How to make it |
|---|---|---|
| Laminations | M270-35A / 35C250 0.35 mm steel | fibre-laser or wire-EDM cut, bonded or welded, powder-coated (or buy Chinese cores) |
| Magnets | N42SH/N45SH arc segments | buy; bond with high-temperature epoxy using a non-magnetic spacer comb; check polarity |
| Rotor can | EN3/EN8 steel | lathe job work |
| Sun and planets | EN353 or 20MnCr5 steel, carburised 58–62 HRC, DIN 7 | gear-hobbing job shop |
| Ring gear | steel | wire-EDM |
| Housings | 6061-T6 aluminium | CNC (or casting, below) |
| Output bearing | crossed-roller, or two thin-section bearings | buy |
| Driver | STM32G4 + gate driver + MOSFETs + CAN | PCB assembled at JLCPCB or Lion Circuits |

**Assembly warning:** insert the rotor with a guide sleeve; the magnetic pull is hundreds of newtons.

**Casting and moulding (user asked):**
- **Molten aluminium cannot be poured into silicone moulds.** Aluminium is poured at 700–750 °C; the best silicones survive
  about 300 °C. Silicone is only for resin (urethane casting, 20–25 parts per mould) or low-melt metals like pewter.
- **Never pour metal into cement or damp moulds.** Water flashes to steam about 1,600× its volume and throws molten metal.
- **Injection moulding** is for plastic (moulds ₹1.5–15 lakh). It suits covers, not ±0.01 mm bearing seats.
- **Methods compared:**
  - sand casting (printed pattern; ₹250–420/kg)
  - investment / lost-PLA casting
  - gravity die (die ₹0.45–2 lakh)
  - high-pressure die casting (die ₹2–6 lakh; pays off at 5–10k parts)
  - urethane casting
  - plastic injection moulding
  - metal injection moulding (MIM; small parts under 50 g)
  - sintered gears (₹5–100 each; tooling pays off at ≥10k/yr)
- **Always cast near-shape, then finish-machine** bearing seats and faces.
- **Cost per finished JXA-120 housing (₹):**

| Route | 2 pcs | 25 | 200 | 1,000 | 10,000 |
|---|---|---|---|---|---|
| CNC from billet | **5,960** | 2,004 | 1,242 | 1,034 | 1,029 |
| Sand cast + machine | 8,426 | **1,585** | **732** | **548** | 536 |
| Gravity die + machine | 65,895 | 6,238 | 1,399 | 767 | 652 |
| High-pressure die + machine | 2,05,350 | 17,072 | 2,516 | 792 | **425** |
| Metal 3D print (AlSi10Mg) + machine | 12,620 | 10,762 | 10,436 | 10,350 | 10,348 |

  - Conclusion: billet below about 10 pieces; sand casting from about 20; die casting only near 10k.
  - The saving is small: about ₹400–500 per housing, 1.5–2 % of an actuator. Machining the bearing seats dominates either way.
  - **Gears are the bigger lever at volume:** sintered or MIM planets cost ₹20–150 each. Keep the sun gear hobbed and hardened.
  - **Never print gears for real loads; never cast gears, shafts or the stator.**
  - Lost-PLA at home needs a burnout kiln (₹24.5–55k), a crucible furnace (about ₹18k), investment powder (about ₹3,200/bag) and
    full protective gear. Start with a foundry instead.

---

## 10. Cost: make in India vs buy from China

**Tiers:**
- **P (prototype):** 2 units, retail parts, engineer at ₹500/h.
- **B (batch):** 25/yr, job-work parts, technician at ₹300/h.
- **F (small factory):** 1,000/yr, stamped laminations, bulk magnets/cores, operator at ₹220/h.

**Direct cost per actuator (₹):**

| Class | Make: proto | Make: batch | Make: 1k/yr | Buy: USD list landed | Buy: China distributor landed | China maker's cost (estimate) |
|---|---|---|---|---|---|---|
| JXA-40 (vs RS06) | 52,845 | 19,777 | 7,479 | 28,522 | 17,059 | 6,354–13,520 |
| JXA-120 (vs RS04) | 77,353 | 30,292 | 11,493 | 34,634 | 24,091 | 8,923–20,280 (central 11,357) |
| JXA-360 (vs Damiao J10422P) | 1,46,564 | 61,822 | 23,322 | 65,194 | – | 20,280–40,560 |

- Including equipment (written off over 3 years) and overhead, JXA-120 costs ₹95,241 / ₹53,279 / ₹15,167 per tier.
- **JXA-120 batch line items (₹):**
  - gears 5,500; housing/hub/carrier 4,500; bearings 4,400; driver + 2 encoders 4,500; labour 3,000
  - magnets 1,876; core 1,200; rotor can 1,200; fasteners etc. 800; copper 312; insulation/varnish 250
  - test/scrap allowance 2,754
  - total 30,292
- **Equipment:**
  - garage kit **₹3.2 lakh** (winding jig, LCR meter, insulation tester, milliohm meter, 60 V supply, oven, oscilloscope,
    hysteresis-brake dynamometer with torque sensor, USB-CAN, fixtures)
  - batch add-ons ₹12.5 lakh (semi-automatic needle winder ₹7 lakh, surge tester, second dynamometer, fixtures, inspection)
  - small factory ₹1.35 crore (CNC winders ₹40 lakh, stamping dies ₹24 lakh, gear tooling ₹15 lakh, end-of-line testers ₹20 lakh, …)
- **Scenarios:**
  - JX1 legs and waist (13 actuators):
    - Buying costs ₹3.99 lakh (USD route) or ₹2.55 lakh (China distributor).
    - Building 15 in-house: ₹3.70 lakh in parts and labour + ₹5.21 lakh for prototype rounds + ₹3.22 lakh of equipment =
      ₹12.13 lakh for the first set; each further set ₹3.20 lakh.
  - Full-size humanoid (4 × JXA-360, 14 × JXA-120, 10 × JXA-40):
    - Buying costs ₹10.3 lakh (USD) or ₹7.7 lakh (China).
    - Building costs ₹8.7 lakh at batch prices (₹15.1 lakh loaded) or ₹3.3 lakh at factory prices (₹4.3 lakh loaded).
    - A Chinese maker would spend about ₹3.5 lakh.
- **Break-even:**
  - At batch scale the JXA-120 costs ₹6,200 **more** than buying, so there is no break-even.
  - At factory scale the margin is ₹12,599 per unit against ₹1.10 crore/yr of fixed cost, so break-even is
    **≈ 875 JXA-120-class actuators per year**.
  - Even then an Indian line doesn't reach RobStride's own cost.
  - **Exception:** the 360 N·m class. A batch JXA-360 (₹61,822) already roughly equals the import price (₹65,194).
- **Conclusion of the technical paper:**
  - Building is feasible: the garage kit, bought cores and Indian job shops are enough.
  - It is not cheaper below about 875–1,000 units a year.
  - Keep buying RobStride for JX1 now. Develop in-house in parallel, starting with the 360 N·m class and supply security.

---

## 11. How Chinese makers do it (economics)

- **Broker teardowns put Unitree G1 joints at ¥1,000 (small) to ¥1,500 (large).** The split is:
  - reducer about 27 %
  - motor 20 %
  - encoders 20 %
  - driver 17 %
  - structure 16 %
- **Unitree (prospectus):** 2025 revenue ¥1.70 bn at a 60.4 % gross margin. Direct labour is only 8–14 % of cost. Mostly manual
  assembly, parts bought to its own drawings. Listed in Aug 2026.
- **Volume makers:** Encos shipped over 100k joints in 2025; Quanzhibo runs a 90-second-per-joint line, over 85 % automated,
  with over 96 % first-pass yield.
- **Wages:** Chinese factory wages (about ₹86k/month) are 3.5–4.5× India's. **India's cost gap is volume and supply chain, not wages.**
- **Magnets:**
  - Cheap: about ₹750 of magnets in a JXA-120 at bulk prices.
  - Supply risk: China's April 2025 licence rules for dysprosium/terbium (SH) grades still apply; wider rules are suspended only
    until **10 Nov 2026**.
  - India's ₹7,280 crore magnet scheme has no plant yet; expect Indian supply around 2027–28.
- **Import duty on motors (HS 8501):** 32.3 % in our model; one aggregator says about 40 %. Check ICEGATE.

---

## 12. Business report: is an actuator company a good business?

**Market:**
- Humanoids: 13–20k units in 2025 (mostly China).
- Forecasts:
  - BofA: 1.2 M/yr in 2030, 10 M/yr in 2035
  - Goldman: 6.5 M units, US$138 bn in 2035
  - Morgan Stanley: US$5 trillion by 2050
  - Citi: US$7 trillion by 2050
- Actuators are about 51 % of a humanoid's bill of materials, so the **actuator market is about US$0.23 bn (2025) →
  US$8–14 bn (2030) → US$10–90 bn (2035)**.
- Industrial robots: over 600k installed in 2025; India about 10k (6th), i.e. about 55k servo joints/yr, **all imported**.
- Indian humanoid demand to 2030: only thousands (Addverb targets 3,000; MeitY ₹500 cr humanoid fund announced June 2026).

**Copper:**
- About 6–8 kg per humanoid (about US$115). Humanoids are 0.02–0.08 % of world copper demand in 2030 and under 0.35 % in 2035.
- Copper stays strong (S&P: 28 Mt demand in 2025, 42 Mt by 2040, a 25 % supply gap by 2040; price about US$14.5k/t) because of
  grids, EVs (83 kg each) and data centres (20–40 t/MW), **not robots**.
- A JXA-120 holds about 0.1 kg of copper. **Magnets and quality are the levers, not copper.**

**Software vs hardware to 2030:**
- Entry-level coding is shrinking: US developers aged 22–25 are down about 20 % since 2024 (Stanford AI Index 2026).
- Total software jobs are still projected +15.8 % for 2024–34 (BLS).
- Physical manufacturing skill is less exposed.
- An actuator is about half software (FOC, calibration, simulation models), so CS plus hardware is a strong combination.

**"1 % of a trillion = $10 bn" is a fallacy:**
- The trillion-dollar figures are whole-robot-market estimates for 2050.
- 1 % of the 2030 actuator market is about US$104 M revenue, worth about US$416 M at 4× sales.
- A US$10 bn company needs about US$2.5 bn revenue: about 24 % of the 2030 market, about 10 M actuators a year.

**Indian landscape:**
- xTerra (QDD, ₹94,400, about 15 staff)
- Bhairav Robotics (Zen Technologies took 45 % for about ₹4 cr)
- Perceptyne (US$3 M seed)
- Addverb (Reliance; wheeled humanoid)
- General Autonomy (₹32 cr seed, imports actuators)
- Havells CRI (hiring for actuators)
- Adjacent capability:
  - Vector Technics (drone motors, 300k/yr)
  - Sona Comstar, Lucas TVS, Chara (EV motors)
  - Atomberg (BLDC fans)
  - Pitti (laminations)
- No Indian harmonic-reducer maker.

**Factory architectures:**
- **A. Design + assembly house:** 100–3k/yr, equipment about ₹15.7 lakh.
- **B. Partly integrated:** automated winding and test, 3–30k/yr, about ₹1–3 cr for 10k/yr.
- **C. Volume plant:** stamping, die casting, gear tooling, 50k–1M/yr, ₹20–100+ cr.

**Planning equations:** listed in Section 18.

**Staged capital plan (units are JXA-120 equivalents):**

| Stage | Units/yr | Price | Unit cost | Gross margin | Revenue/yr | Raise |
|---|---|---|---|---|---|---|
| 0. Bootstrap / prototypes (9 mo, 2 people) | 12 | – | ₹30,292 | – | 0 | ₹0.34 cr |
| 1. Seed: labs, startups, defence (18 mo, 9 people) | 600 | ₹42,000 | ₹18,000 | 57 % | ₹2.5 cr | ₹2.06 cr |
| 2. Series A: product line (24 mo, 35 people) | 6,000 | ₹30,000 | ₹11,357 | 62 % | ₹18 cr | ₹11.1 cr |
| 3. Series B: volume plant (24 mo, 140 people) | 60,000 | ₹21,000 | ₹11,357 | 46 % | ₹126 cr | ₹92.4 cr |

- Total about **₹106 crore (about US$11 M)**.
- Risk: at ₹15,000 per unit (a Chinese price war), the Stage-3 margin falls to about 24 %.
- At the end of Stage 3 the company would be worth about US$26–53 M at 2–4× sales.

**Capital sources:**

| Source | Size |
|---|---|
| Bootstrap | ₹10–35 lakh |
| Startup India Seed Fund | ≤₹20 lakh grant + ₹50 lakh debt |
| Incubators: ARTPARK (IISc), IIT hubs | grants, labs |
| Karnataka ELEVATE | ≤₹50 lakh |
| iDEX / ADITI (defence) | ≤₹1.5 cr / ≤₹25 cr |
| MeitY humanoid fund | ₹500 cr total |
| Seed VC (Yali, Speciale, Endiya, pi Ventures, Kalaari, Blume) | US$2–3.5 M |
| Series A / B | US$5–10 M / US$20–30 M |
| Strategic investors (Zen, Reliance, Zoho) | stake or acquisition |
| SIDBI venture debt | ₹10–15 cr |
| ECMS component scheme | 25 % capex support (large investments) |

Indian robotics VC was only US$52.9 M in all of 2025.

**Valuations:**
- Mature component makers trade at 0.3–3.5× sales; humanoid-themed ones at 4.5–10×.
- Unitree about US$27 bn (88× sales), down about 59 % from its IPO-day open.
- Figure about US$39 bn, Apptronik US$5.5 bn (private).

**Go-to-market:**
- **Positioning:** "India's actuator company": RobStride-class joints made and supported in India, with a non-Chinese finished-goods supply chain.
- **Win on:** trust/compliance (defence, government, Western buyers), local support, customisation (360 N·m class, 72 V) and
  software (RobStride-compatible CAN protocol, ROS 2, simulation models). Not on price.
- **Beachhead customers:**
  1. university labs
  2. Indian robotics startups
  3. defence (iDEX, DRDO)
  4. export
  5. industrial servo replacement
- **Sequence:**
  - Months 0–6: sell imported joints with Indian software, stock and support.
  - Months 6–18: sell JXA-120 and JXA-40, hand-built.
  - Months 18–36: JXA-360, 72 V, export.
  - Month 36+: volume contracts.
- **Kill criteria:** if fewer than 5 customers re-order within 18 months, or JXA-120 cannot reach ≤ ₹20k at 600/yr, stay an
  integrator and software company.
- **Recommendation:** build an actuator company, not another humanoid company. Start as an integrator, use grants before VC,
  raise in small steps, and build volume tooling only against signed orders.

---

## 13. JXC-5010: the 3D-printed cycloidal actuator (ready to build)

**Starting parts the user proposed:** 5010 360KV drone motor (Robu SKU 45571, ₹2,239; 12N14P, Φ50 × 26 mm, 4 mm shaft,
about 92–112 g) and SimpleFOCmini driver (₹729).

**Decisions:**
- **Driver: replace the SimpleFOCmini.** It gives only 2.5 A, so 0.023 × 2.5 × 20 × 0.85 ≈ **1.0 N·m max**.
  - Chosen: **ST B-G431B-ESC1**.
    - 40 A peak with forced air (20 A without), up to 6S (about 25 V).
    - STM32G431 on board, CAN, USB ST-Link.
    - Supported by the SimpleFOC library and by Berkeley Humanoid Lite's "Recoil" CAN firmware.
    - About US$18.59 at ST's eStore; often sold out in India (Evelta listed it at ₹2,791).
  - Fallback: Flipsky ODESC V4.2 (₹7,350 on Amazon.in, 24 V). NDrive Z1 (₹13,999 at Robu; 48 V, 55 A peak, CAN) is too big for this one.
  - Keep the SimpleFOCmini for bench learning or very light gimbal-motor joints.
- **Motor: keep the 5010 360KV.** A Tarot 5010 130KV (₹4,779) doubles motor-limited torque, but the printed gears cap torque anyway.
- **Gearbox: cycloidal** (not harmonic, not planetary).
  - Harmonic: printed flexspline is weak and fatigues.
  - Planetary: printed versions are 60–80 % efficient with 0.6–2.6° backlash, and ≤ 10:1 per stage.
  - Cycloidal: 10–25:1 in one stage, load shared over many lobes, steel pins take the contact, shock tolerant, proven printed (BHL).
- **Encoder:** MT6701 14-bit module (about ₹760) with a 6 × 2.5 mm diametric magnet glued on the motor's rear shaft end; AS5600 is the budget fallback.

**Reducer geometry:**
- 20:1, 21 ring pins (Ø4 × 20 mm hardened steel dowels, greased) on a pin circle of radius 32 mm.
- Eccentricity e = 1.0 mm; short-amplitude coefficient λ = eN/R = 0.66 (must be < 1).
- Two discs, 7 mm thick each, 180° apart on a double eccentric cam. 0.10 mm profile clearance for FDM.
- 6 output pins Ø4 on radius 21 mm, each with two MR74ZZ (4 × 7 × 2.5) rollers per disc; disc output holes Ø9.
- Bearings: 6803 (17 × 26 × 5) on each eccentric journal; output bearing 6810 (50 × 65 × 7).
- Checks:
  - profile valid (no self-intersection); minimum concave radius 3.3 mm (> pin radius)
  - disc radius 28.9–30.9 mm; walls around holes 3.5 / 3.4 mm; pin pitch 9.6 mm
- Housing Ø82 mm; total stack Ø82 × 64 mm.
- Disc profile (pin circle R, pin radius r incl. clearance, N pins, eccentricity e):
  - x = R cos t − r cos(t+ψ) − e cos(Nt)
  - y = −R sin t + r sin(t+ψ) + e sin(Nt)
  - ψ = atan2(sin((1−N)t), R/(eN) − cos((1−N)t))

**Stress checks (each disc carries 55 % of torque):**

| Output torque | 4 N·m | 8 N·m | 10 N·m |
|---|---|---|---|
| Max ring-pin force | 21 N | 42 N | 52 N |
| Max output-pin force | 70 N | 140 N | 175 N |
| Ring-pin contact pressure, PLA/PETG | 44 MPa | 62 MPa | 69 MPa |
| Ring-pin contact pressure, PA-CF | 53 MPa | 76 MPa | 85 MPa |
| Output-roller contact pressure, PLA/PETG | 34 MPa | 48 MPa | 53 MPa |
| Output-pin bending | 128 MPa | 256 MPa | 320 MPa |

- PLA yields at about 60–70 MPa in compression.
- **The printed discs limit the actuator to about 10 N·m peak and about 4 N·m continuous**, not the motor.

**Expected performance (calculated):**

| Motor + driver | Peak | Continuous | No-load (24 V) | Motor + driver cost |
|---|---|---|---|---|
| 5010 360KV + SimpleFOCmini | 1.0 N·m | 0.8 N·m | 45 rad/s | ₹2,968 |
| **5010 360KV + B-G431B-ESC1 (chosen)** | **7.8 N·m** | **3.9 N·m** | **45 rad/s** | **₹5,039** |
| Tarot 5010 130KV + B-G431B-ESC1 | 10 (gear-limited) | 4 | 16 rad/s | ₹7,579 |

Mass about 0.46 kg.

**Mechanical stack (heights in mm):**
- adapter plate 0–4 (motor base bolts to it)
- motor 4–30, inside a spacer ring 4–33
- eccentric cam bolted to the rotor bell's propeller-mount holes, centred on the 4 mm shaft (flange 30–33, collar 33–35,
  journal 1 35–42, collar 42–43.5, journal 2 43.5–50.5)
- ring-pin housing 33–61: floor lip 2, pin zone 15.5, carrier-plate zone 3.5 (gives the bearing a shoulder), 6810 seat 7
- disc 1 35–42, disc 2 43.5–50.5
- carrier: plate 3 mm + hub Ø50 × 10 mm in the 6810 (≈50.75–63.75)
- retainer ring 61–64
- six M3 × 65 through-bolts clamp everything

**Bill of materials (₹; E = estimate):**

| Item | Qty | Total |
|---|---|---|
| motor | 1 | 2,239 |
| B-G431B-ESC1 (E) | 1 | 2,800 |
| MT6701 module (E) | 1 | 760 |
| diametric magnets (E) | 2 | 80 |
| 6810 bearing (bearinghouse) | 1 | 470 |
| 6803 bearings (E) | 2 | 200 |
| MR74ZZ rollers (E) | 24 | 720 |
| Ø4 × 20 dowels, pack of 100 (IndustryBuying) | 1 | 624 |
| Ø4 × 30 dowels or silver-steel rod cut to 29 mm (E) | 6 | 150 |
| fasteners, M3 heat-set inserts (E) | – | 300 |
| filament, about 180 g (E) | – | 250 |
| grease (E) | – | 200 |
| 24 V 10 A supply (E) | 1 | 1,200 |
| **Total** | | **≈ ₹9,993** |

**Printing:**
- Print a **test coupon first**: Ø3.95 / 4.0 / 4.05 holes and a Ø26 bore. Tune the dowel press fit and the bearing fit.
- v0 in PLA+: 0.2 mm layers, 4–5 walls; discs flat at 100 % infill; housing 40 % gyroid; carrier and cam 80–100 %.
- v1 in PETG-CF or PA-CF (hardened nozzle, dry filament). Keep PLA away from the motor (PLA softens near 55 °C).
- Remove elephant's foot on the discs.

**Assembly:**
1. Press the 21 ring pins into the housing.
2. Press a 6803 into each disc; press the 6 pins through the carrier; add 2 rollers per pin per disc.
3. Bolt the motor to the adapter; fit the spacer ring; glue the encoder magnet; mount the encoder 1–2 mm below it.
4. Bolt the cam to the bell.
5. Grease. Fit the housing, then disc 1, then disc 2 rotated 180°.
6. Fit the carrier pins through both discs, the 6810 bearing, the retainer and the 6 bolts. One output turn should equal 20 motor turns, with no binding.

**Firmware:**
- Power from a current-limited 24 V supply, starting at 3 A.
- Arduino IDE with the STM32duino core and the SimpleFOC library:
  1. open-loop spin
  2. sensor alignment (7 pole pairs for 12N14P)
  3. torque mode at 3 A
  4. velocity and position loops
  5. raise the current limit stepwise to 20 A
- Later: BHL Recoil firmware for CAN, plus an output encoder or homing switch (with 20:1 gearing, the motor encoder alone
  can't tell the output position after power-up).

**Tests:**
- **Kt:** 100 mm lever on a kitchen scale at 2, 4, 8 A.
- **Peak torque:** 20 A for 2 s; expect about 7.8 N·m.
- **Backlash:** dial gauge (BHL: 1.3°).
- **Thermal:** 30 min at 3–4 N·m; motor below 80 °C, housing below 50 °C.
- **Life:** 20 h at 0–4 N·m.

**⚠ Measure first:**
- The cam and motor-adapter files assume a **25 mm base bolt circle (4 × M3)** and a **16 mm propeller-mount bolt circle**.
  The user must measure their motor and change `motor_bolt_pcd` and `prop_pcd` in `export_cad()` in
  `actuators/diy_cycloid/cycloid_actuator.py`, then re-run.
- Motor height is assumed to be 26 mm (`MOTOR_H`); shim to align.

**Upgrade path:** PA-CF discs → laser-cut steel or aluminium discs (DXF ready) → scale up the stage for 6012/8108 motors → the JXA family.

---

## 14. JXC-8308: the 90 KV motor actuator (next design, waiting on user data)

**User's goal:** take a "90 KV BLDC motor" and make a high-torque actuator that competes with RobStride.
**Assumed motor:** Eaglepower LA8308 KV90 (≈ ₹10,260–10,999 in India; used by the open-source OpenQDD, which measured
16.36 N·m at 9:1). **Confirm the model with the user.**

**Key teaching point:**
- You cannot "convert" a 90 KV motor to more torque by rewinding; KV only trades torque-per-amp against speed.
- The torque comes from (1) a driver giving about 40 A, (2) the gear ratio, (3) cooling (stator pressed onto an aluminium hub).
- Kt ≈ 8.27/90 ≈ 0.092 N·m/A. Rated about 22 A, so about 2 N·m continuous at the motor; about 40 A for seconds, so about 3.7 N·m.

**Calculated options (cycloid, design script checks):**

| Ratio and geometry | At 20 A | At 40 A | Printed-disc limit | No-load 24 V / 48 V |
|---|---|---|---|---|
| 11:1, 12 pins, R45, e 2.5 | 17.2 N·m | 34.4 N·m | too high stress (PLA 92 MPa at 30 N·m), not recommended | 20.6 / 41.1 rad/s |
| **15:1, 16 pins, R48, e 2.0, Ø6 pins, 12 mm discs** (chosen) | 23.4 N·m | 46.9 N·m | about 25 N·m peak (64 MPa PLA, 78 PA-CF), about 15 N·m continuous (49 MPa) | 15.1 / 30.2 rad/s |

- Proposed internals: 8 output pins Ø5 on R28 with Ø10 rollers, 8 mm roller width; eccentric bearings 25 × 37 × 7; output
  bearing 70 × 90 × 10; housing about Ø116.
- Wall checks passed (2.5 / 7.9 mm).

**Expected JXC-8308 performance:**

| Version | Peak | Continuous | Speed at 48 V | Mass | Cost |
|---|---|---|---|---|---|
| Printed discs (PA-CF) | about 25 N·m | about 15 N·m | about 30 rad/s | about 0.9–1.1 kg | ≈ ₹21–29k |
| Laser-cut steel discs | about 40–45 N·m | about 15–17 N·m | about 30 rad/s | about 0.9–1.1 kg | ≈ ₹21–29k |
| RobStride RS06, for comparison | 36 N·m | 11 N·m | 50 rad/s | 621 g | ₹17k (China distributor) / ₹28.5k (USD) |

Cost breakdown: motor ₹11k + driver ₹7–14k + mechanical about ₹3k.

**Verdict:**
- Matches or beats the RS06 on torque (especially continuous).
- Slower and heavier; similar price.
- **Cannot reach RS04 (120 N·m) with an 8308.** That needs the 100 mm-class JXA-120 motor.

**Driver for JXC-8308 (needs 40 A and 48 V):**
- **NDrive Z1** (₹13,999 at Robu; 48 V, 20 A continuous / 55 A peak, CAN, onboard encoder, Indian stock), or
- Flipsky **ODESC 3.6 56 V** (import, about US$69).
- The ₹7,350 ODESC V4.2 is 24 V only (halves the speed). The B-G431B-ESC1 is marginal here (25 V max, fan needed at 40 A).

**To generate JXC-8308 files, the next assistant needs from the user:**
1. Exact motor model (link or photo).
2. Base mounting-hole circle diameter and screw size.
3. Rotor-top (propeller mount) hole circle and screw size.
4. Shaft diameter and protrusion.
5. Overall diameter and height.
6. Which driver they will buy (24 V or 48 V).

Then copy `actuators/diy_cycloid/cycloid_actuator.py`, set the `Cycloid` parameters above, `MOTORS`/`DRIVERS`, `MOTOR_H`,
bolt circles and stack heights, and regenerate STL/DXF, figures and a plan PDF the same way as JXC-5010.

---

## 15. Recommended roadmap

**Build B (JXC-5010) first, then A (JXC-8308).** B is cheap (about ₹10k), the files are ready, and every lesson transfers to A:
printer press-fits, cycloid meshing and wear, encoder calibration, current-loop tuning, measuring Kt and backlash.

- **Week 1:**
  1. Order the B-G431B-ESC1, MT6701, bearings (6810, 2 × 6803, 24 × MR74ZZ), Ø4 dowels and a 24 V supply.
  2. Measure the 5010's bolt circles, update the two numbers, re-run the script.
  3. Print the test coupon, then v0 parts in PLA+.
- **Weeks 2–3:**
  1. Assemble, open-loop spin, encoder calibration, torque mode at 3 A.
  2. Measure Kt, peak torque, backlash and temperature. Update the script with measured Kt.
- **Weeks 3–8:**
  1. Buy the 8308 90 KV motor and the NDrive Z1 (or ODESC 56 V).
  2. Generate the JXC-8308 design and print v0 in PA-CF; test to about 20 N·m.
  3. Laser-cut steel discs for about 40 N·m.
- **Later:**
  - JXA-120 prototype on a bought 10020 stator core, hand-wound (garage kit ₹3.2 lakh).
  - Own driver PCB (KiCad, based on the B-G431B-ESC1 / moteus designs).
  - Business stage 0 → 1 (Section 12): integration and resale first, then own actuators to labs, startups and defence.
- **JX1 robot:** keep buying RobStride. Don't put JX1 on the critical path of a new actuator.

---

## 16. Open questions and data still needed from the user

1. **90 KV motor model** and its dimensions (Section 14 list).
2. **5010 measurements:** base bolt circle, propeller-mount bolt circle, height (for the JXC-5010 `MEASURE_FIRST` parts).
3. **Printer and filaments available** (the repo mentions a Bambu P1S class printer; PA-CF needs a hardened nozzle).
4. **Budget** for the next 2 months, and whether to buy the JXC-8308 parts in parallel.
5. **Power source:** bench supply vs 6S LiPo; 24 V vs 48 V.
6. **Author name and affiliation** to put on the three PDFs (currently "JX1 Humanoid Project").
7. Whether they want a printable notes PDF of the physics lesson (offered, not yet made).

---

## 17. Files in the repository and how to regenerate them

Branch `ccr-44731d06-gibsk7` of `github.com/nickthelegend/thenar-jx1`.

| Path | What |
|---|---|
| `actuators/inhouse/JXA_inhouse_actuator_research_paper.pdf` | **Technical paper** (8 pp, IEEE): physics, survey, torque needs, JXA design, winding, manufacturing, casting, costs |
| `actuators/inhouse/qdd_design.py` | JXA motor + gearbox + thermal model → `results/design.json`, `variants.json`, figures |
| `actuators/inhouse/cost_model.py` | Make-vs-buy, equipment, scenarios, break-even, housing routes → `results/cost.json` |
| `actuators/inhouse/make_paper.py`, `latex_tools.py` | LaTeX paper generators |
| `business/Actuator_business_report_India.pdf` | **Business paper** (5 pp, IEEE): market, copper, labour, landscape, equations, capital, valuation, go-to-market |
| `business/actuator_business_model.py`, `make_business_report.py` | business model and paper |
| `actuators/diy_cycloid/JXC5010_cycloidal_actuator_build_plan.pdf` | **JXC-5010 build plan** (4 pp, IEEE) |
| `actuators/diy_cycloid/cycloid_actuator.py`, `make_plan.py` | cycloid design, checks, CAD export, figures, plan |
| `actuators/diy_cycloid/cad/*.stl, *.dxf` | print files: disc (print 2), ring-pin housing, output carrier, eccentric cam*, motor adapter*, spacer ring, retainer ring (* = measure first) |
| `research/raw/*.md` | all research logs with URLs and evidence labels |
| `actuators/actuator_selection.md` | JX1's current RobStride selection (links to the in-house study) |

Regenerate:

```
pip install numpy matplotlib shapely trimesh manifold3d mapbox_earcut ezdxf
apt-get install texlive-latex-extra texlive-publishers texlive-science lmodern latexmk
python actuators/inhouse/qdd_design.py && python actuators/inhouse/cost_model.py && python actuators/inhouse/make_paper.py
python business/actuator_business_model.py && python business/make_business_report.py
python actuators/diy_cycloid/cycloid_actuator.py && python actuators/diy_cycloid/make_plan.py
```

---

## 18. Key equations reference

**Motor:**
- Torque from size: T = (π/2)·σ·D²·L
- Gap field: B_g = k_l·B_r / (1 + μ_r·k_C·g/h_m); fundamental B_1 = (4/π)·B_g·sin(α_p·π/2)
- Flux linkage: λ = k_w·N_ph·B_1·D·L/p
- Torque: T = (3/2)·p·λ·i_q = K_t·i_q; rule of thumb Kt ≈ 8.27/KV
- Winding factor: k_w = k_p·k_d, with k_p = |sin(pπ/Q)|; k_d from the star of slots
- Phase resistance: R_ph = ρ·N_c·Q·ℓ_t / (3·a²·A_c)
- Motor constant: K_m = K_t,rms / √(3·R_ph); heat = (T/K_m)²
- Voltage limit: (R·i_q + ω_e·λ)² + (ω_e·L·i_q)² ≤ V_max², with V_max = 0.95·V_dc/√3
- Thermal: 3·I_rms²·R + P_Fe = (T_lim − T_amb)/R_th

**Planetary gear:**
- G = 1 + Z_r/Z_s; Z_r = Z_s + 2Z_p; (Z_s + Z_r)/N_planets must be a whole number
- Lewis bending: σ_F = F_t·K_γ·K_v/(b·m·Y)
- Hertz contact: σ_H = Z_E·Z_H·√(F_t(u+1)/(b·d_1·u))
- Reflected inertia: J_out = G²·J_rotor

**Cycloid:**
- G = N − 1; λ = eN/R < 1
- Ring-pin force: F_pin = 4·T_c/(e·N·(N−1)); output-pin force: F_out = 4·T_c/(Z_w·R_w)
- Contact pressure: p = √(F·E*/(π·b·R_eff))

**Actuator:**
- T_out = K_t·I·G·η; speed_out = KV·V·2π/60/G

**Cost and business:**
- Loaded unit cost: C_loaded = Σparts + h·r_L + allowance + (C_NRE/3 + C_overhead)/N
- Break-even: N* = F/(P − C)
- Gross margin: GM = (P − C)/P
- Learning curve: C(N) = C_1·N^(log₂ r); our model r ≈ 0.83 between 25 and 1,000 units/yr
- Line capacity: N_line = t_available·OEE/t_takt (90 s takt, 2 shifts, OEE 0.65 → about 124,800/yr)
- Working capital: WC = COGS/365 × (inventory days + receivable days − payable days), with 120/60/30 days
- Capital to raise: K = capex + Σ losses + WC + 0.5 × opex
- Market cap: MC = multiple × revenue; revenue = robots × actuators per robot × share × price
- Housing route: C(n) = C_tool/n + c_blank + t_m·r(n)
- Actuator market: M_act = N_robots·C_BOM·s_act
- Copper share: s_Cu = N_robots·m_Cu/D_world

---

## 19. Key sources

- RobStride site data and manuals (github.com/RobStride/Product_Information)
- Damiao manuals; CubeMars product pages
- Simplexity "Unitree Go2 motor teardown"; unitree_rl_lab actuator models; Fourier Wiki-GRx models; UBTech Walker S2 SDK
- Wensing et al. 2017 (MIT Cheetah, IEEE T-RO); Katz 2018 MIT thesis; SaLoutos et al. arXiv:2104.09025 (MIT Humanoid)
- Liao et al. arXiv:2504.17249 (Berkeley Humanoid Lite)
- Pyrhönen, *Design of Rotating Electrical Machines*; Hendershot & Miller, *Design of Brushless Permanent-Magnet Machines*;
  Bianchi & Dai Prè 2006 (star of slots); Shigley's
- Schache 2011; Yoshioka 2014
- China Post Securities G1 teardown (Mar 2026); Guosen Unitree prospectus review (Aug 2026); BofA Institute "Physical AI part 2"
  (Mar 2026); KrASIA on RobStride; PMIndia ₹7,280 cr magnet scheme (Nov 2025)
- IFR World Robotics 2026; S&P Global copper (Jan 2026); Stanford AI Index 2026; BLS 2024–34; Brynjolfsson et al. 2025;
  Acemoglu & Restrepo 2020
- Indian prices: Robu, Evelta, IndustryBuying, bearinghouse.in, IndiaMART/TradeIndia, iamRapid, Lion Circuits, JLCPCB, AliExpress
- Full URLs, dates and labels are in `research/raw/` (e.g. `india_motor_materials_raw.md`, `india_casting_moulding_raw.md`,
  `china_actuator_manufacturing_economics_raw.md`, `india_robotics_industry_capital_raw.md`, `market_outlook_2030_copper_raw.md`,
  `actuator_internals_and_torque_raw.md`).

---

## 20. Honesty rules and caveats

- Nothing has been built. All performance figures are calculated (models are accurate to about ±15–30 %); confirm them on the bench.
- Many prices are estimates or listings that need a real quote: B-G431B-ESC1 landed, 6803, MR74ZZ, MT6701, stamping dies, gear hobbing.
- Most bank forecasts and Indian funding figures come from press coverage (unverified); the original notes are paywalled.
- The magnet export situation changes fast (rules suspended until 10 Nov 2026). Re-check before ordering.
- Safety:
  - NdFeB magnets pinch and shatter.
  - 48 V batteries can deliver hundreds of amps; fuse everything and use a current-limited supply first.
  - Molten metal and water are explosive; never use cement or damp moulds.
  - Varnish and epoxy fumes need ventilation.
- Keep advice honest about trade-offs:
  - In-house actuators are **not cheaper** than RobStride below about 875–1,000 units a year.
  - Printed gearboxes are torque-limited.
  - A RobStride RS04 competitor needs a 100 mm-class motor, not a drone motor.
