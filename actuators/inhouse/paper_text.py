"""Fixed text blocks of the in-house actuator paper (HTML fragments). Numbers that come from the design or cost model
are written as $placeholders and filled by make_paper.py with string.Template, so the text never disagrees with the
calculation."""

PHYSICS = r"""
<h2 id="physics">2. How an electric motor makes torque (from magnetism up)</h2>

<h3>2.1 Four facts of electromagnetism you need</h3>
<ol>
<li><b>A current makes a magnetic field.</b> Wind wire around an iron tooth and push current through it: the tooth becomes an
electromagnet. Its strength is set by the <i>ampere-turns</i> N·I (turns × current), not by the current alone. Iron guides
the field about 1000 times more easily than air, which is why motors are mostly iron with a very thin air gap.</li>
<li><b>Opposite poles attract, like poles repel.</b> A permanent magnet (NdFeB, "neodymium") is a magnetic field you get for
free, with no current and no heat. NdFeB grade N42 has a remanence B<sub>r</sub> ≈ 1.3 tesla.</li>
<li><b>Force on a current in a field (Lorentz):</b> F = B · I · ℓ. A wire of length ℓ carrying current I in flux density B
feels a sideways force. Every torque in this paper comes from this one line.</li>
<li><b>A changing field makes a voltage (Faraday):</b> e = −dλ/dt. When the magnets sweep past the coils, they induce a
voltage, the <i>back-EMF</i>. It grows with speed and is what limits how fast the motor can spin on a 48 V battery.
The same physics run backwards is a generator: turn a motor by hand and it makes electricity.</li>
</ol>

<h3>2.2 From force to torque: the one equation that sizes a motor</h3>
<p>Add up the Lorentz force on every conductor in the air gap and multiply by the radius. The result depends on the air-gap
<b>shear stress</b> σ (newtons of tangential pull per square metre of rotor surface) and the rotor size:</p>
<div class="eq">T = σ · (π · D · L) · D/2 = (π/2) · σ · D² · L</div>
<p>D is the air-gap diameter and L the stack length (the length of the iron). σ = (magnetic loading B) × (electric loading A,
amperes of current per metre of circumference) / 2. Air-cooled servo motors run σ ≈ 5–15 kPa continuously and 30–60 kPa
for a few seconds at peak. Our three designs reach $shear_list kPa at peak. <b>Torque grows with D², but only with L</b>, which is why
robot actuators are "pancakes": large diameter, short length.</p>

<h3>2.3 Brushless motor = magnets on the rotor, copper on the stator</h3>
<p>A brushless DC (BLDC) or permanent-magnet synchronous motor (PMSM; same hardware) has:</p>
<ul>
<li>a <b>stator</b>: a stack of thin, insulated silicon-steel sheets (laminations, 0.2–0.35 mm) with <i>teeth</i>; copper coils
are wound around the teeth;</li>
<li>a <b>rotor</b>: a steel ring carrying 2p magnets of alternating polarity (p = pole pairs);</li>
<li>three <b>phases</b> (A, B, C) of coils, driven by a three-phase inverter (six MOSFETs) at a frequency
f = p · rpm / 60.</li>
</ul>
<p>The controller always energises the coils so that the stator field sits 90 electrical degrees ahead of the rotor
field. The rotor keeps chasing it, and that steady pull is the torque. This is <b>field-oriented control (FOC)</b>. It needs
the rotor angle at all times, so every actuator carries a magnetic angle encoder.</p>
<p>Robot actuators use the <b>outer-rotor</b> ("outrunner") layout: stator inside, magnet ring outside, as in drone motors.
For a given outside diameter it gives the largest air-gap diameter D and so the most torque (T ∝ D²). It is also the
easiest stator to wind by hand, because the teeth point outwards and you can reach every slot.</p>

<h3>2.4 Slots, poles and the winding factor</h3>
<p>Robot motors use <b>tooth-concentrated windings</b>: each coil is wound around one tooth. They have short end turns
(less copper, less heat), they are easy to wind, and they work with slot/pole combinations close to each other, such as
12N14P, 24N28P, 36N40P and 48N44P (N = slots/teeth, P = magnet poles). The <b>winding factor</b> k<sub>w</sub>
(0–1) says how much of the copper's ampere-turns produce useful torque. Our script finds the coil-to-phase assignment by the
"star of slots" method:</p>
<table class="small">
<tr><th>Class</th><th>Slots / poles</th><th>k<sub>w</sub></th><th>Repeating units</th><th>Cogging order (LCM)</th><th>Why</th></tr>
$winding_rows
</table>
<p>A high LCM of slots and poles means many small cogging steps that mostly cancel, giving smooth torque. An even number of
repeating units means the magnetic pulls balance and the rotor is not pulled to one side (no unbalanced magnetic pull).</p>

<h3>2.5 The motor constants that matter for a robot</h3>
<div class="eq">T = K<sub>t</sub> · I &nbsp;&nbsp;&nbsp; e = K<sub>e</sub> · ω &nbsp;&nbsp;&nbsp; (K<sub>t</sub> = K<sub>e</sub> in SI units) &nbsp;&nbsp;&nbsp;
P<sub>copper</sub> = 3 · I<sub>rms</sub>² · R &nbsp;&nbsp;&nbsp; K<sub>m</sub> = T / √P<sub>copper</sub></div>
<ul>
<li><b>K<sub>t</sub></b> (N·m per ampere): more turns give more torque per amp, but also more back-EMF and so a lower top speed on 48 V.
The number of turns is therefore chosen <i>from the speed you need</i>, and the wire is then made as thick as the slot allows.</li>
<li><b>K<sub>m</sub></b> (motor constant, N·m/√W): torque per square root of heat. It depends only on how much copper and magnet
you put in the gap, <i>not on the number of turns</i>. It is the true figure of merit: heat = (T/K<sub>m</sub>)². Doubling the
torque costs four times the heat. K<sub>m</sub> grows roughly with D<sup>2.5</sup>·L, so a big, flat motor wins.</li>
<li><b>Thermal limit:</b> the class-H enamel survives 180–200 °C, NdFeB SH grade 150 °C. We cap the winding at 120 °C.
Continuous torque is whatever torque keeps the copper below that with the heat the actuator can shed (here
$rth_list K/W from winding to air when bolted to an aluminium limb).</li>
</ul>

<h3>2.6 Why a low gear ratio ("quasi-direct drive")</h3>
<p>Legged robots hit the ground hard and need to feel forces through the motor current. A gear ratio G multiplies torque by G,
but it also multiplies the rotor's inertia by G² and the friction by roughly G. With G ≈ 6–10 (one planetary stage) the
joint stays <b>back-drivable</b>: you can push it by hand, impacts do not strip teeth, and current is a good measure of
joint torque. That is why MIT Cheetah, Unitree, RobStride, Damiao and Berkeley Humanoid all use 6–10:1 single-stage
planetaries for legs. We use 9:1 for the 40 and 120 N·m classes and 10:1 for the 360 N·m class. The ratio of a planetary
with the ring gear fixed is</p>
<div class="eq">G = 1 + Z<sub>ring</sub> / Z<sub>sun</sub> &nbsp;&nbsp; with &nbsp;&nbsp; Z<sub>ring</sub> = Z<sub>sun</sub> + 2·Z<sub>planet</sub>
&nbsp;&nbsp; and &nbsp;&nbsp; (Z<sub>sun</sub> + Z<sub>ring</sub>) / N<sub>planets</sub> = whole number</div>

<h3>2.7 The 48 V speed limit and the torque–speed curve</h3>
<p>The inverter can put at most about V<sub>dc</sub>/√3 ≈ 26 V (peak, per phase) across a winding. As speed rises, back-EMF
uses up that voltage until no current, and so no torque, can be pushed in: that is the no-load speed. Below it, the current
limit sets the flat "peak torque" line (Fig. 3). Field weakening (negative d-axis current) can stretch the top speed by 20–40 %
at the cost of heat. The same trade-off explains every datasheet: RS04 (120 N·m, 21 rad/s) and RS06 (36 N·m, 50 rad/s) use
different turns on similar hardware.</p>
"""

WINDING = r"""
<h2 id="winding">6. Winding the stator: a procedure you can hand to a technician</h2>
<p class="lead">This is the step people fear most. On a tooth-coil outrunner stator it is slow but simple, and a careful person
can learn it on scrap drone stators in one weekend. Any motor-rewinding shop (ceiling-fan, pump or e-rickshaw hub-motor
rewinders exist in every Indian city) already knows the skills; give them this page, the layout in Fig. 2 and the table below.</p>

<table class="small">
<tr><th>Class</th><th>Teeth</th><th>Turns / tooth</th><th>Wire (bare), strands in hand</th><th>Parallel groups</th><th>Wire per stator</th>
<th>Copper fill (bare)</th><th>R phase @20 °C</th><th>Pattern (tooth 1 →)</th></tr>
$winding_table
</table>

<h3>6.1 Tools and materials</h3>
<ul>
<li>Class-H (200 °C) dual-coat enamelled copper wire in the sizes above (polyesterimide + polyamide-imide, "grade 2"
build). Buy a few hundred grams per stator; budget 1.5× the calculated mass for practice and scrap.</li>
<li>Stator insulation: epoxy powder coating of the lamination stack (0.2–0.3 mm, done by any powder-coating job shop, or
a fluidised-bed epoxy kit), or 0.13–0.18 mm Nomex/DMD slot liners cut to shape. Never wind onto bare laminations: the
sharp edges cut the enamel.</li>
<li>A winding jig: the stator clamped on a mandrel in a bench vice or lathe, plus a turn counter. For production, a
manual or semi-automatic <b>needle winder</b> for outrunner stators (§8.3 gives prices).</li>
<li>Wire tensioner (a felt-pad tensioner or simple drag spool), plastic or brass tamping tool (never steel), flat-nose
pliers with smooth jaws, PTFE sleeving, Kapton tape, class-H varnish (single-component polyester-imide dip varnish or
epoxy trickle resin), an oven that reaches 150 °C, a milliohm meter or 4-wire LCR meter, a 500 V–1 kV insulation tester,
and a 0–60 V bench supply.</li>
</ul>

<h3>6.2 Step by step</h3>
<ol class="steps">
<li><b>Prepare the stack.</b> Deburr the laminations (fine stone, then blow clean). Check the stack is square and tight
(bonded, welded or riveted). Powder-coat or fit slot liners. Check with the insulation tester that the coating holds 500 V.</li>
<li><b>Mark tooth 1</b> with paint and number the teeth clockwise as in Fig. 2. Write the pattern on a card and tick off each
tooth as you go.</li>
<li><b>Plan the paths.</b> For one parallel group, phase A's teeth are wound one after the other with one continuous wire,
following the pattern: capital letter = wind clockwise (looking at the tooth tip), small letter = anticlockwise. Going from
an "A" tooth to the next "a" tooth you simply keep winding in the opposite sense; do not cut the wire. Leave 10 cm tails.</li>
<li><b>Wind the first layer tight against the tooth</b>, turns side by side, starting at the slot bottom (near the yoke)
and working outwards. Keep steady tension (roughly 10–15 % of the wire's breaking load: about 15 N for 0.6 mm wire). Lay the
crossover between teeth along the end face, never across the air-gap face.</li>
<li><b>Count turns exactly.</b> One turn too many or too few on one tooth makes the phases unequal: current ripple, noise
and heat. Use a counter on the jig.</li>
<li><b>Keep half the slot for the neighbour.</b> Each slot holds two coil sides (one from each tooth). Stop each coil at the
slot's centreline; tamp the turns with the plastic tool. Our fill target is $fill_target bare-copper fill; if the last turns
do not fit, the wire is too thick: change to more strands of thinner wire with the same total copper area.</li>
<li><b>Wind B and C the same way</b>, starting 120 electrical degrees later as the pattern shows. With several parallel
groups, wind each group (one repeating unit of the pattern) as a separate continuous wire.</li>
<li><b>Terminate.</b> Scrape or burn off the enamel at the tails (solder pot at 450 °C or a stripping cream), twist the
strands, solder or crimp. Join the three "end" tails into the star point, sleeved in PTFE. Join parallel groups at the
phase terminals. Tie the end turns with polyester lacing cord.</li>
<li><b>Test before varnishing</b> (fix mistakes now, it is impossible later):
<ul><li>phase-to-phase resistance: all three within ±2 % of each other and within ±10 % of the table;</li>
<li>insulation: &gt;100 MΩ at 500 V DC from every phase to the stack;</li>
<li>inductance with an LCR meter at 1 kHz: equal within ±5 % (a wrong-direction coil shows up here);</li>
<li>after the rotor is fitted: spin it by hand (or with a drill) and look at the three line-line back-EMFs on an
oscilloscope: three equal, clean sine waves 120° apart. Their amplitude gives K<sub>e</sub> directly.</li></ul></li>
<li><b>Varnish (impregnate).</b> Pre-heat to 100 °C, dip or trickle class-H varnish until it stops bubbling, drain,
then cure (typically 2 h at 150 °C; follow the varnish datasheet). Varnish locks the turns (no rubbing, no noise),
fills the air pockets and roughly halves the winding-to-iron thermal resistance.</li>
<li><b>Re-test</b> (resistance, insulation, back-EMF) and record the numbers with the stator's serial number.</li>
</ol>

<h3>6.3 Do it yourself, give it to a rewinder, or use a machine?</h3>
<table class="small">
<tr><th>Route</th><th>Time per JXA-120 stator</th><th>Cost</th><th>Quality risk</th><th>When</th></tr>
<tr><td>Hand winding on a jig (you)</td><td>3–5 h (the first ones 8 h+)</td><td>labour only</td><td>turn-count errors, low fill</td><td>prototypes, 1–25 units</td></tr>
<tr><td>Local motor rewinder (job work)</td><td>1–2 days turnaround</td><td>$rewinder_cost per stator (ESTIMATED)</td><td>wire grade swaps, poor insulation: inspect and test</td><td>batches of 5–50</td></tr>
<tr><td>Manual/semi-auto needle winder</td><td>20–40 min</td><td>machine $needle_winder</td><td>low once set up</td><td>50–500 / year</td></tr>
<tr><td>CNC multi-spindle needle winder (China)</td><td>1–3 min</td><td>machine $cnc_winder</td><td>low</td><td>&gt; 5,000 / year</td></tr>
</table>
<p>Practise first: buy two or three cheap 5010/8108-class drone stators, unwind them (count the turns), and rewind them.
When your rewound motor's resistance and back-EMF match the original, you are ready for the real stator.</p>
"""

BUILD = r"""
<h2 id="build">7. Making every other part: the in-house route, step by step</h2>
<p class="lead">"In-house" here means: design, winding, assembly, magnetising, calibration and testing under your roof,
with precision cutting (laminations, gears, housings) bought as <b>job work</b> from Indian shops. Nobody should
buy a gear-hobbing machine or a lamination press for 25 actuators.</p>

<h3>7.1 Parts list and who makes each part</h3>
<table class="small">
<tr><th>Part</th><th>Material / spec</th><th>How to make (prototype)</th><th>How to make (volume)</th></tr>
<tr><td>Stator laminations</td><td>CRNO M270-35A / 35C250 0.35 mm (0.2 mm for lower iron loss)</td><td>fibre-laser or wire-EDM cut stack, then bond with
lamination varnish or weld 3 seams; anneal if possible</td><td>progressive stamping die + interlocking</td></tr>
<tr><td>Magnets</td><td>NdFeB N42SH/N45SH arc or flat segments, Ni-Cu-Ni plated, magnetised radially</td><td>buy pre-magnetised segments (China or Indian distributor)</td><td>same, by the thousand</td></tr>
<tr><td>Rotor can</td><td>EN3/EN8 (1018/1045) mild steel tube or bar</td><td>CNC lathe job work</td><td>CNC lathe / deep-drawn cup</td></tr>
<tr><td>Sun, planets</td><td>EN353 or 20MnCr5, carburised 58–62 HRC case</td><td>gear-hobbing job shop (+ heat treat) or wire-EDM from pre-hardened blanks</td><td>hobbing + grinding, or powder metallurgy</td></tr>
<tr><td>Ring gear</td><td>EN19/42CrMo4 nitrided, or EN353 carburised</td><td>wire-EDM the internal teeth (easiest), or shaping</td><td>broaching / power skiving</td></tr>
<tr><td>Carrier, housing, hub</td><td>Al 6061-T6 / 7075-T6 (or printed AlSi10Mg)</td><td>CNC milling/turning job work (or metal 3D printing, §8.5)</td><td>CNC or pressure die-casting</td></tr>
<tr><td>Output bearing</td><td>crossed-roller (CRBH/RU) or two thin-section 68xx/69xx</td><td>buy</td><td>buy</td></tr>
<tr><td>Encoders</td><td>MT6835/MA600 on the rotor, MT6701/AS5047P on the output, diametric magnets</td><td>on the driver PCB</td><td>same</td></tr>
<tr><td>Driver</td><td>STM32G4 + 3-phase gate driver + 6 × 80–100 V MOSFETs + shunts + CAN transceiver</td><td>PCB + assembly at Lion Circuits / JLCPCB</td><td>same, panelised</td></tr>
</table>

<h3>7.2 The build sequence</h3>
<ol class="steps">
<li><b>Laminations.</b> Send the DXF of one lamination to a fibre-laser shop that cuts electrical steel. Ask for
nitrogen-assist cutting and no burr. Cut 3–5 % extra. Stack on a mandrel with a key, press flat, bond with
lamination varnish (or weld 3 shallow seams along the back of the yoke), then powder-coat. The laser's heat damages the
steel near the cut and raises iron loss by roughly 10–30 % on narrow teeth; acceptable for prototypes. Wire-EDM through a
clamped stack avoids this but costs more per stack.</li>
<li><b>Wind and varnish</b> the stator (Section 6).</li>
<li><b>Rotor.</b> Clean the rotor can and magnets with isopropyl alcohol. Bond the magnets with high-temperature
structural epoxy or anaerobic magnet adhesive (e.g. Loctite AA 3342 / Araldite 2014 class), alternating N and S, using a
non-magnetic (printed or aluminium) spacer comb so they stay equally spaced. Check polarity with a compass or a gauss
meter as you go; one reversed magnet ruins the motor. Optionally wrap with glass-fibre/epoxy or Kevlar for retention.
Balance the rotor on a simple knife-edge or by drilling the end plate.</li>
<li><b>Gears.</b> Order sun, planets and ring from a gear job shop with the tooth data from Table 5 (module, teeth,
pressure angle 20°, profile shift +0.3 on the 12-tooth sun, quality DIN 7 or better, case-carburised 0.4–0.6 mm).
Check the planet bores and pins for a sliding H7/g6 fit; use needle bearings or bronze bushes in the planets.</li>
<li><b>Housings.</b> CNC job work in 6061-T6, anodised. Tolerances that matter: bearing seats (±0.01 mm), ring-gear seat
concentric to the output bearing seat (≤0.02 mm), and the stator hub concentric to the rotor bearings (the air gap is only
$airgap_mm mm).</li>
<li><b>Driver PCB.</b> Two encoders, the FOC microcontroller and the power stage go on one round board on the back of the
actuator. Reuse an open design for the first version (B-G431B-ESC1 class, moteus, or the MIT Mini Cheetah/Ben Katz driver);
keep the same CAN protocol as RobStride (MIT mode) so JX1's software does not change.</li>
<li><b>Assemble.</b> Fit the stator to the hub; press the rotor bearings; insert the rotor <i>with a guide sleeve</i>: the magnets
pull the rotor sideways with hundreds of newtons and will snap onto the stator and chip if you let go. Fit the gear stage
with grease (lithium-complex or synthetic EP grease), the carrier and the output bearing, then the driver.</li>
<li><b>Calibrate.</b> Encoder offset and linearisation, phase order, current-loop tuning, cogging-torque compensation
table, output-encoder offset for absolute joint position.</li>
<li><b>Test on a bench</b> (Section 9): back-EMF, K<sub>t</sub> with a torque arm and a load cell, peak torque,
1 h thermal soak at continuous torque, backlash, then a 50-hour gait-trace life test on at least one unit per class.</li>
</ol>

<h3>7.3 Safety</h3>
<ul>
<li>NdFeB magnets pinch and shatter. Wear eye protection; keep them away from phones, pacemakers and watches; store them in
keepers. Machine or grind them only wet: the dust burns.</li>
<li>A 48 V battery can deliver hundreds of amperes into a short. Fuse every actuator, and test new drivers through a current-limited
supply first.</li>
<li>Varnish and epoxy fumes: work in ventilation, and use the oven only for curing, never for food.</li>
</ul>
"""
