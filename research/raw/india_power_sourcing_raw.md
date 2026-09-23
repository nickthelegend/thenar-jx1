# JX1 power-system sourcing: India (raw research log)

- **Date of all checks:** 2026-09-24 (IST). Researcher: power-system sourcing agent (r5). Status: **complete first pass.**
- **Scope:** cells, packs, BMS, protection, DC-DC, connectors/wire/chargers, battery-safety consumables for JX1 (1.2 m, 25–30 kg, 20–24 BLDC joints, 24 V or 36–48 V bus, 150–400 W average, 1.5–3 kW peaks lasting under 1 s).
- Scratch data (raw JSONL dumps of every store query) is in the session scratchpad `…/scratchpad/r5/` (`results.jsonl`, `woo.jsonl`, `rk*.jsonl`, `oc*.jsonl`, `mog.jsonl`, `ib.jsonl`, `ev.jsonl`, `pages/`).

## 0. Evidence labels, GST basis, coverage

- **VERIFIED**: price and stock read on 2026-09-24 from the live product page, or from the store's own product API (Shopify `suggest.json` / `products/<h>.js`, WooCommerce Store API, JSON-LD on page), with the URL given.
- **ESTIMATED**: a derived number, with the math shown (incl-GST = ex-GST × 1.18; ₹/Wh = incl-GST price ÷ (V_nom × Ah)).
- **UNVERIFIED**: a lead only. This covers IndiaMART and search-engine snippets, prices hidden or shown as placeholders, and blocked stores.
- **GST basis by store** (checked on-site):
  - **robokits.co.in: EXCL GST.** The FAQ says "product price does not include taxes, handling & shipping charges", and product pages show "GST Input Tax Credit @ 18 %". For example, the ₹308 50S lists ITC ₹55.44 = 308 × 0.18.
  - **electronicscomp.com (EC): EXCL GST.** The price line reads "Rs.xxx (Excluding 18% GST)". The "(Inclusive of all Taxes)" figure on the same page is the MRP, not the selling price.
  - **lionbattery.in (LB): EXCL GST** ("Price Excluding Tax"). Its ex-GST figures are round incl-GST prices ÷ 1.18, e.g. 550.85 × 1.18 = 650.00.
  - **evelta.com: EXCL GST** (BigCommerce `price--withoutTax`).
  - **Incl GST:**
    - robocraze.com ("Incl. GST (No Hidden Charges)")
    - indianhobbycenter.com (IHC, "Taxes included")
    - moglix.com and industrybuying.com (IB): "(Incl. of all taxes)" with an ex + 18 % split shown
    - tanotis.com ("Includes all taxes … includes GST and import duties")
    - technobotix.in ("Price including GST")
    - indianrobostore.com (IRS, "(Inc GST)")
    - zbotic.in (shows "₹494.42 (₹419.00 + GST)")
  - **Not stated on product page ("n/s")**: quartzcomponents.com, thinkrobotics.com, kitsguru.com, thebatteryworld.in (TBW), batterysource.in. Indian B2C listings are normally GST-inclusive, but treat these as UNVERIFIED on tax.
- Li-ion cells and packs, BMS and electronics attract 18 % GST (Robokits cell pages show "GST ITC @ 18 %").
- **Not read:**
  - Skipped by instruction: robu.in, amazon.in, in.element14.com, digikey.in.
  - Blocked: tme.com/in (Cloudflare 403) and mouser.in ("Access denied" to automation). flyrobo.in returned 403.
  - probots.co.in: the Magento search redirects and was not parsed.
  - IndiaMART search is JS-rendered, so only snippet leads are included.
  - evelta.com search is fuzzy: it returned no Mean Well, contactors or ANL fuses, but did return JST-GH, TVS and capacitor parts.
- **WebSearch budget was exhausted mid-task.** Every later lead comes from each store's own on-site catalogue search, not a web search.

---

## TOP PICKS (best credible value, 2026-09-24)

| Need | Pick | Supplier | Price (incl GST) | ₹/Wh | Evidence |
|---|---|---|---|---|---|
| High-drain 21700 (cheapest credible) | Samsung INR21700-50S (5.0 Ah, 25 A / 45 A @80 °C cut) | Robokits | ₹363.44 (₹308 + GST) | 20.2 | VERIFIED, In Stock |
| High-drain 21700 (authorised channel) | Molicel INR-21700-P42A | The Battery World (authorised Molicel distributor) | ₹332.50 (GST n/s) | 22.0 (26.0 if +GST) | VERIFIED, In Stock |
| High-drain 21700 (best power) | Molicel P45B (45 A, DCR ≤13.8 mΩ) | Robokits | ₹481.44 (₹408 + GST) | 29.7 | VERIFIED, In Stock |
| High-drain 21700 (deep stock) | Molicel P45B | ElectronicsComp | ₹535.72 (₹454 + GST) | 33.1 | VERIFIED, 314 pcs |
| Budget 6S2P pack (low C) | DMEGC 6S2P 9 Ah 3C | lionbattery.in | ₹4,999 (₹4,236.44 + GST) | 25.0 | VERIFIED, 200 in stock |
| High-drain 6S2P pack | Crocks Pack Samsung 50S 6S2P 10 Ah 90 A | lionbattery.in | ₹8,500 (₹7,203.39 + GST) | 38.3 | VERIFIED, in stock |
| 6S LiPo 5–10 Ah | GenX 22.2 V 6S 10000 mAh 25C | IHC ₹10,319 / Robokits ₹9,088 + GST | ₹10,319 / ₹10,724 | 46.5 / 48.3 | VERIFIED, in stock |
| 13S 48 V pack (low C) | BAK 13S2P 48 V 10 Ah 3C | lionbattery.in | ₹10,560 (₹8,949.15 + GST) | 22.6 | VERIFIED, in stock |
| 13S smart BMS | JBD SP14S004 10–14S 40 A smart | lionbattery.in | ₹2,199 (₹1,863.56 + GST) | – | VERIFIED, 10 in stock |
| 6S/7S hardware BMS | Daly 6S 30 A / 7S 40 A waterproof | Quartz | ₹937 / ₹978 (GST n/s) | – | VERIFIED, available |
| E-stop 22 mm, twist-release | Schneider XB2BS8442C (40 mm, 1NC) | Moglix | ₹399 | – | VERIFIED, In stock |
| E-stop 1NO+1NC | Schneider XB5AS8445N (40 mm, trigger, turn-to-release) | Moglix | ₹789 | – | VERIFIED, In stock |
| MOSFET main switch | Flipsky Anti-Spark Switch Smart Enhanced 300A V2.0 (12–84 V, 100 A cont.) | technobotix.in | ₹7,499 | – | VERIFIED, In stock |
| 48 V → 5/12/19 V (non-isolated) | "48V 36V 24V to 19V 12V 9V 5V 3V" synchronous buck, 6.5–60 V in, 10 A | ElectronicsComp | ₹447.22 (₹379 + GST) | – | VERIFIED, 8 pcs |
| Isolated 48 V → 5 V (Jetson) | Mean Well DDR-60L-5 (5 V 10.8 A, 18–75 V in) | IndustryBuying | ₹4,247 | – | VERIFIED, "ships within 15 days" |
| Main connectors | Amass XT90-S pair (anti-spark) | Robokits | ₹212.40 (₹180 + GST) | – | VERIFIED, In Stock |

---

## 1. CELLS

### 1a. 21700 high-drain cells

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs (as listed) | ₹/Wh incl (EST) | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 21700 cell | Samsung INR21700-50S | Robokits | 308.00 (→363.44) | excl | In Stock | 5.0 Ah, 3.6 V, 25 A no temp cut / 45 A with 80 °C cut, ~72 g; reviewer measured 69 g, 9.97 mΩ @1 kHz | 20.19 | https://robokits.co.in/batteries-chargers/samsung-premium-li-ion-battery/3.7v-samsung-li-ion-batteries/samsung-21700-5000mah-inr21700-50s-45a-9c-li-ion-battery-original | 2026-09-24 | VERIFIED |
| 21700 cell | Samsung INR21700-50S (Original) | lionbattery.in | 550.85 (→650.00) | excl | 27 in stock | 5.0 Ah, 45 A, 70 g, "Genuine Samsung SDI" (seller claim) | 36.11 | https://lionbattery.in/shop/shop/lithium-cells/li-ion-cylindrical-battery-cell/samsung-inr21700-50s-3-6v-5000mah-45a-li-ion-battery-original/ | 2026-09-24 | VERIFIED |
| 21700 cell | Molicel INR-21700-P42A | The Battery World (**authorised Molicel distributor**) | 332.50 (reg 350) | n/s | In Stock (og:availability) | 4.2 Ah, "30–45 A" (listing), NCA | 21.99 (25.95 if +GST) | https://www.thebatteryworld.in/products/molicel-inr-21700-p42a-3-6v-4200mah | 2026-09-24 | VERIFIED |
| 21700 cell | Molicel P42A | Robokits | 356.00 (→420.08) | excl | In Stock | 4.2 Ah, 35 A (listing), 67 g; "graded and tested…testing marks" | 27.78 | https://robokits.co.in/batteries-chargers/li-ion-cells/3.6v-21700-li-ion-cell/molicel-3.6v-4200mah-11c-lithium-ion-battery-original-inr21700-p42a-original | 2026-09-24 | VERIFIED |
| 21700 cell | Molicel P42A | Indian Hobby Center | 449.00 | incl | Available | 4.2 Ah, 45 A, 70 g | 29.70 | https://indianhobbycenter.com/products/molicel-inr-21700-p42a-3-6v-4200mah-11c-li-ion-battery | 2026-09-24 | VERIFIED |
| 21700 cell | Molicel P42A | Indian Robo Store | 479 (MRP 699) | incl | **Pre-order** | 4.2 Ah 11C | 31.68 | https://indianrobostore.com/product/molicel-a-grade-inr-21700-p42a-36v-4200mah-11c-li-ion-battery | 2026-09-24 | VERIFIED |
| 21700 cell | Molicel P42A | ElectronicsComp (listing A) | 419.00 (→494.42) | excl | **Out of stock** | 4.2 Ah 11C | 32.70 | https://www.electronicscomp.com/molicel-inr-21700-p42a-36v-4200mah-11c-li-ion-battery | 2026-09-24 | VERIFIED |
| 21700 cell | Molicel P42A | ElectronicsComp (listing B) | 615.00 (→725.70) | excl | 839 pcs | 4.2 Ah 11C | 48.00 | https://www.electronicscomp.com/molicel-inr21700-p42a-4200mah-11c-lithium-ion-battery | 2026-09-24 | VERIFIED |
| 21700 cell | Molicel P42A | batterysource.in | 560 (1 pc) / 2,360 (5 pc = 472 ea) | n/s | in stock | 4.2 Ah 11C | 37.0 / 31.2 | https://batterysource.in/product/molicel-inr-21700-p42a-3-6v-4200mah-11c-li-ion-battery/ | 2026-09-24 | VERIFIED (Woo API variants) |
| 21700 cell | Molicel P42A | Zbotic | 494.42 (419 + GST) | incl | Out of stock | URL slug embeds "IS 16046 (Part 2) R-41137189" (BIS mark) | 32.70 | https://zbotic.in/product/sealed-secondary-portable-lithiumion-cell-is-16046-part-2-r-41137189-3-6v-4-2ah-15-1w-h/ | 2026-09-24 | VERIFIED |
| 21700 cell | Molicel P42A | olelectronics.in | 457 | n/s | Out of stock | – | 30.2 | https://olelectronics.in/product/molicel-agrade-inr-21700-p42a-3-6v4200mah/ | 2026-09-24 | VERIFIED |
| 21700 cell | Molicel INR-21700-P45B | Robokits | 408.00 (→481.44) | excl | In Stock | 4.5 Ah, 45 A, "22 % lower DCR than P42A", 3C charge | 29.72 | https://robokits.co.in/batteries-chargers/li-ion-cells/3.7v-21700-li-ion-cell/molicel-4500mah-10c-lithium-ion-battery-inr21700-p45b | 2026-09-24 | VERIFIED |
| 21700 cell | Molicel P45B | ElectronicsComp | 454.00 (→535.72) | excl | 314 pcs | 4.5 Ah 10C | 33.07 | https://www.electronicscomp.com/molicel-inr21700-p45b-4500mah-10c-lithium-ion-battery | 2026-09-24 | VERIFIED |
| 21700 cell | Molicel P45B | Indian Hobby Center | 599.00 | incl | Available | 4.5 Ah, 45 A, 70 g, 242 Wh/kg | 36.98 | https://indianhobbycenter.com/products/molicel-inr-21700-p45b-3-6v-4500mah-10c-li-ion-battery | 2026-09-24 | VERIFIED |
| 21700 cell | Molicel P45B | Zbotic / OL Electronics / ThingBits | 516 / 477 / 500 | incl / n/s / "…of GST" | all **Out of stock** | – | – | https://zbotic.in/product/molicel-a-grade-inr-21700-p45b-3-6v-4500mah-10c-li-ion-battery/ ; https://olelectronics.in/product/molicel-agrade-inr-21700-p45b3-6v4500mah/ ; https://www.thingbits.in/products/molicel-inr21700-p45b-3-6v-4500-mah-lithium-ion-rechargeable-battery | 2026-09-24 | VERIFIED |
| 21700 cell | Molicel INR-21700-P50B | Robokits | 583.00 (→687.94) | excl | In Stock | 5.0 Ah, 60 A (80 °C cut-off), ≤70 g, origin "Canada or Taiwan" | 38.22 | https://robokits.co.in/batteries-chargers/li-ion-cells/3.7v-21700-li-ion-cell/molicel-21700-p50b-5000mah-60a-lithium-ion-battery | 2026-09-24 | VERIFIED |
| 21700 cell | Molicel P50B | Indian Hobby Center | 849.00 | incl | Available | 5.0 Ah 12C (60 A) | 47.17 | https://indianhobbycenter.com/products/molicel-inr-21700-p50b-3-6v-5000mah-12c-li-ion-battery-60a | 2026-09-24 | VERIFIED |
| 21700 cell | Samsung INR21700-40T | ElectronicsComp | 879.00 (→1,037) | excl | 64 pcs | **Seller states it is a COPY**: "Brand Generic, Country of Origin China… marking them as a copy" | 72.0 | https://www.electronicscomp.com/samsung-inr21700-40t-4000mah-9c-li-ion-battery | 2026-09-24 | VERIFIED (counterfeit disclosed) |
| 21700 cell | Samsung 40T | olelectronics.in | 901 | n/s | Out of stock | – | – | https://olelectronics.in/product/samsung-inr21700-40t-4000mah/ | 2026-09-24 | VERIFIED |
| 21700 cell | Samsung 50E / 40T, LG M50LT | batterysource.in | "₹110" in schema = **placeholder**; page shows no price ("Request for Bulk Orders") | n/s | n/a | – | – | https://batterysource.in/product/samsung-inr21700-50e-3-6v-5000mah-li-ion-battery/ | 2026-09-24 | UNVERIFIED (RFQ) |
| 21700 cell | LG INR21700 M50LT (4.8 Ah 1C) | olelectronics.in | 553 | n/s | Out of stock | energy cell, not high drain | – | https://olelectronics.in/product/lg-inr21700-m50lt-3-6v-4800mah/ | 2026-09-24 | VERIFIED |
| 21700 cell | LG INR21700H40 / H30 | ElectronicsComp | 879 / 791 | excl | Out of stock | – | – | https://www.electronicscomp.com/lg-inr21700h40-4000mah-9c-li-ion-battery | 2026-09-24 | VERIFIED |
| 21700 cell | Samsung INR21700-50G (2C) | ElectronicsComp | 1,229 (→1,450) | excl | 45 pcs | energy cell, very expensive | 80.6 | https://www.electronicscomp.com/samsung-inr21700-50g-5000mah-2c-li-ion-battery | 2026-09-24 | VERIFIED |
| EVE 40PL/50E, BAK 45A/45D, Lishen, LG M58T | – | not found in readable Indian stores | – | – | – | – | – | – | 2026-09-24 | NOT FOUND |

### 1b. 21700 "budget/energy" cells (3C or less: not for peak power)

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | ₹/Wh incl (EST) | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 21700 | DMEGC INR21700-45E | ElectronicsComp | 233 (→274.94) | excl | 88 | 4.5 Ah, 3C | 16.97 | https://www.electronicscomp.com/dmegc-inr21700-45e-37v-4500mah-li-ion-battery | 2026-09-24 | VERIFIED |
| 21700 | DMEGC INR21700-45E "Original" | Quartz | 245 | n/s | available | 4.5 Ah, 3C, charge 1C | 15.12 (17.85 if +GST) | https://quartzcomponents.com/products/dmegc-inr-21700-li-ion-4500mah-3-7v-4500mah-rechargable-battery-original | 2026-09-24 | VERIFIED |
| 21700 | DMEGC 45E | lionbattery.in | 351.69 (→415) | excl | 200 in stock | 4.5 Ah | 25.62 | https://lionbattery.in/shop/shop/lithium-cells/li-ion-cylindrical-battery-cell/dmegc-inr18650-45e-3-7v-4500mah-li-ion-battery/ | 2026-09-24 | VERIFIED |
| 21700 | "CJ/Winway" 21700 "5000 mAh" | Quartz | 225 | n/s | available | **listing admits actual 4500 mAh, 1C** | 13.9 | https://quartzcomponents.com/products/21700-li-ion-3-7v-5000mah-3c-rechargeable-battery-winway | 2026-09-24 | VERIFIED (capacity inflated) |
| 21700 | BAK NMC 21700 5000 mAh 3C | ElectronicsComp | 448 (→528.64) | excl | 930 | 5 Ah 3C | 29.37 | https://www.electronicscomp.com/bak-nmc-21700-5000mah-3c-lithium-ion-36v-battery | 2026-09-24 | VERIFIED |
| 21700 | HEB ICR-21700 "6800 mAh" | ElectronicsComp | 489 | excl | 8 | **6.8 Ah in 21700 is not credible** (best commercial 21700s are about 5.8 Ah, e.g. LG M58T) | – | https://www.electronicscomp.com/heb-3.7v-6800mah-icr-21700-li-ion-high-energy-rechargeable-battery | 2026-09-24 | VERIFIED (**fake-capacity flag**) |

### 1c. 18650 cells

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | ₹/Wh incl (EST) | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 18650 | Molicel INR-18650-P30B | The Battery World (authorised) | 320 | n/s | "Fresh Stock Arrived" | 3.0 Ah | 29.6 (35.0 if +GST) | https://www.thebatteryworld.in/category/li-ion-rechargeable-batteries | 2026-09-24 | VERIFIED (category page) |
| 18650 | Molicel P30B | Robokits | 316 (→372.88) | excl | In Stock | 3.0 Ah (min 2.9), 30 A cont. (80 °C cut-off), 36 A max; DC IR 17 mΩ @50 % SOC, AC 8 mΩ @30 % SOC (datasheet copy) | 34.53 | https://robokits.co.in/batteries-chargers/li-ion-cells/3.7v-18650-li-ion-cell/molicel-18650mah-13c-lithium-ion-battery-original-inr-18650-p30b | 2026-09-24 | VERIFIED |
| 18650 | Molicel P30B | ElectronicsComp / IHC | 539 (excl) / 599 (incl) | – | 45 / available | 3.0 Ah 10C | 58.9 / 55.5 | https://www.electronicscomp.com/molicel-inr-18650-p30b-36v-3000mah-10c-li-ion-battery ; https://indianhobbycenter.com/products/molicel-inr-18650-p30b-3-6v-2850mah-10c-li-ion-battery | 2026-09-24 | VERIFIED |
| 18650 | Molicel P28A | ElectronicsComp | 382 (→450.76) | excl | 274 | 2.8 Ah 13C | 44.72 | https://www.electronicscomp.com/molicel-inr18650-p28a-2800mah-13c-lithium-ion-battery | 2026-09-24 | VERIFIED |
| 18650 | Molicel P28A | IHC / lionbattery | 429 (incl) / 593.22 (excl, 100 in stock) | – | available | 2.8 Ah | 42.6 / 69.4 | https://indianhobbycenter.com/products/molicel-inr-18650-p28a ; https://lionbattery.in/shop/shop/lithium-cells/li-ion-cylindrical-battery-cell/molicel-2800mah-13c-lithium-ion-battery-original-inr18650-p28a/ | 2026-09-24 | VERIFIED |
| 18650 | Molicel P28A | TBW (authorised) | 305 | n/s | **Out of stock** | – | – | https://www.thebatteryworld.in/products/molicel-inr-18650-p28a-3-6v-2800mah | 2026-09-24 | VERIFIED |
| 18650 | Molicel M35A (3C) | ElectronicsComp / IHC | 449 (excl, 111 pcs) / 499 (incl) | – | in stock | 3.5 Ah 3C | 42.0 / 39.6 | https://www.electronicscomp.com/molicel-inr-18650-m35a-36v-3500mah-3c-li-ion-battery | 2026-09-24 | VERIFIED |
| 18650 | Samsung INR18650-30Q | ElectronicsComp | 699 (→824.82) | excl | 31 | **seller states COPY, "Brand Generic, China"** | – | https://www.electronicscomp.com/samsung-inr18650-30q-3000mah-5c-li-ion-battery | 2026-09-24 | VERIFIED (counterfeit disclosed) |
| 18650 | Samsung INR18650-35E | ElectronicsComp | 719 | excl | 31 | **seller states COPY, "Generic, China", 8 A max** | – | https://www.electronicscomp.com/samsung-inr18650-35e-3500mah-2c-li-ion-battery | 2026-09-24 | VERIFIED (counterfeit disclosed) |
| 18650 | Samsung 30Q / 35E, LG MJ1 | olelectronics.in | 431 / 390 / 333 | n/s | all **Out of stock** | – | – | https://olelectronics.in/product/samsung-inr18650-30q-3000mah/ | 2026-09-24 | VERIFIED |
| 18650 | LG HG2 / MJ1, Samsung 30Q / 35E | batterysource.in | "₹110" placeholder, no price on page | n/s | – | – | – | https://batterysource.in/product/lg-inr18650hg2-3-6v-3000mah-li-ion-battery/ | 2026-09-24 | UNVERIFIED (RFQ) |
| 18650 | Sony/Murata US18650 VTC6 | Robokits | 406 | excl | **Out of Stock** | 3.0 Ah, 15 A (30 A @80 °C cut-off) | – | https://robokits.co.in/batteries-chargers/skycell-li-ion-battery/3.7v-li-ion-batteries-3.2-4.2v/sony-murata-us18650-vtc6-3000mah-7c-li-ion-cell-original | 2026-09-24 | VERIFIED |
| 18650 | DMEGC INR18650-32E / 29E / 26E | ElectronicsComp | 224 / 179 / 113 | excl | 139 / – / – | energy cells | 22.3 (32E: 224×1.18=264.32 ÷ 11.84 Wh) | https://www.electronicscomp.com/dmegc-inr18650-32e-37v-3200mah-li-ion-battery | 2026-09-24 | VERIFIED |
| 18650 | "5000 mAh 18650" (Powerbee, Hongli) | Quartz ₹85 / IHC ₹159 | – | – | – | **5 Ah in an 18650 is not credible** (credible 18650s top out near 3.5–3.6 Ah) | – | https://quartzcomponents.com/products/18650-li-ion-5000mah-rechargeable-battery | 2026-09-24 | VERIFIED (**fake-capacity flag**) |

### 1d. LiFePO4 cells (32650 / 32700 / 26650 / 32140)

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | ₹/Wh incl (EST) | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 32650/32700 LFP | unbranded "Original EV Grade" 6 Ah 3C | Quartz | 225 | n/s | available | 3.2 V 6 Ah 3C | 11.72 (13.83 if +GST) | https://quartzcomponents.com/products/6000mah-3c-battery | 2026-09-24 | VERIFIED |
| 32700 LFP | HX IFR32700 6 Ah 3C | ElectronicsComp | 263 (→310.34) | excl | 842 | 6 Ah 3C | 16.16 | https://www.electronicscomp.com/hx-ifr32700-6000mah-3c-lifepo4-battery | 2026-09-24 | VERIFIED |
| 32700 LFP | HX IFR32700 6 Ah 1C "solar grade" | ElectronicsComp | 224 | excl | 102 | 1C | 13.77 | https://www.electronicscomp.com/hx-ifr32700-32v-6000mah-1c-lifepo4-battery-solar-grade | 2026-09-24 | VERIFIED |
| 32700 LFP | WTT 6 Ah | lionbattery.in | 253.39 (→299) | excl | in stock | – | 15.57 | https://lionbattery.in/shop/shop/lithium-cells/lifepo4-lfp-cylindrical-battery-cell/wtt-cylindrical-lithium-3-2v-6000mah-lfp-32700-lifepo%e2%82%84-rechargeable-battery-cell/ | 2026-09-24 | VERIFIED |
| 26650 LFP (power) | LithiumWerks (ex-A123) ANR26650M1B | The Battery World | 600 | n/s | In Stock | 2.5–2.6 Ah, 3.3 V | 72.7 | https://www.thebatteryworld.in/products/lithiumwerks-anr26650m1b-2-5ah-nanophosphate-lifepo4-power-cell | 2026-09-24 | VERIFIED |
| 26650 LFP (power) | LithiumWerks ANR26650M1B | Indian Hobby Center | 799 | incl | Available | 2.6 Ah typ, **52 A cont., 120 A 10 s pulse**, <10 mΩ AC, 76 g, >4000 cycles (datasheet copy) | 96.9 | https://indianhobbycenter.com/products/lithium-werks-anr26650m1b-3-3-v-2-6-ah-lithium-iron-phosphate-lifepo4-26650-battery | 2026-09-24 | VERIFIED |
| 32140 LFP | CNAE 3.2 V 15 Ah | lionbattery.in | 440.68 (→520) | excl | in stock | 48 Wh cell | 10.8 | https://lionbattery.in/shop/shop/lithium-cells/lifepo4-lfp-cylindrical-battery-cell/cnae-32140-lifepo%e2%82%84-cell-3-2v-15ah-high-capacity-long-life-lfp-battery-cell/ | 2026-09-24 | VERIFIED |

### 1e. Genuineness and counterfeit risk (evidence-based)

- **Samsung/LG cells are the highest risk.** ElectronicsComp's own pages for Samsung 30Q, 35E and 40T say that getting an original is "almost impossible", describe the stock as "Brand/Manufacturer Generic, Country of Origin China", and say they are "marking them as a copy". Treat any "Samsung/LG original" in Indian retail as unproven until tested.
  - The Robokits 50S has a customer review reporting 69 g and 9.97 mΩ @1 kHz, which is consistent with a genuine cell but is one sample only.
  - Lionbattery also claims a genuine Samsung SDI 50S.
- **Molicel has authorised channels in India.** The Battery World is branded "AUTHORISED DISTRIBUTOR OF MOLICEL" (https://www.thebatteryworld.in/). A search snippet also named Global Electronics, Pune (https://www.globalelec.co.in/molicel) as an authorised distributor; that site was not readable (UNVERIFIED).
  - Robokits notes that its Molicels are "graded and tested… testing marks on the cells". That means they may be re-graded rather than factory-fresh boxes.
  - The Zbotic P42A URL embeds a BIS registration string "IS 16046 (Part 2) R-41137189", which is a useful authenticity cross-check against the BIS CRS database (not checked today; the crsbis.in page returned no content).
- **Physical capacity limits expose fakes.** Any "6800 mAh 21700" or "5000 mAh 18650" is fake. The Quartz "21700 5000 mAh" listing itself admits 4500 mAh.
- **Incoming QC (recommended):** weigh each cell (P42A about 67–70 g, P45B about 70 g, 50S about 69–72 g), measure 1 kHz AC IR, and run a 1C capacity check plus a 10 A / 10 s DCR check on a sample. Buy one batch and one date code per pack.

### 1f. UNVERIFIED leads (IndiaMART, marketplaces, distributors; from 2026-09-24 search snippets, not page-verified)

| Item | Seller / price (snippet) | URL | Evidence |
|---|---|---|---|
| Molicel P42A | ₹450/pc (Gandhinagar, "UN/BIS certified"); ₹510 (Bengaluru); ₹450 (Thane); ₹455 (New Delhi) | https://www.indiamart.com/proddetail/molicel-21700-p42a-4200mah-10c-rated-un-bis-certified-cell-for-drone-23961745688.html ; https://www.indiamart.com/proddetail/molicel-inr-21700-p42a-26566365733.html ; https://www.indiamart.com/proddetail/molicel-inr-21700-p42a-high-current-lithium-ion-cell-for-drones-and-evs-2850966779430.html | UNVERIFIED |
| Molicel P45B | ₹410 (Pune); ₹560 (New Delhi) | https://www.indiamart.com/proddetail/molicel-inr21700-p45b-4500mah-lithium-ion-battery-10c-2854340140062.html ; https://www.indiamart.com/proddetail/molicel-inr-21700-p45b-high-current-lithium-ion-cell-for-drones-and-evs-2853200798230.html | UNVERIFIED |
| Samsung 40T | ₹400 (Mumbai) | https://www.indiamart.com/proddetail/samsung-inr21700-40t-3-6v-4000mah-li-ion-battery-2855157763973.html | UNVERIFIED (high fake risk) |
| "Samsung SDI 21700" | ₹366 (Enfeed EV, Aurangabad) | https://www.indiamart.com/proddetail/samusng-lithium-ion-sdi-cell-21700-27013753233.html | UNVERIFIED |
| LG M58T | Accurate Ampere / Genuine Power (Pune), ~₹225 per snippet | https://www.indiamart.com/proddetail/lithium-ion-lg-inr-21700-m58t-2857327454362.html | UNVERIFIED (energy cell, 12.5 A) |
| Samsung SDI 50S | TME India (import distributor) | https://www.tme.com/in/en/details/accu-inr21700-50s/rechargeable-batteries/samsung-sdi/inr21700-50s/ | UNVERIFIED (Cloudflare) |
| Molicel P42A | Flipkart listing | https://www.flipkart.com/molicel-21700-p42a-battery/p/itm5471d59e20d2c | UNVERIFIED |
| EU import option | NKON (Netherlands). Sea or air freight of Li-ion as DG plus 18 % IGST plus duty makes it uncompetitive against ₹20–30/Wh Indian retail | – | note only |

---

## 2. PRE-BUILT PACKS

### 2a. 6S LiPo 5000–10000 mAh

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | ₹/Wh incl (EST) | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 6S LiPo | GenX 22.2 V 6S 5200 mAh 40C/80C | Robokits | 4,768 (→5,626) | excl | In Stock | 708 g, 138×43×48 mm, 115 Wh (163 Wh/kg) | 48.7 | https://robokits.co.in/batteries-chargers/drone-batteries/genx-power-premium-lipo-battery/genxpower-22.2v-lipo-batteries/genx-22.2v-6s-5200mah-40c-80c-premium-lipo-lithium-polymer-battery | 2026-09-24 | VERIFIED |
| 6S LiPo | GenX 6S 6800 mAh 40C | Robokits | 6,287 (→7,419) | excl | listed | 151 Wh | 49.1 | https://robokits.co.in/batteries-chargers/drone-batteries/genx-power-premium-lipo-battery/genxpower-22.2v-lipo-batteries/genx-22.2v-6s-6800mah-40c-80c-premium-lipo-lithium-polymer-battery | 2026-09-24 | VERIFIED (listing) |
| 6S LiPo | GenX 6S 8000 mAh 40C/80C | Robokits | 7,426 (→8,763) | excl | In Stock | 1158 g, 168×59×50 mm, XT90 | 49.3 | https://robokits.co.in/batteries-chargers/drone-batteries/genx-power-premium-lipo-battery/genxpower-22.2v-lipo-batteries/genx-22.2v-6s-8000mah-40c-80c-premium-lipo-lithium-polymer-battery | 2026-09-24 | VERIFIED |
| 6S LiPo | GenX 6S 10000 mAh 25C/50C XT90 | Robokits | 9,088 (→10,724) | excl | In Stock | 1236 g, 181×63×60 mm, 222 Wh (180 Wh/kg) | 48.3 | https://robokits.co.in/batteries-chargers/drone-batteries/genx-power-premium-lipo-battery/genxpower-22.2v-lipo-batteries/genx-22.2v-6s-10000mah-25c-50c-premium-lipo-battery-with-xt-90-connector | 2026-09-24 | VERIFIED |
| 6S LiPo | GenX 6S 5200 / 8000 / 10000 (XT90S) | Indian Hobby Center | 5,899 / 8,399 / 10,319 | incl | Available | same GenX line | 51.1 / 47.3 / 46.5 | https://indianhobbycenter.com/products/genx-22-2v-4s-10000mah-25c-50c-premium-lipo-lithium-polymer-battery-with-xt90s-connector | 2026-09-24 | VERIFIED |
| 6S LiPo | Bonka 22.2 V 5200 mAh 35C / 4200 mAh 35C | Robocraze | 9,309 / 6,705 | incl | Available | – | 80.6 / 71.9 | https://robocraze.com/products/bonka-5200mah-35c-6s1p-22-2v-lipo-battery | 2026-09-24 | VERIFIED |
| 6S LiPo | Bonka 22.2 V 10000 mAh 25C | Indian Hobby Center | 15,999 | incl | Available | – | 72.1 | https://indianhobbycenter.com/products/bonka-10000mah-25c-6s-22-2v-lipo-battery | 2026-09-24 | VERIFIED |
| 6S LiPo | Tattu 22.2 V 6S 25C 10000 mAh | ThinkRobotics | 16,499.99 | n/s | **Out of stock** | – | 74.3 | https://thinkrobotics.com/products/tattu-22-2v-6s-25c-lipo-battery-pack | 2026-09-24 | VERIFIED |
| 6S LiPo | Tattu 16000 / 22000 mAh | Robocraze | 24,149 / 29,899 | incl | **Out of stock** | too large | – | https://robocraze.com/products/22-2v-16000mah-25-50c-6s1p-bonka-lipo-battery-pack | 2026-09-24 | VERIFIED |
| 6S LiPo | Orange, Gens Ace, CNHL 6S 5–10 Ah | – | not listed on Robocraze, IHC, ThinkRobotics, Quartz or Robokits (Robu/Amazon not checked by instruction) | – | – | – | – | – | 2026-09-24 | NOT FOUND |

### 2b. Li-ion packs (6S / 7S / 10S / 12S / 13S)

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | ₹/Wh incl (EST) | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|---|
| 6S2P Li-ion | GenX Molicel 21.6 V 8400 mAh 11C (P42A) | Robokits | 7,380 (→8,708) | excl | In Stock, ships 1–2 d | 948 g, 142×39×80 mm, XT60H, "IR 4.75 mΩ" (vendor), 181 Wh (191 Wh/kg) | 48.0 | https://robokits.co.in/batteries-chargers/drone-batteries/genx-molicel-li-ion-battery/genx-molicel-21.6v-li-ion/genx-molicel-21.6v-8400mah-11c-premium-lithium-ion-rechargeable-battery | 2026-09-24 | VERIFIED |
| 6S2P Li-ion | GenX Molicel+ 21.6 V 9000 mAh 13C | Robokits | 8,676 (→10,238) | excl | In Stock | 948 g, 194 Wh | 52.7 | https://robokits.co.in/batteries-chargers/drone-batteries/genx-molicel-plus-li-ion-battery/genx-molicel-22.2v-li-ion/genx-molicel-22.2v-6s2p-9000mah-12c-20c-premium-lithium-ion-rechargeable-battery | 2026-09-24 | VERIFIED |
| 6S3P Li-ion | GenX Molicel 21.6 V 12600 mAh 11C | Robokits | 10,955 (→12,927) | excl | In Stock | 1362 g, 272 Wh | 47.5 | https://robokits.co.in/batteries-chargers/drone-batteries/genx-molicel-li-ion-battery/genx-molicel-21.6v-li-ion/genx-molicel-21.6v-12600mah-11c-premium-lithium-ion-rechargeable-battery | 2026-09-24 | VERIFIED |
| 6S2P Li-ion | GenX Molicel Pro 21.6 V 10000 mAh 12C/15C | Robokits | 12,235 (→14,437) | excl | In Stock | 972 g, 216 Wh | 66.8 | https://robokits.co.in/batteries-chargers/drone-batteries/genx-molicel-pro-li-ion-battery/genx-molicel-pro-21.6v-li-ion/genx-molicel-pro-21.6v-10000mah-15c-premium-lithium-ion-rechargeable-battery | 2026-09-24 | VERIFIED |
| 6S2P Li-ion | Crocks Pack Samsung 50S 22.2 V 10 Ah, 90 A cont. / ~100 A peak | lionbattery.in | 7,203.39 (→8,500) | excl | in stock | 12× 50S, ~920–950 g (vendor), NCA | 38.3 | https://lionbattery.in/shop/drones-batteries/drones-batteries-for-long-fpv-flight/6-cell-li-ion-drone-battery-pack-22-2v25-2v/crocks-pack-samsung-inr-21700-50s-22-2v-10000mah-6s2p-90a-discharge-li-ion-drone-battery-pack/ | 2026-09-24 | VERIFIED |
| 6S2P Li-ion | Crocks Pack Molicel P42A 22.2 V 8.4 Ah, 80 A / 100 A | lionbattery.in | 6,610.17 (→7,800) | excl | in stock | 900–1050 g (vendor), external BMS optional | 41.8 | https://lionbattery.in/shop/drones-batteries/drones-batteries-for-long-fpv-flight/6-cell-li-ion-drone-battery-pack-22-2v25-2v/crocks-pack-22-2v-8400-mah-li-ion-drone-battery-pack-inr-21700-molicel-6s2p-80a-100a-discharge/ | 2026-09-24 | VERIFIED |
| 6S3P Li-ion | Crocks Pack Samsung 50S 15 Ah 135 A | lionbattery.in | 9,877.12 (→11,655) | excl | in stock | 333 Wh | 35.0 | https://lionbattery.in/shop/drones-batteries/drones-batteries-for-long-fpv-flight/6-cell-li-ion-drone-battery-pack-22-2v25-2v/crocks-pack-samsung-inr-21700-50s-22-2v-15000mah-6s3p-135a-discharge-li-ion-drone-battery-pack/ | 2026-09-24 | VERIFIED |
| 6S2P Li-ion (3C) | DMEGC 6S 22.2 V 9 Ah 3C | lionbattery.in | 4,236.44 (→4,999) | excl | 200 in stock | 27 A cont. (3C), 650–800 g (vendor) | 25.0 | https://lionbattery.in/shop/lithium-battery/li-on-nmc-battery-pack/6-cell-24v-li-ion-battery-pack-22-2v25-2v/dmegc-6s-22-2v-9000mah-6s2p-3c-lithium-ion-rechargeable-battery-pack/ | 2026-09-24 | VERIFIED |
| 6S2P Li-ion (3C) | BAK 6S 22.2 V 10 Ah 3C | lionbattery.in | 4,138.98 (→4,884) | excl | in stock | "~840 g" (vendor, implausibly light), BMS optional | 22.0 | https://lionbattery.in/shop/lithium-battery/li-on-nmc-battery-pack/6-cell-24v-li-ion-battery-pack-22-2v25-2v/bak-6s-22-2v-10000mah-lithium-ion-battery-pack-6s2p-3c-high-capacity-rechargeable-battery/ | 2026-09-24 | VERIFIED |
| 6S3P / 6S4P (3C) | DMEGC 13.5 Ah / 18 Ah | lionbattery.in | 5,931.36 / 7,449.15 | excl | 200 in stock | 3C | 23.4 / 22.0 | https://lionbattery.in/shop/lithium-battery/li-on-nmc-battery-pack/6-cell-24v-li-ion-battery-pack-22-2v25-2v/dmegc-6s-22-2v-18000mah-6s4p-3c-lithium-ion-rechargeable-battery-pack/ | 2026-09-24 | VERIFIED |
| 6S2P "24 V" pack | WATTNINE 24 V 10 Ah NMC (26700 cells, built-in BMS) | Quartz | 4,978 | n/s | available | tested at 5–12 A only (not high drain) | 22.4 | https://quartzcomponents.com/products/24v-10ah-li-ion-nmc-battery-pack | 2026-09-24 | VERIFIED |
| 6S2P pack | Samsung 25R 22.2 V 5 Ah 8C (brand unproven) | ElectronicsComp | 5,807 | excl | Out of stock | – | 61.7 | https://www.electronicscomp.com/samsung-inr18650-25r-li-ion-222v-5000mah-8c-6s2p-li-ion-battery-pack-ev-grade | 2026-09-24 | VERIFIED |
| 6S2P pack | Pro-Range P28A 22.2 V 5.6 Ah 50 A/60 A | olelectronics.in | 6,100 | n/s | Out of stock | – | 49.1 | https://olelectronics.in/product/pro-range-inr-18650-p28a-22-2v-5600mah/ | 2026-09-24 | VERIFIED |
| 7S | none pre-built found (lionbattery "7S2P / 7S3P" queries returned 0) | – | – | – | – | build to order | – | – | 2026-09-24 | NOT FOUND |
| 10S2P 36 V | BAK 36 V 10 Ah 3C (30 A cont., 40–45 A peak) | lionbattery.in | 6,711.86 (→7,920) | excl | in stock | description also says "DMEGC cells" (inconsistent) | 22.0 | https://lionbattery.in/shop/lithium-battery/li-on-nmc-battery-pack/10-cell-36v-li-ion-battery-pack-36v42v/bak-10s-36v-10000mah-10s2p-3c-lithium-ion-rechargeable-battery-packk/ | 2026-09-24 | VERIFIED |
| 10S2P / 10S3P 36 V | Lion e-bike 5.6 Ah / 7.8 Ah with BMS | lionbattery.in | 4,661.02 / 5,720.34 | excl | 100 in stock / in stock | low rate | 27.3 / 24.0 | https://lionbattery.in/shop/lithium-battery/li-on-nmc-battery-pack/10-cell-36v-li-ion-battery-pack-36v42v/lion-e-bike-36v-5600mah-10s2p-lithium-ion-rechargeble-battery-pack/ | 2026-09-24 | VERIFIED |
| 10S3P 36 V | DMEGC 13.5 Ah 3C | lionbattery.in | 9,144.07 (→10,790) | excl | 200 in stock | – | 22.2 | https://lionbattery.in/shop/lithium-battery/li-on-nmc-battery-pack/10-cell-36v-li-ion-battery-pack-36v42v/dmegc-10s-36v-13500mah-10s4p-3c-lithium-ion-rechargeable-battery-pack/ | 2026-09-24 | VERIFIED |
| 12S LiPo | GenX 44.4 V 12S 12000 mAh 20C/40C | Robokits | 20,950 (→24,721) | excl | listed | 533 Wh, large | 46.4 | https://robokits.co.in/batteries-chargers/drone-batteries/genx-power-premium-lipo-battery/genxpower-14.8v-lipo-batteries/genx-44.4v-12s-12000mah-20c-40c-premium-lithium-polymer-battery | 2026-09-24 | VERIFIED (listing) |
| 13S2P 48 V | BAK 48 V 10 Ah 3C (30 A cont., 40–45 A peak) | lionbattery.in | 8,949.15 (→10,560) | excl | in stock | 468 Wh nominal, BMS optional | 22.6 | https://lionbattery.in/shop/lithium-battery/li-on-nmc-battery-pack/13-cell-48v-li-ion-battery-pack-46-8v54-6v/bak-13s-48v-10000mah-13s2p-3c-lithium-ion-rechargeable-battery-pack/ | 2026-09-24 | VERIFIED |
| 13S3P 48 V | DMEGC 13.5 Ah 3C | lionbattery.in | 12,076.27 (→14,250) | excl | 200 in stock | 2.8–3.5 kg (vendor) | 22.6 | https://lionbattery.in/shop/lithium-battery/li-on-nmc-battery-pack/13-cell-48v-li-ion-battery-pack-46-8v54-6v/dmegc-13s-48v-13500mah-13s3p-3c-lithium-ion-rechargeable-battery-pack/ | 2026-09-24 | VERIFIED |
| 13S2P 48 V | WATTNINE 48 V 10 Ah (26650 NMC 3C, BMS) | Quartz | 10,986 | n/s | available | 10 A nominal continuous, 3 kg | 23.5 | https://quartzcomponents.com/products/wattnine%C2%AE-48v-10ah-rechargeable-lithium-ion-battery-with-1-year-warranty | 2026-09-24 | VERIFIED |
| 6S7P "ROV" | Molicel P42A 22.2 V 29.4 Ah | Zbotic / EC / IRS | 39,899 backorder / 35,111 OOS / 37,995 pre-order | incl / excl / incl | not in stock | too big for JX1 | – | https://zbotic.in/product/molicel-inr-21700-p42a-22-2v-29400mah-11c-6s7p-li-ion-rov-battery-pack/ | 2026-09-24 | VERIFIED |

**Pack observations:**
- Indian "3C" DMEGC/BAK packs are the cheapest per Wh (₹22–25/Wh). They are rated about 30 A per 2P string, so they do not cover 1.5–3 kW peaks on a 24 V bus.
- High-drain pre-built packs (Samsung 50S or Molicel) cost ₹38–53/Wh, about 1.6–2.4× the cost of buying the same cells and building yourself.
- Vendor pack weights are sometimes impossible (e.g. "Crocks Ultra 6S2P 8.4 Ah ≈ 680 g" is below the mass of 12 × 21700 cells). Weigh on receipt.

### 2c. Indian custom-pack builders and services with published pricing

| Builder / service | What is published | Price ₹ | GST | URL | Evidence |
|---|---|---|---|---|---|
| lionbattery.in ("LI-ON BATTERY") | Hundreds of priced configurations (1S–20S; Samsung 50S, Molicel P42A/P28A, DMEGC, BAK; LFP), BMS optional or added, connector choice (XT60/XT90/AS150/Anderson) | see 2b | excl | https://lionbattery.in/ | VERIFIED |
| lionbattery.in, Battery Pack / BMS Testing Service | Pack or BMS test service | 1,694.92 (→2,000) | excl | https://lionbattery.in/shop/battery-testing-reports/battery-pack-bms-testing-services/ | VERIFIED |
| lionbattery.in, Li battery testing & diagnosis | Variants from 847.46 to 7,400 | 847.46+ | excl | https://lionbattery.in/shop/battery-testing-service/lithium-battery-testing-diagnosis-service-all-brands/ | VERIFIED (Woo API) |
| Robokits (GenX brand) | Pre-built GenX Molicel/LiPo packs; cell pages say "Please suggest us your required specifications for Customized Li-Ion Battery Pack" | RFQ | excl | https://robokits.co.in/ | VERIFIED (text) |
| ElectronicsComp | "Orange Custom Battery Pack: We build battery packs according to your specific requirement…" (on cell pages) | RFQ | excl | https://www.electronicscomp.com/samsung-inr21700-40t-4000mah-9c-li-ion-battery | VERIFIED (text) |
| The Battery World (authorised Molicel) | Custom BMS, thermal and mechanical design, "Small Quantity Support"; X-Pack 2S 4500 mAh with BMS ₹1,775 | RFQ | n/s | https://www.thebatteryworld.in/ | VERIFIED (text) |
| olelectronics.in "Pro-Range" | P28A packs 1S–6S (mostly OOS) | 1,005–6,100 | n/s | https://olelectronics.in/product/pro-range-inr-18650-p28a-22-2v-5600mah/ | VERIFIED |
| Spot-welding-only service with a published per-cell price | not found | – | – | – | NOT FOUND |

### 2d. Sizing sanity check for JX1 (ESTIMATED)

- **Currents:**
  - 24 V (6S), 3 kW peak: 3000 W ÷ (6 × ~3.3 V under load ≈ 19.8 V) ≈ **152 A**. At 1.5 kW about 76 A. At 400 W average about 18.5 A (at 21.6 V).
  - 48 V (13S), 3 kW peak: 3000 ÷ (13 × 3.3 ≈ 42.9 V) ≈ **70 A**. At 1.5 kW about 35 A. At 400 W average about 8.5 A (at 46.8 V).
- **13S2P Molicel P45B:**
  - 35 A per cell at the 3 kW peak, inside the 45 A rating.
  - Sag ≈ 35 A × 13.8 mΩ (max DCR, 10 A/10 s) ≈ 0.48 V per cell.
  - Energy 26 × 16.2 Wh = 421 Wh. Cells 26 × ~70 g ≈ 1.82 kg.
  - Cell cost at Robokits 26 × ₹481.44 = **₹12,517 (₹29.7/Wh)**.
  - Runtime ≈ 421 × 0.85 ÷ 300 W ≈ 1.2 h.
- **13S2P Samsung 50S:**
  - 26 × ₹363.44 = **₹9,449 for 468 Wh (₹20.2/Wh)**.
  - 35 A per cell is inside the "45 A with 80 °C cut" line but above the 25 A no-cutoff line, which is acceptable for pulses under 1 s. Needs cell thermal checks.
- **6S4P P45B (24 V):**
  - 38 A per cell at the 152 A peak. 24 cells = 389 Wh, ₹11,555.
  - The BMS, wire, fuse and switch must handle about 150 A peaks, which is costlier (e.g. a 7S 100 A Daly was ₹3,220 ex at lionbattery and OOS today).
  - **This current burden argues for the 36–48 V bus.**
- **Prebuilt comparison:**
  - lionbattery BAK 13S2P 3C at ₹10,560 is cheap, but its 30 A continuous / 40–45 A peak does not cover a 70 A peak.
  - Two in parallel (13S4P) would, at ~₹21k.

---

## 3. BMS

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| 6S hardware | Daly Li-ion 6S 24 V 30 A waterproof | Quartz | 937 | n/s | available | 30 A charge/discharge, IP65, NTC | https://quartzcomponents.com/products/daly-li-ion-6s-24v-30a-battery-management-system-bms-protection-board | 2026-09-24 | VERIFIED |
| 6S hardware | Daly 6S 15 A waterproof | Quartz | 620 | n/s | available | – | https://quartzcomponents.com/products/daly-li-ion-nmc-6s-24v-15a-waterproof-battery-management-system-bms-protection-board | 2026-09-24 | VERIFIED |
| 6S hardware | Daly NMC 6S 20 A / 15 A / 30 A | lionbattery.in | 805.08 / 720.34 / 1,016.95 | excl | 1 / 1 / OOS | – | https://lionbattery.in/shop/shop/battery-bms/daly-nmc-bms-hardware/bms-nmc-6s-20a-daly-12d2/ | 2026-09-24 | VERIFIED |
| 7S hardware | Daly 7S 24 V 40 A waterproof | Quartz | 978 | n/s | available | listing text "constant discharge 10A~250A" (generic copy) | https://quartzcomponents.com/products/24v-7s-40a-bms-daly-waterproof-bms-for-li-ion-cell-nmc | 2026-09-24 | VERIFIED |
| 7S hardware | Daly 7S 30 A waterproof | Quartz | 999 | n/s | available | – | https://quartzcomponents.com/products/24v-7s-30a-bms-daly-waterproof-bms-for-li-ion-cell-nmc | 2026-09-24 | VERIFIED |
| 7S hardware | Daly NMC 7S 40 / 60 / 100 A | lionbattery.in | 1,101.69 / 2,118.64 / 3,220.34 | excl | **all OOS** | – | https://lionbattery.in/shop/shop/battery-bms/daly-nmc-bms-hardware/bms-nmc-7s-100a-daly-7aa6/ | 2026-09-24 | VERIFIED |
| 7S hardware | JBD HP07SA 7S 20 A | lionbattery.in | 720.34 | excl | 1 | – | https://lionbattery.in/shop/shop/battery-bms/jbd-nmc-bms-hardware/jbd-bms-nmc-7s-20amp-hardware-hp07sa/ | 2026-09-24 | VERIFIED |
| 10S hardware | Daly NMC 10S 20 A waterproof | Quartz / lionbattery | 897 / 720.34 ex (10 in stock) | n/s / excl | available | – | https://quartzcomponents.com/products/daly-li-ion-nmc-10s-36v-20a-waterproof-battery-management-system-bms-protection-board | 2026-09-24 | VERIFIED |
| 10S hardware | 10S 36 V 60 A / 80 A common-port (unbranded) | Quartz | 1,295 / 1,490 | n/s | available | balance, common port | https://quartzcomponents.com/products/10s-36v-60a-bms-for-lithium-ion-nmc-battery-with-cell-balancing-common-port | 2026-09-24 | VERIFIED |
| 10S hardware | 10S 36 V 30 A common port | Robokits | 1,119 | excl | listed | – | https://robokits.co.in/batteries-chargers/charge-protection-circuit/10s-36v-30a-bms-balance-common-port-charge-protection-board-3.7-li-ion-cell | 2026-09-24 | VERIFIED (listing) |
| 13S hardware | Daly NMC 13S 48 V 40 A waterproof | Quartz | 1,746 | n/s | available | **description says "20A continuous discharge"** despite the 40 A title (flag) | https://quartzcomponents.com/products/daly-li-ion-nmc-13s-48v-40a-waterproof-battery-management-system-bms-protection-board | 2026-09-24 | VERIFIED |
| 13S hardware | Daly NMC 13S 40 A (non-waterproof) | lionbattery.in | 1,059.32 (→1,250) | excl | 40 in stock | – | https://lionbattery.in/shop/shop/battery-bms/daly-nmc-bms-hardware/daly-bms-nmc-13s-40a-non-waterproof/ | 2026-09-24 | VERIFIED |
| 13S hardware | JBD NMC 13S 40 A (ZP16S011) | lionbattery.in | 1,016.10 | excl | 17 in stock | – | https://lionbattery.in/shop/shop/battery-bms/jbd-nmc-bms-hardware/bms-nmc-13s-40a-jbd-zp16s011-548b/ | 2026-09-24 | VERIFIED |
| 13S hardware | 13S 40 A 48 V common port | Robokits | 1,270 (special) | excl | listed | – | https://robokits.co.in/batteries-chargers/accessories/charge-protection-circuit/13s-40a-48v-bms-balance-common-port-charge-protection-board-3.7-li-ion-cell | 2026-09-24 | VERIFIED (listing) |
| 13S hardware | 13S 48 V 20 A common port | Quartz | 1,325 | n/s | available | – | https://quartzcomponents.com/products/13s-48v-20a-bms-for-lithium-ion-nmc-battery-with-cell-balancing-common-port | 2026-09-24 | VERIFIED |
| Smart 10–14S | **JBD SP14S004 10–14S 40 A smart** (UART/BT per JBD line) | lionbattery.in | 1,863.56 (→2,199) | excl | 10 in stock | 30 A version 1,440.68; 20 A version 1,355.93 | https://lionbattery.in/shop/shop/battery-bms/jbd-nmc-bms-smart/bms-nmc-10-14s-40a-smart-jbd-sp14s004-7d43/ | 2026-09-24 | VERIFIED |
| Smart 10–17S | JBD SP17S005 40 / 50 / 60 A smart | lionbattery.in | 2,457.63 / 2,541.53 / 2,796.61 | excl | 13 / 2 / 1 | 100 A version OOS | https://lionbattery.in/shop/shop/battery-bms/jbd-nmc-bms-smart/bms-nmc-10-17s-60a-smart-jbd-sp17s005-73b7/ | 2026-09-24 | VERIFIED |
| Smart 7–17S | **Daly "Black" Smart BMS 7–17S 40 A / 60 A** | lionbattery.in | 2,457.63 / 2,965.25 | excl | 2 / 1 | covers 7S and 13S | https://lionbattery.in/shop/shop/battery-bms/daly-lfp-bms-smart/daly-black-smart-bms-7-17s-40a/ | 2026-09-24 | VERIFIED |
| Smart (LFP) | Daly Smart LiFePO4 BMS with Bluetooth (12S/15S/16S 100 A …) | ThinkRobotics | from 5,199.99 (16S 100 A 7,399.99 in stock) | n/s | some variants | LFP-only listing | https://thinkrobotics.com/products/daly-smart-lifepo4-bms | 2026-09-24 | VERIFIED |
| Smart (LFP) | Daly 8S 60 A smart; 4S 80/100 A smart CAN | Quartz | 4,397; 4,831 / 5,037 | n/s | available | LFP | https://quartzcomponents.com/products/daly-lifepo4-8s-24v-60a-smart-waterproof-battery-management-system-common-port-with-balance-bms-protection-board | 2026-09-24 | VERIFIED |
| JK smart | JK BD4A24S4P 8–24S 40 A (active balance, CAN) | lionbattery.in | 4,406.78 | excl | 2 | 8S minimum, so not usable for 6S/7S | https://lionbattery.in/shop/shop/battery-bms/jk-bms-smart/jk-bms-8-24s-40a-lfp-smart-can-jk-bd4a24s4pcy-7979/ | 2026-09-24 | VERIFIED |
| JK smart | JK BD6A20S10P 8–20S 100 A; BD4A20S4P 8–20S 40 A | lionbattery.in | 4,322.03 / 3,305.08 | excl | 1 / backorder | – | https://lionbattery.in/shop/shop/battery-bms/jk-bms-smart/jk-smart-bms-8-20s-40a-bd4a20s4p/ | 2026-09-24 | VERIFIED |
| JK smart | JK 4–8S 40 A / 60 A (BD4A8S4P / 6P) | lionbattery.in | 2,966.10 / 3,093.22 | excl | **OOS** | would cover 6–7S | https://lionbattery.in/shop/shop/battery-bms/jk-bms-smart/jk-smart-bms-4-8s-40a-jk-bd4a8s4p-be60/ | 2026-09-24 | VERIFIED |
| ANT BMS | – | not found in readable Indian stores | – | – | – | – | – | 2026-09-24 | NOT FOUND |
| Active balancer | Daly 13S 1 A smart; NEEY 15S 2 A; Robokits 14S 5 A | lionbattery / Robokits | 3,050.85 / 1,439.83 / 2,199 | excl | in stock | – | https://lionbattery.in/shop/shop/daly-active-cell-balancer/daly-active-balancer-13s-1a-smart-daly-48f4/ | 2026-09-24 | VERIFIED |
| Balance leads | JST-XH 7-pin F-F 25 cm; 8-pin F-F 25 cm; JST-XH 7-pin male | Indian Hobby Center | 26 / 49 / 5 | incl | available | 2.54 mm | https://indianhobbycenter.com/products/7-pin-jst-xh-2515-rmc-female-to-female-connector-with-wire-25cm-7x7-2-54mm-pitch-1-pc | 2026-09-24 | VERIFIED |
| Balance leads | JST-XH 2–5-pin female cables | Quartz | 13 each | n/s | available | – | https://quartzcomponents.com/products/5-pin-jst-sm-connector-with-wire-5-24mm-pitch | 2026-09-24 | VERIFIED |
| Precharge module | no Daly/JBD precharge module listed | – | – | – | – | use resistor plus anti-spark switch, or a connector with built-in resistor (XT90-S / AS150) | – | 2026-09-24 | NOT FOUND |

**BMS notes:**
- Cheap 40 A-class BMS boards have short over-current trip delays. A 70 A walking peak on 13S will trip a 40 A board unless its over-current delay or threshold is configurable. JBD and Daly smart boards expose these settings in their apps; hardware boards do not.
- Budget for a 60 A-class smart BMS on 13S (JBD SP17S005 60 A at ₹3,300 incl, or Daly Black 60 A at ₹3,499 incl), or put the BMS on a separate FET switch with signal-only protection.

---

## 4. PROTECTION

### 4a. Emergency-stop (22 mm, twist-release)

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| E-stop | **Schneider XB2BS8442C** Harmony XB2 | Moglix | 399 (338 + 61 GST; MRP 560) | incl | In stock | 22 mm, 40 mm mushroom, **1NC**, turn-to-release, metal bezel, screw clamp | https://www.moglix.com/schneider-electric-xb2bs8442c-emergency-stop-mushroom-head-40mm-harmony-xb2-22mm-1nc-red/mp/msnr50n3q8x251 | 2026-09-24 | VERIFIED |
| E-stop | **Schneider XB5AS8445N** Harmony XB5 | Moglix | 789 (668 + 121 GST; MRP 1,152) | incl | In stock | 22 mm, 40 mm, **1NO+1NC**, trigger action, turn-to-release, plastic | https://www.moglix.com/schneider-40-mm-mushroom-head-trigger-action-turn-to-release-type-red-non-illuminated-push-button-xb5as8445n/mp/msn2qgt6g0mxxd | 2026-09-24 | VERIFIED |
| E-stop | Schneider XB5AS542N (1NC turn-to-release) | Moglix | 304 (MRP 476) | incl | listed | 22 mm | https://www.moglix.com/schneider-electric-harmony-xb5-22mm-red-1nc-turn-to-release-emergency-switching-of-mushroom-head-push-button-xb5as542n/mp/msno5wnpw2mw51 | 2026-09-24 | VERIFIED (search listing) |
| E-stop | Schneider XB4BT842 (metal, 1NC) | Moglix | 2,739 | incl | listed | – | https://www.moglix.com/schneider-electric-xb4bt842-xb4-emergency-stop-push-button-red-22mm-40mm-head-1nc/mp/msn75dq1rzzd92 | 2026-09-24 | VERIFIED (search listing) |
| E-stop | Yokins EB2M-A-01-ZS 1NO+1NC | Moglix | 181 | incl | listed | 22 mm | https://www.moglix.com/yokins-22mm-600v-1no1nc-red-emergency-stop-push-button-eb2m-a-01-zs/mp/msn153npnwrj53 | 2026-09-24 | VERIFIED (search listing) |
| E-stop | Emergency Stop Push Button Switch (unbranded) | Robokits | 350 special (reg 450) | excl | In Stock | – | https://robokits.co.in/automation-control-cnc/table-top-cnc-router/cnc-router-accessories/emergency-stop-push-button-switch | 2026-09-24 | VERIFIED |
| E-stop | LAY37 DPST 660 V 10 A | ElectronicsComp | 199 | excl | listed | generic | https://www.electronicscomp.com/ac-660v-10a-lay37-dpst-emergency-stop-push-button-switch | 2026-09-24 | VERIFIED (listing) |
| E-stop | YWBL-WH 22 mm mushroom | Robocraze | 93 | incl | Available | generic | https://robocraze.com/products/ywbl-wh-mushroom-emergency-stop-push-button-switch-22mm | 2026-09-24 | VERIFIED |
| E-stop | Push-button emergency stop 22.5 mm | Quartz | 67 | n/s | available | generic | https://quartzcomponents.com/products/emergency-off-22-5-mm-new | 2026-09-24 | VERIFIED |

Note: every E-stop above is a signal-level switch (10 A AC contacts). Use its NC contact to kill the switch / contactor / gate-driver enable. **Do not break a 70–150 A DC bus directly through it.**

### 4b. Main switching: anti-spark MOSFET switches, DC contactors, relays

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| Anti-spark switch | **Flipsky Anti Spark Switch Smart Enhanced 300A V2.0** | technobotix.in | 7,499 (MRP 8,499) | incl | InStock | 12–84 V (3–20S), **100 A continuous**, 160 A max with big heatsink, HYG015N10NS1TA FETs, auto-off after 5 min, LED button | https://www.technobotix.in/products/flipsky-anti-spark-switch-smart-enhanced-300a-v2-0/1781252000001361046 | 2026-09-24 | VERIFIED |
| Anti-spark switch | Flipsky Antispark Switch Pro, Al PCB/case, 200 A | technobotix.in | 6,999 | incl | **OutOfStock** | 3–14S (12–60 V), 100 A continuous (Al case), 200 A max | https://www.technobotix.in/products/flipsky-antispark-switch-pro-with-aluminum-pcb-case-200a/1781252000001361033 | 2026-09-24 | VERIFIED |
| Anti-spark switch | Flipsky Antispark Switch Pro V3.0 280 A | Indian Robo Store | 4,899 (MRP 5,999) | incl | **Pre-order** | – | https://indianrobostore.com/product/flipsky-antispark-switch-pro-v30-280a | 2026-09-24 | VERIFIED |
| Anti-spark switch | Flipsky Pro V3.0 280 A | Atlantis Robotics (IndiaMART) ₹4,699.99 / ₹6,299.99 | – | – | – | – | https://www.indiamart.com/proddetail/flipsky-antispark-switch-pro-v3-0-280a-2850463605212.html | 2026-09-24 | UNVERIFIED |
| "Flier" anti-spark switch | – | not found in readable Indian stores | – | – | – | – | – | 2026-09-24 | NOT FOUND |
| Anti-spark connector | Amass XT90S pair / AS150 pair (built-in pre-charge resistor) | Robokits | 180 / 770 | excl | In Stock | see §6a | https://robokits.co.in/batteries-chargers/plugs-and-connectors/amass-xt90s-anti-spark-connectors-male-female-pair-original | 2026-09-24 | VERIFIED |
| EV contactor | **TE Kilovac LEV100A4ANG** (100 A, 900 VDC, SPST-NO) | tanotis.com (import) | 16,085.85 | incl GST + duty | listed available | – | https://www.tanotis.com/products/kilovac-te-connectivity-lev100a4ang-contactor-900-vdc-1-pole-spst-no-panel-100-a | 2026-09-24 | VERIFIED (listing; lead time unknown) |
| EV contactor | TE LEV100A5ANG / LEV100A6ANH | tanotis.com | 18,927.92 / 26,292.64 | incl | listed | – | https://www.tanotis.com/products/te-connectivity-lev100a5ang-contactor-panel-900-vdc-spst-no-1-pole | 2026-09-24 | VERIFIED (listing) |
| EV contactor | TE 2071583-2 (flange, 1 kV, SPST-NO-DM) | tanotis.com | 7,732.84 | incl | listed | rating not in title | https://www.tanotis.com/products/te-connectivity-2071583-2-contactor-flange-1-kv-spst-no-dm-1-pole | 2026-09-24 | VERIFIED (listing) |
| Low-cost EV contactor (Albright SW80/SW180, Hongfa HFE18V, "ZJW100A" style) | – | none found on readable Indian retail sites; IndiaMART search is JS-only; web-search budget exhausted | – | – | – | – | – | 2026-09-24 | NOT FOUND (manual IndiaMART check needed) |
| DC SSR | "5-60V SSR-100DD" (Fotek-style) | ElectronicsComp | 798 (→941.64) | excl | 1 | **Not recommended as a main switch.** These modules are widely counterfeited or over-rated. | https://www.electronicscomp.com/5-60v-ssr-100dd-solid-state-relay | 2026-09-24 | VERIFIED |
| Industrial contactors | Schneider TeSys LC1D… (AC-3 ratings, DC coil) | Moglix | 2,379–67,999 | incl | listed | **Not suitable** for breaking a 48 V / 100 A DC battery load (AC-rated contacts) | https://www.moglix.com/schneider-tesys-25a-24vdc-4-pole-d-model-dc-control-power-contactor-lc1dt25bd/mp/msne5n8l0ygykl | 2026-09-24 | VERIFIED (listing) |

### 4c. Fuses and holders (mind the voltage rating)

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| ATO blade 58 V | Littelfuse 0891030.NXS 30 A 58 V / 0891020.NXS 20 A 58 V | tanotis.com | 87.96 / 89.78 | incl + duty | available | **58 V rating, suits a 13S (54.6 V) bus** | https://www.tanotis.com/products/littelfuse-0891030-nxs-auto-blade-fuse-30a-58v | 2026-09-24 | VERIFIED |
| ATO blade 58 V | Littelfuse 0997005/010/020.WXN 58 V | tanotis.com | 147–165 | incl | available | – | https://www.tanotis.com/products/littelfuse-0997010-wxn-auto-blade-fuse-10a-58v | 2026-09-24 | VERIFIED |
| Blade holder 58 V | Littelfuse HLJC1001G J-case holder 58 V 40 A | tanotis.com | 2,086.86 | incl | available | – | https://www.tanotis.com/products/littelfuse-hljc1001g-fuse-holder-automotive-blade-1-pos-jcase-58v-40a-wire-leaded | 2026-09-24 | VERIFIED |
| Bolt-down 58 V | Littelfuse 142.5631.5502 BF1 50 A 58 V (MIDI-size) | tanotis.com | 686.81 | incl | available | time delay | https://www.tanotis.com/products/littelfuse-142-5631-5502-fuse-automotive-time-delay-50-a-58-v-41-6mm-x-12mm-8mm-bf1-series | 2026-09-24 | VERIFIED |
| MIDI holder | Littelfuse 04980900ZXT panel / 04980921GXM5 in-line (MIDI/BF1) | tanotis.com | 1,757 / 1,268.45 | incl | available | holder is 32 V labelled; use with 58 V BF1 per Littelfuse pairing (check datasheet) | https://www.tanotis.com/products/littelfuse-04980900zxt-fuseholder-panel-mount-200a-midi-reg-bf1-stud-bolt-down-cover | 2026-09-24 | VERIFIED |
| MIDI 32 V | Littelfuse 0498080.H 80 A / 0498030.M 30 A | tanotis.com | 519.57 / 424.80 | incl | available | **32 V: 24 V bus only** | https://www.tanotis.com/products/littelfuse-0498080-h-fuse-automotive-80-a-midi-498-series-time-delay-32-v-41mm-x-12mm-x-8-3mm | 2026-09-24 | VERIFIED |
| MEGA 32 V | Littelfuse 0298150–0298500 + holder 02981001ZXT | tanotis.com | 993–1,861; holder 3,080 | incl | available | **32 V: 24 V bus only**, and oversized for JX1 | https://www.tanotis.com/products/littelfuse-0298150-zxeh-fuse-automotive-bolt-down-150-a-mega-298-series-time-delay-32-v-68-58mm-x-16-2mm-x-10-67mm | 2026-09-24 | VERIFIED |
| ANL | Eaton Bussmann ANL-50 (80 V) | tanotis.com | 21,052.35 | incl | listed | absurd price (pack qty?); not recommended | https://www.tanotis.com/products/eaton-bussmann-series-anl-50-fuse-50a-80v-non-time-delay | 2026-09-24 | VERIFIED (listing) |
| Car blade (32 V) | ATO 3–40 A, 2-pc packs | ElectronicsComp | 12–14 | excl | listed | 32 V: 24 V bus only | https://www.electronicscomp.com/30-amp-car-blade-fuse-india | 2026-09-24 | VERIFIED (listing) |
| Car blade (32 V) | Littelfuse 0287010.PXCN 10 A 32 V | Quartz | 19 | n/s | available | 32 V | https://quartzcomponents.com/products/littelfuse-automotive-fuse-32v-1ka-blade-fuse-10a-rohs | 2026-09-24 | VERIFIED |
| In-line holder | 30 A inline fuse holder with 12 AWG 200 mm | lionbattery.in | 161.02 | excl | 4 | ATO type | https://lionbattery.in/shop/shop/batteries-accessories/connectors/30a-inline-fuse-holder-with-12awg-wire-200mm-heavy-duty-fuse-cable/ | 2026-09-24 | VERIFIED |
| Class-T / MRBF | – | not found | – | – | – | – | – | 2026-09-24 | NOT FOUND |

### 4d. Pre-charge resistors / inrush

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| WW resistor | 22 Ω 10 W wire-wound (33 Ω, 220 Ω, 1 k also listed ₹15–19) | ElectronicsComp | 19 | excl | 2,247 | 10 W | https://www.electronicscomp.com/22ohm-10watt-wire-wound-resistor | 2026-09-24 | VERIFIED |
| Ceramic WW | 50 Ω 5 W axial ceramic | olelectronics.in | 10 | n/s | In stock | – | https://olelectronics.in/product/50e-5w-resistors/ | 2026-09-24 | VERIFIED |
| Resistor | 100 Ω 2 W (pack of 4) | Quartz | 22 | n/s | available | 2 W | https://quartzcomponents.com/products/100-ohm-2-watt-resistor | 2026-09-24 | VERIFIED |
| NTC inrush | 5D-11 MF72; 47D-15 | Quartz | 9 / 15 | n/s | available | – | https://quartzcomponents.com/products/ntc-5d-11-5-ohm-mf72-power-direct-heat-type-negative-temperature-coefficient-thermistor | 2026-09-24 | VERIFIED |

Pre-charge example (ESTIMATED): C_bus = 2,000 µF at 54.6 V holds ½CV² ≈ 3.0 J, which the resistor must absorb. With R = 22 Ω, τ = RC = 44 ms and 5τ ≈ 0.22 s. The peak is 54.6/22 ≈ 2.5 A (136 W for a few ms), which a 10 W wire-wound body tolerates as a pulse.

### 4e. TVS diodes and bulk capacitors

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| TVS | SMBJ58A 600 W | Evelta | 4.48 | excl | listed | 58 V stand-off | https://evelta.com/smbj58a-58v-600w-esd-suppressor-tvs-diode-2pin-smb-do-214aa/ | 2026-09-24 | VERIFIED (listing) |
| TVS | SMCJ58A 1500 W | Evelta | 8.20 | excl | listed | – | https://evelta.com/smcj58a-58v-1500w-esd-suppressor-tvs-diode-2pin-smc-do-214ab/ | 2026-09-24 | VERIFIED (listing) |
| TVS | SMBJ100CA | Evelta | 20.42 | excl | listed | bidirectional 100 V | https://evelta.com/smbj100ca-tvs-diode-esd-protection-100vwm-162vc-do-214aa/ | 2026-09-24 | VERIFIED (listing) |
| TVS | Vishay SMBJ58A / SM8S58CA (DO-218, load-dump class) | tanotis.com | 58.69 / 725.25 | incl | available | – | https://www.tanotis.com/products/vishay-sm8s58cahm3-i-tvs-diode-par-sm8s-series-bidirectional-58-v-93-6-v-do-218ab-2-pins | 2026-09-24 | VERIFIED |
| Bulk cap | 470 µF 100 V electrolytic | ElectronicsComp | 28 | excl | 225 | use on a 48 V bus | https://www.electronicscomp.com/470uf-100v-electrolytic-capacitor-india | 2026-09-24 | VERIFIED |
| Bulk cap | Samwha 1000 µF 63 V 16×25 mm | Evelta | 18.50 | excl | listed | 63 V is marginal on 54.6 V | https://evelta.com/1000uf-63v-electrolytic-capacitor/ | 2026-09-24 | VERIFIED (listing) |
| Bulk cap | 1000 µF 63 V radial | Quartz / EC | 23 / 19 | n/s / excl | available | – | https://quartzcomponents.com/products/1000-%C2%B5f-63v-radial-electrolytic-capacitor-through-hole-package | 2026-09-24 | VERIFIED |

---

## 5. CONVERSION (DC-DC)

### 5a. Isolated / branded

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| Isolated DC-DC | **Mean Well DDR-60L-5** | IndustryBuying | 4,247 (3,599 + 18 %) | incl | InStock, ships within 15 days | 5 V 10.8 A; L = 18–75 V input (covers 6S–13S) | https://www.industrybuying.com/industrial-automation-accessories-mean-well-IND.IND.330812914 | 2026-09-24 | VERIFIED |
| Isolated DC-DC | Mean Well DDR-60L-12 / DDR-60L-24 | IndustryBuying | 4,129 / 4,129 | incl | InStock, 15 d | 12 V 5 A / 24 V 2.5 A | https://www.industrybuying.com/industrial-automation-accessories-mean-well-IND.IND.530812882 | 2026-09-24 | VERIFIED |
| Isolated DC-DC | Mean Well DDR-60G-5 / -12 / -24 | IndustryBuying | 4,247 / 4,129 / 4,129 | incl | InStock, 15 d | G = 9–36 V input (24 V bus only) | https://www.industrybuying.com/industrial-automation-accessories-mean-well-IND.IND.230812878 | 2026-09-24 | VERIFIED |
| Isolated DC-DC | Mean Well DDR-120C-12 / DDR-120C-24 | IndustryBuying | 8,377 / 8,259 | incl | InStock, 15 d | 12 V 10 A / 24 V 5 A; C = ~36–72 V class input | https://www.industrybuying.com/industrial-automation-accessories-mean-well-IND.IND.230812623 | 2026-09-24 | VERIFIED |
| Isolated DC-DC | Mean Well DDR-120B-12 / -24 | IndustryBuying | 8,259 / 8,023 | incl | InStock, 15 d | B = 24 V-class input | https://www.industrybuying.com/industrial-automation-accessories-mean-well-IND.IND.530812594 | 2026-09-24 | VERIFIED |
| Isolated DC-DC | Mean Well DDR-240C-24; DDR-30L-5; DDR-15L-5; SD-15C-5; SD-500L-12 | IndustryBuying | 12,979; 3,303; 2,477; 1,887; 20,059 | incl | InStock (15–30 d) | – | https://www.industrybuying.com/industrial-automation-accessories-mean-well-IND.IND.230812834 | 2026-09-24 | VERIFIED |
| Mean Well (other) | SD-25/50/100/200/350 variants listed | IndustryBuying | not priced today | – | – | – | https://www.industrybuying.com/search/?q=mean+well+sd | 2026-09-24 | listing only |
| Mean Well at Evelta / Moglix / Quartz | Evelta search: none; Moglix: none; Quartz: only LRS-100-12 AC SMPS (OOS) | – | – | – | – | – | – | 2026-09-24 | NOT FOUND |
| Isolated DC-DC | Mornsun URF4805QB-100WR3 (quarter-brick) | ElectronicsComp | 7,549 | excl | 3 | 18–75 V in, **5 V 20 A (100 W)**, 94 % efficiency, 2250 VDC isolation | https://www.electronicscomp.com/urf4805qb-100wr3-mornsun-48v-to-5v-dc-dc-converter-100w-power-supply-module-five-sided-metal-shielded-package | 2026-09-24 | VERIFIED |
| Isolated DC-DC | Mornsun URB4805LD-30WR3 / URB4812LD-30WR3 | ElectronicsComp | 2,249 (OOS) / 2,199 | excl | OOS / listed | 18–75 V in, 5 V 6 A / 12 V 2.5 A | https://www.electronicscomp.com/urb4805ld-30wr3-mornsun-48v-to-5v-dc-dc-converter-30w-power-supply-module-horizontal-dip-package | 2026-09-24 | VERIFIED |

### 5b. Non-isolated buck modules (budget)

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| 60 V-in buck | **"48V 36V 24V to 19V 12V 9V 5V 3V" synchronous step-down** | ElectronicsComp | 379 (→447.22) | excl | 8 | **6.5–60 V in**, 1.25–30 V out, 10 A, 97 % max | https://www.electronicscomp.com/48v-36v-24v-to-19v-12v-9v-5v-3v-adjustable-synchronous-step-down-module-car-charging-power-supply | 2026-09-24 | VERIFIED |
| 100 V-in buck | 7Semi LM5164 7–100 V → 5 V 1 A | Robocraze | 548 | incl | Available | logic / aux rail | https://robocraze.com/products/7semi-lm5164-7v-100v-input-to-5v-1a-output-dc-dc-buck-converter | 2026-09-24 | VERIFIED |
| 80 V-in buck | XL7015 5–80 V in, 0.8 A | Robokits / Quartz / Robocraze | 96 ex / 64 / 81 | – | listed / avail / avail | low current | https://robokits.co.in/power-supply/dc-dc-power-supply/xl7015-dc-dc-step-down-voltage-converter-0.8a-input-5v-80v-output-5v-20v | 2026-09-24 | VERIFIED |
| 53 V-in buck | LM2596HV 4.5–53 V, 3 A | Robokits | 66 | excl | listed | **53 V max is below the 54.6 V 13S full charge; 12S at most** | https://robokits.co.in/power-supply/dc-dc-power-supply/step-down-lm2596hv-dc-dc-adjustable-voltage-regulator-4.5-53v-input-and-3a-output | 2026-09-24 | VERIFIED |
| 5 V 5 A (24 V bus) | 7Semi AP64500 7–40 V → 5 V 5 A | Robocraze | 823 | incl | Available | – | https://robocraze.com/products/7semi-dc-dc-buck-converter-7v-40v-input-to-5v-5a-output-ap64500 | 2026-09-24 | VERIFIED |
| 5 V 5 A (24 V bus) | XY-3606 24 V/12 V → 5 V 5 A | Quartz / Robocraze / EC / IHC | 137 / 159 / 139 ex / 199 | – | available | ≤ ~36 V input class | https://quartzcomponents.com/products/24v-12v-to-5v-5a-step-down-power-supply-buck-converter-xy-3606-power-convertor | 2026-09-24 | VERIFIED |
| 5 V 4 A | DFRobot 7–24 V → 5 V 4 A (20 W) | Robocraze | 555 | incl | Available | – | https://robocraze.com/products/dfrobot-20w-dc-dc-buck-converter-power-module-7-24v-to-5v-4a | 2026-09-24 | VERIFIED |
| 5 V 5 A | Mini560 5 V 5 A | Quartz / Robokits | 65 / 92 ex | – | avail / "sold out?" | – | https://quartzcomponents.com/products/mini560-dc-dc-step-down-stabilized-voltage-module | 2026-09-24 | VERIFIED |
| XL4016 (≤40 V in) | XL4016E1 8–12 A 200–300 W | Robocraze 180; Quartz 229 / 251; Robokits 268 ex; lionbattery 338.14 ex (8 pcs) | – | – | available | 4/5–40 V in: **24 V bus only** | https://robocraze.com/products/xl4016e1-dc-4-40v-to-dc-1-25-36v-8a-buck-converter-voltage-regulator-36v-24v-12v-to-5v | 2026-09-24 | VERIFIED |
| 20 A buck | 300 W 20 A CC/CV buck | ElectronicsComp 325 ex (210 pcs); IHC 399; Quartz 458; lionbattery 483.05 ex | – | – | available | 1.2–36 V out; typically ≤40 V in | https://www.electronicscomp.com/300w-20a-dc-dc-buck-converter-step-down-module-constant-current-led-driver-module | 2026-09-24 | VERIFIED |
| LM2596 (low current) | LM2596 3 A module | Quartz 45; Robocraze 48; Robokits 45 ex | – | – | available | ≤40 V in | https://quartzcomponents.com/products/lm2596-buck-converter-power-supply-module | 2026-09-24 | VERIFIED |

**Jetson notes (ESTIMATED / engineering):**
- **Jetson Nano, 5 V 4 A barrel:**
  - 24 V bus: AP64500 5 V 5 A (₹823).
  - 48 V bus: Mean Well DDR-60L-5 (₹4,247, isolated, 10.8 A headroom) or Mornsun URF4805QB (20 A).
  - Budget: the EC 60 V synchronous buck set to 5.1 V.
- **Orin at 19 V:** no fixed-19 V Mean Well DDR model was found. Use the EC 6.5–60 V 10 A adjustable buck set to 19 V (190 W theoretical at 10 A; derate to ≤50 % for a hot enclosure), or check the Orin carrier's actual input range before choosing 12 V or 24 V rails.
- **Hobby buck modules have no input TVS and no UVLO worth the name.** Add an SMBJ58A plus bulk capacitance at the module input on a 48 V bus. Motor regen spikes can exceed 60 V.

---

## 6. CONNECTORS, WIRE, SIGNAL CABLING, CHARGERS

### 6a. Power connectors (Amass originals at Robokits; all prices excl GST)

| Item | Model | Price ₹ | Stock | URL | Evidence |
|---|---|---|---|---|---|
| XT30 M / F / pair | XT30-M / XT30-F / XT30-F/M | 22 / 20 / 41 | XT30-M **Pre Order** | https://robokits.co.in/batteries-chargers/accessories/plugs-and-connectors/amass-xt30-male-and-female-connector-original-xt30-f-m | VERIFIED |
| XT60 M / pair / XT60H pair | XT60-M / XT60 pair / XT60H-M/F | 27 / 54 / 65 | XT60H pair "Ships Within 15 Days" | https://robokits.co.in/batteries-chargers/plugs-and-connectors/amass-xt60h-male-female-connector-with-housing | VERIFIED |
| XT60E-M panel mount | – | 45 | listed | https://robokits.co.in/batteries-chargers/accessories/plugs-and-connectors/amass-xt60e-m-mountable-xt60-male-plug | VERIFIED (listing) |
| XT90 pair / with housing | – | 108 / 120 | listed | https://robokits.co.in/batteries-chargers/plugs-and-connectors/xt90-connectors-male-female-pair | VERIFIED (listing) |
| **XT90-S anti-spark pair** | XT90S-M/F-H | 180 | In Stock | https://robokits.co.in/batteries-chargers/plugs-and-connectors/amass-xt90s-anti-spark-connectors-male-female-pair-original | VERIFIED |
| XT90-S female with wire | – | 259 | In Stock | https://robokits.co.in/batteries-chargers/accessories/plugs-and-connectors/amass-xt90-s-female-connector-with-wire-original | VERIFIED |
| AS150 anti-spark pair (red + black) | – | 770 | In Stock | https://robokits.co.in/batteries-chargers/accessories/plugs-and-connectors/amass-as150-anti-spark-self-insulating-gold-plated-bullet-connector-pair-red-black-original | VERIFIED |
| AS150U M+F | – | 733 | listed | https://robokits.co.in/multirotor-spare-parts/plug-and-connectors/amass-as150u-male-and-female-connector-original | VERIFIED (listing) |
| MR30 M / F (3-pin motor) | MR30-M / MR30-FB | 33 / 28 | MR30-M In Stock | https://robokits.co.in/batteries-chargers/plugs-and-connectors/amass-mr30-m-male-3pin-original-connector | VERIFIED |
| XT60 set (Amass), lionbattery | – | 76.27 ex | 37 | https://lionbattery.in/shop/shop/batteries-accessories/xt60-connector-set-amass-c453/ | VERIFIED |

### 6b. Silicone wire (per metre)

| Gauge | Quartz (n/s GST) | Indian Hobby Center (incl) | Robokits (excl) | lionbattery (excl) | Evidence |
|---|---|---|---|---|---|
| 8 AWG | 230 (red / black) | – | 219 (sold-out flag) | – | VERIFIED |
| 10 AWG | 215 | 199 | 126 (sold-out flag) | 127.12 (17 in stock) | VERIFIED |
| 12 AWG | 136–138 | 139 (125 single-strand) | 82–85 | 101.69 | VERIFIED |
| 14 AWG | 103–105 | 89 | 47 | – | VERIFIED |
| 16 AWG | 56–68 | 70–79 | – | 63.56 | VERIFIED |
| 18 AWG | 35–40 | 59 (65 braided) | – | 61.02 | VERIFIED |
| 20 AWG | – | 49 (2-core 125; 4-core 185) | – | – | VERIFIED |

URLs:
- https://quartzcomponents.com/products/10awg-silicone-wire-black-1-meter-high-quality-ultra-flexible-for-battery-packs
- https://indianhobbycenter.com/products/10-awg-silicone-wire-black-ultra-high-quality-super-flexible-1-meter
- https://robokits.co.in/silicone-wires/super-flexible-high-temp-grade/high-temperature-super-flexible-grade-silicone-wire-12awg-1-meter-red
- https://lionbattery.in/shop/shop/batteries-accessories/silicone-wire-10awg-black-6sqmm-14d3/

### 6c. Signal connectors, CAN cable, heat-shrink, sleeving, drag chain

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | URL | Evidence |
|---|---|---|---|---|---|---|---|
| JST-GH cable | JST GHR-06V 6-pin 1.25 mm 15 cm | Evelta | 25 | excl | listed | https://evelta.com/jst-ghr-06v-cable-6pin-1-25mm-pitch-female-connector-15cm/ | VERIFIED (listing) |
| JST-GH header | SM11B-GHS-TB 11-pin SMT | Evelta | 21 | excl | listed | https://evelta.com/11pin-1-25mm-pitch-shrouded-header-connector/ | VERIFIED (listing) |
| JST-GH cable | SparkFun GHR-04V to GHR-06V 100 mm | Evelta | 165 | excl | listed | https://evelta.com/sparkfun-jst-ghr-04v-to-jst-ghr-06v-cable-100mm/ | VERIFIED (listing) |
| JST-XH | 2–8-pin male ₹2–5; F-F leads ₹13–49 | Quartz / IHC | 2–49 | – | available | https://quartzcomponents.com/products/4-pin-jst-sm-connector-with-wire-5-24mm-pitch | VERIFIED |
| Molex Micro-Fit 3.0 | 43025-0200 (2-way) / 43025-0410 (4-way) / 43645-0400 (1-row 4-way) / 43025-1000 (10-way) | tanotis.com | 41.59 / 63.92 / 44.53 / 78.45 | incl + duty | available | https://www.tanotis.com/products/molex-43025-0410-connector-housing-micro-fit-3-0-43025-series-receptacle-4-ways-3-mm | VERIFIED (terminals not priced; buy 43030 crimps separately) |
| CAN twisted pair | no dedicated CAN cable found. Nearest options: Cat5e patch 3 m (Quartz ₹67), 2-core twisted 1 mm² (Quartz ₹28/m, power not CAN), HELUKAT LAN cable (IB) | – | – | – | – | https://quartzcomponents.com/products/high-speed-cat-5e-ethernet-lan-network-cable-3-meter | VERIFIED (substitute) |
| Heat-shrink | WOER 5 mm (2 m) 17; 8 mm 24; 16 mm 29; 40 mm 91–115 | Robokits | ex | – | listed | https://robokits.co.in/heat-shrink-tubes/hst-11-mm-and-above/heat-shrink-sleeve-40mm-black-1-meter-premium-quality-industrial-grade-woer-hst | VERIFIED (listing) |
| Pack PVC sleeve | 61–480 mm flat PVC, per m | lionbattery (17.8–203 ex) / Quartz (23–89) | – | – | available | https://quartzcomponents.com/products/130mm-pvc-heat-shrink-sleeve-for-lithium-battery-pack-1-meter | VERIFIED |
| Braided sleeving | Raychem VERSAFLEX-1/8 expandable, per m | IndustryBuying | 330 (280 + GST) | incl | InStock, 30 d | https://www.industrybuying.com/industrial-automation-accessories-raychem--te-connectivity-IND.IND.930858668 | VERIFIED |
| Spiral wrap | PVC 6 / 9 / 12 mm per m | Quartz / IHC | 8–19 | – | available | https://quartzcomponents.com/products/spiral-12mm-1-2 | VERIFIED |
| Drag chain | 10×10 mm / 15×20 / 25×38 per m, with ends | Robokits | 215 / 356 / 623 | excl | listed | https://robokits.co.in/3d-printer/accessories/cable-drag-chain-wire-carrier-with-end-connectors-10x10mm-1meter | VERIFIED (listing) |
| Drag chain | Dehmy 18×25 mm 1 m | Moglix | 1,059 | incl | listed | https://www.moglix.com/dehmy-1m-18x25mm-black-heavy-duty-cnc-cable-drag-chain/mp/msne5n8m1vxykl | VERIFIED (listing) |

### 6d. Chargers

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Evidence |
|---|---|---|---|---|---|---|---|---|
| 6S balance | ToolKitRC M6D 500 W 25 A 1–6S dual DC | Indian Hobby Center | 7,999 | incl | Available | needs DC PSU | https://indianhobbycenter.com/products/toolkitrc-m6d-500w-25a-1-6s-dc-dual-smart-charger | VERIFIED |
| 6S balance | ISDT P30 1500 W 50 A 8S dual | Robokits | 16,697 | excl | listed | "Original" | https://robokits.co.in/batteries-chargers/chargers/isdt-premium-chargers-original/isdt-p30-1500w-50a-8s-dual-port-smart-charger-original | VERIFIED (listing) |
| 6S balance | ISDT Air8 500 W 8S / ISDT P20 1000 W | IHC | 6,649 / 11,999 | incl | **Out of stock** | – | https://indianhobbycenter.com/products/isdt-air8-500-w-dc-pocket-charger-20-a-1-channel-supports-1-8s-lipo-life-lihv-ulihv-nimh-pb | VERIFIED |
| 6S balance | SkyRC B6neo 200 W (PD input) | IHC | 3,999 | incl | **Out of stock** | – | https://indianhobbycenter.com/products/skyrc-b6neo-200w-single-channel-dc-lipo-life-liion-lihv-nimh-nicd-pb-smart-charger-with-pd-input-crimson-sky | VERIFIED |
| 6S balance | IMAX B6 80 W / B6AC | Quartz 1,719 / 2,250; IHC 1,825 / 2,499; Robocraze 1,948 / 2,351; Robokits 1,258 / 2,285 ex | – | – | available | 80 W is slow for a 200 Wh pack (about 2.5 h+); IMAX B6 units are widely cloned | https://quartzcomponents.com/products/imax-b6-80w-6a-charger-discharger-1-6-cells | VERIFIED |
| 4S only | ISDT PD60 1–4S USB-C | Robokits 1,624 ex / IHC 2,299 | – | – | – | **not 6S** | https://robokits.co.in/batteries-chargers/chargers/isdt-premium-chargers-original/isdt-pd60-60w-6a-1-4s-usb-c-input-battery-charger-original | VERIFIED |
| HOTA 6S chargers | – | not found | – | – | – | – | – | NOT FOUND |
| 6S CC/CV | 25.2 V 3 A / 25.2 V 5 A table-top | Quartz | 1,633 / 2,673 | n/s | available | CC/CV | https://quartzcomponents.com/products/25-2v-5a-lithium-ion-battery-charger-for-18650-26700-nmc-battery-pack-table-top-126w-with-cc-and-cv | VERIFIED |
| 7S CC/CV | WATTNINE 29.4 V 5 A (147.5 W) | Quartz | 1,988 | n/s | available | – | https://quartzcomponents.com/products/wattnine-29-5v-5a-lithium-ion-battery-charger-for-7s-nmc-battery-pack-147-5w-table-top-charger-with-cc-cv | VERIFIED |
| 10S CC/CV | WATTNINE 42 V 3.5 A (147 W) | Quartz | 1,949 | n/s | available | – | https://quartzcomponents.com/products/wattnine-42v-3-5a-lithium-ion-battery-charger-for-10s-nmc-battery-pack-147w-table-top-charger-with-cc-amp-cv | VERIFIED |
| 13S CC/CV | 54.6 V 6 A e-scooty charger, fan, aluminium case | Quartz | 3,315 | n/s | available | – | https://quartzcomponents.com/products/54-6v-6a-e-scooty-battery-charger-for-48v-nmc-lithium-battery-pack-aluminium-casing | VERIFIED |
| 12S (50.4 V) CC/CV | – | not found | – | – | – | – | – | NOT FOUND |

---

## 7. BATTERY SAFETY CONSUMABLES AND TOOLS

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Evidence |
|---|---|---|---|---|---|---|---|---|
| LiPo bag | Fire / water-resistant 215×165×120 mm | ElectronicsComp | 821 | excl | **Out of stock** | – | https://www.electronicscomp.com/large-space-fire-and-water-resistant-lipo-battery-bag-215mm-x-165mm-x-120mm | VERIFIED |
| LiPo bag | Fire / water-resistant 26×18×13 cm | Quartz | 785 | n/s | **Out of stock** | – | https://quartzcomponents.com/products/large-space-fire-and-water-resistant-lipo-battery-bag-26x18x13cm | VERIFIED |
| Fire box | Lithium Safe Battery Box 300×200×200 mm | lionbattery.in | 24,000 | excl | in stock | fireproof container | https://lionbattery.in/shop/shop/battery-box/lithium-safe-battery-box-300x200x200mm-fireproof-storage-container/ | VERIFIED |
| Cell fuse wire | – | not found in readable Indian stores | – | – | – | – | – | NOT FOUND |
| Pure nickel strip | 8×0.15 mm / 12×0.15 mm / 6×0.15 mm, per m | Quartz | 85 / 105 / 90 | n/s | available | pure Ni | https://quartzcomponents.com/products/nickel-strip-pure-18650-8mm-thickness-0-15mm | VERIFIED |
| Pure nickel H-strip | 27×0.15 mm 2P (18650); 49.5×0.20 mm (32650/32700) | Quartz | 294 / 325 per m | n/s | available | – | https://quartzcomponents.com/products/h-shape-27mm-x-0-15mm-pure-nickel-strip-for-18650-cells-1-meter | VERIFIED |
| Plated nickel strip | 0.12×8 mm; 21700 2P 0.15 mm | lionbattery | 21.19 / 46.61 per m | excl | in stock | **Ni-plated steel: much higher resistance, keep it out of the high-current path** | https://lionbattery.in/shop/shop/batteries-accessories/nickel-strip/nickel-strip-plated-21700-2p-battery-pack-0-15mm-heavy-duty-spot-welding-strip/ | VERIFIED |
| Nickel strip (IHC) | 0.15×8 mm; 2P 0.12×31 mm for 21700 | Indian Hobby Center | 49 / 85 | incl | available | type (pure or plated) not stated | https://indianhobbycenter.com/products/nickel-strip-2p-0-15x30mm-nickel-strip-for-2700-lithium-battery | VERIFIED |
| Spot welder | FNIRSI SWM-10 portable | Quartz | 4,580 | n/s | available | hobby grade | https://quartzcomponents.com/products/fnirsi%C2%AE-swm-10-portable-intelligent-color-screen-spot-welding-machine | VERIFIED |
| Spot welder | 3.5 kVA LS-A200 / 3 kVA SP-3 / 4 kVA (dual pen + pedal) | Quartz | 14,610 / 14,650 / 19,049 | n/s | available | AC transformer type | https://quartzcomponents.com/products/3kva-lsp-a40-portable-lithium-cell-spot-welding-machine-for-battery-pack-includes-double-pen-and-pedal | VERIFIED |
| Spot welder | Glitter 801A / 801B + 70B; Sunkko 709A | lionbattery.in | 13,220.34 / 16,525.42 / 24,152.54 | excl | in stock | – | https://lionbattery.in/shop/shop/spot-welding-machine/spot-welding-machine-glitter-801a-7af6/ | VERIFIED |
| Spot welder | S737G double-pulse / Mechanic PN360 | Indian Hobby Center | 17,999 / 7,500 | incl | Available | – | https://indianhobbycenter.com/products/intelligent-precision-pulse-spot-welding-machine-s737g | VERIFIED |
| Insulation | Barley / fish paper 65 mm per m; 18650 / 32700 insulator rings (10k); Kapton 50 mm; fibreglass tape | lionbattery.in | 25.42; 42.37; 254.24; 186.44 | excl | in stock | – | https://lionbattery.in/shop/shop/batteries-accessories/adhesive-tapes/barley-insulation-paper-65mm-1-meter/ | VERIFIED |
| Capacity tester | ZB2L3 (1.2–12 V) | Robokits 163 ex / ThinkRobotics 349.99 | – | – | listed | single-cell testing | https://robokits.co.in/batteries-chargers/accessories/charge-protection-circuit/zb2l3-18650-battery-capacity-tester-external-load-discharge-type-1.2-12v | VERIFIED |
| Test service | Battery Pack / BMS Testing Service | lionbattery.in | 1,694.92 | excl | – | – | https://lionbattery.in/shop/battery-testing-reports/battery-pack-bms-testing-services/ | VERIFIED |

---

## 8. ENGINEERING NOTES (with sources)

### 8.1 Cell internal resistance: typical values (sourced)

| Cell | Figure | Source |
|---|---|---|
| Molicel P45B | Max DC IR **13.8 mΩ (10 A / 10 s)**; 45 A max discharge; 242 Wh/kg; 13.5 A continuous charge; 184 W 10 s pulse @90 % SOC | https://www.molicel.com/inr-21700-p45b/ (WebFetch 2026-09-24) |
| Molicel P50B | 60 A continuous with 80 °C cut-off; "12.8 mΩ" impedance | https://www.molicel.com/inr-21700-p50b/ (WebFetch 2026-09-24) |
| Molicel P42A | P45B has "22 % lower DCR than P42A". Implied P42A DCR ≈ 13.8 / 0.78 ≈ 17.7 mΩ (ESTIMATED; Molicel P42A page returned 404) | Robokits P45B listing copy; molicel.com |
| Molicel P30B (18650) | Typical DC IR 17 mΩ @50 % SOC; AC 8 mΩ @30 % SOC; 30 A cont. (80 °C cut-off), 36 A max | Robokits listing (datasheet copy) |
| Samsung 50S | 25 A continuous without temperature cut-off / 45 A with 80 °C cut-off; one buyer measured 9.97 mΩ at 1 kHz | Robokits listing and review |
| LithiumWerks ANR26650M1B (LFP) | <10 mΩ @1 kHz typical; 52 A continuous, 120 A 10 s pulse | IHC listing (datasheet copy) |
| GenX Molicel 6S2P pack | Vendor-stated "IR 4.75 mΩ". That is implausible for 6S2P built from ~14–18 mΩ cells (expected ≈ 6 × 16 / 2 ≈ 48 mΩ plus interconnects), so treat it as marketing | Robokits listing |

- **AC (1 kHz) IR is roughly half of the 10 s DC IR.** Always design sag and heat from DC IR.
- IR rises with age and cold: "heat lowers it and cold raises it" (Battery University BU-802a, https://batteryuniversity.com/article/bu-802a-how-does-rising-internal-resistance-affect-performance).

### 8.2 C-rating realism

- **LiPo C ratings are marketing.** Oscar Liang's LiPo guide calls them "mostly a marketing tool" and says internal resistance is "the biggest factor affecting a battery's maximum discharge rate" (https://oscarliang.com/lipo-battery-guide/).
  - Example: "GenX 6S 5200 mAh 40C / 80C" would mean 208 A continuous / 416 A burst from a 708 g pack, which is not thermally credible.
  - Use measured IR (or the brand's IR spec) plus a temperature-rise budget, not the C number.
- **For 18650/21700 Li-ion, the datasheet continuous rating is usually tied to a temperature cut-off** (Molicel P50B "60 A … cut off at 80 °C"; Samsung 50S "45 A with 80 °C cut"). Without cut-off (i.e. sustained), the 50S is rated 25 A.
  - Indian pack listings multiply cell ratings by P-count (e.g. "6S2P 90 A") without thermal derating.

### 8.3 Derating guidance for JX1 (engineering judgement, ESTIMATED)

- **Continuous design current** ≤ 30–50 % of the cell's cut-off-qualified rating. **Short peaks (<1 s)** up to about 80 %.
  - Example, P45B: 15–22 A continuous per cell, 35 A peak.
  - JX1 at 48 V needs about 8.5 A average and 70 A peak. 13S2P gives 4.3 A average and 35 A peak per cell, which is comfortable.
  - At 24 V the same peak needs about 38 A per cell in 6S4P, or 6S5P+.
- **Heat per cell at peak (13S2P P45B):** I²R = 35² × 0.0138 ≈ 17 W for under 1 s, i.e. about 17 J per event. Negligible on a ~70 g cell (≈0.25 K per event at ~1 J/g·K). The average (4.3 A) gives about 0.26 W per cell.
- **Voltage sag budget:** keep the loaded cell voltage above about 3.0 V at end of discharge, i.e. (V_rest − I·R_dc) > 3.0 V.
  - With 0.48 V sag at 35 A, the usable window ends near 3.5 V rest. Usable energy is therefore about 80–85 % of nameplate.
  - Battery University notes that heavy loads warrant lowering the end-of-discharge cut-off (e.g. to 2.70 V per cell for Li-manganese) to allow for sag (BU-501, https://batteryuniversity.com/article/bu-501-basics-about-discharging).
- **Wire, fuse and switch are sized for peak and duration, not average.** 48 V halves every current, and also halves the cost of the BMS, fuses, connectors and anti-spark hardware (see 2d).
- **Fuse voltage matters.** Standard ATO, MIDI and MEGA automotive fuses are 32 V parts, acceptable only on a 24 V (6S/7S) bus. On 10S–13S (42–54.6 V) use 58 V-rated parts (Littelfuse 58 V ATO or BF1/BF2, listed in 4c) or 80 V ANL-class.
- **Capacitors and TVS:** a 13S bus plus regen needs ≥80–100 V caps (EC 470 µF 100 V) and a TVS with stand-off above 54.6 V (SMBJ58A / SMCJ58A: stand-off 58 V, clamp about 93 V).

### 8.4 BIS certification and transport (India)

**Observed on pages today:**
- **Robokits:** P50B and P42A pages say "*Please do not select air shipping for battery as the same is not permitted by airline regulations*". Expect surface courier (slower) for all cells and packs.
- **BIS marking and registration claims seen:**
  - Zbotic P42A listing URL: "…lithium-ion cell IS 16046 (Part 2) R-41137189…".
  - ThinkRobotics: "18650 Li-Ion Battery … – BIS Certified".
  - Quartz 32700 LFP: "It is also BIS certified".
  - IndiaMART Molicel lead: "UN, BIS certified".

**Background, not re-verified today (crsbis.in returned no content; meity.gov.in returned 403):**
- Portable secondary Li-ion cells and batteries fall under MeitY's Compulsory Registration Scheme with BIS (standard IS 16046 Part 2 for lithium systems; registration numbers in the format R-xxxxxxxx). Importers and sellers of covered cells should hold a registration.
- Air transport of Li-ion follows IATA DGR:
  - UN3480 for cells or batteries alone; UN3481 when packed with or contained in equipment.
  - UN38.3 test summary required.
  - Stand-alone Li-ion shipped at ≤30 % SOC (cargo aircraft).
  - The IATA web page checked today (https://www.iata.org/en/programs/cargo/dgr/lithium-batteries/) points to the Battery Guidance Document but did not itself state these numbers.
- **Action:** verify each cell supplier's R-number on the BIS CRS portal before volume purchase.

### 8.5 Storage and charging safety

- LiPo storage at 3.80–3.85 V per cell. Charge at ≤1C. Full charge is 4.2 V (LiHV 4.35 V). LiPo bags "slow down" fires rather than contain them; metal boxes are preferred (Oscar Liang guide, above).
- Both LiPo bags in stock-checked stores were **out of stock** today. Lionbattery sells a ₹24k fire box.

---

## 9. Gaps and next actions

1. **Low-cost sealed EV contactor (Albright / Hongfa / Chinese 48–72 V, 100 A):** no verified Indian retail listing today (IndiaMART is JS-only and the web-search budget was exhausted). Options: check e-rickshaw parts dealers on IndiaMART by hand, or use the Flipsky anti-spark switch plus E-stop-driven enable.
2. **Genuine Samsung/LG:** request invoices or authorised-distributor proof, and consider TME India (blocked today) for SDI 50S. Test incoming cells (weight, 1 kHz IR, 10 A DCR, capacity).
3. **Molicel via The Battery World:** confirm GST basis, MOQ and date code for a 30–60-cell order. It is the only authorised channel whose prices were verified today.
4. **Not checked by design:** Robu.in and Amazon.in, which carry Orange, Gens Ace, CNHL and many anti-spark modules (a separate agent covers these).
5. **Mean Well:** IndustryBuying shows about 15-day dispatch. Get a quote from Mean Well's Indian distributor if quantity exceeds about 5.
