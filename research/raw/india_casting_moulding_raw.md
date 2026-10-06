# JX1: India casting and moulding for actuator housings (and gears), raw research log

- **Purpose:** source data for a "casting and moulding" section of the technical paper. The reference part is an aluminium actuator housing, about Ø120 mm × 70 mm, 250–500 g finished. Bearing seats need ±0.01 mm, so **every route below still ends in CNC finish-machining**. Casting only changes the blank.
- **Research date:** 2026-10-06. Rows marked VERIFIED were read from the live page on that date (IndiaMART pages fetched with curl and parsed, other pages with WebFetch).
- **FX for [E] conversions:** 1 USD = ₹96.38 = CNY 6.7145. Source: https://open.er-api.com/v6/latest/USD (`time_last_update_utc` Tue, 06 Oct 2026 00:02:31 UTC). This is the same rate used elsewhere in the repo.
- **Method limits:**
  - IndiaMART rate-limits WebFetch (HTTP 429), so pages were fetched with curl from a mobile user agent and the static HTML was parsed.
  - Several `impcat` slugs return 404 (for example aluminium-sand-casting, sintered-parts and silicone-mould). The data comes from the slugs that resolved.
  - The WebSearch budget ran out near the end of the session. Some technical figures therefore rest on search-engine snippets and are marked UNVERIFIED.
  - No quotes were requested and no forms were submitted.
- **Related repo files:**
  - `india_mechanical_manufacturing_raw.md`: 6061 bar/plate prices, CNC services, Makenica urethane-casting anchor.
  - `china_actuator_manufacturing_economics_raw.md`: RobStride die-cast housings and PM gears.

### Label legend
| Label | Meaning |
|---|---|
| **VERIFIED** | The number was read on the live page (or its static HTML) on 2026-10-06. For IndiaMART this only proves the listing says it. It does **not** prove the vendor will honour it. |
| **ESTIMATED** | Derived number. The method or math is shown. |
| **UNVERIFIED** | Taken from a search snippet, a marketing blog, a third-party claim or memory of a standard that was not opened. Confirm before relying on it. |
| **NOT FOUND** | Searched and no public figure was found. |

IndiaMART caveat: "₹/kg" listing prices are **ex-works, usually GST-extra (18 %)**. They are often the lowest price for a bulk, repeat order, and many sellers type a placeholder price. Treat them as **order-of-magnitude leads**. A one-off 5–20-piece job will cost more per kg, and many foundries set a minimum batch value.

---

## 0. Quick view (all ₹, ex-GST unless noted)

| Route | Tooling / pattern | Per housing (casting only) | Tolerance as cast | Fit for JX1 |
|---|---|---|---|---|
| Green-sand casting, LM25/LM6/A356 | Wood pattern ₹456–15,000 (listings); FDM-printed pattern ₹5,000 (listing) or about ₹100–200 of PLA if self-printed | ≈ ₹150–380 at ₹250–420/kg × 0.6–0.9 kg as-cast [E] | about ±0.5–1 mm on 120 mm [UNVERIFIED]; Ra 12.5–50 µm [UNVERIFIED] | **Best low-volume metal route** (10–500 pcs). Machine all functional faces. |
| Gravity die (permanent mould) | Die ₹45,000–2,01,000 (listings) | ≈ ₹140–420 (₹310–600/kg × 0.45–0.7 kg) [E] | better than sand; about ±0.3–0.5 mm [UNVERIFIED] | 500–5,000 pcs |
| HPDC (ADC12/A380/LM24) | Die ₹1.8–6 lakh for listed Al HPDC dies; ₹2–6 lakh is realistic for this part [E] | ≈ ₹70–250 metal + die amortisation (₹200–600 at 1k pcs, ₹20–60 at 10k) [E] | NADCA precision ±0.002 in/in → about ±0.14 mm on 120 mm [E from UNVERIFIED] | ≥ 5–10k pcs; cannot be normally T6'd (blistering) |
| Investment (lost wax), Al | Wax die ₹5,000–1,00,000 (listings) | Al ₹350/kg listing; steel ₹250–650/kg | Ra 1.6–6.3 µm [UNVERIFIED] | Better for small steel parts (carriers, brackets) than for a 120 mm Al housing |
| Lost-PLA (DIY or jobbing) | Printed pattern (₹ tens); burnout kiln ₹24,500–55,000 | Investment ≈ ₹190–590 per flask [E] | as investment, with PLA ash/surface risk | Prototype route only |
| Vacuum/urethane casting (plastic) | Silicone mould: ₹1,600–7,600 of RTV [E]; vendor ≈ $200–500 [UNVERIFIED] | ₹90–5,000/pc listings; Makenica FAQ ₹4,000/part | about ±0.1 mm [UNVERIFIED] | Covers, prototypes; not a load-bearing housing |
| Plastic injection moulding (PA66-GF30/PPS) | Al proto ≈ $1,500+ (Protolabs); India steel 2-plate $3.5–8k (₹3.4–7.7 lakh) [UNVERIFIED] | ≈ ₹50–300 [E] | ±0.003 in + resin shrink (Protolabs) | Covers and non-bearing parts at ≥1k pcs |
| MIM (steel) | ₹2.3–2.75 lakh MIM moulds (listings); $10–100k [UNVERIFIED] | ₹20–150/pc listings | needs finishing for gears | Small planets/sun ≤ 50 g at ≥ 5k/yr |
| PM sintered gears | NOT FOUND (India) | ₹5–100/pc listings; density 6.6–7.3 g/cc | – | Low-cost planets; fatigue lower than wrought |

---

## 1. Aluminium sand casting (job work), India

### 1a. Price per kg (IndiaMART listings, fetched 2026-10-06)
| Seller (city) | Product / alloy | ₹ | Unit | Stated specs | URL | Label |
|---|---|---|---|---|---|---|
| Inticore Engineering (Coimbatore) | Aluminium sand casting, **LM25**, green sand | 420 | kg | casting weight 1–5 kg, automotive | https://m.indiamart.com/inticore-engineering/new-items.html | VERIFIED (listing) |
| Inticore Engineering (Coimbatore) | Dry-sand casting, hand moulding | 600 | kg | 5–20 kg | same | VERIFIED (listing) |
| Inticore Engineering (Coimbatore) | Gravity die casting **LM6** | 490 | **piece** | part weight "up to 500 gm", pump/motor parts | same | VERIFIED (listing) |
| Ardent Engineering (Coimbatore) | Sand casting components, **LM25**, "polished" | 250 | kg | – | https://m.indiamart.com/ardent-engineering-coimbatore/sand-casting-components.html | VERIFIED (listing) |
| Ardent Engineering (Coimbatore) | Aluminium sand castings | 330 | kg | – | same | VERIFIED (listing) |
| Ardent Engineering (Coimbatore) | Investment casting wax | 300 | kg | (consumable) | same | VERIFIED (listing) |
| Super Tech Industries (Coimbatore; est. 2007; GDC and green-sand specialist) | Aluminium sand casting, gravity-fed | 370 | kg | page also mentions no-bake sand | https://m.indiamart.com/super-tech-inds/sand-casting.html | VERIFIED (listing) |
| Sigma Techno Cast (Surat) | LM25 / ADC12 / LM24 sand casting; shot-blast, anodise, powder coat | 390 | kg | – | https://m.indiamart.com/sigma-techno-cast/ | VERIFIED (listing) |
| Sigma Techno Cast (Surat) | LM25 sand casting / LM24 / LM02 / ADC12 | 360 / 385 / 335 / 350 | kg | "machining facilities and all post process" | same | VERIFIED (listing) |
| Sigma Techno Cast (Surat) | Aluminium casting with "short blasting, **heat treatment**" | 295 | kg | automotive | same | VERIFIED (listing) |
| Gajanand Aluminium (via GDC category) | price table: LM6 ₹380/kg, LM25 ₹390/kg, LM9 ₹400/kg | 380–400 | kg | GDC and sand castings | https://m.indiamart.com/impcat/gravity-die-casting.html | VERIFIED (listing) |
| **Range, Al sand casting** | 9 listings | **₹250–420/kg (green sand); dry sand ₹600/kg** | – | – | above | ESTIMATED from VERIFIED listings |

A356 is sold as "LM25 / AlSi7Mg / A356" (the BS 1490 LM25 datasheet cross-references A357.0 and AA601/AC601). No India listing separately prices "A356"; treat it as an LM25 price.

### 1b. Patterns
| Item | ₹ | Source | Label |
|---|---|---|---|
| Teak split pattern (green/CO₂/no-bake sand; gearbox/housing/pump) | 456 / piece | Sitara Engineering Works, https://m.indiamart.com/impcat/wooden-pattern.html | VERIFIED (listing) |
| Wooden patterns (various) | 1,000 – 15,000 / piece (most ₹2,000–6,000) | same page (Neptune ₹1,000; Lok Nath ₹1,100; R B ₹2,000; Delisha teak loose pattern ₹3,000; Maheshwari ₹10,000; Pragati ₹15,000) | VERIFIED (listings) |
| **3D-printed sand-casting pattern** (PLA/ABS/PETG, pan-India) | **5,000 / piece** | 3D Fly Printing and Filaments (Surat), https://m.indiamart.com/impcat/sand-casting-patterns.html | VERIFIED (listing) |
| Aluminium patterns (split/single piece/match) | 600 – 31,000 (typically ₹8,000–25,000) | same page | VERIFIED (listings) |
| Polymerate Labs (Hyderabad), FDM sand-casting patterns | no price. "48–72 hours if in Hyderabad or 3–5 days across India"; materials ASA/PETG/ABS/PA/PA6-GF/PLA+-CF; "can save up to 75 % in tooling costs"; pattern life: **PLA ≈ 10–50 impressions, ASA/ABS/PETG ≈ 100–500, CF/GF composite 500+** | https://polymerate.odoo.com/sand-casting-patterns | VERIFIED (page text; vendor claims) |
| Self-printed PLA pattern (JX1 Bambu P1S) | **≈ ₹100–200** material | ESTIMATED: a 150–250 g pattern plus core prints × Numakers PLA ≈ ₹0.67–0.71/g (repo `india_mechanical_manufacturing_raw.md`). Add draft (1–2°), shrink allowance (≈1.3 % for Al [UNVERIFIED rule of thumb]) and 2–3 mm machining stock on machined faces. A cup-shaped housing open at one end can often self-core in green sand. A closed or undercut bore needs a core box, which is a second print. | ESTIMATED |
| Other 3D-pattern leads | Cubein e-Manufacturing (CEMS); 3D Print Edge (Rajkot, "investment casting pattern printing"); Makenica blog on sand casting + 3D printing | search snippets; https://m.indiamart.com/3d-print-edge | UNVERIFIED |

### 1c. MOQ, tolerance, surface finish, porosity, heat treatment
| Topic | Finding | Source | Label |
|---|---|---|---|
| MOQ | None of the fetched listings states an MOQ for Al sand castings. In practice, jobbing foundries price per kg with a minimum batch or heat value. Expect a 1–5 piece job to be quoted as a lot charge. | listings above | NOT FOUND (MOQ) / practice UNVERIFIED |
| Dimensional tolerance | ISO 8062-3 defines DCTG/GCTG grades and machining-allowance grades (RMAG) for castings "as delivered". The table was **not** opened (paywalled). Hand-moulded green-sand aluminium is usually specified around DCTG 10–13, which in practice is **about ±0.5–1 mm on a 120 mm dimension**. | ISO 8062-3 abstract (https://webstore.ansi.org/preview-pages/ISO/preview_ISO+8062-3-2007.pdf); numbers are engineering rule of thumb | UNVERIFIED |
| Machining allowance | The usual practice is 2–3 mm per machined face on small Al sand castings and more on bores. This is why the as-cast weight is ≈ 1.5–2× the finished weight. | practice | UNVERIFIED |
| Surface roughness | Sand Ra 12.5–50 µm (Rz 100–400); investment Ra 1.6–6.3 µm; die casting Ra 0.8–3.2 µm. One HPDC listing states "Ra 6.3 µm". | search snippet citing shop.machinemfg.com (https://shop.machinemfg.com/die-casting-vs-investment-casting-vs-sand-casting-key-differences); Aarenza listing on https://m.indiamart.com/impcat/high-pressure-die-casting.html | UNVERIFIED (snippet) / listing VERIFIED |
| Porosity | Hydrogen is the only gas that dissolves significantly in molten Al. It comes out on solidification as gas porosity. Sources are damp charge, flux, tools, mould sand moisture and binder breakdown. Remedies are degassing or sparging, a dry charge and controlled pouring. Shrinkage porosity needs risers and chills. Machining a bearing seat can open sub-surface pores, which matters for sealed housings. Vacuum impregnation is the usual fix for leak paths (no India price found). | https://en.wikipedia.org/wiki/Hydrogen_gas_porosity ; https://en.wikipedia.org/wiki/Casting_defect | UNVERIFIED (encyclopedic) |
| LM25 composition | Cu ≤0.20, **Mg 0.20–0.60, Si 6.5–7.5**, Fe ≤0.50, Mn ≤0.30, Ti ≤0.20; as-cast **UTS 130 MPa min, elongation 2 % min**; cross-refs A357.0, AA601/AC601 | ICAST Alloys (Rajkot) datasheet PDF, https://www.icastllp.com/material_db_pdf/BS%201490%20LM25.pdf (rendered and read) | VERIFIED |
| LM25-TF (T6) treatment | Literature values: solution ≈ 520–538 °C for 1–8 h, quench, then age ≈ 155–175 °C for 3–12 h. One study reports +60–70 % UTS versus as-cast. | search snippets (czasopisma.pan.pl AFE 2016-0056; Amrita LM25 papers) | UNVERIFIED |
| A356.0-T6 sand cast (typical) | **UTS 234 MPa, YS 165 MPa, elongation 3.5 %** | EngineersEdge table (snippet), https://engineersedge.com/materials/mechanical_properties_of_aluminum_sand_castings_15194.htm | UNVERIFIED (snippet) |
| Heat-treat job work price (India) | No public ₹ price. Sigma Techno Cast lists "Heat Treatment" as a surface-treatment option. Maharsh Metal Heat Treatment (Ahmedabad) advertises aluminium heat-treatment services. | https://m.indiamart.com/impcat/heat-treating-services.html | NOT FOUND (price) |
| 6061 vs LM25-T6 for the paper | Machined 6061-T6 bar is ≈ 290+ MPa UTS with about 2–3× the elongation of cast A356-T6. A cast housing must be designed thicker or accept lower fatigue margin. | general knowledge | UNVERIFIED |

### 1d. Clusters
| Cluster | Specialisation / size | Source | Label |
|---|---|---|---|
| India overall | **15.16 Mt castings in 2023-24** (+7 %); ≈ 5,000 foundries (90 % MSME); grey iron ≈ 68 % of output | Institute of Indian Foundrymen, https://www.foundryinfo-india.org/profile_of_indian.aspx | VERIFIED |
| Coimbatore | pump-set castings; ≈ 600 units; about one tenth of national output (snippet) | foundryinfo-india (specialisation VERIFIED); unit count from search snippet (BEE/SIDBI) | VERIFIED / UNVERIFIED |
| Kolhapur, Belgaum | automotive castings; Kolhapur ≈ 250 units, Belgaum ≈ 100 units | foundryinfo-india; SIDBI cluster profile (snippet) https://development.sidbi.in/files/posts/Cluster-Profile-Report---Kolhapur-(Foundry)-Cluster.pdf | VERIFIED / UNVERIFIED |
| Rajkot | diesel-engine castings (IIF); **largest investment-casting cluster** (> 175 IC foundries, snippet) | foundryinfo-india; https://sidhiee.beeindia.gov.in/AboutUs/foundry (snippet) | VERIFIED / UNVERIFIED |
| Howrah | sanitary castings | foundryinfo-india | VERIFIED |
| Batala / Jalandhar / Ludhiana | machinery parts, agricultural implements | snippet (BEE) | UNVERIFIED |
| Pune, Ahmedabad, Faridabad, Chennai, Hyderabad, Indore, Agra | listed clusters. Pune has Castx Dies and Tools (GDC dies). Faridabad has Baruni Engineers (GDC ₹400/kg). | foundryinfo-india; IndiaMART GDC page | VERIFIED |
| Observed Al job-shop leads for JX1 | Coimbatore (Inticore, Ardent, Super Tech, N M Engineering GDC ₹310/kg), Surat (Sigma Techno Cast), Rajkot (Jupiter Moulding Works GDC ₹380/kg AlSi12; Powerbits ₹500/kg) | IndiaMART pages above | VERIFIED (listings) |

---

## 2. Investment casting (lost wax) and lost-PLA

### 2a. Investment castings, India (IndiaMART)
| Seller (city) | Material | ₹ | Unit | Notes | URL | Label |
|---|---|---|---|---|---|---|
| Metloy | **Aluminium** precision investment casting | **350** | kg | "industrial machinery", grey/silver | https://m.indiamart.com/impcat/precision-investment-casting.html | VERIFIED (listing) |
| Vartis Precision Castings | **Aluminium** lost-wax casting, 1–5 kg | 15,700 | **piece** | general engineering | https://m.indiamart.com/impcat/investment-castings.html | VERIFIED (listing) |
| MNC International | Carbon steel investment (vacuum), **0.1–0.5 kg** | 580 | kg | polished | precision-investment page | VERIFIED (listing) |
| RA Global Tech | IC, up to 0.1 kg, motorsport | 550 | kg | passivated | same | VERIFIED (listing) |
| Supercast Founders | SS investment, 0.2 kg | 650 | kg | railway | same | VERIFIED (listing) |
| Amsol Industries | SS investment, 0.5–1 kg | 400 | kg | valves/pumps | same | VERIFIED (listing) |
| Sulohak Cast (Rajkot) | MS investment | 450 | kg | polished/machined/shot blast | same | VERIFIED (listing) |
| Daichi Overseas; Vardhak; Sudarshan Technocast | IC (various) | 280 / 290 / 250 | kg | – | investment-castings page | VERIFIED (listings) |
| Icast Alloys LLP | IC, "actuator parts, bearing gear" | 975 | kg | – | same | VERIFIED (listing) |
| **Range, steel/SS IC** | ~20 listings | **≈ ₹250–650/kg** typical (outliers ₹110 and ₹8,800) | – | – | above | ESTIMATED from VERIFIED listings |

### 2b. Wax-injection die cost, India
| Seller (city) | Die | ₹ | Label |
|---|---|---|---|
| Neptune Engineering (Ahmedabad) | aluminium lost-wax die | 5,000 | VERIFIED (listing) |
| G M Industries (New Delhi) | SS IC die | 6,000 | VERIFIED (listing) |
| Horizon Metal Components (Rajkot) | aluminium die, shell mould, alloy steel castings | 10,000 | VERIFIED (listing) |
| Khodiyar Enterprise / Metloy (Ahmedabad) | Al / MS dies | 20,000 | VERIFIED (listing) |
| Shree Balvi Engineering (Ahmedabad) | Al multi-cavity, max casting 4 kg | 30,000 | VERIFIED (listing) |
| Shree Balvi Industries / Friends Techno (Rajkot) | Al single-cavity, SS casting; 12–14 in die | 45,000 | VERIFIED (listing) |
| (unnamed) Aluminium IC die | – | 1,00,000 | VERIFIED (listing) |
| **Estimate for a JX1 part** | small steel part (carrier, bracket): **₹10,000–45,000** single-cavity Al die. A 120 mm housing die is at the upper end or above. | ESTIMATED from listings |
| Source page | https://m.indiamart.com/impcat/investment-casting-die.html | – |
| Global reference | IC tooling "$2,000 up to and exceeding $20,000"; Al wax dies are common because they cut cycle time and are cheap to machine | Casting Source (snippet), https://www.castingsource.com/node/1522 | UNVERIFIED |
| MOQ | None stated. 3D-printed wax or PLA patterns replace the die below about 50–100 pcs (practice). | – | NOT FOUND / UNVERIFIED |

### 2c. Lost-PLA practice
| Topic | Finding | Source | Label |
|---|---|---|---|
| Investment | "standard jewelry investment, Plasticast, or Ultravest (for high expansion)". Do **not** use plain plaster of Paris; use a real investment such as SRS. Hobby fallback is plaster + silica sand layers. | Siraya Tech guide https://siraya.tech/blogs/news/lost-pla-casting ; HMEM forum (snippet) https://homemodelenginemachinist.com/threads/lost-pla-processes-products-knowledge.30767/ | VERIFIED (Siraya) / UNVERIFIED (forum) |
| Burnout schedule (gypsum investment) | Siraya: ramp slowly, ≈150 °C (wax/moisture) then **400–700 °C** to burn out PLA, over a **5–12 h** cycle. Generic jeweller schedule: ≈150–175 °C (free water) → 315–370 °C → **peak ≈ 730 °C hold** → cool to casting temperature. Total 6–12 h depending on flask size. | Siraya (VERIFIED); skyjems.ca encyclopedia (snippet) https://skyjems.ca/pages/encyclopedia-flask-burnout | VERIFIED / UNVERIFIED |
| Forum warning | Forum users report moulds "blew up" at ≈1,150 °F (620 °C) and needed ≈1,300 °F (705 °C) for clean PLA burnout | HMEM snippet | UNVERIFIED |
| PLA vs wax | PLA "expands slightly; can leave carbon ash residue" that pits the surface. Castable wax/resin "melts cleanly with zero ash". PLA layer lines copy into the casting. Hollow prints let investment in. Trapped bubbles make metal nodules. **Wet floors and moulds cause molten-metal explosions.** | Siraya | VERIFIED |
| Gypsum vs phosphate binder | Gypsum-bonded investment is chemically unstable above ≈650 °C. It suits Au/Ag/brass and aluminium, **not steel**. Steel and Pt need phosphate-bonded investment or ceramic shell. | dental investment lecture notes (snippet), e.g. https://codental.uobaghdad.edu.iq/wp-content/uploads/sites/14/2021/03/Investment-Materials.pdf | UNVERIFIED |
| Aluminium pour | Pour at ≈700–750 °C into a flask held at ≈150–400 °C. One forum suggests ≤150 °C flask for Al. | general practice; HMEM snippet | UNVERIFIED |
| Flask size for this housing | Ø120 × 70 mm needs an ≈ Ø150–175 mm × 150 mm flask. Jewellery kilns of 9"–12" cube fit one or two flasks. | ESTIMATED (geometry) | ESTIMATED |
| Investment per flask | Ø160 × 150 mm flask ≈ 3.0 L minus a ≈0.15 L pattern ≈ 2.8 L slurry. At ≈1.0–1.1 kg powder per L of slurry that is **≈ 2.8–3.1 kg powder → ₹190–590** at ₹66–190/kg | ESTIMATED | ESTIMATED |

### 2d. Hobby / small-shop equipment and consumables, India (IndiaMART)
| Item | Seller (city) | ₹ | Specs | URL | Label |
|---|---|---|---|---|---|
| Burnout furnace | Shapet Induction | **35,000** | < 5 L, 900 °C, programmable 9-step | https://m.indiamart.com/impcat/burnout-furnace.html | VERIFIED (listing) |
| Burnout furnace | Smitech | 30,000 | 9"×9"×9", IR coil, single phase | same | VERIFIED |
| Burnout furnace | Ultimma Cast Machinery | 48,000 | 12"×12"×12", 6 kW, SS | same | VERIFIED |
| Burnout furnace w/ digital timer | (TrustSEAL listing) | 24,501 | jewellery | same | VERIFIED |
| Burnout furnace | Tiwari Enterprises | 85,000 | 30–60 L, 1000 °C, 3-phase | same | VERIFIED |
| Burnout furnace | Amar Induction (Gondal) | 55,000 | 15 L, 900 °C | search snippet of https://m.indiamart.com/amar-induction | UNVERIFIED (snippet) |
| Burnout furnace | A7 Smart Tech (Jaipur) | 1,20,000–1,75,000 | jewellery production | snippet of https://m.indiamart.com/a7-smart-tech/burnout-furnace.html | UNVERIFIED |
| Electric crucible melting furnace | N D Tools | **18,000** | **5 kg, 1200 °C, crucible** | https://m.indiamart.com/impcat/electric-melting-furnace.html | VERIFIED (listing) |
| Electric melting furnace | Srinathji Jewellery Machinery | 12,991 | 3 kg, 1200 °C | same | VERIFIED (listing; specs inconsistent) |
| Electric melting furnace | Jay Gopal Industries | 19,500 | 1,400 W | same | VERIFIED |
| Electric melting furnace | Smitech | 32,000 | 5 kg Cu/brass, transformer type | same | VERIFIED |
| Al melting furnace, 50 kg | City Hydrothermal | 2,49,950 | 10 kW resistance | https://m.indiamart.com/impcat/aluminium-melting-furnace.html | VERIFIED |
| Vacuum casting machine (jewellery) | Amar Induction | 75,000 | 5 mbar | https://m.indiamart.com/amar-induction/ | VERIFIED |
| Investment powder (gypsum) | various | **₹2,650–3,950 per 20–22.5 kg bag** (≈ ₹118–175/kg) | Prestige SIGMA ₹2,849; **Prestige OPTIMA (for resin/plastic patterns) ₹3,200**; Maximus ₹2,750/20 kg | https://m.indiamart.com/impcat/investment-powder.html | VERIFIED (listings) |
| Investment powder (phosphate-bonded) | Shinetech | ₹1,490 / 22.5 kg bag | phosphate bonded | same | VERIFIED (listing) |
| Global ref, SRS Stonecast | EU retailer | ≈ €78.54 / 22.7 kg ex-VAT | – | snippet, eshop.advantage-fl.cz | UNVERIFIED |

---

## 3. Gravity die casting (GDC) and high-pressure die casting (HPDC)

### 3a. India, per-kg / per-piece
| Seller (city) | Process / alloy | ₹ | Unit | Specs | URL | Label |
|---|---|---|---|---|---|---|
| N M Engineering Works (Coimbatore) | GDC Al | 310 | kg | textile/auto/agri | https://m.indiamart.com/impcat/gravity-die-casting.html | VERIFIED |
| Sigma Techno Cast (Surat) | GDC Al, with machining | 310 / 355 / 360 | kg | up to 50 kg | same; seller page | VERIFIED |
| Jupiter Moulding Works (Rajkot) | GDC AlSi12, 0.5–1 kg | 380 | kg | – | same | VERIFIED |
| Gajanand Aluminium | GDC LM6/LM25/LM9 | 380/390/400 | kg | – | same | VERIFIED |
| Baruni Engineers (Faridabad) | GDC Al auto parts | 400 | kg | – | same | VERIFIED |
| Super Tech Industries (Coimbatore) | GDC Al | 400 | kg | up to 80 kg | https://m.indiamart.com/super-tech-inds/gravity-die-casting.html | VERIFIED |
| Ace Moulds / AGM Diecasting | GDC AlSi10Mg, ≤ 0.5 kg | 450 / 550 | kg | – | GDC page | VERIFIED |
| (listing) | GDC **LM6, 0.5–1 kg** | 600 | kg | – | GDC page | VERIFIED |
| **GDC range** | 10 listings | **₹310–600/kg** | – | – | – | ESTIMATED |
| Supercast Founders | HPDC Al, 50 g–3.5 kg, 150–300 T | 450 | kg | – | https://m.indiamart.com/impcat/high-pressure-die-casting.html | VERIFIED |
| Horizon Metal Components | HPDC Al | 320 (/kg) and 300 (/piece) | – | – | same | VERIFIED |
| Shubh Castings | HPDC Al, ≤150 T, 2 kg | 200 | kg | – | same | VERIFIED |
| Aarenza Die Cast | HPDC Al, 2.5 mm wall, "Ra 6.3 µm" | 250 | kg | – | same | VERIFIED |
| Meta Lab Engineers | HPDC | 450 | kg | – | same | VERIFIED |
| MNC International | HPDC Al 2–5 kg, 150–300 T | 1,000 | kg | – | same | VERIFIED |
| C K Industries / Metloy | HPDC Al | 85 / 100 | kg | – | same | VERIFIED (implausibly low, probably metal-only or a typo) |
| **HPDC range (credible)** | – | **₹200–450/kg** | – | – | – | ESTIMATED |

### 3b. Die/tool cost, India (IndiaMART listings)
| Seller | Die type | ₹ | Notes | URL | Label |
|---|---|---|---|---|---|
| Shree Balvi Industries | GDC die, alloy steel, 10 kg casting | 45,000 | – | https://m.indiamart.com/impcat/die-casting-mould.html | VERIFIED |
| Fenetex (Coimbatore) | GDC dies ("engine pistons") | 45,000 | – | GDC page | VERIFIED |
| Honest Metal Cast (Ahmedabad) | GDC die | 50,000 | – | GDC page | VERIFIED |
| Castx Dies and Tools (Pune) | GDC die, **AlSi7Mg** | **2,01,000** | – | GDC page | VERIFIED |
| Satadhar Tec Mec | Al multi-cavity mould | 2,00,000 | – | die-casting-mould page | VERIFIED |
| Parshuram Technocrafts | HPDC mould, H13, 50 T | 11,500 | (too low for a real die; probably an insert or placeholder) | same | VERIFIED (doubtful) |
| Graphikos Technology | HPDC mould H13, 500–800 T | 20,001 | placeholder-like | same | VERIFIED (doubtful) |
| Aarenza Die Cast | Al PDC mould | 60,000 | – | same | VERIFIED |
| **Nunes Instrumentation** | **Al HPDC mould, "up to 100,000 shots"** | **1,82,000** | – | HPDC page | VERIFIED |
| Evocative Industries | Al PDC die | 2,00,000 | – | die-casting-mould page | VERIFIED |
| Auto Die Cast (India) | Al die | 4,00,000 / 5,00,000 | – | HPDC / mould page | VERIFIED |
| Aarenza Tool Room | 250 T die-casting mould | 6,00,000 | – | mould page | VERIFIED |
| **Estimate, JX1 housing** | GDC die (steel, 2-part + metal/sand core) **₹0.5–2 lakh**; HPDC single-cavity H13 die with 1–2 slides, 150–250 T **₹2–6 lakh** | – | ESTIMATED from the listings above (excluding the sub-₹25k outliers) |

### 3c. Per-part at 1k / 10k (ESTIMATED)
Assumptions:
- HPDC as-cast mass 0.35–0.55 kg (0.5–1 mm machining stock).
- GDC as-cast mass 0.45–0.7 kg.
- Prices from 3a. Die costs from 3b. No die maintenance or re-polish.

| Route | Metal + casting | Die amortisation @1k | @10k | Casting cost @1k | @10k |
|---|---|---|---|---|---|
| GDC (₹310–600/kg; die ₹0.5–2 lakh) | ₹140–420 | ₹50–200 | ₹5–20 | **₹190–620** | **₹145–440** |
| HPDC (₹200–450/kg; die ₹2–6 lakh) | ₹70–250 | ₹200–600 | ₹20–60 | **₹270–850** | **₹90–310** |
| Sand (no die; pattern ₹0.1–15k) | ₹150–380 | ≤ ₹15 | ≈ 0 | ₹150–395 | ₹150–380 |

Takeaway: below about 1k pcs, sand casting is as cheap as or cheaper than GDC or HPDC per part, and needs no die. HPDC pays off near 5–10k. That matches the global break-even "5,000–10,000 units" in the Alibaba seller blog (UNVERIFIED).

### 3d. Tolerance and metallurgy
| Topic | Finding | Source | Label |
|---|---|---|---|
| NADCA precision tolerance (Al) | ±0.002 in for the first inch + ±0.001 in per additional inch. On 120 mm that is ±0.05 + 3.7 × 0.025 ≈ **±0.14 mm** (same die half, not across the parting line). | snippet of teamrapidtooling.com https://www.teamrapidtooling.com/blog/die-casting-tolerance-standards/ ; math ESTIMATED | UNVERIFIED / ESTIMATED |
| Xometry die casting | typical **±0.076–0.127 mm** for Al; rapid tooling in about 12 business days, production tooling about 20 days; samples **12–18 weeks** after order; "ideal for production starting from 100 parts" | Xometry die-casting pages (snippet) https://xometry.eu/en/die-casting/ | UNVERIFIED |
| ±0.01 mm bearing seat | Out of reach for any as-cast route, so it needs machining (or a pressed-in steel bearing sleeve) | follows from the above | ESTIMATED |
| HPDC + T6 | Entrapped gas expands during solution treatment (≈ 510–540 °C) and causes **blistering and dimensional change**. ADC12 pores grew after > 5 min at 490 °C, 3 min at 500 °C, 1 min at 510 °C. Workarounds are vacuum HPDC or short, low-temperature solution treatment. Use HPDC parts as-cast (F) or T5. | search snippets (Springer chapter; JFES; polito.it) | UNVERIFIED |
| HPDC alloys | ADC12/A380/LM24 (high Si+Cu): good fluidity, lower ductility and corrosion resistance than LM25/A356. Not anodise-friendly (grey or blotchy). | general knowledge | UNVERIFIED |

### 3e. China comparison
| Item | Value | Source | Label |
|---|---|---|---|
| Die-cast parts, Made-in-China listings | Motorcycle **motor housing US$1.55–2.95/pc (MOQ 100)**; audio shells $6.85–8.85 (MOQ 100); auto parts $1–3 (MOQ 500); ADC12 parts $0.89–1.36 (MOQ 1,000) ≈ **₹150–850** | https://www.made-in-china.com/products-search/hot-china-products/Aluminum_Die_Casting_Price.html | VERIFIED (listing) |
| Die, China | Foshan Symbos "Aluminum die casting die, automotive" **US$12,000/set** (≈ ₹11.6 lakh [E]) | same page | VERIFIED (listing) |
| Die, China (blog) | simple cavity $15–20k; slides or tight tolerance $25–60k+. Per-part $25–35 at 1k and $8–15 at 10k (+ tooling) for an enclosure. | Alibaba seller blog 2026 https://seller.alibaba.com/blogs/2026/southeast-asia/industrial-machinery/cnc-machining-vs-die-casting-sourcing-guide-alibaba-b2b | UNVERIFIED (marketing blog) |
| ADC12 ingot, China | ≈ US$2,961–3,137/t | SMM (metal.com) snippet | UNVERIFIED |
| RobStride | "all housing and support parts are one-piece aluminium die castings" | repo `china_actuator_manufacturing_economics_raw.md` (36Kr) | UNVERIFIED |
| Reading | Chinese per-part HPDC prices are similar to the India ESTIMATE at ≥ 1k pcs. Listed Chinese dies are **not** cheaper than Indian die listings. Indian listings look under-priced, so confirm with a real RFQ. | – | ESTIMATED |

---

## 4. Vacuum/urethane casting with silicone moulds; low-melt metals in silicone

### 4a. India, vacuum casting services (IndiaMART listings)
| Seller | ₹ | Unit | Notes | Label |
|---|---|---|---|---|
| Instrumus Technologies | 90 | piece | "within ±0.1 mm", "7–10 days for small batches" | VERIFIED (listing) |
| Aarya Precision (Pune) | 100 | piece | PC-ABS/ABS/silicone, batch | VERIFIED |
| Nirmala Manufacturing Systems | 500 | piece | PU, 2–5 kg parts | VERIFIED |
| Exxjet Systems | 5,000 | piece | plastic vacuum casting | VERIFIED |
| Innovixpro | 1,000 | kg | ABS/PP/PC/rubber/UL V-0/nylon-like | VERIFIED |
| Avinya Design | 2,000 | kg | PU, 100–500 g | VERIFIED |
| High On 3D | 2,500 | kg | – | VERIFIED |
| Make By Layer | 4,000 | kg | PU, 100–500 g | VERIFIED |
| 3D Manufacturing Solutions (Chinchwad) | 5,000 | kg | PP/ABS/rubber/PC-ABS/nylon-like | https://m.indiamart.com/3dprototype/rapid-prototyping-services.html, VERIFIED |
| Makenica (FAQ anchor) | 4,000 | part | "urethane casting ₹4,000 per part" | repo `india_mechanical_manufacturing_raw.md`, VERIFIED 2026-09-24 |
| Source | https://m.indiamart.com/impcat/vacuum-castings.html | – | – | – |

### 4b. Mould cost, mould life, materials
| Topic | Finding | Source | Label |
|---|---|---|---|
| RTV-2 silicone, India | **Fortius RTV-2 1:1 ₹3,180/kg** (1+1, 5+5 kg). Tin-cure RTV-2 ₹700–890/kg (Fortisil 15C ₹750; TLSC-215B ₹700–890, MOQ 50 kg). Platinum TLS-130 ₹850/kg. Zhermack ZA 35-15 ₹2,440/kg. | https://m.indiamart.com/impcat/rtv-silicone.html (Fortius VERIFIED); others from snippet of https://m.indiamart.com/impcat/liquid-silicone-rubber.html | VERIFIED / UNVERIFIED |
| Silicone needed for a 120 × 70 mm part | Mould box ≈ 160 × 160 × 110 mm ≈ 2.8 L, minus ≈ 0.8 L part envelope ≈ 2.0 L × 1.1–1.2 kg/L ≈ **2.2–2.4 kg → ₹1,600–7,600** in material | ESTIMATED | ESTIMATED |
| Vendor mould price (global) | $200–500 for small parts; $1,200–3,000 for large/complex. Life ≈ 10–30 parts. Per part $10–100. | hlhrapid / rjcmold blogs (snippet) https://hlhrapid.com/blog/urethane-casting-cost/ | UNVERIFIED |
| Shots per mould | Materialise: "up to 25 copies per mold". Xometry: up to about 20 units per mould. Typical 20–25, up to 50. | snippets of https://reseller.materialise.com/it/node/4644 , Xometry, Fathom, TriMech | UNVERIFIED (consistent across 4 sources) |
| Tolerance | "ISO 2768 coarse … up to ±0.1 mm" | snippet (proleantech) | UNVERIFIED |

### 4c. Silicone temperature limits, and which metals can go in silicone
| Item | Value | Source | Label |
|---|---|---|---|
| Smooth-On **Mold Max 60** (tin-cure, Shore 60A) | heat resistance **up to 560 °F / 294 °C**; for "casting low-melt metal alloys such as tin and pewter" | https://www.smooth-on.com/products/mold-max-60/ (snippet + Smooth-On news page) | UNVERIFIED (snippet of maker page) |
| Creartec Silcotin HB-RTV | up to **300 °C**; tin, zamak, pewter, lead; **100–150 castings** | snippet of https://www.pacoartcenter.gr/en/creartec-silcotin-hb-rtv-heat-resistant-silicone-mold-rubber.html | UNVERIFIED |
| HB/HE blend (flume.de) | short-term up to **380 °C** (lead, pewter, zamak) | snippet | UNVERIFIED |
| Wacker Elastosil M 4370 A/B | intended for low-melting metal alloys; "very good heat resistance" | Wacker TDS (snippet) | UNVERIFIED |
| **Field's metal** | Bi 32.5 / In 51 / Sn 16.5 %, melts **≈ 62 °C**. Fine in any silicone, even PLA or resin moulds. Indium is costly. | https://en.wikipedia.org/wiki/Field%27s_metal (snippet) | UNVERIFIED (encyclopedic) |
| **Pewter** (lead-free Sn-Sb-Cu) | melts **≈ 170–230 °C**. Suits high-temp RTV. | https://en.wikipedia.org/wiki/Pewter (snippet) | UNVERIFIED |
| **Zamak 3** (Zn-Al4) | melting range **379–390 °C**. That is at or above every silicone rating found (294–380 °C short-term), and real pour temperature is higher still. **Marginal**: short mould life, degassing and porosity. Graphite, steel or "kirksite" moulds are the norm. | https://en.wikipedia.org/wiki/Zamak (snippet) | UNVERIFIED |
| **Aluminium** | melts **660 °C** (pure); LM25 is liquid around 615 °C and is poured at ≈ 700–750 °C. That is **≈ 2–2.5× the ≈ 300 °C limit** of the best mould silicones. The rubber decomposes and outgasses, which ruins the mould and fills the casting with gas porosity. **Aluminium needs refractory moulds** (sand, investment/plaster, ceramic shell or steel dies). | melting point: standard data; silicone limits above | ESTIMATED (comparison) |
| Engineering use for JX1 | Silicone + PU (vacuum casting) gives **plastic replicas** (covers, cable guides, fit-check housings), 20–25 per mould. Low-melt metal parts are decorative or ballast only. Pewter/zinc lack the stiffness and creep resistance for a bearing housing. | – | ESTIMATED |

---

## 5. Plastic injection moulding and metal injection moulding (MIM)

### 5a. Injection-mould tooling
| Item | Value | Source | Label |
|---|---|---|---|
| India vs China tooling ranges (Zetwerk) | Simple 2-plate: **China $2,500–6,000, India $3,500–8,000**. Medium (4-plate, slides): China $8–20k, India $10–25k. Complex (hot runner, multiple slides): China $20–60k, India $28–80k. 8-cavity: China $12–30k, India $15–38k. "India's tooling cost premium over China is 20–35 %". Undercut side-actions "$500–5,000 per action". | https://www.zetwerk.com/blog/injection-moulding-in-india-complete-guide-to-plastic-part-manufacturing-and-sourcing/ (WebFetch; article undated) | VERIFIED (page text; vendor content) |
| In ₹ | Simple India tool ₹3.4–7.7 lakh; medium ₹9.6–24 lakh | ESTIMATED at ₹96.38/$ | ESTIMATED |
| Protolabs aluminium tooling | "Molds begin around $1,500" (≈ ₹1.45 lakh), "seven days or less". Al "capable of molding … about 10,000 parts as a rule of thumb". Prototype tooling "guaranteed for at least 2,000 shots". Tolerance "±0.003 in. plus resin tolerance". Steel high-volume tooling "over $50,000". | https://www.protolabs.com/resources/blog/aluminum-mold-tooling-for-injection-molding/ ; https://www.protolabs.com/services/injection-molding/prototyping/ | VERIFIED |
| IndiaMART mould listings | **P20 single-cavity ₹2,00,000** (Trident Technologies); P20 hot-runner multi-cavity ₹1,00,000 (Plastolin); P20 medical 4–16 cavity ₹2,50,000 (Maruti Industries); generic steel moulds ₹40,000–1,30,000; "H13" ₹10,000 (a calculator part, so small); Al multi-cavity hot-runner eye-drop cap ₹19,99,999 | https://m.indiamart.com/impcat/injection-moulds.html | VERIFIED (listings) |
| Al vs P20 cost | Al is faster to machine but costs more per kg, so "the final tool price comes out roughly the same" (HLH). One study found A7075 mould ≈ **23.6 % cheaper** than P20. | snippets (hlhrapid; RMUTP repository) | UNVERIFIED |
| **Estimate for a ≈120 mm housing-like part** (single cavity, 1–2 slides) | **Al prototype tool ₹1.5–4 lakh; P20 ₹3–8 lakh; hardened H13 ₹6–15 lakh** | ESTIMATED from Zetwerk ranges + IndiaMART P20 listings + Protolabs floor | ESTIMATED |
| MOQ | Moulders typically want ≥ 1,000 pcs per run (setup and purge). No listing states an MOQ. | – | NOT FOUND / UNVERIFIED |

### 5b. Per-part cost, PA66-GF30 / PPS (ESTIMATED)
| Input | Value | Source | Label |
|---|---|---|---|
| PA66-GF30 granules | ₹200–400/kg (PA66 30 % GF ₹200; PA66 33 % GF FR V0 ₹400) | snippets of https://m.indiamart.com/impcat/nylon-66-granule.html / polyamide-granules | UNVERIFIED |
| PPS GF40 granules | **₹500–750/kg** (Fortron 40 % GF ₹500; Xytron G4024T 40 % GF ₹680; PPS ₹700–750) | https://m.indiamart.com/impcat/pps-granules.html | VERIFIED (listings) |
| Part mass | The Al housing (≈ 350 g ÷ 2.70 g/cc ≈ 130 cm³) re-designed in plastic with thicker walls ≈ 130–180 cm³. PA66-GF30 (1.36 g/cc) ≈ 180–245 g. PPS-GF40 (1.65 g/cc) ≈ 215–300 g. | ESTIMATED | ESTIMATED |
| Material cost/part | PA66-GF30 **₹35–100**; PPS-GF40 **₹105–225** (+ 5–10 % runner/scrap) | ESTIMATED | ESTIMATED |
| Machine time | 45–90 s cycle on a 150–250 T press at an assumed ₹800–1,500/h → ₹10–40/part | ESTIMATED (hour rate is an assumption; no India source fetched) | ESTIMATED |
| Total per part (ex-tool) | **≈ ₹50–150 (PA66-GF30), ₹120–280 (PPS-GF40)**. Add tool ÷ volume (₹3–8 lakh ÷ 1k = ₹300–800; ÷ 10k = ₹30–80). | ESTIMATED | ESTIMATED |
| Engineering caveat | A plastic housing **cannot hold ±0.01 mm bearing seats** over temperature, creep and moisture (PA66 absorbs water). Use moulded-in or pressed metal bearing sleeves, or keep plastic for covers. | general | UNVERIFIED |

### 5c. Metal injection moulding (MIM)
| Item | Value | Source | Label |
|---|---|---|---|
| Indo-MIM (Bengaluru; Hoskote + Doddaballapur plants) | "Product weight is limited to a maximum weight of about **240 grams** (although economics generally push the weight limit to **no more than 50 grams**)". Tolerances are "highly dependent upon product geometry". Tighter tolerances need post-machining. Low volumes are "uneconomical due to the fact that the customers have to invest on a tool". | https://www.indo-mim.com/metal-injection-molding-faq-materials-problems-process/ (curl, page text) | VERIFIED |
| IndiaMART MIM listings | MIM parts **₹20/unit** (Goldiva, SS/low-alloy/tool steel); ₹75/pc (Precision Sintered); ₹150/pc (Horizon, < 1 g). MIM moulds **₹2,30,000** (New Brahmmani: SS304, 50,000 shots, "0–0.02 mm"), **₹2,75,000** (Shri Vinayak, tool steel, 1–5 g parts). | https://m.indiamart.com/impcat/metal-injection-molding.html | VERIFIED (listings) |
| Global tooling and volume | MIM moulds **$10,000–100,000+** with 200k–1M+ shot life (≈ ₹9.6–96 lakh); "ideal for … exceeding 5,000 units annually"; parts "four-to-five times less expensive than Swiss CNC" in a MIMA case | DFMA / metalsupermarkets / MIMA snippets | UNVERIFIED |
| Other Indian MIM makers (leads) | Goldiva Technology (Rajkot), Precision Sintered Products (Rajkot), Horizon Metal Components (Rajkot) | IndiaMART MIM page | VERIFIED (listings) |
| Suitability for JX1 planets/sun | Planets of m0.8–1, Ø20–35 mm, 8–40 g in 4605/4140-type or 17-4PH are inside MIM's sweet spot (≤ 50 g). Tooling only pays off at ≳ 5k pcs per year per part number. Tooth accuracy needs sizing, shaving or grinding for quiet, low-backlash gears. **Not** suitable for the 120 mm housing (too heavy). | ESTIMATED from Indo-MIM limits | ESTIMATED |

---

## 6. Powder-metallurgy (press + sinter) gears, India

| Item | Value | Source | Label |
|---|---|---|---|
| Market | **GKN Sinter Metals India**: > 45 % of Indian PM market (Pune, Ahmedabad plants; ex-Mahindra Sintered Products). **Sundram Fasteners**: sintered products incl. gears/rotors. | snippets (azom.com GKN buy-out; globalfastener; wrightresearch) | UNVERIFIED |
| Sintered gear listings | Oilite Industries ₹11.50/pc (iron); Swadeshi Engg (Faridabad) **Fe-Cu-C, 6.9–7.1 g/cc, m0.2–0.7, 10–40 teeth, ₹100/pc**; Goldiva (Rajkot) **Fe-Ni spur, 7.1–7.3 g/cc, m0.5–1, ₹19/pc**; Precision Sintered (Rajkot) Fe-Cu-C 6.6–6.9 g/cc m1–2 ₹60/pc; Avadh Metals Cu-infiltrated steel 6.9 g/cc m3 ₹100/pc; Goa Sintered Products F-0208/FC-0204 (steam treat optional; "secondary machining/grinding out to maintain close tolerance") ₹5/pc; Swastika (Noida) ₹5/pc; Suraj Components (Ludhiana) ₹20/pc | https://m.indiamart.com/impcat/sintered-gear.html | VERIFIED (listings) |
| Tooling cost (India) | No public ₹ figure for compaction tooling | – | NOT FOUND |
| Break-even | Spur gears: "10,000 gears were enough to … repay PM tooling in one year or less"; helical ≈ 30,000 | Gear Solutions, Anders Flodin "Powder Metal Gears, Part VIII" (snippet) https://gearsolutions.com/departments/materials-matter-anders-flodin-8/ | UNVERIFIED |
| Density | 7.0 g/cc ≈ 89–90 % of wrought steel (7.87 g/cc); listings show 6.6–7.3 g/cc | math; listings | ESTIMATED |
| Strength | MPIF FLN2-4405-160HT (Q&T): **UTS ≈ 1,100 MPa** at 6.9–7.1 g/cc | Total Materia snippet https://www.totalmateria.com/en-us/material/1625211 | UNVERIFIED |
| Fatigue vs wrought | PM rolling-contact fatigue "typically … inferior to that of wrought steel". Surface densification (rolling) or high core density (7.4–7.6 g/cc) closes most of the gap and can "replace gears made of typical wrought Cr-Mo steel". | Kobelco / Höganäs / patent snippets | UNVERIFIED |
| Use in robots | RobStride's **EduLite** (budget) series uses powder metallurgy and plastics. The flagship uses alloy steel. | repo `china_actuator_manufacturing_economics_raw.md` (36Kr 2025-09-10) | UNVERIFIED |
| Suitability for JX1 planetary | Good for **low-cost planets/sun in the 2nd stage or for light joints** at ≥ 10k pcs. Below that, hobbed/turned steel or bought-in gears are cheaper (no tooling). Ask for sinter-hardened or Q&T grade ≥ 7.0 g/cc and sizing for AGMA/ISO accuracy. | ESTIMATED | ESTIMATED |

---

## 7. Safety facts for DIY metal casting

| Hazard | Fact / control | Source | Label |
|---|---|---|---|
| Steam explosion | Water touching molten metal flashes to steam at **≈ 1,600–1,700× its volume**, a violent explosion. Pouring into a **damp or wet mould** causes it. | Foundry Management & Technology https://www.foundrymag.com/melt-pour/article/21927633/molten-metal-splash-and-furnace-refractory-safety (snippet); HMEM thread | UNVERIFIED (snippet, consistent) |
| Projection distance | Steam pockets have thrown molten aluminium "up to 30 feet in all directions" | ISRI "Molten Aluminum Safety" https://www.recycledmaterials.org/scrap-article/molten-aluminum-safety/ (snippet) | UNVERIFIED |
| Chemical reaction | At high temperature Al + H₂O → Al₂O₃ + H₂. The hydrogen is far above its auto-ignition temperature (751 °F), so an explosion is likely. | ISRI (snippet) | UNVERIFIED |
| Moisture sources | Wet scrap (cans, closed tubes), condensation on cold ingots, uncured or unburnt investment, green sand too wet, cold or damp tools and crucibles, **concrete floors** (spalling). **Preheat moulds, tools, skimmers and charge.** Pour over a dry sand bed. | ISRI; FMT; Siraya ("damp floors cause molten metal explosions") | VERIFIED (Siraya) / UNVERIFIED |
| Hydrogen porosity | The same moisture also causes gas porosity (quality issue) | Wikipedia "Hydrogen gas porosity" | UNVERIFIED |
| PPE | Face shield over safety glasses; aluminised or leather jacket, apron, gloves, **leggings/spats**, leather boots. Aluminised glass fabric deflects ≈ 90 % of radiant heat. No synthetics (they melt onto skin). | OSHA-derived guidance: Oregon OSHA PD-113 https://osha.oregon.gov/OSHARules/pd/pd-113.pdf ; MN DLI CPL 2-1.20 https://www.dli.mn.gov/sites/default/files/pdf/CPL_2-1.20_foundry_PPE.pdf (snippets) | UNVERIFIED (snippets of official docs) |
| Burnout fumes | Burning out PLA or resin gives smoke/VOCs. Run the kiln outdoors or under extraction. | general | UNVERIFIED |
| Silica dust | Investment powders contain crystalline silica (cristobalite/quartz). Mix with a P2/N95+ respirator and wet clean-up. | general | UNVERIFIED |
| Thermal shock | Ramp burnout slowly: fast heating cracks the investment (fins, run-outs) and can spall it | Siraya; skyjems (snippet) | VERIFIED / UNVERIFIED |

---

## 8. Finish-machining a casting vs machining from billet

### 8a. Inputs
| Input | Value | Source | Label |
|---|---|---|---|
| 6061/6082 round bar | ₹230–300/kg (mill lengths; cut pieces cost more) | repo `india_mechanical_manufacturing_raw.md` (IndiaMART, 2026-09-24) | UNVERIFIED → ESTIMATED range |
| VMC job-work rate (Rajkot) | **₹400/hour**, 3-axis, "up to 10 microns", Al/SS/MS | Mahek Engineering https://m.indiamart.com/mahekengineeringrajkot/vmc-job-work.html | VERIFIED (listing) |
| Export-shop rates (India) | 3-axis $20–38/h (≈ ₹1,900–3,600/h); turning $18–32/h | Robocon CNC blog (repo file, 2026-09-24) | VERIFIED (blog) / ESTIMATED ₹ |
| Buy-to-fly ratios (aero reference) | machining from forged block 30:1; from sections 12:1; die forging 8:1; **form casting 1.4:1; pressure die casting 1.2:1** | NATO STO MP-AVT-139-17 (snippet) https://www.sto.nato.int/publications/STO%20Meeting%20Proceedings/RTO-MP-AVT-139/MP-AVT-139-17.pdf | UNVERIFIED |
| Case study | Pump housing: CNC from billet $12,700 vs 3D-printed-sand casting $4,500 (−64 %) | Alibaba seller blog (snippet) | UNVERIFIED (marketing) |

### 8b. JX1 housing, billet vs sand casting (ESTIMATED; per part, batch of about 20–50)
Assumptions:
- Finished part 350 g.
- Billet Ø125 × 75 mm 6061: volume 0.920 L, mass **2.49 kg**, buy-to-fly ≈ **7:1**. Material to remove ≈ 2.14 kg ≈ 790 cm³.
- Sand casting 0.6–0.9 kg as-cast. Material to remove ≈ 0.25–0.55 kg ≈ 95–205 cm³.
- Practical job-shop roughing MRR in Al ≈ 30–80 cm³/min.
- Finishing (bearing seats ±0.01, faces, bolt circle, threads) ≈ 15–30 min on both routes.
- Two setups ≈ 10–20 min on both routes. A casting needs soft-jaw or fixture datums. Fixture ≈ ₹5–15k one-off (assumption).

| | Billet route | Sand-cast route |
|---|---|---|
| Metal / casting | ₹570–750 (2.49 kg × ₹230–300) | ₹150–380 (casting) + pattern amortisation (≈ ₹0–300) + heat treat (NOT FOUND, assume ₹50–150) |
| Roughing time | 10–26 min | 1–7 min |
| Finish + setups | 25–50 min | 25–50 min (+ inspection for porosity) |
| **Total machine time** | **≈ 35–76 min** | **≈ 26–57 min** |
| Machining @ ₹400/h | ₹230–510 | ₹175–380 |
| Machining @ ₹1,900–3,600/h | ₹1,100–4,550 | ₹820–3,400 |
| **Total per part** | **≈ ₹800–1,260 (local VMC) / ₹1,700–5,300 (export shop)** | **≈ ₹375–1,210 (local) / ₹1,000–4,230 (export shop)** + one-off fixture |

Reading:
1. **Material saving is real**: about 2.5 kg of bar down to about 0.75 kg of casting. Swarf is roughly 6× smaller.
2. **Machine time only drops about 25–30 %**. Finishing the bearing seats and the two setups dominate on both routes. Casting does not remove the precision-machining step.
3. The casting route wins most where machining is expensive and volumes are ≥ 20–50. For 1–5 prototypes, billet is simpler: no foundry lead time, no porosity risk, and 6061-T6 is stronger than as-cast LM25.
4. A CNC lathe can rough a round housing from bar much faster than a VMC. With good turning the billet route's time penalty shrinks further. This is a reason to keep billet for small runs.

---

## 9. Open items / what to confirm by phone or RFQ
1. A real per-piece quote for 20 and 200 LM25-TF sand castings (Coimbatore: Inticore, Super Tech; Surat: Sigma Techno Cast) with the customer supplying a 3D-printed pattern. Ask about the minimum lot charge and the heat-treat charge.
2. GDC die quote (Castx Pune; Super Tech Coimbatore) versus HPDC die quote (Nunes / Auto Die Cast / Aarenza) for the housing, plus the per-part price at 1k/10k.
3. ISO 8062-3 DCTG/RMAG grade the foundry will commit to on the drawing.
4. PM compaction tooling cost for one planet gear (GKN Sinter Metals India, Sundram, Goldiva).
5. A MIM tooling quote for one planet (Indo-MIM, Goldiva).
6. Vacuum-impregnation and anodising compatibility of LM25 castings (anodise looks grey and blotchy on high-Si alloys).
