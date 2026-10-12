"""JXC-5010: a 3D-printable cycloidal actuator built around a 5010 drone motor.

What this script does
  1. Compares motor + driver options (torque at the joint, speed, current) - the SimpleFOCmini's 2.5 A is the bottleneck.
  2. Designs a single-stage, dual-disc cycloidal reducer (20:1) and checks it: no undercut, pin and roller loads,
     contact pressure on printed discs, pin bending.
  3. Exports print/cut files: cycloid disc (DXF + STL), ring-pin housing, output carrier, eccentric cam, motor adapter.

All performance numbers are CALCULATED from datasheet-level inputs (KV, current limits) and must be confirmed on the bench.
Usage: python actuators/diy_cycloid/cycloid_actuator.py   -> results/*.json, cad/*.stl|dxf, figures/*.png
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT, CAD, FIG = HERE / "results", HERE / "cad", HERE / "figures"

# ----------------------------------------------------------------------------------------------------------------------
# 1. motors and drivers (prices INR incl. GST; see research/raw/india_robu_browser_sourcing_raw.md, india_electronics_compute_raw.md)
MOTORS = {
    "5010 360KV (Robu, your pick)": dict(kv=360, price=2239, mass_g=112, i_peak=20, i_cont=10, note="12N14P, Φ50×26, 4 mm shaft"),
    "Tarot 5010 130KV (Robu)": dict(kv=130, price=4779, mass_g=150, i_peak=15, i_cont=7, note="28 poles, stator 50×10, upgrade"),
}
DRIVERS = {
    "SimpleFOCmini (your pick)": dict(i_peak=2.5, i_cont=2.0, v_max=30, price=729, note="DRV8313; needs an MCU; no CAN"),
    "ST B-G431B-ESC1": dict(i_peak=40, i_cont=20, v_max=25.2, price=2800, note="STM32G431 on board, CAN, SimpleFOC + Berkeley 'Recoil' firmware; ~US$19 (ST eStore), import"),
    "Flipsky ODESC V4.2": dict(i_peak=50, i_cont=25, v_max=24, price=7350, note="ODrive 3.6 clone, Amazon.in"),
}
V_BUS = 24.0                 # 6S LiPo (22.2 V nominal) or a 24 V bench supply
ETA = 0.85                   # printed cycloid with greased steel ring pins + rolling output pins (BHL measured ~0.90)


def kt_from_kv(kv: float) -> float:
    """Torque constant (N.m/A) estimated from KV; ±20 % - measure it (Section 'Testing')."""
    return 8.27 / kv


# ----------------------------------------------------------------------------------------------------------------------
# 2. cycloidal reducer geometry (mm)
@dataclass
class Cycloid:
    n_pins: int = 21           # ring pins -> 20 lobes -> 20:1
    r_pin_circle: float = 32.0
    d_pin: float = 4.0         # Ø4 hardened steel dowels (DIN 6325), greased
    ecc: float = 1.0           # eccentricity
    disc_t: float = 7.0        # each disc
    clearance: float = 0.10    # profile offset inwards (backlash vs FDM accuracy)
    n_out: int = 6             # output pins
    r_out: float = 21.0        # output-pin circle
    d_out_pin: float = 4.0     # Ø4 dowel
    d_out_roller: float = 7.0  # MR74ZZ (4×7×2.5): two stacked per pin per disc (5 mm contact width)
    roller_w: float = 5.0
    ecc_bearing: tuple = (17.0, 26.0, 5.0)   # 6803 (ID, OD, width) on the eccentric cam, one per disc
    out_bearing: tuple = (50.0, 65.0, 7.0)   # 6810 output bearing
    housing_od: float = 82.0

    @property
    def ratio(self) -> int:
        return self.n_pins - 1

    def profile(self, n=3600):
        """Cycloid disc outline (closed polyline), standard parametric form with pin-radius offset."""
        R, Rr, N, E = self.r_pin_circle, self.d_pin / 2 + self.clearance, self.n_pins, self.ecc
        t = np.linspace(0, 2 * np.pi, n, endpoint=False)
        psi = np.arctan2(np.sin((1 - N) * t), R / (E * N) - np.cos((1 - N) * t))
        x = R * np.cos(t) - Rr * np.cos(t + psi) - E * np.cos(N * t)
        y = -R * np.sin(t) + Rr * np.sin(t + psi) + E * np.sin(N * t)
        return np.column_stack([x, y])


def check_cycloid(c: Cycloid, torque_out: float):
    """Geometry and load checks for a dual-disc design (each disc carries ~55 % of the torque)."""
    from shapely.geometry import Polygon
    prof = c.profile()
    poly = Polygon(prof)
    lam = c.ecc * c.n_pins / c.r_pin_circle                         # short-amplitude coefficient, must be < 1
    # local radius of curvature of the profile (no undercut if the minimum convex radius > 0 and the polygon is simple)
    d1 = np.gradient(prof, axis=0); d2 = np.gradient(d1, axis=0)
    curv = (d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0]) / np.power((d1 ** 2).sum(1), 1.5)
    rho = 1 / np.where(np.abs(curv) < 1e-9, 1e-9, curv)
    r_min_conc = float(np.min(np.abs(rho[rho < 0]))) if np.any(rho < 0) else float("inf")
    rad = np.hypot(prof[:, 0], prof[:, 1])
    t_disc = 0.55 * torque_out                                       # dual discs, unequal sharing allowance
    # max ring-pin force  F = 4 T_c / (K1 Zc rp), K1 = e Zp / rp  ->  4 T_c / (e Zp Zc)
    f_pin = 4 * t_disc / (c.ecc / 1000 * c.n_pins * (c.n_pins - 1))
    # max output-pin force  F = 4 T_c / (Zw Rw)
    f_out = 4 * t_disc / (c.n_out * c.r_out / 1000)
    # Hertz line contact, steel pin on printed disc (pin-on-flat, conservative); E* for PLA/PETG ~ 3.5-4 GPa, PA-CF ~ 6 GPa
    def hertz(F, r_mm, b_mm, e_star):
        return math.sqrt(F * e_star / (math.pi * b_mm / 1000 * r_mm / 1000)) / 1e6
    p_pin = {m: hertz(f_pin, c.d_pin / 2, c.disc_t, e) for m, e in (("PLA/PETG", 4.0e9), ("PA-CF", 6.0e9))}
    # roller (convex) inside the disc hole (concave): R_eff = r1 r2 / (r2 - r1)
    r1, r2 = c.d_out_roller / 2, c.d_out_roller / 2 + c.ecc
    p_out = {m: hertz(f_out, r1 * r2 / (r2 - r1), c.roller_w, e) for m, e in (("PLA/PETG", 4.0e9), ("PA-CF", 6.0e9))}
    # output pin bending: cantilever from the carrier through both discs, load at mid-disc 2 (worst)
    arm = c.disc_t * 1.5 + 1.0
    sigma_out_pin = 32 * f_out * arm / 1000 / (math.pi * (c.d_out_pin / 1000) ** 3) / 1e6
    hole_d = c.d_out_roller + 2 * c.ecc
    wall_in = c.r_out - hole_d / 2 - c.ecc_bearing[1] / 2
    wall_out = rad.min() - (c.r_out + hole_d / 2)
    return {
        "ratio": c.ratio, "lambda_short_amplitude": lam, "profile_simple_no_self_intersection": bool(poly.is_valid),
        "min_concave_radius_mm": r_min_conc, "disc_r_max_mm": float(rad.max()), "disc_r_min_mm": float(rad.min()),
        "output_hole_d_mm": hole_d, "wall_hole_to_bore_mm": wall_in, "wall_hole_to_root_mm": wall_out,
        "pin_pitch_mm": 2 * math.pi * c.r_pin_circle / c.n_pins,
        "torque_per_disc_Nm": t_disc, "ring_pin_force_max_N": f_pin, "output_pin_force_max_N": f_out,
        "contact_pressure_ring_pin_MPa": p_pin, "contact_pressure_output_roller_MPa": p_out,
        "output_pin_bending_MPa": sigma_out_pin,
    }


# ----------------------------------------------------------------------------------------------------------------------
# 3. CAD export (2.5-D parts: extrusions + booleans)
def export_cad(c: Cycloid, motor_bolt_pcd=25.0, motor_bolt_d=3.2, motor_shaft_d=4.0, prop_pcd=16.0):
    import trimesh
    import ezdxf
    from shapely.geometry import Polygon, Point
    from shapely.affinity import translate
    from shapely.ops import unary_union

    CAD.mkdir(exist_ok=True)

    def circle(x, y, d):
        return Point(x, y).buffer(d / 2, resolution=64)

    def ring_of(n, r, d, phase=0.0):
        return [circle(r * math.cos(phase + 2 * math.pi * k / n), r * math.sin(phase + 2 * math.pi * k / n), d) for k in range(n)]

    def extrude(poly, h, z0=0.0):
        m = trimesh.creation.extrude_polygon(poly, h)
        m.apply_translation([0, 0, z0])
        return m

    def save(name, mesh, poly2d=None):
        mesh.export(CAD / f"{name}.stl")
        if poly2d is not None:
            doc = ezdxf.new(); msp = doc.modelspace()
            geoms = [poly2d] if poly2d.geom_type == "Polygon" else list(poly2d.geoms)
            for g in geoms:
                for ring in [g.exterior, *g.interiors]:
                    msp.add_lwpolyline(list(ring.coords), close=True)
            doc.saveas(CAD / f"{name}.dxf")

    # (a) cycloid disc - print TWO; assemble the second rotated by 180 deg on the opposite eccentric
    hole_d = c.d_out_roller + 2 * c.ecc + 0.2
    disc = Polygon(c.profile()).difference(unary_union([circle(0, 0, c.ecc_bearing[1] - 0.05)] + ring_of(c.n_out, c.r_out, hole_d)))
    save("cycloid_disc_x2", extrude(disc, c.disc_t), disc)

    # (b) ring-pin housing, bottom to top: floor lip (keeps pins/discs in) | pin zone (pins half-exposed in grooves)
    #     | carrier-plate zone (Ø60, gives the bearing a shoulder) | output-bearing seat (6810)
    ob_id, ob_od, ob_w = c.out_bearing
    pin_len_zone = 2 * c.disc_t + 1.5
    outer = circle(0, 0, c.housing_od)
    bolts = ring_of(6, c.housing_od / 2 - 4.0, 3.4, phase=math.pi / 6)
    pin_holes = ring_of(c.n_pins, c.r_pin_circle, c.d_pin - 0.05)      # press fit for Ø4 dowels (tune ±0.05 on a test print)
    # Ø4×20 dowels (the length sold in India) need 20 mm: holes run through floor (2) + pin zone (15.5) + plate zone (3.5)
    sec_pins = outer.difference(unary_union([circle(0, 0, 2 * c.r_pin_circle)] + pin_holes + bolts))
    h_total = 2.0 + pin_len_zone + 3.5 + ob_w
    eps = 0.01
    housing = extrude(outer.difference(unary_union(pin_holes + bolts)), h_total)
    for d_bore, z0, z1 in ((2 * c.r_pin_circle - 6, 0.0, 2.0), (2 * c.r_pin_circle, 2.0, 2.0 + pin_len_zone),
                           (60.0, 2.0 + pin_len_zone, 5.5 + pin_len_zone), (ob_od + 0.05, 5.5 + pin_len_zone, h_total)):
        cut = extrude(circle(0, 0, d_bore), (z1 - z0) + 2 * eps, z0 - eps)
        housing = trimesh.boolean.difference([housing, cut])
    save("ring_pin_housing", housing, sec_pins)
    # motor spacer ring (motor sits inside it, bell must not touch: Ø60 clears a Ø50-56 bell) and output retainer ring
    spacer = outer.difference(unary_union([circle(0, 0, 60.0)] + bolts))
    save("motor_spacer_ring", extrude(spacer, MOTOR_H + 3.0), spacer)
    retainer = outer.difference(unary_union([circle(0, 0, 56.0)] + bolts))
    save("output_retainer_ring", extrude(retainer, 3.0), retainer)

    # (c) output carrier: plate with 6 press-fit pin holes + hub that sits in the 6810 bearing + 4×M3 load holes
    plate = circle(0, 0, 2 * c.r_pin_circle - 6.5).difference(unary_union(ring_of(c.n_out, c.r_out, c.d_out_pin - 0.05) + [circle(0, 0, 8)]))
    hub = circle(0, 0, ob_id - 0.02).difference(unary_union(ring_of(c.n_out, c.r_out, c.d_out_pin - 0.05) + ring_of(4, 12, 3.4) + [circle(0, 0, 8)]))
    carrier = trimesh.boolean.union([extrude(plate, 3.0, 0), extrude(hub, ob_w + 3.0, 3.0)])
    save("output_carrier", carrier, plate)

    # (d) eccentric cam: bolt flange (to the rotor bell's prop-mount holes - MEASURE) + two Ø17 journals offset ±e,
    #     180 deg apart, each as long as a disc; Ø4 centre bore locates on the motor shaft stub
    j_d = c.ecc_bearing[0] - 0.02
    bore = circle(0, 0, motor_shaft_d + 0.1)
    flange = circle(0, 0, 26.0).difference(unary_union([bore] + ring_of(4, prop_pcd / 2, 3.2, math.pi / 4)))
    j1 = translate(circle(0, 0, j_d), c.ecc, 0).difference(bore)
    j2 = translate(circle(0, 0, j_d), -c.ecc, 0).difference(bore)
    collar = circle(0, 0, 12.0).difference(bore)
    cam = trimesh.boolean.union([extrude(flange, 3.0, 0), extrude(collar, 2.0, 3.0), extrude(j1, c.disc_t, 5.0),
                                 extrude(collar, 1.5, 5.0 + c.disc_t), extrude(j2, c.disc_t, 6.5 + c.disc_t)])
    save("eccentric_cam_MEASURE_FIRST", cam, flange)

    # (e) motor adapter plate: motor base bolts (MEASURE YOUR MOTOR FIRST) + 6 housing bolts + shaft clearance
    adapter = outer.difference(unary_union([circle(0, 0, 14.0)] + ring_of(4, motor_bolt_pcd / 2, motor_bolt_d, math.pi / 4) + bolts))
    save("motor_adapter_MEASURE_FIRST", extrude(adapter, 4.0), adapter)
    return {"files": sorted(p.name for p in CAD.iterdir()), "motor_bolt_pcd_assumed_mm": motor_bolt_pcd, "prop_pcd_assumed_mm": prop_pcd}


# ----------------------------------------------------------------------------------------------------------------------
def render_assembly(c: Cycloid):
    """To-scale section of the assembled stack (mirror image about the axis; eccentric offsets drawn on the discs).
    Heights (mm): adapter 0-4, motor 4-30, cam on the bell 30-50.5, housing 33-61, discs 35-42 / 43.5-50.5,
    carrier 50.75-63.75, 6810 bearing 54-61, retainer 61-64."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Patch
    plt.rcParams.update({"font.family": "serif", "font.serif": ["STIXGeneral", "DejaVu Serif"], "font.size": 8})
    R_H = c.housing_od / 2
    z_d1, z_d2 = 35.0, 35.0 + c.disc_t + 1.5
    parts = [  # label, colour, [(r0, r1, z0, z1, side)] side: 0 both, +1 right only, -1 left only
        ("motor adapter / spacer / retainer (printed)", "#b0bec5", [(7, R_H, 0, 4, 0), (30, R_H, 4, 33, 0), (28, R_H, 61, 64, 0)]),
        ("5010 motor (stator + bell)", "#b0413e", [(0, 25, 4, 4 + MOTOR_H, 0)]),
        ("ring-pin housing (printed)", "#8fa7c0", [(29, R_H, 33, 35, 0), (c.r_pin_circle, R_H, 35, 50.5, 0), (30, R_H, 50.5, 54, 0), (c.out_bearing[1] / 2, R_H, 54, 61, 0)]),
        ("Ø4 ring pins ×21 (steel)", "#455a64", [(c.r_pin_circle - 2, c.r_pin_circle + 2, 35, 50.5, 0)]),
        ("eccentric cam (printed)", "#37474f", [(2, 13, 30, 33, 0), (2, 6, 33, 35, 0), (2, c.ecc_bearing[0] / 2 + c.ecc, z_d1, z_d1 + c.disc_t, 1),
                                                (2, c.ecc_bearing[0] / 2 - c.ecc, z_d1, z_d1 + c.disc_t, -1), (2, 6, 42, 43.5, 0),
                                                (2, c.ecc_bearing[0] / 2 + c.ecc, z_d2, z_d2 + c.disc_t, -1), (2, c.ecc_bearing[0] / 2 - c.ecc, z_d2, z_d2 + c.disc_t, 1)]),
        ("bearings: 6803 ×2 (eccentric), 6810 (output)", "#26a69a", [(c.ecc_bearing[0] / 2 + c.ecc, c.ecc_bearing[1] / 2 + c.ecc, z_d1, z_d1 + 5, 1),
                                                (c.ecc_bearing[0] / 2 - c.ecc, c.ecc_bearing[1] / 2 - c.ecc, z_d1, z_d1 + 5, -1),
                                                (c.ecc_bearing[0] / 2 + c.ecc, c.ecc_bearing[1] / 2 + c.ecc, z_d2, z_d2 + 5, -1),
                                                (c.ecc_bearing[0] / 2 - c.ecc, c.ecc_bearing[1] / 2 - c.ecc, z_d2, z_d2 + 5, 1),
                                                (c.out_bearing[0] / 2, c.out_bearing[1] / 2, 54, 61, 0)]),
        ("cycloid discs ×2 (printed)", "#c9a227", [(c.ecc_bearing[1] / 2 + c.ecc, 30.9 + c.ecc, z_d1, z_d1 + c.disc_t, 1), (c.ecc_bearing[1] / 2 - c.ecc, 30.9 - c.ecc, z_d1, z_d1 + c.disc_t, -1),
                                                   (c.ecc_bearing[1] / 2 + c.ecc, 30.9 + c.ecc, z_d2, z_d2 + c.disc_t, -1), (c.ecc_bearing[1] / 2 - c.ecc, 30.9 - c.ecc, z_d2, z_d2 + c.disc_t, 1)]),
        ("output carrier (printed)", "#5d7d9a", [(4, 28.75, 50.75, 53.75, 0), (4, c.out_bearing[0] / 2, 53.75, 63.75, 0)]),
        ("Ø4 output pins ×6 + MR74ZZ rollers", "#2e7d32", [(c.r_out - 2, c.r_out + 2, 35, 63.75, 0), (c.r_out - 3.5, c.r_out + 3.5, z_d1 + 1, z_d1 + 6, 0), (c.r_out - 3.5, c.r_out + 3.5, z_d2 + 1, z_d2 + 6, 0)]),
    ]
    fig, ax = plt.subplots(figsize=(3.6, 4.6)); ax.set_aspect("equal"); ax.axis("off")
    for lab, col, rects in parts:
        for r0, r1, z0, z1, side in rects:
            for sg in ((1, -1) if side == 0 else (side,)):
                x0, x1 = sorted((sg * r0, sg * r1))
                ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=col, ec="#263238", lw=0.35))
    for sg in (1, -1):
        ax.plot([sg * (R_H - 4)] * 2, [0, 64], color="#263238", lw=0.6, ls="--")
    ax.plot([0, 0], [-2, 68], color="#263238", lw=0.5, ls="-.")
    ax.annotate("", xy=(-R_H, -4), xytext=(R_H, -4), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text(0, -8, f"Ø{c.housing_od:.0f} mm", ha="center", fontsize=7)
    ax.annotate("", xy=(R_H + 3, 0), xytext=(R_H + 3, 64), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text(R_H + 5, 32, "64 mm", rotation=90, va="center", fontsize=7)
    ax.text(0, 66, "output", ha="center", fontsize=7)
    ax.legend(handles=[Patch(fc=col, ec="#263238", lw=0.4, label=lab) for lab, col, _ in parts], loc="upper center",
              bbox_to_anchor=(0.5, -0.02), ncol=1, fontsize=6.5, frameon=False)
    ax.set_xlim(-R_H - 2, R_H + 9); ax.set_ylim(-10, 70)
    fig.savefig(FIG / "assembly_section.png", dpi=220, bbox_inches="tight"); plt.close(fig)


def render_parts():
    """Shaded previews of the printed parts (figures/printed_parts.png)."""
    import trimesh
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    names = ["cycloid_disc_x2", "ring_pin_housing", "output_carrier", "eccentric_cam_MEASURE_FIRST", "motor_adapter_MEASURE_FIRST"]
    plt.rcParams.update({"font.family": "serif", "font.serif": ["STIXGeneral", "DejaVu Serif"], "font.size": 8})
    fig = plt.figure(figsize=(10, 2.6))
    light = np.array([0.4, -0.4, 0.8]); light /= np.linalg.norm(light)
    for i, n in enumerate(names):
        m = trimesh.load(CAD / f"{n}.stl")
        ax = fig.add_subplot(1, len(names), i + 1, projection="3d")
        base = np.array(matplotlib.colors.to_rgb("#c9a227" if "disc" in n else "#8fa7c0"))
        shade = np.clip(m.face_normals @ light, 0.15, 1.0)
        ax.add_collection3d(Poly3DCollection(m.triangles, facecolor=np.outer(shade, base), edgecolor="none"))
        b = m.bounds; cen = b.mean(0); r = (b[1] - b[0]).max() / 2
        ax.set_xlim(cen[0] - r, cen[0] + r); ax.set_ylim(cen[1] - r, cen[1] + r); ax.set_zlim(cen[2] - r, cen[2] + r)
        ax.view_init(elev=35, azim=-60); ax.set_axis_off()
        ax.set_title(n.replace("_MEASURE_FIRST", "*").replace("_x2", " (×2)").replace("_", " "), fontsize=8)
    fig.tight_layout(); fig.savefig(FIG / "printed_parts.png", dpi=200); plt.close(fig)


def options_table(c: Cycloid):
    rows = []
    for mname, m in MOTORS.items():
        for dname, d in DRIVERS.items():
            kt = kt_from_kv(m["kv"])
            i_pk = min(m["i_peak"], d["i_peak"]); i_c = min(m["i_cont"], d["i_cont"])
            v = min(V_BUS, d["v_max"])
            rows.append({"motor": mname, "driver": dname, "kt": kt, "i_peak": i_pk, "i_cont": i_c,
                         "peak_Nm_motor_limited": kt * i_pk * c.ratio * ETA, "cont_Nm": kt * i_c * c.ratio * ETA,
                         "noload_rad_s": m["kv"] * v * 2 * math.pi / 60 / c.ratio, "price_motor_driver": m["price"] + d["price"]})
    return rows


def plots(c: Cycloid, rows, checks):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "serif", "font.serif": ["STIXGeneral", "DejaVu Serif"], "mathtext.fontset": "stix",
                         "font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False})
    FIG.mkdir(exist_ok=True)
    # disc + pins drawing
    fig, ax = plt.subplots(figsize=(3.6, 3.6)); ax.set_aspect("equal"); ax.axis("off")
    p = c.profile()
    th = np.linspace(0, 2 * np.pi, 200)
    for sgn, col, lab in ((1, "#1f2a44", "disc 1"), (-1, "#c0392b", "disc 2 (180°)")):
        ax.plot(p[:, 0] + sgn * c.ecc, p[:, 1], color=col, lw=1.0, label=lab)
        ax.plot(c.ecc_bearing[1] / 2 * np.cos(th) + sgn * c.ecc, c.ecc_bearing[1] / 2 * np.sin(th), color=col, lw=0.7)
        hd = c.d_out_roller + 2 * c.ecc
        for k in range(c.n_out):
            a = 2 * np.pi * k / c.n_out
            ax.plot(c.r_out * np.cos(a) + sgn * c.ecc + hd / 2 * np.cos(th), c.r_out * np.sin(a) + hd / 2 * np.sin(th), color=col, lw=0.6)
    for k in range(c.n_pins):
        a = 2 * np.pi * k / c.n_pins
        ax.add_patch(plt.Circle((c.r_pin_circle * np.cos(a), c.r_pin_circle * np.sin(a)), c.d_pin / 2, color="#7f8c8d"))
    for k in range(c.n_out):
        a = 2 * np.pi * k / c.n_out
        ax.add_patch(plt.Circle((c.r_out * np.cos(a), c.r_out * np.sin(a)), c.d_out_roller / 2, fc="none", ec="#2e7d32", lw=0.8))
    ax.add_patch(plt.Circle((0, 0), c.housing_od / 2, fc="none", ec="#b0bec5", lw=1.2))
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.06), ncol=2, fontsize=7, frameon=False)
    ax.set_title(f"{c.ratio}:1 dual-disc cycloid, {c.n_pins} pins on R{c.r_pin_circle:.0f}, e = {c.ecc} mm", fontsize=8)
    fig.tight_layout(); fig.savefig(FIG / "cycloid_layout.png", dpi=220); plt.close(fig)

    # torque-speed lines for the main options
    fig, ax = plt.subplots(figsize=(3.6, 2.8))
    sel = [("5010 360KV (Robu, your pick)", "SimpleFOCmini (your pick)", "#b0413e", "5010 360KV + SimpleFOCmini"),
           ("5010 360KV (Robu, your pick)", "ST B-G431B-ESC1", "#1f2a44", "5010 360KV + B-G431B-ESC1"),
           ("Tarot 5010 130KV (Robu)", "ST B-G431B-ESC1", "#2e7d32", "Tarot 5010 130KV + B-G431B-ESC1")]
    for m, d, col, lab in sel:
        r = next(x for x in rows if x["motor"] == m and x["driver"] == d)
        tp = min(r["peak_Nm_motor_limited"], GEAR_LIMIT_NM)
        w0 = r["noload_rad_s"]
        ax.plot([0, 0.6 * w0, w0], [tp, tp, 0], color=col, lw=1.6, label=lab)
        ax.plot([0, w0], [min(r["cont_Nm"], GEAR_CONT_NM)] * 2, color=col, lw=0.8, ls="--")
    ax.axhline(GEAR_LIMIT_NM, color="#7f8c8d", ls=":", lw=1.0)
    ax.text(1, GEAR_LIMIT_NM + 0.3, "printed-gear peak limit", fontsize=6.5, color="#555")
    ax.axhline(GEAR_CONT_NM, color="#7f8c8d", ls=":", lw=0.8); ax.text(30, GEAR_CONT_NM + 0.3, "printed-gear continuous limit", fontsize=6.5, color="#555")
    ax.set_xlabel("output speed [rad/s]"); ax.set_ylabel("output torque [N·m]"); ax.set_ylim(0, 18); ax.grid(alpha=0.25)
    ax.legend(fontsize=6.5, frameon=False, loc="upper right")
    fig.tight_layout(); fig.savefig(FIG / "torque_options.png", dpi=220); plt.close(fig)


GEAR_LIMIT_NM = 10.0   # peak output torque at which ring-pin contact pressure on PLA/PETG reaches ≈ 70 MPa (see checks)
MOTOR_H = 26.0         # generic 5010: Φ50 × 26 mm (Tarot 5010: Φ55.6 × 27) - measure yours; shim to align
GEAR_CONT_NM = 4.0     # continuous: keep contact pressure ≲ 45 MPa for long life in printed parts


def main():
    OUT.mkdir(exist_ok=True)
    c = Cycloid()
    rows = options_table(c)
    checks = {T: check_cycloid(c, T) for T in (4.0, 8.0, 10.0)}
    cad = export_cad(c)
    plots(c, rows, checks)
    render_assembly(c)
    render_parts()
    res = {"cycloid": asdict(c), "ratio": c.ratio, "v_bus": V_BUS, "eta": ETA, "gear_limit_Nm": GEAR_LIMIT_NM,
           "gear_cont_Nm": GEAR_CONT_NM, "options": rows, "checks": checks, "cad": cad}
    (OUT / "jxc5010.json").write_text(json.dumps(res, indent=2, default=float))
    for r in rows:
        print(f"{r['motor']:30s} {r['driver']:28s} Kt {r['kt']:.3f}  peak {r['peak_Nm_motor_limited']:5.1f}  cont {r['cont_Nm']:4.1f}  "
              f"w0 {r['noload_rad_s']:5.1f}  INR {r['price_motor_driver']}")
    for T, ck in checks.items():
        print(T, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in ck.items()})
    print(cad)


if __name__ == "__main__":
    main()
