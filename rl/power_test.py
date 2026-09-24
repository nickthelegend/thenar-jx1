"""Electrical power, battery current and actuator thermal load of the learned gait, on the CAD model.

Same electrical model as calculations/run_power_budget.py (imported, so the numbers are comparable): per actuator
I = |tau| / Kt, P_cu = 3 I^2 R_phase, P_in = max(tau * omega, 0) + P_cu (no regeneration credit), plus actuator standby,
non-actuator loads through the DC-DC and the upper-body allowance. Joint torques and speeds come from constant-command
walks of the exported policy on the CAD model (rl/sim2sim.py CadSim, every physics step after the 2 s settle). The two
ankle motors per leg get their torques and speeds through the parallel linkage (ros2_ws/src/jx1_hw ankle.py, as the hubs).
Writes <policy>/power.json.
Usage: rl/.venv/Scripts/python rl/power_test.py [--policy rl/policies/jx1_walk_rough]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jx1_rl import DEFAULT_POLICY, REPO  # noqa: E402
from sim2sim import CadSim  # noqa: E402

sys.path.insert(0, str(REPO / "ros2_ws" / "src" / "jx1_hw"))
from jx1_hw.ankle import ParallelAnkle  # noqa: E402

SCENARIOS = [("stand", (0.0, 0.0, 0.0)), ("walk_0.3", (0.3, 0.0, 0.0)), ("walk_0.5", (0.5, 0.0, 0.0)), ("walk_0.8", (0.8, 0.0, 0.0)),
             ("turn_0.5", (0.0, 0.0, 0.5))]


def load_budget():
    if importlib.util.find_spec("pandas") is None:           # only its CSV reader needs pandas, not the actuator model
        import types
        sys.modules["pandas"] = types.ModuleType("pandas")
    spec = importlib.util.spec_from_file_location("jx1_power_budget", REPO / "calculations" / "run_power_budget.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default=str(DEFAULT_POLICY))
    ap.add_argument("--duration", type=float, default=10.0)
    a = ap.parse_args()
    pb = load_budget()
    pdir = Path(a.policy)
    sim = CadSim(pdir)
    hw = yaml.safe_load((REPO / "ros2_ws" / "src" / "jx1_hw" / "config" / "hw.yaml").read_text(encoding="utf-8"))
    ankles = {s: ParallelAnkle.from_params(hw["ankle"], s) for s in ("left", "right")}
    m = sim.m
    act = {sim.jname[i]: i for i in range(m.nu)}
    qadr = {j: m.jnt_qposadr[m.actuator_trnid[act[j], 0]] for j in act}
    dadr = {j: m.jnt_dofadr[m.actuator_trnid[act[j], 0]] for j in act}
    standby_w = sum(pb.V_NOM * pb.V(c["standby_current_A"]) * c["count"] for c in pb.CAT.values() if "standby_current_A" in c)
    non_act_w = sum(pb.NON_ACT.values()) / pb.DCDC_EFF
    out = {"policy": pdir.name, "model": "calculations/run_power_budget.py actuator model (Kt VERIFIED, R_phase ESTIMATED), no regeneration",
           "duration_s": a.duration, "scenarios": {}, "thermal": {}}
    for name, cmd in SCENARIOS:
        p_steps, i_sq, n = [], {}, 0

        def step(d, settled):
            nonlocal n
            if not settled:
                return
            p = 0.0
            for side in ("left", "right"):
                for j, cls in pb.LEG_CLASS.items():
                    jn = f"{side}_{j}_joint"
                    pj, ij = pb.actuator_power(np.array([d.actuator_force[act[jn]]]), np.array([d.qvel[dadr[jn]]]), cls)
                    p += float(pj[0])
                    i_sq[j] = i_sq.get(j, 0.0) + float(ij[0]) ** 2 / 2          # mean over both legs
                pa, ra = d.qpos[qadr[f"{side}_ankle_pitch_joint"]], d.qpos[qadr[f"{side}_ankle_roll_joint"]]
                ta, tb = ankles[side].motor_torque(pa, ra, d.actuator_force[act[f"{side}_ankle_pitch_joint"]],
                                                   d.actuator_force[act[f"{side}_ankle_roll_joint"]])
                wa, wb = ankles[side].jacobian(pa, ra) @ np.array([d.qvel[dadr[f"{side}_ankle_pitch_joint"]], d.qvel[dadr[f"{side}_ankle_roll_joint"]]])
                for tm, wm in ((ta, wa), (tb, wb)):
                    pj, ij = pb.actuator_power(np.array([tm]), np.array([wm]), pb.ANKLE_CLASS)
                    p += float(pj[0])
                    i_sq["ankle_motor"] = i_sq.get("ankle_motor", 0.0) + float(ij[0]) ** 2 / 4
            p_steps.append(p)
            n += 1
        r = sim.rollout(cmd, a.duration, step_cb=step)
        legs = np.array(p_steps)
        moving = name != "stand"
        total = legs + standby_w + non_act_w + pb.UPPER_BODY_W["walk" if moving else "stand"]
        out["scenarios"][name] = {"command": list(cmd), "fell": r["fell"], "achieved": r["mean_velocity_b"],
                                  "foot_liftoffs_per_s": r["foot_liftoffs_per_s"],
                                  "legs_mean_W": round(float(legs.mean()), 1), "mean_W": round(float(total.mean()), 1),
                                  "peak_W": round(float(total.max()), 1), "mean_current_A_at_nominal": round(float(total.mean() / pb.V_NOM), 2),
                                  "peak_current_A_at_min_V": round(float(total.max() / pb.V_MIN), 1)}
        for j, s in i_sq.items():
            cls = pb.LEG_CLASS.get(j, pb.ANKLE_CLASS)
            irms = float(np.sqrt(s / max(n, 1)))
            rated = pb.V(pb.CAT[cls]["rated_phase_current_Apk"]) / np.sqrt(2)
            prev = out["thermal"].get(j, {"worst_I_rms_A": 0.0})
            if irms > prev["worst_I_rms_A"]:
                out["thermal"][j] = {"class": cls, "worst_I_rms_A": round(irms, 2), "rated_I_rms_A": round(float(rated), 2),
                                     "utilisation": round(irms / rated, 2), "scenario": name}
        sc = out["scenarios"][name]
        print(f"{name:9s} {'FELL' if r['fell'] else 'ok  '} mean {sc['mean_W']:6.1f} W (legs {sc['legs_mean_W']:6.1f})  peak {sc['peak_W']:7.1f} W  "
              f"peak current {sc['peak_current_A_at_min_V']:5.1f} A at {pb.V_MIN:.1f} V", flush=True)
    pack = pb.PACKS["13S2P Samsung 50S (10.0 Ah, 2x25 A cont.)"]
    usable = 0.8 * pack["Ah"] * pb.V_NOM
    out["pack_13S2P_50S"] = {"usable_Wh_80pct": round(usable, 0), "cont_current_A": pack["I_cont"],
                             "runtime_h": {k: round(usable / v["mean_W"], 2) for k, v in out["scenarios"].items()},
                             "bms_rating_A": 40, "worst_peak_current_A": max(v["peak_current_A_at_min_V"] for v in out["scenarios"].values())}
    (pdir / "power.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out["pack_13S2P_50S"]), json.dumps(out["thermal"]))


if __name__ == "__main__":
    main()
