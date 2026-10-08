"""Build the business paper as an IEEE-style two-column research paper (LaTeX, IEEEtran).

'Humanoid-Robot Actuators as a Manufacturing Business in India: Market Outlook to 2035, Copper Demand,
Manufacturing Economics and a Go-to-Market Strategy'

Numbers come from business/results/business_model.json, actuators/inhouse/results/cost.json and the research logs in
research/raw/ (evidence labels VERIFIED / ESTIMATED / UNVERIFIED are kept there).
Usage: python business/make_business_report.py   (run business/actuator_business_model.py first)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "actuators" / "inhouse"))
from latex_tools import TexTemplate, build_pdf, crore, esc, inr, lakh, num  # noqa: E402

BUILD = HERE / ".report_build"
OUT_PDF = HERE / "Actuator_business_report_India.pdf"
B = json.loads((HERE / "results" / "business_model.json").read_text())
C = json.loads((ROOT / "actuators" / "inhouse" / "results" / "cost.json").read_text())
USD = C["assumptions"]["INR_USD"]


def stage_rows() -> str:
    out = []
    for s in B["stages"]:
        gm = f"{s['gross_margin'] * 100:.0f}\\,\\%" if s["gross_margin"] is not None else "--"
        out.append(f"{esc(s['name'])} & {s['months']} & {num(s['units'])} & {num(s['asp']) if s['asp'] else '--'} & {num(s['unit_cost'])} & {gm} & "
                   f"{s['revenue_per_yr'] / 1e7:,.1f} & {s['opex_per_yr'] / 1e7:,.1f} & {s['ebitda_per_yr'] / 1e7:,.1f} & {s['capex'] / 1e7:,.1f} & "
                   f"\\textbf{{{s['capital_to_raise'] / 1e7:,.1f}}} \\\\")
    return "\n".join(out)


def mc_rows() -> str:
    out = []
    for m in B["mc_check"]["for_10bn_market_cap"]:
        sh = list(m["share_needed"].values())
        out.append(f"{m['ev_to_sales']}$\\times$ & {m['revenue_needed_usd'] / 1e9:.1f} & {m['actuators_per_year_at_usd250'] / 1e6:.0f} & "
                   f"{sh[0] * 100:.0f}\\,\\% & {sh[1] * 100:.1f}\\,\\% & {sh[2] * 100:.1f}\\,\\% \\\\")
    return "\n".join(out)


def values() -> dict:
    s = B["stages"]
    a = B["assumptions"]
    one = B["mc_check"]["one_percent_of_2030_market"]
    s3 = s[3]
    return {
        "date": "October 2026",
        "stage_rows": stage_rows(), "mc_rows": mc_rows(),
        "total_cap": crore(B["total_capital_all_stages"]), "total_cap_usd": f"{B['total_capital_all_stages'] / USD / 1e6:.0f}",
        "one_rev": f"{one['revenue_usd'] / 1e6:,.0f}", "one_mc": f"{one['market_cap_at_4x_usd'] / 1e6:,.0f}",
        "lr": f"{B['learning_rate_per_doubling']:.2f}",
        "inv": f"{a['inventory_days']}", "rec": f"{a['receivable_days']}", "pay": f"{a['payable_days']}",
        "takt": f"{a['takt_s']}", "oee": f"{a['oee']:.2f}", "line_cap": f"{a['shift_seconds_per_year'] * a['oee'] / a['takt_s']:,.0f}",
        "s1_raise": crore(s[1]["capital_to_raise"]), "s2_raise": crore(s[2]["capital_to_raise"]), "s3_raise": crore(s3["capital_to_raise"]),
        "s1_be": f"{s[1]['breakeven_units']:,.0f}", "s1_units": num(s[1]["units"]), "s2_units": num(s[2]["units"]), "s3_units": num(s3["units"]),
        "s3_gm": f"{s3['gross_margin'] * 100:.0f}", "s3_gm_war": f"{(15000 - s3['unit_cost']) / 15000 * 100:.0f}",
        "s3_rev": crore(s3["revenue_per_yr"]), "s3_rev_usd": f"{s3['revenue_per_yr'] / USD / 1e6:.0f}",
        "s3_mc_lo": f"{2 * s3['revenue_per_yr'] / USD / 1e6:.0f}", "s3_mc_hi": f"{4 * s3['revenue_per_yr'] / USD / 1e6:.0f}",
        "cogs120": inr(C["classes"]["JXA-120"]["buy"]["china_cogs"]["central"]),
        "cn120": inr(C["classes"]["JXA-120"]["buy"]["china_distributor"]),
        "nre_ab": lakh(C["nre"]["P"]["total"] + C["nre"]["B"]["total"]), "nre_p": lakh(C["nre"]["P"]["total"]),
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
\graphicspath{{../figures/}{../../actuators/inhouse/figures/}}
\hyphenation{Rob-Stride Uni-tree}

\begin{document}

\title{Humanoid-Robot Actuators as a Manufacturing Business in India: Market Outlook to 2035, Copper Demand, Manufacturing
Economics and a Go-to-Market Strategy}

\author{JX1~Humanoid~Project%
\thanks{Manuscript prepared @@date as part of the open-source \texttt{thenar-jx1} repository
(\url{https://github.com/nickthelegend/thenar-jx1}). The business model is \texttt{business/actuator\_business\_model.py}; source data with
evidence labels are in \texttt{research/raw/}. Forecasts are scenarios, not predictions, and nothing here is investment advice.}}

\markboth{JX1 Humanoid Project Technical Report, @@date}{Humanoid-Robot Actuators as a Manufacturing Business in India}

\maketitle

\begin{abstract}
Every humanoid robot needs 20--40 joint actuators, which make up about half of its bill of materials. This paper evaluates an Indian
company that would manufacture such actuators. Combining bank forecasts, industry statistics and a bottom-up cost model, we find that the
humanoid-actuator market grows from about US\$0.23\,bn in 2025 to US\$8--14\,bn in 2030 and US\$10--90\,bn in 2035, and that India, which installs
about 10{,}000 industrial robots a year, has no volume producer of robot-class actuators. Copper, often cited as the metal of the robot boom, is
not a material driver: a humanoid holds about 6--8\,kg, and humanoids remain below 0.1\,\% of world copper demand in 2030. We formalise the planning
equations of an actuator plant (margin, break-even, learning curve, takt capacity, working capital, capital requirement and valuation), and apply
them to a four-stage plan from a garage to a 60{,}000-unit-per-year plant, which needs about @@total_cap (US\$@@total_cap_usd\,M) of external capital
and reaches about @@s3_rev of yearly revenue. We conclude that the business is viable if it targets buyers that value trust, service and
customisation over price, earns revenue first as an integrator, and scales tooling only against signed orders. A US\$10\,bn outcome would
require about a quarter of the entire 2030 actuator market.
\end{abstract}

\begin{IEEEkeywords}
Humanoid robots, actuators, market analysis, copper demand, manufacturing economics, learning curve, venture capital, go-to-market, India.
\end{IEEEkeywords}

\section{Introduction}
\IEEEPARstart{H}{umanoid} robots went from a few hundred units in 2023 to 13{,}000--20{,}000 in 2025, almost all built in China~\cite{bofa2026,logs_mkt}.
Their cost is dominated by actuators, and Chinese actuator makers (RobStride, Encos, Unitree) already produce 50{,}000--500{,}000 joints a year at about
CNY~1{,}000 each~\cite{logs_cn}. A companion paper~\cite{jxa_paper} showed that an Indian builder can design and make RobStride-class actuators,
but not more cheaply at small volume. This paper asks the business questions that follow:
\begin{enumerate}
\item How large is the actuator market, and how fast does it grow?
\item Does the robot boom make copper the key material, and does copper matter to an actuator maker?
\item Who makes actuators in India, and how are such plants built and financed?
\item What capital does an Indian actuator company need, what is it plausibly worth, and how should it enter the market?
\end{enumerate}

\section{Market Outlook}
\subsection{Humanoids}
Table~\ref{tab:forecast} summarises published forecasts. Estimates for 2035 differ by about $5\times$ and every bank raised its forecast in the
last year. In BofA's 2030 bill of materials, rotary and linear actuators are 51\,\% of a humanoid's cost (dexterous hands a further 19\,\%)~\cite{bofa2026},
so the actuator market follows as
\begin{equation}
M_\mathrm{act} = N_\mathrm{robots} \cdot C_\mathrm{BOM} \cdot s_\mathrm{act},
\end{equation}
giving about US\$0.23\,bn in 2025 (13k\,$\times$\,US\$35k\,$\times$\,0.51), US\$10.4\,bn in 2030 (1.2\,M\,$\times$\,US\$17k\,$\times$\,0.51)
and US\$41--87\,bn in 2035 depending on the source.

\begin{table}[!t]
\caption{Humanoid forecasts}
\label{tab:forecast}
\centering\scriptsize
\begin{tabularx}{\columnwidth}{@{}L l l l@{}}
\toprule
Source & 2030 & 2035 & Long run \\
\midrule
BofA Institute, Mar.~2026~\cite{bofa2026} & 1.2\,M/yr & 10\,M/yr & 3\,bn in use (2060) \\
Goldman Sachs, Sep.~2026$^\dagger$ & 0.89\,M & 6.5\,M; US\$138\,bn & -- \\
Morgan Stanley$^\dagger$ & US\$28\,bn & 13\,M in use & US\$5\,trn (2050) \\
UBS$^\dagger$ & -- & US\$30--50\,bn & 300\,M (2050) \\
Citi GPS, Nov.~2024~\cite{citi2024} & -- & -- & US\$7\,trn (2050) \\
\bottomrule
\end{tabularx}\\[2pt]
{\scriptsize $^\dagger$From press coverage; original notes paywalled~\cite{logs_mkt}.}
\end{table}

\subsection{Industrial robots and India}
More than 600{,}000 industrial robots were installed worldwide in 2025, 59\,\% of them in China, and IFR expects 806{,}000 in 2029~\cite{ifr2026}.
India installed about 9{,}000--10{,}500 (sixth in the world), which corresponds to about 55{,}000 servo joints a year, all imported~\cite{logs_india}.
Domestic humanoid demand to 2030 is likely in the thousands of units (Addverb targets 3{,}000 installations; MeitY announced a INR~500~crore humanoid
fund in June 2026), so an Indian actuator company needs export and non-humanoid volume from the start.

\section{Copper Demand}
World refined-copper demand was about 28\,Mt in 2025 and is projected at 42\,Mt in 2040, with supply peaking near 33\,Mt in 2030 and a shortfall of
about 25\,\% by 2040~\cite{sp2026}. The share of demand attributable to humanoids is
\begin{equation}
s_\mathrm{Cu} = \frac{N_\mathrm{robots}\, m_\mathrm{Cu}}{D_\mathrm{world}},
\end{equation}
with $m_\mathrm{Cu} \approx 6$--8\,kg per humanoid (windings 2--7\,kg, harness, boards, battery), consistent with CRU (4--8\,kg) and Morgan Stanley
(4.5--8.5\,kg) estimates~\cite{logs_mkt}. Table~\ref{tab:cu} gives the result: 0.02--0.08\,\% in 2030 and 0.14--0.33\,\% in 2035, compared with
about 6\,\% for electric vehicles (83\,kg each) and a growing share for AI data centres (20--40\,t/MW). Copper prices are near record levels
(about US\$14{,}500/t, +30\,\% year on year) for reasons unrelated to robots. For an actuator maker copper is a minor cost: a JXA-120 contains
about 0.1\,kg of winding wire, so a 30\,\% copper price rise adds about INR~75 per unit, whereas a magnet export restriction can halt production.

\begin{table}[!t]
\caption{Copper intensity and humanoids' share of demand (estimated)}
\label{tab:cu}
\centering\scriptsize
\begin{tabularx}{\columnwidth}{@{}L r@{}}
\toprule
Item & Value \\
\midrule
World refined demand 2025 / 2030 / 2040 & 28 / $\approx$32 / 42\,Mt \\
Copper per battery EV / per MW data centre & 83\,kg / 20--40\,t \\
Copper per humanoid & 6--8\,kg ($\approx$US\$115) \\
Copper in one 120\,N$\cdot$m actuator & $\approx$0.1\,kg \\
Humanoid share of demand, 2030 & 0.02--0.08\,\% \\
Humanoid share of demand, 2035 & 0.14--0.33\,\% \\
Humanoid share with 1\,bn robots in use (2040+) & $\approx$4\,\% \\
\bottomrule
\end{tabularx}
\end{table}

\section{Software and Hardware Labour to 2030}
Evidence to date shows AI compressing entry-level programming rather than software work as a whole: employment of US developers aged 22--25 fell
by about 20\,\% after 2024 while older developers grew 6--12\,\%~\cite{aiindex2026}, young workers in AI-exposed occupations sit 19\,\% below trend
through reduced hiring~\cite{brynjolfsson2026}, yet the BLS projects software-developer employment to grow 15.8\,\% over 2024--34 while ``computer
programmers'' decline 6\,\%~\cite{bls2025}. Robots displace physical work slowly: one additional robot per 1{,}000 workers lowers the
employment-to-population ratio by about 0.2 percentage points~\cite{acemoglu2020}. Actuator products are roughly half electromechanical and half
software (field-oriented control, calibration, simulation models), so a founder combining software with manufacturing know-how holds a durable
position.

\section{The Indian Actuator Landscape}
Table~\ref{tab:india} lists Indian firms relevant to robot actuation. No Indian company produces RobStride-class actuators at volume and no Indian
harmonic-reducer maker was found; startups build quasi-direct-drive joints by hand in tens to hundreds, and others import. India does, however,
have the adjacent capabilities at scale: drone motors (Vector Technics, 300{,}000 units/yr with in-house winding), EV traction and hub motors
(Sona Comstar, Lucas TVS, Chara), BLDC fan motors (Atomberg, millions per year) and lamination stamping (Pitti Engineering, 90{,}000\,t/yr).
Relevant manufacturing clusters are Coimbatore (motors, winding), Rajkot (CNC, shafts), Pune--Chakan (gears), Bengaluru Peenya (aerospace
machining), Hyderabad (drone motors, laminations, defence) and Chennai--Hosur (drives, EV motors).

\begin{table*}[!t]
\caption{Indian actuator and motor landscape (press and company sources; most funding figures unverified)~\cite{logs_india}}
\label{tab:india}
\centering\scriptsize
\begin{tabularx}{\textwidth}{@{}l L L L@{}}
\toprule
Company & Product & Manufacturing approach & Scale / funding \\
\midrule
xTerra Robotics (Kanpur/Bengaluru) & QDD A2: 12\,N$\cdot$m, 550\,g, INR~94,400 & parts from aerospace job shops, in-house assembly & $\approx$15 staff, $\approx$INR~1\,crore revenue, grants \\
Bhairav Robotics (Kakinada) & ``Prabal'' QDD, quadrupeds, UGVs & in-house & Zen Technologies acquired 45\,\% for $\approx$INR~4\,crore \\
Perceptyne (Hyderabad) & dual-arm semi-humanoid, own actuators & in-house & US\$3\,M seed (Endiya, Yali), 2024 \\
Addverb (Noida; Reliance) & wheeled humanoid ($\approx$US\$45k), BLDC + planetary joints & undisclosed & FY25 revenue INR~800\,crore; INR~75\,crore plant for 60k robots/yr \\
General Autonomy (Bengaluru) & Atom~01 humanoid, quadruped & imports actuators & seed INR~32\,crore at INR~280\,crore valuation \\
Vector Technics (Hyderabad) & drone propulsion motors & own winding and machining, 300k/yr & Zen paid $\approx$INR~25\,crore for 51\,\% \\
Sona Comstar / Lucas TVS / Chara & EV traction and hub motors & automated winding and stamping & INR~99.7\,crore for 200k motors/yr (Sona) \\
Atomberg; Pitti Engineering & BLDC fans; laminations & mass stamping and winding & 6.6\,M units/yr; 90k\,t/yr \\
\bottomrule
\end{tabularx}
\end{table*}

\section{Manufacturing Architectures and Planning Equations}
\subsection{Architectures}
Three architectures are observed. (A)~\emph{Design and assembly house}: design, winding, assembly, calibration and test in-house; all parts from job
shops; 100--3{,}000 units/yr; equipment about @@nre_ab (the kits in~\cite{jxa_paper}). (B)~\emph{Partly integrated}: adds automated needle
winding, magnet bonding, gear finishing and end-of-line test; 3{,}000--30{,}000 units/yr; about INR~1--3~crore for 10{,}000/yr. (C)~\emph{Volume
plant}: adds stamping, die casting, gear hobbing or powder metallurgy and automated lines; 50{,}000--1{,}000{,}000 units/yr; INR~20--100+~crore
(a single Chinese joint-module line is reported at CNY~110\,M~\cite{logs_cn}). The process flow is: incoming inspection, lamination stack,
insulation, needle winding, termination, hipot test, impregnation, rotor bonding and balancing, gear stage, cast-and-machined housing, final
assembly, firmware and encoder calibration, end-of-line test (back-EMF, $K_t$, cogging, thermal, backlash), burn-in and packing. Chinese benchmarks
are 90\,s per joint and over 96\,\% first-pass yield.

\subsection{Planning equations}
With price $P$, unit cost $C$, variable cost $V$ and fixed cost $F$ per year, gross margin and break-even volume are
\begin{equation}
\mathrm{GM} = \frac{P - C}{P}, \qquad N^\ast = \frac{F}{P - V}.
\end{equation}
Unit cost falls with cumulative volume according to Wright's law~\cite{wright1936},
\begin{equation}
C(N) = C_1 N^{\log_2 r},
\end{equation}
where $r$ is the cost ratio per doubling; our cost model gives $r \approx @@lr$ between 25 and 1{,}000 units per year. Line capacity follows from the
takt time $t_\mathrm{takt}$ and overall equipment effectiveness (OEE),
\begin{equation}
N_\mathrm{line} = \frac{t_\mathrm{avail}\,\mathrm{OEE}}{t_\mathrm{takt}},
\end{equation}
so one line at a @@takt\,s takt, two shifts over 300 days and OEE of @@oee makes about @@line_cap actuators a year: capacity is not the constraint;
demand, cost and quality are. Working capital and the capital to raise for a stage are
\begin{align}
\mathrm{WC} &= \frac{\mathrm{COGS}}{365}\,(d_\mathrm{inv} + d_\mathrm{rec} - d_\mathrm{pay}),\\
K &= \mathrm{CAPEX} + \textstyle\sum \text{operating losses} + \mathrm{WC} + 0.5\,\mathrm{OPEX},
\end{align}
with $d_\mathrm{inv} = @@inv$, $d_\mathrm{rec} = @@rec$ and $d_\mathrm{pay} = @@pay$ days, inventory being long because magnets and bearings are imported.
Finally, valuation follows revenue:
\begin{equation}
\mathrm{MC} = m \cdot R, \qquad R = N_\mathrm{robots}\, n_\mathrm{act}\, s\, P ,
\end{equation}
with EV/sales multiple $m$, $n_\mathrm{act}$ actuators per robot and market share $s$.

\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{learning_curve.png}
\caption{JXA-120 direct cost versus yearly volume (estimated). Cost falls steeply up to about 1{,}000 units/yr as job shops are replaced by own
tooling, then is floored at the Chinese manufacturer's estimated cost, because magnets, bearings and chips cost everyone the same.}
\label{fig:learning}
\end{figure}

\section{Capital Requirement}
Table~\ref{tab:stages} applies the equations to a four-stage plan, with units expressed as 120\,N$\cdot$m actuator equivalents, prices falling as
volume rises and cost floored at RobStride's estimated cost (@@cogs120). Total external capital is about @@total_cap (US\$@@total_cap_usd\,M),
dominated by the Series~B plant (Fig.~\ref{fig:capital}).

\begin{table*}[!t]
\caption{Staged plan (estimated; amounts in INR~crore unless noted)}
\label{tab:stages}
\centering\scriptsize\setlength{\tabcolsep}{4pt}
\begin{tabular}{@{}l r r r r r r r r r r@{}}
\toprule
Stage & Months & Units/yr & Price [INR] & Unit cost [INR] & GM & Revenue/yr & Opex/yr & EBITDA/yr & Capex & Raise \\
\midrule
@@stage_rows
\bottomrule
\end{tabular}
\end{table*}

\begin{figure}[!t]
\centering
\includegraphics[width=\columnwidth]{capital_plan.png}
\caption{Capital to raise per stage versus yearly revenue reached at the end of the stage (INR~crore, logarithmic scale).}
\label{fig:capital}
\end{figure}

Three observations follow. First, Stage~1 is close to break-even (about @@s1_be units/yr) only because laboratories and defence buyers pay about
INR~42{,}000 for a 120\,N$\cdot$m joint, still less than half the Indian retail price of a CubeMars AK10-9. Second, the critical risk is Stage~3: at
INR~21{,}000 per unit the gross margin is @@s3_gm\,\%, and if Chinese price cuts force INR~15{,}000 it falls to @@s3_gm_war\,\%; volume tooling should
therefore be built only against signed contracts. Third, at the end of Stage~3 the company earns about @@s3_rev (US\$@@s3_rev_usd\,M) a year, worth
about US\$@@s3_mc_lo--@@s3_mc_hi\,M at 2--4$\times$ sales.

Table~\ref{tab:sources} lists the capital sources found. Indian robotics start-ups raised only US\$52.9\,M in 2025, about 0.5\,\% of Indian
technology venture funding (the US raised US\$5.6\,bn)~\cite{logs_india}, so grants, defence programmes, customer pre-payments and strategic
investors matter more than in software.

\begin{table}[!t]
\caption{Capital sources for an Indian actuator company~\cite{logs_india}}
\label{tab:sources}
\centering\scriptsize
\begin{tabularx}{\columnwidth}{@{}L l@{}}
\toprule
Source & Size \\
\midrule
Bootstrap (garage kit + prototypes) & INR~10--35~lakh \\
Startup India Seed Fund (via incubator) & $\leq$INR~20~lakh grant + 50~lakh debt \\
Incubators: ARTPARK, IIT hubs (DST NM-ICPS) & grants, labs \\
State grants: Karnataka ELEVATE, TANSEED & $\leq$INR~50 / 10--15~lakh \\
Defence: iDEX / ADITI & $\leq$INR~1.5 / 25~crore \\
MeitY humanoid fund (announced) & INR~500~crore total \\
Seed VC (Yali, Speciale, Endiya, pi, Kalaari, Blume) & US\$2--3.5\,M \\
Series A/B VC & US\$5--10\,M / 20--30\,M \\
Strategic (Zen, Reliance, Zoho) & stake or acquisition \\
SIDBI venture debt; credit guarantee & INR~10--15 / $\leq$20~crore \\
ECMS component scheme & 25\,\% capex support (large) \\
\bottomrule
\end{tabularx}
\end{table}

\section{Valuation}
Listed component makers trade at 0.3--3.5$\times$ sales when mature (Nabtesco 1.9$\times$, Inovance 2.9$\times$, Schaeffler 0.25$\times$),
4.5--10$\times$ when priced as humanoid suppliers (Sanhua 4.5$\times$, Harmonic Drive 10$\times$), and 75--88$\times$ for pure plays such as
Leaderdrive and Unitree, whose shares opened 629\,\% above the IPO price in August 2026 and have since fallen about 59\,\% from that open~\cite{logs_mkt}.
One per cent of the 2030 actuator market is about US\$@@one_rev\,M of revenue, worth about US\$@@one_mc\,M at 4$\times$ sales. Table~\ref{tab:mc} shows
what a US\$10\,bn actuator company would require.

\begin{table}[!t]
\caption{Requirements for a US\$10\,bn actuator company (estimated)}
\label{tab:mc}
\centering\scriptsize
\begin{tabular}{@{}c c c c c c@{}}
\toprule
EV/sales & Revenue & Actuators/yr & \multicolumn{3}{c}{Share of actuator market} \\
\cmidrule(l){4-6}
 & [US\$\,bn] & at US\$250 [M] & 2030 & 2035 low & 2035 high \\
\midrule
@@mc_rows
\bottomrule
\end{tabular}
\end{table}

\section{Go-to-Market Strategy}
\subsection{Positioning}
An Indian entrant cannot win on price against CNY~1{,}000 joints. It can win on attributes some buyers value more: \emph{trust and compliance}
(defence, government laboratories and Western buyers avoiding Chinese components), \emph{local support} (Indian stock, GST invoices, two-day
replacement), \emph{customisation} (ratios, shafts, IP rating, 72\,V windings, and the 360\,N$\cdot$m class nobody sells cheaply) and
\emph{software} (a RobStride-compatible CAN protocol, ROS~2 drivers and accurate simulation models for reinforcement learning).

\subsection{Beachhead customers}
In order: (1)~university and research laboratories, which pay INR~34{,}000--1{,}05{,}000 per imported joint today; (2)~Indian robotics start-ups
building quadrupeds, humanoids, cobots and exoskeletons, all of which import joints; (3)~defence programmes (iDEX challenges, DRDO laboratories,
integrators) where a non-Chinese supply chain earns a premium; (4)~export customers seeking a second source; and (5)~later, replacement of the
roughly 55{,}000 industrial servo joints India imports each year.

\subsection{Sequencing}
Table~\ref{tab:gtm} gives the sequence. The first product is \emph{integration}: imported joints sold with Indian-built interface boards, ROS~2
drivers, simulation models, local stock and warranty, which earns revenue and customer relationships while the in-house actuator is developed.
Kill criteria are set in advance: if fewer than five customers re-order within 18 months, or the 120\,N$\cdot$m unit cannot reach INR~20{,}000 at
600 units/yr, the company should remain an integrator and software firm rather than a manufacturer.

\begin{table}[!t]
\caption{Go-to-market sequence}
\label{tab:gtm}
\centering\scriptsize
\begin{tabularx}{\columnwidth}{@{}l L L@{}}
\toprule
Months & Offer & Milestone \\
\midrule
0--6 & integration and resale of imported joints with Indian software, stock and support & 10 paying customers; JXA-120 v1 on the dynamometer \\
6--18 & JXA-120 and JXA-40, hand-assembled, to laboratories and start-ups; first iDEX bid & @@s1_units/yr run-rate; 200\,h life data; seed round (@@s1_raise) \\
18--36 & JXA-360 and 72\,V line; cast housings; own driver board; export & @@s2_units/yr; ISO~9001; Series~A (@@s2_raise) \\
36+ & volume contracts with humanoid makers; automated winding and test & @@s3_units/yr; Series~B or strategic partner (@@s3_raise) \\
\bottomrule
\end{tabularx}
\end{table}

\section{Risks}
The principal risks are: Chinese price cuts (RobStride targets 300{,}000 units in 2026), mitigated by never competing on price alone; rare-earth
magnet export licences (the wider Chinese rules are suspended only until 10~November 2026), mitigated by stockpiling magnet sets, qualifying
dysprosium-free N48H grades and following India's INR~7{,}280~crore magnet scheme; a humanoid hype cycle, mitigated by selling to non-humanoid
robots and raising on revenue; field failures, mitigated by end-of-line testing of every unit and life testing; and thin Indian hardware venture
capital, mitigated by grants, defence programmes and strategic investors.

\section{Conclusion}
An actuator company (``selling shovels'') is a sounder venture for an Indian robotics founder than another humanoid start-up: demand is real,
growing about 40-fold from 2025 to 2030, and every Indian robot maker imports its joints today. It is, however, a manufacturing business with
25--60\,\% gross margins at best, competing with Chinese makers that are already at volume. The recommended path is to earn revenue first as an
integrator, sell in-house actuators to laboratories, start-ups and defence buyers on trust, service and customisation, raise capital in small
steps (about @@s1_raise at seed and @@s2_raise at Series~A), and build volume tooling only against signed orders. Copper will likely remain
expensive because of grids, electric vehicles and data centres, but it is not the lever for an actuator maker; magnet supply and quality are.

\balance
\begin{thebibliography}{99}
\footnotesize
\bibitem{jxa_paper} JX1 Humanoid Project, ``Design and techno-economic analysis of in-house quasi-direct-drive actuators for humanoid robots in India,'' tech. rep., Oct.~2026, \url{actuators/inhouse/JXA_inhouse_actuator_research_paper.pdf}.
\bibitem{bofa2026} BofA Institute, ``Physical AI, part~2,'' Mar.~2026, \url{https://institute.bankofamerica.com/content/dam/transformation/physical-ai-part-2.pdf}.
\bibitem{citi2024} Citi Global Perspectives \& Solutions (GPS), report on AI robots and humanoids, Nov.~2024.
\bibitem{ifr2026} International Federation of Robotics, \emph{World Robotics 2026}, press release, Sep.~2026.
\bibitem{sp2026} S\&P Global, copper demand and supply study (press release), Jan.~2026.
\bibitem{aiindex2026} Stanford Institute for Human-Centered AI, \emph{AI Index Report 2026}, 2026.
\bibitem{brynjolfsson2026} E.~Brynjolfsson, B.~Chandar, and R.~Chen, ``Canaries in the coal mine? Six facts about the recent employment effects of artificial intelligence,'' Stanford Digital Economy Lab, Aug.~2025.
\bibitem{bls2025} U.S. Bureau of Labor Statistics, \emph{Employment Projections 2024--2034}, 2025.
\bibitem{acemoglu2020} D.~Acemoglu and P.~Restrepo, ``Robots and jobs: Evidence from US labor markets,'' \emph{J. Political Economy}, vol.~128, no.~6, pp.~2188--2244, 2020.
\bibitem{wright1936} T.~P. Wright, ``Factors affecting the cost of airplanes,'' \emph{J. Aeronautical Sciences}, vol.~3, no.~4, pp.~122--128, 1936.
\bibitem{logs_mkt} JX1 Project, ``Market outlook 2030 and copper'' research log, \url{research/raw/market_outlook_2030_copper_raw.md}, Oct.~2026.
\bibitem{logs_india} JX1 Project, ``India robotics industry and capital'' research log, \url{research/raw/india_robotics_industry_capital_raw.md}, Oct.~2026.
\bibitem{logs_cn} JX1 Project, ``China actuator manufacturing economics'' research log, \url{research/raw/china_actuator_manufacturing_economics_raw.md}, Oct.~2026.
\end{thebibliography}

\end{document}
"""


def main():
    BUILD.mkdir(exist_ok=True)
    tex = BUILD / "business_paper.tex"
    tex.write_text(TexTemplate(TEX).substitute(values()), encoding="utf-8")
    build_pdf(tex, OUT_PDF)
    print("wrote", OUT_PDF)


if __name__ == "__main__":
    main()
