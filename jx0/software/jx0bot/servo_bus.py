"""Feetech STS serial-bus protocol (Waveshare ST3215 / Feetech STS3215 and the other STS-series servos).

Half-duplex TTL UART through a bus-servo adapter (USB or the Pi's UART), default 1 Mbit/s. Packet:
    0xFF 0xFF ID LEN INSTR PARAM... CHECKSUM,   LEN = len(PARAM) + 2,   CHECKSUM = ~(ID + LEN + INSTR + sum(PARAM)) & 0xFF
STS registers are little-endian (low byte first); position/speed use bit 15 as the sign. Register addresses follow
the Feetech SMS/STS memory table (ASSUMED until checked on a real servo: see jx0/docs/bringup.md).
`FakeBus` emulates servos in software for tests and for running the robot code on a PC.
"""
from __future__ import annotations

import threading
import time

PING, READ, WRITE, SYNC_WRITE = 0x01, 0x02, 0x03, 0x83
BROADCAST = 0xFE

# SMS/STS control table
ADDR_ID = 5
ADDR_MIN_ANGLE, ADDR_MAX_ANGLE = 9, 11
ADDR_TORQUE_ENABLE = 40
ADDR_ACC = 41
ADDR_GOAL_POSITION = 42          # 2 bytes, then goal time (2) and goal speed (2): 42..47
ADDR_TORQUE_LIMIT = 48
ADDR_LOCK = 55
ADDR_PRESENT_POSITION = 56       # 2 bytes, then present speed (2), load (2), voltage (1), temperature (1): 56..63
ADDR_PRESENT_VOLTAGE = 62
ADDR_PRESENT_TEMPERATURE = 63

TICKS_PER_REV = 4096             # 12-bit magnetic encoder, 0.088 deg per tick
CENTER = 2048


def checksum(body: bytes) -> int:
    return (~sum(body)) & 0xFF


def packet(sid: int, instr: int, params: bytes = b"") -> bytes:
    body = bytes([sid, len(params) + 2, instr]) + params
    return b"\xff\xff" + body + bytes([checksum(body)])


def u16(v: int) -> bytes:
    """Encode a signed value in STS format: magnitude in bits 0-14, sign in bit 15, little-endian."""
    v = int(v)
    raw = (-v | 0x8000) if v < 0 else v
    return bytes([raw & 0xFF, (raw >> 8) & 0xFF])


def s16(lo: int, hi: int) -> int:
    raw = lo | (hi << 8)
    return -(raw & 0x7FFF) if raw & 0x8000 else raw


class ServoBus:
    def __init__(self, port: str = "/dev/ttyUSB0", baud: int = 1_000_000, timeout: float = 0.02):
        import serial
        self.ser = serial.Serial(port, baud, timeout=timeout)
        self.lock = threading.Lock()

    # ------------------------------------------------------------------ low level
    def _txrx(self, pkt: bytes, reply_params: int | None):
        with self.lock:
            self.ser.reset_input_buffer()
            self.ser.write(pkt)
            if reply_params is None:
                return None
            n = 6 + reply_params                                  # FF FF ID LEN ERR PARAMS CHK
            data = self.ser.read(n)
            if len(data) != n or data[:2] != b"\xff\xff" or checksum(data[2:-1]) != data[-1]:
                raise IOError(f"no/bad reply from servo {pkt[2]} ({data.hex()})")
            if data[4]:
                raise IOError(f"servo {data[2]} status error 0x{data[4]:02x}")
            return data[5:-1]

    def ping(self, sid: int) -> bool:
        try:
            self._txrx(packet(sid, PING), 0)
            return True
        except IOError:
            return False

    def read(self, sid: int, addr: int, n: int) -> bytes:
        return self._txrx(packet(sid, READ, bytes([addr, n])), n)

    def write(self, sid: int, addr: int, data: bytes) -> None:
        self._txrx(packet(sid, WRITE, bytes([addr]) + data), 0)

    def sync_write(self, addr: int, per_servo: dict[int, bytes]) -> None:
        """One packet for all servos (no replies): the normal way to command a whole pose."""
        if not per_servo:
            return
        n = len(next(iter(per_servo.values())))
        params = bytes([addr, n]) + b"".join(bytes([sid]) + d for sid, d in per_servo.items())
        self._txrx(packet(BROADCAST, SYNC_WRITE, params), None)

    # ------------------------------------------------------------------ helpers
    def torque(self, sid: int, on: bool) -> None:
        self.write(sid, ADDR_TORQUE_ENABLE, bytes([1 if on else 0]))

    def set_positions(self, ticks: dict[int, int], speed: int = 0, acc: int = 0) -> None:
        """Goal position (+ goal time 0, goal speed) for many servos at once. speed 0 = maximum."""
        self.sync_write(ADDR_GOAL_POSITION, {sid: u16(p) + u16(0) + u16(speed) for sid, p in ticks.items()})

    def position(self, sid: int) -> int:
        d = self.read(sid, ADDR_PRESENT_POSITION, 2)
        return s16(d[0], d[1])

    def status(self, sid: int) -> dict:
        d = self.read(sid, ADDR_PRESENT_POSITION, 8)
        return {"position": s16(d[0], d[1]), "speed": s16(d[2], d[3]), "load": s16(d[4], d[5]),
                "voltage_v": d[6] / 10.0, "temperature_c": d[7]}

    def change_id(self, old: int, new: int) -> None:
        """Set a new bus ID (EEPROM): unlock, write, lock. Connect ONE servo at a time for this."""
        self.write(old, ADDR_LOCK, b"\x00")
        self.write(old, ADDR_ID, bytes([new]))
        self.write(new, ADDR_LOCK, b"\x01")


class FakeBus:
    """Software servos: each moves toward its goal at `max_speed_ticks_s`. Same interface as ServoBus."""

    def __init__(self, ids, max_speed_ticks_s: float = 3000.0):
        self.pos = {i: float(CENTER) for i in ids}
        self.goal = dict(self.pos)
        self.on = {i: False for i in ids}
        self.v = max_speed_ticks_s
        self.t = time.time()
        self.log: list = []

    def _advance(self):
        now = time.time()
        dt, self.t = now - self.t, now
        for i in self.pos:
            if self.on[i]:
                err = self.goal[i] - self.pos[i]
                step = max(-self.v * dt, min(self.v * dt, err))
                self.pos[i] += step

    def ping(self, sid):
        return sid in self.pos

    def torque(self, sid, on):
        self._advance()
        self.on[sid] = on

    def set_positions(self, ticks, speed=0, acc=0):
        self._advance()
        for sid, p in ticks.items():
            self.goal[sid] = float(p)
        self.log.append(dict(ticks))

    def position(self, sid):
        self._advance()
        return int(round(self.pos[sid]))

    def status(self, sid):
        return {"position": self.position(sid), "speed": 0, "load": 0, "voltage_v": 12.0, "temperature_c": 30}
