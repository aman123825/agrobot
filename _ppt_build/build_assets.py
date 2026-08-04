"""Generate all visual assets (PNG) for the AgriRover Groww x IITB deck.

Every figure is wrapped in try/except so one failure never blocks the rest.
Outputs go to _ppt_build/assets/.
"""
import os
import math
import traceback

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
import matplotlib.font_manager as fm

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(HERE, "assets")
os.makedirs(OUT, exist_ok=True)

# ---- Theme ----
INK     = "#12281C"   # dark text
FOREST  = "#0E3B2A"   # deep background green
GREEN   = "#1F9254"   # primary
LEAF    = "#6FBF44"   # secondary/highlight
AMBER   = "#F2A03D"   # accent / data
SKY     = "#2B9BD6"   # tech accent (electronics/AI)
PLUM    = "#6A4C93"   # compute
CLOUD   = "#F4F7F2"   # light bg
MIST    = "#E4EDE4"   # panel
GRAY    = "#64748B"
RED     = "#E4572E"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 13,
    "axes.edgecolor": GRAY,
    "text.color": INK,
    "axes.labelcolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "svg.fonttype": "none",
})

created = []


def save(fig, name, dpi=200, transparent=False):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", transparent=transparent,
                facecolor=fig.get_facecolor())
    plt.close(fig)
    created.append(name)
    print("  wrote", name)


def rbox(ax, x, y, w, h, text, fc, ec=None, tc="white", fs=12, bold=True, radius=0.06):
    ec = ec or fc
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle=f"round,pad=0.02,rounding_size={radius}",
                         linewidth=1.6, edgecolor=ec, facecolor=fc,
                         mutation_aspect=1)
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            color=tc, fontsize=fs, fontweight="bold" if bold else "normal",
            wrap=True, zorder=5)


def arrow(ax, p1, p2, color=GRAY, lw=2.0, style="-|>", ls="-"):
    a = FancyArrowPatch(p1, p2, arrowstyle=style, mutation_scale=16,
                        color=color, lw=lw, linestyle=ls,
                        shrinkA=2, shrinkB=2, zorder=1)
    ax.add_patch(a)


# =====================================================================
# 1. SYSTEM ARCHITECTURE (dual-controller)
# =====================================================================
def fig_architecture():
    fig, ax = plt.subplots(figsize=(12.6, 6.9))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis("off")

    # Power rail (top strip)
    rbox(ax, 0.4, 6.1, 3.7, 0.68, "3S LiPo 11.1V  >  Fuse + XT60  >  Buck 5V",
         AMBER, tc=INK, fs=8.6)
    rbox(ax, 4.25, 6.1, 2.45, 0.68, "Power Bank 10 000 mAh\n(isolated Pi rail)",
         AMBER, tc=INK, fs=8.5)

    # ESP32 block
    rbox(ax, 0.5, 2.95, 4.5, 2.45, "", "#EAF5EE", ec=GREEN, tc=INK)
    ax.text(2.75, 5.12, "ESP32 DevKit V1  ·  FreeRTOS", ha="center",
            color=GREEN, fontsize=12.5, fontweight="bold")
    rbox(ax, 0.8, 4.12, 1.95, 0.72, "Core 0\nsensing", GREEN, fs=9)
    rbox(ax, 2.95, 4.12, 1.85, 0.72, "Core 1\ndrive", GREEN, fs=9)
    ax.text(2.75, 3.52, "real-time · dosing · MQTT · watchdog · E-stop",
            ha="center", color=GRAY, fontsize=8, style="italic")

    # Pi block
    rbox(ax, 7.0, 2.95, 4.5, 2.45, "", "#E9F3FA", ec=SKY, tc=INK)
    ax.text(9.25, 5.12, "Raspberry Pi 4  ·  Python", ha="center",
            color=SKY, fontsize=12.5, fontweight="bold")
    rbox(ax, 7.3, 4.12, 1.95, 0.72, "YOLOv8n\nvision", SKY, fs=9)
    rbox(ax, 9.45, 4.12, 1.85, 0.72, "Coral TPU\n+ camera", SKY, fs=9)
    ax.text(9.25, 3.52, "obstacle · weed · disease · EKF nav · dashboard",
            ha="center", color=GRAY, fontsize=8, style="italic")

    # Secure link
    arrow(ax, (5.05, 4.3), (6.95, 4.3), color=PLUM, lw=2.6, style="<|-|>")
    ax.text(6.0, 4.62, "UART link", ha="center", color=PLUM, fontsize=9.5,
            fontweight="bold")
    ax.text(6.0, 4.02, "HMAC-signed · anti-replay", ha="center", color=PLUM,
            fontsize=7.6)

    # Power arrows
    arrow(ax, (1.9, 6.07), (2.0, 5.42), color=AMBER, lw=2)
    arrow(ax, (5.3, 6.07), (9.25, 5.42), color=AMBER, lw=2)

    # ESP32 I/O (bottom-left)
    rbox(ax, 0.4, 1.05, 1.95, 1.4,
         "DRIVE\n2× BTS7960\n→ 4 motors", GREEN, fs=8.5)
    rbox(ax, 2.5, 1.05, 2.05, 1.4,
         "SENSE\nNPK · GPS · DHT22\nmoisture · TDS · US", LEAF, tc=INK, fs=7.8)
    rbox(ax, 4.7, 1.05, 1.9, 1.4,
         "DOSE\npump +\nactuator", AMBER, tc=INK, fs=8.5)
    arrow(ax, (1.35, 2.93), (1.35, 2.47), color=GREEN, lw=1.8)
    arrow(ax, (3.5, 2.93), (3.5, 2.47), color=GREEN, lw=1.8)
    arrow(ax, (2.75, 2.93), (5.6, 2.47), color=GREEN, lw=1.8)

    # Pi I/O (bottom-right)
    rbox(ax, 6.95, 1.05, 1.95, 1.4,
         "MQTT (TLS)\ntelemetry bus", SKY, fs=9)
    rbox(ax, 9.05, 1.05, 1.2, 1.4, "Stream +\nDashboard", SKY, fs=8)
    rbox(ax, 10.35, 1.05, 1.15, 1.4, "Telegram\nalerts", SKY, fs=8)
    arrow(ax, (9.25, 2.93), (7.9, 2.47), color=SKY, lw=1.8)
    arrow(ax, (9.25, 2.93), (9.6, 2.47), color=SKY, lw=1.8)
    arrow(ax, (9.25, 2.93), (10.9, 2.47), color=SKY, lw=1.8)

    # Operator layer
    rbox(ax, 6.95, 0.2, 4.55, 0.56, "Farmer's phone / laptop  <  live field data",
         FOREST, fs=9)
    arrow(ax, (9.2, 1.03), (9.2, 0.78), color=GRAY, lw=1.5)

    save(fig, "architecture.png")


# =====================================================================
# 2. CHASSIS LAYOUT (from real mechanical-layout.md coordinates)
# =====================================================================
def fig_chassis():
    W, L = 320.0, 450.0  # mm
    zone_color = {
        "power": AMBER, "drive": RED, "fluid": SKY, "sensor": GREEN,
        "compute": PLUM, "mech": "#8A97A6", "ui": "#E6B800",
    }
    lower = [
        ("SW", 20, 20, 10, 8, "power"), ("XT60", 22, 16, 34, 10, "power"),
        ("Fuse", 30, 16, 10, 32, "power"), ("Buck", 43, 21, 10, 54, "power"),
        ("INA", 26, 18, 60, 54, "power"), ("Bus", 42, 18, 10, 80, "power"),
        ("Pump", 60, 40, 105, 18, "fluid"),
        ("Tank 500ml", 90, 70, 178, 12, "fluid"), ("Flt", 16, 16, 250, 18, "fluid"),
        ("Power bank", 70, 140, 10, 150, "power"),
        ("LiPo 3S", 34, 105, 150, 165, "power"),
        ("Relay", 51, 39, 250, 150, "drive"),
        ("ACS", 34, 22, 250, 300, "drive"),
        ("BTS1", 50, 50, 95, 372, "drive"),
        ("BTS2", 50, 50, 175, 372, "drive"),
    ]
    upper = [
        ("ESP32", 55, 28, 24, 24, "compute"),
        ("CAM", 40, 27, 24, 66, "compute"),
        ("Raspberry Pi 4", 85, 56, 120, 18, "compute"),
        ("Coral TPU", 65, 30, 218, 20, "compute"),
        ("Fan", 30, 30, 148, 80, "compute"),
        ("I2C sensors", 80, 58, 120, 150, "sensor"),
        ("485", 22, 15, 214, 160, "sensor"),
        ("LoRa", 18, 16, 246, 160, "compute"),
        ("OLED", 27, 27, 18, 378, "ui"),
        ("Mode", 20, 20, 66, 382, "ui"),
        ("Btns", 50, 14, 100, 386, "ui"),
        ("E-STOP", 28, 28, 180, 378, "ui"),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(11, 7))
    fig.patch.set_facecolor("white")
    for ax, comps, title in ((axes[0], lower, "Lower deck — power · drive · fluid"),
                             (axes[1], upper, "Upper deck — compute · sensors · UI")):
        ax.add_patch(Rectangle((0, 0), W, L, facecolor=CLOUD, edgecolor=INK, lw=2))
        for name, w, h, x, y, zone in comps:
            c = zone_color[zone]
            ax.add_patch(FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.4,rounding_size=3",
                         facecolor=c, edgecolor="white", lw=1.2, alpha=0.92))
            fs = 7.5 if max(w, h) >= 45 else (6.3 if max(w, h) >= 22 else 5.3)
            ax.text(x + w / 2, y + h / 2, name, ha="center", va="center",
                    color="white", fontsize=fs, fontweight="bold")
        ax.set_xlim(-12, W + 12)
        ax.set_ylim(L + 12, -12)  # flip so front (y=0) is at top
        ax.set_aspect("equal")
        ax.set_title(title, fontsize=11, fontweight="bold", color=INK, pad=8)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(False)
        ax.annotate("FRONT", (W / 2, -8), ha="center", va="bottom",
                    fontsize=8, color=GRAY, fontweight="bold")

    # legend
    from matplotlib.patches import Patch
    handles = [Patch(facecolor=zone_color[z], label=z.capitalize())
               for z in ["power", "drive", "fluid", "sensor", "compute", "ui", "mech"]]
    fig.legend(handles=handles, loc="lower center", ncol=7, frameon=False,
               fontsize=9, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("320 × 450 mm double-decker chassis (to scale)",
                 fontsize=12.5, fontweight="bold", color=GREEN, y=0.99)
    fig.tight_layout(rect=[0, 0.03, 1, 0.96])
    save(fig, "chassis_layout.png")


# =====================================================================
# 3. COST TIERS
# =====================================================================
def fig_cost():
    fig, ax = plt.subplots(figsize=(10, 4.4))
    fig.patch.set_facecolor("white")
    tiers = ["Core\n(demo)", "Core +\nNavigation", "Full AI\n(this build)"]
    lo = [8, 12, 28]
    hi = [14, 20, 49]
    colors = [LEAF, SKY, GREEN]
    y = range(len(tiers))
    for i in y:
        ax.barh(i, hi[i] - lo[i], left=lo[i], height=0.5,
                color=colors[i], edgecolor="white", zorder=3)
        ax.text(hi[i] + 0.7, i, f"Rs {lo[i]}k - {hi[i]}k", va="center",
                fontsize=11, fontweight="bold", color=INK)
    ax.set_yticks(list(y)); ax.set_yticklabels(tiers, fontsize=11)
    ax.set_xlim(0, 58)
    ax.set_xlabel("Approx. build cost  (Rs thousand, India market)", fontsize=10)
    ax.set_title("Modular build tiers — start small, scale to full autonomy",
                 fontsize=12.5, fontweight="bold", color=GREEN, loc="left")
    ax.grid(axis="x", color=MIST, zorder=0)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.invert_yaxis()
    fig.tight_layout()
    save(fig, "cost_tiers.png")


# =====================================================================
# 4. AI PERFORMANCE
# =====================================================================
def fig_ai():
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    fig.patch.set_facecolor("white")
    labels = ["CPU only", "Coral Edge TPU"]
    fps = [3, 30]
    bars = ax.bar(labels, fps, width=0.5, color=[GRAY, GREEN],
                  edgecolor="white", zorder=3)
    ax.axhline(15, color=AMBER, lw=2.2, ls="--", zorder=2)
    ax.text(1.46, 16, "15 FPS\nsafety floor", color=AMBER, fontsize=9.5,
            fontweight="bold", ha="right")
    for b, v in zip(bars, fps):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.7, f"~{v} FPS",
                ha="center", fontsize=12, fontweight="bold", color=INK)
    ax.set_ylim(0, 34)
    ax.set_ylabel("Inference speed (frames / sec)", fontsize=10)
    ax.set_title("10× faster on-device inference with the Coral Edge TPU",
                 fontsize=12.5, fontweight="bold", color=GREEN, loc="left")
    ax.grid(axis="y", color=MIST, zorder=0)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    save(fig, "ai_performance.png")


# =====================================================================
# 5. INPUT SAVINGS (precision vs blanket)
# =====================================================================
def fig_savings():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.4))
    fig.patch.set_facecolor("white")
    for ax, frac, title, col in ((a1, 1.0, "Blanket spraying", RED),
                                 (a2, 0.25, "AgriRover targeted", GREEN)):
        wedges, _ = ax.pie([frac, 1 - frac] if frac < 1 else [1, 0],
                           colors=[col, MIST], startangle=90,
                           counterclock=False,
                           wedgeprops=dict(width=0.38, edgecolor="white"))
        ax.text(0, 0, f"{int(frac*100)}%", ha="center", va="center",
                fontsize=22, fontweight="bold", color=col)
        ax.set_title(title, fontsize=11.5, fontweight="bold", color=INK)
    fig.suptitle("Spot-spray + micro-dosing can cut chemical use up to ~75%",
                 fontsize=12.5, fontweight="bold", color=GREEN, y=1.02)
    fig.text(0.5, -0.02, "Illustrative: vision-guided nozzle sprays only detected weeds",
             ha="center", fontsize=8.5, color=GRAY, style="italic")
    fig.tight_layout()
    save(fig, "savings.png")


# =====================================================================
# 6. SECURITY / DEFENSE-IN-DEPTH
# =====================================================================
def fig_security():
    fig, ax = plt.subplots(figsize=(10, 4.8))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 10); ax.set_ylim(0, 5); ax.axis("off")
    layers = [
        ("Physical E-stop halts everything on the ESP32 EN pin", FOREST),
        ("HMAC-SHA256 signed + anti-replay UART command link", GREEN),
        ("MQTT over TLS with auth + topic ACLs (no anonymous)", SKY),
        ("Secrets gitignored · ESP32 Secure Boot + Flash Encryption", AMBER),
        ("Hardened Pi: key-only SSH, firewall, least privilege", PLUM),
    ]
    for i, (txt, col) in enumerate(layers):
        y = 4.2 - i * 0.82
        rbox(ax, 0.5, y, 9.0, 0.62, txt, col,
             tc="white" if col != AMBER else INK, fs=10.5, radius=0.08)
    save(fig, "security.png")


# =====================================================================
# 7. Convert repo SVG diagrams (guarded)
# =====================================================================
def convert_svgs():
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
    except Exception as exc:
        print("  svglib unavailable:", exc)
        return
    jobs = [
        ("docs/wiring-v2.svg", "wiring.png"),
        ("docs/bts7960-drive-schematic.svg", "drive_schematic.png"),
        ("docs/chassis-layout.svg", "chassis_repo.png"),
    ]
    for src, dst in jobs:
        try:
            drawing = svg2rlg(os.path.join(REPO, src))
            if drawing is None:
                print("  could not parse", src)
                continue
            renderPM.drawToFile(drawing, os.path.join(OUT, dst), fmt="PNG", dpi=200)
            created.append(dst)
            print("  converted", src, "->", dst)
        except Exception:
            print("  SVG convert failed for", src)
            traceback.print_exc()


def main():
    for fn in (fig_architecture, fig_chassis, fig_cost, fig_ai,
               fig_savings, fig_security):
        try:
            fn()
        except Exception:
            print("FIGURE FAILED:", fn.__name__)
            traceback.print_exc()
    convert_svgs()
    print("\nAssets created:", len(created))
    for c in created:
        print("  -", c)


if __name__ == "__main__":
    main()
