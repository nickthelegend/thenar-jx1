# JX1 safety architecture (v0.3)

JX1 carries ≈ 468 Wh of Li-ion energy and 21 actuators of up to 120 N·m. Safety is designed in from V1; nothing here is
certified — it is an engineering prototype.

## 1. Stop functions

| Function | Implementation | Category |
|---|---|---|
| Emergency stop | Schneider XB2BS8442C (twist-release, NC). Breaks the enable loop of the motor-bus MOSFET switch **and** signals both hubs (second NC contact to a hub GPIO) | IEC 60204-1 cat. 0 (power removal); robot must be on a gantry/harness during bring-up |
| Software stop | Hub commands MIT-mode zero-velocity damping on every joint, then disables after 2 s | cat. 1-like |
| Communication loss | Hub: no host message for 50 ms → damping; RobStride: CAN timeout (configurable) → stop | — |
| Fault latch | Any actuator fault (over-current, over-temp, encoder) → hub latches → damping on that limb → disable | — |

## 2. Electrical protection

| Hazard | Protection |
|---|---|
| Pack over-/under-voltage, over-current, short, over-temperature | JBD 13S smart BMS (40 A) |
| Branch over-current | 4 × Littelfuse 30 A **58 V** ATO fuses (car fuses rated 32 V are NOT used on the 54.6 V bus) |
| Inrush / arcing on connection | XT90-S anti-spark battery connector + Flipsky anti-spark switch precharge |
| Motor regeneration into a full pack | BMS charge-current limit; hub limits braking torque when bus > 54 V (planned) |
| Charging | dedicated 54.6 V 6 A Li-ion charger; charge outside the robot on a non-flammable surface; LiPo bag |

## 3. Motion limits (firmware)

- **Joint limits:** soft limits = `simulation/joint_map.yaml` limits minus 2°; ankle uses a pitch–roll polygon (open issue OI-3).
- **Current limits:** 80 % of each class's peak phase current; continuous limit from the thermal model.
- **Temperature:** derate from 100 °C winding estimate, stop at 130 °C (RobStride limit 145 °C).
- **Self-collision:** hip-roll adduction > ≈ 8° with the other leg vertical causes leg–leg contact (verified in CAD) → controller
  self-collision check using `simulation/` collision meshes.

## 4. Safe start-up and shutdown

1. Power on with the motor bus switch **open**; Jetson + hubs boot from the aux rail.
2. Hubs enumerate all 21 actuators, read absolute encoders, compare with the stored zero offsets (tolerance 3°).
3. Close the motor-bus switch (precharge), enable joints in **damping mode**, then ramp PD gains over 2 s.
4. Shutdown: crouch-and-sit routine → damping → disable → open the bus switch.

## 5. Pinch and crush zones

| Zone | Risk | Mitigation |
|---|---|---|
| Back of the knee (thigh plate vs shin, RS04 120 N·m) | finger crush up to 120° flexion | knee cover, keep hands clear, reduced gains in teach mode |
| Ankle crank – push rod – foot | pinch between rod and motor housing / foot | printed crank guard (phase 3 covers) |
| Hip yaw bracket under the pelvis | shear between rotating bracket and pelvis bottom plate | 7 mm gap; cover |
| Leg–leg (adduction) | pinch between shins | software self-collision limits |
| Gripper (phase 3) | pinch | force limit |

## 6. Test safety

- All leg bring-up on a lifting gantry (2020/4040 extrusion frame, ₹9–12k ESTIMATED) with a chest harness.
- Single-joint tests with the leg clamped before any closed-loop standing.
