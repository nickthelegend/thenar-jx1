"""Linear-elastic voxel FEA for JX1 structural parts (no commercial FEA licence available — see docs/open_issues.md OI-4).

Method
  * the part STL (exported from the native SolidWorks part, part frame) is voxelised on a regular grid of pitch h;
  * every voxel is an 8-node hexahedron with Wilson/Taylor incompatible bending modes (9 internal DOF, statically
    condensed) — exact for pure bending of a rectangular element, so 3-4 elements through an 8 mm plate suffice;
  * anisotropic (transversely isotropic) material for FDM prints is supported through a 6x6 D matrix;
  * interfaces are node sets picked geometrically (mounting-face annuli, pin bores); supports are fixed, loads are
    wrenches distributed RBE3-style (minimum-norm nodal forces that reproduce the resultant force and moment);
  * the stiffness matrix is factorised once (SuperLU) and reused for all unit load cases, so stresses of any
    combination / sign permutation are obtained by superposition;
  * stresses are evaluated at the 8 corners of each element (incompatible modes included) -> element max von Mises.

Limitations (stated in every report): stair-stepped boundaries create artificial notches — peak values at single
voxels are not meaningful, the 99.5th percentile away from load introduction is reported and the geometric stress
concentration of holes is covered by hand-calculation Kt factors; linear material, no contact, bolts idealised as
bonded contact annuli.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

GP = np.array([-1.0, 1.0]) / np.sqrt(3.0)
CORNERS = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]], float)


def iso_D(E, nu):
    lam, mu = E * nu / ((1 + nu) * (1 - 2 * nu)), E / (2 * (1 + nu))
    D = np.zeros((6, 6))
    D[:3, :3] = lam
    D[np.arange(3), np.arange(3)] += 2 * mu
    D[3, 3] = D[4, 4] = D[5, 5] = mu
    return D


def transverse_iso_D(E_p, E_z, nu_p, nu_pz, G_pz, axis=2):
    """Transversely isotropic compliance -> stiffness. p = in-plane (print layer), z = build direction (`axis`)."""
    G_p = E_p / (2 * (1 + nu_p))
    S = np.zeros((6, 6))
    S[0, 0] = S[1, 1] = 1 / E_p
    S[2, 2] = 1 / E_z
    S[0, 1] = S[1, 0] = -nu_p / E_p
    S[0, 2] = S[2, 0] = S[1, 2] = S[2, 1] = -nu_pz / E_p
    S[3, 3] = 1 / G_p        # gamma_xy (in-plane)
    S[4, 4] = S[5, 5] = 1 / G_pz
    D = np.linalg.inv(S)
    # cyclic axis relabelling so the material build direction (3) is global `axis`; Voigt order xx yy zz xy yz zx
    p = {2: [0, 1, 2, 3, 4, 5], 0: [2, 0, 1, 5, 3, 4], 1: [1, 2, 0, 4, 5, 3]}[axis]
    return D[np.ix_(p, p)]


def _dN(xi, eta, zeta):
    """Derivatives of the 8 trilinear shape functions w.r.t. (xi, eta, zeta): shape (8, 3)."""
    c = CORNERS
    d = np.empty((8, 3))
    d[:, 0] = c[:, 0] * (1 + c[:, 1] * eta) * (1 + c[:, 2] * zeta) / 8
    d[:, 1] = c[:, 1] * (1 + c[:, 0] * xi) * (1 + c[:, 2] * zeta) / 8
    d[:, 2] = c[:, 2] * (1 + c[:, 0] * xi) * (1 + c[:, 1] * eta) / 8
    return d


def _B_from_grads(g):
    """Strain-displacement matrix for nodal gradient rows g (n, 3) -> (6, 3n); strains xx yy zz xy yz zx."""
    n = g.shape[0]
    B = np.zeros((6, 3 * n))
    for i in range(n):
        gx, gy, gz = g[i]
        B[:, 3 * i:3 * i + 3] = [[gx, 0, 0], [0, gy, 0], [0, 0, gz], [gy, gx, 0], [0, gz, gy], [gz, 0, gx]]
    return B


def element_matrices(h, D):
    """Condensed 24x24 stiffness of a cube of side h with incompatible modes, plus corner stress operators."""
    s = 2.0 / h                       # d(xi)/dx
    detJ = (h / 2) ** 3
    Kuu, Kua, Kaa = np.zeros((24, 24)), np.zeros((24, 9)), np.zeros((9, 9))
    for xi, eta, ze in itertools.product(GP, GP, GP):
        Bu = _B_from_grads(_dN(xi, eta, ze) * s)
        Ba = _B_from_grads(np.array([[-2 * xi, 0, 0], [0, -2 * eta, 0], [0, 0, -2 * ze]]) * s)
        Kuu += Bu.T @ D @ Bu * detJ
        Kua += Bu.T @ D @ Ba * detJ
        Kaa += Ba.T @ D @ Ba * detJ
    Kaa_inv_Kau = np.linalg.solve(Kaa, Kua.T)
    KE = Kuu - Kua @ Kaa_inv_Kau
    # corner stress operators: sigma_c = D (Bu_c - Ba_c Kaa^-1 Kau) u_e
    S = []
    for c in CORNERS:
        Bu = _B_from_grads(_dN(*c) * s)
        Ba = _B_from_grads(np.array([[-2 * c[0], 0, 0], [0, -2 * c[1], 0], [0, 0, -2 * c[2]]]) * s)
        S.append(D @ (Bu - Ba @ Kaa_inv_Kau))
    return 0.5 * (KE + KE.T), np.array(S)     # (24,24), (8,6,24)


def von_mises(sig):
    sx, sy, sz, txy, tyz, tzx = np.moveaxis(sig, -1, 0)
    return np.sqrt(0.5 * ((sx - sy) ** 2 + (sy - sz) ** 2 + (sz - sx) ** 2) + 3 * (txy ** 2 + tyz ** 2 + tzx ** 2))


@dataclass
class VoxelModel:
    occ: np.ndarray                   # bool (nx, ny, nz) occupancy
    origin: np.ndarray                # xyz of voxel (0,0,0) lower corner [m]
    h: float                          # voxel pitch [m]
    D: np.ndarray                     # 6x6 material matrix [Pa]
    fixed: set = field(default_factory=set)          # fixed DOF indices
    _lu: object = None

    @classmethod
    def from_mesh(cls, mesh_m, h, D, offset=(0.0, 0.0, 0.0)):
        """Voxelise a watertight trimesh (metres): a voxel is solid if its centre lies inside the mesh.

        Scanline parity fill: one vertical ray per (x, y) column of voxel centres, crossings with every triangle
        found by 2-D barycentric tests, sorted per column and filled between crossing pairs. Column centres carry a
        tiny irrational offset so rays never pass exactly through mesh edges/vertices.
        """
        lo, hi = mesh_m.bounds
        # grid snapped to multiples of h (+ optional offset) so whole-millimetre CAD faces fall on voxel boundaries
        origin = np.floor((lo - np.asarray(offset)) / h) * h - h + np.asarray(offset)
        n = np.ceil((hi - origin) / h).astype(int) + 1
        ox, oy = origin[0] + 1.234567e-9, origin[1] + 2.345678e-9
        cols, zs = [], []
        for (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) in mesh_m.triangles:
            d = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
            if abs(d) < 1e-18:
                continue                                    # triangle parallel to the rays
            i0 = max(int(np.ceil((min(x0, x1, x2) - ox) / h - 0.5)), 0)
            i1 = min(int(np.floor((max(x0, x1, x2) - ox) / h - 0.5)), n[0] - 1)
            j0 = max(int(np.ceil((min(y0, y1, y2) - oy) / h - 0.5)), 0)
            j1 = min(int(np.floor((max(y0, y1, y2) - oy) / h - 0.5)), n[1] - 1)
            if i1 < i0 or j1 < j0:
                continue
            I, J = np.meshgrid(np.arange(i0, i1 + 1), np.arange(j0, j1 + 1), indexing="ij")
            X, Y = ox + (I + 0.5) * h, oy + (J + 0.5) * h
            a = ((y1 - y2) * (X - x2) + (x2 - x1) * (Y - y2)) / d
            b = ((y2 - y0) * (X - x2) + (x0 - x2) * (Y - y2)) / d
            c = 1 - a - b
            ins = (a >= 0) & (b >= 0) & (c >= 0)
            if ins.any():
                cols.append((I[ins] * n[1] + J[ins]).ravel())
                zs.append((a * z0 + b * z1 + c * z2)[ins].ravel())
        occ = np.zeros(n, bool)
        if not cols:
            return cls(occ, origin, h, D)
        cols, zs = np.concatenate(cols), np.concatenate(zs)
        order = np.lexsort((zs, cols))
        cols, zs = cols[order], zs[order]
        starts = np.flatnonzero(np.r_[True, cols[1:] != cols[:-1]])
        ends = np.r_[starts[1:], len(cols)]
        bad = 0
        for s_, e_ in zip(starts, ends):
            zc = zs[s_:e_]
            if len(zc) % 2:
                bad += 1
                zc = zc[:-1]
            i, j = divmod(int(cols[s_]), n[1])
            for za, zb in zip(zc[0::2], zc[1::2]):
                k0 = max(int(np.ceil((za - origin[2]) / h - 0.5)), 0)
                k1 = min(int(np.floor((zb - origin[2]) / h - 0.5)), n[2] - 1)
                if k1 >= k0:
                    occ[i, j, k0:k1 + 1] = True
        m = cls(occ, origin, h, D)
        m.parity_errors = bad
        return m

    def build(self):
        occ = self.occ
        nx, ny, nz = occ.shape
        el = np.argwhere(occ)
        offs = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]])
        gnodes = (el[:, None, :] + offs[None]).reshape(-1, 3)
        gid = (gnodes[:, 0] * (ny + 1) + gnodes[:, 1]) * (nz + 1) + gnodes[:, 2]
        uniq, inv = np.unique(gid, return_inverse=True)
        self.elements = el
        self.conn = inv.reshape(-1, 8)
        k = uniq % (nz + 1)
        j = (uniq // (nz + 1)) % (ny + 1)
        i = uniq // ((nz + 1) * (ny + 1))
        self.nodes = self.origin + np.stack([i, j, k], -1) * self.h
        self.ndof = 3 * len(self.nodes)
        self.KE, self.SC = element_matrices(self.h, self.D)
        self.edof = (3 * self.conn[:, :, None] + np.arange(3)[None, None, :]).reshape(-1, 24)
        return self

    # ----------------------------------------------------------------------------- node selections
    def select(self, pred):
        return np.nonzero(pred(self.nodes))[0]

    def face_annulus(self, axis, value, centre, r_in, r_out, tol=None):
        """Nodes on the plane coordinate[axis] == value (within tol) inside an annulus around `centre`."""
        tol = self.h * 0.75 if tol is None else tol
        c = np.asarray(centre, float)
        other = [a for a in range(3) if a != axis]

        def pred(X):
            r = np.linalg.norm(X[:, other] - c[other], axis=1)
            return (np.abs(X[:, axis] - value) <= tol) & (r >= r_in) & (r <= r_out)
        return self.select(pred)

    def bore(self, axis, centre, radius, span, tol=None):
        """Nodes on/near a cylindrical bore (pin hole) of `radius` along `axis` through `centre`, within `span` (lo, hi)."""
        tol = self.h * 1.25 if tol is None else tol
        c = np.asarray(centre, float)
        other = [a for a in range(3) if a != axis]

        def pred(X):
            r = np.linalg.norm(X[:, other] - c[other], axis=1)
            return (r >= radius - 0.25 * self.h) & (r <= radius + tol) & (X[:, axis] >= span[0]) & (X[:, axis] <= span[1])
        return self.select(pred)

    # ----------------------------------------------------------------------------- loads & solve
    def fix(self, nodes, dofs=(0, 1, 2)):
        self.fixed |= set(int(3 * n + d) for n in nodes for d in dofs)

    def rigid_fit(self, U, nodes, point):
        """Best-fit rigid motion (translation of `point`, small rotation) of a node set for each case: (ncase, 6)."""
        X = self.nodes[nodes]
        c = X.mean(0)
        r = X - c
        J = (r ** 2).sum() * np.eye(3) - r.T @ r
        Jinv = np.linalg.pinv(J)
        u = U[:, (3 * nodes[:, None] + np.arange(3))]           # (ncase, n, 3)
        t = u.mean(1)
        th = np.einsum("ij,cj->ci", Jinv, np.cross(r[None], u - t[:, None, :]).sum(1))
        tp = t + np.cross(th, np.asarray(point) - c)
        return np.concatenate([tp, th], axis=1)

    def wrench_loads(self, nodes, point):
        """6 unit load vectors (Fx, Fy, Fz [1 N], Mx, My, Mz [1 N m] about `point`) distributed RBE3-style on `nodes`."""
        X = self.nodes[nodes]
        c = X.mean(0)
        r = X - c
        J = (r ** 2).sum() * np.eye(3) - r.T @ r
        Jinv = np.linalg.pinv(J)
        out = []
        for k in range(6):
            F = np.zeros(3)
            M = np.zeros(3)
            (F if k < 3 else M)[k % 3] = 1.0
            Mc = M + np.cross(np.asarray(point) - c, F)      # moment about the node-set centroid
            f = F / len(nodes) + np.cross(Jinv @ Mc, r)
            vec = np.zeros(self.ndof)
            vec[(3 * nodes[:, None] + np.arange(3)).ravel()] = f.ravel()
            out.append(vec)
        return np.array(out)

    def assemble(self, chunk=20000):
        """Global stiffness (CSR), assembled in element chunks with int32 indices to bound peak memory."""
        K = None
        ke = self.KE.ravel()
        for a in range(0, len(self.conn), chunk):
            ed = self.edof[a:a + chunk].astype(np.int32)
            rows = np.repeat(ed, 24, axis=1).ravel()
            cols = np.tile(ed, (1, 24)).ravel()
            data = np.tile(ke, len(ed))
            part = sp.coo_matrix((data, (rows, cols)), shape=(self.ndof, self.ndof)).tocsr()
            del rows, cols, data
            K = part if K is None else K + part
        return K

    def factorize(self, direct_max_dof=40000, coarse_dof=30000):
        """Direct SuperLU for small models, geometric-multigrid preconditioned block CG for large ones."""
        K = self.assemble()
        fdof = np.array(sorted(self.fixed), int)
        self.free = np.setdiff1d(np.arange(self.ndof), fdof)
        Kff = K[self.free][:, self.free].tocsr()
        if len(self.free) <= direct_max_dof:
            self._lu = spla.splu(Kff.tocsc(), permc_spec="MMD_AT_PLUS_A")
            self._gmg = None
        else:
            self._lu = None
            self._Kff = Kff
            self._gmg = GMG(self, Kff, coarse_dof=coarse_dof)
        return self

    def solve(self, F, tol=1e-8, maxit=600):
        """F: (ncase, ndof) -> displacements (ncase, ndof)."""
        F = np.atleast_2d(F)
        U = np.zeros_like(F)
        if self._lu is not None:
            for i, f in enumerate(F):
                U[i, self.free] = self._lu.solve(f[self.free])
            return U
        B = F[:, self.free].T.copy()                            # (nfree, ncase)
        X, it, res = block_pcg(self._Kff, B, self._gmg, tol, maxit)
        self.last_iterations, self.last_residual = it, res
        U[:, self.free] = X.T
        return U

    def corner_stress(self, U):
        """Stress at the 8 corners of every element for each load case: (ncase, nel, 8, 6) [Pa]."""
        ue = U[:, self.edof]                                   # (ncase, nel, 24)
        return np.einsum("cij,nej->neci", self.SC, ue)

    def element_centres(self):
        return self.origin + (self.elements + 0.5) * self.h


def _prolongation(occ_f, origin, h):
    """Trilinear prolongation from the 2h grid to the h grid (full node sets of both levels).

    Returns (P, occ_c, conn_nodes_c) where P maps coarse node DOFs -> fine node DOFs (3 per node)."""
    nx, ny, nz = occ_f.shape
    pad = [(0, s % 2) for s in occ_f.shape]
    o = np.pad(occ_f, pad)
    occ_c = o.reshape(o.shape[0] // 2, 2, o.shape[1] // 2, 2, o.shape[2] // 2, 2).any(axis=(1, 3, 5))
    return occ_c


class Level:
    def __init__(self, occ, origin, h):
        self.occ, self.origin, self.h = occ, origin, h
        el = np.argwhere(occ)
        offs = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]])
        g = (el[:, None, :] + offs[None]).reshape(-1, 3)
        ny1, nz1 = occ.shape[1] + 1, occ.shape[2] + 1
        gid = (g[:, 0] * ny1 + g[:, 1]) * nz1 + g[:, 2]
        self.gids = np.unique(gid)                              # sorted global node ids (grid index)
        self.dims = (occ.shape[0] + 1, ny1, nz1)

    def index_of(self, gid):
        pos = np.searchsorted(self.gids, gid)
        pos = np.clip(pos, 0, len(self.gids) - 1)
        ok = self.gids[pos] == gid
        return np.where(ok, pos, -1)


def _build_P(fine: Level, coarse: Level):
    """Sparse trilinear interpolation (fine nodes x coarse nodes), scalar (one DOF per node)."""
    ny1, nz1 = fine.dims[1], fine.dims[2]
    gid = fine.gids
    i, j, k = gid // (ny1 * nz1), (gid // nz1) % ny1, gid % nz1
    rows, cols, vals = [], [], []
    cny1, cnz1 = coarse.dims[1], coarse.dims[2]
    for di in (0, 1):
        for dj in (0, 1):
            for dk in (0, 1):
                ci = i // 2 + di * (i % 2)
                cj = j // 2 + dj * (j % 2)
                ck = k // 2 + dk * (k % 2)
                w = np.where(i % 2, 0.5, 1.0 if di == 0 else 0.0) * np.where(j % 2, 0.5, 1.0 if dj == 0 else 0.0) * \
                    np.where(k % 2, 0.5, 1.0 if dk == 0 else 0.0)
                cg = (ci * cny1 + cj) * cnz1 + ck
                c = coarse.index_of(cg)
                ok = (w > 0) & (c >= 0)
                rows.append(np.nonzero(ok)[0])
                cols.append(c[ok])
                vals.append(w[ok])
    rows, cols, vals = np.concatenate(rows), np.concatenate(cols), np.concatenate(vals)
    return sp.coo_matrix((vals, (rows, cols)), shape=(len(fine.gids), len(coarse.gids))).tocsr()


class GMG:
    """Galerkin geometric multigrid V-cycle (l1-Jacobi smoothing) on the voxel hierarchy, used as CG preconditioner."""

    def __init__(self, model, Kff, coarse_dof=30000, sweeps=3):
        self.sweeps = sweeps
        lv = Level(model.occ, model.origin, model.h)
        # fine-level node order of the model equals Level order (both sorted unique grid ids)
        free = model.free
        A = Kff
        self.A, self.P, self.Dinv = [A], [], []
        Pdof_prev = None
        restrict = sp.identity(3 * len(lv.gids), format="csr")[free]      # free DOF selection at the fine level
        while A.shape[0] > coarse_dof:
            occ_c = _prolongation(lv.occ, lv.origin, lv.h)
            lc = Level(occ_c, lv.origin, lv.h * 2)
            Ps = _build_P(lv, lc)
            Pd = sp.kron(Ps, sp.identity(3), format="csr")                 # vector DOFs, node-major (x, y, z)
            Pf = (restrict @ Pd).tocsc()
            keep = np.flatnonzero(np.asarray(abs(Pf).sum(axis=0)).ravel() > 0)
            Pf = Pf[:, keep].tocsr()
            Ac = (Pf.T @ A @ Pf).tocsr()
            self.P.append(Pf)
            self.A.append(Ac)
            restrict = sp.identity(Pd.shape[1], format="csr")[keep]
            A, lv = Ac, lc
            if len(self.P) > 6:
                break
        for Al in self.A[:-1]:
            self.Dinv.append(1.0 / np.asarray(abs(Al).sum(axis=1)).ravel())  # l1-Jacobi
        # near clamped supports some coarse DOFs interpolate to the same few free fine DOFs (dependent columns);
        # a tiny diagonal shift keeps the coarsest operator SPD — CG still converges to the exact fine solution
        Ac = self.A[-1]
        shift = 1e-8 * float(Ac.diagonal().mean())
        self.coarse = spla.splu((Ac + shift * sp.identity(Ac.shape[0], format="csr")).tocsc(), permc_spec="MMD_AT_PLUS_A")
        self.levels = len(self.A)

    def _vcycle(self, l, b):
        if l == self.levels - 1:
            return self.coarse.solve(b)
        A, Dinv = self.A[l], self.Dinv[l][:, None] if b.ndim == 2 else self.Dinv[l]
        x = Dinv * b
        for _ in range(self.sweeps - 1):
            x += Dinv * (b - A @ x)
        r = b - A @ x
        x += self.P[l] @ self._vcycle(l + 1, self.P[l].T @ r)
        for _ in range(self.sweeps):
            x += Dinv * (b - A @ x)
        return x

    def __call__(self, b):
        return self._vcycle(0, b)


def block_pcg(A, B, M, tol=1e-8, maxit=600):
    """Preconditioned CG applied independently (but vectorised) to every column of B."""
    X = np.zeros_like(B)
    R = B.copy()
    Z = M(R)
    P = Z.copy()
    rz = (R * Z).sum(0)
    bn = np.linalg.norm(B, axis=0)
    bn[bn == 0] = 1.0
    it = 0
    for it in range(1, maxit + 1):
        AP = A @ P
        alpha = rz / np.maximum((P * AP).sum(0), 1e-300)
        X += alpha * P
        R -= alpha * AP
        res = np.linalg.norm(R, axis=0) / bn
        if res.max() < tol:
            break
        Z = M(R)
        rz_new = (R * Z).sum(0)
        beta = rz_new / np.maximum(rz, 1e-300)
        P = Z + beta * P
        rz = rz_new
    return X, it, float(res.max())


def envelope_von_mises(sig_unit, scale, signs="all"):
    """Max over sign permutations of sum_k s_k * scale_k * sig_unit[k]; sig_unit (6, nel, 8, 6) -> (nel,) [Pa]."""
    k_active = [k for k in range(len(scale)) if scale[k] != 0]
    best = np.zeros(sig_unit.shape[1])
    perms = itertools.product((1, -1), repeat=len(k_active)) if signs == "all" else [tuple([1] * len(k_active))]
    for sg in perms:
        s = np.zeros(sig_unit.shape[1:])
        for k, g in zip(k_active, sg):
            s += g * scale[k] * sig_unit[k]
        best = np.maximum(best, von_mises(s).max(axis=1))
    return best
