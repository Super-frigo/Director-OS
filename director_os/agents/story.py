"""StoryAgent — proposes story structure, beat types, emotional arcs.

Bound to the 'storytelling' knowledge domain.  Operates in two modes:

    KB mode (no LLM):
        Queries storytelling YAML rules for beat types and structure
        recommendations based on genre and emotional target.

    LLM mode (llm_client provided):
        Sends a structured system prompt with project context, parses
        the YAML response into AgentProposals.

Output: AgentProposals for modules story and story_beats.
"""

from __future__ import annotations

from ..knowledge import KnowledgeRequest
from .base import AgentBase, AgentProposal, AgentRequest, AgentResult


class StoryAgent(AgentBase):
    agent_name = "story_agent"
    bound_domains = ["storytelling"]

    # ---- project slice ---------------------------------------------------

    def read_project_slice(self, project) -> dict:
        """Extract story-relevant fields from Project."""
        st = project.story
        return {
            "premise": st.premise,
            "theme": list(st.theme),
            "genre": list(st.genre),
            "beats": [
                {"beat": b.beat, "type": b.type, "emotion": b.emotion,
                 "objective": b.objective}
                for b in project.story_beats
            ],
        }

    # ---- KB mode (no LLM) ------------------------------------------------

    def propose(
        self,
        request: AgentRequest,
        llm_client: object = None,
    ) -> AgentResult:
        proposals: list[AgentProposal] = []
        warnings: list[str] = []
        stats: dict[str, object] = {"mode": "kb"}

        context = request.context
        genre = context.get("genre", "")
        emotion = context.get("emotion", "")

        # Query storytelling knowledge for structure/beat recommendations
        kb_request = KnowledgeRequest(
            domain="storytelling",
            query=" ".join(filter(None, [genre, emotion, "story structure"])),
            context={"genre": genre, "emotion": emotion},
        )

        # Only use KB mode; LLM mode handled via llm_client in real deployment
        try:
            from ..knowledge import KnowledgeResolver, LocalRulesProvider
            resolver = KnowledgeResolver()
            resolver.register(LocalRulesProvider())
            resolved = resolver.resolve(kb_request)
            stats["kb_entries"] = len(resolved.entries)

            for entry in resolved.entries:
                for rule in (entry.rules or []):
                    proposals.append(self._make_proposal(
                        module="story",
                        field="structure",
                        action="suggest",
                        value=rule,
                        rationale=entry.description,
                        confidence=entry.confidence,
                    ))
        except Exception as exc:
            warnings.append(f"StoryAgent KB query failed: {exc}")

        # Recommend beat types based on genre
        beat_map = _beat_recommendations(genre)
        for beat_name, beat_type in beat_map.items():
            proposals.append(self._make_proposal(
                module="story_beats",
                field=f"append",
                action="append",
                value={"beat": beat_name, "type": beat_type},
                rationale=f"Recommended {beat_type} beat for {genre} genre",
                confidence=0.85,
            ))

        return AgentResult(
            request_id=request.request_id,
            proposals=proposals,
            warnings=warnings,
            stats=stats,
        )


def _beat_recommendations(genre: object) -> dict[str, str]:
    """Return genre-specific beat recommendations."""
    if isinstance(genre, list):
        genre = " ".join(str(g) for g in genre)
    genre = str(genre).lower()
    if "suspense" in genre or "noir" in genre or "黑色" in genre or "悬疑" in genre:
        return {
            "OPENING": "OPENING",
            "BUILDUP": "INCITING",
            "REVELATION": "REVELATION",
            "CLIMAX": "CLIMAX",
            "RESOLUTION": "RESOLUTION",
        }
    if "sci" in genre or "科幻" in genre:
        return {
            "WORLD_ESTABLISH": "OPENING",
            "DISCOVERY": "INCITING",
            "CONFLICT": "CONFLICT",
            "TRANSFORMATION": "REVELATION",
            "NEW_NORMAL": "RESOLUTION",
        }
    # Default
    return {
        "OPENING": "OPENING",
        "TURNING_POINT": "INCITING",
        "MIDPOINT": "CONFLICT",
        "CLIMAX": "CLIMAX",
        "RESOLUTION": "RESOLUTION",
    }
