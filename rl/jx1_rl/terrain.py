"""Procedural terrain for the rough-ground task: a MuJoCo heightfield + a numpy height lookup for rewards and spawning.

Tiles of 2 m on a square map: flat, smooth noise (uneven floor), ramps up to max_slope_deg, and random steps up to
max_step_m (thresholds, cable covers). The policy stays blind (no height scan): the same 47-D observation and
deployment contract as on flat ground. Heights are in metres; MuJoCo stores them normalised to [0, 1] x elevation.
"""
from __future__ import annotations

import math

import mujoco
import numpy as np


class Terrain:
    def __init__(self, cfg: dict, seed: int = 0):
        rng = np.random.default_rng(seed)
        self.size = float(cfg["size_m"])                     # square side
        self.res = float(cfg["resolution_m"])
        n = int(round(self.size / self.res)) + 1
        tile = int(round(cfg.get("tile_m", 2.0) / self.res))
        h = np.zeros((n, n))
        kinds = cfg.get("tiles", ["flat", "noise", "slope", "steps"])
        c = n // 2
        r = max(1, int(round(cfg.get("flat_spawn_radius_m", 1.0) / self.res)))
        for i0 in range(0, n - tile + 1, tile):           # whole tiles only (the last map row stays flat)
            for j0 in range(0, n - tile + 1, tile):
                kind = kinds[rng.integers(len(kinds))]
                if i0 < c + r and i0 + tile > c - r and j0 < c + r and j0 + tile > c - r:
                    kind = "flat"                              # tiles under the central spawn patch stay flat
                sl = (slice(i0, min(i0 + tile, n)), slice(j0, min(j0 + tile, n)))
                ni, nj = h[sl].shape
                # every tile except "steps" returns to zero at its edges, so neighbouring tiles join without cliffs
                wi = np.sin(np.pi * (np.arange(ni) + 0.5) / ni)
                wj = np.sin(np.pi * (np.arange(nj) + 0.5) / nj)
                if kind == "noise":
                    coarse = rng.uniform(-1, 1, (max(2, -(-ni // 6)), max(2, -(-nj // 6))))
                    fine = np.kron(coarse, np.ones((6, 6)))[:ni, :nj]
                    h[sl] = fine * cfg["noise_m"] * np.minimum(1.0, 3 * np.outer(wi, wj))
                elif kind == "slope":
                    # dome / bowl A sin(pi u) sin(pi v): zero on all four edges, steepest gradient A pi / L = tan(slope)
                    ang = math.radians(rng.uniform(0.3, 1.0) * cfg["max_slope_deg"]) * rng.choice((-1, 1))
                    A = math.tan(ang) * min(ni, nj) * self.res / math.pi
                    h[sl] = A * np.outer(wi, wj)
                elif kind == "steps":
                    w = max(2, int(round(0.4 / self.res)))
                    for a in range(0, ni, w):
                        h[sl][a:a + w, :] = rng.uniform(-cfg["max_step_m"], cfg["max_step_m"])
        self.h = h - h.min()
        self.z0 = float(self.h[c, c])                          # centre height
        self.rows = n

    def add_to_spec(self, spec: mujoco.MjSpec, floor_name="floor"):
        """Replace the floor plane by a heightfield geom with the same contact settings."""
        floor = next(g for g in spec.geoms if g.name == floor_name)
        elev = max(float(self.h.max()), 1e-3)
        spec.add_hfield(name="terrain", size=[self.size / 2, self.size / 2, elev, 0.1], nrow=self.rows, ncol=self.rows,
                        userdata=(self.h / elev).flatten().tolist())
        g = spec.worldbody.add_geom(name="terrain", type=mujoco.mjtGeom.mjGEOM_HFIELD, hfieldname="terrain",
                                    pos=[0, 0, -self.z0], contype=floor.contype, conaffinity=floor.conaffinity,
                                    friction=floor.friction, solref=floor.solref, rgba=[0.55, 0.6, 0.55, 1])
        spec.delete(floor)
        return g

    def height(self, x, y):
        """Terrain height (world z) at x, y (arrays), bilinear; the map is centred on the origin."""
        u = (np.asarray(x) + self.size / 2) / self.res
        v = (np.asarray(y) + self.size / 2) / self.res
        u = np.clip(u, 0, self.rows - 1.001)
        v = np.clip(v, 0, self.rows - 1.001)
        i0, j0 = np.floor(v).astype(int), np.floor(u).astype(int)       # MuJoCo hfield rows run along y
        fu, fv = u - j0, v - i0
        h = self.h
        z = (h[i0, j0] * (1 - fu) * (1 - fv) + h[i0, j0 + 1] * fu * (1 - fv) + h[i0 + 1, j0] * (1 - fu) * fv + h[i0 + 1, j0 + 1] * fu * fv)
        return z - self.z0
