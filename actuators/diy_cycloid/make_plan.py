"""Build the JXC-5010 design and build plan as an IEEE-style research paper (LaTeX, IEEEtran).

Numbers come from results/jxc5010.json (run cycloid_actuator.py first).
Usage: python actuators/diy_cycloid/make_plan.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "inhouse"))
from latex_tools import TexTemplate, build_pdf, num  # noqa: E402

R = json.loads((HERE / "results" / "jxc5010.json").read_text())
BUILD = HERE / ".plan_build"
OUT_PDF = HERE / "JXC5010_cycloidal_actuator_build_plan.pdf"

# bill of materials (INR, incl. GST where known). Sources: research/raw/india_*_raw.md; E = estimate, to confirm
BOM = [
    ("Motor", "5010 360KV outrunner (Robu SKU 45571)", 1, 2239, "your pick; keep it"),
    ("Driver", "ST B-G431B-ESC1 (STM32G431, 40\\,A peak, CAN, USB ST-Link)", 1, 2800, "E: US\\$18.59 at ST eStore + shipping/duty"),
    ("Encoder", "MT6701 14-bit magnetic encoder module", 1, 760, "E: Ubuy 2 for INR~1,525; AS5600 (12-bit) is the budget fallback"),
    ("Encoder magnet", "6$\\times$2.5\\,mm diametric NdFeB", 2, 40, "E"),
    ("Output bearing", "6810-2RS (50$\\times$65$\\times$7), FBJ", 1, 470, "bearinghouse.in"),
    ("Eccentric bearings", "6803-2RS (17$\\times$26$\\times$5)", 2, 100, "E"),
    ("Output rollers", "MR74ZZ (4$\\times$7$\\times$2.5), 2 per pin per disc", 24, 30, "E"),
    ("Ring pins", "\\O{}4$\\times$20 steel dowel, pack of 100 (use 21)", 1, 624, "IndustryBuying (CE)"),
    ("Output pins", "\\O{}4$\\times$30 dowel or \\O{}4 silver-steel rod cut to 29\\,mm", 6, 25, "E"),
    ("Fasteners", "6$\\times$ M3$\\times$65 + nuts, M3$\\times$8, M3 heat-set inserts", 1, 300, "E"),
    ("Filament", "$\\approx$180\\,g PLA+ (v0) / PETG-CF or PA-CF (v1)", 1, 250, "INR~700--4,800/kg"),
    ("Grease", "lithium or PTFE grease", 1, 200, "E"),
    ("Power", "24\\,V 10\\,A supply (or a 6S LiPo you have)", 1, 1200, "E; current-limited bench supply preferred"),
]


def bom_rows():
    rows, tot = [], 0
    for item, desc, q, unit, src in BOM:
        line = q * unit; tot += line
        rows.append(f"{item} & {desc} & {q} & {num(unit)} & {num(line)} & {src} \\\\")
    return "\n".join(rows), tot


def opt_rows():
    out = []
    for o in R["options"]:
        pk = min(o["peak_Nm_motor_limited"], R["gear_limit_Nm"])
        lim = "$^\\ast$" if o["peak_Nm_motor_limited"] > R["gear_limit_Nm"] else ""
        motor = o["motor"].replace(" (Robu, your pick)", "$^\\dagger$").replace(" (Robu)", "")
        drv = o["driver"].replace(" (your pick)", "$^\\dagger$")
        out.append(f"{motor} & {drv} & {o['kt']:.3f} & {o['i_peak']:.1f} & {pk:.1f}{lim} & {min(o['cont_Nm'], R['gear_cont_Nm']):.1f} & "
                   f"{o['noload_rad_s']:.0f} & {num(o['price_motor_driver'])} \\\\")
    return "\n".join(out)


def check_rows():
    ck = R["checks"]
    T = list(ck.keys())
    def row(label, f):
        return label + " & " + " & ".join(f(ck[t]) for t in T) + r" \\"
    return "\n".join([
        row("Torque per disc [N$\\cdot$m]", lambda c: f"{c['torque_per_disc_Nm']:.1f}"),
        row("Max ring-pin force [N]", lambda c: f"{c['ring_pin_force_max_N']:.0f}"),
        row("Max output-pin force [N]", lambda c: f"{c['output_pin_force_max_N']:.0f}"),
        row("Ring-pin contact, PLA/PETG [MPa]", lambda c: f"{c['contact_pressure_ring_pin_MPa']['PLA/PETG']:.0f}"),
        row("Ring-pin contact, PA-CF [MPa]", lambda c: f"{c['contact_pressure_ring_pin_MPa']['PA-CF']:.0f}"),
        row("Output-roller contact, PLA/PETG [MPa]", lambda c: f"{c['contact_pressure_output_roller_MPa']['PLA/PETG']:.0f}"),
        row("Output-pin bending [MPa]", lambda c: f"{c['output_pin_bending_MPa']:.0f}"),
    ]), T


def values():
    c = R["cycloid"]; ck = R["checks"]["8.0"] if "8.0" in R["checks"] else list(R["checks"].values())[1]
    bom, tot = bom_rows()
    chk, T = check_rows()
    mini = next(o for o in R["options"] if "SimpleFOCmini" in o["driver"] and "360KV" in o["motor"])
    esc = next(o for o in R["options"] if "B-G431" in o["driver"] and "360KV" in o["motor"])
    return {
        "date": "October 2026", "ratio": f"{R['ratio']}", "npins": f"{c['n_pins']}", "rpc": f"{c['r_pin_circle']:.0f}",
        "dpin": f"{c['d_pin']:.0f}", "ecc": f"{c['ecc']}", "disc_t": f"{c['disc_t']:.0f}", "nout": f"{c['n_out']}", "rout": f"{c['r_out']:.0f}",
        "hod": f"{c['housing_od']:.0f}", "clear": f"{c['clearance']}",
        "lam": f"{ck['lambda_short_amplitude']:.2f}", "rconc": f"{ck['min_concave_radius_mm']:.1f}",
        "rmax": f"{ck['disc_r_max_mm']:.1f}", "rmin": f"{ck['disc_r_min_mm']:.1f}", "hole": f"{ck['output_hole_d_mm']:.1f}",
        "wall_in": f"{ck['wall_hole_to_bore_mm']:.1f}", "wall_out": f"{ck['wall_hole_to_root_mm']:.1f}", "pitch": f"{ck['pin_pitch_mm']:.1f}",
        "mini_pk": f"{mini['peak_Nm_motor_limited']:.1f}", "esc_pk": f"{esc['peak_Nm_motor_limited']:.1f}",
        "esc_ct": f"{min(esc['cont_Nm'], R['gear_cont_Nm']):.1f}", "w0": f"{esc['noload_rad_s']:.0f}",
        "kt": f"{esc['kt']:.3f}", "gear_pk": f"{R['gear_limit_Nm']:.0f}", "gear_ct": f"{R['gear_cont_Nm']:.0f}",
        "bom_rows": bom, "bom_total": num(tot), "opt_rows": opt_rows(), "chk_rows": chk,
        "chk_head": " & ".join(f"{float(t):.0f}\\,N$\\cdot$m" for t in T),
        "cad_pcd": f"{R['cad']['motor_bolt_pcd_assumed_mm']:.0f}", "prop_pcd": f"{R['cad']['prop_pcd_assumed_mm']:.0f}",
    }


TEX = r"""
\documentclass[journal,10pt]{IEEEtran}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{array}
\usepackage{cite}
\usepackage{url}
\usepackage[hidelinks]{hyperref}
\usepackage{balance}
\renewcommand{\arraystretch}{1.12}
\newcolumntype{L}{>{\raggedright\arraybackslash}X}
\graphicspath{{../figures/}}

\begin{document}

\title{JXC-5010: A Low-Cost 3D-Printed Cycloidal Actuator from a Drone Motor --- Design and Build Plan}

\author{JX1~Humanoid~Project%
\thanks{Prepared @@date. Design script, print files and this plan are in \texttt{actuators/diy\_cycloid/} of the
\texttt{thenar-jx1} repository. All performance values are calculated and must be confirmed on the bench (Section~IX).}}

\markboth{JX1 Humanoid Project Technical Note, @@date}{JXC-5010 3D-Printed Cycloidal Actuator}

\maketitle

\begin{abstract}
We design a 3D-printable joint actuator around the low-cost parts initially proposed: a 5010 360\,KV drone motor and a SimpleFOCmini
driver. Analysis shows the driver's 2.5\,A limit caps output torque at about @@mini_pk\,N$\cdot$m regardless of the gearbox, so we
replace it with the ST B-G431B-ESC1 (40\,A peak, CAN, about US\$19), which lifts the motor-limited torque to @@esc_pk\,N$\cdot$m.
Comparing cycloidal, strain-wave and planetary reducers for fused-filament printing, we select a single-stage, dual-disc cycloidal
reducer of @@ratio:1 with @@npins steel ring pins and rolling output pins. Stress checks show that the printed discs, not the motor,
limit the actuator to about @@gear_pk\,N$\cdot$m peak and @@gear_ct\,N$\cdot$m continuous, so a costlier motor adds little at this size.
The resulting JXC-5010 (\O{}@@hod$\times$64\,mm, about 0.46\,kg) delivers about 8\,N$\cdot$m peak, 4\,N$\cdot$m continuous and
@@w0\,rad/s no-load at 24\,V for about INR~@@bom_total in parts. We provide printable STL/DXF files, a bill of materials, print settings,
an assembly sequence, firmware steps and a test plan.
\end{abstract}

\begin{IEEEkeywords}
Cycloidal drive, 3D printing, quasi-direct drive, BLDC, field-oriented control, low-cost robotics.
\end{IEEEkeywords}

\section{Goal and Starting Point}
\IEEEPARstart{T}{he} goal is the highest-torque joint actuator that can be prototyped by fused-filament (FDM) printing at roughly the cost of
the parts initially chosen: a generic 5010 360\,KV outrunner (INR~2,239) and a SimpleFOCmini driver (INR~729). The design follows the
open-source Berkeley Humanoid Lite (BHL) actuators, which walk a 16\,kg humanoid on printed 15:1 cycloidal gearboxes driven by 5010 and
6512 drone motors~\cite{bhl2025}.

\section{Component Selection}
\subsection{The driver is the bottleneck}
A motor's torque constant can be estimated from its KV rating as $K_t \approx 8.27/K_V$\,N$\cdot$m/A, so the 5010 360\,KV gives about
@@kt\,N$\cdot$m/A (measure it; Section~IX). The output torque of a geared actuator is
\begin{equation}
T_\mathrm{out} = K_t\, I\, G\, \eta ,
\end{equation}
with current $I$, ratio $G$ and gearbox efficiency $\eta \approx 0.85$. The SimpleFOCmini (DRV8313) delivers only 2.5\,A, so even at
@@ratio:1 the actuator reaches about @@mini_pk\,N$\cdot$m. The motor itself is rated for 20--40\,A drone ESCs; a driver supplying 20\,A
multiplies torque by eight. Table~\ref{tab:opt} compares options. The \textbf{ST B-G431B-ESC1} is chosen: 40\,A peak with forced air
(20\,A without), up to 6S, an STM32G431 with CAN on board, a USB ST-Link for programming, support in the SimpleFOC library and in BHL's
``Recoil'' CAN firmware~\cite{bhl2025,simplefoc}, at about US\$19. It is often out of stock in India (Evelta listed it at INR~2,791);
order from ST's eStore or a global distributor. The Flipsky ODESC~V4.2 (INR~7,350 on Amazon.in) is the in-stock fallback.
The SimpleFOCmini remains useful for learning FOC on the bench or for very light joints with a gimbal motor.

\begin{table*}[!t]
\caption{Motor and driver options with the @@ratio:1 printed cycloid at 24\,V (calculated; $^\dagger$ = initially chosen part)}
\label{tab:opt}
\centering\footnotesize\setlength{\tabcolsep}{4pt}
\begin{tabular}{@{}l l c c c c c r@{}}
\toprule
Motor & Driver & $K_t$ [N$\cdot$m/A] & $I_\mathrm{peak}$ [A] & Peak [N$\cdot$m] & Cont. [N$\cdot$m] & No-load [rad/s] & Motor + driver [INR] \\
\midrule
@@opt_rows
\bottomrule
\end{tabular}\\[2pt]
{\scriptsize $^\ast$Limited by the printed gearbox, not the motor. Continuous torque is also capped at the printed-gear limit.}
\end{table*}

\subsection{The motor}
Keep the 5010 360\,KV. Its high KV is matched by a high ratio (@@ratio:1 still gives @@w0\,rad/s at the joint). A low-KV 5010 such as the
Tarot 130\,KV (INR~4,779) doubles the motor-limited torque at lower current, but Section~IV shows the printed gearbox caps peak torque near
@@gear_pk\,N$\cdot$m, so the upgrade mainly buys cooler running. Spend the money on the driver first.

\subsection{Which gearbox for a printed prototype}
Table~\ref{tab:gear} compares the three reducer types for FDM printing. A strain-wave (harmonic) drive needs a thin, repeatedly flexed
spline: printed in plastic it has low torque and fatigues quickly. Printed planetaries measured 60--80\,\% efficiency and 0.6--2.6$^\circ$
backlash~\cite{compact}, and a single stage reaches only about 6--10:1, too little for a 360\,KV motor. A cycloidal reducer reaches 10--25:1 in
one stage, spreads load over many lobes at once, uses steel pins for every sliding contact, tolerates shock, and has been validated in print:
BHL measured about 90\,\% efficiency, 1.3$^\circ$ backlash and a 60\,h life test~\cite{bhl2025}. \textbf{We choose a cycloidal reducer.}

\begin{table}[!t]
\caption{Reducer types for a 3D-printed prototype}
\label{tab:gear}
\centering\scriptsize
\begin{tabularx}{\columnwidth}{@{}l L L@{}}
\toprule
Type & For printing & Against \\
\midrule
Cycloidal & 10--25:1 in one stage; many lobes share load; steel pins take contact; shock tolerant; proven in PLA (BHL) & eccentric vibration (use two discs at 180$^\circ$); less back-drivable above 20:1 \\
Strain-wave & very low backlash & printed flexspline is weak and fatigues; hard to make \\
Planetary & back-drivable, simple & 60--80\,\% efficient printed; small teeth wear; $\leq$10:1 per stage \\
\bottomrule
\end{tabularx}
\end{table}

\section{Reducer Design}
\subsection{Geometry}
With $N$ ring pins on a circle of radius $R$, pin radius $r$ (plus a fit clearance) and eccentricity $e$, the disc profile is
{\small
\begin{equation}
\begin{aligned}
x(t) &= R\cos t - r\cos(t+\psi) - e\cos(Nt),\\
y(t) &= -R\sin t + r\sin(t+\psi) + e\sin(Nt),\\
\psi &= \operatorname{atan2}\!\big(\sin((1-N)t),\, \tfrac{R}{eN} - \cos((1-N)t)\big),
\end{aligned}
\end{equation}}
which has $N-1$ lobes and gives a reduction $G = N-1$ with the output taken from the disc through pins in oversized holes of diameter
$d_\mathrm{roller} + 2e$. The short-amplitude coefficient $\lambda = eN/R$ must be below 1 to avoid undercut. The chosen geometry is
$N = @@npins$ ($G = @@ratio$), $R = @@rpc$\,mm, \O{}@@dpin\,mm pins, $e = @@ecc$\,mm, $\lambda = @@lam$, two @@disc_t\,mm discs at 180$^\circ$ on a
double eccentric, @@nout output pins on $R_w = @@rout$\,mm with MR74ZZ rollers, and a @@clear\,mm profile clearance for FDM tolerance
(Fig.~\ref{fig:layout}). The disc spans radius @@rmin--@@rmax\,mm, the pin pitch is @@pitch\,mm, the smallest concave profile radius
@@rconc\,mm exceeds the pin radius, and the walls around the \O{}@@hole\,mm output holes are @@wall_in\,mm (to the bearing bore) and @@wall_out\,mm
(to the lobe root).

\begin{figure}[!t]
\centering
\includegraphics[width=0.92\columnwidth]{cycloid_layout.png}
\caption{Cycloidal stage: two discs 180$^\circ$ apart, @@npins ring pins and @@nout output rollers (green).}
\label{fig:layout}
\end{figure}

\subsection{Loads and stresses}
For a dual-disc drive each disc is assumed to carry 55\,\% of the output torque $T_c$. The largest ring-pin and output-pin forces are
\begin{equation}
F_\mathrm{pin} = \frac{4T_c}{e\,N\,(N-1)}, \qquad F_\mathrm{out} = \frac{4T_c}{Z_w R_w},
\end{equation}
and the contact pressure follows from Hertz line contact,
$p = \sqrt{F E^\ast / (\pi b R_\mathrm{eff})}$, with $E^\ast \approx 4$\,GPa for PLA/PETG and 6\,GPa for PA-CF on steel. Table~\ref{tab:chk}
gives the results. Printed PLA yields at about 60--70\,MPa in compression, so the printed discs set a peak limit of about @@gear_pk\,N$\cdot$m;
for long life the continuous torque should stay near @@gear_ct\,N$\cdot$m (contact pressure $\lesssim$45\,MPa). The hardened \O{}4 output
pins see 128--320\,MPa in bending, well within their strength.

\begin{table}[!t]
\caption{Reducer checks at three output torques (calculated)}
\label{tab:chk}
\centering\scriptsize
\begin{tabularx}{\columnwidth}{@{}L r r r@{}}
\toprule
Quantity & @@chk_head \\
\midrule
@@chk_rows
\bottomrule
\end{tabularx}
\end{table}

\section{Mechanical Layout}
Fig.~\ref{fig:section} shows the stack. The motor base bolts to an adapter plate; a spacer ring surrounds the motor; the eccentric cam bolts to
the rotor bell's propeller-mount holes and is centred on the 4\,mm shaft; the ring-pin housing holds 21 pressed \O{}4$\times$20 dowels
half-exposed in grooves; the carrier, with six \O{}4 pins pressed through it, runs in a 6810 bearing held by a retainer ring; six M3 bolts
clamp the stack. The two parts marked ``MEASURE\_FIRST'' assume a @@cad_pcd\,mm motor-base bolt circle and a @@prop_pcd\,mm propeller-mount
circle: measure your motor and change the two parameters in \texttt{cycloid\_actuator.py} before printing. Fig.~\ref{fig:parts} shows the
printed parts.

\begin{figure}[!t]
\centering
\includegraphics[width=0.9\columnwidth]{assembly_section.png}
\caption{JXC-5010 section to scale (\O{}@@hod$\times$64\,mm).}
\label{fig:section}
\end{figure}

\begin{figure*}[!t]
\centering
\includegraphics[width=\textwidth]{printed_parts.png}
\caption{Printed parts generated by the design script (STL and DXF in \texttt{cad/}); spacer and retainer rings not shown.}
\label{fig:parts}
\end{figure*}

\section{Bill of Materials}
Table~\ref{tab:bom} lists the parts, about INR~@@bom_total including a bench supply. Prices marked E are estimates to be confirmed.

\begin{table*}[!t]
\caption{Bill of materials (INR incl.\ GST; E = estimate)}
\label{tab:bom}
\centering\footnotesize
\begin{tabularx}{\textwidth}{@{}l L c r r L@{}}
\toprule
Item & Part & Qty & Unit & Total & Source / note \\
\midrule
@@bom_rows
\midrule
\multicolumn{4}{@{}l}{\textbf{Total}} & \textbf{@@bom_total} & \\
\bottomrule
\end{tabularx}
\end{table*}

\section{Printing}
\begin{itemize}
\item \emph{Test coupon first}: print a 20\,mm block with \O{}3.95/4.0/4.05 holes and a \O{}26 bore; pick the hole size that presses a dowel
in firmly and the bore that holds a 6803 by hand press. Adjust \texttt{d\_pin} offsets and \texttt{clearance} in the script.
\item \emph{v0 (fit and function)}: PLA+, 0.2\,mm layers, 4--5 walls. Discs flat on the bed, 100\,\% infill (they carry the contact load);
housing output-side up, 40\,\% gyroid; carrier and cam 80--100\,\%.
\item \emph{v1 (durable)}: PETG-CF or PA-CF for discs and cam (higher temperature and stiffness; PA-CF needs a hardened nozzle and dry
filament). Keep PLA away from the motor, which can exceed PLA's 55\,$^\circ$C softening point.
\item Disable elephant-foot on the discs (or chamfer 0.3\,mm); remove all stringing in the holes; dry-fit before greasing.
\end{itemize}

\section{Assembly}
\begin{enumerate}
\item Press the 21 ring pins into the housing (vise, parallel jaws); check that all protrude equally.
\item Press a 6803 bearing into each disc; press the six \O{}4 pins through the carrier; slide two MR74ZZ rollers per disc onto each pin.
\item Bolt the motor to the adapter plate; fit the spacer ring. Glue the diametric magnet to the motor's rear shaft end; mount the encoder
1--2\,mm below it on a printed bracket.
\item Bolt the eccentric cam to the rotor bell; check run-out by eye while spinning slowly.
\item Grease the pins. Fit the housing; drop disc~1 onto the lower journal, then disc~2 rotated 180$^\circ$ onto the upper journal, rotating
the motor slowly until each disc meshes.
\item Insert the carrier pins through both discs; press the 6810 bearing over the carrier hub into the housing seat; fit the retainer and
the six M3 through-bolts. Turn the output by hand: it should rotate the motor 20 times per turn without binding.
\end{enumerate}

\section{Electronics and Firmware}
Power the B-G431B-ESC1 from a current-limited 24\,V supply (start at 3\,A). Wire the motor phases and the MT6701 (ABZ or SSI) or AS5600 (I$^2$C)
encoder. Program it over its USB ST-Link with the Arduino IDE (STM32duino core) and the SimpleFOC library: (1)~open-loop velocity to confirm
the phases; (2)~sensor alignment and pole-pair check (7 pole pairs for a 12N14P motor); (3)~torque (current) mode with a 3\,A limit; (4)~velocity
and position loops; (5)~raise the current limit in steps to 20\,A while watching temperature. For a robot, move to BHL's Recoil firmware for
CAN control and add an output-side encoder or homing switch, since a 20:1 stage makes the motor encoder ambiguous after power-up.

\section{Test Plan and Expected Results}
\begin{itemize}
\item \emph{$K_t$}: lock the output with a 100\,mm lever on a kitchen scale; step current to 2, 4, 8\,A; $K_t = T/(I\,G\,\eta)$. Update the script.
\item \emph{Peak torque}: step to 20\,A for 2\,s; expect $\approx$@@esc_pk\,N$\cdot$m. Stop if the discs creak or the scale reading drops.
\item \emph{Backlash}: lock the motor, rock the output with a 200\,mm arm and a dial gauge (BHL: 1.3$^\circ$ max).
\item \emph{Thermal}: 30\,min at 3--4\,N$\cdot$m; motor below 80\,$^\circ$C, housing below 50\,$^\circ$C (PLA).
\item \emph{Life}: replay a sinusoidal 0--4\,N$\cdot$m load for 20\,h; recheck backlash and efficiency every 4\,h.
\end{itemize}
Expected: about @@esc_pk\,N$\cdot$m peak (2--3\,s), @@esc_ct\,N$\cdot$m continuous, @@w0\,rad/s no-load at 24\,V, about 0.46\,kg.

\section{Upgrade Path}
Beyond about @@gear_pk\,N$\cdot$m the printed discs are the limit. Next steps in order of cost: print discs in PA-CF; have the discs laser-cut
from 3\,mm steel or 6\,mm aluminium (the DXF in \texttt{cad/} is ready for a laser shop); scale the stage to $R \approx 40$\,mm with a 6012 or
8108-class motor for 20--30\,N$\cdot$m, the size of JX1's ankle and hip-yaw joints; or move to the JXA family of the companion paper~\cite{jxa}.

\section{Conclusion}
The initially chosen motor is adequate; the driver is not. With a B-G431B-ESC1 and a printed @@ratio:1 dual-disc cycloid, the 5010 360\,KV
makes an actuator of about 8\,N$\cdot$m peak for roughly the price of a single hobby servo-class joint, limited by the printed discs. All files to
print, assemble and test it are provided.

\balance
\begin{thebibliography}{9}
\footnotesize
\bibitem{bhl2025} Q.~Liao \emph{et~al.}, ``Berkeley Humanoid Lite: An open-source, accessible, and customizable 3D-printed humanoid robot,'' arXiv:2504.17249, 2025.
\bibitem{simplefoc} A.~Skuric, H.~S. Bank, R.~Unger, O.~Williams, and D.~Gonz\'{a}lez-Reyes, ``SimpleFOC: A field oriented control (FOC) library for controlling brushless direct current (BLDC) and stepper motors,'' \emph{J. Open Source Softw.}, vol.~7, no.~74, p.~4232, 2022.
\bibitem{compact} COMPAct: open-source printed planetary actuators (IISc / ARTPARK), summarised in \texttt{research/raw/actuator\_technology\_raw.md}, \S3.
\bibitem{blanche1989} J.~G. Blanche and D.~C.~H. Yang, ``Cycloid drives with machining tolerances,'' \emph{J. Mech. Transm. Autom. Des.}, vol.~111, no.~3, pp.~337--344, 1989.
\bibitem{stm} STMicroelectronics, ``B-G431B-ESC1 Discovery kit,'' user manual UM2516.
\bibitem{jxa} JX1 Humanoid Project, ``Design and techno-economic analysis of in-house quasi-direct-drive actuators for humanoid robots in India,'' Oct.~2026.
\end{thebibliography}

\end{document}
"""


def main():
    BUILD.mkdir(exist_ok=True)
    tex = BUILD / "jxc5010_plan.tex"
    tex.write_text(TexTemplate(TEX).substitute(values()), encoding="utf-8")
    build_pdf(tex, OUT_PDF)
    print("wrote", OUT_PDF)


if __name__ == "__main__":
    main()
