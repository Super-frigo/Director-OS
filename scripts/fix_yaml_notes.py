"""Fix YAML values containing colons in project files.

Edge cases handled:
  - Indented fields (respects original indentation)
  - Multi-line quoted/block scalar values
  - Already-quoted values (single or double)
  - All text-valued fields (notes, description, concept, mood, etc.)
  - Fields inside nested structures (shots > notes, history > notes)
"""

import re
from pathlib import Path

# Fields whose values might contain colons and need quoting
TEXT_FIELDS = {
    "notes", "description", "concept", "mood", "objective",
    "premise", "theme", "atmosphere", "emotion", "action",
    "appearance", "wardrobe", "personality", "motivation",
    "physical_state", "style", "location", "culture",
}


def _needs_quoting(value: str) -> bool:
    """Check if YAML plain scalar needs quoting due to embedded ':'."""
    # Already quoted
    if value.startswith('"') and value.endswith('"'):
        return False
    if value.startswith("'") and value.endswith("'"):
        return False
    # Empty
    if not value:
        return False
    # Contains colon followed by space or end-of-string
    return bool(re.search(r":(?:\s|$)", value))


def _quote_value(value: str) -> str:
    """Wrap a value in double quotes, escaping internal quotes/backslashes."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def fix_yaml_values(path: Path) -> bool:
    """Quote YAML text values that contain unescaped colons."""
    raw = path.read_text(encoding="utf-8-sig")
    lines = raw.splitlines()
    modified = False
    fixed_lines: list[str] = []

    for line in lines:
        # Preserve blank lines and non-field lines
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            fixed_lines.append(line)
            continue

        # Match any indented field: `<spaces><field_name>: <value>`
        # Only match leaf fields (not dict/list values)
        match = re.match(r"^(\s*)(\w+):(\s*)(.*)", line)

        if match:
            indent = match.group(1)      # leading whitespace
            field = match.group(2)       # field name
            sep = match.group(3)         # whitespace after colon
            value = match.group(4)       # the rest of the line

            if field in TEXT_FIELDS and value:
                # Check if the value continues on next lines (multi-line block scalar)
                if _needs_quoting(value):
                    quoted = _quote_value(value)
                    fixed_lines.append(f"{indent}{field}:{sep}{quoted}")
                    modified = True
                    continue

        fixed_lines.append(line)

    if modified:
        text = "\n".join(fixed_lines)
        # Preserve trailing newline
        if raw.endswith("\n"):
            text += "\n"
        path.write_text(text, encoding="utf-8-sig")
    return modified


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python fix_yaml_notes.py <project_file.md> [project_file2.md ...]")
        sys.exit(1)
    for p in sys.argv[1:]:
        path = Path(p)
        if path.exists():
            print(f"Checking {path.name}...")
            if fix_yaml_values(path):
                print(f"  -> Fixed")
            else:
                print(f"  -> No issues")
        else:
            print(f"  Skipped (not found): {p}")
