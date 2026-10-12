# JXC-5010: 3D-printed cycloidal actuator from a 5010 drone motor

**[JXC5010_cycloidal_actuator_build_plan.pdf](JXC5010_cycloidal_actuator_build_plan.pdf)** is the full design and build plan,
4 pages in IEEE paper style.

| | |
|---|---|
| Motor | 5010 360KV outrunner (Robu, ₹2,239), kept from the original choice |
| Driver | **ST B-G431B-ESC1** (40 A peak, CAN, USB, ~US$19) instead of the SimpleFOCmini (2.5 A), which caps torque at ≈ 1 N·m |
| Gearbox | single-stage **dual-disc cycloidal, 20:1**: 21 Ø4 steel ring pins on R32, e = 1 mm, 6 output pins with MR74ZZ rollers |
| Expected | ≈ 8 N·m peak (2–3 s), ≈ 4 N·m continuous, ≈ 45 rad/s no-load at 24 V, Ø82 × 64 mm, ≈ 0.46 kg (CALCULATED) |
| Parts cost | ≈ ₹10,000 including a 24 V bench supply (BOM in the PDF) |

All performance numbers are CALCULATED and must be confirmed with the tests in the PDF (Section IX). At this size the **printed
discs, not the motor, limit torque** (≈ 10 N·m peak, ≈ 4 N·m continuous in PLA/PETG). A more expensive motor mostly buys cooler
running; for more torque, scale up the stage or have the discs laser-cut from metal.

## Files

| Path | What |
|---|---|
| `cycloid_actuator.py` | Motor/driver comparison, cycloid geometry and stress checks, CAD export, figures → `results/jxc5010.json` |
| `make_plan.py` | Builds the PDF from the results (LaTeX/IEEEtran; uses `../inhouse/latex_tools.py`) |
| `cad/*.stl` | Print files: `cycloid_disc_x2` (print two), `ring_pin_housing`, `output_carrier`, `eccentric_cam_MEASURE_FIRST`, `motor_adapter_MEASURE_FIRST`, `motor_spacer_ring`, `output_retainer_ring` |
| `cad/*.dxf` | The same outlines in 2-D, e.g. to laser-cut metal discs or to edit in CAD |
| `figures/` | Layout, section, parts and torque figures used in the PDF |

**Measure your motor before printing the two `MEASURE_FIRST` parts.** They assume a 25 mm base bolt circle (4 × M3) and a 16 mm
propeller-mount bolt circle on the bell. Change `motor_bolt_pcd` and `prop_pcd` in `export_cad()` and re-run. Print a test coupon first
to tune the pin-hole press fit (`d_pin`) and the bearing bore.

```
python actuators/diy_cycloid/cycloid_actuator.py   # needs numpy matplotlib shapely trimesh manifold3d mapbox_earcut ezdxf
python actuators/diy_cycloid/make_plan.py          # needs TeX Live with IEEEtran
```
