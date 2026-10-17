"""JX0 reference gait for the whole-body policy, built from the robot's verified gaits (jx0bot/gaits, the ones the
walking, push and endurance checks pass with):

    python jx0/rl/gait_reference.py        -> jx0/rl/config/jx0_gait_reference.json (+ a table check)

Each verified gait's steady cycle (one left and one right step, 1.2 s) is resampled over the gait clock's phase:
phase = stance_fraction at the left foot's lift-off, as the training clock (rl/jx1_rl/env.py: a leg is in swing for
phase >= stance_fraction). Every cycle is a deviation from the walking stance. The part all of them share is
the stepping itself (S: lifting the feet in turn), so each gait becomes S + its own direction part E_k:
forward 0.05 m/s, backward 0.033 m/s, sideways 0.025 m/s, turning 0.29 rad/s (the right-hand side gaits are mirror
images of the left ones). The reference for a command (vx, vy, wz):

    q_ref(phase, cmd) = stance + moving * (S(phase) + sum_k w_k E_k(phase)),   w_k = command component / gait speed

with moving = 0 below gait.stand_command_threshold. The policy's 17 outputs are corrections to it:
target = q_ref + action_scale * action. reference() below is the numpy version (training env, sim-to-sim, robot);
jx1_isaaclab/mdp.py has the torch twin.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GAITS = ROOT / "jx0" / "software" / "jx0bot" / "gaits"
SIDE_REALISED = 1.0     # the side cycle on the gait clock walks this fraction of its planned speed (see build())
OUT = HERE / "config" / "jx0_gait_reference.json"
N_PHASE = 120
FLIP = ("roll", "yaw")


def rl_name(j: str) -> str:
    s, rest = j.split("_", 1)
    return {"l": "left_", "r": "right_"}.get(s, "") + (rest if s in ("l", "r") else j) + "_joint"


def mirror(names, q):
    """Left/right mirror image of joint vectors q (..., n) (roll / yaw joints change sign)."""
    out = np.empty_like(q)
    for i, j in enumerate(names):
        o = j.replace("left_", "\0").replace("right_", "left_").replace("\0", "right_")
        out[..., i] = q[..., names.index(o)] * (-1.0 if any(t in j for t in FLIP) else 1.0)
    return out


def cycle(name, names):
    """The gait's steady cycle as (N_PHASE, n) deviations from its first frame, starting at a left lift-off, plus the
    left foot's stance fraction and the cycle frames."""
    g = json.loads((GAITS / f"{name}.json").read_text(encoding="utf-8"))
    idx = [g["joints"].index(j) if j in g["joints"] else None for j in names_short(names)]
    q = np.array(g["q"])
    full = np.zeros((len(q), len(names)))
    for c, i in enumerate(idx):
        if i is not None:
            full[:, c] = q[:, i]
    st = np.array(g["stance"])
    lifts = [i for i in range(1, len(st)) if st[i - 1][0] and not st[i][0]]
    a, b = (lifts[1], lifts[2]) if len(lifts) >= 3 else (lifts[0], lifts[0] + int(round(2 * g["step_time_s"] / g["dt"])))
    seg = full[a:b + 1]
    t = np.linspace(0, len(seg) - 1, N_PHASE, endpoint=False)
    res = np.stack([np.interp(t, np.arange(len(seg)), seg[:, c]) for c in range(len(names))], axis=1)
    swing = int(np.sum(~st[a:b, 0]))                                   # frames the left foot is in the air
    return res - full[0], 1.0 - swing / (b - a), full[0], (a, b)


def names_short(names):
    out = []
    for j in names:
        j = j[:-len("_joint")]
        for side, s in (("left_", "l_"), ("right_", "r_")):
            if j.startswith(side):
                j = s + j[len(side):]
        out.append(j)
    return out


def build(names):
    gaits = {"forward": ("forward", (0.05, 0.0, 0.0)), "backward": ("backward", (-0.0333, 0.0, 0.0)),
             "left": ("side_left", (0.0, 0.02, 0.0)), "turn_left": ("turn_left", (0.0, 0.0, math.radians(10.0) / 0.6))}
    cyc, sf, stance = {}, [], None
    for k, (g, _) in gaits.items():
        d, f, st0, _ = cycle(g, names)
        cyc[k] = d
        sf.append(f)
        stance = st0 if stance is None else stance
    S = 0.5 * (cyc["forward"] + cyc["backward"])                        # the stepping both share
    E = {k: cyc[k] - S for k in cyc}
    # the right-hand gaits: mirror images, half a cycle later (the right leg leads)
    half = N_PHASE // 2
    E["right"] = np.roll(mirror(names, E["left"]), half, axis=0)
    E["turn_right"] = np.roll(mirror(names, E["turn_left"]), half, axis=0)
    def gait(name):
        return json.loads((GAITS / f"{name}.json").read_text(encoding="utf-8"))
    # sideways: the side gait's planned speed (lateral_step / step_time; v0.5 leads with the foot on that side, 2 x
    # the step out, the other foot closes). Played under the policy it walks about that fast; with no corrections at
    # all it slips to about 60 % (SIDE_REALISED < 1 made the policy overshoot by 1 / 0.62)
    side = gait("side_left")
    v_side = SIDE_REALISED * abs(side["lateral_step_m"]) / side["step_time_s"]
    speeds = {"forward": 0.05, "backward": 0.0333, "left": v_side, "right": v_side,
              "turn_left": math.radians(10.0) / 0.6, "turn_right": math.radians(10.0) / 0.6}
    return {"source": "jx0bot/gaits (verified): forward, backward, side_left, turn_left; right = mirrored",
            "period_s": 1.2, "stance_fraction": round(float(np.mean(sf)), 4), "n_phase": N_PHASE, "joints": names,
            "stance": [round(float(v), 6) for v in stance],
            "step": np.round(S, 6).tolist(),
            "directions": {k: {"speed": round(speeds[k], 5), "table": np.round(E[k], 6).tolist()} for k in E}}


class Reference:
    """q_ref(phase, command) for the joints of the table (numpy, batched)."""

    def __init__(self, table: dict, joints=None, stand_threshold=None):
        self.t = table
        names = table["joints"]
        cols = [names.index(j) for j in (joints or names)]
        self.stance = np.array(table["stance"])[cols]
        self.S = np.array(table["step"])[:, cols]
        self.E = {k: np.array(v["table"])[:, cols] for k, v in table["directions"].items()}
        self.v = {k: v["speed"] for k, v in table["directions"].items()}
        self.sf = table["stance_fraction"]
        self.thr = stand_threshold

    def weights(self, cmd):
        cmd = np.atleast_2d(np.asarray(cmd, dtype=np.float64))
        vx, vy, wz = cmd[:, 0], cmd[:, 1], cmd[:, 2]
        return {"forward": np.clip(vx, 0, None) / self.v["forward"], "backward": np.clip(-vx, 0, None) / self.v["backward"],
                "left": np.clip(vy, 0, None) / self.v["left"], "right": np.clip(-vy, 0, None) / self.v["right"],
                "turn_left": np.clip(wz, 0, None) / self.v["turn_left"], "turn_right": np.clip(-wz, 0, None) / self.v["turn_right"]}

    def __call__(self, phase, cmd):
        """phase (N,) in [0, 1) of the training clock (left leg), cmd (N, 3) -> (N, n)."""
        phase = np.atleast_1d(np.asarray(phase, dtype=np.float64))
        cmd = np.atleast_2d(np.asarray(cmd, dtype=np.float64))
        k = np.mod(phase - self.sf, 1.0) * self.S.shape[0]                  # table row 0 = left lift-off
        i0 = np.floor(k).astype(int) % self.S.shape[0]
        i1 = (i0 + 1) % self.S.shape[0]
        a = (k - np.floor(k))[:, None]

        def at(T):
            return T[i0] * (1 - a) + T[i1] * a
        moving = np.ones(len(cmd)) if self.thr is None else (np.linalg.norm(cmd, axis=1) >= self.thr).astype(np.float64)
        dev = at(self.S)
        for name, w in self.weights(cmd).items():
            dev = dev + w[:, None] * at(self.E[name])
        return self.stance + moving[:, None] * dev


def load(path=OUT, joints=None, stand_threshold=None):
    return Reference(json.loads(Path(path).read_text(encoding="utf-8")), joints, stand_threshold)


def main():
    sys.path.insert(0, str(ROOT / "rl"))
    import yaml
    cfg = yaml.safe_load((HERE / "config" / "jx0_walk17.yaml").read_text(encoding="utf-8"))
    names = cfg["policy_joints"]
    table = build(names)
    OUT.write_text(json.dumps(table, indent=0), encoding="utf-8")
    ref = Reference(table, stand_threshold=0.02)
    # check: the forward command at the gait's own speed gives back the verified forward cycle
    d, _, st0, _ = cycle("forward", names)
    ph = np.mod(table["stance_fraction"] + np.arange(N_PHASE) / N_PHASE, 1.0)
    back = ref(ph, np.tile([0.05, 0.0, 0.0], (N_PHASE, 1)))
    err = float(np.abs(back - (st0 + d)).max())
    print(f"{OUT.relative_to(ROOT)}: stance fraction {table['stance_fraction']}, period {table['period_s']} s, "
          f"forward cycle rebuilt within {err:.2e} rad; step-in-place amplitude "
          f"{np.abs(np.array(table['step'])).max(axis=0).round(3).tolist()}")


if __name__ == "__main__":
    main()
