"""Training model: the CAD-derived MJCF (simulation/mujoco/jx1.xml) turned into a fast RL model with MjSpec.

- mesh collision hulls (class 'collision') are replaced by primitives fitted to them: capsules for thighs and shins,
  boxes for pelvis and torso; feet keep their sole box. Arms, neck, head and hip housings get no collision geometry.
- collision groups: floor vs every robot geom, left leg vs right leg; no same-leg or upper-body self contacts.
- physics options from the task config; contact solref >= 2 x timestep.
- position actuators get the deployment PD gains (config pd_gains); effort limits stay the actuator-class limits.
- extra sites/sensors: foot touch boxes, sole position/velocity, pelvis velocimeter, actuator torques.
- keyframe 'home': default joint pose with the soles on the floor.
Masses and inertias are the CAD values — nothing about the robot is re-typed here.
"""
from __future__ import annotations

import copy
from pathlib import Path

import mujoco
import numpy as np

from . import REPO
from .config import TaskConfig, joint_type

FLOOR_BITS = (1, 0)                 # contype, conaffinity
LEFT_BITS = (2, 1 | 4)              # left leg: floor + right leg
RIGHT_BITS = (4, 1 | 2)             # right leg: floor + left leg
UPPER_BITS = (8, 1)                 # pelvis / torso: floor only
CAPSULE_LINKS = ("thigh", "shin")
BOX_LINKS = ("pelvis", "torso")


def _body_frame_vertices(m: mujoco.MjModel):
    """body id -> (k, 3) vertices of that body's mesh collision geoms (group 3) in the body frame."""
    out = {}
    R = np.zeros(9)
    for g in range(m.ngeom):
        if m.geom_group[g] != 3 or m.geom_type[g] != mujoco.mjtGeom.mjGEOM_MESH:
            continue
        mid = m.geom_dataid[g]
        v = m.mesh_vert[m.mesh_vertadr[mid]: m.mesh_vertadr[mid] + m.mesh_vertnum[mid]]
        mujoco.mju_quat2Mat(R, m.geom_quat[g])
        out.setdefault(int(m.geom_bodyid[g]), []).append(v @ R.reshape(3, 3).T + m.geom_pos[g])
    return {b: np.vstack(vs) for b, vs in out.items()}


def fit_capsule(v: np.ndarray, q=90.0):
    """Capsule (fromto, radius) along the principal axis of point cloud v; radius = q-th percentile distance to the axis."""
    c = v.mean(axis=0)
    _, _, vt = np.linalg.svd(v - c, full_matrices=False)
    a = vt[0]
    t = (v - c) @ a
    r = float(np.percentile(np.linalg.norm((v - c) - np.outer(t, a), axis=1), q))
    t0, t1 = np.percentile(t, 1), np.percentile(t, 99)
    half = max((t1 - t0) / 2 - r, 0.005)
    mid = c + a * (t0 + t1) / 2
    return np.concatenate([mid - a * half, mid + a * half]), r


def fit_box(v: np.ndarray):
    lo, hi = np.percentile(v, 1, axis=0), np.percentile(v, 99, axis=0)
    return (lo + hi) / 2, (hi - lo) / 2


def _bits(body_name: str):
    if body_name.startswith("left_"):
        return LEFT_BITS
    if body_name.startswith("right_"):
        return RIGHT_BITS
    return UPPER_BITS


def build_spec(cfg: TaskConfig) -> mujoco.MjSpec:
    src = REPO / cfg["model"]["source_mjcf"]
    ref = mujoco.MjModel.from_xml_path(str(src))
    spec = mujoco.MjSpec.from_file(str(src))
    spec.meshdir = str((src.parent / spec.meshdir).resolve())
    mc = cfg["model"]
    opt = spec.option
    opt.timestep = mc["timestep"]
    opt.iterations = mc["solver_iterations"]
    opt.ls_iterations = mc["ls_iterations"]
    opt.integrator = mujoco.mjtIntegrator.mjINT_IMPLICITFAST
    solref = list(mc["contact_solref"])

    verts = _body_frame_vertices(ref)
    for g in list(spec.geoms):
        if g.type == mujoco.mjtGeom.mjGEOM_MESH and g.group == 3:
            spec.delete(g)
    for b in range(1, ref.nbody):
        name = mujoco.mj_id2name(ref, mujoco.mjtObj.mjOBJ_BODY, b)
        body = spec.body(name)
        ct, ca = _bits(name)
        if b in verts and any(k in name for k in CAPSULE_LINKS):
            fromto, r = fit_capsule(verts[b])
            body.add_geom(name=f"{name}_capsule", type=mujoco.mjtGeom.mjGEOM_CAPSULE, fromto=fromto, size=[r, 0, 0],
                          contype=ct, conaffinity=ca, group=3, solref=solref, rgba=[0.5, 0.5, 0.5, 0.3], density=0)
        elif b in verts and any(k in name for k in BOX_LINKS):
            pos, half = fit_box(verts[b])
            body.add_geom(name=f"{name}_box", type=mujoco.mjtGeom.mjGEOM_BOX, pos=pos, size=half,
                          contype=ct, conaffinity=ca, group=3, solref=solref, rgba=[0.5, 0.5, 0.5, 0.3], density=0)
    for g in spec.geoms:
        if g.name == "floor":
            g.contype, g.conaffinity = FLOOR_BITS
            g.solref = solref
            g.friction = [mc["floor_friction"], 0.005, 0.0001]
        elif g.name.endswith("_sole"):
            g.contype, g.conaffinity = _bits(g.name)
            g.solref = solref
            g.friction = [mc["floor_friction"], 0.005, 0.0001]
        elif g.group != 3 and g.type == mujoco.mjtGeom.mjGEOM_BOX and g.contype != 0 and not g.name:
            g.contype, g.conaffinity = 0, 0          # torso placeholder box (older generator output)

    terrain = make_terrain(cfg)
    if terrain is not None:
        terrain.add_to_spec(spec)

    # deployment PD gains on the position actuators
    for a in spec.actuators:
        kp, kd = cfg.gains[a.target]
        a.gainprm = [kp] + [0.0] * 9
        a.biasprm = [0.0, -kp, -kd] + [0.0] * 7

    # sensors used by the environment
    for side in ("left", "right"):
        foot = spec.body(f"{side}_foot_link")
        sole = next(g for g in spec.geoms if g.name == f"{side}_foot_link_sole")
        foot.add_site(name=f"{side}_foot_touch", type=mujoco.mjtGeom.mjGEOM_BOX, pos=sole.pos,
                      size=[sole.size[0] + 0.005, sole.size[1] + 0.005, sole.size[2] + 0.01], rgba=[0, 0, 0, 0])
        spec.add_sensor(name=f"{side}_foot_force", type=mujoco.mjtSensor.mjSENS_TOUCH, objtype=mujoco.mjtObj.mjOBJ_SITE,
                        objname=f"{side}_foot_touch")
        spec.add_sensor(name=f"{side}_foot_pos", type=mujoco.mjtSensor.mjSENS_FRAMEPOS, objtype=mujoco.mjtObj.mjOBJ_SITE,
                        objname=f"{side}_sole")
        spec.add_sensor(name=f"{side}_foot_vel", type=mujoco.mjtSensor.mjSENS_FRAMELINVEL, objtype=mujoco.mjtObj.mjOBJ_SITE,
                        objname=f"{side}_sole")
    for a in spec.actuators:
        spec.add_sensor(name=f"{a.name}_torque", type=mujoco.mjtSensor.mjSENS_ACTUATORFRC, objtype=mujoco.mjtObj.mjOBJ_ACTUATOR,
                        objname=a.name)

    # home keyframe: default pose, soles on the floor
    m = spec.compile()
    d = mujoco.MjData(m)
    qpos = m.qpos0.copy()
    qpos[2] = 1.0
    for j in cfg.all_joints:
        jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, j)
        if jid >= 0:
            qpos[m.jnt_qposadr[jid]] = cfg.default_pos[j]
    d.qpos[:] = qpos
    mujoco.mj_kinematics(m, d)
    soles = [d.site_xpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, f"{s}_sole")][2] for s in ("left", "right")]
    qpos[2] = 1.0 - min(soles) + 0.001
    ctrl = np.zeros(m.nu)
    for a in range(m.nu):
        jn = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, m.actuator_trnid[a, 0])
        ctrl[a] = cfg.default_pos[jn]
    spec.add_key(name="home", qpos=qpos.tolist(), ctrl=ctrl.tolist())
    return spec


def make_terrain(cfg: TaskConfig):
    """The task's terrain object (deterministic from its seed), or None on flat ground."""
    tc = cfg.raw.get("terrain", {"type": "plane"})
    if tc.get("type", "plane") != "rough":
        return None
    from .terrain import Terrain
    return Terrain(tc, seed=tc.get("seed", 0))


def build(cfg: TaskConfig):
    """Compiled training model + facts the environment needs."""
    spec = build_spec(cfg)
    m = spec.compile()
    key = m.key("home")
    info = {"base_height": float(key.qpos[2]), "mass_kg": float(m.body_subtreemass[1]), "spec": spec,
            "terrain": make_terrain(cfg),
            "joints_present": [j for j in cfg.all_joints if mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, j) >= 0]}
    return m, info


def write_xml(cfg: TaskConfig, path: Path) -> Path:
    spec = build_spec(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(spec.to_xml(), encoding="utf-8")
    return path


def make_variants(base: mujoco.MjModel, cfg: TaskConfig, k: int, rng: np.random.Generator):
    """k physics variants of the training model for domain randomisation (the first one is the nominal model)."""
    r = cfg["randomization"]
    out = [base]
    floor_or_sole = [g for g in range(base.ngeom)
                     if mujoco.mj_id2name(base, mujoco.mjtObj.mjOBJ_GEOM, g) in ("floor", "left_foot_link_sole", "right_foot_link_sole")]
    trunk = [b for b in (mujoco.mj_name2id(base, mujoco.mjtObj.mjOBJ_BODY, n) for n in ("pelvis", "torso_link")) if b >= 0]
    for _ in range(k - 1):
        m = copy.deepcopy(base)
        mu = rng.uniform(*r["friction"])
        for g in floor_or_sole:
            m.geom_friction[g, 0] = mu
        s = rng.uniform(*r["link_mass_scale"], size=m.nbody)
        s[0] = 1.0
        m.body_mass[:] = base.body_mass * s
        m.body_inertia[:] = base.body_inertia * s[:, None]
        tb = trunk[-1]
        m.body_mass[tb] += rng.uniform(*r["added_base_mass_kg"])
        m.body_ipos[tb] = base.body_ipos[tb] + rng.uniform(-r["base_com_offset_m"], r["base_com_offset_m"], size=3)
        for a in range(m.nu):
            kp = base.actuator_gainprm[a, 0] * rng.uniform(*r["kp_scale"])
            kd = -base.actuator_biasprm[a, 2] * rng.uniform(*r["kd_scale"])
            m.actuator_gainprm[a, 0] = kp
            m.actuator_biasprm[a, 1] = -kp
            m.actuator_biasprm[a, 2] = -kd
        m.dof_armature[6:] = base.dof_armature[6:] * rng.uniform(*r["armature_scale"], size=m.nv - 6)
        m.dof_frictionloss[6:] = base.dof_frictionloss[6:] * rng.uniform(*r["joint_friction_scale"], size=m.nv - 6)
        d = mujoco.MjData(m)
        mujoco.mj_setConst(m, d)
        out.append(m)
    return out
