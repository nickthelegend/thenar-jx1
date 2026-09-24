"""JX0 servo sizing: can hobby bus servos carry a 1.8 kg, 46 cm humanoid while it walks?

Same pipeline as the JX1 actuator sizing (calculations/run_leg_analysis.py), scaled to JX0:
jx0/design_point.yaml -> parametric MuJoCo model -> walking / turning / squat patterns (footsteps -> ZMP preview
control -> whole-body IK) and static single-leg poses -> floating-base inverse dynamics -> per-joint torque and speed.
Each leg joint is then checked against the servo (design_point.yaml actuator_classes.ST):
  peak     : 1.5 x dynamic peak (1.25 x static) <= stall torque
  thermal  : 1.3 x RMS torque while walking <= rated torque
  speed    : 1.5 x |torque| <= stall x (1 - |speed| / no-load speed) at every sample (linear torque-speed line)
Outputs jx0/results/sizing.json, sizing.md, sizing.png. Usage: .venv/Scripts/python jx0/analysis/sizing.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import mujoco  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "calculations"))
from jx1calc.design import Design, LEG_JOINTS  # noqa: E402
from jx1calc.gait import GaitParams, synthesize  # noqa: E402
from jx1calc.mjcf import build_mjcf  # noqa: E402
from run_leg_analysis import static_case  # noqa: E402

DESIGN = ROOT / "jx0" / "design_point.yaml"
OUT = ROOT / "jx0" / "results"
H = 0.222                                   # walking hip height: knees bent ~40 deg (leg length 0.235 m)
POLICY = {"dynamic_peak_factor": 1.5, "static_peak_factor": 1.25, "continuous_factor": 1.3, "torque_speed_factor": 1.5}


def gaits():
    sq0, sqT, sqA = 1.0, 1.6, 0.045

    def squat(t):
        return H - sqA * 0.5 * (1 - np.cos(2 * np.pi * (t - sq0) / sqT)) if sq0 <= t <= sq0 + sqT else H
    # Hobby servos are slow (no-load ~4.7 rad/s at 7.4 V): a 0.4 s step needs ~7 rad/s at the knee, so JX0 walks with
    # 0.55-0.6 s steps and 1.5 cm foot lift (sweep 2026-09-24: 5 cm / 0.6 s already reaches 96 % of the torque-speed line)
    common = dict(zmp_offset_x=0.005, hip_height=H, ds_ratio=0.25, step_height=0.015)
    return [
        GaitParams("walk_slow_0.05ms", step_length=0.030, step_time=0.60, n_steps=8, **common),
        GaitParams("walk_nominal_0.067ms", step_length=0.040, step_time=0.60, n_steps=10, **common),
        GaitParams("walk_fast_0.073ms", step_length=0.040, step_time=0.55, n_steps=10, **common),
        GaitParams("turn_10deg_per_step", step_length=0.015, step_time=0.60, n_steps=8, turn_per_step_deg=10.0, **common),
        GaitParams("squat_4.5cm_1.6s", n_steps=0, t_start=0.4, t_end=2.6, pelvis_height_profile=squat, **common),
    ]


def statics(d: Design):
    ya = d.hip_spacing / 2
    toe, heel, hw, m = d.foot_length - d.ankle_from_heel, d.ankle_from_heel, d.foot_width / 2, 0.005
    hs = 0.205                              # single-leg poses: the pelvis shifts over the stance foot, so it sits lower
    return [("stand_double", "both", (0.005, 0.0), H), ("stand_deep_squat", "both", (0.005, 0.0), 0.18),
            ("single_leg", "l", (0.005, ya), hs), ("single_leg_bent", "l", (0.005, ya), 0.19),
            ("single_leg_cop_toe", "l", (toe - m, ya), hs), ("single_leg_cop_heel", "l", (-(heel - m), ya), hs),
            ("single_leg_cop_outer_edge", "l", (0.005, ya + hw - m), hs),
            ("single_leg_cop_inner_edge", "l", (0.005, ya - hw + m), hs)]


def main():
    d = Design(DESIGN)
    servo = d.act_classes["ST"]
    stall, rated, w0 = servo["stall_torque_nm"], servo["rated_torque_nm"], servo["no_load_speed_rad_s"]
    OUT.mkdir(parents=True, exist_ok=True)
    model = mujoco.MjModel.from_xml_string(build_mjcf(d, with_actuators=False))
    dof = {j: model.jnt_dofadr[mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, f"l_{j}")] - 6 for j in LEG_JOINTS}
    dof_r = {j: model.jnt_dofadr[mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, f"r_{j}")] - 6 for j in LEG_JOINTS}

    per = {j: {"dyn_peak": 0.0, "dyn_scenario": "", "rms_walk": 0.0, "speed_peak": 0.0, "ts_util": 0.0, "ts_scenario": "",
               "static_peak": 0.0, "static_case": ""} for j in LEG_JOINTS}
    scen = []
    traces = {}
    for g in gaits():
        res = synthesize(model, d, g)
        tau, qvel = res["idr"]["tau"], res["qvel"][:, 6:]           # both indexed by actuated dof (floating base removed)
        zerr = res["zmp_error_history_m"][-1]
        row = {"scenario": g.name, "duration_s": float(res["t"][-1]), "zmp_error_mm": round(1000 * zerr, 2), "joints": {}}
        for j in LEG_JOINTS:
            for side_dof in (dof[j], dof_r[j]):
                t_ = np.abs(tau[:, side_dof])
                w_ = np.abs(qvel[:, side_dof])
                pk, rms, sp = float(t_.max()), float(np.sqrt(np.mean(tau[:, side_dof] ** 2))), float(w_.max())
                avail = stall * np.clip(1 - w_ / w0, 1e-3, None)
                util = float(np.max(POLICY["torque_speed_factor"] * t_ / avail))
                p = per[j]
                if pk > p["dyn_peak"]:
                    p["dyn_peak"], p["dyn_scenario"] = pk, g.name
                if g.name.startswith("walk"):
                    p["rms_walk"] = max(p["rms_walk"], rms)
                p["speed_peak"] = max(p["speed_peak"], sp)
                if util > p["ts_util"]:
                    p["ts_util"], p["ts_scenario"] = util, g.name
            row["joints"][j] = {"peak_nm": round(float(np.abs(tau[:, dof[j]]).max()), 3),
                                "rms_nm": round(float(np.sqrt(np.mean(tau[:, dof[j]] ** 2))), 3),
                                "speed_peak_rad_s": round(float(np.abs(qvel[:, dof[j]]).max()), 2)}
        scen.append(row)
        if g.name == "walk_nominal_0.067ms":
            traces = {"t": res["t"], **{j: tau[:, dof[j]] for j in LEG_JOINTS}}
        print(f"{g.name}: zmp error {1000 * zerr:.1f} mm", flush=True)

    for name, stance, cxy, hh in statics(d):
        sc = static_case(model, d, name, stance, cxy, hh, swing_lift=0.03)
        for j in LEG_JOINTS:
            v = abs(float(sc["tau"][dof[j]]))
            if v > per[j]["static_peak"]:
                per[j]["static_peak"], per[j]["static_case"] = v, name

    rows, ok_all = [], True
    for j in LEG_JOINTS:
        p = per[j]
        need_peak = max(POLICY["dynamic_peak_factor"] * p["dyn_peak"], POLICY["static_peak_factor"] * p["static_peak"])
        need_cont = POLICY["continuous_factor"] * p["rms_walk"]
        ok = need_peak <= stall and need_cont <= rated and p["ts_util"] <= 1.0
        ok_all &= ok
        rows.append({"joint": j, "dynamic_peak_nm": round(p["dyn_peak"], 3), "dynamic_scenario": p["dyn_scenario"],
                     "static_peak_nm": round(p["static_peak"], 3), "static_case": p["static_case"],
                     "required_peak_nm": round(need_peak, 3), "peak_margin": round(stall / need_peak, 2),
                     "rms_walk_nm": round(p["rms_walk"], 3), "required_continuous_nm": round(need_cont, 3),
                     "continuous_margin": round(rated / max(need_cont, 1e-9), 2),
                     "speed_peak_rad_s": round(p["speed_peak"], 2), "torque_speed_utilisation": round(p["ts_util"], 2),
                     "torque_speed_scenario": p["ts_scenario"], "pass": bool(ok)})
    summary = {"design": str(DESIGN.relative_to(ROOT)).replace("\\", "/"), "total_mass_kg": round(d.total_mass, 3),
               "servo": {k: servo[k] for k in ("product", "stall_torque_nm", "rated_torque_nm", "no_load_speed_rad_s", "label")},
               "policy": POLICY, "walking_hip_height_m": H, "joints": rows, "scenarios": scen, "all_pass": bool(ok_all),
               "label": "CALCULATED (servo data and masses ASSUMED until measured)"}
    (OUT / "sizing.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
    names = [r["joint"] for r in rows]
    ax[0].bar(names, [r["required_peak_nm"] for r in rows], color="#1f8fc9", label="required peak (1.5x dynamic / 1.25x static)")
    ax[0].axhline(stall, color="#f26b1d", lw=2, label=f"servo stall {stall} N·m")
    ax[0].axhline(rated, color="#888", ls="--", label=f"servo rated (assumed) {rated} N·m")
    ax[0].bar(names, [r["required_continuous_nm"] for r in rows], width=0.35, color="#0f1622", label="required continuous (1.3x RMS)")
    ax[0].set_ylabel("N·m")
    ax[0].set_title(f"JX0 leg servo requirements ({d.total_mass:.2f} kg)")
    ax[0].legend(fontsize=7)
    ax[0].tick_params(axis="x", rotation=30)
    if traces:
        for j in LEG_JOINTS:
            ax[1].plot(traces["t"], traces[j], lw=1, label=j)
        ax[1].set_title("left-leg joint torque, walking 0.067 m/s")
        ax[1].set_xlabel("s")
        ax[1].set_ylabel("N·m")
        ax[1].legend(fontsize=7, ncol=3)
    fig.tight_layout()
    fig.savefig(OUT / "sizing.png", dpi=130)

    md = [f"# JX0 servo sizing ({summary['label']})", "",
          f"Design `{summary['design']}`, total mass {d.total_mass:.2f} kg, walking hip height {H} m. Servo: {servo['product']}; "
          f"stall {stall} N·m, rated {rated} N·m (assumed 1/3 of stall), no-load {w0} rad/s.",
          "Checks: 1.5 x dynamic peak (1.25 x static) <= stall; 1.3 x walking RMS <= rated; 1.5 x torque within the "
          "linear torque-speed line at every sample.", "",
          "| Joint | Dynamic peak N·m (scenario) | Static peak N·m (case) | Required peak | Peak margin | Walking RMS | Continuous margin | Peak speed rad/s | Torque-speed use | Pass |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['joint']} | {r['dynamic_peak_nm']} ({r['dynamic_scenario']}) | {r['static_peak_nm']} ({r['static_case']}) | "
                  f"{r['required_peak_nm']} | {r['peak_margin']} | {r['rms_walk_nm']} | {r['continuous_margin']} | "
                  f"{r['speed_peak_rad_s']} | {int(100 * r['torque_speed_utilisation'])} % ({r['torque_speed_scenario']}) | "
                  f"{'yes' if r['pass'] else '**no**'} |")
    md += ["", "| Scenario | ZMP tracking error (mm) |", "|---|---|"] + [f"| {s['scenario']} | {s['zmp_error_mm']} |" for s in scen]
    md += ["", "![sizing](sizing.png)", ""]
    (OUT / "sizing.md").write_text("\n".join(md), encoding="utf-8")
    for r in rows:
        print(f"{r['joint']:12s} need {r['required_peak_nm']:.2f} of {stall} N·m (x{r['peak_margin']}), cont x{r['continuous_margin']}, "
              f"speed {r['speed_peak_rad_s']} rad/s, T-S {int(100 * r['torque_speed_utilisation'])} %  {'PASS' if r['pass'] else 'FAIL'}")
    print("ALL PASS" if ok_all else "SOME JOINTS FAIL")


if __name__ == "__main__":
    main()
