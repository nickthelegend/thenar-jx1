"""Screen recorder for CAD timelapses (Windows, ffmpeg gdigrab).

Records one monitor at a low frame rate into a Matroska file (still playable if the recorder is killed), and on a
clean stop remuxes it to MP4. Stop it by creating the stop file (`--stop` does that), or with Ctrl+C.
  start: .venv/Scripts/python tools/media/screen_record.py --out media/timelapse/jx0_solidworks.mkv
  stop : .venv/Scripts/python tools/media/screen_record.py --stop
Timelapse later: ffmpeg -i jx0_solidworks.mp4 -vf "setpts=PTS/20" -an jx0_solidworks_20x.mp4
"""
from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STOP_FILE = ROOT / "media" / "timelapse" / ".stop_recording"


def record(out: Path, fps: int, region: tuple[int, int, int, int]):
    out.parent.mkdir(parents=True, exist_ok=True)
    STOP_FILE.unlink(missing_ok=True)
    x, y, w, h = region
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "gdigrab", "-framerate", str(fps), "-draw_mouse", "1",
           "-offset_x", str(x), "-offset_y", str(y), "-video_size", f"{w}x{h}", "-i", "desktop",
           "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26", "-pix_fmt", "yuv420p", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    print(f"recording {w}x{h}+{x}+{y} at {fps} fps -> {out} (pid {proc.pid})", flush=True)
    try:
        while proc.poll() is None and not STOP_FILE.exists():
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    if proc.poll() is None:
        proc.stdin.write(b"q")              # ffmpeg finishes the file cleanly on 'q'
        proc.stdin.flush()
        try:
            proc.wait(timeout=60)
        except subprocess.TimeoutExpired:
            proc.kill()
    STOP_FILE.unlink(missing_ok=True)
    mp4 = out.with_suffix(".mp4")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(out), "-c", "copy", "-movflags", "+faststart",
                    str(mp4)], check=False)
    print(f"stopped; {mp4} ({mp4.stat().st_size / 1e6:.1f} MB)" if mp4.exists() else "stopped (remux failed; the .mkv is kept)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "media" / "timelapse" / "jx0_solidworks.mkv"))
    ap.add_argument("--fps", type=int, default=4)
    ap.add_argument("--region", default="0,0,1920,1080", help="x,y,w,h of the monitor to record")
    ap.add_argument("--stop", action="store_true", help="ask a running recorder to stop")
    a = ap.parse_args()
    if a.stop:
        STOP_FILE.parent.mkdir(parents=True, exist_ok=True)
        STOP_FILE.write_text("stop")
        print("stop requested")
        return
    record(Path(a.out), a.fps, tuple(int(v) for v in a.region.split(",")))


if __name__ == "__main__":
    main()
