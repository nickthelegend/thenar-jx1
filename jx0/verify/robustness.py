"""Does JX0 really walk? Robustness of the verified gaits + the robot's balance controller (jx0bot/balance.py) when the
real robot differs from the model, and when it is pushed.

Model-error trials: each trial walks a gait in MuJoCo with randomly wrong "reality":
  servo stiffness x0.6-1.4 and damping x0.5-1.5, servo torque/speed x0.85-1.0 (battery sag), bus latency 0-40 ms,
  gear backlash 0-0.6 deg, IMU noise (0.3 deg, 0.02 rad/s) and bias +-1 deg, upper-body mass x0.9-1.1 with its centre
  of mass off by up to 8 mm (x) / 4 mm (y), floor friction 0.5-1.0, floor slope up to +-2 deg in both directions.
Push trials: a sideways shove on the torso (0.12 s) at 24 moments of a 10-step walk, both directions.

    python jx0/verify/robustness.py baseline        # evaluate the current balance gains
    python jx0/verify/robustness.py tune            # random search for better gains, then evaluate them
    -> jx0/results/verify_robustness.json
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from collections import deque
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "jx0" / "sim"))           # module level: Windows worker processes re-import this file
sys.path.insert(0, str(ROOT / "jx0" / "software"))
os.environ["JX0_STL_DIR"] = str(ROOT / "nonexistent")   # physics only: plain box visuals load faster
OUT = ROOT / "jx0" / "results" / "verify_robustness.json"
MC_GAITS = ["forward", "forward_4", "backward_4", "turn_left_2", "turn_right_2", "side_left_2", "side_right_2"]
_CACHE = {}


def _setup(gait, overrides=None):
    key = (gait, json.dumps(overrides or {}, sort_keys=True))
    if key not in _CACHE:
        os.environ["JX0_STL_DIR"] = str(ROOT / "nonexistent")       # physics only: plain box visuals load faster
        sys.path.insert(0, str(ROOT / "jx0" / "sim"))
        sys.path.insert(0, str(ROOT / "jx0" / "software"))
        import mujoco
        import walk_jx0 as W
        from jx1calc.design import Design
        design = Design(W.DESIGN)
        xml = W.build(design)
        m = mujoco.MjModel.from_xml_string(xml)
        saved = dict(W.COMMON)
        W.COMMON.update(overrides or {})
        try:
            g, res = W.plan(m, design, gait)
        finally:
            W.COMMON.clear()
            W.COMMON.update(saved)
        _CACHE[key] = (xml, g, res, design.act_classes["ST"])
    return _CACHE[key]


def nominal():
    return {"kp": 1.0, "kd": 1.0, "stall": 1.0, "latency": 0, "backlash_deg": 0.0, "imu_deg": 0.0, "gyro": 0.0,
            "bias_deg": [0.0, 0.0], "mass": 1.0, "com_mm": [0.0, 0.0], "mu": 0.9, "slope_deg": [0.0, 0.0]}


def sample(rng, latencies=(0, 1, 2)):
    return {"kp": rng.uniform(0.6, 1.4), "kd": rng.uniform(0.5, 1.5), "stall": rng.uniform(0.85, 1.0),
            "latency": int(rng.choice(latencies)), "backlash_deg": rng.uniform(0.0, 0.6), "imu_deg": 0.3, "gyro": 0.02,
            "bias_deg": list(rng.uniform(-1.0, 1.0, 2)), "mass": rng.uniform(0.9, 1.1),
            "com_mm": [rng.uniform(-8, 8), rng.uniform(-4, 4)], "mu": rng.uniform(0.5, 1.0),
            "slope_deg": list(rng.uniform(-2.0, 2.0, 2))}


def trial(spec):
    """One walk. spec: gait, scenario, gains (balance.py overrides), push (t, N toward +y, s) or None, seed."""
    import mujoco
    import walk_jx0 as W
    from jx0bot.balance import Balance
    xml, g, res, st = _setup(spec["gait"], spec.get("gait_overrides"))
    sc, rng = spec["scenario"], np.random.default_rng(spec.get("seed", 0))
    m = mujoco.MjModel.from_xml_string(xml)
    oid = lambda kind, n: mujoco.mj_name2id(m, kind, n)  # noqa: E731
    torso = oid(mujoco.mjtObj.mjOBJ_BODY, "torso")
    m.body_mass[torso] *= sc["mass"]
    m.body_ipos[torso][:2] += np.array(sc["com_mm"]) * 1e-3
    for gname in ("l_foot_geom", "r_foot_geom", "floor"):
        m.geom_friction[oid(mujoco.mjtObj.mjOBJ_GEOM, gname)][0] = sc["mu"]
    ax, ay = (math.radians(v) for v in sc["slope_deg"])
    m.opt.gravity[:] = 9.81 * np.array([math.sin(ay) * math.cos(ax), -math.sin(ax), -math.cos(ax) * math.cos(ay)])
    d = mujoco.MjData(m)

    t_ref, q_ref, contact = res["t"], res["qpos"], res["plan"].contact
    names = [f"{s}_{j}" for s in "lr" for j in W.LEG_JOINTS] + [f"{s}_{j}" for s in "lr" for j in W.ARM_JOINTS] + ["neck_yaw"]
    adr = {n: (m.jnt_qposadr[oid(mujoco.mjtObj.mjOBJ_JOINT, n)], m.jnt_dofadr[oid(mujoco.mjtObj.mjOBJ_JOINT, n)]) for n in names}
    act = {n: oid(mujoco.mjtObj.mjOBJ_ACTUATOR, n) for n in names}
    servo = W.ServoModel(st["stall_torque_nm"] * sc["stall"], st["no_load_speed_rad_s"] * sc["stall"], 60.0 * sc["kp"], 0.6 * sc["kd"])
    d.qpos[:] = q_ref[0]
    for n, v in W.arm_goals(q_ref[0], q_ref[0], adr).items():
        d.qpos[adr[n][0]] = v
    d.qpos[2] += 0.002
    mujoco.mj_forward(m, d)
    dt, T = m.opt.timestep, float(t_ref[-1])
    frame = 1.0 / spec.get("bus_hz", W.BUS_HZ)
    period = int(round(frame / dt))
    goal = {n: float(d.qpos[adr[n][0]]) for n in names}
    lag = int(round(sc["latency"] * 0.02 / frame))                 # latency is given in 20 ms units
    pipe = deque([dict(goal)] * (lag + 1), maxlen=lag + 1)
    bal = Balance(spec.get("gains"), dt=frame)
    bl = math.radians(sc["backlash_deg"]) / 2
    bias = [math.radians(v) for v in sc["bias_deg"]]
    fell, max_tilt, hist = False, 0.0, []
    for k in range(int(T / dt)):
        t = k * dt
        i = min(int(round(t / g.dt)), len(t_ref) - 1)
        roll, pitch, yaw = W.rpy(d.qpos[3:7])
        if k % period == 0:
            n_deg = math.radians(sc["imu_deg"])
            r_m, p_m = roll + bias[0] + rng.normal(0, n_deg), pitch + bias[1] + rng.normal(0, n_deg)
            wx, wy = d.qvel[3] + rng.normal(0, sc["gyro"]), d.qvel[4] + rng.normal(0, sc["gyro"])
            corr = bal.update(r_m, p_m, wx, wy, contact[min(i, len(contact) - 1)])
            arms = W.arm_goals(q_ref[i], q_ref[0], adr)
            new = {n: float((q_ref[i, adr[n][0]] if n.split("_", 1)[1] in W.LEG_JOINTS else arms.get(n, 0.0)) + corr.get(n, 0.0))
                   for n in names}
            pipe.append(new)
            goal = pipe[0]                                  # what the servos act on, `latency` frames late
        for n in names:
            qa, da = adr[n]
            err = goal[n] - d.qpos[qa]
            err = 0.0 if abs(err) < bl else err - math.copysign(bl, err)       # gear backlash
            d.ctrl[act[n]] = servo.torque(d.qpos[qa] + err, d.qpos[qa], d.qvel[da])
        if spec.get("push") is not None:
            tp, f, dur = spec["push"]
            d.xfrc_applied[torso, 1] = f if tp <= t < tp + dur else 0.0
        mujoco.mj_step(m, d)
        if k % 10 == 0:
            tilt = math.degrees(math.hypot(roll, pitch))
            max_tilt = max(max_tilt, tilt)
            hist.append((*d.qpos[:2], *q_ref[i, :2], yaw, W.rpy(q_ref[i, 3:7])[2], roll, pitch, t))
            if d.qpos[2] < 0.13 or tilt > 30:
                fell = True
                break
    h = np.array(hist)
    dist_plan = float(np.linalg.norm(q_ref[-1, :2] - q_ref[0, :2]))
    pos_err = float(np.linalg.norm(h[-1, 0:2] - h[-1, 2:4]))
    head_err = math.degrees((h[-1, 4] - h[-1, 5] + math.pi) % (2 * math.pi) - math.pi)
    ok = (not fell) and pos_err <= 0.05 + 0.10 * dist_plan and abs(head_err) < 10.0
    return {"gait": spec["gait"], "fell": fell, "pass": bool(ok), "pos_err_m": round(pos_err, 3),
            "heading_err_deg": round(head_err, 1), "max_tilt_deg": round(max_tilt, 1), "push": spec.get("push"),
            "end_roll_deg": round(math.degrees(h[-1, 6]), 1), "end_pitch_deg": round(math.degrees(h[-1, 7]), 1),
            "end_t_s": round(float(h[-1, 8]), 2)}


class PerturbedWorld:
    """The robot program's I/O (send / tick / sleep / attitude / read_pose) on a randomly wrong physical robot: the
    same perturbations as trial(), but driven by jx0bot.robot.Robot itself, so whole missions can be tested."""

    def __init__(self, sc, seed):
        import mujoco
        import walk_jx0 as W
        from jx1calc.design import Design
        self.mj, self.W, self.sc, self.rng = mujoco, W, sc, np.random.default_rng(seed)
        design = Design(W.DESIGN)
        m = mujoco.MjModel.from_xml_string(W.build(design))
        oid = lambda kind, n: mujoco.mj_name2id(m, kind, n)  # noqa: E731
        torso = oid(mujoco.mjtObj.mjOBJ_BODY, "torso")
        m.body_mass[torso] *= sc["mass"]
        m.body_ipos[torso][:2] += np.array(sc["com_mm"]) * 1e-3
        for gname in ("l_foot_geom", "r_foot_geom", "floor"):
            m.geom_friction[oid(mujoco.mjtObj.mjOBJ_GEOM, gname)][0] = sc["mu"]
        ax, ay = (math.radians(v) for v in sc["slope_deg"])
        m.opt.gravity[:] = 9.81 * np.array([math.sin(ay) * math.cos(ax), -math.sin(ax), -math.cos(ax) * math.cos(ay)])
        self.m, self.d = m, mujoco.MjData(m)
        st = design.act_classes["ST"]
        self.servo = W.ServoModel(st["stall_torque_nm"] * sc["stall"], st["no_load_speed_rad_s"] * sc["stall"], 60.0 * sc["kp"], 0.6 * sc["kd"])
        from jx0bot.robot import ARM_JOINTS, LEG_JOINTS
        self.names = LEG_JOINTS + ARM_JOINTS
        self.adr = {n: (m.jnt_qposadr[oid(mujoco.mjtObj.mjOBJ_JOINT, n)], m.jnt_dofadr[oid(mujoco.mjtObj.mjOBJ_JOINT, n)]) for n in self.names}
        self.act = {n: oid(mujoco.mjtObj.mjOBJ_ACTUATOR, n) for n in self.names}
        self.goal = {n: 0.0 for n in self.names}
        self.lag = int(round(sc["latency"] * 0.02 / (1.0 / W.BUS_HZ)))
        self.pipe = deque(maxlen=self.lag + 1)
        self.bl = math.radians(sc["backlash_deg"]) / 2
        self.bias = [math.radians(v) for v in sc["bias_deg"]]
        self.fell, self.max_tilt = False, 0.0

    def settle(self, q0):
        mj, d = self.mj, self.d
        for n, v in q0.items():
            d.qpos[self.adr[n][0]] = v
            self.goal[n] = v
        mj.mj_forward(self.m, d)
        sole = min(d.site_xpos[mj.mj_name2id(self.m, mj.mjtObj.mjOBJ_SITE, s)][2] for s in ("l_sole", "r_sole"))
        d.qpos[2] -= sole - 0.001
        mj.mj_forward(self.m, d)
        self.pipe.extend([dict(self.goal)] * (self.lag + 1))

    def send(self, q):
        self.pipe.append({**self.goal, **q})
        self.goal_now = self.pipe[0]

    def read_pose(self):
        return {n: float(self.d.qpos[qa]) for n, (qa, _) in self.adr.items()}

    def attitude(self):
        r, p, y = self.W.rpy(self.d.qpos[3:7])
        n = math.radians(self.sc["imu_deg"])
        g = self.sc["gyro"]
        return (r + self.bias[0] + self.rng.normal(0, n), p + self.bias[1] + self.rng.normal(0, n), y,
                (self.d.qvel[3] + self.rng.normal(0, g), self.d.qvel[4] + self.rng.normal(0, g), self.d.qvel[5]))

    def tick(self, dt):
        self.advance(dt)

    def sleep(self, seconds):
        self.advance(seconds)

    def advance(self, seconds):
        goal = getattr(self, "goal_now", self.goal)
        for _ in range(int(round(seconds / self.m.opt.timestep))):
            for n in self.names:
                qa, da = self.adr[n]
                err = goal[n] - self.d.qpos[qa]
                err = 0.0 if abs(err) < self.bl else err - math.copysign(self.bl, err)
                self.d.ctrl[self.act[n]] = self.servo.torque(self.d.qpos[qa] + err, self.d.qpos[qa], self.d.qvel[da])
            self.mj.mj_step(self.m, self.d)
            r, p, _ = self.W.rpy(self.d.qpos[3:7])
            self.max_tilt = max(self.max_tilt, math.degrees(max(abs(r), abs(p))))
            if self.d.qpos[2] < 0.13 or self.max_tilt > 30:
                self.fell = True
                raise RuntimeError("fell")


MISSION = [("walk", {"steps": 8, "direction": "forward"}), ("turn", {"degrees": 40}), ("walk", {"steps": 4, "direction": "forward"}),
           ("walk", {"steps": 2, "direction": "left"}), ("walk", {"steps": 2, "direction": "backward"}),
           ("wave", {"arm": "right"}), ("nod", {"kind": "yes"}), ("look", {"direction": "left"})]


def mission(spec):
    """The robot program (jx0bot.robot.Robot) runs MISSION on a perturbed robot. Pass = it never falls."""
    from jx0bot.robot import REST_ARMS, Robot, load_config
    world = PerturbedWorld(spec["scenario"], spec.get("seed", 0))
    robot = Robot(world, load_config())
    world.settle({**robot.stand_pose, **REST_ARMS})
    done = []
    try:
        robot.stand(1.0)
        for name, args in MISSION:
            robot.act(name, args)
            done.append(name)
    except RuntimeError:
        pass
    return {"pass": not world.fell and len(done) == len(MISSION), "completed": done, "max_tilt_deg": round(world.max_tilt, 1),
            "distance_m": round(float(np.hypot(*world.d.qpos[:2])), 2), "latency_ms": spec["scenario"]["latency"] * 20}


def model_error_specs(n, seed, gains=None, latencies=(0, 1, 2)):
    rng = np.random.default_rng(seed)
    return [{"gait": MC_GAITS[k % len(MC_GAITS)], "scenario": sample(rng, latencies), "gains": gains, "seed": seed * 1000 + k}
            for k in range(n)]


def push_specs(forces, gains=None, timings=24):
    ts = np.linspace(3.0, 4.8, timings)
    return [{"gait": "forward", "scenario": nominal(), "gains": gains, "push": (float(t), d * f, 0.12)}
            for f in forces for d in (1, -1) for t in ts]


def run_all(specs, pool):
    return pool.map(trial, specs, chunksize=1)


def summarise(results, key=None):
    n = len(results)
    ok = sum(r["pass"] for r in results)
    return {"trials": n, "passed": ok, "rate": round(ok / max(1, n), 3)}


def evaluate(gains, pool, n_mc=140, forces=(2.0, 4.0, 6.0)):
    """Held-out scenarios (seed 7 / 8, not used for tuning). Latency 0-20 ms is the realistic set (the robot's loop:
    IMU filter ~5 ms + bus 1.3 ms + compute < 1 ms); 40 ms is a stress test."""
    out = {"gains": gains}
    for label, seed, lats in (("model_errors_latency_0_20ms", 7, (0, 1)), ("model_errors_latency_40ms_stress", 8, (2,))):
        mc = run_all(model_error_specs(n_mc, seed, gains, lats), pool)
        out[label] = {**summarise(mc), "per_gait": {g: summarise([r for r in mc if r["gait"] == g]) for g in MC_GAITS},
                      "failures": [r for r in mc if not r["pass"]][:8]}
    pu = run_all(push_specs(forces, gains), pool)
    out["pushes_mid_walk"] = {f"{f * 0.12:.2f} N.s": summarise([r for r in pu if abs(abs(r["push"][1]) - f) < 1e-9]) for f in forces}
    return out


def tune(pool, n_cand=48, seed=11):
    """Random search around the current gains; score = pushes survived (0.72 N.s) + model-error trials passed."""
    rng = np.random.default_rng(seed)
    from jx0bot.balance import GAINS
    cands = [dict(GAINS)]
    for _ in range(n_cand):
        cands.append({**GAINS, "ka": rng.uniform(0.3, 1.0), "da": rng.uniform(0.0, 0.15), "kh": rng.uniform(0.0, 0.6),
                      "sr": rng.uniform(-1.5, 1.5), "srd": rng.uniform(-0.3, 0.3),
                      "sp": rng.uniform(-1.0, 1.0), "spd": rng.uniform(-0.2, 0.2), "decay_s": rng.uniform(0.2, 0.8)})
    specs, owner = [], []
    for ci, gns in enumerate(cands):
        for s in push_specs((6.0,), gns, timings=12) + model_error_specs(14, 3, gns):
            specs.append(s)
            owner.append(ci)
    res = run_all(specs, pool)
    score = np.zeros(len(cands))
    for ci, r in zip(owner, res):
        score[ci] += r["pass"]
    order = np.argsort(-score)
    board = [{"rank": int(k + 1), "score": int(score[ci]), "of": len(specs) // len(cands), "gains": cands[ci]} for k, ci in enumerate(order[:5])]
    return cands[order[0]], board


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    t0 = time.time()
    sys.path.insert(0, str(ROOT / "jx0" / "software"))
    out = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    with Pool(os.cpu_count()) as pool:
        if mode == "baseline":
            out["baseline"] = evaluate(None, pool)
            print(json.dumps({k: v for k, v in out["baseline"].items() if k != "gains"}, indent=1)[:3000])
        elif mode == "tune":
            best, board = tune(pool)
            out["tuning"] = {"method": "random search, 49 candidates x (24 pushes at 0.72 N.s + 14 model-error walks)", "top": board}
            print("leaderboard:", json.dumps(board, indent=1)[:2500])
            out["tuned"] = evaluate(best, pool)
            print(json.dumps({k: v for k, v in out["tuned"].items() if k != "gains"}, indent=1)[:3000])
        elif mode == "mission":                # the whole robot program, realistic latency, held-out scenarios
            rng = np.random.default_rng(99)
            specs = [{"scenario": sample(rng, (0, 1)), "seed": k} for k in range(24)]
            res = pool.map(mission, specs, chunksize=1)
            out["mission"] = {"steps": [f"{n} {a}" for n, a in MISSION], **summarise(res), "results": res}
            print(json.dumps({k: v for k, v in out["mission"].items() if k != "results"}))
            for r in res:
                if not r["pass"]:
                    print("  failed after", r["completed"], "tilt", r["max_tilt_deg"], "latency", r["latency_ms"], "ms")
        elif mode == "final":                  # the gains now in balance.py, gaits and rate as in walk_jx0.py
            out = {"final": evaluate(None, pool), **({"mission": out["mission"]} if "mission" in out else {})}
            for k, v in out["final"].items():
                if k != "gains":
                    print(k, json.dumps({kk: vv for kk, vv in v.items() if kk != "failures"}) if isinstance(v, dict) else v)
    out["generated_by"] = "jx0/verify/robustness.py"
    out["seconds_" + mode] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"{mode}: {time.time() - t0:.0f} s -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
