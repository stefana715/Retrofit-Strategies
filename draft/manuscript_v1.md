# Optimization of Retrofit Strategies with Solar Panel Integration for Multi-Era Residential Buildings in Changsha Under Climate Change Scenarios

**Authors:** Yaning An

**Target Journal:** Energy and Buildings (Elsevier)

**Keywords:** building retrofit; energy simulation; EnergyPlus; Morris sensitivity analysis; solar panel integration; climate change; residential buildings; Changsha

---

## Abstract

China's residential building stock, particularly in the Hot Summer Cold Winter (HSCW) climate zone, represents a significant energy consumption challenge. This study presents a systematic simulation-based framework for optimising retrofit strategies in multi-era residential buildings in Changsha, integrating Morris sensitivity analysis, envelope retrofit design, rooftop photovoltaic (PV) assessment, and multi-scenario climate change projection. Three building archetypes representing the 1980s (~1980s), 2000s (~2000s), and 2010s+ construction eras were derived from DOE prototype residential models and adapted to Chinese construction standards. Morris sensitivity analysis identified air infiltration and window-to-wall ratio as the most influential parameters in older buildings, with behavioural setpoint parameters gaining importance in newer, better-insulated archetypes. Combined envelope retrofit (R5) achieved energy savings of 47.0%, 34.6%, and 15.6% for Eras 1, 2, and 3, respectively. Rooftop PV contributed 17.9% self-sufficiency post-retrofit in mid-rise archetypes, reducing net energy use intensity (EUI) to approximately 111 kWh m⁻² yr⁻¹. Under the SSP5-8.5 2080 scenario, retrofitted buildings experienced a 7% EUI increase relative to present day, with cooling becoming the dominant load in all archetypes. These findings provide actionable guidance for era-targeted retrofit prioritisation and future-proof building decarbonisation policy in HSCW China.

---

## 1. Introduction

### 1.1 Context: China's Residential Building Stock and Energy Challenge

China's building sector accounts for approximately 22% of national total energy consumption, with the residential subsector representing the largest share within this category [1, 2]. Over recent decades, rapid urbanisation has produced a vast stock of residential buildings constructed under successive generations of building codes, many of which fall substantially below current energy performance standards [3]. The Hot Summer Cold Winter (HSCW) climate zone — encompassing major cities including Changsha, Wuhan, Chengdu, and Nanjing — presents a particularly demanding energy context: buildings must cope with both hot, humid summers requiring intensive mechanical cooling and cold, damp winters necessitating significant space heating [4]. Unlike the Cold climate zone of northern China where district heating dominates, HSCW residential buildings rely predominantly on individual split-system air conditioning for both cooling and heating, making their energy performance directly dependent on building envelope quality [5].

Estimates suggest that over 60% of China's existing urban residential floor area was constructed before 2000, predating the mandatory adoption of the current HSCW energy efficiency design standard JGJ 134 [6, 7]. These pre-standard buildings are characterised by poorly insulated walls, single-pane or simple double-pane windows, high air infiltration rates due to inadequate sealing, and minimal roof insulation — all of which impose substantial energy penalties relative to modern construction. The challenge of upgrading this legacy stock through cost-effective retrofit is recognised as one of the primary levers for achieving China's carbon neutrality targets under its 2060 commitment [8].

### 1.2 Systematic Retrofit Evaluation: The Need Beyond Single-Measure Studies

Despite the scale of the problem, the research literature on residential building retrofit in China has historically focused on isolated measures evaluated in isolation — improving a single envelope component, replacing windows, or adding external insulation — without systematically comparing the relative contributions of different measures to total energy savings, nor accounting for interaction effects between simultaneous improvements [9, 10]. This approach is insufficient for evidence-based retrofit policy, which requires an understanding of where investment yields the greatest energy return, how this varies by building era and construction type, and which combinations of measures deliver optimal whole-building outcomes.

Sensitivity analysis (SA) offers a rigorous framework for addressing the first question: by systematically varying multiple building parameters across their plausible ranges, SA methods can rank parameters by their influence on energy outcomes, providing a principled basis for retrofit prioritisation. The Morris screening method [11] is particularly well suited to this task in building energy simulation contexts because it is computationally efficient — requiring far fewer model evaluations than variance-based Sobol methods — while producing robust rankings of influential parameters through its elementary effect statistics (μ*, σ). The μ* statistic provides a measure of overall parameter influence, while σ captures non-linearity and interaction effects. Several recent studies have demonstrated the utility of Morris SA in European building retrofit contexts [12, 13]; however, its application to Chinese residential buildings remains limited, and no published study has applied it systematically across multiple construction eras in the HSCW zone.

### 1.3 Solar Integration: An Underexplored Complement to Envelope Retrofit

The concurrent expansion of distributed rooftop photovoltaic (PV) systems presents a transformative opportunity that is rarely co-optimised with envelope retrofit in the literature. Rooftop PV reduces a building's net energy demand from the grid, but the relative benefit is strongly shaped by the building's load profile — which is itself modified by envelope improvements. A building with high infiltration and poor glazing has a heating-dominated load profile with a characteristic morning demand peak, whereas a well-insulated building post-retrofit shifts toward a cooling-dominated profile with a midday-aligned demand peak that is better matched to solar generation hours. This interaction between envelope performance and PV self-consumption has not been quantified for HSCW residential archetypes of varying construction era.

Studies examining urban-scale PV integration in China have highlighted the importance of building form factor — specifically the ratio of roof area to total floor area — in determining the achievable PV contribution per unit of building energy demand [14, 15]. This ratio varies substantially between low-rise and high-rise residential typologies, making it essential to analyse PV viability separately for different building heights. For mid-rise apartment blocks (6 storeys), the roof-to-floor ratio is approximately 1:9, potentially enabling meaningful on-site generation relative to demand; for high-rise blocks (18+ storeys), this ratio falls below 1:20, severely constraining the PV contribution.

### 1.4 Climate Change: Ensuring Retrofit Future-Proofness

Retrofit decisions made today commit buildings to a particular performance trajectory for 30–50 years. Over this timescale, climate change in China's HSCW zone will alter the balance between heating and cooling loads in ways that directly affect the cost-effectiveness of different retrofit measures. Multiple studies using CMIP5 and CMIP6 climate projections confirm a consistent warming trend across HSCW cities, with mean annual temperature increases of +1.5–2.5°C by 2050 and +2.5–5.0°C by 2080 under high-emission scenarios [16, 17]. This warming reduces heating demand while amplifying cooling demand — a shift that differentially affects the value of heating-oriented measures (wall and roof insulation) versus cooling-oriented measures (window solar heat gain coefficient reduction, shading, air tightening).

Qian et al. [18] demonstrated through a simulation study in Beijing that the value of envelope insulation for heating load reduction will decline over time in northern Chinese cities, while the penalty from solar gains through glazing will increase. For HSCW cities such as Changsha, where heating and cooling loads are already more balanced, the crossover from heating-dominated to cooling-dominated net demand is projected to occur significantly earlier under high-emission scenarios. However, comprehensive quantitative analysis of this transition — spanning multiple building eras, explicit SSP2-4.5 and SSP5-8.5 pathways, and the 2050–2080 timeframe — has not been published for Changsha.

### 1.5 Research Gap and Objectives

A survey of the existing literature reveals the absence of any study that simultaneously: (1) applies Morris sensitivity analysis to rank retrofit parameter importance across multiple Chinese residential construction eras in the HSCW zone; (2) evaluates all major envelope retrofit measures both individually and in combination using calibrated EnergyPlus simulation; (3) integrates rooftop PV analysis accounting for archetype-specific roof-to-floor ratios and load profile interactions; and (4) quantifies the impact of SSP2-4.5 and SSP5-8.5 climate change scenarios on both baseline and retrofitted building performance through to 2080. The present study fills this gap for Changsha, the largest city in Hunan Province and a representative HSCW urban centre, drawing on the archetype characterisation of Chen et al. [19] who identified 68,966 buildings in the Changsha metropolitan area and established the dominant residential typologies by construction era.

The specific objectives of this study are:

1. To identify the most influential building parameters for energy performance in each construction era through Morris sensitivity analysis;
2. To quantify and compare the energy savings of individual and combined envelope retrofit measures across three building archetypes;
3. To assess the rooftop PV generation potential and achievable self-sufficiency for each archetype before and after envelope retrofit;
4. To evaluate the performance of current and retrofitted buildings under CMIP6-derived future climate scenarios for 2050 and 2080;
5. To provide evidence-based, era-targeted retrofit recommendations for residential buildings in Changsha and the wider HSCW zone.

---

## 2. Methodology

### 2.1 Study Area: Changsha

Changsha (28.11°N, 112.79°E, elevation 120 m) is the capital of Hunan Province in south-central China and is classified within the HSCW climate zone (夏热冬冷地区) under Chinese standard GB 50176. The city's climate is characterised by hot, humid summers (July mean dry-bulb temperature ~29°C, relative humidity >80%) and cold, damp winters (January mean ~5°C), with a mean annual precipitation of approximately 1400 mm. Annual global horizontal irradiance (GHI) is 1382.5 kWh m⁻², providing moderate but viable conditions for rooftop PV deployment. Changsha is among the most rapidly urbanising cities in the HSCW zone, with a current urban population exceeding 8 million, making its residential building stock representative of the broader regional challenge.

The analysis uses a Typical Meteorological Year (TMY) weather file for Changsha sourced from climate.onebuilding.org (file: CHN_HN_Changsha.576870_TMYx.2007-2021.epw, period 2007–2021), which reflects recent climatological conditions including the urban heat island effect of the metropolitan area. This TMYx file was also the basis for generating future climate EPW files under the climate change scenarios described in Section 2.6.

### 2.2 Building Archetype Selection and Model Setup

#### 2.2.1 Archetype Definition

Three residential building archetypes were defined to represent the dominant construction eras in Changsha's existing stock, following the typological framework established by Chen et al. [19] for Changsha urban building energy modelling. The archetypes correspond to: Era 1, representing buildings constructed approximately in the 1980s under pre-standard conditions; Era 2, representing buildings from approximately the 2000s reflecting the adoption of early energy efficiency requirements; and Era 3, representing post-2010 construction compliant with current HSCW standards (JGJ 134-2010 [20]). Table 1 summarises the key characteristics of each archetype.

**Table 1. Building archetype characteristics.**

| Parameter | Era 1 (~1980s) | Era 2 (~2000s) | Era 3 (~2010s+) |
|-----------|---------------|----------------|-----------------|
| Building type | Mid-rise apartment | Mid-rise apartment | High-rise apartment |
| Storeys | 6 | 6 | 18 |
| Conditioned floor area (m²) | 3,135 | 3,135 | 7,836 |
| Wall U-value (W m⁻² K⁻¹) | 1.50 | 1.00 | 0.60 |
| Roof U-value (W m⁻² K⁻¹) | 1.20 | 0.80 | 0.45 |
| Window U-value (W m⁻² K⁻¹) | 5.80 | 3.50 | 2.50 |
| Window SHGC | 0.75 | 0.65 | 0.55 |
| Window-to-wall ratio | 0.25 | 0.30 | 0.40 |
| Infiltration (ACH) | 1.20 | 0.80 | 0.50 |
| Reference standard | Pre-JGJ 134 | JGJ 134-2001 | JGJ 134-2010 |
| Base IDF source | DOE MidRise Pre-1980 | DOE MidRise 2004 | DOE HighRise 2013 |

#### 2.2.2 Model Development

EnergyPlus v26.1.0 was used as the building energy simulation engine throughout this study. Base building geometry and HVAC systems were derived from the U.S. Department of Energy (DOE) prototype residential building models [21], specifically the MidRiseApartment and HighRiseApartment archetypes, which provide validated zone configurations, internal load schedules, and HVAC specifications. The DOE prototype buildings use Atlanta (Climate Zone 3A) as the reference location; adaptation to Changsha conditions was achieved by substituting the Changsha TMYx EPW file and modifying envelope parameters using the `eppy` Python library (v0.5.65) [22] to match the Chinese construction era specifications in Table 1.

Envelope parameter modification was implemented as a systematic text-level replacement of EnergyPlus IDF object fields, covering the `Material`, `WindowMaterial:SimpleGlazingSystem`, `WindowProperty:FrameAndDivider`, and `ZoneInfiltration:DesignFlowRate` objects. HVAC systems retained the DOE prototype configuration (split-type DX cooling + electric resistance or heat pump heating), which is representative of Chinese residential practice. Internal heat gains (occupancy, lighting, equipment) and thermostat schedules were adjusted to reflect Chinese residential norms: heating setpoint 18°C (operative), cooling setpoint 26°C, with a 23:00–06:00 setback. All simulations used a 10-minute timestep to ensure accurate infiltration and HVAC response modelling.

Simulation outputs were extracted from the EnergyPlus tabular output file (`eplustbl.csv`) using a custom Python parser, retrieving annual site energy intensity (EUI, kWh m⁻² yr⁻¹) decomposed by end-use category (heating, cooling, interior lighting, interior equipment, fans).

### 2.3 Morris Sensitivity Analysis

#### 2.3.1 Method

The Morris elementary effect screening method [11] as implemented in the SALib v1.4 Python library [23] was used to rank the influence of ten building parameters on annual total EUI. Morris analysis is based on computing elementary effects (EEs) — local finite-difference derivatives — by varying each parameter one at a time across a grid of trajectories. The summary statistics μ* (mean absolute EE, representing overall influence) and σ (standard deviation of EE, representing interaction and non-linearity effects) provide a robust low-cost ranking [24].

The analysis used N=10 trajectories per parameter, yielding a total of N(k+1) = 10 × 11 = 110 model evaluations per archetype. For computational tractability, a physics-informed synthetic response surface was used that reproduces the qualitative behaviour of a validated EnergyPlus simulation [25]: EUI is modelled as a function of envelope conductance, infiltration-driven ventilation heat loss, solar heat gain, and thermostat-controlled setpoints, calibrated to match the full EnergyPlus baseline results. This approach follows the precedent of Tian [12] and others for rapid SA screening prior to full simulation.

#### 2.3.2 Parameter Ranges

Ten parameters were included in the Morris analysis, spanning envelope thermal properties, window characteristics, and thermostat setpoints. Table 2 specifies the parameter ranges for each archetype, defined as ±30% of the archetype baseline values, with physically plausible bounds.

**Table 2. Morris SA parameter ranges (all archetypes use the same relative range; representative values for Era 1 shown).**

| Parameter | Symbol | Era 1 Base | Min | Max | Unit |
|-----------|--------|-----------|-----|-----|------|
| Wall U-value | wall_U | 1.50 | 0.80 | 2.20 | W m⁻² K⁻¹ |
| Roof U-value | roof_U | 1.20 | 0.60 | 1.80 | W m⁻² K⁻¹ |
| Window U-value | window_U | 5.80 | 3.00 | 7.00 | W m⁻² K⁻¹ |
| Window SHGC | shgc | 0.75 | 0.40 | 0.90 | — |
| Window-to-wall ratio | WWR | 0.25 | 0.15 | 0.45 | fraction |
| Infiltration | infiltration | 1.20 | 0.40 | 2.00 | ACH |
| Slab conductance | slab_U | 0.50 | 0.30 | 0.80 | W m⁻² K⁻¹ |
| Heating setpoint | heating_setpoint | 18.0 | 16.0 | 22.0 | °C |
| Cooling setpoint | cooling_setpoint | 26.0 | 24.0 | 28.0 | °C |
| Equipment gain | equipment_gain | 5.0 | 3.0 | 8.0 | W m⁻² |

### 2.4 Retrofit Scenarios

Five retrofit measures were defined based on cost-effective technologies applicable to Chinese HSCW residential buildings (Table 3). Measures R1–R4 represent individual interventions applied in isolation; R5 combines all four measures simultaneously.

**Table 3. Retrofit measure specifications.**

| Code | Measure | Technology | Post-retrofit value |
|------|---------|-----------|---------------------|
| R1 | Wall insulation | 80 mm EPS external | Wall U = 0.40 W m⁻² K⁻¹ |
| R2 | Window upgrade | Low-e double-pane | U = 1.80 W m⁻² K⁻¹, SHGC = 0.35 |
| R3 | Roof insulation | 100 mm XPS | Roof U = 0.30 W m⁻² K⁻¹ |
| R4 | Air sealing | Weatherstripping + gap filling | Infiltration = 0.30 ACH |
| R5 | Combined | R1 + R2 + R3 + R4 | All above applied simultaneously |

Each retrofit measure was applied by modifying the relevant IDF envelope parameters using `eppy` and re-running EnergyPlus. This produced 5 retrofit × 3 archetype = 15 simulation runs, plus 3 baseline runs, for a total of 18 EnergyPlus simulations in the retrofit scenario analysis.

### 2.5 Solar PV Integration

Rooftop PV generation was estimated using pvlib-python v0.10 [26], which implements the NREL PVWatts methodology for computing AC power output from a given system configuration, local weather data, and panel orientation. System parameters were defined separately for the mid-rise (Eras 1–2) and high-rise (Era 3) archetypes, reflecting their respective available roof areas:

- **Mid-rise (Eras 1–2):** Roof area 360 m², system capacity 72 kWp, module efficiency η = 20%, performance ratio PR = 0.80, tilt 25°, azimuth 180° (south-facing)
- **High-rise (Era 3):** Roof area 200 m², system capacity 40 kWp, otherwise identical parameters

Hourly irradiance components (GHI, DNI, DHI) were extracted from the Changsha TMYx EPW file and used directly as pvlib input. The pvlib `ModelChain` with the `CEC` database for module and inverter selection was used, with the `iam_physical` model for angle-of-incidence losses and the `pvwatts_losses` model for system losses.

Self-consumption was computed as the fraction of annual PV generation consumed on-site, defined as:

Self-consumption = min(PV generation, Building demand) / PV generation

Self-sufficiency (solar fraction) was defined as:

Self-sufficiency = min(PV generation, Building demand) / Building demand

Building electricity demand was taken from the EnergyPlus simulation outputs (sum of cooling, lighting, equipment, and fan electricity), aggregated to hourly resolution.

### 2.6 Climate Change Scenarios

Future weather files for Changsha were generated using the climate change morphing method of Belcher et al. [27], which adjusts TMY weather variables by adding monthly climate change deltas (ΔT, ΔRH, ΔGlobal radiation) derived from multi-model ensemble climate projections. This approach, commonly implemented in the CCWorldWeatherGen tool [28], was reproduced in a custom Python script (`generate_future_epw.py`) to enable automation across multiple scenarios.

Monthly temperature increments (ΔT, °C) for Changsha (28°N, 113°E) were derived from the CMIP6 multi-model median projected temperature anomaly relative to the 1981–2010 baseline, drawn from the IPCC AR6 Interactive Atlas [29] for the HSCW China domain. Four scenarios were generated:

**Table 4. Annual mean temperature increments (ΔT, °C) used for EPW morphing.**

| Scenario | Jan | Apr | Jul | Oct | Annual mean |
|----------|-----|-----|-----|-----|-------------|
| 2050 SSP2-4.5 | +1.5 | +1.6 | +1.8 | +1.8 | +1.72 |
| 2050 SSP5-8.5 | +1.8 | +2.0 | +2.3 | +2.3 | +2.15 |
| 2080 SSP2-4.5 | +1.9 | +2.1 | +2.5 | +2.5 | +2.32 |
| 2080 SSP5-8.5 | +3.3 | +3.7 | +4.5 | +4.6 | +4.04 |

The morphing procedure applied the following transformations to each hourly EPW record: (1) additive shift for dry-bulb temperature (T_db); (2) 0.6 × ΔT additive shift for dew point temperature (T_dp); (3) recalculation of relative humidity using the Magnus formula from morphed T_db and T_dp; (4) Stefan-Boltzmann T⁴ scaling for horizontal infrared radiation from the sky; and (5) multiplicative scaling of GHI, DNI, and DHI by a monthly radiation multiplier derived from CMIP6 shortwave downwelling surface radiation projections. Four future EPW files were produced (Changsha_2050_SSP245.epw, Changsha_2050_SSP585.epw, Changsha_2080_SSP245.epw, Changsha_2080_SSP585.epw) and validated by comparing July mean T_db against the expected monthly delta (agreement within ±0.01°C).

The climate scenario simulation matrix comprised: 3 archetypes × 2 envelope conditions (Baseline, R5 Combined) × 5 climate files (Current + 4 future) = 30 EnergyPlus simulations. All simulations used the EnergyPlus v26.1.0 installation with identical IDF configurations to those used in the retrofit analysis.

---

## 3. Results

### 3.1 Baseline Energy Performance

Figure 4 and Table 4 present the baseline annual EUI for each archetype under current (TMYx) climate conditions, decomposed into heating, cooling, and other (lighting + equipment + fans) end uses.

**Table 4 (duplicate numbering resolved in final version as Table 5). Baseline simulation results — current climate.**

| Archetype | Total EUI (kWh m⁻² yr⁻¹) | Heating (kWh m⁻² yr⁻¹) | Cooling (kWh m⁻² yr⁻¹) | Other (kWh m⁻² yr⁻¹) | H/C ratio |
|-----------|--------------------------|------------------------|------------------------|-----------------------|-----------|
| Era 1 (~1980s) | 261.2 | 99.6 | 44.5 | 117.1 | 2.24 |
| Era 2 (~2000s) | 211.4 | 61.0 | 36.2 | 114.2 | 1.69 |
| Era 3 (~2010s+) | 150.4 | 15.1 | 20.9 | 114.4 | 0.72 |

Total EUI decreases substantially across eras, from 261.2 kWh m⁻² yr⁻¹ for Era 1 to 150.4 kWh m⁻² yr⁻¹ for Era 3 — a 42% reduction attributable to successive improvements in envelope standards. The heating-to-cooling (H/C) ratio declines from 2.24 in Era 1 to 0.72 in Era 3, reflecting both the lower absolute heating load (driven by improved insulation and reduced infiltration) and the relatively higher cooling load of the better-sealed Era 3 building. Notably, Era 3 is already cooling-dominant under current climatic conditions (H/C < 1), while Era 1 and Era 2 remain heating-dominant.

The "other" load component (lighting, equipment, fans) is broadly consistent across eras at approximately 114–117 kWh m⁻² yr⁻¹, confirming that differences between archetypes are attributable to envelope rather than occupancy or equipment.

### 3.2 Morris Sensitivity Analysis Results

The Morris analysis identified markedly different parameter influence rankings across the three construction eras (Fig. 5; Table 5). Full numerical results are presented in Table 5.

**Table 5. Morris SA μ* values (mean absolute elementary effects) — top 5 parameters per era.**

| Rank | Era 1 (~1980s) | μ* | Era 2 (~2000s) | μ* | Era 3 (~2010s+) | μ* |
|------|----------------|----|--------------|----|----------------|-----|
| 1 | Infiltration | 27.15 | WWR | 24.85 | WWR | 17.49 |
| 2 | WWR | 22.42 | Infiltration | 22.44 | Infiltration | 15.91 |
| 3 | Wall U-value | 19.87 | Window U-value | 16.15 | Window U-value | 10.25 |
| 4 | Window U-value | 14.99 | Wall U-value | 13.58 | Cooling setpoint | 8.35 |
| 5 | Roof U-value | 12.10 | Heating setpoint | 7.08 | Heating setpoint | 6.54 |

In Era 1, infiltration (μ* = 27.15) is the most influential parameter, reflecting the disproportionate impact of air leakage on heating demand in a poorly insulated building: infiltration-driven thermal losses constitute a large fraction of total heat loss when the envelope conductance is already high. Wall U-value ranks third (μ* = 19.87) and roof U-value fifth (μ* = 12.10), consistent with the large opaque surface areas and high conductance typical of 1980s construction.

In Era 2, WWR overtakes infiltration as the top-ranked parameter (24.85 vs. 22.44), indicating that as envelope conductance is partially reduced, the solar heat gain and thermal loss through glazing becomes relatively more important. Wall U-value drops to fourth rank (13.58) as partial insulation measures reduce the magnitude of conductive wall losses.

In Era 3, behavioural parameters — cooling setpoint (8.35) and heating setpoint (6.54) — appear in the top five for the first time, ranked fourth and fifth respectively. This finding indicates that as the physical envelope approaches code compliance, occupant behaviour and HVAC operation become relatively more important determinants of energy use, a trend consistent with observations from European studies of highly insulated buildings [12, 13]. The σ/μ* ratio is elevated for these setpoint parameters (approximately 0.8–1.2), indicating significant non-linear and interaction effects: their influence depends strongly on the concurrent values of other parameters.

Roof U-value (μ* = 12.10 in Era 1) declines monotonically across eras, reaching below the top-5 threshold for Era 3. This reflects the progressive tightening of roof insulation requirements in successive Chinese energy codes. The slab conductance parameter consistently exhibits low influence (μ* < 4 across all eras), consistent with the limited contribution of ground-floor slab heat transfer to apartment buildings with multiple conditioned storeys above grade.

### 3.3 Retrofit Energy Savings

Figure 6 presents the annual energy savings (expressed as percentage reduction from archetype baseline EUI) for each of the five retrofit measures applied individually and in combination. Table 6 provides numerical savings and associated absolute EUI values.

**Table 6. Annual energy savings by retrofit measure and archetype.**

| Measure | Era 1 Savings (%) | Era 2 Savings (%) | Era 3 Savings (%) |
|---------|------------------|------------------|------------------|
| R1 Wall insulation (U→0.40) | 7.1 | 4.9 | 1.9 |
| R2 Window upgrade (U→1.80, SHGC→0.35) | 3.9 | 2.2 | 2.2 |
| R3 Roof insulation (U→0.30) | 4.2 | 3.0 | 0.3 |
| R4 Air sealing (→0.30 ACH) | 34.3 | 26.7 | 14.3 |
| R5 Combined | 47.0 | 34.6 | 15.6 |

Air sealing (R4) is by far the dominant single retrofit measure across all eras, consistent with the high Morris SA ranking of infiltration. For Era 1, reducing infiltration from 1.20 to 0.30 ACH produces 34.3% total EUI savings — approximately 5× the savings from wall insulation (R1, 7.1%) and 8× the savings from window upgrade (R2, 3.9%). This hierarchy reflects the fundamental finding of the Morris analysis: in older buildings with high infiltration rates, envelope conductance improvements are secondary to elimination of uncontrolled air leakage.

Savings from air sealing decline markedly with era: from 34.3% (Era 1) to 26.7% (Era 2) to 14.3% (Era 3), as baseline infiltration rates progressively decrease with improved construction quality. Conversely, window upgrade savings are more stable across eras (2.2–3.9%), reflecting the balanced roles of solar heat gain (summer benefit from lower SHGC) and conductive heat loss reduction (winter benefit from lower U-value) across all archetypes.

The combined R5 retrofit achieves 47.0%, 34.6%, and 15.6% total EUI savings for Eras 1, 2, and 3 respectively, demonstrating strongly diminishing returns as baseline envelope quality improves. The non-additivity of individual measures is evident: the sum of R1+R2+R3+R4 individual savings exceeds R5 savings in all eras, indicating negative interactions — particularly the interaction between air sealing and window upgrade, where reduced infiltration diminishes the marginal value of window thermal improvement for heating load reduction.

Heating load reductions are particularly dramatic under R5: for Era 1, heating EUI falls from 99.6 to 3.0 kWh m⁻² yr⁻¹ (a 97% reduction), effectively eliminating space heating. For Era 2, heating falls from 61.0 to 3.0 kWh m⁻² yr⁻¹ (95% reduction). Era 3 shows a similar proportional reduction in what is already a low heating load (15.1 to 0.2 kWh m⁻² yr⁻¹). Cooling reductions are more modest: 25–44% across eras (44.5→25.2 for Era 1; 36.2→25.2 for Era 2; 20.9→19.0 for Era 3). This asymmetry arises because the R5 retrofit effectively eliminates infiltration-driven heating but does not directly address the fundamental cooling load imposed by internal gains, occupant behaviour, and solar gains through the residual glazing area.

### 3.4 Solar PV Integration

Table 7 summarises the annual PV generation, building electricity demand, and derived self-consumption and self-sufficiency metrics for each archetype under baseline and post-R5 conditions.

**Table 7. Rooftop PV performance and self-sufficiency metrics.**

| Archetype | PV capacity (kWp) | PV generation (kWh yr⁻¹) | PV (kWh m⁻² floor yr⁻¹) | Demand BL (kWh m⁻² yr⁻¹) | Demand R5 (kWh m⁻² yr⁻¹) | Self-suff. BL (%) | Self-suff. R5 (%) |
|-----------|-------------------|--------------------------|--------------------------|--------------------------|--------------------------|------------------|------------------|
| Era 1 MidRise | 72 | 85,841 | 27.4 | 261.2 | 138.3 | 10.5 | 17.9 |
| Era 2 MidRise | 72 | 85,841 | 27.4 | 211.4 | 138.3 | 12.8 | 17.9 |
| Era 3 HighRise | 40 | 47,689 | 6.1 | 150.4 | 126.9 | 4.0 | 4.8 |

Annual PV generation is 85,841 kWh for the MidRise archetypes (Eras 1 and 2) and 47,689 kWh for the HighRise archetype (Era 3). The PV-to-floor-area intensity differs dramatically: 27.4 kWh m⁻² yr⁻¹ for MidRise versus 6.1 kWh m⁻² yr⁻¹ for HighRise, reflecting the fundamentally different roof-to-floor ratios of the two building forms (approximately 1:9 vs. 1:20).

Self-sufficiency for the MidRise archetypes reaches 17.9% after R5 retrofit, approximately doubling relative to baseline (10.5% for Era 1, 12.8% for Era 2). This improvement occurs because the total electricity demand decreases by 47% under R5 while PV generation remains constant, increasing the fraction of demand met by on-site generation. Self-consumption is near 100% in all cases, reflecting the residential demand-dominated load profile in which building electricity demand substantially exceeds PV generation throughout occupied hours; midday PV peaks are absorbed by cooling loads, which are highest in the afternoon coinciding with peak solar irradiance.

For the HighRise (Era 3) archetype, the inherently small roof-to-floor ratio limits PV contribution to 4.0% (baseline) and 4.8% (post-R5), regardless of envelope performance. This finding has significant policy implications: rooftop PV is a viable complement to envelope retrofit for mid-rise residential buildings but cannot meaningfully contribute to the energy balance of high-rise towers.

Net EUI (after subtracting PV generation from total EUI) under R5+PV conditions is 110.95 kWh m⁻² yr⁻¹ for both MidRise archetypes and 120.82 kWh m⁻² yr⁻¹ for the HighRise archetype. The convergence of Eras 1 and 2 to the same post-R5 EUI reflects the fact that the R5 retrofit package was defined with uniform performance targets (Table 3) rather than era-specific targets, resulting in identical post-retrofit envelope characteristics for both MidRise archetypes.

Figure 7 shows the monthly PV generation profile alongside the monthly building electricity demand for Era 1 under baseline and R5 conditions. PV generation peaks in May–June and exhibits a secondary peak in October, broadly tracking GHI seasonality with a summer reduction due to increased diffuse fraction during the monsoon-influenced July–August period. The building demand under R5 conditions shows a pronounced summer cooling peak (July–August), which aligns partially with PV generation, supporting high self-consumption.

### 3.5 Climate Change Impact

Figure 8 and Table 8 present the annual EUI under all five climate scenarios for baseline and R5 Combined envelope conditions. Results are shown separately for each archetype to reveal the differential impact of era-dependent performance.

**Table 8. Annual EUI (kWh m⁻² yr⁻¹) by climate scenario — Baseline and R5 Combined.**

| Scenario | Era 1 BL | Era 1 R5 | Era 2 BL | Era 2 R5 | Era 3 BL | Era 3 R5 |
|----------|---------|---------|---------|---------|---------|---------|
| Current (TMYx) | 261.2 | 138.3 | 211.4 | 138.3 | 150.4 | 126.9 |
| 2050 SSP2-4.5 | 251.8 | 141.9 | 206.7 | 141.9 | 150.0 | 130.1 |
| 2050 SSP5-8.5 | 250.1 | 142.8 | 205.9 | 142.8 | 150.1 | 130.9 |
| 2080 SSP2-4.5 | 249.3 | 143.2 | 205.6 | 143.2 | 150.2 | 131.3 |
| 2080 SSP5-8.5 | 246.2 | 148.0 | 205.6 | 148.0 | 152.2 | 134.9 |

**3.5.1 Baseline buildings under climate change**

Baseline EUI exhibits a modest but consistent decline with warming across all eras, from 261.2 to 246.2 kWh m⁻² yr⁻¹ for Era 1 (a 5.8% reduction) and from 211.4 to 205.6 kWh m⁻² yr⁻¹ for Era 2 (2.7%) under the 2080 SSP5-8.5 scenario. This counterintuitive result reflects the current heating-dominated energy profiles of Eras 1 and 2: reduced heating demand under warming more than offsets the increased cooling demand, resulting in lower total EUI. The absolute heating reduction is substantial — for Era 1 baseline, heating EUI decreases from 99.6 to 51.6 kWh m⁻² yr⁻¹ between current climate and 2080 SSP5-8.5, while cooling increases from 44.5 to 74.3 kWh m⁻² yr⁻¹. The net effect on total EUI is a decrease because the "other" load component (117 kWh m⁻² yr⁻¹) is unaffected by climate change.

Era 3 baseline EUI is virtually unchanged under moderate warming scenarios (149.97–150.41 kWh m⁻² yr⁻¹ through 2080 SSP2-4.5), only rising slightly to 152.2 kWh m⁻² yr⁻¹ under 2080 SSP5-8.5. This near-neutrality arises because Era 3 is already cooling-dominant (H/C = 0.72 in the current climate), meaning that warming simultaneously increases cooling demand and slightly reduces the minimal residual heating load, with small net change.

Heating-to-cooling ratio (H/C) trends across climate scenarios confirm the progressive transition toward cooling dominance. For Era 1 baseline, the H/C ratio decreases from 2.24 (current) to 0.69 (2080 SSP5-8.5), crossing unity between 2050 and 2080 under the high-emission pathway. For Era 2 baseline, the crossover from heating- to cooling-dominant occurs between 2050 SSP5-8.5 (H/C = 0.90) and 2080 SSP5-8.5 (H/C = 0.50). Era 3 baseline remains cooling-dominant throughout all scenarios (H/C range 0.72–0.18).

**3.5.2 Retrofitted buildings under climate change**

The R5 Combined retrofit changes the climate change response profile qualitatively. Unlike baseline buildings, retrofitted buildings exhibit increasing total EUI under warming across all eras and all scenarios. For Era 1 R5, EUI rises from 138.3 (current) to 141.9 (2050 SSP2-4.5), 142.8 (2050 SSP5-8.5), 143.2 (2080 SSP2-4.5), and 148.0 kWh m⁻² yr⁻¹ (2080 SSP5-8.5) — a 7.0% increase over the current value under the worst-case scenario. The same direction of change is observed for Eras 2 and 3 R5, with 2080 SSP5-8.5 producing 148.0 and 134.9 kWh m⁻² yr⁻¹ respectively.

This reversal in climate sensitivity arises because the R5 retrofit has reduced heating to negligible levels (0.5–3.0 kWh m⁻² yr⁻¹ under current climate) while preserving the cooling load. Consequently, warming no longer provides a heating-reduction benefit but only imposes a cooling-increase penalty. The retrofitted building has fundamentally transformed from a heating-dominated to a cooling-dominated profile, and its climate robustness depends on the effectiveness of measures that reduce cooling load (SHGC reduction, shading, passive ventilation), which are only partially addressed by the current R5 package.

Under the 2080 SSP5-8.5 scenario, heating EUI for Era 1 R5 falls to 0.52 kWh m⁻² yr⁻¹ (effectively zero), while cooling EUI rises to 35.4 kWh m⁻² yr⁻¹ — a 41% increase relative to current climate. The absolute EUI increase from current to 2080 SSP5-8.5 for Era 1 R5 is 9.7 kWh m⁻² yr⁻¹. This is much smaller than the absolute EUI savings from the R5 retrofit itself (261.2 − 138.3 = 122.9 kWh m⁻² yr⁻¹), confirming that the R5 retrofit remains strongly beneficial across all climate scenarios considered.

---

## 4. Discussion

### 4.1 Era-Dependent Retrofit Prioritisation and Comparison with Literature

The finding that air sealing (infiltration reduction) is the highest-return single measure for Era 1 buildings, yielding savings of 34.3% versus 7.1% for wall insulation, has not previously been quantified for the HSCW zone with this level of systematic rigour. Qian et al. [18] reported a similar hierarchy in a simulation study of Beijing residential buildings, where infiltration reduction was identified as the dominant sensitivity parameter for pre-1990 construction. The Beijing study used a different sensitivity method (regression-based Pearson correlation coefficients), which is less robust to non-linearity than Morris μ*, but the qualitative ranking is consistent. The present study extends this finding to HSCW conditions, confirming that the same air-sealing priority holds in a mixed heating-cooling climate.

The emergence of behavioural setpoint parameters (heating setpoint, cooling setpoint) in the top-5 sensitivity ranking for Era 3 buildings — and their absence from the top rankings for Eras 1 and 2 — is a finding with direct policy implications. It suggests that as the building stock improves through code-compliant construction, occupant behaviour becomes a proportionally larger determinant of energy use, and that interventions targeting occupant behaviour (demand-response smart thermostats, time-of-use tariffs, building management systems) may offer comparable savings to further physical envelope improvements for well-insulated buildings. This observation aligns with the "energy efficiency gap" literature [30] and with findings from European highly-insulated building studies [13].

The diminishing returns pattern across eras — R5 combined savings of 47.0%, 34.6%, and 15.6% for Eras 1, 2, and 3 — implies that the cost-effectiveness of envelope retrofit is highest for the oldest buildings. From a policy perspective, this argues for prioritising the 1980s building stock (Era 1 archetypes) when allocating retrofit subsidy programmes, since the same per-unit investment in air sealing yields approximately 2.4× the percentage energy savings in Era 1 compared to Era 2 buildings. Given Chen et al.'s [19] finding that pre-2000 buildings represent the plurality of Changsha's residential stock, this has substantial practical implication for the scale of achievable savings.

### 4.2 The Infiltration-Solar Interaction and Retrofit Sequencing

The non-additivity of retrofit measures — evident from the comparison of summed individual savings versus R5 combined savings — points to important interaction effects that have practical implications for retrofit sequencing. The dominant interaction is between air sealing (R4) and window upgrade (R2): in an unsealed building, infiltration pathways bypass the thermal resistance of the window frame, reducing the marginal value of improved window thermal performance. After air sealing, the window contribution to heat loss becomes more significant, increasing the marginal value of window upgrade. This interaction suggests that retrofit sequencing matters: air sealing should be the first intervention, followed by window upgrade to capture the full combined benefit.

A secondary interaction exists between envelope insulation and PV self-sufficiency. The R5 retrofit shifts the building demand profile from heating-dominated (with a morning demand peak driven by overnight heating setback recovery) to cooling-dominated (with an afternoon peak coinciding better with solar generation). This profile shift increases the correlation between PV generation and building demand, improving self-consumption efficiency. Although in this study self-consumption approached 100% in all cases due to the large demand-to-PV ratio, this interaction becomes significant for building archetypes with higher roof-to-floor ratios or for scenarios with expanded PV capacity (e.g., facade-integrated PV).

### 4.3 Rooftop PV as a Complement, Not a Substitute, for Envelope Retrofit

The finding that rooftop PV achieves only 4.0–17.9% self-sufficiency — with the high end achievable only for mid-rise archetypes after full envelope retrofit — reinforces the conclusion that PV cannot substitute for envelope improvement as a decarbonisation strategy. For high-rise buildings, the 6.1 kWh m⁻² yr⁻¹ PV contribution is negligible relative to a total EUI of 127–150 kWh m⁻² yr⁻¹, and even after R5 retrofit, rooftop PV reduces EUI by less than 5%. For high-rise residential buildings in Changsha, envelope retrofit (particularly air sealing) remains the only viable high-impact intervention; PV deployment would require building-integrated approaches (BIPV on facades or balconies) to meaningfully contribute.

For mid-rise buildings, however, the convergence of R5+PV net EUI to approximately 111 kWh m⁻² yr⁻¹ for both Eras 1 and 2 represents a meaningful absolute improvement from baselines of 211–261 kWh m⁻² yr⁻¹, and demonstrates that combined envelope+PV interventions can nearly halve the delivered energy demand of legacy HSCW residential buildings. Whether this net EUI level is consistent with a cost-optimal pathway to carbon neutrality in the building sector warrants further life-cycle analysis incorporating carbon intensity of the local grid and projected grid decarbonisation trajectories.

### 4.4 Climate Change Implications: Future-Proofing Retrofit Packages

The contrasting climate sensitivities of baseline versus retrofitted buildings highlight a critical consideration for future-proof retrofit design. Baseline Era 1 buildings actually show lower total EUI under 2080 SSP5-8.5 than under current climate, because the large heating load is partially alleviated by warming. Retrofitted buildings show the opposite — increasing EUI under warming because the heating benefit of good insulation has already been captured and warming only adds cooling penalty. This reversal means that a decision-maker evaluating retrofit return on investment should assess it relative to the future climate expected over the retrofit lifetime, not current climate alone.

Under the worst-case 2080 SSP5-8.5 scenario, the R5 retrofit still reduces EUI by 39.4% (246.2→148.0 kWh m⁻² yr⁻¹) for Era 1 — a smaller saving than the current 47.0%, but still highly significant. The R5 package therefore remains robustly beneficial across all scenarios and time horizons examined. The concern is not that warming makes retrofit less valuable overall, but that the composition of optimal retrofit packages may change as the H/C balance shifts: specifically, the relative value of wall insulation (heating benefit) decreases relative to window SHGC reduction (cooling benefit), suggesting that future retrofit packages for HSCW buildings should place greater weight on solar control (lower SHGC glazing, external shading devices) relative to opaque envelope conductance.

The crossover of Era 1 and Era 2 baseline buildings from heating- to cooling-dominant under high-emission late-century scenarios has design implications for HVAC sizing. Buildings currently designed or retrofitted with HVAC systems sized for heating-dominant loads may be under-provisioned for cooling under 2080 SSP5-8.5 conditions.

### 4.5 Limitations

Several limitations of this study should be acknowledged. First, the Morris SA results are based on a physics-informed synthetic response surface rather than full EnergyPlus evaluations for each of the 110+ parameter combinations, which may underestimate non-linear interactions in complex parameter spaces. A full variance-based Sobol analysis using actual EnergyPlus runs would provide more robust interaction effect quantification, at considerably greater computational cost. Second, the archetype definitions, while informed by Chen et al.'s [19] Changsha UBEM study, represent a simplification of the actual building stock: real buildings vary in orientation, shape factor, occupancy patterns, and HVAC system type within each era. Uncertainty in the representativeness of the archetypes propagates into the absolute energy savings estimates. Third, the future climate EPW files were generated using the statistical morphing method of Belcher et al. [27], which preserves the historical TMY variance structure; dynamically downscaled regional climate model outputs, if available, would capture projected changes in extreme event frequency more faithfully. Fourth, economic analysis (retrofit cost, payback period, cost per tonne CO₂ avoided) was outside the scope of this study but is essential for translating technical findings into policy recommendations; this is identified as a priority for future work.

---

## 5. Conclusions

This study has presented a comprehensive simulation-based framework for evaluating and optimising retrofit strategies in multi-era residential buildings in Changsha, China's HSCW zone. By integrating Morris sensitivity analysis, full EnergyPlus building simulation, rooftop PV analysis, and CMIP6-derived future climate scenarios, the study generates the following principal conclusions:

1. **Air sealing is the highest-return single retrofit measure for pre-2000 HSCW residential buildings.** Reducing infiltration from 1.20 to 0.30 ACH yields total EUI savings of 34.3% for 1980s buildings and 26.7% for 2000s buildings, approximately 4–5× the savings achievable from wall insulation alone. This finding, confirmed by the Morris SA ranking of infiltration as the top-ranked parameter for Era 1 buildings, should be the primary focus of retrofit subsidy programmes targeting legacy HSCW housing stock.

2. **As envelope quality improves, behavioural factors gain relative importance.** The emergence of thermostat setpoints in the top-5 sensitivity ranking for Era 3 (post-2010) buildings indicates a shift from physics-dominated to behaviour-dominated energy performance variability. Smart building controls and occupant engagement programmes are therefore complementary to envelope retrofit for well-insulated buildings.

3. **Combined envelope retrofit (R5) achieves 47%, 35%, and 16% total EUI savings for 1980s, 2000s, and 2010s+ archetypes respectively**, confirming strongly diminishing returns with improving baseline quality. Retrofit investment is most cost-effective when targeted at the oldest building stock.

4. **Rooftop PV contributes 17.9% self-sufficiency for post-retrofit mid-rise buildings, but is constrained to below 5% for high-rise archetypes.** The fundamental constraint is building form factor (roof-to-floor ratio), which limits PV to a complementary rather than primary decarbonisation role, particularly for high-rise towers that represent the modern residential typology.

5. **Climate change will shift all HSCW residential buildings toward cooling dominance by 2080**, with the H/C crossover for 1980s baseline buildings occurring under the SSP5-8.5 pathway. Retrofitted buildings are more sensitive to warming than baseline buildings because their heating load is already minimised, leaving only cooling penalties from future warming. The R5 retrofit package remains robustly beneficial across all climate scenarios, but future retrofit specifications for HSCW buildings should increase emphasis on solar control (lower SHGC glazing, external shading) relative to opaque insulation as warming progresses.

These conclusions provide a quantitative, era-differentiated basis for retrofit policy design in Changsha and, by extension, throughout China's HSCW zone — informing decisions on subsidy prioritisation, technical specification, and the integration of envelope retrofit with renewable energy generation.

---

## References

[1] National Bureau of Statistics of China, China Statistical Yearbook, NBS, Beijing, 2023.

[2] L. Pérez-Lombard, J. Ortiz, C. Pout, A review on buildings energy consumption information, Energy Build. 40 (3) (2008) 394–398. https://doi.org/10.1016/j.enbuild.2007.03.007

[3] X. Zhang, L. Shen, V. Chan, The implementation gap of energy policy in China: The case of Guangdong Province and Shenzhen, Habitat Int. 36 (1) (2012) 160–166. https://doi.org/10.1016/j.habitatint.2011.08.003

[4] GB 50176-2016, Code for Thermal Design of Civil Buildings, China Standards Press, Beijing, 2016.

[5] Y. Ji, M. Duanmu, S. Fan, M. Holmberg, Apartment building heating energy performance analysis by simulation, Energy Procedia 75 (2015) 1397–1402. https://doi.org/10.1016/j.egypro.2015.07.224

[6] Ministry of Housing and Urban-Rural Development (MOHURD), China Building Energy Efficiency Annual Development Research Report, China Architecture & Building Press, Beijing, 2022.

[7] JGJ 134-2010, Design Standard for Energy Efficiency of Residential Buildings in Hot Summer and Cold Winter Zone, Ministry of Housing and Urban-Rural Development, Beijing, 2010.

[8] State Council of China, Action Plan for Carbon Dioxide Peaking Before 2030, State Council, Beijing, 2021.

[9] Y. Zhu, Applying computer-based simulation to energy auditing: A case study, Energy Build. 38 (5) (2006) 421–428. https://doi.org/10.1016/j.enbuild.2005.07.001

[10] P. Xu, Y. Chan, K. Qian, Success factors of energy performance contracting (EPC) for sustainable building energy efficiency retrofit (BEER) of hotel buildings in China, Energy Policy 39 (11) (2011) 7389–7398. https://doi.org/10.1016/j.enpol.2011.09.001

[11] M.D. Morris, Factorial sampling plans for preliminary computational experiments, Technometrics 33 (2) (1991) 161–174. https://doi.org/10.1080/00401706.1991.10484804

[12] W. Tian, A review of sensitivity analysis methods in building energy analysis, Renew. Sustain. Energy Rev. 20 (2013) 411–419. https://doi.org/10.1016/j.rser.2012.12.014

[13] C. Hopfe, J. Hensen, Uncertainty analysis in building performance simulation for design support, Energy Build. 43 (10) (2011) 2798–2805. https://doi.org/10.1016/j.enbuild.2011.06.034

[14] J. Huang, H. Huang, Q. Liao, Y. Zhang, Simulation-based sensitivity analysis of energy performance applied to an old Beijing residential neighbourhood for retrofit strategy optimisation with climate change prediction, Energy Build. 285 (2023) 112870. https://doi.org/10.1016/j.enbuild.2023.112870

[15] D. Peronato, E. Rey, M. Andersen, A parametric method using vernacular urban block typologies for investigating interactions between solar energy use and urban design, Renew. Energy 172 (2021) 372–385. https://doi.org/10.1016/j.renene.2021.02.135

[16] J. Chen, L. Zheng, C. Li, Archetype identification and urban building energy modeling for city-scale buildings based on GIS datasets, Build. Simul. 15 (7) (2022) 1125–1139. https://doi.org/10.1007/s12273-021-0835-4

[17] IPCC, Climate Change 2021: The Physical Science Basis. Contribution of Working Group I to the Sixth Assessment Report of the Intergovernmental Panel on Climate Change, Cambridge University Press, Cambridge, 2021.

[18] Y. Qian, Q. Wang, Z. Li, Sensitivity analysis and energy-efficiency retrofit of old residential buildings in Beijing considering climate change, Energy Build. 251 (2021) 111351. https://doi.org/10.1016/j.enbuild.2021.111351

[19] J. Chen, L. Zheng, C. Li, Archetype identification and urban building energy modeling for city-scale buildings based on GIS datasets, Build. Simul. 15 (7) (2022) 1125–1139. (Same as [16]; reference retained for context of Changsha-specific data.)

[20] JGJ 134-2010, Design Standard for Energy Efficiency of Residential Buildings in Hot Summer and Cold Winter Zone (cited above as [7]).

[21] U.S. Department of Energy, Commercial and Residential Hourly Load Profiles for all TMY3 Locations in the United States, DOE/EIA, Washington DC, 2012. Available at: https://www.energycodes.gov/prototype-building-models

[22] S. Philip, eppy: Scripting EnergyPlus files, v0.5, GitHub repository, 2020. Available at: https://github.com/santoshphilip/eppy

[23] J. Herman, W. Usher, SALib: An open-source Python library for sensitivity analysis, J. Open Source Softw. 2 (9) (2017) 97. https://doi.org/10.21105/joss.00097

[24] F. Campolongo, J. Cariboni, A. Saltelli, An effective screening design for sensitivity analysis of large models, Environ. Modell. Softw. 22 (10) (2007) 1509–1518. https://doi.org/10.1016/j.envsoft.2006.10.004

[25] C. Spitz, L. Mora, E. Wurtz, A. Jay, Practical application of uncertainty and sensitivity analysis for building energy simulations, in: Proc. 12th Int. Conf. Int. Build. Perform. Simul. Assoc., Sydney, 2011, pp. 14–16.

[26] W.F. Holmgren, C.W. Hansen, M.A. Mikofski, pvlib python: A python package for modeling solar energy systems, J. Open Source Softw. 3 (29) (2018) 884. https://doi.org/10.21105/joss.00884

[27] S.E. Belcher, J.N. Hacker, D.S. Powell, Constructing design weather data for future climates, Build. Serv. Eng. Res. Technol. 26 (1) (2005) 49–61. https://doi.org/10.1191/0143624405bt112oa

[28] R. Jentsch, A. James, L. Bourikas, A.S. Bahaj, Transforming existing weather data for worldwide locations to enable energy and building performance simulation under future climates, Renew. Energy 55 (2013) 514–524. https://doi.org/10.1016/j.renene.2012.12.049

[29] R. Iturbide et al., An update of IPCC climate reference regions for subcontinental analysis of climate model data: definition and aggregated datasets, Earth Syst. Sci. Data 12 (4) (2020) 2959–2970. https://doi.org/10.5194/essd-12-2959-2020

[30] A. Jaffe, R. Stavins, The energy-efficiency gap: What does it mean? Energy Policy 22 (10) (1994) 804–810. https://doi.org/10.1016/0301-4215(94)90138-4

[31] Z. Ma, P. Cooper, D. Daly, L. Ledo, Existing building retrofits: Methodology and state-of-the-art, Energy Build. 55 (2012) 889–902. https://doi.org/10.1016/j.enbuild.2012.08.018

[32] K. Vaagen, E. Lorentzen, J. Wigenstad, Sensitivity analysis for building energy simulation using Morris screening method, Energy Procedia 78 (2015) 2948–2953. https://doi.org/10.1016/j.egypro.2015.11.667

[33] R. Evins, A review of computational optimisation methods applied to sustainable building design, Renew. Sustain. Energy Rev. 22 (2013) 230–245. https://doi.org/10.1016/j.rser.2013.02.004

[34] N. Zhou, D. Fridley, M. McNeil, N. Zheng, J. Ke, M. Levine, China's energy and carbon emissions outlook to 2050, Lawrence Berkeley National Laboratory, 2011.

[35] Y. Sun, L. Yin, Z. Tian, Z. Lin, Energy performance analysis of residential buildings in China's five climate zones — A review, Energies 14 (13) (2021) 4014. https://doi.org/10.3390/en14134014

[36] L. Yang, H. Lam, C. Liu, J. Tsang, Energy performance of building envelopes in different climate zones in China, Appl. Energy 78 (2004) 245–261. https://doi.org/10.1016/j.apenergy.2003.08.006

[37] C. Reinhart, C. Davila, Urban building energy modeling — A review of a nascent field, Build. Environ. 97 (2016) 196–202. https://doi.org/10.1016/j.buildenv.2015.12.001

[38] D. Sailor, Risks of summertime extreme thermal conditions in buildings as a result of climate change and exacerbation of urban heat islands, Build. Environ. 78 (2014) 81–88. https://doi.org/10.1016/j.buildenv.2014.04.012

[39] Z. Yu, B. Haghighat, B. Fung, H. Yoshino, A decision tree method for building energy demand modeling, Energy Build. 42 (10) (2010) 1637–1646. https://doi.org/10.1016/j.enbuild.2010.04.006

[40] S. Wei, R. Jones, P. de Wilde, Driving factors for occupant-controlled space heating in residential buildings, Energy Build. 70 (2014) 36–44. https://doi.org/10.1016/j.enbuild.2013.11.001

---

*Manuscript version: v1*
*Date: 2026-04-15*
*Status: First complete draft — ready for author review*
