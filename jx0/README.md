<p align="center">
  <img src="docs/images/jx0_cover.png" alt="JX0 v0.3: SolidWorks front and back views, and the simulated robot walking with its arms swinging" width="100%">
</p>

<h1 align="center">JX0: a walking, talking STS3215 humanoid you can build at home</h1>

<p align="center">
  <b>54 cm · 2.4 kg · 17 joints, every one a Feetech STS3215 12 V · walks with its arms swinging · talks (Claude) ·
  ₹58,548 in parts</b><br>
  3D-printed in pastel green, styled after a friend's working STS3215 robot. Full SolidWorks CAD, a verified walking
  simulation, the robot program and a parts list with Indian suppliers are all in this folder.
</p>

<p align="center">
  <a href="docs/build_guide.md"><b>Build guide</b></a> ·
  <a href="bom/jx0_bom.csv"><b>Parts list</b></a> ·
  <a href="bom/JX0_cost_estimate.pdf"><b>Cost estimate (PDF)</b></a> ·
  <a href="docs/wiring.md"><b>Wiring</b></a> ·
  <a href="docs/bringup.md"><b>Bring-up</b></a> ·
  <a href="docs/software_setup.md"><b>Software</b></a> ·
  <a href="#try-it-on-your-pc">Try it on your PC</a>
</p>

---

## Watch it

<p align="center">
  <a href="results/images/jx0_demo.mp4"><img src="results/images/jx0_demo.webp" alt="Simulated JX0 waving, walking with its arms swinging, taking a side push and kicking over a bottle" width="720"></a><br>
  <sub><b><a href="results/images/jx0_demo.mp4">Demo film (MP4)</a></b>, staged like the reference video: JX0 walks on
  a wooden floor with its arms swinging, waves, takes a push from the side while walking and keeps going, and kicks
  over a plastic bottle. The robot's own program (<code>software/jx0bot</code>, the same code that runs on the Pi)
  drives the SolidWorks robot in MuJoCo; the push and the bottle are plain physics.</sub>
</p>

<p align="center">
  <img src="docs/images/jx0_cad_timelapse.webp" alt="SolidWorks timelapse: the JX0 parts built feature by feature, then the assembly" width="520"><br>
  <sub>Built in SolidWorks by script (<code>cad/build_cad.py</code>, <code>cad/build_assembly.py</code>). Timelapses:
  <a href="../media/jx0_cad_timelapse_v03.mp4">v0.3 (63 s)</a> ·
  <a href="../media/jx0_cad_timelapse.mp4">every version, from the first parts (99 s)</a>.</sub>
</p>

## The reference robot

JX0 v0.3 copies a friend's robot: a small biped printed in pastel green with **every joint a 12 V STS3215**, a faceted
body, an exposed neck servo under a soft rounded head, and flat blade arms that swing as it walks. It walks steadily,
takes a shove, and knocks over a bottle on the way. JX0 matches that:

| On the reference robot | On JX0 v0.3 |
|---|---|
| 12 V STS3215 in every joint | 17 × Feetech STS3215 12 V (Evelta lists it as ST3215-C018), all on one serial bus |
| pastel green print | eSun PLA-Matte Mint Green (PETG for hot-running leg brackets) |
| faceted torso, vents on top, seam below the shoulders | octagonal torso with chamfered vertical edges; lower shell + chest cap with chamfered top edges, vent slots and a speaker grille |
| black neck servo exposed under the head | neck STS3215 standing on the chest cap |
| soft rounded head with four holes | rounded head, narrower at the chin, four holes in a diamond (the microphone listens through them) |
| shoulder cradle holding a servo, flat tapered arm | shoulder STS3215 in the chest cap, cradle holding the elbow STS3215, flat tapered blade |
| round-ended leg plates, cross-pattern horn screws | the same, on JX0's verified 6-DOF legs |
| walks with the arms swinging, takes a shove | gaits verified with a 1.6× counter-swing; survives a 0.7 N·s side push mid-walk in simulation (see below) |
| runs off a 12.6 V bench supply | 3S LiPo, or a 12.6 V bench supply on the same XT60 |

## Honest status

| | Status |
|---|---|
| SolidWorks CAD: 20 printed parts + all 17 servos in the assembly | **done**, every part rebuilt by script, one body each, no errors |
| Servo sizing (every leg joint, 5 gaits + static cases), 2.43 kg robot | **passes**; the tightest is hip roll with a 1.70× margin |
| Walking in simulation, on the CAD masses and a servo model | **14 of 14 gaits pass** with arm swing (forward 0.067 m/s, backward, turns, side-steps) |
| Push recovery in simulation (sideways shove on the torso mid-walk) | survives **0.72 N·s** (a light tap; it tilts 10° and walks on); falls at 1.08 N·s. The reference robot takes harder shoves, so stepping to catch itself is the next controller upgrade |
| Robot program (voice, Claude brain, walking, gestures) | **written and run in simulation**; not yet on hardware |
| Parts list | ₹58,548; STS3215 price and stock (48) checked 2026-10-04 |
| Physical robot | **not built yet**: this is what the funding is for |

Unverified until the robot is built, and the first things to check: the servo stiffness setting, the M2 screw fit in
the printed holes, the I2S audio overlay, and battery life (about 1 h of walking, ESTIMATED from the 7–19 W the
reference robot drew on its bench supply).

## What it can do

| Ask it… | It… |
|---|---|
| "Hi!" / any question | answers out loud in one to three sentences (Claude) |
| "Walk forward five steps" / "go back" / "step left" | plays the gait blocks verified in simulation, arms swinging, with IMU balance on the stance leg |
| "Turn around" | repeats 10° turn blocks until the IMU says it has turned far enough (in simulation −60° → −59°) |
| "Wave at me" | raises an arm up in front and wags the blade |
| "Look left" / "yes or no?" | turns its head; bows for yes, shakes its head for no |

## JX0 at a glance

| | |
|---|---|
| Height, mass | 53.7 cm, 2.43 kg (CAD) |
| Joints | 17 Feetech STS3215 12 V serial bus servos: 6 per leg, shoulder pitch and elbow per arm, neck yaw |
| Brain | Raspberry Pi 4 (2 GB): gaits at 50 Hz, MPU6050 balance, Vosk speech recognition, Piper voice, Claude over Wi-Fi |
| Power | 3S 2200 mAh LiPo straight to the servo bus (12 V servos); a 5 V UBEC for the Pi; or a 12.6 V bench supply |
| Structure | 20 printed parts, 415 g, pastel green |

## What it costs

| Group | ₹ |
|---|---|
| Servos: 17 × STS3215 | 41,123 |
| Electronics: Pi 4, microSD, servo driver, button, wiring | 9,219 |
| Structure: filament, screws, inserts, rubber | 4,388 |
| Power: LiPo, charger, UBEC, switch, wire, alarm | 3,122 |
| Voice: microphone, amplifier, speaker | 569 |
| Sensors: IMU | 127 |
| **Total** | **58,548** |

Line by line with store links: [bom/jx0_bom.csv](bom/jx0_bom.csv). The 17 servos are 70 % of the cost. JX0 is
₹8,548 over the original ₹50,000 target because every joint is an STS3215, as on the reference robot. The walking needs
1.73 N·m of peak torque at the hip roll (with the 1.5× margin), which rules out MG996R-class hobby servos, and the
serial bus servos also report their position, which the calibration and the balance loop use.

## How it works, in plain words

- **Walking.** A planner (the same one designed for JX1) works out where the body's balance point must be at every
  instant for a given step length and speed, then computes the 12 leg joint angles 50 times a second. The arms
  counter-swing with the opposite leg, like the reference robot. Those trajectories were run on a physics model of this
  exact robot, with a model of how the servos really behave (they give a little under load and slow down when pushed
  hard). Only the gaits that passed are shipped in `software/jx0bot/gaits/`. On the robot, the IMU corrects the ankles
  and hips as it walks.
- **Talking.** A button, or saying "hey robot", starts listening. Vosk turns speech into text on the Pi itself. Claude
  writes a short spoken reply and can call the robot's actions as tools. Piper speaks the reply sentence by sentence
  through the speaker under the chest grille.
- **One bus.** All 17 servos are chained on one serial bus from a small driver board on the Pi's USB. There's no PWM
  wiring, and every joint reports its angle.

## Try it on your PC

No hardware needed. Install the packages, then talk to the simulated robot by typing:

```bash
pip install -r jx0/software/requirements-pc.txt
```

```bash
cd jx0/software && python -m jx0bot.main --sim --text
```

It needs an `ANTHROPIC_API_KEY`. Without one, you can still run three things:
- `python jx0/sim/demo_jx0.py` renders the demo film.
- `python jx0/sim/walk_jx0.py` reruns every walking check.
- `python jx0/cad/preview.py` builds and renders the robot from the geometry, with no SolidWorks needed.

## How it was designed and checked

| Step | Tool | Result |
|---|---|---|
| Design point: sizes, masses, joint ranges | [design_point.yaml](design_point.yaml) | every value labelled VERIFIED / CALCULATED / ESTIMATED / ASSUMED |
| Servo sizing | [analysis/sizing.py](analysis/sizing.py) → [results/sizing.md](results/sizing.md) | peak ×1.5 ≤ stall, RMS ×1.3 ≤ rated, inside the torque-speed line: **all pass** |
| CAD | [cad/geometry.py](cad/geometry.py) → SolidWorks by script | 20 printed parts, assembly with all 17 servos, masses fed back into the design point |
| Walking | [sim/walk_jx0.py](sim/walk_jx0.py) → [results/walking.json](results/walking.json) | 14/14 gaits with arm swing: tilt ≤ 1.0°, final position error ≤ 7 mm, servo peaks ≤ 78 % of stall |
| Push recovery | [sim/walk_jx0.py](sim/walk_jx0.py) → `walking.json` `push_test` | survives 0.72 N·s mid-walk, falls at 1.08 N·s |
| Whole robot program | [sim/demo_jx0.py](sim/demo_jx0.py) | every action runs on the simulated robot; it takes a 0.72 N·s side push and kicks a bottle over |

| Gait | Speed | Distance plan → sim | Heading error | Max tilt | Peak servo load |
|---|---|---|---|---|---|
| forward (10 steps) | 0.067 m/s | 0.340 → 0.338 m | 0.0° | 0.9° | 78 % |
| forward slow | 0.050 m/s | 0.195 → 0.194 m | 0.0° | 0.9° | 76 % |
| backward | 0.042 m/s | 0.163 → 0.156 m | 0.0° | 1.0° | 76 % |
| turn left 70° / right 70° | — | — | −1.3° / +1.3° | 1.0° | 76 % |
| side-step left | — | 0.075 → 0.074 m | +0.1° | 0.9° | 76 % |

## Folder map

| Path | What |
|---|---|
| `design_point.yaml` | the numbers everything else reads |
| `analysis/` | servo sizing |
| `cad/` | geometry, SolidWorks build scripts, `preview.py`, `parts/*.SLDPRT`, `JX0_Robot.SLDASM`, `stl/` for printing |
| `sim/` | MuJoCo model, walking checks, demo film |
| `software/jx0bot/` | the robot program (see [software_setup.md](docs/software_setup.md)) |
| `bom/` | parts list and the cost PDF |
| `docs/` | build guide, wiring, bring-up, software setup |
| `results/` | sizing and walking results, images and films |
