"""
morris_sa.py
============
Full Morris Elementary Effects Sensitivity Analysis for three Changsha
residential building archetypes (Era 1, 2, 3).

Runs real EnergyPlus simulations.  With N=100 trajectories and 10 parameters
each era requires 1 100 simulation runs (~9–36 h wall time depending on CPU).

  Use --N 20 for a quicker validation run.
  Use morris_sa_demo.py for instant pipeline testing (synthetic model).

Usage:
    python morris_sa.py                    # all 3 eras, N=100
    python morris_sa.py --era 2            # single era
    python morris_sa.py --N 20             # fewer trajectories
    python morris_sa.py --era 1 --N 10    # quick smoke-test with real EP

Outputs:
    data/processed/morris_results_era{1,2,3}.csv
    figure/fig05_morris_sa.png  (via plot_morris.py)

References:
    Morris MD (1991) Technometrics 33(2):161-174
    SALib: Herman & Usher (2017) JOSS 2(9):97
"""

import os
import re
import sys
import math
import shutil
import logging
import argparse
import tempfile
import subprocess
import importlib.util

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
DATA_MODELS   = os.path.join(REPO_ROOT, "data", "models")
DATA_PROC     = os.path.join(REPO_ROOT, "data", "processed")
FIGURE_DIR    = os.path.join(REPO_ROOT, "figure")
DATA_CLIMATE  = os.path.join(REPO_ROOT, "data", "climate")

EPW = os.path.join(
    DATA_CLIMATE,
    "CHN_HN_Changsha.576870_TMYx.2007-2021.epw",
)

# ---------------------------------------------------------------------------
# SA problem definition  (10 parameters, bounds span plausible retrofit range)
# ---------------------------------------------------------------------------
PROBLEM = {
    "num_vars": 10,
    "names": [
        "wall_U",           # W/m²K  — wall overall U-value
        "roof_U",           # W/m²K  — roof overall U-value
        "window_U",         # W/m²K  — window centre-of-glass U-factor
        "WWR",              # —      — window-to-wall ratio
        "infiltration",     # ACH    — air changes per hour at 50 Pa (normalised)
        "cooling_setpoint", # °C     — cooling thermostat setpoint
        "heating_setpoint", # °C     — heating thermostat setpoint
        "lighting_power",   # W/m²   — lighting power density
        "equipment_power",  # W/m²   — plug-load power density
        "occupant_density", # m²/p   — floor area per occupant
    ],
    "bounds": [
        [0.4,  1.8],    # wall_U
        [0.3,  1.4],    # roof_U
        [2.0,  6.0],    # window_U
        [0.20, 0.50],   # WWR
        [0.3,  2.0],    # infiltration
        [24.0, 28.0],   # cooling_setpoint
        [16.0, 20.0],   # heating_setpoint
        [3.0,  12.0],   # lighting_power
        [2.0,  10.0],   # equipment_power
        [15.0, 40.0],   # occupant_density
    ],
    "groups": None,
}

# Surface film resistances per ISO 6946
R_SI_WALL, R_SE_WALL = 0.13, 0.04
R_SI_ROOF, R_SE_ROOF = 0.10, 0.04


def u_to_nomass_r(u_val, r_si, r_se):
    """Convert target overall U-value to bulk layer R."""
    return max(1.0 / u_val - r_si - r_se, 0.02)


# ---------------------------------------------------------------------------
# Building archetypes
# ---------------------------------------------------------------------------
ARCHETYPES = {
    "Era1_1980s_MidRise": {
        "era": 1,
        "idf":   os.path.join(DATA_MODELS, "changsha_era1_v26.idf"),
        "shgc":  0.70,
        "label": "Era 1 (~1980s)",
        "description": "MidRise, pre-code",
    },
    "Era2_2000s_MidRise": {
        "era": 2,
        "idf":   os.path.join(DATA_MODELS, "changsha_era2_v26.idf"),
        "shgc":  0.55,
        "label": "Era 2 (~2000s)",
        "description": "MidRise, partial insulation",
    },
    "Era3_2010s_HighRise": {
        "era": 3,
        "idf":   os.path.join(DATA_MODELS, "changsha_era3_v26.idf"),
        "shgc":  0.40,
        "label": "Era 3 (~2010s+)",
        "description": "HighRise, JGJ 134-2010",
    },
}

# ---------------------------------------------------------------------------
# Parameter labels for plots
# ---------------------------------------------------------------------------
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


# ===========================================================================
# SAIDF — text-based IDF modifier for the SA parameter set
# ===========================================================================

class SAIDF:
    """
    Minimal text-based IDF reader/writer for SA parameter modification.
    Extends the TextIDF approach from adapt_envelope.py with additional
    modifications for setpoints, lighting, equipment, and occupancy.
    """

    def __init__(self, path):
        with open(path, "r", encoding="latin-1") as f:
            self.text = f.read()
        self.path = path

    # ---- opaque envelope ------------------------------------------------

    def update_nomass_thermal_r(self, mat_name, r_val):
        """
        Update the Thermal Resistance field of a named Material:NoMass.
        Targets the pattern generated by adapt_envelope.py (CN_Wall_Insulation,
        CN_Roof_Insulation) with comment '!- Thermal Resistance {m2-K/W}'.
        """
        pat = re.compile(
            r"(?mi)"
            r"(^\s*Material:NoMass,\s*\n"
            r"\s*" + re.escape(mat_name) + r"[,;\s][^\n]*\n"
            r"\s*[^\n]+,\s*[^\n]*\n"   # Roughness line
            r"\s*)([0-9eE.+-]+)"        # ← thermal resistance value
            r"(\s*,\s*!-\s*Thermal Resistance[^\n]*)"
        )
        new_text = pat.sub(rf"\g<1>{r_val:.6f}\g<3>", self.text)
        if new_text == self.text:
            log.warning(f"  [SA] Could not update thermal R for '{mat_name}'")
        else:
            self.text = new_text
            log.debug(f"  [SA] {mat_name}: R = {r_val:.4f} m²K/W")

    # ---- window glazing --------------------------------------------------

    def set_window_ufactor_shgc(self, u_val, shgc_val):
        """Update all WindowMaterial:SimpleGlazingSystem U-Factor and SHGC."""
        pat = re.compile(
            r"(?m)(WindowMaterial:SimpleGlazingSystem,\s*\n"
            r".*?,\s*!-\s*Name\s*\n)"
            r"(\s*)([0-9eE.+-]+)(\s*,\s*!-.*?U-Factor.*?\n)"
            r"(\s*)([0-9eE.+-]+)(\s*[,;]?\s*!-.*?Solar Heat Gain.*?\n)",
            re.IGNORECASE,
        )

        def repl(m):
            return (
                m.group(1)
                + m.group(2) + str(u_val) + m.group(4)
                + m.group(5) + str(shgc_val) + m.group(7)
            )

        self.text = pat.sub(repl, self.text)

    # ---- infiltration ----------------------------------------------------

    def set_infiltration_ach(self, ach):
        """Set air changes per hour for all ZoneInfiltration:DesignFlowRate."""
        def repl_infil(m):
            block = m.group(0)
            block = re.sub(
                r"(Flow/ExteriorWallArea|Flow/Zone|Flow/ExteriorArea|AirChanges/Hour)",
                "AirChanges/Hour", block, flags=re.IGNORECASE, count=1
            )
            block = re.sub(
                r"(\s*)([0-9eE.+-]+)(\s*,?\s*!-\s*Design Flow Rate\b[^,\n]*)",
                r"\g<1>0\g<3>", block, flags=re.IGNORECASE, count=1
            )
            block = re.sub(
                r"(\s*)([0-9eE.+-]+)(\s*,?\s*!-\s*Flow per Zone Floor Area[^,\n]*)",
                r"\g<1>\g<3>", block, flags=re.IGNORECASE, count=1
            )
            block = re.sub(
                r"(\s*)([0-9eE.+-]+)(\s*,?\s*!-\s*Flow per Exterior Surface Area[^,\n]*)",
                r"\g<1>\g<3>", block, flags=re.IGNORECASE, count=1
            )
            block = re.sub(
                r"(\s*),(\s*!-\s*Air Changes per Hour[^,\n]*\n)",
                rf"\g<1>{ach}\g<2>", block, flags=re.IGNORECASE, count=1
            )
            block = re.sub(
                r"(\s*)([0-9eE.+-]+)(\s*,?\s*!-\s*Air Changes per Hour[^,\n]*)",
                rf"\g<1>{ach}\g<3>", block, flags=re.IGNORECASE, count=1
            )
            return block

        pat = re.compile(
            r"(?m)^\s*ZoneInfiltration:DesignFlowRate,\s*\n(?:.*\n)*?.*?;",
            re.IGNORECASE,
        )
        self.text = pat.sub(repl_infil, self.text)

    # ---- WWR -------------------------------------------------------------

    def set_wwr(self, target_wwr):
        """Scale FenestrationSurface:Detailed vertices to achieve target WWR."""
        # Reuse geometry helpers from adapt_envelope
        wall_areas = {}
        _bs_pat = re.compile(
            r"(?m)^\s*BuildingSurface:Detailed,\s*\n((?:.*\n)*?.*?;)",
            re.IGNORECASE,
        )
        for m in _bs_pat.finditer(self.text):
            block = m.group(0)
            fields = _extract_fields(block)
            if len(fields) < 9:
                continue
            if "wall" in fields[2].lower() and "outdoor" in "".join(fields).lower():
                verts = _extract_vertices(block)
                if verts:
                    wall_areas[fields[1]] = _poly_area_3d(verts)

        if not wall_areas:
            return

        _fs_pat = re.compile(
            r"(?m)^\s*FenestrationSurface:Detailed,\s*\n((?:.*\n)*?.*?;)",
            re.IGNORECASE,
        )

        def scale_fen(m):
            block = m.group(0)
            fields = _extract_fields(block)
            if len(fields) < 5:
                return block
            parent = fields[4]
            wall_area = wall_areas.get(parent, 0)
            if wall_area < 0.01:
                return block
            verts = _extract_vertices(block)
            if not verts:
                return block
            win_area = _poly_area_3d(verts)
            if win_area < 0.001:
                return block
            scale = min(math.sqrt(target_wwr / (win_area / wall_area)), 0.97)
            return _replace_vertices(block, _scale_poly(verts, scale))

        self.text = _fs_pat.sub(scale_fen, self.text)

    # ---- thermostat setpoints --------------------------------------------

    def set_setpoints(self, heating_sp, cooling_sp):
        """
        Replace all temperature values in apartment thermostat schedules.
        Targets the specific schedule names used in the DOE MidRise/HighRise
        Apartment prototype: *HTGSETP_APT_SCH* and *CLGSETP_APT_SCH*.
        """
        htg_patterns = [
            r"HTGSETP_APT_SCH",
            r"S\s+HTGSETP_APT_SCH",
            r"N\s+HTGSETP_APT_SCH",
        ]
        clg_patterns = [
            r"CLGSETP_APT_SCH",
            r"S\s+CLGSETP_APT_SCH",
            r"N\s+CLGSETP_APT_SCH",
        ]

        def replace_temps_in_schedule(text, name_pat, new_temp):
            # Match the full Schedule:Compact block whose name matches name_pat
            sched_pat = re.compile(
                r"(?mi)(^\s*Schedule:Compact,\s*\n"
                r"\s*" + name_pat + r"[,;\s][^\n]*\n"
                r"(?:.*\n)*?.*?;)"
            )

            def repl(m):
                block = m.group(0)
                # Replace temperature values after "Until: HH:MM,"
                block = re.sub(
                    r"(?i)(Until:\s*\d+:\d+\s*,)\s*([0-9eE.+-]+)",
                    rf"\g<1>{new_temp:.1f}",
                    block,
                )
                return block

            return sched_pat.sub(repl, text)

        for pat in htg_patterns:
            self.text = replace_temps_in_schedule(self.text, pat, heating_sp)
        for pat in clg_patterns:
            self.text = replace_temps_in_schedule(self.text, pat, cooling_sp)

    # ---- internal gains: lighting ----------------------------------------

    def set_lighting_power_density(self, wpm2):
        """Set Watts per Floor Area in all Lights objects."""
        self._set_watt_per_area("Lights", wpm2)

    # ---- internal gains: equipment ---------------------------------------

    def set_equipment_power_density(self, wpm2):
        """Set Watts per Floor Area in all ElectricEquipment objects."""
        self._set_watt_per_area("ElectricEquipment", wpm2)

    def _set_watt_per_area(self, obj_type, wpm2):
        """Replace Watts per Floor Area field within objects of obj_type."""
        pat = re.compile(
            r"(?mi)^\s*" + re.escape(obj_type) + r",\s*\n(?:.*\n)*?.*?;",
        )

        def repl(m):
            block = m.group(0)
            block = re.sub(
                r"(?m)(^\s*)([0-9eE.+-]+)(\s*,\s*!-\s*Watts per Floor Area[^\n]*)",
                rf"\g<1>{wpm2:.4f}\g<3>",
                block,
            )
            return block

        self.text = pat.sub(repl, self.text)

    # ---- occupant density ------------------------------------------------

    def set_occupant_density(self, m2_per_person):
        """
        Switch People objects from absolute count to Area/Person calculation
        method and set the Floor Area per Person field.
        """
        # Switch calculation method field:
        #   "    People,   !- Number of People Calculation Method"
        self.text = re.sub(
            r"(?m)(^\s*)People(\s*,\s*!-\s*Number of People Calculation Method.*)",
            rf"\g<1>Area/Person\g<2>",
            self.text,
        )
        # Clear Number of People field (blank) — field has no trailing {units}
        # Target:  "    2.5,   !- Number of People\n"  (no units braces)
        self.text = re.sub(
            r"(?m)(^\s*)([0-9eE.+-]+)(\s*,\s*!-\s*Number of People\s*\n)",
            r"\g<1>\g<3>",
            self.text,
        )
        # Clear People per Floor Area (field 6, remains blank)
        # Set Floor Area per Person (field 7):  ",   !- Floor Area per Person {m2/person}"
        self.text = re.sub(
            r"(?m)(^\s*),(\s*!-\s*Floor Area per Person[^\n]*)",
            rf"\g<1>{m2_per_person:.2f},\g<2>",
            self.text,
        )

    # ---- save ------------------------------------------------------------

    def save(self, out_path):
        with open(out_path, "w", encoding="latin-1") as f:
            f.write(self.text)


# ---------------------------------------------------------------------------
# Geometry helpers (mirrors adapt_envelope.py — kept local to avoid coupling)
# ---------------------------------------------------------------------------

def _extract_fields(block):
    stripped = re.sub(r"!.*", "", block)
    return [t.strip() for t in re.split(r"[,;]", stripped) if t.strip()]


def _extract_vertices(block):
    verts = []
    coord_b = re.compile(
        r"(?m)^\s*([0-9eE.+-]+)\s*[,;]\s*!-\s*Vertex\s*\d+\s+[XYZ]-coordinate"
    )
    coords_b = coord_b.findall(block)
    if coords_b:
        for i in range(0, len(coords_b) - 2, 3):
            try:
                verts.append((float(coords_b[i]),
                              float(coords_b[i + 1]),
                              float(coords_b[i + 2])))
            except (ValueError, IndexError):
                break
        return verts
    coord_a = re.compile(
        r"(?m)^\s*([0-9eE.+-]+),([0-9eE.+-]+),([0-9eE.+-]+)[,;]?\s*!-\s*X,Y,Z\s*==>"
    )
    for m in coord_a.finditer(block):
        try:
            verts.append((float(m.group(1)), float(m.group(2)), float(m.group(3))))
        except ValueError:
            continue
    return verts


def _poly_area_3d(verts):
    n = len(verts)
    if n < 3:
        return 0.0
    normal = [0.0, 0.0, 0.0]
    v0 = verts[0]
    for i in range(1, n - 1):
        v1, v2 = verts[i], verts[i + 1]
        e1 = (v1[0] - v0[0], v1[1] - v0[1], v1[2] - v0[2])
        e2 = (v2[0] - v0[0], v2[1] - v0[1], v2[2] - v0[2])
        normal[0] += e1[1] * e2[2] - e1[2] * e2[1]
        normal[1] += e1[2] * e2[0] - e1[0] * e2[2]
        normal[2] += e1[0] * e2[1] - e1[1] * e2[0]
    return 0.5 * math.sqrt(sum(x ** 2 for x in normal))


def _scale_poly(verts, scale):
    n = len(verts)
    cx = sum(v[0] for v in verts) / n
    cy = sum(v[1] for v in verts) / n
    cz = sum(v[2] for v in verts) / n
    return [(cx + scale * (v[0] - cx),
             cy + scale * (v[1] - cy),
             cz + scale * (v[2] - cz)) for v in verts]


def _replace_vertices(block, new_verts):
    coord_lines = re.compile(
        r"(?m)(^\s*)([0-9eE.+-]+)(\s*[,;]\s*!-\s*Vertex\s*\d+\s+[XYZ]-coordinate.*)"
    )
    flat = [c for v in new_verts for c in v]
    i = [0]

    def repl(m):
        if i[0] >= len(flat):
            return m.group(0)
        val = flat[i[0]]
        i[0] += 1
        return f"{m.group(1)}{val:.6f}{m.group(3)}"

    return coord_lines.sub(repl, block)


# ===========================================================================
# IDF modification entry point
# ===========================================================================

def apply_params_to_idf(base_idf_path, params, output_path, era_shgc):
    """
    Write a modified copy of base_idf_path with all 10 SA parameters applied.

    Args:
        base_idf_path: path to the era-specific v26 IDF
        params:        dict mapping PROBLEM["names"] → values
        output_path:   where to write the modified IDF
        era_shgc:      SHGC for this era (not varied in SA; kept constant)
    """
    sidf = SAIDF(base_idf_path)

    # --- envelope opaque ---
    wall_r = u_to_nomass_r(params["wall_U"], R_SI_WALL, R_SE_WALL)
    roof_r = u_to_nomass_r(params["roof_U"], R_SI_ROOF, R_SE_ROOF)
    sidf.update_nomass_thermal_r("CN_Wall_Insulation", wall_r)
    sidf.update_nomass_thermal_r("CN_Roof_Insulation", roof_r)

    # --- window glazing ---
    sidf.set_window_ufactor_shgc(params["window_U"], era_shgc)

    # --- infiltration ---
    sidf.set_infiltration_ach(params["infiltration"])

    # --- WWR ---
    sidf.set_wwr(params["WWR"])

    # --- thermostat setpoints ---
    sidf.set_setpoints(params["heating_setpoint"], params["cooling_setpoint"])

    # --- lighting ---
    sidf.set_lighting_power_density(params["lighting_power"])

    # --- equipment ---
    sidf.set_equipment_power_density(params["equipment_power"])

    # --- occupant density ---
    sidf.set_occupant_density(params["occupant_density"])

    sidf.save(output_path)


# ===========================================================================
# EnergyPlus runner + output parser
# ===========================================================================

def find_energyplus():
    ep = shutil.which("energyplus")
    if ep:
        return ep
    for candidate in [
        os.path.join(os.environ.get("ENERGYPLUS_DIR", ""), "energyplus"),
        "/Applications/EnergyPlus-26-1-0/energyplus",
        "/Applications/EnergyPlus-24-1-0/energyplus",
    ]:
        if candidate and os.path.isfile(candidate):
            return candidate
    return None


def _parse_total_eui(tbl_csv_path):
    """
    Parse total site EUI (kWh/m²/yr) from eplustbl.csv.
    Returns float or NaN on failure.
    """
    try:
        with open(tbl_csv_path, encoding="latin-1") as f:
            lines = f.readlines()
    except OSError:
        return float("nan")

    for line in lines:
        s = line.strip()
        if "Total Site Energy," in s or s.startswith(",Total Site Energy,"):
            parts = [p.strip() for p in s.split(",")]
            try:
                eui_per_total_mj_m2 = float(parts[-2])   # MJ/m² per total area
                return eui_per_total_mj_m2 / 3.6          # → kWh/m²
            except (ValueError, IndexError):
                pass
    return float("nan")


def run_ep_get_eui(idf_path, epw_path, ep_exe, run_idx):
    """
    Run one EnergyPlus simulation and return total site EUI (kWh/m²).
    Returns NaN on simulation failure.
    """
    with tempfile.TemporaryDirectory(prefix=f"sa_run_{run_idx:05d}_") as tmpdir:
        cmd = [ep_exe, "-w", epw_path, "-d", tmpdir, idf_path]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,
            )
        except subprocess.TimeoutExpired:
            log.warning(f"  Run {run_idx}: EnergyPlus timed out")
            return float("nan")

        if result.returncode != 0:
            # Log first Severe/Fatal line only
            err_file = os.path.join(tmpdir, "eplusout.err")
            if os.path.isfile(err_file):
                with open(err_file) as f:
                    for ln in f:
                        if "** Severe" in ln or "** Fatal" in ln:
                            log.warning(f"  Run {run_idx}: {ln.strip()[:120]}")
                            break
            return float("nan")

        tbl = os.path.join(tmpdir, "eplustbl.csv")
        eui = _parse_total_eui(tbl)

    return eui


# ===========================================================================
# Morris sampling and evaluation
# ===========================================================================

def generate_sample(N, seed=42):
    X = morris_sample.sample(
        PROBLEM,
        N=N,
        num_levels=4,
        seed=seed,
        optimal_trajectories=None,
    )
    log.info(f"  Sample matrix: {X.shape[0]} runs × {X.shape[1]} parameters")
    return X


def run_morris_era(era_key, meta, N, ep_exe):
    """
    Run Morris SA for one era archetype.

    Returns:
        X (np.ndarray): sample matrix (n_runs, n_params)
        Y (np.ndarray): EUI outputs  (n_runs,)
    """
    base_idf = meta["idf"]
    if not os.path.isfile(base_idf):
        log.error(f"Base IDF not found: {base_idf}")
        log.error("Run adapt_envelope.py + IDFVersionUpdater first.")
        return None, None

    log.info(f"\n=== Morris SA: {era_key}  (N={N}) ===")
    log.info(f"  Base IDF: {os.path.basename(base_idf)}")
    log.info(f"  Total runs: {N * (PROBLEM['num_vars'] + 1)}")

    X = generate_sample(N)
    n_runs = X.shape[0]
    Y = np.full(n_runs, float("nan"))

    with tempfile.TemporaryDirectory(prefix=f"sa_{era_key}_") as sa_dir:
        for i, row in enumerate(X):
            params = dict(zip(PROBLEM["names"], row))
            mod_idf = os.path.join(sa_dir, f"run_{i:05d}.idf")

            try:
                apply_params_to_idf(base_idf, params, mod_idf, meta["shgc"])
            except Exception as e:
                log.warning(f"  Run {i+1}/{n_runs}: IDF modification failed: {e}")
                continue

            eui = run_ep_get_eui(mod_idf, EPW, ep_exe, run_idx=i)
            Y[i] = eui

            if (i + 1) % 10 == 0 or (i + 1) == n_runs:
                n_ok = int(np.sum(~np.isnan(Y[:i + 1])))
                log.info(f"  Progress: {i+1}/{n_runs}  OK={n_ok}  "
                         f"mean={np.nanmean(Y[:i+1]):.1f} kWh/m²")

    return X, Y


# ===========================================================================
# Analysis and output
# ===========================================================================

def analyze_results(X, Y):
    """Run SALib Morris analysis; replace NaN Y values with mean."""
    n_nan = int(np.sum(np.isnan(Y)))
    if n_nan == len(Y):
        log.error("All runs returned NaN — cannot compute SA.")
        return None
    if n_nan > 0:
        log.warning(f"  {n_nan}/{len(Y)} NaN values replaced with mean.")
        Y = np.where(np.isnan(Y), np.nanmean(Y), Y)

    Si = morris_analyze.analyze(
        PROBLEM, X, Y,
        conf_level=0.95,
        print_to_console=False,
        num_levels=4,
    )
    return Si


def save_results(Si, era_num, out_csv):
    """Save sensitivity indices to CSV."""
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


def print_summary(df, era_key):
    log.info(f"\n--- Morris Results: {era_key} ---")
    log.info(f"{'#':<3} {'Parameter':<22} {'μ*':>8} {'±conf':>8} {'σ':>8}")
    log.info("-" * 55)
    for _, r in df.iterrows():
        log.info(f"#{int(r['rank']):<2} {r['parameter']:<22} "
                 f"{r['mu_star']:>8.3f} {r['mu_star_conf']:>8.3f} {r['sigma']:>8.3f}")


# ===========================================================================
# Main
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Morris SA for Changsha residential buildings (real EnergyPlus)"
    )
    parser.add_argument("--N", type=int, default=100,
                        help="Number of Morris trajectories (default 100 ≈ 1 100 runs/era)")
    parser.add_argument("--era", type=int, choices=[1, 2, 3], default=None,
                        help="Run SA for one era only (default: all 3)")
    args = parser.parse_args()

    ep_exe = find_energyplus()
    if ep_exe is None:
        log.error("EnergyPlus executable not found.")
        log.error("Install from https://energyplus.net/ or set ENERGYPLUS_DIR.")
        log.error("Use morris_sa_demo.py for synthetic-model testing.")
        sys.exit(1)
    log.info(f"EnergyPlus: {ep_exe}")

    if not os.path.isfile(EPW):
        log.error(f"EPW not found: {EPW}")
        sys.exit(1)

    os.makedirs(DATA_PROC, exist_ok=True)
    os.makedirs(FIGURE_DIR, exist_ok=True)

    # Select eras
    era_keys = [k for k, v in ARCHETYPES.items()
                if args.era is None or v["era"] == args.era]

    n_total = args.N * (PROBLEM["num_vars"] + 1) * len(era_keys)
    log.info(f"\nPlanned: {len(era_keys)} era(s) × "
             f"{args.N * (PROBLEM['num_vars'] + 1)} runs = {n_total} total")
    log.info("Estimated time: 0.5–2 min/run × runs (see README for HPC options)\n")

    result_dfs = {}
    for era_key in era_keys:
        meta = ARCHETYPES[era_key]
        era_num = meta["era"]

        X, Y = run_morris_era(era_key, meta, args.N, ep_exe)
        if X is None:
            continue

        Si = analyze_results(X, Y)
        if Si is None:
            continue

        out_csv = os.path.join(DATA_PROC, f"morris_results_era{era_num}.csv")
        df = save_results(Si, era_num, out_csv)
        print_summary(df, era_key)
        result_dfs[era_key] = df

    if not result_dfs:
        log.error("No SA results produced.")
        sys.exit(1)

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
        log.warning(f"plot_morris.py not found; run it separately.")

    log.info("\nDone.")


if __name__ == "__main__":
    main()
