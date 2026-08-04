# AgriRover Problem-to-Solution Opportunity Catalog

**Research artefact | 04-Aug-2026 | 20 opportunities ranked, 11 killed, 1 mandatory prerequisite**

> **Purpose.** A ranked catalog of PROBLEM → AGRIROVER-ENABLED SOLUTION
> opportunities across Indian horticulture and field crops, scored by (value at
> stake) × (technical feasibility on *this* platform) × (who actually pays).
>
> **This document is deliberately harsher on AgriRover than any pitch deck.**
> Where a sensing claim is physically dubious — sugar content from a photograph
> being the canonical example — it is said plainly and downgraded, even when
> that removes the most attractive story in the catalog.
>
> **Scope.** Research only. No AgriRover field data exists. Nothing here is a
> capability claim, a forecast, or a price.

## How this document relates to the other three dossiers

| Document | Role | This document must not contradict it |
|---|---|---|
| `FARMER_ADOPTION_AND_PROBLEMS_RESEARCH.md` (v3) | Who pays, at what price, at what route density | The defensible buyer is a **solvent, liable processor/FPO/exporter**; the sellable object is an **audit artefact or physical act, not information**; route density and WTP are the killers |
| `AGRIROVER_MARKET_ADOPTION_RESEARCH.md` | Pilot design, gates, first market | Tomato crop-protection surveillance in Junnar is the *chosen* pilot; the *viable buyer* is grape-shaped and Nashik-shaped |
| `AGRI_PROBLEMS_RESEARCH.md` | 28 verified problems + solvability verdicts | P1–P28 verdicts stand; this document **refines mechanisms** inside them, it does not re-litigate them |

**The three inherited constraints that kill most ideas before feasibility is
even discussed.** Every entry below is scored against these, not against
technical elegance:

1. **Information alone has no market.** Measured WTP for plant-protection
   information is **₹14.89/acre** `[F01]`; AgriRover's deep scan needs
   ₹800–950. The gap is ~50×, and a funded competitor (BharatAgri, ~USD 21 M)
   died selling approximately that product `[G01]`. An entry whose only output
   is *a number the buyer could have guessed* is **park**, regardless of how
   good the computer vision is.
2. **The grower carries no residue liability.** FSSAI exempts farm-level
   produce `[G03]`; liability sits with the **exporter/producer-of-record**
   `[G15]`. Any compliance-flavoured entry must name an exporter, pack-house or
   large traceability-operating FPO as the payer, or it is void.
3. **Travel time, not scan time, sets cost.** Cost per acre-pass moves **4.1×**
   across the density band (₹387–₹1,599 with support) and the ₹300/acre deck
   price is unreachable at every density `[G13]`, §11.3. Under-canopy platforms
   run at **~0.3 m/s** `[G26]` ≈ 0.4 acre/hour fully traversed. **Sentinel
   sampling is a physical necessity, not a cost option.** An entry that
   requires full-field traverse of every plant, every week, is not buildable at
   any price.

---

## Evidence labels (identical scheme to the other three dossiers)

- **[External result]** — measured or published by another organization. It
  validates a problem or a mechanism, **never** AgriRover's performance.
- **[Repository fact]** — present in this repository's code, BOM or design
  documents. **Not** proof that the physical rover works in a field.
- **[Analyst scenario]** — a transparent calculation used to make a decision.
  Not a forecast and not a measured result.
- **[AgriRover target]** — a gate the product must pass before the claim may be
  used in a sales conversation.

New evidence introduced by this document is tagged **`[H01]`…`[H18]`**, listed
in full with sources in §6.6 (the
prefixes `E`, `F`, `G` and `P` are already in use by the other dossiers and are
cited unchanged).

**Cross-reference convention.** `§1`–`§6` always mean sections of *this*
document. `§11.x` and `§12` refer to the v3 farmer-adoption dossier's unit-
economics and subsidy sections; references to other dossiers' §-numbers name the
dossier explicitly.

**Standing caveat.** AgriRover has **no field-validation data**. No measured
accuracy, coverage rate, saving, yield effect or payback exists. Every
feasibility grade below is an engineering judgement against published CV and
agronomy literature — not a test result.

---

## Feasibility grading key

| Grade | Meaning |
|---|---|
| **[buildable now]** | The sensing physically works at RGB/probe resolution, the model class exists and the compute fits the Hailo-8/Coral envelope. Still needs local data and validation — "buildable" is not "validated". |
| **[needs new sensor or model + name it]** | The decision is real but the current stack cannot physically sense it. The specific missing component is named and priced. |
| **[not feasible for a slow ground rover]** | Physics, geometry or throughput defeats it. Listed for honesty, not force-fitted. |

---

## §0. Platform envelope — confirmed from the repository

Everything below is a **[Repository fact]**, read from source rather than from
the deck. **Design only within this envelope.**

### Compute and vision

| Element | Confirmed detail | Source |
|---|---|---|
| Primary compute | **Raspberry Pi 5 4GB** + **Hailo-8 AI HAT+ (26 TOPS)**; BOM prices the **Hailo-8L (13 TOPS)** at ₹6,350 as the pilot candidate | `README.md`, `docs/BOM-top20-groww-trackA.md` #1–2 |
| Fallback compute | Pi 4 + **Coral USB Edge TPU**; CPU-INT8 path always present. `USE_HAILO=1`, `USE_CORAL=1` | `pi/config.py`, `pi/ai/tflite_backend.py` |
| Real-time controller | **ESP32 DevKit V1** (FreeRTOS), dual-core, HMAC-authenticated link | `firmware/src/main.cpp`, `README.md` |
| Detection | **YOLOv8n**, `.hef` → `_edgetpu.tflite` → INT8 → `.pt` candidate chain | `pi/ai/weed_detection.py` |
| Classification | **MobileNetV2 / TFLite**, PlantVillage 38-class | `pi/ai/disease_detection.py` |
| Cameras (BOM) | forward wide row camera (₹1,800); **12MP autofocus side/downward evidence camera** (₹2,500); **macro lens + diffuse ring light** (₹2,200) | BOM #4, #5, #6 |
| **Controlled lighting** | Diffuse ring light + "trap-imaging dock, fiducial scale and controlled light" (BOM #19) | BOM #6, #19 |

**The fiducial scale (BOM #19) and the macro + ring light (BOM #6) are the two
most under-valued items in the whole BOM.** They are what turn a photograph
into a *measurement*, and §1.2, §1.4, §1.7 and §4.3 below depend on them
entirely.

### Sensing

| Element | Confirmed detail | Source |
|---|---|---|
| Soil NPK | 7-in-1 probe, **Modbus RTU over RS485/MAX485** on UART2, vendor-dependent register order, retry-with-last-good-value | `firmware/src/sensors.cpp`, `firmware/include/pins.h` |
| Soil moisture | Capacitive, ADC1_CH6 (GPIO34), **multi-point calibration curve** | `sensors.cpp` `MOIST_CAL_MV[]` |
| TDS | ADC1_CH0 (GPIO36), **temperature-compensated** | `sensors.cpp` |
| Air temp/RH | **DHT22** on GPIO14 | `pins.h` |
| Proximity | **VL53L1X ToF** (0x29) + HC-SR04 ultrasonic on a **SG90 sweep servo**, median-of-N, temp-compensated speed of sound | `pi/config.py`, `pins.h`, `sensors.cpp` |
| Position | **NEO-6M GPS** on UART1 (+ optional RTCM injection on GPIO15); wheel encoders; **MPU6050 IMU** (0x68); **EKF fusion** with `GPS_VAR_M2=2.5` (≈1.5 m σ) | `pins.h`, `pi/config.py`, `pi/nav/ekf.py` |
| Power/health | INA219 (0x40), fuel gauge, thermal guardian | `pi/sensors/*` |

### Actuation

| Element | Confirmed detail | Source |
|---|---|---|
| Drive | **2× BTS7960 (IBT-2)** tank drive, 4× 12V geared motors, LEDC PWM @1 kHz | `pins.h`, `firmware/src/drive.cpp` |
| Dosing | Relay pump (GPIO26) + **linear actuator** (GPIO13), sequential state machine, `SPRAY_FLOW_ML_S=30` | `pins.h`, `firmware/src/dosing.cpp`, `pi/config.py` |
| Aimed spray | **pan/tilt SG90** on GPIO13/19 (Pi, hardware PWM) | `pi/config.py`, `pi/ai/spray_targeting.py` |

### Data layer that already exists — and is the real asset

| Module | What it does | Why it matters here |
|---|---|---|
| `pi/data/plant_db.py` | Per-plant JSON DB, **haversine spatial matching at 0.5 m tolerance**, observation history per plant | This is a **longitudinal per-plant record**, which is what an audit artefact is |
| `pi/data/heatmap.py` | **IDW** interpolation (pure Python) + optional **kriging** (pykrige) to a field grid | Every "map" entry below is this module with a different value field |
| `pi/data/prescription_map.py` | Point NPK → IDW grid → per-cell rate → CSV/GeoJSON/ISOXML | Exists; **the input data is the problem, not the export** (§2.2) |
| `pi/data/isoxml.py` | ISO 11783 export | Prototype, **not** a validated terminal integration |
| `pi/data/recorder.py`, `pi/pipeline/pathway_stream.py` | Field-log CSV + streaming | The evidence spine |
| `pi/ai/plant_tagging.py` | Vision-tagged plant localisation to **~10–20 cm** | Better than GNSS; makes per-plant identity possible |
| `pi/ai/frame_capture.py` | Active-learning hard-case capture | The only credible route out of the PlantVillage domain gap (§4.1) |
| `pi/data/savings.py` | Chemical-savings tracker | Repo itself instructs disabling default rupee estimates until invoice-backed |

### Envelope conclusions that constrain every entry

1. **Surface RGB + geometry is the honest sensing envelope.** No hyperspectral,
   no NIR, no thermal, no chlorophyll fluorescence, no refractometer. Anything
   requiring subsurface chemistry is `[needs new sensor]` by definition.
2. **The rover is at fruiting-zone height on a trellis, and at ground level in
   a field crop.** Trellised grape bunches sit in the rover's natural imaging
   band; mango/banana crown fruit does not (`P13` verdict stands).
3. **~0.3 m/s and ~₹27–50k.** Throughput is the binding operational constraint,
   and the platform is cheap enough that a single new sensor of comparable cost
   is a material BOM decision, not a rounding error.
4. **Night operation with controlled light is an advantage, not a limitation.**
   A slow ground rover carrying its own diffuse light source removes the
   single largest source of outdoor CV variance — ambient illumination. `[H14]`
   This is the platform's one genuine, defensible physical edge over drones,
   and three high-ranked entries below rest on it.

---

## §1. The harvest-intelligence cluster (grapes and trellised perishables)

This is the cluster the seed hypothesis lives in, and it is where the ₹ and the
perishability concentrate. It is also where the temptation to overclaim is
strongest, so it is graded hardest.

### §1.1 — SEED ENTRY, PRESSURE-TESTED: grape harvest-readiness scoring and storage-matched harvest sequencing

**Verdict up front: the ripeness-index-from-RGB version of this idea does not
survive contact with the literature. A restructured version does. Read both.**

#### 1. Problem + India-specific magnitude

Grape post-harvest loss in India is driven by mistimed harvest and a cold-chain
that structurally cannot absorb the peak.

| Quantity | Figure | Label |
|---|---|---|
| Grape national post-harvest loss (NABCONS 2022, MoFPI) | **7.15%** — farm ops 5.09% + market 2.05%; biggest farm contributors **sorting/grading 2.43%** and **harvesting 1.53%** | **[External result]** `P2` |
| Nashik district | **6.69% — the LOWEST-loss district nationally**, credited to APEDA's 160 Maharashtra pack houses | **[External result]** `P2` |
| Literature range (broader) | Sharma et al. 2018 review: **8.23–16%**; Murthy et al. 2014 (Thompson Seedless export chain): **7.82% field + 12.13% cold-storage** | **[External result]** `P2` |
| Pack-house infrastructure gap | NCCD demand-driven assessment: **70,080 pack-houses required vs 249 created** (gap 69,831); **reefer vehicles 61,826 required vs ~9,000** (gap 52,826) | **[External result]** `[H01]` ([NCCD gap analysis, as reported](https://www.nccd.gov.in/)) |
| National cold storage, May 2024 | **395 lakh MT across 8,698 facilities**; bulk cold-storage gap ~10%, but the gap is **overwhelmingly in pack-houses and reefers, not bulk potato-style storage** | **[External result]** `[H02]` |
| Nashik grape exports 2025-26 | **1.4 lakh tonnes, down 9.6%** on unseasonal rain/hail | **[External result]** `[G32]` |
| Indian grape exports 2024-25 | **271,253 MT, ≈₹3,050 crore** | **[External result]** `[H03]` |
| Weather destruction, Oct 2025 | **~45,000 ha** Nashik vineyards damaged, **≈₹3,500 crore** feared loss; Qualicrop estimated ~50% average season loss (white seedless 40–70%, black seedless 30–50%) | **[External result]** `P10` |

**The magnitude finding that reframes the seed hypothesis.** Nashik is already
the *best-performing* grape district in India at 6.69% loss `P2`. The seed
premise — "cold-storage scarcity causes grape loss in Nashik" — is **half
wrong**: the bulk-storage gap is ~10% nationally `[H02]`, while the acute gap is
in **pack-houses (99.6% shortfall) and reefers (85% shortfall)** `[H01]`. Those
are *throughput* constraints, not *volume* constraints.

**This actually strengthens the sequencing idea while destroying the framing.**
A pack-house/reefer bottleneck is precisely a **scheduling** problem: a fixed
number of grading lines and refrigerated trucks per day, against a block of
fruit that all becomes ready in a narrow window. Volume scarcity would need
concrete; throughput scarcity needs a **queue discipline**. A rover can
contribute to a queue discipline. It cannot pour concrete.

**In rupees.** At ₹3,050 crore of exports `[H03]` and the export chain's
**7.82% field loss** `P2`, field-stage loss in the export grape chain is of the
order of **₹240 crore/year** nationally. **[Analyst scenario]** — arithmetic
only, applying a national loss share to a national export value; neither is
locally measured, and the *addressable* fraction is a small slice of this.

#### 2. The rover mechanism

**Senses:** per-bunch RGB from the 12MP autofocus evidence camera at controlled
standoff, with the **fiducial scale** (BOM #19) in frame and **diffuse ring
light** (BOM #6) suppressing ambient variance; GPS + vision-tagged plant
identity at ~10–20 cm (`pi/ai/plant_tagging.py`); ToF for standoff control.

**Computes:** per-bunch **geometric and colorimetric descriptors** — bunch
bounding volume, berry count where separable, berry diameter distribution
against the fiducial, colour distribution / veraison fraction, visible defect
and shrivel fraction — written to `plant_db.py` as a per-bunch observation
series across repeat visits, then IDW/kriged (`heatmap.py`) into a block-level
map.

**Output someone acts on:** a **block-level, date-stamped harvest-order
sequence** — which blocks to cut on which day, ranked, sized in crates against
the grower's *actual* booked pack-house slots and reefer capacity.

#### 3. Feasibility on the CURRENT platform — honestly graded

This must be split, because the two halves have opposite answers.

| Sub-claim | Grade | Evidence and likely error |
|---|---|---|
| **(a) Estimate Brix/TSS from an RGB photo** | **[not feasible at the accuracy required]** — downgraded | See below. This is the physically dubious claim and it must be said plainly. |
| **(b) Measure bunch/berry geometry, colour and visible defects** | **[buildable now]** | Geometry against a fiducial and colour against a controlled light source are direct optical measurements. YOLOv11-class cluster detection reaches **94.3% precision** `[H05]`; multi-view raises tracked-to-ground-truth bunch ratio from **~23% (single view) to 74% (multi-view)** `[H04]`. |
| **(c) Sequence harvest against booked cold-chain slots** | **[buildable now]** — but it is scheduling software, not robotics | Needs the pack-house's slot calendar as an input. The rover is one data source, not the product. |

**(a) in detail — why sugar-from-a-photograph must be downgraded.**

Brix is a **bulk chemical property of juice**. An RGB camera measures reflected
visible light from the berry **skin**. Any RGB→Brix model is therefore
correlational, mediated by skin colour, and inherits the confounds of skin
colour: variety, sun exposure, canopy position, dust, spray residue film, and
time of day.

The literature says exactly this. **[External result]** `[H06]`:

| Setting | Reported error | Interpretation |
|---|---|---|
| Controlled laboratory, feature-based RGB | **RMSE ≈ 0.78 °Brix** | Best case, not a field number |
| Field, recent deep learning | **MAE ≈ 1.05 °Brix** | Best *field* case reported |
| Field, alternative RGB methods | **RMSE ≈ 4.63 °Brix** | The honest spread |
| Hyperspectral / multispectral | **RMSE ≈ 0.25–1.27 °Brix** | The sensor class that actually does this |

Now put that against the **decision threshold**. EU table-grape maturity
requires **minimum 16 °Brix**, or a sugar:acid ratio of **20:1 for 12.5–14
°Brix** and **18:1 for 14–16 °Brix** `[H07]` **[External result]**. The
regulated decision is a **pass/fail at 16 °Brix**.

An estimator with field MAE of **1.05 °Brix** — the *best published field
result* — straddles that threshold. A true 15.2 °Brix bunch reads as compliant
about as often as not. At the 4.63 RMSE end `[H06]`, the estimate is
**decision-worthless**. And the sugar:acid alternative is worse still: **acidity
has no RGB correlate at all.** There is no visible-light proxy for titratable
acidity, so the entire 18:1/20:1 branch of the standard is unreachable by this
sensor **in principle**, not merely in practice.

**Therefore: AgriRover must not output a Brix number, and must not output a
"0–100% ripeness index" that a buyer will read as a Brix proxy.** A refractometer
costs a few hundred rupees and gives the grower a **direct, destructive,
trusted** measurement of the quantity that actually governs the export
decision. Competing with a ₹500 refractometer on its own metric, using a sensor
that is physically wrong for the job, is the single most likely way for this
programme to lose credibility with an exporter's QC team on day one.

**What survives, and it is not small.** The literature's own framing is that
**multi-view geometry** is where ground platforms win `[H04]`, and geometry is
what an RGB camera + fiducial + controlled light genuinely measures. So the
defensible output is:

> **Not** "this block is at 17 °Brix" **but** "this block's bunches are
> geometrically and colorimetrically **uniform and advanced relative to the
> other eleven blocks**, it holds ~N crates, and the grower's refractometer
> should sample **here first**."

That is a **sampling allocator and a queue discipline**, not a ripeness sensor.
It makes the grower's existing refractometer more efficient rather than
pretending to replace it. It is also honest about what a camera does.

**Residual error even on the geometry claim.** Occlusion is the dominant term:
single-view tracks only ~23% of ground-truth bunches `[H04]`; motion blur from
robotic platforms is a named unsolved issue `[H04]`; ID-matching failures occur
in dense canopy `[H04]`. Indian grape trellis systems (Y-trellis, flat roof
"pandal"/bower) present a **denser, more occluding canopy than the vertical
shoot-positioned trellises most of this literature was collected on** — so
expect worse than 74%. Yield-mass inference at **~5–7% error** `[H05]` is a
best-case published figure on favourable architecture; it should not be assumed
to transfer.

#### 4. Value & who pays

**Who pays: an exporter or a large processing FPO — never the grower.** This is
the one entry in the catalog whose payer is fully consistent with the v3
conclusion `[G11]`, `[G12]`, `[G15]`: **Sahyadri Farms** class (₹1,955 cr FY25,
30,000+ farmers, existing IoT traceability) or a Nashik grape exporter under
GrapeNet.

**Why they might pay:** they hold the **scarce asset** (pack-house slots,
reefers) `[H01]`, they carry the **liability** `[G15]`, and their loss function
is asymmetric — a rejected container triggers the APEDA ladder (1st → warning +
written explanation in 7 days; 2nd → **15-day exporter suspension**) `[E05]`.
Better queue discipline on a scarce, capital-intensive asset is a procurement
decision, not an information purchase — which is exactly the category `[F01]`
and `[G01]` say must be sold.

**How it fits the WTP and route-density constraints — the honest part.** It
fits **better than any tomato entry** on three counts and **worse on one**:

- *Fits:* the buyer is solvent by four orders of magnitude vs JTFPC `[G10]`,
  `[G11]`; the object sold is a physical act (scheduling a scarce asset), not
  information; a vineyard is **perennial, trellised and geometrically regular**,
  which is the friendliest possible route geometry for a 0.3 m/s platform.
- *Fits, and this is under-appreciated:* **route density is structurally
  better** than in Junnar tomato. Sahyadri-class aggregation means contiguous
  registered plots under one contracting entity, which is the "dense" row of
  §11.3 (₹387/acre-pass) rather than the fragmentation-realistic sparse row
  (₹946) `[G04]`, `[P12]`.
- *Fights:* the value is **seasonal and compressed**. Harvest sequencing is
  useful for perhaps 4–8 weeks per year. §11's break-even needs **≥100 active
  days/year** `[G13]`. A single-purpose harvest-sequencing rover cannot reach
  100 days. **This entry is only viable as one mission profile on a rover that
  also does §3.1 (residue/PHI records) and §4.2 (mildew scouting) on the same
  vines across the same season.** Standalone, it fails the active-days gate.

**Loss avoided — stated with its own caveat.** **[Analyst scenario]:** if
better sequencing recovered even one-fifth of the export chain's 7.82% field
loss `P2` on a 40,000-acre aggregator footprint, the arithmetic is large. That
calculation is **deliberately not completed here**, because the input — the
fraction of field loss attributable to *sequencing* rather than to weather,
handling, grading or transit — **is unknown and is not in any source located**.
Producing a rupee figure from an unknown fraction would be exactly the
pitch-deck behaviour this dossier exists to prevent.

#### 5. Proof gate

| Metric | Method | Threshold |
|---|---|---|
| Bunch detection recall on **Indian trellis** (Y/bower, not VSP) | 3 varieties × 3 canopy densities, hand-counted ground truth on ≥300 tagged bunches | **≥85% recall, ≥80% precision** per variety |
| Multi-view bunch tracking ratio | Repeat passes, matched via `plant_db.py` 0.5 m tolerance | **≥74%** (parity with `[H04]`) or the mechanism is not viable |
| **Sampling-allocator value** (the actual claim) | Rover ranks 12 blocks; grower refractometers **n** bunches/block; measure whether rover-first sampling reaches the true ripest block in **fewer samples** than the grower's current walk | **≥30% fewer refractometer samples** to identify the ripest block |
| Crate-count estimate | Rover crate estimate vs weighbridge at pack-house intake | **±15% per block** |
| Slot-utilisation effect | Booked pack-house slots filled vs baseline season | **[AgriRover target]** — measure, do not promise |
| **Explicitly NOT a gate** | Brix RMSE | **Do not measure it, do not claim it** — see (a) |

**Note the last row.** Refusing to build the metric is the disciplined choice.
If a Brix number is never produced, it can never be over-trusted.

#### 6. Verdict

**Pursue now — but only as a "sampling allocator + crate forecast + queue
discipline", bundled with §3.1 and §4.2 on the same vines, sold to a
Sahyadri-class aggregator or Nashik exporter. Never as a ripeness or Brix
sensor.**

---

### §1.2 Pre-bloom / fruit-set counting for early yield forecasting and logistics booking

**1. Problem + magnitude.** Nobody knows the size of the crop until it is
nearly on the truck, so nothing downstream can be booked in advance. The
consequence at market level is the synchronized glut: 2023 saw Kolar arrivals
of 4.21 lakh quintals in a month vs 2.31 lakh the prior year, a 15 kg tomato box
falling **₹2,300 → ₹45–120**, and Kolar recording the **lowest** post-harvest
losses nationally (9.46%) — proving the loss was **pure market failure, not
handling failure** `P8` **[External result]**. For grapes, the 2025-26 export
volume moved **−9.6%** on weather `[G32]`, and an aggregator that knew this in
week 3 rather than week 20 could re-contract. RBI analysis puts the farmer's
share of the consumer rupee at **35% for grapes, 33% tomato** `[External result]`.

**2. Rover mechanism.** **Senses:** inflorescence/flower clusters pre-bloom, then
set berries, from the 12MP evidence camera under the **ring light at night**.
**Computes:** YOLO-class inflorescence detection + count per vine, extrapolated
by vine census to block level; stored as a per-plant time series in
`plant_db.py`. **Output:** a **crate/tonnage forecast issued 8–14 weeks before
harvest**, with confidence bounds, to the aggregator's procurement desk.

**3. Feasibility: [buildable now] — and this is the strongest CV result in the
catalog.** Published grapevine flower-counting models (YOLOv5/v8/v11) reach
**R² > 0.90** for flower counts `[H08]` **[External result]**. Critically, the
same literature finds that **pre-bloom daylight imaging is unreliable due to
environmental variability, and that nighttime imaging with controlled artificial
lighting significantly improves detection performance and stability** `[H08]`,
`[H14]`. **That is a direct, published endorsement of this platform's exact
physical configuration** — a slow ground vehicle that carries its own diffuse
light and can work at night. A drone cannot do this; a fixed IoT sensor
(Fyllo/Fasal `[F05]`) cannot do this because it sees one point, not 5,000 vines.
**This is the one capability where AgriRover is not squeezed from both sides.**

*Honest error.* R² > 0.90 is on flower *counts in imaged frames*, not on final
tonnage. Between bloom and harvest sit fruit-set ratio, weather, thinning
decisions and berry-size outcome — each adding variance the count cannot see. A
count-to-tonnage model needs local per-variety calibration over **at least two
seasons** before its bounds are trustworthy. Claiming a tonnage forecast from
one season of flower counts would be dishonest.

**4. Value & who pays.** **The aggregator/exporter procurement desk** — the
same Sahyadri-class buyer as §1.1 `[G11]`. An advance volume forecast is
directly actionable for them: contract negotiation, reefer and slot booking
`[H01]`, export commitments, and packaging procurement. This is **not
information sold to a farmer** (`[F01]`'s ₹14.89 trap); it is a **procurement
input for an entity whose planning error costs crores**. It also fixes §1.1's
active-days problem: bloom-stage passes happen **months before** harvest-stage
passes, on the same vines, extending the rover's season materially.

**5. Proof gate.**

| Metric | Method | Threshold |
|---|---|---|
| Flower/cluster count accuracy | Night imaging, ring light, ≥200 vines, destructive hand count | **R² ≥ 0.85** vs hand count (below `[H08]`'s 0.90 to allow for Indian trellis occlusion) |
| Count → tonnage calibration | Two seasons, ≥3 varieties, weighbridge truth | **±20% block tonnage at 10 weeks out**, with published bounds |
| Night-vs-day advantage | Paired passes, same vines | Confirm `[H08]`'s finding **on Indian canopy** or the night thesis fails |

**6. Verdict: pursue now.** Highest feasibility-times-payer score in the
catalog; it is the entry that best exploits the platform's one genuine physical
edge.

---

### §1.3 Salvage-priority harvest ordering under a 48–72 h weather warning

**1. Problem + magnitude.** Everything ripens at once and a single rain event
destroys it. Oct 2025: **~45,000 ha** Nashik vineyards damaged, **≈₹3,500 crore**
feared, two grower suicides, ~50% average season loss `P10` **[External
result]**. Nov 2023 hailstorm hit ready-to-harvest vineyards; **growers with
crop covers were spared** `P10`. Grape is **non-climacteric** — it does not
ripen after cutting, so an early cut is a permanent quality loss, and a late cut
in front of rain is a total loss.

**2. Rover mechanism.** Reuses §1.1's block map and §1.2's counts: when a
forecast gives 48–72 h warning, output a **ranked cut-order** — which blocks are
geometrically/colorimetrically most advanced *and* largest, so scarce harvest
labour and scarce reefer slots go to the fruit with the most value at risk.
**No new sensing.** This is a query over data the rover already holds.

**3. Feasibility: [buildable now], with an explicit dependency.** The ranking
logic is trivial once §1.1 and §1.2 exist. But it inherits §1.1's error bars
entirely, and it **cannot resolve the actual agronomic question** ("is this
block *ready*?") because that is Brix, which is `[not feasible]` (§1.1a). It can
only answer the *relative* question ("which block is furthest along?"). For
salvage triage, relative ranking is genuinely sufficient — you are choosing an
order, not certifying a standard. **This is the one context where the RGB
sensor's relative-only limitation does not bite.**

**4. Value & who pays.** The grower feels this most, and **the grower will not
pay** `[F01]`, `[G01]`. The payer is again the aggregator, whose contracted
volume is what is being salvaged, or — the interesting variant — an **insurer**.
`P28` (AGRI_PROBLEMS §3.14) notes crop insurance already sells risk
protection; a geotagged,
timestamped pre-event condition record is a **loss-adjustment artefact**. That
is an audit artefact for a liable party, which is the one object v3 says is
sellable `[G19]`. Flagged as a distinct payer hypothesis worth its own research;
not asserted, because no insurer WTP evidence was located.

**5. Proof gate.** Rover-ranked cut order vs agronomist-ranked cut order on the
same 12 blocks: **≥0.7 Spearman rank correlation**, and in ≥1 real weather
event, document whether the ranking was actually used and what it changed.
**[AgriRover target]**

**6. Verdict: pilot later.** Zero marginal build cost on top of §1.1/§1.2, real
emotional salience, but it is a bundled feature and its standalone payer is
unproven.

---

### §1.4 Banana caliper grading and harvest-window call at bunch height

**1. Problem + magnitude.** Indian banana post-harvest loss runs **20–30%**
`[H09]` **[External result]**; in **Jalgaon, Maharashtra** specifically,
documented stage-wise losses are **6.81% farm + 3.90% transport + 1.56%
wholesale + up to 14.12% retail** `[H09]`. Export requires harvest at **75–80%
maturity**, and the governing grading metric is **caliper — fruit diameter
measured at the midpoint** — with export grades specified in bands such as
**46–50 mm** `[H09]` **[External result]**.

**2. Rover mechanism.** **Senses:** the bunch from the side, at rover height,
against the **fiducial scale** (BOM #19) with ring light. **Computes:** finger
diameter distribution in **millimetres**, finger angularity (the classic
maturity cue), hands per bunch. **Output:** a per-bunch **"cut this week / next
week" call and a predicted export-grade yield split**, per plot.

**3. Feasibility: [buildable now] — and it is the cleanest sensing claim in the
whole catalog.** Caliper is a **length**. A calibrated camera with a fiducial in
frame at controlled standoff measures length directly — this is photogrammetry,
not inference. There is no chemical proxy, no correlation, no domain gap.
Angularity (cross-section fullness) is likewise geometric. Unlike §1.1's Brix,
**the regulated decision variable and the sensor's native output are the same
physical quantity.** Expected error is dominated by standoff and pose control,
both of which the ToF sensor and adjustable camera mast (BOM #9, #20) exist to
manage; sub-2 mm is a reasonable engineering target for a fiducial-calibrated
setup, and 2 mm on a 46–50 mm band is a usable decision.

*The honest limit:* banana plants are tall, but **the bunch hangs at or near
rover imaging height** — unlike mango/banana *crown* geometry, which `P13`
correctly rules out. Bunch bagging (common in export banana) may occlude the
fruit entirely, which would defeat the measurement; this must be checked against
actual Jalgaon practice before anything else is built.

**4. Value & who pays.** Banana export pack-houses and aggregators. The
persona is the same class as §1.1 — a liable, solvent buyer of graded fruit.
Route density in Jalgaon banana is plausibly **good** (dense, contiguous,
irrigated blocks), but this is **unmeasured** and subject to the same §11.4
survey requirement as Junnar `[G04]`. Jalgaon is also a **new geography**,
adding a market-entry cost the grape wedge does not carry — which is why this
ranks below §1.1/§1.2 despite better physics.

**5. Proof gate.** Rover caliper vs manual vernier caliper on ≥500 fingers
across ≥50 bunches: **±2 mm at 95%**; grade-split prediction vs pack-house
actual grade-out: **±10 percentage points**. Bagging-occlusion survey completed
**before** any model work. **[AgriRover target]**

**6. Verdict: pilot later.** Best physics-to-decision match in the catalog, but
a different crop, district and buyer network than the grape wedge. Park until
the grape bundle is proven, then port — the *measurement method* transfers
almost unchanged.

---

### §1.5 Pre-storage / pre-pack screening of onion and tomato lots

**1. Problem + magnitude.** Onion storage rot in traditional *kanda chawl*
structures runs **35% to over 60%** over a season (35% is the *minimum*, only in
favourable conditions); NABARD records **50–90% over six months**; ICAR found
bottom-and-side-ventilated structures still lose **up to 46% in 4 months**, vs
7.14% in a cold-storage trial against **54%** uncontrolled `P4` **[External
result]**. NABCONS names **harvesting (2.48%)** as onion's biggest farm-level
loss operation, and **sorting/grading (3.1%)** as tomato's single largest `P2`,
`P8`. Rot propagates from damaged/infected bulbs entering the store.

**2. Rover mechanism.** Camera-based screening of harvested lots — surface rot,
bruising, neck condition, sprouting — before they enter storage, plus in-field
disease-pressure maps indicating which blocks' output is high-risk.

**3. Feasibility: [not feasible for a slow ground rover] as a lot-screening
station; [buildable now] only as an in-field pressure map.** Two hard reasons.
First, **throughput arithmetic**: a rover imaging individual bulbs at ~0.3 m/s
`[G26]` against tonnes of harvested onion is off by orders of magnitude — this
is a **conveyor-and-line-scan-camera problem**, and a stationary sorting line is
a strictly better machine for it, which is what the Narayangaon automated
pack-house track is already building `P2` **[External result]**. Second, the
decisive loss mechanism is **internal** — physiological weight loss 30–40%,
rotting 20–30%, sprouting 20–40% `P4` — and internal rot in a sound-skinned bulb
is invisible to surface RGB. Both existing dossiers already grade this
**NOT SOLVABLE (core), thin PARTIAL slice** `P4`, `P11`, `P22`, and that verdict
is correct and unchanged.

**4. Value & who pays.** Nobody, for the rover version. Storage structures and
grading lines are **capital-infrastructure purchases**, and a rover competing
against a conveyor loses on every axis.

**5. Proof gate.** None — do not build. If it were ever attempted, the gate
would be throughput (bulbs/hour vs a ₹2 lakh line-scan grader), and it would
fail it.

**6. Verdict: park.** Listed to record that it was examined and rejected on
throughput physics, not overlooked. **Say this plainly at Baramati.**

---

### §1.6 Mango and other overhead-canopy tree fruit

**1. Problem + magnitude.** Mango PHL **8.53%** nationally, with the two largest
farm operations being **sorting/grading (2.74%)** and **harvesting (1.80%)**;
worst state Bihar 10.10%, best AP 7.89% `P13` **[External result]**.

**2/3. Feasibility: [not feasible for a slow ground rover].** The fruit is in
the **overhead crown**; a ground rover images trunks and low canopy. No model
fixes a viewing geometry problem. `P13`'s verdict stands verbatim.

**4–5.** No payer, no gate.

**6. Verdict: park.** Retained because the number proves harvest-and-grading
pain is **cross-crop**, which is the argument for §1.1/§1.4 *where the fruit is
at rover height* — trellised vines and hanging banana bunches. This is the
honest boundary of the harvest-intelligence thesis.

---

### §1.7 Bunch-thinning and canopy-work verification (labour audit)

**1. Problem + magnitude.** Nashik grape cost of cultivation (Cost C) is
**₹690,422/ha**, of which **hired human labour is 16.9%** (male 11.25% + female
5.65%) — roughly **₹117,000/ha** — with thinning, dipping, spraying and bunch
cleaning named as the labour-intensive operations driving it `[H10]`
**[External result]**. Nationally, **34 million workers left agriculture**
between 2004-05 and 2011-12 and labour scarcity is documented to **shift harvest
timing off the agronomic optimum** `P9` **[External result]**. Bunch thinning
quality directly determines export grade — it is the operation that decides
berry size — and on a large aggregator's contracted acreage **nobody can verify
it was done properly** across thousands of vines.

**2. Rover mechanism.** **Senses:** bunches before and after a thinning
operation, same vines, matched via `plant_db.py` 0.5 m spatial identity.
**Computes:** berry-count-per-bunch and bunch-geometry delta. **Output:** a
per-block **"thinning completed to spec / not to spec"** report with geotagged
image evidence — an operations-verification artefact for whoever paid for the
labour.

**3. Feasibility: [buildable now], with the same occlusion caveat as §1.1b.**
It is a **paired-difference** measurement, which is far more robust than an
absolute one: systematic biases (occlusion rate, lighting, camera pose) largely
cancel between the before and after pass of the same vine. Detecting *"this
bunch lost ~40% of its berries"* is materially easier than *"this bunch has
exactly 87 berries"*. The `plant_db.py` 0.5 m matching and `frame_capture.py`
infrastructure already exist as **[Repository fact]**.

**4. Value & who pays.** **This is a labour-audit artefact sold to the entity
that pays the labour bill** — an aggregator managing contracted acreage, or a
large grower with ₹117,000/ha of labour exposure `[H10]`. Structurally it is the
**same product shape as the residue/PHI record (§3.1)**: a timestamped,
geotagged verification that a specified physical act was performed to
specification. v3 says that shape is the **one thing that sells** `[G19]`. It is
not information the buyer could have guessed — it is a fact about work done on
plants they cannot personally inspect.

**5. Proof gate.** Paired before/after passes on ≥300 bunches: rover-reported
berry-removal fraction vs hand count, **±15%**; and the operational gate —
**does an aggregator's field-operations manager change a payment, a crew
assignment or a re-work order** on the strength of the report? If no
operational decision changes, the artefact is not a product. **[AgriRover
target]**

**6. Verdict: pursue now (bundled).** Underrated, novel, mechanically honest,
and it stacks onto §1.1/§1.2 on the same vines with **no new hardware** — while
adding active days in the thinning window. It also has the cleanest "physical
act verified" story in the catalog after §3.1.

---

## §2. The soil, water and nutrient cluster

This cluster contains the catalog's most attractive-looking hardware (a 7-in-1
NPK probe on an industrial Modbus bus) attached to its **weakest science**. It
is graded accordingly.

### §2.1 Irrigation scheduling and water-stress detection from canopy + soil moisture

**1. Problem + magnitude.** Groundwater depletion is arguably India's largest
agricultural sustainability threat `P17`, and grape/pomegranate irrigation
timing directly drives berry size, cracking and rot. Nashik's Cost C is
**₹690,422/ha** `[H10]`, so a mistimed irrigation at berry development is
expensive in quality terms, not just water terms.

**2. Rover mechanism.** **Senses:** capacitive soil moisture (multi-point
calibrated, `sensors.cpp`), TDS (temp-compensated), DHT22 air temp/RH, and
canopy RGB for wilt/leaf-angle/colour change — sampled at repeatable geotagged
sentinel points. **Computes:** an IDW/kriged moisture and salinity map
(`heatmap.py`) plus a canopy-condition index. **Output:** per-zone irrigation
"more/less/hold" with a salinity flag.

**3. Feasibility: [needs new sensor — thermal] for the stress claim; [buildable
now] for a spot-sampled moisture/salinity map.** The literature is explicit:
RGB detects water stress only via **visible symptoms — leaf coloration changes
from reduced chlorophyll/carotenoid content** — and is **less accurate than
thermal**, being constrained by lighting and leaf orientation `[H11]`
**[External result]**. Thermal **CWSI** measures canopy temperature directly as
stomata close, and is the sensitive, reliable method — yet even CWSI is **prone
to late detection** and suffers soil-background interference, atmospheric
normalization complexity, and humidity/wind sensitivity `[H11]`.

Read that carefully: **the *good* sensor is already "prone to late detection",
so an RGB proxy for it is detecting a problem that is both late and
second-hand.** By the time chlorophyll loss is visible in RGB, the irrigation
decision was needed days earlier. **The named missing sensor** is a radiometric
thermal camera (FLIR Lepton-class, ~₹15,000–25,000, i.e. **30–50% of the entire
₹50k BOM ceiling**) plus ambient wet/dry reference for CWSI normalization —
which is a major BOM decision, not an add-on.

The moisture probe itself is real but **point-sampled**: a rover visiting weekly
gives ~52 readings/point/year, while a ₹6,000–16,000 Fyllo Nero sits in the soil
and reads continuously `[F05]`. **For a slowly varying state variable, a cheap
fixed sensor beats an expensive mobile one, decisively.** This is the
competitor dossier's core objection `[F05]`, and it is unanswerable here.

**4. Value & who pays.** **Nobody, for the rover version.** The competitor is
Fyllo/Fasal at **₹400–750/month** with a device the farmer owns, never moves,
and which needs no operator, no battery swap and no route density `[F05]`.
AgriRover loses on every operational axis for this specific job.

**5. Proof gate.** Not applicable — do not build. The only defensible gate would
be a paired trial against a ₹6,000 fixed probe, which is a trial designed to
lose.

**6. Verdict: park.** Irrigation is a fixed-sensor market. The rover should
**carry** moisture/TDS readings as free context on passes it is making anyway —
never as a reason for the pass.

---

### §2.2 Nutrient deficiency mapping from leaf colour + the 7-in-1 NPK probe

**1. Problem + magnitude.** Fertilizer is applied blind; Soil Health Card
coverage and utility are weak; NPK imbalance is a national price-policy problem
`P18`, `P19` (AGRI_PROBLEMS §3.4). The value at stake is genuinely large —
fertilizer is a top-3
line item on most crops.

**2. Rover mechanism (as designed in the repo).** RS485/Modbus 7-in-1 probe →
per-point N/P/K → `heatmap.py` IDW grid → `prescription_map.py` per-cell rate
→ CSV/GeoJSON/**ISOXML** for a variable-rate applicator. Plus MobileNet leaf
classification of visible deficiency symptoms.

**3. Feasibility: [not feasible — the sensor does not measure the quantity].
This is the most important negative finding in the catalog.**

Independent validation of low-cost 7-in-1 NPK sensors finds they **do not
accurately measure soil nutrient concentrations** at all. The mechanism is the
problem: these devices **measure soil electrical conductivity (EC) and multiply
by a fixed factory factor**, yielding "an empirical, theoretical value rather
than an actual chemical analysis". Validation studies **consistently report poor
correlation with lab results, high sensitivity to moisture, and significant
errors especially for potassium**, and the devices are recommended **only for
qualitative trend monitoring, never quantitative fertilizer management**
`[H12]` **[External result]**.

This is not a calibration problem that better firmware fixes. **N, P and K are
distinct chemical species; a single bulk-EC measurement cannot resolve three of
them.** The information is not in the signal. It is worth noting that the
repository's own `sensors.cpp` header already flags *"NPK register order is
vendor-dependent"* **[Repository fact]** — the ambiguity starts at the wire
protocol, before any agronomy.

**The consequence is severe and must be stated:** `prescription_map.py` is a
**correctly implemented pipeline fed by a physically invalid input**. IDW
interpolation and ISOXML export of meaningless numbers produces a
professional-looking, geotagged, exportable prescription map that is **wrong**,
and whose wrongness is *invisible* because the output format is credible. That
is worse than having no map — a farmer could over- or under-fertilize on the
strength of it. The **leaf-colour** half is separately limited: visible
deficiency symptoms appear **only after yield has already been lost**, and
generic-symptom classifiers inherit §4.1's domain gap.

**The named alternative, for honesty:** real soil chemistry requires **wet-lab
or ion-selective-electrode analysis** — i.e. the Soil Health Card lab route
`P18`. There is no ₹3,000 probe that replaces a lab.

**4. Value & who pays.** No defensible payer. Selling a fertilizer
prescription derived from a bulk-EC reading is the clearest **liability** in
this catalog, not a product.

**5. Proof gate — the one that must be run before anything else.** Split-sample
the probe against an **NABL-accredited soil lab** across ≥30 points spanning ≥3
moisture levels. Threshold: **r ≥ 0.8 per nutrient, independently at each
moisture level.** `[H12]` predicts failure, especially for K. **If it fails —
which is the expected outcome — `prescription_map.py` must be
feature-flagged off, and the repository must state that its NPK output is a
qualitative trend indicator only.**

**6. Verdict: park — and act on it.** The repo already excludes the NPK probe
and doser from the launch BOM and the first pilot **[Repository fact]**
(`BOM-top20` explicitly: *"A low-cost NPK probe, fertilizer doser… are excluded
because none can currently support a safe farmer-profit claim"*). `[H12]`
supplies the external evidence that this exclusion was **correct and should be
permanent** until a lab correlation passes. **This is the catalog's clearest
"stop shipping a feature" recommendation.**

---

### §2.3 Soil compaction, pH and salinity zoning

**1. Problem + magnitude.** Salinity and pH drift degrade yield persistently in
irrigated Maharashtra horticulture; the effect compounds silently over seasons.

**2/3. Feasibility: [needs new sensor].** TDS gives a crude **bulk EC/salinity
proxy** — genuinely the *one* thing an EC-based sensor legitimately measures
(`[H12]`'s critique is about deriving N/P/K from EC, not about EC itself). But
**pH requires an ion-selective electrode** with calibration buffers and
maintenance, and **compaction requires a penetrometer** — a mechanical
force-insertion device the rover has no mount, mass or actuator for (the
linear actuator is a 500 ml dosing device, not a soil probe). Named additions:
ISE pH probe (~₹4,000–8,000, consumable-dependent) and a load-cell penetrometer
(mechanically incompatible with a ~25 kg platform, which lacks the reaction mass
to push a cone into dry soil).

**4–5.** No payer at this cost; no gate worth running.

**6. Verdict: park.** Salinity trend logging is a free by-product of passes made
for other reasons. Nothing more.

---

## §3. The compliance and audit-artefact cluster

v3 concluded that **exactly one sellable object survives**: an audit artefact
sold to an entity that is itself the liable party `[G19]`. This cluster is that
object. It ranks highest on "who actually pays" and lowest on technical novelty
— which is precisely why it is the wedge.

### §3.1 Per-plot residue / PHI / spray-record artefact for the export chain

**1. Problem + magnitude.**

| Quantity | Figure | Label |
|---|---|---|
| RASFF 2025 | **India topped all countries with 124 pesticide notifications** | **[External result]** `[F17]`, `[H13]` |
| APEDA grape escalation | 1st rejection → warning + written explanation in **7 days**; 2nd → **15-day exporter suspension**; residue certificate required within **6 days** of sampling; NRL internal alert within **24 h** of a failed sample | **[External result]** `[E05]`, `[E06]` |
| Historic loss | 2010 chlormequat detections → multiple container rejections of Maharashtra grapes, reported **~₹250 crore** | **[External result]** `P6` |
| EU audit | India's residue controls for plant-origin exports audited **Oct 2024** (audit 2024-7978) | **[External result]** `[E05]` |
| Export value exposed | **271,253 MT ≈ ₹3,050 crore** (2024-25 grapes) | **[External result]** `[H03]` |
| Plot registration | GrapeNet plot registration **mandatory annually**, ₹50/plot/yr | **[External result]** `[G17]` |

**2. Rover mechanism.** **Senses:** nothing exotic — geotagged, timestamped
imagery of the plot and crop state at each visit, at ~10–20 cm plant-level
identity (`plant_tagging.py`). **Computes:** a per-plot chain-of-custody record
in `plant_db.py`/`recorder.py`: observation → agronomist-reviewed
recommendation → product/active ingredient/rate/date applied → **PHI clock** →
revisit and outcome verification. **Output:** an **audit-ready per-plot dossier**
that maps onto GrapeNet's plot-level traceability requirement, with the PHI
countdown as the actionable item ("this plot must not be harvested before
date X").

**3. Feasibility: [buildable now] — and it is the least technically demanding
entry in the catalog.** It requires **no new sensor and no accurate classifier**.
Geotagging, timestamping, image capture and a per-plant JSON history are all
**[Repository fact]** today. The hard parts are *not* CV: they are (i) the
agronomist review desk, priced at **₹43–₹1,730/pass** depending on utilisation
§11.5; (ii) a **tamper-evident** record — an audit artefact that the audited
party can silently edit is worthless, so hash-chaining the record and signing it
with the existing HMAC/TLS infrastructure is the real engineering work; and (iii)
mapping the schema onto GrapeNet/APEDA field requirements.

**The honest structural problem — and it is the biggest in the catalog.** The
rover is **not necessary** for this artefact. A ₹15,000 phone with a GPS-stamped
camera app and a disciplined agronomist produces most of the same record. The
rover's only defensible added value is **repeatability at scale**: identical
pose, standoff, scale and lighting on the same plants every visit (BOM #19's
fiducial dock exists for exactly this), across thousands of plots that no
agronomist can physically visit weekly. **That argument must be won on
measurement, not asserted** — and if a phone-plus-agronomist matches the rover's
audit pass rate, the correct conclusion is to sell the phone workflow and
retire the rover for this use case. §15's go/no-go should include that test.

**4. Value & who pays.** **The exporter or the large processing/exporting FPO —
Sahyadri-class `[G11]`, `[G12]` — because they are the liable party** `[G15]`.
The grower is statutorily exempt `[G03]`, so **every domestic-grower compliance
pitch is void** and must not be made. The value is **avoided catastrophe**: a
15-day suspension mid-season against a ₹3,050 crore national export flow
`[H03]`, `[E05]`. WTP here is not benchmarked against ₹14.89/acre information
`[F01]`; it is benchmarked against **insurance and audit spend**, a completely
different budget line that already exists — and existing spend is the only kind
v3 accepts. Route density is also favourable: registered export plots are
contiguous, aggregated and already enumerated in GrapeNet `[G17]`.

**5. Proof gate.**

| Metric | Method | Threshold |
|---|---|---|
| **Mock audit** | An APEDA-experienced auditor or exporter QC lead reviews a full season's rover record set for ≥10 plots | **Passes a mock GrapeNet/APEDA audit with zero critical non-conformities** |
| Record completeness | Fraction of applications with product, AI, rate, date, operator and PHI captured | **≥98%** |
| Tamper evidence | Independent attempt to alter a record undetected | **Must fail** |
| **Necessity test** (the one that matters) | Parallel arm: phone + agronomist vs rover, same plots, same season | Rover must show a **material, measured advantage** in repeatability or coverage, or this use case does not need a rover |
| PHI-violation catch | Harvests that would have breached PHI, flagged in advance | **[AgriRover target]** — count them |

**6. Verdict: pursue now — this is the wedge, and it is the only entry whose
payer is fully proven by prior research.** Note honestly that it is also the
entry that least requires a robot; the pilot must include the necessity test
above rather than assume the answer.

---

### §3.2 Cold-chain and transit condition monitoring

**1. Problem + magnitude.** Reefer gap **52,826 vehicles** (61,826 required vs
~9,000) `[H01]`; 10–20% of a consignment spoiling before retail in the local
deluge report `P2`; grape export chain cold-storage losses **12.13%** `P2`.

**2/3. Feasibility: [not feasible for a slow ground rover] — wrong machine
entirely.** Transit monitoring needs a **₹1,500–3,000 BLE/LoRa temperature-
humidity logger riding inside the crate or the reefer**, for the whole journey.
A rover is a field vehicle; it does not board a truck. There is no version of
this where a ₹27–50k mobile robot beats a matchbox-sized data logger. The DHT22
and thermal guardian exist for the rover's own health, not for cargo.

**4–6. Verdict: park.** Recorded because the reefer gap is genuinely one of the
largest numbers in this catalog `[H01]`, and it belongs to **somebody else's
product**. Saying so protects the credibility of §1.1's queue-discipline claim,
which is the adjacent idea that *does* work.

---

### §3.3 Spurious/substandard pesticide detection and spray-efficacy verification

**1. Problem + magnitude.** A threshold recommendation assumes the product in
the can matches the label; spurious pesticides are a documented Indian problem
`P21` (AGRI_PROBLEMS §3.10).

**2. Rover mechanism.** The rover cannot authenticate a chemical. But
**before/after CV on the same tagged plants** (`plant_db.py`) produces an
**efficacy record**: pest/lesion counts pre-treatment and 7–10 days
post-treatment. Systematic non-response across multiple plots using the same
batch is a **statistical signal** about that batch.

**3. Feasibility: [buildable now] for the paired-difference efficacy record;
[not feasible] for authenticating a product.** As in §1.7, paired differencing on
spatially matched plants is much more robust than absolute counting, because
biases cancel. But it inherits §4.1's detection accuracy floor entirely — if the
underlying pest detector is unreliable, the *difference* of two unreliable counts
is worse, not better. This entry is therefore **strictly downstream of §4.1
passing its gate**, and cannot be pursued before it.

**4. Value & who pays.** Interesting and honest: an efficacy record is a
**second-order audit artefact** and its natural buyer is whoever bears the cost
of a failed spray — the aggregator, or potentially an input company defending
its own brand against counterfeits. `P21` already grades the direct problem
**NOT SOLVABLE** with this as the indirect slice. No WTP evidence located.

**5. Proof gate.** Detector must first clear §4.1. Then: paired counts on ≥20
plot-treatment events, agronomist-adjudicated, with **≥80% agreement on
"responded / did not respond"**.

**6. Verdict: pilot later.** Dependent on §4.1; genuinely novel; unproven payer.

---

## §4. The crop-protection cluster — reconciled with the dossiers' stated limits

The existing dossiers set hard limits here, and this section **respects them
rather than relitigating them**. Its contribution is to separate the pest classes
by *whether the sensing can physically work*, which is a sharper cut than
"disease detection" as a single capability.

### §4.1 The base constraint: the PlantVillage domain gap

**This is not an opportunity; it is the ceiling every §4 entry sits under, and it
must be stated before any of them.**

Models trained on **PlantVillage** — which is exactly what
`pi/ai/disease_detection.py` loads, 38 classes, `plantvillage_labels.txt`
**[Repository fact]** — reach **>99% accuracy on same-distribution lab images**
but **collapse to 33–50% accuracy in real field conditions** `[H15]`
**[External result]**. The cause is domain shift: PlantVillage images are single
detached leaves on uniform backgrounds with controlled framing, so models overfit
to the studio setting rather than learning disease features. **Increasing model
complexity does not fix it**; only diverse, representative **field-acquired
training data** does `[H15]`.

**Consequences, stated plainly:**

1. **The shipped disease classifier's real-world accuracy is likely 33–50%**,
   not the notebook's headline number. A coin-flip-grade classifier driving a
   spray recommendation is a **liability**, not a feature.
2. `pi/ai/frame_capture.py` (active-learning hard-case capture) is therefore
   **the most strategically valuable module in the repository** — it is the only
   credible mechanism for closing the gap **[Repository fact]**.
3. The BOM's launch gate (**≥85% recall, ≥80% precision per class on held-out
   local fields**) is the right gate and is **~2× the accuracy the literature
   predicts from PlantVillage weights alone**. It is only reachable with locally
   collected, field-acquired, per-class-validated data.
4. **Every §4 entry below is gated on this**, and none may be sold before it
   passes. The rover's honest §4 role today is **evidence capture for a human
   expert**, not autonomous diagnosis — which is exactly what `P28` already says
   (**PARTIAL / ENABLER, not an extension-agent replacement**).

**Verdict: this is a mandatory prerequisite programme, not an opportunity.**

---

### §4.2 Grape downy and powdery mildew early detection (the bundled scouting mission)

**1. Problem + magnitude.** Downy mildew causes **30–100% loss** in Indian
grapes, with cluster and foliage destruction commonly **50–100%**; powdery mildew
severity in Maharashtra is reported at **11.56–38.22%**; Nashik trials use
**~4 foliar sprays per season** from first symptom `[H16]` **[External result]**.
Crop protection is the **2nd-largest single line item** in grape cost of
cultivation — **16.93% of Cost C in Sangli** `P3` **[External result]** — against
Cost C of ₹690,422/ha `[H10]`.

**2. Rover mechanism.** **Senses:** leaf undersides and canopy interior at
close range with the macro lens and ring light — the "oil spot" upper-surface
lesion and the white sporulation on the **underside** are the diagnostic downy
mildew signs, and powdery mildew shows as surface white colonies. **Computes:**
per-plant lesion presence/severity, geotagged, into a **block risk map** with
week-over-week progression from `plant_db.py`. **Output:** "first symptom
detected in block 7, row 12, on date X" → an agronomist-reviewed spray decision,
timed rather than calendared.

**3. Feasibility: [buildable now, conditional on §4.1] — one of the better
sensing cases.** Mildew lesions are **macroscopic, high-contrast surface
features** on leaves at rover height — genuinely within RGB reach, unlike thrips
or mites. `P24`'s analogous verdict (rust pustules, blight lesions) is
**SOLVABLE (detection wedge)** and applies. Two platform advantages are real
here: (i) a ground rover can image **leaf undersides**, which a drone
fundamentally cannot, and undersides are where downy mildew sporulation actually
appears; (ii) the ring light makes underside imaging in a shaded canopy
practical `[H14]`.

*Honest limits:* the class is **not in PlantVillage's 38** in a
field-representative form, so it needs local data collection from zero; early
lesions are small and easily confused with spray residue film, dust, sunburn and
nutrient flecking; and a **detection is not a spray decision** — `P3` explicitly
states early evidence "does not establish that localized spot treatment can
replace whole-canopy protection", and mildew control is genuinely a
**whole-canopy** job. So the output is **timing**, never spot-treatment
substitution.

**4. Value & who pays.** The value pool (16.93% of Cost C `P3`) is large and
already being spent — the right kind of target per §1's headroom logic. But
**the grower will not pay for the information** `[F01]`, `[G01]`. The payer is
again the **aggregator/exporter**, for whom mildew has a second edge: more
sprays late in the season means **more residue risk**, which ties directly to
§3.1's liability. **Fewer, better-timed sprays is simultaneously a cost story
and a residue-compliance story for the same buyer** — that coupling is what
makes this bundleable rather than standalone.

**5. Proof gate.** ≥85% recall / ≥80% precision per class on **held-out Nashik
vineyards** (the BOM gate); **detection ≥7 days before the grower's own
observation** on ≥10 outbreak events; and the commercial gate — **spray count
and residue-panel outcome vs a paired control block**, invoice-verified, never
modelled.

**6. Verdict: pursue now (bundled with §1.1, §1.2, §1.7, §3.1 on the same
vines).** This is the entry that supplies the **active days** the harvest
entries lack, and it shares the payer.

---

### §4.3 Fall armyworm, pink bollworm and other large-visible-symptom field pests

**1. Problem + magnitude.** Cotton **pink bollworm causes up to 30% yield loss**
in India, and the established ETLs are **8 moths/trap/night for 3 consecutive
nights, 10% rosette flower incidence, or 10% green boll damage** — with recent
research arguing for a **lower 4.5–5.7 moths/trap/night** threshold for earlier
intervention `[H17]` **[External result]**. Weeds and pests aside, cotton is also
the Yavatmal spray-poisoning belt: **50+ deaths, ~800–886 hospitalizations** in
2017 `P1`. FAW damage on maize whorls is at ideal ground-rover imaging height
`P23`.

**2. Rover mechanism.** **Senses:** (i) **pheromone trap faces** at the fiducial
dock under controlled light — counting moths on a trap is a **bounded,
high-contrast counting task**; (ii) **rosette flowers** and green-boll damage on
plants; (iii) FAW whorl damage. **Computes:** counts against the published ETLs.
**Output:** "**ETL crossed / not crossed**" on a named, official threshold.

**3. Feasibility: [buildable now, conditional on §4.1] — and note *why* this one
is unusually strong.** The decision is **a count against a published integer
threshold**, not a diagnosis. **8 moths on a trap. 10% rosette incidence.** These
are exactly the tasks where a detector with imperfect per-object accuracy still
produces a correct *decision*, because counting errors average out across a
sample and the threshold is far from zero. Compare this with §1.1's Brix, where
a 1.05 error straddles a 16.0 boundary. **The lesson generalizes: AgriRover is
strong when the agronomic decision is a count against a documented threshold,
and weak when it is a physicochemical measurement.** `P16`, `P23` support the
detection slice.

*Limits:* trap imaging requires **the same trap, pose and scale every visit** —
which is exactly BOM #19's purpose **[Repository fact]** — and the dossiers
correctly exclude thrips/mites as too small for drive-by RGB `[E27]`, `[E28]`.
This entry covers **large-bodied moths and macroscopic damage only**.

**4. Value & who pays.** Weakest payer in the pursue-tier. Cotton is a
**field crop with low per-acre value** and no export-residue liability chain
comparable to grapes; the grower won't pay `[F01]`; cotton FPOs are not
Sahyadri-class. The honest note: **this is where the health case is strongest
(`P1`) and the commercial case is weakest.** Subsidy/CSR/state-programme funding
(§12's SMAM/MahaDBT instruments `[G08]`, `[G16]`) is the only plausible payer,
which makes it a grant-funded track, not a commercial one.

**5. Proof gate.** Trap moth count vs manual count: **±15% at ETL-relevant
densities**; ETL-crossing agreement with an entomologist on ≥30 trap-weeks:
**≥90%**; rosette incidence estimate: **±5 percentage points** on a 10%
threshold.

**6. Verdict: pilot later.** Excellent feasibility, real magnitude, weak payer.
Pursue only if a public-programme or CSR funder appears.

---

### §4.4 Weed mapping and spot herbicide application

**1. Problem + magnitude.** Weeds cost India an estimated **USD 11 billion/year
across ten major crops** (ICAR-DWR and others), with **cotton yield losses of
40–85%** from weed competition during early growth `[H18]` **[External result]**,
`P5`.

**2. Rover mechanism.** Existing `weed_detection.py` (YOLOv8n, crop-vs-weed
classes, `IGNORE_LABELS` so the sprayer fires only on `weed`) → pan/tilt nozzle
(`spray_targeting.py`) → relay pump micro-dose. Output: a geotagged weed-patch
map plus targeted herbicide instead of blanket spray. **[Repository fact]**

**3. Feasibility: [buildable now] technically; throughput-limited commercially.**
Weeds are ground-level, large and high-contrast — the easiest RGB target in the
catalog — and the full detect-to-spray chain already exists in code. **The
binding constraint is not vision, it is physics:** weeding requires **full-area
coverage**, not sentinel sampling, and at ~0.3 m/s an under-canopy platform
covers **~0.4 acre/hour fully traversed** `[G26]`. A one-acre weeding pass is
therefore a ~2.5-hour job before travel. Meanwhile **Niqo Robotics does AI
spot-spray at ₹300–500/acre** `[F04]`, `[G18]`, and drone spraying runs
**₹400–800/acre at 40–60 acres/day** `[E19]`.

**4. Value & who pays.** **This is the clearest case of the "squeezed from both
sides" problem** `[F04]`, `[G18]`. AgriRover's cost per acre-pass is **₹387
(dense) to ₹1,599 (very sparse)** §11.3 for a *scouting* pass; a competitor
**sprays** for ₹300–500. There is **no density at which AgriRover both operates
well and prices competitively** §11.3 conclusion 2. Weeding is a full-coverage,
throughput-bound task, i.e. the task type this platform is worst at.

**5. Proof gate.** Only meaningful gate: **acres/hour of fully-traversed
weeding at ≥90% weed-strike rate and ≤10% crop-strike rate**, compared directly
against a Niqo-class quote. **[AgriRover target]** — expect to lose.

**6. Verdict: park as a commercial offering; retain as a free by-product.** Weed
maps generated during passes made for §3.1/§4.2 reasons cost nothing extra and
add report value. Do not sell a weeding pass.

---

### §4.5 Sucking pests (thrips, mites, whitefly, jassids)

**1. Problem + magnitude.** Thrips are the primary reason for cosmetic
downgrading of export grapes and a major driver of spray frequency; mites and
whitefly are chronic in cotton and vegetables.

**2/3. Feasibility: [not feasible for a slow ground rover].** Adult thrips are
**~1–2 mm** and mites smaller still. Resolving them requires macro optics at a
few centimetres standoff with the insect **in the plane of focus** — which is
static microscopy, not a drive-by pass from a moving platform. The dossiers
already exclude this class explicitly `[E27]`, `[E28]`, and that exclusion is
correct on optics alone, independent of any model quality. The **damage
symptoms** (silvering, scarring, leaf curl) are visible, but they appear
**after** the cosmetic downgrade has already occurred, so detection carries no
decision value for the export grade it was meant to protect.

**4–5.** No payer, no gate.

**6. Verdict: park.** Recorded to fix the boundary of §4.2/§4.3: **AgriRover can
see mildew colonies and moths; it cannot see thrips.** Stating the boundary
precisely is what makes the positive claims credible.

---

### §4.6 Nematodes, soil-borne disease and root-zone pathogens

**1. Problem + magnitude.** Root-knot nematode and soil-borne wilt are
persistent, yield-limiting and effectively invisible until severe.

**2/3. Feasibility: [not feasible].** The pathogen and its damage are
**below ground**. Above-ground symptoms (stunting, patchy vigour) are
non-specific — indistinguishable from water stress, salinity or nutrient
problems — so a detection cannot be attributed to a cause, and an unattributed
detection is not actionable. Diagnosis requires soil/root sampling and lab
assay.

**4–6. Verdict: park.** No sensor on this platform, at any price, reaches the
root zone.

---

## §5. Labour, mechanization and the "who does the walking" cluster

### §5.1 Replacing manual scouting labour on large aggregated acreage

**1. Problem + magnitude.** **34 million workers left Indian agriculture**
between 2004-05 and 2011-12, and labour scarcity documentably **shifts operations
off their agronomic optimum** `P9` **[External result]**. Hired labour is
**16.9% of Nashik grape Cost C** (~₹117,000/ha) `[H10]`. An aggregator with
30,000+ farmers `[G11]` cannot physically send an agronomist to every plot
weekly; scouting is rationed, so problems are found late.

**2. Rover mechanism.** This is not a new sensing capability — it is the
**framing** under which §1.2, §1.7, §3.1 and §4.2 are all one product: a machine
that **walks the rows so a human does not have to**, capturing a consistent,
geotagged, timestamped record on every plant, every week.

**3. Feasibility: [buildable now] for the capture; the economics are the open
question.** Coverage is the constraint: **~0.4 acre/hour** fully traversed at
~0.3 m/s `[G26]`, with sentinel sampling covering far more ground per hour than
full traversal. **The rover does not replace an agronomist's judgement — it
replaces the agronomist's walking**, feeding a review desk priced at
**₹43–₹1,730/pass** depending on utilisation §11.5.

**4. Value & who pays.** The aggregator, and this is the **honest core of the
whole business case**: the buyer is not purchasing robotics, they are purchasing
**scouting coverage they currently cannot staff**. This reframing matters because
it changes the benchmark from "₹300–500/acre Niqo spray" `[F04]` — which
AgriRover loses — to "**the cost of an agronomist visit**", which is a much
higher number and which the aggregator is **already paying** `[G01]`'s existing-
spend test. It is also the only framing in which §11.3's ₹387/acre-pass dense
figure looks cheap rather than expensive.

**5. Proof gate.** The decisive commercial experiment for the entire programme:
**agronomist-visits-displaced per rover-week**, measured, plus whether the
aggregator's field-ops budget line actually moves. Threshold: rover cost/plot/
season **< current scouting cost/plot/season** at the same or better problem-
detection latency. **[AgriRover target]**

**6. Verdict: pursue now — as the commercial framing for the bundle, not as a
separate feature.** Nothing new is built; this is how §1.2 + §1.7 + §3.1 + §4.2
should be *sold*.

---

### §5.2 Market price intelligence and mandi timing

**1. Problem + magnitude.** Large — farmer's share of consumer rupee is
**33–35%** for tomato/grape **[External result]**, and the 2023 Kolar collapse
(₹2,300 → ₹45–120 per 15 kg box) was a **pure market-timing failure with the
lowest post-harvest losses in the country** `P8`.

**2/3. Feasibility: [not feasible for a rover] — wrong machine, again.** Price
data comes from Agmarknet/eNAM APIs and a mobile phone. A rover contributes
**nothing** to it; there is no sensing content in a mandi price.

**4–6. Verdict: park.** Recorded because it is the largest *farmer-felt*
problem in this entire catalog and the rover is **completely irrelevant** to it.
That asymmetry is worth stating out loud at Baramati: it is the clearest evidence
that "biggest problem" and "problem this machine can address" are different
lists — which is the discipline this document exists to enforce.

---

## §6. Synthesis

### §6.1 The decision rule that emerged

Sorting twenty-plus candidate problems produced one rule that predicted the
grade better than crop, cluster or magnitude:

> **AgriRover is credible when the agronomic decision is a COUNT or a LENGTH
> compared against a documented threshold. It is not credible when the decision
> is a PHYSICOCHEMICAL QUANTITY.**

The evidence for the rule is internal to this catalog:

| Decision type | Entry | Native sensor output | Grade |
|---|---|---|---|
| Count vs integer threshold | §4.3 — 8 moths/trap, 10% rosette | count | **buildable** |
| Count vs count (paired) | §1.7 — berries removed by thinning | count delta | **buildable** |
| Count → forecast | §1.2 — flowers per vine | count | **buildable** |
| **Length vs banded standard** | §1.4 — banana caliper 46–50 mm | **millimetres** | **buildable (cleanest)** |
| Presence vs absence | §4.2 — mildew lesion present | detection | **buildable (post-§4.1)** |
| Timestamped act performed | §3.1 — spray record + PHI clock | metadata | **buildable (no CV needed)** |
| **Sugar concentration** | §1.1a — 16 °Brix pass/fail | skin reflectance | **NOT feasible** |
| **Three chemical species** | §2.2 — soil N, P, K | bulk EC | **NOT feasible** |
| Canopy water potential | §2.1 — irrigate or not | visible wilt (late) | **needs thermal** |

The two hard failures (§1.1a, §2.2) are both **"infer chemistry from a cheap
electrical or optical proxy"**. Both have the same signature: a credible-looking
number, produced by a sensor that does not measure the quantity, feeding a
decision with a sharp threshold. **That signature is the thing to refuse.**

### §6.2 Ranked shortlist

**Ranking criterion: (payer proven) × (feasibility on current BOM) × (fit with
route-density and active-days constraints).** Magnitude of the problem is
deliberately *not* the primary axis — §5.2 and §3.2 have the largest numbers and
the lowest scores.

| Rank | Entry | Feasibility | Payer | Why it ranks here |
|---|---|---|---|---|
| **1** | **§3.1** Residue/PHI audit artefact | buildable, no new CV | **Proven** (exporter/FPO, liable party `[G15]`) | Only entry whose payer prior research already validated. Least robot-dependent — hence the necessity test. |
| **2** | **§1.2** Pre-bloom count → volume forecast | buildable, R²>0.90 `[H08]` | Strong (procurement desk) | Only entry where the literature explicitly endorses **this platform's** night-plus-controlled-light configuration `[H08]`, `[H14]`. |
| **3** | **§4.2** Mildew early detection | buildable **after §4.1** | Strong (same buyer; cost + residue coupling) | Supplies the **active days** §1.1 lacks; 16.93% of Cost C `P3`. Hard-gated on §4.1. |
| **4** | **§1.7** Thinning verification | buildable (paired diff) | Plausible (₹117k/ha labour bill `[H10]`) | Same product shape as §3.1 — a verified physical act `[G19]`. No new hardware. |
| **5** | **§1.1** Sampling allocator + crate forecast | buildable **only as restructured** | Strong, but seasonal | Survives only as queue discipline; **Brix claim deleted**. Fails active-days alone. |
| **6** | **§5.1** Scouting-labour displacement | buildable | **The framing for 1–5** | Not a feature; the correct **benchmark** (agronomist cost, not Niqo's ₹300–500). |
| 7 | §1.3 Salvage cut-order | buildable (bundled) | Unproven (insurer?) | Free on top of 2+5; emotive; payer unproven. |
| 8 | §1.4 Banana caliper | **best physics** | Plausible | New crop/district/buyer. Port after grape proves. |
| 9 | §3.3 Spray-efficacy record | post-§4.1 | Unproven | Novel; strictly downstream of §4.1. |
| 10 | §4.3 Pink bollworm / FAW ETL | buildable | **Weak (grant only)** | Best health case `P1`, worst commercial case. |
| — | **§1.5, §1.6, §2.1, §2.2, §2.3, §3.2, §4.4, §4.5, §4.6, §5.2** | **park** | none | See §6.3. |

### §6.3 The kill list — and why saying it matters

| Entry | Killed by | One-line reason |
|---|---|---|
| §1.1a Brix/ripeness index | `[H06]`, `[H07]` | Field MAE 1.05 °Brix straddles a 16.0 threshold; **acidity has no RGB correlate at all**. A ₹500 refractometer is better. |
| §2.2 NPK prescription maps | `[H12]` | Probe reports **EC × factory constant**, not N/P/K. `prescription_map.py` is a valid pipeline on an invalid input. |
| §1.5 Onion/tomato lot screening | `P4`, throughput | Conveyor + line-scan camera wins; decisive losses are **internal**, invisible to surface RGB. |
| §1.6 Mango | `P13` | Fruit is in the overhead crown; a ground rover cannot see it. |
| §2.1 Irrigation | `[F05]`, `[H11]` | A ₹6,000 buried probe beats a ₹27k mobile one for a slow state variable; real stress sensing needs thermal. |
| §2.3 pH / compaction | physics | ISE needs buffers; penetrometer needs reaction mass a 25 kg platform lacks. |
| §3.2 Cold-chain transit | wrong machine | A ₹1,500 logger rides in the crate. The rover does not board trucks. |
| §4.4 Weeding as a service | `[F04]`, `[G18]`, `[G26]` | Niqo **sprays** for ₹300–500/acre; AgriRover **scouts** for ₹387–1,599. Full-coverage task, throughput-bound platform. |
| §4.5 Thrips/mites | `[E27]`, `[E28]`, optics | 1–2 mm targets need static macro, not a drive-by pass. |
| §4.6 Nematodes | physics | Below ground; above-ground symptoms non-specific. |
| §5.2 Market prices | wrong machine | Largest farmer-felt problem; **zero** rover relevance. |

**These eleven are the document's main contribution.** Each is a direction that
looks fundable in a slide deck and fails on physics, throughput or competition.

### §6.4 The recommended bundle

No entry survives alone. §1.1 fails the **≥100 active days/year** gate `[G13]`;
§3.1 does not need a robot; §4.2 is gated on §4.1. Bundled on **the same
Sahyadri-class vineyard acreage, same season, same payer**, they cover the
calendar:

| Window | Mission | Entry |
|---|---|---|
| Pre-bloom → fruit set | flower/cluster counts (night, ring light) | §1.2 |
| Thinning window | before/after berry-removal verification | §1.7 |
| Whole season, every pass | spray record, PHI clock, geotagged evidence | §3.1 |
| Whole season, every pass | mildew scouting (undersides) | §4.2 |
| Pre-harvest 4–8 weeks | sampling allocation, crate forecast, cut order | §1.1, §1.3 |
| Free by-products | weed map, soil moisture/salinity trend | §4.4, §2.1 |

Sold as **§5.1: contracted scouting coverage the aggregator cannot staff** —
benchmarked against agronomist visit cost, not against Niqo's spray price.

### §6.5 Named research gaps

1. **The NPK lab correlation (§2.2) — highest priority.** Split-sample vs an
   NABL lab. `[H12]` predicts failure; until it is run, `prescription_map.py`
   should stay feature-flagged off.
2. **Route density on aggregator acreage.** §11.4's survey `[G04]` has never been
   run on Sahyadri-class contiguous plots, where the ₹387 dense figure — the only
   one that closes — might actually hold.
3. **Indian trellis occlusion.** All bunch/flower CV results `[H04]`, `[H05]`,
   `[H08]` come from VSP canopies. Y-trellis and flat bower are denser. **Unknown
   transfer.**
4. **Insurer WTP for pre-event condition records (§1.3).** A distinct payer
   hypothesis with zero evidence located.
5. **Banana bunch bagging (§1.4).** If export bunches are bagged, caliper
   measurement is occluded and the entry dies. Survey before building.
6. **The §3.1 necessity test.** Phone + agronomist vs rover. If the phone
   matches, sell the phone workflow.
7. **Aggregator scouting cost baseline (§5.1).** The denominator of the entire
   business case is currently unknown.

### §6.6 New evidence tags introduced

| Tag | Claim | Source |
|---|---|---|
| `[H01]` | Pack-houses 70,080 required vs 249 created; reefers 61,826 vs ~9,000 | NCCD demand-driven gap assessment, as reported |
| `[H02]` | 395 lakh MT cold storage, 8,698 facilities (May 2024); bulk gap ~10% | Govt./NCCD capacity reporting |
| `[H03]` | Grape exports 2024-25: 271,253 MT ≈ ₹3,050 crore | APEDA/trade reporting |
| `[H04]` | Multi-view raises tracked bunch ratio 23% → 74%; motion blur and ID-matching unsolved | Vineyard yield-estimation literature |
| `[H05]` | YOLOv11 cluster detection 94.3% precision; ~5–7% yield-mass error | Grape detection literature |
| `[H06]` | Brix from RGB: lab RMSE 0.78; field MAE 1.05; field RMSE up to 4.63; hyperspectral 0.25–1.27 | Non-destructive TSS estimation literature |
| `[H07]` | EU table grape maturity: min 16 °Brix, or 20:1 (12.5–14) / 18:1 (14–16) sugar:acid | EU/Codex table grape standard |
| `[H08]` | Grapevine flower counting R² > 0.90; daylight pre-bloom unreliable; **night + artificial light significantly better** | Early yield prediction literature |
| `[H09]` | Banana PHL 20–30%; Jalgaon 6.81% farm + 3.90% transport + 14.12% retail; export at 75–80% maturity; caliper bands e.g. 46–50 mm | Banana post-harvest/grading literature |
| `[H10]` | Nashik grape Cost C ₹690,422/ha; hired labour 16.9% | Grape cost-of-cultivation study |
| `[H11]` | RGB detects water stress only via visible colour change, less accurate than thermal; CWSI itself prone to late detection | Water-stress sensing review |
| `[H12]` | 7-in-1 NPK sensors measure EC × fixed factor; poor lab correlation; K worst; qualitative trends only | Low-cost NPK sensor validation |
| `[H13]` | RASFF 2025: India highest, 124 pesticide notifications | RASFF reporting (corroborates `[F17]`) |
| `[H14]` | Controlled artificial lighting improves field detection stability | Field imaging literature |
| `[H15]` | PlantVillage models >99% lab → **33–50% field**; complexity does not fix domain shift | Domain-generalization studies |
| `[H16]` | Grape downy mildew 30–100% loss (50–100% typical on clusters); powdery 11.56–38.22% Maharashtra; ~4 sprays/season Nashik trials | Indian grape pathology literature |
| `[H17]` | Pink bollworm up to 30% loss; ETL 8 moths/trap/night ×3, 10% rosette, 10% boll damage; proposed 4.5–5.7 | Cotton IPM literature |
| `[H18]` | Weeds ~USD 11 bn/yr across ten crops; cotton 40–85% early-growth loss | ICAR-DWR and weed-science literature |

### §6.7 What this catalog does not do

It does not produce a rupee-per-acre benefit figure for any entry. Every attempt
to do so required multiplying a national loss percentage by a national crop value
and then by an **unmeasured** "addressable fraction" — the third term does not
exist in any source located, and inventing it is the exact failure mode the
earlier dossiers were written to stop. **The proof gates in each entry are the
substitute: measure the fraction, then compute the value.** Until a gate is
passed, the honest answer to "what is it worth?" is *"we have a method to find
out and a threshold we have agreed to respect."*
