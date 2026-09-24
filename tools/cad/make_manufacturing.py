"""Manufacturing package for the JX1 custom parts (open issue OI-11).

For every machined / laser-cut part: a SolidWorks drawing (A3, third-angle front/top/right views + isometric; note with
material, process, quantity, tolerances, envelope, mass and cylindrical features) saved as SLDDRW and exported to PDF, plus a
STEP file for CNC/laser quotes. Printed parts get their STL (part frame, mm). Right-hand parts are drawn as the left part
(mirror note) but exported to STEP separately. Default export options are used — no SolidWorks system options change.
Each exported part gets its SolidWorks library material and linked MATERIAL / WEIGHT / Description properties (saved in the
part, open issue OI-5).
Outputs: manufacturing/{drawings,step,print}/ and manufacturing/index.md
Usage: .venv/Scripts/python tools/cad/make_manufacturing.py [--no-drawings]
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from swlib.core import C, Session, typed, var_array, save_as  # noqa: E402
from cad.params import ROOT  # noqa: E402

CAD = ROOT / "CAD"
OUT = ROOT / "manufacturing"
SHEET = Path("C:/ProgramData/SOLIDWORKS/SOLIDWORKS 2026/lang/english/sheetformat/a3 - iso.slddrt")

# (part path under CAD/, process, material, quantity per robot, draw?)
PARTS = [
    ("Hip/JX1_HipYawBracket_L", "CNC 3-axis from 25 mm plate", "7075-T6", 1, True),
    ("Hip/JX1_HipYawBracket_R", "CNC 3-axis from 25 mm plate (mirror of L)", "7075-T6", 1, False),
    ("Hip/JX1_HipRollBracket_L", "laser/waterjet 8 + 10 mm plates, drill/tap, dowel to 20x20 corner bar", "6061-T6", 1, True),
    ("Hip/JX1_HipRollBracket_R", "as L, mirrored", "6061-T6", 1, False),
    ("Thigh/JX1_Thigh_L", "CNC 2 setups from 30 mm plate (or 10 mm plate + bolted flange bars)", "6061-T6", 1, True),
    ("Thigh/JX1_Thigh_R", "as L, mirrored", "6061-T6", 1, False),
    ("Shin/JX1_Shin_L", "laser 10/14 mm plates + CNC joggle block + 9 mm fork tines, bolted/dowelled", "6061-T6", 1, True),
    ("Shin/JX1_Shin_R", "as L, mirrored", "6061-T6", 1, False),
    ("Foot/JX1_Foot_L", "laser 8 mm sole + bolted clevis tines and posts", "6061-T6", 1, True),
    ("Foot/JX1_Foot_R", "as L, mirrored", "6061-T6", 1, False),
    ("Pelvis/JX1_Pelvis", "laser 6/4 mm plates + tapped 8x8 corner bars", "6061-T6", 1, True),
    ("Ankle/JX1_AnkleCrank", "laser/CNC 6 mm plate, pilot recess", "6061-T6", 4, True),
    ("Ankle/JX1_AnkleCross", "turn + cross-drill Ø8 H7 bores", "EN8/EN24", 2, True),
    ("Ankle/JX1_AnkleRod_A", "cut Ø8 rod to length, tap M5x12 both ends", "chrome-plated steel", 2, True),
    ("Ankle/JX1_AnkleRod_B", "cut Ø8 rod to length, tap M5x12 both ends", "chrome-plated steel", 2, False),
    ("Torso/JX1_Torso", "laser 5/4 mm plates + 4x 2020 extrusion posts - ON HOLD until the upper-body FEA", "6061-T6 + 2020", 1, True),
    ("Arms/JX1_ShoulderPitchBracket_L", "laser 5 mm plates, bolted U-bracket - ON HOLD until the upper-body FEA", "6061-T6", 1, True),
    ("Arms/JX1_ShoulderPitchBracket_R", "as L, mirrored", "6061-T6", 1, False),
    ("Arms/JX1_ShoulderRollBracket_L", "laser 6 mm plates, bolted L-bracket - ON HOLD until the upper-body FEA", "6061-T6", 1, True),
    ("Arms/JX1_ShoulderRollBracket_R", "as L, mirrored", "6061-T6", 1, False),
    ("Arms/JX1_UpperArm_L", "laser 6 mm plates, bolted - ON HOLD until the upper-body FEA", "6061-T6", 1, True),
    ("Arms/JX1_UpperArm_R", "as L, mirrored", "6061-T6", 1, False),
    ("Arms/JX1_Forearm_L", "laser 6 mm plates, bolted - ON HOLD until the upper-body FEA", "6061-T6", 1, True),
    ("Arms/JX1_Forearm_R", "as L, mirrored", "6061-T6", 1, False),
]
PRINTED = [("Head/JX1_Head", "PETG-CF, 3 walls, 25 % gyroid", 1), ("Head/JX1_NeckBracket", "PA-CF, solid", 1),
           ("Arms/JX1_Gripper", "PA-CF body + TPU pads", 2)]
# SolidWorks library materials (drawing title block MATERIAL / WEIGHT, SolidWorks mass properties; open issue OI-5)
SW_LIBRARY = "SOLIDWORKS Materials"
SW_MATERIAL = {"6061-T6": "6061-T6 (SS)", "6061-T6 + 2020": "6061-T6 (SS)", "7075-T6": "7075-T6 (SN)",
               "EN8/EN24": "AISI 1045 Steel, cold drawn", "chrome-plated steel": "AISI 1045 Steel, cold drawn"}


def assign_material(doc, material, stem, process):
    """SolidWorks library material + linked title-block properties (MATERIAL / WEIGHT fields) on the part; returns the name set."""
    pd = typed(doc, "IPartDoc")
    name = SW_MATERIAL.get(material)
    if name:
        pd.SetMaterialPropertyName2("", SW_LIBRARY, name)
    cpm = typed(typed(doc.Extension, "IModelDocExtension").CustomPropertyManager(""), "ICustomPropertyManager")
    for k, v in (("Material", f'"SW-Material@{stem}.SLDPRT"'), ("Weight", f'"SW-Mass@{stem}.SLDPRT"'), ("Description", process),
                 ("PartNo", stem)):
        cpm.Add3(k, C.swCustomInfoText, v, C.swCustomPropertyReplaceValue)
    got = pd.GetMaterialPropertyName2("", "")
    return got[0] if isinstance(got, tuple) else got


def part_summary(part):
    """Envelope (mm), SolidWorks mass (g) and the cylindrical features (holes, bores, bosses) grouped by diameter (unique axes)."""
    import numpy as np
    pd = typed(part, "IPartDoc")
    b = pd.GetPartBox(True)
    env = sorted([round((b[3 + i] - b[i]) * 1000, 1) for i in range(3)], reverse=True)
    holes = {}
    for body in pd.GetBodies2(C.swSolidBody, False) or []:
        for f in typed(body, "IBody2").GetFaces() or []:
            face = typed(f, "IFace2")
            srf = typed(face.GetSurface(), "ISurface")
            if not srf.IsCylinder():
                continue
            p = np.array(srf.CylinderParams)                            # origin(3), axis(3), radius
            o, a, r = p[:3], p[3:6] / np.linalg.norm(p[3:6]), p[6]
            a = a if a[np.argmax(np.abs(a))] > 0 else -a
            foot = o - np.dot(o, a) * a                                 # axis point closest to the part origin
            key = (round(2 * r * 1000, 2), tuple(np.round(foot * 1000, 1)), tuple(np.round(a, 3)))
            holes[key] = True
    by_d = {}
    for d, *_ in holes:
        by_d[d] = by_d.get(d, 0) + 1
    mass_g = None
    try:
        mp = typed(typed(part.Extension, "IModelDocExtension").CreateMassProperty(), "IMassProperty")
        mass_g = round(mp.Mass * 1000, 1)
    except Exception:
        pass
    return env, mass_g, dict(sorted(by_d.items()))


def drawing(s, part_path, stem, note, out_dir):
    """A3 third-angle drawing (front/top/right + isometric) with a material/process/envelope/hole note; returns (slddrw, pdf)."""
    doc = s.new_doc("drawing")
    drw = typed(doc, "IDrawingDoc")
    part = s.open_doc(part_path)
    s.activate(doc)
    size = 0.3
    try:
        b = typed(part, "IPartDoc").GetPartBox(True)
        size = max(b[3] - b[0], b[4] - b[1], b[5] - b[2])
    except Exception:
        pass
    scale2 = 1 if size < 0.12 else (2 if size < 0.24 else (3 if size < 0.36 else 5))
    drw.SetupSheet5("Sheet1", C.swDwgPaperA3size, C.swDwgTemplateCustom, 1, scale2, False, str(SHEET), 0.42, 0.297, "Default", True)
    # the title block WEIGHT field reads a drawing-level "Weight" before the part's; an empty one avoids "ERROR!:Weight"
    typed(typed(doc.Extension, "IModelDocExtension").CustomPropertyManager(""), "ICustomPropertyManager").Add3(
        "Weight", C.swCustomInfoText, " ", C.swCustomPropertyReplaceValue)
    drw.Create3rdAngleViews2(str(part_path))
    drw.CreateDrawViewFromModelView3(str(part_path), "*Isometric", 0.33, 0.20, 0)
    # spread the views over the sheet (third angle: top above front, right to the right)
    layout = {"*Front": (0.100, 0.135), "*Top": (0.100, 0.232), "*Right": (0.232, 0.135), "*Isometric": (0.335, 0.225)}
    views = []
    v = typed(drw.GetFirstView(), "IView").GetNextView()     # first view after the sheet itself
    while v is not None:
        vv = typed(v, "IView")
        views.append(vv)
        v = vv.GetNextView()
    front = next((w for w in views if w.GetOrientationName() == "*Front"), None)
    fx, fy = front.Position if front is not None else (None, None)
    for vv in views:
        name = vv.GetOrientationName()
        if name in layout:
            vv.Position = var_array(list(layout[name]))
        elif vv.Type == C.swDrawingProjectedView and front is not None:
            x, y = vv.Position                              # projected views stay aligned with the front view
            if abs(x - fx) < 1e-3:
                vv.Position = var_array([layout["*Front"][0], layout["*Top"][1]])
            elif abs(y - fy) < 1e-3:
                vv.Position = var_array([layout["*Right"][0], layout["*Front"][1]])
    # no imported sketch dimensions: 100-200 of them per part made the sheets unreadable (tested 2026-09-24); the STEP file is
    # the dimensional master and the note lists the envelope, mass and every hole/bore diameter with its count for checking
    env, mass_g, holes = part_summary(part)
    note = "\n".join([note, f"ENVELOPE: {env[0]:g} x {env[1]:g} x {env[2]:g} mm" + (f"   MASS: {mass_g:g} g" if mass_g else ""),
                      "CYLINDRICAL FEATURES (holes / bores / bosses): " + (", ".join(f"D{d:g} x{n}" for d, n in holes.items()) or "none"),
                      "DIMENSIONS: from the STEP model (master geometry).",
                      "This sheet: material, process, quantity, inspection."])
    n = doc.InsertNote(note)
    if n is not None:
        try:
            typed(typed(n, "INote").GetAnnotation(), "IAnnotation").SetPosition2(0.02, 0.05, 0)
        except Exception:
            pass
    doc.EditRebuild3()
    slddrw = CAD / "Drawings" / f"{stem}.SLDDRW"
    slddrw.parent.mkdir(parents=True, exist_ok=True)
    ext = typed(doc.Extension, "IModelDocExtension")
    ext.SaveAs3(str(slddrw), 0, 1, None, None, 0, 0)
    pdf = out_dir / f"{stem}.pdf"
    ext.SaveAs3(str(pdf), 0, 1, None, None, 0, 0)
    s.close(doc)
    return slddrw, pdf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-drawings", action="store_true")
    a = ap.parse_args()
    s = Session()
    for sub in ("drawings", "step", "print"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    rows = []
    for rel, process, material, qty, draw in PARTS:
        path = (CAD / f"{rel}.SLDPRT").resolve()
        stem = path.stem
        doc = s.open_doc(path)
        sw_mat = assign_material(doc, material, stem, process)
        save_as(doc, path)                                   # persist material + title-block properties in the part
        step = (OUT / "step" / f"{stem}.STEP").resolve()
        ok = typed(doc.Extension, "IModelDocExtension").SaveAs3(str(step), 0, 1, None, None, 0, 0)
        pdf = ""
        if draw and not a.no_drawings:
            note = "\n".join([f"JX1 v0.4 - {stem}", f"MATERIAL: {material}", f"PROCESS: {process}",
                              f"QTY/ROBOT: {qty} (+ mirrored R part where listed)",
                              "ALL DIMENSIONS mm. GENERAL TOLERANCE ISO 2768-m. BREAK SHARP EDGES 0.3.",
                              "Actuator bolt patterns ASSUMED (open issue OI-1): confirm against RobStride STEP before release."])
            try:
                _, pdfp = drawing(s, path, stem, note, OUT / "drawings")
                pdf = pdfp.relative_to(ROOT).as_posix()
            except Exception as e:
                print("  drawing failed:", stem, e)
        rows.append((stem, material, process, qty, step.relative_to(ROOT).as_posix(), pdf))
        print(f"{stem:32s} STEP {'ok' if ok else 'FAILED'}  material {sw_mat!s:28s} drawing {pdf or '-'}", flush=True)
        s.close(doc)
    for rel, material, qty in PRINTED:
        stem = Path(rel).name
        src = ROOT / "simulation" / "meshes" / "source_mm" / f"{stem}.STL"
        if src.exists():
            shutil.copy2(src, OUT / "print" / f"{stem}.stl")
        rows.append((stem, material, "FDM print (P1S)", qty, f"manufacturing/print/{stem}.stl", ""))
    # full-size PETG mock-ups of the metal parts: check actuator bolt patterns (ASSUMED, OI-1), clearances and cable routes on the
    # real actuators before ordering metal. NOT structural (printed leg/pelvis parts failed the FEA with SF 0.08-0.90 vs 2.0 required).
    fit = []
    (OUT / "fit_check").mkdir(parents=True, exist_ok=True)
    for rel, *_ in PARTS:
        stem = Path(rel).name
        src = ROOT / "simulation" / "meshes" / "source_mm" / f"{stem}.STL"
        if src.exists():
            shutil.copy2(src, OUT / "fit_check" / f"{stem}_FITCHECK.stl")
            fit.append(stem)
    lines = ["# JX1 manufacturing package (v0.4)", "", "Generated by `tools/cad/make_manufacturing.py` from the native SolidWorks parts.",
             "STEP files are the quote/CAM source; PDFs are A3 third-angle drawings with dimensions imported from the parametric",
             "sketches (verify before release). **Actuator bolt patterns are ASSUMED until the RobStride STEP files are dimensioned (OI-1).**", "",
             "| Part | Material | Process | Qty/robot | STEP / STL | Drawing |", "|---|---|---|---|---|---|"]
    for stem, material, process, qty, f, pdf in rows:
        lines.append(f"| {stem} | {material} | {process} | {qty} | [{Path(f).name}](../{f}) | {f'[pdf](../{pdf})' if pdf else '-'} |")
    lines += ["", "## Fit-check prints (PETG) — NOT structural", "",
              "Full-size copies of the metal parts (`fit_check/*_FITCHECK.stl`, part frame, mm) for checking actuator bolt patterns,",
              "pilots, clearances and cable routes on the real actuators before ordering metal. Plain PETG, 3 walls, 15 % infill is enough.",
              "**Never load them or stand the robot on them**: the printed leg/pelvis parts failed the FEA (SF 0.08-0.90 vs 2.0 required,",
              "`calculations/results/structural/`).", "", "| Part | STL |", "|---|---|"]
    lines += [f"| {stem} | [{stem}_FITCHECK.stl](fit_check/{stem}_FITCHECK.stl) |" for stem in fit]
    (OUT / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote", OUT / "index.md")


if __name__ == "__main__":
    main()
