"""Typed SolidWorks COM helpers for the dedicated JX1 session.

All API lengths are metres and angles radians (SolidWorks API convention), independent of document units.
"""
from __future__ import annotations

import math
from pathlib import Path

import pythoncom
import win32com.client as com
from win32com.client import gencache

from .instance import get_app, active_object_pid, API_DIR

ROOT = Path(__file__).resolve().parents[2]
CAD = ROOT / "CAD"


def _library(name):
    a = pythoncom.LoadTypeLib(str(API_DIR / (name + ".tlb"))).GetLibAttr()
    return gencache.EnsureModule(a[0], a[1], a[3], a[4])


SW = _library("sldworks")
C = _library("swconst").constants


def typed(obj, iface):
    """Cast a COM object to an early-bound SolidWorks interface (e.g. 'IFeature')."""
    if obj is None:
        return None
    return getattr(SW, iface)(obj._oleobj_ if hasattr(obj, "_oleobj_") else obj)


def var_array(values, vt=pythoncom.VT_R8):
    return com.VARIANT(pythoncom.VT_ARRAY | vt, list(values))


def dispatch_array(objs):
    return com.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, [o._oleobj_ if hasattr(o, "_oleobj_") else o for o in objs])


NOTHING = com.VARIANT(pythoncom.VT_DISPATCH, None)


class Session:
    """Connection to the dedicated JX1 SolidWorks session (never the shared GetActiveObject one)."""

    def __init__(self):
        app, pid = get_app()
        self.pid = pid
        self.app = app
        guard = active_object_pid()
        if guard == pid:
            raise RuntimeError("JX1 session is registered as the shared active SolidWorks object; refusing to work")
        self.math = typed(self.app.GetMathUtility(), "IMathUtility")

    # ------------------------------------------------------------------ documents
    TEMPLATE_DIR = Path("C:/ProgramData/SOLIDWORKS/SOLIDWORKS 2026/templates")
    TEMPLATE_FILES = {"part": "Part.PRTDOT", "assembly": "Assembly.ASMDOT", "drawing": "Drawing.DRWDOT"}

    def template(self, kind):
        key = {"part": C.swDefaultTemplatePart, "assembly": C.swDefaultTemplateAssembly, "drawing": C.swDefaultTemplateDrawing}[kind]
        path = self.app.GetUserPreferenceStringValue(key)
        if not path or not Path(path).exists():
            path = str(self.TEMPLATE_DIR / self.TEMPLATE_FILES[kind])
        return path

    def new_doc(self, kind="part"):
        doc = self.app.NewDocument(self.template(kind), 0, 0, 0)
        if doc is None:
            raise RuntimeError(f"NewDocument({kind}) failed")
        return typed(doc, "IModelDoc2")

    def open_doc(self, path, kind=None, silent=True):
        path = Path(path).resolve()
        kind = kind or {".sldprt": "part", ".sldasm": "assembly", ".slddrw": "drawing"}[path.suffix.lower()]
        dtype = {"part": C.swDocPART, "assembly": C.swDocASSEMBLY, "drawing": C.swDocDRAWING}[kind]
        opts = C.swOpenDocOptions_Silent if silent else 0
        doc, err, warn = self.app.OpenDoc6(str(path), dtype, opts, "", 0, 0)
        if doc is None:
            raise RuntimeError(f"OpenDoc6 failed for {path}: err={err} warn={warn}")
        return typed(doc, "IModelDoc2")

    def activate(self, doc):
        self.app.ActivateDoc3(doc.GetTitle(), False, C.swRebuildOnActivation_e.swDontRebuildActiveDoc if hasattr(C, "swRebuildOnActivation_e") else 0, 0)

    def close(self, doc_or_path):
        name = doc_or_path.GetTitle() if hasattr(doc_or_path, "GetTitle") else str(doc_or_path)
        self.app.CloseDoc(name)

    def open_documents(self):
        docs = self.app.GetDocuments() or []
        return [typed(d, "IModelDoc2") for d in docs]


def save_as(doc, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ext = typed(doc.Extension, "IModelDocExtension")
    ok = ext.SaveAs3(str(path), C.swSaveAsCurrentVersion, C.swSaveAsOptions_Silent, None, None, 0, 0)
    # pywin32 returns (bool, errors, warnings) for byref ints
    if isinstance(ok, tuple):
        ok, err, warn = ok
    else:
        err = warn = None
    if not ok:
        raise RuntimeError(f"SaveAs3 failed for {path}: errors={err} warnings={warn}")
    return path


def set_mmgs(doc):
    """Force millimetre-gram-second units with 3 decimals (display only; API stays SI)."""
    ext = typed(doc.Extension, "IModelDocExtension")
    ext.SetUserPreferenceInteger(C.swUnitSystem, 0, C.swUnitSystem_MMGS)
    ext.SetUserPreferenceInteger(C.swUnitsLinearDecimalPlaces, 0, 3)
    ext.SetUserPreferenceInteger(C.swUnitsAngularDecimalPlaces, 0, 2)



def set_view(app, doc, eye=(1.0, 0.75, 0.55), up=(0.0, 0.0, 1.0)):
    """Orient the active view so the robot's +Z is screen-up, looking from direction `eye` (model frame) at the model.

    SolidWorks standard views assume Y-up; JX1 is modelled Z-up (REP-103). SolidWorks transforms use the row-vector convention
    (p' = p . R), so the COLUMNS of the rotation block are the screen X, Y, Z axes in model coordinates (screen Z toward the viewer)."""
    import numpy as np
    zs = np.asarray(eye, float)
    zs = zs / np.linalg.norm(zs)
    ys = np.asarray(up, float) - np.dot(up, zs) * zs
    ys = ys / np.linalg.norm(ys)
    xs = np.cross(ys, zs)
    mu = typed(app.GetMathUtility(), "IMathUtility")
    data = [xs[0], ys[0], zs[0], xs[1], ys[1], zs[1], xs[2], ys[2], zs[2], 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]
    view = typed(doc.ActiveView, "IModelView")
    view.Orientation3 = mu.CreateTransform(var_array(data))
    doc.ViewZoomtofit2()
