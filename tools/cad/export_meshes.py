"""Export every JX1 part to STL (part frame, millimetres) for the simulation pipeline.

Output: simulation/meshes/source_mm/<PartName>.STL (+ index JSON with SolidWorks mass-property volumes).
The part frame is the robot link/actuator frame used by tools/cad/leg_kinematics.py, so no re-registration is needed.

Usage: .venv/Scripts/python tools/cad/export_meshes.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from swlib.core import C, Session, typed  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "simulation" / "meshes" / "source_mm"


def main():
    s = Session()
    OUT.mkdir(parents=True, exist_ok=True)
    # fine STL tessellation (deviation 0.02 mm, angle 5 deg) — system options of this JX1 session only
    s.app.SetUserPreferenceToggle(C.swSTLQuality, False) if hasattr(C, "swSTLQuality") else None
    parts = sorted(p for p in (ROOT / "CAD").rglob("*.SLDPRT") if "_scratch" not in p.parts)
    index = {}
    for p in parts:
        doc = s.open_doc(p)
        ext = typed(doc.Extension, "IModelDocExtension")
        out = (OUT / (p.stem + ".STL")).resolve()
        ok = ext.SaveAs3(str(out), 0, 1, None, None, 0, 0)
        ok = ok[0] if isinstance(ok, tuple) else ok
        mp = typed(ext.CreateMassProperty(), "IMassProperty")
        mp.UseSystemUnits = True
        index[p.stem] = {"cad": str(p.relative_to(ROOT)), "stl": str(out.relative_to(ROOT)), "exported": bool(ok),
                         "sw_volume_m3": mp.Volume, "sw_com_m": list(mp.CenterOfMass)}
        print(p.stem, "ok" if ok else "FAILED", f"{mp.Volume * 1e6:.1f} cm3", flush=True)
        s.close(doc)
    (OUT / "index.json").write_text(json.dumps(index, indent=2))


if __name__ == "__main__":
    main()
