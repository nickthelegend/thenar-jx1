"""Side-by-side comparison of exported policy bundles (markdown table from each bundle's check results).

Usage: rl/.venv/Scripts/python rl/compare_policies.py rl/policies/jx1_walk_flat rl/policies/jx1_walk_rough rl/policies/jx1_walk
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def pct(x):
    return "-" if x is None else f"{x:.0%}"


def row_values(b: Path) -> dict:
    io = yaml.safe_load((b / "policy_io.yaml").read_text(encoding="utf-8"))
    tr = io["trained"]
    out = {"trained": f"{tr.get('run', '?')} it {tr.get('iteration', '?')}"}
    for tag, key in (("", "flat"), ("_rough", "rough")):
        s = load(b / f"sim2sim{tag}.json")
        if s:
            sc = s["scenarios"]
            falls = sum(r["fell"] for r in sc.values())
            f5 = sc["forward_0.5"]
            out[f"sim2sim {key}"] = (f"{len(sc) - falls}/{len(sc)} upright; 0.5 m/s -> {f5['mean_velocity_b'][0]:.2f}, "
                                     f"turn 0.5 -> {sc['turn_0.5']['mean_velocity_b'][2]:.2f} rad/s, peak torque "
                                     f"{pct(max(r['peak_torque_fraction'] for r in sc.values()))}")
    for tag, key in (("", "envelope flat"), ("_rough", "envelope rough")):
        e = load(b / f"envelope{tag}.json")
        if e:
            sm = e["summary"]
            if "self_contact_commands" in sm:
                pairs = ", ".join(f"{p} ({w['commands']})" for p, w in sm["self_contact_pairs"].items()) or "none"
                out[f"self-contact, {key}"] = (f"{sm['self_contact_commands']}/{sm['commands']} commands "
                                               f"({sm['self_contact_commands_trained_range']} in the trained range): {pairs}")
            g = lambda k: f"{sm[k]['achieved']:+.2f}" if sm.get(k) else "-"  # noqa: E731
            out[key] = (f"{sm['tracked']}/{sm['commands']} tracked, {sm['falls']} falls; fwd {g('forward')}, back {g('backward')}, "
                        f"yaw {g('yaw_left')}/{g('yaw_right')}")
    st = (load(b / "sim2sim.json") or {}).get("scenarios", {}).get("stand", {})
    pw = (load(b / "power.json") or {}).get("scenarios", {})
    if "foot_liftoffs_per_s" in st or pw:
        out["stand (zero command)"] = ", ".join(x for x in (
            f"{st['foot_liftoffs_per_s']:.2f} foot lift-offs/s, drift {st['base_travel_m']:.2f} m" if "foot_liftoffs_per_s" in st else "",
            f"{pw['stand']['mean_W']:.0f} W" if "stand" in pw else "") if x)
    if pw.get("walk_0.8"):
        out["power 0.5 / 0.8 m/s"] = f"{pw['walk_0.5']['mean_W']:.0f} W / {pw['walk_0.8']['mean_W']:.0f} W"
    p = load(b / "push_test.json")
    if p:
        v = p["max_survived_impulse_Ns"]
        out["push (N s)"] = f"{min(v.values()):.1f}-{max(v.values()):.1f} (fwd {v['forward']:.1f}, back {v['backward']:.1f}, " \
                            f"left {v['left']:.1f}, right {v['right']:.1f})"
    ps = load(b / "push_test_stand.json")
    if ps:
        v = ps["max_survived_impulse_Ns"]
        out["push standing (N s)"] = f"{min(v.values()):.1f}-{max(v.values()):.1f}"
    h = load(b / "hw_loop_check.json")
    if h and h.get("phases"):
        ph = h["phases"]
        out["HIL (hub twin)"] = f"fwd {ph['forward']['mean_speed_m_s'] / 0.3:.0%} of 0.3 m/s, turn {ph['turn']['yaw_change_deg'] / 103.1:.0%} of 0.3 rad/s"
    lat = load(b / "latency.json")
    if lat:
        r0 = next(r for r in lat["rows"] if r["obs_delay_ms"] == 0 and r["act_delay_ms"] == 0)
        r1 = next((r for r in lat["rows"] if r["obs_delay_ms"] == 20 and r["act_delay_ms"] == 10), None)
        out["turn 0.3 tracking"] = f"{pct(r0['turn_0.3']['fraction'])} (no delay)" + (
            f", {pct(r1['turn_0.3']['fraction'])} (20 + 10 ms)" if r1 else "")
    return out


def main():
    bundles = [Path(p) for p in sys.argv[1:]]
    rows = {b.name: row_values(b) for b in bundles}
    keys = []
    for r in rows.values():
        keys += [k for k in r if k not in keys]
    print("| | " + " | ".join(f"`{n}`" for n in rows) + " |")
    print("|---|" + "---|" * len(rows))
    for k in keys:
        print(f"| {k} | " + " | ".join(r.get(k, "-") for r in rows.values()) + " |")


if __name__ == "__main__":
    main()
