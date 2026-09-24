"""Policy card: collect every check of an exported policy bundle into <policy>/REPORT.md.

Reads what is present next to policy.onnx: policy_io.yaml, training.png, sim2sim*.json, envelope*.json/png,
push_test.json, ros2_check.json, hw_loop_check.json. Nothing is recomputed.
Usage: rl/.venv/Scripts/python rl/report.py [--policy rl/policies/jx1_walk_rough]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jx1_rl import DEFAULT_POLICY, RL_DIR  # noqa: E402


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def pct(x):
    return "-" if x is None else f"{x:.0%}"


def vec(v, nd=2):
    return "(" + ", ".join(f"{x:+.{nd}f}" for x in v) + ")"


def sim2sim_table(s):
    rows = ["| scenario | command (vx, vy, wz) | result | mean velocity | RMSE | max tilt | peak torque / limit | peak speed / limit | "
            "foot lift-offs |", "|---|---|---|---|---|---|---|---|---|"]
    for name, r in s["scenarios"].items():
        lift = f"{r['foot_liftoffs_per_s']:.2f}/s" if "foot_liftoffs_per_s" in r else "-"
        rows.append(f"| {name} | {vec(r['command'], 1)} | {'**fell** at ' + str(r['time_survived_s']) + ' s' if r['fell'] else 'upright'} | "
                    f"{vec(r['mean_velocity_b'])} | {vec(r['velocity_rmse'])} | {r['max_tilt_deg']:.1f}° | "
                    f"{pct(r['peak_torque_fraction'])} {r['peak_torque_joint']} | {pct(r.get('peak_speed_fraction'))} {r.get('peak_speed_joint', '')} | "
                    f"{lift} |")
    return "\n".join(rows)


def phases_table(p):
    rows = ["| phase | command | distance | mean speed | yaw change | min pelvis z | max tilt |", "|---|---|---|---|---|---|---|"]
    for name, r in p["phases"].items():
        rows.append(f"| {name} | {vec(r['command'], 1)} | {r['distance_m']:.2f} m | {r['mean_speed_m_s']:.2f} m/s | {r['yaw_change_deg']:+.1f}° | "
                    f"{r['min_pelvis_z_m']:.3f} m | {r['max_tilt_deg']:.1f}° |")
    return "\n".join(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default=str(DEFAULT_POLICY))
    a = ap.parse_args()
    pdir = Path(a.policy)
    io = yaml.safe_load((pdir / "policy_io.yaml").read_text(encoding="utf-8"))
    tr = io["trained"]
    push = load(pdir / "push_test.json")
    out = [f"# JX1 walking policy: `{pdir.name}`", ""]
    out += ["| | |", "|---|---|",
            f"| trainer | {tr.get('trainer', 'rl/train.py (MuJoCo, rsl_rl-style PPO)')} |",
            f"| checkpoint | {tr.get('run', '?')}/{tr.get('checkpoint', '?')}, iteration {tr.get('iteration', '?')} |",
            f"| task config | {tr.get('task_config', '?')} |",
            f"| robot model | `{tr.get('source_mjcf', tr.get('source_urdf', '?'))}`"
            + (f" (sha256 {tr['source_mjcf_sha256'][:12]}…)" if tr.get("source_mjcf_sha256") else "")
            + (f", {push['robot_mass_kg']} kg" if push else "") + " |",
            f"| interface | {io['observation']['size']} observations → {io['policy']['num_actions']} leg joint targets at "
            f"{1 / io['control']['policy_dt_s']:.0f} Hz; {len(io['joints']['held'])} joints held at the default pose |",
            f"| export check | ONNX max abs diff {tr.get('export_check', {}).get('onnx_max_abs_diff', float('nan')):.1e} |", ""]
    if (pdir / "training.png").exists():
        out += ["## Training", "", "![training curves](training.png)", ""]
    for tag, title in (("", "flat floor"), ("_rough", "rough ground (rl/config/jx1_walk_rough.yaml heightfield)")):
        s = load(pdir / f"sim2sim{tag}.json")
        if s:
            out += [f"## Sim-to-sim on the full CAD model, {title}", "",
                    f"`{s['model']}` as generated: CoACD mesh-hull collisions, {s['physics_dt_s'] * 1000:.0f} ms physics, "
                    f"nominal masses, CAN-hub target ramp {'on' if s['hub_interpolation'] else 'off'}. "
                    f"{'All scenarios upright.' if s['all_upright'] else '**At least one fall.**'}", "", sim2sim_table(s), ""]
            if tag == "" and (pdir / "sim2sim_walk.gif").exists():
                out += ["![walking at 0.5 m/s on the CAD model](sim2sim_walk.gif)", ""]
    for tag in ("", "_rough"):
        e = load(pdir / f"envelope{tag}.json")
        if e:
            sm = e["summary"]

            def best(k, unit):
                v = sm.get(k)
                return f"{v['achieved']:+.2f} {unit} (command {v['command']:+.2f}, peak torque {pct(v['peak_torque_fraction'])})" if v else "-"
            out += [f"## Command envelope{' (rough ground)' if tag else ''}", "",
                    f"{sm['tracked']}/{sm['commands']} commands tracked, {sm['falls']} falls ({e['criterion']}; "
                    f"{e['duration_s']:.0f} s per command). Best tracked pure commands:", "",
                    f"- forward {best('forward', 'm/s')}, backward {best('backward', 'm/s')}",
                    f"- left {best('left', 'm/s')}, right {best('right', 'm/s')}",
                    f"- yaw left {best('yaw_left', 'rad/s')}, yaw right {best('yaw_right', 'rad/s')}", "",
                    f"![command envelope](envelope{tag}.png)", ""]
    lat = load(pdir / "latency.json")
    if lat:
        out += ["## Latency sensitivity (CAD model, added sensing / actuation delay)", "",
                "| sensing delay | actuation delay | turn 0.3 rad/s tracked | forward 0.3 m/s tracked |", "|---|---|---|---|"]
        for r in lat["rows"]:
            cell = lambda s: "**fell**" if s["fell"] else f"{s['fraction']:.0%}"  # noqa: E731
            out.append(f"| {r['obs_delay_ms']} ms | {r['act_delay_ms']} ms | {cell(r['turn_0.3'])} | {cell(r['forward_0.3'])} |")
        out += [""]
    if push:
        out += ["## Push recovery (0.1 s torso pulse while walking at 0.5 m/s, CAD model)", "",
                "| direction | largest survived impulse | CoM velocity change |", "|---|---|---|"]
        out += [f"| {d} | {v:.1f} N·s | {push['equivalent_com_velocity_change_m_s'][d]:.2f} m/s |" for d, v in push["max_survived_impulse_Ns"].items()]
        out += [""]
        push_st = load(pdir / "push_test_stand.json")
        if push_st:
            out += ["Standing (zero command), largest survived impulse: " + ", ".join(
                f"{d} {v:.1f} N·s" for d, v in push_st["max_survived_impulse_Ns"].items()) + ".", ""]
    pw = load(pdir / "power.json")
    if pw:
        out += ["## Power (CAD model; electrical model of calculations/run_power_budget.py, no regeneration)", "",
                "| scenario | command | mean | peak | mean current (nominal V) | runtime, 13S2P 50S (80 %) | foot lift-offs |",
                "|---|---|---|---|---|---|---|"]
        for name, r in pw["scenarios"].items():
            lift = f"{r['foot_liftoffs_per_s']:.2f}/s" if "foot_liftoffs_per_s" in r else "-"
            out.append(f"| {name} | {vec(r['command'], 1)} | {r['mean_W']:.0f} W | {r['peak_W']:.0f} W | {r['mean_current_A_at_nominal']:.1f} A | "
                       f"{pw['pack_13S2P_50S']['runtime_h'][name]:.2f} h | {lift} |")
        out += ["", "Worst actuator RMS current vs rated: " + ", ".join(
            f"{j} {t['utilisation']:.0%} ({t['scenario']})" for j, t in pw["thermal"].items()), ""]
    paths = [(f, load(pdir / f)) for f in ("ros2_check.json", "ros2_launch_check.json", "ros2_control_check.json")]
    paths = [(f, r) for f, r in paths if r and r.get("phases")]
    if paths:
        r2 = paths[0][1]
        out += [f"## ROS 2 {r2.get('ros_distro', '')}: separate node processes driven over `/cmd_vel`, measured from `/jx1/odom`", "",
                "Same script on every path: forward 0.4 m/s for 10 s, turn 0.4 rad/s for 6 s (137.5° commanded), stop.", "",
                "| started by | forward speed | turn | max tilt | upright |", "|---|---|---|---|---|"]
        for f, r in paths:
            ph = r["phases"]
            fw, tn = ph.get("forward", {}), ph.get("turn", {})
            out.append(f"| {r.get('started_by', 'python -m (source tree)')} | {fw.get('mean_speed_m_s', float('nan')):.2f} m/s | "
                       f"{tn.get('yaw_change_deg', float('nan')):.0f}° | {max(p['max_tilt_deg'] for p in ph.values()):.1f}° | "
                       f"{r.get('upright')} |")
        out += ["", phases_table(r2), ""]
    hw = load(pdir / "hw_loop_check.json")
    if hw:
        hubs = hw.get("hub_status_end", {}).get("hubs", {})
        faults = [h for h, s in hubs.items() if s.get("fault") or s.get("estop") or s.get("stale")]
        out += ["## Hardware-in-the-loop: policy → `hw_node` → hub protocol → hub-firmware twin → physics", "",
                f"`{hw['chain']}`. RUN accepted: {hw['run_accepted']}, upright: {hw['upright']}, "
                f"hub faults at the end: {', '.join(faults) if faults else 'none'}.", "", phases_table(hw), ""]
        hl = load(pdir / "hw_loop_launch_check.json")
        if hl and hl.get("phases"):
            ph = hl["phases"]
            out += [f"Started as on the robot, `{hl.get('started_by')}`: forward {ph['forward']['mean_speed_m_s']:.2f} m/s at 0.3, "
                    f"turn {ph['turn']['yaw_change_deg']:.0f}° of 103° commanded, upright {hl.get('upright')}, "
                    f"RUN accepted {hl.get('run_accepted')}.", ""]
    limits = []
    for tag in ("", "_rough"):
        s = load(pdir / f"sim2sim{tag}.json")
        for name, r in (s or {}).get("scenarios", {}).items():
            if r["peak_torque_fraction"] >= 0.95:
                limits.append(f"{name}{tag}: {r['peak_torque_joint']} reaches {pct(r['peak_torque_fraction'])} of its effort limit")
    if limits:
        out += ["## Watch items", ""] + [f"- {x}" for x in limits] + [""]
    (pdir / "REPORT.md").write_text("\n".join(out), encoding="utf-8")
    print("wrote", pdir / "REPORT.md")


if __name__ == "__main__":
    main()
