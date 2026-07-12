"""CameraAgent — proposes shot-level camera, lighting, and composition choices.

Bound to knowledge domains: camera, lighting, composition.

KB mode: maps emotional targets to recommended framing/lens/movement via
         knowledge resolution + built-in lookup tables.

LLM mode: sends structured system prompt, parses YAML response.

Output: AgentProposals for module 'shots' (framing, lens, movement, lighting,
        composition) and 'visual_language' (style, color).
"""

from __future__ import annotations

from ..knowledge import KnowledgeRequest
from .base import AgentBase, AgentProposal, AgentRequest, AgentResult


# ---- Built-in lookup tables (KB mode fallback) ----------------------------


_FRAMING_BY_EMOTION: dict[str, str] = {
    "loneliness": "ELS",
    "isolation": "ELS",
    "intimacy": "CU",
    "love": "CU",
    "tension": "MS",
    "anxiety": "CU",
    "power": "LS",
    "vulnerability": "CU",
    "fear": "CU",
    "awe": "ELS",
    "confusion": "MS",
    "anger": "CU",
    "sorrow": "MLS",
    "joy": "MS",
    "cold": "MS",
    "unease": "MS",
}

_LENS_BY_EMOTION: dict[str, str] = {
    "loneliness": "24mm",
    "isolation": "35mm",
    "intimacy": "85mm",
    "love": "50mm",
    "tension": "50mm",
    "anxiety": "35mm",
    "power": "24mm",
    "vulnerability": "85mm",
    "fear": "24mm",
    "awe": "14mm",
    "confusion": "35mm",
    "cold": "85mm",
}

_LIGHTING_BY_MOOD: dict[str, str] = {
    "dark": "LOW_KEY",
    "noir": "LOW_KEY",
    "warm": "HIGH_KEY",
    "cold": "NATURAL",
    "romantic": "SOFT",
    "tense": "LOW_KEY",
    "mysterious": "LOW_KEY",
    "hopeful": "HIGH_KEY",
    "neutral": "THREE_POINT",
}


class CameraAgent(AgentBase):
    agent_name = "camera_agent"
    bound_domains = ["camera", "lighting", "composition"]

    # ---- project slice ---------------------------------------------------

    def read_project_slice(self, project) -> dict:
        """Extract visual-relevant fields from Project."""
        vl = project.visual_language
        return {
            "visual_style": vl.style,
            "shots": [
                {
                    "shot_id": s.shot_id,
                    "framing": s.framing,
                    "lens": s.lens,
                    "movement": s.movement,
                    "emotion": s.emotion.target,
                    "lighting_mood": s.lighting.mood,
                }
                for s in (project.shots or [])
            ],
            "color": vl.color if isinstance(vl.color, dict) else {"palette": str(vl.color)},
        }

    # ---- propose ----------------------------------------------------------

    def propose(
        self,
        request: AgentRequest,
        llm_client: object = None,
    ) -> AgentResult:
        proposals: list[AgentProposal] = []
        warnings: list[str] = []
        stats: dict[str, object] = {"mode": "kb"}

        context = request.context
        emotion = context.get("emotion", "").lower()
        shots = request.project_slice.get("shots", [])

        # KB lookup: emotion → framing / lens / lighting
        if emotion and shots:
            framing = _FRAMING_BY_EMOTION.get(emotion, "")
            lens = _LENS_BY_EMOTION.get(emotion, "")
            lighting = _LIGHTING_BY_MOOD.get(emotion, "")

            for i, shot in enumerate(shots):
                shot_emotion = (shot.get("emotion", "") or emotion).lower()
                s_framing = _FRAMING_BY_EMOTION.get(shot_emotion, framing)
                s_lens = _LENS_BY_EMOTION.get(shot_emotion, lens)
                s_lighting = _LIGHTING_BY_MOOD.get(shot_emotion, lighting)

                if s_framing:
                    proposals.append(self._make_proposal(
                        module="shots",
                        field=f"shots[{i}].framing",
                        action="set",
                        value=s_framing,
                        rationale=f"Emotion '{shot_emotion}' maps to {s_framing}",
                        confidence=0.9,
                    ))
                if s_lens:
                    proposals.append(self._make_proposal(
                        module="shots",
                        field=f"shots[{i}].lens",
                        action="set",
                        value=s_lens,
                        rationale=f"Emotion '{shot_emotion}' maps to {s_lens}",
                        confidence=0.85,
                    ))
                if s_lighting:
                    proposals.append(self._make_proposal(
                        module="shots",
                        field=f"shots[{i}].lighting.mood",
                        action="set",
                        value=s_lighting,
                        rationale=f"Mood '{shot_emotion}' maps to {s_lighting}",
                        confidence=0.8,
                    ))

        # Query composition knowledge
        try:
            from ..knowledge import KnowledgeResolver, LocalRulesProvider
            resolver = KnowledgeResolver()
            resolver.register(LocalRulesProvider())
            kb_request = KnowledgeRequest(
                domain="composition",
                query=emotion or "visual",
                context={"emotion": emotion},
            )
            resolved = resolver.resolve(kb_request)
            stats["kb_entries"] = len(resolved.entries)

            for entry in resolved.entries:
                for rule in (entry.rules or []):
                    proposals.append(self._make_proposal(
                        module="visual_language",
                        field="camera_philosophy",
                        action="suggest",
                        value=rule,
                        rationale=entry.description,
                        confidence=entry.confidence,
                    ))
        except Exception as exc:
            warnings.append(f"CameraAgent KB query failed: {exc}")

        # Deduplicate: keep highest-confidence proposal per field
        by_field: dict[str, AgentProposal] = {}
        for p in proposals:
            key = f"{p.module}.{p.field}"
            if key not in by_field or p.confidence > by_field[key].confidence:
                by_field[key] = p

        return AgentResult(
            request_id=request.request_id,
            proposals=list(by_field.values()),
            warnings=warnings,
            stats=stats,
        )
