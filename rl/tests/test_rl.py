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
        src = env.obs_src                               # the (latency-randomised) state the actor observation is built from
        qp, qv = src[:, 1:1 + env.nq], src[:, 1 + env.nq:1 + env.nq + env.nv]
        for i in range(16):
            ros.last_action = env.actions[i].copy()
            args = (qp[i, 3:7], qv[i, 3:6], qp[i, env.qadr], qv[i, env.dadr], env.commands[i], env.state[i, 0])   # clock: current time
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


def test_latency_randomisation():
    env = JX1Env(CFG, num_envs=64, nthread=4, seed=11)
    env.reset()
    assert env.act_delay.max() > 0 and env.obs_delay.max() > 0          # both randomised over the batch
    rng = np.random.default_rng(2)
    for _ in range(10):
        env.step(rng.normal(0, 0.5, (64, CFG.num_actions)))
    lag = env.obs_delay == 1
    fresh = env.obs_delay == 0
    assert np.allclose(env.obs_src[fresh], env.state[fresh])
    assert not np.allclose(env.obs_src[lag, 1:], env.state[lag, 1:])      # one substep (5 ms) older
    assert np.allclose(env.obs_src[lag, 0], env.state[lag, 0] - CFG["model"]["timestep"])


def test_hub_interpolation_ramp():
    """Targets ramp over the policy period like the CAN hubs, in the training env and in the ROS MuJoCo node."""
    env = JX1Env(CFG, num_envs=8, nthread=2, seed=3, randomize=False)
    env.reset()
    seen = {}
    orig = env.pool.rollout

    def spy(models, datas, initial_state, control, **kw):
        seen["control"] = control.copy()
        return orig(models, datas, initial_state, control, **kw)
    env.pool.rollout = spy
    before = env.ctrl.copy()
    env.step(np.ones((8, CFG.num_actions)))
    c = seen["control"][:, :, env.act]                   # (N, decimation, n)
    frac = (c - before[:, None, env.act]) / (env.ctrl[:, None, env.act] - before[:, None, env.act])
    assert np.allclose(frac, (np.arange(1, env.decimation + 1) / env.decimation)[None, :, None], atol=1e-9)
    from jx1_sim.sim_core import MujocoSim
    sim = MujocoSim(REPO / "simulation" / "mujoco" / "jx1.xml")
    a = sim.act[CFG.policy_joints[3]]
    sim.set_targets({CFG.policy_joints[3]: 0.0})
    sim.step(10)
    sim.set_targets({CFG.policy_joints[3]: 1.0})         # new command 20 ms after the previous one
    vals = []
    for _ in range(10):
        sim.step(1)
        vals.append(sim.d.ctrl[a])
    assert np.allclose(vals, np.arange(1, 11) / 10, atol=1e-9), vals


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
    for j, v in a["velocity_limits_rad_s"].items():                   # class table == URDF <limit velocity>
        assert abs(b["velocity_limits_rad_s"][j] - v) < 1e-9, (j, v, b["velocity_limits_rad_s"][j])
    for s in a["ankle_polygons_rad"]:
        assert np.allclose(a["ankle_polygons_rad"][s], b["ankle_polygons_rad"][s], atol=1e-6)
    assert abs(tc_mod.load()["base_height"] - JX1Env(CFG, 2, nthread=1, randomize=False).base_height_target) < 0.01


def _hw():
    sys.path.insert(0, str(REPO / "ros2_ws" / "src" / "jx1_hw"))
    from jx1_hw import protocol, bridge, ankle
    return protocol, bridge, ankle


def test_hw_protocol_frames_and_crc():
    P, _, _ = _hw()
    assert P.crc16(b"123456789") == 0x4B37                              # CRC-16/MODBUS check value
    rows = [(0.1 * j, -0.2, 40.0 + j, 1.5, 0.25) for j in range(11)]
    f = P.pack_command(77, P.RUN, rows)
    assert len(f) == P.command_size(11)
    seq, mode, back = P.unpack_command(f, 11)
    assert seq == 77 and mode == P.RUN and np.allclose(back, rows, atol=1e-6)
    st = P.HubState(seq=5, estop=True, fault=False, mode=P.DAMPING, q=[0.5] * 10, dq=[1.0] * 10, tau=[-2.0] * 10, temp=[41.0] * 10,
                    faults=[0x80] + [0] * 9)
    s = P.pack_state(st)
    assert len(s) == P.state_size(10)
    back = P.unpack_state(s, 10)
    assert back.estop and back.mode == P.DAMPING and back.stale[0] and not back.stale[1] and np.allclose(back.q, st.q)
    rd = P.FrameReader(P.STATE_HEAD, P.state_size(10))
    bad = bytearray(s)
    bad[20] ^= 0xFF                                                      # corrupted frame is dropped, stream resynchronises
    stream = b"\x00\x13garbage" + bytes(bad) + s[:30]
    frames = rd.feed(stream) + rd.feed(s[30:] + s)
    assert len(frames) == 2 and rd.crc_errors == 1 and all(fr == s for fr in frames)


def test_hw_bridge_joint_motor_roundtrip():
    P, B, A = _hw()
    sys.path.insert(0, str(REPO / "calculations"))
    from jx1calc.ankle import from_design
    from jx1calc.design import Design
    hw = yaml.safe_load((REPO / "ros2_ws" / "src" / "jx1_hw" / "config" / "hw.yaml").read_text(encoding="utf-8"))
    export = load_module(RL / "export.py", "jx1_export3")
    br = B.Bridge(hw, export.policy_io(CFG, {}))
    ref = from_design(Design())
    rng = np.random.default_rng(4)
    for _ in range(30):
        tgt = {j: rng.uniform(*CFG.limits[j]) * 0.8 for j in br.hub_joints}
        for s, poly in CFG.ankle_polygons.items():                     # ankle targets inside the reachable polygon
            p = policy_io._project_to_convex_polygon(rng.uniform([-0.9, -0.33], [0.5, 0.33]), poly)
            tgt[f"{s}_ankle_pitch_joint"], tgt[f"{s}_ankle_roll_joint"] = p
        rows = br.commands(tgt)
        # hub echoes the commanded motor positions as its measured state -> the bridge must return the joint targets
        states = {h: P.HubState(seq=1, estop=False, fault=False, mode=P.RUN, q=[r[0] for r in rs], dq=[0.0] * len(rs),
                                tau=[0.0] * len(rs), temp=[40.0] * len(rs), faults=[0] * len(rs)) for h, rs in rows.items()}
        js = br.decode(states)
        for j, v in tgt.items():
            assert abs(js[j][0] - v) < 1e-7, (j, js[j][0], v)
        la = br.ankle["left"]
        assert np.allclose(la.crank_angles(tgt["left_ankle_pitch_joint"], tgt["left_ankle_roll_joint"]),
                           ref.crank_angles(tgt["left_ankle_pitch_joint"], tgt["left_ankle_roll_joint"]), atol=1e-12)
    # gains: the realisable ankle gains of the task are reproduced by the per-motor loops (pitch exact, roll within 2 %)
    (kp_m, kd_m), K = br.ankle["left"].motor_gains(0.0, 0.0, [CFG.gains["left_ankle_pitch_joint"][0], CFG.gains["left_ankle_roll_joint"][0]],
                                                    [CFG.gains["left_ankle_pitch_joint"][1], CFG.gains["left_ankle_roll_joint"][1]])
    assert abs(K[0, 0] - CFG.gains["left_ankle_pitch_joint"][0]) < 1e-6
    assert abs(K[1, 1] / CFG.gains["left_ankle_roll_joint"][0] - 1) < 0.02, K


def test_imu_rotations():
    sys.path.insert(0, str(REPO / "ros2_ws" / "src" / "jx1_hw"))
    from jx1_hw.rotations import matrix_to_quat, quat_to_matrix, rpy_matrix
    rng = np.random.default_rng(9)
    for _ in range(200):
        q = rng.normal(size=4)
        q /= np.linalg.norm(q)
        q *= np.sign(q[0]) if q[0] != 0 else 1.0
        R = quat_to_matrix(*q)
        ref = np.zeros(9)
        mujoco.mju_quat2Mat(ref, q)
        assert np.allclose(R, ref.reshape(3, 3), atol=1e-12)
        assert np.allclose(matrix_to_quat(R), q, atol=1e-9)
    Rm = rpy_matrix(0.1, -0.2, 0.3)
    assert np.allclose(Rm @ Rm.T, np.eye(3), atol=1e-12) and abs(np.linalg.det(Rm) - 1) < 1e-12


def test_rough_terrain():
    """Heightfield continuity (only step tiles may jump) and the numpy height lookup against MuJoCo ray-casts."""
    rcfg = config.load(RL / "config" / "jx1_walk_rough.yaml")
    assert rcfg["name"] == "jx1_walk_rough" and rcfg["action_scale"] == CFG["action_scale"]      # inherits the flat task
    env = JX1Env(rcfg, num_envs=32, nthread=2, seed=1)
    t = env.terrain
    jump = max(np.abs(np.diff(t.h, axis=a)).max() for a in (0, 1))
    assert jump <= 2 * rcfg["terrain"]["max_step_m"] + 0.021, jump                              # steps or noise blocks only
    m, d = env.model, mujoco.MjData(env.model)
    mujoco.mj_forward(m, d)
    rng = np.random.default_rng(1)
    err = []
    for _ in range(200):
        x, y = rng.uniform(-7, 7, 2)
        dist = mujoco.mj_ray(m, d, np.array([x, y, 2.0]), np.array([0, 0, -1.0]), None, 1, -1, np.zeros(1, dtype=np.int32))
        err.append(abs((2.0 - dist) - float(env.ground(np.array([x]), np.array([y]))[0])))
    assert np.median(err) < 1e-4 and max(err) < 0.02, (np.median(err), max(err))
    env.reset()
    qp = env.qpos()
    assert np.all(np.abs(qp[:, :2]) < t.size / 2)                                                # spawned on the map
    for _ in range(20):
        obs, priv, rew, done, info = env.step(np.zeros((32, rcfg.num_actions)))
        assert np.isfinite(obs).all() and np.isfinite(rew).all()
    assert env.unstable_resets == 0


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


def test_mirror_symmetry_matches_physics():
    """Mirror maps used by the PPO symmetry loss: MuJoCo physics is equivariant under them, the observation of a mirrored
    state is the mirrored observation, and mirroring twice is the identity."""
    from jx1_rl.symmetry import Mirror, mirror_mujoco_state
    m = mujoco.MjModel.from_xml_path(str(REPO / "simulation" / "mujoco" / "jx1.xml"))
    m.opt.disableflags |= mujoco.mjtDisableBit.mjDSBL_CONTACT          # in the air: no floor, no self-contact
    # the CAD trunk and head are slightly asymmetric (torso COM y 0.8 mm, tilted principal axes; head E-stop): make the
    # inertias exactly mirror-symmetric so that only the sign conventions are tested
    S = np.diag([1.0, -1.0, 1.0])

    def inertia(b):
        R = np.zeros(9)
        mujoco.mju_quat2Mat(R, m.body_iquat[b])
        R = R.reshape(3, 3)
        return R @ np.diag(m.body_inertia[b]) @ R.T

    def set_inertia(b, full):
        w, V = np.linalg.eigh(full)
        if np.linalg.det(V) < 0:
            V[:, 0] *= -1
        q = np.zeros(4)
        mujoco.mju_mat2Quat(q, V.flatten())
        m.body_inertia[b], m.body_iquat[b] = w, q
    for b in range(1, m.nbody):
        name = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_BODY, b) or ""
        if name.startswith("left_"):
            r = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "right_" + name[5:])
            m.body_mass[r], m.body_ipos[r] = m.body_mass[b], m.body_ipos[b] * np.array([1.0, -1.0, 1.0])
            set_inertia(r, S @ inertia(b) @ S)
        elif not name.startswith("right_"):
            set_inertia(b, 0.5 * (inertia(b) + S @ inertia(b) @ S))
            m.body_ipos[b][1] = 0.0
    act = {mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, m.actuator_trnid[a, 0]): a for a in range(m.nu)}
    jid = {j: mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, j) for j in act}
    qadr, dadr = {j: m.jnt_qposadr[i] for j, i in jid.items()}, {j: m.jnt_dofadr[i] for j, i in jid.items()}
    rng = np.random.default_rng(5)
    d, dm = mujoco.MjData(m), mujoco.MjData(m)
    d.qpos[2] = 2.0
    d.qpos[3:7] = np.array([0.95, 0.1, -0.2, 0.2]) / np.linalg.norm([0.95, 0.1, -0.2, 0.2])
    d.qvel[:] = rng.uniform(-0.5, 0.5, m.nv)
    for j, i in jid.items():
        lo, hi = m.jnt_range[i]
        d.qpos[qadr[j]] = rng.uniform(lo + 0.2 * (hi - lo), hi - 0.2 * (hi - lo))
    ctrl = {j: rng.uniform(*m.jnt_range[jid[j]]) * 0.5 for j in act}
    dm.qpos[:], dm.qvel[:] = mirror_mujoco_state(d.qpos, d.qvel, qadr, dadr)
    names = list(act)
    from jx1_rl.symmetry import joint_mirror
    midx, msign = joint_mirror(names)
    for i, j in enumerate(names):
        d.ctrl[act[j]] = ctrl[j]
        dm.ctrl[act[j]] = msign[i] * ctrl[names[midx[i]]]
    for _ in range(100):                                                     # 0.2 s of free flight with PD motion
        mujoco.mj_step(m, d)
        mujoco.mj_step(m, dm)
    qp, qv = mirror_mujoco_state(d.qpos, d.qvel, qadr, dadr)
    assert np.abs(qp - dm.qpos).max() < 1e-4 and np.abs(qv - dm.qvel).max() < 1e-3, (np.abs(qp - dm.qpos).max(), np.abs(qv - dm.qvel).max())

    mir = Mirror(CFG.policy_joints, CFG.num_privileged_obs)
    pj = CFG.policy_joints
    default = np.array([CFG.default_pos[j] for j in pj])

    def obs_of(qpos, qvel, cmd, last, t):
        q = np.array([qpos[qadr[j]] for j in pj])
        dq = np.array([qvel[dadr[j]] for j in pj])
        return policy_io.build_observation(qvel[3:6], policy_io.projected_gravity(qpos[3:7]), cmd, q - default, dq, last,
                                           policy_io.gait_phase(np.asarray(t), CFG["gait"]["period_s"]), CFG["observation"]["scales"])
    cmd, last, t = np.array([0.4, 0.2, -0.3]), rng.normal(0, 0.5, len(pj)), 0.37
    o = obs_of(d.qpos, d.qvel, cmd, last, t)
    om = obs_of(dm.qpos, dm.qvel, cmd * np.array([1, -1, -1]), mir.act(last), t + 0.5 * CFG["gait"]["period_s"])
    assert np.allclose(mir.obs(o), om, atol=1e-5), np.abs(mir.obs(o) - om).max()
    x, p, a = rng.normal(size=(4, CFG.num_obs)), rng.normal(size=(4, CFG.num_privileged_obs)), rng.normal(size=(4, CFG.num_actions))
    assert np.allclose(mir.obs(mir.obs(x)), x) and np.allclose(mir.priv(mir.priv(p)), p) and np.allclose(mir.act(mir.act(a)), a)
    assert np.allclose(mir.priv(p)[:, :CFG.num_obs], mir.obs(p[:, :CFG.num_obs]))
    tx = torch.as_tensor(x, dtype=torch.float32)
    assert torch.allclose(mir.obs(tx), torch.as_tensor(mir.obs(x), dtype=torch.float32))


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
