"""L6: 微观质感 — Micro Texture.

Extracts: detail descriptions ("握着信", "面容阴沉")
Outputs:  optical parameters + skin texture + eye details
"""

from .base import BaseLayer


# Texture keywords → optical/detail descriptors
TEXTURE_KEYWORDS = {
    "毛孔": "pore-level skin detail — hyperrealistic micro-texture",
    "绒毛": "fine vellus hair visible on skin surface — natural fuzz detail",
    "肌肤": "subsurface scattering skin — realistic translucency",
    "皮肤": "realistic skin texture with natural oil and pore variation",
    "布料": "weave-level fabric texture — thread and fiber detail",
    "丝绸": "silk fabric sheen with anisotropic highlight reflection",
    "金属": "metallic surface with accurate specular and anisotropic reflection",
    "木纹": "wood grain texture with natural pore and ring detail",
    "皮革": "leather grain texture with subtle surface wear",
    "玻璃": "glass surface with accurate refraction, reflection, and thin-film interference",
    "水面": "water surface with caustic light patterns and ripples",
    "头发": "individual hair strand detail with specular sheen",
    "眼神": "catchlight in eyes — alive, reflective gaze with micro-saccades",
    "嘴唇": "lip detail with natural moisture and subtle color variation",
    "泪水": "tear film with meniscus refraction and surface tension",
    "血迹": "blood with wet-surface specular and viscosity behavior",
    "伤痕": "scar tissue with altered surface texture and color",
    "皱纹": "wrinkle and fine-line detail with subsurface occlusion",
    "污渍": "surface staining with absorption and edge feathering",
    "锈迹": "rust with crystalline surface growth and color variation",
}

OPTICAL_KEYWORDS = {
    "散景": "bokeh — out-of-focus point light rendering with lens-specific character",
    "旋焦": "swirl bokeh — helical background rotation characteristic of vintage lenses",
    "色差": "chromatic aberration — color fringing on high-contrast edges",
    "紫边": "purple fringing — lateral chromatic aberration",
    "眩光": "lens flare — veiling glare and ghosting from bright light sources",
    "耀斑": "lens flare artifact — colored polygonal or oval reflections",
    "锐化": "image sharpening — edge contrast enhancement",
    "过度锐化": "oversharpening — unnatural edge halos",
    "暗角": "vignette — light falloff toward image edges",
    "畸变": "distortion — barrel or pincushion geometric warp",
    "呼吸效应": "lens breathing — focal length shift during focusing",
    "景深": "depth of field — focus plane transition with defocus gradation",
}


class MicroTextureLayer(BaseLayer):
    """L6: Extract micro-level texture and optical details."""

    def analyze(self, context: dict) -> dict:
        project = context.get("project")
        intent = context.get("intent", {})
        shots = context.get("shots", [])

        vis = intent.get("visual_direction", {})
        vl = getattr(project, "visual_language", None) if project else None

        # Collect all descriptive text
        search_text = ""
        if vl:
            if vl.texture:
                search_text += " " + vl.texture
            if vl.render_settings:
                search_text += " " + vl.render_settings
            if vl.lighting:
                search_text += " " + vl.lighting

        for key in ("texture", "atmosphere", "lighting", "render_settings"):
            val = vis.get(key, "")
            if isinstance(val, str):
                search_text += " " + val

        # Also from constraints
        constraints = intent.get("constraints", {})
        for avoid_list in constraints.get("avoid", []):
            if isinstance(avoid_list, str):
                search_text += " " + avoid_list
        for req_list in constraints.get("must", []):
            if isinstance(req_list, str):
                search_text += " " + req_list

        # Detect texture features
        detected_textures = {}
        for keyword, description in TEXTURE_KEYWORDS.items():
            if keyword in search_text:
                detected_textures[keyword] = description

        # Detect optical features
        detected_optical = {}
        for keyword, description in OPTICAL_KEYWORDS.items():
            if keyword in search_text:
                detected_optical[keyword] = description

        # Parse render settings for structured quality spec
        render_settings = vl.render_settings if vl else ""
        if not render_settings:
            render_settings = vis.get("render_settings", "")

        quality_specs = []
        if render_settings:
            for part in render_settings.replace("，", ",").split(","):
                part = part.strip()
                if part:
                    quality_specs.append(part)

        return {
            "texture_features": detected_textures,
            "optical_features": detected_optical,
            "quality_specifications": quality_specs,
            "texture_description": vl.texture if vl else vis.get("texture", ""),
            "render_settings": render_settings,
            "has_pore_detail": "毛孔" in search_text,
            "has_clothing_texture": any(t in search_text for t in ("布料", "丝绸", "衣物")),
            "has_skin_detail": any(t in search_text for t in ("毛孔", "肌肤", "皮肤", "绒毛")),
        }
