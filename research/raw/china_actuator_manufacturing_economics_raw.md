# China QDD / humanoid joint-actuator manufacturing economics — raw research notes

Compiled 2026-10-06 for the JX1 technical paper section comparing
(a) small-volume in-house actuator building in India with (b) how Chinese makers (RobStride/灵足时代, Damiao/达妙,
Unitree/宇树, Encos/因克斯, Zhaowei/兆威 and others) build them at scale.

## Conventions

- **Labels:** **VERIFIED** = primary or official source read in this session (company filing, prospectus table reproduced
  in a broker report, government notice, company announcement on an exchange). **ESTIMATED** = my arithmetic, method
  shown. **UNVERIFIED** = secondary or media source, forum, reseller, search snippet, or an analyst's own guess. Broker
  teardown cost tables are labelled **ANALYST-EST** (a broker's estimate, not company data).
- **Currency:** same factors as `bom/build_bom.py`: USD/INR 95.96, CNY/USD 7.10, so **₹13.52 per ¥** (ESTIMATED,
  inherited from the repo).
- "Joint", "joint module" (关节模组) and "actuator" mean an integrated motor + reducer + encoder(s) + driver unit unless
  stated otherwise.
- Broker PDFs read in full this session (text extracted with `pdftotext`):
  - **Guosen Securities (国信证券)**, *人形机器人本体系列之宇树科技招股书梳理*, 2026-08-21/22. Its tables reproduce
    Unitree's prospectus (招股书). https://pdf.dfcfw.com/pdf/H3_AP202608231828340886_1.pdf
  - **China Post Securities (中邮证券)**, *宇树G1人形机器人拆解报告* (G1 teardown), 2026-03-30.
    https://pdf.dfcfw.com/pdf/H3_AP202603311820899944_1.pdf
  - **CMB International (招银国际)**, *以智能车为鉴，挖掘人形机器人投资机会*, 2026-08-14.
    https://pdf.dfcfw.com/pdf/H3_AP202608141827986577_1.pdf
  - **Huayuan Securities (华源证券)**, *人形机器人产业2025年报及2026一季报综述*, 2026-05-12.
    https://www.jtcopper.com/wp-content/uploads/2026/05/人形机器人产业2025年报及2026一季报综述：零部件兑现收入，主机厂放量加快.pdf
  - **BofA Institute**, *Physical AI, part 2: Humanoid robots*, 2026-03-12.
    https://institute.bankofamerica.com/content/dam/transformation/physical-ai-part-2.pdf
  - **Techadyant Labs**, *India's Drone Propulsion Opportunity* (free edition), 2026.
    https://lkqojucjkpxhcngtstfy.supabase.co/storage/v1/object/public/reports-free/Indias-Drone-Propulsion-Opportunity-Free-Edition.pdf
- **Not obtained:**
  - Morgan Stanley "Humanoid 100", Goldman Sachs and UBS reports in the original. Only press summaries were found, so
    their numbers are UNVERIFIED.
  - No UBS teardown of Optimus or Unitree was found.
  - GGII (高工机器人) paywalled data. Only figures quoted by the press were found.

---

## 1. Company facts

### 1.1 RobStride Dynamics / 北京灵足时代科技有限公司

| Fact | Value | Source (date) | Label |
|---|---|---|---|
| Founded | **November 2023** (36Kr 2025 and NCSTI 2025). A 2024 36Kr piece says "January 2024", which is probably the company's registration or operating start. | https://www.36kr.com/p/3459194287216261 (2025-09-10); https://www.36kr.com/p/2936510975925123 (2024-09-13) | UNVERIFIED (media; dates disagree) |
| Location | Beijing Economic-Technological Development Area (北京经开区, Yizhuang) | https://www.ncsti.gov.cn/kjdt/scyq/bjjjjskfq/jkdt/202507/t20250701_209102.html (2025-07-01, gov't S&T news site) | VERIFIED (gov't news site) |
| Factory / production line location | **Not disclosed** in any source found. Pre-A money was earmarked "for production line construction and capacity expansion". | 36Kr 2025-09-10 | not found |
| Founders | CEO **Wang Bo (王勃)**: HIT automation graduate; "former head of Xiaomi's robot joint team, Xiaomi robot joint chief architect"; described as chief designer of CyberGear. COO **Shao Yuanxin (邵元欣)**: King's College London; ran the CyberDog / CyberGear projects at Xiaomi. | 36Kr 2025-09-10; KrASIA https://kr-asia.com/robstride-builds-the-joints-that-keep-chinas-robots-moving-and-a-thriving-industry-around-them (2025-09-17) | UNVERIFIED (media; consistent across sources) |
| Funding | **Angel/seed**, Sep 2024: "tens of millions of RMB" (数千万元) from Innoangel (英诺), Y&R / 雅瑞 Scientist Fund, Yiwei (一维) Capital. **Pre-A** (2025): led by **HongShan (红杉) Seed**, with 弘晖 (Highlight) and 兴牛 (Xinniu). **Pre-A+** (2025): 弘晖 alone. Pre-A + Pre-A+ together: "数千万元". FA: 凌霄资本. | 36Kr 2024-09-13; 36Kr 2025-09-10 | UNVERIFIED (media) |
| Units shipped | **>25,000** units by 2025-07-01 (>20 countries). **>50,000** units to 26 countries by 2025-09-10. "5,000 units shipped within one week" for a single order. | NCSTI 2025-07-01; 36Kr 2025-09-10 | UNVERIFIED (company claims via media) |
| Orders / revenue | 2025 orders expected to pass **¥100 M** ("订单额年底达过亿元"); "2025年公司订单已达亿元级别". **2026 guidance: 300,000 units, revenue > ¥300 M.** | 36Kr 2025-09-10; CLS https://www.cls.cn/detail/2417216 (2026-07-05) | UNVERIFIED |
| Capacity | **≈100,000 units/yr now; 200,000 planned** | China Baogao (观研) https://www.chinabaogao.com/tuozi/202606/803020.html (2026-06-27) | UNVERIFIED (industry-report site) |
| Customers | "Nearly half" of China's embodied-AI OEMs; ">48.6 % of complete-machine makers at WRC Aug 2025 are partners". Named customers (2026): **Galbot (银河通用), Unitree (宇树), AgiBot (智元), Galaxea (星海图)**. Embodied AI is only **30–40 % of revenue**; the rest is EVs, pool-cleaning robots and industrial automation. **~30 %** of revenue is retail developer sales. | 36Kr 2025-09-10; KrASIA 2025-09-17; CLS 2026-07-05 | UNVERIFIED |
| Materials / process | Flagship series: alloy-steel gears; "all housing and support parts are one-piece aluminium die castings" (铝压铸一体成型); gears made by "die-casting then post-processing" (压铸后处理; the original wording is odd, probably powder-metal or near-net-shape then machining). EduLite series: powder metallurgy, engineering plastics, some 3D printing; ~50 % cheaper. Philosophy: "costs are designed, not managed". Weekly firmware OTA; a new hardware model about every quarter (7 mass-production models in 18 months). | 36Kr 2025-09-10; KrASIA 2025-09-17 | UNVERIFIED |
| China list prices | RS01 **¥599**, RS03 **¥999**, RS04 **¥1,199** at launch (Sep 2024). The same CN prices are still listed in 2026: RS04 ¥1,199, RS03 ¥999, RS00 ¥598, EduLite05 ¥299 (`actuator_technology_raw.md`). **List prices have been flat 2024 → 2026.** | 36Kr 2024-09-13; robstride.com CN page (checked 2026-09-24 in repo) | VERIFIED (robstride.com) / UNVERIFIED (2024 media) |
| Price claim | "Weight is 1/4 and price 1/3 of traditional solutions" | 36Kr 2024-09-13 | UNVERIFIED |

**ESTIMATED — implied RobStride ASP.**
- 2026 guidance: ¥300 M ÷ 300,000 units ≈ **¥1,000 per unit** (≈ ₹13,500 ≈ $141). This sits between the RS00 (¥598)
  and RS04 (¥1,199) list prices, so volume buyers get little or no discount off the list price, or the mix is weighted
  to large joints.
- 2025 (cumulative): ~¥100 M of orders against >50k units shipped from launch to Sep 2025 gives roughly
  **¥1,000–2,000 per unit**. Order value and shipments are not the same measure, so treat this as a range only.

### 1.2 Damiao / 深圳市达妙科技有限公司

| Fact | Value | Source | Label |
|---|---|---|---|
| Founded / location | **2019, Shenzhen**, "by former DJI engineers"; joint motors since **2022**; >10 BLDC joint-motor models (DM-J4310-2EC etc.); also hub motors and drivers | EtherCAT Technology Group member listing https://www.ethercat.org/en/members/members_01EEF6C8FCC446F5BC8F074562EBECFF.htm ; search snippet from WRC exhibitor page | UNVERIFIED (self-description in a member directory) |
| Funding | **Not found** (no 36Kr / pedaily / 投中 record of a round in the searches) | — | not found |
| Volumes, capacity, factory | **Not found** | — | not found |
| Catalogue | 2025 selection handbook (WRC download). Product data are already in `actuator_technology_raw.md` §1A. | https://www.worldrobotconference.com/profile/robot/download/2025/06/30/达妙科技DAMIAO - 2025年产品选型手册_20250630192546A441.pdf | VERIFIED (product data) |
| Prices | DM-J4310-2EC V1.1 $125 (AIFITLAB); Switch Science ¥21,780 JPY. Taobao prices are in the repo's earlier file (DM-4340P ¥949, DM-10010L ¥1,989 via the Roboto Origin BOM). | aifitlab.com; switch-science.com | UNVERIFIED (resellers) |

### 1.3 Unitree / 宇树科技 (Hangzhou) — prospectus data

Source for all rows in this sub-section unless stated: Guosen Securities 2026-08-21, whose tables are marked
"资料来源：公司招股书". **Label: VERIFIED-via-broker** (prospectus figures reproduced by a licensed broker; I did not
read the prospectus itself). Unitree listed on the **Shanghai STAR Market on 2026-08-19** at an offer price of
**¥150.80**; it opened at ¥1,100 (IT之家 https://www.ithome.com/0/986/699.htm; UNVERIFIED media).

| Item | 2022 | 2023 | 2024 | 2025 | Note |
|---|---:|---:|---:|---:|---|
| Revenue (¥ M) | 120 | 159.1 | 392.8 | **1,699.3** | humanoid ¥867.8 M (51.1 %), quadruped ¥697.6 M (41.1 %), components ¥103.7 M (6.1 %) in 2025 |
| Gross margin | — | 44.75 % | 57.22 % | **60.44 %** | 2025: humanoid **63.2 %**, quadruped 56.7 %, robot components **59.4 %** |
| Humanoid production / sales (units) | — | 9 / 5 | 545 / 412 | **5,716 / 5,215** | ~18,000 humanoids built cumulatively by Jul 2026 |
| Quadruped production / sales | 2,520 / 2,403 | 3,149 / 3,121 | 7,240 / 7,136 | **26,032 / 23,037** | |
| Humanoid ASP (¥ k/unit) | — | 593.4 | 260.4 | **166.4** | −56 % then −36 % y/y |
| Quadruped ASP (¥ k/unit) | 38.6 | 38.3 | 32.3 | **30.3** | |
| Humanoid unit cost (¥ k) | — | 73.2 | 82.3 | **62.2 (9M 2025)** | −24.5 % in 9M 2025 |
| Quadruped unit cost (¥ k) | 22.3 | 21.5 | 15.7 | **12.1 (9M 2025)** | |
| COGS split, company (DM / DL / OH) | 74.0 / 10.3 / 15.7 % | 72.9 / 14.0 / 13.2 % | 72.9 / 12.4 / 14.6 % | **81.7 / 8.1 / 10.2 %** | DM = direct materials, DL = direct labour, OH = manufacturing overhead |
| Humanoid COGS split (DM / DL / OH) | — | 60.3 / 19.5 / 20.2 % | 75.4 / 11.5 / 13.1 % | **82.6 / 6.8 / 10.6 % (9M)** | G1 alone: 83.0 / 6.8 / 10.2 % |
| Quadruped COGS split | 76.4 / 8.9 / 14.7 % | 74.9 / 12.4 / 12.7 % | 70.1 / 13.7 / 16.2 % | **77.2 / 9.5 / 13.4 % (9M)** | |
| Raw-material purchases (¥ M) | 75.0 | 70.6 | 193.7 | **793.8** | 2025 split: **mechanical parts 50.7 %** (machined, die-cast, fasteners, plastics), electronic components 22.4 %, electrical materials 22.2 % (wire, LED, gimbal, batteries), basic materials (steel, aluminium, copper) **2.0 %**, packaging 1.9 %, consumables 0.8 % |
| Employees | — | — | — | **516 (184 R&D)** at end-2025 | |

How Unitree makes its joints (prospectus table via Guosen, VERIFIED-via-broker):

| Joint sub-part | Make/buy mode |
|---|---|
| Reducer | "自主设计研发，零部件定制采购，自主装配": designed in-house, **parts bought to Unitree's drawings**, assembled in-house |
| Motor | same: own design, **custom-purchased parts** (i.e. stators, magnets and housings are not necessarily made in-house), own assembly |
| Encoder | own design, components bought, **SMT outsourced (委外贴片)**, own firmware |
| Driver | own design, components bought, SMT outsourced, own firmware |

Other prospectus facts:
- Outsourced standard sub-assemblies (cells, compute, lidar, cameras, hands) are only **14–18 % of total cost**.
- Joint architecture is a "high-bandwidth force-controlled **quasi-direct-drive planetary** rotary joint" used on
  essentially all core joints.
- Current production is "**以人工装配为主**" (mainly manual assembly). The IPO-funded **智能机器人制造基地** (¥624 M)
  will build automated lines for **75,000 humanoids + 115,000 quadrupeds per year** (30 % ramp at T+3, 100 % at T+5).

Other Unitree facts:
- A new Hangzhou factory of more than 10,000 m² opened in 2025 (SCMP,
  https://scmp.com/tech/tech-trends/article/3307315/chinese-robotics-star-unitree-opens-hangzhou-factory-amid-humanoid-frenzy;
  UNVERIFIED).
- **G1 teardown (China Post, ANALYST-EST):**
  - Reducer gears come from **美湖股份 (Meihu)**; thin-section crossed-roller bearings from **洛阳佰纳 (Luoyang Baina)**.
  - Motors and drivers are in-house; chip markings are removed (anti-reverse-engineering).
  - The small ankle joint is ~Ø60 × 70 mm, 525 g, with an inner-rotor PMSM, a **two-stage planetary of ≈20.58:1**
    (18/14/60 and 16/20/60 teeth), dual encoders and hollow-shaft wiring.

**ESTIMATED — Unitree joint-motor volume in 2025** (not disclosed):
- Humanoids: 5,716 built × 23–35 joints ≈ 131k–200k joints.
- Quadrupeds: 26,032 built × 12 joints ≈ 312k joints.
- Total ≈ **0.45–0.51 M in-house joint motors in 2025**, before spares and component sales. Unitree is therefore
  probably China's largest single QDD maker by volume.

**ESTIMATED — labour per robot.**
- Humanoid: DL 6.8 % × ¥62.2k ≈ **¥4,200 per humanoid** (≈ ₹57k).
- Quadruped: 9.5 % × ¥12.1k ≈ **¥1,150 per quadruped**.
- Spread over 12–35 joints plus body assembly, joint-related direct labour is probably **< ¥100 per joint** at
  Unitree's volume. This is an inference, not disclosed.

### 1.4 Encos / 南京因克斯智能科技有限公司

| Fact | Value | Source | Label |
|---|---|---|---|
| Founded / founder | **2022, Nanjing**. Founder-CEO **Zhu Zonghuang (祝宗煌)**, NUAA graduate, in joint modules since 2018. | Huxiu https://www.huxiu.com/article/4891382.html (2026-09-15) | UNVERIFIED |
| Funding | Three rounds in 2025, latest **≈¥200 M (Series A)** led by 华控基金 + 深创投 (Shenzhen Capital); 普华, 绿洲, 锦秋 followed on. **Series B > ¥300 M announced 2026-09-14** (中信金石 and others). | Huxiu 2026-09-15; Gasgoo https://autonews.gasgoo.com/articles/news/2100179363541975041 (2026-09-16) | UNVERIFIED |
| Shipments | **>100,000 joint modules in 2025** ("industry's first to reach that scale") | Huxiu 2026-09-15; Gasgoo | UNVERIFIED (company claim) |
| Capacity | **>200,000/yr; planning 1 M/yr** | China Baogao 2026-06-27 | UNVERIFIED |
| Vertical integration | "Motors, drivers and reducers are in Encos's own R&D and production system; it built its own production line." Next: flat-wire (hairpin-style) motor windings. | Huxiu 2026-09-15; Gasgoo | UNVERIFIED |
| Range / customers | Planetary, harmonic and cycloid joints, **12–600 N·m peak**. >50 % of robots in the Apr 2025 Beijing half-marathon (both winners fully on Encos); ~60 % at the World Humanoid Games. Revenue, ASP and margin **not disclosed**. | Huxiu 2026-09-15 | UNVERIFIED |
| Price point | EC-A8112-P1-18 (90 N·m) ≈ **$1,000** at a Western reseller | AIFITLAB (repo `actuator_technology_raw.md`) | UNVERIFIED |

### 1.5 Zhaowei / 兆威机电 (Shenzhen, 003021.SZ)

- Zhaowei is a micro-transmission and micro-drive maker (small gearboxes and coreless-motor drives). For humanoids it
  sells **dexterous hands** (A17/B21/B06/C06) and micro-drives for joints. It is not a QDD leg-actuator maker.
- Revenue: ¥1.152 B (2022), ¥1.206 B (2023), ¥1.525 B (2024), ¥1.255 B (9M 2025).
- Gross margin: 29.1 % / 28.9 % / 31.2 % / 32.7 % for the same periods. H1 2026: 30.76 % overall, **micro-transmission
  25.4 %**.
- Source: Sina / 10jqka summaries of the annual report and HK listing documents (UNVERIFIED):
  https://cj.sina.com.cn/articles/view/1850649324/6e4eaaec02002hbte ; https://basic.10jqka.com.cn/003021/operate.html
- This margin profile (≈25–33 %) is a good comparator for a high-volume, cost-driven Chinese drive-component maker.
  Unitree's 59–63 % is an outlier made possible by selling finished robots.

### 1.6 Other Chinese joint-module makers (for scale context)

| Company | City | Funding | Capacity / volume | Process facts | Source | Label |
|---|---|---|---|---|---|---|
| 泉智博 Quanzhibo | — | A+ > ¥100 M (2025); 7 rounds in 18 months (Hillhouse-led, AgiBot / 灵心巧手 in) | 2025: >100k joints shipped, orders >¥150 M. H1 2026: 120k cumulative, **60k in June 2026 alone**. 2026 capacity 300–500k. | **90 s takt per joint** (from 20 min); **>85 % automation**; FPY >96 %, yield >98 %; automated micro-assembly of stator, rotor, reducer, encoder; AGVs; 2,000+ devices on a digital twin; per-unit trace code; dynamic calibration + load test. "Some basic joint modules' **cost** is now at the **hundred-yuan level**; micro joints with driver fell from ~¥1,000 a few years ago to **¥300–400**." | NBD https://www.nbd.com.cn/articles/2026-04-03/4325170.html (2026-04-02); https://www.nbd.com.cn/articles/2026-04-07/4328132.html ; ChinaVenture https://m.chinaventure.com.cn/news/114-20260703-392130.html (2026-07-03) | UNVERIFIED |
| 意优科技 Yiyou | Wuxi + Shanghai Zhangjiang | A, ¥50 M | Delivered 30k (2024), 95k (2025); combined capacity 300k/yr. New Zhangjiang automated line (2026-01-21): 100k/yr, upgradable to 150k. | Line covers assembly, test, calibration, QC | Yicai https://www.yicai.com/news/103017374.html (2026-01) | UNVERIFIED |
| 钛虎 (Hangzhou), 国华 (Qingdao), 睿尔曼, 纽氏达特 | — | various | 80k–100k+/yr each | — | China Baogao 2026-06-27 | UNVERIFIED |

**ESTIMATED — Quanzhibo ASP:** ¥150 M orders ÷ >100k units ≈ **≤ ¥1,500 per joint** (orders ≠ revenue).

**ESTIMATED — one 90 s takt line** = 40 joints/h:
- 1 shift (8 h × 300 d) ≈ **96k joints/yr**; 2 shifts ≈ 192k/yr.
- This matches the 100k–200k/yr "per line" capacities quoted by Yiyou and RobStride.

---

## 2. Cost structure of a humanoid joint actuator in China

### 2.1 Bottom-up component costs (broker teardowns, ANALYST-EST)

**A. China Post Securities teardown of Unitree G1 base (2026-03-30).** These are the broker's estimates, not Unitree
data. Unitree's own joints are QDD planetary.

| ¥ per joint | Small joint (~Ø60 mm, ×14) | Large joint (~Ø80 mm, ×9) |
|---|---:|---:|
| Planetary reducer | 300 (30 %) | 400 (27 %) |
| Motor (stator + rotor + magnets) | 200 (20 %) | 300 (20 %) |
| Encoder(s) (dual) | 200 (20 %) | 300 (20 %) |
| Structure + consumables | 150 (15 %) | 200 (13 %) |
| Driver board | 150 (15 %) | 300 (20 %) |
| **Total** | **1,000** (≈ ₹13,520 / $141) | **1,500** (≈ ₹20,280 / $211) |

Whole-robot figures from the same report:
- G1 base BOM = **¥41,574**; the 23 joints = **¥27,500 (66 %)**, an average of ¥1,196 per joint.
- Assumed processing cost ¥3,000 per robot. Estimated gross margin 40.7 % on the ¥85k base model and 63.5–66.7 % on
  EDU versions; Unitree reported 62.9 % for 9M 2025.

Notes:
- The encoder line (¥200–300 for two magnetic encoders) looks high for a Unitree-volume buyer. Bare magnetic-encoder
  ICs such as MT6835 or AS5047 cost tens of yuan. Treat the motor/encoder/driver split as rough.
- The totals are close to **RobStride's retail list prices** (RS00 ¥598 … RS04 ¥1,199). Either China Post is
  conservative or RobStride's margins at list price are thin. ESTIMATED inference.

**B. CMB International, Optimus-class joints (2026-08-14).** These are harmonic-reducer, torque-sensor joints: the
expensive architecture, not QDD.

| Component per rotary joint | Now ¥ | Long-term ¥ | Decline |
|---|---:|---:|---:|
| Frameless torque motor | 1,300 | 300 | −77 % |
| Harmonic reducer | 1,000 | 250 | −75 % |
| Torque sensor | 1,000 | 200 | −80 % (cost is mostly strain gauges; "domestic vs foreign gauge price gap >10×") |
| Crossed-roller bearing | 200 | 70 | −65 % |
| Angular-contact bearings (×2) | 200 | 120 | −40 % |
| Driver | 300 | 100 | −67 % |
| Encoders (×2) | 800 | 200 | −75 % |
| **Rotary joint total** | **4,800** (≈ $676) | **1,240** (≈ $175) | **−74 %** |
| Linear joint (inverted planetary roller screw) | 5,150 | 1,090 | −79 % |

Whole-robot figures from the same report:
- CMBI's Optimus hardware cost is **≈ ¥320k**: rotary joints 21 %, linear joints 23 %, hands 32 %, sensing 8 %,
  compute 9 %, other 7 %.
- CMBI expects joint modules to fall **another 70–80 %**, and a full-size humanoid to cost **< ¥100k**.
- Harmonic-reducer unit cost is already **−20 % 2023 → 2025**. 绿的谐波 (Leaderdrive) direct materials are only
  **42 %** of its reducer cost (25 % in 2020), so there is still large scale and automation headroom.

**C. Share-of-joint figures (secondary, UNVERIFIED).**
- An industry article puts the shares of a harmonic rotary joint (as % of the robot) at: frameless motor 4 %, harmonic
  reducer 5 %, encoder 2.7 %, driver 1 %, bearings 1.2 %. Source: m.huxiu.com/article/4863413 (MIR 睿工业, 2026-06-01)
  via search snippet; not visible in the fetched text.
- Commonly quoted Morgan Stanley actuator split (secondary blog): reducer / roller-screw 36 %, torque sensor 30 %, motor
  13.5 %, bearings + encoder + housing + firmware 20.5 %. Source: https://fourweekmba.com/where-the-money-goes-in-humanoid-robotics/
  (UNVERIFIED).

**ESTIMATED — what a QDD removes.**
- A QDD planetary joint drops the torque sensor (¥1,000 → 0) and swaps the harmonic reducer (¥1,000) for a 1- or
  2-stage planetary (¥300–400). A thin-section crossed-roller bearing stays.
- This is why QDD joints sell for **¥600–1,500** while Optimus-style joints cost about **¥4,800**: roughly 3–5× apart
  at today's prices.

### 2.2 Raw-material anchors (for a bottom-up motor cost)

| Item | Price | Date | Source | Label |
|---|---|---|---|---|
| Sintered NdFeB **blank**, N38 (Ce) | **¥217–227/kg** | 2026-07-23 | SMM weekly https://news.metal.com/en/newscontent/104021095 | UNVERIFIED (price agency, public summary) |
| NdFeB blank 40H / 45SH (Ce) | ¥267–277 / **¥317–337 per kg** | 2026-07-23 | same | UNVERIFIED |
| PrNd oxide | ¥753–758k/t (Jul 2026); ¥738–740k/t (Sep 2026) | 2026-07/09 | SMM; businessanalytiq | UNVERIFIED |
| Dy-Fe alloy / Tb metal | ¥1.36–1.38 M/t; ¥8.35–8.45 M/t | 2026-07-23 | SMM | UNVERIFIED |
| NdFeB N52 rough blank | ¥165–170/kg | Apr 2024 | Asian Metal headline (search) | UNVERIFIED |
| NdPr price change | Benchmark's China PrNd assessment **+~30 % in Q1 2026** | 2026-04-15 | https://source.benchmarkminerals.com/article/tight-supply-and-chinese-policy-drive-prices-rare-earths-q1-2026-price-review | UNVERIFIED |

**ESTIMATED — magnet cost per actuator.**
- An 80–120 mm outer-diameter QDD motor carries roughly 40–150 g of NdFeB arc segments (assumption; teardown masses
  were not published).
- At ¥220–340/kg of blank, plus about 1.5–2× for slicing, grinding, coating and magnetising, that is **≈ ¥15–100 of
  magnets per actuator** (₹200–1,350).
- Magnets are therefore a small slice of a ¥600–1,500 actuator. The rare-earth risk is about **availability and
  licences, not unit cost**.

### 2.3 Whole-robot BOM and actuator share (Western and Chinese analysts)

| Source (date) | Statement | Label |
|---|---|---|
| Morgan Stanley "Humanoid 100" (Feb 2025) | Optimus Gen 2 BOM ≈ **$50–60k**. Actuators ≈ 56 % of BOM in another MS citation. | UNVERIFIED (press / blog summaries: tagteam.harvard.edu, fourweekmba) |
| Morgan Stanley (note cited Dec 2025 / Jan 2026) | Optimus Gen 2 BOM **≈ $46,000 with the China supply chain vs ≈ $131,000 without**. **Actuators ≈ $22,000 → $58,000** without China. Chips/software $3k → $7k. | UNVERIFIED (SCMP 2025-12-20 via https://tech.yahoo.com/science/articles/china-packs-patent-punch-race-093000841.html ; Interesting Engineering 2026-02-03) |
| Goldman Sachs (2024-02-27) | Humanoid manufacturing cost fell from $50k–250k to **$30k–150k** in a year (**−40 %** vs the 15–20 %/yr expected). TAM $38 B by 2035. | UNVERIFIED (GS web article https://www.goldmansachs.com/intelligence/pages/the-global-market-for-robots-could-reach-38-billion-by-2035.html, summary only) |
| BofA Institute (2026-03-12) | China-built humanoid BOM **$35,000 (2025) → < $17,000 (2030)**. Basis: 16 rotary actuators with harmonic reducers + 14 linear with planetary roller screws. 2030 BOM shares: **linear actuators 27 %, rotary actuators 24 %, dexterous hands 19 %**, i.e. actuators > 50 %. | VERIFIED (BofA PDF text) |
| SemiAnalysis (via Tiger Brokers, 2026-06-11) | Unitree G1 BOM ≈ **$8,976**; gross margin ≈ 67 %. In-house motors "60–70 % cheaper than Western equivalents"; planetary "up to 80 % cheaper" than harmonic. | UNVERIFIED (https://www.itiger.com/news/1105567532) |
| China Post (2026-03-30) | G1 base BOM **¥41,574 (≈ $5,860)**, joints 66 % | ANALYST-EST (PDF read) |
| CMBI (2026-08-14) | Optimus hardware ≈ ¥320k (≈ $45k); joints 44 % (rotary 21 + linear 23) | ANALYST-EST (PDF read) |
| MIR 睿工业 via Huxiu (2026-06-01) | Joint modules ≈ **50 %** of humanoid body cost. China third-party joint-module shipments **>280k in 2025**, ≈5 M by 2030. Third-party share ≈ 63 %. Harmonic + planetary >90 % of shipments. | UNVERIFIED (https://www.huxiu.com/article/4863413.html) |
| 10jqka (2026-07-23) | 2026 joint-module market ≈ ¥3.0–3.5 B. Planetary modules fit ">80 %" of humanoids; harmonic modules limited by impact weakness and cost. ~18k humanoids shipped in China in 2025, ~100k forecast for 2026. | UNVERIFIED (https://stock.10jqka.com.cn/20260723/c678395454.shtml) |

**ESTIMATED — MS actuator dollars per actuator.**
- $22,000 ÷ 28 body actuators (14 rotary + 14 linear) ≈ **$790 per actuator**. This is consistent with CMBI's
  ¥4,800–5,150 (≈ $680–725) per Optimus joint.
- It may include hand actuators, so treat it as an upper bound.

### 2.4 Price and cost decline curve 2023 → 2026

| Series | 2023 | 2024 | 2025 | 2026 | Source / label |
|---|---|---|---|---|---|
| Unitree humanoid ASP (¥ k) | 593 | 260 | 166 | — | prospectus via Guosen — VERIFIED-via-broker |
| Unitree humanoid unit cost (¥ k) | 73.2 | 82.3 | 62.2 (9M) | — | same |
| Unitree quadruped unit cost (¥ k) | 21.5 | 15.7 | 12.1 (9M) | — | same (−44 % 2023 → 9M25) |
| RobStride CN list RS04 / RS03 / RS01 (¥) | — (founded) | 1,199 / 999 / 599 | same | same | 36Kr 2024 + robstride.com — **flat**: cost-down shows up as new models (EduLite) rather than list cuts |
| Xiaomi CyberGear (12 N·m) | **¥499** launch (Aug 2023; "similar products ¥1,000–1,500") | — | — | — | https://www.mi.com/cyber-gear ; news.metal.com 2023-08-29 — UNVERIFIED |
| Quanzhibo micro joint with driver | ~¥1,000 "a few years ago" | | | **¥300–400** | NBD 2026-04 — UNVERIFIED |
| Harmonic reducer unit cost | index 100 | | ~80 | | CMBI — ANALYST-EST |
| Unitree GO-M8010-6 retail (USD) | $500 (earlier) | | | $369 (Unitree shop); $280 elsewhere | search snippets — UNVERIFIED |
| China-built humanoid BOM | | | $35k | → < $17k by 2030 | BofA — VERIFIED |

### 2.5 How cost scales with volume (1k vs 10k vs 100k)

There is no published like-for-like Chinese cost curve. Evidence:

1. **Unitree** shows the fastest observed decline:
   - Humanoid volume ×13 (412 → 5,215), unit cost −24.5 %.
   - Unit labour −55 %, unit overhead −39 %, unit material −17 % (9M 2025 vs 2024).
   - Quadruped volume ×2.5 (2024 → 2025), unit cost −23 %.
   - **ESTIMATED:** this is consistent with a **~75–85 % experience curve on total cost** (15–25 % down per doubling
     of volume). Labour and overhead fall much faster (≈40–50 % per ×10) than materials.
2. Industry statements: "component costs fall 15–20 % with each doubling of cumulative production" (UNVERIFIED,
   wallstreetcn via search snippet). "万台级量产可使单台电机成本下降30%–40%" (10k-unit scale cuts motor cost 30–40 %)
   appears in a search-engine summary of a 2026 Quanzhibo article, but **I could not find it in the article text**
   (UNVERIFIED).
3. **Automation step** (Quanzhibo): 20 min → 90 s per joint; this is what makes 100k+/yr possible. Unitree is still
   "mainly manual assembly" at ~0.5 M joints/yr, so **manual assembly scales to ~10⁵ joints/yr in China** when labour
   is ~¥6–8k/month.

**ESTIMATED illustrative scale table for a 60–120 N·m planetary QDD** (my synthesis of the above; for discussion only):

| Volume / yr | China ex-works cost | China selling price | Main driver |
|---|---|---|---|
| ~1k (prototype batch) | ¥2,000–4,000 | n/a | machined housings and gears, hand winding, manual EOL test |
| ~10k | ¥800–1,500 | ¥1,000–2,000 | die-cast housings, purchased PM or hobbed gears, semi-auto winding |
| ~100k+ | ¥400–1,000 | ¥600–1,200 (RobStride list ~ ASP ¥1,000) | progressive-die laminations, needle-winding cells, automated assembly at 90 s takt, supplier price-downs |

---

## 3. Manufacturing process at Chinese factories

| Step | What Chinese makers do | Evidence | Label |
|---|---|---|---|
| Laminations | Bought from stamping specialists: high-speed press + progressive die with auto-stacking (interlock). Joint makers generally do not stamp in-house. | Unitree "零部件定制采购" for motors (prospectus); generic progressive-die vendor pages (b2bwiki.baidu) | VERIFIED (Unitree mode) / UNVERIFIED (generic) |
| Stator winding | Multi-station **needle (in-slot) winding** machines for inner-rotor stators; flyer/needle for outer-rotor. Encos is moving to **flat-wire** windings for higher slot fill. | Shanghai Wind 4-station needle winder spec (stator OD 20–100 mm, wire 0.08–1.0 mm, 680 kg) https://b2usa.com/hotsite/shanghaiwind2/bldc-motor-inslot-needle-winding-machine ; Ningbo NIDE (OD ≤ 150 mm); Encos flat-wire (Gasgoo 2026-09-16) | UNVERIFIED |
| Magnets / rotor | Unitree: "stator winding + permanent-magnet segments + one-piece rotor hub (磁钢座)"; inner-rotor low-inertia PMSM, 3,000–5,000 rpm max | China Post teardown | ANALYST-EST (photos) |
| Gears | G1 reducer gears bought from **美湖股份**. RobStride flagship: alloy steel, "die-cast then post-processed"; EduLite: powder metallurgy and plastics. A 2-stage planetary of ≈20.6:1 in G1 small joints. | China Post; 36Kr 2025-09-10 | ANALYST-EST / UNVERIFIED |
| Housings | Aluminium die-casting, one-piece (RobStride) | 36Kr 2025-09-10 | UNVERIFIED |
| Bearings | Thin-section crossed-roller (洛阳佰纳 CRBT355A, ID 35 mm, section 5 mm) | China Post | ANALYST-EST (logo visible in teardown) |
| Electronics | Encoders and drivers: own design, bought components, **SMT outsourced** (Unitree) | prospectus via Guosen | VERIFIED-via-broker |
| Assembly | Unitree: mainly manual today. Quanzhibo: >85 % automated, 90 s per joint. Yiyou: automated line (assembly, calibration, test). | Guosen; NBD; Yicai | VERIFIED-via-broker / UNVERIFIED |
| End-of-line test | Quanzhibo: dynamic calibration and **load test** per joint, unique trace code. Assembled modules are tested for **temperature, speed, torque, current, voltage**. Whole robots get ~200 functional and **burn-in tests over 8–10 h** (Beijing-Tianjin-Hebei "super factory"). Back-EMF, cogging and hipot per joint: **not described** in any source found (normal motor-industry practice, see below). | NBD; https://www.chinanews.com.cn/cj/2026/06-16/10641852.shtml (2026-06-16) | UNVERIFIED |
| Yield | FPY > 96 %, overall yield > 98 % (Quanzhibo); FPY > 95 % (Yiyou) | NBD; search snippet | UNVERIFIED |

Typical motor-industry EOL checks: resistance and inductance balance, insulation resistance and hipot, surge or
inter-turn test, back-EMF constant and waveform, cogging torque, no-load current and speed, encoder offset calibration,
plus a short burn-in or thermal soak. These are listed as **common practice (UNVERIFIED for any named maker)**.

### 3.1 Capex benchmarks

| Item | Figure | Source | Label |
|---|---|---|---|
| 富临精工 (Fulin) one "robot smart electric joint module" production line + R&D base, Mianyang, in leased factory space | **¥110 M** total (capacity not stated) | SZSE announcement 2025-02-12 https://static.cninfo.com.cn/finalpage/2025-02-12/1222524317.PDF | VERIFIED |
| 豪能股份 (Haoneng) robot joint **reducer** base, Luzhou | **¥1.0 B for 5 M reducers/yr** → **ESTIMATED ¥200 capex per annual reducer of capacity** | SSE announcement 2026-07-30 https://static.cninfo.com.cn/finalpage/2026-07-30/1225446835.PDF | VERIFIED (ratio ESTIMATED) |
| 中鼎股份 subsidiary: robot joint core-component project | ¥389.7 M for **28,000 joints/yr** + 3,000 sensor/control sets → ≈ ¥13.9k per annual joint (high-end joints, includes buildings) | cs.com.cn 2026-05-26 (search snippet) | UNVERIFIED |
| Unitree IPO "smart robot manufacturing base" | ¥624 M for 75k humanoids + 115k quadrupeds/yr (whole robots incl. joints) | Guosen (prospectus) | VERIFIED-via-broker |
| BLDC needle-winding machine (China, export listings) | **$50,000–100,000** typical listing (4-station / 18-slot needle winders). Some listings show $300k–800k, which look like placeholder prices. | https://www.made-in-china.com/products-search/hot-china-products/Bldc_Stator_Needle_Winding_Machine.html | UNVERIFIED (listing prices, not quotes) |
| Simple / servo winding machines (1688 domestic) | ¥2,100–28,000 | https://www.1688.com/market/-B5E7CFDFC8C6CFDFBBFA.html (search summary) | UNVERIFIED |
| Small gear-hobbing machines (Alibaba) | Y3608 hydraulic **$7,800**; Y3115CNC **$12,000** | Alibaba listings (search snippets) | UNVERIFIED |
| Progressive die + high-speed press for laminations | **no price found** | — | not found |
| Back-EMF / hipot / dyno EOL test bench | **no price found** | — | not found |

**ESTIMATED — capex for a minimal small-volume (≤ 5k/yr) in-house line.**
- If laminations, magnets and gears are bought in: 1–2 semi-auto needle or flyer winders ($20k–100k), a varnish/oven
  station, a press-fit and bonding station, a magnetiser (if magnetising in-house), a CNC lathe/mill cell for housings,
  a dyno/EOL bench, and a burn-in rack.
- The total is plausibly **₹0.5–1.5 crore**, versus ¥100 M+ (₹13.5 crore+) for a Chinese 100k-class automated line.
- This is my synthesis from the listing prices above. It is **not quoted** and should be firmed up with Indian and
  Chinese supplier quotes.

### 3.2 Labour cost China vs India

| Metric | Value | Source | Label |
|---|---|---|---|
| China urban **private-unit manufacturing** average wage 2025 | **¥76,055/yr** (≈ ¥6,340/month ≈ ₹85,700/month ESTIMATED), +6.4 % y/y | NBS release 2026-05-15 https://www.stats.gov.cn/xxgk/sjfb/zxfb2020/202605/t20260515_1963707.html (via search summary and ithome) | VERIFIED (official; figure via summary) |
| China urban **non-private** manufacturing 2025 | **¥101,291/yr** (+5.2 %) | same | VERIFIED |
| China all-sector 2025: non-private / private | ¥129,441 / ¥71,590 per yr | https://www.ithome.com/0/952/418.htm | UNVERIFIED (media quoting NBS) |
| India regular wage/salaried avg monthly earnings 2025 (PLFS) | men **₹24,217**, women ₹18,353 | PLFS annual report 2026-03-27 (via search summary) | UNVERIFIED |
| India factory worker daily wage, ASI 2021-22 | ₹563/day avg (direct ₹586, contract ₹523) | CEDA https://archive.ceda.ashoka.edu.in/?p=7587 | UNVERIFIED (analysis of ASI) |

**ESTIMATED.**
- A Chinese private-sector factory worker costs **≈ 3.5–4.5×** an Indian regular factory worker in wages (₹85.7k vs
  ₹19–24k per month), before social charges.
- At Unitree's direct-labour share (≈7–8 % of COGS), India's wage advantage is worth only **~5–6 % of actuator cost**
  at equal productivity.
- The real gap is material and parts cost at volume, plus productivity and yield, **not wages**.

---

## 4. Supply-chain facts (magnets, India)

| Fact | Value | Source | Label |
|---|---|---|---|
| China share of sintered permanent-magnet production, 2024 | **~94 %** (also ~60 % of mined magnet REEs, ~91 % of refined) | IEA figures quoted by https://www.skillings.net/?p=101182 (search summary) | UNVERIFIED (IEA via secondary) |
| China sintered NdFeB capacity | ~380 kt (2025), approaching 400 kt (2026) | same / Argus | UNVERIFIED |
| China share of REE mine output 2025 | 270 of 390 kt REO = **69 %** | mining-technology.com | UNVERIFIED |
| **MOFCOM/GAC Announcement No. 18 (2025-04-04)** | Licences required for 7 medium/heavy REEs (Sm, Gd, Tb, Dy, Lu, Sc, Y) and their alloys, compounds and **Tb/Dy-containing NdFeB magnets**. **Still in force** (not suspended in Nov 2025). Licence review "45 working days" nominal, longer in practice. | MOFCOM https://english.mofcom.gov.cn/Policies/AnnouncementsOrders/art/2025/art_0dd87cbee7b045bf93fabe6ab2faceee.html ; China Briefing (updated 2025-11-10) | VERIFIED (MOFCOM) / UNVERIFIED (status commentary) |
| Oct 2025 expansion (Ann. 55–58, 61, 62 of 2025-10-09) | Added Ho, Er, Tm, Eu, Yb; **extraterritorial 0.1 % de-minimis** rule for foreign products containing Chinese REE; equipment and technology controls | China Briefing | UNVERIFIED |
| Suspension | **Ann. No. 70 (2025-11-07) suspends the Oct 2025 measures until 2026-11-10**, after the US–China truce. **The suspension ends about one month after this note's date; no extension had been announced in the sources found.** | CIRS https://www.cirs-group.com/en/chemicals/china-temporarily-suspends-export-controls-on-key-raw-materials-including-rare-earths-lithium-batteries-and-diamond ; mining-technology.com | UNVERIFIED (secondary; MOFCOM text not read) |
| Do the controls cover finished motors/actuators? | China Briefing says parts and assemblies containing controlled magnets are covered. My reading: that wide scope came with the **suspended** Oct 2025 rules; No. 18 lists the magnet items themselves. In practice RobStride actuators kept being sold to India through 2025–26 (Alibaba listings in `alibaba_robstride_prices_2026-09-24.md`). **Treat as a live legal risk after 2026-11-10.** | China Briefing; repo file | UNVERIFIED / ESTIMATED inference |
| India's dependence | India imported ~**90 % (FY24–25)** of RE permanent magnets from China. No Indian licence applications approved by June 2025; auto production cuts were threatened from July 2025. | CareEdge via https://www.autocarpro.in/news/chinas-export-controls-on-rare-earth-elements-disrupt-indian-automotive-production-126956 (2025-06-12) | UNVERIFIED |
| India magnet imports FY25 | ~53.7–57 kt, 93 % from China (search summary); SBI report **$291 M** in FY25 | search summaries; https://oga-prod.angelone.in/news/economy/india-s-rare-earth-magnet-imports-soar-to-291-million-in-fy25-amid-china-ban-sbi-report | UNVERIFIED |
| First Chinese licences to Indian firms | ~**2025-10-31**, conditional | https://www.drishtiias.com/daily-updates/daily-news-analysis/india-gains-access-to-chinese-rare-earth-magnets/print_manually | UNVERIFIED |
| **India REPM scheme** | Cabinet approval **2025-11-26**: **₹7,280 crore** = ₹6,450 cr sales-linked incentive over 5 yrs + ₹750 cr capital subsidy. Target **6,000 t/yr** integrated sintered NdFeB, up to 5 beneficiaries (600–1,200 t each). 7-year term (2 yr gestation + 5 yr incentives). | PMIndia https://www.pmindia.gov.in/en/news_updates/cabinet-approves-rs-7280-crore-scheme-to-promote-manufacturing-of-sintered-rare-earth-permanent-magnets-repm | VERIFIED |
| REPM tender | MHI RFP 2026-03-20; deadline moved several times; technical bids opened **2026-08-13**; **20 bids** (incl. Coal India, L&T, ReNew, Prozeal, Attero, Midwest JV). Beneficiaries **not yet announced** as of the latest found. | https://www.energetica-india.net/news/mhi-receives-20-bids-under-inr-7280-crore-repm-manufacturing-scheme ; IANS 2026-03-20 and 2026-06-25 | UNVERIFIED (trade press) |
| Indian NdFeB plants | **Midwest Energy**, Hyderabad: ₹250 cr, "India's first sintered NdFeB plant", 500 t/yr from ~mid-Oct 2026, 5,000 t/yr by Dec 2027. **N.A.N MagneTech**, Naidupeta (AP): integrated plant announced. | digg / metal-powder.tech summaries | UNVERIFIED |
| Union Budget 2026-27 | BCD exemption on capital goods for critical-mineral processing; monazite duty 2.5 % → 0 | taxtmi search summary | UNVERIFIED |

### 4.1 Indian motor makers who could do job-work (stators, windings, magnets, motors)

| Company | City | What they make | Relevance | Source | Label |
|---|---|---|---|---|---|
| Vector Technics (Zen Technologies subsidiary) | Hyderabad (Shamshabad) | Drone BLDC motors, ESCs, propellers; **in-house winding**; 300k units/yr capacity (Jul 2026) | Closest analogue to a QDD motor stator/rotor job-shop; outrunner 40xx–80xx class | https://defence.in/threads/vector-technics-emerges-as-indias-largest-fully-integrated-drone-propulsion-manufacturer-expands-manufacturing-capacity-to-300-000-units-annually.18234/ | UNVERIFIED |
| Reflex Drive | Lucknow | Heavy-lift drone motors, ESCs | same | Techadyant 2026 | UNVERIFIED |
| Zepco Technologies | Bengaluru | ESCs, motors | FOC driver know-how | Techadyant 2026 | UNVERIFIED |
| Iindepro Dynamics | Rajkot | UAV brushless motors | Rajkot motor cluster | YourStory 2026-08 (403 on fetch; search snippet) | UNVERIFIED |
| Bharath Components | Gurugram | Drone BLDC motors (150–420 KV) | | indiandefensenews 2025-10 | UNVERIFIED |
| Lucas TVS | Puducherry | EV hub motors and controllers in series production | Stator winding and magnet-rotor assembly at scale | autocarpro / motorindiaonline | UNVERIFIED |
| Sona Comstar | Gurugram / Chennai | 2W/3W BLDC hub and drive motors and controllers (since 2020) | | autocarpro | UNVERIFIED |
| Weber Drivetrain | Chakan, Pune | "Automated" BLDC hub-motor + controller plant (₹35 cr phase 1) | Pune job-work candidate | themachinemaker; Outlook Startup 2023-10 | UNVERIFIED |
| BLDC ceiling-fan makers (Atomberg, Havells, Crompton, Orient, Bajaj, Usha) | various | High-volume small outer-rotor BLDC stators; ferrite magnets typical | Winding and lamination capacity, but low torque density | electronicsforu, NRDC | UNVERIFIED |

Indian drone-propulsion facts (Techadyant 2026, UNVERIFIED):
- Imports of drone components fell from >80 % (2020) to <40 % (2025). Reflex, Vector and Zepco hold ~65 % of domestic
  motors and ESCs.
- **Magnets and MCUs remain 80–100 % imported**. Magnet imports *rose* from ~$38 M to ~$50 M as assembly localised.
- Illustrative 80xx motor: Chinese **landed $125 vs Indian domestic $106** (ex-works $95 vs $98; duty $12, GST $5,
  freight $7, financing $6).

### 4.2 Indian robot-actuator makers (QDD)

| Company | Product / price | Source | Label |
|---|---|---|---|
| xTerra Robotics | QDD A2: 3 N·m rated / **12 N·m peak**, 550 g, CAN-FD, **₹94,400 incl. GST** (out of stock at Robu) | https://robu.in/product/xterra-actuator-qdd-a2/ (checked 2026-09-24, repo file) | VERIFIED (listing) |
| Bhairav Robotics (Kakinada) | "Prabal" QDD, "designed and manufactured entirely in India" for robots, RCWS, exoskeletons; **price not published** | https://www.indiandefensenews.in/2025/08/bhairav-robotics-unveils-prabal-qdd.html (2025-08) | UNVERIFIED |
| Addverb (Reliance, Noida) | In-house humanoid (Elixis-W wheeled humanoid, early 2026). Actuator source and cost not disclosed. Plant claims 10k robots/yr. | outlookbusiness | UNVERIFIED |
| Havells | Hiring "Lead Actuator Engineer – Robotics/Humanoids" (CRI) | jobs.weekday.works listing | UNVERIFIED |

**ESTIMATED.** xTerra's 12 N·m QDD at ₹94,400 is **≈ 11.7×** RobStride RS00 (14 N·m) at its China list price
(¥598 ≈ ₹8,085) and ≈ 5.7× its landed Alibaba price (≈ ₹16.5k). This is the price gap Indian low-volume QDD makers
show today.

---

## 5. India import duty and GST (buy parts vs buy finished actuators)

| HS | Item | BCD | Cess / SWS | IGST | Total on CIF | Source / date | Label |
|---|---|---|---|---|---|---|---|
| 8501 31 / 8501 32 (DC motors ≤ 750 W / > 750 W; geared actuators normally classify here) | integrated actuator or bare motor | **15 %** | AIDC 2.25 + SWS 1.73 | 18 % | **40.39 %** | eximpe (citing CBIC/ICEGATE, 2026-05-13) https://eximpe.com/hsncode-finder/85013119 ; /85013210 | UNVERIFIED (aggregator) |
| 8501 (repo assumption) | same | 10 % | SWS | 18 % | **32.28 %** | `bom/build_bom.py` (cybex / seair, VERIFIED-secondary in repo) | **Conflicts with eximpe; check ICEGATE before ordering** |
| 8483 40 00 | gearboxes, speed changers, ball/roller screws | 7.5 % | AIDC 0.56 + SWS 0.81 | 18 % | **28.47 %** | eximpe 2026-05-13 https://eximpe.com/hsncode-finder/84834000 | UNVERIFIED |
| 8505 11 (metal permanent magnets) | NdFeB magnets (85051190 "other"; the 85051110 page fetched is "ferrite cores") | 7.5 % | AIDC 0.56 + SWS 0.81 | 18 % | **28.47 %** | eximpe https://eximpe.com/hsncode-finder/85051110 ; generic 8505 = 7.5 % (search) | UNVERIFIED (exact 8-digit line for NdFeB not confirmed) |
| 8503 (parts of motors: stators, rotors, laminations) | — | not checked | | | | — | not found |

**ESTIMATED — what is really a cost.**
- For a **GST-registered Indian company**, IGST (18 %) is creditable against output GST. The non-recoverable part is
  BCD + cess + SWS:
  - Motors / actuators (8501): ≈ **19.0 %** (eximpe stack) or ≈ **11 %** (repo assumption).
  - Gearboxes (8483) and magnets (8505): ≈ **8.9 %**.
- So importing **parts** (magnets, gears, bearings) carries roughly half the non-creditable duty of importing finished
  actuators. On a ₹16k RS04-class actuator the difference is ≈ ₹0.3k (repo's 11 % basis) to ₹1.6k (eximpe's 19 %
  basis) per unit.
- That is far smaller than the 5–12× price gap between Chinese volume actuators and Indian low-volume ones (§4.2). Duty
  alone does not justify in-house building; volume and parts cost dominate.
- For an unregistered buyer or a student lab, the full 28–40 % applies.

---

## 6. Key takeaways for the paper (ESTIMATED synthesis; cite the rows above)

1. **Chinese QDD price floor is ~¥600–1,200 (₹8–16k, $85–170) per actuator at list**, with volume ASPs ~¥1,000
   (RobStride 2026 guidance) to ≤¥1,500 (Quanzhibo). Broker teardown cost of a Unitree G1 joint is ¥1,000–1,500.
   Harmonic + torque-sensor joints are ~¥4,800 today.
2. **Cost composition** (G1 teardown): reducer ~27–30 %, motor ~20 %, encoders ~20 %, driver 15–20 %, structure 13–15 %.
   Magnet material is only ~¥15–100 per actuator (ESTIMATED).
3. **Scale:** leaders ship 10⁵ joints/yr per company: RobStride >50k cumulative by Sep 2025 with a 300k target for
   2026; Encos >100k in 2025; Quanzhibo >100k in 2025 and 60k in June 2026; Yiyou 95k; Unitree ≈ 0.45–0.5 M in-house
   (ESTIMATED). Automated lines run at a **90 s takt** with >85 % automation, yet Unitree is still mostly manual.
4. **Margins:** Unitree 60 % (vertically integrated robot seller; robot components 59 %). Pure drive-component makers
   such as Zhaowei run ~25–33 %. Joint-module start-ups do not disclose margins.
5. **Wages are not the gap:** China manufacturing wages are ~3.5–4.5× India's, but direct labour is only ~7–10 % of
   Unitree COGS.
6. **Rare earths:** China makes ~94 % of sintered magnets. No. 18 licences still apply to Dy/Tb magnets. The wider
   Oct 2025 rules are suspended only **until 2026-11-10**. India's REPM scheme (₹7,280 cr, 6,000 t/yr) has 20 bids but
   no awards yet, and the first Indian NdFeB output (Midwest, 500 t/yr) is only starting around Oct 2026.
7. **Duty:** 8501 motors/actuators 32–40 % all-in (sources conflict); gears and magnets ~28.5 %. For a GST-registered
   firm the non-creditable part is ~11–19 % on motors/actuators and ~9 % on gears and magnets.

## Open gaps (not found in this session)

- RobStride and Damiao factory locations, headcount and gross margins. Damiao funding and volumes.
- Morgan Stanley, Goldman Sachs and UBS primary PDFs. No UBS teardown found.
- Capex quotes for progressive dies, high-speed presses and EOL testers. Per-joint EOL test list for any named Chinese
  maker.
- Exact BCD for 8503 (motor parts) and the 8-digit NdFeB line in 8505. The 8501 BCD conflict (10 % vs 15 %).
