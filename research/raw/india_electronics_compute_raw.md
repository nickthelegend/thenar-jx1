# JX1 – India electronics sourcing & compute-architecture research (RAW)

- Project: JX1 low-cost compact humanoid (~1.2 m, 20–24 BLDC/servo joints on CAN), built in India at lowest practical cost.
- Scope: Part A Indian sourcing (prices/stock), Part B Jetson Nano feasibility, Part C CAN vs CAN-FD bus budget.
- Date of every check: **2026-09-24**. Status: RAW research notes (v2, complete). Not a BOM decision.

## 0. Method, labels, store conventions

**Evidence labels**
- **VERIFIED** – value seen today (2026-09-24) on the supplier's/manufacturer's own page or JSON (URL given).
- **ESTIMATED** – derived by calculation; math shown (e.g. ex-GST x 1.18).
- **UNVERIFIED** – not seen on a primary page today (memory, inference, page silent, or site blocked).

**How data was pulled (read-only; no accounts, carts, forms or binary downloads)**
- Shopify stores (thinkrobotics.com, robocraze.com, quartzcomponents.com; also official vendor stores shop.odriverobotics.com, mjbots.com, flipsky.net, openlightlabs.com): `/search/suggest.json` and `/products/<handle>.js` (price, `available`, variants). Currency confirmed from page `Shopify.currency`: INR for the 3 Indian stores, USD for the 4 vendor stores.
- WooCommerce (zbotic.in, sharvielectronics.com): public Store API `/wp-json/wc/store/v1/products?search=`.
- evelta.com (BigCommerce): search page + product-page JSON (`with_tax`, `without_tax`, `stock`, `instock`, `stock_message`).
- electronicscomp.com, hubtronics.in (OpenCart), robokits.co.in (Zen Cart): search HTML + product pages.
- probots.co.in (Magento 2): public GraphQL `products(search:)` for price; product page for stock.
- ~155 search terms x 10 stores. Raw JSON of every query is in the session scratchpad (`scratchpad/r4/raw/`), not in the repo.
- Blocked/unreadable today: mouser.in ("Access to this page has been denied"), lcsc.com search (Akamai 403 / JS-only), st.com (timeouts), microchip.com (403). robu.in/amazon.in/element14/digikey excluded by brief (covered by another agent).

**GST convention per store (as the store states it)**

| Store | Listed price is | Evidence |
|---|---|---|
| thinkrobotics.com | incl. GST | VERIFIED – ToS: "All products and services show prices, including all the taxes applicable" (https://thinkrobotics.com/policies/terms-of-service) |
| robocraze.com | incl. GST | VERIFIED – product page "Incl. GST (No Hidden Charges)" |
| quartzcomponents.com | not stated | UNVERIFIED – no tax wording on product/FAQ/ToS pages (GST invoice offered) |
| evelta.com | ex. GST (incl. also on product page) | VERIFIED – listing "ex. GST"; product JSON with_tax = without_tax x 1.18 |
| electronicscomp.com | ex. 18 % GST | VERIFIED – product page "Rs.xxx (Excluding 18% GST)" |
| hubtronics.in | incl. GST | VERIFIED – e.g. "₹410.00 … Ex Tax: ₹347.46" |
| probots.co.in | incl. GST | VERIFIED – e.g. "₹3,899.00 = ₹3304.24 + 594.76 GST" |
| zbotic.in | incl. GST | VERIFIED – e.g. "₹293.82 (₹249.00 + GST)" |
| sharvielectronics.com | ex. GST | VERIFIED – "(Excluding All Taxes)" |
| robokits.co.in | ex. GST (inferred) | ESTIMATED – "₹157.00 … GST Input Tax Credit @ 18 % of ₹28.26"; 0.18 x 157 = 28.26 ⇒ GST added on top |

"≈ incl" = ex x 1.18 (ESTIMATED, 18 % slab as applied by Evelta/electronicscomp). Stock: Y / "In stock" / "N in stock" = orderable from stock; OOS = out of stock/sold out; "drop-ship" = page says "Usually Delivered in 2-5 Days" while inventory = 0.

---

## QUICK VIEW – cheapest credible option per category (details + sources in Part A)

| Category | Cheapest credible, in stock today | Price ₹ | Note |
|---|---|---|---|
| Jetson Nano 4GB (complete) | Waveshare JETSON-NANO-DEV-KIT incl. Nano 16 GB-eMMC module + 64 GB TF – ThinkRobotics | 30,899.99 incl | Official NVIDIA B01 kit is EOL / not listed |
| Jetson Nano module only | ThinkRobotics | 23,899.99 incl | + Robocraze carrier ₹6,089 = ₹29,988.99 (ESTIMATED sum) |
| Orin Nano Super Dev Kit (upgrade) | ThinkRobotics | 49,999.99 incl | Quartz lists ₹34,675 but OOS |
| Raspberry Pi 5 (comparison) | 8 GB: ThinkRobotics ₹19,999.99 incl; 4 GB: Probots ₹15,949 incl | – | 4 GB OOS at ThinkRobotics/electronicscomp/Hubtronics |
| STM32 FDCAN dev board | No Nucleo-G431RB/G474RE in stock anywhere checked. In stock: WeAct STM32H743 core (Probots ₹3,999 incl); NUCLEO-H723ZG (Sharvi ₹4,535.63 ex) | – | Cheapest G474RE listing: electronicscomp Rs.1,847 ex (OOS) |
| STM32G4 bare MCU (custom joint PCB) | STM32G431CBT6 – Evelta, 135 in stock | 572.30 incl | 1x FDCAN |
| CAN-FD transceiver | NXP TJA1462AT – Sharvi | 102.36 ex (≈120.78) | 8 Mbit/s SIC |
| Classic transceiver IC | TI SN65HVD230DR – Quartz | 82 | 1 Mbps only |
| MCP2515 module | Robocraze | 134 incl | classic CAN |
| USB-CAN-FD adapter | MKS CANable V2.0 (STM32G431 + TJA1051T/3, candleLight) – Probots | 3,899 incl | 5 Mbit/s data phase (page) |
| 2-CH CAN-FD HAT | Waveshare (MCP2517FD + MCP2562FD) – Hubtronics, 3 in stock | 4,399 incl | – |
| CAN motor driver | ST B-G431B-ESC1 – Evelta ₹2,790.70 incl but **SOLD OUT**; no other Indian listing | – | Import refs: ODESC V4.2 $34.99–43.99, moteus-c1 $69, ODrive Micro $89 |
| FOC driver (no CAN) | SimpleFOCmini – Evelta, 5 in stock | 791.78 incl | 8–30 V, 2.5 A peak |
| Magnetic encoder | AS5600 module – Sharvi | 135.91 ex (≈160) | AS5047P/AS5048A/MT6701/MT6835 boards not found |
| IMU | BNO085 (7Semi Nano) – Evelta, 21 in stock | 1,775 ex (2,094.50 incl) | BNO055 from ₹1,137 ex |
| Camera (Jetson CSI) | IMX219-160 – Hubtronics ₹1,109.20 incl (1 left) / Evelta ₹1,375.88 incl (5); IMX219-77 – ThinkRobotics ₹1,699.99 | – | – |
| Depth camera | Orbbec Gemini E ₹24,499.99; OAK-D Lite ₹31,649.99 (ThinkRobotics, both Y) | – | D435i cheapest listing Rs.34,319 ex (OOS) |
| GbE switch | PUSR USR-SG1005 5-port – ThinkRobotics | 1,549.99 incl | – |
| JST-GH / 120 Ω | Probots JST-GH 4-pin ₹28, 6-pin ₹42; 120 Ω ₹3 | – | Micro-Fit 3.0 not found |

---

## PART A – Indian sourcing tables

### A1. High-level compute (Jetson Nano, Orin Nano upgrade path, Raspberry Pi 5)

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| Jetson Nano 4GB module | NVIDIA Jetson Nano module (SKU SBC1101-MOD) | ThinkRobotics | 23,899.99 (compare-at 18,999.99) | incl | Y | 128-core Maxwell; 4 GB LPDDR4 25.6 GB/s; 16 GB eMMC; 69.6 x 45 mm 260-pin | https://thinkrobotics.com/products/nvidia-jetson-nano-module-online | 2026-09-24 | VERIFIED |
| Jetson Nano 4GB module | NVIDIA Jetson Nano 4GB Module (DVB-QC5769) | Quartz | 17,600 | not stated | OOS | module only | https://quartzcomponents.com/products/nvidia-jetson-nano-4gb-module | 2026-09-24 | VERIFIED |
| Complete Nano kit (cheapest in stock) | Waveshare JETSON-NANO-DEV-KIT, listed as "ThinkRobotics Jetson Nano Dev Kit (SUB)" (SKU SBC1108): B01-alternative carrier + Nano module w/ 16 GB eMMC + 64 GB TF card | ThinkRobotics | 30,899.99 | incl | Y | B01-like I/O | https://thinkrobotics.com/products/thinkrobotics-jetson-nano-dev-kit-sub | 2026-09-24 | VERIFIED |
| Complete Nano kit | Waveshare "Jetson Nano Development Board 4GB with 16GB eMMC" (Expansion Kit Lite + module) | Robocraze | 46,999 | incl | Y | 1x USB 3.2, 2x USB 2.0, CSI, HDMI | https://robocraze.com/products/jetson-nano-development-board-4-gb-16-gb-emmc | 2026-09-24 | VERIFIED |
| Nano mini-PC | Waveshare Jetson Nano Mini Computer (module + metal case) | ThinkRobotics | 34,849.99 (base; WiFi/4G variants OOS) | incl | Y | M.2 B-key, RS485, 2x CSI | https://thinkrobotics.com/products/jetson-nano-mini-computer | 2026-09-24 | VERIFIED |
| Nano carrier only | Waveshare JETSON-IO-BASE-A ("Alternative of B01 Kit"; page: "the Jetson Nano module and other kit accessories are not included") | Robocraze | 6,089 | incl | Y | 4x USB 3.0, GbE, HDMI + DP, 2x CSI, M.2 E, 40-pin | https://robocraze.com/products/jetson-nano-development-kit-with-optional-jetson-nano-core-module-alternative-of-b01-kit | 2026-09-24 | VERIFIED |
| Nano carrier only | Waveshare Jetson Nano Carrier Board (WVSH0482) | ThinkRobotics | 4,599.99 | incl | Y | carrier only | https://thinkrobotics.com/products/waveshare-jetson-nano-carrier-board | 2026-09-24 | VERIFIED |
| Nano carrier only | Seeed reComputer J101 | Robocraze | 7,209 | incl | Y | carrier only | https://robocraze.com/products/seeed-studio-recomputer-j101-carrier-board-for-nvidia-jetson-nano | 2026-09-24 | VERIFIED |
| Official NVIDIA Nano Dev Kit B01 | NVIDIA | – | – | – | not listed at any checked store; NVIDIA lifecycle page: Dev Kit "reached End of Life"; Waveshare page shows original kit "$111.99 DISCONTINUED" | – | https://developer.nvidia.com/embedded/lifecycle ; https://www.waveshare.com/jetson-nano-developer-kit.htm | 2026-09-24 | VERIFIED (EOL) |
| Orin Nano Super Dev Kit | NVIDIA Jetson Orin Nano Super Developer Kit 8GB (SBC1047) | ThinkRobotics | 49,999.99 | incl | Y | 67 TOPS sparse; 8 GB LPDDR5 102 GB/s; 7/15/25 W | https://thinkrobotics.com/products/nvidia-jetson-orin-nano-developer-kit | 2026-09-24 | VERIFIED |
| Orin Nano Super Dev Kit | same (DVB-QC5768) | Quartz | 34,675 | not stated | OOS | – | https://quartzcomponents.com/products/nvidia%C2%AE-jetson-orin-nano-super-developer-kit | 2026-09-24 | VERIFIED |
| Orin Nano module | NVIDIA Jetson Orin Nano 8GB / 4GB | ThinkRobotics | 51,399.99 (8GB, Y) / 45,649.99 (4GB, OOS) | incl | per variant | 260-pin SO-DIMM | https://thinkrobotics.com/products/orin-nano-som | 2026-09-24 | VERIFIED |
| Orin Nano module | NVIDIA Jetson Orin Nano 8GB | Quartz | 28,900 | not stated | OOS | – | https://quartzcomponents.com/products/nvidia-jetson-orin-nano-8gb-module | 2026-09-24 | VERIFIED |
| Orin Nano/NX carrier | Waveshare Jetson Orin Nano/NX carrier | ThinkRobotics | 8,899.99–8,999.99 | incl | Y | carrier | https://thinkrobotics.com/products/waveshare-jetson-orin-nano-nx-carrier-board | 2026-09-24 | VERIFIED |
| Orin Nano/NX carrier | Waveshare Jetson Orin Nano NX Development Board | Robocraze | 8,845 | incl | Y | price implies carrier only | https://robocraze.com/products/waveshare-jetson-orin-nano-nx-development-board | 2026-09-24 | VERIFIED price; contents UNVERIFIED |
| Raspberry Pi 5 | Raspberry Pi 5 2/4/8/16 GB (SBC1067-x) | ThinkRobotics | 7,799.99 (2GB OOS) / 13,999.99 (4GB OOS) / **19,999.99 (8GB Y)** / 35,999.99 (16GB Y) | incl | per variant | 4x Cortex-A76 2.4 GHz | https://thinkrobotics.com/products/raspberry-pi-5 | 2026-09-24 | VERIFIED |
| Raspberry Pi 5 4GB | Raspberry Pi 5 Model B 4GB | Probots | **15,949** | incl | In stock | – | https://probots.co.in/raspberry-pi-5-model-b-bcm2712-arm-cortex-a76-4gb-ram-2-4ghz-single-board-computer.html | 2026-09-24 | VERIFIED |
| Raspberry Pi 5 8GB | Raspberry Pi 5 8GB | electronicscomp | 19,199 ex (≈22,655 incl) | ex 18 % | 16 in stock | – | https://www.electronicscomp.com/raspberry-pi-5-model-with-8gb-ram | 2026-09-24 | VERIFIED |
| Raspberry Pi 5 8GB | Raspberry Pi 5 8GB | Hubtronics / Probots / Sharvi | 20,349 incl (3 in stock) / 22,499 incl (In stock) / 20,769.67 ex (Y) | – | see | – | https://hubtronics.in/raspberry-pi-5-8gb ; https://probots.co.in/raspberry-pi-5-model-b-bcm2712-arm-cortex-a76-8gb-ram-2-4ghz-single-board-computer.html ; https://sharvielectronics.com/product/raspberry-pi-5-8gb-ram/ | 2026-09-24 | VERIFIED |
| Raspberry Pi 5 4GB (OOS listings) | – | electronicscomp / Hubtronics / Sharvi / Zbotic | 13,199 ex / 14,499 incl / 15,669.67 ex / 9,650.04 incl | – | all OOS | – | https://www.electronicscomp.com/raspberry-pi-5-model-4gb ; https://zbotic.in/product/raspberry-pi-5-model-4gb-ram/ | 2026-09-24 | VERIFIED |
| Raspberry Pi 5 16GB | Official Raspberry Pi 5 16GB (DVB-QC3990) | Quartz | 29,225 | not stated | Y | – | https://quartzcomponents.com/products/raspberry-pi-5-16gb | 2026-09-24 | VERIFIED |

Notes: Robocraze search returned no Raspberry Pi 5 board today (only Pi 500+ and accessories). RPi 5 India prices are well above 2024-era levels (cause UNVERIFIED).

### A2. MCUs with CAN / CAN-FD

FDCAN instance counts below are VERIFIED from ST's official CMSIS device headers (GitHub STMicroelectronics/cmsis_device_g4 and cmsis_device_h7: `#define FDCANn`): **G431 = 1, G491 = 2, G474 = 3, H743 = 2, H723 = 3**. Teensy 4.1: "3 CAN Bus (1 with CAN FD)" (https://www.pjrc.com/store/teensy41.html, VERIFIED). ESP32-S3: "includes 1 TWAI controllers" and TWAI is "not compatible with FD format frames and will interpret such frames as errors" (https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/twai.html, VERIFIED).

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| Nucleo-G431RB | ST NUCLEO-G431RB | Evelta | 1,650 ex (1,947 incl) | ex | Sold out (stock 0; "Usually Delivered in 2-5 Days") | 1x FDCAN | https://evelta.com/stm32g431rb-mcu-stm32-nucleo-64-development-board/ | 2026-09-24 | VERIFIED |
| Nucleo-G431RB | ST NUCLEO-G431RB | Hubtronics | 2,566 | incl | OOS | – | https://hubtronics.in/stmicroelectronics-nucleo-g431rb | 2026-09-24 | VERIFIED |
| Nucleo-G474RE | ST NUCLEO-G474RE | electronicscomp | 1,847 ex (≈2,179 incl) | ex 18 % | OOS | 3x FDCAN, 170 MHz M4F | https://www.electronicscomp.com/stmicroelectronics-nucleo-g474re-development-board-stmg474ret6u-mcu-arduino-nano-v3 | 2026-09-24 | VERIFIED |
| Nucleo-G474RE | ST NUCLEO-G474RE | Evelta / Hubtronics | 2,125 ex = 2,507.50 incl (sold out, drop-ship) / 2,179 incl (OOS) | – | OOS | – | https://evelta.com/stm32-nucleo-64-stm32g474re-mcu-development-board/ ; https://hubtronics.in/nucleo-g474re | 2026-09-24 | VERIFIED |
| Nucleo-G431KB | ST NUCLEO-G431KB (Nucleo-32) | Evelta / electronicscomp | 1,265 ex (drop-ship) / 1,385 ex (OOS) | ex | see | 1x FDCAN | https://evelta.com/stm32-nucleo-32-stm32g431kb-mcu-development-board/ | 2026-09-24 | VERIFIED listing; Evelta stock UNVERIFIED |
| Nucleo-G491RE | ST NUCLEO-G491RE | electronicscomp / Hubtronics | 1,583 ex / 1,885 incl | – | both OOS | 2x FDCAN | https://www.electronicscomp.com/stmicroelectronics-nucleo-g491re-development-board-stm32-nucleo-64-stm32g491ret6u-32bit-arm-cortex-m4 | 2026-09-24 | VERIFIED |
| Nucleo-H743ZI2 | ST NUCLEO-H743ZI2 | Hubtronics | 3,410.20 | incl | OOS | 2x FDCAN | https://hubtronics.in/nucelo-h734zi2 | 2026-09-24 | VERIFIED |
| Nucleo-H723ZG | ST NUCLEO-H723ZG | Sharvi | 4,535.63 ex (≈5,352 incl) | ex | Y | 3x FDCAN, 550 MHz M7 (clock UNVERIFIED) | https://sharvielectronics.com/product/nucleo-h723zg-stmicroelectronics-development-board/ | 2026-09-24 | VERIFIED |
| Nucleo-H723ZG | ST NUCLEO-H723ZG | Evelta / Probots / Hubtronics | 4,895 ex / 4,999 incl / 3,540 incl | – | all OOS | – | https://probots.co.in/nucleo-h723zg-arm-stm32-development-boards-kits.html | 2026-09-24 | VERIFIED |
| WeAct H743 core board | WeAct Studio STM32H743VIT6 core board (0.96" TFT, OV7725) | Probots | 3,999 | incl | In stock | 2x FDCAN | https://probots.co.in/weact-studio-stm32h743vit6-development-core-board-with-0-96-tft-screen-ov7725-m12-camera.html | 2026-09-24 | VERIFIED |
| WeAct STM32G431/G474 core boards | WeAct Studio | – | – | – | not found at any readable store | – | – | 2026-09-24 | UNVERIFIED (import only; AliExpress not readable) |
| STM32G431CBT6 (bare MCU) | ST, LQFP-48 | Evelta | 485 ex (572.30 incl) | ex | 135 in stock | 170 MHz M4F, "One FDCAN" (page) | https://evelta.com/stm32g431cbt6-stm32g4-mcu-32bit-arm-cortex-m4-170mhz-128kb-flash-48-lqfp/ | 2026-09-24 | VERIFIED |
| STM32G474RBT3 (bare MCU) | ST, LQFP-64 | Evelta | 421.94 ex (497.89 incl) | ex | Sold out | 3x FDCAN | https://evelta.com/stm32g474rbt3-stm32g4-mcu-32bit-arm-cortex-m4f-128kb-flash-lqfp-64/ | 2026-09-24 | VERIFIED |
| ESP32-S3 (classic TWAI only) | ESP32-S3 Supermini (unsoldered) | Sharvi | 439.91 ex (≈519 incl) | ex | Y | 1x TWAI, no CAN-FD | https://sharvielectronics.com/product/esp32-s3-supermini-development-board-with-wifi-and-bluetooth-unsolder/ | 2026-09-24 | VERIFIED |
| ESP32-S3 | "ESP32E-N16R8 Dual C-Type DOIT" (ESP32-S3-WROOM N16R8) | Quartz | 684 | not stated | Y | 16 MB/8 MB | https://quartzcomponents.com/products/esp32-s3-wroom-n16r8-dual-c-type-usb-development-board-wifi-bluetooth-module | 2026-09-24 | VERIFIED |
| ESP32-S3 | 7Semi ESP32-S3-Dev-BoardC-1-N8R8 | Robocraze | 899 | incl | Y | – | https://robocraze.com/products/7semi-esp32-s3-dev-boardc-1-n8r8-wifi-bluetooth-dual-usb-c-rgb-led | 2026-09-24 | VERIFIED |
| ESP32 (classic) | ESP32 30-pin CP2102 | Quartz | 375 | not stated | Y | 1x TWAI | https://quartzcomponents.com/products/esp32-30-pin-development-board-with-wi-fi-and-bluetooth | 2026-09-24 | VERIFIED |
| ESP32 (classic) | ESP32 38-pin NodeMCU | Robocraze | 425 | incl | Y | – | https://robocraze.com/products/esp32-development-board | 2026-09-24 | VERIFIED |
| Teensy 4.1 | PJRC Teensy 4.1 | Robocraze | 3,545 | incl | Y | 600 MHz M7; 3x CAN (1 FD) | https://robocraze.com/products/teensy-4-1-development-board | 2026-09-24 | VERIFIED |
| Teensy 4.1 | PJRC Teensy 4.1 | Evelta | 3,197 ex (≈3,772 incl) | ex | 12 in stock (listing) | – | https://evelta.com/teensy-4-1-development-board/ | 2026-09-24 | VERIFIED (listing) |
| Teensy 4.1 | – | electronicscomp / Quartz / Zbotic / Sharvi | 2,799 ex / 2,882 / 3,538.82 incl / 2,744.45 ex | – | all OOS | – | https://www.electronicscomp.com/teensy-4.1-development-board | 2026-09-24 | VERIFIED |
| Blue Pill (bxCAN, classic) | STM32F103C8T6 board | Robocraze | 149 | incl | Y | 72 MHz M3 | https://robocraze.com/products/stm32f103c8t6-arm-development-board | 2026-09-24 | VERIFIED |
| Blue Pill | STM32F103C8T6 min. system board | electronicscomp | 159 ex (≈188 incl) | ex 18 % | 441 in stock | – | https://www.electronicscomp.com/stm32f103c8t6-minimum-system-board-stm32-arm-module-india | 2026-09-24 | VERIFIED |
| Raspberry Pi Pico | Pico (original) | Quartz | 325 | not stated | Y | RP2040, no CAN | https://quartzcomponents.com/products/raspberry-pi-pico | 2026-09-24 | VERIFIED |
| Raspberry Pi Pico 2 | Pico 2 with headers / Official Pico 2 | Quartz / Robocraze | 518 / 546 incl | – | Y / Y | RP2350 | https://quartzcomponents.com/products/raspberry-pi-pico-2-with-header-pins ; https://robocraze.com/products/official-raspberry-pi-pico-2 | 2026-09-24 | VERIFIED |
| + MCP2515 for Pico | MCP2515 + TJA1050 module | Robocraze | 134 | incl | Y | classic CAN, 5 V xcvr | https://robocraze.com/products/mcp2515-can-bus-module-board-tja1050-receiver-spi-for-51-mcu-arm-controller | 2026-09-24 | VERIFIED |

### A3. CAN hardware

Transceiver capability (manufacturer pages, VERIFIED today): TI SN65HVD230 "Designed for Data Rates up to 1 Mbps" (https://www.ti.com/product/SN65HVD230); TI TCAN332 "specified for data rates up to 1Mbps" – only TCAN33xG variants do 5 Mbps CAN FD (https://www.ti.com/product/TCAN332); NXP TJA1051 "Timing guaranteed for data rates up to 5 Mbit/s in the CAN FD fast phase", VIO pin on TJA1051T/3 and TK/3 (https://www.nxp.com/products/TJA1051); NXP TJA1462 "CAN FD communication up to 8 Mbit/s", "CAN signal improvement capability as defined in CiA 601-4" (https://www.nxp.com/products/TJA1462). MCP2562FD / ATA6561 / MCP2518FD pages: microchip.com returned 403 → UNVERIFIED.

Transceivers:

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| SN65HVD230 IC | TI SN65HVD230DR | Quartz | 82 | not stated | Y | 3.3 V, ≤1 Mbps (no FD) | https://quartzcomponents.com/products/sn65hvd230dr-texas-instruments-can-interface-transceiver-ic-soic-8 | 2026-09-24 | VERIFIED |
| SN65HVD230 IC | TI SN65HVD230DR | Evelta / Hubtronics / Sharvi | 91.46 ex = 107.92 incl (42 in stock) / 176 incl (138 in stock) / 137.65 ex (Y) | – | Y | – | https://evelta.com/sn65hvd230dr-3-3v-can-transceiver-with-standby-mode-ic-soic-8/ ; https://hubtronics.in/sn65hvd230dr | 2026-09-24 | VERIFIED |
| SN65HVD230 module | generic / Waveshare | Probots (₹125 & ₹289) / Hubtronics (₹410) / Zbotic (₹293.82) | – | incl | **all OOS** | – | https://probots.co.in/sn65hvd230-can-bus-transceiver-communication-module-for-arduino-3c.html ; https://hubtronics.in/sn65hvd230-can-board ; https://zbotic.in/product/sn65hvd230-can-board-network-transceiver-evaluation-development-module/ | 2026-09-24 | VERIFIED |
| TJA1051T/3 IC | NXP | Evelta | 127.50 ex (150.45 incl) | ex | Sold out | 5 Mbit/s FD, VIO | https://evelta.com/tja1051t-3-118-high-speed-can-transceiver-4-5v-5-5v-interface-ic-soic-8/ | 2026-09-24 | VERIFIED |
| TJA1051T IC | NXP TJA1051T-1J | Evelta | 60 ex (70.80 incl) | ex | Sold out | 5 Mbit/s FD, no VIO | https://evelta.com/tja1051t-1j-interface-ic-transceiver-half-canbus-8-so/ | 2026-09-24 | VERIFIED |
| TJA1051 module | Adafruit CAN Pal (TJA1051T/3) | Evelta | 475 ex (560.50 incl) | ex | Sold out | – | https://evelta.com/adafruit-can-pal-can-bus-transceiver-tja1051t-3/ | 2026-09-24 | VERIFIED |
| **TJA1462 IC** | NXP TJA1462AT/0Z | Sharvi | **102.36 ex (≈120.78)** | ex | Y | 8 Mbit/s CAN FD SIC | https://sharvielectronics.com/product/tja1462at-0z-can-fd-signal-improvement-transceiver-with-standby-mode-ic-soic-8-package/ | 2026-09-24 | VERIFIED |
| CAN-FD-ready IC | Microchip ATA6561-GAQW-N | Sharvi | 49.65 ex (≈58.59) | ex | Y | title "CAN FD Ready" | https://sharvielectronics.com/product/ata6561-gaqw-n-high-speed-can-transceiver-with-standby-mode-can-fd-ready-soic-8-package/ | 2026-09-24 | VERIFIED price/stock; FD rate UNVERIFIED |
| TCAN332 IC (classic) | TI TCAN332DR (non-G) | Evelta | 229.88 ex (271.26 incl) | ex | 8 in stock | 1 Mbps only | https://evelta.com/tcan332dr-3-3-v-can-transceiver-interface-ic-soic-8/ | 2026-09-24 | VERIFIED |
| MCP2562 IC (classic) | Microchip MCP2562-E/SN / MCP2562T-E/SN | Quartz / Sharvi | 98 (Y) / 79.65 ex (Y) | – | Y | 1 Mbps (the FD variant is MCP2562**FD**) | https://quartzcomponents.com/products/mcp2562-e-sn-microchip-can-interface-transceiver-ic-soic-8-package ; https://sharvielectronics.com/product/mcp2562t-e-sn-1mbps-high-speed-can-transceiver-ic-soic-8-package/ | 2026-09-24 | VERIFIED |
| MCP2562FD stand-alone | Microchip | – | – | – | not found (only on Waveshare 2-CH CAN FD HAT) | – | – | 2026-09-24 | UNVERIFIED |
| Legacy 5 V TJA1050 module | generic | Quartz / electronicscomp | 58 (Y) / 66 ex (214 in stock) | – | Y | 5 V, ≤1 Mbps | https://quartzcomponents.com/products/m3-x-20mm-hex-allen-socket-head-ss202-boltpack-of-10 ; https://www.electronicscomp.com/tja1050-can-controller-bus-driver-interface-module | 2026-09-24 | VERIFIED |

Controllers:

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| MCP2515 module | MCP2515 + TJA1050 (SPI) | Robocraze | 134 | incl | Y | classic CAN | https://robocraze.com/products/mcp2515-can-bus-module-board-tja1050-receiver-spi-for-51-mcu-arm-controller | 2026-09-24 | VERIFIED |
| MCP2515 module | same | electronicscomp / Probots / Sharvi / Quartz | 135 ex (882 in stock) / 149 incl (In stock) / 117.50 ex (Y) / 78 (OOS) | – | see | – | https://www.electronicscomp.com/mcp2515-can-bus-module-with-tja1050-transreceiver ; https://probots.co.in/mcp2515-can-bus-interface-module-board-for-arduino-raspberry-pi.html ; https://sharvielectronics.com/product/mcp2515-can-bus-module-with-tja1050-transceiver/ | 2026-09-24 | VERIFIED |
| MCP2518FD / MCP2517FD module | – | – | – | – | no stand-alone module found | – | – | 2026-09-24 | UNVERIFIED |
| MCP25625 IC (ctrl + xcvr) | Microchip MCP25625-E/ML | Sharvi / electronicscomp | 154.65 ex (Y) / 165 ex | – | – | classic 1 Mbps | https://sharvielectronics.com/product/mcp25625-e-ml-1mbps-can-controller-with-integrated-transceiver-qfn-28-package/ | 2026-09-24 | VERIFIED |

USB-CAN adapters and HATs:

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| **USB-CAN-FD (CANable class)** | MKS CANable V2.0 | Probots | **3,899** (= 3,304.24 + 594.76 GST) | incl | In stock | STM32G431C8T6 + TJA1051T/3; "up to 1Mbps (Classic CAN), up to 5Mbps (CAN-FD Data Phase)"; "Pre-loaded with CandleLight"; 120 Ω jumper; non-isolated | https://probots.co.in/mks-canable-v2-0-usb-to-can-analyzer-can-fd-stm32g431c8.html | 2026-09-24 | VERIFIED |
| USB-CAN (candleLight class) | UCAN V1.0 (STM32F072, USB-C) | Probots | 1,999 | incl | OOS | classic | https://probots.co.in/ucan-v1-0-usb-to-can-adapter-type-c.html | 2026-09-24 | VERIFIED |
| USB-CAN-A | Waveshare USB-CAN-A (STM32) | Robocraze | 2,189 | incl | Y | "CAN baud rate … 5Kbps to 1Mbps", CAN 2.0A/B; Linux "Ubuntu Under Jetson Nano, Support Secondary Development" (vendor protocol; SocketCAN UNVERIFIED) | https://robocraze.com/products/waveshare-usb-to-can-a-adapter-stm32-chip-solution-with-multi-working-modes | 2026-09-24 | VERIFIED |
| USB-CAN-A | same | Sharvi / Zbotic / Hubtronics / Probots / electronicscomp | 1,912.78 ex (Y) / 2,094.50 incl (Y) / 2,099 incl (1 in stock) / 2,499 incl (In stock) / 1,522 ex (page "Product not found") | – | see | – | https://sharvielectronics.com/product/usb-to-can-adapter-model-a-stm32-chip-solution-multiple-working-modes-multi-system-compatible/ ; https://hubtronics.in/usb-to-can-adapter | 2026-09-24 | VERIFIED |
| Isolated USB-CAN (cheapest isolated) | ISO-B-CAN-A (FTDI) | Sharvi | 859.20 ex (≈1,014) | ex | Y | protocol UNVERIFIED | https://sharvielectronics.com/product/iso-b-can-a-isolated-usb-to-can-interface-converter-ftdi-industrial-grade/ | 2026-09-24 | VERIFIED |
| USB-CAN-B (2-ch classic, isolated) | Waveshare | electronicscomp / Robocraze / Hubtronics / ThinkRobotics | 8,219 ex / 9,119 incl (Y) / 9,499 incl / 10,599.99 incl (Y) | – | see | – | https://robocraze.com/products/waveshare-usb-to-can-adapter-with-dual-channel-can-analyzer | 2026-09-24 | VERIFIED |
| USB-CAN-FD (2-ch analyzer) | Waveshare USB-CAN-FD | Hubtronics | 8,275 | incl | 20 in stock | 2x CAN FD | https://hubtronics.in/usb-can-fd | 2026-09-24 | VERIFIED |
| USB-CAN-FD / FD-B | Waveshare | ThinkRobotics / Sharvi / Robocraze / Zbotic | 9,149.99 & 11,049.99 incl / 9,079.47 ex / 12,975 incl / 12,978.82 incl | – | Y | – | https://thinkrobotics.com/products/industrial-grade-can-can-fd-bus-data-analyzer ; https://zbotic.in/product/waveshare-industrial-grade-usb-can-fd-b/ | 2026-09-24 | VERIFIED |
| PCAN-USB (genuine) | PEAK-System | Hubtronics | 25,369 | incl | OOS | reference | https://hubtronics.in/peak-pcan-usb-rs232-adapter | 2026-09-24 | VERIFIED |
| PCAN clones / "USB2CANFD" | – | – | – | – | not found | – | – | 2026-09-24 | UNVERIFIED |
| **2-CH CAN FD HAT** | Waveshare 2-Channel Isolated CAN FD HAT – page: "CAN controller: MCP2517FD", "CAN transceiver: MCP2562FD", "up to 8Mbps", 5 kV isolation, SPI | Hubtronics | **4,399** (Ex Tax 3,727.97) | incl | 3 in stock | 2x CAN FD | https://hubtronics.in/2-channel-can-fd-hat | 2026-09-24 | VERIFIED |
| 2-CH CAN FD HAT | same | Robocraze | 4,732 | incl | OOS | – | https://robocraze.com/products/waveshare-2-channel-can-fd-hat-raspberry-pi-expansion-board | 2026-09-24 | VERIFIED |
| CAN FD + RS485/232 board | Waveshare isolated RS232/RS485/CAN/CAN FD board | electronicscomp / Hubtronics / ThinkRobotics | 4,292 ex / 5,249 incl / 5,749.99 incl (Y) | – | see | 1x CAN FD + 1x CAN | https://thinkrobotics.com/products/can-fd-rpi-hat | 2026-09-24 | VERIFIED |
| RS485 CAN HAT (classic) | Waveshare | Evelta / Zbotic / Hubtronics / electronicscomp | 796 ex (15 in stock) / 848.42 incl (Y) / 949 incl (10 in stock) / 1,279 ex (3 in stock) | – | Y | MCP2515 (UNVERIFIED) | https://evelta.com/rs485-can-hat-for-raspberry-pi/ ; https://hubtronics.in/rs485-can-hat-rpi | 2026-09-24 | VERIFIED |
| 2-CH isolated CAN HAT (classic) | Waveshare 2-CH CAN HAT(+) | Zbotic / Evelta / Hubtronics / electronicscomp | 2,358.82 incl (Y) / 2,028 ex (4 in stock) / 2,349 incl (2 in stock) / 2,069 ex (1 in stock) | – | Y | – | https://zbotic.in/product/waveshare-2-channel-isolated-can-bus-expansion-hat-for-raspberry-pi/ ; https://hubtronics.in/2-ch-can-hat-plus | 2026-09-24 | VERIFIED |
| CAN board for Jetson Nano | Waveshare RS485 CAN Expansion Board for Jetson Nano – page: "Onboard CAN controller MCP2515 via SPI interface, matching with SIT65HVD230DR transceiver" | ThinkRobotics | 2,399.99 | incl | Y | classic CAN | https://thinkrobotics.com/products/rs485-can-expansion-board-for-jetson-nano-online | 2026-09-24 | VERIFIED |

### A4. Motor drivers with CAN (and FOC drivers)

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| **B-G431B-ESC1** | STMicroelectronics | Evelta | 2,365 ex (**2,790.70 incl**) | ex | **Sold out** (page JSON stock 0, "Sold Out") | STM32G431CB; "up to 6S LiPo"; "up to 40 A peak current with air-forced cooling"; UART/CAN/PWM; Hall/encoder; 30 x 41 mm, 9.2 g; ST-LINK/V2-1 (Evelta description) | https://evelta.com/b-g431b-esc1-esc-with-stm32g431cb-mcu-pwm-can-uart/ | 2026-09-24 | VERIFIED |
| B-G431B-ESC1 elsewhere in India | – | the other 9 readable stores | – | – | 0 hits | – | – | 2026-09-24 | VERIFIED absence (search) |
| SimpleFOC Mini | DFRobot SimpleFOCmini (DRI0058) | Evelta | 671 ex (791.78 incl) | ex | 5 in stock | "eight to thirty volt input and two point five ampere peak current"; no CAN (needs MCU + transceiver) | https://evelta.com/simplefocmini-brushless-dc-motor-driver-board/ | 2026-09-24 | VERIFIED |
| 3-phase gate driver IC (for custom driver) | TI DRV8313PWPR | Evelta | 220 ex (259.60 incl) | ex | "Shipped in 24 Hours" (stock UNVERIFIED) | 2.5 A 3-phase | seen as related product on SimpleFOCmini page | 2026-09-24 | VERIFIED price; URL/stock UNVERIFIED |
| Low-V 3-phase driver | 7Semi TMC6300 breakout | Evelta / Robocraze | 635 ex (44 in stock) / 749 incl (Y) | – | Y | small gimbal motors only (low-voltage part; a Hubtronics 7Semi 3-phase listing says "2V–11V Input" – TMC6300 range itself UNVERIFIED) | https://evelta.com/7semi-3-phase-tmc6300-bldc-pmsm-brushless-motor-driver-breakout/ | 2026-09-24 | VERIFIED |
| ODrive (S1/Micro/Pro), MKS ODrive Mini, ODESC | – | – | – | – | **0 hits** at all readable Indian stores | – | – | 2026-09-24 | VERIFIED absence → import (see A9) |
| VESC / Flipsky ESC | – | ThinkRobotics lists only a Flipsky Antispark Switch (OOS) | – | – | no VESC found | – | https://thinkrobotics.com/products/flipsky-antispark-switch-pro-with-aluminum-pcb-v3-0-280a-for-electric-skateboard-ebike-scooter-robots | 2026-09-24 | VERIFIED absence |
| moteus | mjbots | – | – | – | 0 hits | – | – | 2026-09-24 | VERIFIED absence → import (A9) |
| Integrated CAN actuator (reference) | T-Motor CubeMars AK70-10 KV100 with driver | Robokits | 52,394 | ex (inferred) | in listing | CAN actuator | https://robokits.co.in/t-motor-parts/robot-joint-brushless-motors/t-motor-cubemars-ak70-10-kv100-brushless-dc-actuator-robot-joint-motor-along-with-the-driver | 2026-09-24 | VERIFIED |
| Serial-bus servo (non-CAN alternative) | Waveshare ST3215 series (TTL bus, 360° magnetic encoder) | ThinkRobotics | 2,399.99–2,649.99 | incl | Y | not CAN | https://thinkrobotics.com/products/st3215-series-serial-bus-servo | 2026-09-24 | VERIFIED |

### A5. Magnetic encoders & magnets

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| AS5600 module | "AS5600 12-Bit Magnetic Encoder Sensor Module" | Sharvi | **135.91 ex (≈160)** | ex | Y | 12-bit, I2C/analog/PWM | https://sharvielectronics.com/product/as5600-12-bit-magnetic-encoder-sensor-module/ | 2026-09-24 | VERIFIED |
| AS5600 module | AS5600 | Probots / Quartz | 149 incl / 122 | – | both OOS | – | https://probots.co.in/magnetic-encoder-sensor-as5600.html ; https://quartzcomponents.com/products/as5600-magnetic-angle-encoder-sensor-module | 2026-09-24 | VERIFIED |
| AS5600 + magnet | "AS5600 Absolute Encoder … with Magnet Wheel" (RKI-6142) | Robokits | 157 ex (≈185) | ex (inferred) | OOS | includes magnet | https://robokits.co.in/sensors/encoders/as5600-absolute-encoder-12-bit-precision-angle-measurement-sensor-with-magnet-wheel | 2026-09-24 | VERIFIED |
| AS5600 (Grove) | Seeed Grove AS5600 | electronicscomp | 619 ex | ex 18 % | OOS | – | https://www.electronicscomp.com/seeedstudio-grove-12bit-magnetic-rotary-position-sensor-as5600 | 2026-09-24 | VERIFIED |
| AS5040 module | programmable AS5040 10-bit | Robokits | 646 | ex (inferred) | in listing | 10-bit | https://robokits.co.in/automation-control-cnc/encoders/programmable-as5040-magnetic-rotary-absolute-encoder-16-bit-sensor-module | 2026-09-24 | VERIFIED listing |
| AS5047P / AS5048A / MT6701 / MT6835 boards | – | – | – | – | **not found** at any readable store (MT6701 only inside LILYGO T-Knob kit, Hubtronics ₹5,570) | – | https://hubtronics.in/t-knob | 2026-09-24 | UNVERIFIED (import) |
| Encoder magnets (import ref.) | ODrive "Set of 2 Encoder Magnets" | shop.odriverobotics.com | USD 6.00 | – | Y | – | https://shop.odriverobotics.com/products/set-of-2-encoder-magnets | 2026-09-24 | VERIFIED (USD) |
| Diametric magnets (India) | – | – | – | – | not found as "diametric"; only axial NdFeB discs (e.g. Quartz 8x2 mm ₹13 – axial, unsuitable) | – | https://quartzcomponents.com/products/small-magnets-8mm-diameter | 2026-09-24 | VERIFIED absence |

### A6. IMUs

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| BNO085 | 7Semi BNO085 Nano | Evelta | **1,775 ex (2,094.50 incl)** | ex | 21 in stock | 9-DoF fusion; BHL used BNO085 first | https://evelta.com/7semi-bno085-9-dof-orientation-imu-fusion-nano-breakout/ | 2026-09-24 | VERIFIED |
| BNO085 | 7Semi BNO085 Nano | Robocraze | 2,095 | incl | Y | – | https://robocraze.com/products/bno085-9-dof-orientation-imu-sensor-fusion-nano-breakout-board | 2026-09-24 | VERIFIED |
| BNO085 | Adafruit 4754 | Evelta / electronicscomp | 3,340 ex (17 in stock) / 2,287 ex (OOS) | – | see | – | https://evelta.com/adafruit-bno085-9-dof-orientation-imu-fusion-breakout/ | 2026-09-24 | VERIFIED |
| BNO086 | 7Semi | Evelta / Robocraze / Hubtronics | 1,995 ex (8 in stock) / 2,349 incl (Y) / 2,499 incl (3 in stock) | – | Y | – | https://evelta.com/7semi-bno086-imu-mini-breakout-for-robotics-ar-vr-and-iot/ ; https://robocraze.com/products/7semi-bno086-imu-mini-breakout-board-for-robotics ; https://hubtronics.in/bno086-9dof-imu-breakout | 2026-09-24 | VERIFIED |
| BNO055 | 7Semi BNO055 Qwiic | Evelta | 1,137 ex (1,341.66 incl) | ex | 393 in stock | 9-DoF fusion | https://evelta.com/7semi-bno055-9-dof-absolute-orientation-sensor-breakout-i2c-qwiic/ | 2026-09-24 | VERIFIED |
| BNO055 | various | Hubtronics / ThinkRobotics / Robocraze | 1,274 (12 in stock) / 1,349.99 (Y) / 1,359 (Y) | incl | Y | – | https://hubtronics.in/bno055-9dof-absolute-orientation-sensor ; https://thinkrobotics.com/products/9-dof-absolute-orientation-bno055-sensor | 2026-09-24 | VERIFIED |
| ICM-42688-P | – | – | – | – | no breakout found (only inside FPV flight controllers) | – | – | 2026-09-24 | UNVERIFIED |
| BMI088 | Seeed Grove BMI088 | electronicscomp | 1,387 ex | ex 18 % | OOS | 6-axis | https://www.electronicscomp.com/seeedstudio-grove-6-axis-accelerometer-and-gyroscope-bmi088 | 2026-09-24 | VERIFIED |
| ICM-20948 | 7Semi | Robocraze | 1,130 | incl | Y | 9-axis | https://robocraze.com/products/icm-20948-9dof-imu-breakout-board-mpu-9250-upgrade-7semi | 2026-09-24 | VERIFIED |
| ICM-20948 | 7Semi / SparkFun | Evelta | 960 ex (sold out) / 2,309 ex | ex | – | – | https://evelta.com/7semi-icm-20948-9dof-imu-breakout/ | 2026-09-24 | VERIFIED |
| 6-axis alt. | 7Semi LSM6DSV16X Qwiic | Evelta | 635 ex (749.30 incl) | ex | 18 in stock | – | https://evelta.com/7semi-lsm6dsv16x-6-axis-imu-accelerometer-gyroscope-qwiic/ | 2026-09-24 | VERIFIED |
| 6-axis alt. | 7Semi BMI323 | Evelta | 395 ex (466.10 incl) | ex | 60 in stock | – | https://evelta.com/7semi-bmi323-imu-breakout-board-6dof-accelerometer-gyroscope-with-qwiic-support-spi-i2c/ | 2026-09-24 | VERIFIED |
| MPU6050 | GY-521 type | electronicscomp / Quartz / Robocraze | 122 ex (422 in stock) / 127 (Y) / 154 incl (Y) | – | Y | legacy part | https://www.electronicscomp.com/mpu6050-triple-axis-gyro-accelerometer-module | 2026-09-24 | VERIFIED |
| MPU9250 | module | Robocraze / electronicscomp | 367 incl (Y) / 375 ex (165 in stock) | – | Y | legacy (clone risk UNVERIFIED) | https://robocraze.com/products/mpu-9250-module ; https://www.electronicscomp.com/mpu9250-9-axis-gyro-accelerometer-module | 2026-09-24 | VERIFIED |

### A7. Cameras

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| IMX219-77 (Jetson Nano, 15-pin CSI) | Waveshare IMX219-77 | ThinkRobotics | 1,699.99 | incl | Y | 8 MP, 77° | https://thinkrobotics.com/products/imx219-77-camera-for-jetson-nano-online | 2026-09-24 | VERIFIED |
| IMX219-77 | Waveshare | Hubtronics / electronicscomp / Evelta | 1,804.22 incl (2 in stock) / 2,089 ex (24 in stock) / 1,253 ex (sold out) | – | see | – | https://hubtronics.in/imx219-77 ; https://www.electronicscomp.com/waveshare-imx219-77-camera-applicable-for-jetson-nano ; https://evelta.com/imx219-77-camera-77-fov-applicable-for-jetson-nano/ | 2026-09-24 | VERIFIED |
| IMX219-160 (cheapest) | Waveshare IMX219 160° | Hubtronics / Evelta | 1,109.20 incl (1 in stock) / 1,166 ex = 1,375.88 incl (5 in stock) | – | Y | 160° | https://hubtronics.in/imx219-camera-module ; https://evelta.com/imx219-camera-module-160-degree-fov/ | 2026-09-24 | VERIFIED |
| IMX219-160 | Waveshare | ThinkRobotics / Zbotic / electronicscomp | 2,349.99 (Y) / 2,712.82 (Y) / 2,525 ex (3 in stock) | – | Y | – | https://thinkrobotics.com/products/imx219-160-camera-with-160-fov-for-jetson-nano-online | 2026-09-24 | VERIFIED |
| RPi Camera v2 (IMX219) | Raspberry Pi Camera Module V2 | Quartz | 1,458 | not stated | Y | 8 MP | https://quartzcomponents.com/products/raspberry-pi-camera-module-2 | 2026-09-24 | VERIFIED |
| RPi Camera v2 | official | Robocraze / Hubtronics / Evelta | 1,799 (OOS) / 1,710 (OOS) / 2,938 ex (1 in stock) | – | see | – | https://robocraze.com/products/raspberry-pi-camera-module-v2-8-megapixel-1080p | 2026-09-24 | VERIFIED |
| IMX477 | Waveshare IMX477-160 12.3 MP | ThinkRobotics / Zbotic | 8,449.99 (Y) / 10,028.82 (Y) | incl | Y | 12.3 MP | https://thinkrobotics.com/products/waveshare-imx477-160-12-3mp-camera-160-fov ; https://zbotic.in/product/waveshare-imx477-160-12-3mp-camera-160-fov-applicable-for-jetson-nano-compute-module/ | 2026-09-24 | VERIFIED |
| Stereo (cheap) | Waveshare IMX219-83 | ThinkRobotics / Hubtronics / electronicscomp | 6,599.99 (Y) / 5,799 / 5,876 ex | – | see | 2x IMX219 | https://thinkrobotics.com/products/imx219-83-stereo-camera-module-online | 2026-09-24 | VERIFIED |
| RealSense D435i | Intel | electronicscomp | 34,319 ex (≈40,496) | ex 18 % | OOS | depth + IMU | https://www.electronicscomp.com/intel-realsense-depth-camera-d435i-with-imu | 2026-09-24 | VERIFIED |
| RealSense D435i | Intel | ThinkRobotics | 43,999.99 | incl | OOS | – | https://thinkrobotics.com/products/intel-realsense-depth-camera-d435i | 2026-09-24 | VERIFIED |
| RealSense D435 (no IMU) | Intel | Robocraze | 55,399 | incl | Y | – | https://robocraze.com/products/intel-realsense-d435-depth-camera-for-intelligent-sensing | 2026-09-24 | VERIFIED |
| RealSense D455 | Intel | electronicscomp / ThinkRobotics | 40,462 ex / 55,039.99 incl | – | both OOS | – | https://www.electronicscomp.com/intel-d455-realsense-depth-camera | 2026-09-24 | VERIFIED |
| OAK-D Lite | Luxonis (Waveshare listing) | ThinkRobotics | 31,649.99 | incl | Y | on-camera NN | https://thinkrobotics.com/products/oak-d-lite-opencv-ai-machine-vision-kit-online | 2026-09-24 | VERIFIED |
| Orbbec Gemini 2 | Orbbec | ThinkRobotics | 32,599.99–44,449.99 (variants) | incl | Y | stereo depth | https://thinkrobotics.com/products/orbbec-gemini-2 | 2026-09-24 | VERIFIED |
| Orbbec Gemini 335/335L; 336L | Orbbec | ThinkRobotics | 36,799.99–49,949.99; 52,799.99 | incl | Y | – | https://thinkrobotics.com/products/orbbec-gemini-335 ; https://thinkrobotics.com/products/gemini-336l | 2026-09-24 | VERIFIED |
| Orbbec Gemini E / 215 (cheapest depth) | Orbbec | ThinkRobotics | 24,499.99 / 29,749.99 | incl | Y | – | https://thinkrobotics.com/products/geminie ; https://thinkrobotics.com/products/orbbec-gemini-215 | 2026-09-24 | VERIFIED |

### A8. Ethernet switch, connectors, cable, terminators

| Item | Brand/Model | Supplier | Price ₹ | GST | Stock | Key specs | URL | Date | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| 5-port GbE switch (cheapest) | PUSR USR-SG1005 | ThinkRobotics | 1,549.99 | incl | Y | 5x GbE (unmanaged UNVERIFIED) | https://thinkrobotics.com/products/ethernet-switch-business-usr-sg1005 | 2026-09-24 | VERIFIED |
| 5-port 10/100 switch | PUSR USR-SF1005 | ThinkRobotics | 1,199.99 | incl | Y | 10/100 | https://thinkrobotics.com/products/ethernet-switch-business-usr-sf1005 | 2026-09-24 | VERIFIED |
| 5-port industrial GbE (DIN) | SmartElex Industrial 5P | Robocraze | 2,137 | incl | Y | – | https://robocraze.com/products/smartelex-industrial-5p-gigabit-ethernet-switch-full-duplex-10-100-1000m | 2026-09-24 | VERIFIED |
| 5-port industrial GbE (DIN) | Waveshare Industrial 5P | Evelta / Sharvi / Robocraze | 2,085 ex (17 in stock) / 2,371.24 ex (Y) / 2,659 incl (Y) | – | Y | – | https://evelta.com/industrial-5p-gigabit-ethernet-switch/ ; https://robocraze.com/products/waveshare-industrial-5-port-gigabit-ethernet-switch | 2026-09-24 | VERIFIED |
| JST-GH headers | 4-pin / 6-pin JST GH male 1.25 mm straight | Probots | 28 / 42 | incl | In stock | locking 1.25 mm | https://probots.co.in/4-pin-jst-gh-male-connector-1-25mm-straight.html ; https://probots.co.in/6-pin-jst-gh-male-connector-1-25mm-straight.html | 2026-09-24 | VERIFIED |
| JST-GH cable | JST GHR-06V 15 cm | Evelta | 25 ex | ex | Sold out | – | https://evelta.com/jst-ghr-06v-cable-6pin-1-25mm-pitch-female-connector-15cm/ | 2026-09-24 | VERIFIED |
| JST-GH cable | Adafruit JST GH 6-pin 100 mm (5754) | Hubtronics | 89 | incl | UNVERIFIED | – | https://hubtronics.in/jst-gh-1-25mm-pitch-6-pin-cable-100mm | 2026-09-24 | VERIFIED price |
| JST-GH SMT header | SM11B-GHS-TB | Evelta | 21 ex | ex | 41 in stock | – | https://evelta.com/11pin-1-25mm-pitch-shrouded-header-connector/ | 2026-09-24 | VERIFIED |
| JST-GH CAN cable (import ref.) | ODrive "JST-GH CAN Cable" | shop.odriverobotics.com | USD 4.00–9.00 | – | Y | – | https://shop.odriverobotics.com/products/jst-gh-can-cable | 2026-09-24 | VERIFIED (USD) |
| Molex Micro-Fit 3.0 | – | – | – | – | **not found** (only Mini-Fit Jr 39-30-0060 at Probots ₹330) | – | https://probots.co.in/39-30-0060-mini-fit-junior-4-2mm-pcb-header-connectors-and-wire-housings-6-ckt-r-a-header.html | 2026-09-24 | UNVERIFIED (import) |
| Twisted-pair CAN cable | – | – | – | – | no dedicated CAN cable found; CAT5e patch cords as twisted-pair source: Quartz 3 m ₹67 (Y), Robocraze 1 m ₹145 (Y) | CAT5e ≈100 Ω vs CAN spec 120 Ω (suitability for short in-robot runs ESTIMATED) | https://quartzcomponents.com/products/high-speed-cat-5e-ethernet-lan-network-cable-3-meter ; https://robocraze.com/products/ethernet-lan-cable | 2026-09-24 | VERIFIED price |
| 120 Ω terminator | 120 Ω 1/4 W resistor | Probots | 3 | incl | In stock | – | https://probots.co.in/120-ohm-1-4-w-resistor.html | 2026-09-24 | VERIFIED |
| 120 Ω terminator | 120 Ω 1/4 W, 5-pc pack | electronicscomp | 2 ex / pack | ex 18 % | 22,121 in stock | – | https://www.electronicscomp.com/120-ohm-resistance | 2026-09-24 | VERIFIED |
| 120 Ω SMD | Royal Ohm 1206 120E 1 % | Evelta | 1.80 ex | ex | 3,729 in stock | – | https://evelta.com/120e-1-1206-smd-resistor-royal-ohm-1206w4f1200t5e/ | 2026-09-24 | VERIFIED |

### A9. Import-only references (official vendor stores, USD list price, excl. shipping/duty/IGST)

INR landed cost is NOT computed (no verified FX/duty figures today) → UNVERIFIED.

| Item | Vendor / model | Price (USD) | Stock | URL | Date | Evidence |
|---|---|---|---|---|---|---|
| ODrive Micro | ODrive Robotics | 89.00 | Y | https://shop.odriverobotics.com/products/odrive-micro | 2026-09-24 | VERIFIED |
| ODrive S1 | ODrive Robotics | 149.00 | Y | https://shop.odriverobotics.com/products/odrive-s1 | 2026-09-24 | VERIFIED |
| moteus-c1 / moteus r4.11 / moteus-n1 | mjbots | 69.00 / 94.00 / 149.00 | Y | https://mjbots.com/products/moteus-c1 ; https://mjbots.com/products/moteus-r4-11 ; https://mjbots.com/products/moteus-n1 | 2026-09-24 | VERIFIED |
| mjcanfd-usb-1x (USB-CAN-FD) / pi3hat r4.5 | mjbots | 39.00 / 149.00 | Y | https://mjbots.com/products/mjcanfd-usb-1x ; https://mjbots.com/products/mjbots-pi3hat-r4-5 | 2026-09-24 | VERIFIED |
| ODESC V4.2 single-drive (ODrive 3.6-derived) | Flipsky | 34.99–43.99 | Y | https://flipsky.net/products/odesc-v4-2-single-drive-high-current-high-precision-brushless-servo-motor-controller-based-on-odrive3-6-upgrade-software-configuration-compatible-with-odrivetool-foc-bldc | 2026-09-24 | VERIFIED |
| ODESC3.6 dual-drive 56 V / single-drive | Flipsky | 59.99 / 69.00 | Y | https://flipsky.net/products/odesc3-6-dual-drive-controller-56v-with-heat-sink-optimizes-high-performance-brushless-motor-high-power-foc-bldc-based-on-odrive | 2026-09-24 | VERIFIED |
| Mini FSESC6.7 PRO 70A (VESC 6.6) / Mini FSESC4.20 50A | Flipsky | 57.00 / 56.00 | Y | https://flipsky.net/products/mini-fsesc6-7-pro-70a | 2026-09-24 | VERIFIED |
| CANable 2.0 (FD) / CANable Pro 1.1 (isolated) | Openlight Labs | 35.00 / 70.00 | **OOS** | https://openlightlabs.com/products/canable-2-0 ; https://openlightlabs.com/products/canable-pro-1-1-isolated-usb-to-can-adapter | 2026-09-24 | VERIFIED |
| LCSC chips (AS5047P, AS5048A, MT6701, MT6835, MCP2518FD, MCP2562FD, ICM-42688-P, BMI088, STM32G474) | LCSC | – | – | lcsc.com (search blocked: Akamai 403 / JS-only) | 2026-09-24 | UNVERIFIED |
| WeAct STM32G431/G474 core, MKS ODrive Mini | AliExpress/Makerbase | – | – | not readable | 2026-09-24 | UNVERIFIED |

---

## PART B – Jetson Nano feasibility

### B.1 Platform facts

| # | Fact | Value (quoted where possible) | Source | Evidence |
|---|---|---|---|---|
| B1 | JetPack line for Nano | Jetson Nano only in JetPack 4.x; 4.6.x = 4.6 [L4T 32.6.1] … 4.6.6 [L4T 32.7.6]. Orin Nano: JetPack 6.0 → 7.2.1 [L4T 39.2.1] (latest 6.x = 6.2.3 [L4T 36.5.2]) | https://developer.nvidia.com/embedded/jetpack-archive | VERIFIED |
| B2 | End of software line | "Jetson Linux R32.7.6 with JetPack 4.6.6 marks the final release for Jetson Linux R32 and JetPack 4."; "Linux Kernel 4.9"; "sample filesystem based on Ubuntu 18.04" | https://developer.nvidia.com/embedded/linux-tegra-r3276 | VERIFIED |
| B3 | JetPack 4.6.x libraries | JP 4.6.6 "is the same as JetPack 4.6.5 but includes Jetson Linux 32.7.6"; JP 4.6.1 components: CUDA 10.2, cuDNN 8.2.1, TensorRT 8.2.1, VPI 1.2, OpenCV 4.1.1 | https://developer.nvidia.com/jetpack-sdk-466 | VERIFIED |
| B4 | CPU/GPU/power | "472 GFLOPs"; "Quad-core ARM Cortex-A57 MPCore processor" at "1.43GHz"; 128-core Maxwell; "5W - 10W" | https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-nano/product-development/ | VERIFIED |
| B5 | Memory/storage | "4 GB 64-bit LPDDR4, 1600MHz 25.6 GB/s" (shared CPU/GPU); "16 GB eMMC 5.1" | https://developer.nvidia.com/embedded/jetson-nano | VERIFIED |
| B6 | I/O (module) | "1x USB 3.0 (5 Gbps), 3x USB 2.0", "1x GbE", "3x UART, 2x SPI, 2x I2S, 4x I2C, GPIOs", up to 4 cameras / 12-lane MIPI CSI-2 | B4 + B5 pages | VERIFIED |
| B7 | **CAN** | No CAN in either official Nano I/O list; the Orin Nano/NX spec rows say "1x CAN" ⇒ Jetson Nano has **no native CAN controller**. CAN must come via SPI (MCP2515 / MCP251xFD), USB-CAN, or an MCU bridge | B4/B6 vs https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/ | VERIFIED (absence in official spec) + inference |
| B8 | Size | Module "69.6mm x 45mm", "260-pin SO-DIMM connector"; dev kit "Whole kit: 100mm × 80mm × 29mm" (Waveshare listing of the NVIDIA kit) | B4 page; https://www.waveshare.com/jetson-nano-developer-kit.htm | VERIFIED |
| B9 | Mounting holes (dev-kit carrier / module) | not stated on any page reachable today (Waveshare wiki shows drawings only as images) | https://www.waveshare.com/wiki/JETSON-NANO-DEV-KIT | UNVERIFIED |
| B10 | Lifecycle | Jetson Nano (module): January 2027; Nano Developer Kit listed as reached End of Life; Jetson Orin Nano 8GB and 4GB: January 2032 (table rows "Jetson Nano / January 2027", "Jetson Orin Nano 8GB / January 2032") | https://developer.nvidia.com/embedded/lifecycle | VERIFIED |
| B11 | ROS 2 official support | REP 2000: Humble (May 2022–May 2027) Ubuntu Jammy 22.04 Tier 1 amd64/arm64, Focal Tier 3; Jazzy (May 2024–May 2029) Noble 24.04 Tier 1; Kilted (May 2025–Nov 2026) Noble. Ubuntu Bionic 18.04 only in Dashing (May 2019–May 2021) and Eloquent (Nov 2019–Nov 2020) ⇒ **no supported ROS 2 distro runs natively on the Nano's Ubuntu 18.04** | https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-2000.rst | VERIFIED |
| B12 | ROS 2 on Nano in practice | Community image `dustynv/ros:humble-ros-base-l4t-r32.7.1` exists (Docker Hub last_updated 2023-12-06). jetson-containers master now: "Only Tested and supported Jetpack 6.2 (Cuda 12.6) and JetPack 7 (CUDA 13.x)"; JP4 users → `legacy` branch (lists ROS2 Foxy/Galactic/Humble/Iron containers) | https://hub.docker.com/v2/repositories/dustynv/ros/tags?name=humble-ros-base-l4t-r32 ; https://github.com/dusty-nv/jetson-containers ; https://raw.githubusercontent.com/dusty-nv/jetson-containers/legacy/README.md | VERIFIED |
| B13 | CAN-FD driver gap on kernel 4.9 | Linux `mcp251xfd` (MCP2517FD/2518FD SPI) first in v5.10 (drivers/net/can/spi/mcp251xfd/Kconfig: 404 at tag v5.9, 200 at v5.10); `gs_usb` CAN-FD (`GS_CAN_FEATURE_FD`) first in v5.18 (absent 4.9…5.17) ⇒ on L4T 32.7 neither the Waveshare CAN-FD HAT nor CANable-2 CAN-FD mode works without a kernel backport; classic MCP2515 and classic gs_usb do | https://github.com/torvalds/linux/tree/v5.10/drivers/net/can/spi/mcp251xfd ; https://github.com/torvalds/linux/blob/v5.18/drivers/net/can/usb/gs_usb.c | VERIFIED (source-tree check) |
| B14 | Orin Nano Super | 2024-12-17: "reduced price of $249, down from $499"; "67 Sparse TOPs"; "102 GB/s"; GPU 1,020 MHz; CPU "1.7 GHz"; new 25 W mode; "All previous Jetson Orin Nano Developer Kits can use the new power mode by upgrading to the latest version of JetPack"; SD image "based on JetPack 6.1" | https://developer.nvidia.com/blog/nvidia-jetson-orin-nano-developer-kit-gets-a-super-boost/ | VERIFIED |
| B15 | Orin Nano 8GB module | 67 TOPS; 1024-core Ampere GPU w/ 32 Tensor Cores; 6-core Cortex-A78AE; 8 GB 128-bit LPDDR5; "7W - 15W - 25W"; "1x CAN"; "1x GbE"; "69.6mm x 45mm, 260-pin SO-DIMM connector" | https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/ | VERIFIED |
| B16 | Nano → Orin Nano compatibility | "we've made the Jetson Orin Nano and Jetson Orin NX modules completely pin– and form–factor–compatible" (2022-09-21); "up to 80X the AI performance of NVIDIA Jetson Nano". Same 69.6 x 45 mm SO-DIMM as the Nano, but NVIDIA's pin-compat statement covers Orin NX, not Nano ⇒ plan a **new carrier / re-validation** for the upgrade (Indian stores sell separate Nano vs Orin carriers) | https://developer.nvidia.com/blog/solving-entry-level-edge-ai-challenges-with-nvidia-jetson-orin-nano/ | VERIFIED quote; Nano pin-compat UNVERIFIED |
| B17 | Orin Nano dev-kit CAN header / size | hardware-layout page lists DC jack 5.5 x 2.5 mm, M.2 2280 + 2230 + Key-E, two 22-pin CSI, 40-pin header; CAN header and board size not stated there | https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/hardware_layout.html | VERIFIED (partial) / CAN header UNVERIFIED |
| B18 | Price gap India | Nano complete kit ₹30,899.99 vs Orin Nano Super ₹49,999.99 (both ThinkRobotics, in stock) → Δ = ₹19,100.00; RPi 5 8GB ₹19,999.99 | A1 | ESTIMATED (difference of VERIFIED prices) |

### B.2 RL locomotion policy compute cost (ESTIMATED)

FLOPs of an MLP = 2 x Σ(n_in x n_out) (multiply-accumulate = 2 FLOP; biases/activations negligible). Script: `canload.py` (scratchpad).

| Policy MLP (obs → hidden → actions) | MACs | FLOP / inference | at 50 Hz |
|---|---|---|---|
| 45 → 256 → 128 → 128 → 12 (12-DoF legs) | 62,208 | 0.124 M | 6.2 MFLOP/s |
| 81 → 256 → 256 → 256 → 24 | 157,952 | 0.316 M | 15.8 MFLOP/s |
| 81 → 512 → 256 → 128 → 24 (24-DoF, obs = 3+3+3+24+24+24) | 208,384 | 0.417 M | 20.8 MFLOP/s |
| 405 (5-frame history) → 512 → 256 → 128 → 24 | 374,272 | 0.749 M | 37.4 MFLOP/s |

⇒ 0.1–0.75 MFLOP per step. Versus Nano GPU 472 GFLOPS (VERIFIED) this is < 1e-4 of one second of peak; on the A57 CPU, even an assumed 1 GFLOP/s effective single-thread rate gives ≈0.4 ms per inference (assumption, not measured). Inference is not the bottleneck; OS jitter, I/O latency and software stack age are.

### B.3 Published low-cost deployments (what runs the walking policy)

| Robot | Onboard computer | Bus / rates | Source | Evidence |
|---|---|---|---|---|
| **Berkeley Humanoid Lite** (22 DoF, "under $5,000") | "BeeLink N95 NUC computer" (Intel N95 mini-PC), Ubuntu 22.04 | 4 CAN buses `can0..can3` = L-arm (5), R-arm (5), L-leg (6), R-leg (6); USB-CAN via `gs_usb`, "bitrate 1000000" (classic CAN 1 Mbit/s); motor controllers = Recoil firmware on **ST B-G431B-ESC1**; policy ONNX; `control_dt: 0.004` (250 Hz), `policy_dt: 0.04` (25 Hz, 22-DoF) / 0.02 (50 Hz, biped); PDO2 = target position + velocity "in fp32 format" (8 bytes); "If running into performance issues where the USB-CAN adapter cannot maintain the required communication frequency, we can use the xanmod real-time kernel" | https://berkeley-humanoid-lite.gitbook.io/docs/getting-started-with-software/the-on-board-computer.md ; https://berkeley-humanoid-lite.gitbook.io/docs/in-depth-contents/can-communication.md ; https://berkeley-humanoid-lite.gitbook.io/docs/llms-full.txt ; https://raw.githubusercontent.com/HybridRobotics/Berkeley-Humanoid-Lite/main/configs/policy_humanoid.yaml ; https://raw.githubusercontent.com/HybridRobotics/Berkeley-Humanoid-Lite/main/configs/policy_biped_50hz.yaml ; https://arxiv.org/abs/2504.17249 | VERIFIED |
| ToddlerBot (30 active DoF) | "Jetson Orin NX 16GB" | actuator bus/frequency not on page | https://toddlerbot.github.io/ | VERIFIED (computer) |
| Open Duck Mini v2 | "Raspberry pi zero 2w" runs the ONNX walking policy | Feetech servos (runtime README) | https://github.com/apirrone/Open_Duck_Mini ; https://raw.githubusercontent.com/apirrone/Open_Duck_Mini_Runtime/v2/README.md | VERIFIED |
| Jetson-Nano-hosted RL humanoid walking | – | no primary example found today (web search budget exhausted) | – | UNVERIFIED |

BHL bus-load cross-check with the Part C model: 6 joints x 2 frames x 111–135 bit x 250 Hz = 33.3–40.5 % per bus → consistent with running classic CAN at 250 Hz (ESTIMATED).

### B.4 Feasibility conclusion (Jetson Nano as JX1 high-level computer)

1. **Compute: sufficient.** An MLP walking policy (0.1–0.75 MFLOP/step at 25–50 Hz) is trivial for the Nano (472 GFLOPS GPU, 4x A57); Open Duck Mini walks on a Pi Zero 2W and BHL on an Intel N95. Light perception (1–2 CSI cameras, TensorRT 8.2 detection) also fits (performance not measured here).
2. **Real risks are software/lifecycle, not FLOPs:** JetPack 4.6.6 is the final JP4 (kernel 4.9, Ubuntu 18.04, CUDA 10.2, TRT 8.2); no native ROS 2 (Humble only via a 2023 community container); jetson-containers dropped JP4; kernel 4.9 lacks mcp251xfd and gs_usb CAN-FD; module listed until January 2027, dev kit EOL.
3. **No CAN on the Nano** → put all hard-real-time CAN work on MCUs (Part C). The Nano should talk to one "CAN hub" MCU board (e.g. STM32G474, 3x FDCAN) over USB/UART/SPI and send setpoints at the policy rate (25–50 Hz); the hub interpolates and runs the 500 Hz bus schedule. Data rate hub↔Nano at 500 Hz: 24 joints x (8 B cmd + 16 B state) x 500 = 288 kB/s (≈2.3 Mbit/s payload) → fits USB Full-Speed or 10+ MHz SPI (ESTIMATED).
4. **Verdict:** FEASIBLE for the JX1 prototype (cheapest in-stock path ₹30,899.99 kit, or ₹29,988.99 module + carrier), provided CAN is MCU-bridged and ROS 2 is containerised or replaced by a lean C++/Python runtime. For any product or longer program, budget the Orin Nano (same 69.6 x 45 mm SO-DIMM, JetPack 6/7, supported to 2032, 1x native CAN; ₹49,999.99 kit) – plan carrier re-validation. A policy-only alternative with no GPU is RPi 5 8 GB (₹19,999.99) or an Intel N95/N100 mini-PC (BHL precedent; Indian price not checked).

---

## PART C – CAN vs CAN-FD for ~24 joints at 500–1000 Hz

### C.1 Frame-length model (formulas and sources)

**Classic CAN 2.0A (11-bit ID), s data bytes** – fields SOF 1, ID 11, RTR 1, IDE 1, r0 1, DLC 4, data 8s, CRC 15, CRC-del 1, ACK 2, EOF 7, IFS 3 (Wikipedia field list; VERIFIED https://en.wikipedia.org/wiki/CAN_bus).
- Unstuffed: 47 + 8s bits → **111 bits** for 8 bytes (incl. 3-bit IFS).
- Stuff rule: "a bit of opposite polarity is inserted after five consecutive bits of the same polarity"; CRC delimiter, ACK field and EOF are not stuffed (Wikipedia). Worst case stuff bits = ⌊(34 + 8s − 1)/4⌋ = 24 for s = 8 → **135 bits** (Wikipedia: base frame "≤ 132" bits incl. "≤ 24" stuff bits, excl. 3-bit IFS). 29-bit ID: 131–160 bits.
- At 1 Mbit/s: 111–135 µs per 8-byte frame.

**CAN FD base format, BRS = 1, n data bytes**
- Arbitration (nominal-rate) bits: SOF…BRS = 17, plus CRC-del, ACK slot, ACK-del, EOF 7, IFS 3 = 13 → 30 bits. (Bosch M_CAN: "the bit timing will be switched inside the frame, after the BRS (Bit Rate Switch) bit … switched back from the data phase timing at the CRC delimiter" – counting BRS and CRC-del at nominal rate is slightly conservative.)
- Data-phase bits: ESI 1 + DLC 4 + 8n + stuff count 4 (CiA: "The 3-bit stuff-bit counter is grey-coded and it is protected by a parity bit") + CRC 17 (n ≤ 16) or 21 (n > 16) (CiA) + fixed stuff bits 6 or 7 (CiA: "The CRC field use fixed stuff-bits (FSB)"; one FSB before the stuff count and one after every 4 bits → 6 for CRC-17, 7 for CRC-21 – count ESTIMATED from that rule).
- Dynamic stuffing (SOF … end of data) worst case = ⌊(22 + 8n − 1)/4⌋ bits, 4 of them in the arbitration phase.
- Sources: CiA "CAN FD – the basic idea" https://www.can-cia.org/can-knowledge/can-fd-the-basic-idea (arbitration phase "limited to 1 Mbit/s", data phase "limited by the transceiver characteristics"; 1:8 ratio → "approximately six times higher throughput"); Bosch: CAN FD "introduced by Bosch in 2012 … from up to 8 to up to 64 [bytes] … standardized as ISO11898-1:2015" https://www.bosch-semiconductors.com/ip-modules/can-protocols/can-fd/ ; Bosch M_CAN User's Manual rev 3.3.1 (the IP family behind STM32 FDCAN – UNVERIFIED linkage) https://www.bosch-semiconductors.com/media/ip_modules/pdf_2/m_can/mcan_users_manual_v331.pdf – "with a CAN clock frequency of 20MHz and the shortest configurable bit time of 4 tq, the bit rate in the data phase is 5 Mbit/s"; "Without transmitter delay compensation, the bit rate in the data phase of a CAN FD frame is limited by the transmitter delay" (all VERIFIED).

**Time per frame (ESTIMATED, best = no dynamic stuffing, worst = max stuffing)**

| Frame | 1 / 2 Mbit/s | **1 / 5 Mbit/s** | 1 / 8 Mbit/s |
|---|---|---|---|
| Classic 8 B @ 1 Mbit/s | – | 111–135 µs | – |
| FD 8 B (CRC-17) | 78.0–90.5 µs | **49.2–56.6 µs** | 42.0–48.1 µs |
| FD 12 B | 94.0–110.5 | 55.6–64.6 | 46.0–53.1 |
| FD 16 B | 110.0–130.5 | 62.0–72.6 | 50.0–58.1 |
| FD 32 B (CRC-21) | 176.5–213.0 | 88.6–105.6 | 66.6–78.8 |
| FD 48 B | 240.5–293.0 | 114.2–137.6 | 82.6–98.8 |
| FD 64 B | 304.5–373.0 | 139.8–169.6 | 98.6–118.8 |

Note: for 8-byte payloads the 30-bit nominal-rate part (30 µs) dominates, so CAN-FD gives ≈2.3x (not 5x) per small frame; bigger gains need bigger (aggregated) frames.

### C.2 Bus load per bus (ESTIMATED; % of bus time; 1 command + 1 response per joint per cycle)

Scenarios: **A** classic 8 B cmd + 8 B reply @1 Mbit/s; **B** FD 8 B + 8 B @1/5 Mbit/s; **C** FD one 64-B broadcast command per ≤6 joints + one 16-B reply per joint; **D** FD 8 B cmd + 16 B reply.

| Joints on bus | Loop | A classic | B FD 8+8 | C FD 64-B bcast + 16 B | D FD 8+16 |
|---|---|---|---|---|---|
| 24 (single bus) | 250 Hz | 133–162 % ✗ | 59.0–67.9 % | 51.2–60.5 % | 66.7–77.5 % |
| 24 (single bus) | 500 Hz | 266–324 % ✗ | 118–136 % ✗ | 102–121 % ✗ | 133–155 % ✗ |
| 24 (single bus) | 1000 Hz | 533–648 % ✗ | 236–272 % ✗ | 205–242 % ✗ | 267–310 % ✗ |
| 12 (2 buses) | 500 Hz | 133–162 % ✗ | 59.0–67.9 % | 51.2–60.5 % | 66.7–77.5 % |
| **6 (4 buses, one per limb)** | 250 Hz | 33.3–40.5 % | 14.8–17.0 % | 12.8–15.1 % | 16.7–19.4 % |
| **6 (4 buses)** | **500 Hz** | 66.6–81.0 % | **29.5–34.0 %** | 25.6–30.3 % | 33.4–38.8 % |
| **6 (4 buses)** | **1000 Hz** | 133–162 % ✗ | 59.0–67.9 % | 51.2–60.5 % | 66.7–77.5 % |
| 3 (8 buses) | 1000 Hz | 66.6–81.0 % | 29.5–34.0 % | 32.6–38.7 % | 33.4–38.8 % |

Max joints per bus (worst-case stuffing, 2 frames/joint/cycle): classic – 250 Hz: 7.4 (≤50 % load) / 10.4 (≤70 %); 500 Hz: 3.7 / 5.2; 1 kHz: 1.9 / 2.6. FD 1/5 Mbit/s (8 B+8 B) – 500 Hz: 8.8 / 12.4; 1 kHz: 4.4 / 6.2. (50–70 % is a common engineering ceiling to leave room for retransmissions, SDO/diagnostics and jitter – guideline, UNVERIFIED as a standard.)

Implied bus count for 24 joints: classic CAN needs ≈7 buses at 500 Hz (≤50 %) and ≈12–13 at 1 kHz (impractical); CAN-FD 1/5 Mbit/s needs 3 buses at 500 Hz (≤50 %) and 4–6 at 1 kHz (4 buses at 51–68 % or 6 buses of 4 joints at 39–45 %, scenario B: 4 x 2 x 56.6 µs x 1000 = 45.3 %).

### C.3 Recommendation

1. **Use CAN-FD, 1 Mbit/s arbitration / 5 Mbit/s data, 4 buses = one per limb** (L-leg 6, R-leg 6, L-arm+waist ≤6, R-arm+neck ≤6). Host↔joint exchange at **500 Hz** → 29.5–34 % load per bus (plenty of margin). Same topology as Berkeley Humanoid Lite (4 buses, one per limb), but FD lets JX1 double BHL's 250 Hz exchange rate.
2. **1 kHz** is possible on the 4-bus layout only at 51–68 % load (use the 64-byte broadcast command, scenario C) – or split each leg into 2 buses (6 buses total, ≤34 %). Recommended instead: keep 500 Hz on the bus and run joint PD/impedance locally at ≥1 kHz (FOC loop at 10–20 kHz) on each joint MCU, with the bus carrying (q_des, dq_des, kp, kd, τ_ff).
3. **Classic CAN fallback** (ESP32 TWAI, Blue Pill bxCAN, SN65HVD230, MCP2515): 4 buses x 6 joints only at ≤250–333 Hz (250 Hz: 33–41 %, the BHL operating point); 500 Hz on classic needs ≈7 buses.
4. **Silicon choices** (from Part A): joint MCU STM32G431 (1x FDCAN, Evelta ₹572.30 incl, 135 in stock) or the (sold-out) B-G431B-ESC1; hub MCU STM32G474 (3x FDCAN) – two hubs, or one G474 + one G431, for 4 buses; STM32H723 also has 3x FDCAN; Teensy 4.1 has only 1 FD-capable port. Transceivers: TJA1051T/3 (5 Mbit/s FD) or TJA1462 (8 Mbit/s SIC, Sharvi ₹102.36 ex); do **not** use SN65HVD230 or TCAN332 (non-G), which are 1 Mbps parts, on an FD bus.
5. **Do not mix ESP32 TWAI nodes onto FD buses**: Espressif – TWAI is "not compatible with FD format frames and will interpret such frames as errors".
6. **Jetson side**: no native CAN (B7) and no CAN-FD drivers in kernel 4.9 (B13) → connect the Nano to the hub MCU(s) by USB/UART/SPI, not directly to the FD buses. For bench debugging, MKS CANable V2.0 (₹3,899) works in classic mode on the Nano and in FD mode on a PC with Linux ≥ 5.18.
7. **Physical layer** (TI SLLA270, VERIFIED): ISO 11898 "maximum signaling rate of 1 Mbps with a bus length of 40 m and a maximum of 30 nodes", "maximum un-terminated stub length of 0.3 m", cable "shielded or unshielded twisted-pair with a 120-Ω characteristic impedance", "terminated at both ends with 120-Ω resistors" (https://www.ti.com/lit/an/slla270/slla270.pdf). For 5 Mbit/s keep daisy-chain topology with near-zero stubs (JST-GH pass-through on each joint PCB), bus length per limb < ~2 m (ESTIMATED, in-robot), 120 Ω at both ends only.
8. **Bit-timing example for STM32G4 FDCAN** (ESTIMATED – to be validated): FDCAN kernel clock 80 MHz, identical on every node. Nominal 1 Mbit/s: prescaler 1, 80 tq = 1 + 63 + 16 (sample point 80 %), SJW 16. Data 5 Mbit/s: prescaler 1, 16 tq = 1 + 11 + 4 (sample point 75 %), SJW 4, transmitter delay compensation ON with TDC offset = 12 tq. TDC is mandatory at this rate per the Bosch M_CAN manual quote above.

---

## Sources (primary, fetched 2026-09-24)

Indian stores: thinkrobotics.com, robocraze.com, quartzcomponents.com, evelta.com, electronicscomp.com, hubtronics.in, probots.co.in, zbotic.in, sharvielectronics.com, robokits.co.in (product URLs inline).
Vendor stores (USD): shop.odriverobotics.com, mjbots.com, flipsky.net, openlightlabs.com.
NVIDIA: https://developer.nvidia.com/embedded/jetpack-archive ; https://developer.nvidia.com/embedded/linux-tegra-r3276 ; https://developer.nvidia.com/jetpack-sdk-466 ; https://developer.nvidia.com/embedded/jetson-nano ; https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-nano/product-development/ ; https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-orin/ ; https://developer.nvidia.com/embedded/lifecycle ; https://developer.nvidia.com/blog/nvidia-jetson-orin-nano-developer-kit-gets-a-super-boost/ ; https://developer.nvidia.com/blog/solving-entry-level-edge-ai-challenges-with-nvidia-jetson-orin-nano/ ; https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/hardware_layout.html
ROS/containers: https://raw.githubusercontent.com/ros-infrastructure/rep/master/rep-2000.rst ; https://github.com/dusty-nv/jetson-containers ; https://raw.githubusercontent.com/dusty-nv/jetson-containers/legacy/README.md ; Docker Hub dustynv/ros tags API.
Linux kernel: https://github.com/torvalds/linux (tags v4.9, v5.4, v5.9, v5.10, v5.15–v5.19, v6.0, v6.1).
ST CMSIS headers: https://github.com/STMicroelectronics/cmsis_device_g4 ; https://github.com/STMicroelectronics/cmsis_device_h7
CAN: https://en.wikipedia.org/wiki/CAN_bus ; https://www.can-cia.org/can-knowledge/can-fd-the-basic-idea ; https://www.bosch-semiconductors.com/ip-modules/can-protocols/can-fd/ ; https://www.bosch-semiconductors.com/media/ip_modules/pdf_2/m_can/mcan_users_manual_v331.pdf ; https://www.ti.com/lit/an/slla270/slla270.pdf ; https://www.ti.com/product/SN65HVD230 ; https://www.ti.com/product/TCAN332 ; https://www.nxp.com/products/TJA1051 ; https://www.nxp.com/products/TJA1462 ; https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/twai.html ; https://www.pjrc.com/store/teensy41.html
Robots: https://berkeley-humanoid-lite.gitbook.io/docs/llms-full.txt ; https://github.com/HybridRobotics/Berkeley-Humanoid-Lite ; https://arxiv.org/abs/2504.17249 ; https://toddlerbot.github.io/ ; https://github.com/apirrone/Open_Duck_Mini ; https://github.com/apirrone/Open_Duck_Mini_Runtime

## Gaps / not verified today
- mouser.in INR prices (bot wall), LCSC import prices (blocked), st.com/microchip.com datasheets (timeout/403): ATA6561, MCP2562FD, MCP2518FD specs UNVERIFIED.
- AS5047P/AS5048A/MT6701/MT6835 boards, ICM-42688-P breakout, MCP2518FD module, WeAct G4 boards, ODrive/VESC/moteus, Micro-Fit 3.0, diametric magnets: not found at readable Indian stores (robu.in covered by another agent).
- Jetson Nano dev-kit carrier mounting-hole pattern; Orin Nano dev-kit CAN header; published RL-walking deployment on a Jetson Nano specifically.
- Quartz GST treatment not stated.

Revision log: v1 2026-09-24 (Part A + B facts); v2 2026-09-24 (verified stock on Evelta/Hubtronics/Probots/electronicscomp product pages, RPi 5 rows, import refs A9, ST FDCAN counts, transceiver rate limits, kernel driver checks, BHL/ToddlerBot/Open Duck evidence, Part C calculations & recommendation).
