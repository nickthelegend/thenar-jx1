"""Business model for an Indian humanoid-actuator company: unit economics, learning curve, staged capital plan,
and a market-cap reality check. All outputs are ESTIMATED scenarios, not forecasts.

Inputs: actuators/inhouse/results/cost.json (per-unit cost at 25/yr and 1,000/yr) and the assumptions below.
Outputs: business/results/business_model.json, business/figures/*.png

Key equations (also written out in the report):
  gross margin            GM = (P - C) / P
  break-even volume       N* = F / (P - V)                         F = fixed cost per year, V = variable cost per unit
  Wright's learning curve C(N) = C1 * N ** log2(r)                  r = cost ratio per doubling of cumulative volume
  capacity / takt         lines = annual units / (available seconds per year * OEE / takt seconds)
  working capital         WC = COGS/365 * (inventory days + receivable days - payable days)
  capital to raise        K = capex + sum(operating losses until cash-positive) + WC + buffer (6 months of opex)
  market cap              MC = revenue * EV/revenue multiple ;  revenue = robots/yr * actuators per robot * share * ASP
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
FIG = HERE / "figures"
COST = json.loads((ROOT / "actuators/inhouse/results/cost.json").read_text())
INR_USD = COST["assumptions"]["INR_USD"]

# ---------------------------------------------------------------------------------------------------------------------
# 1. learning curve fitted to our own cost model: JXA-120 at 25/yr (batch) and 1,000/yr (small factory)
c_b = COST["classes"]["JXA-120"]["unit"]["B"]["total"]
c_f = COST["classes"]["JXA-120"]["unit"]["F"]["total"]
# 600/yr anchor, bottom-up (ESTIMATED): job-shop gears ~₹3k/set in lots of 100+, housings ₹2.5k, bearings ₹3k (China),
# driver ₹3.5k, magnets+copper+bought core ₹2k, labour ~5 h at ₹300, consumables + test/scrap ₹2.5k -> ≈ ₹18k
ANCHORS = [(25, c_b), (600, 18000.0), (1000, c_f)]
r_fit = (c_f / c_b) ** (1 / math.log2(1000 / 25))           # average cost ratio per doubling, 25 -> 1,000/yr
CHINA_COGS = COST["classes"]["JXA-120"]["buy"]["china_cogs"]["central"]
FLOOR = CHINA_COGS                                          # assume an Indian line cannot go below RobStride's own cost


def unit_cost(volume_per_year: float) -> float:
    """JXA-120-equivalent direct cost at a yearly volume: log-log interpolation through the anchors, then a slow
    90 %-per-doubling decline above 1,000/yr, floored at RobStride's estimated cost."""
    v = volume_per_year
    if v <= ANCHORS[0][0]:
        return ANCHORS[0][1]
    for (v0, c0), (v1, c1) in zip(ANCHORS, ANCHORS[1:]):
        if v <= v1:
            t = math.log(v / v0) / math.log(v1 / v0)
            return max(FLOOR, math.exp(math.log(c0) + t * (math.log(c1) - math.log(c0))))
    return max(FLOOR, c_f * (v / 1000) ** math.log2(0.90))


# ---------------------------------------------------------------------------------------------------------------------
# 2. staged plan (all figures per year; units are JXA-120-equivalents; ESTIMATED / ASSUMED)
STAGES = [
    # name, years, units/yr, ASP ₹, team, loaded ₹/person/yr, other opex ₹/yr, capex ₹, who buys
    dict(name="0. Bootstrap / prototypes", months=9, units=12, asp=0, team=2, salary=0, other=1500000, capex=322000 + 800000,
         buyers="none yet: build JXA-120 v1/v2, test, show a walking leg"),
    dict(name="1. Seed: first customers", months=18, units=600, asp=42000, team=9, salary=1400000, other=4000000, capex=1572000 + 3000000,
         buyers="Indian university labs, robotics startups, defence R&D (iDEX), cobot/exoskeleton makers"),
    dict(name="2. Series A: product line", months=24, units=6000, asp=30000, team=35, salary=1600000, other=30000000, capex=40000000,
         buyers="Indian humanoid/quadruped/AMR makers, defence programmes, export to non-China-sourcing buyers"),
    dict(name="3. Series B: volume plant", months=24, units=60000, asp=21000, team=140, salary=1700000, other=150000000, capex=450000000,
         buyers="humanoid OEMs at volume (India + export), industrial automation"),
]
INV_DAYS, REC_DAYS, PAY_DAYS = 120, 60, 30                  # magnets/bearings are imported with long lead times
TAKT_S, OEE, SHIFT_S = 90, 0.65, 2 * 8 * 3600 * 300          # 90 s per joint (Quanzhibo benchmark), 2 shifts, 300 days


def stage_economics(s: dict) -> dict:
    yrs = s["months"] / 12
    cogs_u = unit_cost(max(s["units"], 25))
    rev = s["units"] * s["asp"]
    cogs = s["units"] * cogs_u
    opex = s["team"] * s["salary"] + s["other"]
    ebitda = rev - cogs - opex
    wc = cogs / 365 * (INV_DAYS + REC_DAYS - PAY_DAYS)
    burn = max(0.0, -ebitda) * yrs
    raise_needed = s["capex"] + burn + wc + 0.5 * opex
    lines = s["units"] / (SHIFT_S * OEE / TAKT_S)
    return {**s, "unit_cost": cogs_u, "revenue_per_yr": rev, "cogs_per_yr": cogs, "opex_per_yr": opex,
            "gross_margin": (rev - cogs) / rev if rev else None, "ebitda_per_yr": ebitda, "working_capital": wc,
            "burn_over_stage": burn, "capital_to_raise": raise_needed, "assembly_lines_needed": lines,
            "breakeven_units": opex / (s["asp"] - cogs_u) if s["asp"] > cogs_u else None}


# ---------------------------------------------------------------------------------------------------------------------
# 3. market-cap reality check: what does "1 % of a trillion-dollar market" need?
def mc_check():
    """What share of the humanoid-actuator market does a US$10 bn market cap need? (market sizes: market_outlook_2030_copper_raw.md)"""
    markets = {"2030 (BofA: 1.2 M humanoids x US$17k x 51 %)": 10.4e9, "2035 low (Goldman: 30-35 % of US$138 bn)": 41e9,
               "2035 high (BofA: 10 M x US$13-17k x 51 %)": 87e9}
    out = []
    for mult in (2, 4, 10):
        rev = 10e9 / mult
        out.append({"ev_to_sales": mult, "revenue_needed_usd": rev,
                    "share_needed": {k: rev / v for k, v in markets.items()},
                    "actuators_per_year_at_usd250": rev / 250})
    return {"markets_usd": markets, "for_10bn_market_cap": out,
            "one_percent_of_2030_market": {"revenue_usd": 0.01 * 10.4e9, "market_cap_at_4x_usd": 4 * 0.01 * 10.4e9}}


def main():
    OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
    stages = [stage_economics(s) for s in STAGES]
    curve = [{"units_per_year": v, "unit_cost": unit_cost(v)} for v in (25, 100, 300, 1000, 3000, 10000, 30000, 100000, 300000)]
    res = {"learning_rate_per_doubling": r_fit, "floor_unit_cost": FLOOR, "china_cogs_central": CHINA_COGS,
           "rs04_landed_china_distributor": COST["classes"]["JXA-120"]["buy"]["china_distributor"],
           "stages": stages, "curve": curve, "mc_check": mc_check(),
           "total_capital_all_stages": sum(s["capital_to_raise"] for s in stages),
           "assumptions": {"inventory_days": INV_DAYS, "receivable_days": REC_DAYS, "payable_days": PAY_DAYS,
                           "takt_s": TAKT_S, "oee": OEE, "shift_seconds_per_year": SHIFT_S}}
    (OUT / "business_model.json").write_text(json.dumps(res, indent=2, default=float))
    print(f"learning rate {r_fit:.3f}, floor {FLOOR:.0f}")
    for s in stages:
        print(f"{s['name']:32s} units {s['units']:>6} cost {s['unit_cost']:>7.0f} rev {s['revenue_per_yr'] / 1e7:6.2f} cr "
              f"GM {s['gross_margin'] if s['gross_margin'] is None else round(s['gross_margin'], 2)} EBITDA {s['ebitda_per_yr'] / 1e7:6.2f} cr "
              f"raise {s['capital_to_raise'] / 1e7:6.2f} cr lines {s['assembly_lines_needed']:.2f} BE {s['breakeven_units'] and round(s['breakeven_units'])}")
    for c in curve:
        print(c)
    print("total capital", res["total_capital_all_stages"] / 1e7, "cr")
    plots(res)


def plots(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "serif", "font.serif": ["STIXGeneral", "DejaVu Serif"], "mathtext.fontset": "stix", "font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(6.8, 3.3))
    v = [c["units_per_year"] for c in res["curve"]]; y = [c["unit_cost"] / 1000 for c in res["curve"]]
    ax.plot(v, y, "-o", color="#14213d", lw=2, ms=4, label="JXA-120 direct cost in India (ESTIMATED)")
    ax.axhline(res["rs04_landed_china_distributor"] / 1000, color="#1f5fa8", ls="--", lw=1.2, label="RS04 landed in India via China distributor")
    ax.axhline(res["china_cogs_central"] / 1000, color="#7e8c99", ls=":", lw=1.4, label="RobStride's estimated own cost (COGS)")
    for s in res["stages"][1:]:
        ax.axvline(s["units"], color="#c9a227", lw=0.8, alpha=0.7)
        ax.text(s["units"], max(y) * 0.92, s["name"].split(":")[0], rotation=90, va="top", ha="right", fontsize=7, color="#8a6d00")
    ax.set_xscale("log"); ax.set_xlabel("units per year"); ax.set_ylabel("INR thousand per actuator")
    ax.grid(alpha=0.25); ax.legend(fontsize=7, frameon=False, loc="upper right")
    fig.tight_layout(); fig.savefig(FIG / "learning_curve.png", dpi=200); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6.8, 3.0))
    names = [s["name"].split(":")[0] for s in res["stages"]]
    raise_ = [s["capital_to_raise"] / 1e7 for s in res["stages"]]
    rev = [s["revenue_per_yr"] / 1e7 for s in res["stages"]]
    x = range(len(names))
    ax.bar([i - 0.2 for i in x], raise_, width=0.4, color="#b0413e", label="capital to raise (INR crore)")
    ax.bar([i + 0.2 for i in x], rev, width=0.4, color="#14213d", label="revenue per year at end of stage (INR crore)")
    for i, (a, b) in enumerate(zip(raise_, rev)):
        ax.text(i - 0.2, a, f"{a:.1f}", ha="center", va="bottom", fontsize=7)
        ax.text(i + 0.2, b, f"{b:.1f}", ha="center", va="bottom", fontsize=7)
    ax.set_xticks(list(x)); ax.set_xticklabels(names, fontsize=7.5); ax.set_yscale("symlog", linthresh=1)
    ax.set_ylabel("INR crore (log scale)"); ax.legend(fontsize=7, frameon=False); ax.grid(axis="y", alpha=0.25)
    fig.tight_layout(); fig.savefig(FIG / "capital_plan.png", dpi=200); plt.close(fig)


if __name__ == "__main__":
    main()
