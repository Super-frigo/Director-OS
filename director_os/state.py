"""Director State Machine — implements DIRECTOR_STATE_MACHINE.md.

The state machine is the guard layer for the 7-stage creative pipeline.
It validates every state transition and carries a CycleContext through the
pipeline.  The LLM (Claude/GPT) acts as Director's "brain" — it decides when
to transition.  This module provides the "railings" that prevent skipping
stages or compiling before validation passes.

Usage:
    from director_os.state import DirectorState, TransitionError, CycleContext

    director.state           # DirectorState.IDLE
    director.start_cycle(input)   # IDLE → UNDERSTAND
    director.transition_to(DirectorState.PLAN)       # UNDERSTAND → PLAN  ✓
    director.transition_to(DirectorState.COMPILE)    # PLAN → COMPILE    ✗ StateError

Reference:
    docs/DIRECTOR_STATE_MACHINE.md  — full state definitions, entry/exit actions
    docs/WORKFLOW_SPEC.md           — 5 workflow modes driven by the state machine
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from uuid import uuid4


class DirectorState(enum.Enum):
    """8 states defined in DIRECTOR_STATE_MACHINE.md §3."""

    IDLE       = "idle"        # Waiting for user input
    UNDERSTAND = "understand"  # Parsing user intent
    CLARIFY    = "clarify"     # Asking user for missing info
    PLAN       = "plan"        # Creating creative plan (via Engine)
    DESIGN     = "design"      # Detailing shots/characters/lights
    VALIDATE   = "validate"    # Checking consistency rules
    COMMIT     = "commit"      # Writing to Project file
    COMPILE    = "compile"     # Generating platform prompt

    def __str__(self) -> str:
        return self.value


# ---- Transition table (DIRECTOR_STATE_MACHINE.md §4) --------------------

TRANSITIONS: dict[DirectorState, set[DirectorState]] = {
    DirectorState.IDLE:       {DirectorState.UNDERSTAND},
    DirectorState.UNDERSTAND: {DirectorState.CLARIFY, DirectorState.PLAN},
    DirectorState.CLARIFY:    {DirectorState.UNDERSTAND},       # user response → re-parse
    DirectorState.PLAN:       {DirectorState.DESIGN},
    DirectorState.DESIGN:     {DirectorState.VALIDATE},
    DirectorState.VALIDATE:   {DirectorState.PLAN, DirectorState.COMMIT},
    DirectorState.COMMIT:     {DirectorState.COMPILE, DirectorState.IDLE},
    DirectorState.COMPILE:    {DirectorState.IDLE},
}


class StateError(Exception):
    """Raised when an illegal state transition is attempted."""
    pass


def path_to(from_state: DirectorState, to_state: DirectorState) -> list[DirectorState]:
    """Compute the shortest legal path between two states (BFS on TRANSITIONS).

    Returns a list of intermediate states to visit (excluding *from_state*,
    including *to_state*).  Returns an empty list when *from_state* == *to_state*.

    Raises StateError if no path exists.
    """
    if from_state == to_state:
        return []

    from collections import deque
    visited: dict[DirectorState, DirectorState | None] = {from_state: None}
    queue = deque([from_state])

    while queue:
        current = queue.popleft()
        for neighbor in TRANSITIONS.get(current, set()):
            if neighbor not in visited:
                visited[neighbor] = current
                queue.append(neighbor)
                if neighbor == to_state:
                    # Reconstruct path
                    path: list[DirectorState] = []
                    node = to_state
                    while node != from_state:
                        path.append(node)
                        node = visited[node]  # type: ignore[assignment]
                    path.reverse()
                    return path

    raise StateError(
        f"No legal path from {from_state.value} to {to_state.value}"
    )


# ---- Cycle Context -------------------------------------------------------

@dataclass
class CycleContext:
    """Per-cycle data container (§5 of DIRECTOR_STATE_MACHINE.md).

    Carried through the pipeline so each state can reference the
    outputs of previous states.
    """

    cycle_id: str = field(default_factory=lambda: uuid4().hex[:8])
    user_input: str = ""
    state: DirectorState = DirectorState.IDLE
    turn_count: int = 0
