# JX1 unresolved issues (v0.3, 2026-09-24)

| ID | Issue | Evidence | Next action | Blocks |
|---|---|---|---|---|
| OI-1 | MAI bolt-circle diameters, thread sizes and pilot diameters are ASSUMED; RobStride STEP models and dimensioned outlines exist (manual §1.1) | `actuators/modular_actuator_interface.md` | dimension RS00/02/03/04/06 drawings → update `tools/cad/params.py` → rebuild CAD (fully parametric) | ordering CNC parts |
| OI-2 | Hip yaw peak requirement 37.3 N·m vs RS06 36 N·m (−3 %) | `calculations/results/iter1_B_knee_and_pitch_RS04/requirements.yaml` | decide: controller torque cap vs RS03 hip yaw (+0.26 kg/leg) after RL gait torque logs | — |
| OI-3 | Ankle corner (+30° plantarflexion with −20° roll): rod B touches motor B housing (≈ 560 mm³ envelope overlap) | `verification/leg_motion_verification_*.json` pose `ankle_corner_2` | compute the collision-free pitch–roll polygon in CAD; implement as firmware limit; V2 crank neutral offset | final ankle limits |
| OI-4 | No structural FEA yet on printed PA-CF brackets (hip yaw/roll brackets, shin) under RS04 peak torque and impact loads | — | hand calcs + SolidWorks Simulation (if licensed) or CalculiX; printed coupon tests | release of printed parts |
| OI-5 | Part materials are not assigned inside SolidWorks; simulation mass properties use documented densities (PA-CF 800 kg/m³ effective) | `simulation/mass_properties.json` | assign materials in parts; weigh first printed parts; update densities | accurate URDF inertias |
| OI-6 | Knee flexion limited to 120° (target ≥ 135° for get-up/kneel) | CAD verification | V2 knee-at-hip linkage study | get-up behaviours |
| OI-7 | Leg–leg contact beyond ≈ 8° hip adduction with the other leg vertical | CAD verification (inter-leg contacts) | self-collision constraints in controller/RL; consider 0.21 m hip spacing | — |
| OI-8 | Upper body (torso, arms, head, battery bay, electronics tray) not yet in CAD; simulation uses a 12 kg torso placeholder | `tools/sim/build_robot_description.py` | phase-2 CAD | full-robot sim |
| OI-9 | Actuator rotor inertia / phase resistance not published — armature and copper-loss values ESTIMATED | `actuators/actuator_catalog.yaml` | bench sys-ID (torque–speed, thermal, friction) | accurate sim + runtime |
| OI-10 | Hole-pattern clocking between actuator envelopes and brackets not yet aligned after the 90° connector clocking | CAD | align patterns once OI-1 values are known | drawings |
| OI-11 | Manufacturing drawings not yet generated (thigh plate, crank, ankle cross are CNC/turned parts) | — | SolidWorks drawings + PDF after OI-1 | ordering |
| OI-12 | CNC/turning prices are ESTIMATED (no public per-part pricing in India) | `bom/master_bom.csv` | request Makenica / local quotes | cost accuracy |
| OI-13 | GitHub remote `nickthelegend/thenar-jx1` does not exist and the available token cannot create repositories | `git push` → "Repository not found" | owner creates the empty private repo (or grants Administration: write) → `git push -u origin main` | publishing |
