"""Engine interface and pipeline orchestrator."""

from dataclasses import dataclass, field
from typing import Any

from ..models.project import Project
from ..models.production_intent import ProductionIntent, CharacterDirection
from ..layers import LayerPipeline


@dataclass
class EngineInput:
    project: Project
    context: dict = field(default_factory=dict)
    libraries: dict = field(default_factory=dict)


class BaseEngine:
    """Subclass per engine module."""

    def process(self, inp: EngineInput) -> dict:
        raise NotImplementedError


def _get_duration(s: object) -> str:
    """Extract duration string from a Shot or scalar."""
    return str(s) if s else ""


class StoryEngine(BaseEngine):
    """Extract story data from project."""

    def process(self, inp: EngineInput) -> dict:
        project = inp.project
        return {
            "premise": project.story.premise,
            "genre": project.story.genre,
            "theme": project.story.theme,
            "acts": project.story.structure.get("acts", []),
            "creative_goal": {
                "primary": project.story.premise,
                "emotional_target": [],
            },
        }


class CharacterEngine(BaseEngine):
    """Extract character data from project."""

    def process(self, inp: EngineInput) -> dict:
        directions = []
        for ch in inp.project.characters:
            directions.append(CharacterDirection(
                id=ch.id,
                name=ch.name,
                performance=ch.role,
                emotional_state="",
                action="",
            ))
        return {"characters": directions}


class VisualEngine(BaseEngine):
    """Extract visual language data from project."""

    def process(self, inp: EngineInput) -> dict:
        vl = inp.project.visual_language
        primary_framing = ""
        primary_lens = ""
        primary_movement = ""
        primary_lighting = ""
        if inp.project.shots:
            first = inp.project.shots[0]
            primary_framing = first.framing
            primary_lens = first.lens
            primary_movement = first.movement
            if first.lighting:
                primary_lighting = first.lighting.mood or first.lighting.key_light

        mood = []
        color_val = vl.color
        if isinstance(color_val, dict):
            color_palette = color_val.get("palette", color_val.get("description", ""))
        else:
            color_palette = str(color_val)

        return {
            "style": vl.style,
            "mood": mood,
            "composition": primary_framing,
            "color": color_palette,
            "texture": vl.texture if vl.texture else (vl.color.get("texture", "") if isinstance(vl.color, dict) else ""),
            "atmosphere": vl.atmosphere if vl.atmosphere else vl.lighting,
            "lighting": primary_lighting if primary_lighting else vl.lighting,
            "camera_body": vl.camera_body,
            "lens_character": vl.lens_character,
            "film_stock": vl.film_stock,
            "color_grade": vl.color_grade,
            "render_engine": vl.render_engine,
            "render_settings": vl.render_settings,
        }


class ShotEngine(BaseEngine):
    """Extract shot-level data from project shot list."""

    def process(self, inp: EngineInput) -> dict:
        shots_data = []
        for shot in inp.project.shots:
            shots_data.append({
                "shot_id": shot.shot_id,
                "purpose": shot.beat_ref,
                "framing": shot.framing,
                "movement": shot.movement,
                "lens": shot.lens,
                "perspective": shot.angle,
                "action": shot.subject.action,
                "duration": str(shot.duration) + "s" if shot.duration else "",
                "lighting": shot.lighting.mood,
            })
        return {"shots": shots_data}


class EnginePipeline:
    """Orchestrates engine modules to produce a ProductionIntent."""

    def __init__(self):
        self.engines: dict[str, BaseEngine] = {
            "story": StoryEngine(),
            "character": CharacterEngine(),
            "visual": VisualEngine(),
            "shot": ShotEngine(),
        }
        self.layer_pipeline = LayerPipeline()

    def analyze_layers(self, project, intent_dict: dict, shots: list[dict]) -> dict:
        """Run 6-layer analysis on the project and intent."""
        return self.layer_pipeline.analyze(project, intent_dict, shots)

    def run(self, inp: EngineInput) -> ProductionIntent:
        results: dict[str, Any] = {}
        for name, engine in self.engines.items():
            results[name] = engine.process(inp)

        story_out = results.get("story", {})
        char_out = results.get("character", {})
        vis_out = results.get("visual", {})
        shot_out = results.get("shot", {})

        shots = shot_out.get("shots", [])
        camera_strategy = {
            "framing": vis_out.get("composition", ""),
            "movement": _first_shot_field(shots, "movement", ""),
            "perspective": _first_shot_field(shots, "perspective", ""),
            "lens_character": _first_shot_field(shots, "lens", ""),
            "focus_behavior": "",
        }

        project = inp.project
        temporal_design = {
            "pacing": "",
            "motion_style": "",
            "duration": str(len(shots) * 4) + "s",
        }

        scene = {"scene_id": "", "shot_id": ""}
        if project.scenes:
            scene["scene_id"] = project.scenes[0].id
        if shots:
            scene["shot_id"] = shots[0].get("shot_id", "")

        return ProductionIntent(
            scene=scene,
            creative_goal=story_out.get("creative_goal", {}),
            narrative_intent={
                "premise": story_out.get("premise", ""),
                "genre": story_out.get("genre", []),
                "theme": story_out.get("theme", []),
            },
            visual_direction={
                "style": vis_out.get("style", ""),
                "mood": vis_out.get("mood", []),
                "composition": vis_out.get("composition", ""),
                "color": vis_out.get("color", ""),
                "texture": vis_out.get("texture", ""),
                "atmosphere": vis_out.get("atmosphere", ""),
                "lighting": vis_out.get("lighting", ""),
                "camera_body": vis_out.get("camera_body", ""),
                "lens_character": vis_out.get("lens_character", ""),
                "film_stock": vis_out.get("film_stock", ""),
                "color_grade": vis_out.get("color_grade", ""),
                "render_engine": vis_out.get("render_engine", ""),
                "render_settings": vis_out.get("render_settings", ""),
            },
            camera_strategy=camera_strategy,
            character_direction=char_out.get("characters", []),
            environment_direction={},
            temporal_design=temporal_design,
            audio_intent={},
            consistency_requirements={"characters": [], "environment": []},
            constraints={"must": [], "avoid": [], "limitations": []},
        )


def _first_shot_field(shots: list[dict], field: str, default: str = "") -> str:
    """Return the first non-empty shot field value."""
    for s in shots:
        val = s.get(field, "")
        if val:
            return val
    return default





