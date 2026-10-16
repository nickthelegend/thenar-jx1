"""Print the newest checkpoint of the newest Isaac Lab run of an experiment (used by train_isaac.bat).
    python jx0/setup/latest_checkpoint.py [experiment]      default jx0_full17"""
import sys
from pathlib import Path

logs = Path(__file__).resolve().parents[2] / "simulation" / "isaac" / "isaaclab" / "logs" / (sys.argv[1] if len(sys.argv) > 1 else "jx0_full17")
runs = [r for r in logs.iterdir() if r.is_dir() and any(r.glob("model_*.pt"))] if logs.exists() else []
if not runs:
    sys.exit(f"no checkpoints under {logs}")
run = max(runs, key=lambda r: r.stat().st_mtime)
print(max(run.glob("model_*.pt"), key=lambda p: int(p.stem.split("_")[1])))
