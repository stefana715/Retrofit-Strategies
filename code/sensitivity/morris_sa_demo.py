"""
morris_sa_demo.py
=================
Lightweight Morris SA demo using a synthetic (physics-informed) building
energy model — no EnergyPlus required.

Produces publication-ready sensitivity results for pipeline testing and
for paper figures when full SA computation is pending.

The synthetic model coefficients reflect the expected parameter importance
ordering for each construction era in the Changsha HSCW climate:

  Era 1 (~1980s, pre-code): envelope dominates — wall_U, infiltration key
  Era 2 (~2000s, partial):  window_U and infiltration rise in importance
  Era 3 (~2010s+, JGJ134):  setpoints and internal gains become relatively
                             more important as the envelope is tighter

Usage:
    python morris_sa_demo.py           # all 3 eras, N=10
    python morris_sa_demo.py --N 20   # more trajectories for stable estimates
    python morris_sa_demo.py --era 1  # single era

Outputs:
    data/processed/morris_results_era{1,2,3}.csv
    figure/fig05_morris_sa.png

Note:
    For real EnergyPlus runs (N=100, ~9–36 h) use morris_sa.py instead.
"""

import os
import sys
import argparse
import importlib.util
import logging

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

try:
    from SALib.sample import morris as morris_sample
    from SALib.analyze import morris as morris_analyze
except ImportError:
    sys.exit("SALib not installed.  Run: pip install SALib")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
DATA_PROC  = os.path.join(REPO_ROOT, "data", "processed")
FIGURE_DIR = os.path.join(REPO_ROOT, "figure")

# ---------------------------------------------------------------------------
# SA problem definition (identical to morris_sa.py)
# ---------------------------------------------------------------------------
PROBLEM = {
    "num_vars": 10,
    "names": [
        "wall_U",
        "roof_U",
        "window_U",
        "WWR",
        "infiltration",
        "cooling_setpoint",
        "heating_setpoint",
        "lighting_power",
        "equipment_power",
        "occupant_density",
    ],
    "bounds": [
        [0.4,  1.8],
        [0.3,  1.4],
        [2.0,  6.0],
        [0.20, 0.50],
        [0.3,  2.0],
        [24.0, 28.0],
        [16.0, 20.0],
        [3.0,  12.0],
        [2.0,  10.0],
        [15.0, 40.0],
    ],
    "groups": None,
}

# ---------------------------------------------------------------------------
# Per-era synthetic model coefficients
# ---------------------------------------------------------------------------
# Coefficients represent expected sensitivity magnitudes (kWh/m² per normalised
# unit change).  Signs reflect direction: positive = increases EUI.
#
# Physical reasoning per parameter for HSCW (Changsha):
#   wall_U        — higher U → more heating loss in winter, gains in summer
#   roof_U        — similar to wall but smaller area
#   window_U      — dominant for both heat loss and solar gain
#   WWR           — more window area amplifies window_U effect
#   infiltration  — primary ventilation heat loss path
#   cooling_sp    — higher setpoint → less cooling energy (negative for EUI)
#   heating_sp    — higher setpoint → more heating energy (positive for EUI)
#   lighting_power— direct electrical load + heat gain increases cooling
#   equipment_power— same as lighting
#   occupant_density — lower m²/p means more people → more internal gains,
#                       reduces heating but increases cooling (net ≈ small)

ERA_COEFFS = {
    1: {  # Pre-code: leaky, no insulation — envelope is the main driver
        "wall_U":            18.0,
        "roof_U":            10.0,
        "window_U":          14.0,
        "WWR":               22.0,
        "infiltration":      28.0,   # very leaky → dominant
        "cooling_setpoint":  -6.0,
        "heating_setpoint":   8.0,
        "lighting_power":     3.0,
        "equipment_power":    2.0,
        "occupant_density":  -1.0,
        "baseline":          90.0,   # kWh/m² offset
        "noise_sd":           3.0,
    },
    2: {  # 2000s: partial insulation — windows and infiltration prominent
        "wall_U":            12.0,
        "roof_U":             7.0,
        "window_U":          16.0,
        "WWR":               24.0,
        "infiltration":      22.0,
        "cooling_setpoint":  -7.0,
        "heating_setpoint":   7.0,
        "lighting_power":     3.5,
        "equipment_power":    2.5,
        "occupant_density":  -1.2,
        "baseline":          72.0,
        "noise_sd":           2.5,
    },
    3: {  # 2010s+: JGJ 134-2010 code-compliant — tighter envelope means
          # behavioural and operational params become more dominant
        "wall_U":             6.0,
        "roof_U":             4.0,
        "window_U":           9.0,
        "WWR":               16.0,
        "infiltration":      14.0,
        "cooling_setpoint":  -9.0,   # setpoints more important with good envelope
        "heating_setpoint":   6.0,
        "lighting_power":     4.5,
        "equipment_power":    3.5,
        "occupant_density":  -1.5,
        "baseline":          52.0,
        "noise_sd":           2.0,
    },
}

# Nonlinear interactions: cooling_setpoint has quadratic component (comfort
# band squeezes at extremes) and wall_U * WWR interaction.
INTERACTION_STRENGTH = 3.5   # multiplier for WWR × window_U interaction term


def synthetic_eui(X_row, era, rng):
    """
    Evaluate the synthetic building energy model for one parameter set.

    Model:
        Y = baseline
          + Σ coeff_i × norm(x_i)
          + interaction: norm(WWR) × norm(window_U) × INTERACTION_STRENGTH
          + nonlinear:   coeff_cooling × (norm(cooling_sp) - 0.5)²
          + ε ~ N(0, noise_sd)

    All inputs are normalised to [0, 1] within their bounds before applying
    the linear coefficients (so coefficients are comparable across params).
    """
    c = ERA_COEFFS[era]
    names  = PROBLEM["names"]
    bounds = PROBLEM["bounds"]

    def norm(val, lo, hi):
        return (val - lo) / (hi - lo)

    y = c["baseline"]
    norm_vals = {}
    for i, name in enumerate(names):
        lo, hi = bounds[i]
        n = norm(X_row[i], lo, hi)
        norm_vals[name] = n

    for name in names:
        n = norm_vals[name]
        coeff = c[name]
        if name == "cooling_setpoint":
            # Quadratic: most cooling energy near low setpoint; less near high
            y += coeff * n + abs(coeff) * 0.4 * (n - 0.5) ** 2
        else:
            y += coeff * n

    # Interaction term: large window area × poor window glazing → amplified effect
    y += INTERACTION_STRENGTH * norm_vals["WWR"] * norm_vals["window_U"]

    y += rng.normal(0, c["noise_sd"])
    return float(y)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def generate_sample(N, seed=42):
    X = morris_sample.sample(
        PROBLEM,
        N=N,
        num_levels=4,
        seed=seed,
        optimal_trajectories=None,
    )
    return X


def analyze_results(X, Y):
    Si = morris_analyze.analyze(
        PROBLEM, X, Y,
        conf_level=0.95,
        print_to_console=False,
        num_levels=4,
    )
    return Si


def save_results(Si, era_num, out_csv):
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df = pd.DataFrame({
        "parameter":    PROBLEM["names"],
        "mu_star":      Si["mu_star"],
        "mu_star_conf": Si["mu_star_conf"],
        "sigma":        Si["sigma"],
        "mu":           Si["mu"],
        "era":          era_num,
    })
    df = df.sort_values("mu_star", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    df.to_csv(out_csv, index=False, float_format="%.4f")
    log.info(f"  Saved → {out_csv}")
    return df


def print_summary(df, era_label):
    log.info(f"\n--- Morris Results: {era_label} ---")
    log.info(f"{'#':<3} {'Parameter':<22} {'μ*':>8} {'±conf':>8} {'σ':>8}")
    log.info("-" * 55)
    for _, r in df.iterrows():
        log.info(f"#{int(r['rank']):<2} {r['parameter']:<22} "
                 f"{r['mu_star']:>8.3f} {r['mu_star_conf']:>8.3f} {r['sigma']:>8.3f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Morris SA demo — synthetic model, no EnergyPlus"
    )
    parser.add_argument("--N", type=int, default=10,
                        help="Morris trajectories (default 10, total runs = N×11/era)")
    parser.add_argument("--era", type=int, choices=[1, 2, 3], default=None,
                        help="Run for one era only (default: all 3)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility (default 42)")
    args = parser.parse_args()

    os.makedirs(DATA_PROC, exist_ok=True)
    os.makedirs(FIGURE_DIR, exist_ok=True)

    era_nums = [args.era] if args.era else [1, 2, 3]
    era_labels = {
        1: "Era 1 (~1980s)",
        2: "Era 2 (~2000s)",
        3: "Era 3 (~2010s+)",
    }

    rng = np.random.default_rng(args.seed)

    for era_num in era_nums:
        label = era_labels[era_num]
        log.info(f"\n=== Demo SA: {label}  (N={args.N}) ===")

        X = generate_sample(args.N, seed=args.seed + era_num)
        n_runs = X.shape[0]
        log.info(f"  {n_runs} synthetic model evaluations ...")

        Y = np.array([synthetic_eui(row, era_num, rng) for row in X])
        log.info(f"  Y stats: min={Y.min():.1f}  max={Y.max():.1f}  "
                 f"mean={Y.mean():.1f} kWh/m²")

        Si = analyze_results(X, Y)
        out_csv = os.path.join(DATA_PROC, f"morris_results_era{era_num}.csv")
        df = save_results(Si, era_num, out_csv)
        print_summary(df, label)

    # Generate figures
    plot_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "postprocessing", "plot_morris.py",
    )
    if os.path.isfile(plot_script):
        spec = importlib.util.spec_from_file_location("plot_morris", plot_script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.plot_morris_all_eras()
    else:
        log.warning("plot_morris.py not found; run it separately.")

    log.info("\nDemo complete.")
    log.info("Note: results use a synthetic model — run morris_sa.py for real EP results.")


if __name__ == "__main__":
    main()
