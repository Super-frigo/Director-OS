"""L2: 空间建构 — Spatial Construction.

Extracts: scene descriptions, directional words ("门外", "案前")
Outputs:  floor plan + depth layers + visual anchors
"""

from .base import BaseLayer


# Spatial keywords
DEPTH_KEYWORDS = {
    "前景": "foreground",
    "中景": "midground",
    "背景": "background",
    "远景": "far_background",
    "景深": "depth_of_field",
}

DIRECTION_KEYWORDS = {
    "门外": "outside_door",
    "窗前": "by_window",
    "案前": "before_desk",
    "桌前": "before_table",
    "楼梯": "staircase",
    "楼上": "upstairs",
    "楼下": "downstairs",
    "左侧": "frame_left",
    "右侧": "frame_right",
    "中央": "center",
    "中间": "center",
    "角落": "corner",
    "深处": "deep_background",
    "入口": "entrance",
    "出口": "exit",
    "边缘": "edge_of_frame",
    "前方": "in_front",
    "后方": "behind",
}

ENVIRONMENT_TYPES = {
    "室内": "indoor",
    "内景": "indoor",
    "室外": "outdoor",
    "外景": "outdoor",
    "街道": "street",
    "房间": "room",
    "大厅": "hall",
    "宫殿": "palace",
    "森林": "forest",
    "海边": "seaside",
    "城市": "cityscape",
    "乡村": "rural",
    "废墟": "ruins",
}


class SpatialLayer(BaseLayer):
    """L2: Build spatial understanding from world and scene data."""

    def analyze(self, context: dict) -> dict:
        project = context.get("project")
        shots = context.get("shots", [])
        world = getattr(project, "world", None) if project else None
        intent = context.get("intent", {})

        # Collect spatial text
        search_text = ""
        if world:
            if hasattr(world, "location"):
                search_text += " " + (world.location or "")
            if hasattr(world, "architecture"):
                search_text += " " + (world.architecture or "")

        vis_lang = getattr(project, "visual_language", None) if project else None
        if vis_lang and vis_lang.atmosphere:
            search_text += " " + vis_lang.atmosphere

        # Detect environment type
        env_types = []
        for keyword, anchor in ENVIRONMENT_TYPES.items():
            if keyword in search_text:
                if anchor not in env_types:
                    env_types.append(anchor)

        # Detect depth cues from shots
        depth_layers = set()
        directional_anchors = []
        for shot in shots:
            comp = shot.get("composition", {})
            if isinstance(comp, dict):
                d = comp.get("depth", 0)
                if d:
                    depth_layers.add(str(d))
                fg = comp.get("foreground", "")
                mg = comp.get("midground", "")
                bg = comp.get("background", "")
                if fg:
                    depth_layers.add("foreground")
                if mg:
                    depth_layers.add("midground")
                if bg:
                    depth_layers.add("background")

            # Shot action text for directional keywords
            action = shot.get("action", "")
            for keyword, anchor in DIRECTION_KEYWORDS.items():
                if keyword in action:
                    directional_anchors.append(anchor)

        # Detect directional keywords
        for keyword, anchor in DIRECTION_KEYWORDS.items():
            if keyword in search_text:
                directional_anchors.append(anchor)

        return {
            "environment_type": env_types[0] if env_types else "",
            "environment_candidates": env_types,
            "depth_layers": sorted(depth_layers) if depth_layers else ["foreground", "midground", "background"],
            "directional_anchors": list(set(directional_anchors)),
            "location_description": world.location if world and hasattr(world, "location") else "",
            "architecture": world.architecture if world and hasattr(world, "architecture") else "",
            "atmosphere": vis_lang.atmosphere if vis_lang else "",
        }
