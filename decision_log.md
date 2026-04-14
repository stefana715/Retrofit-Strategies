# Decision Log

All major project decisions are recorded here with date, rationale, and status.

---

## Decision 001 — Study City: Shanghai
- **Date:** 2026-04-06
- **Decision:** Use **Shanghai** as the main case-study city.
- **Rationale:**
  - The existing manuscript body (Introduction, Study Area, neighborhood selection) is entirely Shanghai-based.
  - Case-study image folders (`1960-淮海坊/`, `1980-徐家汇花园/`) are Shanghai neighborhoods.
  - The "Shenzhen" version was only a title/abstract adaptation; no actual Shenzhen case-study data exists in the current package.
  - Internal consistency is the fastest path to a submittable paper.
- **Consequence:** All Shenzhen references must be removed from the main manuscript. Shenzhen weather files and conference abstract are preserved in `data/climate/shenzhen_reserved/` for a possible future extension or comparison paper.
- **Status:** ✅ Final

## Decision 002 — Target Journal: Energy and Buildings
- **Date:** 2026-04-06
- **Decision:** Target **Energy and Buildings** (Elsevier, ISSN 0378-7788) as the submission journal.
- **Rationale:**
  - Directly in scope: retrofit strategies, building energy simulation, solar integration, climate change impact on buildings.
  - One of the two core reference papers was published in E&B (the Beijing retrofit sensitivity analysis paper, 2023).
  - High impact and visibility in the building energy research community.
  - The methodology (EnergyPlus + Morris sensitivity + solar + climate scenarios) fits the journal's preference for simulation-based papers with clear links to real building stock.
- **Journal requirements (key points):**
  - Full paper: ≤ 20 double-spaced pages including tables and figures.
  - Abstract: 50–120 words.
  - Structure: Title → Authors → Affiliations → Abstract → Keywords → Main text → Acknowledgements → References → Appendix.
  - Citation style: numbered sequential (`elsarticle-num`).
  - Figures and tables embedded in text (not supplied separately).
  - Single-blind review.
  - Simulation papers are welcome; links to calibration/validation/field data are preferred.
- **Status:** ✅ Final

## Decision 003 — Workflow Convention
- **Date:** 2026-04-06
- **Decision:** Use the following workflow:
  1. All work tracked in this GitHub repo (`stefana715/Retrofit-Strategies`).
  2. Every significant action is logged in `docs/` markdown files.
  3. Claude Code performs the heavy lifting (writing, coding, analysis).
  4. Results are committed and pushed after each work session.
  5. VS Code + Claude Code extension used when visual editing or debugging is needed.
- **Status:** ✅ Final

---
