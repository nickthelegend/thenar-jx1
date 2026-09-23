# JX1 reference-humanoid study: raw data

**File:** `research/raw/reference_robots_raw.md`. **Prepared:** 2026-09-24.

**Purpose.** This file informs JX1 (1.1–1.3 m, 20–24 actuated DOF, 6-DOF legs, lowest-cost build in India). It covers dimensions, DOF layout and actuator torque/speed requirements.

**Scope.** 29 humanoid models from 17 makers and labs:
- **Unitree:** G1 (all variants), H1, H1-2, R1, H2.
- **Berkeley:** Berkeley Humanoid Lite, Berkeley Humanoid (2024).
- **Small and servo-based:** ToddlerBot 1.0 and 2.0, Poppy Humanoid, Robotis OP3, Westwood BRUCE.
- **Booster:** T1, K1.
- **K-Scale:** K-Bot, Zeroth-01 / Z-Bot.
- **Fourier / Noetix:** Fourier N1, Noetix N2, Noetix Bumi.
- **Menlo Research:** Asimov v0 and Asimov 1.
- **Others:** EngineAI PM01 and SA01, PNDbotics Adam Lite, Duke Humanoid v1, AgiBot X1 and X2, HighTorque Mini Pi / Pi+ / Hi, Roboparty Roboto Origin (ATOM 01).

**How it was built.** 43 official model files (URDF/MJCF/xacro) plus actuator/config files were parsed, covering about 30 robot variants. The rest comes from official product pages, docs, papers and GitHub repos.

**Two rules:**
- Every number carries a label: **VERIFIED**, **ESTIMATED** or **UNVERIFIED** (defined in §0), plus a source URL.
- Nothing was invented. "n/p" = not published or not found.

**Contents**
- 0. How to read this file (labels and method)
- 1. Headline numbers for JX1
- (a) Robot-by-robot sections A1–A14
- (b) Comparison table
- (c) Leg segment lengths normalised by height
- (d) Torque/speed normalised by M·g·L, scaled to JX1
- (e) Design lessons
- (f) Sources

## 0. How to read this file

**Labels.** Every number carries one label:

- **VERIFIED**: read today (2026-09-24) on an official or primary source: a manufacturer page or doc, the official GitHub repo or model file, or the authors' paper.
- **ESTIMATED**: derived by us. The derivation is shown or referenced (usually "FK of file values", see §0.2).
- **UNVERIFIED**: a secondary source (press, distributor, forum or wiki), or an official claim we could not re-open today.

**Model-file extraction (§0.2).** Each model file was downloaded as text from `raw.githubusercontent.com` and parsed with a purpose-written Python/lxml parser. The parser scripts live in the scratchpad, not the repo: `urdfkin.py`, `leg.py`, `extract_all.py`. For URDF it composes every `<joint><origin xyz rpy>` (URDF fixed-axis RPY, R = Rz·Ry·Rx) from the root link to the foot. For MJCF it composes `<body pos quat|euler>`, honouring `<compiler angle>` and `<default>` classes. All joints are at **q = 0**, and all values are in the root-link (pelvis/base/trunk) frame, with x forward, y left, z up.

Definitions used throughout:

- **thigh** = vertical distance (Δz) between the hip-pitch and knee joint origins. The 3-D distance is also given.
- **shin** = Δz between the knee and ankle-pitch joint origins.
- **L = thigh + shin**, which is the "leg length" used for normalisation.
- **ankle-pitch→sole** = z(ankle-pitch origin) − lowest z of the foot's *primitive* collision geoms (box/sphere/capsule/cylinder). Where the foot collision is a binary mesh (STL) this number is **not derivable**; we did not download binary meshes.
- **Lateral spacing.** Only axes that are *not* parallel to y have a meaningful lateral (y) position. We therefore quote the hip-yaw axis |y|, the hip-roll joint |y| and the ankle-roll joint |y| (≈ foot centre). A pitch joint's y-origin is arbitrary along its own axis.
- **mass** = Σ `<mass>` / `<inertial mass>` of all links (includes battery if modelled). **one-leg mass** = Σ over the subtree of the first hip link. **shank+foot** = subtree of the knee child link.
- **effort/velocity limits** = `<limit effort velocity>` (URDF) or `actuatorfrcrange`/`ctrlrange`/`forcerange` (MJCF). These are what the vendor put in the model. They are usually peak (not continuous) torque at the joint and are sometimes deliberately de-rated (Berkeley Humanoid README says so explicitly) or placeholders (ToddlerBot URDF uses 100/100).
- **Parallel-linkage ankles** (G1, R1, H1-2, H2, T1, K1, AgiBot X1, Adam Lite, Asimov, Roboto Origin; N1 per its brochure render) are modelled in the serial URDFs as ankle-pitch + ankle-roll joints. Their "effort" values are serial-equivalent joint torques, not motor torques.

## 1. Headline numbers for JX1

Details and sources for every number are in §(a)–(e).

### 1.1 Closest-size references, 1.14–1.40 m (official height / mass)

| robot | height | mass | leg DOF | note |
|---|---|---|---|---|
| Menlo **Asimov 1** | **1.20 m** | 35 kg | 6 | open source, DIY kit US$20k |
| Unitree **R1** | 1.23 m | 27–29 kg | 6 | US$4.9–5.9k |
| Booster **T1** | 1.18 m | 30 kg | 6 | — |
| Noetix N2 | 1.14 m | ≈30 kg | 5 | — |
| Fourier N1 | 1.245–1.30 m | 38–39 kg | 6 | — |
| AgiBot X1 | 1.30 m | 33 kg | 6 | — |
| AgiBot X2 | 1.31 m | ≈35 kg | 6 | — |
| **G1** | 1.32 m | 35 kg | 6 | — |
| PM01 | 1.38–1.40 m | 40–44 kg | 6 | — |
| K-Bot | 1.40 m | 34 kg | 5 | — |
| Roboto Origin | 1.25 m* | 34 kg* | 6 | fully open, BOM CNY 49.7k |

\* Secondary source (UNVERIFIED).

### 1.2 Leg geometry for a 1.2 m robot (ESTIMATED)

Values are the median (p25–p75) over 11 robots of 1.14–1.40 m, taken from the model files and scaled to H = 1.20 m.

| quantity | JX1 value |
|---|---|
| thigh (hip-pitch → knee) | **0.28 m** (0.24–0.29) |
| shin (knee → ankle-pitch) | **0.27 m** (0.265–0.29) |
| leg L = thigh + shin | **0.54 m** (0.53–0.58), i.e. 0.45 H |
| thigh : shin | ≈ 0.93 (0.86–1.11) |
| ankle-pitch → sole | ≈ **0.05 m** (G1 0.053, T1 0.042–0.055, Asimov 1 0.044, R1 0.055, K-Bot 0.058) |
| hip-pitch → sole | ≈ **0.60–0.63 m** |
| foot | ≈ 0.18–0.22 × 0.06–0.10 m (G1-MJX effective sole 0.18 × 0.06; T1 0.225 × 0.10; K1 0.18 × 0.07) |
| foot-centre spacing | ≈ **0.19–0.22 m** (G1 0.237, T1 0.212, Asimov 1 0.215, K1 0.192) |

### 1.3 Model-file leg dimensions of the four robots called out in the brief (ESTIMATED from VERIFIED files)

- **Unitree G1 (rev 1.0 URDF).** Pitch-roll-yaw hip (roll and yaw axes pitched 10°).
  - Thigh 0.337 m, shin 0.300 m, ankle-pitch→sole 0.053 m, hip-pitch→sole 0.689 m, feet 0.237 m apart. Σ mass 33.3 kg; one leg 7.19 kg.
  - Joint limits (sim/URDF): hip pitch 88 N·m @ 32 rad/s, hip roll 139 @ 20, hip yaw 88 @ 32, knee 139 @ 20, ankle 35 @ 30 (29-DOF sim 50).
  - Official knee: 90 N·m (G1) / 120 N·m (EDU).
  - Motors N7520-14.3 / N7520-22.5 (two-stage planetary PMSM) and N5020-16 (ankle, parallel A/B).
- **Berkeley Humanoid Lite (URDF).** Hip roll → yaw (both ±45° tilted) → pitch; serial ankle.
  - Thigh 0.150 m, shin 0.160 m, ankle-pitch→sole 0.100 m, hip-pitch→sole 0.410 m. Σ 16.33 kg (official 16 kg, 0.8 m).
  - All joints 20 N·m / 15 rad/s in the URDF. Leg torque is capped at 6 N·m in firmware and in the Isaac training config (10 rad/s in sim).
  - Actuators: 3-D-printed cycloidal 15:1 on MAD M6C12 / 5010 BLDC. BOM **US$4,312** (US) / **$3,236** (China).
- **ToddlerBot 2.0 (URDF + `robot.yml`).** Pitch-roll-yaw hip; serial ankle.
  - Thigh 0.1015 m, shin 0.110 m, ankle→sole 0.039 m. Σ 3.50 kg (official 0.56 m, 3.4 kg).
  - Dynamixel XM430-W210 knee/ankle (sys-ID τmax 1.61–1.94 N·m, 7.6 rad/s); 2XC430 or XM430-W350 hips.
  - BOM ≈ US$5.7–7.3k.
- **K-Scale K-Bot (URDF + collision MJCF).** Pitch-roll-yaw hip; **5-DOF leg with a pitch-only ankle**.
  - Thigh 0.385 m, shin 0.290 m, ankle→sole 0.058 m, hip-pitch→sole 0.733 m. Σ 36.7 kg (official 1.4 m, 34 kg).
  - Robstride RS04 120 N·m @ 17.5 rad/s (hip pitch, knee); RS03 60 N·m @ 18.8 rad/s (hip roll/yaw); RS02 17 N·m @ 37.7 rad/s (ankle).

### 1.4 Leg torque targets at peak, scaled to JX1 (ESTIMATED)

Scaled from 15 modern RL-walking robots by τ* = τ/(M·g·L), with L = 0.54 m.

| JX1 mass | knee | hip pitch | hip roll | hip yaw | ankle pitch | ankle roll |
|---|---|---|---|---|---|---|
| 30 kg | ≈ 86–113 N·m | ≈ 93–104 | ≈ 78–94 | ≈ 67–76 | ≈ 39–64 | ≈ 32–51 |
| 25 kg | ≈ 71–94 N·m | ≈ 77–86 | ≈ 65–79 | ≈ 56–63 | ≈ 33–53 | ≈ 26–43 |

Ranges are median–p75 across the 15 robots. The ankle values are serial-equivalent; each motor of a two-motor parallel ankle needs roughly half, depending on crank/anchor geometry.

**Speed:** median ω·√(L/g) ≈ 3, so **≈ 13 rad/s** at the joint. Upper quartile ≈ 20 rad/s. G1 is at 20–32 rad/s.

### 1.5 Architecture consensus

- Pitch → roll → yaw hip: 15 of the 27 robots here, including every 2024–26 commercial design except H1-2, N2 and SA01.
- Knee actuated at the knee (direct drive). Flexion ≥ 135° on the agile robots (G1 165°, K-Bot 155°, R1 139°, X2 138°); 123–133° on Booster T1/K1.
- Two-motor parallel (rod-driven) ankle with both motors high in the shank (G1, R1, T1, K1, X1, Asimov, Adam, H1-2, H2).
- 48 V-class (13S) quick-swap battery of ≈ 200–500 Wh carried in the trunk (R1: 33 V, 199 Wh).
- Per-limb CAN (or EtherCAT) buses with daisy-chained power + CAN harnesses.
- Low-ratio planetary QDD actuators (7–25:1).

### 1.6 Cost anchors

| item | price | label |
|---|---|---|
| Unitree R1 | US$4,900–5,900 | VERIFIED |
| Unitree G1 | US$13.5k | VERIFIED |
| Noetix Bumi | CNY 9,998 | VERIFIED (official news repost) |
| HighTorque Mini Pi | US$3,500 | VERIFIED |
| HighTorque Mini Pi+ | US$5,500 | VERIFIED |
| Roboto Origin BOM | CNY 49,713, of which actuators 63 % (9 × DM10010L at CNY 1,989; 14 × DM4340P at CNY 949) | VERIFIED; share ESTIMATED |
| BHL BOM | US$4,312 | VERIFIED |
| K-Bot dev kit | US$9–11k | VERIFIED (archived) |
| Asimov 1 DIY kit | US$20k | VERIFIED |
| Robstride list prices | RS04 US$255, RS03 US$225, RS02 US$145 | VERIFIED |

## (a) Robot-by-robot sections

### A1. Unitree G1 (G1 / G1 EDU / 23- and 29-DOF / G1+, Unitree Robotics, China)

Primary sources (read 2026-09-24):

- Product page: https://www.unitree.com/g1
- Chinese product page: https://www.unitree.com/cn/g1
- G1+ page: https://www.unitree.com/G1pl
- Shop: https://shop.unitree.com/products/unitree-g1
- Developer docs: https://support.unitree.com/home/en/G1_developer — pages `about_G1`, `joint_motor_sequence`, `basic_motion_routine`, `basic_services_interface`. The raw docs come from the JSON API https://robot-api.unitree.com/doc?space=G1_developer&locale=en.
- GitHub: https://github.com/unitreerobotics/unitree_ros (`robots/g1_description`), https://github.com/unitreerobotics/unitree_rl_lab (`assets/robots/unitree.py`, `unitree_actuators.py`), https://github.com/unitreerobotics/unitree_mujoco, https://github.com/unitreerobotics/unitree_rl_gym.

| Field | Value | Label | Source / reference |
|---|---|---|---|
| Height (stand / folded) | **1320** × 450 × 200 mm standing; 690 × 450 × 300 mm folded. It was 1270 mm on the May-2024 page | VERIFIED / VERIFIED-archive | g1 page, row "Height, Width and Thickness"; Wayback 20240513184245 |
| Mass (with battery) | **≈35 kg** (G1); "≈35 kg+" (EDU) | VERIFIED | g1 page, row "Weight (With Battery)" |
| DOF | G1 **23**; EDU 23–43. 23 = legs 6×2 + waist 1 + arms 5×2. 29 = legs 12 + waist 3 + arms 7×2. With Dex3-1 hands: +7×2 | VERIFIED | g1 page; unitree_ros README table |
| Leg order (SDK 0–5) | **hip pitch → hip roll → hip yaw → knee → ankle pitch → ankle roll** | VERIFIED | `joint_motor_sequence` |
| "Calf + thigh length" | **0.6 m** (no split published) | VERIFIED | g1 page; `about_G1` |
| Leg geometry from model | Thigh 0.3366 m + shin 0.300 m (hip-pitch→ankle-pitch 0.637 m; hip-**roll**→ankle-pitch 0.606 m ≈ the official 0.6 m) | ESTIMATED | model §below |
| Knee max torque | **90 N·m (G1) / 120 N·m (EDU)**. The footnote defines it as the max of the largest joint motor | VERIFIED | g1 page, row "Maximum Torque of Knee Joint" |
| Joint motors | Low-inertia high-speed internal-rotor PMSM, hollow shaft, dual encoder, crossed-roller output bearing | VERIFIED | `about_G1` "Joint motor" |
| Motor-to-joint map (rev 1.0) | **N7520-14.3**: hip pitch, hip yaw, waist yaw. **N7520-22.5**: hip roll, knee. **N5020-16**: shoulders, elbow, wrist roll, and in the 29-DOF config the ankles ("N5020-16-parallel") and waist roll/pitch. **W4010-25**: wrist pitch/yaw | VERIFIED | unitree_rl_lab `unitree.py` |
| Torque–speed models (output) | N7520-14.3: 71 / 83.3 N·m (Y1/Y2), 22.63 / 35.52 rad/s (X1/X2), rotor J 0.489e-4 kg·m². N7520-22.5: 111 / 131 N·m, 14.5 / 22.7 rad/s. N5020-16: 24.8 / 31.9 N·m, 30.86 / 40.13 rad/s. N5010-16: 9.5 / 17 N·m. W4010-25: 4.8 / 8.6 N·m | VERIFIED (simulation actuator models) | `unitree_actuators.py` |
| Reducers | Two-stage **planetary**: 14.3 = 4.5 × (48/22 + 1); 22.5 = 4.5 × 5; 16 = (46/18 + 1)(56/16 + 1) | VERIFIED (formulas) / ESTIMATED (type) | `unitree_actuators.py` |
| Hip ratio by `mode_machine` | {pitch, roll} = {14.3, 22.5} for rev 1.0 and modes 13/14; {22.5, 22.5} for modes 10–12, 15, 16, 18; {14.3, 14.5} for deprecated 1–3 | VERIFIED | g1_description README |
| Sim limits (rl_lab) | N7520-14.3 88 N·m / 32 rad/s; N7520-22.5 139 / 20; N5020-16 25 / 37; W4010-25 5 / 22. Ankle 35 N·m / 30 rad/s (23-DOF) or 50 / 37 (29-DOF mimic, armature 2 × N5020) | VERIFIED | `unitree.py` |
| Ankle mechanism | **Parallel**: motors A and B active, pitch and roll passive. PR mode (default, matches the URDF) or AB mode. Rods along the shank are visible in photos (ESTIMATED) | VERIFIED | `basic_motion_routine` |
| Waist (29-DOF) | Roll and pitch also a parallel A/B pair; can be locked with a waist fastener | VERIFIED | `basic_motion_routine`; `waist_fastener` |
| Battery | **13-string Li-ion, 9000 mAh**, quick release; charger 54 V 5 A. ≈46.8 V nominal → **≈421 Wh** (ESTIMATED 13 × 3.6 V × 9 Ah). Spare pack US$700 | VERIFIED / ESTIMATED | g1 page rows "Power Supply", "Smart Battery", "Charger"; shop |
| Runtime | ≈2 h | VERIFIED | row "Battery Life" |
| Compute | Motion control: "8-core high-performance CPU" (model undisclosed). EDU PC2: **Jetson Orin NX 16 GB**, 2 TB. Optional Thor (T5000) backpack | VERIFIED | `about_G1` |
| Sensors | Livox MID-360 lidar, RealSense D435i, 4-mic array, 5 W speaker, Wi-Fi 6 / BT 5.2 | VERIFIED | `about_G1`; g1 page |
| Speed | 2 m/s (SDK speed modes up to 3.0 m/s) | VERIFIED | g1 page image; `sport_services_interface` |
| Materials | Base G1 not published. G1-Comp: aluminium alloy + high-strength engineering plastics | VERIFIED (Comp only) | robocup page |
| Price | **US$13.5k** (shop; launched at US$16k, cut between 2025-11 and 2025-12). CNY 85,000 incl. tax (launch 99,000). G1+ US$15k / CNY 95,000. G1 Pro US$21,500. EDU "contact sales" | VERIFIED / VERIFIED-archive | g1 pages; shop; Wayback |
| Open source | URDF/MJCF (BSD-3), SDK2, rl_gym, rl_lab (Apache-2.0); STEP zips via docs; USD on Hugging Face | VERIFIED | GitHub; docs |

Conflicts:

- Knee torque: 90 or 120 N·m (spec page) vs 111–131 N·m (torque-speed model) vs 139 N·m (URDF/sim).
- Height: 1270 mm (2024) vs 1320 mm (now).
- Hip pitch range: website "±154°" vs docs −145°…+165°.

**Model-file extraction (G1).** Source: `unitreerobotics/unitree_ros` → `robots/g1_description/`. Primary file: https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/g1_description/g1_29dof_rev_1_0.urdf. Variants: `g1_23dof_rev_1_0.urdf`, `g1_23dof_mode_10.urdf`, `g1_29dof_mode_15.urdf` and deprecated `g1_23dof.urdf`, all in the same folder.

Raw left-leg joint origins in the URDF (parent frame, metres/rad), all VERIFIED:

| joint | origin xyz | rpy | axis | limit lower…upper (rad) | effort N·m | vel rad/s |
|---|---|---|---|---|---|---|
| left_hip_pitch | (0, 0.064452, −0.1027) | 0 | y | −2.5307…2.8798 | 88 | 32 |
| left_hip_roll | (0, 0.052, −0.030465) | (0, −0.1749, 0) | x | −0.5236…2.9671 | 139 | 20 |
| left_hip_yaw | (0.025001, 0, −0.12412) | 0 | z | −2.7576…2.7576 | 88 | 32 |
| left_knee | (−0.078273, 0.0021489, −0.17734) | (0, +0.1749, 0) | y | −0.087267…2.8798 | 139 | 20 |
| left_ankle_pitch | (0, −9.4e-5, −0.30001) | 0 | y | −0.87267…0.5236 | 35 | 30 |
| left_ankle_roll | (0, 0, −0.017558) | 0 | x | −0.2618…0.2618 | 35 | 30 |

Foot contact in the ankle-roll link: four spheres, r = 0.005 m, at (−0.05, ±0.025, −0.03) and (0.12, ±0.03, −0.03). VERIFIED.

Derived by FK at q = 0 (ESTIMATED from VERIFIED file values):

- **Hip joint order: pitch → roll → yaw** (pitch proximal, on the pelvis). The roll and yaw axes are pitched by 10.0° (rpy −0.1749 rad). The knee joint's +0.1749 rad returns the shank to vertical.
- Hip-pitch origin at z = −0.1027 m below the pelvis origin. Knee at z = −0.4393 m. **Thigh = 0.3366 m** (vertical). The 3-D distance is 0.341 m because the knee sits 0.054 m further out laterally.
- **Shin = 0.3000 m** (knee→ankle-pitch). Ankle-pitch→ankle-roll = 0.0176 m. Ankle-roll axis→sole = 0.030 + 0.005 = 0.035 m. **Ankle-pitch→sole = 0.0526 m.**
- **Hip-pitch→sole = 0.689 m. Pelvis origin→sole (straight legs) = 0.792 m.** unitree_rl_gym uses `init_state.pos z = 0.8` and `base_height_target = 0.78`, which is consistent.
- Lateral: hip-roll/yaw axes at y = ±0.1165 m. Ankle-roll axis at ±0.1185 m, so **foot-centre spacing ≈ 0.237 m**.
- Foot contact points span 0.17 m (x) by 0.05–0.06 m (y) between sphere centres (0.18 × 0.07 m including radius), from 0.055 m behind to 0.125 m ahead of the ankle axis. These are contact points only; the real sole outline is in the STL mesh, which we did not download.
- **Σ link masses:**
  - 33.34 kg for the 29-DOF rev 1.0 file (with two 0.17 kg rubber hands); 32.11 kg for the 23-DOF rev 1.0.
  - 33.74 kg for the 29-DOF mode 15; 34.13 kg for the deprecated 23-DOF.
  - The unitree_mujoco `g1_29dof.xml` sums to 35.11 kg.
- **Leg link masses (per side):** hip-pitch link 1.35 kg, hip-roll link 1.52 kg, hip-yaw link (thigh) 1.702 kg, knee link (shank, holds both ankle motors) 1.932 kg, ankle-pitch cross 0.074 kg, foot 0.608 kg.
  - One leg = 7.19 kg (both legs = 43 % of total). Shank+foot = 2.61 kg (7.8 %).
  - Torso link = 6.78 kg; pelvis = 3.81 kg.
- Whole-body COM at q = 0: 0.703 m above the sole, 0.020 m forward of the pelvis origin, i.e. about hip height.
- Other joint limits (29-DOF rev 1.0), VERIFIED:
  - Waist yaw 88 N·m / 32 rad/s (±150°); waist roll and pitch 35 N·m / 30 rad/s (±29.8°).
  - Shoulder pitch/roll/yaw, elbow and wrist roll 25 N·m / 37 rad/s; wrist pitch and yaw 5 N·m / 22 rad/s.

**Gear-ratio / "mode_machine" table (G1 README, VERIFIED):** https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/g1_description/README.md

- Hip {pitch, roll} ratio:
  - {14.3, 22.5} for rev 1.0 (mode 4/5/6) and mode 13/14.
  - {22.5, 22.5} for mode 10/11/12/15/16/18.
  - {14.3, 14.5} for the deprecated mode 1–3.
- Wrist motor "4010" or "5010(new)".

The URDF effort/velocity limits track the ratio exactly: 14.3:1 → 88 N·m @ 32 rad/s; 22.5:1 → 139 N·m @ 20 rad/s. Hence 88/14.3 = 6.15 N·m and 139/22.5 = 6.18 N·m at the rotor. 32 × 14.3 = 458 rad/s and 20 × 22.5 = 450 rad/s rotor speed. This points to one common rotor/stator with two planetary ratios (ESTIMATED).

The official `unitree_mujoco/unitree_robots/g1/g1_29dof.xml` (older) uses 88/88/88/139/50/50 N·m for hip-pitch/roll/yaw/knee/ankle-pitch/ankle-roll. VERIFIED: https://raw.githubusercontent.com/unitreerobotics/unitree_mujoco/main/unitree_robots/g1/g1_29dof.xml

**MuJoCo Menagerie G1-MJX (sim-to-real-tested in MuJoCo Playground).** Source: https://raw.githubusercontent.com/google-deepmind/mujoco_menagerie/main/unitree_g1/g1_mjx.xml. VERIFIED values:

- Hand-designed foot collision box of half-size (0.09, 0.03, 0.008) m, centred 0.04 m ahead of and 0.029 m below the ankle-roll origin. **Effective sole ≈ 0.18 × 0.06 m**, extending 0.05 m behind to 0.13 m ahead of the ankle.
- Joint armature: hip pitch/yaw and waist yaw 0.010178, hip roll and knee 0.025102, ankle and waist roll/pitch 0.0072195, shoulder 0.0036097 kg·m².
- Position gains kp 75 / kv 2 for legs and kp 20 for ankles.

Consistency check (ESTIMATED): 0.010178/14.3² = 4.98e-5 and 0.025102/22.5² = 4.96e-5 kg·m². This is the same rotor inertia, which again points to a single motor with two gear ratios.

**RL defaults (unitree_rl_gym, VERIFIED):** https://raw.githubusercontent.com/unitreerobotics/unitree_rl_gym/main/legged_gym/envs/g1/g1_config.py

- Default stance: hip pitch −0.1, knee 0.3, ankle pitch −0.2 rad.
- PD: kp hip 100, knee 150, ankle 40 N·m/rad; kd 2 / 4 / 2.
- Action scale 0.25, decimation 4, 12-DOF training URDF `g1_12dof.urdf`.

### A2. Unitree H1 and H1-2 (1.8 m class, reference only)

Primary sources:

- Product page: https://www.unitree.com/h1
- Docs: https://support.unitree.com/home/en/H1_developer — pages `About_H1`, `About_H1-2`
- Shop: https://shop.unitree.com/products/unitree-h1
- Actuator models: https://github.com/unitreerobotics/unitree_rl_lab (`unitree_actuators.py`, `unitree.py`)

| Field | H1 | H1-2 | Label |
|---|---|---|---|
| Height / mass | ≈1.80 m (1520 + 285 mm) / **≈47 kg** | ≈1.78 m / **≈70 kg** | VERIFIED (h1 page; About_H1 / About_H1-2) |
| DOF | 19: leg 5 (hip 3, knee, ankle 1), arm 4, torso 1 | 27: leg 6 (ankle 2), arm 7, torso 1 | VERIFIED |
| Leg order | hip yaw → roll → pitch → knee → ankle | hip yaw → **pitch → roll** → knee → ankle pitch → roll | VERIFIED (README; H1-2 joint sequence doc) |
| Thigh / calf | **400 mm / 400 mm** | 400 / 400 mm | VERIFIED (both), matching the URDF FK |
| Published joint torque | knee ≈360, hip ≈220, ankle ≈59, arm ≈75 N·m | knee ≈360, hip ≈220, waist ≈220, ankle ≈75 × 2, shoulder/elbow 120, wrist 30 N·m | VERIFIED |
| Main motor | **M107**: 360 N·m, 1.9 kg, 189 N·m/kg, Ø107 × 74 mm, hollow shaft, dual encoder, internal-rotor PMSM, crossed roller | same | VERIFIED |
| Torque–speed model | M107-15: 150 / 182.8 N·m, 14 / 25.6 rad/s. M107-24: 240 / 292.5 N·m, 8.8 / 16 rad/s. Sim: knee 300 N·m / 14 rad/s, hip 200 / 23, ankle ("GO2HV") 40 / 9 | — | VERIFIED |
| Ankle | 1 DOF (mechanism not documented) | **parallel A/B** (pitch/roll passive) | VERIFIED |
| Battery | 15 Ah, 0.864 kWh, 67.2 V max, quick-swap; ≈16S (ESTIMATED) | same | VERIFIED |
| Compute | PC1 i5-1235U; PC2 i7-1255U/1265U; optional Orin NX | same (+ up to 3 Orin NX) | VERIFIED |
| Speed | 3.3 m/s (record) | < 2 m/s | VERIFIED |
| Price | "below US$90k" (shop US$90,000) | not found | VERIFIED |

Conflicts:

- H1 mass: 47 kg (official) vs 59.34 kg (`h1.urdf` Σ) vs 51.4–51.6 kg (MJCF Σ).
- H1 ankle torque: 45 N·m (2023) → 59 N·m (now) vs sim 40 N·m.

**Model-file extraction (H1).** Source: https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/h1_description/urdf/h1.urdf. The README (same folder) lists 19 joints. All values below are VERIFIED file values unless labelled ESTIMATED.

- **Hip order: yaw → roll → pitch** (yaw proximal); single-DOF ankle (pitch only). 5 DOF per leg.
- FK at q = 0 (ESTIMATED):
  - Hip-yaw axis at y = ±0.0875 m, z = −0.1742 m. The hip-pitch/knee/ankle line sits 0.1154 m further out (y = ±0.2029 m), so **foot-centre spacing ≈ 0.406 m**.
  - **Thigh = 0.400 m, shin = 0.400 m.**
  - Foot collision box 0.28 × 0.03 m (x-extent from −0.09 to +0.19 m about the ankle). Ankle→sole = 0.062 m, hip-pitch→sole = 0.862 m, pelvis→sole = 1.036 m.
- **Limits:**
  - Hip yaw/roll/pitch: 200 N·m / 23 rad/s. Yaw and roll ±24.6°; pitch −179.9°…+145°.
  - Knee: 300 N·m / 14 rad/s (−14.9°…117.5°).
  - Ankle: 40 N·m / 9 rad/s (−49.8°…29.8°).
  - Torso: 200 N·m / 23 rad/s.
  - Arms: 40 N·m / 9 rad/s (shoulder pitch, roll); 18 N·m / 20 rad/s (shoulder yaw, elbow).
- **Σ masses** (conflict between official files):
  - `h1.urdf` = 59.34 kg; its torso link alone is 17.789 kg.
  - `unitree_mujoco/.../h1/h1.xml` = 51.65 kg; MuJoCo Menagerie `unitree_h1/h1.xml` = 51.44 kg. Both VERIFIED.
  - One leg = 14.18 kg (URDF); shank+foot = 3.55 kg.
- **RL defaults** (unitree_rl_gym `h1_config.py`, VERIFIED): stance −0.1 / 0.3 / −0.2 rad. kp hip 150, knee 200, ankle 40, torso 300; init z = 1.0 m.

**Model-file extraction (H1-2).** Source: https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/h1_2_description/h1_2_handless.urdf (MJCF twin `h1_2_handless.xml`).

- **Hip order: yaw → pitch → roll**; 2-DOF ankle (pitch → roll, 0.020 m apart). 6 DOF per leg; 27 joints total in the handless file.
- FK (ESTIMATED): hip yaw at y = ±0.0875 m. Hip pitch/roll/knee/ankle line at y = ±0.163 m, so **foot-centre spacing ≈ 0.326 m**. **Thigh = 0.400 m, shin = 0.400 m.** The foot is mesh-only, so sole height is not derivable.
- **Limits:**
  - Hip yaw/pitch/roll: 200 N·m / 23 rad/s. Knee: 300 N·m / 14 rad/s (−6.9°…125.5°).
  - Ankle pitch: 60 N·m / 9 rad/s (−51.4°…30°). Ankle roll: 40 N·m / 9 rad/s (±15°).
- **Σ masses** = 66.98 kg (handless URDF and MJCF agree). One leg = 15.40 kg; shank+foot = 4.69 kg.
- **RL defaults** (`h1_2_config.py`): stance −0.16 / 0.36 / −0.2 rad. kp hip 200, knee 300, ankle 40; init z = 1.05 m.

### A2b. Unitree H2 (context only, 2025–26)

- Height / mass / DOF: 1820 × 456 × 218 mm, ≈70 kg, 31 DOF (leg 6, arm 7, waist 3, head 2).
- Leg torque max 360 N·m. Calf + thigh 1045 mm.
- Parallel ankle and parallel waist.
- Battery 15 Ah, 0.972 kWh, 75.6 V max, ≈3 h.
- Price US$29,900.

All VERIFIED from https://www.unitree.com/H2 and the H2 developer docs.

### A3. Unitree R1 (R1 Air / R1 / R1 EDU, launched 2025)

Primary sources:

- Product pages: https://www.unitree.com/R1 and https://www.unitree.com/cn/R1
- Battery page: https://www.unitree.com/R1/battery
- Shop: https://shop.unitree.com/products/unitree-r1
- Docs: https://support.unitree.com/home/en/R1_developer — pages `about_R1`, `joint_motor_sequence`, `basic_motion_routine`

| Field | Value | Label | Source |
|---|---|---|---|
| Height / mass | **1230** × 357 × 190 mm ("≤123 cm"); **≈27 kg Air / ≈29 kg R1 and EDU**. Aug-2025 launch: 1210 mm, ≈25 kg, 24 DOF | VERIFIED / VERIFIED-archive | R1 page; Wayback 20250807 |
| DOF | Air 20 (leg 6, arm 4); R1 26 (leg 6, arm 5, waist 2, head 2); EDU 26–40 | VERIFIED | R1 page |
| Leg order | hip pitch → roll → yaw → knee → ankle pitch → ankle roll | VERIFIED | `about_R1` |
| Calf + thigh | **600 mm** (Aug-2025: 675 mm). Model: 0.288 + 0.309 = 0.597 m | VERIFIED / ESTIMATED | R1 page; URDF |
| Ranges | knee −10…+139°; hip yaw ±157°, pitch −168…+146°, roll −60…+100°; ankle pitch −50…+33°, roll ±15° | VERIFIED | R1 page; docs |
| Torque | Not published on the page (the "Maximum Torque of Arm Joint" row actually means ≈2 kg arm payload). The docs joint table carries unlabelled columns (hip pitch/yaw 75 & 14.3; hip roll/knee 120 & 22.5; ankle A/B 25 & 16). These look copied from the G1 docs and conflict with the R1 URDF (60 N·m hip/knee, 50 N·m ankle, 33 N·m ankle motors) | VERIFIED as published; interpretation ESTIMATED | `joint_motor_sequence`; URDF |
| Motors | Internal-rotor PMSM, hollow shaft, dual + single encoder; crossed-roller + double-row ball bearing | VERIFIED | R1 page |
| Ankle | **Parallel**, A/B active, P/R passive (same scheme as G1) | VERIFIED | `basic_motion_routine` |
| Battery | **33.12 V, 6000 mAh, 199 Wh** (≈9S ESTIMATED), 93.9 × 90.3 × 159 mm; spare US$500; runtime **≈1 h** | VERIFIED | R1/battery page; shop |
| Compute / sensors | 8-core CPU; head vision module 10 TOPS; EDU optional Orin backpack 40–100 TOPS. Air: monocular camera; R1: binocular depth; 4 mics; no lidar | VERIFIED | R1 page; docs |
| Price | **US$4,900 (Air) / US$5,900 (R1) / US$10,500 (EDU, shop)**; CNY 29,900 / 39,900 incl. tax | VERIFIED | R1 page; shop; CN page |

**Model-file extraction (R1 and R1-Air).** Sources:

- https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/r1_description/R1.urdf
- https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/r1_air_description/R1_AIR.urdf
- MJCF with foot primitives: https://raw.githubusercontent.com/unitreerobotics/unitree_mujoco/main/unitree_robots/r1/R1_C%2B%2B.xml

Findings:

- **Hip order: pitch → roll → yaw.** The hip-pitch axis is **inclined 25°** about x: axis (0, 0.91, ∓0.42) at the pelvis.
- **Ankle:** a **parallel linkage is modelled explicitly** (links `left_ankle_A/B`, `_rod`, `constraint_A/B`). Pitch and roll axes coincide (0 offset).
- DOF: 26 non-fixed joints in `R1.urdf`. That is 6 per leg, 2 waist (roll, yaw), 5 per arm and 2 head. `R1_AIR.urdf` has 20 (no waist and no head joints; arms 4 per side).
- FK at q = 0 (ESTIMATED):
  - Hip pitch at (0.0325, ±0.0705, −0.0902) m; hip roll at y = ±0.0888; hip yaw at y = ±0.0882.
  - **Thigh (hip-pitch→knee) = 0.288 m vertical** (0.291 m 3-D). **Shin = 0.309 m** (0.310 m 3-D).
  - Ankle axis at y = ±0.0863 m, so **foot-centre spacing ≈ 0.173 m**.
  - From the MJCF foot (box + 4 spheres): foot 0.18 × 0.07 m, ankle→sole 0.055 m, hip-pitch→sole 0.652 m, pelvis→sole 0.743 m.
- **Limits (URDF):**
  - Hip pitch, roll, yaw and knee: all **60 N·m / 18.8 rad/s**. Ranges: pitch −168°…146°, roll −60°…100°, yaw ±157°, knee −10°…139°.
  - Ankle pitch/roll: **50 N·m / 30 rad/s** (−50°…33°, ±15°).
  - Ankle drive motors A/B (fixed joints carrying limit tags): **33 N·m / 33.4 rad/s**, the same rating as the arm yaw/elbow/wrist motors.
  - Waist roll/yaw and shoulder pitch/roll: 60 N·m / 18.8 rad/s. Shoulder yaw, elbow, wrist and head: 33 N·m / 33.4 rad/s.
- The unitree_mujoco `R1_C++.xml` joints carry `actuatorfrcrange` ±60 (hip/knee) and ±50 (ankle). Its `<motor ctrlrange>` values (88/139/50) look copied from G1, so the file is internally inconsistent; we treat 60/50 as authoritative.
- **Ankle linkage (ESTIMATED by FK):**
  - Motor A centre 96.5 mm and motor B 162.8 mm below the knee axis.
  - Crank radius 21.0 mm; rods 218 mm (A) and 151.5 mm (B).
  - Foot anchors 21 mm forward of the ankle axis, ±14 mm lateral, 9.4 mm below it.
  - With 33 N·m motors: pitch ≈ 2·33·(21/21) ≈ 66 N·m; roll ≈ 2·33·(14/21) ≈ 44 N·m. The URDF gives 50/50.
- **Σ masses:**
  - R1 = 28.84 kg (URDF) / 28.93 kg (MJCF); R1-Air = 26.68 kg.
  - One leg = 5.81 kg: hip-pitch link 0.94 kg, hip-roll link 0.21 kg, hip-yaw/thigh 1.74 kg, knee/shank 2.27 kg, ankle motors 2×0.048 kg, foot 0.47 kg.
  - Shank+foot = 2.93 kg (10 % of total).

### A4. Berkeley Humanoid Lite (UC Berkeley Hybrid Robotics, RSS 2025) — open source

Primary sources:

- **P** — the paper: https://arxiv.org/html/2504.17249. The site PDF is https://lite.berkeley-humanoid.org/static/paper/demonstrating-berkeley-humanoid-lite.pdf.
- **BOM** — https://docs.google.com/spreadsheets/d/1AQEHcH_nPkXYfor2-h7bwNIUMmsePtAm53epnsWgZXc. It is linked from https://berkeley-humanoid-lite.gitbook.io/docs/getting-started-with-hardware/materials-and-parts-bom.
- **Docs** — https://berkeley-humanoid-lite.gitbook.io/docs. Relevant pages are `in-depth-contents/joint-id-mapping`, `in-depth-contents/motor-characterization` and `getting-started-with-software/the-on-board-computer`.
- **Repos** — https://github.com/HybridRobotics/Berkeley-Humanoid-Lite, https://github.com/HybridRobotics/Berkeley-Humanoid-Lite-Assets and https://github.com/HybridRobotics/berkeley-humanoid-lite-lowlevel.
- **Low-level config (RC)** — https://raw.githubusercontent.com/HybridRobotics/berkeley-humanoid-lite-lowlevel/main/robot_configuration.backup.json.
- **CAD** — robot https://cad.onshape.com/documents/fc6443b1d89dcba950e85b60, 6512 actuator https://cad.onshape.com/documents/55ab471d620553f44eac2d08, 5010 actuator https://cad.onshape.com/documents/192ab9c484f00d0dd33b8f01.

| Field | Value | Label | Source |
|---|---|---|---|
| Height / mass | **0.8 m / 16 kg** | VERIFIED | P §III-A |
| Model mass | 16.33 kg (full), 11.34 kg (biped) | ESTIMATED (Σ links) | URDF |
| DOF | 22 = legs 6×2 + arms 5×2 (+2 servo grippers) | VERIFIED | P, docs joint map |
| Leg order | hip roll → hip yaw → hip pitch → knee → ankle pitch → ankle roll; first two hip axes ±45° in the sagittal plane | VERIFIED (order) / ESTIMATED (axes by FK) | docs, URDF |
| Thigh / shin | 0.15 / 0.16 m (upper arm and forearm 0.16 m) | VERIFIED | P Fig. 2; URDF |
| Ankle | **Serial**, each joint a self-contained actuator. Roll axis 0.05 m and pitch axis 0.10 m above the sole | VERIFIED / ESTIMATED | P §III-D-1; URDF FK |
| Foot | Collision box 0.22 × 0.072 × 0.04 m | ESTIMATED | URDF |
| Actuators | Custom "6512" = MAD Components M6C12 150KV outer-rotor BLDC; "5010" = MAD 5010 110KV. Each has a **3-D-printed PLA cycloidal reducer, 15:1**. BOM: legs 8 × 6512 + 4 × 5010, arms 2 × 6512 + 8 × 5010. The 6512 goes to hip/knee and the 5010 to the ankles (mapping ESTIMATED from torque constants in RC) | VERIFIED (counts, ratio) | P §III-C, BOM, RC |
| Motor constants | M6C12: Kt 0.0919 N·m/A, measured KV 127.2, R 0.1886 Ω, 14 pole pairs. 5010: Kt 0.1176 N·m/A, KV 99.4, R 0.6193 Ω | VERIFIED | docs motor-characterization |
| Torque / speed | No peak or continuous rating published. Stiffness test ramped 0–20 N·m. URDF/MJCF 20 N·m & 15 rad/s. Firmware torque limit 6 N·m (legs), current limit 20 A, velocity limit 20 rad/s. Walking used ≈30 % of the torque limit | VERIFIED | P §IV-B, §V-A; RC; URDF |
| Current-limited torque bound | 6512 ≈ 0.0919·20·15 = 27.6 N·m (×0.9 ≈ 24.8). 5010 ≈ 35.3 N·m. No-load speed at 24 V ≈ 21.3 rad/s (6512), 16.7 rad/s (5010) | ESTIMATED | from Kt/KV above |
| Actuator quality | ≈90 % efficiency, 319.5 N·m/rad stiffness, backlash ≤ 0.0229 rad, 60 h durability test | VERIFIED | P §IV |
| Actuator cost | 6512: $188 (US sourcing) / $157 (China); 5010: $136 / $94 | VERIFIED | P Tables I–II |
| Drivers / bus | ST B-G431B-ESC1 with open "Recoil" FOC firmware (MIT); AS5600 encoder; CAN 2.0 at 1 Mbps on 4 buses via USB-CAN | VERIFIED | P, RC |
| Control | Joint loop 250 Hz; RL policy 25 Hz | VERIFIED | P; `policy_*.yaml` |
| Battery | **6S LiPo 4000 mAh, ≈30 min** (≈88.8 Wh ESTIMATED = 22.2 V × 4 Ah) | VERIFIED | P §III-A |
| Compute | Intel N95 mini-PC (docs name a Beelink N95), Ubuntu 22.04 | VERIFIED | P; docs on-board-computer |
| IMU | BNO085 (orig.); docs now recommend IM10A | VERIFIED | P; docs |
| Materials / manufacturing | PLA FDM (every part fits a 200 mm cube printer), brass standoffs, aluminium-extrusion torso | VERIFIED | P §III-A/C |
| BOM cost | **$4,312 (US) / $3,236 (China)** in the paper; live sheet $4,350.59 / ¥23,244.19 | VERIFIED | P Table III; BOM |
| Build time | Parts ≤ 1 week, printing ≤ 1 week, assembly ≈ 3 days | VERIFIED | P §III-C-3 |
| Walking | Zero-shot RL velocity tracking. Training ranges: vx ±0.5, vy ±0.25 m/s, yaw ±1.0 rad/s | VERIFIED | P, env_cfg |
| Licences | Code MIT; assets CC BY-SA 4.0 | VERIFIED | GitHub |
| Conflicts | BOM lists 6 × 6803 bearings for a "linkage on the pitch actuators on legs", but the paper says no linkages. Joint ranges in the assets README differ from the docs (URDF = docs) | — | agent read of BOM/docs |

**Model-file extraction (Berkeley Humanoid Lite).** Sources (HybridRobotics/Berkeley-Humanoid-Lite-Assets, exported from Onshape with onshape-to-robot):

- https://raw.githubusercontent.com/HybridRobotics/Berkeley-Humanoid-Lite-Assets/main/data/robots/berkeley_humanoid/berkeley_humanoid_lite/urdf/berkeley_humanoid_lite.urdf
- MJCF twin `.../mjcf/berkeley_humanoid_lite.xml`
- Legs-only `..._biped.urdf`
- Export config `urdf/config.json`

Findings (VERIFIED file values; derived numbers ESTIMATED):

- **22 actuated joints**: legs 6 × 2 and arms 5 × 2 (shoulder pitch/roll/yaw, elbow pitch, elbow/wrist roll).
- **Hip order:** `hip_roll` → `hip_yaw` → `hip_pitch`. The first two axes are **±45° inclined in the sagittal plane**: roll-joint axis (0.707, 0, 0.707) and yaw-joint axis (0.707, 0, −0.707) at q = 0, from `rpy="0 0.785398 0"` on the hip-roll origin. Each of these two joints therefore produces a mix of roll and yaw. Hip pitch, knee and ankle pitch are pure y-axes; the ankle roll is a pure x-axis.
- Positions at q = 0. The base-frame origin lies 0.04 m *below* the sole, an Onshape assembly origin.
  - Hip-roll joint at (−0.029, ±0.080, 0.543); hip pitch at z = 0.450.
  - Knee at z = 0.300; ankle pitch at z = 0.140; ankle roll at z = 0.090, 0.03 m forward of the pitch axis.
  - Sole at z = 0.040.
- **Thigh = 0.150 m** (knee origin 0.15 along the thigh link; 0.018 m inward offset). **Shin = 0.160 m.**
- **Ankle-pitch→sole = 0.100 m**; ankle-roll axis→sole = 0.050 m. This is a serial ankle with the roll actuator between the pitch axis and the foot.
- **Hip-pitch→sole = 0.410 m.**
- Foot collision box 0.22 × 0.072 × 0.04 m (x-extent −0.074…+0.146 m about the ankle). Foot-centre spacing ≈ 0.114 m.
- **Every joint: effort 20 N·m, velocity 15 rad/s** in URDF and MJCF (`forcerange="-20 20"`). The export config sets `max_effort 20`, `max_velocity 15` for every joint.
- **Ranges:**
  - Hip roll −10°…90°; hip yaw −56°…34°; hip pitch −109°…56°.
  - Knee 0…140°; ankle pitch ±45°; ankle roll ±15°.
- **Σ masses:**
  - Humanoid 16.33 kg: base 4.44 kg; hip-roll 0.838, hip-yaw 0.838, hip-pitch/thigh 0.948, knee/shank 0.654, ankle-pitch 0.106 and foot 0.707 kg per leg.
  - One leg = 4.09 kg; shank+foot = 1.47 kg. Biped-only model = 11.34 kg.
- **Deployed limits (lower than the URDF):**
  - Isaac Lab articulation `berkeley_humanoid_lite_assets/robots/berkeley_humanoid_lite.py`: legs and ankles `effort_limit=6`, `velocity_limit=10.0`, stiffness 20, damping 2. Armature 0.007 (hip/knee) and 0.002 (ankle); arms effort 4.
  - Deployment `configs/policy_humanoid.yaml`: `effort_limits` 6 N·m legs / 4 N·m arms; kp 20 / kd 2; default pose hip-pitch −0.2, knee 0.4, ankle −0.3 rad; control_dt 0.004 s, policy_dt 0.04 s (25 Hz).
- **Motor firmware config** (`motor_configuration.json`): `gear_ratio −15.0` (i.e. 15:1), `pole_pairs 14`, `torque_constant 0.1176 N·m/A`, `i_limit 20 A`, `velocity_limit 20` rad/s, encoder cpr 4096. The export ignore-list names "Cycloidal Disk", "moteus-controller-r45" (parts that exist in the CAD) and bearings 6809/6811/6701.

### A5. Berkeley Humanoid (2024, Hybrid Robotics)

Primary sources:

- **P** — the paper: https://arxiv.org/html/2407.21781
- **Site** — https://berkeley-humanoid.com/
- **URDF** — https://github.com/HybridRobotics/berkeley_humanoid_description
- **Training code** — https://github.com/HybridRobotics/isaac_berkeley_humanoid

| Field | Value | Label | Source |
|---|---|---|---|
| Height / mass | **0.85 m (nominal stance) / 16 kg, legs only** (≈22 kg with the planned 4-DOF arms) | VERIFIED | P §3.1, Table 1 |
| DOF | 12 (legs only) | VERIFIED | P |
| Leg order | HR (yaw) → HAA (roll) → HFE → KFE → FFE (ankle pitch) → FAA (ankle roll); HR/HAA axes ±45° | VERIFIED / ESTIMATED (FK) | P Table 5; URDF |
| Thigh / calf | **0.22 / 0.18 m** | VERIFIED | P §3.1; URDF |
| Foot | 0.16 × 0.06 m | VERIFIED | P Fig. 2b |
| Knee / ankle drive | FFE (ankle pitch) driven through a linkage (coupled knee–ankle mapping). Fig. 2c shows the knee and ankle-pitch actuators at the hip/upper thigh. FAA direct-drive at the foot | VERIFIED | P §3.2, Fig. 2c |
| Actuators | Custom quasi-direct-drive, **9:1 planetary**, cross-roller output bearing (see table below) | VERIFIED | P Table 2 |
| Joint → actuator | HR, HAA, FFE: 8513; HFE: 8518; KFE: 10413; FAA: 5013 | ESTIMATED (armature = rotor J × 81 in Isaac config; Table 1 torques) | Isaac asset file; P |
| Drivers / bus | Custom drivers; EtherCAT 1–4 kHz; 1 kHz torque bandwidth; policy 50 Hz | VERIFIED | P §3–4 |
| Battery | 2 × DJI TB50, hot-swappable (capacity not verified) | VERIFIED (model) | P §3.3 |
| Compute | Intel i7-1255U PC | VERIFIED | P §3.3 |
| Materials | 7075/6061 aluminium; SKD11 steel gearbox and linkage parts | VERIFIED | P §3.3 |
| Cost | **$9,955 without arms** (≈$15 k with arms). Actuator unit costs: 5013 $422, 8513 $570, 8518 $639, 10413 $676 | VERIFIED | P Tables 1, 3 |
| Performance | Omnidirectional walking; 364 m in 10 min (ESTIMATED average 0.61 m/s); 20° slope trail; hops | VERIFIED | P §5 |
| Joint ranges | HR ±35°, HAA ±35°, HFE −100…30°, KFE 0…120°, FFE −30…70° (paper; URDF −30…40°), FAA ±30° | VERIFIED | P Table 5 |

Berkeley Humanoid actuators (paper Table 2, VERIFIED; all 9:1 planetary):

| actuator | mass g | size mm | peak N·m | sustained N·m | max speed @48 V rad/s | max power W | rotor J kg·m² |
|---|---|---|---|---|---|---|---|
| 5013 | 251 | 54.6 × 53 | 9.7 | 4.59 | 83.7 | 220 | 6.1e-6 |
| 8513 | 756 | 104 × 50 | 45.3 | 18.9 | 40.7 | 570 | 6.9e-5 |
| 8518 | 856 | 104 × 55 | 62.6 | 26.1 | 29.0 | 730 | 9.4e-5 |
| 10413 | 1011 | 123 × 50 | 81.1 | 34.2 | 27.9 | 890 | 1.5e-4 |

**Model-file extraction (Berkeley Humanoid, 2024).** Sources:

- https://raw.githubusercontent.com/HybridRobotics/berkeley_humanoid_description/main/urdf/robot.urdf (legs only; the README says "focused on locomotion", arms in development)
- Actuator config: https://raw.githubusercontent.com/HybridRobotics/isaac_berkeley_humanoid/main/exts/berkeley_humanoid/berkeley_humanoid/assets/berkeley_humanoid.py

Findings:

- **Joint order: HR (hip rotation) → HAA (hip ab/adduction) → HFE → KFE → FFE (ankle pitch) → FAA (ankle roll).** HR and HAA axes are ±45° in the sagittal plane: (0.707, 0, 0.707) and (−0.707, 0, 0.707).
- FK at q = 0 (ESTIMATED):
  - HR at y = ±0.070 m on the torso; HFE at z = −0.103; knee at z = −0.323. **Thigh = 0.220 m** (0.232 3-D; knee 0.074 m further out).
  - **Shin = 0.180 m.** FAA 0.0175 m forward of FFE on the same axis height.
  - Ankle→sole = 0.063 m, hip-pitch→sole = 0.463 m, torso→sole 0.566 m. Foot primitives 0.160 × 0.055 m.
- The zero pose is splayed: foot-centre spacing is 0.320 m at q = 0. At the Isaac init pose (HR ∓0.071, HAA ±0.103, HFE −0.463, KFE 0.983, FFE −0.35, FAA ±0.126 rad) it is **0.221 m**, with torso→sole 0.518 m. Isaac init height is 0.515 m.
- **URDF limits:**
  - HR and HAA: 20 N·m / 23 rad/s (±35°).
  - HFE: 30 N·m / 20 rad/s (−100°…30°). KFE: 30 N·m / 14 rad/s (0…120°).
  - FFE: 20 N·m / 20 (L) or 23 (R) rad/s (−30°…40°). FAA: **5 N·m / 42 rad/s** (±30°).
  - The repo README states: *"The maximum torque is limited for safety reasons"* (it does not match the paper).
- **Isaac Lab identified-actuator config:**
  - HR/HAA: effort 20, velocity 23, saturation 402.
  - HFE: 30 / 20, saturation 443. KFE: 30 / 14, saturation 560.
  - FFE: 20 / 23. FAA: 5 / 42, saturation 112.
  - Armatures are written as `J × 81` (e.g. 6.9e-5 × 81 for HR/HAA, 1.5e-4 × 81 for KFE), which suggests a 9:1 reduction (81 = 9²; ESTIMATED).
- **Σ masses:**
  - 16.06 kg. Torso 5.38 kg; per leg: hr 0.797, haa 0.897, hfe/thigh 2.689, kfe/shank 0.350, ffe 0.099, faa/foot 0.507 kg.
  - One leg = 5.34 kg (both legs 66 % of total, since there are no arms). Shank+foot only 0.96 kg (6.0 %): the knee actuator sits in the thigh link (ESTIMATED from the mass split).

### A6. ToddlerBot (Stanford TML; v1 Feb 2025, v2.0 Aug 2025) — open source

Primary sources:

- **P4** — the paper, v4: https://arxiv.org/html/2502.00893 (v1 is https://arxiv.org/html/2502.00893v1)
- **Site** — https://toddlerbot.github.io/
- **Repo** — https://github.com/hshi74/toddlerbot
- **CHANGELOG** — https://raw.githubusercontent.com/hshi74/toddlerbot/main/CHANGELOG.md
- **BOM** — https://hshi74.github.io/toddlerbot/hardware/01_bill_of_materials.html
- **Battery** — https://hshi74.github.io/toddlerbot/features/03_diy_battery.html

| Field | Value | Label | Source |
|---|---|---|---|
| Height / mass | **0.56 m / 3.4 kg** (3,484 g measured in the payload test) | VERIFIED | P4 abstract, §5 |
| Model mass | 2.0 "2XC" 3.50 kg, "2XM" 3.81 kg; v1 3.36 kg | ESTIMATED (Σ links) | URDFs |
| DOF | 30 active: arms 7×2, legs 6×2, neck 2, waist 2 (+optional grippers) | VERIFIED | P4 §3.2 |
| Leg order | hip pitch → roll → yaw → knee → ankle pitch → ankle roll | VERIFIED | URDF chain |
| Thigh / shin | 2.0: **0.1015 / 0.110 m** (`robot.yml`); v1: 0.143 / 0.100 m (FK) | VERIFIED / ESTIMATED | `robot.yml`; v1 URDF |
| v1 → 2.0 change | Legs 30 mm shorter; knee parallel linkage removed; human-like foot with rubber grips; dual hip-motor option; comm board replaces U2D2; control 50 → 200 Hz | VERIFIED | CHANGELOG |
| Ankle | Serial, direct: XM430-W210 pitch then XC430 roll | VERIFIED | `default.yml` |
| Actuators | 2XC variant: hips 2XC430-W250 (pitch + roll, one dual-axis servo per leg); hip yaw XC330-T288 via 18:21 spur gear; knee and ankle pitch XM430-W210; ankle roll XC430-T240BB. 2XM: hip pitch/roll XM430-W350 | VERIFIED | P4 Table 2; `default.yml`; `robot.yml` |
| Servo datasheet (12 V) | XC330-T288 1.00 N·m / 71 rpm / 23 g; XC430-T240BB 1.9 N·m / 70 rpm / 65 g; XM430-W210 3.0 N·m / 77 rpm / 82 g; XM430-W350 4.1 N·m / 46 rpm / 82 g; 2XC430-W250 1.8 N·m per axis / 64 rpm / 102 g; 2XL430-W250 1.5 N·m / 61 rpm / 98.2 g. Stall torque, not continuous | VERIFIED | ROBOTIS e-manual via P4 |
| Identified model | τmax: 2XL430 0.94, XC330 0.76, XC430 1.32, 2XC430 1.09, XM430-W210 1.61 N·m. Max speed 5.97–7.63 rad/s. Repo `default.yml` uses slightly different τmax (e.g. XM430-W210 1.94) | VERIFIED | P4 Table 3; `default.yml` |
| Battery | 4S LiPo 2000 mAh (215 g) or DIY 4 × 21700 5000 mAh (330 g). 14.8 V nominal, stepped down to 12 V. **29.6 / ≈74 Wh** (ESTIMATED) | VERIFIED | P4 §8.7; battery page |
| Runtime | 19 min continuous stepping before overheating; "about 2 h"; 3–5 h intermittent | VERIFIED (different conditions) | P4, site |
| Compute | Jetson Orin NX 16 GB (reComputer J4012, $955); policy 50 Hz on CPU; 2.0 adds foundation-stereo depth (10 Hz, TensorRT) | VERIFIED | P4, BOM, CHANGELOG |
| Sensors | BNO085 IMU; 2 × Arducam IMX291 fisheye; speaker, 2 mics | VERIFIED | P4, BOM |
| Materials | Fully 3-D printed: 2 kg PLA-CF + 1 kg PLA | VERIFIED | P4, BOM |
| Cost | "< $6,000". 2.0 BOM: 2XC $5,727.94, 2XM $7,293.56 (+ tools $1,976) | VERIFIED | P4; BOM |
| Build / repair | Second robot built in 3 days incl. printing; typical repair 21 min print + 14 min assembly | VERIFIED | P4 §5 |
| Capability | Payload 1,484 g; push-ups, pull-ups; 2.0 walks up to 0.25 m/s, cartwheel, crawl | VERIFIED | P4, site |
| Leg ranges (2XC) | hip pitch −135…105°, hip roll −45…90°, hip yaw ±90°, knee −120…0°, ankle pitch −105…55°, ankle roll ±70° | VERIFIED | URDF |
| Licence | Code MIT; Onshape CAD https://cad.onshape.com/documents/565bc33af293a651f66e88d2; MakerWorld print files | VERIFIED | README |
| Conflicts | Hip-yaw gear: paper says 1:1, model files say 18:21. τmax differs across arXiv v1, v4 and `default.yml` | — | — |

**Model-file extraction (ToddlerBot 2.0 and 1.0).** Sources:

- https://raw.githubusercontent.com/hshi74/toddlerbot/main/toddlerbot/descriptions/toddlerbot_2xc/toddlerbot_2xc.urdf (also `toddlerbot_2xm`)
- Robot geometry `toddlerbot_2xc/robot.yml`; actuator sys-ID table `descriptions/default.yml`
- v1.0.0 tag: https://raw.githubusercontent.com/hshi74/toddlerbot/v1.0.0/toddlerbot/descriptions/toddlerbot/toddlerbot.urdf and `config.json`

Findings for 2.0:

- `robot.yml` (VERIFIED) lists: `hip_pitch_to_roll_z 0.024`, `torso_to_hip_z 0.06459`, `hip_to_knee_z 0.1015`, `knee_to_ankle_z 0.11`, `hip_to_ankle_pitch_z 0.2115`, `foot_to_com_y 0.037`.
- Our FK agrees (ESTIMATED): **thigh 0.1015 m, shin 0.110 m**, ankle-pitch→sole 0.039 m, hip-pitch→sole 0.2505 m. Foot box 0.110 × 0.042 m.
- **Hip order: pitch → roll → yaw.** Hip yaw is gear-driven: the `hip_yaw_drive` motor sits off-axis. Ankle roll is 0.023 m behind the pitch axis.
- Σ masses: 3.50 kg (2XC) / 3.81 kg (2XM). One leg 0.54 / 0.62 kg.
- URDF effort/velocity are **placeholders (100 / 100)**. The real limits are in `default.yml`: sys-ID `tau_max` and `q_dot_max` per Dynamixel model (VERIFIED):

  | Dynamixel | tau_max (N·m) | q_dot_max (rad/s) |
  |---|---|---|
  | XC330 | 0.68 | 6.52 |
  | XC430 | 1.47 | 7.0 |
  | XM430-W210 | 1.94 | 7.6 |
  | XM430-W350 | 2.95 | 4.55 |
  | 2XL430 | 0.93 | 5.97 |
  | 2XC430 | 1.09 | 6.78 |

- Leg motor map, 2XC variant (`default.yml`): hip pitch 2XC430, hip roll 2XC430, hip yaw XC330 (through gears), knee XM430-W210, ankle pitch XM430-W210, ankle roll XC430. The 2XM variant (`robot.yml`) swaps hip pitch and roll to XM430-W350 and the arms to 2XC430. Leg kp 2100 (XC330 1500).
- v1.0 (tag v1.0.0), ESTIMATED by FK:
  - Thigh 0.143 m, shin 0.100 m, ankle-pitch→sole 0.039 m, **hip-pitch→sole 0.282 m**. That is 31.5 mm taller than 2.0, matching the CHANGELOG line *"30mm shorter for enhanced stability"*.
  - Σ = 3.36 kg.
  - v1.0 knee = XM430 through a parallel-rod linkage (`is_knee_closed_loop: true`, links `knee_rod`); hip yaw geared 18:21 (`gear_ratio 0.857`).

### A7. Poppy Humanoid (Inria / Poppy project) — open source

Primary sources:

- **Site** — https://www.poppy-project.org/en/robots/poppy-humanoid/
- **Repo** — https://github.com/poppy-project/poppy-humanoid
- **Motor configuration** — https://raw.githubusercontent.com/poppy-project/poppy-humanoid/master/software/poppy_humanoid/configuration/poppy_humanoid.json
- **Distributor** — https://www.generationrobots.com/en/403347-poppy-humanoid-robot-raspberry-pi-version-with-3d-parts.html

| Field | Value | Label | Source |
|---|---|---|---|
| Height / mass | **83 cm / 3.5 kg** (distributor 85 cm) | VERIFIED | site; distributor |
| DOF | 25 incl. 5-DOF torso; legs 5 DOF each (no ankle roll): hip_x (roll) → hip_z (yaw) → hip_y (pitch) → knee → ankle pitch | VERIFIED | site; JSON; URDF |
| Thigh / shin | 0.182 / 0.180 m | VERIFIED | URDF joint origins |
| Actuators | Dynamixel servos. Hip pitch MX-64 (6.0 N·m @12 V, 63 rpm, 200:1, 135 g). Hip roll/yaw, knee, ankle MX-28 (2.5 N·m @12 V, 55 rpm, 193:1, 77 g). Head AX-12A. Totals 19 × MX-28, 4 × MX-64, 2 × AX-12 | VERIFIED | JSON; ROBOTIS e-manual |
| Power | Tethered 12 V supply + SMPS2Dynamixel; no battery | VERIFIED | Poppy BOM; distributor |
| Compute | Raspberry Pi 3/4 (Odroid XU4 on v1.0.2) | VERIFIED | README; site |
| Materials | 3-D-printed polyamide (SLS) | VERIFIED | distributor |
| Cost | Build $8–9 k (≈60 % Dynamixels); kit €9,971.52 incl. VAT with printed parts / €7,862.40 without | VERIFIED | README; distributor |
| Licence | Hardware CC BY-SA 4.0; software GPL v3 | VERIFIED | README |
| Model mass | 2.61 kg in the URDF, vs 3.5 kg stated | ESTIMATED | URDF |

**Model-file extraction (Poppy Humanoid).** Sources:

- https://raw.githubusercontent.com/poppy-project/poppy-humanoid/master/hardware/URDF/robots/Poppy_Humanoid.URDF
- Motor config: https://raw.githubusercontent.com/poppy-project/poppy-humanoid/master/software/poppy_humanoid/configuration/poppy_humanoid.json

Findings (VERIFIED file values; derived numbers ESTIMATED):

- The URDF frame is x = lateral, z = up.
- **Leg: hip_x (roll) → hip_z (yaw) → hip_y (pitch) → knee_y → ankle_y. 5 DOF, no ankle roll.** 25 joints in total.
- FK (ESTIMATED): hip_z/hip_y at x = ±0.0665 m (yaw-axis spacing 0.133 m). Hip pitch at z = −0.024, knee −0.206, ankle −0.386, so **thigh 0.182 m, shin 0.180 m**. The foot is mesh-only.
- Σ URDF masses = 2.61 kg; one leg 0.44 kg.
- URDF limits: MX-64 joints (hip_y, abs_y, abs_x) 7.3 N·m / 8.2 rad/s; MX-28 joints 3.1 N·m / 7.0 rad/s; AX-12 head 1.8 N·m / 10 rad/s.
- JSON motor map:
  - MX-64: hip_y, abs_y, abs_x.
  - MX-28: hip_x, hip_z, knee, ankle, shoulders, arm_z, elbows, abs_z, bust_x, bust_y.
  - AX-12: head_z, head_y.
- JSON angle limits: knee −3.5°…134° (left); hip_y −104°…84°; ankle ±45°; hip_x −30°…28.5°.


### A8. Booster Robotics T1 (2024) and K1 (2025) (Beijing)

**Sources**

- T1 product page: https://www.booster.tech/booster-t1/
- T1 specifications: https://docs.booster.tech/docs/product-manual/t1/getting-started/specifications/
- K1 product page: https://www.booster.tech/booster-k1/
- K1 specifications: https://docs.booster.tech/docs/product-manual/k1/getting-started/specifications/
- Model assets: https://github.com/BoosterRobotics/booster_assets
- Training code: https://github.com/BoosterRobotics/booster_gym
- Actuator classes: https://raw.githubusercontent.com/BoosterRobotics/booster_train/main/source/booster_train/booster_train/assets/robots/actuator.py
- Actuator-to-joint mapping: https://raw.githubusercontent.com/BoosterRobotics/booster_train/main/source/booster_train/booster_train/assets/robots/booster.py
- Booster Gym paper: https://arxiv.org/abs/2506.15132

| Field | Booster T1 | Booster K1 | Label |
|---|---|---|---|
| Height / mass | **1.18 m** (118 × 47 × 23 cm) / **≈30 kg**; model Σ 31.74 kg | **≈0.95 m / ≈19.5 kg**; model Σ 19.67 kg | VERIFIED / ESTIMATED |
| DOF | 23 = head 2 + arms 4×2 + waist 1 + legs 6×2. With grippers 31, with hands 41 | 22 = head 2 + arms 4×2 + legs 6×2 | VERIFIED |
| Leg order | hip pitch → roll → yaw → knee → ankle pitch ("up") → ankle roll ("down") | same | VERIFIED (docs + model) |
| Leg length | "Leg Length 57 cm" (= our FK hip-pitch→sole 0.571 m) | n/p | VERIFIED |
| Joint ranges (site) | hip pitch ±118° (URDF −170…125.5°), roll −21…88°, yaw ±58°, knee 0…123°, ankle pitch −50…20°, roll ±25° | hip pitch −171…126°, roll −22…89°, yaw ±59°, knee 0…127° (docs/URDF 133°), ankle pitch −50…20°, roll ±20° | VERIFIED |
| Actuators (booster_train classes) | hip pitch **E8112** 96 N·m, 16.76 rad/s. hip roll/yaw **E6408** 68 N·m, 14.66 rad/s. knee **E8116** 130 N·m, 14.66 rad/s. ankle **2 × E4315** 76 N·m, 12.57 rad/s. waist E6408; arms E4310 38.3 N·m; head DM4310 | hip pitch **E6408** 68 N·m. hip roll **E4315** 76 N·m (URDF 43). hip yaw **E4310** 38.3 N·m. knee **E6416** 112 N·m, 12.57 rad/s. ankle 2 × E4310. arms R14 14 N·m, 33.5 rad/s; head HT4438 | VERIFIED (model/config) |
| Actuator brand | "E"-series names and the armature values (E6416 0.095625, E4315 0.0339552, E4310 0.0282528 kg·m²) are **identical** to the Encos EC-A values in the Asimov docs and repo. So Booster very likely uses Encos EC-A actuators | — | ESTIMATED (inference) |
| Torque–speed model | Flat torque to a "knee" speed, then linear drop: knee-point 7.54 / 1.88 / 6.28 / 2.62 rad/s for E8112 / E6408 / E8116 / E4315 | E6416 2.09, E4310 7.85 rad/s | VERIFIED (config) |
| Published peak torque | 130 N·m; dual encoders | 60 N·m (conflicts with the model's 112 N·m knee) | VERIFIED |
| Ankle | **parallel**: two shank motors, cranks, push-rods; serial↔parallel conversion described in the Booster Gym paper | parallel (`K1AnkleParaWrapper`) | VERIFIED |
| Battery | 10.5 Ah; 2 h walking / 4 h standing; ≤2 h charge; slide-in swappable. Voltage n/p ("Li-ion 24–48 V" per a RoboCup team sheet, UNVERIFIED) | 2 Ah (Geek) or 5 Ah (Edu/Pro); 30 / 80 min at 0.4 m/s; removable | VERIFIED |
| Compute | Jetson AGX Orin 32 GB (200 TOPS); Standard adds Intel i7-1370P motion board | Geek: 8-core ARM SoC 48 TOPS. Edu: Orin NX 8 GB. Pro: AGX Orin 32 GB | VERIFIED |
| Sensors | depth camera (RealSense D455 per manual, UNVERIFIED), 9-axis IMU, 6-mic array | stereo depth camera, 9-axis IMU, 3 mics | VERIFIED |
| Speed | 1 m/s (docs; manual V1.1 says 0.5) | 1.1 m/s | VERIFIED |
| Price | No official price. Distributor: €26,000 excl. VAT (Standard) | No official price. CNY 29,900 "from" (press); CNY 38,999 on JD (Explorer, 2026-09-18) | UNVERIFIED |
| Open source | booster_assets (BSD-3), booster_gym (Apache-2.0), booster_train/deploy; MuJoCo Menagerie `booster_t1` | booster_assets, booster_train | VERIFIED |
| Materials | n/p | n/p | — |

Model limits conflict for T1:

- booster_assets `T1_23dof.urdf`: 98.8 / 68 / 68 / 130.5 / 73.1 / 17.2 N·m.
- booster_gym `T1_serial.urdf` and the Menagerie model: 45 / 30 / 30 / 60 / 20 / 15 N·m.
- Deploy `torque_limit`: 60 / 25 / 30 / 60 / 24 / 15 N·m.
- Ankle drive: MJCF 43 N·m vs booster_train E4315 76 N·m.

**Model-file extraction (Booster T1).** Sources:

- Newest assets: https://raw.githubusercontent.com/BoosterRobotics/booster_assets/main/robots/T1/T1_23dof.urdf, `T1_29dof.urdf`, `T1_locomotion.urdf`, and the parallel-ankle MJCF `T1_23dof_parallel.xml`
- Older training model: https://raw.githubusercontent.com/BoosterRobotics/booster_gym/main/resources/T1/T1_serial.urdf
- Deploy config: https://raw.githubusercontent.com/BoosterRobotics/booster_gym/main/deploy/configs/T1.yaml

Findings (VERIFIED file values; derived numbers ESTIMATED):

- 23 DOF = head 2 + arms 4 × 2 + waist yaw 1 + legs 6 × 2 (booster_assets README). The 29-DOF variant has 7-DOF arms.
- **Hip order: pitch → roll → yaw** (all at y = ±0.106 m; the waist-yaw joint sits between trunk and legs).
- FK: **thigh 0.236 m, shin 0.280 m**; ankle pitch→roll 0.012 m.
- **Foot box:**
  - booster_assets: 0.225 × 0.100 m, ankle-pitch→sole 0.055 m, hip-pitch→sole 0.571 m, trunk→sole 0.687 m.
  - booster_gym serial: 0.223 × 0.100 m, ankle→sole 0.042 m, hip→sole 0.558 m.
- Foot-centre spacing 0.212 m (unchanged in the default stance).
- **Limits — two different sets in official files:**
  - (a) booster_assets `T1_23dof.urdf` (and the `T1_23dof_parallel.xml` motors):
    - Hip pitch 98.8 N·m / 15.29 rad/s; hip roll 68 / 14.66; hip yaw 68 / 14.66.
    - Knee 130.5 / 14.76.
    - Ankle pitch 73.1 / 12.57 and ankle roll 17.2 / 12.57 (serial-equivalent). The parallel MJCF drives the ankle with **two 43 N·m motors**.
    - Waist 68 N·m; arms 38.3 N·m / 17.59 rad/s; head 7 N·m.
  - (b) booster_gym `T1_serial.urdf`: hip pitch 45 N·m / 12.5 rad/s; roll 30 / 10.9; yaw 30 / 10.9; knee 60 / 11.7; ankle pitch 20 / 18.8; ankle roll 15 / 12.4.
  - The deploy config `torque_limit` for the legs is **60 / 25 / 30 / 60 / 24 / 15 N·m** (hip pitch, roll, yaw, knee, ankle pitch, roll). Its `mech.parallel_mech_indexes: [15, 16, 21, 22]` marks the ankles as a parallel mechanism.
  - We read (a) as hardware peak and (b) and the deploy limits as software/safety limits (ESTIMATED interpretation).
- Deploy PD: stiffness 200 (hip/knee) and 50 (ankle); damping 5 / 3. Default stance hip-pitch −0.2, knee 0.4, ankle −0.25 rad.
- **Parallel ankle (ESTIMATED from `T1_23dof_parallel.xml`):**
  - Drive-motor centres 96 mm and 156 mm below the knee; crank 43 mm; rods 180 mm and 120 mm.
  - Foot anchors 41.5 mm behind the ankle axis, ±27.5 mm lateral, 20.7 mm above the pitch axis.
  - Drive armature 0.034 kg·m².
- **Σ masses** 31.74 kg (assets) / 31.61 kg (gym). Trunk 11.7 kg. One leg 6.15 kg; shank+foot 2.58 kg.

**Model-file extraction (Booster K1).** Sources:

- https://raw.githubusercontent.com/BoosterRobotics/booster_assets/main/robots/K1/K1_22dof.urdf
- `K1_locomotion.urdf`
- `K1_22dof_parallel.xml`

Findings (VERIFIED file values; derived numbers ESTIMATED):

- 22 DOF = head 2 + arms 4 × 2 + legs 6 × 2. No waist.
- **Hip order: pitch → roll → yaw**, all at y = ±0.096 m.
- FK: **thigh 0.1915 m, shin 0.2452 m**; ankle pitch and roll coincident.
- From the parallel MJCF foot box: foot 0.18 × 0.07 m, ankle→sole 0.038 m, hip-pitch→sole 0.475 m, trunk→sole 0.552 m. Foot-centre spacing 0.192 m.
- **Limits:**
  - Hip pitch **68 N·m / 14.66 rad/s**; hip roll 43 / 12.57; hip yaw 38.3 / 17.59.
  - **Knee 112 N·m / 12.57 rad/s.**
  - Ankle pitch and roll 38.3 / 17.59, serial-equivalent. The parallel MJCF uses **two 38.3 N·m drive motors**.
  - Arms 14 N·m / 33.51 rad/s; head 6 N·m / 7.85 rad/s.
- Ranges: hip pitch −169.5°…127.5°, hip roll −21.5°…88°, hip yaw ±58°, knee 0…133°, ankle pitch −49.8°…19.8°, ankle roll ±19.8°.
- **Parallel ankle (ESTIMATED):**
  - Motors 81.6 mm and 140 mm below the knee; crank 41 mm; rods 158 mm and 82 mm.
  - Anchors 29 mm behind the ankle, ±24 mm lateral, 17.5 mm above.
  - Drive armature 0.028 kg·m². Rule-of-thumb capacity ≈ 2·38.3·29/41 ≈ 54 N·m pitch and ≈ 45 N·m roll. The closed-chain Jacobian gives 58 / 38 N·m at neutral (table below).
- **Σ masses** 19.67 kg (URDF) / 19.87 kg (parallel MJCF). Trunk 6.50 kg. One leg 4.50 kg; shank+foot 2.03 kg.

**Closed-chain ankle capacity (ESTIMATED; our Jacobian analysis of the official `*_parallel.xml` geometry).** Script: `ankle_linkage.py` in the scratchpad.

| robot | drive motors | IK closure error at q = 0 | pure-pitch capacity at neutral | pure-roll capacity at neutral | pitch over ROM grid | roll over ROM grid |
|---|---|---|---|---|---|---|
| T1 | 2 × 43 N·m, crank 43 mm, rods 180/120 mm | 0.25 mm | **98 N·m** | **53 N·m** | 33–126 N·m | 17–77 N·m |
| K1 | 2 × 38.3 N·m, crank 41 mm, rods 158/82 mm | 0 mm | **58 N·m** | **38 N·m** | 35–61 N·m | 12–49 N·m |

The ROM grid spans pitch −50°…+20° and roll ±25° (T1) / ±20° (K1). Capacity is lowest at full dorsiflexion combined with roll.

### A9. K-Scale Labs K-Bot (2025) and Zeroth-01 / Z-Bot (open source; company shut down Nov 2025)

**Sources**

- Mechanical docs: https://github.com/kscalelabs/docs/blob/master/docs/robots/k-bot/mechanical.md
- Electrical docs: https://github.com/kscalelabs/docs/blob/master/docs/robots/k-bot/electrical.md
- Hardware repo: https://github.com/kscalelabs/kbot
- Model files: https://github.com/kscalelabs/kbot-models
- Product page (archived): https://web.archive.org/web/20251006231727/https://www.kscale.dev/kbot
- Shop (archived): https://web.archive.org/web/20250326033803/https://shop.kscale.dev/products/kbot
- Farewell letter (archived): https://web.archive.org/web/20260129051959/https://kscale.ai/
- Robstride vendor site: https://robstride.com/
- Zeroth repo: https://github.com/kscalelabs/zeroth-bot
- Zeroth BOM: https://github.com/kscalelabs/docs/blob/master/docs/robots/zeroth-01/bom.md
- Asset repo (archived): https://github.com/kscalelabs/kscale-assets

| Field | K-Bot | Zeroth-01 / Z-Bot | Label |
|---|---|---|---|
| Height / mass | **1.4 m (4′7″) / 34 kg**, payload 10 kg, up to 4 h (archived official page). Model Σ 36.7 kg | 1.5 ft ≈ **0.46 m** (archived shop). Model Σ 3.75 kg (5-DOF legs) / 3.35 kg (6-DOF) | VERIFIED (archived) / ESTIMATED |
| DOF | **20**: legs **5 each** (hip pitch → roll → yaw → knee → ankle pitch, **no ankle roll**), arms 5 each | `zbot`: 18 (5-DOF legs). `zbot-6dof`: 20 (hip yaw → roll → pitch → knee → ankle pitch → ankle roll; arms 4) | VERIFIED (model/docs) |
| Joint ranges | hip pitch −60…127°, hip roll −130…12°, hip yaw ±90°, knee 0…155°, ankle −15…65° | model hip pitch −90…50°, knee ±80°, ankle pitch −80…40°, roll ±60° | VERIFIED |
| Actuators | **Robstride** QDD, planetary, steel gears, 48 V: **RS04** ×4 (hip pitch, knee) 40/120 N·m rated/peak, 9:1, 1.42 kg, 200 rpm no-load, **US$255**. **RS03** ×8 (hip roll/yaw, shoulder pitch/roll) 20/60 N·m, 9:1, 0.88 kg, 195 rpm, US$225. **RS02** ×6 (ankle, shoulder yaw, elbow) 6/17 N·m, 7.75:1, 0.38–0.405 kg, 410 rpm, US$145. **RS00** ×2 (wrist) 5/14 N·m, 10:1, 0.31 kg, US$125 | **Feetech STS3250** "50 kg·cm" serial-bus servos (16 in BOM); STS3215 too slow for legs. Sys-ID fit (model params, not datasheet): STS3250 max_torque 8.72, max_velocity 8.94 rad/s at 12.1 V | VERIFIED (docs + vendor) |
| Model limits | RS04 120 N·m @ 17.49 rad/s; RS03 60 @ 18.85; RS02 17 @ 37.70; RS00 14 @ 27.23. Soft limits 84/42/11.9/9.8. kp/kd legs 150/24.7 (hip pitch), 200/26.4 (hip roll), 100/3.4 (yaw), 150/8.7 (knee), 40/1.0 (ankle); 50 Hz | URDF placeholders 2 N·m / 2 rad/s | VERIFIED (model) |
| Battery / power | **12 Ah NCM** pack (135 × 180 × 65 mm), 50 A BMS, 80 A fuse; **48 V + CAN to each limb**. ≈576 Wh if 48 V (ESTIMATED) | RC LiPo (1200 mAh listing), ≈12 V class (ESTIMATED from the 12→5 V converter) | VERIFIED / ESTIMATED |
| Compute | **Raspberry Pi 5** (24 V buck); Jetson AGX Orin mentioned in press (UNVERIFIED) | Milk-V Duo S + Waveshare bus-servo adapter, 9-DOF IMU, Milk-V camera | VERIFIED |
| Materials / manufacturing | CNC-machined fabricated parts, designed to be moldable, COTS; hands on a lens-mount interface piggy-backing the 48 V + CAN arm bus; head is a single USB device | 3-D printed (0.16 mm layers, 5 walls) + prefabricated parts | VERIFIED |
| Price | Founder's Edition **US$9,000** (2025-03); site Aug–Oct 2025: US$16,000 struck through, US$10,999 second batch | **BOM from US$350**; Z-Bot Founder's Edition US$1,000 (regular US$1,500) | VERIFIED (archived) |
| Open source | CAD on Onshape (https://cad.onshape.com/publications/e15cf8edefacbba3009917c0/), BOM/assembly/wiring in kscalelabs/docs. Licence: repo LICENSE says MIT; README says CERN-OHL-S hardware + GPL-3 software (conflict) | MIT; Onshape CAD; STL zip | VERIFIED |
| Company status | Shut down Nov 2025, orders cancelled, IP open-sourced (press, UNVERIFIED). kscale.ai farewell letter (VERIFIED archived). api.kscale.dev / kscale.dev do not resolve today (VERIFIED observed) | same | — |

**Model-file extraction (K-Scale K-Bot).** Sources:

- https://raw.githubusercontent.com/kscalelabs/kbot-models/master/kbot/robot.urdf (+ `robot.mjcf`)
- Collision-primitive variant `kbot-full-collisions/robot.mjcf`
- Joint and actuator metadata `kbot/metadata.json`

Findings (VERIFIED file values; derived numbers ESTIMATED):

- **20 DOF: each leg has 5** (hip pitch → hip roll → hip yaw → knee → a **single ankle pitch**). Each arm has 5 (shoulder pitch/roll/yaw, elbow, wrist).
- FK:
  - Hip pitch at (−0.002, ±0.056, −0.074); hip roll/yaw axes at y = ±0.127 m; knee at y = ±0.106, z = −0.459.
  - **Thigh 0.385 m, shin 0.290 m.** The long thigh is unusual.
  - From the full-collision MJCF (two r = 0.02 m capsules): foot ≈ 0.21 m long, ankle→sole 0.058 m, hip-pitch→sole 0.733 m, base→sole 0.807 m.
- **Actuators** (`metadata.json` `actuator_type_to_metadata`):

  | Robstride type | max_torque (N·m) | max_velocity (rad/s) | armature | used at |
  |---|---|---|---|---|
  | robstride_04 | 120 | 17.488 | 0.04 | hip pitch, knee |
  | robstride_03 | 60 | 18.849 | 0.02 | hip roll, hip yaw, shoulder pitch/roll |
  | robstride_02 | 17 | 37.699 | 0.0042 | ankle, shoulder yaw, elbow |
  | robstride_00 | 14 | 27.227 | 0.001 | wrist |

- `soft_torque_limit` per joint: 84 (RS04), 42 (RS03), 11.9 (RS02), 9.8 (RS00) N·m.
- Ranges (metadata.json): hip pitch −60°…127°, hip roll −12°…130°, hip yaw ±90°, knee 0…155°, ankle −72°…13°. The URDF ankle limit is −65°…15°; the docs quote −15°…65° (different sign convention).
- kp/kd: hip pitch 150/24.7, hip roll 200/26.4, hip yaw 100/3.4, knee 150/8.65, ankle 40/0.99. Control frequency 50 Hz.
- **Σ masses** 36.72 kg. Torso 12.97 kg. One leg 7.59 kg: hip yoke 0.55 kg, hip-roll RS03 assembly 2.40 kg, femur 2.35 kg, shin 1.68 kg, foot 0.61 kg. Shank+foot 2.29 kg.

**Z-Bot 6-DOF model (ESTIMATED from VERIFIED files).** Sources: https://raw.githubusercontent.com/kscalelabs/kscale-assets/master/zbot-6dof/robot.urdf (+ `zbot-6dof-feet/robot.mjcf`).

- Hip yaw → roll → pitch → knee → ankle pitch → roll.
- Thigh 0.100 m, shin 0.100 m (3-D 0.106 m); ankle-pitch→sole 0.033 m; hip-pitch→sole 0.233 m.
- Foot box 0.104 × 0.074 m; hip-yaw axes y = ±0.043 m.
- Σ 3.35 kg.

### A10. Fourier N1 (Fourier, Shanghai; open-sourced 2025)

**Sources**

- Product page: https://fftai.com/ecosystem/n1
- Brochure: https://fftai.com/pdf/en/n1.pdf (dated 2025-05-19)
- Model files: https://github.com/FFTAI/Wiki-GRx-Models (branch `FourierN1`), https://github.com/FFTAI/Wiki-GRx-Mujoco (branch `FourierN1`)
- SDK docs: https://github.com/FFTAI/fourier-grx-N1
- MuJoCo Menagerie: `fourier_n1`

| Field | Value | Label |
|---|---|---|
| Height / mass | **1.30 m / 38 kg** (web page) vs **1245 × 441 × 202 mm / ≈39 kg** (brochure). Model Σ 39.73 kg | VERIFIED (conflict) |
| DOF | 23: legs 6+6, waist 1, arms 5+5. Every actuator has its own IP address | VERIFIED |
| Leg order | hip pitch (**15° tilt**) → roll → yaw → knee → ankle roll → ankle pitch (coincident) | VERIFIED (model, SDK sequence) |
| Ankle | **parallel**: two push-rods from two shank-mounted actuators (seen in the brochure render; not stated in text) | ESTIMATED |
| Actuators | **Fourier FSA** (`fi_fsa` SDK). Classes: 8029E (hip pitch, knee) 95 N·m @ 12.36 rad/s; 6043E (hip roll/yaw, waist, shoulder pitch) 54 N·m @ 14.74; 4530E (ankles, arms) 30 N·m @ 16.75 | VERIFIED (model) |
| Joint spec (brochure) | peak joint torque **144 N·m**; peak current 70 A; 24–60 V (46 V rated); backlash ≤ 10 arcmin; dual encoders 16/14-bit; Ethernet | VERIFIED |
| Battery | **475 Wh** Li-ion, ≤3.2 kg, 39.6 V nominal (≈11S, ≈12 Ah, ESTIMATED), 46.2 V cut-off, > 800 cycles, **≈2 h**, ≈3.5 h charge | VERIFIED |
| Power | ≈460 W rated system power | VERIFIED |
| Compute | Intel **i7-13700H**, 16 GB, 512 GB NVMe | VERIFIED |
| Speed | walk 2.7 km/h (0.75 m/s); run 10.8 km/h (3.0 m/s). Web page says 3.5 m/s | VERIFIED (conflict) |
| Materials | aluminium alloy + engineering plastic | VERIFIED |
| Price | not found | — |
| Open source | URDF (Apache-2.0 on the `FourierN1` branch), MJCF, gym, deploy (LGPL-3.0), SDK docs (MIT). Hardware package (BOM, drawings, assembly) via a Baidu Pan link on the product page (not accessed) | VERIFIED |

**Model-file extraction (Fourier N1).** Sources:

- https://raw.githubusercontent.com/FFTAI/Wiki-GRx-Models/FourierN1/N1/urdf/N1_raw.urdf (branch `FourierN1`; `N1_rotor.urdf` includes rotor inertia)
- MuJoCo Menagerie `fourier_n1/n1.xml`
- Joint table: https://raw.githubusercontent.com/FFTAI/fourier-grx-N1/main/docs/reference/joint_sequence.md

Findings (VERIFIED file values; derived numbers ESTIMATED):

- The joint table gives **23 DOF = 6 + 6 legs, 1 waist, 0 head, 5 + 5 arms**. The leg order in the SDK is hip pitch, hip roll, hip yaw, knee, **ankle roll, ankle pitch**.
- FK:
  - Hip pitch axis **tilted 15°** (0, 0.97, ∓0.26). Hip roll/yaw at y = ±0.120 m.
  - **Thigh 0.3076 m** (0.315 3-D), **shin 0.280 m**. Ankle roll and pitch coincident (roll proximal).
  - Foot-centre spacing 0.240 m. The foot is mesh-only.
- **Limits** (URDF; Menagerie actuator classes in brackets):
  - Hip pitch and knee 95 N·m / 12.356 rad/s ["8029E"].
  - Hip roll, hip yaw, waist and shoulder pitch 54 N·m / 14.738 rad/s ["6043E"].
  - Ankle roll/pitch and the other arm joints 30 N·m / 16.747 rad/s ["4530E"].
  - Menagerie armatures: 0.121 / 0.168 / 0.031 kg·m².
- Ranges: hip pitch ±149.9°, roll −15°…90°, yaw ±149.9°, knee −5°…135°, ankle roll ±25°, ankle pitch ±45°.
- **Σ masses** 39.73 kg. Torso 7.99 kg + waist-yaw link 3.18 kg + base 3.18 kg. One leg 8.88 kg (thigh-yaw link 3.37 kg); shank+foot 2.85 kg.

### A11. Noetix Robotics N2 (2025) and Bumi (2025) (Beijing)

**Sources**

- Site: https://www.noetixrobotics.com/ (spec tables are embedded in the site JS bundle)
- Docs: https://web.noetixrobotics.com/docs/ (N2 SDK guide, N2 delivery document, Bumi document)
- Official news: https://www.noetixrobotics.com/official/api/news/detail?id=71 (also 64, 80, 81, 88, 91)
- GitHub: https://github.com/Noetix-Robotics (noetix_n2_gym, noetix_sdk_n2, noetix_sdk_bumi)

| Field | Noetix N2 | Noetix Bumi | Label |
|---|---|---|---|
| Size / mass | 114 × 49 × 28 cm ("1.2 m" in news); **≈30 kg** (site) / 33.5 kg with battery (SDK guide). Model Σ 33.16 kg | **98 × 35 × 20 cm, ≈17 kg** with battery (early coverage: 94 cm, ≈12 kg) | VERIFIED (conflicts noted) |
| DOF | **18**: legs 5 each (hip yaw → hip roll → hip pitch → knee → ankle pitch), arms 4 each. SDK guide says 18–20 | **21**: legs 6 each (hip pitch → roll → thigh yaw → knee → ankle pitch → ankle roll), arms 4 each, waist 1 | VERIFIED |
| Leg geometry | model thigh 0.200 m, shin 0.260 m (the SDK guide's "≈0.76 m thigh+shank" conflicts) | thigh + shank ≈ 513 mm | ESTIMATED / VERIFIED |
| Drive | knee and ankle **linkage-driven** (连杆, "linkage"); crossed-roller + deep-groove output bearings; dual encoders; air-cooled | EtherCAT + CAN-FD joint bus | VERIFIED |
| Joint torque | hip yaw 90, hip roll 90, hip pitch **150**, knee **150**, ankle 70, arms 27 N·m (URDF velocity 14 rad/s legs) | hip pitch 60, hip roll 60, thigh yaw 15, knee 60, ankle pitch 30, ankle roll 30, waist 27, arms 5 N·m; "max 70 N·m" | VERIFIED |
| Ranges | hip pitch −90…45°, roll/yaw −37…57°, knee 0…126° | hip pitch ±120°, knee 0…128°, ankle pitch −55…25°, roll ±10° | VERIFIED |
| Battery | 48 V 7.5 Ah (≈360 Wh ESTIMATED) quick-release (site) / 52 V 7 Ah (SDK); 1–2 h; 1 h charge | **13S 48 V 5.1 Ah** Grepow pack (≈245 Wh ESTIMATED), 1.36 kg, quick-release, 2–3 h | VERIFIED |
| Compute | RK3588S (LubanCat), EtherCAT to joints; EDU adds Jetson Orin Nano Super | RK3576 (closed); EDU-Pro Orin Nano Super, EDU-Max Orin NX | VERIFIED |
| Speed | running up to 3.2 m/s (news) | 0.5 m/s | VERIFIED |
| Materials | n/p | "composite materials" | VERIFIED (Bumi) |
| Price | not found | **CNY 9,998** (launched Oct 2025) | VERIFIED (official news repost) |
| Open source | noetix_n2_gym (URDF/MJCF), noetix_sdk_n2 (BSD-3) | noetix_sdk_bumi (BSD-3); no URDF found | VERIFIED |

**Model-file extraction (Noetix N2).** Source: https://raw.githubusercontent.com/Noetix-Robotics/noetix_n2_gym/main/resources/robots/N2/urdf/N2.urdf (also `N2_10dof.urdf`, `mjcf/n2_18dof.xml`).

Findings (VERIFIED file values; derived numbers ESTIMATED):

- **18 DOF: legs 5 × 2, arms 4 × 2.** Leg = hip "yaw" + hip "roll" (co-located, axes (0.707, 0, ±0.707), i.e. ±45° sagittal, like Berkeley Humanoid) → hip pitch → knee → single ankle pitch.
- FK: **thigh 0.200 m, shin 0.260 m**; hip at y = ±0.09 m.
- **Limits:**
  - Hip yaw/roll 90 N·m / 14 rad/s; hip pitch and knee **150 N·m** / 14 rad/s; ankle 70 N·m / 14 rad/s.
  - Arms 27 N·m / 10 rad/s.
- Ranges: hip pitch −90°…44.7°, knee 0…126°, ankle −57°…43°.
- **Σ masses** 33.16 kg. Base 10.9 kg. One leg 8.77 kg.

### A12. Robotis OP3

Primary sources:

- **e-Manual** — https://emanual.robotis.com/docs/en/platform/op3/introduction/
- **Official xacro** — https://raw.githubusercontent.com/ROBOTIS-GIT/ROBOTIS-OP3-Common/master/op3_description/urdf/robotis_op3.structure.lleg.xacro
- **Shops** — https://robotis.us/products/robotis-op3us and https://en.robotis.com/shop_en/item.php?it_id=905-0036-000

| Field | Value | Label | Source |
|---|---|---|---|
| Height / mass | **≈510 mm / ≈3.5 kg** (without skin) | VERIFIED | e-Manual spec table |
| DOF | 20: legs 6×2, arms 3×2, head 2 | VERIFIED | e-Manual; xacro |
| Leg order | hip yaw → hip roll → hip pitch → knee → ankle pitch → ankle roll | VERIFIED | xacro |
| Thigh / shin | **0.11015 / 0.110 m** (knee origin z −0.11015, ankle −0.110) | VERIFIED | xacro |
| Hip spacing | Hip-yaw origins y = ±0.035 m (0.070 m) | VERIFIED | xacro |
| Actuators | **XM430-W350-R on all 20 joints**: 353.5:1 gear train, 4.1 N·m stall @12 V, 46 rpm (4.82 rad/s), 82 g | VERIFIED | e-Manual |
| Model limits | xacro `effort=1000 velocity=100` (placeholders) | VERIFIED | xacro |
| Compute | Intel NUC i3 (2025: 8 GB DDR4, 250 GB SSD) + OpenCR (STM32F746) sub-controller | VERIFIED | e-Manual |
| Sensors | IMU on OpenCR; Logitech C920 camera | VERIFIED | e-Manual |
| Battery | 3S LiPo 11.1 V, 3300 mAh (older 1800 mAh) → 36.6 Wh (ESTIMATED) | VERIFIED | e-Manual |
| Runtime | 10–15 min (quoted in the ToddlerBot paper) | UNVERIFIED | ToddlerBot P4 §8.7 |
| Price | **US$13,764.35** (ROBOTIS US) / **US$11,969** (ROBOTIS intl.) | VERIFIED | shops |
| Open source | Software Apache-2.0; STEP data in ROBOTIS-OP-Series-Data | VERIFIED | GitHub |

**Model-file extraction (Robotis OP3).** Source: MuJoCo Menagerie https://raw.githubusercontent.com/google-deepmind/mujoco_menagerie/main/robotis_op3/op3.xml. It is derived from the official URDF at https://github.com/ROBOTIS-GIT/ROBOTIS-OP3-Common/tree/master/op3_description/urdf (README, VERIFIED).

- **Hip order: yaw → roll → pitch**; knee; ankle pitch → roll. 20 DOF.
- FK (ESTIMATED):
  - Hip yaw at y = ±0.035 m; roll and pitch at z = −0.0285 m (intersecting).
  - **Thigh 0.110 m, shin 0.110 m**; ankle-pitch→sole 0.0305 m; hip-pitch→sole 0.251 m.
  - Foot boxes 0.127 × 0.078 m.
- Σ = 3.15 kg (the model's inertials).
- Menagerie default actuator: `position kp=21.1, forcerange=-5 5`, joint armature 0.045, damping 1.084, frictionloss 0.03.
- Cross-check against the official xacro https://raw.githubusercontent.com/ROBOTIS-GIT/ROBOTIS-OP3-Common/master/op3_description/urdf/robotis_op3.structure.lleg.xacro (VERIFIED): hip yaw origin (0, 0.035, 0); hip roll (−0.024, 0, −0.0285); hip pitch (0.0241, 0.019, 0); knee z −0.11015; ankle pitch z −0.110; ankle roll (−0.0241, −0.019, 0). The xacro limits are placeholders (effort 1000, velocity 100, ±0.9π).

### A13. Menlo Research Asimov: v0 open-source legs (2025) and Asimov 1 (1.2 m, 2026), open source

This is the closest size match to JX1.

Primary sources:

- Docs (M1): https://docs.menlo.ai/asimov/1/overview/system-tour/mechanical
- Electrical (M2): https://docs.menlo.ai/asimov/1/overview/system-tour/electrical
- Asimov 1 repo (M4): https://github.com/menloresearch/asimov-1
- v0 repo (M5): https://github.com/menloresearch/asimov-v0
- Motor reference (M6): https://raw.githubusercontent.com/menloresearch/asimov-mjlab/main/motor_parameters.md
- Blog (M8): https://menlo.ai/blog/humanoid-legs-100-days
- Product page (M9): https://menlo.ai/asimov-1

| Field | Value | Label | Source |
|---|---|---|---|
| Height / mass | **1.2 m / 35 kg** (model Σ 32.22 kg) | VERIFIED / ESTIMATED | M4 README spec table; M1 |
| DOF | 25 powered: legs 6×2, arms 5×2, waist yaw 1, neck 2 (neck locked in the 23-DOF sim model) | VERIFIED | M1, M4 |
| Leg order | hip pitch → hip roll → hip yaw → knee → ankle pitch → ankle roll. Hip pitch horizontal on v1; v0 tilted 45° | VERIFIED | M1; model files |
| Ankle | **Parallel RSU**: motors A/B drive the ends of a bar through linkages. Small-angle map θA = K_P·θp − K_R·θr, θB = −K_P·θp − K_R·θr | VERIFIED | M5 `mechanical/ankle_mechanism.md` |
| Foot | v1 fixed flat foot (no toe), contact footprint 0.177 × 0.066 m (4 spheres). v0 had a passive toe, 0.2175 × 0.09 m | VERIFIED / ESTIMATED | M1, M8; model |
| Actuators (Encos) | hip pitch EC-A6416-P2-25 (planetary 25:1); hip roll EC-A5013-H17-100 (**harmonic** 100:1); hip yaw EC-A3814-H14-107 (**harmonic** 107:1); knee EC-A4315-P2-36 (planetary 36:1); ankle A/B EC-A4310-P2-36 | VERIFIED | M5 table; M6 |
| Rated / peak torque (N·m) | hip pitch 40/120, hip roll 30/90, hip yaw 20/60, knee 25/75, ankle 12/36 (the docs' joint table lists ankle A 40/145.4 and B 17/57.6, apparently joint-space) | VERIFIED | M1, M6 |
| Rated / peak speed | 107/120, 33/38, 47/52, 109/117, 75/89 rpm. Model joint velocity limits 12.57 / 3.98 / 5.45 / 12.25 / 9.32 rad/s equal the peak speeds | VERIFIED | M6; URDF |
| Actuator mass / size | 803 g (Ø88×67.5 mm), 640 g (Ø63×81.5), 400 g (Ø53×78.5), 455 g (Ø56×69.5), 384 g (Ø56×60.5) | VERIFIED | M6 |
| Actuator mass per leg | ≈3.07 kg (803 + 640 + 400 + 455 + 2 × 384 g) | ESTIMATED | — |
| Efficiency / backlash | 73 % / 15′ (6416); 31 % / 10″ (5013 harmonic); 51 % / 10″ (3814 harmonic); 74 % / 10′ (4315); 71 % / 10′ (4310) | VERIFIED | M6 |
| Rotor inertia → armature | 104.4, 10, 3, 25.5, 18.2 kg·mm² → reflected 0.0652, 0.100, 0.0343, 0.0330, 0.0236 kg·m² (docs list 0.0956 / 0.11 / 0.038 / 0.034 / 0.0565) | VERIFIED | M6; M1 |
| Battery | **INR18650 13S4P, 46.8 V nominal, 10.5 Ah, 491.4 Wh**, 54.6 V charge, 30 A max, ≈2 kg. Runtime not published | VERIFIED | M2 |
| Compute / bus | Radxa CM5 on a custom motion-control board (LSM6DSV IMU, 6 SPI-CAN) + Raspberry Pi 5 in the head (media/network). CAN 5 × 1 Mbps + 1 × 500 kbps; XT30(2+2) daisy-chain harness per limb (`electrical/wiring/motor-wires.csv`) | VERIFIED | M2, M4 |
| Materials / manufacturing | 7075 aluminium + MJF PA12 nylon (v0 legs: MJF + CNC) | VERIFIED | M1, M4, M8 |
| Price | **DIY kit US$20,000** (shipping; $499 deposit). v0 legs "just over $10k", ~$8.5k of it actuators | VERIFIED | M4, M9, M8 |
| Licences | Hardware CERN-OHL-S-2.0, software GPL-2.0 (mjlab repo Apache-2.0). BOM on request / in the manual | VERIFIED | M4 |
| Conflicts | mjlab README rated torques 55/45/30/50/18 vs docs 40/30/20/25/12. mjlab README says "Synapticon" vs v0 README "Encos". URDF efforts 45/45/28/45/40/17 N·m are far below peak | — | — |

**Model-file extraction (Menlo Research Asimov).** Sources:

- Asimov 1: https://raw.githubusercontent.com/menloresearch/asimov-1/main/sim-model/urdf/asimov_1.urdf (+ `xmls/asimov_1.xml`)
- Asimov v0 legs: https://raw.githubusercontent.com/menloresearch/asimov-v0/main/sim-model/xmls/asimov.xml
- Actuator reference: https://raw.githubusercontent.com/menloresearch/asimov-mjlab/main/motor_parameters.md

Findings (VERIFIED file values; derived numbers ESTIMATED):

- Asimov 1 URDF: **23 revolute joints** (neck yaw/pitch fixed in the sim model). Legs 6 × 2, waist yaw, arms 5 × 2.
- **Hip order pitch → roll → yaw, all axes orthogonal (no tilt).**
- FK:
  - Hip pitch at (−0.052, ±0.0675, −0.044); hip roll at y = ±0.1075; hip yaw at y = ±0.1145.
  - **Thigh 0.270 m, shin 0.2724 m**; ankle pitch→roll 0.010 m below.
  - Four foot contact spheres span 0.177 × 0.066 m (0.1255 m ahead / 0.0515 m behind the ankle).
  - **Ankle-pitch→sole 0.044 m; hip-pitch→sole 0.586 m; pelvis→sole 0.630 m.** Foot-centre spacing 0.215 m.
- **URDF limits:**
  - Hip pitch 45 N·m / 12.57 rad/s (−120°…57°).
  - Hip roll 45 / 3.98 (±45°); hip yaw 28 / 5.45 (±45°).
  - Knee 45 / 12.25 (0…86°!).
  - Ankle pitch 40 / 9.32 (±20°); ankle roll 17 / 9.32 (±5.7°).
  - Waist yaw 40 / 12.57. Shoulder pitch 30, roll 25, yaw 20; elbow and wrist 12 N·m.
- The URDF velocity limits equal the Encos datasheet *peak speeds*: 120 / 38 / 52 / 117 / 89 rpm.
- **Σ masses** 32.22 kg (the README says 35 kg). One leg 6.45 kg; shank+foot 3.11 kg.
- **Asimov v0** (legs + pelvis):
  - Hip-pitch axis tilted 45°; articulated toe joint.
  - Thigh 0.299 m, shin 0.295 m, ankle→sole 0.042 m.
  - Σ 15.88 kg; one leg 6.29 kg.

### A14. Other relevant robots found (compact, low-cost or open)

#### A14.1 EngineAI PM01 (and SA01)

Sources:

- E1: https://en.engineai.com.cn/product-pm01.html
- E4: PM01 User Manual V1.0, via https://en.engineai.com.cn/product-support-pm01.html
- E5 (official press release, 2024-12-26): https://www.newsfilecorp.com/release/235198/Breaking-Through-with-Strength-Leading-the-Future-EngineAI-Launches-the-PM01-Humanoid-Robot
- Model: https://raw.githubusercontent.com/engineai-robotics/engineai_robotics_native_sdk/main/assets/resource/robot/pm01_edu/urdf/serial_pm01_edu.urdf

| Field | Value | Label |
|---|---|---|
| Size / mass | 1400 × 540 × 253 mm, ~44 kg EDU (2026 page). Manual: 1388 mm, ~43 kg. Press release: 1.38 m, ~40 kg. URDF Σ 40.92 kg | VERIFIED (conflicting official figures) |
| DOF | 24 (legs 6×2, waist 1, arms 5×2, neck 1) | VERIFIED (E1) |
| Leg length | "thigh + shin" **686.5 mm**; model 0.336 + 0.363 = 0.699 m hip-pitch→ankle (0.687 m hip-roll→ankle) | VERIFIED / ESTIMATED |
| Actuators | Own integrated joints: internal-rotor PMSM, planetary, crossed-roller bearing, dual encoders. Max joint torque 164 N·m (page also says 130; manual 145) | VERIFIED (E1, E4) |
| URDF limits | hip pitch, roll and knee 164 N·m @ 26.3 rad/s; hip yaw and ankles 61 N·m @ 35.2 rad/s | VERIFIED (model) |
| Battery | 10 Ah quick-swap (54.6 V charge) ≈ 468 Wh, ~2 h runtime | VERIFIED / ESTIMATED (Wh) |
| Compute | 8-core CPU + Jetson Orin NX 16 GB (2026 EDU) | VERIFIED |
| Material | aviation aluminium | VERIFIED |
| Speed | 2 m/s | VERIFIED |
| Price | **CNY 88,000** (launch price until 2025-03-31) | VERIFIED (E5) |
| SA01 | 12-DOF legged platform. Model `zq_sa01.urdf`: hip **roll → yaw → pitch**, thigh 0.300 m, shin 0.370 m, 140 N·m @ 25 rad/s hip/knee, 24 N·m @ 31 rad/s ankle, Σ 33.11 kg. Reseller: 1290 mm, ~40 kg, US$7,599 | VERIFIED (model) / UNVERIFIED (reseller) |

#### A14.2 PNDbotics Adam Lite

Sources:

- https://wiki.pndbotics.com/en/robot/humanoid_robot/
- Actuators: https://wiki.pndbotics.com/en/actuator/introduce/
- Models: https://github.com/pndbotics/pnd_models

| Field | Value | Label |
|---|---|---|
| Height / mass | 1.67 m / 60 kg (Lite); URDF Σ 58.48 kg | VERIFIED |
| DOF | 25 (Lite): legs 6×2, waist 3, arms 5×2 | VERIFIED |
| Leg order | hipPitch (35° tilt) → hipRoll → hipYaw → knee → anklePitch → ankleRoll; parallel two-motor ankle | VERIFIED |
| Actuators | PND-130A-7F-7-P hip pitch (7:1, 200/340 N·m, 4 kg); PND-80-20-50-S hip roll (harmonic 51:1, 64/180 N·m, 1.5 kg); PND-60-17-30-S hip yaw (31:1, 16/48 N·m, 1 kg); PND-130-7F-P knee (7:1, 113/340 N·m); PND-50-6F5S-30-P ankle ×2 (30:1, 17.6/46 N·m, 0.7 kg). Planetary vs harmonic inferred from the naming rule (ESTIMATED) | VERIFIED |
| URDF | hip pitch 230 N·m / 15 rad/s; hip roll 160 / 8; hip yaw 105 / 8; knee 230 / 15; ankle pitch 40 / 20; ankle roll 12 / 20 | VERIFIED (model) |
| Battery / compute | 1172 Wh, 46.2 V; NUC12 i7-1260P (+ Orin NX on higher trims) | VERIFIED |
| Speed / price | 1.5 m/s (VERIFIED); US$120,000 (humanoid.guide, UNVERIFIED) | — |
| Open source | URDF/MJCF (BSD-style licence), RL gym and SDK | VERIFIED |

#### A14.3 Duke Humanoid v1 (Duke General Robotics Lab, 2024), open source

Sources:

- Paper: https://arxiv.org/abs/2409.19795
- Repo: https://github.com/generalroboticslab/DukeHumanoidv1 (MIT)
- Model: the `legged_env` URDF (see §A14 model notes)

| Field | Value | Label |
|---|---|---|
| Size / mass | ≈1 m shoulder-to-foot, leg 0.5 m; 30 kg (URDF Σ 29.64 kg) | VERIFIED |
| DOF / order | 10: hip yaw → hip pitch → hip roll → knee → ankle pitch (1-DOF ankle; the foot has a linear contact edge) | VERIFIED |
| Femur / tibia | 0.285 / 0.235 m (paper); URDF 0.281 / 0.235 m | VERIFIED / ESTIMATED |
| Knee / ankle drive | Knee through a parallel linkage; ankle motor at the knee drives through a second linkage (low distal mass) | VERIFIED |
| Actuators | Motorevo BLDC + planetary, same motor everywhere. HR, HAA and KFE 18:1 → 72 N·m rated, 20 rad/s. HFE 20:1 → 80 N·m, 18 rad/s. Ankle 10:1 → 40 N·m, 36 rad/s. Table I max HFE 264, KFE 238 N·m | VERIFIED |
| Power / bus | Tethered (no battery); EtherCAT 2 kHz; Teensy 4.0; MicroStrain 3DM-CV7 IMU | VERIFIED |
| Material | 6061 aluminium plates, extrusion frame, TPU covers | VERIFIED |

#### A14.4 AgiBot X1 (open source, 2024) and AgiBot X2 / Lingxi X2 (2025)

Sources:

- https://www.agibot.com/products/X1
- https://github.com/AgibotTech/agibot_x1_hardware
- https://www.agibot.com/products/X2
- https://github.com/AgibotTech/agibot_x2_urdf
- Actuator map: https://raw.githubusercontent.com/AgibotTech/agibot_x1_infer/main/src/module/dcu_driver_module/cfg/dcu_x1.yaml

| Field | Value | Label |
|---|---|---|
| X1 size / mass | 130 cm, 33 kg, 34 active DOF, 2 h, 1 m/s max | VERIFIED |
| X1 actuators | Hips and knee: PowerFlow R86. Ankle: 2 × PowerFlow R52 driving a parallel rod ankle. R86-3: 1.28 kg, 60/200 N·m, 30/85 rpm, 48 V. R86-2: 0.81 kg, 20/80 N·m. R52: 0.45 kg, 6/19 N·m, 50/130 rpm | VERIFIED |
| X1 model | Hip pitch 45° tilted, pitch → roll → yaw; thigh 0.268 m (hip-pitch→knee; 0.226 m from the hip-roll origin); shin 0.305 m; URDF hip pitch/roll/knee 150 N·m @ 8 rad/s, yaw 50 @ 24, ankle 80 @ 10; Σ 35.32 kg | ESTIMATED from VERIFIED file |
| X1 open source | STEP, drawings, SOP, BOM (xlsx, not downloaded); inference code Mulan PSL v2 | VERIFIED |
| X2 size / mass | 1310 × 460 × 210 mm; ~35 kg (X2), ~39 kg (Ultra); URDF X2-EDU Σ 41.2 kg | VERIFIED (conflict) |
| X2 DOF | 25 (legs 6, waist 3, arms 5); Ultra 30 | VERIFIED |
| X2 model (X2-EDU v1.4) | pitch → roll → yaw; thigh 0.320 m, shin 0.282 m; ankle→sole 0.073 m; foot 0.214 × 0.13 m; hip/knee 120 N·m @ 11.94 rad/s, ankle pitch 60 @ 13.6, ankle roll 36 @ 14.66 | ESTIMATED from VERIFIED file |
| X2 battery / compute / speed | ~500 Wh, ~2 h, swappable; 2 × RK3588 (+Orin NX on Ultra); up to 1.8 m/s | VERIFIED |

#### A14.5 HighTorque Mini Pi / Mini Pi+ / Mini Hi (low-cost kid-size)

Sources:

- https://www.hightorquerobotics.com/pi/
- https://www.hightorque.cn/pi-plus-from-scratch/reference/hardware/
- https://www.hightorque.cn/en/hie/
- Store: https://store.hightorque.cn/products.json
- Actuator: https://www.hightorquerobotics.com/product?id=75
- Models: https://github.com/HighTorque-Robotics/HT_Robot_URDF

| Field | Value | Label |
|---|---|---|
| Mini Pi | 520 mm, 7 kg, 24 V, 12 DOF, **US$3,500** | VERIFIED |
| Mini Pi+ | ~75 cm, 13.84 kg (hardware doc; product page 15 kg), 27 DOF; RK3588; 6S 21.6 V 97.2 Wh pack, 55–65 min; **US$5,500** | VERIFIED (conflicting sub-figures) |
| Leg actuator | HTDW-5036-02: Ø50 × 47.4 mm, 323–345 g, 36:1 two-stage planetary, 6 N·m rated / 21 N·m locked-rotor, 50/75 rpm, CAN-FD | VERIFIED |
| Mini Hi | 890 mm, 20 kg, 48 V, 27 DOF (URDF 25 DOF, Σ 18.32 kg) | VERIFIED |
| Models | Pi+: thigh 0.142 m, shin 0.140 m, 20 N·m @ 5.45 rad/s. Mini Hi: thigh 0.192, shin 0.199 m, 32.4 / 14.4 N·m. Pi: thigh 0.140, shin 0.140 m | ESTIMATED from VERIFIED files |

#### A14.6 Roboparty "Roboto Origin" (ATOM 01), fully open DIY humanoid (Shanghai, 2025)

Sources:

- https://github.com/Roboparty/roboto_origin
- BOM: https://raw.githubusercontent.com/Roboparty/roboto_origin/main/assets/BOM_EN.md
- Models: https://github.com/Roboparty/rpo_description and https://github.com/Roboparty/rpo_hardware

| Field | Value | Label |
|---|---|---|
| Size | 1.25 m, 34 kg (secondary); URDF Σ 33.76 kg | UNVERIFIED / ESTIMATED |
| DOF | 23: legs 6×2 + waist 1 + arms 5×2 | ESTIMATED (URDF) |
| Leg order | hip yaw → hip roll → hip pitch → knee → ankle pitch/roll. Yaw and roll axes tilted 30° | ESTIMATED from VERIFIED file |
| Geometry | thigh 0.250 m, shin 0.300 m; hip-yaw spacing 0.145 m | ESTIMATED |
| Ankle | Rod-driven (BOM lists "Sole Connecting Rod", "Universal Connector" ×4, "Output Flange Connecting Rod" ×4, spherical plain bearings ×8) | VERIFIED (BOM) |
| Actuators | 9 × **Damiao DM10010L** (CNY 1,989 each) on hips, knees and waist; 14 × **DM4340P 48 V** (CNY 949 each) on ankles and arms | VERIFIED (BOM counts/prices); mapping ESTIMATED |
| Model limits | `rpo_description/urdf/rpo.urdf`: hip/knee/waist 120 N·m @ 25 rad/s, ankle/arms 27 N·m @ 8 rad/s. `rpo_hardware` CAD-export URDFs: 80 N·m @ 10.47 and 18 N·m @ 3.77 | VERIFIED (models) |
| DM4340P | 9 / 27 N·m rated/peak, 40:1, ~375 g | UNVERIFIED (Seeed wiki, distributor) |
| Battery | 48 V 15 Ah Li-ion pack, 140×140×115 mm, **CNY 528** → ≈720 Wh (ESTIMATED) | VERIFIED |
| Compute | D-Robotics RDK X5 8 GB (CNY 599); 4 × USB-to-CAN; HI13 IMU (CNY 350) | VERIFIED |
| Frame | CNC aluminium, 120-grit sandblast + black anodise. Subtotal CNY 15,670: inner thigh CNY 1,500 each, calf 1,600 each, hip fixation 1,800 | VERIFIED |
| **Total BOM** | **CNY 49,713** (header, v1.0.1, 2026-01-05; line-item sum 49,743.53). Actuators = CNY 31,187 (**63 %**) | VERIFIED / ESTIMATED (share) |
| Licences | Hardware CERN-OHL-W-2.0, software GPL-3.0 | VERIFIED |

#### A14.7 Westwood Robotics BRUCE (kid-size research biped)

Sources:

- https://www.westwoodrobotics.io/bruce/
- Brochure: https://www.westwoodrobotics.io/wp-content/uploads/2023/08/BRUCE_EN_061823_E.pdf
- Macros: https://raw.githubusercontent.com/Westwood-Robotics/BRUCE-OP/main/Settings/BRUCE_macros.py
- Model: https://raw.githubusercontent.com/Westwood-Robotics/BRUCE_simulation_models/V1.6/Gazebo/urdf/bruce.urdf

| Field | Value | Label |
|---|---|---|
| Size / mass / DOF | 70 cm, 4.8 kg, 16 DOF (legs 5 each, arms 3 each); URDF Σ 4.45 kg | VERIFIED |
| Leg | hip yaw → pitch → roll with **all three axes intersecting** (URDF origin (0.029, ±0.076, −0.040)) → knee → ankle pitch; thigh 0.2049 m, shin 0.1999 m | VERIFIED |
| Actuators | Koala BEAR proprioceptive, 250 g, burst > 8 N·m, liquid-cooled knees; firmware 9:1, 0.35 N·m/A, 10.5 N·m max, 30 A | VERIFIED |
| Battery / compute | 3000 mAh, ~20 min; 6-TOPS computer | VERIFIED |
| Material | carbon-fibre composite | VERIFIED |
| Price | US$15,290 list (US$8,890 limited offer) | VERIFIED |

**Model-file extraction (other robots).**

- **EngineAI PM01 EDU.**
  - Source: https://raw.githubusercontent.com/engineai-robotics/engineai_robotics_native_sdk/main/assets/resource/robot/pm01_edu/urdf/serial_pm01_edu.urdf (+ `xml/serial_actuators.xml`).
  - 24 joints. Pitch → roll → yaw hip with the pitch axis tilted 15°. Thigh 0.336 m, shin 0.363 m; ankle pitch→roll 0.015 m.
  - Hip pitch, hip roll and knee **164 N·m / 26.3 rad/s**. Hip yaw, ankle pitch/roll, waist and arms 61 N·m / 35.2 rad/s.
  - Σ 40.92 kg; one leg 9.31 kg; shank+foot 5.13 kg.
- **PNDbotics Adam Lite** (Menagerie `pndbotics_adam_lite/adam_lite.xml`).
  - Pitch → roll → yaw with the hip-pitch axis tilted 35°. Thigh 0.461 m, shin 0.370 m; ankle→sole 0.065 m; foot 0.22 × 0.08 m.
  - Motor ctrlrange: hip pitch 230, hip roll 160, hip yaw 105, knee 230, ankle pitch 40, ankle roll 12 N·m; waist 110; arms 65/30/6.4.
  - Σ 58.19 kg.
- **Duke Humanoid v1.**
  - Source: https://raw.githubusercontent.com/generalroboticslab/legged_env/master/assets/urdf/v6biped_urdf_v4_aug29/v6biped_urdf_v4_squarefoot_aug29.urdf (the `legged_env` submodule of DukeHumanoidv1).
  - **10 DOF**, legs only: hip yaw → hip pitch → hip roll → knee → ankle pitch. The knee and ankle are driven through rockers/links from actuators in the thigh (`knee_rocker`, `ankle_rocker`, `shank_link_main`).
  - Thigh 0.281 m, shin 0.235 m.
  - Hip yaw/roll and knee 81 N·m / 13.33 rad/s; hip pitch 90 / 12; ankle 45 / 10.67.
  - Σ 29.64 kg (base 9.62 kg); shank+foot only 0.99 kg.
- **AgiBot X1** (open source).
  - Source: https://raw.githubusercontent.com/AgibotTech/agibot_x1_train/main/resources/robots/x1/urdf/x1.urdf
  - Pitch → roll → yaw hip with the pitch axis tilted 45°. Thigh 0.268 m, shin 0.305 m.
  - Parallel ankle (`leg_l_toe_a/b` links): motor centres 110 mm and 165 mm below the knee, crank 32.8 mm, rods 195 mm and 140 mm, anchors 41 mm behind the ankle and ±23.3 mm lateral (ESTIMATED).
  - Hip pitch, hip roll and knee 150 N·m / 8 rad/s; hip yaw 50 / 24; ankle 80 / 10. Joint ranges are placeholders (±180°).
  - Σ 35.32 kg; one leg 7.03 kg.
- **HighTorque** (https://github.com/HighTorque-Robotics/HT_Robot_URDF):
  - *Pi+* (`pi_plus_24dof.urdf`): thigh 0.142 m, shin 0.140 m; all leg joints 20 N·m / 5.45 rad/s; Σ 11.0 kg.
  - *Mini Hi* (`hi_25dof.urdf`): thigh 0.192 m, shin 0.199 m; hip/knee 32.4 N·m / 5.55 rad/s; ankle 14.4 / 5.45; Σ 18.32 kg.
  - *Pi* (`pi_12dof.urdf`, legs only): thigh 0.140 m, shin 0.140 m; 20 N·m; Σ 7.11 kg.
  - All three use a pitch → roll → yaw hip.
- **Roboparty Roboto Origin (Atom01) V2.**
  - Source: https://raw.githubusercontent.com/Roboparty/roboto_origin/main/modules/rpo_hardware/V2.0/roboto_origin_mechanic/03_URDF/urdf/roboto_origin.urdf
  - 23 DOF = legs 6 × 2 + waist 1 + arms 5 × 2.
  - Hip yaw → roll → pitch, with the yaw and roll axes both **tilted 30°** in the sagittal plane: yaw axis (−0.5, 0, −0.87), roll axis (0.87, 0, −0.5). Thigh 0.250 m, shin 0.300 m; ankle pitch and roll coincident (rod-driven, see BOM).
  - Two different sets of limits in the official files:
    - Training model `rpo_description/urdf/rpo.urdf`: hip/knee/waist **120 N·m / 25 rad/s**, ankle/arms **27 N·m / 8 rad/s**.
    - CAD-export URDFs (`rpo_hardware` V1.0/V2.0): 80 N·m / 10.47 rad/s and 18 N·m / 3.77 rad/s.
  - The unit counts match the BOM: DM10010L ×9 (8 leg + waist), DM4340P ×14 (4 ankle + 10 arm).
  - Σ 33.76 kg (V2) / 33.97 kg (V1); one leg 7.85 kg.
- **AgiBot X2 EDU (v1.4).**
  - Sources: https://raw.githubusercontent.com/AgibotTech/agibot_x2_urdf/main/X2_URDF-v1.4.0/X2-EDU.urdf and `X2-EDU.xml`.
  - Pitch → roll → yaw hip, all axes orthogonal. Hip pitch at y = ±0.0713; roll/yaw/knee/ankle line at y = ±0.137 m, so foot-centre spacing ≈ 0.274 m.
  - Thigh 0.320 m, shin 0.282 m. From the 12 MJCF foot spheres: ankle-pitch→sole 0.073 m, hip-pitch→sole 0.675 m, foot 0.214 × 0.13 m.
  - Hip pitch/roll/yaw and knee 120 N·m / 11.94 rad/s; ankle pitch 60 N·m / 13.61 rad/s; ankle roll 36 N·m / 14.66 rad/s. Ranges: hip pitch −155°…146.5°, knee 0…138°, ankle pitch −46°…26°, ankle roll ±17°.
  - Σ 41.2 kg (official ≈35 kg); one leg 8.55 kg.
- **Westwood BRUCE.**
  - Source: https://raw.githubusercontent.com/Westwood-Robotics/BRUCE_simulation_models/V1.6/Gazebo/urdf/bruce.urdf
  - Hip yaw, pitch and roll all have their origin at (0.029, ±0.076, −0.040) m, so the axes intersect.
  - Thigh 0.2049 m, shin 0.1999 m.
  - Σ 4.45 kg. URDF limits are zero placeholders.
- **EngineAI SA01.**
  - Source: https://raw.githubusercontent.com/engineai-robotics/engineai_legged_gym/master/resources/robots/zq_humanoid/urdf/zq_sa01.urdf
  - Roll → yaw (co-located at y = ±0.075 m) → pitch → knee → ankle pitch → ankle roll.
  - Thigh 0.300 m, shin 0.370 m.
  - Hip and knee 140 N·m / 25 rad/s; ankle 24 N·m / 31 rad/s.
  - Σ 33.11 kg (legs + base only).


### A15. Appendix: per-file extraction tables for all 43 parsed model files

These were generated automatically by `extract_all.py` (FK at q = 0).

- All values are VERIFIED file values or ESTIMATED FK derivations.
- Effort/velocity are the file's `<limit>` or actuator range.
- "n/a" means the file has no value.
- Foot extents use primitive collision geoms only.

####  `G1_29dof_rev1.0`
- File: https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/g1_description/g1_29dof_rev_1_0.urdf (parsed URDF, root `pelvis`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **33.34 kg** (39 links, 29 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch_joint[y] → left_hip_roll_joint[x tilt10] → left_hip_yaw_joint[z tilt10] → left_knee_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.3366 m (3-D 0.3409) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.3000 m (3-D 0.3000) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, -0.0176) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0526 m; hip-pitch→sole = 0.6892 m; root→sole = 0.7919 m — ESTIMATED (FK of file values)
  - foot collision primitives (sphere) span 0.180 × 0.070 m; toe ahead of ankle 0.125 m, heel behind 0.055 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1165 m (→ yaw-axis spacing 0.233 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1165 m, z = -0.1332 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1185 m (→ foot-centre spacing at q=0 ≈ 0.237 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 7.186 kg; shank+foot = 2.614 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = 0.020 m, 0.703 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -145.0 … 165.0 | 88.0 | 32.00 |
| hip_roll | `left_hip_roll_joint` | -30.0 … 170.0 | 139.0 | 20.00 |
| hip_yaw | `left_hip_yaw_joint` | -158.0 … 158.0 | 88.0 | 32.00 |
| knee | `left_knee_joint` | -5.0 … 165.0 | 139.0 | 20.00 |
| ankle_pitch | `left_ankle_pitch_joint` | -50.0 … 30.0 | 35.0 | 30.00 |
| ankle_roll | `left_ankle_roll_joint` | -15.0 … 15.0 | 35.0 | 30.00 |


####  `G1_23dof_rev1.0`
- File: https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/g1_description/g1_23dof_rev_1_0.urdf (parsed URDF, root `pelvis`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **32.11 kg** (31 links, 23 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch_joint[y] → left_hip_roll_joint[x tilt10] → left_hip_yaw_joint[z tilt10] → left_knee_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.3366 m (3-D 0.3409) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.3000 m (3-D 0.3000) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, -0.0176) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0526 m; hip-pitch→sole = 0.6892 m; root→sole = 0.7919 m — ESTIMATED (FK of file values)
  - foot collision primitives (sphere) span 0.180 × 0.070 m; toe ahead of ankle 0.125 m, heel behind 0.055 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1165 m (→ yaw-axis spacing 0.233 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1165 m, z = -0.1332 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1185 m (→ foot-centre spacing at q=0 ≈ 0.237 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 7.186 kg; shank+foot = 2.614 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = 0.016 m, 0.697 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -145.0 … 165.0 | 88.0 | 32.00 |
| hip_roll | `left_hip_roll_joint` | -30.0 … 170.0 | 139.0 | 20.00 |
| hip_yaw | `left_hip_yaw_joint` | -158.0 … 158.0 | 88.0 | 32.00 |
| knee | `left_knee_joint` | -5.0 … 165.0 | 139.0 | 20.00 |
| ankle_pitch | `left_ankle_pitch_joint` | -50.0 … 30.0 | 35.0 | 30.00 |
| ankle_roll | `left_ankle_roll_joint` | -15.0 … 15.0 | 35.0 | 30.00 |


####  `G1_23dof_mode10`
- File: https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/g1_description/g1_23dof_mode_10.urdf (parsed URDF, root `pelvis`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **32.11 kg** (30 links, 23 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch_joint[y] → left_hip_roll_joint[x tilt10] → left_hip_yaw_joint[z tilt10] → left_knee_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.3366 m (3-D 0.3409) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.3000 m (3-D 0.3000) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, -0.0176) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0526 m; hip-pitch→sole = 0.6892 m; root→sole = 0.7919 m — ESTIMATED (FK of file values)
  - foot collision primitives (sphere) span 0.180 × 0.070 m; toe ahead of ankle 0.125 m, heel behind 0.055 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1165 m (→ yaw-axis spacing 0.233 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1165 m, z = -0.1332 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1185 m (→ foot-centre spacing at q=0 ≈ 0.237 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 7.186 kg; shank+foot = 2.614 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = 0.016 m, 0.697 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -145.0 … 165.0 | 139.0 | 20.00 |
| hip_roll | `left_hip_roll_joint` | -30.0 … 170.0 | 139.0 | 20.00 |
| hip_yaw | `left_hip_yaw_joint` | -158.0 … 158.0 | 88.0 | 32.00 |
| knee | `left_knee_joint` | -5.0 … 165.0 | 139.0 | 20.00 |
| ankle_pitch | `left_ankle_pitch_joint` | -50.0 … 30.0 | 35.0 | 30.00 |
| ankle_roll | `left_ankle_roll_joint` | -15.0 … 15.0 | 35.0 | 30.00 |


####  `G1_29dof_mode15`
- File: https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/g1_description/g1_29dof_mode_15.urdf (parsed URDF, root `pelvis`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **33.74 kg** (38 links, 29 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch_joint[y] → left_hip_roll_joint[x tilt10] → left_hip_yaw_joint[z tilt10] → left_knee_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.3366 m (3-D 0.3409) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.3000 m (3-D 0.3000) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, -0.0176) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0526 m; hip-pitch→sole = 0.6892 m; root→sole = 0.7919 m — ESTIMATED (FK of file values)
  - foot collision primitives (sphere) span 0.180 × 0.070 m; toe ahead of ankle 0.125 m, heel behind 0.055 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1165 m (→ yaw-axis spacing 0.233 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1165 m, z = -0.1332 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1185 m (→ foot-centre spacing at q=0 ≈ 0.237 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 7.186 kg; shank+foot = 2.614 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = 0.022 m, 0.705 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -145.0 … 165.0 | 139.0 | 20.00 |
| hip_roll | `left_hip_roll_joint` | -30.0 … 170.0 | 139.0 | 20.00 |
| hip_yaw | `left_hip_yaw_joint` | -158.0 … 158.0 | 88.0 | 32.00 |
| knee | `left_knee_joint` | -5.0 … 165.0 | 139.0 | 20.00 |
| ankle_pitch | `left_ankle_pitch_joint` | -50.0 … 30.0 | 35.0 | 30.00 |
| ankle_roll | `left_ankle_roll_joint` | -15.0 … 15.0 | 35.0 | 30.00 |


####  `G1_23dof_deprecated`
- File: https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/g1_description/g1_23dof.urdf (parsed URDF, root `pelvis`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **34.13 kg** (33 links, 23 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch_joint[y] → left_hip_roll_joint[x tilt10] → left_hip_yaw_joint[z tilt10] → left_knee_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.3366 m (3-D 0.3409) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.3000 m (3-D 0.3000) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, -0.0176) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0526 m; hip-pitch→sole = 0.6892 m; root→sole = 0.7919 m — ESTIMATED (FK of file values)
  - foot collision primitives (sphere) span 0.180 × 0.070 m; toe ahead of ankle 0.125 m, heel behind 0.055 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1165 m (→ yaw-axis spacing 0.233 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1165 m, z = -0.1332 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1185 m (→ foot-centre spacing at q=0 ≈ 0.237 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 7.186 kg; shank+foot = 2.614 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = 0.015 m, 0.716 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -145.0 … 165.0 | 88.0 | 32.00 |
| hip_roll | `left_hip_roll_joint` | -30.0 … 170.0 | 88.0 | 32.00 |
| hip_yaw | `left_hip_yaw_joint` | -158.0 … 158.0 | 88.0 | 32.00 |
| knee | `left_knee_joint` | -5.0 … 165.0 | 139.0 | 20.00 |
| ankle_pitch | `left_ankle_pitch_joint` | -50.0 … 30.0 | 35.0 | 30.00 |
| ankle_roll | `left_ankle_roll_joint` | -15.0 … 15.0 | 35.0 | 30.00 |


####  `H1`
- File: https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/h1_description/urdf/h1.urdf (parsed URDF, root `pelvis`, foot `left_ankle_link`; FK at q = 0)
- Σ link masses = **59.34 kg** (25 links, 19 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_yaw_joint[z] → left_hip_roll_joint[x] → left_hip_pitch_joint[y] → left_knee_joint[y] → left_ankle_joint[y]
  - thigh (hip-pitch→knee) Δz = 0.4000 m (3-D 0.4000) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.4000 m (3-D 0.4000) — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0620 m; hip-pitch→sole = 0.8620 m; root→sole = 1.0362 m — ESTIMATED (FK of file values)
  - foot collision primitives (box) span 0.280 × 0.030 m; toe ahead of ankle 0.190 m, heel behind 0.090 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0875 m (→ yaw-axis spacing 0.175 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0875 m, z = -0.1742 m — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 14.182 kg; shank+foot = 3.549 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = 0.016 m, 0.957 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -179.9 … 145.0 | 200.0 | 23.00 |
| hip_roll | `left_hip_roll_joint` | -24.6 … 24.6 | 200.0 | 23.00 |
| hip_yaw | `left_hip_yaw_joint` | -24.6 … 24.6 | 200.0 | 23.00 |
| knee | `left_knee_joint` | -14.9 … 117.5 | 300.0 | 14.00 |
| ankle_pitch | `left_ankle_joint` | -49.8 … 29.8 | 40.0 | 9.00 |


####  `H1-2_handless`
- File: https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/h1_2_description/h1_2_handless.urdf (parsed URDF, root `pelvis`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **66.98 kg** (32 links, 27 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_yaw_joint[z] → left_hip_pitch_joint[y] → left_hip_roll_joint[x] → left_knee_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.4000 m (3-D 0.4000) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.4000 m (3-D 0.4000) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, -0.0200) m — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0875 m (→ yaw-axis spacing 0.175 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1630 m, z = -0.1632 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1630 m (→ foot-centre spacing at q=0 ≈ 0.326 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 15.399 kg; shank+foot = 4.688 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -179.9 … 143.2 | 200.0 | 23.00 |
| hip_roll | `left_hip_roll_joint` | -24.6 … 179.9 | 200.0 | 23.00 |
| hip_yaw | `left_hip_yaw_joint` | -24.6 … 24.6 | 200.0 | 23.00 |
| knee | `left_knee_joint` | -6.9 … 125.5 | 300.0 | 14.00 |
| ankle_pitch | `left_ankle_pitch_joint` | -51.4 … 30.0 | 60.0 | 9.00 |
| ankle_roll | `left_ankle_roll_joint` | -15.0 … 15.0 | 40.0 | 9.00 |


####  `R1`
- File: https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/r1_description/R1.urdf (parsed URDF, root `pelvis_link`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **28.84 kg** (40 links, 26 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch_joint[y tilt25] → left_hip_roll_joint[x] → left_hip_yaw_joint[z] → left_knee_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.2882 m (3-D 0.2910) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.3092 m (3-D 0.3103) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, 0.0000) m — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0883 m (→ yaw-axis spacing 0.177 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0889 m, z = -0.1573 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.0863 m (→ foot-centre spacing at q=0 ≈ 0.173 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 5.810 kg; shank+foot = 2.928 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -168.0 … 146.0 | 60.0 | 18.80 |
| hip_roll | `left_hip_roll_joint` | -60.0 … 100.0 | 60.0 | 18.80 |
| hip_yaw | `left_hip_yaw_joint` | -157.0 … 157.0 | 60.0 | 18.80 |
| knee | `left_knee_joint` | -10.0 … 139.0 | 60.0 | 18.80 |
| ankle_pitch | `left_ankle_pitch_joint` | -50.0 … 33.0 | 50.0 | 30.00 |
| ankle_roll | `left_ankle_roll_joint` | -15.0 … 15.0 | 50.0 | 30.00 |


####  `R1_mjcf(foot)`
- File: https://raw.githubusercontent.com/unitreerobotics/unitree_mujoco/main/unitree_robots/r1/R1_C%2B%2B.xml (parsed MJCF, root `pelvis`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **28.93 kg** (25 links, 24 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch_joint[y tilt25] → left_hip_roll_joint[x] → left_hip_yaw_joint[z] → left_knee_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.2882 m (3-D 0.2910) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.3092 m (3-D 0.3103) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, 0.0000) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0550 m; hip-pitch→sole = 0.6523 m; root→sole = 0.7426 m — ESTIMATED (FK of file values)
  - foot collision primitives (box,sphere) span 0.180 × 0.070 m; toe ahead of ankle 0.130 m, heel behind 0.050 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0883 m (→ yaw-axis spacing 0.177 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0889 m, z = -0.1573 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.0863 m (→ foot-centre spacing at q=0 ≈ 0.173 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 5.810 kg; shank+foot = 2.928 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = 0.036 m, 0.661 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -168.0 … 146.0 | 60.0 | n/a |
| hip_roll | `left_hip_roll_joint` | -60.0 … 100.0 | 60.0 | n/a |
| hip_yaw | `left_hip_yaw_joint` | -157.0 … 157.0 | 60.0 | n/a |
| knee | `left_knee_joint` | -10.0 … 139.0 | 60.0 | n/a |
| ankle_pitch | `left_ankle_pitch_joint` | -50.0 … 33.0 | 50.0 | n/a |
| ankle_roll | `left_ankle_roll_joint` | -15.0 … 15.0 | 50.0 | n/a |


####  `R1_AIR`
- File: https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/r1_air_description/R1_AIR.urdf (parsed URDF, root `pelvis_link`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **26.68 kg** (34 links, 20 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch_joint[y tilt25] → left_hip_roll_joint[x] → left_hip_yaw_joint[z] → left_knee_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.2882 m (3-D 0.2910) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.3092 m (3-D 0.3103) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, 0.0000) m — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0883 m (→ yaw-axis spacing 0.177 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0889 m, z = -0.1573 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.0863 m (→ foot-centre spacing at q=0 ≈ 0.173 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 5.810 kg; shank+foot = 2.928 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -168.0 … 146.0 | 60.0 | 18.80 |
| hip_roll | `left_hip_roll_joint` | -60.0 … 100.0 | 60.0 | 18.80 |
| hip_yaw | `left_hip_yaw_joint` | -157.0 … 157.0 | 60.0 | 18.80 |
| knee | `left_knee_joint` | -10.0 … 139.0 | 60.0 | 18.80 |
| ankle_pitch | `left_ankle_pitch_joint` | -50.0 … 33.0 | 50.0 | 30.00 |
| ankle_roll | `left_ankle_roll_joint` | -15.0 … 15.0 | 50.0 | 30.00 |


####  `H2`
- File: https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/h2_description/H2.urdf (parsed URDF, root `pelvis`, foot `left_ankle_pitch_link`; FK at q = 0)
- Σ link masses = **75.59 kg** (37 links, 31 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch_joint[y tilt30] → left_hip_roll_joint[x] → left_hip_yaw_joint[z] → left_knee_joint[y] → left_ankle_roll_joint[x] → left_ankle_pitch_joint[y]
  - thigh (hip-pitch→knee) Δz = 0.4415 m (3-D 0.4454) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.4966 m (3-D 0.5006) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0145, 0.0373, 0.0000) m — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1164 m (→ yaw-axis spacing 0.233 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1259 m, z = -0.0946 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1159 m (→ foot-centre spacing at q=0 ≈ 0.232 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 16.118 kg; shank+foot = 5.372 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -140.5 … 159.0 | 360.0 | 20.00 |
| hip_roll | `left_hip_roll_joint` | -26.8 … 124.3 | 360.0 | 20.00 |
| hip_yaw | `left_hip_yaw_joint` | -162.0 … 162.0 | 360.0 | 20.00 |
| knee | `left_knee_joint` | -5.0 … 145.0 | 360.0 | 20.00 |
| ankle_pitch | `left_ankle_pitch_joint` | -65.0 … 35.0 | 66.9 | 28.61 |
| ankle_roll | `left_ankle_roll_joint` | -20.0 … 17.0 | 19.0 | 100.70 |


####  `BHL`
- File: https://raw.githubusercontent.com/HybridRobotics/Berkeley-Humanoid-Lite-Assets/main/data/robots/berkeley_humanoid/berkeley_humanoid_lite/urdf/berkeley_humanoid_lite.urdf (parsed URDF, root `base`, foot `leg_left_ankle_roll`; FK at q = 0)
- Σ link masses = **16.33 kg** (27 links, 22 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): leg_left_hip_roll_joint[z tilt45] → leg_left_hip_yaw_joint[z tilt45] → leg_left_hip_pitch_joint[y] → leg_left_knee_pitch_joint[y] → leg_left_ankle_pitch_joint[y] → leg_left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.1500 m (3-D 0.1511) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.1600 m (3-D 0.1600) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0300, 0.0250, -0.0500) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.1000 m; hip-pitch→sole = 0.4100 m; root→sole = -0.0400 m — ESTIMATED (FK of file values)
  - foot collision primitives (box) span 0.220 × 0.072 m; toe ahead of ankle 0.146 m, heel behind 0.074 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0800 m (→ yaw-axis spacing 0.160 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0800 m, z = 0.5426 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.0570 m (→ foot-centre spacing at q=0 ≈ 0.114 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 4.090 kg; shank+foot = 1.467 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = -0.007 m, 0.442 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `leg_left_hip_pitch_joint` | -108.8 … 56.3 | 20.0 | 15.00 |
| hip_roll | `leg_left_hip_roll_joint` | -10.0 … 90.0 | 20.0 | 15.00 |
| hip_yaw | `leg_left_hip_yaw_joint` | -56.3 … 33.8 | 20.0 | 15.00 |
| knee | `leg_left_knee_pitch_joint` | -0.0 … 140.0 | 20.0 | 15.00 |
| ankle_pitch | `leg_left_ankle_pitch_joint` | -45.0 … 45.0 | 20.0 | 15.00 |
| ankle_roll | `leg_left_ankle_roll_joint` | -15.0 … 15.0 | 20.0 | 15.00 |


####  `BHL_biped`
- File: https://raw.githubusercontent.com/HybridRobotics/Berkeley-Humanoid-Lite-Assets/main/data/robots/berkeley_humanoid/berkeley_humanoid_lite/urdf/berkeley_humanoid_lite_biped.urdf (parsed URDF, root `base`, foot `leg_left_ankle_roll`; FK at q = 0)
- Σ link masses = **11.34 kg** (15 links, 12 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): leg_left_hip_roll_joint[z tilt45] → leg_left_hip_yaw_joint[z tilt45] → leg_left_hip_pitch_joint[y] → leg_left_knee_pitch_joint[y] → leg_left_ankle_pitch_joint[y] → leg_left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.1500 m (3-D 0.1511) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.1600 m (3-D 0.1600) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0300, 0.0250, -0.0500) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.1000 m; hip-pitch→sole = 0.4100 m; root→sole = -0.0400 m — ESTIMATED (FK of file values)
  - foot collision primitives (box) span 0.220 × 0.072 m; toe ahead of ankle 0.146 m, heel behind 0.074 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0800 m (→ yaw-axis spacing 0.160 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0800 m, z = 0.5426 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.0570 m (→ foot-centre spacing at q=0 ≈ 0.114 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 4.090 kg; shank+foot = 1.467 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = -0.010 m, 0.368 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `leg_left_hip_pitch_joint` | -108.8 … 56.3 | 20.0 | 15.00 |
| hip_roll | `leg_left_hip_roll_joint` | -10.0 … 90.0 | 20.0 | 15.00 |
| hip_yaw | `leg_left_hip_yaw_joint` | -56.3 … 33.8 | 20.0 | 15.00 |
| knee | `leg_left_knee_pitch_joint` | -0.0 … 140.0 | 20.0 | 15.00 |
| ankle_pitch | `leg_left_ankle_pitch_joint` | -45.0 … 45.0 | 20.0 | 15.00 |
| ankle_roll | `leg_left_ankle_roll_joint` | -15.0 … 15.0 | 20.0 | 15.00 |


####  `BerkeleyHumanoid2024`
- File: https://raw.githubusercontent.com/HybridRobotics/berkeley_humanoid_description/main/urdf/robot.urdf (parsed URDF, root `torso`, foot `ll_faa`; FK at q = 0)
- Σ link masses = **16.06 kg** (15 links, 12 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): LL_HR[x tilt45] → LL_HAA[z tilt45] → LL_HFE[y] → LL_KFE[y] → LL_FFE[y] → LL_FAA[x]
  - thigh (hip-pitch→knee) Δz = 0.2200 m (3-D 0.2322) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.1800 m (3-D 0.1800) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0175, -0.0000, -0.0000) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0627 m; hip-pitch→sole = 0.4627 m; root→sole = 0.5658 m — ESTIMATED (FK of file values)
  - foot collision primitives (box,cylinder) span 0.160 × 0.055 m; toe ahead of ankle 0.111 m, heel behind 0.049 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0700 m (→ yaw-axis spacing 0.140 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0700 m, z = -0.0571 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1600 m (→ foot-centre spacing at q=0 ≈ 0.320 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 5.339 kg; shank+foot = 0.956 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = 0.007 m, 0.478 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `LL_HFE` | -100.0 … 30.0 | 30.0 | 20.00 |
| hip_roll | `LL_HAA` | -35.0 … 35.0 | 20.0 | 23.00 |
| hip_yaw | `LL_HR` | -35.0 … 35.0 | 20.0 | 23.00 |
| knee | `LL_KFE` | 0.0 … 120.0 | 30.0 | 14.00 |
| ankle_pitch | `LL_FFE` | -30.0 … 40.0 | 20.0 | 20.00 |
| ankle_roll | `LL_FAA` | -30.0 … 30.0 | 5.0 | 42.00 |


####  `ToddlerBot2_2XC`
- File: https://raw.githubusercontent.com/hshi74/toddlerbot/main/toddlerbot/descriptions/toddlerbot_2xc/toddlerbot_2xc.urdf (parsed URDF, root `torso`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **3.50 kg** (91 links, 30 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch[y] → left_hip_roll[x] → left_hip_yaw_driven[z] → left_knee[y] → left_ankle_pitch[y] → left_ankle_roll[x]
  - thigh (hip-pitch→knee) Δz = 0.1015 m (3-D 0.1015) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.1100 m (3-D 0.1100) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (-0.0230, 0.0190, 0.0000) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0390 m; hip-pitch→sole = 0.2505 m; root→sole = 0.3151 m — ESTIMATED (FK of file values)
  - foot collision primitives (box) span 0.110 × 0.042 m; toe ahead of ankle 0.071 m, heel behind 0.039 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0370 m (→ yaw-axis spacing 0.074 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0370 m, z = -0.0886 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.0370 m (→ foot-centre spacing at q=0 ≈ 0.074 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 0.541 kg; shank+foot = 0.244 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = -0.020 m, 0.286 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch` | -135.0 … 105.0 | 100.0 | 100.00 |
| hip_roll | `left_hip_roll` | -45.0 … 90.0 | 100.0 | 100.00 |
| hip_yaw | `left_hip_yaw_driven` | -90.0 … 90.0 | 100.0 | 100.00 |
| knee | `left_knee` | -120.0 … 0.0 | 100.0 | 100.00 |
| ankle_pitch | `left_ankle_pitch` | -105.0 … 55.0 | 100.0 | 100.00 |
| ankle_roll | `left_ankle_roll` | -70.0 … 70.0 | 100.0 | 100.00 |


####  `ToddlerBot2_2XM`
- File: https://raw.githubusercontent.com/hshi74/toddlerbot/main/toddlerbot/descriptions/toddlerbot_2xm/toddlerbot_2xm.urdf (parsed URDF, root `torso`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **3.81 kg** (91 links, 30 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch[y] → left_hip_roll[x] → left_hip_yaw_driven[z] → left_knee[y] → left_ankle_pitch[y] → left_ankle_roll[x]
  - thigh (hip-pitch→knee) Δz = 0.1015 m (3-D 0.1015) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.1100 m (3-D 0.1100) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (-0.0230, 0.0190, 0.0000) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0390 m; hip-pitch→sole = 0.2505 m; root→sole = 0.3151 m — ESTIMATED (FK of file values)
  - foot collision primitives (box) span 0.110 × 0.042 m; toe ahead of ankle 0.071 m, heel behind 0.039 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0370 m (→ yaw-axis spacing 0.074 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0370 m, z = -0.0886 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.0370 m (→ foot-centre spacing at q=0 ≈ 0.074 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 0.619 kg; shank+foot = 0.244 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = -0.022 m, 0.287 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch` | -135.0 … 45.0 | 100.0 | 100.00 |
| hip_roll | `left_hip_roll` | -45.0 … 90.0 | 100.0 | 100.00 |
| hip_yaw | `left_hip_yaw_driven` | -90.0 … 90.0 | 100.0 | 100.00 |
| knee | `left_knee` | -120.0 … 0.0 | 100.0 | 100.00 |
| ankle_pitch | `left_ankle_pitch` | -105.0 … 55.0 | 100.0 | 100.00 |
| ankle_roll | `left_ankle_roll` | -70.0 … 70.0 | 100.0 | 100.00 |


####  `Poppy`
- File: https://raw.githubusercontent.com/poppy-project/poppy-humanoid/master/hardware/URDF/robots/Poppy_Humanoid.URDF (parsed URDF, root `pelvis`, foot `l_foot`; FK at q = 0)
- Σ link masses = **2.61 kg** (26 links, 25 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): l_hip_x[y] → l_hip_z[z] → l_hip_y[x] → l_knee_y[x] → l_ankle_y[x]
  - thigh (hip-pitch→knee) Δz = 0.1820 m (3-D 0.1820) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.1800 m (3-D 0.1800) — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0050 m (→ yaw-axis spacing 0.010 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0000 m, z = 0.0000 m — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 0.445 kg; shank+foot = 0.162 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `l_hip_y` | -104.0 … 84.0 | 7.3 | 8.20 |
| hip_roll | `l_hip_x` | -30.0 … 28.5 | 3.1 | 7.00 |
| hip_yaw | `l_hip_z` | -25.0 … 90.0 | 3.1 | 7.00 |
| knee | `l_knee_y` | -3.5 … 134.0 | 3.1 | 7.00 |
| ankle_pitch | `l_ankle_y` | -45.0 … 45.0 | 3.1 | 7.00 |


####  `BoosterT1_23dof`
- File: https://raw.githubusercontent.com/BoosterRobotics/booster_assets/main/robots/T1/T1_23dof.urdf (parsed URDF, root `trunk`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **31.74 kg** (25 links, 23 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch_joint[y] → left_hip_roll_joint[x] → left_hip_yaw_joint[z] → left_knee_pitch_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.2359 m (3-D 0.2363) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.2800 m (3-D 0.2800) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0003, -0.0120) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0553 m; hip-pitch→sole = 0.5711 m; root→sole = 0.6866 m — ESTIMATED (FK of file values)
  - foot collision primitives (box) span 0.225 × 0.100 m; toe ahead of ankle 0.123 m, heel behind 0.102 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1060 m (→ yaw-axis spacing 0.212 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1060 m, z = -0.1355 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1062 m (→ foot-centre spacing at q=0 ≈ 0.212 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 6.150 kg; shank+foot = 2.578 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = 0.056 m, 0.616 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -170.0 … 125.5 | 98.8 | 15.29 |
| hip_roll | `left_hip_roll_joint` | -20.8 … 88.0 | 68.0 | 14.66 |
| hip_yaw | `left_hip_yaw_joint` | -61.7 … 60.8 | 68.0 | 14.66 |
| knee | `left_knee_pitch_joint` | 0.0 … 122.9 | 130.5 | 14.76 |
| ankle_pitch | `left_ankle_pitch_joint` | -49.8 … 20.1 | 73.1 | 12.57 |
| ankle_roll | `left_ankle_roll_joint` | -25.2 … 25.2 | 17.2 | 12.57 |


####  `BoosterK1_22dof`
- File: https://raw.githubusercontent.com/BoosterRobotics/booster_assets/main/robots/K1/K1_22dof.urdf (parsed URDF, root `trunk`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **19.67 kg** (25 links, 22 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch_joint[y] → left_hip_roll_joint[x] → left_hip_yaw_joint[z] → left_knee_pitch_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.1915 m (3-D 0.1915) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.2452 m (3-D 0.2452) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, 0.0000) m — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0960 m (→ yaw-axis spacing 0.192 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0960 m, z = -0.1030 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.0962 m (→ foot-centre spacing at q=0 ≈ 0.192 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 4.503 kg; shank+foot = 2.033 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -169.5 … 127.5 | 68.0 | 14.66 |
| hip_roll | `left_hip_roll_joint` | -21.5 … 88.0 | 43.0 | 12.57 |
| hip_yaw | `left_hip_yaw_joint` | -58.0 … 58.0 | 38.3 | 17.59 |
| knee | `left_knee_pitch_joint` | 0.0 … 133.0 | 112.0 | 12.57 |
| ankle_pitch | `left_ankle_pitch_joint` | -49.8 … 19.8 | 38.3 | 17.59 |
| ankle_roll | `left_ankle_roll_joint` | -19.8 … 19.8 | 38.3 | 17.59 |


####  `BoosterK1_parallel(foot)`
- File: https://raw.githubusercontent.com/BoosterRobotics/booster_assets/main/robots/K1/K1_22dof_parallel.xml (parsed MJCF, root `trunk`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **19.87 kg** (33 links, 30 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch_joint[y] → left_hip_roll_joint[x] → left_hip_yaw_joint[z] → left_knee_pitch_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.1915 m (3-D 0.1915) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.2452 m (3-D 0.2452) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, 0.0000) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0380 m; hip-pitch→sole = 0.4747 m; root→sole = 0.5517 m — ESTIMATED (FK of file values)
  - foot collision primitives (box) span 0.180 × 0.070 m; toe ahead of ankle 0.116 m, heel behind 0.064 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0960 m (→ yaw-axis spacing 0.192 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0960 m, z = -0.1030 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.0962 m (→ foot-centre spacing at q=0 ≈ 0.192 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 4.603 kg; shank+foot = 2.133 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = -0.000 m, 0.478 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -169.5 … 127.5 | 68.0 | n/a |
| hip_roll | `left_hip_roll_joint` | -21.5 … 88.0 | 43.0 | n/a |
| hip_yaw | `left_hip_yaw_joint` | -58.0 … 58.0 | 38.3 | n/a |
| knee | `left_knee_pitch_joint` | 0.0 … 133.0 | 112.0 | n/a |
| ankle_pitch | `left_ankle_pitch_joint` | -49.8 … 19.8 | n/a | n/a |
| ankle_roll | `left_ankle_roll_joint` | -19.8 … 19.8 | n/a | n/a |


####  `KBot`
- File: https://raw.githubusercontent.com/kscalelabs/kbot-models/master/kbot/robot.urdf (parsed URDF, root `base`, foot `LFootBushing_GPF_1517_12`; FK at q = 0)
- Σ link masses = **36.72 kg** (23 links, 20 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): dof_left_hip_pitch_04[y] → dof_left_hip_roll_03[x] → dof_left_hip_yaw_03[z] → dof_left_knee_04[y] → dof_left_ankle_02[y]
  - thigh (hip-pitch→knee) Δz = 0.3850 m (3-D 0.3887) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.2900 m (3-D 0.2915) — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1270 m (→ yaw-axis spacing 0.254 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1270 m, z = -0.1038 m — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 7.590 kg; shank+foot = 2.294 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `dof_left_hip_pitch_04` | -60.0 … 127.0 | 120.0 | 17.49 |
| hip_roll | `dof_left_hip_roll_03` | -12.0 … 130.0 | 60.0 | 18.85 |
| hip_yaw | `dof_left_hip_yaw_03` | -90.0 … 90.0 | 60.0 | 18.85 |
| knee | `dof_left_knee_04` | 0.0 … 155.0 | 120.0 | 17.49 |
| ankle_pitch | `dof_left_ankle_02` | -65.0 … 15.0 | 17.0 | 37.70 |


####  `KBot_fullcoll(foot)`
- File: https://raw.githubusercontent.com/kscalelabs/kbot-models/master/kbot-full-collisions/robot.mjcf (parsed MJCF, root `base`, foot `LFootBushing_GPF_1517_12`; FK at q = 0)
- Σ link masses = **36.71 kg** (23 links, 20 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): dof_left_hip_pitch_04[y] → dof_left_hip_roll_03[x] → dof_left_hip_yaw_03[z] → dof_left_knee_04[y] → dof_left_ankle_02[y]
  - thigh (hip-pitch→knee) Δz = 0.3850 m (3-D 0.3887) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.2900 m (3-D 0.2915) — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0580 m; hip-pitch→sole = 0.7330 m; root→sole = 0.8068 m — ESTIMATED (FK of file values)
  - foot collision primitives (capsule) span 0.210 × 0.072 m; toe ahead of ankle 0.133 m, heel behind 0.076 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1270 m (→ yaw-axis spacing 0.254 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1270 m, z = -0.1038 m — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 7.590 kg; shank+foot = 2.294 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = -0.002 m, 0.750 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `dof_left_hip_pitch_04` | -60.0 … 127.0 | 120.0 | n/a |
| hip_roll | `dof_left_hip_roll_03` | -12.0 … 130.0 | 60.0 | n/a |
| hip_yaw | `dof_left_hip_yaw_03` | -90.0 … 90.0 | 60.0 | n/a |
| knee | `dof_left_knee_04` | 0.0 … 155.0 | 120.0 | n/a |
| ankle_pitch | `dof_left_ankle_02` | -65.0 … 15.0 | 17.0 | n/a |


####  `FourierN1`
- File: https://raw.githubusercontent.com/FFTAI/Wiki-GRx-Models/FourierN1/N1/urdf/N1_raw.urdf (parsed URDF, root `base_link`, foot `left_foot_pitch_link`; FK at q = 0)
- Σ link masses = **39.73 kg** (29 links, 23 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch_joint[y tilt15] → left_hip_roll_joint[x] → left_hip_yaw_joint[z] → left_knee_pitch_joint[y] → left_ankle_roll_joint[x] → left_ankle_pitch_joint[y]
  - thigh (hip-pitch→knee) Δz = 0.3076 m (3-D 0.3154) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.2800 m (3-D 0.2800) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, 0.0000) m — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1200 m (→ yaw-axis spacing 0.240 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1200 m, z = -0.0860 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1200 m (→ foot-centre spacing at q=0 ≈ 0.240 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 8.881 kg; shank+foot = 2.851 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -149.9 … 149.9 | 95.0 | 12.36 |
| hip_roll | `left_hip_roll_joint` | -15.0 … 90.0 | 54.0 | 14.74 |
| hip_yaw | `left_hip_yaw_joint` | -149.9 … 149.9 | 54.0 | 14.74 |
| knee | `left_knee_pitch_joint` | -5.0 … 135.0 | 95.0 | 12.36 |
| ankle_pitch | `left_ankle_pitch_joint` | -45.0 … 45.0 | 30.0 | 16.75 |
| ankle_roll | `left_ankle_roll_joint` | -25.0 … 25.0 | 30.0 | 16.75 |


####  `NoetixN2`
- File: https://raw.githubusercontent.com/Noetix-Robotics/noetix_n2_gym/main/resources/robots/N2/urdf/N2.urdf (parsed URDF, root `base_link`, foot `L_leg_ankle_link`; FK at q = 0)
- Σ link masses = **33.16 kg** (21 links, 18 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): L_leg_hip_yaw_joint[x tilt45] → L_leg_hip_roll_joint[z tilt45] → L_leg_hip_pitch_joint[y] → L_leg_knee_joint[y] → L_leg_ankle_joint[y]
  - thigh (hip-pitch→knee) Δz = 0.2000 m (3-D 0.2000) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.2596 m (3-D 0.2600) — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0912 m (→ yaw-axis spacing 0.182 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0912 m, z = -0.1459 m — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 8.771 kg; shank+foot = 2.262 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `L_leg_hip_pitch_joint` | -90.0 … 44.7 | 150.0 | 14.00 |
| hip_roll | `L_leg_hip_roll_joint` | -37.2 … 57.3 | 90.0 | 14.00 |
| hip_yaw | `L_leg_hip_yaw_joint` | -37.2 … 57.3 | 90.0 | 14.00 |
| knee | `L_leg_knee_joint` | 0.0 … 126.1 | 150.0 | 14.00 |
| ankle_pitch | `L_leg_ankle_joint` | -57.3 … 43.0 | 70.0 | 14.00 |


####  `RobotisOP3(menagerie)`
- File: https://raw.githubusercontent.com/google-deepmind/mujoco_menagerie/main/robotis_op3/op3.xml (parsed MJCF, root `body_link`, foot `l_ank_roll_link`; FK at q = 0)
- Σ link masses = **3.15 kg** (21 links, 20 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): l_hip_yaw[z] → l_hip_roll[x] → l_hip_pitch[y] → l_knee[y] → l_ank_pitch[y] → l_ank_roll[x]
  - thigh (hip-pitch→knee) Δz = 0.1101 m (3-D 0.1101) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.1100 m (3-D 0.1100) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (-0.0241, -0.0190, 0.0000) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0305 m; hip-pitch→sole = 0.2506 m; root→sole = 0.2792 m — ESTIMATED (FK of file values)
  - foot collision primitives (box) span 0.127 × 0.078 m; toe ahead of ankle 0.063 m, heel behind 0.064 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0350 m (→ yaw-axis spacing 0.070 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0350 m, z = -0.0285 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.0350 m (→ foot-centre spacing at q=0 ≈ 0.070 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 0.594 kg; shank+foot = 0.288 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = -0.011 m, 0.274 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `l_hip_pitch` | n/a … n/a | 3.1 | n/a |
| hip_roll | `l_hip_roll` | n/a … n/a | 3.1 | n/a |
| hip_yaw | `l_hip_yaw` | n/a … n/a | 3.1 | n/a |
| knee | `l_knee` | n/a … n/a | 3.1 | n/a |
| ankle_pitch | `l_ank_pitch` | n/a … n/a | 3.1 | n/a |
| ankle_roll | `l_ank_roll` | n/a … n/a | 3.1 | n/a |


####  `Asimov1`
- File: https://raw.githubusercontent.com/menloresearch/asimov-1/main/sim-model/urdf/asimov_1.urdf (parsed URDF, root `pelvis_link`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **32.22 kg** (26 links, 23 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch_joint[y] → left_hip_roll_joint[x] → left_hip_yaw_joint[z] → left_knee_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.2700 m (3-D 0.2730) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.2723 m (3-D 0.2723) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (-0.0015, 0.0000, -0.0100) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0440 m; hip-pitch→sole = 0.5863 m; root→sole = 0.6303 m — ESTIMATED (FK of file values)
  - foot collision primitives (sphere) span 0.177 × 0.066 m; toe ahead of ankle 0.126 m, heel behind 0.052 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1145 m (→ yaw-axis spacing 0.229 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1075 m, z = -0.0440 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1075 m (→ foot-centre spacing at q=0 ≈ 0.215 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 6.446 kg; shank+foot = 3.109 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = -0.057 m, 0.642 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -120.0 … 57.3 | 45.0 | 12.57 |
| hip_roll | `left_hip_roll_joint` | -45.0 … 45.0 | 45.0 | 3.98 |
| hip_yaw | `left_hip_yaw_joint` | -45.0 … 45.0 | 28.0 | 5.45 |
| knee | `left_knee_joint` | 0.0 … 85.9 | 45.0 | 12.25 |
| ankle_pitch | `left_ankle_pitch_joint` | -20.1 … 20.1 | 40.0 | 9.32 |
| ankle_roll | `left_ankle_roll_joint` | -5.7 … 5.7 | 17.0 | 9.32 |


####  `Asimov_v0_legs`
- File: https://raw.githubusercontent.com/menloresearch/asimov-v0/main/sim-model/xmls/asimov.xml (parsed MJCF, root `pelvis_link`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **15.88 kg** (15 links, 14 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch_joint[y tilt45] → left_hip_roll_joint[x] → left_hip_yaw_joint[z] → left_knee_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.2989 m (3-D 0.3033) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.2947 m (3-D 0.2947) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (-0.0015, 0.0000, -0.0100) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0420 m; hip-pitch→sole = 0.6356 m; root→sole = 0.7410 m — ESTIMATED (FK of file values)
  - foot collision primitives (capsule) span 0.145 × 0.090 m; toe ahead of ankle 0.098 m, heel behind 0.046 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1078 m (→ yaw-axis spacing 0.216 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1078 m, z = -0.1567 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1078 m (→ foot-centre spacing at q=0 ≈ 0.216 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 6.286 kg; shank+foot = 3.247 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = 0.009 m, 0.391 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -120.0 … 57.3 | n/a | n/a |
| hip_roll | `left_hip_roll_joint` | -45.0 … 45.0 | n/a | n/a |
| hip_yaw | `left_hip_yaw_joint` | -45.0 … 45.0 | n/a | n/a |
| knee | `left_knee_joint` | 0.0 … 85.9 | n/a | n/a |
| ankle_pitch | `left_ankle_pitch_joint` | -20.0 … 28.6 | n/a | n/a |
| ankle_roll | `left_ankle_roll_joint` | -5.7 … 5.7 | n/a | n/a |


####  `PND_AdamLite(menagerie)`
- File: https://raw.githubusercontent.com/google-deepmind/mujoco_menagerie/main/pndbotics_adam_lite/adam_lite.xml (parsed MJCF, root `pelvis`, foot `toeLeft`; FK at q = 0)
- Σ link masses = **58.19 kg** (26 links, 25 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): hipPitch_Left[y tilt35] → hipRoll_Left[x] → hipYaw_Left[z] → kneePitch_Left[y] → anklePitch_Left[y] → ankleRoll_Left[x]
  - thigh (hip-pitch→knee) Δz = 0.4611 m (3-D 0.4619) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.3700 m (3-D 0.3700) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, 0.0000) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0650 m; hip-pitch→sole = 0.8961 m; root→sole = 0.9293 m — ESTIMATED (FK of file values)
  - foot collision primitives (cylinder) span 0.220 × 0.080 m; toe ahead of ankle 0.155 m, heel behind 0.065 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1527 m (→ yaw-axis spacing 0.305 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1527 m, z = -0.0728 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1172 m (→ foot-centre spacing at q=0 ≈ 0.234 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 12.798 kg; shank+foot = 2.705 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = 0.003 m, 0.907 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `hipPitch_Left` | -119.7 … 119.7 | 230.0 | n/a |
| hip_roll | `hipRoll_Left` | -44.7 … 90.0 | 160.0 | n/a |
| hip_yaw | `hipYaw_Left` | -44.7 … 44.7 | 105.0 | n/a |
| knee | `kneePitch_Left` | -5.2 … 137.5 | 230.0 | n/a |
| ankle_pitch | `anklePitch_Left` | -57.3 … 20.1 | 40.0 | n/a |
| ankle_roll | `ankleRoll_Left` | -20.0 … 20.0 | 12.0 | n/a |


####  `EngineAI_PM01_EDU`
- File: https://raw.githubusercontent.com/engineai-robotics/engineai_robotics_native_sdk/main/assets/resource/robot/pm01_edu/urdf/serial_pm01_edu.urdf (parsed URDF, root `LINK_BASE`, foot `LINK_FOOT_L`; FK at q = 0)
- Σ link masses = **40.92 kg** (29 links, 24 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): J00_HIP_PITCH_L[y tilt15] → J01_HIP_ROLL_L[x] → J02_HIP_YAW_L[z] → J03_KNEE_PITCH_L[y] → J04_ANKLE_PITCH_L[y] → J05_ANKLE_ROLL_L[x]
  - thigh (hip-pitch→knee) Δz = 0.3358 m (3-D 0.3393) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.3630 m (3-D 0.3640) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, -0.0150) m — ESTIMATED (FK of file values)
  - foot collision = none (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1239 m (→ yaw-axis spacing 0.248 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1255 m, z = -0.0744 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1243 m (→ foot-centre spacing at q=0 ≈ 0.249 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 9.306 kg; shank+foot = 5.129 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `J00_HIP_PITCH_L` | -180.0 … 140.0 | 164.0 | 26.30 |
| hip_roll | `J01_HIP_ROLL_L` | -25.0 … 120.0 | 164.0 | 26.30 |
| hip_yaw | `J02_HIP_YAW_L` | -90.0 … 230.0 | 61.0 | 35.20 |
| knee | `J03_KNEE_PITCH_L` | -20.0 … 137.0 | 164.0 | 26.30 |
| ankle_pitch | `J04_ANKLE_PITCH_L` | -39.0 … 41.5 | 61.0 | 35.20 |
| ankle_roll | `J05_ANKLE_ROLL_L` | -15.0 … 15.0 | 61.0 | 35.20 |


####  `DukeHumanoidV1`
- File: https://raw.githubusercontent.com/generalroboticslab/legged_env/master/assets/urdf/v6biped_urdf_v4_aug29/v6biped_urdf_v4_squarefoot_aug29.urdf (parsed URDF, root `base_link`, foot `link_09_L_foot_square_COLLISION_1`; FK at q = 0)
- Σ link masses = **29.64 kg** (19 links, 10 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): joint_01_L_hip_z[z] → joint_02_L_hip_y[y] → joint_03_L_hip_x[x] → joint_07_L_shank_link_main[y] → joint_09_L_foot[y]
  - thigh (hip-pitch→knee) Δz = 0.2810 m (3-D 0.2897) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.2350 m (3-D 0.2351) — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0900 m (→ yaw-axis spacing 0.180 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0910 m, z = -0.0870 m — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 10.010 kg; shank+foot = 0.988 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `joint_02_L_hip_y` | -90.0 … 90.0 | 90.0 | 12.00 |
| hip_roll | `joint_03_L_hip_x` | -36.0 … 36.0 | 81.0 | 13.33 |
| hip_yaw | `joint_01_L_hip_z` | -90.0 … 90.0 | 81.0 | 13.33 |
| knee | `joint_07_L_shank_link_main` | -5.0 … 100.0 | 81.0 | 13.33 |
| ankle_pitch | `joint_09_L_foot` | -50.0 … 50.0 | 45.0 | 10.67 |


####  `AgiBotX1`
- File: https://raw.githubusercontent.com/AgibotTech/agibot_x1_train/main/resources/robots/x1/urdf/x1.urdf (parsed URDF, root `base_link`, foot `left_ankle_roll`; FK at q = 0)
- Σ link masses = **35.32 kg** (58 links, 12 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch_joint[y tilt45] → left_hip_roll_joint[x] → left_hip_yaw_joint[z] → left_knee_pitch_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.2677 m (3-D 0.2678) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.3049 m (3-D 0.3068) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, 0.0000) m — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1339 m (→ yaw-axis spacing 0.268 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1339 m, z = -0.0538 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1338 m (→ foot-centre spacing at q=0 ≈ 0.268 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 7.034 kg; shank+foot = 2.338 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -179.9 … 179.9 | 150.0 | 8.00 |
| hip_roll | `left_hip_roll_joint` | -179.9 … 179.9 | 150.0 | 8.00 |
| hip_yaw | `left_hip_yaw_joint` | -179.9 … 179.9 | 50.0 | 24.00 |
| knee | `left_knee_pitch_joint` | -179.9 … 179.9 | 150.0 | 8.00 |
| ankle_pitch | `left_ankle_pitch_joint` | -179.9 … 179.9 | 80.0 | 10.00 |
| ankle_roll | `left_ankle_roll_joint` | -179.9 … 179.9 | 80.0 | 10.00 |


####  `HighTorque_PiPlus`
- File: https://raw.githubusercontent.com/HighTorque-Robotics/HT_Robot_URDF/main/pi_plus_24dof/urdf/pi_plus_24dof.urdf (parsed URDF, root `base_link`, foot `l_ankle_roll_link`; FK at q = 0)
- Σ link masses = **11.00 kg** (25 links, 24 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): l_hip_pitch_joint[y] → l_hip_roll_joint[x] → l_thigh_joint[z] → l_calf_joint[y] → l_ankle_pitch_joint[y] → l_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.1424 m (3-D 0.1464) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.1400 m (3-D 0.1400) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0510, 0.0000, 0.0000) m — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0815 m (→ yaw-axis spacing 0.163 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0815 m, z = -0.0435 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.0815 m (→ foot-centre spacing at q=0 ≈ 0.163 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 2.584 kg; shank+foot = 1.591 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `l_hip_pitch_joint` | -178.8 … 168.4 | 20.0 | 5.45 |
| hip_roll | `l_hip_roll_joint` | -17.8 … 179.9 | 20.0 | 5.45 |
| hip_yaw | `l_thigh_joint` | -164.4 … 164.4 | 20.0 | 5.45 |
| knee | `l_calf_joint` | -142.7 … 142.7 | 20.0 | 5.45 |
| ankle_pitch | `l_ankle_pitch_joint` | -55.6 … 52.7 | 20.0 | 5.45 |
| ankle_roll | `l_ankle_roll_joint` | -44.7 … 44.7 | 20.0 | 5.45 |


####  `HighTorque_MiniHi`
- File: https://raw.githubusercontent.com/HighTorque-Robotics/HT_Robot_URDF/main/hi_25dof/urdf/hi_25dof.urdf (parsed URDF, root `base_link`, foot `l_ankle_roll_link`; FK at q = 0)
- Σ link masses = **18.32 kg** (27 links, 25 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): l_hip_pitch_joint[y] → l_hip_roll_joint[x] → l_hip_thigh_joint[z] → l_hip_calf_joint[y] → l_ankle_pitch_joint[y] → l_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.1920 m (3-D 0.2057) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.1994 m (3-D 0.1995) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, 0.0000) m — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0995 m (→ yaw-axis spacing 0.199 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0995 m, z = -0.0400 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.0995 m (→ foot-centre spacing at q=0 ≈ 0.199 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 3.994 kg; shank+foot = 2.298 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `l_hip_pitch_joint` | -174.0 … 174.0 | 32.4 | 5.55 |
| hip_roll | `l_hip_roll_joint` | -26.0 … 150.0 | 32.4 | 5.55 |
| hip_yaw | `l_hip_thigh_joint` | -45.0 … 45.0 | 32.4 | 5.55 |
| knee | `l_hip_calf_joint` | -90.0 … 120.0 | 32.4 | 5.55 |
| ankle_pitch | `l_ankle_pitch_joint` | -52.0 … 45.0 | 14.4 | 5.45 |
| ankle_roll | `l_ankle_roll_joint` | -21.5 … 21.5 | 14.4 | 5.45 |


####  `HighTorque_Pi12`
- File: https://raw.githubusercontent.com/HighTorque-Robotics/HT_Robot_URDF/main/pi_12dof/urdf/pi_12dof.urdf (parsed URDF, root `base_link`, foot `l_ankle_roll_link`; FK at q = 0)
- Σ link masses = **7.11 kg** (13 links, 12 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): 07_l_hip_pitch_joint[y] → 08_l_hip_roll_joint[x] → 09_l_thigh_joint[z] → 10_l_calf_joint[y] → 11_l_ankle_pitch_joint[y] → 12_l_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.1395 m (3-D 0.1506) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.1400 m (3-D 0.1400) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0752, 0.0000, 0.0000) m — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0801 m (→ yaw-axis spacing 0.160 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0801 m, z = -0.0330 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.0801 m (→ foot-centre spacing at q=0 ≈ 0.160 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 2.584 kg; shank+foot = 1.591 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `07_l_hip_pitch_joint` | -85.9 … 85.9 | 20.0 | 5.45 |
| hip_roll | `08_l_hip_roll_joint` | -21.8 … 68.8 | 20.0 | 5.45 |
| hip_yaw | `09_l_thigh_joint` | -57.3 … 57.3 | 20.0 | 5.45 |
| knee | `10_l_calf_joint` | 0.0 … 126.1 | 20.0 | 5.45 |
| ankle_pitch | `11_l_ankle_pitch_joint` | -45.8 … 45.8 | 20.0 | 5.45 |
| ankle_roll | `12_l_ankle_roll_joint` | -34.4 … 34.4 | 20.0 | 5.45 |


####  `Roboparty_RobotoOrigin_V2`
- File: https://raw.githubusercontent.com/Roboparty/roboto_origin/main/modules/rpo_hardware/V2.0/roboto_origin_mechanic/03_URDF/urdf/roboto_origin.urdf (parsed URDF, root `base_link`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **33.76 kg** (24 links, 23 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_thigh_yaw_joint[z tilt30] → left_thigh_roll_joint[x tilt30] → left_thigh_pitch_joint[y] → left_knee_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.2500 m (3-D 0.2500) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.3000 m (3-D 0.3007) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, 0.0000) m — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0725 m (→ yaw-axis spacing 0.145 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0725 m, z = -0.1241 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.0725 m (→ foot-centre spacing at q=0 ≈ 0.145 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 7.848 kg; shank+foot = 2.121 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_thigh_pitch_joint` | -90.0 … 90.0 | 80.0 | 10.47 |
| hip_roll | `left_thigh_roll_joint` | -11.5 … 57.3 | 80.0 | 10.47 |
| hip_yaw | `left_thigh_yaw_joint` | -57.3 … 11.5 | 80.0 | 10.47 |
| knee | `left_knee_joint` | -11.5 … 143.2 | 80.0 | 10.47 |
| ankle_pitch | `left_ankle_pitch_joint` | -34.4 … 34.4 | 18.0 | 3.77 |
| ankle_roll | `left_ankle_roll_joint` | -28.6 … 28.6 | 18.0 | 3.77 |


####  `AgiBotX2_EDU(mjcf)`
- File: https://raw.githubusercontent.com/AgibotTech/agibot_x2_urdf/main/X2_URDF-v1.4.0/X2-EDU.xml (parsed MJCF, root `pelvis`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **41.20 kg** (30 links, 29 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch_joint[y] → left_hip_roll_joint[x] → left_hip_yaw_joint[z] → left_knee_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.3200 m (3-D 0.3268) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.2820 m (3-D 0.2822) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (-0.0034, 0.0000, 0.0000) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0730 m; hip-pitch→sole = 0.6750 m; root→sole = 0.6750 m — ESTIMATED (FK of file values)
  - foot collision primitives (sphere) span 0.214 × 0.130 m; toe ahead of ankle 0.141 m, heel behind 0.073 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1371 m (→ yaw-axis spacing 0.274 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1371 m, z = 0.0000 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1372 m (→ foot-centre spacing at q=0 ≈ 0.274 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 8.549 kg; shank+foot = 3.660 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = -0.002 m, 0.687 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -155.0 … 146.5 | 120.0 | n/a |
| hip_roll | `left_hip_roll_joint` | -13.5 … 166.5 | 120.0 | n/a |
| hip_yaw | `left_hip_yaw_joint` | -106.5 … 206.5 | 120.0 | n/a |
| knee | `left_knee_joint` | 0.0 … 138.0 | 120.0 | n/a |
| ankle_pitch | `left_ankle_pitch_joint` | -46.0 … 26.0 | 60.0 | n/a |
| ankle_roll | `left_ankle_roll_joint` | -17.0 … 17.0 | 36.0 | n/a |


####  `AgiBotX2_EDU`
- File: https://raw.githubusercontent.com/AgibotTech/agibot_x2_urdf/main/X2_URDF-v1.4.0/X2-EDU.urdf (parsed URDF, root `pelvis`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **41.20 kg** (32 links, 29 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch_joint[y] → left_hip_roll_joint[x] → left_hip_yaw_joint[z] → left_knee_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.3200 m (3-D 0.3268) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.2820 m (3-D 0.2822) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (-0.0034, 0.0000, 0.0000) m — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1370 m (→ yaw-axis spacing 0.274 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1370 m, z = 0.0000 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1372 m (→ foot-centre spacing at q=0 ≈ 0.274 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 8.549 kg; shank+foot = 3.660 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch_joint` | -155.0 … 146.5 | 120.0 | 11.94 |
| hip_roll | `left_hip_roll_joint` | -13.5 … 166.5 | 120.0 | 11.94 |
| hip_yaw | `left_hip_yaw_joint` | -106.5 … 206.5 | 120.0 | 11.94 |
| knee | `left_knee_joint` | 0.0 … 138.0 | 120.0 | 11.94 |
| ankle_pitch | `left_ankle_pitch_joint` | -46.0 … 26.0 | 60.0 | 13.61 |
| ankle_roll | `left_ankle_roll_joint` | -17.0 … 17.0 | 36.0 | 14.66 |


####  `BRUCE`
- File: https://raw.githubusercontent.com/Westwood-Robotics/BRUCE_simulation_models/V1.6/Gazebo/urdf/bruce.urdf (parsed URDF, root `base_link`, foot `ankle_pitch_link_l`; FK at q = 0)
- Σ link masses = **4.45 kg** (17 links, 16 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): hip_yaw_l[z] → hip_pitch_l[y] → hip_roll_l[x] → knee_pitch_l[y] → ankle_pitch_l[y]
  - thigh (hip-pitch→knee) Δz = 0.2049 m (3-D 0.2049) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.1999 m (3-D 0.1999) — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0759 m (→ yaw-axis spacing 0.152 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0759 m, z = -0.0398 m — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 1.437 kg; shank+foot = 0.123 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `hip_pitch_l` | 0.0 … 0.0 | 0.0 | 0.00 |
| hip_roll | `hip_roll_l` | 0.0 … 0.0 | 0.0 | 0.00 |
| hip_yaw | `hip_yaw_l` | 0.0 … 0.0 | 0.0 | 0.00 |
| knee | `knee_pitch_l` | 0.0 … 0.0 | 0.0 | 0.00 |
| ankle_pitch | `ankle_pitch_l` | 0.0 … 0.0 | 0.0 | 0.00 |


####  `EngineAI_SA01`
- File: https://raw.githubusercontent.com/engineai-robotics/engineai_legged_gym/master/resources/robots/zq_humanoid/urdf/zq_sa01.urdf (parsed URDF, root `base_link`, foot `leg_l6_link`; FK at q = 0)
- Σ link masses = **33.11 kg** (13 links, 12 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): leg_l1_joint[x] → leg_l2_joint[z] → leg_l3_joint[y] → leg_l4_joint[y] → leg_l5_joint[y] → leg_l6_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.3000 m (3-D 0.3000) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.3700 m (3-D 0.3700) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, 0.0000) m — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0750 m (→ yaw-axis spacing 0.150 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0750 m, z = 0.0000 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.0751 m (→ foot-centre spacing at q=0 ≈ 0.150 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 11.469 kg; shank+foot = 4.079 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `leg_l3_joint` | -69.0 … 69.0 | 140.0 | 25.00 |
| hip_roll | `leg_l1_joint` | -30.0 … 30.0 | 140.0 | 25.00 |
| hip_yaw | `leg_l2_joint` | -17.2 … 17.2 | 140.0 | 25.00 |
| knee | `leg_l4_joint` | 0.0 … 129.9 | 140.0 | 25.00 |
| ankle_pitch | `leg_l5_joint` | -57.3 … 34.4 | 24.0 | 31.00 |
| ankle_roll | `leg_l6_joint` | -34.4 … 34.4 | 24.0 | 31.00 |


####  `PND_AdamLite_official`
- File: https://raw.githubusercontent.com/pndbotics/pnd_models/main/adam_lite/adam_lite.urdf (parsed URDF, root `pelvis`, foot `toeLeft`; FK at q = 0)
- Σ link masses = **58.48 kg** (27 links, 25 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): hipPitch_Left[y tilt35] → hipRoll_Left[x] → hipYaw_Left[z] → kneePitch_Left[y] → anklePitch_Left[y] → ankleRoll_Left[x]
  - thigh (hip-pitch→knee) Δz = 0.4611 m (3-D 0.4619) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.3700 m (3-D 0.3700) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, 0.0000) m — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1527 m (→ yaw-axis spacing 0.305 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1527 m, z = -0.0728 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1172 m (→ foot-centre spacing at q=0 ≈ 0.234 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 12.938 kg; shank+foot = 2.919 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `hipPitch_Left` | -124.0 … 124.0 | 230.0 | 15.00 |
| hip_roll | `hipRoll_Left` | -42.0 … 92.0 | 160.0 | 8.00 |
| hip_yaw | `hipYaw_Left` | -45.0 … 45.0 | 105.0 | 8.00 |
| knee | `kneePitch_Left` | 3.0 … 137.0 | 230.0 | 15.00 |
| ankle_pitch | `anklePitch_Left` | -57.3 … 20.1 | 40.0 | 20.00 |
| ankle_roll | `ankleRoll_Left` | -20.0 … 20.0 | 12.0 | 20.00 |


####  `Roboparty_rpo_description`
- File: https://raw.githubusercontent.com/Roboparty/rpo_description/main/urdf/rpo.urdf (parsed URDF, root `base_link`, foot `left_ankle_roll_link`; FK at q = 0)
- Σ link masses = **33.76 kg** (24 links, 23 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_thigh_yaw_joint[z tilt30] → left_thigh_roll_joint[x tilt30] → left_thigh_pitch_joint[y] → left_knee_joint[y] → left_ankle_pitch_joint[y] → left_ankle_roll_joint[x]
  - thigh (hip-pitch→knee) Δz = 0.2500 m (3-D 0.2500) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.3000 m (3-D 0.3007) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0000, 0.0000) m — ESTIMATED (FK of file values)
  - foot collision = mesh (no primitive → sole height not derivable without binary mesh) — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0725 m (→ yaw-axis spacing 0.145 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0725 m, z = -0.1241 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.0725 m (→ foot-centre spacing at q=0 ≈ 0.145 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 7.848 kg; shank+foot = 2.121 kg — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_thigh_pitch_joint` | -120.0 … 45.0 | 120.0 | 25.00 |
| hip_roll | `left_thigh_roll_joint` | -11.5 … 57.3 | 120.0 | 25.00 |
| hip_yaw | `left_thigh_yaw_joint` | -57.3 … 11.5 | 120.0 | 25.00 |
| knee | `left_knee_joint` | -11.5 … 143.2 | 120.0 | 25.00 |
| ankle_pitch | `left_ankle_pitch_joint` | -34.4 … 34.4 | 27.0 | 8.00 |
| ankle_roll | `left_ankle_roll_joint` | -28.6 … 28.6 | 27.0 | 8.00 |


####  `ToddlerBot_v1`
- File: https://raw.githubusercontent.com/hshi74/toddlerbot/v1.0.0/toddlerbot/descriptions/toddlerbot/toddlerbot.urdf (parsed URDF, root `torso`, foot `ank_roll_link`; FK at q = 0)
- Σ link masses = **3.36 kg** (67 links, 56 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): left_hip_pitch[y] → left_hip_roll[x] → left_hip_yaw_driven[z] → left_knee[y] → left_ank_pitch[y] → left_ank_roll[x]
  - thigh (hip-pitch→knee) Δz = 0.1430 m (3-D 0.1433) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.1000 m (3-D 0.1038) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (-0.0227, 0.0190, -0.0000) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0390 m; hip-pitch→sole = 0.2820 m; root→sole = 0.3361 m — ESTIMATED (FK of file values)
  - foot collision primitives (box) span 0.120 × 0.042 m; toe ahead of ankle 0.076 m, heel behind 0.044 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.0370 m (→ yaw-axis spacing 0.074 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.0370 m, z = -0.0781 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.0370 m (→ foot-centre spacing at q=0 ≈ 0.074 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 0.536 kg; shank+foot = 0.251 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = -0.004 m, 0.305 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `left_hip_pitch` | -90.0 … 135.0 | 1.0 | 20.00 |
| hip_roll | `left_hip_roll` | -45.0 … 45.0 | 1.0 | 20.00 |
| hip_yaw | `left_hip_yaw_driven` | -90.0 … 90.0 | 1.0 | 20.00 |
| knee | `left_knee` | -120.0 … 0.0 | 1.0 | 20.00 |
| ankle_pitch | `left_ank_pitch` | -100.0 … 45.0 | 1.0 | 20.00 |
| ankle_roll | `left_ank_roll` | -90.0 … 90.0 | 1.0 | 20.00 |


####  `BoosterT1_gym_serial`
- File: https://raw.githubusercontent.com/BoosterRobotics/booster_gym/main/resources/T1/T1_serial.urdf (parsed URDF, root `Trunk`, foot `left_foot_link`; FK at q = 0)
- Σ link masses = **31.61 kg** (24 links, 23 non-fixed joints) — VERIFIED (file) / sum ESTIMATED
- Left-leg joint chain (pelvis→foot, axis in root frame at q=0): Left_Hip_Pitch[y] → Left_Hip_Roll[x] → Left_Hip_Yaw[z] → Left_Knee_Pitch[y] → Left_Ankle_Pitch[y] → Left_Ankle_Roll[x]
  - thigh (hip-pitch→knee) Δz = 0.2359 m (3-D 0.2363) — ESTIMATED (FK of file values)
  - shin (knee→ankle-pitch) Δz = 0.2800 m (3-D 0.2800) — ESTIMATED (FK of file values)
  - ankle-pitch→ankle-roll offset = (0.0000, 0.0003, -0.0120) m — ESTIMATED (FK of file values)
  - ankle-pitch→sole = 0.0420 m; hip-pitch→sole = 0.5579 m; root→sole = 0.6734 m — ESTIMATED (FK of file values)
  - foot collision primitives (box) span 0.223 × 0.100 m; toe ahead of ankle 0.122 m, heel behind 0.102 m — ESTIMATED (FK of file values)
  - hip-yaw axis lateral offset |y| = 0.1060 m (→ yaw-axis spacing 0.212 m) — ESTIMATED (FK of file values)
  - hip-roll joint origin |y| = 0.1060 m, z = -0.1355 m — ESTIMATED (FK of file values)
  - ankle-roll joint |y| = 0.1062 m (→ foot-centre spacing at q=0 ≈ 0.212 m) — ESTIMATED (FK of file values)
  - one-leg mass (subtree of first hip link) = 6.060 kg; shank+foot = 2.488 kg — ESTIMATED (FK of file values)
  - whole-body COM at q=0: x = 0.056 m, 0.605 m above sole — ESTIMATED (FK of file values)

| role | joint | range (deg) | effort limit (N·m) | velocity limit (rad/s) |
|---|---|---|---|---|
| hip_pitch | `Left_Hip_Pitch` | -103.1 … 90.0 | 45.0 | 12.50 |
| hip_roll | `Left_Hip_Roll` | -11.5 … 90.0 | 30.0 | 10.90 |
| hip_yaw | `Left_Hip_Yaw` | -57.3 … 57.3 | 30.0 | 10.90 |
| knee | `Left_Knee_Pitch` | 0.0 … 134.1 | 60.0 | 11.70 |
| ankle_pitch | `Left_Ankle_Pitch` | -49.8 … 20.1 | 20.0 | 18.80 |
| ankle_roll | `Left_Ankle_Roll` | -25.2 … 25.2 | 15.0 | 12.40 |

## (b) Comparison table

- Official (VERIFIED) values unless marked. "model" = our FK/Σ of the official model file (ESTIMATED).
- The knee column gives official or published peak torque, else the model limit (tagged "model").
- Prices are the published list price at the date read; "n/p" means not published.

| Robot (year) | H (m) | Mass (kg) | DOF (legs) | Hip order | Ankle | Leg actuators / reducer | Knee peak τ (N·m) | Battery | Compute | Price | Open source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Unitree G1** (2024) | 1.32 | ≈35 | 23 / 29 / ≤43 (6+6) | P-R-Y | parallel 2-motor, rods | Unitree N7520 (14.3:1 & 22.5:1), N5020-16; 2-stage planetary PMSM | 90 (G1) / 120 (EDU); model 139 | 13S 9 Ah ≈421 Wh, ≈2 h | 8-core CPU; EDU Orin NX 16 GB | US$13.5k (was 16k); CNY 85k | URDF/MJCF/SDK (BSD-3/Apache) |
| Unitree H1 (2023) | 1.80 | ≈47 | 19 (5+5) | Y-R-P | 1-DOF | M107 (15:1/24:1), 360 N·m | ≈360 | 15 Ah 864 Wh | i5 + i7 PCs | < US$90k | URDF/MJCF |
| Unitree H1-2 | 1.78 | ≈70 | 27 (6+6) | Y-P-R | parallel | M107 | ≈360 | 864 Wh | i5 + i7 (+Orin NX) | n/p | URDF/MJCF |
| **Unitree R1** (2025) | 1.23 | ≈27 (Air) / ≈29 | 20 / 26 (6+6) | P-R-Y (pitch 25° tilt) | parallel 2-motor, rods | Unitree PMSM (model 60 N·m hip/knee, 33 N·m ankle motors) | model 60 | 33.12 V 6 Ah 199 Wh, ≈1 h | 8-core CPU (+10 TOPS head) | **US$4,900 / 5,900**; EDU 10,500 | URDF/MJCF |
| **Berkeley Humanoid Lite** (2025) | 0.80 | 16 | 22 (6+6) | R-Y-P (±45° roll/yaw) | serial | MAD M6C12 / 5010 BLDC + **3-D-printed cycloidal 15:1** | model 20 (fw 6) | 6S 4 Ah ≈89 Wh, ≈30 min | Intel N95 mini-PC | **BOM $4,312 (US) / $3,236 (CN)** | fully open (MIT / CC BY-SA) |
| Berkeley Humanoid (2024) | 0.85 | 16 (no arms) | 12 (6+6) | Y-R-P (±45°) | linkage pitch, direct roll | custom QDD 9:1 planetary (5013/8513/8518/10413) | 81.1 (10413) | 2 × DJI TB50 | i7-1255U | **$9,955** (no arms) | URDF + training code |
| **ToddlerBot 2.0** (2025) | 0.56 | 3.4 | 30 (6+6) | P-R-Y | serial | Dynamixel XM430/2XC430/XC430/XC330 | ≈3.0 stall (XM430-W210) | 4S 2–5 Ah (30–74 Wh) | Jetson Orin NX 16 GB | BOM $5.7k (2XC) / $7.3k (2XM) | fully open (MIT) |
| Poppy Humanoid (2013–) | 0.83 | 3.5 | 25 (5+5) | R-Y-P | pitch only | Dynamixel MX-28 / MX-64 | ≈2.5–3.1 (MX-28) | tethered 12 V | Raspberry Pi 4 | kit €7.9–10.0k | open (CC BY-SA / GPL) |
| **Booster T1** (2024) | 1.18 | ≈30 | 23 (6+6) | P-R-Y | parallel 2 × 43 N·m motors, rods | Booster E8112 / E6408 / E8116 / 2 × E4315 (Encos-class, E) | 130 (page); model 130.5 | 10.5 Ah, ≈2 h walking | AGX Orin + i7 | n/p (distributor €26k excl. VAT, UNVERIFIED) | URDF/MJCF/gym (BSD-3) |
| **Booster K1** (2025) | ≈0.95 | ≈19.5 | 22 (6+6) | P-R-Y | parallel 2 × 38.3 N·m | Booster E6408 / E4315 / E4310 / E6416 / 2 × E4310 (Encos-class, E) | 60 (page) vs model 112 | 2 or 5 Ah (30/80 min) | 8-core ARM 48 TOPS / Orin NX 8 GB / AGX Orin 32 GB | n/p (CNY 29.9–39k in press/JD, UNVERIFIED) | URDF/MJCF |
| **K-Scale K-Bot** (2025) | 1.40 | 34 (model 36.7) | 20 (5+5) | P-R-Y | **1-DOF pitch** | **Robstride RS04 / RS03 / RS02** (planetary QDD) | 120 (RS04) | 12 Ah NCM, 48 V (≈576 Wh E), up to 4 h | Raspberry Pi 5 | US$9,000–10,999 (2025; company closed Nov 2025) | open (CERN-OHL-S / GPL-3) |
| K-Scale Zeroth-01 / Z-Bot | ≈0.46 | ≈3.4–3.8 (model) | 20 (6+6) | Y-R-P (zbot-6dof model) | serial servo | Feetech servos | "50 kg·cm" servo class (≈4.9 N·m, E) | RC LiPo, ≈12 V (E) | Milk-V Duo S | BOM from $350 | open (MIT) |
| **Fourier N1** (2025) | 1.30 (web) / 1.245 (brochure) | 38–39 (model 39.7) | 23 (6+6) | P-R-Y (pitch 15° tilt) | 2-DOF (roll→pitch; parallel push-rods (brochure render, E)) | Fourier FSA 8029E / 6043E / 4530E | 95 (model) | 475 Wh, ≈2 h | i7-13700H | n/p | open (URDF, Apache-2.0 / LGPL-3.0) |
| Noetix N2 (2025) | 1.14 ("1.2 m" in news) | ≈30 (33.5 with battery) (model 33.2) | 18 (5+5) | (±45° yaw/roll)-P | 1-DOF pitch | n/p; knee and ankle linkage-driven | 150 (model) | 48 V 7.5 Ah ≈360 Wh, 1–2 h | RK3588S (+Orin Nano Super EDU) | n/p | gym + URDF + SDK |
| Noetix Bumi (2025) | 0.98 | ≈17 | 21 (6+6) | P-R-Y | 2-DOF (mechanism n/p) | n/p (hip/knee 60 N·m, ankle 30 N·m) | — | 13S 48 V 5.1 Ah ≈245 Wh, 2–3 h | RK3576 | **CNY 9,998** | SDK |
| Robotis OP3 (2017) | 0.51 | 3.5 | 20 (6+6) | Y-R-P | serial | Dynamixel XM430-W350 (353.5:1) | 4.1 (stall @12 V) | 3S 3.3 Ah 37 Wh | Intel NUC i3 | US$11,969–13,764 | software open |
| **Menlo Asimov 1** (2026) | **1.20** | 35 | 25 (6+6) | P-R-Y | **parallel RSU** | Encos EC-A planetary 25/36:1 + **harmonic** 100/107:1 (hip roll/yaw) | 75 (EC-A4315) | 13S4P 46.8 V 10.5 Ah **491 Wh** | Radxa CM5 + Raspberry Pi 5 | **DIY kit US$20k** | open (CERN-OHL-S / GPL-2) |
| EngineAI PM01 (2024) | 1.38–1.40 | 40–44 | 23–24 (6+6) | P-R-Y (pitch 15° tilt) | 2-DOF (model serial) | own PMSM + planetary | 164 (page, 2026) | 10 Ah ≈468 Wh, 2 h | 8-core + Orin NX | CNY 88,000 | URDF / SDK |
| PNDbotics Adam Lite | 1.67 | 60 | 25 (6+6) | P-R-Y (35° tilt) | parallel 2-motor | PND PSA: planetary 7:1 hip pitch/knee, harmonic roll/yaw | 340 | 1172 Wh | NUC12 i7 | ≈US$120k (secondary) | URDF/MJCF/SDK |
| Duke Humanoid v1 (2024) | ≈1.0 (shoulder) | 30 | 10 (5+5) | Y-P-R | 1-DOF, linkage-driven | Motorevo BLDC + planetary (18/20/10:1) | 72 rated / 238 max | tethered | Teensy + off-board | n/p | open (MIT) |
| AgiBot X1 (2024) | 1.30 | 33 | 34 | P-R-Y (45° tilt) | parallel 2 × R52 | PowerFlow R86 / R52 | 200 (R86-3 peak) | 2 h | n/p | n/p | STEP / BOM / code open |
| AgiBot X2 (2025) | 1.31 | ≈35 | 25 (6+6) | P-R-Y | 2-DOF (mechanism n/p) | n/p | 120 | ≈500 Wh, ≈2 h | 2 × RK3588 (+Orin NX) | n/p | URDF (Mulan PSL v2) |
| HighTorque Mini Pi+ | ≈0.75 | 13.8–15 | 27 (6+6) | P-R-Y | serial | HTDW-5036 36:1 two-stage planetary (21 N·m) | 21 | 6S 97 Wh, ≈1 h | RK3588 | **US$5,500** | URDF |
| HighTorque Mini Pi | 0.52 | 7 | 12 (6+6) | P-R-Y | serial | HTDW-5036 | 21 | 24 V | — | **US$3,500** | URDF |
| Roboparty Roboto Origin (2025) | 1.25* | 34* | 23 (6+6) | Y-R-P (30° tilt) | rod-driven 2-DOF | **Damiao DM10010L / DM4340P** | 120 (model) | 48 V 15 Ah ≈720 Wh | RDK X5 8 GB | **BOM CNY 49,713** | fully open (CERN-OHL-W / GPL-3) |
| Westwood BRUCE | 0.70 | 4.8 | 16 (5+5) | Y-P-R (intersecting) | 1-DOF | Koala BEAR 9:1 QDD, 250 g | > 8 burst (10.5 fw) | 3 Ah, ≈20 min | 6-TOPS SBC | US$15,290 (offer 8,890) | code GPL-3 / models Apache |

\* Secondary source (UNVERIFIED).

## (c) Leg segment lengths normalised by standing height

**How the table was built:**

- H = official standing height (VERIFIED in §a).
- Thigh, shin, ankle→sole, hip→sole and foot come from our FK of the official model file at q = 0 (ESTIMATED); for robots with several files we use the one with foot primitives.
- "—" means the foot is mesh-only, so the value is not derivable.
- Foot L/W is the extent of the *primitive* collision geoms; for contact-sphere feet (G1, R1, Asimov) it understates the real sole outline.
- Foot-centre spacing is 2 × |y| of the ankle-roll axis at q = 0. Exceptions: H1-2 and N2 use leg-line / hip spacing, Poppy the hip-yaw spacing, K-Bot the ankle spacing, and Berkeley Humanoid its init pose.

Notes on individual rows:

- Roboto Origin and SA01 heights are secondary sources (*).
- BRUCE (0.70 m) and Mini Pi (0.52 m) have unusually high L/H. Their official heights may exclude the head or refer to a different pose.
- ToddlerBot's 0.56 m refers to v1/v2 per the paper (the 2.0 legs are 30 mm shorter).
- Official "leg length" figures use different datums:
  - G1 "calf + thigh 0.6 m" ≈ hip-roll→ankle 0.606 m.
  - R1 "600 mm" ≈ hip-pitch→ankle 0.597 m.
  - T1 "leg length 57 cm" ≈ hip-pitch→sole 0.571 m.
  - PM01 "thigh+shin 686.5 mm" ≈ hip-roll→ankle 0.687 m.

| robot | H (m) | thigh (m) | shin (m) | L=thigh+shin (m) | ankle→sole (m) | hip-pitch→sole (m) | thigh/H | shin/H | L/H | hip→sole/H | thigh:shin | foot L/H | foot W/H | foot-centre spacing/H |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Unitree G1 | 1.32 | 0.337 | 0.300 | 0.637 | 0.053 | 0.689 | 0.255 | 0.227 | 0.482 | 0.522 | 1.12 | 0.136 | 0.053 | 0.180 |
| Unitree R1 | 1.23 | 0.288 | 0.309 | 0.597 | 0.055 | 0.652 | 0.234 | 0.251 | 0.486 | 0.530 | 0.93 | 0.146 | 0.057 | 0.140 |
| Unitree H1 | 1.80 | 0.400 | 0.400 | 0.800 | 0.062 | 0.862 | 0.222 | 0.222 | 0.444 | 0.479 | 1.00 | 0.156 | 0.017 | — |
| Unitree H1-2 | 1.78 | 0.400 | 0.400 | 0.800 | — | — | 0.225 | 0.225 | 0.449 | — | 1.00 | — | — | 0.183 |
| Booster T1 | 1.18 | 0.236 | 0.280 | 0.516 | 0.055 | 0.571 | 0.200 | 0.237 | 0.437 | 0.484 | 0.84 | 0.191 | 0.085 | 0.180 |
| Booster K1 | 0.95 | 0.192 | 0.245 | 0.437 | 0.038 | 0.475 | 0.202 | 0.258 | 0.460 | 0.500 | 0.78 | 0.189 | 0.074 | 0.203 |
| K-Scale K-Bot | 1.40 | 0.385 | 0.290 | 0.675 | 0.058 | 0.733 | 0.275 | 0.207 | 0.482 | 0.524 | 1.33 | 0.150 | 0.051 | 0.152 |
| Fourier N1 | 1.30 | 0.308 | 0.280 | 0.588 | — | — | 0.237 | 0.215 | 0.452 | — | 1.10 | — | — | 0.185 |
| Noetix N2 | 1.14 | 0.200 | 0.260 | 0.460 | — | — | 0.175 | 0.228 | 0.403 | — | 0.77 | — | — | 0.160 |
| Menlo Asimov 1 | 1.20 | 0.270 | 0.272 | 0.542 | 0.044 | 0.586 | 0.225 | 0.227 | 0.452 | 0.489 | 0.99 | 0.147 | 0.055 | 0.179 |
| EngineAI PM01 | 1.38 | 0.336 | 0.363 | 0.699 | — | — | 0.243 | 0.263 | 0.506 | — | 0.92 | — | — | 0.180 |
| AgiBot X1 | 1.30 | 0.268 | 0.305 | 0.573 | — | — | 0.206 | 0.235 | 0.440 | — | 0.88 | — | — | 0.206 |
| AgiBot X2 | 1.31 | 0.320 | 0.282 | 0.602 | 0.073 | 0.675 | 0.244 | 0.215 | 0.460 | 0.515 | 1.13 | 0.163 | 0.099 | 0.209 |
| Roboparty Roboto Origin* | 1.25 | 0.250 | 0.300 | 0.550 | — | — | 0.200 | 0.240 | 0.440 | — | 0.83 | — | — | 0.116 |
| PNDbotics Adam Lite | 1.67 | 0.461 | 0.370 | 0.831 | 0.065 | 0.896 | 0.276 | 0.222 | 0.498 | 0.537 | 1.25 | 0.132 | 0.048 | 0.140 |
| Berkeley Humanoid (2024) | 0.85 | 0.220 | 0.180 | 0.400 | 0.063 | 0.463 | 0.259 | 0.212 | 0.471 | 0.544 | 1.22 | 0.188 | 0.065 | 0.260 |
| Berkeley Humanoid Lite | 0.80 | 0.150 | 0.160 | 0.310 | 0.100 | 0.410 | 0.187 | 0.200 | 0.387 | 0.513 | 0.94 | 0.275 | 0.090 | 0.142 |
| HighTorque Mini Hi | 0.89 | 0.192 | 0.199 | 0.391 | — | — | 0.216 | 0.224 | 0.440 | — | 0.96 | — | — | 0.224 |
| HighTorque Mini Pi+ | 0.75 | 0.142 | 0.140 | 0.282 | — | — | 0.190 | 0.187 | 0.377 | — | 1.02 | — | — | 0.217 |
| HighTorque Mini Pi | 0.52 | 0.140 | 0.140 | 0.279 | — | — | 0.268 | 0.269 | 0.537 | — | 1.00 | — | — | 0.308 |
| Poppy Humanoid | 0.83 | 0.182 | 0.180 | 0.362 | — | — | 0.219 | 0.217 | 0.436 | — | 1.01 | — | — | 0.160 |
| Westwood BRUCE | 0.70 | 0.205 | 0.200 | 0.405 | — | — | 0.293 | 0.286 | 0.578 | — | 1.03 | — | — | 0.217 |
| ToddlerBot 2.0 (2XC) | 0.56 | 0.102 | 0.110 | 0.212 | 0.039 | 0.251 | 0.181 | 0.196 | 0.378 | 0.447 | 0.92 | 0.196 | 0.075 | 0.132 |
| Robotis OP3 | 0.51 | 0.110 | 0.110 | 0.220 | 0.031 | 0.251 | 0.216 | 0.216 | 0.432 | 0.491 | 1.00 | 0.249 | 0.153 | 0.137 |
| EngineAI SA01* | 1.29 | 0.300 | 0.370 | 0.670 | — | — | 0.233 | 0.287 | 0.519 | — | 0.81 | — | — | 0.116 |


**Statistics over the 1.14–1.40 m full-humanoid set** (ESTIMATED): G1, R1, Booster T1, K-Bot, Fourier N1, Noetix N2, Asimov 1, PM01, AgiBot X1, AgiBot X2 and Roboto Origin; n = 11, fewer where the foot is mesh-only. The last column is scaled to **JX1 at H = 1.20 m**.

| ratio | n | min | p25 | median | p75 | max | → JX1 @ 1.20 m: median (p25–p75) |
|---|---|---|---|---|---|---|---|
| thigh / H | 11 | 0.175 | 0.203 | 0.234 | 0.244 | 0.275 | 0.281 m (0.244–0.293) |
| shin / H | 11 | 0.207 | 0.221 | 0.228 | 0.239 | 0.263 | 0.273 m (0.265–0.286) |
| (thigh+shin) / H | 11 | 0.403 | 0.440 | 0.452 | 0.482 | 0.506 | 0.542 m (0.528–0.579) |
| ankle-pitch→sole / H | 6 | 0.037 | 0.040 | 0.043 | 0.046 | 0.056 | 0.052 m (0.048–0.056) |
| hip-pitch→sole / H | 6 | 0.484 | 0.495 | 0.519 | 0.523 | 0.530 | 0.622 m (0.594–0.628) |
| foot length / H (primitives) | 6 | 0.136 | 0.147 | 0.149 | 0.160 | 0.191 | 0.178 m (0.176–0.192) |
| foot width / H (primitives) | 6 | 0.051 | 0.054 | 0.056 | 0.078 | 0.099 | 0.067 m (0.064–0.093) |
| foot-centre spacing / H | 11 | 0.116 | 0.156 | 0.180 | 0.182 | 0.209 | 0.215 m (0.187–0.219) |
| thigh : shin | 11 | 0.77 | 0.86 | 0.93 | 1.11 | 1.33 | 0.93 (0.86–1.11) |

## (d) Leg joint torque and speed limits normalised by mass × leg length, and scaling to JX1

**Definitions** (all ESTIMATED from the model values quoted in §(a)):

- τ* = τ_limit / (M · g · L). This is a dimensionless torque.
  - M = Σ link masses of the model the limit came from. This keeps τ and M internally consistent.
  - L = thigh + shin (hip-pitch axis → ankle-pitch axis, from §c).
- ω* = ω_limit · √(L / g). This is Froude-scaled speed: the same ω* means the same dynamic similarity.
- To scale to JX1: τ_JX1 = τ* · M_JX1 · g · L_JX1 and ω_JX1 = ω* · √(g / L_JX1).

**Caveats:**

- Limits are whatever the vendor wrote in the model, usually *peak*. Vendors differ: some de-rate for safety (Berkeley Humanoid 2024, Asimov URDF), some put motor-side values, and parallel-ankle robots give serial-equivalent values. For Asimov and Duke we also list datasheet or paper values.
- Where the model only has placeholders (ToddlerBot, OP3), we used the vendor's actuator-model or datasheet value and say so.

Per-robot values (τ* and ω* columns: hp = hip pitch, hr = hip roll, hy = hip yaw, kn = knee, ap = ankle pitch, ar = ankle roll):

| robot | M kg | L m | MgL N·m | τ*hp | τ*hr | τ*hy | τ*kn | τ*ap | τ*ar | ω*hp | ω*hr | ω*hy | ω*kn | ω*ap | ω*ar |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G1 (29dof rev1.0, mode 4/5) | 33.3 | 0.637 | 208 | 0.423 | 0.668 | 0.423 | 0.668 | 0.168 | 0.168 | 8.15 | 5.09 | 8.15 | 5.09 | 7.64 | 7.64 |
| G1 (mode 10-16, hip-pitch 22.5:1) | 33.7 | 0.637 | 211 | 0.660 | 0.660 | 0.418 | 0.660 | 0.166 | 0.166 | 5.09 | 5.09 | 8.15 | 5.09 | 7.64 | 7.64 |
| H1 | 59.3 | 0.800 | 466 | 0.429 | 0.429 | 0.429 | 0.644 | 0.086 | — | 6.57 | 6.57 | 6.57 | 4.00 | 2.57 | — |
| H1-2 | 67.0 | 0.800 | 526 | 0.380 | 0.380 | 0.380 | 0.571 | 0.114 | 0.076 | 6.57 | 6.57 | 6.57 | 4.00 | 2.57 | 2.57 |
| R1 | 28.8 | 0.597 | 169 | 0.355 | 0.355 | 0.355 | 0.355 | 0.296 | 0.296 | 4.64 | 4.64 | 4.64 | 4.64 | 7.40 | 7.40 |
| Berkeley Humanoid Lite (URDF) | 16.3 | 0.310 | 50 | 0.403 | 0.403 | 0.403 | 0.403 | 0.403 | 0.403 | 2.67 | 2.67 | 2.67 | 2.67 | 2.67 | 2.67 |
| Berkeley Humanoid 2024 (URDF, safety-limited) | 16.1 | 0.400 | 63 | 0.476 | 0.317 | 0.317 | 0.476 | 0.317 | 0.079 | 4.04 | 4.64 | 4.64 | 2.83 | 4.04 | 8.48 |
| ToddlerBot 2.0 2XC (sysID tau_max) | 3.5 | 0.211 | 7 | 0.150 | 0.150 | 0.094 | 0.267 | 0.267 | 0.202 | 1.00 | 1.00 | 0.96 | 1.12 | 1.12 | 1.03 |
| ToddlerBot 2.0 2XM (sysID tau_max) | 3.8 | 0.211 | 8 | 0.373 | 0.373 | 0.086 | 0.245 | 0.245 | 0.186 | 0.67 | 0.67 | 0.96 | 1.12 | 1.12 | 1.03 |
| Poppy (URDF) | 2.6 | 0.362 | 9 | 0.788 | 0.334 | 0.334 | 0.334 | 0.334 | — | 1.58 | 1.34 | 1.34 | 1.34 | 1.34 | — |
| Booster T1 (URDF serial-equiv.) | 31.7 | 0.516 | 161 | 0.615 | 0.423 | 0.423 | 0.812 | 0.455 | 0.107 | 3.51 | 3.36 | 3.36 | 3.38 | 2.88 | 2.88 |
| Booster K1 (URDF serial-equiv.) | 19.7 | 0.437 | 84 | 0.807 | 0.510 | 0.455 | 1.329 | 0.455 | 0.455 | 3.09 | 2.65 | 3.71 | 2.65 | 3.71 | 3.71 |
| K-Scale K-Bot | 36.7 | 0.675 | 243 | 0.494 | 0.247 | 0.247 | 0.494 | 0.070 | — | 4.59 | 4.94 | 4.94 | 4.59 | 9.89 | — |
| Fourier N1 | 39.7 | 0.588 | 229 | 0.415 | 0.236 | 0.236 | 0.415 | 0.131 | 0.131 | 3.02 | 3.61 | 3.61 | 3.02 | 4.10 | 4.10 |
| Noetix N2 | 33.2 | 0.460 | 150 | 1.003 | 0.602 | 0.602 | 1.003 | 0.468 | — | 3.03 | 3.03 | 3.03 | 3.03 | 3.03 | — |
| Menlo Asimov 1 (URDF) | 32.2 | 0.542 | 171 | 0.262 | 0.262 | 0.163 | 0.262 | 0.233 | 0.099 | 2.96 | 0.94 | 1.28 | 2.88 | 2.19 | 2.19 |
| Menlo Asimov (Encos peak, v0 table) | 35.0 | 0.542 | 186 | 0.644 | 0.483 | 0.322 | 0.403 | 0.193 | 0.193 | 2.95 | 0.94 | 1.28 | 2.88 | 2.19 | 2.19 |
| EngineAI PM01 EDU | 40.9 | 0.699 | 281 | 0.585 | 0.585 | 0.217 | 0.585 | 0.217 | 0.217 | 7.02 | 7.02 | 9.39 | 7.02 | 9.39 | 9.39 |
| AgiBot X1 | 35.3 | 0.573 | 198 | 0.756 | 0.756 | 0.252 | 0.756 | 0.403 | 0.403 | 1.93 | 1.93 | 5.80 | 1.93 | 2.42 | 2.42 |
| Duke Humanoid v1 | 29.6 | 0.516 | 150 | 0.600 | 0.540 | 0.540 | 0.540 | 0.300 | — | 2.75 | 3.06 | 3.06 | 3.06 | 2.45 | — |
| HighTorque Pi+ | 11.0 | 0.282 | 30 | 0.656 | 0.656 | 0.656 | 0.656 | 0.656 | 0.656 | 0.92 | 0.92 | 0.92 | 0.92 | 0.92 | 0.92 |
| HighTorque Mini Hi | 18.3 | 0.391 | 70 | 0.461 | 0.461 | 0.461 | 0.461 | 0.205 | 0.205 | 1.11 | 1.11 | 1.11 | 1.11 | 1.09 | 1.09 |
| Roboparty Roboto Origin (rpo_description) | 33.8 | 0.550 | 182 | 0.659 | 0.659 | 0.659 | 0.659 | 0.148 | 0.148 | 5.92 | 5.92 | 5.92 | 5.92 | 1.89 | 1.89 |
| AgiBot X2 EDU | 41.2 | 0.602 | 243 | 0.493 | 0.493 | 0.493 | 0.493 | 0.247 | 0.148 | 2.96 | 2.96 | 2.96 | 2.96 | 3.37 | 3.63 |
| EngineAI SA01 (legs only) | 33.1 | 0.670 | 218 | 0.643 | 0.643 | 0.643 | 0.643 | 0.110 | 0.110 | 6.53 | 6.53 | 6.53 | 6.53 | 8.10 | 8.10 |
| Westwood BRUCE (BEAR 10.5 N·m) | 4.5 | 0.405 | 18 | 0.594 | 0.594 | 0.594 | 0.594 | 0.594 | — | — | — | — | — | — | — |
| PNDbotics Adam Lite | 58.5 | 0.831 | 477 | 0.482 | 0.336 | 0.220 | 0.482 | 0.084 | 0.025 | 4.37 | 2.33 | 2.33 | 4.37 | 5.82 | 5.82 |

**Summary over a "core" set of 15 modern, RL-walking, 0.8–1.4 m-class electric humanoids.** The set is G1 (rev 1.0), R1, Booster T1, Booster K1, K-Bot, Fourier N1, Noetix N2, Asimov (Encos peak), PM01, AgiBot X1, AgiBot X2, Berkeley Humanoid Lite (URDF), Duke v1, Roboto Origin (rpo_description) and HighTorque Mini Hi. Servo robots (OP3, Poppy, ToddlerBot) and the 1.7–1.8 m robots (H1, H1-2, Adam Lite) are excluded.

The right-hand columns scale the p50/p75 values to **JX1 with L = 0.54 m** (the §c median for H = 1.2 m) and **M = 25, 30 or 35 kg**. That gives M·g·L = 132 / 159 / 185 N·m and √(g/L) = 4.26 s⁻¹. These inputs are assumptions for illustration, and all values below are ESTIMATED.

| joint | n | τ* p25 | τ* p50 | τ* p75 | JX1 25 kg p50/p75 (N·m) | JX1 30 kg p50/p75 (N·m) | JX1 35 kg p50/p75 (N·m) | ω* p25 | ω* p50 | ω* p75 | JX1 ω p50 / p75 (rad/s) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hip pitch | 15 | 0.442 | 0.585 | 0.652 | 77 / 86 | 93 / 104 | 108 / 121 | 2.85 | 3.03 | 4.61 | 12.9 / 19.7 |
| hip roll | 15 | 0.413 | 0.493 | 0.593 | 65 / 79 | 78 / 94 | 91 / 110 | 2.66 | 3.06 | 4.79 | 13.0 / 20.4 |
| hip yaw | 15 | 0.287 | 0.423 | 0.477 | 56 / 63 | 67 / 76 | 78 / 88 | 2.99 | 3.61 | 5.37 | 15.4 / 22.9 |
| knee | 15 | 0.438 | 0.540 | 0.712 | 71 / 94 | 86 / 113 | 100 / 132 | 2.77 | 3.03 | 4.61 | 12.9 / 19.7 |
| ankle pitch | 15 | 0.181 | 0.247 | 0.403 | 33 / 53 | 39 / 64 | 46 / 75 | 2.43 | 3.03 | 5.75 | 12.9 / 24.5 |
| ankle roll | 12 | 0.148 | 0.199 | 0.323 | 26 / 43 | 32 / 51 | 37 / 60 | 2.36 | 3.26 | 4.93 | 13.9 / 21.0 |


**Reading the table for JX1** (ESTIMATED):

- **Knee**: τ* median ≈ 0.54, upper quartile ≈ 0.71. For JX1 that is **≈ 86–113 N·m peak at 30 kg, ≈ 71–94 N·m at 25 kg**. G1 sits at 0.67 (139 N·m on 33 kg), T1 at 0.81 and K1 at 1.33. K-Bot (0.49), N1 (0.42), Asimov-peak (0.40) and BHL (0.40) are lower.
- At 30 kg (p50–p75): **hip pitch ≈ 93–104 N·m**, **hip roll ≈ 78–94 N·m**, **hip yaw ≈ 67–76 N·m**. The p25 values are about 20 % lower.
- At 30 kg: **ankle pitch ≈ 39–64 N·m** and **ankle roll ≈ 32–51 N·m**. These are serial-equivalent. With a two-motor parallel ankle each motor can be roughly half of this, geometry permitting (see §E3 and the T1/K1 closed-chain analysis).
- **Speed**: ω* ≈ 3 (median) for hips and knee → **≈ 13 rad/s (≈ 120 rpm) at the joint**. The upper quartile ≈ 4.6–5.4 → **≈ 19–23 rad/s**. G1's N7520 family is far above the median (ω* 5.1–8.2 → 20–32 rad/s joint speed), which explains its agility.
  - Low-speed designs (Asimov harmonic hip roll ω* 0.94; X1 hips ω* 1.9; HighTorque ω* ≈ 1) are at the bottom.
  - → **Specify ≥ 12 rad/s at rated torque and ≥ 20 rad/s no-load at the hip and knee.**
- **Continuous torque** is typically ⅓–½ of the peak in the datasheets we saw: Encos 40/120, 25/75 and 12/36; Robstride RS04 40/120, RS03 20/60 and RS02 6/17 (rated/peak per the K-Scale docs); PND 64/180; HighTorque HTDW-5036 6/21. Check standing/crouch loads against the continuous rating, not the peak.

## (e) Design lessons for JX1

Lessons marked **[model]** come from our FK parse of the official files. Every other statement cites §(a).

### E1. Hip architecture

1. **Use a pitch-first hip: pelvis → hip PITCH → hip ROLL → hip YAW → knee [model].** This is now the dominant layout. Robots using it:
   - Unitree G1, R1 and H2
   - Booster T1 and K1
   - Fourier N1, K-Bot
   - Menlo Asimov v0 and 1
   - EngineAI PM01, AgiBot X1 and X2
   - HighTorque Pi, Pi+ and Hi
   - PNDbotics Adam, ToddlerBot v1 and 2.0

   Other orders in the set:
   - Yaw-first (yaw → roll → pitch): H1, OP3, Roboto Origin.
   - Yaw → pitch → roll: H1-2, Duke, BRUCE (BRUCE's three axes intersect).
   - Roll → yaw → pitch: Poppy, EngineAI SA01.
   - Tilted ±45° roll/yaw pairs followed by pitch: Berkeley Humanoid, Berkeley Humanoid Lite, Noetix N2.

   Why pitch-first:
   - The largest hip motor is fixed to the pelvis, so the leg does not carry it.
   - The roll and yaw motors form the thigh structure.
   - Hip flexion can be very large: G1 −145°…+165°, T1 −170°…+125°, X2 −155°…+146.5°. That is what makes getting up from the floor, sitting and kneeling possible.
   - The cost is that the yaw actuator sits mid-thigh and carries the leg's bending moment, so yaw ranges are often small: Asimov ±45°, K1 ±58°, K-Bot ±90°.
2. **Axis tilts are optional packaging tricks [model].**
   - G1 pitches the hip roll and yaw axes 10° (rpy −0.1749 rad, undone at the knee).
   - The hip-pitch axis is tilted 25° on R1, 15° on N1 and PM01, 35° on Adam, and 45° on X1 and Asimov-v0.
   - BH, BHL and N2 use two ±45° actuators that each mix roll and yaw.
   - Asimov 1, which is exactly 1.2 m, went back to orthogonal, untilted axes.

   Orthogonal axes simplify CAD, calibration, URDF and RL. Tilt only if packaging forces it.
3. **Stance width [model].** Foot-centre spacing at q = 0:
   - G1 0.237 m (18 % of H), T1 0.212 m (18 %), Asimov 1 0.215 m (18 %)
   - K1 0.192 m (20 %), R1 0.173 m (14 %), N1 0.240 m, X1 0.268 m, X2 0.274 m
   - H1 0.406 m (outlier)

   → For JX1 at 1.2 m, **0.19–0.23 m foot-centre spacing** fits the cluster.

### E2. Knee

1. **Range.** For get-up, kneel and deep-squat behaviours, aim for ≥ 135°.
   - G1 −5°…+165°, K-Bot 0…155°, BHL 0…140°, R1 −10°…+139°, X2 0…138°, N1 −5°…+135°, K1 0…133°, T1 0…123°.
   - Asimov 1 allows only 0…86°.
2. **Torque.** The knee is the largest leg load: τ* median ≈ 0.54, upper quartile ≈ 0.71 (§d).
3. **Actuator location [model].** Shank+foot mass as a share of total mass:
   - 3.3 % Duke (knee and ankle driven by linkages from the thigh)
   - 6 % Berkeley Humanoid 2024 (knee and ankle actuators at the hip), H1 and K-Bot
   - 8–10 % G1, T1, Asimov 1 and R1 (both ankle motors in the shank)
   - 11–13 % K1, PM01 and HighTorque

   Proximal placement cuts swing inertia, at the cost of linkages and backlash. ToddlerBot 2.0 deliberately *removed* its parallel-link knee to simplify it. G1-class robots accept 8 % and use direct-drive knees.

### E3. Ankle

1. **Two-motor parallel ankles are standard in 1.2–1.4 m commercial robots.**
   - Unitree G1, R1, H1-2 and H2 use A/B motors with PR/AB control modes, per the Unitree docs.
   - Booster T1 and K1, AgiBot X1 (2 × PowerFlow R52) and Adam (2 × PND-50) use the same approach, as do Roboto Origin (rods) and Asimov (RSU bar linkage).
   - Both motors sit high in the shank (80–165 mm below the knee) and drive the foot through rods.

   Geometry extracted from the model files [model]:

   | robot | motor centres below knee | crank r | rods | foot anchor relative to ankle axis |
   |---|---|---|---|---|
   | Unitree R1 | 96.5 / 162.8 mm | 21 mm | 218 / 151.5 mm | 21 mm in front, ±14 mm, −9 mm |
   | Booster T1 | 96 / 156 mm | 43 mm | 180 / 120 mm | 41.5 mm behind, ±27.5 mm, +21 mm |
   | Booster K1 | 81.6 / 140 mm | 41 mm | 158 / 82 mm | 29 mm behind, ±24 mm, +17.5 mm |
   | AgiBot X1 | 110 / 165 mm | 32.8 mm | 195 / 140 mm | 41 mm behind, ±23.3 mm, +9 mm |

2. **Parallel-ankle capacity depends strongly on posture (closed-chain Jacobian on the official T1/K1 geometry, ESTIMATED).**

   | robot | drive motors | pitch at neutral | roll at neutral | pitch over range | roll over range |
   |---|---|---|---|---|---|
   | Booster T1 | 2 × 43 N·m | 98 N·m | 53 N·m | 33–126 N·m | 17–77 N·m |
   | Booster K1 | 2 × 38.3 N·m | 58 N·m | 38 N·m | 35–61 N·m | 12–49 N·m |

   Roll capacity collapses at full dorsiflexion. → Size the crank and anchor geometry for the corners of the workspace, not the neutral pose.
3. **Ankle ranges are small.** Pitch is about −50°…+20…35°; roll is ±15–25° (G1 ±15°, T1 ±25°, N1 ±25°). Asimov limits roll to ±5.7° in its URDF.
4. **Serial ankles** (BHL, Berkeley Humanoid roll, ToddlerBot, OP3, HighTorque, Duke) are simpler and cheaper. The cost is actuator mass at the foot and a taller ankle: BHL's pitch axis is 0.10 m above the sole, versus 0.04–0.055 m for parallel ankles.
5. **1-DOF (pitch-only) ankles** are used by K-Bot, N2, Duke, Poppy, BRUCE and H1. They save 2 actuators but lose lateral foot control. K-Bot's 17 N·m RS02 ankle is the weakest normalised ankle in the set (τ* 0.07).
6. **Ankle-pitch→sole height** is 0.038–0.058 m in 1–1.4 m robots:
   - G1 0.053, T1 0.042–0.055, K1 0.038, Asimov 1 0.044, R1 0.055, K-Bot 0.058, X2 0.073.

### E4. Actuators

1. **A small family of sizes covers the leg.**

   | robot | actuator family | sizing |
   |---|---|---|
   | G1 | one N7520 motor at two planetary ratios, plus N5020 | 14.3:1 → 88 N·m / 32 rad/s; 22.5:1 → 139 / 20 (sim limits); N5020-16 ≈ 25–35 N·m for ankle, waist, arms |
   | K-Bot | Robstride | RS04 (120 N·m) hip pitch and knee; RS03 (60) hip roll and yaw; RS02 (17) ankle |
   | Roboto Origin | Damiao | DM10010L on hips and knees (9 units); DM4340P on ankles and arms (14 units) |
   | Asimov | Encos, 5 SKUs | two are harmonic, used for hip roll and yaw |

   Rotor inertia checks out: G1 armature 0.01018 kg·m² ÷ 14.3² and 0.02510 ÷ 22.5² both equal ≈ 4.9–5.0e-5 kg·m², matching Unitree's stated rotor inertia of 0.489e-4 kg·m². So one motor with two gear ratios is a cheap way to get two torque/speed classes.
2. **Reducer choice.**
   - Low-ratio planetary (7–25:1) dominates: Unitree, Robstride, Encos-P, PND hip pitch/knee (7:1), Berkeley Humanoid (9:1), Motorevo (10–20:1).
   - BHL's 3-D-printed cycloidal 15:1 is the cheapest proven option: $94–188 per actuator, 90 % efficiency, but no published peak rating.
   - Harmonic drives appear only on hip roll/yaw of heavier robots (Asimov 100:1 and 107:1, PND 31–51:1). They bring low efficiency (31–51 % on Asimov), low speed (38–52 rpm) and high reflected inertia (0.10 kg·m²).
   - → For RL sim-to-real and backdrivability, use QDD planetary at every leg joint.
3. **Model limits ≠ datasheet.**
   - Berkeley Humanoid's URDF is capped "for safety".
   - BHL firmware limits torque to 6 N·m against a 20 N·m URDF.
   - Booster deploys 60/25/30/60/24/15 N·m against 98.8/68/68/130.5/73.1/17.2 in the asset URDF.
   - Asimov's URDF uses 45 N·m where the datasheet peak is 120.

   Size JX1 on **peak ≈ p50–p75 of §d** and check **continuous ≈ ⅓–½ of peak** against static loads.
4. **Costs seen.**

   | robot | actuator cost |
   |---|---|
   | BHL | $157–188 (6512) and $94–136 (5010) per actuator |
   | Berkeley Humanoid | $422–676 per actuator |
   | Roboparty | DM10010L CNY 1,989; DM4340P CNY 949 (actuators ≈ 63 % of a CNY 49.7k BOM) |
   | Asimov v0 | ≈ $8.5k of actuators in "just over $10k" legs |
   | Poppy | ≈ 60 % of an $8–9k build is Dynamixels |

   → **Actuators dominate cost in every open BOM.** The JX1 actuator strategy (buy, e.g. Robstride/Damiao/Encos-class QDD, vs build, e.g. BHL-style printed cycloidal or a custom planetary) is the #1 cost lever.

### E5. COM and mass distribution [model]

- At q = 0 the whole-body COM sits at 1.0–1.1 × hip-pitch height above the sole:

  | robot | COM height | hip-pitch height |
  |---|---|---|
  | G1 | 0.703 m | 0.689 m |
  | T1 | 0.616 m | 0.571 m |
  | Asimov 1 | 0.642 m | 0.586 m |
  | K-Bot | 0.750 m | 0.733 m |
  | R1 | 0.661 m | 0.652 m |
  | X2 | 0.687 m | 0.675 m |

- Both legs together weigh 39–48 % of total mass. Examples: G1 43 %, T1 39 %, K-Bot 41 %, N1 45 %, Asimov 1 40 %, R1 40 %.
- Torso/pelvis links carry the battery and compute: G1 torso 6.78 kg + pelvis 3.81 kg; T1 trunk 11.7 kg; K-Bot torso 12.97 kg; N2 base 10.9 kg.

### E6. Battery, power and electronics

1. **Voltage.**
   - 13S (≈48 V nominal, 54.6 V charge) is the norm for 1.2–1.4 m robots: G1 9 Ah (≈421 Wh), Asimov 13S4P 10.5 Ah (491 Wh, ≈2 kg), PM01 ≈468 Wh, Roboparty 48 V 15 Ah (CNY 528), X2 ≈500 Wh.
   - R1 uses a smaller 9S-class 33.12 V 199 Wh pack for ≈1 h.
   - Small robots use 6S (BHL 89 Wh; Pi+ 97 Wh) or 4S (ToddlerBot).
   - Runtime ≈ 1–2 h at ≈200 W average (G1: 421 Wh / 2 h ≈ 210 W, ESTIMATED).
2. **Placement and swapping.**
   - **Quick-swap packs** are standard on commercial units: G1 ("Smart Battery (Quick Release)"), H1, PM01, X2, N2, Bumi, and a T1 slide-in pack. Berkeley Humanoid uses 2 hot-swappable DJI TB50 packs.
   - Roboparty's BOM lists a "Battery Bottom Cover", which suggests the pack sits low in the trunk (ESTIMATED).
   - Pack masses seen: Asimov ≈ 2 kg (491 Wh), N1 ≤ 3.2 kg (475 Wh), Bumi 1.36 kg (245 Wh). → Mount a 2–3 kg pack in the trunk close to the hip line to keep the COM near hip height (§E5).
3. **Compute cost ladder.**
   - Intel N95 mini-PC (BHL).
   - RDK X5 8 GB, CNY 599 (Roboparty).
   - Raspberry Pi 5 + Radxa CM5 (Asimov 1).
   - RK3588 (HighTorque, AgiBot X2).
   - Jetson Orin NX 16 GB (ToddlerBot, G1 EDU, PM01).
   - AGX Orin / Thor (Booster T1, G1 accessory).

   RL locomotion policies run at 25–50 Hz on CPU (BHL 25 Hz on N95; ToddlerBot 50 Hz on the Orin CPU; K-Bot 50 Hz).
4. **Buses and cable routing.**
   - One CAN bus per limb: Asimov uses 5 × 1 Mbps + 1 × 500 kbps; BHL 4 × CAN 1 Mbps via USB-CAN; Roboparty 4 × USB-to-CAN.
   - Use pre-made daisy-chain harnesses carrying power + CAN in one connector: Asimov XT30(2+2), 100–600 mm lengths listed per joint; Roboparty 10/20/40 cm pre-made motor-to-motor leads.
   - Hollow-shaft actuators route cables through the joints: Unitree N-series and M107, Berkeley Humanoid (except the 5013).
   - EtherCAT (Berkeley Humanoid 1–4 kHz, Duke 2 kHz) gives more bandwidth but costs more.
   - → For JX1, per-limb CAN-FD with daisy-chained 48 V + CAN harnesses is the proven low-cost pattern.

### E7. Structure, manufacturing and maintenance

1. **Materials.**
   - CNC aluminium dominates commercial robots. Roboparty's frame is 25 CNC part types, sandblasted and black-anodised (so aluminium, ESTIMATED), CNY 15,670 in total. Berkeley Humanoid uses 7075/6061 with SKD11 steel linkages; Duke 6061 plates; N1 aluminium alloy + engineering plastic; PM01 "aviation aluminium".
   - MJF PA12 nylon + 7075 is Asimov's hybrid.
   - FDM PLA/PLA-CF works for sub-20 kg robots (BHL, ToddlerBot); carbon fibre for BRUCE.
   - The most expensive CNC parts are the big leg members: Roboparty inner thigh CNY 1,500 each, calf CNY 1,600 each, hip fixation CNY 1,800. → Consider sheet-metal or cast/molded alternatives for these in India.
2. **Serviceability.**
   - K-Bot's stated design principles: easy to repair, easy to mass-manufacture (moldable), COTS parts, modular swappable hands and head.
   - ToddlerBot's typical repair takes 21 min of printing + 14 min of assembly.
   - BHL fits every printed part in a 200 mm cube and assembles in about 3 days.
   - Unitree uses quick-release batteries (G1 spare pack US$700). Asimov's DIY kit ships with spare parts.
   - → Design JX1 so any actuator can be swapped with ≤ 6 fasteners and one harness connector.
3. **Sim assets.** Every successful open platform ships a URDF *and* an MJCF with tuned armature, friction and foot contact primitives (Menagerie G1-MJX, Booster, Asimov, ToddlerBot). → Plan JX1's model file as a deliverable, not an afterthought.

## (f) Sources

Every URL cited above is listed once, grouped by the section where it first appears. All were accessed 2026-09-24. Model files were fetched from `raw.githubusercontent.com` (or via read-only `gh api` tree listings).


**A1. Unitree G1 (G1 / G1 EDU / 23- and 29-DOF / G1+, Unitree Robotics, China)**

- https://www.unitree.com/g1
- https://www.unitree.com/cn/g1
- https://www.unitree.com/G1pl
- https://shop.unitree.com/products/unitree-g1
- https://support.unitree.com/home/en/G1_developer
- https://robot-api.unitree.com/doc?space=G1_developer&locale=en
- https://github.com/unitreerobotics/unitree_ros
- https://github.com/unitreerobotics/unitree_rl_lab
- https://github.com/unitreerobotics/unitree_mujoco
- https://github.com/unitreerobotics/unitree_rl_gym
- https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/g1_description/g1_29dof_rev_1_0.urdf
- https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/g1_description/README.md
- https://raw.githubusercontent.com/unitreerobotics/unitree_mujoco/main/unitree_robots/g1/g1_29dof.xml
- https://raw.githubusercontent.com/google-deepmind/mujoco_menagerie/main/unitree_g1/g1_mjx.xml
- https://raw.githubusercontent.com/unitreerobotics/unitree_rl_gym/main/legged_gym/envs/g1/g1_config.py

**A2. Unitree H1 and H1-2 (1.8 m class, reference only)**

- https://www.unitree.com/h1
- https://support.unitree.com/home/en/H1_developer
- https://shop.unitree.com/products/unitree-h1
- https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/h1_description/urdf/h1.urdf
- https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/h1_2_description/h1_2_handless.urdf

**A2b. Unitree H2 (context only, 2025–26)**

- https://www.unitree.com/H2

**A3. Unitree R1 (R1 Air / R1 / R1 EDU, launched 2025)**

- https://www.unitree.com/R1
- https://www.unitree.com/cn/R1
- https://www.unitree.com/R1/battery
- https://shop.unitree.com/products/unitree-r1
- https://support.unitree.com/home/en/R1_developer
- https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/r1_description/R1.urdf
- https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/r1_air_description/R1_AIR.urdf
- https://raw.githubusercontent.com/unitreerobotics/unitree_mujoco/main/unitree_robots/r1/R1_C%2B%2B.xml

**A4. Berkeley Humanoid Lite (UC Berkeley Hybrid Robotics, RSS 2025) — open source**

- https://arxiv.org/html/2504.17249
- https://lite.berkeley-humanoid.org/static/paper/demonstrating-berkeley-humanoid-lite.pdf
- https://docs.google.com/spreadsheets/d/1AQEHcH_nPkXYfor2-h7bwNIUMmsePtAm53epnsWgZXc
- https://berkeley-humanoid-lite.gitbook.io/docs/getting-started-with-hardware/materials-and-parts-bom
- https://berkeley-humanoid-lite.gitbook.io/docs
- https://github.com/HybridRobotics/Berkeley-Humanoid-Lite
- https://github.com/HybridRobotics/Berkeley-Humanoid-Lite-Assets
- https://github.com/HybridRobotics/berkeley-humanoid-lite-lowlevel
- https://raw.githubusercontent.com/HybridRobotics/berkeley-humanoid-lite-lowlevel/main/robot_configuration.backup.json
- https://cad.onshape.com/documents/fc6443b1d89dcba950e85b60
- https://cad.onshape.com/documents/55ab471d620553f44eac2d08
- https://cad.onshape.com/documents/192ab9c484f00d0dd33b8f01
- https://raw.githubusercontent.com/HybridRobotics/Berkeley-Humanoid-Lite-Assets/main/data/robots/berkeley_humanoid/berkeley_humanoid_lite/urdf/berkeley_humanoid_lite.urdf

**A5. Berkeley Humanoid (2024, Hybrid Robotics)**

- https://arxiv.org/html/2407.21781
- https://berkeley-humanoid.com/
- https://github.com/HybridRobotics/berkeley_humanoid_description
- https://github.com/HybridRobotics/isaac_berkeley_humanoid
- https://raw.githubusercontent.com/HybridRobotics/berkeley_humanoid_description/main/urdf/robot.urdf
- https://raw.githubusercontent.com/HybridRobotics/isaac_berkeley_humanoid/main/exts/berkeley_humanoid/berkeley_humanoid/assets/berkeley_humanoid.py

**A6. ToddlerBot (Stanford TML; v1 Feb 2025, v2.0 Aug 2025) — open source**

- https://arxiv.org/html/2502.00893
- https://arxiv.org/html/2502.00893v1
- https://toddlerbot.github.io/
- https://github.com/hshi74/toddlerbot
- https://raw.githubusercontent.com/hshi74/toddlerbot/main/CHANGELOG.md
- https://hshi74.github.io/toddlerbot/hardware/01_bill_of_materials.html
- https://hshi74.github.io/toddlerbot/features/03_diy_battery.html
- https://cad.onshape.com/documents/565bc33af293a651f66e88d2
- https://raw.githubusercontent.com/hshi74/toddlerbot/main/toddlerbot/descriptions/toddlerbot_2xc/toddlerbot_2xc.urdf
- https://raw.githubusercontent.com/hshi74/toddlerbot/v1.0.0/toddlerbot/descriptions/toddlerbot/toddlerbot.urdf

**A7. Poppy Humanoid (Inria / Poppy project) — open source**

- https://www.poppy-project.org/en/robots/poppy-humanoid/
- https://github.com/poppy-project/poppy-humanoid
- https://raw.githubusercontent.com/poppy-project/poppy-humanoid/master/software/poppy_humanoid/configuration/poppy_humanoid.json
- https://www.generationrobots.com/en/403347-poppy-humanoid-robot-raspberry-pi-version-with-3d-parts.html
- https://raw.githubusercontent.com/poppy-project/poppy-humanoid/master/hardware/URDF/robots/Poppy_Humanoid.URDF

**A8. Booster Robotics T1 (2024) and K1 (2025) (Beijing)**

- https://www.booster.tech/booster-t1/
- https://docs.booster.tech/docs/product-manual/t1/getting-started/specifications/
- https://www.booster.tech/booster-k1/
- https://docs.booster.tech/docs/product-manual/k1/getting-started/specifications/
- https://github.com/BoosterRobotics/booster_assets
- https://github.com/BoosterRobotics/booster_gym
- https://raw.githubusercontent.com/BoosterRobotics/booster_train/main/source/booster_train/booster_train/assets/robots/actuator.py
- https://raw.githubusercontent.com/BoosterRobotics/booster_train/main/source/booster_train/booster_train/assets/robots/booster.py
- https://arxiv.org/abs/2506.15132
- https://raw.githubusercontent.com/BoosterRobotics/booster_assets/main/robots/T1/T1_23dof.urdf
- https://raw.githubusercontent.com/BoosterRobotics/booster_gym/main/resources/T1/T1_serial.urdf
- https://raw.githubusercontent.com/BoosterRobotics/booster_gym/main/deploy/configs/T1.yaml
- https://raw.githubusercontent.com/BoosterRobotics/booster_assets/main/robots/K1/K1_22dof.urdf

**A9. K-Scale Labs K-Bot (2025) and Zeroth-01 / Z-Bot (open source; company shut down Nov 2025)**

- https://github.com/kscalelabs/docs/blob/master/docs/robots/k-bot/mechanical.md
- https://github.com/kscalelabs/docs/blob/master/docs/robots/k-bot/electrical.md
- https://github.com/kscalelabs/kbot
- https://github.com/kscalelabs/kbot-models
- https://web.archive.org/web/20251006231727/https://www.kscale.dev/kbot
- https://web.archive.org/web/20250326033803/https://shop.kscale.dev/products/kbot
- https://web.archive.org/web/20260129051959/https://kscale.ai/
- https://robstride.com/
- https://github.com/kscalelabs/zeroth-bot
- https://github.com/kscalelabs/docs/blob/master/docs/robots/zeroth-01/bom.md
- https://github.com/kscalelabs/kscale-assets
- https://cad.onshape.com/publications/e15cf8edefacbba3009917c0/
- https://raw.githubusercontent.com/kscalelabs/kbot-models/master/kbot/robot.urdf
- https://raw.githubusercontent.com/kscalelabs/kscale-assets/master/zbot-6dof/robot.urdf

**A10. Fourier N1 (Fourier, Shanghai; open-sourced 2025)**

- https://fftai.com/ecosystem/n1
- https://fftai.com/pdf/en/n1.pdf
- https://github.com/FFTAI/Wiki-GRx-Models
- https://github.com/FFTAI/Wiki-GRx-Mujoco
- https://github.com/FFTAI/fourier-grx-N1
- https://raw.githubusercontent.com/FFTAI/Wiki-GRx-Models/FourierN1/N1/urdf/N1_raw.urdf
- https://raw.githubusercontent.com/FFTAI/fourier-grx-N1/main/docs/reference/joint_sequence.md

**A11. Noetix Robotics N2 (2025) and Bumi (2025) (Beijing)**

- https://www.noetixrobotics.com/
- https://web.noetixrobotics.com/docs/
- https://www.noetixrobotics.com/official/api/news/detail?id=71
- https://github.com/Noetix-Robotics
- https://raw.githubusercontent.com/Noetix-Robotics/noetix_n2_gym/main/resources/robots/N2/urdf/N2.urdf

**A12. Robotis OP3**

- https://emanual.robotis.com/docs/en/platform/op3/introduction/
- https://raw.githubusercontent.com/ROBOTIS-GIT/ROBOTIS-OP3-Common/master/op3_description/urdf/robotis_op3.structure.lleg.xacro
- https://robotis.us/products/robotis-op3us
- https://en.robotis.com/shop_en/item.php?it_id=905-0036-000
- https://raw.githubusercontent.com/google-deepmind/mujoco_menagerie/main/robotis_op3/op3.xml
- https://github.com/ROBOTIS-GIT/ROBOTIS-OP3-Common/tree/master/op3_description/urdf

**A13. Menlo Research Asimov: v0 open-source legs (2025) and Asimov 1 (1.2 m, 2026), open source**

- https://docs.menlo.ai/asimov/1/overview/system-tour/mechanical
- https://docs.menlo.ai/asimov/1/overview/system-tour/electrical
- https://github.com/menloresearch/asimov-1
- https://github.com/menloresearch/asimov-v0
- https://raw.githubusercontent.com/menloresearch/asimov-mjlab/main/motor_parameters.md
- https://menlo.ai/blog/humanoid-legs-100-days
- https://menlo.ai/asimov-1
- https://raw.githubusercontent.com/menloresearch/asimov-1/main/sim-model/urdf/asimov_1.urdf
- https://raw.githubusercontent.com/menloresearch/asimov-v0/main/sim-model/xmls/asimov.xml

**A14. Other relevant robots found (compact, low-cost or open)**

- https://en.engineai.com.cn/product-pm01.html
- https://en.engineai.com.cn/product-support-pm01.html
- https://www.newsfilecorp.com/release/235198/Breaking-Through-with-Strength-Leading-the-Future-EngineAI-Launches-the-PM01-Humanoid-Robot
- https://raw.githubusercontent.com/engineai-robotics/engineai_robotics_native_sdk/main/assets/resource/robot/pm01_edu/urdf/serial_pm01_edu.urdf
- https://wiki.pndbotics.com/en/robot/humanoid_robot/
- https://wiki.pndbotics.com/en/actuator/introduce/
- https://github.com/pndbotics/pnd_models
- https://arxiv.org/abs/2409.19795
- https://github.com/generalroboticslab/DukeHumanoidv1
- https://www.agibot.com/products/X1
- https://github.com/AgibotTech/agibot_x1_hardware
- https://www.agibot.com/products/X2
- https://github.com/AgibotTech/agibot_x2_urdf
- https://raw.githubusercontent.com/AgibotTech/agibot_x1_infer/main/src/module/dcu_driver_module/cfg/dcu_x1.yaml
- https://www.hightorquerobotics.com/pi/
- https://www.hightorque.cn/pi-plus-from-scratch/reference/hardware/
- https://www.hightorque.cn/en/hie/
- https://store.hightorque.cn/products.json
- https://www.hightorquerobotics.com/product?id=75
- https://github.com/HighTorque-Robotics/HT_Robot_URDF
- https://github.com/Roboparty/roboto_origin
- https://raw.githubusercontent.com/Roboparty/roboto_origin/main/assets/BOM_EN.md
- https://github.com/Roboparty/rpo_description
- https://github.com/Roboparty/rpo_hardware
- https://www.westwoodrobotics.io/bruce/
- https://www.westwoodrobotics.io/wp-content/uploads/2023/08/BRUCE_EN_061823_E.pdf
- https://raw.githubusercontent.com/Westwood-Robotics/BRUCE-OP/main/Settings/BRUCE_macros.py
- https://raw.githubusercontent.com/Westwood-Robotics/BRUCE_simulation_models/V1.6/Gazebo/urdf/bruce.urdf
- https://raw.githubusercontent.com/generalroboticslab/legged_env/master/assets/urdf/v6biped_urdf_v4_aug29/v6biped_urdf_v4_squarefoot_aug29.urdf
- https://raw.githubusercontent.com/AgibotTech/agibot_x1_train/main/resources/robots/x1/urdf/x1.urdf
- https://raw.githubusercontent.com/Roboparty/roboto_origin/main/modules/rpo_hardware/V2.0/roboto_origin_mechanic/03_URDF/urdf/roboto_origin.urdf
- https://raw.githubusercontent.com/AgibotTech/agibot_x2_urdf/main/X2_URDF-v1.4.0/X2-EDU.urdf
- https://raw.githubusercontent.com/engineai-robotics/engineai_legged_gym/master/resources/robots/zq_humanoid/urdf/zq_sa01.urdf

**A15. Appendix: per-file extraction tables for all 43 parsed model files**

- https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/g1_description/g1_23dof_rev_1_0.urdf
- https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/g1_description/g1_23dof_mode_10.urdf
- https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/g1_description/g1_29dof_mode_15.urdf
- https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/g1_description/g1_23dof.urdf
- https://raw.githubusercontent.com/unitreerobotics/unitree_ros/master/robots/h2_description/H2.urdf
- https://raw.githubusercontent.com/HybridRobotics/Berkeley-Humanoid-Lite-Assets/main/data/robots/berkeley_humanoid/berkeley_humanoid_lite/urdf/berkeley_humanoid_lite_biped.urdf
- https://raw.githubusercontent.com/hshi74/toddlerbot/main/toddlerbot/descriptions/toddlerbot_2xm/toddlerbot_2xm.urdf
- https://raw.githubusercontent.com/BoosterRobotics/booster_assets/main/robots/K1/K1_22dof_parallel.xml
- https://raw.githubusercontent.com/kscalelabs/kbot-models/master/kbot-full-collisions/robot.mjcf
- https://raw.githubusercontent.com/google-deepmind/mujoco_menagerie/main/pndbotics_adam_lite/adam_lite.xml
- https://raw.githubusercontent.com/HighTorque-Robotics/HT_Robot_URDF/main/pi_plus_24dof/urdf/pi_plus_24dof.urdf
- https://raw.githubusercontent.com/HighTorque-Robotics/HT_Robot_URDF/main/hi_25dof/urdf/hi_25dof.urdf
- https://raw.githubusercontent.com/HighTorque-Robotics/HT_Robot_URDF/main/pi_12dof/urdf/pi_12dof.urdf
- https://raw.githubusercontent.com/AgibotTech/agibot_x2_urdf/main/X2_URDF-v1.4.0/X2-EDU.xml
- https://raw.githubusercontent.com/pndbotics/pnd_models/main/adam_lite/adam_lite.urdf
- https://raw.githubusercontent.com/Roboparty/rpo_description/main/urdf/rpo.urdf

**Additional official URLs consulted, found by the research sub-agents (not cited inline above)**

- https://berkeley-humanoid-lite.gitbook.io/docs/in-depth-contents/joint-id-mapping
- https://berkeley-humanoid-lite.gitbook.io/docs/in-depth-contents/motor-characterization
- https://berkeley-humanoid-lite.gitbook.io/docs/getting-started-with-software/the-on-board-computer
- https://berkeley-humanoid-lite.gitbook.io/docs/releases
- https://github.com/T-K-233/recoil-motor-controller-besc
- https://arxiv.org/pdf/2407.21781
- https://docs.google.com/spreadsheets/d/e/2PACX-1vQmoxJnTnUaQ_-WAAjnchBhaX5HZ4ElUV5pXksEV6GEbeEjiie1E_BdN9XCMt6FtfBaopXoaeSOeMDg/pubhtml
- https://www.generationrobots.com/en/403348-robot-poppy-humanoid-version-raspberry-sans-impressions-3d.html
- https://docs.poppy-project.org/en/assembly-guides/poppy-humanoid/bom.html
- https://emanual.robotis.com/docs/en/platform/op3/quick_start/
- https://emanual.robotis.com/docs/en/platform/op3/hardware/
- https://emanual.robotis.com/docs/en/parts/controller/opencr10/
- https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/
- https://emanual.robotis.com/docs/en/dxl/x/xm430-w210/
- https://emanual.robotis.com/docs/en/dxl/x/2xc430-w250/
- https://emanual.robotis.com/docs/en/dxl/x/xc330-t288/
- https://emanual.robotis.com/docs/en/dxl/mx/mx-28/
- https://emanual.robotis.com/docs/en/dxl/mx/mx-64/
- https://github.com/ROBOTIS-GIT/ROBOTIS-OP3
- https://github.com/ROBOTIS-GIT/ROBOTIS-OP-Series-Data
- https://docs.menlo.ai/asimov/1
- https://wiki.pndbotics.com/en/actuator/PND-130A-7F-P/
- https://wiki.pndbotics.com/en/actuator/PND-130-7F-P/
- https://wiki.pndbotics.com/en/actuator/PND-80-20-S/
- https://wiki.pndbotics.com/en/actuator/PND-60-17-S/
- https://wiki.pndbotics.com/en/actuator/PND-50-6F5S-P/
- https://raw.githubusercontent.com/pndbotics/pnd_rl_gym/main/resources/robots/adam_lite/adam_lite_12dof.urdf
- https://humanoid.guide/product/adam/
- https://www.engineai.com.cn/product-pm01.html
- https://en.engineai.com.cn/
- https://raw.githubusercontent.com/engineai-robotics/engineai_robotics_description/master/pm01_edu/urdf/serial_pm01_edu.urdf
- https://www.4gltemall.com/engineai-sa01-edu.html
- https://raw.githubusercontent.com/AgibotTech/agibot_x1_train/main/resources/robots/x1/mjcf/robot/xyber_x1/xyber_x1_serial.xml
- https://www.hightorquerobotics.com/mini-pi
- https://www.hightorquerobotics.com/pi-plus/
- https://www.hightorquerobotics.com/product?id=567
- https://raw.githubusercontent.com/Westwood-Robotics/BRUCE_simulation_models/V1.6/MuJoCo/bruce.xml
- https://raw.githubusercontent.com/Roboparty/rpo_description/main/mjcf/rpo.xml
- https://interestingengineering.com/ai-robotics/worlds-first-full-stack-humanoid-robot-open-sourced
- https://www.unitree.com/G1-D
- https://www.unitree.com/robocup
- https://www.unitree.com/H2plus
- https://www.unitree.com/cn/H2
- https://doc-cdn.unitree.com/10/299/en/10_299_en
- https://github.com/unitreerobotics/unitree_sdk2
- https://huggingface.co/datasets/unitreerobotics/unitree_model
- https://shop.unitree.com/products/go2-battery
- http://web.archive.org/web/20240513184245/https://www.unitree.com/g1/
- https://openelab.io/products/unitree-go1-humanoid-robot-battery-9000mah
- https://docs.booster.tech/docs/product-manual/t1/getting-started/quick-start/
- https://docs.booster.tech/docs/product-manual/k1/getting-started/overview/
- https://static.generation-robots.com/media/user-manual-booster-t1-en.pdf
- https://www.generationrobots.com/en/404278-booster-t1-humanoid-robot.html
- https://hsl.robocup.org/wp-content/uploads/2026/03/large_Robotedge-specs-698021eff19c7.pdf
- https://www.ithome.com/1/003/924.htm
- https://www.gamersky.com/tech/202510/2032428.shtml
- https://www.humanoidsdaily.com/news/k-scale-labs-cancels-k-bot-orders-open-sources-all-ip-after-funding-fails
- https://mikekalil.com/blog/k-scale-labs-shuts-down/
- https://www.rs-online.com/designspark/k-scale-labs-launches-k-bot-americas-first-open-source-humanoid-robot
- https://github.com/zeroth-robotics/docs
- https://web.archive.org/web/20250614173437/https://shop.kscale.dev/products/zbot
- https://web.archive.org/web/20250720154158/https://www.kscale.dev/
- https://raw.githubusercontent.com/kscalelabs/kscale-assets/master/kbot-v2-feet/robot.urdf
- https://raw.githubusercontent.com/kscalelabs/kscale-assets/master/actuators/feetech_sts3250.json
- https://raw.githubusercontent.com/FFTAI/Wiki-GRx-Mujoco/FourierN1/robots/N1/mjcf/N1_raw_refine.xml
- https://www.noetixrobotics.com/official/api/news/detail?id=80
- https://www.noetixrobotics.com/official/api/news/detail?id=88
