"""Build the IEI full-length paper PDF from paper/paper_source.md.

The PDF is the companion copy of the mandatory .docx and is set to the same
IEI paper format: A4, 2.54 cm margins on all four sides, Times New Roman
12 pt at 1.5 line spacing, 14 pt bold centred title, 12 pt bold main headings,
12 pt bold italic sub headings, page number at the bottom centre.

Usage:  python paper/build_paper.py
Output: paper/AgriRover_IEI_38th_National_Convention_Full_Paper.pdf

Deliberately dependency-light: reportlab only.
"""

import os
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "paper_source.md")
FIGDIR = os.path.join(HERE, "figures")
OUT = os.path.join(HERE, "AgriRover_IEI_38th_National_Convention_Full_Paper.pdf")

INK = colors.HexColor("#1a1c1a")
ACCENT = colors.HexColor("#2f5d3a")
MUTED = colors.HexColor("#5d6660")
RULE = colors.HexColor("#c8cec9")
BAND = colors.HexColor("#eef2ef")

PAGE_W, PAGE_H = A4
# IEI paper format: A4, top/bottom/left/right margins of 2.54 cm. The running
# head and the page number sit inside the margin band, outside the text frame.
MARGIN = 25.4 * mm
MARGIN_X = MARGIN
MARGIN_T = MARGIN
MARGIN_B = MARGIN
CONTENT_W = PAGE_W - 2 * MARGIN_X

# Body text: Times New Roman 12 pt at 1.5 line spacing.
BODY_PT = 12
LEADING = BODY_PT * 1.5


# ---------------------------------------------------------------- styles
def styles():
    s = {}
    # Title: 14 pt, bold, centred -- exactly as the paper format table states.
    s["title"] = ParagraphStyle(
        "title", fontName="Times-Bold", fontSize=14, leading=17.5,
        alignment=TA_CENTER, textColor=INK, spaceAfter=4,
    )
    s["subtitle"] = ParagraphStyle(
        "subtitle", fontName="Times-Italic", fontSize=BODY_PT, leading=15,
        alignment=TA_CENTER, textColor=INK, spaceAfter=10,
    )
    s["authors"] = ParagraphStyle(
        "authors", fontName="Times-Bold", fontSize=BODY_PT, leading=15,
        alignment=TA_CENTER, textColor=INK, spaceAfter=3,
    )
    s["affil"] = ParagraphStyle(
        "affil", fontName="Times-Roman", fontSize=10, leading=13,
        alignment=TA_CENTER, textColor=MUTED, spaceAfter=2,
    )
    s["venue"] = ParagraphStyle(
        "venue", fontName="Times-Italic", fontSize=10, leading=13,
        alignment=TA_CENTER, textColor=MUTED, spaceAfter=2,
    )
    s["abshead"] = ParagraphStyle(
        "abshead", fontName="Times-Bold", fontSize=BODY_PT, leading=15,
        textColor=ACCENT, spaceAfter=4,
    )
    s["abstract"] = ParagraphStyle(
        "abstract", fontName="Times-Roman", fontSize=BODY_PT, leading=LEADING,
        alignment=TA_JUSTIFY, textColor=INK, firstLineIndent=0,
    )
    s["keywords"] = ParagraphStyle(
        "keywords", fontName="Times-Roman", fontSize=BODY_PT, leading=LEADING,
        alignment=TA_LEFT, textColor=INK, spaceBefore=6,
    )
    # Main heading: 12 pt, bold. Sub heading: 12 pt, bold italic.
    s["h1"] = ParagraphStyle(
        "h1", fontName="Times-Bold", fontSize=BODY_PT, leading=15,
        textColor=INK, spaceBefore=13, spaceAfter=5,
    )
    s["h2"] = ParagraphStyle(
        "h2", fontName="Times-BoldItalic", fontSize=BODY_PT, leading=15,
        textColor=INK, spaceBefore=9, spaceAfter=3,
    )
    s["body"] = ParagraphStyle(
        "body", fontName="Times-Roman", fontSize=BODY_PT, leading=LEADING,
        alignment=TA_JUSTIFY, textColor=INK, spaceAfter=6,
    )
    s["math"] = ParagraphStyle(
        "math", fontName="Times-Italic", fontSize=BODY_PT, leading=LEADING,
        alignment=TA_CENTER, textColor=INK,
        spaceBefore=6, spaceAfter=8,
    )
    # Captions and table matter stay below the body size, as is conventional
    # for figure and table apparatus, which the format table does not govern.
    s["caption"] = ParagraphStyle(
        "caption", fontName="Times-Roman", fontSize=9, leading=12.5,
        alignment=TA_JUSTIFY, textColor=MUTED, spaceBefore=5, spaceAfter=10,
    )
    s["tabcap"] = ParagraphStyle(
        "tabcap", fontName="Times-Bold", fontSize=9.5, leading=12.5,
        alignment=TA_LEFT, textColor=INK, spaceBefore=8, spaceAfter=4,
    )
    s["cell"] = ParagraphStyle(
        "cell", fontName="Times-Roman", fontSize=9, leading=11.6,
        textColor=INK,
    )
    s["cellh"] = ParagraphStyle(
        "cellh", fontName="Times-Bold", fontSize=9, leading=11.6,
        textColor=colors.white,
    )
    s["ref"] = ParagraphStyle(
        "ref", fontName="Times-Roman", fontSize=9.5, leading=13,
        alignment=TA_JUSTIFY, textColor=INK,
        leftIndent=14, firstLineIndent=-14, spaceAfter=3.5,
    )
    return s


# ---------------------------------------------------------------- math
ROMAN = 'Times-Roman'

# Symbols are emitted as self-contained fragments so they can appear anywhere,
# including inside <super>/<sub>, without unbalancing the surrounding <i> span.
GREEK = {
    r"\Delta": "&#916;", r"\theta": "&#952;", r"\omega": "&#969;",
    r"\top": f'<font face="{ROMAN}">T</font>',
    r"\times": "&#215;", r"\cdot": "&#183;",
    r"\sigma": "&#963;", r"\mu": "&#956;", r"\phi": "&#966;",
}


def math_markup(tex):
    t = tex.strip()
    t = t.replace(r"\qquad", "&nbsp;" * 8).replace(r"\quad", "&nbsp;" * 4)
    t = t.replace(r"\left(", "(").replace(r"\right)", ")")
    t = t.replace(r"\left[", "[").replace(r"\right]", "]")
    # Operator names are set upright, per convention, without closing the
    # italic span that wraps the whole expression.
    for fn in ("cos", "sin", "tan", "exp", "log"):
        t = t.replace("\\" + fn, f'<font face="{ROMAN}">{fn}</font>&#8201;')
    for k, v in GREEK.items():
        t = t.replace(k, v)
    t = re.sub(r"\^\{(.*?)\}", r"<super>\1</super>", t)
    t = re.sub(r"_\{([^{}]*)\}", r"<sub>\1</sub>", t)
    t = re.sub(r"\^([A-Za-z0-9])", r"<super>\1</super>", t)
    t = re.sub(r"_([A-Za-z0-9])", r"<sub>\1</sub>", t)
    t = t.replace("\\,", "&#8201;").replace("\\;", "&#8202;")
    return f"<i>{t}</i>"


def inline(text):
    """Inline markup: **bold**, $math$, EVT_NAME kept as-is.

    Math spans are extracted before entity escaping so that the markup emitted
    by math_markup survives, and so an author's plain '&' still escapes.
    """
    out = []
    for i, part in enumerate(re.split(r"\$(.+?)\$", text)):
        if i % 2:
            out.append(math_markup(part))
            continue
        part = (part.replace("&", "&amp;")
                    .replace("<", "&lt;").replace(">", "&gt;"))
        part = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", part)
        out.append(part.replace("--", "&#8212;"))
    return "".join(out)


# ---------------------------------------------------------------- parse
def parse(path):
    raw = open(path, encoding="utf-8").read()
    lines = raw.split("\n")
    meta, blocks = {}, []
    i = 0
    n = len(lines)

    def flush(buf):
        if buf:
            blocks.append(("p", " ".join(buf).strip()))

    para = []
    while i < n:
        ln = lines[i]
        st = ln.strip()

        m = re.match(r"^(TITLE|SUBTITLE|AUTHORS|AFFILIATION|CONTACT|VENUE|KEYWORDS):\s*(.*)$", st)
        if m:
            flush(para); para = []
            meta[m.group(1)] = m.group(2).strip()
            i += 1
            continue

        if st == "ABSTRACT:":
            flush(para); para = []
            i += 1
            buf = []
            while i < n and lines[i].strip():
                buf.append(lines[i].strip())
                i += 1
            meta["ABSTRACT"] = " ".join(buf)
            continue

        if st.startswith("## "):
            flush(para); para = []
            blocks.append(("h2", st[3:].strip()))
            i += 1
            continue

        if st.startswith("# "):
            flush(para); para = []
            blocks.append(("h1", st[2:].strip()))
            i += 1
            continue

        if st.startswith("MATH:"):
            flush(para); para = []
            blocks.append(("math", st[5:].strip()))
            i += 1
            continue

        if st.startswith("FIG:"):
            flush(para); para = []
            spec = st[4:].strip()
            fn, _, cap = spec.partition("|")
            blocks.append(("fig", (fn.strip(), cap.strip())))
            i += 1
            continue

        if st.startswith("REF:"):
            flush(para); para = []
            blocks.append(("ref", st[4:].strip()))
            i += 1
            continue

        if st == "TABLE:":
            flush(para); para = []
            i += 1
            rows = []
            while i < n and "|" in lines[i]:
                rows.append([c.strip() for c in lines[i].split("|")])
                i += 1
            blocks.append(("table", rows))
            continue

        if not st:
            flush(para); para = []
            i += 1
            continue

        para.append(st)
        i += 1

    flush(para)
    check_guidelines(meta)
    return meta, blocks


# The IEI author guidelines cap the abstract at 300 words and the keyword list
# at five entries. Both outputs share this parser, so failing here is the
# cheapest place to catch a violation -- before either file is written.
ABSTRACT_MIN_WORDS = 250
ABSTRACT_MAX_WORDS = 300
KEYWORDS_MAX = 5


def check_guidelines(meta):
    words = len(meta["ABSTRACT"].split())
    if not ABSTRACT_MIN_WORDS <= words <= ABSTRACT_MAX_WORDS:
        raise SystemExit(
            f"abstract is {words} words; the guidelines require "
            f"{ABSTRACT_MIN_WORDS}-{ABSTRACT_MAX_WORDS}. "
            "Adjust paper_source.md.")
    keys = [k for k in re.split(r"[;,]", meta["KEYWORDS"]) if k.strip()]
    if len(keys) > KEYWORDS_MAX:
        raise SystemExit(
            f"{len(keys)} keywords; the guidelines allow {KEYWORDS_MAX}.")


# ---------------------------------------------------------------- build
def build():
    S = styles()
    meta, blocks = parse(SRC)
    flow = []

    # ---- masthead
    flow.append(Paragraph(inline(meta["TITLE"]), S["title"]))
    flow.append(Paragraph(inline(meta["SUBTITLE"]), S["subtitle"]))
    # Escape each name first: the separator is markup and must not be escaped.
    authors = " &#183; ".join(
        inline(a.strip()) for a in meta["AUTHORS"].split("|"))
    flow.append(Paragraph(authors, S["authors"]))
    flow.append(Paragraph(inline(meta["AFFILIATION"]), S["affil"]))
    flow.append(Paragraph(inline(meta["CONTACT"]), S["affil"]))
    flow.append(Paragraph(inline(meta["VENUE"]), S["venue"]))
    flow.append(Spacer(1, 9))

    abs_tbl = Table(
        [[Paragraph("ABSTRACT", S["abshead"])],
         [Paragraph(inline(meta["ABSTRACT"]), S["abstract"])]],
        colWidths=[CONTENT_W],
    )
    abs_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BAND),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 9),
        ("TOPPADDING", (0, 1), (-1, 1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 0),
        ("LINEBEFORE", (0, 0), (0, -1), 1.6, ACCENT),
    ]))
    flow.append(abs_tbl)
    flow.append(Paragraph(
        "<b>Keywords:</b> " + inline(meta["KEYWORDS"]), S["keywords"]))
    flow.append(Spacer(1, 4))

    tbl_no = [0]
    fig_no = [0]
    ref_no = [0]
    in_refs = [False]

    for kind, payload in blocks:
        if kind == "h1":
            in_refs[0] = payload.lower().startswith("references")
            flow.append(Paragraph(inline(payload), S["h1"]))
            flow.append(rule())
        elif kind == "h2":
            flow.append(Paragraph(inline(payload), S["h2"]))
        elif kind == "p":
            flow.append(Paragraph(inline(payload), S["body"]))
        elif kind == "math":
            flow.append(Paragraph(math_markup(payload), S["math"]))
        elif kind == "ref":
            ref_no[0] += 1
            flow.append(Paragraph(
                f"[{ref_no[0]}]&nbsp;&nbsp;{inline(payload)}", S["ref"]))
        elif kind == "fig":
            fig_no[0] += 1
            flow.append(figure(payload[0], payload[1], fig_no[0], S))
        elif kind == "table":
            tbl_no[0] += 1
            flow.append(table_block(payload, tbl_no[0], S))

    doc = BaseDocTemplate(
        OUT, pagesize=A4,
        leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=MARGIN_T, bottomMargin=MARGIN_B,
        title="AgriRover: A Low-Cost Autonomous Ground Robot for Targeted "
              "Agrochemical Dosing and In-Situ Soil Diagnostics on Indian "
              "Smallholdings",
        author="V. K. Gupta, K. H. Mukeshbhai, S. Wagh, P. Nandy",
        subject="38th National Convention of Agricultural Engineers, "
                "The Institution of Engineers (India)",
    )
    frame = Frame(MARGIN_X, MARGIN_B, CONTENT_W,
                  PAGE_H - MARGIN_T - MARGIN_B, id="main",
                  leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="body", frames=[frame],
                                       onPage=decorate)])
    doc.build(flow)
    print("wrote", OUT)


def rule():
    t = Table([[""]], colWidths=[CONTENT_W], rowHeights=[0.9])
    t.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.7, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


TABLE_TITLES = {
    1: "Table 1. Design requirements, responses and verification mechanisms.",
    2: "Table 2. The nine FreeRTOS event bits and their membership of the "
       "drive-inhibit mask.",
    3: "Table 3. Closed-loop simulation of the guidance stack over the "
       "34-pass coverage plan of Figure 3. Identical controller and waypoint "
       "sequence in all conditions; only the pose estimate differs.",
    4: "Table 4. Verification status by subsystem.",
    5: "Table 5. Planned bill of materials, Indian retail pricing at "
       "specification time.",
    6: "Table 6. Six-gate acceptance protocol. No claim may be published "
       "before its gate is passed.",
}


def table_block(rows, num, S):
    header, body = rows[0], rows[1:]
    ncol = len(header)

    if ncol == 3:
        widths = [CONTENT_W * 0.30, CONTENT_W * 0.42, CONTENT_W * 0.28]
    elif ncol == 4:
        widths = [CONTENT_W * 0.31, CONTENT_W * 0.23,
                  CONTENT_W * 0.23, CONTENT_W * 0.23]
    else:
        widths = [CONTENT_W / ncol] * ncol

    data = [[Paragraph(inline(c), S["cellh"]) for c in header]]
    for r in body:
        r = (r + [""] * ncol)[:ncol]
        data.append([Paragraph(inline(c), S["cell"]) for c in r])

    t = Table(data, colWidths=widths, repeatRows=1)
    st = [
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -2), 0.35, RULE),
        ("LINEBELOW", (0, -1), (-1, -1), 0.8, ACCENT),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            st.append(("BACKGROUND", (0, i), (-1, i), BAND))
    t.setStyle(TableStyle(st))

    cap = Paragraph(TABLE_TITLES.get(num, f"Table {num}."), S["tabcap"])
    return KeepTogether([cap, t, Spacer(1, 10)])


FIG_WIDTHS = {
    "fig1_architecture.png": 1.00,
    "fig2_safety_chain.png": 1.00,
    "fig3_coverage_path.png": 1.00,
    "fig4_localisation_error.png": 0.74,
}


def figure(fname, caption, num, S):
    path = os.path.join(FIGDIR, fname)
    from reportlab.lib.utils import ImageReader
    iw, ih = ImageReader(path).getSize()
    target_w = CONTENT_W * FIG_WIDTHS.get(fname, 0.92)
    img = Image(path, width=target_w, height=target_w * ih / iw)
    img.hAlign = "CENTER"
    cap = Paragraph(f"<b>Figure {num}.</b> {inline(caption)}", S["caption"])
    return KeepTogether([Spacer(1, 4), img, cap])


def decorate(canv, doc):
    canv.saveState()
    canv.setFont("Times-Roman", 7.6)
    canv.setFillColor(MUTED)
    if doc.page > 1:
        canv.drawString(
            MARGIN_X, PAGE_H - MARGIN_T + 7 * mm,
            "AgriRover  |  38th National Convention of Agricultural Engineers, "
            "The Institution of Engineers (India)")
        canv.setStrokeColor(RULE)
        canv.setLineWidth(0.5)
        canv.line(MARGIN_X, PAGE_H - MARGIN_T + 5.4 * mm,
                  PAGE_W - MARGIN_X, PAGE_H - MARGIN_T + 5.4 * mm)
    canv.setStrokeColor(RULE)
    canv.setLineWidth(0.5)
    canv.line(MARGIN_X, MARGIN_B - 5 * mm, PAGE_W - MARGIN_X, MARGIN_B - 5 * mm)
    canv.drawCentredString(PAGE_W / 2, MARGIN_B - 9.5 * mm, str(doc.page))
    canv.restoreState()


if __name__ == "__main__":
    build()
