"""Verify the closed-form leg IK against MuJoCo forward kinematics and the ankle linkage model.

Run:  .venv/Scripts/python -m pytest calculations/tests -q   (or python calculations/tests/test_kinematics.py)
"""
import sys
from pathlib import Path

import mujoco
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from jx1calc.design import Design, LEG_JOINTS  # noqa: E402
from jx1calc.mjcf import build_mjcf  # noqa: E402
from jx1calc.kinematics import leg_fk, leg_ik, rpy_to_matrix, rz  # noqa: E402
from jx1calc.gait import WholeBody  # noqa: E402
from jx1calc.ankle import ParallelAnkle  # noqa: E402


def test_ik_roundtrip_random():
    d = Design()
    rng = np.random.default_rng(1)
    worst = 0.0
    for _ in range(2000):
        q = np.array([rng.uniform(-0.6, 0.6), rng.uniform(-0.4, 0.6), rng.uniform(-1.5, 0.4),
                      rng.uniform(0.05, 2.2), rng.uniform(-0.7, 0.5), rng.uniform(-0.3, 0.3)])
        p, R = leg_fk(q, d.thigh, d.shin)
        q2 = leg_ik(np.zeros(3), np.eye(3), p, R, d.thigh, d.shin)
        p2, R2 = leg_fk(q2, d.thigh, d.shin)
        worst = max(worst, np.abs(p2 - p).max(), np.abs(R2 - R).max())
    assert worst < 1e-9, worst


def test_ik_matches_mujoco():
    d = Design()
    m = mujoco.MjModel.from_xml_string(build_mjcf(d, with_actuators=False))
    wb = WholeBody(m, d)
    data = mujoco.MjData(m)
    rng = np.random.default_rng(2)
    worst = 0.0
    for _ in range(300):
        yaw = rng.uniform(-0.5, 0.5)
        pel = np.array([rng.uniform(-0.05, 0.05), rng.uniform(-0.05, 0.05), rng.uniform(0.40, 0.56)])
        feet = {"l": np.array([rng.uniform(-0.12, 0.12), 0.09 + rng.uniform(-0.02, 0.04), d.sole_to_ankle + rng.uniform(0, 0.06)]),
                "r": np.array([rng.uniform(-0.12, 0.12), -0.09 - rng.uniform(-0.02, 0.04), d.sole_to_ankle + rng.uniform(0, 0.06)])}
        fy = {"l": yaw + rng.uniform(-0.2, 0.2), "r": yaw + rng.uniform(-0.2, 0.2)}
        q = wb.ik(pel, yaw, feet, fy)
        data.qpos[:] = wb.set_state(pel, yaw, q)
        mujoco.mj_kinematics(m, data)
        for s in "lr":
            bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, f"{s}_foot")
            worst = max(worst, np.abs(data.xpos[bid] - feet[s]).max(),
                        np.abs(data.xmat[bid].reshape(3, 3) - rz(fy[s])).max())
    assert worst < 1e-9, worst


def test_parallel_ankle_linear_region():
    d = Design()
    a = ParallelAnkle(d.crank_r, d.foot_lever, d.rod_half_spacing, d.ankle_motor_height)
    assert np.allclose(a.crank_angles(0, 0), 0, atol=1e-12)
    J = a.jacobian(0, 0)
    # small-angle theory for r == a: J ~ [[1, w/a], [1, -w/a]]
    ratio = d.rod_half_spacing / d.foot_lever
    assert np.allclose(J, [[1, ratio], [1, -ratio]], atol=0.03), J
    # full range reachable
    for p in np.radians(np.linspace(-45, 30, 16)):
        for r in np.radians(np.linspace(-20, 20, 9)):
            a.crank_angles(p, r)


if __name__ == "__main__":
    test_ik_roundtrip_random()
    test_ik_matches_mujoco()
    test_parallel_ankle_linear_region()
    print("all kinematics tests passed")
