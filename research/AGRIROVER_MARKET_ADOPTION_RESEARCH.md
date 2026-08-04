# AgriRover Market Adoption and Farmer-Profit Research

**Decision dossier | 04-Aug-2026**

> Purpose: determine what AgriRover must do for farmers to pay for it repeatedly,
> what can be claimed today, and what must be proved in a field pilot. This
> document is deliberately stricter than the pitch deck.

## Evidence labels

- **External result:** measured by another organization or study. It validates a
  problem or mechanism, not AgriRover's performance.
- **Repository fact:** present in the current code, BOM, or design documents. It
  is not proof that the physical rover works in a field.
- **Analyst scenario:** a transparent calculation used for a decision. It is not
  a forecast or measured result.
- **AgriRover target:** a gate the product must pass before the claim is used.

No AgriRover field saving, yield increase, model accuracy, coverage rate,
reliability, willingness-to-pay, or payback result exists yet.

---

## 1. Commercial decision

### Recommended first market

Run the first paid-intent pilot as a **tomato crop-protection surveillance and
verification service in the Narayangaon/Junnar cluster**. Use KVK Narayangaon
for local agronomy and recruit a tomato-oriented FPO as route aggregator. KVK
Baramati/CoE Vegetables remains a strong controlled-development site, but it is
not yet evidence of commercial route density. [E16] [E25] [E29] [E30]

The service is:

> **Run a weekly, repeatable sentinel sample and trap read -> count and geotag
> suspected problems -> compare with an economic threshold -> trigger a full-row
> scan only when risk justifies it -> send an agronomist-reviewed action ->
> record treatment and pre-harvest interval -> revisit and verify the outcome.**

It is not, initially, a universal farm robot or a full-field sprayer.

### Why this is the strongest wedge

1. Maharashtra tomato has enough geographic concentration for an operating
   test. In 2023-24 Nashik reported 22,040 ha, Pune 4,772 ha, Ahmednagar 4,324 ha
   and Solapur 4,072 ha. Narayangaon is a nationally significant tomato auction
   market with several publicly listed producer companies in Junnar. [E25] [E29]
2. Maharashtra tomato growers have a documented Rs 17,000 per acre plant-
   protection budget: Rs 15,000 chemicals plus Rs 2,000 application, within an
   illustrative total cultivation cost of Rs 127,300 per acre. [E02]
3. Official tomato IPM guidance calls for weekly observations and gives concrete
   sampling units for fruit borer, leaf miner, whitefly, mites, thrips, diseases
   and pheromone traps. HORTSAP already includes tomato, so AgriRover can supply
   systematic field evidence into an existing expert-advisory workflow. [E24]
   [E26]
4. Chilli has the clearest savings benchmark: 19 versus 29.2 sprays and
   Rs 25,930 versus Rs 51,090 per acre for pesticide plus application under a
   complete IPM demonstration. [E01] However, its key thrips and mites are too
   small for a normal drive-by camera and require terminal-leaf, tapping, flower
   or sticky-trap observations. The invasive Thrips parvispinus makes an old
   generic image classifier especially unsafe. [E27] [E28]
5. KVK Narayangaon is inside the Junnar production belt and has an on-farm-
   testing and technology-transfer mandate. KVK Baramati's CoE can provide
   controlled tomato/chilli material and protected-cultivation facilities.
   [E16] [E30]
6. The business can be sold as a seasonal service through an FPO, avoiding a
   farmer capital purchase and concentrating fields enough to control transport
   cost.

### Launch order

1. **Tomato:** first operational and paid-intent pilot; best combination of
   observable classes, official surveillance workflow and verified route density.
2. **Chilli:** second, only after adding a macro leaf/flower or trap-reading
   workflow and identifying a genuine chilli FPO cluster.
3. **Grapes:** scouting, treatment records, PHI and traceability; do not promise
   spot-fungicide savings.
4. **Cotton:** second-stage trap/scouting service after throughput, ruggedness
   and local models are proved.
5. **Maize:** later; acreage is large but value per acre and service headroom are
   weaker.

---

## 2. The outcome farmers would buy

Farmers do not need another dashboard or disease label. They need a decision
that changes profit. Each paid visit should produce five auditable outputs:

1. **Problem count and map:** affected plants, rows or traps, each with an image.
2. **Threshold decision:** act now, watch, or no treatment, with the threshold
   source and confidence shown.
3. **Treatment record:** product, active ingredient, rate, water, plot, date,
   operator and pre-harvest interval. A qualified agronomist remains responsible
   for the recommendation.
4. **Verification visit:** whether pest pressure or disease severity fell after
   action.
5. **Profit report:** actual treatment and labour cost against the farmer's own
   baseline, plus yield and grade at harvest. No generic litres-times-price
   estimate.

The farmer-facing message can remain simple and local-language, but the evidence
behind it must be inspectable by the FPO, KVK or buyer.

### Proposed service names and packages

| Offer | Included | Initial price hypothesis | Status |
|---|---|---:|---|
| Tomato Sentinel Season | 8 weekly fixed-point samples, pheromone/sticky-trap reads, ETL trend, treatment log and verification | Rs 3,600-4,400/acre/season, excluding triggered deep scans | Test only |
| Triggered Tomato Deep Scan | Full-row evidence map after a sentinel alert or unexplained symptom | Rs 800-1,000/acre/pass | Test only |
| Chilli Macro Sentinel Season | Weekly terminal-leaf/flower or trap sampling, fruit-damage count, ETL trend and treatment log | Price only after macro workflow and cluster are proved | Discovery |
| Vineyard Compliance Scout | scouting, plot map, spray/PHI records, export checklist support | Price through exporter interviews | Discovery |
| Cotton Trap + Field Scout | pheromone-trap reading, hotspot map, ETL alert | Price after throughput proof | Later |

The ranges are not published market prices. They are test cells derived from
provider break-even and farmer value headroom. The sentinel package is a new
operating hypothesis: NIPHM calls for weekly scouting, while repeated full-row
scans are unaffordable at current throughput. [E26]

### 2.1 Adoption interface: voice, proof and callback

The strongest Indian evidence for a farmer-facing advisory interface is not a
complex dashboard. A three-year randomized evaluation of Odisha's Ama Krushi
two-way voice service enrolled 13,675 rice farmers. Among surveyed farmers,
94% in year one and 85% in year two accessed content, but farmers listened to
the majority of only about 10 calls per season, roughly one-quarter of the
messages sent. Access raised mean yield by 1.7% and total harvest by 4.1%; the
average profit effect was not statistically significant. It reduced the
probability of severe crop loss by 10%, with a 26% reduction in losses attributed
to pests and diseases. The estimated 12:1-19:1 benefit-cost ratio depended on
delivery at multi-million-user scale. [E33]

This is evidence that timely local-language advice can change behaviour. It is
not evidence that a farmer will pay AgriRover's price, that a tomato result will
match a rice result, or that a dashboard creates value. Product consequences:

1. deliver a short Marathi voice message plus an image-backed `ACT`, `WATCH` or
   `NO TREATMENT` card;
2. expose a callback to the reviewing agronomist/FPO crop adviser;
3. record whether the message was heard, understood and acted on;
4. keep the detailed evidence report for the FPO, KVK and buyer; and
5. test paid continuation explicitly, because free-service usage is not
   willingness to pay.

---

## 3. Farmer economics

### 3.1 Chilli: strongest profit case

**External result, not AgriRover:** ICAR-NRIIPM's 2023-24 chilli IPM result
contains a complete bundle of IPM practices, training and correct treatment. The
rover cannot claim the whole benefit. It can attempt to make the scouting,
threshold and verification parts cheaper and more consistent. [E01]

| Per acre | IPM | Farmer practice | Difference |
|---|---:|---:|---:|
| Number of sprays | 19.0 | 29.2 | 10.2 fewer |
| Pesticide + spraying cost | Rs 25,930 | Rs 51,090 | Rs 25,160 lower |
| Total cultivation cost | Rs 159,480 | Rs 181,390 | Rs 21,910 lower |
| Gross return | Rs 395,500 | Rs 374,750 | Rs 20,750 higher |
| Net return, calculated | Rs 236,020 | Rs 193,360 | Rs 42,660 higher |
| Benefit-cost ratio | 2.48 | 2.07 | 0.41 higher |

For a six-pass package at **Rs 4,800/acre**, farmer break-even requires the
service to capture either:

- 19.1% of the Rs 25,160 pesticide-and-spraying cost gap; or
- 11.3% of the Rs 42,660 complete IPM net-return gap.

The first is the safer sales test because it does not rely on a yield increase.

| Share of direct cost gap captured | Farmer gross benefit | Net after Rs 4,800 fee |
|---:|---:|---:|
| 10% | Rs 2,516 | -Rs 2,284 |
| 15% | Rs 3,774 | -Rs 1,026 |
| 20% | Rs 5,032 | Rs 232 |
| 30% | Rs 7,548 | Rs 2,748 |

**Commercial gate:** demonstrate at least 20% capture of this direct cost gap,
with no reduction in marketable yield or grade. At that point the farmer margin
is still only Rs 232/acre, so a higher capture or a lower delivered price is
needed before presenting the offer as robustly profitable.

### 3.2 Tomato: good fit, narrower savings headroom

The GIZ/Maharashtra manual gives an illustrative plant-protection budget of
Rs 17,000/acre, consisting of Rs 15,000 chemicals and Rs 2,000 application.
[E02]

A current external benchmark shows why better tomato IPM can be valuable.
ICAR-NRIIPM's 2024 farmer-participatory program at Annamayya, Andhra Pradesh,
reported **7.33 versus 18.66 sprays**, **15.8% lower cultivation cost**,
**23.13 versus 21.84 tonnes/acre yield**, and **Rs 2.25 lakh versus Rs 1.35 lakh
net return** for IPM versus farmer practice. In a separate Bulandshahr trial,
the tested IPM tomato samples were below detectable pesticide-residue limits,
while farmer-practice samples contained four detected fungicide/insecticide
residues. [E32]

That result is an upper benchmark for a complete program, not an AgriRover
forecast. The IPM bundle included seed and soil biocontrol, barrier and trap
crops, 10-12 traps/acre, parasitoids, farmer field schools and need-based
label-claim pesticides. Robotic surveillance is only one possible enabler.
The pilot must isolate whether its evidence changes a treatment, cost, yield or
grade outcome beyond expert-led IPM without the rover.

For the floor **Rs 3,600/acre** sentinel package, savings-only break-even requires
a 21.2% reduction in that budget before any triggered deep-scan fee.

| Share of protection budget avoided | Farmer gross benefit | Net after Rs 3,600 fee |
|---:|---:|---:|
| 10% | Rs 1,700 | -Rs 1,900 |
| 15% | Rs 2,550 | -Rs 1,050 |
| 20% | Rs 3,400 | -Rs 200 |
| 30% | Rs 5,100 | Rs 1,500 |

This is viable only if the pilot proves that rover-assisted threshold decisions
actually remove or improve treatments. Disease identification by itself has no
bankable value.

### 3.3 Cotton: validated IPM value, weaker v1 product fit

At Jalna, Maharashtra, an ICAR-NRIIPM cotton IPM program reported 2.95 versus
5.87 sprays, 17.62 versus 12.60 q/ha yield, and Rs 69,233 versus Rs 39,707/ha
net profit. The Rs 29,526/ha advantage is about Rs 11,948/acre. [E03]

This validates the value of weekly scouting, ETL decisions and IPM. It does not
validate AgriRover detection: pink bollworm larvae feed inside bolls, the
program used pheromone traps and several non-robot interventions, and cotton
acreage demands much higher throughput.

### 3.4 Grapes: high spend but the wrong spray promise

Sangli grape plant protection cost was Rs 190,491/ha, or about Rs 77,090/acre,
and 16.93% of cultivation cost. [E04] APEDA's current grape procedure says the
normal high-volume spray basis is 1,000 L/ha and requires the recommended active
ingredient per hectare to be maintained for efficacy and residue control. [E05]

Therefore:

- high value and repeated disease pressure make grapes attractive for scouting;
- APEDA already requires plot-level chemical, quantity, water, time, operator
  and PHI records, making traceability a real workflow; [E06]
- but localized visible lesions do not prove the rest of a grape canopy is safe
  to leave untreated, especially for fast-spreading fungal disease;
- the 500 ml rover tank cannot replace a normal vineyard spray operation.

Sell compliance and scouting only after exporter interviews. Do not infer a
percentage fungicide saving from the crop-protection budget.

---

## 4. Weighted launch-crop ranking

This is an **analyst decision matrix**, not survey data. Scores are 1-5. The
weights force the decision to favor measurable farmer profit and present
hardware fit over impressive acreage.

| Criterion | Weight |
|---|---:|
| Profit at risk and input-spend headroom | 20% |
| Visible/accessible problem and row geometry | 20% |
| Validated monitoring/IPM lever | 15% |
| Need for repeated service | 10% |
| One-season proof of value | 15% |
| Cluster and partner density | 10% |
| Compliance/data value | 5% |
| Competitive whitespace | 5% |

Component scores below are 1-5 in the same order as the criteria above. The
weighted total is `sum(score / 5 x criterion weight)`.

| Crop | Headroom | Observable fit | IPM lever | Repeat need | One-season proof | Cluster | Compliance | Whitespace | Weighted | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Tomato | 4 | 4 | 5 | 5 | 5 | 5 | 2 | 4 | **88/100** | First pilot; strongest combined hardware, system and cluster fit |
| Chilli | 5 | 2 | 5 | 5 | 4 | 3 | 2 | 4 | **77/100** | Second; strong value but requires macro sampling and a verified cluster |
| Grapes | 5 | 2 | 3 | 5 | 2 | 5 | 5 | 3 | **71/100** | Compliance discovery; do not sell fungicide reduction |
| Cotton | 3 | 2 | 5 | 4 | 4 | 5 | 1 | 3 | **69/100** | Later trap service; concealed pink bollworm limits rover vision |
| Maize | 2 | 4 | 4 | 3 | 3 | 4 | 1 | 3 | **63/100** | Later; accessible damage but lower value density |

The practical recommendation remains one **vegetable protection platform** with
separate crop models and agronomy protocols. Chilli should not inherit tomato
model claims or sampling hardware.

### 4.1 Observable launch classes and sensing gates

The product should be trained around observations that correspond to an
accepted sampling unit, not around every label available in a public image
dataset. Numeric thresholds below are protocol candidates for KVK approval, not
automatic spray commands. [E26] [E27] [E31]

| Crop/observation | Decision unit in guidance | Viable collection method | V1 status |
|---|---|---|---|
| Tomato fruit borer | Eggs/15 plants, larva/plant or percent fruit infestation; official schedule lists 8 eggs/15 plants, 1 larva/plant or 2% fruit infestation | Sentinel fruit/plant sample plus triggered side-view row scan and pheromone trap | **Launch candidate** after local recall test |
| Tomato serpentine leaf miner | Live mines on sampled leaves | Controlled close leaf image at fixed sentinel plants | **Launch candidate**; trend/advisory, not unsourced ETL |
| Tomato Helicoverpa/Spodoptera trap catch | Moths per fixed pheromone trap over time | Fixed-height trap ID plus close, well-lit image and manual correction | **Launch candidate**; strongest repeatable count |
| Tomato wilt, leaf curl and blight-like symptoms | Affected plants/leaves and disease incidence/severity | Geotag symptomatic plants and close images; expert differentiates disease, nutrient, chemical and weather lookalikes | **Alert candidate**, never autonomous diagnosis/dose |
| Tomato whitefly, thrips and mites | Nymph/adult counts on selected leaves; mites and whitefly often occur on leaf undersides | Macro leaf image, tapping sample or sticky trap, not a normal moving wide-angle camera | **Hardware gate** |
| Chilli fruit borer | 1 larva/plant or 1 damaged fruit/plant in the ICAR folder | Fruit/plant sample and pheromone trap | **Second-crop candidate** |
| Chilli thrips, yellow mite and whitefly | 2 thrips/leaf, 1 yellow mite/leaf and 4-5 whiteflies/leaf in the ICAR folder | Terminal-leaf/underside macro image, tapping and trap capture | **Paid-launch blocker** until count agreement passes |
| Invasive chilli Thrips parvispinus | Reproductive-part infestation; current official management guidance supersedes a generic legacy-class assumption | Flower/fruit macro sample with expert species confirmation | **Research only** [E28] |

Minimum useful sensing stack for this workflow:

1. forward row/navigation camera separated from agronomic evidence capture;
2. side/downward high-resolution camera with controlled standoff and lighting;
3. macro/trap capture station with scale reference and a manual correction UI;
4. odometry, row/plant IDs and coarse GPS for repeat visits; and
5. explicit "unobservable/not sampled" states so absence is never inferred from
   a camera angle that could not see the pest.

Multispectral stress or generic leaf classification may support discovery later,
but neither is a launch-critical decision class.

---

## 5. Service-provider economics

### 5.1 Fully loaded daily-cost scenario

The current deck's Rs 300/acre price must be tested against measured productive
coverage. The following values are analyst assumptions except the operator wage.

| Cost per active rover-day | Rs | Basis |
|---|---:|---|
| Operator | 582 | Maharashtra male plant-protection wage, Jan 2026, Labour Bureau [E17] |
| Local transport and mobilization | 250 | Analyst assumption; validate in pilot |
| Charging, data and cleaning | 40 | Analyst assumption |
| Maintenance reserve | 80 | Analyst assumption |
| Rs 50,000 asset recovery | 167 | 3 years x 100 active days/year |
| **Direct rover-day total** | **1,119/day** | Rounded; excludes chemical and per-report support |

The direct total is still favorable to AgriRover because it excludes agronomist
review, booking/sales, software, payment collection, insurance and central
support. Until actual review minutes and overhead are measured, use a separate
per-acre-pass support allowance:

| Support case | Rs/pass | Interpretation |
|---|---:|---|
| Lean | 100 | Exception-only agronomy and highly efficient cluster administration |
| Planning | 200 | Working allowance for agronomy plus commercial/technical overhead |
| Stressed | 300 | Longer expert review, corrections or low route density |

These are sensitivities, not observed costs. The pilot must time every review
and allocate actual payroll and overhead before setting a sustainable price.

### 5.2 Rs 300/acre fails more decisively at the current wage

| Productive deep-scan coverage | Revenue/day at Rs 300 | Direct margin/day | Direct break-even/pass | Break-even with Rs 200 support |
|---:|---:|---:|---:|---:|
| 0.5 acre/day | Rs 150 | -Rs 969 | Rs 2,238 | Rs 2,438 |
| 1.0 acre/day | Rs 300 | -Rs 819 | Rs 1,119 | Rs 1,319 |
| 1.5 acres/day | Rs 450 | -Rs 669 | Rs 746 | Rs 946 |
| 2.5 acres/day | Rs 750 | -Rs 369 | Rs 448 | Rs 648 |
| 4.0 acres/day | Rs 1,200 | Rs 81 | Rs 280 | Rs 480 |

At Rs 300, direct break-even is **3.73 productive acres per rover-day**. With a
Rs 200/pass support allowance it becomes **11.19 acres/day**, because only
Rs 100/pass remains to pay the rover-day cost. Travel, setup, weather and failed
missions make required nominal capacity higher.

**Decision:** retire Rs 300/acre as both a launch price and an unsupported future
promise. It can return only after measured high-throughput sampling and much
lower support cost, not merely by building more rovers.

### 5.3 Deep scans need Rs 800-1,000 and route density

The table uses the planning support allowance of Rs 200/pass.

| Productive deep-scan coverage | Direct cost/pass | Cost with support | Margin at Rs 800/pass |
|---:|---:|---:|---:|
| 1.0 acre/day | Rs 1,119 | Rs 1,319 | -Rs 519 |
| 1.5 acres/day | Rs 746 | Rs 946 | -Rs 146 |
| 2.5 acres/day | Rs 448 | Rs 648 | Rs 152 |
| 4.0 acres/day | Rs 280 | Rs 480 | Rs 320 |

At Rs 800/pass, break-even is **1.86 acres/day**. At Rs 950/pass it is
**1.49 acres/day**. A six-pass chilli package priced at Rs 4,800 loses about
Rs 876/acre at 1.5 acres/day after the planning support allowance; at
2.5 acres/day it contributes about Rs 914/acre before tax and contingency.

This makes three requirements non-negotiable:

1. use roughly Rs 950/pass as the 1.5-acre/day deep-scan test cell, not Rs 650;
2. book contiguous village routes and charge a mobilization minimum for isolated
   plots;
3. reach at least 2.5 acres/day before testing Rs 800/pass as a repeatable price.

### 5.4 Weekly sentinel visits are the affordability hypothesis

NIPHM recommends weekly surveillance after crop establishment and a structured
sample such as five field spots and five plants per spot; it does not require a
full-row robot scan on every visit. [E26] AgriRover should therefore test two
mission types:

- **sentinel visit:** fixed sampling points, trap images and crop-condition
  evidence; and
- **triggered deep scan:** full-row coverage only after a threshold, trend,
  weather risk or unexplained symptom.

If a sentinel visit reaches **5 acres/day** and exception-based support costs
**Rs 100/visit**, its modeled cost is Rs 324/acre-visit. Eight visits cost about
Rs 2,590/acre. A Rs 3,600 seasonal floor would then leave about Rs 1,010/acre of
contribution before triggered scans and contingency.

Every input in that paragraph is an AgriRover target, not a field result. The
pilot must measure whether fixed-point sampling still detects the launch-critical
problems soon enough. Missing infestations to improve throughput is failure.

### 5.5 Autonomy helps but does not rescue a weak price

If safe autonomy eventually lets one operator and one transport movement cover
several rovers, only Rs 832/day of operator plus transport is shared. Energy,
maintenance and asset recovery remain per rover. At 1.5 acres/day per rover:

| Rovers/operator | Direct cost/rover-day | Break-even/pass with Rs 200 support |
|---:|---:|---:|
| 1 | Rs 1,119 | Rs 946 |
| 2 | Rs 703 | Rs 669 |
| 3 | Rs 564 | Rs 576 |
| 4 | Rs 495 | Rs 530 |

Even infinite rover sharing leaves per-rover energy, maintenance, asset recovery
and support. A Rs 300 price therefore requires a large throughput increase and a
support cost below the planning case. It is not a credible v1 fleet promise.

### 5.6 Asset-life sensitivity

Field life matters more than a low purchase price. With the same Rs 50,000 asset,
100 active days/year and Rs 200/pass support at 2.5 acres/day:

| Useful life | Direct rover-day cost | Supported break-even/pass |
|---:|---:|---:|
| 1 year | Rs 1,452 | Rs 781 |
| 2 years | Rs 1,202 | Rs 681 |
| 3 years | Rs 1,119 | Rs 648 |
| 5 years | Rs 1,052 | Rs 621 |

The launch price must survive the one- and two-year cases until dust, water,
vibration, battery degradation and repair data justify a three-year life.

### 5.7 Honest bottom-up scale

One rover at 2.5 acres/day for 100 productive days supplies 250 acre-passes. At
Rs 800/pass that is Rs 200,000 annual service revenue before downtime and
corporate overhead. A Rs 1 crore deep-scan service at six passes per acre
requires about:

- 2,083 contracted acres;
- 12,500 acre-passes; and
- 50 rover-years at 250 passes/year, before spare capacity.

This is a fleet and route-density business. A large national robotics TAM does
not remove that operational requirement.

---

## 6. Product reality audit

### 6.1 The physical product is not yet field-proven

The repository contains extensive code, CAD, tests and BOMs, but its own field
register says key hardware is pending. Software tests do not establish traction,
chemical efficacy, navigation safety, weather resistance or farmer ROI.

Use **"production-intent prototype under construction"**, not
**"production-ready"**.

### 6.2 Current AI models cannot support crop advice

- The PlantVillage paper reported 99.35% held-out accuracy in its controlled
  dataset, but only 31.40% and 31.69% on two external image sets. [E08]
- DeepWeeds contains 17,509 images of eight weed species from northern
  Australian rangelands, not Maharashtra vegetables. [E09]
- The repository's presence of model binaries proves that inference code can
  run. It does not prove field accuracy on chilli, tomato, grapes or cotton.

Required change: limit v1 to 3-5 locally selected, actionable classes per crop;
collect Indian field images; report per-class precision, recall and false-
negative rate; and require expert review below a calibrated confidence level.

### 6.3 Low-cost NPK must not prescribe fertilizer

A 2025 CGIAR evaluation of a low-cost NPK probe found initial R-squared values
from 0.00006 to 0.2458, strong moisture dependence, and a best adjusted
R-squared of only 0.539. It explicitly discouraged fertilizer prescription.
[E10]

Required change: remove NPK-led dosage and lab-replacement claims. At most, use
the sensor for experimental relative trends paired with proper soil tests.

### 6.4 GPS is not row navigation

The u-blox NEO-6 datasheet specifies 2.5 m horizontal accuracy and 2.0 m with
SBAS. [E11] Typical chilli row spacing is around 0.60-0.75 m. [E18] GPS error
therefore spans several rows even in open-sky nominal conditions.

Required change: GPS marks the field and coarse mission position; a camera-based
row follower, odometry and local obstacle/boundary sensing control the row.
RTK is optional later for repeat absolute geotags, not a substitute for crop-row
perception.

### 6.5 Throughput needs a physical path calculation

One acre contains approximately:

- 6.75 km of row at 0.60 m spacing;
- 5.40 km at 0.75 m spacing; and
- 4.50 km at 0.90 m spacing.

At 0.3 m/s, pure travel alone takes about 6.25, 5.00 and 4.16 hours per acre.
At 0.5 m/s it takes 3.75, 3.00 and 2.50 hours, before turns, stops, setup or
refills. The current 1.5-2 hour runtime and stop-and-scan concept therefore do
not support a reliable one-acre-per-charge claim in dense vegetables.

Required change: continuous capture while moving, swappable batteries, measured
turn/setup time, and an instrumented one-acre route test.

### 6.6 The 500 ml tank is for spot treatment only

NIPHM describes common high-volume spraying as 300-500 L/ha, approximately
121-202 L/acre. [E12] APEDA uses 1,000 L/ha, about 405 L/acre, as the normal
high-volume basis for grapes. [E05]

A 0.5 L tank is only 0.25-0.41% of the general high-volume carrier requirement
for one acre and about 0.12% of the grape figure. It cannot support the pitch
that the rover replaces whole-field spraying.

Required change: keep v1 scouting-first. A later spray module needs a crop-
specific tank/nozzle/pressure design, calibrated application rate, agitation,
flow sensing, chemical compatibility and label-compliant testing.

### 6.7 The flow configuration has a 45x conflict

Repository facts:

- `pi/config.py` and `pi/data/savings.py`: **30 ml/second**.
- firmware/BOM micro-dose statement: **40 ml/minute**, or 0.667 ml/second.

The values differ by 45x. With a 500 ml tank:

| Assumption | Continuous spray time | Approx. 0.75 s bursts/tank |
|---|---:|---:|
| 30 ml/s | 16.7 seconds | 22 |
| 40 ml/min | 12.5 minutes | 1,000 |

No savings, dose, tank-capacity or service calculation is valid until the exact
pump, pressure, nozzle and liquid are calibrated gravimetrically.

### 6.8 The rupee-savings tracker mixes incompatible units

The default code multiplies 100 L/acre of **carrier mixture** by Rs 500/L. That
implies a Rs 50,000 one-pass baseline. It confuses water-based spray volume with
the cost of formulated active product and can produce an impossible saving.

For context, the Maharashtra tomato manual puts the entire seasonal chemicals
budget at Rs 15,000/acre. [E02]

Required change:

1. disable farmer-facing rupee savings until calibration;
2. record each product SKU, formulation concentration, actual product ml/g,
   tank recipe and invoice price;
3. calculate saved product versus a documented same-field baseline, not saved
   carrier water;
4. keep application labour and service fee as separate ledger entries; and
5. report confidence and missing data instead of silently applying defaults.

### 6.9 Chemical advice and application need a label-compliance gate

PPQS safe-use guidance requires pesticides to be used according to the approved
label, including dose/dilution, crop and pest, timing, interval, maximum sprays
and pre-harvest interval, with suitable application equipment. [E34] A model
confidence score is not permission to recommend or apply a chemical.

Required v1 controls:

1. keep autonomous pesticide application disabled;
2. maintain a versioned, agronomist-owned table of approved crop-pest-product
   combinations and PHIs;
3. block a recommendation when the product, crop, pest or label version is
   absent rather than filling a default;
4. require reviewer identity and timestamp on every action; and
5. keep calibration, weather, PPE and operator records for any later supervised
   application trial.

---

## 7. Competition and positioning

| Alternative | Strength | Weakness/gap AgriRover can target |
|---|---|---|
| Manual scout + knapsack | Flexible, familiar, low equipment capital | Variable coverage/records; exposure; hard to revisit the same plants |
| Spray drone service | Ministry estimate of roughly Rs 350-450/acre at about 30 acres/day [E19] | Primarily application; limited close under-canopy inspection and plant-level outcome verification |
| Niqo tractor retrofit | Reported 50-60% pesticide reduction, 3,000+ farmers and 140,000 acres; works with existing tractor sprayers [E07] | Needs tractor-accessible geometry; AgriRover cannot beat its throughput |
| Phone diagnosis app | Cheap and scalable | Farmer must notice and photograph the right symptom; no systematic row coverage |
| Satellite/drone imagery | Fast broad-area stress map | Stress is not always diagnosis; resolution/occlusion limits plant-level proof |
| Agronomist field visit | Trusted expert judgment | Scarce, expensive to repeat and difficult to standardize across every row |
| NPSS/HORTSAP public surveillance | Existing quantitative surveillance, expert validation, ETL reports and area-specific advisories [E22] [E24] | Depends on trained sampling and field observations; AgriRover can make collection repeatable, geotagged and auditable |

### Existing public systems change the product category

AgriRover should not compete as another standalone AI agronomist. The National
Pest Surveillance System already offers an offline field app, GPS-linked
quantitative and qualitative surveillance, expert image validation, ETL reports,
area-specific advisories and cotton pheromone-trap counting. Its July 2026
official scale was 73 crops, 436 pests and more than 10,000 extension workers.
[E22] [E23]

Maharashtra also has mature institutional rails. In 2024-25, CROPSAP covered
174.02 lakh ha across eight field crops. HORTSAP covered 6,58,838 ha in 30
districts across nine horticultural crops including tomato and issued 20,885
advisories during 2024. [E24]

The defensible category is therefore:

> **AgriRover is the systematic robotic scout that supplies counted, geotagged,
> repeatable field evidence into trusted public and agronomic decision systems.**

No public NPSS API or bulk-ingestion specification was found in this research.
The manual restricts scientific quantitative surveillance to credentialed
scouts and expert validation. The first integration work is institutional, not
technical theatre:

1. seek a scout credential through KVK/State Horticulture/NPSS;
2. map AgriRover observations to the crop- and pest-specific NPSS fields;
3. provide a human-verifiable export and manual submission path first;
4. request a data-sharing or API agreement before promising synchronization;
5. keep the qualified public/KVK expert as advisory issuer.

### Defensible position

AgriRover should not claim to be a cheaper generic sprayer or a replacement for
NPSS/HORTSAP. Its possible niche is:

> **Close-range, repeatable crop-protection evidence for small, irregular or
> high-value plots: inspection plus decision plus records plus verification.**

That position survives comparison with a drone, Niqo or a phone app because it
sells a different job. If the product is reduced to application-only or generic
diagnosis, its current throughput and public-system competition both lose.

---

## 8. Distribution, trust and policy

### 8.1 FPO first, individual ownership later

India's 10,000-FPO program connects about 30 lakh farmers. The official FPO
description explicitly includes making machinery available to members on a
custom-hiring basis. [E13]

The FPO should be:

- contract buyer and route aggregator;
- source of farmer records and crop calendars;
- local collection point for the rover and spare parts;
- co-owner of consented field data; and
- channel for renewal and demonstration days.

Do not make an individual farmer finance an unproved Rs 50,000 machine.

### 8.2 Use separate technical and commercial field partners

KVK Baramati has a vegetable Centre of Excellence, protected-cultivation
demonstrations and tomato planting material. [E16] Use it for controlled camera,
mobility and protocol development.

The paid-intent route should move to the production cluster. KVK Narayangaon is
inside Junnar, conducts on-farm testing and training, and sits near the
Narayangaon tomato market. [E30] Its expert should select the first target
classes, approve ETLs, audit detections and sign treatment advice.

The product must say **"KVK/agronomist-reviewed"**, not **"AI decides the dose"**.

### 8.3 Maharashtra partner shortlist

This is an interview list, not proof of willingness to partner. Current acreage,
member activity, crop calendar, contiguous route and authority to sign a pilot
must be verified directly.

| Priority | Candidate | Public evidence | Required diligence |
|---:|---|---|---|
| 1 | Junnar Taluka Farmers Producer Company, Narayangaon | Official MSAMB profile; MANAGE case study links the FPC to Narayangaon's tomato auction ecosystem [E29] | Current tomato member acres, active villages, decision maker, paid route minimum |
| 2 | Narayangadh Agro Producer Company, Khodad/Junnar | SFAC directory lists tomato, onion and okra [E29] | Current filing/activity, tomato calendar, field contiguity and willingness to share spray records |
| 3 | Krushi Kunj Agro Producer Company, Dhangarwadi/Junnar | MANAGE directory lists tomato, onion, sweet corn and cabbage [E29] | Directory is older; verify active status and current contact before outreach |
| 4 | Sangamner Kisan Krushi Producer Company | SFAC directory lists tomato among its crops; GIZ tomato work operated in Sangamner [E02] [E29] | Current tomato acreage, village density and route distance from service base |
| 5 | Varad Farmers Producer Company, Sangamner | MSAMB profile describes tomato and vegetables [E29] | Reconcile current crop focus with older SFAC listing and verify member activity |

Commercial-site rule: choose the partner that can contract at least two
contiguous villages and supply last-season spray books and invoices. Do not pick
the best-known institution if its fields are dispersed.

### 8.4 Subsidy is not the launch strategy

SMAM 2025 permits precision-farming technology in CHCs and generally supports
qualifying CHC projects through credit-linked capital subsidy. It also requires
state annual-action-plan inclusion, price discovery/empanelment, relevant test
reports, warranty and after-sales infrastructure. [E14]

Consequences:

- do not put "40% subsidy available" in a sales quote before state eligibility
  is confirmed;
- first obtain performance data, a test route and service support;
- treat SMAM as scale financing, not product-market validation;
- Agriculture Infrastructure Fund debt can later converge with eligible
  schemes, but debt should not fund a negative-margin route.

### 8.5 Avoid the underutilized-CHC failure mode

ICRISAT's scale-appropriate mechanization review identifies underutilization,
weak maintenance and lack of trained operators as recurring CHC problems.
[E15]

AgriRover should ship as an operated service with uptime, route, repair-time and
revenue metrics. A subsidized rover sitting at an FPO is not adoption.

The Namo Drone Didi operating guidelines make the same commercial dependency
explicit for another custom-hiring technology: selection hinges on demonstrated
farmer demand and the right cluster; states are asked to help each service cover
2,000-2,500 acres/year; and the package includes trained operators, repair
support, a one-year warranty and a further two-year maintenance contract. [E35]
That acreage is a drone target and must not be copied to a slow ground rover.
The transferable lesson is to secure bookings, operator training, repair
capacity and a utilization plan before placing shared equipment.

---

## 9. Pilot design that can produce a defensible claim

### 9.1 Pilot question

Can weekly rover-assisted sentinel surveillance plus agronomist-reviewed ETL
advice reduce unnecessary crop-protection spending in tomato without lowering
marketable yield or grade, while operating at a price and throughput that give
both farmer and provider positive economics?

### 9.2 Recommended exploratory design

- **Development partner:** KVK Baramati/CoE Vegetables for controlled protocol
  and hardware work.
- **Field partners:** KVK Narayangaon plus one Junnar tomato FPO selected through
  the diligence rule in Section 8.3.
- **Participants:** 12 tomato growers in two contiguous villages; reserve chilli
  for a separate observational study after the macro workflow exists.
- **Area:** one representative acre per grower. Use matched fields or clusters,
  not automatically split blocks, because spray drift and farmer operations can
  contaminate within-field comparisons.
- **Cadence:** eight weekly sentinel visits over the agreed high-risk window,
  plus up to two triggered full-row scans per intervention acre.
- **Intervention:** rover evidence; KVK/agronomist makes the action recommendation;
  licensed/manual application remains the farmer's operation.
- **Control:** normal farmer practice with an independent recorder collecting
  treatments, cost and outcome without issuing rover alerts.
- **Operational scale:** 96 sentinel acre-visits plus at most 24 deep scans. At
  target throughput of 5 sentinel acres/day and 2.5 deep-scan acres/day this is
  about 29 productive rover-days before weather and failures.

This is an exploratory commercial pilot, not a nationally generalizable efficacy
trial. A statistician/agronomist should finalize randomization and sample size.

### 9.3 Record on every pass

1. start/end time, setup, productive drive, turns, charging and downtime;
2. exact path coverage and independently audited missed rows;
3. expert-confirmed true/false detections and missed infestations by class;
4. severity, pest count and ETL decision;
5. every chemical product, active ingredient, batch, rate, water, labour and
   invoice cost;
6. farmer action, delay from alert to action, and weather;
7. verification count 48-96 hours or the agronomically correct interval later;
8. marketable yield, rejected produce, grade and realized price; and
9. farmer willingness to pay and actual paid renewal, not stated interest.

### 9.4 Technical gates

- at least 85% recall and 80% precision for each launch-critical class on a
  held-out set of local field images;
- at least 90% of expert-confirmed ETL or urgent field events detected by the
  sentinel workflow no more than one scheduled visit late;
- zero unreviewed chemical recommendations;
- at least 90% mission completion without safety intervention;
- at least 5 productive acres/day for sentinel visits and 2.5 acres/day for
  triggered deep scans, measured across real village routes;
- under 15 minutes setup per plot;
- no row/boundary contact causing crop or equipment damage;
- median agronomist review at or below 10 minutes/report without lowering the
  detection gate;
- every report linked to raw images, path and treatment records.

The accuracy thresholds are launch targets, not present performance.

### 9.5 Commercial gates

- at least 25% reduction in the farmer's documented tomato protection budget,
  with non-inferior marketable yield/grade;
- positive farmer net benefit after the actual service fee;
- provider contribution positive after measured agronomy and overhead cost;
- at least 6 of 12 pilot farmers buy a subsequent pass or sign a paid seasonal
  order;
- FPO signs a minimum-acre route for the next season; and
- fewer than 10% reports require correction after agronomist review.

### 9.6 Willingness-to-pay test

Free demonstrations do not validate demand. Fund the first two sentinel visits,
then ask farmers to buy the remaining seasonal sequence at the published test
price. Charge triggered deep scans separately so their value is visible. Record
acceptance, refusal reason and payment timing. Do not discount after hearing the
answer; test a separate cohort or package.

---

## 10. Product changes in priority order

### P0: required before chemicals or farmer savings are shown

1. Build and bench-test the complete physical rover.
2. Resolve 30 ml/s versus 40 ml/min and add measured-flow calibration.
3. Replace the rupee-savings formula with a product-and-invoice ledger.
4. Remove NPK prescription and automatic-dose language.
5. Use vision row following; restrict GPS to coarse location until proved.
6. Add an agronomist approval state between detection and treatment advice.
7. Disable autonomous pesticide spray for the first agronomic pilot.

### P1: required for the tomato pilot

1. Choose 3-5 actionable tomato classes and exact sampling units with KVK.
2. Implement repeatable sentinel points, pheromone/sticky-trap imaging and the
   official 5-spot x 5-plant sampling pattern where applicable.
3. Collect and annotate local images across farms, growth stages, phones/camera,
   sunlight, dust, wet leaves and healthy lookalikes.
4. Train detection/severity models and publish per-class field metrics.
5. Implement triggered continuous row capture, plant/row IDs and revisit matching.
6. Produce offline Marathi/Hindi farmer reports and a simple FPO console.
7. Add treatment, PHI and verification records to the data model.
8. Map observations to NPSS/HORTSAP fields and provide a reviewable export; do
   not claim live integration without authorization.
9. Instrument setup, coverage, downtime, interventions, review time and repair
   time separately for sentinel and deep-scan missions.

### P2: required for a paid cluster

1. Swappable field battery and a full-day charging/transport kit.
2. Washdown-safe fluid path, IP-rated electronics, crop-safe guards and service
   spares.
3. One-operator/two-rover supervision only after independent safety testing.
4. Crop-specific spot module with 2-5 L capacity if agronomy supports spot
   treatment; retain manual/refill coupling for full-volume applications.
5. FPO scheduling, route optimization, consent, invoicing and season reports.
6. Local repair SLA and operator certification.

### P3: scale options, not pilot requirements

- RTK or local beacons for repeat absolute plant positioning;
- grape/APEDA-compatible record export;
- pheromone-trap modules for cotton;
- buyer/insurer evidence products after consent and accuracy validation; and
- multi-rover fleet supervision after safety validation, with price set from
  measured throughput rather than an Rs 300 target.

---

## 11. Claims to retire and claims that are safe

### Retire now

| Current/likely claim | Why it is unsafe | Replacement |
|---|---|---|
| "Production-ready" | Physical hardware and field operation are unproved | "Production-intent prototype under construction" |
| "80% less herbicide/chemical" | Borrowed benchmark; no AgriRover trial | "We will test reduction against a same-field baseline" |
| "70% fertilizer saving" | No valid AgriRover evidence; NPK probe cannot prescribe | Remove |
| "Disease 7-14 days earlier" | No validated multispectral system or crop trial | "Target: earlier threshold alert; timing to be measured" |
| "One-season payback" | Depends on unproved saving and throughput | Show scenario and pilot gate |
| "Rs 300/acre" | Direct break-even is 3.73 acres/day and supported break-even is much higher | Test Rs 800-1,000 deep scans and a separate lower-cost sentinel workflow |
| "Sub-2 m GPS is enough for rows" | Error spans several vegetable rows | "GPS coarse; vision controls rows" |
| "NPK probe replaces lab tests" | Contradicted by independent evaluation | "Use certified soil tests for prescriptions" |
| "AI gives the dosage" | Safety, label and agronomy risk | "Agronomist-reviewed, label-compliant advice" |
| "Rupees saved" from current tracker | Flow and cost units are invalid | "Savings shown only from calibrated product/invoice records" |

### Safe today

- AgriRover is designed as a low-cost ground platform for close-range crop-row
  imaging, geotagged records and future targeted intervention.
- External field studies show that threshold-based IPM and robotic spot spraying
  can reduce chemical use or improve profit in specific crops and systems.
- The current business hypothesis is an FPO/KVK-operated tomato sentinel and
  triggered-scan service in one dense Maharashtra cluster.
- AgriRover is intended to collect repeatable field evidence for qualified
  experts and existing surveillance systems; it is not a standalone agronomist.
- AgriRover's own savings, accuracy, throughput, reliability and willingness-to-
  pay remain to be measured.

### Claim ladder after evidence

1. **Bench:** calibrated flow, battery, safety and path tests.
2. **Model:** local held-out per-class accuracy.
3. **Field operation:** coverage, uptime and crop-safety results.
4. **Agronomic:** treatment reduction without yield/grade loss.
5. **Commercial:** paid renewal and positive provider margin.
6. **Scale:** multi-site replication over at least two seasons.

Do not skip a rung in a deck or sales conversation.

---

## 12. Go-to-market roadmap

### Months 0-2: make measurements trustworthy

- complete one physical rover;
- resolve flow, tank, savings and row-navigation issues;
- sign KVK Narayangaon as agronomy sponsor or secure an equivalent local expert;
- diligence the Junnar/Sangamner shortlist and sign one FPO data/pilot agreement;
- interview at least 12 Junnar tomato growers using spray books and bills;
- define sentinel points, launch classes, ETLs, trigger rules and report format;
- request an NPSS scout/integration discussion through the institutional partner;
  and
- collect field video before training another broad generic model.

**Gate:** safe supervised traversal plus traceable measurements.

### Months 3-6: paired exploratory pilot

- execute the 12-grower protocol;
- compare sentinel detection against blinded expert full-field audits;
- publish weekly technical and economic dashboards internally;
- freeze model versions during each comparison window;
- hold two field days showing raw control/intervention evidence; and
- charge for later passes to test demand.

**Gate:** technical and commercial thresholds in Section 9.

### Months 7-12: one paid cluster

- offer crop-specific seasonal contracts, not hardware sales;
- require an FPO route minimum;
- operate 2-3 rovers with one spare and measure utilization;
- use an agronomist review queue and repair SLA; and
- publish a signed case study with method, denominator and limitations.

**Gate:** positive contribution margin and at least 60% paid renewal.

### Months 13-24: replicate, then broaden

- reproduce the result with two additional FPO/KVK environments;
- prove one-operator/two-rover supervision before lowering price;
- add grape compliance or cotton trap scouting as separate products;
- begin authorized machinery testing/SMAM pathway only with stable hardware;
- use AIF/subsidy convergence for proven assets, not pilots; and
- consider ownership sales only to capable FPO/CHC operators with support.

**Gate:** two seasons, three clusters, stable unit economics and documented
after-sales capability.

---

## 13. Primary customer research still required

Published research validates the problem, not the buying decision. Before
locking price, conduct interviews using bills and field records, not opinions.

### Minimum interview set

- 12 tomato farmers in the target Junnar villages across small and larger
  holdings, plus 6 chilli growers in a genuine chilli district for discovery;
- managers of at least 3 shortlisted tomato FPOs;
- 2 CHC operators;
- 2 KVK/SAU plant-protection experts;
- 3 pesticide retailers or crop advisers;
- 2 spray labour contractors;
- 2 grape exporters/pack houses for traceability discovery; and
- 2 drone/tractor service operators for route and pricing benchmarks.

### Questions that change the product

1. Show every spray from the last season: date, reason, product, cost and who
   advised it.
2. Which spray would you remove in hindsight, and what evidence would have made
   you comfortable removing it?
3. How often does someone inspect every row, how long does it take, and what is
   missed?
4. What was the most expensive late detection in the last three seasons?
5. Who is trusted to authorize a no-spray decision?
6. What report or proof does the buyer/FPO/exporter already require?
7. Would you book the remaining six weekly sentinel visits for Rs 2,700-3,300
   after two funded visits? Then separately test Rs 800-1,000 for a triggered
   full-row scan. Ask for the booking, not a yes/no answer.
8. What minimum saving or loss avoided would justify a seasonal contract?
9. Who transports, cleans, stores and repairs shared machinery now?
10. What happens when service is needed on the same day by twenty farmers?

The answers should update the economics model, crop score and pilot protocol.

---

## 14. Risk register

| Risk | Early test | Kill/mitigation rule |
|---|---|---|
| Local model misses severe disease | Blinded expert audit on held-out farms | No farmer advice until class recall gate passes |
| Sentinel sample misses an urgent field event | Compare every sentinel result with independent full-field audits | Change sample/interval or stop the low-cost mission; do not hide misses with a dashboard |
| Scouting does not change sprays | Compare action logs with control | Stop selling savings; retain only proven record/scouting use |
| Sentinel below 5 or deep scan below 2.5 acres/day | Timed multi-village routes including setup and travel | Raise price/change mission design or stop the affected RaaS offer |
| Farmer will not buy the seasonal continuation | Paid continuation after two funded sentinel visits | Redesign buyer/offer; do not hide with subsidy |
| Agronomist review is too expensive | Measure minutes/report and error rate | Restrict classes, batch review or price it explicitly |
| Tiny chilli pests cannot be counted | Macro leaf/flower and trap trial against hand-lens counts | Keep chilli out of paid launch until count accuracy passes |
| Crop canopy blocks useful views | Coverage audit by growth stage | Change camera geometry or drop that crop/stage |
| Spot treatment harms crop/beneficials | Agronomist-led small-plot efficacy trial | Keep application manual; no autonomous chemical action |
| FPO asset is underutilized | Route bookings before deployment | Operated contract, utilization SLA, no unsupported sale |
| NPSS/HORTSAP integration is unavailable | Written credential/API discussion with the responsible institution | Use explicit manual export; never advertise an unapproved integration |
| Data creates liability/trust concern | Written consent and correction workflow | Farmer/FPO access, purpose limitation and deletion policy |
| Weather/dust/water causes failures | Soak, dust, vibration and field endurance tests | Ruggedize before paid deployment |

---

## 15. Evidence ledger

| ID | Source and result used | Quality and limit |
|---|---|---|
| E01 | [ICAR-NRIIPM Annual Report 2023-24](https://nriipm.res.in/NCIPMPDFs/AnnualReport/AR-2024.pdf): chilli IPM 19 vs 29.2 sprays; cost and return table | Primary institutional demonstration; full IPM bundle, not rover effect |
| E02 | [GIZ Good Agricultural Practices in Tomato Cultivation - Maharashtra, 2024](https://2023.snrd-asia.org/wp-content/uploads/2024/03/Good-agricultural-practices-in-Tomato-Cultivation-%E2%80%93-A-technical-manual-for-Maharashtra.pdf): Rs 15,000 chemicals + Rs 2,000 application/acre | Government/technical manual; illustrative budget, local costs vary |
| E03 | [ICAR-NRIIPM IPM in Bt Cotton](https://nriipm.res.in/NCIPMPDFs/successstories/IPM-inBtCotton.pdf): Jalna four-year IPM economics | Strong local benchmark; multi-component IPM, not AI-only |
| E04 | [Mhetre et al., Sangli grape economics](https://www.ijcmas.com/special/11/A.V.%20Mhetre,%20et%20al.pdf): Rs 190,491/ha plant protection, 16.93% | Farm-economics study; location/year-specific |
| E05 | [APEDA grape export procedure, 2026](https://apeda.gov.in/sites/default/files/export_procedures/procedureforexportofgrapes_17Feb_2026.pdf): normal high-volume basis 1,000 L/ha | Current official procedure; application can vary with efficient equipment but active ingredient/ha remains critical |
| E06 | [APEDA grape export procedure, 2026, Annexure 2A](https://apeda.gov.in/sites/default/files/export_procedures/procedureforexportofgrapes_17Feb_2026.pdf): plot, chemical, active ingredient, batch, quantity, water, PHI, spray time and operator | Current official workflow evidence; AgriRover integration not yet built |
| E07 | [NITI Frontier Tech profile of Niqo Robotics](https://frontiertech.niti.gov.in/story/see-select-spray-how-niqo-robotics-is-cutting-pesticide-use-with-ai-powered-farming): 50-60%, 3,000+ farmers, 140,000 acres | Government-curated company profile; reported impact, not independent trial |
| E08 | [PlantVillage paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC5032846): 99.35% held-out vs 31.40/31.69% external | Peer-reviewed; directly shows domain-shift risk |
| E09 | [DeepWeeds](https://www.nature.com/articles/s41598-018-38343-3): 17,509 images, eight northern-Australian rangeland weeds | Peer-reviewed dataset description; wrong deployment domain |
| E10 | [CGIAR low-cost NPK probe evaluation, 2025](https://cgspace.cgiar.org/bitstreams/fe955214-2ee7-490a-9f63-1d5a7fa09f96/download): poor R-squared and moisture dependence | Independent evaluation; supports removing prescription claims |
| E11 | [u-blox NEO-6 datasheet](https://content.u-blox.com/sites/default/files/products/documents/NEO-6_DataSheet_%28GPS.G6-HW-09005%29.pdf): GPS 2.5 m, SBAS 2.0 m | Manufacturer specification under stated conditions; field can be worse |
| E12 | [NIPHM Pesticide Application Manual](https://niphm.gov.in/Recruitments/ASO-PHE-Manual-NIPHM-03102013.pdf): 300-500 L/ha high-volume guide | Official training manual; crop/nozzle dependent |
| E13 | [PIB 10,000 FPOs release](https://pib.gov.in/PressReleasePage.aspx?PRID=2106913): about 30 lakh farmers and machinery custom hiring | Official channel scale; not proof a specific FPO will buy |
| E14 | [SMAM 2025 Guidelines](https://farmech.dac.gov.in/Content/New_Folder/SMAM-2025.pdf): CHC precision technology, testing, empanelment and state process | Official policy; eligibility is conditional, not automatic |
| E15 | [ICRISAT Scale-Appropriate Mechanization review](https://oar.icrisat.org/13437/1/Scale%20Appropriate%20Mechanization%20Report-%2014012026_Revised.pdf): CHC underutilization, maintenance/operator constraints | Institutional synthesis; exact local utilization must be measured |
| E16 | [CoE Vegetables About](https://coekvkbaramati.com/aboutus.aspx) and [current sale page](https://coekvkbaramati.com/sell.aspx): demonstration role and tomato planting material | Official partner capability; no partnership agreed yet |
| E17 | [Labour Bureau Rural Wages](https://labourbureau.gov.in/rural-wages): Maharashtra male plant-protection worker wage Rs 582.10/day, Jan 2026 | Current official state observation; local peak wage and employment overhead may be higher |
| E18 | [TNAU chilli cultivation guide](http://www.agritech.tnau.ac.in/horticulture/horti_vegetables_chilli_cultural.html): 60 x 45 cm varieties, 75 x 60 cm hybrids | University guide; field layout varies by Maharashtra farm |
| E19 | [Peer-reviewed review of Indian agricultural drones](https://pmc.ncbi.nlm.nih.gov/articles/PMC12349003): ministry estimate Rs 350-450/acre at about 30 acres/day | Secondary synthesis; use as competitive range, verify local quotes |
| E20 | [Peer-reviewed robotic spot-spray field trial](https://doi.org/10.1016/j.compag.2025.110365): 25 ha sugarcane, 97% relative efficacy, 35% mean herbicide reduction | Mechanism benchmark in another crop/system; not transferable as an AgriRover claim |
| E21 | [AI adoption barriers in Indian agriculture](https://ideas.repec.org/a/igg/jide00/v12y2021i3p30-44.html): trust and language identified as critical | Participatory expert study; supports KVK/local-language design |
| E22 | [NPSS official user manual](https://npss.dac.gov.in/app/assets/files/NPSS_User_Manual_English.pdf): offline app, GPS observations, credentialed quantitative surveillance, expert validation, ETL reports, advisories and cotton trap counting | Official system specification; no public API or AgriRover access established |
| E23 | [PIB NPSS update, 24-Jul-2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2289031): 73 crops, 436 pests and more than 10,000 extension workers | Current official scale statement; does not establish local tomato use or integration access |
| E24 | [ICAR-NRIIPM database and networking update](https://nriipm.res.in/databasenetworking.aspx): 2024-25 CROPSAP 174.02 lakh ha; HORTSAP 6,58,838 ha, 30 districts, nine crops including tomato; 20,885 advisories in 2024 | Current institutional operating evidence; official pages report programme aggregates, not AgriRover outcomes |
| E25 | [Horticultural Statistics at a Glance 2024](https://agriwelfare.gov.in/Documents/HORTICULTURAL_STATISTICS_AT_A_GLANCE_2024.pdf): Maharashtra tomato 55,227 ha/1,332,085 t; Nashik 22,040 ha, Pune 4,772 ha, Ahmednagar 4,324 ha, Solapur 4,072 ha; green chilli 43.77 thousand ha/438.38 thousand t | Official 2023-24 statistics; district data are state-reported and do not prove route density inside a village |
| E26 | [NIPHM AESA tomato package](https://niphm.gov.in/IPMPackages/Tomato-R.pdf): weekly scouting; five spots x five plants; pest-specific leaf, fruit, disease and trap observations | Official sampling basis; local KVK must approve launch classes and any modified robotic sample |
| E27 | [ICAR-NRIIPM chilli extension folder](https://nriipm.res.in/NCIPMPDFs/FOLDERS/chilienglish_.pdf) and [NIPHM chilli package](https://niphm.gov.in/IPMPackages/Chilli.pdf): fruit borer, thrips, whitefly and mite thresholds plus leaf/fruit sampling methods | Official guidance; small pests need macro/manual methods and current local validation |
| E28 | [DPPQ&S/PPQS Thrips parvispinus monitoring guide](https://ppqs.gov.in/sites/default/files/south_east_asian_thrips_thrips_parvispinus-monitoring_and_management.pdf): invasive chilli pest colonizes reproductive parts and official guide reports 50-80% damage | Official pest alert/management evidence; reported damage is not an AgriRover-addressable benefit |
| E29 | [MSAMB Junnar Taluka FPC profile](https://fpc.msamb.com/en/FPO/FPCProfile/576/JUNNAR-TALUKA-FARMERS-PRODUCER-COMPANY-LIMITED), [SFAC Maharashtra FPO list](https://sfacindia.com/PDFs/List-of-FPO%20identified-by-SFAC/List%20of%20FPOs%20in%20the%20State%20of%20Maharashtra.pdf), [MANAGE direct-marketing directory](https://www.manage.gov.in/publications/directory-mktg.pdf) and [MSAMB Varad profile](https://fpc.msamb.com/en/FPO/FPCProfile/80/Varad-Farmers-Producer-Company-Limited) | Public candidate evidence; entries and contacts can be stale, so active tomato acres and authority must be verified directly |
| E30 | [KVK Narayangaon official site](https://www.kvknarayangaon.in): Junnar location and on-farm testing/training mandate | Official local capability; no AgriRover partnership agreed |
| E31 | [Integrated Pest Management Schedule for Vegetables](https://agritech.tnau.ac.in/horticulture/pdf/tech_bulletin/national/IPM-Schedule-for-vegetables.pdf): tomato fruit-borer and chilli thrips/mite thresholds plus trap-monitoring guidance | Government technical schedule hosted by TNAU; KVK must validate applicability to local variety, season and current pest complex |
| E32 | [ICAR-NRIIPM Annual Report 2024, pp. 26-27](https://nriipm.res.in/NCIPMPDFs/AnnualReport/AR-2024.pdf): Annamayya tomato IPM 7.33 vs 18.66 sprays, 15.8% lower cultivation cost, 23.13 vs 21.84 t/acre yield and Rs 2.25 vs 1.35 lakh net return; Bulandshahr residue comparison | Current primary institutional demonstration; a full IPM bundle in AP/UP, not a Maharashtra result or a rover effect |
| E33 | [Cole et al., digital agricultural extension RCT](https://precisiondev.org/wp-content/uploads/2025/01/Odisha_RCT_Nov27.2024.pdf) and [authors' 2025 summary](https://voxdev.org/topic/agriculture/customised-agricultural-advice-scale-how-digital-extension-helps-indian-farmers): 13,675 randomized rice farmers, high content access, modest average yield gain and lower severe-loss risk | Large Indian randomized trial; free voice advisory in rice, not paid tomato scouting or AgriRover evidence |
| E34 | [PPQS safe-use instruction](https://ppqs.gov.in/divisions/integrated-pest-management/instruction-safe-use-pesticide?language_content_entity=en) and [PPQS safe/judicious-use SOP](https://ppqs.gov.in/sites/default/files/2025-03/sop_for_safe_and_judicious_use_of_tricyclazole_and_buprofezin_0.pdf): label dose, crop stage, intervals, maximum sprays, equipment and PHI must be followed | Official safety principle; the linked SOP is crop/product-specific and does not authorize robotic application |
| E35 | [Namo Drone Didi operational guidelines](https://farmech.dac.gov.in/Content/New_Folder/Operational_Guidelines_of_Namo_Drone_Didi_Scheme.pdf): demand-led cluster selection, 2,000-2,500 acres/year support target, operator/assistant training, warranty and maintenance | Official custom-service comparator; drone throughput and subsidy are not transferable to AgriRover |

---

## 16. Calculation appendix

### Conversions

- 1 acre = 4,046.86 square metres.
- Row-path length per acre = 4,046.86 / row spacing in metres.
- 1 hectare = 2.47105 acres.

### Provider equations

```text
daily_full_cost = operator + transport + energy + maintenance + asset_recovery
                = 582 + 250 + 40 + 80 + 167
                = Rs 1,119 (rounded)

break_even_price_per_acre = daily_full_cost / productive_acres_per_day
supported_break_even_price = daily_full_cost / productive_acres_per_day
                             + support_cost_per_pass
break_even_acres_at_price = daily_full_cost / (price - support_cost_per_pass)

direct_break_even_acres_at_Rs300 = 1,119 / 300 = 3.73 acres/day
supported_break_even_at_Rs800 = 1,119 / (800 - 200) = 1.86 acres/day
supported_break_even_at_Rs950 = 1,119 / (950 - 200) = 1.49 acres/day

deep_season_cost = passes * (daily_full_cost / acres_per_day + support_per_pass)
sentinel_cost_at_target = 8 * (1,119 / 5 + 100) = Rs 2,590.40/acre
```

### Farmer equations

```text
chilli_direct_gap = 51,090 - 25,930 = Rs 25,160/acre
chilli_net_gap = (395,500 - 159,480) - (374,750 - 181,390)
               = Rs 42,660/acre

capture_required_on_direct_gap = 4,800 / 25,160 = 19.1%
capture_required_on_net_gap = 4,800 / 42,660 = 11.3%

tomato_break_even_share_at_floor = 3,600 / 17,000 = 21.2%
```

### Final decision rule

Continue toward a paid service only if the pilot simultaneously proves:

1. agronomic safety and useful local model accuracy;
2. farmer net benefit after the real fee;
3. at least 5 sentinel acres/day and 2.5 deep-scan acres/day on real routes;
4. paid renewal rather than demonstration interest; and
5. positive provider contribution after measured agronomy, sales/support,
   transport, operator and asset recovery.

If any one of these fails, change the crop, offer, hardware or price before
building a fleet. The design is not the product; repeatable farmer profit is.
