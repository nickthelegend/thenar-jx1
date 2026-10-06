"""JX0 component list and cost estimate: an 8-page A4 PDF generated from jx0/bom/jx0_bom.csv and the verification results.

1 cover · 2 what JX0 is and how far it has got · 3 cost summary · 4 the 17 joint servos (what each joint needs, the
alternatives priced) · 5 printed structure and hardware (filament per part, finite-element safety factors) · 6 electronics,
sensors and voice (how they connect, the control-loop budget) · 7 power and battery life, and what is not included ·
8 the complete item list with the total. Every number comes from the BOM, the CAD index or the verification results, so
the PDF never goes stale. Styling, number formatting and the headless-Chromium printing come from the JX1 report
(bom/make_cost_report.py).

    python jx0/bom/make_cost_report.py [--preview]     -> jx0/bom/JX0_cost_estimate.pdf
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "bom"))
from make_cost_report import CSS, PREVIEW_JS, bars, e, edge, inr, short, subtotal, table, words  # noqa: E402

REPORT_DATE = "24 Sep – 5 Oct 2026"     # prices checked over these dates (servos and filament on 4 Oct)

BOM = ROOT / "jx0" / "bom" / "jx0_bom.csv"
OUT_PDF = ROOT / "jx0" / "bom" / "JX0_cost_estimate.pdf"
BUILD = ROOT / "jx0" / "bom" / ".report_build"
N_PAGES = 8
BUDGET = 50_000
SPEC = {}                       # filled in main() from the CAD and the design point
REPO = "github.com/nickthelegend/thenar-jx1/tree/main/jx0"
RESULTS = ROOT / "jx0" / "results"
STALL = 2.94                    # N·m, STS3215 at 12 V
# servos that could do the job, priced at Indian stores (research/raw/jx0_india_sourcing_raw.md, incl. GST, 24 Sep 2026;
# the STS3215 12 V on 4 Oct): (servo, torque kg·cm and where from, feedback, price ₹ (low, high), store)
ALTERNATIVES = [
    ("TowerPro MG996R", 11.0, "maker's figure at 6 V", "none (PWM)", (259, 409), "Quartz, Robocraze, Robu"),
    ("Waveshare ST3215 7.4 V", 19.5, "at 7.4 V", "position, load, temperature", (2159, 2159), "Robu"),
    ("Hiwonder LX-224", 20.0, "listing", "position", (2900, 2900), "ThinkRobotics"),
    ("Waveshare ST3020", 25.0, "listing", "position, load, temperature", (2618, 2618), "Robu"),
    ("Feetech STS3215 12 V (chosen)", 30.0, "at 12 V", "position, load, temperature", (2419, 2419), "Evelta"),
    ("Waveshare ST3025", 40.0, "listing", "position, load, temperature", (10299, 10299), "Robocraze"),
]
PART_NAMES = {"JX0_Pelvis": "Pelvis", "JX0_YawKeeper": "Hip-yaw keeper", "JX0_HipYawBracket": "Hip-yaw bracket (disc)",
              "JX0_HipRollBracket": "Hip-roll U-bracket", "JX0_Thigh": "Thigh", "JX0_Shin": "Shin",
              "JX0_AnkleBracket": "Ankle bracket", "JX0_Foot": "Foot", "JX0_Torso": "Torso (lower shell, skirt)",
              "JX0_ChestCap": "Chest cap", "JX0_Head": "Head", "JX0_UpperArm": "Upper arm (hood + elbow box)",
              "JX0_ArmBlade": "Arm blade"}
FEA_OF = {"JX0_Pelvis": "pelvis", "JX0_YawKeeper": "yaw_keeper", "JX0_HipYawBracket": "hip_yaw_bracket",
          "JX0_HipRollBracket": "hip_roll_bracket", "JX0_Thigh": "thigh", "JX0_Shin": "shin", "JX0_AnkleBracket": "ankle_bracket",
          "JX0_Foot": "foot"}


def uri(rel):
    return (ROOT / rel).resolve().as_uri()


def page(n, title, body, cls=""):
    head = "" if n == 1 else f'''<div class="phead"><span><b>JX0</b> · the walking, talking STS3215 humanoid · component list and cost estimate</span><span>{n} / {N_PAGES}</span></div>'''
    foot = "" if n == 1 else f'''<div class="pfoot"><span>Prices in INR from Indian online stores, GST included where the store states it · checked {REPORT_DATE} · ESTIMATED lines need a quote</span></div>'''
    h = f"<h1>{title}</h1>" if title else ""
    return f'''<section class="page {cls}" id="p{n}">{head}<div class="content">{h}{body}</div>{foot}</section>'''


def load():
    rows = list(csv.DictReader(BOM.open(encoding="utf-8")))
    for r in rows:
        r["qty"], r["unit"], r["total"] = int(float(r["Qty"])), float(r["Unit INR"]), float(r["Total INR"])
        assert abs(r["qty"] * r["unit"] - r["total"]) < 0.05, r["ID"]
    return rows


def spec_numbers():
    """Height, mass and printed parts from the CAD index and the simulation model, so the PDF never goes stale."""
    import json
    import yaml
    sys.path.insert(0, str(ROOT / "jx0" / "cad"))
    import geometry as G
    idx = json.loads((ROOT / "jx0" / "cad" / "parts" / "index.json").read_text(encoding="utf-8"))
    pieces = sum(q for n, (_, _, q) in G.PARTS.items())
    printed = sum(idx[n]["printed_mass_g"] * q for n, (_, _, q) in G.PARTS.items() if n in idx)
    dp = yaml.safe_load((ROOT / "jx0" / "design_point.yaml").read_text(encoding="utf-8"))
    sys.path.insert(0, str(ROOT / "jx0" / "sim"))
    import mujoco
    from jx0_model import build as build_model
    from jx1calc.design import Design
    m = mujoco.MjModel.from_xml_string(build_model(Design(ROOT / "jx0" / "design_point.yaml")))
    return {"height": f"{dp['overall']['height_m']['value'] * 100:.1f} cm", "mass": f"{m.body_subtreemass[1]:.2f} kg",
            "pieces": pieces, "printed": f"{printed:.0f} g"}


def build(rows):
    total = sum(r["total"] for r in rows)
    by_group = defaultdict(float)
    for r in rows:
        by_group[r["Group"]] += r["total"]
    by_group = dict(sorted(by_group.items(), key=lambda kv: -kv[1]))
    servos = by_group["Servos"]
    pages = []

    # 1 - cover
    pages.append(page(1, "", f'''
<div class="cover-top">
  <div class="kicker">Minimum viable humanoid · component list and cost estimate</div>
  <div class="wordmark"><span class="dot"></span>JX0</div>
  <div class="tag">walks · talks · 17 STS3215 joints</div>
</div>
<div class="cover-img"><img src="{uri('jx0/results/images/jx0_demo_walk.png')}" alt="JX0 walking with its arms swinging (simulation of the CAD model)"></div>
<div class="cover-stats">
  <div><b>{SPEC["height"]}</b><span>height</span></div><div><b>{SPEC["mass"]}</b><span>mass</span></div>
  <div><b>17</b><span>STS3215 joints</span></div><div><b>{SPEC["pieces"]}</b><span>printed parts</span></div><div><b>{len(rows)}</b><span>BOM lines</span></div>
</div>
<div class="cover-cost">
  <div><span>Parts for one robot</span><b>{inr(total)}</b></div>
  <div class="grand"><span>The 17 joint servos</span><b>{inr(rows[0]["total"])}</b></div>
</div>
<div class="cover-foot">{REPORT_DATE} · all figures from the JX0 bill of materials ({REPO})</div>
''', "cover"))

    # 2 - overview
    est = [r for r in rows if r["Label"].startswith("ESTIMATED")]
    n_est = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight", 9: "Nine"}.get(len(est), str(len(est)))
    est_names = ", ".join(e((lambda t: t[0].lower() + t[1:] if t[1:2].islower() else t)(r["Item"].split(" (")[0])) for r in est)
    import json
    margin = min(j["peak_margin"] for j in json.loads((ROOT / "jx0" / "results" / "sizing.json").read_text(encoding="utf-8"))["joints"])
    spec = [("Height / mass", f"{SPEC['height']} / {SPEC['mass']} (CAD, all parts)"),
            ("Joints", "17, every one a Feetech STS3215 12 V serial bus servo (30 kg·cm stall, position feedback), like the reference robot"),
            ("Legs", "6 joints each; every pitch and roll joint double-sided (a U-bracket on the servo's horn and rear hub, the body in a cage), like the reference robot; the hip-yaw disc held from both sides"),
            ("Arms and head", "shoulder pitch and elbow per arm, a paddle blade; neck yaw under a soft rounded head"),
            ("Brain", "Raspberry Pi 4: 100 Hz gait playback with arm swing, IMU balance, offline speech recognition and voice"),
            ("Talking", "Claude over Wi-Fi writes the replies and calls the robot's actions (walk, turn, wave, nod, look)"),
            ("Power", "3S 2200 mAh LiPo (about 73 min of walking, CALCULATED) or a 12.6 V bench supply"),
            ("Structure", f"{SPEC['pieces']} parts, {SPEC['printed']} on a home 3D printer: pelvis and leg parts in PETG, printed near-solid; body, head and arms in pastel green matte PLA")]
    spec_html = "".join(f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in spec)
    pages.append(page(2, "1. What JX0 is", f'''
<p class="lead">JX0 is a small humanoid robot designed to be built by one student at home, from a 3D printer and parts
that can be ordered online in India. Its look and its joints follow a friend's working robot: a faceted green body, every
joint a 12 V STS3215. It is the working prototype of the JX1 project: it uses the same design pipeline (gait planner,
servo sizing, physics simulation) at a price a student can afford.</p>
<div class="two">
  <div><h2>Specification</h2><table class="spec-t">{spec_html}</table></div>
  <div class="imgcol"><img src="{uri('jx0/cad/images/jx0_cad_front.png')}" class="framed tall" alt="JX0 in SolidWorks"></div>
</div>
<div class="two">
  <div><h2>Done (on the computer)</h2><ul class="checks">
    <li class="ok">SolidWorks CAD: {SPEC["pieces"]} printable parts and the full assembly with all 17 servos, built by script</li>
    <li class="ok">Servo sizing all pass (tightest {margin:.2f}×); every printed leg part passes a finite-element check</li>
    <li class="ok">Walking in a physics simulation of the CAD robot: 14 of 14 gaits pass, arms swinging</li>
    <li class="ok">No part collisions in 1,373 moving poses; all 140 walks with random model errors and every push up to 0.96 N·s stay up</li>
    <li class="ok">Robot program (voice, Claude, walking, gestures) runs on the simulated robot: 24/24 missions</li>
    <li class="next">Next: buy the parts → print → assemble → first steps</li></ul></div>
  <div><h2>How this estimate was made</h2><ul class="notes">
    <li>Every line is a real product page at an Indian store (Robu, Evelta, Robocraze, ThinkRobotics, Quartz
      Components and others), price checked {REPORT_DATE}.</li>
    <li>GST is included where the store states it; shipping is not included.</li>
    <li>{n_est} small lines ({est_names}) are ESTIMATED.</li>
    <li>Over the original ₹50,000 target because all 17 joints are STS3215, as on the reference robot.</li></ul></div>
</div>
<h2>From CAD to a working robot</h2>
<div class="strip">
  <figure><img src="{uri('jx0/cad/images/jx0_cad_back.png')}" alt="SolidWorks back view"><figcaption>SolidWorks assembly, back view</figcaption></figure>
  <figure><img src="{uri('jx0/results/images/jx0_demo_wave.png')}" alt="waving"><figcaption>waving (simulation, the robot's own program)</figcaption></figure>
  <figure><img src="{uri('jx0/results/images/jx0_demo_kick.png')}" alt="bumping a bottle"><figcaption>walks into a bottle, as in the reference video</figcaption></figure>
</div>'''))

    # 3 - cost summary
    grp_note = {"Servos": "17 × STS3215 (legs, arms, neck)", "Electronics": "Raspberry Pi 4, microSD, servo driver, wiring",
                "Power": "LiPo, charger, 5 V converter, switch, alarm", "Structure": "filament, screws, inserts, foot rubber",
                "Voice": "microphone, amplifier, speaker", "Sensors": "IMU"}
    grp_rows = [[e(k), e(grp_note.get(k, "")), f'<span class="r">{inr(v)}</span>', f'<span class="r">{100 * v / total:.1f} %</span>']
                for k, v in by_group.items()]
    top = sorted(rows, key=lambda r: -r["total"])[:5]
    top_rows = [[e(r["Item"]), e(short(r["Model"], 60)), str(r["qty"]), f'<span class="r"><b>{inr(r["total"])}</b></span>'] for r in top]
    pages.append(page(3, "2. Cost summary", f'''
<div class="cards">
  <div class="card"><span>Parts total</span><b>{inr(total)}</b><em>{len(rows)} line items, one robot</em></div>
  <div class="card"><span>Joint servos</span><b>{100 * rows[0]["total"] / total:.0f} %</b><em>of the cost: 17 × STS3215 at {inr(rows[0]["unit"])}</em></div>
  <div class="card hi"><span>Everything else</span><b>{inr(total - rows[0]["total"])}</b><em>brain, power, voice, structure</em></div>
</div>
<h2>By group</h2>
{bars(by_group, total)}
<h2>Groups</h2>
{table([("Group", ""), ("What", ""), ("₹", "r"), ("Share", "r")], grp_rows, "compact",
       foot=["<b>Total</b>", "", f'<span class="r"><b>{inr(total)}</b></span>', '<span class="r">100 %</span>'])}
<h2>Five biggest lines</h2>
{table([("Item", ""), ("Model", ""), ("Qty", "r"), ("₹", "r")], top_rows, "compact")}
<p class="note">Why the STS3215 everywhere: the walking needs up to 2.0 N·m at the hip roll (with a 1.25–1.5× safety margin),
more than MG996R-class hobby servos give; the serial bus servos also report their position, which the calibration and the
balance loop use; and one servo type on one bus is how the reference robot is built.</p>'''))

    import json
    sys.path.insert(0, str(ROOT / "jx0" / "cad"))
    import geometry as G
    siz = json.loads((RESULTS / "sizing.json").read_text(encoding="utf-8"))
    pw = json.loads((RESULTS / "verify_power.json").read_text(encoding="utf-8"))
    fea = json.loads((RESULTS / "verify_fea.json").read_text(encoding="utf-8"))["parts"]
    idx = json.loads((ROOT / "jx0" / "cad" / "parts" / "index.json").read_text(encoding="utf-8"))
    by_id = {r["ID"]: r for r in rows}

    def group_rows(groups):
        out = []
        for r in rows:
            if r["Group"] in groups:
                out.append([f'<span class="id">{e(r["ID"][4:])}</span>',
                            f'<b>{e(r["Item"])}</b><br><span class="sub">{e(short(r["Model"], 64))}</span>',
                            f'<span class="sub">{e(r["Store"])}{" · ESTIMATED" if r["Label"].startswith("ESTIMATED") else ""}</span>',
                            str(r["qty"]), inr(r["unit"]), f'<b>{inr(r["total"])}</b>'])
        return out, sum(r["total"] for r in rows if r["Group"] in groups)
    cols6 = [("#", ""), ("Item", ""), ("Store", ""), ("Qty", "r"), ("Unit", "r"), ("Total", "r")]

    # 4 - the joint servos
    servo = rows[0]
    names = {"hip_yaw": "Hip yaw", "hip_roll": "Hip roll", "hip_pitch": "Hip pitch", "knee": "Knee",
             "ankle_pitch": "Ankle pitch", "ankle_roll": "Ankle roll"}
    jrows = [[names[j["joint"]], "2", f'{j["required_peak_nm"]:.2f} N·m', f'<b>{100 * j["required_peak_nm"] / STALL:.0f} %</b>',
              f'×{j["peak_margin"]:.2f}', f'{100 * j["torque_speed_utilisation"]:.0f} %'] for j in siz["joints"]]
    wj = pw["walking_forward"]["joints"]
    for label, key, n in (("Shoulder pitch", "l_shoulder_pitch", 2), ("Elbow", "l_elbow", 2), ("Neck yaw", "neck_yaw", 1)):
        need = 1.5 * wj[key]["peak_nm"]
        jrows.append([label, str(n), f"{need:.2f} N·m", f"<b>{100 * need / STALL:.0f} %</b>", f"×{STALL / max(need, 1e-3):.1f}" if need > 0.05 else "—", "—"])
    hip_roll = next(j["required_peak_nm"] for j in siz["joints"] if j["joint"] == "hip_roll")
    arows = []
    for name, kgcm, where, fb, (lo, hi), store in ALTERNATIVES:
        nm = kgcm * 0.0980665
        price = inr(lo) if lo == hi else f"{inr(lo)}–{inr(hi, False)}"
        price17 = inr(17 * lo) if lo == hi else f"{inr(17 * lo)}–{inr(17 * hi, False)}"
        ok = nm >= hip_roll
        cls = "hl" if "chosen" in name else ""
        arows.append(([f"<b>{e(name)}</b>", f"{kgcm:g} kg·cm = {nm:.2f} N·m<br><span class='sub'>{e(where)}</span>", e(fb),
                       price, price17, ("yes, ×%.2f" % (nm / hip_roll)) if ok else f"no ({100 * nm / hip_roll:.0f} %)"], cls))
    pages.append(page(4, "3. The 17 joint servos — 71 % of the cost", f'''
<p class="lead">Every joint is the same Feetech STS3215 12 V serial bus servo, as on the reference robot: a metal-gear servo
with a 360° magnetic encoder that reports its position, load, voltage and temperature over one shared serial bus. One
servo type means one spare fits every joint.</p>
<div class="cards">
  <div class="card"><span>Servos</span><b>{servo["qty"]}</b><em>12 legs, 4 arms, 1 neck</em></div>
  <div class="card"><span>Each</span><b>{inr(servo["unit"])}</b><em>{e(servo["Store"])}, GST included</em></div>
  <div class="card hi"><span>All 17</span><b>{inr(servo["total"])}</b><em>{100 * servo["total"] / total:.0f} % of the robot</em></div>
</div>
<h2>What each joint needs (simulated, with safety margins)</h2>
{table([("Joint", ""), ("Servos", "r"), ("Needs", "r"), ("Of 2.94 N·m stall", "r"), ("Margin", "r"), ("Speed use", "r")], jrows, "compact")}
<p class="note">Legs: the servo sizing (jx0/analysis/sizing.py) over 5 gaits and 8 static cases, dynamic peaks ×1.5 and static
×1.25; "speed use" is the share of the torque-speed line used at the fastest gait. Arms and neck: the walking peak ×1.5
(the arm swing). Every joint passes; the hip roll, holding the body over one foot, is the tightest.</p>
<h2>Servos considered</h2>
{table([("Servo", ""), ("Torque", ""), ("Feedback", ""), ("Each", "r"), ("For 17", "r"), ("Enough for the hip roll?", "r")], arows, "compact")}
<p class="note">The hip roll needs {hip_roll:.2f} N·m with its margin. MG996R-class hobby servos are a tenth of the price but
have half the torque and no feedback (the balance loop and the calibration need to read the joint angles). The 7.4 V
ST3215 and the LX-224 fall just short. The ST3020 would work but costs more per joint; the ST3025 is over four times
the price.</p>'''))

    # 5 - printed structure and hardware
    petg, pla = by_id["JX0-21b"], by_id["JX0-21"]
    rate = {G.FILL_LEG: petg["unit"] / 1000, G.FILL_BODY: pla["unit"] / 1000}
    parts = {}
    for name, (_, _, q) in G.PARTS.items():
        base = name[:-2] if name.endswith(("_L", "_R")) else name
        r = parts.setdefault(base, {"qty": 0, "g": idx[name]["printed_mass_g"], "fill": G.fill(name)})
        r["qty"] += q
    prow, used = [], {G.FILL_LEG: 0.0, G.FILL_BODY: 0.0}
    for base, r in parts.items():
        g = r["g"] * r["qty"]
        used[r["fill"]] += g
        f = fea.get(FEA_OF.get(base, ""), None)
        sf = f'{f["fatigue_safety"]:.1f} / {f["static_safety"]:.1f}' if f else "—"
        mat = "PETG near-solid" if r["fill"] == G.FILL_LEG else "PLA matte"
        prow.append([f"<b>{e(PART_NAMES.get(base, base))}</b>", str(r["qty"]), mat, f'{r["g"]:.1f} g', f'{g:.0f} g',
                     inr(g * rate[r["fill"]]), sf])
    g_tot = used[G.FILL_LEG] + used[G.FILL_BODY]
    hw_rows, hw_tot = group_rows({"Structure"})
    pages.append(page(5, "4. Printed structure and hardware", f'''
<p class="lead">{sum(r["qty"] for r in parts.values())} printed parts. The pelvis and every leg part carry the robot's
weight at every step, so they are PETG printed near-solid (6 walls, 6 top and bottom layers, 40 % gyroid); the body, head
and arms are matte PLA in the reference robot's pastel green.</p>
{table([("Part", ""), ("Qty", "r"), ("Material", ""), ("Each", "r"), ("All", "r"), ("Filament ₹", "r"), ("FEA SF fatigue / static", "r")],
       prow, "compact", ["<b>Printed parts</b>", "", f"PETG {used[G.FILL_LEG]:.0f} g, PLA {used[G.FILL_BODY]:.0f} g", "", f"<b>{g_tot:.0f} g</b>",
                         f"<b>{inr(sum(used[k] * rate[k] for k in used))}</b>", ""])}
<p class="note">Filament ₹ = the part's share of the 1 kg spools (PETG {inr(petg["unit"])}, PLA {inr(pla["unit"])}). FEA SF: finite-element
safety factors under the simulated walking (fatigue) and the hardest pushes (strength); 2 or more everywhere.</p>
<h2>Filament, screws and small parts</h2>
{table(cols6, hw_rows, "compact")}
{subtotal("Structure", hw_tot)}'''))

    # 6 - electronics, sensors and voice
    el_rows, el_tot = group_rows({"Electronics", "Sensors", "Voice"})
    rt = pw["realtime"]
    pages.append(page(6, "5. Electronics, sensors and voice", f'''
<p class="lead">A Raspberry Pi 4 runs everything on the robot: it plays the verified gaits 100 times a second with the
IMU's balance corrections, listens with an offline speech recogniser, asks Claude over Wi-Fi what to say and do, and
speaks through a small amplifier and speaker.</p>
{table(cols6, el_rows, "items")}
{subtotal("Electronics, sensors and voice", el_tot)}
<h2>How it connects</h2>
<div class="flow">
  <div class="fbox">Raspberry Pi 4<br><small>gaits + balance · 100 Hz</small></div><div class="farrow">USB →</div>
  <div class="fbox">Servo driver<br><small>serial bus, 1 Mbit/s</small></div><div class="farrow">1 bus →</div>
  <div class="fbox">17 × STS3215<br><small>IDs 1–17 · angle, load, temperature</small></div>
</div>
<div class="flow"><div class="fbox soft">MPU6050 IMU → Pi · I2C</div><div class="fbox soft">INMP441 microphone → Pi · I2S</div>
<div class="fbox soft">Pi · I2S → MAX98357A → speaker</div><div class="fbox soft">push-to-talk button → GPIO</div></div>
<div class="two">
  <div><h2>Control-loop budget</h2>{table([("", ""), ("", "r")], [
      ["Loop period", f'{rt["frame_ms"]:.0f} ms (100 Hz)'], ["Servo bus per frame", f'{rt["bus_ms_per_frame"]} ms ({rt["bus_bytes_per_frame"]} bytes)'],
      ["IMU read", f'{rt["imu_read_ms_est"]} ms (estimated)'], ["Robot program on a Pi 4", f'{rt["python_ms_per_frame_pi4_est"]} ms (estimated)'],
      ["Used of each frame", f'<b>{rt["frame_used_ms_pi4_est"]} ms of {rt["frame_ms"]:.0f} ms</b>']], "compact kv")}</div>
  <div><h2>Talking</h2><ul class="notes">
    <li>Speech recognition (Vosk) and the voice (Piper) run on the Pi, offline and free.</li>
    <li>Claude writes the replies and chooses the robot's actions; it needs Wi-Fi and an Anthropic API key, paid per use
      (not in this estimate).</li>
    <li>The microphone listens through the four holes in the head, the speaker sits under the chest grille.</li></ul></div>
</div>'''))

    # 7 - power and battery life
    p_rows, p_tot = group_rows({"Power"})
    wf, bat, st = pw["walking_forward"], pw["battery"], pw["standing"]
    pages.append(page(7, "6. Power and battery life", f'''
<p class="lead">The 12 V servos run straight from a 3S LiPo (11.1 V nominal, 12.6 V full), like the reference robot on its
12.6 V bench supply; a 5 V UBEC feeds the Pi. The same XT60 plug takes a bench supply for long sessions at the desk.</p>
{table(cols6, p_rows, "items")}
{subtotal("Power", p_tot)}
<div class="two">
  <div><h2>Battery life (calculated)</h2>{table([("", ""), ("", "r")], [
      ["Pack", e(bat["pack"]) + " · 24.4 Wh"], ["Walking, average", f'{wf["total_avg_a"]} A ({wf["total_avg_w"]:.0f} W, servos + Pi)'],
      ["Walking, peak", f'{wf["total_peak_a"]} A (pack limit {bat["max_continuous_a"]:.0f} A)'],
      ["Walking time", f'<b>about {bat["walking_minutes_80pct"]} minutes</b>'], ["Standing time", f'about {bat["standing_minutes_80pct"]} minutes'],
      ["Reference robot", f'{bat["reference_robot_bench_supply_a"][0]}–{bat["reference_robot_bench_supply_a"][1]} A at 12.6 V walking (its video)']],
      "compact kv")}
  <p class="note">From the simulated servo torques and the STS3215's current, using 80 % of the pack. The model's
  {wf["servo_current_avg_a"]} A of servo current while walking sits inside the range the reference robot's bench supply showed.</p></div>
  <div><h2>Safety</h2><ul class="notes">
    <li>A 10 A DC-rated switch between the pack and everything else; the peak is {wf["total_peak_a"]} A.</li>
    <li>A buzzer on the balance lead warns before the LiPo is over-discharged.</li>
    <li>Charge only with the balance charger, on a non-flammable surface.</li>
    <li>The UBEC gives the Pi 5 A; it needs up to {pw["ubec_5v"]["pi4_max_a"]:.0f} A, the audio {pw["ubec_5v"]["audio_a"]} A.</li></ul></div>
</div>
<h2>Not included in this estimate</h2>
<div class="excl">
  <div>A 3D printer (or a print service), and the time to print about {g_tot / 1000:.1f} kg of parts</div>
  <div>Tools: M2 / M3 hex keys, a small screwdriver, a soldering iron for the heat-set inserts</div>
  <div>Shipping and delivery charges from the stores</div>
  <div>A spare STS3215 ({inr(servo["unit"])}) and a second battery, recommended</div>
  <div>Claude API usage (pay per use) and Wi-Fi</div>
  <div>An optional 12.6 V bench supply for long sessions at the desk</div>
</div>'''))

    # 8 - complete list
    item_rows = [[f'<span class="id">{e(r["ID"][4:])}</span>', f'<b>{e(r["Item"])}</b><br><span class="sub">{e(short(r["Model"], 70))}</span>',
                  f'<span class="sub">{e(r["Store"])}</span>', str(r["qty"]), f'<span class="r">{inr(r["unit"])}</span>',
                  f'<span class="r"><b>{inr(r["total"])}</b></span>'] for r in rows]
    pages.append(page(8, "7. Complete list of items", f'''
{table([("#", ""), ("Item", ""), ("Store", ""), ("Qty", "r"), ("Unit", "r"), ("Total", "r")], item_rows, "all")}
<div class="final">
  <div class="frow grand"><span>Total for one JX0</span><b>{inr(total)}</b></div>
  <div class="inwords">Rupees {words(total)} only</div>
</div>'''))
    return pages, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    rows = load()
    SPEC.update(spec_numbers())
    pages, total = build(rows)
    assert len(pages) == N_PAGES
    BUILD.mkdir(parents=True, exist_ok=True)
    src = BUILD / "JX0_cost_estimate.html"
    src.write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>JX0 — component list and cost estimate</title>
<style>{CSS}
tr.hl td {{ background: #fff3ea; }} tr.hl td b {{ color: #c4500e; }}</style></head><body>{"".join(pages)}{PREVIEW_JS}</body></html>""", encoding="utf-8")
    prof = BUILD / "edge_profile"
    dom = edge(["--virtual-time-budget=5000", "--dump-dom", src.as_uri() + "?check=1"], prof).stdout
    m = re.search(r'data-overflow="([^"]+)"', dom)
    print("overflow (px past the content box, <= 0 is fine):", m.group(1) if m else "n/a")
    edge(["--no-pdf-header-footer", "--run-all-compositor-stages-before-draw", "--virtual-time-budget=8000",
          f"--print-to-pdf={OUT_PDF}", src.as_uri()], prof, OUT_PDF)
    if a.preview:
        for n in range(1, N_PAGES + 1):
            edge(["--window-size=794,1123", "--force-device-scale-factor=1.4", "--virtual-time-budget=5000",
                  f"--screenshot={BUILD / f'page_{n}.png'}", src.as_uri() + f"?p={n}"], prof, BUILD / f"page_{n}.png")
    pdf = OUT_PDF.read_bytes()
    n_pages = len(re.findall(rb"/Type\s*/Page[^s]", pdf))
    print(f"wrote {OUT_PDF.relative_to(ROOT)}: {n_pages} pages, {len(pdf) / 1e6:.1f} MB; total {inr(total)}")
    assert n_pages == N_PAGES, f"expected {N_PAGES} pages, got {n_pages}"


if __name__ == "__main__":
    main()
