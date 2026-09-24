"""Check that ros2_ws/src/jx1_description/urdf/jx1.urdf.xacro expands (default arguments) to the same robot as jx1.urdf.

Compares every link (mass, COM, inertia, visual + collision meshes) and joint (type, parent, child, origin, axis, limits,
dynamics) numerically, then checks two argument variants: collision:=visual (one collision mesh per link = the visual)
and limit_margin_deg:=2 (every revolute range shrinks by 2 deg at both ends).
Output: verification/xacro_check.json.  Usage: .venv/Scripts/python tools/sim/check_xacro.py
"""
from __future__ import annotations

import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import xacro

ROOT = Path(__file__).resolve().parents[2]
URDF_DIR = ROOT / "ros2_ws" / "src" / "jx1_description" / "urdf"


def nums(s):
    return [float(x) for x in s.split()]


def summarise(root):
    links, joints = {}, {}
    for L in root.findall("link"):
        d = {"visual": [m.get("filename") for m in L.findall("visual/geometry/mesh")],
             "collision": [m.get("filename") for m in L.findall("collision/geometry/mesh")]}
        inert = L.find("inertial")
        if inert is not None:
            d["mass"] = float(inert.find("mass").get("value"))
            d["com"] = nums(inert.find("origin").get("xyz"))
            d["inertia"] = [float(inert.find("inertia").get(k)) for k in ("ixx", "ixy", "ixz", "iyy", "iyz", "izz")]
        links[L.get("name")] = d
    for J in root.findall("joint"):
        d = {"type": J.get("type"), "parent": J.find("parent").get("link"), "child": J.find("child").get("link"),
             "xyz": nums(J.find("origin").get("xyz"))}
        if J.find("axis") is not None:
            d["axis"] = nums(J.find("axis").get("xyz"))
        lim = J.find("limit")
        if lim is not None:
            d["limit"] = [float(lim.get(k)) for k in ("lower", "upper", "effort", "velocity")]
        dyn = J.find("dynamics")
        if dyn is not None:
            d["dynamics"] = [float(dyn.get("damping")), float(dyn.get("friction"))]
        joints[J.get("name")] = d
    return links, joints


def close(a, b, rel=1e-6, abs_=1e-9):
    if isinstance(a, list):
        return len(a) == len(b) and all(close(x, y, rel, abs_) for x, y in zip(a, b))
    if isinstance(a, float):
        return math.isclose(a, b, rel_tol=rel, abs_tol=abs_)
    return a == b


def diff(ref, got):
    out = []
    for kind, r, g in (("link", ref[0], got[0]), ("joint", ref[1], got[1])):
        for name in sorted(set(r) | set(g)):
            if name not in r or name not in g:
                out.append(f"{kind} {name}: only in {'xacro' if name in g else 'urdf'}")
                continue
            for k in sorted(set(r[name]) | set(g[name])):
                if not close(r[name].get(k), g[name].get(k)):
                    out.append(f"{kind} {name}.{k}: urdf {r[name].get(k)} vs xacro {g[name].get(k)}")
    return out


def expand(path, **mappings):
    doc = xacro.process_file(str(path), mappings={k: str(v) for k, v in mappings.items()})
    return ET.fromstring(doc.toxml())


def check(urdf_path=URDF_DIR / "jx1.urdf", xacro_path=URDF_DIR / "jx1.urdf.xacro"):
    ref = summarise(ET.parse(urdf_path).getroot())
    base = summarise(expand(xacro_path))
    d0 = diff(ref, base)
    vis = summarise(expand(xacro_path, collision="visual"))
    d1 = [n for n, L in vis[0].items() if L["visual"] and L["collision"] != L["visual"]]
    m2 = summarise(expand(xacro_path, limit_margin_deg=2))
    d2 = [n for n, J in m2[1].items() if "limit" in J and not (
        close(J["limit"][0], ref[1][n]["limit"][0] + math.radians(2), abs_=1e-7)
        and close(J["limit"][1], ref[1][n]["limit"][1] - math.radians(2), abs_=1e-7))]
    res = {"urdf": urdf_path.relative_to(ROOT).as_posix(), "xacro": xacro_path.relative_to(ROOT).as_posix(),
           "links": len(ref[0]), "joints": len(ref[1]), "revolute": sum(j["type"] == "revolute" for j in ref[1].values()),
           "default_expansion_differences": d0, "collision_visual_mismatches": d1, "margin_2deg_mismatches": d2,
           "pass": not d0 and not d1 and not d2}
    return res


def main():
    res = check()
    (ROOT / "verification" / "xacro_check.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"xacro vs urdf: {res['links']} links, {res['joints']} joints ({res['revolute']} revolute) -> "
          f"{'PASS' if res['pass'] else 'FAIL'}")
    for k in ("default_expansion_differences", "collision_visual_mismatches", "margin_2deg_mismatches"):
        for line in res[k][:10]:
            print(" ", k, line)
    sys.exit(0 if res["pass"] else 1)


if __name__ == "__main__":
    main()
