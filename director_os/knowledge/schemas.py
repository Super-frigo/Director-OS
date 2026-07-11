"""Knowledge Resolution data models.

ADR-008 defines the Knowledge Resolution Architecture.
These schemas are the canonical data shapes for the resolution pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class KnowledgeRequest:
    """A request from Engine to the Resolution layer for domain knowledge."""

    request_id: str = ""
    domain: str = ""               # e.g. "composition", "lighting", "camera"
    query: str = ""                # natural-language question
    context: dict = field(default_factory=dict)  # structured context
    constraints: dict = field(default_factory=lambda: {
        "max_results": 5,
        "min_confidence": 0.0,
    })
    allow_llm: bool = True          # whether live LLM fallback is permitted
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class KnowledgeEntry:
    """A single resolved knowledge item with source traceability."""

    entry_id: str = ""
    domain: str = ""
    description: str = ""
    rules: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    constraints: dict = field(default_factory=dict)   # when this applies
    keywords: list[str] = field(default_factory=list)
    confidence: float = 1.0         # 0.0 - 1.0
    source: str = ""                # provider name
    source_detail: dict = field(default_factory=dict) # path, model, cache_key, etc.


@dataclass
class ResolvedKnowledge:
    """Result of a knowledge resolution request."""

    request_id: str = ""
    entries: list[KnowledgeEntry] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=lambda: {
        "providers_queried": 0,
        "cache_hits": 0,
        "cache_misses": 0,
        "total_entries": 0,
    })
