"""Policy card: collect every check of an exported policy bundle into <policy>/REPORT.md.

Reads what is present next to policy.onnx: policy_io.yaml, training.png, sim2sim*.json, envelope*.json/png,
push_test.json, ros2_check.json, hw_loop_check.json. Nothing is recomputed.
Usage: rl/.venv/Scripts/python rl/report.py [--policy rl/policies/jx1_walk_flat]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jx1_rl import RL_DIR  # noqa: E402


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def pct(x):
    return "-" if x is None else f"{x:.0%}"


def vec(v, nd=2):
    return "(" + ", ".join(f"{x:+.{nd}f}" for x in v) + ")"


def sim2sim_table(s):
    rows = ["| scenario | command (vx, vy, wz) | result | mean velocity | RMSE | max tilt | peak torque / limit | peak speed / limit |",
            "|---|---|---|---|---|---|---|---|"]
    for name, r in s["scenarios"].items():
        rows.append(f"| {name} | {vec(r['command'], 1)} | {'**fell** at ' + str(r['time_survived_s']) + ' s' if r['fell'] else 'upright'} | "
                    f"{vec(r['mean_velocity_b'])} | {vec(r['velocity_rmse'])} | {r['max_tilt_deg']:.1f}° | "
                    f"{pct(r['peak_torque_fraction'])} {r['peak_torque_joint']} | {pct(r.get('peak_speed_fraction'))} {r.get('peak_speed_joint', '')} |")
    return "\n".join(rows)


def phases_table(p):
    rows = ["| phase | command | distance | mean speed | yaw change | min pelvis z | max tilt |", "|---|---|---|---|---|---|---|"]
    for name, r in p["phases"].items():
        rows.append(f"| {name} | {vec(r['command'], 1)} | {r['distance_m']:.2f} m | {r['mean_speed_m_s']:.2f} m/s | {r['yaw_change_deg']:+.1f}° | "
                    f"{r['min_pelvis_z_m']:.3f} m | {r['max_tilt_deg']:.1f}° |")
    return "\n".join(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", default=str(RL_DIR / "policies" / "jx1_walk_flat"))
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
    if push:
        out += ["## Push recovery (0.1 s torso pulse while walking at 0.5 m/s, CAD model)", "",
                "| direction | largest survived impulse | CoM velocity change |", "|---|---|---|"]
        out += [f"| {d} | {v:.1f} N·s | {push['equivalent_com_velocity_change_m_s'][d]:.2f} m/s |" for d, v in push["max_survived_impulse_Ns"].items()]
        out += [""]
    r2 = load(pdir / "ros2_check.json")
    if r2:
        out += [f"## ROS 2 {r2.get('ros_distro', '')}: `jx1_sim` + `jx1_policy` as separate processes, `/cmd_vel` → walk", "",
                f"Reached WALK: {r2['reached_walk_state']}, upright throughout: {r2['upright']}.", "", phases_table(r2), ""]
    hw = load(pdir / "hw_loop_check.json")
    if hw:
        hubs = hw.get("hub_status_end", {}).get("hubs", {})
        faults = [h for h, s in hubs.items() if s.get("fault") or s.get("estop") or s.get("stale")]
        out += ["## Hardware-in-the-loop: policy → `hw_node` → hub protocol → hub-firmware twin → physics", "",
                f"`{hw['chain']}`. RUN accepted: {hw['run_accepted']}, upright: {hw['upright']}, "
                f"hub faults at the end: {', '.join(faults) if faults else 'none'}.", "", phases_table(hw), ""]
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
