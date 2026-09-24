"""Left/right mirror symmetry of JX1 (reflection through the sagittal x-z plane), for the PPO mirror loss.

Every joint has the same axis on both sides (joint_map / MJCF), so the mirror of a joint angle is the angle of its
counterpart, sign-flipped for roll and yaw joints (x and z axes) and kept for pitch joints (knee and elbow included).
Base quantities: positions and linear velocities flip y; angular velocities flip x and z; gravity in the body frame
flips y; the command (vx, vy, wz) -> (vx, -vy, -wz). The gait clock swaps legs: right = left + 0.5 period, so sin and
cos of the phase change sign. rl/tests checks all of this against MuJoCo physics (mirrored states stay mirrored).
"""
from __future__ import annotations

import numpy as np

FLIP_TYPES = ("roll", "yaw")


def joint_mirror(joints: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """Index and sign such that mirrored[i] = sign[i] * q[idx[i]] for a vector ordered like `joints`."""
    def other(j):
        return j.replace("left_", "\0").replace("right_", "left_").replace("\0", "right_")
    idx = np.array([joints.index(other(j)) for j in joints])
    sign = np.array([-1.0 if any(t in j for t in FLIP_TYPES) else 1.0 for j in joints])
    return idx, sign


class Mirror:
    """Mirror maps for the 47-D actor observation, the privileged observation and the actions (torch or numpy)."""

    def __init__(self, policy_joints: list[str], n_priv: int | None = None):
        n = len(policy_joints)
        jidx, jsign = joint_mirror(policy_joints)
        o_idx, o_sign = [0, 1, 2], [-1.0, 1.0, -1.0]                         # angular velocity (roll, pitch, yaw rates)
        o_idx += [3, 4, 5]
        o_sign += [1.0, -1.0, 1.0]                                          # projected gravity
        o_idx += [6, 7, 8]
        o_sign += [1.0, -1.0, -1.0]                                         # command vx, vy, wz
        for base in (9, 9 + n, 9 + 2 * n):                                  # q - q0, dq, last action
            o_idx += list(base + jidx)
            o_sign += list(jsign)
        o_idx += [9 + 3 * n, 10 + 3 * n]
        o_sign += [-1.0, -1.0]                                              # sin, cos of the phase (+0.5 period)
        self.n_obs = 11 + 3 * n
        self.o_idx, self.o_sign = np.array(o_idx), np.array(o_sign)
        self.a_idx, self.a_sign = jidx, jsign
        if n_priv is not None:
            # privileged = obs | lin vel (3) | base height (1) | foot contact (L, R) | foot heights (L, R)
            b = self.n_obs
            p_idx = list(self.o_idx) + [b, b + 1, b + 2, b + 3, b + 5, b + 4, b + 7, b + 6]
            p_sign = list(self.o_sign) + [1.0, -1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
            assert len(p_idx) == n_priv, (len(p_idx), n_priv)
            self.p_idx, self.p_sign = np.array(p_idx), np.array(p_sign)
        self._torch = {}

    def _t(self, name, like):
        key = (name, like.device, like.dtype)
        if key not in self._torch:
            import torch
            v = getattr(self, name)
            self._torch[key] = torch.as_tensor(v, device=like.device, dtype=torch.long if name.endswith("idx") else like.dtype)
        return self._torch[key]

    def _apply(self, x, idx, sign):
        if isinstance(x, np.ndarray):
            return x[..., getattr(self, idx)] * getattr(self, sign)
        return x[..., self._t(idx, x)] * self._t(sign, x)

    def obs(self, x):
        return self._apply(x, "o_idx", "o_sign")

    def priv(self, x):
        return self._apply(x, "p_idx", "p_sign")

    def act(self, x):
        return self._apply(x, "a_idx", "a_sign")


def mirror_mujoco_state(qpos: np.ndarray, qvel: np.ndarray, qadr: dict, dadr: dict) -> tuple[np.ndarray, np.ndarray]:
    """Reflect a free-floating MuJoCo state through the world x-z plane (base: free joint at qpos[0:7], qvel[0:6]).
    qadr / dadr: joint name -> qpos / qvel address of every hinge joint."""
    qp, qv = qpos.copy(), qvel.copy()
    qp[1] = -qpos[1]
    w, x, y, z = qpos[3:7]
    qp[3:7] = [w, -x, y, -z]
    qv[1] = -qvel[1]                                                         # world-frame linear velocity
    qv[3], qv[5] = -qvel[3], -qvel[5]                                        # body-frame angular velocity
    names = list(qadr)
    idx, sign = joint_mirror(names)
    for i, j in enumerate(names):
        src = names[idx[i]]
        qp[qadr[j]] = sign[i] * qpos[qadr[src]]
        qv[dadr[j]] = sign[i] * qvel[dadr[src]]
    return qp, qv
