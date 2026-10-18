"""JX0's eyes: two WS2812 12-LED rings (24 LEDs, chained: left ring first) behind the head's clear lenses.

The data line is the Pi's SPI MOSI, GPIO 10 (pin 19): the I2S audio has GPIO 18-21, so the PWM channel the usual
NeoPixel library wants is taken, and SPI drives WS2812s fine (adafruit-circuitpython-neopixel-spi; enable SPI with
raspi-config). The rings run on the UBEC's 5 V. Brightness is capped (config eyes.brightness) so the 24 LEDs stay under
about 0.5 A: full white would be 1.4 A.

States the program sets: idle (soft cyan, blinking now and then), listening (blue), thinking (a white dot running
round), speaking (cyan, pulsing). Moods Claude can ask for (the "eyes" tool): normal, happy, sad, angry, surprised,
sleepy, love. With no LED hardware (the simulator, a PC) the eyes only remember what they show, for the tests.
"""
from __future__ import annotations

import math
import threading
import time

LEDS_PER_EYE = 12
MOODS = {"normal": (0, 200, 255), "happy": (255, 190, 0), "sad": (30, 60, 255), "angry": (255, 0, 0),
         "surprised": (255, 255, 255), "sleepy": (120, 40, 200), "love": (255, 40, 140)}
STATES = {"idle": (0, 200, 255), "listening": (0, 80, 255), "thinking": (255, 255, 255), "speaking": (0, 220, 255)}


class _NoLeds:
    """Stand-in when there is no LED hardware: keeps the last frame."""

    def __init__(self, n):
        self.frame = [(0, 0, 0)] * n

    def show(self, pixels):
        self.frame = list(pixels)


class _SpiLeds:
    def __init__(self, n):
        import board
        import neopixel_spi
        self.px = neopixel_spi.NeoPixel_SPI(board.SPI(), n, auto_write=False, pixel_order=neopixel_spi.GRB)

    def show(self, pixels):
        for i, c in enumerate(pixels):
            self.px[i] = c
        self.px.show()


class Eyes:
    def __init__(self, cfg: dict | None = None, hardware: bool = True, fps: float = 30.0):
        c = (cfg or {}).get("eyes", {})
        self.n = LEDS_PER_EYE
        self.brightness = float(c.get("brightness", 0.3))
        self.blink_s = float(c.get("blink_every_s", 4.0))
        self.leds = _NoLeds(2 * self.n)
        if hardware and c.get("enabled", True):
            try:
                self.leds = _SpiLeds(2 * self.n)
            except Exception as exc:                       # no SPI / library: carry on without lights
                print(f"[eyes] no LED rings ({exc}); running without them")
        self.state, self.mood_name = "idle", "normal"
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._dt = 1.0 / fps
        self._t0 = time.monotonic()
        self._thread = None

    # ---- what the program and Claude set
    def set_state(self, state: str):
        if state not in STATES:
            raise ValueError(f"unknown eye state {state}")
        with self._lock:
            self.state = state

    def mood(self, name: str) -> str:
        """Claude's "eyes" tool: the colour the eyes keep (idle and speaking) until the next mood."""
        if name not in MOODS:
            raise ValueError(f"unknown mood {name}")
        with self._lock:
            self.mood_name = name
        return f"eyes {name}"

    def color(self, state=None):
        state = state or self.state
        if state in ("listening", "thinking"):
            return STATES[state]
        return MOODS[self.mood_name] if self.mood_name != "normal" else STATES[state]

    # ---- drawing
    def frame(self, t: float):
        """The 24 colours at time t (s): left ring then right ring."""
        with self._lock:
            state = self.state
            r, g, b = self.color(state)
        k = self.brightness
        if state == "thinking":
            lit = int(t * 12) % self.n                     # one dot chasing round, one turn a second
            ring = [(r, g, b) if i == lit else (r // 12, g // 12, b // 12) for i in range(self.n)]
            return [tuple(int(v * k) for v in c) for c in ring + ring]
        level = 1.0
        if state == "speaking":
            level = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(2 * math.pi * 3.0 * t))
        elif state == "listening":
            level = 0.75 + 0.25 * math.sin(2 * math.pi * 0.8 * t)
        elif state == "idle" and self.blink_s > 0 and (t % self.blink_s) < 0.15:
            level = 0.0                                    # a blink
        c = tuple(int(v * k * level) for v in (r, g, b))
        return [c] * (2 * self.n)

    def show(self, t: float | None = None):
        self.leds.show(self.frame(time.monotonic() - self._t0 if t is None else t))

    def start(self):
        def run():
            while not self._stop.is_set():
                self.show()
                time.sleep(self._dt)
        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()
        return self

    def close(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)
        self.leds.show([(0, 0, 0)] * (2 * self.n))
