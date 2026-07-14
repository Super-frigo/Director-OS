"""Gate 1 — Schema Gate: YAML structure validation.

Validates generated knowledge entries against library.schema.yaml.
Checks: required fields, enum values, ID format, ID uniqueness, YAML syntax.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# Allowed category values. Schema doc lists 9 values, but existing lighting
# entries use "lighting" in practice — we include it for backward compatibility.
ALLOWED_CATEGORIES = [
    "cinematography",
    "storytelling",
    "character",
    "visual_style",
    "genre",
    "production",
    "sound",
    "editing",
    "model_capability",
    "lighting",  # used by existing entries; not in schema doc but in practice
]

# Category ↔ directory mapping (plan adjustment: plan categories → actual directories)
CATEGORY_DIR_MAP = {
    "camera": "camera",
    "lighting": "lighting",
    "color": "color",
}

# ID prefix patterns per category directory
ID_PREFIX_PATTERNS = {
    "camera": r"^(lens_|movement_|angle_|height_|shot_size_|framing_)",
    "lighting": r"^light_",
    "color": r"^color_",
}

# Required top-level keys
REQUIRED_SECTIONS = [
    "metadata", "category", "knowledge",
    "applicability", "engine_guidance", "version",
]

# Required fields within sections
REQUIRED_FIELDS = {
    "metadata": ["id", "name"],
    "knowledge": ["concept", "principles", "emotional_effects", "techniques", "constraints"],
    "applicability": ["emotions", "genres", "keywords"],
    "engine_guidance": ["when_to_use", "recommended_actions", "avoid"],
}


@dataclass
class SchemaIssue:
    """A single schema validation issue."""

    entry_id: str
    severity: str  # error | warning
    field: str
    description: str
    suggestion: str = ""


@dataclass
class SchemaGateResult:
    """Result of schema gate validation."""

    passed: bool
    issues: list[SchemaIssue] = field(default_factory=list)
    entry_ids: set[str] = field(default_factory=set)


class SchemaGate:
    """Gate 1: Validate YAML knowledge entries against schema."""

    def __init__(self, schema_path: Path | str | None = None):
        if schema_path:
            self._schema_path = Path(schema_path)
        else:
            # Default: project root / schemas / library.schema.yaml
            self._schema_path = Path(__file__).resolve().parents[2] / "schemas" / "library.schema.yaml"

        self._seen_ids: set[str] = set()

    def validate_file(self, file_path: Path) -> SchemaGateResult:
        """Validate a single YAML file."""
        return self.validate_entry(file_path, self._load_yaml(file_path))

    def validate_entry(self, file_path: Path, data: dict) -> SchemaGateResult:
        """Validate a parsed entry dict."""
        issues: list[SchemaIssue] = []
        entry_id = ""

        # --- YAML structure: must have library key ---
        if "library" not in data:
            issues.append(SchemaIssue(
                entry_id="<unknown>",
                severity="error",
                field="root",
                description="Missing 'library' top-level key",
                suggestion="Wrap content under 'library:' key",
            ))
            return SchemaGateResult(passed=False, issues=issues)

        lib = data["library"]

        # --- schema_version ---
        if lib.get("schema_version") != "1.0":
            issues.append(SchemaIssue(
                entry_id=lib.get("metadata", {}).get("id", "<unknown>"),
                severity="error",
                field="schema_version",
                description=f"Expected '1.0', got '{lib.get('schema_version')}'",
                suggestion="Set schema_version: '1.0'",
            ))

        # --- Required sections ---
        entry_id = lib.get("metadata", {}).get("id", "<unknown>")
        for section in REQUIRED_SECTIONS:
            if section not in lib:
                issues.append(SchemaIssue(
                    entry_id=entry_id,
                    severity="error",
                    field=section,
                    description=f"Missing required section '{section}'",
                    suggestion=f"Add '{section}' section",
                ))

        # --- Required fields within sections ---
        for section, fields in REQUIRED_FIELDS.items():
            if section not in lib:
                continue
            for fld in fields:
                val = lib[section].get(fld)
                if val is None or (isinstance(val, list) and len(val) == 0):
                    issues.append(SchemaIssue(
                        entry_id=entry_id,
                        severity="warning",
                        field=f"{section}.{fld}",
                        description=f"Empty or missing field '{fld}' in '{section}'",
                        suggestion=f"Provide at least one value for '{fld}'",
                    ))

        # --- Category enum check ---
        category = lib.get("category", "")
        if category and category not in ALLOWED_CATEGORIES:
            issues.append(SchemaIssue(
                entry_id=entry_id,
                severity="error",
                field="category",
                description=f"Invalid category '{category}'. Allowed: {ALLOWED_CATEGORIES}",
                suggestion=f"Use one of: {', '.join(ALLOWED_CATEGORIES)}",
            ))

        # --- ID format check ---
        if entry_id and entry_id != "<unknown>":
            if not re.match(r"^[a-z][a-z0-9_]+$", entry_id):
                issues.append(SchemaIssue(
                    entry_id=entry_id,
                    severity="error",
                    field="metadata.id",
                    description=f"Invalid ID format '{entry_id}'. Must be lowercase with underscores.",
                    suggestion="Use format like 'lens_24mm_wide'",
                ))

        # --- ID uniqueness ---
        if entry_id and entry_id != "<unknown>":
            if entry_id in self._seen_ids:
                issues.append(SchemaIssue(
                    entry_id=entry_id,
                    severity="error",
                    field="metadata.id",
                    description=f"Duplicate ID '{entry_id}'",
                    suggestion="Use a unique identifier",
                ))
            else:
                self._seen_ids.add(entry_id)

        # --- List type checks ---
        list_fields = [
            "knowledge.principles", "knowledge.emotional_effects",
            "knowledge.techniques", "knowledge.constraints",
            "applicability.emotions", "applicability.genres",
            "applicability.keywords", "engine_guidance.recommended_actions",
            "engine_guidance.avoid",
        ]
        for lf in list_fields:
            parts = lf.split(".", 1)
            if len(parts) == 2 and parts[0] in lib and parts[1] in lib[parts[0]]:
                val = lib[parts[0]][parts[1]]
                if not isinstance(val, list):
                    issues.append(SchemaIssue(
                        entry_id=entry_id,
                        severity="error",
                        field=lf,
                        description=f"Expected list, got {type(val).__name__}",
                        suggestion=f"Convert '{lf}' to a YAML list",
                    ))

        has_errors = any(i.severity == "error" for i in issues)
        return SchemaGateResult(
            passed=not has_errors,
            issues=issues,
            entry_ids={entry_id} if entry_id else set(),
        )

    def validate_directory(self, dir_path: Path) -> SchemaGateResult:
        """Validate all YAML files in a directory."""
        all_issues: list[SchemaIssue] = []
        all_ids: set[str] = set()

        if not dir_path.exists():
            return SchemaGateResult(passed=False, issues=[
                SchemaIssue("<dir>", "error", dir_path, f"Directory does not exist: {dir_path}")
            ])

        for yaml_file in sorted(dir_path.glob("*.yaml")):
            result = self.validate_file(yaml_file)
            all_issues.extend(result.issues)
            all_ids.update(result.entry_ids)

        has_errors = any(i.severity == "error" for i in all_issues)
        return SchemaGateResult(passed=not has_errors, issues=all_issues, entry_ids=all_ids)

    @staticmethod
    def _load_yaml(file_path: Path) -> dict:
        """Load a YAML file, returning empty dict on parse failure."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            # Return a minimal dict that will fail validation
            return {"_parse_error": str(e)}
