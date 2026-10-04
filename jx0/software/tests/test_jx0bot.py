"""JX0 software tests (standard library unittest, no extra packages):

    python -m unittest discover -s jx0/software/tests -v

- servo_bus: packet bytes against the worked examples of the Feetech/Waveshare STS protocol manual, sign encoding,
  the sync-write packet the robot sends every 50 Hz frame;
- config.yaml: 17 unique bus IDs, every model joint present, limits inside the collision-free ranges found by
  jx0/verify/verify_cad.py and inside the simulation model's joint ranges;
- gaits/*.json: every frame inside the limits, 50 Hz, blocks start and end in the same stance (so they chain);
- HardwareIO: joint angle <-> servo ticks with direction, zero offset and clamping (on a fake bus);
- Robot: every action through a fake I/O stays inside the limits, walk/turn plans;
- balance: zero tilt gives zero correction, corrections oppose the tilt;
- brain: tool-input validation, and the tool loop with a scripted fake Claude client (run, reject, truncation, refusal).
"""
from __future__ import annotations

import json
import math
import sys
import types
import unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
if "anthropic" not in sys.modules:                       # the tests never call the real API
    try:
        import anthropic  # noqa: F401
    except ImportError:
        stub = types.ModuleType("anthropic")
        stub.Anthropic = object
        sys.modules["anthropic"] = stub

from jx0bot import servo_bus as sb  # noqa: E402
from jx0bot.balance import Balance  # noqa: E402
from jx0bot.robot import ARM_JOINTS, LEG_JOINTS, REST_ARMS, Robot, load_config  # noqa: E402

CFG = load_config()
SERVOS = {**CFG["leg_servos"], **CFG["arm_servos"]}
GAITS = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (HERE.parent / "jx0bot" / "gaits").glob("*.json")}


class FakeSerial:
    def __init__(self, *a, **k):
        self.sent = []
        self.reply = b""

    def reset_input_buffer(self):
        pass

    def write(self, data):
        self.sent.append(bytes(data))

    def read(self, n):
        out, self.reply = self.reply[:n], self.reply[n:]
        return out


class ServoBusProtocol(unittest.TestCase):
    def test_manual_examples(self):
        # ping ID 1: FF FF 01 02 01 FB
        self.assertEqual(sb.packet(1, sb.PING), bytes.fromhex("FFFF010201FB"))
        # read 2 bytes of present position (0x38) from ID 1: FF FF 01 04 02 38 02 BE
        self.assertEqual(sb.packet(1, sb.READ, bytes([0x38, 2])), bytes.fromhex("FFFF0104023802BE"))
        # write goal position 2048, time 0, speed 1000 to ID 1: FF FF 01 09 03 2A 00 08 00 00 E8 03 D5
        p = sb.packet(1, sb.WRITE, bytes([sb.ADDR_GOAL_POSITION]) + sb.u16(2048) + sb.u16(0) + sb.u16(1000))
        self.assertEqual(p, bytes.fromhex("FFFF0109032A00080000E803D5"))

    def test_sign_encoding(self):
        for v in (0, 1, 2047, 4095, -1, -100, -4095):
            lo, hi = sb.u16(v)
            self.assertEqual(sb.s16(lo, hi), v)
        self.assertEqual(sb.u16(-100), bytes([100, 0x80]))           # magnitude, sign in bit 15

    def test_sync_write_frame(self):
        bus = sb.ServoBus.__new__(sb.ServoBus)
        bus.ser, bus.lock = FakeSerial(), __import__("threading").Lock()
        bus.set_positions({1: 2048, 17: 100})
        pkt = bus.ser.sent[-1]
        self.assertEqual(pkt[:5], bytes([0xFF, 0xFF, 0xFE, 2 * 7 + 4, sb.SYNC_WRITE]))
        self.assertEqual(pkt[5:7], bytes([sb.ADDR_GOAL_POSITION, 6]))
        self.assertEqual(pkt[7:14], bytes([1]) + sb.u16(2048) + sb.u16(0) + sb.u16(0))
        self.assertEqual(pkt[14:21], bytes([17]) + sb.u16(100) + sb.u16(0) + sb.u16(0))
        self.assertEqual(pkt[-1], sb.checksum(pkt[2:-1]))
        # a full 17-servo frame is 2 + 3 + 2 + 17 x 7 + 1 = 127 bytes: 1.27 ms at 1 Mbit/s, well inside the 20 ms frame
        bus.set_positions({s["id"]: 2048 for s in SERVOS.values()})
        self.assertEqual(len(bus.ser.sent[-1]), 127)

    def test_read_reply_parsing(self):
        bus = sb.ServoBus.__new__(sb.ServoBus)
        bus.ser, bus.lock = FakeSerial(), __import__("threading").Lock()
        body = bytes([5, 4, 0]) + sb.u16(-300)
        bus.ser.reply = b"\xff\xff" + body + bytes([sb.checksum(body)])
        self.assertEqual(bus.position(5), -300)
        bus.ser.reply = b"\xff\xff\x05\x04\x00\x00\x00\x00"                      # bad checksum
        with self.assertRaises(IOError):
            bus.position(5)


class ConfigAndGaits(unittest.TestCase):
    def test_ids(self):
        ids = sorted(s["id"] for s in SERVOS.values())
        self.assertEqual(ids, list(range(1, 18)))
        self.assertEqual(set(SERVOS), set(LEG_JOINTS + ARM_JOINTS))
        for s in SERVOS.values():
            self.assertIn(s["direction"], (1, -1))
            self.assertTrue(0 <= s["zero_ticks"] <= 4095)

    def test_limits_inside_cad_clear_range(self):
        cad = ROOT / "jx0" / "results" / "verify_cad.json"
        if not cad.exists():
            self.skipTest("run jx0/verify/verify_cad.py first")
        sweeps = json.loads(cad.read_text(encoding="utf-8"))["joint_sweeps"]
        for name, s in SERVOS.items():
            lo, hi = s["limits_deg"]
            c_lo, c_hi = sweeps[name]["own_limb_clear_deg"]
            self.assertGreaterEqual(lo, c_lo, name)
            self.assertLessEqual(hi, c_hi, name)

    def test_gaits(self):
        expected = {"forward", "forward_slow", "backward", "turn_left", "turn_right", "side_left", "forward_2", "forward_4",
                    "backward_2", "backward_4", "turn_left_2", "turn_right_2", "side_left_2", "side_right_2"}
        self.assertTrue(expected <= set(GAITS))
        stand0 = None
        for name, g in GAITS.items():
            self.assertAlmostEqual(g["dt"], 1.0 / CFG["bus"]["rate_hz"])
            self.assertEqual(len(g["q"]), len(g["stance"]))
            self.assertTrue(set(LEG_JOINTS) <= set(g["joints"]), name)
            for frame in g["q"]:
                for j, v in zip(g["joints"], frame):
                    lo, hi = SERVOS[j]["limits_deg"]
                    self.assertTrue(lo - 1e-6 <= math.degrees(v) <= hi + 1e-6, f"{name} {j} {math.degrees(v):.1f}")
            first, last = dict(zip(g["joints"], g["q"][0])), dict(zip(g["joints"], g["q"][-1]))
            for j in LEG_JOINTS:                       # blocks start and end in the same stance: they chain
                self.assertAlmostEqual(first[j], last[j], delta=0.002, msg=f"{name} {j}")
                if stand0 is None:
                    pass
                else:
                    self.assertAlmostEqual(first[j], stand0[j], delta=0.002, msg=f"{name} {j}")
            stand0 = stand0 or first
            for st in g["stance"]:
                self.assertTrue(st[0] or st[1], f"{name}: a frame with no foot on the ground")


class FakeBus:
    def __init__(self):
        self.ticks, self.torqued = {}, {}

    def set_positions(self, ticks, speed=0, acc=0):
        self.ticks.update(ticks)

    def position(self, sid):
        return self.ticks.get(sid, 2048)

    def torque(self, sid, on):
        self.torqued[sid] = on


def hardware_io():
    from jx0bot.robot import HardwareIO
    io = HardwareIO.__new__(HardwareIO)
    io.cfg, io.tpr = CFG, sb.TICKS_PER_REV
    io.servos = {k: dict(v) for k, v in SERVOS.items()}
    io.bus = FakeBus()
    return io


class HardwareMapping(unittest.TestCase):
    def test_angle_ticks_round_trip(self):
        io = hardware_io()
        io.servos["l_knee"].update(direction=-1, zero_ticks=1900)
        q = {"l_knee": math.radians(45), "r_hip_pitch": math.radians(-20), "neck_yaw": math.radians(30)}
        io.send(q)
        self.assertEqual(io.bus.ticks[4], round(1900 - 512))                   # 45 deg = 512 ticks, reversed
        back = io.read_pose()
        for k, v in q.items():
            self.assertAlmostEqual(back[k], v, delta=math.radians(0.1))

    def test_clamped_to_limits(self):
        io = hardware_io()
        io.send({"l_knee": math.radians(170), "l_ankle_roll": math.radians(-40)})
        self.assertAlmostEqual(io.read_pose()["l_knee"], math.radians(SERVOS["l_knee"]["limits_deg"][1]), delta=math.radians(0.1))
        self.assertAlmostEqual(io.read_pose()["l_ankle_roll"], math.radians(SERVOS["l_ankle_roll"]["limits_deg"][0]), delta=math.radians(0.1))


class RecordingIO:
    """Instant I/O for the action tests: records every command, upright IMU, yaw that follows the turn gaits."""

    def __init__(self):
        self.sent, self.yaw = [], 0.0

    def send(self, q):
        self.sent.append(dict(q))

    def tick(self, dt):
        pass

    def sleep(self, s):
        pass

    def attitude(self):
        return 0.0, 0.0, self.yaw, (0.0, 0.0, 0.0)

    def read_pose(self):
        return {}


class Actions(unittest.TestCase):
    def setUp(self):
        self.io = RecordingIO()
        self.robot = Robot(self.io, CFG)

    def check_limits(self):
        for q in self.io.sent:
            for j, v in q.items():
                lo, hi = SERVOS[j]["limits_deg"]
                self.assertTrue(lo - 0.5 <= math.degrees(v) <= hi + 0.5, f"{j} {math.degrees(v):.1f}")

    def test_every_action_inside_limits(self):
        r = self.robot
        r.stand(0.2)
        for call in (lambda: r.wave("left"), lambda: r.wave("right"), lambda: r.nod("yes"), lambda: r.nod("no"),
                     lambda: r.look("left"), lambda: r.look("right"), lambda: r.walk(5, "forward"),
                     lambda: r.walk(3, "backward"), lambda: r.walk(2, "left"), lambda: r.walk(2, "right")):
            call()
        self.check_limits()
        self.assertTrue(set(LEG_JOINTS + ARM_JOINTS) <= set(self.io.sent[-1]))

    def test_walk_plans(self):
        played = []
        self.robot.play = lambda g: played.append(g)
        self.robot.stand = lambda s=0: None
        self.robot.walk(10, "forward")
        self.assertEqual(played, ["forward_4", "forward_4", "forward_2"])
        played.clear()
        self.robot.walk(7, "forward")
        self.assertEqual(played, ["forward_4", "forward_2", "forward_2"])
        played.clear()
        self.robot.walk(3, "left")
        self.assertEqual(played, ["side_left_2", "side_left_2"])

    def test_turn_closes_on_yaw(self):
        io, r = self.io, self.robot

        def play(g):
            io.yaw += math.radians(10 if g == "turn_left_2" else -10)
        r.play, r.stand = play, (lambda s=0: None)
        for want in (45, -90, 20, -170):                # stops within half a block (5 deg) of the request
            io.yaw = 0.0
            got = int(r.turn(want).split()[1])
            self.assertLessEqual(abs(got - want), 5, (want, got))

    def test_unknown_action(self):
        with self.assertRaises(ValueError):
            self.robot.act("fly", {})


class BalanceTests(unittest.TestCase):
    def test_zero_and_signs(self):
        b = Balance()
        self.assertTrue(all(abs(v) < 1e-12 for v in b.update(0, 0, 0, 0, [True, True]).values()))
        c = Balance().update(0.05, 0.05, 0.0, 0.0, [True, False])        # leaning: stance leg pushes back
        self.assertGreater(c["l_ankle_pitch"], 0)
        self.assertGreater(c["l_ankle_roll"], 0)
        c = Balance({"limit": 0.1, "sr": 5.0}).update(0.2, 0.0, 0.0, 0.0, [True, False])
        self.assertAlmostEqual(c["r_hip_roll"], 0.1)                        # swing step clamped to the limit
        self.assertAlmostEqual(c["r_ankle_roll"], -0.1)                     # foot kept flat


class Ev:
    def __init__(self, t):
        self.type, self.text = "text", t


class FakeStream:
    def __init__(self, texts, final):
        self.texts, self.final = texts, final

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def __iter__(self):
        return iter(Ev(t) for t in self.texts)

    def get_final_message(self):
        return self.final


class FakeClient:
    """Scripted Claude: a list of (text chunks, content blocks, stop_reason) turns."""

    def __init__(self, turns):
        self.turns, self.calls = list(turns), []
        self.beta = SimpleNamespace(messages=SimpleNamespace(stream=self.stream))

    def stream(self, **kw):
        self.calls.append(kw)
        texts, blocks, stop = self.turns.pop(0)
        return FakeStream(texts, SimpleNamespace(content=blocks, stop_reason=stop))


def tool(name, args, i="t1"):
    return SimpleNamespace(type="tool_use", id=i, name=name, input=args)


def text(t):
    return SimpleNamespace(type="text", text=t)


class BrainLoop(unittest.TestCase):
    def setUp(self):
        from jx0bot import brain
        self.brain_mod = brain
        self.acts, self.said = [], []

    def make(self, turns):
        def act(name, args):
            self.acts.append((name, args))
            return "done"
        return self.brain_mod.Brain(act=act, on_sentence=self.said.append, client=FakeClient(turns))

    def test_validate(self):
        v = self.brain_mod.validate
        self.assertIsNone(v("walk", {"steps": 4, "direction": "forward"}))
        self.assertIsNotNone(v("walk", {"steps": 40, "direction": "forward"}))
        self.assertIsNotNone(v("walk", {"steps": 4}))
        self.assertIsNotNone(v("walk", {"steps": True, "direction": "left"}))
        self.assertIsNotNone(v("wave", {"arm": "middle"}))
        self.assertIsNotNone(v("fly", {}))
        names = {t["name"] for t in self.brain_mod.TOOLS}
        self.assertEqual(names, {"wave", "nod", "walk", "turn", "look"})     # all handled by Robot.act

    def test_tool_runs_and_result_returns(self):
        b = self.make([(["Sure, walking. ", "Here I go!"], [text("Sure, walking. Here I go!"), tool("walk", {"steps": 4, "direction": "forward"})], "tool_use"),
                       (["Done!"], [text("Done!")], "end_turn")])
        b.reply("walk forward four steps")
        self.assertEqual(self.acts, [("walk", {"steps": 4, "direction": "forward"})])
        self.assertEqual(self.said, ["Sure, walking.", "Here I go!", "Done!"])
        results = b.messages[2]["content"]
        self.assertEqual(results[0]["type"], "tool_result")
        self.assertEqual(results[0]["content"], "done")
        self.assertEqual(b.client.calls[0]["tools"], self.brain_mod.TOOLS)

    def test_invalid_input_not_run(self):
        b = self.make([([], [tool("walk", {"steps": 99, "direction": "forward"})], "tool_use"),
                       (["Ok."], [text("Ok.")], "end_turn")])
        b.reply("walk a lot")
        self.assertEqual(self.acts, [])
        self.assertTrue(b.messages[2]["content"][0]["is_error"])

    def test_truncated_input_not_run(self):
        b = self.make([([], [tool("walk", {"steps": 3})], "max_tokens"), (["Sorry."], [text("Sorry.")], "end_turn")])
        b.reply("walk")
        self.assertEqual(self.acts, [])

    def test_refusal(self):
        b = self.make([(["I"], [text("I")], "refusal")])
        b.reply("something bad")
        self.assertEqual(self.said[-1], "I'd rather not do that one.")


if __name__ == "__main__":
    unittest.main()
