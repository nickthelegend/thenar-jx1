"""Build JX1 simulation assets from the SolidWorks CAD: link meshes, mass properties, URDF and MuJoCo MJCF.

Pipeline
  1. read part STLs (part frame, mm) exported by tools/cad/export_meshes.py
  2. place every component at its zero-pose transform (tools/cad/leg_kinematics.py — the same transforms the SolidWorks
     assembly was built from and verified against), group components into URDF links, express them in the link frame
  3. mass properties from the CAD geometry with documented densities; actuators scaled to datasheet mass
  4. visual mesh per link (merged STL, metres), collision = CoACD convex decomposition per link (feet use a box sole)
  5. write ros2_ws/src/jx1_description/urdf/jx1.urdf and simulation/mujoco/jx1.xml (+ mass report)

Upper body: until phase-2 CAD exists, a documented 12 kg torso placeholder rides on waist_yaw_joint.
Usage: .venv/Scripts/python tools/sim/build_robot_description.py [--no-coacd]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import trimesh
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from cad.leg_kinematics import LegCAD  # noqa: E402
from cad.params import ACT, PKG, DP  # noqa: E402

SRC = ROOT / "simulation" / "meshes" / "source_mm"
PKG_DIR = ROOT / "ros2_ws" / "src" / "jx1_description"
MESH_DIR = PKG_DIR / "meshes"
MJ_DIR = ROOT / "simulation" / "mujoco"
JM = yaml.safe_load((ROOT / "simulation" / "joint_map.yaml").read_text(encoding="utf-8"))
CAT = yaml.safe_load((ROOT / "actuators" / "actuator_catalog.yaml").read_text(encoding="utf-8"))["classes"]

# densities kg/m^3 — labels: 6061/steel VERIFIED handbook values; printed-part effective density ESTIMATED (4 walls, 40 % gyroid)
DENSITY = {"PA-CF print": 800.0, "6061-T6": 2700.0, "steel": 7850.0, "rod assembly (M5 rod + rod ends in Ø8/Ø14 envelope)": 3000.0}
PART_MATERIAL = {"Pelvis": "PA-CF print", "HipYawBracket": "PA-CF print", "HipRollBracket": "PA-CF print", "Shin": "PA-CF print",
                 "Foot": "PA-CF print", "Thigh": "6061-T6", "AnkleCrank": "6061-T6", "AnkleCross": "steel",
                 "AnkleRod": "rod assembly (M5 rod + rod ends in Ø8/Ø14 envelope)"}
OUTPUT_MASS_SHARE = 0.15   # ESTIMATED share of actuator mass on the rotating output side
FASTENER_ALLOWANCE = 0.05  # ESTIMATED +5 % per structural link for screws, inserts, pins, bearings
LINK_OF = {"YawH": "pelvis", "YawO": "hip_yaw", "HipYawBr": "hip_yaw", "RollH": "hip_yaw", "RollO": "hip_roll", "HipRollBr": "hip_roll",
           "PitchH": "hip_roll", "PitchO": "thigh", "Thigh": "thigh", "KneeH": "thigh", "KneeO": "shin", "Shin": "shin",
           "AnkAH": "shin", "AnkBH": "shin", "AnkAO": "shin", "AnkBO": "shin", "CrankA": "shin", "CrankB": "shin",
           "RodA": "shin", "RodB": "shin", "Cross": "ankle_cross", "Foot": "foot"}
URDF_LINK = {"pelvis": "pelvis", "hip_yaw": "{s}_hip_yaw_link", "hip_roll": "{s}_hip_roll_link", "thigh": "{s}_thigh_link",
             "shin": "{s}_shin_link", "ankle_cross": "{s}_ankle_cross_link", "foot": "{s}_foot_link"}
TORSO_PLACEHOLDER = {"mass": 12.0, "com": [0.0, 0.0, 0.15], "box": [0.18, 0.28, 0.40],
                     "note": "phase-2 upper body (torso, battery, Jetson, electronics, arms, head) lumped — ASSUMED from design_point"}


def part_stem(key, side):
    sfx = "L" if side > 0 else "R"
    if key.startswith("ACT_"):
        return f"JX1_{key}"
    return {"HipYawBracket": f"JX1_HipYawBracket_{sfx}", "HipRollBracket": f"JX1_HipRollBracket_{sfx}", "Thigh": f"JX1_Thigh_{sfx}",
            "Shin": f"JX1_Shin_{sfx}", "Foot": f"JX1_Foot_{sfx}", "AnkleCrank": "JX1_AnkleCrank", "AnkleCross": "JX1_AnkleCross",
            "RodA": "JX1_AnkleRod_A", "RodB": "JX1_AnkleRod_B"}[key]


def load_mm(stem):
    m = trimesh.load(SRC / f"{stem}.STL", force="mesh")
    m.apply_scale(0.001)
    return m


def component_mass(stem, mesh):
    """Mass (kg) and material label for a component mesh."""
    if stem.startswith("JX1_ACT_"):
        cls = stem.split("_")[2]
        total = float(CAT[cls]["mass_kg"]["value"])
        share = OUTPUT_MASS_SHARE if stem.endswith("Output") else 1 - OUTPUT_MASS_SHARE
        return total * share, f"{CAT[cls]['product']} ({'output' if stem.endswith('Output') else 'housing'} share, VERIFIED total mass)"
    key = next(k for k in PART_MATERIAL if k in stem)
    mat = PART_MATERIAL[key]
    return abs(mesh.volume) * DENSITY[mat], mat


def rigid_props(mesh, mass):
    """COM and inertia (about COM) of a mesh scaled to `mass`."""
    mesh = mesh.copy()
    if not mesh.is_watertight:
        mesh.fill_holes()
    vol = abs(mesh.volume)
    mesh.density = mass / max(vol, 1e-12)
    return np.array(mesh.center_mass), np.array(mesh.moment_inertia)


def combine(items):
    """items: [(mass, com(3), inertia(3x3) about com)] -> total mass, com, inertia about com."""
    m = sum(i[0] for i in items)
    c = sum(i[0] * i[1] for i in items) / m
    I = np.zeros((3, 3))
    for mi, ci, Ii in items:
        d = ci - c
        I += Ii + mi * (np.dot(d, d) * np.eye(3) - np.outer(d, d))
    return m, c, I


def build_links(use_coacd=True):
    links = {}
    report = []
    # pelvis structure (identity) + both hip-yaw housings
    groups = {"pelvis": [("JX1_Pelvis", np.eye(4))]}
    for side, s in (("left", 1), ("right", -1)):
        leg = LegCAD(s)
        W = leg.links({})
        comp = leg.component_poses({})
        for key, (part, link, _) in leg.comps.items():
            lk = LINK_OF[key]
            name = URDF_LINK[lk].format(s=side)
            T_local = np.linalg.inv(W[lk if lk in W else "pelvis"]) @ comp[key]
            groups.setdefault(name, []).append((part_stem(part, s), T_local))
        for rod in ("RodA", "RodB"):
            name = URDF_LINK["shin"].format(s=side)
            groups[name].append((part_stem(rod, s), np.linalg.inv(W["shin"]) @ comp[rod]))
    MESH_DIR.mkdir(parents=True, exist_ok=True)
    (MESH_DIR / "collision").mkdir(exist_ok=True)
    for name, comps in groups.items():
        items, meshes = [], []
        for stem, T in comps:
            m = load_mm(stem)
            m.apply_transform(T)
            mass, mat = component_mass(stem, m)
            com, I = rigid_props(m, mass)
            items.append((mass, com, I))
            meshes.append(m)
            report.append({"link": name, "component": stem, "material": mat, "mass_kg": round(mass, 4)})
        mass, com, I = combine(items)
        if name != "pelvis" or True:
            structural = sum(i[0] for (stem, _), i in zip(comps, items) if not stem.startswith("JX1_ACT_"))
            extra = FASTENER_ALLOWANCE * structural
            mass += extra
        merged = trimesh.util.concatenate(meshes)
        merged.export(MESH_DIR / f"{name}.stl")
        hulls = []
        if use_coacd and name.endswith("foot_link") is False:
            try:
                import coacd
                cm = coacd.Mesh(merged.vertices, merged.faces)
                parts = coacd.run_coacd(cm, threshold=0.08, max_convex_hull=10, preprocess_mode="auto", resolution=1500)
                for k, (v, f) in enumerate(parts):
                    h = trimesh.Trimesh(v, f)
                    fn = f"collision/{name}_c{k}.stl"
                    h.export(MESH_DIR / fn)
                    hulls.append(fn)
            except Exception as e:  # pragma: no cover
                print("CoACD failed for", name, e)
        if not hulls:
            h = merged.convex_hull
            fn = f"collision/{name}_c0.stl"
            h.export(MESH_DIR / fn)
            hulls.append(fn)
        links[name] = {"mass": mass, "com": com, "inertia": I, "visual": f"{name}.stl", "collision": hulls,
                       "bbox": merged.bounds.tolist()}
        print(f"{name:26s} {mass:7.3f} kg  com {np.round(com, 4)}  hulls {len(hulls)}", flush=True)
    return links, report


def inertia_xml(I):
    return f'ixx="{I[0, 0]:.6e}" ixy="{I[0, 1]:.6e}" ixz="{I[0, 2]:.6e}" iyy="{I[1, 1]:.6e}" iyz="{I[1, 2]:.6e}" izz="{I[2, 2]:.6e}"'


def joint_by_name():
    return {j["name"]: j for j in JM["joints"]}


LEG_JOINT_ORDER = ["hip_yaw", "hip_roll", "hip_pitch", "knee", "ankle_pitch", "ankle_roll"]
CLASS_OF = {"hip_yaw": "M", "hip_roll": "L", "hip_pitch": "XL", "knee": "XL", "ankle_pitch": "ANKLE_P", "ankle_roll": "ANKLE_R", "waist_yaw": "M"}
EFFORT = {"XL": 120.0, "L": 60.0, "M": 36.0, "ANKLE_P": 46.0, "ANKLE_R": 51.0}   # ankle: linkage capability (min over range)
VELOCITY = {"XL": 20.9, "L": 20.9, "M": 50.3, "ANKLE_P": 30.0, "ANKLE_R": 30.0}
ARMATURE = {"XL": 0.040, "L": 0.020, "M": 0.010, "ANKLE_P": 0.020, "ANKLE_R": 0.016}   # ESTIMATED reflected rotor inertia
KP = {"XL": 200.0, "L": 150.0, "M": 80.0, "ANKLE_P": 80.0, "ANKLE_R": 40.0}
KD = {"XL": 5.0, "L": 4.0, "M": 2.0, "ANKLE_P": 2.0, "ANKLE_R": 1.5}


def write_urdf(links):
    J = joint_by_name()
    out = ['<?xml version="1.0"?>', '<!-- JX1 lower body + torso placeholder. Generated by tools/sim/build_robot_description.py from the SolidWorks CAD. -->',
           '<robot name="jx1">']

    def link(name, L):
        c = L["com"]
        s = [f'  <link name="{name}">', '    <inertial>', f'      <origin xyz="{c[0]:.6f} {c[1]:.6f} {c[2]:.6f}" rpy="0 0 0"/>',
             f'      <mass value="{L["mass"]:.5f}"/>', f'      <inertia {inertia_xml(L["inertia"])}/>', '    </inertial>',
             '    <visual>', f'      <geometry><mesh filename="package://jx1_description/meshes/{L["visual"]}"/></geometry>', '    </visual>']
        for h in L["collision"]:
            s += ['    <collision>', f'      <geometry><mesh filename="package://jx1_description/meshes/{h}"/></geometry>', '    </collision>']
        s.append('  </link>')
        return s

    for name, L in links.items():
        out += link(name, L)
    tp = TORSO_PLACEHOLDER
    I = np.diag([tp["mass"] / 12 * (tp["box"][1] ** 2 + tp["box"][2] ** 2), tp["mass"] / 12 * (tp["box"][0] ** 2 + tp["box"][2] ** 2),
                 tp["mass"] / 12 * (tp["box"][0] ** 2 + tp["box"][1] ** 2)])
    out += ['  <link name="torso_link">', '    <inertial>', f'      <origin xyz="{tp["com"][0]} {tp["com"][1]} {tp["com"][2]}" rpy="0 0 0"/>',
            f'      <mass value="{tp["mass"]}"/>', f'      <inertia {inertia_xml(I)}/>', '    </inertial>', '    <visual>',
            f'      <origin xyz="{tp["com"][0]} {tp["com"][1]} {tp["com"][2]}"/>', f'      <geometry><box size="{tp["box"][0]} {tp["box"][1]} {tp["box"][2]}"/></geometry>',
            '    </visual>', '  </link>']
    for side in ("left", "right"):
        for jn in LEG_JOINT_ORDER:
            j = J[f"{side}_{jn}_joint"]
            cls = CLASS_OF[jn]
            parent = "pelvis" if jn == "hip_yaw" else j["parent"]
            o = j["origin_xyz_m"]
            out += [f'  <joint name="{j["name"]}" type="revolute">', f'    <parent link="{parent}"/>', f'    <child link="{j["child"]}"/>',
                    f'    <origin xyz="{o[0]} {o[1]} {o[2]}" rpy="0 0 0"/>', f'    <axis xyz="{j["axis"][0]} {j["axis"][1]} {j["axis"][2]}"/>',
                    f'    <limit lower="{j["lower_rad"]}" upper="{j["upper_rad"]}" effort="{EFFORT[cls]}" velocity="{VELOCITY[cls]}"/>',
                    '    <dynamics damping="0.05" friction="0.3"/>', '  </joint>']
    w = J["waist_yaw_joint"]
    out += ['  <joint name="waist_yaw_joint" type="revolute">', '    <parent link="pelvis"/>', '    <child link="torso_link"/>',
            f'    <origin xyz="{w["origin_xyz_m"][0]} {w["origin_xyz_m"][1]} {w["origin_xyz_m"][2]}" rpy="0 0 0"/>', '    <axis xyz="0 0 1"/>',
            f'    <limit lower="{w["lower_rad"]}" upper="{w["upper_rad"]}" effort="36" velocity="50.3"/>', '  </joint>', '</robot>']
    (PKG_DIR / "urdf").mkdir(parents=True, exist_ok=True)
    (PKG_DIR / "urdf" / "jx1.urdf").write_text("\n".join(out), encoding="utf-8")


def write_mjcf(links):
    J = joint_by_name()
    ms = ['<mujoco model="jx1">', '  <!-- Generated by tools/sim/build_robot_description.py from the SolidWorks CAD; lower body + torso placeholder. -->',
          '  <compiler angle="radian" meshdir="../../ros2_ws/src/jx1_description/meshes" autolimits="true"/>',
          '  <option timestep="0.002" integrator="implicitfast" cone="elliptic" impratio="10"/>',
          '  <default>', '    <joint damping="0.05" frictionloss="0.3"/>',
          '    <geom contype="1" conaffinity="1" friction="0.9 0.02 0.001" solref="0.004 1"/>',
          '    <default class="visual"><geom contype="0" conaffinity="0" group="2" type="mesh"/></default>',
          '    <default class="collision"><geom group="3" type="mesh" rgba=".5 .5 .5 .3"/></default>', '  </default>', '  <asset>']
    for name, L in links.items():
        ms.append(f'    <mesh name="{name}_vis" file="{L["visual"]}"/>')
        for k, h in enumerate(L["collision"]):
            ms.append(f'    <mesh name="{name}_col{k}" file="{h}"/>')
    ms += ['    <texture name="grid" type="2d" builtin="checker" rgb1=".85 .87 .9" rgb2=".75 .78 .82" width="512" height="512"/>',
           '    <material name="grid" texture="grid" texrepeat="8 8"/>', '  </asset>', '  <worldbody>',
           '    <geom name="floor" type="plane" size="0 0 0.05" material="grid"/>', '    <light pos="0 0 3" dir="0 0 -1" directional="true"/>']
    colors = {"pelvis": ".16 .16 .17 1", "hip_yaw": ".18 .19 .21 1", "hip_roll": ".18 .19 .21 1", "thigh": ".80 .81 .83 1",
              "shin": ".16 .16 .17 1", "ankle_cross": ".6 .61 .63 1", "foot": ".95 .42 .10 1"}

    def body_inertial(L):
        c = L["com"]
        I = L["inertia"]
        return (f'<inertial pos="{c[0]:.6f} {c[1]:.6f} {c[2]:.6f}" mass="{L["mass"]:.5f}" '
                f'fullinertia="{I[0, 0]:.6e} {I[1, 1]:.6e} {I[2, 2]:.6e} {I[0, 1]:.6e} {I[0, 2]:.6e} {I[1, 2]:.6e}"/>')

    def geoms(name, key):
        rgba = next((v for k, v in colors.items() if k in name), ".5 .5 .5 1")
        g = [f'<geom class="visual" mesh="{name}_vis" rgba="{rgba}"/>']
        if key == "foot":
            d = DP["geometry"]
            L_, W_, h_ = d["foot"]["length_m"]["value"], d["foot"]["width_m"]["value"], d["sole_to_ankle_m"]["value"]
            heel = d["foot"]["ankle_from_heel_m"]["value"]
            g.append(f'<geom name="{name}_sole" type="box" size="{L_ / 2:.4f} {W_ / 2:.4f} 0.005" pos="{L_ / 2 - heel:.4f} 0 {-h_ + 0.005:.4f}" rgba=".1 .1 .1 1"/>')
        else:
            for k in range(len(links[name]["collision"])):
                g.append(f'<geom class="collision" mesh="{name}_col{k}"/>')
        return g

    ms.append('    <body name="pelvis" pos="0 0 0.64">')
    ms.append('      <freejoint name="root"/>')
    ms.append("      " + body_inertial(links["pelvis"]))
    ms += ["      " + g for g in geoms("pelvis", "pelvis")]
    ms.append('      <site name="imu" pos="0 0 0.05" size="0.01"/>')
    tp = TORSO_PLACEHOLDER
    w = J["waist_yaw_joint"]
    ms += [f'      <body name="torso_link" pos="{w["origin_xyz_m"][0]} {w["origin_xyz_m"][1]} {w["origin_xyz_m"][2]}">',
           f'        <joint name="waist_yaw_joint" axis="0 0 1" range="{w["lower_rad"]} {w["upper_rad"]}" armature="0.01"/>',
           f'        <inertial pos="{tp["com"][0]} {tp["com"][1]} {tp["com"][2]}" mass="{tp["mass"]}" diaginertia="0.24 0.19 0.11"/>',
           f'        <geom type="box" size="{tp["box"][0] / 2} {tp["box"][1] / 2} {tp["box"][2] / 2}" pos="{tp["com"][0]} {tp["com"][1]} {tp["com"][2]}" rgba=".92 .92 .94 1" contype="0" conaffinity="0"/>',
           '      </body>']
    for side in ("left", "right"):
        depth = 0
        for jn in LEG_JOINT_ORDER:
            j = J[f"{side}_{jn}_joint"]
            cls = CLASS_OF[jn]
            child = j["child"]
            key = next(k for k in colors if k in child) if any(k in child for k in colors) else ""
            o = j["origin_xyz_m"]
            ind = "      " + "  " * depth
            ms.append(f'{ind}<body name="{child}" pos="{o[0]} {o[1]} {o[2]}">')
            ms.append(f'{ind}  <joint name="{j["name"]}" axis="{j["axis"][0]} {j["axis"][1]} {j["axis"][2]}" range="{j["lower_rad"]} {j["upper_rad"]}" armature="{ARMATURE[cls]}"/>')
            ms.append(f'{ind}  ' + body_inertial(links[child]))
            ms += [f'{ind}  ' + g for g in geoms(child, "foot" if "foot" in child else key)]
            if "foot" in child:
                ms.append(f'{ind}  <site name="{side}_sole" pos="0 0 {-DP["geometry"]["sole_to_ankle_m"]["value"]}" size="0.01"/>')
            depth += 1
        ms.append("      " + "</body>" * depth)
    ms += ['    </body>', '  </worldbody>', '  <actuator>']
    for side in ("left", "right"):
        for jn in LEG_JOINT_ORDER:
            cls = CLASS_OF[jn]
            ms.append(f'    <position name="{side}_{jn}" joint="{side}_{jn}_joint" kp="{KP[cls]}" kv="{KD[cls]}" forcerange="{-EFFORT[cls]} {EFFORT[cls]}"/>')
    ms.append('    <position name="waist_yaw" joint="waist_yaw_joint" kp="80" kv="2" forcerange="-36 36"/>')
    ms += ['  </actuator>', '  <sensor>', '    <framequat name="imu_quat" objtype="site" objname="imu"/>', '    <gyro name="imu_gyro" site="imu"/>',
           '    <accelerometer name="imu_acc" site="imu"/>', '    <touch name="left_foot_touch" site="left_sole"/>',
           '    <touch name="right_foot_touch" site="right_sole"/>', '  </sensor>', '</mujoco>']
    MJ_DIR.mkdir(parents=True, exist_ok=True)
    (MJ_DIR / "jx1.xml").write_text("\n".join(ms), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-coacd", action="store_true")
    a = ap.parse_args()
    links, report = build_links(not a.no_coacd)
    write_urdf(links)
    write_mjcf(links)
    total = sum(L["mass"] for L in links.values()) + TORSO_PLACEHOLDER["mass"]
    summary = {"total_mass_kg": round(total, 3), "torso_placeholder": TORSO_PLACEHOLDER, "densities_kg_m3": DENSITY,
               "output_mass_share": OUTPUT_MASS_SHARE, "fastener_allowance": FASTENER_ALLOWANCE,
               "links": {n: {"mass_kg": round(L["mass"], 4), "com_m": [round(float(x), 5) for x in L["com"]],
                             "inertia_diag_kgm2": [float(f"{x:.4e}") for x in np.diag(L["inertia"])], "collision_hulls": len(L["collision"])}
                         for n, L in links.items()},
               "components": report}
    (ROOT / "simulation" / "mass_properties.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"TOTAL modelled mass {total:.2f} kg (incl. {TORSO_PLACEHOLDER['mass']} kg torso placeholder)")


if __name__ == "__main__":
    main()
