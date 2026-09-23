# JX1 India sourcing — Robu.in / Amazon.in browser capture (RAW)

- Project: JX1 low-cost compact humanoid (~1.2 m, 20–24 DOF), built in India.
- Date checked: **2026-09-24** (all rows).
- Method: the in-app browser loaded Robu.in search pages (`https://robu.in/?s=<query>&post_type=product`). For each search I read the result cards (title, SKU, "₹ price (Incl. GST)", Add to Cart / Out of Stock / Backorder). For top candidates I opened the product page and read its Specification table and Description.
- Supplier "Robu" = Robu.in (MACFOS Ltd, Pune). All Robu prices below are **as displayed, "(Incl. GST)"**.
- Stock: **IN** = "Add to Cart" shown; **OOS** = "Out of Stock" shown; **BO** = "Add to Cart (Backorder)".
- Evidence labels:
  - **VERIFIED-PP** = product page opened today; specs copied from its spec table/description.
  - **VERIFIED-SR** = seen today on a Robu search-results card (title/SKU/price/stock only). Specs in those rows come **only from the product title**.
  - **UNVERIFIED** = not seen on a page today.
- Page errors and contradictions are copied as shown and flagged ("page shows …").
- No login, no cart, no forms. Nothing on this page was bought.

---

## 1. Integrated robot actuators / joint motors (CAN)

| Item | Brand/Model | SKU | Supplier | Price ₹ (incl GST?) | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| T-motor CubeMars AK10-9 V2.0 100KV Brushless DC Actuator Robot Joint Motor | CubeMars AK10-9 V2.0 | 1374857 | Robu | 104,809 (incl GST) | IN | KV100; rated 15 N·m, peak 38 N·m; peak current 50 A (page also lists "Rated Current 185 A", which looks like a page error); 42 poles (21 pole pairs); rated speed 222/445 rpm (output); 820 g; 12-bit encoder; UART/CAN; Kt 0.095; phase-phase R 90±5 mΩ, L 331±10 µH; OD ~98 mm (desc "Op(mm) 098"); integrated reducer + controller; configured with RUBIK Link. Gear-ratio field shows "0.375694444", probably 9:1 entered as a time value. Package line says "AK10-9/V1.1". | https://robu.in/product/t-motor-cubemars-ak10-9-v1-1-100kv-brushless-dc-actuator-robot-joint-motor/ | 2026-09-24 | VERIFIED-PP |
| T-Motor CubeMars Ak80-9 V3.0 100KV Brushless Dc Actuator Robot Joint Motor | CubeMars AK80-9 V3.0 | R256311 | Robu | 79,739 (incl GST) | OOS | KV100, 9:1 (title) | https://robu.in/product/t-motor-ak80-9-v3-0-actuator-100kv-brushless-dc/ | 2026-09-24 | VERIFIED-SR |
| T Motors AK60-6 V1.1 80KV Cube Mars Motor | CubeMars AK60-6 V1.1 | 1722066 | Robu | 33,919 (incl GST) | OOS | KV80; 24 V; rated 3 N·m; rated speed 233/420 rpm; star winding; 6:1 planetary (ratio field shows "0.250694444"); NTC MF51B 103F3950; integrated BLDC + planetary + encoder + driver; servo and MIT modes | https://robu.in/product/t-motors-ak60-6-v1-1-80kv-cube-mars-motor/ | 2026-09-24 | VERIFIED-PP |
| T Motor AK70-10 KV100 Brushless Robot Motor (Without Driver) | T-Motor AK70-10 | 1402969 | Robu | 53,299 (incl GST) | OOS | KV100, 10:1, no driver (title) | https://robu.in/product/t-motor-ak70-10-kv100-brushless-robot-motor/ | 2026-09-24 | VERIFIED-SR |
| T Motors AK80-64 6-8S Legged Robot Power-KV80 | T-Motor AK80-64 | 1842324 | Robu | 104,639 (incl GST) | OOS | KV80, 6–8S (title) | https://robu.in/product/t-motors-ak80-64-6-8s-legged-robot-power-kv80/ | 2026-09-24 | VERIFIED-SR |
| xTerra Robotics – Actuator QDD A2 | xTerra Robotics QDD A2 | R258076 | Robu | 94,400 (incl GST) | OOS | Quasi-direct-drive joint; rated 3 N·m, peak 12 N·m; 10–24 VDC; max 20 A; FOC; CAN FD; 14-bit encoder; OD 77 mm × width 50 mm; 550 g; 360 rpm @24 VDC | https://robu.in/product/xterra-actuator-qdd-a2/ | 2026-09-24 | VERIFIED-PP |
| T-Motor CubeMars RI80 KV75 Brushless DC Inner Runner Robot Joint Motor (with Hall sensor) | CubeMars RI80 KV75 (frameless) | R256265 | Robu | 22,929 (incl GST) | IN | Frameless BLDC inrunner (you add your own bearings, reducer, encoder and driver); rated 1.45 N·m, peak 4.1 N·m; 24–48 V; rated 9.4 A; KV75; 8 pole pairs; delta winding; Ke 15.5 V/krpm; Hall sensor | https://robu.in/product/t-motor-cubemars-ri80-kv75-brushless-dc-inner-runner-robot-joint-motor-with-hall-sensor/ | 2026-09-24 | VERIFIED-PP |
| T-Motor CubeMars RI100 KV105 Brushless DC Inner Runner Robot Joint Motor (with Hall sensor) | CubeMars RI100 KV105 (frameless) | R256266 | Robu | 21,589 (incl GST) | IN | Frameless inrunner with Hall sensor; FOC-optimised; KV105 (title). Spec table was empty and the description was cut off, so torque and current were not captured. | https://robu.in/product/t-motor-cubemars-ri100-kv105-brushless-dc-inner-runner-robot-joint-motor-with-hall-sensor/ | 2026-09-24 | VERIFIED-PP (partial) |
| Seeed Studio reBot Arm B601-DM (Without Power Supply) | Seeed reBot Arm B601-DM | R264651 | Robu | 238,519 (incl GST) | BO | Complete arm kit. The "DM" suffix may mean Damiao motors, but that was not checked. Reference only. | https://robu.in/product/seeed-studio-rebot-arm-b601-dm-without-power-supply/ | 2026-09-24 | VERIFIED-SR |
| Unitree G1 Humanoid Robot (Unassemble) | Unitree G1 | R257706 | Robu | 3,875,299 (incl GST) | BO | Complete humanoid (reference / benchmark only) | https://robu.in/product/unitree-g1-humanoid-ai-agent-robot/ | 2026-09-24 | VERIFIED-SR |
| Unitree R1 Humanoid Robot (Unassemble) | Unitree R1 | R257707 | Robu | 1,332,629 (incl GST) | BO | Complete humanoid (reference only) | https://robu.in/product/unitree-r1-humanoid-robot/ | 2026-09-24 | VERIFIED-SR |
| Hiwonder AiNex Standard Kit / With Raspberry Pi 4B 4GB | Hiwonder AiNex | R213294 | Robu | 95,379 (incl GST) | OOS | Small bus-servo humanoid kit (reference only) | https://robu.in/product/hiwonder-ainex-ros-education-ai-vision-humanoid-robot-powered-by-raspberry-pi-biped-inverse-kinematics-algorithm-learning-teaching-kit/ | 2026-09-24 | VERIFIED-SR |

**Searches in category 1 with no relevant Robu result:**
- No products found: "Damiao", "Robstride", "MyActuator", "LKMTech", "cycloidal".
- Unrelated results only: "DM-J4310", "DM-J8009", "RMD-X8", "SteadyWin", "GIM8108", "GIM6010", "MG4010", "harmonic reducer", "quasi direct drive".
- "Unitree motor": complete Unitree robots and arms only, all on backorder; no bare joint motors.
- "planetary actuator": only brushed or BLDC planetary gearmotors (Pro-Range PG36/PG42/PG28BL, IG45, IG52). These are not back-drivable joint actuators. Examples: Pro-Range PG42BL4224-10.2K 24 V BLDC planetary, 63.76 N·cm, 470 rpm, SKU 812263, ₹4,479, IN; PG28BL-462K, 225.63 N·cm, 11 rpm, SKU 812259, ₹3,579, IN (VERIFIED-SR).
- "robot joint motor" / "CubeMars" / "T-motor AK": only the CubeMars/T-Motor rows above.

---

## 2. BLDC outrunner motors for DIY actuators

| Item | Brand/Model | SKU | Supplier | Price ₹ (incl GST?) | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| 5010 360KV High Torque Brushless Motor for Drone | Generic (Robu) 5010 360KV | 45571 | Robu | 1,799 (incl GST) | IN | 2–6S; ESC 20–40 A; 4 mm shaft; 50 × 50 mm (L × W); 112 g; 14–16" props; black or silver may ship | https://robu.in/product/5010-360kv-high-torque-brushless-motors-multicopter-quadcopter-multi-axis-aircraft/ | 2026-09-24 | VERIFIED-PP |
| 5010 750KV High Torque Brushless Motor for Drone | Generic 5010 750KV | 45573 | Robu | 1,699 (incl GST) | IN | 5010, 750 KV (title) | https://robu.in/product/5010-750kv-high-torque-brushless-motors-multicopter-quadcopter-multi-axis-aircraft/ | 2026-09-24 | VERIFIED-SR |
| Tarot Martin Brushless Motor … 12S/5010/130KV TL50M10 | Tarot TL50M10 5010 130KV | R211413 | Robu | 4,779 (incl GST) | IN | 130 KV; 28 poles; stator 50 mm, stator end thickness 10 mm; motor OD 55.6 mm; length 27 mm; φ4 mm shaft (26.9 mm long); 12S; 25 mm symmetric mount holes; mass not listed | https://robu.in/product/tarot-martin-brushless-motor-multi-rotor-high-efficiency-long-endurance-motor-12s-5010-130kv-tl50m10/ | 2026-09-24 | VERIFIED-PP |
| Tarot Martin Brushless Motor … 12S/6009/130KV TL60M09 | Tarot TL60M09 6009 130KV | R211410 | Robu | 6,969 (incl GST) | IN | 130 KV; stator 60 mm (6009); poles "20P"; length 26 mm; shaft 27.4 mm; 25 mm mount; page shows "Rated Voltage 20 V" (title says 12S); mass not listed | https://robu.in/product/tarot-martin-brushless-motor-multi-rotor-high-efficiency-long-endurance-motor-12s-6009-130kv-tl60m09/ | 2026-09-24 | VERIFIED-PP |
| Tarot TL3009 6012/132KV Martin Brushless Motor | Tarot TL3009 6012 132KV | 1578671 | Robu | 7,249 (incl GST) | IN | 132 KV; Φ68 × 29.8 mm; stator 60 × 12 mm; 24P; 8 mm shaft; 20 A continuous; 880 W max; 260 g (from the package line "Φ68×30 260g") | https://robu.in/product/tarot-tl3009-6012-132kv-martin-brushless-motor/ | 2026-09-24 | VERIFIED-PP |
| Tarot 5012/300KV Motor TL50P12 | Tarot TL50P12 | R211412 | Robu | 6,749 (incl GST) | IN | 5012, 300 KV (title) | https://robu.in/product/tarot-5012-300kv-motor-tl50p12/ | 2026-09-24 | VERIFIED-SR |
| TAROT TL96020 5008 340KV High Power Brushless Motor | Tarot TL96020 | R101295 | Robu | 5,549 (incl GST) | IN | 5008, 340 KV (title) | https://robu.in/product/tarot-tl96020-5008-340kv-high-power-brushless-motor/ | 2026-09-24 | VERIFIED-SR |
| Tarot 4114/320KV Brushless Motor for Multicopter DIY Drone | Tarot 4114 | 1357457 | Robu | 4,039 (incl GST) | IN | 4114, 320 KV (title) | https://robu.in/product/tarot-4114-320kv-brushless-motor-for-multicopter-diy-drone/ | 2026-09-24 | VERIFIED-SR |
| Tarot Martin … 6S/5006/290KV TL50M06 | Tarot TL50M06 | R211414 | Robu | 6,169 (incl GST) | OOS | 5006, 290 KV (title) | https://robu.in/product/tarot-martin-brushless-motor-multi-rotor-high-efficiency-long-endurance-motor-6s-5006-290kv-tl50m06/ | 2026-09-24 | VERIFIED-SR |
| Martin TL2954 6S 4006 320KV Brushless Motor | Tarot Martin TL2954 | R258262 | Robu | 3,239 (incl GST) | OOS | 4006, 320 KV (title) | https://robu.in/product/martin-tl2954-6s-4006-320kv-brushless-motor/ | 2026-09-24 | VERIFIED-SR |
| Eaglepower LA 8308 KV90 motor | Eaglepower LA8308 KV90 | 1504803 | Robu | 11,579 (incl GST) | IN | 90 KV; 6–12S; 92 × 28.5 mm; 336 g; 22 A continuous; 900 W max; 0.186 Ω; idle 0.6 A @24 V | https://robu.in/product/eaglepower-la-8308-kv90-motor/ | 2026-09-24 | VERIFIED-PP |
| MAD CO 6215 IPE Agriculture Brushless motor 170 KV | MAD 6215 IPE 170KV | R112493 | Robu | 11,239 (incl GST) | IN | 170 KV; max 59.7 A; max 2808 W; 43 mΩ; IP35; hollow shaft; oversized bearings | https://robu.in/product/mad-co-6215-ipe-agriculture-brushless-motor-170-kv/ | 2026-09-24 | VERIFIED-PP |
| MAD CO 6215 IPE Agriculture Brushless motor 320 KV | MAD 6215 IPE 320KV | R112494 | Robu | 8,789 (incl GST) | IN | 6215, 320 KV (title) | https://robu.in/product/mad-co-6215-ipe-agriculture-brushless-motor-320-kv/ | 2026-09-24 | VERIFIED-SR |
| MAD CO 8318 IPE Agriculture Drone motor (Silver) 100 KV | MAD 8318 IPE 100KV | R112495 | Robu | 14,479 (incl GST) | IN | 100 KV; max 68 A; max 3224 W; 36 mΩ; up to 17.5 kg thrust on 28–32" prop | https://robu.in/product/mad-co-8318-ipe-agriculture-drone-motor-silver-100-kv/ | 2026-09-24 | VERIFIED-PP |
| MAD CO 8318 IPE Agriculture Drone Motor (Black) 120 KV | MAD 8318 IPE 120KV | R112498 | Robu | 19,129 (incl GST) | IN | 8318, 120 KV (title); Silver 120 KV version SKU R112496 is also ₹19,129 and IN | https://robu.in/product/mad-co-8318-ipe-agriculture-drone-motor-black-120-kv/ | 2026-09-24 | VERIFIED-SR |
| MAD CO 8318 IPE Agriculture Drone motor (Black) 100 KV | MAD 8318 IPE 100KV black | R112497 | Robu | 13,859 (incl GST) | OOS | 8318, 100 KV (title) | https://robu.in/product/mad-co-8318-ipe-agriculture-drone-motor-black-100-kv/ | 2026-09-24 | VERIFIED-SR |
| Reflex Drive RD MI X6 6215 180KV Motor 12S | Reflex Drive RD MI X6 6215 | R149363 | Robu | 8,869 (incl GST) | IN | Spec table shows KV 175 (title says 180 KV); 6S–12S; peak 54 A; 24N28P; Φ70 mm (from description). A CCW version (SKU R150191) is ₹10,200 and OOS. | https://robu.in/product/reflex-drive-rd-mi-x6-6215-180kv-motor-12s/ | 2026-09-24 | VERIFIED-PP |
| MAD CO 4014 EEE Brushless Motor 370KV (Pack Of 2) | MAD 4014 EEE 370KV ×2 | R248902 | Robu | 15,559 per pack of 2 (incl GST) | IN | 4014, 370 KV (title) | https://robu.in/product/mad-co-4014-eee-370kv-brushless-motor-pack-of-2-2/ | 2026-09-24 | VERIFIED-SR |
| MAD CO 4014 IPE Brushless Motor 450KV (Pack Of 2) | MAD 4014 IPE 450KV ×2 | R248893 | Robu | 15,559 per pack of 2 (incl GST) | IN | 4014, 450 KV (title) | https://robu.in/product/mad-co-4014-ipe-450kv-brushless-drone-motor/ | 2026-09-24 | VERIFIED-SR |
| MAD CO 3508 IPE Brushless Drone Motor 360KV (Pack Of 2) | MAD 3508 IPE 360KV ×2 | R248905 | Robu | 10,839 per pack of 2 (incl GST) | IN | 3508, 360 KV (title) | https://robu.in/product/mad-co-3508-ipe-brushless-drone-motor-360kv/ | 2026-09-24 | VERIFIED-SR |
| MAD CO 3506 EEE brushless drone motor 400KV (Pack Of 2) | MAD 3506 EEE 400KV ×2 | R248909 | Robu | 11,899 per pack of 2 (incl GST) | IN | 3506, 400 KV (title) | https://robu.in/product/mad-co-3506-eee-400kv-brushless-motor/ | 2026-09-24 | VERIFIED-SR |
| MAD 4112 450 KV PRO IPE Feathering Propeller Drone Motor (Pack of 2) | MAD 4112 PRO IPE ×2 | R248897 | Robu | 17,329 per pack of 2 (incl GST) | IN | 4112, 450 KV (title) | https://robu.in/product/mad-4112-pro-ipe-feathering-propeller-drone-motor-450kv/ | 2026-09-24 | VERIFIED-SR |
| Sunny Sky V4004 KV300 Brushless Motors | SunnySky V4004 KV300 | 1569811 | Robu | 6,339 (incl GST) | IN | 300 KV; 51 g; OD 43.6 mm × 16 mm; stator 40 × 4 mm; 18 arms / 24 poles; 448 mΩ; 10 A for 60 s; 250 W; no-load 0.2 A @10 V | https://robu.in/product/sunny-sky-v4004-kv300-brushless-motors/ | 2026-09-24 | VERIFIED-PP |
| Sunny Sky V4008 KV380 Brushless Motors | SunnySky V4008 | 1569813 | Robu | 7,879 (incl GST) | IN | 4008, 380 KV (title) | https://robu.in/product/sunny-sky-v4008-kv380-brushless-motors/ | 2026-09-24 | VERIFIED-SR |
| Sunny Sky V4006 KV320 Brushless Motors | SunnySky V4006 | 1569812 | Robu | 7,339 (incl GST) | OOS | 4006, 320 KV (title) | https://robu.in/product/sunny-sky-v4006-kv-320-brushless-motor/ | 2026-09-24 | VERIFIED-SR |
| Sunny Sky M industry drone series Motor M8 V2/KV115 | SunnySky M8 V2 KV115 | R153579 | Robu | 23,159 (incl GST) | IN | M8 V2, 115 KV (title). KV150 (R153580), KV170 (R153581) and KV190 (R153582) are ₹19,729 each, all IN. | https://robu.in/product/sunny-sky-m-industry-drone-series-motor-m8-v2-kv115/ | 2026-09-24 | VERIFIED-SR |
| T Motor Antigravity MN7005 KV115 | T-Motor MN7005 KV115 | 1402971 | Robu | 22,549 (incl GST) | IN | 7005, 115 KV (title) | https://robu.in/product/t-motor-antigravity-mn7005-kv115/ | 2026-09-24 | VERIFIED-SR |
| T Motor MN4112 KV420 | T-Motor MN4112 | 1272313 | Robu | 11,329 (incl GST) | IN | 4112, 420 KV (title) | https://robu.in/product/t-motor-mn4112-kv420/ | 2026-09-24 | VERIFIED-SR |
| T Motor Navigator Waterproof Mn501-S 300KV | T-Motor MN501-S 300KV | 1092916 | Robu | 10,489 (incl GST) | IN | 300 KV, waterproof (title) | https://robu.in/product/t-motor-navigator-waterproof-mn501-s-300kv/ | 2026-09-24 | VERIFIED-SR |
| T MOTOR ANTIGRAVITY 4004 300KV 2pcs/set | T-Motor Antigravity 4004 ×2 | 1092911 | Robu | 14,249 per set of 2 (incl GST) | IN | 4004, 300 KV (title) | https://robu.in/product/t-motor-antigravity-4004kv-300-2pcs-set-antigarvity/ | 2026-09-24 | VERIFIED-SR |
| T MOTOR ANTIGRAVITY 4006 380KV 2pcs/set | T-Motor Antigravity 4006 ×2 | 1092912 | Robu | 15,369 per set of 2 (incl GST) | IN | 4006, 380 KV (title) | https://robu.in/product/t-motor-antigravity-4006kv-380-2pcs-set-antigarvity/ | 2026-09-24 | VERIFIED-SR |
| T Motor Antigravity MN5008 KV170 | T-Motor MN5008 KV170 | 1402970 | Robu | 10,649 (incl GST) | OOS | 5008, 170 KV (title). Other T-Motor low-KV motors also OOS: MN6007II 160 KV (1814077, ₹15,179), MN801-S KV120 (1438354, ₹26,979), MN8012 KV100 (1402972, ₹37,409), MN5006 300 KV (R247108, ₹8,999), MN1005 V2.0 90 KV (1746036, ₹31,683), U12 II KV60 (1695819, ₹36,249). | https://robu.in/product/t-motor-antigravity-mn5008-kv170/ | 2026-09-24 | VERIFIED-SR |
| Axisflying 4214 Brushless Motors … 380 KV | Axisflying 4214 380KV | R160132 | Robu | 6,449 (incl GST) | IN | 4214, 380 KV (title) | https://robu.in/product/axisflying-4214-brushless-motors-for-13-inch-fpv-drone-cinematic-long-range-loading-380-kv/ | 2026-09-24 | VERIFIED-SR |
| 2204 260KV Brushless Gimbal Motor | Generic 2204 gimbal | 57801 | Robu | 979 (incl GST) | IN | 260 KV; 12–24 V; "Max operating current 600" (no unit on page; probably mA); 26 g; 28 × 28 mm; 100–200 g load; servo connector | https://robu.in/product/2204-260kv-brushless-gimbal-motor/ | 2026-09-24 | VERIFIED-PP |
| 2805 140KV Gimbal Brushless Motor | FlyCat 2805 gimbal | 57750 | Robu | 1,239 (incl GST) | IN | 140 KV; no spec table (shipping weight 0.043 kg) | https://robu.in/product/2805-140kv-gimbal-brushless-motor/ | 2026-09-24 | VERIFIED-PP (no specs) |
| 2804 140KV Brushless Motor for 2-Axis Camera Gimbal | Generic 2804 gimbal | R262067 | Robu | 1,269 (incl GST) | IN | 140 KV (title) | https://robu.in/product/2804-140kv-gimbal-brushless-motor-2-axis-camera/ | 2026-09-24 | VERIFIED-SR |
| FLYCCI Brushless Motors BGM2606-90 90KV | FLYCCI BGM2606-90 | R175978 | Robu | 3,029 (incl GST) | IN | 90 KV gimbal; 8.5 Ω; 32 × 17.5 mm; 4 mm shaft; 0–80 °C | https://robu.in/product/flycci-brushless-motors-bgm2606-90-90kv/ | 2026-09-24 | VERIFIED-PP |
| T Motor GB4106 Precision Gimbal Motor | T-Motor GB4106 | 1374860 | Robu | 5,059 (incl GST) | OOS | 4106 gimbal (title) | https://robu.in/product/t-motor-gb4106-precision-gimbal-motor/ | 2026-09-24 | VERIFIED-SR |
| T Motor GB2208 KV128 Gimbal Motor | T-Motor GB2208 | 1272310 | Robu | 2,829 (incl GST) | OOS | 128 KV (title). The similar generic 2208 80KV (57831, ₹1,189) is also OOS. | https://robu.in/product/t-motor-gb2208-kv128-gimbal-motor/ | 2026-09-24 | VERIFIED-SR |
| T Motor U15Ⅱ KV100 BLDC drone motor | T-Motor U15 II | 1330781 | Robu | 79,799 (incl GST) | IN | 100 KV (title); large and costly, listed for reference | https://robu.in/product/t-motor-u15%e2%85%b1-kv100-bldc-drone-motor/ | 2026-09-24 | VERIFIED-SR |

**Searches in category 2 with no relevant Robu result:**
- Only cooling fans or non-motor items: "5015 motor", "6010 motor", "5208", "4108".
- Nothing relevant: "6374 motor", "6374 brushless" (returned one NEMA17 stepper), "6384" (no products found), "8108" (limit switches only).
- "iFlight motor": only high-KV (≥800 KV) XING FPV motors.
- "Readytosky": no low-KV motors.
- "Eaglepower": only the LA8308.
- No 4108/5208/6374/8108 gimbal or skate motors are listed on Robu.

---

## 3. Motor drivers / FOC controllers

| Item | Brand/Model | SKU | Supplier | Price ₹ (incl GST?) | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| SimpleFOCmini Brushless DC Motor Driver Board | SimpleFOCmini | R261566 | Robu | 729 (incl GST) | IN | FOC; 8–30 V DC input; 2.5 A per phase max; 3.3/5 V logic; 26 × 21.5 mm; SimpleFOC library (Arduino/ESP32/RPi). For gimbal-class motors only. | https://robu.in/product/simplefocmini-brushless-dc-motor-driver-board/ | 2026-09-24 | VERIFIED-PP |
| NDrive Z1 Single Channel Versatile BLDC Motor Controllers | NMotion NDrive Z1 | R213120 | Robu | 13,999 (incl GST) | IN | FOC; 12–48 V (peak 56 V); 20 A continuous / 55 A peak for 2 s; onboard 14-bit MA732 absolute encoder; external ABZ + SPI absolute encoder inputs; CAN 2.0B at 500 kbps (page says 1 Mbps "coming soon"); DIP-switch termination, daisy-chain; brake resistor and thermistor I/O; 52 × 52 mm; Python/C++ SDK (docs.nmotion.in); PC link needs the NLink USB-CAN adapter | https://robu.in/product/ndrive-z1-single-channel-versatile-bldc-motor-controllers/ | 2026-09-24 | VERIFIED-PP |
| Nlink USB-CAN Converter | NMotion NLink | R213121 | Robu | 2,999 (incl GST) | IN | USB–CAN adapter needed for the NDrive Z1 (per Z1 page) | https://robu.in/product/nlink-usb-can-converter/ | 2026-09-24 | VERIFIED-SR |
| Makerbase XDrive MINI High-Precision Brushless Servo Motor Controller, Based On ODrive3.6 with AS5047P on board | Makerbase MKS ODrive MINI V1.0 | R263153 | Robu | 4,999 (incl GST) | OOS | ODrive v3.6 architecture; STM32F405RGT6; firmware 0.5.1; 8–56 V; 60 A continuous / 120 A peak; onboard AS5047P; USB / CAN / UART / PWM / STEP-DIR; position/speed/torque modes | https://robu.in/product/makerbase-xdrive-mini-high-precision-brushless-servo-motor-controller-based-on-odrive36-with-as5047p-on-board/ | 2026-09-24 | VERIFIED-PP |
| STMICROELECTRONICS NUCLEO-G431KB Development Board | ST NUCLEO-G431KB | R165694 | Robu | 3,039 (incl GST) | IN | STM32G431KBT6U (title). Could be the MCU for a custom FOC board. | https://robu.in/product/nucleo-g431kb/ | 2026-09-24 | VERIFIED-SR |
| M5Stack BLDC Motor Driver Unit (STM32) | M5Stack Unit-BLDC | R135359 | Robu | 829 (incl GST) | IN | DRV11873 **sensorless** driver; I2C (0x65); PWM speed control only; 32 × 24 mm. **Not suitable for joint position/torque control.** | https://robu.in/product/m5stack-bldc-motor-driver-unit-stm32/ | 2026-09-24 | VERIFIED-PP |
| DRV8313PWPR-Texas Instruments-HTSSOP-28 BLDC Motor Driver | TI DRV8313PWPR (IC) | R239650 | Robu | 352 (incl GST) | IN | 3-phase driver IC. Per the title of sibling SKU R201998 (DRV8313PWP, ₹529, IN): 8–60 V, 2.5 A. The VQFN-36 DRV8313RHHR (R239715) is ₹101, IN. | https://robu.in/product/drv8313pwpr-texas-instruments-htssop-28-ep-4-5mm-brushless-dc-bldc-motor-driver-rohs/ | 2026-09-24 | VERIFIED-SR |
| DRV8323RSRGZT MOSFET Driver 4–60 V | TI DRV8323RS (IC) | R201990 | Robu | 380 (incl GST) | OOS | Gate driver, 4–60 V (title). Also OOS: DRV8353RHRGZT (1363824, ₹629), DRV8305NQPHPRQ1 (R239604, ₹328). In stock: DRV8304SRHAR gate driver, 6–38 V (R239594, ₹180). | https://robu.in/product/drv8323rsrgzt-texas-instruments-mosfet-driver-half-bridge-4-v-to-60-v-supply-2-a-out-150-ns-propagation-delay-vqfn-48/ | 2026-09-24 | VERIFIED-SR |
| STMICROELECTRONICS Expansion Board, STSPIN230 Low Voltage 3-Phase BLDC Driver | ST X-NUCLEO (STSPIN230) | 1470080 | Robu | 1,329 (incl GST) | IN | Low-voltage 3-phase driver board (title). The STSPIN830 board (1470060, ₹2,089) is OOS. | https://robu.in/product/stmicroelectronics-expansion-board-stspin230-low-voltage-3-phase-brushless-dc-motor-driver/ | 2026-09-24 | VERIFIED-SR |
| LILYGO T-Knob ESP32-C6 + BLDC Gimbal Motor + MT6701 | LILYGO T-Knob | R160898 | Robu | 6,089 (incl GST) | OOS | ESP32-C6 + gimbal motor + MT6701 encoder (title); a haptic-knob dev kit | https://robu.in/product/lilygo-t-knob-esp32-c6bldc-gimbal/ | 2026-09-24 | VERIFIED-SR |
| Yalu Brushless Controller for 1000W 48V BLDC Motor | Yalu 48 V 1000 W | 971969 | Robu | 4,199 (incl GST) | IN | E-bike style speed controller (title). Not a servo/FOC joint driver. | https://robu.in/product/brushless-controller-for-1000w48v-bldc-motor/ | 2026-09-24 | VERIFIED-SR |

**Searches in category 3 with no relevant Robu result:**
- "B-G431B-ESC1": the search tokenised into unrelated results. "G431" found only Nucleo boards. ST's B-G431B-ESC1 is **not listed**.
- "ODrive" / "Makerbase": only the XDrive MINI (OOS). No genuine ODrive S1/Pro.
- No products found: "VESC", "moteus".
- "Flipsky": only FlySky RC radios.
- "FOC driver" / "BLDC driver CAN": only the rows above plus bare TI driver ICs.

---

## 4. Encoders & magnets

| Item | Brand/Model | SKU | Supplier | Price ₹ (incl GST?) | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| MT6835 magnetic encoder module PWM/SPI brushless motor 21BIT encoder with magnet to replace AS5048 - AB 8192 | MagnTek MT6835 module | R224599 | Robu | 619 (incl GST) | IN | 21-bit absolute via SPI (18-bit core), 12-bit PWM; ABZ/UVW programmable; 3.3–5 V; −40 to 125 °C; up to 120k rpm; 27 × 27 mm; 3.2 g; magnet included | https://robu.in/product/mt6835-magnetic-encoder-module-pwm-spi/ | 2026-09-24 | VERIFIED-PP |
| MT6835 … - AB 10000 | MT6835 module (ABZ 10000) | R224598 | Robu | 679 (incl GST) | IN | Same family, ABZ 10000 variant (title) | https://robu.in/product/mt6835-magnetic-encoder-module-pwm-spi-brushless-motor-21bit-encoder-with-magnet-to-replace-as5048-ab-10000/ | 2026-09-24 | VERIFIED-SR |
| MT6835 … - AB 16384 | MT6835 module (ABZ 16384) | R224597 | Robu | 729 (incl GST) | OOS | The 4 × 2 mm-magnet version (R265582, ₹729) is also OOS | https://robu.in/product/mt6835-magnetic-encoder-module-pwm-spi-brushless-motor-21bit-encoder-with-magnet-to-replace-as5048-ab-16384/ | 2026-09-24 | VERIFIED-SR |
| Magnetic encoder sensor module AS5600 | AS5600 module (generic) | R175153 | Robu | 144 (incl GST) | IN | 12-bit (4096 positions); I2C / PWM / analog; 3.3 V; −40 to 125 °C | https://robu.in/product/magnetic-encoder-sensor-module-as5600/ | 2026-09-24 | VERIFIED-PP |
| AS5600-ASOM AMS 0°~360° SOIC-8 Position Sensors | ams AS5600-ASOM (IC) | R182262 | Robu | 169 (incl GST) | IN | Bare IC (title) | https://robu.in/product/as5600-asom-ams-0360-soic-8-position-sensors-rohs/ | 2026-09-24 | VERIFIED-SR |
| SeeedStudio Grove 12bit Magnetic Rotary Position Sensor (AS5600) | Seeed Grove AS5600 | 1147638 | Robu | 749 (incl GST) | IN | 12-bit AS5600, Grove connector (title) | https://robu.in/product/seeedstudio-grove-12bit-magnetic-rotary-position-sensor-as5600/ | 2026-09-24 | VERIFIED-SR |
| AS5045B-ASST AMS SSOP-16 Position Sensors | ams AS5045B (IC) | R182277 | Robu | 419 (incl GST) | IN | Bare IC (title) | https://robu.in/product/as5045b-asst-ams-ssop-16-208mil-position-sensors-rohs/ | 2026-09-24 | VERIFIED-SR |
| XJX-134 MT6701 Module | MT6701 module | R254845 | Robu | 249 (incl GST) | OOS | MT6701 module (title) | https://robu.in/product/xjx-134-mt6701-module/ | 2026-09-24 | VERIFIED-SR |
| Orange 600 PPR ABZ 3-Phase Incremental Magnetic Rotary Encoder | Orange (Robu) 600 PPR | 232566 | Robu | 3,379 (incl GST) | IN | Shaft-type incremental encoder, 600 PPR ABZ (title) | https://robu.in/product/orange-600-ppr-abz-3-phase-incremental-magnetic-rotary-encoder/ | 2026-09-24 | VERIFIED-SR |

**Searches in category 4 with no relevant Robu result:**
- "AS5047": no AS5047P module; it appears only on the XDrive MINI board.
- "AS5048": no AS5048A/B module; only MT6835 "to replace AS5048".
- No products found: "diametric magnet", "diametrically magnetized".

---

## 5. Bus servos (upper body) and related

| Item | Brand/Model | SKU | Supplier | Price ₹ (incl GST?) | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| Waveshare ST3215 Serial Bus Servo, 360° Encoder, 19.5kg.cm @ 7.4V | Waveshare ST3215 (Feetech STS3215-class) | R258500 | Robu | 2,159 (incl GST) | IN | 12-bit 360° magnetic encoder (0–4095); metal gears; 0.192 s/60° (52 rpm) @7.4 V; IDs 0–253; 38.4 kbps–1 Mbps (1 Mbps default); no-load 150 mA; 45.22 × 37.25 mm; dual shaft; includes cable, 2 aluminium horns, screws. Title says 19.5 kg·cm @7.4 V; description also mentions "30 kg.cm (12V)". | https://robu.in/product/waveshare-st3215-serial-bus-servo/ | 2026-09-24 | VERIFIED-PP |
| Waveshare 30KG Serial Bus Servo | Waveshare 30 kg (ST3215 12 V class) | 1331215 | Robu | 2,599 (incl GST) | IN | 30 kg·cm @12 V; 6–12.6 V; 0.222 s/60° (45 rpm) @12 V; 360° magnetic encoder, 4096 steps; no mechanical limit; metal gears; stall 2.7 A; no-load 180 mA; torque constant 11 kg·cm/A; feedback position/load/speed/voltage; 1 Mbps | https://robu.in/product/waveshare-30kg-serial-bus-servo/ | 2026-09-24 | VERIFIED-PP |
| Waveshare 20kg.cm Bus Servo Motor, 106RPM High Speed … 360° Magnetic Encoder | Waveshare 20 kg high-speed | 1738071 | Robu | 2,529 (incl GST) | IN | 20 kg·cm @12 V; 106 rpm (title); 6–12.6 V; 4096 steps; metal gears; stall 2.4 A; no-load 240 mA | https://robu.in/product/waveshare-20kg-cm-bus-servo-motor-106prm-high-speed-large-torque-with-360-degrees-high-precision-magnetic-encoder/ | 2026-09-24 | VERIFIED-PP |
| Waveshare 25kg.cm Wide Range Voltage Serial Bus Servo … 360° Magnetic Encoder | Waveshare 25 kg wide-voltage | 1738072 | Robu | 2,618 (incl GST) | IN | 25 kg·cm; 6–14 V (typ. 12 V); 12-bit encoder (0.088°); no-load 200 mA @12 V; metal gears | https://robu.in/product/waveshare-25kg-cm-wide-range-voltage-serial-bus-servo-high-precision-and-large-torque-with-programmable-360-degrees-magnetic-encoder/ | 2026-09-24 | VERIFIED-PP |
| Waveshare 30kg.cm ST3235 Serial Bus Servo, Aluminum Alloy Case | Waveshare ST3235 | R136626 | Robu | 5,689 (incl GST) | IN | 30 kg·cm, aluminium case, 360° encoder (title) | https://robu.in/product/waveshare-30kg-cm-st3235-serial-bus-servo-high-precision-and-large-torque-aluminum-alloy-case-with-programmable-360-degrees-magnetic-encoder/ | 2026-09-24 | VERIFIED-SR |
| Waveshare SC15 17kg Large Torque Programmable Serial Bus Servo | Waveshare SC15 | 1219081 | Robu | 2,069 (incl GST) | IN | 17 kg (title) | https://robu.in/product/waveshare-sc15-17kg-large-torque-programmable-serial-bus-servo/ | 2026-09-24 | VERIFIED-SR |
| Waveshare 45kg.cm RSBL45-24 Servo Motor | Waveshare RSBL45-24 | R140321 | Robu | 13,999 (incl GST) | IN | 45 kg·cm, aluminium case, 360° encoder (title) | https://robu.in/product/waveshare-45kg-cm-rsbl45-24-servo-motor-high-precision-and-large-torque-aluminum-alloy-case-with-programmable-360-magnetic-encoder/ | 2026-09-24 | VERIFIED-SR |
| Waveshare 40kg.cm Metal Serial Bus Servo … and brushless motor | Waveshare 40 kg brushless | 1738073 | Robu | 9,259 (incl GST) | OOS | 40 kg·cm (title). Also OOS: Waveshare 35 kg RS485 (R179658, ₹12,809) and CF35-12 (R212478, ₹7,419). | https://robu.in/product/waveshare-40kg-cm-metal-serial-bus-servo-high-precision-and-large-torque-with-programmable-360-degrees-magnetic-encoder-and-brushless-motor/ | 2026-09-24 | VERIFIED-SR |
| Hiwonder LX224 HV servo motor | Hiwonder LX-224HV | R140355 | Robu | 2,089 (incl GST) | IN | 20 kg·cm @11.1 V; 9–12.6 V; UART serial command; 0–240° (motor mode 360°); 0.18 s/60° @11.1 V; 0.24° accuracy; no-load 100 mA; potentiometer feedback (the description text is copied from the LX-15D) | https://robu.in/product/hiwonder-lx224-hv-servo-motor/ | 2026-09-24 | VERIFIED-PP |
| Hiwonder HTS-30HS Servo Motor 30KG | Hiwonder HTS-30HS | R154797 | Robu | 6,869 (incl GST) | IN | 30 kg (title); bus type not checked | https://robu.in/product/hiwonder-hts-30hs-servo-motor-30kg/ | 2026-09-24 | VERIFIED-SR |
| Hiwonder HTS-35H High Voltage Bus Servo 35KG | Hiwonder HTS-35H | R154801 | Robu | 4,039 (incl GST) | OOS | Also OOS: HX-35H (R134528, ₹5,189), HTS-20L (R154800, ₹3,069), LX-15D (R134529, ₹2,809), HX-12H (R134527, ₹3,759) | https://robu.in/product/hiwonder-hts-35h-high-voltage-bus-servo-35kg/ | 2026-09-24 | VERIFIED-SR |
| Pro-Range OT6560 7.4V 60kg.cm 120° Metal Gear Serial Control BUS Servo Motor | Pro-Range (Robu) OT6560 | 867251 | Robu | 4,149 (incl GST) | IN | 4–8.4 V; stall 48–62 kg·cm; 0.13 s/60° @7.4 V; steel gears; 190 g; 66 × 30 mm; 7.5 mm 15T shaft; JR 3-wire plug. **Title says "BUS servo", but the description says it works "with any servo code" and the spec says "Rotation 180". The protocol is unclear; check before buying.** | https://robu.in/product/orange-ot6560-7-4v-60kg-cm-120-metal-gear-serial-control-bus-servo/ | 2026-09-24 | VERIFIED-PP |
| SmartElex Serial Bus Servo Driver Board | SmartElex | R255565 | Robu | 509 (incl GST) | IN | Bus-servo driver board: servo power + control circuit (title) | https://robu.in/product/smartelex-serial-bus-servo-driver-board/ | 2026-09-24 | VERIFIED-SR |
| Waveshare Serial Bus Servo DC Buck Adapter, 7.2V | Waveshare | R136622 | Robu | 479 (incl GST) | IN | 7.2 V buck for bus servos (title). OOS: Waveshare Bus Servo Driver Board (1782919, ₹481) and ESP32 Driver HAT (R136625, ₹2,099). | https://robu.in/product/waveshare-serial-bus-servo-dc-buck-adapter-mini-module-design-for-serial-bus-servos-easy-to-use-7-2v-buck-regulator/ | 2026-09-24 | VERIFIED-SR |
| Seeed Studio SO-ARM101 Pro Servo Motor Kit (Without 3D Printed Parts) | Seeed SO-ARM101 Pro | R268622 | Robu | 34,440 (incl GST) | BO | Bus-servo arm servo kit (reference) | https://robu.in/product/Seeed%20Studio%20SO-ARM101%20Pro%20Servo%20Motor%20Kit%20(Without%203D%20Printed%20Parts)/ (slug shown as-is on the page) | 2026-09-24 | VERIFIED-SR |
| Pro-Range DS5160 60kgcm Metal Gear Digital Servo Motor - 180 degree | Pro-Range DS5160 (PWM) | R251566 | Robu | 2,329 (incl GST) | IN | 60 kg·cm PWM servo (title); no bus or feedback | https://robu.in/product/pro-range-ds5160-60kgcm-digital-servo-motor/ | 2026-09-24 | VERIFIED-SR |
| Pro-Range Coreless DS3235 35kgcm Metal Gear Digital Servo Motor | Pro-Range DS3235 (PWM) | R251569 | Robu | 2,269 (incl GST) | IN | 35 kg·cm coreless PWM (title). DS3245 45 kg·cm (R251571) is ₹2,489, IN. | https://robu.in/product/pro-range-coreless-ds3235-35kgcm-digital-servo/ | 2026-09-24 | VERIFIED-SR |
| Pro-Range Brushless BLS3245 45kgcm Metal Gear Digital Servo Motor | Pro-Range BLS3245 (PWM) | R251574 | Robu | 2,939 (incl GST) | IN | 45 kg·cm brushless PWM (title). Other Pro-Range brushless PWM servos, all IN: BLS3225 (R251572, ₹2,939), BLS3235 (R251573, ₹2,859), BL51180-24V 180 kg·cm (R251585, ₹7,329), BLS51180-12V (R251584, ₹7,159). | https://robu.in/product/pro-range-bls3245-45kgcm-brushless-digital-servo/ | 2026-09-24 | VERIFIED-SR |
| Waveshare WP5335 35kg.cm Large Torque 180° Digital Servo | Waveshare WP5335 (PWM) | R249001 | Robu | 1,639 (incl GST) | IN | 35 kg·cm PWM (title) | https://robu.in/product/waveshare-35kg-cm-large-torque-180-digital-servo/ | 2026-09-24 | VERIFIED-SR |
| DYS GOTeck GB3506MG Metal Geared 180° HV Brushless Servo 35kg/0.06sec/75g | DYS GB3506MG (PWM) | R189096 | Robu | 5,519 (incl GST) | IN | 35 kg, 0.06 s, 75 g, HV, brushless (title) | https://robu.in/product/dys-goteck-gb3506mg-metal-geared-180-high-torque-hv-digital-brushless-servo-35kg-0-06sec-75g/ | 2026-09-24 | VERIFIED-SR |

**Searches in category 5 with no relevant Robu result:**
- "STS3215": only Waveshare ST3215 rebrands; no Feetech-branded STS3215.
- "STS3250": no match.
- "Feetech": only Feetech PWM servos (FS/FT series); no STS/SCS bus servos.
- "Dynamixel": no Dynamixel servos; only a DFRobot shield for Dynamixel AX (R254411, ₹2,629, IN).
- "XL430": no match.
