# Full-length paper — 38th National Convention of Agricultural Engineers (IEI)

**AgriRover: A Low-Cost Autonomous Ground Robot for Targeted Agrochemical
Dosing and In-Situ Soil Diagnostics on Indian Smallholdings**
Accepted for presentation, 27–28 August 2026. Full paper due **12 August 2026,
17:00 IST**. Corresponding author: Vivek Kumar Gupta (25b2269@iitb.ac.in).

## One source, two outputs

`paper_source.md` is the only file to edit. Both deliverables are generated
from it, so the Word file and the PDF can never drift apart.

| Output | Built by | Required by IEI |
| --- | --- | --- |
| `AgriRover_IEI_38th_National_Convention_Full_Paper.docx` | `build_paper_docx.py` | Mandatory |
| `AgriRover_IEI_38th_National_Convention_Full_Paper.pdf` | `build_paper.py` | Companion copy |

## Build

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r paper/requirements.txt

python paper/experiments/ekf_coverage_sim.py   # optional: results.json + figures
python paper/build_paper.py                    # PDF
python paper/build_paper_docx.py               # DOCX
```

The simulation is seeded (`SEED` in `ekf_coverage_sim.py`), so re-running it
reproduces the numbers quoted in the paper exactly. If a figure or a reported
value ever changes, the simulation changed — check that before the text.

## Source markup

`paper_source.md` uses a small line-oriented syntax, not general Markdown:

| Marker | Meaning |
| --- | --- |
| `TITLE:` `SUBTITLE:` `AUTHORS:` `AFFILIATION:` `CONTACT:` `VENUE:` `KEYWORDS:` | Front-matter fields; authors separated by `\|` |
| `ABSTRACT:` | Followed by one block of text, terminated by a blank line |
| `# ` / `## ` | Numbered section / subsection heading |
| `MATH:` | Display equation, LaTeX-like subset |
| `$...$` | Inline math inside prose, e.g. `$F_k$` |
| `**bold**` | Bold span |
| `FIG: file.png \| caption` | Figure from `figures/`, auto-numbered |
| `TABLE:` | Followed by pipe-delimited rows, header first, auto-numbered |
| `REF:` | Reference entry, auto-numbered |

Table captions live in `TABLE_TITLES` in `build_paper.py` and are shared by
both builders; adding a table means adding its caption there.

## Figures

`experiments/ekf_coverage_sim.py` writes `figures/fig3_coverage_path.png` and
`figures/fig4_localisation_error.png` plus `experiments/results.json`.
`experiments/make_diagrams.py` writes the architecture and safety-chain
diagrams. Figures are committed so the paper builds without matplotlib.

## Covering e-mail

`SUBMISSION_EMAIL.md` holds the ready-to-send covering e-mail to the National
Convenor, stating **online presentation** as the preferred mode. It still has
three `[[placeholders]]` — the payment reference, the co-author certificate
clause, and a phone number — listed under "Open items" in that file.

It also flags one substantive point: the accepted abstract title differs from
the current paper title, and the e-mail declares the change and offers to
revert it.

## Submission checklist (IEI, on or before 12 August 2026, 17:00 IST)

- [ ] Full-length paper in `.docx` — generated above
- [ ] PDF copy of the same paper — generated above
- [ ] Registration payment receipt / transaction reference
- [ ] Preferred presentation mode stated in the covering e-mail: **online**
      (drafted in `SUBMISSION_EMAIL.md`)
- [ ] Separate registration + receipt for any co-author who needs their own
      presentation certificate (the single registration covers only the
      corresponding author)

## Claim discipline

Section 10 of the paper defines six acceptance gates. No figure for detection
accuracy, dosing volume, chemical reduction, or yield may be added to this
paper until the corresponding gate has been passed and the measurement
recorded. Simulation results are always labelled as such in the text.
