"""Knowledge Resolution module.

Provides the Knowledge Resolution Architecture (ADR-008) implementation:
- KnowledgeRequest / KnowledgeEntry / ResolvedKnowledge schemas
- KnowledgeProvider interface + LocalRulesProvider + LLMProvider (stub)
- CacheManager for LLM response caching
- KnowledgeResolver pipeline (multi-provider routing + merge/rank)
"""

from .schemas import KnowledgeRequest, KnowledgeEntry, ResolvedKnowledge
from .providers import KnowledgeProvider, LocalRulesProvider, LLMProvider
from .cache import CacheManager
from .resolver import KnowledgeResolver

__all__ = [
    "KnowledgeRequest",
    "KnowledgeEntry",
    "ResolvedKnowledge",
    "KnowledgeProvider",
    "LocalRulesProvider",
    "LLMProvider",
    "CacheManager",
    "KnowledgeResolver",
]
