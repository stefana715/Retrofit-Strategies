"""
plot_retrofit.py
================
Publication-quality figure of energy savings achieved by five retrofit
measures across three Changsha residential building archetypes.

Produces:
    figure/fig07_retrofit_savings.png   — grouped bar chart, 300 dpi

Reads:
    data/processed/retrofit_results.csv

Usage (standalone):
    python plot_retrofit.py

Or called programmatically:
    from plot_retrofit import plot_retrofit_savings
    plot_retrofit_savings()
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
REPO_ROOT  = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PROC  = os.path.join(REPO_ROOT, "data", "processed")
FIGURE_DIR = os.path.join(REPO_ROOT, "figure")

RETROFIT_CSV = os.path.join(DATA_PROC, "retrofit_results.csv")
OUT_FIG      = os.path.join(FIGURE_DIR, "fig07_retrofit_savings.png")

# ---------------------------------------------------------------------------
# Style constants (Energy & Buildings / Elsevier)
# ---------------------------------------------------------------------------
FIG_W  = 7.2    # inches — double-column width
FIG_H  = 5.0
DPI    = 300
FONT_S = 8.5
FONT_L = 9.5
FONT_T = 10.5

# Era colours (Wong 2011, colour-blind safe)
ERA_COLORS = {
    "Era 1 (~1980s)":  "#D55E00",   # vermillion
    "Era 2 (~2000s)":  "#0072B2",   # blue
    "Era 3 (~2010s+)": "#009E73",   # green
}
ERA_HATCHES = {
    "Era 1 (~1980s)":  "",
    "Era 2 (~2000s)":  "///",
    "Era 3 (~2010s+)": "...",
}

# Retrofit display order and short labels (matching RETROFIT_MEASURES in retrofit_scenarios.py)
RETROFIT_ORDER = ["R1_Wall", "R2_Window", "R3_Roof", "R4_Infiltration", "R5_Combined"]
RETROFIT_LABELS = {
    "R1_Wall":         "R1\nWall",
    "R2_Window":       "R2\nWindow",
    "R3_Roof":         "R3\nRoof",
    "R4_Infiltration": "R4\nAir sealing",
    "R5_Combined":     "R5\nCombined",
}


def plot_retrofit_savings(csv_path=RETROFIT_CSV, out_path=OUT_FIG):
    """
    Create grouped bar chart of total EUI savings % per retrofit × era.

    Layout:
        x-axis: retrofit measures (R1–R5)
        groups: 3 bars per measure, one per era
        y-axis: total EUI savings % vs baseline
    """
    os.makedirs(FIGURE_DIR, exist_ok=True)

    if not os.path.isfile(csv_path):
        print(f"ERROR: {csv_path} not found.  Run retrofit_scenarios.py first.",
              file=sys.stderr)
        return

    df = pd.read_csv(csv_path)
    df_ret = df[df["retrofit"] != "Baseline"].copy()

    # Filter to retrofit order
    df_ret = df_ret[df_ret["retrofit"].isin(RETROFIT_ORDER)]
    df_ret["retrofit_order"] = df_ret["retrofit"].map(
        {k: i for i, k in enumerate(RETROFIT_ORDER)}
    )
    df_ret = df_ret.sort_values("retrofit_order")

    era_labels = sorted(df_ret["era_label"].unique(),
                        key=lambda x: int(x.split("~")[1][:4]))

    n_retrofits = len(RETROFIT_ORDER)
    n_eras      = len(era_labels)
    x           = np.arange(n_retrofits)
    total_w     = 0.72        # total bar group width
    bar_w       = total_w / n_eras
    offsets     = np.linspace(-(total_w - bar_w) / 2,
                               (total_w - bar_w) / 2, n_eras)

    # ---------------------------------------------------------------------------
    fig, axes = plt.subplots(
        2, 1, figsize=(FIG_W, FIG_H),
        gridspec_kw={"height_ratios": [2.5, 1]},
        constrained_layout=True,
    )
    ax_main, ax_sub = axes

    # =========================================================================
    # Top panel: Total EUI savings %
    # =========================================================================
    for j, era_label in enumerate(era_labels):
        era_data = df_ret[df_ret["era_label"] == era_label]
        values   = []
        for r_key in RETROFIT_ORDER:
            row = era_data[era_data["retrofit"] == r_key]
            values.append(float(row["savings_percent"].values[0]) if len(row) else 0.0)

        color   = ERA_COLORS.get(era_label, "#888888")
        hatch   = ERA_HATCHES.get(era_label, "")
        x_pos   = x + offsets[j]

        bars = ax_main.bar(
            x_pos, values,
            width=bar_w * 0.92,
            color=color,
            hatch=hatch,
            edgecolor="white",
            linewidth=0.6,
            alpha=0.90,
            zorder=3,
            label=era_label,
        )

        # Value labels on bars ≥ 2 %
        for bar, val in zip(bars, values):
            if val >= 2.0:
                ax_main.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.4,
                    f"{val:.1f}",
                    ha="center", va="bottom",
                    fontsize=FONT_S - 1.5, color="#333333",
                )

    ax_main.set_xlim(-0.5, n_retrofits - 0.5)
    ax_main.set_xticks(x)
    ax_main.set_xticklabels(
        [RETROFIT_LABELS.get(r, r) for r in RETROFIT_ORDER],
        fontsize=FONT_L,
    )
    ax_main.set_ylabel("Total EUI savings vs baseline (%)", fontsize=FONT_L)
    ax_main.set_title(
        "Retrofit Strategy Energy Savings — Changsha Residential Buildings\n"
        r"(TMYx 2007–2021, EnergyPlus 26.1)",
        fontsize=FONT_T, pad=6,
    )

    y_max = ax_main.get_ylim()[1]
    ax_main.set_ylim(0, max(y_max * 1.12, 10))
    ax_main.yaxis.set_major_locator(MultipleLocator(10))
    ax_main.yaxis.set_minor_locator(MultipleLocator(5))

    ax_main.spines["top"].set_visible(False)
    ax_main.spines["right"].set_visible(False)
    ax_main.spines["left"].set_linewidth(0.7)
    ax_main.spines["bottom"].set_linewidth(0.7)
    ax_main.yaxis.grid(True, which="major", linestyle="--",
                       linewidth=0.4, color="#cccccc", zorder=0)
    ax_main.set_axisbelow(True)
    ax_main.tick_params(axis="both", which="both", labelsize=FONT_S)

    # Legend
    patches = [
        mpatches.Patch(
            facecolor=ERA_COLORS.get(el, "#888888"),
            hatch=ERA_HATCHES.get(el, ""),
            edgecolor="white", linewidth=0.5, label=el,
        )
        for el in era_labels
    ]
    leg = ax_main.legend(
        handles=patches,
        loc="upper left",
        fontsize=FONT_S,
        frameon=True, framealpha=0.9,
        edgecolor="#cccccc",
        ncol=1,
    )
    leg.get_frame().set_linewidth(0.5)

    # =========================================================================
    # Bottom panel: heating vs cooling savings breakdown for Combined (R5)
    # =========================================================================
    r5_data = df_ret[df_ret["retrofit"] == "R5_Combined"]
    heat_saves = []
    cool_saves = []
    era_labels_r5 = []
    for el in era_labels:
        row = r5_data[r5_data["era_label"] == el]
        if len(row):
            heat_saves.append(float(row["heat_savings_pct"].values[0]))
            cool_saves.append(float(row["cool_savings_pct"].values[0]))
            era_labels_r5.append(el)

    x_r5  = np.arange(len(era_labels_r5))
    bw    = 0.32
    bars_h = ax_sub.bar(x_r5 - bw/2, heat_saves, width=bw,
                        color="#E69F00", edgecolor="white", linewidth=0.5,
                        label="Heating savings", zorder=3)
    bars_c = ax_sub.bar(x_r5 + bw/2, cool_saves, width=bw,
                        color="#56B4E9", edgecolor="white", linewidth=0.5,
                        label="Cooling savings", zorder=3)

    for bar, val in zip(list(bars_h) + list(bars_c),
                        heat_saves + cool_saves):
        if abs(val) >= 3.0:
            ax_sub.text(
                bar.get_x() + bar.get_width() / 2,
                (bar.get_height() + 1.5 if val >= 0
                 else bar.get_height() - 3.5),
                f"{val:.0f}%",
                ha="center", va="bottom",
                fontsize=FONT_S - 1.5, color="#333333",
            )

    ax_sub.set_xticks(x_r5)
    ax_sub.set_xticklabels(
        [el.replace(" (~", "\n(~") for el in era_labels_r5],
        fontsize=FONT_S,
    )
    ax_sub.set_ylabel("Combined retrofit\nsavings (%)", fontsize=FONT_S)
    ax_sub.set_title("R5 Combined: heating vs cooling breakdown",
                     fontsize=FONT_S + 0.5, pad=3)

    ax_sub.spines["top"].set_visible(False)
    ax_sub.spines["right"].set_visible(False)
    ax_sub.spines["left"].set_linewidth(0.7)
    ax_sub.spines["bottom"].set_linewidth(0.7)
    ax_sub.yaxis.grid(True, which="major", linestyle="--",
                      linewidth=0.4, color="#cccccc", zorder=0)
    ax_sub.set_axisbelow(True)
    ax_sub.tick_params(labelsize=FONT_S)
    ax_sub.set_xlim(-0.5, len(era_labels_r5) - 0.5)

    sub_leg = ax_sub.legend(
        fontsize=FONT_S - 0.5, frameon=True, framealpha=0.9,
        edgecolor="#cccccc", loc="upper right",
    )
    sub_leg.get_frame().set_linewidth(0.5)

    # Bottom annotation
    fig.text(
        0.5, -0.02,
        "Ref: JGJ 134-2010 (HSCW zone) | DOE/PNNL prototype geometry | "
        "R1: wall EPS (U=0.4), R2: low-e window (U=1.8), "
        "R3: roof XPS (U=0.3), R4: air sealing (0.3 ACH)",
        ha="center", fontsize=6.0, color="#888888",
    )

    plt.savefig(out_path, dpi=DPI, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()
    print(f"Saved: {out_path}")


def main():
    if not os.path.isfile(RETROFIT_CSV):
        print(
            f"ERROR: {RETROFIT_CSV} not found.\n"
            "Run retrofit_scenarios.py first.",
            file=sys.stderr,
        )
        sys.exit(1)
    plot_retrofit_savings()


if __name__ == "__main__":
    main()
