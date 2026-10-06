"""Cost model: building JXA actuators in India vs buying RobStride/Damiao from China, and what a Chinese maker spends.

Three production tiers per actuator class (all ESTIMATED; every input price is traced to research/raw/*):
  P  prototype   2 units of a class, parts bought at retail/small MOQ, engineer's hands-on time
  B  batch       25 units/yr of a class (one JX1 set + spares), job-work parts, technician time
  F  factory     1,000 units/yr of a class, own semi-automatic line, stamped laminations, bulk magnets/cores
Buy options (from bom/ and research/raw/actuator_technology_raw.md): USD list landed in India, China distributor (CNY list),
and an ESTIMATED Chinese manufacturing cost (COGS) from broker teardowns and RobStride's price
(research/raw/china_actuator_manufacturing_economics_raw.md).

Usage: python actuators/inhouse/cost_model.py   -> results/cost.json + figures/cost_*.png
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
FIG = HERE / "figures"
INR_USD = 95.96          # repo convention (bom/build_bom.py)
INR_CNY = 13.52
LANDED = 1.3228 * 1.07   # HS 8501 effective duty (repo; an aggregator says 40.4 % - confirm on ICEGATE) x shipping

design = {d["spec"]["name"]: d for d in json.loads((OUT / "design.json").read_text())}
TIERS = ["P", "B", "F"]
TIER_NAME = {"P": "Prototype (2 units)", "B": "Batch (25 / yr)", "F": "Small factory (1,000 / yr)"}

# ---------------------------------------------------------------------------------------------------------------------
# unit prices (INR). Sources: india_motor_materials_raw.md (IMM), india_mechanical_manufacturing_raw.md (IMF),
# china_actuator_manufacturing_economics_raw.md (CME). All ESTIMATED from the cited listings.
MAGNET_INR_PER_KG = {"P": 33000, "B": 15000, "F": 6000}   # custom arcs, small lot by air (~US$340/kg) -> 100s (~$155) -> bulk blanks x1.6-2 (IMM 2.1/2.2)
COPPER_INR_PER_KG = {"P": 6000, "B": 2000, "F": 1700}     # AliExpress 1 kg reels landed (IMM 1.4) -> bulk class-200 wire (IMM 1.1, LME $14.5k/t)
COPPER_SCRAP = 1.5
LABOUR_INR_PER_H = {"P": 500, "B": 300, "F": 220}         # engineer / technician / operator, fully loaded (CME 3: India ₹19-24k/month base)
TEST_SCRAP = {"P": 0.15, "B": 0.10, "F": 0.05}

# per-class items that do not scale with a model mass: (P, B, F)
ITEMS = {
    "JXA-40": {
        "stator core (laminations)": (2500, 800, 180),    # bought 6110/7215-class core or EDM stack -> laser+bond -> stamped
        "insulation + varnish": (500, 200, 60),
        "rotor can + end plate": (2000, 800, 260),
        "gear set (sun, 3 planets, ring), carburised": (9000, 3300, 1100),
        "housing, hub, carrier (CNC Al)": (6500, 2800, 1000),
        "bearings (output + rotor + planets)": (3800, 2400, 1200),
        "driver PCB + 2 encoders": (5500, 3800, 2200),
        "fasteners, connectors, grease, adhesive": (1000, 550, 250),
        "_hours": (26, 8, 2.0),
    },
    "JXA-120": {
        "stator core (laminations)": (3000, 1200, 300),   # bought 10020 core ~US$19-31 landed / EDM ₹1.3-2.2k (IMM 3.2, 3.4)
        "insulation + varnish": (600, 250, 80),
        "rotor can + end plate": (3000, 1200, 400),
        "gear set (sun, 3 planets, ring), carburised": (15000, 5500, 1800),
        "housing, hub, carrier (CNC Al)": (10000, 4500, 1600),
        "bearings (output + rotor + planets)": (6100, 4400, 2250),  # crossed-roller $13-67 China (IMM 4.1) vs IKO ₹11.8k India (IMF 1d)
        "driver PCB + 2 encoders": (7000, 4500, 2600),             # ~US$30-45 landed board at 10 pcs (IMM 4.5), 90 A stage
        "fasteners, connectors, grease, adhesive": (1500, 800, 350),
        "_hours": (32, 10, 2.5),
    },
    "JXA-360": {
        "stator core (laminations)": (9000, 3500, 800),   # 3 stacked 13710 cores (US$74 each) or EDM 30 mm stack
        "insulation + varnish": (1000, 450, 150),
        "rotor can + end plate": (6500, 2700, 900),
        "gear set (sun, 3 planets, ring), carburised": (32000, 12500, 4100),
        "housing, hub, carrier (CNC Al)": (21000, 10000, 3600),
        "bearings (output + rotor + planets)": (12000, 8500, 4500),
        "driver PCB + 2 encoders": (12000, 8000, 4500),            # 200 A peak stage: paralleled MOSFETs, 4-layer heavy copper
        "fasteners, connectors, grease, adhesive": (2500, 1400, 600),
        "_hours": (40, 14, 3.5),
    },
}

# buy options per class (INR per unit)
BUY = {
    "JXA-40": {"ref": "RobStride RS06 (36 N·m)", "usd": 210, "cny": 849, "peak": 36},
    "JXA-120": {"ref": "RobStride RS04 (120 N·m)", "usd": 255, "cny": 1199, "peak": 120},
    "JXA-360": {"ref": "Damiao DM-J10422P (400 N·m)", "usd": 480, "cny": None, "peak": 400},
}
# Chinese maker's manufacturing cost per unit (COGS), ESTIMATED: list price x (1 - gross margin 30-45 %) for RobStride,
# cross-checked with China Post's Unitree G1 joint BOM (¥1,000 small / ¥1,500 large) - CME section 2
CHINA_COGS_CNY = {"JXA-40": (470, 600, 1000), "JXA-120": (660, 840, 1500), "JXA-360": (1500, 2000, 3000)}  # low, central, high
COGS_SPLIT = {"reducer": 0.27, "motor (stator, magnets, rotor)": 0.20, "encoders": 0.20, "driver": 0.17, "structure + bearings": 0.16}

# one-time equipment (INR); IMM section 6 test-gear and winder prices, CME 3 capex benchmarks
NRE = {
    "P": {"winding jig + turn counter": 5000, "LCR meter (TH2830 class)": 45000, "insulation (hipot) tester": 15000,
          "4-wire milliohm meter": 10000, "bench supply 60 V / 15 A": 18000, "curing oven (used)": 15000,
          "oscilloscope": 35000, "dyno bench: hysteresis brake + DYN-200 torque sensor + frame": 140000,
          "USB-CAN adapters": 6000, "printed assembly fixtures, rotor guide sleeves": 8000, "hand tools, consumables": 25000},
    "B": {"semi-automatic needle winder (US$5-8k + duty)": 700000, "surge (impulse) tester": 100000,
          "second dyno + thermal chamber": 150000, "assembly + magnet-bonding fixtures": 150000,
          "simple rotor balancer": 50000, "inspection: bore gauges, height gauge, gear-roll tester": 100000},
    "F": {"CNC needle winders x2": 4000000, "stator stamping dies, 3 classes (no quote found)": 2400000,
          "gear tooling (hobs, PM dies for sun/planets)": 1500000, "end-of-line test stations x2": 2000000,
          "dynamic balancing machine": 600000, "varnish/cure line": 500000, "ESD assembly line + fixtures": 1500000,
          "quality lab": 1000000},
}
OVERHEAD_PER_YEAR = {"P": 0, "B": 1200000, "F": 6000000}   # B: 1 engineer + space; F: 3 engineers, QA, rent, utilities
AMORT_YEARS = 3


def unit_cost(cls: str, tier: str) -> dict:
    d = design[cls]
    i = TIERS.index(tier)
    lines = {}
    lines["magnets (NdFeB SH)"] = d["materials_bill"]["magnet_g"] / 1000 * MAGNET_INR_PER_KG[tier]
    lines["copper wire (class 200)"] = d["materials_bill"]["copper_g"] / 1000 * COPPER_SCRAP * COPPER_INR_PER_KG[tier]
    for k, v in ITEMS[cls].items():
        if not k.startswith("_"):
            lines[k] = v[i]
    hours = ITEMS[cls]["_hours"][i]
    lines["labour (winding, assembly, calibration)"] = hours * LABOUR_INR_PER_H[tier]
    sub = sum(lines.values())
    lines["test + scrap allowance"] = sub * TEST_SCRAP[tier]
    return {"lines": lines, "total": sum(lines.values()), "hours": hours}


def buy_cost(cls: str) -> dict:
    b = BUY[cls]
    out = {"ref": b["ref"], "usd_landed": b["usd"] * INR_USD * LANDED}
    out["china_distributor"] = b["cny"] * INR_CNY * 1.05 * LANDED if b["cny"] else None   # +5 % agent, duty, freight (repo: RS04 ₹24,008)
    lo, mid, hi = CHINA_COGS_CNY[cls]
    out["china_cogs"] = {"low": lo * INR_CNY, "central": mid * INR_CNY, "high": hi * INR_CNY}
    out["china_cogs_split"] = {k: v * mid * INR_CNY for k, v in COGS_SPLIT.items()}
    return out


def main():
    res = {"assumptions": {"INR_USD": INR_USD, "INR_CNY": INR_CNY, "landed_factor": LANDED, "amort_years": AMORT_YEARS,
                           "magnet_inr_per_kg": MAGNET_INR_PER_KG, "copper_inr_per_kg": COPPER_INR_PER_KG,
                           "labour_inr_per_h": LABOUR_INR_PER_H, "overhead_per_year": OVERHEAD_PER_YEAR},
           "classes": {}, "nre": {t: {"items": NRE[t], "total": sum(NRE[t].values())} for t in TIERS}}
    for cls in ITEMS:
        res["classes"][cls] = {"unit": {t: unit_cost(cls, t) for t in TIERS}, "buy": buy_cost(cls),
                               "peak_Nm": design[cls]["performance"]["peak_out_Nm"]}
    nre_cum = {"P": res["nre"]["P"]["total"], "B": res["nre"]["P"]["total"] + res["nre"]["B"]["total"]}
    nre_cum["F"] = nre_cum["B"] + res["nre"]["F"]["total"]
    res["nre_cumulative"] = nre_cum

    # fully loaded per-unit cost at each tier: direct + (equipment / 3 yr + overhead) shared over all units of the tier
    units_per_year = {"P": 6, "B": 75, "F": 3000}             # all three classes together
    for cls, c in res["classes"].items():
        c["loaded"] = {}
        for t in TIERS:
            share = (nre_cum[t] / AMORT_YEARS + OVERHEAD_PER_YEAR[t]) / units_per_year[t]
            c["loaded"][t] = c["unit"][t]["total"] + share
        c["per_Nm"] = {t: c["loaded"][t] / c["peak_Nm"] for t in TIERS}

    # scenario 1: JX1 legs + waist (today 4 x RS04, 2 x RS03, 7 x RS06) -> 6 x JXA-120 + 7 x JXA-40, + 1 spare each
    jx1_buy_usd = 4 * 34634 + 2 * 30560 + 7 * 28522
    jx1_buy_cn = 4 * 24008 + 2 * 20004 + 7 * 17000
    u = {cls: res["classes"][cls]["unit"] for cls in ITEMS}
    proto_rounds = 2 * 2 * (u["JXA-120"]["P"]["total"] + u["JXA-40"]["P"]["total"])     # 2 design rounds x 2 units x 2 classes
    jx1_build = 7 * u["JXA-120"]["B"]["total"] + 8 * u["JXA-40"]["B"]["total"]
    res["scenario_jx1"] = {
        "buy_usd_route": jx1_buy_usd, "buy_china_distributor": jx1_buy_cn,
        "inhouse_parts_and_labour": jx1_build, "inhouse_prototype_rounds": proto_rounds,
        "inhouse_garage_equipment": res["nre"]["P"]["total"],
        "inhouse_total_first_set": jx1_build + proto_rounds + res["nre"]["P"]["total"],
        "inhouse_marginal_next_set": 6 * u["JXA-120"]["B"]["total"] + 7 * u["JXA-40"]["B"]["total"],
        "note": "JX1 buys 13 leg/waist actuators; in-house builds 15 (1 spare per class); arms keep RS02/RS00",
    }
    # scenario 2: full-size humanoid (1.75 m, ~65 kg, 28 actuators): 4 x 360, 14 x 120, 10 x 40
    mix = {"JXA-360": 4, "JXA-120": 14, "JXA-40": 10}
    buy_full = sum(n * res["classes"][c]["buy"]["usd_landed"] for c, n in mix.items())
    buy_full_cn = (4 * res["classes"]["JXA-360"]["buy"]["usd_landed"]
                   + 14 * res["classes"]["JXA-120"]["buy"]["china_distributor"] + 10 * res["classes"]["JXA-40"]["buy"]["china_distributor"])
    res["scenario_fullsize"] = {"mix": mix,
                                "buy_usd_route": buy_full, "buy_china_distributor": buy_full_cn,
                                **{f"inhouse_{t}": sum(n * res["classes"][c]["unit"][t]["total"] for c, n in mix.items()) for t in TIERS},
                                **{f"loaded_{t}": sum(n * res["classes"][c]["loaded"][t] for c, n in mix.items()) for t in TIERS},
                                "china_cogs_central": sum(n * res["classes"][c]["buy"]["china_cogs"]["central"] for c, n in mix.items())}

    # break-even for JXA-120 vs China-distributor RS04: units/yr N where direct_B + (NRE_B/3 + OH_B)/N = buy
    c120 = res["classes"]["JXA-120"]
    buy = c120["buy"]["china_distributor"]
    gaps = {}
    for t in ("B", "F"):
        margin = buy - c120["unit"][t]["total"]
        fixed = nre_cum[t] / AMORT_YEARS + OVERHEAD_PER_YEAR[t]
        gaps[t] = {"margin_per_unit": margin, "fixed_per_year": fixed, "breakeven_units_per_year": fixed / margin if margin > 0 else None}
    res["breakeven_jxa120_vs_rs04_china"] = gaps

    OUT.mkdir(exist_ok=True)
    (OUT / "cost.json").write_text(json.dumps(res, indent=2, default=float))
    for cls, c in res["classes"].items():
        print(cls, {t: round(c["unit"][t]["total"]) for t in TIERS}, "loaded", {t: round(c["loaded"][t]) for t in TIERS},
              "buy", round(c["buy"]["usd_landed"]), c["buy"]["china_distributor"] and round(c["buy"]["china_distributor"]),
              "cogs", {k: round(v) for k, v in c["buy"]["china_cogs"].items()})
    print("NRE", {t: res["nre"][t]["total"] for t in TIERS}, "cum", nre_cum)
    print("JX1", {k: (round(v) if isinstance(v, (int, float)) else v) for k, v in res["scenario_jx1"].items()})
    print("FULL", {k: (round(v) if isinstance(v, (int, float)) else v) for k, v in res["scenario_fullsize"].items()})
    print("BE", gaps)
    plots(res)


def plots(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False})

    # 1. per-unit cost: in-house tiers vs buy options, per class (log scale is avoided so the gap is honest)
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.6))
    for ax, (cls, c) in zip(axes, res["classes"].items()):
        labels = ["Make:\nproto", "Make:\nbatch 25", "Make:\n1k/yr", "Buy:\nUSD", "Buy:\nChina", "China\nCOGS"]
        vals = [c["unit"]["P"]["total"], c["unit"]["B"]["total"], c["unit"]["F"]["total"], c["buy"]["usd_landed"],
                c["buy"]["china_distributor"] or 0, c["buy"]["china_cogs"]["central"]]
        cols = ["#b0413e", "#d98c3a", "#e8b04b", "#1f5fa8", "#5b8fd1", "#7e8c99"]
        bars = ax.bar(range(6), [v / 1000 for v in vals], color=cols)
        loaded = [c["loaded"]["P"], c["loaded"]["B"], c["loaded"]["F"]]
        ax.scatter(range(3), [v / 1000 for v in loaded], marker="_", s=400, color="#222", zorder=3, label="incl. equipment + overhead")
        lo, hi = c["buy"]["china_cogs"]["low"], c["buy"]["china_cogs"]["high"]
        ax.errorbar([5], [c["buy"]["china_cogs"]["central"] / 1000], yerr=[[(c["buy"]["china_cogs"]["central"] - lo) / 1000], [(hi - c["buy"]["china_cogs"]["central"]) / 1000]],
                    color="#222", capsize=3, lw=0.8)
        for b_, v in zip(bars, vals):
            if v:
                ax.text(b_.get_x() + b_.get_width() / 2, v / 1000 + 1, f"{v / 1000:.0f}k", ha="center", fontsize=7)
        ax.set_xticks(range(6)); ax.set_xticklabels(labels, fontsize=7)
        ax.set_title(f"{cls} vs {c['buy']['ref']}", fontsize=8.5, fontweight="bold")
        ax.set_ylabel("₹ thousand per actuator"); ax.grid(axis="y", alpha=0.25)
        top = max(max(vals), max(loaded))
        ax.set_ylim(0, top / 1000 * 1.1)
    axes[0].legend(fontsize=6.5, frameon=False, loc="upper right")
    fig.tight_layout(); fig.savefig(FIG / "cost_per_unit.png", dpi=200); plt.close(fig)

    # 2. cost breakdown of a JXA-120 at the three tiers (stacked)
    c = res["classes"]["JXA-120"]
    keys = list(c["unit"]["P"]["lines"].keys())
    fig, ax = plt.subplots(figsize=(7.6, 3.5))
    cmap = plt.get_cmap("tab20")
    left = np.zeros(4)
    rows = [c["unit"][t]["lines"] for t in TIERS] + [None]
    names = [TIER_NAME[t] for t in TIERS] + ["China maker COGS (est.)"]
    cogs = c["buy"]["china_cogs_split"]
    for j, k in enumerate(keys):
        v = np.array([r[k] for r in rows[:3]] + [0]) / 1000
        ax.barh(names, v, left=left, color=cmap(j), label=k, height=0.6)
        left += v
    left_c = 0
    for j, (k, v) in enumerate(cogs.items()):
        ax.barh(names[3], v / 1000, left=left_c, color=plt.get_cmap("Greys")(0.35 + 0.12 * j), height=0.6)
        left_c += v / 1000
    ax.invert_yaxis(); ax.set_xlabel("₹ thousand per JXA-120 / RS04-class actuator")
    ax.legend(fontsize=6, frameon=False, loc="center left", bbox_to_anchor=(1.0, 0.5))
    for y, t in enumerate(TIERS):
        ax.text(c["unit"][t]["total"] / 1000 + 0.8, y, f"₹{c['unit'][t]['total'] / 1000:.1f}k", va="center", fontsize=7)
    ax.text(left_c + 0.8, 3, f"₹{left_c:.1f}k", va="center", fontsize=7)
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout(); fig.savefig(FIG / "cost_breakdown_jxa120.png", dpi=200); plt.close(fig)


if __name__ == "__main__":
    main()
