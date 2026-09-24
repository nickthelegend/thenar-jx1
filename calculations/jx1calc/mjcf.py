"""Generate the parametric MuJoCo *analysis* model of the JX1 lower body + lumped upper body.

This model exists to size actuators before CAD. The CAD-derived simulation model lives in
simulation/ and is generated from SolidWorks mass properties later.
"""
from __future__ import annotations

import numpy as np

from .design import Design, LEG_JOINTS, LEG_LINKS

AXES = {"hip_yaw": "0 0 1", "hip_roll": "1 0 0", "hip_pitch": "0 1 0",
        "knee": "0 1 0", "ankle_pitch": "0 1 0", "ankle_roll": "1 0 0"}


def _f(x):
    return " ".join(f"{float(v):.6g}" for v in np.atleast_1d(x))


def joint_range_rad(design: Design, joint: str, side: str):
    lo, hi = design.ranges_deg[joint]
    if side == "r" and joint in ("hip_yaw", "hip_roll", "ankle_roll"):
        lo, hi = -hi, -lo
    return np.radians(lo), np.radians(hi)


def joint_armature(design: Design, joint: str) -> float:
    """Reflected actuator inertia in joint space. The parallel ankle maps both motors through the
    linkage Jacobian J ~ [[1, w/a], [1, -w/a]] (crank radius = foot lever): pitch sees 2*I, roll 2*I*(w/a)^2."""
    cls = design.act_classes
    if getattr(design, "ankle_type", "parallel") == "serial":     # one actuator per ankle axis
        if joint == "ankle_pitch":
            return cls[design.assign["ankle_A"]]["reflected_inertia_kgm2"]
        if joint == "ankle_roll":
            return cls[design.assign["ankle_B"]]["reflected_inertia_kgm2"]
    if joint == "ankle_pitch":
        return 2 * cls[design.assign["ankle_A"]]["reflected_inertia_kgm2"]
    if joint == "ankle_roll":
        return 2 * cls[design.assign["ankle_A"]]["reflected_inertia_kgm2"] * (design.rod_half_spacing / design.foot_lever) ** 2
    return cls[design.assign[joint]]["reflected_inertia_kgm2"]


def _inertial(link, mirror=False):
    com = np.array(link.com, float)
    if mirror:
        com = com * np.array([1, -1, 1])
    inertia = np.maximum(link.inertia, 1e-6)
    return f'<inertial pos="{_f(com)}" mass="{link.mass:.6g}" diaginertia="{_f(inertia)}"/>'


def build_mjcf(design: Design, timestep=0.001, with_actuators=True, kp=None, floor=True, damping=0.0) -> str:
    d = design
    hs = d.hip_spacing / 2
    body_offsets = {
        "hip_yaw_link": None,  # set per side
        "hip_roll_link": [0, 0, 0],
        "thigh": [0, 0, 0],
        "shin": [0, 0, -d.thigh],
        "ankle_cross": [0, 0, -d.shin],
        "foot": [0, 0, 0],
    }
    visual = {
        "hip_yaw_link": '<geom type="cylinder" size="0.035 0.03" pos="0 0 0.03" rgba=".3 .3 .35 1" contype="0" conaffinity="0"/>',
        "hip_roll_link": '<geom type="cylinder" size="0.045 0.03" euler="90 0 0" pos="0 {y} 0" rgba=".25 .25 .3 1" contype="0" conaffinity="0"/>',
        "thigh": f'<geom type="capsule" fromto="0 0 -0.03 0 0 {-d.thigh + 0.03}" size="0.035" rgba=".85 .85 .88 1" contype="0" conaffinity="0"/>',
        "shin": f'<geom type="capsule" fromto="0 0 -0.03 0 0 {-d.shin + 0.03}" size="0.03" rgba=".85 .85 .88 1" contype="0" conaffinity="0"/>',
        "ankle_cross": '<geom type="sphere" size="0.015" rgba=".2 .2 .2 1" contype="0" conaffinity="0"/>',
        "foot": (f'<geom name="{{side}}_foot_geom" type="box" size="{d.foot_length / 2} {d.foot_width / 2} {d.foot_thickness / 2}" '
                 f'pos="{d.foot_center_x} 0 {-d.sole_to_ankle + d.foot_thickness / 2}" rgba=".15 .15 .15 1" friction="1.0 0.02 0.001"/>'
                 f'<site name="{{side}}_sole" pos="0 0 {-d.sole_to_ankle}" size="0.01"/>'),
    }

    def leg(side):
        sgn = 1 if side == "l" else -1
        mirror = side == "r"
        xml = []
        closes = 0
        for jn, ln in zip(LEG_JOINTS, LEG_LINKS):
            pos = [0, sgn * hs, 0] if ln == "hip_yaw_link" else body_offsets[ln]
            lo, hi = joint_range_rad(d, jn, side)
            link = d.links[ln]
            vis = visual[ln].replace("{side}", side).replace("{y}", f"{sgn * 0.055}")
            xml.append(f'<body name="{side}_{ln}" pos="{_f(pos)}">')
            xml.append(_inertial(link, mirror))
            arm = joint_armature(d, jn)
            xml.append(f'<joint name="{side}_{jn}" axis="{AXES[jn]}" range="{lo:.6f} {hi:.6f}" limited="true" armature="{arm:.5g}" damping="{damping}"/>')
            xml.append(vis)
            closes += 1
        xml.append("</body>" * closes)
        return "\n".join(xml)

    pel = d.links["pelvis"]
    ub = d.links["upper_body"]
    act = ""
    if with_actuators:
        kp = kp or 300.0
        rows = []
        for side in ("l", "r"):
            for jn in LEG_JOINTS:
                rows.append(f'<position name="{side}_{jn}_act" joint="{side}_{jn}" kp="{kp}" kv="{kp / 30:.3g}" forcerange="-400 400"/>')
        act = "<actuator>" + "\n".join(rows) + "</actuator>"
    floor_xml = '<geom name="floor" type="plane" size="5 5 0.1" rgba=".8 .8 .8 1"/>' if floor else ""
    stand_z = d.leg_length
    return f"""<mujoco model="jx1_analysis">
  <compiler angle="radian" autolimits="true"/>
  <option timestep="{timestep}" gravity="0 0 -9.81" integrator="implicitfast"/>
  <worldbody>
    {floor_xml}
    <light pos="0 0 3" dir="0 0 -1"/>
    <body name="pelvis" pos="0 0 {stand_z:.5f}">
      <freejoint name="root"/>
      {_inertial(pel)}
      <geom type="box" size="0.06 0.13 0.05" pos="0 0 0.05" rgba=".9 .5 .1 1" contype="0" conaffinity="0"/>
      <site name="imu" pos="0 0 0.05" size="0.01"/>
      <body name="upper_body" pos="0 0 0">
        {_inertial(ub)}
        <geom type="box" size="0.09 0.14 0.2" pos="{_f(ub.com)}" rgba=".9 .9 .92 .6" contype="0" conaffinity="0"/>
      </body>
      {leg("l")}
      {leg("r")}
    </body>
  </worldbody>
  {act}
</mujoco>
"""
