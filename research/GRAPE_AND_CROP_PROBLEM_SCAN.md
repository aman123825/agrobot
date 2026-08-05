# AgriRover — Grape & Crop Problem Scan (problem → rover fit → add-on that unlocks it)

**First-hand web research pass | 04-Aug-2026 | focus: grapes (Nashik), with onion & pomegranate adjacencies**

> Purpose: start from the grape cold-storage / harvest-timing idea and scan real,
> sourced Indian crop problems, and for each say honestly (a) what AgriRover can do
> with its **current** hardware, and (b) **what single cheap add-on component would
> unlock it** if the current stack can't. Ranked by value × feasibility × who pays.

## Method & limits (honest)

Sources below are real, with working links, gathered from news, government/ICAR/APEDA
material, peer-reviewed sensing papers, and agri-vendor pages. I did **not** watch
video/audio, so "farmer voice" is quoted from reportage (§5), not transcribed from
YouTube. Numbers are labelled with the same scheme as the other dossiers:

- **[External result]** — measured/published elsewhere; validates a problem, not AgriRover.
- **[Repository fact]** — present in this repo's BOM/code/design.
- **[Analyst scenario]** — a transparent estimate (incl. component prices), not a quote or forecast.
- **[AgriRover target]** — a gate to prove in a field trial before the claim is used.

Standing caveat: AgriRover has **no field-validation data**. Every "rover can…" is an
[AgriRover target]. Component prices are indicative India-market ranges [Analyst scenario].

Sources numbered `[S1]…[S25]` at the end (separate from the `[E]/[F]/[G]/[H]` ledgers in the other dossiers). Where a claim overlaps the existing `PROBLEM_SOLUTION_CATALOG.md`, this file **defers to it and does not contradict its kills** (esp. the RGB-Brix pass/fail kill in its §1.1a).

---

## AgriRover's current sensing envelope (what we're designing around)

**[Repository fact]** (`firmware/include/pins.h`, `README.md`, `docs/BOM-top20-groww-trackA.md`):
slow close-range **ground rover**, RGB camera + Hailo-8/Coral AI, 7-in-1 NPK/RS485 soil probe,
soil moisture + TDS, DHT22 air temp/RH, ToF + ultrasonic, GPS, IMU/encoders, 500 ml pump +
linear-actuator spot dosing with pan/tilt nozzle. It drives *inside* the canopy at close range
(its real edge over drones and fixed weather stations), but it is slow and RGB-only.

---

## 1. GRAPES (Nashik / Maharashtra)

### 1.1 Downy & powdery mildew — the recurring money pit
- **Problem & magnitude.** Downy mildew (*Plasmopara viticola*) and powdery mildew are the most destructive grape diseases in India; by the time visible "oil spots" appear the infection is already system-wide, causing defoliation and flower/bunch drop. **[External result]** `[S4]`, `[S8-refs]` Growers spray prophylactically all season; downy alone commonly needs ~7–8 fungicide sprays/season (US benchmark) `[S24]`, and fungicide resistance is a documented problem. Cost of cultivation has ballooned (one Hyderabad grower: ~₹60k/acre 15 yrs ago → ~₹4 lakh/acre today). **[External result]** `[S25]`
- **Current-hardware fit.** RGB can spot late, visible lesions — **too late** to be worth much. DHT22 gives *air* temp/RH but not canopy microclimate or leaf wetness. → low value as-is.
- **Add-on that unlocks it →** a **leaf-wetness sensor + canopy-level temp/RH logger** (SHT31 ~₹300–800; leaf-wetness sensor ~₹1,500–5,000) to compute the classic infection index (≈ temperature × leaf-wetness duration) and warn **48–72 h before** symptoms — the preventive window. Sensor-node systems using atmospheric parameters report **94.4% (downy) / 96% (powdery)** detection accuracy. **[External result]** `[S15]`, `[S18]` For pre-symptomatic optical detection, a **cheap thermal camera** (MLX90640 ~₹2,500–5,000; FLIR Lepton ~₹15–25k) — thermal imaging detects downy early `[S16]`; hyperspectral hits ~81% `[S17]` but is out of budget. **Rover's unique edge:** it can carry these *into many rows* and build a **spatial risk map**, so spraying is targeted to hot-spots rather than the whole block. [Analyst scenario]
- **Who pays.** Grower/FPO (recurring spray budget); overlaps export compliance (§1.2).
- **Proof gate.** Rover-mounted micro-climate index predicts a real downy outbreak ≥48 h ahead on a held-out Nashik block, beating a fixed station on spatial resolution. **[AgriRover target]**
- **Verdict:** pursue — but the value is in the **add-on microclimate sensor + map**, not the RGB camera. (Note: fixed IoT stations like Fyllo `[S4]` already sell the point-forecast; the rover must prove the *spatial* version is worth more.)

### 1.2 Export residue / MRL rejection — the wedge with a real payer
- **Problem & magnitude.** EU rejections over **chlormequat** residue once cost exporters an estimated **₹273 crore**; EU MRL is **0.05 mg/kg**. **[External result]** `[S5]`, `[S6]` Grape export to the EU is legally gated by **APEDA registration + a Residue Monitoring Plan (RMP) / GrapeNet traceability**. **[External result]** `[S7]`
- **Current-hardware fit.** The rover can capture **geotagged, timestamped records** of scouting + (with an agronomist) the product/dose/PHI applied — an audit artefact that feeds GrapeNet/RMP. It **cannot measure residue** (that's a lab).
- **Add-on that unlocks it →** none on the rover; residue is a lab test. The rover's role is the **record**, not the measurement. (This matches the adoption dossier's conclusion: the defensible buyer is a solvent, *liable* exporter/pack-house.)
- **Who pays.** Exporter / pack-house (real liability). **Proof gate:** a per-plot record an exporter's QA actually accepts into their RMP file. **[AgriRover target]**
- **Verdict:** pursue as a **traceability/record** product for exporters — highest-quality payer in the whole scan.

### 1.3 Weather / climate loss & berry cracking — mostly NOT rover-solvable
- **Problem & magnitude.** NRCG scientists warned of up to **50% harvest loss** across Maharashtra this season from poor sunlight + prolonged rain; a Nashik grower reported bunches per vine crashing from **35–40 to just 3–5**; wine prices expected **+25–30%**. **[External result]** `[S1]`, `[S2]`, `[S3]` Rain cracks tender berries.
- **Rover fit.** Can't stop rain. Only real role: **document damage** (geotagged) for a crop-insurance claim.
- **Add-on:** none. **Verdict:** park (evidence-capture only).

### 1.4 Harvest-timing vs cold-storage — **your idea, in its defensible form**
- **Problem & magnitude.** India loses **~8.23–16%** of grapes post-harvest (~223k tonnes/yr at the low end); nationally **~30%** of fruit & veg (≈40 Mt, ~US$13 bn) is wasted, and roughly **90% moves without any cooling** — cold-chain is scarce and concentrated in a few states. **[External result]** `[S8]`, `[S9]`, `[S10]` Mistimed cutting (before/after optimal maturity) shortens shelf life and fails export grade.
- **Current-hardware fit.** RGB can score **colour/veraison, bunch count, and visible defects** → a **relative harvest-readiness index (0–100%)**, geotag it, and build a **block maturity map**. It then **sequences the harvest to the grower's available cold-storage / reefer / market slots** — pick the ready blocks first, leave the rest — exactly your cold-storage-loss idea.
- **Honest limit (do not overclaim).** RGB **cannot read Brix/sugar or acidity** — the true maturity index (Thompson Seedless ~18–22 °Brix; NHB harvest TSS >17 °Brix). `[S13]`, `[S14]` The existing `PROBLEM_SOLUTION_CATALOG.md` §1.1a already **kills** RGB→absolute-Brix for a regulated pass/fail. So sell this as **relative ripeness for sequencing**, not an absolute Brix number.
- **Add-on that would deepen it →** a **handheld/inline refractometer** (₹500–2,000, but destructive + manual) for spot-calibrating the RGB index against real Brix; portable NIR "pocket" sensors exist (~₹30k+) but are flagged unreliable for field pass/fail in the catalog. So keep it RGB-relative + occasional refractometer ground-truth. [Analyst scenario]
- **Who pays.** FPO / pack-house / exporter juggling limited cold storage and harvest crews. **Proof gate:** the RGB readiness index rank-orders blocks in agreement with refractometer Brix on a held-out set, and sequencing measurably cuts spoilage vs the grower's baseline. **[AgriRover target]**
- **Verdict:** pursue — this is a genuinely good fit **because it needs only *relative* ripeness**, which sidesteps the Brix kill. Strongest new idea in this scan alongside §1.2.

### 1.5 Labour scarcity — rover reduces the *scouting* walk, not skilled work
- **Problem.** Grapes are highly labour-intensive (~10 workers/acre, mostly skilled) `[S12]`; during COVID, Nashik grapes were left to **rot for want of harvest labour**. **[External result]** `[S11]` Girdling/thinning/dipping are skilled and can't be automated cheaply.
- **Rover fit.** Replaces the **weekly disease/ripeness scouting walk** (ties to §1.1 & §1.4), not the skilled hand-work. **Add-on:** none beyond §1.1/§1.4. **Verdict:** supporting benefit, not a standalone product.

---

## 2. ONION — storage loss (the other "cold storage" problem you meant)
- **Problem & magnitude.** Under ambient storage, onion losses reach **up to 50%** (physiological weight loss 20–25%, sprouting 10–12%, rotting 10–12%); other work puts **30–40%** lost, and ~**40–50%** of stored onion never reaches consumers. Irradiation cut sprouting to **0.3%** vs 6.05%. **[External result]** `[S19]`, `[S20]`, `[S21]`
- **Rover fit (honest).** A field ground rover **doesn't help inside a storage chawl** — this is a *storage* problem, not a field one. Two real angles:
  1. **Field angle (rover fits):** detect **% neck-fall / topple** at maturity so onions are lifted at the right time (early/late lifting worsens storability). RGB-buildable. **[AgriRover target]**
  2. **Storage angle (needs a different product, not the rover):** a static **storage-monitoring node** — temp/RH + an **ammonia/VOC gas sensor (MQ-137 ~₹300–900)** + camera — to flag rot hot-spots and sprouting early (the direction of the IoT/UV-C work in `[S20]`).
- **Verdict:** the field harvest-timing angle is a rover fit; the storage-monitor is an **adjacent product** worth noting but off the rover's envelope.

## 3. POMEGRANATE — bacterial blight (Telya)
- **Problem & magnitude.** Bacterial blight (*Xanthomonas axonopodis* pv. *punicae*) causes yield losses **up to 80%** under epidemic conditions across Maharashtra/Karnataka/AP/Gujarat; it survives in stems/debris, so **roguing + preventive sprays in humid windows** are key. **[External result]** `[S22]` Vendors forecast blight risk **48–72 h** ahead from weather. **[External result]** `[S23]`
- **Current-hardware fit.** RGB detects visible oily lesions / fruit cracking → **map + flag plants to rogue**. Close-range fruit/stem inspection is the rover's edge.
- **Add-on that unlocks it →** same **canopy leaf-wetness + temp/RH logger** as §1.1 to drive the 48–72 h forecast. **Who pays:** pomegranate FPO/grower. **Verdict:** pursue as a second crop once the grape microclimate+map stack works — same components.

---

## 4. Add-on component shortlist (what each unlocks, rough ₹)

| Component | Rough ₹ (indicative) | Unlocks | Priority |
|---|---|---|---|
| Canopy temp/RH logger (SHT31) + **leaf-wetness sensor** | ₹300–800 + ₹1,500–5,000 | Downy/powdery + pomegranate blight **early warning** (§1.1, §3) | **High** |
| Cheap **thermal camera** (MLX90640) | ₹2,500–5,000 | Pre-symptomatic mildew detection (§1.1) | Medium |
| **Refractometer** for RGB ground-truthing | ₹500–2,000 | Calibrate ripeness index (§1.4) | Medium |
| **Ammonia/VOC gas sensor** (MQ-137) | ₹300–900 | Onion storage rot node (§2, adjacent product) | Low/adjacent |
| RTK-GPS | ₹15,000–40,000 | Precise per-plot maps (all mapping uses) | Later |

All prices **[Analyst scenario]**, to confirm against live India suppliers.

## 5. Farmer voice (from reportage, not video)
- Nashik grower, on this season's collapse: bunches per vine fell from "**35 to 40**" to "**just three to five**." **[External result]** `[S2]`
- Nashik, COVID: vineyards "full of good quality produce" but left to rot with "**no labour to harvest**" and no way to market. **[External result]** `[S11]`
(Short quotes; full context at the sources. Content paraphrased where longer.)

## 6. Verdict — what to build first
1. **Grape downy/powdery early-warning map** (§1.1) — add the **leaf-wetness + canopy RH/temp** node; this is the recurring pain with the clearest sensing evidence.
2. **Export traceability record** (§1.2) — best *payer* (liable exporter); needs process, not new hardware.
3. **Ripeness-index → storage-matched harvest sequencing** (§1.4) — your idea, in the RGB-*relative* form that dodges the Brix kill.
4. **Pomegranate blight** (§3) reuses the §1.1 components — a clean second crop.
5. Onion: do the **field harvest-timing** angle on the rover; treat the **storage node** as a separate product.

**One-line takeaway:** the rover's RGB camera is rarely the thing that unlocks value here — a **~₹2–6k canopy micro-climate sensor** (leaf-wetness + RH/temp) unlocks the biggest, most recurring grape and pomegranate problems, and your cold-storage idea is viable **if scoped to relative ripeness for harvest sequencing** rather than absolute Brix.

---

## v2 (in progress) — deeper verification

### v2 progress checklist
- [x] (1) Verify add-on component prices vs live Indian suppliers — **done (v2.1 below)**
- [x] (2) Drone-vs-ground-rover cost-per-acre model — done (v2.2 below)
- [x] (3) Cotton problems + rover/component fit — done (v2.3)
- [x] (4) Banana problems + rover/component fit — done (v2.4)
- [x] (5) Real farmer complaints from forums/reportage — done (v2.5)
- [x] (6) Sugarcane problems + rover/component fit — done (v2.6)
- [x] (7) Chilli problems + rover/component fit — done (v2.7)
- [x] (8) Deepen grape downy/powdery economics — done (v2.8)
- [x] (9) APEDA GrapeNet / Residue Monitoring Plan specifics — done (v2.9)
- [x] (10) Onion storage-monitoring node BOM + cost — done (v2.10)
- [x] v2 queue COMPLETE (items 1–10)

### v2.1 Add-on component prices — verified against live Indian listings (04-Aug-2026)
Several v1 estimates were **too low**. Corrected, live retail figures — all **[External result]**:

| Component | v1 estimate | Verified live India price | Source |
|---|---|---|---|
| Refractometer 0–32 °Brix | ₹500–2,000 | **₹859–1,283** (Real Instruments ₹859; Labsoul ₹1,000; Erma digital ₹1,283) | `[S26]` |
| SHT31 temp/RH module | ₹300–800 | **₹700–1,200** branded (Adafruit ~₹966); generic breakouts lower | `[S27]` |
| MQ-137 ammonia sensor | ₹300–900 | **~₹1,199** (Robocraze) — higher than estimated | `[S28]` |
| MLX90640 thermal camera (32×24) | ₹2,500–5,000 | **₹7,250–10,000** (ThinkRobotics ₹7,250–7,350; Adafruit ~₹8,815; M5StickC ₹10,004) — **much** higher | `[S29]` |
| Leaf-wetness sensor | ₹1,500–5,000 | **₹3,700–11,600** for a real RS485 field sensor (imports, ~$45–139); no cheap hobby module found | `[S30]` |

**Correction to the v1 takeaway (important).** v1 claimed a "~₹2–6k canopy micro-climate node" unlocks the biggest grape/pomegranate problems. Verified prices push that **up**: a credible **leaf-wetness + SHT31 node is ~₹4,400–12,800** (leaf-wetness ₹3,700–11,600 + SHT31 ₹700–1,200), and adding a **thermal camera is ₹7,250–10,000**, not ₹2,500–5,000. The mildew early-warning idea still stands, but its hardware bill is **~2–3× the v1 figure** — which strengthens the argument that a *fixed* IoT station (Fyllo-type) may amortise that sensor better than a slow rover carrying one. **[Analyst scenario]** The genuinely cheap, confirmed items are the **refractometer (₹859–1,283)** for ripeness ground-truthing and **SHT31 (₹700–1,200)**.

### v2.2 Drone vs ground-rover — cost per acre (why the rover is not a coverage tool)
**The throughput gap is the whole story.** A spraying drone does **1 acre in ~7–8 min**, a Namo Drone Didi rig covers **up to 20 acres/day**, and commercial rigs claim 10–15 acres/hour. **[External result]** `[S31]`, `[S32]` A small, slow, close-row scouting rover like AgriRover moves at **~0.6–1.0 m/s** `[S34]`; driving 3 m-spaced rows is roughly **1,350 m of travel per acre ≈ 25–30 min/acre of pure driving**, so realistically **~4–6 acres/day** after turns, stops and scan pauses. **[Analyst scenario]**

| Metric | Spraying drone (India) | AgriRover (ground) |
|---|---|---|
| What it does | Physically **sprays** | **Scouts / images** only (v1 spray subsystem is bench-only) |
| Service price | **₹350–450/acre** (some from ₹400) | scouting pass **₹387–1,599/acre-pass** (repo analyst est.) |
| Throughput | ~20 ac/day (Namo); 10–15 ac/hr commercial | **~4–6 ac/day** |
| Capital | ₹5–8 lakh+ (80% subsidy → ~₹1.6 lakh to SHG) | ₹27–50k build |

**Honest conclusion.** On **cost per acre for physical coverage the drone wins decisively** — it *sprays* a field for ₹350–450/acre while the rover merely *looks* at it for a similar-or-higher ₹/acre and ~4× slower. Cheap hardware (₹27–50k) does **not** translate to cheap per-acre service, because **throughput, not capital, sets the per-acre cost** (the route-density problem from the adoption dossier). The rover's **only** defensible niche is exactly where a drone physically cannot go: **close-range, under-canopy, per-plant / per-bunch / trap-level** inspection. It is not, and must not be pitched as, a cheaper sprayer. **[Analyst scenario]**

Sources for this section:
- `[S31]` Vigyan Varta — drone-as-service ₹350–450/acre; Kisan drone ~7–8 min/acre — http://www.vigyanvarta.in/adminpanel/upload_doc/VV_0526_22.pdf
- `[S32]` Namo Drone Didi — up to 20 acres/day; 80% subsidy up to ₹8 lakh/drone — https://www.nextias.com/ca/current-affairs/05-11-2024/namo-drone-didi-scheme
- `[S33]` Agridrone.io — spraying from ₹400/acre — https://www.agridrone.io/
- `[S34]` Ground UGV field speeds 0.6–1.0 m/s — https://www.mdpi.com/2073-4395/15/12/2793
- `[S35]` IIFL — agri-drone service startup ₹5–30 lakh — https://www.iifl.com/blogs/gold-loan/how-to-start-a-agri-drone-service-business

### v2.3 Cotton — pink bollworm, and why a fixed smart-trap beats the rover here
- **Problem & magnitude.** Pink bollworm (PBW, *Pectinophora gossypiella*) has evolved resistance to Bt cotton; field infestation **40–95%**, yield loss **20–30%**. **[External result]** `[S36]` Nationally, cotton has lost ~**20 lakh ha in six years** and production is **down 27%** from the 2013-14 peak. **[External result]** `[S37]` PBW is tied to acute distress in Vidarbha (Yavatmal: **800+ farmer suicides in 2.5 years**). **[External result]** `[S40]`
- **The decision variable is a trap count.** ICAR/CAI action thresholds are pheromone-trap based — **8 moths/trap/night over 3 nights** (recent work revises to 4.5–5.7), with **5 traps/ha** from August. **[External result]** `[S38]` PBW larvae live **inside the boll** — not imageable — so, like the tomato pinworm, the actionable signal is a **countable moth in a trap**, not a photo of the pest.
- **Rover/component fit — honest.** A trap is a **fixed point**: a **static AI smart-trap** (pheromone lure → sticky liner → camera → weather sensors) already exists in India and is cheaper than driving a rover to each trap. **[External result]** `[S39]` So for PBW a **fixed camera-trap beats a roving rover** — the rover only wins if it reads many farmers' traps on a dense route. RGB close-range *does* help the **visible** cotton problems (whitefly, leaf-curl virus, sucking-pest leaf damage). **Verdict: park PBW as a rover use-case; it favours a static smart-trap.** **[Analyst scenario]**

### v2.4 Banana — Panama wilt (rogue-mapping) and post-harvest
- **Problem & magnitude.** Panama/Fusarium wilt (*Foc*, incl. lethal **TR4**, in India since a 2017 UP report) causes **30–40% losses in India** (60–90% globally); it is **soil-borne, survives in soil for years, and spreads via infected planting material**. **[External result]** `[S41]`, `[S42]` Banana post-harvest loss runs **20–30%** (up to 30–40% farm-to-consumer). **[External result]** `[S43]`
- **Rover/component fit.** Wilt shows as **progressive leaf yellowing/wilting** — RGB can **map visibly infected plants** so they're rogued and spread contained (the core lever). Honest limits: it is a **root/vascular, soil-borne** disease, so RGB catches it only once symptoms show (often too late for that plant); true early detection needs multispectral/soil assays, not a cheap add-on. Post-harvest: RGB **bunch colour/ripeness grading** fits harvest-timing (as with grapes). **Verdict: rover fits roguing-map + harvest grading, not early wilt detection.** **[Analyst scenario]**

### v2.5 Farmer voice (from reportage, not video)
- Grape (Nashik, 2015): production cost **₹25/kg** but sold at **₹8–10/kg**; berry weight down **30–40%**; spraying expense up **~30%**. **[External result]** `[S44]`
- Grape (Nashik, 2025): a grower hit by the COVID price crash, then a 2023 hailstorm on a harvest-ready vineyard — "couldn't repay loan." **[External result]** `[S2]`
- Cotton (Vidarbha): a farmer, crop ruined, **drank pesticide**; carrying a ~₹20 lakh loan. **[External result]** `[S45]`
- Systemic: **Sahyadri Farms + IPH Pune** now run farmer **mental-health counselling** — growers cite unpredictable weather and rising input costs. **[External result]** `[S46]`
- **What this means for AgriRover:** the pain is **financial survival under input cost + weather + price volatility**, not a missing dashboard. Anything sold must cut a real ₹ cost or protect a real ₹ of yield — echoing the adoption dossier. **[Analyst scenario]**

Sources for these sections:
- `[S36]` Springer — PBW 40–95% infestation, 20–30% yield loss on Bt cotton — https://link.springer.com/article/10.1007/s12600-019-00738-x
- `[S37]` India Today — cotton lost ~20 lakh ha in 6 yrs, production −27% — https://www.indiatoday.in/science/story/bt-cotton-india-pink-bollworm-white-gold-gm-crops-mission-productivity-gene-editing-science-news-2910816-2026-05-13
- `[S38]` CAI/ICAR — PBW trap ETL 8 moths/trap/night ×3; 5 traps/ha — https://caionline.in/uploads/publications/doc/06_08-05-2018.pdf
- `[S39]` IndiaAI (aikosh) — AI smart pheromone trap for PBW — https://aikosh.indiaai.gov.in/home/use-cases/details/ai_smart_pheromone_trap_for_area_wide_pink_bollworm_management.html
- `[S40]` UNI India — Yavatmal 800+ farmer suicides in 2.5 yrs — http://www.uniindia.com/news/west/farmers-suicides-in-vidarbha-region/3932428.html
- `[S41]` IntechOpen — Panama wilt India 30–40% (world 60–90%) — https://www.intechopen.com/chapters/79683
- `[S42]` APSnet — first TR4 report in India (2017, UP) — https://apsjournals.apsnet.org/doi/10.1094/PDIS-07-18-1263-PDN
- `[S43]` Asian J. Hort. — banana post-harvest loss 20–30% — https://researchjournal.co.in/online/TAJH/TAJH%207(1)/7_A-9-12.pdf
- `[S44]` TOI 2015 — grape ₹25/kg cost vs ₹8–10/kg sale; weight −30–40% — https://timesofindia.indiatimes.com/city/nashik/Grape-growers-seek-subsidy-on-plastic-net-covers-from-state/articleshow/46913058.cms
- `[S45]` Indian Express — Vidarbha farmer drank pesticide amid ruined crop — https://indianexpress.com/article/india/india-others/amidst-his-ruined-crop-he-drank-pesticide/lite/
- `[S46]` Indian Express 2026 — Sahyadri Farms + IPH Pune farmer mental-health initiative — https://indianexpress.com/article/cities/pune/maharashtra-sahyadri-farms-iph-pune-farmer-mental-health-initiative-10813110-https-indianexpress-com-article-c-10813750/

### v2.6 Sugarcane — weak fit (tall dense canopy; the real problem is water, not scouting)
- **Problem & magnitude.** Sugarcane's dominant issue in Maharashtra is **water**: it occupies only ~**4–6%** of farmland but consumes ~**70%** of the state's irrigation water, uses **10–15× more water** than traditional crops, and ~**79.5%** of the state's cane grows in **drought-prone** regions. **[External result]** `[S49]` Disease: **red rot** (*Colletotrichum falcatum*), "the cancer of sugarcane," causes severe yield/quality loss and repeatedly breaks resistant varieties; **woolly aphid** (*Ceratovacuna lanigera*) has hit ~**1.32 lakh ha** across Maharashtra/Karnataka. **[External result]** `[S47]`, `[S48]`
- **Rover/component fit — honest and mostly negative.** (a) The biggest problem, **water over-use**, is a policy/irrigation-infrastructure issue, not something a scouting rover solves. (b) Cane grows **2–4 m tall with a dense closing canopy**, so a small ground rover can only scout **early season**; once the canopy closes it drives under a wall of cane with no useful view. (c) **Red rot is internal** (reddened internodes) with late external symptoms — RGB can't catch it early. (d) Woolly-aphid colonies sit **high on tall cane**, out of a ground rover's close-range view. **Verdict: weak fit — park sugarcane.** **[Analyst scenario]**

### v2.7 Chilli — pests too small for a drive-by camera (confirms the adoption dossier)
- **Problem & magnitude.** The invasive thrips **_Thrips parvispinus_** caused a 2021–22 outbreak with reported **80–100% yield loss** (official estimate **40–80%** across AP & Telangana); yields crashed from ~**25 quintals/acre to 3–4**, over **0.4 million ha** affected, worsened by leaf-curl virus. **[External result]** `[S50]`, `[S51]`, `[S52]`
- **Rover/component fit — honest and negative for direct detection.** Thrips and the leaf-curl "murda" **mites are sub-millimetre** — **not** resolvable by a drive-by RGB camera, and the invasive species makes an old image classifier unsafe (as the adoption dossier warned). Recommended monitoring is **coloured (blue) sticky traps** + terminal-leaf/flower tapping — a **fixed smart-trap** job, not a rover pass. **[External result]** `[S53]` RGB can at best **map already-curled/bronzed plants** (symptom, not pest, and late). **Verdict: park chilli for direct scouting; at most symptom-mapping.** **[Analyst scenario]**

Sources for these sections:
- `[S47]` ResearchGate — red rot, "the cancer of sugarcane" — https://www.researchgate.net/publication/333194052_A_Review_on_Red_Rot_The_Cancer_of_Sugarcane
- `[S48]` Springer — woolly aphid (*Ceratovacuna lanigera*) impact on sugarcane — https://link.springer.com/article/10.1007/s12355-008-0025-x
- `[S49]` TOI — sugarcane ~4–6% of land, ~70% of Maharashtra irrigation water — https://timesofindia.indiatimes.com/india/cane-crops-get-bulk-of-dam-water-industry-8/articleshow/50261163.cms · Copernicus EGU25 — 79.5% of cane in drought-prone regions — https://meetingorganizer.copernicus.org/EGU25/EGU25-925.html
- `[S50]` ResearchGate/IIHR — T. parvispinus 80–100% chilli yield loss (2021) — https://www.researchgate.net/publication/359108075_Dominance_of_invasive_species_Thrips_parvispinus_Karny_over_the_existing_chilli_thrips_Scirtothrips_dorsalis_Hood_on_chilli_in_the_southern_states_of_India
- `[S51]` TradeBrains/PTI — Govt: 40–80% chilli damage in AP & Telangana — https://tradebrains.in/features/rsq-chilli-crop/
- `[S52]` Reuters — chilli hit by thrips despite heavy pesticide; prices surge — https://www.reuters.com/world/india/red-chilli-pepper-prices-surge-crop-damage-top-exporter-india-2022-03-07/
- `[S53]` Plant Archives — blue sticky traps most effective for T. parvispinus — http://plantarchives.org/article/313-%20Evaluation%20of%20Coloured%20Sticky%20Traps%20for%20Thrips%20parvispinus%20(Karny)%20Management%20and%20Its%20Impact%20on%20Chilli%20Yield.pdf

### v2.8 Grape mildew economics (deepened) — the spray treadmill + resistance is the target
- **Spray load.** Downy mildew alone needs ~**7–8 fungicide sprays/season** (US benchmark); Indian grape POP schedules run from foundation pruning **through the monsoon**, with a decision-support system placing the first sprays **25–45 days after pruning**. **[External result]** `[S24]`, `[S56]` Tropical Indian table grape carries an even heavier total program across downy + powdery + pests (growers reported spraying cost up ~30% in a bad year, `[S44]`).
- **Why it never stops: resistance.** *Plasmopara viticola* is a **high-risk pathogen for fungicide resistance and has developed resistance to most fungicide classes** (the metalaxyl/phenylamide case is classic). **[External result]** `[S55]` Calendar spraying accelerates that treadmill.
- **What this means for the sensor node (§1.1).** A leaf-wetness + RH/temp forecast node earns its keep by **cutting unneeded sprays** (spray on risk, not calendar) — protecting both cost and the useful life of each chemistry. **Honest gap:** a clean *India ₹-per-season* spray total needs **local grower invoices** (manuals disagree, per §3.2); do not quote a single figure in a pitch. **[Analyst scenario]**

### v2.9 APEDA GrapeNet / Residue Monitoring Plan — the record must plug INTO an existing system
- **What already exists.** EU grape export is **permitted only with APEDA registration**, under a **Residue Monitoring Plan (RMP)** monitoring residues of **CIB&RC-permitted chemicals**, with **farmer + exporter registration, plot registration, inspection authorities, accredited-lab residue testing, and traceability** via the **GrapeNet** system; the trade notice ships per-chemical MRL annexures. **[External result]** `[S57]`, `[S7]`
- **Implication for AgriRover's "record" product.** The compliance apparatus is **already built** — GrapeNet already demands a spray diary, plot registration and lab residue tests. A rover-generated geotagged, timestamped treatment/PHI record therefore does **not create a new need; it can only make the existing GrapeNet record easier and more trustworthy to compile**. Residue itself stays a **lab test**, never rover-measurable. The exporter wedge (adoption dossier) holds — *sell a cleaner GrapeNet-ready evidence trail* — but it is an **integration into GrapeNet, not a standalone product**. **[Analyst scenario]**

### v2.10 Onion storage-monitoring node — cheap, viable, but a separate product (not the rover)
- **Problem.** ~**25–45%** of stored onion is lost, largely from **unmonitored temperature, humidity and rot-gas build-up**; low-cost IoT monitoring aims to cut this toward **15–20%**. **[External result]** `[S58]`, `[S59]`
- **BOM (indicative India prices) for one static node:**

| Part | Role | ₹ (indicative) |
|---|---|---|
| ESP32 dev board | MCU + WiFi | **₹250–400** `[S60]` |
| DHT22 (or SHT31) | temp / RH | ₹200–400 (SHT31 ₹700–1,200, `[S27]`) |
| MQ-135 (or MQ-137) gas sensor | rot / ammonia gases | ₹150–300 (MQ-137 ₹1,199, `[S28]`) |
| Relay module + fan | ventilation trigger | ₹150–400 |
| Enclosure, wiring, power | — | ₹300–500 |
| **Node total** | | **~₹1,050–2,500** (cheap build) |

- **Verdict.** A **~₹1–2.5k static node per chawl** is genuinely viable and cheap — but it is a **fixed storage sensor, not the field rover**. Treat it as an **adjacent product**, exactly as v1 §2 flagged. **[Analyst scenario]**

Sources for these sections:
- `[S55]` MDPI Microorganisms — *P. viticola* high-risk, resistant to most fungicide classes — https://www.mdpi.com/2076-2607/9/1/119
- `[S56]` MASU / Indian grape POP — DM spray schedule, first sprays 25–45 days after pruning — https://www.masujournal.org/107/lxjAVbDrcjXNomWCZcotEkXPG03InT.pdf
- `[S57]` APEDA — grape export procedure 2026 (APEDA registration + RMP + GrapeNet) — https://apeda.gov.in/sites/default/files/export_procedures/procedureforexportofgrapes_17Feb_2026.pdf · MRL annexure — https://apeda.gov.in/sites/default/files/export_procedures/Annexure_9_17012026.pdf
- `[S58]` IJARSCT — onion 25–40% lost from poor temp/humidity/gas monitoring — https://www.ijarsct.co.in/Paper36761.pdf
- `[S59]` arXiv — IoT onion storage (ESP32 + DHT22 + MQ-135 + UV-C), target 15–20% — https://arxiv.org/html/2601.10745v1
- `[S60]` Robocraze — ESP32 NodeMCU dev board ₹383 — https://robocraze.com/products/nodemcu-32-wifi-bluetooth-esp32-development-board30-pin

### v2 sources
- `[S26]` Flipkart, 0–32 °Brix handheld refractometers ₹859–1,283 — https://www.flipkart.com/real-instruments-0-32-brix-hand-refractometer-atc-measuring-fruits-wine-beer-sugars-manual-handheld/p/itme5b7738d9159a
- `[S27]` Evelta, Adafruit SHT31-D temp/RH module (~₹966) — https://evelta.com/2857-adafruit-sensirion-sht31-d-temperature-humidity-sensor/
- `[S28]` Robocraze, MQ-137 NH3 ammonia sensor ₹1,199 — https://robocraze.com/products/mq-137-nh3-gas-sensor-module
- `[S29]` ThinkRobotics, MLX90640 32×24 thermal camera ₹7,249–7,349 — https://thinkrobotics.com/products/mlx90640-ir-array-thermal-imaging-camera
- `[S30]` Industrial leaf-wetness sensors ~$45–139 (RS485) — https://www.accio.com/plp/leaf-wetness-sensor-price · research-grade METER PHYTOS 31 — https://metergroup.com/products/phytos-31/

---

## Sources
- `[S1]` NRCG/TOI, up-to-50% grape loss warning (2025) — https://timesofindia.indiatimes.com/city/pune/scientists-warn-of-50-drop-in-grape-yield-across-maharashtra-this-season/articleshow/124856506.cms
- `[S2]` TOI Nashik, farmers axe grapevines, 35–40→3–5 bunches — https://timesofindia.indiatimes.com/city/nashik/adverse-weather-hits-grape-dreams-hard-farmers-forced-to-axe-grapevines-in-nashik/articleshow/125031286.cms
- `[S3]` Livemint, wine prices +25–30% on crop damage — https://www.livemint.com/economy/wine-prices-maharashtra-grape-crop-damage-rainfall-vineyards-grape-exports-winemakers-11765167885235.html
- `[S4]` Fyllo, grape downy mildew (RH>85% + leaf wetness) — https://www.fyllo.in/solutions/grapes
- `[S5]` ET, EU chlormequat rejection ~₹273 cr loss — https://m.economictimes.indiatimes.com/news/economy/foreign-trade/indian-grapes-stuck-at-eu-ports-govt-to-take-steps-soon/articleshow/5934330.cms
- `[S6]` ET, EU chlormequat MRL 0.05 mg/kg — https://economictimes.indiatimes.com/news/economy/foreign-trade/eu-using-pesticide-content-as-trade-barrier-say-grape-farmers/articleshow/7518702.cms
- `[S7]` APEDA, grape export procedure / RMP / GrapeNet (2026) — https://apeda.gov.in/sites/default/files/export_procedures/procedureforexportofgrapes_17Feb_2026.pdf
- `[S8]` ResearchGate, post-harvest loss in grapes 8.23–16% (~223k t/yr) — https://www.researchgate.net/publication/311693568_Postharvest_losses_in_grapes_Indian_status
- `[S9]` PHT Net, ~30% F&V wasted (~40 Mt, ~US$13 bn), cold-chain gaps — https://www.phtnet.org/research/download/pdf/wz111.pdf
- `[S10]` Bharatnama (secondary), ~90% F&V moves without cooling — https://bharatnama.substack.com/p/why-90-of-indias-produce-still-moves
- `[S11]` TOI, Nashik grapes rot, no labour to harvest (2020) — https://timesofindia.indiatimes.com/city/mumbai/nashiks-grapes-rot-as-exports-to-eu-and-local-sales-grind-to-halt/articleshow/74877315.cms
- `[S12]` CSRBox (secondary/pitch), grape ~10 workers/acre — https://www.csrbox.org/company/pitch_idea_doc/1605860802Grape%20farm%20pitch%20Proposal%20.pdf
- `[S13]` Testbook (secondary), Thompson Seedless 18–22 °Brix maturity — https://testbook.com/question-answer/which-one-of-the-following-is-the-best-maturity-in--69ccfc4b69516332eafdffe9
- `[S14]` NHB, grape maturity TSS >17 °Brix — https://www.nhb.gov.in/pdf/fruits/grape/gra004.pdf
- `[S15]` Early downy/powdery detection via sensor nodes, 94.4%/96% — https://bibbase.org/service/mendeley/bfbbf840-4c42-3914-a463-19024f50b30c/file/58515b91-55fd-589b-5486-779c9a3662ea/1_s20_S2589721721000283_main.pdf.pdf
- `[S16]` MDPI Sensors, thermal imaging early downy detection — https://www.mdpi.com/1424-8220/22/9/3585
- `[S17]` MDPI Horticulturae, hyperspectral downy ~81% — https://www.mdpi.com/2311-7524/7/5/103
- `[S18]` MDPI Plants, downy forecasting (temp × leaf-wetness) — https://www.mdpi.com/2223-7747/11/14/1807
- `[S19]` ResearchGate, onion ambient storage losses up to 50% — https://www.researchgate.net/publication/303749496_Cold_storage_of_onion_and_garlic
- `[S20]` arXiv, onion 30–40% storage loss + IoT/UV-C — https://arxiv.org/html/2601.10745v1
- `[S21]` TOI, onion irradiation sprouting 0.3% vs 6.05% — https://timesofindia.indiatimes.com/city/nashik/Irradiation-can-save-42k-tonne-onions-Study/articleshow/51884540.cms
- `[S22]` Springer, pomegranate bacterial blight up to 80% loss — https://link.springer.com/chapter/10.1007/978-81-322-2571-3_11
- `[S23]` Fyllo, pomegranate blight 48–72 h forecast — https://www.fyllo.in/insights/usecase/bacterial-blight-pomegranate-control-iot-weather-station
- `[S24]` UMD Extension (US benchmark), 7–8 downy fungicide sprays/season — https://extension.umd.edu/resource/downy-mildew-management/
- `[S25]` TOI Hyderabad, vineyard cost ₹60k→₹4 lakh/acre — https://timesofindia.indiatimes.com/city/hyderabad/crushing-realty-squeezes-hyderabads-once-flourishing-vineyards/articleshow/132795365.cms
