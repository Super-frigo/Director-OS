"""Gate 2 — Consistency Gate: LLM-based internal consistency review.

Runs three rounds of LLM review (accuracy, completeness, practicality)
against generated knowledge entries. Aggregates issues and triggers
re-generation for severity=error.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from director_os.knowledge.llm_client import LLMClient, OpenAIClient


@dataclass
class ConsistencyIssue:
    """A single consistency review issue."""

    entry_id: str
    severity: str  # error | warning | suggestion
    field: str
    description: str
    suggestion: str = ""
    review_round: str = ""  # accuracy | completeness | practicality


@dataclass
class ConsistencyGateResult:
    """Result of consistency gate review."""

    passed: bool
    issues: list[ConsistencyIssue] = field(default_factory=list)
    entries_needing_regeneration: list[str] = field(default_factory=list)
    entries_needing_review: list[str] = field(default_factory=list)


class ConsistencyGate:
    """Gate 2: LLM-based internal consistency review.

    Runs three reviewer prompts against each batch of entries:
    1. Accuracy reviewer (skeptical professor)
    2. Completeness reviewer (curriculum designer)
    3. Practicality reviewer (working DP)
    """

    REVIEWER_PROMPTS = {
        "accuracy": "reviewer_accuracy.yaml",
        "completeness": "reviewer_completeness.yaml",
        "practicality": "reviewer_practicality.yaml",
    }

    def __init__(
        self,
        client: LLMClient | None = None,
        prompts_dir: Path | str | None = None,
    ):
        self._client = client
        if prompts_dir:
            self._prompts_dir = Path(prompts_dir)
        else:
            self._prompts_dir = Path(__file__).resolve().parents[1] / "prompts"

        self._prompt_cache: dict[str, dict] = {}

    def _ensure_client(self) -> LLMClient:
        """Create a default client if none provided."""
        if self._client is None:
            import os
            self._client = OpenAIClient(
                api_key=os.environ.get("OPENAI_API_KEY", ""),
                model=os.environ.get("BOOTSTRAP_MODEL", "deepseek-chat"),
                base_url=os.environ.get("OPENAI_BASE_URL", ""),
                temperature=0.3,
                max_tokens=4000,
            )
        return self._client

    def _load_prompt(self, name: str) -> dict:
        """Load a prompt template YAML."""
        if name not in self._prompt_cache:
            path = self._prompts_dir / name
            with open(path, "r", encoding="utf-8") as f:
                self._prompt_cache[name] = yaml.safe_load(f)
        return self._prompt_cache[name]

    def _render_prompt(self, template: str, variables: dict[str, str]) -> str:
        """Replace {{variable}} placeholders in a prompt template."""
        for key, value in variables.items():
            template = template.replace(f"{{{{{key}}}}}", value)
        return template

    def _extract_yaml_block(self, text: str) -> dict:
        """Extract YAML from LLM response, handling markdown fencing."""
        # Strip markdown code fences if present
        cleaned = re.sub(r"```ya?ml\s*", "", text)
        cleaned = re.sub(r"```\s*", "", cleaned)
        cleaned = cleaned.strip()

        try:
            result = yaml.safe_load(cleaned)
            return result if isinstance(result, dict) else {}
        except yaml.YAMLError:
            # Try to find YAML-like content
            return {"issues": []}

    def _run_single_review(
        self,
        review_type: str,
        entries_text: str,
    ) -> list[ConsistencyIssue]:
        """Run a single reviewer round."""
        client = self._ensure_client()
        prompt_file = self.REVIEWER_PROMPTS[review_type]
        prompt = self._load_prompt(prompt_file)

        system_msg = prompt["system"].strip()
        user_msg = self._render_prompt(
            prompt["user"].strip(),
            {"entries": entries_text},
        )

        response = client.chat(system_msg, user_msg)
        parsed = self._extract_yaml_block(response)

        issues: list[ConsistencyIssue] = []
        for item in parsed.get("issues", []):
            issues.append(ConsistencyIssue(
                entry_id=item.get("entry_id", ""),
                severity=item.get("severity", "suggestion"),
                field=item.get("field", ""),
                description=item.get("description", ""),
                suggestion=item.get("suggestion", ""),
                review_round=review_type,
            ))
        return issues

    def review_entries(
        self,
        entries: list[dict],
        review_types: list[str] | None = None,
    ) -> ConsistencyGateResult:
        """Run consistency review on a batch of entries.

        Args:
            entries: List of parsed YAML dicts (each with 'library' key).
            review_types: Which reviewers to run. Default: all three.

        Returns:
            ConsistencyGateResult with all issues and categorization.
        """
        if review_types is None:
            review_types = ["accuracy", "completeness", "practicality"]

        # Format entries for reviewer
        entries_text = self._format_entries(entries)

        all_issues: list[ConsistencyIssue] = []
        for review_type in review_types:
            round_issues = self._run_single_review(review_type, entries_text)
            all_issues.extend(round_issues)

        # Categorize
        error_ids: set[str] = set()
        warning_ids: set[str] = set()
        for issue in all_issues:
            if issue.severity == "error":
                error_ids.add(issue.entry_id)
            elif issue.severity == "warning":
                warning_ids.add(issue.entry_id)

        passed = len(error_ids) == 0
        return ConsistencyGateResult(
            passed=passed,
            issues=all_issues,
            entries_needing_regeneration=sorted(error_ids),
            entries_needing_review=sorted(warning_ids),
        )

    def review_file(self, file_path: Path) -> ConsistencyGateResult:
        """Review a single YAML file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return self.review_entries([data])

    def review_directory(self, dir_path: Path) -> ConsistencyGateResult:
        """Review all YAML files in a directory."""
        entries: list[dict] = []
        for yaml_file in sorted(dir_path.glob("*.yaml")):
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if data:
                entries.append(data)
        return self.review_entries(entries)

    @staticmethod
    def _format_entries(entries: list[dict]) -> str:
        """Format entries for LLM review prompt."""
        parts: list[str] = []
        for entry in entries:
            entry_id = entry.get("library", {}).get("metadata", {}).get("id", "<unknown>")
            parts.append(f"### {entry_id}")
            parts.append(yaml.dump(entry, default_flow_style=False, allow_unicode=True))
        return "\n".join(parts)
