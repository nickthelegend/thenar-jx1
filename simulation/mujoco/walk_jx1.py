"""Walking validation of the CAD-derived JX1 MuJoCo model (simulation/mujoco/jx1.xml).

The walking pattern is planned on the CAD model itself with the analysis pipeline (calculations/jx1calc/gait.py: footsteps ->
ZMP reference -> two-stage preview control (Kajita 2003) whose multibody ZMP correction uses the CAD model's masses and
inertias -> whole-body IK), with the upper body in a walking posture (shoulder roll 8 deg, elbows -20 deg). Inverse dynamics
of the same model along the plan gives the feedforward torques of all 23 joints. The simulation (CAD meshes, CoACD collision
hulls, contacts, friction) tracks it with joint PD (the actuator-class gains of the MJCF) + feedforward, torques clipped to the
actuator-class peak torques, plus a torso-tilt stabiliser on the stance ankle(s) and hips (ankle + hip strategy).

Pass: no fall (pelvis above 0.35 m, tilt < 25 deg), forward progress within 25 % of the plan, lateral drift < 0.10 m,
no actuator above its peak torque (by construction) and < 5 % of samples saturated.
Outputs verification/mujoco_walking.json, verification/images/mujoco/walk_*.png and walk.gif.
Usage: .venv/Scripts/python simulation/mujoco/walk_jx1.py [--gait slow|nominal] [--no-render] [--no-stabiliser]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "calculations"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from jx1calc import gait as gait_mod  # noqa: E402
from jx1calc.design import Design, LEG_JOINTS  # noqa: E402
from jx1calc.gait import GaitParams, synthesize  # noqa: E402
from validate_jx1 import XML, load, act_index, self_contacts  # noqa: E402

OUT = ROOT / "verification"
IMG = OUT / "images" / "mujoco"
DESIGN_C = ROOT / "calculations" / "results" / "variant_C_cad_masses.yaml"
GAITS = {"slow": dict(step_length=0.15, step_time=0.50, step_height=0.04, n_steps=8),
         "nominal": dict(step_length=0.22, step_time=0.42, step_height=0.05, n_steps=10)}
ARM_POSTURE = {"left_shoulder_roll": np.radians(8), "right_shoulder_roll": np.radians(-8),
               "left_elbow": np.radians(-20), "right_elbow": np.radians(-20)}
# stabiliser gains (rad of joint correction per rad of torso tilt error, and per rad/s of tilt rate) — tuned in simulation
K_ANKLE, D_ANKLE, K_HIP = 0.6, 0.05, 0.3


def rpy(quat):
    w, x, y, z = quat
    roll = np.arctan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
    pitch = np.arcsin(np.clip(2 * (w * y - z * x), -1, 1))
    yaw = np.arctan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    return np.array([roll, pitch, yaw])


def planning_model():
    """The CAD MJCF with the analysis naming (l_hip_yaw, l_sole, ...) that jx1calc.gait / invdyn expect."""
    xml = XML.read_text(encoding="utf-8").replace('meshdir="../../', f'meshdir="{ROOT.as_posix()}/')
    for side in ("left", "right"):
        for j in LEG_JOINTS:
            xml = xml.replace(f'"{side}_{j}_joint"', f'"{side[0]}_{j}"')
        xml = xml.replace(f'"{side}_sole"', f'"{side[0]}_sole"')
    return mujoco.MjModel.from_xml_string(xml)


def plan(gait: str):
    """Walking pattern + feedforward torques on the CAD model. Returns (gait params, synthesis result, joint -> (qadr, dofadr))."""
    design = Design(DESIGN_C) if DESIGN_C.exists() else Design()       # geometry (hip spacing, segment lengths, sole)
    ma = planning_model()
    posture = []
    for n, v in ARM_POSTURE.items():
        jid = mujoco.mj_name2id(ma, mujoco.mjtObj.mjOBJ_JOINT, n + "_joint")
        if jid >= 0:
            posture.append((ma.jnt_qposadr[jid], v))
    orig = gait_mod.WholeBody.set_state

    def set_state(self, p_pelvis, yaw, q_legs):                      # upper body in the walking posture while planning
        qpos = orig(self, p_pelvis, yaw, q_legs)
        for adr, v in posture:
            qpos[adr] = v
        return qpos

    gait_mod.WholeBody.set_state = set_state
    try:
        g = GaitParams(f"walk_{gait}", hip_height=0.54, **GAITS[gait])
        res = synthesize(ma, design, g)
    finally:
        gait_mod.WholeBody.set_state = orig
    cols = {}
    for j in range(ma.njnt):
        n = mujoco.mj_id2name(ma, mujoco.mjtObj.mjOBJ_JOINT, j)
        if not n or ma.jnt_type[j] == mujoco.mjtJoint.mjJNT_FREE:
            continue
        key = f"{'left' if n[0] == 'l' else 'right'}_{n[2:]}" if n[:2] in ("l_", "r_") else n.replace("_joint", "")
        cols[key] = (int(ma.jnt_qposadr[j]), int(ma.jnt_dofadr[j]))
    return g, res, cols


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gait", default="slow", choices=list(GAITS))
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--no-stabiliser", action="store_true")
    a = ap.parse_args()
    g, res, cols = plan(a.gait)
    t_ref, q_ref, qd_ref, tau_ff = res["t"], res["qpos"], res["qvel"], res["idr"]["tau"]
    contact = res["plan"].contact

    m = load()
    d = mujoco.MjData(m)
    ai = act_index(m)
    # actuators -> torque motors: keep the MJCF PD gains for the Python-side law, clamp to the forcerange (peak torque)
    kp = {n: float(m.actuator_gainprm[i, 0]) for n, i in ai.items()}
    kv = {n: float(-m.actuator_biasprm[i, 2]) for n, i in ai.items()}
    tau_max = {n: float(m.actuator_forcerange[i, 1]) for n, i in ai.items()}
    m.actuator_gainprm[:, 0] = 1.0
    m.actuator_biasprm[:, :] = 0.0
    m.actuator_ctrllimited[:] = 0
    jadr = {}
    for n in ai:
        jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n + "_joint")
        jadr[n] = (m.jnt_qposadr[jid], m.jnt_dofadr[jid])

    # initial state = first plan frame
    mujoco.mj_resetData(m, d)
    d.qpos[:7] = q_ref[0, :7]
    d.qpos[2] += 0.003
    for n, (qa, _) in cols.items():
        if n in jadr:
            d.qpos[jadr[n][0]] = q_ref[0, qa]
    mujoco.mj_forward(m, d)

    dt = m.opt.timestep
    T = float(t_ref[-1])
    n_steps = int(T / dt)
    frames, peak, sat, samples = [], {n: 0.0 for n in ai}, {n: 0 for n in ai}, 0
    hist, contacts_seen, track_err = [], set(), []
    renderer = None
    if not a.no_render:
        try:
            renderer = mujoco.Renderer(m, 240, 320)
            cam = mujoco.MjvCamera()
            cam.distance, cam.azimuth, cam.elevation = 2.2, 120, -12
        except Exception as e:  # pragma: no cover
            print("render disabled:", e)
            renderer = None
    sole = {side: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, f"{side}_sole") for side in ("left", "right")}
    stance0, slip, landing = {}, {"left": [], "right": []}, {"left": [], "right": []}
    fell = False
    for k in range(n_steps):
        t = k * dt
        i = min(int(t / g.dt), len(t_ref) - 2)
        s = (t - t_ref[i]) / g.dt
        interp = lambda arr, c: (1 - s) * arr[i, c] + s * arr[i + 1, c]  # noqa: E731
        roll, pitch, _ = rpy(d.qpos[3:7])
        wx, wy = d.qvel[3], d.qvel[4]
        st = contact[i]                                    # [left, right] stance flags
        corr = {}
        if not a.no_stabiliser:
            for side, on in (("left", st[0]), ("right", st[1])):
                if on:
                    corr[f"{side}_ankle_pitch"] = K_ANKLE * pitch + D_ANKLE * wy
                    corr[f"{side}_ankle_roll"] = K_ANKLE * roll + D_ANKLE * wx
                    corr[f"{side}_hip_pitch"] = K_HIP * pitch
                    corr[f"{side}_hip_roll"] = K_HIP * roll
        for n, i_act in ai.items():
            qa, da = jadr[n]
            c_q, c_d = cols[n]
            qr, qdr, ff = interp(q_ref, c_q), interp(qd_ref, c_d), interp(tau_ff, c_d - 6)
            qr += corr.get(n, 0.0)
            u = kp[n] * (qr - d.qpos[qa]) + kv[n] * (qdr - d.qvel[da]) + ff
            if abs(u) >= tau_max[n]:
                sat[n] += 1
            u = float(np.clip(u, -tau_max[n], tau_max[n]))
            d.ctrl[i_act] = u
            peak[n] = max(peak[n], abs(u))
            if n.split("_", 1)[1] in LEG_JOINTS:
                track_err.append(abs(float(d.qpos[qa] - qr)))
        samples += 1
        mujoco.mj_step(m, d)
        # stance-foot slip (sole displacement over each planned stance phase) and landing error vs the planned footstep
        for idx, side in enumerate(("left", "right")):
            ps = d.site_xpos[sole[side]][:2].copy()
            if st[idx] and side not in stance0:
                stance0[side] = ps
                landing[side].append(float(np.linalg.norm(ps - res["plan"].feet["l" if side == "left" else "r"][i][:2])))
            elif not st[idx] and side in stance0:
                slip[side].append(float(np.linalg.norm(ps - stance0.pop(side))))
        if k % 10 == 0:
            tilt = float(np.degrees(np.hypot(roll, pitch)))
            base_ref = q_ref[i, :3]
            hist.append((float(t), *[float(x) for x in d.qpos[:3]], *[float(x) for x in base_ref], tilt))
            for p in self_contacts(m, d):
                contacts_seen.add(tuple(sorted(p[:2])))
            if d.qpos[2] < 0.35 or tilt > 25:
                fell = True
                break
        if renderer is not None and k % int(0.08 / dt) == 0:
            cam.lookat[:] = [d.qpos[0], d.qpos[1], 0.6]
            renderer.update_scene(d, cam)
            frames.append(renderer.render().copy())
    h = np.array(hist)
    x_plan = float(q_ref[-1, 0] - q_ref[0, 0])
    x_sim = float(h[-1, 1] - h[0, 1])
    out = {"gait": a.gait, "gait_params": {k: v for k, v in vars(g).items() if isinstance(v, (int, float, str))},
           "planning_model": "simulation/mujoco/jx1.xml (CAD masses/inertias); geometry from "
                             + (DESIGN_C.relative_to(ROOT).as_posix() if DESIGN_C.exists() else "calculations/design_point.yaml"),
           "zmp_error_history_m": [round(x, 4) for x in res["zmp_error_history_m"]],
           "stabiliser": None if a.no_stabiliser else {"k_ankle": K_ANKLE, "d_ankle": D_ANKLE, "k_hip": K_HIP},
           "duration_s": round(float(h[-1, 0]), 3), "planned_duration_s": round(T, 3), "fell": fell,
           "forward_progress_m": {"plan": round(x_plan, 3), "sim": round(x_sim, 3), "ratio": round(x_sim / x_plan, 3) if x_plan else None},
           "lateral_drift_m": round(float(h[-1, 2] - h[-1, 5]), 3), "pelvis_height_final_m": round(float(h[-1, 3]), 3),
           "max_tilt_deg": round(float(h[:, 7].max()), 2),
           "joint_tracking_error_deg": {"rms": round(float(np.degrees(np.sqrt(np.mean(np.square(track_err))))), 2),
                                        "max": round(float(np.degrees(np.max(track_err))), 2)},
           "peak_torque_Nm": {n: round(v, 1) for n, v in peak.items()},
           "peak_torque_fraction_of_limit": {n: round(v / tau_max[n], 3) for n, v in peak.items()},
           "saturated_sample_fraction": {n: round(c / samples, 4) for n, c in sat.items() if c},
           "stance_slip_mm": {sd: {"max": round(1000 * max(v), 1), "mean": round(1000 * float(np.mean(v)), 1)} for sd, v in slip.items() if v},
           "landing_error_mm": {sd: {"max": round(1000 * max(v), 1), "mean": round(1000 * float(np.mean(v)), 1)} for sd, v in landing.items() if v},
           "self_contact_pairs": sorted(contacts_seen)}
    worst_sat = max(out["saturated_sample_fraction"].values(), default=0.0)
    out["pass"] = (not fell and x_plan > 0 and 0.75 <= x_sim / x_plan <= 1.25 and abs(out["lateral_drift_m"]) < 0.10
                   and worst_sat < 0.05)
    (OUT / "mujoco_walking.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    if frames:
        import PIL.Image
        IMG.mkdir(parents=True, exist_ok=True)
        ims = [PIL.Image.fromarray(f) for f in frames]
        ims[0].save(IMG / "walk.gif", save_all=True, append_images=ims[1:], duration=80, loop=0, optimize=True)
        for tag, f in (("start", frames[0]), ("mid", frames[len(frames) // 2]), ("end", frames[-1])):
            PIL.Image.fromarray(f).save(IMG / f"walk_{tag}.png")
    print(json.dumps({k: out[k] for k in ("fell", "forward_progress_m", "lateral_drift_m", "max_tilt_deg", "joint_tracking_error_deg",
                                          "saturated_sample_fraction", "stance_slip_mm", "landing_error_mm", "pass")}, indent=1))


if __name__ == "__main__":
    main()
