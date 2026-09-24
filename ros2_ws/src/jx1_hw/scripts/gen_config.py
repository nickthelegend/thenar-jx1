"""Generate ros2_ws/src/jx1_hw/config/hw.yaml from the generated firmware configs and the ankle design.

firmware/hub/jx1_hub/config_hub_a.h / config_hub_b.h (tools/gen_firmware_config.py) give each hub's joint order, CAN
bus/id, RobStride model, sign, zero, soft limits and torque limit - the order of the joint blocks in the USB frames.
calculations/design_point.yaml -> ankle_linkage gives the push-rod geometry for the ankle pitch/roll <-> crank mapping.
Usage: python ros2_ws/src/jx1_hw/scripts/gen_config.py
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

PKG = Path(__file__).resolve().parents[1]
REPO = PKG.parents[2]
ROW = re.compile(r'\{"(\w+)",\s*(\d+),\s*(\d+),\s*robstride::(\w+),\s*([-\d.]+)f,\s*([-\d.]+)f,\s*([-\d.]+)f,\s*([-\d.]+)f,\s*([-\d.]+)f\}')
CONST = re.compile(r"static const \w+ (\w+) = ([-\w.]+?)f?;")


def hub(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    joints = [{"name": m[0], "bus": int(m[1]), "can_id": int(m[2]), "model": m[3], "sign": float(m[4]), "zero": float(m[5]),
               "q_min": float(m[6]), "q_max": float(m[7]), "tau_limit": float(m[8])} for m in ROW.findall(text)]
    consts = {k: v for k, v in CONST.findall(text)}
    return {"joints": joints, "soft_margin_rad": float(consts["SOFT_MARGIN"]), "damping_kd": float(consts["DAMPING_KD"]),
            "host_timeout_us": int(consts["HOST_TIMEOUT_US"]), "bus_period_us": int(consts["BUS_PERIOD_US"]),
            "state_div": int(consts["STATE_DIV"])}


def main():
    fw = REPO / "firmware" / "hub" / "jx1_hub"
    dp = yaml.safe_load((REPO / "calculations" / "design_point.yaml").read_text(encoding="utf-8"))["ankle_linkage"]
    v = lambda k: float(dp[k]["value"])  # noqa: E731
    cfg = {"generated_by": "ros2_ws/src/jx1_hw/scripts/gen_config.py (firmware configs + calculations/design_point.yaml)",
           "hubs": {"a": hub(fw / "config_hub_a.h"), "b": hub(fw / "config_hub_b.h")},
           "ankle": {"crank_radius_m": v("crank_radius_m"), "foot_lever_m": v("foot_lever_m"), "rod_half_spacing_m": v("rod_half_spacing_m"),
                     "crank_half_spacing_m": v("crank_half_spacing_m"), "motor_A_height_m": v("motor_A_height_above_ankle_m"),
                     "motor_B_height_m": v("motor_B_height_above_ankle_m")}}
    out = PKG / "config" / "hw.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(cfg, sort_keys=False, width=140), encoding="utf-8")
    print("wrote", out, {k: len(h["joints"]) for k, h in cfg["hubs"].items()})


if __name__ == "__main__":
    main()
