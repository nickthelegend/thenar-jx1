"""Export every JX1 part to STL (part frame, millimetres) for the simulation pipeline.

Output: simulation/meshes/source_mm/<PartName>.STL (+ index.json with SolidWorks mass-property volumes / COMs).
Triangles come straight from the B-rep tessellation via the API (IFace2.GetTessTriangles, ITessellation fallback),
so the mesh is guaranteed to be in the part (= robot link / actuator) frame and no SolidWorks system options
(e.g. STL "translate to positive space", which is registry-persistent) are changed.

Usage: .venv/Scripts/python tools/cad/export_meshes.py [PartStem ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from swlib.core import C, Session, typed  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "simulation" / "meshes" / "source_mm"


def _tess_fallback(body):
    """Explicit ITessellation of one body (used when display tessellation is unavailable)."""
    t = typed(body.GetTessellation(None), "ITessellation")
    t.NeedFaceFacetMap = True
    t.NeedVertexParams = False
    t.NeedVertexNormal = False
    t.ImprovedQuality = True
    t.CurveChordTolerance = 0.0001
    t.CurveChordAngleTolerance = 0.1
    t.SurfacePlaneTolerance = 0.0001
    t.SurfacePlaneAngleTolerance = 0.1
    t.MatchType = 0
    if not t.Tessellate():
        raise RuntimeError("ITessellation.Tessellate failed")
    tris = []
    for f in body.GetFaces() or []:
        for fid in t.GetFaceFacets(f) or []:
            fins = t.GetFacetFins(fid)
            tris.append([t.GetVertexPoint(t.GetFinVertices(fin)[0]) for fin in fins])
    return np.asarray(tris, float).reshape(-1, 3, 3)


def body_triangles(body):
    body = typed(body, "IBody2")
    chunks = []
    for f in body.GetFaces() or []:
        tri = typed(f, "IFace2").GetTessTriangles(True)
        if tri is None:
            return _tess_fallback(body), "itessellation"
        chunks.append(np.asarray(tri, float).reshape(-1, 3, 3))
    return (np.concatenate(chunks) if chunks else np.zeros((0, 3, 3))), "display"


def main():
    only = set(sys.argv[1:])
    s = Session()
    OUT.mkdir(parents=True, exist_ok=True)
    parts = sorted(p for p in (ROOT / "CAD").rglob("*.SLDPRT") if "_scratch" not in p.parts and not p.name.startswith("~$")
                   and (not only or p.stem in only))
    idx_path = OUT / "index.json"
    index = json.loads(idx_path.read_text()) if idx_path.exists() else {}
    for p in parts:
        doc = s.open_doc(p)
        part = typed(doc, "IPartDoc")
        tris, how = [], set()
        for b in part.GetBodies2(C.swSolidBody, True) or []:
            t, h = body_triangles(b)
            tris.append(t)
            how.add(h)
        V = np.concatenate(tris) * 1000.0                        # m -> mm, part frame
        mesh = trimesh.Trimesh(vertices=V.reshape(-1, 3), faces=np.arange(len(V) * 3).reshape(-1, 3), process=True)
        mesh.merge_vertices()
        out = OUT / (p.stem + ".STL")
        mesh.export(out)
        ext = typed(doc.Extension, "IModelDocExtension")
        mp = typed(ext.CreateMassProperty(), "IMassProperty")
        mp.UseSystemUnits = True
        vol_sw = mp.Volume
        vol_mesh = mesh.volume * 1e-9 if mesh.is_watertight else None
        index[p.stem] = {"cad": p.relative_to(ROOT).as_posix(), "stl": out.relative_to(ROOT).as_posix(), "triangles": len(mesh.faces),
                         "tessellation": sorted(how), "watertight": bool(mesh.is_watertight), "sw_volume_m3": vol_sw,
                         "mesh_volume_m3": vol_mesh, "sw_com_m": list(mp.CenterOfMass),
                         "mesh_bounds_mm": np.round(mesh.bounds, 3).tolist()}
        err = f"{abs(vol_mesh - vol_sw) / vol_sw * 100:.2f} %" if vol_mesh else "n/a (not watertight)"
        print(f"{p.stem:28s} {len(mesh.faces):6d} tris  {vol_sw * 1e6:8.1f} cm3  mesh-vs-SW volume {err}  {sorted(how)}", flush=True)
        s.close(doc)
    idx_path.write_text(json.dumps(index, indent=2))


if __name__ == "__main__":
    main()
