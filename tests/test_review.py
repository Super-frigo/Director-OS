"""Unit tests for director_os/review/base.py — BaseReviewer and ConsistencyReviewer."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from director_os.review.base import BaseReviewer, ConsistencyReviewer
from director_os.models.review import Review, Issue, Suggestion


# ============================================================================
# BaseReviewer
# ============================================================================

def test_base_reviewer_evaluate_raises():
    reviewer = BaseReviewer()
    with pytest.raises(NotImplementedError):
        reviewer.evaluate({}, {})


# ============================================================================
# ConsistencyReviewer — evaluate()
# ============================================================================

def test_consistency_reviewer_matching():
    """When character matches, should pass with high confidence."""
    reviewer = ConsistencyReviewer()
    intended = {"character": "Alice"}
    generated = {"character": "Alice"}
    result = reviewer.evaluate(intended, generated)

    assert isinstance(result, Review)
    assert result.confidence["overall"] == 0.8
    assert result.issues == []
    eval_char = result.evaluation["dimensions"]["consistency"]["character"]
    assert eval_char == "passed"


def test_consistency_reviewer_mismatch():
    """When character differs, should fail with issues and low confidence."""
    reviewer = ConsistencyReviewer()
    intended = {"character": "Alice"}
    generated = {"character": "Bob"}
    result = reviewer.evaluate(intended, generated)

    assert result.confidence["overall"] == 0.4
    assert len(result.issues) >= 1
    assert result.issues[0].id == "character_drift"
    assert result.issues[0].severity == "high"
    assert len(result.suggestions) >= 1
    assert result.suggestions[0].target == "character_engine"

    eval_char = result.evaluation["dimensions"]["consistency"]["character"]
    assert eval_char == "failed"


def test_consistency_reviewer_no_character_key():
    """When character key is missing, comparison (None != None) should pass."""
    reviewer = ConsistencyReviewer()
    intended = {}
    generated = {}
    result = reviewer.evaluate(intended, generated)
    assert result.confidence["overall"] == 0.8
    assert result.issues == []


def test_consistency_reviewer_returns_review_with_all_fields():
    reviewer = ConsistencyReviewer()
    result = reviewer.evaluate({"character": "X"}, {"character": "Y"})

    assert result.schema_version == "1.0"
    assert isinstance(result.target, dict)
    assert isinstance(result.comparison, dict)
    assert isinstance(result.evaluation, dict)
    assert isinstance(result.issues, list)
    assert isinstance(result.suggestions, list)
