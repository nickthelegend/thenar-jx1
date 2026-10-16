"""JX0 robot description for reinforcement learning, in the conventions of JX1's training stack (rl/, Isaac Lab):

    python jx0/description/build_description.py
        -> jx0/description/jx0.xml          MJCF (MuJoCo training: rl/train.py --config jx0/rl/config/jx0_walk.yaml)
           jx0/description/joint_map.yaml   joints, limits, actuator class, sole frames, coupled limits
           jx0/description/urdf/jx0.urdf   URDF (Isaac Sim URDF importer -> USD, Isaac Lab)

Everything comes from the verified JX0 model (jx0/sim/jx0_model.py: CAD masses, inertias, joint frames) and the
robot's own config (jx0/software/jx0bot/config.yaml: the commanded joint limits, servo stiffness and damping) - nothing
about the robot is re-typed. Renamed to the training conventions: l_knee -> left_knee_joint, l_shin -> left_shin_link,
l_sole -> left_sole, the foot box -> left_foot_link_sole. The servos become position actuators (stiffness / damping of
config.yaml, +-stall torque); thighs, shins, pelvis and torso carry their CAD meshes as collision group 3, from which
rl/jx1_rl/assets.py fits capsules and boxes. Meshes: copied from jx0/cad/stl_engraved into jx0/description/meshes,
so this folder works on its own (MuJoCo: python -m mujoco.viewer --mjcf jx0/description/jx0.xml).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import mujoco
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "jx0" / "sim"))
sys.path.insert(0, str(ROOT / "calculations"))
import os  # noqa: E402

os.environ["JX0_STL_DIR"] = str(ROOT / "jx0" / "cad" / "stl_engraved")      # jx0_model reads its meshes there
from jx0_model import build  # noqa: E402
from jx1calc.design import Design  # noqa: E402

OUT = ROOT / "jx0" / "description"
SOURCE_MESHES = ROOT / "jx0" / "cad" / "stl_engraved"     # the print meshes (SolidWorks + lettering)
MESHES = OUT / "meshes"                                    # copied here: the description stands on its own
CONFIG = ROOT / "jx0" / "software" / "jx0bot" / "config.yaml"
SIDES = {"l": "left", "r": "right"}
LINKS = {"hip_yaw_link": "hip_yaw_link", "hip_roll_link": "hip_roll_link", "thigh": "thigh_link", "shin": "shin_link",
         "ankle_cross": "ankle_pitch_link", "foot": "foot_link", "upper_arm": "upper_arm_link", "forearm": "forearm_link"}
COLLISION_MESH_LINKS = ("thigh_link", "shin_link")           # + pelvis, torso_link (rl/jx1_rl/assets.py fits primitives)


def body_name(n: str) -> str:
    if n in ("pelvis", "world"):
        return n
    if n == "torso":
        return "torso_link"
    if n == "head":
        return "head_link"
    s, rest = n.split("_", 1)
    return f"{SIDES[s]}_{LINKS[rest]}"


def joint_name(n: str) -> str:
    if n == "neck_yaw":
        return "neck_yaw_joint"
    s, rest = n.split("_", 1)
    return f"{SIDES[s]}_{rest}_joint"


def quat_to_rpy(q):
    w, x, y, z = q
    roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
    pitch = math.asin(max(-1.0, min(1.0, 2 * (w * y - z * x))))
    yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    return [roll, pitch, yaw]


def fmt(v, n=6):
    return " ".join(f"{float(a):.{n}g}" for a in v)


def main():
    design = Design(ROOT / "jx0" / "design_point.yaml")
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    servos = {**cfg["leg_servos"], **cfg["arm_servos"]}
    st = design.act_classes["ST"]
    kp, kd = float(cfg["bus"]["stiffness_nm_per_rad"]), float(cfg["bus"]["damping_nm_s_per_rad"])
    spec = mujoco.MjSpec.from_string(build(design))
    ref = spec.compile()

    # ---- rename to the training conventions, meshes relative to the description
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "urdf").mkdir(exist_ok=True)
    MESHES.mkdir(exist_ok=True)
    import shutil
    for mesh in spec.meshes:
        shutil.copyfile(SOURCE_MESHES / Path(mesh.file).name, MESHES / Path(mesh.file).name)
    rel = os.path.relpath(MESHES, OUT).replace("\\", "/")
    spec.meshdir = rel
    for m in spec.meshes:
        m.file = Path(m.file).name
    for b in spec.bodies:
        if b.name and b.name != "world":
            b.name = body_name(b.name)
    for j in spec.joints:
        if j.name and j.name != "root":
            old = j.name
            j.name = joint_name(old)
            lo, hi = servos[old]["limits_deg"]
            j.range = [math.radians(lo), math.radians(hi)]
            j.limited = mujoco.mjtLimited.mjLIMITED_TRUE
    for s in spec.sites:
        if s.name in ("l_sole", "r_sole"):
            s.name = f"{SIDES[s.name[0]]}_sole"
        elif s.name in ("l_hand", "r_hand"):
            s.name = f"{SIDES[s.name[0]]}_hand"
    for g in spec.geoms:
        if g.name in ("l_foot_geom", "r_foot_geom"):
            g.name = f"{SIDES[g.name[0]]}_foot_link_sole"
    # collision meshes (group 3) on the links whose primitives rl/jx1_rl/assets.py fits
    for b in spec.bodies:
        if any(k in (b.name or "") for k in COLLISION_MESH_LINKS + ("pelvis", "torso_link")):
            for g in list(b.geoms):
                if g.type == mujoco.mjtGeom.mjGEOM_MESH and "Servo" not in g.meshname:
                    b.add_geom(type=mujoco.mjtGeom.mjGEOM_MESH, meshname=g.meshname, pos=g.pos, quat=g.quat, group=3,
                               contype=0, conaffinity=0, density=0, rgba=[0.5, 0.5, 0.5, 0.0])
    # servos -> position actuators (stiffness / damping as the STS3215 registers are set, +- stall torque)
    for a in list(spec.actuators):
        spec.delete(a)
    joints = [j.name for j in spec.joints if j.name and j.name != "root"]
    for jn in joints:
        j = spec.joint(jn)
        spec.add_actuator(name=jn, target=jn, trntype=mujoco.mjtTrn.mjTRN_JOINT, gaintype=mujoco.mjtGain.mjGAIN_FIXED,
                          biastype=mujoco.mjtBias.mjBIAS_AFFINE, gainprm=[kp] + [0] * 9, biasprm=[0, -kp, -kd] + [0] * 7,
                          ctrlrange=list(j.range), ctrllimited=mujoco.mjtLimited.mjLIMITED_TRUE,
                          forcerange=[-st["stall_torque_nm"], st["stall_torque_nm"]],
                          forcelimited=mujoco.mjtLimited.mjLIMITED_TRUE)
    spec.meshdir = MESHES.as_posix()                           # absolute to compile here, relative in the file
    m = spec.compile()
    xml = spec.to_xml().replace(f'meshdir="{MESHES.as_posix()}', f'meshdir="{rel}')
    assert f'meshdir="{rel}' in xml
    (OUT / "jx0.xml").write_text("<!-- generated by jx0/description/build_description.py from jx0/sim/jx0_model.py: do not edit -->\n"
                                 + xml, encoding="utf-8")

    # ---- joint map
    jm = {"robot": "JX0", "generated_by": "jx0/description/build_description.py",
          "conventions": {"frames": "x forward, y left, z up (REP-103); joint angles as jx0/software/jx0bot (config.yaml)",
                          "base_link": "pelvis", "zero_pose": "legs straight down and parallel, feet flat, arms hanging",
                          "limits": "the commanded limits of config.yaml (each servo stores them 1 deg wider)"},
          "joints": [], "fixed_frames": [], "coupled_limits": {}}
    for jn in joints:
        jid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, jn)
        b = m.jnt_bodyid[jid]
        lo, hi = m.jnt_range[jid]
        jm["joints"].append({
            "name": jn, "type": "revolute", "parent": mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.body_parentid[b]),
            "child": mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, b),
            "origin_xyz_m": [round(float(v), 6) for v in m.body_pos[b]],
            "origin_rpy_rad": [round(v, 6) for v in quat_to_rpy(m.body_quat[b])],
            "axis": [round(float(v), 6) for v in m.jnt_axis[jid]],
            "lower_rad": round(float(lo), 6), "upper_rad": round(float(hi), 6),
            "lower_deg": round(math.degrees(lo), 1), "upper_deg": round(math.degrees(hi), 1),
            "actuator_class": "ST", "effort_nm": st["stall_torque_nm"], "velocity_rad_s": st["no_load_speed_rad_s"]})
    for s in ("left", "right"):
        sid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, f"{s}_sole")
        jm["fixed_frames"].append({"name": f"{s}_sole_fixed", "type": "fixed", "parent": f"{s}_foot_link",
                                   "child": f"{s}_sole_link", "origin_xyz_m": [round(float(v), 6) for v in m.site_pos[sid]],
                                   "origin_rpy_rad": [0, 0, 0]})
    lim = {j["name"]: (j["lower_deg"], j["upper_deg"]) for j in jm["joints"]}
    poly = {}
    for s in ("left", "right"):
        (p0, p1), (r0, r1) = lim[f"{s}_ankle_pitch_joint"], lim[f"{s}_ankle_roll_joint"]
        poly[f"{s}_polygon_deg"] = [[p0, r0], [p1, r0], [p1, r1], [p0, r1]]     # serial ankle: the limits' rectangle
    jm["coupled_limits"]["ankle_pitch_roll"] = {"joints": ["ankle_pitch", "ankle_roll"], **poly}
    jm["coupled_limits"]["hip_roll_vs_pitch"] = {
        "note": "jx0bot.robot.couple_hips: roll toward the leg's own side <= max(10, min(20, 22 - 0.5 (-30 - pitch_deg))), "
                "toward the middle >= min(-12, max(-20, -20 + 0.5 (-34 - pitch_deg))) (right leg mirrored); "
                "verify_stops.py"}
    (OUT / "joint_map.yaml").write_text("# generated by jx0/description/build_description.py: do not edit\n"
                                        + yaml.safe_dump(jm, sort_keys=False), encoding="utf-8")

    # ---- URDF (Isaac Sim URDF importer): links with CAD inertia, mesh visuals, sole boxes + mesh hull collisions
    mesh_rel = os.path.relpath(MESHES, OUT / "urdf").replace("\\", "/")
    L = ['<?xml version="1.0"?>', "<!-- generated by jx0/description/build_description.py: do not edit -->", '<robot name="jx0">']
    R = np.zeros(9)
    for b in range(1, m.nbody):
        name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, b)
        mujoco.mju_quat2Mat(R, m.body_iquat[b])
        Rm = R.reshape(3, 3)
        I = Rm @ np.diag(m.body_inertia[b]) @ Rm.T
        L += [f'  <link name="{name}">', "    <inertial>", f'      <origin xyz="{fmt(m.body_ipos[b])}" rpy="0 0 0"/>',
              f'      <mass value="{m.body_mass[b]:.6g}"/>',
              f'      <inertia ixx="{I[0, 0]:.6g}" ixy="{I[0, 1]:.6g}" ixz="{I[0, 2]:.6g}" iyy="{I[1, 1]:.6g}" '
              f'iyz="{I[1, 2]:.6g}" izz="{I[2, 2]:.6g}"/>', "    </inertial>"]
        sb = spec.body(name)
        for g in sb.geoms:
            if g.type == mujoco.mjtGeom.mjGEOM_MESH and g.group != 3:
                f = spec.mesh(g.meshname).file
                origin = f'<origin xyz="{fmt(g.pos)}" rpy="{fmt(quat_to_rpy(g.quat))}"/>'
                L += ["    <visual>", f"      {origin}",
                      f'      <geometry><mesh filename="{mesh_rel}/{f}" scale="0.001 0.001 0.001"/></geometry>', "    </visual>"]
                if any(k in name for k in COLLISION_MESH_LINKS) and "Servo" not in f:
                    L += ["    <collision>", f"      {origin}",
                          f'      <geometry><mesh filename="{mesh_rel}/{f}" scale="0.001 0.001 0.001"/></geometry>',
                          "    </collision>"]
            elif g.name.endswith("_sole") and g.type == mujoco.mjtGeom.mjGEOM_BOX:
                L += [f'    <collision name="{g.name}">', f'      <origin xyz="{fmt(g.pos)}" rpy="{fmt(quat_to_rpy(g.quat))}"/>',
                      f'      <geometry><box size="{fmt(2 * np.asarray(g.size))}"/></geometry>', "    </collision>"]
        L.append("  </link>")
    for b in range(2, m.nbody):
        name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, b)
        parent = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, m.body_parentid[b])
        origin = f'<origin xyz="{fmt(m.body_pos[b])}" rpy="{fmt(quat_to_rpy(m.body_quat[b]))}"/>'
        jids = [j for j in range(m.njnt) if m.jnt_bodyid[j] == b]
        if jids:
            j = jids[0]
            jn = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j)
            lo, hi = m.jnt_range[j]
            L += [f'  <joint name="{jn}" type="revolute">', f"    {origin}", f'    <parent link="{parent}"/>',
                  f'    <child link="{name}"/>', f'    <axis xyz="{fmt(m.jnt_axis[j])}"/>',
                  f'    <limit lower="{lo:.6g}" upper="{hi:.6g}" effort="{st["stall_torque_nm"]}" velocity="{st["no_load_speed_rad_s"]}"/>',
                  f'    <dynamics damping="{m.dof_damping[m.jnt_dofadr[j]]:.6g}" friction="0"/>', "  </joint>"]
        else:
            L += [f'  <joint name="{name}_fixed" type="fixed">', f"    {origin}", f'    <parent link="{parent}"/>',
                  f'    <child link="{name}"/>', "  </joint>"]
    for fr in jm["fixed_frames"]:
        L += [f'  <link name="{fr["child"]}"/>', f'  <joint name="{fr["name"]}" type="fixed">',
              f'    <origin xyz="{fmt(fr["origin_xyz_m"])}" rpy="0 0 0"/>', f'    <parent link="{fr["parent"]}"/>',
              f'    <child link="{fr["child"]}"/>', "  </joint>"]
    L.append("</robot>")
    (OUT / "urdf" / "jx0.urdf").write_text("\n".join(L) + "\n", encoding="utf-8")

    # ---- self-check: the description has the verified model's masses and joints
    mass = float(m.body_subtreemass[1])
    assert abs(mass - float(ref.body_subtreemass[1])) < 1e-9, "mass changed"
    print(f"{(OUT / 'jx0.xml').relative_to(ROOT)}: {m.nbody - 1} bodies, {len(joints)} joints, {m.nu} position actuators "
          f"(kp {kp:g} N m/rad, kd {kd:g}, +-{st['stall_torque_nm']} N m), {mass:.3f} kg")
    print(f"{(OUT / 'joint_map.yaml').relative_to(ROOT)}, {(OUT / 'urdf' / 'jx0.urdf').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
