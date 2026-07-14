"""Gate 4 — Spotcheck Report: Human spot-check report generation.

Generates Markdown reports for manual review, sampling 2-3 entries
per category and displaying full YAML + Gate 2 issues alongside.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class SpotcheckEntry:
    """An entry selected for spot-check."""

    entry_id: str
    file_path: Path
    content: dict
    gate2_issues: list[dict] = field(default_factory=list)


@dataclass
class SpotcheckReport:
    """Generated spot-check report."""

    category: str
    entries: list[SpotcheckEntry] = field(default_factory=list)
    pass_rate: float = 0.0


class SpotcheckReportGenerator:
    """Generate human-readable spot-check reports."""

    def __init__(
        self,
        output_dir: Path | str | None = None,
        sample_count: int = 3,
        seed: int | None = None,
    ):
        if output_dir:
            self._output_dir = Path(output_dir)
        else:
            self._output_dir = Path(__file__).resolve().parents[1] / "reports"
        self._sample_count = sample_count
        self._rng = random.Random(seed)

    def generate(
        self,
        category: str,
        dir_path: Path,
        gate2_issues: dict[str, list[dict]] | None = None,
    ) -> SpotcheckReport:
        """Generate a spot-check report for a category.

        Args:
            category: Category name (for report title).
            dir_path: Path to the category directory with YAML entries.
            gate2_issues: Optional dict mapping entry_id -> list of issues
                         from Gate 2 review.

        Returns:
            SpotcheckReport with sampled entries.
        """
        yaml_files = sorted(dir_path.glob("*.yaml"))
        if not yaml_files:
            return SpotcheckReport(category=category)

        # Sample entries
        sampled = self._rng.sample(
            yaml_files,
            min(self._sample_count, len(yaml_files)),
        )

        entries: list[SpotcheckEntry] = []
        for fpath in sampled:
            with open(fpath, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            entry_id = data.get("library", {}).get("metadata", {}).get("id", fpath.stem)
            issues = (gate2_issues or {}).get(entry_id, [])

            entries.append(SpotcheckEntry(
                entry_id=entry_id,
                file_path=fpath,
                content=data,
                gate2_issues=issues,
            ))

        # Calculate pass rate (no error-severity issues)
        total = len(entries)
        passed = sum(
            1 for e in entries
            if not any(i.get("severity") == "error" for i in e.gate2_issues)
        )
        pass_rate = passed / total if total > 0 else 0.0

        report = SpotcheckReport(
            category=category,
            entries=entries,
            pass_rate=pass_rate,
        )

        # Write report to disk
        self._write_report(report)

        return report

    def _write_report(self, report: SpotcheckReport) -> Path:
        """Write the spot-check report to a Markdown file."""
        self._output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self._output_dir / f"{report.category}_spotcheck.md"

        lines: list[str] = []
        lines.append(f"# Spot-Check Report: {report.category}")
        lines.append("")
        lines.append(f"**Category:** {report.category}")
        lines.append(f"**Entries sampled:** {len(report.entries)}")
        lines.append(f"**Pass rate:** {report.pass_rate:.0%}")
        lines.append(f"**Status:** {'✅ PASSED' if report.pass_rate >= 0.9 else '❌ FAILED'}")
        lines.append("")
        lines.append("---")
        lines.append("")

        for idx, entry in enumerate(report.entries, 1):
            lines.append(f"## {idx}. {entry.entry_id}")
            lines.append("")
            lines.append(f"**File:** `{entry.file_path}`")
            lines.append("")

            # Gate 2 issues summary
            if entry.gate2_issues:
                lines.append("### Gate 2 Issues")
                lines.append("")
                for issue in entry.gate2_issues:
                    severity = issue.get("severity", "suggestion")
                    icon = {"error": "🔴", "warning": "🟡", "suggestion": "🔵"}.get(severity, "⚪")
                    lines.append(
                        f"- {icon} **[{severity.upper()}]** `{issue.get('field', '')}`: "
                        f"{issue.get('description', '')}"
                    )
                    if issue.get("suggestion"):
                        lines.append(f"  - 💡 {issue['suggestion']}")
                lines.append("")

            # Full YAML content
            lines.append("### Full Entry Content")
            lines.append("")
            lines.append("```yaml")
            lines.append(yaml.dump(entry.content, default_flow_style=False, allow_unicode=True, sort_keys=False))
            lines.append("```")
            lines.append("")
            lines.append("---")
            lines.append("")

        # Review checklist
        lines.append("## Review Checklist")
        lines.append("")
        lines.append("For each entry above, verify:")
        lines.append("")
        lines.append("- [ ] Technical claims are factually correct")
        lines.append("- [ ] Emotional effects match film theory")
        lines.append("- [ ] Genre associations are reasonable")
        lines.append("- [ ] Engine guidance is actionable")
        lines.append("- [ ] Techniques are practical for a working DP")
        lines.append("- [ ] Constraints reflect real production limitations")
        lines.append("")
        lines.append("**Pass criteria:** ≥ 90% of sampled entries have no factual errors.")
        lines.append("")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return output_path
