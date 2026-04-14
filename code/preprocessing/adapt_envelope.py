"""
adapt_envelope.py
=================
Modifies DOE prototype residential IDF files to match Chinese residential
construction standards for three building eras (JGJ 134-2010, HSCW zone).

Primary implementation uses **eppy** (requires EnergyPlus + matching IDD).
Falls back to robust text-based IDF editing when the IDD is unavailable.

Usage:
    python adapt_envelope.py

Outputs:
    data/models/changsha_era1.idf   (~1980s, pre-code, no insulation)
    data/models/changsha_era2.idf   (~2000s, partial insulation)
    data/models/changsha_era3.idf   (~2010s+, JGJ 134-2010 code-compliant)

Reference:
    JGJ 134-2010 Design Standard for Energy Efficiency of Residential
    Buildings in Hot Summer and Cold Winter Zone.
    Chen et al. (2022) Building Simulation — Changsha archetype study.
"""

import os
import re
import sys
import math
import copy
import shutil
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
DATA_MODELS = os.path.join(REPO_ROOT, "data", "models")
DATA_CLIMATE = os.path.join(REPO_ROOT, "data", "climate")

EPW_FILE = os.path.join(
    DATA_CLIMATE,
    "CHN_HN_Changsha.576870_TMYx.2007-2021.epw",
)

BASE_MIDRISE = os.path.join(
    DATA_MODELS, "ASHRAE901_ApartmentMidRise_STD2004_Atlanta.idf"
)
BASE_HIGHRISE = os.path.join(
    DATA_MODELS, "ASHRAE901_ApartmentHighRise_STD2019_Atlanta.idf"
)

OUTPUT_FILES = {
    1: os.path.join(DATA_MODELS, "changsha_era1.idf"),
    2: os.path.join(DATA_MODELS, "changsha_era2.idf"),
    3: os.path.join(DATA_MODELS, "changsha_era3.idf"),
}

# ---------------------------------------------------------------------------
# Era definitions  (JGJ 134-2010, HSCW zone)
# ---------------------------------------------------------------------------
ERA_PARAMS = {
    1: {
        "label": "Era-1 (~1980s): pre-code, no insulation",
        "base_idf": BASE_MIDRISE,
        "wall_U": 1.5,      # W/m²K  (single-wythe brick, ~200 mm)
        "roof_U": 1.2,      # concrete slab, no insulation
        "window_U": 5.8,    # single-pane clear glass
        "window_SHGC": 0.70,
        "WWR": 0.25,
        "infil_ACH": 1.5,
    },
    2: {
        "label": "Era-2 (~2000s): partial insulation",
        "base_idf": BASE_MIDRISE,
        "wall_U": 1.0,      # brick + thin EPS board
        "roof_U": 0.8,      # concrete + expanded polystyrene
        "window_U": 3.5,    # double-pane clear glass
        "window_SHGC": 0.55,
        "WWR": 0.30,
        "infil_ACH": 1.0,
    },
    3: {
        "label": "Era-3 (~2010s+): JGJ 134-2010 code-compliant",
        "base_idf": BASE_HIGHRISE,
        "wall_U": 0.6,      # brick + XPS, meets JGJ 134 limit
        "roof_U": 0.4,      # SBS membrane + XPS
        "window_U": 2.5,    # low-e double-pane
        "window_SHGC": 0.40,
        "WWR": 0.40,
        "infil_ACH": 0.5,
    },
}

# EnergyPlus surface film resistances (ISO 6946, used to compute bulk R)
R_SI_WALL = 0.13   # m²K/W  internal surface
R_SE_WALL = 0.04   # m²K/W  external surface
R_SI_ROOF = 0.10
R_SE_ROOF = 0.04


# ===========================================================================
# Part 1 — eppy-based implementation (preferred when EnergyPlus IDD available)
# ===========================================================================

def find_idd():
    """
    Search for an EnergyPlus IDD file on the local system.
    Returns path string or None if not found.
    """
    candidate_dirs = [
        "/usr/local/EnergyPlus",
        "/Applications/EnergyPlus-26-1-0",
        "/Applications/EnergyPlus-24-1-0",
        "/Applications/EnergyPlus-23-1-0",
        "/Applications/EnergyPlus-22-1-0",
        os.path.expanduser("~/EnergyPlus"),
        os.environ.get("ENERGYPLUS_DIR", ""),
    ]
    for d in candidate_dirs:
        if not d:
            continue
        for name in ("Energy+.idd", "Energy+V22_1.idd"):
            idd = os.path.join(d, name)
            if os.path.isfile(idd):
                return idd

    # Check eppy's bundled IDDs (oldest-to-newest, pick newest)
    try:
        import eppy
        ep_dir = os.path.dirname(eppy.__file__)
        idd_dir = os.path.join(ep_dir, "resources", "iddfiles")
        idds = sorted(
            f for f in os.listdir(idd_dir) if f.endswith(".idd")
        )
        if idds:
            return os.path.join(idd_dir, idds[-1])
    except Exception:
        pass
    return None


def u_to_nomass_r(U, r_si, r_se):
    """Convert target U-value to bulk R-value of opaque material layer."""
    r_total = 1.0 / U
    r_bulk = r_total - r_si - r_se
    return max(r_bulk, 0.02)


def adapt_with_eppy(era_num, params, output_path):
    """
    Load IDF with eppy, apply Chinese-era envelope properties, and save.
    Returns True on success, False on failure.
    """
    from eppy.modeleditor import IDF
    from eppy import modeleditor

    idd = find_idd()
    if idd is None:
        log.warning("  [eppy] No IDD found — skipping eppy path.")
        return False

    try:
        try:
            IDF.setiddname(idd)
        except modeleditor.IDDAlreadySetError:
            pass

        idf = IDF(params["base_idf"])
    except Exception as e:
        log.warning(f"  [eppy] Failed to load IDF: {e}")
        return False

    # --- Site:Location ---
    loc_objs = idf.idfobjects.get("SITE:LOCATION", [])
    if loc_objs:
        loc = loc_objs[0]
        loc.Name = "Changsha"
        loc.Latitude = 28.22
        loc.Longitude = 112.93
        loc.Time_Zone = 8.0
        loc.Elevation = 44.0

    # --- Wall + Roof constructions ---
    wall_r = u_to_nomass_r(params["wall_U"], R_SI_WALL, R_SE_WALL)
    roof_r = u_to_nomass_r(params["roof_U"], R_SI_ROOF, R_SE_ROOF)

    def _add_nomass(idf, name, r_val):
        existing = [m for m in idf.idfobjects.get("MATERIAL:NOMASS", [])
                    if m.Name == name]
        mat = existing[0] if existing else idf.newidfobject("MATERIAL:NOMASS")
        mat.Name = name
        mat.Roughness = "MediumRough"
        mat.Thermal_Resistance = r_val
        mat.Thermal_Absorptance = 0.9
        mat.Solar_Absorptance = 0.7
        mat.Visible_Absorptance = 0.7
        return mat

    def _add_construction(idf, name, layer):
        existing = [c for c in idf.idfobjects.get("CONSTRUCTION", [])
                    if c.Name == name]
        con = existing[0] if existing else idf.newidfobject("CONSTRUCTION")
        con.Name = name
        con.Outside_Layer = layer
        return con

    _add_nomass(idf, "CN_Wall_Insulation", wall_r)
    _add_nomass(idf, "CN_Roof_Insulation", roof_r)
    _add_construction(idf, "CN_Ext_Wall", "CN_Wall_Insulation")
    _add_construction(idf, "CN_Ext_Roof", "CN_Roof_Insulation")

    for s in idf.idfobjects.get("BUILDINGSURFACE:DETAILED", []):
        if (getattr(s, "Outside_Boundary_Condition", "").lower() == "outdoors"):
            st = getattr(s, "Surface_Type", "").lower()
            if st == "wall":
                s.Construction_Name = "CN_Ext_Wall"
            elif st == "roof":
                s.Construction_Name = "CN_Ext_Roof"

    # --- Window glazing ---
    for mat in idf.idfobjects.get("WINDOWMATERIAL:SIMPLEGLAZINGSYSTEM", []):
        mat.UFactor = params["window_U"]
        mat.Solar_Heat_Gain_Coefficient = params["window_SHGC"]

    # --- Infiltration ---
    for obj in idf.idfobjects.get("ZONEINFILTRATION:DESIGNFLOWRATE", []):
        obj.Design_Flow_Rate_Calculation_Method = "AirChanges/Hour"
        obj.Design_Flow_Rate = ""
        obj.Flow_per_Zone_Floor_Area = ""
        obj.Flow_per_Exterior_Surface_Area = ""
        obj.Air_Changes_per_Hour = params["infil_ACH"]
        obj.Constant_Term_Coefficient = 1.0
        obj.Temperature_Term_Coefficient = 0.0
        obj.Velocity_Term_Coefficient = 0.0
        obj.Velocity_Squared_Term_Coefficient = 0.0

    idf.save(output_path)
    log.info(f"  [eppy] Saved {os.path.basename(output_path)}")
    return True


# ===========================================================================
# Part 2 — Text-based IDF editor (fallback when IDD version mismatch)
# ===========================================================================

class TextIDF:
    """
    Minimal IDF reader/writer for targeted envelope modifications.
    Parses IDF as structured text; no IDD required.
    """

    def __init__(self, path):
        with open(path, "r", encoding="latin-1") as f:
            self.text = f.read()
        self.path = path

    # ---- helpers -----------------------------------------------------------

    @staticmethod
    def _obj_pattern(obj_type):
        """Return a regex that matches a complete IDF object of given type."""
        return re.compile(
            r"(?m)^\s*" + re.escape(obj_type) + r",\s*\n((?:.*\n)*?.*?;)",
            re.IGNORECASE,
        )

    def get_objects(self, obj_type):
        """Return list of raw string blocks for all objects of obj_type."""
        pat = self._obj_pattern(obj_type)
        return pat.findall(self.text)

    # ---- site location -----------------------------------------------------

    def set_location(self, name, lat, lon, tz, elev):
        """Update Site:Location values."""
        def repl(m):
            block = m.group(0)
            block = re.sub(r"(?m)^(\s*)(.*?)(,\s*!-\s*Name)", lambda x: f"{x.group(1)}{name}{x.group(3)}", block, count=1)
            return block

        # Simple approach: replace field by field using comment markers
        text = self.text
        # Update latitude
        text = re.sub(
            r"(Site:Location,.*?!-\s*Name.*?\n.*?,)\s*[0-9eE.+-]+(\s*!-\s*Latitude)",
            lambda m: m.group(1) + f"  {lat}" + m.group(2),
            text, flags=re.IGNORECASE | re.DOTALL, count=1
        )
        self.text = text

    # ---- construction / material replacement --------------------------------

    def _build_nomass_block(self, name, r_val):
        return (
            f"  Material:NoMass,\n"
            f"    {name},             !- Name\n"
            f"    MediumRough,        !- Roughness\n"
            f"    {r_val:.6f},        !- Thermal Resistance {{m2-K/W}}\n"
            f"    0.9,               !- Thermal Absorptance\n"
            f"    0.7,               !- Solar Absorptance\n"
            f"    0.7;               !- Visible Absorptance\n"
        )

    def _build_construction_block(self, name, layer):
        return (
            f"  Construction,\n"
            f"    {name},            !- Name\n"
            f"    {layer};           !- Outside Layer\n"
        )

    def add_block(self, block):
        """Append a new IDF object block before the final blank line."""
        self.text = self.text.rstrip() + "\n\n" + block + "\n"

    def replace_construction_on_surfaces(self, surf_type_kw, new_construction):
        """
        Replace Construction_Name field for exterior surfaces matching surf_type_kw.
        surf_type_kw: 'Wall' or 'Roof'
        """
        # BuildingSurface:Detailed objects have comma-delimited fields
        # Field 3: Surface Type, Field 4: Construction Name, Field 6: Outside BC
        count = 0

        def replace_bs(m):
            nonlocal count
            block = m.group(0)
            # Only act on exterior (Outdoors) surfaces of the right type
            lines = block.split("\n")
            fields = []
            for ln in lines:
                # strip comment
                code = ln.split("!")[0].strip().rstrip(",").rstrip(";").strip()
                if code:
                    fields.append(code)
            if len(fields) < 6:
                return block
            # fields[0]=type, [1]=name, [2]=surf_type, [3]=construction,
            # [4]=zone, [5]=outside_bc_object, [6]=outside_bc,...
            if (surf_type_kw.lower() in fields[2].lower()
                    and "outdoor" in "".join(fields).lower()):
                # Replace construction field (index 3 in 0-based fields)
                # Find the 4th comma-delimited value in the block text
                # and replace it
                new_block = _replace_nth_field(block, 4, new_construction)
                count += 1
                return new_block
            return block

        pat = re.compile(
            r"(?m)^\s*BuildingSurface:Detailed,\s*\n((?:.*\n)*?.*?;)",
            re.IGNORECASE,
        )
        self.text = pat.sub(lambda m: replace_bs(m), self.text)
        log.info(f"  [text] Replaced {count} {surf_type_kw} surface constructions → {new_construction}")

    # ---- window glazing -----------------------------------------------------

    def set_window_ufactor_shgc(self, u_val, shgc_val):
        """Update U-Factor and SHGC in all WindowMaterial:SimpleGlazingSystem."""
        pat = re.compile(
            r"(?m)(WindowMaterial:SimpleGlazingSystem,\s*\n"
            r".*?,\s*!-\s*Name\s*\n)"   # name field
            r"(\s*)([0-9eE.+-]+)(\s*,\s*!-.*?U-Factor.*?\n)"  # U-Factor
            r"(\s*)([0-9eE.+-]+)(\s*[,;]?\s*!-.*?Solar Heat Gain.*?\n)",  # SHGC
            re.IGNORECASE,
        )
        count = [0]

        def repl(m):
            count[0] += 1
            return (
                m.group(1)
                + m.group(2) + str(u_val) + m.group(4)
                + m.group(5) + str(shgc_val) + m.group(7)
            )

        self.text = pat.sub(repl, self.text)
        log.info(f"  [text] Updated {count[0]} window glazing: U={u_val}, SHGC={shgc_val}")

    # ---- infiltration -------------------------------------------------------

    def set_infiltration_ach(self, ach):
        """
        Convert all ZoneInfiltration:DesignFlowRate objects to AirChanges/Hour.
        """
        def repl_infil(m):
            block = m.group(0)
            # Replace calculation method
            block = re.sub(
                r"(Flow/ExteriorWallArea|Flow/Zone|Flow/ExteriorArea|AirChanges/Hour)",
                "AirChanges/Hour",
                block, flags=re.IGNORECASE, count=1
            )
            # Replace flow-per-exterior-wall-area value with empty (field 9 ~ index 8)
            # and set air-changes-per-hour (field 10 ~ index 9)
            # Approach: replace numeric values in specific comment-tagged fields
            block = re.sub(
                r"(\s*)([0-9eE.+-]+)(\s*,?\s*!-\s*Design Flow Rate\b[^,\n]*)",
                r"\g<1>0\g<3>", block, flags=re.IGNORECASE, count=1
            )
            block = re.sub(
                r"(\s*)([0-9eE.+-]+)(\s*,?\s*!-\s*Flow per Zone Floor Area[^,\n]*)",
                r"\g<1>\g<3>", block, flags=re.IGNORECASE, count=1
            )
            block = re.sub(
                r"(\s*)([0-9eE.+-]+)(\s*,?\s*!-\s*Flow per Exterior Surface Area[^,\n]*)",
                r"\g<1>\g<3>", block, flags=re.IGNORECASE, count=1
            )
            block = re.sub(
                r"(\s*),(\s*!-\s*Air Changes per Hour[^,\n]*\n)",
                rf"\g<1>{ach}\g<2>", block, flags=re.IGNORECASE, count=1
            )
            block = re.sub(
                r"(\s*)([0-9eE.+-]+)(\s*,?\s*!-\s*Air Changes per Hour[^,\n]*)",
                rf"\g<1>{ach}\g<3>", block, flags=re.IGNORECASE, count=1
            )
            # Set wind/temp coefficients to constant=1, rest=0
            block = re.sub(
                r"(\s*)([0-9eE.+-]+)(\s*,?\s*!-\s*Constant Term Coefficient[^,\n]*)",
                r"\g<1>1.0\g<3>", block, flags=re.IGNORECASE, count=1
            )
            block = re.sub(
                r"(\s*)([0-9eE.+-]+)(\s*,?\s*!-\s*Temperature Term Coefficient[^,\n]*)",
                r"\g<1>0.0\g<3>", block, flags=re.IGNORECASE, count=1
            )
            block = re.sub(
                r"(\s*)([0-9eE.+-]+)(\s*,?\s*!-\s*Velocity Term Coefficient[^,\n]*\n)",
                r"\g<1>0.0\g<3>", block, flags=re.IGNORECASE, count=1
            )
            block = re.sub(
                r"(\s*)([0-9eE.+-]+)(\s*;?\s*!-\s*Velocity Squared Term Coefficient[^;\n]*)",
                r"\g<1>0.0\g<3>", block, flags=re.IGNORECASE, count=1
            )
            return block

        pat = re.compile(
            r"(?m)^\s*ZoneInfiltration:DesignFlowRate,\s*\n(?:.*\n)*?.*?;",
            re.IGNORECASE,
        )
        orig = self.text
        self.text = pat.sub(repl_infil, self.text)
        n = len(pat.findall(orig))
        log.info(f"  [text] Set infiltration to {ach} ACH ({n} zones)")

    # ---- WWR ----------------------------------------------------------------

    def set_wwr(self, target_wwr):
        """
        Scale all FenestrationSurface:Detailed vertex coordinates about their
        centroids to achieve the target window-to-wall ratio.
        """
        # Collect all BuildingSurface:Detailed exterior walls and their areas
        wall_areas = {}  # name → area
        _bs_pat = re.compile(
            r"(?m)^\s*BuildingSurface:Detailed,\s*\n((?:.*\n)*?.*?;)",
            re.IGNORECASE,
        )
        for m in _bs_pat.finditer(self.text):
            block = m.group(0)
            fields = _extract_fields(block)
            if len(fields) < 9:
                continue
            if ("wall" in fields[2].lower()
                    and "outdoor" in "".join(fields).lower()):
                verts = _extract_vertices(block)
                if verts:
                    wall_areas[fields[1]] = _poly_area_3d(verts)

        if not wall_areas:
            log.warning("  [text] No exterior wall surfaces found for WWR adjustment")
            return

        # For each FenestrationSurface:Detailed on an exterior wall, scale vertices
        _fs_pat = re.compile(
            r"(?m)^\s*FenestrationSurface:Detailed,\s*\n((?:.*\n)*?.*?;)",
            re.IGNORECASE,
        )
        total_scaled = 0

        def scale_fen(m):
            nonlocal total_scaled
            block = m.group(0)
            fields = _extract_fields(block)
            if len(fields) < 5:
                return block
            parent_name = fields[4]  # Building Surface Name
            if parent_name not in wall_areas:
                return block
            wall_area = wall_areas[parent_name]
            if wall_area < 0.01:
                return block

            verts = _extract_vertices(block)
            if not verts:
                return block
            win_area = _poly_area_3d(verts)
            if win_area < 0.001:
                return block

            # Current WWR for this wall/window pair
            # Scale all windows on each wall uniformly
            target_win_area = target_wwr * wall_area
            # Collect all windows on this parent wall to get current total
            # (simplified: treat each window independently with same scale)
            scale = math.sqrt(target_wwr / (win_area / wall_area))
            scale = min(scale, 0.97)  # cap at 97% of wall area

            new_verts = _scale_poly(verts, scale)
            new_block = _replace_vertices(block, new_verts)
            total_scaled += 1
            return new_block

        self.text = _fs_pat.sub(scale_fen, self.text)
        log.info(f"  [text] Scaled {total_scaled} windows toward WWR={target_wwr:.2f}")

    # ---- site metadata ------------------------------------------------------

    def set_location_changsha(self):
        """Set Site:Location to Changsha."""
        pat = re.compile(
            r"(?m)(^\s*Site:Location,\s*\n)((?:.*\n)*?.*?;)",
            re.IGNORECASE,
        )

        def repl(m):
            return (
                m.group(1)
                + "  Changsha,                !- Name\n"
                + "  28.22,                   !- Latitude {deg}\n"
                + "  112.93,                  !- Longitude {deg}\n"
                + "  8.0,                     !- Time Zone {hr}\n"
                + "  44.0;                    !- Elevation {m}\n"
            )

        self.text = pat.sub(repl, self.text, count=1)

    # ---- save ---------------------------------------------------------------

    def save(self, out_path):
        with open(out_path, "w", encoding="latin-1") as f:
            f.write(self.text)
        log.info(f"  [text] Saved {os.path.basename(out_path)}")


# ---------------------------------------------------------------------------
# Geometry helpers (used by TextIDF)
# ---------------------------------------------------------------------------

def _extract_fields(block):
    """
    Extract ordered field values from an IDF object block.

    Strategy:
      1. Strip all end-of-line comments (! ... ) so the next field
         value on the following line is not discarded.
      2. Split on commas and semicolons.
      3. Strip whitespace; skip empty tokens.

    First element is the object type (e.g. 'BuildingSurface:Detailed').
    """
    # Remove comments: everything from '!' to end of line
    stripped = re.sub(r"!.*", "", block)
    fields = []
    for token in re.split(r"[,;]", stripped):
        val = token.strip()
        if val:
            fields.append(val)
    return fields


def _extract_vertices(block):
    """
    Parse vertex coordinate triplets from an IDF surface block.
    Handles two EnergyPlus vertex formats:

    Format A (BuildingSurface:Detailed):
        0.0,0.0,3.05,  !- X,Y,Z ==> Vertex 1 {m}

    Format B (FenestrationSurface:Detailed):
        2.895,    !- Vertex 1 X-coordinate {m}
        0,        !- Vertex 1 Y-coordinate {m}
        0.954,    !- Vertex 1 Z-coordinate {m}

    Returns list of (x, y, z) tuples.
    """
    verts = []

    # Format B: individual X / Y / Z lines with 'X-coordinate', 'Y-coordinate', 'Z-coordinate'
    coord_b = re.compile(
        r"(?m)^\s*([0-9eE.+-]+)\s*[,;]\s*!-\s*Vertex\s*\d+\s+[XYZ]-coordinate"
    )
    coords_b = coord_b.findall(block)
    if coords_b:
        for i in range(0, len(coords_b) - 2, 3):
            try:
                verts.append((float(coords_b[i]), float(coords_b[i+1]), float(coords_b[i+2])))
            except (ValueError, IndexError):
                break
        return verts

    # Format A: triplets on one line  "X,Y,Z, !- X,Y,Z ==> Vertex N {m}"
    coord_a = re.compile(
        r"(?m)^\s*([0-9eE.+-]+),([0-9eE.+-]+),([0-9eE.+-]+)[,;]?\s*!-\s*X,Y,Z\s*==>"
    )
    for m in coord_a.finditer(block):
        try:
            verts.append((float(m.group(1)), float(m.group(2)), float(m.group(3))))
        except ValueError:
            continue
    return verts


def _poly_area_3d(verts):
    """Compute area of a planar polygon using cross-product accumulation."""
    n = len(verts)
    if n < 3:
        return 0.0
    normal = [0.0, 0.0, 0.0]
    v0 = verts[0]
    for i in range(1, n - 1):
        v1 = verts[i]
        v2 = verts[i + 1]
        e1 = (v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2])
        e2 = (v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2])
        normal[0] += e1[1]*e2[2] - e1[2]*e2[1]
        normal[1] += e1[2]*e2[0] - e1[0]*e2[2]
        normal[2] += e1[0]*e2[1] - e1[1]*e2[0]
    return 0.5 * math.sqrt(sum(x**2 for x in normal))


def _scale_poly(verts, scale):
    """Scale polygon vertices about centroid."""
    n = len(verts)
    cx = sum(v[0] for v in verts) / n
    cy = sum(v[1] for v in verts) / n
    cz = sum(v[2] for v in verts) / n
    return [
        (cx + scale*(v[0]-cx), cy + scale*(v[1]-cy), cz + scale*(v[2]-cz))
        for v in verts
    ]


def _replace_vertices(block, new_verts):
    """
    Replace vertex coordinates in a FenestrationSurface:Detailed block.
    Handles Format B (individual X-coordinate / Y-coordinate / Z-coordinate lines).
    """
    coord_lines = re.compile(
        r"(?m)(^\s*)([0-9eE.+-]+)(\s*[,;]\s*!-\s*Vertex\s*\d+\s+[XYZ]-coordinate.*)"
    )
    flat = [c for v in new_verts for c in v]
    i = [0]

    def repl(m):
        if i[0] >= len(flat):
            return m.group(0)
        val = flat[i[0]]
        i[0] += 1
        return f"{m.group(1)}{val:.6f}{m.group(3)}"

    return coord_lines.sub(repl, block)


def _replace_nth_field(block, n, new_val):
    """
    Replace the n-th comma/semicolon-delimited field in an IDF object block.
    Field indices are 1-based (field 1 = object type).
    """
    # Tokenize by commas and semicolons, preserving delimiters and comments
    count = [0]

    def repl(m):
        count[0] += 1
        if count[0] == n:
            pre = m.group(1)  # indent
            post = m.group(3)  # delimiter + comment
            return f"{pre}{new_val}{post}"
        return m.group(0)

    pat = re.compile(r"(?m)(^\s*)([^,;\n!]+)([,;][ \t]*(?:![^\n]*)?\n?)")
    return pat.sub(repl, block)


# ===========================================================================
# Part 3 — Orchestration
# ===========================================================================

def adapt_idf(era_num, params, output_path):
    """Apply era-specific Chinese residential envelope properties to base IDF."""
    log.info(f"\n=== Era {era_num}: {params['label']} ===")
    log.info(f"  Base: {os.path.basename(params['base_idf'])}")

    # Try eppy first
    try:
        import eppy
        success = adapt_with_eppy(era_num, params, output_path)
        if success:
            return
        log.info("  eppy path failed — using text-based fallback")
    except ImportError:
        log.info("  eppy not installed — using text-based fallback")

    # Text-based fallback
    adapt_with_text(era_num, params, output_path)


def adapt_with_text(era_num, params, output_path):
    """Text-based IDF modification (fallback when eppy IDD unavailable)."""
    wall_r = u_to_nomass_r(params["wall_U"], R_SI_WALL, R_SE_WALL)
    roof_r = u_to_nomass_r(params["roof_U"], R_SI_ROOF, R_SE_ROOF)

    log.info(f"  Wall R_bulk = {wall_r:.3f} m²K/W  (U_target={params['wall_U']})")
    log.info(f"  Roof R_bulk = {roof_r:.3f} m²K/W  (U_target={params['roof_U']})")

    tidf = TextIDF(params["base_idf"])

    # 1. Add Material:NoMass + Construction objects for wall & roof
    tidf.add_block(tidf._build_nomass_block("CN_Wall_Insulation", wall_r))
    tidf.add_block(tidf._build_nomass_block("CN_Roof_Insulation", roof_r))
    tidf.add_block(tidf._build_construction_block("CN_Ext_Wall", "CN_Wall_Insulation"))
    tidf.add_block(tidf._build_construction_block("CN_Ext_Roof", "CN_Roof_Insulation"))

    # 2. Point exterior wall/roof surfaces to new constructions
    tidf.replace_construction_on_surfaces("Wall", "CN_Ext_Wall")
    tidf.replace_construction_on_surfaces("Roof", "CN_Ext_Roof")

    # 3. Window glazing (U-factor and SHGC)
    tidf.set_window_ufactor_shgc(params["window_U"], params["window_SHGC"])

    # 4. Infiltration
    tidf.set_infiltration_ach(params["infil_ACH"])

    # 5. Window-to-wall ratio
    tidf.set_wwr(params["WWR"])

    # 6. Update Site:Location comment (informational)
    tidf.text = (
        f"! Adapted for Changsha HSCW zone, Era {era_num}\n"
        f"! Wall U={params['wall_U']} W/m2K, Roof U={params['roof_U']}, "
        f"Window U={params['window_U']}, SHGC={params['window_SHGC']}\n"
        f"! WWR={params['WWR']}, Infiltration={params['infil_ACH']} ACH\n"
        f"! Weather: {os.path.basename(EPW_FILE)}\n"
        f"! Ref: JGJ 134-2010 (HSCW zone residential energy standard)\n\n"
    ) + tidf.text

    tidf.save(output_path)


def main():
    os.makedirs(DATA_MODELS, exist_ok=True)

    if not os.path.isfile(EPW_FILE):
        log.warning(f"EPW file not found at expected path: {EPW_FILE}")

    for era_num, params in sorted(ERA_PARAMS.items()):
        if not os.path.isfile(params["base_idf"]):
            log.error(f"Base IDF missing: {params['base_idf']}")
            log.error("Run Task 2 to download DOE prototype IDF files first.")
            continue
        adapt_idf(era_num, params, OUTPUT_FILES[era_num])

    log.info("\nDone. Output files:")
    for era, path in OUTPUT_FILES.items():
        exists = os.path.isfile(path)
        size = f"{os.path.getsize(path)//1024}KB" if exists else "MISSING"
        log.info(f"  Era {era}: {os.path.basename(path)}  ({size})")

    log.info("\nTo simulate:")
    log.info(f"  energyplus -w {EPW_FILE} -d results/era1 data/models/changsha_era1.idf")


if __name__ == "__main__":
    main()
