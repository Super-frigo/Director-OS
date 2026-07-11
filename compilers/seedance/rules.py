"""Seedance translation rules — deterministic lookup tables.

Every rule maps a Project schema value to a Seedance natural-language fragment.
No TODOs, no placeholder strings.  These tables are the single source of truth
for how Shot Grammar enums become Seedance prompt text.

The tables mirror the valid enum sets defined in schemas/project_schema.py.
"""

from typing import Dict

# ============================================================================
# Framing → Seedance description
# ============================================================================

FRAMING_MAP: Dict[str, str] = {
    "ECU":         "extreme close-up",
    "CU":          "close-up",
    "MCU":         "medium close-up",
    "MS":          "medium shot",
    "MLS":         "medium long shot",
    "LS":          "wide shot",
    "ELS":         "extreme wide shot",
    "EST":         "establishing wide shot",
    "OTS":         "over-the-shoulder shot",
    "POV":         "point-of-view shot",
    "TWO_SHOT":    "two-shot",
    "GROUP_SHOT":  "group shot",
    "INSERT":      "insert shot",
    "DETAIL":      "detail close-up",
}

# ============================================================================
# Angle → Seedance description
# ============================================================================

ANGLE_MAP: Dict[str, str] = {
    "EYE_LEVEL":   "eye-level",
    "HIGH_ANGLE":  "high angle looking down",
    "LOW_ANGLE":   "low angle looking up",
    "BIRDS_EYE":   "bird's-eye view from above",
    "WORMS_EYE":   "worm's-eye view from ground level",
    "DUTCH_ANGLE": "dutch angle canted frame",
    "OVERHEAD":    "overhead top-down view",
    "CANTED":      "canted dutch tilt",
}

# ============================================================================
# Camera Height → Seedance description
# ============================================================================

HEIGHT_MAP: Dict[str, str] = {
    "GROUND":    "ground-level camera",
    "WAIST":     "waist-high camera",
    "CHEST":     "chest-high camera",
    "EYE":       "eye-level camera",
    "ABOVE_EYE": "above-eye camera",
    "HIGH":      "high camera position",
    "CEILING":   "ceiling-height camera",
}

# ============================================================================
# Lens → Seedance description
# ============================================================================

LENS_MAP: Dict[str, str] = {
    "14mm":   "14mm ultra-wide lens",
    "18mm":   "18mm wide-angle lens",
    "24mm":   "24mm wide-angle lens",
    "35mm":   "35mm standard wide lens",
    "50mm":   "50mm standard lens",
    "85mm":   "85mm portrait lens",
    "100mm":  "100mm medium telephoto lens",
    "135mm":  "135mm telephoto lens",
    "200mm":  "200mm telephoto lens",
    "400mm+": "400mm super telephoto lens",
}

# ============================================================================
# Camera Movement → Seedance description
# ============================================================================

MOVEMENT_MAP: Dict[str, str] = {
    "STATIC":      "static camera",
    "PAN_L":       "panning left",
    "PAN_R":       "panning right",
    "TILT_UP":     "tilting up",
    "TILT_DOWN":   "tilting down",
    "DOLLY_IN":    "dollying in",
    "DOLLY_OUT":   "dollying out",
    "TRACK_L":     "tracking left",
    "TRACK_R":     "tracking right",
    "TRACK_F":     "tracking forward",
    "TRACK_B":     "tracking backward",
    "ARC_L":       "arcing left around subject",
    "ARC_R":       "arcing right around subject",
    "BOOM_UP":     "booming up",
    "BOOM_DOWN":   "booming down",
    "HANDHELD":    "handheld camera",
    "STEADICAM":   "steadicam smooth following",
    "GIMBAL":      "gimbal-stabilized movement",
    "CRANE":       "crane shot",
    "DRONE":       "drone aerial shot",
    "ZOOM_IN":     "zooming in",
    "ZOOM_OUT":    "zooming out",
    "DUTCH_TILT":  "dutch angle tilt",
    "WHIP_PAN":    "whip pan",
    "SNAP_ZOOM":   "snap zoom",
    "RACK_FOCUS":  "rack focus pull",
}

# ============================================================================
# Focus → Seedance description
# ============================================================================

FOCUS_MAP: Dict[str, str] = {
    "DEEP_FOCUS":    "deep focus",
    "SHALLOW_FOCUS": "shallow focus",
    "RACK_FOCUS":    "rack focus",
    "SOFT_FOCUS":    "soft focus",
    "PULL_FOCUS":    "pull focus",
    "MACRO_FOCUS":   "macro focus",
    "INFRARED":      "infrared",
    "MOTION_BLUR":   "motion blur",
    "SPLIT_DIOPTER": "split diopter",
}

# ============================================================================
# Lighting Type → Seedance description
# ============================================================================

LIGHTING_TYPE_MAP: Dict[str, str] = {
    "NATURAL":       "natural light",
    "HARD":          "hard direct light",
    "SOFT":          "soft diffused light",
    "MOTIVATED":     "motivated naturalistic light",
    "PRACTICAL":     "practical in-scene light sources",
    "CONTRAST":      "high-contrast light",
    "SILHOUETTE":    "silhouette lighting",
    "RIM":           "rim light outlining subject",
    "HAIR":          "hair light",
    "EYE_LIGHT":     "eye light catchlight",
    "NEGATIVE_FILL": "negative fill",
    "CHIAROSCURO":   "chiaroscuro high-contrast lighting",
    "THREE_POINT":   "three-point lighting",
    "HIGH_KEY":      "high-key bright lighting",
    "LOW_KEY":       "low-key dramatic lighting",
}

# ============================================================================
# Lighting Position → Seedance description
# ============================================================================

LIGHTING_POSITION_MAP: Dict[str, str] = {
    "FRONT":          "front-lit",
    "THREE_QUARTER":  "three-quarter lit",
    "SIDE":           "side-lit with strong shadows",
    "RIM":            "rim-lit from behind",
    "BACK":           "backlit",
    "TOP":            "top-lit",
    "UNDER":          "under-lit",
    "FRONTAL_45":     "lit from frontal 45 degrees",
    "SIDE_90":        "lit from 90 degrees side",
    "BACK_45":        "lit from 45 degrees behind",
}

# ============================================================================
# Color Temperature → Seedance description
# ============================================================================

COLOR_TEMP_MAP: Dict[str, str] = {
    "2000K":    "2000K candlelight warm",
    "3200K":    "3200K tungsten warm",
    "4300K":    "4300K neutral white",
    "5500K":    "5500K daylight",
    "6500K":    "6500K overcast cool",
    "8000K+":   "8000K+ deep cool blue",
    "VARIABLE": "variable color temperature",
}

# ============================================================================
# Composition Rule → Seedance description
# ============================================================================

COMPOSITION_MAP: Dict[str, str] = {
    "RULE_OF_THIRDS":     "rule of thirds composition",
    "GOLDEN_RATIO":       "golden ratio composition",
    "CENTER_COMPOSITION": "centered composition",
    "SYMMETRY":           "symmetrical composition",
    "LEADING_LINES":      "leading lines drawing the eye",
    "FRAME_WITHIN_FRAME": "frame within a frame",
    "DIAGONAL":           "diagonal composition",
    "TRIANGULAR":         "triangular composition",
    "CIRCULAR":           "circular composition",
    "NEGATIVE_SPACE":     "negative space composition",
    "RULE_OF_SPACE":      "rule of space",
    "HEADROOM":           "proper headroom",
    "LOOKROOM":           "look room for gaze direction",
    "DYNAMIC_SYMMETRY":   "dynamic symmetry",
    "GOLDEN_SPIRAL":      "golden spiral composition",
    "BALANCED":           "balanced composition",
    "ASYMMETRICAL":       "asymmetrical composition",
}

# ============================================================================
# Transition → Seedance description
# ============================================================================

TRANSITION_MAP: Dict[str, str] = {
    "CUT_TO":           "cut to",
    "FADE_TO":          "fade to",
    "FADE_TO_BLACK":    "fade to black",
    "FADE_FROM_BLACK":  "fade from black",
    "FADE_TO_WHITE":    "fade to white",
    "FADE_FROM_WHITE":  "fade from white",
    "DISSOLVE_TO":      "dissolve to",
    "SLOW_DISSOLVE_TO": "slow dissolve to",
    "SMASH_CUT_TO":     "smash cut to",
    "MATCH_CUT_TO":     "match cut to",
    "WIPE_TO":          "wipe to",
    "IRIS_TO":          "iris to",
}

# ============================================================================
# Beat Type → Seedance description
# ============================================================================

BEAT_TYPE_MAP: Dict[str, str] = {
    "OPENING":    "opening sequence",
    "INCITING":   "inciting incident",
    "REVELATION": "revelation moment",
    "CONFLICT":   "conflict escalation",
    "DECISION":   "decision point",
    "LOSS":       "moment of loss",
    "GAIN":       "moment of gain",
    "TWIST":      "plot twist",
    "CLIMAX":     "climax",
    "RESOLUTION": "resolution",
    "THE_RITUAL": "ritual sequence",
    "THE_FACE":   "character revelation",
    "AFTERMATH":  "aftermath",
}

# ============================================================================
# Aperture → Seedance description
# ============================================================================

APERTURE_MAP: Dict[str, str] = {
    "f1.2": "f/1.2 very shallow depth of field",
    "f1.4": "f/1.4 shallow depth of field",
    "f1.8": "f/1.8 shallow depth of field",
    "f2.8": "f/2.8 moderate shallow depth",
    "f4":   "f/4 moderate depth of field",
    "f5.6": "f/5.6 deep depth of field",
    "f8":   "f/8 deep focus",
    "f11":  "f/11 deep focus",
    "f16":  "f/16 very deep focus",
}


# ============================================================================
# Lookup helpers — safe getters that return the Seedance string or empty string.
# ============================================================================

def lookup(table: Dict[str, str], key: str) -> str:
    """Return the mapped value, or empty string if key is missing/falsy."""
    if not key:
        return ""
    k = key.strip()
    # Try exact match first (e.g. "35mm", "50mm")
    if k in table:
        return table[k]
    # Fall back to uppercase (e.g. "cu" -> "CU", "static" -> "STATIC")
    return table.get(k.upper(), "")


def lookup_composition(raw: str) -> str:
    """Handle compound composition rules like 'RULE_OF_THIRDS + LEADING_LINES'."""
    if not raw:
        return ""
    parts = [p.strip() for p in raw.split("+")]
    mapped = [COMPOSITION_MAP.get(p, p) for p in parts if p]
    return ", ".join(mapped) if mapped else ""


def lookup_with_fallback(table: Dict[str, str], key: str, fallback: str = "") -> str:
    """Return mapped value or the fallback (default empty string)."""
    if not key:
        return fallback
    return table.get(key.strip().upper(), fallback)
