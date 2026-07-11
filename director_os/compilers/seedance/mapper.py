"""Seedance mapper — translates Production Intent concepts into Seedance language.

Core principle: this is translation, not creation.
The creative decisions are already made in the Project.
The mapper only converts them to Seedance-readable form.
"""

# ── Camera ──────────────────────────────────────────────────────────────

SEEDANCE_CAMERA_MAP = {
    "slow_push": "slow cinematic push in",
    "slow_pull": "slow cinematic pull out",
    "static": "static camera",
    "tracking": "tracking shot",
    "track_left": "camera tracks left",
    "track_right": "camera tracks right",
    "handheld": "handheld camera",
    "crane": "crane shot rising",
    "crane_down": "crane shot descending",
    "slow_pan": "slow panning shot",
    "pan_left": "panning left",
    "pan_right": "panning right",
    "dolly_in": "camera dollies in",
    "dolly_out": "camera dollies out",
    "whip_pan": "quick whip pan",
    "arc_left": "camera arcs around left",
    "arc_right": "camera arcs around right",
    "boom_up": "camera booms up",
    "boom_down": "camera booms down",
    "steadicam": "smooth steadicam following",
    "gimbal": "gimbal-stabilized movement",
    "drone": "drone aerial shot",
    "zoom_in": "zoom in",
    "zoom_out": "zoom out",
    "dutch_tilt": "dutch angle tilt",
    "rack_focus": "focus shift",
}

# ── Framing ─────────────────────────────────────────────────────────────

SEEDANCE_FRAMING_MAP = {
    "ec": "extreme close-up",
    "ecu": "extreme close-up",
    "cu": "close-up",
    "mcu": "medium close-up",
    "ms": "medium shot",
    "mls": "medium long shot",
    "ls": "wide shot",
    "els": "extreme wide shot",
    "est": "establishing wide shot",
    "establishing": "establishing wide shot",
    "wide": "wide shot",
    "medium": "medium shot",
    "close_up": "close-up shot",
    "extreme_close_up": "extreme close-up",
    "over_shoulder": "over-the-shoulder shot",
    "ots": "over-the-shoulder shot",
    "pov": "point-of-view shot",
    "two_shot": "two-shot",
    "group": "group shot",
    "insert": "insert shot",
    "detail": "detail close-up",
}

# ── Lens / Focal Length ────────────────────────────────────────────────

SEEDANCE_LENS_MAP = {
    "14mm": "14mm ultra-wide angle lens",
    "18mm": "18mm wide-angle lens",
    "24mm": "24mm wide-angle lens",
    "35mm": "35mm standard wide lens",
    "50mm": "50mm standard lens",
    "85mm": "85mm portrait lens",
    "100mm": "100mm medium telephoto lens",
    "135mm": "135mm telephoto lens",
    "200mm": "200mm telephoto lens",
    "400mm+": "400mm super telephoto lens",
    "anamorphic": "anamorphic widescreen lens",
    "fisheye": "fisheye lens",
    "macro": "macro lens",
}

# ── Angle ───────────────────────────────────────────────────────────────

SEEDANCE_ANGLE_MAP = {
    "eye_level": "eye-level angle",
    "high_angle": "high angle looking down",
    "low_angle": "low angle looking up",
    "birds_eye": "bird's-eye view from above",
    "worms_eye": "worm's-eye view from ground level",
    "dutch_angle": "dutch angle canted frame",
    "overhead": "overhead top-down view",
    "subjective": "subjective point-of-view",
}

# ── Lighting ────────────────────────────────────────────────────────────

SEEDANCE_LIGHTING_MAP = {
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

# ── Mood / Atmosphere ──────────────────────────────────────────────────

SEEDANCE_MOOD_MAP = {
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

# ── Transition ──────────────────────────────────────────────────────────

SEEDANCE_TRANSITION_MAP = {
    "cut": "hard cut",
    "fade_in": "fade in",
    "fade_out": "fade out",
    "dissolve": "dissolve transition",
    "crossfade": "crossfade transition",
    "wipe": "wipe transition",
    "fade_to_black": "fade to black",
    "fade_from_black": "fade from black",
}

# ── Texture / Film Stock ───────────────────────────────────────────────

SEEDANCE_TEXTURE_MAP = {
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

# ── Mapper Functions ───────────────────────────────────────────────────


def map_camera_movement(movement: str) -> str:
    """Translate production camera movement to Seedance description."""
    if not movement:
        return ""
    key = movement.strip().lower()
    return SEEDANCE_CAMERA_MAP.get(key, movement)


def map_framing(framing: str) -> str:
    """Translate production framing to Seedance description."""
    if not framing:
        return ""
    key = framing.strip().lower()
    return SEEDANCE_FRAMING_MAP.get(key, framing)


def map_lens(lens: str) -> str:
    """Translate production lens to Seedance description."""
    if not lens:
        return ""
    key = lens.strip().lower()
    return SEEDANCE_LENS_MAP.get(key, lens)


def map_angle(angle: str) -> str:
    """Translate production angle to Seedance description."""
    if not angle:
        return ""
    key = angle.strip().lower()
    return SEEDANCE_ANGLE_MAP.get(key, angle)


def map_lighting(lighting: str) -> str:
    """Translate production lighting style to Seedance description."""
    if not lighting:
        return ""
    key = lighting.strip().lower()
    return SEEDANCE_LIGHTING_MAP.get(key, lighting)


def map_mood(mood: str) -> str:
    """Translate production mood to Seedance description."""
    if not mood:
        return ""
    key = mood.strip().lower()
    return SEEDANCE_MOOD_MAP.get(key, mood)


def map_texture(texture: str) -> str:
    """Translate production texture/film stock to Seedance description."""
    if not texture:
        return ""
    key = texture.strip().lower().replace(" ", "_")
    return SEEDANCE_TEXTURE_MAP.get(key, texture)


def map_transition(transition: str) -> str:
    """Translate production transition to Seedance description."""
    if not transition:
        return ""
    key = transition.strip().lower()
    return SEEDANCE_TRANSITION_MAP.get(key, transition)

# ── Camera Body ──────────────────────────────────────────────────────

SEEDANCE_CAMERA_BODY_MAP = {
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

# ── Lens Character / Optical Quality ─────────────────────────────────

SEEDANCE_LENS_CHARACTER_MAP = {
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

# ── Film Stock (detailed) ────────────────────────────────────────────

SEEDANCE_FILM_STOCK_MAP = {
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

# ── Render Engine ────────────────────────────────────────────────────

SEEDANCE_RENDER_ENGINE_MAP = {
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

# ── Render Settings / Quality ────────────────────────────────────────

SEEDANCE_RENDER_SETTINGS_MAP = {
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

# ── Color Grade ──────────────────────────────────────────────────────

SEEDANCE_COLOR_GRADE_MAP = {
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

# ── Mapper Functions (new) ──────────────────────────────────────────────


def map_camera_body(body: str) -> str:
    """Translate camera body model to Seedance description."""
    if not body:
        return ""
    key = body.strip().lower().replace(" ", "_").replace("-", "_")
    return SEEDANCE_CAMERA_BODY_MAP.get(key, body)


def map_lens_character(char: str) -> str:
    """Translate lens optical character to Seedance description."""
    if not char:
        return ""
    key = char.strip().lower().replace(" ", "_").replace("-", "_")
    return SEEDANCE_LENS_CHARACTER_MAP.get(key, char)


def map_film_stock(stock: str) -> str:
    """Translate film stock name to detailed Seedance description."""
    if not stock:
        return ""
    key = stock.strip().lower().replace(" ", "_").replace("-", "_").replace("/", "_")
    return SEEDANCE_FILM_STOCK_MAP.get(key, stock)


def map_render_engine(engine: str) -> str:
    """Translate render engine to Seedance description."""
    if not engine:
        return ""
    key = engine.strip().lower().replace(" ", "_").replace("-", "_")
    return SEEDANCE_RENDER_ENGINE_MAP.get(key, engine)


def map_render_setting(setting: str) -> str:
    """Translate a single render setting to Seedance description."""
    if not setting:
        return ""
    key = setting.strip().lower().replace(" ", "_").replace("-", "_")
    # Also try the Chinese key directly
    for k, v in SEEDANCE_RENDER_SETTINGS_MAP.items():
        if key in k or k in key:
            return v
    return setting


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
    return grade


