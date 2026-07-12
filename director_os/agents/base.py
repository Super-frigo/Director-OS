"""Agent base protocol — the common interface for all specialist agents.

Each agent implements:
    agent_name: str                 — unique identifier
    bound_domains: list[str]        — knowledge domains
    read_project_slice(project)     — extract narrow Project subset
    propose(request, llm_client)    — generate AgentProposals

Design constraints (ADR-009):
    - Agents never talk directly to the user
    - Agents never talk directly to each other
    - All agent output is structured (AgentProposal), never natural language
    - Director is the sole orchestrator

Usage:
    from director_os.agents.base import AgentBase, AgentProposal, AgentRequest, AgentResult
    from director_os.agents.story import StoryAgent
    from director_os.agents.camera import CameraAgent
    from director_os.agents.continuity import ContinuityAgent
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


# ---- Structured output types ------------------------------------------------


@dataclass
class AgentProposal:
    """A single structured modification proposed by an agent.

    Maps to a specific module/field in the Project dataclass tree.
    Field uses dotted notation: 'story.premise', 'shots[0].framing',
    'visual_language.style'.
    """

    proposal_id: str = field(default_factory=lambda: uuid4().hex[:8])
    agent: str = ""          # e.g. "story_agent", "camera_agent"
    module: str = ""         # Project module: story, characters, shots, visual_language
    field: str = ""          # dotted path to the field
    action: str = ""         # "set" | "append" | "remove" | "suggest"
    value: object = None     # the proposed value
    rationale: str = ""      # human-readable justification
    confidence: float = 1.0  # 0.0 – 1.0

    def __repr__(self) -> str:
        cls = type(self).__name__
        return (
            f"{cls}({self.agent}/{self.action} {self.module}.{self.field}"
            f"={self.value!r} [{self.confidence:.0%}])"
        )


@dataclass
class AgentRequest:
    """Task dispatched from Director to a specialist agent."""

    request_id: str = field(default_factory=lambda: uuid4().hex[:8])
    agent: str = ""               # target agent name
    project_slice: dict = field(default_factory=dict)
    context: dict = field(default_factory=dict)  # intent, cycle_id, emotion, genre...
    constraints: dict = field(default_factory=lambda: {"max_proposals": 10})


@dataclass
class AgentResult:
    """Aggregated output from one agent call."""

    request_id: str = ""
    proposals: list[AgentProposal] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


# ---- Agent base -------------------------------------------------------------


class AgentBase:
    """Protocol base class for specialist agents.

    Subclasses must provide:
        agent_name: str
        bound_domains: list[str]

    Subclasses may override:
        read_project_slice(project) -> dict
        propose(request, llm_client) -> AgentResult
    """

    agent_name: str = "base"
    bound_domains: list[str] = []

    def read_project_slice(self, project) -> dict:
        """Extract the narrow subset of Project this agent cares about.

        Override in subclasses to read only the relevant modules.
        Default: returns empty dict (agent has full access via project).
        """
        return {}

    def propose(
        self,
        request: AgentRequest,
        llm_client: object = None,
    ) -> AgentResult:
        """Generate structured change proposals.

        Args:
            request: The task with project_slice and context.
            llm_client: Optional LLMClient protocol for LLM-powered reasoning.
                        When None, falls back to knowledge-based rules only.

        Returns:
            AgentResult with proposals, warnings, and call statistics.
        """
        raise NotImplementedError

    def _make_proposal(
        self,
        module: str,
        field: str,
        action: str,
        value: object,
        rationale: str = "",
        confidence: float = 1.0,
    ) -> AgentProposal:
        """Convenience factory for proposals with agent name auto-filled."""
        return AgentProposal(
            agent=self.agent_name,
            module=module,
            field=field,
            action=action,
            value=value,
            rationale=rationale,
            confidence=confidence,
        )
