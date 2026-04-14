# Materials-to-Method Mapping

> Maps every existing file/resource to its role in the paper workflow.
> Status: ✅ Done | ⚠ Partial | ❌ Missing | 🔒 Reserved (not for main paper)

---

## Method Step 1: Case-Study Selection

| Resource | File/Location | Status | Notes |
|----------|--------------|--------|-------|
| Shanghai neighborhood list | Existing drafts (Introduction/Study Area) | ✅ | 4 neighborhoods identified |
| Site photos — 淮海坊 | `1960-淮海坊/` | ⚠ | Images exist; need quality check |
| Site photos — 徐家汇花园 | `1980-徐家汇花园/` | ⚠ | Images exist; need quality check |
| Site photos — Biyun / Century Park | Not found in upload | ❌ | Need to source |
| Shanghai location map | Not yet created | ❌ | Create with Python/GIS |
| Neighborhood attribute table (era, floors, area, typology) | Partially in draft text | ⚠ | Extract and formalize |

## Method Step 2: Geometry & Attribute Collection

| Resource | File/Location | Status | Notes |
|----------|--------------|--------|-------|
| Building footprint data | Not confirmed | ❌ | Need GIS/CAD source |
| Height / floor count data | Partially in draft text | ⚠ | Extract and verify |
| Envelope U-values by era | Partially in draft text | ⚠ | Cross-check with Chinese standards |
| Window-wall ratios | Not confirmed | ❌ | Measure or assume from standards |

## Method Step 3: Model Generation

| Resource | File/Location | Status | Notes |
|----------|--------------|--------|-------|
| EnergyPlus IDF files | Not found in upload | ❌ | Critical gap |
| SimStock project files | Not found in upload | ❌ | May not have been used yet |
| Model generation scripts | Not found | ❌ | Need to build or confirm approach |

## Method Step 4: Baseline Simulation

| Resource | File/Location | Status | Notes |
|----------|--------------|--------|-------|
| Shanghai TMY weather file (EPW) | Not in current upload | ❌ | **Must obtain** — try climate.onebuilding.org |
| Shenzhen TMY weather file | `CHN_GD_Shenzhen.594930_TMYx/` | 🔒 | Reserved for extension |
| Baseline simulation outputs | Not found | ❌ | Depends on IDF + weather file |
| EUI results table | Not found | ❌ | Depends on simulation |

## Method Step 5: Morris Sensitivity Analysis

| Resource | File/Location | Status | Notes |
|----------|--------------|--------|-------|
| SA parameter list & ranges | Partially described in draft | ⚠ | Needs formal definition |
| SALib or custom SA code | Not found | ❌ | Need to write |
| SA result tables / plots | Not found | ❌ | Depends on simulation batch |

## Method Step 6: Retrofit Scenario Design

| Resource | File/Location | Status | Notes |
|----------|--------------|--------|-------|
| Retrofit measure list | Partially described in draft | ⚠ | Needs formal specification |
| Chinese retrofit standards reference | Not compiled | ❌ | GB 50189, JGJ 134, etc. |
| Cost data | Not found | ❌ | Optional for E&B; decide inclusion |

## Method Step 7: Solar Panel Integration

| Resource | File/Location | Status | Notes |
|----------|--------------|--------|-------|
| PV sizing methodology | Partially described in draft | ⚠ | Needs detail |
| Roof area estimates per typology | Not found | ❌ | Derive from geometry |
| PV performance parameters | Not found | ❌ | Define (efficiency, tilt, etc.) |
| Vernacular block + solar ref paper | `1-s2.0-S0960148120316335-main.pdf` | ✅ | Key reference for solar method |

## Method Step 8: Climate Change Scenarios

| Resource | File/Location | Status | Notes |
|----------|--------------|--------|-------|
| Future weather files (Shanghai 2050/2080) | Not found | ❌ | Generate with CCWorldWeatherGen or WeatherShift |
| Climate scenario selection (SSP/RCP) | Not formalized | ❌ | Choose SSP2-4.5 and SSP5-8.5 |
| Beijing SA + climate paper | `1-s2.0-S0378778823005145-main.pdf` | ✅ | Key reference for climate method |

## Method Step 9: Results & Figures

| Resource | File/Location | Status | Notes |
|----------|--------------|--------|-------|
| Result CSV/Excel files | Not found | ❌ | All depend on simulation |
| Plotting scripts | Not found | ❌ | Will build in `code/postprocessing/` |
| Draft figures | Not found | ❌ | To create |

## Method Step 10: Manuscript Writing

| Resource | File/Location | Status | Notes |
|----------|--------------|--------|-------|
| Shanghai draft (main body) | `Optimization of Retrofit...docx` + `Simulation Shanghai.docx` | ✅ | Usable text, needs cleanup |
| Mid-term draft | `draft 中期.docx` | ⚠ | May contain additional notes |
| Shenzhen-titled draft | `Shenzhen ICSCGE/Shenzhen_Optimization...docx` | 🔒 | Title/abstract only; body is Shanghai |
| ICSCGE abstract | `Shenzhen ICSCGE/ICSCGE 2024_Yaning An.docx/.pdf` | 🔒 | Reference only |

---

## Critical Path Summary

The **blocking dependencies** for paper completion are:

```
Shanghai TMY weather file ──→ Baseline simulation ──→ Everything downstream
                                     │
EnergyPlus IDF files ────────────────┘
                                     │
                              Morris SA runs ──→ Retrofit scenarios ──→ Solar integration
                                                                              │
                              Future weather files ──→ Climate change testing ─┘
                                                                              │
                                                              Results & Figures ──→ Manuscript
```

**Immediate blockers to resolve:**
1. 🔴 Shanghai EPW weather file
2. 🔴 EnergyPlus IDF model files (or enough data to build them)
3. 🔴 Future climate weather files for Shanghai

---

*Last updated: 2026-04-06*
