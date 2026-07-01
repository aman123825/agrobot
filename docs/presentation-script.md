# AgriRover — Presentation Script (GrowwxIITB INV.ENT, Track A)

**Deck:** `AgriRover_GrowwxIITB.pptx` (speaker notes are embedded on every slide — use PowerPoint **Presenter View** / Google Slides **Presenter notes**).
**Main pitch:** slides 1–16, ~8 minutes. Slides 17–21 are an **appendix** — show only if judges ask for engineering depth.

> Delivery tips: open strong on slide 1, slow down on slides 2–3 (problem+solution), speed up through 5–7, land hard on 10 (what we built) and 16 (the ask). Make eye contact; let the charts breathe.

## Talking points (one line per slide)

| # | Slide | Say (short) | ~sec |
|---|-------|-------------|------|
| 1 | Title | "We're AgriRover, a 4-member IIT Bombay team — precision farming for every small farm." | 15 |
| 2 | Problem | "86% of Indian farms are under 2 ha — too small for tractors, so farmers fertilise blind, waste money, degrade soil." | 40 |
| 3 | Solution | "One low-cost autonomous rover that senses, decides and acts per plant." | 35 |
| 4 | Why us | "Only option that's affordable + autonomous + per-plant — and also senses soil." | 30 |
| 5 | How it works | "Two brains: real-time ESP32 for control, Raspberry Pi for AI, over a secure link." | 25 |
| 6 | Sense & See | "7-in-1 soil probe + 3 AI models on a Coral TPU at ~30 fps." | 35 |
| 7 | Act & Autonomy | "Sequential dosing, vision-aimed spray, autonomous snake routes, fail-safe by design." | 40 |
| 8 | Market | "Precision-ag doubles to ~$739M by 2034; our core is 126M small farms." | 30 |
| 9 | Tailwinds | "Policy is on our side — SMAM 50–80% subsidy, AIF, Soil Health Card; we go via FPOs/CHCs." | 35 |
| 10 | What we've built | "Not just an idea — full firmware, AI, nav, dashboard, simulator, circuit + 110-part BOM, validated in sim." | 30 |
| 11 | Hypothesis | "Per-plant dosing cuts inputs sharply, no yield loss — we'll prove it in pilot." | 30 |
| 12 | Projected impact | "~45% less fertiliser, ~40% cost saving, ~88% accuracy — projections to validate." | 20 |
| 13 | Execution | "Build in 3 months → pilot 5–10 farms → iterate → scale via FPOs/CHCs." | 30 |
| 14 | Team | "Four IIT Bombay engineers who built this end-to-end." | 25 |
| 15 | Budget | "Affordable & modular — demo ₹8–14k, full AI build ₹27–48k." | 20 |
| 16 | Ask | "We need mentorship + a pilot + seed support. Thank you." | 20 |

**Total main pitch ≈ 7–8 minutes.**

## Q&A prep (anticipate these)

- **"Is it actually built or just an idea?"** → Full software stack + hardware design done and validated in simulation; hardware integration is the funded next step. (Point to slide 10 + appendix.)
- **"Why won't a drone company just do this?"** → Drones spray but can't sense soil or act per plant on the ground; we're a ground rover built for per-plant precision on small farms. (Slide 4.)
- **"How do farmers afford it?"** → They don't buy it — FPOs/CHCs run it as a shared service, financed by AIF, subsidised 50–80% under SMAM. (Slide 9.)
- **"Where do your impact numbers come from?"** → Simulation and design targets; honestly labelled as projections — validating them is the core purpose of the pilot. (Slide 12.)
- **"What's your biggest risk?"** → Adoption + closing the sim-to-field gap; we de-risk via the shared-service model and an early 5–10 farm pilot.
- **"Can a mostly-mechanical team do the AI/software?"** → We already built the full stack ourselves; the appendix shows the depth. Gaps (agronomy, GTM) filled via mentors + a field partner.
- **"Revenue model?"** → Rover sale + AMC, Rover-as-a-Service (per-acre), and a data/analytics subscription. (Slide 9.)
- **"Unit economics?"** → Full build ₹27–48k; shared across many farms via one FPO/CHC → per-acre price stays low. (Slides 9, 15.)

## Honesty guardrails (say these as projections, not facts)
- 45% / 40% / 88% numbers → "projected / to be validated in pilot".
- Subsidy % (SMAM 50–80%) → "verify current terms for our machine class and state".
