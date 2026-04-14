# Retrofit-Strategies

Optimization of retrofit strategies with solar panel integration for multi-era residential neighborhoods in Shanghai under climate change scenarios.

**Target journal:** Energy and Buildings (Elsevier)

---

## Repository Structure

```
docs/                    # Project management & planning
  project_memory.md      # Persistent context for Claude Code (read first)
  decision_log.md        # All major decisions with rationale
  paper_plan.md          # Paper outline, figure/table plan, word budget
  materials_map.md       # Maps files → method steps → paper sections
draft/                   # Manuscript drafts
  manuscript_v1.md       # Clean manuscript (to be created)
  extracted_notes.md     # Extracted content from Word drafts
data/
  climate/               # Weather files (EPW, TMY)
  raw/                   # Original case-study data
  processed/             # Cleaned data for analysis
code/
  preprocessing/         # Data prep scripts
  simulation/            # EnergyPlus batch run scripts
  sensitivity/           # Morris SA scripts
  postprocessing/        # Results analysis & plotting
figure/                  # All paper figures
refs/
  core_papers/           # Key reference PDFs
output/                  # Final simulation outputs
```

## Methodology

1. Case-study selection (Shanghai, multi-era neighborhoods)
2. Building geometry & attribute collection
3. EnergyPlus model generation
4. Baseline energy simulation
5. Morris sensitivity analysis
6. Retrofit scenario evaluation
7. Solar panel integration
8. Climate change scenario testing
9. Results visualization
10. Manuscript writing

## Current Status

- [x] Project structure created
- [x] Study city locked: Shanghai
- [x] Target journal locked: Energy and Buildings
- [x] Paper outline completed
- [x] Materials inventory completed
- [ ] Shanghai weather file obtained
- [ ] EnergyPlus models built
- [ ] Baseline simulations run
- [ ] Sensitivity analysis completed
- [ ] Retrofit scenarios evaluated
- [ ] Solar integration calculated
- [ ] Future climate testing done
- [ ] Manuscript draft v1 complete

---

*Repository: `stefana715/Retrofit-Strategies`*
