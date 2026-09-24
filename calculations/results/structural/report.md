# JX1 structural analysis (OI-4) — voxel FEA + hand calculations

Body weight 269 N (mass 27.47 kg). Actuator peaks: hip yaw 36, hip roll 60, hip pitch 120, knee 120, ankle motor 36 N·m.

**Load model (leg chain: hip brackets, pelvis, thigh, shin)** — `calculations/structural/leg_loads.py`:
* **LC1 strength**: 2160 ground-reaction samples (8 poses × CoP grid over the sole × 5 GRF directions × 3 free yaw moments) at 3 BW, propagated through the leg kinematics; whenever a joint (or an ankle motor through the parallel linkage) would exceed its actuator peak the GRF is scaled to the saturation point (2034 samples scaled, min scale 0.23). Required SF 1.5 on minimum yield (6061-T6) / 2.0 on conditioned strength (PA-CF).
* **LC2 fatigue**: fast walk 0.79 m/s, nominal walk 0.52 m/s and 15°/step turning time series (inverse-dynamics joint torques → equivalent foot wrench), Goodman mean/amplitude per element, required SF 1.5.
* Foot and ankle crank: capped envelope cases (foot patch loads limited by the ankle's torque capability; crank rod force from the RS06 peak).
* SF = 1 / (99.9th-percentile failure index away from load/support introduction). Method validated against closed-form solutions (`test_voxel_fea.py`). Label: CALCULATED (linear, bonded interfaces, ASSUMED printed-material knockdowns).

| Part | Material / print build axis | Elements | SF LC1 (req) | SF LC2 fatigue (req) | Result | Worst location [mm] |
|---|---|---|---|---|---|---|
| JX1_Thigh_L | 6061-T6 | 40278 | 2.31 (1.5) | 2.78 (1.5) | PASS | [23.0, 35.0, -205.0] |
| JX1_HipRollBracket_L | 6061-T6 | 20997 | 2.76 (1.5) | 3.8 (1.5) | PASS | [-69.0, -19.0, -39.0] |
| JX1_HipYawBracket_L | 7075-T6 | 38205 | 1.77 (1.5) | 1.58 (1.5) | PASS | [-131.0, 3.0, 55.0] |
| JX1_Shin_L | 6061-T6 | 54333 | 3.37 (1.5) | 4.17 (1.5) | PASS | [-15.0, -20.0, -271.0] |
| JX1_Foot_L | 6061-T6 | 23194 | 3.5 (1.5) | 2.03 (1.5) | PASS | [25.0, 11.0, -41.0] |
| JX1_Pelvis | 6061-T6 | 61436 | 2.9 (1.5) | 3.44 (1.5) | PASS | [71.0, 133.0, 131.0] |
| JX1_AnkleCrank | 6061-T6 | 21080 | 14.44 (1.5) | 24.7 (1.5) | PASS | [-37.5, -18.5, 5.5] |
| JX1_Torso | 6061-T6 **(recommended)** | 136604 | 4.44 (1.5) | 3.59 (1.5) | PASS | [51.0, 79.0, 5.0] |
| JX1_Torso | PA-CF build z | 136604 | 0.7 (2.0) | 0.42 (1.5) | **FAIL** | [-11.0, 25.0, 5.0] |
| JX1_ShoulderPitchBracket_L | 6061-T6 **(recommended)** | 125734 | 2.17 (1.5) | 1.75 (1.5) | PASS | [-45.5, 5.5, 42.5] |
| JX1_ShoulderPitchBracket_L | PA-CF build x | 125734 | 0.24 (2.0) | 0.15 (1.5) | **FAIL** | [-45.5, 5.5, -42.5] |
| JX1_ShoulderPitchBracket_L | PA-CF build y | 125734 | 0.41 (2.0) | 0.25 (1.5) | **FAIL** | [-45.5, 5.5, -42.5] |
| JX1_ShoulderPitchBracket_L | PA-CF build z | 125734 | 0.32 (2.0) | 0.19 (1.5) | **FAIL** | [-45.5, 5.5, 42.5] |
| JX1_ShoulderRollBracket_L | 6061-T6 **(recommended)** | 44276 | 2.05 (1.5) | 1.66 (1.5) | PASS | [-33.5, 22.5, -13.5] |
| JX1_ShoulderRollBracket_L | PA-CF build x | 44276 | 0.23 (2.0) | 0.14 (1.5) | **FAIL** | [-33.5, 31.5, -13.5] |
| JX1_ShoulderRollBracket_L | PA-CF build y | 44276 | 0.28 (2.0) | 0.17 (1.5) | **FAIL** | [-33.5, 22.5, -13.5] |
| JX1_ShoulderRollBracket_L | PA-CF build z | 44276 | 0.36 (2.0) | 0.21 (1.5) | **FAIL** | [-33.5, 15.5, -18.5] |
| JX1_UpperArm_L | 6061-T6 **(recommended)** | 133148 | 5.99 (1.5) | 4.84 (1.5) | PASS | [23.5, -25.5, -82.5] |
| JX1_UpperArm_L | PA-CF build x | 133148 | 0.84 (2.0) | 0.5 (1.5) | **FAIL** | [23.5, -25.5, -82.5] |
| JX1_UpperArm_L | PA-CF build y | 133148 | 1.23 (2.0) | 0.74 (1.5) | **FAIL** | [-24.5, -26.5, -84.5] |
| JX1_UpperArm_L | PA-CF build z | 133148 | 0.73 (2.0) | 0.44 (1.5) | **FAIL** | [23.5, -25.5, -82.5] |
| JX1_Forearm_L | 6061-T6 **(recommended)** | 73032 | 3.27 (1.5) | 2.65 (1.5) | PASS | [-10.5, 30.5, -14.5] |
| JX1_Forearm_L | PA-CF build x | 73032 | 0.45 (2.0) | 0.27 (1.5) | **FAIL** | [10.5, 30.5, -14.5] |
| JX1_Forearm_L | PA-CF build y | 73032 | 0.56 (2.0) | 0.34 (1.5) | **FAIL** | [-10.5, 30.5, -14.5] |
| JX1_Forearm_L | PA-CF build z | 73032 | 0.36 (2.0) | 0.21 (1.5) | **FAIL** | [5.5, 25.5, -21.5] |

## Interface compliance (unit loads)

| Part | Interface | translation [mm/kN] | rotation [deg per 100 N·m] |
|---|---|---|---|
| JX1_Thigh_L | knee | [0.7458, 3.7481, 0.3328] | [1.1871, 0.0471, 1.7081] |
| JX1_HipRollBracket_L | leg | [0.0646, 0.2491, 0.052] | [0.2806, 0.0156, 0.5987] |
| JX1_HipYawBracket_L | leg | [0.8448, 1.519, 1.6288] | [0.6211, 1.0395, 0.2367] |
| JX1_Shin_L | fork | [0.2488, 7.4568, 0.0352] | [2.1782, 0.1824, 1.3216] |
| JX1_Foot_L | toe patch GRF (ankle-torque capped) | [0.0567, 0.4649, 1.4021] | [1.5337, 2.2517, 0.1846] |
| JX1_Pelvis | leg | [0.5581, 1.3261, 0.176] | [0.4197, 0.175, 0.0059] |
| JX1_AnkleCrank | rod-end stud (rod force; radial component up to 0.7 F at +-45 deg crank) | [0.0028, 0.0081, 0.1251] | [2.2353, 3.7026, 0.3691] |
| JX1_Torso | left shoulder-pitch housing (arm wrench @ shoulder centre) | [3.8377, 3.3647, 1.6193] | [1.0509, 0.4469, 0.2176] |
| JX1_ShoulderPitchBracket_L | shoulder-roll housing (arm wrench @ roll centre) | [1.0128, 1.382, 2.1076] | [1.5022, 0.622, 3.3117] |
| JX1_ShoulderRollBracket_L | shoulder-yaw housing (arm wrench @ roll centre) | [0.1025, 0.0541, 0.2198] | [0.8622, 2.2299, 0.0396] |
| JX1_UpperArm_L | elbow housing (forearm wrench @ elbow) | [0.5382, 0.426, 0.1656] | [1.0374, 0.1109, 0.8965] |
| JX1_Forearm_L | gripper mount (hand wrench @ hand frame) | [1.9761, 24.4128, 2.2831] | [17.1862, 0.9722, 10.6951] |

## Design history (voxel variant studies, same consistent loads)

Variants start from the voxelised first-iteration CAD (printed PA-CF brackets) and add material or change the alloy (`part_variants.py`, `thigh_variants.py`); they drove the redesign now in the CAD.

| Part | Variant | Material | Mass (solid) kg | SF LC1 | SF LC2 |
|---|---|---|---|---|---|
| foot | F0_pacf | PA-CF build z | 0.274 | 0.74 | 0.33 |
| foot | F1_al | 6061-T6 | 0.597 | 4.29 | 2.5 |
| hip_roll | R0_pacf | PA-CF build y | 0.18 | 0.35 | 0.37 |
| hip_roll | R1_al | 6061-T6 | 0.392 | 1.96 | 2.64 |
| hip_roll | R2_al_12mm | 6061-T6 | 0.611 | 4.42 | 6.68 |
| hip_roll | R3_al_ribs | 6061-T6 | 0.78 | 4.25 | 6.19 |
| hip_roll | R4_al_ribs_gussets | 6061-T6 | 0.846 | 6.45 | 9.35 |
| hip_yaw | Y0_pacf | PA-CF build z | 0.312 | 0.08 | 0.07 |
| hip_yaw | Y1_al | 6061-T6 | 0.68 | 0.7 | 0.79 |
| hip_yaw | Y1_7075 | 7075-T6 | 0.708 | 1.25 | 1.14 |
| hip_yaw | Y12_7075_back12 | 7075-T6 | 0.856 | 1.65 | 1.42 |
| hip_yaw | Y13_7075_back12_keel | 7075-T6 | 0.864 | 1.87 | 1.6 |
| hip_yaw | Y2_al_back16 | 6061-T6 | 0.965 | 1.06 | 1.09 |
| hip_yaw | Y3_al_box | 6061-T6 | 1.36 | 1.25 | 1.33 |
| hip_yaw | Y6_al_raised_box | 6061-T6 | 2.207 | 4.03 | 4.43 |
| hip_yaw | Y7_al_raised_light | 6061-T6 | 1.254 | 2.12 | 2.32 |
| hip_yaw | Y8_al_raised_walls | 6061-T6 | 1.596 | 2.18 | 2.39 |
| hip_yaw | Y4_al_box_keel | 6061-T6 | 1.45 | 1.36 | 1.52 |
| pelvis | P0_pacf | PA-CF build z | 0.858 | 0.9 | 0.73 |
| pelvis | P1_al | 6061-T6 | 1.867 | 5.82 | 6.72 |
| shin | S0_pacf | PA-CF build y | 0.396 | 0.35 | 0.43 |
| shin | S1_al | 6061-T6 | 0.863 | 2.06 | 3.46 |
| shin | S2_al_deep_joggle | 6061-T6 | 0.978 | 2.16 | 3.7 |
| shin | S3_al_knee14 | 6061-T6 | 1.073 | 3.12 | 4.04 |
| shin | S4_al_knee14_flanges | 6061-T6 | 1.096 | 3.23 | 4.04 |
| upper_arm | U0_al | 6061-T6 | 0.189 | 1.34 | 1.08 |
| upper_arm | U1_al_elbow10 | 6061-T6 | 0.266 | 1.95 | 1.57 |
| upper_arm | U2_al_elbow10_gussets | 6061-T6 | 0.323 | 2.34 | 1.89 |
| upper_arm | U3_al_elbow10_gussets_yaw8 | 6061-T6 | 0.334 | 3.12 | 2.52 |
| thigh | V0 | 6061-T6 | 0.68 | 1.01 | 1.19 |
| thigh | V1 | 6061-T6 | 0.712 | 1.35 | 1.6 |
| thigh | V2 | 6061-T6 | 0.804 | 1.34 | 1.7 |
| thigh | V3 | 6061-T6 | 1.103 | 2.91 | 3.35 |
| thigh | V4 | 6061-T6 | 1.195 | 2.98 | 3.73 |
| thigh | V5 | 6061-T6 | 1.023 | 3.27 | 3.65 |
| thigh | V6 | 6061-T6 | 1.115 | 3.14 | 3.65 |
| thigh | V7 | 6061-T6 | 0.723 | 1.64 | 1.94 |
| thigh | V9 | 6061-T6 | 0.873 | 2.35 | 2.81 |

## Hand calculations

```json
{
 "ankle_rod_buckling": {
  "rod_force_LC1_N": 720.0,
  "rod_force_LC2_N": 170.0,
  "pinned_pinned_K": 1.0,
  "options": {
   "M5 threaded rod (d3 = 4.019 mm)": {
    "A": {
     "length_mm": 182.7,
     "P_cr_N": 731.0,
     "SF_LC1": 1.02
    },
    "B": {
     "length_mm": 95.3,
     "P_cr_N": 2687.0,
     "SF_LC1": 3.73
    }
   },
   "M6 threaded rod (d3 = 4.773 mm)": {
    "A": {
     "length_mm": 182.7,
     "P_cr_N": 1454.0,
     "SF_LC1": 2.02
    },
    "B": {
     "length_mm": 95.3,
     "P_cr_N": 5344.0,
     "SF_LC1": 7.42
    }
   },
   "Ø8 solid 304 rod, M5 tapped ends": {
    "A": {
     "length_mm": 182.7,
     "P_cr_N": 11478.0,
     "SF_LC1": 15.94
    },
    "B": {
     "length_mm": 95.3,
     "P_cr_N": 42179.0,
     "SF_LC1": 58.58
    }
   }
  },
  "required_SF": 3.0,
  "decision": "Ø8 solid 304 rod with M5 tapped ends (M5 threaded rod buckles below the RS06 peak rod force)"
 },
 "rod_end_PHS5": {
  "static_SF_LC1": 7.96,
  "dynamic_rating_over_LC2": 19.2
 },
 "ankle_pins": {
  "pin_force_LC1_N": 2260.0,
  "double_shear_MPa": 22.5,
  "SF_shear_on_0.577Y": 9.1,
  "tine_bearing_SF_on_conditioned_xy": 4.44,
  "pin_bearing": "HK0810 drawn-cup needle bearings (8x12x10, BOM) pressed into the printed tines: bore pressure on the 12 mm OD",
  "tine_bore_pressure_MPa": 10.5,
  "decision": "keep HK0810 needle bearings (static rating >> 1.1 kN per bearing); ream printed bores for a 0.02-0.04 mm press fit"
 },
 "bolted_joints_LC1": {
  "hip_yaw_RS06_output_M3_12.9": {
   "bolts": "6 x M3 12.9 on PCD 46 mm",
   "max_bolt_tension_N": 2079.0,
   "preload_70pct_proof_N": 3415.0,
   "separation_SF": 1.64,
   "slip_torque_SF": 1.96
  },
  "hip_yaw_RS06_output_M3_8.8": {
   "bolts": "6 x M3 8.8 on PCD 46 mm",
   "max_bolt_tension_N": 2079.0,
   "preload_70pct_proof_N": 2042.0,
   "separation_SF": 0.98,
   "slip_torque_SF": 1.17
  },
  "hip_pitch_RS04_output_M5_12.9": {
   "bolts": "8 x M5 12.9 on PCD 64 mm",
   "max_bolt_tension_N": 567.0,
   "preload_70pct_proof_N": 9642.0,
   "separation_SF": 17.01,
   "slip_torque_SF": 3.09
  },
  "knee_RS04_output_M5_12.9": {
   "bolts": "8 x M5 12.9 on PCD 64 mm",
   "max_bolt_tension_N": 567.0,
   "preload_70pct_proof_N": 9642.0,
   "separation_SF": 17.01,
   "slip_torque_SF": 3.09
  },
  "ankle_RS06_output_M3_12.9": {
   "bolts": "6 x M3 12.9 on PCD 46 mm",
   "max_bolt_tension_N": 609.0,
   "preload_70pct_proof_N": 3415.0,
   "separation_SF": 5.61,
   "slip_torque_SF": 1.96
  },
  "note": "bolt patterns are ASSUMED until RobStride drawings are dimensioned (OI-1); proof strengths ISO 898-1 (8.8: 580 MPa for M3-M5 is conservative vs 600-640; 12.9: 970 MPa)"
 },
 "actuator_output_bearing_moments": {
  "hip_yaw_RS06_tilting_moment_Nm": {
   "LC1": 134.2,
   "LC2_walk": 66.0
  },
  "hip_roll_RS03_tilting_moment_Nm": {
   "LC1": 125.3,
   "LC2_walk": 62.1
  },
  "status": "UNVERIFIED — RobStride manuals (rev. 260713) publish no output-bearing axial/radial/moment ratings; request from RobStride or add an external yaw support bearing (risk R17)"
 }
}
```
