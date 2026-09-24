"""JX0 component list and cost estimate: a 4-page A4 PDF generated from jx0/bom/jx0_bom.csv.

Cover, what JX0 is and how far it has got, the cost summary, and the complete item list with the total. Styling, number
formatting and the headless-Chromium printing come from the JX1 report (bom/make_cost_report.py).

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
from make_cost_report import CSS, PREVIEW_JS, REPORT_DATE, bars, e, edge, inr, short, table, words  # noqa: E402

BOM = ROOT / "jx0" / "bom" / "jx0_bom.csv"
OUT_PDF = ROOT / "jx0" / "bom" / "JX0_cost_estimate.pdf"
BUILD = ROOT / "jx0" / "bom" / ".report_build"
N_PAGES = 4
BUDGET = 50_000
REPO = "github.com/nickthelegend/thenar-jx1/tree/main/jx0"


def uri(rel):
    return (ROOT / rel).resolve().as_uri()


def page(n, title, body, cls=""):
    head = "" if n == 1 else f'''<div class="phead"><span><b>JX0</b> · the under-₹50k walking, talking humanoid · component list and cost estimate</span><span>{n} / {N_PAGES}</span></div>'''
    foot = "" if n == 1 else f'''<div class="pfoot"><span>Prices in INR from Indian online stores, GST included where the store states it · checked {REPORT_DATE} · ESTIMATED lines need a quote</span></div>'''
    h = f"<h1>{title}</h1>" if title else ""
    return f'''<section class="page {cls}" id="p{n}">{head}<div class="content">{h}{body}</div>{foot}</section>'''


def load():
    rows = list(csv.DictReader(BOM.open(encoding="utf-8")))
    for r in rows:
        r["qty"], r["unit"], r["total"] = int(float(r["Qty"])), float(r["Unit INR"]), float(r["Total INR"])
        assert abs(r["qty"] * r["unit"] - r["total"]) < 0.05, r["ID"]
    return rows


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
  <div class="tag">walks · talks · shows a face · uses its hands</div>
</div>
<div class="cover-img"><img src="{uri('jx0/results/images/jx0_demo_take.png')}" alt="JX0 holding out its gripper hand (simulation of the CAD model)"></div>
<div class="cover-stats">
  <div><b>51.7 cm</b><span>height</span></div><div><b>2.07 kg</b><span>mass</span></div>
  <div><b>21</b><span>servos</span></div><div><b>23</b><span>printed parts</span></div><div><b>{len(rows)}</b><span>BOM lines</span></div>
</div>
<div class="cover-cost">
  <div><span>Parts for one robot</span><b>{inr(total)}</b></div>
  <div class="grand"><span>Under the ₹50,000 budget by</span><b>{inr(BUDGET - total)}</b></div>
</div>
<div class="cover-foot">{REPORT_DATE} · all figures from the JX0 bill of materials ({REPO})</div>
''', "cover"))

    # 2 - overview
    spec = [("Height / mass", "51.7 cm / 2.07 kg (CAD, all parts)"),
            ("Legs", "6 joints each: Feetech ST3215-C018 12 V serial bus servos (30 kg·cm stall, position feedback)"),
            ("Arms and hands", "shoulder pitch and roll, elbow and a three-finger gripper per arm: MG90S micro servos"),
            ("Head", "neck yaw, a 1.28-inch round screen as the face (eyes and a mouth that moves with speech), camera"),
            ("Brain", "Raspberry Pi 4: 50 Hz gait playback, IMU balance, offline speech recognition and voice"),
            ("Talking", "Claude over Wi-Fi writes the replies and calls the robot's actions (wave, walk, take, give)"),
            ("Power", "3S 2200 mAh LiPo, about 20-30 minutes of walking (ESTIMATED)"),
            ("Structure", "PETG on a home 3D printer: 23 parts, 379 g")]
    spec_html = "".join(f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in spec)
    pages.append(page(2, "1. What JX0 is", f'''
<p class="lead">JX0 is a small humanoid robot designed to be built by one student at home, from a 3D printer and parts
that can be ordered online in India. It is the working prototype of the JX1 project: it uses the same design pipeline
(gait planner, servo sizing, physics simulation) at a price a student can afford.</p>
<div class="two">
  <div><h2>Specification</h2><table class="spec-t">{spec_html}</table></div>
  <div class="imgcol"><img src="{uri('jx0/cad/images/jx0_cad_front.png')}" class="framed tall" alt="JX0 in SolidWorks"></div>
</div>
<div class="two">
  <div><h2>Done (on the computer)</h2><ul class="checks">
    <li class="ok">SolidWorks CAD: 23 printable parts, 46-component assembly, built by script</li>
    <li class="ok">Servo sizing for every leg joint: all pass (tightest margin 1.89×)</li>
    <li class="ok">Walking in a physics simulation of the CAD robot: 14 of 14 gaits pass</li>
    <li class="ok">Robot program (voice, Claude, face, walking, hands) runs on the simulated robot</li>
    <li class="next">Next: buy the parts → print → assemble → first steps</li></ul></div>
  <div><h2>How this estimate was made</h2><ul class="notes">
    <li>Every line is a real product page at an Indian store (Robu, Evelta, Robocraze, ThinkRobotics, Quartz
      Components and others), price checked {REPORT_DATE}.</li>
    <li>GST is included where the store states it; shipping is not included.</li>
    <li>Two small lines (button, jumper wires) are ESTIMATED.</li></ul></div>
</div>
<h2>From CAD to a working robot</h2>
<div class="strip">
  <figure><img src="{uri('jx0/cad/images/jx0_cad_back.png')}" alt="SolidWorks back view"><figcaption>SolidWorks assembly, back view</figcaption></figure>
  <figure><img src="{uri('jx0/results/images/jx0_demo_wave.png')}" alt="waving"><figcaption>waving (simulation, the robot's own program)</figcaption></figure>
  <figure><img src="{uri('jx0/results/images/walk_forward_mid.png')}" alt="walking"><figcaption>walking at 0.067 m/s (simulation)</figcaption></figure>
</div>'''))

    # 3 - cost summary
    grp_note = {"Servos": "12 × ST3215 leg servos, 9 × MG90S", "Electronics": "Raspberry Pi 4, microSD, servo driver, wiring",
                "Power": "LiPo, charger, converters, switch, alarm", "Structure": "PETG filament, screws, inserts, foot rubber",
                "Face": "round display, camera", "Voice": "microphone, amplifier, speaker", "Sensors": "IMU"}
    grp_rows = [[e(k), e(grp_note.get(k, "")), f'<span class="r">{inr(v)}</span>', f'<span class="r">{100 * v / total:.1f} %</span>']
                for k, v in by_group.items()]
    top = sorted(rows, key=lambda r: -r["total"])[:5]
    top_rows = [[e(r["Item"]), e(short(r["Model"], 60)), str(r["qty"]), f'<span class="r"><b>{inr(r["total"])}</b></span>'] for r in top]
    pages.append(page(3, "2. Cost summary", f'''
<div class="cards">
  <div class="card"><span>Parts total</span><b>{inr(total)}</b><em>{len(rows)} line items, one robot</em></div>
  <div class="card"><span>Leg servos</span><b>{100 * rows[0]["total"] / total:.0f} %</b><em>of the cost: 12 × ST3215 at {inr(rows[0]["unit"])}</em></div>
  <div class="card hi"><span>Left in a ₹50k budget</span><b>{inr(BUDGET - total)}</b><em>for shipping and spares</em></div>
</div>
<h2>By group</h2>
{bars(by_group, total)}
<h2>Groups</h2>
{table([("Group", ""), ("What", ""), ("₹", "r"), ("Share", "r")], grp_rows, "compact",
       foot=["<b>Total</b>", "", f'<span class="r"><b>{inr(total)}</b></span>', '<span class="r">100 %</span>'])}
<h2>Five biggest lines</h2>
{table([("Item", ""), ("Model", ""), ("Qty", "r"), ("₹", "r")], top_rows, "compact")}
<p class="note">Why these leg servos: the walking needs up to 1.56 N·m at the hip (with a 1.5× safety margin), which is
more than MG996R-class hobby servos give. The serial bus servos also report their position, which the calibration and
the balance loop use.</p>'''))

    # 4 - complete list
    item_rows = [[f'<span class="id">{e(r["ID"][4:])}</span>', f'<b>{e(r["Item"])}</b><br><span class="sub">{e(short(r["Model"], 70))}</span>',
                  f'<span class="sub">{e(r["Store"])}</span>', str(r["qty"]), f'<span class="r">{inr(r["unit"])}</span>',
                  f'<span class="r"><b>{inr(r["total"])}</b></span>'] for r in rows]
    pages.append(page(4, "3. Complete list of items", f'''
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
    pages, total = build(rows)
    assert len(pages) == N_PAGES
    BUILD.mkdir(parents=True, exist_ok=True)
    src = BUILD / "JX0_cost_estimate.html"
    src.write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>JX0 — component list and cost estimate</title>
<style>{CSS}</style></head><body>{"".join(pages)}{PREVIEW_JS}</body></html>""", encoding="utf-8")
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
