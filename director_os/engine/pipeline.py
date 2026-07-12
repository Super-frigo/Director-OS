"""Engine interface and pipeline orchestrator."""

from dataclasses import dataclass, field
from typing import Any

from ..models.project import Project
from ..models.production_intent import ProductionIntent, CharacterDirection
from ..layers import LayerPipeline
from ..models.library_entry import LibraryEntry
from .analyzer import RequirementAnalyzer, AnalysisResult
from .enricher import ProjectEnricher, EnrichmentResult


@dataclass
class EngineInput:
    project: Project
    context: dict = field(default_factory=dict)
    # Legacy: dict-of-lists for backward compatibility
    libraries: dict = field(default_factory=dict)
    # New: Knowledge Resolver (ADR-008). When set, _query_library() delegates here.
    resolver: object | None = None  # director_os.knowledge.KnowledgeResolver


class BaseEngine:
    """Subclass per engine module."""

    def process(self, inp: EngineInput) -> dict:
        raise NotImplementedError

    def _query_library(self, inp: EngineInput, category: str = "", emotion: str = "", genre: str = "") -> list[LibraryEntry]:
        """Query libraries by category / emotion / genre."""
        # --- New path: Knowledge Resolver (ADR-008) ---
        if inp.resolver is not None:
            return _resolve_knowledge(inp.resolver, category, emotion, genre)

        # --- Legacy path: direct LibraryEntry search ---
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
    return str(s) if s is not None else ""


def _resolve_knowledge(resolver, domain: str, emotion: str = "", genre: str = "") -> list:
    """Bridge: call Knowledge Resolver and convert results to LibraryEntry list.

    This keeps backward compatibility with the existing engine code that
    consumes LibraryEntry objects. When engines are refactored to consume
    KnowledgeEntry directly, this bridge can be removed.
    """
    from ..knowledge import KnowledgeRequest
    from ..models.library_entry import LibraryEntry as LE

    query_parts = []
    if emotion:
        query_parts.append(emotion)
    if genre:
        query_parts.append(genre)

    request = KnowledgeRequest(
        domain=domain,
        query=" ".join(query_parts) if query_parts else domain,
        context={"emotion": emotion, "genre": genre},
    )
    resolved = resolver.resolve(request)

    # Convert KnowledgeEntry -> LibraryEntry (bridge)
    result: list = []
    for ke in resolved.entries:
        le = LE(
            metadata={"id": ke.entry_id, "name": ke.description[:60] if ke.description else ke.entry_id},
            category=ke.domain,
            knowledge={"concept": ke.description, "principles": ke.rules},
            applicability={"emotions": ke.keywords, "genres": [genre] if genre else [], "keywords": ke.keywords},
            engine_guidance={"when_to_use": "", "recommended_actions": ke.rules},
            examples={"successful": ke.examples},
        )
        result.append(le)
    return result


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
        # Vision Step 5: explicit analysis + enrichment stages
        self.analyzer = RequirementAnalyzer()
        self.enricher = ProjectEnricher()

    def analyze_layers(self, project, intent_dict: dict, shots: list[dict]) -> dict:
        """Run 6-layer analysis on the project and intent."""
        return self.layer_pipeline.analyze(project, intent_dict, shots)

    def run(self, inp: EngineInput) -> ProductionIntent:
        results: dict[str, Any] = {}
        for name, engine in self.engines.items():
            results[name] = engine.process(inp)

        # --- Vision Step 5: Analyze → Resolve → Enrich ---
        knowledge_enrichment: dict[str, Any] = {}
        if inp.resolver is not None:
            analysis = self.analyzer.analyze(inp.project, results)
            all_entries = []
            for req in analysis.requests:
                resolved = inp.resolver.resolve(req)
                all_entries.extend(resolved.entries)
            if all_entries:
                from ..knowledge import ResolvedKnowledge
                merged = ResolvedKnowledge(entries=all_entries)
                enrichment = self.enricher.enrich({}, merged)
                knowledge_enrichment = enrichment.enriched

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
            "duration": _total_shot_duration(shots),
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
                # Core visual fields
                "style": vis_out.get("style", ""),
                "mood": vis_out.get("mood", []),
                "composition": vis_out.get("composition", ""),
                "color": vis_out.get("color", ""),
                # Knowledge enrichment from Resolution pipeline
                "composition_guidance": _safe_guidance(knowledge_enrichment, "composition_guidance"),
                "lighting_guidance": _safe_guidance(knowledge_enrichment, "lighting_guidance"),
                "camera_guidance": _safe_guidance(knowledge_enrichment, "camera_guidance"),
                "style_guidance": _safe_guidance(knowledge_enrichment, "style_guidance"),
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


def _total_shot_duration(shots: list[dict]) -> str:
    """Sum per-shot durations into a total like '15s'.

    ShotEngine emits duration as '4.0s' / '3s' / '' (empty when unset).
    Shots without an explicit duration fall back to a 4s default so the
    total stays a reasonable estimate instead of silently dropping them.
    """
    if not shots:
        return ""
    total = 0.0
    for s in shots:
        raw = s.get("duration", "")
        if not raw:
            total += 4.0
            continue
        try:
            total += float(str(raw).rstrip("s"))
        except (ValueError, AttributeError):
            total += 4.0
    # Render as integer when whole (15s) else keep one decimal (15.5s)
    return f"{int(total)}s" if total.is_integer() else f"{total:g}s"


def _safe_guidance(enrichment: dict, key: str) -> dict:
    """Safely extract a guidance field from the enrichment result."""
    vd = enrichment.get("visual_direction", {})
    if not isinstance(vd, dict):
        return {}
    return vd.get(key, {})
