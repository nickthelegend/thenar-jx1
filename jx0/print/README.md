# JX0 print plates

The plates are made by `python tools/print/make_plates.py`. The script orients every part the way the build guide says,
lays each plate out, and slices it. Settings: 0.2 mm layers, Textured PEI plate, tree supports.
- PETG, pelvis and leg parts (red, on the i7): 6 walls, 40 % gyroid, 240 / 80 °C.
- PLA, body parts (white, on the P1S): 3 walls, 25 % gyroid, 210 / 60 °C. The eye lenses: clear PETG, 3 walls.

`python tools/print/verify_plates.py` checks every plate before printing:
- every part of the build guide's table is on a plate, in its quantity and material;
- each part stands on a flat face with its centre of mass over it;
- no two parts touch;
- in the G-code: the printer's own start G-code, the print temperatures (PETG 240 / 80 °C, PLA 210 / 60 °C), walls, infill and supports, every move inside the bed, and every part printed from the bed to its top.

Result: 0 problems (`verify_plates.json`). Filament: PETG 714 g red (legs) + PLA 626 g white (body) + 6 g clear PETG (lenses).

The plates use the parts with their lettering (`jx0/cad/engrave.py`, 0.6 mm deep):
- torso front: JX0 and JNTUH's 1st Humanoid Robot;
- torso back: thenar.io and JX0;
- chest band: thenar.io;
- both arm blades: JX0.

For contrast, fill the letters with an acrylic paint marker and wipe off the excess.

The sliced files are not in git; re-run the script to make them. Each plate folder holds:
- `<plate>.stl`: the laid-out plate.
- `<plate>.gcode.3mf`: open it in Bambu Studio.
- `<plate>.gcode`: plain G-code.

| Order | Plate | Printer | Filament | Time | Parts |
|---|---|---|---|---|---|
| 2 | i7-1_pelvis_hip_yaw | i7 | PETG (red) | 9.2 h | Pelvis, hip-yaw brackets, keepers, yaw rings |
| 3 | i7-2_feet_hip_roll | i7 | PETG (red) | 8.4 h | Feet, hip-roll brackets |
| 4 | i7-3_shins_shims | i7 | PETG (red) | 4.9 h | Both shins, 40 horn shims |
| 5 | i7-4_thighs_ankles | i7 | PETG (red) | 11.7 h | Thighs, ankle brackets |
| 6 | i7-5_eye_lenses | i7 | PETG, **clear** (swap the spool) | 0.2 h | The two eye lenses |
| 1 | P1S-1_torso_head | P1S | PLA (white) | 16.2 h | Torso (camera shelves inside), head, neck hub |
| 2 | P1S-2_chest_arms | P1S | PLA (white) | 4.6 h | Chest cap, upper arms |
| 3 | P1S-3_blades_clamp | P1S | PLA (white) | 1.5 h | Arm blades, camera clamp |

How to print on each printer:
- **P1S:** open the `.gcode.3mf` in Bambu Studio, then Print plate.
- **i7:** send the `.gcode` from Creality Print, or put it on USB. The file calls START_PRINT / END_PRINT with the plate's temperatures. With a CFS, load the filament in slot 1.
