"""Knowledge Provider interface and implementations.

Providers are swappable knowledge sources. Each implements resolve() and
returns KnowledgeEntry lists. The LocalRulesProvider wraps existing library
YAML files. LLMProvider will be added when GPT is back.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml

from .schemas import KnowledgeEntry, KnowledgeRequest


class KnowledgeProvider(ABC):
    """Interface every knowledge provider must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique provider identifier."""

    @property
    @abstractmethod
    def is_deterministic(self) -> bool:
        """Whether this provider always returns the same result for the same input."""

    @abstractmethod
    def resolve(self, request: KnowledgeRequest) -> list[KnowledgeEntry]:
        """Resolve a knowledge request and return matching entries."""

    def can_handle(self, domain: str) -> bool:
        """Whether this provider can handle the given domain."""
        return True


class LocalRulesProvider(KnowledgeProvider):
    """Provider backed by local YAML rule files.

    Reads entries from libraries/ directory (existing structure).
    When libraries/ is migrated to knowledge/providers/local_rules/,
    simply point the rules_dir there.
    """

    name = "local_rules"
    is_deterministic = True

    def __init__(self, rules_dir: str | Path | None = None):
        if rules_dir is None:
            # Default: project-root knowledge/providers/local_rules/ directory
            rules_dir = Path(__file__).resolve().parent.parent.parent / "knowledge" / "providers" / "local_rules"
        self.rules_dir = Path(rules_dir)
        self._entries: list[KnowledgeEntry] = []
        self._by_domain: dict[str, list[KnowledgeEntry]] = {}
        self._load_all()

    def _load_all(self) -> None:
        """Load all YAML entries from the rules directory."""
        if not self.rules_dir.exists():
            return
        entry_list: list[KnowledgeEntry] = []
        for yaml_file in sorted(self.rules_dir.rglob("*.yaml")):
            if yaml_file.stem.startswith("REF_"):
                continue
            entry = self._parse_entry(yaml_file)
            if entry:
                entry_list.append(entry)
        self._entries = entry_list
        self._by_domain.clear()
        for e in entry_list:
            self._by_domain.setdefault(e.domain, []).append(e)

    def _parse_entry(self, yaml_file: Path) -> KnowledgeEntry | None:
        """Parse a single YAML file into a KnowledgeEntry."""
        try:
            data = yaml.safe_load(yaml_file.read_text(encoding="utf-8-sig"))
            if not isinstance(data, dict):
                return None
            # Handle both old library format and new knowledge entry format
            lib = data.get("library", data)
            if not isinstance(lib, dict):
                return None

            meta = lib.get("metadata", {})
            if not isinstance(meta, dict) or not meta.get("id"):
                return None

            knowledge = lib.get("knowledge", {})
            if isinstance(knowledge, dict):
                description = knowledge.get("concept", knowledge.get("description", ""))
                rules = knowledge.get("principles", knowledge.get("rules", []))
                if isinstance(rules, str):
                    rules = [rules]
            else:
                description = ""
                rules = []

            applicability = lib.get("applicability", {})
            if isinstance(applicability, dict):
                constraints = dict(applicability)
                keywords = applicability.get("keywords", applicability.get("emotions", []))
            else:
                constraints = {}
                keywords = []

            # Determine domain from category or file path
            category = lib.get("category", "")
            if not category:
                # Infer from path: libraries/composition/entries/xxx.yaml -> composition
                parts = yaml_file.relative_to(self.rules_dir).parts
                category = parts[0] if len(parts) > 1 else "unknown"

            return KnowledgeEntry(
                entry_id=meta.get("id", yaml_file.stem),
                domain=category,
                description=description,
                rules=rules,
                examples=lib.get("examples", {}).get("successful", []),
                constraints=constraints,
                keywords=keywords if isinstance(keywords, list) else [keywords],
                confidence=0.95,
                source="local_rules",
                source_detail={"path": str(yaml_file.relative_to(self.rules_dir))},
            )
        except Exception:
            return None

    def resolve(self, request: KnowledgeRequest) -> list[KnowledgeEntry]:
        """Resolve by domain + keyword/emotion matching."""
        pool = self._by_domain.get(request.domain, self._entries)
        results: list[KnowledgeEntry] = []

        query_lower = request.query.lower()
        context = request.context
        emotion = context.get("emotion", "")
        scene_type = context.get("scene_type", "")

        for entry in pool:
            score = 0.0
            # Domain match
            if entry.domain == request.domain:
                score += 0.3

            # Keyword match from query
            kw_match = any(kw.lower() in query_lower for kw in entry.keywords)
            if kw_match:
                score += 0.3

            # Context field match
            if emotion and emotion in entry.constraints.get("emotions", entry.constraints.get("emotion", [])):
                score += 0.2
            if scene_type and scene_type in entry.constraints.get("scene_types", entry.constraints.get("scene_type", [])):
                score += 0.2

            if score > 0:
                results.append(entry)

        # Sort by score, apply max_results
        max_results = request.constraints.get("max_results", 5)
        results.sort(key=lambda e: e.confidence, reverse=True)
        return results[:max_results]

    def can_handle(self, domain: str) -> bool:
        # Local rules always try — resolve() falls back to all entries
        # when the domain is not explicitly indexed.
        return True


class LLMProvider(KnowledgeProvider):
    """Provider that queries an LLM and caches results.

    Placeholder — the real implementation will:
    1. Check cache first (via CacheManager)
    2. If miss: call LLM with domain-specific system prompt
    3. Parse structured YAML response into KnowledgeEntry list
    4. Write cache entry

    This provider requires an LLM client (OpenAI, Anthropic, etc.) and
    will be implemented when GPT is available.
    """

    name = "cached_llm"
    is_deterministic = True  # via caching

    def __init__(self, cache_manager: Any | None = None):
        self._cache = cache_manager

    def resolve(self, request: KnowledgeRequest) -> list[KnowledgeEntry]:
        """Stub — returns empty list until LLM client is wired in."""
        if self._cache:
            cached = self._cache.get(request)
            if cached:
                return cached
        # TODO: call LLM, parse response, cache result
        return []

    def can_handle(self, domain: str) -> bool:
        return True
