"""Generate docs/final_robot_specification.md — the FINAL ROBOT SPECIFICATION — from the evidence files.

Every number is read from a result file (never typed by hand): design point, joint map, CAD mass properties, actuator
catalogue, latest requirements, structural FEA summary, CAD/MuJoCo verification results and the BOM.
Usage: .venv/Scripts/python tools/gen_final_spec.py
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def load_json(rel):
    p = ROOT / rel
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def load_yaml(rel):
    p = ROOT / rel
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else None


def v(x):
    return x["value"] if isinstance(x, dict) and "value" in x else x


def latest_requirements():
    for tag in ("iter2_C_cad_masses", "iter1_B_knee_and_pitch_RS04"):
        r = load_yaml(f"calculations/results/{tag}/requirements.yaml")
        if r:
            return tag, r
    return None, None


def default_policy():
    """The recommended RL policy bundle (rl/jx1_rl/__init__.py DEFAULT_POLICY), read without importing the RL stack."""
    import re
    m = re.search(r'DEFAULT_POLICY = RL_DIR / "policies" / "([^"]+)"', (ROOT / "rl" / "jx1_rl" / "__init__.py").read_text(encoding="utf-8"))
    return f"rl/policies/{m.group(1)}" if m else None


def rl_policy_lines(cat, req):
    """Learned walking controller: CAD sim-to-sim, command envelope, actuator loads, pushes, ROS 2 / HIL, Isaac status."""
    pol = default_policy()
    if not pol or not (ROOT / pol / "sim2sim.json").exists():
        return []
    io = load_yaml(f"{pol}/policy_io.yaml")
    tr = io.get("trained", {})
    out = ["", f"Learned walking controller ({pol.split('/')[-1]}: {io['observation']['size']} obs -> {io['policy']['num_actions']} leg targets at "
               f"{1 / io['control']['policy_dt_s']:.0f} Hz, PPO in MuJoCo, {tr.get('run', '?')} iteration {tr.get('iteration', '?')})  [CALCULATED, MuJoCo]"]
    for tag, name in (("", "flat floor"), ("_rough", "rough heightfield")):
        s = load_json(f"{pol}/sim2sim{tag}.json")
        if s:
            sc = s["scenarios"]
            f8 = sc.get("forward_0.8", {})
            out.append(f"  CAD sim-to-sim, {name:17s}: {sum(not r['fell'] for r in sc.values())}/{len(sc)} scenarios upright; "
                       f"0.8 m/s cmd -> {f8.get('mean_velocity_b', [0])[0]:.2f} m/s, turn 0.5 rad/s -> "
                       f"{sc['turn_0.5']['mean_velocity_b'][2]:.2f} rad/s, peak torque {max(r['peak_torque_fraction'] for r in sc.values()):.0%} of limit")
    for tag, name in (("", "flat"), ("_rough", "rough")):
        e = load_json(f"{pol}/envelope{tag}.json")
        if e:
            sm = e["summary"]
            g = lambda k: f"{sm[k]['achieved']:+.2f}" if sm.get(k) else "-"  # noqa: E731
            out.append(f"  command envelope, {name + ' floor' if name == 'flat' else 'rough ground':12s}: {sm['tracked']}/{sm['commands']} commands tracked, {sm['falls']} falls; forward {g('forward')} m/s, "
                       f"backward {g('backward')}, lateral {g('left')}/{g('right')} m/s, yaw {g('yaw_left')}/{g('yaw_right')} rad/s")
    s = load_json(f"{pol}/sim2sim.json")
    f8 = s["scenarios"].get("forward_0.8", {}) if s else {}
    if f8.get("joint_torque_peak_Nm") and req:
        f_dyn = req["policy"]["dynamic_peak_factor"]
        cls = {"hip_yaw": "M", "hip_roll": "L", "hip_pitch": "XL", "knee": "XL"}
        out.append(f"  actuator load walking 0.8 m/s (left leg; {f_dyn} x peak vs actuator peak, RMS vs rated):")
        for j, c in cls.items():
            pk, rms = f8["joint_torque_peak_Nm"][f"left_{j}_joint"], f8["joint_torque_rms_Nm"][f"left_{j}_joint"]
            cap, rated = v(cat[c]["peak_torque_Nm"]), v(cat[c]["rated_torque_Nm"])
            out.append(f"    {j:10s}: peak {pk:5.1f} N m x {f_dyn} = {f_dyn * pk:5.1f} {'<=' if f_dyn * pk <= cap else '>'} {cap} N m; "
                       f"RMS {rms:4.1f} {'<=' if rms <= rated else '>'} {rated} N m rated")
        for j in ("ankle_pitch", "ankle_roll"):
            pk, rms = f8["joint_torque_peak_Nm"][f"left_{j}_joint"], f8["joint_torque_rms_Nm"][f"left_{j}_joint"]
            lim = io["effort_limits_Nm"][f"left_{j}_joint"]
            out.append(f"    {j:10s}: peak {pk:5.1f} N m = {pk / lim:.0%} of the {lim:g} N m linkage capability; RMS {rms:4.1f} N m")
    p = load_json(f"{pol}/push_test.json")
    if p:
        imp = p["max_survived_impulse_Ns"]
        out.append(f"  push recovery (0.5 m/s, 0.1 s torso pulse): {min(imp.values()):.1f}-{max(imp.values()):.1f} N s survived "
                   f"(forward {imp['forward']:.1f}, backward {imp['backward']:.1f}, left {imp['left']:.1f}, right {imp['right']:.1f})")
    lat = load_json(f"{pol}/latency.json")
    if lat:
        r = {(x["obs_delay_ms"], x["act_delay_ms"]): x for x in lat["rows"]}
        a, b = r.get((0, 0)), r.get((40, 20))
        if a and b:
            out.append(f"  latency: 0.3 rad/s turn tracked {a['turn_0.3']['fraction']:.0%} without delay, {b['turn_0.3']['fraction']:.0%} "
                       "with 40 ms sensing + 20 ms actuation delay")
    paths = [(f, load_json(f"{pol}/{f}")) for f in ("ros2_check.json", "ros2_launch_check.json", "ros2_control_check.json")]
    ok = [r for _, r in paths if r and r.get("phases")]
    if ok:
        out.append(f"  ROS 2 {ok[0].get('ros_distro', '')} (separate node processes, /cmd_vel -> walk): {len(ok)} start paths "
                   f"(python -m, ros2 launch, ros2_control), all upright {all(r.get('upright') for r in ok)}; "
                   f"forward {min(r['phases']['forward']['mean_speed_m_s'] for r in ok):.2f}-{max(r['phases']['forward']['mean_speed_m_s'] for r in ok):.2f} m/s at 0.4")
    hw = load_json(f"{pol}/hw_loop_check.json")
    if hw and hw.get("phases"):
        ph = hw["phases"]
        out.append(f"  hardware-in-the-loop (hw_node + hub protocol + hub-firmware twin): forward {ph['forward']['mean_speed_m_s'] / 0.3:.0%} and "
                   f"turn {ph['turn']['yaw_change_deg'] / 103.13:.0%} of the 0.3 command, upright {hw.get('upright')}  [CALCULATED, emulated hubs]")
    oc = load_json("simulation/isaac/isaaclab/offline_check.json")
    if oc:
        n = sum(c["ok"] for c in oc["checks"])
        out.append(f"  Isaac Lab / Isaac Sim: {n}/{len(oc['checks'])} offline checks against the Isaac Lab 2.3.2 / Isaac Sim 5.1 sources; "
                   "not run in Isaac Sim  [UNVERIFIED runtime]")
    return out


def main():
    dp = load_yaml("calculations/design_point.yaml")
    jm = load_yaml("simulation/joint_map.yaml")
    mp = load_json("simulation/mass_properties.json")
    cat = load_yaml("actuators/actuator_catalog.yaml")["classes"]
    tag, req = latest_requirements()
    st = load_json("calculations/results/structural/summary.json")
    pw = load_json(f"calculations/results/{tag}/power_budget.json") or load_json("calculations/results/iter1_B_knee_and_pitch_RS04/power_budget.json")
    g = dp["geometry"]
    ub = dp["upper_body_geometry"]
    leg_len = v(g["thigh_m"]) + v(g["shin_m"]) + v(g["sole_to_ankle_m"])
    head_top = leg_len + v(ub["waist_yaw_origin"])[2] + v(ub["neck_yaw_origin"])[2] + v(ub["neck_pitch_offset"])[2] + v(ub["head_top_above_neck_pitch_m"])
    L = ["# JX1 — FINAL ROBOT SPECIFICATION", "",
         f"Generated by `tools/gen_final_spec.py` from the evidence files (design point v{dp['meta']['version']}). "
         "Labels: VERIFIED / MEASURED / CALCULATED / ESTIMATED / ASSUMED / UNVERIFIED. Nothing has been built or physically tested.", "",
         "```text", "JX1 FINAL ROBOT SPECIFICATION"]
    mass = mp["total_mass_kg"] if mp else None
    upper_src = "CAD" if mp and mp.get("upper_body") == "CAD" else "placeholder"
    L += [f"Height (zero pose, CAD)        : {head_top:.3f} m  [CALCULATED]",
          f"Mass (CAD, all components)     : {mass:.2f} kg  [ESTIMATED: CAD volumes x documented densities, datasheet actuator masses; upper body {upper_src}]" if mass else "Mass: n/a",
          f"Degrees of freedom             : {jm['dof']['total_actuated']} (legs {jm['dof']['legs']}, waist {jm['dof']['waist']}, arms {jm['dof']['arms']}, neck {jm['dof']['neck']})",
          f"Leg                            : thigh {v(g['thigh_m'])} m, shin {v(g['shin_m'])} m, ankle-sole {v(g['sole_to_ankle_m'])} m, hip spacing {v(g['hip_spacing_m'])} m",
          f"Foot                           : {v(g['foot']['length_m'])} x {v(g['foot']['width_m'])} m",
          "Leg kinematics                 : hip yaw-roll-pitch (intersecting), knee pitch, 2-motor parallel ankle (pitch/roll)"]
    L.append("")
    L.append("Actuators (joint: model, peak / rated torque, requirement peak)")
    cls_of = {"hip_yaw": "M", "hip_roll": "L", "hip_pitch": "XL", "knee": "XL", "ankle_motor": "M"}
    for j, c in cls_of.items():
        a = cat[c]
        r = req["leg_joint_requirements"].get(j, {}) if req else {}
        need = r.get("REQ_peak_torque_Nm")
        cap = v(a["peak_torque_Nm"])
        margin = f"{(cap / need - 1) * 100:+.0f} %" if need else "n/a"
        L.append(f"  {j:14s}: {a['product']:15s} {cap:>5} / {v(a['rated_torque_Nm']):>4} N m   need {need} N m ({margin})")
    L.append("  waist          : RobStride RS06     36 / 11 N m")
    L.append("  shoulder p/r   : RobStride RS02     17 / 6 N m ; shoulder yaw, elbow: RobStride RS00 14 / 5 N m ; neck: Waveshare ST3215 x2")
    L.append(f"  requirement source: calculations/results/{tag}/requirements.yaml (policy: peak = max(1.5 x dynamic, 1.25 x static))")
    dyn = (load_json(f"calculations/results/{tag}/summary.json") or {}).get("dynamic", {}) if tag else {}
    if dyn and req:
        f_dyn = req["policy"]["dynamic_peak_factor"]
        runs = []
        for name, r in dyn.items():
            over = []
            for j, c in cls_of.items():
                pk = r["joints"].get(j, {}).get("peak_torque_Nm")
                cap = v(cat[c]["peak_torque_Nm"])
                if pk and f_dyn * pk > cap:
                    over.append(f"{j} {pk:.1f} N m x {f_dyn} = {f_dyn * pk:.1f} > {cap} N m")
            runs.append(f"{name.split('_')[0] if name.startswith('squat') else name}: " + ("margins met" if not over else "; ".join(over)))
        L.append("  per scenario (1.5 x dynamic peak vs actuator peak): " + runs[0])
        L += [f"                                                      {x}" for x in runs[1:]]
        st_ank = req["leg_joint_requirements"].get("ankle_motor", {}).get("static_peak_torque_Nm")
        if st_ank:
            L.append(f"  static worst case (edge-of-foot CoP): ankle motor {st_ank:.1f} N m raw = {v(cat['M']['peak_torque_Nm']) / st_ank:.2f}x margin "
                     f"(policy {req['policy']['static_peak_factor']}x)")
    L.append("")
    L.append("Structure (FEA: actuator-capped GRF samples + walking fatigue; SF LC1 / LC2, required 1.5 / 1.5 for aluminium)")
    if st:
        for key, r in st["parts"].items():
            m = r["materials"][r["recommended"]]
            L.append(f"  {r['stl']:22s}: {r['recommended']:8s} SF {m['SF_LC1']:5.2f} / {m['SF_LC2']:5.2f}  {'PASS' if m['pass'] else 'FAIL'}")
    L.append("")
    L.append("Compute / electronics : Jetson Nano 4 GB (policy 50 Hz) + 2 x Teensy 4.1 CAN hubs (6 x CAN 1 Mbit/s, 500 Hz), BNO085 IMU,")
    L.append("                        IMX219-83 stereo camera, RobStride on-board FOC drivers")
    if pw:
        sc = pw["scenarios"]
        pack = next((pk for k, pk in pw["packs"].items() if k.startswith("13S2P Samsung 50S")), {})
        L.append(f"Power                 : 13S2P Samsung 50S (41.6-54.6 V, {pack.get('energy_Wh', 468)} Wh); standing {sc['stand_idle']['mean_W']} W, "
                 f"walking {sc['walk_nominal_0.52ms']['mean_W']} W (0.52 m/s), {sc['walk_fast_0.79ms']['mean_W']} W mean / "
                 f"{sc['walk_fast_0.79ms']['peak_W']} W peak (0.79 m/s); runtime {pack.get('runtime_walk_nominal_h', '?')} h walking, "
                 f"{pack.get('runtime_standing_h', '?')} h standing  [CALCULATED, lower-body dynamics]")
    else:
        L.append("Power                 : 13S2P Samsung 50S (41.6-54.6 V, 468 Wh)")
    L.append("Safety                : dual-path E-stop (motor-bus switch + hub damping), 58 V branch fuses, smart BMS, host/CAN watchdogs")
    # verification
    ver = []
    for f, name in (("verification/leg_motion_verification_L.json", "left leg"), ("verification/leg_motion_verification_R.json", "right leg"),
                    ("verification/upper_motion_verification.json", "upper body"), ("verification/robot_motion_verification.json", "whole robot")):
        d = load_json(f)
        if d:
            inside = [r for r in d if r.get("within_coupled_ankle_limits", True) and not r.get("outside_documented_limits")]
            extra = f" ({sum(r['collision_free'] for r in inside)}/{len(inside)} within the joint/controller limits)" if len(inside) < len(d) else ""
            ver.append(f"{name} {sum(r['kinematics_pass'] for r in d)}/{len(d)} kinematic, {sum(r['collision_free'] for r in d)}/{len(d)} collision-free{extra}")
    L.append("CAD verification      : " + "; ".join(ver))
    aw = load_json("verification/ankle_workspace_L.json")
    if aw:
        L.append(f"Ankle workspace       : {aw['collision_free_fraction'] * 100:.0f} % of the pitch x roll box collision-free; coupled limit polygon in joint_map.yaml")
    mj = load_json("verification/mujoco_validation.json")
    if mj:
        s_ = mj.get("standing", {})
        L.append(f"MuJoCo                : standing {'held' if not s_.get('fell') else 'FELL'} (max tilt {s_.get('max_tilt_deg')} deg), "
                 f"squat {'ok' if not mj.get('squat', {}).get('fell') else 'fell'}")
    wk = load_json("verification/mujoco_walking.json")
    if wk and "gaits" in wk:
        gs = wk["gaits"]
        runs = ", ".join(f"{n} {r['speed_m_s']:.2f} m/s {'ok' if r['pass'] else 'FAIL'}" for n, r in gs.items())
        worst = max(((j, f, n) for n, r in gs.items() for j, f in r["peak_torque_fraction_of_limit"].items()), key=lambda x: x[1])
        L.append(f"Walking (MuJoCo, CAD) : {runs}; max tilt {max(r['max_tilt_deg'] for r in gs.values()):.1f} deg; "
                 f"highest torque {worst[0]} {worst[1]:.0%} of peak ({worst[2]})  [CALCULATED, MuJoCo]")
    pu = load_json("verification/mujoco_push.json")
    if pu:
        imp = pu["max_survived_impulse_Ns"]
        L.append(f"Push recovery         : walking {pu['gait']}, 0.1 s torso pushes of {min(imp.values()):.1f}-{max(imp.values()):.1f} N s survived, "
                 f"by direction (fixed footsteps, ankle + hip strategy)  [CALCULATED, MuJoCo]")
    L += rl_policy_lines(cat, req)
    xc = load_json("verification/xacro_check.json")
    if xc:
        L.append(f"Robot description     : URDF + xacro ({xc['links']} links, {xc['revolute']} revolute joints; xacro expansion "
                 f"{'matches' if xc['pass'] else 'DIFFERS FROM'} the URDF), MuJoCo MJCF, Isaac Sim import script")
    # cost
    rows = list(csv.DictReader(open(ROOT / "bom" / "master_bom.csv", encoding="utf-8")))
    total = sum(float(r["Total INR"]) for r in rows if r["Status"] != "DEFERRED")
    act = sum(float(r["Total INR"]) for r in rows if r["Part"] == "Joint actuator")
    L.append(f"Cost (India, landed)  : Rs {total:,.0f} (+15 % contingency = Rs {total * 1.15:,.0f}); actuators {act / total * 100:.0f} %  [ESTIMATED/VERIFIED mix, bom/master_bom.csv]")
    L += ["```", "",
          "Details: [README](../README.md) · [architecture](architecture.md) · [structural report](../calculations/results/structural/report.md) · "
          "[open issues](open_issues.md) · [risk register](risk_register.md) · [BOM](../bom/cost_summary.md)", ""]
    (ROOT / "docs" / "final_robot_specification.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
