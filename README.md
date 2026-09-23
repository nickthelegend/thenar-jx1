# JX1 — low-cost compact humanoid, designed to be built in India

JX1 is an engineering project for the **lowest-cost practical compact humanoid that can realistically be built in India**:
1.20 m, ≈ 27.5 kg, 23 DOF, 12-DOF walking legs with a two-motor parallel ankle, 48 V RobStride CAN actuators,
NVIDIA Jetson Nano high-level compute with Teensy 4.1 real-time CAN hubs, native parametric SolidWorks CAD as the
mechanical source of truth, and one kinematic contract shared by CAD, URDF, MuJoCo, Isaac Sim and firmware.

> **Status (2026-09-24): Phase 1 — walking lower body designed, assembled and verified in CAD.**
> Nothing has been built or physically tested. Every number carries a label: VERIFIED / MEASURED / CALCULATED /
> ESTIMATED / ASSUMED / UNVERIFIED.

## Headline numbers

| | JX1 v0.3 | Evidence |
|---|---|---|
| Height / mass | 1.20 m / ≈ 27.5 kg | CALCULATED / ESTIMATED — `calculations/results/iter1_B_knee_and_pitch_RS04/` |
| DOF | 23 (legs 12, waist 1, arms 8, neck 2) | `simulation/joint_map.yaml` |
| Leg actuators | RS04 hip pitch + knee (120 N·m), RS03 hip roll (60), RS06 hip yaw + ankle pairs (36) | VERIFIED datasheets — `actuators/actuator_catalog.yaml` |
| Walking analysis | ZMP walking 0.30 / 0.52 / 0.79 m/s, squat, turning; all leg joints within limits with 1.5× peak margin | CALCULATED — `calculations/` |
| Power / runtime | 204 W walking, 79 W standing; 13S2P Samsung 50S 468 Wh → ≈ 1.8 h walking | CALCULATED — `calculations/run_power_budget.py` |
| Cost | ₹6.96 lakh (₹8.0 lakh with 15 % contingency); lower body ₹3.95 lakh; actuators 78 % | ESTIMATED — `bom/cost_summary.md` |
| CAD verification | 25 poses per leg: SolidWorks mate solution == analytic kinematics to 0.0000 mm / 0.0000° (incl. the closed ankle linkage); interference-checked | `verification/leg_motion_verification_*.json` |

## Repository map

| Folder | Contents |
|---|---|
| `research/` | [reference_robots.md](research/reference_robots.md) (29 humanoids, 43 model files), `raw/` evidence: actuator technology, Indian sourcing (Robu/Amazon.in, electronics & compute, power, mechanical & manufacturing) |
| `requirements/` | [robot_requirements.yaml](requirements/robot_requirements.yaml) — living requirements with status per item |
| `calculations/` | parametric leg model, closed-form IK, ZMP preview control, floating-base inverse dynamics, parallel-ankle model, sensitivity, power budget |
| `actuators/` | [actuator_selection.md](actuators/actuator_selection.md), [modular_actuator_interface.md](actuators/modular_actuator_interface.md), [actuator_catalog.yaml](actuators/actuator_catalog.yaml) |
| `CAD/` | native parametric SolidWorks parts & `Assemblies/JX1_LowerBody.SLDASM` (pelvis + both legs, articulated) |
| `tools/swlib`, `tools/cad` | SolidWorks COM automation (isolated JX1 session), part builders, assembly builder, motion/collision verifier |
| `bom/` | [master_bom.csv](bom/master_bom.csv), [cost_summary.md](bom/cost_summary.md), generator `build_bom.py` |
| `docs/` | [architecture](docs/architecture.md), [safety](docs/safety_architecture.md), [risk register](docs/risk_register.md), [open issues](docs/open_issues.md) |
| `simulation/` | `joint_map.yaml`, MuJoCo model + validation, Isaac Sim import assets, mass properties |
| `ros2_ws/` | `jx1_description` ROS 2 package (URDF generated from CAD) |
| `firmware/` | Teensy 4.1 CAN hub: RobStride protocol codec, 500 Hz scheduler, watchdogs, E-stop |
| `verification/` | machine-readable CAD/sim evidence and images |

## Reproduce

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python calculations/tests/test_kinematics.py
.venv/Scripts/python calculations/run_leg_analysis.py --design calculations/results/variant_B_knee_and_pitch_RS04.yaml --tag iter1_B
.venv/Scripts/python bom/build_bom.py
```

SolidWorks 2026 is driven through COM in a **dedicated session** (`tools/swlib/instance.py`) so other SolidWorks work on the
same machine is never touched. Full CAD regeneration:

```bash
.venv/Scripts/python tools/cad/build_actuators.py XL L M S XS
.venv/Scripts/python tools/cad/build_leg_parts.py --side L
.venv/Scripts/python tools/cad/build_leg_parts.py --side R
.venv/Scripts/python tools/cad/build_leg_assembly.py --sides LR
.venv/Scripts/python tools/cad/verify_leg_motion.py --side L --images
```

## Development phases

1. **Walking lower body** — pelvis, hips, thighs, knees, shins, ankles, feet (12 DOF). *Designed + CAD-verified.*
2. **Upper body** — torso, battery bay, Jetson Nano, power distribution, shoulders, arms, grippers, head/sensors. *Architecture and BOM done; CAD next.*
3. **Optimisation** — covers, appearance, hands, sensors, autonomy.
