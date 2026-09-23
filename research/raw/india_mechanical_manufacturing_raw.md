# JX1 — India mechanical sourcing & manufacturing: RAW research log

- **Project:** JX1 low-cost compact humanoid (~1.2 m, 25–30 kg), built in India. FDM (Bambu P1S class: PETG, PETG-CF, PA-CF) + CNC aluminium only where justified.
- **Research date:** 2026-09-24 (all "VERIFIED" rows were read from the live page/API on this date).
- **Method:** curl/Python against store pages & public JSON: IndustryBuying (search-page `ng-state` JSON, PDP JSON-LD), Moglix (`ssr-pwa-state` JSON), Shopify stores Robocraze / ThinkRobotics / Quartz Components (`/search/suggest.json`, `/products/<handle>.js`; after HTTP 429 rate-limits some reads were done with WebFetch of the same JSON), WooCommerce store bearinghouse.in (`/wp-json/wc/store/products`), Robokits (Zen Cart listing HTML), SKF India e-Marketplace (page title/meta + its search-suggest endpoint), IndiaMART category pages (listing HTML; rate-limited after ~6 pages → leads only), Evelta (BigCommerce listing), WebSearch/WebFetch for services. robu.in, amazon.in, element14, digikey **not** checked (out of scope — covered elsewhere). Filament (§5) and manufacturing-service (§6) sweeps were run as parallel sub-tasks with the same rules.
- **Checked but not useful:** bearingkart.com/.in and bearingsdirect.in (domains do not resolve), rollon.in (parked domain), bearingmart.in / bearingstore.in (no public catalogue/price API), probots.co.in (Magento search returned unrelated items), electronicscomp.com (no bearing results), evelta.com (no bare magnets/mechanical stock).
- **No accounts, no forms submitted, no downloads.**

### Label legend
| Label | Meaning |
|---|---|
| **VERIFIED** | Price/stock seen on the live page or the store's own public JSON on 2026-09-24; URL given. |
| **ESTIMATED** | Derived number; math shown. |
| **UNVERIFIED** | Lead only (IndiaMART/TradeIndia listing, marketing blog, third-party claim, or price not visible in static HTML). Must be confirmed by phone/quote. |

### GST conventions seen
- **IndustryBuying (IB):** listing gives both *incl-GST* and *excl-GST* (GST 18 % on bearings/fasteners). Price is **per selling unit** (per piece, or per pack if title says "Pack of N"). "Min" = minimum order quantity of that unit — check it, some SKUs have MOQ 10–100 units.
- **Moglix:** `salesPrice` = incl GST, `priceWithoutTax` = excl GST; `moq`; `itemInPack`.
- **bearinghouse.in:** shows *excl. GST* and *incl. GST* explicitly (18 %).
- **Robocraze:** product pages state "Incl. GST (No Hidden Charges)".
- **Quartz Components / ThinkRobotics:** Shopify price as displayed; GST wording not present in static HTML → treated as **displayed price (GST status not stated)**; Indian Shopify retail prices are normally GST-inclusive, but confirm at checkout.
- **SKF India e-Marketplace:** price appears in page `<title>`/`og:title` ("at Best Price ₹X"); live price widget is JS-loaded, GST treatment **not visible** in static HTML.
- **Robokits:** product pages show "GST Input Tax Credit @ 18 % of ₹X available" where X = 18 % × displayed price (e.g. ₹315 rod → ₹56.7), i.e. the displayed price may be **ex-GST** (+18 % at checkout) — not confirmed; marked "not stated*".
- **IB GST exceptions:** springs listed at 5 % GST; everything else used here is 18 %.

---

## 0. BEST-VALUE PICKS (quick view; details & URLs in sections below)

| Need | Best-value credible pick (2026-09-24) | ₹ (incl GST unless noted) | Branded fallback |
|---|---|---|---|
| Thin-section 6804/6805/6806/6807/6808/6810/6908 | **FBJ 2RS/ZZ @ bearinghouse.in** (1-pc MOQ, in stock) | 111 / 132 / 165 / 192 / 276 / 470 / 276 | NTN 68xxJR (IB) 353–837; SKF 61805 domestic 261; KOYO 6807 530; SKF 61804-2RS1 1,066 (SKF e-Mkt) |
| 6000/6001/6002/608/625/626/688 | FBJ @ bearinghouse.in; Quartz/Robocraze for 608/625/626 | 30–53 | SKF 6000-2RS1 174 / 608-2RSH 264 (SKF e-Mkt) |
| Angular contact 7001/7002 | KOYO / NTN @ IB | 601 – 707 | SKF 7201/7202 BEP 1,396–1,413 |
| Crossed roller | none cheap: IKO CRBHV3510 / CRB4010 / CRB5013 @ IB | 11,799 – 15,339 | IndiaMART "THK RB3510" lead ₹4,200 (unverified) → **use paired 68xx instead** |
| Thrust / needle | N2K 51104 / 51106, HK0810 / HK1012; KHK AXK3047 @ bearinghouse | 34 – 118 | NBC 51104 152–169 |
| SHCS M3–M6 (bulk) | **Unbrako packs of 100 @ IB** (M3×8 = A2-70 SS) | 211–530 /100 (₹2.1–5.3/pc), 30-day lead | 12.9: Caparo M3×16 ₹896/200; TVS packs on Moglix |
| Heat-set inserts M3 | **Quartz** M3 brass (pack 10) | 33–70 /10 | ThinkRobotics M4/M5 80–100 /10 |
| Dowel pins 3/4/5 mm | CE solid dowel packs of 100 @ IB | 471 – 719 /100 | ThinkRobotics alloy 150–240 /10 |
| Linear shafts Ø5–Ø16 | **Robokits Astro hard-chrome rod, 1 m** | 220 – 450 /m (GST may be extra) | Robocraze SS rods 149–324 (short lengths) |
| Al 6061-T6 | IndiaMART stockists (plate ₹260–555/kg; bar ₹230–300/kg) — leads | – | retail cut plate ≈ ₹1,815/kg (IB Invento) |
| CF tube Ø20–28 | ThinkRobotics roll-wrapped 3K, 1 m | 1,620 – 2,160 | – |
| GT2 belt / pulleys | Robokits (₹46/m belt; 20T–80T pulleys) | 46 /m; 89–419 | IB Invento 4 m belt ₹931 |
| HTD 3M/5M | only Contitech/Optibelt @ IB, 120-day lead | 919+ belt; 3,539+ pulley | → print HTD pulleys, source belts elsewhere |
| Rod ends / ankle linkages | **N2K POS5/PHS5 (M5) @ bearinghouse**; GE12/GE15 spherical plain | 141.60; 159–177 | THK POS5 1,769 (IB) |
| Drag chain | Robokits 10×10 / 15×20 per metre | 215 / 356 | – |
| 2020 extrusion | **Robokits Astro 2020H** per metre | 341 /m | 4040 ₹876/m (pre-order) |
| Foot soles | 4 mm rubber anti-skid mat (Moglix) to cut, or print TPU 95A | 548 /mat | NBR sheet 3 mm 300×300 ₹1,084 (IB) |
| Filament PETG | **Numakers PETG-HS** ₹599 ex-GST (≈ ₹707 incl.) | ≈ 707 /kg | Bambu PETG HF refill ₹1,150 (Ideal3D) |
| Filament PETG-CF | **Numakers PETG-CF** ₹1,149 ex-GST (≈ ₹1,356 incl.) | ≈ 1,356 /kg | Bambu PETG-CF ₹1,599–1,900 — **OOS at all readable resellers** |
| Filament PA-CF | **eSUN PA-CF @ 3Idea** (in stock) | 4,799 /kg | Bambu PAHT-CF ₹6,299 (WOL3D, in stock); Bambu PA6-CF ₹4,999–5,000 (OOS) |
| Filament PLA / PLA+ | Numakers PLA ₹565 / PLA+ ₹600 ex-GST | ≈ 667–708 /kg | Bambu PLA Basic refill ₹1,149–1,150 |
| Filament TPU 95A | **Elegoo TPU 95A @ 3D Master India** | 1,399 /kg | Bambu TPU 95A HF ₹3,299–3,300 |
| Filament ASA | Numakers ASA ₹699 ex-GST (white/grey); black ₹891 incl. (Zbotic) | ≈ 825–891 /kg | Bambu ASA ₹1,999 (WOL3D) |
| PCB fab (5 pcs, 100×100, 2L) | **Lion Circuits** (public calculator) | ₹1,877 ex-GST (≈ ₹2,215 incl), ~5 d | PCB Power ₹5,210 ex-GST; JLCPCB $2 headline (app-only, duty/KYC) |
| Outsourced 3D printing | **iamRapid** published examples | PETG ≈ ₹17/g, CF-PETG ≈ ₹42/g, SLS/MJF PA12 ≈ ₹40/cm³ (ex-GST) | 3Ding (₹200 FDM / ₹2,000 MJF per-part minimum) |
| CNC aluminium | Makenica (instant quote, 1-pc MOQ, <5 d; FAQ anchor ₹7,000 for "1 part") / Robocon CNC (manual quote, in-house anodise) | no public per-part price | FabFlow/Custiv/Karkhana claims ₹450–1,200/bracket (unverified) |
| Laser cutting / bending | no Indian instant-quote site found; IndiaMART fibre-laser shops | ₹40–500 /sq ft, ₹150–200 /kg (unverified) | Manufyn / Custiv manual RFQ |
| Anodising | IndiaMART job shops | Type II ≈ ₹3.9–43 /dm² (unverified, lot charges extra) | Robocon in-house (in quote) |

---

## 1. BEARINGS

### 1a. Thin-section deep-groove (6700 / 6800 / 61800 / 6900 / 61900) — robot-joint output & cross-support bearings

Note: SKF/FAG name 6804 as **61804**, 6908 as **61908**, etc. Dimensions: 6804/61804 = 20×32×7; 6805 = 25×37×7; 6806 = 30×42×7; 6807 = 35×47×7; 6808 = 40×52×7; 6810 = 50×65×7; 6908/61908 = 40×62×12.

| Item | Brand/Model | Supplier | Price ₹ (incl GST) | GST | Qty | Stock / lead | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 6804 | FBJ 6804-2RS (61804 2RS) | bearinghouse.in | 110.92 (ex 94.00) | 18% | 1 pc | In stock | 20×32×7, rubber sealed | https://bearinghouse.in/shop/fbj-6804-2rs-ball-bearing/ | 2026-09-24 | VERIFIED (Woo Store API) |
| 6804 | NBC 6804ZZ | bearinghouse.in | 276.12 (ex 234) | 18% | 1 pc | In stock | 20×32×7, metal shields | https://bearinghouse.in/shop/nbc-6804zz-ball-bearings/ | 2026-09-24 | VERIFIED |
| 6804 | NBC 6804ZZ | IndustryBuying | 294 (ex 249) | 18% | 1 pc, MOQ 2 | In stock, ships ≤4 d | 20×32×7 | https://www.industrybuying.com/deep-groove-ball-bearings-nbc-BEA.DEE.23230984 | 2026-09-24 | VERIFIED (IB search state) |
| 6804 | NTN 6804JR | IndustryBuying | 388 (ex 329) | 18% | 1 pc, MOQ 2 | In stock, ≤8 d | 20×32×7 open | https://www.industrybuying.com/deep-groove-ball-bearings-ntn-FAM163780 | 2026-09-24 | VERIFIED |
| 61804 | SKF 61804/C3 (Domestic) | IndustryBuying | 341 (ex 289) | 18% | 1 pc, MOQ 5 | In stock, ≤30 d | 20×32×7, C3 | https://www.industrybuying.com/deep-groove-ball-bearings-skf-FAM142190 | 2026-09-24 | VERIFIED |
| 61804 | UBC 61804 / 61804 ZZ / 61804 2RS | IndustryBuying | 67 (ex 57) | 18% | 1 pc, MOQ 10 | In stock, ≤3 d | 20×32×7 (generic brand) | https://www.industrybuying.com/deep-groove-ball-bearings-ubc-BEA.DEE.48613516 | 2026-09-24 | VERIFIED |
| 61804 | FAG 61804-HLC (imported) | IndustryBuying | 648 (ex 549) | 18% | 1 pc | In stock, ≤4 d | 20×32×7 | https://www.industrybuying.com/deep-groove-ball-bearings-fag-FAM156097 | 2026-09-24 | VERIFIED |
| 61804 | SKF 61804-2RS1 (imported) | bearinghouse.in | 1,329.86 (ex 1,127) | 18% | 1 pc | In stock | 20×32×7, 2RS1 | https://bearinghouse.in/shop/skf-61804-2rs1-6804-deep-groove-ball-bearing/ | 2026-09-24 | VERIFIED |
| 61804 | SKF 61804-2RS1 | SKF India e-Marketplace (official) | 1,066 (title price) | not shown | 1 pc | – | 20×32×7 | https://www.emarketplace.in.skf.com/deep-groove-ball-bearing/61804-2rs1 | 2026-09-24 | VERIFIED (page title) / GST UNVERIFIED |
| 61804 | SKF 61804-2RZ | SKF India e-Marketplace | 1,056 (title price) | not shown | 1 pc | – | 20×32×7 | https://www.emarketplace.in.skf.com/deep-groove-ball-bearing/61804-2rz | 2026-09-24 | VERIFIED (title) |
| 6805 | FBJ 6805-2RS | bearinghouse.in | 132.16 (ex 112) | 18% | 1 pc | In stock | 25×37×7 | https://bearinghouse.in/shop/fbj-6805-2rs-ball-bearing/ | 2026-09-24 | VERIFIED |
| 6805 | EVO 6805ZZCM | IndustryBuying | 152 (ex 129) | 18% | 1 pc, **MOQ 10** | In stock, ≤11 d | 25×37×7 | https://www.industrybuying.com/deep-groove-ball-bearings-evo-BEA.DEE.66136926 | 2026-09-24 | VERIFIED |
| 6805 | SKF 61805 (domestic, open) | bearinghouse.in | 260.78 (ex 221) | 18% | 1 pc | In stock | 25×37×7 open | https://bearinghouse.in/shop/skf-61805-6805-deep-groove-ball-bearing/ | 2026-09-24 | VERIFIED |
| 6805 | SKF 61805 (domestic) | IndustryBuying | 336 (ex 285) | 18% | 1 pc, MOQ 6 | In stock, ≤7 d | 25×37×7 | https://www.industrybuying.com/deep-groove-ball-bearings-skf-BEA.DEE.107402631 | 2026-09-24 | VERIFIED |
| 6805 | NBC 6805ZZ | bearinghouse.in | 300.90 (ex 255) | 18% | 1 pc | In stock | 25×37×7 ZZ | https://bearinghouse.in/shop/nbc-6805zz-ball-bearings/ | 2026-09-24 | VERIFIED |
| 6805 | NTN 6805JR | IndustryBuying | 353 (ex 299) | 18% | 1 pc, MOQ 2 | In stock, ≤8 d | 25×37×7 | https://www.industrybuying.com/deep-groove-ball-bearings-ntn-FAM165892 | 2026-09-24 | VERIFIED |
| 61805 | SKF 61805-2RS1 | bearinghouse.in | 1,588.28 (ex 1,346) | 18% | 1 pc | In stock | 25×37×7 | https://bearinghouse.in/shop/skf-61805-2rs1-6805-deep-groove-ball-bearing/ | 2026-09-24 | VERIFIED |
| 61805 | SKF 61805-2RS1 | SKF India e-Marketplace | 1,282 (title) | not shown | 1 pc | – | 25×37×7 | https://www.emarketplace.in.skf.com/deep-groove-ball-bearing/61805-2rs1 | 2026-09-24 | VERIFIED (title) |
| 6806 | FBJ 6806-2RS / 6806-ZZ | bearinghouse.in | 165.20 (ex 140) | 18% | 1 pc | In stock | 30×42×7 | https://bearinghouse.in/shop/fbj-6806-2rs-ball-bearing/ | 2026-09-24 | VERIFIED |
| 61806 | UBC 61806 / ZZ / 2RS | IndustryBuying | 100 (ex 85) | 18% | 1 pc, **MOQ 10** | In stock, ≤3 d | 30×42×7 generic | https://www.industrybuying.com/deep-groove-ball-bearings-ubc-BEA.DEE.68626093 | 2026-09-24 | VERIFIED |
| 61806 | CNA 61806 ZZ (Pack of 10) | Moglix | 2,313 /10 (ex 1,960) → **231/pc** | 18% | 10 pcs | Qty avail 100; ETA 1 Oct | 30×42×7 | https://www.moglix.com/cna-61806-zz-deep-groove-ball-bearing-42x30x7-mm-pack-of-10/mp/msnr50nw8p1251 | 2026-09-24 | VERIFIED |
| 6806 | NTN 6806JR | IndustryBuying | 459 (ex 389) | 18% | 1 pc | In stock, ≤8 d | 30×42×7 | https://www.industrybuying.com/deep-groove-ball-bearings-ntn-FAM165919 | 2026-09-24 | VERIFIED |
| 61806 | FAG 61806-HLC (imported) | IndustryBuying | 1,073 (ex 909) | 18% | 1 pc | In stock, ≤4 d | 30×42×7 | https://www.industrybuying.com/deep-groove-ball-bearings-fag-FAM156109 | 2026-09-24 | VERIFIED |
| 61806 | SKF 61806 (open) | bearinghouse.in | 1,416.00 (ex 1,200) | 18% | 1 pc | In stock | 30×42×7 | https://bearinghouse.in/shop/skf-6806-deep-groove-ball-bearing/ | 2026-09-24 | VERIFIED |
| 61806 | SKF 61806-2RS1 (imported) | bearinghouse.in | 1,949.36 (ex 1,652) | 18% | 1 pc | In stock | 30×42×7 | https://bearinghouse.in/shop/skf-61806-2rs1-6806-deep-groove-ball-bearing/ | 2026-09-24 | VERIFIED |
| 6807 | FBJ 6807-ZZ / 6807-2RS | bearinghouse.in | 184.08 / 192.34 (ex 156/163) | 18% | 1 pc | In stock | 35×47×7 | https://bearinghouse.in/shop/fbj-6807-2rs-ball-bearing/ | 2026-09-24 | VERIFIED |
| 6807 | EVO 6807LLUCM | IndustryBuying | 211 (ex 179) | 18% | 1 pc, MOQ 2 | In stock, ≤7 d | 35×47×7 sealed | https://www.industrybuying.com/deep-groove-ball-bearings-evo-BEA.DEE.26136943 | 2026-09-24 | VERIFIED |
| 61807 | UBC 61807 | IndustryBuying | 176 (ex 149) | 18% | 1 pc, MOQ 10 | In stock, ≤3 d | 35×47×7 | https://www.industrybuying.com/deep-groove-ball-bearings-ubc-BEA.DEE.98626137 | 2026-09-24 | VERIFIED |
| 61807 | CNA 61807 ZZ (Pack of 10) | Moglix | 2,582 /10 → **258/pc** (ex 2,188) | 18% | 10 pcs | Qty avail 100 | 35×47×7 | https://www.moglix.com/cna-61807-zz-single-row-deep-groove-ball-bearing-35x47x7-mm-pack-of-10/mp/msnr50nev0e251 | 2026-09-24 | VERIFIED |
| 61807 | ZKL 61807-2RS | IndustryBuying | 400 (ex 339) | 18% | 1 pc | In stock, ≤10 d | 35×47×7 (Czech/ZKL) | https://www.industrybuying.com/deep-groove-ball-bearings-zkl-BEA.DEE.325502172 | 2026-09-24 | VERIFIED |
| 6807 | KOYO 6807 | IndustryBuying | 530 (ex 449) | 18% | 1 pc | In stock, ≤30 d | 35×47×7 | https://www.industrybuying.com/deep-groove-ball-bearings-koyo-FAM116823 | 2026-09-24 | VERIFIED |
| 61807 | SKF 61807-2RS1 | bearinghouse.in | 2,256.16 (ex 1,912) | 18% | 1 pc | In stock | 35×47×7 | https://bearinghouse.in/shop/skf-61807-2rs1-6807-deep-groove-ball-bearing/ | 2026-09-24 | VERIFIED |
| 6808 | FBJ 6808-ZZ / 6808-2RS | bearinghouse.in | 247.80 / 276.12 (ex 210/234) | 18% | 1 pc | In stock | 40×52×7 | https://bearinghouse.in/shop/fbj-6808-2rs-ball-bearing/ | 2026-09-24 | VERIFIED |
| 61808 | UBC 61808 ZZ | IndustryBuying | 188 (ex 159) | 18% | 1 pc, MOQ 10 | In stock, ≤3 d | 40×52×7 | https://www.industrybuying.com/deep-groove-ball-bearings-ubc-BEA.DEE.98626160 | 2026-09-24 | VERIFIED |
| 6808 | NTN 6808JR | IndustryBuying | 589 (ex 499) | 18% | 1 pc | In stock, ≤8 d | 40×52×7 | https://www.industrybuying.com/deep-groove-ball-bearings-ntn-FAM165957 | 2026-09-24 | VERIFIED |
| 61808 | FAG 61808-2Z-HLC | IndustryBuying | 1,769 (ex 1,499) | 18% | 1 pc | In stock, ≤4 d | 40×52×7 | https://www.industrybuying.com/deep-groove-ball-bearings-fag-FAM156116 | 2026-09-24 | VERIFIED |
| 61808 | SKF 61808-2RS1 | bearinghouse.in | 3,348.84 (ex 2,838) | 18% | 1 pc | In stock | 40×52×7 | https://bearinghouse.in/shop/skf-61808-2rs1-6808-deep-groove-ball-bearing/ | 2026-09-24 | VERIFIED |
| 6810 | FBJ 6810-ZZ / 6810-2RS | bearinghouse.in | 401.20 / 469.64 (ex 340/398) | 18% | 1 pc | In stock | 50×65×7 | https://bearinghouse.in/shop/fbj-6810-2rs-ball-bearing/ | 2026-09-24 | VERIFIED |
| 61810 | UBC 61810 / ZZ / 2RS | IndustryBuying | 317 (ex 269) | 18% | 1 pc, MOQ 10 | In stock, ≤3 d | 50×65×7 | https://www.industrybuying.com/deep-groove-ball-bearings-ubc-BEA.DEE.38626207 | 2026-09-24 | VERIFIED |
| 61810 | ZKL 61810-2RS | IndustryBuying | 754 (ex 639) | 18% | 1 pc | In stock, ≤10 d | 50×65×7 | https://www.industrybuying.com/deep-groove-ball-bearings-zkl-BEA.DEE.925502253 | 2026-09-24 | VERIFIED |
| 6810 | NTN 6810JR | IndustryBuying | 837 (ex 709) | 18% | 1 pc | In stock, ≤8 d | 50×65×7 | https://www.industrybuying.com/deep-groove-ball-bearings-ntn-FAM165990 | 2026-09-24 | VERIFIED |
| 6810 | KOYO 6810ZZCM | IndustryBuying | 978 (ex 829) | 18% | 1 pc | In stock, ≤3 d | 50×65×7 | https://www.industrybuying.com/deep-groove-ball-bearings-koyo-FAM116826 | 2026-09-24 | VERIFIED |
| 61810 | SKF 61810-2RS1 | bearinghouse.in | 4,485.18 (ex 3,801) | 18% | 1 pc | In stock | 50×65×7 | https://bearinghouse.in/shop/skf-61810-2rs1-6810-deep-groove-ball-bearing/ | 2026-09-24 | VERIFIED |
| 6908 | FBJ 6908 / 6908-ZZ / 6908-2RS | bearinghouse.in | 238.36 / 266.68 / 276.12 | 18% | 1 pc | In stock | 40×62×12 | https://bearinghouse.in/shop/fbj-6908-2rs-ball-bearing/ | 2026-09-24 | VERIFIED |
| 61908 | UBC 61908 / ZZ / 2RS | IndustryBuying | 247 (ex 209) | 18% | 1 pc, MOQ 10 | In stock, ≤3 d | 40×62×12 | https://www.industrybuying.com/deep-groove-ball-bearings-ubc-BEA.DEE.28626703 | 2026-09-24 | VERIFIED |
| 6908 | KOYO 6908ZZC3 | IndustryBuying | 542 (ex 459) | 18% | 1 pc | In stock, ≤3 d | 40×62×12 | https://www.industrybuying.com/deep-groove-ball-bearings-koyo-FAM116859 | 2026-09-24 | VERIFIED |
| 6908 | NBC 6908ZZ | bearinghouse.in | 628.94 (ex 533) | 18% | 1 pc | In stock | 40×62×12 | https://bearinghouse.in/shop/nbc-6908zz-ball-bearings/ | 2026-09-24 | VERIFIED |
| 6908 | NTN 6908 | IndustryBuying | 825 (ex 699) | 18% | 1 pc | In stock, ≤5 d | 40×62×12 | https://www.industrybuying.com/deep-groove-ball-bearings-ntn-FAM163836 | 2026-09-24 | VERIFIED |
| 61908 | FAG 61908 / 61908-C3 | IndustryBuying | 2,359 (ex 1,999) | 18% | 1 pc | In stock, ≤4 d | 40×62×12 | https://www.industrybuying.com/deep-groove-ball-bearings-fag-FAM156117 | 2026-09-24 | VERIFIED |
| 61908 | SKF 61908-2RS1 / -2RZ | SKF India e-Marketplace | 4,235 (title) | not shown | 1 pc | – | 40×62×12 | https://www.emarketplace.in.skf.com/deep-groove-ball-bearing/61908-2rs1 | 2026-09-24 | VERIFIED (title) |
| 61908 | SKF 61908-2RS1 | bearinghouse.in | 5,272.24 (ex 4,468) | 18% | 1 pc | In stock | 40×62×12 | https://bearinghouse.in/shop/skf-61908-2rs1-6908-deep-groove-ball-bearing/ | 2026-09-24 | VERIFIED |
| 61904/5/6 | SKF 61904-2RS1 / 61905-2RS1 / 61906-2RS1 | SKF India e-Marketplace | 938 / 1,107 / 1,346 (title) | not shown | 1 pc | – | 20×37×9 / 25×42×9 / 30×47×9 | https://www.emarketplace.in.skf.com/deep-groove-ball-bearing/61906-2rs1 | 2026-09-24 | VERIFIED (title) |
| 61900–61902 | SKF 61900-2RS1 / 61901-2RS1 / 61902-2RS1 | SKF India e-Marketplace | 774 / 747 / 842 (title) | not shown | 1 pc | – | 10×22×6 / 12×24×6 / 15×28×7 | https://www.emarketplace.in.skf.com/deep-groove-ball-bearing/61901-2rs1 | 2026-09-24 | VERIFIED (title) |
| 6700 | NTN 6700 / NSK 6700 | IndustryBuying | 1,297 / 1,415 | 18% | 1 pc | In stock, ≤19 d | 10×15×3 | https://www.industrybuying.com/deep-groove-ball-bearings-ntn-BEA.DEE.638787477 | 2026-09-24 | VERIFIED (expensive; Japanese import) |
| 6704 | NSK 6704ZZ | IndustryBuying | 1,132 (ex 959) | 18% | 1 pc | In stock, ≤19 d | 20×27×4 | https://www.industrybuying.com/special-bearing-nsk-BEA.NSK.33961495 | 2026-09-24 | VERIFIED |

**Observations (bearings 1a):**
- Cheapest credible thin-section source = **bearinghouse.in FBJ** line (₹111–470 incl GST, 1-pc MOQ, in stock). FBJ is a Chinese commodity brand — fine for prototypes; check radial play before use in joint output stages.
- "Branded but cheap": **SKF domestic 61805 @ ₹261–336**, **NTN 6804JR–6810JR @ ₹353–837**, **KOYO 6807 @ ₹530**. Imported SKF 2RS1 thin-section = ₹1.3k–5.3k (4–10× FBJ).
- IB "UBC" generic 618xx is the lowest unit price (₹67–317) but **MOQ 10**.
- 6700-series (ultra-thin) only as Japanese imports at ₹1.1k–1.4k each on IB → avoid in design, or source via robu/AliExpress (not checked here).

### 1b. Standard small bearings (6000/6001/6002, 608, 625, 626, 688)

| Item | Brand/Model | Supplier | Price ₹ (incl GST) | GST | Qty | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 6000 | FBJ 6000-2RS | bearinghouse.in | 40.12 (ex 34) | 18% | 1 | In stock | 10×26×8 | https://bearinghouse.in/shop/fbj-6000-2rs-ball-bearing/ | 2026-09-24 | VERIFIED |
| 6000 | NBC 6000RSS (2RS) | bearinghouse.in | 114.46 (ex 97) | 18% | 1 | In stock | 10×26×8 | https://bearinghouse.in/shop/nbc-6000rss-ball-bearings/ | 2026-09-24 | VERIFIED |
| 6000 | SKF 6000-2RS1 | bearinghouse.in | 238.36 (ex 202) | 18% | 1 | In stock | 10×26×8 | https://bearinghouse.in/shop/skf-6000-2rs1-deep-groove-ball-bearings/ | 2026-09-24 | VERIFIED |
| 6000 | SKF 6000-2RS1 | SKF India e-Marketplace | 174 (title) | not shown | 1 | – | 10×26×8 | https://www.emarketplace.in.skf.com/deep-groove-ball-bearing/6000-2rs1 | 2026-09-24 | VERIFIED (title) |
| 6000 | Quartz "6000 ZZ" | quartzcomponents.com | 23 | displayed | 1 | Available | 10×26×8 ZZ (unbranded) | https://quartzcomponents.com/products/6000-zz-metal-double-shielded-miniature-ball-bearings10mm-x-26mm-x-8mm-robotics | 2026-09-24 | VERIFIED (Shopify JSON) |
| 6001 | FBJ 6001-2RS | bearinghouse.in | 41.30 (ex 35) | 18% | 1 | In stock | 12×28×8 | https://bearinghouse.in/shop/fbj-6001-2rs-ball-bearing/ | 2026-09-24 | VERIFIED |
| 6001 | SKF 6001-2RS1 | SKF India e-Marketplace | 175 (title) | not shown | 1 | – | 12×28×8 | https://www.emarketplace.in.skf.com/deep-groove-ball-bearing/6001-2rs1 | 2026-09-24 | VERIFIED (title) |
| 6001 | MBL 6001 2RS | IndustryBuying | 39 (ex 33) | 18% | 1, MOQ 10 | In stock ≤4 d | 12×28×8 | https://www.industrybuying.com/deep-groove-ball-bearings-mbl-FAM247807 | 2026-09-24 | VERIFIED |
| 6002 | FBJ 6002-2RS | bearinghouse.in | 50.74 (ex 43) | 18% | 1 | In stock | 15×32×9 | https://bearinghouse.in/shop/fbj-6002-2rs-ball-bearing/ | 2026-09-24 | VERIFIED |
| 6002 | NBC 6002LLU (2RS) | bearinghouse.in | 148.68 (ex 126) | 18% | 1 | In stock | 15×32×9 | https://bearinghouse.in/shop/nbc-6002llu-ball-bearings/ | 2026-09-24 | VERIFIED |
| 6002 | SKF 6002-2RS1 | SKF India e-Marketplace | 189 (title) | not shown | 1 | – | 15×32×9 | https://www.emarketplace.in.skf.com/deep-groove-ball-bearing/6002-2rs1 | 2026-09-24 | VERIFIED (title) |
| 608 | FBJ 608-2RS | bearinghouse.in | 30.68 (ex 26) | 18% | 1 | In stock | 8×22×7 | https://bearinghouse.in/shop/fbj-608-2rs-ball-bearing/ | 2026-09-24 | VERIFIED |
| 608 | NBC 608ZZ | bearinghouse.in | 66.08 (ex 56) | 18% | 1 | In stock | 8×22×7 | https://bearinghouse.in/shop/nbc-608zz-ball-bearings/ | 2026-09-24 | VERIFIED |
| 608 | SKF 608-2RSH | SKF India e-Marketplace | 264 (title) | not shown | 1 | – | 8×22×7 | https://www.emarketplace.in.skf.com/deep-groove-ball-bearing/608-2rsh | 2026-09-24 | VERIFIED (title) |
| 608 | Quartz "608 2RS" | quartzcomponents.com | 24 | displayed | 1 | Available | 8×22×7 | https://quartzcomponents.com/products/608-2rs-rubber-sealed-ball-bearings-8-22-7-mm-double-rubber-sealed | 2026-09-24 | VERIFIED |
| 608 | Robocraze 608ZZ (Pack of 4) | robocraze.com | 135 /4 → 33.75/pc | incl | 4 | Available | 8×22×7 | https://robocraze.com/products/radial-ball-bearing-608zz-for-3d-printer-pack-of-4 | 2026-09-24 | VERIFIED |
| 625 | FBJ 625-ZZ / 625-2RS | bearinghouse.in | 44.84 / 53.10 | 18% | 1 | In stock | 5×16×5 | https://bearinghouse.in/shop/fbj-625-2rs-ball-bearing/ | 2026-09-24 | VERIFIED |
| 625 | Quartz "625 ZZ" | quartzcomponents.com | 20 | displayed | 1 | Available | 5×16×5 | https://quartzcomponents.com/products/606-zz-miniature-deep-groove-ball-bearing-6-17-6-mm-double-metal-shielded | 2026-09-24 | VERIFIED |
| 625 | Robocraze 625ZZ (Pack of 4) | robocraze.com | 69 /4 → 17.25/pc | incl | 4 | Available | 5×16×5 | https://robocraze.com/products/radial-ball-bearing-625zz-for-3d-printer-pack-of-4 | 2026-09-24 | VERIFIED |
| 625 | SKF 625-2Z | SKF India e-Marketplace | 253 (title) | not shown | 1 | – | 5×16×5 | https://www.emarketplace.in.skf.com/deep-groove-ball-bearing/625-2z | 2026-09-24 | VERIFIED (title) |
| 626 | FBJ 626-2RS / 626-ZZ | bearinghouse.in | 30.68 (ex 26) | 18% | 1 | In stock | 6×19×6 | https://bearinghouse.in/shop/fbj-626-2rs-ball-bearing/ | 2026-09-24 | VERIFIED |
| 626 | Robocraze 626ZZ | robocraze.com | 21 | incl | 1 | Available | 6×19×6 | https://robocraze.com/products/radial-ball-bearing-626zz-for-3d-printer | 2026-09-24 | VERIFIED |
| 626 | SKF 626-2RS | bearinghouse.in | 210.04 (ex 178) | 18% | 1 | In stock | 6×19×6 | https://bearinghouse.in/shop/skf-626-2rs-deep-groove-ball-bearing/ | 2026-09-24 | VERIFIED |
| 688 | FBJ 688-2RS | bearinghouse.in | 51.92 (ex 44) | 18% | 1 | In stock | 8×16×5 | https://bearinghouse.in/shop/fbj-688-2rs-ball-bearing/ | 2026-09-24 | VERIFIED |
| 688 | NBC 688ZZ | bearinghouse.in | 93.22 (ex 79) | 18% | 1 | In stock | 8×16×5 | https://bearinghouse.in/shop/nbc-688zz-ball-bearings/ | 2026-09-24 | VERIFIED |
| 688 | Quartz "688 ZZ" | quartzcomponents.com | 19 | displayed | 1 | Available | title says 8×22×7 but handle says 8×16×5 — **listing inconsistent, confirm** | https://quartzcomponents.com/products/688-zz-invento-8mm-rod-radial-ball-bearings-8x16x5mm-robotics-bearing | 2026-09-24 | VERIFIED (price) / spec UNVERIFIED |

**Small bearings for planetary carriers / idlers (6xx, MR)**

| Item | Brand/Model | Supplier | Price ₹ | GST | Qty | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 623ZZ | Quartz "623 ZZ Bearings" | quartzcomponents.com | 25 | displayed | 1 | Available | 3×10×4 | https://quartzcomponents.com/products/623-zz-bearings-limiting-robotics-projects-3-x-10-x-4-mm-radial-bearing | 2026-09-24 | VERIFIED |
| 693ZZ | Quartz | quartzcomponents.com | 31 | displayed | 1 | Available | 3×8×4 | https://quartzcomponents.com/products/693zz-ball-bearings-miniature-carbon-steel-bearings-3mm-x-8mm-x-4-mm-deep-groove-bearing | 2026-09-24 | VERIFIED |
| 684ZZ / 604ZZ / 605ZZ | Quartz | quartzcomponents.com | 30 / 38 / 39 | displayed | 1 | Available | 4×9×4 / 4×12×4 / 5×14×5 | 684: https://quartzcomponents.com/products/608-zz-miniature-deep-groove-ball-bearing-8-22-7-mm-double-metal-shielded-copy-1 ; 604: https://quartzcomponents.com/products/12-4-4mm-ball-bearing-604-zz-stainless-steel-pack-of ; 605: https://quartzcomponents.com/products/m10r6-zz-miniature-deep-groove-ball-bearing-6-10-3-mm-double-metal-shielded-copy | 2026-09-24 | VERIFIED |
| MR105ZZ / MR106ZZ | Quartz | quartzcomponents.com | 60 / 60 | displayed | 1 | Available | 5×10×4 / 6×10×3 | MR105: https://quartzcomponents.com/products/625-zz-miniature-deep-groove-ball-bearing-5-16-5-mm-double-metal-shielded ; MR106: https://quartzcomponents.com/products/m10r5-zz-miniature-deep-groove-ball-bearing-5-10-4-mm-double-metal-shielded-copy | 2026-09-24 | VERIFIED (Quartz handles do not match titles) |
| 623-ZZ / 605-ZZ / 693ZZ | FBJ | bearinghouse.in | 48.38 / 48.38 / 41.30 (ex 41/41/35) | 18% | 1 | In stock | – | https://bearinghouse.in/shop/fbj-623-zz-ball-bearing/ | 2026-09-24 | VERIFIED |
| 623ZZ | NBC / SKF 623-2Z | bearinghouse.in | 93.22 / 247.80 | 18% | 1 | In stock | – | https://bearinghouse.in/shop/skf-623-2z-zz-deep-groove-ball-bearing/ | 2026-09-24 | VERIFIED |
| F688ZZ | Robokits | robokits.co.in | 26 | not stated* | 1 | In stock | 8×16×5 flanged | https://robokits.co.in/3d-printer/accessories/f688zz-flanged-shielded-deep-groove-ball-bearing | 2026-09-24 | VERIFIED |

(*Robokits GST: see note under §2a.)

### 1c. Angular-contact (7000 series) — for preloaded pairs (e.g. hip-yaw, wrist)

| Item | Brand/Model | Supplier | Price ₹ (incl GST) | GST | Qty | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 7001 | KOYO 7001 | IndustryBuying | 601 (ex 509) | 18% | 1 | In stock ≤3 d | 12×28×8, single row | https://www.industrybuying.com/angular-contact-ball-bearings-koyo-BEA.ANG.14120958 | 2026-09-24 | VERIFIED |
| 7001 | NTN 7001 | IndustryBuying | 612 (ex 519) | 18% | 1 | In stock ≤8 d | 12×28×8 | https://www.industrybuying.com/angular-contact-ball-bearings-ntn-PO.BE.AN.181059 | 2026-09-24 | VERIFIED |
| 7001 | NTN 7001 (Pack of 5) | Moglix | 2,677 /5 → 535/pc (ex 2,269) | 18% | 5 | MOQ 1 pack; qty-available field = 1 | 12×28×8, C 5.05 kN | https://www.moglix.com/ntn-12x28x8mm-single-angular-contact-ball-bearing-7001-pack-of-5/mp/msn4k6zjywp8kq | 2026-09-24 | VERIFIED |
| 7002 | KOYO 7002 | IndustryBuying | 695 (ex 589) | 18% | 1 | In stock ≤4 d | 15×32×9 | https://www.industrybuying.com/angular-contact-ball-bearings-koyo-BEA.ANG.14120965 | 2026-09-24 | VERIFIED |
| 7002 | NTN 7002 | IndustryBuying | 707 (ex 599) | 18% | 1 | In stock ≤8 d | 15×32×9 | https://www.industrybuying.com/angular-contact-ball-bearings-ntn-FAM168870 | 2026-09-24 | VERIFIED |
| 7000 | NSK 7000A | IndustryBuying | 1,769 (ex 1,499) | 18% | 1 | In stock ≤19 d | 10×26×8 | https://www.industrybuying.com/angular-contact-ball-bearings-nsk-BEA.ANG.238731051 | 2026-09-24 | VERIFIED |
| 7200 | SKF 7200 BEP | bearinghouse.in | 1,686.22 (ex 1,429) | 18% | 1 | In stock | 10×30×9 (per designation) | https://bearinghouse.in/shop/skf-7200-bep-angular-contact-ball-bearing/ | 2026-09-24 | VERIFIED |
| 7201 / 7202 | SKF 7201 BEP / 7202 BEP | SKF India e-Marketplace | 1,413 / 1,396 (title price) | not shown | 1 | – | 12×32×10 / 15×35×11 (per designation) | https://www.emarketplace.in.skf.com/angular-contact-ball-bearing/7201-bep | 2026-09-24 | VERIFIED (title) |

Note: No cheap generic 7000-series seen at bearinghouse/IB; KOYO/NTN 7001–7002 at ₹600–700 are the best value found. For thin preloaded pairs consider 2× 6800-series back-to-back with printed spacers instead (design option).

### 1d. Crossed-roller bearings (RU / RB / CRBH / CRBC)

| Item | Brand/Model | Supplier | Price ₹ | GST | Qty | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| CRBHV3510 | IKO CRBHV3510AC1 | IndustryBuying | 11,799 (ex 9,999) | 18% | 1 | "In stock", ships ≤19 d | C = 7,900 N (listing); 35×60×10 per IKO designation (not on listing) | https://www.industrybuying.com/special-bearing-iko-BEA.SPE.939191295 | 2026-09-24 | VERIFIED |
| CRB4010 | IKO CRB4010C1 | IndustryBuying | 15,339 (ex 12,999) | 18% | 1 | ≤19 d | C = 5,980 N (listing); 40×65×10 per designation (not on listing) | https://www.industrybuying.com/special-bearing-iko-BEA.SPE.939192083 | 2026-09-24 | VERIFIED |
| CRB5013 | IKO CRB5013C1 | IndustryBuying | 15,339 (ex 12,999) | 18% | 1 | ≤19 d | C = 14,200 N (listing); 50×80×13 per designation (not on listing) | https://www.industrybuying.com/special-bearing-iko-BEA.SPE.739192138 | 2026-09-24 | VERIFIED |
| RB3510 | "THK RB3510 UU" | IndiaMART seller (Ahmedabad, listing) | 4,200 /pc (listing) | ? | 1 | ? | 35×60×10 per THK designation | https://dir.indiamart.com/impcat/crossed-roller-bearings.html | 2026-09-24 | UNVERIFIED (lead; authenticity unknown) |
| RB/CRB 20 mm bore | "Crossed Roller Bearings" RB/CRB, 20 bore, 36 OD | IndiaMART — Vaibhav Bearing Centre, Mumbai | 4,000 /pc (listing) | ? | 1 | ? | 20×36 (≈RB2008) | https://dir.indiamart.com/impcat/crossed-roller-bearings.html | 2026-09-24 | UNVERIFIED |
| RU42/RU66/RU85 | "THK Cross Roller Ring RU" | IndiaMART — Mechatronix Pvt Ltd, Mumbai | 22,500 /pc (listing) | ? | 1 | ? | RU42 = 20×70×12 | https://dir.indiamart.com/impcat/crossed-roller-bearings.html | 2026-09-24 | UNVERIFIED |
| RB2008 | RB2008UUCCOP5 | IndiaMART — JK Linear Motion, Dombivli | 1,111 (placeholder; seller says "ask price") | ? | 1 | ? | 20×36×8 | https://dir.indiamart.com/impcat/crossed-roller-bearings.html | 2026-09-24 | UNVERIFIED |

**Crossed-roller takeaway:** genuine IKO/THK in India = ₹11.8k–22.5k each → not viable for a ~12–14-joint low-cost build. Options: (a) import Chinese RU42/CRBH-class (not priced here — out of scope), (b) replace with **pairs of 68xx/69xx thin-section bearings** (₹110–470 each from bearinghouse FBJ) spaced apart in a printed/aluminium housing, or (c) **4-point contact wire-race / printed-race** designs. Recommend (b) for JX1 v1.

### 1e. Thrust & needle bearings

| Item | Brand/Model | Supplier | Price ₹ (incl GST) | GST | Qty | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 51100 | FBJ 51100 | bearinghouse.in | 73.16 (ex 62) | 18% | 1 | In stock | 10×24×9 thrust ball | https://bearinghouse.in/shop/fbj-51100-thrust-ball-bearing/ | 2026-09-24 | VERIFIED |
| 51100 | UBC 51100 | IndustryBuying | 68 (ex 58) | 18% | 1, MOQ 10 | In stock ≤3 d | 10×24×9 | https://www.industrybuying.com/thrust-roller-bearings-ubc-BEA.THR.98612717 | 2026-09-24 | VERIFIED |
| 51101 | FBJ 51101 | bearinghouse.in | 77.88 (ex 66) | 18% | 1 | In stock | 12×26×9 | https://bearinghouse.in/shop/fbj-51101-thrust-ball-bearing/ | 2026-09-24 | VERIFIED |
| 51101 | NBC 51101 | bearinghouse.in | 151.04 (ex 128) | 18% | 1 | In stock | 12×26×9 | https://bearinghouse.in/shop/nbc-51101-ball-bearings/ | 2026-09-24 | VERIFIED |
| 51104 | N2K 51104 | bearinghouse.in | 34.22 (ex 29) | 18% | 1 | In stock | 20×35×10 | https://bearinghouse.in/shop/n2k-51104-thrust-ball-bearing/ | 2026-09-24 | VERIFIED |
| 51104 | NBC 51104 | bearinghouse.in | 168.74 (ex 143) | 18% | 1 | In stock | 20×35×10 | https://bearinghouse.in/shop/nbc-51104-ball-bearings/ | 2026-09-24 | VERIFIED |
| 51104 | NBC 51104 | IndustryBuying | 152 (ex 129) | 18% | 1, MOQ 5 | In stock ≤4 d | 20×35×10 | https://www.industrybuying.com/thrust-roller-bearings-nbc-PO.BE.DE.455405 | 2026-09-24 | VERIFIED |
| 51106 | N2K 51106 | bearinghouse.in | 62.54 (ex 53) | 18% | 1 | In stock | 30×47×11 | https://bearinghouse.in/shop/n2k-51106-thrust-ball-bearing/ | 2026-09-24 | VERIFIED |
| 51106 | NBC 51106 | bearinghouse.in | 234.82 (ex 199) | 18% | 1 | In stock | 30×47×11 | https://bearinghouse.in/shop/nbc-51106-ball-bearings/ | 2026-09-24 | VERIFIED |
| AXK3047 | KHK AXK 3047 needle thrust | bearinghouse.in | 118.00 (ex 100) | 18% | 1 | In stock | 30×47 per designation (check whether AS washers are included) | https://bearinghouse.in/shop/khk-axk-3047-needle-thrust-bearings/ | 2026-09-24 | VERIFIED |
| AXK3047 | INA AXK3047-A/0-10 | IndustryBuying | 1,179 (ex 999) | 18% | 1 | ≤120 d | 30×47 | https://www.industrybuying.com/spherical-roller-bearings-ina-BEA.SPH.434946234 | 2026-09-24 | VERIFIED (long lead) |
| AXK1024 | INA AXK1024-A/0-10 | IndustryBuying | 931 (ex 789) | 18% | 1 | ≤120 d | 10×24 | https://www.industrybuying.com/spherical-roller-bearings-ina-BEA.SPH.234946186 | 2026-09-24 | VERIFIED (long lead) |
| HK0810 | N2K HK0810 | bearinghouse.in | 35.40 (ex 30) | 18% | 1 | In stock | 8×12×10 drawn cup | https://bearinghouse.in/shop/n2k-hk0810-needle-roller-bearing/ | 2026-09-24 | VERIFIED |
| HK0810 | NTN HK0810C | IndustryBuying | 84 (ex 71) | 18% | 1, MOQ 10 | In stock ≤8 d | 8×12×10 | https://www.industrybuying.com/needle-roller-bearings-ntn-PO.BE.NE.185996 | 2026-09-24 | VERIFIED |
| HK1012 | N2K HK1012 | bearinghouse.in | 41.30 (ex 35) | 18% | 1 | In stock | 10×14×12 | https://bearinghouse.in/shop/n2k-hk1012-needle-roller-bearing/ | 2026-09-24 | VERIFIED |
| HK1012 | INA HK1012 | bearinghouse.in | 177.00 (ex 150) | 18% | 1 | In stock | 10×14×12 | https://bearinghouse.in/shop/ina-hk1012-needle-roller-bearing/ | 2026-09-24 | VERIFIED |
| HK1012 | NTN HK1012 | IndustryBuying | 103 (ex 87) | 18% | 1, MOQ 5 | ≤30 d | 10×14×12 | https://www.industrybuying.com/needle-roller-bearings-ntn-FAM167547 | 2026-09-24 | VERIFIED |

(AXK2035 was not found on IB/bearinghouse under that exact number on 2026-09-24.)

### 1f. Flanged miniature bearings

| Item | Brand/Model | Supplier | Price ₹ | GST | Qty | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| F688ZZ | Quartz F688ZZ | quartzcomponents.com | 36 | displayed | 1 | Available | 8×16×5 flanged | https://quartzcomponents.com/products/f688zz-flanged-stee-ball-bearing | 2026-09-24 | VERIFIED |
| F608ZZ | FBJ F-608-ZZ | bearinghouse.in | 106.20 (ex 90) | 18% | 1 | In stock | 8×22×7 flanged | https://bearinghouse.in/shop/fbj-f-608-zz-ball-bearing/ | 2026-09-24 | VERIFIED |
| F625ZZ | NSK F625ZZ | IndustryBuying | 483 (ex 409) | 18% | 1 | ≤19 d | 5×16×5 flanged | https://www.industrybuying.com/flange-bearings-nsk-BEA.NSK.83961247 | 2026-09-24 | VERIFIED |
| MF105ZZ | Robocraze MF105ZZ | robocraze.com | 42 | incl | 1 | Available | 5×10×4 flanged | https://robocraze.com/products/mf105zz-flanged-shielded-bearing | 2026-09-24 | VERIFIED |
| F604ZZ | Robocraze F604ZZ | robocraze.com | 40 | incl | 1 | Available | 4×12×4 flanged | https://robocraze.com/products/f604zz-flanged-shielded-ball-bearing | 2026-09-24 | VERIFIED |

---
## 2. FASTENERS

Per-piece cost is shown as ESTIMATED (= pack price ÷ pack qty).

### 2a. Socket-head cap screws (SHCS), button/countersunk heads

| Item | Brand/Model | Supplier | Price ₹ (incl GST) | GST | Qty | Stock / lead | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| M3×8 SHCS | Unbrako 5000731 | IndustryBuying | 211 (ex 179) → ₹2.11/pc | 18% | Pack 100, MOQ 1 | In stock, ships ≤30 d | ISO 4762 / DIN 912, **A2-70, AISI 304** (PDP spec) | https://www.industrybuying.com/socket-head-cap-screw-unbrako-FA.SC.SO4.208127 | 2026-09-24 | VERIFIED (PDP JSON-LD + spec) |
| M3×6/10/12/16/20 SHCS | Unbrako 5000730/32/33/34/35 | IndustryBuying | 223 / 223 / 223 / 247 / 270 per 100 | 18% | Pack 100 | ≤30 d | ISO 4762; material not stated on these PDPs (sister SKU 5000731 = A2-70) | https://www.industrybuying.com/socket-head-cap-screw-unbrako-FA.SC.SO4.208129 | 2026-09-24 | VERIFIED (price) / material UNVERIFIED |
| M3×8 SHCS | Unbrako 5000947 | IndustryBuying | 258 (ex 219) | 18% | Pack 100 | ≤30 d | ISO 4762 (grade not stated) | https://www.industrybuying.com/socket-head-cap-screw-unbrako-FA.SC.SO4.208403 | 2026-09-24 | VERIFIED |
| M4×8/10/12/16 SHCS | Unbrako 5000739/40/41/42 | IndustryBuying | 247 / 235 / 235 / 270 per 100 (≈₹2.35/pc) | 18% | Pack 100 | ≤30 d | ISO 4762 | https://www.industrybuying.com/socket-head-cap-screw-unbrako-FA.SC.SO4.208137 | 2026-09-24 | VERIFIED |
| M5×10/12/16/20/25 SHCS | Unbrako 5000749/50/51/52/53 | IndustryBuying | 294 / 317 / 353 / 388 / 435 per 100 | 18% | Pack 100 | ≤30 d | ISO 4762 | https://www.industrybuying.com/socket-head-cap-screw-unbrako-FA.SC.SO4.208146 | 2026-09-24 | VERIFIED |
| M6×10/12/16/20/25 SHCS | Unbrako 5000762/63/64/65/66 | IndustryBuying | 388 / 400 / 435 / 471 / 530 per 100 | 18% | Pack 100 (M6×10/12 MOQ 2 packs) | ≤30 d | ISO 4762 | https://www.industrybuying.com/socket-head-cap-screw-unbrako-FA.SC.SO4.208159 | 2026-09-24 | VERIFIED |
| M2.5×10 SHCS | Unbrako 104164 | IndustryBuying | 3,303 (ex 2,799) per 500 | 18% | Pack 500, **MOQ 3 packs** | ≤30 d | – | https://www.industrybuying.com/socket-head-cap-screw-unbrako-FAM257494 | 2026-09-24 | VERIFIED (MOQ makes it ₹9.9k) |
| M3×16 SHCS **12.9** | Caparo (full thread) | IndustryBuying | 896 (ex 759) per 200 → ₹4.48/pc | 18% | Pack 200 | ≤30 d | Grade 12.9 alloy | https://www.industrybuying.com/allen-cap-screw-caparo-FAM170624 | 2026-09-24 | VERIFIED |
| M3×18 SHCS **12.9** | TVS | Moglix | 5,747 (ex 4,864) per 1000 → ₹5.75/pc | 18% | Pack 1000, MOQ 2 | qty-available field = 0 → confirm | 12.9 | https://www.moglix.com/tvs-m3x18mm-socket-head-cap-screw-grade-129-pack-of-1000/mp/msnl5glgxdpyk4 | 2026-09-24 | VERIFIED listing / stock UNVERIFIED |
| M6×10 SHCS **12.9** | TVS | Moglix | 2,322 (ex 1,973) per 500 → ₹4.64/pc | 18% | Pack 500, MOQ 2 | qty 0 → confirm | 12.9 | https://www.moglix.com/tvs-m6x10mm-socket-head-cap-screw-grade-129-pack-of-500/mp/msnpkep782ld9g | 2026-09-24 | VERIFIED listing / stock UNVERIFIED |
| M4×10 SHCS | Generic carbon steel FACSM410 | IndustryBuying | 84 (ex 71) per 100 | 18% | Pack 100, MOQ 2 | In stock | carbon steel, grade n/s | https://www.industrybuying.com/allen-cap-screw-generic-FAM113225 | 2026-09-24 | VERIFIED |
| M3×8 / M4×10 / M5×10 SHCS | Zhongfa "Alloy Steel Black-Oxide Socket Head" | thinkrobotics.com | 64.99 / 99.99 / 169.99 per 10 | displayed | Pack 10 | Available | alloy steel black oxide | https://thinkrobotics.com/products/alloy-steel-black-oxide-socket-head-screws-pack-of-10 | 2026-09-24 | VERIFIED (Shopify variant JSON) |
| M3×8 SHCS | Quartz SS202 | quartzcomponents.com | 35 per 10 | displayed | Pack 10 | Available | SS202, head Ø5.3 | https://quartzcomponents.com/products/m3-x-8mm-hex-allen-socket-head-screwpack-of-10 | 2026-09-24 | VERIFIED |
| M3×8 SHCS | Robokits SS304 | robokits.co.in | 13.00 /pc (MOQ 15) | not stated* | per pc | In stock | SS304 | https://robokits.co.in/robot-parts/nut-bolts-standoffs/allen-cap-socket-head-bolts/m3-x-8-mm-socket-head-cap-stainless-steel-304-bolt-moq-15-pcs | 2026-09-24 | VERIFIED |
| M3×10 button head | Rpi Ind | IndustryBuying | 424 (ex 359) per 100 | 18% | Pack 100 | ≤6 d | button head socket | https://www.industrybuying.com/allen-cap-screw-rpi-ind-FAM180456 | 2026-09-24 | VERIFIED |
| M3×8 button head A2 | TR Fastenings | IndustryBuying | 671 (ex 569) per 50 | 18% | Pack 50 | ≤20 d | A2 stainless, button head hex socket | https://www.industrybuying.com/self-tapping-screw-tr-fastenings-HAR.SEL.833449943 | 2026-09-24 | VERIFIED |
| M4×25 button head 10.9 | Zhongfa | thinkrobotics.com | 109.99 per 10 | displayed | Pack 10 | Available (many other sizes OOS) | class 10.9 | https://thinkrobotics.com/products/metric-alloy-steel-button-head-hex-drive-screws-class-10-9-alloy-steel | 2026-09-24 | VERIFIED |
| M4×8 countersunk | Rpi Ind CSK socket | IndustryBuying | 353 (ex 299) per 50 | 18% | Pack 50 | ≤4 d | countersunk hex socket (bright) | https://www.industrybuying.com/allen-cap-screw-rpi-ind-FAM180466 | 2026-09-24 | VERIFIED |
| M3×12 countersunk A2 | TR Fastenings | IndustryBuying | 695 (ex 589) per 50 | 18% | Pack 50 | ≤20 d | A2 CSK hex socket | https://www.industrybuying.com/special-screw-tr-fastenings-HAR.SPE.930902195 | 2026-09-24 | VERIFIED |

\*Robokits product pages show "GST Input Tax Credit @18 % of ₹X" where X = 18 % × displayed price (e.g. ₹315 item → ₹56.7), which suggests displayed prices may be **ex-GST**; confirm at checkout.

### 2b. Nuts, washers

| Item | Brand/Model | Supplier | Price ₹ (incl GST) | GST | Qty | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| M4 nyloc | TR Fastenings N5ST-Z | IndustryBuying | 188 (ex 159) per 100 | 18% | Pack 100 | ≤20 d | steel, zinc plated | https://www.industrybuying.com/lock-nut-tr-fastenings-HAR.LOC.830907894 | 2026-09-24 | VERIFIED |
| M3/M4/M5 nyloc A4 | TR Fastenings | IndustryBuying | 494 / 589 / 565 per 50 | 18% | Pack 50 | ≤20 d | stainless A4 | https://www.industrybuying.com/lock-nut-tr-fastenings-HAR.LOC.730908003 | 2026-09-24 | VERIFIED |
| M3 / M4 nyloc SS | Unbrako 5010922 / 5010923 (ISO 10511) | IndustryBuying | 211 / 188 per 100 | 18% | Pack 100, **MOQ 100 packs** (PDP price = ₹21,100 / ₹18,800) | ≤30 d | stainless | https://www.industrybuying.com/nyloc-nut-unbrako-FAS.NYL.72502243 | 2026-09-24 | VERIFIED — not practical (MOQ) |
| M3 nyloc SS304 | Robokits | robokits.co.in | 2.00 /pc, MOQ 25 | not stated* | per pc | In stock | SS304 | https://robokits.co.in/robot-parts/nut-bolts-standoffs/nuts/m3-nyloc-nuts-304-stainless-steel-moq-25-pcs | 2026-09-24 | VERIFIED |
| M3 / M4 / M5 hex nut A2 | Unbrako 5001319 / 5001320 / 5001321 | IndustryBuying | 66 / 81 / 97 per 100 | 18% | Pack 100, MOQ 4 / 3 / 2 packs | ≤30 d | SS304 A2 | https://www.industrybuying.com/hex-nut-unbrako-FA.NU.HE0.593413 | 2026-09-24 | VERIFIED |
| M3 hex nut SS304 | Robokits | robokits.co.in | 1.00 /pc, MOQ 50 | not stated* | per pc | In stock (M4: OOS) | SS304 | https://robokits.co.in/robot-parts/nut-bolts-standoffs/nuts/m3-nuts-304-stainless-steel-moq-50-pcs | 2026-09-24 | VERIFIED |
| M5 flange nut (serrated) | TR Fastenings SFST-Z | IndustryBuying | 294 (ex 249) per 100 | 18% | Pack 100 | ≤20 d | steel BZP | https://www.industrybuying.com/nuts-tr-fastenings-HAN.NUT.333455048 | 2026-09-24 | VERIFIED |
| M5 flange nut SS304 | Astro (Robokits) | robokits.co.in | 11.50 /pc, MOQ 10 | not stated* | per pc | In stock | SS304 | https://robokits.co.in/mechanical-parts/aluminium-profile-accessories/astro-m5-flange-nuts-304-stainless-steel-moq-10-pcs | 2026-09-24 | VERIFIED |
| M3 spring washer | Unbrako 5001420 | IndustryBuying | 85 (ex 72) per 100 | 18% | Pack 100 | ≤30 d | spring (flat section) | https://www.industrybuying.com/plain-washer-unbrako-FA.WA6.335313 | 2026-09-24 | VERIFIED |
| M3 flat washer | Tanish SS202 1 mm | IndustryBuying | 78 (ex 66) per 100 | 18% | Pack 100, MOQ 3 | ≤30 d | SS202 | https://www.industrybuying.com/plain-washer-tanish-enterprises-FAM285751 | 2026-09-24 | VERIFIED |
| M3 / M4 / M5 flat washer SS304 | Robokits | robokits.co.in | 2.40 / 3.20 / 4.80 per pc, MOQ 50 | not stated* | per pc | In stock | SS304 | https://robokits.co.in/robot-parts/nut-bolts-standoffs/washers/m3-flat-washer-304-stainless-steel-moq-50-pcs | 2026-09-24 | VERIFIED |
| M3 / M4 flat washer | Quartz "Flat SS Washer" | quartzcomponents.com | 2 /pc | displayed | 1 | Available | SS | https://quartzcomponents.com/products/m3-zinc-plated-steel-washer | 2026-09-24 | VERIFIED |

### 2c. Pins, set screws, circlips, shoulder bolts

| Item | Brand/Model | Supplier | Price ₹ (incl GST) | GST | Qty | Stock / lead | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| Dowel 3×14 / 3×20 | CE solid dowel pin | IndustryBuying | 471 / 589 per 100 | 18% | Pack 100 | ≤3–4 d | solid steel dowel (tolerance not stated) | https://www.industrybuying.com/dowel-pin-ce-FAM239553 | 2026-09-24 | VERIFIED |
| Dowel 4×14 / 4×20 | CE | IndustryBuying | 518 / 624 per 100 | 18% | Pack 100 | ≤4 d | – | https://www.industrybuying.com/dowel-pin-ce-FAM239546 | 2026-09-24 | VERIFIED |
| Dowel 5×14 / 5×20 | CE | IndustryBuying | 565 / 719 per 100 | 18% | Pack 100 | ≤3–4 d | – | https://www.industrybuying.com/dowel-pin-ce-FAM239553 | 2026-09-24 | VERIFIED |
| Dowel 3×40 hardened | Unbrako 402124 | IndustryBuying | 601 per 40 | 18% | Pack 40, **MOQ 10 packs** | ≤30 d | high-grade alloy (hardened) | https://www.industrybuying.com/dowel-pin-unbrako-FAM257317 | 2026-09-24 | VERIFIED (MOQ ₹6k) |
| Dowel 3×10 / 4×10 / 5×10 | Zhongfa alloy steel | thinkrobotics.com | 149.99 / 179.99 / 239.99 per 10 | displayed | Pack 10 | Available | alloy steel | https://thinkrobotics.com/products/dowel-pins-assembly-pins | 2026-09-24 | VERIFIED |
| Grub M3×3 | Immech (bright) | IndustryBuying | 100 (ex 85) per 10 | 18% | Pack 10, MOQ 5 | ≤5 d | hex socket set screw | https://www.industrybuying.com/grub-screw-immech-FAM203248 | 2026-09-24 | VERIFIED |
| Grub M4×4 | Rpi Shop | IndustryBuying | 188 (ex 159) per 25 | 18% | Pack 25, MOQ 2 | ≤4 d | – | https://www.industrybuying.com/grub-screw-rpi-shop-FAM205622 | 2026-09-24 | VERIFIED |
| Set screw M3×10 cup | TVS knurled cup point | Moglix | 303 (ex 255) per 100 | 18% | Pack 100, MOQ 2 | qty 0 → confirm | TVS | https://www.moglix.com/tvs-10-mm-metric-series-m3-knurled-cup-point-socket-set-screw-pack-of-100/mp/msn2km1dz43x9v | 2026-09-24 | VERIFIED listing |
| Set screw M3×6 / M4×5 cup | Zhongfa | thinkrobotics.com | 34.99 / 29.99 per 5 | displayed | Pack 5 | Available | alloy steel | https://thinkrobotics.com/products/metric-alloy-steel-cup-point-set-screws | 2026-09-24 | VERIFIED |
| E-clip 4 mm | Qualfast | IndustryBuying | 129 (ex 109) per 100 | 18% | Pack 100, MOQ 3 | ≤2 d | carbon steel (standard not stated) | https://www.industrybuying.com/e-clips-qualfast-FAS.ECL.66551590 | 2026-09-24 | VERIFIED |
| E-clip 5 mm | Qualfast | IndustryBuying | 164 (ex 139) per 100 | 18% | Pack 100, MOQ 2 | ≤90 d | – | https://www.industrybuying.com/e-clips-qualfast-FAS.ECL.76551601 | 2026-09-24 | VERIFIED |
| Internal circlip 8/10/12 mm | Qualfast | IndustryBuying | 105 / 140 / 140 per 50 | 18% | Pack 50 (MOQ 5/1/2) | ≤90 d (10 mm: n/s) | internal circlip (standard not stated) | https://www.industrybuying.com/internal-circlip-qualfast-FAS.CIR.96551431 | 2026-09-24 | VERIFIED |
| External circlip 18 mm | Qualfast | IndustryBuying | 152 (ex 129) per 25 | 18% | Pack 25, MOQ 2 | ≤2 d | external circlip (standard not stated) | https://www.industrybuying.com/external-circlip-qualfast-FAS.CIR.36551363 | 2026-09-24 | VERIFIED |
| Circlip kit 890 pcs | RS PRO 523165 | IndustryBuying | 11,091 | 18% | kit | ≤20 d | E/int/ext 1.7–12 mm | https://www.industrybuying.com/circlip-pliers-rs-pro-HAN.CIR.520659764 | 2026-09-24 | VERIFIED (poor value) |
| Shoulder bolts | – | IB / Moglix / Shopify stores | **not found** (only Makita spare-part shoulder bolts) | – | – | – | – | – | 2026-09-24 | NOT FOUND → use dowel + SHCS or turned bushings |

### 2d. Threaded inserts for printed parts, kits

| Item | Brand/Model | Supplier | Price ₹ | GST | Qty | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| M3 heat-set L8 | Quartz "M3x8x4.2mm Brass Heat Set" | quartzcomponents.com | **33 per 10** | displayed | Pack 10 | Available | knurled brass; title = M3 × 8 L × 4.2 OD (listing text inconsistent — confirm dims) | https://quartzcomponents.com/products/m3-x-8mm-brass-heat-set-threaded-round-insert-nut-10-pcs | 2026-09-24 | VERIFIED (price) |
| M3 heat-set L4 / L6 / L10 / L12 | Quartz | quartzcomponents.com | 43 / 58 / 70 / 65 per 10 | displayed | Pack 10 | Available | OD 4.2 | https://quartzcomponents.com/products/m3-x-4mm-brass-heat-set-threaded-round-insert-nut-10-pcs | 2026-09-24 | VERIFIED |
| M3 heat-set L15 OD5 | Quartz | quartzcomponents.com | 62 per 10 | displayed | Pack 10 | Available | – | https://quartzcomponents.com/products/m3-x-15mm-brass-heat-set-threaded-round-insert-nut-10-pcs | 2026-09-24 | VERIFIED |
| M2.5 / M3 / M4 / M5 heat-set | ThinkRobotics MEC8005 | thinkrobotics.com | 59.99 / 64.99 (**M3 OOS**) / 79.99 / 99.99 per 10 | displayed | Pack 10 | M2.5, M4, M5 available | knurled brass: M3×4.5, M4×5, M5×6 | https://thinkrobotics.com/products/brass-heat-set-inserts-for-plastic | 2026-09-24 | VERIFIED |
| M2×5 heat-set | Robokits | robokits.co.in | 2.52 /pc, MOQ 25 | not stated* | per pc | listed | brass | https://robokits.co.in/robot-parts/nut-bolts-standoffs/nuts/m2-x-5-mm-brass-heat-threaded-round-insert-nut-moq-25-pcs | 2026-09-24 | VERIFIED |
| M3 industrial insert | SI IUB-M3-1 (brass, OD 4.37) | IndustryBuying | 109 (ex 92) **each** | 18% | 1, MOQ 5 | ≤45 d | brass threaded insert (install type not stated) | https://www.industrybuying.com/mounting-accessories-si-IND.MOU.635734646 | 2026-09-24 | VERIFIED (≈30× Quartz price) |
| Heat-insert tip set M2–M6 | amiciTools | IndustryBuying | 778 (ex 659) | 18% | set | ≤5 d | soldering-iron tips | https://www.industrybuying.com/soldering-kits-amicitools-WEL.SOL.640810027 | 2026-09-24 | VERIFIED |
| M4 Phillips assortment 180 pcs | Quartz KIT-QC4841 | quartzcomponents.com | 298 | displayed | 180 pcs | Available | M4 6–25 mm pan head | https://quartzcomponents.com/products/bolts-and-nuts-kit-m3-copy | 2026-09-24 | VERIFIED |

**Fastener takeaways:** For bulk socket-head screws use **Unbrako packs of 100 on IB (₹2.1–5.3/pc; 30-day lead)** — the one PDP checked (M3×8, 5000731) is **A2-70 stainless**, not 12.9. For true **12.9 alloy**: Caparo M3×16 (₹4.5/pc, pack 200) or TVS packs of 500–1000 on Moglix (stock unconfirmed). For fast small quantities: ThinkRobotics/Quartz packs of 10 (₹3.5–17/pc). Heat-set inserts: **Quartz ₹3.3–7/pc** is the cheapest seen; ThinkRobotics M3 OOS today.

## 3. SHAFTS, BAR/PLATE STOCK, CARBON FIBRE

### 3a. Ground / hard-chrome shafts (linear rods) and D-shafts

| Item | Brand/Model | Supplier | Price ₹ | GST | Qty | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| Ø5 × 1000 | Astro "Super Smooth Hard Chrome plated carbon steel rod" | robokits.co.in | 220 | not stated* | 1 | In stock | hard-chrome carbon steel (hardness not stated) | https://robokits.co.in/mechanical-parts/cnc-router-xyz-axis-part/astro-chrome-plated-steel-rods/astro-super-smooth-hard-chrome-plated-5mm-diameter-carbon-steel-rod-1000mm-long | 2026-09-24 | VERIFIED (listing) |
| Ø6 × 1000 | Astro hard chrome | robokits.co.in | 342 | not stated* | 1 | In stock | – | https://robokits.co.in/mechanical-parts/cnc-router-xyz-axis-part/astro-chrome-plated-steel-rods/astro-super-smooth-hard-chrome-plated-6mm-diameter-carbon-steel-rod-1000mm-long | 2026-09-24 | VERIFIED |
| Ø8 × 1000 | Astro hard chrome | robokits.co.in | 280 | not stated* | 1 | In stock | – | https://robokits.co.in/mechanical-parts/cnc-router-xyz-axis-part/astro-chrome-plated-steel-rods/astro-super-smooth-hard-chrome-plated-8mm-diameter-carbon-steel-rod-1000mm-long | 2026-09-24 | VERIFIED |
| Ø10 × 1000 | Astro hard chrome (RKI-6025) | robokits.co.in | 315 (MRP 415) | not stated* ("GST ITC @18 % of ₹56.7") | 1 | In stock | ESTIMATED ₹/kg: 0.617 kg/m (π/4·10²·7.85 g/cm³) → **≈ ₹511/kg** | https://robokits.co.in/mechanical-parts/cnc-router-xyz-axis-part/astro-chrome-plated-steel-rods/astro-super-smooth-hard-chrome-plated-10mm-diameter-carbon-steel-rod-1000mm-long | 2026-09-24 | VERIFIED (PDP) |
| Ø12 × 1000 | Astro hard chrome | robokits.co.in | 353 | not stated* | 1 | In stock | – | https://robokits.co.in/mechanical-parts/cnc-router-xyz-axis-part/astro-chrome-plated-steel-rods/astro-super-smooth-hard-chrome-plated-12mm-diameter-carbon-steel-rod-1000mm-long | 2026-09-24 | VERIFIED |
| Ø16 × 1000 | Astro hard chrome | robokits.co.in | 450 | not stated* | 1 | In stock | – | https://robokits.co.in/mechanical-parts/cnc-router-xyz-axis-part/astro-chrome-plated-steel-rods/astro-super-smooth-hard-chrome-plated-16mm-diameter-carbon-steel-rod-1000mm-long | 2026-09-24 | VERIFIED |
| Ø6 × 300 | "6mm Smooth Rod 300mm Stainless Steel Linear Shaft" | robocraze.com | 149 | incl | 1 | Available | SS | https://robocraze.com/products/6mm-smooth-rod-300mm-stainless-steel-linear-shaft | 2026-09-24 | VERIFIED |
| Ø8 × 500 | "500mm Chrome Plated Stainless Steel Smooth Rod 8mm" | robocraze.com | 279 | incl | 1 | Available | – | https://robocraze.com/products/500mm-smooth-rod | 2026-09-24 | VERIFIED |
| Ø10 × 400 | "Stainless Steel Smooth Rod Shaft 10 mm x 400 mm" | robocraze.com | 324 | incl | 1 | Available | SS | https://robocraze.com/products/stainless-steel-smooth-rod-shaft-10-mm-x-400-mm | 2026-09-24 | VERIFIED |
| Ø8 / Ø12 × 4000 | "Linear Bearing … C45/GCr15/SUS440C Hard Chrome Plated Rod" | Moglix | 5,321 / 8,388 (ex 5,066 / 7,987) | tax field 18 % but incl/ex ratio = 1.05 (listing inconsistent) | 4 m bar, **MOQ 20** | qty 0 | hard-chrome | https://www.moglix.com/linear-bearing-8mm-4000mm-c45gcr15sus440c-hard-chrome-plated-rod/mp/msne5n81zdq0kl | 2026-09-24 | VERIFIED listing — impractical MOQ |
| Ø15 / Ø20 induction-hardened | – | IB / Moglix / Robokits / Shopify stores | **not found** today (Robokits stops at Ø16) | – | – | – | – | – | 2026-09-24 | NOT FOUND → IndiaMART "hard chrome induction hardened rod" sellers (not fetched – IndiaMART rate-limited) |
| D-shaft | – | all checked stores | **not found** | – | – | – | – | – | 2026-09-24 | NOT FOUND → grind a flat on Astro rod, or order D-cut from CNC service |
| Steel parallel keys | – | IB (search returned only clamps) | **not found** | – | – | – | – | – | 2026-09-24 | NOT FOUND → buy key-steel bar locally / machine |

\* Robokits GST note: see §2a.

### 3b. Aluminium plate/bar, steel bar — ₹/kg (Hindalco / Jindal equivalents)

| Item | Brand/Grade | Supplier | Price ₹/kg | GST | MOQ | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 6061-T6 plate | "Rectangular Aluminium Plate 6061" (make: Hindalco/China/Russia) | IndiaMART — Maxal Impex, Mumbai | 365 /kg (listing) | ? | ? | ? | 0.7–300 mm, grades 6061/6082/7075 | https://dir.indiamart.com/impcat/aluminium-plate-6061.html | 2026-09-24 | UNVERIFIED (lead) |
| 6061-T6 plate | "Aluminium Plate 6061 T6" | IndiaMART — Maharashtra Metal (India), Mumbai | 382 /kg | ? | ? | ? | T6 | same | 2026-09-24 | UNVERIFIED |
| 6061-T6 plate | "ASTM B209 6061 Plate" 5 mm, 4'×8' | IndiaMART — Nenava Metal LLP, Mumbai | 300 /kg | ? | ? | ? | 5 mm T6 | same | 2026-09-24 | UNVERIFIED |
| 6061-T6 plate | "6061 Aluminium Alloy Plates" (cut sizes) | IndiaMART — Swagat Steel & Alloys, Mumbai | 301 /kg | ? | ? | ? | cut sizes offered | same | 2026-09-24 | UNVERIFIED |
| 6061-T6 plate | "Aluminum Alloy 6061 T6 Plate" | IndiaMART — Special Metals, Mumbai | 435 /kg | ? | ? | ? | ASTM B209 | same | 2026-09-24 | UNVERIFIED |
| 6061-T6 plate 6 mm | "Aluminium Plate 6061 T652" | IndiaMART — Vijay Prakash Aeromarine Metals, New Delhi | 552 /kg | ? | ? | ? | 6×1220×3000 | same | 2026-09-24 | UNVERIFIED |
| 6061-T651 thick plate | "Aluminium Plate 6061 T651" | IndiaMART — Solitaire Steel & Engg, Mumbai | 555 /kg | ? | ? | ? | 5–500 mm | same | 2026-09-24 | UNVERIFIED |
| **6061-T6 plate range** | 14 IndiaMART listings | – | **₹260 – ₹555 /kg; median ≈ ₹380–400 /kg** | ? | mill sizes (1220×2440 etc.) | – | – | same | 2026-09-24 | ESTIMATED from UNVERIFIED listings |
| Retail cut Al plate | Invento "300x300x5 mm … 1.3 kg" (alloy not stated) | IndustryBuying | 2,359 (ex 1,999) → **≈ ₹1,815/kg** (2,359 ÷ 1.3) | 18% | 1 pc | ≤6 d | 300×300×5 | https://www.industrybuying.com/plates-invento-IND.PLA.439471378 | 2026-09-24 | VERIFIED price / ESTIMATED ₹/kg |
| Retail cut Al plate | Invento 100×100×5 / 150×150×5 | IndustryBuying | 530 / 919 | 18% | 1 | ≤6 d | alloy n/s | https://www.industrybuying.com/plates-invento-FAM281047 | 2026-09-24 | VERIFIED |
| 6061 round rod 6–75 mm | "Round Aluminum Rod 6061" | IndiaMART — Mallinath Metal, Mumbai | 230 /kg (listing) | ? | ? | ? | 6061 | https://dir.indiamart.com/impcat/aluminium-round-bar.html | 2026-09-24 | UNVERIFIED (lead) |
| 6082 round bar (HE30) | "6082 Aluminium Round Bar" 25 mm / "12mm Aluminum 6082 T651 Round Rods" | IndiaMART — Solitaire Steel & Engg / Jagdish Metal, Mumbai | 300 /kg | ? | 6 m lengths | ? | 6082 (T651) | same | 2026-09-24 | UNVERIFIED |
| 6063 / HE9 rod | Special Metals (6063-T6) / Overseas Al (HE9 20 mm) / Grand Metal (6063) | IndiaMART, Mumbai | 425 / 325 / 200 /kg | ? | ? | ? | 6063 = softer extrusion alloy | same | 2026-09-24 | UNVERIFIED |
| **Al round bar range** | 12 IndiaMART listings | – | **₹200 – ₹425 /kg (6061/6082 ≈ ₹230–300)**; 2024 rod ₹650/kg | ? | – | – | – | same | 2026-09-24 | ESTIMATED from UNVERIFIED listings |
| 6061 round bar (other) | web-search snippets: "Aluminium Round Bar 6061 at ₹430/kg" (Ahmedabad), "6061 Aluminum Round Bar at ₹215/kg" (Mumbai) | IndiaMART | 215 – 430 /kg | ? | ? | ? | – | https://www.indiamart.com/proddetail/60mm-aluminium-round-rod-23924684712.html ; https://www.indiamart.com/proddetail/aluminum-round-6061-t6-bar-4454281948.html | 2026-09-24 | UNVERIFIED (snippets; pages not opened) |
| EN8 round bar | "En8 Round Steel Bars, 16mm" etc. | IndiaMART — Fortran Steel (Navi Mumbai), Maxell Steel, Dhand Steel … | 50 – 95 /kg (black/bright) | ? | often 1–2 t | ? | EN8 | https://dir.indiamart.com/impcat/en8-bright-bar.html | 2026-09-24 | UNVERIFIED |
| EN24 round bar | "EN24 Bright Round Bar" (Sunflag) / "EN-24 Round Bar" 12 mm / "EN24 Black Round Bars" | IndiaMART — K.R. Steel Udyog (Howrah) / Pramod Steel (Mumbai) / Steelloys India (Mumbai) | 91 / 140 / 55 /kg | ? | mill lengths 3–6 m | ? | EN24 (Ni-Cr-Mo) | https://dir.indiamart.com/impcat/en24-round-bar.html | 2026-09-24 | UNVERIFIED |
| **EN24 range** | 12 listings | – | **₹55 – ₹150 /kg** | ? | – | – | – | same | 2026-09-24 | ESTIMATED from UNVERIFIED |
| SS304 round bar | – | IB / Moglix / IndiaMART (rate-limited) | not captured | – | – | – | – | – | 2026-09-24 | NOT FOUND (IndiaMART likely; not fetched) |

### 3c. Carbon-fibre tubes & plates (limb tubes)

| Item | Brand/Model | Supplier | Price ₹ | GST | Qty | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| CF round tube 24×22×1000 (1.0 wall) | Shenzhen GDC "3K Twill Roll Wrapped CF Hollow Round Tube – Gloss" | thinkrobotics.com | **1,889.99** | displayed | 1 | Available | roll-wrapped 3K twill | https://thinkrobotics.com/products/high-quality-3k-twill-roll-wrapped-carbon-fibre-hollow-round-tube-gloss | 2026-09-24 | VERIFIED (Shopify product JSON; SKU MEC52.24.22.1000) |
| CF round tube 20×1.0×1000 | same | thinkrobotics.com | 1,619.99 | displayed | 1 | Available | – | same | 2026-09-24 | VERIFIED |
| CF round tube 28×1.0×1000 | same | thinkrobotics.com | 2,159.99 | displayed | 1 | Available | – | same | 2026-09-24 | VERIFIED |
| CF round tube 30×2.0×500 | same | thinkrobotics.com | 2,149.99 | displayed | 1 | Available | – | same | 2026-09-24 | VERIFIED |
| CF round tube 18×1.0×1000 / 12×1.5×1000 | same | thinkrobotics.com | 1,479.99 / 1,479.99 | displayed | 1 | Available | – | same | 2026-09-24 | VERIFIED (most 6–16 mm variants OOS today) |
| CF pultruded tube 20×16×1000 | Shenzhen GDC "Precision CF Pultruded Hollow Tube" | thinkrobotics.com | 3,399.99 | displayed | 1 | Available (all smaller sizes OOS) | pultruded | https://thinkrobotics.com/products/precision-carbon-fiber-pultruded-hollow-tube | 2026-09-24 | VERIFIED |
| CF plate 100×250×3 / 400×400×1 / 400×400×3 | Shenzhen GDC "3K Twill … CF Plate/Sheet" | thinkrobotics.com | 1,879.99 / 6,199.99 / 12,299.99 | displayed | 1 | Available | 3K twill | https://thinkrobotics.com/products/high-quality-3k-twill-roll-wrapped-carbon-fibre-plate-sheet | 2026-09-24 | VERIFIED |
| CF sheet 300×300×2 | "High-Strength Carbon Fiber Sheets" | IndiaMART — Nikol Advance Materials, Ahmedabad | 2,000 /sheet | ? | ? | ? | twill | https://dir.indiamart.com/impcat/carbon-fiber-sheet.html | 2026-09-24 | UNVERIFIED |
| CF sheet 350×350×3 | "Carbon Fiber Composites Polymer Sheet" | IndiaMART — Funique Composites, New Delhi | 2,499 /sheet | ? | ? | ? | for drones/robotics | same | 2026-09-24 | UNVERIFIED |
| CF sheet 500×500×2 | "2mm Carbon Fiber Sheet" | IndiaMART — Carbon Fiber Unique, New Delhi | 2,800 /sheet | ? | ? | ? | twill | same | 2026-09-24 | UNVERIFIED |
| CF sheet 300×300×1 | RS PRO 7648703 | IndustryBuying | 28,319 | 18% | 1 | ≤20 d | – | https://www.industrybuying.com/special-washer-rs-pro-FAS.FLA.820518005 | 2026-09-24 | VERIFIED (≈10× IndiaMART — avoid) |

ESTIMATED CF ₹/kg (ρ ≈ 1.55 g/cm³): tube 24×22×1000 → wall area π/4·(24²−22²) = 72.3 mm² → 72.3 cm³ → 0.112 kg → ₹1,890/0.112 ≈ **₹16,900/kg**; ThinkRobotics plate 400×400×1 → 160 cm³ → 0.248 kg → ≈ **₹25,000/kg**; IndiaMART Nikol 300×300×2 → 180 cm³ → 0.279 kg → ≈ **₹7,200/kg** (unverified).

---

## 4. TRANSMISSION PARTS

| Item | Brand/Model | Supplier | Price ₹ | GST | Qty | Stock / lead | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| GT2 open belt, 6 mm | "GT2 Timing Belt With Steel Cords 2mm Pitch – 1Meter" | robokits.co.in | 46 /m | not stated* | 1 m | In stock | steel cord | https://robokits.co.in/3d-printer/accessories/gt2-timing-belt-2mm-pitch-1meter | 2026-09-24 | VERIFIED |
| GT2 open belt 4 m | Invento ISC 021-2 | IndustryBuying | 931 (ex 789) → 233/m | 18% | 4 m | ≤6 d | 6 mm | https://www.industrybuying.com/timing-belt-invento-FAM281141 | 2026-09-24 | VERIFIED |
| GT2 closed loop 280 / 400 / 610 mm | Robokits | robokits.co.in | 82 / 142 / 107 | not stated* | 1 | In stock (200 mm OOS) | 6 mm | https://robokits.co.in/automation-control-cnc/gt-timing-wheels-pulley-and-belt/gt2-6mm-closed-timing-belt-280mm (400/610 mm: same path, -400mm / -610mm) | 2026-09-24 | VERIFIED |
| GT2 closed 280 mm | Quartz | quartzcomponents.com | 66 | displayed | 1 | Available | 6 mm | https://quartzcomponents.com/products/gt2-timing-belt-280mm-6mm-width-closed-loop-rubber-belt-for-3d-printer | 2026-09-24 | VERIFIED |
| GT2 pulley 20T idler / 40T / 60T / 80T | Robokits | robokits.co.in | 89 / 128 / 220 / 419 | not stated* | 1 | In stock | 5 mm bore (20T, 40T) | https://robokits.co.in/automation-control-cnc/gt-timing-wheels-pulley-and-belt/aluminum-gt2-timing-pulley-for-6mm-belt-40-tooth-5mm-bore ; …/gt2-synchronous-wheel-timing-pulley-60t ; …/gt2-synchronous-wheel-timing-pulley-80t ; https://robokits.co.in/robot-parts/belts-and-pulleys/aluminum-gt2-timing-idler-pulley-for-6mm-belt-20-tooth-5mm-bore | 2026-09-24 | VERIFIED |
| HTD 3M closed belts 6 mm | Contitech HTD 150-3M-06 … 216-3M-06 | IndustryBuying | 919 – 1,002 each | 18% | 1 | **≤120 d** | 3M, 6 mm | https://www.industrybuying.com/timing-belt-contitech-AUT.TIM.934183373 | 2026-09-24 | VERIFIED (slow, pricey) |
| HTD 5M closed belts | Contitech 225-5M-15 … 1500-5M-09 | IndustryBuying | 2,241 – 3,657 | 18% | 1 | ≤120 d | 5M | https://www.industrybuying.com/timing-belt-contitech-AUT.TIM.234183442 | 2026-09-24 | VERIFIED |
| HTD 5M pulleys | OPTIBELT 5M 9/15/25 mm | IndustryBuying | 3,539 – 4,011 | 18% | 1 | ≤120 d | steel | https://www.industrybuying.com/pulleys-optibelt-AUT.PUL.935154968 | 2026-09-24 | VERIFIED (→ print HTD pulleys instead) |
| Spur gear m0.5 (POM) | RS PRO 5217130 (48T, 5 bore) etc. | IndustryBuying | 648 – 848 each | 18% | 1, MOQ 2–4 | ≤20 d | POM, m0.5 | https://www.industrybuying.com/transmission-parts-rs-pro-AUT.TRA.320373225 | 2026-09-24 | VERIFIED |
| Spur gear m1.5 (printed plastic) | Invento ISC 2035-1 … | IndustryBuying | 294 – 636 | 18% | 1 | ≤6 d | 3D-printed, m1.5 | https://www.industrybuying.com/plastic-gears-invento-FAM280740 | 2026-09-24 | VERIFIED |
| Steel/brass m0.5–1 gears, ring gears | – | all checked stores | **not found** | – | – | – | – | – | 2026-09-24 | NOT FOUND → print (PA-CF) or CNC/hob via service |
| Rod end M5 (male/female, RH/LH) | N2K POS5 / POS5L / PHS5 / PHS5L | bearinghouse.in | **141.60** (ex 120) | 18% | 1 | In stock | 5 mm bore, M5 | https://bearinghouse.in/shop/n2k-pos5-rod-end-bearing/ | 2026-09-24 | VERIFIED |
| Rod end M6 / M8 | N2K POS6 / POS8, PHS6L / PHS8L | bearinghouse.in | 141.60 / 177.00 | 18% | 1 | In stock | – | https://bearinghouse.in/shop/n2k-pos6-rod-end-bearing/ | 2026-09-24 | VERIFIED |
| Rod end M5 (THK) | THK POS5 / BL5DA link ball | IndustryBuying | 1,769 / 1,533 | 18% | 1 | ≤19 d | genuine THK | https://www.industrybuying.com/rod-end-bearings-thk-BEA.ROD.638143236 | 2026-09-24 | VERIFIED (10× N2K) |
| Rod end M5 (IKO) | IKO PHSA5 | IndustryBuying | 1,887 | 18% | 1 | ≤19 d | die-cast female | https://www.industrybuying.com/special-bearing-iko-BEA.SPE.238949105 | 2026-09-24 | VERIFIED |
| M3/M4 ball links (RC type) | – | Robocraze / ThinkRobotics / Quartz / IB | **not found** | – | – | – | – | – | 2026-09-24 | NOT FOUND (robu.in not checked) |
| Linkage rod M4 / M5 (threaded, SS304) | Invento ISC 468 (M4×300) / ISC 469 (M5×300) | IndustryBuying | 577 / 600 per pack of 2 | 18% | 2 | ≤6 d | SS304 fully threaded | https://www.industrybuying.com/threaded-rod-invento-FAM104784 ; https://www.industrybuying.com/threaded-rod-invento-FAM104785 | 2026-09-24 | VERIFIED |
| Spherical plain bearing | FBJ GE12-2RS / N2K GE15ES-2RS / N2K GE17 / GE20 | bearinghouse.in | 177.00 / 159.30 / 177.00 / 212.40 | 18% | 1 | In stock | for printed ankle-linkage rods | https://bearinghouse.in/shop/fbj-ge-12-spherical-plain-bearings/ | 2026-09-24 | VERIFIED |
| Ball & socket M5 | RS PRO 689394 | IndustryBuying | 3,185 per 4 | 18% | bag of 4 | ≤15 d | steel | https://www.industrybuying.com/socket-sets-rs-pro-HAN.SOC.820471105 | 2026-09-24 | VERIFIED (expensive) |
| Neodymium disc 8×2 / 8×5 / 10×10 | Quartz NdFeB (grade & magnetisation not stated) | quartzcomponents.com | 13 / 23 / 57 | displayed | 1 | Available | axial assumed — **confirm** | https://quartzcomponents.com/products/small-magnets-8mm-diameter | 2026-09-24 | VERIFIED (price) |
| AS5600 encoder module (check whether a diametric magnet is included) | Quartz | quartzcomponents.com | 122 | displayed | 1 | **Out of stock** | – | https://quartzcomponents.com/products/as5600-magnetic-angle-encoder-sensor-module | 2026-09-24 | VERIFIED |
| Diametric N52 6×2.5 | – | all checked stores | **not found** | – | – | – | – | – | 2026-09-24 | NOT FOUND (robu/AliExpress – other agent) |
| Arc magnets N35–N52 | – | all checked stores | **not found** | – | – | – | – | – | 2026-09-24 | NOT FOUND |
| Compression springs | STANDARD SS.37xx | IndustryBuying | 16 each (ex 15) | 5% | 1, **MOQ 100** | ≤3 d | spec only by code | https://www.industrybuying.com/compression-spring-standard-FAS.SPR.103168756 | 2026-09-24 | VERIFIED |
| Compression springs | RS PRO 751360 (15.7×2.75, 0.22 N/mm) etc. | IndustryBuying | 36 – 44 each | 5% | MOQ 10–20 | ≤20 d | alloy steel, rate given | https://www.industrybuying.com/compression-spring-rs-pro-FAS.COM.320948167 | 2026-09-24 | VERIFIED |
| Belt-tension spring Ø4.8 | Robokits | robokits.co.in | 3 each, MOQ 10 | not stated* | – | In stock | – | https://robokits.co.in/3d-printer/accessories/3d-printer-belt-tightening-spring-diameter-4.8mm-moq-10-pcs | 2026-09-24 | VERIFIED |

---

## 5. FILAMENTS (1.75 mm) — ₹/kg

Method: each store's own public JSON (WooCommerce Store API / public product feed, Shopify `products.json`/`.js`, Wix/BigCommerce/Next.js page data, JSON-LD) or product page, read 2026-09-24. Price/stock/GST wording = **VERIFIED**; every ₹/kg = **ESTIMATED** (price ÷ kg). "Assumed 1 kg" = weight not stated on page (Bambu standard spool). "Refill" = no spool. Bambu official resellers per bambulab.com dealer page (India): Hydrotech 3D Chennai, WOL3D, 3D Bazaar, Robu, Ideal3D, 3idea Technology. Spot re-checks done directly: Ideal3D PETG HF refill black ₹1,150 (avail), Numakers PETG-HS ₹599, WOL3D PAHT-CF ₹3,699 (0.5 kg) – ₹6,299 (1 kg).

**GST note — Numakers India store (india.numakers.com):** page says "Taxes and shipping will be calculated at checkout"; the same spools sell at Ideal3D/Zbotic for ≈ 1.18× (₹707, ₹708, ₹825, ₹1,356) → Numakers direct prices are treated as **ex-GST** (≈ incl. figure = × 1.18, ESTIMATED). WOL3D pages are Cloudflare-blocked (data came from its public product feed) → GST wording not visible.

| Material | Exact product title | Brand | Supplier | Price ₹ | GST | Net kg | ₹/kg (EST.) | Stock | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|---|
| PETG | PETG-HS Filament (1.75 mm / 1 kg / Pitch Black) | Numakers | india.numakers.com (maker) | 599 | ex (see note) | 1 | 599 (≈ 707 incl.) | Black in stock | https://india.numakers.com/products/petg-hs-filament | 2026-09-24 | VERIFIED |
| PETG | Numakers PETG-HS Filament 1.75 mm 1 KG | Numakers | Ideal3D (Bambu reseller) | 707 | incl. ("Tax included.") | 1 | 707 | Pitch Black in stock | https://ideal3d.in/products/numakers-petg-high-speed-filament-1-75-mm-1-kg-copy-1 | 2026-09-24 | VERIFIED |
| PETG | 3D Printing Filaments PETG Pro 1kg, 1.75mm (Black) | generic | Quartz Components | 759 | not stated | 1 | 759 | "1 In Stock" | https://quartzcomponents.com/products/3d-printing-filaments-petg-pro-1kg-1-75mm-black | 2026-09-24 | VERIFIED |
| PETG | iSANMATE High Speed PETG Black | iSANMATE | 3D Master India | 799 (was 999) | not stated | 1 | 799 | In stock | https://3dmasterindia.in/product/isanmate-high-speed-petg-black/ | 2026-09-24 | VERIFIED |
| PETG | Brahma Lab Premium PETG 1.75mm – 1kg (black) | Brahma Lab (WOL3D house brand) | WOL3D | 800 | not stated | 1 | 800 | Black & white in stock | https://wol3d.com/product/brahma-lab-petg/ | 2026-09-24 | VERIFIED |
| PETG | PETG 3D Printer Filament 1.75mm 1Kg | Kingroon | Evelta | 814.20 | incl. (₹690 ex) | 1 | 814 | In stock | https://evelta.com/petg-3d-printer-filament-1-75mm-1kg/ | 2026-09-24 | VERIFIED |
| PETG | ELEGOO Rapid PETG Filament 1.75mm Black 1KG | Elegoo | 3D Master India | 849 | not stated | 1 | 849 | In stock | https://3dmasterindia.in/product/elegoo-rapid-petg-filament-1-75mm-black-1kg/ | 2026-09-24 | VERIFIED |
| PETG | FilamentX PETG – Black | FilamentX (3Ding house brand) | 3Ding | 999 | incl. ("Incl. of all taxes") | 1 | 999 | Black, 8 in stock | https://3ding.in/materials/filamentx-petg/ | 2026-09-24 | VERIFIED |
| PETG | eSun PETG – BASIC 1.75mm 1kg – Black | eSUN | Zbotic | 1,178.82 | incl. (₹999 + GST) | 1 | 1,179 | In stock | https://zbotic.in/product/esun-petg-1-75mm-3d-printing-filament-1kg-solid-black/ | 2026-09-24 | VERIFIED |
| PETG | Polymaker Polylite PETG 1.75MM 1KG | Polymaker | Ideal3D | 1,700 | incl. | 1 | 1,700 | Black in stock | https://ideal3d.in/products/polymaker-polylite-petg-1-75mm-filament-1kg | 2026-09-24 | VERIFIED |
| PETG HF (Bambu) | Bambu PETG HF – Without Bambu Reusable Spool | Bambu Lab | Ideal3D (official) | **1,150 (refill)** | incl. | assumed 1 | 1,150 | Black in stock | https://ideal3d.in/products/bambu-petg-hf-with-bambu-reusable-spool-copy | 2026-09-24 | VERIFIED (re-checked) |
| PETG HF (Bambu) | Bambu PETG HF – With Bambu Reusable Spool | Bambu Lab | Ideal3D (official) | 1,300 | incl. | assumed 1 | 1,300 | all 8 colours in stock | https://ideal3d.in/products/bambu-petg-hf-with-bambu-reusable-spool | 2026-09-24 | VERIFIED |
| PETG HF (Bambu) | Bambu PETG HF 1KG – With Bambu Reusable Spool | Bambu Lab | Hydrotech 3D Chennai (official) | 1,300 | incl. ("Taxes Included") | 1 | 1,300 | Black, 82 in stock | https://www.hydrotech3dchennai.com/product-page/bambu-petg-hf-1kg-with-bambu-reusable-spool | 2026-09-24 | VERIFIED |
| PETG HF (Bambu) | Bambu Lab PETG HF 3D Printer Filament 1.75mm | Bambu Lab | WOL3D (official) | 1,299 | not stated | assumed 1 | 1,299 | Black OOS; grey 3 left | https://wol3d.com/product/bambu-lab-petg-hf-3d-printer-filament-1-75mm/ | 2026-09-24 | VERIFIED |
| PETG Basic (Bambu) | Bambulab Petg basic with spool | Bambu Lab | Hydrotech (official) | 900 | incl. | assumed 1 | 900 | White 366 in stock; black 0 | https://www.hydrotech3dchennai.com/product-page/bambulab-petg-basic-with-spool | 2026-09-24 | VERIFIED |
| PETG-CF | PETG CF (1 kg / Black) | Numakers | india.numakers.com | **1,149** | ex (see note) | 1 | 1,149 (≈ 1,356 incl.) | Black in stock | https://india.numakers.com/products/petg-cf | 2026-09-24 | VERIFIED |
| PETG-CF | 3Idea PETG-CF (Carbon Fiber) Premium, Black, 1.75mm, Reusable Spool, 1kg | 3Idea (house brand) | 3Idea Technology | 1,349 | not stated (cart: "Taxes and shipping calculated at checkout") | 1 | 1,349 | In stock | https://www.3idea.in/product-detail/3idea-petg-cf-carbon-fiber-premium-3d-printing-filament-black-1-75mm-reusable-spool-net-weight-1kg | 2026-09-24 | VERIFIED |
| PETG-CF | Numakers Petg Cf Filament 1.75 mm 1 KG – Purple | Numakers | Ideal3D | 1,356 | incl. | 1 | 1,356 | Purple in stock (only colour) | https://ideal3d.in/products/numakers-petg-cf-filament-1-75-mm-1-kg-purple-1 | 2026-09-24 | VERIFIED |
| PETG-CF | PETG Carbon Fiber Filament 1.75mm | 3D MASTER | 3D Master India | 3,300 | not stated | 1 | 3,300 | In stock | https://3dmasterindia.in/product/petg-carbon-fiber-1-75mm/ | 2026-09-24 | VERIFIED |
| PETG-CF | "Esun ePETG - CF - Black" | eSUN | Ideal3D | 3,200 | incl. | not stated | n/a | In stock | https://ideal3d.in/products/corbon-fiber | 2026-09-24 | VERIFIED (weight unknown) |
| PETG-CF (Bambu) | Bambu PETG – CF – Black – With / Without Bambu Reusable Spool | Bambu Lab | Ideal3D (official) | 1,900 spool / 1,600 refill | incl. | assumed 1 | 1,900 / 1,600 | **Out of stock** | https://ideal3d.in/products/bambu-petg-cf-black-with-bambu-reusable-spool | 2026-09-24 | VERIFIED |
| PETG-CF (Bambu) | Bambu Lab PETG-CF 1.75mm (spool / without spool) | Bambu Lab | WOL3D (official) | 1,899 / 1,599 | not stated | assumed 1 | 1,899 / 1,599 | **Out of stock** (all colours) | https://wol3d.com/product/bambu-lab-petg-cf-3d-printer-filament-1-75mm/ | 2026-09-24 | VERIFIED |
| PAHT-CF (Bambu) | Bambu Lab PAHT – CF Black 3D Filament (Weight = 1kg) | Bambu Lab | WOL3D (official) | **6,299** (500 g: 3,699, OOS) | not stated | 1 | 6,299 | 10 in stock | https://wol3d.com/product/bambu-lab-paht-cf-black-3d-filament-500-gram/ | 2026-09-24 | VERIFIED (re-checked) |
| PAHT-CF (Bambu) | Bambu PAHT – CF – Black – With Bambu Reusable Spool – 1kg | Bambu Lab | Ideal3D (official) | 6,300 | incl. | 1 | 6,300 | Out of stock (Hydrotech ₹6,299 also OOS) | https://ideal3d.in/products/bambu-paht-cf-black-with-bambu-reusable-spool | 2026-09-24 | VERIFIED |
| PA6-CF (Bambu) | Bambu PA6-CF-Black – with Bambu Reusable Spool – 1 KG / 500 gm | Bambu Lab | Ideal3D (official) | 5,000 / 2,900 | incl. | 1 / 0.5 | 5,000 / 5,800 | **Out of stock** | https://ideal3d.in/products/bambu-pa6-cf-black-with-bambu-reusable-spool-500gm-copy | 2026-09-24 | VERIFIED |
| PA6-CF (Bambu) | Bambu Lab PA6-CF Filament 1.75mm (Black) | Bambu Lab | WOL3D (official) | 4,999 | not stated | assumed 1 | 4,999 | **Out of stock** | https://wol3d.com/product/bambu-lab-pa6-cf-filament-1-75mm-black/ | 2026-09-24 | VERIFIED |
| PA-CF | eSUN PA-CF 3D Printing Filament Black, 1.75mm, Net Weight-1kg | eSUN | 3Idea | **4,799** | not stated | 1 | 4,799 | In stock | https://www.3idea.in/product-detail/esun-pa-cf-3d-printing-filament-black-1-75mm-net-weight-1kg | 2026-09-24 | VERIFIED |
| PA-CF | 3Idea PA-CF Premium, Black, 1.75mm, 1kg | 3Idea | 3Idea | 4,999 | not stated | 1 | 4,999 | In stock | https://www.3idea.in/product-detail/3idea-pa-cf-premium-3d-printing-filament-black-1-75mm-net-weight-1kg | 2026-09-24 | VERIFIED |
| PAHT-CF | iSANMATE High-Temperature Industrial Grade PAHT Carbon Fiber Nylon Filament | iSANMATE | 3D Master India | 6,999 | not stated | 1 | 6,999 | In stock | https://3dmasterindia.in/product/isanmate-high-temperature-industrial-grade-paht-carbon-fiber-nylon-filament/ | 2026-09-24 | VERIFIED |
| PA6-CF | Brahma Lab Premium PA6-CF 1.75mm – Black – 1kg | Brahma Lab (WOL3D) | WOL3D | 4,099 | not stated | 1 | 4,099 | Out of stock | https://wol3d.com/product/brahma-lab-premium-pa6-cf/ | 2026-09-24 | VERIFIED |
| PA6-CF | iSANMATE Strong Durable PA6 Carbon Fiber Nylon Filament | iSANMATE | 3D Master India | 3,999 | not stated | 1 | 3,999 | Out of stock | https://3dmasterindia.in/product/isanmate-strong-durable-pa6-carbon-fiber-nylon-filament/ | 2026-09-24 | VERIFIED |
| PA12-CF | CARBONX Carbon Fibre Nylon – PA12 + CF15, 1.75 mm 500 g | 3DXTech | ThinkRobotics | 9,499.99 | not stated | 0.5 | 18,999.98 | 1.75 mm OOS (2.85 mm in stock) | https://thinkrobotics.com/products/3dxtech-carbonx-pa12-cf | 2026-09-24 | VERIFIED |
| PLA | PLA (1.75 mm / 1 kg / Pitch Black) | Numakers | india.numakers.com | 565 | ex (see note) | 1 | 565 (≈ 667 incl.) | Black in stock | https://india.numakers.com/products/pla | 2026-09-24 | VERIFIED |
| PLA+ | PLA+ Filament (with Spool / 1 kg / Pitch Black) | Numakers | india.numakers.com | 600 (refill 580; 3 kg 1,800) | ex (see note) | 1 | 600 (≈ 708 incl.) | spool in stock; refill OOS | https://india.numakers.com/products/pla-filament | 2026-09-24 | VERIFIED |
| PLA | FilamentX PLA – Black | FilamentX (3Ding) | 3Ding | 799 | incl. | 1 | 799 | Black, 21 in stock | https://3ding.in/materials/filamentx-pla/ | 2026-09-24 | VERIFIED |
| PLA Basic | eSun PLA-Basic 1.75mm 1kg Black | eSUN | Robocraze | 919 | incl. ("Incl. GST") | 1 | 919 | In stock (3Idea also ₹919) | https://robocraze.com/products/esun-pla-basic-1-75mm-1kg-3d-printing-filament-black-color | 2026-09-24 | VERIFIED |
| PLA+ | eSUN 1.75mm PLA+ Black – 1kg | eSUN | Robocraze | 1,349 | incl. | 1 | 1,349 | In stock (Thingbits ₹1,349.92, 3Idea ₹1,349) | https://robocraze.com/products/esun-pla-3d-printing-filament-1-75mm-black-color | 2026-09-24 | VERIFIED |
| PLA Basic (Bambu) | Bambu Lab PLA Basic – Black, Refill 1KG | Bambu Lab | 3Idea (official) | 1,149 | not stated | 1 | 1,149 | In stock | https://www.3idea.in/product-detail/bambu-lab-pla-basic-3d-printing-filament-black-refill-1kg | 2026-09-24 | VERIFIED |
| PLA Basic (Bambu) | Bambu PLA Basic – Without Bambu Reusable Spool | Bambu Lab | Ideal3D (official) | 1,150 | incl. | assumed 1 | 1,150 | Black in stock | https://ideal3d.in/products/bambu-pla-basic-with-bambu-reusable-spool-copy | 2026-09-24 | VERIFIED |
| PLA Basic (Bambu) | Bambu Lab PLA Basic 3D Filament (Without Spool) | Bambu Lab | WOL3D (official) | 1,199 | not stated | assumed 1 | 1,199 | Black in stock | https://wol3d.com/product/bambu-lab-pla-basic-without-spool/ | 2026-09-24 | VERIFIED |
| PLA Basic (Bambu) | Bambu Lab Pla Basic with reusable spool 1kg | Bambu Lab | Hydrotech (official) | 1,299 | incl. | 1 | 1,299 | Black, 272 in stock | https://www.hydrotech3dchennai.com/product-page/bambu-lab-pla-basic-with-reusable-spool-1kg | 2026-09-24 | VERIFIED |
| TPU 95A | ELEGOO TPU 3D Filament 1.75mm Black 1KG ("Material: TPU 95A") | Elegoo | 3D Master India | **1,399** | not stated | 1 | 1,399 | In stock | https://3dmasterindia.in/product/elegoo-tpu-3d-filament-1-75mm-black-1kg/ | 2026-09-24 | VERIFIED |
| TPU 95A | TPU 3D Printer Filament 1.75mm 1Kg ("95A hardness") | Kingroon | Evelta | 1,462.07 | incl. (₹1,239.04 ex) | 1 | 1,462 | In stock | https://evelta.com/tpu-3d-printer-filament-1-75mm-1kg/ | 2026-09-24 | VERIFIED |
| TPU 95A | Brahma Lab TPU95A 3D Printer Filament | Brahma Lab (WOL3D) | WOL3D | 1,599 pink / 1,649 other | not stated | not stated | n/a | Black OOS; pink 19, yellow 25 | https://wol3d.com/product/brahma-lab-tpu95a-3d-printer-filament/ | 2026-09-24 | VERIFIED (weight unknown) |
| TPU 95A | eSUN TPU-95A 1.75mm 1Kg – Clear | eSUN | Zbotic | 2,122.82 | incl. | 1 | 2,123 | In stock | https://zbotic.in/product/esun-tpu-95a-1-75mm-3d-printing-filament-1kg-clear/ | 2026-09-24 | VERIFIED |
| TPU 95A HF (Bambu) | Bambu Lab TPU 95A HF 1.75mm | Bambu Lab | WOL3D (official) | 3,299 | not stated | assumed 1 | 3,299 | Black OOS; grey 3 left | https://wol3d.com/product/bambu-lab-tpu-95a-hf-1-75mm-3d-filament/ | 2026-09-24 | VERIFIED |
| TPU 95A HF (Bambu) | Bambu TPU 95A HF – with Bambu Reusable Spool | Bambu Lab | Ideal3D (official) | 3,300 | incl. | assumed 1 | 3,300 | Black OOS; white in stock | https://ideal3d.in/products/bambu-tpu-95a-hf-with-bambu-reusable-spool | 2026-09-24 | VERIFIED |
| ASA | ASA Filament (1.75 mm / 1 kg) | Numakers | india.numakers.com | 699 | ex (see note) | 1 | 699 (≈ 825 incl.) | Black OOS; white/grey in stock | https://india.numakers.com/products/asa-filament | 2026-09-24 | VERIFIED |
| ASA | Numakers ASA Filament – Pitch Black – 1.75 mm / 1 kg | Numakers | Zbotic | 890.90 | incl. (₹755 + GST) | 1 | 891 | Black in stock | https://zbotic.in/product/numakers-asa-filament-pitch-black/ | 2026-09-24 | VERIFIED |
| ASA | iSANMATE ASA 3D Filament – Black | iSANMATE | 3D Master India | 899 | not stated | 1 | 899 | In stock | https://3dmasterindia.in/product/isanmate-asa-3d-filament-1-75mm-black/ | 2026-09-24 | VERIFIED |
| ASA | ELEGOO ASA Filament 1.75mm Black 1KG | Elegoo | 3D Master India | 999 | not stated | 1 | 999 | In stock | https://3dmasterindia.in/product/elegoo-asa-filament-1-75mm-black-1kg/ | 2026-09-24 | VERIFIED |
| ASA | 3Idea ASA Filament, 1.75mm, Black, Reusable Spool, 1kg/roll | 3Idea | 3Idea | 1,349 | not stated | 1 | 1,349 | In stock | https://www.3idea.in/product-detail/3idea-asa-filament-1-75mm-black-reusable-spool-1kg-roll | 2026-09-24 | VERIFIED |
| ASA | Polymaker Polylite ASA 1.75MM 1KG | Polymaker | Ideal3D | 2,700 | incl. | 1 | 2,700 | Black in stock | https://ideal3d.in/products/polymaker-polylite-asa-1-75mm-filament-1kg | 2026-09-24 | VERIFIED |
| ASA (Bambu) | Bambu Lab ASA 1.75mm | Bambu Lab | WOL3D (official) | 1,999 | not stated | assumed 1 | 1,999 | Black in stock (6 colours in stock) | https://wol3d.com/product/bambu-lab-asa-1-75mm-3d-printer-filament/ | 2026-09-24 | VERIFIED |
| ASA (Bambu) | Bambu ASA – With Bambu Reusable Spool | Bambu Lab | Ideal3D (official) | 2,000 | incl. | assumed 1 | 2,000 | Black OOS; red/green in stock (Hydrotech ₹1,999 OOS) | https://ideal3d.in/products/bambu-asa-with-bambu-reusable-spool | 2026-09-24 | VERIFIED |

**Bulk / multi-spool pricing seen (VERIFIED):** Numakers India (mix & match, ex-GST): PETG-HS ₹599 → ₹575 (13–24) → ₹549 (25+); PETG-CF ₹1,149 → ₹1,125 (13+) → ₹1,099 (25+); ASA ₹699 → ₹675 → ₹649; PLA ₹565 → ₹540 → ₹515; PLA+ ₹600 → ₹575 → ₹550; PLA+ 3 kg ₹1,800 → ₹1,725 (4–7) → ₹1,650 (8+); >50 spools: contact. Ideal3D: Numakers PETG-HS ₹707 → ₹678 (13–24) → ₹648 (25+); JAMG HE PETG 5 kg ₹4,250 (₹850/kg). Hydrotech: "Buy 4+ rolls of bambulab filament get 10% off". Thingbits house PETG ₹885 → ₹831.90 (4–9) → ₹814.20 (10–24). Robocraze / ThinkRobotics / Evelta: bulk by quote only.

**Best ₹/kg per material (ESTIMATED from VERIFIED prices):**

| Material | Cheapest credible, in stock | Cheapest official Bambu reseller | Note for JX1 |
|---|---|---|---|
| PETG | Numakers PETG-HS ₹599 ex-GST (≈ ₹707 incl.; ₹549 ex at 25+) / ₹707 incl. at Ideal3D | PETG HF refill **₹1,150** (Ideal3D, black in stock); spool ₹1,300 (Ideal3D / Hydrotech 82 black); PETG Basic ₹900 (Hydrotech, white only) | bulk structural parts |
| PETG-CF | Numakers PETG-CF ₹1,149 ex-GST (≈ ₹1,356 incl.); 3Idea house PETG-CF ₹1,349 | **Out of stock at all readable resellers**; listed ₹1,599–1,600 refill / ₹1,899–1,900 spool | stiff brackets; stock risk on Bambu |
| Nylon-CF (PA-CF / PA6-CF / PAHT-CF) | eSUN PA-CF **₹4,799** (3Idea, in stock); 3Idea PA-CF ₹4,999 | PAHT-CF **₹6,299** (WOL3D, 10 in stock); PA6-CF ₹4,999–5,000 listed but OOS | joint housings / gear parts; needs dry box + hardened nozzle |
| PLA / PLA+ | Numakers PLA ₹565 / PLA+ ₹600 ex-GST (≈ ₹667 / ₹708 incl.); FilamentX PLA ₹799 incl. | PLA Basic refill ₹1,149 (3Idea) / ₹1,150 (Ideal3D); spool ₹1,299 (Hydrotech) | jigs, fit-checks |
| TPU 95A | Elegoo TPU 95A **₹1,399** (3D Master India); Kingroon ₹1,462 incl. (Evelta) | TPU 95A HF ₹3,299 (WOL3D grey) / ₹3,300 (Ideal3D white); black OOS | foot pads, bumpers |
| ASA | Numakers ASA ₹699 ex-GST (≈ ₹825 incl., white/grey); black: Numakers ₹890.90 incl. (Zbotic) / iSANMATE ₹899 | ASA ₹1,999 (WOL3D, black in stock) | outdoor/UV covers |

**Unreadable / limited filament stores:** 3dbazaar.in (official Bambu reseller) — Cloudflare bot check on all pages (not bypassed); wol3d.com product pages 403 (public product feed used instead); thingbits.in Bambu listing is JS-only (only eSUN PLA+ and house PLA/PETG readable; not on Bambu dealer page); printrix.in 403 / printrix.co.in placeholder; solidspace.co.in live but 0 products (only Solid Space listing seen: PETG Orange at 3Idea ₹1,199, OOS); numakers.com = US store (USD) → used india.numakers.com; creality.in parked (Sedo); esun3d.in, sunlu.in, polymaker.in do not resolve; Robocraze = PLA/PLA+ only; KSP Electronics = Bambu PLA Basic only (₹1,299 black spool incl. GST, in stock; not on Bambu dealer list); Makerbazar no relevant 1.75 mm stock; robu.in / amazon.in / flipkart skipped (out of scope).

---

## 6. MANUFACTURING SERVICES (pricing models, example rates)

Scope/method: provider pages read on 2026-09-24 (curl/WebFetch). **No accounts, no uploads, no quote/contact forms submitted.** The two PCB prices were read from the providers' own public price calculators (the same request the page makes when size/qty is changed; no login, no upload, no enquiry, no cart). USD→INR conversions use ₹95.65/USD (open.er-api.com, updated 23 Sep 2026). Prices are **ex-GST** unless stated.

### 6a. CNC machining / turning

| Provider | URL | Services | Pricing model | MOQ | Lead time | Example rates / prices | Evidence | Notes |
|---|---|---|---|---|---|---|---|---|
| Makenica | https://makenica.com/cnc-machining-service-online/ | 3/5-axis milling; Al 6061-T6/6082/7075; steels 1018/1045/304/316; plastics | Instant online quote (needs sign-in + CAD upload — not used) | 1 part | "less than 5 days" | FAQ example: "CNC machining → INR 7000 for 1 part" (part not described); same FAQ: 3D printing ₹4,500, urethane casting ₹4,000 per part | VERIFIED (page text re-checked) | Finishes: anodise Type II/III, bead blast, powder coat, alodine, electroless Ni, black oxide; tolerance ±0.25 % (≥ ±0.25 mm) |
| Robocon CNC (Pune) | https://roboconcnc.com/prototype-cnc-machining | 3/4/5-axis milling, turning, mill-turn; Al 6061/6082/7075/2024 | Manual quote within 24 h | 1 pc | 5–7 business days (3-day express on request) | Their blog quotes *general Indian export-shop* rates: 3-axis $20–38/h, 5-axis $38–65/h, turning $18–32/h → ≈ ₹1,913–3,635/h, ₹3,635–6,217/h, ₹1,722–3,061/h | VERIFIED (blog text) / ₹ ESTIMATED | In-house anodising Type II (7–25 µm) & Type III (25–75 µm), priced in the quote |
| Amuse3D | https://amuse3d.in/cnc-machining-services | CNC, MJF, injection moulding | Instant quote after CAD upload (not used) | – | domestic 3–7 d | none public | VERIFIED | – |
| Manufyn (Pune) | https://manufyn.com | 3/4/5-axis CNC, turning, EDM, sheet metal, laser | Manual quote ("24hr Quote Response") | no fixed MOQ | CNC prototypes 3–7 business days | none public | VERIFIED | – |
| Custiv | https://custiv.com | CNC, laser cutting, bending, casting, forging | Upload/email RFQ (rfq@custiv.com); "Price Match Guarantee" | – | – | FabFlow blog claims ₹700–1,000 per Al bracket | model VERIFIED; price UNVERIFIED | – |
| Karkhana.io | https://karkhana.io/mechanical-solutions/ | now mainly electronics mfg; CNC secondary | "Get a Quote" form (not submitted) | "no rigid MOQ… engage when there's a clear intent to scale" | – | FabFlow blog claims ₹800–1,200/part (qty 10, 10–15 d) | MOQ text VERIFIED; price UNVERIFIED | poor fit for 1–20 pcs |
| FabFlow | https://fabflow.app | marketplace of local shops (CNC, printing, laser, sheet metal, PCB) | shops quote; buyer pays no platform fee | 1 (own blog) | 5–8 d (own blog) | own blog claims ₹450–800 per Al bracket | model VERIFIED; numbers UNVERIFIED (self-published comparison, 2026-08-12) | – |
| Think3D / Venttup / Zetwerk | https://think3d.in/placeorder/ · https://venttup.com · https://zetwerk.com | CNC / contract mfg | quote forms only (not submitted); Think3D says reply in 2–4 h | Zetwerk = volume | – | – | VERIFIED | – |
| Amazon Manufacturing Central | https://sell.amazon.in/grow-your-business/amazon-global-selling/manufacturing-central | directory of manufacturers | needs Seller Central login; request form only | set by maker | – | – | VERIFIED | not a CNC service |
| JLCCNC (China, import reference) | https://jlcpcb.com | CNC 3/4/5-axis, turning | instant quote | – | "3-day build" | "From $5.00" (≈ ₹478) + intl shipping + Indian duty | VERIFIED (headline) | – |
| IndiaMART CNC/VMC job-work | https://dir.indiamart.com/impcat/cnc-machining-services.html | local job shops | "Get Best Price" only | – | – | no prices published | VERIFIED (no prices) | – |
| Names that did not check out | – | Zeal 3D = Melbourne (AU); WeProtoType = San Diego (US); Chiselon = Hyderabad software co.; "Protoplant"/"Protoshop" = no Indian service found; nexgenprototype.com = 3D printing quote form, no CNC | – | – | – | – | UNVERIFIED (directory/search results) | – |

### 6b. Laser cutting, sheet-metal bending

| Provider | URL | Services | Pricing model | MOQ | Lead time | Example rates | Evidence | Notes |
|---|---|---|---|---|---|---|---|---|
| (no Indian instant-quote laser service found) | cutter.in | – | – | – | – | – | VERIFIED: cutter.in and lasercut.in are for sale; lasercutindia.com parked | – |
| Manufyn | https://manufyn.com | sheet metal, laser cutting, bending, welding | manual quote (24 h) | no fixed MOQ | 5–10 business days | – | VERIFIED | – |
| Custiv / FabFlow | https://custiv.com · https://fabflow.app | laser, bending / local laser shops | manual RFQ / marketplace quotes | – | – | – | VERIFIED | – |
| IndiaMART metal fibre-laser shops | https://dir.indiamart.com/impcat/laser-cutting-services.html ; …/metal-laser-cutting-service.html | MS, SS, Al | ₹/sq ft, ₹/piece or ₹/kg | varies | one listing: 3 days | mostly **₹40–500 /sq ft** (outliers ₹10 and ₹3,500); **₹150–200 /kg** | UNVERIFIED | unclear whether "sq ft" = sheet or part area |
| IndiaMART acrylic CO₂-laser shops | https://dir.indiamart.com/impcat/acrylic-cutting-service.html | acrylic | ₹/min or ₹/sq ft | – | one listing: 1 day | **₹6–10 /min**; ₹7–250 /sq ft | UNVERIFIED | – |
| IndiaMART CNC bending | https://dir.indiamart.com/impcat/cnc-bending-services.html | press-brake bending | "Get Best Price" only | – | – | none published | VERIFIED (no prices) | – |

### 6c. Anodising / powder coating (job-work)

| Provider | URL | Pricing model | Example rates | Evidence | Notes |
|---|---|---|---|---|---|
| IndiaMART anodising shops | https://dir.indiamart.com/impcat/anodizing-services.html ; …/aluminium-anodizing-services.html | mostly ₹/sq inch; some ₹/kg | Type II: ₹0.25–2.76 /in² (≈ ₹3.9–42.8 /dm²); hard anodise ₹0.08–4 /in² (≈ ₹1.2–62 /dm²); also ₹80–310 /kg; one listing needs 1 t | UNVERIFIED; ₹/dm² ESTIMATED (1 dm² = 15.5 in²) | minimum batch charges not shown — expect a lot charge for prototype quantities |
| IndiaMART powder-coating shops | https://dir.indiamart.com/impcat/powder-coating-services.html | ₹/sq ft, ₹/kg, ₹/piece | ₹12–40 /ft² (≈ ₹1.3–4.3 /dm²); ₹30–65 /kg; ₹60–120 /piece | UNVERIFIED; conversion ESTIMATED (1 ft² = 9.29 dm²) | – |
| Robocon CNC / Makenica | (see 6a) | included in part quote | not published | VERIFIED (offered) | Robocon also offers PTFE-impregnated hard anodise |

### 6d. 3D-printing services (prices before 18 % GST)

| Provider | URL | Processes / materials | Pricing model | Minimum | Lead time | Example rates / prices | Evidence | Notes |
|---|---|---|---|---|---|---|---|---|
| **iamRapid** (Bengaluru / Delhi / Pune) | https://iamrapid.com/pricing/ | FDM PLA/ABS/PETG/ASA/nylon/TPU/CF-PETG/CF-PLA; SLA; SLS PA2200 & PA12-GF30; MJF PA12 | public price estimator (no upload); exact quote needs CAD upload | 1–50 pcs ("Basic" plan) | FDM 2 d; SLA 2–3 d; SLS/MJF 3–5 d | page text: "FDM PLA … ₹6/gram", SLA ₹30–40 /cm³, SLS/MJF ₹32–40 /cm³ (re-checked). Sample 83 cm³ part: PLA ₹820; PETG ₹1,734 (102.1 g); nylon ₹3,315 (124.5 g); CF-PETG ₹4,519 (107.9 g). Sample 94 cm³: SLS PA2200 ₹3,760, MJF PA12 ₹3,760 | VERIFIED | ESTIMATED ₹/g: PETG ≈ 17.0 (1,734/102.1), nylon ≈ 26.6, CF-PETG ≈ 41.9, PLA ≈ 8.0 (with part minimums); SLS/MJF ≈ ₹40 /cm³ (3,760/94) |
| 3Ding (Chennai) | https://3ding.in/print/ | FDM PLA/ABS/PETG/TPU; resin; SLS PA12/PA11; MJF PA12; metal | instant quote after upload (not used) | per-part minimum: FDM ₹200, resin ₹1,000, SLS ₹2,000, MJF ₹2,000; metal manual | 1–5 business days | shipping ₹150 below ₹1,500 order, free above; GST 18 % | VERIFIED | FDM max 310×330×310 mm; no nylon/CF FDM |
| Makenica | https://makenica.com | FDM PLA/ABS/PETG/TPU/PC/"CF blends"; SLA; SLS; MJF PA12/PA11 | instant quote tool (sign-in + upload — not used) | no MOQ | prototypes 1–3 business days | indicative: FDM small parts ₹300–1,200; SLA ₹800–3,000; SLS/MJF ₹1,200–4,000 per part | VERIFIED (their indicative ranges) | – |
| Amuse3D | https://amuse3d.in/mjf-3d-printing-service | MJF PA12, FDM, SLA | instant quote after upload (not used) | – | MJF 3–5 d; express 24 h dispatch | none public | VERIFIED | – |
| Think3D / Imaginarium / Protomont / NexGen3D | https://think3d.in/placeorder/ · https://imaginarium.io · https://protomont.com · https://nexgen3d.in | various (Protomont lists nylon, CF, PEEK, ULTEM) | forms/contact only | – | NexGen3D 24–72 h; Think3D replies 2–4 h | – | VERIFIED | – |
| 3dprintservice.in | https://3dprintservice.in/shop/fdm-3d-printing-services/ | FDM | shop page | – | – | "Starting at just ₹1 per gram" (material unspecified) | VERIFIED as their claim (low confidence) | – |
| JLC3DP (China, import reference) | https://jlcpcb.com | SLA, MJF, SLS, FDM, metal | instant quote | – | "2-day build" | "From $0.30" (≈ ₹29) + shipping + duty | VERIFIED (headline) | – |
| Not checked / not applicable | – | WOL3D print service (blocked automated access), 3dprintinindia.com (blocked), Zeal 3D (Australian), "Imagineering" (imagineering.in parked), Protoplant (not found), Robu (skipped) | – | – | – | – | – | – |

### 6e. PCB fabrication & assembly (reference board: 100×100 mm, 2-layer FR4 1.6 mm, HASL, green)

| Provider | URL | Pricing model | MOQ | Lead time | Example price | Evidence | Notes |
|---|---|---|---|---|---|---|---|
| **Lion Circuits** | https://lioncircuits.com/quote | public calculator (no login); ordering needs Gerber + login | 5 pcs | 5 days (ship by 29 Sep 2026); custom specs 8 d | **5 pcs ₹1,877** (≈ ₹2,215 incl 18 % GST, ESTIMATED); 10 pcs ₹3,203; 50×40 mm ×5 ₹835; custom-spec 5 pcs ₹4,501 incl ₹2,200 setup; standard shipping ₹0 (express ₹300) | VERIFIED (calculator) | homepage headline "5 Boards for Just ₹799" vs FAQ "INR 799… for 10 units" — the two pages disagree |
| PCB Power | https://pcbpower.com/page/pcb-fabrication | "Calculated Price" on page | – | 7 working days default (3–25 selectable) | **5 pcs ₹1,042 each = ₹5,210** (≈ ₹6,148 incl GST, ESTIMATED); 10 pcs ₹764 each = ₹7,640; setup & E-test free; freight ₹0 | VERIFIED (calculator) | assembly price needs BOM upload (not done) |
| JLCPCB (China, import reference) | https://jlcpcb.com | instant quote | 5 pcs | 24 h build; 2–7 business-day delivery | homepage "From $2.00 / 5 pcs" (≈ ₹191) | VERIFIED (headline) | JLCPCB news (22 Aug 2026): $2 deal now only in the JLCONE desktop app; JLCPCB lists India's duty-free limit as "0 USD" and requires ID/KYC — shipping & duty to India **not verified** |

**Services takeaways:** (1) **PCBs → Lion Circuits** (₹1,877 + GST for 5 boards, ~5 d, no import duty/KYC). (2) **Outsourced prints → iamRapid** (published per-material examples: PETG ≈ ₹17/g, CF-PETG ≈ ₹42/g, MJF/SLS PA12 ≈ ₹40/cm³, 2–5 d), 3Ding as fallback (₹200/part FDM minimum). Neither offers PA-CF FDM → print PA-CF in-house on the P1S. (3) **CNC aluminium → Makenica (instant quote, <5 d) or Robocon CNC (manual quote, in-house anodise)** — no per-part prices published; Makenica's FAQ anchor is ₹7,000 for "1 part". (4) **Laser-cut plates** → no verified online price; send DXFs to Manufyn/Custiv or a local fibre-laser shop (IndiaMART ₹40–500/sq ft, unverified).

---

## 7. FEET / CONTACT, CABLE MANAGEMENT, SMALL PARTS

| Item | Brand/Model | Supplier | Price ₹ | GST | Qty | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| Rubber anti-skid mat 4 mm (cut into foot pads) | Forgesy 4mm Rubber Anti Skid Yoga Mat | Moglix | 548 (ex 464) | 18% | 1 mat | qty 10 | rubber, 4 mm | https://www.moglix.com/forgesy-4-mm-rubber-anti-skid-yoga-mat/mp/msn8kl2wp0rr5v | 2026-09-24 | VERIFIED listing (unconventional but cheap sole material) |
| TPE anti-skid mat 4 mm | Fairbizps | Moglix | 246 (ex 208) | 18% | 1 mat | qty 42 | TPE | https://www.moglix.com/fairbizps-4mm-tpe-blue-anti-skid-yoga-mat/mp/msn19z2ey8n353 | 2026-09-24 | VERIFIED listing |
| NBR rubber sheet 3 mm 300×300 | MonotaRO NBR3x300x300 | IndustryBuying | 1,084 (ex 919) | 18% | 1 | ≤19 d | nitrile | https://www.industrybuying.com/esd-rubber-mats-accessories-monotaro-SAF.ESD.938081276 | 2026-09-24 | VERIFIED |
| Natural rubber strip 3×100×1000 | MonotaRO MBL-100 | IndustryBuying | 990 (ex 839) | 18% | 1 | ≤19 d | NR | https://www.industrybuying.com/esd-rubber-mats-accessories-monotaro-SAF.ESD.238081913 | 2026-09-24 | VERIFIED |
| Adhesive rubber feet 13 mm sq | MCM 28-941 | IndustryBuying | 188 each | 18% | MOQ 7 | ≤20 d | – | https://www.industrybuying.com/feet-mcm-HAR.FEE.932324740 | 2026-09-24 | VERIFIED (pricey) |
| Rubber bumpers | KEYSTONE 722/724/728 | IndustryBuying | 107 – 140 each | 18% | MOQ 6–10 | ≤15 d | recessed round | https://www.industrybuying.com/industrial-automation-accessories-keystone-IND.IND.832201531 | 2026-09-24 | VERIFIED (→ print TPU bumpers instead) |
| TPU 95A feet pads | print in-house | – | see filament table §5 | – | – | – | – | – | – | – |
| Neoprene / PU sheet | – | IB / Moglix | not found (search noise only) | – | – | – | – | – | 2026-09-24 | NOT FOUND |
| O-ring kit | KESARIA NBR 3–25 mm, 36 / 90 pcs | IndustryBuying | 353 / 435 | 18% | MOQ 5 kits | ≤4 d | NBR metric | https://www.industrybuying.com/seal-rings-kesaria-BEA.SEA.144461813 | 2026-09-24 | VERIFIED |
| Drag chain 10×10, 1 m | Robokits "Cable Drag Chain Wire Carrier with end connectors" | robokits.co.in | 215 | not stated* | 1 m | In stock | 10×10 inner | https://robokits.co.in/3d-printer/accessories/cable-drag-chain-wire-carrier-with-end-connectors-10x10mm-1meter | 2026-09-24 | VERIFIED |
| Drag chain 15×20 / 25×38 / 18×50, 1 m | Robokits | robokits.co.in | 356 / 623 / 941 | not stated* | 1 m | In stock (10×20 OOS) | – | https://robokits.co.in/3d-printer/accessories/cable-drag-chain-wire-carrier-with-end-connectors-15x20mm-1meter | 2026-09-24 | VERIFIED |
| Drag chain 18×25, 1 m | Dehmy | Moglix | 1,059 (ex 897) | 18% | 1 m | qty 20 | heavy duty | https://www.moglix.com/dehmy-1m-18x25mm-black-heavy-duty-cnc-cable-drag-chain/mp/msne5n8m1vxykl | 2026-09-24 | VERIFIED listing |
| Cable ties 100 mm, black UV | Rpi Ind | IndustryBuying | 81 per 100 | 18% | **MOQ 35 packs** | ≤2 d | – | https://www.industrybuying.com/cable-ties-rpi-ind-FAM190542 | 2026-09-24 | VERIFIED (MOQ) |
| Cable ties 100×2.5 | TJIKKO | IndustryBuying | 235 per 100 | 18% | MOQ 5 | ≤30 d | white | https://www.industrybuying.com/cable-ties-tjikko-FAM190667 | 2026-09-24 | VERIFIED |
| Cable ties 100 mm | HellermannTyton 111-01812 | IndustryBuying | 365 per 100 | 18% | 1 | ≤15 d | – | https://www.industrybuying.com/industrial-automation-accessories-hellermanntyton-IND.IND.231065737 | 2026-09-24 | VERIFIED |
| Spiral wrap 9 mm / 12 mm / 3 mm, 1 m | Quartz "PVC Spiral Wrapping Sleeve Band" (white) | quartzcomponents.com | 10 / 19 / 30 per m | displayed | 1 m | Available | PVC | https://quartzcomponents.com/products/9mm-white-spiral-wrapping-band-for-wires-1-meter ; https://quartzcomponents.com/products/spiral-12mm-1-2 | 2026-09-24 | VERIFIED |
| Cable ties 100×2.5 / 200×3.6 | Quartz nylon (pack 100) | quartzcomponents.com | 44 / 99 per 100 | displayed | 100 | Available | nylon | https://quartzcomponents.com/products/tie-100x2-2-100-pc-in-each | 2026-09-24 | VERIFIED (cheapest ties seen) |
| Heat-shrink 8–12 mm, 1 m | Quartz | quartzcomponents.com | 19 – 29 per m | displayed | 1 m | Available | – | https://quartzcomponents.com/products/10mm-transparent-industrial-grade-heat-shrink-sleeve-1-meter | 2026-09-24 | VERIFIED |

---

## 8. 2020 EXTRUSION, THREADED ROD, TEST/LIFT GANTRY

| Item | Brand/Model | Supplier | Price ₹ | GST | Qty | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 2020 profile 1 m | Astro "Industrial Duty Aluminium 2020H European Standard Anodized V-Slot Profile" (RKI-4480) | robokits.co.in | **341 /m** | not stated* (ITC 18 % of ₹61.38) | 1 m | In stock | anodised | https://robokits.co.in/mechanical-parts/aluminium-profile-accessories/astro-industrial-duty-aluminium-2020h-european-standard-anodized-v-slot-profile | 2026-09-24 | VERIFIED |
| 2020 V-slot 1 m black | Robokits | robokits.co.in | 414 | not stated* | 1 m | In stock | black anodised | https://robokits.co.in/robot-parts/aluminium-profile-accessories/black-anodized-aluminium-2020-v-slot-profile-1meter | 2026-09-24 | VERIFIED |
| 4040 T-slot 1 m | Astro RKI-4470 | robokits.co.in | 876 | not stated* | 1 m | **Pre-order** | heavy duty | https://robokits.co.in/mechanical-parts/aluminium-profile-accessories/astro-anodized-heavy-duty-industrial-grade-aluminium-4040-t-slot-profile | 2026-09-24 | VERIFIED |
| 3030H / 2080 | Astro | robokits.co.in | 720 / 900 | not stated* | 1 m | In stock | – | https://robokits.co.in/mechanical-parts/aluminium-profile-accessories/astro-industrial-duty-aluminium-3030h-european-standard-anodized-t-type-profile ; …/astro-heavy-duty-industrial-2080-european-standard-anodized-aluminium-t-type-profile | 2026-09-24 | VERIFIED |
| 2020 V-slot 500 mm | Generic | IndustryBuying | 660 | 18% | 1 | ≤10 d | – | https://www.industrybuying.com/handrail-generic-HAR.HAN.442529812 | 2026-09-24 | VERIFIED (2.5× Robokits per m) |
| T-nuts M3/M4/M5 for 2020 | Robokits T-type nut | robokits.co.in | 7.50 / 6.00 / 5.00 each (MOQ 10) | not stated* | – | M5 OOS | – | https://robokits.co.in/robot-parts/aluminium-profile-accessories/t-type-nut-m4-for-2020-aluminium-profile-moq-10pcs | 2026-09-24 | VERIFIED |
| Hammer T-nut M4/M5 (pack 10) | Robocraze | robocraze.com | 140 / 129 | incl | 10 | Available | – | https://robocraze.com/products/hammer-drop-in-t-nut-m5-10-6-t | 2026-09-24 | VERIFIED (WebFetch of store JSON) |
| 3-way inside corner 2020 | Robokits | robokits.co.in | 90 | not stated* | 1 | In stock | – | https://robokits.co.in/robot-parts/aluminium-profile-accessories/standard-3-way-inside-corner-brackets-connector-for-2020-profile | 2026-09-24 | VERIFIED |
| L-clamp 2020 (MOQ 4) | Robokits 1720 | robokits.co.in | 24 each | not stated* | – | In stock | – | https://robokits.co.in/robot-parts/aluminium-profile-accessories/l-shape-aluminium-clamp-with-straight-angle-for-2020-profile-moq-4pcs | 2026-09-24 | VERIFIED |
| SS304 threaded rod M6×300 (pack 2) | Invento ISC 470 | IndustryBuying | 624 | 18% | 2 | ≤6 d | SS304 | https://www.industrybuying.com/threaded-rod-invento-FAM104786 | 2026-09-24 | VERIFIED |
| SS304 threaded rod M8×100 (pack 2) | Invento ISC 1938 | IndustryBuying | 577 | 18% | 2 | ≤6 d | SS304 | https://www.industrybuying.com/threaded-rod-invento-FAM104807 | 2026-09-24 | VERIFIED |

**Test/lift gantry idea (ESTIMATED BOM, prices from rows above):** 2.0 m tall × 1.2 m wide "goalpost" with a 1.2 m base and outriggers, built from **Astro 4040**: uprights 2 × 2.0 m + top beam 1.2 m + base rails 2 × 1.2 m + outriggers 2 × 0.8 m = 4.0 + 1.2 + 2.4 + 1.6 = **9.2 m × ₹876 = ₹8,059** (or doubled **2020H**: 18.4 m × ₹341 = ₹6,274, noticeably less stiff). Add ~40 corner brackets / T-nuts / L-clamps (≈ 40 × ₹24–90 → ₹1,000–3,600) ⇒ **frame ≈ ₹9–12k** (Robokits prices may be ex-GST → +18 %), plus a ≥100 kg-rated pulley/rope or ratchet hoist and a torso harness with an inline load cell (**not priced here**). Verify 4040 stock (shown as pre-order today).

---

## 9. MATERIAL PRICE TABLE (₹/kg)

| Material / form | ₹/kg | Basis | Source(s) | Evidence |
|---|---|---|---|---|
| Al 6061-T6 plate (mill sizes) | **260 – 555 (median ≈ 380–400)** | 14 IndiaMART listings (Mumbai/Delhi stockists; Hindalco/imported make) | https://dir.indiamart.com/impcat/aluminium-plate-6061.html | UNVERIFIED listings → ESTIMATED range |
| Al 6061 / 6082 round bar | **230 – 300** (6063/HE9 200–425; 2024 ≈ 650) | 12 IndiaMART listings | https://dir.indiamart.com/impcat/aluminium-round-bar.html | UNVERIFIED → ESTIMATED range |
| Al plate, retail cut piece (alloy n/s) | **≈ 1,815** | Invento 300×300×5, 1.3 kg, ₹2,359 incl GST → 2,359 ÷ 1.3 | IndustryBuying | ESTIMATED from VERIFIED price |
| EN8 carbon steel bar | **50 – 95** | IndiaMART listings | https://dir.indiamart.com/impcat/en8-bright-bar.html | UNVERIFIED |
| EN24 alloy steel bar | **55 – 150** | IndiaMART listings | https://dir.indiamart.com/impcat/en24-round-bar.html | UNVERIFIED |
| Hard-chrome carbon-steel rod (linear shaft) Ø10 | **≈ 511** | Robokits ₹315 per 1 m; mass = π/4 × 1.0² cm² × 100 cm × 7.85 g/cm³ = 616.5 g | robokits.co.in | ESTIMATED from VERIFIED price |
| Hard-chrome rod Ø8 / Ø12 / Ø16 | **≈ 710 / 397 / 285** | ₹280 ÷ 0.395 kg; ₹353 ÷ 0.888 kg; ₹450 ÷ 1.579 kg (same formula) | robokits.co.in | ESTIMATED |
| CF roll-wrapped tube 24×22 mm | **≈ 16,900** | ₹1,889.99 ÷ 0.112 kg (72.3 cm³ × 1.55 g/cm³) | thinkrobotics.com | ESTIMATED |
| CF plate 3K 1 mm (400×400) | **≈ 25,000** | ₹6,199.99 ÷ 0.248 kg | thinkrobotics.com | ESTIMATED |
| CF sheet 2 mm (300×300), IndiaMART | **≈ 7,200** | ₹2,000 ÷ 0.279 kg | IndiaMART (Nikol) | ESTIMATED from UNVERIFIED |
| PETG filament | **≈ 707** (Numakers, incl. est.) – 1,150 (Bambu HF refill) – 1,700 (Polymaker) | 1 kg spool price ÷ 1 kg | §5 | ESTIMATED from VERIFIED |
| PETG-CF filament | **≈ 1,356** (Numakers) – 1,600/1,900 (Bambu, OOS) – 3,300 | ÷ 1 kg | §5 | ESTIMATED |
| PA-CF / PA6-CF / PAHT-CF filament | **4,799** (eSUN PA-CF) – 6,299 (Bambu PAHT-CF) – 6,999 (iSANMATE PAHT-CF); PA12-CF (3DXTech) ≈ 19,000 | ÷ kg | §5 | ESTIMATED |
| PLA / PLA+ filament | **≈ 667 / 708** (Numakers) – 1,149 (Bambu refill) | ÷ 1 kg | §5 | ESTIMATED |
| TPU 95A filament | **1,399** (Elegoo) – 2,123 (eSUN) – 3,300 (Bambu HF) | ÷ 1 kg | §5 | ESTIMATED |
| ASA filament | **≈ 825** (Numakers) – 1,999 (Bambu) – 2,700 (Polymaker) | ÷ 1 kg | §5 | ESTIMATED |

---

## 10. GAPS / NOT FOUND ON 2026-09-24 (need robu.in / import / local trade / phone quotes)

| Item | Status | Suggested next step |
|---|---|---|
| Crossed-roller RU42/RU66/CRBH3510 at low cost | only genuine IKO (₹11.8k–15.3k, IB) and unverified IndiaMART leads (₹4k–22.5k) | price Chinese RU/CRBH via import channel (other agent); or design around paired 68xx |
| Diametric N52 Ø6×2.5 encoder magnets; N35–N52 arc magnets | not in any checked store | robu.in / AliExpress (other agent) |
| M3/M4 RC-style ball links | not found; smallest found = M5 POS5/PHS5 (₹141.60) | robu.in / RC hobby shops; or use GE12/GE15 in printed rod ends |
| Ø15 / Ø20 hardened shafts, D-shafts | not found (Robokits max Ø16) | IndiaMART hard-chrome rod stockists (phone), or have a CNC shop grind flats |
| Shoulder bolts (ISO 7379) | not found | substitute dowel + SHCS, or turned bushings |
| SS304 round bar ₹/kg, neoprene/PU sheet | IndiaMART rate-limited after ~6 pages | re-query IndiaMART later / local stockist |
| HTD 3M/5M belts & pulleys at hobby prices | only Contitech/Optibelt (₹919+/₹3.5k+, 120-day lead) | print HTD pulleys (PA-CF), buy belts from robu/AliExpress |
| Steel/brass m0.5–1 spur & ring gears | not found | print PA-CF, or hob/CNC via service |
| Laser-cut aluminium plates with published price | no instant-quote Indian site found | send DXF to Manufyn/Custiv/local fibre-laser shops |

---

## 11. REPRODUCIBILITY (scratch scripts, not part of the deliverable)

Helper scripts used (in the session scratchpad `…\scratchpad\r6\`): `ib.py` (IndustryBuying search → ng-state JSON), `pdp.py` (IB product JSON-LD/specs), `mog.py` (Moglix ssr-pwa-state JSON), `shop.py` (Shopify suggest / product .js), `woo.py` (WooCommerce Store API), `rk.py` / `rkcat.py` (Robokits listing HTML), `im.py` (IndiaMART listing HTML), `ev.py` (Evelta listing). Raw outputs: `ib_*.txt`, `mog_*.txt`, `woo_*.txt`, `rk_*.txt`, `im_*.txt`, `shop_*.txt`. Filament and service sub-task working files: `…\r6\fil\`, `…\r6\svc\`.

<!-- END: all sections complete (2026-09-24) -->

