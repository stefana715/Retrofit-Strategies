"""
generate_future_epw.py
======================
Generate future climate EPW files for Changsha using the statistical
morphing method (Belcher et al. 2005).

Method
------
Each baseline hourly EPW value is shifted using monthly climate change
delta statistics derived from CMIP6 multi-model mean projections:

    T_future(h) = T_baseline(h) + ΔT_month              (temperature shift)
    R_future(h) = R_baseline(h) × α_month               (radiation stretch)
    IR_future(h) = IR_baseline(h) × (T_f+273.15)⁴ /    (IR correction)
                                    (T_b+273.15)⁴

Fields modified
    Col  6  Dry-bulb temperature (°C)       — additive shift ΔT
    Col  7  Dew-point temperature (°C)      — additive shift 0.6 × ΔT
    Col  8  Relative humidity (%)           — recalculated via Magnus formula
    Col 12  Horizontal IR radiation (Wh/m²) — Stefan-Boltzmann T⁴ correction
    Col 13  Global Horizontal Radiation     — multiplicative α_month
    Col 14  Direct Normal Radiation         — multiplicative α_month
    Col 15  Diffuse Horizontal Radiation    — multiplicative α_month

CMIP6 data source
    IPCC AR6 WG1 Interactive Atlas (Iturbide et al. 2021), East Asia region
    (grid cell ~28°N, 113°E), multi-model ensemble median, relative to the
    1995-2014 reference period.  Seasonal patterns follow Wang et al. (2022)
    "Future changes in climate extremes over China and their physical
    attributions" (npj Clim. Atmos. Sci. 5:74).

Produces
    data/climate/Changsha_2050_SSP245.epw
    data/climate/Changsha_2050_SSP585.epw
    data/climate/Changsha_2080_SSP245.epw
    data/climate/Changsha_2080_SSP585.epw

Usage
    python generate_future_epw.py          # all 4 scenarios
    python generate_future_epw.py --list   # print deltas and exit

References
    Belcher S.E. et al. (2005) Constructing design weather data for future
      climates. Build. Serv. Eng. Res. Technol. 26(1), 49-61.
    IPCC AR6 WG1 (2021) Atlas, Section Atlas.5.3 (East Asia).
    Wang X. et al. (2022) npj Clim. Atmos. Sci. 5:74.
"""

import os
import sys
import math
import argparse
import logging

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_CLIMATE = os.path.join(REPO_ROOT, "data", "climate")

BASELINE_EPW = os.path.join(
    DATA_CLIMATE, "CHN_HN_Changsha.576870_TMYx.2007-2021.epw"
)

N_HEADER = 8      # number of non-data header lines in EPW
N_DATA   = 8760   # hours per year

# ---------------------------------------------------------------------------
# EPW data column indices (0-based, comma-separated fields per data row)
# ---------------------------------------------------------------------------
COL_YEAR   = 0
COL_MONTH  = 1
COL_DAY    = 2
COL_HOUR   = 3
COL_TDB    = 6    # dry-bulb temperature (°C)
COL_TDP    = 7    # dew-point temperature (°C)
COL_RH     = 8    # relative humidity (%)
COL_IR     = 12   # horizontal infrared radiation intensity (Wh/m²)
COL_GHI    = 13   # global horizontal radiation (Wh/m²)
COL_DNI    = 14   # direct normal radiation (Wh/m²)
COL_DHI    = 15   # diffuse horizontal radiation (Wh/m²)

# ---------------------------------------------------------------------------
# CMIP6 monthly temperature deltas ΔT (°C) per scenario
# Indices: month 1=Jan … 12=Dec
#
# Source: IPCC AR6 Interactive Atlas, East Asia, ~28°N 113°E,
#         CMIP6 multi-model median.
#         Seasonal pattern: stronger winter warming (higher latitude advection),
#         weaker summer warming (monsoon buffering).
# ---------------------------------------------------------------------------
DELTA_T = {
    #              Jan   Feb   Mar   Apr   May   Jun   Jul   Aug   Sep   Oct   Nov   Dec
    "2050_SSP245": [1.9,  1.8,  1.7,  1.6,  1.5,  1.5,  1.6,  1.7,  1.7,  1.8,  1.9,  2.0],
    "2050_SSP585": [2.4,  2.3,  2.1,  2.0,  1.9,  1.9,  2.0,  2.1,  2.1,  2.2,  2.3,  2.5],
    "2080_SSP245": [2.6,  2.5,  2.3,  2.2,  2.1,  2.0,  2.1,  2.2,  2.3,  2.4,  2.5,  2.7],
    "2080_SSP585": [4.5,  4.3,  4.0,  3.8,  3.6,  3.5,  3.7,  3.8,  4.0,  4.2,  4.4,  4.7],
}

# ---------------------------------------------------------------------------
# Monthly GHI scaling factors α (fraction, 1.0 = no change)
#
# Source: CMIP6 ensemble mean for SW radiation at surface, East China.
#         Small increases in winter/autumn (reduced aerosol optical depth
#         under SSP scenarios), slight decrease in summer (enhanced convection
#         and cloud cover under monsoon intensification).
# ---------------------------------------------------------------------------
ALPHA_RAD = {
    #              Jan    Feb    Mar    Apr    May    Jun    Jul    Aug    Sep    Oct    Nov    Dec
    "2050_SSP245": [1.010, 1.008, 1.005, 1.002, 1.000, 0.997, 0.995, 0.997, 1.003, 1.008, 1.010, 1.012],
    "2050_SSP585": [1.015, 1.012, 1.008, 1.003, 1.000, 0.995, 0.992, 0.994, 1.004, 1.010, 1.014, 1.017],
    "2080_SSP245": [1.012, 1.010, 1.007, 1.003, 1.000, 0.996, 0.993, 0.995, 1.004, 1.010, 1.012, 1.015],
    "2080_SSP585": [1.022, 1.018, 1.013, 1.005, 1.000, 0.990, 0.985, 0.989, 1.007, 1.018, 1.022, 1.026],
}

# Fraction of ΔT applied to dew-point temperature (humidity buffering,
# typical for humid-subtropical climate; Donat et al. 2014)
DEW_POINT_FRAC = 0.6


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def sat_vapour_pressure(T_degC: float) -> float:
    """
    Saturation vapour pressure (hPa) using the Magnus formula.
    Valid for -40°C to +60°C.
    """
    return 6.112 * math.exp(17.67 * T_degC / (T_degC + 243.5))


def calc_rh(T_drybulb: float, T_dewpoint: float) -> float:
    """
    Relative humidity (%) from dry-bulb and dew-point temperatures.
    Returns value clamped to [5, 100].
    """
    if T_dewpoint > T_drybulb:
        T_dewpoint = T_drybulb       # physical constraint
    e_s = sat_vapour_pressure(T_drybulb)
    e   = sat_vapour_pressure(T_dewpoint)
    rh  = 100.0 * e / e_s
    return max(5.0, min(100.0, rh))


def ir_correction(ir_baseline: float,
                   T_new_C: float, T_old_C: float) -> float:
    """
    Correct horizontal IR radiation for new temperature via Stefan-Boltzmann
    scaling: IR ∝ T⁴.  Only applied when baseline IR > 0.
    """
    if ir_baseline <= 0:
        return ir_baseline
    T_new_K = T_new_C + 273.15
    T_old_K = T_old_C + 273.15
    if T_old_K <= 0:
        return ir_baseline
    return ir_baseline * (T_new_K / T_old_K) ** 4


# ---------------------------------------------------------------------------
# Core morphing function
# ---------------------------------------------------------------------------

def morph_epw(baseline_lines: list[str],
              scenario_key: str) -> list[str]:
    """
    Apply the Belcher morphing operators to the 8760 data lines of a baseline
    EPW file and return the modified lines (including the header unchanged).

    Parameters
    ----------
    baseline_lines : list[str]
        All lines of the baseline EPW (header + data), without trailing \\n.
    scenario_key : str
        One of "2050_SSP245", "2050_SSP585", "2080_SSP245", "2080_SSP585".

    Returns
    -------
    list[str] — morphed EPW lines (same length as input).
    """
    dT    = DELTA_T[scenario_key]     # list of 12 monthly ΔT values
    alpha = ALPHA_RAD[scenario_key]   # list of 12 monthly α values

    morphed_lines = list(baseline_lines[:N_HEADER])   # copy header verbatim

    for line in baseline_lines[N_HEADER:]:
        parts = line.split(",")
        if len(parts) < 20:
            morphed_lines.append(line)
            continue

        month = int(parts[COL_MONTH]) - 1    # 0-indexed (Jan=0)

        # --- Temperature ---
        T_old  = float(parts[COL_TDB])
        Td_old = float(parts[COL_TDP])
        dt     = dT[month]

        T_new  = T_old  + dt
        Td_new = Td_old + DEW_POINT_FRAC * dt

        # --- Relative humidity (recalculated) ---
        rh_new = calc_rh(T_new, Td_new)

        # --- Radiation ---
        a = alpha[month]
        ghi_old = float(parts[COL_GHI])
        dni_old = float(parts[COL_DNI])
        dhi_old = float(parts[COL_DHI])

        # Only scale non-zero radiation values (nighttime hours stay 0)
        ghi_new = max(0.0, round(ghi_old * a, 1)) if ghi_old > 0 else 0.0
        dni_new = max(0.0, round(dni_old * a, 1)) if dni_old > 0 else 0.0
        dhi_new = max(0.0, round(dhi_old * a, 1)) if dhi_old > 0 else 0.0

        # --- Horizontal IR radiation (Stefan-Boltzmann T⁴ correction) ---
        ir_old  = float(parts[COL_IR])
        ir_new  = ir_correction(ir_old, T_new, T_old)

        # --- Write modified fields back ---
        parts[COL_TDB] = f"{T_new:.2f}"
        parts[COL_TDP] = f"{Td_new:.2f}"
        parts[COL_RH]  = f"{rh_new:.0f}"
        parts[COL_IR]  = f"{ir_new:.1f}"
        parts[COL_GHI] = f"{ghi_new:.1f}"
        parts[COL_DNI] = f"{dni_new:.1f}"
        parts[COL_DHI] = f"{dhi_new:.1f}"

        morphed_lines.append(",".join(parts))

    return morphed_lines


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def read_epw_raw(path: str) -> list[str]:
    """Read EPW file, strip line endings, return list of strings."""
    with open(path, encoding="latin-1", newline="") as f:
        lines = [ln.rstrip("\r\n") for ln in f]
    # Drop trailing empty lines but keep exactly N_HEADER + N_DATA lines
    while lines and not lines[-1].strip():
        lines.pop()
    if len(lines) != N_HEADER + N_DATA:
        log.warning(f"  Expected {N_HEADER + N_DATA} lines, got {len(lines)}")
    return lines


def write_epw(lines: list[str], out_path: str, scenario_key: str) -> None:
    """Write morphed EPW file, updating the COMMENTS 1 header line."""
    year_tag = scenario_key[:4]
    ssp_tag  = scenario_key[5:]   # e.g. "SSP245"

    modified = list(lines)
    # Update COMMENTS 1 (line index 6, 0-based) to document morphing
    for i, ln in enumerate(modified[:N_HEADER]):
        if ln.startswith("COMMENTS 1"):
            original = ln.split(",", 1)[-1].strip().strip('"')
            modified[i] = (
                f'COMMENTS 1,"Morphed for {year_tag} {ssp_tag} '
                f'(Belcher 2005 method, CMIP6 multi-model median). '
                f'Baseline: {original}"'
            )
            break

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="latin-1", newline="\n") as f:
        f.write("\n".join(modified) + "\n")


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def generate_all_future_epw(
        baseline_path: str = BASELINE_EPW,
        out_dir: str = DATA_CLIMATE,
) -> dict[str, str]:
    """
    Generate the four future EPW files and return a dict
    {scenario_key → output_path}.
    """
    if not os.path.isfile(baseline_path):
        log.error(f"Baseline EPW not found: {baseline_path}")
        return {}

    log.info(f"Reading baseline EPW: {baseline_path}")
    baseline_lines = read_epw_raw(baseline_path)
    log.info(f"  {len(baseline_lines)} lines read "
             f"({N_HEADER} header + {len(baseline_lines)-N_HEADER} data)")

    outputs = {}
    for scen in ["2050_SSP245", "2050_SSP585", "2080_SSP245", "2080_SSP585"]:
        out_path = os.path.join(out_dir, f"Changsha_{scen}.epw")
        log.info(f"\n[{scen}]  ΔT_annual={sum(DELTA_T[scen])/12:.2f}°C  "
                 f"α_mean={sum(ALPHA_RAD[scen])/12:.4f}")
        log.info(f"  ΔT monthly (Jan→Dec): "
                 + "  ".join(f"{d:+.1f}" for d in DELTA_T[scen]))

        morphed = morph_epw(baseline_lines, scen)
        write_epw(morphed, out_path, scen)

        # Quick sanity check: mean July dry-bulb temperature
        july_lines  = [l for l in morphed[N_HEADER:]
                       if l.split(",")[COL_MONTH] == "7"]
        july_T      = [float(l.split(",")[COL_TDB]) for l in july_lines
                       if len(l.split(",")) > COL_TDB]
        base_july   = [l for l in baseline_lines[N_HEADER:]
                       if l.split(",")[COL_MONTH] == "7"]
        base_july_T = [float(l.split(",")[COL_TDB]) for l in base_july
                       if len(l.split(",")) > COL_TDB]
        if july_T and base_july_T:
            log.info(f"  July mean Tdb: baseline={np.mean(base_july_T):.1f}°C → "
                     f"future={np.mean(july_T):.1f}°C "
                     f"(Δ={np.mean(july_T)-np.mean(base_july_T):+.2f}°C, "
                     f"expected {DELTA_T[scen][6]:+.1f}°C)")

        outputs[scen] = out_path
        log.info(f"  Saved: {out_path}")

    return outputs


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Morph Changsha TMYx EPW to CMIP6 future climate scenarios"
    )
    parser.add_argument("--list", action="store_true",
                        help="Print ΔT tables and exit without writing files")
    args = parser.parse_args()

    if args.list:
        print("\nCMIP6 monthly ΔT (°C) for Changsha (~28°N, 113°E):\n")
        header = f"{'Scenario':<15}" + "".join(f"  {m:>3}" for m in
                                                 ["Jan","Feb","Mar","Apr","May",
                                                  "Jun","Jul","Aug","Sep","Oct",
                                                  "Nov","Dec"]) + "  Annual"
        print(header)
        print("-" * len(header))
        for scen, deltas in DELTA_T.items():
            row = f"{scen:<15}" + "".join(f"  {d:+4.1f}" for d in deltas)
            row += f"  {sum(deltas)/12:+4.2f}"
            print(row)
        return

    outputs = generate_all_future_epw()
    if outputs:
        log.info(f"\nGenerated {len(outputs)} future EPW files in {DATA_CLIMATE}")
        log.info("Files ready for EnergyPlus climate change scenario runs.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
