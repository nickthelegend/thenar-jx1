"""Build the HyperFrames composition for the JX1 assembly film from media/assembly/timeline.json.

The 3D footage (tools/media/assembly_film.py) carries the motion; this composition adds the titles in sync with it:
opening title (waterfall-entry), the "87 parts" explode beat, one step card per assembly step (lower-third revealed
with waterfall-entry, calm hold, quick fade), a build-progress bar (stat-bars-and-fills, scaleX fill), the finale and
walking titles, and a held end card (titlecard-reveal). Fonts are the renderer's bundled League Gothic (titles) and
IBM Plex Mono (specs/data).
Writes media/assembly-film/index.html and re-encodes the footage (1 s GOP) to media/assembly-film/assets/footage.mp4.
Usage: .venv/Scripts/python tools/media/build_assembly_composition.py
"""
from __future__ import annotations

import html
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TL = json.loads((ROOT / "media" / "assembly" / "timeline.json").read_text(encoding="utf-8"))
PROJ = ROOT / "media" / "assembly-film"
REPO_URL = "github.com/nickthelegend/thenar-jx1"


def section(step):
    return "LOWER BODY" if step <= 12 else ("TORSO + POWER" if step <= 15 else ("ARMS" if step <= 20 else "HEAD"))


def esc(s):
    return html.escape(s, quote=True)


def items(s):
    """A ' · '-separated spec line whose items never break inside (lines wrap only between items)."""
    return " &#183; ".join(f'<span class="nw">{esc(p)}</span>' for p in s.split(" · "))


def main():
    segs = TL["segments"]
    dur = TL["duration"]
    steps = [s for s in segs if s["kind"] == "step"]
    intro = next(s for s in segs if s["kind"] == "intro")
    explode = next(s for s in segs if s["kind"] == "explode")
    finale = next(s for s in segs if s["kind"] == "finale")
    walk = next((s for s in segs if s["kind"] == "walk"), None)
    p0, p1 = steps[0]["start"], steps[-1]["end"]
    end_card = round(dur - 2.4, 3)

    clips, js = [], []
    # ---------------------------------------------------------------- intro title
    d = intro["end"] - intro["start"]
    clips.append(f'''      <section id="intro" class="clip" data-start="{intro['start']}" data-duration="{d}" data-track-index="2">
        <div class="intro-wrap">
          <div class="mark"><span class="brand-dot"></span><span id="intro-jx1" class="wordmark">JX1</span></div>
          <p id="intro-l1" class="mono lead">A 1.23 M HUMANOID YOU CAN BUILD IN INDIA</p>
          <p id="intro-l2" class="mono small">{items("23 DOF · 33.6 KG · 21 ROBSTRIDE ACTUATORS · OPEN CAD, FEA, BOM, SIM")}</p>
        </div>
      </section>''')
    js.append(f'''      // intro — waterfall-entry (anchor wordmark, then two mono lines), fade out before the explode
      tl.set("#intro-jx1", {{ opacity: 1, y: 80 }}, 0.35);
      tl.to("#intro-jx1", {{ y: 0, duration: 0.2, ease: "power4.out" }}, 0.35);
      tl.set("#intro-l1", {{ opacity: 1, y: 45 }}, 0.55 + 2 / 60);
      tl.to("#intro-l1", {{ y: 0, duration: 0.15, ease: "power4.out" }}, 0.55 + 2 / 60);
      tl.set("#intro-l2", {{ opacity: 1, y: 40 }}, 0.70);
      tl.to("#intro-l2", {{ y: 0, duration: 0.14, ease: "power4.out" }}, 0.70);
      tl.to("#intro .intro-wrap", {{ opacity: 0, duration: 0.35, ease: "power2.in" }}, {intro['end'] - 0.45});''')
    # ---------------------------------------------------------------- explode beat
    d = explode["end"] - explode["start"]
    t = explode["start"]
    clips.append(f'''      <section id="explode" class="clip" data-start="{t}" data-duration="{d}" data-track-index="2">
        <div class="explode-wrap">
          <p id="ex-1" class="display big">87 PARTS.</p>
          <p id="ex-2" class="display big accent">LET&#8217;S BUILD IT.</p>
        </div>
      </section>''')
    js.append(f'''      // explode beat — waterfall-entry, second line one beat later
      tl.set("#ex-1", {{ opacity: 1, y: 70 }}, {t + 0.25});
      tl.to("#ex-1", {{ y: 0, duration: 0.18, ease: "power4.out" }}, {t + 0.25});
      tl.set("#ex-2", {{ opacity: 1, y: 70 }}, {t + 1.05});
      tl.to("#ex-2", {{ y: 0, duration: 0.18, ease: "power4.out" }}, {t + 1.05});
      tl.to("#explode .explode-wrap", {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, {explode['end'] - 0.35});''')
    # ---------------------------------------------------------------- step cards
    for s in steps:
        k, t, d = s["step"], s["start"], round(s["end"] - s["start"], 3)
        cid = f"step{k:02d}"
        clips.append(f'''      <section id="{cid}" class="clip step" data-start="{t}" data-duration="{d}" data-track-index="3">
        <div class="card">
          <p id="{cid}-k" class="mono kicker">STEP {k:02d} / {s['of']} &#183; {section(k)}</p>
          <p id="{cid}-t" class="display title{' long' if len(s['title']) > 24 else ''}">{esc(s['title'])}</p>
          <p id="{cid}-s" class="mono spec">{items(s['subtitle'])}</p>
        </div>
      </section>''')
        js.append(f'''      // step {k} — lower-third, waterfall-entry (kicker, title anchor, spec), hold, fade
      tl.set("#{cid}-k", {{ opacity: 1, y: 30 }}, {t + 0.15});
      tl.to("#{cid}-k", {{ y: 0, duration: 0.12, ease: "power4.out" }}, {t + 0.15});
      tl.set("#{cid}-t", {{ opacity: 1, y: 70 }}, {t + 0.25});
      tl.to("#{cid}-t", {{ y: 0, duration: 0.19, ease: "power4.out" }}, {t + 0.25});
      tl.set("#{cid}-s", {{ opacity: 1, y: 40 }}, {t + 0.45});
      tl.to("#{cid}-s", {{ y: 0, duration: 0.14, ease: "power4.out" }}, {t + 0.45});
      tl.to("#{cid} .card", {{ opacity: 0, duration: 0.22, ease: "power2.in" }}, {round(t + d - 0.28, 3)});''')
    # ---------------------------------------------------------------- build progress bar
    clips.append(f'''      <section id="progress" class="clip" data-start="{p0}" data-duration="{round(p1 - p0, 3)}" data-track-index="4">
        <div class="track"><div id="fill" class="fill"></div></div>
      </section>''')
    js.append(f'''      // build progress — stat-bars-and-fills progress fill (scaleX from the left), one notch per step
      tl.fromTo("#fill", {{ scaleX: 0 }}, {{ scaleX: 1 / {len(steps)}, duration: 0.6, ease: "power2.out" }}, {p0 + 1.2});''')
    for s in steps[1:]:
        js.append(f'''      tl.to("#fill", {{ scaleX: {s['step']} / {len(steps)}, duration: 0.6, ease: "power2.out" }}, {s['start'] + 1.2});''')
    # ---------------------------------------------------------------- finale + walk
    t, d = finale["start"], round(finale["end"] - finale["start"], 3)
    clips.append(f'''      <section id="finale" class="clip" data-start="{t}" data-duration="{d}" data-track-index="2">
        <div class="finale-wrap">
          <p id="fi-1" class="display huge">JX1 &#8212; ASSEMBLED</p>
          <p id="fi-2" class="mono lead">{items("1.23 m tall · 33.6 kg · 23 degrees of freedom")}</p>
          <p id="fi-3" class="mono lead">{items("12-DOF legs · 2-motor parallel ankles · 48 V CAN actuators")}</p>
          <p id="fi-4" class="mono lead">{items("Aluminium structure · every part FEA-checked")}</p>
        </div>
      </section>''')
    js.append(f'''      // finale — waterfall-entry, fade before the walk
      tl.set("#fi-1", {{ opacity: 1, y: 80 }}, {t + 1.2});
      tl.to("#fi-1", {{ y: 0, duration: 0.2, ease: "power4.out" }}, {t + 1.2});
      tl.set("#fi-2", {{ opacity: 1, y: 45 }}, {t + 1.42});
      tl.to("#fi-2", {{ y: 0, duration: 0.15, ease: "power4.out" }}, {t + 1.42});
      tl.set("#fi-3", {{ opacity: 1, y: 45 }}, {t + 1.55});
      tl.to("#fi-3", {{ y: 0, duration: 0.15, ease: "power4.out" }}, {t + 1.55});
      tl.set("#fi-4", {{ opacity: 1, y: 45 }}, {t + 1.68});
      tl.to("#fi-4", {{ y: 0, duration: 0.15, ease: "power4.out" }}, {t + 1.68});
      tl.to("#finale .finale-wrap", {{ opacity: 0, duration: 0.3, ease: "power2.in" }}, {round(finale['end'] - 0.35, 3)});''')
    if walk:
        t = walk["start"]
        d = round(end_card - t, 3)
        clips.append(f'''      <section id="walk" class="clip" data-start="{t}" data-duration="{d}" data-track-index="2">
        <div class="walk-wrap">
          <p id="wa-1" class="display big accent">AND IT WALKS.</p>
          <p id="wa-2" class="mono spec">{items("MuJoCo simulation of the CAD model · ZMP gait · 0.52 m/s")}</p>
        </div>
      </section>''')
        js.append(f'''      // walk title — waterfall-entry
      tl.set("#wa-1", {{ opacity: 1, y: 70 }}, {t + 1.0});
      tl.to("#wa-1", {{ y: 0, duration: 0.18, ease: "power4.out" }}, {t + 1.0});
      tl.set("#wa-2", {{ opacity: 1, y: 40 }}, {t + 1.2});
      tl.to("#wa-2", {{ y: 0, duration: 0.14, ease: "power4.out" }}, {t + 1.2});''')
    # ---------------------------------------------------------------- end card
    clips.append(f'''      <section id="endcard" class="clip" data-start="{end_card}" data-duration="{round(dur - end_card, 3)}" data-track-index="5">
        <div id="end-bg" class="end-bg"></div>
        <div class="end-wrap">
          <div class="mark center"><span class="brand-dot"></span><span id="end-jx1" class="wordmark">JX1</span></div>
          <p id="end-url" class="mono url">{REPO_URL}</p>
          <p id="end-sub" class="mono small">CAD &#183; FEA &#183; BOM &#183; SIMULATION &#183; RL &#8212; all open. Build one.</p>
        </div>
      </section>''')
    js.append(f'''      // end card — titlecard-reveal: one restrained move (slide-up crossfade), then a still hold
      tl.fromTo("#end-bg", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.45, ease: "power2.out" }}, {end_card});
      tl.fromTo("#endcard .end-wrap", {{ opacity: 0, y: 30 }}, {{ opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }}, {end_card + 0.2});''')

    doc = f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <title>JX1 assembly</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: #05070a; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; color: #f2f4f7; }}
      #footage {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
      .shade {{ position: absolute; inset: 0; pointer-events: none;
        background: linear-gradient(90deg, rgba(3,5,8,0.72) 0%, rgba(3,5,8,0.30) 34%, rgba(3,5,8,0) 55%),
                    linear-gradient(0deg, rgba(3,5,8,0.70) 0%, rgba(3,5,8,0) 38%); }}
      .clip {{ position: absolute; inset: 0; }}
      .display {{ font-family: "League Gothic", sans-serif; font-weight: 400; letter-spacing: 0.01em; line-height: 0.95; }}
      .mono {{ font-family: "IBM Plex Mono", monospace; font-weight: 400; letter-spacing: 0.02em; }}
      .accent {{ color: #3cc8ff; }}
      .nw {{ white-space: nowrap; }}
      .display, .mono {{ text-shadow: 0 2px 16px rgba(2,4,7,0.6); }}
      .intro-wrap, .explode-wrap, .finale-wrap, .walk-wrap {{ position: absolute; left: 110px; top: 300px; width: 700px; }}
      .walk-wrap {{ top: 120px; }}
      .finale-wrap {{ top: 120px; width: 720px; }}
      .mark {{ display: flex; align-items: center; gap: 28px; }}
      .mark.center {{ justify-content: center; }}
      .brand-dot {{ display: block; width: 46px; height: 46px; background: #f26b1d; border-radius: 6px; }}
      .wordmark {{ display: inline-block; font-family: "League Gothic", sans-serif; font-size: 260px; line-height: 0.9; opacity: 0; }}
      .lead {{ font-size: 25px; line-height: 1.45; color: #dfe5ec; margin-top: 18px; opacity: 0; }}
      .small {{ font-size: 20px; line-height: 1.5; color: #aeb7c4; margin-top: 14px; opacity: 0; }}
      .big {{ font-size: 136px; opacity: 0; }}
      .huge {{ font-size: 124px; opacity: 0; }}
      .explode-wrap .big + .big {{ margin-top: 8px; }}
      .card {{ position: absolute; left: 96px; bottom: 118px; width: 980px; }}
      .kicker {{ font-size: 24px; color: #3cc8ff; letter-spacing: 0.08em; opacity: 0; }}
      .title {{ font-size: 112px; margin-top: 10px; opacity: 0; }}
      .title.long {{ font-size: 92px; }}
      .spec {{ font-size: 27px; line-height: 1.45; color: #d2d9e2; margin-top: 12px; opacity: 0; }}
      .walk-wrap .spec {{ margin-top: 18px; font-size: 24px; }}
      .track {{ position: absolute; left: 96px; right: 96px; bottom: 64px; height: 6px; background: rgba(255,255,255,0.14);
        border-radius: 3px; overflow: hidden; }}
      .fill {{ width: 100%; height: 100%; background: #3cc8ff; transform-origin: 0 50%; }}
      .end-bg {{ position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 50%, rgba(8,11,16,0.92) 0%, rgba(3,5,8,0.97) 70%); }}
      .end-wrap {{ position: absolute; left: 0; right: 0; top: 330px; text-align: center; }}
      .end-wrap .wordmark {{ opacity: 1; font-size: 220px; }}
      .url {{ font-size: 40px; color: #3cc8ff; margin-top: 24px; }}
      .end-wrap .small {{ opacity: 1; font-size: 26px; margin-top: 18px; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1920" data-height="1080">
      <video id="footage" class="clip-media" src="assets/footage.mp4" data-start="0" data-duration="{dur}" data-track-index="0" muted playsinline></video>
      <div class="shade"></div>
{chr(10).join(clips)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
    (PROJ / "index.html").write_text(doc, encoding="utf-8")
    (PROJ / "assets").mkdir(exist_ok=True)
    src = ROOT / "media" / "assembly" / "footage.mp4"
    dst = PROJ / "assets" / "footage.mp4"
    if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
        # re-encode with a 1 s GOP: HyperFrames seeks the footage frame by frame (sparse keyframes freeze on seek)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                        "-pix_fmt", "yuv420p", "-r", "30", "-g", "30", "-keyint_min", "30", "-movflags", "+faststart", "-an", str(dst)],
                       check=True)
    print(f"wrote {PROJ / 'index.html'} ({len(steps)} steps, {dur} s)")


if __name__ == "__main__":
    main()
