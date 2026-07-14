#!/usr/bin/env python3
"""Director OS — CLI entry point.

Usage:
    python -m director_os.cli new --title "My Film" --premise "A story about..."
    python -m director_os.cli load projects/the_hanging.md --compile seedance
"""

import argparse
import sys
from pathlib import Path

from .director import Director
from .state import DirectorState


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="director-os",
        description="Director OS — AI-native filmmaking operating system",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # ── new ────────────────────────────────────────────────────
    new_p = sub.add_parser("new", help="Create a new project")
    new_p.add_argument("--title", default="Untitled")
    new_p.add_argument("--premise", default="")

    # ── load ────────────────────────────────────────────────────
    load_p = sub.add_parser("load", help="Load a project file")
    load_p.add_argument("path", type=Path)
    load_p.add_argument("--compile", choices=["seedance", "veo", "kling", "runway"],
                        help="Compile after loading")

    # ── validate ────────────────────────────────────────────────
    val_p = sub.add_parser("validate", help="Validate a project file")
    val_p.add_argument("path", type=Path)

    # ── save ──────────────────────────────────────────────────────
    save_p = sub.add_parser("save", help="Save a project file (with auto-version and history)")
    save_p.add_argument("path", type=Path)
    save_p.add_argument("--message", "-m", default="", help="Commit message (recorded in history)")

    # ── mcp ────────────────────────────────────────────────────────
    sub.add_parser("mcp", help="Start MCP server (requires: pip install mcp[cli])")

    # ── chat ────────────────────────────────────────────────────────
    sub.add_parser("chat", help="Interactive chat with Director (requires OPENAI_API_KEY)")

    args = parser.parse_args()
    director = Director()

    if args.command == "new":
        project = director.new_project(title=args.title, premise=args.premise)
        print(f"Project created: {project.metadata.title}")
        print(f"  Premise: {project.story.premise}")
        print(f"  Status:  {len(director.validate_project())} validation issues")

    elif args.command == "load":
        try:
            project = director.load_project(args.path)
            print(f"Project loaded: {project.metadata.title}")
            issues = director.validate_project()
            if issues:
                print(f"  Warnings:")
                for i in issues:
                    print(f"    - {i}")
            else:
                print(f"  Validation: passed")

            # CLI auto-fast-forwards through the state machine
            director.start_cycle(f"load {args.path}")
            director.fast_forward_to(DirectorState.PLAN)
            intent = director.plan()
            print(f"  Production Intent generated")

            if args.compile:
                director.fast_forward_to(DirectorState.COMPILE)
                pkg = director.compile(platform=args.compile)
                print(f"\n── {args.compile.upper()} Prompt ──")
                print(pkg.instructions.get("prompt", ""))
                if pkg.validation.get("warnings"):
                    print(f"\n  Warnings: {pkg.validation['warnings']}")

                # Translation quality check: warn if Chinese remains in the prompt
                _warn_untranslated(pkg.instructions.get("prompt", ""),
                                   has_llm=director.has_llm)

        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "validate":
        try:
            project = director.load_project(args.path)
            issues = director.validate_project()
            print(f"Project: {project.metadata.title}")
            if issues:
                print(f"Issues ({len(issues)}):")
                for i in issues:
                    print(f"  - {i}")
            else:
                print("No issues found — project is valid.")
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "save":
        try:
            project = director.load_project(args.path)
            print(f"Project loaded: {project.metadata.title} (v{project.metadata.version})")
            director.start_cycle(f"save {args.path}")
            director.fast_forward_to(DirectorState.PLAN)
            director.plan()
            director.fast_forward_to(DirectorState.COMMIT)
            issues = director.save_project(args.path, message=args.message)
            print(f"Saved: {project.metadata.title} v{project.metadata.version}")
            if issues:
                print(f"  Warnings: {issues}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "mcp":
        from .mcp_server import main as mcp_main
        mcp_main()

    elif args.command == "chat":
        _run_chat_mode()


def _warn_untranslated(prompt: str, has_llm: bool) -> None:
    """Warn the user if Chinese characters remain in the compiled prompt.

    AI video platforms (Seedance/Veo/Kling) perform better with English
    prompts. If the offline glossary left CJK text behind, point the user
    at the fix (configure an LLM for fluent translation).
    """
    from .compilers.offline_glossary import has_cjk

    if not has_cjk(prompt):
        return

    import re
    cjk_chars = len(re.findall(r'[\u4e00-\u9fff]', prompt))
    total_chars = len(prompt)
    ratio = cjk_chars / total_chars if total_chars else 0

    if has_llm:
        print(f"\n  ⚠ Note: {cjk_chars} Chinese characters remain in the prompt "
              f"({ratio:.0%}). The LLM may have skipped some fields — consider "
              f"re-running or reviewing the project source.")
    else:
        print(f"\n  ⚠ Note: {cjk_chars} Chinese characters remain in the prompt "
              f"({ratio:.0%}). AI video platforms work best with English. "
              f"Configure OPENAI_API_KEY for fluent translation, or expand "
              f"the offline glossary (director_os/compilers/offline_glossary.py).")


def _run_chat_mode() -> None:
    """Create an LLM client from env vars and launch the interactive chat."""
    import os

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        print(
            "Error: OPENAI_API_KEY is not set.\n"
            "  Set it to use the interactive chat:\n"
            "    export OPENAI_API_KEY=sk-...\n"
            "  Or for DeepSeek:\n"
            "    export OPENAI_API_KEY=sk-...\n"
            "    export OPENAI_BASE_URL=https://api.deepseek.com/v1\n"
            "    export OPENAI_MODEL=deepseek-chat\n",
            file=sys.stderr,
        )
        sys.exit(1)

    from .knowledge.llm_client import OpenAIClient
    from .chat import run_chat

    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    base_url = os.getenv("OPENAI_BASE_URL", "")

    client = OpenAIClient(
        api_key=api_key,
        model=model,
        base_url=base_url,
        temperature=0.7,
        max_tokens=2048,
    )
    run_chat(client)


if __name__ == "__main__":
    main()
