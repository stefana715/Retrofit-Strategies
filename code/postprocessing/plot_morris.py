"""
plot_morris.py
==============
Publication-quality Morris SA figures for the three Changsha building eras.

Produces:
  figure/fig05_morris_sa.png — 3-panel μ* vs σ scatter (one panel per era)

Usage (standalone):
    python plot_morris.py

Or called programmatically:
    from plot_morris import plot_morris_all_eras
    plot_morris_all_eras()

Reads:
    data/processed/morris_results_era{1,2,3}.csv

Style:
    Energy & Buildings / Elsevier single-column subfigure layout
    300 dpi, colour-blind-friendly palette
"""

import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
DATA_PROC  = os.path.join(REPO_ROOT, "data", "processed")
FIGURE_DIR = os.path.join(REPO_ROOT, "figure")

OUT_FIG = os.path.join(FIGURE_DIR, "fig05_morris_sa.png")

# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------
FIG_W   = 7.2    # inches (double-column width)
FIG_H   = 5.5
DPI     = 300
FONT_S  = 8.5
FONT_L  = 9.5
FONT_T  = 10.0

ERA_TITLES = {
    1: "Era 1 (~1980s)\nPre-code, no insulation",
    2: "Era 2 (~2000s)\nPartial insulation",
    3: "Era 3 (~2010s+)\nJGJ 134-2010 code-compliant",
}

# Labels
PARAM_LABELS = {
    "wall_U":           r"Wall $U$",
    "roof_U":           r"Roof $U$",
    "window_U":         r"Window $U$",
    "WWR":              "WWR",
    "infiltration":     "Infiltration",
    "cooling_setpoint": "Cooling SP",
    "heating_setpoint": "Heating SP",
    "lighting_power":   "Lighting",
    "equipment_power":  "Equipment",
    "occupant_density": "Occupancy",
}

# Colour by parameter group (Wong 2011, colour-blind friendly)
GROUP_COLORS = {
    "wall_U":           "#0072B2",   # blue — opaque envelope
    "roof_U":           "#0072B2",
    "window_U":         "#56B4E9",   # sky blue — transparent envelope
    "WWR":              "#56B4E9",
    "infiltration":     "#009E73",   # green — air tightness
    "cooling_setpoint": "#D55E00",   # vermillion — HVAC setpoints
    "heating_setpoint": "#CC79A7",   # mauve
    "lighting_power":   "#E69F00",   # orange — internal gains
    "equipment_power":  "#F0E442",   # yellow
    "occupant_density": "#999999",   # grey — occupancy
}

# Legend group definitions
LEGEND_GROUPS = [
    ("Opaque envelope",      "#0072B2"),
    ("Transparent envelope", "#56B4E9"),
    ("Air tightness",        "#009E73"),
    ("Cooling setpoint",     "#D55E00"),
    ("Heating setpoint",     "#CC79A7"),
    ("Internal gains",       "#E69F00"),
    ("Occupancy",            "#999999"),
]


# ---------------------------------------------------------------------------
# Core plot function
# ---------------------------------------------------------------------------

def _plot_single_era(ax, df, era_num, show_ylabel=True, show_legend=False):
    """
    Draw μ* vs σ scatter for one era.

    Args:
        ax:          matplotlib Axes object
        df:          DataFrame with columns parameter, mu_star, mu_star_conf, sigma
        era_num:     1, 2, or 3
        show_ylabel: draw y-axis label on left panel only
        show_legend: draw group colour legend
    """
    names    = df["parameter"].values
    mu_star  = df["mu_star"].values.astype(float)
    sigma    = df["sigma"].values.astype(float)
    conf     = df["mu_star_conf"].values.astype(float)

    # --- Reference line σ = μ* ---
    lim = max(np.nanmax(mu_star) * 1.30, np.nanmax(sigma) * 1.30, 0.5)
    ax.plot([0, lim], [0, lim], color="#bbbbbb", linestyle="--",
            linewidth=0.8, zorder=1)

    # --- Reference line σ = 0.1 × μ* (near-linear threshold) ---
    ax.plot([0, lim], [0, 0.1 * lim], color="#dddddd", linestyle=":",
            linewidth=0.6, zorder=1)

    # --- Data points with error bars ---
    for i, name in enumerate(names):
        color = GROUP_COLORS.get(name, "#888888")
        ax.errorbar(
            mu_star[i], sigma[i],
            xerr=conf[i],
            fmt="o",
            color=color,
            markersize=7,
            capsize=3,
            linewidth=1.0,
            elinewidth=0.8,
            zorder=3,
        )

        # --- Parameter labels (adaptive placement to reduce overlap) ---
        label = PARAM_LABELS.get(name, name)
        # Offset logic: alternate above/below for close points
        dx, dy = 4, 4
        rank_col = "rank" if "rank" in df.columns else None
        if rank_col:
            rank_val = df.loc[df["parameter"] == name, "rank"].values
            if len(rank_val) and int(rank_val[0]) % 2 == 0:
                dy = -10
        ax.annotate(
            label,
            xy=(mu_star[i], sigma[i]),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=FONT_S - 1.0,
            color=color,
            fontweight="bold",
            zorder=4,
        )

    # --- Quadrant annotations ---
    ax.text(0.97, 0.97, "Important\n(nonlinear/interactions)",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=FONT_S - 1.5, color="#aaaaaa", style="italic")
    ax.text(0.97, 0.03, "Important\n(linear/additive)",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=FONT_S - 1.5, color="#aaaaaa", style="italic")
    ax.text(0.03, 0.03, "Negligible",
            transform=ax.transAxes, ha="left", va="bottom",
            fontsize=FONT_S - 1.5, color="#aaaaaa", style="italic")

    # --- Axes ---
    ax.set_xlim(left=0, right=lim)
    ax.set_ylim(bottom=0, top=lim)
    ax.set_aspect("equal", adjustable="box")

    ax.set_xlabel(r"$\mu^*$ (modified mean elementary effect)", fontsize=FONT_L)
    if show_ylabel:
        ax.set_ylabel(r"$\sigma$ (std. dev. of elementary effects)", fontsize=FONT_L)

    ax.set_title(ERA_TITLES.get(era_num, f"Era {era_num}"),
                 fontsize=FONT_T, pad=6)

    ax.tick_params(axis="both", which="both", labelsize=FONT_S)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.7)
    ax.spines["bottom"].set_linewidth(0.7)
    ax.grid(True, linestyle=":", linewidth=0.4, color="#cccccc", zorder=0)
    ax.set_axisbelow(True)

    if show_legend:
        patches = [
            mpatches.Patch(facecolor=c, edgecolor="white", linewidth=0.5,
                           label=grp)
            for grp, c in LEGEND_GROUPS
        ]
        ax.legend(
            handles=patches,
            loc="upper left",
            fontsize=FONT_S - 1.0,
            frameon=True,
            framealpha=0.9,
            edgecolor="#cccccc",
            ncol=1,
            handlelength=1.0,
            handleheight=0.8,
        ).get_frame().set_linewidth(0.5)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def plot_morris_all_eras(out_path=OUT_FIG, data_dir=DATA_PROC):
    """
    Load morris_results_era{1,2,3}.csv and produce fig05.

    Missing era CSVs are silently skipped (figure still saved for available eras).
    """
    os.makedirs(FIGURE_DIR, exist_ok=True)

    era_dfs = {}
    for era_num in [1, 2, 3]:
        csv = os.path.join(data_dir, f"morris_results_era{era_num}.csv")
        if os.path.isfile(csv):
            era_dfs[era_num] = pd.read_csv(csv)
        else:
            print(f"WARNING: {csv} not found — era {era_num} skipped.",
                  file=sys.stderr)

    if not era_dfs:
        print("ERROR: No morris_results_era*.csv found.  "
              "Run morris_sa.py or morris_sa_demo.py first.",
              file=sys.stderr)
        return

    n_eras = len(era_dfs)
    fig, axes = plt.subplots(1, n_eras, figsize=(FIG_W, FIG_H),
                             constrained_layout=True)
    if n_eras == 1:
        axes = [axes]

    for ax_idx, (era_num, df) in enumerate(sorted(era_dfs.items())):
        show_ylabel  = (ax_idx == 0)
        show_legend  = (ax_idx == 0)
        _plot_single_era(axes[ax_idx], df, era_num,
                         show_ylabel=show_ylabel, show_legend=show_legend)

    # Super-title
    fig.suptitle(
        "Morris Sensitivity Analysis — Changsha Residential Buildings\n"
        r"(10 parameters, TMYx 2007–2021, EUI kWh m$^{-2}$ yr$^{-1}$)",
        fontsize=FONT_T + 0.5,
        y=1.01,
    )

    # Bottom annotation
    fig.text(
        0.5, -0.02,
        "Ref: JGJ 134-2010 (HSCW zone) | DOE/PNNL prototype geometry | "
        r"Morris (1991) $\mu^*$ index via SALib",
        ha="center", fontsize=6.0, color="#888888",
    )

    plt.savefig(out_path, dpi=DPI, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()
    print(f"Saved: {out_path}")


# ---------------------------------------------------------------------------
# Standalone μ* bar chart (supplementary figure helper)
# ---------------------------------------------------------------------------

def plot_mu_star_bars_all_eras(out_path=None, data_dir=DATA_PROC):
    """
    Horizontal bar chart of μ* rankings, one column per era.
    Optional supplementary figure; saves alongside fig05.
    """
    if out_path is None:
        out_path = os.path.join(FIGURE_DIR, "fig05b_morris_bar.png")

    era_dfs = {}
    for era_num in [1, 2, 3]:
        csv = os.path.join(data_dir, f"morris_results_era{era_num}.csv")
        if os.path.isfile(csv):
            era_dfs[era_num] = pd.read_csv(csv)

    if not era_dfs:
        return

    n_eras = len(era_dfs)
    fig, axes = plt.subplots(1, n_eras, figsize=(FIG_W, 4.5),
                             constrained_layout=True)
    if n_eras == 1:
        axes = [axes]

    for ax_idx, (era_num, df) in enumerate(sorted(era_dfs.items())):
        ax = axes[ax_idx]
        df_sorted = df.sort_values("mu_star", ascending=True)
        labels  = [PARAM_LABELS.get(n, n) for n in df_sorted["parameter"]]
        colors  = [GROUP_COLORS.get(n, "#888888") for n in df_sorted["parameter"]]
        mu      = df_sorted["mu_star"].values.astype(float)
        conf    = df_sorted["mu_star_conf"].values.astype(float)

        ax.barh(labels, mu, xerr=conf, color=colors,
                edgecolor="white", linewidth=0.4,
                error_kw={"elinewidth": 1.0, "capsize": 2.5})

        ax.set_title(ERA_TITLES.get(era_num, f"Era {era_num}"),
                     fontsize=FONT_T, pad=4)
        ax.set_xlabel(r"$\mu^*$", fontsize=FONT_L)
        ax.tick_params(labelsize=FONT_S)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="x", linestyle=":", linewidth=0.4, color="#cccccc")
        ax.set_axisbelow(True)
        ax.set_xlim(left=0)

        if ax_idx > 0:
            ax.set_yticklabels([])

    fig.suptitle(
        r"Morris $\mu^*$ Rankings — Changsha Residential Buildings",
        fontsize=FONT_T + 0.5,
    )

    plt.savefig(out_path, dpi=DPI, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close()
    print(f"Saved: {out_path}")


# ---------------------------------------------------------------------------
# Standalone entry point
# ---------------------------------------------------------------------------

def main():
    # Check at least one results file exists
    any_found = any(
        os.path.isfile(os.path.join(DATA_PROC, f"morris_results_era{e}.csv"))
        for e in [1, 2, 3]
    )
    if not any_found:
        print(
            "ERROR: No morris_results_era*.csv files found.\n"
            "Run morris_sa_demo.py (fast) or morris_sa.py (full EP) first.",
            file=sys.stderr,
        )
        sys.exit(1)

    plot_morris_all_eras()
    plot_mu_star_bars_all_eras()


if __name__ == "__main__":
    main()
