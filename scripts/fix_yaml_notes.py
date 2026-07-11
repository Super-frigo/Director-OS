"""Fix YAML notes values that contain unescaped colons in project files."""

import re
from pathlib import Path


def fix_notes_values(path: Path) -> bool:
    """Quote YAML 'notes:' values that contain ':' to prevent YAML parse errors."""
    raw = path.read_text(encoding="utf-8-sig")
    lines = raw.splitlines()
    modified = False
    fixed_lines = []

    for line in lines:
        stripped = line.strip()
        # Match lines like: "    notes: some text: more text"
        match = re.match(r"^(\s*notes:\s*)(.*)", stripped)
        if match:
            prefix = match.group(1)
            value = match.group(2)
            if ":" in value and not (value.startswith('"') or value.startswith("'")):
                # Unquoted value containing colon — wrap in quotes
                value_escaped = value.replace("\\", "\\\\").replace('"', '\\"')
                fixed_lines.append(f"{prefix}\"{value_escaped}\"")
                modified = True
                print(f"  Fixed: {prefix}\"{value[:40]}...\"")
                continue
        fixed_lines.append(line)

    if modified:
        text = "\n".join(fixed_lines)
        if raw.endswith("\n"):
            text += "\n"
        path.write_text(text, encoding="utf-8-sig")
    return modified


if __name__ == "__main__":
    import sys
    for p in sys.argv[1:]:
        path = Path(p)
        if path.exists():
            print(f"Checking {path}...")
            if fix_notes_values(path):
                print(f"  ✓ Fixed")
            else:
                print(f"  ✓ No issues")
