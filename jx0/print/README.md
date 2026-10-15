# JX0 print plates

The plates are made by `python tools/print/make_plates.py`. The script orients every part the way the build guide says,
lays each plate out, and slices it. Settings: 0.2 mm layers, Textured PEI plate, tree supports.
- PETG: 6 walls, 40 % gyroid, 240 / 80 °C.
- PLA: 3 walls, 25 % gyroid, 210 / 60 °C.

`python tools/print/verify_plates.py` checks every plate before printing:
- every part of the build guide's table is on a plate, in its quantity and material;
- each part stands on a flat face with its centre of mass over it;
- no two parts touch;
- in the G-code: the printer's own start G-code, the print temperatures (PETG 240 / 80 °C, PLA 210 / 60 °C), walls, infill and supports, every move inside the bed, and every part printed from the bed to its top.

Result: 0 problems (`verify_plates.json`). Filament: PETG 654 g, PLA 462 g.

The sliced files are not in git; re-run the script to make them. Each plate folder holds:
- `<plate>.stl`: the laid-out plate.
- `<plate>.gcode.3mf`: open it in Bambu Studio.
- `<plate>.gcode`: plain G-code.

| Order | Plate | Printer | Filament | Time | Parts |
|---|---|---|---|---|---|
| 1 | P1S-0_test_shin | P1S | PETG | 1.8 h | Shin L. **Fit a servo in it before printing the rest** |
| 2 | P1S-1_pelvis_hip_yaw | P1S | PETG | 7.5 h | Pelvis, hip-yaw brackets, keepers, yaw rings |
| 2 | i7-1_thighs_ankles | i7 | PETG | 10.2 h | Thighs, ankle brackets |
| 3 | P1S-2_feet_hip_roll | P1S | PETG | 7.2 h | Feet, hip-roll brackets |
| 3 | i7-2_torso_head | i7 | PLA | 11.0 h | Torso, head, neck hub |
| 4 | P1S-3_shin_shims | P1S | PETG | 2.3 h | Shin R, 40 horn shims |
| 5 | P1S-4_chest_arms | P1S | PLA | 5.5 h | Chest cap, upper arms, arm blades |

How to print on each printer:
- **P1S:** open the `.gcode.3mf` in Bambu Studio, then Print plate.
- **i7:** send the `.gcode` from Creality Print, or put it on USB. The file calls START_PRINT / END_PRINT with the plate's temperatures. With a CFS, load the filament in slot 1.
