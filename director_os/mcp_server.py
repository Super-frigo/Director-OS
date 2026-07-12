"""MCP Server — exposes Director OS as MCP tools for LLM clients.

Start the server:
    python -m director_os.cli mcp
    # or:  director-os mcp

The server communicates over stdio (standard MCP transport).  Any MCP-capable
client (Claude Desktop, ZCode, Cursor, etc.) can connect and use Director OS
as a tool-providing Agent.

Install the optional dependency:
    pip install "mcp[cli]"

Reference:
    docs/adr/ADR-009.md  Agent Implementation Strategy
    docs/DIRECTOR_STATE_MACHINE.md  state machine spec
"""

from __future__ import annotations

import sys
from typing import Any


# Graceful import — only required when running as MCP server
try:
    from mcp.server.fastmcp import FastMCP
    _MCP_AVAILABLE = True
except ImportError:
    _MCP_AVAILABLE = False
    FastMCP = None  # type: ignore[assignment,misc]


def _ensure_mcp() -> None:
    """Raise a helpful error when mcp is not installed."""
    if not _MCP_AVAILABLE:
        print(
            "MCP SDK is not installed.\n"
            "Install it with:  pip install 'mcp[cli]'\n"
            "Then restart:     director-os mcp",
            file=sys.stderr,
        )
        sys.exit(1)


# ---- Lazy Director singleton -----------------------------------------------

_director = None


def _get_director():
    """Return a shared Director instance for the MCP session."""
    global _director
    if _director is None:
        from .director import Director
        _director = Director()
    return _director


# ---- Tool definitions ------------------------------------------------------

def _create_mcp() -> FastMCP:
    """Build and return the FastMCP application with all tools registered."""
    _ensure_mcp()

    mcp = FastMCP("director-os")

    # ── Project lifecycle ────────────────────────────────────────

    @mcp.tool()
    def new_project(title: str = "", premise: str = "") -> dict[str, Any]:
        """Create a new project. Returns a summary of the created project."""
        d = _get_director()
        p = d.new_project(title=title, premise=premise)
        return {
            "title": p.metadata.title,
            "status": p.metadata.status,
            "premise": p.story.premise,
            "characters": len(p.characters),
            "shots": len(p.shots),
        }

    @mcp.tool()
    def load_project(path: str) -> dict[str, Any]:
        """Load an existing project from disk. Returns a summary."""
        d = _get_director()
        p = d.load_project(path)
        return {
            "title": p.metadata.title,
            "status": p.metadata.status,
            "version": p.metadata.version,
            "premise": p.story.premise,
            "characters": len(p.characters),
            "shots": len(p.shots),
            "story_beats": len(p.story_beats),
            "visual_style": p.visual_language.style,
        }

    @mcp.tool()
    def save_project(path: str, message: str = "") -> dict[str, Any]:
        """Save (commit) the current project to disk. Requires COMMIT state."""
        d = _get_director()
        d.save_project(path, message=message)
        return {
            "title": d.project.metadata.title,
            "version": d.project.metadata.version,
            "updated": d.project.metadata.updated_at,
        }

    # ── State machine ─────────────────────────────────────────────

    @mcp.tool()
    def start_cycle(user_input: str) -> dict[str, Any]:
        """Begin a new creative cycle (IDLE → UNDERSTAND)."""
        d = _get_director()
        ctx = d.start_cycle(user_input)
        return {
            "cycle_id": ctx.cycle_id,
            "state": d.state.value,
            "legal_next": d.get_legal_transitions(),
        }

    @mcp.tool()
    def transition_to(state: str) -> dict[str, Any]:
        """Move to the target state. Returns current state and legal next states."""
        from .state import DirectorState, StateError
        d = _get_director()
        try:
            target = DirectorState(state)
        except ValueError:
            raise ValueError(
                f"Unknown state '{state}'. Valid states: "
                f"{[s.value for s in DirectorState]}"
            )
        d.transition_to(target)
        return {
            "state": d.state.value,
            "legal_next": d.get_legal_transitions(),
        }

    @mcp.tool()
    def get_state() -> dict[str, Any]:
        """Return the current state machine status."""
        d = _get_director()
        return {
            "state": d.state.value,
            "legal_next": d.get_legal_transitions(),
            "project": d.project.metadata.title if d.project else None,
        }

    # ── Creative pipeline ──────────────────────────────────────────

    @mcp.tool()
    def plan_project() -> dict[str, Any]:
        """Run Engine pipeline (requires PLAN state). Returns intent summary."""
        d = _get_director()
        intent = d.plan()
        return {
            "premise": intent.narrative_intent.get("premise", ""),
            "genre": intent.narrative_intent.get("genre", []),
            "visual_style": intent.visual_direction.get("style", ""),
            "shot_count": len(d.project.shots) if d.project else 0,
        }

    @mcp.tool()
    def validate_project() -> dict[str, Any]:
        """Run validation and return issues (if any)."""
        d = _get_director()
        issues = d.validate_project()
        return {
            "valid": len(issues) == 0,
            "issues": issues,
        }

    @mcp.tool()
    def compile_project(platform: str = "seedance") -> dict[str, Any]:
        """Compile the project into a platform prompt (requires COMPILE state)."""
        d = _get_director()
        pkg = d.compile(platform)
        return {
            "platform": platform,
            "prompt": pkg.instructions.get("prompt", ""),
            "warnings": pkg.validation.get("warnings", []),
        }

    @mcp.tool()
    def get_project_summary() -> dict[str, Any]:
        """Return an overview of the current project for the LLM's context."""
        d = _get_director()
        if not d.project:
            return {"error": "No project loaded"}
        p = d.project
        return {
            "title": p.metadata.title,
            "version": p.metadata.version,
            "status": p.metadata.status,
            "premise": p.story.premise,
            "genre": p.story.genre,
            "theme": p.story.theme,
            "characters": [
                {"id": c.id, "name": c.name, "role": c.role}
                for c in p.characters
            ],
            "shot_count": len(p.shots),
            "beat_count": len(p.story_beats),
            "visual_style": p.visual_language.style,
            "duration": p.output_profile.duration,
            "history_entries": len(p.history),
            "validation_issues": d.validate_project(),
        }

    return mcp


# ---- Entry point -----------------------------------------------------------

def main() -> None:
    """Start the MCP server on stdio."""
    _ensure_mcp()
    mcp = _create_mcp()
    mcp.run()


if __name__ == "__main__":
    main()
