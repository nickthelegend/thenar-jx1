# JX1 — India mechanical sourcing & manufacturing: RAW research log

- **Project:** JX1 low-cost compact humanoid (~1.2 m, 25–30 kg), built in India. FDM (Bambu P1S class: PETG, PETG-CF, PA-CF) + CNC aluminium only where justified.
- **Research date:** 2026-09-24 (all "VERIFIED" rows were read from the live page/API on this date).
- **Method:** curl/Python against store pages & public JSON: IndustryBuying (search-page `ng-state` JSON, PDP JSON-LD), Moglix (`ssr-pwa-state` JSON), Shopify stores (`/search/suggest.json`, `/products/<handle>.js`), WooCommerce stores (`/wp-json/wc/store/products`), SKF India e-Marketplace (page title/meta), WebSearch/WebFetch for services. robu.in, amazon.in, element14, digikey **not** checked (out of scope — covered elsewhere).
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

### 1c. Angular-contact (7000 series) — for preloaded pairs (e.g. hip-yaw, wrist)

| Item | Brand/Model | Supplier | Price ₹ (incl GST) | GST | Qty | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 7001 | KOYO 7001 | IndustryBuying | 601 (ex 509) | 18% | 1 | In stock ≤3 d | 12×28×8, single row | https://www.industrybuying.com/angular-contact-ball-bearings-koyo-BEA.ANG.14120958 | 2026-09-24 | VERIFIED |
| 7001 | NTN 7001 | IndustryBuying | 612 (ex 519) | 18% | 1 | In stock ≤8 d | 12×28×8 | https://www.industrybuying.com/angular-contact-ball-bearings-ntn-PO.BE.AN.181059 | 2026-09-24 | VERIFIED |
| 7001 | NTN 7001 (Pack of 5) | Moglix | 2,677 /5 → 535/pc (ex 2,269) | 18% | 5 | MOQ 1 pack | 12×28×8, C 5.05 kN | https://www.moglix.com/ntn-12x28x8mm-single-angular-contact-ball-bearing-7001-pack-of-5/mp/msn4k6zjywp8kq | 2026-09-24 | VERIFIED |
| 7002 | KOYO 7002 | IndustryBuying | 695 (ex 589) | 18% | 1 | In stock ≤4 d | 15×32×9 | https://www.industrybuying.com/angular-contact-ball-bearings-koyo-BEA.ANG.14120965 | 2026-09-24 | VERIFIED |
| 7002 | NTN 7002 | IndustryBuying | 707 (ex 599) | 18% | 1 | In stock ≤8 d | 15×32×9 | https://www.industrybuying.com/angular-contact-ball-bearings-ntn-FAM168870 | 2026-09-24 | VERIFIED |
| 7000 | NSK 7000A | IndustryBuying | 1,769 (ex 1,499) | 18% | 1 | In stock ≤19 d | 10×26×8 | https://www.industrybuying.com/angular-contact-ball-bearings-nsk-BEA.ANG.238731051 | 2026-09-24 | VERIFIED |
| 7200 | SKF 7200 BEP | bearinghouse.in | 1,686.22 (ex 1,429) | 18% | 1 | In stock | 10×30×9 | https://bearinghouse.in/shop/skf-7200-bep-angular-contact-ball-bearing/ | 2026-09-24 | VERIFIED |

Note: No cheap generic 7000-series seen at bearinghouse/IB; KOYO/NTN 7001–7002 at ₹600–700 are the best value found. For thin preloaded pairs consider 2× 6800-series back-to-back with printed spacers instead (design option).

### 1d. Crossed-roller bearings (RU / RB / CRBH / CRBC)

| Item | Brand/Model | Supplier | Price ₹ | GST | Qty | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| CRBHV3510 | IKO CRBHV3510AC1 | IndustryBuying | 11,799 (ex 9,999) | 18% | 1 | "In stock", ships ≤19 d | 35×60×10 (IKO std), C = 7,900 N | https://www.industrybuying.com/special-bearing-iko-BEA.SPE.939191295 | 2026-09-24 | VERIFIED |
| CRB4010 | IKO CRB4010C1 | IndustryBuying | 15,339 (ex 12,999) | 18% | 1 | ≤19 d | 40×65×10, C = 5,980 N | https://www.industrybuying.com/special-bearing-iko-BEA.SPE.939192083 | 2026-09-24 | VERIFIED |
| CRB5013 | IKO CRB5013C1 | IndustryBuying | 15,339 (ex 12,999) | 18% | 1 | ≤19 d | 50×80×13, C = 14,200 N | https://www.industrybuying.com/special-bearing-iko-BEA.SPE.739192138 | 2026-09-24 | VERIFIED |
| RB3510 | "THK RB3510 UU" | IndiaMART seller (Ahmedabad, listing) | 4,200 /pc (listing) | ? | 1 | ? | 35×60×10 | https://dir.indiamart.com/impcat/crossed-roller-bearings.html | 2026-09-24 | UNVERIFIED (lead; authenticity unknown) |
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
| AXK3047 | KHK AXK 3047 needle thrust | bearinghouse.in | 118.00 (ex 100) | 18% | 1 | In stock | 30×47×2 (+washers separate) | https://bearinghouse.in/shop/khk-axk-3047-needle-thrust-bearings/ | 2026-09-24 | VERIFIED |
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
<!-- PROGRESS MARK: bearings done; fasteners next -->
