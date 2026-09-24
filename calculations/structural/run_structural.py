"""JX1 structural analysis (open issue OI-4): voxel FEA of the load-bearing leg parts + hand calculations.

Load cases (all loads actuator-limited — the hip's three intersecting joints and the knee cannot transmit moments
beyond their actuators' peak torque, so the structure is sized to what the actuators can do, not to a guessed impact):
  LC1 strength  every actuator at its peak torque simultaneously during a 3 x body-weight landing (+0.2 x 3BW shear),
                all sign combinations enveloped; required SF >= 1.5 on min yield (6061-T6) / >= 2.0 on conditioned
                strength (printed PA-CF)
  LC2 fatigue   fast-walk (0.79 m/s) dynamic peak joint torques + 1.5 BW vertical + 0.2 BW shear, treated as fully
                reversed amplitudes (conservative), 1e7 cycles; required SF >= 1.5 on the fatigue allowable
Printed parts are evaluated for every candidate print orientation (build axis) with a transversely isotropic
material and an in-layer / interlayer failure index; the best orientation is the design output.

Outputs: calculations/results/structural/{summary.json, report.md, <part>_<orientation>.png}
Usage: .venv/Scripts/python calculations/structural/run_structural.py [--parts thigh shin ...] [--h-scale 1.0]
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import trimesh
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools"))
from voxel_fea import VoxelModel, iso_D, transverse_iso_D  # noqa: E402
from cad.params import ACT, PKG, THIGH, SHIN, HIP_Y, SOLE_TO_ANKLE, FOOT_L, FOOT_HEEL, FOOT_W, CRANK_R, FOOT_LEVER  # noqa: E402

def _num(x):
    """YAML 1.1 reads '68.9e9' as a string — coerce numeric-looking strings recursively."""
    if isinstance(x, dict):
        return {k: _num(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_num(v) for v in x]
    if isinstance(x, str):
        try:
            return float(x)
        except ValueError:
            return x
    return x


MAT = _num(yaml.safe_load((HERE / "materials.yaml").read_text(encoding="utf-8")))
RES = ROOT / "calculations" / "results" / "iter1_B_knee_and_pitch_RS04"
REQ = yaml.safe_load((RES / "requirements.yaml").read_text(encoding="utf-8"))["leg_joint_requirements"]
MESH = ROOT / "simulation" / "meshes" / "source_mm"
OUT = ROOT / "calculations" / "results" / "structural"

MASS = json.loads((RES / "summary.json").read_text()).get("total_mass_kg", 27.466) if (RES / "summary.json").exists() else 27.466
BW = MASS * 9.81
PEAK = {c: {"XL": 120.0, "L": 60.0, "M": 36.0, "S": 17.0, "XS": 14.0}[c] for c in ("XL", "L", "M", "S", "XS")}
T_PEAK = {"hip_yaw": PEAK["M"], "hip_roll": PEAK["L"], "hip_pitch": PEAK[PKG["pitch_class"]], "knee": PEAK[PKG["knee_class"]],
          "ankle_motor": PEAK[PKG["ankle_class"]]}
T_WALK = {j: REQ[j]["dynamic_peak_torque_Nm"] for j in ("hip_yaw", "hip_roll", "hip_pitch", "knee", "ankle_motor")}

# wrench magnitudes (Fx, Fy, Fz, Mx, My, Mz) at the hip centre / knee centre
HIP_LC1 = [0.2 * 3 * BW, 0.2 * 3 * BW, 3 * BW, T_PEAK["hip_roll"], T_PEAK["hip_pitch"], T_PEAK["hip_yaw"]]
HIP_LC2 = [0.2 * BW, 0.2 * BW, 1.5 * BW, T_WALK["hip_roll"], T_WALK["hip_pitch"], T_WALK["hip_yaw"]]
KNEE_LC1 = [0.2 * 3 * BW, 0.2 * 3 * BW, 3 * BW, T_PEAK["hip_roll"], T_PEAK["knee"], T_PEAK["hip_yaw"]]
KNEE_LC2 = [0.2 * BW, 0.2 * BW, 1.5 * BW, T_WALK["hip_roll"], T_WALK["knee"], T_WALK["hip_yaw"]]
F_ROD_LC1 = T_PEAK["ankle_motor"] / CRANK_R
F_ROD_LC2 = T_WALK["ankle_motor"] / CRANK_R

PC, KC, M_, L_, AK = ACT[PKG["pitch_class"]], ACT[PKG["knee_class"]], ACT["M"], ACT["L"], ACT[PKG["ankle_class"]]
T = PKG["plate_t"]


# ---------------------------------------------------------------------------------------------------- materials
def al():
    m = MAT["al6061_t6"]
    return {"kind": "iso", "D": iso_D(m["E_Pa"], m["nu"]), "static": m["yield_min_Pa"], "fatigue": m["fatigue_limit_Pa"], "uts": m["uts_min_Pa"],
            "sf_static": MAT["design_factors"]["metal_static_on_min_yield"], "sf_fatigue": MAT["design_factors"]["fatigue_on_endurance"]}


def al7075():
    m = MAT["al7075_t6"]
    return {"kind": "iso", "D": iso_D(m["E_Pa"], m["nu"]), "static": m["yield_min_Pa"], "fatigue": m["fatigue_limit_Pa"], "uts": m["uts_min_Pa"],
            "sf_static": MAT["design_factors"]["metal_static_on_min_yield"], "sf_fatigue": MAT["design_factors"]["fatigue_on_endurance"]}


def pacf(axis):
    m = MAT["esun_epa_cf"]
    k = m["knockdown_moisture"] * m["knockdown_process"]
    return {"kind": "print", "axis": axis,
            "D": transverse_iso_D(m["flex_modulus_xy_Pa"], m["flex_modulus_z_Pa"], m["nu_p"], m["nu_p"], m["G_pz_Pa"], axis=axis),
            "S": np.array([m["tensile_xy_Pa"], m["tensile_z_Pa"], m["interlayer_shear_Pa"]]) * k,
            "fatigue_fraction": m["fatigue_fraction"],
            "sf_static": MAT["design_factors"]["printed_static_on_conditioned_strength"], "sf_fatigue": MAT["design_factors"]["fatigue_on_endurance"]}


VO = {(0, 1): 3, (1, 0): 3, (1, 2): 4, (2, 1): 4, (0, 2): 5, (2, 0): 5}


def failure_index(sig, mat, fatigue=False):
    """sig (..., 6) -> failure index (applied / allowable) at every point."""
    if mat["kind"] == "iso":
        sx, sy, sz, txy, tyz, tzx = np.moveaxis(sig, -1, 0)
        vm = np.sqrt(0.5 * ((sx - sy) ** 2 + (sy - sz) ** 2 + (sz - sx) ** 2) + 3 * (txy ** 2 + tyz ** 2 + tzx ** 2))
        return vm / (mat["fatigue"] if fatigue else mat["static"])
    b = mat["axis"]
    a1, a2 = [a for a in range(3) if a != b]
    S = mat["S"] * (mat["fatigue_fraction"] if fatigue else 1.0)
    s11, s22, t12 = sig[..., a1], sig[..., a2], sig[..., VO[(a1, a2)]]
    vm_p = np.sqrt(s11 ** 2 - s11 * s22 + s22 ** 2 + 3 * t12 ** 2)
    sn, t1, t2 = sig[..., b], sig[..., VO[(b, a1)]], sig[..., VO[(b, a2)]]
    fi_inter = np.sqrt((np.maximum(sn, 0) / S[1]) ** 2 + (t1 ** 2 + t2 ** 2) / S[2] ** 2)
    return np.maximum(vm_p / S[0], fi_inter)


def fatigue_index(sig_a, sig_m, mat):
    """Goodman-type fatigue index from amplitude and mean stress tensors (..., 6)."""
    if mat["kind"] == "iso":
        def vm(s):
            sx, sy, sz, txy, tyz, tzx = np.moveaxis(s, -1, 0)
            return np.sqrt(0.5 * ((sx - sy) ** 2 + (sy - sz) ** 2 + (sz - sx) ** 2) + 3 * (txy ** 2 + tyz ** 2 + tzx ** 2))
        return vm(sig_a) / mat["fatigue"] + vm(sig_m) / mat["uts"]
    b = mat["axis"]
    a1, a2 = [a for a in range(3) if a != b]
    S, f = mat["S"], mat["fatigue_fraction"]

    def vmp(s):
        return np.sqrt(s[..., a1] ** 2 - s[..., a1] * s[..., a2] + s[..., a2] ** 2 + 3 * s[..., VO[(a1, a2)]] ** 2)
    inplane = vmp(sig_a) / (f * S[0]) + vmp(sig_m) / S[0]
    ta = np.sqrt(sig_a[..., VO[(b, a1)]] ** 2 + sig_a[..., VO[(b, a2)]] ** 2)
    inter = np.sqrt((np.abs(sig_a[..., b]) / (f * S[1])) ** 2 + (ta / (f * S[2])) ** 2) + np.maximum(sig_m[..., b], 0) / S[1]
    return np.maximum(inplane, inter)


_LOADS = {}


def loads():
    """Physically consistent load samples (calculations/structural/leg_loads.py), cached in results/structural/loads.npz."""
    if _LOADS:
        return _LOADS
    cache = OUT / "loads.npz"
    if cache.exists():
        z = np.load(cache, allow_pickle=True)
        _LOADS.update(z["loads"].item())
        return _LOADS
    import leg_loads
    lc1, lc2, summ = leg_loads.build(MASS)
    _LOADS.update({"LC1": lc1, "LC2": lc2, "summary": summ})
    OUT.mkdir(parents=True, exist_ok=True)
    np.savez(cache, loads=np.array(dict(_LOADS), dtype=object))
    return _LOADS


def evaluate_samples(model, part_key, groups, mat, chunk=12):
    """LC1: max failure index over all actuator-capped GRF samples; LC2: Goodman fatigue index over walking series.
    groups: [(group_key, selector, point)] matching leg_loads keys (part_key, group_key)."""
    L = loads()
    F = []
    for gkey, sel, point in groups:
        nodes = sel(model)
        if len(nodes) < 4:
            raise RuntimeError(f"{part_key}: load group '{gkey}' selected {len(nodes)} nodes")
        F.append(model.wrench_loads(nodes, np.asarray(point, float)))
    U = model.solve(np.concatenate(F))
    sig = model.corner_stress(U).astype(np.float32)                     # (6*ng, nel, 8, 6)
    C1 = np.concatenate([L["LC1"][(part_key, g[0])] for g in groups], axis=1).astype(np.float32)
    fi1 = np.zeros(sig.shape[1])
    for a in range(0, len(C1), chunk):
        st = np.tensordot(C1[a:a + chunk], sig, axes=(1, 0))            # (k, nel, 8, 6)
        fi1 = np.maximum(fi1, failure_index(st, mat).max(axis=(0, 2)))
    fi2 = np.zeros(sig.shape[1])
    nser = len(L["LC2"][(part_key, groups[0][0])])
    for si in range(nser):
        C2 = np.concatenate([L["LC2"][(part_key, g[0])][si] for g in groups], axis=1).astype(np.float32)
        mx = np.full(sig.shape[1:], -np.inf, np.float32)
        mn = np.full(sig.shape[1:], np.inf, np.float32)
        for a in range(0, len(C2), chunk):
            st = np.tensordot(C2[a:a + chunk], sig, axes=(1, 0))
            mx = np.maximum(mx, st.max(0))
            mn = np.minimum(mn, st.min(0))
        fi2 = np.maximum(fi2, fatigue_index((mx - mn) / 2, (mx + mn) / 2, mat).max(axis=1))
    return fi1, fi2, U


# ---------------------------------------------------------------------------------------------------- part definitions
# Each part: STL stem, voxel pitch, material factory + candidate print axes, supports, load groups.
# A load group = (name, node-selector, wrench point, LC1 magnitudes[6], LC2 magnitudes[6]); all groups of a part act
# simultaneously and every sign combination of the non-zero components is enveloped.
def thigh_def():
    y0, Lt = PKG["pitch_out_y"], THIGH
    return {
        "stl": "JX1_Thigh_L", "h": 0.002, "materials": {"6061-T6": al()},
        "supports": [("hip pitch output flange", lambda m: m.face_annulus(1, y0, (0, y0, 0), PC["PILOT_D"] / 2 + 0.0004, PC["D_OUT"] / 2), (0, 1, 2))],
        "sample_groups": [("knee", lambda m: m.face_annulus(1, y0, (0, y0, -Lt), 0.0135, KC["PCD_REAR"] / 2 + 0.006), (0, 0, -Lt))],
        "note": "thigh plate + medial flanges; knee housing and hip-pitch output bolt to the same plane (y = pitch_out_y)",
    }


def hip_roll_def():
    xf = PKG["roll_out_x"]
    y_med = PKG["pitch_out_y"] - PC["T_OUT"] - PC["L_HOUSING"]
    return {
        "stl": "JX1_HipRollBracket_L", "h": 0.002, "materials": {f"PA-CF build {'xyz'[a]}": pacf(a) for a in (0, 1, 2)},
        "supports": [("hip roll output flange", lambda m: m.face_annulus(0, xf, (xf, 0, 0), L_["PILOT_D"] / 2 + 0.0004, L_["D_OUT"] / 2), (0, 1, 2))],
        "sample_groups": [("leg", lambda m: m.face_annulus(1, y_med, (0, y_med, 0), 0.0135, PC["PCD_REAR"] / 2 + 0.006), (0, 0, 0))],
        "note": "L-bracket: roll output (back plate, normal x) -> pitch housing (medial plate, normal y)",
    }


def hip_yaw_def():
    zt = PKG["yaw_out_z"]
    x_back = PKG["roll_out_x"] - L_["T_OUT"] - L_["L_HOUSING"]
    return {
        "stl": "JX1_HipYawBracket_L", "h": 0.002, "materials": {f"PA-CF build {'xyz'[a]}": pacf(a) for a in (0, 2)},
        "supports": [("hip yaw output flange", lambda m: m.face_annulus(2, zt, (0, 0, zt), M_["PILOT_D"] / 2 + 0.0004, M_["D_OUT"] / 2), (0, 1, 2))],
        "sample_groups": [("leg", lambda m: m.face_annulus(0, x_back, (x_back, 0, 0), 0.0135, L_["PCD_REAR"] / 2 + 0.006), (0, 0, 0))],
        "note": "L-bracket: yaw output (top plate, normal z) -> roll housing (back plate, normal x)",
    }


def shin_def():
    y_out = PKG["knee_rear_y"] - KC["L_HOUSING"] - KC["T_OUT"]
    web = PKG["shin_web_t"]
    zA, zB, Ls, wc = PKG["ankle_A_z"], PKG["ankle_B_z"], SHIN, PKG["rod_crank_w"]
    return {
        "stl": "JX1_Shin_L", "h": 0.002, "offset": (0.0, 0.001, 0.0), "materials": {f"PA-CF build {'xyz'[a]}": pacf(a) for a in (0, 1)},
        "supports": [("knee output flange", lambda m: m.face_annulus(1, y_out, (0, y_out, 0), KC["PILOT_D"] / 2 + 0.0004, KC["D_OUT"] / 2), (0, 1, 2))],
        "sample_groups": [
            ("fork", lambda m: m.bore(1, (0, 0, -Ls), 0.004, (-0.03, 0.03)), (0, 0, -Ls)),
            ("rodA", lambda m: m.face_annulus(1, web / 2, (0, web / 2, zA), 0.0115, AK["PCD_REAR"] / 2 + 0.005), (-CRANK_R, wc, zA)),
            ("rodB", lambda m: m.face_annulus(1, -web / 2, (0, -web / 2, zB), 0.0115, AK["PCD_REAR"] / 2 + 0.005), (-CRANK_R, -wc, zB)),
        ],
        "note": "knee output plate -> joggle -> central web (both ankle motors) -> ankle fork; fork pin load includes both rod reactions",
    }


def foot_def():
    zs = -SOLE_TO_ANKLE
    toe, heel, hw = FOOT_L - FOOT_HEEL, -FOOT_HEEL, FOOT_W / 2
    wf = PKG["rod_foot_w"]

    def patch(x0, x1, y0, y1):
        return lambda m: m.select(lambda X: (np.abs(X[:, 2] - zs) <= 0.75 * m.h) & (X[:, 0] >= x0) & (X[:, 0] <= x1) & (X[:, 1] >= y0) & (X[:, 1] <= y1))
    # patch loads are capped by what the parallel ankle can hold before back-driving (pitch 58 / roll 65 N m peak capability,
    # walking: REQ ankle pitch 40.5 / roll 12.6 N m) — a larger toe/edge force simply rotates the foot
    xt, xh, ye = toe - 0.0195, heel + 0.0195, hw - 0.012

    def grf(cap1, cap2):
        f1, f2 = min(3 * BW, cap1), min(1.5 * BW, cap2)
        return [0.2 * f1, 0.2 * f1, f1, 0, 0, 0], [0.2 * f2, 0.2 * f2, f2, 0, 0, 0]
    toe_l, heel_l, edge_l = grf(58 / xt, 40.5 / xt), grf(58 / -xh, 40.5 / -xh), grf(65 / ye, 12.6 / ye)
    return {
        "stl": "JX1_Foot_L", "h": 0.002, "materials": {"PA-CF build z": pacf(2)},
        "supports": [("roll pin (cross)", lambda m: m.bore(0, (0, 0, 0), 0.004, (-0.03, 0.03)), (0, 1, 2)),
                     ("rod-end posts (axial)", lambda m: m.select(lambda X: (np.abs(X[:, 2] + 0.004) <= 0.75 * m.h) & (np.abs(X[:, 0] + FOOT_LEVER) <= 0.007)
                                                               & (np.abs(np.abs(X[:, 1]) - wf) <= 0.007)), (2,))],
        "scenarios": {
            "toe": [("toe patch GRF (ankle-torque capped)", patch(toe - 0.035, toe - 0.004, -hw + 0.012, hw - 0.012), None, *toe_l)],
            "heel": [("heel patch GRF (ankle-torque capped)", patch(heel + 0.004, heel + 0.035, -hw + 0.012, hw - 0.012), None, *heel_l)],
            "lateral edge": [("lateral edge GRF (ankle-torque capped)", patch(-0.030, 0.080, hw - 0.022, hw - 0.002), None, *edge_l)],
        },
        "note": "sole plate + roll clevis + rod posts; three non-simultaneous GRF patch scenarios",
    }


def pelvis_def():
    Mh = M_
    z0 = PKG["yaw_out_z"] + Mh["T_OUT"] + Mh["L_HOUSING"]
    z1 = z0 + T
    return {
        "stl": "JX1_Pelvis", "h": 0.002, "materials": {"PA-CF build z": pacf(2)},
        "supports": [("waist actuator (torso)", lambda m: m.face_annulus(2, z1, (0, 0, z1), 0.0155, Mh["PCD_REAR"] / 2 + 0.006), (0, 1, 2))],
        "sample_groups": [("leg", lambda m: m.face_annulus(2, z0, (0, HIP_Y, z0), 0.0125, Mh["PCD_REAR"] / 2 + 0.006), (0, HIP_Y, 0))],
        "note": "torsion box; single-support leg wrench reacted by the torso through the waist interface",
    }


def crank_def():
    f1 = [0.7 * F_ROD_LC1, F_ROD_LC1, 0.12 * F_ROD_LC1, 0, 0, 0]
    f2 = [0.7 * F_ROD_LC2, F_ROD_LC2, 0.12 * F_ROD_LC2, 0, 0, 0]
    return {
        "stl": "JX1_AnkleCrank", "h": 0.001, "materials": {"6061-T6": al()},
        "supports": [("ankle motor output flange", lambda m: m.face_annulus(2, 0.0, (0, 0, 0), AK["PILOT_D"] / 2 + 0.0004, AK["D_OUT"] / 2), (0, 1, 2))],
        "loads": [("rod-end stud (rod force; radial component up to 0.7 F at +-45 deg crank)", lambda m: m.bore(2, (-CRANK_R, 0, 0), 0.0025, (-0.001, 0.007)),
                   (-CRANK_R, 0, 0.003), f1, f2)],
        "note": "6 mm 6061 crank; rod force from ankle-motor peak torque / crank radius",
    }


PARTS = {"thigh": thigh_def, "hip_roll": hip_roll_def, "hip_yaw": hip_yaw_def, "shin": shin_def, "foot": foot_def,
         "pelvis": pelvis_def, "crank": crank_def}


# ---------------------------------------------------------------------------------------------------- analysis
def envelope(sig_unit, scales, mat, fatigue):
    """Max failure index over sign permutations of the active unit cases. sig_unit (ncase, nel, 8, 6)."""
    act = [k for k, s in enumerate(scales) if s]
    best = np.zeros(sig_unit.shape[1])
    for sg in itertools.product((1.0, -1.0), repeat=len(act)):
        s = np.zeros(sig_unit.shape[1:])
        for k, g in zip(act, sg):
            s += g * scales[k] * sig_unit[k]
        best = np.maximum(best, failure_index(s, mat, fatigue).max(axis=1))
    return best


def run_scenario(model, groups, mat):
    F, sc1, sc2, meta = [], [], [], []
    for name, sel, point, lc1, lc2 in groups:
        nodes = sel(model)
        if len(nodes) < 4:
            raise RuntimeError(f"load group '{name}' selected {len(nodes)} nodes")
        pt = model.nodes[nodes].mean(0) if point is None else np.asarray(point, float)
        unit = model.wrench_loads(nodes, pt)
        for k in range(6):
            if lc1[k] or lc2[k]:
                F.append(unit[k])
                sc1.append(lc1[k])
                sc2.append(lc2[k])
        meta.append({"name": name, "nodes": int(len(nodes)), "point_m": np.round(pt, 4).tolist(),
                     "LC1": [round(v, 1) for v in lc1], "LC2": [round(v, 1) for v in lc2]})
    U = model.solve(np.array(F))
    sig = model.corner_stress(U)
    fi1 = envelope(sig, sc1, mat, fatigue=False)
    fi2 = envelope(sig, sc2, mat, fatigue=True)
    return fi1, fi2, U, sc1, sc2, meta


def summarise(model, fi, excl_nodes):
    """Robust statistics of a failure-index field away from load/support introduction (2.5 voxels)."""
    cen = model.element_centres()
    ex = model.nodes[np.array(sorted(excl_nodes))]
    tree = trimesh.proximity.cKDTree(ex) if hasattr(trimesh.proximity, "cKDTree") else None
    if tree is None:
        from scipy.spatial import cKDTree
        tree = cKDTree(ex)
    d, _ = tree.query(cen)
    far = d > 2.5 * model.h
    v = fi[far]
    i_max = int(np.argmax(np.where(far, fi, -1)))
    return {"p99_9": float(np.percentile(v, 99.9)), "p99": float(np.percentile(v, 99.0)), "max": float(v.max()),
            "max_at_mm": np.round(cen[i_max] * 1000, 1).tolist(), "elements_evaluated": int(far.sum())}, far


def image(model, fi, far, title, path, sf_req):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    grid = np.full(model.occ.shape, np.nan)
    e = model.elements
    grid[e[:, 0], e[:, 1], e[:, 2]] = np.where(far, fi, np.nan)
    fig, axs = plt.subplots(1, 3, figsize=(15, 5.2))
    lo = model.origin * 1000
    hh = model.h * 1000
    views = [(1, 0, 2, "side view (x-z, max over y)"), (0, 1, 2, "front view (y-z, max over x)"), (2, 0, 1, "top view (x-y, max over z)")]
    vmax = 1.0 / sf_req
    for ax, (red, ia, ib, lab) in zip(axs, views):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            img = np.nanmax(grid, axis=red)
        ext = [lo[ia], lo[ia] + img.shape[0] * hh, lo[ib], lo[ib] + img.shape[1] * hh]
        im = ax.imshow(img.T, origin="lower", extent=ext, cmap="turbo", vmin=0, vmax=vmax * 1.2, interpolation="nearest")
        ax.set_title(lab, fontsize=9)
        ax.set_xlabel("xyz"[ia] + " [mm]")
        ax.set_ylabel("xyz"[ib] + " [mm]")
        ax.set_aspect("equal")
    fig.colorbar(im, ax=axs, shrink=0.8, label=f"LC1 failure index (1/SF); limit {vmax:.2f} (SF {sf_req})")
    fig.suptitle(title, fontsize=11)
    fig.savefig(path, dpi=100, bbox_inches="tight")
    plt.close(fig)


def evaluate_part(model, d, key, mat):
    """Failure-index fields (LC1 strength, LC2 fatigue) + excluded nodes + interface compliance for one model."""
    excl = set()
    for _, sel, _ in d["supports"]:
        excl |= set(sel(model).tolist())
    if "sample_groups" in d:
        fi1, fi2, _ = evaluate_samples(model, key, d["sample_groups"], mat)
        groups = [(g[0], g[1], g[2]) for g in d["sample_groups"]]
    else:
        fi1 = fi2 = None
        groups = []
        for groups_ in d.get("scenarios", {"all loads": d.get("loads")}).values():
            a1, a2, *_ = run_scenario(model, groups_, mat)
            fi1 = a1 if fi1 is None else np.maximum(fi1, a1)
            fi2 = a2 if fi2 is None else np.maximum(fi2, a2)
            groups += [(g[0], g[1], g[2]) for g in groups_]
    for _, sel, _ in groups:
        excl |= set(sel(model).tolist())
    name0, sel0, pt0 = groups[0]
    n0 = sel0(model)
    pt = model.nodes[n0].mean(0) if pt0 is None else np.asarray(pt0, float)
    fit = model.rigid_fit(model.solve(model.wrench_loads(n0, pt)), n0, pt)
    comp = {"interface": name0, "translation_mm_per_kN": np.round(np.diag(fit)[:3] * 1e6, 4).tolist(),
            "rotation_deg_per_100Nm": np.round(np.degrees(np.diag(fit)[3:]) * 100, 4).tolist()}
    return fi1, fi2, excl, comp


def analyse_part(key, h_scale=1.0):
    d = PARTS[key]()
    mesh = trimesh.load(MESH / f"{d['stl']}.STL", force="mesh")
    mesh.apply_scale(0.001)
    h = d["h"] * h_scale
    out = {"part": key, "stl": d["stl"], "voxel_mm": round(h * 1000, 3), "note": d["note"], "materials": {},
           "mesh_volume_cm3": round(mesh.volume * 1e6, 2),
           "load_model": "actuator-capped GRF samples + walking time series (leg_loads.py)" if "sample_groups" in d else "capped envelope"}
    base = None
    for mname, mat in d["materials"].items():
        t0 = time.time()
        model = (VoxelModel.from_mesh(mesh, h, mat["D"], d.get("offset", (0, 0, 0))) if base is None
                 else VoxelModel(base.occ, base.origin, h, mat["D"]))
        base = base or model
        model.build()
        sup_meta = []
        for sname, sel, dofs in d["supports"]:
            nodes = sel(model)
            if len(nodes) < 4:
                raise RuntimeError(f"{key}: support '{sname}' selected {len(nodes)} nodes")
            model.fix(nodes, dofs)
            sup_meta.append({"name": sname, "nodes": int(len(nodes)), "dofs": list(dofs)})
        model.factorize()
        fi1, fi2, excl, comp = evaluate_part(model, d, key, mat)
        s1, far = summarise(model, fi1, excl)
        s2, _ = summarise(model, fi2, excl)
        res = {"elements": int(len(model.elements)), "dof": int(model.ndof), "supports": sup_meta,
               "voxel_volume_error_pct": round((model.occ.sum() * h ** 3 / mesh.volume - 1) * 100, 2),
               "LC1": {**s1, "SF": round(1 / s1["p99_9"], 2)}, "LC2_fatigue": {**s2, "SF": round(1 / s2["p99_9"], 2)},
               "interface_compliance": comp, "SF_LC1": round(1 / s1["p99_9"], 2), "SF_LC2": round(1 / s2["p99_9"], 2),
               "required": {"LC1": mat["sf_static"], "LC2": mat["sf_fatigue"]}}
        res["pass"] = bool(res["SF_LC1"] >= mat["sf_static"] and res["SF_LC2"] >= mat["sf_fatigue"])
        res["solve_s"] = round(time.time() - t0, 1)
        tag = mname.replace(" ", "_").replace("-", "")
        image(model, fi1, far, f"JX1 {d['stl']} — {mname} — LC1 (SF {res['SF_LC1']}, LC2 fatigue SF {res['SF_LC2']})",
              OUT / f"{key}_{tag}.png", mat["sf_static"])
        out["materials"][mname] = res
        print(f"{key:9s} {mname:14s} el {res['elements']:6d}  SF LC1 {res['SF_LC1']:6.2f} (req {mat['sf_static']})  "
              f"SF LC2 {res['SF_LC2']:6.2f} (req {mat['sf_fatigue']})  {'PASS' if res['pass'] else 'FAIL'}  {res['solve_s']} s", flush=True)
    best = max(out["materials"].items(), key=lambda kv: min(kv[1]["SF_LC1"] / kv[1]["required"]["LC1"], kv[1]["SF_LC2"] / kv[1]["required"]["LC2"]))
    out["recommended"] = best[0]
    return out


# ---------------------------------------------------------------------------------------------------- hand calculations
def hand_calcs():
    hc = {}
    E304, Y304 = MAT["stainless_304_rod"]["E_Pa"], MAT["stainless_304_rod"]["yield_Pa"]
    hA, hB = SHIN + PKG["ankle_A_z"], SHIN + PKG["ankle_B_z"]
    dw, dr = PKG["rod_crank_w"] - PKG["rod_foot_w"], CRANK_R - FOOT_LEVER
    rods = {"A": math.sqrt(hA ** 2 + dw ** 2 + dr ** 2), "B": math.sqrt(hB ** 2 + dw ** 2 + dr ** 2)}
    options = {"M5 threaded rod (d3 = 4.019 mm)": math.pi * 0.004019 ** 4 / 64, "M6 threaded rod (d3 = 4.773 mm)": math.pi * 0.004773 ** 4 / 64,
               "Ø8 solid 304 rod, M5 tapped ends": math.pi * 0.008 ** 4 / 64}
    buck = {}
    for opt, I in options.items():
        buck[opt] = {r: {"length_mm": round(L * 1000, 1), "P_cr_N": round(math.pi ** 2 * E304 * I / L ** 2, 0),
                         "SF_LC1": round(math.pi ** 2 * E304 * I / L ** 2 / F_ROD_LC1, 2)} for r, L in rods.items()}
    hc["ankle_rod_buckling"] = {"rod_force_LC1_N": round(F_ROD_LC1, 0), "rod_force_LC2_N": round(F_ROD_LC2, 0), "pinned_pinned_K": 1.0,
                                "options": buck, "required_SF": MAT["design_factors"]["buckling"],
                                "decision": "Ø8 solid 304 rod with M5 tapped ends (M5 threaded rod buckles below the RS06 peak rod force)"}
    phs5 = MAT["rod_end_phs5"]
    hc["rod_end_PHS5"] = {"static_SF_LC1": round(phs5["static_load_N"] / F_ROD_LC1, 2), "dynamic_rating_over_LC2": round(phs5["dynamic_load_N"] / F_ROD_LC2, 1)}
    # ankle pins: double shear + bearing on the printed tines
    Fpin1 = math.hypot(3 * BW + 2 * F_ROD_LC1, 0.2 * 3 * BW * math.sqrt(2))
    A = math.pi * 0.004 ** 2
    hc["ankle_pins"] = {"pin_force_LC1_N": round(Fpin1, 0), "double_shear_MPa": round(Fpin1 / (2 * A) / 1e6, 1),
                        "SF_shear_on_0.577Y": round(0.577 * MAT["steel_pin_c45_hard_chrome"]["yield_Pa"] / (Fpin1 / (2 * A)), 1),
                        "tine_bearing_SF_on_conditioned_xy": round(MAT["esun_epa_cf"]["tensile_xy_Pa"] * 0.65 * 0.85 / (Fpin1 / 2 / (0.012 * 0.009)), 2),
                        "pin_bearing": "HK0810 drawn-cup needle bearings (8x12x10, BOM) pressed into the printed tines: bore pressure on the 12 mm OD",
                        "tine_bore_pressure_MPa": round(Fpin1 / 2 / (0.012 * 0.009) / 1e6, 1),
                        "decision": "keep HK0810 needle bearings (static rating >> 1.1 kN per bearing); ream printed bores for a 0.02-0.04 mm press fit"}
    # bolted actuator joints: circular pattern under tilting moment M + axial force Fz + torque T
    def bolt_group(n, pcd, d_nom, As, proof, M, Fz, Tq, mu=0.15):
        r = pcd / 2
        Fb = 2 * M / (n * r) + Fz / n                      # max bolt tension (rigid flange, pivot at centre)
        preload = 0.7 * proof * As
        slip = mu * preload * n * r                        # friction torque capacity
        return {"bolts": f"{n} x {d_nom} on PCD {pcd * 1000:.0f} mm", "max_bolt_tension_N": round(Fb, 0),
                "preload_70pct_proof_N": round(preload, 0), "separation_SF": round(preload / Fb, 2), "slip_torque_SF": round(slip / Tq, 2)}
    hc["bolted_joints_LC1"] = {
        "hip_yaw_RS06_output_M3_12.9": bolt_group(6, M_["PCD_OUT"], "M3 12.9", 5.03e-6, 970e6, math.hypot(HIP_LC1[3], HIP_LC1[4]), HIP_LC1[2], HIP_LC1[5]),
        "hip_yaw_RS06_output_M3_8.8": bolt_group(6, M_["PCD_OUT"], "M3 8.8", 5.03e-6, 580e6, math.hypot(HIP_LC1[3], HIP_LC1[4]), HIP_LC1[2], HIP_LC1[5]),
        "hip_pitch_RS04_output_M5_12.9": bolt_group(8, PC["PCD_OUT"], "M5 12.9", 14.2e-6, 970e6, math.hypot(HIP_LC1[3], HIP_LC1[5]), HIP_LC1[1], HIP_LC1[4]),
        "knee_RS04_output_M5_12.9": bolt_group(8, KC["PCD_OUT"], "M5 12.9", 14.2e-6, 970e6, math.hypot(KNEE_LC1[3], KNEE_LC1[5]), KNEE_LC1[1], KNEE_LC1[4]),
        "ankle_RS06_output_M3_12.9": bolt_group(6, AK["PCD_OUT"], "M3 12.9", 5.03e-6, 970e6, F_ROD_LC1 * PKG["rod_crank_w"], F_ROD_LC1 * 0.12, T_PEAK["ankle_motor"]),
        "note": "bolt patterns are ASSUMED until RobStride drawings are dimensioned (OI-1); proof strengths ISO 898-1 (8.8: 580 MPa for M3-M5 is conservative "
                "vs 600-640; 12.9: 970 MPa)",
    }
    hc["actuator_output_bearing_moments"] = {
        "hip_yaw_RS06_tilting_moment_Nm": {"LC1": round(math.hypot(HIP_LC1[3], HIP_LC1[4]), 1), "LC2_walk": round(math.hypot(HIP_LC2[3], HIP_LC2[4]), 1)},
        "hip_roll_RS03_tilting_moment_Nm": {"LC1": round(math.hypot(HIP_LC1[4], HIP_LC1[5]), 1), "LC2_walk": round(math.hypot(HIP_LC2[4], HIP_LC2[5]), 1)},
        "status": "UNVERIFIED — RobStride manuals (rev. 260713) publish no output-bearing axial/radial/moment ratings; request from RobStride "
                  "or add an external yaw support bearing (risk R17)",
    }
    return hc


def report(results, hc):
    L = loads()
    summ = L.get("summary", {})
    lines = ["# JX1 structural analysis (OI-4) — voxel FEA + hand calculations", "",
             f"Body weight {BW:.0f} N (mass {MASS:.2f} kg). Actuator peaks: hip yaw {T_PEAK['hip_yaw']:.0f}, hip roll {T_PEAK['hip_roll']:.0f}, "
             f"hip pitch {T_PEAK['hip_pitch']:.0f}, knee {T_PEAK['knee']:.0f}, ankle motor {T_PEAK['ankle_motor']:.0f} N·m.", "",
             "**Load model (leg chain: hip brackets, pelvis, thigh, shin)** — `calculations/structural/leg_loads.py`:",
             f"* **LC1 strength**: {summ.get('samples', '?')} ground-reaction samples (8 poses × CoP grid over the sole × 5 GRF directions × 3 free "
             "yaw moments) at 3 BW, propagated through the leg kinematics; whenever a joint (or an ankle motor through the parallel "
             f"linkage) would exceed its actuator peak the GRF is scaled to the saturation point ({summ.get('scaled', '?')} samples scaled, "
             f"min scale {summ.get('min_scale', 0):.2f}). Required SF 1.5 on minimum yield (6061-T6) / 2.0 on conditioned strength (PA-CF).",
             "* **LC2 fatigue**: fast walk 0.79 m/s, nominal walk 0.52 m/s and 15°/step turning time series (inverse-dynamics joint "
             "torques → equivalent foot wrench), Goodman mean/amplitude per element, required SF 1.5.",
             "* Foot and ankle crank: capped envelope cases (foot patch loads limited by the ankle's torque capability; crank rod force "
             "from the RS06 peak).",
             "* SF = 1 / (99.9th-percentile failure index away from load/support introduction). Method validated against closed-form "
             "solutions (`test_voxel_fea.py`). Label: CALCULATED (linear, bonded interfaces, ASSUMED printed-material knockdowns).", "",
             "| Part | Material / print build axis | Elements | SF LC1 (req) | SF LC2 fatigue (req) | Result | Worst location [mm] |",
             "|---|---|---|---|---|---|---|"]
    for key, r in results.items():
        for mname, m in r["materials"].items():
            star = " **(recommended)**" if mname == r["recommended"] and len(r["materials"]) > 1 else ""
            lines.append(f"| {r['stl']} | {mname}{star} | {m['elements']} | {m['SF_LC1']} ({m['required']['LC1']}) | {m['SF_LC2']} ({m['required']['LC2']}) | "
                         f"{'PASS' if m['pass'] else '**FAIL**'} | {m['LC1']['max_at_mm']} |")
    lines += ["", "## Interface compliance (unit loads)", "", "| Part | Interface | translation [mm/kN] | rotation [deg per 100 N·m] |", "|---|---|---|---|"]
    for key, r in results.items():
        c = r["materials"][r["recommended"]]["interface_compliance"]
        lines.append(f"| {r['stl']} | {c['interface']} | {c['translation_mm_per_kN']} | {c['rotation_deg_per_100Nm']} |")
    lines += ["", "## Hand calculations", "", "```json", json.dumps(hc, indent=1, ensure_ascii=False), "```", ""]
    (OUT / "report.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", nargs="*", default=list(PARTS))
    ap.add_argument("--h-scale", type=float, default=1.0)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "summary.json"
    old = json.loads(path.read_text()) if path.exists() else {}
    results = old.get("parts", {})
    for key in a.parts:
        results[key] = analyse_part(key, a.h_scale)
    hc = hand_calcs()
    path.write_text(json.dumps({"loads": {"BW_N": BW, "HIP_LC1": HIP_LC1, "HIP_LC2": HIP_LC2, "KNEE_LC1": KNEE_LC1, "KNEE_LC2": KNEE_LC2,
                                          "F_ROD_LC1": F_ROD_LC1, "F_ROD_LC2": F_ROD_LC2}, "parts": results, "hand_calcs": hc}, indent=1))
    report({k: results[k] for k in PARTS if k in results}, hc)


if __name__ == "__main__":
    main()
