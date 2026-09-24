# JX1 — low-cost compact humanoid, designed to be built in India

JX1 is an engineering project for the **lowest-cost practical compact humanoid that can realistically be built in India**:
≈ 1.23 m, 33.6 kg, 23 DOF, 12-DOF walking legs with a two-motor parallel ankle, 48 V RobStride CAN actuators, NVIDIA Jetson
Nano high-level compute with Teensy 4.1 real-time CAN hubs, native parametric SolidWorks CAD as the mechanical source of
truth, and one kinematic contract shared by CAD, URDF/xacro, MuJoCo, Isaac Sim/Isaac Lab, ROS 2 and firmware.

> **Status (2026-09-24): v0.5 — the whole robot is designed, CAD-verified, FEA-checked and simulated; a manufacturing
> package exists.** Nothing has been built or physically tested. Every number carries a label:
> VERIFIED / MEASURED / CALCULATED / ESTIMATED / ASSUMED / UNVERIFIED.
> One-page summary: the generated [FINAL ROBOT SPECIFICATION](docs/final_robot_specification.md).
> **Want to build it? Start with the [build guide](docs/build_guide.md)** — what to buy, machine and print, and in what
> order. Short answer to "can I print the parts?": the leg, pelvis, torso and arm structure must be aluminium (every
> printed version failed the FEA); print only the head, covers, neck bracket, grippers — and PETG fit-check copies.

## Key results (v0.5)

| Area | Result | Evidence |
|---|---|---|
| CAD | 46 native parametric parts, fully constrained sketches, global variables; `JX1_LowerBody`, `JX1_UpperBody`, `JX1_Robot` assemblies with limit-mated joints | `CAD/`, `verification/cad_build_*.json` |
| Motion verification (SolidWorks vs analytic kinematics) | legs 25/25 poses each at 0.0000 mm / 0.0000°, 24/24 collision-free inside the coupled ankle limits; upper body 36/36 exact and collision-free (with the redesigned arms); whole robot 13/13 exact, 11/11 collision-free inside the controller limits (pre-arm-redesign, OI-25) | `verification/*motion_verification.json`, images |
| Structure (voxel FEA, actuator-capped loads) | every structural part passes in 6061/7075 (SF static 1.77–14.4, fatigue 1.58–24.7); every printed PA-CF variant fails (0.07–1.23) | [structural report](calculations/results/structural/report.md) |
| Actuator margins (CAD masses) | slow/nominal walking (≤ 0.52 m/s), turning and squat meet the 1.5× margin policy; the 0.79 m/s gait needs 37.0 N·m hip yaw vs RS06 36 N·m → speed cap ≈ 0.6 m/s or RS03 hip yaw (OI-2) | `calculations/results/iter2_C_cad_masses/` |
| Simulation | MuJoCo model from the CAD (33.61 kg, CoACD hulls): standing, squat, ZMP walking 4/4 gaits, push recovery 5.3–7.8 N·s; URDF + xacro (expansion checked) | `verification/mujoco_*.json`, `verification/xacro_check.json` |
| Trainable model (phase 3) | MuJoCo RL pipeline; interim walking policy verified sim-to-sim on the CAD model (7/7 scenarios upright), over ROS 2 and through the hub emulator (HIL); Isaac Lab task UNVERIFIED | [rl/README.md](rl/README.md), `rl/policies/jx1_walk_flat/` |
| Manufacturing | 24 STEP files, 14 A3 drawings (PDF), 24 PETG fit-check STLs, 3 print STLs | [manufacturing/index.md](manufacturing/index.md) |
| Cost (India, landed) | ₹7,12,481; ₹8,19,353 with 15 % contingency; actuators 77 % | [bom/cost_summary.md](bom/cost_summary.md) |
| Power | 13S2P 468 Wh: 92 W standing, 285 W walking at 0.52 m/s → ≈ 1.3 h walking, 4.1 h standing | `calculations/results/iter2_C_cad_masses/power_budget.json` |

## What changed in v0.5

- **FEA-driven aluminium structure everywhere.** Legs and pelvis (7075 hip-yaw bracket, 6061 elsewhere), and — after the
  upper-body FEA — torso and arms as 6061 plate. The upper arm was redesigned (10/8 mm plates + gussets: SF 5.99/4.84;
  the 6 mm version failed at 1.34/1.08) and a foot lightening hole moved off the clevis (fatigue 1.48 → 2.03).
- **CAD fixes found by verification:** arm connector clocking, E-stop bushing, shoulder pilot recess, head chamfer,
  hip-roll back plate clearance at full hip extension; negative-test poses mark states the controller must forbid.
- **Manufacturing package** with SolidWorks materials, drawings and PETG fit-check copies; **build guide**.
- **Simulation:** full-robot model regenerated from the final CAD; xacro description; MuJoCo walking and push tests.
- **Phase 3 trainable model** (built in parallel): RL training, ONNX export, sim-to-sim, ROS 2 packages
  (`jx1_policy`, `jx1_sim`, `jx1_bringup`, `jx1_hw` hardware bridge + hub emulator), Isaac Lab task.

## Repository map

| Folder | Contents |
|---|---|
| `research/` | [reference_robots.md](research/reference_robots.md) (29 humanoids), `raw/` evidence: actuators, Indian sourcing, electronics, power, manufacturing |
| `requirements/` | [robot_requirements.yaml](requirements/robot_requirements.yaml) — living requirements with status |
| `calculations/` | leg model, closed-form IK, ZMP preview control, floating-base inverse dynamics, parallel-ankle model, power budget; `structural/` voxel FEA, consistent load generator, variant studies |
| `actuators/` | [actuator_selection.md](actuators/actuator_selection.md), [modular_actuator_interface.md](actuators/modular_actuator_interface.md), [actuator_catalog.yaml](actuators/actuator_catalog.yaml) |
| `CAD/` | native parametric SolidWorks parts; `Assemblies/` (`JX1_Robot`, `JX1_LowerBody`, `JX1_UpperBody`); `Drawings/` |
| `tools/swlib`, `tools/cad` | SolidWorks COM automation (isolated JX1 session), part/assembly builders, motion + interference verifiers, mesh and manufacturing export |
| `manufacturing/` | [index](manufacturing/index.md): STEP, PDF drawings, fit-check and print STLs |
| `bom/` | [master_bom.csv](bom/master_bom.csv), [cost_summary.md](bom/cost_summary.md), generator `build_bom.py` |
| `docs/` | [build guide](docs/build_guide.md), [architecture](docs/architecture.md), [electrical wiring](docs/electrical_wiring.md), [safety](docs/safety_architecture.md), [risk register](docs/risk_register.md), [open issues](docs/open_issues.md), [final spec](docs/final_robot_specification.md) |
| `simulation/` | `joint_map.yaml` (kinematic contract), MuJoCo model + validation/walking/push tests, Isaac Sim import, Isaac Lab task, CAD meshes |
| `rl/` | RL training (MuJoCo), export (ONNX + `policy_io.yaml`), sim-to-sim, ROS 2 end-to-end and hardware-loop checks, trained policies |
| `ros2_ws/` | `jx1_description` (URDF + xacro from the CAD), `jx1_sim`, `jx1_policy`, `jx1_bringup`, `jx1_hw` (Jetson ↔ CAN-hub bridge) |
| `firmware/` | Teensy 4.1 CAN hub: RobStride protocol codec, 500 Hz scheduler, watchdogs, E-stop |
| `verification/` | machine-readable CAD / simulation evidence and images |

## Reproduce

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python calculations/tests/test_kinematics.py
.venv/Scripts/python calculations/structural/test_voxel_fea.py
.venv/Scripts/python bom/build_bom.py
```

SolidWorks 2026 is driven through COM in a **dedicated session** (`tools/swlib/instance.py`) so other SolidWorks work on
the same machine is never touched. Full CAD regeneration, verification and export (restart the JX1 session between the
heavy steps — the whole-robot assembly needs ≈ 10 GB):

```bash
.venv/Scripts/python tools/cad/build_actuators.py XL L M S XS
.venv/Scripts/python tools/cad/build_leg_parts.py --side L
.venv/Scripts/python tools/cad/build_leg_parts.py --side R
.venv/Scripts/python tools/cad/build_upper_parts.py
.venv/Scripts/python tools/cad/build_upper_parts.py --side R
.venv/Scripts/python tools/cad/build_leg_assembly.py --sides LR
.venv/Scripts/python tools/cad/verify_leg_motion.py --side L --images
.venv/Scripts/python tools/cad/build_upper_assembly.py
.venv/Scripts/python tools/cad/verify_upper_motion.py --images
.venv/Scripts/python tools/cad/build_robot_assembly.py
.venv/Scripts/python tools/cad/verify_robot_motion.py --images
.venv/Scripts/python tools/cad/export_meshes.py
.venv/Scripts/python tools/cad/make_manufacturing.py
```

Then the analysis and simulation chain (no SolidWorks needed):

```bash
.venv/Scripts/python calculations/structural/run_structural.py
.venv/Scripts/python tools/sim/build_robot_description.py
.venv/Scripts/python tools/sim/check_xacro.py
.venv/Scripts/python simulation/mujoco/validate_jx1.py
.venv/Scripts/python calculations/update_mass_budget_from_cad.py
.venv/Scripts/python calculations/run_leg_analysis.py --design calculations/results/variant_C_cad_masses.yaml --tag iter2_C_cad_masses
.venv/Scripts/python simulation/mujoco/walk_jx1.py
.venv/Scripts/python simulation/mujoco/push_jx1.py
.venv/Scripts/python tools/gen_final_spec.py
```

RL training, export and the ROS 2 checks: see [rl/README.md](rl/README.md).

## Development phases

1. **Walking lower body** — pelvis, hips, thighs, knees, shins, ankles, feet (12 DOF). *Designed, CAD-verified, FEA-checked, manufacturing package.*
2. **Upper body** — torso, battery bay, Jetson Nano, power distribution, shoulders, arms, grippers, head/sensors. *Designed, CAD-verified, FEA-checked; wiring routing and covers next.*
3. **Trainable model** — MuJoCo RL pipeline (`rl/`), Isaac Lab task (`simulation/isaac/isaaclab/`, UNVERIFIED), ROS 2 packages `jx1_policy` / `jx1_sim` / `jx1_bringup` / `jx1_hw`; a walking policy verified sim-to-sim on the CAD model, end-to-end over ROS 2 and through the hub emulator. Next: mass reduction, actuator system ID, hardware bring-up.

Top open decisions: actuator interface dimensions (OI-1), hip-yaw actuator vs walking speed (OI-2), commercial-use
licensing of the drawings (OI-19). See [open issues](docs/open_issues.md).
