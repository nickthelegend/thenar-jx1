"""Generate bom/master_bom.csv and bom/cost_summary.md for JX1 (INR).

Every purchased row cites the Indian (or import) source read on 2026-09-24 in research/raw/*.md.
Price basis column says whether the unit price includes GST, or is an ESTIMATED landed import cost.
Re-run after any design change:  .venv/Scripts/python bom/build_bom.py
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-24"
USD_INR = 95.96            # VERIFIED via web search 2026-09-24 (tradingeconomics / foreignexchange.org.uk quotes 95.71-95.96)
DUTY = 0.3228              # effective import duty HS 8501 (BCD 10 % + SWS + IGST 18 %), cybex.in / seair.co.in (VERIFIED-secondary)
SHIP = 0.07                # courier/forwarding allowance on import value (ASSUMED)
CNY_INR = USD_INR / 7.10   # ASSUMED CNY/USD 7.10 for the China-distributor alternative


def landed_usd(usd):
    return round(usd * USD_INR * (1 + DUTY) * (1 + SHIP))


def landed_cny(cny, agent=0.05):
    return round(cny * CNY_INR * (1 + DUTY) * (1 + SHIP + agent))


RS = "https://robstride.com  (official intl. store; datasheets github.com/RobStride/Product_Information)"
ROWS = []


def add(sub, part, model, spec, qty, supplier, url, unit, basis, avail, weight_kg, alt="", alt_price="", reason="", status="PLANNED",
        evidence="VERIFIED", phase="1"):
    ROWS.append({"ID": f"JX1-{len(ROWS) + 1:03d}", "Subsystem": sub, "Part": part, "Exact model": model, "Specification": spec,
                 "Quantity": qty, "Supplier": supplier, "URL": url, "Unit price INR": unit, "Total INR": round(unit * qty),
                 "Price basis": basis, "Availability": avail, "Weight kg (each)": weight_kg, "Alternative": alt,
                 "Alternative price INR": alt_price, "Reason selected": reason, "Status": status, "Evidence": evidence,
                 "Date checked": DATE, "Phase": phase})


# ------------------------------------------------------------------ actuators (import: no Indian stockist found, see research)
for sub, n, model, usd, cny, kg, spec, reason, phase in [
    ("Legs", 4, "RobStride RS04", 255, 1199, 1.42, "120/40 N·m peak/rated, 9:1, 48 V, CAN 1 Mbps, 14-bit abs., Ø120×56", "hip pitch + knee: only class meeting 85/71 N·m peak and 26-30 N·m continuous with policy margins (iter1-B)", "1"),
    ("Legs", 2, "RobStride RS03", 225, 999, 0.88, "60/20 N·m, 9:1, 48 V, CAN, Ø106×56", "hip roll: 50 N·m peak / 17 N·m cont. required", "1"),
    ("Legs", 6, "RobStride RS06", 210, 849, 0.621, "36/11 N·m, 9:1, 48 V, 50 rad/s, Ø88×49", "hip yaw (37 N·m) and parallel-ankle pairs (32 N·m motor-side incl. toe-stand)", "1"),
    ("Torso", 1, "RobStride RS06", 210, 849, 0.621, "36/11 N·m", "waist yaw 21 N·m peak required", "2"),
    ("Arms", 4, "RobStride RS02", 145, 699, 0.38, "17/6 N·m, 7.75:1, Ø78.5×45.5", "shoulder pitch/roll 15 N·m at 0.3 kg payload", "2"),
    ("Arms", 4, "RobStride RS00", 125, 598, 0.31, "14/5 N·m, 10:1, Ø57×51", "shoulder yaw 9 N·m, elbow 6 N·m", "2"),
]:
    add(sub, "Joint actuator", model, spec, n, "RobStride Dynamics (import, courier)", RS, landed_usd(usd), "ESTIMATED landed: USD list × 95.96 × 1.323 duty × 1.07 ship",
        "In stock at official store; NOT stocked in India (Robu/Robocraze/ThinkRobotics/Amazon.in searched)", kg,
        alt=f"Same unit via China distributor (CNY {cny})", alt_price=landed_cny(cny), reason=reason, status="SELECTED", evidence="VERIFIED list price / ESTIMATED landed", phase=phase)

# ------------------------------------------------------------------ leg mechanics (per robot)
add("Legs", "Hip yaw bracket (L/R)", "JX1_HipYawBracket", "FDM PA-CF, 4 walls, 40 % gyroid, ~0.15 kg (~7 h)", 2, "In-house Bambu P1S", "CAD/Hip", 105, "ESTIMATED print time @ ₹15/h (material in filament line)", "Make", 0.15, "Outsourced CF-PETG print (iamRapid ≈ ₹42/g)", 6300, "structural bracket, printable in one piece")
add("Legs", "Hip roll bracket (L/R)", "JX1_HipRollBracket", "FDM PA-CF ~0.18 kg (~8 h)", 2, "In-house Bambu P1S", "CAD/Hip", 120, "ESTIMATED print time @ ₹15/h", "Make", 0.18, "", "", "L-bracket joining roll output to pitch housing")
add("Legs", "Thigh plate (L/R)", "JX1_Thigh", "6061-T6 8 mm plate, waterjet/CNC + 2 flanges", 2, "Local CNC job shop (Makenica instant quote / Robocon CNC)", "https://makenica.com/cnc-machining-service-online/", 4000, "ESTIMATED (no public per-part price; FabFlow claims ₹450-1,200/bracket)", "Quote required", 0.55, "FDM PA-CF thigh (stiffness check pending)", 1500, "carries hip-pitch + knee loads; coplanar actuator faces")
add("Legs", "Shin (L/R)", "JX1_Shin", "FDM PA-CF ~0.40 kg (web + knee plate + fork, ~16 h)", 2, "In-house Bambu P1S", "CAD/Shin", 240, "ESTIMATED print time @ ₹15/h", "Make", 0.40, "Al plate web + printed fork", 3500, "central web carries both ankle motors")
add("Legs", "Ankle cross (spider)", "JX1_AnkleCross", "EN8/EN24 steel, 32×33×26 turned + 2 cross-drilled Ø8 bores", 2, "Local turner", "", 800, "ESTIMATED", "Quote required", 0.20, "", "", "universal-joint centre, hardened pins")
add("Legs", "Ankle pins", "Astro hard-chrome Ø8 rod 1 m (cut to 4 pins)", "Ø8 h6 hard-chrome carbon steel", 1, "Robokits", "https://robokits.co.in/mechanical-parts/cnc-router-xyz-axis-part/astro-chrome-plated-steel-rods/", 280, "excl. GST (may be added)", "In stock", 0.40)
add("Legs", "Needle bearings", "N2K HK0810", "8×12×10 drawn-cup needle bearing", 8, "bearinghouse.in", "https://bearinghouse.in/shop/n2k-hk0810-needle-roller-bearing/", 35.40, "incl. GST", "In stock", 0.004)
add("Legs", "Ankle crank", "JX1_AnkleCrank", "6061 6 mm plate, CNC/laser, pilot recess", 4, "Local CNC / laser", "", 600, "ESTIMATED", "Quote required", 0.05)
add("Legs", "Rod-end bearings", "N2K POS5 / PHS5 (M5)", "M5 rod end, female/male", 8, "bearinghouse.in", "https://bearinghouse.in/shop/n2k-pos5-rod-end-bearing/", 141.60, "incl. GST", "In stock", 0.02, "THK POS5", 1769, "10x cheaper than THK; adequate for 32 N·m motor / 50 mm crank (≈ 640 N rod force)")
add("Legs", "Push-rod studs", "M5 threaded rod SS304 (cut to 199/106 mm)", "M5", 4, "Robokits / local hardware", "", 60, "ESTIMATED", "In stock", 0.02)
add("Legs", "Foot (L/R)", "JX1_Foot", "FDM PA-CF ~0.30 kg + clevis + rod posts (~12 h)", 2, "In-house Bambu P1S", "CAD/Foot", 180, "ESTIMATED print time @ ₹15/h", "Make", 0.30)
add("Legs", "Sole pad material", "4 mm rubber anti-skid mat (cut)", "4 mm rubber", 1, "Moglix", "https://www.moglix.com/forgesy-4-mm-rubber-anti-skid-yoga-mat/mp/msn8kl2wp0rr5v", 548, "incl. GST", "In stock", 0.10, "TPU 95A printed sole (Elegoo ₹1,399/kg)", 400)
add("Legs", "Foot contact sensors", "SOUSHINE FSR406", "39.7 mm FSR, 20 g-10 kg", 8, "Robu", "https://robu.in/product/soushine-fsr406-short-tail-39-7-mm-39-7-mm-force-sensing-shunt-resistor-20g10kg/", 379, "incl. GST", "In stock", 0.003, "", "", "4 per foot for CoP estimation", status="OPTIONAL", phase="2")
add("Legs", "Leg fasteners & inserts", "Unbrako SHCS M3/M4/M5 packs + Quartz M3 heat-set inserts", "per robot allowance", 1, "IndustryBuying / Quartz", "https://www.industrybuying.com/dowel-pin-unbrako-FAM257317", 3000, "ESTIMATED from pack prices (₹211-530 per 100 SHCS, ₹33-70 per 10 inserts)", "In stock (30-day lead on Unbrako)", 0.30)

# ------------------------------------------------------------------ pelvis
add("Pelvis", "Pelvis torsion box", "JX1_Pelvis", "FDM PA-CF ~0.65 kg, M3 heat-set inserts (~24 h)", 1, "In-house Bambu P1S", "CAD/Pelvis", 360, "ESTIMATED print time @ ₹15/h", "Make", 0.65)
add("Pelvis", "IMU", "7Semi BNO085 Nano breakout", "9-DOF fusion IMU, SPI/I2C", 1, "Evelta", "https://evelta.com/7semi-bno085-9-dof-orientation-imu-fusion-nano-breakout/", 2094.50, "incl. GST", "In stock (21)", 0.005, "SmartElex BNO085 (Robu)", 2409, "on-chip fusion, 400 Hz rotation vector")

# ------------------------------------------------------------------ compute & real-time network
add("Electronics", "High-level computer", "Waveshare JETSON-NANO-DEV-KIT (Nano 4 GB module, 16 GB eMMC, 64 GB card)", "4× A57, 128-core Maxwell, 4 GB", 1, "ThinkRobotics", "https://thinkrobotics.com/products/thinkrobotics-jetson-nano-dev-kit-sub", 30899.99, "incl. GST", "In stock", 0.25, "Jetson Orin Nano Super dev kit (upgrade path, native CAN)", 49999.99, "brief mandates Jetson Nano; adequate for 50 Hz RL policy + vision (research B.2)")
add("Electronics", "Real-time CAN hub MCU", "PJRC Teensy 4.1", "i.MX RT1062 600 MHz, 3× CAN (1× CAN-FD)", 2, "Robu", "https://robu.in/product/buy-teensy-4-1-development-board/", 3539, "incl. GST", "In stock", 0.01, "WeAct STM32H743 core (2× FDCAN, Probots ₹3,999)", 3999, "6 CAN buses total: 2 per leg (≤ 3 joints each) + 1 per arm; 500 Hz joint exchange, watchdogs, E-stop monitor")
add("Electronics", "CAN transceivers", "NXP TJA1462AT (SOIC-8)", "CAN/CAN-FD 8 Mbit/s SIC transceiver", 8, "Sharvi Electronics", "https://sharvielectronics.com/product/tja1462at-0z-can-fd-signal-improvement-transceiver-with-standby-mode-ic-soic-8-package/", 120.78, "incl. GST (₹102.36 ex)", "In stock", 0.001)
add("Electronics", "CAN hub carrier PCB", "JX1 hub board (2× Teensy, 6× transceiver, E-stop input, 5 V/12 V rails)", "2-layer 100×100 mm, 5 pcs", 1, "Lion Circuits", "https://lioncircuits.com/quote", 2215, "incl. GST (₹1,877 ex, public calculator)", "~5 days", 0.05, "PCB Power", 5210, "cheapest verified Indian fab")
add("Electronics", "Bench USB-CAN adapter", "Waveshare USB-CAN-A", "CAN 2.0A/B up to 1 Mbps", 1, "Robu", "https://robu.in/product/usb-to-can-adapter-model-a-stm32-chip-solution-multiple-working-modes-multi-system-compatible/", 2189, "incl. GST", "In stock", 0.03, "MKS CANable V2 (Probots ₹3,899)", 3899, "actuator bring-up / diagnostics")
add("Electronics", "CAN / power harness", "JST-GH 1.25 2-4 pin leads, twisted pair, XT30 pairs", "per robot", 1, "Probots / Robokits / Quartz", "https://probots.co.in", 3500, "ESTIMATED from ₹25-42 GH leads, ₹40-65 XT pairs, ₹35-199 /m silicone wire", "In stock", 0.40)
add("Electronics", "Wi-Fi card", "Intel AC8265 for Jetson Nano", "802.11ac + BT", 1, "Robocraze", "https://robocraze.com/search?q=AC8265", 2200, "incl. GST", "In stock", 0.01, status="PLANNED")

# ------------------------------------------------------------------ power & safety
add("Power", "Li-ion cells", "Samsung INR21700-50S", "5.0 Ah, 45 A pulse / 25 A cont., 69 g", 28, "Robokits", "https://robokits.co.in/batteries-chargers/samsung-premium-li-ion-battery/3.7v-samsung-li-ion-batteries/samsung-21700-5000mah-inr21700-50s-45a-9c-li-ion-battery-original", 363.44, "incl. GST (₹308 ex)", "In stock", 0.069, "Molicel P45B (Robokits ₹481)", 481, "13S2P = 468 Wh, 50 A cont. vs 23 A peak demand; ₹20/Wh (26 + 2 spare)")
add("Power", "BMS", "JBD SP14S004 smart BMS 10-14S 40 A", "13S configured, Bluetooth, precharge-capable", 1, "lionbattery.in", "https://lionbattery.in/shop/shop/battery-bms/jbd-nmc-bms-hardware/", 2199, "incl. GST", "In stock (10)", 0.08, "Daly smart 13S 60 A (lionbattery ₹3,499)", 3499)
add("Power", "Pack build + test service", "lionbattery.in pack/BMS test service", "spot welding, capacity test", 1, "lionbattery.in", "https://lionbattery.in", 2000, "ESTIMATED from published service price", "Service", 0.10)
add("Power", "Battery connector", "Amass XT90-S anti-spark pair", "90 A", 1, "Robokits", "https://robokits.co.in/batteries-chargers/plugs-and-connectors/amass-xt90s-anti-spark-connectors-male-female-pair-original", 212.40, "incl. GST", "In stock", 0.02)
add("Power", "Motor-bus main switch", "Flipsky Anti-Spark Switch Smart Enhanced 300A V2.0", "12-84 V, 100 A cont., remote-able", 1, "Technobotix", "https://www.technobotix.in/products/flipsky-anti-spark-switch-smart-enhanced-300a-v2-0/1781252000001361046", 7499, "incl. GST", "In stock", 0.12, "custom MOSFET switch on hub PCB", 1500, "E-stop-controlled motor bus disconnect with precharge (no low-cost DC contactor in Indian retail)")
add("Power", "Emergency stop", "Schneider XB2BS8442C", "40 mm mushroom, twist release, 1NC", 1, "Moglix", "https://www.moglix.com/schneider-electric-xb2bs8442c-emergency-stop-mushroom-head-40mm-harmony-xb2-22mm-1nc-red/mp/msnr50n3q8x251", 399, "incl. GST", "In stock", 0.08, "LANBOO E-stop (Robu ₹374)", 374)
add("Power", "Branch fuses", "Littelfuse 0891030.NXS 30 A 58 V ATO", "58 V rated (suits 54.6 V bus)", 4, "Tanotis", "https://www.tanotis.com/products/littelfuse-0891030-nxs-auto-blade-fuse-30a-58v", 87.96, "incl. GST + duty", "Available", 0.003, "", "", "one per limb bus (32 V car fuses are NOT rated for 13S)")
add("Power", "Fuse holders", "30 A inline ATO holder, 12 AWG", "", 4, "lionbattery.in", "https://lionbattery.in/shop/shop/batteries-accessories/connectors/30a-inline-fuse-holder-with-12awg-wire-200mm-heavy-duty-fuse-cable/", 190, "incl. GST (₹161 ex)", "In stock (4)", 0.02)
add("Power", "Jetson 5 V supply", "Mean Well DDR-60L-5", "18-75 V in, 5 V 10.8 A isolated", 1, "IndustryBuying", "https://www.industrybuying.com/industrial-automation-accessories-mean-well-IND.IND.330812914", 4247, "incl. GST", "Ships in 15 days", 0.18, "6.5-60 V 10 A synchronous buck (ElectronicsComp ₹447)", 447, "isolated, brand-name supply for the computer")
add("Power", "12 V auxiliary supply", "6.5-60 V → adjustable 10 A synchronous buck", "neck servos, fans", 1, "ElectronicsComp", "https://www.electronicscomp.com/48v-36v-24v-to-19v-12v-9v-5v-3v-adjustable-synchronous-step-down-module-car-charging-power-supply", 447.22, "incl. GST", "In stock (8)", 0.05)
add("Power", "Charger", "54.6 V 6 A Li-ion charger (13S)", "", 1, "Quartz Components", "https://quartzcomponents.com", 3315, "listed price (GST basis not stated)", "In stock", 0.8)

# ------------------------------------------------------------------ upper body (phase 2 — structure estimated from CAD mass budget)
add("Torso", "Torso frame + battery bay", "JX1 torso (PA-CF prints + 2020 extrusion spine)", "~1.5 kg (prints ~40 h + 2 m 2020 extrusion + brackets)", 1, "In-house print + Robokits 2020", "https://robokits.co.in", 2600, "ESTIMATED print time + ₹341/m extrusion + hardware", "Make", 1.5, phase="2")
add("Arms", "Arm structures (upper arm, forearm, shoulder brackets) ×2", "JX1 arm set", "FDM PA-CF ~1.0 kg total (~36 h)", 1, "In-house Bambu P1S", "CAD/Arms", 540, "ESTIMATED print time @ ₹15/h", "Make", 1.0, phase="2")
add("Arms", "Simple grippers ×2", "JX1 parallel-jaw gripper (RS00-sized servo or bus servo)", "", 2, "In-house + Robu servo", "", 3500, "ESTIMATED", "Phase 3", 0.25, status="DEFERRED", phase="3")
add("Head", "Neck servos", "Waveshare ST3215 serial bus servo", "19.5 kg·cm @ 7.4 V, 12-bit encoder", 2, "Robu", "https://robu.in/product/waveshare-st3215-serial-bus-servo/", 2159, "incl. GST", "In stock", 0.055, "Genuine Feetech STS3215 (Amazon.in ₹4,415 each)", 4415, phase="2")
add("Head", "Bus-servo driver", "SmartElex serial bus servo driver board", "", 1, "Robu", "https://robu.in/", 509, "incl. GST", "In stock", 0.02, phase="2")
add("Head", "Stereo camera", "Waveshare IMX219-83 stereo", "2× 8 MP, 83° FOV, CSI", 1, "Robu", "https://robu.in/product/waveshare-imx219-83-stereo-camera-8mp-binocular-camera-module-depth-vision/", 6399, "incl. GST", "In stock", 0.04, "IMX219-77 mono (ThinkRobotics ₹1,700)", 1700, phase="2")
add("Head", "Head shell + neck brackets", "JX1 head", "FDM PETG-CF ~0.3 kg (~12 h)", 1, "In-house Bambu P1S", "CAD/Head", 180, "ESTIMATED print time @ ₹15/h", "Make", 0.3, phase="2")

# ------------------------------------------------------------------ manufacturing consumables (whole robot)
add("Manufacturing", "PA-CF filament", "eSUN PA-CF 1.75 mm 1 kg", "structural prints (legs, pelvis, torso, arms)", 5, "3Idea", "https://www.3idea.in/product-detail/esun-pa-cf-3d-printing-filament-black-1-75mm-net-weight-1kg", 4799, "listed price", "In stock", 1.0, "Numakers PETG-CF (≈₹1,356/kg incl.)", 1356, "stiffness/heat resistance for actuator mounts; ~4.6 kg structural prints + 20 % waste; printed-part rows carry print time only")
add("Manufacturing", "PETG-CF filament", "Numakers PETG-CF 1 kg", "covers, head, battery box", 3, "Numakers / 3D Master India", "https://3dmasterindia.in/product/petg-carbon-fiber-1-75mm/", 1356, "incl. GST (≈₹1,149 ex)", "In stock", 1.0)
add("Manufacturing", "Misc. consumables", "cable ties, spiral wrap, heat-shrink, drag chain 10×10, thread-locker", "", 1, "Quartz / Robokits", "https://robokits.co.in/3d-printer/accessories/cable-drag-chain-wire-carrier-with-end-connectors-10x10mm-1meter", 2500, "ESTIMATED", "In stock", 0.2)


def main():
    out = ROOT / "bom" / "master_bom.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ROWS[0].keys()))
        w.writeheader()
        w.writerows(ROWS)
    # ------------------------------------------------------------------ rollups
    by_sub, by_phase = {}, {}
    for r in ROWS:
        if r["Status"] in ("DEFERRED",):
            continue
        by_sub[r["Subsystem"]] = by_sub.get(r["Subsystem"], 0) + r["Total INR"]
        by_phase[r["Phase"]] = by_phase.get(r["Phase"], 0) + r["Total INR"]
    total = sum(by_sub.values())
    act = sum(r["Total INR"] for r in ROWS if r["Part"] == "Joint actuator")
    act_cny = sum(r["Alternative price INR"] * r["Quantity"] for r in ROWS if r["Part"] == "Joint actuator")
    lower_body = by_sub.get("Legs", 0) + by_sub.get("Pelvis", 0)
    top = sorted([r for r in ROWS if r["Status"] != "DEFERRED"], key=lambda r: -r["Total INR"])[:10]
    lines = [f"# JX1 cost summary (INR) — generated {DATE}", "",
             "Generated by `bom/build_bom.py` from `bom/master_bom.csv`. Imports use USD list × ₹95.96 × 1.323 duty × 1.07 shipping "
             "(ESTIMATED landed cost). Printed/machined parts are ESTIMATED until quotes are received.", "",
             "## Totals", "", "| Item | INR |", "|---|---:|"]
    for k in ("Legs", "Pelvis", "Electronics", "Power", "Torso", "Arms", "Head", "Manufacturing"):
        if k in by_sub:
            lines.append(f"| {k} | {by_sub[k]:,.0f} |")
    cont = 0.15 * total
    lines += [f"| **Robot total (excl. deferred grippers)** | **{total:,.0f}** |",
              f"| Prototype contingency 15 % | {cont:,.0f} |",
              f"| **Total with contingency** | **{total + cont:,.0f}** |", "",
              f"- **Lower body (legs + pelvis) = ₹{lower_body:,.0f}**; Phase 1 (lower body + compute + power + consumables) = ₹{by_phase.get('1', 0):,.0f}.",
              f"- Actuators = ₹{act:,.0f} (**{100 * act / total:.0f} %** of the robot).",
              f"- Buying the same RobStride units through a China distributor (CNY list, ₹{CNY_INR:.2f}/CNY, +5 % agent) = ₹{act_cny:,.0f} (saves ₹{act - act_cny:,.0f}).",
              f"- USD/INR {USD_INR}, duty {DUTY * 100:.2f} %, shipping {SHIP * 100:.0f} % (see script header for labels).", "",
              "## Top 10 cost lines (cost-reduction loop input)", "", "| # | ID | Part | Model | Qty | Total INR | Alternative | Alt. unit INR |", "|---|---|---|---|---:|---:|---|---:|"]
    for i, r in enumerate(top, 1):
        lines.append(f"| {i} | {r['ID']} | {r['Part']} | {r['Exact model']} | {r['Quantity']} | {r['Total INR']:,.0f} | {r['Alternative']} | {r['Alternative price INR']} |")
    (ROOT / "bom" / "cost_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
