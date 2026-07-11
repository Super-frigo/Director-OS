"""Engine interface and pipeline orchestrator."""

from dataclasses import dataclass, field
from typing import Any

from ..models.project import Project
from ..models.production_intent import ProductionIntent, CharacterDirection
from ..layers import LayerPipeline
from ..models.library_entry import LibraryEntry


@dataclass
class EngineInput:
    project: Project
    context: dict = field(default_factory=dict)
    libraries: dict = field(default_factory=dict)


class BaseEngine:
    """Subclass per engine module."""

    def process(self, inp: EngineInput) -> dict:
        raise NotImplementedError

    def _query_library(self, inp: EngineInput, category: str = "", emotion: str = "", genre: str = "") -> list[LibraryEntry]:
        """Query libraries by category / emotion / genre."""
        results: list[LibraryEntry] = []
        pool: list[LibraryEntry] = []
        if category:
            pool = inp.libraries.get(category, [])
        else:
            for entries in inp.libraries.values():
                pool.extend(entries)

        for entry in pool:
            app = entry.applicability
            if emotion and emotion not in app.get("emotions", []):
                continue
            if genre and genre not in app.get("genres", []):
                continue
            results.append(entry)
        return results


def _get_duration(s: object) -> str:
    """Extract duration string from a Shot or scalar."""
    return str(s) if s else ""


class StoryEngine(BaseEngine):
    """Extract story data from project, enriched by library knowledge."""

    def process(self, inp: EngineInput) -> dict:
        project = inp.project

        genre = project.story.genre[0] if project.story.genre else ""
        story_libs = self._query_library(inp, category="storytelling", genre=genre)
        beat_libs = [e for e in story_libs if "beat" in e.metadata.get("id", "").lower()]
        struct_libs = [e for e in story_libs if "act" in e.metadata.get("id", "").lower() or "structure" in e.metadata.get("id", "").lower()]
        world_libs = [e for e in story_libs if "world" in e.metadata.get("id", "").lower()]

        return {
            "premise": project.story.premise,
            "genre": project.story.genre,
            "theme": project.story.theme,
            "acts": project.story.structure.get("acts", []),
            "creative_goal": {
                "primary": project.story.premise,
                "emotional_target": [],
                "library_guidance": [
                    {"id": e.metadata.get("id", ""), "concept": e.knowledge.get("concept", "")}
                    for e in (beat_libs + struct_libs + world_libs)
                ],
            },
            "library_references": {
                "story_beats": [{"id": e.metadata.get("id", ""), "name": e.metadata.get("name", "")} for e in beat_libs],
                "structures": [{"id": e.metadata.get("id", ""), "name": e.metadata.get("name", "")} for e in struct_libs],
                "worldbuilding": [{"id": e.metadata.get("id", ""), "name": e.metadata.get("name", "")} for e in world_libs],
            },
        }


class CharacterEngine(BaseEngine):
    """Extract character data from project, enriched by library knowledge."""

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

        char_libs = self._query_library(inp, category="storytelling")
        char_archetypes = [
            {"id": e.metadata.get("id", ""), "concept": e.knowledge.get("concept", "")}
            for e in char_libs
            if "character" in e.metadata.get("id", "").lower() or "archetype" in e.metadata.get("id", "").lower()
        ]

        return {"characters": directions,
                "library_archetypes": char_archetypes,
                }


class VisualEngine(BaseEngine):
    """Extract visual language data from project, enriched by library knowledge."""

    def process(self, inp: EngineInput) -> dict:
        vl = inp.project.visual_language
        project = inp.project
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

        # Enrich with library knowledge
        story_genre = project.story.genre[0] if project.story.genre else ""
        style_libs = self._query_library(inp, category="visual_style", genre=story_genre)
        cinematography_libs = self._query_library(inp, category="cinematography")
        lighting_libs = self._query_library(inp, category="lighting")
        composition_libs = self._query_library(inp, category="composition")

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
            # Library-enriched guidance
            "library_style": [
                {"id": e.metadata.get("id", ""), "name": e.metadata.get("name", ""), "concept": e.knowledge.get("concept", "")}
                for e in style_libs
            ],
            "library_camera": [
                {"id": e.metadata.get("id", ""), "name": e.metadata.get("name", ""), "concept": e.knowledge.get("concept", "")}
                for e in cinematography_libs
            ],
            "library_lighting": [
                {"id": e.metadata.get("id", ""), "name": e.metadata.get("name", ""), "concept": e.knowledge.get("concept", "")}
                for e in lighting_libs
            ],
            "library_composition": [
                {"id": e.metadata.get("id", ""), "name": e.metadata.get("name", ""), "concept": e.knowledge.get("concept", "")}
                for e in composition_libs
            ],
        }


class ShotEngine(BaseEngine):
    """Extract shot-level data from project shot list, enriched by library knowledge."""

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

        # Enrich with library knowledge for shot composition reference
        camera_libs = self._query_library(inp, category="cinematography")
        lighting_libs = self._query_library(inp, category="lighting")
        composition_libs = self._query_library(inp, category="composition")
        matched_entries = []
        for entry in camera_libs + lighting_libs + composition_libs:
            matched_entries.append({
                "id": entry.metadata.get("id", ""),
                "name": entry.metadata.get("name", ""),
                "concept": entry.knowledge.get("concept", ""),
            })

        return {"shots": shots_data,
                "library_camera_lighting": matched_entries,
                }


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
                "library_style": vis_out.get("library_style", []),
                "library_camera": vis_out.get("library_camera", []),
                "library_lighting": vis_out.get("library_lighting", []),
                "library_composition": vis_out.get("library_composition", []),
            },
            camera_strategy=camera_strategy,
            character_direction=char_out.get("characters", []),
            environment_direction={
                "library_archetypes": char_out.get("library_archetypes", []),
            },
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
