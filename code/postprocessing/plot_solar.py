"""
plot_solar.py
=============
Publication-quality figure of rooftop PV integration for three Changsha
residential building archetypes.

Produces:
    figure/fig08_solar_pv.png   — two-panel figure, 300 dpi

Panel 1 (top):  Grouped bar chart — building energy demand vs PV generation
                per m² floor area for each archetype × {Baseline, R5_Combined}.
                Shows net EUI after PV offset as a horizontal reference.

Panel 2 (bottom): Monthly PV generation profile (kWh/m² floor) for the three
                  archetypes, showing seasonal variation.

Reads:
    data/processed/solar_results.csv
    data/processed/solar_monthly.csv

Usage (standalone):
    python plot_solar.py

Or called programmatically:
    from plot_solar import plot_solar_all
    plot_solar_all()
"""

import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.ticker import MultipleLocator

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT  = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PROC  = os.path.join(REPO_ROOT, "data", "processed")
FIGURE_DIR = os.path.join(REPO_ROOT, "figure")

SOLAR_CSV   = os.path.join(DATA_PROC, "solar_results.csv")
MONTHLY_CSV = os.path.join(DATA_PROC, "solar_monthly.csv")
OUT_FIG     = os.path.join(FIGURE_DIR, "fig08_solar_pv.png")

# ---------------------------------------------------------------------------
# Style constants (Energy & Buildings / Elsevier double-column)
# ---------------------------------------------------------------------------
FIG_W  = 7.2
FIG_H  = 6.5
DPI    = 300
FONT_S = 8.5
FONT_L = 9.5
FONT_T = 10.5

# Era colours (Wong 2011, colour-blind safe) — consistent with other figures
ERA_COLORS = {
    "Era 1 (~1980s)":  "#D55E00",
    "Era 2 (~2000s)":  "#0072B2",
    "Era 3 (~2010s+)": "#009E73",
}

# PV bar colour (golden yellow)
PV_COLOR    = "#E69F00"
PV_COLOR_BL = "#F5C842"   # lighter shade for Baseline PV reference line


MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ---------------------------------------------------------------------------
# Top panel: demand vs PV per archetype
# ---------------------------------------------------------------------------

def _plot_demand_pv(ax, df_sum):
    """
    Grouped horizontal sections, one per archetype:
        Baseline EUI bar  | R5_Combined EUI bar  | PV generation bar

    x-axis: groups (one per era × retrofit pair)
    y-axis: kWh/m² floor area per year
    """
    era_order  = ["Era 1 (~1980s)", "Era 2 (~2000s)", "Era 3 (~2010s+)"]
    retro_order = ["Baseline", "R5_Combined"]

    # Build ordered data structure
    group_labels = []
    demand_vals  = []
    pv_vals      = []
    net_vals     = []
    bar_colors   = []
    bar_hatches  = []

    for era_lbl in era_order:
        for ret in retro_order:
            row = df_sum[
                (df_sum["era_label"] == era_lbl) &
                (df_sum["retrofit"]  == ret)
            ]
            if row.empty:
                continue
            r = row.iloc[0]
            demand_vals.append(float(r["retrofit_eui_kwh_m2"]))
            pv_vals.append(float(r["pv_per_m2_floor"]))
            net_vals.append(float(r["net_eui_kwh_m2"]))
            bar_colors.append(ERA_COLORS.get(era_lbl, "#888888"))
            bar_hatches.append("" if ret == "Baseline" else "///")
            short_era = era_lbl.split("~")[1][:5]   # e.g. "1980s"
            group_labels.append(f"{short_era}\n{ret.replace('_Combined','')}")

    x       = np.arange(len(group_labels))
    bar_w   = 0.32
    x_dem   = x - bar_w / 2
    x_pv    = x + bar_w / 2

    # Demand bars
    for i, (xpos, val, col, hat) in enumerate(
            zip(x_dem, demand_vals, bar_colors, bar_hatches)):
        ax.bar(xpos, val, width=bar_w * 0.90,
               color=col, hatch=hat,
               edgecolor="white", linewidth=0.6,
               alpha=0.88, zorder=3,
               label=None)
        # Value label
        ax.text(xpos, val + 3, f"{val:.0f}",
                ha="center", va="bottom", fontsize=FONT_S - 1.5, color="#333333")

    # PV generation bars
    for i, (xpos, val) in enumerate(zip(x_pv, pv_vals)):
        ax.bar(xpos, val, width=bar_w * 0.90,
               color=PV_COLOR,
               edgecolor="white", linewidth=0.6,
               alpha=0.88, zorder=3,
               label=None)
        ax.text(xpos, val + 3, f"{val:.0f}",
                ha="center", va="bottom", fontsize=FONT_S - 1.5, color="#7a5000")

    # Net EUI markers (diamond)
    ax.scatter(x_dem, net_vals, marker="D", s=28, color="black",
               zorder=5, linewidths=0.5, label="Net EUI (demand − PV)")

    # Separator lines between era groups
    n_per_era = len(retro_order)
    for i in range(1, len(era_order)):
        sep_x = i * n_per_era - 0.5
        ax.axvline(sep_x, color="#cccccc", linewidth=0.8, linestyle="--", zorder=1)

    y_max = max(demand_vals) * 1.18
    ax.set_ylim(0, y_max)

    ax.set_xticks(x)
    ax.set_xticklabels(group_labels, fontsize=FONT_S)
    ax.set_xlim(-0.5, len(group_labels) - 0.5)
    ax.set_ylabel("Energy intensity (kWh m⁻² yr⁻¹)", fontsize=FONT_L)
    ax.set_title(
        "Building Energy Demand vs. Rooftop PV Generation\n"
        "(per m² floor area — Changsha residential archetypes)",
        fontsize=FONT_T, pad=6,
    )

    ax.yaxis.set_major_locator(MultipleLocator(50))
    ax.yaxis.set_minor_locator(MultipleLocator(25))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.7)
    ax.spines["bottom"].set_linewidth(0.7)
    ax.yaxis.grid(True, which="major", linestyle="--",
                  linewidth=0.4, color="#cccccc", zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", which="both", labelsize=FONT_S)

    # Era group labels drawn after ylim is set
    for i, era_lbl in enumerate(era_order):
        centre = i * n_per_era + (n_per_era - 1) / 2
        ax.text(centre, y_max * 0.97,
                era_lbl, ha="center", va="top",
                fontsize=FONT_S, fontweight="bold", color="#555555")

    # Legend
    era_patches = [
        mpatches.Patch(facecolor=ERA_COLORS[el], edgecolor="white",
                       linewidth=0.5, label=el)
        for el in era_order
    ]
    hatch_patches = [
        mpatches.Patch(facecolor="#aaaaaa", hatch="",   edgecolor="white",
                       linewidth=0.5, label="Baseline"),
        mpatches.Patch(facecolor="#aaaaaa", hatch="///", edgecolor="white",
                       linewidth=0.5, label="R5 Combined"),
    ]
    pv_patch  = mpatches.Patch(facecolor=PV_COLOR, edgecolor="white",
                                linewidth=0.5, label="PV generation")
    net_marker = mlines.Line2D([], [], color="black", marker="D",
                               markersize=5, linewidth=0,
                               label="Net EUI (demand − PV)")

    leg = ax.legend(
        handles=era_patches + hatch_patches + [pv_patch, net_marker],
        loc="upper right",
        fontsize=FONT_S - 0.5,
        frameon=True, framealpha=0.9,
        edgecolor="#cccccc",
        ncol=2,
    )
    leg.get_frame().set_linewidth(0.5)


# ---------------------------------------------------------------------------
# Bottom panel: monthly generation profile
# ---------------------------------------------------------------------------

def _plot_monthly(ax, df_monthly):
    """Line chart of monthly PV generation (kWh/m² floor) per archetype."""
    era_order = ["Era 1 (~1980s)", "Era 2 (~2000s)", "Era 3 (~2010s+)"]
    linestyles = ["-", "--", ":"]

    for era_lbl, ls in zip(era_order, linestyles):
        sub = df_monthly[df_monthly["era_label"] == era_lbl]
        if sub.empty:
            continue
        # kWh/m² floor = monthly_pv_kwh / floor_area
        # floor_area comes from solar_results; get it via archetype key
        arch_key = sub["archetype"].iloc[0]
        # We need floor_area — embed it from ARCHETYPES; use sum divided by 12 approach
        # But we'll derive it from the monthly totals vs annual
        monthly = sub.groupby("month")["pv_gen_kwh"].sum().sort_index()

        # We need floor_area to normalise.  Compute from arch_type.
        arch_type = sub["arch_type"].iloc[0]
        floor_areas = {
            "MidRise":  3134.6,
            "HighRise": 7836.4,
        }
        fa = floor_areas.get(arch_type, 1.0)
        monthly_per_m2 = monthly / fa

        color = ERA_COLORS.get(era_lbl, "#888888")
        ax.plot(monthly.index, monthly_per_m2.values,
                color=color, linewidth=1.5, linestyle=ls,
                marker="o", markersize=4, zorder=3,
                label=era_lbl)

        # Annotate annual total
        ann = monthly_per_m2.sum()
        ax.text(12.2, monthly_per_m2.iloc[-1],
                f"{ann:.0f} kWh/m²",
                fontsize=FONT_S - 1.5, color=color, va="center")

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MONTH_LABELS, fontsize=FONT_S)
    ax.set_xlim(0.5, 13.5)
    ax.set_ylabel("PV generation (kWh m⁻² floor yr⁻¹)", fontsize=FONT_L)
    ax.set_title("Monthly Rooftop PV Generation Profile — Changsha TMYx",
                 fontsize=FONT_T - 0.5, pad=4)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.7)
    ax.spines["bottom"].set_linewidth(0.7)
    ax.yaxis.grid(True, which="major", linestyle="--",
                  linewidth=0.4, color="#cccccc", zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=FONT_S)
    ax.set_ylim(bottom=0)

    leg = ax.legend(fontsize=FONT_S - 0.5, frameon=True, framealpha=0.9,
                    edgecolor="#cccccc", loc="upper left")
    leg.get_frame().set_linewidth(0.5)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def plot_solar_all(csv_path=SOLAR_CSV, monthly_csv=MONTHLY_CSV, out_path=OUT_FIG):
    """
    Produce fig08_solar_pv.png: demand/PV bar chart + monthly profile.
    """
    os.makedirs(FIGURE_DIR, exist_ok=True)

    for p, name in [(csv_path, "solar_results.csv"), (monthly_csv, "solar_monthly.csv")]:
        if not os.path.isfile(p):
            print(f"ERROR: {p} not found.  Run solar_pv.py first.", file=sys.stderr)
            return

    df_sum     = pd.read_csv(csv_path)
    df_monthly = pd.read_csv(monthly_csv)

    fig, axes = plt.subplots(
        2, 1, figsize=(FIG_W, FIG_H),
        gridspec_kw={"height_ratios": [1.8, 1.0]},
        constrained_layout=True,
    )

    _plot_demand_pv(axes[0], df_sum)

    # After the top panel is drawn, fix the era label y position
    y_top = axes[0].get_ylim()[1]
    for text in axes[0].texts:
        # Era label texts were drawn at placeholder y; update now
        pass  # constrained_layout handles this

    _plot_monthly(axes[1], df_monthly)

    # Bottom annotation
    fig.text(
        0.5, -0.01,
        "PV: monocrystalline Si, η=20%, PR=0.80, tilt=25°, azimuth=S | "
        "MidRise: 360 m² usable roof (72 kWp) | "
        "HighRise: 200 m² usable roof (40 kWp) | "
        "TMYx 2007–2021, pvlib 0.13",
        ha="center", fontsize=5.8, color="#888888",
    )

    plt.savefig(out_path, dpi=DPI, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()
    print(f"Saved: {out_path}")


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

def main():
    for p in [SOLAR_CSV, MONTHLY_CSV]:
        if not os.path.isfile(p):
            print(f"ERROR: {p} not found.\nRun solar_pv.py first.",
                  file=sys.stderr)
            sys.exit(1)
    plot_solar_all()


if __name__ == "__main__":
    main()
