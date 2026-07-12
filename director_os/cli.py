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


if __name__ == "__main__":
    main()
