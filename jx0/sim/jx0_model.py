"""MuJoCo model of JX0 generated from jx0/design_point.yaml (masses and geometry), for planning, simulation and renders.

Joint, body and site names follow the analysis convention (pelvis, l_hip_yaw ... r_ankle_roll, l_sole, r_sole, imu), so
the JX1 gait pipeline (calculations/jx1calc) plans on this model directly. Arms (shoulder pitch/roll, elbow) and the neck
are separate bodies with joints, so the robot can wave and look around; the leg analysis lumps them into upper_body.
Collision: feet only (plus the floor). Actuators are torque motors; the servo behaviour (position control, stiffness,
torque-speed limit) is applied in Python by `ServoModel` in walk_jx0.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "calculations"))
from jx1calc.design import Design, LEG_JOINTS, LEG_LINKS  # noqa: E402
from jx1calc.mjcf import AXES, joint_armature, joint_range_rad  # noqa: E402

DESIGN = ROOT / "jx0" / "design_point.yaml"
SERVO = (0.0452, 0.0247, 0.035)                 # ST3215 body (ASSUMED until the datasheet check)
WHITE, BLACK, ORANGE, GREY, RUBBER = ".93 .93 .95 1", ".12 .12 .14 1", ".95 .42 .11 1", ".55 .57 .6 1", ".08 .08 .08 1"
ARM_JOINTS = ["shoulder_pitch", "shoulder_roll", "elbow"]
ARM_MASS = {"upper_arm": 0.020, "forearm": 0.008}   # CAD printed link + MG90S elbow (upper arm), each (ESTIMATED)
HEAD_MASS = 0.057                                    # CAD head shell 43 g + round display + camera (ESTIMATED)
SMALL_SERVO_STALL = 0.45                         # N·m, arm/neck servos (ASSUMED; see the BOM)


def _f(x):
    return " ".join(f"{float(v):.6g}" for v in np.atleast_1d(x))


def _box(size, pos=(0, 0, 0), rgba=WHITE, euler=None, name=None, collide=False):
    e = f' euler="{_f(euler)}"' if euler is not None else ""
    n = f' name="{name}"' if name else ""
    c = "" if collide else ' contype="0" conaffinity="0"'
    return f'<geom{n} type="box" size="{_f(np.array(size) / 2)}" pos="{_f(pos)}"{e} rgba="{rgba}"{c}/>'


CAD = ROOT / "jx0" / "cad"
PART_RGBA = {"JX0_Head": ORANGE, "JX0_Servo_ST3215": BLACK, "JX0_Servo_MG90S": ".15 .3 .75 1"}


def cad_visuals():
    """(asset xml, {link: [geom xml]}) with the SolidWorks STL meshes at the CAD component poses, or (None, {}) if absent."""
    stl = CAD / "stl"
    if not (stl / "JX0_Torso.stl").exists():
        return None, {}
    sys.path.insert(0, str(CAD))
    from layout import components, link_of
    import mujoco as _mj
    assets, geoms = set(), {}
    for key, part, M in components():
        link, origin = link_of(key)
        assets.add(part)
        q = np.zeros(4)
        _mj.mju_mat2Quat(q, np.ascontiguousarray(M[:3, :3]).flatten())
        pos = M[:3, 3] - origin * 1e-3
        rgba = PART_RGBA.get(part, WHITE)
        geoms.setdefault(link, []).append(
            f'<geom type="mesh" mesh="m_{part}" pos="{_f(pos)}" quat="{_f(q)}" rgba="{rgba}" contype="0" conaffinity="0"/>')
    asset = chr(10).join(f'<mesh name="m_{a}" file="{(stl / (a + ".stl")).as_posix()}" scale="0.001 0.001 0.001"/>' for a in sorted(assets))
    return asset, geoms


def _inertial(link, mirror=False):
    com = np.array(link.com, float) * (np.array([1, -1, 1]) if mirror else 1)
    return f'<inertial pos="{_f(com)}" mass="{link.mass:.6g}" diaginertia="{_f(np.maximum(link.inertia, 1e-7))}"/>'


def build(design: Design | None = None, timestep: float = 0.001) -> str:
    d = design or Design(DESIGN)
    hs = d.hip_spacing / 2
    ub = d.raw["upper_body_geometry"]
    sh = np.array(ub["shoulder_pitch_origin"]["value"], float)
    la, lf = ub["upper_arm_m"]["value"], ub["forearm_m"]["value"]
    neck = np.array(ub["neck_yaw_origin"]["value"], float)
    hsz = np.array(ub["head_size_m"]["value"], float)
    ubr = d.raw["upper_body_joint_ranges_deg"]
    sx, sy, sz = SERVO

    def leg(side):
        sgn = 1 if side == "l" else -1
        vis = {
            "hip_yaw_link": [_box((0.05, 0.035, 0.006), (0, 0, 0.012)),                           # yaw horn plate
                             _box((sx, sz, sy), (-0.02, 0, -0.002), BLACK)],                       # hip-roll servo (axis x)
            "hip_roll_link": [_box((0.045, 0.006, 0.05), (0, sgn * -0.004, 0)),
                              _box((sx, sy, sz), (0, sgn * 0.018, 0), BLACK, euler=(90, 0, 0))],   # hip-pitch servo (axis y)
            "thigh": [_box((0.034, 0.004, d.thigh), (0, 0.018, -d.thigh / 2)), _box((0.034, 0.004, d.thigh), (0, -0.018, -d.thigh / 2)),
                      _box((sz, sy, sx), (0, 0, -d.thigh + 0.012), BLACK)],                         # knee servo
            "shin": [_box((0.034, 0.004, d.shin), (0, 0.018, -d.shin / 2)), _box((0.034, 0.004, d.shin), (0, -0.018, -d.shin / 2)),
                     _box((sz, sy, sx), (0, 0, -d.shin + 0.024), BLACK)],                           # ankle-pitch servo
            "ankle_cross": [_box((sx, sz, sy), (0, 0, -0.012), BLACK)],                             # ankle-roll servo
            "foot": [_box((d.foot_length, d.foot_width, 0.006), (d.foot_center_x, 0, -d.sole_to_ankle + 0.005)),
                     _box((d.foot_length, d.foot_width, 0.002), (d.foot_center_x, 0, -d.sole_to_ankle + 0.001), RUBBER,
                          name=f"{side}_foot_geom", collide=True),
                     f'<site name="{side}_sole" pos="0 0 {-d.sole_to_ankle}" size="0.005"/>'],
        }
        offs = {"hip_yaw_link": [0, sgn * hs, 0], "hip_roll_link": [0, 0, 0], "thigh": [0, 0, 0],
                "shin": [0, 0, -d.thigh], "ankle_cross": [0, 0, -d.shin], "foot": [0, 0, 0]}
        xml = []
        for jn, ln in zip(LEG_JOINTS, LEG_LINKS):
            lo, hi = joint_range_rad(d, jn, side)
            xml.append(f'<body name="{side}_{ln}" pos="{_f(offs[ln])}">')
            xml.append(_inertial(d.links[ln], side == "r"))
            xml.append(f'<joint name="{side}_{jn}" axis="{AXES[jn]}" range="{lo:.6f} {hi:.6f}" armature="{joint_armature(d, jn):.5g}" damping="0.01"/>')
            if cadv:
                xml += cadv.get(f"{side}_{ln}", [])
                if ln == "foot":                                    # keep the contact box and the sole site
                    xml += [g for g in vis[ln] if "collide" in g or "contype" not in g or "site" in g][-2:]
            else:
                xml += vis[ln]
        xml.append("</body>" * len(LEG_JOINTS))
        return "\n".join(xml)

    asset_xml, cadv = cad_visuals()

    def arm(side):
        sgn = 1 if side == "l" else -1
        rng = {j: np.radians([ubr[j]["min"], ubr[j]["max"]]) for j in ARM_JOINTS}
        if side == "r":
            rng["shoulder_roll"] = -rng["shoulder_roll"][::-1]
        ax = {"shoulder_pitch": "0 1 0", "shoulder_roll": "1 0 0", "elbow": "0 1 0"}
        mu, mf = ARM_MASS["upper_arm"], ARM_MASS["forearm"]
        return f"""<body name="{side}_shoulder" pos="{_f(sh * [1, sgn, 1])}">
  <inertial pos="0 0 0" mass="0.02" diaginertia="2e-6 2e-6 2e-6"/>
  <joint name="{side}_shoulder_pitch" axis="{ax['shoulder_pitch']}" range="{rng['shoulder_pitch'][0]:.4f} {rng['shoulder_pitch'][1]:.4f}" damping="0.01" armature="0.0005"/>
  {"".join(cadv.get(f"{side}_shoulder", [])) if cadv else _box((0.03, 0.022, 0.03), (0, sgn * 0.012, 0), BLACK)}
  <body name="{side}_upper_arm" pos="0 {sgn * 0.010} -0.016">
    <inertial pos="0 0 {-la / 2}" mass="{mu}" diaginertia="{mu * la * la / 12:.3g} {mu * la * la / 12:.3g} 1e-6"/>
    <joint name="{side}_shoulder_roll" axis="{ax['shoulder_roll']}" range="{rng['shoulder_roll'][0]:.4f} {rng['shoulder_roll'][1]:.4f}" damping="0.01" armature="0.0005"/>
    {"".join(cadv.get(f"{side}_upper_arm", [])) if cadv else _box((0.026, 0.026, la), (0, 0, -la / 2))}
    <body name="{side}_forearm" pos="0.008 0 {-la}">
      <inertial pos="0 0 {-lf / 2}" mass="{mf}" diaginertia="{mf * lf * lf / 12:.3g} {mf * lf * lf / 12:.3g} 1e-6"/>
      <joint name="{side}_elbow" axis="{ax['elbow']}" range="{rng['elbow'][0]:.4f} {rng['elbow'][1]:.4f}" damping="0.01" armature="0.0005"/>
      {"".join(cadv.get(f"{side}_forearm", [])) if cadv else _box((0.02, 0.022, lf), (0, 0, -lf / 2))}
    </body>
  </body>
</body>"""

    # torso = lumped upper body minus the arms and head modelled above
    ubl = d.links["upper_body"]
    arms_head = 2 * (0.02 + ARM_MASS["upper_arm"] + ARM_MASS["forearm"]) + HEAD_MASS
    torso_m = ubl.mass - arms_head
    nr = np.radians([ubr["neck_yaw"]["min"], ubr["neck_yaw"]["max"]])
    if cadv:
        pelvis_vis, torso_vis, head_vis = ("".join(cadv.get(k, [])) for k in ("pelvis", "torso", "head"))
    else:
        pelvis_vis = (_box((0.06, 0.13, 0.024), (0, 0, 0.034)) + _box((sx, sy, sz), (0, hs, 0.03), BLACK, euler=(0, 0, 90))
                      + _box((sx, sy, sz), (0, -hs, 0.03), BLACK, euler=(0, 0, 90)))
        torso_vis = _box((0.075, 0.14, 0.13), (0, 0, 0.11)) + _box((0.004, 0.10, 0.07), (0.039, 0, 0.12), GREY)
        head_vis = _box(hsz, (0, 0, hsz[2] / 2 + 0.005), ORANGE)
    motors = [f'<motor name="{s}_{j}" joint="{s}_{j}" ctrlrange="-5 5"/>' for s in "lr" for j in LEG_JOINTS]
    motors += [f'<motor name="{s}_{j}" joint="{s}_{j}" ctrlrange="-5 5"/>' for s in "lr" for j in ARM_JOINTS]
    motors.append('<motor name="neck_yaw" joint="neck_yaw" ctrlrange="-5 5"/>')
    return f"""<mujoco model="jx0">
  <compiler angle="radian" autolimits="true"/>
  <option timestep="{timestep}" gravity="0 0 -9.81" integrator="implicitfast"/>
  <visual><global offwidth="1920" offheight="1080"/><quality shadowsize="4096"/><headlight ambient=".35 .35 .38" diffuse=".4 .4 .4"/></visual>
  <asset>
    <texture name="grid" type="2d" builtin="checker" rgb1=".2 .22 .26" rgb2=".26 .28 .32" width="512" height="512"/>
    <material name="grid" texture="grid" texrepeat="8 8" reflectance=".15"/>
    {asset_xml or ""}
  </asset>
  <worldbody>
    <geom name="floor" type="plane" size="6 6 0.1" material="grid" friction="0.9 0.02 0.001"/>
    <light pos="0.5 -0.5 2" dir="-0.2 0.2 -1" diffuse=".7 .7 .7" castshadow="true"/>
    <body name="pelvis" pos="0 0 {d.leg_length + 0.002:.5f}">
      <freejoint name="root"/>
      {_inertial(d.links["pelvis"])}
      {pelvis_vis}
      <site name="imu" pos="0 0 0.03" size="0.005"/>
      <body name="torso" pos="0 0 0">
        <inertial pos="{_f(ubl.com)}" mass="{torso_m:.4f}" diaginertia="{_f(np.maximum(ubl.inertia * torso_m / ubl.mass, 1e-6))}"/>
        {torso_vis}
        {arm("l")}
        {arm("r")}
        <body name="head" pos="{_f(neck)}">
          <inertial pos="0 0 {hsz[2] / 2}" mass="{HEAD_MASS}" diaginertia="4e-5 4e-5 4e-5"/>
          <joint name="neck_yaw" axis="0 0 1" range="{nr[0]:.4f} {nr[1]:.4f}" damping="0.01" armature="0.0005"/>
          {head_vis}
          <geom type="cylinder" size="0.0162 0.001" pos="{hsz[0] / 2 - 0.0015:.4f} 0 0.038" euler="0 90 0" rgba=".03 .03 .05 1" contype="0" conaffinity="0"/>
          <geom type="sphere" size="0.005" pos="{hsz[0] / 2 - 0.001:.4f} 0.007 0.041" rgba=".3 .85 1 1" contype="0" conaffinity="0"/>
          <geom type="sphere" size="0.005" pos="{hsz[0] / 2 - 0.001:.4f} -0.007 0.041" rgba=".3 .85 1 1" contype="0" conaffinity="0"/>
        </body>
      </body>
      {leg("l")}
      {leg("r")}
    </body>
  </worldbody>
  <actuator>
    {chr(10).join(motors)}
  </actuator>
  <sensor>
    <framequat name="imu_quat" objtype="site" objname="imu"/>
    <gyro name="imu_gyro" site="imu"/>
    <accelerometer name="imu_acc" site="imu"/>
  </sensor>
</mujoco>
"""


if __name__ == "__main__":
    import mujoco
    xml = build()
    out = ROOT / "jx0" / "sim" / "jx0.xml"
    out.write_text(xml, encoding="utf-8")
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    mujoco.mj_forward(m, d)
    print(f"wrote {out.relative_to(ROOT)}: {m.nbody} bodies, {m.njnt} joints, {m.nu} actuators, "
          f"mass {sum(m.body_mass):.3f} kg")
