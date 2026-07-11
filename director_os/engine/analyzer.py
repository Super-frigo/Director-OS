"""Requirement Analyzer — identifies knowledge gaps from Project context.

Vision Step 5: The Analyzer sits between Project and Knowledge Resolver,
inspecting the current creative state and determining what domain knowledge
the Engine needs but doesn't yet have.
"""

from dataclasses import dataclass, field
from typing import Any

from ..knowledge import KnowledgeRequest


@dataclass
class AnalysisResult:
    """Output of RequirementAnalyzer: a set of knowledge requests."""
    requests: list[KnowledgeRequest] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


class RequirementAnalyzer:
    """Inspects project + engine state and identifies knowledge gaps.

    Usage:
        analyzer = RequirementAnalyzer()
        result = analyzer.analyze(project, engine_input)
        # result.requests → list of KnowledgeRequest for the resolver
    """

    # Domains that map to engine concerns
    DOMAIN_MAP = {
        "story": "storytelling",
        "character": "storytelling",
        "visual": "visual_style",
        "shot": "cinematography",
    }

    def analyze(self, project: Any, engine_input: dict) -> AnalysisResult:
        """Inspect project state and return knowledge requests.

        Args:
            project: Project dataclass
            engine_input: dict with keys like 'story', 'character', 'visual', 'shot'
                          (partial engine outputs already generated)

        Returns:
            AnalysisResult with prioritized KnowledgeRequest list
        """
        requests: list[KnowledgeRequest] = []
        notes: list[str] = []

        # --- Story domain ---
        story_out = engine_input.get("story", {})
        premise = story_out.get("premise", project.story.premise if hasattr(project, "story") else "")
        genre = (project.story.genre[0] if hasattr(project, "story") and project.story.genre else "")
        if genre:
            requests.append(KnowledgeRequest(
                request_id="story_structure",
                domain="storytelling",
                query=f"story structure for {genre}",
                context={"genre": genre, "premise": premise[:200] if premise else ""},
            ))

        # --- Character domain ---
        if hasattr(project, "characters") and project.characters:
            char_count = len(project.characters)
            roles = [c.role for c in project.characters if hasattr(c, "role")]
            requests.append(KnowledgeRequest(
                request_id="character_design",
                domain="storytelling",
                query="character archetypes and relationships",
                context={"character_count": char_count, "roles": roles},
            ))

        # --- Visual domain ---
        vis_out = engine_input.get("visual", {})
        style = vis_out.get("style", "")
        mood_list = vis_out.get("mood", [])
        if style:
            requests.append(KnowledgeRequest(
                request_id="visual_style",
                domain="visual_style",
                query=f"visual style reference for {style}",
                context={"style": style},
            ))
        if mood_list and isinstance(mood_list, list) and mood_list:
            requests.append(KnowledgeRequest(
                request_id="lighting_mood",
                domain="lighting",
                query=f"lighting for mood: {', '.join(str(m) for m in mood_list)}",
                context={"mood": mood_list[0] if mood_list else ""},
            ))

        # --- Shot domain ---
        shot_out = engine_input.get("shot", {})
        shots = shot_out.get("shots", [])
        if shots:
            primary_emotion = ""
            if hasattr(project, "shots") and project.shots:
                first_shot = project.shots[0]
                primary_emotion = getattr(first_shot, "emotion", "") or ""
            requests.append(KnowledgeRequest(
                request_id="shot_composition",
                domain="composition",
                query=f"composition for {len(shots)} shots",
                context={"shot_count": len(shots), "emotion": primary_emotion},
            ))
            requests.append(KnowledgeRequest(
                request_id="camera_language",
                domain="cinematography",
                query="camera movement and lens for shot sequence",
                context={"shot_count": len(shots)},
            ))

        # Deduplicate by domain + query
        seen = set()
        deduped: list[KnowledgeRequest] = []
        for req in requests:
            key = (req.domain, req.query)
            if key not in seen:
                seen.add(key)
                deduped.append(req)
            else:
                notes.append(f"Skipped duplicate request: {req.domain}/{req.query[:40]}")

        return AnalysisResult(requests=deduped, notes=notes)
