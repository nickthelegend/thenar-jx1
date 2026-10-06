# JX1: actuator internals, full-size humanoid torque requirements, QDD gearbox practice (RAW)

Compiled 2026-10-06. Scope: the gaps left by `actuator_technology_raw.md` (prices and catalogue specs) and `reference_robots_raw.md` (small and mid-size robots, Unitree G1/H1/H1-2/H2 model files). Neither of those files is repeated here; pointers are given where they already hold the data.

## Contents
- 0. Labels and conventions
- 1. Internal motor design of popular QDD actuators
  - 1.1 Master table
  - 1.2 Derived motor constants (ESTIMATED)
  - 1.3 Per-actuator notes and sources
  - 1.4 What could not be found
- 2. Torque and speed requirements of full-size humanoids, and human data
  - 2.1 Robot joint torque and speed table
  - 2.2 Tesla Optimus details
  - 2.3 Human joint moments (75 kg reference)
  - 2.4 Synthesis: torque targets for a 1.6–1.9 m, 60–80 kg robot (ESTIMATED)
- 3. Planetary and cycloid gearbox practice for QDD
  - 3.1 Published or measured tooth counts
  - 3.2 Tooth-count feasibility for common ratios (ESTIMATED arithmetic)
  - 3.3 Module, material, heat treatment
  - 3.4 Output bearings
  - 3.5 Backlash, efficiency and life
  - 3.6 Two-stage and belt-assisted practice
- 4. Gaps and honest limits
- 5. Source index

---

## 0. Labels and conventions

- **VERIFIED (V)**: official manufacturer page, manual, firmware or model file, or the primary paper.
- **VERIFIED-T (VT)**: a primary teardown measurement published by a named third party (engineering firm or author). It is a real measurement but not an official specification.
- **ESTIMATED (E)**: my own arithmetic. The method is given each time.
- **UNVERIFIED (U)**: secondary sources, resellers, news, forums, search-engine excerpts I could not open, or securities-report summaries.
- "Output-side" means after the gearbox and "motor-side" means at the rotor. RobStride and CubeMars quote Kt at the **output**.
- "Arms" means RMS phase amps and "Apk" means peak phase amps.
- Kv conversion (E): Kv [rpm/V] ≈ 1000 / (back-EMF line-line Vrms per krpm × √2).
- Kt from back-EMF (E): Kt [N·m/Arms] ≈ √3 × Ke,LL,rms [V·s/rad], valid for a sinusoidal PMSM.
- Copper loss (E): for a wye winding, R_phase = R_line / 2 and P_cu = 3·I_rms²·R_phase = 1.5·R_line·I_rms².
- Motor constant (E): Km = Kt_motor / √(1.5·R_line) [N·m/√W]. Output-side Km = Km × N.

---

## 1. Internal motor design of popular QDD actuators

### 1.1 Master table

`n/p` = not published / not found.

| Actuator | Rotor | Slots / poles | Stator or motor size | Ratio and gear | Kt (as published) | Back-EMF / Kv | R / L | Mass | Peak / rated torque | Thermal | Label |
|---|---|---|---|---|---|---|---|---|---|---|---|
| RobStride RS00 | n/p | ?/28 (24N28P likely, E) | housing 57×57×51 mm | 10:1, "Machined Steel" | 1.48 N·m/Arms (output) | 9.5 Vrms/krpm (Kv ≈74, E) | n/p | 310 g | 14 / 5 N·m | Class B insulation | V (robstride.com bundle) |
| RobStride RS01 | n/p | ?/28 | 78.5×78.5×40 | 7.75:1, machined steel | 1.22 N·m/Arms | 9.6 Vrms/krpm (Kv ≈74) | line 0.58 Ω; 187–339 µH | 380 g | 17 / 6 | Class B | V |
| RobStride RS02 | n/p | ?/28 | 78.5×78.5×45.5 | 7.75:1, machined steel | 1.22 N·m/Arms | 9.6 Vrms/krpm | 0.58 Ω; 187–339 µH | 405 g (380 g in manual) | 17 / 6 | Class B | V |
| RobStride RS03 | n/p | ?/42 (36N42P likely, E) | 106×106×56 | 9:1, machined steel | 2.36 N·m/Arms | 17 Vrms/krpm (Kv ≈42) | 0.39 Ω; 0.275 mH | 880 g | 60 / 20; 43 Apk peak, 12 Apk rated | Class B | V |
| RobStride RS04 | n/p | ?/42 (36N42P likely, E) | 120×120×56 | 9:1, machined steel | 2.1 N·m/Arms | "16.9 Vrms/rpm" (sic, = krpm; Kv ≈42) | 0.16 Ω; 0.211 mH | 1420 g | 120 / 40; 90 Apk peak, 27 Apk rated | Class B | V |
| RobStride RS05 | n/p | ?/20 | 46×46×44 | 7.75:1, machined steel | 0.94 N·m/Arms | 7.4 Vrms/krpm (Kv ≈96) | n/p | 191 g | 5.5 / 1.6 | — | V |
| RobStride RS06 | n/p | ?/28 | 88×88×49 | 9:1, machined steel | 1.1 N·m/Arms | 7.6 Vrms/krpm (Kv ≈93) | n/p | 621 g | 36 / 11; 57 Apk | — | V |
| RobStride RS10P | n/p | ?/28 | 78.5×78.5×45.5 class | 25:1, machined steel | 3.73 N·m/Arms | 9.5 Vrms/krpm | 1.41 Ω; 750 µH | 460 g | 42 / 14 (at 100 rpm) | — | V |
| RobStride EduLite05 | n/p | ?/20 | 46×46×44 | 9:1, **powder metallurgy** gears | 0.94 N·m/Arms | 7.4 Vrms/krpm | 2.72 Ω; 0.813 mH | 242 g | 6 / 1.8 | — | V |
| Xiaomi CyberGear (EOL) | n/p (outer-rotor not confirmed) | ?/28 | Φ58 (driver), size n/p | 7.75:1 planetary | 0.87 N·m/Arms | 0.054–0.057 Vrms/rpm output-side (≈7.0–7.4 Vrms/krpm motor-side, E) | line 0.45 Ω; 187–339 µH | 317 g | 12 / 4 (24 V) | warning 75 °C, fault 80 °C default; Class B | V (manual mirror) |
| MIT Mini Cheetah | outer rotor (custom rotor on hobby stator) | 36/42 (U) | iFlight BE8108-class stator (≈81 mm × 8 mm, E from name) | 6:1 single-stage planetary; knee 9.33:1 (extra belt stage) | motor-side "KT .05 (flux linkage × pole pairs)", 0.075 N·m per peak A (U); output 0.84 N·m/A per Urs et al. | n/p | R 0.173 Ω (control model) | 480 g (U); rotor 0.055 kg | 17 / 6.9 N·m continuous | R_th 1.23 °C/W (U) | mixed (see notes) |
| MIT Humanoid U10 module | outer rotor (T-Motor U10 base) | 36/42 (U10 II) | Ø101 × 36 mm module | 6:1 planetary | n/p | n/p | n/p | 619 g | 33.6 N·m; 55 rad/s at 60 V | n/p | V (paper) |
| MIT Humanoid U12 module | outer rotor (T-Motor U12 base) | 36/42 (U12 II) | Ø120 × 44 mm module | 6:1 planetary | n/p | n/p | n/p | 1174 g | 68 N·m; 45 rad/s at 60 V | n/p | V (paper) |
| MIT Cheetah 3 (context) | custom | n/p | n/p | abad/hip 7.667:1, knee 8.846:1 | motor "KT 0.266" | n/p | R 0.45 Ω | n/p | motor τmax 27.2 N·m (≈208 N·m at hip, E) | n/p | V (control code) |
| Unitree A1 motor | n/p | n/p | n/p | planetary; 9.1:1 (U) | 0.9287 N·m/A (output) | n/p | n/p | 605 g | 33.5 N·m; 21 rad/s | temperature sensor | V (official page) |
| Unitree GO-M8010-6 (Go1) | n/p | n/p | n/p | 6.33:1 planetary | n/p | n/p | n/p | ≈530 g (U) | 23.7 N·m; 30 rad/s | n/p | V/U (official page via search excerpt) |
| Unitree Go2 joint motor | **outer rotor** | **36/42**, fractional slot (2/7 SPP), **delta** | housing ≈96 mm × 40 mm | planetary, fixed ring: **sun 9 / planet 19 / ring 47 → 6.22:1** | Kt_phase ≈0.22; Kt_q ≈0.26 N·m/A (motor side) | Ke ≈0.22 V·s/rad (line); Kv ≈44 rpm/V | R_line ≈440 mΩ; L_line ≈165 µH | n/p | sim "Go2HV": 20.2 / 23.4 N·m, 30 rad/s (V) | n/p | VT (Simplexity teardown) + V (sim) |
| Unitree G1 knee/hip roll (N7520-22.5) | **inner rotor** (U) | **18/16** (U, teardown summary) | "7520" ≈ 75 mm × 20 mm stator class (E from naming) | 2-stage planetary 4.5 × 5.0 = 22.5:1 | n/p | n/p | n/p | ≈1 kg actuator (U) | 111/131 N·m model; 139 N·m sim limit; rotor J 0.489e-4 kg·m² | knee: vapour chamber / heat pipe (U) | V (unitree_rl_lab) + U |
| Unitree G1 hip pitch/yaw (N7520-14.3) | inner rotor (U) | n/p | same N7520 motor | 4.5 × (48/22 + 1) = 14.3:1 | n/p | n/p | n/p | n/p | 71/83.3 N·m; 22.6/35.5 rad/s | — | V (unitree_rl_lab) |
| Unitree G1 arm/ankle (N5020-16) | inner rotor (U) | n/p | "5020" class | (46/18 + 1)(56/16 + 1) = 16.0:1 | n/p | n/p | n/p | ≈525 g "small joint" (U) | 24.8/31.9 N·m; 30.9/40.1 rad/s | — | V (unitree_rl_lab) + U |
| Unitree H1 M107 | **internal-rotor PMSM** | n/p | Ø107 × 74 mm, hollow shaft | variants M107-15 and M107-24 (ratio from name, E) | n/p | n/p | n/p | 1.9 kg | 360 N·m (knee); 189 N·m/kg | n/p | V (reference_robots_raw.md) |
| CubeMars AK80-9 V3 KV100 | outer rotor (E) | **36N42P** (21 pole pairs) | Ф98 × 38.5 mm | 9:1 planetary; backlash 15′ | 0.095 N·m/A (motor side) | KV 100; Ke 10 V/krpm | 160 mΩ phase; 116 µH | 490 g | 22 / 9 N·m | NTC MF51B 103F3950; insulation class C | V |
| CubeMars AK10-9 V3 KV60 | outer rotor (E) | **36N42P** | Ф98 × 61.7 mm | 9:1 planetary | 0.16 N·m/A | KV 60; Ke 16.7 V/krpm | 248 mΩ; 213 µH | 940 g | 53 / 18 N·m | Km 0.32 N·m/√W | V |
| T-Motor U8 (Mini Cheetah class) | outer | 36N42P (E, U8 family) | gap radius 40.8 mm, length 8.0 mm | — | 0.14 N·m/A | — | 0.279 Ω (delta); 0.069 µH (sic) | 242 g | — | Km 0.23 N·m/√W | V (Urs et al. Table 1) |
| T-Motor U10 II KV100 | outer | 36N42P | Φ98.6 × 33.1 mm | — | — | KV 100 | 101 ± 5 mΩ | 415 g | — | — | U (resellers) |
| T-Motor U12 II KV120 | outer | 36N42P | Φ106.8 × 47.6 mm | — | — | KV 120 | 22 mΩ | 778 g | 95 A peak (180 s) | — | V (T-Motor store) |
| Berkeley Humanoid Lite 6512 / 5010; ODRI | — | see `actuator_technology_raw.md` §3 (rows 1–3) and §2.1–2.2 | | | | | | | | | already covered |

### 1.2 Derived motor constants (ESTIMATED)

Method: Kt_motor = Kt_output / N; Kt check from back-EMF as in §0; P_cu at peak from published Apk and R_line; Km as in §0. RobStride back-EMF is assumed to be **motor-side, line-line RMS**. That assumption reproduces the published Kt within 1–7 % for every model except RS04 (17 %), which supports it.

| Model | Kt motor-side (N·m/Arms) | Kt from back-EMF | Ratio of the two | Kv (rpm/V) | Kt × Ipk(rms) vs published peak | Cu loss at peak current | Km motor / output (N·m/√W) | Torque at 100 W Cu loss |
|---|---|---|---|---|---|---|---|---|
| RS00 | 0.148 | 0.157 | 0.94 | ≈74 | 16.2 vs 14 | R n/p | — | — |
| RS01/RS02 | 0.157 | 0.159 | 0.99 | ≈74 | 19.8 vs 17 | ≈230 W | 0.169 / 1.31 | ≈13 N·m |
| RS03 | 0.262 | 0.281 | 0.93 | ≈42 | 71.8 vs 60 | ≈540 W | 0.343 / 3.09 | ≈31 N·m |
| RS04 | 0.233 | 0.280 | 0.83 | ≈42 | 133.6 vs 120 | ≈970 W | 0.476 / 4.29 | ≈43 N·m (rated 40) |
| RS05 | 0.121 | 0.122 | 0.99 | ≈96 | 7.3 vs 5.5 | R n/p | — | — |
| RS06 | 0.122 | 0.126 | 0.97 | ≈93 | 44.3 vs 36 | R n/p | — | — |
| RS10P | 0.149 | 0.157 | 0.95 | ≈74 | 50.1 vs 42 | ≈380 W | 0.103 / 2.56 | ≈26 N·m |
| CyberGear | 0.112 | 0.117 | 0.96 | ≈100 | 14.1 vs 12 | ≈180 W | 0.137 / 1.06 | ≈11 N·m |
| AK10-9 (for comparison) | 0.16 (published, motor) | — | — | 60 | — | — | 0.32 (published) / 2.88 | ≈29 N·m |
| AK80-9 | 0.095 | — | — | 100 | — | — | 0.2387 (published) / 2.15 | ≈21 N·m |

Readings (E):
- **RS04 has the highest motor constant in the set** (0.48 N·m/√W motor-side). That is about 1.5× the AK10-9 and implies a larger or longer stator than the Ф98 CubeMars motors. The 120 mm housing is consistent with a ~100–105 mm stator, but this is **not published**.
- RS03 and RS04 share pole count, back-EMF and ratio. They are probably the same lamination at two stack lengths or two windings: RS04 has 0.41× the resistance and 1.8× Km² (E).
- RS01/RS02 match CyberGear in pole count (28), ratio (7.75) and inductance (187–339 µH, identical text). RS02's Kt is 1.4× CyberGear's at 2× the bus voltage. This is consistent with the same frame wound for 48 V (E; the identical inductance range suggests a shared datasheet origin).
- A fixed winding temperature budget sets the continuous torque. At about 100 W of copper loss, RS04 gives ~43 N·m, which matches its 40 N·m rating. Use Km_output × √(allowed W) as a first sizing rule for an in-house design.
- Slot counts: every 42-pole motor found with published slots is 36N42P (U8, U10 II, U12 II, AK80-9, AK10-9, Go2). The 28-pole drone motors in `actuator_technology_raw.md` §4 are almost all 24N28P. So RS03/RS04 are **probably 36N42P** and RS00/01/02/06/10P **probably 24N28P** (E, not confirmed by any teardown).

### 1.3 Per-actuator notes and sources

**RobStride (all V).** Read on 2026-10-06 from the live site bundle `https://robstride.com/assets/index-f063c142.js`. The bundle hash is unchanged since 2026-09-24. Product keys present: robStride00, 01, 02, 02Ip67, 03, 04, 05, 06, 10P, eduLite05. **No RobStride model above 120 N·m exists on the official site as of 2026-10-06**, and none turned up in searches for 2026 launches (U for "none exist"; a China-only or OEM product could be missed). Verbatim snippets:
- RS04: `Poles 42`, `Reduction Ratio 9 : 1`, `Gear Material Machined Steel`, `Back-EMF 16.9Vrms/rpm ±10%`, `Line Resistance 0.16Ω ± 10%`, `Torque Constant 2.1N.m/Arms`, `Inductance 0.211mH ± 10%`, `Peak Phase Current 90Apk`, `Rated Load Speed 50rpm`, `Insulation Level Class B`.
- RS03: `Poles 42`, `9 : 1`, `Back-EMF 17Vrms/krpm`, `Line Resistance 0.39Ω`, `Torque Constant 2.36N.m/Arms`, `Inductance 0.275mH`, `Peak Phase Current 43Apk`.
- RS02: `Poles 28`, `7.75 : 1`, `Back-EMF 9.6Vrms/krpm`, `Line Resistance 0.58Ω`, `Torque Constant 1.22N.m/Arms`, `Inductance 187~339μH`.
- RS06: `Poles 28`, `9 : 1`, `Back-EMF 7.6 Vrms/kRPM`, `Torque Constant 1.1 N.m/Arms`, `Max Load Phase Current(Peak) 57 Apk`.
- RS10P: `Reduction Ratio 25 : 1`, `Line Resistance 1.41Ω`, `Torque Constant 3.73N.m/Arms`, `Inductance 750±20μH`, `Moment Inertia 0.00625kgm2`.
- EduLite05: `Gear Material Powder Metallurgy`, `Line Resistance 2.72Ω`, `Inductance 0.813mH`.
- Not published: stator diameter, stack length, slot count, magnet grade, winding, rotor topology (inner or outer), tooth counts. **No RobStride teardown was found** in English or Chinese searches (Bilibili, Zhihu, CSDN keywords tried).

**Xiaomi CyberGear (V, manual mirror).** AIFITLAB wiki copy of the official user manual, https://aifitlab-wiki.super.site/xiaomi-cybergear-docs/xiaomi-cybergear-micro-motor-user-manual:
- "Number of Poles: 28 poles"; "Gear Ratio: 7.75 : 1"; "Line Resistance: 0.45Ω ±10%"; "Torque Constant: 0.87 N·m / Arms"; "Motor Inductance: 187 - 339 μH"; "Motor Back EMF: 0.054 - 0.057 Vrms/rpm"; "Peak Current (Peak): 23A"; "Rated Voltage: 24 VDC"; over-temperature fault 80 °C and warning 75 °C (defaults).

Teardown evidence (U, SimpleFOC forum, https://community.simplefoc.com/t/xiaomi-cyber-dog-geared-motor-60/3855):
- hansihe (2023-12-02): "It has a GD32F303 inside"; the encoder is on the underside of the PCB.
- Owen_Williams (2024-02): an SPI Infineon gate driver, and "spi2 to as5047"; the CyberDog has a 240 Ω CAN termination.
- jgillick (2025-03): the encoder is motor-side, about 8 turns per output turn.
- Xiaomi's own download (password "QDD1") contains a 3D model of the motor. I did not download it: the link is a Xiaomi cloud folder.

**MIT Mini Cheetah.**
- Gear ratios (V): `_abadGearRatio = 6`, `_hipGearRatio = 6`, `_kneeGearRatio = 9.33`, `_motorKT = .05; // this is flux linkage * pole pairs`, `_motorR = 0.173`, `_motorTauMax = 3.f`, `_batteryV = 24`, rotor mass 0.055 kg (`common/include/Dynamics/MiniCheetah.h`, https://github.com/mit-biomimetics/Cheetah-Software).
- Motor source (V, Katz blog, https://build-its-inprogress.blogspot.com/2019/03/hello-there-mini-cheetah.html): modified off-the-shelf iFlight BE8108-class motors, with MoS₂ grease in the gearbox.
- Urs et al. 2022 Table 2 (V, secondary-academic, arXiv 2202.12395): MC ratio "6:1"; "Eff. Torque Const. KTa 0.84 Nm/A"; "Eff. Motor Const. KMa 1.38"; continuous 6.9 N·m.
- U from search excerpts: 36 slots / 42 poles; "42x 12x5x3 N52 magnets"; 0.075 N·m per peak phase amp; R 0.105 Ω; thermal resistance 1.23 °C/W; 480 g; 96 × 40 mm; 40 rad/s.
- The Kt value 0.075 = 1.5 × 0.05 is consistent with the firmware comment (E). It conflicts with Urs's 0.84/6 = 0.14 motor-side (different current definitions; unresolved).
- **The Katz thesis (dspace.mit.edu/handle/1721.1/118671) could not be opened.** An AWS WAF captcha blocked both curl and WebFetch. So the stator stack length, turns and planetary tooth counts were **not obtained**.

**MIT Humanoid (V)**, Chignoli, Kim, Stanger-Jones, Kim, "The MIT Humanoid Robot", arXiv 2104.09025, Tables I–II:

| Joint | Motor module | Gear ratio | Max torque | Max joint speed |
|---|---|---|---|---|
| Hip yaw / ab-ad | U10 | 6.0 | 33.6 N·m | 55 rad/s |
| Hip flexion | U12 | 6.0 | 68.0 N·m | 45 rad/s |
| Knee | U12 | 12.0 | 136.0 N·m | 22.5 rad/s |
| Ankle | U10 | 9.33 | 52.2 N·m | 35 rad/s |
| Shoulder ab-ad / flexion | U10 | 6.0 | 33.6 N·m | 55 rad/s |
| Elbow | U10 | 9.33 | 52.2 N·m | 35 rad/s |

- Module data: U10 619 g, Ø101 × 36 mm, output inertia 0.0023 kg·m². U12 1174 g, Ø120 × 44 mm, output inertia 0.02 kg·m².
- Robot: about 21 kg and 0.7 m (hip height scale); 60 V, 3 Ah pack. "no torque or force sensors"; "The knee, ankle and elbow joints contain a belt gearing system."
- E: the knee belt stage is 2:1 (12/6) and the ankle/elbow stage 1.555:1 (9.33/6), the same 1.555 as the Mini Cheetah knee.

**Unitree Go2 motor (VT)**, Simplexity Product Development teardown, https://www.simplexitypd.com/blog/unitree-go2-motor-teardown/:
- "out-runner design"; "36 slots … and 42 poles (or 21 pole-pairs)"; delta wound.
- "R_line ~= 440 mOhms"; "L_line ~= 165 uH"; "Kv_line = 95 RPM / 2.15V ~= 44 RPM/V_line"; "Kt_q = Ke_q ~= 0.26 N*m/A".
- Gears: "Sun (9), Planet (19 each), Ring (47)"; "Ratio = 1 + (47/9) ~= 6.22 to 1"; diametric ring magnet with an absolute magnetic encoder IC; six power MOSFETs.
- Caveat (E): 9 + 47 = 56 is not divisible by 3. Three equally spaced planets would not mesh, and four planets of 19 teeth would collide (see §3.2). Either the planets are unequally spaced or a count is off by one. Unitree's GO-M8010-6 is specified at 6.33:1, which 18/39/96 with 3 planets satisfies exactly (E).

**Unitree G1 (V + U).**
- Ratios from Unitree's own actuator models (`unitree_rl_lab/.../unitree_actuators.py`, commit 4960b84, 2025-11-19):
  - N7520-14.3: gear_1 4.5, gear_2 "48/22+1", rotor 0.489e-4 kg·m².
  - N7520-22.5: gear_1 4.5, gear_2 5.0.
  - N5020-16: "46/18+1" × "56/16+1"; rotor 0.139e-4.
  - N5010-16: 4 × 4.
  - W4010-25: 5 × 5.
  - Friction parameters, e.g. N7520-22.5 Fs 2.4 N·m and Fd 0.24 N·m·s/rad.
- Teardown summaries (U):
  - china-amass.net (2026-09-05) relays a teardown by "overseas engineer Grant": "an 18slot, 16pole motor, a 22.5:1 twostage planetary gear reducer, dual encoders, crossroller bearings"; about 1 kg. The joint has a hollow aluminium shaft with PTFE liner, needle bearing at the motor end, B6 bridge with two "R003" shunts, XT30 2+2 daisy-chain connectors, and a laser-ablated QFN MCU.
  - China Post Securities G1 teardown (2026-03-30, via longbridge.com): "internal rotor permanent magnet synchronous motor with a maximum speed of 3,000-5,000 RPM"; total ratio "approximately 20.58"; tooth counts sun 18 / planet 14 / ring 60 and sun 16 / planet 20 / ring 60 (as relayed by search); crossed roller bearings from Luoyang Baina, "CRBT355A 10E4J3"; small joint ≈525 g (60 × 70 mm), large joint ≈1100 g; knee "vapor chambers".
  - Munro Live (humanoid.guide): two-stage planetaries at about 15:1, "copper heat pipe against the motor stator", and two centrifugal fans at the hip.
- Cross-check (E): the securities-report tooth counts are geometrically impossible (18 + 2·14 = 46 ≠ 60; 16 + 2·20 = 56 ≠ 60). The rings were probably mis-transcribed. With rings of 46 and 56 they become exactly Unitree's N5020-16 stages (46/18 + 1)(56/16 + 1) = 16.0. Treat 20.58 as unreliable.

**Unitree A1 (V)**, https://www.unitree.com/A1/motor:
- "Maximum Instantaneous Torque: 33.5N·m"; "Torque Constant: 0.9287N·m/A"; "weight 605g"; "Maximum Joint Rotate Speed: 21rad/s".
- "0.2 mm silicon steel sheet material"; "Single-strand winding reduces resistance loss"; "dip paint technology"; "Oversized Industrial Grade Crossed Roller Bearings".
- The 9.1:1 ratio is widely used by community code but was **not confirmed** (U). The SDK hides it in a compiled `queryGearRatio()`.

**CubeMars AK80-9 / AK10-9 (V)**: https://www.cubemars.com/product/ak80-9-v3-0-robotic-actuator.html and …/ak10-9-v3-0-kv60-robotic-actuator.html. Values are in the table. AK80-9 output bearing: "Basic Dynamic Load Rating 2760 N", "Static 2810 N".

**T-Motor base motors.**
- U12 II KV120: "Configuration: 36N42P"; "Φ106.8*47.6 mm"; "Internal Resistance: 22mΩ"; "778g" (V, https://store.tmotor.com/product/u12-v2-kv120-u-efficiency.html).
- U8 (V, Urs et al., arXiv 2202.12365, Table 1): R 0.279 Ω, Kt 0.14 N·m/A, Km 0.23, inertia 1200 g·cm², 242 g, gap radius 40.8 mm, length 8.0 mm, delta, nt ≈ 16 turns.

### 1.4 What could not be found (motor internals)
- RobStride (any model): stator OD, stack, slot count, magnet grade, wire and turns, rotor topology. **No teardown found.**
- CyberGear: stator dimensions and tooth counts. The official 3D model sits in a Xiaomi cloud zip (password QDD1), which I did not fetch.
- MIT Mini Cheetah: stack length, turns, tooth counts (thesis behind a captcha).
- Unitree M107 and N7520: stator dimensions, magnets, winding. Only the G1 "18-slot/16-pole" teardown summary (U) exists.
- Magnet grades: only the Mini Cheetah's N52 (U). No vendor publishes it.

---

## 2. Torque and speed requirements of full-size humanoids, and human data

### 2.1 Robot joint torque and speed table

Unitree G1/H1/H1-2/H2 and the small robots are detailed in `reference_robots_raw.md`; only headline rows are repeated here. "Per kg" = peak knee torque ÷ robot mass (E).

| Robot | Height / mass | Knee peak | Hip pitch | Hip roll / yaw | Ankle | Waist | Shoulder / elbow | Joint speeds | Knee N·m/kg (E) | Label / source |
|---|---|---|---|---|---|---|---|---|---|---|
| Unitree H1 | 1.80 m / 47 kg | ≈360 | ≈220 (hip) | ≈220 | ≈59 | — | ≈75 (arm) | URDF: knee 14 rad/s, hip 23, ankle 9 | 7.7 | V (unitree.com/h1; URDF) |
| Unitree H1-2 | 1.78 m / 70 kg | ≈360 | ≈220 | ≈220 | ≈75 × 2 (parallel) | ≈220 | 120 / 120; wrist 30 | URDF: knee 14, hip 23, ankle 9 | 5.1 | V |
| Unitree H2 | 1.82 m / ≈70 kg | 360 ("leg torque max") | 360 (URDF) | 360 (URDF) | 66.9 / 19 (URDF) | — | — | URDF: hip/knee 20 rad/s; ankle pitch 28.6 | 5.1 | V (reference_robots_raw.md §A2b) |
| Fourier GR-1 (T2) | 1.65 m / ≈52 kg (official), 54.5 kg (URDF Σ) | 135 (URDF) | 135 | 84 / 65 | 41.7 / 41.7 | 65 (3 axes) | 38.5 / 30.3 | knee & hip pitch 18.5 rad/s; hip roll 7.6; ankle 10.3 | 2.5 | V (official: "maximum joint peak torque of 230N.m"; URDF FFTAI/Wiki-GRx-Models gr1t2.urdf) |
| Fourier GR-2 | n/p / 63.0 kg (URDF Σ) | **366** | **366** | 95.5 / 54.3 | 54.3 / 29.8 | 74.5 (yaw) | 74.5 / 42.8 | knee & hip pitch **6.5 rad/s**; hip roll 12.4; ankle 14.7–16.8 | 5.8 | V (gr2v3_8_7.urdf) |
| Fourier GR-3 | n/p / 69.7 kg (URDF Σ) | **366** | **366** | 140.4 / 140.4 | 59.4 / 59.4 | 140.4 yaw; 108.6 pitch/roll | 74.4 / 42.9 | knee & hip pitch 6.5 rad/s; hip roll/yaw 13.0; ankle 16.8 | 5.25 | V (gr3v2_1_1.urdf) |
| UBTech Walker S2 | 1.76 m / 70 kg | **225 peak / 75 rated** | 225 / 75 | roll 225/75; yaw 65/22 | 65/22 per motor (2-motor parallel) | pitch 265/79; yaw 85/35 | shoulder 80/27; elbow 45/17; wrist 20/17 | legs: rated 50 rpm, max **80 rpm (8.4 rad/s)**; waist pitch 20 rpm max | 3.2 | V (Walker S2 SDK document PDF) |
| AgiBot A2 Lite | 1.69 m / ≈64 kg | **270** | n/p | n/p | n/p | — | arm load ≈2 kg | max walk 0.8 m/s | 4.2 | V (agibot.com/products/A2_Pro page, A2 Lite spec) |
| AgiBot A2 family (marketing) | 1.75 m / 55 kg (U) | "integrated joint … peak torque of 512 Nm"; A2-Max arms 450 N·m, legs "8800N of thrust" | | | | | | | — | U (search excerpts of agibot.com / resellers) |
| Figure 02 | ≈1.68 m / ≈70 kg (U) | 150 ("L4 actuator: 150Nm torque with 135° ranges") | 150 ("L1 … 195°") | n/p | n/p | n/p | 50 (shoulder "A2 actuator") | n/p | ≈2.1 | U (interestingengineering.com, from Figure's teaser) |
| Tesla Optimus (AI Day 2022 → Gen 2/3) | 1.73 m / 57 kg (Wikipedia) or 73 kg (itmedia) | knee = linear actuator (likely 8,000 N class, E) via four-bar | rotary 110–180 class (E) | rotary | linear pair (500/3,900 N class, E) | rotary | elbow linear (2) | n/p | — | V (classes) / E (placement) — see §2.2 |
| Boston Dynamics electric Atlas (2026 product) | 1.90 m / 90 kg | n/p | n/p | n/p | n/p | n/p | lift 50 kg instant, 30 kg sustained | n/p | — | V-ish (robotsguide.com) |
| Agility Digit (V5) | ≈1.75 m / ≈65 kg (U) | n/p ("proprietary cycloidal actuator" legs) | n/p | n/p | n/p | — | lifts up to 22.7 kg repeatedly | n/p | — | U (automate.org) |
| Apptronik Apollo | 1.73 m / 73 kg (U) | n/p (linear actuators at knee and elbow) | n/p | n/p | n/p | — | 25 kg payload | n/p | — | U |
| 1X NEO | 1.65 m / ≈30 kg (U) | n/p ("Revo 2" in-house motors, tendon drive) | n/p | n/p | n/p | — | wrist 17.75; thumb CMC 3.5; finger MCP 2.6 | n/p | — | U (humanoid.guide) |
| XPeng IRON (2025) | n/p | n/p | n/p | n/p | n/p | flexible spine | 82 DoF total, 22 per hand | n/p | — | U (technode) |
| MIT Humanoid (research) | ≈0.7 m hip scale / 21 kg | 136 | 68 | 33.6 / 33.6 | 52.2 | — | 33.6 / 52.2 | knee 22.5 rad/s; hip 45–55 rad/s | 6.5 | V (arXiv 2104.09025) |
| Booster T1, G1, R1, BHL etc. | 1.2–1.3 m class | see `reference_robots_raw.md` | | | | | | | | — |

Observations (E):
- Two design camps exist.
  - "High-torque, slow": GR-2/GR-3 at 366 N·m and 6.5 rad/s, and Walker S2 at 225 N·m and 8.4 rad/s.
  - "Agile QDD": H1 at 360 N·m and 14 rad/s, GR-1 at 135 N·m and 18.5 rad/s, MIT Humanoid at 136 N·m and 22.5 rad/s.
- Knee peak normalized by robot mass ranges from **2.1 to 7.7 N·m/kg** (median ≈4–5). The human walking need is ~1 N·m/kg and the human running need ~3–3.5 N·m/kg (§2.3).
- Hip-pitch peak usually **equals the knee** (same actuator), while hip roll/yaw run at 25–60 % of knee.
- Ankles are 15–25 % of knee per motor, often as two motors in a parallel linkage.

### 2.2 Tesla Optimus details

- AI Day 2022 transcript (V, Whisper transcript, https://gist.github.com/L0rdCha0s/de22ae0c7e7a7a70b37ac9c1262e27e1):
  - "The robot that has 28 actuators".
  - "the resulting portfolio is six actuators … three rotary and three linear actuators".
  - Rotary: "a mechanical clutch integrated … On the high speed side angular contact ball bearing … on the low speed side a cross roller bearing and the gear train is a strain wave gear … three integrated sensors … bespoke permanent magnet machine".
  - Linear: "planetary rollers and an inverted planetary screw as a gear train".
  - The linear actuator "is able to lift a half ton nine foot concert grand piano".
  - Knee: a four-bar link that "linearized" the force requirement. Battery "2.3 kilowatt hours".
- Classes (U, widely reported and consistent): rotary **20 / 110 / 180 N·m** (frameless motor + harmonic reducer); linear **500 / 3,900 / 8,000 N** (frameless motor + inverted planetary roller screw).
  - 14 rotary units at shoulders, hips, waist and wrist roll; 14 linear units: 2 elbow, 4 wrist, 8 leg (knee and ankle).
  - Sources: humanoid.guide/linear-vs-rotary-actuators-humanoid-joints/; optimusk.blog; Chinese summaries (e.g. sina.cn).
- Per-actuator masses: commonly quoted from the AI Day slide as rotary 0.55 / 1.62 / 2.26 kg and linear 0.36 / 0.93 / 2.2 kg. **I could not find these in any accessible source.** Treat them as UNVERIFIED recollection and do not cite them.
- Independent corroboration of the two mid classes: NSK's 2026 technical review (V, https://www.nsk.com/tools-resources/research-and-development/technical-review/2026/actuators-for-robots/) gives these humanoid targets:
  - Rotary: "Repetitive peak torque: 110 N·m"; "approximately 110 N·m/kg"; "φ80 × L79 mm"; "1.0 kg or less"; "φ18 mm" bore.
  - Linear: "Maximum thrust: 3,900 N"; "approximately 4,300 N/kg"; "φ55 × L200 mm"; "0.9 kg or less".
- Gen 2 and Gen 3 (U): body actuators unchanged at 28; Gen 3 hands have 22 DoF with 25 forearm actuators per hand. In April 2026 Musk reportedly said V3 would not use the patented hand. A reported US$685 M Sanhua linear-actuator order exists. **No Gen 2/3 joint torque numbers were published.**

### 2.3 Human joint moments (75 kg reference unless stated)

| Activity | Hip (N·m/kg → N·m at 75 kg) | Knee | Ankle plantarflexion | Speed or notes | Label / source |
|---|---|---|---|---|---|
| Level walk 1.2–1.4 m/s | ext 0.5–1.0 → 38–75 | ext 0.46–1.27 → 35–95 | 1.2–1.9 → 90–143; push-off power 2.5–3.5 W/kg (190–260 W) | ankle 8–12 rad/s at push-off | V (compiled: "Human-Level Actuation for Humanoids", arXiv 2511.06796, Table 3, citing Winter 2009 etc.) |
| Level walk, young males (normative) | ext 0.72 | ext (early stance) 0.71 | 1.30 | self-selected | U (PMC4499994 Table 2 via search; page captcha-blocked) |
| Walk push-off (Winter) | flexor 0.4 | extensor 0.16 | — | ~55 % of gait cycle | V-secondary (clinicalgaitanalysis.com FAQ quoting Winter) |
| Stair ascent | 38–75 N·m | ≈1.0 → ≈75; 0.94 ± 0.29; 1.06–1.16 first peak | 1.4–1.8 → 105–135; 3.0–3.5 W/kg | 0.5–2 rad/s at knee | V (arXiv 2511.06796) + U (stair studies via search) |
| Stair descent | — | 0.60–1.01 | — | — | U (search excerpt) |
| Sit-to-stand (seat 10–40 cm) | 0.24–1.92 | 0.51–1.97 | 0.33–0.46 | **hip + knee peak sum ≈ 1.53 N·m/kg minimum**, invariant to strategy; n = 8, 63 kg | V (Yoshioka et al. 2014, BioMed Eng OnLine 13:27, PMC3995647) |
| Repetitive lift floor→waist | — | 3.0–3.4 → 225–255 | — | — | V-compiled (arXiv 2511.06796 Table 4) |
| Run 3.5 m/s | ext stance 2.02 ± 0.36 → 152 | ext midstance 3.12 ± 0.56 → 234 | 2.94 ± 0.35 → 220 | ankle power 16.1 W/kg | V (Schache et al. 2011, MSSE, Table 1) |
| Run 5.0 m/s | 2.95 → 221 | 3.52 → 264 | 3.55 → 266 | — | V (Schache 2011) |
| Sprint 8.95 m/s | 4.09 → 307; swing flexion −4.30 | 3.55 → 266 | 4.00 → 300 | hip power 41 W/kg terminal swing | V (Schache 2011) |
| Hip abduction (running 3.5 m/s) | 2.00 → 150 | knee abd 0.65 | ankle inversion 0.24 | frontal plane | V (Schache 2011) |

Key points (E):
- Walking needs only ~1 N·m/kg at knee and hip, but the ankle needs ~1.3–1.9 N·m/kg.
- Getting up from a chair needs ≥1.53 N·m/kg summed over hip and knee.
- Running needs ~3–3.5 N·m/kg at the knee and ~3–4 at the ankle.
- A human at 75 kg therefore needs ~75–100 N·m knee for walking and stairs, ~150 N·m for sit-to-stand with a knee-dominant strategy, and ~230–260 N·m for running or heavy squats.

### 2.4 Synthesis: torque targets for a 1.6–1.9 m, 60–80 kg robot (ESTIMATED)

Method: human N·m/kg × robot mass × factor. The factor is 1.3 for robots' bent-knee gait and heavier distal mass, plus a 1.5× peak margin for disturbances and falls. Each target is checked against §2.1.

| Joint | Walking/stairs need at 70 kg | Recommended peak (walk, stairs, sit-to-stand, light jog) | Precedent | Speed target |
|---|---|---|---|---|
| Knee | 70–90 N·m | **200–250 N·m** (≈3–3.5 N·m/kg) | Walker S2 225, A2 Lite 270, GR-1 135 (too low for 70 kg), H1 360 | 10–14 rad/s |
| Hip pitch | 50–70 N·m | **200–250 N·m** (same actuator as knee) | H1 220, Walker 225, GR-2/3 366 | 10–20 rad/s |
| Hip roll | 50–100 (frontal stance) | **120–220 N·m** | Walker 225, GR-3 140, GR-2 95 | 8–13 rad/s |
| Hip yaw | small | **60–140 N·m** | Walker 65, GR-3 140, GR-2 54 | 8–15 rad/s |
| Ankle pitch | 90–135 N·m (human!) | **120–150 N·m effective** (2 × 60–75 N·m motors in a parallel linkage) | H1-2 75 × 2, GR-3 59, Walker 65 × 2 | 10–15 rad/s |
| Ankle roll | small | 40–60 N·m | GR-3 59, H1-2 40 | — |
| Waist yaw / pitch | — | 80–140 / 150–265 N·m | Walker 85 / 265; GR-3 140 / 109 | 2–8 rad/s |
| Shoulder pitch/roll | — | 50–80 N·m | Walker 80, GR-2/3 74 | 6–8 rad/s |
| Elbow | — | 40–50 N·m | Walker 45, GR-2/3 43 | 6 rad/s |
| Wrist | — | 15–20 N·m | Walker 20, GR-2/3 17 | 9 rad/s |

---

## 3. Planetary and cycloid gearbox practice for QDD

### 3.1 Published or measured tooth counts

| Actuator | Topology | Sun / planet / ring (× planets) | Ratio | Module, material | Label / source |
|---|---|---|---|---|---|
| mjbots qdd100 gearset | 1-stage, sun input, ring fixed | 20 / 40 / 100 (× 3) | 6.0 | m0.5; 42CrMo / C40Cr, HRC 25; needle-bearing planets (HK0608) | V (in `actuator_technology_raw.md` §2.4) |
| ISSPG design for T-Motor U12 (paper) | internal 1-stage | 20 / 40 / 100 (× 3) | 6.0 | m0.5; "cast carbon steel"; 92.3 % efficiency (model) | V (arXiv 2506.16356) |
| ESSPG design for U12 (paper) | external 1-stage | 20 / 52 / 124 (× 3) | 7.2 | m0.5; 93.3 % efficiency (model) | V (same) |
| Unitree Go2 motor | 1-stage, fixed ring | 9 / 19 / 47 | 6.22 | n/p | VT (Simplexity) |
| Unitree G1 N7520-14.3 | 2-stage | stage 1 ratio 4.5; stage 2 = 48/22 + 1 → sun 22 / ring 48 (planets 13, E) | 14.3 | n/p | V (ratio formula) / E (planets) |
| Unitree G1 N7520-22.5 | 2-stage | 4.5 × 5.0 | 22.5 | n/p | V |
| Unitree G1 N5020-16 | 2-stage | sun 18 / ring 46 (planets 14, E) then sun 16 / ring 56 (planets 20, E) | 16.0 | n/p | V (ratio formula) / E |
| Unitree G1 W4010-25, N5010-16 | 2-stage | 5 × 5; 4 × 4 | 25; 16 | n/p | V |
| MIT Mini Cheetah | 1-stage + knee belt | **n/p (thesis blocked)** | 6 (knee 9.33) | n/p | V (ratios) |
| MIT Cheetah 3 | 1-stage + knee stage | n/p | 7.667; knee 8.846 | n/p | V (ratios) |
| UCLA C-QDD | 10:1 cycloid inside stator, 4140 steel | see `actuator_technology_raw.md` row R1 | 10 | 4140 | V |
| Compound planetary example (C-QDD-style paper) | compound | sun 12; planets 36 & 22; ring 70 | — | — | U (search excerpt of arXiv 2410.16591) |

### 3.2 Tooth-count feasibility for common ratios (ESTIMATED arithmetic)

Rules for a simple planetary with standard (unshifted) gears, ring fixed and sun driving:
- ratio = 1 + Nr/Ns
- Nr = Ns + 2Np
- (Ns + Nr)/n must be an integer for n equally spaced planets
- planets must not collide: (Ns + Np)·sin(π/n) > Np + 2

Enumerated with Ns from 8 to 40 and Nr ≤ 130:

| Target ratio | Valid standard sets (Ns / Np / Nr, 3 planets) | Comment |
|---|---|---|
| 6.0 | 8/16/40, 9/18/45, 10/20/50, 12/24/60, 14/28/70, 15/30/75 … (20/40/100 at Nr ≤ 100) | easy; mjbots uses 20/40/100 at m0.5 |
| 6.33 (Unitree GO-M8010-6) | **18/39/96** | the only standard set ≤ 130 teeth |
| 7.75 (RobStride 01/02/05, CyberGear) | **none** with 3–5 planets and unshifted gears | Implies **profile-shifted gears**. E.g. 12/34/81 (Ns + Nr = 93, divisible by 3) needs a non-standard centre distance. This is an inference, not confirmed. |
| 9.0 (RobStride 03/04/06, AK80-9, AK10-9) | 8/28/64, 10/35/80, **12/42/96**, 14/49/112, 16/56/128 | 12/42/96 is the most plausible at m0.5–0.7 (ring PCD 48–67 mm) |
| 10.0 (RobStride 00, many 10:1) | 9/36/81, 12/48/108 | — |
| 6.22 (Go2 teardown 9/19/47) | not equally spaceable with 3 planets; 4 planets of 19 T collide | check the teardown count |

Sun-tooth minimum: 17 teeth at a 20° pressure angle avoids undercut without shift. The paper constraint is Ns, Np ≥ 20 (arXiv 2506.16356). A 9-tooth sun (Go2) or 8–12-tooth sun (9:1) **must be positive-profile-shifted**, or the sun is cut on the motor shaft. This is normal in commercial QDDs and a key point for Indian gear shops, which must be able to hob or shape shifted small-tooth pinions.

### 3.3 Module, material, heat treatment
- Module range: "between mmin = 0.5 mm" and 1.2 mm "as per manufacturing limits" (V, arXiv 2506.16356). mjbots uses m0.5 (V).
- Sizing method: Lewis bending equation for face width with a safety factor (V, arXiv 2506.16356).
- Materials:
  - mjbots: 42CrMo / C40Cr through-hardened to only HRC 25 (V).
  - RobStride: "Machined Steel"; EduLite: "Powder Metallurgy" (V).
  - KOFON (Chinese humanoid reducer maker): sun and planets in **20CrMnTi**, carburized and quenched, "surface (typically HRC 58-64)", "core (HRC 30-45)" (U, search excerpt; page 403).
  - UCLA C-QDD cycloid in 4140 (V, existing file).
- Recommendation (E): for India, use 20MnCr5 (IS 4432 / EN 207; the 20CrMnTi analogue) carburized to HRC 58–62 with ground or honed teeth. The alternative is 42CrMo4 (EN19) nitrided for lower-volume CNC work. The ring is often 42CrMo4 QT + nitrided or a 7075 insert for light joints. The mjbots HRC 25 set is a low-cost lower bound, not a target.
- Pressure angle: no vendor publishes one. The literature uses 20°, and high pressure angles appear in printed-gear work (Urs cites Miller, "very strong gear teeth by means of high pressure angles").

### 3.4 Output bearings
- Crossed-roller output bearings are standard on commercial QDDs:
  - Unitree A1: "Oversized Industrial Grade Crossed Roller Bearings" (V).
  - Unitree M107: crossed roller (V, reference file).
  - Unitree G1: crossed roller, supplier Luoyang Baina, part "CRBT355A" (U). Under IKO CRBT naming that is a 35 mm bore × 5 mm wide super-slim bearing, ≈46 mm OD (E).
  - Damiao "P" suffix = crossed roller (V, existing file).
  - SteadyWin GIM10015 (V, existing).
- Optimus rotary: crossed roller on the low-speed side, angular-contact ball on the high-speed side (V, transcript).
- Schaeffler's humanoid planetary actuator (CES 2026): 2-stage, 60–250 N·m (V-ish news, roboticsandautomationnews.com). Crossed-roller use there is not confirmed.
- CubeMars AK80-9 output bearing: C = 2760 N dynamic, C₀ = 2810 N static (V). That is small relative to a humanoid knee's radial and moment loads (E).

### 3.5 Backlash, efficiency and life
- Backlash (V, in `actuator_technology_raw.md` §1B): 6–18 arcmin for 1-stage QDDs. Examples: CubeMars 9–18′ (AK80-9 15′), LK-Tech ≤6–10′, MyActuator ≤10–15′.
- Efficiency: single-stage planetary 92–96 % modelled (arXiv 2506.16356).
  - RobStride's Kt-vs-back-EMF ratio (§1.2) implies ≈93–99 % torque transfer for most models and ≈83 % for RS04 at its test point (E).
  - Roller screws: "75 to 80%" (humanoid.guide, U).
- Friction: Unitree models static friction 1.6–2.4 N·m and viscous 0.16–0.24 N·m·s/rad for the N7520 joints (V). That is about 1.5–2 % of peak torque.
- Life: **no QDD vendor publishes an L10 or rated-life figure.** AgiBot claims "stable operation for thousands of hours" (U). The only life data found are for printed reducers (existing file §3). Plan in-house life tests: design for ≥10⁷ sun-tooth cycles at rated torque under AGMA/ISO 6336 bending and pitting checks (E).

### 3.6 Two-stage and belt-assisted practice
- Unitree G1 uses only 2-stage planetaries (14.3–25:1) with inner-rotor motors. Unitree H1 M107 comes in 15 and 24 ratio variants (E from names M107-15 and M107-24).
- RobStride 10P: 25:1. Schaeffler: 2-stage, 60–250 N·m.
- MIT keeps 6:1 at the motor and adds a 1.55–2:1 belt for knee, ankle and elbow. This puts the motor mass at the hip and gives 12:1 at the knee.
- Fourier GR-2/GR-3's 366 N·m at 6.5 rad/s implies a high-ratio reducer, likely ≥30:1 (E; type not published).
- Rule of thumb from the data (E):
  - ≤10:1 single stage gives ≥20 rad/s and good backdrive, but needs a large motor (RS04 class, ~1.4 kg for 120 N·m).
  - 14–25:1 two-stage gives 2–3× the torque per kg at 14–22 rad/s (G1 N7520-22.5: 139 N·m sim limit from a ~1 kg joint).
  - Full-size 200–360 N·m knees use either 2-stage planetaries (H1 M107: 1.9 kg) or linear and roller-screw drives (Optimus, Apollo).

---

## 4. Gaps and honest limits
1. **No RobStride teardown and no published RobStride stator geometry.** The slot counts in §1.1–1.2 are inferences from pole count. Pole counts and electrical constants are official.
2. **Katz MIT thesis inaccessible** (captcha). Mini Cheetah tooth counts, stack length and turns are missing. The 36/42, N52 12×5×3 and Kt 0.075 values are UNVERIFIED search excerpts.
3. **CyberGear internals** (stator, gears) not found. The official 3D model exists in a Xiaomi cloud zip that I did not fetch.
4. **Unitree tooth counts:** only Go2 was measured (9/19/47, with a geometry inconsistency). G1 counts come from a securities report whose ring counts are wrong. Unitree's own ratio formulas (V) give partial counts.
5. **Optimus per-actuator masses and Gen 2/3 torques** were not found in any accessible source.
6. **Figure 02/03, Atlas, Digit, Apollo, NEO, IRON joint torques are not published.** Figure 02's 150 N·m is UNVERIFIED (teaser-derived).
7. **Human walking normative table** (PMC) was captcha-blocked; values come via a search excerpt or a compiled source. Schache 2011 (running) and Yoshioka 2014 (sit-to-stand) were read in full.
8. **Gear material** for specific products is published only as "machined steel" or "powder metallurgy" (RobStride). The 20CrMnTi carburizing data is a vendor excerpt (U).
9. **No QDD life ratings** from any vendor.

## 5. Source index (accessed 2026-10-06)
- RobStride site bundle (V): https://robstride.com/assets/index-f063c142.js (product pages https://robstride.com/products/robStride04 etc.)
- CyberGear manual mirror (V): https://aifitlab-wiki.super.site/xiaomi-cybergear-docs/xiaomi-cybergear-micro-motor-user-manual
- SimpleFOC CyberGear thread (U): https://community.simplefoc.com/t/xiaomi-cyber-dog-geared-motor-60/3855
- Unitree Go2 motor teardown (VT): https://www.simplexitypd.com/blog/unitree-go2-motor-teardown/
- Unitree actuator models (V): https://github.com/unitreerobotics/unitree_rl_lab (`assets/robots/unitree_actuators.py`)
- Unitree A1 motor (V): https://www.unitree.com/A1/motor ; Unitree H1 (V): https://www.unitree.com/h1
- G1 knee teardown summary (U): https://www.china-amass.net/news/deep-dismantling-of-unitree-g1-knee-joint-actuator-full-analysis-of-120-n%c2%b7m-torque-twostage-planetary-reduction-and-dual-encoders/
- China Post Securities G1 report summary (U): https://longbridge.com/en/news/281283080
- Munro G1 teardown summary (U): https://humanoid.guide/?p=17935
- CubeMars AK80-9 / AK10-9 (V): https://www.cubemars.com/product/ak80-9-v3-0-robotic-actuator.html ; https://www.cubemars.com/product/ak10-9-v3-0-kv60-robotic-actuator.html
- T-Motor U12 II (V): https://store.tmotor.com/product/u12-v2-kv120-u-efficiency.html
- Mini Cheetah control model (V): https://github.com/mit-biomimetics/Cheetah-Software (`common/include/Dynamics/MiniCheetah.h`, `Cheetah3.h`)
- Katz blog (V): https://build-its-inprogress.blogspot.com/2019/03/hello-there-mini-cheetah.html ; thesis (not accessible): https://dspace.mit.edu/handle/1721.1/118671
- Urs et al. 3D-printed QDD (V): https://arxiv.org/abs/2202.12395 ; RI50 vs U8 motor metrics (V): https://arxiv.org/abs/2202.12365
- MIT Humanoid (V): https://arxiv.org/abs/2104.09025
- ESSPG vs ISSPG (V): https://arxiv.org/abs/2506.16356 ; Task-oriented co-design vs DM8009 (V): https://arxiv.org/abs/2609.22795
- Fourier GR-1 intro (V): https://support-old.fftai.com/en/docs/GR-X-Humanoid-Robot/GR1/GR-1_Introduction/ ; URDFs (V): https://github.com/FFTAI/Wiki-GRx-Models
- UBTech Walker S2 SDK document (V): https://a.storyblok.com/f/298593/x/1329253096/ubtech-walker-s2-sdk-secondary-development-document-external.pdf
- AgiBot A2 (V): https://agibot.com/products/A2_Pro
- Figure 02 (U): https://interestingengineering.com/innovation/figure-02-worlds-most-advanced-humanoid-robot
- Atlas (V-ish): https://robotsguide.com/robots/atlas
- Tesla AI Day 2022 transcript (V): https://gist.github.com/L0rdCha0s/de22ae0c7e7a7a70b37ac9c1262e27e1 ; actuator classes (U): https://humanoid.guide/linear-vs-rotary-actuators-humanoid-joints/
- NSK humanoid actuator targets (V): https://www.nsk.com/tools-resources/research-and-development/technical-review/2026/actuators-for-robots/
- Human-Level Actuation for Humanoids (V, compiled biomechanics): https://arxiv.org/abs/2511.06796
- Schache et al. 2011 running kinetics (V): https://paulogentil.com/pdf/Effect%20of%20Running%20Speed%20on%20Lower%20Limb%20Joint%20Kinetics.pdf
- Yoshioka et al. 2014 sit-to-stand (V): https://pmc.ncbi.nlm.nih.gov/articles/PMC3995647/
- Winter push-off moments (V-secondary): https://clinicalgaitanalysis.com/faq/moment.html
- Schaeffler planetary actuator (V-ish news): https://roboticsandautomationnews.com/2025/12/30/schaeffler-presents-innovative-planetary-gear-actuator-for-humanoid-robots/97939/
