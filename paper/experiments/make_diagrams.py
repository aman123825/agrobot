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


def box(ax, x, y, w, h, text, fill, fs=6.6, weight="normal", edge=EDGE, lw=0.7):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02",
        linewidth=lw, edgecolor=edge, facecolor=fill))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color=INK, fontweight=weight, linespacing=1.35)


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


def fig1():
    fig, ax = canvas(7.0, 5.2)

    # Centred over the layers below, with its annotation on a line of its own:
    # a left-aligned label beside this box collides with the box text.
    box(ax, 0.315, 0.930, 0.37, 0.058,
        "Farmer / agronomist  ·  Telegram bot, web UI", FILL_HW, 6.6, "bold")
    ax.text(0.500, 1.002, "advisory reports  ·  remote stop  ·  status queries",
            ha="center", va="bottom", fontsize=6.2, color=LINE)

    # Supervisory layer
    ax.add_patch(FancyBboxPatch((0.035, 0.575), 0.93, 0.315,
                 boxstyle="round,pad=0.004,rounding_size=0.02",
                 linewidth=0.8, edgecolor=EDGE, facecolor=FILL_SUP))
    ax.text(0.055, 0.862, "SUPERVISORY LAYER  —  Raspberry Pi 5 (Linux, Python)",
            fontsize=7.2, fontweight="bold", color=ACCENT, va="center")

    box(ax, 0.055, 0.755, 0.20, 0.088,
        "Perception\nYOLOv8n-INT8 weed +\nobstacle detection", "#ffffff", 6.2)
    box(ax, 0.265, 0.755, 0.20, 0.088,
        "Classification\nMobileNetV2, 38-class\nPlantVillage disease", "#ffffff", 6.2)
    box(ax, 0.475, 0.755, 0.20, 0.088,
        "Accelerator abstraction\nHailo-8L HEF → Coral\nEdge TPU → CPU INT8", "#ffffff", 6.2)
    box(ax, 0.685, 0.755, 0.265, 0.088,
        "Aimed spray targeting\npinhole back-projection +\npan/tilt solution", "#ffffff", 6.2)

    box(ax, 0.055, 0.640, 0.20, 0.088,
        "Localisation\n3-state pose EKF,\nodometry + gyro + GNSS", "#ffffff", 6.2)
    box(ax, 0.265, 0.640, 0.20, 0.088,
        "Mission planning\nboustrophedon coverage,\ncross-track guidance", "#ffffff", 6.2)
    box(ax, 0.475, 0.640, 0.20, 0.088,
        "Evidence store\nplant DB, black-box log,\nISO 11783-10 export", "#ffffff", 6.2)
    box(ax, 0.685, 0.640, 0.265, 0.088,
        "Health + savings\nthermal, current, disk,\nper-acre chemical audit", "#ffffff", 6.2)

    # Links
    arrow(ax, (0.455, 0.930), (0.455, 0.893))
    arrow(ax, (0.545, 0.893), (0.545, 0.930))

    box(ax, 0.055, 0.470, 0.42, 0.062,
        "UART 115200 baud\nHMAC-SHA256/128 signed, monotonic counter", FILL_HW, 6.2)
    box(ax, 0.530, 0.470, 0.42, 0.062,
        "MQTT over TLS, port 8883\nper-rover topic ACL, Mosquitto on the Pi", FILL_HW, 6.2)
    arrow(ax, (0.265, 0.575), (0.265, 0.534), "commands")
    arrow(ax, (0.740, 0.534), (0.740, 0.575), "telemetry")

    # Real-time layer
    ax.add_patch(FancyBboxPatch((0.035, 0.205), 0.93, 0.235,
                 boxstyle="round,pad=0.004,rounding_size=0.02",
                 linewidth=0.8, edgecolor=EDGE, facecolor=FILL_RT))
    ax.text(0.055, 0.415, "REAL-TIME LAYER  —  ESP32 DevKit V1 (FreeRTOS, dual core)",
            fontsize=7.2, fontweight="bold", color=ACCENT, va="center")

    box(ax, 0.055, 0.300, 0.27, 0.088,
        "Core 1 · driveTask · 50 Hz\nskid-steer PWM, gated by\nEVT_DRIVE_INHIBIT", "#ffffff", 6.2)
    box(ax, 0.345, 0.300, 0.27, 0.088,
        "Core 0 · sensorTask · 5 Hz\nModbus NPK, DHT22, GNSS,\nADC oversampling ×16", "#ffffff", 6.2)
    box(ax, 0.635, 0.300, 0.315, 0.088,
        "Dosing state machine\npre-soak 1500 ms · dwell 800 ms ·\ninject 1500 ms · travel 4000 ms", "#ffffff", 6.2)
    box(ax, 0.055, 0.225, 0.895, 0.058,
        "FreeRTOS event group  ·  9 event bits  ·  task watchdog 5 s  ·  "
        "command dead-man 1500 ms  ·  signature-failure lockout", "#ffffff", 5.9)

    arrow(ax, (0.265, 0.470), (0.265, 0.440))
    arrow(ax, (0.740, 0.440), (0.740, 0.470))

    # Hardware
    box(ax, 0.035, 0.098, 0.30, 0.080,
        "Drive\n2 × BTS7960 half-bridge,\n4 × 12 V geared motors", FILL_HW, 6.2)
    box(ax, 0.350, 0.098, 0.30, 0.080,
        "Application\nperistaltic pump, linear\nactuator, pan/tilt nozzle", FILL_HW, 6.2)
    box(ax, 0.665, 0.098, 0.30, 0.080,
        "Sensing\nVL53L1X ToF, HC-SR04, IMU,\nencoders, INA219, GNSS", FILL_HW, 6.2)
    for x in (0.185, 0.500, 0.815):
        arrow(ax, (x, 0.205), (x, 0.178))

    box(ax, 0.035, 0.005, 0.93, 0.072,
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
    w = 0.152
    gap = 0.0145
    x0 = 0.014
    for i, (cause, bit) in enumerate(triggers):
        x = x0 + i * (w + gap)
        box(ax, x, 0.775, w, 0.16, cause, "#ffffff", 6.0)
        box(ax, x, 0.585, w, 0.115, bit, FILL_RT, 5.8, "bold")
        arrow(ax, (x + w / 2, 0.775), (x + w / 2, 0.700))
        arrow(ax, (x + w / 2, 0.585), (x + w / 2, 0.470))

    box(ax, 0.014, 0.360, 0.972, 0.100,
        "EVT_DRIVE_INHIBIT  =  logical OR of the six bits above   "
        "(single definition in firmware/include/events.h)",
        FILL_SUP, 6.8, "bold")

    box(ax, 0.014, 0.190, 0.306, 0.115,
        "driveTask, 50 Hz\ntests the mask before every\nPWM write → motors to 0",
        "#ffffff", 6.2)
    box(ax, 0.347, 0.190, 0.306, 0.115,
        "dosingTask\nasserts EVT_DOSING for the\nwhole sequence duration",
        "#ffffff", 6.2)
    box(ax, 0.680, 0.190, 0.306, 0.115,
        "Supervisory layer\nfail-safe stop when ToF\nrange is unavailable",
        "#ffffff", 6.2)
    for x in (0.167, 0.500, 0.833):
        arrow(ax, (x, 0.360), (x, 0.305))

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
