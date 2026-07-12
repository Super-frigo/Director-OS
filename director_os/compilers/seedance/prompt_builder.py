"""PromptBuilder — assembles rich cinematic prompt from mapped intent parts."""

from .mapper import (
    map_camera_movement,
    map_framing,
    map_lens,
    map_angle,
    map_lighting,
    map_mood,
    map_texture,
    map_transition,
    map_camera_body,
    map_lens_character,
    map_film_stock,
    map_render_engine,
    map_render_settings,
    map_color_grade,
)


class PromptBuilder:
    """Assembles translated parts into a cinematic, Seedance-optimized prompt."""

    def __init__(self, translator=None):
        self._tr = translator  # Translator instance or None
    def build(self, intent: dict, layers: dict = None) -> str:
        """Build a rich cinematic prompt, optionally enriched by 6-layer analysis."""
        _t = self._translate
        vis = intent.get("visual_direction", {})
        cam = intent.get("camera_strategy", {})
        chars = intent.get("character_direction", [])
        narrative = intent.get("narrative_intent", {})

        # Layer 1: Core visual prompt
        core_parts = []

        framing_raw = cam.get("framing", "")
        framing = map_framing(framing_raw) if framing_raw else ""
        char_name = self._get_char_name(chars, 0)
        char_action = self._get_char_action(chars, 0)
        char_name = _t(char_name) if char_name else ""
        char_action = _t(char_action) if char_action else ""

        if framing and char_name:
            if char_action:
                core_parts.append(f"{framing} {char_name} {char_action}")
            else:
                core_parts.append(f"{framing} of {char_name}")
        elif char_action:
            core_parts.append(f"{char_action}")
        elif framing:
            core_parts.append(f"{framing}")

        camera_body = vis.get("camera_body", "")
        if camera_body:
            body_desc = map_camera_body(camera_body)
            if body_desc:
                core_parts.append(f"shot on {body_desc}")

        lens_focal = cam.get("lens_character", "")
        if lens_focal:
            lens_mapped = map_lens(lens_focal)
            if lens_mapped and lens_mapped != lens_focal:
                core_parts.append(f"using {lens_mapped}")
            else:
                core_parts.append(f"using {lens_focal}")

        lens_char = vis.get("lens_character", "")
        if lens_char:
            char_desc = map_lens_character(lens_char)
            if char_desc and char_desc != lens_char:
                core_parts.append(f"with {char_desc}")

        movement_raw = cam.get("movement", "")
        if movement_raw and movement_raw.lower() != "static":
            movement = map_camera_movement(movement_raw)
            if movement:
                core_parts.append(f"with {movement}")

        perspective_raw = cam.get("perspective", "")
        if perspective_raw:
            angle = map_angle(perspective_raw)
            if angle:
                core_parts.append(f"from {angle}")

        vis_lighting = vis.get("lighting", "")
        if vis_lighting:
            lighting = map_lighting(vis_lighting)
            if lighting:
                core_parts.append(f"with {lighting}")

        mood_raw = vis.get("mood", [])
        if isinstance(mood_raw, list) and mood_raw:
            for m in mood_raw:
                mapped = map_mood(m)
                if mapped:
                    core_parts.append(mapped)
        elif isinstance(mood_raw, str) and mood_raw:
            mapped = map_mood(mood_raw)
            if mapped:
                core_parts.append(mapped)

        film_stock = vis.get("film_stock", "")
        if film_stock:
            film_desc = map_film_stock(film_stock)
            if film_desc:
                core_parts.append(f"on {film_desc}")

        texture_raw = vis.get("texture", "")
        if texture_raw:
            texture = map_texture(texture_raw)
            if texture:
                core_parts.append(f"with {texture}")

        color_grade = vis.get("color_grade", "")
        if color_grade:
            grade_desc = map_color_grade(color_grade)
            if grade_desc:
                core_parts.append(f"in a {grade_desc}")
        else:
            color_raw = vis.get("color", "")
            if color_raw:
                core_parts.append(f"in {color_raw} color palette")

        atmos = vis.get("atmosphere", "")
        if atmos:
            core_parts.append(f"{_t(atmos)} atmosphere")

        render_engine = vis.get("render_engine", "")
        if render_engine:
            engine_desc = map_render_engine(render_engine)
            if engine_desc:
                core_parts.append(f"with {engine_desc}")

        render_settings = vis.get("render_settings", "")
        if render_settings:
            settings_desc = map_render_settings(render_settings)
            if settings_desc:
                core_parts.append(f"featuring {settings_desc}")

        # Assemble core prompt (trim to ~55 words)
        prompt = ", ".join(core_parts)
        words = prompt.split()
        if len(words) > 55:
            prompt = " ".join(words[:55]) + "..."

        # Layer 2: Rich production brief
        brief_parts = []

        equip_parts = []
        if camera_body:
            equip_parts.append(f"{camera_body}")
        if lens_focal:
            equip_parts.append(f"{lens_focal}")
        if render_engine:
            equip_parts.append(f"{render_engine}")
        if render_settings:
            equip_parts.append(f"{render_settings}")
        if equip_parts:
            brief_parts.append(f"EQUIPMENT: {', '.join(equip_parts)}")

        scene_parts = []
        if char_name and char_action:
            scene_parts.append(f"SCENE: {char_name} {char_action}")
        elif char_name:
            scene_parts.append(f"SCENE: {char_name}")

        color_desc = color_grade or vis.get("color", "")
        if color_desc:
            scene_parts.append(f"COLOR: {color_desc}")

        if scene_parts:
            brief_parts.extend(scene_parts)

        premise = narrative.get("premise", "")
        if premise:
            brief_parts.append(f"ACTION: {_t(premise)}")

        # Combine prompt with brief
        if brief_parts:
            brief = "\n".join(brief_parts)
            prompt = f"{prompt}\n\n{brief}"

        # Layer enrichment: inject structured layer insights
        if layers:
            l1 = layers.get("l1_baseline", {})
            l4 = layers.get("l4_camera", {})
            l6 = layers.get("l6_microtexture", {})

            extra = []
            style_anchor = l1.get("style_anchor", "")
            res = l1.get("resolution", "")
            if style_anchor and res:
                extra.append(f"VISUAL DIRECTION: {_t(style_anchor)} | {res} output")
            elif style_anchor:
                extra.append(f"VISUAL DIRECTION: {_t(style_anchor)}")

            sb = l4.get("storyboard_summary", "")
            if sb:
                extra.append(f"SHOT SEQUENCE: {_t(sb)}")

            specs = l6.get("quality_specifications", [])
            if specs:
                extra.append(f"TEXTURE SPEC: {'; '.join(specs[:4])}")

            if extra:
                prompt += "\n" + "\n".join(extra)

        return prompt

    def build_shot_prompt(self, shot: dict, layers: dict = None) -> str:
        """Build a prompt for a single shot."""
        parts = []

        framing_raw = shot.get("framing", "")
        framing = map_framing(framing_raw) if framing_raw else ""
        movement_raw = shot.get("movement", "")
        movement = map_camera_movement(movement_raw) if movement_raw else ""
        action = shot.get("action", "")

        if framing and action:
            parts.append(f"{framing} {action}")
        elif framing:
            parts.append(f"{framing}")
        elif action:
            parts.append(f"{action}")

        lens_raw = shot.get("lens", "")
        if lens_raw:
            lens_desc = map_lens(lens_raw)
            if lens_desc:
                parts.append(f"using {lens_desc}")

        if movement:
            parts.append(f"camera {movement}")

        return ", ".join(parts) if parts else ""

    def _translate(self, text: str) -> str:
        """Translate free-text through the injected translator (passthrough if none)."""
        if self._tr is None:
            return text
        return self._tr.translate(text)

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

    @staticmethod
    def _get_nested(d: dict, path: str, default: str = "") -> str:
        keys = path.split(".")
        current = d
        for key in keys:
            try:
                if key.isdigit():
                    current = current[int(key)]
                else:
                    current = current.get(key, {})
            except (IndexError, KeyError, TypeError, ValueError):
                return default
        if isinstance(current, str):
            return current
        if isinstance(current, list):
            return current[0] if current else default
        return str(current) if current else default
