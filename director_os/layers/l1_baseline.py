"""L1: 基底定调 — Baseline Tuning.

Extracts: era keywords, style hints ("烛火" → costume drama)
Outputs:  resolution + style positioning + era anchor
"""

from .base import BaseLayer


# ── era keyword lookup (Chinese → English anchor) ─────────────────────

ERA_KEYWORDS = {
    "古代": "ancient",
    "古装": "ancient_costume",
    "唐朝": "tang_dynasty",
    "宋代": "song_dynasty",
    "民国": "republican_era",
    "1930": "republican_era",
    "民初": "republican_era",
    "现代": "modern",
    "当代": "contemporary",
    "未来": "futuristic",
    "赛博朋克": "cyberpunk",
    "蒸汽波": "vaporwave",
    "复古": "retro",
    "中世纪": "medieval",
    "奇幻": "fantasy",
    "科幻": "sci_fi",
    "宫廷": "imperial_court",
    "军阀": "warlord_era",
}

STYLE_KEYWORDS = {
    "写实": "realistic",
    "超写实": "hyper_realistic",
    "胶片": "film_stock",
    "复古": "retro",
    "动漫": "anime",
    "二次元": "anime",
    "水墨": "ink_wash",
    "油画": "oil_painting",
    "赛博朋克": "cyberpunk",
    "废土": "wasteland",
    "暗黑": "dark_fantasy",
    "梦幻": "dreamy",
    "童话": "fairy_tale",
    "极简": "minimalist",
    "奢华": "luxury",
    "纪实": "documentary",
    "黑白": "monochrome",
    "漫画": "comic",
}


class BaselineLayer(BaseLayer):
    """L1: Extract era, style baseline from project metadata and creative section."""

    def analyze(self, context: dict) -> dict:
        project = context.get("project")
        intent = context.get("intent", {})
        creative = {}
        world = {}
        output = {}

        if hasattr(project, "story"):
            pass
        if hasattr(project, "metadata"):
            desc = project.metadata.description or ""
        else:
            desc = ""

        # Collect text to search for keywords
        search_text = desc
        if hasattr(project, "story") and project.story:
            search_text += " " + project.story.premise
            if isinstance(project.story.genre, list):
                search_text += " " + " ".join(project.story.genre)
            if isinstance(project.story.theme, list):
                search_text += " " + " ".join(project.story.theme)

        creative = intent.get("creative_goal", {})
        vl = getattr(project, "visual_language", None)

        # Detect era
        detected_eras = []
        for keyword, anchor in ERA_KEYWORDS.items():
            if keyword in search_text:
                detected_eras.append(anchor)
        if not detected_eras and vl and vl.style:
            for keyword, anchor in ERA_KEYWORDS.items():
                if keyword in vl.style:
                    detected_eras.append(anchor)

        # Detect style
        detected_styles = []
        if vl and vl.style:
            detected_styles.append(vl.style)
        for keyword, anchor in STYLE_KEYWORDS.items():
            if keyword in search_text:
                if anchor not in detected_styles:
                    detected_styles.append(anchor)

        # Resolution from output profile
        resolution = ""
        output_raw = None
        if hasattr(project, "output"):
            output_raw = project.output
        if isinstance(output_raw, dict):
            resolution = output_raw.get("resolution", "")
        if not resolution and vl and vl.render_settings:
            if "8K" in vl.render_settings or "8k" in vl.render_settings:
                resolution = "8K"
            elif "4K" in vl.render_settings or "4k" in vl.render_settings:
                resolution = "4K"

        # Era anchor (most confident)
        era_anchor = detected_eras[0] if detected_eras else ""

        return {
            "era_anchor": era_anchor,
            "era_candidates": detected_eras,
            "style_anchor": detected_styles[0] if detected_styles else "",
            "style_candidates": detected_styles,
            "resolution": resolution or "HD",
            "creative_goal": creative.get("primary", ""),
            "description": desc,
        }
