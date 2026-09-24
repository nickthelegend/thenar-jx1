# RobStride actuators on Alibaba.com — reseller prices (checked 2026-09-24)

Source: alibaba.com search "robstride 04" with delivery set to India (in-app browser), plus the listing the user found
(RobStride EduLite 05, Shenzhen Gegu Dingxin Technology). Prices are Alibaba listing prices in INR as displayed:
**before Indian import duty and before shipping**; several were "Super September" sale prices (36 % off, ending
2026-09-30). Label: VERIFIED as listed (seller claims, not verified products).

| Model (peak torque) | Seller (years on Alibaba, rating) | Listed ₹ | MOQ | Note |
|---|---|---:|---:|---|
| RS04 (120 N·m) | Shenzhen Gegu Dingxin "GGDX" (1 yr, 4.8/67) | 22,422 (was 35,034) | 1 | sale price, 3 sold |
| RS04 | Shenzhen Lingxiang Security Technology (1 yr, 5.0/4) | 20,245–21,984 | 1 | 10 sold |
| RS04 | Shenzhen Anshengchuang "Chipboard" (2 yr, 5.0/5) | 23,569 | 1 | |
| RS04 | Shanghai Xuanxin Technology (7 yr, 4.7/44) | 24,298 | 1 | |
| RS04 | Shenzhen Jia Neng Electronics (9 yr, 3.8/55) | 32,923 | 1 | |
| RS04 | Shenzhen Yiqi Technology (8 yr, 4.9/36) | 50,151 | 1 | 30 sold |
| RS03 (60 N·m) | Guangdong Gongboshi (1 yr) | 18,574–19,557 | 1 | |
| RS03 | Shenzhen Anshengchuang (2 yr, 5.0/5) | 21,426 | 1 | |
| RS03 | GGDX (1 yr, 4.8/67) | 21,447 (was 33,511) | 1 | sale price |
| RS03 | Shenzhen Yiqi (8 yr, 4.9/36) | 35,291 | 1 | 22 sold |
| RS06 (36 N·m) | Foshan Yun Qu Zhe (2 yr, 4.6/2) | 16,059–17,666 | 3 | listing text mixes in unrelated specs |
| RS02 (17 N·m) | Shenzhen You Ju Jia Pin (6 yr, 4.6/121) | 8,747–12,776 | 2 | |
| RS02 | Shenzhen Lingxiang (1 yr, 5.0/4) | 11,793–12,776 | 1 | 4 sold |
| RS02 | Shenzhen Yiqi (8 yr, 4.9/36) | 40,333 | 2 | 22 sold |
| RS00 (14 N·m) | Shenzhen Lingxiang (1 yr, 5.0/4) | 9,926–10,968 | 1 | |
| RS00 | Shenzhen Komo Innovation Robotics (1 yr) | 12,383 | 2 | |
| RS00 | Shanghai Xuanxin (7 yr, 4.7/44) | 13,734 | 1 | |
| EduLite 05 (6 N·m) | GGDX (1 yr, 4.8/67) | 6,823 (was 10,661) | 1 | the listing the user found; 1 sold, no reviews |
| RS05 (5.5 N·m) | Shenzhen Qianbao (4 yr, 4.5/57) | 9,818 | 1 | |

Also listed: GGDX bundle "RobStride 00/01/02/03/04/05/05 EduLite/06", ₹1,523–29,704 per piece at MOQ 25 (bulk
pricing: ask for a quotation for the 21-unit set).

## Estimated landed cost in India

Same factors as the BOM (`bom/build_bom.py`): × 1.3228 import duty (HS 8501) × 1.07 shipping = × 1.4154. Using the
cheapest and dearest of the reasonable listings above (ignoring the ₹32–50k outliers):

| Model | Qty | BOM landed (official store) | Alibaba landed, low – high |
|---|---:|---:|---:|
| RS04 | 4 | 34,634 | 28,655 – 34,391 |
| RS03 | 2 | 30,560 | 26,290 – 30,356 |
| RS06 | 7 | 28,522 | 22,730 – 25,004 |
| RS02 | 4 | 19,694 | 12,380 – 18,083 |
| RS00 | 4 | 16,978 | 14,049 – 19,439 |
| **All 21** | | **5,45,998** | **≈ 4,32,000 – 5,23,000** |

So Alibaba resellers save ≈ ₹0.2–1.1 lakh on the 21 actuators, less than the China-domestic-price estimate in the BOM
(₹3,58,924), because resellers charge more than the CNY list and Indian duty still applies. The same model ranges from
₹19k to ₹50k between sellers: request quotations (with shipping to India) from several established sellers.

## EduLite 05 — why it is cheap and where it could fit

EduLite 05: 6 N·m peak / 1.8 N·m rated, Ø46 mm, 242 g, 9:1 powder-metallurgy planetary gears (research table,
`actuator_technology_raw.md`). It is RobStride's smallest education-grade module: 1/20 of the knee actuator's torque.
Per N·m of peak torque it is not cheap (₹6,823 / 6 ≈ ₹1,140 per N·m before duty, vs ≈ ₹187 per N·m for an RS04
at ₹22,422). Against the JX1 requirements (`requirements/robot_requirements.yaml`) it cannot drive any leg joint, the
waist, the shoulders (15 N·m) or shoulder yaw (8.9 N·m); the elbow needs 5.8 N·m peak, which leaves it 3 % margin.
