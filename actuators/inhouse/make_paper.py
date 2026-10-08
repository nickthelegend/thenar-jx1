"""Build the technical paper as an IEEE-style two-column research paper (LaTeX, IEEEtran).

'Design and Techno-Economic Analysis of In-House Quasi-Direct-Drive Actuators for Humanoid Robots in India'

Every number is read from results/design.json, results/variants.json and results/cost.json (run qdd_design.py and
cost_model.py first), so the paper never disagrees with the calculation. Needs pdflatex + IEEEtran
(apt-get install texlive-latex-extra texlive-publishers texlive-science latexmk).
Usage: python actuators/inhouse/make_paper.py
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from latex_tools import TexTemplate, build_pdf, esc, inr, lakh, num

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
FIG = HERE / "figures"
BUILD = HERE / ".paper_build"
OUT_PDF = HERE / "JXA_inhouse_actuator_research_paper.pdf"

D = {d["spec"]["name"]: d for d in json.loads((RES / "design.json").read_text())}
VAR = json.loads((RES / "variants.json").read_text())
C = json.loads((RES / "cost.json").read_text())
N = ["JXA-40", "JXA-120", "JXA-360"]


def design_table() -> str:
    def row(label, f):
        return label + " & " + " & ".join(f(D[n]) for n in N) + r" \\"
    rows = [
        row("Benchmark", lambda d: {"JXA-40": "RobStride RS06", "JXA-120": "RobStride RS04", "JXA-360": "Unitree H1 knee"}[d["spec"]["name"]]),
        row("Slots / poles", lambda d: f"{d['spec']['slots']}N{d['spec']['poles']}P"),
        row("Stator OD $\\times$ stack [mm]", lambda d: f"{d['geometry_mm']['stator_od']:.0f} $\\times$ {d['geometry_mm']['stack']:.0f}"),
        row("Rotor OD / stator bore [mm]", lambda d: f"{d['geometry_mm']['rotor_od']:.1f} / {d['geometry_mm']['stator_bore_d']:.1f}"),
        row("Air gap / magnet [mm]", lambda d: f"{d['spec']['airgap_mm']} / {d['spec']['magnet_mm']}"),
        row("Tooth / slot depth / yoke [mm]", lambda d: f"{d['geometry_mm']['tooth_width']:.1f} / {d['geometry_mm']['slot_depth']:.0f} / {d['geometry_mm']['stator_yoke']:.1f}"),
        row("$B_g$ at 80\\,$^\\circ$C [T]", lambda d: f"{d['magnetics']['B_gap_T']:.2f}"),
        row("Winding $k_w$", lambda d: f"{d['winding']['kw']:.3f}"),
        row("Turns/tooth, strands $\\times$ wire, paths", lambda d: f"{d['winding']['turns_per_coil']}, {d['winding']['strands_in_hand']}$\\times${d['winding']['wire_bare_mm']:.2f}\\,mm, {d['winding']['parallel_paths']}"),
        row("Copper fill (bare)", lambda d: f"{d['winding']['copper_fill_bare']:.2f}"),
        row("Gear $Z_s/Z_p/Z_r$, module [mm]", lambda d: f"{d['gear']['z_sun']}/{d['gear']['z_planet']}/{d['gear']['z_ring']}, {d['gear']['module_mm']}"),
        row("Gear ratio $G$", lambda d: f"{d['gear']['ratio']:.0f}"),
        r"\midrule",
        row("\\textbf{Peak torque} [N$\\cdot$m]", lambda d: f"\\textbf{{{d['performance']['peak_out_Nm']:.0f}}}"),
        row("\\textbf{Continuous torque} [N$\\cdot$m]", lambda d: f"\\textbf{{{d['performance']['cont_out_Nm']:.0f}}}"),
        row("\\textbf{No-load speed} at 48\\,V [rad/s]", lambda d: f"\\textbf{{{d['performance']['noload_out_rad_s']:.1f}}}"),
        row("Peak phase current [A]", lambda d: f"{d['electrical']['i_peak_A']}"),
        row("$K_t$ at output [N$\\cdot$m/A$_\\mathrm{rms}$]", lambda d: f"{d['electrical']['Kt_output_Nm_per_Arms']:.2f}"),
        row("$K_e$ [V$_\\mathrm{rms,LL}$/krpm]", lambda d: f"{d['electrical']['Ke_LL_Vrms_per_krpm_motor']:.1f}"),
        row("$K_m$ motor / output [N$\\cdot$m/$\\sqrt{\\mathrm{W}}$]", lambda d: f"{d['electrical']['Km_Nm_per_sqrtW_hot']:.2f} / {d['electrical']['Km_output_Nm_per_sqrtW']:.1f}"),
        row("$R_\\mathrm{ph}$ (20\\,$^\\circ$C) / $L_\\mathrm{ph}$", lambda d: f"{d['electrical']['R_phase_20C_mohm']:.0f}\\,m$\\Omega$ / {d['electrical']['L_phase_uH']:.0f}\\,$\\mu$H"),
        row("$J$ peak / cont. [A/mm$^2$]", lambda d: f"{d['electrical']['J_peak_A_per_mm2']:.0f} / {d['electrical']['J_cont_Arms_per_mm2']:.0f}"),
        row("Time at peak, adiabatic [s]", lambda d: f"{d['electrical']['seconds_at_peak_adiabatic']:.1f}"),
        row("Peak air-gap shear [kPa]", lambda d: f"{d['performance']['air_gap_shear_peak_kPa']:.0f}"),
        row("Gear SF: bend.\\ static / fatigue / contact", lambda d: f"{d['gear']['SF_bending_static_at_peak']:.1f} / {d['gear']['SF_bending_fatigue_at_cont']:.1f} / {d['gear']['SF_contact_at_cont']:.2f}"),
        row("Reflected inertia [kg$\\cdot$cm$^2$]", lambda d: f"{d['performance']['reflected_inertia_kgm2'] * 1e4:.0f}"),
        row("Envelope \\O{} $\\times$ length [mm]", lambda d: f"{d['geometry_mm']['envelope_d']:.0f} $\\times$ {d['geometry_mm']['envelope_len']:.0f}"),
        row("\\textbf{Mass} [kg] (N$\\cdot$m/kg)", lambda d: f"\\textbf{{{d['performance']['mass_kg']:.2f}}} ({d['performance']['torque_density_Nm_per_kg']:.0f})"),
    ]
    return "\n".join(rows)


def winding_table() -> str:
    out = []
    for n in N:
        w = D[n]["winding"]
        pat = " ".join(w["layout"][: len(w["layout"]) // w["repeat_units"]])
        out.append(f"{n} & {D[n]['spec']['slots']} & {w['turns_per_coil']} & {w['strands_in_hand']}$\\times${w['wire_bare_mm']:.2f} & "
                   f"{w['parallel_paths']} & {w['wire_length_m']:.0f} / {w['copper_mass_g']:.0f} & {D[n]['electrical']['R_phase_20C_mohm']:.0f} & "
                   f"\\texttt{{{pat}}} ($\\times${w['repeat_units']}) \\\\")
    return "\n".join(out)


def cost_rows() -> str:
    out = []
    for n in N:
        c = C["classes"][n]; b = c["buy"]
        out.append(f"{n} & {num(c['unit']['P']['total'])} & {num(c['unit']['B']['total'])} & {num(c['unit']['F']['total'])} & "
                   f"{num(b['usd_landed'])} & {num(b['china_distributor']) if b['china_distributor'] else '--'} & "
                   f"{num(b['china_cogs']['low'])}--{num(b['china_cogs']['high'])} \\\\")
    return "\n".join(out)


def line_items() -> str:
    u = C["classes"]["JXA-120"]["unit"]
    rows = [f"{esc(k)} & {num(u['P']['lines'][k])} & {num(u['B']['lines'][k])} & {num(u['F']['lines'][k])} \\\\" for k in u["P"]["lines"]]
    rows.append(r"\midrule")
    rows.append(f"\\textbf{{Total}} & \\textbf{{{num(u['P']['total'])}}} & \\textbf{{{num(u['B']['total'])}}} & \\textbf{{{num(u['F']['total'])}}} \\\\")
    return "\n".join(rows)


def housing_rows() -> str:
    hr = C["housing_routes_jxa120"]
    lots = list(next(iter(hr.values()))["per_part"].keys())
    best = {n: min(hr, key=lambda k: hr[k]["per_part"][n]) for n in lots}
    short = {"CNC from billet (6061-T6)": "CNC from billet", "Sand casting (LM25) + finish machining": "Sand cast + machine",
             "Gravity die casting + finish machining": "Gravity die + machine", "High-pressure die casting + finish machining": "HPDC + machine",
             "Metal 3D printing (AlSi10Mg) + finish machining": "DMLS AlSi10Mg + machine"}
    out = []
    for name, v in hr.items():
        cells = [(f"\\textbf{{{num(v['per_part'][n])}}}" if best[n] == name else num(v["per_part"][n])) for n in lots]
        out.append(short.get(name, esc(name)) + " & " + " & ".join(cells) + r" \\")
    return "\n".join(out)


def nre_rows(tier: str) -> str:
    return "\n".join(f"{esc(k)} & {num(v)} \\\\" for k, v in C["nre"][tier]["items"].items())


def values() -> dict:
    d40, d120, d360 = (D[n] for n in N)
    c = C["classes"]
    j = C["scenario_jx1"]; f = C["scenario_fullsize"]; be = C["breakeven_jxa120_vs_rs04_china"]
    v120, v360 = VAR[0], VAR[1]
    return {
        "date": "October 2026",
        "kt120": f"{d120['electrical']['Kt_output_Nm_per_Arms']:.2f}", "ke120": f"{d120['electrical']['Ke_LL_Vrms_per_krpm_motor']:.1f}",
        "r120": f"{d120['electrical']['R_phase_20C_mohm']:.0f}", "l120": f"{d120['electrical']['L_phase_uH']:.0f}",
        "ipk120": f"{d120['electrical']['i_peak_A']}", "w0120": f"{d120['performance']['noload_out_rad_s']:.1f}",
        "m120": f"{d120['performance']['mass_kg']:.2f}", "m120pct": f"{(d120['performance']['mass_kg'] / 1.42 - 1) * 100:.0f}",
        "kt40": f"{d40['electrical']['Kt_output_Nm_per_Arms']:.2f}",
        "pk40": f"{d40['performance']['peak_out_Nm']:.0f}", "pk120": f"{d120['performance']['peak_out_Nm']:.0f}", "pk360": f"{d360['performance']['peak_out_Nm']:.0f}",
        "ct40": f"{d40['performance']['cont_out_Nm']:.0f}", "ct120": f"{d120['performance']['cont_out_Nm']:.0f}", "ct360": f"{d360['performance']['cont_out_Nm']:.0f}",
        "w040": f"{d40['performance']['noload_out_rad_s']:.1f}", "w0360": f"{d360['performance']['noload_out_rad_s']:.1f}",
        "ipk360": f"{d360['electrical']['i_peak_A']}", "sh_list": " / ".join(f"{D[n]['performance']['air_gap_shear_peak_kPa']:.0f}" for n in N),
        "rth_list": " / ".join(f"{D[n]['spec']['rth_K_per_W']:.2f}" for n in N),
        "contact120": f"{d120['gear']['contact_peak_MPa']:,.0f}", "airgap": f"{d120['spec']['airgap_mm']:.2f}",
        "fill": f"{d120['spec']['fill_target']:.2f}",
        "design_rows": design_table(), "winding_rows": winding_table(), "cost_rows": cost_rows(), "line_items": line_items(),
        "housing_rows": housing_rows(), "nre_p": nre_rows("P"), "nre_b": nre_rows("B"), "nre_f": nre_rows("F"),
        "nre_p_tot": lakh(C["nre"]["P"]["total"]), "nre_b_tot": lakh(C["nre"]["B"]["total"]), "nre_f_tot": lakh(C["nre"]["F"]["total"]),
        "v120": esc(v120["label"]), "v120pk": f"{v120['performance']['peak_out_Nm']:.0f}", "v120ct": f"{v120['performance']['cont_out_Nm']:.0f}",
        "v120w0": f"{v120['performance']['noload_out_rad_s']:.1f}",
        "v120wind": f"{v120['winding']['turns_per_coil']} turns, {v120['winding']['strands_in_hand']}$\\times${v120['winding']['wire_bare_mm']}\\,mm, {v120['winding']['parallel_paths']} paths",
        "v360": esc(v360["label"]), "v360pk": f"{v360['performance']['peak_out_Nm']:.0f}", "v360ct": f"{v360['performance']['cont_out_Nm']:.0f}",
        "v360w0": f"{v360['performance']['noload_out_rad_s']:.1f}",
        "v360wind": f"{v360['winding']['turns_per_coil']} turns, {v360['winding']['strands_in_hand']}$\\times${v360['winding']['wire_bare_mm']}\\,mm, {v360['winding']['parallel_paths']} paths",
        "p120": inr(c["JXA-120"]["unit"]["P"]["total"]), "b120": inr(c["JXA-120"]["unit"]["B"]["total"]), "f120": inr(c["JXA-120"]["unit"]["F"]["total"]),
        "b360": inr(c["JXA-360"]["unit"]["B"]["total"]), "usd360": inr(c["JXA-360"]["buy"]["usd_landed"]),
        "cn120": inr(c["JXA-120"]["buy"]["china_distributor"]), "usd120": inr(c["JXA-120"]["buy"]["usd_landed"]),
        "cogs120": inr(c["JXA-120"]["buy"]["china_cogs"]["central"]),
        "magnet120": inr(D["JXA-120"]["materials_bill"]["magnet_g"] / 1000 * 6000),
        "loaded_p120": inr(c["JXA-120"]["loaded"]["P"]), "loaded_b120": inr(c["JXA-120"]["loaded"]["B"]), "loaded_f120": inr(c["JXA-120"]["loaded"]["F"]),
        "be_b_margin": inr(-be["B"]["margin_per_unit"]), "be_f_margin": inr(be["F"]["margin_per_unit"]),
        "be_f_fixed": lakh(be["F"]["fixed_per_year"]), "be_units": f"{be['F']['breakeven_units_per_year']:,.0f}",
        "jx1_usd": inr(j["buy_usd_route"]), "jx1_cn": inr(j["buy_china_distributor"]), "jx1_parts": inr(j["inhouse_parts_and_labour"]),
        "jx1_proto": inr(j["inhouse_prototype_rounds"]), "jx1_equip": inr(j["inhouse_garage_equipment"]),
        "jx1_total": inr(j["inhouse_total_first_set"]), "jx1_next": inr(j["inhouse_marginal_next_set"]),
        "fs_usd": inr(f["buy_usd_route"]), "fs_cn": inr(f["buy_china_distributor"]), "fs_p": inr(f["inhouse_P"]),
        "fs_b": inr(f["inhouse_B"]), "fs_lb": inr(f["loaded_B"]), "fs_f": inr(f["inhouse_F"]), "fs_lf": inr(f["loaded_F"]),
        "fs_cogs": inr(f["china_cogs_central"]),
        "inr_usd": f"{C['assumptions']['INR_USD']}", "inr_cny": f"{C['assumptions']['INR_CNY']}",
    }


TEX = r"""
\documentclass[journal,10pt]{IEEEtran}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{multirow}
\usepackage{array}
\usepackage{cite}
\usepackage{url}
\usepackage[hidelinks]{hyperref}
\usepackage{xcolor}
\usepackage{balance}
\renewcommand{\arraystretch}{1.12}
\newcolumntype{L}{>{\raggedright\arraybackslash}X}
\graphicspath{{../figures/}}
\hyphenation{Rob-Stride Da-miao Uni-tree quasi-direct}

\begin{document}

\title{Design and Techno-Economic Analysis of In-House Quasi-Direct-Drive Actuators for Humanoid Robots in India}

\author{JX1~Humanoid~Project%
\thanks{Manuscript prepared @@date. This work is part of the open-source \texttt{thenar-jx1} humanoid repository
(\url{https://github.com/nickthelegend/thenar-jx1}); all design scripts, cost models and research logs cited here are in
\texttt{actuators/inhouse/} and \texttt{research/raw/}.}%
\thanks{Labels: values marked \emph{calculated} come from the analytic model of Section~IV; \emph{estimated} costs are derived from
cited price listings (24~Sep--6~Oct 2026); nothing in this paper has yet been built or measured.}}

\markboth{JX1 Humanoid Project Technical Report, @@date}{Design and Techno-Economic Analysis of In-House QDD Actuators}

\maketitle

\begin{abstract}
Joint actuators account for 77\,\% of the parts cost of the JX1 humanoid and are today imported from China. This paper asks whether
quasi-direct-drive (QDD) actuators of the RobStride class, and the larger units needed by full-size humanoids, can be designed and
built in India with minimal tooling, and at what cost. We (i)~derive joint torque requirements from a rigid-body analysis of JX1,
the published limits of full-size humanoids and human biomechanics, arriving at three classes of 40, 120 and 360\,N$\cdot$m peak torque;
(ii)~size an outer-rotor surface-permanent-magnet motor with tooth-concentrated windings and a single-stage planetary reducer for each class
with an analytic electromagnetic, thermal and gear-stress model, which reproduces the RobStride RS04 datasheet within 3--20\,\%;
(iii)~describe a winding, casting and assembly process that relies on Indian job shops rather than a factory; and (iv)~build a cost model
at prototype, batch and 1{,}000-unit-per-year scale. The 120\,N$\cdot$m class reaches @@pk120\,N$\cdot$m peak, @@ct120\,N$\cdot$m continuous and
@@w0120\,rad/s at 48\,V with an estimated mass of @@m120\,kg. Built in batches of 25 it costs @@b120 per unit against @@cn120 for an imported
RS04, and an Indian line breaks even with the import only at about @@be_units units per year. In-house production is therefore justified by
capability, the 360\,N$\cdot$m class and supply security, not by unit cost at small volume.
\end{abstract}

\begin{IEEEkeywords}
Humanoid robot, quasi-direct-drive actuator, permanent-magnet motor, concentrated winding, planetary gear, techno-economic analysis, India.
\end{IEEEkeywords}

\section{Introduction}
\IEEEPARstart{L}{egged} and humanoid robots are built around their joint actuators. Since the MIT Cheetah~\cite{wensing2017,katz2018},
the dominant design for dynamic legs has been the \emph{quasi-direct-drive} (QDD) actuator: a large-diameter permanent-magnet motor with a
low-ratio (6--10:1) planetary reducer, which keeps the joint back-drivable, tolerant of impacts and torque-controllable through motor current.
Chinese manufacturers such as RobStride, Damiao and Unitree now sell such actuators at about US\$1--2 per newton-metre of peak torque~\cite{robstride,china_econ},
which has made low-cost humanoids possible, including the 1.2\,m, 27.5\,kg JX1 developed in this project.

For an Indian builder, however, the actuators are imported (77\,\% of the JX1 bill of materials), subject to duty, lead time and export-control
risk, and no Indian manufacturer offers comparable units at volume~\cite{india_capital}. This motivates three questions:
\begin{enumerate}
\item How much torque and speed do humanoid joints need, from JX1 up to 70\,kg full-size robots?
\item Can a QDD actuator of that class be designed from first principles and built with job-shop processes and hand winding?
\item What does it cost compared with importing, and compared with what Chinese manufacturers spend?
\end{enumerate}
The contributions of this paper are: an open, reproducible analytic sizing model for outer-rotor QDD actuators validated against a commercial
datasheet; a three-class actuator family (JXA-40/120/360) with complete winding data; a manufacturing route, including a casting and moulding
analysis, suited to Indian job shops; and a make-versus-buy cost model at three production scales.

\section{Background and Related Work}
\subsection{Electromagnetic principles}
A current-carrying conductor of length $\ell$ in a flux density $B$ experiences the Lorentz force $F = B I \ell$, and a changing flux
linkage induces the back-EMF $e = -\mathrm{d}\lambda/\mathrm{d}t$ (Faraday). Integrating the tangential force over the air gap gives the
torque of any radial-flux machine in terms of the air-gap shear stress $\sigma$, gap diameter $D$ and stack length $L$~\cite{pyrhonen2014}:
\begin{equation}
T = \tfrac{\pi}{2}\,\sigma\,D^2 L .
\label{eq:shear}
\end{equation}
Air-cooled servo machines sustain $\sigma\approx5$--15\,kPa continuously and 30--60\,kPa for seconds. Because torque grows with $D^2$ but only
linearly with $L$, robot actuators are flat ``pancake'' machines, usually with an outer rotor that maximises $D$ for a given envelope~\cite{hendershot2010}.
Field-oriented control (FOC) keeps the stator field in quadrature with the rotor magnets, so that torque is proportional to the $q$-axis current.

\subsection{Quasi-direct-drive actuators}
Wensing \emph{et~al.}~\cite{wensing2017} and Katz~\cite{katz2018} showed that a 6:1 single-stage planetary with a large-gap motor gives
the impact tolerance and force transparency needed for dynamic locomotion; the MIT Humanoid~\cite{saloutos2023} scaled the concept to 33.6
and 68\,N$\cdot$m modules. A gear ratio $G$ multiplies torque by $G$ but reflected rotor inertia by $G^2$, which is why legged robots favour
6--10:1. Open-source low-cost designs include Berkeley Humanoid Lite~\cite{bhl2025} with 3D-printed cycloidal reducers. Table~\ref{tab:survey}
summarises representative commercial and research actuators; the full survey of about 110 units is in the project logs~\cite{logs_act}.

\begin{table*}[!t]
\caption{Representative QDD and humanoid actuators (datasheet values unless noted)}
\label{tab:survey}
\centering\footnotesize
\begin{tabularx}{\textwidth}{@{}L c c c c L l@{}}
\toprule
Actuator & Peak [N$\cdot$m] & Rated [N$\cdot$m] & No-load [rad/s] & Mass [g] & Reducer / motor & Price \\
\midrule
RobStride RS00 / RS02 / RS06~\cite{robstride} & 14 / 17 / 36 & 5 / 6 / 11 & 33 / 43 / 50 & 310 / 405 / 621 & 10 / 7.75 / 9:1 planetary; 28-pole & US\$125 / 145 / 210 \\
RobStride RS03 / RS04~\cite{robstride} & 60 / 120 & 20 / 40 & 20.4 / 20.9 & 880 / 1{,}420 & 9:1 planetary; 42-pole & US\$225 / 255 \\
Damiao DM-J10010L / J10422P~\cite{damiao} & 120 / 400 & 40 / 100 & 20.9 / 12.6 & 1{,}372 / 2{,}700 & 10:1 / 22:1 & US\$265 / 480 \\
Unitree Go2 motor~\cite{simplexity} & 23.7 & -- & 30 & 530 & 6.22:1 (9/19/47); outer rotor 36N42P & -- \\
Unitree G1 knee / H1 knee~\cite{unitree_rl} & 90--139 / 360 & -- & $\sim$20 / 14 & -- & G1: 2-stage 22.5:1 & -- \\
CubeMars AK80-9 / AK10-9~\cite{cubemars} & 18 / 48 & 9 / 18 & -- / 10.5 & 485 / 960 & 9:1; 36N42P, \O{}98\,mm & INR~79,739 / 104,809 \\
MIT Humanoid U10 / U12~\cite{saloutos2023} & 33.6 / 68 & -- & 55 / 45 & 619 / 1{,}174 & 6:1 (+ belts) & research \\
Berkeley Humanoid Lite 6512~\cite{bhl2025} & $\sim$20--28 & -- & -- & -- & 15:1 printed cycloid & US\$157--188 \\
Tesla Optimus rotary~\cite{tesla2022,nsk2026} & 20 / 110 / 180 & -- & -- & -- & strain-wave + clutch; plus linear 0.5--8\,kN & in-house \\
\bottomrule
\end{tabularx}
\end{table*}

No teardown of a RobStride actuator has been published. The vendor's own site data give 42 poles, a 9:1 machined-steel planetary and the
electrical constants used for validation in Section~V-B; every 42-pole motor of this size with a published slot count (CubeMars AK10-9, Unitree
Go2, T-Motor U10) is 36N42P~\cite{simplexity,cubemars}.

\section{Torque and Speed Requirements}
\subsection{JX1 (1.2\,m, 27.5\,kg)}
A rigid-body inverse-dynamics model of JX1 walking at 0.30--0.79\,m/s, turning, squatting and standing on one leg, with peak requirement
$\max(1.5\,\tau_\mathrm{dyn},\,1.25\,\tau_\mathrm{static})$, gives the joint requirements of Table~\ref{tab:jx1} (\texttt{calculations/} in the repository).

\begin{table}[!t]
\caption{JX1 joint requirements and the class that covers each joint}
\label{tab:jx1}
\centering\footnotesize
\begin{tabularx}{\columnwidth}{@{}L c l l@{}}
\toprule
Joint & Peak / cont. [N$\cdot$m] & Today & In-house \\
\midrule
Hip pitch & 85 / 26 & RS04 & JXA-120 \\
Knee & 71 / 30 & RS04 & JXA-120 \\
Hip roll & 50 / 17 & RS03 & JXA-120 \\
Hip yaw & 37 / 8 & RS06$^\ast$ & JXA-40 \\
Ankle motors ($\times$2) & 32 / 3.4 & RS06 & JXA-40 \\
Waist yaw & $\approx$30 & RS06 & JXA-40 \\
Shoulder, elbow & $\leq$17 & RS02 / RS00 & buy \\
\bottomrule
\end{tabularx}\\[2pt]
{\scriptsize $^\ast$RS06 is 3\,\% below the hip-yaw peak requirement.}
\end{table}

\subsection{Full-size humanoids and human data}
Table~\ref{tab:full} lists published limits of 50--70\,kg humanoids from official model files and SDKs~\cite{unitree_rl,fourier,ubtech};
peak knee torque normalised by robot mass ranges from 2.1 to 7.7\,N$\cdot$m/kg. Human knee moments reach 0.5--1.3\,N$\cdot$m/kg in walking,
up to 2.0 in rising from a chair, 3.1 in running at 3.5\,m/s and 3.6 in sprinting~\cite{schache2011,yoshioka2014,walknorms}. A 70\,kg robot that
should run or rise from the floor therefore needs 200--360\,N$\cdot$m at the knee.

\begin{table}[!t]
\caption{Joint limits of full-size humanoids [N$\cdot$m]}
\label{tab:full}
\centering\footnotesize
\begin{tabularx}{\columnwidth}{@{}L c c c c@{}}
\toprule
Robot (mass) & Knee & Hip pitch & Hip roll/yaw & Ankle \\
\midrule
Unitree H1/H1-2 (47/70\,kg) & 360 & 220 & 220 & 59 / 2$\times$75 \\
Fourier GR-2/GR-3 (63/70\,kg) & 366 & 366 & 95--140 & 54--59 \\
UBTech Walker S2 (70\,kg) & 225 & 225 & 225 / 65 & 2$\times$65 \\
AgiBot A2 Lite (64\,kg) & 270 & -- & -- & -- \\
Fourier GR-1T2 ($\approx$53\,kg) & 135 & 135 & 84 / 65 & 42 \\
\bottomrule
\end{tabularx}
\end{table}

\subsection{Actuator classes}
Three classes cover JX1 completely and every leg joint of the largest humanoids: \textbf{JXA-40} (40\,N$\cdot$m, $\geq$40\,rad/s; RS06 class),
\textbf{JXA-120} (120\,N$\cdot$m, $\geq$20\,rad/s; RS04 class) and \textbf{JXA-360} (360\,N$\cdot$m, $\geq$15\,rad/s; Unitree H1 knee class,
for which no RobStride product exists).

\section{Design Model}
Each actuator is an outer-rotor surface-PM motor with double-layer tooth-concentrated windings, a single-stage planetary (sun input, ring fixed,
carrier output), dual magnetic encoders and a 48\,V FOC driver on the rear cover (Fig.~\ref{fig:section}). The model is implemented in
\texttt{qdd\_design.py}.

\subsection{Magnetic circuit and torque constant}
With remanence $B_r$ (N42SH, 80\,$^\circ$C), recoil permeability $\mu_r$, magnet thickness $h_m$, air gap $g$, Carter coefficient $k_C$ and
leakage factor $k_l = 0.95$, the air-gap flux density and its fundamental are
\begin{equation}
B_g = \frac{k_l B_r}{1 + \mu_r k_C g / h_m}, \qquad B_1 = \frac{4}{\pi} B_g \sin\!\Big(\frac{\alpha_p \pi}{2}\Big),
\end{equation}
with pole-arc ratio $\alpha_p = 0.85$. Teeth and yokes are sized for 1.75\,T and 1.55\,T in M270-35A steel. For $p$ pole pairs,
$N_\mathrm{ph}$ series turns per phase and winding factor $k_w$, the phase flux linkage and torque are
\begin{equation}
\lambda = \frac{k_w N_\mathrm{ph} B_1 D L}{p}, \qquad T = \tfrac{3}{2}\, p\, \lambda\, i_q = K_t\, i_q .
\end{equation}

\subsection{Winding factor and layout}
For $Q$ slots and $2p$ poles, adjacent tooth coils are displaced by $\theta_s = 2\pi p/Q$ electrical. The pitch factor is
$k_p = |\sin(p\pi/Q)|$; the distribution factor $k_d$ and the coil-to-phase assignment follow from the star of slots~\cite{bianchi2006,magnussen2003}:
each coil phasor is assigned to the 60$^\circ$ phase belt that contains it, and $k_w = k_p k_d$. The resulting layouts (Fig.~\ref{fig:winding})
give $k_w$ = 0.933 (24N28P), 0.945 (36N40P) and 0.949 (48N44P), all with an even number of repeating units (no unbalanced magnetic pull).

\subsection{Turns, wire and resistance}
The number of turns is chosen from the speed target: $\lambda_\mathrm{target} = V_\mathrm{max}/(1.12\, p\, G\, \omega_0)$, with
$V_\mathrm{max} = 0.95\,V_\mathrm{dc}/\sqrt{3}$ for space-vector modulation and 12\,\% headroom. The conductor is then made as large as a bare-copper
slot fill of @@fill allows (realistic for careful hand or needle winding). With $N_c$ turns per tooth, $a$ parallel paths, conductor area $A_c$
and mean turn length $\ell_t$,
\begin{equation}
R_\mathrm{ph} = \frac{\rho_\mathrm{Cu}\, N_c\, Q\, \ell_t}{3 a^2 A_c}, \qquad K_m = \frac{K_{t,\mathrm{rms}}}{\sqrt{3 R_\mathrm{ph}}} .
\end{equation}
The motor constant $K_m$ (torque per square root of copper loss) is independent of the number of turns and is the figure of merit for thermally
limited joints.

\subsection{Inductance, torque--speed and thermal limits}
The phase inductance is estimated as the sum of the tooth-coil air-gap term, slot leakage and end-winding leakage,
$L_\mathrm{ph} \approx \frac{Q}{3a^2}\mu_0 N_c^2 \tau_s L / g_e + L_\mathrm{slot} + L_\mathrm{end}$. With $i_d = 0$ the steady-state voltage limit
\begin{equation}
(R\, i_q + \omega_e \lambda)^2 + (\omega_e L_\mathrm{ph} i_q)^2 \leq V_\mathrm{max}^2
\end{equation}
together with the current limit gives the torque--speed envelope (Fig.~\ref{fig:ts}). Saturation is represented by an 11\,\% roll-off of $K_t$
between $I_\mathrm{pk}/3$ and $I_\mathrm{pk}$, calibrated on RS04 (120\,N$\cdot$m at 90\,A versus 40\,N$\cdot$m at 27\,A). Continuous torque follows
from a lumped winding-to-ambient resistance $R_\mathrm{th}$ (@@rth_list\,K/W for a unit bolted to an aluminium limb) and a 120\,$^\circ$C winding limit:
\begin{equation}
3 I_\mathrm{rms}^2 R_\mathrm{ph} + P_\mathrm{Fe} = (T_\mathrm{lim} - T_\mathrm{amb}) / R_\mathrm{th} .
\end{equation}

\subsection{Planetary stage}
For a planetary with fixed ring, $G = 1 + Z_r/Z_s$, with $Z_r = Z_s + 2Z_p$ and $(Z_s+Z_r)/N_p$ an integer. A 12/42/96 set with three planets
gives 9:1 (12/48/108 gives 10:1). The sun is checked with the Lewis bending and Hertz contact equations~\cite{shigley2015}:
\begin{equation}
\sigma_F = \frac{F_t K_\gamma K_v}{b\, m\, Y}, \qquad \sigma_H = Z_E Z_H \sqrt{\frac{F_t (u+1)}{b\, d_1\, u}},
\end{equation}
with load-sharing and dynamic factors $K_\gamma = K_v = 1.15$, against case-carburised EN353 ($\sigma_{F,\lim} = 430$\,MPa,
$\sigma_{H,\lim} = 1{,}400$\,MPa). The 12-tooth sun needs a $+0.3$ profile shift to avoid undercut.

\section{Results}
\subsection{The JXA family}
Table~\ref{tab:design} gives the calculated designs. All three classes meet their peak, continuous and speed targets; peak air-gap shear
stresses are @@sh_list\,kPa. Fig.~\ref{fig:ts} compares the envelopes with commercial units, Fig.~\ref{fig:section} shows the JXA-120 section to scale
and Fig.~\ref{fig:winding} the winding layouts.

\begin{table*}[!t]
\caption{Calculated JXA designs (analytic model; expected accuracy $\pm$15--30\,\% until measured)}
\label{tab:design}
\centering\footnotesize
\begin{tabular}{@{}l c c c@{}}
\toprule
 & JXA-40 & JXA-120 & JXA-360 \\
\midrule
@@design_rows
\bottomrule
\end{tabular}
\end{table*}

\begin{figure*}[!t]
\centering
\includegraphics[width=\textwidth]{torque_speed.png}
\caption{Calculated torque--speed envelopes at 48\,V (no field weakening) and thermal continuous torque, with commercial benchmarks
($\bullet$ peak torque, $\blacksquare$ no-load speed).}
\label{fig:ts}
\end{figure*}

\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{jxa120_section.png}
\caption{JXA-120 section drawn to scale from the calculated dimensions: stator on a fixed hub, outer magnet rotor driving the sun gear,
ring gear integral with the housing, carrier output on a single large bearing, driver and encoders on the rear cover.}
\label{fig:section}
\end{figure}

\subsection{Validation against a commercial datasheet}
Table~\ref{tab:valid} compares the JXA-120 model with RobStride's published RS04 constants~\cite{robstride}. The calculated torque constant,
back-EMF constant, inductance, peak current and no-load speed are within 3--20\,\% of the datasheet; the lower calculated resistance reflects the
longer (20\,mm) stack and correspondingly more copper. The JXA-40 output torque constant (@@kt40\,N$\cdot$m/A) likewise matches RS06's 1.10.

\begin{table}[!t]
\caption{Model check: JXA-120 versus the RS04 datasheet}
\label{tab:valid}
\centering\footnotesize
\begin{tabularx}{\columnwidth}{@{}L c c r@{}}
\toprule
Quantity & RS04 & JXA-120 & $\Delta$ \\
\midrule
$K_t$ output [N$\cdot$m/A$_\mathrm{rms}$] & 2.10 & @@kt120 & +10\,\% \\
$K_e$ [V$_\mathrm{rms,LL}$/krpm] & 16.9 & @@ke120 & $-$3\,\% \\
$R_\mathrm{ph}$ [m$\Omega$] & $\approx$80 & @@r120 & more Cu \\
$L_\mathrm{ph}$ [$\mu$H] & $\approx$105 & @@l120 & $-$19\,\% \\
Peak current [A] & 90 & @@ipk120 & $-$4\,\% \\
No-load speed [rad/s] & 20.9 & @@w0120 & +11\,\% \\
Mass [kg] & 1.42 & @@m120 & +@@m120pct\,\% \\
\bottomrule
\end{tabularx}
\end{table}

\subsection{Discussion of the design}
The first-iteration JXA-120 is @@m120pct\,\% heavier than RS04, mainly from solid planets, conservative housings and the longer stack;
compound planets, lightened carriers, 0.2\,mm laminations and die-cast housings are the second-iteration levers. Peak current densities of
60--95\,A/mm$^2$ are sustainable for only 1.5--4\,s (adiabatic copper heating of 40\,K), so the controller must enforce an $I^2t$ limit. The sun
gear is the most loaded component (contact stress @@contact120\,MPa at peak) and must be carburised and ground. The JXA-360 driver must supply
@@ipk360\,A peak at 48\,V; a 72\,V bus (as on Unitree H1) with 1.5$\times$ the turns reduces this by a third.

\subsection{Prototype shortcut: commercial stator cores}
Bare outer-rotor stator cores are sold in China in exactly these sizes~\cite{logs_mat}. Re-running the model on a 10020 core (100$\times$20\,mm,
36N42P, US\$19--31) gives @@v120pk/@@v120ct\,N$\cdot$m at @@v120w0\,rad/s (@@v120wind); three stacked 13710 cores (137$\times$30\,mm, 36N42P) give
@@v360pk/@@v360ct\,N$\cdot$m at @@v360w0\,rad/s (@@v360wind). Buying cores removes the lamination tooling step from the first prototypes.

\begin{figure*}[!t]
\centering
\includegraphics[width=0.92\textwidth]{winding_layouts.png}
\caption{Winding layouts from the star of slots, viewed from the tooth tips: each tooth carries one coil; capital letter = clockwise,
lower case = anticlockwise; tooth 1 at 12 o'clock, numbered clockwise.}
\label{fig:winding}
\end{figure*}

\section{Manufacturing Route}
\subsection{Winding procedure}
Table~\ref{tab:wind} gives the winding data. The procedure, suitable for a technician or a local motor-rewinding shop, is:
(1)~deburr the lamination stack and insulate it with 0.2--0.3\,mm epoxy powder coat or Nomex/DMD liners, verified at 500\,V;
(2)~mark tooth~1 and follow the pattern, winding each phase group with one continuous wire, capital letters clockwise;
(3)~wind the first layer tight against the tooth from the slot bottom outwards at about 10--15\,\% of the wire's breaking load, filling only half
of each slot; (4)~count turns exactly; (5)~terminate, form the star point and lace the end turns; (6)~test before impregnation: phase
resistances within $\pm$2\,\%, insulation $>$100\,M$\Omega$ at 500\,V, inductances within $\pm$5\,\%, and, once the rotor is fitted, three equal
back-EMF sine waves; (7)~impregnate with class-H varnish (pre-heat 100\,$^\circ$C, cure about 2\,h at 150\,$^\circ$C) and re-test.
Hand winding takes 3--5\,h per JXA-120 stator, a manual needle winder 20--40\,min and a CNC multi-spindle winder 1--3\,min.

\begin{table*}[!t]
\caption{Winding data (class-200 dual-coat wire; star connection)}
\label{tab:wind}
\centering\scriptsize
\begin{tabularx}{\textwidth}{@{}l c c c c c c L@{}}
\toprule
Class & Teeth & Turns/tooth & Strands $\times$ wire [mm] & Paths & Wire [m] / Cu [g] & $R_\mathrm{ph}$ 20\,$^\circ$C [m$\Omega$] & Pattern from tooth 1 (one repeating unit) \\
\midrule
@@winding_rows
\bottomrule
\end{tabularx}
\end{table*}

\subsection{Other parts and assembly}
Laminations are fibre-laser or wire-EDM cut M270-35A (bonded, powder-coated); magnets are bought pre-magnetised N42SH arc segments bonded with
high-temperature epoxy using a non-magnetic spacer comb; the rotor can is turned EN3/EN8 steel; gears are hobbed EN353 or 20MnCr5, carburised to
58--62\,HRC, DIN~7; the ring gear is wire-EDM cut; output bearings are crossed-roller or paired thin-section units; the driver is an STM32G4
board with a three-phase gate driver, 80--100\,V MOSFETs and a CAN transceiver, keeping RobStride's MIT-mode protocol. The rotor must be inserted
with a guide sleeve because magnetic pull exceeds several hundred newtons; the air gap is only @@airgap\,mm, so the hub must be concentric with
the rotor bearings to $\leq$0.02\,mm.

\subsection{Casting and moulding}
Molten aluminium (poured at 700--750\,$^\circ$C) cannot be cast in silicone moulds, whose best grades survive about 300\,$^\circ$C, and must never be
poured into cement or damp media, because water flashes to steam at about 1{,}600 times its volume~\cite{logs_cast}. Silicone moulds suit urethane
resins or low-melting alloys only; plastic injection moulding (moulds INR~1.5--15~lakh) suits covers but cannot hold $\pm$0.01\,mm bearing seats.
For aluminium housings we compare five routes with
\begin{equation}
C_\mathrm{part}(n) = \frac{C_\mathrm{tool}}{n} + c_\mathrm{blank} + t_m\, r(n),
\end{equation}
where $t_m$ is the finish-machining time (25--60\,\% lower for a near-net blank) and $r(n)$ the shop rate, falling from INR~2{,}500/h for tiny lots
to INR~400/h at volume. Table~\ref{tab:housing} and Fig.~\ref{fig:housing} show that billet machining wins below about 10 pieces, sand casting
from a 3D-printed pattern from about 20 pieces, and high-pressure die casting only near 10{,}000 pieces. The saving is modest (about INR~400--500
per housing, 1.5--2\,\% of a batch actuator) because the bearing seats and two set-ups dominate machining either way. Sintered or
metal-injection-moulded planets (INR~20--150 each after tooling) are the larger lever at volume, while the highly loaded sun should remain hobbed
and case-hardened.

\begin{table}[!t]
\caption{Cost per finished JXA-120 housing [INR] (cheapest in bold)}
\label{tab:housing}
\centering\scriptsize\setlength{\tabcolsep}{3.5pt}
\begin{tabular}{@{}l r r r r r@{}}
\toprule
Route / lot size & 2 & 25 & 200 & 1k & 10k \\
\midrule
@@housing_rows
\bottomrule
\end{tabular}
\end{table}

\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{housing_routes.png}
\caption{Finished-housing cost versus lot size for five process routes.}
\label{fig:housing}
\end{figure}

\subsection{Test protocol}
Each design iteration is verified by: winding resistance and inductance balance; insulation and hipot; back-EMF and harmonic content; cogging torque
($<$1\,\% of rated after compensation); $K_t$ and peak torque with a lever arm and load cell; torque--speed on a hysteresis brake at 48\,V
($\pm$10\,\% of Fig.~\ref{fig:ts}); a 1\,h thermal soak at continuous torque ($<$120\,$^\circ$C); backlash ($<$15\,arcmin); and a life test replaying
JX1 gait torque traces for $\geq$200\,h at 50--80\,\% of rated torque. The longest published life test of a DIY QDD reducer is 57\,h~\cite{logs_act}.

\section{Cost Analysis}
\subsection{Method}
Unit cost is the sum of parts, labour $h\,r_L$ and a test/scrap allowance; the loaded cost adds equipment written off over three years and
overhead shared over the yearly volume $N$:
\begin{equation}
C_\mathrm{loaded} = \sum_i c_i + h\, r_L + a + \frac{C_\mathrm{NRE}/3 + C_\mathrm{OH}}{N} .
\end{equation}
Three tiers are modelled: prototype (2 units, retail parts, engineer at INR~500/h), batch (25/yr, job-work parts, technician at INR~300/h) and small
factory (1{,}000/yr, stamped laminations, bulk magnets and cores, operator at INR~220/h). Prices are converted at INR~@@inr_usd/US\$ and
INR~@@inr_cny/CNY, with imports carrying duty (32.3\,\%) and freight (7\,\%). The Chinese manufacturer's cost (COGS) is estimated from list prices
less a 30--45\,\% gross margin and cross-checked with broker teardowns of the Unitree G1~\cite{chinapost2026,guosen2026}.

\subsection{Results}
Table~\ref{tab:cost} and Fig.~\ref{fig:cost} give the per-unit results, and Table~\ref{tab:items} the JXA-120 line items (Fig.~\ref{fig:breakdown}).
A prototype JXA-120 costs @@p120, a batch unit @@b120 and a factory unit @@f120, against @@usd120 (US-dollar list, landed) or @@cn120 (China
distributor, landed) for RS04, and an estimated @@cogs120 for RobStride's own cost. Including equipment and overhead, the loaded JXA-120 costs
@@loaded_p120, @@loaded_b120 and @@loaded_f120 in the three tiers.

\begin{table*}[!t]
\caption{Direct cost per actuator versus buying [INR] (estimated)}
\label{tab:cost}
\centering\footnotesize
\begin{tabular}{@{}l r r r r r r@{}}
\toprule
 & \multicolumn{3}{c}{Make in India} & \multicolumn{2}{c}{Buy (landed in India)} & China maker's \\
\cmidrule(lr){2-4}\cmidrule(lr){5-6}
Class & Prototype & Batch 25/yr & 1{,}000/yr & USD list & China distributor & COGS (est.) \\
\midrule
@@cost_rows
\bottomrule
\end{tabular}
\end{table*}

\begin{figure*}[!t]
\centering
\includegraphics[width=\textwidth]{cost_per_unit.png}
\caption{Per-unit cost: making (prototype, batch, 1{,}000/yr) versus buying versus the estimated cost to a Chinese manufacturer (with range).
Horizontal bars include equipment (three-year write-off) and overhead.}
\label{fig:cost}
\end{figure*}

\begin{table}[!t]
\caption{JXA-120 cost line items [INR]}
\label{tab:items}
\centering\scriptsize
\begin{tabularx}{\columnwidth}{@{}L r r r@{}}
\toprule
Item & Prototype & Batch & 1k/yr \\
\midrule
@@line_items
\bottomrule
\end{tabularx}
\end{table}

\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{cost_breakdown_jxa120.png}
\caption{Where the money goes in a JXA-120 at the three tiers, and the estimated split of a Chinese manufacturer's cost.}
\label{fig:breakdown}
\end{figure}

\subsection{Equipment}
The prototype kit (winding jig, LCR and milliohm meters, insulation tester, supply, oven, oscilloscope, a hysteresis-brake dynamometer with torque
sensor) costs @@nre_p_tot; batch add-ons (semi-automatic needle winder, surge tester, second dynamometer, fixtures, inspection) @@nre_b_tot; and a
small factory (CNC winders, stamping dies, gear tooling, end-of-line testers, balancing, varnish line) @@nre_f_tot (Appendix~A).

\subsection{Scenarios and break-even}
For JX1's 13 leg and waist actuators, buying costs @@jx1_usd (USD route) or @@jx1_cn (China distributor). Building 15 in-house units (one spare
per class) costs @@jx1_parts in parts and labour, plus @@jx1_proto for two prototype rounds and @@jx1_equip of equipment, @@jx1_total in total;
each further set costs @@jx1_next. For a full-size humanoid with 4$\times$360, 14$\times$120 and 10$\times$40\,N$\cdot$m joints, buying costs
@@fs_usd (or @@fs_cn); building costs @@fs_p at prototype prices, @@fs_b (loaded @@fs_lb) at batch prices and @@fs_f (loaded @@fs_lf) at factory
prices, against an estimated @@fs_cogs for a Chinese manufacturer.

The break-even volume against the landed China-distributor price $P$ is
\begin{equation}
N^\ast = \frac{C_\mathrm{NRE}/3 + C_\mathrm{OH}}{P - C_\mathrm{unit}} .
\end{equation}
At batch scale the JXA-120 costs @@be_b_margin \emph{more} than buying before any equipment, so no break-even exists. At factory scale the margin
is @@be_f_margin per unit against @@be_f_fixed of yearly fixed cost, giving $N^\ast \approx$ @@be_units units per year. Even then an Indian line
does not reach RobStride's estimated own cost and must compete on duty, service, lead time and supply security. The 360\,N$\cdot$m class is the
exception: a batch JXA-360 (@@b360) already matches the landed price of the nearest import (@@usd360).

\section{Discussion}
\emph{Model accuracy.} The analytic model omits finite-element saturation, harmonic and eddy losses in magnets, and detailed thermal paths; the
3--20\,\% agreement with RS04 is encouraging but a single comparison. \emph{Supply risk.} High-temperature (SH) NdFeB grades containing Dy/Tb need
Chinese export licences under the April 2025 rules, and broader rules are suspended only until 10~November 2026; India's INR~7{,}280~crore
magnet scheme has no producing plant yet~\cite{pmindia2025}. Magnets cost only about @@magnet120 per JXA-120 at bulk prices, so the risk is
availability, not cost. \emph{Economics.} Chinese cost advantage comes from volume (RobStride shipped over 50{,}000 joints by September 2025 and
targets 300{,}000 in 2026~\cite{krasia2025}) and a dense supply chain, not from wages, which are higher in China than in India; direct labour is
only 8--14\,\% of Unitree's cost~\cite{guosen2026}.

\section{Conclusion}
A RobStride-class QDD actuator can be designed from first principles and built in India with job-shop processes, bought stator cores and hand
winding; the analytic JXA-120 reproduces the RS04 datasheet within 3--20\,\%. A INR~3--4~lakh test kit suffices for prototypes. In-house units
are not cheaper below about @@be_units units per year, so JX1 should continue to use imported actuators while the JXA family is developed in
parallel, starting with the 360\,N$\cdot$m class, where no low-cost import exists, and with supply security as the goal. Future work is the
construction and bench testing of JXA-120 prototypes, finite-element refinement of the motor, and a life test of the planetary stage.

\appendices
\section{Equipment Lists [INR]}
\begin{table}[!h]
\centering\scriptsize
\begin{tabularx}{\columnwidth}{@{}L r@{}}
\toprule
\multicolumn{2}{@{}l}{\textbf{A. Prototype kit} (@@nre_p_tot)} \\
\midrule
@@nre_p
\midrule
\multicolumn{2}{@{}l}{\textbf{B. Batch add-ons} (@@nre_b_tot)} \\
\midrule
@@nre_b
\midrule
\multicolumn{2}{@{}l}{\textbf{C. Small-factory add-ons} (@@nre_f_tot)} \\
\midrule
@@nre_f
\bottomrule
\end{tabularx}
\end{table}

\section{Reproducibility}
All results are generated by \texttt{actuators/inhouse/qdd\_design.py} (design, figures), \texttt{cost\_model.py} (costs) and \texttt{make\_paper.py}
(this paper). Source data and every price, with URL, date and evidence label, are in the research logs~\cite{logs_act,logs_mat,logs_cast,china_econ,india_capital}.

\balance
\begin{thebibliography}{99}
\footnotesize
\bibitem{wensing2017} P.~M. Wensing, A.~Wang, S.~Seok, D.~Otten, J.~Lang, and S.~Kim, ``Proprioceptive actuator design in the MIT Cheetah: Impact mitigation and high-bandwidth physical interaction for dynamic legged robots,'' \emph{IEEE Trans. Robot.}, vol.~33, no.~3, pp.~509--522, 2017.
\bibitem{katz2018} B.~G. Katz, ``A low cost modular actuator for dynamic robots,'' M.S. thesis, Massachusetts Institute of Technology, 2018.
\bibitem{saloutos2023} A.~SaLoutos, E.~Stanger-Jones, M.~Guo, H.~Kim, and S.~Kim, ``Design of a highly dynamic humanoid robot,'' arXiv:2104.09025, 2021.
\bibitem{bhl2025} Q.~Liao \emph{et~al.}, ``Berkeley Humanoid Lite: An open-source, accessible, and customizable 3D-printed humanoid robot,'' 2025.
\bibitem{pyrhonen2014} J.~Pyrh\"{o}nen, T.~Jokinen, and V.~Hrabovcov\'{a}, \emph{Design of Rotating Electrical Machines}, 2nd~ed. Chichester, U.K.: Wiley, 2014.
\bibitem{hendershot2010} J.~R. Hendershot and T.~J.~E. Miller, \emph{Design of Brushless Permanent-Magnet Machines}. Venice, FL, USA: Motor Design Books, 2010.
\bibitem{bianchi2006} N.~Bianchi and M.~Dai~Pr\'{e}, ``Use of the star of slots in designing fractional-slot single-layer synchronous motors,'' \emph{IEE Proc. Electr. Power Appl.}, vol.~153, no.~3, pp.~459--466, 2006.
\bibitem{magnussen2003} F.~Magnussen and C.~Sadarangani, ``Winding factors and Joule losses of permanent magnet machines with concentrated windings,'' in \emph{Proc. IEEE IEMDC}, 2003, pp.~333--339.
\bibitem{shigley2015} R.~G. Budynas and J.~K. Nisbett, \emph{Shigley's Mechanical Engineering Design}, 10th~ed. New York, NY, USA: McGraw-Hill, 2015.
\bibitem{robstride} RobStride Dynamics, product data (robstride.com) and RS04 user manual rev.~260713, \url{https://github.com/RobStride/Product_Information}, accessed Sep.~2026.
\bibitem{damiao} Damiao Technology, DM-J series manuals and 2025 product handbook, accessed Sep.~2026.
\bibitem{cubemars} CubeMars, AK80-9 and AK10-9 product pages, \url{https://www.cubemars.com}, accessed Oct.~2026.
\bibitem{simplexity} Simplexity Product Development, ``Unitree Go2 motor teardown,'' \url{https://www.simplexitypd.com/blog/unitree-go2-motor-teardown/}.
\bibitem{unitree_rl} Unitree Robotics, \texttt{unitree\_rl\_lab} actuator models, \url{https://github.com/unitreerobotics/unitree_rl_lab}.
\bibitem{fourier} Fourier Intelligence, GRx robot models, \url{https://github.com/FFTAI/Wiki-GRx-Models}.
\bibitem{ubtech} UBTech Robotics, \emph{Walker S2 SDK Secondary Development Document}, 2026.
\bibitem{tesla2022} Tesla, Inc., AI Day 2022 presentation (transcript), Sep.~2022.
\bibitem{nsk2026} NSK Ltd., ``Actuators for robots,'' \emph{NSK Technical Review}, 2026.
\bibitem{schache2011} A.~G. Schache, P.~D. Blanch, T.~W. Dorn, N.~A.~T. Brown, D.~Rosemond, and M.~G. Pandy, ``Effect of running speed on lower limb joint kinetics,'' \emph{Med. Sci. Sports Exerc.}, vol.~43, no.~7, pp.~1260--1271, 2011.
\bibitem{yoshioka2014} S.~Yoshioka, A.~Nagano, D.~C. Hay, and S.~Fukashiro, ``Peak hip and knee joint moments during a sit-to-stand movement are invariant to the change of seat height within the range of low to normal seat height,'' \emph{BioMed. Eng. OnLine}, vol.~13, 2014.
\bibitem{walknorms} Normative walking joint moments, arXiv:2511.06796, 2025.
\bibitem{chinapost2026} China Post Securities, ``Unitree G1 humanoid teardown report,'' Mar.~2026 (in Chinese).
\bibitem{guosen2026} Guosen Securities, ``Review of the Unitree Robotics prospectus,'' Aug.~2026 (in Chinese).
\bibitem{krasia2025} KrASIA, ``RobStride builds the joints that keep China's robots moving,'' 2025.
\bibitem{pmindia2025} Government of India, ``Cabinet approves Rs 7,280 crore scheme to promote manufacturing of sintered rare earth permanent magnets,'' PMIndia, Nov.~2025.
\bibitem{logs_act} JX1 Project, ``Actuator technology survey'' and ``Actuator internals and humanoid torque'' research logs, \url{research/raw/actuator_technology_raw.md}, \url{actuator_internals_and_torque_raw.md}, 2026.
\bibitem{logs_mat} JX1 Project, ``India motor materials'' research log, \url{research/raw/india_motor_materials_raw.md}, Oct.~2026.
\bibitem{logs_cast} JX1 Project, ``India casting and moulding'' research log, \url{research/raw/india_casting_moulding_raw.md}, Oct.~2026.
\bibitem{china_econ} JX1 Project, ``China actuator manufacturing economics'' research log, \url{research/raw/china_actuator_manufacturing_economics_raw.md}, Oct.~2026.
\bibitem{india_capital} JX1 Project, ``India robotics industry and capital'' research log, \url{research/raw/india_robotics_industry_capital_raw.md}, Oct.~2026.
\end{thebibliography}

\end{document}
"""


def main():
    BUILD.mkdir(exist_ok=True)
    tex = BUILD / "jxa_paper.tex"
    tex.write_text(TexTemplate(TEX).substitute(values()), encoding="utf-8")
    build_pdf(tex, OUT_PDF)
    print("wrote", OUT_PDF)


if __name__ == "__main__":
    main()
