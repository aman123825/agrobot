from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_THEME_COLOR
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls, qn
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "docs" / "Agrobot_IDEAS_Level_1_Kickoff_14_Aug_2026.pptx"

W, H = Inches(13.333), Inches(7.5)
NAVY = RGBColor(15, 29, 38)
GREEN = RGBColor(41, 105, 75)
LIME = RGBColor(180, 210, 85)
PAPER = RGBColor(244, 246, 239)
WHITE = RGBColor(255, 255, 255)
MUTED = RGBColor(105, 119, 114)
FONT = "Aptos"
DISPLAY = "Aptos Display"

prs = Presentation()
prs.slide_width, prs.slide_height = W, H
prs.core_properties.title = "Agrobot — IDEAS IIT Bombay Level 1 Kickoff"
prs.core_properties.subject = "Customer discovery kickoff; not a prototype presentation"
prs.core_properties.author = "Agrobot Team, IIT Bombay"
prs.core_properties.comments = "Prepared for IDEAS Level 1 kickoff, 14 August 2026. Claims are hypotheses or secondary evidence unless explicitly marked."
blank = prs.slide_layouts[6]


def rect(slide, x, y, w, h, fill, radius=0, line=None, lw=1, transparency=0, shadow=False):
    typ = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    s = slide.shapes.add_shape(typ, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if transparency:
        s.fill.transparency = transparency
    s.line.color.rgb = line or fill; s.line.width = Pt(lw)
    if radius:
        try: s.adjustments[0] = 0.08
        except Exception: pass
    if shadow:
        sp_pr = s._element.spPr
        effect = parse_xml(
            '<a:effectLst %s><a:outerShdw blurRad="63500" dist="25400" dir="2700000" algn="ctr" rotWithShape="0">'
            '<a:srgbClr val="0F1D26"><a:alpha val="18000"/></a:srgbClr></a:outerShdw></a:effectLst>' % nsdecls('a')
        )
        sp_pr.append(effect)
    return s


def glass(slide, x, y, w, h, dark=False, radius=1):
    return rect(
        slide, x, y, w, h,
        WHITE if dark else WHITE,
        radius=radius,
        line=RGBColor(100, 130, 125) if dark else RGBColor(219, 226, 220),
        lw=.8,
        transparency=78 if dark else 8,
        shadow=True,
    )


def transition(slide, kind="fade", duration=700):
    """Add a restrained PowerPoint slide transition; content remains fully editable."""
    timing = parse_xml(
        f'<p:transition {nsdecls("p")} spd="med" advClick="1" dur="{duration}"><p:{kind}/></p:transition>'
    )
    slide._element.insert(2, timing)


def text(slide, x, y, w, h, value, size=20, color=NAVY, bold=False, font=FONT,
         align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP, margin=0, italic=False, tracking=None):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.clear(); tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = value
    r.font.name = font; r.font.size = Pt(size); r.font.bold = bold; r.font.italic = italic; r.font.color.rgb = color
    if tracking is not None: r.font._element.set('spc', str(tracking))
    return box


def rich(slide, x, y, w, h, parts, size=16, color=NAVY, leading=1.05):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.clear(); tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]; p.space_after = Pt(0); p.line_spacing = leading
    for val, bold, col in parts:
        r = p.add_run(); r.text = val; r.font.name = FONT; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = col or color
    return box


def add_bg(slide, dark=False):
    bg = slide.background.fill; bg.solid(); bg.fore_color.rgb = NAVY if dark else PAPER


def chrome(slide, n, section, dark=False):
    c = WHITE if dark else NAVY
    text(slide, .55, .28, 2.0, .25, f"IDEAS · L1C19", 9, c, True)
    text(slide, 10.0, .28, 2.75, .25, section.upper(), 9, c, True, align=PP_ALIGN.RIGHT)
    rect(slide, .55, 7.12, 12.23, .012, LIME if dark else GREEN)
    text(slide, .55, 7.18, 3.0, .18, "AGROBOT · IIT BOMBAY", 8, c)
    text(slide, 12.25, 7.17, .5, .18, f"0{n}", 8, c, True, align=PP_ALIGN.RIGHT)


def pill(slide, x, y, w, label, fill, fg):
    rect(slide, x, y, w, .34, fill, radius=1)
    text(slide, x, y+.01, w, .25, label, 9, fg, True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)


def source(slide, value, dark=False):
    text(slide, .58, 6.78, 12.1, .22, value, 7.5, WHITE if dark else MUTED)

# 1 — COVER
s = prs.slides.add_slide(blank); add_bg(s, True); transition(s, "fade", 850)
rect(s, 0, 0, 4.4, 7.5, GREEN)
# field-line motif
for i in range(7):
    x = .35 + i*.55
    rect(s, x, 4.0 + (i%2)*.12, .03, 2.75, LIME, transparency=18)
# Large translucent editorial pane creates depth without turning the slide into a UI mockup.
glass(s, 4.62, .72, 8.05, 6.0, dark=True)
text(s, 11.15, .98, 1.1, .24, "PRE-KICKOFF", 8, RGBColor(190,205,200), True, align=PP_ALIGN.RIGHT)
text(s, .58, .42, 3.25, .35, "IDEAS · IIT BOMBAY", 11, WHITE, True)
pill(s, .58, 1.25, 1.35, "LEVEL 1", LIME, NAVY)
text(s, .58, 1.85, 3.25, 1.25, "AGROBOT", 40, WHITE, True, DISPLAY)
text(s, .58, 3.12, 3.15, .9, "Start with the field.\nNot the machine.", 21, WHITE, True, DISPLAY)
text(s, 4.95, 1.18, 7.45, .65, "CUSTOMER DISCOVERY KICKOFF", 13, LIME, True)
text(s, 4.95, 1.95, 7.25, 1.7, "Finding the decision\nworth paying for.", 36, WHITE, True, DISPLAY)
text(s, 4.98, 4.08, 6.8, .9, "We are here to test the customer, pain, payer and value hypothesis — before any prototype decision.", 18, WHITE)
rect(s, 4.98, 5.35, 6.9, .02, LIME)
text(s, 4.98, 5.62, 3.3, .55, "14 AUGUST 2026", 14, WHITE, True)
text(s, 8.6, 5.62, 3.25, .55, "L1C19 · DSSE", 14, WHITE, True, align=PP_ALIGN.RIGHT)
text(s, 4.98, 6.42, 6.9, .3, "Agrobot Team · Mechanical Engineering · IIT Bombay", 10, RGBColor(190,205,200))

# 2 — PROBLEM
s = prs.slides.add_slide(blank); add_bg(s); transition(s, "fade", 700); chrome(s,2,"Problem & Customer Segment")
text(s,.58,.72,7.4,.55,"Problem & Customer Segment",28,NAVY,True,DISPLAY)
text(s,.58,1.28,7.7,.55,"A compliance workflow may be painful — but the payer is still a hypothesis.",16,GREEN,True)
# left customer card
glass(s,.58,2.0,3.45,4.45)
pill(s,.85,2.28,1.45,"BEACHHEAD",GREEN,WHITE)
text(s,.85,2.82,2.9,.8,"Exporter /\npack-house QA",22,NAVY,True,DISPLAY)
text(s,.85,3.78,2.85,.72,"Export-linked grape and pomegranate clusters in Maharashtra",14,MUTED)
text(s,.85,4.72,2.9,.24,"STAKEHOLDER CHAIN",9,GREEN,True)
text(s,.85,5.05,2.9,.85,"Grower  →  Agronomist\n→  FPO / exporter  →  audit",14,NAVY,True)
# pain flow
for y,num,title,body in [
(2.0,"01","Fragmented records","Spray, plot, operator and PHI evidence are assembled across people and formats."),
(3.34,"02","Verification gap","The buyer must trust that the right treatment and waiting period were followed."),
(4.68,"03","Cost is unclear","Audit friction or rejection may create real loss — but we have not measured it first-hand.")]:
    pill(s,4.4,y,.58,num,LIME,NAVY)
    text(s,5.15,y-.02,3.0,.32,title,17,NAVY,True)
    text(s,5.15,y+.38,4.25,.63,body,13,MUTED)
# hypothesis panel
rect(s,9.62,2.0,3.12,4.45,NAVY,radius=1)
text(s,9.92,2.3,2.55,.3,"LEVEL 1 MUST TEST",10,LIME,True)
for i,t in enumerate(["Is this problem frequent and costly?","Who owns the loss — and budget?","What evidence is trusted today?","Will anyone name a ₹ value?"]):
    y=2.88+i*.72
    text(s,9.92,y,.26,.3,"•",18,LIME,True)
    text(s,10.23,y+.02,2.15,.52,t,12,WHITE,True)
source(s,"Secondary evidence: APEDA grape traceability/PHI workflow; repo evidence [E05–E06], [F17], [G03]. No Agrobot interviews completed yet.")

# 3 — SOLUTION HYPOTHESIS
s = prs.slides.add_slide(blank); add_bg(s); transition(s, "fade", 700); chrome(s,3,"Proposed Solution")
text(s,.58,.72,7.4,.55,"Proposed Solution",28,NAVY,True,DISPLAY)
pill(s,10.42,.75,2.32,"HYPOTHESIS · NOT BUILT",LIME,NAVY)
text(s,.58,1.28,10.8,.48,"The outcome hypothesis: one trustworthy field-to-buyer evidence record.",16,GREEN,True)
# pipeline
steps=[("OBSERVE","What happened?"),("VERIFY","Is it credible?"),("RECORD","Can it be audited?"),("DECIDE","Is it worth paying for?")]
for i,(a,b) in enumerate(steps):
    x=.58+i*3.1
    glass(s,x,2.12,2.7,1.28)
    text(s,x+.22,2.36,2.25,.26,a,11,GREEN,True)
    text(s,x+.22,2.75,2.25,.38,b,14,NAVY,True)
    if i<3: text(s,x+2.78,2.5,.25,.3,"→",19,GREEN,True,align=PP_ALIGN.CENTER)
# record artifact
rect(s,.58,3.83,6.0,2.45,NAVY,radius=1)
text(s,.9,4.12,5.35,.32,"EARLY VALUE PROPOSITION",10,LIME,True)
text(s,.9,4.57,5.15,.9,"Agronomist-reviewed, geotagged treatment + PHI evidence for an audit-obligated buyer.",20,WHITE,True,DISPLAY)
text(s,.9,5.67,5.15,.3,"The record is the hypothesis. The rover is not the assumption.",11,RGBColor(190,205,200))
# falsifiers
text(s,7.02,3.85,5.6,.3,"WHAT WOULD MAKE US PIVOT",10,GREEN,True)
for i,t in enumerate(["Buyers already receive equivalent evidence free.","The problem is rare, cheap or owned by someone else.","No buyer names a budget or advances the conversation."]):
    y=4.32+i*.59
    pill(s,7.02,y,.48,"×",NAVY,WHITE)
    text(s,7.68,y+.01,4.75,.45,t,13,NAVY,True)
source(s,"Level 1 boundary: interview and validate H1–H8 first. No prototype, field-result, savings, accuracy, coverage or payback claim is made.")

# 4 — WHY US / NOW
s = prs.slides.add_slide(blank); add_bg(s); transition(s, "fade", 700); chrome(s,4,"Why Us? Why Now?")
text(s,.58,.72,7.4,.55,"Why Us? Why Now?",28,NAVY,True,DISPLAY)
text(s,.58,1.28,11.7,.5,"A field-connected team with the discipline to learn before building.",16,GREEN,True)
names=[("HITANSHU\nKAPADIYA","Mechanical Engineering","ENT101 · customer discovery"),("VIVEK\nGUPTA","Mechanical Engineering","Discovery owner · systems"),("SHREYASH\nWAGH","Mechanical Engineering","Nashik context · field access")]
for i,(name,dept,role) in enumerate(names):
    x=.58+i*3.36
    glass(s,x,2.02,3.08,3.75)
    # editable photo placeholder
    ph=rect(s,x+.28,2.3,2.52,1.28,RGBColor(228,233,224),radius=1,line=GREEN,lw=1)
    ph.line.dash_style = 4
    text(s,x+.28,2.73,2.52,.3,"ADD PHOTO",10,GREEN,True,align=PP_ALIGN.CENTER)
    text(s,x+.28,3.86,2.5,.72,name,17,NAVY,True,DISPLAY)
    text(s,x+.28,4.67,2.5,.28,dept,10,MUTED)
    text(s,x+.28,5.08,2.5,.42,role,11,GREEN,True)
# why now rail
rect(s,10.66,2.02,2.08,3.75,NAVY,radius=1)
text(s,10.94,2.31,1.55,.28,"WHY NOW",10,LIME,True)
for y,head,sub in [(2.85,"Audit pressure","Residue and PHI evidence matters to export chains."),(3.92,"Weak WTP","Information-only models face a severe price gap."),(4.98,"Right moment","Level 1 can kill the wrong thesis cheaply.")]:
    text(s,10.94,y,1.55,.28,head,12,WHITE,True)
    text(s,10.94,y+.31,1.52,.6,sub,9,RGBColor(190,205,200))
source(s,"Team facts: repository roster. Timing evidence: APEDA workflow; [F01] farmer information WTP; [G01–G03] advisory-market and liability evidence.")

# 5 — CLOSE
s = prs.slides.add_slide(blank); add_bg(s,True); transition(s, "fade", 850); chrome(s,5,"Thank You",True)
text(s,.58,.78,4.0,.3,"THANK YOU",11,LIME,True)
text(s,.58,1.42,11.5,1.25,"Level 1 is not where\nwe prove the machine.",36,WHITE,True,DISPLAY)
text(s,.58,3.0,11.5,.78,"It is where we prove whether a customer problem, payer and decision are real.",20,RGBColor(210,221,216),True)
# commitment blocks
for i,(n,a,b) in enumerate([("40–50","conversations","across the stakeholder chain"),("H1–H8","falsifiable hypotheses","validated / invalidated / unclear"),("1+","real advancement","intro, time, pilot slot or ₹")]):
    x=.58+i*4.05
    rect(s,x,4.25,3.62,1.45,RGBColor(25,43,52),radius=1,line=RGBColor(55,79,82))
    text(s,x+.25,4.48,1.05,.42,n,24,LIME,True,DISPLAY)
    text(s,x+1.32,4.47,2.0,.3,a,11,WHITE,True)
    text(s,x+1.32,4.82,2.0,.52,b,9,RGBColor(190,205,200))
text(s,.58,6.18,11.7,.38,"Our next action: listen, quantify, falsify — then decide go, pivot or stop.",14,WHITE,True)
source(s,"Discovery targets and guardrails: repository CUSTOMER_DISCOVERY_KIT.md. No field validation or prototype claim.",True)

# strip empty initial slide if any (Presentation starts with zero slides)
prs.save(OUT)
print(OUT)
