"""Interactive chat mode for Director OS.

Usage:
    python -m director_os.cli chat

Requires OPENAI_API_KEY (or OPENAI_BASE_URL for DeepSeek/other providers).

ChatDirector wraps a Director + LLM client into an interactive REPL. Each
turn the LLM receives a dynamic system prompt with the current project
state and responds in a structured format: natural language (shown to
the user) followed by an optional YAML actions block that ChatDirector
parses and executes.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from typing import Any

from .director import Director
from .state import DirectorState


# ---------------------------------------------------------------------------
# Structured response from LLM
# ---------------------------------------------------------------------------

_ACTIONS_SEP = re.compile(r"^---\s*actions\s*$", re.MULTILINE)
_YAML_LOADER: Any = None


def _get_yaml():
    global _YAML_LOADER
    if _YAML_LOADER is None:
        import yaml
        _YAML_LOADER = yaml.safe_load
    return _YAML_LOADER


@dataclass
class ChatResponse:
    message: str = ""
    actions: list[dict[str, str]] = field(default_factory=list)


def _parse_response(raw: str) -> ChatResponse:
    """Split LLM output into natural-language message and YAML actions."""
    parts = _ACTIONS_SEP.split(raw, maxsplit=1)
    message = parts[0].strip()
    actions: list[dict[str, str]] = []
    if len(parts) > 1 and parts[1].strip():
        yaml_load = _get_yaml()
        try:
            parsed = yaml_load(parts[1])
            if isinstance(parsed, dict):
                cmds = parsed.get("commands", parsed.get("actions", []))
                if isinstance(cmds, list):
                    normalized: list[dict[str, str]] = []
                    for a in cmds:
                        if isinstance(a, str):
                            normalized.append({"action": a})
                        elif isinstance(a, dict):
                            # Single-key dict like {run_agents: story} → {"action": "run_agents", ...}
                            normalized.append(a)
                        else:
                            normalized.append({"action": str(a)})
                    actions = normalized
        except Exception:
            pass  # If YAML is broken, just ignore the actions block
    return ChatResponse(message=message, actions=actions)


# ---------------------------------------------------------------------------
# System prompt builder
# ---------------------------------------------------------------------------

_PROMPT_HEADER = """You are the Director of Director OS — an AI-native filmmaking system.

Your job: guide the user through creating a film project. Think like a director,
not a prompt engineer. You have access to specialist agents (Story, Camera,
Continuity) and platform compilers (Seedance, Veo).

## Current project
"""

_PROMPT_FOOTER = """
## Response format
Respond with natural language for the user, then optionally include a YAML
actions block for operations you want to execute. Example:

  I've planned a 5-beat noir structure for your story...

  ---actions
  commands:
    - run_agents: story
    - plan
    - compile: seedance

## Available commands
  load: path           — load a project file
  new: title|premise   — create a new project
  plan                 — run the Engine pipeline
  run_agents: name,...  — run specialist agents (story, camera, continuity)
  apply                — apply pending agent proposals to the project
  compile: platform    — compile to Seedance/Veo prompt
  save: path           — validate and save the project
  show: summary|shots|characters|beats|validate
  help                 — show available commands

Keep your response concise and director-like. Speak the user's language.
Return ONLY the response — no extra commentary outside the format.
"""


def _build_system_prompt(director: Director) -> str:
    """Construct a dynamic system prompt with current project state."""
    p = director.project
    state = director.state.value

    if p is None or not p.metadata.title:
        project_block = """title: (no project loaded)
state: {}

Use 'new: title|premise' or 'load: path' to start.""".format(state)
    else:
        shots_n = len(p.shots)
        chars_n = len(p.characters)
        beats_n = len(p.story_beats)
        dur = p.output_profile.duration
        dur_str = f"{dur}s" if dur else "not set"
        issues = p.validate()
        status = "valid" if not issues else f"{len(issues)} issues"

        project_block = f"""title: {p.metadata.title}
premise: {p.story.premise[:120]}
genre: {', '.join(p.story.genre) if p.story.genre else 'not set'}
status: {p.metadata.status}
state: {state}
characters: {chars_n}
story beats: {beats_n}
shots: {shots_n}
duration: {dur_str}
validation: {status}
legal next states: {director.get_legal_transitions()}"""

        if issues:
            project_block += f"\nissues: {'; '.join(issues[:3])}"

    return _PROMPT_HEADER + project_block + _PROMPT_FOOTER


# ---------------------------------------------------------------------------
# ChatDirector — the interactive REPL
# ---------------------------------------------------------------------------

class ChatDirector:
    """Wraps a Director + LLM client into an interactive chat loop.

    Each turn:
        1. User types a message
        2. LLM receives system prompt (project state) + conversation context
        3. LLM responds with natural language [+ optional YAML actions]
        4. Actions are executed on the Director
        5. Results are shown to the user
    """

    def __init__(self, director: Director, client: Any):
        if director._llm_client is None:
            director._llm_client = client
        self.director = director
        self.client = client
        self.history: list[tuple[str, str]] = []  # (role, content)
        self.turn_count = 0

    def chat_turn(self, user_input: str) -> ChatResponse:
        """Process one turn: send to LLM, parse response, execute actions.

        Returns the parsed ChatResponse for display + testing.
        """
        self.turn_count += 1

        # Guard: ensure Director is ready for a cycle if idle
        if self.director.state == DirectorState.IDLE and user_input.strip():
            try:
                self.director.start_cycle(user_input[:200])
            except Exception:
                pass  # Continue even if cycle start fails

        # Build system prompt
        system = _build_system_prompt(self.director)

        # Build user message with conversation context
        context_lines = []
        for role, content in self.history[-6:]:  # last 3 exchanges
            prefix = "User" if role == "user" else "Director"
            context_lines.append(f"{prefix}: {content}")
        if context_lines:
            context_str = "## Conversation history\n" + "\n".join(context_lines) + "\n\n"
        else:
            context_str = ""
        user_msg = f"{context_str}## User says\n{user_input}"

        # Call LLM
        raw = self.client.chat(system, user_msg)
        if not raw:
            raw = "(No response from LLM — check your API key and model.)"

        # Parse
        resp = _parse_response(raw)

        # Store in history
        self.history.append(("user", user_input[:500]))
        self.history.append(("assistant", resp.message[:1000]))

        # Execute actions
        self._execute_actions(resp.actions)

        return resp

    # ── action execution ──────────────────────────────────────────────

    def _execute_actions(self, actions: list[dict[str, str]]) -> list[str]:
        """Execute parsed YAML actions on the Director. Returns log lines."""
        log: list[str] = []
        d = self.director

        for a in actions:
            cmd = (a.get("action", a.get("command", "")) or
                   next(iter(a)) if a else "").strip()
            if not cmd:
                continue

            try:
                log.append(self._exec_one(cmd, a))
            except Exception as exc:
                log.append(f"✗ {cmd}: {exc}")

        return log

    def _exec_one(self, cmd: str, a: dict[str, str]) -> str:
        d = self.director

        # If cmd is empty but a is a single-key dict (YAML parsed {run_agents: story}),
        # use the key as the command and the value as additional context.
        if not cmd and len(a) == 1:
            cmd = next(iter(a))
        cmd_lower = cmd.lower()

        # ── project lifecycle ──
        if cmd_lower == "plan":
            d.fast_forward_to(DirectorState.PLAN)
            d.plan()
            return "✓ Plan complete — ProductionIntent generated"

        if cmd_lower == "compile" or cmd_lower.startswith("compile:"):
            platform = a.get("platform", cmd.split(":")[-1].strip() or "seedance")
            d.fast_forward_to(DirectorState.COMPILE)
            pkg = d.compile(platform)
            prompt = pkg.instructions.get("prompt", "")
            preview = prompt[:300] + ("..." if len(prompt) > 300 else "")
            return f"✓ Compiled for {platform}\n{preview}"

        if cmd_lower.startswith("save:") or cmd_lower.startswith("save "):
            path = a.get("path", cmd.split(":", 1)[-1].strip())
            d.fast_forward_to(DirectorState.COMMIT)
            d.save_project(path)
            return f"✓ Saved to {path}"

        if cmd_lower.startswith("load:") or cmd_lower.startswith("load "):
            path = a.get("path", cmd.split(":", 1)[-1].strip())
            d.load_project(path)
            d.start_cycle(f"load {path}")
            return f"✓ Loaded {d.project.metadata.title} ({len(d.project.shots)} shots)"

        if cmd_lower.startswith("new:") or cmd_lower.startswith("new "):
            spec = cmd.split(":", 1)[-1].strip()
            parts = spec.split("|", 1)
            title = parts[0].strip()
            premise = parts[1].strip() if len(parts) > 1 else ""
            d.new_project(title=title, premise=premise)
            return f"✓ Created '{title}'"

        # ── agents ──
        if cmd_lower.startswith("run_agents:") or cmd_lower.startswith("run_agents "):
            names = cmd.split(":", 1)[-1].strip()
            agents = [n.strip() for n in names.split(",")] if names else None
            d._require_state({DirectorState.PLAN, DirectorState.DESIGN, DirectorState.VALIDATE})
            result = d.run_agent_cycle(target_agents=agents)
            n_proposals = len(result["proposals"])
            n_warnings = len(result["warnings"])
            return f"✓ Agents ran: {n_proposals} proposals, {n_warnings} warnings"

        if cmd_lower == "apply":
            return self.apply_last_cycle()

        # ── show ──
        if cmd_lower.startswith("show:") or cmd_lower.startswith("show "):
            what = cmd.split(":", 1)[-1].strip().lower()
            return _format_show(d, what)

        if cmd_lower == "help":
            return "Commands: new, load, plan, run_agents, apply, compile, save, show"

        return f"? Unknown command: {cmd}"

    # ── apply after agents ────────────────────────────────────────────

    def apply_last_cycle(self) -> str:
        """Re-run the last agent cycle and apply its proposals. Returns summary."""
        d = self.director
        if d.state not in {DirectorState.PLAN, DirectorState.DESIGN, DirectorState.VALIDATE}:
            return "✗ Cannot apply — not in PLAN/DESIGN/VALIDATE state"
        cycle = d.run_agent_cycle()
        result = d.apply_proposals(cycle["proposals"])
        applied = len(result["applied"])
        skipped = len(result["skipped"])
        errors = len(result["errors"])
        parts = [f"{applied} applied"]
        if skipped:
            parts.append(f"{skipped} skipped")
        if errors:
            parts.append(f"{errors} errors: {'; '.join(result['errors'][:2])}")
        return "✓ " + ", ".join(parts)


# ---------------------------------------------------------------------------
# Show formatters
# ---------------------------------------------------------------------------

def _format_show(d: Director, what: str) -> str:
    p = d.project
    if p is None:
        return "No project loaded"

    if what in ("summary", ""):
        return (
            f"**{p.metadata.title}** — {p.story.premise[:100]}\n"
            f"  State: {d.state.value} | Status: {p.metadata.status}\n"
            f"  Characters: {len(p.characters)} | Beats: {len(p.story_beats)} "
            f"| Shots: {len(p.shots)} | Duration: {p.output_profile.duration}s"
        )

    if what in ("shots", "shot"):
        if not p.shots:
            return "No shots defined"
        lines = [f"{len(p.shots)} shots:"]
        for s in p.shots:
            lines.append(
                f"  {s.shot_id}: {s.framing or '?'} {s.lens or ''} "
                f"{s.movement or ''} — {s.emotion.target or s.lighting.mood or ''}"
            )
        return "\n".join(lines)

    if what in ("characters", "character"):
        if not p.characters:
            return "No characters defined"
        lines = [f"{len(p.characters)} characters:"]
        for c in p.characters:
            lines.append(f"  {c.id}: {c.name} ({c.role}) — {c.personality[:3] if c.personality else ''}")
        return "\n".join(lines)

    if what in ("beats", "beat", "story_beats"):
        if not p.story_beats:
            return "No story beats defined"
        lines = [f"{len(p.story_beats)} beats:"]
        for b in p.story_beats:
            lines.append(f"  {b.beat} [{b.type}] — {b.emotion or ''}")
        return "\n".join(lines)

    if what == "validate":
        issues = d.validate_project()
        if not issues:
            return "✓ Project is valid"
        return f"{len(issues)} issues:\n" + "\n".join(f"  - {i}" for i in issues)

    return f"Unknown show target: {what}"


# ---------------------------------------------------------------------------
# REPL loop (invoked from CLI)
# ---------------------------------------------------------------------------

def run_chat(client: Any) -> None:
    """Main REPL loop. Press Ctrl+C or type /quit to exit."""
    director = Director()
    chat = ChatDirector(director, client)

    print()
    print("╔══════════════════════════════════════════╗")
    print("║       Director OS — Interactive Chat     ║")
    print("╠══════════════════════════════════════════╣")
    print("║  Type your film idea to start.           ║")
    print("║  /quit  — exit                           ║")
    print("║  /show  — project summary                ║")
    print("║  /help  — available commands             ║")
    print("╚══════════════════════════════════════════╝")
    print()

    while True:
        try:
            user_input = input("You › ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue

        # Slash-commands (shortcuts, bypass LLM)
        if user_input.startswith("/"):
            _handle_slash(chat, director, user_input)
            continue

        # Send to LLM
        print("Director › ", end="", flush=True)
        try:
            resp = chat.chat_turn(user_input)
            print(resp.message)
            # Show action results
            for action in resp.actions:
                cmd = (action.get("action", action.get("command", "")) or
                       next(iter(action)) if action else "")
                # Execute synchronously so side effects take effect
                try:
                    result = chat._exec_one(str(cmd), action)
                    if not result.startswith("✓"):  # verbose result (compile output)
                        print(f"  {result}")
                except Exception:
                    pass
        except Exception as exc:
            print(f"(Error: {exc})")


def _handle_slash(chat: ChatDirector, director: Director, raw: str) -> None:
    """Handle slash-commands that bypass the LLM."""
    raw = raw[1:]  # strip leading /
    parts = raw.split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if cmd == "quit" or cmd == "exit":
        raise EOFError

    if cmd == "help":
        print("Commands: /show, /save <path>, /compile <platform>, /plan, /agents, /quit")
        return

    if cmd == "show":
        what = arg or "summary"
        print(_format_show(director, what))
        return

    if cmd == "save":
        path = arg or "projects/chat_output.md"
        try:
            director.fast_forward_to(DirectorState.COMMIT)
            director.save_project(path)
            print(f"✓ Saved to {path}")
        except Exception as exc:
            print(f"✗ Save failed: {exc}")
        return

    if cmd == "compile":
        platform = arg or "seedance"
        try:
            director.fast_forward_to(DirectorState.COMPILE)
            pkg = director.compile(platform)
            print(f"\n── {platform.upper()} Prompt ──")
            print(pkg.instructions.get("prompt", ""))
            if pkg.validation.get("warnings"):
                print(f"\n  Warnings: {pkg.validation['warnings']}")
        except Exception as exc:
            print(f"✗ Compile failed: {exc}")
        return

    if cmd == "plan":
        try:
            director.fast_forward_to(DirectorState.PLAN)
            director.plan()
            print("✓ Plan complete")
        except Exception as exc:
            print(f"✗ Plan failed: {exc}")
        return

    if cmd == "agents":
        try:
            director._require_state({DirectorState.PLAN, DirectorState.DESIGN, DirectorState.VALIDATE})
            cycle = director.run_agent_cycle()
            print(f"✓ {len(cycle['proposals'])} proposals from agents")
            for p in cycle['proposals'][:5]:
                print(f"  [{p['agent']}] {p['action']} {p['module']}.{p['field']} = {str(p['value'])[:60]}")
            if len(cycle['proposals']) > 5:
                print(f"  ... and {len(cycle['proposals']) - 5} more")
        except Exception as exc:
            print(f"✗ Agents failed: {exc}")
        return

    if cmd == "apply":
        result = chat.apply_last_cycle()
        print(result)
        return

    if cmd == "load":
        path = arg
        if not path:
            print("Usage: /load <path>")
            return
        try:
            director.load_project(path)
            print(f"✓ Loaded {director.project.metadata.title}")
        except Exception as exc:
            print(f"✗ Load failed: {exc}")
        return

    print(f"? Unknown command: /{cmd}")
