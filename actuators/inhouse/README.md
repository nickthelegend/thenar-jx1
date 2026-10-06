# In-house actuators (JXA family): research paper and design tools

**[JXA_inhouse_actuator_research_paper.pdf](JXA_inhouse_actuator_research_paper.pdf)** (18 pages, 6 Oct 2026) covers:
- how a permanent-magnet motor makes torque, starting from magnetism;
- what is inside RobStride, Damiao, Unitree and other actuators;
- how much torque JX1 and full-size humanoids need;
- a three-class actuator family you can build;
- a step-by-step winding and build procedure;
- the costs of making them in India vs buying from China.

| Class | Peak / continuous | No-load at 48 V | Mass (est.) | Replaces | Batch cost (25/yr) | Buy (landed, China distributor) |
|---|---|---|---|---|---|---|
| JXA-40 | 41 / 13 N·m | 47.7 rad/s | 0.88 kg | RobStride RS06 | ₹19,777 | ₹17,059 |
| JXA-120 | 125 / 46 N·m | 23.1 rad/s | 1.91 kg | RobStride RS04 / RS03 | ₹30,292 | ₹24,091 |
| JXA-360 | 371 / 147 N·m | 18.6 rad/s | 4.27 kg | Unitree H1 knee class (no RobStride equivalent) | ₹61,822 | ₹65,194 (Damiao J10422P, USD list) |

All design values are CALCULATED (analytic model, ±15–30 %); all costs are ESTIMATED from cited listings. Nothing has been
built yet. The model reproduces the RobStride RS04 datasheet within 3–20 % (K<sub>t</sub>, K<sub>e</sub>, R, L, peak current).

**Short answer:**
- You can build these yourself with a ₹3.2 lakh test kit and Indian job shops; winding is the main skill.
- Below about 900–1,000 units a year, building costs more than importing RobStride.
- Making them is worth it for learning, for the 360 N·m class (nobody sells it cheaply) and for supply security.

## Files

| File | What it does |
|---|---|
| `qdd_design.py` | Motor + gearbox + thermal design of the three classes → `results/design.json`, `results/variants.json`, `figures/torque_speed.png`, `figures/winding_layouts.png`, `figures/jxa120_section.png` |
| `cost_model.py` | Make-vs-buy cost at prototype / batch / 1,000-per-year scale, equipment budgets, scenarios, break-even → `results/cost.json`, `figures/cost_*.png` |
| `paper_text.py` | Fixed text of the paper (physics primer, winding procedure, build sequence) |
| `make_paper.py` | Builds the PDF from the results (HTML printed with headless Chromium) |

Run them in this order:

```
python actuators/inhouse/qdd_design.py
python actuators/inhouse/cost_model.py
python actuators/inhouse/make_paper.py
```

Requirements: numpy, matplotlib, and a Chromium or Chrome binary.

## Research logs used

All under `research/raw/`:
- `actuator_internals_and_torque_raw.md` (new): what is inside commercial actuators, full-size humanoid torques, human joint moments, gear practice.
- `india_motor_materials_raw.md` (new): copper wire, NdFeB magnets, laminations, stator cores, bearings, driver ICs, metal 3D printing, winding and test equipment.
- `china_actuator_manufacturing_economics_raw.md` (new): RobStride, Unitree and other makers; cost structure; capex; wages; rare-earth export rules; import duty.
- `actuator_technology_raw.md`, `india_mechanical_manufacturing_raw.md`, `india_electronics_compute_raw.md` (existing).
