"""Finite-element check of JX0's printed leg brackets (v0.4 double-sided joints) with the repository's voxel FEA
(calculations/structural/voxel_fea.py: 8-node hexahedra with incompatible bending modes, validated against closed-form
solutions by its own tests).

Each bracket is held where it bolts to the servo upstream (a U-bracket: the output horn's face and the rear hub's face;
the foot: its sole on the floor) and loaded where the servo downstream sits in its cage (the cage's rear plate, which
the case is screwed to; the foot: its U-bracket), with the downstream joint's actual 6-axis load from the simulation,
instant by instant (every 10 ms: robustness.trial(..., series=True)), so the stress at each instant is the true
combination of forces and moments, not peaks of different moments added up:
  fatigue: the 14 verified gaits on the nominal robot (what every step does), against PETG's ~15 MPa at 10^6 cycles;
  strength: 42 walks with random model errors + 48 mid-walk sideways pushes of 0.96 N·s (24 moments x 2 directions,
    runs that fell excluded: the model has no body collisions), against 50 MPa along the print layers.
Stress = 99.9th percentile of each element's highest von Mises over time, away from the supports and loads (voxel
steps make single-voxel peaks meaningless). PETG isotropic E = 2.0 GPa, nu = 0.38 (ASSUMED). Label: CALCULATED.

    python jx0/verify/verify_fea.py      -> jx0/results/verify_fea.json, jx0/results/images/fea_*.png
"""
from __future__ import annotations

import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "calculations" / "structural"))
sys.path.insert(0, str(ROOT / "jx0" / "cad"))
sys.path.insert(0, str(ROOT / "jx0" / "verify"))
from voxel_fea import VoxelModel, iso_D, von_mises  # noqa: E402
import geometry as G  # noqa: E402
from preview import build  # noqa: E402
import robustness as RB  # noqa: E402

OUT = ROOT / "jx0" / "results" / "verify_fea.json"
IMG = ROOT / "jx0" / "results" / "images"
E, NU = 2.0e9, 0.38
ALLOW = {"static_mpa": 50.0, "fatigue_mpa": 15.0}
H = 0.0007                                                         # voxel pitch (m)
HF, HC = G.HF, G.HC
GAITS = ["forward", "forward_slow", "backward", "turn_left", "turn_right", "side_left", "forward_2", "forward_4",
         "backward_2", "backward_4", "turn_left_2", "turn_right_2", "side_left_2", "side_right_2"]


def u_support(axis, centre, hs=1):
    """Node sets of a U-bracket's two interfaces on servo (axis, centre): horn face and hub face annuli."""
    c = np.asarray(centre, float) / 1000
    i = "xyz".index(axis)

    def sel(m):
        a = m.face_annulus(i, c[i] + hs * HF / 1000, c, 0.0032, 0.0098)
        b = m.face_annulus(i, c[i] - hs * HF / 1000, c, 0.0032, 0.0092)
        return np.concatenate([a, b])
    return sel


def cage_load(axis, centre, hs=1):
    """Nodes of a cage's rear plate where the next servo's case sits (its inner face, around the hub hole)."""
    c = np.asarray(centre, float) / 1000
    i = "xyz".index(axis)
    return lambda m: m.face_annulus(i, c[i] - hs * HC / 1000, c, 0.0114, 0.040)


def parts():
    """part -> (primitives, support, load nodes, load point (mm, part frame = link frame), joint, which side's frame)."""
    r, ra = G.roll_servo(), G.ankle_roll_servo()
    zs = -G.SOLE_TO_ANKLE
    y_s = G.yaw_servo(1)
    z_in = (y_s.c["z"] + G.HC) / 1000                                       # yaw case's rear face (plate underside)

    def pelvis_support(m):                                                  # the 4 bolts into the torso floor
        return np.concatenate([m.face_annulus(2, G.TZ0 / 1000, (x / 1000, y / 1000, G.TZ0 / 1000), 0.0016, 0.0045)
                               for x in (-20.0, 24.0) for y in (-25.0, 25.0)])

    def pelvis_load(m):                                                     # the left yaw servo's case, on its plate
        X = m.nodes
        sx = np.abs(X[:, 2] - z_in) <= 0.75 * m.h
        inside = (np.abs(X[:, 0]) <= 0.0128) & (X[:, 1] >= 0.045 - 0.0355) & (X[:, 1] <= 0.045 + 0.0105)
        far = np.hypot(X[:, 0], X[:, 1] - 0.045) >= 0.0114
        return np.nonzero(sx & inside & far)[0]
    return {
        "pelvis": (G.pelvis(), pelvis_support, pelvis_load, (0, G.HIP_Y, y_s.c["z"]), "l_hip_yaw", "parent"),
        "hip_yaw_bracket": (G.hip_yaw_bracket(), lambda m: m.face_annulus(2, G.ZY / 1000, (0, 0, G.ZY / 1000), 0.0032, 0.0098),
                            cage_load("x", (r.c["x"], 0, 0)), (r.c["x"], 0, 0), "l_hip_roll", "parent"),
        "hip_roll_bracket": (G.hip_roll_bracket(), u_support("x", (r.c["x"], 0, 0)), cage_load("y", (0, 0, 0)), (0, 0, 0),
                             "l_hip_pitch", "parent"),
        "thigh": (G.thigh(), u_support("y", (0, 0, 0)), cage_load("y", (0, 0, -G.THIGH)), (0, 0, -G.THIGH), "l_knee", "parent"),
        "shin": (G.shin(), u_support("y", (0, 0, 0)), cage_load("y", (0, 0, -G.SHIN)), (0, 0, -G.SHIN), "l_ankle_pitch", "parent"),
        "ankle_bracket": (G.ankle_bracket(), u_support("y", (0, 0, 0)), cage_load("x", (ra.c["x"], 0, 0)), (ra.c["x"], 0, 0),
                          "l_ankle_roll", "parent"),
        "foot": (G.foot(), lambda m: m.face_annulus(2, zs / 1000, (0, 0, zs / 1000), 0.0, 0.2), u_support("x", (ra.c["x"], 0, 0)),
                 (ra.c["x"], 0, 0), "l_ankle_roll", "child"),
    }


def load_series():
    """Run the load cases once: {set: {joint: {frame: (T, 6) array}}}, plus how many runs fell."""
    walk = [{"gait": g, "scenario": RB.nominal(), "series": True} for g in GAITS]
    worst = [{**s, "series": True} for s in RB.push_specs((8.0,), timings=24)]
    worst += [{**s, "series": True} for s in RB.model_error_specs(42, 7, None, (0, 1))]
    with Pool(os.cpu_count()) as pool:
        rw = pool.map(RB.trial, walk, chunksize=1)
        rs = pool.map(RB.trial, worst, chunksize=1)
    out, fell = {}, 0
    for tag, res in (("walking", rw), ("worst", rw + rs)):
        acc = {}
        for r in res:
            if r["fell"]:
                fell += tag == "worst"
                continue
            for j, e in r["series"].items():
                for fr in ("parent", "child"):
                    acc.setdefault(j, {}).setdefault(fr, []).extend(e[fr])
        out[tag] = {j: {fr: np.asarray(v) for fr, v in e.items()} for j, e in acc.items()}
    return out, fell


def max_vm_over_time(sig_unit, W, far, chunk=400, n_inst=1500):
    """Each element's highest von Mises over the load history W (T, 6), exact for the elements and instants that can
    matter: per-component bounds pick the 1500 most severe instants and the top 3 % of elements (everything else keeps
    its bound, which only overestimates)."""
    vm_k = np.stack([von_mises(sig_unit[k]).max(axis=1) for k in range(6)])  # (6, nel) per unit component
    sens = np.array([vm_k[k][far].max() for k in range(6)])
    proxy = np.abs(W) @ sens                                                # bound on the worst element at each instant
    if len(W) > n_inst:
        W = W[np.argsort(proxy)[-n_inst:]]
    mags = np.abs(W).max(axis=0)
    bound = mags @ vm_k                                                     # |sum| <= sum |.|: von Mises bound
    cand = np.nonzero(far & (bound >= np.percentile(bound[far], 97.0)))[0]
    exact = np.zeros(len(cand))
    su = sig_unit[:, cand]                                                  # (6, nc, 8, 6)
    for a in range(0, len(W), chunk):
        s = np.einsum("tk,keci->teci", W[a:a + chunk], su)
        exact = np.maximum(exact, von_mises(s).max(axis=(0, 2)))
    vm = bound.copy()
    vm[cand] = exact
    return vm


def analyse(name, prims, sup, lod, point_mm, W_walk, W_worst):
    t0 = time.time()
    mm = build(prims).to_mesh()
    mesh = trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3] / 1000, np.asarray(mm.tri_verts))
    model = VoxelModel.from_mesh(mesh, H, iso_D(E, NU)).build()
    ns, nl = sup(model), lod(model)
    if len(ns) < 6 or len(nl) < 6:
        raise RuntimeError(f"{name}: support {len(ns)} / load {len(nl)} nodes")
    model.fix(ns)
    model.factorize()
    U = model.solve(model.wrench_loads(nl, np.asarray(point_mm) / 1000))
    sig = model.corner_stress(U)                                            # (6, nel, 8, 6) Pa per unit F (N) / M (N m)
    from scipy.spatial import cKDTree
    d, _ = cKDTree(model.nodes[np.concatenate([ns, nl])]).query(model.element_centres())
    far = d > 2.5 * H
    out = {"elements": int(len(model.elements)), "dof": int(model.ndof), "support_nodes": int(len(ns)),
           "load_nodes": int(len(nl)), "instants": {"walking": int(len(W_walk)), "worst": int(len(W_worst))}}
    for tag, W in (("walking", W_walk), ("worst", W_worst)):
        vm = max_vm_over_time(sig, W, far) / 1e6
        out[f"{tag}_mpa_p99_9"] = round(float(np.percentile(vm[far], 99.9)), 2)
        out[f"{tag}_mpa_max"] = round(float(vm[far].max()), 2)
        if tag == "worst":
            _image(model, vm, far, name)
    out["fatigue_safety"] = round(ALLOW["fatigue_mpa"] / out["walking_mpa_p99_9"], 1)
    out["static_safety"] = round(ALLOW["static_mpa"] / out["worst_mpa_p99_9"], 1)
    out["seconds"] = round(time.time() - t0, 1)
    return out


def _image(model, vm, far, name):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import warnings
    grid = np.full(model.occ.shape, np.nan)
    e = model.elements
    grid[e[:, 0], e[:, 1], e[:, 2]] = np.where(far, vm, np.nan)
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.4))
    lo, hh = model.origin * 1000, model.h * 1000
    for ax, (red, ia, ib, lab) in zip(axs, [(1, 0, 2, "side (x-z)"), (0, 1, 2, "front (y-z)"), (2, 0, 1, "top (x-y)")]):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            img = np.nanmax(grid, axis=red)
        ext = [lo[ia], lo[ia] + img.shape[0] * hh, lo[ib], lo[ib] + img.shape[1] * hh]
        im = ax.imshow(img.T, origin="lower", extent=ext, cmap="turbo", vmin=0, vmax=ALLOW["fatigue_mpa"], interpolation="nearest")
        ax.set_title(lab, fontsize=9)
        ax.set_aspect("equal")
        ax.set_xlabel("xyz"[ia] + " (mm)")
        ax.set_ylabel("xyz"[ib] + " (mm)")
    fig.colorbar(im, ax=axs, shrink=0.8, label="von Mises over the worst load history (MPa); top of scale = PETG fatigue 15 MPa")
    fig.suptitle(f"JX0 v0.4 {name}: voxel FEA, simulated walking + pushes", fontsize=10)
    IMG.mkdir(parents=True, exist_ok=True)
    fig.savefig(IMG / f"fea_{name}.png", dpi=90, bbox_inches="tight")
    plt.close(fig)


def main():
    t0 = time.time()
    series, fell = load_series()
    print(f"load histories: {time.time() - t0:.0f} s ({fell} runs fell, excluded)", flush=True)
    res = {}
    only = sys.argv[1:]
    if only and OUT.exists():
        res = json.loads(OUT.read_text(encoding="utf-8"))["parts"]
    for name, (prims, sup, lod, pt, joint, frame) in parts().items():
        if only and name not in only:
            continue
        r = analyse(name, prims, sup, lod, pt, series["walking"][joint][frame], series["worst"][joint][frame])
        res[name] = {"loaded_by": f"{joint} ({frame} frame)", **r}
        print(f"{name:17s} {r['elements']:7d} el  walking {r['walking_mpa_p99_9']:5.2f} MPa (fatigue SF {r['fatigue_safety']:4.1f})  "
              f"worst {r['worst_mpa_p99_9']:5.2f} MPa (static SF {r['static_safety']:4.1f})  {r['seconds']} s", flush=True)
    OUT.write_text(json.dumps({"generated_by": "jx0/verify/verify_fea.py", "label": "CALCULATED (voxel FEA, PETG ASSUMED)",
                               "material": {"E_gpa": E / 1e9, "nu": NU, **ALLOW}, "voxel_mm": H * 1000,
                               "load_cases": {"walking": "14 gaits, nominal robot", "worst": "+ 42 model-error walks + 48 pushes of 0.96 N.s",
                                              "runs_that_fell_excluded": fell},
                               "parts": res, "seconds": round(time.time() - t0, 1)}, indent=1), encoding="utf-8")
    print("->", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
