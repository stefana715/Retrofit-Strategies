"""
morris_sa.py
============
Morris Method (Elementary Effects) Sensitivity Analysis for Changsha
residential building energy performance.

Identifies which envelope and operational parameters most influence heating
and cooling energy demand, to guide retrofit strategy prioritisation.

Usage:
    python morris_sa.py               # run full SA (requires EnergyPlus)
    python morris_sa.py --demo        # demo with dummy results (no EnergyPlus)

Outputs:
    data/processed/morris_results.csv    — μ*, σ, μ for each parameter
    figure/fig01_morris_scatter.png      — μ* vs σ scatter (ranking plot)

References:
    Morris MD (1991) Technometrics 33(2):161-174
    Saltelli A et al. (2008) Global Sensitivity Analysis: The Primer
    SALib: Herman & Usher (2017) JOSS 2(9):97
"""

import os
import sys
import json
import argparse
import subprocess
import tempfile
import shutil
import logging

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

try:
    from SALib.sample import morris as morris_sample
    from SALib.analyze import morris as morris_analyze
except ImportError:
    sys.exit("SALib not installed. Run: pip install SALib")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
DATA_MODELS = os.path.join(REPO_ROOT, "data", "models")
DATA_PROCESSED = os.path.join(REPO_ROOT, "data", "processed")
FIGURES = os.path.join(REPO_ROOT, "figure")
DATA_CLIMATE = os.path.join(REPO_ROOT, "data", "climate")

EPW_FILE = os.path.join(
    DATA_CLIMATE,
    "CHN_HN_Changsha.576870_TMYx.2007-2021.epw",
)

BASE_IDF = os.path.join(DATA_MODELS, "changsha_era2.idf")  # Era 2 as SA baseline

# ---------------------------------------------------------------------------
# SA problem definition
# ---------------------------------------------------------------------------
# Parameters and physically motivated ranges for Changsha HSCW residential
# buildings. Ranges bracket values across the three construction eras and
# plausible retrofit levels.
#
# Ref:  JGJ 134-2010, GB 50189-2015, Chen et al. (2022 Bldg Simul)

PROBLEM = {
    "num_vars": 10,
    "names": [
        "wall_U",           # W/m²K  — wall overall thermal transmittance
        "roof_U",           # W/m²K  — roof overall thermal transmittance
        "window_U",         # W/m²K  — window centre-of-glass U-factor
        "WWR",              # —      — window-to-wall ratio (fraction)
        "infiltration",     # ACH    — air changes per hour
        "cooling_setpoint", # °C     — cooling thermostat setpoint
        "heating_setpoint", # °C     — heating thermostat setpoint
        "lighting_power",   # W/m²   — lighting power density
        "equipment_power",  # W/m²   — plug load power density
        "occupant_density", # m²/person
    ],
    "bounds": [
        [0.4,  1.8],    # wall_U           (Era3 code limit → pre-code)
        [0.3,  1.4],    # roof_U
        [2.0,  6.0],    # window_U         (low-e double → single-pane)
        [0.20, 0.50],   # WWR
        [0.3,  2.0],    # infiltration
        [24.0, 28.0],   # cooling_setpoint (typical Chinese residential range)
        [16.0, 20.0],   # heating_setpoint
        [3.0,  12.0],   # lighting_power   (LED → fluorescent vintage)
        [2.0,  10.0],   # equipment_power
        [15.0, 40.0],   # occupant_density  (persons per m² → sparse)
    ],
    "groups": None,
}

# Morris sampling settings
MORRIS_N = 10          # number of trajectories (increase to 50+ for publication)
MORRIS_LEVELS = 4      # number of grid levels (4 or 6 typical)
MORRIS_SEED = 42       # reproducibility

# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------

def generate_sample(problem=PROBLEM, N=MORRIS_N, num_levels=MORRIS_LEVELS,
                    seed=MORRIS_SEED):
    """
    Generate Morris sample matrix.

    Returns:
        X (np.ndarray): shape (N*(D+1), D) — parameter combinations
        problem (dict): the problem definition
    """
    log.info(f"Generating Morris sample: N={N}, levels={num_levels}, "
             f"D={problem['num_vars']} parameters")
    X = morris_sample.sample(
        problem,
        N=N,
        num_levels=num_levels,
        seed=seed,
        optimal_trajectories=None,
    )
    log.info(f"  Sample matrix shape: {X.shape}  "
             f"({X.shape[0]} EnergyPlus runs required)")
    return X


# ---------------------------------------------------------------------------
# EnergyPlus runner (placeholder — complete after Task 3 IDF files are ready)
# ---------------------------------------------------------------------------

def apply_params_to_idf(base_idf_path, params_dict, output_idf_path):
    """
    Write a modified IDF with the given parameter values.
    Calls adapt_envelope.py logic for envelope params;
    other params (setpoints, LPD, EPD, occupancy) modify schedules/objects.

    Args:
        base_idf_path (str): path to the base IDF (changsha_era2.idf)
        params_dict (dict): parameter name → value
        output_idf_path (str): where to write the modified IDF

    NOTE: This function is a structured placeholder.  The full implementation
    requires:
      - eppy (with EnergyPlus IDD) to modify HVAC setpoints, LPD, EPD
      - The adapt_envelope.TextIDF class for envelope modifications
    """
    import shutil
    shutil.copy(base_idf_path, output_idf_path)

    # ---- envelope ----
    # (could call adapt_envelope functions directly)
    # adapt_envelope.TextIDF → set_opaque_constructions, set_window_properties,
    #                           set_infiltration_ach, set_wwr

    # ---- cooling / heating setpoints ----
    # EnergyPlus objects: ThermostatSetpoint:DualSetpoint
    # Field: Heating_Setpoint_Temperature_Schedule_Name
    #        Cooling_Setpoint_Temperature_Schedule_Name
    # or modify Schedule:Constant objects for setpoints

    # ---- lighting power density ----
    # EnergyPlus object: Lights
    # Field: Watts_per_Zone_Floor_Area

    # ---- equipment power density ----
    # EnergyPlus object: ElectricEquipment
    # Field: Watts_per_Zone_Floor_Area

    # ---- occupant density ----
    # EnergyPlus object: People
    # Field: Zone_Floor_Area_per_Person

    log.debug(f"    Placeholder: copied {os.path.basename(base_idf_path)} → "
              f"{os.path.basename(output_idf_path)}")


def run_energyplus(idf_path, epw_path, output_dir):
    """
    Run a single EnergyPlus simulation.

    Args:
        idf_path (str): modified IDF path
        epw_path (str): weather file path
        output_dir (str): directory for EnergyPlus output files

    Returns:
        float: total annual site energy intensity (kWh/m²·yr), or NaN on error
    """
    os.makedirs(output_dir, exist_ok=True)
    ep_exe = shutil.which("energyplus") or shutil.which("EnergyPlus")
    if ep_exe is None:
        log.warning("EnergyPlus executable not found — returning NaN")
        return float("nan")

    cmd = [ep_exe, "-w", epw_path, "-d", output_dir, idf_path]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300
        )
        if result.returncode != 0:
            log.warning(f"EnergyPlus error (rc={result.returncode}): "
                        f"{result.stderr[-200:]}")
            return float("nan")
    except subprocess.TimeoutExpired:
        log.warning("EnergyPlus timed out after 5 min")
        return float("nan")

    # Parse output: read eplusout.csv or .eso for site energy
    # Simplest: read the HTML summary table or the EnergyPlusOutput.csv
    eso_path = os.path.join(output_dir, "eplusout.eso")
    if not os.path.isfile(eso_path):
        return float("nan")

    # Look for "Site:EnergyMeterArray" or use the Table output
    # Here we parse the tab-separated annual total from eplusout.eso
    # (A full parser is needed for production use; use pandas/eppy for this)
    return _parse_site_energy(output_dir)


def _parse_site_energy(output_dir):
    """
    Parse annual total site energy intensity (kWh/m²) from EnergyPlus output.
    Tries multiple output file formats in order of preference.

    Returns float (kWh/m²) or NaN.
    """
    # Try reading from the annual summary CSV (EnergyPlus -o csv generates this)
    csv_path = os.path.join(output_dir, "eplusout.csv")
    if os.path.isfile(csv_path):
        try:
            df = pd.read_csv(csv_path)
            # Look for a column containing site energy intensity
            for col in df.columns:
                if "site" in col.lower() and "energy" in col.lower():
                    return float(df[col].iloc[-1])
        except Exception:
            pass

    # Fallback: return NaN (implement full ESO parser for production)
    log.debug("    Could not parse site energy from EnergyPlus output — NaN")
    return float("nan")


def run_model(X_row, base_idf, epw_path, run_idx):
    """
    Evaluate the model for one row of the Morris sample matrix.

    Args:
        X_row (np.ndarray): 1D array of parameter values
        base_idf (str): path to the base IDF file
        epw_path (str): EPW weather file path
        run_idx (int): index for this run (used in output directory naming)

    Returns:
        float: model output Y (annual cooling + heating energy, kWh/m²)
    """
    params = dict(zip(PROBLEM["names"], X_row))

    with tempfile.TemporaryDirectory(prefix=f"ep_run_{run_idx:04d}_") as tmpdir:
        mod_idf = os.path.join(tmpdir, f"run_{run_idx:04d}.idf")
        apply_params_to_idf(base_idf, params, mod_idf)
        Y = run_energyplus(mod_idf, epw_path, os.path.join(tmpdir, "out"))

    return Y


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyze_results(problem, X, Y):
    """
    Run SALib Morris analysis.

    Args:
        problem (dict): SALib problem definition
        X (np.ndarray): sample matrix  (n_runs, n_params)
        Y (np.ndarray): model outputs  (n_runs,)

    Returns:
        dict: SALib sensitivity indices (mu, mu_star, sigma, mu_star_conf)
    """
    log.info("Running Morris analysis ...")
    Si = morris_analyze.analyze(
        problem,
        X,
        Y,
        conf_level=0.95,
        print_to_console=False,
        num_levels=MORRIS_LEVELS,
    )
    return Si


def save_results(Si, problem, out_csv):
    """Save sensitivity indices to CSV."""
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df = pd.DataFrame({
        "parameter": problem["names"],
        "mu_star": Si["mu_star"],
        "mu_star_conf": Si["mu_star_conf"],
        "sigma": Si["sigma"],
        "mu": Si["mu"],
    })
    df = df.sort_values("mu_star", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    df.to_csv(out_csv, index=False, float_format="%.4f")
    log.info(f"Saved sensitivity indices → {out_csv}")
    return df


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

# Label mapping: internal name → paper-ready label
PARAM_LABELS = {
    "wall_U":           r"Wall $U$ (W/m²K)",
    "roof_U":           r"Roof $U$ (W/m²K)",
    "window_U":         r"Window $U$ (W/m²K)",
    "WWR":              "WWR",
    "infiltration":     "Infiltration (ACH)",
    "cooling_setpoint": "Cooling setpoint (°C)",
    "heating_setpoint": "Heating setpoint (°C)",
    "lighting_power":   r"Lighting (W/m²)",
    "equipment_power":  r"Equipment (W/m²)",
    "occupant_density": "Occupant density (m²/p)",
}

# Colour coding by parameter group
GROUP_COLORS = {
    "wall_U":           "#2c7bb6",   # blue — envelope opaque
    "roof_U":           "#2c7bb6",
    "window_U":         "#abd9e9",   # light blue — envelope transparent
    "WWR":              "#abd9e9",
    "infiltration":     "#74c476",   # green — air tightness
    "cooling_setpoint": "#d7191c",   # red — occupant behaviour
    "heating_setpoint": "#d7191c",
    "lighting_power":   "#fdae61",   # orange — internal gains
    "equipment_power":  "#fdae61",
    "occupant_density": "#fdae61",
}


def plot_morris_scatter(Si, problem, out_png):
    """
    μ* vs σ scatter plot — standard Morris ranking chart.

    Quadrant interpretation:
      High μ*, low σ  → important, linear/additive effect
      High μ*, high σ → important, nonlinear/interacting
      Low  μ*, low σ  → negligible
    """
    os.makedirs(os.path.dirname(out_png), exist_ok=True)

    names = problem["names"]
    mu_star = np.asarray(Si["mu_star"])
    sigma   = np.asarray(Si["sigma"])
    conf    = np.asarray(Si["mu_star_conf"])

    fig, ax = plt.subplots(figsize=(7, 5.5))

    for i, name in enumerate(names):
        color = GROUP_COLORS.get(name, "#888888")
        ax.errorbar(
            mu_star[i], sigma[i],
            xerr=conf[i],
            fmt="o",
            color=color,
            markersize=9,
            capsize=4,
            linewidth=1.2,
            label=PARAM_LABELS.get(name, name),
        )
        ax.annotate(
            PARAM_LABELS.get(name, name),
            xy=(mu_star[i], sigma[i]),
            xytext=(5, 4),
            textcoords="offset points",
            fontsize=7.5,
            color=color,
        )

    # Reference line: σ = μ* (used in some studies to separate linear/nonlinear)
    lim = max(max(mu_star), max(sigma)) * 1.15
    ax.plot([0, lim], [0, lim], "k--", linewidth=0.8, alpha=0.4,
            label=r"$\sigma = \mu^*$")

    ax.set_xlabel(r"$\mu^*$ — Modified mean elementary effect", fontsize=11)
    ax.set_ylabel(r"$\sigma$ — Standard deviation of elementary effects", fontsize=11)
    ax.set_title(
        "Morris Sensitivity Analysis\nChangsha Residential Building Energy",
        fontsize=12,
    )
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f"))
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.1f"))

    # Quadrant labels
    ax.text(0.97, 0.97, "Important\n(nonlinear/interactions)",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=8, color="#888888")
    ax.text(0.97, 0.05, "Important\n(linear/additive)",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8, color="#888888")
    ax.text(0.03, 0.05, "Negligible",
            transform=ax.transAxes, ha="left", va="bottom",
            fontsize=8, color="#888888")

    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_aspect("equal", adjustable="box")
    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close()
    log.info(f"Saved Morris scatter plot → {out_png}")


def plot_mu_star_bar(df_results, out_png):
    """
    Horizontal bar chart of μ* values with confidence intervals.
    Useful as a supplementary figure or main ranking chart.
    """
    os.makedirs(os.path.dirname(out_png), exist_ok=True)

    df = df_results.sort_values("mu_star", ascending=True)
    labels = [PARAM_LABELS.get(n, n) for n in df["parameter"]]
    colors = [GROUP_COLORS.get(n, "#888888") for n in df["parameter"]]

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    bars = ax.barh(labels, df["mu_star"], xerr=df["mu_star_conf"],
                   color=colors, edgecolor="white", linewidth=0.5,
                   error_kw={"elinewidth": 1.2, "capsize": 3})

    ax.set_xlabel(r"$\mu^*$ — Modified mean elementary effect", fontsize=11)
    ax.set_title("Morris SA Parameter Ranking\n(Changsha residential, Era 2 baseline)",
                 fontsize=11)
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.set_xlim(left=0)
    plt.tight_layout()
    plt.savefig(out_png, dpi=150, bbox_inches="tight")
    plt.close()
    log.info(f"Saved μ* bar chart → {out_png}")


# ---------------------------------------------------------------------------
# Demo mode — synthetic results for testing the analysis/plotting pipeline
# ---------------------------------------------------------------------------

def run_demo():
    """
    Run SA with synthetic (dummy) model outputs to test the full pipeline
    without requiring EnergyPlus.

    The synthetic model is:
        Y = a1*wall_U + a2*roof_U + a3*window_U + a4*WWR + a5*infiltration
          + a6*(cooling_sp - 26)^2 + a7*(heating_sp - 18)
          + a8*lighting + a9*equipment + a10/occupant_density + noise

    This mimics physically reasonable sensitivity ordering:
    window_U > infiltration > wall_U > cooling_setpoint > ...
    """
    log.info("=== DEMO MODE (synthetic model — no EnergyPlus required) ===")

    X = generate_sample()
    log.info(f"Evaluating synthetic model on {X.shape[0]} sample points ...")

    # Coefficients (arbitrary but physically informed order of magnitude)
    # HSCW zone: cooling dominated, so cooling_setpoint and window_U are key
    coeffs = {
        "wall_U":           8.0,
        "roof_U":           5.0,
        "window_U":         12.0,
        "WWR":              25.0,
        "infiltration":     18.0,
        "cooling_setpoint": -7.0,   # higher setpoint → less cooling
        "heating_setpoint": 4.0,    # higher setpoint → more heating
        "lighting_power":   3.5,
        "equipment_power":  2.0,
        "occupant_density": -0.8,   # more persons/m² → less area → more gains
    }

    names = PROBLEM["names"]
    bounds = PROBLEM["bounds"]

    # Normalize to [0, 1] for consistent coefficient interpretation
    def norm(val, lo, hi):
        return (val - lo) / (hi - lo)

    Y = np.zeros(X.shape[0])
    rng = np.random.default_rng(MORRIS_SEED)

    for j, row in enumerate(X):
        y = 60.0  # baseline offset (kWh/m²)
        for i, name in enumerate(names):
            lo, hi = bounds[i]
            x_n = norm(row[i], lo, hi)
            c = coeffs[name]
            if name == "cooling_setpoint":
                y += c * x_n + 2.0 * x_n**2  # nonlinear
            else:
                y += c * x_n
        y += rng.normal(0, 1.5)  # noise
        Y[j] = y

    log.info(f"  Y stats: min={Y.min():.1f}  max={Y.max():.1f}  "
             f"mean={Y.mean():.1f} kWh/m²")
    return X, Y


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Morris SA for Changsha residential building energy"
    )
    parser.add_argument(
        "--demo", action="store_true",
        help="Use synthetic model outputs (no EnergyPlus required)"
    )
    parser.add_argument(
        "--N", type=int, default=MORRIS_N,
        help=f"Number of Morris trajectories (default {MORRIS_N})"
    )
    args = parser.parse_args()

    os.makedirs(DATA_PROCESSED, exist_ok=True)
    os.makedirs(FIGURES, exist_ok=True)

    out_csv = os.path.join(DATA_PROCESSED, "morris_results.csv")
    out_scatter = os.path.join(FIGURES, "fig01_morris_scatter.png")
    out_bar = os.path.join(FIGURES, "fig02_morris_bar.png")

    if args.demo:
        X, Y = run_demo()
    else:
        # Full run with EnergyPlus
        if not os.path.isfile(BASE_IDF):
            log.error(f"Base IDF not found: {BASE_IDF}")
            log.error("Run adapt_envelope.py (Task 3) first.")
            sys.exit(1)
        if not os.path.isfile(EPW_FILE):
            log.error(f"EPW not found: {EPW_FILE}")
            log.error("Run Task 1 first to download the Changsha EPW file.")
            sys.exit(1)
        if shutil.which("energyplus") is None:
            log.error("energyplus executable not found on PATH.")
            log.error("Install EnergyPlus (https://energyplus.net/) and add it to PATH.")
            log.error("Use --demo to test the analysis pipeline without EnergyPlus.")
            sys.exit(1)

        PROBLEM["num_vars"] = len(PROBLEM["names"])
        X = generate_sample(problem=PROBLEM, N=args.N)
        n_runs = X.shape[0]
        Y = np.zeros(n_runs)

        log.info(f"Running {n_runs} EnergyPlus simulations ...")
        for i, row in enumerate(X):
            log.info(f"  Run {i+1}/{n_runs} ...")
            Y[i] = run_model(row, BASE_IDF, EPW_FILE, run_idx=i)

        if np.all(np.isnan(Y)):
            log.error("All EnergyPlus runs returned NaN. Cannot compute SA.")
            sys.exit(1)

        # Replace NaNs with mean for analysis (flag warning)
        n_nan = np.sum(np.isnan(Y))
        if n_nan > 0:
            log.warning(f"  {n_nan} NaN outputs replaced with mean for analysis.")
            Y = np.where(np.isnan(Y), np.nanmean(Y), Y)

    # Analyse
    Si = analyze_results(PROBLEM, X, Y)

    # Print summary table
    log.info("\n--- Morris Sensitivity Indices ---")
    log.info(f"{'Parameter':<22} {'μ*':>8} {'±conf':>8} {'σ':>8} {'μ':>8}")
    log.info("-" * 58)
    for i, name in enumerate(PROBLEM["names"]):
        log.info(
            f"{name:<22} "
            f"{Si['mu_star'][i]:>8.3f} "
            f"{Si['mu_star_conf'][i]:>8.3f} "
            f"{Si['sigma'][i]:>8.3f} "
            f"{Si['mu'][i]:>8.3f}"
        )

    # Save + plot
    df = save_results(Si, PROBLEM, out_csv)
    plot_morris_scatter(Si, PROBLEM, out_scatter)
    plot_mu_star_bar(df, out_bar)

    log.info("\nTop 5 most influential parameters:")
    for _, row in df.head(5).iterrows():
        log.info(f"  #{int(row['rank'])} {row['parameter']:<22}  "
                 f"μ*={row['mu_star']:.3f}")


if __name__ == "__main__":
    main()
