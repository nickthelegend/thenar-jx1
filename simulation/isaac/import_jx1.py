"""Import the JX1 URDF into Isaac Sim and save USD. Run with Isaac Sim's python.sh (UNVERIFIED here)."""
from pathlib import Path

from isaacsim import SimulationApp

app = SimulationApp({"headless": True})
import omni.kit.commands  # noqa: E402

here = Path(__file__).resolve().parent
urdf = (here / "../../ros2_ws/src/jx1_description/urdf/jx1.urdf").resolve()
ok, cfg = omni.kit.commands.execute("URDFCreateImportConfig")
cfg.merge_fixed_joints = False
cfg.fix_base = False
cfg.import_inertia_tensor = True
cfg.self_collision = True
omni.kit.commands.execute("URDFParseAndImportFile", urdf_path=str(urdf), import_config=cfg, dest_path=str(here / "jx1.usd"))
app.close()
