"""Build 'Robot actuators as a business in India' (A4 PDF): market to 2030/2035, copper, software vs hardware, the
Indian actuator landscape, how actuator factories are built (with the equations), capital needed, valuation reality
check and a go-to-market plan. Numbers come from business/results/business_model.json, actuators/inhouse/results/
cost.json and the research logs in research/raw/ (labels VERIFIED / ESTIMATED / UNVERIFIED are kept there).
Usage: python business/make_business_report.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "actuators" / "inhouse"))
from make_paper import CSS, CHROME, inr, lakh, table  # noqa: E402  (shared look and helpers)

FIG = HERE / "figures"
BUILD = HERE / ".report_build"
OUT_PDF = HERE / "Actuator_business_report_India.pdf"
DATE = "6 October 2026"
B = json.loads((HERE / "results" / "business_model.json").read_text())
C = json.loads((ROOT / "actuators" / "inhouse" / "results" / "cost.json").read_text())


def cr(x):
    return f"₹{x / 1e7:,.1f} cr"


def fig(name, caption, width="100%"):
    return f'<figure><img src="{(FIG / name).as_uri()}" style="width:{width}"><figcaption>{caption}</figcaption></figure>'


def answers():
    one = B["mc_check"]["one_percent_of_2030_market"]
    return f"""
<h2 id="answers">1. Your questions, answered straight</h2>
<table class="small">
<tr><th style="width:24%">Question</th><th>Short answer</th></tr>
<tr><td><b>Is an actuator company a good business?</b></td><td>It is a <b>real and growing</b> business: every robot needs 20–40 actuators and
banks put the humanoid-actuator market at ≈ US$8–14 bn in 2030 (from ≈ US$0.23 bn in 2025). But it is a <b>hard, low-margin manufacturing
business against very strong Chinese incumbents</b> (RobStride, Encos, Unitree make 50k–500k joints a year at ≈ ¥1,000 each). It is a good business
for India only if you pick buyers who will not or cannot buy Chinese, and if you scale slowly with customer money, not hype.</td></tr>
<tr><td><b>"1 % of a trillion dollars = US$10 bn"?</b></td><td>The trillion-dollar numbers are the <i>whole robot market in 2050</i> (Morgan Stanley US$5 trn,
Citi US$7 trn), not something you can take 1 % of today. 1 % of the 2030 humanoid-actuator market is ≈ US${one['revenue_usd'] / 1e6:,.0f} M of revenue a year,
worth ≈ US${one['market_cap_at_4x_usd'] / 1e6:,.0f} M at a typical 4× sales. A US$10 bn company needs ≈ US$2.5 bn of revenue: about a quarter of the
entire 2030 market, or 10 million actuators a year. Possible only in a 2035+ world, and only for a top-3 global supplier.</td></tr>
<tr><td><b>Will copper prices go up because of robots?</b></td><td>Copper probably will stay strong (S&amp;P sees a 25 % supply gap by 2040) <b>but not because of robots</b>.
A humanoid holds ≈ 6–8 kg of copper (≈ US$115, &lt; 1 % of its cost). Even bullish forecasts make humanoids 0.02–0.08 % of world copper demand in 2030 and
&lt; 0.35 % in 2035. Grids, EVs (83 kg each) and AI data centres (20–40 t per MW) drive copper. For an actuator maker copper is a small cost, not a lever.</td></tr>
<tr><td><b>2030: will coding stay, or will robot manufacturing win?</b></td><td>Both stay, but differently. AI is already shrinking <i>entry-level</i> coding jobs
(US developers aged 22–25 down ≈ 20 % since 2024, Stanford AI Index 2026) while total software jobs still grow (BLS +15.8 % to 2034). Physical manufacturing
know-how is much less exposed. The strongest position is <b>both</b>: a CS person who understands motors, control and factories. In actuators the
differentiator is increasingly software: FOC firmware, calibration, digital-twin models and fleet data.</td></tr>
<tr><td><b>Should we make actuators instead of whole robots?</b></td><td>Yes, this is the right instinct ("sell shovels in a gold rush"): every Indian robot maker
needs actuators, all of them import today, and a component supplier is not betting on which robot company wins. Start as the <b>Indian actuator
supplier + integrator</b>, not as another humanoid startup.</td></tr>
</table>
"""


def market():
    return """
<h2 id="market">2. The robot market to 2030–2035</h2>
<p>Humanoids went from a few hundred units in 2023 to ≈ 13,000–20,000 in 2025 (Omdia; BofA), almost all made in China (AgiBot ≈ 5,200, Unitree
≈ 4,200–5,500, UBTech ≈ 1,100). Unitree's 2025 revenue was ¥1.7 bn at a 60 % gross margin; its humanoid price fell 72 % in two years to ≈ US$25k.
Tesla says meaningful Optimus volume comes in 2027.</p>
<table class="small">
<tr><th>Forecast (label)</th><th>2030</th><th>2035</th><th>Long run</th></tr>
<tr><td>BofA Institute, Mar 2026 (VERIFIED)</td><td>1.2 M humanoids / yr; BOM &lt; US$17k</td><td>10 M / yr</td><td>3 bn in use by 2060</td></tr>
<tr><td>Goldman Sachs, Sep 2026 (press)</td><td>0.89 M units</td><td>6.5 M units, US$138 bn</td><td>–</td></tr>
<tr><td>Morgan Stanley (press)</td><td>US$28 bn; China 446k units</td><td>13 M in use</td><td>≈ 1 bn units, US$5 trn by 2050</td></tr>
<tr><td>UBS (press)</td><td>–</td><td>2 M in use, US$30–50 bn</td><td>300 M by 2050</td></tr>
<tr><td>Citi GPS, Nov 2024 (VERIFIED)</td><td>–</td><td>–</td><td>648 M units, US$7 trn by 2050</td></tr>
</table>
<p class="caption">Table 1. Humanoid forecasts (<code>research/raw/market_outlook_2030_copper_raw.md</code>). 2035 estimates differ by ≈ 5×; all banks raised them in the last year.</p>
<p><b>The actuator slice.</b> In BofA's 2030 bill of materials, rotary + linear actuators are 51 % of a humanoid (hands another 19 %). That gives an
actuator market of ≈ <b>US$0.23 bn in 2025, US$8–14 bn in 2030 and US$10–90 bn in 2035</b> depending on the bank (ESTIMATED).</p>
<p><b>Industrial robots</b> are the steadier market: &gt; 600k installed worldwide in 2025 (IFR, VERIFIED), 806k forecast for 2029. China installed 354k;
<b>India ≈ 9–10.5k (6th in the world)</b>, i.e. roughly 55,000 servo joints a year, <b>all imported</b>. India's domestic humanoid demand to 2030 is
likely only thousands of units (Addverb targets 3,000 installs; MeitY announced a ₹500 cr humanoid fund in June 2026). An Indian actuator company therefore
needs <b>export customers and non-humanoid volume</b> (AMRs, cobots, exoskeletons, defence UGVs, servo replacement) from day one.</p>
"""


def copper():
    return """
<h2 id="copper">3. Copper: a good bet, but not because of robots</h2>
<table class="small">
<tr><th>Item</th><th>Value</th><th>Source / label</th></tr>
<tr><td>World refined copper demand</td><td>≈ 28 Mt (2025) → ≈ 32 Mt (2030) → 42 Mt (2040)</td><td>S&amp;P Global, Jan 2026 (VERIFIED); 2030 interpolated</td></tr>
<tr><td>Supply gap</td><td>supply peaks ≈ 33 Mt in 2030; ≈ 10 Mt (25 %) short by 2040</td><td>S&amp;P (VERIFIED); JPMorgan ≈ 2 Mt deficit 2030 (press)</td></tr>
<tr><td>Near term</td><td>ICSG forecasts small surpluses in 2026–27</td><td>ICSG (press)</td></tr>
<tr><td>Price</td><td>≈ US$14,500/t (Oct 2026, +30 % y/y, near record)</td><td>COMEX (VERIFIED)</td></tr>
<tr><td>Copper per battery EV / data centre</td><td>83 kg per BEV; 20–40 t per MW</td><td>ICA/IDTechEx; JPMorgan</td></tr>
<tr><td>Copper per humanoid</td><td>≈ 6–8 kg (windings 2–7 kg, harness, PCBs, battery)</td><td>ESTIMATED; CRU 4–8 kg, MS 4.5–8.5 kg</td></tr>
<tr><td>Copper in one JXA-120</td><td>≈ 0.1 kg of winding wire (≈ ₹250 at bulk prices)</td><td>our design model</td></tr>
<tr><td>Humanoids' share of copper demand</td><td>0.02–0.08 % (2030); 0.14–0.33 % (2035); ≈ 4 % only with 1 bn robots (2040+)</td><td>ESTIMATED</td></tr>
</table>
<p><b>Bottom line:</b> copper is the right metal to understand (it is the winding), but owning copper is an investment decision, unrelated to whether an actuator
company works. For your actuators, a 30 % rise in copper adds ≈ ₹75 to a JXA-120; a change in magnet export rules can stop production entirely. <b>Worry about magnets,
not copper.</b></p>
"""


def software():
    return """
<h2 id="software">4. Software vs hardware in 2030: what the evidence says</h2>
<ul>
<li><b>Entry-level coding is being squeezed.</b> US software developers aged 22–25: employment down ≈ 20 % since 2024, older developers +6–12 % (Stanford AI Index 2026).
Brynjolfsson et al. (2026) find young workers in AI-exposed jobs 19 % below trend, through less hiring rather than layoffs.</li>
<li><b>Software as a whole still grows.</b> BLS projects software developers +15.8 % over 2024–34 but "computer programmers" −6 %: writing code is commoditising;
designing systems is not.</li>
<li><b>Robots replace physical work slowly.</b> WEF 2025 expects robotics/automation to be a small net job reducer (≈ −5 M jobs globally); each extra robot per 1,000
workers lowers employment by 0.2 points (Acemoglu &amp; Restrepo).</li>
<li><b>What that means for you:</b> an actuator is ≈ 50 % mechanics and magnetics and ≈ 50 % software (FOC, encoder calibration, thermal models, CAN protocol, test
automation, simulation models for reinforcement learning). Your CS background is an advantage. The skills AI will not quickly replace are the physical ones:
winding, gear quality, supplier management, factory process. Learn those; let AI help write the code.</li>
</ul>
"""


def landscape():
    rows = [
        ["xTerra Robotics (Kanpur/Bengaluru)", "QDD A2: 12 N·m, 550 g, <b>₹94,400</b>", "Parts machined by Bengaluru aerospace job shops, assembled in-house", "≈ 15 people, ≈ ₹1 cr revenue, grants only", "Mixed"],
        ["Bhairav Robotics (Kakinada)", "'Prabal' QDD, quadrupeds, UGVs", "In-house", "Zen Technologies bought 45 % for ≈ ₹4 cr", "UNVERIFIED"],
        ["Perceptyne (Hyderabad)", "Dual-arm semi-humanoid, own actuators", "In-house", "US$3 M seed (Endiya, Yali), 2024", "UNVERIFIED"],
        ["Addverb (Noida; Reliance)", "Elixis-W wheeled humanoid ≈ US$45k; 'BLDC + planetary'", "Undisclosed (likely imported joints)", "FY25 revenue ₹800 cr; plant ≈ ₹75 cr for 60k robots/yr", "Mixed"],
        ["General Autonomy (Bengaluru)", "Atom 01 humanoid, Param quadruped", "Imports actuators", "Seed ₹32 cr at ₹280 cr valuation (pre-revenue)", "UNVERIFIED"],
        ["Havells CRI", "Hiring to build harmonic + QDD actuators", "Starting", "–", "UNVERIFIED"],
        ["Vector Technics (Hyderabad)", "Drone propulsion motors", "Winds own motors, machines own parts; 300k units/yr", "Zen paid ≈ ₹25 cr for 51 %", "VERIFIED"],
        ["Sona Comstar / Lucas TVS / Chara", "EV traction and hub motors", "Automated winding + stamping lines", "Sona ₹99.7 cr for 200k motors/yr; Chara ₹52 cr Series A", "Mixed"],
        ["Atomberg / fan makers; Pitti Engineering", "BLDC fan motors; laminations (Pitti 90k t/yr)", "Mass stamping and winding", "Atomberg 6.6 M units/yr", "Mixed"],
        ["Yaskawa India (Bengaluru)", "Industrial servos", "Only confirmed local servo production", "–", "UNVERIFIED"],
    ]
    return f"""
<h2 id="landscape">5. Who makes actuators in India today</h2>
<p>Short version: <b>nobody makes RobStride-class actuators in India at volume.</b> A handful of startups build quasi-direct-drive joints by hand in tens to
hundreds; everyone else imports. No Indian harmonic-reducer maker was found. Meanwhile India <i>does</i> have the building blocks at scale in neighbouring
industries: drone motors (Vector: 300k/yr, own winding), EV motors (Sona, Lucas TVS, Chara), BLDC fans (Atomberg: millions/yr) and laminations (Pitti).</p>
{table(["Company", "Product", "How they make it", "Scale / money", "Label"], rows)}
<p class="caption">Table 2. Indian actuator and motor landscape (<code>research/raw/india_robotics_industry_capital_raw.md</code>). Funding figures are mostly from press summaries.</p>
<p><b>Indian manufacturing clusters you would use:</b> Coimbatore (motors, pumps, micro winding units), Rajkot (CNC, shafts, winders), Pune/Chakan (gears,
auto parts), Bengaluru Peenya (aerospace-grade CNC), Hyderabad (drone motors, laminations, defence), Chennai–Hosur (Bonfiglioli, Delta, Sona, Agile Robots'
₹300 cr plant). Contract manufacturers: Zetwerk (≈ 7,000 suppliers) for machined parts; EMS firms (Kaynes, Syrma, SFO, Dixon) for driver boards.</p>
"""


def factory():
    a = B["assumptions"]
    lines_per = a["shift_seconds_per_year"] * a["oee"] / a["takt_s"]
    return f"""
<h2 id="factory">6. How an actuator factory is built (and the equations behind it)</h2>
<h3>6.1 Three architectures</h3>
<table class="small">
<tr><th>Architecture</th><th>What you do in-house</th><th>What you buy</th><th>Volume</th><th>Capex</th><th>Who does this</th></tr>
<tr><td><b>A. Design + assembly house</b></td><td>design, winding, assembly, calibration, test, firmware</td><td>stator cores, magnets, gears, housings, bearings, PCBs (all job work)</td>
<td>100–3,000 / yr</td><td>{lakh(C['nre']['P']['total'] + C['nre']['B']['total'])} (our garage + workshop kits)</td><td>xTerra, Unitree (still mostly manual assembly)</td></tr>
<tr><td><b>B. Partly integrated</b></td><td>+ automated needle winding, magnet bonding, gear finishing, end-of-line test</td><td>laminations, magnets, castings, bearings, PCBs</td>
<td>3k–30k / yr</td><td>₹1–3 cr for 10k/yr (ESTIMATED)</td><td>RobStride-type start, Indian EV-motor lines</td></tr>
<tr><td><b>C. Volume plant</b></td><td>+ stamping, die-casting, gear hobbing/PM, automated lines, own driver SMT</td><td>magnets, bearings, chips</td>
<td>50k–1 M / yr</td><td>₹20–100+ cr; China: ¥110 M for one joint-module line (Fulin)</td><td>Encos, Quanzhibo (90 s per joint, &gt; 85 % automated)</td></tr>
</table>
<h3>6.2 The process flow of an actuator line</h3>
<p>Incoming inspection → lamination stack (stamp or buy) → insulate → <b>wind</b> (needle winder) → terminate → hipot/resistance test → varnish + cure →
rotor (bond magnets, balance) → gear stage (finish, inspect, grease) → housing (cast + machine) → <b>final assembly</b> (stator, rotor, gears, bearing,
driver PCB) → flash firmware, calibrate encoders → <b>end-of-line test</b> (back-EMF, K<sub>t</sub>, cogging, thermal, backlash) → burn-in → pack.
Chinese benchmarks: 90 s per joint, &gt; 96 % first-pass yield.</p>
<h3>6.3 The equations you plan with</h3>
<div class="eq">Gross margin: GM = (P − C) / P &nbsp;&nbsp;&nbsp; Break-even volume: N* = F / (P − V)</div>
<div class="eq">Learning curve (Wright): C(N) = C<sub>1</sub> · N<sup>log₂ r</sup> &nbsp;&nbsp; (r = cost ratio per doubling; our model ≈ {B['learning_rate_per_doubling']:.2f} between 25 and 1,000 units/yr)</div>
<div class="eq">Takt time = available time / demand &nbsp;&nbsp;&nbsp; Line capacity = available seconds × OEE / takt</div>
<div class="eq">Working capital = COGS/365 × (inventory days + receivable days − payable days)</div>
<div class="eq">Capital to raise = capex + operating losses until cash-positive + working capital + ≈ 6 months of opex</div>
<div class="eq">Market cap = revenue × (EV/sales multiple) &nbsp;&nbsp; revenue = robots/yr × actuators per robot × your share × price</div>
<p>Worked example: one line at a 90 s takt, 2 shifts × 300 days and 65 % OEE makes ≈ {lines_per:,.0f} actuators a year. So capacity is not the
problem; <b>demand, cost and quality are</b>. Working capital is large in this business because magnets and bearings are imported with 2–4 month lead
times: we assume {a['inventory_days']} inventory days, {a['receivable_days']} receivable days, {a['payable_days']} payable days.</p>
{fig("learning_curve.png", "Figure 1. Our JXA-120 cost vs yearly volume (ESTIMATED): cost falls steeply until ≈ 1,000/yr (job shops → own tooling), then cannot fall below RobStride's own cost because magnets, bearings and chips cost everyone the same.", "86%")}
"""


def capital():
    rows = []
    for s in B["stages"]:
        rows.append([f"<b>{s['name']}</b><br><span class='muted'>{s['buyers']}</span>", f"{s['months']} mo", f"{s['units']:,}",
                     inr(s['asp']) if s['asp'] else "–", inr(s['unit_cost']),
                     f"{s['gross_margin'] * 100:.0f} %" if s['gross_margin'] is not None else "–",
                     cr(s['revenue_per_yr']), cr(s['opex_per_yr']), cr(s['ebitda_per_yr']), cr(s['capex']), f"<b>{cr(s['capital_to_raise'])}</b>"])
    t = table(["Stage", "Time", "Units/yr", "Price", "Unit cost", "GM", "Revenue/yr", "Opex/yr", "EBITDA/yr", "Capex", "Raise"], rows)
    s3 = B["stages"][3]
    gm_war = (15000 - s3["unit_cost"]) / 15000
    schemes = table(["Source of money", "How much", "Fit"], [
        ["Your savings / bootstrap", "₹10–35 lakh", "Stage 0: garage kit + first prototypes (this repo's numbers)"],
        ["Startup India Seed Fund (via incubator)", "≤ ₹20 lakh grant + ≤ ₹50 lakh debt", "Stage 0–1, company ≤ 2 years old"],
        ["Incubators: ARTPARK (IISc), IIT hubs (DST NM-ICPS ₹3,660 cr)", "grants, labs, customers", "xTerra and Twara came from here"],
        ["State: Karnataka ELEVATE, TANSEED", "≤ ₹50 lakh / ₹10–15 lakh", "Stage 1"],
        ["Defence: iDEX / ADITI", "≤ ₹1.5 cr / ≤ ₹25 cr grants", "strong fit: UGV, exoskeleton, robot joints with no Chinese supply"],
        ["MeitY humanoid fund (announced Jun 2026)", "₹500 cr total", "R&amp;D and indigenous manufacturing (UNVERIFIED details)"],
        ["Seed VC: Yali, Speciale, Endiya, pi Ventures, Kalaari, Exfinity, Blume", "US$2–3.5 M typical", "Stage 1"],
        ["Series A/B VC: Peak XV, Elevation, Info Edge, Capital-A, TDK Ventures", "US$5–10 M / US$20–30 M", "Stage 2–3"],
        ["Strategic investors: Zen (bought Vector, Bhairav), Reliance (Addverb), Zoho", "acquisition or minority stake", "an exit path"],
        ["Debt: SIDBI venture debt, credit guarantee (≤ ₹20 cr), RDI scheme loans", "₹10–15 cr; RDI for large projects (paused Oct 2026)", "Stage 2–3 capex"],
        ["ECMS component scheme (₹40,000 cr)", "25 % capex support above ₹10–50 cr investment", "Stage 3; ask MeitY whether robot joints qualify"],
    ])
    return f"""
<h2 id="capital">7. How much capital, when, and from whom</h2>
<p>The plan below grows from a garage to a 60,000-a-year plant in four stages. It uses our own cost model and conservative assumptions (prices fall as
volume rises; cost never falls below RobStride's estimated own cost). Total external capital across all stages: <b>≈ {cr(B['total_capital_all_stages'])}</b>
(≈ US${B['total_capital_all_stages'] / C['assumptions']['INR_USD'] / 1e6:.0f} M).</p>
{t}
<p class="caption">Table 3. Staged plan (<code>business/actuator_business_model.py</code>; ESTIMATED). Units are JXA-120 equivalents. "Raise" = capex + losses during
the stage + working capital + 6 months of opex.</p>
{fig("capital_plan.png", "Figure 2. Capital to raise per stage vs revenue per year reached at the end of the stage (₹ crore, log scale).", "82%")}
<ul>
<li><b>Stage 1 is nearly break-even</b> only because Indian labs and defence buyers pay ≈ ₹42k for a 120 N·m joint (still less than half a CubeMars AK10-9's
₹1.05 lakh in India). It needs ≈ {B['stages'][1]['breakeven_units'] or 0:,.0f} units a year to break even.</li>
<li><b>The danger is Stage 3</b>: competing at ₹21k per unit leaves a {s3['gross_margin'] * 100:.0f} % gross margin. If Chinese makers cut prices so that you must
sell at ₹15k, the margin falls to <b>{gm_war * 100:.0f} %</b>. Do not build a volume plant without signed volume contracts.</li>
<li>At the end of Stage 3 the company makes ≈ {cr(s3['revenue_per_yr'])} (≈ US${s3['revenue_per_yr'] / C['assumptions']['INR_USD'] / 1e6:.0f} M) a year.
At 2–4× sales that is worth ≈ US${2 * s3['revenue_per_yr'] / C['assumptions']['INR_USD'] / 1e6:.0f}–{4 * s3['revenue_per_yr'] / C['assumptions']['INR_USD'] / 1e6:.0f} M:
a good company, not yet a unicorn.</li>
</ul>
<h3>7.1 Where the money comes from</h3>
{schemes}
<p class="caption">Table 4. Capital sources (<code>india_robotics_industry_capital_raw.md</code>; check official guidelines before applying). Indian robotics startups raised only
US$52.9 M in all of 2025 (≈ 0.5 % of Indian tech VC; the US raised US$5.6 bn), so plan for <b>small rounds and customer revenue</b>.</p>
"""


def valuation():
    rows = [["Harmonic Drive (JP)", "3.96", "10×"], ["Nabtesco (JP)", "3.7", "1.9×"], ["Leaderdrive (CN, harmonic reducers)", "7.5", "75×"],
            ["Sanhua (CN)", "21.3", "4.5×"], ["Tuopu (CN)", "12.0", "2.6×"], ["Inovance (CN, servos)", "20.9", "2.9×"],
            ["Zhaowei (CN, micro-drives)", "2.6", "10×"], ["Regal Rexnord / Kollmorgen (US)", "10.7", "1.8×"], ["Schaeffler (DE)", "≈ 6.9", "0.25×"],
            ["Unitree (CN, listed Aug 2026)", "≈ 27", "88×"], ["UBTech (HK)", "4.8", "12×"]]
    mc = B["mc_check"]["for_10bn_market_cap"]
    need = table(["EV / sales multiple", "Revenue needed for US$10 bn", "Actuators / yr at US$250", "Share of 2030 market", "Share of 2035 market (high case)"],
                 [[f"{m['ev_to_sales']}×", f"US${m['revenue_needed_usd'] / 1e9:.1f} bn", f"{m['actuators_per_year_at_usd250'] / 1e6:.0f} M",
                   f"{list(m['share_needed'].values())[0] * 100:.0f} %", f"{list(m['share_needed'].values())[2] * 100:.1f} %"] for m in mc])
    return f"""
<h2 id="valuation">8. Valuation reality check</h2>
{table(["Listed company", "Market cap, US$ bn", "Price / sales"], rows)}
<p class="caption">Table 5. Component makers' valuations (stockanalysis.com, 5–6 Oct 2026). Mature makers trade at 0.3–3.5× sales; "humanoid" names at 4.5–10×;
pure plays at 75–88× look like a bubble (Unitree opened +629 % and has since fallen ≈ 59 %).</p>
{need}
<p class="caption">Table 6. What a US$10 bn actuator company needs (ESTIMATED).</p>
<p>Private humanoid makers are valued far higher (Figure ≈ US$39 bn, Apptronik US$5.5 bn) on expectations, not revenue. A component supplier is valued on
revenue and margin. The path to a large outcome is therefore <b>volume + share in a market that is ≈ 10× bigger in 2035 than in 2030</b>, which means being
one of the few qualified non-Chinese suppliers when Western and Indian OEMs reach volume.</p>
"""


def gtm():
    s = B["stages"]
    return f"""
<h2 id="gtm">9. Go-to-market strategy</h2>
<h3>9.1 Positioning</h3>
<p><b>"India's actuator company: RobStride-class joints, made and supported in India, with a supply chain that does not depend on Chinese finished
goods."</b> You cannot win on price against ¥1,000 Chinese joints. You can win on what Chinese suppliers cannot offer some buyers:</p>
<ul>
<li><b>Trust and compliance:</b> defence, government labs and Western buyers who must avoid Chinese robots or components.</li>
<li><b>Local support:</b> stock in India, a 2-day replacement, Indian invoices with GST credit, engineers who answer the phone.</li>
<li><b>Customisation:</b> custom ratios, shafts, mounting, IP rating, 72 V windings, bigger sizes (the 360 N·m class nobody sells cheaply).</li>
<li><b>Software:</b> RobStride-compatible CAN protocol (drop-in), a ready ROS 2 driver, accurate MuJoCo/Isaac actuator models for RL.</li>
</ul>
<h3>9.2 Beachhead customers (in order)</h3>
<ol>
<li><b>Indian university and research labs</b> (IITs, IISc, IIITs, ARTPARK): they pay ₹34k–1.05 lakh per imported joint today and need GST invoices and fast service.</li>
<li><b>Indian robotics startups</b> (quadrupeds, humanoids, cobots, exoskeletons: Perceptyne, General Autonomy, Svaya, Bhairav, Addverb's suppliers):
every one of them imports joints.</li>
<li><b>Defence</b> (iDEX challenges, DRDO labs, Zen-type integrators): UGVs, exoskeletons, gimbals, robotic arms: no-China supply is worth a premium.</li>
<li><b>Export</b>: Western startups that want a non-China second source.</li>
<li><b>Industrial servo replacement</b> (≈ 55k joints/yr imported in India): later, with certifications.</li>
</ol>
<h3>9.3 Product and revenue sequence</h3>
<table class="small">
<tr><th>Months</th><th>What you sell</th><th>Why</th><th>Milestone</th></tr>
<tr><td>0–6</td><td><b>Integration + resale</b>: RobStride/Damiao joints with an Indian-built CAN interface board, ROS 2 driver, sim models, and an India stock + warranty</td>
<td>Earns cash and customer relationships immediately while your own actuator is developed</td><td>10 paying customers; JXA-120 v1 on the dyno</td></tr>
<tr><td>6–18</td><td><b>JXA-120 and JXA-40</b>, hand-assembled (architecture A), sold to labs and startups; first iDEX application</td>
<td>Learn quality on low volumes with forgiving customers</td><td>{s[1]['units']:,} units/yr run-rate; 200 h life data; seed round</td></tr>
<tr><td>18–36</td><td><b>JXA-360</b> + a 72 V line; die-cast housings, own driver PCB; first export customers</td>
<td>The big joint has no cheap competitor; export lifts price</td><td>{s[2]['units']:,} units/yr; ISO 9001; Series A</td></tr>
<tr><td>36+</td><td>Volume contracts with humanoid OEMs; automated winding and EOL test; second source for magnets (Indian REPM plants)</td>
<td>Scale only against signed demand</td><td>{s[3]['units']:,} units/yr; Series B or strategic partner</td></tr>
</table>
<h3>9.4 Metrics to watch and kill criteria</h3>
<ul>
<li>Gross margin per unit ≥ 35 % after Stage 1; field failure rate &lt; 1 %/yr; repeat orders from ≥ 50 % of customers.</li>
<li>Kill or pivot criteria: if after 18 months fewer than 5 customers re-order, or if JXA-120 cannot reach ≤ ₹20k cost at 600/yr, switch to being an
integrator/distributor + software company (still a business) instead of a manufacturer.</li>
</ul>
"""


def risks_reco():
    return """
<h2 id="risks">10. Risks</h2>
<table class="small">
<tr><th>Risk</th><th>Mitigation</th></tr>
<tr><td>Chinese price cuts (RobStride guides 300k units in 2026)</td><td>Never compete on price alone; sell compliance, service, custom and large joints</td></tr>
<tr><td>Rare-earth magnet export licences (wider Chinese rules paused only until 10 Nov 2026)</td><td>Stockpile magnet sets; qualify N48H (no Dy); watch India's REPM plants (2027–28)</td></tr>
<tr><td>Humanoid hype cycle (Unitree −59 % from its IPO open)</td><td>Sell to non-humanoid robots too; keep burn low; raise on revenue</td></tr>
<tr><td>Quality / field failures</td><td>End-of-line testing on every unit, life testing, warranty reserves</td></tr>
<tr><td>Thin Indian VC for hardware (US$53 M for all robotics in 2025)</td><td>Use grants, defence programmes, customer prepayments, strategic investors</td></tr>
</table>

<h2 id="reco">11. Recommendation</h2>
<ol>
<li><b>Yes, build an actuator company, not another humanoid company.</b> The demand is real and every Indian robot maker imports today.</li>
<li><b>Start as an integrator</b> (sell imported joints with Indian software, stock and support) to earn revenue in months, while JXA-120/40 are
developed with the ₹3–4 lakh garage kit from the technical paper.</li>
<li><b>Sell first to labs, startups and defence</b>, at prices between RobStride-landed and CubeMars-India; use grants (Seed Fund, incubators, iDEX) before VC.</li>
<li><b>Raise in small steps</b> (≈ ₹2 cr seed, ≈ ₹11 cr Series A) and build volume tooling only against signed orders.</li>
<li><b>Forget "1 % of a trillion"</b>: aim to be one of the qualified non-Chinese actuator suppliers by 2030. If the 2035 market reaches US$40–90 bn,
that position is worth far more than any shortcut.</li>
<li><b>Copper is not your lever; magnets and quality are.</b></li>
</ol>
<h2 id="sources">Sources</h2>
<ul class="refs">
<li><code>research/raw/market_outlook_2030_copper_raw.md</code>: humanoid forecasts (BofA Institute "Physical AI" Mar 2026, Citi GPS, Goldman, Morgan Stanley, UBS), IFR World Robotics 2026,
S&amp;P Global copper study (Jan 2026), ICSG, COMEX, Stanford AI Index 2026, BLS 2024–34 projections, Brynjolfsson et al., WEF Future of Jobs 2025, valuations (stockanalysis.com)</li>
<li><code>research/raw/india_robotics_industry_capital_raw.md</code>: Indian actuator/robot companies, clusters, motor-line capex, government schemes (PIB: RDI scheme, ECMS), Indian VC data (Tracxn via press)</li>
<li><code>research/raw/china_actuator_manufacturing_economics_raw.md</code>: RobStride, Unitree prospectus, broker teardowns, wages, magnet export rules, India REPM scheme, duties</li>
<li><code>actuators/inhouse/</code>: the technical paper, design and cost models used for unit costs</li>
<li><code>business/actuator_business_model.py</code>: the staged capital model (all assumptions in the code)</li>
</ul>
"""


def build_html():
    s = B["stages"]
    cover = f"""
<div class="cover">
 <div class="band">
  <div class="sub">JX1 humanoid project · business research · {DATE}</div>
  <h1>Robot actuators as a business in India</h1>
  <div class="sub">The robot market to 2030–2035, copper, software vs hardware, who makes actuators in India, how actuator factories are built,
  how much capital it takes, and a go-to-market plan</div>
 </div>
 <div>
 <div class="kpis">
  <div class="kpi"><b>US$8–14 bn</b><span>humanoid-actuator market in 2030 (from ≈ US$0.23 bn in 2025); US$10–90 bn in 2035</span></div>
  <div class="kpi"><b>&lt; 0.1 %</b><span>humanoids' share of world copper demand in 2030: copper is not the lever</span></div>
  <div class="kpi"><b>≈ 0</b><span>Indian makers of RobStride-class actuators at volume; ≈ 55k industrial servo joints/yr imported</span></div>
  <div class="kpi"><b>{cr(B['total_capital_all_stages'])}</b><span>external capital from garage to a 60k/yr plant, in four stages</span></div>
  <div class="kpi"><b>{cr(s[3]['revenue_per_yr'])}/yr</b><span>revenue at 60k actuators/yr (≈ US${s[3]['revenue_per_yr'] / C['assumptions']['INR_USD'] / 1e6:.0f} M)</span></div>
  <div class="kpi"><b>≈ 25 %</b><span>of the whole 2030 actuator market needed for a US$10 bn company at 4× sales</span></div>
 </div>
 <div class="abstract"><b>Summary.</b> Making actuators ("selling shovels") is a sounder business than making another humanoid: the market is real, growing ≈ 40× from 2025 to 2030,
 and every Indian robot maker imports its joints today. But it is a manufacturing business with 25–45 % gross margins, against Chinese makers already at
 50k–500k units a year. An Indian company should start as an integrator and supplier to labs, startups and defence, sell trust, service and
 customisation rather than price, use grants before venture capital, and build volume tooling only against signed orders. Copper will likely stay
 expensive, but because of grids, EVs and data centres, not robots.</div>
 </div>
 <div class="toc"><b>Contents</b><br><a href="#answers">1. Your questions</a><br><a href="#market">2. Robot market</a><br><a href="#copper">3. Copper</a><br>
 <a href="#software">4. Software vs hardware</a><br><a href="#landscape">5. India landscape</a><br><a href="#factory">6. Factory + equations</a><br>
 <a href="#capital">7. Capital</a><br><a href="#valuation">8. Valuation</a><br><a href="#gtm">9. Go-to-market</a><br><a href="#risks">10. Risks</a><br>
 <a href="#reco">11. Recommendation</a></div>
</div>"""
    body = cover + answers() + market() + copper() + software() + landscape() + factory() + capital() + valuation() + gtm() + risks_reco()
    return f'<!doctype html><html><head><meta charset="utf-8"><title>Robot actuators as a business in India</title><style>{CSS}</style></head><body>{body}</body></html>'


def main():
    BUILD.mkdir(exist_ok=True)
    html = BUILD / "report.html"
    html.write_text(build_html(), encoding="utf-8")
    subprocess.run([CHROME[0], "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={OUT_PDF}", html.as_uri()], check=True, capture_output=True, timeout=180)
    print("wrote", OUT_PDF, f"{OUT_PDF.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
