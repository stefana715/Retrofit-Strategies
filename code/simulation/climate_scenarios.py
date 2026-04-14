"""
climate_scenarios.py
====================
Run EnergyPlus for all climate change scenarios.

Matrix: 3 eras × 2 envelope conditions × 5 climate files = 30 simulations

    Eras:        Era1_1980s_MidRise, Era2_2000s_MidRise, Era3_2010s_HighRise
    Envelopes:   Baseline (no retrofit), R5_Combined (all measures)
    Climates:    Current (TMYx 2007-2021),
                 2050_SSP245, 2050_SSP585, 2080_SSP245, 2080_SSP585

IDF files used (already prepared by previous steps):
    Baseline : data/models/changsha_era{1,2,3}_v26.idf
    R5       : data/models/retrofit_{1,2,3}_R5_Combined.idf

EPW files:
    Current  : data/climate/CHN_HN_Changsha.576870_TMYx.2007-2021.epw
    Future   : data/climate/Changsha_{scenario}.epw

Produces:
    data/processed/climate_results.csv

Usage:
    python climate_scenarios.py
"""

import os
import sys
import subprocess
import shutil
import logging

import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_MODELS  = os.path.join(REPO_ROOT, "data", "models")
DATA_CLIMATE = os.path.join(REPO_ROOT, "data", "climate")
DATA_SIM     = os.path.join(REPO_ROOT, "data", "simulation")
DATA_PROC    = os.path.join(REPO_ROOT, "data", "processed")

# ---------------------------------------------------------------------------
# Simulation matrix
# ---------------------------------------------------------------------------
ARCHETYPES = [
    {
        "key":       "Era1_1980s_MidRise",
        "era":       1,
        "era_label": "Era 1 (~1980s)",
        "baseline_idf": os.path.join(DATA_MODELS, "changsha_era1_v26.idf"),
        "r5_idf":       os.path.join(DATA_MODELS, "retrofit_1_R5_Combined.idf"),
    },
    {
        "key":       "Era2_2000s_MidRise",
        "era":       2,
        "era_label": "Era 2 (~2000s)",
        "baseline_idf": os.path.join(DATA_MODELS, "changsha_era2_v26.idf"),
        "r5_idf":       os.path.join(DATA_MODELS, "retrofit_2_R5_Combined.idf"),
    },
    {
        "key":       "Era3_2010s_HighRise",
        "era":       3,
        "era_label": "Era 3 (~2010s+)",
        "baseline_idf": os.path.join(DATA_MODELS, "changsha_era3_v26.idf"),
        "r5_idf":       os.path.join(DATA_MODELS, "retrofit_3_R5_Combined.idf"),
    },
]

CLIMATE_SCENARIOS = [
    {
        "key":    "Current",
        "label":  "Current\n(TMYx)",
        "year":   2013,
        "ssp":    "—",
        "epw":    os.path.join(DATA_CLIMATE,
                               "CHN_HN_Changsha.576870_TMYx.2007-2021.epw"),
    },
    {
        "key":    "2050_SSP245",
        "label":  "2050\nSSP2-4.5",
        "year":   2050,
        "ssp":    "SSP2-4.5",
        "epw":    os.path.join(DATA_CLIMATE, "Changsha_2050_SSP245.epw"),
    },
    {
        "key":    "2050_SSP585",
        "label":  "2050\nSSP5-8.5",
        "year":   2050,
        "ssp":    "SSP5-8.5",
        "epw":    os.path.join(DATA_CLIMATE, "Changsha_2050_SSP585.epw"),
    },
    {
        "key":    "2080_SSP245",
        "label":  "2080\nSSP2-4.5",
        "year":   2080,
        "ssp":    "SSP2-4.5",
        "epw":    os.path.join(DATA_CLIMATE, "Changsha_2080_SSP245.epw"),
    },
    {
        "key":    "2080_SSP585",
        "label":  "2080\nSSP5-8.5",
        "year":   2080,
        "ssp":    "SSP5-8.5",
        "epw":    os.path.join(DATA_CLIMATE, "Changsha_2080_SSP585.epw"),
    },
]

RETROFITS = [
    {"key": "Baseline",    "idf_field": "baseline_idf", "label": "Baseline"},
    {"key": "R5_Combined", "idf_field": "r5_idf",       "label": "R5 Combined"},
]


# ---------------------------------------------------------------------------
# EnergyPlus helpers  (mirrors retrofit_scenarios.py)
# ---------------------------------------------------------------------------

def find_energyplus():
    ep = shutil.which("energyplus")
    if ep:
        return ep
    for p in [
        os.path.join(os.environ.get("ENERGYPLUS_DIR", ""), "energyplus"),
        "/Applications/EnergyPlus-26-1-0/energyplus",
        "/Applications/EnergyPlus-24-1-0/energyplus",
    ]:
        if p and os.path.isfile(p):
            return p
    return None


def run_energyplus(idf_path, epw_path, output_dir, ep_exe, timeout=600):
    """Run EnergyPlus. Returns True on success."""
    os.makedirs(output_dir, exist_ok=True)
    cmd = [ep_exe, "-w", epw_path, "-d", output_dir, idf_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=timeout)
    except subprocess.TimeoutExpired:
        log.error("  EnergyPlus timed out")
        return False
    if result.returncode != 0:
        err_file = os.path.join(output_dir, "eplusout.err")
        if os.path.isfile(err_file):
            with open(err_file) as f:
                for ln in f:
                    if "** Severe" in ln or "** Fatal" in ln:
                        log.error(f"  EP error: {ln.strip()[:120]}")
                        break
        return False
    return True


def parse_tbl_csv(tbl_csv_path):
    """Parse eplustbl.csv → dict with energy metrics."""
    results = {}
    with open(tbl_csv_path, encoding="latin-1") as f:
        lines = f.readlines()

    def find_line(tag, start=0):
        for i in range(start, len(lines)):
            if lines[i].strip().startswith(tag) or f",{tag}," in lines[i]:
                return i, lines[i]
        return -1, None

    idx, line = find_line("Total Site Energy,")
    if idx == -1:
        idx, line = find_line(",Total Site Energy,")
    if line:
        parts = [p.strip() for p in line.split(",")]
        try:
            total_gj      = float(parts[-3])
            eui_mj_m2     = float(parts[-2])
            results["total_site_gj"] = total_gj
            results["eui_mj_m2"]     = eui_mj_m2
            results["floor_area_m2"] = (
                total_gj * 1000.0 / eui_mj_m2 if eui_mj_m2 > 0 else 0.0
            )
        except (ValueError, IndexError):
            pass

    end_uses_idx = -1
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s == "End Uses" or s.endswith(",End Uses"):
            end_uses_idx = i
            break

    if end_uses_idx != -1:
        ELEC_COL    = 1
        NATGAS_COL  = 2

        def parse_row(label, start):
            for i in range(start, min(start + 25, len(lines))):
                s = lines[i].strip()
                if s.startswith(f",{label},") or s.startswith(f"{label},"):
                    parts = [p.strip() for p in s.split(",")]
                    if parts and parts[0] == "":
                        parts = parts[1:]
                    try:
                        return [float(p) if p else 0.0 for p in parts[1:]]
                    except ValueError:
                        return []
            return []

        def sg(lst, idx):
            try:
                return float(lst[idx]) if lst else 0.0
            except (IndexError, ValueError):
                return 0.0

        heat = parse_row("Heating",            end_uses_idx)
        cool = parse_row("Cooling",            end_uses_idx)
        ltg  = parse_row("Interior Lighting",  end_uses_idx)
        eqp  = parse_row("Interior Equipment", end_uses_idx)
        fans = parse_row("Fans",               end_uses_idx)

        results["heating_gj"]  = sg(heat, NATGAS_COL - 1) + sg(heat, 10) + sg(heat, 11)
        results["cooling_gj"]  = sg(cool, ELEC_COL - 1)   + sg(cool, 9)
        results["lighting_gj"] = sg(ltg,  ELEC_COL - 1)
        results["equipment_gj"]= sg(eqp,  ELEC_COL - 1)
        results["fans_gj"]     = sg(fans, ELEC_COL - 1)

    return results


def gj_to_kwh_m2(gj, fa):
    if not fa or fa <= 0:
        return 0.0
    return gj * 1e9 / 3.6e6 / fa


def extract_eui(output_dir):
    tbl = os.path.join(output_dir, "eplustbl.csv")
    if not os.path.isfile(tbl):
        return None
    raw = parse_tbl_csv(tbl)
    fa  = raw.get("floor_area_m2", 0)
    if not fa:
        return None
    return {
        "floor_area_m2":    round(fa, 1),
        "heating_kwh_m2":   round(gj_to_kwh_m2(raw.get("heating_gj", 0), fa), 2),
        "cooling_kwh_m2":   round(gj_to_kwh_m2(raw.get("cooling_gj", 0), fa), 2),
        "total_eui_kwh_m2": round(raw.get("eui_mj_m2", 0) / 3.6, 2),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ep_exe = find_energyplus()
    if not ep_exe:
        log.error("EnergyPlus not found. Install or set ENERGYPLUS_DIR.")
        sys.exit(1)
    log.info(f"EnergyPlus: {ep_exe}")

    # Validate all input files exist
    missing = []
    for arch in ARCHETYPES:
        for ret in RETROFITS:
            idf = arch[ret["idf_field"]]
            if not os.path.isfile(idf):
                missing.append(idf)
    for clim in CLIMATE_SCENARIOS:
        if not os.path.isfile(clim["epw"]):
            missing.append(clim["epw"])
    if missing:
        for p in missing:
            log.error(f"Missing: {p}")
        sys.exit(1)

    os.makedirs(DATA_PROC, exist_ok=True)

    total_runs = len(ARCHETYPES) * len(RETROFITS) * len(CLIMATE_SCENARIOS)
    run_num    = 0
    rows       = []

    for arch in ARCHETYPES:
        for ret in RETROFITS:
            idf_path = arch[ret["idf_field"]]

            for clim in CLIMATE_SCENARIOS:
                run_num += 1
                tag = f"{arch['key']}_{ret['key']}_{clim['key']}"
                out_dir = os.path.join(DATA_SIM, f"climate_{tag}")

                log.info(f"\n[{run_num}/{total_runs}] "
                         f"{arch['era_label']} | {ret['label']} | {clim['label'].replace(chr(10),' ')}")

                # Check for existing valid output
                tbl_path = os.path.join(out_dir, "eplustbl.csv")
                if os.path.isfile(tbl_path):
                    eui = extract_eui(out_dir)
                    if eui:
                        log.info(f"  Using cached result — EUI={eui['total_eui_kwh_m2']} kWh/m²")
                    else:
                        eui = None
                else:
                    eui = None

                if eui is None:
                    ok = run_energyplus(idf_path, clim["epw"], out_dir, ep_exe)
                    if not ok:
                        log.error(f"  Simulation FAILED — skipping")
                        continue
                    eui = extract_eui(out_dir)
                    if eui is None:
                        log.error(f"  Could not parse EUI — skipping")
                        continue

                log.info(f"  Total EUI : {eui['total_eui_kwh_m2']} kWh/m²")
                log.info(f"  Heating   : {eui['heating_kwh_m2']}   "
                         f"Cooling: {eui['cooling_kwh_m2']} kWh/m²")

                rows.append({
                    "archetype":          arch["key"],
                    "era":                arch["era"],
                    "era_label":          arch["era_label"],
                    "retrofit":           ret["key"],
                    "retrofit_label":     ret["label"],
                    "climate":            clim["key"],
                    "climate_label":      clim["label"].replace("\n", " "),
                    "year":               clim["year"],
                    "ssp":                clim["ssp"],
                    "heating_kwh_m2":     eui["heating_kwh_m2"],
                    "cooling_kwh_m2":     eui["cooling_kwh_m2"],
                    "total_eui_kwh_m2":   eui["total_eui_kwh_m2"],
                    "floor_area_m2":      eui["floor_area_m2"],
                })

    df = pd.DataFrame(rows)
    out_csv = os.path.join(DATA_PROC, "climate_results.csv")
    df.to_csv(out_csv, index=False)
    log.info(f"\nSaved {len(df)} rows → {out_csv}")

    # Summary pivot
    log.info("\n--- Total EUI (kWh/m²) by scenario and retrofit ---")
    for arch in ARCHETYPES:
        sub = df[df["archetype"] == arch["key"]]
        if sub.empty:
            continue
        piv = sub.pivot_table(
            index="climate", columns="retrofit",
            values="total_eui_kwh_m2", aggfunc="first"
        )
        log.info(f"\n{arch['era_label']}:\n{piv.to_string()}")

    log.info("\nDone.")


if __name__ == "__main__":
    main()
