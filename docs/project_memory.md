# Project Memory

> This file is the persistent context for Claude Code. Read this first in every session.

---

## Project Identity
- **Repo:** `stefana715/Retrofit-Strategies`
- **Author:** Yaning An
- **Target journal:** Energy and Buildings (Elsevier)
- **Study city:** Changsha (HSCW climate zone, locked — see `decision_log.md`)
- **Paper topic:** Optimization of retrofit strategies with solar panel integration in residential buildings under climate change scenarios

## One-Sentence Summary
A simulation-based study using EnergyPlus and Morris sensitivity analysis to optimize envelope retrofit strategies and solar panel integration for representative Changsha residential building archetypes across different construction eras, evaluated under future climate change scenarios.

## Key Approach: No Manual Modeling
We do NOT build EnergyPlus models from scratch. Instead:
1. Use DOE/PNNL prototype residential buildings (MidRiseApartment, HighRiseApartment) as base IDF files.
2. Modify envelope parameters with `eppy` (Python) to represent different Chinese construction eras.
3. Run with Changsha TMY weather file.
4. This is academically justified — see Chen et al. (2022) Building Simulation, who did exactly this for 68,966 buildings in Changsha.

## Method Chain (10 steps)
1. **Weather data** — download Changsha TMY EPW from climate.onebuilding.org
2. **Base building models** — obtain DOE prototype residential IDF files (MidRise/HighRise Apartment)
3. **Era-specific adaptation** — use eppy to modify envelope U-values, WWR, infiltration to match Chinese standards for 1980s, 2000s, 2010s+ construction
4. **Baseline simulation** — run EnergyPlus with Changsha TMY weather
5. **Morris sensitivity analysis** — SALib to identify most influential parameters
6. **Retrofit scenario design** — wall insulation, window upgrade, roof insulation, shading
7. **Solar panel integration** — rooftop PV sizing with PVLib or E+ PV objects
8. **Climate change scenarios** — generate future EPW files (2050, 2080 SSP2-4.5/SSP5-8.5) with CCWorldWeatherGen, re-run simulations
9. **Results & figures** — energy savings %, sensitivity rankings, solar contribution
10. **Manuscript writing** — structured per E&B format

## Building Archetypes (Changsha)
| ID | Archetype | Era | Base IDF | Key Envelope Mods |
|----|-----------|-----|----------|-------------------|
| CS-01 | MidRise Apartment (6F) | ~1980s | DOE MidRiseApartment Pre-1980 | Wall U=1.5, Window U=5.8, WWR=0.25, no insulation |
| CS-02 | MidRise Apartment (6F) | ~2000s | DOE MidRiseApartment 2004 | Wall U=1.0, Window U=3.5, WWR=0.30, partial insulation |
| CS-03 | HighRise Apartment (18F) | ~2010s+ | DOE HighRiseApartment 2013 | Wall U=0.6, Window U=2.5, WWR=0.40, code-compliant |

> ⚠ U-values above are indicative. Must cross-check with Chinese standards:
> - JGJ 134 (Design Standard for Energy Efficiency of Residential Buildings in HSCW Zone)
> - GB 50189 (Design Standard for Energy Efficiency of Public Buildings)

## Key Software & Tools
- **EnergyPlus** (v24.1+) — simulation engine
- **eppy** (Python) — IDF modification and batch runs
- **SALib** (Python) — Morris sensitivity analysis
- **PVLib** (Python) — solar PV estimation
- **CCWorldWeatherGen** (Excel) — future climate EPW generation
- **pandas + matplotlib** — data processing and figures
- **Climate files:** Changsha TMY EPW + future morphed EPW files

## Open-Source Resources
- EnergyPlus: https://github.com/NREL/EnergyPlus
- DOE Prototype Buildings: https://www.energycodes.gov/prototype-building-models
- openstudio-standards: https://github.com/NREL/openstudio-standards
- SALib: https://github.com/SALib/SALib
- eppy: https://github.com/santoshphilip/eppy
- PVLib: https://github.com/pvlib/pvlib-python
- Weather files: https://climate.onebuilding.org
- CCWorldWeatherGen: https://energy.soton.ac.uk/ccworldweathergen/

## Key Reference Papers
1. **Beijing retrofit SA** (E&B 2023): "Simulation-based sensitivity analysis of energy performance applied to an old Beijing residential neighbourhood for retrofit strategy optimisation with climate change prediction" — closest methodological predecessor
2. **Solar urban block** (Renewable Energy 2021): "A parametric method using vernacular urban block typologies for investigating interactions between solar energy use and urban design"
3. **Changsha UBEM** (Building Simulation 2022): Chen et al., "Archetype identification and urban building energy modeling for city-scale buildings based on GIS datasets" — 68,966 buildings in Changsha

## Immediate TODO (ordered)
1. ✅ Lock study city: Changsha
2. ✅ Lock approach: DOE prototypes + eppy modification
3. ⬜ Download Changsha TMY EPW file
4. ⬜ Obtain DOE prototype residential IDF files
5. ⬜ Write Python script to adapt IDF envelope parameters for Chinese eras
6. ⬜ Run baseline simulations
7. ⬜ Set up Morris SA with SALib
8. ⬜ Design retrofit scenarios
9. ⬜ Generate future climate EPW files
10. ⬜ Write manuscript

## File Conventions
- Manuscripts: `draft/manuscript_v{N}.md`
- Figures: `figure/fig{NN}_{short_name}.{ext}`
- Data: `data/processed/{description}.csv`
- Code: `code/{stage}/{script_name}.py`
- All docs: `docs/{name}.md`
- Weather files: `data/climate/{filename}.epw`
- IDF models: `data/models/{archetype_name}.idf`

---

*Last updated: 2026-04-14*
