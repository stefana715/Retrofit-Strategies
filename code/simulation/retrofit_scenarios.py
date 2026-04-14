"""
retrofit_scenarios.py
=====================
Design and simulate five envelope retrofit measures for three Changsha
residential building archetypes (Era 1–3).

Retrofit measures:
    R1_Wall        — wall insulation upgrade (EPS to achieve U = 0.4 W/m²K)
    R2_Window      — window replacement (low-e double, U = 1.8 W/m²K, SHGC = 0.35)
    R3_Roof        — roof insulation (XPS to achieve U = 0.3 W/m²K)
    R4_Infiltration— envelope air-sealing (0.3 ACH)
    R5_Combined    — all four measures together

Each measure is applied to the era-specific v26 IDF (changsha_era{1,2,3}_v26.idf).
IDF modification uses text-based editing (same approach as morris_sa.py),
which is equivalent to eppy but version-agnostic.

Usage:
    python retrofit_scenarios.py

Outputs:
    data/processed/retrofit_results.csv
    figure/fig07_retrofit_savings.png   (via plot_retrofit.py)
    data/simulation/retrofit_*/         (per-scenario EnergyPlus output dirs)
"""

import os
import re
import sys
import math
import shutil
import logging
import tempfile
import subprocess
import importlib.util

import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT    = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_MODELS  = os.path.join(REPO_ROOT, "data", "models")
DATA_PROC    = os.path.join(REPO_ROOT, "data", "processed")
DATA_SIM     = os.path.join(REPO_ROOT, "data", "simulation")
FIGURE_DIR   = os.path.join(REPO_ROOT, "figure")
DATA_CLIMATE = os.path.join(REPO_ROOT, "data", "climate")

EPW = os.path.join(DATA_CLIMATE, "CHN_HN_Changsha.576870_TMYx.2007-2021.epw")

# ---------------------------------------------------------------------------
# Surface resistances (ISO 6946)
# ---------------------------------------------------------------------------
R_SI_WALL, R_SE_WALL = 0.13, 0.04
R_SI_ROOF, R_SE_ROOF = 0.10, 0.04


def u_to_nomass_r(u, r_si, r_se):
    return max(1.0 / u - r_si - r_se, 0.02)


# ---------------------------------------------------------------------------
# Retrofit measure definitions
# ---------------------------------------------------------------------------
RETROFIT_MEASURES = {
    "R1_Wall": {
        "label":       "Wall insulation\n(U=0.4 W/m²K)",
        "short":       "R1: Wall",
        "description": "EPS insulation board added externally to achieve U = 0.4 W/m²K",
        "wall_U":      0.4,
    },
    "R2_Window": {
        "label":        "Window replacement\n(U=1.8 W/m²K)",
        "short":        "R2: Window",
        "description":  "Low-e double glazing, U = 1.8 W/m²K, SHGC = 0.35",
        "window_U":     1.8,
        "window_SHGC":  0.35,
    },
    "R3_Roof": {
        "label":       "Roof insulation\n(U=0.3 W/m²K)",
        "short":       "R3: Roof",
        "description": "XPS insulation board on roof to achieve U = 0.3 W/m²K",
        "roof_U":      0.3,
    },
    "R4_Infiltration": {
        "label":        "Air sealing\n(0.3 ACH)",
        "short":        "R4: Air sealing",
        "description":  "Envelope air-sealing: reduce infiltration to 0.3 ACH",
        "infiltration": 0.3,
    },
    "R5_Combined": {
        "label":        "Combined\n(R1+R2+R3+R4)",
        "short":        "R5: Combined",
        "description":  "All four measures applied simultaneously",
        "wall_U":       0.4,
        "window_U":     1.8,
        "window_SHGC":  0.35,
        "roof_U":       0.3,
        "infiltration": 0.3,
    },
}

# ---------------------------------------------------------------------------
# Building archetypes (era baselines for reference)
# ---------------------------------------------------------------------------
ARCHETYPES = {
    "Era1_1980s_MidRise": {
        "era":          1,
        "idf":          os.path.join(DATA_MODELS, "changsha_era1_v26.idf"),
        "label":        "Era 1 (~1980s)",
        "description":  "MidRise, pre-code",
        "baseline_wall_U":      1.5,
        "baseline_roof_U":      1.2,
        "baseline_window_U":    5.8,
        "baseline_window_SHGC": 0.70,
        "baseline_infiltration": 1.5,
    },
    "Era2_2000s_MidRise": {
        "era":          2,
        "idf":          os.path.join(DATA_MODELS, "changsha_era2_v26.idf"),
        "label":        "Era 2 (~2000s)",
        "description":  "MidRise, partial insulation",
        "baseline_wall_U":      1.0,
        "baseline_roof_U":      0.8,
        "baseline_window_U":    3.5,
        "baseline_window_SHGC": 0.55,
        "baseline_infiltration": 1.0,
    },
    "Era3_2010s_HighRise": {
        "era":          3,
        "idf":          os.path.join(DATA_MODELS, "changsha_era3_v26.idf"),
        "label":        "Era 3 (~2010s+)",
        "description":  "HighRise, JGJ 134-2010",
        "baseline_wall_U":      0.6,
        "baseline_roof_U":      0.4,
        "baseline_window_U":    2.5,
        "baseline_window_SHGC": 0.40,
        "baseline_infiltration": 0.5,
    },
}


# ===========================================================================
# Text-based IDF modifier (SAIDF) — mirrors morris_sa.py implementation
# ===========================================================================

class SAIDF:
    """
    Minimal text-based IDF editor for retrofit parameter modifications.
    No IDD required; works reliably with EnergyPlus v22–v26 IDFs.
    """

    def __init__(self, path):
        with open(path, "r", encoding="latin-1") as f:
            self.text = f.read()

    def update_nomass_thermal_r(self, mat_name, r_val):
        """Update Thermal Resistance of a named Material:NoMass."""
        pat = re.compile(
            r"(?mi)"
            r"(^\s*Material:NoMass,\s*\n"
            r"\s*" + re.escape(mat_name) + r"[,;\s][^\n]*\n"
            r"\s*[^\n]+,\s*[^\n]*\n"
            r"\s*)([0-9eE.+-]+)"
            r"(\s*,\s*!-\s*Thermal Resistance[^\n]*)"
        )
        new_text = pat.sub(rf"\g<1>{r_val:.6f}\g<3>", self.text)
        if new_text == self.text:
            log.warning(f"  Could not update Thermal Resistance for '{mat_name}'")
        else:
            self.text = new_text

    def set_window_ufactor_shgc(self, u_val, shgc_val):
        """Update all WindowMaterial:SimpleGlazingSystem objects."""
        pat = re.compile(
            r"(?m)(WindowMaterial:SimpleGlazingSystem,\s*\n"
            r".*?,\s*!-\s*Name\s*\n)"
            r"(\s*)([0-9eE.+-]+)(\s*,\s*!-.*?U-Factor.*?\n)"
            r"(\s*)([0-9eE.+-]+)(\s*[,;]?\s*!-.*?Solar Heat Gain.*?\n)",
            re.IGNORECASE,
        )
        self.text = pat.sub(
            lambda m: (
                m.group(1)
                + m.group(2) + str(u_val) + m.group(4)
                + m.group(5) + str(shgc_val) + m.group(7)
            ),
            self.text,
        )

    def set_infiltration_ach(self, ach):
        """Set AirChanges/Hour for all ZoneInfiltration:DesignFlowRate."""
        def repl_infil(m):
            block = m.group(0)
            block = re.sub(
                r"(Flow/ExteriorWallArea|Flow/Zone|Flow/ExteriorArea|AirChanges/Hour)",
                "AirChanges/Hour", block, flags=re.IGNORECASE, count=1,
            )
            block = re.sub(
                r"(\s*)([0-9eE.+-]+)(\s*,?\s*!-\s*Design Flow Rate\b[^,\n]*)",
                r"\g<1>0\g<3>", block, flags=re.IGNORECASE, count=1,
            )
            block = re.sub(
                r"(\s*),(\s*!-\s*Air Changes per Hour[^,\n]*\n)",
                rf"\g<1>{ach}\g<2>", block, flags=re.IGNORECASE, count=1,
            )
            block = re.sub(
                r"(\s*)([0-9eE.+-]+)(\s*,?\s*!-\s*Air Changes per Hour[^,\n]*)",
                rf"\g<1>{ach}\g<3>", block, flags=re.IGNORECASE, count=1,
            )
            return block

        pat = re.compile(
            r"(?m)^\s*ZoneInfiltration:DesignFlowRate,\s*\n(?:.*\n)*?.*?;",
            re.IGNORECASE,
        )
        self.text = pat.sub(repl_infil, self.text)

    def save(self, out_path):
        with open(out_path, "w", encoding="latin-1") as f:
            f.write(self.text)


# ===========================================================================
# Retrofit IDF generator
# ===========================================================================

def apply_retrofit(base_idf_path, retrofit_params, output_path):
    """
    Apply one retrofit measure to a copy of the era v26 IDF and save.

    Args:
        base_idf_path:  path to era-specific v26 IDF (unmodified baseline)
        retrofit_params: dict of retrofit targets, e.g. {"wall_U": 0.4}
        output_path:    where to write the modified IDF
    """
    sidf = SAIDF(base_idf_path)

    if "wall_U" in retrofit_params:
        r = u_to_nomass_r(retrofit_params["wall_U"], R_SI_WALL, R_SE_WALL)
        sidf.update_nomass_thermal_r("CN_Wall_Insulation", r)
        log.info(f"    wall: U={retrofit_params['wall_U']} → R_bulk={r:.4f} m²K/W")

    if "roof_U" in retrofit_params:
        r = u_to_nomass_r(retrofit_params["roof_U"], R_SI_ROOF, R_SE_ROOF)
        sidf.update_nomass_thermal_r("CN_Roof_Insulation", r)
        log.info(f"    roof: U={retrofit_params['roof_U']} → R_bulk={r:.4f} m²K/W")

    if "window_U" in retrofit_params:
        shgc = retrofit_params.get("window_SHGC", 0.35)
        sidf.set_window_ufactor_shgc(retrofit_params["window_U"], shgc)
        log.info(f"    window: U={retrofit_params['window_U']}, SHGC={shgc}")

    if "infiltration" in retrofit_params:
        sidf.set_infiltration_ach(retrofit_params["infiltration"])
        log.info(f"    infiltration: {retrofit_params['infiltration']} ACH")

    sidf.save(output_path)


# ===========================================================================
# EnergyPlus runner + output parser
# ===========================================================================

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


def run_energyplus(idf_path, epw_path, output_dir, ep_exe):
    """Run EnergyPlus. Returns True on success."""
    os.makedirs(output_dir, exist_ok=True)
    cmd = [ep_exe, "-w", epw_path, "-d", output_dir, idf_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
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
    """
    Parse eplustbl.csv and return dict with energy metrics.
    Mirrors the parse_tbl_csv() in run_baseline.py.
    """
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
            total_gj       = float(parts[-3])
            eui_per_total  = float(parts[-2])
            results["total_site_gj"]  = total_gj
            results["eui_mj_m2"]      = eui_per_total
            results["floor_area_m2"]  = (
                total_gj * 1000.0 / eui_per_total if eui_per_total > 0 else 0.0
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
        DIST_COOL   = 10
        DIST_HEAT_W = 11
        DIST_HEAT_S = 12

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

        heat = parse_row("Heating",           end_uses_idx)
        cool = parse_row("Cooling",           end_uses_idx)
        ltg  = parse_row("Interior Lighting", end_uses_idx)
        eqp  = parse_row("Interior Equipment",end_uses_idx)
        fans = parse_row("Fans",              end_uses_idx)

        results["heating_gj"]  = sg(heat, NATGAS_COL-1) + sg(heat, DIST_HEAT_W-1) + sg(heat, DIST_HEAT_S-1)
        results["cooling_gj"]  = sg(cool, ELEC_COL-1)   + sg(cool, DIST_COOL-1)
        results["lighting_gj"] = sg(ltg,  ELEC_COL-1)
        results["equipment_gj"]= sg(eqp,  ELEC_COL-1)
        results["fans_gj"]     = sg(fans, ELEC_COL-1)

    return results


def gj_to_kwh_m2(gj, fa):
    if not fa or fa <= 0:
        return 0.0
    return gj * 1e9 / 3.6e6 / fa


def extract_eui(output_dir):
    """
    Parse EnergyPlus output directory and return energy metrics (kWh/m²).
    Returns None on failure.
    """
    tbl = os.path.join(output_dir, "eplustbl.csv")
    if not os.path.isfile(tbl):
        log.error(f"  eplustbl.csv not found in {output_dir}")
        return None

    raw = parse_tbl_csv(tbl)
    fa  = raw.get("floor_area_m2", 0)
    if not fa:
        return None

    return {
        "floor_area_m2":    round(fa, 1),
        "heating_kwh_m2":   round(gj_to_kwh_m2(raw.get("heating_gj", 0), fa), 2),
        "cooling_kwh_m2":   round(gj_to_kwh_m2(raw.get("cooling_gj", 0), fa), 2),
        "lighting_kwh_m2":  round(gj_to_kwh_m2(raw.get("lighting_gj", 0), fa), 2),
        "equipment_kwh_m2": round(gj_to_kwh_m2(raw.get("equipment_gj", 0), fa), 2),
        "fans_kwh_m2":      round(gj_to_kwh_m2(raw.get("fans_gj", 0), fa), 2),
        "total_eui_kwh_m2": round(raw.get("eui_mj_m2", 0) / 3.6, 2),
    }


# ===========================================================================
# Main orchestration
# ===========================================================================

def main():
    ep_exe = find_energyplus()
    if ep_exe is None:
        log.error("EnergyPlus not found.  Install or set ENERGYPLUS_DIR.")
        sys.exit(1)
    log.info(f"EnergyPlus: {ep_exe}")

    if not os.path.isfile(EPW):
        log.error(f"EPW not found: {EPW}")
        sys.exit(1)

    # Load baseline results
    baseline_csv = os.path.join(DATA_PROC, "baseline_results.csv")
    if not os.path.isfile(baseline_csv):
        log.error(f"Baseline results not found: {baseline_csv}")
        log.error("Run run_baseline.py first.")
        sys.exit(1)

    baseline_df = pd.read_csv(baseline_csv)
    baseline_lookup = {
        int(r["era"]): r for _, r in baseline_df.iterrows()
    }

    os.makedirs(DATA_PROC, exist_ok=True)
    os.makedirs(FIGURE_DIR, exist_ok=True)
    os.makedirs(DATA_SIM,   exist_ok=True)

    rows = []

    # ---- Add baseline rows ----
    for era_key, meta in ARCHETYPES.items():
        era_num = meta["era"]
        base = baseline_lookup.get(era_num)
        if base is None:
            continue
        rows.append({
            "archetype":       era_key,
            "era":             era_num,
            "era_label":       meta["label"],
            "retrofit":        "Baseline",
            "retrofit_label":  "Baseline",
            "description":     "No retrofit applied",
            "heating_kwh_m2":  float(base["heating_kwh_m2"]),
            "cooling_kwh_m2":  float(base["cooling_kwh_m2"]),
            "total_eui_kwh_m2": float(base["total_eui_kwh_m2"]),
            "baseline_eui":    float(base["total_eui_kwh_m2"]),
            "savings_percent": 0.0,
            "heat_savings_pct": 0.0,
            "cool_savings_pct": 0.0,
        })

    # ---- Simulate each era × retrofit ----
    n_total   = len(ARCHETYPES) * len(RETROFIT_MEASURES)
    n_done    = 0
    n_failed  = 0

    for era_key, meta in ARCHETYPES.items():
        era_num     = meta["era"]
        base_idf    = meta["idf"]
        base_metrics = baseline_lookup.get(era_num)

        if not os.path.isfile(base_idf):
            log.error(f"Base IDF not found: {base_idf}")
            continue

        if base_metrics is None:
            log.error(f"No baseline row for era {era_num}")
            continue

        baseline_eui  = float(base_metrics["total_eui_kwh_m2"])
        baseline_heat = float(base_metrics["heating_kwh_m2"])
        baseline_cool = float(base_metrics["cooling_kwh_m2"])

        for retrofit_key, retrofit_meta in RETROFIT_MEASURES.items():
            n_done += 1
            log.info(f"\n[{n_done}/{n_total}] {era_key} + {retrofit_key}")

            # Build retrofit params (only the keys that belong to retrofit measures)
            retrofit_param_keys = {"wall_U", "roof_U", "window_U", "window_SHGC", "infiltration"}
            retrofit_params = {k: v for k, v in retrofit_meta.items()
                               if k in retrofit_param_keys}

            # Apply retrofit to a temporary IDF
            scenario_name = f"retrofit_{era_num}_{retrofit_key}"
            out_dir       = os.path.join(DATA_SIM, scenario_name)
            mod_idf_path  = os.path.join(DATA_MODELS, f"{scenario_name}.idf")

            try:
                apply_retrofit(base_idf, retrofit_params, mod_idf_path)
            except Exception as e:
                log.error(f"  IDF modification failed: {e}")
                n_failed += 1
                continue

            # Run EnergyPlus
            ok = run_energyplus(mod_idf_path, EPW, out_dir, ep_exe)
            if not ok:
                log.error(f"  Simulation failed — skipping")
                n_failed += 1
                continue

            # Parse results
            metrics = extract_eui(out_dir)
            if metrics is None:
                log.error("  Could not parse EnergyPlus output")
                n_failed += 1
                continue

            # Compute savings
            retrofit_eui  = metrics["total_eui_kwh_m2"]
            retrofit_heat = metrics["heating_kwh_m2"]
            retrofit_cool = metrics["cooling_kwh_m2"]

            savings_pct    = (baseline_eui  - retrofit_eui)  / baseline_eui  * 100 if baseline_eui  else 0.0
            heat_save_pct  = (baseline_heat - retrofit_heat) / baseline_heat * 100 if baseline_heat else 0.0
            cool_save_pct  = (baseline_cool - retrofit_cool) / baseline_cool * 100 if baseline_cool else 0.0

            log.info(f"  EUI: {baseline_eui:.1f} → {retrofit_eui:.1f} kWh/m²  "
                     f"(savings {savings_pct:.1f}%)")
            log.info(f"  Heating: {baseline_heat:.1f} → {retrofit_heat:.1f}  "
                     f"({heat_save_pct:.1f}%)")
            log.info(f"  Cooling: {baseline_cool:.1f} → {retrofit_cool:.1f}  "
                     f"({cool_save_pct:.1f}%)")

            rows.append({
                "archetype":        era_key,
                "era":              era_num,
                "era_label":        meta["label"],
                "retrofit":         retrofit_key,
                "retrofit_label":   retrofit_meta["short"],
                "description":      retrofit_meta["description"],
                "heating_kwh_m2":   retrofit_heat,
                "cooling_kwh_m2":   retrofit_cool,
                "total_eui_kwh_m2": retrofit_eui,
                "baseline_eui":     baseline_eui,
                "savings_percent":  round(savings_pct, 2),
                "heat_savings_pct": round(heat_save_pct, 2),
                "cool_savings_pct": round(cool_save_pct, 2),
            })

    if not rows:
        log.error("No results produced.")
        sys.exit(1)

    # ---- Save CSV ----
    df = pd.DataFrame(rows)
    out_csv = os.path.join(DATA_PROC, "retrofit_results.csv")
    df.to_csv(out_csv, index=False, float_format="%.2f")
    log.info(f"\nSaved retrofit results → {out_csv}")

    # ---- Print summary table ----
    pivot = (
        df[df["retrofit"] != "Baseline"]
        .pivot_table(index="retrofit", columns="era_label",
                     values="savings_percent", aggfunc="first")
    )
    log.info("\n--- Energy Savings (%) vs Baseline ---")
    log.info(pivot.to_string(float_format=lambda x: f"{x:.1f}%"))

    # ---- Generate figure ----
    plot_script = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "postprocessing", "plot_retrofit.py",
    )
    if os.path.isfile(plot_script):
        spec = importlib.util.spec_from_file_location("plot_retrofit", plot_script)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.plot_retrofit_savings()
    else:
        log.warning(f"plot_retrofit.py not found; run it separately.")

    if n_failed:
        log.warning(f"\n{n_failed}/{n_total} scenario(s) failed — check logs above.")
    log.info("Done.")


if __name__ == "__main__":
    main()
