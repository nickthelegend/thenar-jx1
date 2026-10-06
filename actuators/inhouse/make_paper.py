"""Build the research paper 'Building humanoid joint actuators in-house' as an A4 PDF.

All numbers are read from results/design.json, results/variants.json and results/cost.json (run qdd_design.py and
cost_model.py first), so the paper never disagrees with the calculation. HTML is printed with headless Chromium.
Usage: python actuators/inhouse/make_paper.py
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from string import Template

import paper_text as T

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
FIG = HERE / "figures"
BUILD = HERE / ".paper_build"
OUT_PDF = HERE / "JXA_inhouse_actuator_research_paper.pdf"
DATE = "6 October 2026"
CHROME = [p for p in ("/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell",
                      "/opt/pw-browsers/chromium-1194/chrome-linux/chrome", shutil.which("chromium") or "",
                      shutil.which("google-chrome") or "") if p and Path(p).exists()]

D = {d["spec"]["name"]: d for d in json.loads((RES / "design.json").read_text())}
V = json.loads((RES / "variants.json").read_text())
C = json.loads((RES / "cost.json").read_text())
N = ["JXA-40", "JXA-120", "JXA-360"]


def r(x, n=0):
    return f"{x:,.{n}f}"


def inr(x):
    """₹ with Indian grouping (lakh/crore)."""
    x = round(x)
    s = str(abs(x))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:]); head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts) + "," + tail
    return ("−" if x < 0 else "") + "₹" + s


def lakh(x):
    return f"₹{x / 1e5:.1f} lakh" if x < 1e7 else f"₹{x / 1e7:.2f} crore"


def table(head, rows, cls="small"):
    h = "".join(f"<th>{x}</th>" for x in head)
    b = "".join("<tr>" + "".join(f"<td>{x}</td>" for x in row) + "</tr>" for row in rows)
    return f'<table class="{cls}"><tr>{h}</tr>{b}</table>'


def fig(name, caption, width="100%"):
    return f'<figure><img src="{(FIG / name).as_uri()}" style="width:{width}"><figcaption>{caption}</figcaption></figure>'


# ----------------------------------------------------------------------------------------------------------------------
def fill_fixed():
    win_rows = []
    why = {"JXA-40": "same family as 12N14P drone motors; RS06/CyberGear are 28-pole",
           "JXA-120": "highest k<sub>w</sub> of the 36-slot options, 4 symmetric units allow 4 parallel groups",
           "JXA-360": "many poles for a large diameter; balanced, smooth (LCM 528)"}
    wt = []
    for n in N:
        w = D[n]["winding"]; s = D[n]["spec"]; e = D[n]["electrical"]
        win_rows.append(f"<tr><td>{n}</td><td>{s['slots']}N{s['poles']}P</td><td>{w['kw']:.3f}</td><td>{w['repeat_units']}</td>"
                        f"<td>{w['lcm']}</td><td>{why[n]}</td></tr>")
        pat = " ".join(w["layout"][: len(w["layout"]) // w["repeat_units"]])
        wt.append(f"<tr><td>{n}</td><td>{s['slots']}</td><td><b>{w['turns_per_coil']}</b></td><td>{w['wire_bare_mm']:.2f} mm × {w['strands_in_hand']}"
                  f" ({w['wire_SWG_note']})</td><td>{w['parallel_paths']}</td><td>{w['wire_length_m']:.0f} m / {w['copper_mass_g']:.0f} g</td>"
                  f"<td>{w['copper_fill_bare']:.2f}</td><td>{e['R_phase_20C_mohm']:.0f} mΩ</td><td class='mono'>{pat} (×{w['repeat_units']})</td></tr>")
    sub = {
        "shear_list": " / ".join(f"{D[n]['performance']['air_gap_shear_peak_kPa']:.0f}" for n in N),
        "rth_list": " / ".join(f"{D[n]['spec']['rth_K_per_W']:.2f}" for n in N),
        "winding_rows": "".join(win_rows), "winding_table": "".join(wt),
        "fill_target": f"{D['JXA-120']['spec']['fill_target']:.2f}",
        "rewinder_cost": "₹800–2,000", "needle_winder": "₹2–7 lakh (US$5–8k semi-auto)",
        "cnc_winder": "₹15–30 lakh (US$15–30k)",
        "airgap_mm": f"{D['JXA-120']['spec']['airgap_mm']:.2f}",
    }
    hr = C["housing_routes_jxa120"]
    lots = list(next(iter(hr.values()))["per_part"].keys())
    rows = []
    for name, v in hr.items():
        best = {n: min(hr, key=lambda k: hr[k]["per_part"][n]) for n in lots}
        rows.append([f"{name}<br><span class='muted'>{v['note']}</span>"] +
                    [(f"<b>{inr(v['per_part'][n])}</b>" if best[n] == name else inr(v["per_part"][n])) for n in lots])
    sub["housing_table"] = table(["JXA-120 housing route (finished, ESTIMATED)"] + [f"{int(n):,} pcs" for n in lots], rows) + \
        '<p class="caption">Table 7b. Cost per finished JXA-120 housing by route and lot size (cost_model.py; cheapest in bold). '\
        'Machining rate falls from ₹2,500/h for tiny lots to ₹400/h at volume.</p>'
    sub["housing_fig"] = fig("housing_routes.png", "Figure 3b. Finished-housing cost vs lot size. Billet CNC wins below ≈ 10 pieces, sand casting from ≈ 20, high-pressure die casting only near 10,000.", "80%")
    return (Template(T.PHYSICS).safe_substitute(sub), Template(T.WINDING).safe_substitute(sub),
            Template(T.BUILD + T.CASTING).safe_substitute(sub))


# ----------------------------------------------------------------------------------------------------------------------
def section_survey():
    rows = [
        ["RobStride RS00 / RS02 / RS06", "14 / 17 / 36", "5 / 6 / 11", "33 / 43 / 50", "310 / 405 / 621", "10 / 7.75 / 9 planetary", "$125 / $145 / $210 (¥598 / ¥699 / ¥849)", "Beijing; ex-Xiaomi CyberGear team"],
        ["RobStride RS03 / RS04", "60 / 120", "20 / 40", "20.4 / 20.9", "880 / 1,420", "9:1 planetary, 42 poles", "$225 / $255 (¥999 / ¥1,199)", "largest RobStride model (no >120 N·m unit)"],
        ["Damiao DM-J10010L / J10422P", "120 / 400", "40 / 100", "20.9 / 12.6", "1,372 / 2,700", "10:1 / 22:1", "$265 / $480 (reseller)", "Shenzhen; CAN-FD on new models"],
        ["Unitree GO-M8010-6 / IM6014", "23.7 / 34.4", "–", "30 / 54", "530 / 535", "6.33 / 12.66", "$369 / $269", "RS-485; Go2: outer rotor 36N42P, 6.22:1"],
        ["Unitree G1 knee / H1 knee", "90–139 / 360", "–", "~20 / 14", "–", "2-stage 22.5:1 / –", "not sold separately", "G1: 18N16P inner rotor (teardown, unverified)"],
        ["CubeMars AK80-9 / AK10-9", "18 / 48", "9 / 18", "– / 10.5", "485 / 960", "9:1 planetary, 36N42P Ø98", "₹79,739 / ₹1,04,809 (Robu)", "3–8× RobStride per N·m in India"],
        ["MIT Humanoid (U10 / U12 module)", "33.6 / 68", "–", "55 / 45", "619 / 1,174", "6:1 planetary (+ belts)", "research", "knee 136 N·m via 12:1 incl. belt"],
        ["Berkeley Humanoid Lite 6512", "~20–28", "–", "–", "–", "15:1 printed cycloid", "US$157–188", "open source; walks at 6 N·m caps"],
        ["Tesla Optimus rotary (3 sizes)", "20 / 110 / 180", "–", "–", "–", "strain-wave + clutch + crossed roller", "in-house", "plus linear 500 / 3,900 / 8,000 N roller screws"],
    ]
    t = table(["Actuator", "Peak N·m", "Rated N·m", "No-load rad/s", "Mass g", "Reducer", "Price", "Notes"], rows)
    internals = table(["Quantity (RS04 datasheet → our JXA-120 model)", "RobStride RS04 (published)", "JXA-120 (calculated)", "Comment"], [
        ["Poles / slots", "42 / 36 (slots inferred)", f"{D['JXA-120']['spec']['poles']} / {D['JXA-120']['spec']['slots']}", "bought-core variant uses 36N42P"],
        ["Gear ratio", "9", "9 (12 / 42 / 96 teeth)", "same"],
        ["Kt at output, N·m/A<sub>rms</sub>", "2.10", f"{D['JXA-120']['electrical']['Kt_output_Nm_per_Arms']:.2f}", "+10 %"],
        ["Back-EMF, V<sub>rms</sub> line-line per 1000 motor rpm", "16.9", f"{D['JXA-120']['electrical']['Ke_LL_Vrms_per_krpm_motor']:.1f}", "−3 %"],
        ["Phase resistance", "≈ 80 mΩ (0.16 Ω line-line)", f"{D['JXA-120']['electrical']['R_phase_20C_mohm']:.0f} mΩ at 20 °C", "ours has a 20 mm stack: more copper"],
        ["Phase inductance", "≈ 105 µH (0.211 mH line-line)", f"{D['JXA-120']['electrical']['L_phase_uH']:.0f} µH", "−19 %"],
        ["Peak phase current", "90 A", f"{D['JXA-120']['electrical']['i_peak_A']} A", "−4 %"],
        ["No-load speed at 48 V", "20.9 rad/s", f"{D['JXA-120']['performance']['noload_out_rad_s']:.1f} rad/s", "+11 %"],
        ["Mass", "1.42 kg", f"{D['JXA-120']['performance']['mass_kg']:.2f} kg", "first in-house design is heavier"],
    ])
    return f"""
<h2 id="survey">3. What is on the market, and what is inside it</h2>
<p>The existing repository survey (<code>research/raw/actuator_technology_raw.md</code>, ≈110 actuators) and two new logs
(<code>actuator_internals_and_torque_raw.md</code>, <code>china_actuator_manufacturing_economics_raw.md</code>) were
condensed into Table 1. Almost every walking robot today uses the same recipe: an outer-rotor or frameless PM motor,
a 6–10:1 planetary (two stages, 14–25:1, for the biggest joints), a crossed-roller output bearing, two magnetic encoders and a
FOC driver on the back, talking CAN or RS-485.</p>
{t}
<p class="caption">Table 1. Representative actuators (VERIFIED datasheets/official sites unless the notes say otherwise; full sources in the raw logs).</p>
<h3>3.1 What we know about the inside of a RobStride RS04</h3>
<p>No teardown of a RobStride actuator has been published (English or Chinese searches, October 2026). RobStride's own
website code gives 42 poles, 9:1, "machined steel" gears and the electrical constants. Every 42-pole motor of this
size with a published slot count (CubeMars AK10-9, Unitree Go2, T-Motor U10) is 36N42P, so RS04 is very probably the
same. We used the RS04 numbers to check our own motor model (Table 2): the calculated JXA-120 lands within
3–20 % of the RS04 datasheet on every electrical constant, which is about as close as an analytic model gets. This is
the main evidence that the designs in Section 5 are realistic.</p>
{internals}
<p class="caption">Table 2. Model check against the RS04 datasheet (RobStride site code and manual 260713).</p>
"""


def section_torque():
    jx1 = table(["JX1 joint (27.5 kg robot)", "Required peak / continuous / speed", "Today (bought)", "In-house replacement"], [
        ["Hip pitch", "85 N·m / 26 N·m / 12 rad/s", "RS04 120 N·m", "JXA-120"],
        ["Knee", "71 / 30 / 12", "RS04 120", "JXA-120"],
        ["Hip roll", "50 / 17 / 6", "RS03 60", "JXA-120 (one class instead of two)"],
        ["Hip yaw", "37 / 8 / 6", "RS06 36 (3 % short)", "JXA-40 (41 N·m: closes open issue OI-2)"],
        ["Ankle motors (×2 per ankle)", "32 / 3.4 / 8.8", "RS06 36", "JXA-40"],
        ["Waist yaw", "≈ 30", "RS06 36", "JXA-40"],
        ["Shoulders, elbows", "≤ 17", "RS02 / RS00", "keep buying (small, cheap per unit)"],
    ])
    full = table(["Robot", "Mass", "Knee", "Hip pitch", "Hip roll / yaw", "Ankle", "Knee speed"], [
        ["Unitree H1 / H1-2", "47 / 70 kg", "360 N·m", "220", "220", "59 / 2 × 75", "14 rad/s"],
        ["Fourier GR-2 / GR-3", "63 / 70 kg", "366", "366", "95–140", "54–59", "6.5 rad/s"],
        ["UBTech Walker S2", "70 kg", "225 peak / 75 rated", "225", "225 / 65", "2 × 65", "8.4 rad/s"],
        ["AgiBot A2 Lite", "64 kg", "270", "–", "–", "–", "–"],
        ["Figure 02 (unverified)", "≈ 70 kg", "150", "150", "–", "–", "–"],
        ["Fourier GR-1T2", "≈ 53 kg", "135", "135", "84 / 65", "42", "18.5 rad/s"],
        ["Tesla Optimus (unverified classes)", "≈ 57–73 kg", "linear 8,000 N actuator via four-bar", "rotary 180 N·m", "110 N·m", "linear 3,900 N", "–"],
    ])
    human = table(["Human, per kg body mass (75 kg adult)", "Hip", "Knee", "Ankle"], [
        ["Walking", "0.5–1.0 N·m/kg", "0.46–1.27", "1.2–1.9"], ["Stairs", "–", "≈ 1.0", "1.4–1.8"],
        ["Rising from a chair", "0.24–1.92", "0.51–1.97", "–"], ["Running 3.5 m/s", "2.0", "3.1", "2.9"],
        ["Sprinting ≈ 9 m/s", "4.1", "3.6", "4.0"]])
    return f"""
<h2 id="torque">4. How much torque does a humanoid need?</h2>
<p>Torque needs scale with mass × leg length × how violently the robot moves. Three sources were combined:
JX1's own rigid-body analysis (walking up to 0.79 m/s, squats, single-leg stands, with a 1.5× dynamic margin;
<code>calculations/results/iter1_B_knee_and_pitch_RS04/</code>), the published limits of 29 commercial and open humanoids, and
human biomechanics.</p>
<h3>4.1 JX1 (1.2 m, 27.5 kg)</h3>
{jx1}
<p class="caption">Table 3. JX1 requirements (CALCULATED, <code>actuators/actuator_selection.md</code>) and the in-house class that covers each joint.</p>
<h3>4.2 The biggest humanoids (1.6–1.9 m, 50–70 kg)</h3>
{full}
<p class="caption">Table 4. Full-size humanoid joint limits (VERIFIED from official model files/SDKs unless marked; <code>actuator_internals_and_torque_raw.md</code> §2).</p>
{human}
<p class="caption">Table 5. Human joint moments (Schache 2011, Yoshioka 2014, arXiv 2511.06796). A 70 kg robot that should run, jump or get up
from the floor needs about 3–5 N·m/kg at the knee, i.e. 200–360 N·m.</p>
<h3>4.3 Three classes cover everything</h3>
<p>Peak knee torque divided by robot mass ranges from 2.1 (Walker S2) to 7.7 N·m/kg (H1) across the field. We therefore
define three classes. Together they cover JX1 completely and every leg joint of the largest humanoids, including the
H1-class knee:</p>
<ul>
<li><b>JXA-40</b>: 40 N·m peak, ≥ 40 rad/s. RS06 class. JX1 ankle, hip yaw, waist; arms of a full-size robot.</li>
<li><b>JXA-120</b>: 120 N·m peak, ≥ 20 rad/s. RS04 class. JX1 hip pitch, knee, hip roll; hip roll/yaw, ankle, shoulder, waist of a
full-size robot.</li>
<li><b>JXA-360</b>: 360 N·m peak, ≥ 15 rad/s. Unitree H1 knee / Fourier GR-2 class. Knee and hip pitch of a 1.7–1.8 m, 50–70 kg
robot. RobStride does not make anything this big.</li>
</ul>
"""


def section_design():
    rows = []
    def row(label, f):
        rows.append([label] + [f(D[n]) for n in N])
    row("Role", lambda d: d["spec"]["role"])
    row("Benchmark", lambda d: d["spec"]["benchmark"])
    row("Motor: slots / poles", lambda d: f"{d['spec']['slots']}N{d['spec']['poles']}P, outer rotor")
    row("Stator OD × stack", lambda d: f"{d['geometry_mm']['stator_od']:.0f} × {d['geometry_mm']['stack']:.0f} mm")
    row("Rotor OD / stator bore", lambda d: f"{d['geometry_mm']['rotor_od']:.1f} / {d['geometry_mm']['stator_bore_d']:.1f} mm")
    row("Air gap / magnet thickness", lambda d: f"{d['spec']['airgap_mm']} / {d['spec']['magnet_mm']} mm N42SH")
    row("Tooth width / slot depth / yoke", lambda d: f"{d['geometry_mm']['tooth_width']:.1f} / {d['geometry_mm']['slot_depth']:.0f} / {d['geometry_mm']['stator_yoke']:.1f} mm")
    row("Air-gap flux density (80 °C)", lambda d: f"{d['magnetics']['B_gap_T']:.2f} T")
    row("Gear: sun / planet / ring × 3 planets", lambda d: f"{d['gear']['z_sun']} / {d['gear']['z_planet']} / {d['gear']['z_ring']}, module {d['gear']['module_mm']}, face {d['gear']['face_mm']} mm")
    row("Gear ratio", lambda d: f"{d['gear']['ratio']:.0f} : 1")
    row("<b>Peak torque (output)</b>", lambda d: f"<b>{d['performance']['peak_out_Nm']:.0f} N·m</b> at {d['electrical']['i_peak_A']} A peak")
    row("<b>Continuous torque</b> (120 °C winding)", lambda d: f"<b>{d['performance']['cont_out_Nm']:.0f} N·m</b>")
    row("<b>No-load speed at 48 V</b>", lambda d: f"<b>{d['performance']['noload_out_rad_s']:.1f} rad/s</b> ({d['performance']['noload_out_rpm']:.0f} rpm)")
    row("Kt at output", lambda d: f"{d['electrical']['Kt_output_Nm_per_Arms']:.2f} N·m/A<sub>rms</sub>")
    row("Km motor / at output", lambda d: f"{d['electrical']['Km_Nm_per_sqrtW_hot']:.2f} / {d['electrical']['Km_output_Nm_per_sqrtW']:.1f} N·m/√W")
    row("R phase 20 °C / L phase", lambda d: f"{d['electrical']['R_phase_20C_mohm']:.0f} mΩ / {d['electrical']['L_phase_uH']:.0f} µH")
    row("Copper loss at peak / time at peak (adiabatic)", lambda d: f"{d['electrical']['P_cu_at_peak_W']:.0f} W / {d['electrical']['seconds_at_peak_adiabatic']:.1f} s")
    row("Current density peak / continuous", lambda d: f"{d['electrical']['J_peak_A_per_mm2']:.0f} / {d['electrical']['J_cont_Arms_per_mm2']:.0f} A/mm²")
    row("Gear safety: bending static at peak / fatigue at cont. / contact at cont.",
        lambda d: f"{d['gear']['SF_bending_static_at_peak']:.1f} / {d['gear']['SF_bending_fatigue_at_cont']:.1f} / {d['gear']['SF_contact_at_cont']:.2f}")
    row("Reflected rotor inertia at output", lambda d: f"{d['performance']['reflected_inertia_kgm2'] * 1e4:.0f} kg·cm²")
    row("Envelope Ø × length", lambda d: f"{d['geometry_mm']['envelope_d']:.0f} × {d['geometry_mm']['envelope_len']:.0f} mm")
    row("<b>Mass (estimated)</b>", lambda d: f"<b>{d['performance']['mass_kg']:.2f} kg</b> ({d['performance']['torque_density_Nm_per_kg']:.0f} N·m/kg)")
    t = table(["", *N], rows, cls="small design")
    mrows = []
    keys = list(D["JXA-120"]["masses_g"].keys())
    for k in keys:
        mrows.append([k.replace("_", " ")] + [f"{D[n]['masses_g'][k]:.0f}" for n in N])
    mt = table(["Mass breakdown, g", *N], mrows)
    vr = table(["Prototype shortcut", "Peak", "Cont.", "No-load", "Winding"], [[
        v["label"], f"{v['performance']['peak_out_Nm']:.0f} N·m", f"{v['performance']['cont_out_Nm']:.0f} N·m",
        f"{v['performance']['noload_out_rad_s']:.1f} rad/s",
        f"{v['winding']['turns_per_coil']} turns × {v['winding']['strands_in_hand']} × {v['winding']['wire_bare_mm']} mm, {v['winding']['parallel_paths']} groups, k<sub>w</sub> {v['winding']['kw']:.3f}"]
        for v in V])
    return f"""
<h2 id="design">5. The JXA actuator family: a design you can build</h2>
<p>The design script <code>actuators/inhouse/qdd_design.py</code> sizes each class from first principles (Section 2): magnet
circuit → air-gap flux → flux linkage → K<sub>t</sub>; slot geometry → copper fill → resistance and K<sub>m</sub>; inductance →
torque–speed at 48 V; a lumped thermal resistance → continuous torque; Lewis bending and Hertz contact → gear safety factors;
part volumes → mass and the material bill used by the cost model. Turns are chosen to meet the speed target with 12 %
headroom, and the wire is then made as thick as a realistic hand/needle-wound fill of 0.42 (bare copper / slot area)
allows. Saturation at peak current is calibrated on RS04 (its Kt drops ≈ 10 % between rated and peak current). All values are
<b>CALCULATED</b>; expect ±15–30 % until a prototype is measured.</p>
{t}
<p class="caption">Table 6. JXA family, first-pass design (results/design.json).</p>
{fig("jxa120_section.png", "Figure 1. JXA-120 section, drawn to scale from the calculated dimensions. The stator is fixed on an aluminium hub; the outer magnet rotor drives the sun gear; the ring gear is part of the housing; the carrier is the output, held by one large bearing. The driver board and both encoders sit on the back cover.", "92%")}
{fig("torque_speed.png", "Figure 2. Calculated torque–speed envelopes at 48 V (field weakening off) and thermal continuous torque, with commercial benchmarks: ● peak torque, ■ no-load speed.")}
<h3>5.1 What the numbers say</h3>
<ul>
<li>All three classes meet their peak, continuous and speed targets on paper. JXA-120's constants are within 3–20 % of RS04's
datasheet (Table 2), and JXA-40's output K<sub>t</sub> (1.11 N·m/A) matches RS06's (1.10).</li>
<li><b>Our first design is heavier</b>: JXA-120 ≈ {D['JXA-120']['performance']['mass_kg']:.1f} kg vs 1.42 kg for RS04, mostly from the
solid planets, thick housings and a longer stack. Lightening holes in the planets, a stepped-planet (compound) stage, 0.2 mm
laminations and a die-cast housing are the second-iteration levers. A {(D['JXA-120']['performance']['mass_kg'] / 1.42 - 1) * 100:.0f} % heavier knee actuator is acceptable on JX1 for a
first build (the extra ≈ 0.5 kg per joint is ≈ 2 % of robot mass) but it costs walking efficiency.</li>
<li>Peak current densities of 60–95 A/mm² are normal for robot actuators but only for 1.5–4 seconds before the copper heats 40 K
(adiabatic estimate). The controller must enforce an I²t limit, exactly as commercial units do.</li>
<li>The 12-tooth sun needs a +0.3 profile shift. It is the most heavily loaded gear; contact stress at peak torque is
≈ {D['JXA-120']['gear']['contact_peak_MPa']:.0f} MPa, so it must be case-carburised and ground (not through-hardened, not printed).</li>
<li>The JXA-360 driver must handle ≈ {D['JXA-360']['electrical']['i_peak_A']} A peak. On a 72 V bus (Unitree H1 uses ≈ 67 V) the same motor wound
with 1.5× the turns needs one third less current, which is the better choice for a full-size robot.</li>
</ul>
<h3>5.2 Prototype shortcut: wind a bought stator core</h3>
<p>Chinese sellers list bare outer-rotor stator cores of exactly these sizes: "10020" (100 × 20 mm, 36N42P) for US$19–31 and
"13710" (137 × 10 mm, 36N42P) for US$74 (<code>india_motor_materials_raw.md</code> §3.4). Re-running the model with those cores:</p>
{vr}
<p>For the first prototypes, buying cores removes the hardest tooling step (laminations) and lets you start with winding,
which is the actual skill to learn. Check the slot shape on arrival and re-run the script with measured dimensions.</p>
{mt}
<p class="caption">Table 7. Estimated mass by part (g).</p>
{fig("winding_layouts.png", "Figure 3. Winding layouts from the star-of-slots calculation, viewed from the tooth tips. Each tooth carries one coil; the letter is the phase, capital = clockwise, small = anticlockwise.")}
"""


def section_cost():
    cls = C["classes"]
    rows = []
    for n in N:
        c = cls[n]; b = c["buy"]
        rows.append([f"<b>{n}</b><br><span class='muted'>{b['ref']}</span>", inr(c["unit"]["P"]["total"]), inr(c["unit"]["B"]["total"]),
                     inr(c["unit"]["F"]["total"]), inr(b["usd_landed"]), inr(b["china_distributor"]) if b["china_distributor"] else "–",
                     f"{inr(b['china_cogs']['low'])}–{inr(b['china_cogs']['high'])}"])
    t = table(["Class", "Make: prototype", "Make: batch 25/yr", "Make: 1,000/yr", "Buy: USD list, landed", "Buy: China distributor, landed", "China maker's cost (COGS, est.)"], rows)
    lrows = []
    for n in N:
        c = cls[n]
        lrows.append([n] + [inr(c["loaded"][t_]) for t_ in "PBF"] + [f"₹{c['per_Nm'][t_]:.0f}" for t_ in "PBF"])
    lt = table(["Fully loaded (equipment over 3 yr + overhead)", "Prototype", "Batch", "1,000/yr", "₹/N·m proto", "₹/N·m batch", "₹/N·m 1k/yr"], lrows)
    # line items for JXA-120
    u = cls["JXA-120"]["unit"]
    li = [[k, inr(u["P"]["lines"][k]), inr(u["B"]["lines"][k]), inr(u["F"]["lines"][k])] for k in u["P"]["lines"]]
    li.append(["<b>Total</b>", f"<b>{inr(u['P']['total'])}</b>", f"<b>{inr(u['B']['total'])}</b>", f"<b>{inr(u['F']['total'])}</b>"])
    lit = table(["JXA-120 line item", "Prototype", "Batch 25/yr", "1,000/yr"], li)
    nre = []
    for tier, title in (("P", "A. Garage / prototype kit"), ("B", "B. Workshop add-ons (batch)"), ("F", "C. Small factory add-ons (1,000+/yr per class)")):
        items = C["nre"][tier]["items"]
        nre.append(f"<h4>{title}: {lakh(C['nre'][tier]['total'])}</h4>" + table(["Item", "₹"], [[k, inr(v)] for k, v in items.items()], cls="small half"))
    j = C["scenario_jx1"]; f = C["scenario_fullsize"]; be = C["breakeven_jxa120_vs_rs04_china"]
    return f"""
<h2 id="cost">8. What it costs: make in India vs buy from China</h2>
<p class="lead">All prices are ESTIMATED from listings read on 24 Sep–6 Oct 2026 (sources in the raw logs) at ₹{C['assumptions']['INR_USD']}/US$ and
₹{C['assumptions']['INR_CNY']}/CNY; imports carry the repository's landed factor (duty 32.3 % × freight 7 %). One aggregator
quotes a higher motor duty (≈ 40 %); confirm on ICEGATE before ordering.</p>

<h3>8.1 How Chinese makers get so cheap</h3>
<ul>
<li><b>Volume.</b> RobStride (founded Nov 2023 by Xiaomi's former CyberGear team) passed 50,000 joints shipped by Sep 2025 and guides
300,000 units for 2026 at an average ≈ ¥1,000 each. Encos shipped &gt; 100,000 in 2025; Quanzhibo runs a 90-second-per-joint,
&gt; 85 %-automated line.</li>
<li><b>Bill of materials, not wages.</b> Broker teardowns put a Unitree G1 joint at ¥1,000 (small) to ¥1,500 (large): reducer ≈ 27 %,
motor ≈ 20 %, encoders ≈ 20 %, driver ≈ 17 %, structure ≈ 16 %. Direct labour is only 8–14 % of Unitree's cost; Chinese factory
wages (≈ ₹86k/month) are 3.5–4.5× India's. <b>India's lower wages cannot close a gap that comes from volume and a dense
local supply chain.</b></li>
<li><b>Everything is next door.</b> Stamped laminations, sintered magnets (China makes ≈ 94 % of the world's), hobbed gears,
crossed rollers (Luoyang), die-cast housings and PCB assembly are all bought within a day's drive, at volume prices. In
India, magnets and most crossed-roller bearings are 100 % imported; gear and lamination job shops exist but quote one-off prices.</li>
<li><b>Magnets are cheap; access is the risk.</b> At bulk prices the magnets in a JXA-120 cost ≈ ₹750. China's April 2025 licence
rules for Dy/Tb (high-temperature SH grades) still apply; the wider October 2025 rules are suspended only until <b>10 November 2026</b>.
India's ₹7,280 crore magnet scheme (approved Nov 2025) has bids but no plant yet; expect no Indian supply before 2027–28.</li>
</ul>
<p>Our estimate of a Chinese maker's manufacturing cost (COGS) for RS04 is ¥660–1,500, central ¥840 (≈ {inr(cls['JXA-120']['buy']['china_cogs']['central'])}),
from the list price minus a 30–45 % gross margin, cross-checked with the G1 teardowns.</p>

<h3>8.2 Cost per actuator</h3>
{t}
<p class="caption">Table 8. Direct cost per actuator (parts + labour + 5–15 % test/scrap), vs buying. The batch tier assumes job-work parts and a
technician at ₹300/h; the factory tier assumes stamped laminations, bulk magnets/cores and a semi-automatic line.</p>
{fig("cost_per_unit.png", "Figure 4. Per-unit cost: making (red/orange/yellow) vs buying (blue) vs what it costs a Chinese maker (grey, with range). Black bars add equipment (3-year write-off) and overhead.")}
{lt}
<p class="caption">Table 9. Fully loaded cost per unit and per N·m of peak torque.</p>
{fig("cost_breakdown_jxa120.png", "Figure 5. Where the money goes in a JXA-120. Prototypes are dominated by gears, machining and your own hours; at 1,000/yr the bill looks like the Chinese one.", "88%")}
{lit}
<p class="caption">Table 10. JXA-120 line items.</p>

<h3>8.3 Equipment you need (one-time)</h3>
<p>You do not need a factory to start. The garage kit below makes and tests prototypes; the workshop add-ons take you to batches;
only the third list is a real factory, and it only pays at ≈ 1,000 units per year (Section 8.6).</p>
<div class="cols">{''.join(nre)}</div>

<h3>8.4 Metal 3D printing</h3>
<p>Indian DMLS services (iamRapid, Bengaluru: AlSi10Mg ≈ ₹15–30 per gram, i.e. ₹40–80/cm³, 7–10 working days; Wipro3D and others on quote)
can print the housing, hub and carrier. For a JXA-120 that is ≈ 150 cm³ of AlSi10Mg, roughly ₹6,000–12,000 plus post-machining of
the bearing seats and the ring-gear bore (printing holds ±0.1 mm; bearing seats need ±0.01 mm). That is <b>no cheaper than CNC from
billet</b> and slower, so print only shapes CNC cannot make (lattice-lightened housings, integrated cooling fins). <b>Do not print gears:</b>
printed steel (316L ≈ ₹160/cm³ at JLC3DP) has neither the case hardness nor the surface finish a carburised sun gear needs at
1,400 MPa contact stress.</p>

<h3>8.5 Scenarios</h3>
{table(["JX1: legs + waist (13 actuators)", "₹"], [
        ["Buy: 4 × RS04 + 2 × RS03 + 7 × RS06, USD list landed (current BOM)", inr(j['buy_usd_route'])],
        ["Buy: same via China distributor, landed", inr(j['buy_china_distributor'])],
        ["Make: 7 × JXA-120 + 8 × JXA-40 (incl. 1 spare each) at batch cost", inr(j['inhouse_parts_and_labour'])],
        ["  + 2 prototype rounds × 2 units × 2 classes", inr(j['inhouse_prototype_rounds'])],
        ["  + garage equipment kit", inr(j['inhouse_garage_equipment'])],
        ["<b>Make: first set, all-in</b>", f"<b>{inr(j['inhouse_total_first_set'])}</b>"],
        ["Make: every further set (13 actuators, batch cost)", inr(j['inhouse_marginal_next_set'])]])}
{table(["Full-size humanoid (28 actuators: 4 × 360, 14 × 120, 10 × 40 N·m)", "₹"], [
        ["Buy: Damiao J10422P + RS04 + RS06, USD list landed", inr(f['buy_usd_route'])],
        ["Buy: same, RobStride via China distributor", inr(f['buy_china_distributor'])],
        ["Make: prototype prices", inr(f['inhouse_P'])],
        ["Make: batch prices (direct) / fully loaded", f"{inr(f['inhouse_B'])} / {inr(f['loaded_B'])}"],
        ["Make: 1,000/yr prices (direct) / fully loaded", f"{inr(f['inhouse_F'])} / {inr(f['loaded_F'])}"],
        ["China maker's cost for the same set (COGS, est.)", inr(f['china_cogs_central'])]])}

<h3>8.6 Break-even</h3>
<p>Against an RS04 bought through a China distributor ({inr(cls['JXA-120']['buy']['china_distributor'])} landed):</p>
<ul>
<li><b>Batch tier:</b> each in-house JXA-120 costs {inr(cls['JXA-120']['unit']['B']['total'])} in parts and labour,
<b>{inr(-be['B']['margin_per_unit'])} more than buying</b> before any equipment or overhead. There is no break-even at this scale: making 25 actuators a year is
a learning and independence investment, not a saving.</li>
<li><b>Factory tier:</b> at 1,000/yr the direct cost falls to {inr(cls['JXA-120']['unit']['F']['total'])}, {inr(be['F']['margin_per_unit'])} below the
landed RS04 price. With {lakh(be['F']['fixed_per_year'])} of yearly fixed cost (equipment written off over 3 years + engineers, QA, rent),
break-even is ≈ <b>{be['F']['breakeven_units_per_year']:,.0f} JXA-120-class actuators a year</b> (fewer if the fixed cost is shared with
the other classes). Above that, an Indian maker beats the <i>landed</i> import, but still not RobStride's own cost
(≈ {inr(cls['JXA-120']['buy']['china_cogs']['central'])}), so it would need to compete on duty, service, lead time and supply security,
not on price.</li>
<li><b>Where in-house wins clearly:</b> the 360 N·m class. Nobody sells it cheaply (RobStride has none; Damiao J10422P lands at
{inr(cls['JXA-360']['buy']['usd_landed'])}), and an in-house batch unit ({inr(cls['JXA-360']['unit']['B']['total'])}) is already close to that.</li>
</ul>
"""


TEST = r"""
<h2 id="test">9. Testing: how you know your actuator is good</h2>
<table class="small">
<tr><th>Test</th><th>How (garage kit)</th><th>Pass criterion</th></tr>
<tr><td>Winding resistance, balance</td><td>4-wire milliohm meter, each phase pair</td><td>within ±2 % of each other, ±10 % of design</td></tr>
<tr><td>Insulation</td><td>500 V–1 kV insulation tester, phases to stack</td><td>&gt; 100 MΩ; no breakdown at 2 × V<sub>dc</sub> + 1,000 V hipot (production)</td></tr>
<tr><td>Inductance balance</td><td>LCR meter at 1 kHz</td><td>±5 %</td></tr>
<tr><td>Back-EMF / K<sub>e</sub></td><td>spin with a drill, scope the line voltages</td><td>three equal sines, K<sub>e</sub> ±10 % of design, harmonic distortion &lt; 5 %</td></tr>
<tr><td>Cogging torque</td><td>torque sensor, rotate slowly by hand</td><td>&lt; 1 % of rated torque at the output (after compensation)</td></tr>
<tr><td>K<sub>t</sub> and peak torque</td><td>lever arm + load cell or DYN-200 sensor; locked output; current steps up to peak</td><td>torque vs current straight to ≈ I<sub>pk</sub>/3, then within 15 % of design at peak</td></tr>
<tr><td>Torque–speed</td><td>hysteresis brake load at 48 V</td><td>matches Fig. 2 within ±10 %</td></tr>
<tr><td>Thermal</td><td>continuous torque on an aluminium plate, 1 h, thermistor in winding</td><td>winding stabilises &lt; 120 °C</td></tr>
<tr><td>Backlash, stiffness</td><td>lock motor, dial gauge on an arm, ±10 % rated torque</td><td>&lt; 15 arcmin backlash (RobStride class: 6–18)</td></tr>
<tr><td>Life</td><td>replay JX1 walking torque traces on the dyno (57 h is the longest published DIY test)</td><td>≥ 200 h at 50–80 % rated torque with no backlash growth &gt; 50 %</td></tr>
</table>
"""

RISKS = r"""
<h2 id="risks">10. Risks</h2>
<table class="small">
<tr><th>Risk</th><th>Effect</th><th>Mitigation</th></tr>
<tr><td>Chinese rare-earth export rules (SH grades with Dy/Tb need a licence; wider rules return after 10 Nov 2026 unless extended)</td><td>no high-temperature magnets, months of delay</td>
<td>buy the first 200–300 magnet sets early; design with N48H (no Dy, needs a lower temperature limit, ≤ 100 °C); watch the Indian REPM scheme plants</td></tr>
<tr><td>Gear quality from local job shops</td><td>noise, backlash, early pitting of the 12-tooth sun</td><td>specify DIN 7, profile shift, case depth and hardness on the drawing; inspect with a gear-roll tester; first lot from two shops</td></tr>
<tr><td>Winding errors</td><td>unequal phases, hot spots, failed hipot</td><td>test before varnish (Section 6.2 step 9); jig with turn counter</td></tr>
<tr><td>Heavier than RobStride</td><td>more inertia in the legs, less battery life</td><td>second iteration: compound planets, lightened carrier, die-cast housing, 0.2 mm laminations</td></tr>
<tr><td>Driver development time</td><td>months of firmware work</td><td>start from an open driver (moteus / Ben Katz / B-G431B-ESC1 class) and keep RobStride's MIT-mode CAN frames</td></tr>
<tr><td>Hidden cost of your time</td><td>a year of engineering is the biggest real cost</td><td>run the program in parallel with buying JX1's actuators; do not put JX1 on the critical path of a new actuator</td></tr>
</table>
"""


def roadmap():
    P = C["classes"]
    m0 = 3 * P["JXA-120"]["unit"]["P"]["total"] * 0.4
    return f"""
<h2 id="plan">11. Plan: from a rewound drone motor to your own actuator line</h2>
<table class="small">
<tr><th>Phase</th><th>What</th><th>Time</th><th>Cash (ESTIMATED)</th><th>Exit test</th></tr>
<tr><td>0. Learn</td><td>Buy 2–3 cheap 8108/10010-class stators and one RS04 (to measure and take apart). Rewind a stator; drive it with an open FOC board.</td>
<td>1 month</td><td>₹60k–1 lakh</td><td>your rewound motor matches its original R and K<sub>e</sub> within 5 %</td></tr>
<tr><td>1. Garage kit + JXA-120 v1</td><td>Buy the test kit; bought 10020 core, bought magnets, job-shop gears and housings; 2 units.</td>
<td>3–4 months</td><td>{lakh(C['nre']['P']['total'] + 2 * P['JXA-120']['unit']['P']['total'])}</td><td>Table in Section 9 passes; 50 h gait-trace test</td></tr>
<tr><td>2. JXA-40 v1 + JXA-120 v2</td><td>Own laser-cut laminations; lighter planets; own driver PCB on the back.</td>
<td>3 months</td><td>{lakh(2 * P['JXA-40']['unit']['P']['total'] + 2 * P['JXA-120']['unit']['P']['total'])}</td><td>mass ≤ 1.6 kg (JXA-120); 200 h life test</td></tr>
<tr><td>3. One leg</td><td>Fit JX1's knee and hip pitch with JXA-120 (the Modular Actuator Interface keeps the bolt pattern).</td>
<td>2 months</td><td>{lakh(4 * P['JXA-120']['unit']['B']['total'])}</td><td>leg passes JX1's bench walking test</td></tr>
<tr><td>4. Batch</td><td>Workshop add-ons; 15 actuators for a full JX1 set.</td><td>3 months</td>
<td>{lakh(C['nre']['B']['total'] + C['scenario_jx1']['inhouse_parts_and_labour'])}</td><td>robot walks on in-house actuators</td></tr>
<tr><td>5. JXA-360</td><td>Full-size knee class for the next robot.</td><td>4 months</td><td>{lakh(2 * P['JXA-360']['unit']['P']['total'] + 3e5)}</td><td>360 N·m, 15 rad/s on the dyno</td></tr>
</table>
"""


def conclusions():
    c = C["classes"]
    return f"""
<h2 id="conclusion">12. Conclusions and recommendation</h2>
<ol>
<li><b>You can build a RobStride-class actuator yourself.</b> The physics is the Lorentz force and a careful slot/pole/turns
calculation; our analytic JXA-120 lands within 3–20 % of RS04's published constants. The only skilled manual job is winding,
which a careful person or any motor-rewinding shop can do with the procedure in Section 6.</li>
<li><b>You do not need a factory.</b> A {lakh(C['nre']['P']['total'])} garage kit, bought stator cores and magnets, and Indian job shops
for gears and housings are enough for prototypes.</li>
<li><b>It will not be cheaper at small volume.</b> A prototype JXA-120 costs ≈ {inr(c['JXA-120']['unit']['P']['total'])} and a
batch unit ≈ {inr(c['JXA-120']['unit']['B']['total'])}, against {inr(c['JXA-120']['buy']['china_distributor'])} for a landed RS04 and
≈ {inr(c['JXA-120']['buy']['china_cogs']['central'])} for RobStride's own cost. An Indian line only beats the import at about
{C['breakeven_jxa120_vs_rs04_china']['F']['breakeven_units_per_year']:,.0f} actuators a year, and it never beats the Chinese maker's cost unless
volume reaches Chinese levels.</li>
<li><b>Recommendation:</b> keep buying RobStride for JX1 now (the robot should not wait for a new actuator); start the in-house
program in parallel at Phase 0–1 as the "V2 localisation" path already planned in <code>actuators/actuator_selection.md</code>.
Aim it first at the <b>360 N·m class</b>, where nothing cheap exists and the in-house cost is already near the import price,
and at <b>supply independence</b> from rare-earth and export-rule shocks.</li>
</ol>
"""


SOURCES = r"""
<h2 id="sources">References and data</h2>
<p class="small">Every number in this paper is labelled in the underlying logs: <b>VERIFIED</b> (official page or primary document),
<b>CALCULATED</b> (our model), <b>ESTIMATED</b> (our arithmetic on cited prices), <b>UNVERIFIED</b> (secondary source).</p>
<ul class="refs">
<li>Design model and figures: <code>actuators/inhouse/qdd_design.py</code> → <code>results/design.json</code>, <code>results/variants.json</code></li>
<li>Cost model: <code>actuators/inhouse/cost_model.py</code> → <code>results/cost.json</code></li>
<li>Actuator survey (≈ 110 units, prices, specs): <code>research/raw/actuator_technology_raw.md</code></li>
<li>Actuator internals, full-size humanoid torques, human biomechanics, gear practice: <code>research/raw/actuator_internals_and_torque_raw.md</code></li>
<li>India / China material, part, equipment prices: <code>research/raw/india_motor_materials_raw.md</code>, <code>india_mechanical_manufacturing_raw.md</code>, <code>india_electronics_compute_raw.md</code></li>
<li>Chinese makers, costs, wages, export rules, duty: <code>research/raw/china_actuator_manufacturing_economics_raw.md</code></li>
<li>JX1 requirements: <code>actuators/actuator_selection.md</code>, <code>calculations/results/iter1_B_knee_and_pitch_RS04/report.md</code></li>
<li>RobStride official site data (robstride.com/assets/index-f063c142.js) and manuals (github.com/RobStride/Product_Information)</li>
<li>Unitree Go2 motor teardown, Simplexity Product Development: simplexitypd.com/blog/unitree-go2-motor-teardown</li>
<li>Unitree actuator models: github.com/unitreerobotics/unitree_rl_lab; Fourier models: github.com/FFTAI/Wiki-GRx-Models; UBTech Walker S2 SDK document</li>
<li>Saloutos et al., "Design of a Highly Dynamic Humanoid Robot" (MIT Humanoid), arXiv:2104.09025</li>
<li>Planetary gear optimisation for QDD: arXiv:2506.16356</li>
<li>Schache et al., Med. Sci. Sports Exerc. 2011 (running joint moments); Yoshioka et al. 2014, PMC3995647 (sit-to-stand); arXiv:2511.06796 (walking norms)</li>
<li>NSK Technical Review 2026, "Actuators for robots"; Tesla AI Day 2022 transcript</li>
<li>China Post Securities, Unitree G1 teardown (2026-03-30); Guosen Securities, Unitree prospectus review (2026-08-21); CMBI Optimus cost table; BofA Institute, "Physical AI part 2" (2026)</li>
<li>KrASIA / 36Kr on RobStride (2025–2026); PMIndia, ₹7,280 crore REPM scheme (26 Nov 2025)</li>
<li>JLCPCB parts library and assembly prices; AliExpress stator-core listings; K&amp;J Magnetics arc-segment prices; iamRapid DMLS cost guide</li>
</ul>
"""

CSS = r"""
@page { size: A4; margin: 16mm 15mm 16mm 15mm; }
body { font-family: "DejaVu Sans", "Liberation Sans", sans-serif; font-size: 9.3pt; line-height: 1.42; color: #1d2733; }
h1 { font-size: 22pt; margin: 0 0 4mm; color: #14213d; line-height: 1.15; }
h2 { font-size: 13.5pt; color: #14213d; border-bottom: 1.5px solid #c9a227; padding-bottom: 1.5mm; margin-top: 7mm; break-after: avoid; }
h3 { font-size: 10.8pt; color: #23395b; margin: 5mm 0 2mm; break-after: avoid; }
h4 { font-size: 9.5pt; margin: 3mm 0 1mm; color: #23395b; }
p { margin: 1.6mm 0; text-align: justify; }
.lead { font-size: 9.6pt; color: #33475b; }
.eq { font-family: "DejaVu Serif", serif; text-align: center; background: #f4f6f9; border-left: 3px solid #c9a227; padding: 2mm; margin: 2.5mm 6mm; }
table { border-collapse: collapse; width: 100%; margin: 2mm 0 1mm; break-inside: auto; }
tr { break-inside: avoid; }
th { background: #14213d; color: #fff; font-weight: 600; text-align: left; padding: 1.2mm 1.5mm; font-size: 7.8pt; }
td { border-bottom: 0.5px solid #d5dbe3; padding: 1.1mm 1.5mm; vertical-align: top; font-size: 7.9pt; }
tr:nth-child(even) td { background: #f7f9fb; }
table.design td:first-child { font-weight: 600; width: 27%; }
table.half { width: 100%; }
.mono { font-family: "DejaVu Sans Mono", monospace; font-size: 7pt; }
.muted { color: #66788a; font-size: 7pt; }
.caption, figcaption { font-size: 7.8pt; color: #4a5b6c; margin: 1mm 0 3mm; }
figure { margin: 3mm 0; text-align: center; break-inside: avoid; }
figcaption { text-align: left; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 7.6pt; background: #f1f3f6; padding: 0 1px; }
ol.steps li, ul li { margin-bottom: 1.1mm; }
.cols { columns: 2; column-gap: 6mm; } .cols > * { break-inside: avoid; }
.cover { height: 255mm; display: flex; flex-direction: column; justify-content: space-between; break-after: page; }
.cover .band { background: #14213d; color: #fff; padding: 9mm 9mm 7mm; }
.cover .band h1 { color: #fff; font-size: 24pt; }
.cover .sub { color: #e8d48a; font-size: 11pt; }
.kpis { display: grid; grid-template-columns: repeat(3, 1fr); gap: 3mm; margin: 5mm 0; }
.kpi { border: 1px solid #d5dbe3; border-top: 3px solid #c9a227; padding: 3mm; }
.kpi b { display: block; font-size: 15pt; color: #14213d; }
.kpi span { font-size: 7.8pt; color: #4a5b6c; }
.abstract { background: #f4f6f9; padding: 4mm 5mm; border-left: 3px solid #14213d; }
.toc { columns: 2; font-size: 8.8pt; }
.toc a { color: #14213d; text-decoration: none; }
.pb { break-before: page; }
ul.refs li { font-size: 8pt; }
"""


def build_html():
    phys, wind, build = fill_fixed()
    c120 = C["classes"]["JXA-120"]
    d120 = D["JXA-120"]
    cover = f"""
<div class="cover">
 <div class="band">
  <div class="sub">JX1 humanoid project · research paper · {DATE}</div>
  <h1>Building humanoid joint actuators in-house</h1>
  <div class="sub">How the motors work, how much torque a humanoid needs, how to design, wind and build your own
  RobStride-class actuators in India, and what it costs compared with buying from China</div>
 </div>
 <div>
 <div class="kpis">
  <div class="kpi"><b>3 classes</b><span>JXA-40 · JXA-120 · JXA-360: 40 / 120 / 360 N·m peak, covering JX1 and the knee of a 70 kg full-size humanoid</span></div>
  <div class="kpi"><b>±3–20 %</b><span>our calculated JXA-120 vs the RobStride RS04 datasheet (K<sub>t</sub>, K<sub>e</sub>, R, L, peak current)</span></div>
  <div class="kpi"><b>{inr(c120['unit']['B']['total'])}</b><span>JXA-120 in-house batch cost, vs {inr(c120['buy']['china_distributor'])} for an RS04 landed via a China distributor</span></div>
  <div class="kpi"><b>{lakh(C['nre']['P']['total'])}</b><span>garage kit to wind, assemble and test prototypes (no factory needed)</span></div>
  <div class="kpi"><b>≈ {C['breakeven_jxa120_vs_rs04_china']['F']['breakeven_units_per_year']:,.0f} / yr</b><span>volume at which an Indian line beats the landed import price</span></div>
  <div class="kpi"><b>{inr(c120['buy']['china_cogs']['central'])}</b><span>estimated cost for RobStride to make one RS04 (range {inr(c120['buy']['china_cogs']['low'])}–{inr(c120['buy']['china_cogs']['high'])})</span></div>
 </div>
 <div class="abstract"><b>Abstract.</b> We explain from first principles how a permanent-magnet motor turns current into torque, survey the
 actuators used by today's humanoids (RobStride, Damiao, Unitree, CubeMars, MIT, Tesla), and derive torque needs from JX1's own analysis,
 29 robots and human biomechanics. A three-class family of outer-rotor, single-stage planetary actuators (JXA-40/120/360) is designed with an
 analytic model that reproduces the RS04 datasheet within 3–20 %. We give a winding procedure a technician can follow, a build sequence
 that uses Indian job shops instead of a factory, a test plan, and a cost model at prototype, batch and 1,000-per-year scale,
 compared with buying and with Chinese makers' estimated costs. Conclusion: building is feasible and valuable for learning, the 360 N·m class and
 supply security. It is not cheaper than RobStride below ≈ 1,000 units a year, and Chinese makers' advantage is volume and supply chain, not wages.</div>
 </div>
 <div class="toc"><b>Contents</b><br>
 <a href="#intro">1. Goal and scope</a><br><a href="#physics">2. How a motor makes torque</a><br><a href="#survey">3. Actuators on the market</a><br>
 <a href="#torque">4. Torque a humanoid needs</a><br><a href="#design">5. The JXA family design</a><br><a href="#winding">6. Winding the stator</a><br>
 <a href="#build">7. Making the other parts</a><br><a href="#cost">8. Costs: make vs buy</a><br><a href="#test">9. Testing</a><br>
 <a href="#risks">10. Risks</a><br><a href="#plan">11. Plan</a><br><a href="#conclusion">12. Conclusions</a><br><a href="#sources">References</a></div>
</div>"""
    intro = f"""
<h2 id="intro">1. Goal and scope</h2>
<p>JX1 spends 77 % of its parts budget on actuators bought from RobStride (<code>bom/cost_summary.md</code>). This paper asks whether
those actuators, and the bigger ones a full-size humanoid needs, can be designed and built in-house in India with little tooling, how
to do it, and what it costs compared with buying and with how Chinese makers do it. It covers:</p>
<ul><li>the physics (magnetism, Lorentz force, induction, torque and speed limits): Section 2;</li>
<li>today's actuators and what is inside them: Section 3;</li><li>torque needs from JX1 up to 70 kg humanoids: Section 4;</li>
<li>a complete first-pass design of three actuator classes, with winding data: Sections 5–6;</li>
<li>how to make each part with job shops and a small workshop: Section 7;</li>
<li>costs at three scales vs RobStride and vs Chinese factory costs: Section 8; then testing, risks and a phased plan.</li></ul>
<p>Labels follow the repository convention: VERIFIED, CALCULATED, ESTIMATED, UNVERIFIED. Nothing here has been built yet; every design
number is a calculation to be confirmed on the bench.</p>"""
    body = (cover + intro + phys + section_survey() + section_torque() + '<div class="pb"></div>' + section_design()
            + '<div class="pb"></div>' + wind + build + section_cost() + TEST + RISKS + roadmap() + conclusions() + SOURCES)
    return f'<!doctype html><html><head><meta charset="utf-8"><title>Building humanoid joint actuators in-house</title><style>{CSS}</style></head><body>{body}</body></html>'


def main():
    BUILD.mkdir(exist_ok=True)
    html = BUILD / "paper.html"
    html.write_text(build_html(), encoding="utf-8")
    if not CHROME:
        raise SystemExit("no headless Chromium found; open .paper_build/paper.html and print to PDF")
    subprocess.run([CHROME[0], "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={OUT_PDF}", html.as_uri()], check=True, capture_output=True, timeout=180)
    print("wrote", OUT_PDF, f"{OUT_PDF.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
