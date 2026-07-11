"""Cache manager for LLM-sourced knowledge entries.

Ensures determinism: once an LLM response is cached, subsequent identical
queries return the cached result without calling the LLM.

Cache files are YAML and stored version-controlled so the team shares
the same resolved knowledge.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .schemas import KnowledgeEntry, KnowledgeRequest


class CacheManager:
    """Manages LLM knowledge cache: read, write, invalidate, index."""

    def __init__(self, cache_dir: str | Path | None = None):
        if cache_dir is None:
            cache_dir = Path(__file__).resolve().parent.parent.parent / "knowledge" / "providers" / "llm_cache"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._index: dict[str, dict] = {}
        self._load_index()

    def _compute_key(self, request: KnowledgeRequest) -> str:
        """Compute a deterministic cache key from a request."""
        payload = json.dumps({
            "domain": request.domain,
            "query": request.query,
            "context": request.context,
        }, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def _load_index(self) -> None:
        """Load the cache index from disk."""
        index_path = self.cache_dir / "index.yaml"
        if index_path.exists():
            try:
                data = yaml.safe_load(index_path.read_text(encoding="utf-8-sig"))
                if isinstance(data, dict) and "entries" in data:
                    self._index = data["entries"]
            except Exception:
                self._index = {}

    def _save_index(self) -> None:
        """Persist the cache index to disk."""
        index_path = self.cache_dir / "index.yaml"
        index_path.write_text(
            yaml.safe_dump({"version": 1, "entries": self._index}, allow_unicode=True),
            encoding="utf-8",
        )

    def get(self, request: KnowledgeRequest) -> list[KnowledgeEntry] | None:
        """Retrieve cached entries for a request. Returns None on miss."""
        key = self._compute_key(request)
        if key not in self._index:
            return None
        entry_path = self.cache_dir / self._index[key]["file"]
        if not entry_path.exists():
            # Index entry exists but file is missing — treat as miss
            self._index.pop(key, None)
            return None
        try:
            data = yaml.safe_load(entry_path.read_text(encoding="utf-8-sig"))
            entries_data = data.get("entries", [])
            return [_dict_to_entry(e) for e in entries_data]
        except Exception:
            return None

    def put(self, request: KnowledgeRequest, entries: list[KnowledgeEntry],
            model: str = "unknown", model_version: str = "") -> None:
        """Write entries to cache for a request."""
        key = self._compute_key(request)
        filename = f"{key}.yaml"
        entry_path = self.cache_dir / filename

        cache_data = {
            "cache_key": key,
            "domain": request.domain,
            "query": request.query,
            "model": model,
            "model_version": model_version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entries": [_entry_to_dict(e) for e in entries],
        }
        # Atomic write
        tmp = entry_path.with_suffix(".tmp")
        tmp.write_text(yaml.safe_dump(cache_data, allow_unicode=True), encoding="utf-8")
        tmp.replace(entry_path)

        self._index[key] = {
            "domain": request.domain,
            "file": filename,
            "model": model,
            "created": datetime.now(timezone.utc).isoformat(),
        }
        self._save_index()

    def invalidate(self, request: KnowledgeRequest) -> bool:
        """Remove a single cache entry. Returns True if found."""
        key = self._compute_key(request)
        if key not in self._index:
            return False
        entry_path = self.cache_dir / self._index[key]["file"]
        entry_path.unlink(missing_ok=True)
        self._index.pop(key, None)
        self._save_index()
        return True

    def invalidate_all(self) -> int:
        """Clear the entire cache. Returns number of entries removed."""
        count = len(self._index)
        for entry_info in self._index.values():
            (self.cache_dir / entry_info["file"]).unlink(missing_ok=True)
        self._index.clear()
        self._save_index()
        return count

    def stats(self) -> dict:
        """Return cache statistics."""
        return {
            "total_entries": len(self._index),
            "domains": list({v["domain"] for v in self._index.values()}),
        }


def _entry_to_dict(entry: KnowledgeEntry) -> dict:
    return {
        "entry_id": entry.entry_id,
        "domain": entry.domain,
        "description": entry.description,
        "rules": entry.rules,
        "examples": entry.examples,
        "constraints": entry.constraints,
        "keywords": entry.keywords,
        "confidence": entry.confidence,
        "source": entry.source,
        "source_detail": entry.source_detail,
    }


def _dict_to_entry(data: dict) -> KnowledgeEntry:
    return KnowledgeEntry(
        entry_id=data.get("entry_id", ""),
        domain=data.get("domain", ""),
        description=data.get("description", ""),
        rules=data.get("rules", []),
        examples=data.get("examples", []),
        constraints=data.get("constraints", {}),
        keywords=data.get("keywords", []),
        confidence=data.get("confidence", 1.0),
        source=data.get("source", ""),
        source_detail=data.get("source_detail", {}),
    )
