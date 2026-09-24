"""Physically consistent structural load samples for the JX1 leg (OI-4).

Instead of stacking every actuator's peak torque on top of a landing force, every sample starts from a ground reaction
(GRF) at a centre of pressure on the sole and is propagated through the leg kinematics:

LC1 (strength)  poses x CoP grid x GRF directions x free yaw moments at 3 BW. For each sample the static joint torques
                (hip yaw/roll/pitch, knee, both ankle motors through the parallel-ankle model) are computed; if any
                exceeds its actuator's peak, the whole GRF is scaled down to the saturation point — the joint would
                back-drive, so the structure never sees more than the actuators can react.
LC2 (fatigue)   the fast-walk, nominal-walk and turning time series from calculations/results/iter1_B_*: joint angles
                and inverse-dynamics torques -> equivalent foot wrench W = A(q)^-1 tau (stance and swing).
For both, the wrench is transported to every structural interface and expressed in the part (= link) frame:
  hip_yaw / hip_roll / pelvis   wrench of the distal leg about the hip centre
  thigh                         wrench about the knee centre
  shin                          ankle fork pin (force + yaw moment) and the two push-rod forces at the crank pins
Output: dict part -> group -> {"LC1": (N, 6) array, "LC2": [(T, 6) arrays per series]}; saved as loads.npz for reuse.
"""
from __future__ import annotations

import itertools
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cad.leg_kinematics import LegCAD  # noqa: E402
from cad.params import PKG, ACT, SOLE_TO_ANKLE, FOOT_L, FOOT_HEEL, FOOT_W, HIP_Y, THIGH, SHIN, CRANK_R  # noqa: E402

RES = ROOT / "calculations" / "results" / "iter1_B_knee_and_pitch_RS04"
PEAK = {"XL": 120.0, "L": 60.0, "M": 36.0}
TAU_MAX = {"hip_yaw": PEAK["M"], "hip_roll": PEAK["L"], "hip_pitch": PEAK[PKG["pitch_class"]], "knee": PEAK[PKG["knee_class"]]}
MOTOR_MAX = PEAK[PKG["ankle_class"]]
JOINTS = ["hip_yaw", "hip_roll", "hip_pitch", "knee", "ankle_pitch", "ankle_roll"]


def joint_axes(W):
    """World origin and unit axis of the six leg joints for link transforms W (LegCAD.links)."""
    return [(W["hip_yaw"][:3, 3], W["hip_yaw"][:3, 2]), (W["hip_roll"][:3, 3], W["hip_roll"][:3, 0]),
            (W["thigh"][:3, 3], W["thigh"][:3, 1]), (W["shin"][:3, 3], W["shin"][:3, 1]),
            (W["ankle_cross"][:3, 3], W["ankle_cross"][:3, 1]), (W["foot"][:3, 3], W["foot"][:3, 0])]


def torques(W, p, F, M):
    """Static joint torques of an external wrench (force F at point p plus couple M) about each joint axis."""
    return np.array([a @ (np.cross(p - o, F) + M) for o, a in joint_axes(W)])


def rod_split(leg, W, comp, F, M_ankle):
    """Foot equilibrium: rods react the foot moment's components about the two ankle axes; returns rod tensions
    f_A, f_B (+ = rod pulls the foot post up), unit rod directions (post -> crank pin) and crank-pin points (world)."""
    pa = W["foot"][:3, 3]
    ax_p, ax_r = W["ankle_cross"][:3, 1], W["foot"][:3, 0]
    cols, dirs, pins = [], [], []
    for rod in ("RodA", "RodB"):
        R = comp[rod]
        u = R[:3, 2]                                   # rod frame +z: from lower (foot) ball to upper (crank) ball
        pin = R[:3, 3]
        post = pin - comp[rod + "_len"] * u if (rod + "_len") in comp else pin - 0.1 * u
        m = np.cross(post - pa, u)                     # moment of a unit rod tension about the ankle centre
        cols.append([m @ ax_p, m @ ax_r])
        dirs.append(u)
        pins.append(pin)
    A = np.array(cols).T                               # 2x2: [pitch; roll] moment per unit tension of rod A, B
    b = -np.array([M_ankle @ ax_p, M_ankle @ ax_r])
    f = np.linalg.solve(A, b)
    return f, dirs, pins


def crank_torque(leg, W, comp, f, dirs, pins):
    """Motor torque needed to hold each rod tension: moment of the rod force about the motor axis (shin y at zA/zB)."""
    out = []
    for k, key in enumerate(("rotorA", "rotorB")):
        o, a = W[key][:3, 3], W[key][:3, 1]
        out.append(a @ np.cross(pins[k] - o, -f[k] * dirs[k]))
    return np.array(out)


def interface_wrenches(leg, q, p, F, Mfree):
    """Wrenches on each part (in the part frame) for a GRF (F at p, couple Mfree) in pose q."""
    W = leg.links(q)
    comp = leg.component_poses(q)
    out = {}

    def about(frame, point):
        R = W[frame][:3, :3]
        M = np.cross(p - point, F) + Mfree
        return np.concatenate([R.T @ F, R.T @ M])

    hip = W["hip_yaw"][:3, 3]
    knee = W["shin"][:3, 3]
    out[("hip_yaw", "leg")] = about("hip_yaw", hip)
    out[("hip_roll", "leg")] = about("hip_roll", hip)
    out[("pelvis", "leg")] = about("pelvis", hip)
    out[("thigh", "knee")] = about("thigh", knee)
    pa = W["foot"][:3, 3]
    M_ankle = np.cross(p - pa, F) + Mfree
    f, dirs, pins = rod_split(leg, W, comp, F, M_ankle)
    Rs = W["shin"][:3, :3]
    Fpin = F + f[0] * dirs[0] + f[1] * dirs[1]
    # the universal joint passes the yaw component (about the axis normal to both pins) — use the foot moment's
    # component along the shin z axis as the transmitted yaw couple
    Mz = (Rs.T @ M_ankle)[2]
    out[("shin", "fork")] = np.concatenate([Rs.T @ Fpin, [0.0, 0.0, Mz]])
    ref = {"rodA": np.array([-CRANK_R, PKG["rod_crank_w"] * leg.sy, PKG["ankle_A_z"]]),
           "rodB": np.array([-CRANK_R, -PKG["rod_crank_w"] * leg.sy, PKG["ankle_B_z"]])}
    for k, key in enumerate(("rodA", "rodB")):
        Fr = Rs.T @ (-f[k] * dirs[k])                              # rod pulls the crank pin toward the foot when in tension
        pin_s = Rs.T @ (pins[k] - W["shin"][:3, 3])
        out[("shin", key)] = np.concatenate([Fr, np.cross(pin_s - ref[key], Fr)])   # about the zero-pose pin point
    tau = torques(W, p, F, Mfree)
    tm = crank_torque(leg, W, comp, f, dirs, pins)
    return out, tau, tm


def lc1_samples(mass_kg, side=1):
    """Actuator-capped landing/peak samples. Returns dict (part, group) -> (N, 6) and a summary."""
    leg = LegCAD(side)
    BW = mass_kg * 9.81
    d = math.radians
    poses = {"stand": {"hip_pitch": d(-18), "knee": d(36), "ankle_pitch": d(-18)},
             "walk_crouch": {"hip_pitch": d(-30), "knee": d(58), "ankle_pitch": d(-28)},
             "landing_crouch": {"hip_pitch": d(-45), "knee": d(90), "ankle_pitch": d(-45)},
             "deep_squat": {"hip_pitch": d(-70), "knee": d(120), "ankle_pitch": d(-50)},
             "single_leg": {"hip_pitch": d(-31), "knee": d(55), "ankle_pitch": d(-24), "hip_roll": d(-14), "ankle_roll": d(14)},
             "heel_strike": {"hip_pitch": d(-30), "knee": d(15), "ankle_pitch": d(15)},
             "toe_off": {"hip_pitch": d(15), "knee": d(35), "ankle_pitch": d(-50)},
             "turn_stance": {"hip_yaw": d(20), "hip_pitch": d(-30), "knee": d(58), "ankle_pitch": d(-28)}}
    xs = [-FOOT_HEEL + 0.008, -0.030, 0.0, 0.050, 0.100, FOOT_L - FOOT_HEEL - 0.008]
    ys = [-FOOT_W / 2 + 0.008, 0.0, FOOT_W / 2 - 0.008]
    shear = [(0, 0), (0.3, 0), (-0.3, 0), (0, 0.3), (0, -0.3)]
    myaw = [0.0, 15.0, -15.0]
    rows, summary = {}, {"samples": 0, "scaled": 0, "min_scale": 1.0}
    for pname, q in poses.items():
        W = leg.links(q)
        Rf = W["foot"][:3, :3]
        pf = W["foot"][:3, 3]
        for x, y, (sx, sy_), mz in itertools.product(xs, ys, shear, myaw):
            p = pf + Rf @ np.array([x, y * side, -SOLE_TO_ANKLE])
            F = 3 * BW * np.array([sx, sy_, 1.0])
            M = np.array([0.0, 0.0, mz])
            out, tau, tm = interface_wrenches(leg, q, p, F, M)
            ratio = max(max(abs(tau[k]) / TAU_MAX[j] for k, j in enumerate(JOINTS[:4])), max(abs(tm)) / MOTOR_MAX)
            s = 1.0 / ratio if ratio > 1 else 1.0
            summary["samples"] += 1
            if s < 1:
                summary["scaled"] += 1
                summary["min_scale"] = min(summary["min_scale"], s)
            for key, w in out.items():
                rows.setdefault(key, []).append(s * w)
    return {k: np.array(v) for k, v in rows.items()}, summary


def lc2_series(side=1, stride=4):
    """Walking/turning time series -> interface wrench histories. Returns dict (part, group) -> list of (T, 6) arrays."""
    leg = LegCAD(side)
    series = {}
    for f in ("timeseries_walk_fast_0.79ms.csv", "timeseries_walk_nominal_0.52ms.csv", "timeseries_turn_15deg_per_step.csv"):
        df = pd.read_csv(RES / f).iloc[::stride]
        per = {}
        for _, r in df.iterrows():
            q = {j: float(r[f"l_{j}_q"]) for j in JOINTS}
            tau = np.array([float(r[f"l_{j}_tau"]) for j in JOINTS])
            W = leg.links(q)
            pa = W["foot"][:3, 3]
            A = np.array([np.concatenate([np.cross(a, pa - o), a]) for o, a in joint_axes(W)])   # tau = A @ [F; M_about_ankle]
            wrench = np.linalg.lstsq(A, tau, rcond=None)[0]
            F, M = wrench[:3], wrench[3:]
            out, _, _ = interface_wrenches(leg, q, pa, F, M)
            for key, w in out.items():
                per.setdefault(key, []).append(w)
        for key, v in per.items():
            series.setdefault(key, []).append(np.array(v))
    return series


def build(mass_kg=27.466):
    lc1, summ = lc1_samples(mass_kg)
    lc2 = lc2_series()
    return lc1, lc2, summ


if __name__ == "__main__":
    lc1, lc2, summ = build()
    print(summ)
    for key, arr in lc1.items():
        mx = np.abs(arr).max(0)
        print(f"LC1 {key[0]:9s} {key[1]:5s} max |F| {np.round(mx[:3], 0)} N  max |M| {np.round(mx[3:], 1)} N m")
    for key, lst in lc2.items():
        mx = np.max([np.abs(a).max(0) for a in lst], axis=0)
        print(f"LC2 {key[0]:9s} {key[1]:5s} max |F| {np.round(mx[:3], 0)} N  max |M| {np.round(mx[3:], 1)} N m")
