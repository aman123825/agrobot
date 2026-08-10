from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "Agrobot_IDEAS_Level_1_Kickoff_14_Aug_2026.pptx"
HERO = ROOT / "_ppt_build/assets/v3/s1_Image_0.png"

# Apple-keynote direction: large editorial type, calm whitespace, one photographic moment.
INK = RGBColor(19, 22, 20)
FOREST = RGBColor(24, 61, 43)
GREEN = RGBColor(45, 132, 78)
LIME = RGBColor(188, 224, 91)
MIST = RGBColor(242, 245, 240)
LINE = RGBColor(214, 220, 214)
MUTED = RGBColor(92, 101, 95)
WHITE = RGBColor(255, 255, 255)
DISPLAY = "Aptos Display"
BODY = "Aptos"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
prs.core_properties.title = "Agrobot — IDEAS IIT Bombay Level 1 Kickoff"
prs.core_properties.subject = "Customer discovery: customer, pain, payer and value hypothesis"
prs.core_properties.author = "Agrobot Team, IIT Bombay"
prs.core_properties.comments = "14 August 2026. Secondary evidence is identified; no prototype or field validation claim is made."
blank = prs.slide_layouts[6]


def shape(slide, x, y, w, h, fill, radius=False, line=None, transparency=0):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = fill; s.fill.transparency = transparency
    s.line.color.rgb = line or fill; s.line.width = Pt(.8)
    if radius:
        try: s.adjustments[0] = .08
        except Exception: pass
    return s


def txt(slide, x, y, w, h, value, size=16, color=INK, bold=False, font=BODY,
        align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP, margin=0, italic=False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.clear(); tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]; p.alignment = align; p.space_after = Pt(0)
    r = p.add_run(); r.text = value
    r.font.name = font; r.font.size = Pt(size); r.font.bold = bold; r.font.italic = italic; r.font.color.rgb = color
    return box


def transition(slide, duration=650):
    el = parse_xml(f'<p:transition {nsdecls("p")} spd="med" advClick="1" dur="{duration}"><p:fade/></p:transition>')
    slide._element.insert(2, el)


def base(slide, dark=False):
    bg = slide.background.fill; bg.solid(); bg.fore_color.rgb = INK if dark else WHITE
    transition(slide)


def rule(slide, x, y, w, color=LINE, thick=.012):
    shape(slide, x, y, w, thick, color)


def header(slide, number, title, dark=False):
    color = WHITE if dark else INK
    txt(slide, .62, .32, 3.4, .25, "IDEAS · IIT BOMBAY · L1C19", 8.5, color, True)
    txt(slide, 10.2, .32, 2.5, .25, title.upper(), 8.5, color, True, align=PP_ALIGN.RIGHT)
    txt(slide, 12.2, 7.08, .5, .18, f"0{number}", 8, color, True, align=PP_ALIGN.RIGHT)


def source(slide, value, dark=False):
    rule(slide, .62, 6.86, 12.08, RGBColor(62, 68, 64) if dark else LINE)
    txt(slide, .62, 6.98, 11.5, .24, value, 7.2, RGBColor(173, 180, 175) if dark else MUTED)


def tag(slide, x, y, label, dark=False, width=1.55):
    fill = LIME if dark else FOREST
    fg = INK if dark else WHITE
    shape(slide, x, y, width, .34, fill, True)
    txt(slide, x, y+.01, width, .23, label, 8.5, fg, True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)


def bullet(slide, x, y, w, title, body, dark=False):
    fg = WHITE if dark else INK; sub = RGBColor(188,195,190) if dark else MUTED
    shape(slide, x, y+.06, .11, .11, LIME if dark else GREEN, True)
    txt(slide, x+.28, y, w-.28, .28, title, 13, fg, True)
    txt(slide, x+.28, y+.34, w-.28, .55, body, 10.5, sub)

# 1 — cinematic cover
s = prs.slides.add_slide(blank); base(s, True)
s.shapes.add_picture(str(HERO), Inches(7.55), Inches(0), width=Inches(5.78), height=Inches(7.5))
# dark veil makes the image feel photographic rather than illustrative
shape(s, 7.55, 0, 5.78, 7.5, INK, transparency=42)
shape(s, 7.53, 0, .04, 7.5, LIME)
header(s, 1, "Level 1 kickoff", True)
tag(s, .64, 1.02, "14 AUGUST 2026", True, 1.72)
txt(s, .62, 1.72, 6.3, .72, "AGROBOT", 46, WHITE, True, DISPLAY)
txt(s, .62, 2.55, 6.25, 1.55, "Before we build,\nwe need to know.", 38, WHITE, True, DISPLAY)
txt(s, .65, 4.42, 5.95, .9, "Is there a painful, frequent and paid problem in agricultural compliance evidence?", 18, RGBColor(221,226,222), True)
txt(s, .65, 5.78, 5.95, .5, "LEVEL 1 · CUSTOMER DISCOVERY", 11, LIME, True)
txt(s, .65, 6.18, 5.95, .45, "Customer  ·  Pain  ·  Payer  ·  Value", 11, WHITE)

# 2 — problem, an argument not a dashboard
s = prs.slides.add_slide(blank); base(s); header(s, 2, "Problem & customer")
tag(s, .62, .86, "OUR STARTING THESIS", False, 1.75)
txt(s, .62, 1.38, 9.5, .68, "The record may matter more than the robot.", 31, INK, True, DISPLAY)
txt(s, .62, 2.08, 8.8, .48, "Export-linked agriculture requires credible treatment and PHI evidence. Today, that evidence may be fragmented, late or expensive to verify.", 14, MUTED)
# main customer and consequence
shape(s, .62, 2.92, 4.05, 2.87, MIST, True, LINE)
txt(s, .94, 3.24, 3.4, .25, "BEACHHEAD CUSTOMER HYPOTHESIS", 8.5, GREEN, True)
txt(s, .94, 3.72, 3.35, .85, "Exporter / pack-house\nquality team", 23, INK, True, DISPLAY)
txt(s, .94, 4.82, 3.35, .55, "Maharashtra grape and pomegranate clusters", 12, MUTED)
shape(s, 4.97, 2.92, 3.42, 2.87, FOREST, True, FOREST)
txt(s, 5.28, 3.24, 2.78, .25, "THE CONSEQUENCE TO TEST", 8.5, LIME, True)
txt(s, 5.28, 3.72, 2.72, .85, "Audit friction.\nRework. Rejection risk.", 22, WHITE, True, DISPLAY)
txt(s, 5.28, 4.84, 2.68, .58, "We have secondary signals—no first-hand cost baseline yet.", 11, RGBColor(201,211,205))
# four decisive questions
shape(s, 8.7, 2.92, 4.0, 2.87, WHITE, True, LINE)
txt(s, 9.02, 3.24, 3.35, .25, "FOUR QUESTIONS DECIDE THE THESIS", 8.5, GREEN, True)
for i, line in enumerate(["Is the problem frequent and costly?", "Who owns the loss and budget?", "What evidence is trusted today?", "Will the payer name a ₹ value?"]):
    y=3.72+i*.47
    txt(s, 9.02, y, .28, .25, f"{i+1}", 10, GREEN, True)
    txt(s, 9.42, y, 2.85, .34, line, 11.2, INK, True)
source(s, "Sources: APEDA GrapeNet / Residue Monitoring workflow; repository evidence [E05–E06], [F17], [G03]. Status: secondary evidence only; 0 Agrobot interviews completed.")

# 3 — solution as hypothesis with explicit boundary
s = prs.slides.add_slide(blank); base(s); header(s, 3, "Proposed solution")
tag(s, .62, .86, "HYPOTHESIS · NOT BUILT", False, 1.78)
txt(s, .62, 1.38, 10.7, .68, "One trusted evidence record.", 31, INK, True, DISPLAY)
txt(s, .62, 2.05, 10.5, .48, "A geotagged, time-stamped treatment + PHI record, reviewed by an agronomist and usable by the buyer’s QA workflow.", 14, MUTED)
# keynote sequence
sequence=[("01", "Observe", "Capture what happened in the field."), ("02", "Verify", "Attach place, time and accountable review."), ("03", "Record", "Map evidence to the buyer’s workflow."), ("04", "Decide", "Test whether the buyer will pay.")]
for i,(n,h,b) in enumerate(sequence):
    x=.62+i*3.03
    txt(s,x,3.0,.5,.3,n,10,GREEN,True)
    rule(s,x,3.42,2.65,FOREST if i==3 else LINE,.025)
    txt(s,x,3.68,2.56,.38,h,18,INK,True,DISPLAY)
    txt(s,x,4.18,2.55,.66,b,11,MUTED)
# boundary statement
shape(s, .62, 5.17, 12.08, 1.15, INK, True, INK)
txt(s, .94, 5.48, 2.05, .26, "LEVEL 1 BOUNDARY", 9, LIME, True)
txt(s, 3.1, 5.4, 9.1, .48, "Interview first. Quantify pain. Identify payer. Seek real advancement. Only then decide go, pivot or stop.", 14, WHITE, True)
source(s, "No prototype, accuracy, coverage, savings or payback claim is made. The solution is an early value hypothesis to be tested through H1–H8 interviews.")

# 4 — why team / why now; photo-ready without fake portraits
s = prs.slides.add_slide(blank); base(s); header(s, 4, "Why us · why now")
tag(s, .62, .86, "TEAM + TIMING", False, 1.45)
txt(s, .62, 1.38, 9.8, .98, "Close enough to the field.\nDisciplined enough to question the thesis.", 28, INK, True, DISPLAY)
# members in clean editorial bands
people=[("HITANSHU KAPADIYA", "Customer discovery · ENT101"), ("VIVEK GUPTA", "Systems thinking · discovery owner"), ("SHREYASH WAGH", "Nashik context · field access")]
for i,(name,role) in enumerate(people):
    y=3.15+i*.92
    ph=shape(s,.62,y,.68,.68,MIST,True,GREEN)
    ph.line.dash_style = MSO_LINE_DASH_STYLE.DASH
    txt(s,.62,y+.2,.68,.24,"PHOTO",7.5,GREEN,True,align=PP_ALIGN.CENTER)
    txt(s,1.55,y+.04,3.2,.28,name,12.5,INK,True)
    txt(s,1.55,y+.37,3.2,.25,role,10.5,MUTED)
# right-side timing case
shape(s, 6.02, 2.78, 6.68, 3.15, FOREST, True, FOREST)
txt(s, 6.38, 3.15, 5.8, .26, "WHY THIS IS THE RIGHT MOMENT TO DISCOVER", 9, LIME, True)
bullet(s, 6.38, 3.7, 5.72, "Compliance evidence has a defined workflow", "APEDA traceability and PHI requirements create an observable context—not yet proof of willingness to pay.", True)
bullet(s, 6.38, 4.57, 5.72, "Information-only economics are weak", "Repository research finds farmer WTP near ₹14.89/acre, making the buyer and outcome critical.", True)
bullet(s, 6.38, 5.44, 5.72, "Learning is still cheap", "Interviews can invalidate the thesis before capital, hardware or field claims.", True)
source(s, "Team: repository IDEAS roster. Timing: APEDA workflow; [F01] information WTP; [G01–G03] advisory market and liability evidence. Photo boxes remain editable.")

# 5 — finish with commitments, not vanity
s = prs.slides.add_slide(blank); base(s, True); header(s, 5, "Level 1 commitment", True)
tag(s, .62, .86, "NEXT: DISCOVER", True, 1.5)
txt(s, .62, 1.4, 10.8, 1.08, "We do not need a prototype\nto learn what matters next.", 34, WHITE, True, DISPLAY)
txt(s, .65, 2.78, 10.9, .52, "Our commitment for Level 1", 15, RGBColor(195,204,198), True)
# three large commitments
items=[("40–50", "conversations", "Grower → agronomist → FPO/exporter → QA"), ("H1–H8", "hypotheses", "Validated · invalidated · still unclear"), ("1+", "real advancement", "Named ₹, buyer intro, data access or future pilot slot")]
for i,(n,h,b) in enumerate(items):
    x=.62+i*4.02
    rule(s,x,3.58,3.55,RGBColor(68,76,71),.025)
    txt(s,x,3.86,3.52,.6,n,29,LIME,True,DISPLAY)
    txt(s,x,4.58,3.52,.32,h,13,WHITE,True)
    txt(s,x,5.08,3.48,.62,b,10.5,RGBColor(183,192,186))
txt(s, .62, 6.24, 11.7, .38, "Listen. Quantify. Falsify. Then decide: go, pivot or stop.", 16, WHITE, True)
source(s, "Discovery targets and guardrails: CUSTOMER_DISCOVERY_KIT.md. This deck makes no prototype or field-validation claim.", True)

prs.save(OUT)
print(OUT)
