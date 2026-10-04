"""Capture-point stepping on top of the verified gaits: a shove is caught by moving the next footstep.

The gaits in gaits/*.json are verified joint trajectories (ZMP preview control on the full JX0 model, closed loop on
the servo model, robust to model errors). This player keeps them, and adds what they cannot do: step somewhere else.

Plan (once per gait): the planned pelvis is level at a constant height, so the joint angles + stance flags give the
whole planned motion in the gait's own world frame: feet, pelvis, whole-body centre of mass (COM, kinematics.com) and
its divergent component of motion (DCM, the "capture point")  xi = c + c_dot / omega.

Every frame (100 Hz):
1. measure the COM the same way, from the real support foot, the support leg's encoders and the IMU tilt, filtered
   with the pendulum model; the DCM error e = xi_measured - xi_planned (the same kinematic model is on both sides, so
   the model's own errors cancel and e is what the floor, a push or the servos did differently);
2. in single support: the stiff servos pull the body back onto the plan by moving the zero-moment point (ZMP) inside
   the stance foot, so an error only grows beyond the point where the ZMP reaches the foot's edge. Holding the ZMP
   shifted by dz until the touchdown removes dz (exp(omega t) - 1) of the error there; whatever needs more than the
   foot can give (a margin inside its edges) is the step: the swing foot is aimed that much further out / ahead /
   behind, re-aimed every frame, and clamped to the leg's reach and to the other foot (no crossing);
3. every foot keeps the offset it landed with, the next footstep is planned relative to the support foot, and the
   pelvis follows the plan shifted by the offsets of the feet it stands on: after a caught push the robot simply walks
   on from where it landed;
4. both legs come from the closed-form inverse kinematics (kinematics.py), the arms from the gait; the stance-leg
   ankle and hip tilt feedback of balance.py is added on top. When the body is tilted (a shove rocks it onto a foot
   edge) the swing leg is computed from the measured pelvis, so the foot keeps its path over the floor instead of
   dragging on it.
With no disturbance the offsets stay zero and the joints are exactly the verified gait.
"""
from __future__ import annotations

import math

import numpy as np

from . import kinematics as K
from .balance import Balance

G = 9.81
PARAMS = {
    "margin": 0.012,                     # m: the ZMP the stance foot can take stays this far inside its edges
    "gain": 1.0,                         # share of the rest the step takes
    "dx_lim": (-0.06, 0.10),             # swing ankle relative to the support ankle, support-foot frame (m)
    "w_lim": (0.08, 0.17),               # sideways: 8 cm keeps 1 cm between the feet; 17 cm is the hip-roll reach
    "est_gains": (0.35, 0.074),          # COM filter (alpha, beta): position / velocity correction per frame
    "pelvis_tau": 0.06,                  # s: the pelvis offset follows the feet's offsets this smoothly
    "horizon": "mid_ds",                 # predict the error to the middle of the double support after touchdown
    "swing_world": (0.02, 0.05),         # rad: from this pelvis tilt to this, the swing leg is computed from the measured
                                         # (tilted) pelvis, so a rocking body does not drag the swing foot on the floor
    "swing_blend": 0.06,                 # s: that switches in after lift-off (and out over the double support)
}


def _rot2(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s], [s, c]])


def _smooth(s):
    s = min(1.0, max(0.0, s))
    return s * s * (3 - 2 * s)


class CaptureStepper:
    """s = CaptureStepper(gait); s.start(); then for k in range(s.n): q = s.frame(k, q_meas, roll, pitch, wx, wy)."""

    def __init__(self, gait: dict, gains: dict | None = None, params: dict | None = None):
        self.p = {**PARAMS, **(params or {})}
        self.gains = gains
        self.dt = float(gait["dt"])
        self.joints = list(gait["joints"])
        self.Q = np.array(gait["q"], float)
        self.stance = [tuple(bool(v) for v in st) for st in gait["stance"]]
        self.n = len(self.Q)
        self.hip_h = float(gait.get("hip_height_m", 0.215))
        self.col = {j: i for i, j in enumerate(self.joints)}
        self._plan()

    # ------------------------------------------------------------------------------------------------ the plan
    def _legs(self, k):
        return {s: np.array([self.Q[k, self.col[f"{s}_{j}"]] for j in K.LEG]) for s in "lr"}

    def _plan(self):
        n, dt = self.n, self.dt
        rel = []                                                    # per frame: {side: (ankle in pelvis frame, foot yaw)}
        comr = np.zeros((n, 3))
        for k in range(n):
            q = self._legs(k)
            r = {}
            for s in "lr":
                p, R = K.fk(q[s], s)
                r[s] = (p, math.atan2(R[1, 0], R[0, 0]))
            rel.append(r)
            comr[k] = K.com(q["l"], q["r"])[0]
        self.rel = rel
        pel = np.zeros((n, 3))                                      # x, y, yaw (level pelvis at hip_h)
        feet = {s: np.zeros((n, 4)) for s in "lr"}                  # ankle x, y, z, yaw
        for k in range(n):
            if k == 0:
                anchor = None
            else:
                both = [s for i, s in enumerate("lr") if self.stance[k - 1][i] and self.stance[k][i]]
                anchor = both[0] if both else ("l" if self.stance[k][0] else "r")
            if anchor is not None:
                p_a, yaw_a = rel[k][anchor]
                psi = feet[anchor][k - 1, 3] - yaw_a
                pel[k, :2] = feet[anchor][k - 1, :2] - (K.rz(psi) @ p_a)[:2]
                pel[k, 2] = psi
            for s in "lr":
                if s == anchor:
                    feet[s][k] = feet[s][k - 1]
                else:
                    p, yaw = rel[k][s]
                    w = K.rz(pel[k, 2]) @ p
                    feet[s][k] = [pel[k, 0] + w[0], pel[k, 1] + w[1], self.hip_h + w[2], pel[k, 2] + yaw]
        self.pel, self.feet = pel, feet
        c = np.array([pel[k, :2] + (K.rz(pel[k, 2]) @ comr[k])[:2] for k in range(n)])
        self.z_com = self.hip_h + float(np.mean(comr[:, 2]))
        self.w = math.sqrt(G / self.z_com)
        cd = np.gradient(c, dt, axis=0)
        cdd = np.gradient(cd, dt, axis=0)
        self.c_plan, self.xi_plan = c, c + cd / self.w
        self.zmp_plan = c - cdd / self.w ** 2
        fl, fr = feet["l"][:, :2], feet["r"][:, :2]
        d = fr - fl
        self.lam = np.clip(np.einsum("ij,ij->i", c - fl, d) / np.maximum(1e-9, np.einsum("ij,ij->i", d, d)), 0.0, 1.0)
        # single-support segments: swing side, touchdown frame, and the middle of the double support after it
        self.seg = [None] * n
        k = 0
        while k < n:
            st = self.stance[k]
            if st[0] != st[1]:
                k0 = k
                while k < n and self.stance[k] == st:
                    k += 1
                swing = "r" if st[0] else "l"
                kd = k
                while kd < n and self.stance[kd][0] and self.stance[kd][1]:
                    kd += 1
                for j in range(k0, k):
                    self.seg[j] = {"support": "l" if st[0] else "r", "swing": swing, "k0": k0, "td": k,
                                   "mid": min(n - 1, (k + kd) // 2)}
            else:
                k += 1

    # ------------------------------------------------------------------------------------------------ running
    def start(self):
        self.o = {"l": np.zeros(2), "r": np.zeros(2)}               # where each real foot is, relative to its plan
        self.o_pel = np.zeros(2)
        self.o_sw = None
        self.last_seg = None
        self.c = self.cd = None
        self.balance = Balance(self.gains, dt=self.dt)
        self.log = []

    def _support(self, k):
        st = self.stance[k]
        if st[0] != st[1]:
            return "l" if st[0] else "r"
        return "l" if self.lam[k] < 0.5 else "r"

    def _measure(self, k, q, roll, pitch):
        s = self._support(k)
        legs = {t: np.array([q[f"{t}_{j}"] for j in K.LEG]) for t in "lr"}
        p_ank, R_fp = K.fk(legs[s], s)
        f = self.feet[s][k]
        yaw_p = f[3] - math.atan2(R_fp[1, 0], R_fp[0, 0])
        R_wp = K.rz(yaw_p) @ K.ry(pitch) @ K.rx(roll)
        ankle = np.array([f[0] + self.o[s][0], f[1] + self.o[s][1], f[2]])
        pelvis = ankle - R_wp @ p_ank
        self.pel_meas, self.tilt = pelvis, (roll, pitch)
        c_meas = (pelvis + R_wp @ K.com(legs["l"], legs["r"])[0])[:2]
        if self.c is None:
            self.c, self.cd = c_meas, (self.c_plan[min(k + 1, self.n - 1)] - self.c_plan[k]) / self.dt
        else:
            dt = self.dt
            acc = self.w ** 2 * (self.c - (self.zmp_plan[max(0, k - 1)] + self.o_pel))
            c_p, cd_p = self.c + self.cd * dt + 0.5 * acc * dt * dt, self.cd + acc * dt
            a, b = self.p["est_gains"]
            r = c_meas - c_p
            self.c, self.cd = c_p + a * r, cd_p + (b / dt) * r
        return self.c + self.cd / self.w

    def frame(self, k: int, q: dict, roll, pitch, wx, wy) -> dict:
        """Joint goals (radians) for gait frame k from the measured joints, IMU roll/pitch and rates."""
        P, dt = self.p, self.dt
        xi = self._measure(k, q, roll, pitch)
        err = xi - (self.xi_plan[k] + self.o_pel)
        seg = self.seg[k]
        swing = None
        if seg is not None:
            s, sw = seg["support"], seg["swing"]
            if k == seg["k0"] or self.o_sw is None:
                self.o_sw = self.o[sw].copy()
            k_h = seg["mid"] if P["horizon"] == "mid_ds" else seg["td"]
            grow = math.exp(self.w * max(0.0, (k_h - k) * dt))
            g = max(1e-6, grow - 1.0)
            fs, fl = self.feet[s][k], self.feet[sw][seg["td"]]
            R = _rot2(fs[3])
            # what the stance foot can take: the ZMP range left around the planned ZMP, a margin inside the edges
            zp = R.T @ (self.zmp_plan[k] - fs[:2])
            m = P["margin"]
            lo = np.array([K.FOOT_X[0] + m, -K.FOOT_HALF_W + m]) - zp
            hi = np.array([K.FOOT_X[1] - m, K.FOOT_HALF_W - m]) - zp
            need = R.T @ err * grow / g
            dz = np.clip(need, np.minimum(lo, 0.0), np.maximum(hi, 0.0))
            step = P["gain"] * (R @ (need - dz)) * g
            tgt = self.o[s] + step
            # clamp the landing relative to the real support foot (support-foot frame)
            rel = R.T @ ((fl[:2] + tgt) - (fs[:2] + self.o[s]))
            sg = 1.0 if sw == "l" else -1.0
            rel = np.array([np.clip(rel[0], *P["dx_lim"]), sg * np.clip(sg * rel[1], *P["w_lim"])])
            tgt = fs[:2] + self.o[s] + R @ rel - fl[:2]
            # the foot moves to its target over the rest of the swing (re-aimed every frame, smoothly)
            n_sw = seg["td"] - seg["k0"]
            u0, u1 = _smooth((k - seg["k0"]) / n_sw), _smooth((k + 1 - seg["k0"]) / n_sw)
            self.o_sw = self.o_sw + (tgt - self.o_sw) * ((u1 - u0) / max(1e-9, 1.0 - u0))
            swing = sw
            self.tgt = tgt
        elif self.o_sw is not None:                                    # touchdown: the foot keeps where it landed
            prev = self.seg[k - 1] if k > 0 else None
            if prev is not None:
                self.o[prev["swing"]] = self.o_sw.copy()
            self.o_sw = None
        # pelvis: the plan shifted by the offsets of the feet it stands on
        o_l = self.o["l"]
        o_r = self.o["r"]
        target = o_l + (o_r - o_l) * self.lam[k]
        a = 1.0 - math.exp(-dt / P["pelvis_tau"])
        self.o_pel = self.o_pel + a * (target - self.o_pel)
        # how much of the swing leg follows the measured pelvis: only when tilted, only off the ground
        lo, hi = P["swing_world"]
        w_tilt = min(1.0, max(0.0, (math.hypot(*self.tilt) - lo) / (hi - lo)))
        nb = max(1, int(round(P["swing_blend"] / dt)))
        w_leg = {"l": 0.0, "r": 0.0}
        if seg is not None:
            w_leg[seg["swing"]] = min(1.0, (k - seg["k0"] + 1) / nb) * w_tilt
        else:
            prev = self.last_seg
            if prev is not None and k >= prev["td"]:
                n_ds = max(1, 2 * (prev["mid"] - prev["td"]))
                w_leg[prev["swing"]] = max(0.0, 1.0 - (k - prev["td"] + 1) / n_ds) * w_tilt
        if seg is not None:
            self.last_seg = seg
        q_cmd = self._ik(k, swing, w_leg)
        for name, v in self.balance.update(roll, pitch, wx, wy, self.stance[k]).items():
            q_cmd[name] += v
        self.log.append((k, *err, *self.o_pel, *(self.o_sw if self.o_sw is not None else (0.0, 0.0))))
        return q_cmd

    def _ik(self, k, swing, w_leg):
        pel = self.pel[k]
        psi = pel[2]
        pos_c = np.array([pel[0] + self.o_pel[0], pel[1] + self.o_pel[1], self.hip_h])
        q = {j: float(self.Q[k, i]) for j, i in self.col.items()}
        for s in "lr":
            f = self.feet[s][k]
            o = self.o_sw if (s == swing and self.o_sw is not None) else self.o[s]
            w = w_leg[s]
            if not o.any() and not self.o_pel.any() and w == 0.0:
                continue                                               # exactly the verified gait
            pos = (1.0 - w) * pos_c + w * self.pel_meas
            Rp = K.rz(psi) @ K.ry(w * self.tilt[1]) @ K.rx(w * self.tilt[0])
            a = np.array([f[0] + o[0], f[1] + o[1], f[2]])
            p_ank = Rp.T @ (a - pos)
            h = K.hip(s)
            r = p_ank - h
            nr = float(np.linalg.norm(r))
            if nr > 0.199:
                p_ank = h + r * (0.199 / nr)
            q.update(K.leg_dict(K.ik(p_ank, Rp.T @ K.rz(f[3]), s), s))
        return q
