"""Veo Compiler — translates ProductionIntent into Veo ExecutionPackage.

Veo (Google DeepMind) generates richer output with longer, detailed
cinematic descriptions — the opposite constraint from Seedance.
"""

from ..base.compiler import Compiler
from .prompt_builder import VeoPromptBuilder
from .mapper import map_camera_movement, map_framing


class VeoCompiler(Compiler):
    """Google DeepMind Veo platform compiler."""

    platform = "veo"

    def __init__(self):
        self.prompt_builder = VeoPromptBuilder()

    def compile(self, production_intent: dict) -> dict:
        prompt = self.prompt_builder.build(production_intent)
        params = self._extract_parameters(production_intent)
        validation = self._validate(production_intent)
        return {
            "execution_package": {
                "schema_version": "1.0",
                "target": {"provider": "veo", "model": production_intent.get("target_model", "veo-v1")},
                "instructions": {"prompt": prompt},
                "parameters": params,
                "validation": validation,
            }
        }

    def compile_with_layers(self, production_intent: dict, layers: dict) -> dict:
        prompt = self.prompt_builder.build(production_intent, layers=layers)
        params = self._extract_parameters(production_intent)
        validation = self._validate(production_intent)
        return {
            "execution_package": {
                "schema_version": "1.0",
                "target": {"provider": "veo", "model": production_intent.get("target_model", "veo-v1")},
                "instructions": {"prompt": prompt},
                "parameters": params,
                "validation": validation,
            }
        }

    def _extract_parameters(self, intent: dict) -> dict:
        camera = intent.get("camera_strategy", {})
        temporal = intent.get("temporal_design", {})
        params = {}
        movement = camera.get("movement", "")
        if movement:
            params["camera_motion"] = map_camera_movement(movement)
        framing = camera.get("framing", "")
        if framing:
            params["framing"] = map_framing(framing)
        duration = temporal.get("duration", "")
        if duration:
            params["duration"] = duration
        return params

    def _validate(self, intent: dict) -> dict:
        warnings = []
        # Veo supports up to 60s, so no duration warning
        characters = intent.get("character_direction", [])
        if len(characters) > 4:
            warnings.append(f"{len(characters)} characters may cause consistency drift")
        return {"warnings": warnings, "unsupported_features": [], "transformations": []}
