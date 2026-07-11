"""Veo PromptBuilder — generates longer, cinematically-rich prompts.

Veo responds better to detailed, professional descriptions.
Unlike Seedance, longer prompts improve output quality.
"""

from .mapper import (
    map_camera_movement, map_framing, map_lens, map_lighting,
    map_mood, map_texture, map_camera_body, map_lens_character,
    map_film_stock, map_color_grade,
)


class VeoPromptBuilder:
    """Assembles verbose, cinematic prompts optimized for Veo."""

    def build(self, intent: dict, layers: dict = None) -> str:
        vis = intent.get("visual_direction", {})
        cam = intent.get("camera_strategy", {})
        chars = intent.get("character_direction", [])
        narrative = intent.get("narrative_intent", {})

        paragraphs = []

        # ── Visual paragraph ───────────────────────────────────────
        visual_parts = []

        framing_raw = cam.get("framing", "")
        framing = map_framing(framing_raw) if framing_raw else ""
        char_name = self._get_char_name(chars, 0)
        char_action = self._get_char_action(chars, 0)

        if framing and char_name:
            visual_parts.append(f"{framing} of {char_name}")
            if char_action:
                visual_parts.append(f"who {char_action}")
        elif framing:
            visual_parts.append(f"{framing}")

        movement_raw = cam.get("movement", "")
        if movement_raw:
            movement = map_camera_movement(movement_raw)
            if movement:
                visual_parts.append(f"The camera performs {movement}")

        lens_raw = cam.get("lens_character", "")
        if lens_raw:
            lens_desc = map_lens(lens_raw)
            if lens_desc:
                visual_parts.append(f"Shot with a {lens_desc}")

        angle_raw = cam.get("perspective", "")
        if angle_raw:
            angle_map = {"eye_level": "at eye level", "low_angle": "from a low angle looking up",
                         "high_angle": "from above looking down", "dutch_angle": "with a canted dutch angle"}
            visual_parts.append(f"The camera is positioned {angle_map.get(angle_raw.lower(), angle_raw)}")

        if visual_parts:
            paragraphs.append(". ".join(visual_parts) + ".")

        # ── Lighting & color paragraph ─────────────────────────────
        light_parts = []

        lighting_raw = vis.get("lighting", "")
        if lighting_raw:
            light = map_lighting(lighting_raw)
            if light:
                light_parts.append(f"The scene is lit with {light}")

        mood_raw = vis.get("mood", [])
        if isinstance(mood_raw, list) and mood_raw:
            moods = [map_mood(m) for m in mood_raw if m]
            if moods:
                light_parts.append(f"The atmosphere is {', '.join(moods)}")

        film_stock = vis.get("film_stock", "")
        if film_stock:
            film_desc = map_film_stock(film_stock)
            if film_desc:
                light_parts.append(f"The image emulates {film_desc}")

        color_grade = vis.get("color_grade", "")
        if color_grade:
            grade = map_color_grade(color_grade)
            if grade:
                light_parts.append(f"The color grade is a {grade}")
        else:
            color_raw = vis.get("color", "")
            if color_raw:
                light_parts.append(f"The color palette is {color_raw}")

        texture_raw = vis.get("texture", "")
        if texture_raw:
            tex = map_texture(texture_raw)
            if tex:
                light_parts.append(f"Texturally, {tex}")

        atmos = vis.get("atmosphere", "")
        if atmos:
            light_parts.append(f"The overall atmosphere is {atmos}")

        if light_parts:
            paragraphs.append(" ".join(light_parts) + ".")

        # ── Equipment paragraph ────────────────────────────────────
        equip_parts = []
        camera_body = vis.get("camera_body", "")
        if camera_body:
            body_desc = map_camera_body(camera_body)
            if body_desc:
                equip_parts.append(f"Filmed on {body_desc}")

        lens_char = vis.get("lens_character", "")
        if lens_char:
            char_desc = map_lens_character(lens_char)
            if char_desc:
                equip_parts.append(f"with {char_desc}")

        render_engine = vis.get("render_engine", "")
        if render_engine:
            from .mapper import VEO_CAMERA_BODY_MAP
            key = render_engine.strip().lower().replace(" ", "_").replace("-", "_")
            if key in ("pbr", "pbr物理渲染"):
                equip_parts.append("The rendering uses physically-based shading for realistic material response")
            else:
                equip_parts.append(f"The rendering engine is {render_engine}")

        render_settings = vis.get("render_settings", "")
        if render_settings:
            equip_parts.append(f"Render features include: {render_settings}")

        if equip_parts:
            paragraphs.append(" ".join(equip_parts) + ".")

        # ── Narrative paragraph ────────────────────────────────────
        premise = narrative.get("premise", "")
        if premise:
            paragraphs.append(f"The scene: {premise}.")

        # ── Layer enrichment ───────────────────────────────────────
        if layers:
            l1 = layers.get("l1_baseline", {})
            l4 = layers.get("l4_camera", {})
            l6 = layers.get("l6_microtexture", {})

            enrich = []
            style_anchor = l1.get("style_anchor", "")
            res = l1.get("resolution", "")
            if style_anchor and res:
                enrich.append(f"Visual style: {style_anchor}. Output resolution: {res}.")
            sb = l4.get("storyboard_summary", "")
            if sb:
                enrich.append(f"Shot sequence: {sb}.")
            specs = l6.get("quality_specifications", [])
            if specs:
                enrich.append(f"Quality specifications: {'; '.join(specs[:4])}.")

            if enrich:
                paragraphs.extend(enrich)

        return "\n\n".join(paragraphs)

    def build_shot_prompt(self, shot: dict, layers: dict = None) -> str:
        parts = []
        framing_raw = shot.get("framing", "")
        framing = map_framing(framing_raw) if framing_raw else ""
        movement_raw = shot.get("movement", "")
        movement = map_camera_movement(movement_raw) if movement_raw else ""
        action = shot.get("action", "")

        if framing and action:
            parts.append(f"{framing} of {action}")
        elif framing:
            parts.append(f"{framing}")
        if movement:
            parts.append(f"camera {movement}")
        lens_raw = shot.get("lens", "")
        if lens_raw:
            lens_desc = map_lens(lens_raw)
            if lens_desc:
                parts.append(f"shot on {lens_desc}")
        return ". ".join(parts) if parts else ""

    @staticmethod
    def _get_char_name(chars: list, idx: int = 0) -> str:
        if idx < len(chars):
            return chars[idx].get("name", "") or chars[idx].get("id", "")
        return ""

    @staticmethod
    def _get_char_action(chars: list, idx: int = 0) -> str:
        if idx < len(chars):
            return chars[idx].get("action", "")
        return ""
