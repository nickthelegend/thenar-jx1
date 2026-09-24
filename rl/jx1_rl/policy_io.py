"""Policy input/output conventions shared by training, export, sim-to-sim and the ROS 2 node.

Everything is plain numpy with leading batch dimensions, so the batched training environment and the single-robot
deployment path build observations and joint targets with the same code. The ROS 2 package (ros2_ws/src/jx1_policy)
carries an equivalent implementation driven by the exported policy_io.yaml; rl/tests/test_policy_io.py checks they agree.
"""
from __future__ import annotations

import numpy as np


def quat_rotate_inverse(q_wxyz: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Rotate world-frame vectors v into the body frame of unit quaternions q (w, x, y, z). Shapes (..., 4), (..., 3)."""
    w = q_wxyz[..., :1]
    u = q_wxyz[..., 1:4]
    a = v * (2.0 * w * w - 1.0)
    b = np.cross(u, v) * w * 2.0          # sign: inverse rotation
    c = u * np.sum(u * v, axis=-1, keepdims=True) * 2.0
    return a - b + c


def projected_gravity(q_wxyz: np.ndarray) -> np.ndarray:
    g = np.zeros(q_wxyz.shape[:-1] + (3,))
    g[..., 2] = -1.0
    return quat_rotate_inverse(q_wxyz, g)


def gait_phase(t: np.ndarray, period: float) -> np.ndarray:
    return np.mod(t / period, 1.0)


def gait_moving(command, threshold):
    """1 while walking, 0 in stand mode: |(vx, vy, wz)| below gait.stand_command_threshold (OI-27; None = always 1)."""
    command = np.asarray(command, dtype=np.float64)
    if threshold is None:
        return np.ones(command.shape[:-1])
    return (np.linalg.norm(command, axis=-1) >= threshold).astype(np.float64)


def build_observation(ang_vel_b, gravity_b, command, dof_pos_rel, dof_vel, last_action, phase, scales, clip=100.0, moving=None):
    """Actor observation. ang_vel_b: body angular velocity (rad/s); gravity_b: unit gravity in the body frame;
    command: (vx, vy, wz); dof_pos_rel: q - q_default (policy joints); dof_vel: dq; last_action: previous raw action;
    phase: gait phase in [0, 1). scales: dict from the task config (observation.scales). moving: gait_moving(); the
    clock features are 0 in stand mode."""
    cmd_scale = np.asarray(scales["commands"], dtype=np.float64)
    m = 1.0 if moving is None else np.asarray(moving, dtype=np.float64)[..., None]
    obs = np.concatenate([
        ang_vel_b * scales["ang_vel"],
        gravity_b,
        command * cmd_scale,
        dof_pos_rel * scales["dof_pos"],
        dof_vel * scales["dof_vel"],
        last_action,
        np.sin(2 * np.pi * phase)[..., None] * m,
        np.cos(2 * np.pi * phase)[..., None] * m,
    ], axis=-1)
    return np.clip(obs, -clip, clip)


def actions_to_targets(action, default_pos, action_scale, lower, upper):
    """Joint position targets for the policy joints: default + scale * action, clipped to the joint limits."""
    return np.clip(default_pos + action_scale * action, lower, upper)


def _project_to_convex_polygon(p: np.ndarray, poly: np.ndarray) -> np.ndarray:
    """Project points p (..., 2) onto a convex polygon (k, 2) given counter- or clockwise; points inside are unchanged."""
    k = len(poly)
    a = poly
    b = np.roll(poly, -1, axis=0)
    e = b - a                                                  # (k, 2)
    # orientation of the polygon (sign of area) so "inside" is on the same side of every edge
    area = 0.5 * np.sum(a[:, 0] * b[:, 1] - b[:, 0] * a[:, 1])
    s = np.sign(area) if area != 0 else 1.0
    d = p[..., None, :] - a                                    # (..., k, 2)
    cross = e[:, 0] * d[..., 1] - e[:, 1] * d[..., 0]          # (..., k)
    inside = np.all(s * cross >= -1e-12, axis=-1)
    t = np.clip(np.sum(d * e, axis=-1) / np.sum(e * e, axis=-1), 0.0, 1.0)
    closest = a + t[..., None] * e                             # (..., k, 2)
    dist = np.sum((closest - p[..., None, :]) ** 2, axis=-1)
    best = np.take_along_axis(closest, np.argmin(dist, axis=-1)[..., None, None].repeat(2, axis=-1), axis=-2)[..., 0, :]
    return np.where(inside[..., None], p, best)


def clip_ankle_targets(targets: np.ndarray, joints: list, polygons: dict) -> np.ndarray:
    """Project each ankle's (pitch, roll) target into its collision-free coupled polygon (joint_map coupled_limits)."""
    out = targets.copy()
    for side, poly in polygons.items():
        try:
            ip = joints.index(f"{side}_ankle_pitch_joint")
            ir = joints.index(f"{side}_ankle_roll_joint")
        except ValueError:
            continue
        pr = np.stack([out[..., ip], out[..., ir]], axis=-1)
        pr = _project_to_convex_polygon(pr, poly)
        out[..., ip], out[..., ir] = pr[..., 0], pr[..., 1]
    return out


def clip_hip_yaw_toe_out(targets: np.ndarray, joints: list, max_sum: float | None) -> np.ndarray:
    """Hip-yaw toe-out coupling (joint_map coupled_limits.hip_yaw_toe_out, OI-24): the bracket tails touch when both
    hips toe out, so left_hip_yaw - right_hip_yaw <= max_sum; any excess is taken off both hips equally."""
    if max_sum is None or "left_hip_yaw_joint" not in joints or "right_hip_yaw_joint" not in joints:
        return targets
    il, ir = joints.index("left_hip_yaw_joint"), joints.index("right_hip_yaw_joint")
    out = np.array(targets, dtype=np.float64, copy=True)
    excess = np.maximum(out[..., il] - out[..., ir] - max_sum, 0.0)
    out[..., il] -= 0.5 * excess
    out[..., ir] += 0.5 * excess
    return out


def ankle_polygon_violation(q: np.ndarray, joints: list, polygons: dict) -> np.ndarray:
    """Distance (rad) of each ankle's (pitch, roll) outside its polygon, summed over ankles. q (..., n)."""
    total = np.zeros(q.shape[:-1])
    for side, poly in polygons.items():
        if f"{side}_ankle_pitch_joint" not in joints:
            continue
        ip, ir = joints.index(f"{side}_ankle_pitch_joint"), joints.index(f"{side}_ankle_roll_joint")
        pr = np.stack([q[..., ip], q[..., ir]], axis=-1)
        total += np.linalg.norm(pr - _project_to_convex_polygon(pr, poly), axis=-1)
    return total
