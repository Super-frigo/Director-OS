"""Veo mapper — translates Production Intent concepts into Veo-optimized language.

Veo responds better to professional, detailed cinematography vocabulary.
Mappings are more verbose and technically precise than Seedance equivalents.
"""

# ── Camera Movement ──────────────────────────────────────────────────

VEO_CAMERA_MAP = {
    "slow_push": "a slow, deliberate dolly push — the camera glides forward with cinematic smoothness",
    "slow_pull": "a slow dolly pull — the camera drifts backward, revealing spatial context",
    "static": "locked-off static camera — absolutely still, no camera movement",
    "tracking": "smooth tracking shot — the camera moves laterally alongside the subject",
    "track_left": "tracking left — the camera glides horizontally to the left",
    "track_right": "tracking right — the camera glides horizontally to the right",
    "handheld": "intimate handheld camera — subtle organic movement with natural micro-bounces",
    "crane": "crane shot rising — the camera lifts gracefully upward, expanding the view",
    "crane_down": "crane shot descending — the camera lowers, compressing the frame",
    "slow_pan": "slow panoramic pan — the camera rotates horizontally with fluid motion",
    "pan_left": "panning left — the camera rotates to reveal the left side of the scene",
    "pan_right": "panning right — the camera rotates to reveal the right side of the scene",
    "dolly_in": "dolly in — the camera physically moves forward, intensifying focus",
    "dolly_out": "dolly out — the camera physically moves backward, widening context",
    "whip_pan": "rapid whip pan — a fast rotational camera move creating energy",
    "arc_left": "arcing left — the camera traces a semicircular path around the subject",
    "arc_right": "arcing right — the camera traces a semicircular path around the subject",
    "boom_up": "booming up — the camera rises vertically on a boom arm",
    "boom_down": "booming down — the camera descends vertically on a boom arm",
    "steadicam": "steadicam shot — smooth stabilized walking movement following the subject",
    "gimbal": "gimbal-stabilized — ultra-smooth camera movement with three-axis stabilization",
    "drone": "drone aerial perspective — soaring camera with expansive vertical movement",
    "zoom_in": "zoom in — the lens focal length increases, magnifying the subject",
    "zoom_out": "zoom out — the lens focal length decreases, widening the field of view",
    "dutch_tilt": "dutch angle tilt — the camera rolls off-axis, creating unease",
    "rack_focus": "rack focus — the focus plane shifts from foreground to background",
}

# ── Framing ──────────────────────────────────────────────────────────

VEO_FRAMING_MAP = {
    "ec": "extreme close-up frame",
    "ecu": "extreme close-up frame",
    "cu": "close-up frame",
    "mcu": "medium close-up frame — from chest up",
    "ms": "medium shot frame — from waist up",
    "mls": "medium long shot frame — full figure with environmental context",
    "ls": "wide shot — the full scene with subjects clearly placed within the environment",
    "els": "extreme wide shot — the camera captures a vast landscape, subjects are small within the frame",
    "est": "establishing shot — a wide view that establishes the location and spatial layout",
    "establishing": "establishing shot",
    "wide": "wide shot",
    "medium": "medium shot",
    "close_up": "close-up frame",
    "extreme_close_up": "extreme close-up — intimate detail filling the entire frame",
    "over_shoulder": "over-the-shoulder shot — the frame includes part of a character's shoulder in the foreground",
    "ots": "over-the-shoulder shot",
    "pov": "point-of-view shot — the camera assumes the character's perspective",
    "two_shot": "two-shot — both characters framed together in a single composition",
    "group": "group shot — multiple characters arranged within the frame",
    "insert": "insert shot — a focused detail shot of a specific object or action",
    "detail": "detail close-up — a macro-level view of fine detail",
}

# ── Lens ─────────────────────────────────────────────────────────────

VEO_LENS_MAP = {
    "14mm": "14mm ultra-wide-angle lens — expansive field of view with pronounced perspective distortion",
    "18mm": "18mm wide-angle lens — broad view with moderate distortion, dynamic spatial relationships",
    "24mm": "24mm wide-angle lens — wide perspective with natural-looking spatial expansion",
    "35mm": "35mm standard wide lens — a cinematic workhorse, slightly wider than human vision",
    "50mm": "50mm standard lens — the closest to natural human vision, neutral perspective",
    "85mm": "85mm portrait lens — flattering compression with beautiful background separation",
    "100mm": "100mm medium telephoto lens — intimate compression with narrow field of view",
    "135mm": "135mm telephoto lens — strong compression isolating the subject from background",
    "200mm": "200mm telephoto lens — extreme compression, flattening spatial depth",
    "400mm+": "400mm super-telephoto lens — extreme magnification with atmospheric haze compression",
    "anamorphic": "anamorphic widescreen lens — oval bokeh, horizontal lens flares, 2.39:1 aspect ratio",
    "fisheye": "fisheye lens — extreme wide angle with hemispherical distortion",
    "macro": "macro lens — extreme close focus capability for minute detail capture",
}

# ── Lighting ─────────────────────────────────────────────────────────

VEO_LIGHTING_MAP = {
    "natural": "natural available light — soft, organic illumination from environmental sources",
    "low_key": "low-key lighting — dramatic shadows with high contrast, predominantly dark tones",
    "high_key": "high-key lighting — bright, even illumination with minimal shadow, airy mood",
    "soft": "soft diffused lighting — gentle light wrap, minimal shadows, flattering on skin",
    "hard": "hard direct lighting — sharp shadow edges, strong contrast, sculptural quality",
    "rim": "rim lighting — a thin line of light tracing the subject's edge, separating from background",
    "back": "backlighting — the primary light source originates behind the subject, creating silhouette or glow",
    "side": "side lighting — light strikes from the side, emphasizing texture and depth through strong shadows",
    "practical": "practical in-scene lighting — visible light sources within the frame (lamps, candles, windows)",
    "motivated": "motivated lighting — the lighting appears to come from natural in-scene sources",
    "chiaroscuro": "chiaroscuro lighting — dramatic contrast between light and dark, Rembrandt-inspired",
    "neon": "neon lighting — vibrant colored light from neon tubes, creating atmospheric color casts",
    "golden_hour": "golden hour lighting — warm low-angle sunlight with long shadows and amber tones",
    "blue_hour": "blue hour lighting — cool twilight illumination with deep blue tones and soft ambient light",
    "candlelight": "candlelight — warm, flickering low-level light with orange color temperature",
}

# ── Mood ─────────────────────────────────────────────────────────────

VEO_MOOD_MAP = {
    "cold": "cold, cool-toned atmosphere — blue and cyan undertones create emotional distance",
    "warm": "warm, golden atmosphere — amber and honey tones envelop the scene",
    "mysterious": "mysterious, enigmatic atmosphere — shadows and ambiguity create intrigue",
    "tense": "palpable tension — the visual atmosphere builds psychological pressure",
    "dreamy": "dreamy, ethereal atmosphere — soft focus, gentle light, floating quality",
    "melancholic": "melancholic, somber atmosphere — subdued tones, lingering sadness in the frame",
    "romantic": "romantic, warm atmosphere — soft golden light, gentle contrasts, tender mood",
    "dark": "dark, shadowy atmosphere — low light, deep blacks, hidden details in shade",
    "bright": "bright, airy atmosphere — open light, high visibility, spacious feel",
    "noir": "film noir atmosphere — high-contrast shadows, venetian blind patterns, moral ambiguity",
    "nostalgic": "nostalgic, vintage atmosphere — warm fade, slight desaturation, memory-like quality",
    "dramatic": "dramatic, intense atmosphere — strong contrasts, emotional weight in every frame",
    "peaceful": "peaceful, serene atmosphere — calm light, balanced composition, stillness",
    "suspenseful": "suspenseful atmosphere — waiting, anticipation, the calm before revelation",
    "epic": "epic, grand atmosphere — sweeping scale, majestic lighting, monumental composition",
}

# ── Texture / Film Stock ─────────────────────────────────────────────

VEO_TEXTURE_MAP = {
    "film_grain": "organic film grain structure — subtle photochemical texture across the entire frame",
    "kodak_portra_400": "Kodak Portra 400 film stock — warm-skinned emulsion with fine grain structure, wide exposure latitude, and natural color rendering beloved by portrait photographers",
    "kodak_ektachrome": "Kodak Ektachrome — cool-toned reversal film with fine grain, punchy blues, and high contrast",
    "kodak_vision3": "Kodak Vision3 motion picture film — industry-standard cinema stock with advanced color science",
    "fuji_provia": "Fuji Provia — neutral color reversal film with ultra-fine grain, accurate reproduction",
    "fuji_velvia": "Fuji Velvia — saturated reversal film with intense primary colors and high contrast",
    "bleach_bypass": "bleach bypass process — desaturated image with retained silver, high contrast and deep blacks",
    "teal_orange": "teal-and-orange blockbuster grade — warm skin tones against complementary cool shadows",
    "vintage_film": "vintage film aesthetic — halation, gate weave, color fading, and subtle emulsion imperfections",
    "digital_clean": "clean digital sensor capture — pristine image with maximum detail and no grain",
    "anamorphic_flare": "anamorphic lens flares — horizontal blue streaks with characteristic oval bokeh",
    "chromatic_aberration": "subtle chromatic aberration — color fringing along high-contrast edges",
    "lens_breathing": "slight lens breathing — the subtle focal length shift characteristic of cinema lenses",
    "vignette": "natural vignette — gradual light falloff toward the frame edges",
}

# ── Mapper Functions ─────────────────────────────────────────────────

VEO_CAMERA_BODY_MAP = {
    "arri_alexa65": "ARRI Alexa 65 — a large-format cinema camera with 6K resolution, 14+ stops of dynamic range, and ARRI's renowned color science producing a distinctly filmic image",
    "arri_alexa_mini": "ARRI Alexa Mini — a compact cinema camera with the same color science as the full Alexa, rich highlight rolloff, and organic texture",
    "arri_alexa_35": "ARRI Alexa 35 — the latest ARRI sensor with REVEAL color science, extended dynamic range, and enhanced highlight reproduction",
    "sony_venice": "Sony Venice — a full-frame 6K cinema camera with dual base ISO, 16 stops of dynamic range, and a distinctly cinematic look with excellent highlight handling",
    "red_komodo": "RED Komodo 6K — a compact global shutter camera with 6K resolution and RED's characteristic detail-rich image",
    "red_monstro": "RED Monstro 8K — an 8K VV sensor with extreme resolution and rich color rendering",
    "panavision": "Panavision Millennium XL2 — a classic anamorphic cinema camera with Panavision's legendary optical system",
    "phantom_flex": "Phantom Flex 4K — a high-speed cinema camera capable of 1,000 frames per second",
    "sony_a7siii": "Sony a7S III — a full-frame mirrorless camera with exceptional low-light sensitivity and 4K 120p recording",
    "canon_c70": "Canon C70 — a compact RF-mount cinema camera with Canon's Dual Gain Output sensor and cinematic color",
    "bmcc_6k": "Blackmagic Pocket Cinema Camera 6K — a compact raw-recording cinema camera with filmic dynamic range and gen-5 color science",
    "iphone_pro": "iPhone Pro — computational cinematography with Dolby Vision HDR, cinematic mode rack focus, and Apple Log encoding",
}

VEO_LENS_CHARACTER_MAP = {
    "swirl_bokeh": "swirling helical bokeh — the background rotates around the focal plane, a characteristic of vintage Petzval-derived optics",
    "chromatic_aberration": "subtle chromatic aberration — delicate color fringing along high-contrast edges, a natural optical characteristic",
    "anamorphic_flare": "anamorphic lens flares — horizontal blue streaks with the signature oval defocus highlights of cinema anamorphic glass",
    "lens_breathing": "lens breathing — the subtle focal length shift during focus pulls, characteristic of cine lenses",
    "vignette": "natural vignette — smooth light falloff toward image corners, drawing attention to the center",
    "soft_wide_open": "soft image quality at wide aperture — the lens resolves gently wide open, sharpening progressively on stopping down",
    "no_sharpening": "organically resolving image — no artificial sharpening, natural optical acuity with smooth transitions",
    "transparent_optics": "transparent optical path — zero veiling glare, pristine contrast with deep blacks and clean highlights",
}

VEO_FILM_STOCK_MAP = {
    "kodak_portra_400": "Kodak Portra 400 — the iconic portrait film stock with warm skin tone rendering, subtle grain structure, and remarkable exposure latitude that handles both highlight and shadow detail with grace",
    "kodak_portra_800": "Kodak Portra 800 — a high-speed portrait film with warmer color balance, more pronounced grain, and excellent performance in low-light conditions",
    "kodak_vision3_250d": "Kodak Vision3 250D — a daylight-balanced motion picture film with natural color reproduction and fine grain, ideal for cinematic narratives",
    "kodak_vision3_500t": "Kodak Vision3 500T — a tungsten-balanced high-speed motion picture film with distinctive cinematic grain structure and warm shadow tones",
    "fuji_provia_100f": "Fuji Provia 100F — a neutral color reversal film with ultra-fine grain and accurate color reproduction prized by landscape photographers",
    "fuji_velvia_50": "Fuji Velvia 50 — a high-saturation reversal film with intense greens and reds, high contrast, and a distinctive vibrant palette",
    "ilford_hp5_plus": "Ilford HP5 Plus — a classic black-and-white film with beautiful grain structure, pushed for increased contrast and textural presence",
    "kodak_tri_x": "Kodak Tri-X 400 — the iconic black-and-white film, pushed for gritty texture, high contrast, and documentary authenticity",
    "bleach_bypass": "bleach bypass process — the silver is retained in the emulsion, creating a desaturated, high-contrast look with crushed blacks and metallic sheen",
}

VEO_COLOR_GRADE_MAP = {
    "teal_orange": "teal-and-orange complementary color grade — warm skin tones are accentuated against cool blue-teal shadows, the modern cinematic standard",
    "warm_brown_cool_teal": "warm brown foundation with cool teal-gray undertones — an organic, film-inspired grade with earthy richness and atmospheric depth",
    "cold_gray": "cold gray desaturated grade — bleak, atmospheric, minimal color temperature, emotionally distant",
    "bleach_bypass_look": "bleach bypass — desaturated, high-contrast, with retained silver creating a metallic, timeless quality",
    "vintage_technicolor": "vintage Technicolor grade — rich, saturated primaries with warm highlights and the three-strip color process look",
    "modern_blockbuster": "modern blockbuster grade — skin-safe warm tones against cool blue shadows, high dynamic range with controlled saturation",
    "monochrome": "black-and-white monochrome — luminance-graded with channel mixing for optimal tonal separation across the frame",
}


def map_camera_movement(movement: str) -> str:
    if not movement: return ""
    key = movement.strip().lower()
    mapped = VEO_CAMERA_MAP.get(key, "")
    if mapped:
        return mapped
    from director_os.compilers.translation import translate_to_english
    return translate_to_english(movement)
    mapped = VEO_CAMERA_MAP.get(key, "")
    if mapped:
        return mapped
    from director_os.compilers.translation import translate_to_english
    return translate_to_english(movement)

def map_framing(framing: str) -> str:
    if not framing: return ""
    key = framing.strip().lower()
    mapped = VEO_FRAMING_MAP.get(key, "")
    if mapped:
        return mapped
    from director_os.compilers.translation import translate_to_english
    return translate_to_english(framing)
    mapped = VEO_FRAMING_MAP.get(key, "")
    if mapped:
        return mapped
    from director_os.compilers.translation import translate_to_english
    return translate_to_english(framing)

def map_lens(lens: str) -> str:
    if not lens: return ""
    key = lens.strip().lower()
    mapped = VEO_LENS_MAP.get(key, "")
    if mapped:
        return mapped
    from director_os.compilers.translation import translate_to_english
    return translate_to_english(lens)
    mapped = VEO_LENS_MAP.get(key, "")
    if mapped:
        return mapped
    from director_os.compilers.translation import translate_to_english
    return translate_to_english(lens)

def map_lighting(lighting: str) -> str:
    if not lighting: return ""
    key = lighting.strip().lower()
    mapped = VEO_LIGHTING_MAP.get(key, "")
    if mapped:
        return mapped
    from director_os.compilers.translation import translate_to_english
    return translate_to_english(lighting)

def map_mood(mood: str) -> str:
    if not mood: return ""
    key = mood.strip().lower()
    mapped = VEO_MOOD_MAP.get(key, "")
    if mapped:
        return mapped
    from director_os.compilers.translation import translate_to_english
    return translate_to_english(mood)

def map_texture(texture: str) -> str:
    if not texture: return ""
    key = texture.strip().lower().replace(" ", "_")
    mapped = VEO_TEXTURE_MAP.get(key, "")
    if mapped:
        return mapped
    from director_os.compilers.translation import translate_to_english
    return translate_to_english(texture)

def map_camera_body(body: str) -> str:
    if not body: return ""
    key = body.strip().lower().replace(" ", "_").replace("-", "_")
    mapped = VEO_CAMERA_BODY_MAP.get(key, "")
    if mapped:
        return mapped
    from director_os.compilers.translation import translate_to_english
    return translate_to_english(body)
    mapped = VEO_CAMERA_BODY_MAP.get(key, "")
    if mapped:
        return mapped
    from director_os.compilers.translation import translate_to_english
    return translate_to_english(body)

def map_lens_character(char: str) -> str:
    if not char: return ""
    key = char.strip().lower().replace(" ", "_").replace("-", "_")
    mapped = VEO_LENS_CHARACTER_MAP.get(key, "")
    if mapped:
        return mapped
    from director_os.compilers.translation import translate_to_english
    return translate_to_english(char)
    mapped = VEO_LENS_CHARACTER_MAP.get(key, "")
    if mapped:
        return mapped
    from director_os.compilers.translation import translate_to_english
    return translate_to_english(char)

def map_film_stock(stock: str) -> str:
    if not stock: return ""
    key = stock.strip().lower().replace(" ", "_").replace("-", "_")
    mapped = VEO_FILM_STOCK_MAP.get(key, "")
    if mapped:
        return mapped
    from director_os.compilers.translation import translate_to_english
    return translate_to_english(stock)
    mapped = VEO_FILM_STOCK_MAP.get(key, "")
    if mapped:
        return mapped
    from director_os.compilers.translation import translate_to_english
    return translate_to_english(stock)

def map_color_grade(grade: str) -> str:
    if not grade: return ""
    key = grade.strip().lower().replace(" ", "_").replace("-", "_").replace("+", "_")
    for k, v in VEO_COLOR_GRADE_MAP.items():
        if key in k or k in key:
            return v
    from director_os.compilers.translation import translate_to_english
    return translate_to_english(grade)
