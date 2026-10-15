"""JX0 fit check against the REAL STS3215, before anything is printed (no SolidWorks needed):

0. every printed part is one solid piece;
1. the real servo at all 17 joints: geometry.servo_st() (the Feetech factory model / SO-ARM100 model envelope: case,
   rear pad, label block, both horns, output strip) and, as a second opinion, TheRobotStudio's SO-ARM100 STS3215 mesh
   (jx0/cad/vendor), intersected with every printed part at the zero pose;
2. the cables: each servo's cable keep-out (geometry.servo_cables) must be free of every part;
3. every screw (geometry.SCREWS), measured on the solids along its axis: the plate under its head, the gap to what it
   screws into, the thread length that gives in the horn / case / insert / printed hole (against what that hole can
   take: the drive horn with 0-2 shims, the passive horn, the case's 2.9 mm holes), that the axis is on a real hole of
   the servo, and that its head has room (nothing inside the head's cylinder);
4. assembly, in the build guide's order: each servo slid into its cage and each bracket slid onto its servo along its
   path (1 mm steps from 60 mm out), and a straight screwdriver along every screw's axis, against what is already
   assembled at that step.

    python jx0/verify/verify_fit.py          -> jx0/results/verify_fit.json
    python jx0/verify/verify_fit.py --quick  (1-3 only)
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import trimesh
from manifold3d import Manifold, Mesh

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "jx0" / "cad"))
import geometry as G  # noqa: E402
import layout as L  # noqa: E402
from preview import build  # noqa: E402

OUT = ROOT / "jx0" / "results" / "verify_fit.json"
SO_MESH = ROOT / "jx0" / "cad" / "vendor" / "STS3215_SO-ARM100.stl"
CLASH_MM3 = 0.5
DRIVER = {"M2": 4.5, "M3": 5.6}            # screwdriver / hex key shaft Ø (mm)
PROBE = {"M2": 1.55, "M3": 2.2}             # radius of the rays that measure the plate under a head
THREAD = {"M2": 0.95, "M3": 1.35}           # radius of the rays that measure thread engagement (between hole and major Ø)


def to_tm(m: Manifold) -> trimesh.Trimesh:
    mm = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts), process=False)


def to_mf(t: trimesh.Trimesh) -> Manifold:
    return Manifold(Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))


def mm_pose(M):
    T = np.array(M, float)
    T[:3, 3] *= 1000.0
    return T


def so_arm_mesh():
    """TheRobotStudio's STS3215 (with both horns) in our servo frame, mm."""
    m = trimesh.load(SO_MESH)
    m.apply_scale(1000.0)
    v = np.column_stack([12.5 - m.vertices[:, 0], -m.vertices[:, 1], m.vertices[:, 2]])
    return trimesh.Trimesh(v, m.faces, process=True)


class Scene:
    """Every component and keep-out at the zero pose, as manifolds and trimeshes in the pelvis frame (mm)."""

    def __init__(self):
        self.comps = L.components()
        self.pose = {k: mm_pose(M) for k, _, M in self.comps}
        self.part_of = {k: p for k, p, _ in self.comps}
        lib = {}
        for name, (prims, _, _) in {**G.PARTS, **G.SERVOS}.items():
            lib[name] = build(prims)
        self.lib = lib
        self.mf = {k: lib[p].transform(self.pose[k][:3, :].tolist()) for k, p, _ in self.comps}
        self.tm = {k: to_tm(m) for k, m in self.mf.items()}
        self.servos = [k for k, p, _ in self.comps if p == L.ST]
        self.parts = [k for k, p, _ in self.comps if p != L.ST]

    def place(self, prims_or_mf, key):
        m = prims_or_mf if isinstance(prims_or_mf, Manifold) else build(prims_or_mf)
        return m.transform(self.pose[key][:3, :].tolist())


def clash(a: Manifold, b: Manifold) -> float:
    ba, bb = a.bounding_box(), b.bounding_box()
    if any(ba[i + 3] < bb[i] or bb[i + 3] < ba[i] for i in range(3)):
        return 0.0
    return (a ^ b).volume()


# ------------------------------------------------------------------------------------------------ 1-2 servo and cables
def so_offsets(t: trimesh.Trimesh):
    """The SO-ARM100 mesh's own rear-face contact (lowest point of its rear cover outside the label / horn / sockets)
    and passive-horn face, as servo-frame z shifts that seat it on a cage plate at -HR / under a boss at -HI."""
    v = t.vertices
    pad = v[(v[:, 0] > 5.5) & (v[:, 0] < 34.5) & (np.abs(v[:, 1]) > 9.8) & (v[:, 2] < -14.0) & (v[:, 2] > -17.0)]
    idl = v[(np.hypot(v[:, 0], v[:, 1]) > 4.0) & (np.hypot(v[:, 0], v[:, 1]) < 9.5) & (v[:, 2] < -15.0)]
    return -G.HR - pad[:, 2].min(), -G.HI - idl[:, 2].min()


def servo_and_cables(sc: Scene):
    """Each servo against every part. The SO-ARM100 mesh is seated like the real servo: on its own rear cover against
    its cage (parts on the servo's link, and anything placed through that link) and on its own passive horn against
    the bracket bolted to its horns."""
    so_t = so_arm_mesh()
    cage_dz, horn_dz = so_offsets(so_t)
    so = to_mf(so_t)
    rows = []
    for k in sc.servos:
        mode = L.cable_mode(k)
        horn_part = L.HORN_PART[L.base(k)] + (k[-2:] if k[-2:] in ("_L", "_R") and L.HORN_PART[L.base(k)] not in
                                               ("chest_cap", "neck_hub") else "")
        on = {}
        for name, dz in (("cage", cage_dz), ("horns", horn_dz)):
            S = np.eye(4)
            S[2, 3] = dz
            on[name] = so.transform((sc.pose[k] @ S)[:3, :].tolist())
        for p in sc.parts:
            bodies = {"servo (factory/SO-ARM100 envelope)": sc.mf[k],
                      "servo (SO-ARM100 mesh)": on["horns" if p == horn_part else "cage"],
                      "cables": sc.place(G.servo_cables(mode), k)}
            for what, body in bodies.items():
                v = clash(body, sc.mf[p])
                if v > CLASH_MM3:
                    rows.append({"servo": k, "what": what, "part": p, "mm3": round(v, 1)})
    return rows, {"so_arm_seated_on_cage_dz_mm": round(cage_dz, 2), "so_arm_seated_on_horns_dz_mm": round(horn_dz, 2)}


# ------------------------------------------------------------------------------------------------ 3 screws
def screw_world(sc: Scene, key, s):
    """Screw s of component key -> (seat point, unit direction head->tip, two unit vectors across the axis) in mm."""
    T = sc.pose[key]
    ia = "xyz".index(s["axis"])
    p = np.zeros(3)
    p[ia] = s["seat"]
    for i, v in zip([i for i in range(3) if i != ia], s["c"]):
        p[i] = v
    e = np.zeros(3)
    e[ia] = s["sense"]
    P = T[:3, :3] @ p + T[:3, 3]
    d = T[:3, :3] @ e
    u = np.cross(d, [1.0, 0.0, 0.0] if abs(d[0]) < 0.9 else [0.0, 1.0, 0.0])
    u /= np.linalg.norm(u)
    return P, d, u, np.cross(d, u)


def hits(mesh: trimesh.Trimesh, o, d):
    loc, _, _ = mesh.ray.intersects_location([o], [d], multiple_hits=True)
    if len(loc) == 0:
        return []
    return sorted(float(np.dot(q - o, d)) for q in loc)


def inside_length(mesh, o, d, a, b):
    """Length of the segment o + t d, t in [a, b], inside the (watertight) mesh."""
    ts = [t for t in hits(mesh, o, d) if t > 1e-6]
    inside, last, total = False, 0.0, 0.0
    for t in ts:                                                     # crossings alternate entering / leaving
        if inside:
            total += max(0.0, min(t, b) - max(last, a))
        inside, last = not inside, t
    return total


def first_hit(sc: Scene, o, d, skip=(), tmax=200.0):
    best = (None, tmax)
    for k, m in sc.tm.items():
        if k in skip:
            continue
        h = [t for t in hits(m, o, d) if t > 1e-6]
        if h and h[0] < best[1]:
            best = (k, h[0])
    return best


def check_screw(sc: Scene, key, s):
    P, d, u, v = screw_world(sc, key, s)
    L_ = s["length"]
    own = sc.tm[key]
    r = PROBE[s["size"]]
    ts = []
    for ang in range(0, 360, 45):
        q = P + r * (np.cos(np.radians(ang)) * u + np.sin(np.radians(ang)) * v) - 0.3 * d
        h = [t for t in hits(own, q, d) if t > 1e-6]
        if len(h) >= 2:
            ts.append((h[0] - 0.3, h[1] - h[0]))
    seated = [t for a_, t in ts if abs(a_) < 0.15]                  # rays whose head bears on the surface at the seat
    seat_err = None if not ts else round(min(abs(a_) for a_, _ in ts), 2)
    under = min(seated) if len(seated) >= 3 else (min(t for _, t in ts) if ts else 0.0)
    # the gap to what it screws into, along the axis line offset to the thread radius (the holes there are empty);
    # the ray starts just inside the part, so a face in contact with it counts
    rt = 2.2 if s["into"] == "insert" else THREAD[s["size"]]           # (an insert sits in a 4 mm hole)
    o = P + rt * u + (under - 0.05) * d
    tgt, gap = first_hit(sc, o, d, skip=(key,))
    gap -= 0.05
    e = L_ - under - gap
    res = {"part": key, "size": s["size"], "length": s.get("nominal", L_), "into": s["into"], "note": s["note"],
           "under_head_mm": round(under, 2), "seat_error_mm": None if seat_err is None else round(seat_err, 2),
           "target": tgt, "gap_mm": round(gap, 2), "engagement_mm": round(e, 2), "problems": []}
    pr = res["problems"]
    if len(seated) < 3:
        pr.append(f"the head does not bear on the part at its seat ({len(seated)} of 8 probes, nearest {seat_err} mm)")
    if s["into"] in ("drive", "idler", "case"):
        if tgt not in sc.servos:
            pr.append(f"it runs into {tgt}, not a servo")
            return res
        T = np.linalg.inv(sc.pose[tgt])
        Pl, dl = T[:3, :3] @ (P + (under + gap) * d) + T[:3, 3], T[:3, :3] @ d
        res["servo_point"] = [round(x, 2) for x in Pl]
        if abs(abs(dl[2]) - 1) > 1e-6:
            pr.append("not parallel to the servo's shaft")
        xy = Pl[:2]
        if s["into"] == "case":
            holes = [(x, y) for x in G.ST["MOUNT_L"] for y in (-G.ST["MOUNT_W"], G.ST["MOUNT_W"])]
            face, lo, hi = -G.HR, 1.8, G.ST["MOUNT_DEPTH"] - 0.4
        else:
            holes = G.pcd_points((0.0, 0.0))
            face = G.ST["HORN_REAL"][1] if s["into"] == "drive" else -G.HI
            if s["into"] == "drive":
                lo, hi = 1.7 + 2 * G.SHIM, G.ST["HORN_T"] + G.ST["HORN_FREE"] - 0.3
            else:
                lo, hi = 1.7, G.ST["IDLER_T"] + G.ST["IDLER_FREE"] - 0.3
        miss = min(np.hypot(xy[0] - a, xy[1] - b) for a, b in holes)
        res["hole_offset_mm"] = round(float(miss), 3)
        if miss > 0.25:
            pr.append(f"its axis misses the servo's holes by {miss:.2f} mm")
        if abs(Pl[2] - face) > 0.3:
            pr.append(f"it meets the servo at z {Pl[2]:.2f}, not on the {s['into']} face ({face})")
        res["allowed_mm"] = [round(lo, 2), round(hi, 2)]
        if not lo - 1e-6 <= e <= hi + 1e-6:
            pr.append(f"thread {e:.2f} mm outside {lo:.2f}..{hi:.2f}")
    else:
        if tgt is None or tgt in sc.servos:
            pr.append(f"it runs into {tgt}, not the printed part it is meant for")
            return res
        tm = sc.tm[tgt]
        o0 = P + (under + gap + 0.05) * d                            # on the axis, just inside the target's hole
        if s["into"] == "insert":                                    # (the insert's 4 mm hole: start past it)
            o0 = P + (under + gap + 4.0) * d
        h = [t for t in hits(tm, o0, d) if t > 1e-6]
        depth = (h[0] + (4.0 if s["into"] == "insert" else 0.05)) if h else 99.0
        other, t_other = first_hit(sc, o0, d)
        free = min(depth, t_other + (4.0 if s["into"] == "insert" else 0.05))
        thread = inside_length(tm, P + THREAD[s["size"]] * u, d, under + gap, L_)
        res["hole_depth_mm"] = round(free, 2)
        res["thread_in_part_mm"] = round(thread, 2)
        if s["into"] == "insert":                                   # an M3 x 4 insert pressed flush with the face
            if min(e, 4.0) < 2.5:
                pr.append(f"only {min(e, 4.0):.2f} mm of thread in the insert")
        else:
            need = 2.0
            if thread < need - 1e-6:
                pr.append(f"only {thread:.2f} mm of thread in {tgt} (wants {need})")
        if e > free - 0.3 + 1e-6:
            pr.append(f"the tip ({e:.2f} mm in) reaches the bottom / something else at {free:.2f} mm")
    return res


def screws(sc: Scene):
    rows = []
    for key, part, _ in sc.comps:
        for i, s in enumerate(G.SCREWS.get(part, [])):
            r = check_screw(sc, key, s)
            r["index"] = i
            rows.append(r)
    heads = []
    for key, part, _ in sc.comps:
        for i, s in enumerate(G.SCREWS.get(part, [])):
            hm = sc.place(G.screw_head(s), key)
            for k in sc.mf:
                v = clash(hm, sc.mf[k])
                if v > CLASH_MM3:
                    heads.append({"part": key, "index": i, "hits": k, "mm3": round(v, 1)})
    return rows, heads


# ------------------------------------------------------------------------------------------------ 4 assembly
# servo states while it is being fitted: (drive horn on, passive horn on, the drive horn's centre screw in)
FULL, NO_SCREW, BARE, NO_PASSIVE = (True, True, True), (True, True, False), (False, False, False), (True, False, True)


def hip_seq(s):
    """The hip of one side, on the robot (build guide steps 1-3)."""
    sg = 1 if s == "L" else -1
    return [
        (f"hip-yaw servo up into the pelvis ({s})", [f"servo_hip_yaw_{s}"], "robot",
         ([f"servo_hip_yaw_{s}"], (0, 0, 1)), {f"servo_hip_yaw_{s}": NO_PASSIVE}),
        (f"yaw ring insert up around the yaw horn ({s})", [f"yaw_ring_{s}"], "robot", ([f"yaw_ring_{s}"], (0, 0, 1)), {}),
        (f"hip-roll servo into the hip-yaw bracket ({s})", [f"hip_yaw_{s}", f"servo_hip_roll_{s}"], f"hipyaw_{s}",
         ([f"servo_hip_roll_{s}"], (-1, 0, 0)), {}),
        (f"hip-yaw bracket onto the yaw horn ({s})", f"hipyaw_{s}", "robot",
         ([f"hip_yaw_{s}", f"servo_hip_roll_{s}"], (0, 0, 1)), {}),
        (f"keeper under the disc's rim ({s})", [f"keeper_{s}"], "robot",
         ([f"keeper_{s}"], (-np.cos(np.radians(30)), -sg * np.sin(np.radians(30)), 0)), {}),
        (f"hip-roll bracket onto the roll servo ({s})", [f"hip_roll_{s}"], "robot", ([f"hip_roll_{s}"], (0, 0, 1)),
         {f"servo_hip_roll_{s}": NO_SCREW}),
        (f"hip-pitch servo into the hip-roll bracket ({s})", [f"servo_hip_pitch_{s}"], "robot",
         ([f"servo_hip_pitch_{s}"], (0, -sg, 0)), {}),
    ]


def lower_leg_seq(s):
    """The lower leg of one side, built on the bench, then onto the hip-pitch servo (build guide steps 4-7)."""
    sg = 1 if s == "L" else -1
    leg = f"leg_{s}"
    return [
        (f"knee servo into the thigh ({s})", [f"thigh_{s}", f"servo_knee_{s}"], leg,
         ([f"servo_knee_{s}"], (-1, 0, 0)), {f"servo_knee_{s}": BARE}),
        (f"ankle-pitch servo up into the shin ({s})", [f"shin_{s}", f"servo_ankle_pitch_{s}"], f"shin_{s}",
         ([f"servo_ankle_pitch_{s}"], (0, 0, 1)), {f"servo_ankle_pitch_{s}": NO_PASSIVE}),
        (f"shin onto the knee servo ({s})", f"shin_{s}", leg, ([f"shin_{s}", f"servo_ankle_pitch_{s}"], (0, 0, 1)),
         {f"servo_knee_{s}": NO_SCREW}),
        (f"ankle-roll servo into the ankle bracket ({s})", [f"ankle_{s}", f"servo_ankle_roll_{s}"], f"ankle_{s}",
         ([f"servo_ankle_roll_{s}"], (0, sg, 0)), {f"servo_ankle_roll_{s}": BARE}),
        (f"foot onto the ankle-roll servo ({s})", [f"foot_{s}"], f"ankle_{s}", ([f"foot_{s}"], (0, 0, 1)),
         {f"servo_ankle_roll_{s}": NO_SCREW}),
        (f"ankle bracket and foot onto the ankle-pitch servo ({s})", f"ankle_{s}", leg,
         ([f"ankle_{s}", f"servo_ankle_roll_{s}", f"foot_{s}"], (0, 0, 1)), {f"servo_ankle_pitch_{s}": NO_SCREW}),
        (f"lower leg onto the hip-pitch servo ({s})", leg, "robot",
         ([f"{p}_{s}" for p in ("thigh", "servo_knee", "shin", "servo_ankle_pitch", "ankle", "servo_ankle_roll", "foot")],
          (0, 0, 1)), {f"servo_hip_pitch_{s}": NO_SCREW}),
    ]


def arm_seq(s):
    sg = 1 if s == "L" else -1
    return [
        (f"shoulder servo into the upper arm ({s})", [f"upper_arm_{s}", f"servo_shoulder_pitch_{s}"], f"arm_{s}",
         ([f"servo_shoulder_pitch_{s}"], (0, sg, 0)), {}),
        (f"elbow servo into the upper arm ({s})", [f"servo_elbow_{s}"], f"arm_{s}", ([f"servo_elbow_{s}"], (0, -sg, 0)), {}),
        (f"blade onto the elbow horn ({s})", [f"blade_{s}"], f"arm_{s}", ([f"blade_{s}"], (0, -sg, 0)), {}),
    ]


def sequence():
    out = [("pelvis", ["pelvis"], "robot", ([], (0, 0, 1)), {})]
    for s in ("L", "R"):
        out += hip_seq(s)
    for s in ("L", "R"):
        out += lower_leg_seq(s)
    out.append(("lower torso onto the pelvis", ["torso"], "robot", (["torso"], (0, 0, -1)), {}))
    for s in ("L", "R"):
        out += arm_seq(s)
    out += [("neck servo onto the chest cap", ["chest_cap", "servo_neck"], "cap", (["servo_neck"], (0, 0, -1)),
             {"servo_neck": NO_PASSIVE})]
    for s, sg in (("L", 1), ("R", -1)):
        out.append((f"arm onto the chest cap's pad ({s})", f"arm_{s}", "cap",
                    ([f"upper_arm_{s}", f"servo_shoulder_pitch_{s}", f"servo_elbow_{s}", f"blade_{s}"], (0, -sg, 0)),
                    {}))
    out += [("chest cap onto the torso", "cap", "robot",
             (["chest_cap", "servo_neck"] + [f"{p}_{s}" for s in "LR" for p in ("upper_arm", "servo_shoulder_pitch",
                                                                                   "servo_elbow", "blade")], (0, 0, -1)), {}),
            ("neck hub onto the neck horn", ["neck_hub"], "robot", (["neck_hub"], (0, 0, -1)), {"servo_neck": NO_PASSIVE}),
            ("head down over the neck hub", ["head"], "robot", (["head"], (0, 0, -1)), {"servo_neck": NO_PASSIVE})]
    return out


def _cyl_along(p0, direction, length, d):
    """Manifold cylinder of diameter d from point p0 along unit direction for length (mm)."""
    z = np.asarray(direction, float)
    x = np.cross(z, [1, 0, 0] if abs(z[0]) < 0.9 else [0, 1, 0])
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    return Manifold.cylinder(length, d / 2, d / 2, 32).transform(np.column_stack([x, y, z, p0]).tolist())


def tool_access(solids, P, d, size):
    """How a screw with its head at P (pointing d) can be driven, against the solids around it (every head is Phillips):
    a screwdriver (60 mm straight along the axis), else a 25 mm PH bit turned by hand or with a small spanner (30 mm
    straight along the axis, and a Ø22 x 8 mm ring of room for the fingers / spanner at 20-28 mm). Returns (tool, free
    length along the axis, blockers of the screwdriver)."""
    kh = (G.M3 if size == "M3" else G.M2)["head"][1]
    top = P - d * (kh + 0.3)
    D = DRIVER[size]

    def free(m):
        return [(k, round(v, 1)) for k, s_ in solids if (v := clash(m, s_)) > CLASH_MM3]
    straight = free(_cyl_along(top, -d, 60.0, D))
    if not straight:
        return "screwdriver", 60.0, []
    lo, hi = 0.0, 60.0                                                  # free length along the axis (bisection)
    for _ in range(8):
        mid = (lo + hi) / 2
        if free(_cyl_along(top, -d, mid, D)):
            hi = mid
        else:
            lo = mid
    if lo >= 30.0 and not free(_cyl_along(top - d * 20.0, -d, 8.0, 22.0)):
        return "PH bit by hand / spanner", round(lo, 1), straight
    return "blocked", round(lo, 1), straight


def assembly(sc: Scene, step_mm=1.0, reach=60.0):
    groups = {}                                                       # assembly -> set of keys
    sweeps, drivers = [], []
    screw_list = [(k, p, i, s) for k, p, _ in sc.comps for i, s in enumerate(G.SCREWS.get(p, []))]
    targets = {(k, i): check_screw(sc, k, s)["target"] for k, p, i, s in screw_list}
    done = set()
    variant_cache = {}

    def solid(k, var):
        if var is None or k not in sc.servos:
            return sc.mf[k]
        if var not in variant_cache:
            variant_cache[var] = build(G.servo_st(*var))
        return variant_cache[var].transform(sc.pose[k][:3, :].tolist())

    for name, add, into, (moving, direction), variants in sequence():
        keys = groups.pop(add) if isinstance(add, str) else set(add)
        target = groups.setdefault(into, set())
        dvec = np.asarray(direction, float)
        dvec /= np.linalg.norm(dvec)
        mov = [(k, solid(k, variants.get(k))) for k in moving]
        sta = [(k, solid(k, variants.get(k))) for k in sorted(target | keys) if k not in moving]
        worst = (0.0, None, None)
        for off in np.arange(reach, -0.01, -step_mm):
            t = (-dvec * off).tolist()
            for km, m in mov:
                mm = m.translate(t)
                for ks, s_ in sta:
                    v = clash(mm, s_)
                    if v > worst[0]:
                        worst = (v, (km, ks), round(float(off), 1))
        sweeps.append({"step": name, "moving": moving, "direction": [round(float(x), 3) for x in dvec],
                       "worst_mm3": round(worst[0], 1), "pair": worst[1], "at_mm": worst[2],
                       "ok": worst[0] <= CLASH_MM3})
        target |= keys
        # screws that can be driven now: their part and what they screw into are together for the first time
        here = [(k, solid(k, None)) for k in sorted(target)]
        for k, p, i, s in screw_list:
            if (k, i) in done or k not in target or targets[(k, i)] not in target:
                continue
            done.add((k, i))
            P, d, _, _ = screw_world(sc, k, s)
            tool, free_len, straight = tool_access(here, P, d, s["size"])
            drivers.append({"step": name, "part": k, "index": i, "size": s["size"], "length": s["length"],
                            "into": s["into"], "note": s["note"], "tool": tool, "free_along_axis_mm": free_len,
                            "straight_driver_blocked_by": straight, "ok": tool != "blocked"})
    left = [(k, i) for k, p, i, s in screw_list if (k, i) not in done]
    return sweeps, drivers, left


def check_target(sc: Scene, key, s):
    return check_screw(sc, key, s)["target"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    sc = Scene()
    print(f"{len(sc.parts)} printed parts, {len(sc.servos)} servos", flush=True)
    res = {"clash_threshold_mm3": CLASH_MM3}
    multi = {n: len(build(pr).decompose()) for n, (pr, _, _) in G.PARTS.items()}
    res["parts_in_pieces"] = {n: k for n, k in multi.items() if k != 1}
    print(f"0. every printed part one solid piece: {len(multi) - len(res['parts_in_pieces'])}/{len(multi)}"
          + (f"  NOT: {res['parts_in_pieces']}" if res["parts_in_pieces"] else ""), flush=True)
    rows, res["so_arm_seating"] = servo_and_cables(sc)
    res["servo_and_cables"] = rows
    print("   SO-ARM100 mesh seating shifts:", res["so_arm_seating"])
    print(f"1-2. real servo and cables vs parts: {len(rows)} clashes", flush=True)
    for r in rows:
        print("    ", r)
    sr, heads = screws(sc)
    bad = [r for r in sr if r["problems"]]
    res["screws"] = sr
    res["screw_heads"] = heads
    print(f"3. screws: {len(sr)} checked, {len(bad)} with problems, {len(heads)} head clashes", flush=True)
    for r in bad:
        print(f"     {r['part']}#{r['index']} {r['size']}x{r['length']:g} into {r['into']} ({r['target']}): "
              f"under {r['under_head_mm']} gap {r['gap_mm']} thread {r['engagement_mm']}  {r['problems']}")
    for h in heads:
        print("     head", h)
    ok = not rows and not bad and not heads and not res["parts_in_pieces"]
    if not a.quick:
        sw, dr, left = assembly(sc)
        res["assembly_sweeps"], res["screwdriver_access"], res["screws_never_reached"] = sw, dr, left
        bs = [x for x in sw if not x["ok"]]
        bd = [x for x in dr if not x["ok"]]
        off = [x for x in dr if x["tool"] != "screwdriver"]
        print(f"4. assembly: {len(sw)} steps, {len(bs)} blocked; screwdriver: {len(dr)} screws, {len(bd)} blocked, "
              f"{len(off)} need a PH bit, {len(left)} never reachable", flush=True)
        for x in off:
            if x["ok"]:
                print(f"     PH bit: {x['part']}#{x['index']} {x['size']}x{x['length']:g} into {x['into']} "
                      f"({x['free_along_axis_mm']} mm free along the axis) at '{x['step']}'")
        for x in bs:
            print("     slide", x)
        for x in bd:
            print("     driver", x)
        ok &= not bs and not bd and not left
    res["seconds"] = round(time.time() - t0, 1)
    res["pass"] = ok
    OUT.write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    print(f"fit check: {'PASS' if ok else 'FAIL'} ({res['seconds']} s) -> {OUT.relative_to(ROOT)}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
