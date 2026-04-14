"""
run_baseline.py
===============
Run EnergyPlus baseline simulations for the three Changsha residential
building archetypes and extract key annual energy performance metrics.

Usage:
    python run_baseline.py

Outputs:
    data/processed/baseline_results.csv
    figure/fig04_baseline_eui.png  (via plot_baseline.py)

Requires:
    - EnergyPlus 24.1+ on PATH  (or ENERGYPLUS_DIR env var)
    - Upgraded IDF files: data/models/changsha_era{1,2,3}_v26.idf
    - EPW:  data/climate/CHN_HN_Changsha.576870_TMYx.2007-2021.epw
"""

import os
import sys
import csv
import shutil
import subprocess
import tempfile
import logging
import importlib.util

import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
DATA_MODELS  = os.path.join(REPO_ROOT, "data", "models")
DATA_CLIMATE = os.path.join(REPO_ROOT, "data", "climate")
DATA_PROC    = os.path.join(REPO_ROOT, "data", "processed")
FIGURE_DIR   = os.path.join(REPO_ROOT, "figure")

EPW = os.path.join(
    DATA_CLIMATE,
    "CHN_HN_Changsha.576870_TMYx.2007-2021.epw",
)

ARCHETYPES = {
    "Era1_1980s_MidRise": {
        "idf": os.path.join(DATA_MODELS, "changsha_era1_v26.idf"),
        "era": 1,
        "label": "Era 1\n(~1980s)",
        "description": "MidRise, pre-code",
    },
    "Era2_2000s_MidRise": {
        "idf": os.path.join(DATA_MODELS, "changsha_era2_v26.idf"),
        "era": 2,
        "label": "Era 2\n(~2000s)",
        "description": "MidRise, partial insulation",
    },
    "Era3_2010s_HighRise": {
        "idf": os.path.join(DATA_MODELS, "changsha_era3_v26.idf"),
        "era": 3,
        "label": "Era 3\n(~2010s+)",
        "description": "HighRise, JGJ 134-2010",
    },
}


# ---------------------------------------------------------------------------
# EnergyPlus runner
# ---------------------------------------------------------------------------

def find_energyplus():
    """Return path to the energyplus executable."""
    # Check PATH first
    ep = shutil.which("energyplus")
    if ep:
        return ep
    # Check ENERGYPLUS_DIR env var
    ep_dir = os.environ.get("ENERGYPLUS_DIR", "")
    if ep_dir:
        ep = os.path.join(ep_dir, "energyplus")
        if os.path.isfile(ep):
            return ep
    # macOS common install locations
    for candidate in [
        "/Applications/EnergyPlus-26-1-0/energyplus",
        "/Applications/EnergyPlus-24-1-0/energyplus",
        "/usr/local/EnergyPlus/energyplus",
    ]:
        if os.path.isfile(candidate):
            return candidate
    return None


def run_energyplus(idf_path, epw_path, output_dir, ep_exe):
    """
    Run a single EnergyPlus simulation.

    Returns True on success, False on failure.
    """
    os.makedirs(output_dir, exist_ok=True)
    cmd = [ep_exe, "-w", epw_path, "-d", output_dir, idf_path]
    log.info(f"  CMD: {' '.join(os.path.basename(c) for c in cmd)}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode != 0:
        log.error(f"  EnergyPlus failed (rc={result.returncode})")
        err_file = os.path.join(output_dir, "eplusout.err")
        if os.path.isfile(err_file):
            with open(err_file) as f:
                errs = [l for l in f if "** Severe" in l or "** Fatal" in l]
            for e in errs[:5]:
                log.error(f"    {e.strip()}")
        return False

    # Confirm success line in end file
    end_file = os.path.join(output_dir, "eplusout.end")
    if os.path.isfile(end_file):
        with open(end_file) as f:
            end_text = f.read()
        if "EnergyPlus Completed Successfully" in end_text:
            return True
        log.error(f"  EnergyPlus end file does not confirm success: {end_text[:200]}")
        return False

    return True


# ---------------------------------------------------------------------------
# Output parsing
# ---------------------------------------------------------------------------

def parse_tbl_csv(tbl_csv_path):
    """
    Parse eplustbl.csv to extract:
      - floor_area_m2        : total conditioned floor area
      - heating_gj           : annual heating energy (Natural Gas + District Heating)
      - cooling_gj           : annual cooling energy (Electricity cooling)
      - total_site_gj        : total site energy
      - eui_mj_m2            : site EUI (MJ/m²)
      - lighting_gj          : interior lighting electricity
      - equipment_gj         : interior equipment electricity

    Returns a dict.
    """
    results = {}

    with open(tbl_csv_path, encoding="latin-1", newline="") as f:
        lines = f.readlines()

    # Helper: find a line starting with a given tag
    def find_line(tag, start=0):
        for i in range(start, len(lines)):
            if lines[i].strip().startswith(tag):
                return i, lines[i]
        return -1, None

    # --- Total site energy and floor area ---
    idx, line = find_line(",Total Site Energy,")
    if idx == -1:
        idx, line = find_line("Total Site Energy,")
    if line:
        parts = [p.strip() for p in line.split(",")]
        # Format: [prefix, "Total Site Energy", total_GJ, per_total_MJ_m2, per_cond_MJ_m2]
        try:
            total_gj = float(parts[-3])
            eui_per_total = float(parts[-2])   # MJ/m² per total building area
            eui_per_cond  = float(parts[-1])   # MJ/m² per conditioned area
            results["total_site_gj"] = total_gj
            results["eui_mj_m2"] = eui_per_total       # use total building area
            results["floor_area_m2"] = (
                total_gj * 1000.0 / eui_per_total if eui_per_total > 0 else 0.0
            )
        except (ValueError, IndexError):
            log.warning("  Could not parse site energy totals")

    # --- End uses table ---
    # Find the first "End Uses" section (not "End Uses By Subcategory")
    end_uses_idx = -1
    for i, line in enumerate(lines):
        s = line.strip()
        if s == "End Uses" or s.endswith(",End Uses"):
            end_uses_idx = i
            break

    if end_uses_idx == -1:
        log.warning("  End Uses section not found in CSV")
    else:
        # Column order: Electricity, NatGas, Gasoline, Diesel, Coal, FOil1, FOil2,
        #               Propane, OtherFuel1, OtherFuel2, DistCooling, DistHeatWater,
        #               DistHeatSteam, Water
        ELEC_COL   = 1   # 0-indexed after row label
        NATGAS_COL = 2
        DIST_COOL  = 10
        DIST_HEAT_W = 11
        DIST_HEAT_S = 12

        def parse_end_use_row(row_label, start):
            for i in range(start, min(start + 25, len(lines))):
                s = lines[i].strip()
                if s.startswith(f",{row_label},") or s.startswith(f"{row_label},"):
                    parts = [p.strip() for p in s.split(",")]
                    # Strip leading empty element if present
                    if parts and parts[0] == "":
                        parts = parts[1:]
                    try:
                        return [float(p) if p else 0.0 for p in parts[1:]]
                    except ValueError:
                        return []
            return []

        heating_cols = parse_end_use_row("Heating", end_uses_idx)
        cooling_cols = parse_end_use_row("Cooling", end_uses_idx)
        lighting_cols = parse_end_use_row("Interior Lighting", end_uses_idx)
        equipment_cols = parse_end_use_row("Interior Equipment", end_uses_idx)
        fans_cols = parse_end_use_row("Fans", end_uses_idx)

        def safe_get(lst, idx, default=0.0):
            try:
                return float(lst[idx]) if lst else default
            except (IndexError, ValueError):
                return default

        # Heating = NatGas heating + District Heating Water/Steam (all in GJ)
        results["heating_gj"] = (
            safe_get(heating_cols, NATGAS_COL - 1)
            + safe_get(heating_cols, DIST_HEAT_W - 1)
            + safe_get(heating_cols, DIST_HEAT_S - 1)
        )
        # Cooling = Electricity cooling + District Cooling
        results["cooling_gj"] = (
            safe_get(cooling_cols, ELEC_COL - 1)
            + safe_get(cooling_cols, DIST_COOL - 1)
        )
        results["lighting_gj"] = safe_get(lighting_cols, ELEC_COL - 1)
        results["equipment_gj"] = safe_get(equipment_cols, ELEC_COL - 1)
        results["fans_gj"] = safe_get(fans_cols, ELEC_COL - 1)

    return results


def parse_peak_loads(tbl_csv_path, floor_area_m2):
    """
    Parse peak zone design loads from eplustbl.csv HVAC Sizing Summary.
    Returns peak_heating_w_m2 and peak_cooling_w_m2.
    """
    peak_heat_w = 0.0
    peak_cool_w = 0.0

    try:
        with open(tbl_csv_path, encoding="latin-1", newline="") as f:
            lines = f.readlines()

        # Find the zone sizing section (not HVAC system sizing)
        # Look for lines with "User Design Capacity [W]"
        for i, line in enumerate(lines):
            parts = [p.strip() for p in line.split(",")]
            # Air Terminal / Zone equipment sizing rows have a Load Type column
            if len(parts) >= 6 and "User Design Capacity [W]" in line:
                # Read subsequent data rows
                for j in range(i + 1, min(i + 300, len(lines))):
                    data = [p.strip() for p in lines[j].split(",")]
                    if len(data) < 5:
                        continue
                    # Look for heating/cooling load type
                    load_type = data[2].lower() if len(data) > 2 else ""
                    capacity_str = data[4] if len(data) > 4 else "0"
                    try:
                        cap = float(capacity_str)
                    except ValueError:
                        continue
                    if "heat" in load_type:
                        peak_heat_w += cap
                    elif "cool" in load_type:
                        peak_cool_w += cap
                break
    except Exception as e:
        log.warning(f"  Peak load parsing error: {e}")

    if floor_area_m2 and floor_area_m2 > 0:
        return peak_heat_w / floor_area_m2, peak_cool_w / floor_area_m2
    return 0.0, 0.0


def gj_to_kwh_m2(gj, floor_area_m2):
    """Convert GJ total energy to kWh/m².
    1 GJ = 1e9 J; 1 kWh = 3.6e6 J  →  1 GJ = 277.778 kWh
    """
    if not floor_area_m2 or floor_area_m2 <= 0:
        return 0.0
    return gj * 1e9 / 3.6e6 / floor_area_m2  # GJ → kWh, per m²


def extract_results(output_dir):
    """
    Extract energy metrics from one EnergyPlus output directory.
    Returns dict with kWh/m² values.
    """
    tbl_csv = os.path.join(output_dir, "eplustbl.csv")
    if not os.path.isfile(tbl_csv):
        log.error(f"  Missing eplustbl.csv in {output_dir}")
        return None

    raw = parse_tbl_csv(tbl_csv)
    fa = raw.get("floor_area_m2", 0)

    heating_kwh  = gj_to_kwh_m2(raw.get("heating_gj", 0), fa)
    cooling_kwh  = gj_to_kwh_m2(raw.get("cooling_gj", 0), fa)
    lighting_kwh = gj_to_kwh_m2(raw.get("lighting_gj", 0), fa)
    equipment_kwh= gj_to_kwh_m2(raw.get("equipment_gj", 0), fa)
    fans_kwh     = gj_to_kwh_m2(raw.get("fans_gj", 0), fa)
    eui_kwh      = raw.get("eui_mj_m2", 0) / 3.6   # MJ/m² → kWh/m²

    peak_heat_w_m2, peak_cool_w_m2 = parse_peak_loads(tbl_csv, fa)

    return {
        "floor_area_m2":        round(fa, 1),
        "heating_kwh_m2":       round(heating_kwh, 2),
        "cooling_kwh_m2":       round(cooling_kwh, 2),
        "lighting_kwh_m2":      round(lighting_kwh, 2),
        "equipment_kwh_m2":     round(equipment_kwh, 2),
        "fans_kwh_m2":          round(fans_kwh, 2),
        "other_kwh_m2":         round(
            max(0, eui_kwh - heating_kwh - cooling_kwh), 2
        ),
        "total_eui_kwh_m2":     round(eui_kwh, 2),
        "peak_heating_w_m2":    round(peak_heat_w_m2, 2),
        "peak_cooling_w_m2":    round(peak_cool_w_m2, 2),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ep_exe = find_energyplus()
    if ep_exe is None:
        log.error(
            "EnergyPlus executable not found. "
            "Install EnergyPlus (https://energyplus.net) and add it to PATH, "
            "or set the ENERGYPLUS_DIR environment variable."
        )
        sys.exit(1)
    log.info(f"EnergyPlus: {ep_exe}")

    if not os.path.isfile(EPW):
        log.error(f"EPW not found: {EPW}")
        sys.exit(1)

    os.makedirs(DATA_PROC, exist_ok=True)
    os.makedirs(FIGURE_DIR, exist_ok=True)

    results_sim_dir = os.path.join(REPO_ROOT, "data", "simulation")
    os.makedirs(results_sim_dir, exist_ok=True)

    rows = []
    for name, meta in ARCHETYPES.items():
        idf = meta["idf"]
        if not os.path.isfile(idf):
            log.error(f"IDF not found: {idf}  (run adapt_envelope.py + version upgrade first)")
            continue

        out_dir = os.path.join(results_sim_dir, name)
        log.info(f"\n=== Simulating {name} ===")
        log.info(f"  IDF: {os.path.basename(idf)}")

        ok = run_energyplus(idf, EPW, out_dir, ep_exe)
        if not ok:
            log.error(f"  Simulation failed for {name} — skipping")
            continue

        log.info(f"  Simulation complete. Parsing results...")
        metrics = extract_results(out_dir)
        if metrics is None:
            continue

        row = {
            "archetype":    name,
            "era":          meta["era"],
            "label":        meta["label"].replace("\n", " "),
            "description":  meta["description"],
        }
        row.update(metrics)
        rows.append(row)

        log.info(
            f"  EUI={metrics['total_eui_kwh_m2']:.1f} kWh/m²  "
            f"(heating={metrics['heating_kwh_m2']:.1f}, "
            f"cooling={metrics['cooling_kwh_m2']:.1f})"
        )

    if not rows:
        log.error("No successful simulations — no results to save.")
        sys.exit(1)

    df = pd.DataFrame(rows).sort_values("era")
    out_csv = os.path.join(DATA_PROC, "baseline_results.csv")
    df.to_csv(out_csv, index=False, float_format="%.2f")
    log.info(f"\nSaved baseline results → {out_csv}")

    # Print summary table
    log.info("\n--- Baseline Energy Summary ---")
    log.info(f"{'Archetype':<30} {'EUI':>8} {'Heat':>8} {'Cool':>8} {'Other':>8}  kWh/m²")
    log.info("-" * 70)
    for _, r in df.iterrows():
        log.info(
            f"{r['archetype']:<30} "
            f"{r['total_eui_kwh_m2']:>8.1f} "
            f"{r['heating_kwh_m2']:>8.1f} "
            f"{r['cooling_kwh_m2']:>8.1f} "
            f"{r['other_kwh_m2']:>8.1f}"
        )

    # Generate figure via plot_baseline.py
    plot_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "postprocessing", "plot_baseline.py",
    )
    if os.path.isfile(plot_script):
        log.info("\nGenerating figures via plot_baseline.py ...")
        spec = importlib.util.spec_from_file_location("plot_baseline", plot_script)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.plot_baseline_eui(df, os.path.join(FIGURE_DIR, "fig04_baseline_eui.png"))
    else:
        log.warning(f"plot_baseline.py not found at {plot_script}")


if __name__ == "__main__":
    main()
