"""Engrave the JX0 lettering into the printed parts' outer faces (0.6 mm deep, 3 layers):

    python jx0/cad/engrave.py         jx0/cad/stl/<part>.stl -> jx0/cad/stl_engraved/<part>.stl (+ engrave.json)

Only the body shell and the arms carry text; the leg parts and the pelvis take the walking loads (verify_fea) and stay
plain. Each line of text is checked: every letter lies on solid plastic (the cut removes exactly its area x depth),
with at least BEHIND mm of wall left under it, and the part is still one body. The SolidWorks parts stay plain;
the print plates (tools/print/make_plates.py) and the renders use these meshes; the renders also show the letters
filled with paint (stl_engraved/inlay/<part>.stl).
Font: DejaVu Sans Bold (bundled with matplotlib, free licence).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import trimesh
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from manifold3d import CrossSection, FillRule, Manifold, Mesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import geometry as G  # noqa: E402

SRC, OUT = HERE / "stl", HERE / "stl_engraved"
DEPTH = 0.4                     # mm, 2 layers of 0.2: crisp, not deep
BEHIND = 1.2                    # mm of wall that must stay under the letters
INLAY = 0.25                    # the paint in the letters, for the renders: inlay/<part>.stl, the bottom 0.25 mm
FONT = FontProperties(family="DejaVu Sans", weight="bold")

TD, TW, TCH, TZS, TZT, CH = G.TD, G.TW, G.TCH, G.TZS, G.TZT, G.TOP_CH
FRONT, BACK = (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0)
UP = (0.0, 0.0, 1.0)

# part -> lines of (text, cap height mm, centre of the line on the face, outward normal, the text's up direction)
# Premium and quiet: one small, widely spaced mark on the chest; the rest is a small nameplate on the back. Letters are
# left in the body colour (tone on tone). Entries: (text, cap height mm, centre, outward normal, up, tracking) - tracking
# = extra space between letters in cap heights; text "[frame W H]" is a nameplate outline (W x H mm, 0.8 mm line).
NAMEPLATE_Z = 140.0
TEXT = {
    "JX0_Torso": [("JX0", 9.0, (TD, 0.0, 176.0), FRONT, UP, 0.9),
                  ("[frame 62 27]", 0.0, (-TD, 0.0, NAMEPLATE_Z), BACK, UP, 0.0),
                  ("JNTUH'S 1ST", 3.4, (-TD, 0.0, NAMEPLATE_Z + 7.0), BACK, UP, 0.15),
                  ("HUMANOID ROBOT", 3.4, (-TD, 0.0, NAMEPLATE_Z), BACK, UP, 0.12),
                  ("THENAR.IO", 2.8, (-TD, 0.0, NAMEPLATE_Z - 7.5), BACK, UP, 0.5)],
}


def text_section(text, cap, tracking=0.0):
    """The text as a 2D cross-section (mm), its cap height = cap, centred on (0, 0); tracking = extra space between the
    letters in cap heights. "[frame W H]": a W x H mm rounded nameplate outline, 0.8 mm wide."""
    if text.startswith("[frame"):
        w, h = (float(v) for v in text.strip("[]").split()[1:3])
        return _rrect(w, h, 3.0) - _rrect(w - 1.6, h - 1.6, 2.2), (w, h)
    ref = TextPath((0, 0), "H", size=100.0, prop=FONT).get_extents()
    scale = cap / ref.height
    polys, x = [], 0.0
    for ch in text:                                        # letter by letter, so the spacing can open up
        if ch == " ":                                      # (TextPath has no outline for a space)
            x += 0.32 * 100.0 + tracking * ref.height
            continue
        tp = TextPath((x, 0), ch, size=100.0, prop=FONT)
        polys += [np.asarray(q) * scale for q in tp.to_polygons() if len(q) >= 3]
        adv = TextPath((0, 0), ch + "|", size=100.0, prop=FONT).get_extents().x1 - TextPath((0, 0), "|", size=100.0, prop=FONT).get_extents().x1
        x += adv + tracking * ref.height
    allp = np.vstack(polys)
    lo, hi = allp.min(axis=0), allp.max(axis=0)
    c = (lo + hi) / 2
    polys = [[(float(px - c[0]), float(py - c[1])) for px, py in q] for q in polys]
    return CrossSection(polys, FillRule.EvenOdd), tuple(float(v) for v in hi - lo)


def _rrect(w, h, r, n=10):
    pts = []
    for cx, cy, a0 in ((w / 2 - r, h / 2 - r, 0), (-w / 2 + r, h / 2 - r, 90), (-w / 2 + r, -h / 2 + r, 180), (w / 2 - r, -h / 2 + r, 270)):
        for k in range(n + 1):
            t = np.radians(a0 + 90 * k / n)
            pts.append((cx + r * np.cos(t), cy + r * np.sin(t)))
    return CrossSection([pts], FillRule.EvenOdd)


def cutter(section, depth, centre, normal, up, start=-0.5):
    """The text as a solid from start mm under the face (negative: outside it) to depth mm under it."""
    n, v = np.asarray(normal, float), np.asarray(up, float)
    u = np.cross(v, n)                                       # read from outside: u x v = n
    solid = Manifold.extrude(section, depth - start)
    o = np.asarray(centre, float) - start * n                # local (x, y, z) -> u, v, -n
    M = np.column_stack([u, v, -n, o])                      # 3 x 4
    return solid.transform(M.tolist())


def to_mf(t):
    return Manifold(Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))


def to_tm(m):
    mm = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts))


def main():
    (OUT / "inlay").mkdir(parents=True, exist_ok=True)
    report, bad = {}, 0
    for stl in sorted(SRC.glob("JX0_*.stl")):
        name = stl.stem
        mesh = trimesh.load(stl)
        if name not in TEXT:
            mesh.export(OUT / stl.name)
            continue
        part = to_mf(mesh)
        rows, inlay = [], Manifold()
        for text, cap, centre, normal, up, tracking in TEXT[name]:
            v0 = part.volume()
            sec, (w, h) = text_section(text, cap, tracking)
            area = sec.area()
            removed = v0 - (part - cutter(sec, DEPTH, centre, normal, up)).volume()
            deep = v0 - (part - cutter(sec, DEPTH + BEHIND, centre, normal, up)).volume()
            problems = []
            if abs(removed - area * DEPTH) > 0.03 * area * DEPTH:
                problems.append(f"cuts {removed:.1f} mm3, expected {area * DEPTH:.1f}: off the face or over a hole")
            if deep < 0.98 * area * (DEPTH + BEHIND):
                problems.append(f"less than {BEHIND} mm of wall under the letters")
            rows.append(dict(text=text, cap_mm=cap, size_mm=[round(w, 1), round(h, 1)], area_mm2=round(area, 1),
                             removed_mm3=round(removed, 1), problems=problems))
            part = part - cutter(sec, DEPTH, centre, normal, up)
            inlay = inlay + cutter(sec, DEPTH, centre, normal, up, start=DEPTH - INLAY)
            bad += len(problems)
            print(f"{name:16s} {text!r:18s} {w:5.1f} x {h:4.1f} mm  {'; '.join(problems) or 'OK'}")
        out = to_tm(part)
        pieces = len(out.split(only_watertight=False))
        if pieces != 1:
            rows.append(dict(problems=[f"{pieces} bodies after engraving"]))
            bad += 1
        out.export(OUT / stl.name)
        to_tm(inlay).export(OUT / "inlay" / stl.name)
        report[name] = rows
    (OUT / "engrave.json").write_text(json.dumps(dict(depth_mm=DEPTH, wall_behind_mm=BEHIND, parts=report,
                                                       problems=bad), indent=1), encoding="utf-8")
    print(f"engraving: {bad} problems -> {OUT.relative_to(HERE.parents[1])}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
