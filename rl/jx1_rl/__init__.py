"""JX1 reinforcement-learning package: CAD-derived MuJoCo training model, batched environment, PPO, export."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RL_DIR = REPO / "rl"
# the recommended policy bundle: the default of every rl tool (sim2sim, play, envelope, push, latency, report, ROS checks)
DEFAULT_POLICY = RL_DIR / "policies" / "jx1_walk_rough"
