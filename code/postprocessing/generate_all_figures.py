#!/usr/bin/env python3
"""
generate_all_figures.py
=======================
Generates all 14 publication-quality figures for the Changsha residential
retrofit study submitted to Energy and Buildings.

Usage:
    python code/postprocessing/generate_all_figures.py

Output: figure/fig{01..14}_*.png at 300 dpi
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch, Polygon, FancyArrowPatch
from matplotlib.lines import Line2D
warnings.filterwarnings('ignore')

# ─── Paths ────────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, 'data', 'processed')
FIG  = os.path.join(ROOT, 'figure')
os.makedirs(FIG, exist_ok=True)

# ─── Palette ──────────────────────────────────────────────────────────────────
C1    = '#D85A30'   # Era 1 (~1980s)
C2    = '#2E75B6'   # Era 2 (~2000s)
C3    = '#1D9E75'   # Era 3 (~2010s+)
HEAT  = '#E24B4A'   # Heating
COOL  = '#378ADD'   # Cooling
PV    = '#EF9F27'   # PV / Solar
OTHER = '#73726C'   # Other / DHW
LIGHT = '#9DC3E6'   # Lighting
EQUIP = '#C4A265'   # Equipment
FANS  = '#B4C7A0'   # Fans

ERA_COLORS = [C1, C2, C3]
ERA_LABELS = ['Era 1 (~1980s)', 'Era 2 (~2000s)', 'Era 3 (~2010s+)']

PARAM_CATS = {
    'wall_U':           ('Envelope',      '#4472C4'),
    'window_U':         ('Envelope',      '#4472C4'),
    'roof_U':           ('Envelope',      '#4472C4'),
    'WWR':              ('Geometry',      '#70AD47'),
    'infiltration':     ('Infiltration',  '#D85A30'),
    'heating_setpoint': ('Setpoints',     '#FFC000'),
    'cooling_setpoint': ('Setpoints',     '#FFC000'),
    'equipment_power':  ('Internal gains','#7030A0'),
    'occupant_density': ('Internal gains','#7030A0'),
    'lighting_power':   ('Internal gains','#7030A0'),
}
PARAM_LABELS = {
    'wall_U':           'Wall U-value',
    'window_U':         'Window U-value',
    'roof_U':           'Roof U-value',
    'WWR':              'WWR',
    'infiltration':     'Infiltration',
    'heating_setpoint': 'Heating setpoint',
    'cooling_setpoint': 'Cooling setpoint',
    'equipment_power':  'Equipment power',
    'occupant_density': 'Occupant density',
    'lighting_power':   'Lighting power',
}

# CMIP6 monthly ΔT values (from generate_future_epw.py)
DELTA_T = {
    '2050 SSP2-4.5': [1.9, 1.8, 1.7, 1.6, 1.5, 1.5, 1.6, 1.7, 1.7, 1.8, 1.9, 2.0],
    '2050 SSP5-8.5': [2.4, 2.3, 2.1, 2.0, 1.9, 1.9, 2.0, 2.1, 2.1, 2.2, 2.3, 2.5],
    '2080 SSP2-4.5': [2.6, 2.5, 2.3, 2.2, 2.1, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.7],
    '2080 SSP5-8.5': [4.5, 4.3, 4.0, 3.8, 3.6, 3.5, 3.7, 3.8, 4.0, 4.2, 4.4, 4.7],
}

# ─── Style helpers ────────────────────────────────────────────────────────────
def style_ax(ax, grid=True):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(labelsize=10)
    if grid:
        ax.yaxis.grid(True, linestyle='--', alpha=0.4, linewidth=0.6)
        ax.set_axisbelow(True)

def save_fig(fig, name):
    path = os.path.join(FIG, name)
    fig.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  [OK] {name}')

# ─── Load data ────────────────────────────────────────────────────────────────
df_base    = pd.read_csv(os.path.join(DATA, 'baseline_results.csv'))
df_retro   = pd.read_csv(os.path.join(DATA, 'retrofit_results.csv'))
df_solar   = pd.read_csv(os.path.join(DATA, 'solar_results.csv'))
df_climate = pd.read_csv(os.path.join(DATA, 'climate_results.csv'))
df_solar_m = pd.read_csv(os.path.join(DATA, 'solar_monthly.csv'))
df_m = {
    1: pd.read_csv(os.path.join(DATA, 'morris_results_era1.csv')),
    2: pd.read_csv(os.path.join(DATA, 'morris_results_era2.csv')),
    3: pd.read_csv(os.path.join(DATA, 'morris_results_era3.csv')),
}


# =============================================================================
# FIG 01 — Study area: Changsha location, HSCW zone, climate card
# =============================================================================
def fig01_study_area():
    fig = plt.figure(figsize=(15, 6))
    fig.patch.set_facecolor('white')
    gs = gridspec.GridSpec(1, 3, figure=fig, wspace=0.30)

    # ── Panel A: simplified China map ──────────────────────────────────────
    ax = fig.add_subplot(gs[0, 0])

    # Approximate mainland China boundary (lon, lat)
    china = np.array([
        [73.5,39.5],[77,38],[80,37],[83,37],[87,49],[91,48],[96,42],[99,42],
        [103,50],[106,52],[108,53],[113,50],[116,51],[119,48],[123,47],
        [130,42],[134,46],[135,48],[132,43],[129,37],[123,32],[121,27],
        [119,22],[114,20],[109,18],[104,21],[101,22],[100,28],[97,24],
        [93,21],[89,27],[84,29],[80,30],[78,35],[73.5,39.5]
    ])
    china_patch = Polygon(china, closed=True, facecolor='#ECEEE6',
                          edgecolor='#888', linewidth=0.8, zorder=1)
    ax.add_patch(china_patch)

    # HSCW zone (approximate region: Yangtze River Basin + south)
    hscw = np.array([
        [104,24],[104,30],[108,34],[114,34],[119,32],[122,28],
        [121,24],[116,22],[110,20],[106,22],[104,24]
    ])
    hscw_patch = Polygon(hscw, closed=True, facecolor='#FFD4B0',
                         edgecolor='#D85A30', linewidth=1.8, alpha=0.65, zorder=2)
    ax.add_patch(hscw_patch)

    # Changsha marker (28.2°N, 112.9°E)
    ax.plot(112.9, 28.2, 'o', color='white', markersize=11, zorder=5)
    ax.plot(112.9, 28.2, '*', color=C1, markersize=12, zorder=6)
    ax.annotate('Changsha\n28.2°N, 112.9°E', xy=(112.9, 28.2),
                xytext=(101.5, 22.5), fontsize=9, fontweight='bold', color=C1,
                arrowprops=dict(arrowstyle='->', color=C1, lw=1.5),
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white',
                          edgecolor=C1, alpha=0.9))

    ax.set_xlim(70, 138)
    ax.set_ylim(14, 56)
    ax.set_aspect('equal')
    ax.set_xlabel('Longitude (°E)', fontsize=12)
    ax.set_ylabel('Latitude (°N)', fontsize=12)
    ax.set_title('(a) Study Location', fontsize=12, fontweight='bold')
    ax.tick_params(labelsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    hscw_leg = mpatches.Patch(facecolor='#FFD4B0', edgecolor='#D85A30',
                               linewidth=1.5, label='HSCW Climate Zone',
                               alpha=0.65)
    ax.legend(handles=[hscw_leg], loc='lower left', fontsize=8.5)

    # ── Panel B: monthly temperature ───────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    months = np.arange(1, 13)
    mlabels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    # Changsha TMYx approximate monthly means
    t_mean = [4.5, 6.2, 10.8, 17.2, 22.1, 26.4, 29.4, 28.9, 24.1, 18.5, 12.3, 6.5]
    t_max  = [8.1, 10.0,15.2, 22.1, 27.0, 30.8, 33.5, 33.2, 28.7, 23.2, 16.8,10.0]
    t_min  = [1.2, 2.8,  7.0, 13.0, 18.0, 23.0, 26.2, 25.7, 20.5, 14.5,  8.5, 3.5]
    # Precip (mm) on secondary axis
    precip = [62, 85, 115, 143, 175, 168, 110, 98, 72, 58, 62, 55]

    ax2.fill_between(months, t_min, t_max, alpha=0.20, color=HEAT, label='Min–Max range')
    ax2.plot(months, t_mean, 'o-', color=HEAT, linewidth=2.0, markersize=5,
             label='Monthly mean T (°C)')
    ax2.axhline(18, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax2.axhline(26, color='gray', linestyle=':',  linewidth=1, alpha=0.7)
    ax2.text(12.2, 18, '18°C', fontsize=7.5, va='center', color='gray')
    ax2.text(12.2, 26, '26°C', fontsize=7.5, va='center', color='gray')

    ax2b = ax2.twinx()
    ax2b.bar(months, precip, color=COOL, alpha=0.30, width=0.7,
             label='Precipitation (mm)')
    ax2b.set_ylabel('Precipitation (mm)', fontsize=11, color=COOL)
    ax2b.tick_params(axis='y', labelcolor=COOL, labelsize=9)
    ax2b.spines['top'].set_visible(False)
    ax2b.set_ylim(0, 350)

    ax2.set_xticks(months)
    ax2.set_xticklabels(mlabels, fontsize=9)
    ax2.set_ylabel('Temperature (°C)', fontsize=12)
    ax2.set_title('(b) Monthly Climate Profile', fontsize=12, fontweight='bold')
    ax2.tick_params(labelsize=10)
    ax2.spines['top'].set_visible(False)
    ax2.set_ylim(-2, 42)

    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2b.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc='upper left')

    # ── Panel C: climate data card ─────────────────────────────────────────
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.axis('off')
    ax3.set_title('(c) Climate Zone Characteristics', fontsize=12,
                  fontweight='bold')

    rect = FancyBboxPatch((0.01, 0.01), 0.98, 0.92,
                           boxstyle='round,pad=0.03', linewidth=2.0,
                           edgecolor=C1, facecolor='#FFF6F2',
                           transform=ax3.transAxes, zorder=0)
    ax3.add_patch(rect)

    rows = [
        ('Location:',      'Changsha, Hunan Province'),
        ('Coordinates:',   '28.2°N, 112.9°E, Elev. 68 m'),
        ('Climate class:', 'HSCW (Hot Summer, Cold Winter)'),
        ('CN standard:',   'JGJ 134-2010'),
        ('ASHRAE zone:',   '3A (Humid Subtropical)'),
        ('Ann. mean T:',   '17.5°C'),
        ('July mean T:',   '29.4°C  |  Jan mean T: 4.5°C'),
        ('HDD₁₈:',         '≈ 1,350 degree-days'),
        ('CDD₂₆:',         '≈ 490 degree-days'),
        ('Ann. precip.:',  '≈ 1,360 mm'),
        ('Ann. GHI:',      '≈ 1,190 kWh/m²'),
        ('PV potential:',  '1,060–1,190 kWh/kWp·yr'),
        ('Weather file:',  'EnergyPlus TMYx 2007–2021'),
        ('Data source:',   'climate.onebuilding.org'),
    ]
    y0, dy = 0.895, 0.060
    for lbl, val in rows:
        ax3.text(0.05, y0, lbl, fontsize=9, fontweight='bold',
                 transform=ax3.transAxes, va='top', zorder=5)
        ax3.text(0.40, y0, val, fontsize=9,
                 transform=ax3.transAxes, va='top', zorder=5)
        y0 -= dy

    fig.suptitle('Study Area: Changsha, China (HSCW Climate Zone)',
                 fontsize=13, fontweight='bold', y=1.005)
    save_fig(fig, 'fig01_study_area.png')


# =============================================================================
# FIG 02 — Research methodology flowchart
# =============================================================================
def fig02_methodology():
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('white')
    ax.axis('off')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)

    stage_data = [
        (1.0, 6.8, '#4472C4', 'Stage 1\nBuilding Archetypes',
         '• 3 construction eras (1980s, 2000s, 2010s+)\n'
         '• DOE prototype IDF files (Mid/HighRise)\n'
         '• Envelope adapted for Chinese standards'),
        (4.0, 6.8, '#70AD47', 'Stage 2\nBaseline Simulation',
         '• EnergyPlus v24.1 + Changsha TMYx EPW\n'
         '• eppy for IDF modification\n'
         '• EUI decomposition: heat/cool/lights/equip'),
        (7.5, 6.8, '#FFC000', 'Stage 3\nSensitivity Analysis',
         '• Morris elementary effects (SALib)\n'
         '• 10 parameters × N=100 trajectories\n'
         '• μ*, σ ranking per era'),
        (1.0, 3.5, '#ED7D31', 'Stage 4\nRetrofit Scenarios',
         '• R1: Wall insul. (U=0.4 W/m²K)\n'
         '• R2: Window upgrade (U=1.8, SHGC=0.35)\n'
         '• R3: Roof insul. (U=0.3 W/m²K)\n'
         '• R4: Air-sealing (0.3 ACH)\n'
         '• R5: Combined (all four measures)'),
        (4.5, 3.5, '#A9D18E', 'Stage 5\nSolar PV Integration',
         '• pvlib-based rooftop PV sizing\n'
         '• MidRise: 72 kWp / HighRise: 40 kWp\n'
         '• Net EUI = R5 EUI − PV generation'),
        (8.0, 3.5, '#9DC3E6', 'Stage 6\nClimate Change',
         '• CMIP6 ΔT morphed EPW (Belcher 2005)\n'
         '• 4 scenarios: 2050/2080 × SSP2-4.5/5-8.5\n'
         '• 30 EnergyPlus runs (3 eras × 2 retrofits × 5 climates)'),
    ]

    box_w, box_h = 2.5, 2.0

    for (x, y, color, title, body) in stage_data:
        rect = FancyBboxPatch((x, y - box_h), box_w, box_h,
                               boxstyle='round,pad=0.12',
                               linewidth=1.8, edgecolor='#555',
                               facecolor=color + '40', zorder=2)
        ax.add_patch(rect)
        ax.text(x + box_w/2, y - 0.15, title, ha='center', va='top',
                fontsize=10, fontweight='bold', color='#222', zorder=3)
        ax.text(x + 0.12, y - 0.60, body, ha='left', va='top',
                fontsize=7.8, color='#333', zorder=3,
                family='monospace', linespacing=1.5)

    # Top-row arrows
    arrowprops = dict(arrowstyle='->', color='#444', lw=1.8,
                      connectionstyle='arc3,rad=0')
    for x_start, x_end, y_row in [(3.55, 3.95, 5.85), (6.55, 7.45, 5.85)]:
        ax.annotate('', xy=(x_end, y_row), xytext=(x_start, y_row),
                    arrowprops=arrowprops)

    # Bottom-row arrows
    for x_start, x_end, y_row in [(3.55, 4.45, 2.55), (7.05, 7.95, 2.55)]:
        ax.annotate('', xy=(x_end, y_row), xytext=(x_start, y_row),
                    arrowprops=arrowprops)

    # Down arrow between rows (from Stage 3 to Stage 4 region)
    # Go from end of Stage 3 down to Stage 4
    ax.annotate('', xy=(2.25, 3.5), xytext=(2.25, 4.8),
                arrowprops=arrowprops)

    # Output box at bottom
    out_rect = FancyBboxPatch((3.5, 0.15), 7, 1.0,
                               boxstyle='round,pad=0.12',
                               linewidth=2.0, edgecolor=C1,
                               facecolor='#FFF0EB', zorder=2)
    ax.add_patch(out_rect)
    ax.text(7, 0.90, 'OUTPUTS', ha='center', va='top',
            fontsize=11, fontweight='bold', color=C1, zorder=3)
    ax.text(7, 0.60,
            'Energy savings (%) · Parameter rankings (μ*) · Net EUI after PV · '
            'EUI under 2050/2080 climate scenarios',
            ha='center', va='top', fontsize=9, color='#333', zorder=3)

    # Arrows from bottom row to output
    for xc in [2.25, 5.75, 9.25]:
        ax.annotate('', xy=(7, 1.15), xytext=(xc, 1.5),
                    arrowprops=dict(arrowstyle='->', color='#888', lw=1.2))

    ax.set_title('Research Methodology Flowchart',
                 fontsize=13, fontweight='bold', pad=8)
    save_fig(fig, 'fig02_methodology.png')


# =============================================================================
# FIG 03 — Building archetype characteristics
# =============================================================================
def fig03_archetypes():
    fig = plt.figure(figsize=(14, 7))
    gs  = gridspec.GridSpec(2, 4, figure=fig, wspace=0.45, hspace=0.55)

    # Archetype data
    labels = ERA_LABELS
    wall_u  = [1.5, 1.0, 0.6]
    win_u   = [5.8, 3.5, 2.5]
    roof_u  = [2.0, 0.8, 0.4]
    wwr     = [0.25, 0.30, 0.40]
    ach     = [1.5, 1.0, 0.6]
    fa      = [3134.6, 3134.6, 7836.4]
    floors  = [6, 6, 18]
    shgc    = [0.70, 0.60, 0.45]

    bar_kw = dict(width=0.55, edgecolor='white', linewidth=0.8)
    x = np.arange(3)
    xlabels = ['Era 1\n(~1980s)', 'Era 2\n(~2000s)', 'Era 3\n(~2010s+)']

    params = [
        ('Wall U-value (W/m²K)', wall_u, 0, 0),
        ('Window U-value (W/m²K)', win_u, 0, 1),
        ('Roof U-value (W/m²K)', roof_u, 0, 2),
        ('WWR (–)', wwr, 0, 3),
        ('Infiltration (ACH)', ach, 1, 0),
        ('Floor area (m²)', fa, 1, 1),
        ('Number of floors', floors, 1, 2),
        ('Window SHGC (–)', shgc, 1, 3),
    ]

    for title, vals, row, col in params:
        ax = fig.add_subplot(gs[row, col])
        bars = ax.bar(x, vals, color=ERA_COLORS, **bar_kw)
        ax.set_xticks(x)
        ax.set_xticklabels(xlabels, fontsize=8.5)
        ax.set_title(title, fontsize=10, fontweight='bold', pad=4)
        style_ax(ax)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.02,
                    f'{v:.2f}' if v < 10 else f'{v:.0f}',
                    ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    legend_patches = [mpatches.Patch(color=c, label=l)
                      for c, l in zip(ERA_COLORS, ERA_LABELS)]
    fig.legend(handles=legend_patches, loc='lower center', ncol=3,
               fontsize=9.5, bbox_to_anchor=(0.5, -0.02),
               frameon=True, edgecolor='#ccc')

    fig.suptitle('Building Archetype Characteristics — Three Construction Eras',
                 fontsize=13, fontweight='bold', y=1.01)
    save_fig(fig, 'fig03_archetypes.png')


# =============================================================================
# FIG 04 — Baseline EUI stacked bar (heating / cooling / other)
# =============================================================================
def fig04_baseline_eui():
    fig, ax = plt.subplots(figsize=(9, 6))

    eras = df_base['era'].values
    x    = np.arange(len(eras))

    heat  = df_base['heating_kwh_m2'].values
    cool  = df_base['cooling_kwh_m2'].values
    light = df_base['lighting_kwh_m2'].values
    equip = df_base['equipment_kwh_m2'].values
    fans  = df_base['fans_kwh_m2'].values
    other = df_base['other_kwh_m2'].values

    w = 0.45
    p1 = ax.bar(x, heat,  w, color=HEAT,  label='Heating',   edgecolor='white')
    p2 = ax.bar(x, cool,  w, bottom=heat, color=COOL,  label='Cooling',
                edgecolor='white')
    p3 = ax.bar(x, light, w, bottom=heat+cool, color=LIGHT, label='Lighting',
                edgecolor='white')
    p4 = ax.bar(x, equip, w, bottom=heat+cool+light, color=EQUIP,
                label='Equipment', edgecolor='white')
    p5 = ax.bar(x, fans,  w, bottom=heat+cool+light+equip, color=FANS,
                label='Fans', edgecolor='white')
    p6 = ax.bar(x, other, w, bottom=heat+cool+light+equip+fans, color=OTHER,
                label='DHW & Other', edgecolor='white')

    totals = df_base['total_eui_kwh_m2'].values
    for xi, tot in zip(x, totals):
        ax.text(xi, tot + 3, f'{tot:.1f}', ha='center', va='bottom',
                fontsize=11, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(ERA_LABELS, fontsize=11)
    ax.set_ylabel('EUI (kWh/m²·yr)', fontsize=12)
    ax.set_xlabel('Building Archetype', fontsize=12)
    ax.legend(fontsize=9, loc='upper right', framealpha=0.9)
    style_ax(ax)

    # Annotate heating/cooling split
    for xi, h, c in zip(x, heat, cool):
        ax.text(xi, h/2,  f'{h:.1f}', ha='center', va='center',
                fontsize=8.5, color='white', fontweight='bold')
        ax.text(xi, h + c/2, f'{c:.1f}', ha='center', va='center',
                fontsize=8.5, color='white', fontweight='bold')

    ax.set_title('Baseline Energy Use Intensity by End-Use — Three Archetypes',
                 fontsize=13, fontweight='bold', pad=8)
    ax.set_ylim(0, max(totals) * 1.18)
    save_fig(fig, 'fig04_baseline_eui.png')


# =============================================================================
# FIG 05 — Morris μ* vs σ scatter, 3 panels
# =============================================================================
def fig05_morris_scatter():
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5), sharey=False)

    cat_legend_done = {}

    for idx, (era, ax) in enumerate(zip([1, 2, 3], axes)):
        df = df_m[era]
        for _, row in df.iterrows():
            p = row['parameter']
            cat, color = PARAM_CATS.get(p, ('Other', '#999'))
            label = cat if cat not in cat_legend_done else '_nolegend_'
            cat_legend_done[cat] = True
            ax.scatter(row['mu_star'], row['sigma'], color=color,
                       s=90, zorder=4, edgecolors='white', linewidth=0.8,
                       label=label)
            ax.annotate(PARAM_LABELS.get(p, p),
                        (row['mu_star'], row['sigma']),
                        xytext=(3, 3), textcoords='offset points',
                        fontsize=7.8, color='#333')

        # Reference line σ = μ* (linear sensitivity)
        mx = df['mu_star'].max() * 1.1
        ax.plot([0, mx], [0, mx], '--', color='#aaa', linewidth=1.0,
                label='σ = μ* (linear)' if idx == 0 else '_nolegend_')

        ax.set_xlabel('μ* (mean absolute EE)', fontsize=12)
        ax.set_ylabel('σ (std. dev. EE)', fontsize=12 if idx == 0 else 0)
        ax.set_title(f'({chr(97+idx)}) {ERA_LABELS[idx]}',
                     fontsize=12, fontweight='bold')
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
        style_ax(ax, grid=False)
        ax.spines['left'].set_visible(True)
        ax.spines['bottom'].set_visible(True)

    # Build unified legend
    cat_colors = {}
    for p, (cat, col) in PARAM_CATS.items():
        cat_colors[cat] = col
    cat_colors['σ = μ* (linear)'] = '#aaa'

    handles = [mpatches.Patch(color=c, label=l) if l != 'σ = μ* (linear)'
               else Line2D([0],[0], linestyle='--', color='#aaa', label=l)
               for l, c in cat_colors.items()]
    fig.legend(handles=handles, loc='lower center', ncol=5, fontsize=9,
               bbox_to_anchor=(0.5, -0.06), frameon=True, edgecolor='#ccc')

    fig.suptitle('Morris Sensitivity Analysis — μ* vs σ by Parameter',
                 fontsize=13, fontweight='bold', y=1.01)
    save_fig(fig, 'fig05_morris_scatter.png')


# =============================================================================
# FIG 06 — Top-5 parameter ranking, horizontal grouped bar
# =============================================================================
def fig06_parameter_ranking():
    fig, axes = plt.subplots(1, 3, figsize=(14, 5.5), sharey=False)

    for idx, (era, ax) in enumerate(zip([1, 2, 3], axes)):
        df = df_m[era].sort_values('rank').head(5)
        params = [PARAM_LABELS.get(p, p) for p in df['parameter']]
        vals   = df['mu_star'].values
        y = np.arange(len(params))

        # Color by category
        colors = [PARAM_CATS.get(p, ('', '#999'))[1] for p in df['parameter']]
        bars = ax.barh(y, vals, color=colors, edgecolor='white',
                       height=0.6)
        ax.set_yticks(y)
        ax.set_yticklabels(params, fontsize=10)
        ax.set_xlabel('μ* (mean absolute EE)', fontsize=11)
        ax.set_title(f'({chr(97+idx)}) {ERA_LABELS[idx]}',
                     fontsize=12, fontweight='bold')
        ax.invert_yaxis()
        for bar, v in zip(bars, vals):
            ax.text(v + 0.3, bar.get_y() + bar.get_height()/2,
                    f'{v:.1f}', va='center', fontsize=9.5, fontweight='bold')
        style_ax(ax, grid=False)
        ax.xaxis.grid(True, linestyle='--', alpha=0.4)
        ax.set_axisbelow(True)

    cat_colors = {}
    for p, (cat, col) in PARAM_CATS.items():
        cat_colors[cat] = col
    handles = [mpatches.Patch(color=c, label=l) for l, c in cat_colors.items()]
    fig.legend(handles=handles, loc='lower center', ncol=4, fontsize=9,
               bbox_to_anchor=(0.5, -0.06), frameon=True, edgecolor='#ccc')

    fig.suptitle('Top-5 Influential Parameters by Construction Era (Morris μ*)',
                 fontsize=13, fontweight='bold', y=1.01)
    save_fig(fig, 'fig06_parameter_ranking.png')


# =============================================================================
# FIG 07 — Retrofit energy savings grouped bar (5 measures × 3 eras)
# =============================================================================
def fig07_retrofit_savings():
    fig, ax = plt.subplots(figsize=(12, 6))

    retro_order = ['R1_Wall', 'R2_Window', 'R3_Roof', 'R4_Infiltration', 'R5_Combined']
    retro_labels = ['R1: Wall\nInsulation', 'R2: Window\nUpgrade',
                    'R3: Roof\nInsulation', 'R4: Air\nSealing', 'R5: Combined']
    retro_colors = ['#4472C4', '#70AD47', '#FFC000', C1, '#7030A0']

    n_retro = len(retro_order)
    n_eras  = 3
    bar_w   = 0.24
    x       = np.arange(n_retro)

    df_r = df_retro[df_retro['retrofit'] != 'Baseline'].copy()

    for ei, (era_val, ec, el) in enumerate(zip([1, 2, 3], ERA_COLORS, ERA_LABELS)):
        df_e = df_r[df_r['era'] == era_val]
        offsets = (ei - 1) * bar_w
        savings = []
        for r in retro_order:
            row = df_e[df_e['retrofit'] == r]
            savings.append(row['savings_percent'].values[0] if len(row) else 0)
        bars = ax.bar(x + offsets, savings, bar_w, color=ec, label=el,
                      edgecolor='white', linewidth=0.8)
        for bar, s in zip(bars, savings):
            if s > 1:
                ax.text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() + 0.5,
                        f'{s:.1f}%', ha='center', va='bottom',
                        fontsize=7.5, rotation=90)

    ax.set_xticks(x)
    ax.set_xticklabels(retro_labels, fontsize=10.5)
    ax.set_ylabel('Total EUI Savings (%)', fontsize=12)
    ax.set_xlabel('Retrofit Measure', fontsize=12)
    ax.legend(fontsize=9.5, loc='upper left')
    ax.set_ylim(0, 58)
    style_ax(ax)
    ax.set_title('Retrofit Energy Savings by Measure and Construction Era',
                 fontsize=13, fontweight='bold', pad=8)
    save_fig(fig, 'fig07_retrofit_savings.png')


# =============================================================================
# FIG 08 — EUI before/after paired stacked bars (Baseline vs R5)
# =============================================================================
def fig08_eui_before_after():
    fig, ax = plt.subplots(figsize=(11, 6.5))

    bar_w = 0.35
    n_eras = 3
    x = np.arange(n_eras) * 2.2

    df_bl = df_retro[df_retro['retrofit'] == 'Baseline'].reset_index(drop=True)
    df_r5 = df_retro[df_retro['retrofit'] == 'R5_Combined'].reset_index(drop=True)

    # Baseline bars
    for i in range(n_eras):
        row_bl = df_bl.iloc[i]
        row_r5 = df_r5.iloc[i]
        other_bl = row_bl['total_eui_kwh_m2'] - row_bl['heating_kwh_m2'] - row_bl['cooling_kwh_m2']
        other_r5 = row_r5['total_eui_kwh_m2'] - row_r5['heating_kwh_m2'] - row_r5['cooling_kwh_m2']

        # Baseline stacked
        ax.bar(x[i], row_bl['heating_kwh_m2'], bar_w, color=HEAT,
               edgecolor='white', label='Heating' if i == 0 else '_nolegend_')
        ax.bar(x[i], row_bl['cooling_kwh_m2'], bar_w,
               bottom=row_bl['heating_kwh_m2'],
               color=COOL, edgecolor='white',
               label='Cooling' if i == 0 else '_nolegend_')
        ax.bar(x[i], other_bl, bar_w,
               bottom=row_bl['heating_kwh_m2'] + row_bl['cooling_kwh_m2'],
               color=OTHER, edgecolor='white',
               label='DHW & Other' if i == 0 else '_nolegend_')

        # R5 stacked
        ax.bar(x[i] + bar_w + 0.05, row_r5['heating_kwh_m2'], bar_w,
               color=HEAT, edgecolor='white', alpha=0.6)
        ax.bar(x[i] + bar_w + 0.05, row_r5['cooling_kwh_m2'], bar_w,
               bottom=row_r5['heating_kwh_m2'],
               color=COOL, edgecolor='white', alpha=0.6)
        ax.bar(x[i] + bar_w + 0.05, other_r5, bar_w,
               bottom=row_r5['heating_kwh_m2'] + row_r5['cooling_kwh_m2'],
               color=OTHER, edgecolor='white', alpha=0.6)

        # Total labels
        ax.text(x[i], row_bl['total_eui_kwh_m2'] + 3,
                f'{row_bl["total_eui_kwh_m2"]:.1f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
        ax.text(x[i] + bar_w + 0.05, row_r5['total_eui_kwh_m2'] + 3,
                f'{row_r5["total_eui_kwh_m2"]:.1f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold',
                color='#555')

        # Savings annotation
        sav = row_r5['savings_percent']
        mid_x = x[i] + bar_w/2 + 0.025
        ax.annotate(f'−{sav:.1f}%',
                    xy=(mid_x, (row_bl['total_eui_kwh_m2'] + row_r5['total_eui_kwh_m2'])/2),
                    fontsize=10, ha='center', color=ERA_COLORS[i], fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                              edgecolor=ERA_COLORS[i], alpha=0.85))

    # X-axis labels
    tick_x = [xi + bar_w/2 + 0.025 for xi in x]
    ax.set_xticks(tick_x)
    ax.set_xticklabels([f'{l}\nBaseline / R5' for l in ERA_LABELS], fontsize=10)

    # Add baseline/R5 text above each pair
    for i, xi in enumerate(x):
        ax.text(xi, -12, 'Baseline', ha='center', fontsize=8.5, color='#333')
        ax.text(xi + bar_w + 0.05, -12, 'R5', ha='center', fontsize=8.5,
                color='#777')

    ax.set_ylabel('EUI (kWh/m²·yr)', fontsize=12)
    ax.legend(fontsize=9.5, loc='upper right')
    style_ax(ax)
    ax.set_ylim(-20, 310)
    ax.set_title('EUI Before and After R5 Combined Retrofit — All Three Archetypes',
                 fontsize=13, fontweight='bold', pad=8)
    save_fig(fig, 'fig08_eui_before_after.png')


# =============================================================================
# FIG 09 — PV generation vs building demand grouped bar
# =============================================================================
def fig09_solar_pv_demand():
    fig, ax = plt.subplots(figsize=(11, 6.5))

    bar_w = 0.18
    x = np.arange(3)

    # Data
    bl_eui  = []
    r5_eui  = []
    pv_gen  = []
    net_eui = []

    for era in [1, 2, 3]:
        bl = df_solar[(df_solar['era'] == era) & (df_solar['retrofit'] == 'Baseline')].iloc[0]
        r5 = df_solar[(df_solar['era'] == era) & (df_solar['retrofit'] == 'R5_Combined')].iloc[0]
        bl_eui.append(bl['retrofit_eui_kwh_m2'])
        r5_eui.append(r5['retrofit_eui_kwh_m2'])
        pv_gen.append(r5['pv_per_m2_floor'])
        net_eui.append(r5['net_eui_kwh_m2'])

    labels = ['Baseline\nEUI', 'R5\nEUI', 'PV Gen.\n(per m² floor)', 'Net EUI\n(R5 − PV)']
    offsets = [-1.5, -0.5, 0.5, 1.5]
    colors  = [OTHER, COOL, PV, C3]
    data    = [bl_eui, r5_eui, pv_gen, net_eui]

    for di, (d, off, col, lbl) in enumerate(zip(data, offsets, colors, labels)):
        bars = ax.bar(x + off * bar_w, d, bar_w * 0.90, color=col,
                      label=lbl, edgecolor='white', linewidth=0.8)
        for bar, v in zip(bars, d):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                    f'{v:.1f}', ha='center', va='bottom', fontsize=9,
                    fontweight='bold')

    # Self-sufficiency annotations
    for i, era in enumerate([1, 2, 3]):
        r5 = df_solar[(df_solar['era'] == era) & (df_solar['retrofit'] == 'R5_Combined')].iloc[0]
        ss = r5['self_sufficiency_pct']
        ax.text(i, -10, f'PV covers\n{ss:.1f}% (R5)',
                ha='center', fontsize=8.5, color='#555')

    ax.set_xticks(x)
    ax.set_xticklabels(ERA_LABELS, fontsize=11)
    ax.set_ylabel('Energy (kWh/m²·yr)', fontsize=12)
    ax.legend(fontsize=9.5, loc='upper right')
    style_ax(ax)
    ax.set_ylim(-18, 305)
    ax.set_title('Solar PV Generation vs Building Energy Demand — Three Archetypes',
                 fontsize=13, fontweight='bold', pad=8)
    save_fig(fig, 'fig09_solar_pv_demand.png')


# =============================================================================
# FIG 10 — Monthly PV generation + GHI overlay (dual y-axis)
# =============================================================================
def fig10_monthly_pv():
    fig, ax = plt.subplots(figsize=(11, 6))

    months  = np.arange(1, 13)
    mlabels = ['Jan','Feb','Mar','Apr','May','Jun',
               'Jul','Aug','Sep','Oct','Nov','Dec']
    days    = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    bar_w = 0.26
    for i, (era, ec, el) in enumerate(zip([1, 2, 3], ERA_COLORS, ERA_LABELS)):
        sub = df_solar_m[df_solar_m['era'] == era].sort_values('month')
        pv  = sub['pv_gen_kwh'].values
        # Normalise to kWh/m²/month using rooftop area
        area = 360.0 if era <= 2 else 200.0
        pv_m2 = pv / area
        ax.bar(months + (i-1)*bar_w, pv_m2, bar_w,
               color=ec, label=el, edgecolor='white', linewidth=0.5, alpha=0.85)

    # GHI overlay (derive from MidRise PV: GHI ≈ PV / (Area * η * PR))
    sub_era1 = df_solar_m[df_solar_m['era'] == 1].sort_values('month')
    pv_kwh   = sub_era1['pv_gen_kwh'].values
    eta, pr, area = 0.20, 0.80, 360.0
    ghi_kwh_m2_month = pv_kwh / (area * eta * pr)
    ghi_daily = np.array([g / d for g, d in zip(ghi_kwh_m2_month, days)])

    ax2 = ax.twinx()
    ax2.plot(months, ghi_daily, 'o-', color='#F5A623', linewidth=2.2,
             markersize=6, label='Mean daily GHI (kWh/m²/day)', zorder=5)
    ax2.fill_between(months, 0, ghi_daily, color='#F5A623', alpha=0.12)
    ax2.set_ylabel('Mean Daily GHI (kWh/m²/day)', fontsize=12, color='#F5A623')
    ax2.tick_params(axis='y', labelcolor='#F5A623', labelsize=10)
    ax2.set_ylim(0, 8)
    ax2.spines['top'].set_visible(False)

    ax.set_xticks(months)
    ax.set_xticklabels(mlabels, fontsize=10)
    ax.set_ylabel('PV Generation per Rooftop m² (kWh/m²/month)', fontsize=12)
    ax.set_xlabel('Month', fontsize=12)
    style_ax(ax)

    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2,
              fontsize=9, loc='upper left', framealpha=0.9)

    ax.set_title('Monthly PV Generation Profile and Solar Resource (Changsha)',
                 fontsize=13, fontweight='bold', pad=8)
    save_fig(fig, 'fig10_monthly_pv.png')


# =============================================================================
# FIG 11 — Future climate temperature shifts (ΔT)
# =============================================================================
def fig11_climate_temp():
    fig, ax = plt.subplots(figsize=(10, 6))

    scenarios = list(DELTA_T.keys())
    annual_dt = [np.mean(v) for v in DELTA_T.values()]
    july_dt   = [v[6] for v in DELTA_T.values()]   # July index 6
    jan_dt    = [v[0] for v in DELTA_T.values()]    # January index 0

    x = np.arange(len(scenarios))
    bar_w = 0.25

    ssp_colors = ['#2E75B6', '#6CB4E4', '#D85A30', '#FF6B35']

    b1 = ax.bar(x - bar_w, annual_dt, bar_w, color=ssp_colors, label='_',
                edgecolor='white', linewidth=0.8)
    b2 = ax.bar(x,          july_dt,  bar_w, color=ssp_colors,
                edgecolor='white', linewidth=0.8, alpha=0.75)
    b3 = ax.bar(x + bar_w,  jan_dt,   bar_w, color=ssp_colors,
                edgecolor='white', linewidth=0.8, alpha=0.50)

    for bars, label in zip([b1, b2, b3], ['Annual mean ΔT', 'July ΔT', 'January ΔT']):
        for bar, v in zip(bars, [annual_dt, july_dt, jan_dt][
                [b1, b2, b3].index(bars)]):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.06,
                    f'+{v:.1f}', ha='center', va='bottom', fontsize=9)

    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, fontsize=11)
    ax.set_ylabel('Temperature Change ΔT (°C)', fontsize=12)
    ax.set_xlabel('Climate Scenario', fontsize=12)
    style_ax(ax)
    ax.set_ylim(0, 5.8)

    # Custom legend for bar types
    ann_patch = mpatches.Patch(facecolor='#555', alpha=1.0, label='Annual mean ΔT')
    jul_patch = mpatches.Patch(facecolor='#555', alpha=0.75, label='July ΔT')
    jan_patch = mpatches.Patch(facecolor='#555', alpha=0.50, label='January ΔT')
    # SSP colors
    ssp_patches = [mpatches.Patch(color=c, label=s)
                   for c, s in zip(ssp_colors, scenarios)]
    ax.legend(handles=[ann_patch, jul_patch, jan_patch] + ssp_patches,
              fontsize=9, loc='upper left', ncol=2, framealpha=0.9)

    ax.set_title('Future Climate Temperature Shifts — CMIP6 Multi-Model Median\n'
                 '(Belcher 2005 morphing method; baseline: 1995–2014)',
                 fontsize=13, fontweight='bold', pad=8)
    save_fig(fig, 'fig11_climate_temp.png')


# =============================================================================
# FIG 12 — EUI under climate scenarios (line chart)
# =============================================================================
def fig12_climate_eui():
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), sharey=True)

    climate_order = ['Current', '2050_SSP245', '2050_SSP585',
                     '2080_SSP245', '2080_SSP585']
    climate_labels = ['Current\n(TMYx)', '2050\nSSP2-4.5', '2050\nSSP5-8.5',
                      '2080\nSSP2-4.5', '2080\nSSP5-8.5']
    x = np.arange(len(climate_order))

    for plot_idx, (era_val, era_label) in enumerate(zip([1, 2], ERA_LABELS[:2])):
        ax = axes[plot_idx]
        for retrofit, lstyle, marker, alpha in [
            ('Baseline',    '-',  'o', 1.0),
            ('R5_Combined', '--', 's', 0.85)
        ]:
            label = f'{era_label} — {retrofit.replace("_Combined", "")}'
            sub = df_climate[(df_climate['era'] == era_val) &
                             (df_climate['retrofit'] == retrofit)]
            euis = []
            for clim in climate_order:
                row = sub[sub['climate'] == clim]
                euis.append(row['total_eui_kwh_m2'].values[0] if len(row) else np.nan)

            ax.plot(x, euis, marker=marker, linestyle=lstyle,
                    color=ERA_COLORS[era_val - 1], linewidth=2.0,
                    markersize=7, label=label, alpha=alpha)
            for xi, eui in zip(x, euis):
                if not np.isnan(eui):
                    ax.text(xi, eui + 2.5, f'{eui:.1f}', ha='center',
                            fontsize=8, color=ERA_COLORS[era_val - 1])

        ax.set_xticks(x)
        ax.set_xticklabels(climate_labels, fontsize=10)
        ax.set_xlabel('Climate Scenario', fontsize=12)
        if plot_idx == 0:
            ax.set_ylabel('Total EUI (kWh/m²·yr)', fontsize=12)
        ax.set_title(f'({chr(97+plot_idx)}) {era_label}',
                     fontsize=12, fontweight='bold')
        ax.legend(fontsize=9, loc='upper right')
        style_ax(ax)

    # Also add Era 3 on second axis
    ax2 = axes[1].twinx() if False else None  # skip for clarity

    fig.suptitle('Building EUI Under Current and Future Climate Scenarios',
                 fontsize=13, fontweight='bold', y=1.01)
    save_fig(fig, 'fig12_climate_eui.png')


# =============================================================================
# FIG 13 — Heating/cooling ratio shift stacked bar
# =============================================================================
def fig13_heating_cooling_shift():
    fig, axes = plt.subplots(1, 3, figsize=(15, 6), sharey=True)

    climate_order = ['Current', '2050_SSP245', '2050_SSP585',
                     '2080_SSP245', '2080_SSP585']
    climate_labels = ['Current', '2050\nSSP2-4.5', '2050\nSSP5-8.5',
                      '2080\nSSP2-4.5', '2080\nSSP5-8.5']

    for idx, (era_val, ax) in enumerate(zip([1, 2, 3], axes)):
        sub_bl = df_climate[(df_climate['era'] == era_val) &
                            (df_climate['retrofit'] == 'Baseline')]
        x = np.arange(len(climate_order))
        heat_pct = []
        cool_pct = []
        for clim in climate_order:
            row = sub_bl[sub_bl['climate'] == clim]
            if len(row):
                h = row['heating_kwh_m2'].values[0]
                c = row['cooling_kwh_m2'].values[0]
                total = h + c
                heat_pct.append(100 * h / total if total > 0 else 0)
                cool_pct.append(100 * c / total if total > 0 else 0)
            else:
                heat_pct.append(0); cool_pct.append(0)

        bars_h = ax.bar(x, heat_pct, color=HEAT, label='Heating',
                        edgecolor='white', width=0.6)
        bars_c = ax.bar(x, cool_pct, color=COOL, label='Cooling',
                        bottom=heat_pct, edgecolor='white', width=0.6)

        for xi, hp, cp in zip(x, heat_pct, cool_pct):
            if hp > 8:
                ax.text(xi, hp/2, f'{hp:.0f}%', ha='center', va='center',
                        fontsize=8.5, color='white', fontweight='bold')
            if cp > 8:
                ax.text(xi, hp + cp/2, f'{cp:.0f}%', ha='center', va='center',
                        fontsize=8.5, color='white', fontweight='bold')

        ax.set_xticks(x)
        ax.set_xticklabels(climate_labels, fontsize=9)
        ax.set_title(f'({chr(97+idx)}) {ERA_LABELS[idx]}',
                     fontsize=12, fontweight='bold')
        if idx == 0:
            ax.set_ylabel('Heating/Cooling Share (%)', fontsize=12)
            ax.legend(fontsize=9.5, loc='upper right')
        style_ax(ax, grid=False)
        ax.set_ylim(0, 108)

    fig.suptitle('Shift in Heating vs Cooling Energy Share Under Climate Change\n'
                 '(Baseline scenario; % of total heating+cooling demand)',
                 fontsize=13, fontweight='bold', y=1.01)
    save_fig(fig, 'fig13_heating_cooling_shift.png')


# =============================================================================
# FIG 14 — Combined intervention summary: stepwise EUI reduction
# =============================================================================
def fig14_combined_summary():
    fig, ax = plt.subplots(figsize=(13, 7.5))

    steps = ['Baseline', 'R5\nRetrofit', 'R5 +\nSolar PV', '2080\nSSP5-8.5']
    step_colors = [OTHER, COOL, PV, '#C00000']
    x = np.arange(len(steps))
    n_eras = 3
    bar_w = 0.22

    # Prepare EUI values per step
    # Step 3 (2080 SSP5-8.5): R5 EUI under worst future climate
    r5_2080 = {}
    for era in [1, 2, 3]:
        row = df_climate[(df_climate['era'] == era) &
                         (df_climate['retrofit'] == 'R5_Combined') &
                         (df_climate['climate'] == '2080_SSP585')]
        r5_2080[era] = row['total_eui_kwh_m2'].values[0] if len(row) else np.nan

    step_data = {}
    for era in [1, 2, 3]:
        bl_row  = df_retro[(df_retro['era'] == era) &
                           (df_retro['retrofit'] == 'Baseline')].iloc[0]
        r5_row  = df_retro[(df_retro['era'] == era) &
                           (df_retro['retrofit'] == 'R5_Combined')].iloc[0]
        solar_r = df_solar[(df_solar['era'] == era) &
                           (df_solar['retrofit'] == 'R5_Combined')].iloc[0]
        step_data[era] = [
            bl_row['total_eui_kwh_m2'],
            r5_row['total_eui_kwh_m2'],
            solar_r['net_eui_kwh_m2'],
            r5_2080[era],
        ]

    for i, (era, ec, el) in enumerate(zip([1, 2, 3], ERA_COLORS, ERA_LABELS)):
        vals = step_data[era]
        offset = (i - 1) * bar_w
        bars = ax.bar(x + offset, vals, bar_w, color=ec, label=el,
                      edgecolor='white', linewidth=0.8, alpha=0.88)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                    f'{v:.1f}', ha='center', va='bottom', fontsize=9,
                    fontweight='bold', color=ec)

    # Metric cards: total reduction baseline → R5+PV
    card_texts = []
    for era in [1, 2, 3]:
        bl   = step_data[era][0]
        net  = step_data[era][2]
        pct  = 100 * (bl - net) / bl
        card_texts.append(f'{pct:.1f}%\nsaving\n(baseline → R5+PV)')

    card_y = max([max(v) for v in step_data.values()]) * 1.08
    for i, (era, ec, ct) in enumerate(zip([1, 2, 3], ERA_COLORS, card_texts)):
        offset = (i - 1) * bar_w
        xi = 0 + offset  # above first bar
        ax.text(4.0 + (i - 1) * 0.55, card_y,
                f'{ERA_LABELS[i].split(" ")[0]} {ERA_LABELS[i].split(" ")[1]}\n{ct}',
                ha='center', va='bottom', fontsize=9.5, color=ec,
                fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor=ec, linewidth=1.5, alpha=0.9))

    ax.set_xticks(x)
    ax.set_xticklabels(steps, fontsize=11)
    ax.set_ylabel('Total EUI (kWh/m²·yr)', fontsize=12)
    ax.set_xlabel('Intervention Stage', fontsize=12)
    ax.legend(fontsize=10, loc='upper right')
    style_ax(ax)
    ax.set_ylim(0, card_y + 70)
    ax.set_xlim(-0.7, 4.5)

    # Add step labels on top of x-axis area
    step_labels2 = ['Baseline\nperformance', 'After\nR5 retrofit',
                    'After R5\n+ Solar PV', 'R5 under 2080\nSSP5-8.5']
    for xi, lbl in zip(x, step_labels2):
        ax.text(xi, -22, lbl, ha='center', fontsize=8.5, color='#555',
                style='italic')

    ax.set_title('Stepwise EUI Reduction: Baseline → Retrofit → Solar PV → Future Climate',
                 fontsize=13, fontweight='bold', pad=8)
    save_fig(fig, 'fig14_combined_summary.png')


# =============================================================================
# Main
# =============================================================================
if __name__ == '__main__':
    print('Generating all 14 figures...\n')
    fig01_study_area()
    fig02_methodology()
    fig03_archetypes()
    fig04_baseline_eui()
    fig05_morris_scatter()
    fig06_parameter_ranking()
    fig07_retrofit_savings()
    fig08_eui_before_after()
    fig09_solar_pv_demand()
    fig10_monthly_pv()
    fig11_climate_temp()
    fig12_climate_eui()
    fig13_heating_cooling_shift()
    fig14_combined_summary()
    print(f'\nAll 14 figures saved to {FIG}/')
