"""JX0's face: two eyes and a mouth on the round 1.28" 240x240 display in the head, drawn with Pillow.

Moods: idle (blinking, eyes drift), listening (big eyes), busy (eyes look down, moving). `mouth(level)` opens the
mouth with the speech loudness (voice.Speaker calls it), so the face talks in sync.

Backends:
  none     - no display; writes face.png every second (PC / simulation testing)
  gc9a01   - the round GC9A01 module in the BOM, on SPI0 through luma.core's SPI interface. The init sequence is the
             GC9A01 vendor sequence used by the common open-source drivers; UNVERIFIED on the JX0 hardware.
  st7789   - a 240x240 ST7789 module (luma.lcd's own driver), the fallback if the round module gives trouble.
"""
from __future__ import annotations

import math
import random
import threading
import time
from pathlib import Path

from PIL import Image, ImageDraw

SIZE = 240
BG, FG, ACCENT = (0, 0, 0), (120, 230, 255), (255, 170, 60)

# GC9A01 power-on sequence: (command, data bytes, delay after in s)
GC9A01_INIT = [
    (0xEF, [], 0), (0xEB, [0x14], 0), (0xFE, [], 0), (0xEF, [], 0), (0xEB, [0x14], 0),
    (0x84, [0x40], 0), (0x85, [0xFF], 0), (0x86, [0xFF], 0), (0x87, [0xFF], 0), (0x88, [0x0A], 0),
    (0x89, [0x21], 0), (0x8A, [0x00], 0), (0x8B, [0x80], 0), (0x8C, [0x01], 0), (0x8D, [0x01], 0),
    (0x8E, [0xFF], 0), (0x8F, [0xFF], 0), (0xB6, [0x00, 0x20], 0),
    (0x36, [0x08], 0),                                   # MADCTL: BGR order
    (0x3A, [0x06], 0),                                   # COLMOD: 18 bit/pixel (what luma's RGB writer sends)
    (0x90, [0x08, 0x08, 0x08, 0x08], 0), (0xBD, [0x06], 0), (0xBC, [0x00], 0), (0xFF, [0x60, 0x01, 0x04], 0),
    (0xC3, [0x13], 0), (0xC4, [0x13], 0), (0xC9, [0x22], 0), (0xBE, [0x11], 0), (0xE1, [0x10, 0x0E], 0),
    (0xDF, [0x21, 0x0C, 0x02], 0),
    (0xF0, [0x45, 0x09, 0x08, 0x08, 0x26, 0x2A], 0), (0xF1, [0x43, 0x70, 0x72, 0x36, 0x37, 0x6F], 0),
    (0xF2, [0x45, 0x09, 0x08, 0x08, 0x26, 0x2A], 0), (0xF3, [0x43, 0x70, 0x72, 0x36, 0x37, 0x6F], 0),
    (0xED, [0x1B, 0x0B], 0), (0xAE, [0x77], 0), (0xCD, [0x63], 0),
    (0x70, [0x07, 0x07, 0x04, 0x0E, 0x0F, 0x09, 0x07, 0x08, 0x03], 0), (0xE8, [0x34], 0),
    (0x62, [0x18, 0x0D, 0x71, 0xED, 0x70, 0x70, 0x18, 0x0F, 0x71, 0xEF, 0x70, 0x70], 0),
    (0x63, [0x18, 0x11, 0x71, 0xF1, 0x70, 0x70, 0x18, 0x13, 0x71, 0xF3, 0x70, 0x70], 0),
    (0x64, [0x28, 0x29, 0xF1, 0x01, 0xF1, 0x00, 0x07], 0),
    (0x66, [0x3C, 0x00, 0xCD, 0x67, 0x45, 0x45, 0x10, 0x00, 0x00, 0x00], 0),
    (0x67, [0x00, 0x3C, 0x00, 0x00, 0x00, 0x01, 0x54, 0x10, 0x32, 0x98], 0),
    (0x74, [0x10, 0x85, 0x80, 0x00, 0x00, 0x4E, 0x00], 0), (0x98, [0x3E, 0x07], 0),
    (0x35, [], 0), (0x21, [], 0),                        # tearing effect on, inversion on
    (0x11, [], 0.12), (0x29, [], 0.02),                  # sleep out, display on
]


def open_display(cfg: dict, backend: str):
    if backend == "none":
        return None
    from luma.core.interface.serial import spi
    serial = spi(port=cfg.get("spi_port", 0), device=cfg.get("spi_device", 0), gpio_DC=cfg["gpio_dc"],
                 gpio_RST=cfg["gpio_rst"], bus_speed_hz=cfg.get("spi_hz", 40_000_000))
    from luma.lcd.device import backlit_device, st7789
    if backend == "st7789":
        return st7789(serial, width=SIZE, height=SIZE, gpio_LIGHT=cfg["gpio_backlight"])
    if backend != "gc9a01":
        raise ValueError(f"unknown face backend {backend!r}")

    class GC9A01(st7789):
        """st7789's window/RGB writer is the same MIPI command set; only the power-on sequence differs."""
        def __init__(self, serial_interface, **kw):
            backlit_device.__init__(self, None, serial_interface, **kw)   # skip the ST7789 init
            self.capabilities(SIZE, SIZE, 0, mode="RGB")
            for cmd, data, delay in GC9A01_INIT:
                self.command(cmd, *data)
                if delay:
                    time.sleep(delay)
            self.clear()
            self.show()

    return GC9A01(serial, gpio_LIGHT=cfg["gpio_backlight"])


class Face:
    def __init__(self, cfg: dict | None = None, backend: str = "none", fps: float = 20.0, png: str = "face.png"):
        self.dev = open_display(cfg or {}, backend)
        self.fps, self.png = fps, Path(png)
        self.mood, self.level = "idle", 0.0
        self._gaze = [0.0, 0.0]
        self._gaze_goal = [0.0, 0.0]
        self._blink_at = time.time() + 2.0
        self._stop = threading.Event()
        self._last_png = 0.0

    # --- inputs --------------------------------------------------------------------------------------------------
    def set_mood(self, mood: str):
        self.mood = mood

    def mouth(self, level: float):
        """Speech loudness 0..1 (voice.Speaker's on_level callback)."""
        self.level = max(0.0, min(1.0, float(level)))

    # --- drawing -------------------------------------------------------------------------------------------------
    def draw(self, t: float) -> Image.Image:
        img = Image.new("RGB", (SIZE, SIZE), BG)
        d = ImageDraw.Draw(img)
        if self.mood == "busy":
            self._gaze_goal = [0.25 * math.sin(2.0 * t), 0.5]
        elif self.mood == "listening":
            self._gaze_goal = [0.0, -0.1]
        elif random.random() < 0.01:
            self._gaze_goal = [random.uniform(-0.6, 0.6), random.uniform(-0.3, 0.3)]
        self._gaze = [g + 0.2 * (goal - g) for g, goal in zip(self._gaze, self._gaze_goal)]

        blink = 0.0
        if t >= self._blink_at:
            phase = (t - self._blink_at) / 0.15
            blink = 1.0 - abs(1.0 - phase) if phase < 2.0 else 0.0
            if phase >= 2.0:
                self._blink_at = t + random.uniform(2.0, 5.0)
        w = 44 if self.mood == "listening" else 36
        h = (64 if self.mood == "listening" else 52) * (1.0 - 0.9 * blink)
        gx, gy = 14 * self._gaze[0], 10 * self._gaze[1]
        for cx in (80, 160):
            x, y = cx + gx, 95 + gy
            d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], radius=min(w, h) / 2, fill=FG)

        open_h = 4 + 30 * self.level
        mw = 60 + 10 * self.level
        color = ACCENT if self.level > 0.05 else FG
        d.rounded_rectangle([120 - mw / 2, 165 - open_h / 2, 120 + mw / 2, 165 + open_h / 2],
                            radius=min(open_h, mw) / 2, fill=color)
        return img

    def show_once(self, t: float | None = None):
        img = self.draw(time.time() if t is None else t)
        if self.dev is not None:
            self.dev.display(img)
        elif time.time() - self._last_png > 1.0:
            img.save(self.png)
            self._last_png = time.time()
        return img

    def _loop(self):
        period = 1.0 / self.fps
        while not self._stop.is_set():
            t0 = time.time()
            self.show_once(t0)
            self.level *= 0.85                     # mouth closes between speech level updates
            self._stop.wait(max(0.0, period - (time.time() - t0)))

    def start(self):
        threading.Thread(target=self._loop, daemon=True).start()
        return self

    def stop(self):
        self._stop.set()


if __name__ == "__main__":                        # python -m jx0bot.face  -> face_idle.png, face_talking.png ...
    f = Face()
    for mood, level, name in (("idle", 0.0, "idle"), ("listening", 0.0, "listening"), ("busy", 0.0, "busy"),
                              ("idle", 0.8, "talking")):
        f.set_mood(mood)
        f.mouth(level)
        for i in range(30):
            img = f.draw(1.0 + i / 20)
        img.save(f"face_{name}.png")
        print(f"face_{name}.png")
