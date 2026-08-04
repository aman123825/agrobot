# Farmer Adoption and Problem Research — Why an Indian Smallholder Would Pay for AgriRover

**Buyer-side research dossier | 04-Aug-2026**
**First market focus: the tomato cluster around Narayangaon / Junnar, Pune district, Maharashtra**

> Purpose: establish, with India-specific rupee figures and cited sources, which
> real problems create willingness to pay for AgriRover; who actually signs the
> cheque; and what remains unproven. This document is deliberately harsher on
> AgriRover than any pitch deck.
>
> Companion documents: `research/AGRI_PROBLEMS_RESEARCH.md` (problem
> solvability catalog) and `research/AGRIROVER_MARKET_ADOPTION_RESEARCH.md`
> (commercial decision, provider economics, pilot gates). Where a claim already
> exists there with an evidence ID, that ID is reused (`[E01]`–`[E35]`).

## Evidence labels (identical scheme to `AGRIROVER_MARKET_ADOPTION_RESEARCH.md`)

- **[External result]** — measured or published by another organization. It
  validates a problem or a mechanism, never AgriRover's performance.
- **[Repository fact]** — present in this repository's code, BOM, deck or design
  documents. It is not proof that the physical rover works in a field.
- **[Analyst scenario]** — a transparent calculation used to make a decision. It
  is not a forecast and not a measured result.
- **[AgriRover target]** — a gate the product must pass before the claim may be
  used in a sales conversation.

**Standing caveat that applies to every line of this document:** AgriRover has
**no field-validation data**. No measured saving, yield effect, model accuracy on
local tomato classes, productive coverage rate, reliability figure,
willingness-to-pay result or payback exists. Every benefit below is an
**[AgriRover target]**, and every rupee benefit is an **[Analyst scenario]**
built on somebody else's **[External result]**.

---

## 1. Executive summary — the buying case in ten lines

1. Junnar/Narayangaon is a genuinely dense, commercially sophisticated tomato
   cluster: Narayangaon is described as the country's largest open tomato auction
   market, with cultivation having grown from 500 acres across 50 villages to
   2,200 acres across 150 villages around it, and peak arrivals of 50,000–60,000
   crates (20 kg) per day. **[External result]** ([SIBM Bengaluru JTFPC case study](https://www.sibmbengaluru.edu.in/wp-content/uploads/2023/08/4_Junnar-Taluka-Farmers-Producers-Company-Ltd.pdf), [TOI, Narayangaon APMC](https://timesofindia.indiatimes.com/city/pune/deluge-ravages-tomato-crops-in-junnar-and-ambegaon-supply-plummets-by-60/articleshow/132399448.cms), [eSakal, 27-Jun-2026](https://www.esakal.com/pune/tomato-prices-fall-in-narayangaon-as-sub-market-records-season-high-arrival-of-60000-crates-pjp78))
2. The money at stake per acre is large and mostly *already being spent*: local
   reporting puts one acre of Junnar tomato at about **₹1.5 lakh** of cultivation
   cost, of which the GIZ Maharashtra tomato manual budgets **₹17,000/acre** for
   plant protection (₹15,000 chemicals + ₹2,000 application). **[External result]** ([Lokmat Times](https://www.lokmattimes.com/maharashtra/junnar-tomato-prices-crash-from-rs900-to-rs150-per-crate-farmers-seek-government-support-a525/), [E02])
3. The loss it is spent against is real: fruit borer *Helicoverpa armigera*
   losses in Indian tomato are reported at 5–55% (commonly 22–38%); ICAR reports
   tomato pinworm *Tuta absoluta* can cause **up to 90%** yield/quality loss and
   it was first found in **Pune** in Oct 2014 with >50% of plants affected in
   several Maharashtra fields; tomato leaf-curl incidence is reported between
   17.6% and 99.7%. **[External result]** ([ICAR pest alert](https://icar.org.in/node/7571), [IntechOpen ToLCD review](https://www.intechopen.com/chapters/60615))
4. The behaviour that wastes that spend is calendar spraying rather than
   threshold-based decisions. ICAR-NRIIPM's tomato IPM demonstration at
   Annamayya recorded **7.33 vs 18.66 sprays**, **15.8% lower cultivation cost**
   and **₹2.25 lakh vs ₹1.35 lakh net return**, with IPM samples below detectable
   residues while farmer-practice samples carried four residues. **[External result]** `[E32]`
5. That is the headroom AgriRover is aiming at — **not** a new revenue stream.
   For the ₹3,600/acre sentinel package, savings-only break-even needs a
   **21.2%** reduction of the ₹17,000 protection budget. **[Analyst scenario]** (`AGRIROVER_MARKET_ADOPTION_RESEARCH.md` §3.2)
6. Scouting is the binding constraint: NIPHM's tomato package expects **weekly**
   surveillance at five spots × five plants, and the Maharashtra plant-protection
   wage is **₹582.10/day** (Jan 2026, Labour Bureau) with transplanting labour
   already reported at ₹500/day and ₹10,000–12,000/acre in Nashik. **[External result]** `[E26]`, `[E17]`, ([Indie Journal](https://www.indiejournal.in/article/labour-trouble-singes-onion-farmers-in-maharashtra))
7. Nobody in this cluster currently pays cash for *looking at plants*. Growers
   scout with family labour, or take free advice from the input dealer who earns
   on the chemical. **Any price for surveillance alone is a new line item in the
   grower's budget** — the hardest kind of sale. **[Analyst scenario]**
8. Price sensitivity is brutal because the alternative machine services are
   cheaper per pass: drone spraying is quoted at **₹400–800/acre** at 40–60
   acres/day, and a ministry estimate cited in a peer-reviewed review is
   **₹350–450/acre at ~30 acres/day**. A scouting-only rover pass that needs
   **₹800–950** to break even is priced *above* a service that physically sprays
   the field. **[External result]** ([AgriFarming rate survey](https://www.agrifarming.in/drone-spraying-cost-per-acre), `[E19]`) + **[Analyst scenario]**
9. Therefore the defensible buyer is **not** the individual smallholder paying
   ₹75k to own a rover. It is the **FPO/CHC or agronomy service** buying a
   route-dense cluster service, with the KVK as the trust anchor — 86.1% of
   Indian holdings are under 2 ha and average 1.08 ha, which makes individual
   ownership of unproved machinery structurally wrong. **[External result]** (`AGRI_PROBLEMS_RESEARCH.md` P12)
10. What must be sold in the pilot is therefore **evidence and accountability**,
    not hardware or hours: a repeatable, geotagged, expert-reviewed record of
    what was found, what was applied, at what pre-harvest interval, and whether
    it worked. Whether that changes a treatment, a cost, a grade or a yield in
    Junnar is **completely unproven** and is exactly what the pilot exists to
    measure. **[AgriRover target]**

---

## 2. Buyer personas — and who actually pays

| Persona | Who they are in Junnar | What they are optimizing | Pays cash? | What they will pay for |
|---|---|---|---|---|
| **A. Commercial tomato grower (1–5 acres)** | Staked, mulched, drip tomato; 2 crops/yr; sells at Narayangaon sub-market | Recovering a ~₹1.5 lakh/acre outlay before the price window shuts **[External result]** ([Lokmat](https://www.lokmattimes.com/maharashtra/junnar-tomato-prices-crash-from-rs900-to-rs150-per-crate-farmers-seek-government-support-a525/)) | Rarely, and only after seeing a neighbour's result | A cheaper or safer spray decision; nothing abstract |
| **B. FPO / producer company** | e.g. Junnar Taluka Farmers Producer Company — 1,600 members, promoted by SFAC and VGAI, built the Narayangaon wholesale tomato market **[External result]** ([SIBM case study](https://www.sibmbengaluru.edu.in/wp-content/uploads/2023/08/4_Junnar-Taluka-Farmers-Producers-Company-Ltd.pdf), `[E28]`) | Member retention, grade uniformity, input margin, machinery utilization | **Yes — the most likely first payer** | A cluster service with route density, member reporting and a defensible utilization story |
| **C. KVK / agronomist** | KVK Narayangaon (Junnar) — on-farm testing and training mandate `[E30]`; CoE Vegetables, Baramati `[E16]` | Scientific defensibility, advisory throughput, extension reach | **No — pays in credibility, not cash** | Data quality, sampling that matches NIPHM/AESA protocol, co-authorship of results |
| **D. Exporter / pack-house** | Grape and vegetable exporters under APEDA traceability; the Narayangaon pack-house/grading upgrade track **[External result]** ([HollandDoor](https://hollanddoor.nl/component/content/article/295-next-steps-in-the-development-of-the-tomato-area-in-narayangaon-india?Itemid=101&catid=77)) | Avoiding an RASFF rejection and the suspension ladder that follows | **Yes, for compliance — but not for tomato yet** | Plot-level, timestamped chemical/PHI records that survive an audit |
| **E. Input dealer** | Free advice, credit, product margin | Volume of chemical sold | No — **structurally a competitor** | Nothing; a threshold service reduces their volume |

**Conclusion on who pays.** The realistic v1 contract is **B pays, C validates,
A consents, D is a later adjacency, E resists.** Persona A's willingness to pay
is contingent and second-order; persona E is the incumbent advisor and will not
cooperate. Designing the pilot around persona A signing up individually is the
most likely way to fail. **[Analyst scenario]**

---

## 3. Problem catalog

Each entry: description → India-specific magnitude in ₹ with source → how
farmers cope today and what that costs → the exact gap AgriRover addresses, and
what it explicitly does not.

### 3.1 Farm fragmentation — why ₹7–17 lakh machines do not fit

**Description.** The plot, not the farmer's ambition, sets the price ceiling.

**Magnitude.** Agriculture Census 2015-16: **86.1% of holdings are under 2 ha**
(~126M of 146M); average holding **1.08 ha**, down from 2.28 ha in 1970-71;
marginal holdings average **0.38 ha**; NABARD puts the average at **0.74 ha** by
2021-22; NSS 77th round (2019) reports **89.4%** of agricultural households
owning under 2 ha. Small and marginal farms produce ~51% of output and ~70% of
high-value fruit and vegetables. **[External result]** (`AGRI_PROBLEMS_RESEARCH.md`
P12; [PIB](https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=1910357))

**How they cope and what it costs.** They hire, not own. Drone spraying is
quoted at **₹400–800/acre** service-only, with a **₹500–1,500 call-out minimum
below ~1.5 acres**, and 40–60 acres/day throughput. **[External result]**
([AgriFarming](https://www.agrifarming.in/drone-spraying-cost-per-acre)) A peer-reviewed
review cites a ministry estimate of **₹350–450/acre at about 30 acres/day**. `[E19]`
Autonomous field robots remain capital equipment: XMachines' Neo is announced at
**USD 19,995** (≈ ₹17–18 lakh at current rates), consistent with the ₹17 lakh
figure in this repository's competitor slide. **[External result]** ([agriaifarming
product page](https://agriaifarming.com/ai-farming-machines/xmachines-neo-autonomous-robot)) +
**[Repository fact]** (`AgriRover_Investor_Full.pptx`, per `PROJECT_AUDIT.md` §6)

**The gap AgriRover addresses.** A ₹41,150 planning-cost platform (₹34,800
CPU-only; ₹50,000 Groww Track A ceiling) is one to two orders of magnitude below
a robot and roughly a fifth of a ₹7–10 lakh drone system, so it can be justified
on a 1–2 acre plot's economics in a way those cannot. **[Repository fact]**
(`docs/BOM-top20-groww-trackA.md`)

**What it does not address.** Fragmentation also destroys *route density*, which
is the single biggest driver of AgriRover's own cost per pass. A cheap machine
crossing many tiny scattered plots can easily be more expensive per acre than an
expensive machine crossing few large ones. Cheap hardware is necessary and not
sufficient. **[Analyst scenario]** (§5.2–5.3 of the adoption research)

### 3.2 Pest and disease loss on tomato — and the ₹15,000+/acre it triggers

**Description.** Junnar tomato faces a stacked complex: fruit borer, the
invasive pinworm/leaf miner, whitefly-transmitted leaf curl, thrips, mites, and
early/late blight.

**Magnitude.**

| Pest / disease | Reported loss or incidence | Source |
|---|---|---|
| Fruit borer (*H. armigera*) | 5–55% yield loss; commonly cited 22–38%; up to 50–80% in severe unmanaged cases | **[External result]** (synthesis of Indian tomato entomology literature; see §9 note) |
| Tomato pinworm / leaf miner (*Tuta / Phthorimaea absoluta*) | **up to 90%** loss of yield and fruit quality; first detected **Pune, Oct 2014**; >50% of plants affected in several Maharashtra fields; now in Pune, Ahmadnagar, Dhule, Jalgaon, Nashik, Satara | **[External result]** ([ICAR](https://icar.org.in/node/7571), [EPPO](https://gd.eppo.int/reporting/article-4450)) |
| Tomato leaf curl (ToLCD, whitefly-vectored) | incidence/loss **17.6–99.7%**; summer-planted 6.4–52.2% vs winter 52.5–100%; **92.3%** loss when infected 30 days after transplanting | **[External result]** ([IntechOpen](https://www.intechopen.com/chapters/60615)) |
| Leaf curl + whitefly, Karnataka field epidemiology | 17–53% Jul–Nov rising to 100% Feb–May; cv. Pusa Ruby **50–70%** yield loss; strong correlation with whitefly counts | **[External result]** ([ICRISAT eprints](http://eprints.icrisat.ac.in/9294)) |
| Thrips (incl. invasive *T. parvispinus*) | official guide reports **50–80%** damage | **[External result]** `[E28]` |
| Early blight / late blight / leaf curl under an IPM schedule | late blight **−31.40%**, early blight **−41.17%**, leaf curl **−67.47%** vs control; yield 377.77 q/ha; incremental cost-benefit ratio **10.3** | **[External result]** ([PMHE journal](https://pmhe.in/index.php/pmhe/article/download/38/25/48)) |

**In rupees.** The GIZ Maharashtra tomato manual budgets **₹17,000/acre** of
plant protection — ₹15,000 chemicals + ₹2,000 application. `[E02]` Against the
locally reported **₹1.5 lakh/acre** total cultivation cost, protection is
roughly **11%** of outlay — and at two crops a year a 1-acre grower is spending
about **₹34,000/year** purely on crop protection. **[Analyst scenario]** from
`[E02]` + [Lokmat](https://www.lokmattimes.com/maharashtra/junnar-tomato-prices-crash-from-rs900-to-rs150-per-crate-farmers-seek-government-support-a525/)
(A Nagpur-district tomato economics study reports a much lower plant-protection
share — ₹3,918/ha, 2.65% of cost C3 of ₹147,394/ha — which shows how wide the
real spread is and why **local invoices, not manuals, must set the pilot
baseline**. **[External result]** ([Pharma Innovation, 2023](https://www.thepharmajournal.com/archives/2023/vol12issue4/PartO/12-4-108-313.pdf)))

**How they cope and what it costs.** Prophylactic tank mixes on a 7–10 day
calendar, escalated after any visible damage; advice from the seller of the
chemical. The cost is the full ₹15,000/acre chemical bill whether or not the
pest was above threshold.

**The gap AgriRover addresses.** A repeatable, geotagged sentinel sample plus
trap images at NIPHM's prescribed cadence, escalated to a triggered close-row
scan, so that a qualified agronomist decides from counts instead of the
calendar. `[E26]` **[AgriRover target]**

**What it does not address.** Borer larvae inside fruit, pinworm mines on the
underside of leaves, adult thrips and mites at sub-millimetre scale, and root or
vascular disease are **not** established as detectable by the current camera
geometry and models. This repository's own audit records that current models
cannot support crop advice and that launch-critical tomato classes need local
field data and held-out per-class validation. **[Repository fact]**
(`README.md`; `AGRIROVER_MARKET_ADOPTION_RESEARCH.md` §6.2)

### 3.3 Calendar spraying vs threshold IPM — waste, resistance, residue, PHI

**Description.** The waste is not the chemical price; it is the sprays that were
never needed and the resistance and residue they buy.

**Magnitude.** ICAR-NRIIPM Annamayya tomato: **7.33 vs 18.66 sprays**, **15.8%
lower cultivation cost**, 23.13 vs 21.84 t/acre, **₹2.25 lakh vs ₹1.35 lakh net
return**; in the paired Bulandshahr trial the IPM samples were below detectable
residue limits while farmer-practice samples carried **four** detected
fungicide/insecticide residues. `[E32]` **[External result]** Resistance in
*H. armigera*, whitefly and thrips is attributed in the literature specifically
to **prophylactic calendar spraying**, with weekly monitoring against Economic
Threshold Levels and chemical-group rotation as the recommended alternative.
**[External result]** (resistance-management synthesis; NCIPM/IRM guidance)
PPQS requires that label dose, crop stage, spray interval, maximum number of
sprays, equipment and **pre-harvest interval** all be respected. `[E34]`

**In rupees.** 11.33 avoided sprays and a 15.8% cost reduction is the *upper
benchmark* of a complete IPM programme. Applied naively to a ₹17,000/acre
protection budget it would be ~₹2,700/acre; applied to the whole ₹1.5 lakh/acre
cost base, 15.8% would be ₹23,700/acre. **Neither number belongs in a sales
conversation** — the Annamayya bundle included seed and soil biocontrol, barrier
and trap crops, 10–12 traps/acre, released parasitoids and farmer field schools.
Robotic surveillance was not part of it. **[Analyst scenario]** with a hard
warning attached.

**How they cope and what it costs.** They over-spray as insurance, which is
rational under uncertainty and is precisely what makes the spend addressable —
and what raises PHI and residue risk at harvest.

**The gap AgriRover addresses.** Threshold evidence + a timestamped treatment
and PHI record, then a verification pass. **[AgriRover target]**

**What it does not address.** AgriRover cannot legally or safely prescribe or
apply chemicals in v1. The repository already flags a label-compliance gate on
chemical advice and application, a spray subsystem that is bench/research-only,
a 500 ml tank suited only to spot treatment, and a **45× flow-configuration
conflict** still unresolved. **[Repository fact]** (`AGRIROVER_MARKET_ADOPTION_RESEARCH.md` §6.6–6.9)

### 3.4 Fertilizer applied blind, without NPK data

**Description.** Nutrient decisions are made from habit and dealer advice, not
measurement.

**Magnitude.** A nationally representative farmer sample found Soil Health Card
awareness at **82%**, but only **66%** could understand the recommendations and
only **48%** followed the recommended application rate. **[External result]**
([SHC scheme assessment](https://www.academia.edu/112536003/The_Soil_Health_Card_Scheme_in_India_Lessons_Learned_and_Challenges_for_Replication_in_Other_Developing_Countries))
A 2024-25 Haryana farm survey found SHC adopters apply less urea than
conventional practice but **still exceed recommended doses**. **[External result]**
([Indian Journal of Extension Education](https://epubs.icar.org.in/index.php/IJEE/article/view/165252))
India's NPK use ratio reached **8.2:3.2:1** against the 4:2:1 reference, with a
fertilizer subsidy bill of roughly **₹1.9 lakh crore** in 2025-26; SHC sampling
found **39%** of soils zinc-deficient and **64%** low in organic carbon.
**[External result]** (`AGRI_PROBLEMS_RESEARCH.md` P19–P20)

**How they cope and what it costs.** Uniform broadcast or fertigation schedules
across a heterogeneous plot; cost shows up as both wasted input and, at the
extreme, suppressed yield from imbalance.

**The gap AgriRover addresses — deliberately, almost none in v1.** This is the
most important honest line in this document. An independent CGIAR evaluation of
low-cost NPK probes found **poor R² and strong moisture dependence**. `[E10]`
The repository's first pilot therefore **explicitly does not use the low-cost
NPK probe to prescribe fertilizer**. **[Repository fact]** (`README.md`;
`AGRIROVER_MARKET_ADOPTION_RESEARCH.md` §6.3) The only defensible v1 role is to
log a *visible* deficiency symptom as a flag to **get a proper soil test** —
never a dose. **[AgriRover target]**

### 3.5 Labour scarcity and cost — why weekly scouting does not happen

**Description.** The task AgriRover replaces is exactly the task nobody can
staff.

**Magnitude.** NIPHM's tomato AESA package expects **weekly** surveillance with
five spots × five plants and pest-specific leaf, fruit, disease and trap
observations. `[E26]` The Maharashtra male plant-protection wage was
**₹582.10/day** in Jan 2026. `[E17]` In Nashik, onion transplanting wages rose
from **₹300 to ₹500/day** in one season, with transplanting alone costing
**₹10,000–12,000/acre**, growers cutting acreage from 3 acres to 1, and
substitution of Konkan labour with workers from MP and Nandurbar. **[External
result]** ([Indie Journal](https://www.indiejournal.in/article/labour-trouble-singes-onion-farmers-in-maharashtra),
[HT, Mar 2025](https://www.hindustantimes.com/cities/pune-news/farmers-blame-freebie-schemes-for-labour-shortage-rising-costs-in-rural-maharashtra-101742841368476.html))
Structurally, **34 million workers left agriculture** between 2004-05 and
2011-12, while agriculture still accounts for ~46% of the workforce (PLFS
2023-24: 46.1%). **[External result]** (`AGRI_PROBLEMS_RESEARCH.md` P9)

**How they cope and what it costs.** They skip protocol scouting. Family labour
does a casual walk-through; the dealer diagnoses from a photo or a plucked leaf.
A trained human scout doing one protocol round on one acre in 2–3 hours costs
about **₹150–220** at the ₹582/day wage — roughly **₹2,000–2,900 across a
13-week crop**. **[Analyst scenario]** from `[E17]`

**The gap AgriRover addresses.** Repeatable sampling at the same points, every
week, without asking a scarce worker to walk the rows. **[AgriRover target]**

**What it does not address — and the commercial trap.** Because growers pay
₹0 cash for scouting today, the ₹150–220/acre human figure is the *shadow* price
of the alternative, not a budget line AgriRover can capture. A rover pass that
needs ₹800–950 to break even is **4–6× the cost of a man walking the same acre**.
AgriRover cannot win on the cost of the walk. It can only win on the value of
the *record and the decision*. **[Analyst scenario]**

### 3.6 Climate stress — heat and erratic rain

**Description.** Both tails now hit the same cluster within one season.

**Magnitude.** Tomato reproduction collapses under heat: in an ICAR phytotron
study, fruit set was normal (>80%) at 20/24 °C and 22/26 °C night/day, fell to
**25–49%** at 24/32 °C for most genotypes, and **no genotype set fruit at
27/37 °C** except a tolerant line at 19%; day temperature ≥35 °C and night
≥26 °C are proposed as the screening thresholds, with >35 °C inducing flower
drop. **[External result]** ([Indian Journal of Agricultural Sciences](https://epubs.icar.org.in/index.php/IJAgS/article/view/38052),
[Plant Science Today](https://doi.org/10.14719/pst.9940))
On the rain side, Maharashtra reported crops on **14.44 lakh ha** damaged across
29 districts after the Aug 2025 rains, and separately sanctioned **₹337.41
crore** of compensation for unseasonal Feb–May rain damage across **1.87 lakh
ha** affecting **3.98 lakh farmers** — capped at SDRF/NDRF norms of about
**₹17,000/ha for up to 2 ha**. In Nashik, October 2025 rain damaged ~**45,000 ha**
of vineyards with an estimated **₹3,500 crore** loss. **[External result]**
([The Hindu](https://www.thehindu.com/news/national/maharashtra/crops-on-1444-lakh-hectares-damaged-by-heavy-rain-says-maharashtra-government/article70016983.ece),
[TOI compensation](https://timesofindia.indiatimes.com/city/kolhapur/state-approves-rs-337cr-in-compensation-to-rain-hit-farmers/articleshow/123003757.cms),
`AGRI_PROBLEMS_RESEARCH.md` P10)

**Directly in Junnar/Ambegaon.** IMD recorded **over 200 mm in 24 hours for four
consecutive days**; waterlogging triggered fungal and bacterial outbreaks;
Narayangaon APMC arrivals fell **50–60%** from a normal 50,000–55,000 crates/day
to ~25,000; a prominent Junnar grower estimated **half his crop lost**; traders
reported **10–20% of every consignment spoiling** before retail; and prices still
did **not** rise, staying at ₹200–400/crate because of out-of-state supply.
**[External result]** ([TOI](https://timesofindia.indiatimes.com/city/pune/deluge-ravages-tomato-crops-in-junnar-and-ambegaon-supply-plummets-by-60/articleshow/132399448.cms))

**How they cope and what it costs.** Preventive fungicide sprays that the same
report notes are impossible to apply during continuous rain; drainage; then a
compensation claim capped at ~₹17,000/ha on 2 ha against a ₹1.5 lakh/acre outlay
— i.e. compensation recovers on the order of **5%** of the cost of a 2-acre
tomato loss. **[Analyst scenario]**

**The gap AgriRover addresses.** Post-event condition evidence and disease-onset
timing that lets an agronomist prioritize which blocks to treat or harvest
first. **[AgriRover target]**

**What it does not address.** It cannot prevent heat or rain, cannot operate in a
waterlogged field, and has no validated maturity or yield map. Weather-triggered
harvest prioritization is listed in this repository as **research, not a
product**. **[Repository fact]**

### 3.7 Weak market access, price volatility, traceability and export compliance

**Description.** A better crop is not the same as a better price, and this
cluster's defining risk is the price, not the pest.

**Magnitude — volatility.** In the 2026 Junnar season, tomato moved from
**₹900/crate at the opening, to ₹600, to ₹150–300/crate**, against a stated
~**₹1.5 lakh/acre** cost — while a record **60,000 crates** arrived at the
Narayangaon sub-market in a single day. **[External result]** ([Lokmat Times](https://www.lokmattimes.com/maharashtra/junnar-tomato-prices-crash-from-rs900-to-rs150-per-crate-farmers-seek-government-support-a525/),
[eSakal](https://www.esakal.com/pune/tomato-prices-fall-in-narayangaon-as-sub-market-records-season-high-arrival-of-60000-crates-pjp78))
The 2023 cycle is the extreme case: Narayangaon wholesale peaked near
**₹3,200/crate** in July, Nashik mandis fell from **₹2,000 to ₹90/crate** in six
weeks, retail went from ~₹200 to ₹3–5/kg, and growers in **Junnar and Ambegaon
began abandoning plantations**; one Solapur grower destroyed 1.5 acres because
₹8,500 of harvest and transport could not be recovered. **[External result]**
([TOI](https://timesofindia.indiatimes.com/business/india-business/from-rs-200-to-rs-5-a-kilo-in-a-month-tomato-farmers-in-dire-straits/articleshow/103941812.cms))

**Magnitude — value-chain share.** RBI working-paper analysis puts the farmer's
share of the consumer rupee at **33% for tomato** (36% onion, 37% potato, 35%
grapes) against ~70% in dairy. **[External result]**
([Indian Express](https://indianexpress.com/article/business/economy/farmers-get-only-a-third-of-what-consumer-pays-for-vegetables-fruits-rbi-study-9607829/),
[BusinessLine](https://www.thehindubusinessline.com/economy/agri-business/rbi-study-tomato-onion-and-potato-farmers-get-only-a-third-of-retail-price/article68714566.ece))

**Magnitude — compliance.** APEDA's grape procedure runs plot-level traceability
through GrapeNet, requires the residue certificate within six days of sampling,
obliges the National Referral Laboratory to issue an internal alert within 24
hours of a failed sample, and escalates RASFF rejections: **1st** → warning and
a written explanation within seven days; **2nd** → **15-day suspension of the
exporter**. The EU audited India's residue controls for plant-origin exports as
recently as Oct 2024 (audit 2024-7978). Historically, the 2010 chlormequat
detections caused multiple container rejections of Maharashtra grapes and a
reported **~₹250 crore** loss. **[External result]** (`[E05]`, `[E06]`,
[APEDA procedure](https://apeda.gov.in/sites/default/files/export_procedures/procedureforexportofgrapes_30Jan_2025.pdf),
[EU audit record](https://ec.europa.eu/food/audits-analysis/audit-report/details/4870),
`AGRI_PROBLEMS_RESEARCH.md` P6)

**How they cope and what it costs.** They sell into the daily auction and accept
the print; on the export side they maintain records manually to satisfy
GrapeNet.

**The gap AgriRover addresses.** A per-plot, timestamped, geotagged record of
observation → treatment → PHI → verification is the exact artefact an
audit-driven chain needs, and it is the one output of AgriRover that has a buyer
with an existing budget and an existing legal obligation. **[AgriRover target]**

**What it does not address.** Nothing AgriRover does changes market-wide supply,
the auction price, the intermediary structure or the 33% share. Marketing this as
a fix for the tomato crash would be dishonest; the repository already classifies
the glut problem as **not core / research**. **[Repository fact]**

### 3.8 Post-harvest losses

**Description.** Loss concentrated at harvest and grading, not in transit alone.

**Magnitude.** NABCONS 2022 (MoFPI-commissioned; 54 commodities, 292 districts,
15 agro-climatic zones) puts national **tomato post-harvest loss at 11.61%** —
farm 8.37% + market 3.25% — with **sorting/grading alone at 3.1%** the single
largest loss operation and improper hand-plucking named as the harvesting
driver; national vegetable losses run 4.87–11.61% and fruit 6.02–15.05%, against
the older ICAR-CIPHET national figure of **₹92,651 crore/year**. **[External
result]** (`AGRI_PROBLEMS_RESEARCH.md` P2, P8) Locally, the deluge report puts
**10–20% of every consignment** spoiling before retail. **[External result]** (TOI)

**In rupees.** At a mid-season ₹600/crate and 11.61% loss, an acre yielding ~400
crates loses on the order of **₹27,800/acre** of gross value. **[Analyst
scenario]** — arithmetic only; loss share and yield are not locally measured.

**How they cope and what it costs.** Hand-plucking, ungraded or roughly graded
lots, immediate sale. The Narayangaon cluster is separately pursuing an
automated pack-house and grading centre, which is the correct fix and is **not**
a rover. **[External result]** (HollandDoor)

**The gap AgriRover addresses.** Only a narrow slice, and only hypothetically:
ripeness/maturity mapping to inform harvest sequencing. This repository rates it
**PARTIAL / RESEARCH** with no validated maturity model. **[Repository fact]**

**What it does not address.** Cold chain, pre-cooling, grading lines, packaging
and transport — i.e. the large majority of the loss.

---

## 4. Willingness to pay and unit economics

### 4.1 What a Junnar tomato grower actually spends today

| Line | ₹ per acre per crop | Label / source |
|---|---:|---|
| Total cultivation cost (local reporting) | ~150,000 | **[External result]** ([Lokmat](https://www.lokmattimes.com/maharashtra/junnar-tomato-prices-crash-from-rs900-to-rs150-per-crate-farmers-seek-government-support-a525/)) |
| Plant protection (GIZ Maharashtra manual) | 17,000 (15,000 chemical + 2,000 application) | **[External result]** `[E02]` |
| Plant protection (Nagpur economics study, cost C3) | ~1,586/acre (₹3,918/ha) | **[External result]** ([Pharma Innovation 2023](https://www.thepharmajournal.com/archives/2023/vol12issue4/PartO/12-4-108-313.pdf)) |
| Cash paid for scouting | **0** | **[Analyst scenario]** |
| Shadow cost of protocol human scouting, 13 weekly rounds | ~2,000–2,900 | **[Analyst scenario]** from `[E17]` |
| Drone spray service, per pass | 400–800 | **[External result]** (AgriFarming; `[E19]` ₹350–450) |

The ₹17,000 vs ₹1,586 spread between two published sources is the most important
uncertainty in this entire document. **The pilot must establish the local
protection spend from farmer invoices before any headroom claim is made.**
**[AgriRover target]**

### 4.2 Headroom against the ₹3,600/acre sentinel package

From `AGRIROVER_MARKET_ADOPTION_RESEARCH.md` §3.2, savings-only break-even needs
**21.2%** of the ₹17,000 budget avoided. **[Analyst scenario]**

| Share of protection budget avoided | Grower gross benefit | Net after ₹3,600 fee |
|---:|---:|---:|
| 10% | ₹1,700 | −₹1,900 |
| 15% | ₹2,550 | −₹1,050 |
| 20% | ₹3,400 | −₹200 |
| 30% | ₹5,100 | +₹1,500 |

If the true local spend is nearer the Nagpur study's ₹1,586/acre, **no plausible
saving percentage pays for any AgriRover package**, and the entire commercial
case must shift from cost saving to loss avoidance, grade or compliance. That is
a live possibility, not a remote one. **[Analyst scenario]**

### 4.3 Price sensitivity of the three deck options

The current canonical deck prices **₹75k own / ₹300 per acre-pass / ₹199 per
month**. **[Repository fact]** (`AgriRover_Investor_Full.pptx`, per
`PROJECT_AUDIT.md` §6)

**Option 1 — ₹75,000 to own.** Against a ₹41,150 planning BOM (plus ₹4,000–7,000
of durability upgrades), the hardware margin is plausible. The *farmer* case is
not. For a 1-acre grower with ₹34,000/year of protection spend across two crops,
a 20% saving is **₹6,800/year → an ~11-year simple payback**, on a machine with
a 3-year asset-life assumption in this repository's own model, no field
reliability data, and no service network. **Individual ownership fails on
arithmetic, not on price.** **[Analyst scenario]** + **[Repository fact]**

**Option 2 — ₹300 per acre-pass.** Already retired inside this repository. At a
fully loaded **₹1,119/rover-day**, ₹300/acre requires **3.73 productive acres/day**
to cover direct cost, and **11.19 acres/day** once a ₹200/pass support allowance
is included. Deep scans need **₹800–950/pass** with break-even at 1.86 acres/day
(₹800) or 1.49 acres/day (₹950). **[Analyst scenario]** (§5.1–5.3) The
competitive problem is now unavoidable: **₹800–950 for a scouting pass sits above
the ₹400–800 that a drone charges to actually spray the acre.** Growers will
compare those two numbers directly.

**Option 3 — ₹199 per month.** ₹2,388/year. A weekly visit implies ~4.3
visits/month, i.e. **~₹46 per visit** against a ₹1,119 rover-day. Even at an
optimistic 4 acres/day, direct cost is ₹280/pass. **₹199/month cannot fund
physical visits at any credible density.** It is defensible only as a
**data/advisory subscription layered on top of separately priced visits**, and
must be repositioned or withdrawn. **[Analyst scenario]**

### 4.4 The FPO view, which is the one that matters

At 100 active days/year and 2.5 productive acres/day, a single rover yields ~250
acre-passes/year; at ₹800/pass that is **₹200,000 of revenue** against ~₹112,000
of direct rover-day cost plus ₹50,000 of support at the planning allowance —
thin, and only positive **if** 2.5 acres/day and contiguous village routing are
both achieved. Neither has been measured. **[Analyst scenario]** ICRISAT's
synthesis of custom-hiring centres records exactly the failure mode to avoid:
**underutilization plus maintenance and operator constraints.** `[E15]`
**[External result]**

### 4.5 Honest ranking of what a buyer would pay for first

1. **Exporter/pack-house compliance records** — existing budget, existing legal
   obligation, existing audit ladder. Highest willingness to pay per unit of
   proof. **[Analyst scenario]**
2. **FPO cluster surveillance with agronomist review** — plausible, contingent
   on route density and a KVK endorsement.
3. **Grower-paid savings package** — weakest, because the saving is contested,
   the baseline is unmeasured and the competing service is cheaper per pass.
4. **Grower-paid ownership at ₹75k** — not viable on current arithmetic.

---

## 5. Why current alternatives fail them — and where the alternatives win

| Alternative | Cost to the grower | Where it fails him | Where it beats AgriRover today |
|---|---|---|---|
| **Own eyes / family labour** | ₹0 cash | Not protocol-based, not weekly, not recorded, no trend, no residue/PHI defence | Free, instant, trusted, needs no charging or network — **the true incumbent** |
| **Input dealer advice** | ₹0, embedded in chemical margin | Advisor is paid on volume; drives calendar spraying, resistance and residue risk | Credit, availability, relationship, same-day product |
| **Hired scout** | ~₹582/day; ~₹150–220 per acre-round `[E17]` | Scarce; wage rising ₹300→₹500/day in nearby districts; inconsistent counts | 4–6× cheaper per pass than a break-even rover pass |
| **Spray drones (Marut ~₹7–10 lakh capital)** | ₹400–800/acre service; ₹350–450/acre at ~30 acres/day in a ministry estimate | Sprays but does not *diagnose*; canopy penetration and small-plot call-out minimums (₹500–1,500) | 40–60 acres/day throughput, visible output, and SMAM subsidy of 40–75% plus the Namo Drone Didi channel `[E19]`, `[E35]` |
| **Autonomous robots (XMachines ~₹17 lakh; Neo at USD 19,995)** | Capital cost 35–40× AgriRover's BOM | Unaffordable for 86% of holdings; needs plot scale AgriRover's target customer does not have | Proven multi-operation payload, tilling/mowing/transport, commercial support |
| **Public surveillance systems (NPSS, CROPSAP/HORTSAP)** | Free to the farmer | Depends on extension-worker visits, not per-plot continuous evidence | **Free, official, at scale** — NPSS covers 73 crops and 436 pests with 10,000+ extension workers; HORTSAP covered 6,58,838 ha across 30 districts including tomato, issuing 20,885 advisories in 2024 `[E22]`–`[E24]` |

**The uncomfortable conclusion.** AgriRover's cheapest competitor is free
(family eyes, dealer advice and a government advisory app), and its most
expensive competitor delivers more visible work per rupee (drones). Positioning
must therefore be **evidence + accountability + verification**, aimed at a buyer
who needs a *record*, not at a grower who needs a *look*. **[Analyst scenario]**

---

## 6. What would actually make them buy

### 6.1 Decision triggers, by persona

| Persona | The trigger that opens the wallet |
|---|---|
| Grower | A neighbour on the same variety and planting week visibly skipped sprays and got the same or a better lot at the same auction |
| FPO | A route-dense package that fills a rover's day inside 2–3 villages, plus a member-level report they can show at the AGM, plus a maintenance answer |
| KVK / agronomist | Sampling that matches the NIPHM AESA protocol (five spots × five plants, pest-specific observations) and counts that agree with their own manual counts `[E26]` |
| Exporter | One audit or RASFF near-miss. The APEDA ladder — warning on the 1st rejection, 15-day suspension on the 2nd — converts records into insurance |

### 6.2 Trust signals, in the order they are actually weighed

1. **A local institutional name.** KVK Narayangaon or CoE Vegetables Baramati
   co-signing the observation protocol. `[E30]`, `[E16]` Research on AI-adoption
   barriers in Indian agriculture identifies **trust and language** as critical.
   `[E21]` **[External result]**
2. **Marathi voice output and a callback**, not a dashboard.
3. **A neighbour's field, this season, same variety.**
4. **A visible, boring reliability record** — passes completed vs passes
   attempted, published without editing.
5. **An explicit list of what the rover cannot see.** Naming the blind spots
   (borer inside fruit, mites, roots) buys more credibility than any accuracy
   number.

### 6.3 The proof each persona needs before paying

| Persona | Minimum acceptable proof | Status |
|---|---|---|
| Grower | Paired plots, same variety/planting week, showing either fewer sprays at equal grade or fewer plants lost | **Does not exist** |
| FPO | Measured productive acres/day, cost per pass, and utilization over a season | **Does not exist** |
| KVK | Rover counts vs expert counts, per class, on held-out local data | **Does not exist**; repository states models cannot support crop advice `[Repository fact]` |
| Exporter | A record set that passes a mock APEDA/GrapeNet audit | **Not built**; ISOXML export is a prototype `[Repository fact]` |

---

## 7. Objections and honest rebuttals

**"A man can walk my field for free."**
Correct, and today he does. AgriRover is not selling the walk; it is selling the
same five spots, on the same day of every week, counted the same way, geotagged,
with the treatment and PHI recorded and a verification pass afterwards. Whether
that record is worth cash in Junnar is unproven. **[AgriRover target]**

**"A drone costs ₹400–800/acre and actually sprays."**
Also correct, and a scouting pass that needs ₹800–950 to break even is a worse
deal per pass on its face. The honest answer is that they are complements — the
rover is a decision and record layer that could reduce the number of drone or
knapsack passes bought — and that the rover's price must fall through route
density before it can be sold beside a drone. **[Analyst scenario]**

**"Government advisories are free and already cover tomato."**
True: NPSS spans 73 crops and 436 pests with 10,000+ extension workers, and
HORTSAP covered 6,58,838 ha including tomato with 20,885 advisories in 2024.
`[E22]`–`[E24]` AgriRover must be positioned as a per-plot evidence feed that a
credentialed expert uses inside that system, not as a competitor to it — and
this repository records that **no public API or integration access exists**.
**[Repository fact]**

**"₹15,000/acre of chemical is not real on my farm."**
Possibly right. Published Maharashtra tomato figures range from ₹17,000/acre
(GIZ) to ~₹1,586/acre (Nagpur study). AgriRover must baseline from the grower's
own invoices, not a manual. **[AgriRover target]**

**"Will it survive my field, and who fixes it?"**
Unknown. The repository budgets ₹4,000–7,000 for a durability upgrade, uses a
3-year/100-active-days asset assumption, and has no field reliability data. Any
availability promise today would be invented. **[Repository fact]**

**"Prices crashed from ₹900 to ₹150 a crate — how does a robot help?"**
It does not. The 2026 Junnar collapse and the 2023 ₹3,200→abandonment cycle were
market events. Yield forecasting is classified in this repository as **not core /
research**. Claiming otherwise would be dishonest. **[Repository fact]**

**"Just tell me the fertilizer dose."**
It will not. Independent evaluation of low-cost NPK probes found poor R² and
moisture dependence, so the first pilot deliberately excludes fertilizer
prescription. `[E10]`, **[Repository fact]**

**"There's a 40–75% subsidy on drones — get one for the rover."**
SMAM eligibility is conditional on testing and empanelment, not automatic, and
`AGRIROVER_MARKET_ADOPTION_RESEARCH.md` §8.4 is explicit that subsidy is not the
launch strategy. `[E14]` **[External result]** + **[Repository fact]**

---

## 8. Evidence gaps — what AgriRover must prove before any claim is used

| # | Gap | Why the sale is blocked without it | Gate |
|---|---|---|---|
| 1 | **Local protection-spend baseline** from ≥12 growers' invoices (chemical, application, labour, per crop) | The entire headroom argument swings between ₹1,586 and ₹17,000/acre | **[AgriRover target]** |
| 2 | **Per-class detection accuracy on local tomato data**, held out, agreed against KVK expert counts | Repository states current models cannot support crop advice | **[AgriRover target]** |
| 3 | **Productive acres/day**, measured with travel, setup, failed missions and weather included | Every price in §4 depends on it; ₹800/pass needs 1.86 acres/day | **[AgriRover target]** |
| 4 | **Timed agronomist review minutes and real overhead per pass** | The ₹100/₹200/₹300 support allowances are assumptions, not observations | **[AgriRover target]** |
| 5 | **Did the evidence change a treatment?** Paired plots vs expert-led IPM *without* the rover | Otherwise AgriRover is claiming credit for IPM itself, as at Annamayya | **[AgriRover target]** |
| 6 | **Season-long reliability and availability** — passes completed / attempted, MTBF, repair time | FPOs buy uptime; ICRISAT documents CHC failure via maintenance `[E15]` | **[AgriRover target]** |
| 7 | **Row navigation, not GPS** — NEO-6 is specified at 2.5 m (2.0 m SBAS) `[E11]` | Repeatable sentinel points need better-than-row accuracy | **[AgriRover target]** |
| 8 | **Label/PHI compliance workflow** signed off before any chemical guidance `[E34]` | Advising a dose without this is a legal exposure | **[AgriRover target]** |
| 9 | **Willingness-to-pay evidence** — a booked, paid repeat order, not a stated intention | No WTP result exists in any form | **[AgriRover target]** |
| 10 | **Flow-configuration conflict (45×) and the 500 ml tank scope** resolved on the bench | Blocks any application claim | **[Repository fact]** to close |

**Until gates 1–5 close, the only defensible sales sentence is:** *"We produce a
repeatable, geotagged, expert-reviewed record of what is in your field, what was
applied and whether it worked. We have not yet proved it saves you money, and
we are running the pilot that will tell us."*

---

## 9. Sources list with labels

### External results — Junnar / Narayangaon cluster specific
- **[External result]** [Lokmat Times — "Junnar Tomato Prices Crash: From ₹900 To ₹150 Per Crate"](https://www.lokmattimes.com/maharashtra/junnar-tomato-prices-crash-from-rs900-to-rs150-per-crate-farmers-seek-government-support-a525/): ₹900 → ₹600 → ₹150–300/crate; ~₹1.5 lakh/acre cultivation cost. *Limit: newspaper report; a single season and a grower-stated cost.*
- **[External result]** [eSakal, 27-Jun-2026](https://www.esakal.com/pune/tomato-prices-fall-in-narayangaon-as-sub-market-records-season-high-arrival-of-60000-crates-pjp78): record 60,000 crates at Narayangaon sub-market. *Limit: one day's arrival.*
- **[External result]** [Times of India — Junnar/Ambegaon deluge](https://timesofindia.indiatimes.com/city/pune/deluge-ravages-tomato-crops-in-junnar-and-ambegaon-supply-plummets-by-60/articleshow/132399448.cms): >200 mm/24 h for four days; arrivals 50,000–55,000 → ~25,000 crates; 10–20% consignment spoilage; ₹200–400/crate. *Limit: trade estimates, not audited.*
- **[External result]** [Times of India — "From Rs 200 to Rs 5 a kilo"](https://timesofindia.indiatimes.com/business/india-business/from-rs-200-to-rs-5-a-kilo-in-a-month-tomato-farmers-in-dire-straits/articleshow/103941812.cms): Narayangaon ₹3,200/crate peak; Nashik ₹2,000 → ₹90/crate; Junnar/Ambegaon abandonment. *Limit: 2023 event.*
- **[External result]** [SIBM Bengaluru — Junnar Taluka Farmers Producer Company case study](https://www.sibmbengaluru.edu.in/wp-content/uploads/2023/08/4_Junnar-Taluka-Farmers-Producers-Company-Ltd.pdf): 1,600 members; largest open tomato auction market; 500 acres/50 villages → 2,200 acres/150 villages. *Limit: business-school case study, undated growth figures.*
- **[External result]** [HollandDoor — Narayangaon tomato area development](https://hollanddoor.nl/component/content/article/295-next-steps-in-the-development-of-the-tomato-area-in-narayangaon-india?Itemid=101&catid=77): planned pack-house with automated sorting/grading. *Limit: consultancy page; area figure not reconciled with official statistics.*
- **[External result]** `[E25]` [Horticultural Statistics at a Glance 2024](https://agriwelfare.gov.in/Documents/HORTICULTURAL_STATISTICS_AT_A_GLANCE_2024.pdf): Maharashtra tomato 55,227 ha / 1,332,085 t; Pune 4,772 ha.
- **[External result]** `[E28]`, `[E30]` MSAMB Junnar Taluka FPC profile; [KVK Narayangaon](https://www.kvknarayangaon.in).

### External results — pest, disease and IPM
- **[External result]** `[E32]` [ICAR-NRIIPM Annual Report 2024, pp. 26–27](https://nriipm.res.in/NCIPMPDFs/AnnualReport/AR-2024.pdf): tomato IPM 7.33 vs 18.66 sprays; 15.8% lower cost; ₹2.25 lakh vs ₹1.35 lakh net; Bulandshahr residue comparison. *Limit: AP/UP full-bundle IPM, not a rover effect.*
- **[External result]** [ICAR — *Tuta absoluta* invasive pest alert](https://icar.org.in/node/7571) and [EPPO Reporting Service 2015/024](https://gd.eppo.int/reporting/article-4450): up to 90% loss; first found Pune, Oct 2014; >50% plants affected in several Maharashtra fields.
- **[External result]** [IntechOpen — Tomato leaf curl disease in India](https://www.intechopen.com/chapters/60615): incidence/loss 17.6–99.7%; summer 6.4–52.2% vs winter 52.5–100%; 92.3% loss at 30 DAT infection.
- **[External result]** [ICRISAT eprints — TLCV epidemiology, southern India](http://eprints.icrisat.ac.in/9294): 17–53% Jul–Nov, up to 100% Feb–May; Pusa Ruby 50–70% yield loss; whitefly correlation.
- **[External result]** [PMHE — IPM schedule for tomato diseases](https://pmhe.in/index.php/pmhe/article/download/38/25/48): late blight −31.40%, early blight −41.17%, leaf curl −67.47% vs control; 377.77 q/ha; ICBR 10.3.
- **[External result]** *H. armigera* tomato loss range 5–55%, commonly 22–38%, up to 50–80% unmanaged — **synthesis across Indian tomato entomology literature via search aggregation; the underlying primary papers were not opened and must be cited individually before use in any deck.** *Flagged as the weakest citation in this document.*
- **[External result]** `[E26]` [NIPHM AESA tomato package](https://niphm.gov.in/IPMPackages/Tomato-R.pdf); `[E31]` [IPM Schedule for Vegetables](https://agritech.tnau.ac.in/horticulture/pdf/tech_bulletin/national/IPM-Schedule-for-vegetables.pdf); `[E28]` [PPQS *Thrips parvispinus* guide](https://ppqs.gov.in/sites/default/files/south_east_asian_thrips_thrips_parvispinus-monitoring_and_management.pdf) (50–80% damage).
- **[External result]** `[E34]` [PPQS safe and judicious use of pesticides](https://ppqs.gov.in/divisions/integrated-pest-management/instruction-safe-use-pesticide?language_content_entity=en): label dose, intervals, maximum sprays, PHI.
- **[External result]** Insecticide-resistance management synthesis for *H. armigera*, whitefly and thrips: resistance attributed to prophylactic calendar spraying; weekly ETL monitoring and group rotation recommended. *Limit: search-aggregated synthesis of IRM guidance; cite NCIPM/ICAR primary documents before external use.*

### External results — costs, labour, nutrients, climate, market
- **[External result]** `[E02]` [GIZ Good Agricultural Practices in Tomato Cultivation, Maharashtra, 2024](https://2023.snrd-asia.org/wp-content/uploads/2024/03/Good-agricultural-practices-in-Tomato-Cultivation-%E2%80%93-A-technical-manual-for-Maharashtra.pdf): ₹15,000 chemicals + ₹2,000 application per acre.
- **[External result]** [Pharma Innovation 2023 — Economics of tomato production, Nagpur district](https://www.thepharmajournal.com/archives/2023/vol12issue4/PartO/12-4-108-313.pdf): cost C3 ₹147,394/ha; plant protection ₹3,918/ha (2.65%); yield 245.57 q/ha. *Limit: Nagpur, 2021-22; contradicts the GIZ budget.*
- **[External result]** `[E17]` [Labour Bureau Rural Wages](https://labourbureau.gov.in/rural-wages): Maharashtra male plant-protection worker ₹582.10/day, Jan 2026.
- **[External result]** [Indie Journal — labour trouble, Maharashtra onion](https://www.indiejournal.in/article/labour-trouble-singes-onion-farmers-in-maharashtra): ₹300 → ₹500/day; ₹10,000–12,000/acre transplanting; acreage cut 3 acres → 1. *Limit: onion transplanting in Nashik, not tomato scouting in Junnar.*
- **[External result]** [Hindustan Times, Mar 2025 — labour shortage in rural Maharashtra](https://www.hindustantimes.com/cities/pune-news/farmers-blame-freebie-schemes-for-labour-shortage-rising-costs-in-rural-maharashtra-101742841368476.html).
- **[External result]** [SHC scheme assessment — lessons and challenges](https://www.academia.edu/112536003/The_Soil_Health_Card_Scheme_in_India_Lessons_Learned_and_Challenges_for_Replication_in_Other_Developing_Countries): 82% aware, 66% understood, 48% followed the recommended rate.
- **[External result]** [Indian Journal of Extension Education — SHC impact on urea use, Haryana 2024-25](https://epubs.icar.org.in/index.php/IJEE/article/view/165252): adopters use less urea but still exceed recommended doses. *Limit: Haryana paddy/wheat, not Maharashtra tomato.*
- **[External result]** `[E10]` [CGIAR low-cost NPK probe evaluation, 2025](https://cgspace.cgiar.org/bitstreams/fe955214-2ee7-490a-9f63-1d5a7fa09f96/download): poor R², moisture dependence.
- **[External result]** [Indian Journal of Agricultural Sciences — high day/night temperature regimes on tomato](https://epubs.icar.org.in/index.php/IJAgS/article/view/38052): fruit set >80% at 22/26 °C, 25–49% at 24/32 °C, none at 27/37 °C except 19%; ≥35 °C day / ≥26 °C night screening thresholds. *Limit: phytotron, five genotypes.*
- **[External result]** [Plant Science Today — predicting tomato yield under heat stress](https://doi.org/10.14719/pst.9940): optimum 25–30 °C day / 20 °C night; >35 °C reduces fruit set and induces flower drop. *Limit: Tamil Nadu modelling study.*
- **[External result]** [The Hindu — 14.44 lakh ha damaged, Aug 2025](https://www.thehindu.com/news/national/maharashtra/crops-on-1444-lakh-hectares-damaged-by-heavy-rain-says-maharashtra-government/article70016983.ece).
- **[External result]** [Times of India — ₹337.41 crore compensation](https://timesofindia.indiatimes.com/city/kolhapur/state-approves-rs-337cr-in-compensation-to-rain-hit-farmers/articleshow/123003757.cms): 1.87 lakh ha; 3.98 lakh farmers; SDRF/NDRF ~₹17,000/ha capped at 2 ha.
- **[External result]** [RBI study via Indian Express](https://indianexpress.com/article/business/economy/farmers-get-only-a-third-of-what-consumer-pays-for-vegetables-fruits-rbi-study-9607829/) and [BusinessLine](https://www.thehindubusinessline.com/economy/agri-business/rbi-study-tomato-onion-and-potato-farmers-get-only-a-third-of-retail-price/article68714566.ece): farmer's share 33% tomato, 35% grapes, vs ~70% in dairy.
- **[External result]** `[E05]`, `[E06]` and [APEDA grape export procedure, Jan-2025 edition](https://apeda.gov.in/sites/default/files/export_procedures/procedureforexportofgrapes_30Jan_2025.pdf): GrapeNet traceability; residue certificate within six days; 24-hour NRL alert; RASFF ladder — warning on 1st, 15-day suspension on 2nd.
- **[External result]** [European Commission audit 2024-7978, India, pesticide residue controls](https://ec.europa.eu/food/audits-analysis/audit-report/details/4870): EU audit of Indian residue controls for plant-origin exports, Oct 2024.
- **[External result]** [AgriFarming — drone spraying cost per acre in India](https://www.agrifarming.in/drone-spraying-cost-per-acre): ₹400–800/acre service-only; 40–60 acres/day; ₹500–1,500 call-out minimum. *Limit: aggregator survey of operator quotes, not an official tariff.*
- **[External result]** `[E19]` [Peer-reviewed review of Indian agricultural drones](https://pmc.ncbi.nlm.nih.gov/articles/PMC12349003): ministry estimate ₹350–450/acre at ~30 acres/day.
- **[External result]** [XMachines Neo product coverage](https://agriaifarming.com/ai-farming-machines/xmachines-neo-autonomous-robot) and [XMachines](https://www.xmachines.ai/): Neo announced at USD 19,995. *Limit: third-party product page; verify against an Indian quotation.*
- **[External result]** `[E14]` [SMAM 2025 Guidelines](https://farmech.dac.gov.in/Content/New_Folder/SMAM-2025.pdf); `[E35]` [Namo Drone Didi operational guidelines](https://farmech.dac.gov.in/Content/New_Folder/Operational_Guidelines_of_Namo_Drone_Didi_Scheme.pdf).
- **[External result]** `[E15]` [ICRISAT Scale-Appropriate Mechanization review](https://oar.icrisat.org/13437/1/Scale%20Appropriate%20Mechanization%20Report-%2014012026_Revised.pdf): CHC underutilization, maintenance and operator constraints.
- **[External result]** `[E22]`–`[E24]` [NPSS user manual](https://npss.dac.gov.in/app/assets/files/NPSS_User_Manual_English.pdf), [PIB NPSS update 24-Jul-2026](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2289031) (73 crops, 436 pests, 10,000+ extension workers), [ICAR-NRIIPM database and networking](https://nriipm.res.in/databasenetworking.aspx) (HORTSAP 6,58,838 ha, 30 districts, tomato included, 20,885 advisories in 2024).
- **[External result]** `[E21]` [AI adoption barriers in Indian agriculture](https://ideas.repec.org/a/igg/jide00/v12y2021i3p30-44.html): trust and language critical.
- **[External result]** `[E11]` [u-blox NEO-6 datasheet](https://content.u-blox.com/sites/default/files/products/documents/NEO-6_DataSheet_%28GPS.G6-HW-09005%29.pdf): 2.5 m, SBAS 2.0 m.
- **[External result]** Post-harvest and fragmentation figures reused from `research/AGRI_PROBLEMS_RESEARCH.md` P2, P6, P8, P9, P12, P19, P20 — NABCONS 2022 (MoFPI), ICAR-CIPHET 2015, Agriculture Census 2015-16 / NABARD / NSS 77th, SHC nutrient status, NPK ratio and fertilizer subsidy, and the 2010 EU chlormequat grape rejections (~₹250 crore). *Limit: see that document's per-problem source lists and verdicts.*

### Repository facts
- **[Repository fact]** `README.md`: dual-controller architecture; Narayangaon/Junnar tomato crop-protection hypothesis; **first pilot keeps pesticide application manual and does not use the low-cost NPK probe to prescribe fertilizer**; launch-critical tomato classes still need local field data and held-out per-class validation.
- **[Repository fact]** `docs/BOM-top20-groww-trackA.md`: planned hardware total **₹41,150**; CPU-only scout **₹34,800**; Groww Track A ceiling **₹50,000**; unallocated ₹8,850.
- **[Repository fact]** `docs/farmer-needs-and-durability.md`: durability upgrade **₹4,000–7,000** on top of the BOM.
- **[Repository fact]** `PROJECT_AUDIT.md` §6: `AgriRover_Investor_Full.pptx` is canonical and carries the **₹75k own / ₹300 per acre-pass / ₹199 per month** pricing plus the XMachines ₹17 L and Marut ₹7–10 L comparison.
- **[Repository fact]** `research/AGRIROVER_MARKET_ADOPTION_RESEARCH.md` §6.1–6.9: product not field-proven; models cannot support crop advice; NPK must not prescribe; GPS is not row navigation; throughput needs a physical path calculation; 500 ml tank is spot-treatment only; **45× flow-configuration conflict**; rupee-savings tracker mixes incompatible units; chemical advice needs a label-compliance gate.
- **[Repository fact]** `research/AGRI_PROBLEMS_RESEARCH.md` final catalog: tomato glut is **not core / research**; post-harvest and maturity mapping are **partial / research**.

### Analyst scenarios (all derived, none measured)
- **[Analyst scenario]** ₹1,119 fully loaded rover-day; ₹100/₹200/₹300 per-pass support allowances; ₹300/acre break-even at 3.73 acres/day direct and 11.19 acres/day with support; ₹800/pass break-even at 1.86 acres/day; ₹950/pass at 1.49 acres/day — all from `AGRIROVER_MARKET_ADOPTION_RESEARCH.md` §5.1–5.3.
- **[Analyst scenario]** ₹3,600/acre sentinel package needs 21.2% of a ₹17,000 protection budget avoided (§3.2).
- **[Analyst scenario]** ₹34,000/year protection spend for a 1-acre two-crop grower; 20% saving → ₹6,800/year → ~11-year payback on ₹75,000.
- **[Analyst scenario]** ₹199/month ≈ ₹46 per weekly visit against a ₹1,119 rover-day, therefore not a visit product.
- **[Analyst scenario]** Human protocol scouting ≈ ₹150–220 per acre-round, ₹2,000–2,900 per 13-week crop, at the ₹582.10/day wage.
- **[Analyst scenario]** ~₹27,800/acre of gross value at an 11.61% tomato post-harvest loss on ~400 crates at ₹600 — arithmetic only.
- **[Analyst scenario]** ~250 acre-passes per rover-year at 100 days × 2.5 acres/day; ₹200,000 revenue at ₹800/pass.
- **[Analyst scenario]** SDRF compensation of ~₹17,000/ha capped at 2 ha recovers on the order of 5% of a 2-acre tomato loss at ₹1.5 lakh/acre.

### AgriRover targets (nothing here is proven)
Local protection-spend baseline from invoices; per-class detection accuracy vs
KVK expert counts; measured productive acres/day; timed review minutes and true
overhead; a paired-plot test isolating the rover's effect beyond expert-led IPM;
season-long reliability and availability; row-level navigation accuracy;
label/PHI compliance workflow sign-off; a booked and paid repeat order as the
only acceptable willingness-to-pay evidence; and a mock APEDA-style audit passed
on the record set.

---

**Status:** buyer-side research complete for the Junnar/Narayangaon tomato
wedge. No claim in this document may be used in a sales conversation or deck
without its label, its source and its stated limit. The two weakest citations —
the aggregated *H. armigera* loss range and the aggregated resistance-management
synthesis — are flagged in §9 and must be replaced with opened primary papers
before external use.
