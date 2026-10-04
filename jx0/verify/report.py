"""Collect the verification results into jx0/results/verification.md (run by run_all.py, or on its own)."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "jx0" / "results"


def load(name):
    p = RES / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def tests_summary():
    r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "jx0/software/tests"], cwd=ROOT,
                       capture_output=True, text=True)
    tail = (r.stderr or r.stdout).strip().splitlines()
    ran = next((line for line in tail if line.startswith("Ran ")), "Ran ? tests")
    return ran, tail[-1] if tail else "?"


def pct(d, key="passed"):
    n = d[key]
    return f"{n}/{d['trials']} ({100 * n / max(1, d['trials']):.0f} %)"


def main():
    walk, cad, rob, pw, siz, st, fea = (load(n) for n in ("walking.json", "verify_cad.json", "verify_robustness.json",
                                                            "verify_power.json", "sizing.json", "verify_strength.json",
                                                            "verify_fea.json"))
    gaits = walk.get("gaits", {})
    n_pass = sum(g["pass"] for g in gaits.values())
    fin, mis = rob.get("final", {}), rob.get("mission", {})
    ran, status = tests_summary()
    peak = max((max(g["peak_torque_fraction_of_stall"].values()) for g in gaits.values()), default=0)
    L = ["# JX0 verification report", "",
         f"Generated {date.today().isoformat()} by `jx0/verify/run_all.py` from the CAD geometry, the MuJoCo model and the robot "
         "software in this repository (design v0.4: double-sided legs like the reference robot). Everything here is "
         "simulation and analysis: the physical robot is not built yet, so the numbers say the design should work, not that "
         "it has been seen working.", "",
         "## Summary", "",
         "| Check | Result |", "|---|---|"]
    L.append(f"| Servo sizing (every leg joint, 5 gaits + 8 static cases, 1.25–1.5x margins) | {'**ALL PASS**' if siz.get('all_pass') else 'FAIL'} |")
    L.append(f"| The 14 robot gaits, closed loop on the servo model (100 Hz) | **{n_pass}/{len(gaits)} pass**, peak servo load {peak:.0%} of stall |")
    if cad:
        sw = cad["joint_sweeps"]
        L.append(f"| Parts and servos colliding, standing (all {cad['static_zero_pose']['pairs_checked']} pairs) | "
                 f"{len(cad['static_zero_pose']['clashes']) + len(cad['static_walking_stance']['clashes'])} clashes |")
        L.append(f"| Parts colliding in motion ({cad['motion']['poses_checked']} poses: every gait frame + every action) | "
                 f"{len(cad['motion']['clashes'])} clashes |")
        L.append(f"| Joint limits inside the collision-free range | {sum(v['ok'] for v in sw.values())}/{len(sw)} joints |")
    if st:
        j = st["joints"]
        v3 = [r["v03_single_sided"]["fatigue_safety"] for r in j.values()]
        v4 = [r["v04"]["fatigue_safety"] for k, r in j.items() if k != "hip_yaw"]
        L.append(f"| Leg joints: single-sided (v0.3) vs double-sided (v0.4), beam model, fatigue safety factor | "
                 f"v0.3 {min(v3):.2f}–{max(v3):.2f} (**would break**) → v0.4 **{min(v4):.1f}–{max(v4):.1f}** |")
    if fea:
        p = fea["parts"]
        L.append(f"| Printed leg brackets, voxel FEA under the simulated loads, worst bracket | fatigue SF "
                 f"**{min(r['fatigue_safety'] for r in p.values()):.1f}**, strength SF **{min(r['static_safety'] for r in p.values()):.1f}** |")
    if fin:
        L.append(f"| Walking with realistic model errors (latency 0–20 ms), all gaits | **{pct(fin['model_errors_latency_0_20ms'])}** |")
        L.append(f"| Same, stress test with 40 ms latency | {pct(fin['model_errors_latency_40ms_stress'])} |")
        for k, v in fin["pushes_mid_walk"].items():
            if "stayed_up" in v:
                L.append(f"| Sideways push of {k} mid-walk (24 moments × 2 directions): stayed up | {pct(v, 'stayed_up')} |")
    if mis:
        L.append(f"| Whole robot program, 8-step mission, random realistic errors | **{pct(mis)}** |")
    if pw:
        w = pw["walking_forward"]
        L.append(f"| Battery current walking (servos + Pi) | {w['total_avg_a']} A average, {w['total_peak_a']} A peak → about "
                 f"{pw['battery']['walking_minutes_80pct']} min walking per charge |")
        L.append(f"| 100 Hz control loop on a Raspberry Pi 4 (estimated) | {pw['realtime']['frame_used_ms_pi4_est']} ms of "
                 f"{pw['realtime']['frame_ms']:.0f} ms |")
    L.append(f"| Software unit tests | {ran}: {status} |")

    if st:
        L += ["", "## Leg joints: why double-sided", "",
              "Every leg joint's load from the simulation (14 gaits, 42 walks with model errors, 48 pushes of 0.96 N·s), and what "
              "it does to a single-sided joint (v0.3: one plate on the servo's horn) and to a U-bracket on both faces (v0.4). The "
              "servo only *drives* the torque about its axis; the bending moment about the other two axes is what the "
              "structure carries. On a single-sided joint it all goes through one printed plate and the servo's output shaft. "
              "In a U-bracket it becomes a pair of forces in the two arms, 42.75 mm apart, and the output shaft sees no bending "
              f"at all. PETG ASSUMED: {st['petg_strength']['along_layers_mpa']:.0f} MPa static, "
              f"{st['petg_strength']['fatigue_1e6_mpa']:.0f} MPa fatigue (10^6 cycles, about 700 hours of walking).", "",
              "| Joint | Torque N·m | Bending at the horn N·m | v0.3 plate MPa (fatigue SF) | v0.4 MPa (fatigue SF) | Servo shaft bending N·m, v0.3 → v0.4 |",
              "|---|---|---|---|---|---|"]
        for k, r in st["joints"].items():
            a, b, lw = r["v03_single_sided"], r["v04"], r["loads_worst_with_pushes"]
            L.append(f"| {k.replace('_', ' ')} | {lw['torque_nm']:.2f} | {lw['bending_horn_nm']:.2f} | {a['walking_mpa']} ({a['fatigue_safety']}) | "
                     f"{b['walking_mpa']} ({b['fatigue_safety']}){' — single-sided + thrust ring' if k == 'hip_yaw' else ''} | "
                     f"{a['shaft_bending_worst_nm']} → {b['shaft_bending_worst_nm']} |")
    if fea:
        L += ["", "## Printed leg brackets: finite elements", "",
              "Voxel FEA (`calculations/structural/voxel_fea.py`, 0.7 mm hexahedra with bending modes). Each bracket is held "
              "where it bolts to the servo above it (horn and rear hub) and loaded where the next servo is screwed into its cage, "
              "with that joint's actual 6-axis load every 10 ms of the simulation (all components at the same instant). "
              "Stress = 99.9th percentile of each element's worst von Mises, away from the bolted faces.", "",
              "| Bracket | Elements | Walking MPa (fatigue SF) | Worst with pushes MPa (strength SF) |", "|---|---|---|---|"]
        for k, r in fea["parts"].items():
            L.append(f"| {k.replace('_', ' ')} | {r['elements']:,} | {r['walking_mpa_p99_9']} ({r['fatigue_safety']}) | "
                     f"{r['worst_mpa_p99_9']} ({r['static_safety']}) |")
        L += ["", "Stress maps: `images/fea_*.png`."]

    L += ["", "## What the verification found and fixed", "",
          "### v0.4 (double-sided legs, 2026-10-05)", "",
          "- **Single-sided joints would break** (the builder's own call, confirmed): with v0.4's loads, a v0.3-style joint's "
          "printed plate sees 32–64 MPa every step, above PETG's fatigue strength at every leg joint, and the servo's "
          "output shaft carries up to 3.3 N·m of bending. Every leg pitch and roll joint is now a U-bracket on the servo's "
          "horn and rear hub, the servo body screwed into a cage, like the reference robot.",
          "- **The first U-brackets had weak joints between the arms and the next servo's cage** (voxel FEA): the shin's arms "
          "met the ankle cage through two 18 × 3 mm tabs, the ankle bracket through 2.5 mm bands, the hip-yaw disc through a "
          "thin plate. Solid plates now join each arm to its cage over the whole overlap; cage rear plates went from 2.4 to "
          "4 mm (screw heads counterbored), arms from 3.5 to 4.5 mm; the hip-yaw bracket got a 7 mm disc, a keel and a solid "
          "block; the hip-roll bracket a 10 × 16 mm bridge.",
          "- **Assembly**: plates that cover a cage would have locked the servo out. The knee cage is open at the front and "
          "the ankle cage at the bottom (the servos slide in there), with screwdriver holes through the arms for the far "
          "case screws.",
          "- **Shorter legs swayed 26° sideways and pushed the ankle-roll servo against its stop** (100 % of stall): the "
          "gaits now keep the zero-moment point 20 mm inside each foot (planner option `zmp_offset_y`, chosen by Monte Carlo "
          "over 0–20 mm and 0.45–0.6 s steps): 15° at most, 50 % peak load.",
          "- **Knee speed**: with 62/58 mm leg links the knee swings faster; 0.5 s steps reach the servo's no-load speed. The "
          "gaits keep 0.6 s steps (sizing: 56 % of the torque-speed line at 0.55 s).",
          "- **Collision ranges re-measured** for every joint; limits set inside them (left leg: hip roll −20…22°, hip pitch "
          "−70…8°, knee 0…84°, ankle roll ±20°; every range the gaits use is inside).",
          "", "### v0.3 (2026-10-04)", "",
          "- Shoulder servos inside the chest cap; a hip gusset into the hip-pitch servo; the foot grazing the ankle-pitch "
          "servo; ankle brackets touching in side-steps; limits allowing collisions — all fixed then. Walking robustness: "
          "100 Hz control, a lower stance, 2- and 4-step blocks. An over-claimed push result (one lucky timing) and a wrong "
          "battery estimate were corrected."]
    L += ["", "## Honest limits", ""]
    if fin:
        pu = fin["pushes_mid_walk"]
        L.append("- **Pushes**: " + ", ".join(f"{k} stays up {100 * v['stayed_up_rate']:.0f} %" for k, v in pu.items() if "stayed_up_rate" in v)
                 + " of 48 timed pushes mid-walk. Harder shoves need a step to a new place; the gait player does not re-plan "
                 "its steps (a capture-point stepper is in `jx0bot/stepper.py`, not yet enabled).")
    L += ["- **The hip-yaw joint is still single-sided**: there is no room for a second support between the yaw servo and the "
          "hip-roll servo. A thrust ring under the pelvis carries the leg's axial load and part of the bending; the yaw "
          "servo's two output bearings carry the rest (see the table above). Check the yaw horns for play after the first "
          "hours of walking; a printed slewing ring is the upgrade path.",
          "- **Material and servo data are assumed**: PETG strengths (50 / 15 MPa), the STS3215's rear hub screw pattern "
          "(assumed equal to the horn's), and the servo stiffness (60 N·m/rad, 0.6–1.4x tested). Print a test U-bracket and "
          "fit-check a servo before printing the rest; measure the servo stiffness (bringup.md step 5).",
          "- **Speed**: about 5 cm/s. The short legs make the knee the speed limit of the STS3215 at 12 V.",
          "- **Latency**: the robot needs its control loop to react within about 20 ms (estimate on the Pi: about 8 ms). At "
          "40 ms, long walks often fail; 2- and 4-step blocks mostly survive.",
          "- **Not tested here**: falls (the model has no body collisions, so a fall's impact on the brackets is not "
          "simulated), carpet or very slippery floors (friction below 0.5), stairs, the I2S audio overlay on the Pi, screw "
          "fit in the printed holes, long-term servo heating."]
    L += ["", "## Re-run", "", "```bash", "python jx0/verify/run_all.py", "```", "",
          "Detailed results in this folder: `walking.json`, `verify_cad.json`, `verify_robustness.json`, `verify_strength.json`, "
          "`verify_fea.json`, `verify_power.json`, `sizing.json`."]
    (RES / "verification.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("wrote", (RES / "verification.md").relative_to(ROOT))


if __name__ == "__main__":
    main()
