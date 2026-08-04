# AgriRover - Field Upgrade Roadmap
## IIT-B x Groww Track A | Rs 50,000 hardware ceiling

This roadmap is optimized for the first commercial question: can a supervised
rover collect repeatable tomato pest evidence cheaply enough to improve farmer
profit through an FPO/KVK service?

It is not a feature-count roadmap. Each upgrade must improve one of five pilot
measurements: detection, coverage, safety, service cost or paid renewal. See
`research/AGRIROVER_MARKET_ADOPTION_RESEARCH.md` for source evidence and the
full acceptance gates.

---

## Current Design Baseline

The repository contains designs or code paths for the following subsystems.
Their presence is not proof that the assembled rover meets field performance,
life, safety or ROI requirements.

| Subsystem | Valid statement today | Required proof |
|---|---|---|
| ESP32 plus Raspberry Pi architecture | Separates motor/safety control from higher-level software | Fault-injection and physical stop tests |
| BTS7960 drive and 4WD chassis | Higher current headroom than an L298N design | Mud, slope, stall-temperature and crop-clearance tests |
| ToF, IMU, encoders and current sensing | Inputs exist for local stops, tilt, odometry and stall detection | Measured false-stop, missed-stop and intervention rates |
| RGB model pipelines | Inference interfaces and model artifacts exist | Local tomato per-class precision/recall and domain-shift audit |
| GPS/EKF code | Supports coarse field location and mapping | Camera row following; metre-scale GPS cannot choose a vegetable row |
| Pan/tilt nozzle and pump design | Experimental supervised application hardware | Flow, droplet, efficacy, crop-safety and label-compliance trials |
| NPK probe and dosing design | Experimental sensor/actuator path | Independent calibration; no fertilizer prescription or lab replacement |

---

## P0 - Make Every Measurement Trustworthy

**Cost:** mostly software and bench fixtures  
**Timing:** before any farmer saving, dosage or acres/day result is shown

1. Resolve the current 30 ml/second versus 40 ml/minute flow conflict by
   gravimetric calibration with the actual pump, liquid, pressure and nozzle.
2. Disable the default rupee-savings display; use formulation quantity, tank
   recipe and invoice price from a documented baseline.
3. Add timestamped logs for setup, productive motion, turns, charging, weather,
   failures, support minutes and missed rows.
4. Separate coarse GNSS location from row-control accuracy in every report.
5. Add model version, image pose, standoff, light level and reviewer correction
   to each agronomic observation.
6. Implement a versioned crop-pest-product label and PHI rule table; reject
   missing combinations rather than inserting a default.
7. Keep autonomous pesticide application disabled for the first agronomic
   pilot.

This tier has more commercial value than adding another sensor because it makes
the pilot auditable.

---

## P1 - Tomato Evidence Capture

**Planning cost:** Rs 4,500-6,500

| Item | Planning Rs | What it must establish |
|---|---:|---|
| 12MP autofocus side/downward camera | 2,000-3,000 | Controlled plant, leaf and fruit evidence |
| Macro lens/camera and diffuse ring light | 1,500-2,500 | Count agreement on traps and selected close samples |
| Adjustable mast, guards and standoff gauge | 600-800 | Repeatable pose without touching the crop |
| Trap dock, fiducial scale and ID marker | 400-600 | Same trap and scale on every weekly visit |

The first launch candidates are tomato fruit-borer evidence, live leaf mines,
pheromone-trap trend and geotagged symptomatic-plant incidence. Whiteflies,
thrips and mites remain behind a macro/manual count-agreement gate. A normal
moving wide camera cannot prove their absence.

**Pass condition:** at least 85% recall and 80% precision for every launch class
on held-out local fields, plus at least 90% detection of expert-confirmed urgent
or ETL events by the full sentinel workflow.

---

## P2 - Repeatable Rows and Productive Coverage

**Planning cost:** Rs 1,500-4,000 beyond the existing drive design

| Upgrade | Purpose |
|---|---|
| Dedicated forward row camera | Keep navigation geometry separate from agronomic images |
| Camera row follower plus encoder odometry | Hold the local row while GNSS supplies only coarse position |
| Physical bumper/contact strip and rear stop sensor | Independent low-speed stop path |
| Swappable battery tray and second pack | Remove charging from productive route time |
| Instrumented turn/setup state machine | Expose the real cause of low acres/day |

At common vegetable spacings, one acre contains roughly 4.5-6.75 km of crop
row. Pure travel at 0.3 m/s can take 4.2-6.3 hours before turns and stops. That
is why the affordable service uses fixed sentinel samples every week and a
full-row scan only when triggered.

**Pass condition:** at least 5 productive sentinel acres/day, 2.5 triggered
deep-scan acres/day, under 15 minutes setup/plot, and no crop/boundary contact.

---

## P3 - Field Survival and Repair

**Planning cost:** Rs 4,500-8,500

| Item | Planning Rs | Validation |
|---|---:|---|
| Industrial/pSLC storage | 800-1,500 | Logged write endurance and recovery test |
| IP-rated enclosure and membrane vent | 800-1,800 | Dust, splash and condensation tests |
| Conformal coating and protected connectors | 900-1,800 | Humidity and vibration inspection |
| Anti-vibration mounts and sun canopy | 250-650 | Camera stability and thermal mission log |
| Labelled field-replaceable harness | 500-1,200 | Connector replacement without rewiring |
| Local spares kit | 1,500-3,500 | Median repair time during the pilot |

Do not convert battery cycle ratings, enclosure labels or component datasheets
into a "five-season life" statement. Launch pricing must survive the one- and
two-year asset-life cases until real failure data supports a longer life.

---

## P4 - Compute Only After the Local Dataset Exists

| Option | Planning Rs | Decision use |
|---|---:|---|
| Pi 5 CPU/offline processing | Included in base | Lowest-risk data-collection path |
| Hailo-8L 13 TOPS | About 6,350 | Keep only if sustained end-to-end benchmark passes |
| Hailo-8 26 TOPS | About 10,500 | Consider only if the frozen model needs it |

The benchmark must report model version, per-class field accuracy, end-to-end
latency, sustained temperature, energy and fallback behaviour. Accelerator TOPS
and a laboratory FPS number do not establish acres/day or farmer value.

---

## P5 - Farmer and FPO Interface

**Hardware cost:** Rs 0-1,000 using phone tethering/offline sync first

The farmer output should be a short Marathi voice message plus one evidence card:

- `ACT`: expert-reviewed action and PHI;
- `WATCH`: repeat count/visit date; or
- `NO TREATMENT`: threshold source and next observation date.

The FPO/KVK receives the detailed image, count, path, reviewer, treatment and
verification record. Log whether the message was heard and acted on. Add LoRa
only for small telemetry after a real coverage survey; LoRa by itself does not
deliver Telegram, voice, images or internet access.

---

## Deferred or Excluded From the First Pilot

| Item | Why it is deferred |
|---|---|
| Low-cost RS485 NPK probe | Independent evaluation found weak, moisture-dependent prediction; do not prescribe fertilizer or replace certified tests |
| NoIR camera plus blue filter | A low-cost camera paper does not prove early tomato disease detection, calibrated NDVI or farmer benefit |
| Autonomous pesticide spray | No AgriRover efficacy, drift, crop-safety or label-compliance result exists |
| Whole-field fertilizer dosing | No valid soil prescription and the current small tank/actuator do not establish field-scale application |
| RTK GNSS | Useful later for repeat absolute geotags, but not a substitute for local row perception |
| Professional multispectral camera | Consider only after RGB sentinel misses a decision-critical event that spectral data can demonstrably recover |
| Tractor ISOXML integration | Future enterprise path; validate a real terminal and buyer workflow before advertising compatibility |
| Laser/mechanical weeding attachment | Different safety, geometry and economics program; not required for tomato surveillance proof |

---

## Budget Scenarios

| Configuration | Planning total | Use |
|---|---:|---|
| CPU evidence scout | About Rs 34,800 | Data collection, supervised mobility and protocol work |
| Hailo-8L field pilot scout | About Rs 41,150 | Local edge benchmark and full pilot workflow |
| Hardware ceiling with spares/iteration | Rs 50,000 | Groww Track A allocation |

Agronomist review, traps/consumables, travel, farmer compensation and field
insurance belong in a separate operating budget. Hiding them inside a cheap BOM
would make the service economics misleading.

---

## What Judges and Partners Should Be Shown

Show the raw evidence and pass/fail gates, not projected percentages:

1. the same trap and sentinel plants revisited over eight weeks;
2. expert-confirmed detections, false alarms and misses by class;
3. complete route time, setup, charging, weather and downtime;
4. treatment/PHI and verification records;
5. farmer invoices, marketable yield and grade for intervention and control;
6. provider contribution after operator, transport, maintenance and review; and
7. an actual paid continuation or FPO minimum-acre booking.

Only those results can support a chemical-saving, profit, life or payback claim.
