"""Regenerate the robot software's centre-of-mass table (jx0/software/jx0bot/kinematics.py: UPPER_MASS, UPPER_COM, LINKS)
from the MuJoCo model, so the robot's COM estimate uses the same masses as the simulation.

    python jx0/sim/com_table.py          (rewrites the table in kinematics.py; tests/test_jx0bot.py checks it)
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "jx0" / "sim"))
os.environ.setdefault("JX0_STL_DIR", str(ROOT / "nonexistent"))


def table():
    import mujoco
    import numpy as np
    import walk_jx0 as W
    from jx1calc.design import Design
    m = mujoco.MjModel.from_xml_string(W.build(Design(W.DESIGN)))
    d = mujoco.MjData(m)
    d.qpos[:3] = [0, 0, 0.3]
    d.qpos[3] = 1
    for n, v in W.ARM_POSE.items():
        d.qpos[m.jnt_qposadr[mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, n)]] = v
    mujoco.mj_forward(m, d)
    mass, s = 0.0, np.zeros(3)
    for n in ("pelvis", "torso", "l_upper_arm", "l_forearm", "r_upper_arm", "r_forearm", "head"):
        b = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, n)
        mass += m.body_mass[b]
        s += m.body_mass[b] * (d.xipos[b] - d.xpos[1])
    links = {}
    for ln in ("hip_yaw_link", "hip_roll_link", "thigh", "shin", "ankle_cross", "foot"):
        b = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, f"l_{ln}")
        links[ln] = (float(m.body_mass[b]), tuple(float(v) for v in m.body_ipos[b]))
    return mass, s / mass, links


def main():
    mass, com, links = table()
    text = (f"UPPER_MASS, UPPER_COM = {mass:.4f}, np.array([{com[0]:.4f}, 0.0, {com[2]:.4f}])   "
            "# pelvis + torso + head + arms (arms at rest)\nLINKS = {\n"
            + "".join(f'    "{k}": ({m_:.4f}, ({c[0]:.4f}, {c[1]:.4f}, {c[2]:.4f})),\n' for k, (m_, c) in links.items()) + "}\n")
    p = ROOT / "jx0" / "software" / "jx0bot" / "kinematics.py"
    s = p.read_text(encoding="utf-8")
    s2 = re.sub(r"UPPER_MASS, UPPER_COM = .*?\nLINKS = \{\n.*?\}\n", text, s, flags=re.S)
    assert s2 != s or text in s
    p.write_text(s2, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
