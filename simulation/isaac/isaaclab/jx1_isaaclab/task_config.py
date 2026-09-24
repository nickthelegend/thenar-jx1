"""JX1 task facts for Isaac Lab, read from the same files as the MuJoCo training (no Isaac imports here).

rl/config/jx1_walk.yaml: policy joints, default pose, PD gains, action scale, observation scales, gait clock, commands,
rewards, randomisation.  simulation/joint_map.yaml: joint limits.  ros2_ws/src/jx1_description/urdf/jx1.urdf: effort
and velocity limits per joint (actuator classes), link names.
"""
from __future__ import annotations

import math
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[4]
URDF = REPO / "ros2_ws" / "src" / "jx1_description" / "urdf" / "jx1.urdf"
USD = REPO / "simulation" / "isaac" / "jx1.usd"
CACHE = Path(__file__).resolve().parents[1] / ".cache"


def _jtype(name: str) -> str:
    base = name[:-6] if name.endswith("_joint") else name
    for side in ("left_", "right_"):
        if base.startswith(side):
            return base[len(side):]
    return base


def base_height(cfg: dict, jm: dict) -> float:
    """Pelvis height with the soles flat on the floor at the default pose (planar leg FK from the joint map origins)."""
    import math
    org = {j["name"]: j["origin_xyz_m"] for j in jm["joints"]}
    thigh = -org["left_knee_joint"][2]
    shin = -org["left_ankle_pitch_joint"][2]
    sole = -next(f["origin_xyz_m"][2] for f in jm["fixed_frames"] if f["name"] == "left_sole_fixed")
    d = cfg["default_joint_pos"]
    hp, kn = d.get("left_hip_pitch_joint", 0.0), d.get("left_knee_joint", 0.0)
    return thigh * math.cos(hp) + shin * math.cos(hp + kn) + sole


def mjcf_armature() -> dict:
    """Rotor armature per joint from the CAD MJCF (not carried by the URDF)."""
    path = REPO / "simulation" / "mujoco" / "jx1.xml"
    if not path.exists():
        return {}
    return {j.get("name"): float(j.get("armature")) for j in ET.parse(path).getroot().iter("joint") if j.get("armature")}


def _load_task_yaml(path: Path) -> dict:
    """Task YAML with the `base:` inheritance of rl/jx1_rl/config.py (deep merge)."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if "base" in raw:
        base = _load_task_yaml(path.parent / raw.pop("base"))

        def merge(a, b):
            out = dict(a)
            for k, v in b.items():
                out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
            return out
        raw = merge(base, raw)
    return raw


def load(config_path: Path | None = None) -> dict:
    cfg = _load_task_yaml(Path(config_path or REPO / "rl" / "config" / "jx1_walk.yaml"))
    jm = yaml.safe_load((REPO / "simulation" / "joint_map.yaml").read_text(encoding="utf-8"))
    joints = [j["name"] for j in jm["joints"]]
    limits = {j["name"]: (j["lower_rad"], j["upper_rad"]) for j in jm["joints"]}
    classes = {j["name"]: str(j["actuator_class"]).split()[0] for j in jm["joints"]}
    effort, velocity, links = {}, {}, []
    if URDF.exists():
        root = ET.parse(URDF).getroot()
        links = [link.get("name") for link in root.findall("link")]
        for j in root.findall("joint"):
            lim = j.find("limit")
            if j.get("type") == "revolute" and lim is not None:
                effort[j.get("name")] = float(lim.get("effort"))
                velocity[j.get("name")] = float(lim.get("velocity"))
    return {
        "raw": cfg,
        "joints": joints,
        "present": [j for j in joints if not effort or j in effort],
        "policy_joints": list(cfg["policy_joints"]),
        "default_pos": {j: float(cfg["default_joint_pos"].get(j, 0.0)) for j in joints},
        "gains": {j: tuple(cfg["pd_gains"][_jtype(j)]) for j in joints},
        "limits": limits,
        "effort": effort,
        "velocity": velocity,
        "links": links,
        "classes": classes,
        "armature": mjcf_armature(),
        "base_height": base_height(cfg, jm),
        "sole_offset": [float(v) for v in next(f["origin_xyz_m"] for f in jm["fixed_frames"] if f["name"] == "left_sole_fixed")],
        "polygons_deg": {s: jm["coupled_limits"]["ankle_pitch_roll"][f"{s}_polygon_deg"] for s in ("left", "right")},
        "toe_out_max_rad": (math.radians(jm["coupled_limits"]["hip_yaw_toe_out"]["toe_out_sum_max_deg"])
                            if "hip_yaw_toe_out" in jm.get("coupled_limits", {}) else None),
    }


OBS_LAYOUT = ["base_ang_vel_body x3 (rad/s) * scales.ang_vel", "projected_gravity_body x3", "command (vx m/s, vy m/s, wz rad/s) * scales.commands",
              "joint_pos - default (policy joints) * scales.dof_pos", "joint_vel (policy joints) * scales.dof_vel",
              "last_action (raw policy output)", "sin(2 pi phase), 0 in stand mode", "cos(2 pi phase), 0 in stand mode"]


def policy_io(tc: dict, meta: dict) -> dict:
    """policy_io.yaml content (same schema as rl/export.py) for a policy trained in Isaac Lab."""
    import math
    raw = tc["raw"]
    present = tc["joints"]                                   # whole robot (joint_map), like rl/export.py
    class_effort = {"XL": 120.0, "L": 60.0, "M": 36.0, "S": 17.0, "XS": 14.0, "servo": 1.9}
    class_velocity = {"XL": 20.9, "L": 20.9, "M": 50.3, "S": 44.0, "XS": 33.0, "servo": 4.7}
    effort = {j: tc["effort"].get(j, 46.0 if "ankle_pitch" in j else 51.0 if "ankle_roll" in j else class_effort[tc["classes"][j]])
              for j in present}
    n = len(tc["policy_joints"])
    return {
        "format": "jx1-policy-io/1",
        "policy": {"onnx": "policy.onnx", "torchscript": None, "input": "obs", "output": "actions", "num_obs": 9 + 3 * n + 2, "num_actions": n},
        "control": {"policy_dt_s": raw["model"]["timestep"] * raw["model"]["decimation"], "trained_physics_dt_s": raw["model"]["timestep"],
                    "trained_decimation": raw["model"]["decimation"]},
        "joints": {"policy": tc["policy_joints"], "held": [j for j in present if j not in tc["policy_joints"]]},
        "default_joint_pos": {j: tc["default_pos"][j] for j in present},
        "action_scale": raw["action_scale"],
        "pd_gains": {j: list(tc["gains"][j]) for j in present},
        "effort_limits_Nm": effort,
        "velocity_limits_rad_s": {j: 30.0 if "ankle" in j else tc["velocity"].get(j, class_velocity[tc["classes"][j]]) for j in present},
        "joint_limits_rad": {j: list(tc["limits"][j]) for j in present},
        "ankle_polygons_rad": {s: [[round(math.radians(a), 6), round(math.radians(b), 6)] for a, b in p] for s, p in tc["polygons_deg"].items()},
        **({"hip_yaw_toe_out_max_rad": round(tc["toe_out_max_rad"], 6)} if tc.get("toe_out_max_rad") is not None else {}),
        "observation": {"size": 9 + 3 * n + 2, "layout": OBS_LAYOUT, "scales": raw["observation"]["scales"], "clip": raw["observation"]["clip"]},
        "gait": raw["gait"],
        "commands": raw["commands"]["ranges"],
        "targets": "q_target = clip(default + action_scale * action, joint limits); ankle (pitch, roll) targets projected into ankle_polygons_rad; "
                   "left_hip_yaw - right_hip_yaw <= hip_yaw_toe_out_max_rad (excess taken off both hips equally)",
        "trained": meta,
    }


def urdf_with_absolute_meshes() -> Path:
    """Copy of jx1.urdf with package://jx1_description/ mesh URIs replaced by absolute paths (Isaac's URDF importer)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    pkg = (REPO / "ros2_ws" / "src" / "jx1_description").as_posix()
    out = CACHE / "jx1_abs.urdf"
    out.write_text(URDF.read_text(encoding="utf-8").replace("package://jx1_description", pkg), encoding="utf-8")
    return out
