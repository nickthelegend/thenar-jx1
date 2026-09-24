"""Build JX1 simulation assets from the SolidWorks CAD: link meshes, mass properties, URDF and MuJoCo MJCF.

Pipeline
  1. read part STLs (part frame, mm) exported by tools/cad/export_meshes.py
  2. place every component at its zero-pose transform (tools/cad/leg_kinematics.py — the same transforms the SolidWorks
     assembly was built from and verified against), group components into URDF links, express them in the link frame
  3. mass properties from the CAD geometry with documented densities; actuators scaled to datasheet mass
  4. visual mesh per link (merged STL, metres), collision = CoACD convex decomposition per link (feet use a box sole)
  5. write ros2_ws/src/jx1_description/urdf/jx1.urdf and simulation/mujoco/jx1.xml (+ mass report)

Upper body: built from the phase-2 CAD (tools/cad/upper_kinematics.py) when its meshes exist; otherwise a documented
torso placeholder (design_point mass budget) rides on waist_yaw_joint.
URDF and MJCF are written generically from simulation/joint_map.yaml (23 revolute joints + fixed hand/sole/imu frames).
Usage: .venv/Scripts/python tools/sim/build_robot_description.py [--no-coacd] [--placeholder-torso]
"""
from __future__ import annotations

import argparse
import hashlib
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
DENSITY = {"PA-CF print": 800.0, "6061-T6": 2700.0, "7075-T6": 2810.0, "steel": 7850.0,
           "rod assembly (Ø8 steel rod + 2x POS5 in Ø8/Ø14 envelope)": 7500.0,
           "torso frame (6061 plates + 2020 posts modelled solid)": 2240.0, "PETG-CF shell": 1100.0}
PART_MATERIAL = {"Pelvis": "6061-T6", "HipYawBracket": "7075-T6", "HipRollBracket": "6061-T6", "Shin": "6061-T6",
                 "Foot": "6061-T6", "Thigh": "6061-T6", "AnkleCrank": "6061-T6", "AnkleCross": "steel",
                 "AnkleRod": "rod assembly (Ø8 steel rod + 2x POS5 in Ø8/Ø14 envelope)",
                 "Torso": "torso frame (6061 plates + 2020 posts modelled solid)", "ShoulderPitchBracket": "6061-T6",
                 "ShoulderRollBracket": "6061-T6", "UpperArm": "6061-T6", "Forearm": "6061-T6", "NeckBracket": "PA-CF print",
                 "Head": "PETG-CF shell"}
# bought-in / envelope parts: mass from datasheets / BOM (kg)
FIXED_MASS = {"JX1_BatteryPack": (2.05, "26 x Samsung 50S 69 g + BMS/wiring (CALCULATED)"), "JX1_JetsonNano": (0.25, "BOM"),
              "JX1_HubBoard": (0.08, "ESTIMATED"), "JX1_DCDC5V": (0.20, "ESTIMATED"), "JX1_PowerSwitch": (0.12, "ESTIMATED"),
              "JX1_EStop": (0.10, "ESTIMATED"), "JX1_Gripper": (0.25, "BOM"), "JX1_Servo_ST3215_Body": (0.050, "ESTIMATED"),
              "JX1_Servo_ST3215_Horn": (0.005, "ESTIMATED"), "JX1_StereoCamera": (0.04, "ESTIMATED")}
OUTPUT_MASS_SHARE = 0.15   # ESTIMATED share of actuator mass on the rotating output side
FASTENER_ALLOWANCE = 0.05  # ESTIMATED +5 % per structural link for screws, inserts, pins, bearings
LINK_OF = {"YawH": "pelvis", "YawO": "hip_yaw", "HipYawBr": "hip_yaw", "RollH": "hip_yaw", "RollO": "hip_roll", "HipRollBr": "hip_roll",
           "PitchH": "hip_roll", "PitchO": "thigh", "Thigh": "thigh", "KneeH": "thigh", "KneeO": "shin", "Shin": "shin",
           "AnkAH": "shin", "AnkBH": "shin", "AnkAO": "shin", "AnkBO": "shin", "CrankA": "shin", "CrankB": "shin",
           "RodA": "shin", "RodB": "shin", "Cross": "ankle_cross", "Foot": "foot"}
URDF_LINK = {"pelvis": "pelvis", "hip_yaw": "{s}_hip_yaw_link", "hip_roll": "{s}_hip_roll_link", "thigh": "{s}_thigh_link",
             "shin": "{s}_shin_link", "ankle_cross": "{s}_ankle_cross_link", "foot": "{s}_foot_link"}
_UB = DP["mass_budget"]["upper_body"]
_WAIST = DP["upper_body_geometry"]["waist_yaw_origin"]["value"]
TORSO_PLACEHOLDER = {"mass": float(_UB["mass_kg"]["value"]),
                     "com": [float(_UB["com_m"][k] - _WAIST[k]) for k in range(3)],     # design-point COM (pelvis frame) in the torso frame
                     "box": [0.18, 0.28, 0.40],
                     "note": "phase-2 upper body (torso, battery, Jetson, electronics, arms, head) lumped — ASSUMED from design_point"}


HULL_CACHE = {}                 # link name -> {"key": md5 of merged mesh, "hulls": [files]} (meshes/collision/cache.json)


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
    if stem in FIXED_MASS:
        return FIXED_MASS[stem][0], f"fixed mass ({FIXED_MASS[stem][1]})"
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


UPPER_LINK = {"pelvis": "pelvis", "torso": "torso_link", "neck": "neck_link", "head": "head_link"}
for _S, _n in (("L", "left"), ("R", "right")):
    UPPER_LINK.update({f"{_S}_shoulder_pitch": f"{_n}_shoulder_pitch_link", f"{_S}_shoulder_roll": f"{_n}_shoulder_roll_link",
                       f"{_S}_upper_arm": f"{_n}_upper_arm_link", f"{_S}_forearm": f"{_n}_forearm_link",
                       f"{_S}_hand": f"{_n}_forearm_link"})          # gripper merged into the forearm (hand_link = fixed frame)


def upper_stem(key, part):
    if part.startswith("ACT_"):
        return f"JX1_{part}"
    if part in ("ShoulderPitchBracket", "ShoulderRollBracket", "UpperArm", "Forearm"):
        return f"JX1_{part}_{key[0]}"
    return f"JX1_{part}"


def upper_groups():
    """Upper-body components grouped per URDF link (component transform in the link frame)."""
    from cad.upper_kinematics import UpperCAD
    uc = UpperCAD()
    W = uc.links({})
    comp = uc.component_poses({})
    groups = {}
    for key, (part, link, _) in uc.comps.items():
        if key == "Pelvis":
            continue
        urdf = UPPER_LINK[link]
        frame = {"L_hand": "L_forearm", "R_hand": "R_forearm"}.get(link, link)
        groups.setdefault(urdf, []).append((upper_stem(key, part), np.linalg.inv(W[frame]) @ comp[key]))
    return groups


def upper_available():
    try:
        return all((SRC / f"{stem}.STL").exists() for g in upper_groups().values() for stem, _ in g)
    except Exception:
        return False


def build_links(use_coacd=True, upper=True):
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
    if upper:
        for name, comps in upper_groups().items():
            groups.setdefault(name, []).extend(comps)
    MESH_DIR.mkdir(parents=True, exist_ok=True)
    (MESH_DIR / "collision").mkdir(exist_ok=True)
    cache_file = MESH_DIR / "collision" / "cache.json"
    HULL_CACHE.update(json.loads(cache_file.read_text()) if cache_file.exists() else {})
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
        key = hashlib.md5(np.round(merged.vertices, 6).tobytes() + merged.faces.astype(np.int64).tobytes()).hexdigest()
        cached = HULL_CACHE.get(name)
        if use_coacd and cached and cached["key"] == key and all((MESH_DIR / h).exists() for h in cached["hulls"]):
            hulls = list(cached["hulls"])                  # geometry unchanged since the last decomposition
        elif use_coacd and name.endswith("foot_link") is False:
            try:
                import coacd
                cm = coacd.Mesh(merged.vertices, merged.faces)
                parts = coacd.run_coacd(cm, threshold=0.08, max_convex_hull=10, preprocess_mode="auto", resolution=1500)
                for k, (v, f) in enumerate(parts):
                    h = trimesh.Trimesh(v, f)
                    fn = f"collision/{name}_c{k}.stl"
                    h.export(MESH_DIR / fn)
                    hulls.append(fn)
                HULL_CACHE[name] = {"key": key, "hulls": hulls}
                (MESH_DIR / "collision" / "cache.json").write_text(json.dumps(HULL_CACHE, indent=1))
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
CLASS_OF = {"hip_yaw": "M", "hip_roll": "L", "hip_pitch": "XL", "knee": "XL", "ankle_pitch": "ANKLE_P", "ankle_roll": "ANKLE_R", "waist_yaw": "M",
            "shoulder_pitch": "S", "shoulder_roll": "S", "shoulder_yaw": "XS", "elbow": "XS", "neck_yaw": "SERVO", "neck_pitch": "SERVO"}
# peak torque N m (VERIFIED datasheets; ankle = linkage capability, min over range; SERVO = ST3215 19.5 kg cm @ 7.4 V)
EFFORT = {"XL": 120.0, "L": 60.0, "M": 36.0, "ANKLE_P": 46.0, "ANKLE_R": 51.0, "S": 17.0, "XS": 14.0, "SERVO": 1.9}
VELOCITY = {"XL": 20.9, "L": 20.9, "M": 50.3, "ANKLE_P": 30.0, "ANKLE_R": 30.0, "S": 44.0, "XS": 33.0, "SERVO": 4.7}
ARMATURE = {"XL": 0.040, "L": 0.020, "M": 0.010, "ANKLE_P": 0.020, "ANKLE_R": 0.016, "S": 0.0035, "XS": 0.002, "SERVO": 0.001}   # ESTIMATED


def jclass(joint_name):
    base = joint_name.replace("_joint", "")
    for pre in ("left_", "right_"):
        if base.startswith(pre):
            base = base[len(pre):]
    return CLASS_OF[base]
# joint-space PD gains of the default position actuators (N m/rad, N m s/rad). Sizing rule: an ankle-held stance is an
# inverted pendulum that needs sum(kp_ankle) > m g h_com (27.5 kg x 9.81 x 0.59 m = 159 N m/rad); use >= 4x that margin.
# RobStride MIT-mode Kp range is 0-500 (RS00/RS02) / 0-5000 (RS03/RS04/RS06) — VERIFIED manuals — so these are realisable.
KP = {"XL": 400.0, "L": 300.0, "M": 150.0, "ANKLE_P": 350.0, "ANKLE_R": 200.0, "S": 60.0, "XS": 40.0, "SERVO": 8.0}
KD = {"XL": 8.0, "L": 6.0, "M": 3.0, "ANKLE_P": 6.0, "ANKLE_R": 4.0, "S": 1.5, "XS": 1.0, "SERVO": 0.2}


def write_urdf(links, placeholder):
    J = joint_by_name()
    out = ['<?xml version="1.0"?>', '<!-- JX1 humanoid. Generated by tools/sim/build_robot_description.py from the SolidWorks CAD. -->',
           '<robot name="jx1">']

    def link(name, L):
        c = L["com"]
        s_ = [f'  <link name="{name}">', '    <inertial>', f'      <origin xyz="{c[0]:.6f} {c[1]:.6f} {c[2]:.6f}" rpy="0 0 0"/>',
              f'      <mass value="{L["mass"]:.5f}"/>', f'      <inertia {inertia_xml(L["inertia"])}/>', '    </inertial>',
              '    <visual>', f'      <geometry><mesh filename="package://jx1_description/meshes/{L["visual"]}"/></geometry>', '    </visual>']
        for h in L["collision"]:
            s_ += ['    <collision>', f'      <geometry><mesh filename="package://jx1_description/meshes/{h}"/></geometry>', '    </collision>']
        s_.append('  </link>')
        return s_

    for name, L in links.items():
        out += link(name, L)
    if placeholder:
        tp = TORSO_PLACEHOLDER
        I = np.diag([tp["mass"] / 12 * (tp["box"][1] ** 2 + tp["box"][2] ** 2), tp["mass"] / 12 * (tp["box"][0] ** 2 + tp["box"][2] ** 2),
                     tp["mass"] / 12 * (tp["box"][0] ** 2 + tp["box"][1] ** 2)])
        out += ['  <link name="torso_link">', '    <inertial>', f'      <origin xyz="{tp["com"][0]} {tp["com"][1]} {tp["com"][2]}" rpy="0 0 0"/>',
                f'      <mass value="{tp["mass"]}"/>', f'      <inertia {inertia_xml(I)}/>', '    </inertial>', '    <visual>',
                f'      <origin xyz="{tp["com"][0]} {tp["com"][1]} {tp["com"][2]}"/>', f'      <geometry><box size="{tp["box"][0]} {tp["box"][1]} {tp["box"][2]}"/></geometry>',
                '    </visual>', '  </link>']
    present = set(links) | ({"torso_link"} if placeholder else set())
    for j in JM["joints"]:
        if j["parent"] not in present or j["child"] not in present:
            continue
        cls = jclass(j["name"])
        o = j["origin_xyz_m"]
        out += [f'  <joint name="{j["name"]}" type="revolute">', f'    <parent link="{j["parent"]}"/>', f'    <child link="{j["child"]}"/>',
                f'    <origin xyz="{o[0]} {o[1]} {o[2]}" rpy="0 0 0"/>', f'    <axis xyz="{j["axis"][0]} {j["axis"][1]} {j["axis"][2]}"/>',
                f'    <limit lower="{j["lower_rad"]}" upper="{j["upper_rad"]}" effort="{EFFORT[cls]}" velocity="{VELOCITY[cls]}"/>',
                '    <dynamics damping="0.05" friction="0.3"/>', '  </joint>']
    for f in JM["fixed_frames"]:
        if f["parent"] not in present:
            continue
        o = f["origin_xyz_m"]
        out += [f'  <link name="{f["child"]}"/>', f'  <joint name="{f["name"]}" type="fixed">', f'    <parent link="{f["parent"]}"/>',
                f'    <child link="{f["child"]}"/>', f'    <origin xyz="{o[0]} {o[1]} {o[2]}" rpy="0 0 0"/>', '  </joint>']
    out.append('</robot>')
    (PKG_DIR / "urdf").mkdir(parents=True, exist_ok=True)
    (PKG_DIR / "urdf" / "jx1.urdf").write_text("\n".join(out), encoding="utf-8")


def write_mjcf(links, placeholder):
    ms = ['<mujoco model="jx1">', '  <!-- Generated by tools/sim/build_robot_description.py from the SolidWorks CAD. -->',
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
    colors = {"pelvis": ".80 .81 .83 1", "hip_yaw": ".80 .81 .83 1", "hip_roll": ".80 .81 .83 1", "thigh": ".80 .81 .83 1",
              "shin": ".80 .81 .83 1", "ankle_cross": ".6 .61 .63 1", "foot": ".95 .42 .10 1", "torso": ".75 .76 .78 1",
              "shoulder": ".80 .81 .83 1", "arm": ".80 .81 .83 1", "forearm": ".80 .81 .83 1", "neck": ".16 .16 .17 1", "head": ".95 .42 .10 1"}
    children = {}
    for j in JM["joints"]:
        children.setdefault(j["parent"], []).append(j)
    fixed = {}
    for f in JM["fixed_frames"]:
        fixed.setdefault(f["parent"], []).append(f)
    present = set(links) | ({"torso_link"} if placeholder else set())

    def body_inertial(L):
        c, I = L["com"], L["inertia"]
        return (f'<inertial pos="{c[0]:.6f} {c[1]:.6f} {c[2]:.6f}" mass="{L["mass"]:.5f}" '
                f'fullinertia="{I[0, 0]:.6e} {I[1, 1]:.6e} {I[2, 2]:.6e} {I[0, 1]:.6e} {I[0, 2]:.6e} {I[1, 2]:.6e}"/>')

    def geoms(name):
        rgba = next((v for k, v in colors.items() if k in name), ".5 .5 .5 1")
        g = [f'<geom class="visual" mesh="{name}_vis" rgba="{rgba}"/>']
        if name.endswith("foot_link"):
            d = DP["geometry"]
            L_, W_, h_ = d["foot"]["length_m"]["value"], d["foot"]["width_m"]["value"], d["sole_to_ankle_m"]["value"]
            heel = d["foot"]["ankle_from_heel_m"]["value"]
            g.append(f'<geom name="{name}_sole" type="box" size="{L_ / 2:.4f} {W_ / 2:.4f} 0.005" pos="{L_ / 2 - heel:.4f} 0 {-h_ + 0.005:.4f}" rgba=".1 .1 .1 1"/>')
        else:
            for k in range(len(links[name]["collision"])):
                g.append(f'<geom class="collision" mesh="{name}_col{k}"/>')
        return g

    def emit(name, ind):
        out = []
        if name in links:
            out.append(ind + body_inertial(links[name]))
            out += [ind + g for g in geoms(name)]
        elif name == "torso_link" and placeholder:
            tp = TORSO_PLACEHOLDER
            out.append(ind + f'<inertial pos="{tp["com"][0]} {tp["com"][1]} {tp["com"][2]}" mass="{tp["mass"]}" diaginertia="0.24 0.19 0.11"/>')
            out.append(ind + f'<geom type="box" size="{tp["box"][0] / 2} {tp["box"][1] / 2} {tp["box"][2] / 2}" '
                             f'pos="{tp["com"][0]} {tp["com"][1]} {tp["com"][2]}" rgba=".92 .92 .94 1" contype="0" conaffinity="0"/>')
        for f in fixed.get(name, []):
            o = f["origin_xyz_m"]
            out.append(ind + f'<site name="{f["child"].replace("_link", "")}" pos="{o[0]} {o[1]} {o[2]}" size="0.01"/>')
        for j in children.get(name, []):
            if j["child"] not in present:
                continue
            o = j["origin_xyz_m"]
            cls = jclass(j["name"])
            out.append(ind + f'<body name="{j["child"]}" pos="{o[0]} {o[1]} {o[2]}">')
            out.append(ind + f'  <joint name="{j["name"]}" axis="{j["axis"][0]} {j["axis"][1]} {j["axis"][2]}" '
                             f'range="{j["lower_rad"]} {j["upper_rad"]}" armature="{ARMATURE[cls]}"/>')
            out += emit(j["child"], ind + "  ")
            out.append(ind + "</body>")
        return out

    ms.append('    <body name="pelvis" pos="0 0 0.64">')
    ms.append('      <freejoint name="root"/>')
    ms += emit("pelvis", "      ")
    ms += ['    </body>', '  </worldbody>', '  <contact>']
    # explicit exclusions for jointed neighbours (MuJoCo's parent filter does not apply when the parent is welded to the
    # world in fixed-base variants); the push-rods are rigid shin geometry here, so shin-foot is excluded as well
    for j in JM["joints"]:
        if j["parent"] in present and j["child"] in present:
            ms.append(f'    <exclude body1="{j["parent"]}" body2="{j["child"]}"/>')
    # nested links around one joint centre (hip: yaw/roll/pitch intersect; shoulder: pitch/roll/yaw) overlap as convex hulls
    # although the real parts clear each other (verified by SolidWorks interference detection over the full ranges), so
    # grandparent pairs inside those clusters are excluded too; legs vs legs, arms vs legs/torso stay enabled
    extra = [("{s}_shin_link", "{s}_foot_link"), ("pelvis", "{s}_hip_roll_link"), ("pelvis", "{s}_thigh_link"),
             ("{s}_hip_yaw_link", "{s}_thigh_link"), ("{s}_thigh_link", "{s}_ankle_cross_link"),
             ("torso_link", "{s}_shoulder_roll_link"), ("{s}_shoulder_pitch_link", "{s}_upper_arm_link")]
    for side in ("left", "right"):
        for a_, b_ in extra:
            a_, b_ = a_.format(s=side), b_.format(s=side)
            if a_ in present and b_ in present:
                ms.append(f'    <exclude body1="{a_}" body2="{b_}"/>')
    if "torso_link" in present and "head_link" in present:
        ms.append('    <exclude body1="torso_link" body2="head_link"/>')
    ms += ['  </contact>', '  <actuator>']
    for j in JM["joints"]:
        if j["child"] not in present:
            continue
        cls = jclass(j["name"])
        ms.append(f'    <position name="{j["name"].replace("_joint", "")}" joint="{j["name"]}" kp="{KP[cls]}" kv="{KD[cls]}" '
                  f'forcerange="{-EFFORT[cls]} {EFFORT[cls]}"/>')
    ms += ['  </actuator>', '  <sensor>', '    <framequat name="imu_quat" objtype="site" objname="imu"/>', '    <gyro name="imu_gyro" site="imu"/>',
           '    <accelerometer name="imu_acc" site="imu"/>', '    <touch name="left_foot_touch" site="left_sole"/>',
           '    <touch name="right_foot_touch" site="right_sole"/>', '  </sensor>', '</mujoco>']
    MJ_DIR.mkdir(parents=True, exist_ok=True)
    (MJ_DIR / "jx1.xml").write_text("\n".join(ms), encoding="utf-8")


def write_isaac_config(links, placeholder):
    """Isaac Sim import settings with the same per-joint drive gains / effort limits as the MJCF (UNVERIFIED: no Isaac Sim here)."""
    present = set(links) | ({"torso_link"} if placeholder else set())
    gains = {}
    for j in JM["joints"]:
        if j["child"] in present:
            cls = jclass(j["name"])
            gains[j["name"]] = {"kp_Nm_per_rad": KP[cls], "kd_Nms_per_rad": KD[cls], "max_effort_Nm": EFFORT[cls], "max_velocity_rad_s": VELOCITY[cls]}
    cfg = {"generated_by": "tools/sim/build_robot_description.py (UNVERIFIED — no Isaac Sim on the design machine)",
           "urdf": "../../ros2_ws/src/jx1_description/urdf/jx1.urdf", "output_usd": "jx1.usd", "fix_base": False,
           "merge_fixed_joints": False, "convex_decomposition": False, "import_inertia_tensor": True, "self_collision": True,
           "note": "PhysX angular drives take stiffness/damping per degree: the importer multiplies by pi/180", "drive_gains": gains}
    (ROOT / "simulation" / "isaac" / "import_config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-coacd", action="store_true")
    ap.add_argument("--placeholder-torso", action="store_true", help="ignore the phase-2 upper-body CAD")
    a = ap.parse_args()
    upper = (not a.placeholder_torso) and upper_available()
    links, report = build_links(not a.no_coacd, upper=upper)
    placeholder = not upper
    write_urdf(links, placeholder)
    write_mjcf(links, placeholder)
    total = sum(L["mass"] for L in links.values()) + (TORSO_PLACEHOLDER["mass"] if placeholder else 0.0)
    summary = {"total_mass_kg": round(total, 3), "upper_body": "CAD" if upper else TORSO_PLACEHOLDER, "densities_kg_m3": DENSITY,
               "fixed_masses_kg": {k: v[0] for k, v in FIXED_MASS.items()},
               "output_mass_share": OUTPUT_MASS_SHARE, "fastener_allowance": FASTENER_ALLOWANCE,
               "links": {n: {"mass_kg": round(L["mass"], 4), "com_m": [round(float(x), 5) for x in L["com"]],
                             "inertia_diag_kgm2": [float(f"{x:.4e}") for x in np.diag(L["inertia"])], "collision_hulls": len(L["collision"])}
                         for n, L in links.items()},
               "components": report}
    (ROOT / "simulation" / "mass_properties.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_isaac_config(links, placeholder)
    src = "CAD upper body" if upper else f"incl. {TORSO_PLACEHOLDER['mass']} kg torso placeholder"
    print(f"TOTAL modelled mass {total:.2f} kg ({src})")


if __name__ == "__main__":
    main()
