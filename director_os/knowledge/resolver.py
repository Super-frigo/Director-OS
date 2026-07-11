"""Knowledge Resolution Pipeline.

Routes knowledge requests to available providers, merges results,
ranks by relevance, and returns deterministic ResolvedKnowledge.

This is the central component of the Knowledge Resolution Architecture (ADR-008).
"""

from __future__ import annotations

from .providers import KnowledgeProvider, LocalRulesProvider, LLMProvider
from .cache import CacheManager
from .schemas import KnowledgeRequest, KnowledgeEntry, ResolvedKnowledge


class KnowledgeResolver:
    """Orchestrates knowledge resolution across multiple providers.

    Usage:
        resolver = KnowledgeResolver()
        resolver.register(LocalRulesProvider())
        resolver.register(LLMProvider(cache_manager))

        result = resolver.resolve(KnowledgeRequest(
            domain="composition",
            query="How to frame loneliness?",
            context={"emotion": "loneliness"},
        ))
    """

    def __init__(self):
        self._providers: list[KnowledgeProvider] = []
        self._cache: CacheManager | None = None

    def register(self, provider: KnowledgeProvider) -> None:
        """Register a knowledge provider. Order = priority."""
        self._providers.append(provider)

    def set_cache(self, cache: CacheManager) -> None:
        """Attach a cache manager for LLM responses."""
        self._cache = cache

    def resolve(self, request: KnowledgeRequest) -> ResolvedKnowledge:
        """Execute the full resolution pipeline.

        1. Query providers in registration order
        2. Merge and deduplicate results
        3. Rank by relevance score
        4. Return ResolvedKnowledge
        """
        all_entries: list[KnowledgeEntry] = []
        stats = {
            "providers_queried": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_entries": 0,
        }
        warnings: list[str] = []

        # Check cache first for LLM-sourced entries
        if self._cache and request.allow_llm:
            cached = self._cache.get(request)
            if cached:
                stats["cache_hits"] += 1
                all_entries.extend(cached)
            else:
                stats["cache_misses"] += 1

        # Query providers (skip LLM if cache hit)
        cache_hit = stats["cache_hits"] > 0
        for provider in self._providers:
            if not provider.can_handle(request.domain):
                continue
            # Skip LLM provider if we already have cached results
            if isinstance(provider, LLMProvider) and cache_hit:
                continue
            try:
                entries = provider.resolve(request)
                all_entries.extend(entries)
                stats["providers_queried"] += 1
            except Exception as e:
                warnings.append(f"Provider '{provider.name}' failed: {e}")

        # If no cached results but LLM provider returned entries, cache them
        if not cache_hit and self._cache:
            llm_entries = [e for e in all_entries if e.source == "cached_llm"]
            if llm_entries:
                self._cache.put(request, llm_entries)

        # Deduplicate and rank
        merged = self._merge_and_rank(all_entries, request)

        stats["total_entries"] = len(merged)

        return ResolvedKnowledge(
            request_id=request.request_id,
            entries=merged,
            warnings=warnings,
            stats=stats,
        )

    def _merge_and_rank(self, entries: list[KnowledgeEntry],
                        request: KnowledgeRequest) -> list[KnowledgeEntry]:
        """Deduplicate entries and rank by relevance.

        Deduplication: entries with the same entry_id are merged (keep
        the one with highest confidence). If entry_ids differ but content
        is similar, prefer local_rules over cached_llm.

        Ranking: sort by confidence descending, then by source priority
        (local_rules > cached_llm).
        """
        if not entries:
            return []

        # Phase 1: simple dedup by entry_id
        seen: dict[str, KnowledgeEntry] = {}
        for e in entries:
            if e.entry_id not in seen:
                seen[e.entry_id] = e
            elif e.confidence > seen[e.entry_id].confidence:
                seen[e.entry_id] = e
            elif e.confidence == seen[e.entry_id].confidence:
                # Prefer local_rules at same confidence
                if e.source == "local_rules":
                    seen[e.entry_id] = e

        deduped = list(seen.values())

        # Phase 2: rank by confidence (desc), then source priority
        source_priority = {"local_rules": 0, "cached_llm": 1}
        deduped.sort(key=lambda e: (
            -e.confidence,
            source_priority.get(e.source, 99),
        ))

        # Phase 3: apply max_results
        max_results = request.constraints.get("max_results", 5)
        return deduped[:max_results]

    @property
    def provider_count(self) -> int:
        return len(self._providers)
