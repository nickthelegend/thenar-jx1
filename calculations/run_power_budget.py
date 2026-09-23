"""JX1 electrical power budget, battery sizing and actuator thermal check.

Inputs: gait timeseries from run_leg_analysis (per-joint torque & speed), actuators/actuator_catalog.yaml (VERIFIED Kt,
standby current; ESTIMATED phase resistance). Model per actuator (FOC, no regeneration credit — conservative):
    I_rms = |tau| / Kt,   P_cu = 3 I_rms^2 R_phase,   P_in = max(tau*omega, 0) + P_cu + V_bus * I_standby
Non-actuator loads (ASSUMED, documented below) are added through a DC-DC efficiency.

Usage: .venv/Scripts/python calculations/run_power_budget.py [--tag iter1_B_knee_and_pitch_RS04]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CAT = yaml.safe_load((ROOT / "actuators" / "actuator_catalog.yaml").read_text(encoding="utf-8"))["classes"]
V = lambda n: n["value"] if isinstance(n, dict) else n  # noqa: E731

LEG_CLASS = {"hip_yaw": "M", "hip_roll": "L", "hip_pitch": "XL", "knee": "XL"}
ANKLE_CLASS = "M"
NON_ACT = {  # W, ASSUMED (typical datasheet figures; refine when parts are bench-measured)
    "jetson_nano_10W_mode": 10.0, "can_hub_mcu": 1.0, "imu": 0.2, "camera": 1.5, "wifi_ethernet": 2.0,
    "fans_leds_misc": 2.0,
}
DCDC_EFF = 0.88
UPPER_BODY_W = {"walk": 20.0, "stand": 5.0}  # arms swing / waist hold allowance (CALCULATED from upper-body reqs, rounded up)
PACKS = {  # 13S configurations (cell data VERIFIED in research/raw/india_power_sourcing_raw.md)
    "13S1P Samsung 50S (5.0 Ah, 25 A cont.)": {"Ah": 5.0, "cells": 13, "I_cont": 25, "cell_kg": 0.069, "cell_inr": 363},
    "13S2P Molicel P45B (9.0 Ah, 2x45 A cont.)": {"Ah": 9.0, "cells": 26, "I_cont": 90, "cell_kg": 0.070, "cell_inr": 481},
    "13S2P Samsung 50S (10.0 Ah, 2x25 A cont.)": {"Ah": 10.0, "cells": 26, "I_cont": 50, "cell_kg": 0.069, "cell_inr": 363},
}
V_NOM, V_MIN = 13 * 3.6, 13 * 3.2


def actuator_power(tau, w, cls):
    c = CAT[cls]
    kt, r = V(c["torque_constant_Nm_per_Arms"]), V(c["phase_resistance_ohm"])
    i = np.abs(tau) / kt
    pcu = 3 * i ** 2 * r
    pmech = np.clip(tau * w, 0, None)
    return pmech + pcu, i


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="iter1_B_knee_and_pitch_RS04")
    a = ap.parse_args()
    res = HERE / "results" / a.tag
    standby_w = sum(V_NOM * V(c["standby_current_A"]) * V(c["count"]) if isinstance(c.get("count"), (int, float)) else 0
                    for k, c in CAT.items() if "standby_current_A" in c)
    standby_w = sum(V_NOM * V(c["standby_current_A"]) * c["count"] for k, c in CAT.items() if "standby_current_A" in c)
    non_act_w = sum(NON_ACT.values()) / DCDC_EFF
    out = {"assumptions": {"non_actuator_loads_W": NON_ACT, "dcdc_efficiency": DCDC_EFF, "upper_body_allowance_W": UPPER_BODY_W,
                           "bus_nominal_V": V_NOM, "bus_min_V": V_MIN, "actuator_standby_W": round(standby_w, 1),
                           "regeneration": "none credited (conservative)"}, "scenarios": {}, "thermal": {}}
    for f in sorted(res.glob("timeseries_*.csv")):
        name = f.stem.replace("timeseries_", "")
        df = pd.read_csv(f)
        t = df["t"].to_numpy()
        p = np.zeros(len(df))
        irms = {}
        for side in ("l", "r"):
            for j, cls in LEG_CLASS.items():
                pj, ij = actuator_power(df[f"{side}_{j}_tau"].to_numpy(), df[f"{side}_{j}_dq"].to_numpy(), cls)
                p += pj
                irms.setdefault(j, []).append(float(np.sqrt(np.mean(ij ** 2))))
            for m in ("A", "B"):  # ankle motors: left-leg series used for both legs (symmetric gait)
                pj, ij = actuator_power(df[f"l_ankle_motor{m}_tau"].to_numpy(), df[f"l_ankle_motor{m}_w"].to_numpy(), ANKLE_CLASS)
                p += pj
                irms.setdefault("ankle_motor", []).append(float(np.sqrt(np.mean(ij ** 2))))
        moving = not name.startswith("stand")
        p_total = p + standby_w + non_act_w + UPPER_BODY_W["walk" if moving else "stand"]
        out["scenarios"][name] = {"mean_W": round(float(p_total.mean()), 1), "peak_W": round(float(p_total.max()), 1),
                                  "legs_mean_W": round(float(p.mean()), 1), "mean_current_A_at_nominal": round(float(p_total.mean() / V_NOM), 2),
                                  "peak_current_A_at_min_V": round(float(p_total.max() / V_MIN), 1)}
        for j, v in irms.items():
            cls = LEG_CLASS.get(j, ANKLE_CLASS)
            rated = V(CAT[cls]["rated_phase_current_Apk"]) / np.sqrt(2)
            prev = out["thermal"].get(j, {"worst_I_rms_A": 0})
            if max(v) > prev["worst_I_rms_A"]:
                out["thermal"][j] = {"class": cls, "worst_I_rms_A": round(max(v), 2), "rated_I_rms_A": round(float(rated), 2),
                                     "utilisation": round(max(v) / rated, 2), "scenario": name}
    # standing: static double stance from the static-case table
    st = pd.read_csv(res / "static_cases.csv")
    row = st[st.case == "stand_double_nominal"].iloc[0]
    p_stand = 0.0
    for j, cls in LEG_CLASS.items():
        p_stand += 2 * actuator_power(np.array([row[f"{j}_Nm"]]), np.array([0.0]), cls)[0][0]
    p_stand += 4 * actuator_power(np.array([row["ankle_motor_Nm"]]), np.array([0.0]), ANKLE_CLASS)[0][0]
    p_stand_total = p_stand + standby_w + non_act_w + UPPER_BODY_W["stand"]
    out["scenarios"]["stand_idle"] = {"mean_W": round(float(p_stand_total), 1), "legs_mean_W": round(float(p_stand), 1)}
    # battery options
    walk = out["scenarios"]["walk_nominal_0.52ms"]["mean_W"]
    fast_peak = max(s.get("peak_W", 0) for s in out["scenarios"].values())
    out["packs"] = {}
    for n, pk in PACKS.items():
        wh = pk["Ah"] * V_NOM
        usable = 0.8 * wh
        out["packs"][n] = {"energy_Wh": round(wh, 0), "usable_Wh_80pct": round(usable, 0),
                           "runtime_walk_nominal_h": round(usable / walk, 2),
                           "runtime_standing_h": round(usable / p_stand_total, 2),
                           "cont_current_A": pk["I_cont"], "peak_demand_A_at_min_V": round(fast_peak / V_MIN, 1),
                           "current_margin": round(pk["I_cont"] / (fast_peak / V_MIN), 2),
                           "cell_mass_kg": round(pk["cells"] * pk["cell_kg"], 2), "cell_cost_inr": pk["cells"] * pk["cell_inr"]}
    (res / "power_budget.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
