"""Generates the block diagrams used in the IEI full-length paper.

Fig. 1  Two-brain control architecture (supervisory Pi + real-time ESP32).
Fig. 2  Safety interlock chain and the drive-inhibit event mask.

Run:  python paper/experiments/make_diagrams.py
"""
from __future__ import annotations

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO, "paper", "figures")

INK = "#111111"
LINE = "#5a5a5a"
FILL_SUP = "#eef2ee"
FILL_RT = "#e6ece6"
FILL_HW = "#f6f6f4"
EDGE = "#2f4f34"
ACCENT = "#166534"
DANGER = "#8c2f2f"


PAD_X = 0.022   # breathing space kept inside each vertical box edge


def text_width(ax, s, fs, weight):
    """Width of one line of text, in the data units the boxes are laid out in.

    Measured with the real renderer rather than estimated: the diagrams are
    dense, and a label that is one per cent too wide crosses a box border.
    """
    r = ax.figure.canvas.get_renderer()
    probe = ax.text(0, 0, s, fontsize=fs, fontweight=weight)
    bb = probe.get_window_extent(renderer=r)
    probe.remove()
    inv = ax.transData.inverted()
    (x0, _), (x1, _) = inv.transform([(0, 0), (bb.width, 0)])
    return x1 - x0


def fit_fontsize(ax, text, w, fs, weight):
    """Largest size at or below fs whose longest line fits inside width w."""
    avail = w - 2 * PAD_X
    widest = max(text_width(ax, ln, fs, weight)
                 for ln in text.split("\n") if ln.strip())
    if widest <= avail:
        return fs
    return max(4.4, fs * avail / widest)


def row_fontsize(ax, texts, w, fs, weight="normal"):
    """One size that fits every label in a row of equal-width boxes.

    Sizing each box independently makes a row of siblings read as a hierarchy
    it does not have: the longest identifier shrinks and its neighbours do not.
    """
    return min(fit_fontsize(ax, t, w, fs, weight) for t in texts)


def box(ax, x, y, w, h, text, fill, fs=6.6, weight="normal", edge=EDGE, lw=0.7):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.0,rounding_size=0.02",
        linewidth=lw, edgecolor=edge, facecolor=fill))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fit_fontsize(ax, text, w, fs, weight), color=INK,
            fontweight=weight, linespacing=1.35)


def arrow(ax, p, q, text=None, fs=5.8, color=LINE, style="-|>", dash=None):
    ax.add_patch(FancyArrowPatch(
        p, q, arrowstyle=style, mutation_scale=7, linewidth=0.75,
        color=color, linestyle=dash or "solid",
        shrinkA=1, shrinkB=1))
    if text:
        ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + 0.012, text,
                ha="center", va="bottom", fontsize=fs, color=color)


def canvas(w, h):
    fig, ax = plt.subplots(figsize=(w, h), dpi=220)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def track(x0, x1, n, gap):
    """Left edges and common width of n boxes evenly spaced between x0 and x1."""
    w = ((x1 - x0) - (n - 1) * gap) / n
    return [x0 + i * (w + gap) for i in range(n)], w


# Page frame and the inset used inside a layer container.
FRAME_L, FRAME_R = 0.035, 0.965
IN_L, IN_R = 0.052, 0.948


def fig1():
    fig, ax = canvas(7.0, 5.2)

    # Centred over the layers below, with its annotation on a line of its own:
    # a left-aligned label beside this box collides with the box text.
    box(ax, 0.285, 0.928, 0.43, 0.056,
        "Farmer / agronomist  ·  Telegram bot, web UI", FILL_HW, 6.6, "bold")
    ax.text(0.500, 0.994, "advisory reports  ·  remote stop  ·  status queries",
            ha="center", va="bottom", fontsize=6.2, color=LINE)

    # Supervisory layer
    ax.add_patch(FancyBboxPatch((FRAME_L, 0.575), FRAME_R - FRAME_L, 0.315,
                 boxstyle="round,pad=0.004,rounding_size=0.02",
                 linewidth=0.8, edgecolor=EDGE, facecolor=FILL_SUP))
    ax.text(IN_L, 0.862, "SUPERVISORY LAYER  —  Raspberry Pi 5 (Linux, Python)",
            fontsize=7.2, fontweight="bold", color=ACCENT, va="center")

    xs, w = track(IN_L, IN_R, 4, 0.012)
    sup_top = (
        "Perception\nYOLOv8n-INT8 weed +\nobstacle detection",
        "Classification\nMobileNetV2, 38-class\nPlantVillage disease",
        "Accelerator abstraction\nHailo-8L HEF → Coral\nEdge TPU → CPU INT8",
        "Aimed spray targeting\npinhole back-projection +\npan/tilt solution",
    )
    sup_bot = (
        "Localisation\n3-state pose EKF,\nodometry + gyro + GNSS",
        "Mission planning\nboustrophedon coverage,\ncross-track guidance",
        "Evidence store\nplant DB, black-box log,\nISO 11783-10 export",
        "Health + savings\nthermal, current, disk,\nper-acre chemical audit",
    )
    # One size across both rows of the layer, so the eight peer capabilities
    # are set at the same weight on the page.
    sup_fs = row_fontsize(ax, sup_top + sup_bot, w, 6.2)
    for x, txt in zip(xs, sup_top):
        box(ax, x, 0.752, w, 0.092, txt, "#ffffff", sup_fs)

    for x, txt in zip(xs, sup_bot):
        box(ax, x, 0.636, w, 0.092, txt, "#ffffff", sup_fs)

    # Links
    arrow(ax, (0.455, 0.928), (0.455, 0.894))
    arrow(ax, (0.545, 0.894), (0.545, 0.928))

    lxs, lw = track(IN_L, IN_R, 2, 0.030)
    box(ax, lxs[0], 0.470, lw, 0.062,
        "UART 115200 baud\nHMAC-SHA256/128 signed, monotonic counter", FILL_HW, 6.2)
    box(ax, lxs[1], 0.470, lw, 0.062,
        "MQTT over TLS, port 8883\nper-rover topic ACL, Mosquitto on the Pi", FILL_HW, 6.2)
    # The labels are set beside the arrows rather than above them: centred over
    # a 43 pt gap they land on the container border and read as struck through.
    arrow(ax, (0.265, 0.570), (0.265, 0.532))
    arrow(ax, (0.740, 0.532), (0.740, 0.570))
    ax.text(0.277, 0.551, "commands", ha="left", va="center",
            fontsize=5.8, color=LINE)
    ax.text(0.728, 0.551, "telemetry", ha="right", va="center",
            fontsize=5.8, color=LINE)

    # Real-time layer
    ax.add_patch(FancyBboxPatch((FRAME_L, 0.205), FRAME_R - FRAME_L, 0.235,
                 boxstyle="round,pad=0.004,rounding_size=0.02",
                 linewidth=0.8, edgecolor=EDGE, facecolor=FILL_RT))
    ax.text(IN_L, 0.415, "REAL-TIME LAYER  —  ESP32 DevKit V1 (FreeRTOS, dual core)",
            fontsize=7.2, fontweight="bold", color=ACCENT, va="center")

    rxs, rw = track(IN_L, IN_R, 3, 0.014)
    rt_tasks = (
        "Core 1 · driveTask · 50 Hz\nskid-steer PWM, gated by\nEVT_DRIVE_INHIBIT",
        "Core 0 · sensorTask · 5 Hz\nModbus NPK, DHT22, GNSS,\nADC oversampling ×16",
        "Dosing state machine\npre-soak 1500 ms · dwell 800 ms ·\ninject 1500 ms · travel 4000 ms",
    )
    rt_fs = row_fontsize(ax, rt_tasks, rw, 6.2)
    for x, txt in zip(rxs, rt_tasks):
        box(ax, x, 0.297, rw, 0.092, txt, "#ffffff", rt_fs)

    box(ax, IN_L, 0.223, IN_R - IN_L, 0.058,
        "FreeRTOS event group  ·  9 event bits  ·  task watchdog 5 s  ·  "
        "command dead-man 1500 ms  ·  signature-failure lockout", "#ffffff", 5.9)

    arrow(ax, (0.265, 0.470), (0.265, 0.440))
    arrow(ax, (0.740, 0.440), (0.740, 0.470))

    # Hardware
    hxs, hw = track(FRAME_L, FRAME_R, 3, 0.016)
    hardware = (
        "Drive\n2 × BTS7960 half-bridge,\n4 × 12 V geared motors",
        "Application\nperistaltic pump, linear\nactuator, pan/tilt nozzle",
        "Sensing\nVL53L1X ToF, HC-SR04, IMU,\nencoders, INA219, GNSS",
    )
    hw_fs = row_fontsize(ax, hardware, hw, 6.2)
    for x, txt in zip(hxs, hardware):
        box(ax, x, 0.096, hw, 0.082, txt, FILL_HW, hw_fs)
    for x in (hxs[0] + hw / 2, hxs[1] + hw / 2, hxs[2] + hw / 2):
        arrow(ax, (x, 0.205), (x, 0.178))

    box(ax, FRAME_L, 0.004, FRAME_R - FRAME_L, 0.072,
        "INDEPENDENT SAFETY PATH\nLatching mushroom E-stop wired to the ESP32 EN pin  ·  relay coils "
        "de-energised at boot  ·  no software element can override it",
        "#fbf1f1", 6.3, "bold", DANGER, 0.9)

    fig.savefig(os.path.join(OUT, "fig1_architecture.png"), bbox_inches="tight")
    plt.close(fig)


def fig2():
    fig, ax = canvas(7.2, 3.5)
    ax.set_xlim(-0.012, 1.012)

    triggers = [
        ("E-stop pressed\nor tilt limit", "EVT_HALT"),
        ("Pack below\n9.9 V cutoff", "EVT_LOW_BATTERY"),
        ("Dosing sequence\nin progress", "EVT_DOSING"),
        ("Obstacle inside\n250 mm envelope", "EVT_OBSTACLE"),
        ("No signed command\nfor 1500 ms", "EVT_LINK_LOST"),
        ("Die temperature\nat or above 85 °C", "EVT_OVERTEMP"),
    ]
    xs, w = track(0.014, 0.986, 6, 0.013)
    cause_fs = row_fontsize(ax, [c for c, _ in triggers], w, 6.0)
    bit_fs = row_fontsize(ax, [b for _, b in triggers], w, 5.8, "bold")
    for x, (cause, bit) in zip(xs, triggers):
        box(ax, x, 0.775, w, 0.16, cause, "#ffffff", cause_fs)
        box(ax, x, 0.585, w, 0.115, bit, FILL_RT, bit_fs, "bold")
        arrow(ax, (x + w / 2, 0.775), (x + w / 2, 0.700))
        arrow(ax, (x + w / 2, 0.585), (x + w / 2, 0.470))

    box(ax, 0.014, 0.360, 0.972, 0.100,
        "EVT_DRIVE_INHIBIT  =  logical OR of the six bits above   "
        "(single definition in firmware/include/events.h)",
        FILL_SUP, 6.8, "bold")

    cxs, cw = track(0.014, 0.986, 3, 0.016)
    consumers = (
        "driveTask, 50 Hz\ntests the mask before every\nPWM write → motors to 0",
        "dosingTask\nasserts EVT_DOSING for the\nwhole sequence duration",
        "Supervisory layer\nfail-safe stop when ToF\nrange is unavailable",
    )
    cons_fs = row_fontsize(ax, consumers, cw, 6.2)
    for x, txt in zip(cxs, consumers):
        box(ax, x, 0.190, cw, 0.115, txt, "#ffffff", cons_fs)
    for x in cxs:
        arrow(ax, (x + cw / 2, 0.360), (x + cw / 2, 0.305))

    box(ax, 0.014, 0.030, 0.972, 0.115,
        "DESIGN INVARIANT — the real-time layer never waits for the supervisory layer.\n"
        "Loss of camera, model, network or Pi resolves to a stop, never to continued motion or an uncommanded dose.",
        "#fbf1f1", 6.8, "bold", DANGER, 0.9)

    fig.savefig(os.path.join(OUT, "fig2_safety_chain.png"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig1()
    fig2()
    print("wrote fig1_architecture.png and fig2_safety_chain.png to", OUT)
