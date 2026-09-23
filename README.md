# JX1 — low-cost compact humanoid (India build)

JX1 is an engineering project to design the **lowest-cost practical compact humanoid that can realistically be built in India**:
~1.2 m tall, 12-DOF walking legs first, distributed CAN joint control, NVIDIA Jetson Nano high-level compute,
native parametric SolidWorks CAD as the mechanical source of truth, and a consistent model across ROS 2, MuJoCo and Isaac Sim.

> Status: **Phase 1 — research & requirements.** Nothing has been built or physically tested yet.
> Every number in this repository is labelled VERIFIED / MEASURED / CALCULATED / ESTIMATED / ASSUMED / UNVERIFIED.

## Repository map

| Folder | Contents |
|---|---|
| `research/` | Reference-robot study, actuator technology, Indian supplier research (`raw/` holds agent-collected evidence) |
| `requirements/` | `robot_requirements.yaml` — the living system requirements |
| `calculations/` | Leg geometry, torque/speed, battery, structural calculations (Python, reproducible) and results |
| `actuators/` | Actuator classes, modular actuator interface specification |
| `CAD/` | Native SolidWorks parts & assemblies (Actuators, Pelvis, Hip, Thigh, Knee, Shin, Ankle, Foot, Torso, Arms, Head, Electronics, Hardware, Assemblies, Drawings) |
| `tools/` | SolidWorks COM automation and pipeline scripts |
| `bom/` | `master_bom.csv` (INR) and cost summaries |
| `docs/` | Architecture, electrical, safety, assembly, risk register, open issues |
| `simulation/` | `joint_map.yaml`, URDF/Xacro, MuJoCo MJCF, Isaac Sim assets |
| `ros2_ws/` | ROS 2 description package |
| `manufacturing/` | Drawings and print files |
| `verification/` | Joint, collision, mass-property and simulation evidence |
| `firmware/` | Joint-controller / CAN protocol reference firmware |

## Development phases

1. **Walking lower body** — pelvis, hips, thighs, knees, shins, ankles, feet (12 DOF). *Highest priority.*
2. **Upper body** — torso, battery, Jetson Nano, power distribution, shoulders, arms, simple grippers, head/sensors.
3. **Optimisation** — covers, appearance, hands, sensors, autonomy.

## Python environment

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
```
