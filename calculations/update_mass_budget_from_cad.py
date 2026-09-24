"""Iteration 2 input: replace the ASSUMED structure masses of calculations/design_point.yaml with CAD-derived values.

Reads simulation/mass_properties.json (tools/sim/build_robot_description.py: every CAD component with its mass, grouped
per URDF link) and writes calculations/results/variant_C_cad_masses.yaml — a copy of the design point whose mass_budget
uses, per leg link, the non-actuator component masses and COM (actuators are added by the analysis from the catalogue),
and for the upper body the total CAD mass/COM/inertia at the zero pose (arms down).
Usage: .venv/Scripts/python calculations/update_mass_budget_from_cad.py
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
DP = yaml.safe_load((ROOT / "calculations" / "design_point.yaml").read_text(encoding="utf-8"))
MP = json.loads((ROOT / "simulation" / "mass_properties.json").read_text(encoding="utf-8"))

LEG = {"pelvis": "pelvis", "hip_yaw_link": "left_hip_yaw_link", "hip_roll_link": "left_hip_roll_link", "thigh": "left_thigh_link",
       "shin": "left_shin_link", "ankle_cross": "left_ankle_cross_link", "foot": "left_foot_link"}
UPPER_LINKS = ("torso_link", "neck_link", "head_link") + tuple(f"{s}_{l}_link" for s in ("left", "right")
                                                              for l in ("shoulder_pitch", "shoulder_roll", "upper_arm", "forearm"))


def main():
    comps = MP["components"]
    if isinstance(MP.get("upper_body"), dict):
        sys.exit("mass_properties.json was built with the torso placeholder — build the CAD upper body first")
    out = copy.deepcopy(DP)
    mb = out["mass_budget"]
    rows = {}
    for key, link in LEG.items():
        struct = [c for c in comps if c["link"] == link and not c["component"].startswith("JX1_ACT_")]
        m = sum(c["mass_kg"] for c in struct)
        m *= 1 + MP["fastener_allowance"]
        rows[key] = round(m, 3)
        mb[key]["structure_kg"] = {"value": round(m, 3), "label": "CALCULATED",
                                   "note": f"CAD components ({', '.join(sorted(set(c['component'] for c in struct)))}) + {MP['fastener_allowance']:.0%} fasteners"}
    # upper body: every component on the upper links (+ the waist housing, below); structure COMs keep the design-point values
    mass, mom = 0.0, np.zeros(3)
    # link COMs are in link frames; the zero-pose link origins come from the joint map (all joints zero, no rotation)
    jm = yaml.safe_load((ROOT / "simulation" / "joint_map.yaml").read_text(encoding="utf-8"))
    origin = {"pelvis": np.zeros(3)}
    for j in jm["joints"]:
        origin[j["child"]] = origin.get(j["parent"], np.zeros(3)) + np.array(j["origin_xyz_m"])
    for link in UPPER_LINKS:
        if link in MP["links"]:
            L = MP["links"][link]
            mass += L["mass_kg"]
            mom += L["mass_kg"] * (origin[link] + np.array(L["com_m"]))
    # the waist RS06 housing sits on the pelvis link in the URDF next to the two hip-yaw housings; the analysis model only
    # carries the hip-yaw actuators on the pelvis, so the waist housing joins the upper-body lump at its real height
    m_housings = [c for c in comps if c["link"] == "pelvis" and c["component"] == "JX1_ACT_M_Housing"]
    if len(m_housings) == 3:
        wh = m_housings[0]["mass_kg"]
        wz = float(yaml.safe_load((ROOT / "calculations" / "design_point.yaml").read_text(encoding="utf-8"))
                   ["upper_body_geometry"]["waist_yaw_origin"]["value"][2]) - 0.005 - 0.022      # housing centre below the output face
        mass += wh
        mom += wh * np.array([0.0, 0.0, wz])
    com = mom / mass
    mb["upper_body"]["mass_kg"] = {"value": round(mass, 3), "label": "CALCULATED",
                                   "note": "phase-2 CAD: torso frame, battery, Jetson, electronics, waist output, arms, grippers, neck, head (zero pose)"}
    mb["upper_body"]["com_m"] = [round(float(x), 4) for x in com]
    out["meta"]["version"] = str(out["meta"]["version"]) + "-C"
    out["meta"]["note"] = "variant C: CAD-derived structure masses after the FEA-driven aluminium redesign (iteration 2)"
    path = ROOT / "calculations" / "results" / "variant_C_cad_masses.yaml"
    path.write_text(yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=140), encoding="utf-8")
    print("structure masses (kg):", rows)
    print(f"upper body {mass:.2f} kg, COM {np.round(com, 3)} (pelvis frame)")
    print("wrote", path)


if __name__ == "__main__":
    main()
