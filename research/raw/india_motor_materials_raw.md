# JX1: QDD actuator materials, motor parts, process and test-equipment pricing, India vs China (RAW)

- **Purpose:** inputs for the paper "build QDD joint actuators (BLDC/PMSM + planetary + FOC driver) in-house in India vs buy RobStride from China".
- **Research date:** 2026-10-06 (all rows "seen" on this date unless a different date is given).
- **Scope rule:** this file only adds what the existing raw files lack. It does **not** repeat:
  - bearings (thin-section 68xx/69xx, crossed-roller IKO prices in India), fasteners, Al/steel ₹/kg, CNC/laser/3D-print service rates, PCB fab → `india_mechanical_manufacturing_raw.md` (§1, §2, §6, §9);
  - Indian MCU / CAN transceiver / encoder module / FOC driver prices, import vendor-store driver prices → `india_electronics_compute_raw.md` (§A2–A5, §A9);
  - Robu/Amazon.in prices for MT6835 module, DRV8323/DRV8353, NUCLEO-G4, WeAct G4, NDrive Z1, MKS XDrive Mini → `india_robu_browser_sourcing_raw.md`;
  - open-source / commercial FOC driver specs and official prices (B-G431B-ESC1 $39.26 ST eStore, moteus, ODrive, Recoil, mini-cheetah, SteadyWin/Damiao boards) → `actuator_technology_raw.md` §5.
- **FX used (ESTIMATED conversions):** 1 USD = ₹96.38 = CNY 6.7145, so 1 CNY = ₹14.35. Source: https://open.er-api.com/v6/latest/USD, "time_last_update_utc": Tue, 06 Oct 2026 00:02:31 UTC (read 2026-10-06).
- **Method:** WebSearch and WebFetch, plus curl of public listing pages. Sources read: Made-in-China.com search pages (static HTML), AliExpress search pages (embedded JSON; prices are what the page showed a US-located visitor), TradeIndia search pages, IndustryBuying, JLCPCB's public parts-library JSON (the request the parts search page makes, no login), K&J Magnetics, SteelOrbis, metalcharts.org, vendor and news pages. No accounts, carts, quote forms or uploads were used.
- **Could not read:** Alibaba.com (captcha / "punish" page), IndiaMART (HTTP 429), Robu.in (403), Amazon.in (503), LCSC (Akamai 403), Digikey India (403), SMM metal.com price tables (sign-in), Mysteel (paywall), zbotic.in (403), Business Standard (403).

### Label legend
| Label | Meaning |
|---|---|
| **VERIFIED** | Seen on the seller's, maker's or official page or JSON on the date given; URL given. A listing price is VERIFIED **as a listing**. That does not mean you can buy at that price (B2B "FOB" ranges are often placeholders). |
| **ESTIMATED** | My own arithmetic. The method is shown. |
| **UNVERIFIED** | Secondary source: a search-engine snippet, news article, blog or forum, or a page I could not open myself. |

### Reading AliExpress and Made-in-China rows
- AliExpress search JSON gives two prices per item. The first is the list price; the second (if present) is the sale price. The price belongs to the **default/cheapest SKU variant**, which may be a different size or quantity from the title. **US $1.09** and **US $0.99** are usually new-user bait prices and are ignored.
- Made-in-China "US$ x – y / Piece" ranges for custom parts (magnets, laminations) are often placeholders such as US$0.01–10. They are recorded but marked "placeholder".

---

## 0. QUICK VIEW (details and URLs in §1–§7)

| Item | India (best credible) | China (best credible) | Note |
|---|---|---|---|
| LME copper (cash/3M) | MCX ≈ ₹1,385/kg (11 Sep 2026, UNVERIFIED) | **US$14,528/t** (6 Oct 2026, VERIFIED) = ₹1,400/kg (ESTIMATED) | record high cash 14,737 on 8 Sep 2026 (UNVERIFIED) |
| Enamelled Cu wire, bulk (class 155–200) | listings ₹630–1,200/kg (TradeIndia), **below copper value, so stale**. Fair price ≈ ₹1,460–1,610/kg + 18% GST (ESTIMATED) | MIC EI/AIW-200 listings US$7–9.9/kg (also below copper, so placeholders). Fair FOB ≈ US$15.5–17.5/kg (ESTIMATED) | wire price ≈ 0.97 × copper + conversion cost |
| Enamelled Cu wire, retail 1 kg reel | Multicomp Pro reels on IndustryBuying ≈ ₹6,100–7,000/kg (ESTIMATED from VERIFIED) | AliExpress 1 kg QZY-2/180 0.47–1.2 mm **US$43.5–45.8** ≈ ₹4,190–4,410/kg | retail is 3–5× the bulk price |
| NdFeB blank (China domestic index) | – | N52(Ce) ≈ US$31/kg; 45SH(Ce) ≈ US$39/kg (SMM, Dec 2025, UNVERIFIED) | Pr-Nd oxide CNY 738–758k/t, late Sep 2026 (UNVERIFIED) |
| NdFeB retail arc (US benchmark) | – | K&J N52 arc 9.89 g **US$10.21** (≈ US$1,030/kg retail) | shows the 20–30× retail premium |
| SH/UH/EH magnets from China | 100% imported; licence needed (Dy/Tb) | MOFCOM April-2025 licensing in force; the Oct-2025 extra rules are suspended until **10 Nov 2026** | see §2.3 |
| CRNO electrical steel 0.35–0.5 mm | ₹72–100/kg (IndiaMART snippets, UNVERIFIED); stamped BLDC-fan stator stacks ₹90–100/kg | 50WW600 0.5 mm **CNY 4,527/t = US$662/t** (May 2026, VERIFIED); 35W250 listings US$1,580–2,800/t | India has ADD of US$223.82/t on Chinese CRNO (UNVERIFIED) |
| Ready-made BLDC stator cores | BLDC ceiling-fan stator stacks (18-slot, 0.5 mm) ₹90/kg or ₹90/pc (UNVERIFIED) | **8110 36N40P core US$10.5–11.4; 10010 36N42P US$10.4–31.1** (AliExpress) | §3.4 |
| Crossed-roller bearings | IKO CRBH3510 ₹11,799 (mech file §1d) | **CRBH3510 US$13–35; RU42 US$27–40; RU66 US$51; RU85 US$67** | about 4–8× cheaper from China before duty |
| FOC driver BOM (48 V, ~30 A, qty 10) | – | **≈ US$24 parts + ~US$4–7 PCB/PCBA ≈ US$30/board** (ESTIMATED, JLCPCB prices) | vs B-G431B-ESC1 $39.26, moteus-c1 $69 |
| Metal AM | iamRapid: ₹50–150/g (all metals); AlSi10Mg ₹15–30k/kg (UNVERIFIED blog) | JLC3DP SLM-316L **US$0.21/g** (Aug 2025, VERIFIED) | China is ~3–7× cheaper for steel |
| Stator winding machine | manual fan-stator winders ₹10.5–27k; CNC fan winder ₹2 lakh | hand-crank winder US$24–40; automatic BLDC needle winders US$5k–30k | §6.1 |
| Hipot / surge / LCR / dyno | hipot ₹10–39k; surge tester ₹25k–1.8 lakh | RK2670 hipot US$111–217; impulse tester US$1.4–2.2k; TH2830 LCR US$367–480; HB hysteresis brake US$125–288; DYN-200 torque sensor US$704 | §6.3 |

---

## 1. ENAMELLED (MAGNET) COPPER WIRE

### 1.1 Copper reference price

| Item | Value | Date | Source | Label |
|---|---|---|---|---|
| LME copper | **US$14,528.23 /t**, "up 0.05% over the past 24 hours" | 2026-10-06 | https://metalcharts.org/lme-copper-price | VERIFIED |
| LME copper record cash close | US$14,737/t (8 Sep 2026); US$14,238.50 by 11 Sep | Sep 2026 | search snippet (tacto.ai / metalradar.com) https://www.tacto.ai/en/commodities/copper-price | UNVERIFIED |
| LME copper average, May / Jun 2026 | US$13,476 / US$13,548 per t | 2026 | snippet, https://www.miningreporters.com/noticia/news/2026/07/copper-price-625-73-cents-new-annual-high-2026 | UNVERIFIED |
| MCX copper (India) | ₹1,384.75/kg (11 Sep 2026); Jun 2026 average ₹1,342/kg | Sep 2026 | snippet, https://upstox.com/commodity-market-trading/mcx-copper-price ; https://cbonds.com/indexes/221385/ | UNVERIFIED |
| LME copper in ₹/kg | 14,528 × 96.38 / 1000 = **₹1,400/kg** | 2026-10-06 | arithmetic | ESTIMATED |

**Copper share of wire mass (ESTIMATED):** for 0.5 mm grade-2 wire, overall diameter ≈ 0.548 mm. Enamel volume fraction = (0.548² − 0.5²)/0.548² = 16.8%. With enamel at ≈1.4 g/cm³ and Cu at 8.96 g/cm³, enamel is ≈3% of the mass, so the wire is **≈97% copper by mass**. At 1.0 mm the copper share is ≈98%.
**Floor price of the wire = 0.97 × ₹1,400 = ₹1,358/kg** before any conversion cost (ESTIMATED).

### 1.2 Indian makers (no public price lists)

| Maker | What they make (relevant) | Price | Source | Label |
|---|---|---|---|---|
| Precision Wires India Ltd (Mumbai/Silvassa) | "Enamelled Round and Rectangular Copper Winding Wires… largest producer of Winding Wires in South Asia". FY26 revenue ₹5,410 cr; Silvassa expansion +4,620 MT/yr | no list price | https://www.arihantcapital.com/company-information/about-company/2400 ; https://www.sahi.com/news/precision-wires-q1-net-profit-surges-71-5-to-46-45-crore-amid-150-crore-fundraise-982-PE1_CORP | UNVERIFIED (secondary) |
| Ram Ratna Wires / RR Kabel ("RR Shramik" brand) | super-enamelled winding wire, sold through distributors | **₹950/kg, MOQ 50 kg** (Damani Sales Agency, Kolkata, "Rr Shramik Enamelled Copper Wire") | https://www.tradeindia.com/search.html?keyword=enamelled+copper+wire | VERIFIED listing (price likely stale; see 1.4) |
| Vidya Wires (Anand, Gujarat; IPO Dec 2025) | ">8,000 SKUs… 0.07 mm to 25 mm", enamelled Cu wire and strip | no list price | https://zerodha.com/ipo/413186/vidya-wires | UNVERIFIED (secondary) |
| Standard for class 200 dual coat | IEC 60317-13 / IS 13730-13: polyester or polyesterimide overcoated with polyamide-imide, class 200, heat shock ≥220 °C; grade 2 up to 0.5 mm | – | https://services.bis.gov.in/tmp/SR13730_13.pdf ; https://knowledge.bsigroup.com/products/specifications-for-particular-types-of-winding-wires-polyester-or-polyesterimide-overcoated-with-polyamide-imide-enamelled-round-copper-wire-class-200 | UNVERIFIED (snippet) |

### 1.3 Indian listings (bulk) and retail

| Item | Seller (city) | Price | MOQ | URL | Date | Label |
|---|---|---|---|---|---|---|
| RR Shramik enamelled Cu wire | Damani Sales Agency (Kolkata) | ₹950/kg | 50 kg | https://www.tradeindia.com/search.html?keyword=enamelled+copper+wire | 2026-10-06 | VERIFIED listing |
| Enamelled Cu wire 2–3 mm | Ganpati Engineering Industries (Jaipur) | ₹940/kg | 50 kg | same | 2026-10-06 | VERIFIED listing |
| Transformer winding wire | Shreeji Strips & Wires (Delhi) | ₹1,200/kg | 80 kg | same | 2026-10-06 | VERIFIED listing |
| Enamelled round Cu & Al winding wire | Bharat Insulation Co. (Mumbai) | ₹980/kg | 500 kg | same | 2026-10-06 | VERIFIED listing |
| Enamelled Cu winding wire | Insulating Material Corporation (Mumbai) | ₹1,100/kg | 100 kg | same | 2026-10-06 | VERIFIED listing |
| Self-bonding enamelled Cu wire | Jain Wire Products (Delhi) / Vidyut Teletronics (Jaipur) | ₹1,000/kg | 60 / 100 kg | same | 2026-10-06 | VERIFIED listing |
| 22 SWG super-enamelled | Ramsons (Jaipur) | ₹900/kg | 100 kg | same | 2026-10-06 | VERIFIED listing |
| Polycap super-enamelled | K. D. Insulation Products (Delhi) | ₹800/kg | 20 kg | same | 2026-10-06 | VERIFIED listing |
| Dual-coated enamel Cu wire | Superlex Wire Industries (Delhi) | price on request | – | same | 2026-10-06 | VERIFIED (no price) |
| IndiaMART category range | various | ₹345–1,340/kg ("motor winding super enameled" ₹1,340/kg; 0.5 mm ₹900/kg; 35 SWG ₹985/kg) | – | https://m.indiamart.com/impcat/enamelled-copper-wire.html | 2026-10-06 | UNVERIFIED (snippet; site gave HTTP 429) |
| Multicomp Pro ECW0.80 (0.8 mm, 125 m) | IndustryBuying (Farnell stock, ships ≤20 d) | ₹3,421/reel | 1 | https://www.industrybuying.com/search/?q=enamelled%20copper%20wire | 2026-10-06 | VERIFIED |
| → ₹/kg | 0.5027 mm² × 125 m = 62.8 cm³ × 8.9 g/cm³ ≈ 0.559 kg, so **≈ ₹6,120/kg** | | | | | ESTIMATED |
| Multicomp Pro ECW0.56 (0.56 mm, 230 m) | IndustryBuying | ₹3,539/reel → 0.246 mm² × 230 m ≈ 0.504 kg, so **≈ ₹7,020/kg** | 1 | same | 2026-10-06 | VERIFIED price / ESTIMATED ₹/kg |
| Robu.in / Amazon.in 0.3–1.0 mm reels | – | **not read** (Robu 403, Amazon 503) | – | – | 2026-10-06 | GAP |

### 1.4 China

| Item | Supplier | Price | MOQ | URL | Date | Label |
|---|---|---|---|---|---|---|
| EI/AIW 200 (PEI + PAI overcoat, Q(ZY/XY)-200) round Cu wire | Ousinai (Hebei) | US$7.9–9.9/kg FOB | 100 kg | https://www.made-in-china.com/products-search/hot-china-products/Eiaiw_Enameled_Copper_Wire.html | 2026-10-06 | VERIFIED listing (**placeholder: below copper value**) |
| EIAIW Class 200 IEC 60317-13 Grade 2 | Shenzhou brand | US$7–8/kg FOB | 500 kg | same | 2026-10-06 | VERIFIED listing (placeholder) |
| "Eiaiw 200 grade polyamideimide composite…" | – | US$2,600–2,700/t | 1 t | same | 2026-10-06 | VERIFIED listing (**not credible**: ~18% of copper value) |
| 200 °C enamelled round Cu magnet wire | Hangzhou Hongtong | US$9.99–29.99/kg | 100 kg | https://www.made-in-china.com/products-search/hot-china-products/Enameled_Copper_Wire.html | 2026-10-06 | VERIFIED listing |
| AIW 220 °C flat/rectangular Cu wire | Tianjin Rui Yuan (Rvyuan) | US$15.99–32.99/kg | 10–100 kg | Eiaiw page above | 2026-10-06 | VERIFIED listing (plausible; above copper value) |
| 1 kg/roll QZY-2/180 0.47–1.2 mm | AliExpress (item 3256…; several sellers) | **US$45.75 list / US$43.46 sale** | 1 kg | https://www.aliexpress.com/w/wholesale-enameled-copper-wire-1kg.html | 2026-10-06 | VERIFIED (US-visitor price) |
| 1 kg/roll QZY-2/180 0.15–0.44 mm | AliExpress | US$46.49 / 44.17 | 1 kg | same | 2026-10-06 | VERIFIED |
| 1 kg enamelled Cu 0.06–1.5 mm (generic) | AliExpress | US$45.75 / 43.46 | 1 kg | same | 2026-10-06 | VERIFIED |
| Self-bonding (2UEWB / 2HUEW) 1 kg | AliExpress | US$99–117 | 1 kg | same | 2026-10-06 | VERIFIED |
| **Fair bulk price, class 180–200 round, China** | LME US$14.53/kg × 0.97 = US$14.1/kg of copper, plus US$1.5–3.5/kg conversion and enamel (assumed) | **≈ US$15.5–17.5/kg ≈ ₹1,500–1,690/kg FOB** | – | – | – | ESTIMATED (conversion margin assumed, not sourced) |
| **Fair bulk price, India** | ₹1,358/kg Cu content + ₹100–250/kg conversion (assumed) | **≈ ₹1,460–1,610/kg + 18% GST**; class 200 dual coat probably +5–15% (assumed) | – | – | – | ESTIMATED |

**Takeaway:** Indian B2B listings at ₹630–1,200/kg date from the 2023–24 copper price (≈US$8–9k/t). At US$14.5k/t no honest seller can supply below ≈₹1,360/kg. For a prototype run of 12–30 motors (≈30–80 g of copper each, so 1–3 kg total), wire costs **₹2,000–15,000 at retail** whatever the source. Wire cost is negligible next to labour and tooling.

---

## 2. NdFeB MAGNETS

### 2.1 Price indices and benchmarks

| Item | Value | Date | Source | Label |
|---|---|---|---|---|
| SMM NdFeB blank N52(Ce) | US$30.35–31.60/kg (avg 30.98), delivered to works in China | 8 Dec 2025 | search snippet of https://www.metal.com/Rare-Earth-Magnets (page now needs sign-in) | UNVERIFIED |
| SMM NdFeB blank 45SH(Ce) | US$37.85–40.35/kg (avg 39.10) | 8 Dec 2025 | same | UNVERIFIED |
| SMM blank 28SH(Ce) page exists, values hidden | – | 30 Sep 2026 | https://www.metal.com/en/Rare-Earth-Magnet/202103120027 | VERIFIED (no number visible) |
| Asian Metal rough sintered N52 block | RMB 155–166/kg (≈US$22/kg) | Mar–Apr 2024 | https://amoffice.asianmetal.com/news/2048050/Chinese-rough-sintered-NdFeB-magnet-N52-prices-steady | UNVERIFIED (old) |
| Pr-Nd oxide (China) | CNY 738,000–758,000/t (late Sep 2026); US$96.69/kg on 5 Sep 2026 | Sep 2026 | snippet, https://news.metal.com/en/newscontent/104021095-pr-nd-oxide-price-pulls-back-slightly-rare-earth-market-overall-in-the-doldrums-smm-rare-earth-weekly-review | UNVERIFIED |
| Ex-China NdPr | "slip below $110/kg price floor" | Aug 2026 | https://source.benchmarkminerals.com/article/ex-china-ndpr-prices-slip-below-110-kg-price-floor-as-oversupply-builds | UNVERIFIED (headline) |
| K&J Magnetics AX2C45-N arc (N52, 57.15 OD × 50.8 ID × 19.05 mm, 45°, 9.89 g, NiCuNi, max 80 °C) | **US$10.21 (1 pc)** … US$8.16 (1,000–2,499) | 2026-10-06 | http://www.kjmagnetics.com/ax2c45-n-neodymium-arc-segment-magnet?cat=168 | VERIFIED |
| → US retail ₹/kg | 10.21 / 0.00989 kg ≈ **US$1,032/kg ≈ ₹99,500/kg** | | | ESTIMATED |

### 2.2 Per-piece listings (China and India)

| Item | Supplier | Price | MOQ | URL | Date | Label |
|---|---|---|---|---|---|---|
| N52SH arc, UAV/FPV motors | Ningbo Bestway Magnet | US$0.022–0.08/pc | 1,000 pcs | https://www.made-in-china.com/products-search/hot-china-products/Arc_Neodymium_Magnet_For_Motor.html | 2026-10-06 | VERIFIED listing (small FPV arcs) |
| N48SH / N52 super-thin arc, "robot small motor" | Xiamen Balin | US$0.05–0.10/pc | 10 pcs | same | 2026-10-06 | VERIFIED listing |
| N38SH arc segment, custom | Ningbo MGT | US$0.12–0.68/pc | 10 pcs | same | 2026-10-06 | VERIFIED listing |
| N42SH / N42M arc segment for BLDC rotor | Anhui Lulang | US$0.10–1.00/pc | 1,000 pcs | same | 2026-10-06 | VERIFIED listing |
| N35–N54 custom arc | Ningbo Eastar | US$0.01–10/pc | 10 pcs | same | 2026-10-06 | placeholder |
| N35 arc | Ningbo Zhaobao | US$2–10/pc | **1 pc** | same | 2026-10-06 | VERIFIED listing |
| Custom arc magnets, MOQ and lead time | Ningbo suppliers: Yunsheng MOQ 10,000 pcs / 30 d; Keke MOQ 1 / 30 d; others 15 d; custom N48SH "ready 7–9 weeks after payment" | – | – | snippet https://www.globalsources.com/knowledge/sintered-ndfeb-magnet-for-motors/ ; https://www.stanfordmagnets.com/sman2687-custom-ndfeb-arc-magnet.html | 2026-10-06 | UNVERIFIED |
| N52 block 20×10×1…10 (N35/N52) | AliExpress | US$5.28 list / 3.59 sale (default SKU; pack size not visible) | – | https://www.aliexpress.com/w/wholesale-neodymium-block-magnet-n52-20x10x3.html | 2026-10-06 | VERIFIED (SKU ambiguous) |
| Diametric 6×2.5 mm encoder magnets | AliExpress | 50 pcs lot US$17.77 sale (→ ≈US$0.36/pc, ESTIMATED; SKU ambiguous); single-pack listing US$11.99 | – | https://www.aliexpress.com/w/wholesale-diametric-magnet-6x2.5-encoder.html | 2026-10-06 | VERIFIED |
| India: 23×16×3 mm rectangular NdFeB for motors | TradeIndia seller | ₹23/pc | 1,000 pcs | https://www.tradeindia.com/search.html?keyword=neodymium+magnet | 2026-10-06 | VERIFIED listing |
| India: 40×20×10 mm NdFeB block | Magneticks | ₹150/pc | 300 pcs | same | 2026-10-06 | VERIFIED listing |
| India: arc magnets | Rare Earth Magnetics (Patiala/Chandigarh), Sonal Magnetics (Ahmedabad), Meena Magnetic (Ahmedabad) | price on request; "₹25/pc (3 mm N45)… ₹180/pc high-power motor magnet" | – | https://www.tradeindia.com/search.html?keyword=neodymium+arc+magnet ; snippet https://m.indiamart.com/impcat/motor-magnets.html | 2026-10-06 | VERIFIED (no price) / UNVERIFIED (snippet) |
| India: arc listings on TradeIndia | mostly **Chinese** sellers (Shenzhen Tecomag ₹8/pc MOQ 10,000; Hangzhou Lingmai US$1/pc MOQ 500) | – | – | same | 2026-10-06 | VERIFIED listing |

**ESTIMATED magnet cost per motor (method):** take an 8108-class outrunner: magnet ring ≈ 83 mm mean diameter × 2 mm thick × 10 mm long. Volume = π × 83 × 2 × 10 ≈ 5,215 mm³, × 7.5 g/cm³ ≈ **39 g of magnet per motor**.
- Cost at finished-magnet prices of US$45–80/kg (SMM blank US$31–39/kg × an assumed 1.3–2× for machining, coating and magnetising): **≈ US$1.8–3.1 ≈ ₹170–300 per motor**.
- The same 39 g at K&J-style retail (≈US$1,000/kg) costs ≈US$39.
- So the real cost driver is MOQ and custom tooling, not the material.

### 2.3 Chinese export controls (status on 2026-10-06) and India

| Fact | Source | Label |
|---|---|---|
| MOFCOM/GAC April 2025 regime (Ann. 18/2025) is **still in force**. It requires a licence for every export of 7 medium/heavy REEs (Sm, Gd, Tb, Dy, Lu, Sc, Y) and their magnets. "These were never suspended." | https://carraglobe.com/china-rare-earth-export-controls-2026/ (5 May 2026) | VERIFIED (article) |
| Ann. 70/2025 (7 Nov 2025) suspended Ann. 55–58, 61 and 62 of 9 Oct 2025 "until November 10, 2026". That suspends the 0.1%-of-value extraterritorial rule, the technology controls and 5 more elements (Ho, Er, Tm, Eu, Yb). | https://www.cirs-group.com/en/chemicals/china-temporarily-suspends-export-controls-on-key-raw-materials-including-rare-earths-lithium-batteries-and-diamond ; carraglobe (above) | VERIFIED (article) |
| Grades that need a licence: "SH, UH, EH, AH grades (controlled)" and all SmCo. "Standard NdFeB grades (N35–N52, many M/H grades) typically don't require licences unless they contain controlled heavy rare earths". "Verify composition by testing." | https://mainrichmagnets.com/rare-earth-magnet-export-compliance (8 Jun 2026) | VERIFIED (vendor article) |
| India "imports 100% of its sintered NdFeB magnet requirements". SIAM asked to move the EV traction-motor localisation deadline from Sep 2026 to Apr 2027. | https://rareearthexchanges.com/news/india-ev-ndfeb-magnet-supply-gap/ (1 Sep 2026) | VERIFIED (article) |
| India REPM scheme: ₹7,280 cr (₹750 cr capex subsidy + ₹6,450 cr sales-linked incentives) for 6,000 t/yr integrated sintered NdFeB, 600–1,200 t/yr per bidder. IREL supplies NdPr oxide to the 3 lowest bidders. 20 bids; technical bids opened 13 Aug 2026 (bidders include Coal India, L&T, Neo Performance). | https://www.autocarpro.in/news/heavy-industries-ministry-receives-20-bids-for-rs-7280-crore-rare-earth-magnet-scheme-134083 ; https://psuwatch.com/amp/story/newsupdates/coal-india-lt-neo-performance-among-20-bidders-under-rs-7280-cr-rare-earth-magnet-scheme-mhi | UNVERIFIED (news snippets) |
| India import duty on permanent magnets (HS 8505.11): 7.5% BCD + 18% IGST, but the source row is labelled "ferrite cores". | https://eximguru.com/hs-codes/85051110-ferrite-cores.aspx | UNVERIFIED (classification unclear) |
| MOFCOM licence review time: statutory up to 45 working days (from memory of the 2025 rules; not re-read today) | – | UNVERIFIED |

**Implications for JX1 (analysis, not sourced):**
1. Hot-running QDD motors (winding 120–155 °C, magnets 80–120 °C) would normally use **N42SH/N45SH/N48SH**. Those contain Dy/Tb and need a Chinese licence. That means end-use paperwork and weeks of delay, and the rules may tighten after 10 Nov 2026.
2. **N48H/N52 (no Dy) avoid the licence** but are limited to ≈80–120 °C, so they need a thermal derate.
3. Buying finished motors or actuators (RobStride) moves the licence burden to the Chinese maker. Whether finished motors are caught is not covered by the sources read (GAP).
4. A domestic Indian sintered supply under REPM will not exist before ~2027–28.

---

## 3. ELECTRICAL STEEL, LAMINATIONS, STATORS

### 3.1 Sheet price

| Item | Value | Date | Source | Label |
|---|---|---|---|---|
| China 50WW600 0.5 mm NGO, ex-warehouse incl. 13% VAT | Shanghai CNY 4,550; Wuhan 4,500; Guangzhou 4,530; **avg CNY 4,527/t = US$662/t** | 13 May 2026 | https://www.steelorbis.com/steel-prices/steel-prices-market-analyses/flats-and-slab/silicon-steel-sheet-prices-in-local-chinese-market-week-20-2026-1453292.htm | VERIFIED |
| China 50WW800 0.5 mm | avg CNY 4,360/t = US$637/t | 13 May 2026 | same | VERIFIED |
| China 35WW250 (Wuhan) daily price | page exists, paywalled | 2026 | https://www.mysteel.net/daily-prices/7067961-non-grain-oriented-electrical-steel-prices-wuhan | VERIFIED (no number) |
| 35W230/35W250/35W270 NGO coil | US$1,580–1,680/t, MOQ 1 t | 2026-10-06 | https://www.made-in-china.com/products-search/hot-china-products/35W250_Silicon_Steel.html | VERIFIED listing |
| 35W250/35W400/50W270 NGO "Hongwang" | US$2,200–2,800/t, MOQ 1 t | 2026-10-06 | same | VERIFIED listing |
| B35A270 / 35W270 (Baosteel) | US$800–1,030/t, MOQ 25 t | 2026-10-06 | same | VERIFIED listing (low; possibly placeholder) |
| "Low iron loss NGO coil for motors" | US$3–18/kg, MOQ 100 kg | 2026-10-06 | https://www.made-in-china.com/products-search/hot-china-products/0.2mm_Non_Oriented_Silicon_Steel.html | VERIFIED listing (small-lot price signal) |
| 0.2 mm thin-gauge NGO (20WTG1500, B20AT1500, 20WTG…) | **no NGO 0.2 mm price found**; the 0.2 mm listings seen are all **grain-oriented** (B20HS085 etc., US$699–1,500/t, 20 t MOQ) | 2026-10-06 | same | GAP |
| India CRNO (IndiaMART snippets) | 0.35 mm slit coil ₹100/kg; 0.5 mm 50A470 ₹85/kg; 0.65 mm ₹85/kg; ₹72–80/kg | 2026-10-06 | https://m.indiamart.com/impcat/crno-coils.html | UNVERIFIED (snippet) |
| India CRNO electrical steel (TradeIndia) | Rishika Enterprise ₹42,500/t (MOQ 1 t); JSW Steel listed (MOQ 1,000 kg, no price) | 2026-10-06 | https://www.tradeindia.com/search.html?keyword=crno+electrical+steel | VERIFIED listing (₹42.5/kg looks like non-prime/CRCA) |
| India electrical-steel index (all grades) | US$2,065/t (Mar 2026); US$2,110/t (Sep 2025) | 2026 | https://www.imarcgroup.com/electrical-steel-pricing-report | UNVERIFIED (likely CRGO-weighted) |
| India anti-dumping duty on Chinese CRNO | US$223.82/t for 5 years (CRFH excluded) | 2025 | https://gmk.center/en/news/india-has-imposed-anti-dumping-duties-on-imports-of-chinese-electrical-steel/amp/ | UNVERIFIED |
| India CRGO/amorphous ADD probe (China, Japan, Korea, Russia), petitioner JSW JFE Electrical Steel Nashik | initiated 22 Jun 2026 | 2026 | https://antidumping.vn/india-govt-launches-anti-dumping-probe-into-electrical-steel-imports-from-china-japan-korea-and-russ-n30350.html | UNVERIFIED |

**Mass per motor (ESTIMATED):** an 8108-class 36-slot stator, OD 81 mm, ID ≈ 40 mm, stack 8–10 mm, with ~50% removed for slots → ≈2,500 mm² × 9 mm × 7.65 g/cm³ ≈ **170 g of steel per stator**. At ₹100–250/kg that is **₹17–43 of steel**. Cutting cost dominates.

### 3.2 Cutting the laminations: laser vs wire EDM vs stamping

| Route | Cost data found | Source | Label |
|---|---|---|---|
| Wire EDM job work (India) | ₹0.12–0.20 per mm² of cut area (= cut length × thickness), e.g. ₹0.13, ₹0.16, ₹0.20/mm²; academic WEDM ₹1,200/h for industry (NIAMT) | snippet https://m.indiamart.com/impcat/wire-cutting-services.html ; https://niamt.ac.in/WriteReadData/EDM-CPDA-12092025.pdf | UNVERIFIED |
| → EDM of a glued/clamped stack (ESTIMATED) | 36-slot 81 mm stator: cut length ≈ OD 254 mm + 36 slots × ~20 mm + bore 126 mm ≈ 1,100 mm. × 10 mm stack = 11,000 mm² × ₹0.12–0.20 = **₹1,300–2,200 per stator stack** (+ rotor if inrunner) | arithmetic | ESTIMATED |
| Fiber-laser job work (India) | ₹40–500/sq ft, ₹150–200/kg (see mech file §6b; not repeated) | `india_mechanical_manufacturing_raw.md` §6b | UNVERIFIED |
| → per-lamination laser (ESTIMATED, low confidence) | 1,100 mm cut ≈ 10–20 s at thin-sheet speed + 40+ pierces; a job shop is likely to charge ₹15–40 per lamination → 28 laminations (0.35 mm, 10 mm stack) ≈ **₹400–1,100 per stack**, plus burr and heat-affected-zone (HAZ) loss | assumed rates | ESTIMATED |
| Laser vs stamping (research) | polystromata (multi-sheet) laser "37% less cost than stamping" but "79% more time" per stack; laser better for small machines | https://eprints.whiterose.ac.uk/192576 (Dodd et al., PLoS ONE 2022) | UNVERIFIED (snippet) |
| Chemical etching / water-jet-guided laser | etching is cost-effective for prototypes, with no tooling; WJGL gives negligible thermal damage | https://www.precisionmicro.com/motor-lamination-manufacturing-processes-a-comparison-of-stamping-laser-cutting-and-chemical-etching ; https://www.the-mtc.org/media/gbkdoslh/mtc-case-study-wjgl-of-electric-steel-laminations.pdf | UNVERIFIED |
| Stamping die (India) | "Motor Stamping Blank Die" ₹25,000 (Nissi Press Tools, Mumbai), a simple blanking die, not a progressive stator die | https://www.tradeindia.com/search.html?keyword=motor+stamping+die | VERIFIED listing |
| Progressive / compound die for a BLDC stator | **no price found** (searched India and China) | – | GAP. Get 2–3 quotes from fan-stamping houses (Taneja, Silicon Cortech, Pearl Engineering) |
| Stamped laminations from existing dies (India) | stator/rotor stampings ₹50–120/kg (Alliance Tools ₹50/kg, Kalburgi ₹120/kg, Shree Arya "skewed stator CRNO" ₹95/kg); Pearl Engineering ₹110–150 | https://www.tradeindia.com/search.html?keyword=bldc+stator+lamination ; snippet https://m.indiamart.com/pearl-engineering | VERIFIED listing / UNVERIFIED |
| Laser-cut / bonded lamination stacks (China) | "Laser cutting motor lamination, customisable prototype, glue bonding" US$0.10–10/pc, MOQ 1,000; "0.1 mm ultra-thin bonded motor core… stack" **US$500, MOQ 1 pc** (Huaci, Shenzhen) | https://www.made-in-china.com/products-search/hot-china-products/Laser_Cutting_Motor_Lamination.html ; …/Stator_Lamination_Stack.html | VERIFIED listing (first = placeholder) |
| Welded / interlocked / bonded stacks (China) | Shenyang Ruifeng US$1.78/pc welded or interlocked, US$0.38 bonded, MOQ 1,000 | …/Stator_Lamination_Stack.html | VERIFIED listing (placeholder-like) |
| Joining method notes | bonding (Backlack) has "no short cuts between the single sheets", better magnetic properties and lower loss, better thermal conductivity, less noise; interlocking struggles at 0.2 mm; cost and tolerance decide | https://voestalpine.com/isovac/it/Mediateca/News/Backlack-the-joining-technology-for-perfect-lamination-stacks ; https://www.emobility-engineering.com/content/uploads/magazines/EME012/71/ | UNVERIFIED (snippet) |

### 3.3 Coating and insulating the stator

| Item | Value | Source | Label |
|---|---|---|---|
| Epoxy powder (bulk, L&T SuFin) | "price on request" (5–10 kg packs) | https://lntsufin.com/product/epoxy-coating-powder-5-kg/17609-1110 | UNVERIFIED |
| Powder-coating job work (general, not stator-specific) | ₹12–40/ft², ₹30–65/kg, ₹60–120/pc (see mech file §6c) | `india_mechanical_manufacturing_raw.md` §6c | UNVERIFIED |
| Stator fluidised-bed epoxy coating job work in India | **not found** | – | GAP |

### 3.4 Ready-made stators and rotors

| Item | Seller | Price (list / sale) | Sold | URL | Date | Label |
|---|---|---|---|---|---|---|
| **8110 disc outrunner stator core 81×10 mm, 36N40P**, silicon steel | AliExpress item 3256812635607279 | US$11.41 / **10.50** | 15 | https://www.aliexpress.com/item/3256812635607279.html | 2026-10-06 | VERIFIED (search JSON) |
| 81×10 mm 36N40P stator core | AliExpress 3256811940316497 | US$15.87 / 12.54 | – | https://www.aliexpress.com/item/3256811940316497.html | 2026-10-06 | VERIFIED |
| **10010 stator core 36N42P** | AliExpress 3256806767815772 / 3256810357268070 / 3256812386577347 | US$20.76 / **10.38**; US$31.07; US$31.44 | 1 / 6 / – | https://www.aliexpress.com/item/3256806767815772.html | 2026-10-06 | VERIFIED |
| 10020 stator core 36N42P | AliExpress 3256812130300225 | US$27.42 / 18.92 | – | https://www.aliexpress.com/item/3256812130300225.html | 2026-10-06 | VERIFIED |
| 6110 stator core (24N28P), "2 pcs" | AliExpress 3256812162219702 | US$56.02 / 26.33 | – | https://www.aliexpress.com/item/3256812162219702.html | 2026-10-06 | VERIFIED |
| 6110 outer-rotor stator lamination | AliExpress 3256808052065426 | US$29.57 / 16.26 | 2 | https://www.aliexpress.com/item/3256808052065426.html | 2026-10-06 | VERIFIED |
| **8110 "outer rotor brushless motor stator… robot joint accessory"** (likely wound) | AliExpress 3256811400446151 | US$54.23 / **35.79** | 32 | https://www.aliexpress.com/item/3256811400446151.html | 2026-10-06 | VERIFIED |
| 8030 stator core | AliExpress 3256811670899650 | US$60.26 / 39.77 | 11 | https://www.aliexpress.com/item/3256811670899650.html | 2026-10-06 | VERIFIED |
| 13710 stator core 36N42P | AliExpress 3256813093430764 | US$74.47 | – | https://www.aliexpress.com/item/3256813093430764.html | 2026-10-06 | VERIFIED |
| 12-pole stator core OD 94 / ID 55.8 mm (and with rotor) | AliExpress 3256812957080563 / 3256809910658707 | US$49.34; with rotor US$74.10 | 6 / – | https://www.aliexpress.com/item/3256812957080563.html | 2026-10-06 | VERIFIED |
| Custom 77×39×12 mm stator + rotor core "OEM stamping" | AliExpress 3256812238692916 | US$264.46 / 137.52 | – | https://www.aliexpress.com/item/3256812238692916.html | 2026-10-06 | VERIFIED |
| Frameless robotic outer-rotor stator + reducer (PrimoPal) | AliExpress 3256811576162147 | US$465.72 / 433.12 | – | https://www.aliexpress.com/item/3256811576162147.html | 2026-10-06 | VERIFIED |
| CubeMars RI80 KV75 frameless (India, Robu) | ₹22,929 | – | see `india_robu_browser_sourcing_raw.md` | 2026-09-24 | (cross-ref) |
| **India: BLDC ceiling-fan stator stampings / stacks** (0.5 mm, 18-slot outer rotor, some 132 mm OD) | Taneja Stampings (Karnal) ₹90/kg; SPJ Solar (Ghaziabad) 18-pole 132 OD ₹100/kg; Silicon Cortech (Goa) "BLDC stator lamination stamping stack ₹90/piece" and "18 pole plastic over-moulded wound stator ₹90/piece"; range ₹75–117/kg | snippet https://m.indiamart.com/tanejastampings ; https://m.indiamart.com/siliconcortech/silicon-cortech.html | 2026-10-06 | UNVERIFIED |

**Insight (analysis):** India already mass-stamps outer-rotor BLDC stators for the ceiling-fan industry (BEE star-rating push). These are 0.5 mm, large OD and short stack, so they are not optimal for a QDD. Still, a fan-stator stamper with existing presses is the most realistic domestic route to **custom-die** laminations, and it may be able to supply off-the-shelf outer-rotor stacks for first prototypes. Chinese 8110/10010 cores at US$10–31 are the cheapest way to start.

---

## 4. OTHER ACTUATOR PARTS

### 4.1 Crossed-roller bearings (China; India prices are in mech file §1d)

| Item | Seller | Price (list / sale) | MOQ / sold | URL | Date | Label |
|---|---|---|---|---|---|---|
| **CRBH3510** (35×60×10) | Luoyang Monton Bearing (MIC) | **US$12.98** ("CRBH3010/3510") and **US$19.00** ("CRBH3510/4010/4510") | 1 pc | https://www.made-in-china.com/products-search/hot-china-products/CRBH3510.html | 2026-10-06 | VERIFIED listing |
| CRBH3510 "HXHV" | MIC seller | US$34.93–35.73 | 1 pc | same | 2026-10-06 | VERIFIED listing |
| CRBH series 3010/3510 | MIC seller | US$60.60–120 | 10 pcs | same | 2026-10-06 | VERIFIED listing |
| CRBH5013 (50×80×13) | Luoyang Monton | US$12.98–15.00 | 1 pc | https://www.made-in-china.com/products-search/hot-china-products/CRBH5013.html | 2026-10-06 | VERIFIED listing |
| CRBH5013 HXHV / "high precision" | MIC sellers | US$40.48–41.28 / US$99–199 | 1 | same | 2026-10-06 | VERIFIED listing |
| CRBH robot-joint series (208…11020) UUT1P5 | AliExpress 3256808446020201 | US$65.79 / 53.95 (default SKU) | – | https://www.aliexpress.com/item/3256808446020201.html | 2026-10-06 | VERIFIED (SKU ambiguous) |
| IKO CRBH3510A UU (genuine?) | AliExpress | US$343 / 315.56 | – | https://www.aliexpress.com/w/wholesale-CRBH3510-crossed-roller-bearing.html | 2026-10-06 | VERIFIED |
| **RU42 (20×70×12) GZN UUCC0P5 / CRBF2012AT** | AliExpress 3256809065790415 | US$58.23 / **40.18** | 24 sold | https://www.aliexpress.com/item/3256809065790415.html | 2026-10-06 | VERIFIED |
| XRU2012 (20×70×12, mounting holes) | AliExpress 3256812663367240 | US$34.85 / **26.84** | – | https://www.aliexpress.com/item/3256812663367240.html | 2026-10-06 | VERIFIED |
| **RU66 (35×95×15) CRBF3515** | AliExpress 3256806255845857 | US$79.50 / **50.88** | 54 sold | https://www.aliexpress.com/item/3256806255845857.html | 2026-10-06 | VERIFIED |
| **RU85 (55×120×15) CRBF5515** | AliExpress 3256808658286879 | US$91.22 / **66.59** | 18 sold | https://www.aliexpress.com/item/3256808658286879.html | 2026-10-06 | VERIFIED |
| RB10020 (100×150×20) | AliExpress 2261800078879173 | US$154.47 / 112.76 | 6 | https://www.aliexpress.com/item/2261800078879173.html | 2026-10-06 | VERIFIED |
| CRBTF305A (30×63×5, thin) | AliExpress 3256809307267416 | US$241 / 190 | 2 | https://www.aliexpress.com/item/3256809307267416.html | 2026-10-06 | VERIFIED |
| RU28–RU148 multi-SKU listings | AliExpress (TRH, MHCNC, generic) | US$18–174 (default SKU unknown) | up to 188 sold | https://www.aliexpress.com/w/wholesale-RU42-crossed-roller-bearing.html | 2026-10-06 | VERIFIED (SKU ambiguous) |
| → landed India, CRBH3510 at US$13–35 | × ₹96.38 = ₹1,250–3,370; + ~10% BCD (assumed) + 18% IGST + shipping ≈ **₹2,000–5,000** vs IKO ₹11,799 (IB) | | | | | ESTIMATED (duty rate assumed) |

### 4.2 Thin-section deep-groove (China reference; India in mech file §1a)

| Item | Price | URL | Date | Label |
|---|---|---|---|---|
| 6814-2RS / 61814 (70×90×10), 2 pcs | US$17.78 (2 pcs) → ≈US$8.9 each | https://www.aliexpress.com/item/2255800921950059.html | 2026-10-06 | VERIFIED / ESTIMATED each |
| 6814 ZZ 2 pcs | US$18.66 | https://www.aliexpress.com/item/3256801673985944.html | 2026-10-06 | VERIFIED |
| 6812 2RS (60×78×10), "1–4 pcs" | US$6.35 (default SKU) | https://www.aliexpress.com/item/2251832633230326.html | 2026-10-06 | VERIFIED (SKU ambiguous) |

### 4.3 Planetary gears

| Item | Seller | Price | URL | Date | Label |
|---|---|---|---|---|---|
| Module 1 spur gears, 45# steel, 12–60T | AliExpress (many) | US$3.3–7 typical; 42–56T 10 mm wide US$14.43 | https://www.aliexpress.com/w/wholesale-internal-ring-gear-module-1-steel.html | 2026-10-06 | VERIFIED |
| Module 1 stainless 304 spur 42–68T | AliExpress 3256803903508337 | US$11.59 / 9.27 | same | 2026-10-06 | VERIFIED |
| **Internal ring gear 0.6M 48T, metal** | AliExpress 3256809320393626 | US$2.92 / **2.69** | https://www.aliexpress.com/item/3256809320393626.html | 2026-10-06 | VERIFIED |
| E-bike (Bafang) planetary set: 36T planets + 70 mm clutch + **93T steel ring** | AliExpress 3256807215436480 | US$46.37 | https://www.aliexpress.com/item/3256807215436480.html | 2026-10-06 | VERIFIED (an off-the-shelf steel planetary set to repurpose) |
| 3 × e-bike planetary gears 36T steel (Bafang) | AliExpress 3256805792146845 | US$10.01 (677 sold) | https://www.aliexpress.com/item/3256805792146845.html | 2026-10-06 | VERIFIED |
| SDP/SI module 0.8 carbon-steel spur (KSSY0.8-25) | US$9.31–10.56 | https://shop.sdp-si.com/kssy08-25.html | 2026-10-06 | UNVERIFIED (snippet) |
| Custom hardened (carburised) planetary sets, module 0.5–1, China | listings only ("M1–M8, quench and temper or carburise"); no price | https://pto-shaft.com/?p=40073 | 2026-10-06 | UNVERIFIED |
| India: steel m0.5–1 gears off the shelf | none in stores (mech file §4 and §10); custom gear hobbing job-work rates **not published** (DG Panchal, Ahmedabad offers gear hobbing job work, no price) | https://m.indiamart.com/dgpanchal/new-items.html | 2026-10-06 | GAP |

### 4.4 FOC driver ICs and passives: China prices (JLCPCB parts library, USD, read 2026-10-06)

Source for every row: JLCPCB public parts API (`https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList`), searched from https://jlcpcb.com/parts. The library is the LCSC catalogue. Prices are shown in USD on jlcpcb.com (currency field not checked; assumed USD). Label: **VERIFIED** (JSON). The Indian prices for the same parts are in the electronics file (§A2 STM32G431CBT6 ₹572 incl at Evelta; §A3 transceivers) and the Robu file (DRV8323RS ₹380 OOS, DRV8353RH ₹629 OOS, MT6835 module ₹619).

| Part | LCSC # | Brand | Stock | 1+ | 10+ | 100+ |
|---|---|---|---|---|---|---|
| STM32G431CBU6 (QFN48) | C529356 | ST | 4,156 | 7.91 | 7.00 | 5.85 |
| STM32G431CBT6 (LQFP48) | C529355 | ST | 4,039 | 5.39 | 4.69 | 3.81 (250+) |
| STM32G474RET6 (LQFP64) | C521608 | ST | 397 | 13.54 | 11.91 | 10.14 |
| DRV8353RSRGZR (100 V, 3 CSAs) | C506246 | TI | 1,744 | 5.75 | 5.22 | 4.60 |
| DRV8323RSRGZR (60 V) | C545497 | TI | 0 | 5.67 | 5.55 | 5.38 |
| DRV8316RRGFR (40 V integrated FETs, 8 A) | C5218861 | TI | 2,793 | 4.53 | 4.00 | 3.37 |
| FD6288Q-type gate driver (JSM6288Q) | C19077370 | JSMSEMI | 31,267 | 0.50 | 0.39 | 0.29 |
| MT6835GT-STD-R (21-bit magnetic) | C2932578 | MagnTek (listed "NOVOSENSE") | 1,956 | 4.87 | 4.28 | 3.53 |
| MA732GQ-Z | C3824836 | MPS | 603 | 4.76 | 4.34 (50+) | 4.17 |
| MA600GQ-Z | C7434430 | MPS | 0 | price placeholder | – | – |
| AS5047P-ATSM | C962063 | ams | 4,150 | 4.72 | 4.19 | 3.23 |
| TLE5012BE1000 | C123083 | Infineon | 6,666 | 4.07 | 3.63 | 2.67 |
| BSC070N10NS5 (100 V, 7 mΩ, SuperSO8) | C534364 | Infineon | 15,006 | 0.58 | 0.49 | 0.32 |
| BSC016N06NS (60 V, 1.6 mΩ) | C454269 | Infineon | 10,849 | 1.15 | 0.95 | 0.71 |
| IPT015N10N5 (100 V, 1.5 mΩ, TOLL) | C108964 | Infineon | 29,992 | 1.87 | 1.67 | 1.25 |
| NCEP6080AG (60 V, DFN5×6) | C182469 | Wuxi NCE | 2,600 | 0.89 | 0.71 | 0.52 |
| TCAN1044VDRQ1 (CAN FD) | C1852061 | TI | 13,224 | 0.44 | 0.35 | 0.26 |
| TJA1051T/3/1J | C38695 | NXP | 287,227 | 0.57 | – | 0.47 (500+) |
| SIT1044QT/3 (CAN FD, Chinese) | C5121967 | SIT | 9,921 | 0.52 | 0.42 | 0.32 |
| INA240A2DR (current-sense amp) | C2060768 | TI | 6,239 | 1.74 | 1.45 | 1.11 |
| INA181A2IDBVR | C2058784 | TI | 22,129 | 0.33 | 0.27 (50+) | 0.20 (500+) |
| Shunt 2512 1 mΩ 1% (RALEC LR2512-22R001F4) | C154668 | RALEC | 4,155 | 0.096 | 0.077 (50+) | 0.061 (500+) |
| NTC 10 k 0603 (Murata NCP18XH103F03RB) | C13564 | Murata | 240,228 | 0.046 | 0.039 (100+) | 0.032 (1000+) |
| LMR38010SDDAR (80 V, 1 A buck) | C5219310 | TI | 453 | 0.93 | 0.74 | 0.52 |
| TPS54360BDDAR (60 V, 3.5 A buck) | C524806 | TI | 59,580 | 0.75 | 0.63 | 0.46 |
| AMS1117-3.3 (UMW) | C347222 | UMW | 914,811 | 0.049 | 0.038 (100+) | 0.026 (2500+) |
| XT30PW-M (Amass) | C431092 | Amass | 31,629 | 0.38 | 0.33 | 0.26 |

### 4.5 FOC driver board BOM estimate (48 V, ~30 A peak, CAN FD, onboard encoder): ESTIMATED

Assumption: a moteus-c1/ODrive-Micro-class single-axis board, 4-layer, ≈40×40 mm, 10 boards. JLCPCB 10+ prices from §4.4.

| Line | Part | Qty | US$ each | US$ |
|---|---|---|---|---|
| MCU | STM32G431CBU6 | 1 | 7.00 | 7.00 |
| Gate driver + 3 CSA | DRV8353RS | 1 | 5.22 | 5.22 |
| Power FETs | BSC070N10NS5 | 6 | 0.49 | 2.94 |
| Encoder IC | MT6835GT | 1 | 4.28 | 4.28 |
| Encoder magnet | 6×2.5 diametric | 1 | 0.36 | 0.36 |
| CAN FD transceiver | TCAN1044V | 1 | 0.35 | 0.35 |
| Bus buck + LDO | LMR38010 + AMS1117 | 1+1 | 0.74 + 0.05 | 0.79 |
| Shunts | 1 mΩ 2512 | 3 | 0.096 | 0.29 |
| NTC | 10 k 0603 | 1 | 0.05 | 0.05 |
| Bulk and ceramic 100 V caps, ~60 passives | assumed | – | – | 2.10 |
| Connectors (XT30 + 2× JST-GH) | – | – | – | 0.73 |
| **Parts subtotal** | | | | **≈ 24.1** |
| PCB 4-layer, 10 pcs | assumed US$1–3/board | | | 1–3 |
| Assembly at JLCPCB economic tier: setup US$8.18 + stencil 1.53 + ~10 extended parts × 3.07 + ~300 joints × US$0.0016 × 10 boards → ≈US$45 per order | per board | | | ≈4.5 |
| **Ex-works per board** | | | | **≈ US$30–32** (₹2,900–3,100) |
| Landed India (+ DHL US$12–25 per order + BCD/IGST, assumed +30–40%) | | | | **≈ US$40–45 (₹3,900–4,300)** |

Assembly fee source: https://jlcpcb.com/help/article/pcb-assembly-price (setup Economic US$8.18, Standard US$25.56; stencil US$1.53 / 8.21; US$0.0016/joint; extended-part loading US$3.07 Economic / 1.53 Standard; "single board assembly surcharge: $0.48 minimum per board"). VERIFIED 2026-10-06. Shipping, duty and KYC are from the Zbotic guide (snippet; India requires consignee KYC; "DHL Express shipping cost: $12–25 USD"): https://zbotic.in/pcb-assembly-service-india-jlcpcb-vs-local-fab-cost-guide/. UNVERIFIED.

**Compare (cross-refs):** B-G431B-ESC1 US$39.26 (ST eStore, 24 V class, actuator file §5); moteus-c1 US$69; ODrive Micro US$89; ODESC V4.2 US$34.99–43.99; Robu NDrive Z1 ₹13,999; MKS XDrive Mini ₹4,999 (OOS).

### 4.6 PCB assembly in India

| Provider | Data | URL | Label |
|---|---|---|---|
| Lion Circuits (Bengaluru) | "No MOQ"; instant quote needs BOM + Gerber; **no public PCBA price** | https://lioncircuits.com/pcb-assembly | VERIFIED (no price) |
| PCB Power (Gujarat) | "Assembly lead time can start from 1 working day"; no fixed rate published (blog 21 May 2026) | https://www.pcbpower.com/blog-detail/surface-mount-technology-assembly-cost-india | VERIFIED (no price) |
| Generic Indian PCBA (blog) | setup ₹3,000–15,000; per board ₹200–2,000 | snippet https://zbotic.in/pcb-assembly-services-in-india-pcba-complete-guide/ | UNVERIFIED |
| Bare-PCB comparison | see mech file §6e (Lion Circuits 5 × 100×100 2-layer ₹1,877 ex-GST) | – | (cross-ref) |

---

## 5. METAL 3D PRINTING AND CNC RATE (India vs China)

| Item | Value | Source | Date | Label |
|---|---|---|---|---|
| India DMLS, all metals (iamRapid cost guide) | "₹50–150 per gram depending on the metal alloy"; per part ₹5,000–50,000+; AlSi10Mg "₹15,000–30,000/kg"; Ti6Al4V "₹20,000–40,000/kg"; Ti bracket ~100 g ₹15,000–25,000 | https://iamrapid.com/knowledge-hub/3d-printing-cost-guide/ | 19 Mar 2026 | VERIFIED (vendor blog figures) |
| → ₹/cm³ | AlSi10Mg (2.68 g/cm³): ₹40–80/cm³ (₹15–30/g × 2.68); steels (7.8 g/cm³) at ₹50–150/g: ₹390–1,170/cm³ | arithmetic | – | ESTIMATED |
| iamRapid DMLS service | AlSi10Mg and Ti6Al4V ELI active; FAQ lists 316L, 17-4PH, Inconel 625/718, CoCr; build 250×250×325 mm; 20–60 µm; ±0.1 mm; **7–10 business days** (Bengaluru 24 h fastest) | https://iamrapid.com/3d-printing-services/dmls/ | 2026-10-06 | VERIFIED |
| Wipro3D (Bengaluru) | metal AM services and machines (with IISc; Nikon SLM partnership); no public price | https://www.metal-am.com/?p=101143 ; https://www.cbinsights.com/company/wipro-3d | 2026-10-06 | UNVERIFIED |
| Think3D, Imaginarium (Mumbai), Objectify | metal AM listed, quote forms only (see mech file §6d for their polymer services) | https://www.cbinsights.com/compare/imaginarium-1-vs-think3d | 2026-10-06 | UNVERIFIED |
| Maraging steel (MS1) price in India | **not found** | – | – | GAP |
| JLC3DP SLM-316L (China) | "$0.24 → $0.21 per gram" (−12.5%), effective 13 Aug 2025 | https://jlc3dp.com/blog/drastic-material-price-cuts-and-adjusted-post-processing-service-fees | 2025-08-13 | VERIFIED |
| → ₹/cm³ | 0.21 × 7.9 g/cm³ = US$1.66/cm³ ≈ **₹160/cm³** (+ shipping/duty) | arithmetic | – | ESTIMATED |
| JLC3DP Jul 2026 update | "Titanium TC4 ↓ 47%", effective 24 Jul 2026; BJ-316L binder-jet available; no per-gram numbers in the notice | https://jlc3dp.com/news/materials-finishing-pricing-update-july2026 | 2026-07 | VERIFIED |
| JLC3DP AlSi10Mg / 17-4PH price | **not found** (needs instant-quote upload) | – | – | GAP |
| India CNC hourly rate | see mech file §6a (Robocon CNC blog: 3-axis US$20–38/h ≈ ₹1,900–3,600/h; 5-axis US$38–65/h) | `india_mechanical_manufacturing_raw.md` §6a | – | (cross-ref) |
| China CNC hourly rate | conflicting: "3-axis as low as US$5/h; 5-axis US$10–30/h" (GR Prototypes, ~Sep 2024) vs "3-axis US$30–60/h, 5-axis US$80–150/h" (Alibaba seller blog 2026) | https://grprototypes.com/blog/how-much-will-cnc-machining-cost-in-china-in-2024/ ; https://seller.alibaba.com/blogs/2026/southeast-asia/machinery/cnc-machining-service-cost-guide-precision-manufacturing-alibaba | 2026-10-06 | UNVERIFIED |

---

## 6. COIL WINDING EQUIPMENT, CONSUMABLES, TEST EQUIPMENT

### 6.1 Winding machines

| Item | Seller | Price | URL | Date | Label |
|---|---|---|---|---|---|
| Hand-crank winder with 0–99,999 counter, 0.02–2.6 mm wire | AliExpress 3256811564555385 | US$100.12 / **24.04** (300 sold) | https://www.aliexpress.com/item/3256811564555385.html | 2026-10-06 | VERIFIED |
| NZ-1 hand winder with chuck, 0–999 counter | AliExpress 3256812407102092 / 3256811766636020 | US$39.04 / US$25.30 | https://www.aliexpress.com/w/wholesale-manual-coil-winding-machine-counter.html | 2026-10-06 | VERIFIED |
| Manual winder with counter (dual-purpose) | AliExpress 3256808459888298 | US$77.13 / 40.11 | same | 2026-10-06 | VERIFIED |
| "Automatic CNC coil winding machine… motor stator brushless motor winder" | AliExpress 3256810553996378 | US$263.32 | https://www.aliexpress.com/w/wholesale-brushless-motor-stator-winding-machine.html | 2026-10-06 | VERIFIED (likely a bobbin winder, not a needle winder) |
| 750 W programmable CNC coil winder 0.01–2.5 mm (bobbin) | AliExpress 3256812119987129 | US$3,032.70 / 1,334.39 | same | 2026-10-06 | VERIFIED |
| BLDC 2-station stator winding machine | AliExpress 3256810490052363 | US$17,404.59 | same | 2026-10-06 | VERIFIED |
| Automatic stator copper-wire winding machine (vertical) | AliExpress 3256810092795954 | US$25,115.32 | same | 2026-10-06 | VERIFIED |
| Six-axis BLDC stator winding machine | Zhengzhou Dream Machinery (MIC) | US$8,999 | https://www.made-in-china.com/products-search/hot-china-products/BLDC_Stator_Winding_Machine.html | 2026-10-06 | VERIFIED listing |
| BLDC stator winding machine (automotive) | Shenzhen Jiuju (MIC) | US$5,000 | same | 2026-10-06 | VERIFIED listing |
| Ceiling-fan/BLDC stator winder | MIC sellers | US$5,000–30,000 | same | 2026-10-06 | VERIFIED listing |
| Outer-stator (outrunner) needle winder "for brushless motor" | Shenzhen High-Flyer (MIC) | US$10,000; other seller US$17,999–18,999 | https://www.made-in-china.com/products-search/hot-china-products/Outer_Stator_Winding_Machine.html | 2026-10-06 | VERIFIED listing |
| Flying-fork BLDC winder (production) | Guangdong Zongqi (MIC) | US$100,000 | BLDC page above | 2026-10-06 | VERIFIED listing |
| India: manual motor coil winder | Rajlaxmi Machine Tools (Rajkot) ₹2,800 (MOQ 20); Satyam ₹4,500 (MOQ 10); NIJ Shyam ₹3,600–14,000; Bhagwati ₹15,000; Tesca (with reel carrier) ₹40,000 | https://www.tradeindia.com/search.html?keyword=coil+winding+machine+manual | 2026-10-06 | VERIFIED listing |
| India: hand ceiling-fan stator winder | Tahseen Machine Mart (Delhi) ₹10,500; Nishan Electric ₹13,500; Kisan Engg 2-in-1 ₹18,000 | same | 2026-10-06 | VERIFIED listing |
| India: semi-automatic fan stator winder | Tahseen ₹12,500 (1/6 hp); Satyam ₹27,000; Venu Rewinding Works ₹25,500 | https://www.tradeindia.com/search.html?keyword=automatic+stator+winding+machine | 2026-10-06 | VERIFIED listing |
| India: CNC ceiling-fan stator rewinder (KIJ 150) | Kisan Engineering (Jind) ₹2,00,000 | same | 2026-10-06 | VERIFIED listing |

### 6.2 Insulation and impregnation consumables

| Item | Seller | Price | URL | Date | Label |
|---|---|---|---|---|---|
| Dr. Beck (Elantas) insulating varnish, red | TradeIndia seller | ₹295/kg (MOQ 1 kg) | https://www.tradeindia.com/search.html?keyword=insulating+varnish | 2026-10-06 | VERIFIED listing |
| Dr. Beck Elmotherm F 50 (class F) | Harnawa Insulations | ₹330/kg (MOQ 1 kg) | https://www.tradeindia.com/search.html?keyword=winding+varnish | 2026-10-06 | VERIFIED listing |
| Dr. Beck insulation varnish, black/clear | Damani Sales Agency | ₹240/L (MOQ 15 L) | same | 2026-10-06 | VERIFIED listing |
| Generic insulating varnishes | various | ₹99–180/kg or /L | same | 2026-10-06 | VERIFIED listing |
| Elantas Beck India class H/200 °C resins | "solvent-borne varnishes and solvent-less resins up to a thermal class of 200 °C"; no price | https://pt.elantas.com/beck-india/products/electrical-insulation-system/electrical-insulating-varnishes-resins.html | 2026-10-06 | UNVERIFIED (snippet); class-H price = GAP |
| Nomex 410 / aramid paper (India) | ₹630/kg "DuPont Nomex unprinted" (Shiv Trading, MOQ 100 kg); ₹900/kg (Damani, 50 kg); "class H Nomex" ₹4,950/kg (PD Transformer Insulation, 10 kg); ₹7,000/kg (Suman Intl, 5 kg); ₹4,000/kg (Adisha, 50 kg) | https://www.tradeindia.com/search.html?keyword=nomex+insulation+paper | 2026-10-06 | VERIFIED listing (wide spread; ₹630–900 is probably not genuine T410) |
| Nomex 410 A4 sheet (China) | AliExpress 3256806836026805 US$31.24; X-FIPER "replacing Nomex T410" US$35.04 | https://www.aliexpress.com/w/wholesale-nomex-paper-insulation.html | 2026-10-06 | VERIFIED (pack size n/s) |
| Aramid/Nomex tape 0.09 mm × 50 m | AliExpress 3256807159241558 US$9.79 / 7.15 | same | 2026-10-06 | VERIFIED |
| Nomex NMN 6640 laminate | AliExpress 3256806800620759 US$36.00 | same | 2026-10-06 | VERIFIED |
| DMD (class F/155) | ₹190/kg (950 mm wide, MOQ 50 kg); ₹220/kg (Accurate Industrial, 10 kg); ₹400/kg (Ganapathy, 500 kg) | https://www.tradeindia.com/search.html?keyword=dmd+insulation+paper | 2026-10-06 | VERIFIED listing |
| Heat-shrink, slot wedges, lead wire (PTFE/silicone) | not researched in detail (cheap; Robu/AliExpress) | – | – | GAP (low impact) |

### 6.3 Test equipment

| Item | Seller | Price | URL | Date | Label |
|---|---|---|---|---|---|
| Hipot tester RK2670YM AC 5 kV 20 mA | AliExpress 3256812208504518 | US$111.12 | https://www.aliexpress.com/w/wholesale-hipot-tester-5kv.html | 2026-10-06 | VERIFIED |
| Hipot RK2670AM 5 kV / RK2672AM AC/DC 5 kV | AliExpress | US$200.63 / 216.75 | same | 2026-10-06 | VERIFIED |
| Programmable hipot RK9320 (AC 5 kV / DC 6 kV) | AliExpress | US$483–505 | same | 2026-10-06 | VERIFIED |
| India hipot testers | Kamla Electricals 0–2.8 kV DC ₹10,000; Yashika "hipot + IR" ₹10,600; DGSY breakdown tester ₹13,500; Jogeshwari ₹39,000; up to ₹2–10 lakh for HV units | https://www.tradeindia.com/search.html?keyword=hipot+tester | 2026-10-06 | VERIFIED listing |
| Impulse (surge) winding tester, China | UNI-T U9845 4-ch 100–5,000 V US$1,427.58; Tonghui TH2883 US$1,968.76; UCE UC5815 US$1,781.25; Huazheng HZ-6300C US$3,579.55 | https://www.aliexpress.com/w/wholesale-impulse-winding-tester.html | 2026-10-06 | VERIFIED |
| Surge comparison tester, India | Permax ₹25,000 (MOQ 2); Fijosa 6 kV ₹1,20,000; Sivananda (Nashik) ₹1,50,000; Motwane ₹1,80,000 | https://www.tradeindia.com/search.html?keyword=surge+comparison+tester | 2026-10-06 | VERIFIED listing |
| LCR meter Tonghui TH2830 / TH2822 class | AliExpress | US$367.53–480.42 | https://www.aliexpress.com/w/wholesale-LCR-meter-TH2830.html | 2026-10-06 | VERIFIED |
| Hysteresis brake (HB series), dyno load | AliExpress 3256812597593773 / 3256811686279505 / LB hollow 3256809079386784 | US$285.42 / 125.61 / 165.01 | https://www.aliexpress.com/w/wholesale-hysteresis-brake-dynamometer.html | 2026-10-06 | VERIFIED (rated torque n/s; small-torque units) |
| Eddy-current brake dyno (small) | AliExpress | US$2,677–3,745 | same | 2026-10-06 | VERIFIED |
| Rotary torque sensor DYN-200 (10–100 N·m) | AliExpress 3256811976842931 | US$838 / **703.92** (12 sold) | https://www.aliexpress.com/w/wholesale-rotary-torque-sensor.html | 2026-10-06 | VERIFIED |
| Rotary torque transducer 0–50 N·m, 0.1% FS | AliExpress 3256805067064824 | US$104.29 / 95.95 (spec claim doubtful at this price) | same | 2026-10-06 | VERIFIED listing |
| Magnetizer (capacitor-discharge) + multipole fixture | **no price found** | https://e-magnetsuk.com/magnetising-equipment/ (no prices) | 2026-10-06 | GAP. Alternative: buy pre-magnetised segments and assemble with a jig (standard hobby/QDD practice) |
| CNC wire-cut EDM machine (India, capex reference) | FDK 7725 ₹5.71 lakh; Simos ₹7.85 lakh; others ₹8.5–13.5 lakh | https://www.tradeindia.com/search.html?keyword=wire+cut+edm+machine | 2026-10-06 | VERIFIED listing |
| Fiber laser cutter (India, capex reference) | ₹22.5–43.5 lakh (1–6 kW, 3015/6015 beds) | https://www.tradeindia.com/search.html?keyword=fiber+laser+cutting+machine | 2026-10-06 | VERIFIED listing |

---

## 7. GAPS / NOT FOUND (2026-10-06)

| Gap | Why | Suggested next step |
|---|---|---|
| Robu / Amazon.in / IndiaMART retail magnet wire (0.3–1.0 mm, class 180–200) | Robu 403, Amazon 503, IndiaMART 429 | browser session or phone; ask an RR Kabel or Precision Wires distributor for a class 200 dual-coat ₹/kg quote |
| Current Indian ₹/kg for class 200 EI/AIW | no maker publishes prices; listings stale | 2–3 distributor quotes; sanity floor ≈ ₹1,360/kg copper content |
| Chinese finished-magnet ₹/kg for N45SH/N48H arcs at 1k–10k pcs | Alibaba captcha; SMM paywalled; MIC ranges are placeholders | RFQ to 3 Ningbo makers with drawing; ask for Dy/Tb content and licence status |
| Whether Chinese finished motors / stator-rotor kits need an export licence | not covered by sources read | ask the supplier / MOFCOM guidance |
| 0.2 mm NGO (20WTG1500 / B20AT1500) price and Indian availability | none found (only CRGO 0.2 mm) | ask JSW JFE / Baosteel agents; Indian importers |
| Progressive / compound stator die cost | not published | quotes from fan-stator stampers (Taneja Karnal, Silicon Cortech Goa, Pearl Engg) |
| Stator epoxy (fluidised-bed) coating job work | not found | local motor-rewinding / coating shops |
| India gear hobbing / shaping job rates for m0.5–1 | not published | DG Panchal or local gear shops; or JLCCNC / Chinese gear makers |
| JLC3DP AlSi10Mg and 17-4PH per-gram; India maraging/17-4PH | quote tool needs upload | upload test part to JLC3DP / iamRapid |
| Magnetizer and fixture price | none | assemble pre-magnetised arcs (avoid) |
| Class-H (200 °C) varnish ₹/kg | only class F prices seen (₹240–330) | Elantas Beck distributor quote |
| Exact India BCD on NdFeB magnets / bearings / PCBA | classification ambiguous | CBIC tariff lookup |
| AliExpress per-SKU prices | product pages need JS | the "default SKU" caveat applies to every AE row |

<!-- END india_motor_materials_raw.md (2026-10-06) -->
