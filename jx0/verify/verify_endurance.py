"""60 s endurance of the robot program itself (jx0bot.robot.Robot with the verified gaits and balance controller):

    python jx0/verify/verify_endurance.py      -> jx0/results/verify_endurance.json

Each run drives the robot program for 60 s or more through walking at its speeds (forward 0.05 m/s, the 4-step
forward and backward gaits, side steps), turns both ways, waves and looks around, with a horizontal push on the torso
every 7 s (0.48 N s, front / left / back / right in turn). It runs on 12 randomly wrong robots (robustness.py's
model errors: servo stiffness 0.6-1.4x, damping, torque and speed, 0-40 ms latency, backlash, IMU noise and bias,
upper-body mass and centre of mass, friction, floor slope), at 1 kHz with the STS3215 torque-speed model.
Pass: no run falls; every servo's mean |torque| under its rated 0.98 N m.
"""
from __future__ import annotations

import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import robustness as R  # noqa: E402

OUT = R.ROOT / "jx0" / "results" / "verify_endurance.json"
SECONDS = 60.0
PUSH_NS, PUSH_S, PUSH_EVERY = 0.48, 0.1, 7.0
PROGRAM = [("walk", {"steps": 6, "direction": "forward"}), ("turn", {"degrees": 40}), ("walk", {"steps": 4, "direction": "left"}),
           ("walk", {"steps": 4, "direction": "backward"}), ("turn", {"degrees": -40}), ("walk", {"steps": 4, "direction": "right"}),
           ("wave", {"arm": "left"}), ("walk", {"steps": 8, "direction": "forward"}), ("look", {"direction": "right"}),
           ("turn", {"degrees": -30}), ("wave", {"arm": "right"}), ("walk", {"steps": 4, "direction": "forward"})]
DIRS = [(-1.0, 0.0), (0.0, -1.0), (1.0, 0.0), (0.0, 1.0)]          # push from the front, left, back, right


class PushedWorld(R.PerturbedWorld):
    """robustness.PerturbedWorld + the endurance pushes and a torque log."""

    def __init__(self, sc, seed):
        super().__init__(sc, seed)
        mj = self.mj
        self.torso = mj.mj_name2id(self.m, mj.mjtObj.mjOBJ_BODY, "torso")
        self.next_push, self.k_push, self.push_until, self.f = PUSH_EVERY, 0, -1.0, np.zeros(2)
        self.abs_tau = {n: 0.0 for n in self.names}
        self.n = 0
        self.pushes = 0

    def advance(self, seconds):
        mj, d = self.mj, self.d
        goal = getattr(self, "goal_now", self.goal)
        for _ in range(int(round(seconds / self.m.opt.timestep))):
            if d.time >= self.next_push:
                h = self.W.rpy(d.qpos[3:7])[2]
                dx, dy = DIRS[self.k_push % 4]
                self.f = PUSH_NS / PUSH_S * np.array([math.cos(h) * dx - math.sin(h) * dy, math.sin(h) * dx + math.cos(h) * dy])
                self.push_until, self.next_push, self.k_push = d.time + PUSH_S, self.next_push + PUSH_EVERY, self.k_push + 1
                self.pushes += 1
            d.xfrc_applied[self.torso, :] = 0.0
            if d.time < self.push_until:
                d.xfrc_applied[self.torso, :2] = self.f
            for n in self.names:
                qa, da = self.adr[n]
                err = goal[n] - d.qpos[qa]
                err = 0.0 if abs(err) < self.bl else err - math.copysign(self.bl, err)
                tau = self.servo.torque(d.qpos[qa] + err, d.qpos[qa], d.qvel[da])
                d.ctrl[self.act[n]] = tau
                self.abs_tau[n] += abs(tau)
            self.n += 1
            mj.mj_step(self.m, d)
            r, p, _ = self.W.rpy(d.qpos[3:7])
            self.max_tilt = max(self.max_tilt, math.degrees(max(abs(r), abs(p))))
            if d.qpos[2] < 0.13 or self.max_tilt > 30:
                self.fell = True
                raise RuntimeError("fell")


def endurance(spec):
    from jx0bot.robot import REST_ARMS, Robot, load_config
    world = PushedWorld(spec["scenario"], spec["seed"])
    robot = Robot(world, load_config())
    world.settle({**robot.stand_pose, **REST_ARMS})
    t0, actions = time.perf_counter(), 0
    try:
        robot.stand(1.0)
        while world.d.time < SECONDS:
            for name, args in PROGRAM:
                robot.act(name, args)
                actions += 1
                if world.d.time >= SECONDS:
                    break
    except RuntimeError:
        pass
    mean = {n: world.abs_tau[n] / max(world.n, 1) for n in world.names}
    worst = max(mean, key=mean.get)
    return {"seed": spec["seed"], "fell": world.fell, "seconds": round(world.d.time, 1), "actions": actions,
            "pushes": world.pushes, "max_tilt_deg": round(world.max_tilt, 1),
            "distance_from_start_m": round(float(np.hypot(*world.d.qpos[:2])), 2),
            "worst_mean_torque_nm": round(mean[worst], 3), "worst_joint": worst,
            "latency_ms": spec["scenario"]["latency"] * 20, "stiffness_x": round(spec["scenario"]["kp"], 2),
            "real_time_factor": round(world.d.time / (time.perf_counter() - t0), 2)}


def main():
    t0 = time.time()
    rng = np.random.default_rng(60)
    specs = [{"scenario": R.nominal(), "seed": 0}] + [{"scenario": R.sample(rng), "seed": k} for k in range(1, 12)]
    with Pool(min(12, len(specs))) as pool:
        res = pool.map(endurance, specs, chunksize=1)
    sys.path.insert(0, str(R.ROOT / "calculations"))
    from jx1calc.design import Design
    rated = Design(R.ROOT / "jx0" / "design_point.yaml").act_classes["ST"]["rated_torque_nm"]
    ok = all(not r["fell"] and r["seconds"] >= SECONDS for r in res) and max(r["worst_mean_torque_nm"] for r in res) < rated
    for r in res:
        state = f"FELL at {r['seconds']} s" if r["fell"] else f"{r['seconds']} s"
        print(f"  run {r['seed']:2d}: {state}, "
              f"{r['actions']} actions, {r['pushes']} pushes, tilt {r['max_tilt_deg']} deg, latency {r['latency_ms']} ms, "
              f"stiffness x{r['stiffness_x']}, worst mean torque {r['worst_mean_torque_nm']} N m ({r['worst_joint']})", flush=True)
    out = {"seconds": SECONDS, "push_ns": PUSH_NS, "push_every_s": PUSH_EVERY, "program": [f"{n} {a}" for n, a in PROGRAM],
           "runs": res, "stayed_up": sum(not r["fell"] for r in res), "of": len(res), "rated_torque_nm": rated,
           "pass": ok, "wall_s": round(time.time() - t0, 1)}
    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"endurance: {'PASS' if ok else 'FAIL'} - {out['stayed_up']}/{out['of']} runs stayed up for {SECONDS:.0f} s "
          f"({out['wall_s']} s) -> {OUT.relative_to(R.ROOT)}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
