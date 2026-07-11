"""Unit tests for director_os/library/loader.py — LibraryLoader."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from director_os.library.loader import LibraryLoader
from director_os.models.library_entry import LibraryEntry


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_entries():
    return [
        LibraryEntry(
            metadata={"id": "lib_dolly", "name": "Dolly Shot"},
            category="cinematography",
            knowledge={"concept": "Smooth dolly movement"},
            applicability={"emotions": ["tension"], "genres": ["action"]},
        ),
        LibraryEntry(
            metadata={"id": "lib_noir", "name": "Noir Lighting"},
            category="lighting",
            knowledge={"concept": "High contrast shadow lighting"},
            applicability={"emotions": ["mystery", "tension"], "genres": ["noir", "drama"]},
        ),
        LibraryEntry(
            metadata={"id": "lib_rule_thirds", "name": "Rule of Thirds"},
            category="composition",
            knowledge={"concept": "Classic framing rule"},
            applicability={"emotions": ["balance"], "genres": []},
        ),
    ]


# ============================================================================
# load() — indexing
# ============================================================================

def test_load_indexes_by_category(sample_entries):
    loader = LibraryLoader()
    loader.load(sample_entries)
    assert len(loader._entries) == 3
    assert "cinematography" in loader._by_category
    assert "lighting" in loader._by_category
    assert "composition" in loader._by_category
    assert len(loader._by_category["cinematography"]) == 1


def test_load_empty():
    loader = LibraryLoader()
    loader.load([])
    assert loader._entries == []
    assert loader._by_category == {}


# ============================================================================
# query()
# ============================================================================

def test_query_by_category(sample_entries):
    loader = LibraryLoader()
    loader.load(sample_entries)
    results = loader.query(category="cinematography")
    assert len(results) == 1
    assert results[0].metadata["id"] == "lib_dolly"


def test_query_by_emotion(sample_entries):
    loader = LibraryLoader()
    loader.load(sample_entries)
    results = loader.query(emotion="tension")
    assert len(results) == 2
    ids = {r.metadata["id"] for r in results}
    assert ids == {"lib_dolly", "lib_noir"}


def test_query_by_emotion_and_category(sample_entries):
    loader = LibraryLoader()
    loader.load(sample_entries)
    results = loader.query(category="lighting", emotion="tension")
    assert len(results) == 1
    assert results[0].metadata["id"] == "lib_noir"


def test_query_by_genre(sample_entries):
    loader = LibraryLoader()
    loader.load(sample_entries)
    results = loader.query(genre="noir")
    assert len(results) == 1
    assert results[0].metadata["id"] == "lib_noir"


def test_query_no_match(sample_entries):
    loader = LibraryLoader()
    loader.load(sample_entries)
    results = loader.query(emotion="happiness")
    assert results == []


def test_query_empty_loader():
    loader = LibraryLoader()
    results = loader.query(category="anything")
    assert results == []


def test_query_all_no_filters(sample_entries):
    loader = LibraryLoader()
    loader.load(sample_entries)
    results = loader.query()
    assert len(results) == 3


def test_query_category_then_emotion_filter(sample_entries):
    """When category is specified, only that category is searched."""
    loader = LibraryLoader()
    loader.load(sample_entries)
    # Query cinematography with emotion=mystery should find nothing
    # (lib_dolly has emotion=tension, not mystery)
    results = loader.query(category="cinematography", emotion="mystery")
    assert results == []


# ============================================================================
# load_all() — directory discovery
# ============================================================================

def test_load_all_existing_dir():
    """load_all() should discover YAML files in the libraries/ directory."""
    loader = LibraryLoader()
    loader.load_all()
    # The project has libraries/ with entries
    assert len(loader._entries) > 0


def test_load_all_nonexistent_dir():
    """load_all() on a nonexistent path should not crash."""
    loader = LibraryLoader()
    loader.load_all("/nonexistent/path")
    assert loader._entries == []
