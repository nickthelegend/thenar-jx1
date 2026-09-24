"""Offline check of the JX1 Isaac Lab tasks against an Isaac Lab source checkout: no Isaac Sim, no GPU.

  rl/.venv/Scripts/python simulation/isaac/isaaclab/scripts/offline_check.py --isaaclab D:/jx1-deps/IsaacLab-2.3.2 \
      --rsl-rl D:/jx1-deps/rsl_rl_src [--json simulation/isaac/isaaclab/offline_check.json]

The Omniverse / Isaac Sim modules (omni, pxr, carb, isaacsim, warp, ...) and any other module that is not installed are
replaced by import mocks, the trick Isaac Lab's own documentation build uses. The real isaaclab, isaaclab_tasks,
isaaclab_rl (and rsl_rl) sources are imported. A top-level package that exists is never mocked, so a typo in an
isaaclab import still fails.

For every registered JX1 task the script:
  1. resolves the gym entry points and instantiates the env config (the whole configclass __post_init__ chain),
     then runs validate() so that no MISSING field is left.
  2. resolves every manager term the way Isaac Lab does at start-up (ManagerBase._resolve_common_term_cfg):
     the term is callable and its params match the function signature.
  3. resolves every SceneEntityCfg with the real SceneEntityCfg.resolve() against the robot that Isaac's URDF
     importer builds (movable URDF joints; links after merge_fixed_joints).
  4. evaluates every observation, reward and termination term (Isaac Lab's and JX1's) on a fake scene. The fake
     scene's attribute names are checked against the real ArticulationData / ContactSensorData classes. Each term
     must return a finite (num_envs, k) or (num_envs,) tensor.
  5. compares the policy observation with rl/jx1_rl/policy_io.build_observation (the MuJoCo and ROS 2 layout) on the
     same state.
  6. steps the JX1 action term (joint-limit clamp, ankle polygon, CAN-hub ramp, transport delay, reset) and
     compares every physics substep target with the MuJoCo pipeline (rl/jx1_rl/env.py).
  7. checks that the actuator groups cover every joint once with the task gains, effort/velocity limits and armature.
It also instantiates the rsl_rl runner config, converts it with to_dict() and checks its policy/algorithm keys against
rsl_rl's ActorCritic / PPO constructors.

Not covered (still needs Isaac Sim): the PhysX behaviour, the USD/URDF import itself, and sensor data at runtime.
"""
from __future__ import annotations

import argparse
import dataclasses
import importlib
import importlib.abc
import importlib.machinery
import inspect
import json
import math
import sys
import tomllib
import traceback
import types
import xml.etree.ElementTree as ET
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]                    # simulation/isaac/isaaclab
REPO = PKG.parents[2]
N_ENVS = 8


# ------------------------------------------------------------------------------------------------ import mocks
class _Mock:
    """Anything taken from a mocked module. Attribute access, calls, indexing, arithmetic, `X | None` annotations,
    context managers and subclassing (class Foo(omni.Base)) all work, and each yields another mock."""
    _name = "mock"

    def __init__(self, *args, **kwargs):
        pass

    def __mro_entries__(self, bases):
        return (type(self),)

    def __getattr__(self, key):
        if key.startswith("__") and key.endswith("__"):
            raise AttributeError(key)
        return _mock(f"{self._name}.{key}")

    def __call__(self, *args, **kwargs):
        if len(args) == 1 and not kwargs and (inspect.isfunction(args[0]) or inspect.isclass(args[0])):
            return args[0]                                    # used as a decorator: keep the function / class
        return _mock(f"{self._name}()")

    def __getitem__(self, key):
        return _mock(f"{self._name}[]")

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0

    def __bool__(self):
        return True

    def __contains__(self, item):
        return False

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def __or__(self, other):
        return self

    __ror__ = __add__ = __radd__ = __sub__ = __rsub__ = __mul__ = __rmul__ = __truediv__ = __rtruediv__ = __or__

    def __int__(self):
        return 0

    def __float__(self):
        return 0.0

    def __index__(self):
        return 0

    def __lt__(self, other):
        return False

    __le__ = __gt__ = __ge__ = __lt__

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return f"<mock {self._name}>"

    def __str__(self):
        return self._name


def _mock(name: str):
    short = name.rsplit(".", 1)[-1] or "mock"
    return type(short, (_Mock,), {"_name": name, "__name__": short, "__qualname__": short})()


class _MockModule(types.ModuleType):
    def __getattr__(self, key):
        if key.startswith("__") and key.endswith("__"):
            raise AttributeError(key)
        value = _mock(f"{self.__name__}.{key}")
        setattr(self, key, value)
        return value


class _MockFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Last entry of sys.meta_path. A module that no real finder found is mocked, unless its top-level package
    exists; then the ImportError stands."""

    def __init__(self, always=()):
        self.mocked, self.real = set(always), set()

    def find_spec(self, fullname, path=None, target=None):
        root = fullname.partition(".")[0]
        if root not in self.mocked:
            loaded = sys.modules.get(root)
            if root in self.real or (loaded is not None and not isinstance(loaded, _MockModule)) \
                    or importlib.machinery.PathFinder.find_spec(root) is not None:
                self.real.add(root)
                return None
            self.mocked.add(root)
        return importlib.machinery.ModuleSpec(fullname, self, is_package=True)

    def create_module(self, spec):
        return _MockModule(spec.name)

    def exec_module(self, module):
        module.__path__ = []


GYM_REGISTRY: dict[str, dict] = {}


def install_import_hooks(isaaclab_root: Path, rsl_rl_root: Path | None) -> _MockFinder:
    finder = _MockFinder(always={"gymnasium", "omni", "pxr", "carb", "isaacsim", "warp", "usdrt"})
    sys.meta_path.append(finder)
    # gymnasium: record registrations so that the entry points can be resolved
    gym = _MockModule("gymnasium")
    gym.__path__ = []
    gym.register = lambda id, entry_point=None, kwargs=None, **kw: GYM_REGISTRY.__setitem__(
        id, {"entry_point": entry_point, **(kwargs or {}), **kw})
    sys.modules["gymnasium"] = gym
    # toml (isaaclab/__init__ reads its extension.toml): the standard library parser
    toml = types.ModuleType("toml")
    toml.load = lambda f: tomllib.loads(Path(f).read_text(encoding="utf-8") if isinstance(f, (str, Path)) else f.read())
    sys.modules["toml"] = toml
    src = isaaclab_root / "source"
    for pkg in ("isaaclab", "isaaclab_rl", "isaaclab_assets", "isaaclab_tasks"):
        sys.path.insert(0, str(src / pkg))
    # isaaclab_tasks/__init__ imports every task in the repository; only the locomotion base config is needed
    tasks = types.ModuleType("isaaclab_tasks")
    tasks.__path__ = [str(src / "isaaclab_tasks" / "isaaclab_tasks")]
    sys.modules["isaaclab_tasks"] = tasks
    if rsl_rl_root is not None:
        sys.path.insert(0, str(rsl_rl_root))
    sys.path.insert(0, str(PKG))
    sys.path.insert(0, str(REPO / "rl"))
    return finder


# ------------------------------------------------------------------------------------------------ robot model
def robot_from_urdf(urdf: Path):
    """Joints and bodies of the articulation Isaac's URDF importer builds (merge_fixed_joints=True)."""
    root = ET.parse(urdf).getroot()
    joints, children, parent_of = [], [], {}
    for j in root.findall("joint"):
        child = j.find("child").get("link")
        parent_of[child] = j.find("parent").get("link")
        if j.get("type") in ("revolute", "continuous", "prismatic"):
            joints.append(j.get("name"))
            children.append(child)
    links = [link.get("name") for link in root.findall("link")]
    base = next(link for link in links if link not in parent_of)
    return joints, [base] + children


# ------------------------------------------------------------------------------------------------ fake runtime
class _Checked:
    """Attribute bag that only allows the names the real Isaac Lab class defines."""

    def __init__(self, real_cls, values: dict):
        allowed = set(dir(real_cls)) | set(getattr(real_cls, "__annotations__", {}))
        for c in real_cls.__mro__:
            allowed |= set(getattr(c, "__annotations__", {}))
        object.__setattr__(self, "_real", real_cls)
        object.__setattr__(self, "_allowed", allowed)
        object.__setattr__(self, "_values", values)
        object.__setattr__(self, "used", set())

    def __getattr__(self, key):
        if key not in self._allowed:
            raise AttributeError(f"{self._real.__name__} has no attribute '{key}' (Isaac Lab API)")
        if key not in self._values:
            raise AttributeError(f"offline_check: no fake value for {self._real.__name__}.{key}; add it")
        self.used.add(key)
        return self._values[key]


def build_fake_env(torch, env_cfg, tc, joints, bodies, articulation_cls, articulation_data_cls, sensor_cls, sensor_data_cls,
                   ray_caster_data_cls, string_utils, seed=0):
    g = torch.Generator().manual_seed(seed)
    n, nj, nb = N_ENVS, len(joints), len(bodies)

    def U(lo, hi, *shape):
        return lo + (hi - lo) * torch.rand(*shape, generator=g)

    lim = torch.tensor([tc["limits"][j] for j in joints], dtype=torch.float32)
    mid, half = lim.mean(dim=1), 0.5 * (lim[:, 1] - lim[:, 0])
    soft = torch.stack([mid - 0.9 * half, mid + 0.9 * half], dim=1)     # soft_joint_pos_limit_factor 0.9 (robot.py)
    default = torch.tensor([tc["default_pos"][j] for j in joints]).repeat(n, 1)
    q = torch.clamp(default + U(-0.3, 0.3, n, nj), lim[:, 0], lim[:, 1])
    effort = torch.tensor([tc["effort"].get(j, 50.0) for j in joints]).repeat(n, 1)
    grav = torch.nn.functional.normalize(torch.tensor([0.0, 0.0, -1.0]) + U(-0.2, 0.2, n, 3), dim=1)
    root_pos = torch.cat([U(-1, 1, n, 2), tc["base_height"] + U(-0.05, 0.05, n, 1)], dim=1)
    body_pos = torch.cat([root_pos[:, None, :2] + U(-0.3, 0.3, n, nb, 2), U(0.0, 1.0, n, nb, 1)], dim=2)
    data = {
        "joint_names": joints, "body_names": bodies,
        "joint_pos": q, "joint_vel": U(-3, 3, n, nj), "joint_acc": U(-50, 50, n, nj),
        "default_joint_pos": default, "default_joint_vel": torch.zeros(n, nj),
        "joint_pos_limits": lim.repeat(n, 1, 1), "soft_joint_pos_limits": soft.repeat(n, 1, 1),
        "joint_effort_limits": effort, "joint_vel_limits": torch.tensor([tc["velocity"].get(j, 20.0) for j in joints]).repeat(n, 1),
        "applied_torque": effort * U(-1.0, 1.0, n, nj), "computed_torque": effort * U(-1.2, 1.2, n, nj),
        "joint_pos_target": default.clone(),
        "root_pos_w": root_pos, "root_quat_w": torch.tensor([1.0, 0, 0, 0]).repeat(n, 1),
        "root_lin_vel_b": U(-1, 1, n, 3), "root_ang_vel_b": U(-1, 1, n, 3),
        "root_lin_vel_w": U(-1, 1, n, 3), "root_ang_vel_w": U(-1, 1, n, 3),
        "projected_gravity_b": grav, "heading_w": U(-math.pi, math.pi, n),
        "body_pos_w": body_pos, "body_lin_vel_w": U(-1, 1, n, nb, 3), "body_ang_vel_w": U(-1, 1, n, nb, 3),
        "body_quat_w": torch.tensor([1.0, 0, 0, 0]).repeat(n, nb, 1),
    }

    class FakeArticulation:
        def __init__(self):
            self.data = _Checked(articulation_data_cls, data)
            self.joint_names, self.body_names = list(joints), list(bodies)
            self.num_joints, self.num_bodies = nj, nb
            self.num_instances = n
            self.device = "cpu"
            self.targets = default.clone()
            self.target_writes = 0

        def find_joints(self, name_keys, joint_subset=None, preserve_order=False):
            return string_utils.resolve_matching_names(name_keys, self.joint_names if joint_subset is None else joint_subset,
                                                       preserve_order)

        def find_bodies(self, name_keys, preserve_order=False):
            return string_utils.resolve_matching_names(name_keys, self.body_names, preserve_order)

        def set_joint_position_target(self, target, joint_ids=None, env_ids=None):
            rows = torch.arange(n) if env_ids is None or env_ids == slice(None) else torch.as_tensor(env_ids)
            cols = torch.arange(nj) if joint_ids is None or joint_ids == slice(None) else torch.as_tensor(joint_ids)
            self.targets[rows[:, None], cols[None, :]] = target
            self.target_writes += 1

    for name in ("find_joints", "find_bodies", "set_joint_position_target", "joint_names", "body_names", "num_joints", "data"):
        if not hasattr(articulation_cls, name):
            raise AttributeError(f"Articulation has no '{name}' (Isaac Lab API)")

    contact_bodies = list(bodies)
    nc = len(contact_bodies)
    forces = U(0, 200, n, nc, 3) * (torch.rand(n, nc, 1, generator=g) > 0.5)
    sensor_values = {"net_forces_w": forces, "net_forces_w_history": forces[:, None].repeat(1, 3, 1, 1),
                     "current_air_time": U(0, 1, n, nc), "last_air_time": U(0, 1, n, nc),
                     "current_contact_time": U(0, 1, n, nc), "last_contact_time": U(0, 1, n, nc)}

    class FakeContactSensor:
        def __init__(self, cfg):
            self.cfg = cfg
            self.data = _Checked(sensor_data_cls, sensor_values)
            self.body_names, self.num_bodies = contact_bodies, nc

        def find_bodies(self, name_keys, preserve_order=False):
            return string_utils.resolve_matching_names(name_keys, self.body_names, preserve_order)

    class FakeRayCaster:
        def __init__(self, cfg):
            self.cfg = cfg
            hits = torch.cat([root_pos[:, None, :2] + U(-0.3, 0.3, n, 169, 2), U(-0.05, 0.05, n, 169, 1)], dim=2)
            self.data = _Checked(ray_caster_data_cls, {"ray_hits_w": hits, "pos_w": root_pos + torch.tensor([0, 0, 20.0])})

    scene_cfg = env_cfg.scene
    entities = {"robot": FakeArticulation()}
    sensors = {}
    if getattr(scene_cfg, "contact_forces", None) is not None:
        sensors["contact_forces"] = FakeContactSensor(scene_cfg.contact_forces)
    if getattr(scene_cfg, "height_scanner", None) is not None:
        sensors["height_scanner"] = FakeRayCaster(scene_cfg.height_scanner)
    for name in dir(scene_cfg):                                    # extra ray casters (e.g. foot scanners)
        cfg = getattr(scene_cfg, name, None)
        if name not in sensors and type(cfg).__name__ == "RayCasterCfg":
            sensors[name] = FakeRayCaster(cfg)

    class FakeScene(dict):
        def __init__(self):
            super().__init__({**entities, **sensors})
            self.sensors, self.articulations = sensors, entities
            self.env_origins = torch.zeros(n, 3)

    class Commands:
        def __init__(self):
            r = env_cfg.commands.base_velocity.ranges
            self.cmd = torch.stack([U(*r.lin_vel_x, n), U(*r.lin_vel_y, n), U(*r.ang_vel_z, n)], dim=1)
            self.cmd[:2] = 0.0                                        # two standing envs

        def get_command(self, name):
            assert name == "base_velocity", name
            return self.cmd

    class Actions:
        def __init__(self, dim):
            self.action, self.prev_action = U(-1, 1, n, dim), U(-1, 1, n, dim)

    class Terminations:
        terminated = torch.tensor([True, False] * (n // 2))
        time_outs = torch.tensor([False, False, True, False] * (n // 4))

    class FakeSim:
        dt = env_cfg.sim.dt

        @staticmethod
        def is_playing():
            return False

    class FakeEnv:
        pass

    env = FakeEnv()
    env.num_envs, env.device, env.cfg, env.sim = n, "cpu", env_cfg, FakeSim()
    env.physics_dt, env.step_dt = env_cfg.sim.dt, env_cfg.sim.dt * env_cfg.decimation
    env.episode_length_buf = torch.randint(0, 1000, (n,), generator=g)
    env.max_episode_length = math.ceil(env_cfg.episode_length_s / env.step_dt)
    env.max_episode_length_s = env_cfg.episode_length_s
    env.common_step_counter = 0
    env.scene = FakeScene()
    env.command_manager = Commands()
    env.action_manager = Actions(len(tc["policy_joints"]))
    env.termination_manager = Terminations()
    env.reset_buf = Terminations.terminated | Terminations.time_outs
    return env


# ------------------------------------------------------------------------------------------------ checks
class Report:
    def __init__(self):
        self.items = []

    def add(self, task, check, ok, detail=""):
        self.items.append({"task": task, "check": check, "ok": bool(ok), "detail": detail})
        print(f"  [{'PASS' if ok else 'FAIL'}] {check}" + (f": {detail}" if detail else ""))

    @property
    def failed(self):
        return [i for i in self.items if not i["ok"]]


def term_items(group_cfg):
    """(name, term cfg) pairs of a manager config object, in declaration order, skipping None/disabled terms."""
    out = []
    for name, value in group_cfg.__dict__.items():
        if name.startswith("_") or value is None:
            continue
        if hasattr(value, "func"):
            out.append((name, value))
    return out


def find_missing(obj, path="", seen=None):
    """Dotted paths of dataclasses.MISSING values left in a configclass tree."""
    seen = seen if seen is not None else set()
    if id(obj) in seen:
        return []
    seen.add(id(obj))
    out = []
    items = obj.items() if isinstance(obj, dict) else getattr(obj, "__dict__", {}).items()
    for k, v in items:
        if isinstance(k, str) and k.startswith("_"):
            continue
        p = f"{path}.{k}" if path else str(k)
        if v is dataclasses.MISSING:
            out.append(p)
        elif dataclasses.is_dataclass(v) or isinstance(v, dict):
            out += find_missing(v, p, seen)
    return out


def check_task(task_id, reg, rep, mods, tc_default):
    torch, np = mods["torch"], mods["np"]
    ManagerBase, SceneEntityCfg = mods["ManagerBase"], mods["SceneEntityCfg"]
    print(f"\n== {task_id}")
    module_name, cls_name = reg["env_cfg_entry_point"].split(":")
    env_mod = importlib.import_module(module_name)
    env_cfg = getattr(env_mod, cls_name)()
    rep.add(task_id, "env config instantiates", True, f"{module_name}:{cls_name}")
    missing = find_missing(env_cfg)
    ignorable = {"scene.robot.spawn.usd_path"}                     # none expected; listed for visibility
    rep.add(task_id, "no MISSING fields", not [m for m in missing if m not in ignorable], ", ".join(missing))
    entry_mod, entry_cls = reg["entry_point"].split(":")
    rep.add(task_id, "gym entry point resolves", hasattr(importlib.import_module(entry_mod), entry_cls), reg["entry_point"])

    tc = tc_default                                                   # rough inherits every field used here
    joints, bodies = mods["robot_joints"], mods["robot_bodies"]
    env = build_fake_env(torch, env_cfg, tc, joints, bodies, mods["Articulation"], mods["ArticulationData"], mods["ContactSensor"],
                         mods["ContactSensorData"], mods["RayCasterData"], mods["string_utils"])

    # 2 + 3: term resolution exactly as the managers do it, then scene entity resolution
    stub = types.SimpleNamespace(_env=env)
    managers = [("observations." + g, getattr(env_cfg.observations, g), 1) for g in ("policy", "critic")
                if getattr(env_cfg.observations, g, None) is not None]
    managers += [("rewards", env_cfg.rewards, 1), ("terminations", env_cfg.terminations, 1), ("events", env_cfg.events, 2),
                 ("curriculum", env_cfg.curriculum, 2)]
    resolved = {}
    for mname, group, argc in managers:
        for tname, term in term_items(group):
            key = f"{mname}.{tname}"
            try:
                ManagerBase._resolve_common_term_cfg(stub, key, term, min_argc=argc)
                for pv in term.params.values():
                    if isinstance(pv, SceneEntityCfg):
                        pv.resolve(env.scene)
                resolved[key] = term
            except Exception as e:                                    # noqa: BLE001 - report every term
                rep.add(task_id, f"term {key}", False, f"{type(e).__name__}: {e}")
    rep.add(task_id, "all manager terms resolve (signature + scene entities)",
            len(resolved) == sum(len(term_items(g)) for _, g, _ in managers), f"{len(resolved)} terms")

    # 4: evaluate observation / reward / termination terms
    dims = {}
    for key, term in resolved.items():
        if key.startswith(("events", "curriculum")):
            continue
        try:
            out = term.func(env, **term.params)
            if key.startswith("observations"):
                ok = out.ndim == 2 and out.shape[0] == N_ENVS
                dims[key] = out.shape[1]
            else:
                ok = out.shape == (N_ENVS,)
            ok = ok and bool(torch.isfinite(out.float()).all())
            if not ok:
                rep.add(task_id, f"evaluate {key}", False, f"shape {tuple(out.shape)}")
        except Exception as e:                                        # noqa: BLE001
            rep.add(task_id, f"evaluate {key}", False, f"{type(e).__name__}: {e}")
            dims[key] = None
    evaluated = [k for k in resolved if not k.startswith(("events", "curriculum"))]
    rep.add(task_id, "observation/reward/termination terms evaluate", all(dims.get(k, 0) is not None for k in evaluated),
            f"{len(evaluated)} terms on {N_ENVS} fake envs")
    rl_cfg = mods["rl_config"].load(REPO / "rl" / "config" / "jx1_walk.yaml")
    for group, want in (("policy", rl_cfg.num_obs), ("critic", rl_cfg.num_privileged_obs)):
        size = sum(v or 0 for k, v in dims.items() if k.startswith(f"observations.{group}."))
        rep.add(task_id, f"{group} observation size == MuJoCo task ({'obs' if group == 'policy' else 'privileged obs'})",
                size == want, f"{size} vs {want}")

    # 5: observation parity with the MuJoCo / ROS 2 layout
    pio = mods["policy_io"]
    S = tc["raw"]["observation"]["scales"]
    obs = []
    for tname, term in term_items(env_cfg.observations.policy):
        v = term.func(env, **term.params).float()
        if term.scale is not None:
            v = v * torch.as_tensor(term.scale, dtype=torch.float32)
        obs.append(v)
    obs = torch.cat(obs, dim=1).numpy()
    rob = env.scene["robot"]
    pj = [joints.index(j) for j in tc["policy_joints"]]
    q = rob.data.joint_pos.numpy()
    t = (env.episode_length_buf.float() * env.step_dt).numpy()
    ref = pio.build_observation(rob.data.root_ang_vel_b.numpy(), rob.data.projected_gravity_b.numpy(), env.command_manager.cmd.numpy(),
                                q[:, pj] - rob.data.default_joint_pos.numpy()[:, pj], rob.data.joint_vel.numpy()[:, pj],
                                env.action_manager.action.numpy(), pio.gait_phase(t, tc["raw"]["gait"]["period_s"]), S,
                                tc["raw"]["observation"]["clip"])
    err = float(np.abs(obs - ref).max()) if obs.shape == ref.shape else float("inf")
    rep.add(task_id, "policy observation == policy_io.build_observation (MuJoCo / ROS 2)", err < 1e-5,
            f"max |diff| {err:.2e}, shape {obs.shape} vs {ref.shape}")

    # critic parity with the privileged part of rl/jx1_rl/env.py observations(), heights from the local ground
    crit = []
    for tname, term in term_items(env_cfg.observations.critic):
        v = term.func(env, **term.params).float()
        crit.append(v * torch.as_tensor(term.scale, dtype=torch.float32) if term.scale is not None else v)
    crit = torch.cat(crit, dim=1).numpy()
    ground_cfg = env_cfg.rewards.base_height_l2.params.get("ground_cfg")

    def ground(xy):                                                   # nearest scanner hit (independent of jx1 mdp code)
        if ground_cfg is None:
            return np.zeros(xy.shape[:-1])
        hits = env.scene.sensors[ground_cfg.name].data.ray_hits_w.numpy()
        d = ((xy[:, :, None, :] - hits[:, None, :, :2]) ** 2).sum(-1)
        return np.take_along_axis(hits[..., 2], d.argmin(-1), axis=1)

    feet = [mods["robot_bodies"].index(f) for f in ("left_foot_link", "right_foot_link")]
    root = rob.data.root_pos_w.numpy()
    sole = rob.data.body_pos_w.numpy()[:, feet] + np.array(tc["sole_offset"])   # fake feet are level (identity quaternions)
    force = env.scene.sensors["contact_forces"].data.net_forces_w.numpy()[:, feet]
    h_base = root[:, 2] - ground(root[:, None, :2])[:, 0]
    priv = np.concatenate([ref, rob.data.root_lin_vel_b.numpy() * S["lin_vel"], (h_base - tc["base_height"])[:, None] * 5.0,
                           (np.linalg.norm(force, axis=-1) > 1.0).astype(np.float64), (sole[..., 2] - ground(sole[..., :2])) * 10.0], axis=1)
    err = float(np.abs(crit - priv).max()) if crit.shape == priv.shape else float("inf")
    rep.add(task_id, "critic observation == MuJoCo privileged observation" + (" (terrain-relative heights)" if ground_cfg else ""),
            err < 1e-4, f"max |diff| {err:.2e}, shape {crit.shape} vs {priv.shape}")

    # 6: action term vs the MuJoCo action pipeline (clamp, ankle polygon, hub ramp, delay, reset)
    check_action_term(task_id, env_cfg, env, tc, joints, rep, mods)

    # 7: actuators
    check_actuators(task_id, env_cfg, tc, joints, rep, mods)
    return env_cfg


def check_action_term(task_id, env_cfg, env, tc, joints, rep, mods):
    torch, np, pio = mods["torch"], mods["np"], mods["policy_io"]
    cfg = env_cfg.actions.joint_pos
    try:
        term = cfg.class_type(cfg, env)
    except Exception as e:                                            # noqa: BLE001
        rep.add(task_id, "action term instantiates", False, f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
        return
    rob = env.scene["robot"]
    pol = tc["policy_joints"]
    pj = [joints.index(j) for j in pol]
    rep.add(task_id, "action term joints == policy_joints (order)", list(term._joint_names) == pol, f"{term.action_dim} actions")
    lim = np.array([tc["limits"][j] for j in pol])
    default = np.array([tc["default_pos"][j] for j in pol])
    polys = {s: np.radians(np.array(p, dtype=float)) for s, p in tc["polygons_deg"].items()}
    dec = env_cfg.decimation
    delay = getattr(term, "_delay", None)
    g = torch.Generator().manual_seed(1)
    prev = np.repeat(default[None], N_ENVS, axis=0)                   # MuJoCo prev_ctrl after reset = hold pose
    term.reset(None)
    worst = 0.0
    for step in range(4):
        a = (torch.rand(N_ENVS, len(pol), generator=g) * 6 - 3)        # beyond the limits on purpose
        if step == 2:                                                  # reset half of the envs mid-run
            ids = torch.arange(0, N_ENVS, 2)
            term.reset(ids)
            prev[ids.numpy()] = default
        target = pio.clip_ankle_targets(pio.actions_to_targets(a.numpy(), default, tc["raw"]["action_scale"], lim[:, 0], lim[:, 1]),
                                        pol, polys)
        term.process_actions(a)
        d = np.zeros(N_ENVS, dtype=int) if delay is None else delay.numpy()
        for k in range(1, dec + 1):
            term.apply_actions()
            alpha = k / dec if cfg.hub_interpolation else 1.0
            expect = prev + alpha * (target - prev)
            late = d >= k
            expect[late] = prev[late]
            got = rob.targets[:, pj].numpy()
            worst = max(worst, float(np.abs(got - expect).max()))
        prev = target
    rep.add(task_id, "action targets == MuJoCo pipeline every substep (clamp, ankle polygon, hub ramp, delay, reset)", worst < 1e-5,
            f"max |diff| {worst:.2e} rad over 4 steps x {dec} substeps")


def check_actuators(task_id, env_cfg, tc, joints, rep, mods):
    su = mods["string_utils"]
    robot = env_cfg.scene.robot
    seen = {}
    problems = []
    for gname, act in robot.actuators.items():
        ids, names = su.resolve_matching_names(act.joint_names_expr, joints)
        for j in names:
            if j in seen:
                problems.append(f"{j} in {seen[j]} and {gname}")
            seen[j] = gname
        for field in ("stiffness", "damping", "effort_limit_sim", "velocity_limit_sim", "armature"):
            val = getattr(act, field)
            if isinstance(val, dict):
                _, vnames, vals = su.resolve_matching_names_values(val, names)
                if sorted(vnames) != sorted(names):
                    problems.append(f"{gname}.{field} misses {sorted(set(names) - set(vnames))}")
                for j, v in zip(vnames, vals):
                    if field == "stiffness" and abs(v - tc["gains"][j][0]) > 1e-9:
                        problems.append(f"{j} kp {v} != {tc['gains'][j][0]}")
                    if field == "damping" and abs(v - tc["gains"][j][1]) > 1e-9:
                        problems.append(f"{j} kd {v} != {tc['gains'][j][1]}")
            elif val is None:
                problems.append(f"{gname}.{field} unset")
    uncovered = [j for j in joints if j not in seen]
    rep.add(task_id, "actuator groups cover every joint once with the task gains and limits", not problems and not uncovered,
            "; ".join(problems + [f"uncovered {uncovered}"] if uncovered else problems) or f"{len(seen)} joints in {len(robot.actuators)} groups")
    _, names, _ = su.resolve_matching_names_values(robot.init_state.joint_pos, joints)
    rep.add(task_id, "initial joint positions resolve", sorted(names) == sorted(joints), f"{len(names)}/{len(joints)}")


def check_agent(task_id, reg, rep, mods):
    module_name, cls_name = reg["rsl_rl_cfg_entry_point"].split(":")
    agent = getattr(importlib.import_module(module_name), cls_name)()
    missing = find_missing(agent)
    rep.add(task_id, "rsl_rl runner config: no MISSING fields", not missing, ", ".join(missing))
    d = agent.to_dict()
    rep.add(task_id, "rsl_rl obs_groups", d.get("obs_groups") == {"policy": ["policy"], "critic": ["critic"]}, str(d.get("obs_groups")))
    if mods.get("rsl_rl") is None:
        return
    from rsl_rl.algorithms import PPO
    from rsl_rl.modules import ActorCritic
    pol = {k: v for k, v in d["policy"].items() if k != "class_name"}
    sig = inspect.signature(ActorCritic.__init__).parameters
    extra = [k for k in pol if k not in sig]
    rep.add(task_id, "policy keys accepted by rsl_rl ActorCritic", not extra, f"unknown {extra}" if extra else f"{len(pol)} keys")
    alg = {k: v for k, v in d["algorithm"].items() if k != "class_name"}
    sig = inspect.signature(PPO.__init__).parameters
    extra = [k for k in alg if k not in sig]
    rep.add(task_id, "algorithm keys accepted by rsl_rl PPO", not extra, f"unknown {extra}" if extra else f"{len(alg)} keys")
    runner_src = inspect.getsource(importlib.import_module("rsl_rl.runners.on_policy_runner"))
    rep.add(task_id, "empirical_normalization unset (deprecated in rsl_rl >= 3)", d.get("empirical_normalization") is None
            or "empirical_normalization" not in runner_src, str(d.get("empirical_normalization")))


def check_scripts(rep, mods):
    """train.py / export_policy.py: every `from X import Y` exists and keyword arguments match the real signatures."""
    import ast
    for script in ("train.py", "export_policy.py"):
        tree = ast.parse((PKG / "scripts" / script).read_text(encoding="utf-8"))
        names, problems = {}, []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0 and not node.module.startswith("jx1"):
                try:
                    mod = importlib.import_module(node.module)
                except Exception as e:                                # noqa: BLE001
                    problems.append(f"import {node.module}: {e}")
                    continue
                for alias in node.names:
                    if not hasattr(mod, alias.name):
                        problems.append(f"{node.module}.{alias.name} does not exist")
                    else:
                        names[alias.asname or alias.name] = getattr(mod, alias.name)
        calls = 0
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            target, label = None, None
            if isinstance(node.func, ast.Name) and node.func.id in names:
                target, label = names[node.func.id], node.func.id
            elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "runner":
                target, label = getattr(names.get("OnPolicyRunner"), node.func.attr, None), f"runner.{node.func.attr}"
            if target is None or isinstance(target, _Mock):
                continue
            try:
                params = inspect.signature(target).parameters
            except (TypeError, ValueError):
                continue
            calls += 1
            if any(p.kind == p.VAR_KEYWORD for p in params.values()):
                continue
            problems += [f"{label}({kw.arg}=...) not accepted" for kw in node.keywords if kw.arg and kw.arg not in params]
        rep.add("scripts", f"{script}: imports exist, keyword arguments match the Isaac Lab / rsl_rl signatures", not problems,
                "; ".join(problems) or f"{len(names)} imported names, {calls} calls checked")


def check_exporter(rep, mods):
    """export_offline.py against the real rsl_rl ActorCritic (>= 3) and a synthetic rsl_rl 2.x checkpoint."""
    torch, np = mods["torch"], mods["np"]
    import onnxruntime as ort
    import export_offline
    tc = mods["tc"]
    rl_cfg = mods["rl_config"].load(REPO / "rl" / "config" / "jx1_walk.yaml")
    n, n_obs, n_priv, P = rl_cfg.num_actions, rl_cfg.num_obs, rl_cfg.num_privileged_obs, tc["raw"]["ppo"]
    root = PKG / ".cache" / "offline_check"
    root.mkdir(parents=True, exist_ok=True)
    x = torch.randn(32, n_obs) * 2.0

    def onnx(bundle):
        return ort.InferenceSession(str(bundle / "policy.onnx")).run(["actions"], {"obs": x.numpy()})[0]

    if mods.get("rsl_rl") is not None:
        from rsl_rl.modules import ActorCritic
        torch.manual_seed(0)
        ac = ActorCritic({"policy": torch.zeros(1, n_obs), "critic": torch.zeros(1, n_priv)}, {"policy": ["policy"], "critic": ["critic"]}, n,
                         actor_obs_normalization=True, critic_obs_normalization=True, actor_hidden_dims=P["actor_hidden"],
                         critic_hidden_dims=P["critic_hidden"], activation=P["activation"], init_noise_std=P["init_noise_std"])
        for _ in range(3):
            ac.actor_obs_normalizer.update(torch.randn(256, n_obs) * 3.0 + 1.0)     # non-trivial running statistics
        ac.eval()
        ck = root / "rsl_rl3_model_1234.pt"
        torch.save({"model_state_dict": ac.state_dict(), "optimizer_state_dict": {}, "iter": 1234, "infos": None}, ck)
        res = export_offline.export(ck, root / "bundle_rsl_rl3")
        with torch.no_grad():
            want = ac.act_inference({"policy": x, "critic": torch.zeros(32, n_priv)}).numpy()
        err = float(np.abs(onnx(root / "bundle_rsl_rl3") - want).max())
        rep.add("export", "export_offline ONNX == rsl_rl 3 ActorCritic.act_inference (normaliser in the policy)", err < 1e-4,
                f"max |diff| {err:.2e}; {res['format']}")
    # rsl_rl 2.x layout: plain actor state dict + runner normaliser
    g = torch.Generator().manual_seed(1)
    dims = [n_obs] + list(P["actor_hidden"]) + [n]
    sd = {}
    for i, (a, b) in enumerate(zip(dims[:-1], dims[1:])):
        sd[f"actor.{2 * i}.weight"] = torch.randn(b, a, generator=g) / math.sqrt(a)
        sd[f"actor.{2 * i}.bias"] = torch.randn(b, generator=g) * 0.1
    sd["std"] = torch.ones(n)
    mean, std = torch.randn(1, n_obs, generator=g), torch.rand(1, n_obs, generator=g) * 3 + 0.1
    ck = root / "rsl_rl2_model_500.pt"
    torch.save({"model_state_dict": sd, "optimizer_state_dict": {}, "iter": 500, "infos": None,
                "obs_norm_state_dict": {"_mean": mean, "_var": std ** 2, "_std": std, "count": torch.tensor(1000)}}, ck)
    export_offline.export(ck, root / "bundle_rsl_rl2")
    h = ((x - mean) / (std + 1e-2)).numpy()
    for i in range(len(dims) - 1):
        h = h @ sd[f"actor.{2 * i}.weight"].numpy().T + sd[f"actor.{2 * i}.bias"].numpy()
        if i < len(dims) - 2:
            h = np.where(h > 0, h, np.expm1(h))                        # ELU
    err = float(np.abs(onnx(root / "bundle_rsl_rl2") - h).max())
    rep.add("export", "export_offline ONNX == hand-computed rsl_rl 2.x actor (runner normaliser)", err < 1e-4, f"max |diff| {err:.2e}")
    import yaml
    io = yaml.safe_load((root / "bundle_rsl_rl2" / "policy_io.yaml").read_text(encoding="utf-8"))
    ok = io["format"] == "jx1-policy-io/1" and io["policy"]["num_obs"] == n_obs and len(io["default_joint_pos"]) == len(mods["robot_joints"])
    rep.add("export", "exported policy_io.yaml: jx1-policy-io/1, whole robot", ok, f"{len(io['default_joint_pos'])} joints")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--isaaclab", type=Path, required=True, help="Isaac Lab source checkout (git clone, any 2.x tag)")
    ap.add_argument("--rsl-rl", type=Path, default=None, help="rsl_rl sources (folder containing the rsl_rl package)")
    ap.add_argument("--json", type=Path, default=None)
    args = ap.parse_args()

    finder = install_import_hooks(args.isaaclab, args.rsl_rl)
    import numpy as np
    import torch
    import isaaclab
    import isaaclab.envs  # noqa: F401  (import order of the Isaac Lab scripts: envs before managers)
    from isaaclab.assets import Articulation
    from isaaclab.assets.articulation.articulation_data import ArticulationData
    from isaaclab.managers import SceneEntityCfg
    from isaaclab.managers.manager_base import ManagerBase
    from isaaclab.sensors import ContactSensor
    from isaaclab.sensors.contact_sensor.contact_sensor_data import ContactSensorData
    from isaaclab.sensors.ray_caster.ray_caster_data import RayCasterData
    from isaaclab.utils import string as string_utils

    from jx1_rl import config as rl_config
    from jx1_rl import policy_io
    import jx1_isaaclab  # noqa: F401  (registers the tasks into GYM_REGISTRY)
    from jx1_isaaclab import task_config

    sys.path.insert(0, str(PKG / "scripts"))
    tc = task_config.load()
    joints, bodies = robot_from_urdf(task_config.URDF)
    mods = {"torch": torch, "np": np, "ManagerBase": ManagerBase, "SceneEntityCfg": SceneEntityCfg, "Articulation": Articulation,
            "ArticulationData": ArticulationData, "ContactSensor": ContactSensor, "ContactSensorData": ContactSensorData,
            "RayCasterData": RayCasterData, "string_utils": string_utils, "policy_io": policy_io, "task_config": task_config,
            "rl_config": rl_config, "tc": tc, "robot_joints": joints, "robot_bodies": bodies}
    try:
        import rsl_rl  # noqa: F401
        mods["rsl_rl"] = rsl_rl if "rsl_rl" not in finder.mocked else None
    except ImportError:
        mods["rsl_rl"] = None
    version = getattr(isaaclab, "__version__", "?")
    print(f"Isaac Lab {version} from {args.isaaclab}; rsl_rl {'real' if mods['rsl_rl'] else 'not checked'}")
    print(f"robot: {len(joints)} movable joints, {len(bodies)} bodies after merge_fixed_joints (URDF {task_config.URDF.name})")
    print(f"mocked modules: {sorted(finder.mocked)}")

    rep = Report()
    for task_id, reg in sorted(GYM_REGISTRY.items()):
        try:
            check_task(task_id, reg, rep, mods, tc)
            check_agent(task_id, reg, rep, mods)
        except Exception as e:                                        # noqa: BLE001
            rep.add(task_id, "task check ran", False, f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    for name, fn in (("scripts", check_scripts), ("export", check_exporter)):
        print(f"\n== {name}")
        try:
            fn(rep, mods)
        except Exception as e:                                        # noqa: BLE001
            rep.add(name, f"{name} check ran", False, f"{type(e).__name__}: {e}\n{traceback.format_exc()}")
    print(f"\n{len(rep.items) - len(rep.failed)}/{len(rep.items)} checks passed over {len(GYM_REGISTRY)} tasks")
    if args.json:
        args.json.write_text(json.dumps({"isaaclab_version": version, "isaaclab_source": args.isaaclab.as_posix(),
                                         "rsl_rl_checked": mods["rsl_rl"] is not None, "mocked_modules": sorted(finder.mocked),
                                         "tasks": sorted(GYM_REGISTRY), "checks": rep.items}, indent=1), encoding="utf-8")
    return 1 if rep.failed else 0


if __name__ == "__main__":
    sys.exit(main())
