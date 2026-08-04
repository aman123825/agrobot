"""Asset generator for the AgriRover GrowwXIITB deck.

Renders (with Pillow only) all the raster art used by the presentation:
  - gradient backgrounds with soft glows + a faint dot grid
  - an illustrated rover graphic
  - a set of clean line-icons

Everything is deterministic and self-contained (no network, no external art),
so the build is reproducible and error-free.
"""
from __future__ import annotations

import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- palette ----
INK     = (9, 16, 12)      # near-black forest
INK2    = (13, 24, 17)
PANEL   = (18, 34, 24)
GREEN   = (46, 125, 50)
GREEN_D = (24, 74, 34)
GREEN_L = (102, 187, 106)
LIME    = (198, 255, 0)
MINT    = (34, 227, 140)
SKY     = (33, 118, 210)
BROWN   = (94, 66, 47)
BROWN_D = (66, 45, 32)
CLOUD   = (233, 240, 235)
MUTE    = (150, 170, 158)
WHITE   = (255, 255, 255)


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(w, h, top, bottom):
    """Vertical gradient (fast row loop)."""
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        d.line([(0, y), (w, y)], fill=_lerp(top, bottom, y / max(1, h - 1)))
    return img


def glow(img, cx, cy, radius, color, alpha):
    """Composite a soft radial glow onto img."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
              fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(radius * 0.42))
    img.paste(layer, (0, 0), layer)
    return img


def dot_grid(img, step=46, r=1, color=(255, 255, 255), alpha=16):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(step, img.size[1], step):
        for x in range(step, img.size[0], step):
            d.ellipse([x - r, y - r, x + r, y + r], fill=color + (alpha,))
    img.paste(layer, (0, 0), layer)
    return img


def circuit_lines(img, color=LIME, alpha=26):
    """A few faint tech traces + nodes for texture."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    w, h = img.size
    segs = [
        [(int(w * 0.06), int(h * 0.82)), (int(w * 0.20), int(h * 0.82)),
         (int(w * 0.26), int(h * 0.74)), (int(w * 0.40), int(h * 0.74))],
        [(int(w * 0.72), int(h * 0.14)), (int(w * 0.86), int(h * 0.14)),
         (int(w * 0.90), int(h * 0.22)), (int(w * 0.98), int(h * 0.22))],
        [(int(w * 0.80), int(h * 0.9)), (int(w * 0.88), int(h * 0.9)),
         (int(w * 0.92), int(h * 0.83))],
    ]
    for pts in segs:
        d.line(pts, fill=color + (alpha,), width=3, joint="curve")
        for p in (pts[0], pts[-1]):
            d.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6],
                      fill=color + (alpha + 30,))
    img.paste(layer, (0, 0), layer)
    return img


# ------------------------------------------------------------ backgrounds ----
def make_title_bg(path, mirror=False):
    w, h = 1920, 1080
    img = vgrad(w, h, (11, 22, 15), (6, 12, 9))
    if not mirror:
        glow(img, int(w * 0.16), int(h * 0.90), 620, GREEN, 120)
        glow(img, int(w * 0.90), int(h * 0.12), 520, MINT, 70)
        glow(img, int(w * 0.83), int(h * 0.85), 360, LIME, 45)
    else:
        glow(img, int(w * 0.86), int(h * 0.88), 640, GREEN, 120)
        glow(img, int(w * 0.12), int(h * 0.14), 520, MINT, 70)
        glow(img, int(w * 0.16), int(h * 0.82), 340, LIME, 45)
    dot_grid(img)
    circuit_lines(img)
    img.save(path)


def make_content_bg(path):
    w, h = 1920, 1080
    img = vgrad(w, h, (12, 23, 16), (8, 15, 11))
    glow(img, int(w * 0.96), int(h * 0.06), 460, GREEN, 60)
    glow(img, int(w * 0.02), int(h * 0.98), 460, GREEN_D, 60)
    dot_grid(img, step=54, alpha=10)
    img.save(path)


def make_section_bg(path):
    w, h = 1920, 1080
    img = vgrad(w, h, (18, 52, 30), (7, 16, 11))
    glow(img, int(w * 0.82), int(h * 0.80), 620, GREEN, 130)
    glow(img, int(w * 0.14), int(h * 0.20), 460, MINT, 70)
    dot_grid(img, step=50, alpha=12)
    circuit_lines(img, alpha=30)
    img.save(path)


# -------------------------------------------------------- rover illustration -
def make_rover(path):
    S = 2
    W, H = 1500 * S, 1040 * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def rr(box, radius, **kw):
        d.rounded_rectangle([c * S for c in box], radius=radius * S, **kw)

    def circle(cx, cy, r, **kw):
        d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], **kw)

    # ground shadow
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.ellipse([260 * S, 830 * S, 1240 * S, 940 * S], fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(26 * S))
    img.alpha_composite(sh)

    # soil strip + sprouts
    rr((0, 812, 1500, 980), 0, fill=BROWN + (255,))
    rr((0, 812, 1500, 838), 0, fill=(120, 84, 60, 255))
    for sx in (250, 470, 1040, 1270):
        d.line([(sx * S, 812 * S), (sx * S, 760 * S)], fill=GREEN_L + (255,),
               width=7 * S)
        circle(sx - 16, 756, 16, fill=GREEN + (255,))
        circle(sx + 16, 748, 15, fill=GREEN_L + (255,))

    # wheels
    def wheel(cx, cy, r):
        circle(cx, cy, r, fill=(20, 20, 20, 255))
        circle(cx, cy, r - 18, outline=(44, 44, 44, 255), width=10 * S)
        circle(cx, cy, r * 0.52, fill=(30, 30, 30, 255),
               outline=LIME + (255,), width=8 * S)
        circle(cx, cy, r * 0.16, fill=LIME + (255,))
        for a in range(0, 360, 45):
            rad = math.radians(a)
            x1 = cx + math.cos(rad) * r * 0.2
            y1 = cy + math.sin(rad) * r * 0.2
            x2 = cx + math.cos(rad) * r * 0.5
            y2 = cy + math.sin(rad) * r * 0.5
            d.line([(x1 * S, y1 * S), (x2 * S, y2 * S)],
                   fill=(70, 70, 70, 255), width=6 * S)

    wheel(470, 812, 120)
    wheel(1030, 812, 120)

    # chassis
    rr((300, 560, 1200, 770), 44, fill=GREEN_D + (255,))
    rr((300, 560, 1200, 640), 44, fill=GREEN + (255,))
    rr((316, 574, 1184, 610), 30, fill=(78, 150, 84, 255))  # highlight
    # side vents
    for vx in range(360, 520, 40):
        d.line([(vx * S, 690 * S), (vx * S, 745 * S)],
               fill=(15, 45, 22, 255), width=6 * S)

    # top deck
    rr((360, 470, 1140, 566), 26, fill=(20, 40, 27, 255))
    # solar panel
    rr((378, 486, 720, 556), 12, fill=SKY + (255,))
    for gx in range(378, 720, 46):
        d.line([(gx * S, 486 * S), (gx * S, 556 * S)], fill=(12, 60, 120, 255),
               width=4 * S)
    for gy in range(486, 556, 22):
        d.line([(378 * S, gy * S), (720 * S, gy * S)], fill=(12, 60, 120, 255),
               width=4 * S)
    # electronics box + LEDs
    rr((760, 486, 1120, 556), 12, fill=(16, 30, 22, 255),
       outline=(40, 70, 50, 255), width=3 * S)
    for i, col in enumerate([LIME, MINT, (255, 90, 90), CLOUD]):
        circle(792 + i * 34, 508, 9, fill=col + (255,))
    rr((792, 528, 1096, 546), 8, fill=(30, 55, 40, 255))

    # camera mast + head
    rr((690, 300, 726, 480), 16, fill=(70, 78, 74, 255))
    rr((640, 250, 800, 350), 20, fill=(22, 28, 24, 255),
       outline=(60, 70, 62, 255), width=3 * S)
    circle(742, 300, 40, fill=(10, 12, 11, 255))
    circle(742, 300, 26, fill=(18, 40, 46, 255), outline=LIME + (255,),
           width=6 * S)
    circle(742, 300, 10, fill=LIME + (255,))
    # camera glow
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(gl).ellipse([(742 - 70) * S, (300 - 70) * S,
                                (742 + 70) * S, (300 + 70) * S],
                               fill=LIME + (60,))
    gl = gl.filter(ImageFilter.GaussianBlur(24 * S))
    img.alpha_composite(gl)

    # antenna + signal arcs
    d.line([(1090 * S, 486 * S), (1150 * S, 320 * S)],
           fill=(150, 160, 152, 255), width=7 * S)
    circle(1150, 312, 14, fill=LIME + (255,))
    for rr_ in (44, 70, 96):
        d.arc([(1150 - rr_) * S, (312 - rr_) * S,
                (1150 + rr_) * S, (312 + rr_) * S],
              start=-70, end=10, fill=MINT + (200,), width=5 * S)

    # spray arm + droplets (front-left)
    d.line([(320 * S, 660 * S), (232 * S, 700 * S)],
           fill=(150, 160, 152, 255), width=9 * S)
    circle(226, 702, 14, fill=(60, 70, 62, 255))
    for i, (dx, dy) in enumerate([(-40, 60), (-8, 78), (28, 70), (-24, 108),
                                  (10, 118)]):
        circle(226 + dx, 702 + dy, 6 + (i % 2) * 2, fill=SKY + (220,))

    # NPK probe (angled spike into soil, right side)
    d.line([(1150 * S, 700 * S), (1250 * S, 852 * S)],
           fill=(180, 188, 182, 255), width=12 * S)
    d.polygon([(1236 * S, 838 * S), (1264 * S, 838 * S), (1250 * S, 878 * S)],
              fill=(120, 128, 122, 255))

    img = img.resize((1500, 1040), Image.LANCZOS)
    img.save(path)


# ------------------------------------------------------------------- icons ---
def _icon_canvas():
    s = 4
    size = 240
    img = Image.new("RGBA", (size * s, size * s), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img), s, size


def _finish(img, size, path):
    img = img.resize((size, size), Image.LANCZOS)
    img.save(path)


def draw_icon(name, color, path):
    img, d, s, size = _icon_canvas()
    c = color + (255,)
    lw = 12 * s

    def L(pts, width=lw):
        d.line([(x * s, y * s) for x, y in pts], fill=c, width=width,
               joint="curve")

    def E(box, width=lw, fill=None):
        b = [v * s for v in box]
        d.ellipse(b, outline=c, width=width, fill=fill)

    def RRO(box, rad, width=lw, fill=None):
        b = [v * s for v in box]
        d.rounded_rectangle(b, radius=rad * s, outline=c, width=width, fill=fill)

    if name == "camera":
        RRO([34, 78, 206, 188], 22)
        d.polygon([(v * s) for p in [(92, 78), (110, 56), (150, 56), (168, 78)]
                   for v in p], outline=c, width=lw)
        E([94, 96, 166, 168])
        E([120, 122, 140, 142], fill=c)
    elif name == "chip":
        RRO([66, 66, 174, 174], 16)
        RRO([96, 96, 144, 144], 8)
        for x in (96, 120, 144):
            L([(x, 40), (x, 66)]); L([(x, 174), (x, 200)])
            L([(40, x), (66, x)]); L([(174, x), (200, x)])
    elif name == "shield":
        pts = [(120, 34), (196, 66), (196, 128), (120, 208), (44, 128),
               (44, 66)]
        d.polygon([v * s for p in pts for v in p], outline=c, width=lw)
        L([(86, 122), (112, 150), (162, 92)])
    elif name == "pin":
        E([70, 44, 170, 144])
        d.polygon([120 * s, 208 * s, 78 * s, 120 * s, 162 * s, 120 * s],
                  outline=c, width=lw)
        E([104, 78, 136, 110], fill=c)
    elif name == "drop":
        d.polygon([120 * s, 40 * s, 176 * s, 150 * s, 64 * s, 150 * s],
                  outline=None, fill=None)
        # teardrop: triangle top + arc bottom
        d.pieslice([64 * s, 96 * s, 176 * s, 208 * s], 0, 360, outline=c,
                   width=lw)
        d.polygon([120 * s, 40 * s, 150 * s, 128 * s, 90 * s, 128 * s], fill=c)
        d.pieslice([64 * s, 96 * s, 176 * s, 208 * s], 0, 360, fill=c)
    elif name == "thermo":
        RRO([104, 40, 136, 150], 16)
        E([92, 146, 148, 202], fill=c)
        L([(120, 74), (120, 150)], width=8 * s)
    elif name == "bolt":
        pts = [(134, 34), (78, 130), (116, 130), (104, 208), (166, 106),
               (126, 106)]
        d.polygon([v * s for p in pts for v in p], fill=c)
    elif name == "leaf":
        d.pieslice([54 * s, 54 * s, 200 * s, 200 * s], 90, 270, fill=c)
        d.pieslice([40 * s, 40 * s, 186 * s, 186 * s], 270, 90, fill=c)
        L([(76, 176), (168, 76)], width=8 * s)  # vein (drawn over -> subtractive look)
    elif name == "gauge":
        d.arc([44 * s, 60 * s, 196 * s, 212 * s], 180, 360, fill=c, width=lw)
        L([(120, 136), (168, 96)])
        E([110, 126, 130, 146], fill=c)
        for a in (200, 235, 270, 305, 340):
            rad = math.radians(a)
            x1 = 120 + math.cos(rad) * 66; y1 = 136 + math.sin(rad) * 66
            x2 = 120 + math.cos(rad) * 78; y2 = 136 + math.sin(rad) * 78
            L([(x1, y1), (x2, y2)], width=6 * s)
    elif name == "robot":
        RRO([56, 74, 184, 190], 24)
        L([(120, 44), (120, 74)])
        E([108, 30, 132, 54], fill=c)
        E([86, 108, 114, 136], fill=c)
        E([126, 108, 154, 136], fill=c)
        L([(96, 162), (144, 162)])
    elif name == "rupee":
        E([40, 40, 200, 200])
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/seguisb.ttf", 150 * s)
            tb = d.textbbox((0, 0), "₹", font=font)
            tw, th = tb[2] - tb[0], tb[3] - tb[1]
            d.text(((240 * s - tw) / 2 - tb[0], (240 * s - th) / 2 - tb[1]),
                   "₹", font=font, fill=c)
        except Exception:
            L([(96, 80), (150, 80)]); L([(96, 108), (150, 108)])
            L([(96, 80), (96, 130)]); L([(96, 130), (150, 176)])
    elif name == "target":
        E([50, 50, 190, 190])
        E([86, 86, 154, 154])
        E([112, 112, 128, 128], fill=c)
        L([(120, 30), (120, 66)]); L([(120, 174), (120, 210)])
        L([(30, 120), (66, 120)]); L([(174, 120), (210, 120)])
    elif name == "wave":
        for i, yy in enumerate((150,)):
            pass
        E([104, 178, 136, 210], fill=c)
        for rr_ in (44, 78, 112):
            d.arc([(120 - rr_) * s, (194 - rr_) * s, (120 + rr_) * s,
                    (194 + rr_) * s], 210, 330, fill=c, width=lw)
    _finish(img, size, path)


ICONS = ["camera", "chip", "shield", "pin", "drop", "thermo", "bolt",
         "leaf", "gauge", "robot", "rupee", "target", "wave"]


def main():
    make_title_bg(os.path.join(OUT, "title_bg.png"))
    make_title_bg(os.path.join(OUT, "close_bg.png"), mirror=True)
    make_content_bg(os.path.join(OUT, "content_bg.png"))
    make_section_bg(os.path.join(OUT, "section_bg.png"))
    make_rover(os.path.join(OUT, "rover.png"))
    for ic in ICONS:
        draw_icon(ic, LIME, os.path.join(OUT, f"ic_{ic}.png"))
        draw_icon(ic, WHITE, os.path.join(OUT, f"icw_{ic}.png"))
    print("assets written to", OUT)


if __name__ == "__main__":
    main()
