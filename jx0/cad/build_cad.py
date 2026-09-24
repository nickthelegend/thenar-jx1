"""Build the JX0 parts in SolidWorks from jx0/cad/geometry.py (native parametric features in the dedicated JX session).

Every primitive becomes an offset reference plane + a fully defined sketch + an extrude / cut, so the feature tree reads
like a hand-built part. Each part is checked (bounding box against the geometry, rebuild errors, solid body count),
saved to jx0/cad/parts/<name>.SLDPRT, exported to jx0/cad/stl/<name>.stl (millimetres, link frame) and summarised in
jx0/cad/parts/index.json (volume, printed-mass estimate).
Usage: .venv/Scripts/python jx0/cad/build_cad.py [PartName ...] [--slow]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "cad"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from swlib.core import C, Session, set_view, typed  # noqa: E402
from swlib.part import MM, Part  # noqa: E402
import geometry as G  # noqa: E402

PARTS_DIR = ROOT / "jx0" / "cad" / "parts"
STL_DIR = ROOT / "jx0" / "cad" / "stl"
COLOURS = {"white": (0.92, 0.92, 0.94), "orange": (0.95, 0.42, 0.11), "black": (0.12, 0.12, 0.14), "blue": (0.15, 0.3, 0.75)}
BASE = {"z": ("Front Plane", "XY"), "y": ("Top Plane", "XZ"), "x": ("Right Plane", "YZ")}
PETG_DENSITY = 1270.0          # kg/m^3
PRINT_FILL = 0.55              # printed mass / solid mass (3 walls + 25 % gyroid on these small parts, ESTIMATED)


class Builder:
    def __init__(self, part: Part, slow=False):
        self.p, self.planes, self.n, self.slow = part, {}, 0, slow

    def plane(self, axis, offset_mm):
        base, key = BASE[axis]
        if abs(offset_mm) < 1e-6:
            return base, key
        name = f"P{axis.upper()}_{offset_mm:+.3f}".replace(".", "_").replace("-", "m").replace("+", "p")
        if name not in self.planes:
            self.p.ref_plane_offset(base, abs(offset_mm) * MM, name, flip=offset_mm < 0)
            self.planes[name] = True
        return name, key

    def _uv(self, key, x, y, z):
        from swlib.part import to_uv
        return to_uv(key, (x * MM, y * MM, z * MM))

    def feature(self, prim):
        self.n += 1
        kind = prim[0]
        tag = f"{kind}{self.n}"
        if kind in ("box", "cut"):
            (x0, x1), (y0, y1), (z0, z1) = prim[1], prim[2], prim[3]
            pname, key = self.plane("z", z0)
            with self.p.sketch(key, f"S_{tag}", plane_name=pname) as sk:
                u0, v0 = self._uv(key, x0, y0, z0)
                u1, v1 = self._uv(key, x1, y1, z0)
                sk.rect(min(u0, u1), min(v0, v1), max(u0, u1), max(v0, v1))
            depth = (z1 - z0) * MM
            if kind == "box":
                self.extrude(f"S_{tag}", depth, f"Boss_{self.n}")
            else:
                # SolidWorks' blind cut defaults to the opposite side of the sketch normal from an extrude: reverse it
                self.p.cut(f"S_{tag}", depth, f"Pocket_{self.n}", reverse=True)
        else:
            _, axis, c, r, (s0, s1) = prim
            pname, key = self.plane(axis, s0)
            pt = {"x": (s0, c[0], c[1]), "y": (c[0], s0, c[1]), "z": (c[0], c[1], s0)}[axis]
            u, v = self._uv(key, *pt)
            rad = r if kind == "cyl" else r / 2
            with self.p.sketch(key, f"S_{tag}", plane_name=pname) as sk:
                sk.circle(u, v, rad * MM)
            depth = (s1 - s0) * MM
            if kind == "cyl":
                self.extrude(f"S_{tag}", depth, f"Boss_{self.n}")
            else:
                self.p.cut(f"S_{tag}", depth, f"Hole_{self.n}", reverse=True)
        if self.slow:
            self.p.doc.ViewZoomtofit2()

    def extrude(self, sketch, depth, name):
        try:
            return self.p.extrude(sketch, depth, name)
        except RuntimeError:
            # a start face exactly on an existing face can make a merged boss fail: build it as its own body
            return self.p.extrude(sketch, depth, name, merge=False)


def build_part(s: Session, name, prims, colour, slow=False):
    part = Part(s, name, PARTS_DIR / f"{name}.SLDPRT")
    part.gv("plate_t", G.T)
    part.gv("clearance", G.C)
    b = Builder(part, slow)
    first = True
    # bosses first, then pockets and holes (so every cut sees the finished solid)
    for prim in [q for q in prims if q[0] in ("box", "cyl")] + [q for q in prims if q[0] in ("cut", "hole")]:
        b.feature(prim)
        if first:
            set_view(s.app, part.doc, eye=(1.0, -0.8, 0.6))
            first = False
    part.color(COLOURS[colour])
    part.prop("Material", "PETG (printed)" if colour in ("white", "orange") else "stand-in")
    part.prop("Project", "JX0")
    part.rebuild()
    set_view(s.app, part.doc, eye=(1.0, -0.8, 0.6))
    bb = part.bbox()
    lo, hi = G.bbox(prims)
    got = [round(v / MM, 2) for v in bb] if bb else None
    want = [round(v, 2) for v in lo + hi]
    ok_bbox = got is not None and all(abs(a - w) < 0.05 for a, w in zip(got, want))
    tris = export_stl(part, STL_DIR / f"{name}.stl")
    info = part.save(close=False)
    mp = info["mass"] or {}
    vol_cm3 = (mp.get("volume_m3", 0.0) or 0.0) * 1e6
    rec = {"part": name, "bodies": info["bodies"], "errors": info["errors"], "bbox_mm": got, "bbox_expected_mm": want,
           "bbox_ok": ok_bbox, "volume_cm3": round(vol_cm3, 2), "solid_mass_g_petg": round(vol_cm3 * PETG_DENSITY / 1000, 1),
           "printed_mass_g": round(vol_cm3 * PETG_DENSITY / 1000 * PRINT_FILL, 1), "features": b.n, "triangles": tris,
           "com_mm": [round(v / MM, 2) for v in mp.get("com_m", [0, 0, 0])]}
    return part, rec


def export_stl(part: Part, path: Path) -> int:
    import trimesh
    from export_meshes import body_triangles
    bodies = typed(part.doc, "IPartDoc").GetBodies2(C.swSolidBody, False) or []
    tris = [body_triangles(b)[0] for b in bodies]
    tris = np.concatenate(tris) if tris else np.zeros((0, 3, 3))
    mesh = trimesh.Trimesh(vertices=(tris.reshape(-1, 3) / MM), faces=np.arange(len(tris) * 3).reshape(-1, 3), process=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    mesh.export(path)
    return int(len(mesh.faces))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--slow", action="store_true", help="zoom to fit after every feature (nicer screen recording)")
    ap.add_argument("--keep-open", type=int, default=3, help="leave the last N parts open")
    a = ap.parse_args()
    catalogue = {**G.PARTS, **G.SERVOS}
    names = a.names or list(catalogue)
    s = Session()
    PARTS_DIR.mkdir(parents=True, exist_ok=True)
    index_path = PARTS_DIR / "index.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {}
    opened = []
    for name in names:
        prims, colour, qty = catalogue[name]
        t0 = time.time()
        part, rec = build_part(s, name, prims, colour, slow=a.slow)
        rec["quantity"] = qty
        rec["build_s"] = round(time.time() - t0, 1)
        index[name] = rec
        index_path.write_text(json.dumps(index, indent=1), encoding="utf-8")
        print(f"{name:26s} {rec['features']:3d} features  bodies {rec['bodies']}  bbox {'OK' if rec['bbox_ok'] else 'MISMATCH ' + str(rec['bbox_mm'])}  "
              f"errors {rec['errors'] or 'none'}  {rec['printed_mass_g']} g printed  {rec['build_s']} s", flush=True)
        opened.append(part)
        while len(opened) > a.keep_open:
            s.close(opened.pop(0).doc)


if __name__ == "__main__":
    main()
