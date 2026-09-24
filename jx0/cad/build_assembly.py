"""Assemble JX0 in SolidWorks at its zero pose: every printed part in its link frame and a servo stand-in at every joint.

The link frames are those of the simulation model (jx0/sim/jx0_model.py): hip centres at y = +-45 mm, knee 100 mm
and ankle 200 mm below them; arms and head from jx0/cad/geometry.py. Components are placed by transform (no mates yet)
and the assembly is checked for interferences between parts that are not bolted together.
Output: jx0/cad/JX0_Robot.SLDASM, jx0/cad/assembly.json (component poses, interference report), images.
Usage: .venv/Scripts/python jx0/cad/build_assembly.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "cad"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from swlib.core import Session, save_as, set_mmgs, set_view, typed  # noqa: E402
from build_leg_assembly import sw_transform  # noqa: E402
import geometry as G  # noqa: E402
from layout import components  # noqa: E402

PARTS = ROOT / "jx0" / "cad" / "parts"
OUT = ROOT / "jx0" / "cad" / "JX0_Robot.SLDASM"
MM = 1e-3


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default=None, help="folder for a PNG of the assembly after every component (timelapse)")
    a = ap.parse_args()
    from build_cad import FrameGrabber
    s = Session()
    frames = FrameGrabber(s, a.frames)
    doc = s.new_doc("assembly")
    set_mmgs(doc)
    save_as(doc, OUT)
    A = typed(doc, "IAssemblyDoc")
    placed = []
    for key, part, M in components():
        path = (PARTS / f"{part}.SLDPRT").resolve()
        s.open_doc(path)
        s.activate(doc)
        c = A.AddComponent5(str(path), 0, "", False, "", float(M[0, 3]), float(M[1, 3]), float(M[2, 3]))
        if c is None:
            raise RuntimeError(f"AddComponent5 failed for {part}")
        c = typed(c, "IComponent2")
        c.Transform2 = sw_transform(s, M)
        placed.append({"key": key, "part": part, "name": c.Name2, "pose_mm": (M[:3, 3] / MM).round(3).tolist(),
                       "R": M[:3, :3].round(6).tolist()})
        s.close(path.name)
        print(f"placed {key:26s} {part}", flush=True)
        if frames.dir:
            frames.grab(doc, eye=(1.0, -0.8, 0.45))
        elif len(placed) % 6 == 0:
            set_view(s.app, doc, eye=(1.0, -0.8, 0.45))
    doc.ForceRebuild3(False)
    set_view(s.app, doc, eye=(1.0, -0.8, 0.45))
    save_as(doc, OUT)
    if frames.dir:                                      # a slow turn around the finished robot
        import math
        for k in range(48):
            a_ = 2 * math.pi * k / 48
            frames.grab(doc, eye=(math.cos(a_ - 0.67), math.sin(a_ - 0.67), 0.45))
    (ROOT / "jx0" / "cad" / "assembly.json").write_text(json.dumps({"assembly": str(OUT.relative_to(ROOT)).replace("\\", "/"),
                                                                     "components": placed}, indent=1), encoding="utf-8")
    print(f"saved {OUT.relative_to(ROOT)} with {len(placed)} components")


if __name__ == "__main__":
    main()
