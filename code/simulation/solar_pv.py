"""
solar_pv.py
===========
Estimate annual rooftop PV generation and net energy balance for each
Changsha residential archetype using pvlib-python and the Changsha TMY
weather file.

Covers:
    - Three archetypes × {Baseline, R5_Combined retrofit}
    - Annual PV generation (kWh, kWh/m² floor)
    - Monthly generation profile
    - Self-consumption and self-sufficiency ratios
      (synthetic residential hourly load profile, scaled to archetype EUI)
    - Net energy balance = retrofitted EUI − PV generation per m² floor

Produces:
    data/processed/solar_results.csv      — annual summary per scenario
    data/processed/solar_monthly.csv      — monthly generation per archetype

Usage (standalone):
    python solar_pv.py

Or called programmatically:
    from solar_pv import run_solar_analysis
    run_solar_analysis()

Reads:
    data/climate/CHN_HN_Changsha.576870_TMYx.2007-2021.epw
    data/processed/retrofit_results.csv
"""

import os
import sys
import logging

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

try:
    import pvlib
except ImportError:
    sys.exit("pvlib not installed.  Run: pip install pvlib")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT     = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_PROC     = os.path.join(REPO_ROOT, "data", "processed")
DATA_CLIMATE  = os.path.join(REPO_ROOT, "data", "climate")
FIGURE_DIR    = os.path.join(REPO_ROOT, "figure")

EPW_FILE         = os.path.join(DATA_CLIMATE, "CHN_HN_Changsha.576870_TMYx.2007-2021.epw")
RETROFIT_CSV     = os.path.join(DATA_PROC, "retrofit_results.csv")
OUT_SOLAR        = os.path.join(DATA_PROC, "solar_results.csv")
OUT_MONTHLY      = os.path.join(DATA_PROC, "solar_monthly.csv")

# ---------------------------------------------------------------------------
# Site and system constants
# ---------------------------------------------------------------------------
CHANGSHA_LAT   = 28.11     # degrees N (from EPW metadata)
CHANGSHA_LON   = 112.79    # degrees E
CHANGSHA_ALT   = 120.0     # m a.s.l.
CHANGSHA_TZ    = "Asia/Shanghai"

PV_TILT        = 25.0      # degrees — near-optimal for 28°N latitude
PV_AZIMUTH     = 180.0     # degrees — south-facing

PV_EFFICIENCY  = 0.20      # STC module efficiency (20 % monocrystalline Si)
PERF_RATIO     = 0.80      # System performance ratio (inverter + wiring + soiling)
TEMP_COEFF     = -0.004    # Pmpp temperature coefficient per °C (typical Si)
T_STC          = 25.0      # °C reference temperature

# Roof parameters per archetype type
ROOF_PARAMS = {
    "MidRise":  {"roof_total_m2": 600.0, "usable_frac": 0.60},
    "HighRise": {"roof_total_m2": 400.0, "usable_frac": 0.50},
}

# ---------------------------------------------------------------------------
# Archetype definitions
# Floor areas derived from EnergyPlus eplustbl.csv: total_GJ × 1000 / EUI_MJ_m2
# MidRise (6F, DOE prototype):  3134.6 m²
# HighRise (18F, DOE prototype): 7836.4 m²
# ---------------------------------------------------------------------------
ARCHETYPES = {
    "Era1_1980s_MidRise": {
        "era":        1,
        "era_label":  "Era 1 (~1980s)",
        "arch_type":  "MidRise",
        "floor_area": 3134.6,
    },
    "Era2_2000s_MidRise": {
        "era":        2,
        "era_label":  "Era 2 (~2000s)",
        "arch_type":  "MidRise",
        "floor_area": 3134.6,
    },
    "Era3_2010s_HighRise": {
        "era":        3,
        "era_label":  "Era 3 (~2010s+)",
        "arch_type":  "HighRise",
        "floor_area": 7836.4,
    },
}

RETROFITS_OF_INTEREST = ["Baseline", "R5_Combined"]


# ---------------------------------------------------------------------------
# Load profile helper
# ---------------------------------------------------------------------------

def make_synthetic_load_profile(annual_eui_kwh_m2: float,
                                floor_area_m2: float,
                                index: pd.DatetimeIndex) -> np.ndarray:
    """
    Generate a synthetic hourly electricity load profile (8760 values, kWh/h).

    Shape is based on typical Chinese urban residential patterns:
      - Low overnight baseload (0–5 h)
      - Morning peak during 7–9 h (breakfast, getting ready)
      - Daytime trough with small midday bump (12–13 h)
      - Strong evening peak 18–22 h (cooking, TV, AC/heating)
    Seasonal scaling:
      - Summer (+20 % for cooling) / Winter (+15 % for heating)
      - Shoulder months: baseline

    The profile is normalised so that its integral equals
    annual_eui_kwh_m2 × floor_area_m2.

    Parameters
    ----------
    annual_eui_kwh_m2 : float
        Annual energy intensity of the building (kWh/m²·yr).
    floor_area_m2 : float
        Conditioned floor area (m²).
    index : pd.DatetimeIndex
        Hourly time index (8760 entries) used to extract hour and month.

    Returns
    -------
    np.ndarray of shape (8760,), kWh per hour.
    """
    hour_shape = np.array([
        0.25, 0.20, 0.18, 0.17, 0.18, 0.25,  # 00–05 h (overnight baseload)
        0.50, 1.20, 1.50, 0.80, 0.65, 0.60,  # 06–11 h (morning peak)
        0.75, 0.55, 0.45, 0.42, 0.50, 0.85,  # 12–17 h (daytime trough)
        1.55, 1.80, 1.80, 1.60, 1.25, 0.85,  # 18–23 h (evening peak)
    ])                                          # shape sums to 20.0

    # Monthly seasonal multipliers (relative to annual average day)
    monthly_mult = {
        1: 1.10, 2: 1.05, 3: 0.95, 4: 0.90,
        5: 0.95, 6: 1.15, 7: 1.25, 8: 1.20,
        9: 1.05, 10: 0.90, 11: 0.90, 12: 1.10,
    }

    hours = np.array([ts.hour for ts in index])
    months = np.array([ts.month for ts in index])

    profile = np.array([
        hour_shape[h] * monthly_mult[m]
        for h, m in zip(hours, months)
    ])

    # Normalise so annual total = annual_eui × floor_area
    annual_total_kwh = annual_eui_kwh_m2 * floor_area_m2
    profile = profile / profile.sum() * annual_total_kwh

    return profile


# ---------------------------------------------------------------------------
# PV calculation
# ---------------------------------------------------------------------------

def compute_pv_generation(epw_data: pd.DataFrame,
                           meta: dict,
                           pv_area_m2: float) -> pd.Series:
    """
    Calculate hourly PV generation (kWh/h) from EPW irradiance data.

    Method:
        1. Compute solar position.
        2. Transpose GHI/DNI/DHI to plane-of-array (POA) using Perez model.
        3. Apply cell temperature correction (Faiman/SAPM model).
        4. Apply fixed performance ratio for remaining system losses.

    Returns
    -------
    pd.Series, index = epw_data.index, values in kWh per hour.
    """
    location = pvlib.location.Location(
        latitude  = meta["latitude"],
        longitude = meta["longitude"],
        tz        = CHANGSHA_TZ,
        altitude  = meta["altitude"],
        name      = meta["city"],
    )

    solar_pos = location.get_solarposition(epw_data.index)

    poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt    = PV_TILT,
        surface_azimuth = PV_AZIMUTH,
        solar_zenith    = solar_pos["apparent_zenith"],
        solar_azimuth   = solar_pos["azimuth"],
        dni             = epw_data["dni"],
        ghi             = epw_data["ghi"],
        dhi             = epw_data["dhi"],
        model           = "perez",
        airmass         = location.get_airmass(solar_position=solar_pos)["airmass_relative"],
        dni_extra        = pvlib.irradiance.get_extra_radiation(epw_data.index),
    )

    # Cell temperature (Faiman model via SAPM coefficients for glass/glass free-mount)
    t_cell = pvlib.temperature.sapm_cell(
        poa_global = poa["poa_global"],
        temp_air   = epw_data["temp_air"],
        wind_speed = epw_data["wind_speed"],
        a          = -3.56,   # SAPM free-standing rack
        b          = -0.0750,
        deltaT     = 3,
    )

    # Temperature correction factor
    temp_factor = 1.0 + TEMP_COEFF * (t_cell - T_STC)
    temp_factor = temp_factor.clip(lower=0.5)   # physical safeguard

    # Hourly DC power (W), applying temperature correction
    p_dc = poa["poa_global"] * pv_area_m2 * PV_EFFICIENCY * temp_factor

    # Hourly AC energy (kWh/h), applying remaining performance ratio
    # (inverter, wiring, soiling — temperature already accounted for above)
    pr_remaining = PERF_RATIO / 0.95  # approx: 0.80 / 0.95 ≈ 0.842
    # The full PR=0.80 includes temperature losses; since we handle those
    # explicitly, we apply a reduced PR for other losses.
    p_ac_kwh = (p_dc * pr_remaining / 1000.0).clip(lower=0.0)

    # Fill NaN (edge cases at sunrise/sunset, below-horizon angles) with 0.
    # These represent hours with no viable solar generation.
    return p_ac_kwh.fillna(0.0)


def compute_self_consumption(pv_gen_kwh: np.ndarray,
                              load_kwh: np.ndarray) -> dict:
    """
    Calculate self-consumption and self-sufficiency ratios.

    Definitions (IEC 62786 / EN 15316-4-6):
        self_consumption = Σ min(PV, Load) / Σ PV
        self_sufficiency = Σ min(PV, Load) / Σ Load

    Parameters
    ----------
    pv_gen_kwh  : np.ndarray (8760,) — hourly PV generation (kWh/h)
    load_kwh    : np.ndarray (8760,) — hourly electrical demand (kWh/h)

    Returns
    -------
    dict with keys: self_consumption, self_sufficiency, direct_use_kwh
    """
    direct_use = np.minimum(pv_gen_kwh, load_kwh).sum()
    total_pv   = pv_gen_kwh.sum()
    total_load = load_kwh.sum()

    return {
        "direct_use_kwh":    round(direct_use, 1),
        "self_consumption":  round(direct_use / total_pv   if total_pv   > 0 else 0.0, 4),
        "self_sufficiency":  round(direct_use / total_load if total_load > 0 else 0.0, 4),
    }


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def run_solar_analysis(
        epw_path    = EPW_FILE,
        retro_csv   = RETROFIT_CSV,
        out_csv     = OUT_SOLAR,
        out_monthly = OUT_MONTHLY,
):
    """
    Run the full solar PV integration analysis.

    For each archetype × {Baseline, R5_Combined}:
      1. Compute PV generation from Changsha TMY EPW (pvlib).
      2. Compute self-consumption using synthetic residential load profile.
      3. Calculate net energy balance = retrofit_eui − pv_per_m2_floor.

    Saves solar_results.csv and solar_monthly.csv.
    Returns the summary DataFrame.
    """
    if not os.path.isfile(epw_path):
        log.error(f"EPW file not found: {epw_path}")
        return None
    if not os.path.isfile(retro_csv):
        log.error(f"retrofit_results.csv not found: {retro_csv}")
        return None

    os.makedirs(DATA_PROC, exist_ok=True)

    # -----------------------------------------------------------------------
    # Read EPW and compute PV generation once per archetype type
    # (MidRise and HighRise have different usable areas but same irradiance)
    # -----------------------------------------------------------------------
    log.info(f"Reading EPW: {epw_path}")
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        epw_data, meta = pvlib.iotools.read_epw(epw_path, coerce_year=2013)

    log.info(f"  Location: {meta['city']} "
             f"lat={meta['latitude']:.2f}° lon={meta['longitude']:.2f}° "
             f"alt={meta['altitude']:.0f} m")
    log.info(f"  Annual GHI: {epw_data['ghi'].sum()/1000:.1f} kWh/m²/yr")

    # Compute PV generation for each unique roof configuration
    pv_hourly = {}   # arch_type → pd.Series (kWh/h)
    for arch_type, rp in ROOF_PARAMS.items():
        usable_area = rp["roof_total_m2"] * rp["usable_frac"]
        log.info(f"\nComputing PV generation: {arch_type}  "
                 f"({usable_area:.0f} m² usable = "
                 f"{usable_area * PV_EFFICIENCY:.1f} kWp)")
        pv_hourly[arch_type] = compute_pv_generation(epw_data, meta, usable_area)
        log.info(f"  Annual PV: {pv_hourly[arch_type].sum():.0f} kWh/yr")

    # -----------------------------------------------------------------------
    # Read retrofit results
    # -----------------------------------------------------------------------
    df_ret = pd.read_csv(retro_csv)

    # -----------------------------------------------------------------------
    # Build summary rows
    # -----------------------------------------------------------------------
    rows = []
    monthly_rows = []

    for arch_key, arch in ARCHETYPES.items():
        arch_type  = arch["arch_type"]
        floor_area = arch["floor_area"]
        era        = arch["era"]
        era_label  = arch["era_label"]

        rp         = ROOF_PARAMS[arch_type]
        usable_area = rp["roof_total_m2"] * rp["usable_frac"]
        capacity_kwp = usable_area * PV_EFFICIENCY
        pv_series   = pv_hourly[arch_type]
        pv_annual   = pv_series.sum()                          # kWh/yr
        pv_per_m2   = pv_annual / floor_area                   # kWh/m² floor

        log.info(f"\n{'='*60}")
        log.info(f"Archetype: {arch_key}")
        log.info(f"  Floor area: {floor_area:.1f} m²  |  "
                 f"Usable roof: {usable_area:.0f} m²  |  "
                 f"Capacity: {capacity_kwp:.1f} kWp")
        log.info(f"  Annual PV generation: {pv_annual:.0f} kWh  "
                 f"({pv_per_m2:.1f} kWh/m² floor)")

        # Monthly breakdown (same for all retrofits of this archetype)
        monthly_pv = (
            pv_series
            .groupby(lambda t: t.month)
            .sum()
            .rename("pv_gen_kwh")
        )
        for month, val in monthly_pv.items():
            monthly_rows.append({
                "archetype": arch_key,
                "era":       era,
                "era_label": era_label,
                "arch_type": arch_type,
                "month":     month,
                "pv_gen_kwh": round(float(val), 1),
            })

        # Per-retrofit analysis
        for retrofit_key in RETROFITS_OF_INTEREST:
            row_match = df_ret[
                (df_ret["archetype"] == arch_key) &
                (df_ret["retrofit"]  == retrofit_key)
            ]
            if row_match.empty:
                log.warning(f"  No match in retrofit CSV: {arch_key} / {retrofit_key}")
                continue

            row = row_match.iloc[0]
            eui = float(row["total_eui_kwh_m2"])

            # Self-consumption via synthetic load profile
            load_profile = make_synthetic_load_profile(eui, floor_area, pv_series.index)
            sc_stats     = compute_self_consumption(pv_series.values, load_profile)

            net_eui     = eui - pv_per_m2
            label_str   = "Baseline" if retrofit_key == "Baseline" else "R5_Combined"

            log.info(f"\n  [{label_str}]  EUI={eui:.1f}  "
                     f"PV/m²={pv_per_m2:.1f}  Net={net_eui:.1f} kWh/m²")
            log.info(f"    Self-consumption: {sc_stats['self_consumption']*100:.1f}%  "
                     f"Self-sufficiency: {sc_stats['self_sufficiency']*100:.1f}%")

            rows.append({
                "archetype":           arch_key,
                "era":                 era,
                "era_label":           era_label,
                "arch_type":           arch_type,
                "floor_area_m2":       round(floor_area, 1),
                "retrofit":            label_str,
                "retrofit_eui_kwh_m2": round(eui, 2),
                "pv_usable_area_m2":   usable_area,
                "pv_capacity_kwp":     round(capacity_kwp, 1),
                "pv_annual_kwh":       round(pv_annual, 0),
                "pv_per_m2_floor":     round(pv_per_m2, 2),
                "net_eui_kwh_m2":      round(net_eui, 2),
                "pv_to_demand_ratio":  round(pv_per_m2 / eui if eui > 0 else 0.0, 4),
                "self_consumption_pct":  round(sc_stats["self_consumption"] * 100, 1),
                "self_sufficiency_pct":  round(sc_stats["self_sufficiency"] * 100, 1),
                "direct_use_kwh":        sc_stats["direct_use_kwh"],
            })

    df_summary = pd.DataFrame(rows)
    df_monthly = pd.DataFrame(monthly_rows)

    df_summary.to_csv(out_csv,     index=False)
    df_monthly.to_csv(out_monthly, index=False)

    log.info(f"\nSaved: {out_csv}")
    log.info(f"Saved: {out_monthly}")

    # -----------------------------------------------------------------------
    # Summary table
    # -----------------------------------------------------------------------
    log.info("\n--- Net Energy Balance Summary ---")
    pivot = df_summary.pivot_table(
        index="era_label", columns="retrofit",
        values=["retrofit_eui_kwh_m2", "pv_per_m2_floor", "net_eui_kwh_m2"],
        aggfunc="first",
    )
    log.info(f"\n{pivot.to_string()}")

    return df_summary


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    missing = [p for p in [EPW_FILE, RETROFIT_CSV] if not os.path.isfile(p)]
    if missing:
        for p in missing:
            log.error(f"Required file not found: {p}")
        sys.exit(1)

    df = run_solar_analysis()
    if df is None:
        sys.exit(1)

    # Trigger figure generation
    plot_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "postprocessing", "plot_solar.py",
    )
    if os.path.isfile(plot_script):
        import importlib.util
        spec = importlib.util.spec_from_file_location("plot_solar", plot_script)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.plot_solar_all()
    else:
        log.warning("plot_solar.py not found; run it separately.")

    log.info("\nSolar PV analysis complete.")


if __name__ == "__main__":
    main()
