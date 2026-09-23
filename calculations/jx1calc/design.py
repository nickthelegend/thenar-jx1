"""Design-point loading and derived mass properties for the parametric analysis model."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DESIGN = ROOT / "calculations" / "design_point.yaml"

LEG_JOINTS = ["hip_yaw", "hip_roll", "hip_pitch", "knee", "ankle_pitch", "ankle_roll"]
LEG_LINKS = ["hip_yaw_link", "hip_roll_link", "thigh", "shin", "ankle_cross", "foot"]


def _v(node):
    """Return the numeric value of a labelled YAML entry ({value:, label:}) or a raw number."""
    if isinstance(node, dict) and "value" in node:
        return node["value"]
    return node


@dataclass
class LinkMass:
    name: str
    mass: float
    com: np.ndarray
    inertia: np.ndarray  # principal moments about COM, aligned with link frame
    parts: list = field(default_factory=list)


def cylinder_inertia(m, r, h, axis):
    """Solid cylinder principal inertia about its centre; axis in {'x','y','z'}."""
    ia = 0.5 * m * r * r
    it = m * (3 * r * r + h * h) / 12.0
    return {"x": np.array([ia, it, it]), "y": np.array([it, ia, it]), "z": np.array([it, it, ia])}[axis]


def box_inertia(m, sx, sy, sz):
    return m / 12.0 * np.array([sy * sy + sz * sz, sx * sx + sz * sz, sx * sx + sy * sy])


def combine(parts):
    """Combine point-like parts [(mass, com(3), inertia_diag(3))] into one rigid body (diag approx)."""
    m = sum(p[0] for p in parts)
    c = sum(p[0] * np.asarray(p[1], float) for p in parts) / m
    inertia = np.zeros((3, 3))
    for pm, pc, pi in parts:
        d = np.asarray(pc, float) - c
        inertia += np.diag(pi) + pm * (np.dot(d, d) * np.eye(3) - np.outer(d, d))
    # keep the full tensor diagonal (off-diagonals are small for these symmetric layouts)
    return m, c, np.diag(inertia).copy(), inertia


class Design:
    def __init__(self, path: Path | str = DEFAULT_DESIGN, overrides: dict | None = None):
        self.path = Path(path)
        self.raw = yaml.safe_load(self.path.read_text(encoding="utf-8"))
        if overrides:
            _deep_update(self.raw, overrides)
        g = self.raw["geometry"]
        self.height = _v(self.raw["overall"]["height_m"])
        self.sole_to_ankle = _v(g["sole_to_ankle_m"])
        self.shin = _v(g["shin_m"])
        self.thigh = _v(g["thigh_m"])
        self.hip_spacing = _v(g["hip_spacing_m"])
        f = g["foot"]
        self.foot_length = _v(f["length_m"])
        self.foot_width = _v(f["width_m"])
        self.ankle_from_heel = _v(f["ankle_from_heel_m"])
        self.foot_thickness = _v(f["thickness_m"])
        self.ranges_deg = {k: (v["min"], v["max"]) for k, v in self.raw["joint_ranges_deg"].items()}
        self.act_classes = self.raw["actuator_classes"]
        self.assign = self.raw["leg_actuator_assignment"]
        al = self.raw["ankle_linkage"]
        self.crank_r = _v(al["crank_radius_m"])
        self.foot_lever = _v(al["foot_lever_m"])
        self.rod_half_spacing = _v(al["rod_half_spacing_m"])
        self.ankle_motor_height = _v(al["motor_height_above_ankle_m"])
        self.links = self._build_links()

    # ------------------------------------------------------------------ geometry helpers
    @property
    def foot_center_x(self):
        """x of the foot's geometric centre relative to the ankle axis."""
        return self.foot_length / 2 - self.ankle_from_heel

    @property
    def leg_length(self):
        return self.thigh + self.shin + self.sole_to_ankle

    def actuator(self, joint_key):
        cls = self.assign[joint_key]
        a = self.act_classes[cls]
        return cls, a["mass_kg"], a["diameter_m"], a["length_m"]

    # ------------------------------------------------------------------ mass model
    def _actuator_part(self, joint_key, center, axis):
        _, m, d, l = self.actuator(joint_key)
        return (m, center, cylinder_inertia(m, d / 2, l, axis))

    def _build_links(self):
        mb = self.raw["mass_budget"]
        links = {}
        hs = self.hip_spacing / 2
        # Pelvis: structure + both hip-yaw actuators (vertical axis, above each hip centre)
        p = mb["pelvis"]
        parts = [(_v(p["structure_kg"]), p["com_m"], box_inertia(_v(p["structure_kg"]), 0.12, 0.26, 0.10))]
        for s in (+1, -1):
            parts.append(self._actuator_part("hip_yaw", [0.0, s * hs, 0.075], "z"))
        m, c, i, _ = combine(parts)
        links["pelvis"] = LinkMass("pelvis", m, c, i, parts)
        ub = mb["upper_body"]
        um = _v(ub["mass_kg"])
        links["upper_body"] = LinkMass("upper_body", um, np.array(ub["com_m"], float), box_inertia(um, *ub["inertia_box_m"]))
        # Leg links (left leg frame; right mirrors y)
        spec = {
            "hip_yaw_link": [("hip_roll", [-0.055, 0.0, 0.0], "x")],       # roll actuator behind hip centre, axis x
            "hip_roll_link": [("hip_pitch", [0.0, 0.055, 0.0], "y")],      # pitch actuator lateral of hip centre, axis y
            "thigh": [("knee", [0.0, 0.0, -self.thigh], "y")],             # knee actuator coaxial with knee
            "shin": [("ankle_A", [-0.02, 0.035, -self.shin + self.ankle_motor_height], "y"),
                      ("ankle_B", [-0.02, -0.035, -self.shin + self.ankle_motor_height], "y")],
            "ankle_cross": [],
            "foot": [],
        }
        struct_box = {
            "hip_yaw_link": (0.10, 0.08, 0.06),
            "hip_roll_link": (0.08, 0.10, 0.08),
            "thigh": (0.07, 0.07, self.thigh),
            "shin": (0.06, 0.06, self.shin),
            "ankle_cross": (0.03, 0.03, 0.03),
            "foot": (self.foot_length, self.foot_width, 0.03),
        }
        for name in LEG_LINKS:
            b = mb[name]
            sm = _v(b["structure_kg"])
            parts = [(sm, b["com_m"], box_inertia(sm, *struct_box[name]))]
            for jk, cen, ax in spec[name]:
                parts.append(self._actuator_part(jk, cen, ax))
            m, c, i, _ = combine(parts)
            links[name] = LinkMass(name, m, c, i, parts)
        return links

    @property
    def total_mass(self):
        legs = sum(self.links[n].mass for n in LEG_LINKS) * 2
        return self.links["pelvis"].mass + self.links["upper_body"].mass + legs

    def mass_table(self):
        rows = []
        for n in ["pelvis", "upper_body"] + LEG_LINKS:
            L = self.links[n]
            k = 2 if n in LEG_LINKS else 1
            rows.append({"link": n, "count": k, "mass_each_kg": round(L.mass, 4), "mass_total_kg": round(L.mass * k, 4),
                         "com_m": [round(x, 4) for x in L.com], "inertia_diag_kgm2": [float(f"{x:.3e}") for x in L.inertia]})
        return rows


def _deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, dict) and isinstance(d.get(k), dict):
            _deep_update(d[k], v)
        else:
            d[k] = v
