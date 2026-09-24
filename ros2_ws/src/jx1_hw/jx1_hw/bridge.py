"""ROS-independent core of the JX1 hardware bridge: robot joint space <-> the two CAN hubs' frame layout.

Joint space is the policy/simulation space of simulation/joint_map.yaml (e.g. left_ankle_pitch_joint). Hub space is the
order and naming of firmware/hub/jx1_hub/config_hub_{a,b}.h (config/hw.yaml): leg, arm and waist joints map 1:1
(`<name>_joint`), the ankle is driven as its two crank motors (`<side>_ankle_motorA/B`).
  commands(): joint targets + policy_io PD gains -> per-hub (q, dq, kp, kd, tau) lists (ankle IK + motor gains)
  decode():   per-hub HubState -> joint positions/velocities/torques (ankle FK, J^-1 velocities, J^T torques)
Joints that are not on a hub (neck servos) are ignored here.
"""
from __future__ import annotations

import numpy as np

from .ankle import ParallelAnkle
from .protocol import HubState


class Bridge:
    def __init__(self, hw_cfg: dict, policy_io: dict):
        self.hubs = {h: [j["name"] for j in c["joints"]] for h, c in hw_cfg["hubs"].items()}
        self.ankle = {s: ParallelAnkle.from_params(hw_cfg["ankle"], s) for s in ("left", "right")}
        self.gains = {j: tuple(g) for j, g in policy_io["pd_gains"].items()}
        self.default = dict(policy_io["default_joint_pos"])
        self.ankle_q = {s: np.array([self.default.get(f"{s}_ankle_pitch_joint", 0.0), self.default.get(f"{s}_ankle_roll_joint", 0.0)])
                        for s in ("left", "right")}
        self.hub_joints = [f"{n}_joint" for names in self.hubs.values() for n in names if "ankle_motor" not in n] + \
                          [f"{s}_ankle_{a}_joint" for s in ("left", "right") for a in ("pitch", "roll")]
        missing = [j for j in self.hub_joints if j not in self.gains]
        if missing:                                    # fail fast: never guess gains for a motor
            raise ValueError(f"policy_io.yaml has no PD gains for hub joints {missing}; re-export the policy with rl/export.py")

    @staticmethod
    def _ankle_side(name):
        return "left" if name.startswith("left_") else "right"

    def commands(self, targets: dict, feedforward: dict | None = None) -> dict:
        """targets: joint -> position target (missing joints hold the default pose). Returns hub -> [(q, dq, kp, kd, tau)]."""
        ff = feedforward or {}
        tgt = {j: targets.get(j, self.default.get(j, 0.0)) for j in self.hub_joints}
        phi, mgain = {}, {}
        for s in ("left", "right"):
            p, r = tgt[f"{s}_ankle_pitch_joint"], tgt[f"{s}_ankle_roll_joint"]
            phi[s] = self.ankle[s].crank_angles(p, r)
            kq = (self.gains[f"{s}_ankle_pitch_joint"][0], self.gains[f"{s}_ankle_roll_joint"][0])
            dq = (self.gains[f"{s}_ankle_pitch_joint"][1], self.gains[f"{s}_ankle_roll_joint"][1])
            mgain[s] = self.ankle[s].motor_gains(*self.ankle_q[s], kq, dq)[0]            # at the current ankle pose
        out = {}
        for h, names in self.hubs.items():
            rows = []
            for n in names:
                if "ankle_motor" in n:
                    s, i = self._ankle_side(n), (0 if n.endswith("A") else 1)
                    kp_m, kd_m = mgain[s]
                    rows.append((float(phi[s][i]), 0.0, float(kp_m[i]), float(kd_m[i]), 0.0))
                else:
                    j = f"{n}_joint"
                    kp, kd = self.gains[j]
                    rows.append((float(tgt[j]), 0.0, kp, kd, float(ff.get(j, 0.0))))
            out[h] = rows
        return out

    def decode(self, states: dict) -> dict:
        """states: hub -> HubState. Returns joint -> (q, dq, tau) in joint space."""
        out, motors = {}, {"left": {}, "right": {}}
        for h, st in states.items():
            st: HubState
            for k, n in enumerate(self.hubs[h]):
                if "ankle_motor" in n:
                    motors[self._ankle_side(n)][n[-1]] = (st.q[k], st.dq[k], st.tau[k])
                else:
                    out[f"{n}_joint"] = (st.q[k], st.dq[k], st.tau[k])
        for s, m in motors.items():
            if "A" not in m or "B" not in m:
                continue
            (pa, va, ta), (pb, vb, tb) = m["A"], m["B"]
            q = self.ankle[s].joint_angles(pa, pb, guess=self.ankle_q[s])
            self.ankle_q[s] = q
            dq = self.ankle[s].joint_velocity(*q, va, vb)
            tq = self.ankle[s].joint_torque(*q, ta, tb)
            out[f"{s}_ankle_pitch_joint"] = (float(q[0]), float(dq[0]), float(tq[0]))
            out[f"{s}_ankle_roll_joint"] = (float(q[1]), float(dq[1]), float(tq[1]))
        return out
