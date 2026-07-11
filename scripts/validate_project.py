#!/usr/bin/env python3
"""Validate a Director OS project file against the canonical schema.

Usage:
    python scripts/validate_project.py projects/the_hanging.md
    python scripts/validate_project.py projects/*.md --verbose

Dependencies: PyYAML (already in project requirements)
"""

import argparse
import re
import sys
from pathlib import Path

# Allow running from project root or scripts/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def load_yaml(path: Path) -> dict:
    """Load a project YAML file, stripping Markdown headers and --- separators."""
    try:
        import yaml
    except ImportError:
        sys.exit("PyYAML is required: pip install pyyaml")

    raw = path.read_text(encoding="utf-8-sig")
    cleaned = []
    for line in raw.splitlines():
        if re.match(r"^#{2,}\s+", line):
            continue
        if line.strip() == "---":
            continue
        cleaned.append(line)
    clean_text = "\n".join(cleaned)
    data = yaml.safe_load(clean_text)
    if not isinstance(data, dict):
        sys.exit(f"{path.name}: expected a YAML mapping, got {type(data).__name__}")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Director OS project files")
    parser.add_argument("files", nargs="+", type=Path, help="Project .md or .yaml files to validate")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all checks, not just failures")
    args = parser.parse_args()

    from schemas.project_schema import validate_yaml

    total = 0
    passed = 0
    failed = 0

    for path in args.files:
        if not path.exists():
            print(f"  SKIP: {path.name} (not found)")
            continue

        total += 1
        print(f"  {path.name} ... ", end="")

        try:
            data = load_yaml(path)
        except Exception as e:
            print(f"LOAD ERROR: {e}")
            failed += 1
            continue

        errors = validate_yaml(data)

        if errors:
            print(f"FAIL ({len(errors)} issues)")
            for e in errors:
                print(f"    - {e}")
            failed += 1
        else:
            print("PASS")
            passed += 1
            if args.verbose:
                _print_summary(data)

    print()
    print(f"Results: {passed}/{total} passed" +
          (f", {failed} failed" if failed else ""))

    if failed:
        sys.exit(1)


def _print_summary(data: dict) -> None:
    """Print a brief project summary when --verbose."""
    meta = data.get("metadata", {})
    shots = data.get("shots", [])
    beats = data.get("story_beats", [])
    chars = data.get("characters", [])
    print(f"      title={meta.get('title', '?')}  status={meta.get('status', '?')}  "
          f"shots={len(shots)}  beats={len(beats)}  characters={len(chars)}")


if __name__ == "__main__":
    main()
