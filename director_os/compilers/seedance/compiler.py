"""Seedance Compiler — translates ProductionIntent into Seedance ExecutionPackage.

Architecture:
    Production Intent (dict)
        |
    SeedanceCompiler
        ├── mapper.py       (translation: Intent → Seedance concepts)
        ├── prompt_builder.py  (assembly: concepts → fluent prompt)
        └── capabilities.yaml  (platform constraints)
        |
    Execution Package (dict)
        |
    Seedance AI

The compiler is a pure adapter:
- It does NOT make creative decisions
- It does NOT know what makes a good story
- It only knows how to translate Production Intent into Seedance form
"""

from ..base.compiler import Compiler
from .prompt_builder import PromptBuilder
from .mapper import (
    map_camera_movement,
    map_framing,
    map_lens,
    map_mood,
    map_texture,
)


class SeedanceCompiler(Compiler):
    """Seedance platform compiler."""

    platform = "seedance"

    def __init__(self, translator=None):
        # Lazy-init translator from environment if not injected
        if translator is None:
            from ..translation import Translator, set_translator
            translator = Translator.create()
            set_translator(translator)
        else:
            from ..translation import set_translator
            set_translator(translator)
        self.prompt_builder = PromptBuilder(translator=translator)

    def compile(self, production_intent: dict) -> dict:
        """Translate a Production Intent dict into a Seedance Execution Package."""
        prompt = self.prompt_builder.build(production_intent)
        parameters = self._extract_parameters(production_intent)
        validation = self._validate(production_intent)
        return {
            "execution_package": {
                "schema_version": "1.0",
                "target": {
                    "provider": "seedance",
                    "model": production_intent.get("target_model", "default"),
                    "version": production_intent.get("target_version", ""),
                },
                "instructions": {
                    "prompt": prompt,
                },
                "parameters": parameters,
                "validation": validation,
            }
        }

    def compile_with_layers(self, production_intent: dict, layers: dict) -> dict:
        """Compile with 6-layer analysis data for richer prompting."""
        prompt = self.prompt_builder.build(production_intent, layers=layers)
        parameters = self._extract_parameters(production_intent)
        validation = self._validate(production_intent)
        return {
            "execution_package": {
                "schema_version": "1.0",
                "target": {
                    "provider": "seedance",
                    "model": production_intent.get("target_model", "default"),
                    "version": production_intent.get("target_version", ""),
                },
                "instructions": {
                    "prompt": prompt,
                },
                "parameters": parameters,
                "validation": validation,
            }
        }

    # ── shot-level compilation ──────────────────────────────────────

    def compile_shots(self, production_intent: dict) -> list[dict]:
        """Compile each shot in the intent into individual prompts."""
        character_directions = production_intent.get("character_direction", [])
        shots = production_intent.get("shots", [])

        packages = []
        for shot in shots:
            shot_prompt = self.prompt_builder.build_shot_prompt(shot)
            packages.append({
                "shot_id": shot.get("shot_id", ""),
                "prompt": shot_prompt,
                "parameters": self._extract_shot_params(shot),
            })
        return packages

    # ── parameter extraction ────────────────────────────────────────

    def _extract_parameters(self, intent: dict) -> dict:
        camera = intent.get("camera_strategy", {})
        visual = intent.get("visual_direction", {})
        temporal = intent.get("temporal_design", {})

        params = {}

        movement = camera.get("movement", "")
        if movement:
            params["camera_motion"] = map_camera_movement(movement)

        framing = camera.get("framing", "")
        if framing:
            params["framing"] = map_framing(framing)

        lens_char = camera.get("lens_character", "")
        if lens_char:
            params["lens"] = map_lens(lens_char)

        mood_raw = visual.get("mood", [])
        if isinstance(mood_raw, list) and mood_raw:
            moods = [map_mood(m) for m in mood_raw if m]
            if moods:
                params["mood"] = moods[0]
        elif isinstance(mood_raw, str) and mood_raw:
            params["mood"] = map_mood(mood_raw)

        texture_raw = visual.get("texture", "")
        if texture_raw:
            params["texture"] = map_texture(texture_raw)

        duration = temporal.get("duration", "")
        if duration:
            params["duration"] = duration

        return params

    def _extract_shot_params(self, shot: dict) -> dict:
        params = {}
        framing = shot.get("framing", "")
        if framing:
            params["framing"] = map_framing(framing)
        movement = shot.get("movement", "")
        if movement:
            params["camera_motion"] = map_camera_movement(movement)
        lens = shot.get("lens", "")
        if lens:
            params["lens"] = map_lens(lens)
        duration = shot.get("duration", "")
        if duration:
            params["duration"] = duration
        return params

    # ── validation ──────────────────────────────────────────────────

    def _validate(self, intent: dict) -> dict:
        warnings = []
        unsupported = []
        transformations = []

        camera = intent.get("camera_strategy", {})
        movement = camera.get("movement", "").lower()
        if movement in ("whip_pan", "snap_zoom", "complex"):
            unsupported.append(f"Seedance may not reliably render '{movement}' movement")
            transformations.append(f"'{movement}' → simplified camera move description")

        temporal = intent.get("temporal_design", {})
        duration_str = temporal.get("duration", "")
        if duration_str:
            try:
                duration = float(duration_str.replace("s", ""))
                if duration > 15:
                    warnings.append(
                        f"Duration {duration}s exceeds Seedance 15s maximum. "
                        "Consider splitting into multiple clips."
                    )
            except (ValueError, AttributeError):
                pass

        characters = intent.get("character_direction", [])
        if len(characters) > 2:
            warnings.append(
                f"{len(characters)} characters — Seedance consistency "
                "declines with more than 2 subjects."
            )

        return {
            "warnings": warnings,
            "unsupported_features": unsupported,
            "transformations": transformations,
        }

