"""Tests for the JX1 RL stack: conventions shared by training (MuJoCo), deployment (ROS 2) and Isaac Lab.

Run: rl/.venv/Scripts/python rl/tests/test_rl.py      (plain script; exits non-zero on failure)
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import traceback
from pathlib import Path

import mujoco
import numpy as np
import torch
import yaml

HERE = Path(__file__).resolve()
RL = HERE.parents[1]
REPO = HERE.parents[2]
sys.path.insert(0, str(RL))
sys.path.insert(0, str(REPO / "ros2_ws" / "src" / "jx1_policy"))
sys.path.insert(0, str(REPO / "ros2_ws" / "src" / "jx1_sim"))
from jx1_rl import config, policy_io  # noqa: E402
from jx1_rl.env import JX1Env  # noqa: E402
from jx1_rl.ppo import ActorCritic, Normalizer, Storage  # noqa: E402


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CFG = config.load()


def export_untrained(tmp: Path) -> Path:
    """Export a randomly initialised policy through rl/export.py (exercises the whole export path)."""
    pc = CFG["ppo"]
    ac = ActorCritic(CFG.num_obs, CFG.num_privileged_obs, CFG.num_actions, pc["actor_hidden"], pc["critic_hidden"], pc["activation"])
    ac.obs_norm.update(torch.randn(256, CFG.num_obs) * 2 + 1)
    ck = tmp / "model_00000.pt"
    torch.save({"model": ac.state_dict(), "iteration": -1, "config": str(RL / "config" / "jx1_walk.yaml"), "num_obs": CFG.num_obs,
                "num_privileged_obs": CFG.num_privileged_obs, "num_actions": CFG.num_actions}, ck)
    export = load_module(RL / "export.py", "jx1_export")
    sys.argv = ["export.py", "--checkpoint", str(ck), "--out", str(tmp / "bundle")]
    export.main()
    return tmp / "bundle"


# ----------------------------------------------------------------------------------------------------------------- tests
def test_quat_rotate_inverse_matches_mujoco():
    rng = np.random.default_rng(0)
    for _ in range(50):
        q = rng.normal(size=4)
        q /= np.linalg.norm(q)
        v = rng.normal(size=3)
        ref = np.zeros(3)
        qc = np.zeros(4)
        mujoco.mju_negQuat(qc, q)
        mujoco.mju_rotVecQuat(ref, v, qc)
        assert np.allclose(policy_io.quat_rotate_inverse(q, v), ref, atol=1e-12)


def test_polygon_projection_numpy_ros_torch_agree():
    runner = load_module(REPO / "ros2_ws" / "src" / "jx1_policy" / "jx1_policy" / "runner.py", "ros_runner")
    geom = load_module(REPO / "simulation" / "isaac" / "isaaclab" / "jx1_isaaclab" / "geometry.py", "isaac_geometry")
    rng = np.random.default_rng(1)
    for side, poly in CFG.ankle_polygons.items():
        pts = rng.uniform(-1.4, 0.9, size=(500, 2))
        a = policy_io._project_to_convex_polygon(pts, poly)
        b = np.array([runner.project_to_polygon(p, poly) for p in pts])
        c = geom.project_to_polygon(torch.tensor(pts), torch.tensor(poly)).numpy()
        assert np.allclose(a, b, atol=1e-12) and np.allclose(a, c, atol=1e-9), side
        inside = np.all(np.isclose(a, pts), axis=1)
        assert 0 < inside.sum() < len(pts)                      # both cases exercised
        again = policy_io._project_to_convex_polygon(a, poly)   # projected points are inside (idempotent)
        assert np.allclose(again, a, atol=1e-9)


def test_env_step_shapes_determinism_and_stability():
    outs = []
    for _ in range(2):
        env = JX1Env(CFG, num_envs=64, nthread=4, seed=123)
        obs, priv = env.reset()
        assert obs.shape == (64, CFG.num_obs) and priv.shape == (64, CFG.num_privileged_obs)
        rng = np.random.default_rng(7)
        for _ in range(60):
            obs, priv, rew, done, info = env.step(rng.normal(0, 0.5, (64, CFG.num_actions)))
            assert np.isfinite(obs).all() and np.isfinite(priv).all() and np.isfinite(rew).all()
        assert env.unstable_resets == 0
        outs.append(obs.copy())
    assert np.array_equal(outs[0], outs[1]), "same seed and actions must reproduce the rollout"


def test_deploy_observation_matches_training_env():
    """The ROS 2 runner and the sim-to-sim runner build the training observation from robot-style inputs."""
    runner_mod = load_module(REPO / "ros2_ws" / "src" / "jx1_policy" / "jx1_policy" / "runner.py", "ros_runner2")
    sim2sim = load_module(RL / "sim2sim.py", "jx1_sim2sim")
    env = JX1Env(CFG, num_envs=16, nthread=2, seed=5)
    env.reset()
    rng = np.random.default_rng(3)
    for _ in range(25):
        env.step(rng.normal(0, 0.5, (16, CFG.num_actions)))
    obs_env, _ = env.observations(noise=False)
    with tempfile.TemporaryDirectory() as tmp:
        bundle = export_untrained(Path(tmp))
        ros = runner_mod.PolicyRunner(bundle)
        s2s = sim2sim.Runner(bundle)
        qp, qv = env.qpos(), env.qvel()
        for i in range(16):
            ros.last_action = env.actions[i].copy()
            args = (qp[i, 3:7], qv[i, 3:6], qp[i, env.qadr], qv[i, env.dadr], env.commands[i], env.state[i, 0])
            o_ros = ros.observation(*args)
            assert np.allclose(o_ros, obs_env[i], atol=1e-5), np.abs(o_ros - obs_env[i]).max()
            # same targets from both deployment runners
            s2s.last_action = env.actions[i].copy()
            t_ros = ros.step(*args)
            t_s2s = s2s.targets(*args)
            assert np.allclose([t_ros[j] for j in ros.policy_joints], t_s2s, atol=1e-6)
        io = yaml.safe_load((bundle / "policy_io.yaml").read_text(encoding="utf-8"))
        assert io["policy"]["num_obs"] == CFG.num_obs and io["joints"]["policy"] == CFG.policy_joints
        assert max(io["trained"]["export_check"].values()) < 1e-4


def test_isaac_policy_io_schema_matches_mujoco_export():
    tc_mod = load_module(REPO / "simulation" / "isaac" / "isaaclab" / "jx1_isaaclab" / "task_config.py", "isaac_task_config")
    export = load_module(RL / "export.py", "jx1_export2")
    a = export.policy_io(CFG, {})
    b = tc_mod.policy_io(tc_mod.load(), {})
    assert set(a) == set(b)
    for k in ("control", "joints", "default_joint_pos", "action_scale", "pd_gains", "joint_limits_rad", "observation", "gait", "commands"):
        assert a[k] == b[k], k
    assert a["policy"]["num_obs"] == b["policy"]["num_obs"]
    for j, e in a["effort_limits_Nm"].items():                       # MJCF forcerange == URDF <limit effort>
        assert abs(b["effort_limits_Nm"][j] - e) < 1e-9, j
    for s in a["ankle_polygons_rad"]:
        assert np.allclose(a["ankle_polygons_rad"][s], b["ankle_polygons_rad"][s], atol=1e-6)
    assert abs(tc_mod.load()["base_height"] - JX1Env(CFG, 2, nthread=1, randomize=False).base_height_target) < 0.01


def test_normalizer_and_gae():
    x = torch.randn(1000, 5) * 3 + 2
    n = Normalizer(5)
    for chunk in x.split(137):
        n.update(chunk)
    assert torch.allclose(n.mean, x.mean(0), atol=1e-5) and torch.allclose(n.var, x.var(0, unbiased=False), atol=1e-4)
    T, N = 6, 3
    st = Storage(T, N, 2, 2, 1, "cpu")
    r, v, d = torch.rand(T, N), torch.rand(T, N), (torch.rand(T, N) < 0.2).float()
    st.rewards, st.values, st.dones = r.clone(), v.clone(), d.clone()
    last = torch.rand(N)
    st.compute_returns(last, 0.99, 0.95)
    ref, adv = np.zeros((T, N)), np.zeros(N)
    for t in reversed(range(T)):
        nv = last.numpy() if t == T - 1 else v[t + 1].numpy()
        delta = r[t].numpy() + (1 - d[t].numpy()) * 0.99 * nv - v[t].numpy()
        adv = delta + (1 - d[t].numpy()) * 0.99 * 0.95 * adv
        ref[t] = adv + v[t].numpy()
    assert np.allclose(st.returns.numpy(), ref, atol=1e-6)


def test_ros2_control_xacro_expands():
    import xacro
    urdf_dir = REPO / "ros2_ws" / "src" / "jx1_description" / "urdf"
    base = urdf_dir / "jx1.urdf.xacro"
    if not base.exists():
        print("   (skipped: jx1.urdf.xacro not generated yet)")
        return
    with tempfile.TemporaryDirectory() as tmp:
        text = (urdf_dir / "jx1_system.urdf.xacro").read_text(encoding="utf-8").replace("$(find jx1_description)", str(REPO / "ros2_ws" / "src" / "jx1_description"))
        p = Path(tmp) / "system.urdf.xacro"
        p.write_text(text, encoding="utf-8")
        for hw in ("topic", "mock"):
            doc = xacro.process_file(str(p), mappings={"hardware": hw})
            rc = doc.getElementsByTagName("ros2_control")
            assert len(rc) == 1
            joints = [j.getAttribute("name") for j in rc[0].getElementsByTagName("joint")]
            urdf_joints = [j.getAttribute("name") for j in doc.getElementsByTagName("joint") if j.getAttribute("type") == "revolute"]
            assert set(joints) >= set(urdf_joints) - {""}, set(urdf_joints) - set(joints)
    ctrl = yaml.safe_load((REPO / "ros2_ws" / "src" / "jx1_bringup" / "config" / "controllers.yaml").read_text(encoding="utf-8"))
    order = ctrl["jx1_position_controller"]["ros__parameters"]["joints"]
    assert order[:CFG.num_actions] == CFG.policy_joints


def main():
    tests = [(n, f) for n, f in globals().items() if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS {name}")
        except Exception:
            failed += 1
            print(f"FAIL {name}")
            traceback.print_exc()
    print(f"{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
