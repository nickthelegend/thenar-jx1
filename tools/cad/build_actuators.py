"""Build the JX1 Modular Actuator Interface envelope parts (housing = stator side, output = rotor side).

Each class (L, M) yields two native parametric parts driven by global variables:
  CAD/Actuators/JX1_ACT_<cls>_Housing.SLDPRT   origin at the output face centre, housing along -Z
  CAD/Actuators/JX1_ACT_<cls>_Output.SLDPRT    output disc z in [0, T_OUT] + pilot boss, mounting face at z = T_OUT
Reference geometry for mates: Front Plane = interface plane at z = 0, axis AX_Joint = Z, Top Plane = clocking reference.
These are interface envelopes (label: ASSUMED) until the DIY joint-module internals are designed.

Usage: .venv/Scripts/python tools/cad/build_actuators.py [L M]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from swlib.core import Session  # noqa: E402
from swlib.part import Part  # noqa: E402
from cad.params import ACT, ROOT  # noqa: E402

OUT = ROOT / "CAD" / "Actuators"
HOUSING_RGB = (0.18, 0.19, 0.21)
OUTPUT_RGB = (0.78, 0.79, 0.81)


def mm(x):
    return round(x * 1000, 4)


def housing(s, cls):
    a = ACT[cls]
    R, L = a["D"] / 2, a["L_HOUSING"]
    p = Part(s, f"JX1_ACT_{cls}_Housing", OUT / f"JX1_ACT_{cls}_Housing.SLDPRT")
    p.gv("D_act", mm(a["D"])); p.gv("L_housing", mm(L)); p.gv("PCD_rear", mm(a["PCD_REAR"]))
    p.gv("D_rear_hole", mm(a["HOLE_REAR"])); p.gv("D_bearing_boss", mm(a["D_OUT"] - 0.004))
    # Main body: revolve half-section in the XZ plane (Top Plane: u = x = radius, v = -z)
    ch = 0.003
    with p.sketch("XZ", "SK_Body") as sk:
        sk.centerline(0, -0.01, 0, L + 0.01)
        pts = [(0, 0), (R - ch, 0), (R, ch), (R, L - ch), (R - ch, L), (0, L)]
        sk.polygon(pts, names=[(None, None), ("R_front", None), (None, None), ("R_body", "L_body"), (None, None), (None, None)],
                   gvs=[(None, None), (f'"D_act"/2-{mm(ch)}', None), (None, None), ('"D_act"/2', '"L_housing"'), (None, None), (None, None)])
    p.revolve("SK_Body", "Housing_Body")
    # Rear face tapped-hole pattern (blind 8 mm, drawn as tap drill)
    p.ref_plane_offset("Front Plane", L, "PL_Rear", flip=True)
    with p.sketch("XY", "SK_RearHole", plane_name="PL_Rear") as sk:
        sk.circle(a["PCD_REAR"] / 2, 0, a["HOLE_REAR"] / 2, "D_rh", '"D_rear_hole"', pos_names=("R_rh", None), pos_gvs=('"PCD_rear"/2', None))
    p.cut("SK_RearHole", 0.008, "Rear_Tapped_Hole", reverse=False)
    p.ref_axis("Top Plane", "Right Plane", "AX_Joint")
    p.circular_pattern(["Rear_Tapped_Hole"], "AX_Joint", a["N_REAR"], "Rear_Hole_Pattern")
    # Connector zone (CAN in/out + power) on +Y side at the rear
    cw, ch_, cl = a["CONN"]
    with p.sketch("XY", "SK_Connector", plane_name="PL_Rear") as sk:
        sk.rect(-cw / 2, R - 0.004, cw / 2, R + ch_)
    p.extrude("SK_Connector", cl, "Connector_Zone", reverse=False)
    p.color(HOUSING_RGB)
    p.prop("JX1_Class", cls)
    p.prop("JX1_Role", "actuator housing (stator side) - MAI envelope")
    p.prop("Evidence", "ASSUMED envelope; DIY joint-module internals pending")
    return p.save(close=False)


def output(s, cls):
    a = ACT[cls]
    Ro, T = a["D_OUT"] / 2, a["T_OUT"]
    p = Part(s, f"JX1_ACT_{cls}_Output", OUT / f"JX1_ACT_{cls}_Output.SLDPRT")
    p.gv("D_out", mm(a["D_OUT"])); p.gv("T_out", mm(T)); p.gv("PCD_out", mm(a["PCD_OUT"]))
    p.gv("D_pilot", mm(a["PILOT_D"])); p.gv("H_pilot", mm(a["PILOT_H"])); p.gv("D_out_hole", mm(a["HOLE_OUT"]))
    with p.sketch("XY", "SK_Disc") as sk:
        sk.circle(0, 0, Ro, "D_disc", '"D_out"')
    p.extrude("SK_Disc", T, "Output_Disc", depth_gv='"T_out"')
    p.ref_plane_offset("Front Plane", T, "PL_Mount")
    with p.sketch("XY", "SK_Pilot", plane_name="PL_Mount") as sk:
        sk.circle(0, 0, a["PILOT_D"] / 2, "D_pil", '"D_pilot"')
    p.extrude("SK_Pilot", a["PILOT_H"], "Pilot_Boss", depth_gv='"H_pilot"')
    with p.sketch("XY", "SK_OutHole", plane_name="PL_Mount") as sk:
        sk.circle(a["PCD_OUT"] / 2, 0, a["HOLE_OUT"] / 2, "D_oh", '"D_out_hole"', pos_names=("R_oh", None), pos_gvs=('"PCD_out"/2', None))
    p.cut("SK_OutHole", T, "Output_Tapped_Hole", reverse=True)
    p.ref_axis("Top Plane", "Right Plane", "AX_Joint")
    p.circular_pattern(["Output_Tapped_Hole"], "AX_Joint", a["N_OUT"], "Output_Hole_Pattern")
    p.color(OUTPUT_RGB)
    p.prop("JX1_Class", cls)
    p.prop("JX1_Role", "actuator output flange (rotor side) - MAI envelope")
    return p.save(close=False)


def main():
    classes = sys.argv[1:] or ["L", "M"]
    s = Session()
    report = {}
    for cls in classes:
        for fn in (housing, output):
            info = fn(s, cls)
            report[Path(info["path"]).stem] = {k: info[k] for k in ("bodies", "errors", "sketch_status")} | {"mass": info["mass"]}
            print(Path(info["path"]).stem, "bodies", info["bodies"], "errors", info["errors"], "sketches", info["sketch_status"], flush=True)
    ev = ROOT / "verification" / "cad_build_actuators.json"
    ev.parent.mkdir(exist_ok=True)
    ev.write_text(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
