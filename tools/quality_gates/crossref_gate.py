"""Gate 3 — Crossref Gate: Bidirectional relationship validation.

Checks:
1. Bidirectionality: A.related contains B → B.related must contain A
2. Conflict symmetry: A.conflicts contains B → B.conflicts must contain A
3. Consistency: conflicts and related should not overlap
4. Auto-fix:补全 missing reverse directions with auto_filled marker
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class CrossrefIssue:
    """A single cross-reference issue."""

    entry_id: str
    severity: str  # error | warning | auto_fixed
    field: str
    description: str
    suggestion: str = ""


@dataclass
class CrossrefGateResult:
    """Result of crossref gate validation."""

    passed: bool
    issues: list[CrossrefIssue] = field(default_factory=list)
    auto_fixes_applied: list[str] = field(default_factory=list)


class CrossrefGate:
    """Gate 3: Validate and auto-fix bidirectional relationships."""

    def __init__(self):
        self._entries: dict[str, dict] = {}

    def load_directory(self, dir_path: Path) -> None:
        """Load all YAML entries from a directory for cross-referencing."""
        self._entries.clear()
        if not dir_path.exists():
            return

        for yaml_file in sorted(dir_path.glob("*.yaml")):
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data and "library" in data:
                entry_id = data["library"].get("metadata", {}).get("id", "")
                if entry_id:
                    self._entries[entry_id] = {
                        "data": data,
                        "path": yaml_file,
                    }

    def load_entries(self, entries: list[dict]) -> None:
        """Load entries from a list of parsed dicts."""
        self._entries.clear()
        for data in entries:
            if data and "library" in data:
                entry_id = data["library"].get("metadata", {}).get("id", "")
                if entry_id:
                    self._entries[entry_id] = {"data": data, "path": None}

    def validate(self) -> CrossrefGateResult:
        """Run crossref checks without modifying files."""
        issues: list[CrossrefIssue] = []
        all_ids = set(self._entries.keys())

        for entry_id, entry_info in self._entries.items():
            rels = (
                entry_info["data"]
                .get("library", {})
                .get("relationships", {})
            )

            related = set(rels.get("related", []) or [])
            conflicts = set(rels.get("conflicts", []) or [])
            extensions = set(rels.get("extensions", []) or [])

            # --- Check references point to existing entries ---
            for ref_id in related | conflicts | extensions:
                if ref_id not in all_ids:
                    issues.append(CrossrefIssue(
                        entry_id=entry_id,
                        severity="warning",
                        field="relationships",
                        description=f"References non-existent entry '{ref_id}'",
                        suggestion=f"Remove '{ref_id}' or create the entry",
                    ))

            # --- Check related/conflicts overlap ---
            overlap = related & conflicts
            for ref_id in overlap:
                issues.append(CrossrefIssue(
                    entry_id=entry_id,
                    severity="warning",
                    field="relationships",
                    description=f"'{ref_id}' appears in both related and conflicts",
                    suggestion=f"Remove from one of the lists",
                ))

            # --- Check bidirectionality of related ---
            for ref_id in related:
                if ref_id in self._entries:
                    other_rels = (
                        self._entries[ref_id]["data"]
                        .get("library", {})
                        .get("relationships", {})
                    )
                    other_related = set(other_rels.get("related", []) or [])
                    if entry_id not in other_related:
                        issues.append(CrossrefIssue(
                            entry_id=entry_id,
                            severity="warning",
                            field="relationships.related",
                            description=f"'{ref_id}' lists this as related, but reverse is missing",
                            suggestion=f"Add '{entry_id}' to '{ref_id}' relationships.related",
                        ))

            # --- Check bidirectionality of conflicts ---
            for ref_id in conflicts:
                if ref_id in self._entries:
                    other_rels = (
                        self._entries[ref_id]["data"]
                        .get("library", {})
                        .get("relationships", {})
                    )
                    other_conflicts = set(other_rels.get("conflicts", []) or [])
                    if entry_id not in other_conflicts:
                        issues.append(CrossrefIssue(
                            entry_id=entry_id,
                            severity="warning",
                            field="relationships.conflicts",
                            description=f"'{ref_id}' lists this as conflicts, but reverse is missing",
                            suggestion=f"Add '{entry_id}' to '{ref_id}' relationships.conflicts",
                        ))

            # --- Check extensions directionality ---
            for ref_id in extensions:
                if ref_id in self._entries:
                    other_rels = (
                        self._entries[ref_id]["data"]
                        .get("library", {})
                        .get("relationships", {})
                    )
                    other_ext = set(other_rels.get("extensions", []) or [])
                    if entry_id not in other_ext:
                        # extensions is directional, so this is just a suggestion
                        issues.append(CrossrefIssue(
                            entry_id=entry_id,
                            severity="suggestion",
                            field="relationships.extensions",
                            description=f"'{ref_id}' is listed as extension, verify hierarchy direction",
                            suggestion="Ensure '{ref_id}' is the parent and '{entry_id}' is the specialization",
                        ))

        has_errors = any(i.severity == "error" for i in issues)
        return CrossrefGateResult(passed=not has_errors, issues=issues)

    def fix_bidirectional(self) -> CrossrefGateResult:
        """Validate and auto-fix missing reverse relationships.

        Writes fixes back to the YAML files on disk.
        """
        validate_result = self.validate()
        fixes: list[str] = []
        fix_issues: list[CrossrefIssue] = []

        for issue in validate_result.issues:
            if issue.severity != "warning":
                continue
            if "reverse is missing" not in issue.description:
                continue

            # Parse the issue to extract direction
            entry_id = issue.entry_id
            field_name = issue.field.split(".")[-1]  # related or conflicts

            # Find what ref_id is missing the reverse
            desc = issue.description
            # "'X' lists this as related, but reverse is missing"
            # We need to find X and add entry_id to X's list
            for other_id, other_info in self._entries.items():
                other_rels = (
                    other_info["data"]
                    .get("library", {})
                    .get("relationships", {})
                )
                other_list = other_rels.get(field_name, []) or []
                # Check if this entry lists the other, but other doesn't list back
                this_rels = (
                    self._entries[entry_id]["data"]
                    .get("library", {})
                    .get("relationships", {})
                )
                this_list = this_rels.get(field_name, []) or []

                if other_id in this_list and entry_id not in other_list:
                    # Auto-fix: add entry_id to other's list
                    if not other_list:
                        other_info["data"]["library"]["relationships"][field_name] = [entry_id]
                    else:
                        other_info["data"]["library"]["relationships"][field_name].append(entry_id)

                    fix_msg = (
                        f"Auto-fixed: added '{entry_id}' to "
                        f"'{other_id}.relationships.{field_name}'"
                    )
                    fixes.append(fix_msg)
                    fix_issues.append(CrossrefIssue(
                        entry_id=other_id,
                        severity="auto_fixed",
                        field=f"relationships.{field_name}",
                        description=fix_msg,
                    ))

        # Write fixed entries back to disk
        for entry_id, entry_info in self._entries.items():
            if entry_info["path"] and entry_info["path"].exists():
                with open(entry_info["path"], "w", encoding="utf-8") as f:
                    yaml.dump(
                        entry_info["data"],
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                        sort_keys=False,
                    )

        return CrossrefGateResult(
            passed=True,
            issues=[i for i in validate_result.issues if i.severity != "warning"] + fix_issues,
            auto_fixes_applied=fixes,
        )
