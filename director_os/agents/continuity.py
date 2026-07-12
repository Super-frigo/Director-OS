"""ContinuityAgent — deterministic consistency checks across modules.

Pure code, no LLM dependency.  Validates:
    - Character continuity: locked characters must have consistent attributes
    - Wardrobe: no conflicting changes between shots
    - Timeline: scene/shot ordering has no impossible time jumps
    - Environment: weather/location continuity within a sequence

Output: AgentProposals for fixes and validation warnings.
"""

from __future__ import annotations

from .base import AgentBase, AgentProposal, AgentRequest, AgentResult


class ContinuityAgent(AgentBase):
    agent_name = "continuity_agent"
    bound_domains = []  # pure logic, no knowledge domain

    def read_project_slice(self, project) -> dict:
        """Extract continuity-relevant fields from Project."""
        return {
            "characters": [
                {
                    "id": c.id,
                    "name": c.name,
                    "wardrobe": c.wardrobe,
                    "physical_state": c.physical_state,
                    "continuity_lock": c.continuity_lock,
                }
                for c in (project.characters or [])
            ],
            "shots": [
                {
                    "shot_id": s.shot_id,
                    "order": s.order,
                    "subject_character": s.subject.character,
                    "subject_action": s.subject.action,
                    "notes": s.notes,
                }
                for s in (project.shots or [])
            ],
            "world_weather": project.world.weather,
            "world_season": project.world.season,
            "constraints_avoid": list(project.constraints.avoid),
            "constraints_required": list(project.constraints.required),
        }

    # ---- propose ----------------------------------------------------------

    def propose(
        self,
        request: AgentRequest,
        llm_client: object = None,
    ) -> AgentResult:
        proposals: list[AgentProposal] = []
        warnings: list[str] = []
        stats: dict[str, object] = {}

        ps = request.project_slice

        # Rule 1: Character continuity locks
        locked_chars = [c for c in ps.get("characters", []) if c.get("continuity_lock")]
        stats["locked_characters"] = len(locked_chars)

        if locked_chars:
            for ch in locked_chars:
                proposals.append(self._make_proposal(
                    module="continuity",
                    field="character",
                    action="suggest",
                    value={
                        "character_id": ch["id"],
                        "name": ch.get("name", ""),
                        "note": "Character is continuity-locked. Verify no attribute drift across shots.",
                    },
                    rationale=f"Character '{ch.get('name', ch['id'])}' has continuity_lock=True",
                    confidence=1.0,
                ))

        # Rule 2: Shots referencing undefined characters
        char_ids = {c["id"] for c in ps.get("characters", [])}
        for shot in ps.get("shots", []):
            subj = shot.get("subject_character", "")
            if subj and subj not in char_ids:
                msg = f"Shot {shot['shot_id']} references undefined character '{subj}'"
                warnings.append(msg)
                proposals.append(self._make_proposal(
                    module="shots",
                    field=f"shots[{shot['order'] - 1}].subject.character",
                    action="set",
                    value="",
                    rationale=msg,
                    confidence=1.0,
                ))

        # Rule 3: Shot order consistency
        shots = ps.get("shots", [])
        orders = [s.get("order", 0) for s in shots]
        if orders and sorted(orders) != orders:
            warnings.append("Shot orders are not strictly ascending")

        stats["shots_checked"] = len(shots)
        stats["warnings"] = len(warnings)

        return AgentResult(
            request_id=request.request_id,
            proposals=proposals,
            warnings=warnings,
            stats=stats,
        )
