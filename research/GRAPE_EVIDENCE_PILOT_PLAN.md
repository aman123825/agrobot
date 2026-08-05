# AgriRover — Grape Export-Evidence Pilot Plan (the #1 wedge, made actionable)

**04-Aug-2026 | derived from `GRAPE_AND_CROP_PROBLEM_SCAN.md` §v3.14–v3.15 and `AGRIROVER_MARKET_ADOPTION_RESEARCH.md`**

> This turns the research conclusion into a plan you can start next week. It is deliberately **cheapest-first**: three of the earliest gates need only interviews, audited accounts and a GPS walk — **no hardware, no capital**. If any early gate fails, you stop before spending on a build.

## 1. The one hypothesis under test
> *A solvent, audit-obligated grape buyer (exporter / pack-house / large FPO) will **pay** for a rover-generated, geotagged, agronomist-signed **treatment + pre-harvest-interval (PHI) evidence record** that plugs into their existing **APEDA GrapeNet / Residue Monitoring Plan** workflow.*

**Why this and not the others:** the scan showed the rover's two "obvious" plays are already taken by better-funded incumbents — **Niqo** (₹350/acre physical spot-spray) and **Fyllo** (one fixed weather station covering 100+ acres). The **only non-contested ground** is close-range, per-plant *evidence + traceability*, which neither a spray robot nor a point-station produces. **[Analyst scenario]**

**What would falsify it (be honest and look for these):** exporters already get compliant records cheaply from their own agronomists; or they won't pay a separate line item; or route-density makes the ₹/acre-pass exceed the value.

## 2. Stage 0 — desk gates (Week 1–2, ~₹0, no hardware)
Do these before building anything. Any red → stop or re-scope.

| Gate | How to check | Pass criterion |
|---|---|---|
| **A payer exists** | Interview 3–5 Nashik grape exporters / pack-houses (and 1–2 large FPOs, e.g. Sahyadri-type) | ≥ 2 say a cleaner GrapeNet-ready evidence record is worth paying for, and name a ₹ |
| **Payer is solvent** | Pull the target FPO/exporter's audited turnover (MCA filings) | Turnover supports a paid season (adoption dossier flagged JTFPC at ~₹1.19 L FY22 — disqualified) |
| **Route density is viable** | GPS-walk 1–2 candidate clusters; measure plots/km² and drive-time | A realistic ~4–6 ac/day gives a ₹/acre-pass **below** the payer's stated willingness |
| **Records aren't already free** | Ask what GrapeNet spray-diary/record they compile today and its pain | There is real, paid-worthy friction in their current record-keeping |

## 3. Stage 1 — minimum build + partner (Week 3–6)
Only if Stage 0 passes.
- **Rover capability (not a new build):** existing chassis + RGB close-range row scan + GPS geotag + timestamp. **No spraying. No Brix claim.**
- **Record template:** product, active ingredient, dose, water, plot, date, operator, **PHI** — mapped to the APEDA GrapeNet / RMP fields (`GRAPE_SCAN §v2.9`).
- **Agronomist partner (critical):** a licensed agronomist signs the recommendation/record — **not the company** (see `LEGAL_QUESTIONS.md`; keeps liability off you). This is the product, per the adoption dossier — the rover is the cheap part.
- **Optional add-on:** leaf-wetness + SHT31 node (**₹4,400–12,800**, corrected price `§v2.1`) only if the payer values a disease-risk map too.

## 4. Stage 2 — field pilot (Week 7–14)
- **Scope:** 1 committed buyer + **8–12 grower plots** on one dense route.
- **Loop:** weekly close-range scan → geotagged images + any visible lesions → agronomist review → treatment/PHI record → verification revisit.
- **Numeric kill-gates:**
  - **Route density:** ≥ target ac/day at ₹/acre-pass below the buyer's willingness.
  - **Record acceptance:** buyer QA accepts **≥ 90%** of records into their GrapeNet/RMP file unedited.
  - **Value:** measurable reduction in rejected-consignment risk or audit/record-keeping time vs the buyer's baseline.
  - **Willingness to renew:** buyer commits to pay for a second cluster/season.

## 5. Cost (pilot, indicative)
| Item | ₹ (indicative) |
|---|---|
| Rover (existing BOM) | 27,000–50,000 |
| Optional leaf-wetness + RH node | 4,400–12,800 |
| Agronomist time (season, partnered) | to negotiate |
| Field logistics (transport, one route) | modest |
| **Farmer-paid** | **₹0 — pilot-funded, never charge the grower** (WTP ~₹14.89/acre, adoption dossier) |

## 6. Who does what (team, from the roster)
- **Vivek** — electronics/firmware/AI: scan capture + geotag + record pipeline.
- **Hitanshu / Shreyash** — chassis/field ruggedness for the route.
- **Pritish** — dashboard + the record/report the buyer sees.
- **External** — one licensed agronomist (signs records); one KVK Narayangaon contact (scientific credibility, not cash).

## 7. What needs YOUR real-world input (I can't get these from a desk)
1. Which exporter / pack-house / FPO to approach first (a warm intro beats cold).
2. Budget ceiling for the pilot.
3. Whether an agronomist partner is available to sign records.
4. Go-ahead to contact KVK Narayangaon.

## 8. Honest risks (carried from the research)
- **Legal:** signed advisories create liability under a label-locked regime — keep the agronomist as signer; open `LEGAL_QUESTIONS.md` **before** charging (`[G23]`).
- **Competitor squeeze:** if the buyer already gets records via Fyllo/agronomist cheaply, the wedge narrows — Stage 0 must confirm real willingness to pay.
- **Throughput:** the rover is slow (~4–6 ac/day); route density is the make-or-break cost driver.

**Bottom line:** the first ₹0 of this plan (interviews + accounts + a GPS walk) can kill or greenlight the whole venture before a single new part is bought. Start there.
