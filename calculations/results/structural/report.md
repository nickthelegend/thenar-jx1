# JX1 structural analysis (OI-4) — voxel FEA + hand calculations

Body weight 269 N (mass 27.47 kg). Actuator peaks: hip yaw 36, hip roll 60, hip pitch 120, knee 120, ankle motor 36 N·m. Walking dynamic peaks (fast walk): hip yaw 24.9, hip roll 33.3, hip pitch 56.9, knee 47.4, ankle motor 8.5 N·m.

* **LC1 strength**: all actuators at peak torque simultaneously during a 3 BW landing with 0.6 BW shear, every sign combination enveloped.
* **LC2 fatigue**: fast-walk dynamic peaks + 1.5 BW + 0.2 BW shear as fully reversed amplitudes, 1e7 cycles.
* SF = 1 / (99.9th-percentile failure index away from load/support introduction). Printed parts: in-layer von Mises vs conditioned XY strength and interlayer (normal + shear) vs conditioned Z strength; the best print orientation is selected.
* Method validated against closed-form solutions (`calculations/structural/test_voxel_fea.py`: patch test exact, cantilever deflection 1.2 %, surface bending stress 1.9 %). Label: CALCULATED (linear, bonded interfaces, ASSUMED knockdowns).

| Part | Material / print build axis | Elements | SF LC1 (req) | SF LC2 (req) | Result | Worst location [mm] |
|---|---|---|---|---|---|---|
| JX1_Thigh_L | 6061-T6 | 31500 | 0.6 (1.5) | 0.48 (1.5) | **FAIL** | [23.0, 35.0, -101.0] |
| JX1_HipRollBracket_L | PA-CF build x | 18164 | 0.16 (2.0) | 0.08 (1.5) | **FAIL** | [-67.0, -21.0, -45.0] |
| JX1_HipRollBracket_L | PA-CF build y **(recommended)** | 18164 | 0.29 (2.0) | 0.16 (1.5) | **FAIL** | [-67.0, -21.0, -45.0] |
| JX1_HipRollBracket_L | PA-CF build z | 18164 | 0.2 (2.0) | 0.11 (1.5) | **FAIL** | [-69.0, -19.0, -43.0] |
| JX1_HipYawBracket_L | PA-CF build x **(recommended)** | 31474 | 0.1 (2.0) | 0.06 (1.5) | **FAIL** | [-131.0, 3.0, 55.0] |
| JX1_HipYawBracket_L | PA-CF build z | 31474 | 0.08 (2.0) | 0.05 (1.5) | **FAIL** | [-131.0, 3.0, 55.0] |
| JX1_Shin_L | PA-CF build x | 39938 | 0.15 (2.0) | 0.14 (1.5) | **FAIL** | [-31.0, -22.0, -65.0] |
| JX1_Shin_L | PA-CF build y **(recommended)** | 39938 | 0.16 (2.0) | 0.15 (1.5) | **FAIL** | [37.0, -28.0, -53.0] |
| JX1_Foot_L | PA-CF build z | 27626 | 0.52 (2.0) | 0.32 (1.5) | **FAIL** | [27.0, 9.0, -41.0] |
| JX1_Pelvis | PA-CF build z | 86446 | 0.76 (2.0) | 0.48 (1.5) | **FAIL** | [23.0, 43.0, 139.0] |
| JX1_AnkleCrank | 6061-T6 | 21080 | 14.44 (1.5) | 24.7 (1.5) | PASS | [-37.5, -18.5, 5.5] |

## Interface compliance under LC2 (walking) loads

| Part | Interface | translation [mm] | rotation [deg] |
|---|---|---|---|
| JX1_Thigh_L (all loads) | knee housing (shin wrench @ knee centre) | [0.729, 5.706, 1.534] | [2.213, 0.039, 0.903] |
| JX1_HipRollBracket_L (all loads) | hip pitch housing (leg wrench @ hip centre) | [1.549, 3.097, 1.519] | [2.891, 0.25, 3.744] |
| JX1_HipYawBracket_L (all loads) | hip roll housing (leg wrench @ hip centre) | [48.919, 24.05, 68.047] | [11.263, 43.277, 3.924] |
| JX1_Shin_L (all loads) | ankle fork pin (foot force + yaw moment @ ankle centre) | [1.414, 22.537, 1.877] | [5.936, 0.536, 6.714] |
| JX1_Foot_L (toe) | toe patch GRF | [0.511, 0.675, 4.375] | [0.17, 3.309, 0.308] |
| JX1_Foot_L (heel) | heel patch GRF | [0.155, 0.149, 0.188] | [0.007, 0.365, 0.133] |
| JX1_Foot_L (lateral edge) | lateral edge GRF | [0.186, 0.288, 0.422] | [0.512, 0.404, 0.281] |
| JX1_Pelvis (all loads) | stance hip yaw housing (leg wrench @ hip centre) | [1.774, 3.353, 1.155] | [1.417, 0.746, 0.016] |
| JX1_AnkleCrank (all loads) | rod-end stud (rod force; radial component up to 0.7 F at +-45 deg crank) | [0.0, 0.001, 0.003] | [0.0, 0.009, 0.002] |

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
