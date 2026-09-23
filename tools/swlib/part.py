"""Native parametric SolidWorks part builder for JX1.

Parts are modelled directly in their robot link frame (x forward, y left, z up = SolidWorks model axes).
Driving dimensions are named and linked to global variables through the Equations manager; remaining
sketch degrees of freedom are closed with SolidWorks' own Fully Define Sketch so every sketch is fully
constrained (verified per sketch).

Plane mappings (model -> sketch), measured in tools/swlib probe 2026-09-24:
  Front Plane (XY): u = x,  v = y   (normal +z)
  Top Plane   (XZ): u = x,  v = -z  (normal +y)
  Right Plane (YZ): u = -z, v = y   (normal +x)
"""
from __future__ import annotations

import math
from contextlib import contextmanager
from pathlib import Path

import numpy as np

from .core import C, NOTHING, SW, Session, save_as, set_mmgs, typed, var_array

MM = 1e-3
PLANES = {"XY": "Front Plane", "XZ": "Top Plane", "YZ": "Right Plane"}


def to_uv(plane: str, p):
    """Model point (x,y,z) [m] -> sketch (u,v) on a base plane key XY/XZ/YZ."""
    x, y, z = p
    if plane == "XY":
        return x, y
    if plane == "XZ":
        return x, -z
    if plane == "YZ":
        return -z, y
    raise ValueError(plane)


def from_uv(plane: str, u, v, w=0.0):
    if plane == "XY":
        return (u, v, w)
    if plane == "XZ":
        return (u, w, -v)
    if plane == "YZ":
        return (w, v, -u)
    raise ValueError(plane)


class Sketch:
    """Sketch context. Coordinates are sketch (u, v) in metres; helpers accept mm via *_mm methods."""

    def __init__(self, part: "Part", plane_key: str, name: str, plane_name: str | None = None):
        self.part, self.doc = part, part.doc
        self.plane_key = plane_key
        self.name = name
        self.sm = part.sm
        self.named_dims = []  # (dim name, gv expression)
        self.n_dims = 0
        self.doc.ClearSelection2(True)
        target = plane_name or PLANES[plane_key]
        kind = "PLANE"
        if not part.ext.SelectByID2(target, kind, 0, 0, 0, False, 0, None, 0):
            raise RuntimeError(f"cannot select plane {target}")
        self.sm.InsertSketch(True)
        self.sm.AddToDB = True
        self.sm.DisplayWhenAdded = False
        self.sketch = typed(self.sm.ActiveSketch, "ISketch")
        self.feature = typed(self.sketch, "IFeature") if False else None

    # ---------------------------------------------------------------- geometry (metres, sketch coords)
    def line(self, u1, v1, u2, v2, construction=False):
        seg = self.sm.CreateLine(u1, v1, 0, u2, v2, 0)
        if seg is None:
            raise RuntimeError("CreateLine failed")
        seg = typed(seg, "ISketchSegment")
        if construction:
            seg.ConstructionGeometry = True
        return seg

    def point(self, u, v, names=(None, None), gvs=(None, None)):
        """Fully located sketch point (used as a mate reference: Point<n>@<sketch>)."""
        pt = typed(self.sm.CreatePoint(u, v, 0), "ISketchPoint")
        if pt is None:
            raise RuntimeError("CreatePoint failed")
        self.locate(pt, u, v, names, gvs)
        return pt

    def centerline(self, u1, v1, u2, v2):
        seg = typed(self.sm.CreateCenterLine(u1, v1, 0, u2, v2, 0), "ISketchSegment")
        ln = typed(seg, "ISketchLine")
        self.locate(typed(ln.GetStartPoint2(), "ISketchPoint"), u1, v1)
        self.locate(typed(ln.GetEndPoint2(), "ISketchPoint"), u2, v2)
        return seg

    def circle(self, uc, vc, r, dia_name=None, gv=None, locate=True, pos_names=(None, None), pos_gvs=(None, None)):
        """Circle with a (named) diameter dimension and its centre located from the sketch origin."""
        seg = self.sm.CreateCircleByRadius(uc, vc, 0, r)
        if seg is None:
            raise RuntimeError("CreateCircleByRadius failed")
        seg = typed(seg, "ISketchSegment")
        self.n_dims += 1
        self.dim(seg, dia_name or f"D{self.n_dims}_{self.name}", gv, (uc + r * 0.8, vc + r * 0.8))
        if locate:
            cp = typed(typed(seg, "ISketchArc").GetCenterPoint2(), "ISketchPoint")
            self.locate(cp, uc, vc, pos_names, pos_gvs)
        return seg

    def arc(self, uc, vc, u1, v1, u2, v2, direction=1):
        seg = self.sm.CreateArc(uc, vc, 0, u1, v1, 0, u2, v2, 0, direction)
        if seg is None:
            raise RuntimeError("CreateArc failed")
        return typed(seg, "ISketchSegment")

    def polygon(self, pts, names=None, gvs=None):
        """Closed polygon, corners merged, every vertex dimensioned from the origin -> fully defined.
        names/gvs: optional per-vertex (u_name, v_name) / (u_expr, v_expr) to link key dimensions."""
        n = len(pts)
        lines = [typed(self.line(*pts[i], *pts[(i + 1) % n]), "ISketchLine") for i in range(n)]
        for i in range(n):
            a = typed(lines[i].GetEndPoint2(), "ISketchPoint")
            b = typed(lines[(i + 1) % n].GetStartPoint2(), "ISketchPoint")
            self.doc.ClearSelection2(True)
            a.Select4(False, None)
            b.Select4(True, None)
            self.doc.SketchAddConstraints("sgMERGEPOINTS")
        self.doc.ClearSelection2(True)
        for i in range(n):
            pt = typed(lines[i].GetStartPoint2(), "ISketchPoint")
            nm = names[i] if names else (None, None)
            gv = gvs[i] if gvs else (None, None)
            self.locate(pt, pts[i][0], pts[i][1], nm, gv)
        return lines

    def rect(self, u1, v1, u2, v2, names=None, gvs=None):
        return self.polygon([(u1, v1), (u2, v1), (u2, v2), (u1, v2)], names, gvs)

    def rect_center(self, uc, vc, w, h):
        return self.rect(uc - w / 2, vc - h / 2, uc + w / 2, vc + h / 2)

    def bolt_circle(self, uc, vc, pcd, n, d, start_deg=0.0):
        segs = []
        for k in range(n):
            a = math.radians(start_deg + 360.0 * k / n)
            segs.append(self.circle(uc + pcd / 2 * math.cos(a), vc + pcd / 2 * math.sin(a), d / 2))
        return segs

    # ---------------------------------------------------------------- constraints
    def _select_origin(self, append):
        return self.part.ext.SelectByID2("Point1@Origin", "EXTSKETCHPOINT", 0, 0, 0, append, 0, None, 0)

    def locate(self, pt, u, v, names=(None, None), gvs=(None, None), eps=1e-9):
        """Fully constrain sketch point pt at (u, v) relative to the sketch origin."""
        if abs(u) < eps and abs(v) < eps:
            self.doc.ClearSelection2(True)
            self._select_origin(False)
            pt.Select4(True, None)
            self.doc.SketchAddConstraints("sgCOINCIDENT")
            self.doc.ClearSelection2(True)
            return
        for axis, val, nm, gv in (("u", u, names[0], gvs[0]), ("v", v, names[1], gvs[1])):
            self.doc.ClearSelection2(True)
            self._select_origin(False)
            pt.Select4(True, None)
            if abs(val) < eps:
                self.doc.SketchAddConstraints("sgVERTICALPOINTS2D" if axis == "u" else "sgHORIZONTALPOINTS2D")
                continue
            tu, tv = (u / 2, v + 0.004) if axis == "u" else (u + 0.004, v / 2)
            tp = from_uv(self.plane_key, tu, tv)
            dd = (self.doc.AddHorizontalDimension2 if axis == "u" else self.doc.AddVerticalDimension2)(tp[0], tp[1], tp[2])
            if dd is None:
                raise RuntimeError(f"locate dimension failed at ({u}, {v})")
            dim = typed(typed(dd, "IDisplayDimension").GetDimension2(0), "IDimension")
            self.n_dims += 1
            dim.Name = nm or f"P{self.n_dims}"
            if gv:
                self.named_dims.append((dim.Name, gv))
        self.doc.ClearSelection2(True)

    # ---------------------------------------------------------------- dimensions / parametrics
    def dim(self, seg, name, gv=None, text_uv=None):
        """Dimension a segment (length for lines, diameter for circles). Optionally link to a global variable."""
        self.doc.ClearSelection2(True)
        seg.Select4(False, None)
        tu, tv = text_uv if text_uv is not None else (0.0, 0.0)
        tp = from_uv(self.plane_key, tu, tv)
        dd = self.doc.AddDimension2(tp[0], tp[1], tp[2])
        if dd is None:
            raise RuntimeError(f"AddDimension2 failed for {name}")
        d = typed(typed(dd, "IDisplayDimension").GetDimension2(0), "IDimension")
        d.Name = name
        self.doc.ClearSelection2(True)
        if gv:
            self.named_dims.append((name, gv))
        return d

    def close(self, fully_define=False):
        """Exit the sketch; fully define it; rename; return the sketch feature."""
        if fully_define:
            rel = 0
            for k in dir(C):
                if k.startswith("swSketchFullyDefineRelationType_"):
                    rel |= getattr(C, k)
            self.sm.FullyDefineSketch(True, True, rel, True, C.swBasicDimType_Baseline, None,
                                      C.swBasicDimType_Baseline, None, 1, 1)
        status = self.sketch.GetConstrainedStatus()
        self.sm.AddToDB = False
        self.sm.DisplayWhenAdded = True
        self.sm.InsertSketch(True)
        feat = typed(self.doc.FeatureByPositionReverse(0), "IFeature")
        old = feat.Name
        feat.Name = self.name
        for dname, gv in self.named_dims:
            self.part.link(f"{dname}@{self.name}", gv)
        self.part.sketch_status[self.name] = int(status)
        return feat


class Part:
    """Parametric part document builder."""

    def __init__(self, session: Session, name: str, path: Path, material: str | None = None):
        self.s = session
        self.name = name
        self.path = Path(path)
        self.doc = session.new_doc("part")
        set_mmgs(self.doc)
        self.ext = typed(self.doc.Extension, "IModelDocExtension")
        self.fm = typed(self.doc.FeatureManager, "IFeatureManager")
        self.sm = typed(self.doc.SketchManager, "ISketchManager")
        self.eq = typed(self.doc.GetEquationMgr(), "IEquationMgr")
        self.gvars: dict[str, float] = {}
        self.sketch_status: dict[str, int] = {}
        self.features: list[str] = []
        self.material = material
        # no modal "Modify" dialog when adding dimensions through the API
        self.s.app.SetUserPreferenceToggle(C.swInputDimValOnCreate, False)

    # ---------------------------------------------------------------- global variables & equations
    def gv(self, name: str, value: float, unit: str = "mm"):
        """Create a global variable (mm or deg)."""
        expr = f'"{name}" = {value:g}' + ("" if unit == "mm" else unit)
        idx = self.eq.Add2(-1, expr, True)
        if idx < 0:
            raise RuntimeError(f"equation failed: {expr}")
        self.gvars[name] = value
        return name

    def link(self, dim_full_name: str, expr: str):
        e = f'"{dim_full_name}" = {expr}'
        idx = self.eq.Add2(-1, e, True)
        if idx < 0:
            raise RuntimeError(f"equation failed: {e}")

    # ---------------------------------------------------------------- sketches
    @contextmanager
    def sketch(self, plane_key: str, name: str, plane_name: str | None = None, fully_define=False):
        sk = Sketch(self, plane_key, name, plane_name)
        try:
            yield sk
        finally:
            sk.feature = sk.close(fully_define)

    # ---------------------------------------------------------------- features
    def _select_sketch(self, sketch_name):
        self.doc.ClearSelection2(True)
        if not self.ext.SelectByID2(sketch_name, "SKETCH", 0, 0, 0, False, 0, None, 0):
            raise RuntimeError(f"cannot select sketch {sketch_name}")

    def _name(self, feat, name, what):
        if feat is None:
            raise RuntimeError(f"{what} failed for {name}")
        f = typed(feat, "IFeature")
        f.Name = name
        self.features.append(name)
        return f

    def extrude(self, sketch_name, depth, name, mid_plane=False, reverse=False, depth_gv=None, both=None, merge=True):
        """Boss extrude (metres). mid_plane: symmetric. both=(d1,d2) for two directions."""
        self._select_sketch(sketch_name)
        if both:
            f = self.fm.FeatureExtrusion3(False, False, reverse, C.swEndCondBlind, C.swEndCondBlind, both[0], both[1],
                                          False, False, False, False, 0, 0, False, False, False, False, merge, True, True,
                                          C.swStartSketchPlane, 0, False)
        else:
            t1 = C.swEndCondMidPlane if mid_plane else C.swEndCondBlind
            f = self.fm.FeatureExtrusion3(True, False, reverse, t1, 0, depth, 0, False, False, False, False, 0, 0,
                                          False, False, False, False, merge, True, True, C.swStartSketchPlane, 0, False)
        f = self._name(f, name, "extrude")
        if depth_gv:
            self.link(f"D1@{name}", depth_gv)
        return f

    def cut(self, sketch_name, depth=None, name="Cut", through_all=False, mid_plane=False, reverse=False, both_through=False):
        self._select_sketch(sketch_name)
        if through_all and not reverse:
            both_through = True
        if both_through:
            f = self.fm.FeatureCut4(False, False, reverse, C.swEndCondThroughAll, C.swEndCondThroughAll, 0.01, 0.01,
                                    False, False, False, False, 0, 0, False, False, False, False, False, True, True,
                                    True, True, False, C.swStartSketchPlane, 0, False, False)
        else:
            t1 = C.swEndCondThroughAll if through_all else (C.swEndCondMidPlane if mid_plane else C.swEndCondBlind)
            f = None
            for rev in (reverse, not reverse):  # a blind cut that removes nothing returns None -> try the other side
                self._select_sketch(sketch_name)
                f = self.fm.FeatureCut4(True, False, rev, t1, 0, depth or 0.01, 0, False, False, False, False, 0, 0,
                                        False, False, False, False, False, True, True, True, True, False,
                                        C.swStartSketchPlane, 0, False, False)
                if f is not None:
                    break
        return self._name(f, name, "cut")

    def revolve(self, sketch_name, name, angle_deg=360.0, cut=False, merge=True):
        """Revolve about the sketch's single centerline."""
        self._select_sketch(sketch_name)
        f = self.fm.FeatureRevolve2(True, True, False, cut, False, False, C.swEndCondBlind, 0,
                                    math.radians(angle_deg), 0, False, False, 0, 0, 0, 0, 0, merge, True, True)
        return self._name(f, name, "revolve")

    def ref_plane_offset(self, base_plane, dist, name, flip=False):
        self.doc.ClearSelection2(True)
        if not self.ext.SelectByID2(base_plane, "PLANE", 0, 0, 0, False, 0, None, 0):
            raise RuntimeError(f"cannot select {base_plane}")
        cons = C.swRefPlaneReferenceConstraint_Distance
        if flip:
            cons |= C.swRefPlaneReferenceConstraint_OptionFlip
        rp = self.fm.InsertRefPlane(cons, dist, 0, 0, 0, 0)
        if rp is None:
            raise RuntimeError(f"ref plane {name} failed")
        f = typed(self.doc.FeatureByPositionReverse(0), "IFeature")
        f.Name = name
        self.features.append(name)
        return f

    def ref_plane_angle(self, base_plane, axis_name, angle_deg, name):
        """Reference plane through `axis_name`, rotated `angle_deg` from `base_plane`."""
        self.doc.ClearSelection2(True)
        if not self.ext.SelectByID2(base_plane, "PLANE", 0, 0, 0, False, 0, None, 0):
            raise RuntimeError(f"cannot select {base_plane}")
        if not self.ext.SelectByID2(axis_name, "AXIS", 0, 0, 0, True, 1, None, 0):
            raise RuntimeError(f"cannot select {axis_name}")
        rp = self.fm.InsertRefPlane(C.swRefPlaneReferenceConstraint_Angle, math.radians(angle_deg),
                                    C.swRefPlaneReferenceConstraint_Coincident, 0, 0, 0)
        if rp is None:
            raise RuntimeError(f"angle plane {name} failed")
        f = typed(self.doc.FeatureByPositionReverse(0), "IFeature")
        f.Name = name
        self.features.append(name)
        return f

    def ref_axis(self, plane_a, plane_b, name):
        self.doc.ClearSelection2(True)
        self.ext.SelectByID2(plane_a, "PLANE", 0, 0, 0, False, 0, None, 0)
        self.ext.SelectByID2(plane_b, "PLANE", 0, 0, 0, True, 0, None, 0)
        ok = self.doc.InsertAxis2(True)
        if not ok:
            raise RuntimeError(f"axis {name} failed")
        f = typed(self.doc.FeatureByPositionReverse(0), "IFeature")
        f.Name = name
        self.features.append(name)
        return f

    def ref_points_sketch(self, plane_key, name, pts_uv, plane_name=None):
        """A sketch that only holds located reference points (mate targets). SolidWorks does not number sketch
        points sequentially, so the real selection names are discovered by position and stored in self.refpoints."""
        with self.sketch(plane_key, name, plane_name=plane_name) as sk:
            for (u, v) in pts_uv:
                sk.point(u, v)
        sel = typed(self.doc.SelectionManager, "ISelectionMgr")
        found = {}
        for i in range(1, 40):
            self.doc.ClearSelection2(True)
            if self.ext.SelectByID2(f"Point{i}@{name}", "EXTSKETCHPOINT", 0, 0, 0, False, 0, None, 0):
                pt = typed(sel.GetSelectedObject6(1, -1), "ISketchPoint")
                found[f"Point{i}@{name}"] = (pt.X, pt.Y)
        self.doc.ClearSelection2(True)
        names = []
        for (u, v) in pts_uv:
            best = min(found.items(), key=lambda kv: (kv[1][0] - u) ** 2 + (kv[1][1] - v) ** 2)
            names.append(best[0])
        self.refpoints = getattr(self, "refpoints", {})
        self.refpoints[name] = names
        return names

    def coordinate_system(self, name, origin_xyz=(0, 0, 0)):
        """Coordinate system at the part origin aligned with model axes (link frame marker for URDF export)."""
        self.doc.ClearSelection2(True)
        f = self.fm.InsertCoordinateSystem(False, False, False)
        if f is None:
            return None
        f = typed(f, "IFeature")
        f.Name = name
        return f

    def circular_pattern(self, feature_names, axis_name, count, name, spacing_deg=360.0):
        self.doc.ClearSelection2(True)
        for fn in feature_names:
            if not self.ext.SelectByID2(fn, "BODYFEATURE", 0, 0, 0, True, 4, None, 0):
                raise RuntimeError(f"cannot select feature {fn}")
        if not self.ext.SelectByID2(axis_name, "AXIS", 0, 0, 0, True, 1, None, 0):
            raise RuntimeError(f"cannot select axis {axis_name}")
        f = self.fm.FeatureCircularPattern5(count, math.radians(spacing_deg), False, "NULL", False, True, False, False,
                                            False, False, 1, 0, "NULL", False)
        return self._name(f, name, "circular pattern")

    def mirror(self, feature_names, plane_name, name):
        self.doc.ClearSelection2(True)
        self.ext.SelectByID2(plane_name, "PLANE", 0, 0, 0, False, 2, None, 0)
        for fn in feature_names:
            self.ext.SelectByID2(fn, "BODYFEATURE", 0, 0, 0, True, 1, None, 0)
        f = self.fm.InsertMirrorFeature2(False, False, False, False, 0)
        return self._name(f, name, "mirror")

    # ---------------------------------------------------------------- appearance / material / properties
    def color(self, rgb, shininess=0.3):
        r, g, b = rgb
        props = [r, g, b, 1.0, 0.6, 0.4, shininess, 0.0, 0.0]
        self.doc.MaterialPropertyValues = var_array(props)

    def set_material(self, library, material):
        pd = typed(self.doc, "IPartDoc")
        pd.SetMaterialPropertyName2("", library, material)
        self.material = material

    def prop(self, name, value):
        cpm = typed(self.ext.CustomPropertyManager(""), "ICustomPropertyManager")
        cpm.Add3(name, C.swCustomInfoText, str(value), C.swCustomPropertyReplaceValue)

    # ---------------------------------------------------------------- finish
    def rebuild(self):
        return self.doc.ForceRebuild3(False)

    def mass_properties(self):
        mp = typed(self.ext.CreateMassProperty(), "IMassProperty")
        if mp is None:
            return None
        mp.UseSystemUnits = True
        com_ = list(mp.CenterOfMass)
        return {"mass_kg": mp.Mass, "volume_m3": mp.Volume, "com_m": com_,
                "moi_about_com_kgm2": list(mp.GetMomentOfInertia(C.swMassPropertyMomentAboutCenterOfMass)),
                "surface_area_m2": mp.SurfaceArea}

    def bbox(self):
        """Axis-aligned bounding box of all solid bodies [xmin,ymin,zmin,xmax,ymax,zmax] (m)."""
        bodies = typed(self.doc, "IPartDoc").GetBodies2(C.swSolidBody, False) or []
        boxes = [list(typed(b, "IBody2").GetBodyBox()) for b in bodies]
        if not boxes:
            return None
        import numpy as _np
        b = _np.array(boxes)
        return list(b[:, :3].min(axis=0)) + list(b[:, 3:].max(axis=0))

    def body_count(self):
        bodies = typed(self.doc, "IPartDoc").GetBodies2(C.swSolidBody, False)
        return len(bodies or [])

    def errors(self):
        """Features with rebuild errors."""
        bad = []
        f = self.doc.FirstFeature()
        while f is not None:
            f = typed(f, "IFeature")
            code = f.GetErrorCode2()
            err = code[0] if isinstance(code, tuple) else code
            if err not in (0, None):
                bad.append((f.Name, err))
            f = f.GetNextFeature()
        return bad

    def save(self, close=True):
        self.rebuild()
        self.doc.ShowNamedView2("*Isometric", 7)
        self.doc.ViewZoomtofit2()
        save_as(self.doc, self.path)
        info = {"path": str(self.path), "bodies": self.body_count(), "errors": self.errors(), "refpoints": getattr(self, "refpoints", {}),
                "sketch_status": self.sketch_status, "global_variables": self.gvars, "mass": self.mass_properties()}
        if close:
            self.s.close(self.doc)
        return info
