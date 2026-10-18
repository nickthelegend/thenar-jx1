"""JX0's chest camera: the USB webcam behind the torso's window records what the robot sees.

    python -m jx0bot.camera --seconds 30                     record 30 s to recordings/jx0_<date>_<time>.mp4
    python -m jx0bot.camera --snapshot                       one photo to recordings/jx0_<date>_<time>.jpg

The main program (jx0bot.main) starts a Recorder too when config camera.record is true: it records while JX0 runs,
in files of camera.segment_s seconds, so a crash or a pulled battery loses at most the last one. Needs OpenCV
(sudo apt install python3-opencv); without it, or without a camera, the recorder says so and does nothing.
"""
from __future__ import annotations

import argparse
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _stamp():
    return time.strftime("%Y%m%d_%H%M%S")


class Recorder:
    def __init__(self, cfg: dict | None = None, out_dir: Path | None = None):
        c = (cfg or {}).get("camera", {})
        self.device = c.get("device", 0)
        self.size = tuple(c.get("size", (1280, 720)))
        self.fps = float(c.get("fps", 15))
        self.segment_s = float(c.get("segment_s", 300))
        self.out_dir = Path(out_dir or c.get("out_dir", HERE.parent / "recordings"))
        self._stop = threading.Event()
        self._thread = None
        self.files: list[Path] = []
        self.cap = None
        try:
            import cv2
            self.cv2 = cv2
        except ImportError:
            self.cv2 = None
            print("[camera] OpenCV not installed (sudo apt install python3-opencv): no recording")

    def open(self) -> bool:
        if self.cv2 is None:
            return False
        cap = self.cv2.VideoCapture(self.device)
        if not cap.isOpened():
            print(f"[camera] no camera at {self.device}: no recording")
            return False
        cap.set(self.cv2.CAP_PROP_FRAME_WIDTH, self.size[0])
        cap.set(self.cv2.CAP_PROP_FRAME_HEIGHT, self.size[1])
        cap.set(self.cv2.CAP_PROP_FPS, self.fps)
        self.cap = cap
        return True

    def _writer(self, frame):
        self.out_dir.mkdir(parents=True, exist_ok=True)
        path = self.out_dir / f"jx0_{_stamp()}.mp4"
        h, w = frame.shape[:2]
        wr = self.cv2.VideoWriter(str(path), self.cv2.VideoWriter_fourcc(*"mp4v"), self.fps, (w, h))
        self.files.append(path)
        return wr

    def record(self, seconds: float | None = None):
        """Record until stop() (or for `seconds`), in segments of segment_s."""
        if self.cap is None and not self.open():
            return []
        t0 = seg0 = time.monotonic()
        wr = None
        dt = 1.0 / self.fps
        while not self._stop.is_set() and (seconds is None or time.monotonic() - t0 < seconds):
            ok, frame = self.cap.read()
            if not ok:
                time.sleep(dt)
                continue
            if wr is None or time.monotonic() - seg0 >= self.segment_s:
                if wr is not None:
                    wr.release()
                wr, seg0 = self._writer(frame), time.monotonic()
            wr.write(frame)
        if wr is not None:
            wr.release()
        return self.files

    def snapshot(self) -> Path | None:
        if self.cap is None and not self.open():
            return None
        for _ in range(5):                                 # let the exposure settle
            ok, frame = self.cap.read()
        if not ok:
            return None
        self.out_dir.mkdir(parents=True, exist_ok=True)
        path = self.out_dir / f"jx0_{_stamp()}.jpg"
        self.cv2.imwrite(str(path), frame)
        return path

    def start(self):
        self._thread = threading.Thread(target=self.record, daemon=True)
        self._thread.start()
        return self

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=3.0)
        if self.cap is not None:
            self.cap.release()
            self.cap = None


def main():
    from .robot import load_config
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=30.0)
    ap.add_argument("--snapshot", action="store_true")
    a = ap.parse_args()
    rec = Recorder(load_config())
    if a.snapshot:
        print(rec.snapshot())
    else:
        print("\n".join(str(p) for p in rec.record(a.seconds)))
    rec.stop()


if __name__ == "__main__":
    main()
