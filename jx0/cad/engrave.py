"""Engrave the JX0 lettering into the printed parts' outer faces (0.6 mm deep, 3 layers):

    python jx0/cad/engrave.py         jx0/cad/stl/<part>.stl -> jx0/cad/stl_engraved/<part>.stl (+ engrave.json)

Only the body shell and the arms carry text; the leg parts and the pelvis take the walking loads (verify_fea) and stay
plain. Each line of text is checked: every letter lies on solid plastic (the cut removes exactly its area x depth),
with at least BEHIND mm of wall left under it, and the part is still one body. The SolidWorks parts stay plain;
the print plates (tools/print/make_plates.py) and the renders use these meshes.
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
DEPTH = 0.6                     # mm, 3 layers of 0.2
BEHIND = 1.2                    # mm of wall that must stay under the letters
FONT = FontProperties(family="DejaVu Sans", weight="bold")

TD, TW, TCH, TZS, TZT, CH = G.TD, G.TW, G.TCH, G.TZS, G.TZT, G.TOP_CH
FRONT, BACK = (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0)
UP = (0.0, 0.0, 1.0)

# part -> lines of (text, cap height mm, centre of the line on the face, outward normal, the text's up direction)
TEXT = {
    "JX0_Torso": [("JX0", 30.0, (TD, 0.0, 128.0), FRONT, UP),
                  ("JNTUH's 1st", 6.5, (TD, 0.0, 96.0), FRONT, UP),
                  ("Humanoid Robot", 6.5, (TD, 0.0, 85.0), FRONT, UP),
                  ("thenar.io", 9.0, (-TD, 0.0, 122.0), BACK, UP),
                  ("JX0", 14.0, (-TD, 0.0, 56.0), BACK, UP)],
    "JX0_ChestCap": [("thenar.io", 8.0, (TD, 0.0, (TZS + TZT - CH) / 2 - 2.0), FRONT, UP)],
    # the blades hang down from the elbow: on both the text runs up the blade, from the hand to the elbow
    "JX0_ArmBlade_L": [("JX0", 13.0, (1.0, G.BLADE_T, -58.0), (0.0, 1.0, 0.0), (1.0, 0.0, 0.0))],
    "JX0_ArmBlade_R": [("JX0", 13.0, (1.0, -G.BLADE_T, -58.0), (0.0, -1.0, 0.0), (-1.0, 0.0, 0.0))],
}


def text_section(text, cap):
    """The text as a 2D cross-section (mm), its cap height = cap, centred on (0, 0)."""
    ref = TextPath((0, 0), "H", size=100.0, prop=FONT).get_extents()
    scale = cap / ref.height
    tp = TextPath((0, 0), text, size=100.0, prop=FONT)
    polys = [np.asarray(p) * scale for p in tp.to_polygons() if len(p) >= 3]
    ext = tp.get_extents()
    cx, cy = (ext.x0 + ext.x1) / 2 * scale, (ext.y0 + ext.y1) / 2 * scale
    polys = [[(float(x - cx), float(y - cy)) for x, y in p] for p in polys]
    return CrossSection(polys, FillRule.EvenOdd), (ext.width * scale, ext.height * scale)


def cutter(section, depth, centre, normal, up):
    """The text pushed depth mm into the face (from 0.5 mm outside it)."""
    n, v = np.asarray(normal, float), np.asarray(up, float)
    u = np.cross(v, n)                                       # read from outside: u x v = n
    solid = Manifold.extrude(section, depth + 0.5)           # z 0 .. depth + 0.5
    # local (x, y, z) -> u, v, -n; origin 0.5 mm outside the face
    o = np.asarray(centre, float) + 0.5 * n
    M = np.column_stack([u, v, -n, o])                      # 3 x 4
    return solid.transform(M.tolist())


def to_mf(t):
    return Manifold(Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))


def to_tm(m):
    mm = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts))


def main():
    OUT.mkdir(exist_ok=True)
    report, bad = {}, 0
    for stl in sorted(SRC.glob("JX0_*.stl")):
        name = stl.stem
        mesh = trimesh.load(stl)
        if name not in TEXT:
            mesh.export(OUT / stl.name)
            continue
        part = to_mf(mesh)
        rows = []
        for text, cap, centre, normal, up in TEXT[name]:
            v0 = part.volume()
            sec, (w, h) = text_section(text, cap)
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
            bad += len(problems)
            print(f"{name:16s} {text!r:18s} {w:5.1f} x {h:4.1f} mm  {'; '.join(problems) or 'OK'}")
        out = to_tm(part)
        pieces = len(out.split(only_watertight=False))
        if pieces != 1:
            rows.append(dict(problems=[f"{pieces} bodies after engraving"]))
            bad += 1
        out.export(OUT / stl.name)
        report[name] = rows
    (OUT / "engrave.json").write_text(json.dumps(dict(depth_mm=DEPTH, wall_behind_mm=BEHIND, parts=report,
                                                       problems=bad), indent=1), encoding="utf-8")
    print(f"engraving: {bad} problems -> {OUT.relative_to(HERE.parents[1])}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
