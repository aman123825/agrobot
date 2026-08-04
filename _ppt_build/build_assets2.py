"""Impact & market charts for the business deck (themed to match assets)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets")
os.makedirs(OUT, exist_ok=True)

INK = "#12281C"; GREEN = "#1F9254"; DKGREEN = "#14532D"; LEAF = "#6FBF44"
AMBER = "#F2A03D"; SKY = "#2B9BD6"; GRAY = "#5B6B62"; MIST = "#E4EDE4"
BASE = "#E0934B"  # baseline / "before" (muted orange)

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12,
                     "text.color": INK, "axes.labelcolor": INK,
                     "xtick.color": INK, "ytick.color": INK})


def impact_charts():
    fig, ax = plt.subplots(1, 3, figsize=(11.4, 3.7))
    fig.patch.set_facecolor("white")

    # 1) fertilizer use per acre (kg)
    a = ax[0]
    bars = a.bar(["Broadcast", "AgriRover"], [100, 55], width=0.55,
                 color=[BASE, GREEN], edgecolor="white", zorder=3)
    for b, v in zip(bars, [100, 55]):
        a.text(b.get_x() + b.get_width() / 2, v + 2, str(v), ha="center",
               fontsize=12, fontweight="bold", color=INK)
    a.set_title("Fertiliser use / acre (kg)", fontsize=11.5, fontweight="bold",
                color=INK)
    a.text(0.5, 78, "–45%", ha="center", fontsize=14, fontweight="bold",
           color=GREEN)
    a.set_ylim(0, 115)

    # 2) input cost per acre / season
    a = ax[1]
    bars = a.bar(["Before", "With AgriRover"], [6000, 3600], width=0.55,
                 color=[BASE, GREEN], edgecolor="white", zorder=3)
    for b, v in zip(bars, [6000, 3600]):
        a.text(b.get_x() + b.get_width() / 2, v + 120, f"{v:,}", ha="center",
               fontsize=12, fontweight="bold", color=INK)
    a.set_title("Input cost / acre / season (₹)", fontsize=11.5,
                fontweight="bold", color=INK)
    a.text(0.5, 4700, "–40%", ha="center", fontsize=14, fontweight="bold",
           color=GREEN)
    a.set_ylim(0, 7000)

    # 3) farms served (3-yr projection)
    a = ax[2]
    bars = a.bar(["Yr 1", "Yr 2", "Yr 3"], [10, 80, 400], width=0.6,
                 color=[LEAF, GREEN, DKGREEN], edgecolor="white", zorder=3)
    for b, v in zip(bars, [10, 80, 400]):
        a.text(b.get_x() + b.get_width() / 2, v + 8, str(v), ha="center",
               fontsize=12, fontweight="bold", color=INK)
    a.set_title("Farms served (3-yr projection)", fontsize=11.5,
                fontweight="bold", color=INK)
    a.set_ylim(0, 450)

    for a in ax:
        a.grid(axis="y", color=MIST, zorder=0)
        for sp in ["top", "right"]:
            a.spines[sp].set_visible(False)
        a.tick_params(labelsize=10.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "impact_charts.png"), dpi=200,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote impact_charts.png")


def market_chart():
    fig, a = plt.subplots(figsize=(5.2, 3.4))
    fig.patch.set_facecolor("white")
    yrs = ["2025", "2034"]
    vals = [0.97, 2.5]
    bars = a.bar(yrs, vals, width=0.5, color=[LEAF, GREEN], edgecolor="white",
                 zorder=3)
    for b, v in zip(bars, vals):
        a.text(b.get_x() + b.get_width() / 2, v + 0.05, f"${v} Bn", ha="center",
               fontsize=12.5, fontweight="bold", color=INK)
    a.set_title("India agritech market  (~10.6% CAGR)", fontsize=11.5,
                fontweight="bold", color=INK)
    a.set_ylim(0, 3.0)
    a.grid(axis="y", color=MIST, zorder=0)
    for sp in ["top", "right"]:
        a.spines[sp].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "market_growth.png"), dpi=200,
                bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote market_growth.png")


if __name__ == "__main__":
    impact_charts()
    market_chart()
