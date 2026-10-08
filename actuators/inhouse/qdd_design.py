"""First-pass design of the in-house JXA quasi-direct-drive (QDD) actuator family.

Three classes, sized against JX1's own torque analysis and against full-size humanoids:
  JXA-40   ~ RobStride RS06 class (ankle, hip yaw, waist, shoulders of a 1.2 m robot; arms of a 1.7 m robot)
  JXA-120  ~ RobStride RS04 class (JX1 hip pitch and knee; hip roll/yaw and ankles of a 1.7 m robot)
  JXA-360  ~ Unitree H1 M107 class (knee and hip pitch of a 1.7-1.8 m, 50-70 kg robot)

Each actuator = outer-rotor surface-PM motor with tooth-concentrated windings (the kind you can wind by hand)
+ single-stage planetary (sun in, ring fixed, carrier out) + dual magnetic encoders + 48 V FOC driver on the back.

Model (all results CALCULATED; analytic, expect +/-15-30 % until a prototype is measured):
  magnet circuit -> air-gap flux density -> flux linkage -> torque constant Kt and back-EMF Ke
  slot geometry -> copper fill, phase resistance, copper loss, motor constant Km
  tooth-coil + slot-leakage inductance -> torque-speed envelope at 48 V (SVPWM, Id = 0)
  lumped thermal resistance -> continuous torque
  Lewis bending + Hertz contact -> planetary gear safety factors
  part volumes -> mass and material quantities (input to the cost model in cost_model.py)
Saturation at peak current is calibrated to RobStride RS04's datasheet (120 N.m at 90 Apk vs 40 N.m at 27 Apk).

Usage: python actuators/inhouse/qdd_design.py   -> results/design.json + figures/*.png
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
FIG = HERE / "figures"
MU0 = 4e-7 * math.pi
RHO_CU20 = 1.724e-8      # ohm.m, annealed copper at 20 C
ALPHA_CU = 0.00393       # 1/K
VDC = 48.0               # JX1 13S battery, nominal

# --------------------------------------------------------------------------------------------------------------------
# materials (VERIFIED datasheet-typical values; grades available in India or by import)
MAGNET = {"grade": "N42SH", "Br20": 1.29, "tc_Br": -0.0012, "mu_r": 1.05, "density": 7500, "Tmax_C": 150}
STEEL_LAM = {"grade": "M270-35A / 35CS250 CRNO, 0.35 mm", "density": 7650, "stack_factor": 0.95,
             "P_W_per_kg_1T_400Hz": 17.0, "B_tooth_max": 1.75, "B_yoke_max": 1.55}
GEAR_STEEL = {"grade": "EN353 (15NiCr1Mo12) carburised, case 58-62 HRC", "sigma_F_lim": 430e6, "sigma_F_static": 1000e6,
              "sigma_H_lim": 1400e6, "density": 7850}


@dataclass
class ActuatorSpec:
    name: str
    role: str
    target_peak_Nm: float
    target_cont_Nm: float
    target_noload_rad_s: float
    benchmark: str
    # motor geometry
    slots: int
    poles: int
    stator_od_mm: float
    stack_mm: float
    airgap_mm: float
    magnet_mm: float
    pole_arc: float           # magnet arc / pole pitch
    tooth_tip_mm: float
    slot_open_mm: float
    slot_depth_mm: float
    # gearbox
    z_sun: int
    z_planet: int
    z_ring: int
    n_planets: int
    module_mm: float
    face_mm: float
    # thermal / driver
    rth_K_per_W: float        # winding -> ambient, mounted on an aluminium limb (ESTIMATED)
    gear_eff: float = 0.95
    r_ext_ohm: float = 0.006  # MOSFET + cable + connector, per phase
    fill_target: float = 0.42 # bare-copper slot fill reachable by careful hand / needle winding
    max_strands: int = 6
    notes: list = field(default_factory=list)


SPECS = [
    ActuatorSpec(
        name="JXA-40", role="ankle, hip yaw, waist, shoulder (1.2 m robot); arms (1.7 m robot)",
        target_peak_Nm=40, target_cont_Nm=12, target_noload_rad_s=40, benchmark="RobStride RS06 (36/11 N.m, 621 g, 88 mm)",
        slots=24, poles=28, stator_od_mm=72, stack_mm=14, airgap_mm=0.5, magnet_mm=2.5, pole_arc=0.85,
        tooth_tip_mm=0.9, slot_open_mm=2.0, slot_depth_mm=11.0,
        z_sun=12, z_planet=42, z_ring=96, n_planets=3, module_mm=0.7, face_mm=10,
        rth_K_per_W=2.0),
    ActuatorSpec(
        name="JXA-120", role="hip pitch, knee (1.2 m robot); hip roll/yaw, ankle (1.7 m robot)",
        target_peak_Nm=120, target_cont_Nm=40, target_noload_rad_s=20, benchmark="RobStride RS04 (120/40 N.m, 1420 g, 120 mm)",
        slots=36, poles=40, stator_od_mm=100, stack_mm=20, airgap_mm=0.55, magnet_mm=3.0, pole_arc=0.85,
        tooth_tip_mm=1.0, slot_open_mm=2.2, slot_depth_mm=15.0,
        z_sun=12, z_planet=42, z_ring=96, n_planets=3, module_mm=1.0, face_mm=13,
        rth_K_per_W=1.05),
    ActuatorSpec(
        name="JXA-360", role="knee, hip pitch (1.7-1.8 m, 50-70 kg robot)",
        target_peak_Nm=360, target_cont_Nm=100, target_noload_rad_s=15, benchmark="Unitree H1 M107 knee (360 N.m)",
        slots=48, poles=44, stator_od_mm=140, stack_mm=28, airgap_mm=0.6, magnet_mm=3.5, pole_arc=0.85,
        tooth_tip_mm=1.2, slot_open_mm=2.5, slot_depth_mm=15.0,
        z_sun=12, z_planet=48, z_ring=108, n_planets=3, module_mm=1.25, face_mm=20,
        rth_K_per_W=0.62),
]


# --------------------------------------------------------------------------------------------------------------------
def winding_layout(Q: int, poles: int):
    """Double-layer tooth-coil winding by the star of slots. Returns per-tooth phase letters (upper = forward wound,
    lower = reversed), the fundamental winding factor kw = kp*kd, and the LCM (cogging) / GCD (symmetry) numbers.
    The 60-degree phase belts are rotated in small steps so that no coil phasor sits on a belt boundary; the balanced
    assignment with the highest kw is kept."""
    p = poles // 2
    slot_angle_e = 2 * math.pi * p / Q                     # electrical angle between neighbouring tooth coils
    kp = abs(math.sin(slot_angle_e / 2))                   # pitch factor of a coil around one tooth
    phasors = [(k * slot_angle_e) % (2 * math.pi) for k in range(Q)]
    belts = [("A", 1), ("C", -1), ("B", 1), ("A", -1), ("C", 1), ("B", -1)]
    best = None
    for off_deg in np.arange(0.0, 60.0, 0.25):
        off = math.radians(off_deg) + 1e-6
        layout, sums, counts = [], {"A": 0j, "B": 0j, "C": 0j}, {"A": 0, "B": 0, "C": 0}
        for ang in phasors:
            idx = int(((ang - off + math.pi / 6) % (2 * math.pi)) // (math.pi / 3))
            ph, sgn = belts[idx]
            layout.append(ph if sgn > 0 else ph.lower())
            sums[ph] += sgn * complex(math.cos(ang), math.sin(ang))
            counts[ph] += 1
        mags = [abs(sums[x]) for x in "ABC"]
        if len(set(counts.values())) != 1 or max(mags) - min(mags) > 1e-6:
            continue
        # phase B must lag A by 120 deg electrically (positive sequence)
        kd = mags[0] / counts["A"]
        if best is None or kd > best[0] + 1e-9:
            best = (kd, layout, counts["A"])
    kd, layout, n = best
    # rotate the labelling so tooth 1 carries a forward-wound A coil
    k0 = layout.index("A")
    layout = layout[k0:] + layout[:k0]
    return {"layout": layout, "kp": kp, "kd": kd, "kw": kp * kd, "lcm": math.lcm(Q, poles),
            "coils_per_phase": n, "balanced": True, "repeat_units": math.gcd(Q, p),
            "symmetric_no_ump": (math.gcd(Q, poles) % 2 == 0)}


def lewis_Y(z: int) -> float:
    """Lewis form factor (module basis), 20 deg full-depth teeth; adequate for a first pass."""
    return math.pi * (0.154 - 0.912 / z)


def design(s: ActuatorSpec, T_hot_C=100.0, T_mag_C=80.0):
    p = s.poles // 2
    Q = s.slots
    wl = winding_layout(Q, s.poles)
    kw = wl["kw"]

    # ---------------- geometry (outer rotor: teeth point outwards) ----------------
    Ds = s.stator_od_mm / 1000
    g = s.airgap_mm / 1000
    hm = s.magnet_mm / 1000
    L = s.stack_mm / 1000
    D = Ds + g                                  # mean air-gap diameter
    tau_s = math.pi * Ds / Q                    # slot pitch at the tooth tips
    tau_p = math.pi * D / s.poles               # pole pitch
    b0 = s.slot_open_mm / 1000
    # Carter coefficient
    g_mag = g + hm / MAGNET["mu_r"]
    gam = (b0 / g_mag) ** 2 / (5 + b0 / g_mag)
    kc = tau_s / (tau_s - gam * g_mag)
    # magnet working point (simple series reluctance, leakage factor 0.95)
    Br = MAGNET["Br20"] * (1 + MAGNET["tc_Br"] * (T_mag_C - 20))
    Bg = 0.95 * Br / (1 + MAGNET["mu_r"] * kc * g / hm)
    B1 = (4 / math.pi) * Bg * math.sin(s.pole_arc * math.pi / 2)     # fundamental amplitude
    # tooth and yoke sizing from flux
    kst = STEEL_LAM["stack_factor"]
    w_t = Bg * tau_s / (STEEL_LAM["B_tooth_max"] * kst)
    phi_pole = s.pole_arc * Bg * tau_p * L                            # actual flux per pole
    h_y = phi_pole / (2 * STEEL_LAM["B_yoke_max"] * L * kst)
    h_rotor = phi_pole / (2 * 1.6 * L)                                # rotor back iron (1018 / EN3 steel, 1.6 T)
    r_tip = Ds / 2
    r2 = r_tip - s.tooth_tip_mm / 1000                                # under the tooth tips
    r1 = r2 - s.slot_depth_mm / 1000                                  # slot bottom
    r_bore = r1 - h_y                                                 # stator bore (hub, bearings)
    A_slot_gross = (math.pi * (r2 ** 2 - r1 ** 2) - Q * w_t * (r2 - r1)) / Q
    liner = 0.25e-3                                                   # epoxy powder coat / Nomex liner
    perim = 2 * (r2 - r1) + (2 * math.pi * r1 / Q - w_t)
    A_slot = A_slot_gross - liner * perim
    # winding: (1) series turns from the no-load speed target, (2) wire from the slot fill target
    lam_per_turn = kw * B1 * D * L / p                                # flux linkage per series turn
    G_ = 1 + s.z_ring / s.z_sun
    Vmax_ = 0.95 * VDC / math.sqrt(3)
    lam_target = Vmax_ / (p * G_ * s.target_noload_rad_s * 1.12)      # 12 % headroom for IR drop and friction
    n_coils = wl["coils_per_phase"]
    choices = []
    for a_ in [x for x in (1, 2, 3, 4, 6, 8) if n_coils % x == 0 and wl["repeat_units"] % x == 0]:
        for Nc_ in range(3, 80):
            lam_ = lam_per_turn * Nc_ * n_coils / a_
            if lam_ <= lam_target:
                choices.append((abs(lam_ - lam_target) / lam_target + 0.004 * a_, a_, Nc_))
    _, a, Nc = min(choices)
    best_w = None
    for dd in (0.35, 0.40, 0.45, 0.50, 0.56, 0.60, 0.63, 0.67, 0.71, 0.75, 0.80, 0.85, 0.90, 1.00):
        for ns in range(1, s.max_strands + 1):
            fill = 2 * Nc * ns * math.pi * (dd / 1000) ** 2 / 4 / A_slot
            if fill <= s.fill_target and (best_w is None or fill > best_w[0] + 0.01 or (abs(fill - best_w[0]) <= 0.01 and ns < best_w[1])):
                best_w = (fill, ns, dd)
    _, strands, wire_mm = best_w
    d = wire_mm / 1000
    d_ins = d * 1.08 + 0.02e-3                                        # grade-2 enamel build
    A_strand = math.pi * d ** 2 / 4
    A_cond = strands * A_strand
    cu_fill = 2 * Nc * A_cond / A_slot                                # bare copper / net slot area (2 coil sides)
    pack_fill = 2 * Nc * strands * (math.pi * d_ins ** 2 / 4) / A_slot
    r_mid = (r1 + r2) / 2
    w_slot_mid = 2 * math.pi * r_mid / Q - w_t
    coil_build = 0.5 * w_slot_mid
    l_turn = 2 * (L + 2 * liner) + 2 * (w_t + 2 * liner) + math.pi * coil_build
    N_ph = Nc * Q / 3 / a                                             # series turns per phase
    rho_hot = RHO_CU20 * (1 + ALPHA_CU * (T_hot_C - 20))
    R20 = RHO_CU20 * Nc * Q * l_turn / (3 * a ** 2 * A_cond)
    R_hot = R20 * (1 + ALPHA_CU * (T_hot_C - 20))
    m_cu = Q * Nc * A_cond * l_turn * 8960 * 1.08                     # +8 % leads, terminations
    wire_len = Q * Nc * strands * l_turn * 1.08

    # ---------------- electromagnetics ----------------
    lam = kw * N_ph * B1 * D * L / p                                  # peak flux linkage per phase (Wb-turn)
    Kt_pk = 1.5 * p * lam                                             # N.m per A (amplitude)
    Kt_rms = Kt_pk * math.sqrt(2)
    Ke_LL_rms_per_krpm = math.sqrt(3) * p * lam * (1000 * 2 * math.pi / 60) / math.sqrt(2)
    Km = Kt_rms / math.sqrt(3 * R_hot)                                # N.m / sqrt(W), hot
    g_e = kc * g + hm / MAGNET["mu_r"]
    L_gap = (Q / 3) * MU0 * Nc ** 2 * tau_s * L / g_e / a ** 2
    w_slot_top = 2 * math.pi * r2 / Q - w_t
    lam_slot = (s.slot_depth_mm / 1000) / (3 * max(w_slot_mid / 2, 1e-4)) + (s.tooth_tip_mm / 1000) / b0
    L_slot = (Q / 3) * 2 * MU0 * L * Nc ** 2 * lam_slot / a ** 2
    L_end = (Q / 3) * MU0 * Nc ** 2 * (2 * (w_t + coil_build)) * 0.3 / a ** 2
    Ls = L_gap + L_slot + L_end
    shear_peak_kPa = None

    # ---------------- torque-speed at 48 V ----------------
    G = 1 + s.z_ring / s.z_sun
    eta = s.gear_eff
    R_tot = R_hot + s.r_ext_ohm
    Vmax = 0.95 * VDC / math.sqrt(3)                                  # SVPWM phase-peak limit
    # peak current: enough for the peak-torque target; Kt rolls off 11 % between I_pk/3 and I_pk
    # (calibrated on RS04: 120 N.m at 90 Apk is 0.90 x the Kt implied by 40 N.m at 27 Apk)
    i_peak = 1.03 * s.target_peak_Nm / (G * eta * Kt_pk * 0.89)
    i_peak = math.ceil(i_peak)

    def ksat(I):
        knee = i_peak / 3
        return 1.0 - 0.11 * max(0.0, (I - knee) / (i_peak - knee))

    def tq_motor(I):
        return Kt_pk * I * ksat(I)

    w_out = np.linspace(0, 1.25 * s.target_noload_rad_s * 1.6, 400)
    T_env, T_env_fw = [], []
    for wo in w_out:
        we = p * wo * G
        A_ = R_tot ** 2 + (we * Ls) ** 2
        B_ = 2 * R_tot * we * lam
        C_ = (we * lam) ** 2 - Vmax ** 2
        disc = B_ ** 2 - 4 * A_ * C_
        if C_ >= 0 or disc < 0:
            Iq = 0.0
        else:
            Iq = (-B_ + math.sqrt(disc)) / (2 * A_)
        Iq = min(Iq, i_peak)
        T_env.append(max(0.0, G * eta * tq_motor(Iq) - 0.02 * G * Kt_pk))
    T_env = np.array(T_env)
    noload = float(w_out[np.argmax(T_env <= 0)]) if np.any(T_env <= 0) else float(w_out[-1])

    peak_motor = tq_motor(i_peak)
    peak_out = G * eta * peak_motor
    shear_peak_kPa = 2 * peak_motor / (math.pi * D ** 2 * L) / 1000

    # ---------------- thermal ----------------
    # iron loss at the continuous operating speed (joint at 40 % of no-load speed)
    f_e = p * 0.4 * noload * G / (2 * math.pi)
    m_teeth = Q * w_t * (r2 - r1 + s.tooth_tip_mm / 1000) * L * kst * STEEL_LAM["density"]
    m_yoke = math.pi * (r1 ** 2 - r_bore ** 2) * L * kst * STEEL_LAM["density"]
    m_stator = m_teeth + m_yoke
    P_fe = STEEL_LAM["P_W_per_kg_1T_400Hz"] * (f_e / 400) ** 1.5 * (STEEL_LAM["B_tooth_max"] * 0.9) ** 2 * m_stator
    T_amb, T_lim = 30.0, 120.0                                        # leave 25 K margin below the class-H 145-155 C limit
    P_allow = (T_lim - T_amb) / s.rth_K_per_W - P_fe
    I_cont_rms = math.sqrt(max(P_allow, 0) / (3 * R_hot))
    T_cont_out = G * eta * Kt_rms * I_cont_rms
    P_cu_peak = 3 * (i_peak / math.sqrt(2)) ** 2 * R_hot
    # adiabatic time at peak: copper heat capacity only (worst case)
    t_peak_s = m_cu * 385 * (T_lim - 80) / P_cu_peak

    # ---------------- gearbox ----------------
    m_g = s.module_mm / 1000
    b = s.face_mm / 1000
    assembly_ok = (s.z_sun + s.z_ring) % s.n_planets == 0
    coax_ok = s.z_ring == s.z_sun + 2 * s.z_planet
    a_c = (s.z_sun + s.z_planet) * m_g / 2                            # carrier radius
    tip_planet = (s.z_planet + 2) * m_g
    adjacency_gap = 2 * a_c * math.sin(math.pi / s.n_planets) - tip_planet
    d_sun = s.z_sun * m_g
    K_share, K_v = 1.15, 1.15
    def gear_stress(T_m):
        Ft = T_m / (d_sun / 2) / s.n_planets * K_share * K_v
        sigF = Ft / (b * m_g * lewis_Y(s.z_sun))
        u = s.z_planet / s.z_sun
        ZE, ZH = 189.8e3 ** 1.0 * 1e3, 2.49                         # sqrt(Pa) units: 189.8 sqrt(MPa) -> 189.8e3 sqrt(Pa)
        sigH = 189.8e3 * ZH * math.sqrt(Ft * (u + 1) / (b * d_sun * u))
        return Ft, sigF, sigH
    Ft_pk, sigF_pk, sigH_pk = gear_stress(peak_motor)
    T_cont_motor = T_cont_out / (G * eta)
    Ft_c, sigF_c, sigH_c = gear_stress(T_cont_motor)
    gear = {
        "ratio": G, "z_sun": s.z_sun, "z_planet": s.z_planet, "z_ring": s.z_ring, "n_planets": s.n_planets,
        "module_mm": s.module_mm, "face_mm": s.face_mm, "d_sun_mm": d_sun * 1e3, "d_planet_mm": s.z_planet * s.module_mm,
        "d_ring_pitch_mm": s.z_ring * s.module_mm, "carrier_radius_mm": a_c * 1e3,
        "assembly_condition_ok": assembly_ok, "coaxial_ok": coax_ok, "planet_tip_clearance_mm": adjacency_gap * 1e3,
        "sun_profile_shift_note": "12-tooth sun: use +0.3 profile shift (or 25 deg pressure angle) to avoid undercut",
        "sun_bending_peak_MPa": sigF_pk / 1e6, "SF_bending_static_at_peak": GEAR_STEEL["sigma_F_static"] / sigF_pk,
        "sun_bending_cont_MPa": sigF_c / 1e6, "SF_bending_fatigue_at_cont": GEAR_STEEL["sigma_F_lim"] / sigF_c,
        "contact_peak_MPa": sigH_pk / 1e6, "contact_cont_MPa": sigH_c / 1e6,
        "SF_contact_at_cont": GEAR_STEEL["sigma_H_lim"] / sigH_c, "material": GEAR_STEEL["grade"],
        "reflected_rotor_inertia_note": "reflected inertia scales with ratio^2: J_out = G^2 * J_rotor",
    }

    # ---------------- masses (ESTIMATED from volumes) ----------------
    r_rot_in = r_tip + g
    r_rot_out = r_rot_in + hm + h_rotor
    m_mag = s.poles * s.pole_arc * (math.pi * 2 * (r_rot_in + hm / 2) / s.poles) * hm * L * MAGNET["density"]
    m_rotor_iron = math.pi * (r_rot_out ** 2 - (r_rot_in + hm) ** 2) * (L + 2e-3) * 7850
    J_rotor = 0.5 * (m_rotor_iron + m_mag) * (r_rot_out ** 2 + r_rot_in ** 2) * 1.35   # + end plate/hub (ESTIMATED)
    r_ring = s.z_ring * m_g / 2
    m_ring = math.pi * ((r_ring + 3.5 * m_g + 2e-3) ** 2 - r_ring ** 2) * b * 7850
    m_planets = s.n_planets * math.pi * (s.z_planet * m_g / 2) ** 2 * b * 7850 * 0.55
    m_sun = math.pi * (d_sun / 2) ** 2 * b * 7850 * 2
    m_carrier = math.pi * (a_c + 0.35 * s.z_planet * m_g) ** 2 * 2 * 3e-3 * 2700 * 1.6
    env_d = 2 * max(r_rot_out + 4e-3, r_ring + 3.5 * m_g + 6e-3)
    env_len = L + 2 * s.tooth_tip_mm / 1000 + 2 * coil_build + b + 30e-3          # end turns, gear, bearings, driver
    m_housing = math.pi * env_d * env_len * 1.8e-3 * 2700 + 2 * math.pi * (env_d / 2) ** 2 * 2.5e-3 * 2700
    m_bearings = 0.06 * (env_d / 0.12) ** 2
    m_elec = 0.045 * (env_d / 0.12) ** 1.5
    parts = {"stator_laminations": m_stator, "copper": m_cu, "magnets": m_mag, "rotor_back_iron": m_rotor_iron,
             "ring_gear": m_ring, "planets": m_planets, "sun_and_shaft": m_sun, "carrier": m_carrier,
             "housing_al": m_housing, "bearings": m_bearings, "driver_pcb_encoders": m_elec}
    m_total = sum(parts.values()) * 1.07                                   # fasteners, adhesive, cable
    J_out = J_rotor * G ** 2

    return {
        "spec": asdict(s),
        "winding": {**wl, "layout_str": " ".join(wl["layout"]), "turns_per_coil": Nc, "parallel_paths": a,
                    "strands_in_hand": strands, "wire_bare_mm": wire_mm, "wire_SWG_note": swg_note(wire_mm),
                    "series_turns_per_phase": N_ph, "copper_fill_bare": cu_fill, "packing_fill_insulated": pack_fill,
                    "mean_turn_mm": l_turn * 1e3, "wire_length_m": wire_len, "copper_mass_g": m_cu * 1e3,
                    "connection": "star (Y); parallel paths joined at the terminals" if a > 1 else "star (Y), series"},
        "geometry_mm": {"stator_od": s.stator_od_mm, "airgap_diameter": D * 1e3, "stack": s.stack_mm,
                        "tooth_width": w_t * 1e3, "slot_depth": s.slot_depth_mm, "stator_yoke": h_y * 1e3,
                        "stator_bore_d": 2 * r_bore * 1e3, "magnet_thickness": s.magnet_mm,
                        "rotor_back_iron": h_rotor * 1e3, "rotor_od": 2 * r_rot_out * 1e3,
                        "slot_area_net_mm2": A_slot * 1e6, "carter": kc,
                        "envelope_d": env_d * 1e3, "envelope_len": env_len * 1e3},
        "magnetics": {"Br_hot_T": Br, "B_gap_T": Bg, "B1_fundamental_T": B1, "flux_linkage_mWb": lam * 1e3,
                      "kw": kw, "pole_pairs": p, "elec_freq_at_noload_Hz": p * noload * G / (2 * math.pi)},
        "electrical": {"R_phase_20C_mohm": R20 * 1e3, "R_phase_100C_mohm": R_hot * 1e3, "L_phase_uH": Ls * 1e6,
                       "Kt_motor_Nm_per_Apk": Kt_pk, "Kt_motor_Nm_per_Arms": Kt_rms,
                       "Kt_output_Nm_per_Arms": Kt_rms * G * eta,
                       "Ke_LL_Vrms_per_krpm_motor": Ke_LL_rms_per_krpm, "Km_Nm_per_sqrtW_hot": Km,
                       "Km_output_Nm_per_sqrtW": Km * G * eta, "i_peak_A": i_peak,
                       "J_peak_A_per_mm2": i_peak / a / (A_cond * 1e6), "J_cont_Arms_per_mm2": I_cont_rms / a / (A_cond * 1e6),
                       "P_cu_at_peak_W": P_cu_peak, "seconds_at_peak_adiabatic": t_peak_s},
        "performance": {"gear_ratio": G, "peak_out_Nm": peak_out, "cont_out_Nm": T_cont_out,
                        "noload_out_rad_s": noload, "noload_out_rpm": noload * 60 / (2 * math.pi),
                        "air_gap_shear_peak_kPa": shear_peak_kPa, "P_iron_cont_W": P_fe,
                        "I_cont_Arms": I_cont_rms, "reflected_inertia_kgm2": J_out,
                        "mass_kg": m_total, "torque_density_Nm_per_kg": peak_out / m_total,
                        "meets_peak": peak_out >= s.target_peak_Nm, "meets_cont": T_cont_out >= s.target_cont_Nm,
                        "meets_speed": noload >= s.target_noload_rad_s},
        "masses_g": {k: v * 1e3 for k, v in parts.items()} | {"total_g": m_total * 1e3},
        "materials_bill": {"magnet_g": m_mag * 1e3, "magnet_pieces": s.poles, "copper_g": m_cu * 1e3,
                           "wire_length_m": wire_len, "lamination_blank_g": math.pi * (Ds / 2) ** 2 * L * STEEL_LAM["density"] * 1e3 / kst,
                           "lamination_sheets": round(L / 0.35e-3), "gear_steel_g": (m_ring + m_planets + m_sun) * 1e3},
        "gear": gear,
        "curve": {"w_out_rad_s": w_out.tolist(), "T_out_Nm": T_env.tolist()},
    }


def swg_note(d_mm: float) -> str:
    table = {0.50: "25 SWG (0.508)", 0.56: "24 SWG (0.559)", 0.60: "23 SWG is 0.610", 0.71: "22 SWG (0.711)",
             0.80: "21 SWG (0.813)", 0.40: "27 SWG (0.417)", 0.45: "26 SWG (0.457)"}
    return table.get(round(d_mm, 2), "metric")


# --------------------------------------------------------------------------------------------------------------------
def plots(results):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Wedge, Circle, Rectangle, FancyArrowPatch

    plt.rcParams.update({"font.family": "serif", "font.serif": ["STIXGeneral", "DejaVu Serif"], "mathtext.fontset": "stix", "font.size": 9, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.grid": True, "grid.alpha": 0.25})
    colors = {"A": "#c0392b", "B": "#2e7d32", "C": "#1f5fa8"}
    ref = {"JXA-40": [("RS06", 36, 50.3), ("Damiao J8009P", 40, 35.1)],
           "JXA-120": [("RS04", 120, 20.9), ("Damiao J10010L", 120, 20.9), ("CubeMars AK10-9", 48, 10.5)],
           "JXA-360": [("Unitree H1 knee (max speed)", 360, 14.0), ("Damiao J10422P", 400, 12.6)]}

    # 1. torque-speed envelopes
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.2))
    for ax, r in zip(axes, results):
        c = r["curve"]; s = r["spec"]
        ax.plot(c["w_out_rad_s"], c["T_out_Nm"], color="#1f2a44", lw=2, label=f"{s['name']} peak (48 V)")
        ax.plot(c["w_out_rad_s"], np.minimum(r["performance"]["cont_out_Nm"], c["T_out_Nm"]), color="#d35400", ls="--", lw=1.2, label="JXA continuous (thermal)")
        for i, (lab, T, w) in enumerate(ref.get(s["name"], [])):
            col = ["#2e7d32", "#7b1fa2", "#00838f"][i]
            ax.plot([0], [T], "o", ms=5, color=col, clip_on=False, label=f"{lab}: ● {T:.0f} N·m peak, ■ {w:.0f} rad/s no-load")
            ax.plot([w], [0], "s", ms=5, color=col, clip_on=False)
        ax.set_xlabel("output speed [rad/s]"); ax.set_ylabel("output torque [N·m]")
        ax.set_title(s["name"], fontweight="bold"); ax.set_xlim(0, r["performance"]["noload_out_rad_s"] * 1.25)
        ax.set_ylim(0, max(max(c["T_out_Nm"]), max([t for _, t, _ in ref.get(s['name'], [(0, 0, 0)])])) * 1.15)
        ax.legend(fontsize=6.2, loc="lower left", frameon=True, framealpha=0.9)
    fig.tight_layout(); fig.savefig(FIG / "torque_speed.png", dpi=200); plt.close(fig)

    # 2. winding diagram for each class (teeth coloured by phase, arrow = winding direction)
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.7))
    for ax, r in zip(axes, results):
        Q = r["spec"]["slots"]; lay = r["winding"]["layout"]
        ax.set_aspect("equal"); ax.axis("off")
        ax.add_patch(Circle((0, 0), 0.62, fc="#eceff1", ec="#90a4ae"))
        for k, ph in enumerate(lay):
            ang = 90 - k * 360 / Q
            w = 360 / Q * 0.62
            col = colors[ph.upper()]
            ax.add_patch(Wedge((0, 0), 1.0, ang - w / 2, ang + w / 2, width=0.38, fc=col if ph.isupper() else "white",
                               ec=col, lw=1.4))
            th = math.radians(ang)
            ax.text(1.12 * math.cos(th), 1.12 * math.sin(th), ph, ha="center", va="center", fontsize=6.5,
                    color=col, fontweight="bold")
            ax.text(0.5 * math.cos(th), 0.5 * math.sin(th), str(k + 1), ha="center", va="center", fontsize=4.8, color="#455a64")
        ax.set_xlim(-1.25, 1.25); ax.set_ylim(-1.25, 1.25)
        ax.set_title(f"{r['spec']['name']}: {Q}N{r['spec']['poles']}P, kw = {r['winding']['kw']:.3f}", fontsize=9, fontweight="bold")
    fig.text(0.5, 0.02, "Filled tooth / capital letter = wind clockwise (seen from the tooth tip); white tooth / small letter = "
             "anticlockwise. Tooth 1 at 12 o'clock, numbering clockwise.", ha="center", fontsize=7.5)
    fig.tight_layout(rect=(0, 0.05, 1, 1)); fig.savefig(FIG / "winding_layouts.png", dpi=200); plt.close(fig)

    # 3. section of JXA-120 (to scale, mm; x = axial, y = radial), legend instead of leader lines
    r = results[1]; gm = r["geometry_mm"]; gr = r["gear"]
    Rs = gm["stator_od"] / 2; Rb = gm["stator_bore_d"] / 2; Rr = gm["rotor_od"] / 2
    Lst = gm["stack"]; hm = gm["magnet_thickness"]; gap = gm["airgap_diameter"] / 2 - Rs
    r2 = Rs - 1.0; r1 = r2 - gm["slot_depth"]; ce = 3.0
    b = gr["face_mm"]; ac = gr["carrier_radius_mm"]; dp = gr["d_planet_mm"]; rs = gr["d_sun_mm"] / 2; rr = gr["d_ring_pitch_mm"] / 2
    xg = Lst + 9; Rh = max(Rr + 1.5, rr + 5)
    parts = [  # (label, colour, [(x, y, w, h), ...])
        ("aluminium housing + covers", "#b0bec5", [(-22, Rh, xg + b + 31, 2.2), (-16, 3, 2.2, Rh - 3), (-22, 3, 1.5, Rh - 3), (xg + b + 7, ac + 19, 2, Rh - ac - 19)]),
        ("stationary hub (Al)", "#cfd8dc", [(-13.8, 8, 2, Rb - 8), (-11.8, Rb - 5, Lst + 11.8, 5), (-11.8, 8, Lst + 11.8, 2), (Lst - 2, 10, 2, Rb - 15)]),
        ("driver PCB (FOC, CAN)", "#2e7d32", [(-19.5, 6, 1.6, Rh - 12)]),
        ("encoder magnet", "#6a1b9a", [(-15.6, 0, 1.6, 3)]),
        ("rotor shaft", "#455a64", [(-13.6, 0, xg + b + 13.6, 4)]),
        ("ball bearings", "#26a69a", [(-10, 4, 5, 4), (Lst - 7, 4, 5, 4), (xg + b + 1, ac + 10, 6, 8)]),
        ("stator laminations", "#8d8d8d", [(0, Rb, Lst, r1 - Rb), (0, r2, Lst, Rs - r2)]),
        ("copper coils", "#d98c3a", [(-ce, r1, Lst + 2 * ce, r2 - r1)]),
        ("NdFeB magnets", "#ab47bc", [(0, Rs + gap, Lst, hm)]),
        ("rotor can + end plate (steel)", "#546e7a", [(-2, Rs + gap + hm, Lst + 6, Rr - Rs - gap - hm), (Lst + 4, 4, 2.5, Rr - 4)]),
        ("sun gear", "#ff8f00", [(xg, 4, b, rs - 4 + 0.6)]),
        ("planet gears (x3)", "#ffe082", [(xg, ac - dp / 2, b, dp)]),
        ("ring gear (fixed)", "#ffb300", [(xg, rr, b, Rh - rr)]),
        ("output carrier", "#78909c", [(xg - 1.8, 4, 1.2, ac + 4), (xg + b + 0.6, 4, 1.2, ac + 6), (xg + b + 1.8, 4, 5, 6)]),
    ]
    fig, ax = plt.subplots(figsize=(4.0, 4.9)); ax.set_aspect("equal"); ax.axis("off")
    handles = []
    from matplotlib.patches import Patch
    for lab, col, rects in parts:
        for (x, yv, w, h) in rects:
            for sgn in (1, -1):
                ax.add_patch(Rectangle((x, yv if sgn > 0 else -yv - h), w, h, fc=col, ec="#263238", lw=0.5))
        handles.append(Patch(fc=col, ec="#263238", lw=0.5, label=lab))
    ax.plot([-26, xg + b + 14], [0, 0], color="#37474f", lw=0.6, ls="-.")
    ax.annotate("", xy=(xg + b + 13, -Rh - 6), xytext=(-22, -Rh - 6), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text((xg + b - 3) / 2, -Rh - 10, f"≈ {xg + b + 31:.0f} mm", ha="center", fontsize=7)
    ax.annotate("", xy=(xg + b + 16, Rh + 2.2), xytext=(xg + b + 16, -Rh - 2.2), arrowprops=dict(arrowstyle="<->", lw=0.6))
    ax.text(xg + b + 18, 0, f"Ø {2 * Rh + 4.4:.0f} mm", rotation=90, va="center", fontsize=7)
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=2, fontsize=7, frameon=False)
    ax.set_xlim(-27, xg + b + 22); ax.set_ylim(-Rh - 13, Rh + 5)
    ax.set_title("JXA-120 section (to scale)", fontsize=9, fontweight="bold")
    fig.tight_layout(); fig.savefig(FIG / "jxa120_section.png", dpi=220); plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
    results = [design(s) for s in SPECS]
    slim = []
    for r in results:
        rr = {k: v for k, v in r.items() if k != "curve"}
        slim.append(rr)
        p = r["performance"]; e = r["electrical"]; w = r["winding"]; g = r["gear"]
        print(f"\n== {r['spec']['name']} ==  ratio {p['gear_ratio']:.1f}  peak {p['peak_out_Nm']:.1f} N.m  cont {p['cont_out_Nm']:.1f} N.m  "
              f"no-load {p['noload_out_rad_s']:.1f} rad/s  mass {p['mass_kg']:.2f} kg  shear {p['air_gap_shear_peak_kPa']:.1f} kPa")
        print(f"   kw {w['kw']:.3f}  fill(bare) {w['copper_fill_bare']:.2f}  pack {w['packing_fill_insulated']:.2f}  R100 {e['R_phase_100C_mohm']:.1f} mOhm  "
              f"L {e['L_phase_uH']:.0f} uH  Kt_out {e['Kt_output_Nm_per_Arms']:.2f} N.m/Arms  Km {e['Km_Nm_per_sqrtW_hot']:.3f}  "
              f"Ke {e['Ke_LL_Vrms_per_krpm_motor']:.1f}")
        print(f"   gear: asm {g['assembly_condition_ok']} gap {g['planet_tip_clearance_mm']:.1f} mm  SFstatic {g['SF_bending_static_at_peak']:.2f} "
              f"SFfat {g['SF_bending_fatigue_at_cont']:.2f}  SFcontact {g['SF_contact_at_cont']:.2f}  sigH_pk {g['contact_peak_MPa']:.0f}")
        print(f"   geom: {json.dumps({k: round(v, 2) for k, v in r['geometry_mm'].items()})}")
        print(f"   mass g: {json.dumps({k: round(v) for k, v in r['masses_g'].items()})}")
        print(f"   layout: {w['layout_str']}  balanced {w['balanced']} sym {w['symmetric_no_ump']} lcm {w['lcm']}")
        print(f"   t_peak {e['seconds_at_peak_adiabatic']:.1f} s  Pcu_peak {e['P_cu_at_peak_W']:.0f} W  Pfe {p['P_iron_cont_W']:.1f} W")
    # prototype shortcut: wind off-the-shelf Chinese stator cores (research/raw/india_motor_materials_raw.md section 3.4)
    variants = []
    for base, label, kw in [(SPECS[1], "JXA-120 on a bought 10020 core (100 x 20 mm, 36N42P, US$19-31)", dict(poles=42)),
                            (SPECS[2], "JXA-360 on three stacked 13710 cores (137 x 30 mm, 36N42P, US$74 each)",
                             dict(slots=36, poles=42, stator_od_mm=137, stack_mm=30))]:
        import dataclasses
        rv = design(dataclasses.replace(base, **kw))
        variants.append({"label": label, "performance": rv["performance"], "winding": {k: rv["winding"][k] for k in
                         ("kw", "turns_per_coil", "parallel_paths", "strands_in_hand", "wire_bare_mm", "layout_str")},
                         "electrical": rv["electrical"]})
    (OUT / "variants.json").write_text(json.dumps(variants, indent=2, default=float))
    (OUT / "design.json").write_text(json.dumps(slim, indent=2, default=float))
    (OUT / "curves.json").write_text(json.dumps([{"name": r["spec"]["name"], **r["curve"]} for r in results]))
    plots(results)
    return results


if __name__ == "__main__":
    main()
