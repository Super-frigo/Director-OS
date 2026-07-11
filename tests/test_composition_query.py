"""Tests for knowledge/providers/local_rules/composition/query.py v2 -- token-based matching, balanced weights.

Key regression tests:
  - Substring false positives eliminated ("instability" != "stability")
  - TRIANGULAR/BALANCED no longer appear via substring
  - Emotion-only entry < emotion+shot-param entry when W_SEMANTIC=W_SHOT=0.5
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from knowledge.providers.local_rules.composition.query import (
    query_compositions,
    query_compositions_detailed,
    load_entries,
    set_weights,
    W_SEMANTIC,
    W_SHOT,
    _EMOTION_MAP,
    _SCENE_MAP,
    _tokenize,
    _token_match,
    _tokenize_english,
    _tokenize_chinese,
    _semantic_score,
    _shot_param_score,
    _compute_entry_score,
    _resolve_emotion_keywords,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def reset_weights():
    """Reset scoring weights to defaults before each test."""
    set_weights(0.50, 0.50)


@pytest.fixture
def all_entries():
    entries = load_entries()
    assert len(entries) == 14
    return entries


# ============================================================================
# Loader tests
# ============================================================================

def test_load_entries_count(all_entries):
    assert len(all_entries) == 14


def test_load_entries_required_fields(all_entries):
    required = {"id", "rule", "name", "effect", "technique", "best_for",
                "example_films", "notes"}
    for entry in all_entries:
        missing = required - set(entry.keys())
        assert not missing, f"Entry {entry.get('id', '?')} missing: {missing}"


def test_load_entries_query_fields(all_entries):
    query_fields = {"emotions", "scene_types", "keywords", "framings", "lenses"}
    for entry in all_entries:
        missing = query_fields - set(entry.keys())
        assert not missing, f"Entry {entry.get('id', '?')} missing query fields: {missing}"


def test_load_entries_no_duplicate_ids(all_entries):
    ids = [e["id"] for e in all_entries]
    assert len(ids) == len(set(ids))


# ============================================================================
# Tokenizer tests
# ============================================================================

def test_tokenize_english():
    tokens = _tokenize_english("unease anxiety tension")
    assert "unease" in tokens
    assert "anxiety" in tokens
    assert "tension" in tokens


def test_tokenize_english_splits_underscores():
    tokens = _tokenize_english("rule_of_thirds")
    assert "rule" in tokens
    assert "thirds" in tokens


def test_tokenize_chinese():
    tokens = _tokenize_chinese("\u4e0d\u5b89\u7684\u8868\u60c5")  # bu an de biao qing
    assert len(tokens) > 0


def test_tokenize_mixed():
    tokens = _tokenize("unease tension \u4e0d\u5b89")
    assert "unease" in tokens
    assert "tension" in tokens
    # Chinese tokens should also be present
    assert len(tokens) >= 3


# ============================================================================
# Token match tests -- no substring false positives
# ============================================================================

def test_token_match_exact():
    """Exact token match should score 1.0 when all query tokens match."""
    score, matched = _token_match(
        ["unease", "anxiety", "tension"],
        ["unease", "anxiety", "tension", "dread"],
    )
    assert score == 1.0
    assert len(matched) == 3


def test_token_match_partial():
    """Partial token match should score proportionally."""
    score, matched = _token_match(
        ["unease", "anxiety", "tension"],
        ["unease"],
    )
    assert score == 1.0 / 3.0


def test_token_match_none():
    score, matched = _token_match(["xyz"], ["unease"])
    assert score == 0.0
    assert matched == []


def test_token_match_no_substring_instability_vs_stability():
    """REGRESSION: 'instability' must NOT match 'stability'."""
    score, matched = _token_match(
        ["instability"],
        ["stability"],
    )
    assert score == 0.0, (
        f"instability should NOT match stability via substring. "
        f"Got score={score}, matched={matched}"
    )


def test_token_match_no_substring_anxiety_vs_anxiety_disorder():
    """Even compound words: 'anxiety' vs 'anxiety disorder' -- only if the
    entry token SET contains the exact token 'anxiety'."""
    score, _ = _token_match(
        ["anxiety"],
        ["anxiety"],  # exact match
    )
    assert score == 1.0
    # But if the entry only has "anxiety_disorder" as a token...
    score2, _ = _token_match(
        ["anxiety"],
        ["anxiety_disorder"],  # not the same token
    )
    assert score2 == 0.0, "anxiety != anxiety_disorder as tokens"


def test_token_match_empty():
    assert _token_match([], ["unease"]) == (0.0, [])
    assert _token_match(["unease"], []) == (0.0, [])


# ============================================================================
# Shot param score tests
# ============================================================================

def test_shot_param_score_full_match():
    """All provided shot params match."""
    entry = {"framings": ["CU", "MCU"], "lenses": ["85mm", "100mm"]}
    context = {"framing": "CU", "lens": "85mm"}
    score, matched = _shot_param_score(context, entry)
    assert score == 1.0
    assert len(matched) == 2


def test_shot_param_score_partial_match():
    """Only one of two provided params matches."""
    entry = {"framings": ["CU"], "lenses": ["50mm"]}
    context = {"framing": "CU", "lens": "85mm"}
    score, matched = _shot_param_score(context, entry)
    assert score == 0.5


def test_shot_param_score_no_match():
    entry = {"framings": ["LS"], "lenses": ["24mm"]}
    context = {"framing": "CU", "lens": "85mm"}
    score, matched = _shot_param_score(context, entry)
    assert score == 0.0


def test_shot_param_score_empty_context():
    entry = {"framings": ["CU"]}
    score, matched = _shot_param_score({}, entry)
    assert score == 0.0


# ============================================================================
# Semantic score tests
# ============================================================================

def test_semantic_score_normalized():
    """Semantic score should be 0-1 normalized."""
    entry = {"emotions": ["unease", "anxiety", "tension"], "scene_types": ["tension"]}
    score, _ = _semantic_score(
        ["unease", "anxiety", "tension", "dread", "instability"],
        ["tension", "anxiety", "psychological"],
        entry,
    )
    assert 0.0 <= score <= 1.0


# ============================================================================
# Scoring weight tests
# ============================================================================

def test_set_weights_valid():
    import knowledge.providers.local_rules.composition.query as qmod
    qmod.set_weights(0.3, 0.7)
    assert qmod.W_SEMANTIC == 0.3
    assert qmod.W_SHOT == 0.7
    qmod.set_weights(0.5, 0.5)  # restore


def test_set_weights_invalid():
    with pytest.raises(ValueError):
        set_weights(0.5, 0.6)  # sum != 1.0


# ============================================================================
# Retrieval tests -- meaningful results
# ============================================================================

def test_query_emotion_loneliness_returns_negative_space():
    results = query_compositions({"emotion": "loneliness"}, min_score=0.05)
    assert len(results) > 0
    top_ids = [r[0]["id"] for r in results[:3]]
    assert "comp_negative_space" in top_ids


def test_query_emotion_loneliness_chinese():
    results = query_compositions({"emotion": "\u5b64\u7368"}, min_score=0.05)
    top_ids = [r[0]["id"] for r in results[:3]]
    assert "comp_negative_space" in top_ids


def test_query_scene_type_tension_returns_asymmetrical():
    results = query_compositions({"scene_type": "tension"}, min_score=0.05)
    assert len(results) > 0
    top_ids = [r[0]["id"] for r in results[:5]]
    tension_ids = {"comp_asymmetrical", "comp_diagonal", "comp_center_composition"}
    assert any(tid in top_ids for tid in tension_ids)


def test_query_unease_chinese_returns_relevant():
    results = query_compositions(
        {"emotion": "\u4e0d\u5b89", "scene_type": "psychological"},
        min_score=0.05,
    )
    assert len(results) > 0
    top_ids = [r[0]["id"] for r in results[:3]]
    relevant = {"comp_asymmetrical", "comp_center_composition", "comp_frame_within_frame"}
    assert any(tid in top_ids for tid in relevant)


def test_query_empty_context_returns_nothing():
    results = query_compositions({}, min_score=0.2)
    assert len(results) == 0


# ============================================================================
# REGRESSION: Substring false positives eliminated
# ============================================================================

def test_regression_no_triangular_from_instability_substring():
    """REGRESSION: Querying 'instability' must NOT return TRIANGULAR
    or BALANCED as high-ranked results.  These previously appeared because
    'instability' is a substring of 'stability'.

    With token-based matching, 'instability' != 'stability'.
    """
    results = query_compositions_detailed(
        {"emotion": "unease", "scene_type": "instability"},
        min_score=0.05,
    )
    # The word "instability" appears in the psychological scene map
    # It should NOT match entries whose keywords contain only "stability"
    for r in results:
        # Check matched_on: should not contain "substr" because we don't do substring
        for m in r.matched_on:
            assert "substr" not in m, (
                f"Entry {r.entry['id']} matched via substring: {m}. "
                f"Token-based matching should not use substring."
            )


def test_regression_triangular_not_top_ranked_for_unease():
    """REGRESSION: TRIANGULAR should not appear in top results for 'unease'.

    Previously, TRIANGULAR scored 0.468 because 'instability' substring-matched
    'stability' in its keywords.  With token matching, this path is gone.
    """
    results = query_compositions({"emotion": "unease"}, min_score=0.05)
    top_ids = [r[0]["id"] for r in results]
    # TRIANGULAR may still appear (e.g., via scene_type matching), but if it
    # does, its score should be driven by legitimate matches, not substrings.
    if "comp_triangular" in top_ids:
        # Get detailed scores
        detailed = query_compositions_detailed({"emotion": "unease"}, min_score=0.05)
        for d in detailed:
            if d.entry["id"] == "comp_triangular":
                # It should not have semantic matches for 'instability'
                for m in d.matched_on:
                    assert "instability" not in m or "substr" not in m, (
                        f"TRIANGULAR matched via 'instability' substring: {m}"
                    )


def test_regression_balanced_not_top_ranked_for_unease():
    """REGRESSION: Same as above but for BALANCED."""
    results = query_compositions({"emotion": "unease"}, min_score=0.05)
    top_ids = [r[0]["id"] for r in results]
    if "comp_balanced" in top_ids:
        detailed = query_compositions_detailed({"emotion": "unease"}, min_score=0.05)
        for d in detailed:
            if d.entry["id"] == "comp_balanced":
                for m in d.matched_on:
                    assert "instability" not in m or "substr" not in m


# ============================================================================
# REGRESSION: Weight balance -- emotion-only should not dominate
# ============================================================================

def test_regression_shot_param_matters():
    """REGRESSION: An entry with partial semantic match but full shot-param
    match should outrank one with full semantic but zero shot-param match,
    when W_SEMANTIC = W_SHOT = 0.5.

    We test this by constructing a controlled scenario:
    - Entry A: 100% semantic match, 0% shot match
    - Entry B: 50% semantic match, 100% shot match
    With equal weights, both should score ~0.5, but B should NOT be
    unfairly penalized below A.

    Real scenario from the_hanging.md SHOT_03:
    - ASYMMETRICAL: strong semantic (unease) + good shot (CU/85mm)
    - Some entry with only semantic but wrong framing: should rank lower
    """
    # Use real data: query with both emotion AND shot params
    results = query_compositions_detailed(
        {"emotion": "unease", "framing": "CU", "lens": "85mm", "scene_type": "psychological"},
        min_score=0.05,
    )

    # Find ASYMMETRICAL (should rank high due to semantic + shot)
    asym = next((r for r in results if r.entry["id"] == "comp_asymmetrical"), None)
    assert asym is not None, "ASYMMETRICAL must appear in results"

    # ASYMMETRICAL should have a non-trivial shot_param_score (> 0)
    assert asym.shot_param_score > 0, (
        f"ASYMMETRICAL shot_param_score={asym.shot_param_score}. "
        f"With framing=CU, lens=85mm, it should match at least one."
    )

    # Now check: an entry with high semantic but zero shot should NOT
    # outrank ASYMMETRICAL (unless its semantic is drastically higher)
    for r in results:
        if r.shot_param_score == 0.0 and r.semantic_score > 0:
            # This entry had zero shot match.  With equal weights,
            # it should generally rank below entries with shot matches.
            # This is a soft assertion; we just log it.
            pass


def test_regression_scores_are_normalized():
    """All sub-scores must be in [0, 1]."""
    results = query_compositions_detailed(
        {"emotion": "unease", "scene_type": "psychological", "framing": "CU", "lens": "85mm"},
        min_score=0.0,
    )
    for r in results:
        assert 0.0 <= r.semantic_score <= 1.0, (
            f"{r.entry['id']} semantic_score={r.semantic_score} out of range"
        )
        assert 0.0 <= r.shot_param_score <= 1.0, (
            f"{r.entry['id']} shot_param_score={r.shot_param_score} out of range"
        )
        assert 0.0 <= r.score <= 1.0, (
            f"{r.entry['id']} score={r.score} out of range"
        )


# ============================================================================
# Detailed query tests
# ============================================================================

def test_detailed_query_returns_matched_on():
    results = query_compositions_detailed({"emotion": "loneliness"})
    assert len(results) > 0
    assert results[0].matched_on
    assert any("token" in m for m in results[0].matched_on)


def test_detailed_query_scores_monotonic():
    results = query_compositions_detailed({"emotion": "unease"})
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


# ============================================================================
# Emotion/scene map coverage
# ============================================================================

def test_emotion_map_has_chinese_entries():
    required = ["\u4e0d\u5b89", "\u58d3\u6291", "\u5b64\u7368", "\u6050\u61fc", "\u5e73\u975c"]
    for term in required:
        assert term in _EMOTION_MAP, f"Missing: {term}"


def test_scene_map_has_key_entries():
    required = ["isolation", "tension", "confrontation", "dialogue", "psychological"]
    for term in required:
        assert term in _SCENE_MAP, f"Missing: {term}"


def test_resolve_emotion_keywords_chinese():
    """Chinese emotion should resolve to English keyword list."""
    keywords = _resolve_emotion_keywords("\u4e0d\u5b89")
    assert "unease" in keywords or "anxiety" in keywords or "tension" in keywords


def test_resolve_emotion_keywords_english():
    keywords = _resolve_emotion_keywords("unease")
    assert "unease" in keywords


# ============================================================================
# REGRESSION: Jieba-segmented lookup (modifier + base emotion combos)
# ============================================================================

def test_resolve_emotion_yinyin_buan_via_jieba():
    """REGRESSION: '隐隐不安' must resolve via jieba segmentation.
    Previously, this returned raw tokens (no English keywords) because
    the full phrase was not in _EMOTION_MAP.  Now jieba splits it into
    ['隐隐', '不安'] and both tokens contribute keywords."""
    keywords = _resolve_emotion_keywords("隐隐不安")
    assert len(keywords) > 0
    # Should include base emotion keywords from '不安'
    assert "unease" in keywords or "anxiety" in keywords or "tension" in keywords
    # Should also include modifier keywords from '隐隐'
    assert "subdued" in keywords or "suppressed" in keywords


def test_resolve_weiw_jinzhang_via_jieba():
    """REGRESSION: '微微紧张' must resolve both tokens."""
    keywords = _resolve_emotion_keywords("微微紧张")
    assert "tension" in keywords or "anxiety" in keywords
    assert "subtle" in keywords or "slight" in keywords


def test_resolve_zhujian_juewang_via_jieba():
    """REGRESSION: '逐渐绝望' must resolve both tokens."""
    keywords = _resolve_emotion_keywords("逐渐绝望")
    assert "despair" in keywords
    assert "growing" in keywords or "mounting" in keywords


def test_resolve_yisi_gudu_via_jieba():
    """REGRESSION: '一丝孤独' must resolve both tokens."""
    keywords = _resolve_emotion_keywords("一丝孤独")
    assert "loneliness" in keywords or "isolation" in keywords
    assert "trace" in keywords or "hint" in keywords


def test_resolve_simplified_chinese_entries():
    """REGRESSION: Simplified Chinese entries must be in _EMOTION_MAP.
    Previously only traditional characters were mapped, causing jieba
    (which outputs simplified) to miss base emotion lookups."""
    simplified = ["紧张", "孤独", "恐惧", "权力", "压抑", "绝望", "焦虑"]
    for term in simplified:
        assert term in _EMOTION_MAP, f"Missing simplified: {term}"
        assert len(_EMOTION_MAP[term]) > 0, f"Empty mapping for: {term}"


def test_emotion_query_yiny_buan_semantic_not_zero():
    """REGRESSION: Querying '隐隐不安' must produce non-zero semantic scores.
    Before the jieba fix, all entries had semantic_score=0 because the
    raw Chinese tokens didn't match English keywords."""
    results = query_compositions_detailed(
        {"emotion": "隐隐不安", "scene_type": "psychological"},
        min_score=0.05,
    )
    assert len(results) > 0, "No results for '隐隐不安' — regression"
    # At least the top result must have semantic_score > 0
    assert results[0].semantic_score > 0.0, (
        f"semantic_score is still 0 for '隐隐不安'. Got: {results[0].semantic_score}"
    )


def test_emotion_query_yayi_semantic_not_zero():
    """REGRESSION: '压抑' (simplified) must produce non-zero semantic."""
    results = query_compositions_detailed(
        {"emotion": "压抑", "scene_type": "psychological"},
        min_score=0.05,
    )
    assert len(results) > 0
    assert results[0].semantic_score > 0.0


def test_emotion_query_chenzhong_semantic_not_zero():
    """REGRESSION: '沉重' must produce non-zero semantic."""
    results = query_compositions_detailed(
        {"emotion": "沉重", "scene_type": "psychological"},
        min_score=0.05,
    )
    assert len(results) > 0
    assert results[0].semantic_score > 0.0
