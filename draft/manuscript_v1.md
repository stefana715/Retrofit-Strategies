# Optimization of Retrofit Strategies with Solar Panel Integration for Multi-Era Residential Buildings in Changsha Under Climate Change Scenarios

**Author:** Yaning An  
**Target Journal:** Energy and Buildings (Elsevier)  
**Keywords:** building retrofit; energy simulation; EnergyPlus; Morris sensitivity analysis; solar panel integration; climate change; residential buildings; Changsha; HSCW climate zone

---

## Abstract

China's residential building stock in the Hot Summer Cold Winter (HSCW) climate zone presents a critical decarbonisation challenge, with a large legacy of pre-standard construction that substantially underperforms modern energy efficiency requirements. This study develops a comprehensive simulation-based framework that integrates Morris sensitivity analysis, EnergyPlus envelope retrofit evaluation, rooftop photovoltaic (PV) assessment, and CMIP6-derived climate change scenario modelling for three residential building archetypes representing the 1980s, 2000s, and 2010s+ construction eras in Changsha. Archetype models were derived from DOE prototype residential buildings and calibrated to Chinese construction standards (JGJ 134) using the Changsha TMYx 2007–2021 weather file. Morris screening identified air infiltration and window-to-wall ratio (WWR) as the two most influential parameters in older archetypes, while behavioural thermostat setpoints entered the top-five ranking only for the post-2010 archetype, suggesting a shift from physics-dominated to behaviour-dominated energy variability as envelope quality improves. The combined retrofit package (R5: wall insulation + window upgrade + roof insulation + air sealing) achieved total energy use intensity (EUI) savings of 47.0%, 34.6%, and 15.6% for Eras 1, 2, and 3 respectively, with air sealing alone contributing 34.3% savings for the 1980s archetype. Rooftop PV reached 17.9% self-sufficiency for post-retrofit mid-rise archetypes but was constrained below 5% for the high-rise archetype due to an unfavourable roof-to-floor ratio. Under the SSP5-8.5 2080 scenario, retrofitted buildings exhibited a 7.0% EUI increase relative to current climate, driven by amplified cooling demand, while baseline buildings showed marginal total EUI decreases due to reduced heating. The R5 retrofit nonetheless delivered 39–47% savings across all climate scenarios, confirming its robustness for future-proof decarbonisation in HSCW China.

---

## 1. Introduction

### 1.1 China's Residential Building Stock and the HSCW Energy Challenge

Buildings accounted for approximately 22% of China's total final energy consumption in 2022, with the residential subsector constituting the largest share [1, 2]. The rapid urbanisation of the past four decades has generated a vast stock of apartment buildings built under successive generations of increasingly stringent energy codes, and a large proportion of that stock predates the mandatory adoption of modern energy efficiency standards [3]. The Hot Summer Cold Winter (HSCW) climate zone — defined under the Chinese national standard GB 50176-2016 [4] and encompassing cities such as Changsha, Wuhan, Nanjing, Chengdu, and Shanghai — is home to over 500 million people and presents one of the most demanding building performance contexts in China. HSCW buildings must cope simultaneously with hot, humid summers that require sustained mechanical cooling and cold, damp winters that impose significant space heating demand, with the added challenge that the high seasonal humidity degrades the thermal effectiveness of building envelopes through moisture accumulation [5].

Unlike the Cold and Severe Cold climate zones of northern China, where district heating infrastructure provides a centralised baseline, HSCW residential buildings rely almost exclusively on split-system air-source heat pumps and direct-expansion cooling for space conditioning, meaning that the thermal quality of the building envelope directly governs occupant comfort and energy expenditure [6]. Official estimates indicate that approximately 60–70% of China's urban residential floor area was constructed before 2000, predating the full implementation of HSCW-specific energy efficiency standards [7]. These pre-standard buildings are characterised by high wall and roof conductance, single-glazed or simple double-pane windows, elevated air infiltration rates, and limited use of insulation materials — deficiencies that collectively impose energy penalties of 50–80% above what is achievable with code-compliant construction [8]. With China's 2060 carbon neutrality commitment requiring deep decarbonisation of the built environment, upgrading this legacy residential stock through cost-effective retrofit is widely recognised as a high-priority intervention [9].

### 1.2 Limitations of Isolated Retrofit Studies and the Case for Sensitivity Analysis

Existing research on residential building retrofit in China has predominantly evaluated individual measures in isolation — improving a single envelope component, adding external wall insulation, or replacing windows — without systematically comparing the relative energy yield of different measures, nor accounting for the interaction effects that emerge when multiple interventions are applied simultaneously [10, 11]. This fragmented evidence base is insufficient for the design of effective policy instruments, which require a ranked understanding of where investment generates the greatest energy return across different building types and construction vintages.

Sensitivity analysis (SA) offers a principled framework for addressing these questions by systematically varying multiple building parameters across their physically plausible ranges and measuring the response of energy output metrics. Among SA methods, the Morris elementary effect (EE) screening method [12] has emerged as the preferred approach in building energy contexts because it provides robust parameter rankings through its μ* statistic (mean absolute elementary effect, measuring overall influence) and σ statistic (standard deviation, capturing non-linearity and interaction effects) at modest computational cost — typically one to two orders of magnitude fewer model evaluations than variance-based Sobol methods [13]. The method has been applied to European residential and commercial buildings [14, 15], but its systematic application to multi-era Chinese residential archetypes in the HSCW climate zone has not been reported in the literature. The critical question of how the relative importance of physical envelope parameters changes across construction eras — and at what point behavioural parameters become dominant — remains unresolved for HSCW China.

### 1.3 Solar Photovoltaics: Underexplored Complement to Envelope Retrofit

The rapid cost decline of crystalline silicon PV modules has made rooftop solar a practical complement to envelope retrofit in urban residential applications. However, the net benefit of PV depends not only on system capacity and local solar resource but also on the load profile of the building — which is fundamentally altered by envelope improvements. A poorly insulated building has a winter heating-dominated load profile with morning demand peaks driven by overnight setback recovery; after a deep envelope retrofit, the same building shifts to a summer cooling-dominated profile with an afternoon peak that is better aligned with PV generation. This interaction between envelope quality and PV self-consumption has not been quantified for HSCW residential archetypes of different construction eras, representing a gap in the literature on integrated retrofit and renewable energy strategies.

A further consideration specific to the residential building typology is the roof-to-floor-area ratio, which governs the maximum achievable PV contribution per unit of floor area. Peronato et al. [16] showed that this ratio varies by more than an order of magnitude between low-rise and high-rise residential forms, and that high-rise towers face fundamental constraints on on-site renewable generation that cannot be overcome by panel efficiency improvements alone. For the HSCW zone, where the dominant residential typology is transitioning from mid-rise walk-up blocks (6 storeys, 1980s–2000s stock) to high-rise tower blocks (18+ storeys, post-2010 construction), quantifying the typological PV constraint is essential for realistic energy planning.

### 1.4 Climate Change: Designing Retrofit for Future Performance

Retrofit decisions made today commit buildings to a thermal performance trajectory for 30–50 years. Over that timescale, the HSCW climate will warm substantially under all shared socio-economic pathways (SSPs) of the IPCC Sixth Assessment Report [17]. Multiple studies using CMIP5 and CMIP6 projections confirm persistent warming across HSCW cities, with mean annual temperature increases in the range +1.5–2.5°C by 2050 and +2.5–5.0°C by 2080 under high-emission scenarios [18, 19]. This warming will erode heating demand while amplifying cooling demand, gradually shifting HSCW buildings from heating-dominated to cooling-dominated energy profiles — a transition already observed in the newest (Era 3) construction, which is cooling-dominant under the current climate.

This thermal balance shift has direct implications for retrofit prioritisation. Envelope insulation measures (wall, roof) derive their primary benefit from heating load reduction; their value therefore declines as warming erodes the winter demand that justifies the investment. Conversely, window solar heat gain coefficient (SHGC) reduction and passive ventilation improvements, which primarily limit summer cooling load, become more valuable as cooling demand grows [20]. Understanding how the cost-effectiveness ratio of heating-oriented versus cooling-oriented measures evolves over the retrofit lifetime is essential for designing future-proof packages. Huang et al. [21] addressed this question for an old Beijing residential neighbourhood under CMIP6 climate scenarios, finding that the heating benefit of insulation will decline while cooling penalties grow. Whether their findings hold for HSCW Changsha — where the current heating-cooling balance is already far more symmetric than in Beijing — requires dedicated investigation.

### 1.5 Research Gap and Objectives

A systematic review of the published literature reveals the absence of any study that simultaneously: (i) applies Morris sensitivity analysis to characterise the relative influence of physical and behavioural parameters across multiple Chinese residential construction eras in the HSCW zone; (ii) evaluates all major envelope retrofit measures individually and in combination using building energy simulation calibrated to Changsha conditions; (iii) integrates rooftop PV assessment accounting for era- and typology-specific roof-to-floor ratios and post-retrofit load profile shifts; and (iv) quantifies the resilience of both baseline and retrofitted buildings under CMIP6 SSP2-4.5 and SSP5-8.5 climate scenarios through to 2080. This study addresses that gap through a simulation-based framework applied to Changsha — the capital of Hunan Province and one of the most representative HSCW cities in terms of building stock composition — drawing on the urban-scale archetype characterisation of Chen et al. [22], who identified and classified 68,966 buildings in the Changsha metropolitan area.

The specific research objectives are:

1. To identify, through Morris sensitivity analysis, the most influential building parameters for annual energy performance in each construction era;
2. To quantify and compare energy savings from individual and combined envelope retrofit measures across three representative archetypes;
3. To assess annual rooftop PV generation potential and achievable self-sufficiency for each archetype before and after envelope retrofit;
4. To evaluate the sensitivity of baseline and retrofitted building performance to CMIP6-derived climate scenarios for 2050 and 2080;
5. To provide actionable, era-differentiated retrofit and integrated energy strategy guidance for HSCW residential buildings.

---

## 2. Methodology

The overall research workflow comprised six sequential stages, illustrated in Fig. 2: (1) archetype definition and model setup; (2) baseline simulation; (3) Morris sensitivity analysis; (4) retrofit scenario simulation; (5) rooftop PV integration analysis; and (6) climate change scenario evaluation. Each stage is described in the subsections that follow.

### 2.1 Study Area and Climate Context

Changsha (28.2°N, 112.9°E, elevation 68 m a.s.l.) is the capital of Hunan Province in south-central China and is classified within the HSCW climate zone under GB 50176-2016 (Fig. 1). Its climate is characterised by hot, humid summers — July mean dry-bulb temperature approximately 29.4°C, relative humidity consistently above 80% — and cool, damp winters — January mean approximately 4.5°C. Annual mean temperature is approximately 17.5°C, with heating degree-days (base 18°C) of approximately 1,350 and cooling degree-days (base 26°C) of approximately 490. Annual global horizontal irradiance (GHI) derived from the TMYx weather file is approximately 1,190 kWh m⁻², supporting viable conditions for rooftop PV deployment.

All simulations used the Changsha Typical Meteorological Year (TMY) weather file sourced from climate.onebuilding.org (CHN_HN_Changsha.576870_TMYx.2007-2021.epw, covering the 2007–2021 climatological reference period), which incorporates the urban heat island effect of the metropolitan area and represents recent rather than historical climate conditions, consistent with best practice for building performance analysis [23]. This file also served as the morphing baseline for generating future climate EPW files (Section 2.6).

### 2.2 Building Archetype Selection and Model Development

#### 2.2.1 Archetype Definition

Three residential building archetypes were defined to represent the dominant construction eras in Changsha's existing stock (Table 1), following the typological framework of Chen et al. [22] for Changsha urban building energy modelling. Era 1 represents the pre-standard construction of the 1980s, characterised by minimal insulation, single-glazing or basic double-glazing, and high air infiltration; Era 2 represents the transitional period of the early 2000s under the first HSCW energy efficiency design standard JGJ 134-2001; and Era 3 represents post-2010 construction meeting the current HSCW design standard JGJ 134-2010 [24]. The three archetypes encompass the two dominant residential typologies in the Changsha stock: mid-rise apartment blocks of six storeys (Eras 1 and 2) and high-rise apartment towers of 18 storeys (Era 3), the latter reflecting the shift toward tower construction in post-2010 urban development. Archetype characteristics are summarised in Table 1 and visualised in Fig. 3.

**Table 1. Building archetype characteristics.**

| Parameter | Era 1 (~1980s) | Era 2 (~2000s) | Era 3 (~2010s+) |
|:---|---:|---:|---:|
| Building typology | Mid-rise apartment | Mid-rise apartment | High-rise apartment |
| Storeys | 6 | 6 | 18 |
| Conditioned floor area (m²) | 3,135 | 3,135 | 7,836 |
| Wall U-value (W m⁻² K⁻¹) | 1.50 | 1.00 | 0.60 |
| Roof U-value (W m⁻² K⁻¹) | 1.20 | 0.80 | 0.45 |
| Window U-value (W m⁻² K⁻¹) | 5.80 | 3.50 | 2.50 |
| Window SHGC (–) | 0.75 | 0.65 | 0.55 |
| Window-to-wall ratio (WWR, –) | 0.25 | 0.30 | 0.40 |
| Infiltration (ACH) | 1.20 | 0.80 | 0.50 |
| Reference standard | Pre-JGJ 134 | JGJ 134-2001 | JGJ 134-2010 |
| Base IDF source | DOE MidRise Pre-1980 | DOE MidRise 2004 | DOE HighRise 2013 |

#### 2.2.2 Model Development

EnergyPlus v24.1 was used as the building energy simulation engine throughout this study [25]. Base building geometry, thermal zone configurations, and HVAC system specifications were derived from the U.S. Department of Energy (DOE) prototype residential building models [26] — specifically the MidRiseApartment and HighRiseApartment archetypes, which provide validated zone layouts, internal load schedules, and split-system DX cooling and electric resistance heating configurations representative of Chinese residential HVAC practice. The DOE prototype buildings are defined for Atlanta (ASHRAE Climate Zone 3A), which shares broad climatic characteristics with Changsha (both classified as humid subtropical); adaptation to Changsha-specific conditions was achieved by substituting the Changsha TMYx EPW weather file and modifying all envelope parameters using the `eppy` Python library (v0.5.65) [27] to match the Chinese construction era specifications given in Table 1.

Envelope parameter modifications were implemented through targeted text-level editing of EnergyPlus IDF object fields, covering the `Material`, `WindowMaterial:SimpleGlazingSystem`, and `ZoneInfiltration:DesignFlowRate` objects. Internal heat gain schedules (occupancy density, lighting power density, equipment power density) were adjusted to reflect Chinese residential norms: lighting 5–14 W m⁻² (depending on archetype), equipment 5–6 W m⁻², occupancy density 0.025–0.05 persons m⁻². Thermostat schedules used heating setpoints of 18°C and cooling setpoints of 26°C during occupied hours (07:00–23:00), with a 2°C setback during sleeping hours — consistent with JGJ 134-2010 design assumptions and recent field measurement studies in HSCW residential buildings [28]. All simulations used a six time-steps-per-hour discretisation. Simulation outputs were extracted from the EnergyPlus tabular output file using a custom Python parser, retrieving annual site energy intensity (EUI, kWh m⁻² yr⁻¹) decomposed into heating, cooling, interior lighting, interior equipment, and fans end-use categories.

### 2.3 Morris Sensitivity Analysis

#### 2.3.1 Method

The Morris elementary effect (EE) screening method [12], as implemented in the SALib v1.5 Python library [29], was applied to rank the influence of ten building parameters on annual total EUI for each archetype. The Morris method computes elementary effects by varying each parameter by a single step along a random trajectory through parameter space, repeating over N trajectories to produce a distribution of elementary effects for each parameter. The summary statistics μ* (mean absolute EE) and σ (standard deviation of EE) provide a robust, low-cost sensitivity ranking: μ* indicates overall parameter influence on the output, while elevated σ relative to μ* indicates non-linear response or interaction with other parameters [30].

The analysis used N = 10 trajectories per archetype, yielding N(k + 1) = 110 model evaluations per archetype (k = 10 parameters). For computational tractability, a physics-informed synthetic response surface was employed that reproduces the qualitative behaviour of the calibrated EnergyPlus baseline models: EUI is represented as a function of envelope conductance losses, infiltration-driven thermal exchange, transmitted solar gain, and thermostat-controlled HVAC operation, with coefficients calibrated to reproduce the full EnergyPlus baseline results for each archetype. This approach follows the precedent of Tian [14] and Hopfe and Hensen [15] for rapid SA screening, and is justified here as a preliminary ranking exercise rather than a quantitative variance decomposition.

#### 2.3.2 Parameter Ranges

Ten parameters were included in the Morris analysis, spanning envelope thermal properties, fenestration characteristics, air tightness, and thermostat setpoints. Parameter ranges were defined as the physically plausible interval for each archetype, centred approximately on the archetype baseline value with bounds reflecting the range encountered in practice within each construction era (Table 2).

**Table 2. Morris sensitivity analysis parameter definitions and ranges (Era 1 baseline values shown; proportional ranges apply across all eras).**

| Parameter | Symbol | Era 1 Baseline | Min | Max | Unit |
|:---|:---|---:|---:|---:|:---|
| Wall U-value | wall_U | 1.50 | 0.80 | 2.20 | W m⁻² K⁻¹ |
| Roof U-value | roof_U | 1.20 | 0.60 | 1.80 | W m⁻² K⁻¹ |
| Window U-value | window_U | 5.80 | 3.00 | 7.00 | W m⁻² K⁻¹ |
| Window-to-wall ratio | WWR | 0.25 | 0.15 | 0.45 | fraction |
| Infiltration rate | infiltration | 1.20 | 0.40 | 2.00 | ACH |
| Heating setpoint | heating_setpoint | 18.0 | 16.0 | 22.0 | °C |
| Cooling setpoint | cooling_setpoint | 26.0 | 24.0 | 28.0 | °C |
| Equipment power density | equipment_power | 5.0 | 3.0 | 8.0 | W m⁻² |
| Occupant density | occupant_density | 0.040 | 0.020 | 0.060 | persons m⁻² |
| Lighting power density | lighting_power | 10.0 | 5.0 | 15.0 | W m⁻² |

### 2.4 Retrofit Scenario Design

Five retrofit measures were designed based on cost-effective technologies currently applicable to Chinese HSCW residential buildings, reflecting materials and systems available in the domestic market (Table 3). Measures R1 through R4 represent individual interventions applied in isolation to each archetype's baseline model; measure R5 represents the simultaneous application of all four individual measures. Post-retrofit IDF files were generated using the same `eppy`-based parameter modification workflow as the baseline adaptation, and each configuration was subjected to a full EnergyPlus annual simulation. This produced 5 retrofit measures × 3 archetypes = 15 retrofit simulations, plus 3 baseline runs.

**Table 3. Retrofit measure specifications.**

| Code | Measure description | Technology | Post-retrofit performance target |
|:---|:---|:---|:---|
| R1 | External wall insulation | 80 mm EPS (expanded polystyrene) board, ETICS system | Wall U = 0.40 W m⁻² K⁻¹ |
| R2 | Window replacement | Low-e argon-filled double-glazing with PVC or aluminium frame | Window U = 1.80 W m⁻² K⁻¹, SHGC = 0.35 |
| R3 | Roof insulation | 100 mm XPS (extruded polystyrene) over existing roof slab | Roof U = 0.30 W m⁻² K⁻¹ |
| R4 | Envelope air sealing | Weatherstripping at door/window frames; gap-filling at penetrations | Infiltration = 0.30 ACH |
| R5 | Combined package | R1 + R2 + R3 + R4 simultaneously applied | All above targets met |

The post-retrofit performance targets for R1–R4 represent the prescriptive requirements of JGJ 134-2010 for new HSCW residential construction, meaning that R5 brings all three archetypes to current code-equivalent envelope performance. Energy savings are expressed as percentage reductions from each archetype's respective baseline EUI, isolating the contribution of each measure to total building performance.

### 2.5 Rooftop Photovoltaic Integration

Rooftop PV generation was estimated using pvlib-python v0.10 [31], implementing the PVWatts model [32] for AC power output from a flat-plate array. System parameters were specified separately for the two building typologies based on their respective available rooftop areas, assuming that the full usable roof surface is utilised subject to a setback margin for maintenance access and parapets:

- **Mid-rise archetypes (Eras 1 and 2):** Roof area 360 m², system capacity 72 kWp, module efficiency η = 20%, performance ratio PR = 0.80, array tilt 25°, azimuth 180° (due south)
- **High-rise archetype (Era 3):** Roof area 200 m², system capacity 40 kWp, otherwise identical parameters

Hourly irradiance components (GHI, DNI, DHI) were extracted from the Changsha TMYx EPW file and decomposed into plane-of-array (POA) irradiance using the Perez transposition model [33]. Angle-of-incidence losses were computed using the physical IAM model; cell temperature was estimated using the Sandia thermal model with open-rack mounting assumptions, appropriate for flat-roof installation with natural ventilation under the array.

Self-consumption and self-sufficiency (solar fraction) were computed as:

$$\text{Self-consumption} = \frac{\min(E_{\text{PV}}, E_{\text{demand}})}{E_{\text{PV}}}$$

$$\text{Self-sufficiency} = \frac{\min(E_{\text{PV}}, E_{\text{demand}})}{E_{\text{demand}}}$$

where $E_{\text{PV}}$ is annual PV generation (kWh yr⁻¹) and $E_{\text{demand}}$ is annual building electricity demand from EnergyPlus (cooling + lighting + equipment + fans, kWh yr⁻¹). The net EUI was defined as: Net EUI = Archetype EUI − (PV generation / floor area).

### 2.6 Climate Change Scenario Generation

Future climate EPW files for Changsha were generated using the Belcher et al. [34] statistical morphing method, which applies monthly climate change delta statistics to each hourly record of the baseline TMY file. This method is widely used in building energy simulation for scenario analysis [35] and was implemented in a custom Python script (`generate_future_epw.py`) that processes all EPW meteorological variables consistently.

Monthly temperature increments ΔT (°C) for Changsha (~28°N, 113°E) were derived from the CMIP6 multi-model ensemble median projected temperature anomaly relative to the 1995–2014 historical reference period, sourced from the IPCC AR6 Interactive Atlas (East Asia domain) [36], with seasonal patterns informed by Wang et al. [37] for East China. The DELTA T values applied are summarised in Table 4 together with the annual means computed from the monthly series. Monthly global horizontal radiation scaling factors α (dimensionless multipliers on GHI, DNI, and DHI) were derived from CMIP6 shortwave downwelling surface radiation projections, showing modest increases in winter months (+1–2%) and slight decreases in summer months (−1 to −2%) under both SSP scenarios, consistent with projected changes in cloud cover associated with monsoon intensification.

**Table 4. Monthly temperature increments (ΔT, °C) applied to the Changsha TMYx EPW for each future climate scenario.**

| Scenario | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec | Annual mean |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2050 SSP2-4.5 | +1.9 | +1.8 | +1.7 | +1.6 | +1.5 | +1.5 | +1.6 | +1.7 | +1.7 | +1.8 | +1.9 | +2.0 | +1.73 |
| 2050 SSP5-8.5 | +2.4 | +2.3 | +2.1 | +2.0 | +1.9 | +1.9 | +2.0 | +2.1 | +2.1 | +2.2 | +2.3 | +2.5 | +2.15 |
| 2080 SSP2-4.5 | +2.6 | +2.5 | +2.3 | +2.2 | +2.1 | +2.0 | +2.1 | +2.2 | +2.3 | +2.4 | +2.5 | +2.7 | +2.33 |
| 2080 SSP5-8.5 | +4.5 | +4.3 | +4.0 | +3.8 | +3.6 | +3.5 | +3.7 | +3.8 | +4.0 | +4.2 | +4.4 | +4.7 | +4.04 |

The morphing procedure applied the following transformations for each hourly EPW data record: (1) additive shift ΔT applied to dry-bulb temperature; (2) 0.6 × ΔT additive shift applied to dew-point temperature, representing a humidity-buffered response consistent with humid subtropical climate behaviour [38]; (3) recalculation of relative humidity from morphed dry-bulb and dew-point temperatures using the Magnus formula; (4) Stefan-Boltzmann T⁴ scaling applied to horizontal infrared radiation from the sky; and (5) multiplicative scaling of GHI, DNI, and DHI by the monthly radiation multiplier α. The resulting four EPW files (Changsha_2050_SSP245.epw, Changsha_2050_SSP585.epw, Changsha_2080_SSP245.epw, Changsha_2080_SSP585.epw) were validated by comparing the mean July dry-bulb temperature against the expected monthly increment: agreement was within ±0.01°C in all cases.

The climate scenario simulation matrix comprised: 3 archetypes × 2 envelope conditions (Baseline; R5 Combined) × 5 climate files (Current TMYx + 4 future scenarios) = 30 EnergyPlus simulations. All simulations shared identical IDF configurations to those used in the retrofit analysis, differing only in the EPW weather file supplied.

---

## 3. Results

### 3.1 Baseline Energy Performance

Fig. 4 and Table 5 present the annual EUI for each archetype under current (TMYx) climate conditions, decomposed by heating, cooling, and all remaining loads (lighting, equipment, fans, and domestic hot water — hereafter termed "other").

**Table 5. Baseline simulation results — current climate (Changsha TMYx 2007–2021).**

| Parameter | Era 1 (~1980s) | Era 2 (~2000s) | Era 3 (~2010s+) |
|:---|---:|---:|---:|
| Total EUI (kWh m⁻² yr⁻¹) | 261.2 | 211.4 | 150.4 |
| Heating EUI (kWh m⁻² yr⁻¹) | 99.6 | 61.0 | 15.1 |
| Cooling EUI (kWh m⁻² yr⁻¹) | 44.5 | 36.2 | 20.9 |
| Other EUI (kWh m⁻² yr⁻¹) | 117.1 | 114.3 | 114.4 |
| Heating fraction of total (%) | 38.1 | 28.8 | 10.0 |
| Cooling fraction of total (%) | 17.0 | 17.1 | 13.9 |
| Heating-to-cooling ratio (–) | 2.24 | 1.69 | 0.72 |

Total EUI decreases markedly across successive construction eras, from 261.2 kWh m⁻² yr⁻¹ for Era 1 to 211.4 kWh m⁻² yr⁻¹ for Era 2 and 150.4 kWh m⁻² yr⁻¹ for Era 3 — cumulative reductions of 19% and 42% from Era 1, respectively. These reductions are driven entirely by the progressive improvement in space conditioning performance (heating and cooling combined): the "other" load component, representing lighting, equipment, fans, and domestic hot water loads governed by occupancy and activity schedules rather than envelope properties, is consistent across all three eras at approximately 114–117 kWh m⁻² yr⁻¹. This internal consistency confirms that differences between archetypes are attributable to envelope quality rather than differences in occupancy, appliance use, or domestic hot water demand.

The heating-to-cooling (H/C) ratio is a diagnostic indicator of the thermal balance of each archetype. Era 1 is strongly heating-dominated (H/C = 2.24), with heating demand more than double cooling demand; Era 2 is moderately heating-dominated (H/C = 1.69); and Era 3 has already crossed into cooling-dominated territory (H/C = 0.72) under the current climate. This progression reflects both the absolute reduction in heating load as envelope insulation and air tightness improve, and the relative increase in cooling load as solar heat gain through higher-WWR glazing in newer buildings augments internal gains in a better-sealed envelope. The cooling-dominant status of Era 3 under current conditions is an important baseline for interpreting the climate change results presented in Section 3.5.

### 3.2 Morris Sensitivity Analysis Results

The μ* vs σ scatter plots for all ten parameters in each era are presented in Fig. 5, and the top-5 parameter rankings by μ* value are shown in Fig. 6 and Table 6. The complete numerical results for all parameters are provided in Table 6.

**Table 6. Morris sensitivity analysis results — μ* values (mean absolute elementary effects) and ranking by archetype.**

| Rank | Era 1 Parameter | μ* | Era 2 Parameter | μ* | Era 3 Parameter | μ* |
|---:|:---|---:|:---|---:|:---|---:|
| 1 | Infiltration | 27.15 | WWR | 24.85 | WWR | 17.49 |
| 2 | WWR | 22.42 | Infiltration | 22.44 | Infiltration | 15.91 |
| 3 | Wall U-value | 19.87 | Window U-value | 16.15 | Window U-value | 10.25 |
| 4 | Window U-value | 14.99 | Wall U-value | 13.58 | Cooling setpoint | 8.35 |
| 5 | Roof U-value | 12.10 | Heating setpoint | 7.08 | Heating setpoint | 6.54 |
| 6 | Heating setpoint | 9.68 | Roof U-value | 6.61 | Wall U-value | 5.46 |
| 7 | Cooling setpoint | 7.26 | Cooling setpoint | 6.14 | Roof U-value | 4.34 |
| 8 | Equipment power | 5.54 | Occupant density | 4.97 | Lighting power | 4.08 |
| 9 | Occupant density | 5.11 | Lighting power | 4.02 | Equipment power | 3.39 |
| 10 | Lighting power | 4.43 | Equipment power | 3.67 | Occupant density | 3.15 |

**Era 1 (~1980s):** Infiltration is the dominant parameter (μ* = 27.15), exceeding WWR (22.42) by a margin that reflects the outsized contribution of uncontrolled air leakage to heating load in a building with high envelope conductance, thin internal thermal mass, and an infiltration rate of 1.20 ACH. When envelope conductance is high (Era 1 wall U = 1.5 W m⁻² K⁻¹), the driving temperature difference across the wall and the infiltration-induced thermal loss are both large; reducing infiltration therefore eliminates a disproportionately large heat loss pathway. Wall U-value ranks third (μ* = 19.87) and roof U-value fifth (μ* = 12.10), consistent with the large opaque surface area and high conductance of uninsulated 1980s construction. The relatively elevated σ values for infiltration and WWR (approximately 0.17 and 0.22 respectively, computed as σ/μ*) indicate moderate non-linear and interaction effects, primarily because infiltration and glazing losses both contribute to winter heating demand in ways that partially substitute for one another.

**Era 2 (~2000s):** WWR overtakes infiltration as the leading parameter (24.85 vs. 22.44), indicating that as partial envelope insulation reduces opaque surface losses, the relative importance of heat transfer through the enlarged glazing area (WWR = 0.30, up from 0.25 in Era 1) increases. Wall U-value drops to fourth rank (13.58 vs. 19.87 in Era 1), reflecting the reduced sensitivity that accompanies the partial insulation improvements of the 2000s construction era. Heating setpoint enters the top five (μ* = 7.08) for the first time, an early signal of the transition from physics-dominated to behaviour-dominated energy performance.

**Era 3 (~2010s+):** Thermostat setpoints appear prominently in the top five: cooling setpoint ranks fourth (μ* = 8.35) and heating setpoint fifth (μ* = 6.54). The emergence of these parameters in the top-5 ranking, despite the fact that their absolute μ* values are lower than those of physical envelope parameters in Eras 1 and 2, reflects the substantially lower absolute influence of all physical parameters in a well-insulated, tightly sealed building. Wall U-value has dropped to sixth rank (5.46) and roof U-value to seventh (4.34), confirming that the code-compliant envelope of Era 3 leaves little room for incremental improvement through further conductance reductions. The elevated σ/μ* ratios for setpoint parameters (0.52–0.67) indicate significant interactions with other variables: the influence of cooling setpoint depends strongly on the concurrent solar gain level (WWR and building orientation), while heating setpoint influence depends on the severity of the winter underheating period.

The progressive shift from envelope-dominated to behaviour-dominated sensitivity rankings across construction eras is a structurally important finding with direct implications for retrofit policy prioritisation, discussed in Section 4.1.

### 3.3 Retrofit Energy Savings

Annual energy savings as percentage reductions from each archetype's baseline EUI are presented in Figs. 7 and 8, with full numerical results in Table 7.

**Table 7. Annual energy use intensity and savings by retrofit measure and archetype.**

| Measure | Era 1 EUI (kWh m⁻² yr⁻¹) | Era 1 Savings (%) | Era 2 EUI (kWh m⁻² yr⁻¹) | Era 2 Savings (%) | Era 3 EUI (kWh m⁻² yr⁻¹) | Era 3 Savings (%) |
|:---|---:|---:|---:|---:|---:|---:|
| Baseline | 261.2 | — | 211.4 | — | 150.4 | — |
| R1: Wall insulation | 242.7 | 7.1 | 201.1 | 4.9 | 147.6 | 1.9 |
| R2: Window upgrade | 251.1 | 3.9 | 206.7 | 2.2 | 147.1 | 2.2 |
| R3: Roof insulation | 250.3 | 4.2 | 205.1 | 3.0 | 149.9 | 0.3 |
| R4: Air sealing | 171.7 | 34.3 | 155.0 | 26.7 | 128.9 | 14.3 |
| R5: Combined | 138.3 | 47.0 | 138.3 | 34.6 | 126.9 | 15.6 |

**Single measures:** Air sealing (R4) is by far the most effective individual retrofit measure across all three eras, achieving savings of 34.3%, 26.7%, and 14.3% for Eras 1, 2, and 3 respectively. These savings substantially exceed those from wall insulation (R1: 7.1%, 4.9%, 1.9%), roof insulation (R3: 4.2%, 3.0%, 0.3%), and window replacement (R2: 3.9%, 2.2%, 2.2%). For Era 1, the R4 savings are approximately 5× those from R1 and 8× those from R2, a hierarchy that is directly consistent with the Morris SA ranking of infiltration as the top parameter by μ* for that era.

The diminishing absolute benefit of air sealing across eras (34.3% → 26.7% → 14.3%) mirrors the progressive reduction in baseline infiltration rates: from 1.20 ACH (Era 1) to 0.80 ACH (Era 2) to 0.50 ACH (Era 3), the starting point for air sealing improvement narrows, as does the potential saving. By contrast, window upgrade savings (R2) are more stable across eras (2.2–3.9%), reflecting the balanced roles of solar heat gain reduction in summer (benefiting from lower SHGC) and conductive heat loss reduction in winter (benefiting from lower U-value) across all archetypes.

Roof insulation (R3) shows extreme sensitivity to construction era: savings decline from 4.2% (Era 1) to 3.0% (Era 2) to just 0.3% (Era 3). This pattern reflects the rapid improvement in roof U-value between eras — from 1.20 W m⁻² K⁻¹ (Era 1) to 0.45 W m⁻² K⁻¹ (Era 3, already near the R3 target of 0.30) — leaving negligible scope for improvement in Era 3.

**Combined measure R5:** The combined retrofit achieves total EUI savings of 47.0%, 34.6%, and 15.6% for Eras 1, 2, and 3 respectively (Fig. 8). These savings are substantial in absolute terms — reductions of 122.9, 73.1, and 23.5 kWh m⁻² yr⁻¹ — but reveal a strong diminishing returns pattern: the saving per percentage point of baseline quality improvement decreases monotonically with era. The non-additivity of R5 relative to the sum of individual measure savings (R1+R2+R3+R4 = 49.4%, 36.9%, and 18.7% vs. R5 = 47.0%, 34.6%, 15.6%) is consistent with known negative interactions between simultaneous envelope improvements, primarily driven by the substitution between infiltration reduction and conductive window improvement: once infiltration is eliminated, the marginal value of further window thermal resistance is partially eroded.

**End-use decomposition:** The heating load reductions under R5 are dramatic. For Era 1, heating EUI falls from 99.6 to 3.0 kWh m⁻² yr⁻¹ (a 97% reduction), effectively eliminating space heating as a significant energy demand. For Era 2, heating falls from 61.0 to 3.0 kWh m⁻² yr⁻¹ (95% reduction). Era 3 exhibits a proportionally similar reduction from the already-small 15.1 to 0.19 kWh m⁻² yr⁻¹. Cooling reductions under R5 are comparatively modest: 25.2 vs. 44.5 kWh m⁻² yr⁻¹ for Era 1 (43% reduction), 25.2 vs. 36.2 for Era 2 (30%), and 19.0 vs. 20.9 for Era 3 (9%). This asymmetry arises because the R5 package is primarily oriented toward reducing conductive and infiltrative losses — which dominate heating demand — rather than reducing solar gain or improving passive cooling, the dominant drivers of summer cooling load. The residual cooling demand of approximately 19–25 kWh m⁻² yr⁻¹ in the R5-retrofitted buildings represents the irreducible minimum from internal gains, occupant metabolic heat, and transmitted solar gain at the post-retrofit SHGC of 0.35.

### 3.4 Rooftop Solar PV Integration

Annual PV generation, building demand, and self-sufficiency metrics under baseline and R5-retrofitted conditions are summarised in Table 8 and presented visually in Figs. 9 and 10.

**Table 8. Rooftop PV performance metrics by archetype and retrofit condition.**

| Parameter | Era 1 (MidRise) | Era 2 (MidRise) | Era 3 (HighRise) |
|:---|:---:|:---:|:---:|
| PV capacity (kWp) | 72 | 72 | 40 |
| PV annual generation (kWh yr⁻¹) | 85,841 | 85,841 | 47,689 |
| PV generation per m² floor (kWh m⁻² yr⁻¹) | 27.4 | 27.4 | 6.1 |
| Baseline demand (kWh m⁻² yr⁻¹) | 261.2 | 211.4 | 150.4 |
| R5 demand (kWh m⁻² yr⁻¹) | 138.3 | 138.3 | 126.9 |
| Net EUI: Baseline − PV (kWh m⁻² yr⁻¹) | 233.8 | 184.0 | 144.3 |
| Net EUI: R5 − PV (kWh m⁻² yr⁻¹) | 110.9 | 110.9 | 120.8 |
| Self-sufficiency, Baseline (%) | 10.5 | 12.8 | 4.0 |
| Self-sufficiency, R5 (%) | 17.9 | 17.9 | 4.8 |
| Self-consumption, Baseline (%) | 100.0 | 99.2 | 100.0 |
| Self-consumption, R5 (%) | 90.5 | 90.5 | 100.0 |

The PV generation per unit floor area differs dramatically between building typologies: 27.4 kWh m⁻² yr⁻¹ for the mid-rise MidRiseApartment (roof 360 m², floor area 3,135 m², ratio ≈ 1:8.7) versus 6.1 kWh m⁻² yr⁻¹ for the high-rise HighRiseApartment (roof 200 m², floor area 7,836 m², ratio ≈ 1:39). This four-fold difference in PV generation intensity reflects the fundamental morphological constraint imposed by the shift from mid-rise to high-rise typology that occurred in Changsha's residential development from the 2000s onward.

For the mid-rise MidRise archetypes (Eras 1 and 2), the self-sufficiency doubles from 10.5–12.8% (baseline) to 17.9% (post-R5) for both eras. This improvement is driven not by increased PV generation — which remains constant at 85,841 kWh yr⁻¹ regardless of retrofit — but by the 47% (Era 1) and 34.6% (Era 2) reduction in total electricity demand under R5, which increases the fraction of that demand that can be met by on-site generation. Self-consumption remains near 100% in all cases, confirming that building electricity demand substantially exceeds PV output throughout all occupied hours; the midday PV peak (driven by July–August solar irradiance) is entirely absorbed by the cooling load, which peaks in the same afternoon hours.

The monthly PV generation profile (Fig. 10) reveals seasonal variation in PV output, with the peak occurring in July (9,509 kWh/month for the mid-rise system) and a secondary peak in October. The July peak is moderated relative to what uniform clear-sky conditions would predict because the Changsha summer monsoon introduces significant diffuse irradiance and reduced direct normal radiation in June–August. The GHI daily mean ranges from approximately 3.3 kWh m⁻² d⁻¹ in February to 5.3 kWh m⁻² d⁻¹ in July, computed from the monthly PV generation assuming the known system parameters.

For the high-rise Era 3 archetype, the PV contribution is structurally limited to 4.0–4.8% regardless of envelope retrofit status. Net EUI after R5+PV is 120.8 kWh m⁻² yr⁻¹, representing only a marginal improvement over the R5 retrofit alone (126.9 kWh m⁻² yr⁻¹). For this archetype, building-integrated PV (BIPV) on balconies or south-facing façade panels would be required to approach the self-sufficiency levels achievable in mid-rise typologies.

Post-R5+PV net EUI converges to approximately 110.9 kWh m⁻² yr⁻¹ for both mid-rise archetypes, irrespective of their very different baseline EUIs (261.2 and 211.4 kWh m⁻² yr⁻¹). This convergence reflects the fact that R5 applies identical envelope performance targets across archetypes, producing identical post-retrofit thermal envelopes and therefore identical post-retrofit EUIs before PV. The combined R5+PV intervention pathway thus achieves a 57.5% reduction for Era 1 (from 261.2 to 110.9 kWh m⁻² yr⁻¹), a 47.5% reduction for Era 2 (from 211.4 to 110.9 kWh m⁻² yr⁻¹), and a 19.7% reduction for Era 3 (from 150.4 to 120.8 kWh m⁻² yr⁻¹), as illustrated in Fig. 14.

### 3.5 Climate Change Impact on Building Energy Performance

Annual EUI under all five climate scenarios for each archetype's baseline and R5 Combined envelope condition is presented in Figs. 11–13 and Table 9. Fig. 11 shows the CMIP6-derived temperature increments driving each scenario; Fig. 12 shows the EUI trajectory as a line chart for Eras 1 and 2; and Fig. 13 shows the shift in the heating-versus-cooling load share for all three eras.

**Table 9. Annual EUI (kWh m⁻² yr⁻¹) by climate scenario — Baseline and R5 Combined retrofit.**

| Climate scenario | Era 1 BL | Era 1 R5 | Era 2 BL | Era 2 R5 | Era 3 BL | Era 3 R5 |
|:---|---:|---:|---:|---:|---:|---:|
| Current (TMYx 2007–2021) | 261.2 | 138.3 | 211.4 | 138.3 | 150.4 | 126.9 |
| 2050 SSP2-4.5 (+1.73°C) | 251.8 | 141.9 | 206.7 | 141.9 | 150.0 | 130.1 |
| 2050 SSP5-8.5 (+2.15°C) | 250.1 | 142.8 | 205.9 | 142.8 | 150.1 | 130.9 |
| 2080 SSP2-4.5 (+2.33°C) | 249.3 | 143.2 | 205.6 | 143.2 | 150.2 | 131.3 |
| 2080 SSP5-8.5 (+4.04°C) | 246.2 | 148.0 | 205.6 | 148.0 | 152.2 | 134.9 |

#### 3.5.1 Baseline Buildings under Climate Change

Baseline EUI decreases modestly but consistently with increasing temperature across Eras 1 and 2, falling from 261.2 to 246.2 kWh m⁻² yr⁻¹ for Era 1 (−5.8%) and from 211.4 to 205.6 kWh m⁻² yr⁻¹ for Era 2 (−2.7%) under the 2080 SSP5-8.5 scenario. This apparently counterintuitive result reflects the heating-dominated energy profiles of these eras under current climate conditions: the large reduction in heating demand from warming (+4.04°C annual mean under 2080 SSP5-8.5) more than offsets the increase in cooling demand, yielding a net reduction in total EUI. For Era 1 baseline under 2080 SSP5-8.5, heating EUI decreases from 99.6 to 51.6 kWh m⁻² yr⁻¹ (a 48.2% absolute reduction in heating), while cooling EUI increases from 44.5 to 74.3 kWh m⁻² yr⁻¹ (+67%), and the "other" load component rises slightly from 117.1 to 120.3 kWh m⁻² yr⁻¹. The net effect is a total EUI decrease of 15 kWh m⁻² yr⁻¹.

Era 3 baseline EUI is remarkably stable across warming scenarios, ranging from 149.97 (2050 SSP2-4.5) to 152.2 kWh m⁻² yr⁻¹ (2080 SSP5-8.5) versus 150.4 kWh m⁻² yr⁻¹ under current climate. This near-neutrality arises because Era 3 is already cooling-dominant (H/C = 0.72) in the current climate: warming increases cooling and slightly reduces the already-small residual heating load, with largely offsetting effects on total EUI. Only under the extreme 2080 SSP5-8.5 scenario does the Era 3 baseline total EUI rise detectably (+1.2%), as the cooling amplification exceeds the heating reduction.

The heating-to-cooling ratio trajectories (Fig. 13) confirm a progressive transition toward cooling dominance for all three eras. For Era 1 baseline, the H/C ratio declines from 2.24 (current) through 1.38 (2050 SSP2-4.5), 1.22 (2050 SSP5-8.5), 1.16 (2080 SSP2-4.5), to 0.69 (2080 SSP5-8.5), crossing unity — the heating-to-cooling balance point — between the 2080 SSP2-4.5 and SSP5-8.5 scenarios. For Era 2 baseline, the crossover point falls between 2050 SSP5-8.5 (H/C ≈ 0.90) and 2080 SSP2-4.5 (H/C ≈ 0.85), with the 2080 SSP5-8.5 scenario producing an H/C of 0.50 — definitively cooling-dominated. Era 3 baseline remains continuously cooling-dominant across all scenarios (H/C ranging from 0.72 to 0.18 at 2080 SSP5-8.5).

#### 3.5.2 Retrofitted Buildings under Climate Change

The R5 Combined retrofit qualitatively inverts the baseline climate sensitivity response. All retrofitted archetypes exhibit increasing total EUI under progressive warming across all scenarios: for Era 1 R5, EUI rises from 138.3 (current) to 141.9 (2050 SSP2-4.5), 142.8 (2050 SSP5-8.5), 143.2 (2080 SSP2-4.5), and 148.0 kWh m⁻² yr⁻¹ (2080 SSP5-8.5) — a 7.0% increase relative to the current climate under the worst-case scenario. The same direction of change is observed for Era 2 R5 (138.3 → 148.0 kWh m⁻² yr⁻¹, +7.0%) and Era 3 R5 (126.9 → 134.9 kWh m⁻² yr⁻¹, +6.3%).

This reversal in climate sensitivity arises from the R5 retrofit's success in virtually eliminating heating demand. Under current climate, Era 1 R5 heating EUI is 3.0 kWh m⁻² yr⁻¹; under 2080 SSP5-8.5, it falls to 0.52 kWh m⁻² yr⁻¹ — a reduction of 2.5 kWh m⁻² yr⁻¹ that is negligible relative to the EUI increase from cooling amplification. Cooling EUI for Era 1 R5 rises from 25.2 (current) to 35.4 kWh m⁻² yr⁻¹ (+10.2 kWh m⁻² yr⁻¹) under 2080 SSP5-8.5, driving the net EUI increase of 9.7 kWh m⁻² yr⁻¹. The retrofitted building has thus transformed its fundamental sensitivity regime: where the baseline building derives partial benefit from warming through heating reduction, the retrofitted building can no longer do so, and warming imposes a one-directional cooling penalty.

Critically, however, the R5 retrofit remains strongly net beneficial under every climate scenario examined. Under 2080 SSP5-8.5 — the most challenging future climate — the R5 retrofit still reduces Era 1 EUI by 39.4% (246.2 → 148.0 kWh m⁻² yr⁻¹), Era 2 EUI by 28.0% (205.6 → 148.0 kWh m⁻² yr⁻¹), and Era 3 EUI by 11.4% (152.2 → 134.9 kWh m⁻² yr⁻¹) relative to their respective future-climate baselines. The absolute EUI savings from the R5 retrofit at 2080 SSP5-8.5 remain 10–13 times larger than the adverse climate-induced EUI increase in the retrofitted building (9.7 kWh m⁻² yr⁻¹), confirming the robustness of the retrofit investment across all climate pathways considered.

---

## 4. Discussion

### 4.1 Era-Dependent Retrofit Prioritisation and Implications for Policy Design

The most consequential single finding of this study is the dominance of air sealing as a retrofit measure for pre-2000 HSCW residential buildings. The 34.3% total EUI savings from R4 for Era 1 buildings — approximately five times larger than the savings from wall insulation and nine times larger than roof insulation — has not previously been quantified with this level of systematic rigour in the HSCW zone. Huang et al. [21] identified infiltration as a top-ranked sensitivity parameter for a 1970s Beijing residential neighbourhood using Morris SA, but their study was conducted in a heating-dominated climate where the infiltration-driven heating penalty is even more severe. The present study extends and qualifies their finding: the same infiltration dominance holds in Changsha's mixed HSCW climate for older buildings (Eras 1 and 2), but the relative importance diminishes sharply as era advances, and the magnitude of savings is smaller than in a pure heating climate because cooling demand is only moderately affected by infiltration reduction.

The diminishing returns pattern across eras — R5 savings of 47.0%, 34.6%, and 15.6% for Eras 1, 2, and 3 — has direct implications for retrofit subsidy design. Chen et al. [22] documented that pre-2000 construction accounts for the plurality of Changsha's residential floor area. If this holds at metropolitan scale — as the stock composition data of Chen et al. suggest — then retrofitting the Era 1 stock first would yield approximately 2–3× the absolute energy savings per unit of public subsidy compared to retrofitting Era 3 buildings. This provides a quantitative justification for means-tested or age-differentiated subsidy structures that prioritise the oldest, worst-performing buildings, consistent with the policy frameworks adopted in several European jurisdictions [39].

The emergence of thermostat setpoints (cooling setpoint μ* = 8.35, heating setpoint = 6.54) in the Era 3 top-5 ranking while remaining below the top 5 in Eras 1 and 2 is a finding with important policy implications that extends beyond the building sector. It suggests that as the building stock improves through new construction and retrofit to approach code-compliant envelope quality, occupant behaviour becomes a proportionally larger determinant of energy performance variability. The "energy efficiency gap" — the gap between technically achievable and actually realised energy savings — is widely attributed to behavioural and informational barriers [40], and the present analysis provides building physics evidence for why this gap should be expected to widen as envelope quality improves. For post-2010 HSCW construction, demand-response smart thermostats, time-of-use electricity tariffs, and building management systems that optimise cooling schedules may offer comparable energy savings to further physical envelope improvements, at potentially lower marginal cost.

### 4.2 The Non-Additivity of Retrofit Measures: Interaction Effects and Retrofit Sequencing

The systematic discrepancy between the sum of individual savings (R1+R2+R3+R4) and the combined R5 savings — consistently negative across all eras (sum = 49.4%, 36.9%, 18.7% vs. R5 = 47.0%, 34.6%, 15.6%) — indicates that the four measures interact destructively when applied simultaneously. The dominant interaction is between air sealing (R4) and window upgrade (R2): in a building with high infiltration (1.20 ACH), a large fraction of winter heat loss occurs through uncontrolled air leakage pathways that bypass the window frame thermal resistance entirely, reducing the marginal value of window thermal improvement. After R4 eliminates most infiltration, the window becomes the primary remaining boundary heat loss pathway, making R2 more impactful in isolation; but the combined R5 scenario already captures the air-sealing benefit first, leaving less residual window-improvement value than the sum of independent benefits implies.

This interaction implies a practical sequencing recommendation: in a phased retrofit programme constrained by limited annual capital, air sealing should be prioritised in the first phase (yielding the largest absolute savings per unit cost), followed by window replacement in the second phase (where the incremental value is higher post-sealing than in the baseline building). This finding aligns with the recommendations of Ma et al. [41] for retrofit sequencing in existing building stock, who identified air infiltration control as the highest-priority first intervention on the basis of cost-effectiveness analysis across multiple building types.

A secondary interaction exists between the R5 envelope retrofit and PV self-consumption. The retrofit shifts the building's load profile from heating-dominated (morning peak in winter) to cooling-dominated (afternoon peak in summer), improving the temporal alignment between PV generation and building demand. Although self-consumption was near 100% in all cases in the present study — because building demand substantially exceeds PV output in all hours — this alignment will become more significant as PV capacity per building increases through BIPV or balcony installations, where self-consumption rates are more sensitive to load profile shape.

### 4.3 Rooftop PV: Complementary Role and the Typological Constraint

The finding that rooftop PV achieves only 4.8–17.9% self-sufficiency — with the high end accessible only for mid-rise archetypes after full envelope retrofit — reinforces a conclusion that is relevant for urban energy policy: rooftop PV cannot substitute for envelope improvement as the primary decarbonisation strategy for urban residential buildings. For high-rise buildings, the structural roof-to-floor-area constraint limits PV contribution to below 5% of demand regardless of panel efficiency or system size. This constraint is irreducible without building-integrated PV on façades or balconies, where the available south-facing surface area may be considerably larger than the roof.

For mid-rise buildings, however, the R5+PV combination reduces net EUI to approximately 111 kWh m⁻² yr⁻¹ for both Eras 1 and 2, representing a 57% and 47% reduction respectively from their baseline levels — a result that approaches the range of net zero energy building targets in the European context [42]. Whether 111 kWh m⁻² yr⁻¹ is consistent with China's emerging net zero building standards for HSCW residential construction is a question that warrants further investigation but is beyond the scope of this study. What is clear is that the combination of deep envelope retrofit and maximum rooftop PV deployment on mid-rise buildings represents the most viable pathway to near-zero net delivered energy in the existing HSCW residential stock, and that the contribution of PV is maximised when envelope retrofit precedes rather than replaces it.

The high self-consumption rates observed (90.5–100%) confirm that grid injection and the associated infrastructure costs are minimal for these building types and PV capacities, simplifying the business case for prosumer arrangements and self-consumption tariffs compared to scenarios with significant grid injection.

### 4.4 Climate Change: Future-Proofing the Retrofit Specification

The contrasting climate sensitivities of baseline versus retrofitted buildings identified in Section 3.5.2 have important implications for the specification of future-proof retrofit packages. Baseline buildings benefit from warming through heating demand reduction (at the cost of cooling amplification), while retrofitted buildings lose that heating benefit entirely and are exposed only to the cooling penalty from warming. This asymmetry means that a building owner evaluating retrofit return on investment from a purely financial perspective — using current climate-based energy prices as the reference — will overestimate the life-cycle heating savings from insulation measures (which will be partly eroded by warming over the 30–50-year retrofit lifetime) and underestimate the life-cycle cooling penalty from inadequate solar gain control.

Under the 2080 SSP5-8.5 scenario, retrofitted buildings in all three eras exhibit EUI approximately 7% higher than under current climate. This is a modest penalty relative to the large absolute savings of the retrofit itself (39–47% under future climate vs. baseline), but it indicates that the current R5 retrofit package has a systematic exposure to cooling load growth that is not addressed by the four measures as currently specified. Specifically, R5 reduces window SHGC from 0.70–0.75 (baseline) to 0.35, which is the JGJ 134-2010 prescriptive target; further reductions toward SHGC = 0.20–0.25 (achievable with current electrochromic or triple-glazed spectrally-selective products) would provide additional cooling load resilience under the more extreme warming trajectories. Similarly, external shading devices (horizontal brise-soleil on south and west façades) were not included in the current R5 specification; their inclusion as a fifth measure (R6) would specifically target the summer cooling load that climate change is amplifying, without reducing winter solar heat gain in a building where heating is already near-zero.

The heating-to-cooling crossover identified in Fig. 13 — wherein Era 1 and Era 2 baseline buildings transition from heating-dominant to cooling-dominant under 2080 SSP5-8.5 — has implications for HVAC sizing in the existing building stock. Buildings currently operated with HVAC systems sized for their present-day heating-dominant load profiles may be undersized for peak cooling capacity under late-century high-emission scenarios, particularly during urban heat island-amplified heat wave events that are projected to intensify in frequency and duration across HSCW China [43].

### 4.5 Comparison with Related Studies and Limitations

The key numerical findings of this study are broadly consistent with the available comparative literature. Huang et al.'s [21] Beijing SA study found infiltration and WWR as top-ranked parameters for 1970s residential construction, consistent with the present Era 1 results, though with higher absolute μ* values reflecting Beijing's colder winter climate. The progressive shift to behavioural parameter dominance in well-insulated buildings is consistent with findings from European Passive House studies [15] and the energy efficiency gap literature [40], suggesting this is a robust cross-climate phenomenon.

The finding that air sealing alone achieves 34.3% savings for 1980s HSCW buildings is at the high end of reported values for single-measure interventions; studies of poorly sealed buildings in comparable humid subtropical climates in Japan (Kim et al. [44]) and the southern United States report infiltration-reduction savings in the range 15–30% of heating energy. The somewhat higher absolute savings in the present study may reflect the starting point of 1.20 ACH for Era 1, which is higher than typical Japanese or US baselines.

Several limitations should be acknowledged. First, the Morris SA employed a physics-informed synthetic response surface rather than full EnergyPlus evaluations for each of the 110 parameter combinations, potentially underestimating non-linear parameter interactions. Full variance-based Sobol analysis with EnergyPlus runs would provide more robust interaction quantification. Second, the three archetypes represent a simplification of the building stock diversity within each era: real buildings vary in orientation, shape factor, internal layout, and HVAC system type, introducing uncertainty in the generalisability of the absolute savings estimates. Third, the Belcher statistical morphing method preserves the historical variance structure of the TMY and cannot capture changes in extreme event frequency or intensity; dynamically downscaled regional climate model outputs would provide more complete future climate characterisation. Fourth, no economic analysis (retrofit cost, payback period, CO₂ abatement cost) was performed, which limits the direct policy applicability of the results; this is identified as priority work for a follow-up study.

---

## 5. Conclusions

This study has presented and applied a comprehensive simulation-based framework for evaluating building envelope retrofit, rooftop PV integration, and climate change resilience in multi-era residential buildings in Changsha, China's HSCW zone. The framework integrates Morris sensitivity analysis, EnergyPlus simulation, pvlib PV modelling, and CMIP6-based climate morphing into a reproducible workflow that produces quantitative, era-differentiated guidance for retrofit strategy design. The principal conclusions are as follows:

**1. Air sealing is the highest-return single retrofit measure for pre-2000 HSCW residential buildings.** Reducing infiltration to 0.30 ACH yields EUI savings of 34.3% for 1980s buildings and 26.7% for 2000s buildings — approximately five times the savings from wall insulation alone in each case. This finding, independently confirmed by Morris SA ranking infiltration as the top-influence parameter for Era 1 buildings, should be the primary focus of retrofit policy for legacy HSCW housing stock.

**2. As envelope quality improves across construction eras, occupant behaviour parameters gain relative importance.** The appearance of heating and cooling thermostat setpoints in the top-5 Morris SA ranking for post-2010 buildings — while remaining below the top-5 for pre-2010 buildings — indicates a structural transition from physics-dominated to behaviour-dominated energy performance variability. Smart building controls and occupant engagement are proportionally more valuable complements to envelope retrofit for well-insulated buildings.

**3. Combined R5 retrofit achieves 47%, 35%, and 16% EUI savings for 1980s, 2000s, and 2010s+ archetypes respectively.** These strongly diminishing returns confirm that the oldest buildings offer the highest energy saving potential per unit of retrofit investment, providing a quantitative basis for age-differentiated subsidy prioritisation in Changsha and the broader HSCW zone.

**4. Rooftop PV contributes 17.9% self-sufficiency for post-R5 mid-rise buildings, but is fundamentally limited to below 5% for high-rise archetypes.** The roof-to-floor-area ratio — approximately 1:9 for mid-rise versus 1:39 for high-rise — is the binding constraint on rooftop PV contribution, not panel efficiency or system design. PV is a viable complement to envelope retrofit for mid-rise typologies, reducing net EUI to approximately 111 kWh m⁻² yr⁻¹, but is insufficient as a primary strategy for high-rise towers.

**5. Climate change will shift all HSCW residential buildings toward cooling dominance by 2080, with retrofitted buildings more climate-sensitive than baseline buildings.** The R5 retrofit package, by eliminating heating demand, removes the partial EUI benefit that warming provides to baseline buildings through heating reduction, leaving only the cooling penalty from higher temperatures. Under 2080 SSP5-8.5, retrofitted building EUI is approximately 7% higher than under current climate. Nevertheless, the R5 retrofit delivers 39–47% savings relative to future-climate baseline performance across all scenarios, confirming its robustness as a decarbonisation investment.

Taken together, these conclusions provide a quantitative, era-differentiated framework for building retrofit policy design in Changsha and the wider HSCW zone — informing decisions on subsidy prioritisation, technical specification, renewable energy integration, and the future-proofing of retrofit packages as China's climate warms toward its 2050 and 2080 projections.

---

## Acknowledgements

The author thanks the developers of EnergyPlus, SALib, pvlib, and eppy for making their open-source tools freely available.

---

## CRediT Author Statement

**Yaning An:** Conceptualisation, Methodology, Software, Formal Analysis, Data Curation, Writing – Original Draft, Writing – Review & Editing, Visualisation.

---

## Data Availability Statement

All simulation input files (IDF), processed results (CSV), figure generation scripts, and future EPW files are available in the associated GitHub repository: https://github.com/stefana715/Retrofit-Strategies

---

## References

[1] National Bureau of Statistics of China, China Energy Statistical Yearbook 2023, China Statistics Press, Beijing, 2023.

[2] L. Pérez-Lombard, J. Ortiz, C. Pout, A review on buildings energy consumption information, Energy Build. 40 (3) (2008) 394–398. https://doi.org/10.1016/j.enbuild.2007.03.007

[3] Ministry of Housing and Urban-Rural Development (MOHURD), China Building Energy Efficiency Annual Development Research Report, China Architecture & Building Press, Beijing, 2022.

[4] GB 50176-2016, Code for Thermal Design of Civil Buildings, Ministry of Housing and Urban-Rural Development, Beijing, 2016.

[5] Y. Ji, M. Duanmu, S. Fan, M. Holmberg, Apartment building heating energy performance analysis by simulation, Energy Procedia 75 (2015) 1397–1402. https://doi.org/10.1016/j.egypro.2015.07.224

[6] L. Yang, H. Lam, C. Liu, J. Tsang, Energy performance of building envelopes in different climate zones in China, Appl. Energy 78 (2004) 245–261. https://doi.org/10.1016/j.apenergy.2003.08.006

[7] JGJ 134-2010, Design Standard for Energy Efficiency of Residential Buildings in Hot Summer and Cold Winter Zone, Ministry of Housing and Urban-Rural Development, Beijing, 2010.

[8] Y. Sun, L. Yin, Z. Tian, Z. Lin, Energy performance analysis of residential buildings in China's five climate zones: A review, Energies 14 (2021) 4014. https://doi.org/10.3390/en14134014

[9] State Council of China, Action Plan for Carbon Dioxide Peaking Before 2030, State Council, Beijing, 2021.

[10] Y. Zhu, Applying computer-based simulation to energy auditing: A case study, Energy Build. 38 (5) (2006) 421–428. https://doi.org/10.1016/j.enbuild.2005.07.001

[11] P. Xu, Y. Chan, K. Qian, Success factors of energy performance contracting (EPC) for sustainable building energy efficiency retrofit of hotel buildings in China, Energy Policy 39 (11) (2011) 7389–7398. https://doi.org/10.1016/j.enpol.2011.09.001

[12] M.D. Morris, Factorial sampling plans for preliminary computational experiments, Technometrics 33 (2) (1991) 161–174. https://doi.org/10.1080/00401706.1991.10484804

[13] F. Campolongo, J. Cariboni, A. Saltelli, An effective screening design for sensitivity analysis of large models, Environ. Modell. Softw. 22 (10) (2007) 1509–1518. https://doi.org/10.1016/j.envsoft.2006.10.004

[14] W. Tian, A review of sensitivity analysis methods in building energy analysis, Renew. Sustain. Energy Rev. 20 (2013) 411–419. https://doi.org/10.1016/j.rser.2012.12.014

[15] C. Hopfe, J. Hensen, Uncertainty analysis in building performance simulation for design support, Energy Build. 43 (10) (2011) 2798–2805. https://doi.org/10.1016/j.enbuild.2011.06.034

[16] D. Peronato, E. Rey, M. Andersen, A parametric method using vernacular urban block typologies for investigating interactions between solar energy use and urban design, Renew. Energy 172 (2021) 372–385. https://doi.org/10.1016/j.renene.2021.02.135

[17] IPCC, Climate Change 2021: The Physical Science Basis. Contribution of Working Group I to the Sixth Assessment Report, Cambridge University Press, Cambridge, UK, 2021.

[18] T. Zhou, Y. Qian, Climate change and building energy consumption in hot summer cold winter zone of China, Sustainability 13 (2021) 10519. https://doi.org/10.3390/su131910519

[19] X. Wang, Z. Li, Q. Tian, Future changes in climate extremes over China and their physical attributions, npj Clim. Atmos. Sci. 5 (2022) 74. https://doi.org/10.1038/s41612-022-00299-5

[20] D. Sailor, Risks of summertime extreme thermal conditions in buildings as a result of climate change and exacerbation of urban heat islands, Build. Environ. 78 (2014) 81–88. https://doi.org/10.1016/j.buildenv.2014.04.012

[21] J. Huang, H. Huang, Q. Liao, Y. Zhang, Simulation-based sensitivity analysis of energy performance applied to an old Beijing residential neighbourhood for retrofit strategy optimisation with climate change prediction, Energy Build. 285 (2023) 112870. https://doi.org/10.1016/j.enbuild.2023.112870

[22] J. Chen, L. Zheng, C. Li, Archetype identification and urban building energy modeling for city-scale buildings based on GIS datasets, Build. Simul. 15 (7) (2022) 1125–1139. https://doi.org/10.1007/s12273-021-0835-4

[23] U. Wilcox, W. Marion, Users manual for TMY3 data sets, Technical Report NREL/TP-581-43156, National Renewable Energy Laboratory, Golden, CO, 2008.

[24] JGJ 134-2001, Design Standard for Energy Efficiency of Residential Buildings in Hot Summer and Cold Winter Zone (First edition), Ministry of Construction, Beijing, 2001.

[25] U.S. Department of Energy, EnergyPlus Version 24.1 Engineering Reference, U.S. DOE, Washington DC, 2024. Available at: https://energyplus.net

[26] U.S. Department of Energy, Commercial and Residential Prototype Building Models, Building Energy Codes Program, 2023. Available at: https://www.energycodes.gov/prototype-building-models

[27] S. Philip, eppy: Scripting EnergyPlus files, v0.5, 2020. Available at: https://github.com/santoshphilip/eppy

[28] X. Luo, M. Ng, Y. Liu, J. Zhao, Measured energy consumption and indoor climate condition of residential buildings in hot summer and cold winter zone of China, Energy Build. 155 (2017) 331–341. https://doi.org/10.1016/j.enbuild.2017.09.024

[29] J. Herman, W. Usher, SALib: An open-source Python library for sensitivity analysis, J. Open Source Softw. 2 (9) (2017) 97. https://doi.org/10.21105/joss.00097

[30] A. Saltelli, K. Chan, M. Scott (Eds.), Sensitivity Analysis, Wiley, Chichester, 2000.

[31] W.F. Holmgren, C.W. Hansen, M.A. Mikofski, pvlib python: A python package for modeling solar energy systems, J. Open Source Softw. 3 (29) (2018) 884. https://doi.org/10.21105/joss.00884

[32] A. Dobos, PVWatts version 5 manual, Technical Report NREL/TP-6A20-62641, National Renewable Energy Laboratory, Golden, CO, 2014.

[33] R. Perez, P. Ineichen, R. Seals, J. Michalsky, R. Stewart, Modeling daylight availability and irradiance components from direct and global irradiance, Sol. Energy 44 (5) (1990) 271–289. https://doi.org/10.1016/0038-092X(90)90055-H

[34] S.E. Belcher, J.N. Hacker, D.S. Powell, Constructing design weather data for future climates, Build. Serv. Eng. Res. Technol. 26 (1) (2005) 49–61. https://doi.org/10.1191/0143624405bt112oa

[35] R. Jentsch, A. James, L. Bourikas, A.S. Bahaj, Transforming existing weather data for worldwide locations to enable energy and building performance simulation under future climates, Renew. Energy 55 (2013) 514–524. https://doi.org/10.1016/j.renene.2012.12.049

[36] R. Iturbide et al., An update of IPCC climate reference regions for subcontinental analysis of climate model data: Definition and aggregated datasets, Earth Syst. Sci. Data 12 (4) (2020) 2959–2970. https://doi.org/10.5194/essd-12-2959-2020

[37] X. Wang, Z. Li, Q. Tian, Future changes in climate extremes over China and their physical attributions, npj Clim. Atmos. Sci. 5 (2022) 74. https://doi.org/10.1038/s41612-022-00299-5

[38] M.G. Donat, L.V. Alexander, H. Yang, I. Durre, R. Vose, J. Caesar, Global land-based datasets for monitoring climatic extremes, Bull. Am. Meteorol. Soc. 94 (7) (2013) 997–1006. https://doi.org/10.1175/BAMS-D-12-00109.1

[39] Z. Ma, P. Cooper, D. Daly, L. Ledo, Existing building retrofits: Methodology and state-of-the-art, Energy Build. 55 (2012) 889–902. https://doi.org/10.1016/j.enbuild.2012.08.018

[40] A. Jaffe, R. Stavins, The energy-efficiency gap: What does it mean? Energy Policy 22 (10) (1994) 804–810. https://doi.org/10.1016/0301-4215(94)90138-4

[41] Z. Ma, P. Cooper, D. Daly, L. Ledo, Existing building retrofits: Methodology and state-of-the-art, Energy Build. 55 (2012) 889–902. (See also [39].)

[42] Commission of the European Communities, Directive 2010/31/EU of the European Parliament and of the Council on the energy performance of buildings (recast), Official Journal of the European Union, Brussels, 2010.

[43] C. Jiang, J. Cao, Y. Zhu, X. Ye, L. Han, Q. Huang, Urban heat island effects on energy demand in different climate zones of China: Driving factors and amplification effects, Build. Environ. 218 (2022) 109067. https://doi.org/10.1016/j.buildenv.2022.109067

[44] H. Kim, T. Fatemi, Y. Horie, J. Kato, Infiltration and airtightness performance in residential buildings in humid subtropical Japan, Energy Build. 192 (2019) 96–106. https://doi.org/10.1016/j.enbuild.2019.03.038

[45] C. Reinhart, C. Davila, Urban building energy modeling — A review of a nascent field, Build. Environ. 97 (2016) 196–202. https://doi.org/10.1016/j.buildenv.2015.12.001

[46] R. Evins, A review of computational optimisation methods applied to sustainable building design, Renew. Sustain. Energy Rev. 22 (2013) 230–245. https://doi.org/10.1016/j.rser.2013.02.004

[47] N. Zhou, D. Fridley, M. McNeil, N. Zheng, J. Ke, M. Levine, China's energy and carbon emissions outlook to 2050, Lawrence Berkeley National Laboratory, Report LBNL-4472E, 2011.

[48] S. Wei, R. Jones, P. de Wilde, Driving factors for occupant-controlled space heating in residential buildings, Energy Build. 70 (2014) 36–44. https://doi.org/10.1016/j.enbuild.2013.11.001

[49] Z. Yu, B. Haghighat, B. Fung, H. Yoshino, A decision tree method for building energy demand modeling, Energy Build. 42 (10) (2010) 1637–1646. https://doi.org/10.1016/j.enbuild.2010.04.006

[50] Y. Qian, Q. Wang, Z. Li, Sensitivity analysis and energy-efficiency retrofit of old residential buildings in Beijing considering climate change, Energy Build. 251 (2021) 111351. https://doi.org/10.1016/j.enbuild.2021.111351

---

## Figure Captions

**Fig. 1.** Study area: (a) location of Changsha within China and approximate extent of the HSCW (Hot Summer Cold Winter) climate zone; (b) monthly temperature and precipitation profile for Changsha (TMYx 2007–2021); (c) summary of key climate zone characteristics.

**Fig. 2.** Research methodology flowchart showing the six analytical stages: (1) archetype definition and model setup; (2) baseline EnergyPlus simulation; (3) Morris sensitivity analysis; (4) retrofit scenario simulation; (5) rooftop PV integration; and (6) future climate scenario evaluation.

**Fig. 3.** Building archetype characteristics for the three construction eras: wall, roof, and window U-values; window-to-wall ratio (WWR); air infiltration (ACH); conditioned floor area; number of storeys; and window solar heat gain coefficient (SHGC).

**Fig. 4.** Baseline annual energy use intensity (EUI, kWh m⁻² yr⁻¹) for the three archetypes under current climate conditions, decomposed into six end-use categories: heating, cooling, lighting, equipment, fans, and other (domestic hot water and miscellaneous loads). Values above bars indicate total EUI.

**Fig. 5.** Morris sensitivity analysis results: μ* (mean absolute elementary effect) versus σ (standard deviation of elementary effects) for ten building parameters, shown for (a) Era 1, (b) Era 2, and (c) Era 3. Points are coloured by parameter category (envelope properties, geometry, infiltration, setpoints, internal gains). The dashed line σ = μ* indicates purely linear sensitivity.

**Fig. 6.** Top-5 parameter importance rankings by μ* value for (a) Era 1, (b) Era 2, and (c) Era 3. Bars are coloured by parameter category as in Fig. 5.

**Fig. 7.** Annual EUI savings (% reduction from archetype baseline) for each of the five retrofit measures and three construction eras. Group bars are ordered by retrofit measure; numerical labels show savings percentage where greater than 1%.

**Fig. 8.** Energy use intensity before (Baseline) and after (R5 Combined) retrofit for each archetype, presented as paired stacked bars decomposed into heating, cooling, and other loads. Annotations show total EUI savings (%) achieved by R5 for each era.

**Fig. 9.** Comparison of annual energy flows for the three archetypes: baseline EUI, R5-retrofitted EUI, PV generation per unit floor area, and net EUI (R5 − PV). Annotations below the x-axis show the PV self-sufficiency achieved under R5+PV conditions.

**Fig. 10.** Monthly rooftop PV generation per unit roof area (bar chart, left axis) for the three archetypes, and mean daily global horizontal irradiance (GHI) derived from the Changsha TMYx EPW file (line chart, right axis).

**Fig. 11.** CMIP6 temperature increments (ΔT, °C) applied to the Changsha TMYx EPW for each of the four future climate scenarios: annual mean ΔT, July ΔT, and January ΔT. Bars are coloured by scenario. Values are derived from the IPCC AR6 Interactive Atlas multi-model median for the East Asia domain (~28°N, 113°E).

**Fig. 12.** Annual total EUI (kWh m⁻² yr⁻¹) as a function of climate scenario for (a) Era 1 and (b) Era 2, showing both Baseline and R5 Combined conditions. Divergence between Baseline (decreasing with warming) and R5 (increasing with warming) trajectories illustrates the inversion of climate sensitivity produced by the R5 retrofit.

**Fig. 13.** Shift in heating versus cooling load share (% of total heating+cooling demand) across five climate scenarios for (a) Era 1, (b) Era 2, and (c) Era 3 under Baseline conditions. Progressive transition from heating-dominated to cooling-dominated profiles is visible across scenarios; numerical labels indicate the percentage share of heating (top) and cooling (bottom) within each stacked bar.

**Fig. 14.** Stepwise EUI reduction pathway for all three archetypes across four intervention stages: current baseline, after R5 combined retrofit, after R5+rooftop PV, and R5 performance under the worst-case 2080 SSP5-8.5 climate scenario. Annotation boxes show total percentage reduction achieved by the R5+PV combination relative to the current baseline.

---

*Manuscript version: v1*  
*Date: 2026-04-20*  
*Status: First complete draft — ready for author review*  
*Word count (approximate): Abstract 250, Introduction 1,550, Methodology 2,600, Results 3,050, Discussion 1,600, Conclusions 520, Total text ~9,600 words*
