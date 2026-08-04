# AgriRover - Top 20 Pilot Components (IIT-B x Groww Track A)

**Budget ceiling:** Rs 50,000  
**First field use:** supervised tomato sentinel surveillance in Junnar  
**Commercial form:** FPO-operated service, not an individual-farmer machine sale

This BOM builds the measurement tool required for the proposed pilot. It does
not assume that a component creates farmer savings by itself. Product evidence,
economics and validation gates are documented in
`research/AGRIROVER_MARKET_ADOPTION_RESEARCH.md`.

The launch BOM deliberately prioritizes controlled close images, repeatable
sampling, swappable power, local row navigation and repairability. A low-cost
NPK probe, fertilizer doser, improvised NDVI camera and autonomous pesticide
sprayer are excluded from the first agronomic pilot because none can currently
support a safe farmer-profit claim.

---

| # | Component | Pilot role / claim to validate | Qty | Planning Rs |
|---:|---|---|---:|---:|
| 1 | **Raspberry Pi 5 4GB, 27W PSU and active cooler** | Evidence capture, mission logging, local UI and model inference | 1 | 7,000 |
| 2 | **Hailo-8L AI HAT+ (13 TOPS)** | Edge-inference candidate; benchmark local tomato models before freezing it | 1 | 6,350 |
| 3 | **ESP32 DevKit V1** | Deterministic motor, sensor, watchdog and emergency-stop control | 1 | 400 |
| 4 | **Forward RGB row camera with wide lens** | Row perception and obstacle evidence; GPS is not row control | 1 | 1,800 |
| 5 | **12MP autofocus side/downward evidence camera** | Repeatable plant, leaf and fruit images at controlled standoff | 1 | 2,500 |
| 6 | **Macro camera/lens plus diffuse ring light** | Trap and close-leaf counts; required before tiny pests are in scope | 1 | 2,200 |
| 7 | **12V geared motors, 4WD** | Supervised traversal on the actual Junnar row geometry | 4 | 1,200 |
| 8 | **BTS7960 motor drivers** | Drive-current headroom; stall and heat limits still require bench tests | 2 | 500 |
| 9 | **Front/rear ToF sensors** | Local stop envelope and setup-clearance measurement | 2 | 800 |
| 10 | **Hall-effect wheel encoders** | Odometry, distance and productive-coverage measurement | 2 | 300 |
| 11 | **6-axis IMU** | Tilt logging and rollover-stop input | 1 | 200 |
| 12 | **GNSS receiver** | Field/plot geotag only; nominal metre-scale GNSS cannot select a crop row | 1 | 400 |
| 13 | **LiFePO4 battery packs, swappable** | Measure mission endurance and remove charge-time from productive routes | 2 | 7,000 |
| 14 | **Charger, BMS, fuses and current monitor** | Safe power isolation plus measured energy and battery health | 1 set | 1,800 |
| 15 | **Industrial/pSLC microSD** | Logging-endurance candidate; prove life under the actual write load | 1 | 1,200 |
| 16 | **IP-rated enclosure, membrane vent and conformal coating** | Dust, splash and condensation test package | 1 set | 1,800 |
| 17 | **GX12 connectors and labelled service harness** | Fast replacement and vibration-resistant connections | 1 set | 1,000 |
| 18 | **Physical E-stop, bumper/contact and ultrasonic backup** | Independent supervised stop paths | 1 set | 900 |
| 19 | **Trap-imaging dock, fiducial scale and controlled light** | Same trap ID, pose and scale on every weekly visit | 1 set | 800 |
| 20 | **Chassis, adjustable camera mast, guards and sun canopy** | Stable image geometry, crop clearance and serviceable packaging | 1 set | 3,000 |

## Planned Hardware Total: Rs 41,150

**Unallocated Rs 8,850:** replacement motors/connectors, spare storage, camera
mount iterations, sticky/pheromone traps, field consumables and price variance.
Travel, agronomist time and farmer compensation belong in the pilot operating
budget, not inside the machine BOM.

Prices are planning estimates, not quotations. Confirm tax, shipping, warranty,
availability and supplier support before purchase.

---

## Why This BOM Matches the Market Wedge

| Design choice | Evidence or constraint | Decision |
|---|---|---|
| Fixed-point plant and trap imaging | Official tomato IPM guidance uses weekly, specified plant/leaf/fruit/trap samples | Build repeatable evidence capture before broad classification |
| Separate row and evidence cameras | Navigation and agronomy need different pose, focus and field of view | Do not force one wide camera to do both jobs |
| Macro camera and controlled light | Whiteflies, mites and thrips are not reliably visible in ordinary drive-by RGB | Keep those classes behind a hardware and count-agreement gate |
| Vision plus odometry for rows | NEO-6-class GNSS error spans several vegetable rows | Use GNSS only for coarse field location |
| Two swappable batteries | Dense-row path length can be 4.5-6.75 km/acre before turns and stops | Measure productive acres/day on a real route |
| Rugged, repairable harness | Shared machinery fails commercially when repair and operator support are weak | Time every failure and maintain a local spares kit |
| Human review and manual application | PPQS label, dose, interval and PHI rules still apply; rover efficacy is unproved | No autonomous pesticide action in the first pilot |

The external 2024 ICAR-NRIIPM tomato program used 7.33 sprays versus 18.66 in
farmer practice and reported better cost, yield and net return. That was a full
IPM bundle with traps, bioagents, cultural controls, training and need-based
pesticides. It validates the value pool, not this rover's performance.

---

## Compute Decision

The Hailo-8L is a **candidate**, not a production declaration. Keep it only if a
reproducible device benchmark shows that the frozen local model meets required
latency, thermal and energy limits. The minimum benchmark report must include:

1. model version, input resolution and exact compiler/runtime versions;
2. per-class precision, recall and false-negative rate on held-out local fields;
3. end-to-end image-to-record latency, not accelerator-only FPS;
4. sustained temperature, throttling and watt-hours over a full mission; and
5. CPU/offline fallback behaviour when the accelerator fails.

A CPU-only scout costs about **Rs 34,800** using this planning sheet. That is a
valid fallback for early fixed-point data collection if it meets visit time;
expensive compute should not displace cameras, batteries, guards or spares.

---

## Pilot Acceptance Gates

These are targets to measure, not current capabilities:

| Gate | Target |
|---|---:|
| Local launch-class model | At least 85% recall and 80% precision per class |
| Sentinel detection | At least 90% of expert-confirmed urgent/ETL events, no more than one visit late |
| Mission completion | At least 90% without safety intervention |
| Sentinel throughput | At least 5 productive acres/day on real village routes |
| Triggered deep-scan throughput | At least 2.5 productive acres/day |
| Plot setup | Under 15 minutes |
| Expert review | Median at or below 10 minutes/report |
| Farmer result | At least 25% lower documented tomato protection spend with non-inferior marketable yield/grade |
| Demand | At least 6 of 12 growers buy another pass or sign a seasonal order |

If the agronomic, throughput and paid-renewal gates do not pass together, do not
convert the hardware into a farmer ROI or payback claim.

---

## Software Status and Pilot Gaps

| Capability | Current position |
|---|---|
| Dual-controller firmware and Raspberry Pi service structure | Repository implementation; verify on assembled hardware |
| Model inference interfaces and active-learning capture | Repository implementation; local tomato model not validated |
| Telegram, dashboard and field-history infrastructure | Repository implementation; redesign farmer output for Marathi voice plus action card |
| HMAC command authentication, watchdogs and stop logic | Repository implementation; physical safety test pending |
| Fixed sentinel points and repeatable trap imaging | Pilot build required |
| Agronomist review, label/PHI gate and correction audit | Pilot build required |
| Calibrated coverage, energy, downtime and service-cost logging | Pilot build required |
| Invoice-based farmer profit report | Pilot build required; disable default rupee-saving estimates |
| FPO route booking, consent and renewal workflow | Pilot build required |

---

## Budget Configurations

| Configuration | Planning total | Appropriate use |
|---|---:|---|
| **CPU scout without Hailo** | Rs 34,800 | Fixed-point data collection and early mobility work |
| **Field pilot scout with Hailo-8L** | Rs 41,150 | Local inference and full mission benchmark |
| **Field pilot allocation with spares/iteration** | Rs 50,000 | Groww Track A hardware ceiling |

An NPK probe, fertilizer actuator, NoIR/filter camera and spray module remain
research options outside this launch BOM. They may return only after an
independent measurement protocol and a crop-specific safety/economics case.
