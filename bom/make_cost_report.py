"""JX1 component list and cost estimate: a 9-page A4 PDF generated from bom/master_bom.csv.

Every price, quantity and total comes from the master BOM (the same numbers as bom/cost_summary.md); the report only
arranges them: cover, overview, cost summary, actuators, structure, electronics, power, printing + cost-reduction options,
and the complete item list with the grand total. The HTML is printed to PDF with Microsoft Edge (headless).
Usage: .venv/Scripts/python bom/make_cost_report.py [--preview]   (--preview also writes one PNG per page for checking)
"""
from __future__ import annotations

import argparse
import csv
import html
import re
import subprocess
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOM = ROOT / "bom" / "master_bom.csv"
OUT_PDF = ROOT / "bom" / "JX1_cost_estimate.pdf"
BUILD = ROOT / "bom" / ".report_build"
IMG = ROOT / "docs" / "images"
# a synchronous headless Chromium (the one puppeteer/HyperFrames installs) is preferred; the Edge launcher returns before
# its print job finishes, so with Edge the outputs are polled for
HEADLESS = sorted(Path.home().glob(".cache/puppeteer/chrome-headless-shell/*/chrome-headless-shell-win64/chrome-headless-shell.exe"))
EDGE = Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
N_PAGES = 9
CONTINGENCY = 0.15
REPORT_DATE = "September 2026"
REPO = "github.com/nickthelegend/thenar-jx1"

# FEA safety factors, static / fatigue (docs/final_robot_specification.md; required >= 1.5 for aluminium)
FEA = {"JX1-007": "1.77 / 1.58", "JX1-008": "2.76 / 3.80", "JX1-009": "2.31 / 2.78", "JX1-010": "3.37 / 4.17",
       "JX1-014": "14.4 / 24.7", "JX1-017": "3.50 / 2.03", "JX1-021": "2.90 / 3.44", "JX1-041": "4.44 / 3.59",
       "JX1-042": "2.05–5.99 / 1.66–4.84", "JX1-011": "steel"}
# where each actuator line is used
ACT_USE = {"JX1-001": "hip pitch ×2, knee ×2", "JX1-002": "hip roll ×2", "JX1-003": "hip yaw ×2, ankle ×4 (2 per ankle)",
           "JX1-004": "waist yaw", "JX1-005": "shoulder pitch ×2, shoulder roll ×2", "JX1-006": "shoulder yaw ×2, elbow ×2"}
# cost category of each line (by type, for the summary); lines not listed fall under their subsystem rule below
TYPE_OF = {**{f"JX1-00{i}": "Joint actuators" for i in range(1, 7)},
           **{k: "Machined / laser-cut metal parts" for k in ["JX1-007", "JX1-008", "JX1-009", "JX1-010", "JX1-011", "JX1-014",
                                                            "JX1-017", "JX1-021", "JX1-041", "JX1-042"]},
           **{k: "Bearings, rods, rubber, fasteners" for k in ["JX1-012", "JX1-013", "JX1-015", "JX1-016", "JX1-018", "JX1-020"]},
           **{k: "Electronics, sensors, servos" for k in ["JX1-019", "JX1-022", "JX1-023", "JX1-024", "JX1-025", "JX1-026",
                                                        "JX1-027", "JX1-028", "JX1-029", "JX1-044", "JX1-045", "JX1-046"]},
           **{f"JX1-0{i}": "Battery and power distribution" for i in range(30, 41)},
           **{k: "3D printing and consumables" for k in ["JX1-047", "JX1-048", "JX1-049", "JX1-050"]}}
# stage A of the purchase plan: what to buy first to validate the design on the bench (line id -> quantity)
BENCH_KIT = {"JX1-001": 1, "JX1-002": 1, "JX1-003": 1, "JX1-024": 1, "JX1-027": 1, "JX1-049": 2}
# actuator load while walking at 0.8 m/s with the learned controller (jx1_walk_rough, CAD model; final spec):
# (joint, actuator, simulated peak N·m, capability N·m, how compared)
TORQUE = [("Hip yaw", "RS06", 11.3, 36, "1.5×"), ("Hip roll", "RS03", 31.4, 60, "1.5×"), ("Hip pitch", "RS04", 28.2, 120, "1.5×"),
          ("Knee", "RS04", 61.5, 120, "1.5×"), ("Ankle pitch", "2 × RS06 via linkage", 32.9, 46, "1.0×"),
          ("Ankle roll", "2 × RS06 via linkage", 18.2, 51, "1.0×")]
# realistic ways to spend less (from the BOM "Alternative" column): (line id, what changes, trade-off)
SAVINGS = [
    ("ACT", "Buy the same 21 RobStride actuators through a China distributor (CNY list + 5 % agent)",
     "same parts; longer lead time, agent risk"),
    ("JX1-034", "Motor-bus switch as a MOSFET stage on the hub PCB instead of the Flipsky switch", "needs design and testing"),
    ("JX1-046", "IMX219-77 mono camera instead of the IMX219-83 stereo camera", "no stereo depth (walking unaffected)"),
    ("JX1-038", "Synchronous buck instead of the isolated Mean Well 5 V supply", "not isolated; more noise on the Jetson rail"),
    ("JX1-007", "6061-T6 box-beam hip-yaw bracket (variant Y7) instead of CNC 7075-T6", "hip stack +18 mm; re-verify CAD/FEA"),
    ("JX1-009", "8 mm thigh plate (variant V7, SF 1.64 / 1.94)", "smaller strength margin"),
    ("JX1-018", "Printed TPU 95A sole instead of the rubber mat", "grip to be tested"),
]


# ------------------------------------------------------------------------------------------------ helpers
def inr(n, sign=True):
    """Indian digit grouping: 712481 -> 7,12,481."""
    neg = n < 0
    s = str(int(round(abs(n))))
    head, tail = s[:-3], s[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    out = ",".join(groups + [tail]) if groups else tail
    return ("−" if neg else "") + ("₹" if sign else "") + out


ONES = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen",
        "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def words(n):
    """Indian number words: 819353 -> Eight Lakh Nineteen Thousand Three Hundred Fifty-Three."""
    def two(x):
        return ONES[x] if x < 20 else TENS[x // 10] + ("-" + ONES[x % 10] if x % 10 else "")

    def three(x):
        return " ".join(p for p in [ONES[x // 100] + " Hundred" if x // 100 else "", two(x % 100) if x % 100 else ""] if p)
    n = int(round(n))
    parts = []
    for div, name in [(10 ** 7, "Crore"), (10 ** 5, "Lakh"), (10 ** 3, "Thousand")]:
        if n >= div:
            parts.append(f"{two(n // div) if div < 10 ** 7 else words(n // div)} {name}")
            n %= div
    if n:
        parts.append(three(n))
    return " ".join(parts)


def e(s):
    return html.escape(str(s), quote=True)


def num(s):
    try:
        return float(str(s).replace(",", ""))
    except ValueError:
        return 0.0


def short(s, n):
    s = str(s)
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def img_url(name):
    return (IMG / name).resolve().as_uri()


def repo_url(rel):
    return (ROOT / rel).resolve().as_uri()


# ------------------------------------------------------------------------------------------------ data
def load():
    rows = list(csv.DictReader(BOM.open(encoding="utf-8")))
    for r in rows:
        r["qty"] = int(num(r["Quantity"]))
        r["unit"] = num(r["Unit price INR"])
        r["total"] = num(r["Total INR"])
        r["alt"] = num(r["Alternative price INR"])
        r["kg"] = num(r["Weight kg (each)"])
        r["in_total"] = r["Status"].strip().upper() != "DEFERRED"
    return rows


def summarise(rows):
    inc = [r for r in rows if r["in_total"]]
    total = sum(r["total"] for r in inc)
    by_sub, by_type, by_phase = defaultdict(float), defaultdict(float), defaultdict(float)
    for r in inc:
        by_sub[r["Subsystem"]] += r["total"]
        by_type[TYPE_OF.get(r["ID"], "Deferred")] += r["total"]
        by_phase[r["Phase"]] += r["total"]
    return dict(total=total, cont=round(total * CONTINGENCY), grand=total + round(total * CONTINGENCY),
                by_sub=dict(sorted(by_sub.items(), key=lambda kv: -kv[1])), by_type=dict(sorted(by_type.items(), key=lambda kv: -kv[1])),
                by_phase=dict(by_phase), deferred=[r for r in rows if not r["in_total"]])


def check_against_summary(s):
    """The report must agree with the generated bom/cost_summary.md."""
    txt = (ROOT / "bom" / "cost_summary.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*Robot total[^|]*\|\s*\*\*([\d,]+)\*\*", txt)
    if m:
        ref = int(m.group(1).replace(",", ""))
        assert ref == int(s["total"]), f"BOM total {s['total']} != cost_summary.md {ref}; run bom/build_bom.py first"


# ------------------------------------------------------------------------------------------------ page parts
def page(n, title, body, cls=""):
    head = "" if n == 1 else f'''<div class="phead"><span><b>JX1</b> · JNTUH's first humanoid · component list and cost estimate</span><span>{n} / {N_PAGES}</span></div>'''
    foot = "" if n == 1 else f'''<div class="pfoot"><span>Prices in INR, GST and import duty included where stated · checked {REPORT_DATE} · items marked ESTIMATED need supplier quotes</span></div>'''
    h = f'<h1>{title}</h1>' if title else ""
    return f'''<section class="page {cls}" id="p{n}">{head}<div class="content">{h}{body}</div>{foot}</section>'''


def table(cols, rows, cls="", foot=None):
    """cols: list of (header, css class). rows: list of cell lists (already HTML)."""
    th = "".join(f'<th class="{c}">{h}</th>' for h, c in cols)
    trs = []
    for r in rows:
        rc = ""
        if isinstance(r, tuple):
            r, rc = r
        trs.append(f'<tr class="{rc}">' + "".join(f'<td class="{c}">{v}</td>' for v, (_, c) in zip(r, cols)) + "</tr>")
    tf = ""
    if foot:
        tf = "<tfoot><tr>" + "".join(f'<td class="{c}">{v}</td>' for v, (_, c) in zip(foot, cols)) + "</tr></tfoot>"
    return f'<table class="{cls}"><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody>{tf}</table>'


def item_rows(rows, ids, extra=None):
    out = []
    for r in rows:
        if r["ID"] not in ids:
            continue
        cells = [f'<span class="id">{r["ID"][4:]}</span>',
                 f'<b>{e(r["Part"])}</b><br><span class="sub">{e(short(r["Exact model"], 110))}</span>',
                 f'<span class="spec">{e(short(r["Specification"], 160))}</span>',
                 f'{r["qty"]}', inr(r["unit"]), f'<b>{inr(r["total"])}</b>']
        if extra:
            cells.insert(3, extra(r))
        out.append((cells, "muted" if not r["in_total"] else ""))
    return out


def bars(items, total, cls=""):
    top = max(items.values())
    rows = []
    for k, v in items.items():
        rows.append(f'''<div class="bar"><div class="blabel">{e(k)}</div><div class="btrack"><div class="bfill {cls}" style="width:{100 * v / top:.1f}%"></div></div>
<div class="bval">{inr(v)}</div><div class="bpct">{100 * v / total:.1f} %</div></div>''')
    return '<div class="bars">' + "".join(rows) + "</div>"


def subtotal(label, v):
    return f'<div class="subtotal"><span>{label}</span><b>{inr(v)}</b></div>'


# ------------------------------------------------------------------------------------------------ pages
def build(rows, s):
    by_id = {r["ID"]: r for r in rows}
    ids = lambda sub: [r["ID"] for r in rows if TYPE_OF.get(r["ID"], "Deferred") == sub]  # noqa: E731
    total, cont, grand = s["total"], s["cont"], s["grand"]
    act_total = s["by_type"]["Joint actuators"]
    pages = []

    # 1 — cover
    pages.append(page(1, "", f'''
<div class="cover-top">
  <div class="kicker">Design proposal · component list and cost estimate</div>
  <div class="wordmark"><span class="dot"></span>JX1</div>
  <div class="tag">JNTUH's first humanoid robot</div>
</div>
<div class="cover-img"><img src="{img_url('jx1_hero.png')}" alt="JX1 humanoid, fully assembled (render of the CAD model)"></div>
<div class="cover-stats">
  <div><b>1.23 m</b><span>height</span></div><div><b>33.6 kg</b><span>mass</span></div>
  <div><b>23</b><span>joints (DOF)</span></div><div><b>21</b><span>actuators</span></div><div><b>{len(rows)}</b><span>BOM lines</span></div>
</div>
<div class="cover-cost">
  <div><span>Estimated cost of the robot</span><b>{inr(total)}</b></div>
  <div class="grand"><span>With 15 % prototype contingency</span><b>{inr(grand)}</b></div>
</div>
<div class="cover-foot">{REPORT_DATE} · design v0.5 · all figures from the project bill of materials ({REPO})</div>
''', "cover"))

    # 2 — overview
    spec = [("Height / mass", "1.23 m / 33.6 kg (CAD, all parts)"),
            ("Joints (DOF)", "23 — legs 12 (6 per leg), waist 1, arms 8 (4 per arm), neck 2"),
            ("Legs", "thigh 0.27 m, shin 0.30 m, hip spacing 0.20 m, foot 210 × 95 mm; parallel ankle (2 motors per ankle)"),
            ("Actuators", "21 RobStride 48 V CAN actuators (RS04, RS03, RS06, RS02, RS00) + 2 neck bus servos"),
            ("Brain", "NVIDIA Jetson Nano 4 GB — runs the learned walking controller 50 times a second"),
            ("Motor control", "2 × Teensy 4.1 hub boards, 6 CAN buses at 1 Mbit/s, 500 Hz control loop"),
            ("Sensors", "BNO085 IMU, IMX219-83 stereo camera, 21 joint encoders, optional foot pressure sensors"),
            ("Battery", "13S2P Li-ion, 41.6–54.6 V, 468 Wh; ≈ 1.3 h walking, 2.3–4.1 h standing (calculated)"),
            ("Structure", "6061-T6 / 7075-T6 aluminium plates, every structural part strength-checked (FEA, SF ≥ 1.5)"),
            ("Walking", "up to 0.8 m/s with the reinforcement-learning controller (simulation of the CAD model)")]
    spec_html = "".join(f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in spec)
    pages.append(page(2, "1. The JX1 humanoid", f'''
<p class="lead">JX1 is a full-size walking humanoid robot designed to be built from parts that can be bought in India and
metal plates that any laser-cutting or CNC job shop can make. The complete design (3D CAD, strength analysis, wiring,
firmware, physics simulation and a trained walking controller) is finished and verified on the computer. This document
lists every component of the first prototype and what it costs.</p>
<div class="two">
  <div><h2>Specification</h2><table class="spec-t">{spec_html}</table></div>
  <div class="imgcol"><img src="{img_url('jx1_front.png')}" class="framed tall" alt="JX1 front view"></div>
</div>
<div class="two">
  <div><h2>Design status</h2><ul class="checks">
    <li class="ok">3D CAD of all 87 parts; every joint moved through its range and checked for collisions</li>
    <li class="ok">Strength analysis (FEA) of every structural part — all pass in aluminium</li>
    <li class="ok">Physics simulation: standing, squatting, walking, push recovery</li>
    <li class="ok">Walking controller trained (reinforcement learning), tested in simulation and over ROS 2</li>
    <li class="ok">Drawings and STEP files for the job shop, wiring diagrams, hub firmware</li>
    <li class="next">Next: supplier quotes → purchase → assembly → first power-on</li></ul></div>
  <div><h2>How this estimate was made</h2><ul class="notes">
    <li>Indian catalogue prices (Robu, Evelta, IndustryBuying, Moglix, bearinghouse.in …), GST included where stated.</li>
    <li>Imported actuators: USD list price × ₹95.96 × 1.323 (import duty) × 1.07 (shipping) = landed cost.</li>
    <li>Machined and laser-cut parts: ESTIMATED from job-shop rates and plate prices — quotes required.</li>
    <li>15 % contingency for a first prototype (rework, spares, price changes).</li></ul></div>
</div>
<h2>From CAD to a walking robot</h2>
<div class="strip">
  <figure><img src="{img_url('jx1_exploded.png')}" alt="exploded view"><figcaption>87 parts, exploded view of the CAD</figcaption></figure>
  <figure><img src="{repo_url('docs/assembly/step_11.png')}" alt="assembly step 11"><figcaption>assembly step 11 of 22: ankles and feet</figcaption></figure>
  <figure><img src="{img_url('jx1_walking.png')}" alt="walking in simulation"><figcaption>walking in the physics simulation</figcaption></figure>
</div>'''))

    # 3 — cost summary
    sub_rows = [[e(k), inr(v), f"{100 * v / total:.1f} %"] for k, v in s["by_sub"].items()]
    p1 = s["by_phase"].get("1", 0)
    p2 = s["by_phase"].get("2", 0)
    defer = sum(r["total"] for r in s["deferred"])
    stage_a = sum(by_id[k]["unit"] * q for k, q in BENCH_KIT.items())
    pages.append(page(3, "2. Cost summary", f'''
<div class="cards">
  <div class="card"><span>Robot total</span><b>{inr(total)}</b><em>{len([r for r in rows if r["in_total"]])} line items</em></div>
  <div class="card"><span>Contingency 15 %</span><b>{inr(cont)}</b><em>first-prototype allowance</em></div>
  <div class="card hi"><span>Total budget</span><b>{inr(grand)}</b><em>≈ ₹{grand / 1e5:.2f} lakh</em></div>
</div>
<h2>By type of component</h2>
{bars(s["by_type"], total)}
<p class="note">The 21 joint actuators are <b>{100 * act_total / total:.0f} %</b> of the cost. Everything else — metal, electronics,
battery — together is {inr(total - act_total)}.</p>
<div class="two">
  <div><h2>By subsystem</h2>{table([("Subsystem", ""), ("Cost", "r"), ("Share", "r")], sub_rows, "compact",
                                      ["<b>Total</b>", f"<b>{inr(total)}</b>", "100 %"])}</div>
  <div><h2>By build phase</h2>{table([("Phase", ""), ("What it delivers", ""), ("Cost", "r")], [
      ["<b>1</b>", "walking lower body: legs, pelvis, computer, electronics, battery, printing", inr(p1)],
      ["<b>2</b>", "upper body: waist, torso, arms, head, camera, foot sensors", inr(p2)],
      ["<b>3</b>", "grippers (deferred, not in the total)", f'<span class="muted-t">{inr(defer)}</span>']], "compact",
      ["", "<b>Phases 1 + 2</b>", f"<b>{inr(p1 + p2)}</b>"])}
  <p class="note">Phase 1 alone produces a robot that stands and walks; it can be funded first.</p></div>
</div>
<h2>Suggested purchase order</h2>
{table([("Stage", ""), ("What is bought", ""), ("Why", ""), ("Cost", "r"), ("Cumulative", "r")], [
    ["<b>A</b>", "one actuator of each leg size (RS04, RS03, RS06), USB-CAN adapter, one Teensy 4.1, 2 kg PETG-CF",
     "confirm bolt patterns, CAN control and fit-check prints before ordering metal", inr(stage_a), inr(stage_a)],
    ["<b>B</b>", "rest of phase 1: 9 more leg actuators, all metal leg parts, Jetson, hub PCB, battery, power",
     "lower body stands and walks on a safety gantry", inr(p1 - stage_a), inr(p1)],
    ["<b>C</b>", "phase 2: waist, torso, 8 arm actuators, head, camera, foot sensors", "complete humanoid", inr(p2), inr(p1 + p2)],
    ["<b>—</b>", "15 % contingency, released as needed", "rework, spares, price changes", inr(cont), inr(grand)]], "compact")}'''))

    # 4 — actuators
    act_rows = []
    for r in rows:
        if TYPE_OF.get(r["ID"], "Deferred") != "Joint actuators":
            continue
        tq, _, rest = r["Specification"].partition(",")
        act_rows.append([f'<span class="id">{r["ID"][4:]}</span>', f'<b>{e(r["Exact model"])}</b>', e(ACT_USE[r["ID"]]),
                         e(tq.replace(" peak/rated", "")), f'{r["kg"]:.2f}', str(r["qty"]), inr(r["unit"]), f'<b>{inr(r["total"])}</b>'])
    alt_rows, alt_total = [], 0
    for r in rows:
        if TYPE_OF.get(r["ID"], "Deferred") == "Joint actuators":
            alt_total += r["alt"] * r["qty"]
            alt_rows.append([e(r["Exact model"]), str(r["qty"]), inr(r["unit"]), inr(r["alt"]), inr((r["unit"] - r["alt"]) * r["qty"])])
    pages.append(page(4, "3. Joint actuators — the largest cost", f'''
<p class="lead">Each actuator is a complete joint: brushless motor, planetary gearbox, absolute encoder and motor driver in one
housing, controlled over CAN at 48 V. They are bought from RobStride (not stocked by Indian distributors) and imported;
the prices below are landed costs.</p>
{table([("ID", ""), ("Model", ""), ("Used for", ""), ("Torque peak / rated", ""), ("kg", "r"), ("Qty", "r"), ("Unit", "r"), ("Total", "r")],
       act_rows, "items", ["", "<b>21 actuators</b>", "", "", "", "<b>21</b>", "", f"<b>{inr(act_total)}</b>"])}
<div class="two">
  <div><h2>Joint map</h2>{table([("Joint", ""), ("Actuator", ""), ("Count", "r")], [
      ["hip yaw · hip roll · hip pitch", "RS06 · RS03 · RS04", "2 · 2 · 2"],
      ["knee", "RS04", "2"], ["ankle (parallel, 2 motors each)", "RS06", "4"], ["waist yaw", "RS06", "1"],
      ["shoulder pitch · shoulder roll", "RS02 · RS02", "2 · 2"], ["shoulder yaw · elbow", "RS00 · RS00", "2 · 2"],
      ["neck yaw · pitch (see §5)", "Waveshare ST3215 servo", "2"]], "compact")}</div>
  <div><h2>Option: China distributor</h2>{table([("Model", ""), ("Qty", "r"), ("Landed", "r"), ("Via China", "r"), ("Saving", "r")],
      alt_rows, "compact", ["<b>All 21</b>", "", f"<b>{inr(act_total)}</b>", f"<b>{inr(alt_total)}</b>", f"<b>{inr(act_total - alt_total)}</b>"])}
  <p class="note">Same units priced from the Chinese list (CNY, ₹13.52/CNY) plus a 5 % buying-agent fee, duty and shipping.</p></div>
</div>
<h2>Are these actuators strong enough?</h2>
{table([("Joint", ""), ("Actuator", ""), ("Peak torque walking 0.8 m/s", "r"), ("With margin", "r"), ("Available", "r"), ("Used", "r")],
       [[j, a, f"{t:.1f} N·m", f"{t * (1.5 if m == '1.5×' else 1.0):.1f} N·m ({m})", f"{c} N·m", f"<b>{100 * t * (1.5 if m == '1.5×' else 1.0) / c:.0f} %</b>"]
        for j, a, t, c, m in TORQUE], "compact")}
<p class="note">Simulated on the full CAD model with the trained walking controller (calculated, not yet measured). Hip and knee
peaks are multiplied by the 1.5 safety margin used throughout the design; ankle values are compared with what the two-motor
linkage can deliver. The next smaller RobStride size would not be enough at the knee (92 N·m needed, 60 N·m available) or at hip roll (47 N·m needed, 36 N·m available).</p>'''))

    # 5 — structure
    metal = ids("Machined / laser-cut metal parts")
    hw = ids("Bearings, rods, rubber, fasteners")
    metal_rows = []
    for rid in metal:
        r = by_id[rid]
        metal_rows.append([f'<span class="id">{rid[4:]}</span>', f'<b>{e(r["Part"])}</b>', f'<span class="spec">{e(r["Specification"])}</span>',
                           f'{r["kg"]:.2f}', FEA.get(rid, "—"), str(r["qty"]), inr(r["unit"]), f'<b>{inr(r["total"])}</b>'])
    hw_rows = [[f'<span class="id">{by_id[i]["ID"][4:]}</span>', f'<b>{e(by_id[i]["Part"])}</b>', f'<span class="spec">{e(by_id[i]["Exact model"] + " — " + by_id[i]["Specification"])}</span>',
                str(by_id[i]["qty"]), inr(by_id[i]["unit"]), f'<b>{inr(by_id[i]["total"])}</b>'] for i in hw]
    m_tot = sum(by_id[i]["total"] for i in metal)
    h_tot = sum(by_id[i]["total"] for i in hw)
    pages.append(page(5, "4. Structure and mechanical parts", f'''
<p class="lead">The skeleton is flat 6061-T6 aluminium plate (7075-T6 for the most loaded part, the hip-yaw bracket), laser-cut or
CNC-machined from the STEP files and A3 drawings in the repository. 3D-printed versions were analysed too and failed:
the load path must be metal.</p>
{table([("ID", ""), ("Part", ""), ("Material and process", ""), ("kg", "r"), ("FEA SF", "r"), ("Qty", "r"), ("Unit", "r"), ("Total", "r")],
       metal_rows, "items", ["", "<b>Metal parts</b>", "", "", "", "", "", f"<b>{inr(m_tot)}</b>"])}
<p class="note">FEA SF = safety factor, static / fatigue (strength ÷ worst stress; 1.5 required). Prices ESTIMATED from 3-axis CNC
rates (US$20–38/h) and plate at ₹380–400/kg — send the STEP + PDF set to 2–3 job shops for quotes.</p>
<h2>Ankle linkage, bearings and fasteners</h2>
{table([("ID", ""), ("Item", ""), ("Model and specification", ""), ("Qty", "r"), ("Unit", "r"), ("Total", "r")],
       hw_rows, "items", ["", "<b>Hardware</b>", "", "", "", f"<b>{inr(h_tot)}</b>"])}
{subtotal("Structure and mechanical parts", m_tot + h_tot)}'''))

    # 6 — electronics
    el = ids("Electronics, sensors, servos")
    el_rows = item_rows(rows, el)
    e_tot = sum(by_id[i]["total"] for i in el)
    pages.append(page(6, "5. Electronics, computing and sensors", f'''
<p class="lead">The Jetson Nano runs the walking controller; two Teensy 4.1 boards on a small carrier PCB talk to the actuators
over six CAN buses, 500 times a second, and handle the emergency stop. The IMU senses balance; the stereo camera gives
the robot depth vision.</p>
{table([("ID", ""), ("Item", ""), ("Specification", ""), ("Qty", "r"), ("Unit", "r"), ("Total", "r")], el_rows, "items",
       ["", "<b>Electronics, sensors, servos</b>", "", "", "", f"<b>{inr(e_tot)}</b>"])}
<h2>How the electronics connect</h2>
<div class="flow">
  <div class="fbox">Jetson Nano<br><small>walking policy · 50 Hz</small></div><div class="farrow">USB →</div>
  <div class="fbox">Hub A + Hub B<br><small>2 × Teensy 4.1 · 500 Hz</small></div><div class="farrow">6 × CAN →</div>
  <div class="fbox">21 actuators<br><small>48 V · encoders</small></div>
</div>
<div class="flow"><div class="fbox soft">IMU (pelvis) → Hub A · SPI</div><div class="fbox soft">Neck servos → Hub B · serial bus</div>
<div class="fbox soft">Stereo camera → Jetson · CSI</div><div class="fbox soft red">E-stop → both hubs + motor power</div></div>
<p class="note">Foot pressure sensors (line 019) are optional (phase 2). The hub PCB price is for 5 boards from Lion Circuits'
public calculator; one board is used.</p>'''))

    # 7 — power
    pw = ids("Battery and power distribution")
    pw_rows = item_rows(rows, pw)
    p_tot = sum(by_id[i]["total"] for i in pw)
    pages.append(page(7, "6. Battery and power system", f'''
<p class="lead">A 13S2P pack of 28 Samsung 21700 cells (48 V nominal, 468 Wh) feeds the actuators through an anti-spark switch
and 58 V-rated branch fuses; isolated and step-down supplies feed the computers and servos.</p>
{table([("ID", ""), ("Item", ""), ("Specification", ""), ("Qty", "r"), ("Unit", "r"), ("Total", "r")], pw_rows, "items",
       ["", "<b>Power system</b>", "", "", "", f"<b>{inr(p_tot)}</b>"])}
<div class="two">
  <div><h2>Battery at a glance</h2>{table([("", ""), ("", "r")], [
      ["Configuration", "13S2P, 28 × 21700 cells"], ["Voltage", "41.6–54.6 V"], ["Energy", "468 Wh"],
      ["BMS limit", "40 A continuous"], ["Walking 0.5 m/s", "≈ 283 W → ≈ 1.3 h"], ["Standing", "92–163 W → 2.3–4.1 h"]], "compact kv")}</div>
  <div><h2>Safety built in</h2><ul class="notes">
    <li>Emergency stop with two independent paths: it cuts the 48 V motor bus <i>and</i> puts every joint into damping.</li>
    <li>58 V-rated fuses on every branch (car fuses are rated 32 V and are not safe here).</li>
    <li>Smart BMS: over-charge, over-discharge and over-current protection, Bluetooth monitoring.</li>
    <li>XT90-S anti-spark service disconnect; pack built and capacity-tested by lionbattery.in.</li></ul></div>
</div>'''))

    # 8 — printing, optional items, savings, exclusions
    pr = ids("3D printing and consumables")
    pr_rows = item_rows(rows, pr)
    pr_tot = sum(by_id[i]["total"] for i in pr)
    sav_rows, sav_tot = [], 0
    for rid, what, trade in SAVINGS:
        if rid == "ACT":
            d = act_total - alt_total
        else:
            r = by_id[rid]
            d = (r["unit"] - r["alt"]) * r["qty"]
        sav_tot += d
        sav_rows.append([e(what), e(trade), f'<b>{inr(-d)}</b>'])
    gr = s["deferred"]
    pages.append(page(8, "7. 3D printing, consumables and optional items", f'''
{table([("ID", ""), ("Item", ""), ("Used for", ""), ("Qty", "r"), ("Unit", "r"), ("Total", "r")], pr_rows, "items",
       ["", "<b>Printing and consumables</b>", "", "", "", f"<b>{inr(pr_tot)}</b>"])}
<p class="note">Print PETG <b>fit-check copies</b> of every metal part first and bolt them to the real actuators before ordering metal.
Deferred to phase 3 (not in the total): {", ".join(f"{e(r['Part'].lower())} ({inr(r['total'])})" for r in gr)}.</p>
<h2>8. Ways to reduce the cost</h2>
{table([("Option", ""), ("Trade-off", ""), ("Change", "r")], sav_rows, "compact",
       ["<b>All options together</b>", f"budget build ≈ <b>{inr(total - sav_tot)}</b> (+ contingency {inr(round((total - sav_tot) * (1 + CONTINGENCY)))})", f"<b>{inr(-sav_tot)}</b>"])}
<p class="note">Upgrade path (not included): Jetson Orin Nano Super dev kit ({inr(by_id["JX1-023"]["alt"])}, +{inr(by_id["JX1-023"]["alt"] - by_id["JX1-023"]["unit"])})
for more computing power and native CAN.</p>
<h2>Not included in this estimate — budget separately</h2>
<div class="excl">
  <div>Hand tools: hex keys, torque screwdriver and wrench, taps, reamers, calipers</div>
  <div>Bench equipment: current-limited power supply, multimeter, soldering station</div>
  <div>Lifting gantry or chest harness for safe first power-on and walking tests</div>
  <div>Spares (e.g. one actuator of each size) and a second battery pack</div>
  <div>Job-shop setup charges above the estimate, customs-clearance fees, courier delays</div>
  <div>A laptop/PC with a GPU if new walking controllers are to be trained</div>
</div>'''))

    # 9 — complete list + grand total
    all_rows = []
    for r in rows:
        name = f'{e(short(r["Part"], 46))} <span class="sub">— {e(short(r["Exact model"], 44))}</span>'
        all_rows.append(([f'<span class="id">{r["ID"][4:]}</span>', e(r["Subsystem"]), name, str(r["qty"]), inr(r["unit"], False),
                          inr(r["total"], False) if r["in_total"] else f'({inr(r["total"], False)})'], "" if r["in_total"] else "muted"))
    pages.append(page(9, "9. Complete list of components and total cost", f'''
{table([("#", ""), ("Group", ""), ("Item — model", ""), ("Qty", "r"), ("Unit ₹", "r"), ("Total ₹", "r")], all_rows, "all")}
<div class="final">
  <div class="frow"><span>Robot total ({len([r for r in rows if r["in_total"]])} lines; deferred item in brackets not included)</span><b>{inr(total)}</b></div>
  <div class="frow"><span>Prototype contingency 15 %</span><b>{inr(cont)}</b></div>
  <div class="frow grand"><span>TOTAL ESTIMATED COST OF JX1</span><b>{inr(grand)}</b></div>
  <div class="inwords">Rupees {words(grand)} only</div>
</div>'''))
    return pages


CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: #e9ecf1; }
body { font-family: "Segoe UI", "Nirmala UI", sans-serif; color: #1c2430; font-size: 9pt; line-height: 1.38;
  -webkit-print-color-adjust: exact; print-color-adjust: exact; font-variant-numeric: tabular-nums; }
.page { width: 210mm; height: 297mm; position: relative; overflow: hidden; background: #ffffff; margin: 0 auto;
  break-after: page; page-break-after: always; padding: 17mm 14mm 14mm 14mm; }
.page:last-child { break-after: auto; page-break-after: auto; }
@media screen { .page { margin: 10mm auto; box-shadow: 0 2px 12px rgba(0,0,0,.15); } }
.phead { position: absolute; top: 7mm; left: 14mm; right: 14mm; display: flex; justify-content: space-between;
  font-size: 7.5pt; color: #6b7686; border-bottom: 0.6pt solid #d5dbe3; padding-bottom: 1.6mm; }
.phead b { color: #f26b1d; letter-spacing: .04em; }
.pfoot { position: absolute; bottom: 6mm; left: 14mm; right: 14mm; font-size: 6.8pt; color: #8a94a3;
  border-top: 0.6pt solid #e1e5eb; padding-top: 1.4mm; }
.content { height: 100%; overflow: hidden; }
h1 { font-family: "Bahnschrift", "Segoe UI", sans-serif; font-weight: 600; font-size: 19pt; color: #0f1622;
  letter-spacing: -.005em; margin: 1mm 0 3mm; }
h2 { font-family: "Bahnschrift", "Segoe UI", sans-serif; font-weight: 600; font-size: 11pt; color: #0f1622; margin: 4.2mm 0 1.8mm; }
.lead { font-size: 9.6pt; color: #2d3746; margin-bottom: 3mm; }
.note { font-size: 7.8pt; color: #566173; margin-top: 1.6mm; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; font-weight: 600; font-size: 7.3pt; color: #566173; text-transform: uppercase; letter-spacing: .03em;
  border-bottom: 1pt solid #0f1622; padding: 1.2mm 1.4mm; }
td { padding: 1.25mm 1.4mm; border-bottom: 0.5pt solid #e1e5eb; vertical-align: top; }
.r { text-align: right; white-space: nowrap; }
tfoot td { border-top: 1pt solid #0f1622; border-bottom: none; background: #f4f6f9; }
table.items td { font-size: 8pt; }
table.items td .spec { font-size: 7.4pt; }
table.compact td { font-size: 8pt; padding: 1.05mm 1.4mm; }
table.kv th { display: none; }
.id { font-family: Consolas, monospace; font-size: 7.5pt; color: #8a94a3; }
.sub { color: #6b7686; font-size: 7.3pt; }
.spec { color: #3b4656; font-size: 7.6pt; }
tr.muted td { color: #9aa3b0; }
tr.muted td b { color: #9aa3b0; }
.muted-t { color: #9aa3b0; }
.spec-t th { width: 27%; text-transform: none; letter-spacing: 0; font-size: 8pt; color: #0f1622; border-bottom: 0.5pt solid #e1e5eb;
  vertical-align: top; }
.spec-t td { font-size: 8pt; }
.imgcol { display: flex; align-items: flex-start; }
img.framed { width: 100%; border-radius: 2mm; display: block; }
img.tall { height: 96mm; object-fit: cover; object-position: 50% 38%; margin-top: 9mm; }
.imgrow img { height: 52mm; object-fit: cover; object-position: 50% 45%; margin-top: 3mm; }
ul.checks, ul.notes { list-style: none; }
ul.checks li, ul.notes li { position: relative; padding-left: 5mm; margin-bottom: 1.3mm; font-size: 8.2pt; }
ul.checks li.ok::before { content: "✓"; position: absolute; left: 0; color: #1a9a5c; font-weight: 700; }
ul.checks li.next::before { content: "→"; position: absolute; left: 0; color: #f26b1d; font-weight: 700; }
ul.checks li.next { font-weight: 600; }
ul.notes li::before { content: ""; position: absolute; left: 1mm; top: 1.9mm; width: 1.6mm; height: 1.6mm; background: #1f8fc9; border-radius: 50%; }
.cards { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 4mm; margin-bottom: 2mm; }
.card { border: 0.8pt solid #d5dbe3; border-radius: 2mm; padding: 3mm 3.5mm; }
.card span { display: block; font-size: 7.6pt; color: #566173; text-transform: uppercase; letter-spacing: .04em; }
.card b { display: block; font-family: "Bahnschrift", sans-serif; font-weight: 600; font-size: 19pt; color: #0f1622; margin: .6mm 0; }
.card em { font-style: normal; font-size: 7.5pt; color: #6b7686; }
.card.hi { background: #0f1622; border-color: #0f1622; }
.card.hi span, .card.hi em { color: #aab4c3; }
.card.hi b { color: #ffffff; }
.bars { margin-top: 1mm; }
.bar { display: grid; grid-template-columns: 50mm 1fr 21mm 13mm; align-items: center; gap: 2.5mm; margin: 1.3mm 0; font-size: 8.2pt; }
.btrack { height: 4.2mm; background: #eef1f5; border-radius: 1mm; overflow: hidden; }
.bfill { height: 100%; background: linear-gradient(90deg, #1f8fc9, #3cc8ff); border-radius: 1mm; }
.bar:first-child .bfill { background: linear-gradient(90deg, #f26b1d, #ff9a52); }
.bval { text-align: right; font-weight: 600; }
.bpct { text-align: right; color: #6b7686; }
.subtotal { display: flex; justify-content: space-between; margin-top: 3mm; padding: 2.4mm 3.5mm; background: #0f1622; color: #fff;
  border-radius: 1.6mm; font-size: 9.5pt; }
.subtotal b { font-family: "Bahnschrift", sans-serif; font-weight: 600; font-size: 12pt; }
.flow { display: flex; align-items: center; gap: 2.5mm; margin: 2mm 0; flex-wrap: wrap; }
.fbox { border: 0.8pt solid #1f8fc9; border-radius: 1.6mm; padding: 2mm 3mm; font-weight: 600; font-size: 8.4pt; text-align: center;
  background: #f1f8fc; }
.fbox small { font-weight: 400; color: #566173; }
.fbox.soft { border-color: #d5dbe3; background: #f7f8fa; font-weight: 400; font-size: 7.8pt; }
.fbox.red { border-color: #d64545; background: #fdf1f1; }
.farrow { color: #1f8fc9; font-weight: 600; font-size: 8pt; }
.strip { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 3mm; }
.strip img { width: 100%; height: 34mm; object-fit: cover; border-radius: 1.6mm; display: block; }
.strip figcaption { font-size: 7.2pt; color: #566173; margin-top: 1mm; }
.excl { display: grid; grid-template-columns: 1fr 1fr; gap: 1.6mm 5mm; }
.excl div { font-size: 7.9pt; padding-left: 4mm; position: relative; }
.excl div::before { content: "–"; position: absolute; left: 0; color: #f26b1d; font-weight: 700; }
table.all th { padding: .9mm 1.2mm; font-size: 6.6pt; }
table.all td { font-size: 6.9pt; padding: .28mm 1.2mm; line-height: 1.2; }
table.all td .sub { font-size: 6.5pt; }
.final { margin-top: 2mm; border: 1pt solid #0f1622; border-radius: 2mm; overflow: hidden; }
.frow { display: flex; justify-content: space-between; padding: 1.5mm 4mm; font-size: 8.8pt; border-bottom: 0.5pt solid #e1e5eb; }
.frow b { font-weight: 600; }
.frow.grand { background: #0f1622; color: #fff; font-family: "Bahnschrift", sans-serif; font-weight: 600; font-size: 12pt;
  letter-spacing: .02em; padding: 2.4mm 4mm; border-bottom: none; }
.frow.grand b { font-size: 15pt; color: #ffb27a; }
.inwords { padding: 1.5mm 4mm; font-size: 8pt; font-style: italic; color: #2d3746; background: #fff7f1; }
/* cover */
.page.cover { background: #0f1622; color: #e9edf3; padding: 0; }
.cover .content { position: relative; }
.cover-top { position: absolute; top: 18mm; left: 16mm; right: 16mm; z-index: 2; }
.kicker { font-size: 9pt; letter-spacing: .18em; text-transform: uppercase; color: #8fa0b6; }
.wordmark { font-family: "Bahnschrift", sans-serif; font-weight: 700; font-size: 104pt; line-height: .95; color: #ffffff;
  letter-spacing: -.01em; display: flex; align-items: center; gap: 5mm; margin-top: 3mm; }
.wordmark .dot { display: inline-block; width: 13mm; height: 13mm; background: #f26b1d; border-radius: 2mm; }
.tag { font-family: "Bahnschrift", sans-serif; font-weight: 400; font-size: 22pt; color: #3cc8ff; margin-top: 2mm; }
.cover-img { position: absolute; top: 66mm; left: 0; right: 0; height: 150mm; z-index: 1; }
.cover-img img { width: 100%; height: 100%; object-fit: cover; object-position: 50% 30%; display: block;
  -webkit-mask-image: linear-gradient(180deg, transparent 0%, #000 14%, #000 80%, transparent 100%); }
.cover-stats { position: absolute; top: 214mm; left: 16mm; right: 16mm; display: grid; grid-template-columns: repeat(5, 1fr);
  gap: 3mm; z-index: 2; }
.cover-stats div { border-left: 1.2pt solid #f26b1d; padding-left: 3mm; }
.cover-stats b { display: block; font-family: "Bahnschrift", sans-serif; font-weight: 600; font-size: 17pt; color: #fff; }
.cover-stats span { font-size: 8pt; color: #8fa0b6; text-transform: uppercase; letter-spacing: .06em; }
.cover-cost { position: absolute; top: 237mm; left: 16mm; right: 16mm; display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; z-index: 2; }
.cover-cost div { border: 0.8pt solid #2c3a4f; border-radius: 2mm; padding: 3.5mm 4mm; background: #141d2b; }
.cover-cost span { display: block; font-size: 8pt; color: #8fa0b6; text-transform: uppercase; letter-spacing: .06em; }
.cover-cost b { display: block; font-family: "Bahnschrift", sans-serif; font-weight: 600; font-size: 24pt; color: #fff; margin-top: 1mm; }
.cover-cost .grand { background: #f26b1d; border-color: #f26b1d; }
.cover-cost .grand span { color: #fff3ea; }
.cover-foot { position: absolute; bottom: 10mm; left: 16mm; right: 16mm; font-size: 7.6pt; color: #6f7f95; z-index: 2; }
"""

PREVIEW_JS = """
<script>
const q = new URLSearchParams(location.search);
if (q.has("p")) {
  document.querySelectorAll(".page").forEach(p => { if (p.id !== "p" + q.get("p")) p.style.display = "none"; else p.style.margin = "0"; });
  document.documentElement.style.background = "#fff"; document.body.style.background = "#fff";
}
if (q.has("check")) {
  const res = [...document.querySelectorAll(".page .content")].map((c, i) => {
    const last = [...c.children].pop(); const over = last ? (last.getBoundingClientRect().bottom - c.getBoundingClientRect().bottom) : 0;
    return `p${i + 1}:${Math.round(over)}`; });
  document.body.setAttribute("data-overflow", res.join(","));
}
</script>"""


def write_html(pages, path):
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>JX1 — component list and cost estimate</title>
<style>{CSS}</style></head><body>{"".join(pages)}{PREVIEW_JS}</body></html>"""
    path.write_text(doc, encoding="utf-8")


def edge(args, profile, wait_for=None):
    exe = [str(HEADLESS[-1])] if HEADLESS else [str(EDGE), "--headless=new"]
    if wait_for is not None and wait_for.exists():
        wait_for.unlink()
    cmd = exe + ["--disable-gpu", "--no-first-run", "--hide-scrollbars", f"--user-data-dir={profile}"] + args
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if wait_for is not None:                     # Edge: wait until the file exists and has stopped growing
        last, t0 = -1, time.time()
        while time.time() - t0 < 120:
            size = wait_for.stat().st_size if wait_for.exists() else -1
            if size > 0 and size == last:
                break
            last = size
            time.sleep(1.0)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    rows = load()
    s = summarise(rows)
    check_against_summary(s)
    pages = build(rows, s)
    assert len(pages) == N_PAGES
    BUILD.mkdir(parents=True, exist_ok=True)
    src = BUILD / "JX1_cost_estimate.html"
    write_html(pages, src)
    prof = BUILD / "edge_profile"            # Edge keeps files locked briefly after exit, so the profile is kept
    if True:
        # layout check: how far the last block of each page reaches past its content box (px; > 0 = overflow)
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
    print(f"wrote {OUT_PDF.relative_to(ROOT)}: {n_pages} pages, {len(pdf) / 1e6:.1f} MB; robot total {inr(s['total'])}, "
          f"with contingency {inr(s['grand'])}")
    assert n_pages == N_PAGES, f"expected {N_PAGES} pages, got {n_pages}"


if __name__ == "__main__":
    main()
