"""Build the complete articulated JX1 robot in SolidWorks: JX1_Robot.SLDASM (pelvis, both legs with closed ankle
linkages, torso, arms, neck, head — 23 actuated joints in one flat assembly, so arm-to-leg contacts are checkable).

The leg part is built by tools/cad/build_leg_assembly.build (verified kinematics), the upper body is added with
tools/cad/build_upper_assembly.add_upper; both use the same limit-mate calibration convention.
Usage: .venv/Scripts/python tools/cad/build_robot_assembly.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from swlib.core import save_as  # noqa: E402
from cad.params import ROOT  # noqa: E402
from cad.build_leg_assembly import build as build_legs  # noqa: E402
from cad.build_upper_assembly import add_upper  # noqa: E402


def main(name="JX1_Robot"):
    asm, legs, report = build_legs(sides=("L", "R"), name=name)
    upper = add_upper(asm, include_pelvis=False)
    report["limit_calibration"].update(upper)
    report["components"] = len(asm.comp)
    report["mates"] = len(asm.mates)
    report["mate_errors_final"] = asm.mate_errors()
    report["names"] = asm.names
    asm.doc.ShowNamedView2("*Isometric", 7)
    asm.doc.ViewZoomtofit2()
    save_as(asm.doc, asm.path)
    (ROOT / "verification" / f"{name}_build.json").write_text(json.dumps(report, indent=2, default=str))
    ok = all(c.get("sign_check_pass", False) for c in report["limit_calibration"].values())
    print(f"{name}: components {report['components']}, mates {report['mates']}, mate errors {report['mate_errors_final']}, "
          f"sign checks {'ALL OK' if ok else 'FAILED'}")


if __name__ == "__main__":
    main()
