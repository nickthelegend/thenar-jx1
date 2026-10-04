"""JX0 electrical and timing checks.

1. Servo loads and current while walking and gesturing, from the simulation's actuator torques and joint speeds
   (the same servo model the gaits are verified with), per joint: peak / RMS torque vs the STS3215's 2.94 N·m stall and
   0.98 N·m rated torque, and current from the published electrical data (Waveshare ST3215 12 V: kt 11 kg·cm/A,
   no-load 0.2 A, stall 2.7 A).
2. Battery: total current at 12 V (17 servos + Pi 4 + audio), peak vs the 3S 35C pack, the 10 A switch and the UBEC;
   walking time from a 2200 mAh pack; compared with the reference robot's bench supply (0.6-1.5 A at 12.6 V).
3. Real-time budget of one 50 Hz robot frame: the bus packet time at 1 Mbit/s and the Python cost of the balance
   controller + command mapping, measured here and scaled for a Raspberry Pi 4.

    python jx0/verify/verify_power.py     -> jx0/results/verify_power.json
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "jx0" / "sim"))
sys.path.insert(0, str(ROOT / "jx0" / "software"))
os.environ.setdefault("JX0_STL_DIR", str(ROOT / "nonexistent"))
OUT = ROOT / "jx0" / "results" / "verify_power.json"

KT = 11 * 0.0980665          # N·m per A (11 kg·cm/A)
I0, I_STALL = 0.20, 2.7      # A (no-load current is at full speed; a servo holding still draws only its electronics)
V_SERVO = 12.0
R_MOTOR = V_SERVO / I_STALL  # ohm: the motor's winding resistance from the stall current
I_IDLE = 0.02                # A per servo, electronics (ESTIMATED; checked against the reference robot's standing current)
STALL, RATED = 2.94, 0.98    # N·m
V_BATT = 11.1                # V nominal 3S
PI_W, AUDIO_W = 4.0, 1.0     # Raspberry Pi 4 under load (ESTIMATED), mic + amplifier idle/average (ESTIMATED)
PACK_AH, PACK_C = 2.2, 35


def servo_current(tau, w):
    """Supply current of one PWM-driven servo: the motor needs i = tau / kt; the supply delivers the copper loss i²R plus
    the mechanical power tau·w (none back when braking), plus the electronics."""
    i_m = abs(tau) / KT
    p = i_m * i_m * R_MOTOR + max(0.0, tau * w)
    return I_IDLE + p / V_SERVO


def stand_current(seconds=2.0):
    """Servo supply current with the robot standing still in the walking stance (compare: the reference robot's bench
    supply read 0.58 A at 12.6 V standing)."""
    import mujoco
    import walk_jx0 as W
    from jx1calc.design import Design
    design = Design(W.DESIGN)
    m = mujoco.MjModel.from_xml_string(W.build(design))
    d = mujoco.MjData(m)
    g, res = W.plan(m, design, "forward_2")
    q0 = res["qpos"][0]
    st = design.act_classes["ST"]
    names = [f"{s}_{j}" for s in "lr" for j in W.LEG_JOINTS] + [f"{s}_{j}" for s in "lr" for j in W.ARM_JOINTS] + ["neck_yaw"]
    oid = lambda k, n: mujoco.mj_name2id(m, k, n)  # noqa: E731
    adr = {n: (m.jnt_qposadr[oid(mujoco.mjtObj.mjOBJ_JOINT, n)], m.jnt_dofadr[oid(mujoco.mjtObj.mjOBJ_JOINT, n)]) for n in names}
    act = {n: oid(mujoco.mjtObj.mjOBJ_ACTUATOR, n) for n in names}
    servo = W.ServoModel(st["stall_torque_nm"], st["no_load_speed_rad_s"], 60.0, 0.6)
    d.qpos[:] = q0
    for n, v in W.arm_goals(q0, q0, adr).items():
        d.qpos[adr[n][0]] = v
    mujoco.mj_forward(m, d)
    goal = {n: float(d.qpos[adr[n][0]]) for n in names}
    cur = []
    for k in range(int(seconds / m.opt.timestep)):
        total = 0.0
        for n in names:
            qa, da = adr[n]
            u = servo.torque(goal[n], d.qpos[qa], d.qvel[da])
            d.ctrl[act[n]] = u
            total += servo_current(u, d.qvel[da])
        mujoco.mj_step(m, d)
        if k > seconds / m.opt.timestep / 2:
            cur.append(total)
    return float(np.mean(cur))


def walk_loads(gait="forward"):
    import mujoco
    import walk_jx0 as W
    from jx1calc.design import Design
    from jx0bot.balance import Balance
    design = Design(W.DESIGN)
    m = mujoco.MjModel.from_xml_string(W.build(design))
    d = mujoco.MjData(m)
    g, res = W.plan(m, design, gait)
    t_ref, q_ref, contact = res["t"], res["qpos"], res["plan"].contact
    st = design.act_classes["ST"]
    names = [f"{s}_{j}" for s in "lr" for j in W.LEG_JOINTS] + [f"{s}_{j}" for s in "lr" for j in W.ARM_JOINTS] + ["neck_yaw"]
    oid = lambda k, n: mujoco.mj_name2id(m, k, n)  # noqa: E731
    adr = {n: (m.jnt_qposadr[oid(mujoco.mjtObj.mjOBJ_JOINT, n)], m.jnt_dofadr[oid(mujoco.mjtObj.mjOBJ_JOINT, n)]) for n in names}
    act = {n: oid(mujoco.mjtObj.mjOBJ_ACTUATOR, n) for n in names}
    servo = W.ServoModel(st["stall_torque_nm"], st["no_load_speed_rad_s"], 60.0, 0.6)
    d.qpos[:] = q_ref[0]
    for n, v in W.arm_goals(q_ref[0], q_ref[0], adr).items():
        d.qpos[adr[n][0]] = v
    d.qpos[2] += 0.002
    mujoco.mj_forward(m, d)
    bal = Balance(dt=1.0 / W.BUS_HZ)
    goal = {n: float(d.qpos[adr[n][0]]) for n in names}
    tau_log, cur_log = {n: [] for n in names}, []
    for k in range(int(float(t_ref[-1]) / m.opt.timestep)):
        t = k * m.opt.timestep
        i = min(int(round(t / g.dt)), len(t_ref) - 1)
        roll, pitch, _ = W.rpy(d.qpos[3:7])
        if k % int(round(1.0 / W.BUS_HZ / m.opt.timestep)) == 0:
            corr = bal.update(roll, pitch, d.qvel[3], d.qvel[4], contact[min(i, len(contact) - 1)])
            arms = W.arm_goals(q_ref[i], q_ref[0], adr)
            goal = {n: float((q_ref[i, adr[n][0]] if n.split("_", 1)[1] in W.LEG_JOINTS else arms.get(n, 0.0)) + corr.get(n, 0.0))
                    for n in names}
        total = 0.0
        for n in names:
            qa, da = adr[n]
            u = servo.torque(goal[n], d.qpos[qa], d.qvel[da])
            d.ctrl[act[n]] = u
            tau_log[n].append(u)
            total += servo_current(u, d.qvel[da])
        cur_log.append(total)
        mujoco.mj_step(m, d)
    return {n: np.array(v) for n, v in tau_log.items()}, np.array(cur_log), m.opt.timestep


def gesture_loads():
    """Holding torque of the arm and neck servos in the worst static poses (arm straight out in front, blade
    horizontal), from the simulation model's masses: gravity torque about each joint."""
    import mujoco
    import walk_jx0 as W
    from jx1calc.design import Design
    m = mujoco.MjModel.from_xml_string(W.build(Design(W.DESIGN)))
    d = mujoco.MjData(m)
    out = {}
    for s in "lr":
        jid = {j: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, f"{s}_{j}") for j in ("shoulder_pitch", "elbow")}
        d.qpos[:] = 0
        d.qpos[3] = 1
        d.qpos[m.jnt_qposadr[jid["shoulder_pitch"]]] = -math.pi / 2          # arm horizontal in front
        mujoco.mj_forward(m, d)
        mujoco.mj_rne(m, d, 0, d.qfrc_bias)                                    # gravity-only generalized forces
        for j, i in jid.items():
            out[f"{s}_{j}"] = round(abs(float(d.qfrc_bias[m.jnt_dofadr[i]])), 3)
    return out


def frame_budget():
    """Python cost of one robot frame (balance + angle->ticks + packet build) on this PC; a Pi 4 core is roughly 5x
    slower for this kind of code (ESTIMATED)."""
    from jx0bot import servo_bus as sb
    from jx0bot.balance import Balance
    from jx0bot.robot import load_config
    cfg = load_config()
    servos = {**cfg["leg_servos"], **cfg["arm_servos"]}
    gait = json.loads((ROOT / "jx0" / "software" / "jx0bot" / "gaits" / "forward.json").read_text(encoding="utf-8"))
    bal = Balance(dt=0.01)
    n = 3000
    t0 = time.perf_counter()
    for k in range(n):
        frame, stance = gait["q"][k % len(gait["q"])], gait["stance"][k % len(gait["q"])]
        q = dict(zip(gait["joints"], frame))
        for kk, v in bal.update(0.01, -0.01, 0.02, 0.01, stance).items():
            q[kk] += v
        ticks = {}
        for name, s in servos.items():
            if name in q:
                lo, hi = (math.radians(v) for v in s["limits_deg"])
                a = min(max(q[name], lo), hi)
                ticks[s["id"]] = int(round(s["zero_ticks"] + s["direction"] * a * 4096 / (2 * math.pi)))
        sb.packet(sb.BROADCAST, sb.SYNC_WRITE, bytes([sb.ADDR_GOAL_POSITION, 6]) +
                  b"".join(bytes([i]) + sb.u16(p) + sb.u16(0) + sb.u16(0) for i, p in ticks.items()))
    pc_ms = (time.perf_counter() - t0) / n * 1000
    bytes_frame = 2 + 3 + 2 + 7 * len(servos) + 1
    return {"python_ms_per_frame_pc": round(pc_ms, 3), "python_ms_per_frame_pi4_est": round(pc_ms * 5, 2),
            "bus_bytes_per_frame": bytes_frame, "bus_ms_per_frame": round(bytes_frame * 10 / 1e6 * 1000, 2),
            "imu_read_ms_est": 0.4, "frame_ms": 1000.0 / cfg["bus"]["rate_hz"]}


def main():
    t0 = time.time()
    result = {}
    taus, cur, dt = walk_loads("forward")
    joints = {}
    for n, t in taus.items():
        joints[n] = {"peak_nm": round(float(np.abs(t).max()), 3), "rms_nm": round(float(np.sqrt(np.mean(t ** 2))), 3),
                     "peak_of_stall": round(float(np.abs(t).max() / STALL), 2), "rms_of_rated": round(float(np.sqrt(np.mean(t ** 2)) / RATED), 2)}
    servo_avg = float(cur.mean())
    # the current limit of the servos' own electronics smooths the 1 ms spikes: report the 20 ms (one frame) peak
    win = int(0.02 / dt)
    cur_20ms = np.convolve(cur, np.ones(win) / win, mode="valid")
    total_avg_a = servo_avg + (PI_W + AUDIO_W) / V_BATT
    total_peak_a = float(cur_20ms.max()) + (PI_W + AUDIO_W) / V_BATT
    result["walking_forward"] = {"joints": joints, "servo_current_avg_a": round(servo_avg, 2),
                                 "servo_current_peak_20ms_a": round(float(cur_20ms.max()), 2),
                                 "total_avg_a": round(total_avg_a, 2), "total_peak_a": round(total_peak_a, 2),
                                 "total_avg_w": round(total_avg_a * V_BATT, 1)}
    standing = stand_current()
    result["standing"] = {"servo_current_a": round(standing, 2), "reference_robot_standing_a": 0.58,
                          "note": "reference robot's bench supply at 12.6 V, standing (17 STS3215, no Pi)"}
    result["battery"] = {"pack": f"3S {PACK_AH * 1000:.0f} mAh {PACK_C}C", "max_continuous_a": PACK_AH * PACK_C,
                         "walking_minutes_80pct": round(PACK_AH * 0.8 / total_avg_a * 60),
                         "standing_minutes_80pct": round(PACK_AH * 0.8 / (standing + (PI_W + AUDIO_W) / V_BATT) * 60),
                         "switch_rating_a": 10, "switch_ok": total_peak_a < 10, "pack_ok": total_peak_a < PACK_AH * PACK_C,
                         "reference_robot_bench_supply_a": [0.6, 1.5],
                         "note": "the reference robot (17 STS3215, no Pi) drew 0.6-1.5 A at 12.6 V while walking"}
    result["ubec_5v"] = {"pi4_max_a": 3.0, "audio_a": 0.4, "ubec_a": 5.0, "ok": 3.4 < 5.0}
    result["arm_neck_holding"] = {"arm_straight_out_nm": gesture_loads(), "stall_nm": STALL, "rated_nm": RATED}
    result["realtime"] = frame_budget()
    rt = result["realtime"]
    rt["frame_used_ms_pi4_est"] = round(rt["python_ms_per_frame_pi4_est"] + rt["bus_ms_per_frame"] + rt["imu_read_ms_est"], 2)
    rt["ok"] = rt["frame_used_ms_pi4_est"] < 0.5 * rt["frame_ms"]
    worst = max(joints.items(), key=lambda kv: kv[1]["peak_of_stall"])
    result["pass"] = bool(result["battery"]["switch_ok"] and result["battery"]["pack_ok"] and result["ubec_5v"]["ok"] and rt["ok"]
                          and worst[1]["peak_of_stall"] < 1.0 and all(v["rms_of_rated"] < 1.0 for v in joints.values()))
    result["seconds"] = round(time.time() - t0, 1)
    OUT.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "walking_forward"}, indent=1))
    w = result["walking_forward"]
    print(f"walking: servos avg {w['servo_current_avg_a']} A, 20 ms peak {w['servo_current_peak_20ms_a']} A; total avg {w['total_avg_a']} A "
          f"({w['total_avg_w']} W), peak {w['total_peak_a']} A; worst joint {worst[0]} peak {worst[1]['peak_of_stall']:.0%} of stall")
    print("power check:", "PASS" if result["pass"] else "FAIL")


if __name__ == "__main__":
    main()
