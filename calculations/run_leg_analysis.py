"""JX1 lower-body torque / speed requirement analysis.

Pipeline: design_point.yaml -> parametric MuJoCo model -> gait & static scenarios -> floating-base
inverse dynamics -> per-joint torque/speed/power envelopes -> actuator requirements with documented
safety factors -> results/ (CSV, JSON, PNG, markdown report).

Usage: .venv/Scripts/python calculations/run_leg_analysis.py [--design path] [--tag iter0]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import mujoco  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from jx1calc.design import Design, LEG_JOINTS  # noqa: E402
from jx1calc.mjcf import build_mjcf  # noqa: E402
from jx1calc.gait import GaitParams, WholeBody, plan_steps, synthesize  # noqa: E402
from jx1calc.invdyn import finite_diff, inverse_dynamics  # noqa: E402
from jx1calc.ankle import ParallelAnkle  # noqa: E402

G = 9.81

# Requirement policy — every factor is an engineering assumption, documented in the report.
POLICY = {
    "dynamic_peak_factor": 1.5,     # RL-policy aggressiveness, disturbance rejection, touchdown impacts, model error
    "static_peak_factor": 1.25,     # mass growth / model error on quasi-static worst cases
    "continuous_factor": 1.3,       # thermal margin on RMS walking torque and indefinite standing torque
    "speed_factor": 1.3,            # headroom over the fastest analysed gait
    "speed_floor_rad_s": {"hip_yaw": 6.0, "hip_roll": 6.0, "hip_pitch": 10.0, "knee": 10.0,
                          "ankle_pitch": 8.0, "ankle_roll": 6.0},
    "note": "Floors guard against gaits faster than analysed (push recovery, RL exploration). ASSUMED; revisit with reference data.",
}


def dynamic_scenarios(d: Design):
    h = 0.54
    sq_t0, sq_T, sq_A = 1.0, 1.6, 0.20

    def squat_profile(t):
        if sq_t0 <= t <= sq_t0 + sq_T:
            return h - sq_A * 0.5 * (1 - np.cos(2 * np.pi * (t - sq_t0) / sq_T))
        return h

    return [
        GaitParams("walk_slow_0.30ms", step_length=0.15, step_time=0.50, step_height=0.04, hip_height=h, n_steps=8),
        GaitParams("walk_nominal_0.52ms", step_length=0.22, step_time=0.42, step_height=0.05, hip_height=h, n_steps=10),
        GaitParams("walk_fast_0.79ms", step_length=0.30, step_time=0.38, step_height=0.06, hip_height=h - 0.02, n_steps=10),
        GaitParams("turn_15deg_per_step", step_length=0.08, step_time=0.45, step_height=0.05, hip_height=h, n_steps=8,
                   turn_per_step_deg=15.0),
        GaitParams("squat_0.20m_1.6s", n_steps=0, hip_height=h, t_start=0.4, t_end=2.6, pelvis_height_profile=squat_profile),
    ]


def run_dynamic(model, d: Design, g: GaitParams):
    res = synthesize(model, d, g)
    return res, res["qvel"], res["qacc"], res["idr"]


def static_case(model, d: Design, name, stance, com_xy, hip_height, swing_lift=0.08, iters=8):
    """Quasi-static pose with the whole-body COM projected at com_xy; stance in {'both','l'}."""
    wb = WholeBody(model, d)
    w = d.hip_spacing
    feet = {"l": np.array([0.0, w / 2, d.sole_to_ankle]), "r": np.array([0.0, -w / 2, d.sole_to_ankle])}
    if stance == "l":
        feet["r"] = feet["r"] + np.array([0.0, 0.0, swing_lift])
    fy = {"l": 0.0, "r": 0.0}
    p = np.array([com_xy[0], com_xy[1], hip_height])
    for _ in range(iters):
        q = wb.ik(p, 0.0, feet, fy)
        qp = wb.set_state(p, 0.0, q)
        c = wb.com(qp)
        p[:2] += np.asarray(com_xy) - c[:2]
    contact = np.array([[True, stance == "both"]])
    z = np.zeros((1, model.nv))
    idr = inverse_dynamics(model, qp[None], z, z, contact)
    return {"name": name, "stance": stance, "qpos": qp, "q": q, "tau": idr["tau"][0], "cop": idr["cop"][0],
            "wrench": idr["wrench"][0], "com": wb.com(qp)}


def static_scenarios(d: Design):
    ya = d.hip_spacing / 2
    toe = d.foot_length - d.ankle_from_heel
    heel = d.ankle_from_heel
    half_w = d.foot_width / 2
    margin = 0.010
    return [
        ("stand_double_nominal", "both", (0.015, 0.0), 0.54),
        ("stand_double_deep_squat", "both", (0.015, 0.0), 0.34),
        ("single_leg_nominal", "l", (0.015, ya), 0.54),
        ("single_leg_bent_knee90", "l", (0.015, ya), 0.44),
        ("single_leg_cop_toe", "l", (toe - margin, ya), 0.50),
        ("single_leg_cop_heel", "l", (-(heel - margin), ya), 0.50),
        ("single_leg_cop_outer_edge", "l", (0.015, ya + half_w - margin), 0.50),
        ("single_leg_cop_inner_edge", "l", (0.015, ya - half_w + margin), 0.50),
        ("single_leg_cop_toe_outer_corner", "l", (toe - margin, ya + half_w - margin), 0.50),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--design", default=str(HERE / "design_point.yaml"))
    ap.add_argument("--tag", default="iter0")
    args = ap.parse_args()
    d = Design(args.design)
    out = HERE / "results" / args.tag
    out.mkdir(parents=True, exist_ok=True)
    xml = build_mjcf(d, with_actuators=False)
    (out / "jx1_analysis_model.xml").write_text(xml, encoding="utf-8")
    model = mujoco.MjModel.from_xml_string(xml)
    ankle = ParallelAnkle(d.crank_r, d.foot_lever, d.rod_half_spacing, d.ankle_motor_height)
    mass_rows = d.mass_table()
    total_mass = d.total_mass
    jn = [f"l_{j}" for j in LEG_JOINTS] + [f"r_{j}" for j in LEG_JOINTS]

    # ------------------------------------------------------------------ dynamic scenarios
    dyn_summary = {}
    ts_frames = {}
    envelopes = {j: [] for j in LEG_JOINTS + ["ankle_motor"]}
    for g in dynamic_scenarios(d):
        res, qvel, qacc, idr = run_dynamic(model, d, g)
        tau, qv = idr["tau"], qvel[:, 6:]
        q = res["qpos"][:, 7:]
        # joint-limit check
        lim_viol = []
        for k, name in enumerate(jn):
            jid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, name)
            lo, hi = model.jnt_range[jid]
            if q[:, k].min() < lo - 1e-6 or q[:, k].max() > hi + 1e-6:
                lim_viol.append(name)
        # ankle motor space (left leg)
        ia, ir = LEG_JOINTS.index("ankle_pitch"), LEG_JOINTS.index("ankle_roll")
        mt = np.array([ankle.motor_torques(q[i, ia], q[i, ir], tau[i, ia], tau[i, ir]) for i in range(len(q))])
        ms = np.array([ankle.motor_speeds(q[i, ia], q[i, ir], qv[i, ia], qv[i, ir]) for i in range(len(q))])
        s = {}
        for k, j in enumerate(LEG_JOINTS):
            both = np.r_[tau[:, k], tau[:, k + 6]]
            vel = np.r_[qv[:, k], qv[:, k + 6]]
            pw = np.r_[tau[:, k] * qv[:, k], tau[:, k + 6] * qv[:, k + 6]]
            s[j] = {"peak_torque_Nm": float(np.abs(both).max()), "rms_torque_Nm": float(np.sqrt(np.mean(tau[:, k] ** 2))),
                    "peak_speed_rad_s": float(np.abs(vel).max()), "peak_power_W": float(np.abs(pw).max()),
                    "min_angle_deg": float(np.degrees(q[:, k].min())), "max_angle_deg": float(np.degrees(q[:, k].max()))}
            envelopes[j].append(np.c_[np.abs(vel), np.abs(both)])
        s["ankle_motor"] = {"peak_torque_Nm": float(np.abs(mt).max()), "rms_torque_Nm": float(np.sqrt(np.mean(mt ** 2, axis=0)).max()),
                            "peak_speed_rad_s": float(np.abs(ms).max()), "peak_power_W": float(np.abs(mt * ms).max())}
        envelopes["ankle_motor"].append(np.c_[np.abs(ms).ravel(), np.abs(mt).ravel()])
        total_pw = (tau * qv).sum(axis=1)
        positive = np.clip(tau * qv, 0, None).sum(axis=1)
        dur = res["t"][-1] - res["t"][0]
        dist = res["plan"].feet["l"][-1, 0]
        cop = idr["cop"]
        fr = idr["friction"]
        foot_ok = np.nanmax(np.abs(cop[..., 1])) <= d.foot_width / 2 and \
            np.nanmax(cop[..., 0]) <= d.foot_length - d.ankle_from_heel and np.nanmin(cop[..., 0]) >= -d.ankle_from_heel
        dyn_summary[g.name] = {
            "params": {k: v for k, v in g.__dict__.items() if k != "pelvis_height_profile"},
            "speed_m_s": float(g.step_length / g.step_time) if g.n_steps else 0.0,
            "zmp_error_history_m": res["zmp_error_history_m"],
            "joints": s,
            "joint_limit_violations": lim_viol,
            "mean_positive_mech_power_W": float(positive.mean()),
            "peak_total_mech_power_W": float(np.abs(total_pw).max()),
            "cop_inside_feet": bool(foot_ok),
            "max_cop_x_m": float(np.nanmax(cop[..., 0])), "min_cop_x_m": float(np.nanmin(cop[..., 0])),
            "max_abs_cop_y_m": float(np.nanmax(np.abs(cop[..., 1]))),
            "max_friction_ratio_per_foot": float(np.nanmax(fr)),
            "max_total_friction_ratio": float(np.nanmax(np.hypot(*(idr["wrench"][:, 0, :2] + idr["wrench"][:, 1, :2]).T)
                                                        / (idr["wrench"][:, 0, 2] + idr["wrench"][:, 1, 2]))),
            "zc_m": float(res["zc"]),
        }
        df = pd.DataFrame({"t": res["t"]})
        for k, name in enumerate(jn):
            df[f"{name}_q"] = q[:, k]
            df[f"{name}_dq"] = qv[:, k]
            df[f"{name}_tau"] = tau[:, k]
        df["l_ankle_motorA_tau"], df["l_ankle_motorB_tau"] = mt[:, 0], mt[:, 1]
        df["l_ankle_motorA_w"], df["l_ankle_motorB_w"] = ms[:, 0], ms[:, 1]
        df["com_ref_x"], df["com_ref_y"] = res["com_ref"][:, 0], res["com_ref"][:, 1]
        df["zmp_ref_x"], df["zmp_ref_y"] = res["plan"].zmp_ref[:, 0], res["plan"].zmp_ref[:, 1]
        df["contact_l"], df["contact_r"] = res["plan"].contact[:, 0], res["plan"].contact[:, 1]
        df.to_csv(out / f"timeseries_{g.name}.csv", index=False, float_format="%.6g")
        ts_frames[g.name] = (res, df, idr)
        print(f"[dyn] {g.name}: " + ", ".join(f"{j}={s[j]['peak_torque_Nm']:.1f}Nm/{s[j]['peak_speed_rad_s']:.1f}rad/s" for j in LEG_JOINTS)
              + f", ankle_motor={s['ankle_motor']['peak_torque_Nm']:.1f}Nm; limits_ok={not lim_viol}; cop_ok={foot_ok}", flush=True)

    # ------------------------------------------------------------------ static scenarios
    static_rows = []
    for name, stance, com_xy, hh in static_scenarios(d):
        r = static_case(model, d, name, stance, com_xy, hh)
        t6 = r["tau"][:6]
        q6 = r["q"]["l"]
        mt = ankle.motor_torques(q6[4], q6[5], t6[4], t6[5])
        row = {"case": name, "stance": stance, "hip_height_m": hh, "com_x": round(float(r["com"][0]), 4), "com_y": round(float(r["com"][1]), 4)}
        for k, j in enumerate(LEG_JOINTS):
            row[f"{j}_Nm"] = round(float(max(abs(r["tau"][k]), abs(r["tau"][k + 6]) if stance == "both" else abs(r["tau"][k]))), 3)
            row[f"{j}_deg"] = round(float(np.degrees(q6[k])), 2)
        row["ankle_motor_Nm"] = round(float(np.abs(mt).max()), 3)
        static_rows.append(row)
        print(f"[static] {name}: " + ", ".join(f"{j}={row[f'{j}_Nm']:.1f}" for j in LEG_JOINTS) + f", ankle_motor={row['ankle_motor_Nm']:.1f}", flush=True)
    static_df = pd.DataFrame(static_rows)
    static_df.to_csv(out / "static_cases.csv", index=False)

    # ------------------------------------------------------------------ requirements
    req = {}
    walk_names = [n for n in dyn_summary if n.startswith("walk")]
    for j in LEG_JOINTS + ["ankle_motor"]:
        dyn_pk = max(dyn_summary[n]["joints"][j]["peak_torque_Nm"] for n in dyn_summary)
        dyn_sp = max(dyn_summary[n]["joints"][j]["peak_speed_rad_s"] for n in dyn_summary)
        rms = max(dyn_summary[n]["joints"][j]["rms_torque_Nm"] for n in walk_names)
        col = f"{j}_Nm"
        st_pk = float(static_df[col].max())
        st_stand = float(static_df.loc[static_df.case == "stand_double_nominal", col].iloc[0])
        floor = POLICY["speed_floor_rad_s"].get(j, POLICY["speed_floor_rad_s"]["ankle_pitch"])
        req[j] = {
            "dynamic_peak_torque_Nm": round(dyn_pk, 2),
            "static_peak_torque_Nm": round(st_pk, 2),
            "walking_rms_torque_Nm": round(rms, 2),
            "standing_torque_Nm": round(st_stand, 2),
            "peak_speed_rad_s": round(dyn_sp, 2),
            "REQ_peak_torque_Nm": round(max(POLICY["dynamic_peak_factor"] * dyn_pk, POLICY["static_peak_factor"] * st_pk), 1),
            "REQ_continuous_torque_Nm": round(POLICY["continuous_factor"] * max(rms, st_stand), 1),
            "REQ_speed_rad_s": round(max(POLICY["speed_factor"] * dyn_sp, floor), 1),
            "label": "CALCULATED (parametric model iteration " + args.tag + ")",
        }
    summary = {"design_file": str(Path(args.design).relative_to(HERE.parent)), "tag": args.tag, "total_mass_kg": round(total_mass, 3),
               "mass_table": mass_rows, "policy": POLICY, "dynamic": dyn_summary, "requirements": req}
    (out / "summary.json").write_text(json.dumps(summary, indent=2, default=float), encoding="utf-8")
    (out / "requirements.yaml").write_text(yaml.safe_dump({"leg_joint_requirements": req, "policy": POLICY}, sort_keys=False), encoding="utf-8")

    # ------------------------------------------------------------------ plots
    colors = ["#1f5fa8", "#d1495b", "#2e933c", "#edae49", "#6c4f9e", "#00798c"]
    res, df, idr = ts_frames["walk_nominal_0.52ms"]
    fig, axs = plt.subplots(6, 2, figsize=(13, 15), sharex=True)
    for k, j in enumerate(LEG_JOINTS):
        axs[k, 0].plot(df.t, np.degrees(df[f"l_{j}_q"]), color=colors[k])
        axs[k, 0].set_ylabel(f"{j}\nangle [deg]")
        axs[k, 1].plot(df.t, df[f"l_{j}_tau"], color=colors[k])
        axs[k, 1].set_ylabel("torque [N·m]")
        for a in axs[k]:
            a.grid(alpha=.3)
            for i0 in np.where(np.diff(df.contact_l.astype(int)) != 0)[0]:
                a.axvline(df.t[i0], color="k", alpha=.12)
    axs[-1, 0].set_xlabel("t [s]")
    axs[-1, 1].set_xlabel("t [s]")
    fig.suptitle(f"JX1 left leg — nominal walk 0.52 m/s (iteration {args.tag})")
    fig.tight_layout()
    fig.savefig(out / "walk_nominal_left_leg.png", dpi=110)
    plt.close(fig)

    fig, axs = plt.subplots(2, 4, figsize=(16, 7.5))
    for ax, j in zip(axs.ravel(), LEG_JOINTS + ["ankle_motor"]):
        for n, e in zip(dyn_summary, envelopes[j]):
            ax.scatter(e[:, 0], e[:, 1], s=2, alpha=.35, label=n)
        r = req[j]
        ax.plot([0, r["REQ_speed_rad_s"], r["REQ_speed_rad_s"]], [r["REQ_peak_torque_Nm"], r["REQ_peak_torque_Nm"], 0], "k--", lw=1.2)
        ax.axhline(r["REQ_continuous_torque_Nm"], color="r", ls=":", lw=1.2)
        ax.set_title(j)
        ax.set_xlabel("|speed| [rad/s]")
        ax.set_ylabel("|torque| [N·m]")
        ax.grid(alpha=.3)
    axs.ravel()[-1].axis("off")
    axs.ravel()[0].legend(fontsize=7, markerscale=4)
    fig.suptitle("Joint torque–speed demand (all dynamic cases); dashed = peak requirement box, dotted red = continuous requirement")
    fig.tight_layout()
    fig.savefig(out / "torque_speed_envelopes.png", dpi=110)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    plan = res["plan"]
    ax.plot(df.zmp_ref_x, df.zmp_ref_y, "k-", lw=1, label="ZMP reference")
    ax.plot(res["com_ref"][:, 0], res["com_ref"][:, 1], "-", color="#d1495b", lw=1.6, label="CoM (LIPM preview control)")
    for s, c in (("l", "#1f5fa8"), ("r", "#2e933c")):
        f = plan.feet[s]
        on = plan.contact[:, 0 if s == "l" else 1]
        starts = np.where(np.diff(on.astype(int)) == 1)[0] + 1
        for i in np.r_[0, starts]:
            x, y = f[i, 0], f[i, 1]
            ax.add_patch(plt.Rectangle((x - d.ankle_from_heel, y - d.foot_width / 2), d.foot_length, d.foot_width, fill=False, ec=c))
    ax.set_aspect("equal")
    ax.legend(loc="upper left", fontsize=8)
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("Footprints, ZMP reference and CoM — nominal walk")
    fig.tight_layout()
    fig.savefig(out / "walk_nominal_footprints_zmp_com.png", dpi=110)
    plt.close(fig)

    # ------------------------------------------------------------------ report
    lines = [f"# JX1 leg torque/speed analysis — iteration `{args.tag}`", "",
             "Generated by `calculations/run_leg_analysis.py` from `" + summary["design_file"] + "`. Label: **CALCULATED** "
             "from a parametric rigid-body model with ASSUMED masses; not measured.", "",
             f"Total modelled mass: **{total_mass:.2f} kg**.", "", "## Mass model", "",
             "| Link | Count | Mass each [kg] | COM [m] |", "|---|---:|---:|---|"]
    for r in mass_rows:
        lines.append(f"| {r['link']} | {r['count']} | {r['mass_each_kg']:.3f} | {r['com_m']} |")
    lines += ["", "## Dynamic scenarios", "",
              "| Scenario | Speed [m/s] | CoP in feet | max total friction ratio | mean +mech power [W] | limit violations |", "|---|---:|---|---:|---:|---|"]
    for n, s in dyn_summary.items():
        lines.append(f"| {n} | {s['speed_m_s']:.2f} | {s['cop_inside_feet']} | {s['max_total_friction_ratio']:.2f} | {s['mean_positive_mech_power_W']:.1f} | {', '.join(s['joint_limit_violations']) or 'none'} |")
    lines += ["", "Peak |torque| [N·m] / peak |speed| [rad/s] per joint:", "",
              "| Scenario | " + " | ".join(LEG_JOINTS + ["ankle motor"]) + " |", "|---|" + "---:|" * 7]
    for n, s in dyn_summary.items():
        lines.append(f"| {n} | " + " | ".join(f"{s['joints'][j]['peak_torque_Nm']:.1f} / {s['joints'][j]['peak_speed_rad_s']:.1f}" for j in LEG_JOINTS + ["ankle_motor"]) + " |")
    lines += ["", "## Static scenarios (|torque| N·m)", "", static_df.to_markdown(index=False) if hasattr(static_df, "to_markdown") else static_df.to_string(index=False), "",
              "## Requirements (policy applied)", "",
              f"Peak = max({POLICY['dynamic_peak_factor']} × dynamic peak, {POLICY['static_peak_factor']} × static peak); "
              f"continuous = {POLICY['continuous_factor']} × max(walking RMS, nominal standing); speed = max({POLICY['speed_factor']} × peak, floor).", "",
              "| Joint | dyn peak | static peak | RMS walk | stand | peak speed | **REQ peak** | **REQ cont.** | **REQ speed** |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for j, r in req.items():
        lines.append(f"| {j} | {r['dynamic_peak_torque_Nm']} | {r['static_peak_torque_Nm']} | {r['walking_rms_torque_Nm']} | {r['standing_torque_Nm']} | {r['peak_speed_rad_s']} | **{r['REQ_peak_torque_Nm']}** | **{r['REQ_continuous_torque_Nm']}** | **{r['REQ_speed_rad_s']}** |")
    lines += ["", "![torque-speed](torque_speed_envelopes.png)", "", "![walk](walk_nominal_left_leg.png)", "", "![zmp](walk_nominal_footprints_zmp_com.png)", ""]
    (out / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({j: {k: v for k, v in r.items() if k.startswith("REQ")} for j, r in req.items()}, indent=1))


if __name__ == "__main__":
    main()
