# JX0 India sourcing (RAW)

**Date: 2026-09-24.** **Method:** live store checks on 2026-09-24.
- **Robu.in:** in-app browser, using the site's own search API (`POST /api/search/`, the same call the search page makes) plus product pages.
- **Shopify stores (Robocraze, ThinkRobotics, Quartz Components, Indian Hobby Center):** curl of `search/suggest.json` and `products/<handle>.js`, which give variant-level price and availability.
- **Evelta, ElectronicsComp, Probots, Hubtronics, Zbotic, IndustryBuying:** curl of search and product pages.
- **Waveshare specs:** waveshare.com wiki, product pages, 2D drawing zip and memory-table spreadsheets.

Nothing was bought. No accounts were created and no forms were filled.

Project: JX0, a ~45 cm, ~2 kg 3D-printed hobby humanoid; total budget under ₹50,000; student build in India.

**Legend**
- **GST incl.?**
  - **Yes:** the page states the price includes GST. Robu shows "(Incl. GST)". Robocraze shows "Incl. GST (No Hidden Charges)". Evelta shows "inc. GST" and "ex. GST" side by side. IndustryBuying shows "(Incl. of all taxes)". Probots and Zbotic show the GST split. Hubtronics shows "Ex Tax" under the incl. price.
  - **Ex:** the page gives the price without GST. ElectronicsComp shows "(Excluding 18% GST)". For those rows I add the incl. figure as ×1.18, marked "calc".
  - **Not stated:** no GST wording found on the product page or the policy pages checked (ThinkRobotics, Quartz Components, Indian Hobby Center).
- **Stock**
  - **IN:** Robu API `in_stock=true` or "Add to Cart"; Shopify variant `available=true`; or a stock count on the page.
  - **OOS:** out of stock or sold out.
  - **BO:** backorder.
- Prices are ₹ as displayed on 2026-09-24. They are not landed cost, and shipping is not included.
- "Reputable store" here means Robu, Robocraze, ThinkRobotics, Quartz Components, Evelta, ElectronicsComp, Indian Hobby Center (IHC) or Probots. IndustryBuying (IB) is used only when none of those had the part.

---

## A. Servos

### A1. Waveshare ST3215 / Feetech STS3215 / ST3215-HS

| Item | Product title (as listed) | Store | Price ₹ | GST incl.? | Stock | URL | Note |
|---|---|---|---|---|---|---|---|
| ST3215 7.4 V | Waveshare ST3215 Serial Bus Servo, 360° Encoder, 19.5kg.cm @ 7.4V (SKU R258500) | Robu | 2,159 | Yes | IN | https://robu.in/product/waveshare-st3215-serial-bus-servo/ | Confirms ₹2,159. Page text: "Torque:19.5kg.cm@7.4V", "Operating Voltage:4V ~ 7.4V", "0.192sec / 60°(52RPM)@7.4V", 1 Year Warranty. The page's `<title>` says "30kg.cm", which conflicts with the listing. |
| ST3215 7.4 V | ST3215 Series Serial Bus Servo, High precision and torque, 360 Degrees Magnetic Encoder, variant "19.5kg.cm@7.4V" (SKU WVSH0593) | ThinkRobotics | 2,399.99 | Not stated | IN | https://thinkrobotics.com/products/st3215-series-serial-bus-servo | Same page also has the 12 V variant (next row) |
| ST3215 12 V | same page, variant "30kg.cm@12V" (SKU WVSH0241) | ThinkRobotics | 2,649.99 | Not stated | IN | https://thinkrobotics.com/products/st3215-series-serial-bus-servo | – |
| ST3215 12 V | Waveshare 30KG Serial Bus Servo (SKU 1331215) | Robu | 2,599 | Yes | IN | https://robu.in/product/waveshare-30kg-serial-bus-servo/ | Listing text: "Model: ST3215 serial bus servo", "Operating voltage: 6 - 12V" |
| ST3215 12 V | Waveshare 360° 30KG Serial Servo with High Precision & Torque | Robocraze | 2,599 | Yes | IN | https://robocraze.com/products/waveshare-30kg-serial-servo-with-360-magnetic-encoder-high-precision | – |
| Feetech STS3215 7.4 V | ST3215 - 7.4V 19Kg 1/345 Gear Dual Axis TTL String Servo Motor (brand Feetech, MPN STS3215-C001) | Evelta | 2,224.30 (1,885.00 ex) | Yes (both shown) | IN (80) | https://evelta.com/st3215-7-4v-19kg-1-345-gear-dual-axis-ttl-string-servo-motor/ | Evelta spec block: 19.5kg.cm@6V, 6-7.4V, 55±1g, "Horn Gear Spline: 25T" (see spec section) |
| Feetech STS3215 7.4 V (other gear ratios) | STS3215-C046 - 7.4V 1:147 … / STS3215-C044 - 7.4V 1:191 86RPM … | Evelta | 2,224.30 each (1,885.00 ex) | Yes | IN (60) / IN (25) | https://evelta.com/sts3215-c046-7-4v-1-147-magnetic-encoding-metal-gear-dual-axis-ttl-serial-bus-servo-motor/ | Faster, lower-ratio variants. C044 URL: https://evelta.com/sts3215-c044-7-4v-1-191-86rpm-metal-gear-dual-axis-ttl-serial-bus-servo-motor/ |
| Feetech STS3215 12 V | ST3215-C018 - 12V 30kg·cm Dual-Shaft TTL Serial Servo, Metal Gears, Magnetic Encoder (brand Feetech) | Evelta | 2,419.00 (2,050.00 ex) | Yes | IN (61) | https://evelta.com/st3215-c018-12v-30kg-cm-dual-shaft-ttl-serial-servo-metal-gears-magnetic-encoder/ | Evelta spec: 30kg.cm@12V stall, 10kg.cm@12V rated, 4-14V, "25T/OD5.9mm" spline |
| ST3215-HS | Waveshare 20kg.cm Bus Servo Motor, 106PRM High Speed, Large Torque, With 360 Degrees High Precision Magnetic Encoder (SKU 1738071) | Robu | 2,529 | Yes | IN | https://robu.in/product/waveshare-20kg-cm-bus-servo-motor-106prm-high-speed-large-torque-with-360-degrees-high-precision-magnetic-encoder/ | Listing: "ST3215-HS", 6 to 12.6 V |
| ST3215-HS | ST3215-HS 20kg.cm Bus Servo Motor, 106PRM High Speed (SKU WVSH0244) | ThinkRobotics | 2,699.99 | Not stated | IN | https://thinkrobotics.com/products/st3215-hs | – |
| ST3215-HS | Waveshare 20kg·cm High-Torque Bus Servo Motor, 106RPM with 360° Magnetic Encoder | Robocraze | 2,529 | Yes | OOS | https://robocraze.com/products/waveshare-20kg-cm-high-torque-bus-servo-motor | – |

**Recommended picks**
- **ST3215 (7.4 V):** Robu, ₹2,159 incl. GST, in stock. Alternatives: Evelta Feetech STS3215-C001 ₹2,224.30 incl. (80 in stock); ThinkRobotics ₹2,399.99.
- **Feetech STS3215 (7.4 V):** Evelta STS3215-C001, ₹2,224.30 incl. GST (80 in stock). No other store checked lists it as a separate product; ThinkRobotics has it only inside the SO-101 arm kit.
- **12 V version:** Evelta Feetech ST3215-C018, ₹2,419.00 incl. GST (61 in stock). Waveshare 12 V: Robu or Robocraze, ₹2,599 incl.
- **ST3215-HS:** Robu, ₹2,529 incl. GST, in stock.

### A2. Cheaper serial-bus servos (arms / head)

| Item | Product title (as listed) | Store | Price ₹ | GST incl.? | Stock | URL | Note |
|---|---|---|---|---|---|---|---|
| Waveshare SC09 | Waveshare 2.3kg Dual-axis Serial Bus Servo, Two-way Feedback, Servo/Motor Mode Switchable, Compact Size, 300 Rotation Angle | ElectronicsComp | 985.30 calc (835.00 ex) | Ex | IN (1) | https://www.electronicscomp.com/waveshare-23kg-dual-axis-serial-bus-servo-two-way-feedback-servo-motor-mode-switchable-compact-size-300-rotation-angle | Only 1 unit in stock |
| Waveshare SC09 | Waveshare 2.3kg Dual-axis Serial Bus Servo … 300° Rotation Angle (second listing) | ElectronicsComp | 1,233.10 calc (1,045.00 ex) | Ex | IN (32) | https://www.electronicscomp.com/waveshare-2.3kg-dual-axis-serial-bus-servo-two-way-feedback-servo-motor-mode-switchable-compact-size-300-rotation-angle | – |
| Waveshare SC09 | Waveshare 2.3kg Dual-axis Serial Bus Servo, Two-way Feedback, Servo/Motor Mode Switchable, Compact Size, 300° Rotation Angle (SKU 1592663) | Robu | 1,088 | Yes | IN | https://robu.in/product/waveshare-2-3kg-dual-axis-serial-bus-servo/ | The product page description calls it "SC09 Servo". Robu text says "Wide voltage input 4.8-8.4V", but Waveshare says 4~6V (see spec section). |
| Feetech SCS0009 | SCS0009 - 6V 2.3kg 300deg Serial BUS Servo Motor (brand Feetech) | Evelta | 1,074.91 (910.94 ex) | Yes | IN (182) | https://evelta.com/scs0009-6v-2-3kg-300deg-serial-bus-servo-motor/ | Evelta: 2.3kg.cm@6V, 0.7kg.cm rated, 13.2±1g, spline 20T |
| Waveshare ST3020 | Waveshare 25kg.cm Wide Range Voltage Serial Bus Servo, High Precision And Large Torque, With Programmable 360 Degrees Magnetic Encoder (SKU 1738072) | Robu | 2,618 | Yes | IN | https://robu.in/product/waveshare-25kg-cm-wide-range-voltage-serial-bus-servo-high-precision-and-large-torque-with-programmable-360-degrees-magnetic-encoder/ | Listing: "Product Type: ST3020 serial bus servo", 6 to 14 V (typ. 12V), 25kg.cm@12V, 12-bit encoder. Not on Robocraze, ThinkRobotics, Quartz, Evelta or ElectronicsComp. |
| Feetech STS3020 (different product) | STS3020 - 7.4V 20kg.cm 360deg Copper Metal Gear Digital Servo Motor | Evelta | 2,426.73 (2,056.55 ex) | Yes | IN (5) | https://evelta.com/sts3020-7-4v-20kg-cm-360deg-copper-metal-gear-digital-servo-motor/ | Feetech part, not the Waveshare ST3020 |
| Waveshare ST3025 | Waveshare 40kg.cm Metal Serial Bus Servo with Brushless Motor & 360° Magnetic Encoder | Robocraze | 10,299 | Yes | IN | https://robocraze.com/products/waveshare-40kg-cm-metal-serial-bus-servo-with-brushless-motor | Not cheaper than ST3215 |
| Waveshare ST3025 | ST3025 40kg.cm Metal Serial Bus Servo, High Precision And Large Torque (SKU WVSH0243) | ThinkRobotics | 10,299.99 | Not stated | IN | https://thinkrobotics.com/products/40kg-cm-metal-serial-bus-servo-high-precision-and-large-torque | – |
| Waveshare ST3025 | Waveshare 40kg.cm Metal Serial Bus Servo … Brushless Motor (SKU 1738073) | Robu | 9,259 | Yes | OOS | https://robu.in/product/waveshare-40kg-cm-metal-serial-bus-servo-high-precision-and-large-torque-with-programmable-360-degrees-magnetic-encoder-and-brushless-motor/ | – |
| Feetech STS3032 | STS3032 - 6V 4.5kg 360deg Serial Bus Servo Motor | Evelta | 3,451.65 (2,925.13 ex) | Yes | OOS | https://evelta.com/sts3032-6v-4-5kg-360deg-serial-bus-servo-motor/ | Not found on Robu, Robocraze, ThinkRobotics or Quartz |
| Feetech ST-3032 | ST-3032-C001 - 6V 4.5kg.cm 360deg Metal Gear Single-Axis TTL Serial Bus Servo Motor | Evelta | 3,451.65 calc (2,925.13 ex) | Yes | IN (15) | https://evelta.com/st-3032-c001-6v-4-5kg-cm-360deg-metal-gear-single-axis-ttl-serial-bus-servo-motor/ | – |
| Feetech ST-3032 | ST-3032-C036 - 6V 4.5kg.cm 360deg Dual-Axis Metal Case Steel Gear Serial Bus Servo Motor | Evelta | 3,872.77 calc (3,282.01 ex) | Yes | IN (5) | https://evelta.com/st-3032-c036-6v-4-5kg-cm-360deg-dual-axis-metal-case-steel-gear-serial-bus-servo-m | URL is as shown in the Evelta search result (it looks truncated) |
| Hiwonder LX-16A | Hiwonder LX-16A Full Metal Gear Serial Bus Servo with Real-Time Feedback Function for RC Robot | ThinkRobotics | 2,099.99 | Not stated | IN | https://thinkrobotics.com/products/hiwonder-lx-16a-full-metal-gear-serial-bus-servo-with-real-time-feedback-function-for-rc-robot-control-angle-240 | Not found on Robu, Robocraze, Evelta or ElectronicsComp |
| Hiwonder LX-15D | Hiwonder LX-15D Intelligent Serial Bus Servo with RGB Indicator for Displaying Robot Status | ThinkRobotics | 2,899.99 | Not stated | IN | https://thinkrobotics.com/products/hiwonder-lx-15d-intelligent-serial-bus-servo-with-rgb-indicator-for-displaying-robot-status | – |
| Hiwonder LX-15D | same title (SKU R134529) | Robu | 2,809 | Yes | OOS | https://robu.in/product/hiwonder-lx-15d-intelligent-serial-bus-servo-with-rgb-indicator-for-displaying-robot-status/ | – |
| Hiwonder LX-224 | Hiwonder LX-224 Serial Bus Servo with Three Connectors /20KG Large Torque | ThinkRobotics | 2,899.99 | Not stated | IN | https://thinkrobotics.com/products/hiwonder-lx-224-serial-bus-servo-with-three-connectors-20kg-large-torque | – |
| Hiwonder LX-224HV | Hiwonder LX224 HV servo motor (SKU R140355) | Robu | 2,089 | Yes | IN | https://robu.in/product/hiwonder-lx224-hv-servo-motor/ | HV version. ThinkRobotics sells LX-224HV at ₹3,499.99 (IN). |
| (extra) Waveshare SC15 | Waveshare SC15 17kg Large Torque Programmable Serial Bus Servo (SKU 1219081) | Robu | 2,069 | Yes | IN | https://robu.in/product/waveshare-sc15-17kg-large-torque-programmable-serial-bus-servo/ | Listing: 4.8-8.4V, 180°/1024, 38400bps–1Mbps. ThinkRobotics ₹2,099.99 (IN). |

**Recommended picks**
- **SC09:** ElectronicsComp, ₹985.30 incl. (₹835 + 18% GST), but only 1 unit is in stock. For several units: Evelta Feetech SCS0009 ₹1,074.91 incl. (182 in stock) or Robu Waveshare SC09 ₹1,088 incl.
- **ST3020:** Robu, ₹2,618 incl. GST, in stock.
- **ST3025:** Robocraze, ₹10,299 incl. GST, in stock. This is about 4.8× the ST3215 price.
- **STS3032:** Evelta ST-3032-C001, ₹3,451.65 incl. (15 in stock). The plain STS3032 listing is out of stock.
- **LX-16A:** ThinkRobotics, ₹2,099.99 (GST not stated), in stock.
- **LX-15D:** ThinkRobotics, ₹2,899.99, in stock.
- **LX-224:** ThinkRobotics, ₹2,899.99, in stock. The HV version at Robu is ₹2,089 incl.
- **Price note:** none of the ST3020, ST3025, STS3032 or LX-series servos is cheaper than the Robu ST3215 at ₹2,159. Only the SC09/SCS0009 class, at about ₹985–1,088, is cheaper.

### A3. PWM servos (comparison)

| Item | Product title (as listed) | Store | Price ₹ | GST incl.? | Stock | URL | Note |
|---|---|---|---|---|---|---|---|
| MG90S | Tower Pro MG90S Servo Motor with Metal Gear | Quartz | 124 | Not stated | IN | https://quartzcomponents.com/products/tower-pro-mg90s-servo-motor-with-metal-gear | – |
| MG90S | TowerPro MG90S Mini Digital Servo Motor (180° Rotation)-Normal Quality (SKU 1308083) | Robu | 125 | Yes | IN | https://robu.in/product/towerpro-mg90s-mini-digital-servo-motor-180-rotation-standard-quality/ | Robu "High Quality" MG90S (SKU 23904) is ₹279 |
| MG90S | MG90S Mini Servo Motor (180 Degree) | Robocraze | 145 | Yes | IN | https://robocraze.com/products/mg90s-servo-motor | – |
| SG90 | Tower Pro SG90 Servo Motor - 9 gms Mini/Micro Servo Motor | Quartz | 86 | Not stated | IN | https://quartzcomponents.com/products/tower-pro-sg90-servo-9-gms-mini-micro-servo-motor | – |
| SG90 | TowerPro SG90 Mini Servo - 180 degree Rotation - Standard Quality (SKU 5764) | Robu | 89 | Yes | IN | https://robu.in/product/towerpro-sg90-9g-mini-servo-9-gram/ | "Good Quality" SG90 is ₹198 |
| SG90 | TowerPro SG90 9G Micro Servo Motor 180° for Arduino & Robotics | Robocraze | 99 | Yes | IN | https://robocraze.com/products/sg90-micro-servo-motor | – |
| MG996R | MG996R Tower Pro Digital Metal Gear High Torque Servo Motor (180 Degree Rotation) | Quartz | 259 | Not stated | IN | https://quartzcomponents.com/products/mg996 | Quartz 360° version ₹254 |
| MG996R | MG996R Metal Gear Servo Motor - 180 Degree | Robocraze | 399 | Yes | IN | https://robocraze.com/products/mg996r-servo-motor | – |
| MG996R | TowerPro MG996R Digital High Torque Servo Motor(180° Rotation) (SKU 1070680) | Robu | 409 | Yes | IN | https://robu.in/product/towardpro-mg996r-digital-high-torque-servo-motor/ | – |

**Recommended picks**
- **MG90S:** Quartz, ₹124, in stock.
- **SG90:** Quartz, ₹86, in stock.
- **MG996R:** Quartz, ₹259 (180°), in stock.

### A4. Serial-bus servo driver boards

| Item | Product title (as listed) | Store | Price ₹ | GST incl.? | Stock | URL | Note |
|---|---|---|---|---|---|---|---|
| Waveshare Bus Servo Adapter (A) | – | Robu, Robocraze, ThinkRobotics, Quartz, Evelta, ElectronicsComp | – | – | NOT FOUND | – | No listing with this name in any store searched |
| Waveshare Serial Bus Servo Driver Board | Serial Bus Servo Driver (SKU WVSH0166) | ThinkRobotics | 499.99 | Not stated | IN | https://thinkrobotics.com/products/serial-bus-servo-driver | Page: controls up to 253 ST/SC servos; "9~12.6V voltage input (the input voltage and the servo voltage must be matched)"; UART; 42.00 × 33.00 mm; mounting holes 2.50 mm at 37.00 × 28.00 mm |
| Waveshare Serial Bus Servo Driver Board | Waveshare Serial Bus Servo Driver Board, Integrates Servo Power Supply And Control Circuit, Applicable for ST/SC Series Serial Bus Servos (SKU 1782919) | Robu | 481 | Yes | OOS | https://robu.in/product/waveshare-serial-bus-servo-driver-board-integrates-servo-power-supply-and-control-circuit-applicable-for-st-sc-series-serial-bus-servos/ | – |
| Waveshare Serial Bus Servo Driver Board | same title | ElectronicsComp | 518.02 calc (439.00 ex) | Ex | OOS | https://www.electronicscomp.com/waveshare-serial-bus-servo-driver-board-integrates-servo-power-supply-and-control-circuit-applicable-for-st-sc-series-serial-bus-servos | – |
| Waveshare Serial Bus Servo Driver Board | Serial Bus Servo Driver Board 9~12.6V DC, Control up to 253 Servos | Evelta | 581.74 (493.00 ex) | Yes | OOS | https://evelta.com/serial-bus-servo-driver-board-9-12-6v-dc-control-up-to-253-servos/ | – |
| SmartElex serial bus servo driver | SmartElex Serial Bus Servo Driver Board, Integrates Servo Power Supply And Control Circuit (SKU R255565) | Robu | 509 | Yes | IN | https://robu.in/product/smartelex-serial-bus-servo-driver-board/ | Confirms ₹509. Listing: "253 servos control", "9–12.6V input", UART/USB. |
| SmartElex serial bus servo driver | SmartElex Serial Bus Servo Driver Board, Integrates Servo Power Supply and Control Circuit | Robocraze | 509 | Yes | IN | https://robocraze.com/products/smartelex-serial-bus-servo-driver-board-integrates-servo-power-supply-and-control-circuit | – |
| (related) 7.2 V buck for bus servos | Waveshare Serial Bus Servo DC Buck Adapter, Mini Module, Design for Serial Bus Servos, Easy to Use, 7.2V Buck Regulator (SKU R136622) | Robu | 479 | Yes | IN | https://robu.in/product/waveshare-serial-bus-servo-dc-buck-adapter-mini-module-design-for-serial-bus-servos-easy-to-use-7-2v-buck-regulator/ | ElectronicsComp lists it at ₹334 ex (stock not checked): https://www.electronicscomp.com/waveshare-serial-bus-servo-dc-buck-adapter-mini-module-design-for-serial-bus-servos-easy-to-use-72v-buck-regulator |
| (related) Feetech USB programmer | FE-URT-1 - RS485 Servo Bus Programmer, USB to TTL Serial Signal Converter | Evelta | 1,249.90 calc (1,059.24 ex) | Yes | IN (2) | https://evelta.com/fe-urt-1-rs485-servo-bus-programmer-usb-to-ttl-serial-signal-converter/ | – |
| (related) ESP32 driver board | Waveshare ESP32-Based General Driver board for Robots supports Wi-Fi & Bluetooth | Robocraze | 3,178 | Yes | IN | https://robocraze.com/products/waveshare-esp32-based-general-driver-board-for-robots-supports-wi-fi-bluetooth | Robocraze listing says it controls up to 253 ST3215 servos. ThinkRobotics ₹3,249.99. |

**Recommended pick**
- ThinkRobotics Waveshare Serial Bus Servo Driver, ₹499.99 (GST not stated), in stock.
- Alternative: SmartElex board, ₹509 incl. GST, at Robu or Robocraze, both in stock.
- Voltage flag (not tested): both boards list 9–12.6 V input, and Waveshare says the input voltage "must be matched" to the servo voltage. Check this before pairing them with 7.4 V ST3215 servos on a 2S pack.

---

## B. Compute

| Item | Product title (as listed) | Store | Price ₹ | GST incl.? | Stock | URL | Note |
|---|---|---|---|---|---|---|---|
| Raspberry Pi 5 4GB | Raspberry PI 5 Model B BCM2712 Arm Cortex-A76 4GB RAM 2.4GHZ Single Board Computer (SKU PRO4729) | Probots | 15,949 | Yes (13,516.10 + 2,432.90 GST) | IN | https://probots.co.in/raspberry-pi-5-model-b-bcm2712-arm-cortex-a76-4gb-ram-2-4ghz-single-board-computer.html | Only in-stock 4 GB found |
| Raspberry Pi 5 4GB | Raspberry Pi 5 Model 4GB RAM (SKU 1749032) | Robu | 13,409 | Yes | OOS | https://robu.in/product/raspberry-pi-5-model-4gb/ | Robu "Official Raspberry Pi 5 4GB Starter Kit" ₹16,149 is also OOS |
| Raspberry Pi 5 4GB | Raspberry Pi 5, variant 4GB (SKU SBC1067-4) | ThinkRobotics | 16,199.99 | Not stated | OOS | https://thinkrobotics.com/products/raspberry-pi-5 | – |
| Raspberry Pi 5 4GB | Raspberry Pi 5 Model with 4GB Ram | ElectronicsComp | 15,574.82 calc (13,199.00 ex) | Ex | OOS | https://www.electronicscomp.com/raspberry-pi-5-model-4gb | – |
| Raspberry Pi 5 8GB | Raspberry Pi 5 Model 8GB RAM (SKU 1749034) | Robu | 19,999 | Yes | IN | https://robu.in/product/raspberry-pi-5-model-8gb/ | – |
| Raspberry Pi 5 8GB | Raspberry Pi 5, variant 8GB (SKU SBC1067-8) | ThinkRobotics | 19,999.99 | Not stated | IN | https://thinkrobotics.com/products/raspberry-pi-5 | – |
| Raspberry Pi 4 2GB | Raspberry Pi 4 Model B, variant "2GB with Case" (SKU SBC1010) | ThinkRobotics | 6,999.99 | Not stated | IN | https://thinkrobotics.com/products/raspberry-pi-4-model-b | Variant includes a case |
| Raspberry Pi 4 2GB | Raspberry Pi 4 Model B with 2GB RAM (SKU 471148) | Robu | 6,449 | Yes | OOS | https://robu.in/product/raspberry-pi-4-model-b-with-2-gb-ram/ | – |
| Raspberry Pi 4 2GB | Raspberry Pi 4 Model B with 2GB Ram (Latest & Original) | ElectronicsComp | 9,379.82 calc (7,949.00 ex) | Ex | IN (4) | https://www.electronicscomp.com/raspberry-pi-4-model-b-with-2-gb-ram-india | – |
| Raspberry Pi 4 4GB | Raspberry Pi 4 Model B - 4GB RAM | Quartz | 9,695 | Not stated | IN | https://quartzcomponents.com/products/raspberry-pi-4-model-b-4-gb-ram | – |
| Raspberry Pi 4 4GB | Official Raspberry Pi 4 Model B 4GB RAM Development Board | Robocraze | 11,465 | Yes | IN | https://robocraze.com/products/raspberry-pi-4-model-b-4gb-ram | – |
| Raspberry Pi 4 4GB | Raspberry Pi 4 Model B with 4GB RAM (SKU 471149) | Robu | 11,469 | Yes | IN | https://robu.in/product/raspberry-pi-4-model-b-with-4-gb-ram/ | ThinkRobotics 4GB variant ₹12,449.99 (IN) |
| Raspberry Pi Zero 2 W | Raspberry Pi Zero 2 W (SKU 1124637) | Robu | 2,079 | Yes | OOS | https://robu.in/product/raspberry-pi-zero-2-w/ | – |
| Raspberry Pi Zero 2 W | Raspberry Pi Zero 2 W | Evelta | 1,748.76 (1,482.00 ex) | Yes | OOS (schema OutOfStock) | https://evelta.com/raspberry-pi-zero-2-w/ | – |
| Raspberry Pi Zero 2 W | Raspberry Pi Zero 2 W | ElectronicsComp | 2,358.82 calc (1,999.00 ex) | Ex | OOS | https://www.electronicscomp.com/raspberry-pi-zero-2-w-india | – |
| Raspberry Pi Zero 2 W | Raspberry Pi Zero 2W (SKU AI5307) | Zbotic | 1,648.46 (1,397.00 + GST) | Yes | OOS | https://zbotic.in/?s=raspberry+pi+zero+2+w&post_type=product | Search page |
| Raspberry Pi Zero 2 W | Raspberry Pi Zero 2W | Hubtronics | 2,360 (2,000 ex) | Yes | OOS ("Notify when available") | https://hubtronics.in/index.php?route=product/search&search=zero%202%20w | Search page |
| Official Pi 5 27 W PSU | Official 27W USB-C PD Power Supply for Raspberry Pi 5 - Black | Quartz | 1,063 | Not stated | IN | https://quartzcomponents.com/products/official-27w-usb-c-pd-power-supply-for-raspberry-pi-5-white-black | – |
| Official Pi 5 27 W PSU | Official Raspberry Pi 5 27W USB-C PD Power Supply (Black) | Robocraze | 1,204 | Yes | IN | https://robocraze.com/products/raspberry-pi-5-27w-usb-c-power-supply-black-colour | White version ₹1,255 |
| Official Pi 5 27 W PSU | Official 27W USB-C PD Power Supply for Raspberry Pi 5 - Black(Plug Type :IN) (SKU 1749014) | Robu | 1,255 | Yes | IN | https://robu.in/product/official-27w-usb-c-pd-power-supply-for-raspberry-pi-5-black/ | Evelta ₹1,091.50 incl. is OOS |
| Pi 5 Active Cooler | Official Raspberry Pi 5 Active Cooler Fan | Quartz | 438 | Not stated | IN | https://quartzcomponents.com/products/official-raspberry-pi-5-active-cooler | – |
| Pi 5 Active Cooler | Official Raspberry Pi 5 Active Cooler (SKU 1749017) | Robu | 519 | Yes | IN | https://robu.in/product/official-raspberry-pi-5-active-cooler/ | – |
| Pi 5 Active Cooler | Raspberry Pi 5 Active Cooler | Robocraze | 522 | Yes | IN | https://robocraze.com/products/raspberry-pi-active-cooler | Evelta ₹460.20 incl. is OOS |
| SanDisk 32 GB microSD | SanDisk Ultra Micro SD 32GB UHS-I, 120MB/s R , Class 10 Memory Card | Quartz | 1,499 | Not stated | IN | https://quartzcomponents.com/products/32gb-ultra-microsd-memory-card-red-grey | Description: "Class 10, UHS-I, A1" |
| SanDisk 32 GB microSD | SanDisk Ultra GO micro SDHC 32GB UHS-I, 120MB/s R , Class 10 Memory Card (SKU R268040) | Robu | 1,629 | Yes | IN | https://robu.in/product/sandisk-ultra-go-micro-sdhc-32gb-uhs-i-120mbs-r-class-10-memory-card/ | A1/A2 class not in title. Robu SanDisk Ultra 32GB (SKU 544645) ₹1,519 is OOS. |
| SanDisk 32 GB microSD | SanDisk 32GB Micro SDHC Memory Card Class 10 A1 for Raspberry Pi | Robocraze | 1,549 | Yes | OOS | https://robocraze.com/products/sandisk-32gb-micro-sd-sdhc-card | – |
| 32 GB microSD A2 (not SanDisk) | Official Raspberry Pi 32GB Micro SD Card A2 Class | ThinkRobotics | 1,479.99 | Not stated | IN | https://thinkrobotics.com/products/official-raspberry-pi-32gb-micro-sd-card-a2-class-unprogrammed | Excluded: ThinkRobotics "SanDisk Extreme SDHC 90MBPS 32GB" (₹1,299.99) is a full-size SD card per its description, not microSD |

**Recommended picks**
- **Pi 5 4GB:** Probots, ₹15,949 incl. GST, in stock. It is out of stock at Robu, ThinkRobotics and ElectronicsComp.
- **Pi 5 8GB:** Robu, ₹19,999 incl. GST, in stock.
- **Pi 4 2GB:** ThinkRobotics "2GB with Case", ₹6,999.99, in stock.
- **Pi 4 4GB:** Quartz, ₹9,695, in stock.
- **Pi Zero 2 W:** no in-stock listing in any of 5 stores (Robu, Evelta, ElectronicsComp, Zbotic, Hubtronics). The lowest listed price is Zbotic ₹1,648.46 incl. (OOS).
- **27 W PSU:** Quartz, ₹1,063, in stock.
- **Active Cooler:** Quartz, ₹438, in stock.
- **SanDisk 32 GB microSD:** Quartz SanDisk Ultra A1, ₹1,499, in stock. The cheapest A2 card found is the non-SanDisk ThinkRobotics official Raspberry Pi card at ₹1,479.99.

---

## C. IMU breakouts

| Item | Product title (as listed) | Store | Price ₹ | GST incl.? | Stock | URL | Note |
|---|---|---|---|---|---|---|---|
| MPU6050 | MPU6050 3-Axis Gyroscope/Accelerometer Sensor Module | Quartz | 127 | Not stated | IN | https://quartzcomponents.com/products/mpu6050-gyroscope-accelerometer-sensor | – |
| MPU6050 | MPU-6050 Triple-Axis Accelerometer & Gyroscope Module | Robocraze | 154 | Yes | IN | https://robocraze.com/products/mpu-6050-triple-axis-accelerometer-gyroscope-module | – |
| MPU6050 | SmartElex MPU-6050 3-Axis Accelerometer and Gyro Sensor Module (SKU R268095) | Robu | 444 | Yes | IN | https://robu.in/product/smartelex-mpu-6050-3-axis-accelerometer-and-gyro-sensor-module/ | Robu generic MPU-6050 (SKU 2846) ₹159 is OOS |
| BNO055 | 7Semi BNO055 9-DOF Absolute Orientation Sensor Breakout I2C Qwiic | Evelta | 1,341.66 (1,137.00 ex) | Yes | IN (392) | https://evelta.com/7semi-bno055-9-dof-absolute-orientation-sensor-breakout-i2c-qwiic/ | – |
| BNO055 | BNO055 9-DOF Absolute Orientation Sensor | ThinkRobotics | 1,349.99 | Not stated | IN | https://thinkrobotics.com/products/9-dof-absolute-orientation-bno055-sensor | – |
| BNO055 | BNO055 9-DOF Absolute Orientation Sensor Breakout with I2C Qwiic - 7Semi | Robocraze | 1,359 | Yes | IN | https://robocraze.com/products/bno055-9-dof-absolute-orientation-sensor-breakout-with-i2c-qwiic-7semi | Robu "Bosch BNO055, 9-Axis…" (SKU R231480) ₹1,439 IN |
| BNO085 | 7Semi BNO085 9-DOF Orientation IMU Fusion Nano Breakout | Evelta | 2,094.50 (1,775.00 ex) | Yes | IN (21) | https://evelta.com/7semi-bno085-9-dof-orientation-imu-fusion-nano-breakout/ | – |
| BNO085 | BNO085 9-DOF Orientation IMU Sensor Fusion Nano Breakout Board | Robocraze | 2,095 | Yes | IN | https://robocraze.com/products/bno085-9-dof-orientation-imu-sensor-fusion-nano-breakout-board | – |
| BNO085 | SmartElex 9-DOF Orientation IMU Fusion Breakout - BNO085 (SKU R268085) | Robu | 2,409 | Yes | IN | https://robu.in/product/smartelex-9-dof-orientation-imu-fusion-breakout-bno085/ | Adafruit BNO085 at Robu ₹4,299 IN |
| ICM-20948 | ICM-20948 9DoF IMU Breakout Board (MPU-9250 Upgrade) - 7Semi | Robocraze | 1,130 | Yes | IN | https://robocraze.com/products/icm-20948-9dof-imu-breakout-board-mpu-9250-upgrade-7semi | Not on ThinkRobotics or Quartz |
| ICM-20948 | SparkFun SEN-15335 9DoF IMU Breakout - ICM-20948 (SKU 637310) | Robu | 2,959 | Yes | IN | https://robu.in/product/sparkfun-9dof-imu-m0-razor-breakout-board-with-micro-sd-card-socket/ | URL slug differs from the title (as listed) |
| ICM-20948 | ICM-20948 Low Power 9 Axis MEMS Motion Tracking Device Sensor (SKU R263837) | Robu | 789 | Yes | OOS | https://robu.in/product/icm-20948-low-power-9-axis-mems-motion-tracking-device-sensor/ | – |

**Recommended picks**
- **MPU6050:** Quartz, ₹127, in stock.
- **BNO055:** Evelta 7Semi, ₹1,341.66 incl. (392 in stock).
- **BNO085:** Evelta 7Semi Nano, ₹2,094.50 incl. (21 in stock). Robocraze has it at ₹2,095 incl.
- **ICM-20948:** Robocraze 7Semi, ₹1,130 incl., in stock.

---

## D. Audio

| Item | Product title (as listed) | Store | Price ₹ | GST incl.? | Stock | URL | Note |
|---|---|---|---|---|---|---|---|
| INMP441 I2S mic | INMP441 MEMS High Precision Omnidirectional Microphone Module I2S | Quartz | 145 | Not stated | IN | https://quartzcomponents.com/products/inmp441-mems-high-precision-omnidirectional-microphone-module-i2s | – |
| INMP441 I2S mic | same title (SKU 975775) | Robu | 139 | Yes | OOS | https://robu.in/product/inmp441-mems-high-precision-omnidirectional-microphone-module-i2s/ | Robocraze ₹135 also OOS |
| MAX98357A amp | MAX98357 I2S 3W Class D Amplifier Audio Decoder Module | Quartz | 124 | Not stated | IN | https://quartzcomponents.com/products/max98357-3w-amplifier | – |
| MAX98357A amp | SmartElex I2S Audio Breakout - MAX98357A (SKU R196218) | Robu | 194 | Yes | IN | https://robu.in/product/smartelex-i2s-audio-breakout-max98357a/ | Listing: "3.2W at 4Ω, 10% THD, 1.8W at 8Ω … with 5V supply" |
| MAX98357A amp | SmartElex MAX98357A I2S Audio Breakout Amplifier for Raspberry Pi and Microcontrollers | Robocraze | 195 | Yes | IN | https://robocraze.com/products/smartelex-max98357a-i2s-audio-breakout-amplifier-for-raspberry-pi-and-microcontrollers | – |
| Speaker 3 W 4 Ω ~40 mm | – | Robu, Robocraze, ThinkRobotics, Quartz, IHC, Evelta, ElectronicsComp | – | – | NOT FOUND | – | No 3 W / 4 Ω small speaker found. Closest alternatives are in the next rows. |
| (alt) small speaker | 2030 Cavity Speaker, 8Ω 2W (Waveshare, SKU WVSH0095) | ThinkRobotics | 299.99 | Not stated | IN | https://thinkrobotics.com/products/2030-cavity-speaker-8%CF%89-2w | 8 Ω 2 W, 20 × 30 × 5.5 mm, PH1.25 connector, 6 g. Evelta lists the same speaker at ₹168.74 incl. (OOS). |
| (alt) 3 W speaker | DFRobot FIT0502 Stereo Enclosed Speaker - 3W 8Ω (SKU R261339) | Robu | 519 | Yes | IN | https://robu.in/product/dfrobot-fit0502-stereo-enclosed-speaker-3w-8%cf%89/ | 8 Ω, not 4 Ω |
| (alt) 4 Ω speaker | 4 ohm Speaker - 0.5W | ElectronicsComp | 53.10 calc (45.00 ex) | Ex | IN (1069) | https://www.electronicscomp.com/4-ohm-speaker-0.5-watt | Only 0.5 W |
| (alt) 4 Ω 4 W | MULTICOMP PRO … SPEAKER, MINIATURE, 4OHM, 4W, ABS-230-RC | IndustryBuying | 778 | Yes | "Ships within 20 days" | https://www.industrybuying.com/speakers-multicomp-pro-SAF.SPE.130485065 | Long lead time |
| USB mini microphone | USB Plug and Play Desktop Microphone for Raspberry Pi | Quartz | 185 | Not stated | IN | https://quartzcomponents.com/products/usb-plug-and-play-desktop-microphone-for-raspberry-pi | – |
| USB mini microphone | USB Microphone for Raspberry Pi (Color may Vary) | Robocraze | 199 | Yes | IN | https://robocraze.com/products/usb-microphone-for-raspberry-pi-color-may-vary | – |
| USB mini microphone | Raspberry Pi USB2.0 Mini Microphone | Robocraze | 279 | Yes | IN | https://robocraze.com/products/raspberry-pi-usb2-0-mini-microphone | Robu "Raspberry Pi USB Plug and Play Desktop Microphone" ₹183 is OOS |
| USB sound card | USB To 3.5mm Mic and Headphone Jack Stereo Headset Audio Adapter USB Sound Card 7.1 (SKU 51861) | Robu | 105 | Yes | IN | https://robu.in/product/usb-to-3-5mm-mic-and-headphone-jack-stereo-headset-audio-adapter-usb-sound-card-7-1-hot/ | – |
| USB sound card | 5.1 channel USB Sound Card for Raspberry Pi and Computers (SKU 815865) | Robu | 110 | Yes | IN | https://robu.in/product/5-1-channel-usb-sound-card-for-raspberry-pi-and-computers/ | – |
| USB sound card | Waveshare USB Sound Card, Driver-Free, for Raspberry Pi / Jetson Nano (SKU 1323472) | Robu | 779 | Yes | IN | https://robu.in/product/waveshare-usb-sound-card-driver-free-for-raspberry-pi-jetson-nano/ | – |

**Recommended picks**
- **INMP441:** Quartz, ₹145, in stock. It is out of stock at Robu and Robocraze.
- **MAX98357A:** Quartz, ₹124, in stock. Alternative: SmartElex at Robu, ₹194 incl.
- **3 W 4 Ω speaker:** NOT FOUND. The nearest in-stock option is the ThinkRobotics 2030 cavity speaker (8 Ω 2 W), ₹299.99.
- **USB mini mic:** Quartz, ₹185, in stock.
- **USB sound card:** Robu generic "7.1", ₹105 incl., in stock.

---

## E. Display

| Item | Product title (as listed) | Store | Price ₹ | GST incl.? | Stock | URL | Note |
|---|---|---|---|---|---|---|---|
| 1.28" round GC9A01 240×240 | 1.28 Inch TFT LCD Display Module Round 240*240 GC9A01 Driver SPI Interface with Soldering (SKU R267806) | Robu | 469 | Yes | IN | https://robu.in/product/128-inch-tft-lcd-display-module-round-240240-gc9a01-driver-spi-interface-with-soldering/ | – |
| 1.28" GC9A01 240×240 | 1.28 Inch TFT Display Module 240*240 GC9A01 Driver SPI Interface Red (SKU R267793) | Robu | 449 | Yes | IN | https://robu.in/product/128-inch-tft-display-module-240240-gc9a01-driver-spi-interface-red/ | Title does not say "round"; listing says "Display Color: Red". A "Square" variant (SKU R267805) is ₹459. |
| 1.28" round GC9A01 + touch | SmartElex 1.28 inch ROUND TFT LCD Module (SKU R257747) | Robu | 1,159 | Yes | IN | https://robu.in/product/smartelex-128-inch-round-tft-lcd-module/ | Listing: GC9A01 + CST816S capacitive touch |
| 1.28" round (Waveshare) | Waveshare 240×240 1.28inch Round LCD Display Module, 65K RGB (SKU WVSH0028) | ThinkRobotics | 1,499.99 | Not stated | IN | https://thinkrobotics.com/products/waveshare-1-28inch-lcd-module | Driver IC not in title |

**Recommended pick:** Robu R267806 (explicitly round, GC9A01), ₹469 incl. GST, in stock.

---

## F. Power

| Item | Product title (as listed) | Store | Price ₹ | GST incl.? | Stock | URL | Note |
|---|---|---|---|---|---|---|---|
| 2S LiPo 2200 mAh | GenX 7.4V 2S 2200mAh 40C / 80C Premium Lipo Lithium Polymer Battery | IHC | 1,499 | Not stated | IN | https://indianhobbycenter.com/products/genx-7-4v-2s-2200mah-40c-80c-premium-lipo-lithium-polymer-battery | Description: XT60 connector |
| 2S LiPo 2200 mAh | Pro- Range 7.4V 2200mAh 45C 2S Lithium Polymer Battery Pack (SKU 649553) | Robu | 1,629 | Yes | IN | https://robu.in/product/orange-2200mah-2s-45c-lithium-polymer-battery-pack-lipo/ | Listing: 133 g, 16×34×106 mm, JST-XH balance plug, 90C burst |
| 2S LiPo 2200 mAh | Pro-Range 7.4V 2200mAh 30C 2S Lithium Polymer Battery Pack (SKU 23768) | Robu | 1,399 | Yes | OOS | https://robu.in/product/orange-2200mah-2s-30c-60c-lithium-polymer-battery-pack-lipo/ | Bonka 2200 25C ₹1,339 and 45C ₹1,569 are also OOS at Robu |
| 2S LiPo ~3000 mAh | Bonka 7.4V 3300mAh 25C 2S Lithium Polymer Battery Pack (SKU 1891446) | Robu | 2,149 | Yes | IN | https://robu.in/product/bonka-7-4v-3300mah-25c-2s-lithium-polymer-battery-pack/ | – |
| 2S LiPo ~3000 mAh | Pro- Range 7.4V 3300mAh 25C 2S Lithium Polymer Battery Pack (SKU 649550) | Robu | 2,209 | Yes | IN | https://robu.in/product/orange-3300mah-2s-25c-7-4v-lithium-polymer-battery-pack-lipo/ | Listing: 166 g, 140×43×14 mm, JST-XH |
| Orange-brand 2S | Orange 7.4V 4200mAh 35C 2S Lithium Polymer Battery Pack (SKU 649551) | Robu | 2,599 | Yes | IN | https://robu.in/product/orange-4200mah-2s-35c-7-4v-lithium-polymer-battery-pack-lipo/ | No Orange-branded 2200–3000 mAh 2S pack in stock at Robu; Pro-Range listings use "orange-…" URL slugs |
| (caution) 2S "LiPo" | 7.4V Rechargeable LiPo Battery, variant 3800mAh (SKU ELC5066) | ThinkRobotics | 619.99 | Not stated | IN | https://thinkrobotics.com/products/7-4v-rechargeable-lipo-battery | The listing's own specs (3800 mAh, 25C, 50×40×10 mm, 40 g, JST-XH 2.54) look inconsistent for a 2S 3800 mAh pack; verify before buying |
| (not LiPo) 2S Li-ion | WATTNINE® 7.4V 2200mAh Rechargeable Lithium Battery Pack with Warranty (Includes BMS & Balance Pin) - 2S 1P | Quartz | 366 | Not stated | IN | https://quartzcomponents.com/products/copy-of-7-4v-rechargeable-lithium-battery-pack-with-warranty-includes-bms-balance-pin-2s-1p-1800mah-1 | 18650 cells, BMS, "Max. Discharge current - 2A" |
| Balance charger (B3) | B3 Lithium Battery Charger for 2S and 3S LiPo Batteries | Quartz | 294 | Not stated | IN | https://quartzcomponents.com/products/b3-lithium-battery-charger-for-2s-and-3s-lipo-batteries | 100–240 V AC in, 3 × 800 mA |
| Balance charger (B3) | I MAX B3 CHARGER (135) | Robocraze | 332 | Yes | IN | https://robocraze.com/products/b3-pro-li-po-battery-charger | – |
| Balance charger (B3) | Imax B3 AC Compact Balance Charger for 2S-3S LiPo | IHC | 349 | Not stated | IN | https://indianhobbycenter.com/products/imax-b3-ac-compact-balance-charger-for-2s-3s-lipo-1 | Robu IMAX B3 AC Pro (SKU 7364) ₹329 OOS; ThinkRobotics ₹819.99 OOS |
| Balance charger (B6) | IMAX B6 80W 6A Balance Charger/Discharger for LiIon, LiPo, LiFe , NiCd and NiMH - (1-6 Cells) | Quartz | 1,719 | Not stated | IN | https://quartzcomponents.com/products/imax-b6-80w-6a-charger-discharger-1-6-cells | IHC ₹1,825; Robocraze ₹1,948. Robu ₹2,079 is titled "(Copy)". Genuine SkyRC iMAX B6 V2 at Robu ₹3,279 (IN). |
| 5 V 5 A UBEC | UBEC-5V/5A (SKU 974872) | Robu | 409 | Yes | IN | https://robu.in/product/ubec-5v-5a/ | Listing: 5.5–35 V in (2–8S), 5 A continuous, 5.25 V ±0.5 V out |
| 5 V 5 A buck | MINI560 5V 5A DC-DC Step-Down Stabilized Voltage Module | Quartz | 65 | Not stated | IN | https://quartzcomponents.com/products/mini560-dc-dc-step-down-stabilized-voltage-module | Description: 6–24 V in, 5 V out, up to 5 A |
| 5 V 5 A buck | MINI560 Pro DC-DC 5V 5A Step-Down Stabilized Voltage Source Module (SKU R260412) | Robu | 89 | Yes | IN | https://robu.in/product/mini560-pro-dc-dc-5v-5a-step-down-stabilized/ | Listing: 6–24 V in |
| 5 V 5 A buck | SmartElex TPS565201DDCR Buck Module - 3.3V/5V, 5A (SKU R214563) | Robu | 396 | Yes | IN | https://robu.in/product/smartelex-tps565201ddcr-buck-module-3-3v-5v-5a/ | Listing: 4.5–17 V in |
| (not for 2S) 5 V 5 A buck | 24V/12V To 5V 5A Step Down Power Supply Buck Converter XY-3606 Power Convertor | Quartz | 137 | Not stated | IN | https://quartzcomponents.com/products/24v-12v-to-5v-5a-step-down-power-supply-buck-converter-xy-3606-power-convertor | Description: input 9–36 V, so a 7.4 V pack is below its input range |
| XL4015 (comparison) | XL4015 5A Adjustable Step Down Power Supply Buck Module | Quartz | 79 | Not stated | IN | https://quartzcomponents.com/products/xl4015-lithium-charger-dc-dc-adjustable-power-supply-module | IHC ₹89 (https://indianhobbycenter.com/products/dc-dc-adj-cccv-buck-5a); Robu ₹109 (SKU 1510171) |
| LM2596 (comparison) | LM2596 3A DC DC Buck Converter Power Supply Module | Quartz | 45 | Not stated | IN | https://quartzcomponents.com/products/lm2596-buck-converter-power-supply-module | Robocraze ₹48; Robu "LM2596S with SMD LED" ₹49 |
| XT60 pair | XT60 Connector Male Female Pair | Robocraze | 29 | Yes | IN | https://robocraze.com/products/xt60-connector-pair | – |
| XT60 pair | XT60 Connector - Male and Female Pair | Quartz | 32 | Not stated | IN | https://quartzcomponents.com/products/xt60 | IHC ₹35 (https://indianhobbycenter.com/products/xt60-connector-female) |
| XT60 pair (Amass) | Amass XT60 Gold Plated Bullet Battery Connector Pair - XT60-F.G.Y & XT60-M.G.Y (SKU R264640) | Robu | 62 | Yes | IN | https://robu.in/product/amass-xt60-gold-plated-bullet-battery-connector-pair-xt60-fgy-and-xt60-mgy/ | Brand Amass named in the title |
| 10 A switch | Toggle Switch 10A SPDT ON-OFF 125VDC and 250VAC - CALONIX Panel Mount Switch | Quartz | 63 | Not stated | IN | https://quartzcomponents.com/products/toggle-10a-spdt-on-off-calonix | Only 10 A switch found with a DC voltage rating in its listing |
| 10 A switch | 10A 250V AC SPST ON-OFF Black Oval Rocker Switch (SKU 704500) | Robu | 42 | Yes | IN | https://robu.in/product/10a-250v-ac-spst-on-off-round-rocker-switch/ | Listing: "Max 10A at 250VAC"; no DC rating given |
| 16 AWG silicone wire | 16AWG High Quality Ultra Flexible Silicone Wire - black (SKU R179510) | Robu | 49 per m | Yes | IN | https://robu.in/product/high-quality-ultra-flexible-16awg-silicone-wire-black/ | Page note: "1 Qty = 1 Meter". Red (R179511) is OOS; braided red (R257318) ₹54 IN, unit not checked. |
| 16 AWG silicone wire | 16AWG Silicone Wire Red ( 1 meter ) / Black ( 1 meter ) | Quartz | 68 / 65 per m | Not stated | IN | https://quartzcomponents.com/products/16awg-silicone-wire-red-1-meter-high-quality-ultra-flexible-for-battery-packs | – |
| 20 AWG silicone wire | 20AWG High Quality Ultra Flexible Silicone Wire - White (SKU 1824993) | Robu | 21 per m | Yes | IN | https://robu.in/product/high-quality-ultra-flexible-20awg-silicone-wire-1000m-white/ | Page note: "1 Qty = 1 Meter". Green and blue are IN; red and black are OOS. |
| 20 AWG silicone wire | 20AWG 2 Cores Silicone Wire Red-Black - 1 Meter | IHC | 125 | Not stated | IN | https://indianhobbycenter.com/products/20awg-multicore-insulated-cable-silicone-red-black-2-cores-1-meter | Single-colour 20 AWG (blue/white/yellow) ₹49 per 1 m |
| LiPo checker/alarm | Lithium/LiPo Battery Voltage Checker Tester for 1S-8S (Low Voltage Buzzer Alarm) for Lipo and NMC Battery Packs | Quartz | 98 | Not stated | IN | https://quartzcomponents.com/products/lipo-battery-vltage-testerlow-voltage-buzzer-alarm | – |
| LiPo checker/alarm | 1-8S Lipo Battery Voltage Tester (SKU 815782) | Robu | 109 | Yes | IN | https://robu.in/product/1-8s-lipo-battery-voltage-tester/ | Robocraze "LiPo Battery Voltage Tester" ₹118 IN |

**Recommended picks**
- **2S LiPo 2200 mAh:** IHC GenX 40C, ₹1,499 (GST not stated). Alternative: Robu Pro-Range 45C, ₹1,629 incl.
- **2S LiPo ~3000 mAh:** Robu Bonka 3300 mAh 25C, ₹2,149 incl.
- **Balance charger:** Quartz B3, ₹294.
- **5 V 5 A:**
  - UBEC: Robu UBEC-5V/5A, ₹409 incl.
  - Cheapest buck: Quartz MINI560, ₹65 (6–24 V input).
- **XL4015 / LM2596:** Quartz, ₹79 and ₹45.
- **XT60 pair:** Robocraze, ₹29 incl.
- **10 A switch:** Quartz CALONIX toggle, ₹63. The cheapest overall is the Robu rocker at ₹42, but it has an AC rating only.
- **16 AWG wire:** Robu, ₹49/m (black).
- **20 AWG wire:** Robu, ₹21/m (white, green or blue only).
- **LiPo checker:** Quartz, ₹98.

---

## G. Mechanical

| Item | Product title (as listed) | Store | Price ₹ | GST incl.? | Stock | URL | Note |
|---|---|---|---|---|---|---|---|
| PETG 1 kg 1.75 mm | Sunlu PETG Red 1.75mm Filament - 1kg Spool (SKU R171832) | Robu | 739 | Yes | IN | https://robu.in/product/sunlu-petg-red-1-75mm-1kg-roll-filament/ | ₹739 colours: red, yellow, green, cyan, purple. Transparent is ₹1,344. |
| PETG 1 kg 1.75 mm | Numakers PETG HS Filament – Pitch Black – 1.75 mm / 1 kg | IHC | 749 | Not stated | IN | https://indianhobbycenter.com/products/numakers-petg-hs-filament-pitch-black-1-75-mm-1-kg | – |
| PETG 1 kg 1.75 mm | 3D Printing Filaments PETG Pro 1kg, 1.75mm (Black) | Quartz | 759 | Not stated | IN | https://quartzcomponents.com/products/3d-printing-filaments-petg-pro-1kg-1-75mm-black | Brand not in title |
| PETG 1 kg 1.75 mm | Numakers PETG-HS Filament- Pitch Black (1.75mm/ 1kg Spool) (SKU 1665490) | Robu | 780 | Yes | IN | https://robu.in/product/numaker-petg-hs-filament-pitch-black-1-75-mm-1-kg/ | – |
| PETG 1 kg 1.75 mm | eSUN PETG+ Red - 1.75mm 3D Printing Filament Spool (SKU 323822) | Robu | 1,249 | Yes | IN | https://robu.in/product/esun-petg-1-75mm-3d-printing-filament-1kg-solid-red/ | ThinkRobotics eSun PETG ₹1,499.99: all 1.75 mm variants OOS. ThinkRobotics own-brand HS PETG ₹949.99 IN. No "Robu-brand" PETG found. |
| M2/M3 socket-screw assortment kit | 100pcs M3 12.9 Grade Alloy Steel Hex Bolt Socket Head Cap Screws Kit (SKU 1295634) | Robu | 429 | Yes | OOS | https://robu.in/product/100pcs-m3-12-9-grade-alloy-steel-hex-bolt-socket-head-cap-screws-kit/ | No in-stock M2 or M3 socket-head assortment kit found at Robu, Robocraze, ThinkRobotics, Quartz or IHC |
| M3 assortment (Phillips) | M3 Phillips head Assorted Fastening Kit from 6mm to 25mm - 180Pcs | Quartz | 252 | Not stated | IN | https://quartzcomponents.com/products/bolts-and-nuts-kit-m3 | Phillips head, not socket head |
| M3 socket screws (per size) | M3 X 8mm Hex Allen Socket Head SS202 Bolt (Pack of 10) | Quartz | 35 | Not stated | IN | https://quartzcomponents.com/products/m3-x-8mm-hex-allen-socket-head-screwpack-of-10 | Quartz M3×10 ₹47 and M3×12 ₹43 (packs of 10). IHC M3×10 SS202 ₹35, M3×20/25 12.9 black ₹59 (packs of 10). |
| M2 socket screws (per size) | M2x6mm Hex (Allen) Socket Head High Tensile(12.9) Black Oxide Screw (Pack of 10) | IHC | 49 | Not stated | IN | https://indianhobbycenter.com/products/m2-x-6mm-hex-allen-socket-head-high-tensile12-9-black-oxide-screw-copy | IHC M2×8 ₹59, M2×10 ₹49, M2×12 ₹75 (packs of 10). Robu EasyMech M2×6 socket + nut set of 12 ₹239. |
| M3 heat-set inserts | M3x4 mm Brass Heat Set Threaded Round Insert Nut (25Pcs) (SKU 260977) | Robu | 91 | Yes | IN | https://robu.in/product/m3-x-4-mm-brass-heat-set-knurl-threaded-round-insert-nut-25-pcs/ | ₹3.64 each. Robu M3×6 25 pcs also ₹91. |
| M3 heat-set inserts | M3x4x4.2mm Brass Heat Set Threaded Round Insert Nut - 10 Pcs. | Quartz | 43 | Not stated | IN | https://quartzcomponents.com/products/m3-x-4mm-brass-heat-set-threaded-round-insert-nut-10-pcs | ₹4.30 each |
| M3 heat-set inserts (kit) | Brass Heat Set Insert Nut Hot Melt Knurled Threaded M3 400PCS Kit (SKU R267266) | Robu | 1,519 | Yes | IN | https://robu.in/product/brass-heat-set-insert-nut-hot-melt-knurled-threaded-m3-400pcs-kit/ | ThinkRobotics M3 × 4.5 mm pack of 10 ₹64.99 is OOS |
| 623ZZ (3×10×4) | 623 ZZ Bearings Limiting Robotics Projects (3 x 10 x 4 mm) - Double Metal Shielded | Quartz | 25 | Not stated | IN | https://quartzcomponents.com/products/623-zz-bearings-limiting-robotics-projects-3-x-10-x-4-mm-radial-bearing | Quantity not stated in title (single variant) |
| 623ZZ | 623ZZ Radial Ball Bearing for 3D Printer/ Robot (4Pcs) (SKU 52567) | Robu | 84 per 4 | Yes | IN | https://robu.in/product/radial-ball-bearing-623zz-3d-printer-robot-4pcs/ | ₹21 each; listing says ABEC-3. Robocraze single ₹25 IN. |
| 624ZZ (4×13×5) | 624 ZZ 4mm Radial Ball Bearings (4x13x5mm) - Double Metal Shielded | Quartz | 18 | Not stated | IN | https://quartzcomponents.com/products/624-zz-invento-4mm-radial-ball-bearings-4x13x5mm-invento-bearing | Robu 4 pcs ₹78 (SKU 52536); Robocraze single ₹26 |
| 693ZZ (3×8×4) | 693 ZZ Ball Bearings Miniature Carbon Steel Bearings (3mm x 8mm x 4 mm) - Double Metal Shielded | Quartz | 31 | Not stated | IN | https://quartzcomponents.com/products/693zz-ball-bearings-miniature-carbon-steel-bearings-3mm-x-8mm-x-4-mm-deep-groove-bearing | Not on Robu or Robocraze. IB MonotaRO 693ZZ ₹778 (ships within 19 days). |
| MR63ZZ (3×6×2.5) | Invento Radial Ball Bearing Steel 3 mm Inner and 6 mm Outer Diameter, MR63ZZ (Pack of 10) | IndustryBuying | 1,297 per 10 | Yes | "Ships within 6 days" (schema InStock) | https://www.industrybuying.com/deep-groove-ball-bearings-invento-BEA.RAD.65121362 | Other variants on the page: pack of 2 ₹542, pack of 4 ₹707. Not found at Robu, Robocraze, ThinkRobotics, Quartz, IHC, Evelta or ElectronicsComp. Nearest small size in stock: Quartz 683ZZ (3×7×3) ₹39. |
| Thin anti-slip rubber sheet | MonotaRO Natural Rubber Sheet Black 1 m Length 1 mm Thickness 100 mm Width, MBL-100 | IndustryBuying | 978 | Yes | "Ships within 19 days" | https://www.industrybuying.com/esd-rubber-mats-accessories-monotaro-SAF.ESD.238081761 | No rubber sheet found at the electronics stores |
| (alt) silicone pad | Red TE-701 Drone Separator Silicone Pad 16.2*7.9cm (SKU R264588) | Robu | 135 | Yes | IN | https://robu.in/product/red-te-701-drone-separator-silicone-pad-16279cm/ | Thickness not given in the listing |
| (alt) TPU for printed soles | Polymaker PolyFlex TPU 95- Black (750g) 1.75mm Filament Spool (SKU R266003) | Robu | 2,382 | Yes | IN | https://robu.in/product/polymaker-polyflex-tpu-95-black-750g-175mm-filament-spool/ | – |

**Recommended picks**
- **PETG:** Robu Sunlu PETG, ₹739 incl. (limited colours). For black or white: IHC Numakers PETG-HS, ₹749.
- **M2/M3 socket-screw kits:** no in-stock assortment kit found. Buy per-size packs of 10: Quartz M3 SS202 ₹35–47; IHC M2 12.9 ₹49–75.
- **M3 heat-set inserts:** Robu M3×4, 25 pcs for ₹91 incl.
- **623ZZ:** Quartz ₹25, or Robu 4 for ₹84.
- **624ZZ:** Quartz, ₹18.
- **693ZZ:** Quartz, ₹31.
- **MR63ZZ:** IB Invento, 2 for ₹542 (6-day dispatch); none found at the hobby stores.
- **Rubber sheet:** IB MonotaRO 1 mm × 100 mm × 1 m, ₹978 (19-day dispatch). Printing TPU soles (Robu PolyFlex TPU95, ₹2,382 per 750 g) is the in-stock alternative.

---

## H. Optional camera

| Item | Product title (as listed) | Store | Price ₹ | GST incl.? | Stock | URL | Note |
|---|---|---|---|---|---|---|---|
| Pi Camera Module 3 | Raspberry Pi Camera Module 3 (SKU 1441079) | Robu | 3,249 | Yes | IN | https://robu.in/product/raspberry-pi-camera-module-3/ | Listing: IMX708, 12 MP, autofocus, 76° |
| Pi Camera Module 3 | Raspberry Pi Camera Module 3 Sensor Assembly, Auto-focus, IMX708 Sensor, variant "Basic version (75° FOV) / Standard" (SKU WVSH0541) | ThinkRobotics | 3,349.99 | Not stated | IN | https://thinkrobotics.com/products/raspberry-pi-camera-module-3-sensor-assembly-auto-focus-imx708-sensor | The SKU prefix is Waveshare's |
| Pi Camera Module 3 NoIR | Raspberry Pi Camera Module 3 NoIR | Robocraze | 3,379 | Yes | IN | https://robocraze.com/products/raspberry-pi-camera-module-3-noir | Robocraze Wide ₹4,379 IN |
| Pi CM3 sensor assembly | Raspberry Pi Camera Module 3 Sensor Assembly SA31VA30P 11.9MP, 4.74mm Standard Lens (SKU R254275) | Robu | 1,801 | Yes | IN | https://robu.in/product/raspberry-pi-camera-module-3-sa31va30p/ | Sensor assembly only; what is included was not checked |
| OV5647 Pi camera | 5MP Raspberry Pi Camera Module for Pi 3/4 Model B – Rev 1.3 (SKU 10957) | Robu | 319 | Yes | IN | https://robu.in/product/raspberry-pi-camera-module/ | – |
| OV5647 Pi camera (Zero) | 5MP Raspberry Pi Zero W Camera Module W/ HBV FFC Cable (SKU 51705) | Robu | 289 | Yes | IN | https://robu.in/product/5mp-raspberry-pi-camera-module-w-hbv-ffc-cable/ | Zero-size cable |
| OV5647 IR-cut | OV5647 5MP 1080P IR-Cut Camera for Raspberry Pi 3/4 with Automatic Day Night Mode (SKU 130221) | Robu | 979 | Yes | IN | https://robu.in/product/ov5647-5mp-ir-cut-camera-for-raspberry-pi-3-with-automatic-day-night-mode-switching/ | ThinkRobotics Arducam OV5647 listings are OOS |

**Recommended picks**
- **Camera Module 3:** Robu, ₹3,249 incl., in stock.
- **OV5647:** Robu Rev 1.3, ₹319 incl., in stock.
- Cable flag: Evelta lists an "Official Raspberry Pi 5 Camera Cable, CSI FPC Flexible Cable" (₹80 ex, OOS), so a Pi 5 needs a different cable from the Pi 3/4 one. Not checked further.

---

## ST3215 specifications (Waveshare)

Source keys (all fetched 2026-09-24):
- **[W]** https://www.waveshare.com/wiki/ST3215_Servo (revision oldid=111151)
- **[P]** https://www.waveshare.com/st3215-servo.htm. The spec table has two columns: "ST3215" (12 V, sku=22414) and "ST3215-7.4V" (sku=33014).
- **[P12]** https://www.waveshare.com/st3215-servo.htm?sku=22414 (Package Content tab)
- **[P74]** https://www.waveshare.com/st3215-servo.htm?sku=33014 (Package Content tab)
- **[IMG]** https://www.waveshare.com/img/devkit/accessories/ST3215-Servo/ST3215-Servo-details-size.jpg (outline-dimension image)
- **[2D]** https://files.waveshare.com/upload/0/08/ST3215-2D.zip. It holds a vector PDF and a DXF; the drawing title block says "SCS215", dated 2022/6/8.
- **[XLS]** https://files.waveshare.com/upload/2/27/ST3215%20memory%20register%20map-EN.xls ("ST3215 Memory Table Parsing -V3.7", linked from the [W] FAQ)
- **[XLSX]** `sts3215_memory_table.xlsx` (V3.6) inside https://files.waveshare.com/wiki/common/Smart%20%20Bus%20Servo%20Communication%20Protocol%20Manua.zip
- **[CP]** https://files.waveshare.com/upload/2/27/Communication_Protocol_User_Manual-EN%28191218-0923%29.pdf

| Spec | Value (as published) | Source |
|---|---|---|
| Stall torque, 12 V version | "30kg.cm@12V" ([W]: "High torque, up to 30kg.cm@12V") | [P], [W] |
| Stall torque, 7.4 V version | "19.5kg.cm@7.4V" | [P] |
| Stall-torque definition | "the Locked-rotor torque is measured at the typical voltage of each servo" | [P] |
| Stall torque in N·m | NOT FOUND (not published) | – |
| Rated / continuous torque | NOT FOUND on Waveshare pages | – |
| Torque constant | "kt: 11kg.cm/A" (12 V) / "7.8kg.cm/A" (7.4 V) | [P] |
| No-load speed, 12 V | "0.222sec / 60° (45RPM)@12V" | [P], [W] |
| No-load speed, 7.4 V | "0.192sec / 60°(52RPM)@7.4V" | [P] |
| No-load speed in register sheet | "No-load speed（RPM） 49.776", "3400 step/s", test voltage 7.4 V | [XLS] |
| Operating voltage | 12 V version "6 ~ 12.6 V" ([W]: "Input Voltage: 6-12.6V"); 7.4 V version "4V ~ 7.4V" | [P], [W] |
| No-load current | 12 V: "200mA"; 7.4 V: "150mA" | [P], [W] |
| Stall (locked-rotor) current | 12 V: "2.7A"; 7.4 V: "2.5A" | [P], [W] |
| Weight | 12 V: "Weight: 0.089 kg"; 7.4 V: "Weight: 0.07 kg". The page does not say whether this is net or package weight. | [P12], [P74] |
| Body dimensions | "Dimension: 45.22mm x 35mm x 24.72mm". Drawing: 45.22 long, 24.72 wide, case height 32 / 35, 37.25 across both horn discs. | [W], [2D], [IMG] |
| Mounting holes, connector-side face | 4 holes at 24.45 × 20.5 spacing; first hole row 18.41 from the output end | [2D], [IMG] |
| Mounting holes, output face | Holes spaced 20.7 along the length, 18.41 from the output end and 6.11 from the far end. Cross spacing on this face is not dimensioned. | [2D], [IMG] |
| Mounting screw size | NOT FOUND in text. The DXF shows concentric Ø2.0 / Ø1.6 circles at the case holes (read from drawing geometry, not stated). | [2D] |
| Output horn | Ø19.2 horn on both faces; output axis 10.11 from the case end; horn holes "14" apart; "High strength aluminum servo wheels / Using T6061 aluminum alloy". The DXF shows 4 × Ø2.5 holes on a 14 mm circle (drawing reading). | [2D], [IMG], [P] |
| Output spline tooth count | NOT FOUND on Waveshare pages. (Evelta's Feetech STS3215 listing says "25T"; see the supplementary table.) | – |
| Horn screw size | NOT FOUND | – |
| Encoder / resolution | "360° / 4096"; "12-bit high-precision magnetic encoding angle sensor" | [P], [W] |
| Rotation range | "360° (0~4095)", "MECHANISM LIMITED ANGLE: No Limit". [W]: servo mode 360° angle control / motor mode continuous rotation. | [P], [W] |
| Modes | Register 33: 0 position servo, 1 constant-speed motor, 2 PWM open loop, 3 step servo. [W]: step mode covers "±7 circles". | [XLS], [W] |
| Step units | 0.087890625°/step; "50 steps/sec≈0.732RPM"; acceleration unit 100 step/s² | [XLS], [W] |
| Protocol | TTL bus servo interface, "half duplex"; frame 1 start bit, 8 data bits, 1 stop bit, no parity; 2-byte values low byte first (magnetic-encoder series) | [W], [P], [CP] |
| Baud rate | "38400bps ~ 1Mbps (1Mbps by default)" ([W]: "Baudrate: 1Mbps"). Register 6 codes 0–7 = 1000000, 500000, 250000, 128000, 115200, 76800, 57600, 38400; default 0. | [P], [W], [XLS] |
| ID range | "0 ~ 253"; 254 (0xFE) = broadcast; factory ID 1 | [P], [W], [XLS] |
| Connector | "5264/2.54 3P", two ports per servo for daisy-chaining | [W] FAQ |
| Gears / case | "high precision metal gear", "High precision copper and steel gears"; "Nylon and fiberglass case" | [P], [W] |
| Feedback | Position, Load, Speed, Input Voltage (registers also give temperature and current) | [P], [W] |
| Gear ratio, motor type, operating temperature, cable length | NOT FOUND on Waveshare pages | – |

**ST3215 control table** (from [XLS] V3.7; addresses match [XLSX] V3.6). Decimal addresses; 2-byte values are low byte first. "EPROM" is the sheet's name for the non-volatile area.

| Register | Addr | Bytes | Access | Notes |
|---|---|---|---|---|
| ID | 5 | 1 | EPROM R/W | 0–253, default 1 |
| Baud rate | 6 | 1 | EPROM R/W | 0–7, default 0 (1 Mbps) |
| Min / Max angle limit | 9 / 11 | 2 / 2 | EPROM R/W | defaults 0 / 4095 |
| Max temperature | 13 | 1 | EPROM R/W | default 70 °C |
| Max / Min input voltage | 14 / 15 | 1 / 1 | EPROM R/W | defaults 80 / 40 (unit 0.1 V) |
| Max torque | 16 | 2 | EPROM R/W | default 1000 |
| Protection current | 28 | 2 | EPROM R/W | default 500 (unit 6.5 mA) |
| Position correction (offset) | 31 | 2 | EPROM R/W | −2047…2047 |
| Operating mode | 33 | 1 | EPROM R/W | 0–3 |
| **Torque Enable** ("Torque switch") | **40** | 1 | SRAM R/W | 0 off, 1 on, 128 = set current position as 2048 |
| Goal Acceleration | 41 | 1 | SRAM R/W | 0–254 (×100 step/s²) |
| **Goal Position** ("Target location") | **42** | 2 | SRAM R/W | −30719…30719 step |
| Operation time | 44 | 2 | SRAM R/W | – |
| **Goal Speed** ("Operation speed") | **46** | 2 | SRAM R/W | 0–3400 step/s |
| Torque limit | 48 | 2 | SRAM R/W | default 1000 |
| Lock flag (EEPROM write lock) | 55 | 1 | SRAM R/W | 0 = writes saved through power-off, 1 = not saved |
| **Present Position** | **56** | 2 | R | – |
| Present Speed | 58 | 2 | R | step/s |
| Present Load | 60 | 2 | R | unit 0.001 duty |
| Present Voltage | 62 | 1 | R | 0.1 V |
| Present Temperature | 63 | 1 | R | °C |
| Status | 65 | 1 | R | error bits |
| Moving flag | 66 | 1 | R | 1 = moving |
| Present Current | 69 | 2 | R | unit 6.5 mA |

**Contradictions noted between sources**
1. **Baud rate:** [W] says "1Mbps"; [P] says 38400–1M with 1M as the default.
2. **7.4 V speed:** [P] says 52 rpm; [XLS] says 49.776 rpm (3400 step/s).
3. **Max speed setting:** [W] says "about 3073"; [XLS] V3.7 says 3400; [XLSX] V3.6 says 254.
4. **Target-position range:** [XLSX] V3.6 says ±32766; V3.7 says ±30719.
5. **Which version the sheets cover:** both register sheets describe the 7.4 V variant (test voltage 7.4 V, max-voltage default 8.0 V). No 12 V-specific sheet was found.
6. **Drawing title:** the 2D drawing's title block says "SCS215".
7. **Electrical level:** the protocol manual [CP] describes magnetic-encoder servos as "RS485"; the ST3215 pages say TTL half-duplex.
8. **Robu page title:** Robu's ST3215 7.4 V page `<title>` says "30kg.cm", while its listing says 19.5 kg·cm @ 7.4 V.

**Supplementary (not Waveshare): Feetech STS3215 figures as listed by Evelta**, for comparison only.

| Spec | STS3215-C001 (7.4 V) | ST3215-C018 (12 V) |
|---|---|---|
| Source | https://evelta.com/st3215-7-4v-19kg-1-345-gear-dual-axis-ttl-string-servo-motor/ | https://evelta.com/st3215-c018-12v-30kg-cm-dual-shaft-ttl-serial-servo-metal-gears-magnetic-encoder/ |
| Stall torque | "19.5kg.cm@6V" | "30kg.cm@12V" |
| Rated torque | "6.5kg.cm@6V" | "10kg.cm@12V" |
| Voltage | "6-7.4V" | "4-14V" |
| Speed | "0.238sec/60°@6V" | "0.222sec/60@12V" |
| Size | "45.2mmx24.7mmx35mm" | "45.2mmx24.7mmx35mm" |
| Weight | "55± 1g" | "55+- 1g" |
| Horn spline | "25T" | "25T/OD5.9mm" |
| Case / motor | "Aluminum Alloy" / "Coreless motor" | "PA+GF" / "Core Motor" |
| Stall current | "2000mA@6V" | "2.7A@12V" |

Evelta's STS3215-C001 figures (torque rated at 6 V, aluminium case) differ from Waveshare's ST3215 7.4 V figures (19.5 kg·cm @ 7.4 V, nylon/fiberglass case). Whether the Waveshare ST3215 is the same unit as a Feetech STS3215 variant is NOT CONFIRMED.

## SC09 specifications (Waveshare)

Sources:
- **[SW]** https://www.waveshare.com/wiki/SC09_Servo (oldid=111160)
- **[SP]** https://www.waveshare.com/sc09-servo.htm
- **[SIMG]** https://www.waveshare.com/img/devkit/accessories/SC09-Servo/SC09-Servo-details-size.jpg
- **[SCS]** https://files.waveshare.com/upload/5/5c/SCS_Series_Memory_Table_Analysis.xls

| Spec | Value (as published) | Source |
|---|---|---|
| Stall torque | "2.3kg.cm@6V" | [SP], [SW] |
| Rated torque | "0.7kg.cm@6V" | [SP] |
| No-load speed | "0.1sec/60° (100RPM)@6V" | [SP], [SW] |
| Operating voltage | "4~6V" ([SW] "4-6V"). Robu's SC09 page says "Wide voltage input 4.8-8.4V", which conflicts. | [SP], [SW] |
| Currents | no-load "150mA@6V"; locked-rotor "1.0A" | [SP], [SW] |
| Weight | "Weight: 0.021 kg" | [SP] |
| Dimensions | "23.2×12.0×25.5mm". The drawing image shows 23.3 / 12.1 / 25.25. | [SP], [SW], [SIMG] |
| Mounting holes | Image only: flange 16.25 + 16.25; hole to axis 8.55; hole dimension "2". Screw size NOT FOUND. | [SIMG] |
| Output shaft / spline | "Output shaft: 20T/OD3.95mm"; horn hole pattern NOT FOUND | [SP] |
| Position sensor / resolution | "Carbon film potentiometer"; "0.293° (300°/1024)" | [SP], [SW] |
| Range | "300° (0~1024)" [SP] vs "300° (0~1023)" [SW]; motor mode continuous | [SP], [SW] |
| Protocol | half-duplex asynchronous serial (TTL); 2-byte values high byte first | [SP], [CP], [SCS] |
| Baud / ID | "38400bps~1Mbps"; ID "0 ~ 253". A default baud is not stated on the SC09 pages. | [SP], [SW] |
| Gears / motor | metal (copper and steel) gears; iron-core motor; sliding bearing | [SP] |
| Temperatures | operating −15~70 °C; storage −30~80 °C | [SP] |
| Cable | "15cm" | [SP] |
| Registers (generic SCS table, sheet named "SCS15") | ID 5; Baud 6; Min/Max angle 9/11; Torque switch 40; Target position 42 (2 B, 0–1023); Operation time 44; Operation speed 46; Lock flag 48; Present position 56; Present speed 58; Present load 60; Present voltage 62; Present temperature 63; Status 65; Moving 66. This table has no acceleration register and no present-current register. | [SCS] |
| NOT FOUND | N·m values, horn hole pattern, screw size, connector type, gear ratio, an SC09-specific register table | – |

---

## Summary of picks (cheapest in-stock, reputable store)

| Item | Pick | ₹ | GST |
|---|---|---|---|
| ST3215 7.4 V | Robu R258500 | 2,159 | incl |
| Feetech STS3215 7.4 V | Evelta STS3215-C001 | 2,224.30 | incl |
| ST3215 12 V | Evelta Feetech ST3215-C018 (Waveshare 12 V: Robu or Robocraze ₹2,599) | 2,419.00 | incl |
| ST3215-HS | Robu 1738071 | 2,529 | incl |
| SC09 / SCS0009 | ElectronicsComp SC09 (1 unit); for quantity, Evelta SCS0009 ₹1,074.91 | 985.30 | incl (calc) |
| ST3020 | Robu 1738072 | 2,618 | incl |
| ST3025 | Robocraze | 10,299 | incl |
| STS3032 | Evelta ST-3032-C001 | 3,451.65 | incl |
| LX-16A / LX-15D / LX-224 | ThinkRobotics | 2,099.99 / 2,899.99 / 2,899.99 | not stated |
| MG90S / SG90 / MG996R | Quartz | 124 / 86 / 259 | not stated |
| Bus servo driver | ThinkRobotics Waveshare Serial Bus Servo Driver (SmartElex at Robu/Robocraze ₹509 incl) | 499.99 | not stated |
| Bus Servo Adapter (A) | NOT FOUND | – | – |
| Pi 5 4 GB | Probots | 15,949 | incl |
| Pi 5 8 GB | Robu | 19,999 | incl |
| Pi 4 2 GB | ThinkRobotics (with case) | 6,999.99 | not stated |
| Pi 4 4 GB | Quartz | 9,695 | not stated |
| Pi Zero 2 W | none in stock (5 stores) | – | – |
| Pi 5 27 W PSU | Quartz | 1,063 | not stated |
| Pi 5 Active Cooler | Quartz | 438 | not stated |
| SanDisk 32 GB microSD (A1) | Quartz | 1,499 | not stated |
| MPU6050 | Quartz | 127 | not stated |
| BNO055 | Evelta 7Semi | 1,341.66 | incl |
| BNO085 | Evelta 7Semi Nano | 2,094.50 | incl |
| ICM-20948 | Robocraze 7Semi | 1,130 | incl |
| INMP441 | Quartz | 145 | not stated |
| MAX98357A | Quartz | 124 | not stated |
| Speaker 3 W 4 Ω | NOT FOUND (alt: ThinkRobotics 2030 8 Ω 2 W ₹299.99) | – | – |
| USB mini mic | Quartz | 185 | not stated |
| USB sound card | Robu 51861 | 105 | incl |
| GC9A01 1.28" round | Robu R267806 | 469 | incl |
| 2S LiPo 2200 | IHC GenX 40C (Robu Pro-Range 45C ₹1,629 incl) | 1,499 | not stated |
| 2S LiPo ~3000 | Robu Bonka 3300 25C | 2,149 | incl |
| Balance charger | Quartz B3 | 294 | not stated |
| 5 V 5 A UBEC / buck | Robu UBEC-5V/5A ₹409 incl / Quartz MINI560 ₹65 | 409 / 65 | incl / not stated |
| XL4015 / LM2596 | Quartz | 79 / 45 | not stated |
| XT60 pair | Robocraze | 29 | incl |
| 10 A switch | Quartz CALONIX toggle (DC-rated) | 63 | not stated |
| 16 AWG / 20 AWG wire | Robu | 49/m / 21/m | incl |
| LiPo checker | Quartz | 98 | not stated |
| PETG 1 kg | Robu Sunlu | 739 | incl |
| M2/M3 socket kits | none in stock; per-size packs (Quartz/IHC) | 35–75 per 10 | not stated |
| M3 heat-set inserts | Robu 25 pcs | 91 | incl |
| 623ZZ / 624ZZ / 693ZZ | Quartz | 25 / 18 / 31 | not stated |
| MR63ZZ | IndustryBuying Invento, pack of 2 (6-day dispatch) | 542 | incl |
| Rubber sheet | IndustryBuying MonotaRO 1 mm × 100 mm × 1 m (19-day dispatch) | 978 | incl |
| Pi Camera Module 3 | Robu | 3,249 | incl |
| OV5647 | Robu Rev 1.3 | 319 | incl |

**Not found / not in stock anywhere checked**
- Waveshare Bus Servo Adapter (A).
- 3 W 4 Ω ~40 mm speaker.
- In-stock M2/M3 socket-head screw assortment kit.
- Raspberry Pi Zero 2 W: out of stock at Robu, Evelta, ElectronicsComp, Zbotic and Hubtronics.
- Orange-brand 2S 2200–3000 mAh pack in stock.
- "Robu-brand" PETG.
- MR63ZZ and rubber sheet at hobby/electronics stores (only IndustryBuying, with 6–19-day dispatch).
- Hiwonder LX-series and STS3032 at Robu, Robocraze and Quartz.
- ST3215 values not published by Waveshare: stall torque in N·m, rated torque, spline tooth count, horn and mounting screw sizes, gear ratio, motor type, operating temperature, cable length, and net-vs-package weight.
