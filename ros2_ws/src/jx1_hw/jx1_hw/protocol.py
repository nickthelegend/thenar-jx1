"""Host <-> hub USB-serial protocol of firmware/hub/jx1_hub/jx1_hub.ino (little-endian, CRC-16/MODBUS).

host -> hub : A5 5A | seq u32 | mode u8 | pad u8 | NJ x {q, dq, kp, kd, tau} f32 | crc16      (joint space of the hub:
              sign/zero are applied by the hub; the ankle "joints" are the crank angles of motors A and B)
hub -> host : 5A A5 | seq u32 | flags u8 (estop | fault<<1 | mode<<2) | NJ x {q, dq, tau, temp} f32 + faults u8 | crc16
              (faults bit 7 = no CAN feedback for longer than CAN_TIMEOUT_US)
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field

DISABLED, DAMPING, RUN = 0, 1, 2
CMD_HEAD, STATE_HEAD = b"\xA5\x5A", b"\x5A\xA5"


def crc16(data: bytes) -> int:
    """CRC-16/MODBUS (poly 0xA001 reflected, init 0xFFFF) - the firmware's crc16()."""
    c = 0xFFFF
    for b in data:
        c ^= b
        for _ in range(8):
            c = (c >> 1) ^ 0xA001 if c & 1 else c >> 1
    return c


def command_size(nj: int) -> int:
    return 8 + nj * 20 + 2


def state_size(nj: int) -> int:
    return 7 + nj * 17 + 2


def pack_command(seq: int, mode: int, targets) -> bytes:
    """targets: NJ tuples (q, dq, kp, kd, tau) in hub joint space."""
    body = CMD_HEAD + struct.pack("<IBx", seq & 0xFFFFFFFF, mode) + b"".join(struct.pack("<5f", *t) for t in targets)
    return body + struct.pack("<H", crc16(body))


@dataclass
class HubState:
    seq: int
    estop: bool
    fault: bool
    mode: int
    q: list = field(default_factory=list)
    dq: list = field(default_factory=list)
    tau: list = field(default_factory=list)
    temp: list = field(default_factory=list)
    faults: list = field(default_factory=list)

    @property
    def stale(self):
        return [bool(f & 0x80) for f in self.faults]


def pack_state(st: HubState) -> bytes:
    flags = int(st.estop) | (int(st.fault) << 1) | ((st.mode & 0x3F) << 2)
    body = STATE_HEAD + struct.pack("<IB", st.seq & 0xFFFFFFFF, flags)
    for j in range(len(st.q)):
        body += struct.pack("<4fB", st.q[j], st.dq[j], st.tau[j], st.temp[j], st.faults[j])
    return body + struct.pack("<H", crc16(body))


def unpack_state(frame: bytes, nj: int) -> HubState:
    seq, flags = struct.unpack_from("<IB", frame, 2)
    st = HubState(seq=seq, estop=bool(flags & 1), fault=bool(flags & 2), mode=flags >> 2)
    for j in range(nj):
        q, dq, tau, temp, f = struct.unpack_from("<4fB", frame, 7 + j * 17)
        st.q.append(q), st.dq.append(dq), st.tau.append(tau), st.temp.append(temp), st.faults.append(f)
    return st


def unpack_command(frame: bytes, nj: int):
    seq, mode = struct.unpack_from("<IB", frame, 2)
    return seq, mode, [struct.unpack_from("<5f", frame, 8 + j * 20) for j in range(nj)]


class FrameReader:
    """Byte-stream -> complete, CRC-checked frames with a given header and size (resynchronises on garbage)."""

    def __init__(self, head: bytes, size: int):
        self.head, self.size, self.buf = head, size, bytearray()
        self.crc_errors = 0

    def feed(self, data: bytes):
        self.buf += data
        out = []
        while True:
            i = self.buf.find(self.head)
            if i < 0:
                del self.buf[:-1]
                return out
            if i:
                del self.buf[:i]
            if len(self.buf) < self.size:
                return out
            frame = bytes(self.buf[:self.size])
            if struct.unpack_from("<H", frame, self.size - 2)[0] == crc16(frame[:-2]):
                out.append(frame)
                del self.buf[:self.size]
            else:
                self.crc_errors += 1
                del self.buf[:2]
