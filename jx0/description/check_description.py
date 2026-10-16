"""Check the JX0 robot description (urdf/jx0.urdf, jx0.xml, joint_map.yaml) against the verified model:

    python jx0/description/check_description.py      -> jx0/description/check.json

1. URDF structure: one tree rooted at the pelvis, every joint's links exist, every mesh file exists, every link with
   mass has a physical inertia (positive, triangle inequality);
2. URDF = verified model: MuJoCo loads the URDF; total mass, the composite inertia about the pelvis, the centre of mass
   and both sole points agree with jx0/sim/jx0_model.py in 200 random poses inside the joint limits;
3. MJCF = verified model: same, for jx0.xml;
4. limits: the URDF's and the MJCF's joint limits are the commanded limits of jx0bot's config.yaml (and joint_map.yaml);
   effort / velocity = the STS3215's stall torque and no-load speed.
"""
from __future__ import annotations

import json
import math
import os
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import mujoco
import numpy as np
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "jx0" / "sim"))
sys.path.insert(0, str(ROOT / "calculations"))
os.environ.setdefault("JX0_STL_DIR", str(ROOT / "jx0" / "cad" / "stl_engraved"))
from jx0_model import build  # noqa: E402
from jx1calc.design import Design  # noqa: E402

TOL_POS, TOL_MASS = 1e-6, 1e-6


def short(j):
    j = j[:-len("_joint")] if j.endswith("_joint") else j
    for side, s in (("left_", "l_"), ("right_", "r_")):
        if j.startswith(side):
            return s + j[len(side):]
    return j


def fixed_base(xml: str) -> str:
    """The model with the free joint removed (the pelvis at the origin), for kinematic comparison."""
    return xml.replace('<freejoint name="root"/>', "").replace('<joint name="root" type="free"/>', "")


def snapshot(m, d, sites):
    mujoco.mj_kinematics(m, d)
    mujoco.mj_comPos(m, d)
    com = d.subtree_com[1].copy()
    return com, [d.site_xpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, s)].copy() for s in sites]


def composite_inertia(m, d):
    """Inertia of the whole robot about the pelvis origin, world axes (pelvis at the origin)."""
    mujoco.mj_kinematics(m, d)
    I = np.zeros((3, 3))
    p0 = d.xpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "pelvis")]
    for b in range(1, m.nbody):
        Ri = d.ximat[b].reshape(3, 3)                          # the body's principal inertia axes, world frame
        c = d.xipos[b] - p0
        I += Ri @ np.diag(m.body_inertia[b]) @ Ri.T + m.body_mass[b] * (np.dot(c, c) * np.eye(3) - np.outer(c, c))
    return I


def main():
    out, problems = {}, []
    urdf = HERE / "urdf" / "jx0.urdf"
    root = ET.parse(urdf).getroot()
    links = {l.get("name"): l for l in root.findall("link")}
    joints = root.findall("joint")
    children = [j.find("child").get("link") for j in joints]
    parents = [j.find("parent").get("link") for j in joints]
    roots = [l for l in links if l not in children]
    if roots != ["pelvis"]:
        problems.append(f"URDF roots {roots} (expected pelvis only)")
    if len(set(children)) != len(children):
        problems.append("a link has two parent joints")
    for n in parents + children:
        if n not in links:
            problems.append(f"joint refers to missing link {n}")
    meshes = 0
    for mesh in root.iter("mesh"):
        f = (urdf.parent / mesh.get("filename")).resolve()
        meshes += 1
        if not f.exists():
            problems.append(f"missing mesh {mesh.get('filename')}")
    for n, l in links.items():
        inn = l.find("inertial")
        if inn is None:
            continue
        mass = float(inn.find("mass").get("value"))
        I = inn.find("inertia").attrib
        T = np.array([[float(I["ixx"]), float(I["ixy"]), float(I["ixz"])], [float(I["ixy"]), float(I["iyy"]), float(I["iyz"])],
                      [float(I["ixz"]), float(I["iyz"]), float(I["izz"])]])
        ev = np.linalg.eigvalsh(T)
        if mass <= 0 or ev.min() <= 0 or ev[2] > ev[0] + ev[1] + 1e-12:
            problems.append(f"link {n}: mass {mass}, principal inertia {ev} not physical")
    out["urdf_structure"] = {"links": len(links), "joints": len(joints), "revolute": sum(j.get("type") == "revolute" for j in joints),
                             "meshes": meshes}

    # the verified model, fixed at the pelvis
    design = Design(ROOT / "jx0" / "design_point.yaml")
    ref = mujoco.MjModel.from_xml_string(fixed_base(build(design)))
    # the URDF in MuJoCo: a temporary copy with the MuJoCo compiler extension (mesh folder, keep visuals)
    text = urdf.read_text(encoding="utf-8").replace('<robot name="jx0">', '<robot name="jx0">\n  <mujoco><compiler meshdir="'
                                                     + (HERE / "meshes").as_posix() + '" strippath="true" '
                                                     'discardvisual="false" fusestatic="false" balanceinertia="false"/></mujoco>')
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp) / "jx0.urdf"
        f.write_text(text, encoding="utf-8")
        mu = mujoco.MjModel.from_xml_path(str(f))
    spec = mujoco.MjSpec.from_file(str(HERE / "jx0.xml"))
    spec.meshdir = (HERE / "meshes").as_posix()
    for j in list(spec.joints):
        if j.name == "root":
            spec.delete(j)
    mx = spec.compile()

    # sole points: the verified model's sites; in the URDF, the fixed sole links; in the MJCF, its sites
    for label, m in (("urdf", mu), ("mjcf", mx)):
        d, dr = mujoco.MjData(m), mujoco.MjData(ref)
        names = [mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, i) for i in range(m.njnt)]
        mass = float(m.body_subtreemass[0] if label == "urdf" else m.body_subtreemass[1])
        mref = float(ref.body_subtreemass[1])
        rows = {"mass_kg": round(mass, 6), "verified_mass_kg": round(mref, 6)}
        if abs(mass - mref) > TOL_MASS:
            problems.append(f"{label}: mass {mass:.6f} vs verified {mref:.6f}")
        rng = np.random.default_rng(0)
        worst_com = worst_sole = travel = 0.0
        sole0 = None
        for k in range(200):
            q = {}
            for n in names:
                jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)
                lo, hi = m.jnt_range[jid]
                q[n] = 0.0 if k == 0 else float(rng.uniform(lo, hi))
                d.qpos[m.jnt_qposadr[jid]] = q[n]
                rj = mujoco.mj_name2id(ref, mujoco.mjtObj.mjOBJ_JOINT, short(n))
                dr.qpos[ref.jnt_qposadr[rj]] = q[n]
            com_r, (sl_r, sr_r) = snapshot(ref, dr, ["l_sole", "r_sole"])
            mujoco.mj_kinematics(m, d)
            mujoco.mj_comPos(m, d)
            if label == "urdf":
                com = d.subtree_com[0]
                soles = [d.xpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, f"{s}_sole_link")] for s in ("left", "right")]
            else:
                com = d.subtree_com[1]
                soles = [d.site_xpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, f"{s}_sole")] for s in ("left", "right")]
            # pelvis frame: the verified model's pelvis sits at its body pos; compare relative to each model's pelvis
            p_ref = dr.xpos[mujoco.mj_name2id(ref, mujoco.mjtObj.mjOBJ_BODY, "pelvis")]
            p_m = d.xpos[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "pelvis")]
            worst_com = max(worst_com, float(np.linalg.norm((com - p_m) - (com_r - p_ref))))
            worst_sole = max(worst_sole, max(float(np.linalg.norm((a - p_m) - (b - p_ref))) for a, b in zip(soles, (sl_r, sr_r))))
            sole0 = soles[0].copy() if sole0 is None else sole0
            travel = max(travel, float(np.linalg.norm(soles[0] - sole0)))      # the poses really differ
            if k == 0:
                Ii = composite_inertia(m, d)
                Ir = composite_inertia(ref, dr)
                # both about their own pelvis origin: shift the reference to its pelvis
                rows["composite_inertia_rel_err"] = float(np.abs(Ii - Ir).max() / np.abs(Ir).max())
        rows.update({"poses": 200, "worst_com_mm": round(worst_com * 1000, 6), "worst_sole_mm": round(worst_sole * 1000, 6),
                     "left_sole_travel_mm": round(travel * 1000, 1)})
        if rows["composite_inertia_rel_err"] > 1e-6:
            problems.append(f"{label}: composite inertia about the pelvis off by {rows['composite_inertia_rel_err']:.2e} (relative)")
        if travel < 0.05:
            problems.append(f"{label}: the random poses did not move the sole (joint names?)")
        if worst_com > TOL_POS or worst_sole > TOL_POS:
            problems.append(f"{label}: centre of mass off by {worst_com * 1000:.4f} mm, soles by {worst_sole * 1000:.4f} mm")
        out[label] = rows

    # limits
    cfg = yaml.safe_load((ROOT / "jx0" / "software" / "jx0bot" / "config.yaml").read_text(encoding="utf-8"))
    servos = {**cfg["leg_servos"], **cfg["arm_servos"]}
    jm = {j["name"]: j for j in yaml.safe_load((HERE / "joint_map.yaml").read_text(encoding="utf-8"))["joints"]}
    st = design.act_classes["ST"]
    for j in joints:
        if j.get("type") != "revolute":
            continue
        n = j.get("name")
        lim = j.find("limit").attrib
        want = [math.radians(v) for v in servos[short(n)]["limits_deg"]]
        got = [float(lim["lower"]), float(lim["upper"])]
        jid = mujoco.mj_name2id(mx, mujoco.mjtObj.mjOBJ_JOINT, n)
        if max(abs(a - b) for a, b in zip(got, want)) > 1e-5 or max(abs(a - b) for a, b in zip(mx.jnt_range[jid], want)) > 1e-5 \
                or max(abs(a - b) for a, b in zip((jm[n]["lower_rad"], jm[n]["upper_rad"]), want)) > 1e-5:
            problems.append(f"{n}: limits urdf {got}, mjcf {list(mx.jnt_range[jid])}, joint map vs config.yaml {want}")
        if abs(float(lim["effort"]) - st["stall_torque_nm"]) > 1e-9 or abs(float(lim["velocity"]) - st["no_load_speed_rad_s"]) > 1e-9:
            problems.append(f"{n}: effort / velocity {lim['effort']} / {lim['velocity']}")
    out["limits_checked"] = sum(j.get("type") == "revolute" for j in joints)
    out["problems"] = problems
    out["pass"] = not problems
    (HERE / "check.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k != "problems"}, indent=1))
    print(f"description check: {'PASS' if out['pass'] else 'FAIL'} ({len(problems)} problems)")
    for p in problems[:20]:
        print("  ", p)
    sys.exit(0 if out["pass"] else 1)


if __name__ == "__main__":
    main()
