"""L3: 光影系统 — Lighting System.

Extracts: light source words ("烛火", "月光"), mood words ("阴沉")
Outputs:  light topology (key/fill/rim/ambient) + color temperature scheme
"""

from .base import BaseLayer


LIGHT_SOURCE_KEYWORDS = {
    "日光": {"type": "key", "position": "natural", "temp": "5500K"},
    "月光": {"type": "key", "position": "natural", "temp": "6500K"},
    "烛火": {"type": "practical", "position": "low", "temp": "2000K"},
    "蜡烛": {"type": "practical", "position": "low", "temp": "2000K"},
    "台灯": {"type": "practical", "position": "desk_level", "temp": "3200K"},
    "吊灯": {"type": "practical", "position": "overhead", "temp": "3200K"},
    "窗户": {"type": "motivated", "position": "side", "temp": "5500K"},
    "天光": {"type": "ambient", "position": "overhead", "temp": "6500K"},
    "篝火": {"type": "practical", "position": "low", "temp": "2000K"},
    "火把": {"type": "practical", "position": "hand_level", "temp": "2000K"},
    "霓虹": {"type": "practical", "position": "wall", "temp": "variable"},
    "路灯": {"type": "practical", "position": "overhead", "temp": "3200K"},
    "车灯": {"type": "practical", "position": "ground", "temp": "4300K"},
    "闪电": {"type": "effect", "position": "overhead", "temp": "8000K"},
    "投影": {"type": "effect", "position": "side", "temp": "variable"},
}

MOOD_LIGHTING_MAP = {
    "阴沉": {"mood": "oppressive", "contrast": "high", "key": "hard"},
    "压抑": {"mood": "oppressive", "contrast": "high", "key": "hard"},
    "明亮": {"mood": "cheerful", "contrast": "low", "key": "soft"},
    "温暖": {"mood": "warm", "contrast": "low", "key": "soft"},
    "柔和": {"mood": "soft", "contrast": "low", "key": "diffused"},
    "阴森": {"mood": "creepy", "contrast": "extreme", "key": "hard"},
    "浪漫": {"mood": "romantic", "contrast": "low", "key": "soft_warm"},
    "梦幻": {"mood": "dreamy", "contrast": "low", "key": "diffused"},
    "紧张": {"mood": "tense", "contrast": "high", "key": "hard"},
    "神秘": {"mood": "mysterious", "contrast": "high", "key": "hard"},
    "黑暗": {"mood": "dark", "contrast": "extreme", "key": "hard"},
}


class LightingLayer(BaseLayer):
    """L3: Extract lighting topology from project data."""

    def analyze(self, context: dict) -> dict:
        project = context.get("project")
        shots = context.get("shots", [])
        intent = context.get("intent", {})

        vis = intent.get("visual_direction", {})
        vl = getattr(project, "visual_language", None) if project else None

        search_text = ""
        if vl:
            if vl.lighting:
                search_text += " " + vl.lighting
            if vl.atmosphere:
                search_text += " " + vl.atmosphere
            if vl.render_settings:
                search_text += " " + vl.render_settings

        # Detect light sources mentioned in project
        detected_sources = []
        for keyword, config in LIGHT_SOURCE_KEYWORDS.items():
            if keyword in search_text:
                detected_sources.append({**config, "keyword": keyword})

        # Also check shot data
        for shot in shots:
            lighting = shot.get("lighting", "")
            if isinstance(lighting, str) and lighting:
                for keyword, config in LIGHT_SOURCE_KEYWORDS.items():
                    if keyword in lighting:
                        detected_sources.append({**config, "keyword": keyword})

        # Lighting key from visual_direction
        lighting_text = vis.get("lighting", "") or search_text

        # Detect mood
        mood_config = {}
        for keyword, config in MOOD_LIGHTING_MAP.items():
            if keyword in search_text or keyword in lighting_text:
                mood_config = config
                break

        # Color temperature
        temp_scheme = ""
        if detected_sources:
            temps = [s["temp"] for s in detected_sources if s.get("temp")]
            if temps:
                temp_scheme = " + ".join(list(set(temps)))

        # Build light topology
        light_topology = {}
        if detected_sources:
            for i, src in enumerate(detected_sources[:4]):
                role = "key" if i == 0 else ("fill" if i == 1 else "rim" if i == 2 else "ambient")
                light_topology[role] = {
                    "type": src.get("type", ""),
                    "position": src.get("position", ""),
                    "temp": src.get("temp", ""),
                    "description": src.get("keyword", ""),
                }
        else:
            # Fallback from visual_direction
            lighting_desc = vis.get("lighting", "")
            if lighting_desc:
                light_topology["key"] = {"type": "described", "description": lighting_desc}

        return {
            "light_topology": light_topology,
            "color_temperature_scheme": temp_scheme,
            "lighting_mood": mood_config.get("mood", ""),
            "contrast": mood_config.get("contrast", ""),
            "key_light_quality": mood_config.get("key", ""),
            "sources_detected": [s["keyword"] for s in detected_sources],
            "lighting_description": lighting_text,
        }
