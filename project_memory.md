# Project Memory

> This file is the persistent context for Claude Code. Read this first in every session.

---

## Project Identity
- **Repo:** `stefana715/Retrofit-Strategies`
- **Author:** Yaning An
- **Target journal:** Energy and Buildings (Elsevier)
- **Study city:** Shanghai (locked, see `decision_log.md`)
- **Paper topic:** Optimization of retrofit strategies with solar panel integration in residential buildings under climate change scenarios

## One-Sentence Summary
A simulation-based study using EnergyPlus and Morris sensitivity analysis to optimize envelope retrofit strategies and solar panel integration for representative Shanghai residential neighborhoods across different construction eras, evaluated under future climate change scenarios.

## Method Chain (10 steps)
1. **Case-study selection** — representative Shanghai neighborhoods from different decades (1960s, 1980s, 2000s+)
2. **Geometry & attribute collection** — building footprint, height, floor count, envelope U-values, window-wall ratio, age, typology
3. **Model generation** — EnergyPlus models, possibly via SimStock or manual IDF construction
4. **Baseline simulation** — annual energy performance under current TMY weather
5. **Morris sensitivity analysis** — identify most influential envelope/operational parameters
6. **Retrofit scenario design** — wall insulation, window upgrade, roof insulation, shading, etc.
7. **Solar panel integration** — rooftop/facade PV sizing, orientation, generation estimation
8. **Climate change scenario testing** — future weather files (e.g., 2050, 2080 under RCP/SSP scenarios)
9. **Results & figures** — energy savings %, sensitivity rankings, solar contribution, cost-benefit if applicable
10. **Manuscript writing** — structured per E&B format

## Case-Study Neighborhoods (Shanghai)
| ID | Name | Era | Notes |
|----|------|-----|-------|
| SH-01 | 淮海坊 (Huaihai Fang) | ~1960s | Lilong / lane-house typology |
| SH-02 | 徐家汇花园 (Xujiahui Garden) | ~1980s | Multi-storey residential |
| SH-03 | 碧云国际社区 (Biyun International Community) | ~2000s | Modern high-rise residential |
| SH-04 | 世纪公园高端住宅区 (Century Park high-end) | ~2010s | High-end modern residential |

> ⚠ Confirm: are all four neighborhoods still in the final scope, or will it be narrowed to 2–3?

## Key Software & Tools
- **EnergyPlus** — building energy simulation engine
- **SimStock** — urban building stock model generator (UCL-based tool)
- **Morris method** — global sensitivity analysis (SALib or custom implementation)
- **Python** — preprocessing, postprocessing, plotting
- **Climate files needed:** Shanghai TMY + future climate morphed EPW files

## Available Materials Status

### ✅ Clearly available
- Shanghai manuscript narrative backbone (Introduction, Study Area, partial Methodology)
- Shenzhen weather files (reserved, not for main paper)
- Two core reference papers (Beijing E&B 2023; Renewable Energy 2021)
- Shanghai case-study image material (淮海坊, 徐家汇花园 folders)
- ICSCGE 2024 conference abstract (Shenzhen version — reference only)

### ⚠ Partially available / needs verification
- EnergyPlus model files (IDF) — not yet confirmed in upload
- SimStock project files — not yet confirmed
- Shanghai TMY weather file — **needed, not yet in repo**
- Sensitivity analysis results — some text suggests completion, but no raw output found

### ❌ Not yet available
- Future climate weather files for Shanghai (2050, 2080 under SSP scenarios)
- Final simulation output tables (CSV/Excel)
- Sensitivity analysis result tables / figures
- Solar panel generation calculation outputs
- Complete, internally consistent manuscript draft
- Submission-ready reference list
- Figure source files

## Immediate Priorities (ordered)
1. Get Shanghai TMY weather file into `data/climate/`
2. Extract usable text from existing Word drafts into `draft/extracted_notes.md`
3. Build a clean manuscript outline matching E&B structure → `docs/paper_plan.md`
4. Map each existing file to the paper section it supports → `docs/materials_map.md`
5. Identify which simulation runs are actually complete vs. only described

## File Conventions
- Manuscripts: `draft/manuscript_v{N}.md`
- Figures: `figure/fig{NN}_{short_name}.{ext}`
- Data: `data/processed/{description}.csv`
- Code: `code/{stage}/{script_name}.py`
- All docs: `docs/{name}.md`

---

*Last updated: 2026-04-06*
