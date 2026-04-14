#!/usr/bin/env bash
# =============================================================================
# run_baseline.sh
# Run EnergyPlus baseline simulations for three Changsha residential archetypes.
#
# Prerequisites:
#   1. EnergyPlus 24.1+ installed (https://energyplus.net)
#   2. Era IDF files upgraded to match your EnergyPlus version:
#        data/models/changsha_era{1,2,3}_v26.idf
#      (Created by running the IDFVersionUpdater transition chain from v22.1)
#   3. Python 3.9+ with pandas, matplotlib installed
#
# Usage:
#   chmod +x code/simulation/run_baseline.sh
#   ./code/simulation/run_baseline.sh
#
# Or with a custom EnergyPlus path:
#   ENERGYPLUS=/path/to/energyplus ./code/simulation/run_baseline.sh
# =============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EPW="${REPO_ROOT}/data/climate/CHN_HN_Changsha.576870_TMYx.2007-2021.epw"
SIM_DIR="${REPO_ROOT}/data/simulation"
PROC_DIR="${REPO_ROOT}/data/processed"
FIG_DIR="${REPO_ROOT}/figure"

# ---------------------------------------------------------------------------
# Locate EnergyPlus executable
# ---------------------------------------------------------------------------
if [[ -n "${ENERGYPLUS:-}" ]]; then
    EP_EXE="${ENERGYPLUS}"
elif command -v energyplus &>/dev/null; then
    EP_EXE="$(command -v energyplus)"
elif [[ -f "/Applications/EnergyPlus-26-1-0/energyplus" ]]; then
    EP_EXE="/Applications/EnergyPlus-26-1-0/energyplus"
elif [[ -f "/Applications/EnergyPlus-24-1-0/energyplus" ]]; then
    EP_EXE="/Applications/EnergyPlus-24-1-0/energyplus"
elif [[ -n "${ENERGYPLUS_DIR:-}" && -f "${ENERGYPLUS_DIR}/energyplus" ]]; then
    EP_EXE="${ENERGYPLUS_DIR}/energyplus"
else
    echo "ERROR: EnergyPlus executable not found."
    echo "  Install from https://energyplus.net/ or set ENERGYPLUS env var."
    exit 1
fi

echo "EnergyPlus: ${EP_EXE}"
"${EP_EXE}" --version 2>&1 | head -1
echo ""

# ---------------------------------------------------------------------------
# Check inputs
# ---------------------------------------------------------------------------
if [[ ! -f "${EPW}" ]]; then
    echo "ERROR: EPW not found: ${EPW}"
    echo "  Run Task 1 (download Changsha EPW) first."
    exit 1
fi

mkdir -p "${SIM_DIR}" "${PROC_DIR}" "${FIG_DIR}"

# ---------------------------------------------------------------------------
# Era definitions
# ---------------------------------------------------------------------------
declare -A ERA_IDF=(
    ["Era1_1980s_MidRise"]="changsha_era1_v26.idf"
    ["Era2_2000s_MidRise"]="changsha_era2_v26.idf"
    ["Era3_2010s_HighRise"]="changsha_era3_v26.idf"
)

# ---------------------------------------------------------------------------
# Run simulations
# ---------------------------------------------------------------------------
FAILED=()
for name in "${!ERA_IDF[@]}"; do
    IDF="${REPO_ROOT}/data/models/${ERA_IDF[$name]}"
    OUT="${SIM_DIR}/${name}"

    if [[ ! -f "${IDF}" ]]; then
        echo "WARNING: IDF not found: ${IDF} — skipping ${name}"
        FAILED+=("${name}")
        continue
    fi

    echo "=== Simulating ${name} ==="
    echo "  IDF: ${ERA_IDF[$name]}"
    mkdir -p "${OUT}"

    if "${EP_EXE}" \
        -w "${EPW}" \
        -d "${OUT}" \
        "${IDF}" \
        > "${OUT}/energyplus.log" 2>&1; then
        echo "  SUCCESS ($(grep 'EnergyPlus Run Time' "${OUT}/energyplus.log" | tail -1))"
    else
        echo "  FAILED — see ${OUT}/energyplus.log and ${OUT}/eplusout.err"
        FAILED+=("${name}")
    fi
    echo ""
done

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
if [[ ${#FAILED[@]} -gt 0 ]]; then
    echo "WARNING: ${#FAILED[@]} simulation(s) failed: ${FAILED[*]}"
fi

# ---------------------------------------------------------------------------
# Post-process: extract results and plot
# ---------------------------------------------------------------------------
echo "Running post-processing ..."
python3 "${REPO_ROOT}/code/simulation/run_baseline.py"

echo ""
echo "Done. Results:"
echo "  ${PROC_DIR}/baseline_results.csv"
echo "  ${FIG_DIR}/fig04_baseline_eui.png"
