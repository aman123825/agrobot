# Farmer Adoption and Problem Research — Why an Indian Smallholder Would Pay for AgriRover

**Buyer-side research dossier | v2, deep-research revision | 04-Aug-2026**
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

## What changed in v2 (deep-research revision)

This revision was commissioned to go deeper than the first pass and to close the
two citations the v1 document itself flagged as weakest. New evidence carries
IDs **`[F01]`–`[F24]`** to keep it separable from the inherited `[E..]` ledger.
The material findings of this revision, in order of how much they change the
commercial conclusion:

1. **Measured willingness to pay for plant-protection advice in India is
   ₹14.89 per acre** — not per pass, not per month — against a mean ₹18.10/acre
   for a full composite advisory bundle, with only 61.11% of farmers willing to
   pay anything at all. `[F01]` This is roughly **1/50th** of the ₹800–950 a
   deep scan must earn, and it is the single most damaging number in this
   dossier. §4.6 is new and built entirely around it.
2. **The presumed first payer may be insolvent.** Junnar Taluka Farmers Producer
   Company — 1,600 members, the FPO that built the Narayangaon market — shows
   operational revenue of the order of **₹1.19 lakh in FY22** in filings, and
   nationally only about **one-third of ~33,000 registered FPOs are financially
   viable**, with as few as **2% of surveyed FPOs running a custom-hiring
   centre**. `[F02]`, `[F03]` §4.7 is new.
3. **A direct competitor already prices below AgriRover while doing more work.**
   Niqo Robotics runs a village-level-entrepreneur model at **₹300–500/acre for
   AI spot-spraying with no software subscription**, and Fyllo/Fasal sell
   sensor-plus-advisory at roughly **₹400–750/month**. `[F04]`, `[F05]` §5 is
   rewritten around this.
4. **The `H. armigera` loss range is now properly sourced** — 5–55%, ~35%
   overall, 37.79% Karnataka, 31.53% avoidable loss in a Rajasthan
   protected-vs-unprotected trial, 22–38% commonly reported. `[F06]` The v1
   "weakest citation" flag on this item is retired.
5. **Resistance-management guidance is now attributed** to the ICAR/NCIPM window
   strategy — economic injury thresholds, weekly scouting of 50 plants,
   chemical-group rotation, explicit rejection of calendar spraying. `[F07]`
   The second v1 "weakest citation" flag is retired.
6. **Public extension barely reaches anyone, and dealers dominate.** Public
   extension including KVKs reaches **under 10%** of agricultural households
   while input dealers and progressive farmers reach **20–34%**; only 40–50%
   receive any technical advice at all. Maharashtra's agriculture department is
   carrying about **8,953 vacancies, ~32–33% of sanctioned strength**. `[F08]`,
   `[F09]` This is a new problem entry (§3.9) and it cuts both ways: it is the
   gap AgriRover exploits *and* the reason the KVK trust anchor has thin
   capacity to lend.
7. **Threshold literacy, not sensing, is the binding IPM constraint.** The
   documented barriers to IPM adoption are ignorance of the Economic Threshold
   Level concept itself, unavailability and short shelf life of bio-inputs,
   labour intensity, and dealer-side marketing pressure. `[F10]` A rover that
   supplies counts into a system where nobody knows what to do with counts
   solves the wrong half of the problem.
8. **New problem entries added:** spurious pesticides at 25–30% of the market
   `[F11]`, applicator health cost `[F12]`, farm-household debt and cash
   constraint `[F13]`, digital-access ceiling `[F14]`, and crop insurance as an
   existing competing risk product `[F15]`.
9. **New negative competitive evidence:** Namo Drone Didi drones are reported
   idle for transport, battery, service and maintenance reasons — the same
   failure mode AgriRover would face, now observed in a subsidised national
   programme. `[F16]`
10. **Export compliance is quantified.** India led RASFF in 2025 with **124
    pesticide-related notifications**, and 365 Indian products were flagged
    May-2024 to May-2026. `[F17]` This strengthens the one persona with a real
    budget — and it is still not tomato.

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

## 1. Executive summary — the buying case in fourteen lines

*Lines 1–10 are the v1 case. Lines 11–14 are the v2 findings that materially
change the conclusion; read them before acting on lines 1–10.*

1. Junnar/Narayangaon is a genuinely dense, commercially sophisticated tomato
   cluster: Narayangaon is described as the country's largest open tomato auction
   market, with cultivation having grown from 500 acres across 50 villages to
   2,200 acres across 150 villages around it, and peak arrivals of 50,000–60,000
   crates (20 kg) per day. **[External result]** ([SIBM Bengaluru JTFPC case study](https://www.sibmbengaluru.edu.in/wp-content/uploads/2023/08/4_Junnar-Taluka-Farmers-Producers-Company-Ltd.pdf), [TOI, Narayangaon APMC](https://timesofindia.indiatimes.com/city/pune/deluge-ravages-tomato-crops-in-junnar-and-ambegaon-supply-plummets-by-60/articleshow/132399448.cms), [eSakal, 27-Jun-2026](https://www.esakal.com/pune/tomato-prices-fall-in-narayangaon-as-sub-market-records-season-high-arrival-of-60000-crates-pjp78))
    *v2 caveat:* more recent estimates put the area **as high as 10,000 acres**,
    and no official hectare series could be located; the Junnar (Narayangaon) APMC
    modal price was **₹1,500/quintal (₹15/kg)** on 22-Jul-2026. `[F23]` The
    **2,200 vs 10,000 acre spread is unreconciled**, and since it spans ~4.5× it
    cannot be used to estimate **route density — the single biggest driver of
    AgriRover's cost per pass** (§3.1, §4.4). Cluster density must be measured on
    the ground, not inferred from press figures. **[AgriRover target]**
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

### The four v2 findings that change the conclusion

11. **The measured price of advice is ₹14.89/acre.** A published Indian
    extension study puts willingness to pay for *plant-protection information*
    at **₹14.89/acre**, weather at ₹15.98, market at ₹14.80, and a composite
    bundle at **₹18.10/acre**, with **only 61.11%** willing to pay anything.
    `[F01]` **[External result]** AgriRover's deep scan needs ₹800–950. The gap
    is not a discount away; it is **~50×**. Information alone has no market at
    AgriRover's cost. Whatever is sold must be *liability transfer, a physical
    act, or an audit artefact* — not a number a farmer could have guessed.
12. **The FPO's balance sheet may not support the purchase.** Only ~1/3 of
    ~33,000 registered FPOs are financially viable; **2% of surveyed FPOs run a
    CHC**; and JTFPC itself shows operational revenue of the order of **₹1.19
    lakh in FY22**. `[F02]`, `[F03]` **[External result]** The v1 conclusion
    "the FPO is the first payer" survives only as *the least-bad payer*, and the
    pilot must qualify the specific FPO's audited turnover before designing a
    price around it. **[AgriRover target]**
13. **A cheaper competitor already does more.** Niqo Robotics: **₹300–500/acre,
    AI spot-spray, no subscription, VLE-operated**; Fyllo/Fasal: **₹400–750/month**
    for sensors plus advisory. `[F04]`, `[F05]` **[External result]** AgriRover's
    scouting-only pass is priced above a service that sprays, and its ₹199/month
    tier is priced below firms that ship a physical sensor. It is currently
    squeezed from both sides.
14. **The honest v2 position.** The defensible wedge narrows to **one sentence**:
    a *per-plot, timestamped, expert-signed residue-and-PHI record for a buyer
    with an audit obligation*, with cluster surveillance for an FPO as the second
    option and grower-paid scouting effectively dead at current cost. India led
    RASFF in 2025 with **124 pesticide notifications** `[F17]`, which is where the
    money and the fear both are. **[Analyst scenario]**

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
| Fruit borer (*H. armigera*) | **5–55%** yield loss; **~35%** overall and **37.79%** in Karnataka; **31.53% avoidable** quantitative loss (unprotected vs protected plots, Rajasthan); **22–38%** commonly reported | **[External result]** `[F06]` — *v1's flagged weak citation now resolved to specific studies* |
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
fungicide/insecticide residues. `[E32]` **[External result]**

**Resistance — now properly attributed.** ICAR/NCIPM insecticide-resistance
management guidance for *H. armigera* and *Bemisia tabaci* explicitly **rejects
calendar-based spraying** and prescribes instead: economic injury thresholds,
**weekly scouting of 50 plants**, rotation of insecticide chemical groups,
"window strategies" that rotate chemistries by season and pest stage, delaying
early-season foliar sprays via systemic seed treatment, and **not repeating the
same chemical class after a control failure**. `[F07]` **[External result]**
*This retires v1's second flagged weak citation.* Note the number: the official
scouting unit is **50 plants weekly**, against NIPHM's tomato AESA five spots ×
five plants (25 plants). `[E26]` A robotic sample must be reconciled to whichever
protocol the local KVK actually endorses, and the two are not the same.

**Thresholds are specific and low, which is the real product spec.** For the
tomato pinworm the published action thresholds are **20–30 moths/trap/week** for
intervention, or **10 moths/trap/week** to trigger azadirachtin, using **10–12
pheromone traps/acre** for monitoring and mass trapping. `[F18]` **[External
result]** These are *trap counts*, not leaf-image classifications — which is a
significant and under-appreciated point for AgriRover's design: **the decision
variable the protocol actually uses is a countable insect in a trap**, a far
easier machine-vision target than a mine on the underside of a leaf.

**How often this actually reaches the produce — and why it cuts both ways.**
Under FSSAI's national monitoring programme, **86,401 food samples were analysed
between 2022 and 2025, with 2.8% exceeding notified MRLs**, and tomato appears
consistently among the vegetables with frequent residue detections alongside
brinjal, okra, cabbage and cauliflower. `[F22]` **[External result]** *Limit: the
2.8% aggregate spans all commodities; this dossier could not isolate a
tomato-specific Maharashtra violation rate.*

Two consequences pull in opposite directions and both must be stated. The residue
problem is **real and officially measured**, which supports §3.7's compliance
thesis. But a ~2.8% violation rate also means **roughly 97% of samples already
pass** — so for a grower selling into Narayangaon, "avoid an MRL breach" is a
low-probability event and therefore a weak reason to buy anything. The buyer who
pays for residue assurance is the one for whom a single breach is *catastrophic*
rather than merely unlikely: an exporter facing a border rejection and the
suspension ladder behind it `[F17]`, not a domestic-market grower. This is the
sharpest available argument for why AgriRover's compliance product must be sold to
persona D and not persona A. **[Analyst scenario]**

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

**The barrier is threshold literacy, not sensing — and this is the deepest
problem in the dossier.** Documented constraints on IPM adoption in India are, in
order: **lack of knowledge of the Economic Threshold Level concept itself** and
inability to identify pests and natural enemies; **unavailability and short shelf
life** of pheromone traps, trichocards and bio-agents; **high upfront cost and
labour intensity** of IPM operations, worsened by the wage spiral; **aggressive
chemical-pesticide marketing and supply chains** creating systemic bias; and
**risk aversion** — a preference for known chemical reliance over the perceived
complexity and uncertain outcome of IPM, especially with no market premium for
lower residue. `[F10]` **[External result]**

Read that list against AgriRover's value proposition and the conclusion is
uncomfortable: **AgriRover supplies counts into a decision system whose binding
constraint is that nobody knows what to do with counts, cannot buy the bio-inputs
the count would call for, has no price incentive to use them, and is being
actively marketed against.** A count is only worth money if a competent decision
and an available input sit behind it. That means the *agronomist review layer and
input logistics are not an add-on to AgriRover — they are the product*, and the
rover is the cheapest part of it. Any pilot that ships sensing without a
contracted agronomist and an input-supply answer is testing the wrong hypothesis.
**[Analyst scenario]**

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

### 3.9 The advice vacuum — who the farmer actually listens to (new in v2)

**Description.** AgriRover's real competitor is not a machine. It is the person
who currently answers the question "what should I spray?".

**Magnitude.** NSSO-based analysis finds only **40–50%** of agricultural
households access *any* technical advice. Of those who do, **input dealers and
progressive farmers each reach roughly 20–34%**, while **public extension —
government extension workers and KVKs together — reaches under 10%**. `[F08]`
**[External result]** The supply side explains it: the Maharashtra agriculture
department is recruiting for about **8,953 vacant posts, roughly 32–33% of
sanctioned strength**, with the shortage concentrated in Group C — precisely the
agricultural assistants and village-level field staff who would do farmer-facing
scouting; the state has separately announced **Shetkari Mitra Bharti 2026** for
over **11,000** village-level assistants. `[F09]` **[External result]**

**How they cope and what it costs.** They ask the dealer, who is paid on volume.
The cost is invisible because it is embedded in the chemical margin — and it is
the mechanism that produces the calendar spraying in §3.3 and the resistance in
§3.2. Free advice from an interested party is the most expensive advice in the
budget.

**The gap AgriRover addresses.** A disinterested, evidence-backed second opinion
in a market where the only available opinion is sold by the seller. This is the
strongest *narrative* AgriRover has, and it is genuinely well evidenced.
**[AgriRover target]**

**What it does not address — and the trap.** The same statistic that creates the
opportunity destroys the trust anchor. **§6.2 of this document rests the entire
credibility strategy on a KVK endorsement, and KVKs reach under 10% of
households.** `[F08]` A KVK signature is scientifically necessary and
commercially thin: it convinces an agronomist and a grant committee, not a
village. The trust route that actually has reach is the **progressive farmer**
(20–34%), which argues for a demonstration-farmer strategy alongside — not
instead of — the KVK. Note also that the ~11,000 new Shetkari Mitra posts, if
filled, are a **state-funded substitute** for the human half of AgriRover's
service, arriving free. **[Analyst scenario]**

### 3.10 Spurious and substandard pesticides (new in v2)

**Description.** A threshold-based recommendation assumes the product in the can
is the product on the label.

**Magnitude.** FICCI and Tata Strategic Management Group estimates put
counterfeit and spurious pesticides at **25–30% of the Indian pesticide market by
volume**, growing ~20% a year, contributing an estimated **4% crop-yield
reduction** and about **10.6 million tonnes** of lost produce annually. `[F11]`
**[External result]** *Limit: industry-association estimates, repeatedly recycled
in trade press; the underlying methodology is not public and the projections are
dated. Treat the direction as sound and the precision as unreliable.*

**How they cope and what it costs.** They buy on dealer trust and re-spray when a
product "does not work" — which is indistinguishable, from the farmer's chair,
from resistance or from a wrong diagnosis. On a ₹15,000/acre chemical budget, a
25–30% spurious share implies of the order of **₹3,750–4,500/acre** of spend with
uncertain active ingredient. **[Analyst scenario]** — share applied to budget,
arithmetic only; no local product-testing data exists.

**The gap AgriRover addresses.** Something genuinely useful and under-exploited:
a **before/after verification pass** turns "the spray failed" from an argument
into a measurement. Over a season, per-product efficacy evidence across many
plots is an asset neither the dealer nor the farmer currently possesses, and it
is a plausible reason for an FPO to fund the service — it protects the FPO's own
input-procurement decisions.

**What it does not address.** AgriRover cannot assay a chemical. It can only
observe that pest pressure did not fall after an application, which has at least
four competing explanations (spurious product, resistance, wrong diagnosis, bad
application). Attributing failure to counterfeiting on rover evidence alone would
be indefensible. **[AgriRover target]**

### 3.11 Applicator health cost (new in v2)

**Description.** Someone walks into the crop with a knapsack, and that has a
measurable cost that never appears in a cost-of-cultivation table.

**Magnitude.** In Yavatmal, Maharashtra, the 2017–18 episodes produced thousands
of acute poisoning cases with the state's highest death and hospitalisation
counts; drivers were absence of protective equipment, spraying above head height
and early re-entry into treated fields; families reported private medical costs
**sometimes exceeding ₹1 lakh**. `[F12]` **[External result]** The repository's
own catalog already carries pesticide-applicator exposure as **P1, VERIFIED**.
**[Repository fact]** (`AGRI_PROBLEMS_RESEARCH.md` P1)

**How they cope and what it costs.** They spray anyway, usually without PPE,
often hiring the poorest available labour to do it.

**The gap AgriRover addresses.** Two honest ones. Fewer *necessary* sprays means
fewer exposure events — an outcome the grower does not pay for but an FPO, a
donor, a CSR programme or a state scheme plausibly would. And a **timestamped
re-entry-interval record** addresses the specific documented driver of early
re-entry, using the same PHI plumbing already required for §3.7.

**What it does not address.** AgriRover does not spray in v1 — application stays
manual by design **[Repository fact]** (`README.md`) — so it removes no exposure
directly. Any exposure-reduction claim is entirely contingent on the unproven
spray-reduction claim, and stacking one unproven claim on another is exactly what
§8 exists to prevent. **[AgriRover target]**

### 3.12 The cash constraint — debt, income and why ₹75,000 is not a price (new in v2)

**Description.** Whether the grower *should* buy is a different question from
whether he *can*.

**Magnitude.** NSS 77th round (2018-19 agricultural year): average monthly income
per agricultural household **₹10,218**, average outstanding debt **₹74,121**, with
**50.2%** of agricultural households indebted. NABARD NAFIS 2021-22: average
monthly income **₹13,661** for agricultural households, and the share of rural
households reporting outstanding debt up to **52.0%** from 47.4% in 2016-17.
`[F13]` **[External result]**

**In rupees, and this is the arithmetic that ends the ownership option.**
AgriRover's ₹75,000 own-it price is approximately **5.5 months of total household
income** at the NAFIS figure, and it is **slightly more than the average
household's entire outstanding debt** (₹74,121). **[Analyst scenario]** A
₹3,600/acre season package is **~26% of one month's household income** for a
one-acre grower. Even the ₹199/month tier is a recurring commitment for a
household where half the peer group is already carrying debt.

**How they cope and what it costs.** They buy inputs on dealer credit and settle
after the auction — which is also the mechanism that locks them to the dealer's
advice in §3.9. Cash price is not the barrier; **cash *timing*** is.

**The gap AgriRover addresses.** Nothing, directly — but it dictates the
commercial form. A service billed **after** the harvest auction, or billed to the
FPO and netted against member payout, matches the cashflow. An upfront
₹75,000 capital purchase inverts it. **[Analyst scenario]**

**What it does not address.** AgriRover is not a credit product and must not
become one. Financing unproven machinery to indebted households would be
indefensible on the evidence in §8.

### 3.13 Digital access ceiling (new in v2)

**Description.** Every AgriRover output has to arrive through a phone.

**Magnitude.** As of 2025 roughly **51% of rural adults** own a smartphone with
household internet access; **83%** of rural households report internet access but
overwhelmingly via mobile networks with only **8%** on broadband; and nearly
**40% of rural adults are digitally illiterate** in the sense of being unable to
use the internet for informational purposes. `[F14]` **[External result]**
Independently, research on AI adoption in Indian agriculture identifies **trust
and language** as the critical barriers. `[E21]`

**How they cope and what it costs.** Voice calls and WhatsApp forwarded through a
younger family member.

**The gap AgriRover addresses.** The repository's own adoption interface —
**voice, proof and callback** rather than a dashboard — is the correct design and
is already documented. **[Repository fact]**
(`AGRIROVER_MARKET_ADOPTION_RESEARCH.md` §2.1)

**What it does not address — and a hard planning consequence.** With ~49% of
rural adults *not* holding a smartphone-plus-internet position and ~40%
digitally illiterate, a **self-serve app has a structural ceiling of roughly half
the market**, and the reachable half skews younger and larger-holding. Marathi
voice output plus a human callback is therefore **not a nicety, it is the
delivery mechanism**, and its cost — a person, on a phone, per plot, per week —
belongs in the unit economics as a **hard cost, not an allowance**. The
₹100/₹200/₹300 per-pass support figures in §4 are assumptions and §8 gate 4
already flags them as unmeasured. **[Analyst scenario]**

### 3.14 Crop insurance already sells "risk protection" (new in v2)

**Description.** AgriRover's loss-avoidance pitch competes with a subsidised
product the farmer may already hold.

**Magnitude.** Annual horticultural crops including tomato **are eligible** under
the restructured PMFBY and RWBCIS, and Maharashtra covers them at a farmer
premium of **5% of sum insured**; PMFBY is area-yield based and explicitly
includes pest and disease risk, while RWBCIS is parametric/weather-based. `[F15]`
**[External result]** Set against §3.6: SDRF/NDRF relief is separately capped at
about **₹17,000/ha for up to 2 ha** — of the order of **5%** of a 2-acre tomato
outlay at ₹1.5 lakh/acre. **[Analyst scenario]**

**How they cope and what it costs.** They pay 5% premium and accept
area-yield basis risk — the well-known weakness being that an individual plot's
loss may not trigger when the notified area's average does not.

**The gap AgriRover addresses.** Plot-level, timestamped, geotagged loss and
condition evidence is precisely what an area-yield product cannot see. That makes
**insurers and loss adjusters a genuinely new candidate buyer** not considered in
v1 — a party with an existing budget, a quantified loss function and a documented
verification problem. Flagged as a hypothesis worth one exploratory conversation,
**not** as a validated channel. **[Analyst scenario]**

**What it does not address.** No insurer has been approached, no product exists,
and admissibility of rover evidence in a claims process is entirely unexamined.
AgriRover must not be pitched as improving a farmer's insurance outcome.
**[AgriRover target]**

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

**v2 addition — a third and fourth data point, and the spread gets worse.** A
2025-26 Maharashtra open-field tomato input breakdown puts **total operating cost
at ₹31,500–46,500/acre** with **crop protection at only ₹2,000–4,000/acre**
(alongside seedlings ₹3,000–5,000, FYM ₹4,000–6,000, mulch film ₹2,500–3,500,
amortised drip ₹4,000–5,000, fertiliser ₹4,000–6,000, labour ₹6,000–8,000);
hybrid F1 seed alone runs **₹8,000–20,000/acre**. `[F19]` **[External result]**
A Nashik kharif figure of **₹5,892/ha** (~₹2,384/acre) sits in the same low band.
`[F20]` **[External result]**

| Source | Total cost/acre | Plant protection/acre | Ratio to GIZ |
|---|---:|---:|---:|
| GIZ Maharashtra manual `[E02]` | — | **17,000** | 1.0× |
| Local Junnar reporting (Lokmat) | ~150,000 | — | — |
| Maharashtra 2025-26 input breakdown `[F19]` | 31,500–46,500 | **2,000–4,000** | 0.12–0.24× |
| Nashik kharif `[F20]` | — | ~2,384 | 0.14× |
| Nagpur economics study, cost C3 | ~59,600 (��147,394/ha) | ~1,586 | 0.09× |

**This is now the single most dangerous fact in the dossier, and it is worse than
v1 stated.** Four of five independent sources put tomato plant protection between
**₹1,586 and ₹4,000/acre**. Only the GIZ manual — an illustrative budget, not a
survey — supports ₹17,000. The ₹150,000/acre Junnar figure is a grower-stated
number in a newspaper during a price-crash story, i.e. the moment when reported
costs are least reliable.

**If the true Junnar figure is ₹2,000–4,000/acre, the entire savings thesis is
dead on arrival.** A ₹3,600/acre package would cost *approximately the whole
plant-protection budget*, and the required saving would exceed 100%. The
₹17,000-based headroom table in §4.2 must be read as **the optimistic bound of a
range whose pessimistic bound is negative**, and no version of it may appear in a
deck. Resolving this against real invoices is **gate 1 in §8 and it is now a
kill-or-continue gate, not a refinement.** **[AgriRover target]**

*Reconciliation note, stated so it is not used as an excuse:* GIZ's ₹17,000 may
describe an intensively staked hybrid crop under heavy pinworm and leaf-curl
pressure, while the low figures may describe a lighter open-field crop — the ₹1.5
lakh vs ₹31,500–46,500 total-cost gap suggests these are genuinely different
farming systems. That is a plausible reconciliation and it is **not evidence**.
Only invoices from the target growers settle it.

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

### 4.6 Measured willingness to pay for advice — the ₹14.89 problem (new in v2)

Until now every WTP statement in this repository has been an assumption. There is
published Indian evidence, and it is brutal.

An Indian Journal of Extension Education study of farmer willingness to pay for
agro-advisory information found that **61.11% of farmers were willing to pay
anything at all**, and among those willing, the mean amounts were:

| Information type | Mean WTP (₹/acre) |
|---|---:|
| Composite information bundle | **18.10** |
| Weather information | 15.98 |
| **Plant protection information** | **14.89** |
| Market information | 14.80 |

`[F01]` **[External result]** Rainfed farmers were willing to pay *more* per unit
area than irrigated farmers across every category — the opposite of the intuition
that irrigated commercial growers pay more. *Limits: the study is not
Junnar-specific, not tomato-specific, and measures stated WTP for* information
delivery *rather than for a physical robotic visit; stated WTP typically overstates
revealed WTP. It is nonetheless the only measured Indian anchor available and it
points the same direction as every other datum in this document.*

**The gap, stated without softening.**

| Item | ₹/acre | Multiple of measured plant-protection WTP |
|---|---:|---:|
| Measured WTP, plant-protection info `[F01]` | 14.89 | 1× |
| Retired ₹300/acre-pass option | 300 | **20×** |
| Sentinel-package break-even per pass (~₹324 at 5 acres/day + ₹100) | ~324 | **~22×** |
| Deep-scan break-even per pass | 800–950 | **54–64×** |
| ₹3,600/acre season package | 3,600 | **242×** |

**Four conclusions follow, and they are not negotiable by better marketing.**

1. **Information has no market at AgriRover's cost structure.** A 50× gap is not
   a pricing problem, a packaging problem or an education problem. Any business
   model whose revenue line is "farmer pays for insight" is arithmetically dead.
2. **Therefore the sold object must not be information.** It must be one of:
   a **physical act** (a spray actually applied — which v1 explicitly cannot do),
   an **audit artefact** with a legal consequence (§3.7, §4.5 rank 1), a
   **liability transfer** (someone else carries the consequence of the spray
   decision), or an **input-procurement advantage** an FPO monetises directly
   (§3.10). "Better decisions" is not on that list.
3. **The ₹199/month tier is the only AgriRover price in the same universe as
   measured WTP** — ₹2,388/year over, say, 2 acres and 2 crops is ~₹600/acre-crop,
   still ~40× the ₹14.89 anchor, but within an order of magnitude of a bundled
   subscription. §4.3 already establishes it cannot fund physical visits. The two
   findings together say something coherent: **₹199/month is roughly the right
   price and the wrong product.**
4. **The 38.89% who would pay nothing** are not a segment to be converted; they
   are the base rate. Any pilot conversion assumption above ~60% of *approached*
   growers contradicts published evidence. **[Analyst scenario]**

### 4.7 Can the FPO actually pay? (new in v2)

§2 and §4.4 rest the commercial case on the FPO. That assumption now needs its own
evidence, and it does not survive intact.

- Of roughly **33,000 registered FPOs**, only about **one-third are considered
  financially viable**; constraints are inadequate equity, limited credit access
  and low turnover. `[F02]` **[External result]**
- As few as **2% of surveyed FPOs operate a custom-hiring centre** — the exact
  business model AgriRover's cluster-service plan assumes. `[F03]` **[External
  result]** FPOs that diversify across multiple activities show higher turnover
  and margins than single-business FPOs. `[F03]`
- **Junnar Taluka FPC specifically:** ~1,600 members, promoted by VGAI and SFAC,
  credited with transforming the local tomato trade by establishing the open
  auction market. Some reports historically cite turnover above **₹1 crore**,
  while **recent financial filings indicate operational revenue of the order of
  ₹1.19 lakh as of FY22**. `[F02]`, ([SIBM case study](https://www.sibmbengaluru.edu.in/wp-content/uploads/2023/08/4_Junnar-Taluka-Farmers-Producers-Company-Ltd.pdf))
  **[External result]** *Limit: filing-derived revenue figures for FPCs are
  frequently mis-stated in aggregator databases and may exclude commission or
  agency turnover that flows outside the P&L; the two figures differ by ~100×
  and this dossier cannot reconcile them from public sources.*

**What this does to §4.4.** The §4.4 model has one rover producing **₹200,000 of
revenue** against ~₹162,000 of cost. If JTFPC's own operating revenue is anywhere
near the lakh scale, **a single rover's annual revenue would exceed the FPO's
entire reported turnover** — which is not a business case, it is a category error.
If the ₹1 crore figure is the right one, a ₹200,000 service line is ~2% of
turnover and entirely plausible. **The pilot therefore cannot price anything until
the target FPO's audited turnover, cash position and existing machinery
utilisation are read directly.** This is now an explicit new gate in §8.
**[AgriRover target]**

**The uncomfortable structural point.** AgriRover's plan is to sell a CHC-style
service to a class of buyer of which **2% currently run a CHC** `[F03]` and
**two-thirds are not financially viable** `[F02]`, in a category where ICRISAT has
already documented underutilisation and maintenance failure `[E15]`, and where a
**nationally subsidised** comparator programme (Namo Drone Didi) shows drones
sitting idle for transport, battery, service-support and maintenance-cost reasons
`[F16]`. Every independent data point about this delivery model is negative. That
does not make it wrong — the price and route density might still work — but it
means **the burden of proof sits entirely on AgriRover's pilot**, and a pilot that
does not measure utilisation and downtime is not testing the thing most likely to
kill it. **[Analyst scenario]**

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

### 5.1 The competitors v1 missed — and they are the dangerous ones (new in v2)

The v1 table benchmarked AgriRover against ₹7–17 lakh capital equipment, which
flatters it. The real competition is priced *below* AgriRover and is already in
the field.

| Competitor | What it costs | What it delivers | Why it is worse news than a drone |
|---|---|---|---|
| **Niqo Robotics** (VLE model) | **₹300–500/acre**, **no software subscription** — AI embedded in hardware; NITI-profiled at 3,000+ farmers, 140,000 acres, 50–60% reported chemical reduction `[F04]`, `[E07]` | AI **see-and-spray**: detects *and* acts, operated by a local village-level entrepreneur | It occupies AgriRover's exact positioning — AI-driven chemical reduction — at **₹300–500/acre while physically spraying**, versus ₹800–950 to only look. It has also solved the last-mile operator problem AgriRover has not. |
| **Fyllo** | Nero devices ~**₹6,000–16,000**; Kairo **₹45,000–70,000**; subscription ~**₹400/month** `[F05]` | Fixed IoT sensing + AI advisory for high-value crops incl. grapes | A device the farmer **owns and never moves**, with no operator, no route density problem, no battery-swap, no downtime — for less than AgriRover's ₹75k. It beats AgriRover on every operational risk in §4.7. |
| **Fasal** | ~**₹500–750/month** + hardware install `[F05]` | Subscription sensing + irrigation/pest/fertigation advisory | Establishes the market's **actual price point for recurring agri-advisory: ₹500–750/month** — which brackets AgriRover's ₹199/month and shows the tier is under-priced for a *product*, not over-priced. |
| **Cropin** | OrbitAI reportedly **free** to set up farms and access insights (Jul 2026) `[F04]` | Satellite + AI farm intelligence, agribusiness-facing | Marginal-cost-zero satellite advisory sets the price of "insight" at **zero** for anything visible from orbit. |
| **Shetkari Mitra Bharti 2026** | Free to the farmer | **11,000+** state-funded village-level agricultural assistants announced `[F09]` | If filled, this is a **publicly funded human scouting network** — the labour AgriRover's business case assumes is unavailable and unaffordable. |

**The squeeze, stated plainly.** AgriRover is priced **above** an AI robot that
sprays (₹300–500/acre), **above** measured WTP for advice by ~50× (₹14.89/acre),
and **below** the market price of a sensor subscription it cannot match on
reliability (₹400–750/month). Its differentiator versus every row above is
**mobility with close-range ground truth** — Fyllo and Fasal see one point,
Cropin sees from orbit, Niqo sees only while spraying. Nobody else produces a
repeatable geotagged close-range record of *many* points across a plot over time.

**That is a real and defensible technical difference. Nothing in this dossier
shows anyone will pay for it.** The gap between "genuinely differentiated" and
"commercially viable" is exactly what §8's gates exist to close, and v2's evidence
widens it rather than narrowing it. **[Analyst scenario]**

### 5.2 What the alternatives' failures teach AgriRover (new in v2)

The most useful competitive evidence is not pricing, it is failure modes:

- **Namo Drone Didi:** against a 15,000-drone target by 2026, **1,094 drones were
  distributed in 2023-24** (only 500 under the scheme proper), and users report
  significant **idle time due to high transport costs, limited battery life, lack
  of service support and expensive maintenance** — so much so that the government
  now offers **80% assistance for multi-utility transport vehicles** to move the
  drones. `[F16]` **[External result]** Read that list again: transport, battery,
  service, maintenance. **AgriRover has all four problems and no subsidy.** A
  ~25 kg rover between scattered sub-2-ha plots faces a *worse* transport problem
  than a drone, and §4.4's ₹250/day transport line is an assumption.
- **CHC underutilisation** is documented by ICRISAT `[E15]` and corroborated by
  the 2%-of-FPOs figure `[F03]`.
- **Model domain shift** is documented in the repository's own ledger: PlantVillage
  fell from **99.35% held-out to 31.40/31.69% on external images** `[E08]`, and
  current literature confirms field accuracy drops for tomato pest/disease vision
  under fluctuating light, dense foliage and complex backgrounds, with **small,
  dense and occluded pests the primary failure case** `[F21]` **[External result]**
  — i.e. precisely thrips, mites and pinworm mines, three of the six target pests
  in §3.2.

**The single most valuable design implication in this document.** Because
(a) small occluded pests are the documented vision failure case `[F21]`, and
(b) the official pinworm thresholds are expressed as **moths per trap per week**
with 10–12 traps/acre `[F18]`, the highest-confidence, lowest-risk product is
**automated pheromone-trap counting** — a high-contrast, well-lit, fixed-geometry,
countable target that maps **directly onto a published action threshold**, rather
than free-form leaf-disease classification on a moving platform. NPSS already does
credentialed trap counting for cotton `[E22]`, which establishes both the protocol
precedent and the integration risk. This reframes the sensing roadmap: **trap
counts first, canopy classification later.** **[Analyst scenario]**

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

### 6.4 Two corrections to the v1 trust strategy (new in v2)

**Correction 1 — the KVK anchor has credibility but not reach.** §6.2 ranks a
local institutional name first. That remains right for *scientific defensibility*
and for persona C. It is wrong as a *distribution* strategy: public extension
including KVKs reaches **under 10%** of agricultural households, while
progressive farmers and input dealers reach **20–34%** each. `[F08]` **[External
result]** The revised trust sequence is therefore **two-track**:

| Track | Instrument | Buys you |
|---|---|---|
| **Scientific** | KVK Narayangaon / CoE Baramati co-signed protocol `[E30]`, `[E16]` | Defensibility, agronomist trust, publishable results, grant credibility |
| **Social** | 3–5 paid **demonstration growers** who are already the village's reference point | Actual reach, because that is the channel 20–34% of households use `[F08]` |

Running only the scientific track produces a well-documented pilot nobody hears
about. **[Analyst scenario]**

**Correction 2 — the dealer may have to be co-opted, not fought.** §2 classes the
input dealer as "structurally a competitor", which is analytically correct: he
earns on volume. But he is also the advice channel with the widest reach `[F08]`,
the credit line that funds the season (§3.12), and the physical supply point for
the bio-inputs whose **unavailability and short shelf life** is a documented IPM
barrier `[F10]`. A threshold service that reduces total chemical volume but
**shifts mix toward higher-margin bio-inputs and reduces his product-failure
complaints** is not automatically against his interest. This is a hypothesis worth
one exploratory conversation in Junnar, not a strategy — and if it fails, the
dealer's opposition should be treated as a **quantified commercial risk** rather
than an afterthought, because he can end the pilot by withdrawing credit.
**[Analyst scenario]**

**Correction 3 — add one trust signal v1 omitted.** Growers and FPOs in this
cluster have watched subsidised machinery sit idle `[F16]`, `[E15]`. The single
most persuasive artefact is therefore not an accuracy number but a **published
uptime log**: passes attempted, passes completed, days lost, and who fixed it —
unedited, from the pilot's first day. §6.2 item 4 says this; v2 elevates it to a
launch requirement. **[AgriRover target]**

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
launch strategy. `[E14]` **[External result]** + **[Repository fact]** And note
what subsidy did *not* fix: Namo Drone Didi machines are reported idle for
transport, battery, service and maintenance reasons despite the subsidy — which is
why the scheme added 80% support for transport vehicles on top. `[F16]` Subsidy
solves acquisition, not utilisation, and utilisation is AgriRover's risk.

### New objections surfaced by v2 research

**"Studies say farmers will pay ₹15 an acre for pest advice. You want ₹800."**
This is the hardest objection in the document and it is correct. Measured Indian
WTP for plant-protection information is **₹14.89/acre**, composite ₹18.10/acre,
with 38.89% unwilling to pay anything. `[F01]` There is no rebuttal at the
information level — a ~50× gap cannot be closed by presentation. The only honest
response is to **stop selling information**: sell an audit artefact to a party
with a legal obligation (§3.7), an input-procurement advantage to an FPO (§3.10),
or nothing. If the pilot cannot find a buyer of one of those, the correct outcome
is to stop. **[Analyst scenario]**

**"Niqo already does AI spraying at ₹300–500 an acre. Why would I buy a rover
that only looks?"**
You probably would not, and that comparison should be conceded immediately rather
than argued. `[F04]` AgriRover's only defensible differentiator is **repeatable
close-range multi-point evidence over time**, which a spray pass does not produce
and a satellite cannot see (§5.1). Whether that difference is worth money is
unproven. Anyone pitching AgriRover as a cheaper Niqo is misrepresenting it.

**"Fyllo sells me a device for ₹6,000–16,000 that never breaks down and never
needs a driver."**
Also correct, and the honest answer is that they solve different problems: a
fixed sensor characterises **one point continuously**, a rover characterises
**many points periodically**. For irrigation and microclimate, fixed sensing is
strictly better and AgriRover should not compete there. For spatial pest
distribution across a plot, it cannot help. `[F05]`

**"My whole spray bill is ₹3,000 an acre, not ₹17,000."**
On current evidence this grower is more likely to be right than the GIZ manual.
Four of five sources put Maharashtra tomato plant protection at **₹1,586–4,000/acre**
`[F19]`, `[F20]`. If that is the local truth, AgriRover has **no savings case at
any price** and must say so rather than argue with an invoice. §4.1 and gate 1 in
§8. **[AgriRover target]**

**"The government is hiring 11,000 village agriculture assistants. Why do I need a
robot?"**
A fair challenge. `[F09]` If those posts are filled, the state supplies free human
scouting and AgriRover's labour-scarcity premise weakens materially. The
non-defensive answer is that AgriRover's output is a *record*, not a visit, and
that a human assistant covering many villages cannot produce weekly
same-point-geotagged repeatability. But this is a genuine strategic risk to be
tracked, not dismissed. **[Analyst scenario]**

**"Half the chemical sold here is fake. Your threshold advice is useless if the
can is wrong."**
Partly right, and it is an argument *for* verification passes rather than against
them: with a spurious share estimated at 25–30% of the market `[F11]`, a
before/after measurement is the only way to distinguish product failure from
resistance or misdiagnosis. But AgriRover cannot assay a chemical and must never
attribute a failure to counterfeiting on image evidence alone (§3.10).

**"I don't have a smartphone / I can't read the app."**
Roughly 49% of rural adults lack the smartphone-plus-internet position and ~40%
are digitally illiterate. `[F14]` The repository's voice-and-callback interface is
the right answer **[Repository fact]**, but the cost of that human callback is an
unmeasured assumption in the unit economics, not a solved feature (§3.13, §8 gate 4).

**"₹75,000 is more than I owe in total."**
Literally true for the average agricultural household: mean outstanding debt is
**₹74,121** and mean monthly income **₹10,218–13,661**. `[F13]` The ownership
option should be withdrawn from farmer-facing material, not repriced (§3.12).

**"Our FPO doesn't have that kind of money."**
Very likely true. Only ~1/3 of FPOs are financially viable, 2% run a CHC, and
JTFPC's own filed operational revenue may be of the order of ₹1.19 lakh.
`[F02]`, `[F03]` The pilot must read the FPO's audited accounts before quoting a
price (§4.7, §8 gate 11). **[AgriRover target]**

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

### New gates added by v2 research

| # | Gate | Why the sale is blocked without it | Label |
|---|---|---|---|
| 11 | **The target FPO's audited turnover, cash position and existing machinery utilisation**, read from accounts — not from a database entry | Public sources put JTFPC's FY22 operational revenue anywhere from ₹1.19 lakh to >₹1 crore, a ~100× spread `[F02]`; §4.4's whole model assumes the FPO can absorb a ₹200k service line | **[AgriRover target]** |
| 12 | **Revealed willingness to pay, not stated** — a signed order at a real price from a named buyer | Measured Indian WTP for plant-protection advice is ₹14.89/acre against an ₹800–950 break-even, a ~54–64× gap `[F01]`. Stated interest is worthless at this gap | **[AgriRover target]** |
| 13 | **A named buyer with a legal obligation** identified and interviewed (exporter, pack-house, certifier, or insurer) | §4.6 concludes information cannot be sold at AgriRover's cost; the audit-artefact route is the only one with an existing budget. India led RASFF 2025 with 124 pesticide notifications `[F17]` | **[AgriRover target]** |
| 14 | **Transport cost and time between scattered sub-2-ha plots**, measured on real village routes | Namo Drone Didi's documented idle time is driven by transport, battery, service and maintenance `[F16]`; §4.4's ₹250/day transport line is an assumption and a ~25 kg rover is harder to move than a drone | **[AgriRover target]** |
| 15 | **Trap-count accuracy against manual trap counts** for pinworm at the published 10 and 20–30 moths/trap/week thresholds `[F18]` | §5.2 argues this is the highest-confidence sensing product; if it fails, the low-risk roadmap fails with it | **[AgriRover target]** |
| 16 | **Which scouting protocol the local KVK actually endorses** — NIPHM's 5×5 = 25 plants `[E26]` or ICAR/NCIPM's 50 plants weekly `[F07]` | The two official protocols differ ~2× in sample size; pass duration, cost per pass and every price in §4 depend on which one is being replicated | **[AgriRover target]** |
| 17 | **Bio-input availability in the target cluster** — can a grower actually buy the trichocards, traps and bio-agents a threshold recommendation calls for, within the window? | Documented IPM barrier is unavailability and short shelf life `[F10]`; a recommendation that cannot be acted on generates no value and destroys trust | **[AgriRover target]** |
| 18 | **Agronomist review capacity and cost at scale**, timed | §3.9 shows public extension reaches <10% of households `[F08]`; if the review layer is the product (§3.3), its cost is the business, and Maharashtra's own department carries ~32–33% vacancies `[F09]` | **[AgriRover target]** |
| 19 | **Callback delivery cost per plot per week** for the ~49% without smartphone-plus-internet and ~40% digitally illiterate `[F14]` | Voice + callback is the delivery mechanism, not a feature; it is currently an unpriced human cost | **[AgriRover target]** |

### The kill criteria, stated explicitly

v1 listed gaps. v2 is blunter: three of these are **kill gates**, not improvement
opportunities. If any one of them resolves negatively, the current business model
should be stopped rather than iterated.

1. **Gate 1 (local protection spend).** If invoices show ₹2,000–4,000/acre rather
   than ₹17,000 `[F19]`, `[F20]`, there is **no savings case at any price** and the
   product must be repositioned onto compliance or abandoned.
2. **Gate 12 + 13 (a buyer who is not the grower).** If no party with a legal or
   procurement obligation will sign, then given ₹14.89/acre measured WTP `[F01]`
   there is **no route to revenue** at AgriRover's cost structure.
3. **Gate 3 + 14 (productive acres/day including transport).** If real routes
   cannot sustain ~1.86 acres/day for a deep scan, every price in §4 fails, and
   `[F16]`/`[E15]` say this is the most likely single failure mode.

**Until gates 1–5 close, the only defensible sales sentence is:** *"We produce a
repeatable, geotagged, expert-reviewed record of what is in your field, what was
applied and whether it worked. We have not yet proved it saves you money, and
we are running the pilot that will tell us."*

**v2 adds a second mandatory sentence for any FPO or grower conversation:**
*"Published Indian studies say farmers will pay about ₹15 an acre for pest advice.
Our pass costs far more than that. So we are not selling you advice — and if we
cannot find something worth more than advice, we will tell you and stop."*

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

### v2 evidence ledger — `[F01]`–`[F24]`

New research for this revision. Every row is **[External result]** unless stated.
Limits are mandatory reading; several of these are search-aggregated and are
marked as such.

| ID | Finding used | Where used | Quality and limit |
|---|---|---|---|
| **F01** | Farmer WTP for agro-advisory: **61.11%** willing to pay; mean **₹18.10/acre** composite, **₹14.89/acre plant protection**, ₹15.98 weather, ₹14.80 market; rainfed > irrigated WTP per unit area. Indian Journal of Extension Education | §1.11, §4.6, §7, §8 gate 12 | Peer-reviewed Indian extension study — **the only measured WTP anchor in this dossier**. *Limit: not Junnar, not tomato, measures* stated *WTP for information delivery, not for a robotic visit; stated WTP normally overstates revealed WTP. Locate and open the primary paper before external use.* |
| **F02** | Only about **one-third of ~33,000 registered FPOs** are financially viable; constraints are inadequate equity, limited credit, low turnover. JTFPC: ~1,600 members, VGAI/SFAC-promoted; historical reports >₹1 crore turnover vs **filings indicating ~₹1.19 lakh operational revenue FY22** | §1.12, §4.7, §8 gate 11 | Sector studies plus company-filing aggregation. *Limit: the ~100× discrepancy in JTFPC revenue is unresolved from public sources; FPC filings frequently exclude commission/agency turnover. **Must be read from audited accounts, not quoted.*** |
| **F03** | As few as **2% of surveyed FPOs operate a custom-hiring centre**; diversified FPOs show higher turnover and margin than single-business FPOs | §1.12, §4.7, §5.2 | Survey-based research. *Limit: sample and geography not verified; directionally consistent with `[E15]`.* |
| **F04** | **Niqo Robotics**: village-level-entrepreneur model, AI spot-spray at **₹300–500/acre**, **no software subscription** (AI embedded in hardware). **Cropin OrbitAI** (Jul 2026): free farm setup and insights | §1.13, §5.1, §7 | Company/market reporting; consistent with NITI profile `[E07]` (3,000+ farmers, 140,000 acres, 50–60% reported reduction). *Limit: vendor-reported pricing; verify with a local quote. NITI figures are company-reported, not independently trialled.* |
| **F05** | **Fyllo**: Nero ~₹6,000–16,000, Kairo ₹45,000–70,000, subscription ~₹400/month. **Fasal**: ~₹500–750/month plus hardware install | §1.13, §5.1, §7 | Aggregated vendor/market pricing. *Limit: both firms quote per farm on enquiry; treat as an order-of-magnitude market price, not a tariff.* |
| **F06** | *H. armigera* tomato loss: **5–55%**; **~35%** overall; **37.79%** Karnataka; **31.53% avoidable** loss unprotected vs protected (Rajasthan); **22–38%** commonly reported | §3.2 | **Retires v1's flagged weakest citation** by resolving it to identifiable regional studies. *Limit: assembled via search across Indian entomology literature; the individual primary papers must be cited by name and year before deck use.* |
| **F07** | ICAR/NCIPM insecticide-resistance management for *H. armigera* and *B. tabaci*: **rejects calendar spraying**; prescribes economic injury thresholds, **weekly scouting of 50 plants**, chemical-group rotation, seasonal "window strategies", systemic seed treatment to delay early foliar sprays, and no repeat of a class after control failure | §3.3, §8 gate 16 | **Retires v1's second flagged weakest citation.** Official IRM guidance. *Limit: developed primarily for cotton; the 50-plant unit conflicts ~2× with NIPHM tomato AESA's 25 plants `[E26]` and the KVK must adjudicate.* |
| **F08** | Only **40–50%** of agricultural households access any technical advice; input dealers and progressive farmers each reach **~20–34%**; **public extension including KVKs reaches under 10%** | §1.6, §3.9, §6.4, §7 | NSSO-based analysis. *Limit: national, multi-round; Junnar's commercially sophisticated cluster may differ materially — verify locally.* |
| **F09** | Maharashtra agriculture department recruiting **~8,953 vacant posts, ~32–33% of sanctioned strength**, concentrated in Group C field staff; **Shetkari Mitra Bharti 2026** announced for **11,000+** village-level assistants | §3.9, §5.1, §7 | State recruitment notifications and reporting. *Limit: announced posts are not filled posts; treat the 11,000 as a strategic risk with uncertain timing.* |
| **F10** | IPM adoption barriers in India: ignorance of the **ETL concept** and of pest/natural-enemy identification; **unavailability and short shelf life** of traps, trichocards and bio-agents; high upfront cost and labour intensity; aggressive chemical marketing and supply chains; risk aversion absent a market premium | §1.7, §3.3, §6.4, §8 gate 17 | Multiple Indian adoption-constraint studies. *Limit: search-aggregated across studies of differing crops and states; the specific ranking is indicative, not measured for Junnar tomato.* |
| **F11** | Counterfeit/spurious pesticides estimated at **25–30% of the Indian market by volume**, ~20% annual growth, ~**4%** crop-yield reduction, ~**10.6 mt** produce lost annually (FICCI / Tata Strategic Management Group) | §3.10, §7 | Industry-association estimates. *Limit: **weakest new citation in v2.** Methodology not public, figures widely recycled and dated, projections unverified. Use the direction, never the decimal.* |
| **F12** | Yavatmal, Maharashtra 2017–18: thousands of acute pesticide-poisoning cases, highest state death/hospitalisation counts; drivers were absent PPE, above-head spraying, early re-entry; family medical costs **sometimes exceeding ₹1 lakh** | §3.11 | Well-documented public-health episode. *Limit: cotton in Vidarbha, not tomato in Junnar; the ₹1 lakh figure is an anecdotal maximum, not a mean.* |
| **F13** | NSS 77th round (2018-19): agricultural household monthly income **₹10,218**, average outstanding debt **₹74,121**, **50.2%** indebted. NABARD NAFIS 2021-22: agricultural household monthly income **₹13,661**; rural households with outstanding debt **52.0%** (from 47.4% in 2016-17) | §3.12, §7 | Official national surveys. *Limit: national averages; a commercial Junnar tomato grower is likely above them — which weakens the affordability argument but not the cashflow-timing argument.* |
| **F14** | 2025: **~51%** of rural adults own a smartphone with household internet; **83%** of rural households report internet access but only **8%** broadband; **~40%** of rural adults digitally illiterate for informational use | §3.13, §7, §8 gate 19 | National digital-access survey reporting. *Limit: rural aggregate across all occupations; Maharashtra is described as high-penetration, so the local ceiling is probably better than 51%.* |
| **F15** | Annual horticultural crops **including tomato are eligible** under restructured PMFBY and RWBCIS; Maharashtra farmer premium **5% of sum insured**; PMFBY area-yield based and includes pest/disease risk, RWBCIS parametric | §3.14 | Official scheme design. *Limit: eligibility is not enrolment; local tomato enrolment rates unknown, and area-yield basis risk is a known structural weakness.* |
| **F16** | Namo Drone Didi: target **15,000** drones by 2026; **1,094 distributed in 2023-24** (only **500** under the scheme proper, rest via lead fertiliser companies); users report significant **idle time from high transport cost, limited battery life, lack of service support, expensive maintenance**; government added **80%** assistance for multi-utility transport vehicles | §1.9, §5.1, §5.2, §7, §8 gate 14 | Scheme reporting and user accounts. *Limit: press-derived; no audited utilisation dataset. **The most directly transferable negative evidence in the dossier** — same four failure modes AgriRover faces.* |
| **F17** | India **topped RASFF in 2025 with 124 pesticide-related notifications**; **365** Indian food products flagged for pesticide/heavy-metal levels May-2024 to May-2026; okra, curry leaves and chilli under stringent EU border controls with mandatory sampling | §1.10, §1.14, §3.7, §8 gate 13 | EU alert-system reporting. *Limit: notification counts cover all Indian food exports, not Maharashtra tomato; tomato is **not** among the named high-frequency commodities — the compliance buyer exists but is not yet a tomato buyer.* |
| **F18** | Tomato pinworm action thresholds: **20–30 moths/trap/week** for intervention, or **10 moths/trap/week** to trigger azadirachtin; **10–12 pheromone traps/acre** for monitoring and mass trapping; resistance managed by rotating actives plus *Trichogramma chilonis* and botanicals | §3.3, §5.2, §8 gate 15 | Indian extension/IPM guidance for *P. absoluta*. *Limit: thresholds vary by source and season; the local KVK must confirm which applies. **Strategically the most useful finding in v2** — the decision variable is a countable trap insect.* |
| **F19** | Maharashtra open-field tomato 2025-26: total operating cost **₹31,500–46,500/acre**; **crop protection ₹2,000–4,000/acre**; seedlings ₹3,000–5,000; FYM ₹4,000–6,000; mulch film ₹2,500–3,500; amortised drip ₹4,000–5,000; fertiliser ₹4,000–6,000; labour ₹6,000–8,000; hybrid F1 seed ₹8,000–20,000/acre | §4.1, §7, §8 gate 1 | Current cultivation-cost breakdown. *Limit: an advisory/aggregator breakdown rather than a farm survey; ranges are wide. **Contradicts `[E02]`'s ₹17,000 by 4–8× and that contradiction is now a kill gate.*** |
| **F20** | Nashik kharif tomato plant protection ~**₹5,892/ha** (~₹2,384/acre) | §4.1 | Regional farm-economics figure. *Limit: Nashik kharif only; corroborates the low band.* |
| **F21** | Machine-vision tomato pest/disease accuracy degrades in field conditions from domain shift — fluctuating light, dense foliage, complex backgrounds; **small, dense and occluded pests are the primary failure case**, causing localisation errors and missed detections; mitigations include lightweight architectures, calibration/uncertainty rejection, CNN-Transformer hybrids, TensorRT/FP16 for 10–35 FPS on edge devices | §5.2 | Current computer-vision literature. *Limit: benchmark-paper claims, not independent field validation; directly corroborates `[E08]`. Confirms thrips, mites and pinworm mines are the hardest three of six target pests.* |
| **F22** | FSSAI/MPRNL: **86,401** food samples analysed 2022–2025, **2.8%** exceeding notified MRLs; tomato consistently among vegetables with frequent residue detections alongside brinjal, okra, cabbage, cauliflower | §3.3, §3.7 | Official national residue monitoring. *Limit: the 2.8% aggregate spans all commodities; tomato-specific violation rates for Maharashtra were not isolated.* |
| **F23** | Junnar/Narayangaon tomato area: historical **2,200 acres across 150 villages**, with more recent estimates **as high as 10,000 acres**; no official hectare series located; Junnar (Narayangaon) APMC modal price **₹1,500/quintal (₹15/kg)** on 22-Jul-2026, trading ₹1,500–2,001/quintal in late July | §1.1, §3.7 | Mixed press and market-data sources. *Limit: the 2,200 vs 10,000 acre spread is unreconciled and **route density — AgriRover's key cost driver — cannot be established from it.** Must be measured on the ground.* |
| **F24** | Maharashtra horticulture labour: harvesting costs for crops such as onion up **30–40%**; growing reliance on migrant labour from MP, Gujarat and Bihar who demand higher pay or leave unexpectedly; mechanisation shifting notably in sugarcane | §3.5 | Current agricultural labour reporting. *Limit: press-derived and largely onion/sugarcane; corroborates `[E17]` and the Indie Journal figures for direction.* |

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
