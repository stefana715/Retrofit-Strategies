# Paper Plan — Energy and Buildings Submission

> Target: **Energy and Buildings** (Elsevier)
> Format: Full paper, ≤ 20 double-spaced pages, elsarticle-num citation style

---

## Working Title
**Optimization of Retrofit Strategies with Solar Panel Integration for Multi-Era Residential Neighborhoods in Shanghai Under Climate Change Scenarios**

## Keywords (6–8)
building retrofit; energy simulation; EnergyPlus; Morris sensitivity analysis; solar panel integration; climate change; residential buildings; Shanghai

---

## Paper Structure & Section Plan

### 1. Introduction (~1500 words)
**Purpose:** Motivate the research gap; position the paper in context.

**Key arguments to make:**
- China's existing residential building stock is aging and energy-inefficient; Shanghai has a large stock spanning multiple construction eras
- Retrofit strategies must be evaluated systematically, not as isolated interventions
- Sensitivity analysis is underused in retrofit optimization for Chinese residential buildings
- Solar panel integration is rarely co-optimized with envelope retrofits
- Climate change will shift heating/cooling demands; retrofit decisions made today must remain robust under future climate conditions
- Research gap: no existing study combines Morris SA + multi-era neighborhood comparison + solar integration + climate change testing for Shanghai residential stock

**Core references to build on:**
- Beijing retrofit SA paper (E&B 2023) — closest methodological predecessor; this paper extends to Shanghai, adds solar, adds multi-era comparison
- Vernacular urban block + solar energy paper (Renewable Energy 2021) — typological approach to solar analysis
- Additional references needed: Shanghai building stock studies; Chinese retrofit policy context; climate change projection studies for Yangtze River Delta

### 2. Literature Review (~1000 words)
**Sub-themes:**
- 2.1 Building energy retrofit in Chinese residential stock
- 2.2 Sensitivity analysis methods for retrofit optimization
- 2.3 Solar energy integration in urban residential retrofit
- 2.4 Climate change impacts on building energy performance
- 2.5 Research gap and contribution statement

> Note: E&B sometimes merges Lit Review into Introduction. Decide based on final length.

### 3. Methodology (~2500 words)
**Sub-sections:**

#### 3.1 Study Area and Case-Study Selection
- Shanghai climate context (hot-summer, cold-winter zone)
- Selection criteria: representative neighborhoods from different construction decades
- Description of each case-study neighborhood (era, typology, building form, envelope characteristics)
- Maps and site photos

#### 3.2 Building Energy Model Development
- EnergyPlus version and configuration
- SimStock or manual model generation process
- Model inputs: geometry, construction materials, schedules, HVAC assumptions
- Baseline calibration / validation approach (if field data available, describe; if not, justify with standards/codes)

#### 3.3 Morris Sensitivity Analysis
- Method description (OAT screening, elementary effects)
- Selected parameters and their ranges (envelope U-values, WWR, infiltration, schedules, setpoints, etc.)
- Number of trajectories, levels
- Output metrics (annual heating/cooling energy, total energy use intensity)

#### 3.4 Retrofit Strategy Design
- Retrofit measures considered (wall insulation, window replacement, roof insulation, shading devices, etc.)
- Retrofit packages (individual + combined scenarios)
- Cost assumptions (if included)

#### 3.5 Solar Panel Integration
- PV system sizing methodology
- Roof area / facade area available for each typology
- PV performance parameters (efficiency, orientation, tilt)
- Grid interaction assumptions (net metering, self-consumption)

#### 3.6 Climate Change Scenario Testing
- Future weather file generation method (morphing tool, e.g., CCWorldWeatherGen or WeatherShift)
- Climate scenarios used (e.g., SSP2-4.5, SSP5-8.5 for 2050 and 2080)
- How future performance is compared to baseline

### 4. Results (~3000 words)
#### 4.1 Baseline Energy Performance
- EUI comparison across neighborhoods and eras
- Heating vs. cooling breakdown

#### 4.2 Sensitivity Analysis Results
- Morris μ* and σ rankings
- Most influential parameters per neighborhood type
- Comparative sensitivity across eras

#### 4.3 Retrofit Scenario Performance
- Energy savings by individual and combined retrofit measures
- Best-performing retrofit packages per neighborhood type
- Cost-effectiveness ranking (if included)

#### 4.4 Solar Integration Results
- PV generation potential per typology
- Net energy balance with retrofits + solar
- Contribution of solar to overall energy reduction

#### 4.5 Climate Change Impact
- How baseline and retrofitted performance changes under future scenarios
- Robustness of retrofit strategies across climate scenarios
- Shift in heating/cooling balance

### 5. Discussion (~1500 words)
- Comparison with Beijing SA study and other Chinese retrofit studies
- Why construction era matters for retrofit prioritization
- Interaction between envelope retrofit and solar potential
- Policy implications for Shanghai's retrofit programs
- Limitations and future work

### 6. Conclusions (~500 words)
- Summary of key findings (3–5 bullet points distilled into prose)
- Contribution to knowledge
- Practical recommendations
- Future research directions

### Acknowledgements
- Funding sources
- Data providers

### References
- Target: 40–60 references
- Citation style: numbered sequential (elsarticle-num)

### Appendix (if needed)
- Detailed parameter tables
- Additional sensitivity plots

---

## Figure Plan (preliminary)

| Fig # | Description | Status |
|-------|-------------|--------|
| 1 | Study area map — Shanghai with neighborhood locations | ❌ To create |
| 2 | Site photos / aerial views of each case-study neighborhood | ⚠ Partial (image folders exist) |
| 3 | Methodology flowchart | ❌ To create |
| 4 | Typical building models / 3D views from EnergyPlus | ❌ To create |
| 5 | Morris sensitivity analysis results (μ* vs σ scatter plots) | ❌ Needs simulation |
| 6 | Baseline EUI comparison across neighborhoods | ❌ Needs simulation |
| 7 | Retrofit scenario energy savings (bar chart) | ❌ Needs simulation |
| 8 | Solar PV generation by typology | ❌ Needs simulation |
| 9 | Climate change impact on energy demand (line/bar chart) | ❌ Needs simulation |
| 10 | Combined retrofit + solar net energy under future climate | ❌ Needs simulation |

## Table Plan (preliminary)

| Table # | Description | Status |
|---------|-------------|--------|
| 1 | Case-study neighborhood characteristics | ⚠ Partial |
| 2 | EnergyPlus model input parameters | ❌ To compile |
| 3 | Morris SA parameter ranges | ❌ To define |
| 4 | Retrofit measure specifications | ❌ To define |
| 5 | PV system assumptions | ❌ To define |
| 6 | Baseline simulation results | ❌ Needs simulation |
| 7 | Sensitivity rankings by neighborhood | ❌ Needs simulation |
| 8 | Retrofit energy savings summary | ❌ Needs simulation |
| 9 | Climate scenario comparison | ❌ Needs simulation |

---

## Word Budget (approximate, for ≤ 20 pages)

| Section | Target words |
|---------|-------------|
| Abstract | 100 |
| Introduction | 1500 |
| Literature Review | 1000 |
| Methodology | 2500 |
| Results | 3000 |
| Discussion | 1500 |
| Conclusions | 500 |
| **Total text** | **~10,100** |

Remaining page budget: figures (~6–8) + tables (~4–6) + references.

---

*Last updated: 2026-04-06*
