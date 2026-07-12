"""Seedance mapper — translates Production Intent concepts into Seedance language.

Core principle: this is translation, not creation.
The creative decisions are already made in the Project.
The mapper only converts them to Seedance-readable form.

Schema-aligned tables (SCREAMING_CASE keys) mirror the valid enum sets defined
in schemas/project_schema.py.  Every schema enum value that has a mapping here
is guaranteed to produce a non-empty Seedance description string.
"""

from typing import Dict

# ═══════════════════════════════════════════════════════════════════════════
# Schema-aligned maps — keys match schemas/project_schema.py VALID_* enums
# ═══════════════════════════════════════════════════════════════════════════

# ── Framing (14 schema keys + mapper-only aliases) ───────────────────────

SEEDANCE_FRAMING_MAP: Dict[str, str] = {
    # Schema keys (SCREAMING_CASE, primary)
    "ECU":        "extreme close-up",
    "CU":         "close-up",
    "MCU":        "medium close-up",
    "MS":         "medium shot",
    "MLS":        "medium long shot",
    "LS":         "wide shot",
    "ELS":        "extreme wide shot",
    "EST":        "establishing wide shot",
    "OTS":        "over-the-shoulder shot",
    "POV":        "point-of-view shot",
    "TWO_SHOT":   "two-shot",
    "GROUP_SHOT": "group shot",
    "INSERT":     "insert shot",
    "DETAIL":     "detail close-up",
    # Mapper-only aliases (lowercase, human-friendly)
    "ec":                 "extreme close-up",
    "ecu":                "extreme close-up",
    "establishing":       "establishing wide shot",
    "wide":               "wide shot",
    "medium":             "medium shot",
    "close_up":           "close-up shot",
    "extreme_close_up":   "extreme close-up",
    "over_shoulder":      "over-the-shoulder shot",
    "two_shot":           "two-shot",
    "group":              "group shot",
}

# ── Angle (8 schema keys + mapper-only) ──────────────────────────────────

SEEDANCE_ANGLE_MAP: Dict[str, str] = {
    # Schema keys (SCREAMING_CASE, primary)
    "EYE_LEVEL":   "eye-level",
    "HIGH_ANGLE":  "high angle looking down",
    "LOW_ANGLE":   "low angle looking up",
    "BIRDS_EYE":   "bird's-eye view from above",
    "WORMS_EYE":   "worm's-eye view from ground level",
    "DUTCH_ANGLE": "dutch angle canted frame",
    "OVERHEAD":    "overhead top-down view",
    "CANTED":      "canted dutch tilt",
    # Mapper-only aliases
    "eye_level":   "eye-level angle",
    "high_angle":  "high angle looking down",
    "low_angle":   "low angle looking up",
    "birds_eye":   "bird's-eye view from above",
    "worms_eye":   "worm's-eye view from ground level",
    "dutch_angle": "dutch angle canted frame",
    "subjective":  "subjective point-of-view",
}

# ── Camera Height (7 schema keys) ────────────────────────────────────────

SEEDANCE_HEIGHT_MAP: Dict[str, str] = {
    "GROUND":    "ground-level camera",
    "WAIST":     "waist-high camera",
    "CHEST":     "chest-high camera",
    "EYE":       "eye-level camera",
    "ABOVE_EYE": "above-eye camera",
    "HIGH":      "high camera position",
    "CEILING":   "ceiling-height camera",
}

# ── Lens (10 schema keys + mapper-only lens types) ───────────────────────

SEEDANCE_LENS_MAP: Dict[str, str] = {
    # Schema keys (primary)
    "14mm":   "14mm ultra-wide angle lens",
    "18mm":   "18mm wide-angle lens",
    "24mm":   "24mm wide-angle lens",
    "35mm":   "35mm standard wide lens",
    "50mm":   "50mm standard lens",
    "85mm":   "85mm portrait lens",
    "100mm":  "100mm medium telephoto lens",
    "135mm":  "135mm telephoto lens",
    "200mm":  "200mm telephoto lens",
    "400mm+": "400mm super telephoto lens",
    # Mapper-only lens types (not in schema VALID_LENS)
    "anamorphic": "anamorphic widescreen lens",
    "fisheye":    "fisheye lens",
    "macro":      "macro lens",
}

# ── Camera Movement (26 schema keys + mapper-only) ───────────────────────

SEEDANCE_CAMERA_MAP: Dict[str, str] = {
    # Schema keys (SCREAMING_CASE, primary)
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
    # Mapper-only aliases (lowercase)
    "slow_push":   "slow cinematic push in",
    "slow_pull":   "slow cinematic pull out",
    "static":      "static camera",
    "tracking":    "tracking shot",
    "track_left":  "camera tracks left",
    "track_right": "camera tracks right",
    "handheld":    "handheld camera",
    "crane":       "crane shot rising",
    "crane_down":  "crane shot descending",
    "slow_pan":    "slow panning shot",
    "pan_left":    "panning left",
    "pan_right":   "panning right",
    "dolly_in":    "camera dollies in",
    "dolly_out":   "camera dollies out",
    "whip_pan":    "quick whip pan",
    "arc_left":    "camera arcs around left",
    "arc_right":   "camera arcs around right",
    "boom_up":     "camera booms up",
    "boom_down":   "camera booms down",
    "steadicam":   "smooth steadicam following",
    "gimbal":      "gimbal-stabilized movement",
    "drone":       "drone aerial shot",
    "zoom_in":     "zoom in",
    "zoom_out":    "zoom out",
    "dutch_tilt":  "dutch angle tilt",
    "rack_focus":  "focus shift",
}

# ── Focus (9 schema keys) ────────────────────────────────────────────────

SEEDANCE_FOCUS_MAP: Dict[str, str] = {
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

# ── Lighting Type (15 schema keys) ───────────────────────────────────────

SEEDANCE_LIGHTING_TYPE_MAP: Dict[str, str] = {
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

# ── Lighting Position (10 schema keys) ───────────────────────────────────

SEEDANCE_LIGHTING_POSITION_MAP: Dict[str, str] = {
    "FRONT":         "front-lit",
    "THREE_QUARTER": "three-quarter lit",
    "SIDE":          "side-lit with strong shadows",
    "RIM":           "rim-lit from behind",
    "BACK":          "backlit",
    "TOP":           "top-lit",
    "UNDER":         "under-lit",
    "FRONTAL_45":    "lit from frontal 45 degrees",
    "SIDE_90":       "lit from 90 degrees side",
    "BACK_45":       "lit from 45 degrees behind",
}

# ── Color Temperature (7 schema keys) ────────────────────────────────────

SEEDANCE_COLOR_TEMP_MAP: Dict[str, str] = {
    "2000K":    "2000K candlelight warm",
    "3200K":    "3200K tungsten warm",
    "4300K":    "4300K neutral white",
    "5500K":    "5500K daylight",
    "6500K":    "6500K overcast cool",
    "8000K+":   "8000K+ deep cool blue",
    "VARIABLE": "variable color temperature",
}

# ── Composition Rule (17 schema keys) ────────────────────────────────────

SEEDANCE_COMPOSITION_MAP: Dict[str, str] = {
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

# ── Transition (12 schema keys + mapper-only) ────────────────────────────

SEEDANCE_TRANSITION_MAP: Dict[str, str] = {
    # Schema keys (SCREAMING_CASE, primary)
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
    # Mapper-only aliases (lowercase)
    "cut":              "hard cut",
    "fade_in":          "fade in",
    "fade_out":         "fade out",
    "dissolve":         "dissolve transition",
    "crossfade":        "crossfade transition",
    "wipe":             "wipe transition",
    "fade_to_black":    "fade to black",
    "fade_from_black":  "fade from black",
}

# ── Beat Type (13 schema keys) ───────────────────────────────────────────

SEEDANCE_BEAT_TYPE_MAP: Dict[str, str] = {
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

# ── Aperture (9 schema keys) ─────────────────────────────────────────────

SEEDANCE_APERTURE_MAP: Dict[str, str] = {
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

# ═══════════════════════════════════════════════════════════════════════════
# Visual-language maps — no corresponding schema enum (domain-level concepts)
# ═══════════════════════════════════════════════════════════════════════════

# ── Lighting (descriptive, no schema enum) ───────────────────────────────

SEEDANCE_LIGHTING_MAP: Dict[str, str] = {
    "natural": "natural lighting",
    "low_key": "low-key dramatic lighting",
    "high_key": "high-key bright lighting",
    "soft": "soft diffused lighting",
    "hard": "hard direct lighting",
    "rim": "rim light outlining subject",
    "back": "backlit with silhouetted edges",
    "side": "side-lit with strong shadows",
    "practical": "practical in-scene lighting",
    "motivated": "motivated naturalistic lighting",
    "chiaroscuro": "chiaroscuro high-contrast lighting",
    "neon": "neon atmospheric lighting",
    "golden_hour": "golden hour warm lighting",
    "blue_hour": "blue hour cool twilight lighting",
    "candlelight": "warm candlelight glow",
}

# ── Mood / Atmosphere ────────────────────────────────────────────────────

SEEDANCE_MOOD_MAP: Dict[str, str] = {
    "cold": "cold atmospheric mood",
    "warm": "warm atmospheric mood",
    "mysterious": "mysterious cinematic mood",
    "tense": "tense atmosphere",
    "dreamy": "dreamy ethereal mood",
    "melancholic": "melancholic somber mood",
    "romantic": "romantic warm mood",
    "dark": "dark moody atmosphere",
    "bright": "bright airy mood",
    "noir": "film noir shadowy atmosphere",
    "nostalgic": "nostalgic vintage mood",
    "dramatic": "dramatic intense mood",
    "peaceful": "peaceful serene atmosphere",
    "suspenseful": "suspenseful tense atmosphere",
    "epic": "epic grand atmosphere",
}

# ── Texture / Film Stock ─────────────────────────────────────────────────

SEEDANCE_TEXTURE_MAP: Dict[str, str] = {
    "film_grain": "film grain texture",
    "kodak_portra_400": "Kodak Portra 400 film stock emulation, warm skin tones with subtle grain",
    "kodak_ektachrome": "Kodak Ektachrome stock, cool blues with fine grain",
    "kodak_vision3": "Kodak Vision3 motion film stock, cinematic color science",
    "fuji_provia": "Fuji Provia stock, neutral accurate color with fine grain",
    "fuji_velvia": "Fuji Velvia stock, saturated colors with high contrast",
    "bleach_bypass": "bleach bypass process, desaturated with high contrast",
    "teal_orange": "teal-and-orange cinematic color grade",
    "vintage_film": "vintage film look with halation and gate weave",
    "digital_clean": "clean digital sensor look",
    "anamorphic_flare": "anamorphic lens flare artifacts",
    "chromatic_aberration": "subtle chromatic aberration on edges",
    "lens_breathing": "slight lens breathing effect",
    "vignette": "subtle vignette darkening edges",
}

# ── Camera Body ──────────────────────────────────────────────────────────

SEEDANCE_CAMERA_BODY_MAP: Dict[str, str] = {
    "arri_alexa65": "ARRI Alexa 65 large-format sensor — 6K resolution, filmic dynamic range",
    "arri_alexa_mini": "ARRI Alexa Mini — compact cinema camera, rich color science",
    "arri_alexa_35": "ARRI Alexa 35 — new sensor with REVEAL color science, extended dynamic range",
    "sony_venice": "Sony Venice — full-frame 6K, dual base ISO, cinematic look",
    "red_komodo": "RED Komodo 6K — global shutter, compact form factor",
    "red_monstro": "RED Monstro 8K — 8K VV sensor, extreme detail",
    "panavision": "Panavision Millennium XL2 — classic anamorphic cinema",
    "phantom_flex": "Phantom Flex 4K — high-speed cinema camera, 1000fps",
    "sony_a7siii": "Sony a7S III — full-frame mirrorless, excellent low-light",
    "canon_c70": "Canon C70 — RF mount cinema camera, compact form",
    "bmcc_6k": "Blackmagic Pocket Cinema Camera 6K — raw recording, filmic image",
    "iphone_pro": "iPhone Pro series — computational cinematography, Dolby Vision HDR",
}

# ── Lens Character / Optical Quality ─────────────────────────────────────

SEEDANCE_LENS_CHARACTER_MAP: Dict[str, str] = {
    "swirl_bokeh": "swirl bokeh with helical background rotation",
    "chromatic_aberration": "subtle chromatic aberration on high-contrast edges",
    "anamorphic_flare": "oval anamorphic lens flares with blue streaks",
    "lens_breathing": "slight lens breathing during focus pulls",
    "vignette": "subtle natural vignette toward frame edges",
    "soft_wide_open": "soft image wide-open, sharpens on stopping down",
    "no_sharpening": "naturally resolving without artificial sharpening, organic look",
    "transparent_optics": "transparent optical path with zero veiling glare",
    "macro_capability": "macro focusing ability for extreme close-up detail",
    "tilt_shift": "tilt-shift perspective control with selective focus plane",
    "split_diopter": "split-field diopter for simultaneous near-far focus",
    "pedestrian_cinema": "cinematic rehoused vintage still lens character",
}

# ── Film Stock (detailed) ────────────────────────────────────────────────

SEEDANCE_FILM_STOCK_MAP: Dict[str, str] = {
    "kodak_portra_400": "Kodak Portra 400 — warm skin-toned emulsion with subtle grain structure and wide latitude",
    "kodak_portra_800": "Kodak Portra 800 — increased sensitivity, warmer tones with visible grain",
    "kodak_ektachrome_e100": "Kodak Ektachrome E100 — reversal film, punchy blues, fine grain, high contrast",
    "kodak_vision3_250d": "Kodak Vision3 250D — daylight-balanced motion film, natural color reproduction",
    "kodak_vision3_500t": "Kodak Vision3 500T — tungsten-balanced, high-speed motion film, cinematic grain",
    "fuji_provia_100f": "Fuji Provia 100F — neutral accurate color reversal, ultra-fine grain",
    "fuji_velvia_50": "Fuji Velvia 50 — saturated color reversal, intense greens and reds, high contrast",
    "fuji_superia_400": "Fuji Superia 400 — consumer print film, slightly cool palette, fine grain",
    "ilford_hp5_plus": "Ilford HP5 Plus — classic B&W film, pushed for contrasty grain",
    "ilford_delta_3200": "Ilford Delta 3200 — high-speed B&W, extreme grain character",
    "kodak_tri_x": "Kodak Tri-X 400 — iconic B&W film, pushed for gritty texture",
    "bleach_bypass": "bleach bypass — desaturated, high-contrast with silver retention and deep blacks",
    "cross_processed": "cross-processing — unnatural color shifts, increased contrast and grain",
}

# ── Render Engine ────────────────────────────────────────────────────────

SEEDANCE_RENDER_ENGINE_MAP: Dict[str, str] = {
    "pbr": "physically based rendering (PBR) — realistic material response to light",
    "pbr物理渲染": "physically based rendering — realistic material response and energy-conserving shading",
    "unreal_engine_5": "Unreal Engine 5 — Nanite geometry + Lumen global illumination",
    "unity_hdrp": "Unity HDRP — high-definition render pipeline with ray tracing",
    "path_tracing": "full path tracing — unbiased global illumination with physically accurate light transport",
    "ray_tracing": "hardware-accelerated ray tracing — reflections, shadows, and ambient occlusion",
    "render_man": "RenderMan — Reyes-style rendering with subsurface scattering and deep compositing",
    "arnold": "Arnold renderer — ray-traced global illumination with physically plausible lights",
    "vray": "V-Ray — biased global illumination renderer with GPU acceleration",
    "cycles": "Cycles — path-traced GPU/CPU renderer with Principled BSDF shader",
    "octane": "OctaneRender — GPU-accelerated unbiased renderer with spectral light simulation",
    "redshift": "Redshift — biased GPU renderer with global illumination and caustics",
}

# ── Render Settings / Quality ────────────────────────────────────────────

SEEDANCE_RENDER_SETTINGS_MAP: Dict[str, str] = {
    "8k": "8K resolution output — 7680x4320, extreme fine detail",
    "6k": "6K resolution output — 6144x3456, high detail reserve",
    "4k": "4K resolution output — 3840x2160, Ultra HD",
    "global_illumination": "global illumination — indirect light bounces for natural ambient lighting",
    "全局光照": "global illumination — indirect light bounces for natural ambient lighting",
    "subsurface_scattering": "subsurface scattering (SSS) — light penetration through skin for lifelike translucency",
    "sss": "subsurface scattering (SSS) — light penetration through skin for lifelike translucency",
    "高光不溢出": "highlights carefully controlled with zero clipping — full detail retention in bright areas",
    "no_highlight_clipping": "zero highlight clipping — full specular detail retention",
    "毛孔细节": "pore-level skin detail — hyperrealistic texture down to individual pores",
    "pore_detail": "pore-level skin detail — hyperrealistic micro-texture resolution",
    "绒毛细节": "fine downy hair and fuzz rendering — realistic cloth fiber and peach-fuzz detail",
    "cloth_texture": "weave-level fabric texture — realistic thread pattern and material drape",
}

# ── Color Grade ──────────────────────────────────────────────────────────

SEEDANCE_COLOR_GRADE_MAP: Dict[str, str] = {
    "teal_orange": "teal-and-orange complementary color grade — warm skin against cool shadows",
    "teal_and_orange": "teal-and-orange complementary color grade — warm skin against cool shadows",
    "暖棕基底冷青灰调": "warm brown foundation with cool teal-gray undertones — Kodak Portra-inspired organic grade",
    "warm_brown_cool_teal": "warm brown base with cool teal-gray shadows — nostalgic cinematic grade",
    "cold_gray": "cold gray desaturated grade — bleak, atmospheric, minimal color temperature",
    "bleach_bypass_look": "bleach bypass grade — desaturated high-contrast with crushed blacks",
    "vintage_technicolor": "vintage Technicolor grade — rich primaries with warm highlights",
    "modern_blockbuster": "modern blockbuster grade — skin-safe orange-teal with deep blue shadows",
    "monochrome": "black and white monochrome — luminance-graded with channel mixing",
}

# ═══════════════════════════════════════════════════════════════════════════
# Lookup helpers
# ═══════════════════════════════════════════════════════════════════════════


def _lookup(table: Dict[str, str], key: str) -> str:
    """Return mapped value; try exact match, then uppercase, then empty string."""
    if not key:
        return ""
    k = key.strip()
    if k in table:
        return table[k]
    return table.get(k.upper(), "")


def _lookup_with_lower_fallback(table: Dict[str, str], key: str) -> str:
    """Try exact → uppercase → lowercase → passthrough."""
    if not key:
        return ""
    k = key.strip()
    if k in table:
        return table[k]
    upper = table.get(k.upper(), "")
    if upper:
        return upper
    lower = table.get(k.lower(), "")
    if lower:
        return lower
    return key


# ═══════════════════════════════════════════════════════════════════════════
# Mapper Functions — schema-aligned (SCREAMING_CASE primary, lowercase fallback)
# ═══════════════════════════════════════════════════════════════════════════


def map_framing(framing: str) -> str:
    """Translate framing to Seedance description.  Accepts schema enums or lowercase aliases."""
    return _lookup_with_lower_fallback(SEEDANCE_FRAMING_MAP, framing)


def map_angle(angle: str) -> str:
    """Translate camera angle to Seedance description."""
    return _lookup_with_lower_fallback(SEEDANCE_ANGLE_MAP, angle)


def map_height(height: str) -> str:
    """Translate camera height to Seedance description."""
    return _lookup(SEEDANCE_HEIGHT_MAP, height)


def map_lens(lens: str) -> str:
    """Translate lens to Seedance description."""
    return _lookup_with_lower_fallback(SEEDANCE_LENS_MAP, lens)


def map_camera_movement(movement: str) -> str:
    """Translate camera movement to Seedance description.  Accepts schema enums or lowercase."""
    return _lookup_with_lower_fallback(SEEDANCE_CAMERA_MAP, movement)


def map_focus(focus: str) -> str:
    """Translate focus style to Seedance description."""
    return _lookup(SEEDANCE_FOCUS_MAP, focus)


def map_lighting_type(lighting_type: str) -> str:
    """Translate lighting type (schema enum) to Seedance description."""
    return _lookup(SEEDANCE_LIGHTING_TYPE_MAP, lighting_type)


def map_lighting_position(position: str) -> str:
    """Translate lighting position (schema enum) to Seedance description."""
    return _lookup(SEEDANCE_LIGHTING_POSITION_MAP, position)


def map_color_temp(temp: str) -> str:
    """Translate color temperature to Seedance description."""
    return _lookup(SEEDANCE_COLOR_TEMP_MAP, temp)


def map_composition(rule: str) -> str:
    """Translate composition rule to Seedance description.
    Handles compound rules like 'RULE_OF_THIRDS + LEADING_LINES'.
    """
    if not rule:
        return ""
    parts = [p.strip() for p in rule.split("+")]
    from ..translation import translate_to_english
    mapped = [SEEDANCE_COMPOSITION_MAP.get(p, translate_to_english(p)) for p in parts if p]
    return ", ".join(mapped) if mapped else ""


def map_transition(transition: str) -> str:
    """Translate transition to Seedance description."""
    return _lookup_with_lower_fallback(SEEDANCE_TRANSITION_MAP, transition)


def map_beat_type(beat_type: str) -> str:
    """Translate story beat type to Seedance description."""
    return _lookup(SEEDANCE_BEAT_TYPE_MAP, beat_type)


def map_aperture(aperture: str) -> str:
    """Translate aperture to Seedance description."""
    return _lookup(SEEDANCE_APERTURE_MAP, aperture)


# ═══════════════════════════════════════════════════════════════════════════
# Visual-language mapper functions (no schema enum — domain-level concepts)
# ═══════════════════════════════════════════════════════════════════════════


def map_lighting(lighting: str) -> str:
    """Translate descriptive lighting style to Seedance description."""
    if not lighting:
        return ""
    key = lighting.strip().lower()
    mapped = SEEDANCE_LIGHTING_MAP.get(key, "")
    if mapped:
        return mapped
    from ..translation import translate_to_english
    return translate_to_english(lighting)


def map_mood(mood: str) -> str:
    """Translate production mood to Seedance description."""
    if not mood:
        return ""
    key = mood.strip().lower()
    mapped = SEEDANCE_MOOD_MAP.get(key, "")
    if mapped:
        return mapped
    from ..translation import translate_to_english
    return translate_to_english(mood)


def map_texture(texture: str) -> str:
    """Translate production texture/film stock to Seedance description."""
    if not texture:
        return ""
    key = texture.strip().lower().replace(" ", "_")
    mapped = SEEDANCE_TEXTURE_MAP.get(key, "")
    if mapped:
        return mapped
    from ..translation import translate_to_english
    return translate_to_english(texture)


def map_camera_body(body: str) -> str:
    """Translate camera body model to Seedance description."""
    if not body:
        return ""
    key = body.strip().lower().replace(" ", "_").replace("-", "_")
    mapped = SEEDANCE_CAMERA_BODY_MAP.get(key, "")
    if mapped:
        return mapped
    from ..translation import translate_to_english
    return translate_to_english(body)
    mapped = SEEDANCE_CAMERA_BODY_MAP.get(key, "")
    if mapped:
        return mapped
    from ..translation import translate_to_english
    return translate_to_english(body)


def map_lens_character(char: str) -> str:
    """Translate lens optical character to Seedance description."""
    if not char:
        return ""
    key = char.strip().lower().replace(" ", "_").replace("-", "_")
    mapped = SEEDANCE_LENS_CHARACTER_MAP.get(key, "")
    if mapped:
        return mapped
    from ..translation import translate_to_english
    return translate_to_english(char)
    mapped = SEEDANCE_LENS_CHARACTER_MAP.get(key, "")
    if mapped:
        return mapped
    from ..translation import translate_to_english
    return translate_to_english(char)


def map_film_stock(stock: str) -> str:
    """Translate film stock name to detailed Seedance description."""
    if not stock:
        return ""
    key = stock.strip().lower().replace(" ", "_").replace("-", "_").replace("/", "_")
    mapped = SEEDANCE_FILM_STOCK_MAP.get(key, "")
    if mapped:
        return mapped
    from ..translation import translate_to_english
    return translate_to_english(stock)
    mapped = SEEDANCE_FILM_STOCK_MAP.get(key, "")
    if mapped:
        return mapped
    from ..translation import translate_to_english
    return translate_to_english(stock)


def map_render_engine(engine: str) -> str:
    """Translate render engine to Seedance description."""
    if not engine:
        return ""
    key = engine.strip().lower().replace(" ", "_").replace("-", "_")
    mapped = SEEDANCE_RENDER_ENGINE_MAP.get(key, "")
    if mapped:
        return mapped
    from ..translation import translate_to_english
    return translate_to_english(engine)
    mapped = SEEDANCE_RENDER_ENGINE_MAP.get(key, "")
    if mapped:
        return mapped
    from ..translation import translate_to_english
    return translate_to_english(engine)


def map_render_setting(setting: str) -> str:
    """Translate a single render setting to Seedance description."""
    if not setting:
        return ""
    key = setting.strip().lower().replace(" ", "_").replace("-", "_")
    for k, v in SEEDANCE_RENDER_SETTINGS_MAP.items():
        if key in k or k in key:
            return v
    from ..translation import translate_to_english
    return translate_to_english(setting)


def map_render_settings(settings_str: str) -> str:
    """Translate combined render settings string."""
    if not settings_str:
        return ""
    parts = []
    for chunk in settings_str.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        mapped = map_render_setting(chunk)
        parts.append(mapped)
    return ", ".join(parts)


def map_color_grade(grade: str) -> str:
    """Translate color grade description."""
    if not grade:
        return ""
    key = grade.strip().lower().replace(" ", "_").replace("-", "_").replace("+", "_")
    for k, v in SEEDANCE_COLOR_GRADE_MAP.items():
        if key in k or k in key:
            return v
    from ..translation import translate_to_english
    return translate_to_english(grade)
