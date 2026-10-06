# India robotics / actuator industry, manufacturing architectures and capital: raw research notes

Compiled 2026-10-06 for the business report on starting a humanoid-robot **actuator** manufacturing company in India.

## Conventions

- **Labels:**
  - **VERIFIED** = primary or official source opened and read in this session (company press release filed on
    NSE/BSE, government PIB document, IFR press release, company website).
  - **ESTIMATED** = my arithmetic. The method is shown.
  - **UNVERIFIED** = secondary source: trade press, startup media, search-result summary, aggregator database
    (Tracxn/CB Insights/Inc42 company pages), or a page that returned 403 so that only the search snippet was seen.
- Many Indian media pages (YourStory, Business Standard, Mint, Entrackr, ipocentral) returned **HTTP 403** to the fetch
  tool. For those, the figure comes from the search engine's summary of the page and is labelled UNVERIFIED.
- **Currency:** USD/INR **95.96**, as in `bom/build_bom.py` and the other raw files. 1 crore (cr) = ₹10 million;
  1 lakh = ₹100,000.
- **Do not duplicate.** These facts are already in the repo and are only cross-referenced here:
  - `china_actuator_manufacturing_economics_raw.md`:
    - §3 and §3.1: Chinese process and capex
    - §3.2: China vs India wages
    - §4: rare-earth controls and the India REPM scheme (₹7,280 cr)
    - §4.1: Indian motor job-work candidates (Vector Technics, Reflex Drive, Zepco, Lucas TVS, Sona Comstar, Weber,
      fan makers)
    - §4.2: Indian QDD makers (xTerra QDD A2 ₹94,400; Bhairav Prabal; Addverb; Havells job ad)
    - §5: import duty
  - `actuator_technology_raw.md`: xTerra and other Indian availability notes, Indian reseller prices.
  - `india_robu_browser_sourcing_raw.md` line 26: the Robu listing for the xTerra QDD A2.
  - `india_motor_materials_raw.md`:
    - §6.1: Indian winding-machine prices (₹2,800 manual to ₹2 lakh CNC)
    - §4.6: Indian PCBA providers
  - `india_mechanical_manufacturing_raw.md` §6: Indian CNC, laser and anodising job-work rates.

---

## 1. Indian companies relevant to robot actuators

### 1A. Robot-actuator makers and robot companies that build their own joints

| Company (city, founded) | Product / actuator approach | Published torque / price | Manufacturing approach | Headcount / revenue | Funding, investors, valuation | Sources (date) | Label |
|---|---|---|---|---|---|---|---|
| **xTerra Robotics** (registered Kanpur UP; operations Bengaluru; founded Mar 2023) | Quadrupeds, humanoids. Actuators and electronics designed in-house ("compact gearbox design", compliant, back-drivable). | QDD A2: 3 N·m rated, 12 N·m peak, 550 g, 14-bit encoder; ₹94,400 incl GST on Robu (see repo files). No other models are listed on its site. | Machining **outsourced** to "aerospace-grade partners in Bengaluru"; **assembly in Kanpur**. | 15 staff incl. 5 co-founders (8 R&D, 2 production); 12 customers. Revenue "crossed 10 million" (currency not stated; probably ₹1 cr). | **No VC.** Grants via incubators (IIT Kanpur SIIC, I-Hub Foundation IIT Delhi, ITEL Chennai). | electronicsforu interview 2026-05-20 https://www.electronicsforu.com/electronics-startups/talent-is-harder-to-find-than-funding-so-we-develop-it-in-house-and-train-students-at-iits-and-nits-aditya-pratap-singh-rajawat-xterra-robotics ; site https://www.xterrarobotics.com/ (A2: 12 N·m, 550 g) | UNVERIFIED (interview); VERIFIED (site specs) |
| **Bhairav Robotics** (Kakinada AP; founded 2023, incorporated late 2024) | "Prabal" QDD for robots, RCWS, exoskeletons, satellite tracking. Also UGVs and the "Shvana" quadruped. | Not published | "Designed and manufactured entirely in India" (claim) | n/a | **Zen Technologies took 45.33 %** (Feb 2025). Reported cash in: ₹4 cr (INR 40 M). ESTIMATED implied post-money ≈ ₹4 cr ÷ 0.4533 ≈ **₹8.8 cr (~$0.9 M)**, if it was all primary. | indiandefensenews 2025-08 (repo); machinist.in 2025-02-17 https://machinist.in/2025/02/zen-technologies-acquires-stakes-in-vector-technics-and-bhairav-robotics/ ; dealroom summary https://app.dealroom.co/companies/bhairav_robotics_llp | UNVERIFIED / ESTIMATED |
| **Perceptyne** (Hyderabad, 2021) | Dual-arm "semi-humanoid" industrial robots PR-34D (7-DOF arms, 5-finger hands, tactile sensing) and PR-9D. Says it builds "the entire robotics stack in-house, from actuators to AI software". | No actuator specs. Claims its dual-arm robot sells at about **1/10 of $100k+** competitors (no list price found). | In-house actuators (claim; no process detail found) | ">150 employees" (2026 secondary) | Pre-seed led by Venture Catalysts. **Seed $3 M, Oct 2024, co-led by Endiya Partners and Yali Capital**, with Whiteboard Capital. 2026 secondary sources claim ₹30 cr raised in total (incl. ₹5 cr pre-seed from T-Hub and the Startup India Seed Fund) and a **term sheet for $10 M from Premji Invest at a $50 M valuation**. That claim could not be confirmed. | Entrackr 2024-10 https://entrackr.com/2024/10/deeptech-robotics-startup-perceptyne-raises-3-mn-in-seed-round ; ventureintelligence; techleap feed (403) https://finder.techleap.nl/news/feed/perceptyne-raises-3-6m-to-build-ai-humanoid-robots-for-indian-factories ; YourStory 2026-04 (403) | UNVERIFIED |
| **Addverb Technologies** (Noida; Reliance-owned; founded 2016) | Warehouse automation. Humanoids **Elixis-W** (wheeled; launched LogiMAT India 2026, Mumbai) and **Elixis** (walking; launch "later in 2026"). Actuators: "high-speed **BLDC actuators** and **planetary gearboxes**". Whether they are made in-house is **not disclosed**. | Elixis-W: 67 DOF (24 in hands), 75 kg, 183 cm, 10 kg payload, 1.5 m/s; **$45,000** (humanoid.guide, marked "Not Verified"). No torque data. | Noida plant: 60,000 m², ≈ **₹75 cr** facility cost, up to 60k robots/yr (2022 press release). Later "100,000 robots/yr" (2026). | Revenue **FY25 ₹800 cr**; FY27 target > ₹1,400 cr. FY26 order book ₹1,400 cr. Target **3,000 humanoids deployed by 2030**. | Reliance: **$132 M** (≈ 54 % stake, 2021). | Addverb PR 2022-04-12 https://addverb.com/press-release/addverb-technologies-to-open-worlds-largest-robot-manufacturing-factory-in-india ; themachinemaker 2026 https://themachinemaker.com/news/addverb-marks-10-years-with-expansion-into-humanoid-robotics/ ; humanoid.guide https://humanoid.guide/?p=18863 | VERIFIED (2022 PR) / UNVERIFIED (rest) |
| **General Autonomy** (Bengaluru; incorporated May 2023; ShareChat co-founders) | "Param" quadruped and "Atom 01" humanoid (31 kg, built in about 4 months; price target < ₹20 lakh ≈ $21k ESTIMATED). Builds "far more in-house" but **imports "a handful of specialised actuators"** and NVIDIA compute. A Feb 2026 article says actuators are the "only non-indigenous component" of Param. | — | Custom-machined aluminium and carbon profiles; imported actuators | ~19 staff; **pre-revenue** | Pre-seed ₹25 cr (Nov 2023; India Quotient, Elevation). **Seed ₹32 cr at ₹280 cr valuation (May 2026)**, led by Elevation Capital and India Quotient. ESTIMATED: ₹280 cr ≈ **$29.2 M**; dilution ≈ 11.4 % if post-money. | Inc42 2026-05 https://inc42.com/buzz/exclusive-robotics-startup-general-autonomy-raises-₹32-cr-at-₹280-cr-valuation/ ; officechai https://officechai.com/startups/how-general-autonomy-is-building-robot-dogs-and-humanoid-robots-in-india/ ; startupfeed 2026-02 https://startupfeed.in/?p=4639 | UNVERIFIED. Conflict: startupfeed calls it a "bootstrapped 5-person team", which contradicts the funding reports. |
| **Svaya Robotics** (Hyderabad, 2018) | India's "first indigenous" cobot (2023); quadruped (25 kg payload) and exoskeleton with DRDO R&DE and DEBEL; humanoid claimed. Mechanics, control electronics and software in-house (vertically integrated). | n/a | In-house design (claim) | n/a | **Bootstrapped** (per aiwiki) | aiwiki https://aiwiki.ai/wiki/svaya_robotics ; roboticsandautomationnews 2023-02-06 | UNVERIFIED |
| **Twara Robotics** (ARTPARK / IISc Bengaluru) | Actuators, industrial arms and soft grippers. Founder says actuators are "nearly 70 % of a robot's cost and complexity". | n/a | "Precision manufacturing" named as the critical challenge | 11+ staff | Grant-backed: MHI CAMRAS accelerator, DST, Govt of Karnataka | themachinemaker 2025-03-21 https://themachinemaker.com/madeinindia/twara-robotics-revolutionizing-indian-manufacturing/ | UNVERIFIED |
| **Quintrans** (Pune, 2021) | Direct-drive **linear** electromagnetic actuators. Target 500,000 actuators/yr by 2030. | n/a | Setting up in-house manufacturing and test facility in Pune | n/a | **$750k pre-seed** led by Capital-A (2025-12-17); IIMA Ventures and others | themachinemaker https://themachinemaker.com/news/capital-a-anchors-750000-pre-seed-investment-in-quintrans-to-advance-indigenous-linear-motion-systems/ | UNVERIFIED |
| **Havells (CRI)** (Noida) | Hiring a "Lead Actuator Engineer – Robotics/Humanoids" to develop **strain-wave (harmonic) and QDD actuators** for humanoids, quadrupeds, cobots and surgical robots. | — | Large appliance and motor maker entering the field | — | Listed company | jobs.weekday.works listing https://jobs.weekday.works/lead-actuator-engineer-robotics-humanoids-havells-cri-at-havells-india-ltd-wkdydpjw7k | UNVERIFIED (job ad) |
| **iHub Robotics** (Kochi, 2022) | Service humanoid "Tara" and industrial humanoid "Daksha" (25 kg payload). Control boards and BMS in-house. Actuator sourcing **not disclosed**. ~28–30 % of components from Japan, Taiwan and China; "~70 % indigenous". | — | Makes 10–20 robots/month (another article claims capacity of 300/month: conflict) | 75 staff (32 R&D); ~62 Tara units deployed; break-even | ₹4.3–4.5 cr pre-seed from US angels (2024/25) | circuitdigest interview https://circuitdigest.com/interview/ihub-robotics-kerala-startup-building-almost-every-layer-of-its-humanoids-in-house ; electronicsforu https://www.electronicsforu.com/electronics-startups/kerala-startup-building-humanoid-robots-from-scratch | UNVERIFIED |
| **DRDO R&DE (Engineers)** (Pune) | Military humanoid: separate upper- and lower-body prototypes after 4 years of work; completion target 2027. Actuator source not stated. | — | Govt lab | — | Govt | dtnext/PTI 2025-05 https://www.dtnext.in/news/national/drdo-scientists-working-on-humanoid-robot-for-military-missions-to-reduce-risk-for-troops-833155 | UNVERIFIED |

### 1B. Other Indian robotics hardware companies (customers or comparables; mostly buy their motors)

| Company | What | Funding / valuation | Revenue / scale | Source | Label |
|---|---|---|---|---|---|
| CynLr (Bengaluru, 2019) | Vision-based dexterous manipulation "CyRo" (3-arm). Supply chain of **400+ parts from 14 countries**. Target of 1 robot system/day and $22 M revenue by 2027. | **Series A $10 M (Nov 2024)**, led by Pavestone and Athera, with Speciale Invest and Infoedge (Redstart); total $15.2 M | 25 systems in lab | therobotreport / AIM / inc42 https://www.therobotreport.com/cynlr-raises-series-a-funding-to-realize-robot-vision-for-universal-factory/ | UNVERIFIED |
| Ati Motors (Bengaluru) | Autonomous tuggers "Sherpa"; "Sherpa Mecha" dual-arm mobile manipulator (Oct 2025) | **Series B $20 M (Jan 2025)**, led by Walden Catalyst and NGP; earlier Series A $10.85 M (Jul 2023, True Ventures), pre-A $3.5 M (2021); total > $37 M. Others: Exfinity, Athera, Blume, MFV. | Hundreds of Sherpas at ~40 manufacturers | pulse2 / entrepreneur https://pulse2.com/ati-motors-autonomous-robotics-company-raises-20-million-series-b | UNVERIFIED |
| Unbox Robotics (Pune) | Swarm sortation robots | **Series B $28 M (Jan 2026)**, led by ICICI Venture and Redstart Labs (Info Edge); with F-Prime, 3one4, Navam, Force Ventures; primary plus secondary. Valuation $25 M (Jan 2024, CB Insights). | — | evertiq 2026-01-22 https://evertiq.com/news/2026-01-22-indias-unbox-robotics-raises-28-million-in-series-b | UNVERIFIED |
| Genrobotics (Thiruvananthapuram) | Bandicoot sewer robot, G-Gaiter rehab exoskeleton | > ₹100 cr raised incl. debt (Zoho ₹20 cr in 2022, Unicorn India Ventures, Peak XV, Anand Mahindra). Seeking a **₹150 cr Series B**. ₹150 cr Tamil Nadu plant MoU. | **FY26 revenue ₹43.7 cr** (+35 %), PAT ₹2.6 cr, EBITDA 15.2 %. 30,000 sq ft of manufacturing (Kerala and AP). | Inc42 2026-07-11 https://inc42.com/buzz/zoho-backed-genrobotics-posts-₹2-6-cr-profit-in-fy26-eyes-₹150-cr-series-b-round/ | UNVERIFIED |
| Peer Robotics | Haptic-sensing cobot / mobile manipulators | $2.3 M seed, led by Kalaari (with Axilor and others); total ~$2.6 M | — | peoplematters https://www.peoplematters.in/news/funding-investment/peer-robotics-secures-23-million-in-seed-funding-to-help-companies-automate-operations-35278 | UNVERIFIED |
| Armatrix (Bengaluru, 2024) | Snake-arm manipulator (> 22 DOF, 3–5 m long, 50–150 mm diameter): many small actuators | $2.1 M (₹18 cr) seed, led by **pi Ventures** | — | Entrackr https://entrackr.com/snippets/deep-tech-robotics-startup-armatrix-raises-21-mn-led-by-pi-ventures-11152392 | UNVERIFIED |
| Anscer Robotics (Bengaluru) | AMRs | $2 M seed (Info Edge, Feb 2025); **₹45 cr Series A (2026, IAN Group)** | — | inc42; search summary | UNVERIFIED |
| Sastra Robotics (Kochi) | Robotic test automation | ~$185k across 2 rounds | — | CB Insights page | UNVERIFIED |
| Haddock | (identity unclear) | CB Insights: $3.56 M over 10 rounds; Wayra investor. **Probably not the Indian company the brief meant: not used.** | — | https://www.cbinsights.com/company/haddock/financials | UNVERIFIED |
| Ottonomy, Mukunda Foods | not researched (budget) | — | — | — | GAP |

### 1C. BLDC / PMSM motor makers (EV, drone, appliance): potential job-work suppliers or competitors

| Company | Product | Scale / capex | Manufacturing approach | Funding / ownership | Source | Label |
|---|---|---|---|---|---|---|
| **Vector Technics** (Hyderabad, Shamshabad; 51 % Zen Technologies) | Drone BLDC motors, ESCs, CFRP props, UAV IC engines (60/170/210 cc), starter-generators | **Capacity 300,000 propulsion units/yr** (6 Jul 2026); 26,000 sq ft; 300+ clients in 10 countries | "**Winds its own motors**, writes its own firmware, lays out its own power electronics, **machines its own components**". "No Chinese parts". Tested on 3 NABL-accredited thrust benchmarks. | Zen bought 51 % (Feb 2025), reportedly for **₹25 cr**. ESTIMATED implied equity value ≈ ₹49 cr (~$5.1 M). | Zen/NSE press release 2026-07-06 https://nsearchives.nseindia.com/corporate/ZENTEC_06072026193453_SEPressRelease06072026.pdf ; ₹25 cr via startupfeed / search summary | VERIFIED (capacity, process) / UNVERIFIED (price) |
| **Sona Comstar** (Gurugram / Chennai) | 2W/3W BLDC traction motors and controllers | Chennai motor plant since Nov 2020; 100k motors in 21 months. Board approved **₹99.7 cr (INR 997 M) to expand from 400k to 600k motors/yr** plus 500k PCBA/yr by FY25. ESTIMATED: ≤ **₹4,985 capex per added annual motor** (the ₹99.7 cr also covers PCBA lines, so the true motor-only figure is lower). Group EV capex ~₹1,200 cr over 3 yrs. | Stator winding and magnet-rotor assembly in-house (repo §4.1) | Listed | autocarpro https://www.autocarpro.in/news/sona-comstar-raises-capex-to-rs-1200-crore-for-ev-biz-116802 ; search summary of company disclosure | UNVERIFIED / ESTIMATED |
| **Lucas TVS** (Puducherry) | EV hub motors and controllers | **~₹30 cr over 1.5 yrs for 3 assembly lines**, ~100 staff, 3,000 sets/month, scaling to 10–15k/month. PLI commitment ₹250 cr. ESTIMATED: ₹30 cr ÷ 36k/yr = **₹8,300 per annual unit** at current output; ₹1,700 at 180k/yr. | Series assembly lines | Private (TVS group) | autocarpro 2022 https://www.autocarpro.in/feature/lucas-tvs-gears-up-for-evs-92241 | UNVERIFIED (2022 data) / ESTIMATED |
| **Atomberg** (Pune, Chakan) | BLDC fans and appliances. **New B2B arm (Atomberg Innovation Pvt Ltd)** makes BLDC motors and controllers for ACs, refrigerators and washing machines (Godrej, Voltas). Says it is exploring drone motors and industrial. | Chakan: **6.6 M units/yr** installed (largest BLDC fan plant in India, per DRHP summary), 283k sq ft; separate Chakan-Varale proprietary-components unit. New **₹150–200 cr, 2 lakh sq ft** B2B motor plant (Mar 2026). | Proprietary components made in-house | VC-backed (Temasek, Steadview; $86 M Series C). IPO planned by 2027. | Inc42 2026-03-17 https://inc42.com/?p=552345 ; ipocentral DRHP review (403) | UNVERIFIED |
| **Chara Technologies** (Bengaluru, Peenya) | **Rare-earth-free synchronous-reluctance** motors and controllers (2W to industrial) | **Series A ₹52 cr ($6 M, Oct 2025)**, led by Arkam, with Exfinity, Kalaari and IIMA Ventures; total ~$11.9 M over 5 rounds. Capacity going **20k → 100k units/yr**. Controller line of 25k/yr (7–30 kW) opened 11 Feb 2026. | Motors and controllers under one roof | > 75 staff | entrepreneur https://india.entrepreneur.com/news-and-trends/chara-technologies-raises-inr-52-cr-to-expand/498240 ; machinist 2026-02 https://machinist.in/2026/02/chara-technologies-inaugurates-motor-controller-manufacturing-facility-in-bengaluru/ | UNVERIFIED |
| **Ultraviolette** (Bengaluru) | E-motorcycles. BMS, motor controllers and software in-house (motor production not described). | **$85 M Series E (Sep 2026)**, co-led by Yali Capital and TDK Ventures; > $135 M total. "BIGGA" plant ≈ ₹800 cr for 2.5–5 lakh vehicles/yr. ESTIMATED: ≈ ₹32k capex per annual vehicle. | — | — | Inc42 https://inc42.com/buzz/exclusive-ultraviolette-to-raise-₹373-cr-as-manufacturing-facility-bigga-takes-shape/ | UNVERIFIED |
| **Weber Drivetrain** (Pune, Chakan) | 0.25–4 kW BLDC hub motors and controllers | ₹35 cr phase 1, "semi-robotic" line (2022). Capacity not stated. | — | — | evreporter 2022-11 https://evreporter.com/weber-drivetrain-launches-automated-manufacturing-facility/ | UNVERIFIED |
| **Pitti Engineering** (Hyderabad) | **Electrical-steel laminations**, motor cores, stator/rotor assemblies, die-cast rotors, machining | 90,000 t/yr sheet-metal capacity → 108,000 t; 648k machine-hours; FY26 target ≈ ₹2,000 cr revenue | India's largest lamination stamper and exporter (progressive dies, press tools in-house) | Listed | DSIJ / NSE PR https://nsearchives.nseindia.com/corporate/PITTIENG_14052026193352_Pressrelease.pdf (not opened) | UNVERIFIED |
| Raphe mPhibr (Noida) | Military drones; in-house autopilot, IC engine, metal and composite processing | **$100 M Series B (Jun 2025)**, led by General Catalyst; **$900 M valuation**; $145 M total | — | — | DealStreetAsia https://media.dealstreetasia.com/stories/raphe-general-catalyst-447075 | UNVERIFIED |
| Polycab (Halol) | BLDC fans | > 9 M fans/yr | — | Listed | tndindia | UNVERIFIED |
| ebm-papst (Chennai) | EC/BLDC fans and motors | New **₹340 cr** plant, ~700 jobs, operational end-2026 | — | German MNC | industrialautomationindia (403) | UNVERIFIED |
| Crompton, Havells, Orient, Bajaj (BLDC fans); Varroc; Simple Energy | not researched in depth (budget) | — | — | — | — | GAP |

### 1D. Industrial servo, gearbox and harmonic-drive makers in India

| Company | India footprint | Relevance | Source | Label |
|---|---|---|---|---|
| Yaskawa India | Bengaluru; production of drives and servo products since **Jan 2011**; robotics division in Gurgaon | Only clear evidence found of a Japanese servo maker producing in India | https://yaskawaindia.in/yaskawa-india.php ; automate.org | UNVERIFIED |
| Delta Electronics India | Krishnagiri TN, 95-acre campus, > 3,800 staff (Sep 2025). **$500 M** India investment; power supplies, DC brushless fans, industrial automation; smart line uses servo systems. | Servo drives sold in India; local servo-motor production **not confirmed** | machinist.in 2025-02 and 2025-09 https://machinist.in/2025/09/delta-electronics-breaks-ground-for-two-new-factories-at-krishnagiri-campus/ | UNVERIFIED |
| Lubi Electronics (Ahmedabad, 1997) | Lists servo motors and drives, AC/DC drives. Whether servos are designed in-house or rebadged is **unclear**. | Possible local servo-drive partner | https://www.lubielectronics.com/automation/drive-motion | UNVERIFIED |
| Siemens, Bosch Rexroth, Mitsubishi, Inovance | Present in the market via sales and distributors. **Local servo-motor manufacturing not confirmed** in this session. | — | search | GAP |
| Bonfiglioli India (Chennai; Pune; Cheyyar TN from 2025) | Gearboxes and planetary drives; > **350,000 gearboxes/gear-motors per yr** (group India); Chennai: 100k/yr (1999 plant) + 75k/yr (2018 plant) | Industrial planetary; **not robot-joint size** | https://bonfiglioli.com/india/en/bonfiglioli_india ; nbmcw | UNVERIFIED |
| Elecon Engineering (Gujarat) | Industrial gears. FY26 consolidated revenue **₹2,366 cr**; gear order book ₹894 cr. | Heavy industrial, not precision robot gears | themachinemaker https://themachinemaker.com/news/elecon-engineering-reports-q4-and-fy26-results/ | UNVERIFIED |
| Shanthi Gears (Murugappa, Coimbatore), Premium Transmission | Industrial gears | Not robot-joint size; FY26 data not found | — | GAP |
| **Harmonic / strain-wave reducers** | **No Indian manufacturer found.** Indian firms only repair or distribute (Synchronics; Rotolinear Bengaluru; Narzo Mumbai). Havells CRI is starting R&D (1A). | Strain-wave reducers would have to be imported or developed from scratch | https://synchronics.co.in/manufacturers/harmonic-drive | UNVERIFIED (absence of evidence) |

Market context:
- **IFR World Robotics 2025:** India installed **9,120 industrial robots in 2024** (+7 %), 6th worldwide. Automotive took
  4,070 (45 %). Operational stock 52,570 (10th). IFR warns of a possible **2026 contraction when PLI programmes run
  out**. VERIFIED (IFR press release, 2025-09-25):
  https://ifr.org/downloads/press_docs/2025-09-25-IFR_press_release_India_in_English.pdf
- ESTIMATED: 9,120 robots × ~6 joints ≈ **55k servo joints/yr** go into industrial robots in India. All of them are
  imported inside foreign-brand robots.
- **India servo motors and drives market ≈ $452 M (2025)**. 70–80 % of servo drivers come from Japan, China and
  Germany. UNVERIFIED (IMARC / Nexdigm market reports via search summary).
- **Foreign robot maker manufacturing in India:** Agile Robots SE (Germany) opened a **₹300 cr** robot-parts plant at
  SIPCOT Irungattukottai, Tamil Nadu, on 2025-06-04, with 300+ jobs. UNVERIFIED (machinist.in)
  https://machinist.in/2025/06/agile-robots-se-inaugurates-new-manufacturing-plant-in-kanchipuram-tamil-nadu/

---

## 2. Manufacturing architectures used in India for motors and gearboxes

### 2.1 Clusters

| Cluster | Specialism | Facts found | Use for an actuator start-up (ESTIMATED judgement) | Source | Label |
|---|---|---|---|---|---|
| **Coimbatore** (TN) | Pumps and motors; foundries. Micro units do casting, machining, welding, grinding and **winding**. | Pump/motor plus foundry turnover ~₹3,200 cr. City makes "nearly 50 %" of India's motors and pumps (induction motors, not PMSM). | Winding labour and stator know-how; ferrite/induction culture, few PMSM skills | https://www.ngmc.org/ngmc_content/uploads/2024/03/4.-3.4.3-2021-2022-UGC-Article-Dr.T.S.Kavitha-1.pdf ; dtnext | UNVERIFIED |
| **Rajkot** (Gujarat) | "Machine-tool capital": lathes, CNC (Jyoti CNC), submersible-pump shafts, castings. Iindepro Dynamics makes UAV BLDC motors (repo §4.1). Manual winders sold at ₹2,800+ (repo `india_motor_materials_raw.md` §6.1). | Unit count not found | Cheap shafts, housings and CNC capacity | search | UNVERIFIED |
| **Pune / Chakan** | Auto components, Bharat Forge, Weber, Atomberg, Quintrans | see 1C | Automotive-grade machining, heat treatment, gear cutting | 1C | UNVERIFIED |
| **Bengaluru (Peenya / Bommasandra)** | Precision machining, aerospace job shops (xTerra machines parts here), Chara (Peenya), ARTPARK | — | Aerospace-grade 5-axis CNC partners; robotics talent | 1A/1C | UNVERIFIED |
| **Hyderabad** | Defence/aero machining, Vector Technics, Pitti laminations, Perceptyne, Svaya | — | Drone-motor winding plus lamination stamping in one city | 1C | UNVERIFIED |
| **Ludhiana** | Fasteners, cycle parts, hand tools | not researched | — | — | GAP |
| **Chennai / Krishnagiri / Hosur** | Bonfiglioli, Delta, Sona Comstar, TVS, ebm-papst, Agile Robots | — | Volume motor and gearbox supply chain | 1C/1D | UNVERIFIED |

### 2.2 Contract manufacturers

| Type | Firms | Facts | Relevance | Source | Label |
|---|---|---|---|---|---|
| EMS (PCBA, box build) | Kaynes (Mysuru), Syrma SGS, SFO Technologies, Dixon | **No public humanoid or robot-actuator programme found** for any of them. All do industrial, auto and aero PCBA. | Driver-board PCBA at volume. Small lots go to Lion Circuits / PCB Power (repo §4.6). | search | UNVERIFIED (absence) |
| Mechanical "manufacturing-as-a-service" | Zetwerk | FY26 revenue ₹15,913 cr (+40 %); 26 plants in 4 countries; **6,979 third-party suppliers**; IPO filed (₹2,600 cr fresh issue); valuation ~$3.1 B | Sourcing of CNC parts and castings through a supplier network. No robotics programme seen. | Inc42 https://inc42.com/features/zetwerks-ipo-test-can-revenue-growth-outrun-its-cash-flow-pressure/ ; upstox | UNVERIFIED |
| Laminations | Pitti Engineering (1C) | Largest Indian stamper | Stamped laminations instead of laser-cut, once the design is frozen and volume > ~10k | 1C | UNVERIFIED |
| Drone-motor job-work | Vector Technics (1C), Reflex, Zepco (repo §4.1) | In-house winding at 300k/yr | Closest analogue for QDD stator and rotor job-work | 1C | VERIFIED (Vector) |

### 2.3 How Indian motor makers do winding, stamping and assembly (what was found)

- **Winding:**
  - Vector Technics winds its own drone motors (VERIFIED).
  - Coimbatore micro units hand- and semi-auto-wind induction motors (UNVERIFIED).
  - Indian winder prices are in `india_motor_materials_raw.md` §6.1: ₹2,800 manual to ₹2 lakh CNC fan winder.
  - Chinese needle winders cost $5k–100k (same file and the China file §3.1).
  - No Indian maker of multi-station BLDC **needle** winders was found (GAP).
- **Stamping:**
  - Volume laminations come from specialists such as Pitti, with in-house press tools (UNVERIFIED).
  - Start-ups use laser or wire-EDM cutting (repo `india_motor_materials_raw.md` §3.2).
- **Magnets:** imported, about 90 % from China (repo China file §4). Vector claims "non-Chinese raw materials" but does
  not name its magnet source.
- **Assembly:**
  - Lucas TVS: 3 assembly lines with ~100 people.
  - Weber: "semi-robotic".
  - Addverb: human-robot collaborative lines.
  - No Indian actuator maker publishes takt, yield or EOL test data (GAP).

### 2.4 Capex benchmarks in India (to set against the China file §3.1)

| Plant | Capex | Capacity | ESTIMATED capex per annual unit | Source label |
|---|---|---|---|---|
| Sona Comstar Chennai expansion (motors + PCBA) | ₹99.7 cr | +200k motors/yr (+500k PCBA) | ≤ ₹4,985 per motor | UNVERIFIED |
| Lucas TVS Puducherry hub motors | ₹30 cr | 36k/yr now; 120–180k/yr planned | ₹8,300 → ₹1,700 | UNVERIFIED (2022) |
| Weber Drivetrain Chakan | ₹35 cr | not stated | — | UNVERIFIED |
| Atomberg B2B motor plant | ₹150–200 cr | not stated (2 lakh sq ft) | — | UNVERIFIED |
| Chara (Peenya) | part of the $6 M Series A | 20k → 100k motors/yr; 25k controllers/yr | upper bound ≈ ₹52 cr ÷ 80k = ₹6,500 (if the whole round went into capex, which it did not) | UNVERIFIED / ESTIMATED |
| Addverb Noida (mobile robots) | ≈ ₹75 cr | 60k robots/yr | ≈ ₹12,500 per robot | VERIFIED (2022 PR) / ESTIMATED |
| Ultraviolette BIGGA (vehicles) | ≈ ₹800 cr | 2.5 lakh/yr | ≈ ₹32,000 per vehicle | UNVERIFIED |
| Agile Robots TN | ₹300 cr | not stated | — | UNVERIFIED |
| China Fulin joint line / Haoneng reducers / Zhongding joints | see China file §3.1 | — | ¥200 per reducer to ¥13.9k per joint | (cross-ref) |

**ESTIMATED synthesis.**
- Indian BLDC/EV motor lines cost roughly **₹1,700–8,300 of capex per unit of annual capacity**. The figure depends on
  utilisation.
- At those rates, a **10k actuators/yr** line would need about ₹0.2–0.8 cr for motor-line capex alone, before gear
  cutting, machining, the encoder/driver line and test benches.
- That fits the China file's ₹0.5–1.5 cr estimate for a minimal ≤ 5k/yr in-house line, provided laminations,
  magnets and gears are bought in.
- Caveat: all inputs are secondary and come from much simpler 2W hub motors.

---

## 3. Capital

### 3A. Government schemes relevant to a robotics or actuator hardware start-up (status as of 2026-10-06)

| Scheme | Size / instrument | Eligibility (key points) | Fit for an actuator start-up (ESTIMATED judgement) | Source | Label |
|---|---|---|---|---|---|
| **RDI Scheme (Research Development & Innovation)**, DST/ANRF | Corpus **₹1 lakh cr** over 6 yrs. Cabinet approval **2025-07-01**; launched 2025-11-03. Two tiers: Special Purpose Fund in ANRF → 2nd-level fund managers. "Long-term concessional loans" at **low or nil interest**; **equity for start-ups**; can contribute to a **Deep-Tech Fund of Funds**. | TRL ≥ 4; India-HQ, majority-Indian-owned, IP registered in India. Covers **up to 50 % of project cost**. Reported terms: **2–4 % interest, up to 15 yrs, collateral-free**. **Robotics is a named sunrise sector.** | **High fit for Series A+ firms.** TDB's 1st round: **22 projects, total cost ₹4,744 cr, RDI support ₹2,192 cr** → ESTIMATED average project ₹216 cr and support ≈ ₹100 cr, i.e. large firms. **TDB paused new applications in Oct 2026** because the first ₹2,000 cr was used up (only ₹500 cr released to TDB by Mar 2026). BIRAC handles biotech. | PIB 2025-07-01 (PRID 2141154, read in Gujarati) https://www.pib.gov.in/PressReleasePage.aspx?PRID=2141154 ; letsdatascience (TDB call 2026-02-04); nextias 2026-08-07; policycircle 2026-07-23; Outlook Business 2026-10 https://www.outlookbusiness.com/news/deep-tech-funding-push-hits-pause-as-1-lakh-cr-rdi-corpus-runs-short | VERIFIED (structure) / UNVERIFIED (terms, round data, pause) |
| **Startup India Fund of Funds 2.0** (DPIIT, run by SIDBI) | **₹10,000 cr**. Cabinet **2026-02-14**; rolled out Apr 2026. Invests through AIFs (VC funds), not directly. Segments: (1) **deep tech**, (2) micro-VCs, (3) **tech-driven innovative manufacturing (Make in India)**, (4) sector-agnostic. Per-segment amounts not published. | DPIIT-recognised start-ups via SEBI-registered AIFs | Indirect: raises the pool of deep-tech and manufacturing VC money | Medianama 2026-04-13 https://www.medianama.com/2026/04/223-govt-rs-10000-cr-fund-of-funds-2-0-deep-tech/ ; pulse2 | UNVERIFIED |
| **Startup India Seed Fund Scheme (SISFS)** | ₹945 cr (2021-22 to 2024-25). **Grant ≤ ₹20 lakh** (PoC/prototype); **≤ ₹50 lakh** as convertible debenture or debt for market entry. Via incubators. | DPIIT-recognised; **incorporated ≤ 2 yrs** at application; ≤ ₹10 lakh of other govt support; ≥ 51 % Indian promoters | Good for a first prototype. Perceptyne got pre-seed money via T-Hub and SISFS (UNVERIFIED). **No 2026 renewal found.** | myscheme.gov.in https://www.myscheme.gov.in/schemes/sisfs-fs ; bankbazaar | UNVERIFIED (official page via summary) |
| **Credit Guarantee Scheme for Startups (CGSS)** | Cover raised to **₹20 cr per borrower** (from ₹10 cr), notified May 2025. Covers 85 % of default ≤ ₹10 cr and 75 % above. Annual fee cut to **1 %** in 27 champion sectors. | DPIIT start-ups borrowing from banks, NBFCs or venture-debt funds | Makes venture debt and term loans easier | Business Standard 2025-05-09 (403); YourStory | UNVERIFIED |
| **SIDBI venture debt** | Rupee term loans up to ₹10 cr (↑ ₹15 cr); ~3-yr tenor incl. moratorium | VC/AIF-backed start-ups with growth traction | Equipment and working capital after a priced round | SIDBI PDF https://www.sidbi.in/head/uploads/other_loans_document/Venture%20Debt%20Financing%20to%20MSMEs.pdf (not opened) | UNVERIFIED |
| **ECMS (Electronics Component Manufacturing Scheme)** (MeitY) | Notified **2025-04-08**, ₹22,919 cr, 6-yr tenure (+1 yr gestation). **Raised to ₹40,000 cr in Budget 2026-27.** 46 applications approved (₹54,567 cr investment) as of the Feb 2026 PIB note. Press reports 106 projects / ₹69,548 cr by Aug 2026. | Segment B "electro-mechanicals" explicitly lists **actuators** (and vibrator motors). Turnover-linked incentive (e.g. 8→4 % over 6 yrs for some lines). **Minimum investment ₹50–500 cr** for Segment B; **₹10 cr for Segment D** (parts and capital goods for components; 25 % capex incentive). | Robot actuators may fit "actuators" in Segment B, but the ₹50 cr+ minimum puts it beyond a seed-stage firm. Segment D (₹10 cr minimum, 25 % capex) could fit encoder or driver sub-parts. **Eligibility of robot joint modules needs MeitY confirmation.** | PIB doc Feb 2026 https://static.pib.gov.in/WriteReadData/specificdocs/documents/2026/feb/doc202623777901.pdf ; India Briefing https://www.india-briefing.com/news/ecms-2025-application-incentives-eligibility-37134.html | VERIFIED (outlay, dates, approvals) / UNVERIFIED (segment detail) |
| **REPM magnet scheme** | ₹7,280 cr | Magnet makers only | Indirect: domestic NdFeB supply. See China file §4. | (cross-ref) | VERIFIED (in repo) |
| **PLI Auto (Component Champion)** | ₹25,938 cr scheme. **8–11 %** of determined sales value (+2 % above ₹1,250 cr cumulative). | Global group revenue **≥ ₹500 cr** and fixed assets ≥ ₹150 cr; first-year DSV growth ≥ 10 % with ≥ ₹25 cr | **Not reachable** for a start-up. Relevant only if partnering with Sona or Lucas TVS (both beneficiaries). | ACMA / MHI FAQ https://www.acma.in/uploads/otherdocmanager/MoHI-FAQs-PLIs_8th%20October%202021.pdf (not opened) ; lakshmisri | UNVERIFIED |
| **PLI Drones** | ₹120 cr over FY22–FY24; 20 % of value addition; min. 40 % domestic value addition. Turnover ≥ ₹2 cr (drones) or ₹50 lakh (components). | 14 beneficiaries (5 drone makers incl. Raphe, ideaForge; 9 component makers) | **Expired (FY24).** No 2026 successor found. | inc42; taxguru | UNVERIFIED |
| **PLI White Goods / ACC** | not researched in detail | Large firms only | Low fit | — | GAP |
| **National Manufacturing Mission** (Budget 2025-26) | Announced Feb 2025: clean-tech focus (solar, batteries, electrolysers), MSMEs, skills incl. "robotics" | Framework only; no robotics money identified | Low direct fit | impriindia; southfirst | UNVERIFIED |
| **NM-ICPS Technology Innovation Hubs** (DST) | ₹3,660 cr for 25 TIHs (Cabinet Dec 2018). **ARTPARK (IISc) got ₹170 cr**; I-Hub Foundation IIT Delhi; IIT Kanpur; etc. | Incubation, grants and pre-seed via each hub | xTerra (I-Hub IIT Delhi) and Twara (ARTPARK) are direct examples | dst.gov.in https://dst.gov.in/node/7600 ; biospectrum | UNVERIFIED |
| **iDEX / ADITI** (MoD) | iDEX/DISC grants **≤ ₹1.5 cr**. **ADITI ≤ ₹25 cr** grant-in-aid (₹750 cr, 2023-24 to 2025-26) for 30 critical technologies. iDEX ~90 % committed; more money requested. | Defence problem statements | Good fit for QDD in UGVs, exoskeletons or RCWS (Bhairav's market) | aviation-defence-universe; raksha-anirveda | UNVERIFIED |
| **MHI CAMRAS / capital-goods scheme** | Twara Robotics is in the MHI CAMRAS accelerator | n/a | Possible grant route | themachinemaker 2025-03 | UNVERIFIED |
| **Karnataka** | Industrial Policy 2025-30: choose **up to 25 % capital subsidy or up to 2.5 % PLI for 7 yrs**. "Deep Tech Decade" ₹600 cr. **ELEVATE grant ≤ ₹50 lakh** (2025: 146 start-ups, ₹38.85 cr). | State-registered start-ups / units | ELEVATE is the most useful state grant found | thesouthfirst 2025-02; Outlook Business; Deccan Herald | UNVERIFIED |
| **Tamil Nadu** | **TANSEED** equity-linked grant ₹10–15 lakh (TANSEED 8.0). New industrial policy announced 2026 (focus: semis, AI, space, shipbuilding). SIPCOT sites (Agile Robots, Genrobotics ₹150 cr MoU). | — | Grant small; strong motor and gear supply chain | entrepreneur; dtnext | UNVERIFIED |
| **Telangana** | State Robotics Framework (2023-05-09): Robo Park, robotics accelerator, TRIC (Telangana Robotics Innovation Centre). No cash incentive quantified. | — | Ecosystem support, Hyderabad cluster | Business Standard 2023 | UNVERIFIED |
| **National Strategy on Robotics** (MeitY) | Draft 2023, revised Feb 2024; proposes a National Robotics Mission and a Robotics Innovation Unit in IndiaAI. **No funded mission found as of Oct 2026.** | — | Watch item | https://innovateindia.mygov.in/national-strategy-on-robotics/ | UNVERIFIED |
| **Budget 2026-27** | Rare-earth corridors (Odisha, Kerala, AP, TN); ECMS → ₹40,000 cr; Hi-Tech Tool Rooms by CPSEs; continued RDI and ANRF funding | — | Magnets, tooling | drishtiias; KPMG | UNVERIFIED |

### 3B. Indian VC funding for robotics and deep-tech hardware, 2024–2026

**Totals**

| Metric | Value | Source | Label |
|---|---|---|---|
| Indian robotics start-ups, 2025 full year | **$52.9 M** | Tracxn via search summary | UNVERIFIED |
| Robotics H1 2024 / H1 2025 / **H1 2026** | $35.8 M / $22.7 M / **$42.1 M** | Tracxn via Mint (2026-06-29) and lapaasvoice https://lapaasvoice.com/indian-robotics-startups-raise-42-1-million-in-h1-2026/ | UNVERIFIED |
| Average robotics cheque | **$1.8 M (2025) → $3.5 M (H1 2026)**, +94.4 %. ESTIMATED: ≈ 29 rounds in 2025, ≈ 12 in H1 2026. | Tracxn via Mint / search summary | UNVERIFIED / ESTIMATED |
| US vs China robotics VC, 2025 | US $5.6 B, China $2.7 B. India < 1 % of US and ~2 % of China. | Mint (Tracxn) via search summary | UNVERIFIED |
| India deep tech, 2025 | $2.3 B (+37 %, Nasscom–Zinnov; AI = 91 %) **or** $2.96 B over 189 deals (another tally). Cumulative 2015–mid-2026: $11.4 B (IVCA Bharat DeepTech Report 2026). | peoplematters; YourStory 2026-08 (403) | UNVERIFIED (sources disagree) |
| All Indian tech start-ups, 2025 | $10.5 B (−17 %, Tracxn) | search summary | UNVERIFIED |

**ESTIMATED reading.**
- Robotics is about **0.5 %** of Indian tech VC ($52.9 M ÷ $10.5 B).
- About 2 % of deep-tech VC goes to robotics. Deep-tech money is overwhelmingly AI software.
- One $20–30 M round (Ati in 2025, Unbox in 2026) moves the robotics annual total by ~50 %.

**Notable rounds (robotics and motor hardware)**

| Company | Round, date | Size | Valuation | Lead / key investors | Label |
|---|---|---|---|---|---|
| Raphe mPhibr (drones) | Series B, Jun 2025 | $100 M | $900 M | General Catalyst | UNVERIFIED |
| Ultraviolette (EV, motor controllers in-house) | Series E, Sep 2026 | $85 M | n/d | Yali Capital, TDK Ventures | UNVERIFIED |
| Unbox Robotics | Series B, Jan 2026 | $28 M | n/d ($25 M in 2024) | ICICI Venture, Redstart | UNVERIFIED |
| Ati Motors | Series B, Jan 2025 | $20 M | n/d | Walden Catalyst, NGP | UNVERIFIED |
| CynLr | Series A, Nov 2024 | $10 M | n/d | Pavestone, Athera; Speciale | UNVERIFIED |
| Chara Technologies (motors) | Series A, Oct 2025 | ₹52 cr ($6 M) | n/d | Arkam; Exfinity, Kalaari, IIMA Ventures | UNVERIFIED |
| Anscer Robotics | Series A, 2026 | ₹45 cr (~$4.7 M) | n/d | IAN Group | UNVERIFIED |
| **General Autonomy (humanoid / quadruped)** | Seed, May 2026 | ₹32 cr ($3.3 M) | **₹280 cr ($29 M)** | Elevation, India Quotient | UNVERIFIED |
| General Autonomy | Pre-seed, Nov 2023 | ₹25 cr | n/d | India Quotient, Elevation | UNVERIFIED |
| Alphadroid | 2026 | $3.8 M | n/d | n/d | UNVERIFIED |
| **Perceptyne (semi-humanoid, in-house actuators)** | Seed, Oct 2024 | $3 M | n/d. A $50 M valuation term sheet is claimed but unconfirmed. | Endiya, Yali; Whiteboard | UNVERIFIED |
| Peer Robotics | Seed | $2.3 M | n/d | Kalaari | UNVERIFIED |
| Armatrix | Pre-seed/seed, 2025–26 | $2.1 M | n/d | pi Ventures | UNVERIFIED |
| Anscer Robotics | Seed, Feb 2025 | $2 M | n/d | Info Edge Ventures | UNVERIFIED |
| Integra Robotics | Pre-Series A, Jun 2026 | $1.12 M | n/d | Finvolve, India Accelerator | UNVERIFIED |
| Quintrans (linear actuators) | Pre-seed, Dec 2025 | $0.75 M | n/d | Capital-A | UNVERIFIED |
| iHub Robotics (humanoid) | Pre-seed, 2024/25 | ₹4.3–4.5 cr (~$0.5 M) | n/d | US angels | UNVERIFIED |
| Bhairav Robotics (QDD) | Strategic, Feb 2025 | ~₹4 cr for 45.33 % | ESTIMATED ~₹8.8 cr post | Zen Technologies | UNVERIFIED / ESTIMATED |
| Vector Technics (drone motors) | Strategic, Feb 2025 | ~₹25 cr for 51 % | ESTIMATED ~₹49 cr | Zen Technologies | UNVERIFIED / ESTIMATED |
| xTerra Robotics (QDD) | Grants only | — | — | IIT Kanpur / IIT Delhi incubators | UNVERIFIED |

**Active investors in Indian robotics and deep-tech hardware (evidence found in this session)**

| Investor | Fund size / cheque | Robotics or hardware deals seen | Label |
|---|---|---|---|
| Yali Capital | Deep-tech Fund I **₹893 cr ($103 M)**, closed Jul 2025 | Perceptyne (seed co-lead), Ultraviolette (Series E co-lead) | UNVERIFIED |
| Speciale Invest | Fund II ₹300 cr, cheques **$0.75–1 M**; Growth Fund II target ₹1,400 cr | CynLr | UNVERIFIED |
| Endiya Partners | n/d | Perceptyne | UNVERIFIED |
| pi Ventures | n/d | Armatrix | UNVERIFIED |
| Kalaari Capital | n/d | Peer Robotics, Chara | UNVERIFIED |
| Exfinity Venture Partners | n/d | Ati Motors, Chara | UNVERIFIED |
| Blume Ventures | n/d | Ati Motors | UNVERIFIED |
| Elevation Capital, India Quotient | n/d | General Autonomy | UNVERIFIED |
| Info Edge / Redstart | n/d | CynLr, Unbox, Anscer | UNVERIFIED |
| Peak XV | n/d | Genrobotics | UNVERIFIED |
| Accel | $550 M new India fund (2026) | Haber (water-treatment AI, $44 M Series C): **no actuator or robotics hardware deal found** | UNVERIFIED |
| Lightspeed India | "India Ascends 2026" programme: $200k–3 M cheques for R&D-first founders under 25 (robotics included) | — | UNVERIFIED |
| Stellaris | — | **none found** | GAP |
| Arkam, Capital-A, IIMA Ventures, Athera, Pavestone, Walden Catalyst, NGP, General Catalyst, TDK Ventures, ICICI Venture | see the rounds table | | UNVERIFIED |
| Strategic acquirers | Zen Technologies (Vector, Bhairav); Reliance (Addverb); Zoho (Genrobotics, Ultraviolette) | | UNVERIFIED |

**ESTIMATED: typical Indian hardware round sizes, 2024–26** (from the deals above).
- Pre-seed (grants plus angels): **₹2–8 cr ($0.2–0.8 M)**.
- Seed: **$2–3.5 M (₹20–32 cr)**. Humanoid-labelled seed reached a **₹280 cr ($29 M) post-money** valuation (General
  Autonomy) while still pre-revenue.
- Series A: **$5–10 M**.
- Series B: **$20–30 M**.
- Strategic stakes in component makers are priced far lower: **₹9–50 cr** implied for Bhairav and Vector.
- Indian rounds run about 5–10× smaller than Chinese actuator-maker rounds (see China file §1).

---

## 4. Indian humanoid efforts and their actuators (summary)

| Effort | Form | Actuators used (as disclosed) | Label |
|---|---|---|---|
| Addverb Elixis-W / Elixis | Wheeled (67 DOF) / bipedal | "High-speed BLDC actuators + planetary gearboxes". Supplier or in-house **not disclosed**. | UNVERIFIED |
| Perceptyne PR-34D | Dual-arm semi-humanoid | **In-house** actuators (claim) | UNVERIFIED |
| General Autonomy Atom 01 / Param | Biped humanoid / quadruped | **Imported** "specialised actuators" (origin not stated; probably Chinese QDDs) | UNVERIFIED |
| xTerra | Quadrupeds, humanoid in development | **In-house QDD** (A2, 12 N·m); parts machined in Bengaluru | UNVERIFIED / VERIFIED (spec) |
| Bhairav Robotics | Quadruped "Shvana", UGVs | **In-house "Prabal" QDD** | UNVERIFIED |
| Svaya Robotics | Cobot, quadruped, exoskeleton, humanoid (claimed) | In-house (vertically integrated claim) | UNVERIFIED |
| iHub Robotics Tara / Daksha | Service and industrial humanoid | Not disclosed; ~30 % of parts imported | UNVERIFIED |
| DRDO R&DE | Military humanoid (upper and lower body prototypes) | Not disclosed | UNVERIFIED |
| Galgotias University "Orion" (India AI Impact Summit, 2026-02-18) | Quadruped shown as home-built | Rebadged **Unitree Go2**; stall vacated | UNVERIFIED |

**ESTIMATED reading.**
- Every Indian humanoid or quadruped effort found either designs its own QDDs at tiny volume (xTerra, Bhairav,
  Perceptyne, Svaya) or imports them (General Autonomy, very probably Addverb's planetary BLDC joints).
- No Indian actuator maker publishes volume, cost or price except xTerra (₹94,400 for 12 N·m, ≈ 5.7–11.7× RobStride;
  see China file §4.2).
- No Indian harmonic-reducer maker exists.
- Havells' job ad is the only sign of a large Indian manufacturer moving into humanoid actuators.

---

## 5. Key takeaways (ESTIMATED synthesis; cite the rows above)

1. **Incumbents in India are tiny.** The QDD makers are 15-person grant-funded teams (xTerra) or ~₹9 cr strategic
   subsidiaries (Bhairav). The nearest scaled analogue is Vector Technics: 300k drone-propulsion units/yr with in-house
   winding (VERIFIED). It shows Indian in-house BLDC winding at volume is feasible.
2. **Demand side.**
   - About 9.1k industrial robots/yr are installed, all with imported servos (IFR VERIFIED).
   - Humanoid targets are small: Addverb plans 3,000 humanoids by 2030.
   - About 10 domestic robot start-ups build legged or dual-arm robots. They are the first customers, but each buys only
     hundreds to low thousands of joints per year.
3. **Supply chain.**
   - Strong: laminations (Pitti), BLDC/EV motor lines (Sona, Lucas TVS, Atomberg), CNC clusters (Rajkot, Peenya,
     Pune), industrial gearboxes (Bonfiglioli).
   - Missing: precision small reducers, harmonic drives, NdFeB magnets (REPM scheme not yet awarded) and Indian-made
     multi-station needle winders.
4. **Capex.** Indian BLDC motor lines run at about ₹1,700–8,300 of capex per unit of annual capacity. A 10k/yr actuator
   line is therefore a ₹1–3 cr problem (motor line plus machining, gear sourcing and test). The capital constraint is
   working capital and NRE (non-recurring engineering), not plant.
5. **Capital.**
   - Indian robotics VC is small: $52.9 M in 2025; average cheque $1.8–3.5 M.
   - It is concentrated among a handful of deep-tech funds: Yali, Speciale, Endiya, pi, Kalaari, Exfinity, Elevation,
     India Quotient, Info Edge.
   - A humanoid label can win a ₹280 cr seed valuation.
   - Non-dilutive routes by stage:
     - Prototype: SISFS (≤ ₹20 lakh grant + ₹50 lakh debt), Karnataka ELEVATE (≤ ₹50 lakh), TIH incubator grants,
       iDEX (≤ ₹1.5 cr), ADITI (≤ ₹25 cr) for defence uses.
     - Scale-up: RDI loans (50 % of project, 2–4 %, 15 yrs, TRL ≥ 4), but the first tranche is exhausted and paused in
       Oct 2026. Also CGSS-backed debt (≤ ₹20 cr) and SIDBI venture debt (≤ ₹10–15 cr).
     - Plant: ECMS lists "actuators", but the ₹50 cr+ minimum investment suits a later-stage plant.
   - The PLI auto and drone schemes are unreachable (thresholds) or expired.

---

## 6. Gaps and caveats (honest list)

- Not obtained:
  - MCA filings (revenue and paid-up capital) for xTerra, Bhairav, Perceptyne, General Autonomy, Svaya.
  - Tracxn or Inc42 primary pages (403).
  - All valuations except General Autonomy (₹280 cr) and Raphe ($900 M) are undisclosed.
- **Torque and price data:** only xTerra publishes them. Bhairav, Perceptyne, Svaya and Addverb publish no torque,
  price or volume.
- **Addverb humanoid actuators:** whether they are made in-house is unknown. The humanoid.guide page is self-marked
  "Not Verified".
- **Conflicts:**
  - Perceptyne's 2026 round ($3.6 M / ₹30 cr / a $50 M Premji term sheet) is unconfirmed.
  - General Autonomy is called "bootstrapped, 5 people" by one outlet against ₹57 cr raised in others.
  - iHub's capacity is 10–20/month vs 300/month.
  - iHub's funding is ₹4.3 cr vs ₹4.5 cr.
  - Deep-tech 2025 totals differ ($2.3 B vs $2.96 B).
- Industrial servo manufacturing in India: only Yaskawa (2011) was confirmed. Siemens, Bosch Rexroth, Mitsubishi,
  Delta (servo motors specifically), Elmo and Inovance local production were not confirmed.
- Not researched for budget reasons: Ottonomy, Mukunda Foods, Crompton/Havells/Varroc BLDC lines, Shanthi Gears and
  Premium Transmission financials, Ludhiana cluster, Bharat Forge or Kalyani e-motor capex, Dixon, Kaynes and SFO
  motor-controller programmes, Stellaris robotics deals.
- Scheme terms: RDI, CGSS, SISFS and FoF 2.0 terms come from secondary summaries. Only the RDI Cabinet note (PIB) and
  the ECMS PIB backgrounder were read in the original. Check the official guidelines before relying on rates or caps.
- Capex-per-unit figures (§2.4) are crude: different products, unknown utilisation, mixed scopes (PCBA included).
