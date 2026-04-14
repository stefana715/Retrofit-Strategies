"""
plot_baseline.py
================
Publication-quality grouped stacked bar chart of baseline EUI for the
three Changsha residential building archetypes.

Usage (standalone):
    python plot_baseline.py

Or called from run_baseline.py via importlib.

Output:
    figure/fig04_baseline_eui.png   (300 dpi, Energy & Buildings style)
"""

import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import MultipleLocator

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
DATA_PROC  = os.path.join(REPO_ROOT, "data", "processed")
FIGURE_DIR = os.path.join(REPO_ROOT, "figure")

BASELINE_CSV = os.path.join(DATA_PROC, "baseline_results.csv")
OUT_FIG      = os.path.join(FIGURE_DIR, "fig04_baseline_eui.png")

# ---------------------------------------------------------------------------
# Style constants (Energy & Buildings / Elsevier guidelines)
# ---------------------------------------------------------------------------
# Single-column width ≈ 3.5 in; double-column ≈ 7.2 in
FIG_W  = 7.0   # inches
FIG_H  = 4.5   # inches
DPI    = 300
FONT_S = 9     # base font size (pt)
FONT_L = 10    # axis-label font size
FONT_T = 11    # title font size

# Colour palette — colour-blind friendly (Wong 2011 palette)
COLORS = {
    "heating":   "#E69F00",   # orange
    "cooling":   "#56B4E9",   # sky blue
    "lighting":  "#009E73",   # green
    "fans":      "#F0E442",   # yellow
    "other":     "#CC79A7",   # mauve / pink
}

ERA_LABELS = {
    1: "Era 1\n(~1980s)",
    2: "Era 2\n(~2000s)",
    3: "Era 3\n(~2010s+)",
}


def plot_baseline_eui(df: pd.DataFrame, out_path: str = OUT_FIG) -> None:
    """
    Stacked bar chart: x = era, bars split by heating / cooling / other.

    Args:
        df:       DataFrame with columns era, heating_kwh_m2, cooling_kwh_m2,
                  fans_kwh_m2, lighting_kwh_m2, other_kwh_m2, total_eui_kwh_m2
        out_path: where to save the figure
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df = df.sort_values("era").reset_index(drop=True)

    # Build stacked components
    components = [
        ("heating_kwh_m2",   "Heating",             COLORS["heating"]),
        ("cooling_kwh_m2",   "Cooling",             COLORS["cooling"]),
        ("lighting_kwh_m2",  "Interior Lighting",   COLORS["lighting"]),
        ("fans_kwh_m2",      "Fans & Pumps",        COLORS["fans"]),
        ("other_kwh_m2",     "Other (Plug+Equip.)", COLORS["other"]),
    ]

    # Fill missing columns with 0
    for col, _, _ in components:
        if col not in df.columns:
            df[col] = 0.0

    x = np.arange(len(df))
    bar_w = 0.52

    # ---------------------------------------------------------------------------
    # Figure
    # ---------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))

    bottoms = np.zeros(len(df))
    patches = []
    for col, label, color in components:
        vals = df[col].fillna(0).values
        bars = ax.bar(
            x, vals,
            bottom=bottoms,
            width=bar_w,
            color=color,
            edgecolor="white",
            linewidth=0.6,
            zorder=3,
        )
        patches.append(mpatches.Patch(facecolor=color, edgecolor="white",
                                       linewidth=0.6, label=label))
        bottoms += vals

    # Total EUI labels on top of each bar
    for i, (_, row) in enumerate(df.iterrows()):
        total = row.get("total_eui_kwh_m2", bottoms[i])
        ax.text(
            x[i], bottoms[i] + 2.5,
            f"{total:.0f}",
            ha="center", va="bottom",
            fontsize=FONT_S, fontweight="bold", color="#333333",
        )

    # ---------------------------------------------------------------------------
    # Axes formatting (publication style)
    # ---------------------------------------------------------------------------
    ax.set_xticks(x)
    ax.set_xticklabels(
        [ERA_LABELS.get(r["era"], r.get("label", f"Era {r['era']}"))
         for _, r in df.iterrows()],
        fontsize=FONT_L,
    )
    ax.set_ylabel(r"Annual Energy Use Intensity (kWh m$^{-2}$ yr$^{-1}$)",
                  fontsize=FONT_L)
    ax.set_xlabel("Building Archetype", fontsize=FONT_L)
    ax.set_title(
        "Baseline Energy Use Intensity — Changsha Residential Buildings\n"
        r"(TMYx 2007–2021, Changsha WMO 576870)",
        fontsize=FONT_T,
        pad=8,
    )

    # y-axis: minor ticks every 20 kWh/m², major every 50
    y_max = max(bottoms) * 1.18
    ax.set_ylim(0, y_max)
    ax.yaxis.set_major_locator(MultipleLocator(50))
    ax.yaxis.set_minor_locator(MultipleLocator(25))

    # Spine cleanup — keep left and bottom only
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)

    # Light horizontal grid on major ticks only
    ax.yaxis.grid(True, which="major", linestyle="--",
                  linewidth=0.5, color="#cccccc", zorder=0)
    ax.set_axisbelow(True)

    ax.tick_params(axis="both", which="both", labelsize=FONT_S)
    ax.tick_params(axis="y",   which="minor", length=2)

    # Legend — inside upper right to avoid wasted whitespace
    leg = ax.legend(
        handles=patches[::-1],   # reverse so heating is at bottom
        loc="upper right",
        fontsize=FONT_S - 0.5,
        frameon=True,
        framealpha=0.9,
        edgecolor="#cccccc",
        ncol=1,
    )
    leg.get_frame().set_linewidth(0.5)

    # Annotation: Chinese standard reference
    ax.text(
        0.01, 0.02,
        "Ref: JGJ 134-2010 (HSCW zone) | DOE/PNNL prototype geometry",
        transform=ax.transAxes,
        fontsize=6.5,
        color="#888888",
        va="bottom",
    )

    # ---------------------------------------------------------------------------
    # Save
    # ---------------------------------------------------------------------------
    plt.tight_layout(pad=1.2)
    plt.savefig(out_path, dpi=DPI, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()
    print(f"Saved: {out_path}")


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

def main():
    if not os.path.isfile(BASELINE_CSV):
        print(f"ERROR: {BASELINE_CSV} not found. Run run_baseline.py first.",
              file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(BASELINE_CSV)
    plot_baseline_eui(df, OUT_FIG)


if __name__ == "__main__":
    main()
