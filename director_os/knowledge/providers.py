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

    Reads entries from knowledge/providers/local_rules/ by default.
    Each domain (composition, lighting, camera, ...) is a subdirectory
    of YAML entries. REF_*.md files alongside are human reference docs
    and are skipped during loading.
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
                # Infer from path: local_rules/composition/xxx.yaml -> composition
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
                entry.confidence = score
                results.append(entry)

        # Sort by score, apply max_results
        max_results = request.constraints.get("max_results", 5)
        results.sort(key=lambda e: e.confidence, reverse=True)
        return results[:max_results]

    def can_handle(self, domain: str) -> bool:
        # Local rules always try -- resolve() falls back to all entries
        # when the domain is not explicitly indexed.
        return True


class LLMProvider(KnowledgeProvider):
    """Provider that queries an LLM and caches results for determinism.

    Flow:
    1. Check cache -> return if hit
    2. Load domain prompt template
    3. Format prompt with query context
    4. Call LLM via client
    5. Parse YAML response into KnowledgeEntry list
    6. Write cache -> return
    """

    name = "cached_llm"
    is_deterministic = True

    def __init__(self, client=None, cache_manager=None, prompts_path=None):
        if client is None:
            raise ValueError("LLMProvider requires a client (e.g. OpenAIClient)")
        self._client = client
        self._cache = cache_manager
        if prompts_path is None:
            prompts_path = (
                Path(__file__).resolve().parent.parent.parent
                / "knowledge" / "providers" / "llm_cache" / "domain_prompts.yaml"
            )
        self._prompts = self._load_prompts(Path(prompts_path))

    def _load_prompts(self, path):
        if not path.exists():
            return {}
        data = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
        if not isinstance(data, dict):
            return {}
        return data.get("domains", {})

    def resolve(self, request):
        if self._cache:
            cached = self._cache.get(request)
            if cached is not None:
                return cached
        domain_config = self._prompts.get(request.domain)
        if not domain_config:
            return []
        system_prompt = domain_config.get("system", "")
        user_template = domain_config.get("user_template", "{query}")
        user_prompt = self._format_template(user_template, request)
        try:
            raw = self._client.chat(system_prompt, user_prompt)
        except Exception:
            return []
        entries = self._parse_response(raw, request.domain)
        if self._cache and entries:
            try:
                self._cache.put(request, entries, model=self._client.model_name)
            except Exception:
                pass
        return entries

    def _format_template(self, template, request):
        ctx = request.context
        result = template
        result = result.replace("{query}", request.query)
        result = result.replace("{max_results}", str(request.constraints.get("max_results", 3)))
        for key, value in ctx.items():
            result = result.replace(f"{{context.{key}}}", str(value) if value else "")
        return result

    def _parse_response(self, raw, domain):
        yaml_str = self._extract_yaml(raw)
        if not yaml_str:
            return []
        try:
            data = yaml.safe_load(yaml_str)
        except yaml.YAMLError:
            return []
        if not isinstance(data, dict):
            return []
        entries_data = data.get("entries", [data])
        if not isinstance(entries_data, list):
            return []
        entries = []
        for item in entries_data:
            if not isinstance(item, dict):
                continue
            entry = KnowledgeEntry(
                entry_id=item.get("entry_id", f"llm_{domain}_{len(entries)}"),
                domain=item.get("domain", domain),
                description=item.get("description", ""),
                rules=item.get("rules", []),
                examples=item.get("examples", []),
                constraints=item.get("constraints", {}),
                keywords=item.get("keywords", []),
                confidence=0.80,
                source="cached_llm",
                source_detail={"model": self._client.model_name},
            )
            entries.append(entry)
        return entries

    def _extract_yaml(self, raw):
        raw = raw.strip()
        if "```yaml" in raw:
            start = raw.index("```yaml") + 7
            end = raw.index("```", start)
            return raw[start:end].strip()
        if "```" in raw:
            start = raw.index("```") + 3
            if "```" in raw[start:]:
                end = raw.index("```", start)
                return raw[start:end].strip()
        if "entries:" in raw:
            idx = raw.index("entries:")
            return raw[idx:]
        return raw

    def can_handle(self, domain):
        return domain in self._prompts
