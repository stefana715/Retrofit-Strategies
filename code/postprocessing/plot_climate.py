"""
plot_climate.py
===============
Publication-quality figure of climate change impact on building energy
performance for Changsha residential archetypes.

Produces:
    figure/fig09_climate_impact.png  — two-panel figure, 300 dpi

Panel 1 (top):
    Grouped bar chart — total EUI (kWh/m²/yr) across 5 climate scenarios
    for each archetype × {Baseline, R5_Combined}.
    Stacked bars show heating / cooling breakdown.
    Highlights the shift from heating-dominated to cooling-dominated demand
    under progressive warming.

Panel 2 (bottom):
    Heat-cool ratio (heating EUI / cooling EUI) for each archetype × retrofit
    across climate scenarios, showing the convergence toward cooling dominance.

Reads:
    data/processed/climate_results.csv

Usage (standalone):
    python plot_climate.py

Or called programmatically:
    from plot_climate import plot_climate_all
    plot_climate_all()
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
REPO_ROOT   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PROC   = os.path.join(REPO_ROOT, "data", "processed")
FIGURE_DIR  = os.path.join(REPO_ROOT, "figure")

CLIMATE_CSV = os.path.join(DATA_PROC, "climate_results.csv")
OUT_FIG     = os.path.join(FIGURE_DIR, "fig09_climate_impact.png")

# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------
FIG_W  = 7.2
FIG_H  = 11.0
DPI    = 300
FONT_S = 8.0
FONT_L = 9.0
FONT_T = 10.0

# Scenario colours — sequential blue-to-red for warming severity
SCENARIO_COLORS = {
    "Current":    "#333333",   # dark grey — present
    "2050_SSP245":"#56B4E9",   # sky blue — low-medium warming
    "2050_SSP585":"#0072B2",   # blue — medium-high warming
    "2080_SSP245":"#E69F00",   # amber — late century moderate
    "2080_SSP585":"#D55E00",   # vermillion — worst case
}

# Stacked bar components
HEAT_COLOR = "#4393C3"   # blue for heating
COOL_COLOR = "#D6604D"   # red/orange for cooling
OTHER_COLOR = "#888888"  # grey for other loads

ERA_LABELS = ["Era 1 (~1980s)", "Era 2 (~2000s)", "Era 3 (~2010s+)"]
RETROFIT_ORDER = ["Baseline", "R5_Combined"]
CLIMATE_ORDER  = ["Current", "2050_SSP245", "2050_SSP585", "2080_SSP245", "2080_SSP585"]

SCENARIO_XLABELS = {
    "Current":    "Current",
    "2050_SSP245":"2050\nSSP2-4.5",
    "2050_SSP585":"2050\nSSP5-8.5",
    "2080_SSP245":"2080\nSSP2-4.5",
    "2080_SSP585":"2080\nSSP5-8.5",
}


# ---------------------------------------------------------------------------
# Top panel helper — stacked bars per (era, retrofit) pair
# ---------------------------------------------------------------------------

def _plot_eui_stacked(ax, df, era_label, show_legend=False):
    """
    Stacked bar chart of heating / cooling / other EUI for one era.
    X-axis: 5 climate scenarios × 2 retrofits = 10 bar groups.
    """
    df_era = df[df["era_label"] == era_label]

    bar_w   = 0.36
    n_ret   = len(RETROFIT_ORDER)
    offsets = [-bar_w / 2, bar_w / 2]

    x_labels  = []
    x_ticks   = []

    max_eui = 0.0

    for c_idx, clim_key in enumerate(CLIMATE_ORDER):
        df_c = df_era[df_era["climate"] == clim_key]
        for r_idx, ret_key in enumerate(RETROFIT_ORDER):
            df_r = df_c[df_c["retrofit"] == ret_key]
            if df_r.empty:
                continue

            row      = df_r.iloc[0]
            heat     = float(row["heating_kwh_m2"])
            cool     = float(row["cooling_kwh_m2"])
            total    = float(row["total_eui_kwh_m2"])
            other    = max(0.0, total - heat - cool)

            x_pos = c_idx * (n_ret + 0.6) + offsets[r_idx]
            x_ticks.append(x_pos)
            short_ret = "BL" if ret_key == "Baseline" else "R5"
            x_labels.append(short_ret)

            alpha = 0.92
            ax.bar(x_pos, heat,  width=bar_w * 0.90,
                   color=HEAT_COLOR,  alpha=alpha, zorder=3, bottom=0)
            ax.bar(x_pos, cool,  width=bar_w * 0.90,
                   color=COOL_COLOR,  alpha=alpha, zorder=3, bottom=heat)
            ax.bar(x_pos, other, width=bar_w * 0.90,
                   color=OTHER_COLOR, alpha=alpha, zorder=3, bottom=heat + cool)

            max_eui = max(max_eui, total)

            # Total label on bar
            if total > 5:
                ax.text(x_pos, total + 2, f"{total:.0f}",
                        ha="center", va="bottom",
                        fontsize=FONT_S - 2.0, color="#222222", rotation=90)

    y_bottom = -max_eui * 0.18   # reserve space below axis for scenario labels

    # Scenario group labels — placed in data coordinates below the bars
    for c_idx, clim_key in enumerate(CLIMATE_ORDER):
        centre   = c_idx * (n_ret + 0.6)
        scen_lbl = SCENARIO_XLABELS[clim_key]
        color    = SCENARIO_COLORS[clim_key]
        ax.text(centre, y_bottom * 0.5, scen_lbl,
                ha="center", va="center",
                fontsize=FONT_S - 0.5, color=color, fontweight="bold",
                clip_on=False)

    # Separator lines between scenario groups
    for c_idx in range(1, len(CLIMATE_ORDER)):
        sep_x = c_idx * (n_ret + 0.6) - (n_ret + 0.6) / 2 - 0.15
        ax.axvline(sep_x, color="#cccccc", linewidth=0.7,
                   linestyle="--", zorder=1)

    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels, fontsize=FONT_S - 0.5)
    ax.set_xlim(
        -1.0,
        (len(CLIMATE_ORDER) - 1) * (n_ret + 0.6) + 1.0
    )
    ax.set_ylim(y_bottom, max_eui * 1.22)
    ax.spines["bottom"].set_position(("data", 0))  # keep x-axis at 0
    ax.set_ylabel("EUI (kWh m⁻² yr⁻¹)", fontsize=FONT_L)
    ax.set_title(era_label, fontsize=FONT_L, pad=4, fontweight="bold")

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

    if show_legend:
        patches = [
            mpatches.Patch(facecolor=HEAT_COLOR,  alpha=0.92,
                           edgecolor="none", label="Heating"),
            mpatches.Patch(facecolor=COOL_COLOR,  alpha=0.92,
                           edgecolor="none", label="Cooling"),
            mpatches.Patch(facecolor=OTHER_COLOR, alpha=0.92,
                           edgecolor="none", label="Lighting + equipment"),
        ]
        leg = ax.legend(handles=patches, loc="upper right",
                        fontsize=FONT_S - 0.5,
                        frameon=True, framealpha=0.9,
                        edgecolor="#cccccc", ncol=1)
        leg.get_frame().set_linewidth(0.5)


# ---------------------------------------------------------------------------
# Bottom panel — heating/cooling ratio trend
# ---------------------------------------------------------------------------

def _plot_hc_ratio(ax, df):
    """
    Line chart of heating-to-cooling ratio across climate scenarios.
    One line per (era × retrofit) combination.
    """
    era_colors = {
        "Era 1 (~1980s)":  "#D55E00",
        "Era 2 (~2000s)":  "#0072B2",
        "Era 3 (~2010s+)": "#009E73",
    }
    linestyles = {
        "Baseline":    "-",
        "R5_Combined": "--",
    }
    markers = {
        "Baseline":    "o",
        "R5_Combined": "s",
    }

    x = np.arange(len(CLIMATE_ORDER))

    for era_lbl in ERA_LABELS:
        for ret_key in RETROFIT_ORDER:
            sub = df[(df["era_label"] == era_lbl) & (df["retrofit"] == ret_key)]
            if sub.empty:
                continue
            ratios = []
            for clim_key in CLIMATE_ORDER:
                row = sub[sub["climate"] == clim_key]
                if row.empty:
                    ratios.append(np.nan)
                    continue
                heat = float(row["heating_kwh_m2"].values[0])
                cool = float(row["cooling_kwh_m2"].values[0])
                ratio = heat / cool if cool > 0.1 else np.nan
                ratios.append(ratio)

            short_era = era_lbl.split("~")[1][:5]
            lbl = f"{short_era} — {ret_key.replace('_Combined','')}"
            ax.plot(x, ratios,
                    color=era_colors.get(era_lbl, "#888888"),
                    linestyle=linestyles[ret_key],
                    marker=markers[ret_key],
                    markersize=4,
                    linewidth=1.3,
                    zorder=3,
                    label=lbl)

    ax.axhline(1.0, color="#bbbbbb", linewidth=0.8, linestyle=":",
               zorder=1, label="Heating = Cooling (ratio = 1)")
    ax.text(len(CLIMATE_ORDER) - 0.05, 1.03, "cooling\ndominates →",
            ha="right", va="bottom",
            fontsize=FONT_S - 1.5, color="#888888", style="italic")
    ax.text(len(CLIMATE_ORDER) - 0.05, 0.97, "← heating\ndominates",
            ha="right", va="top",
            fontsize=FONT_S - 1.5, color="#888888", style="italic")

    ax.set_xticks(x)
    ax.set_xticklabels(
        [SCENARIO_XLABELS[k] for k in CLIMATE_ORDER],
        fontsize=FONT_S,
    )
    ax.set_ylabel("Heating-to-cooling\nEUI ratio", fontsize=FONT_L)
    ax.set_title(
        "Heating-to-Cooling Ratio across Climate Scenarios\n"
        "(ratio < 1 → cooling-dominant regime)",
        fontsize=FONT_T - 0.5, pad=4,
    )
    ax.set_xlim(-0.3, len(CLIMATE_ORDER) - 0.7)
    ax.set_ylim(bottom=0)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.7)
    ax.spines["bottom"].set_linewidth(0.7)
    ax.yaxis.grid(True, which="major", linestyle="--",
                  linewidth=0.4, color="#cccccc", zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=FONT_S)

    leg = ax.legend(fontsize=FONT_S - 1.0, frameon=True, framealpha=0.9,
                    edgecolor="#cccccc", loc="upper right",
                    ncol=2)
    leg.get_frame().set_linewidth(0.5)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def plot_climate_all(csv_path=CLIMATE_CSV, out_path=OUT_FIG):
    """
    Produce fig09_climate_impact.png.
    """
    os.makedirs(FIGURE_DIR, exist_ok=True)

    if not os.path.isfile(csv_path):
        print(f"ERROR: {csv_path} not found.  Run climate_scenarios.py first.",
              file=sys.stderr)
        return

    df = pd.read_csv(csv_path)
    available_eras = [e for e in ERA_LABELS if e in df["era_label"].values]
    n_eras = len(available_eras)

    if n_eras == 0:
        print("ERROR: No valid era data found in climate_results.csv.",
              file=sys.stderr)
        return

    fig = plt.figure(figsize=(FIG_W, FIG_H))
    gs  = fig.add_gridspec(n_eras + 1, 1,
                           height_ratios=[1.0] * n_eras + [0.75],
                           hspace=0.55)
    ax_top  = [fig.add_subplot(gs[i, 0]) for i in range(n_eras)]
    ax_bot  = fig.add_subplot(gs[n_eras, 0])

    for i, era_lbl in enumerate(available_eras):
        _plot_eui_stacked(ax_top[i], df, era_lbl,
                          show_legend=(i == 0))

    _plot_hc_ratio(ax_bot, df)

    fig.suptitle(
        "Climate Change Impact on Heating/Cooling Energy — Changsha Residential\n"
        r"(CMIP6 morphed EPW, Belcher 2005 method | TMYx 2007-2021 baseline)",
        fontsize=FONT_T + 0.5,
        y=1.01,
    )

    fig.text(
        0.5, -0.01,
        "BL = Baseline (no retrofit)  |  R5 = Combined retrofit "
        "(wall U=0.4, window U=1.8, roof U=0.3, infiltration 0.3 ACH) | "
        "EUI stacked: blue=heating, red=cooling, grey=other",
        ha="center", fontsize=5.8, color="#888888",
    )

    fig.tight_layout(rect=[0, 0.02, 1, 0.98])
    plt.savefig(out_path, dpi=DPI, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()
    print(f"Saved: {out_path}")


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

def main():
    if not os.path.isfile(CLIMATE_CSV):
        print(f"ERROR: {CLIMATE_CSV} not found.\nRun climate_scenarios.py first.",
              file=sys.stderr)
        sys.exit(1)
    plot_climate_all()


if __name__ == "__main__":
    main()
