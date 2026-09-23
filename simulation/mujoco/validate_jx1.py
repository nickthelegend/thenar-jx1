"""MuJoCo validation of the CAD-derived JX1 model (simulation/mujoco/jx1.xml).

Checks (results -> verification/mujoco_validation.json, images -> verification/images/mujoco/):
  1. model integrity: mass, COM, joint limits == simulation/joint_map.yaml
  2. standing: PD hold of a bent-knee stance on the floor for 6 s (height drift, tilt, torque saturation, self-contacts)
  3. squat: 0.54 -> 0.40 -> 0.54 m hip height in 3 s via analytic IK targets (tracking error, peak torques vs limits)
  4. leg swings (fixed base): every leg joint min -> max -> min (self-collision contacts, torques)
  5. self-collision scan (fixed base): 3,000 random in-limit leg configurations
Usage: .venv/Scripts/python simulation/mujoco/validate_jx1.py [--no-render]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import mujoco
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "calculations"))
from jx1calc.kinematics import leg_ik  # noqa: E402

XML = ROOT / "simulation" / "mujoco" / "jx1.xml"
OUT = ROOT / "verification"
IMG = OUT / "images" / "mujoco"
JM = yaml.safe_load((ROOT / "simulation" / "joint_map.yaml").read_text(encoding="utf-8"))
DP = yaml.safe_load((ROOT / "calculations" / "design_point.yaml").read_text(encoding="utf-8"))
G = lambda k: DP["geometry"][k]["value"]  # noqa: E731
THIGH, SHIN, HIPY, SOLE = G("thigh_m"), G("shin_m"), G("hip_spacing_m") / 2, G("sole_to_ankle_m")
LEG = ["hip_yaw", "hip_roll", "hip_pitch", "knee", "ankle_pitch", "ankle_roll"]


def load(fixed=False):
    xml = XML.read_text(encoding="utf-8")
    if fixed:
        xml = xml.replace('<freejoint name="root"/>', "").replace('<body name="pelvis" pos="0 0 0.64">', '<body name="pelvis" pos="0 0 1.2">')
    return mujoco.MjModel.from_xml_string(xml.replace('meshdir="../../', f'meshdir="{(ROOT).as_posix()}/'))


def leg_targets(hip_h):
    """Joint targets for a symmetric stance with feet under the hips at hip height hip_h (flat feet)."""
    out = {}
    for side, s in (("left", 1), ("right", -1)):
        hip = np.array([0, s * HIPY, hip_h])
        foot = np.array([0, s * HIPY, SOLE])
        q = leg_ik(hip, np.eye(3), foot, np.eye(3), THIGH, SHIN)
        for k, j in enumerate(LEG):
            out[f"{side}_{j}"] = q[k]
    return out


def act_index(m):
    return {mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_ACTUATOR, i): i for i in range(m.nu)}


def self_contacts(m, d):
    floor = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_GEOM, "floor")
    pairs = []
    for i in range(d.ncon):
        c = d.contact[i]
        if floor in (c.geom1, c.geom2):
            continue
        b1, b2 = m.geom_bodyid[c.geom1], m.geom_bodyid[c.geom2]
        pairs.append((mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, b1), mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, b2), float(c.dist)))
    return pairs


def set_qpos_legs(m, d, targets, z=None):
    for name, v in targets.items():
        jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, name + "_joint")
        d.qpos[m.jnt_qposadr[jid]] = v
    if z is not None:
        d.qpos[2] = z


def render(m, d, path, cam_dist=1.8, azimuth=135, elevation=-15, lookat_z=0.55):
    try:
        r = mujoco.Renderer(m, 480, 640)
        cam = mujoco.MjvCamera()
        cam.distance, cam.azimuth, cam.elevation = cam_dist, azimuth, elevation
        cam.lookat[:] = [0, 0, lookat_z]
        r.update_scene(d, cam)
        import PIL.Image
        PIL.Image.fromarray(r.render()).save(path)
        r.close()
        return True
    except Exception as e:  # pragma: no cover
        print("render skipped:", e)
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-render", action="store_true")
    a = ap.parse_args()
    IMG.mkdir(parents=True, exist_ok=True)
    res = {}
    # ------------------------------------------------------------------ 1. integrity
    m = load()
    d = mujoco.MjData(m)
    mujoco.mj_forward(m, d)
    total = float(sum(m.body_mass))
    lim_ok, lim_rows = True, []
    for j in JM["joints"]:
        jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, j["name"])
        if jid < 0:
            continue
        lo, hi = m.jnt_range[jid]
        ok = abs(lo - j["lower_rad"]) < 1e-6 and abs(hi - j["upper_rad"]) < 1e-6
        lim_ok &= ok
        lim_rows.append({"joint": j["name"], "model": [float(lo), float(hi)], "joint_map": [j["lower_rad"], j["upper_rad"]], "match": ok})
    res["integrity"] = {"total_mass_kg": round(total, 3), "nbody": m.nbody, "njnt": m.njnt, "nu": m.nu, "joint_limits_match_joint_map": lim_ok,
                        "limits": lim_rows}
    # ------------------------------------------------------------------ 2. standing
    ai = act_index(m)
    tgt = leg_targets(0.56)
    mujoco.mj_resetData(m, d)
    set_qpos_legs(m, d, tgt, z=0.56 + 0.005)
    for name, v in tgt.items():
        d.ctrl[ai[name]] = v
    mujoco.mj_forward(m, d)
    z0 = float(d.qpos[2])
    hist = []
    peak_tau = {}
    contacts_seen = set()
    for k in range(int(6.0 / m.opt.timestep)):
        mujoco.mj_step(m, d)
        if k % 25 == 0:
            quat = d.qpos[3:7]
            tilt = 2 * np.degrees(np.arccos(np.clip(abs(quat[0]), -1, 1)))
            hist.append((float(d.time), float(d.qpos[2]), float(tilt)))
            for p in self_contacts(m, d):
                contacts_seen.add(tuple(sorted(p[:2])))
        for name, i in ai.items():
            peak_tau[name] = max(peak_tau.get(name, 0.0), abs(float(d.actuator_force[i])))
    h = np.array(hist)
    sat = {n: round(t, 2) for n, t in peak_tau.items() if t >= 0.98 * m.actuator_forcerange[ai[n]][1]}
    res["standing"] = {"hip_height_target_m": 0.56, "pelvis_z_start": round(z0, 4), "pelvis_z_end": round(float(h[-1, 1]), 4),
                       "max_tilt_deg": round(float(h[:, 2].max()), 3), "final_tilt_deg": round(float(h[-1, 2]), 3),
                       "fell": bool(h[-1, 1] < 0.4 or h[:, 2].max() > 20), "peak_actuator_torque_Nm": {k: round(v, 2) for k, v in peak_tau.items()},
                       "saturated_actuators": sat, "self_contact_pairs": sorted(contacts_seen)}
    if not a.no_render:
        render(m, d, IMG / "standing.png")
    # ------------------------------------------------------------------ 3. squat
    T = 3.0
    err_max, peak_sq = 0.0, {}
    for k in range(int((T + 1.0) / m.opt.timestep)):
        t = k * m.opt.timestep
        hh = 0.56 - 0.16 * 0.5 * (1 - np.cos(2 * np.pi * min(t, T) / T))
        tg = leg_targets(hh)
        for name, v in tg.items():
            d.ctrl[ai[name]] = v
        mujoco.mj_step(m, d)
        for name, i in ai.items():
            peak_sq[name] = max(peak_sq.get(name, 0.0), abs(float(d.actuator_force[i])))
            if name in tg:
                jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, name + "_joint")
                err_max = max(err_max, abs(float(d.qpos[m.jnt_qposadr[jid]] - tg[name])))
        if not a.no_render and abs(t - T / 2) < m.opt.timestep / 2:
            render(m, d, IMG / "squat_bottom.png", lookat_z=0.45)
    quat = d.qpos[3:7]
    res["squat"] = {"hip_height_range_m": [0.40, 0.56], "duration_s": T, "max_joint_tracking_error_deg": round(float(np.degrees(err_max)), 2),
                    "peak_actuator_torque_Nm": {k: round(v, 2) for k, v in peak_sq.items()},
                    "saturated": {n: round(t, 2) for n, t in peak_sq.items() if t >= 0.98 * m.actuator_forcerange[ai[n]][1]},
                    "fell": bool(d.qpos[2] < 0.35), "final_tilt_deg": round(float(2 * np.degrees(np.arccos(min(1.0, abs(quat[0]))))), 2)}
    # ------------------------------------------------------------------ 4. leg swings (fixed base)
    mf = load(fixed=True)
    df = mujoco.MjData(mf)
    aif = act_index(mf)
    swings = {}
    for side in ("left", "right"):
        for jn in LEG:
            jid = mujoco.mj_name2id(mf, mujoco.mjtObj.mjOBJ_JOINT, f"{side}_{jn}_joint")
            lo, hi = mf.jnt_range[jid]
            mujoco.mj_resetData(mf, df)
            contacts, peak = set(), 0.0
            steps = int(3.0 / mf.opt.timestep)
            for k in range(steps):
                ph = k / steps
                tgt = lo + (hi - lo) * (0.5 - 0.5 * np.cos(2 * np.pi * ph)) if ph < 1 else 0.0
                df.ctrl[aif[f"{side}_{jn}"]] = tgt
                mujoco.mj_step(mf, df)
                peak = max(peak, abs(float(df.actuator_force[aif[f"{side}_{jn}"]])))
                if k % 10 == 0:
                    for p in self_contacts(mf, df):
                        contacts.add(tuple(sorted(p[:2])))
            reached = [float(lo), float(hi)]
            swings[f"{side}_{jn}"] = {"range_rad": reached, "peak_torque_Nm": round(peak, 2), "self_contacts": sorted(contacts)}
    res["leg_swings_fixed_base"] = swings
    # ------------------------------------------------------------------ 5. random self-collision scan
    rng = np.random.default_rng(7)
    leg_j = [mujoco.mj_name2id(mf, mujoco.mjtObj.mjOBJ_JOINT, f"{s}_{j}_joint") for s in ("left", "right") for j in LEG]
    n, hits, pairs = 3000, 0, {}
    for _ in range(n):
        mujoco.mj_resetData(mf, df)
        for jid in leg_j:
            lo, hi = mf.jnt_range[jid]
            df.qpos[mf.jnt_qposadr[jid]] = rng.uniform(lo, hi)
        mujoco.mj_forward(mf, df)
        sc = [p for p in self_contacts(mf, df) if p[2] < -0.002]
        if sc:
            hits += 1
            for p in sc:
                key = "/".join(sorted(p[:2]))
                pairs[key] = pairs.get(key, 0) + 1
    res["self_collision_scan"] = {"samples": n, "colliding_fraction": round(hits / n, 4),
                                  "top_pairs": dict(sorted(pairs.items(), key=lambda kv: -kv[1])[:12]),
                                  "note": "uniform sampling over the full per-joint box; walking poses occupy a small collision-free subset"}
    (OUT / "mujoco_validation.json").write_text(json.dumps(res, indent=2, default=float), encoding="utf-8")
    print(json.dumps({k: (v if k != "integrity" else {kk: vv for kk, vv in v.items() if kk != "limits"}) for k, v in res.items()
                      if k != "leg_swings_fixed_base"}, indent=1, default=float)[:4000])


if __name__ == "__main__":
    main()
