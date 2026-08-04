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
