"""Run every JX0 verification and write the report (about 30 minutes on a 12-core PC, no SolidWorks needed):

    python jx0/verify/run_all.py          -> jx0/results/verification.md

Order: servo sizing, the 14 gaits (exports the robot's gait files), CAD interference, robustness (model errors,
pushes, whole-program missions), joint strength and bracket FEA, power and timing, the software unit tests, then the report.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable
STEPS = [
    ("servo sizing", [PY, "jx0/analysis/sizing.py"]),
    ("gaits", [PY, "jx0/sim/walk_jx0.py", "--no-render"]),
    ("CAD interference", [PY, "jx0/verify/verify_cad.py"]),
    ("robustness: model errors and pushes", [PY, "jx0/verify/robustness.py", "final"]),
    ("robustness: whole-program missions", [PY, "jx0/verify/robustness.py", "mission"]),
    ("joint strength (single- vs double-sided)", [PY, "jx0/verify/verify_strength.py"]),
    ("printed brackets: voxel FEA", [PY, "jx0/verify/verify_fea.py"]),
    ("power and timing", [PY, "jx0/verify/verify_power.py"]),
    ("software tests", [PY, "-m", "unittest", "discover", "-s", "jx0/software/tests"]),
]


def main():
    ok = True
    for name, cmd in STEPS:
        print(f"== {name}", flush=True)
        r = subprocess.run(cmd, cwd=ROOT)
        ok &= r.returncode == 0
        if r.returncode:
            print(f"   {name} exited with {r.returncode}")
    subprocess.run([PY, "jx0/verify/report.py"], cwd=ROOT, check=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
