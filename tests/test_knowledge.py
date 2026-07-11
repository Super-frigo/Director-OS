"""Tests for the Knowledge Resolution module (ADR-008)."""

import tempfile
from pathlib import Path

import pytest

from director_os.knowledge import (
    KnowledgeRequest,
    KnowledgeEntry,
    ResolvedKnowledge,
    KnowledgeProvider,
    LocalRulesProvider,
    LLMProvider,
    CacheManager,
    KnowledgeResolver,
)


# ============================================================================
# Schemas
# ============================================================================

def test_knowledge_request_defaults():
    req = KnowledgeRequest()
    assert req.domain == ""
    assert req.constraints["max_results"] == 5
    assert req.timestamp


def test_knowledge_entry_defaults():
    entry = KnowledgeEntry()
    assert entry.confidence == 1.0
    assert entry.rules == []


def test_resolved_knowledge_defaults():
    rk = ResolvedKnowledge()
    assert rk.entries == []
    assert rk.stats["total_entries"] == 0


# ============================================================================
# LocalRulesProvider
# ============================================================================

def test_local_rules_loads_entries():
    """Provider should load entries from knowledge/providers/local_rules/."""
    p = LocalRulesProvider()
    assert len(p._entries) > 0
    assert "composition" in p._by_domain
    assert "lighting" in p._by_domain


def test_local_rules_resolve_by_domain():
    p = LocalRulesProvider()
    req = KnowledgeRequest(domain="composition", query="")
    result = p.resolve(req)
    assert len(result) > 0
    assert all(e.domain == "composition" for e in result)


def test_local_rules_resolve_with_emotion():
    p = LocalRulesProvider()
    req = KnowledgeRequest(
        domain="composition",
        query="loneliness isolation",
        context={"emotion": "loneliness"},
    )
    result = p.resolve(req)
    # Should find at least negative_space or frame_within_frame
    ids = {e.entry_id for e in result}
    assert ids, "Should match at least one composition entry for loneliness"


def test_local_rules_deterministic():
    p = LocalRulesProvider()
    req = KnowledgeRequest(domain="lighting", query="noir")
    r1 = p.resolve(req)
    r2 = p.resolve(req)
    assert len(r1) == len(r2)
    assert [e.entry_id for e in r1] == [e.entry_id for e in r2]


def test_local_rules_can_handle():
    p = LocalRulesProvider()
    assert p.can_handle("composition")
    assert p.can_handle("nonexistent")  # falls back to all entries


# ============================================================================
# LLMProvider (stub)
# ============================================================================

def test_llm_provider_requires_client():
    with pytest.raises(ValueError):
        LLMProvider()


def test_llm_provider_with_cache_hit():
    from unittest.mock import MagicMock
    cm = CacheManager(cache_dir=tempfile.mkdtemp())
    entry = KnowledgeEntry(entry_id="c1", domain="test", description="cached", source="cached_llm")
    req = KnowledgeRequest(domain="test", query="cached query")
    cm.put(req, [entry], model="test")

    mock_client = MagicMock()
    mock_client.model_name = "test"
    p = LLMProvider(client=mock_client, cache_manager=cm)
    result = p.resolve(req)
    assert len(result) == 1
    assert result[0].entry_id == "c1"


# ============================================================================
# CacheManager
# ============================================================================

@pytest.fixture
def cache():
    d = tempfile.mkdtemp()
    cm = CacheManager(cache_dir=d)
    yield cm
    import shutil
    shutil.rmtree(d, ignore_errors=True)


def test_cache_put_and_get(cache):
    req = KnowledgeRequest(domain="composition", query="loneliness")
    entry = KnowledgeEntry(entry_id="e1", domain="composition", description="test")
    cache.put(req, [entry], model="gpt-5")

    result = cache.get(req)
    assert result is not None
    assert result[0].entry_id == "e1"


def test_cache_miss(cache):
    req = KnowledgeRequest(domain="composition", query="nonexistent query")
    assert cache.get(req) is None


def test_cache_invalidate(cache):
    req = KnowledgeRequest(domain="test", query="temp")
    cache.put(req, [KnowledgeEntry(entry_id="x")], model="test")
    assert cache.get(req) is not None
    assert cache.invalidate(req)
    assert cache.get(req) is None


def test_cache_invalidate_all(cache):
    for i in range(3):
        req = KnowledgeRequest(domain="test", query=f"query_{i}")
        cache.put(req, [KnowledgeEntry(entry_id=f"e{i}")], model="test")
    assert cache.stats()["total_entries"] == 3
    removed = cache.invalidate_all()
    assert removed == 3
    assert cache.stats()["total_entries"] == 0


def test_cache_deterministic_key():
    """Same request should produce the same cache key."""
    cm = CacheManager(cache_dir=tempfile.mkdtemp())
    req1 = KnowledgeRequest(domain="test", query="hello", context={"a": 1})
    req2 = KnowledgeRequest(domain="test", query="hello", context={"a": 1})
    assert cm._compute_key(req1) == cm._compute_key(req2)


def test_cache_different_key():
    cm = CacheManager(cache_dir=tempfile.mkdtemp())
    req1 = KnowledgeRequest(domain="test", query="hello")
    req2 = KnowledgeRequest(domain="test", query="world")
    assert cm._compute_key(req1) != cm._compute_key(req2)


# ============================================================================
# KnowledgeResolver
# ============================================================================

def test_resolver_with_local_rules():
    r = KnowledgeResolver()
    r.register(LocalRulesProvider())
    req = KnowledgeRequest(domain="composition", query="loneliness")
    result = r.resolve(req)
    assert len(result.entries) > 0
    assert result.stats["providers_queried"] == 1


def test_resolver_deduplicates():
    """Same entry_id from two providers should be deduplicated."""
    r = KnowledgeResolver()

    class DupProvider(KnowledgeProvider):
        name = "dup_test"
        is_deterministic = True

        def resolve(self, request):
            return [
                KnowledgeEntry(entry_id="same_id", domain="test",
                               description="from dup", confidence=0.5, source="dup_test"),
            ]

    r.register(DupProvider())
    r.register(DupProvider())  # register twice
    req = KnowledgeRequest(domain="test", query="")
    result = r.resolve(req)
    # Both providers return same entry_id → dedup should produce 1
    assert len(result.entries) == 1


def test_resolver_ranks_by_confidence():
    r = KnowledgeResolver()

    class RankProvider(KnowledgeProvider):
        name = "rank_test"
        is_deterministic = True

        def resolve(self, request):
            return [
                KnowledgeEntry(entry_id="low", confidence=0.3, source="rank_test"),
                KnowledgeEntry(entry_id="high", confidence=0.9, source="rank_test"),
                KnowledgeEntry(entry_id="mid", confidence=0.6, source="rank_test"),
            ]

    r.register(RankProvider())
    req = KnowledgeRequest(domain="test", query="")
    result = r.resolve(req)
    confidences = [e.confidence for e in result.entries]
    assert confidences == sorted(confidences, reverse=True)


def test_resolver_respects_max_results():
    r = KnowledgeResolver()

    class ManyProvider(KnowledgeProvider):
        name = "many"
        is_deterministic = True

        def resolve(self, request):
            return [KnowledgeEntry(entry_id=f"e{i}", source="many") for i in range(10)]

    r.register(ManyProvider())
    req = KnowledgeRequest(domain="test", query="", constraints={"max_results": 3})
    result = r.resolve(req)
    assert len(result.entries) == 3


def test_resolver_prefers_local_over_llm():
    """At same confidence, local_rules should rank above cached_llm."""
    r = KnowledgeResolver()

    class FakeLLM(KnowledgeProvider):
        name = "cached_llm"
        is_deterministic = True

        def resolve(self, request):
            return [KnowledgeEntry(entry_id="e1", confidence=0.8, source="cached_llm")]

    class FakeLocal(KnowledgeProvider):
        name = "local_rules"
        is_deterministic = True

        def resolve(self, request):
            return [KnowledgeEntry(entry_id="e1", confidence=0.8, source="local_rules")]

    r.register(FakeLLM())
    r.register(FakeLocal())
    req = KnowledgeRequest(domain="test", query="")
    result = r.resolve(req)
    assert len(result.entries) == 1
    assert result.entries[0].source == "local_rules"


# ============================================================================
# Engine Pipeline integration
# ============================================================================

def test_engine_pipeline_with_resolver():
    """EnginePipeline should work with KnowledgeResolver wired in."""
    from director_os.engine.pipeline import EnginePipeline, EngineInput
    from director_os.loader import load_project

    resolver = KnowledgeResolver()
    resolver.register(LocalRulesProvider())

    project = load_project("projects/the_hanging.md")
    inp = EngineInput(project=project, resolver=resolver)
    pipeline = EnginePipeline()
    intent = pipeline.run(inp)

    assert intent.visual_direction["style"] == "Republican Noir"
    assert len(intent.character_direction) > 0


def test_engine_pipeline_without_resolver():
    """EnginePipeline should work without resolver (legacy path)."""
    from director_os.engine.pipeline import EnginePipeline, EngineInput
    from director_os.loader import load_project

    project = load_project("projects/the_hanging.md")
    inp = EngineInput(project=project)  # no resolver
    pipeline = EnginePipeline()
    intent = pipeline.run(inp)

    assert intent.visual_direction["style"] == "Republican Noir"
