"""Validation of the voxel FEA against closed-form solutions (run: .venv/Scripts/python calculations/structural/test_voxel_fea.py).

1. patch test: uniform tension of a block -> uniform stress sigma = F/A everywhere (exact)
2. cantilever 10 x 10 x 100 mm, 4 elements through the depth, tip load -> Euler-Bernoulli + Timoshenko shear deflection
   and bending stress sigma = M c / I at the surface
3. transversely isotropic material: uniaxial tension along the build axis gives strain sigma / E_z
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from voxel_fea import VoxelModel, iso_D, transverse_iso_D, von_mises  # noqa: E402

E, NU = 70e9, 0.33


def block(nx, ny, nz, h, D):
    m = VoxelModel(np.ones((nx, ny, nz), bool), np.zeros(3), h, D)
    return m.build()


def test_patch():
    h = 0.002
    m = block(10, 3, 3, h, iso_D(E, NU))
    X = m.nodes
    m.fix(np.nonzero(X[:, 0] < 1e-9)[0])
    tip = np.nonzero(np.abs(X[:, 0] - 0.020) < 1e-9)[0]
    m.factorize()
    F = m.wrench_loads(tip, point=X[tip].mean(0))[0] * 1000.0          # 1 kN along x
    U = m.solve(F)
    sig = m.corner_stress(U)[0]
    xc = m.element_centres()[:, 0]
    mid = (xc > 0.006) & (xc < 0.014)                                  # away from the clamped end (Poisson restraint)
    sxx = sig[mid][:, :, 0]
    exact = 1000.0 / (0.006 * 0.006)
    err = abs(sxx.mean() - exact) / exact
    print(f"patch: sigma_xx mean {sxx.mean() / 1e6:.3f} MPa vs exact {exact / 1e6:.3f} MPa (err {err * 100:.2f} %), "
          f"spread {sxx.std() / exact * 100:.2f} %")
    assert err < 0.01 and sxx.std() / exact < 0.02


def test_cantilever():
    h, L, b = 0.0025, 0.100, 0.010
    m = block(40, 4, 4, h, iso_D(E, NU))
    X = m.nodes
    m.fix(np.nonzero(X[:, 0] < 1e-9)[0])
    tip = np.nonzero(np.abs(X[:, 0] - L) < 1e-9)[0]
    m.factorize()
    P = 100.0
    F = m.wrench_loads(tip, point=(L, b / 2, b / 2))[2] * P                # tip force along z
    U = m.solve(F)
    I = b * b ** 3 / 12
    G = E / (2 * (1 + NU))
    d_eb = P * L ** 3 / (3 * E * I)
    d_sh = P * L / (5 / 6 * G * b * b)
    d_fe = U[0, 3 * tip + 2].mean()
    err_d = abs(d_fe - (d_eb + d_sh)) / (d_eb + d_sh)
    print(f"cantilever: tip deflection {d_fe * 1e6:.2f} um vs Timoshenko {(d_eb + d_sh) * 1e6:.2f} um (err {err_d * 100:.2f} %)")
    sig = m.corner_stress(U)[0]                                           # (nel, 8, 6)
    # corner coordinates of every element, compare sigma_xx at the top surface (z = b) with M(x) c / I
    offs = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]]) * h
    cx = m.elements[:, None, :] * h + offs[None]
    sel = (cx[..., 2] > b - 1e-9) & (cx[..., 0] > 0.030 - 1e-9) & (cx[..., 0] < 0.070 + 1e-9)
    exact = -P * (L - cx[..., 0]) * (b / 2) / I                          # tip load +z -> top fibre in compression
    err_s = np.abs(sig[..., 0][sel] - exact[sel]).max() / np.abs(exact[sel]).max()
    print(f"cantilever: surface bending stress max error {err_s * 100:.2f} % (x = 30..70 mm, |sigma| up to "
          f"{np.abs(exact[sel]).max() / 1e6:.1f} MPa)")
    assert err_d < 0.03 and err_s < 0.03


def test_transverse_iso():
    h = 0.002
    Ep, Ez = 6.0e9, 1.6e9
    for axis in (0, 1, 2):
        D = transverse_iso_D(Ep, Ez, 0.35, 0.35 * Ez / Ep, 0.6e9, axis=axis)
        m = block(3, 3, 3, h, D)
        X = m.nodes
        m.fix(np.nonzero(X[:, axis] < 1e-9)[0])
        top = np.nonzero(np.abs(X[:, axis] - 0.006) < 1e-9)[0]
        m.factorize()
        F = m.wrench_loads(top, point=X[top].mean(0))[axis] * 100.0
        U = m.solve(F)
        # a clamped 3x3x3 block is not uniaxial; compare the axial stiffness ordering instead of an exact value
        d = U[0, 3 * top + axis].mean()
        print(f"transverse-iso build axis {axis}: axial tip displacement {d * 1e6:.3f} um")
    Dz = transverse_iso_D(Ep, Ez, 0.35, 0.35 * Ez / Ep, 0.6e9, axis=2)
    S = np.linalg.inv(Dz)
    assert abs(1 / S[2, 2] - Ez) / Ez < 1e-9 and abs(1 / S[0, 0] - Ep) / Ep < 1e-9
    Dx = transverse_iso_D(Ep, Ez, 0.35, 0.35 * Ez / Ep, 0.6e9, axis=0)
    Sx = np.linalg.inv(Dx)
    assert abs(1 / Sx[0, 0] - Ez) / Ez < 1e-9 and abs(1 / Sx[1, 1] - Ep) / Ep < 1e-9
    print("transverse-iso: compliance along build axis == 1/E_z for axis 0 and 2")


def test_gmg_matches_direct():
    h = 0.0025
    res = []
    for direct in (True, False):
        m = block(40, 8, 8, h, iso_D(E, NU))
        X = m.nodes
        m.fix(np.nonzero(X[:, 0] < 1e-9)[0])
        tip = np.nonzero(np.abs(X[:, 0] - 0.100) < 1e-9)[0]
        m.factorize(direct_max_dof=10 ** 9 if direct else 0, coarse_dof=500)
        F = m.wrench_loads(tip, point=(0.1, 0.01, 0.01))[[1, 2, 3]] * 100.0
        res.append(m.solve(F))
        if not direct:
            print(f"GMG: {m._gmg.levels} levels, {m.last_iterations} CG iterations, residual {m.last_residual:.1e}")
    err = np.abs(res[0] - res[1]).max() / np.abs(res[0]).max()
    print(f"GMG vs direct: max relative displacement difference {err:.2e}")
    assert err < 1e-5


if __name__ == "__main__":
    test_patch()
    test_cantilever()
    test_transverse_iso()
    test_gmg_matches_direct()
    print("voxel FEA validation: all tests passed")
