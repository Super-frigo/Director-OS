"""Unit tests for director_os/director.py — Director class methods."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from director_os.director import Director
from director_os.state import DirectorState, StateError
from director_os.models.project import Project, Character


# ============================================================================
# new_project()
# ============================================================================

def test_new_project_creates_project():
    d = Director()
    p = d.new_project(title="My Film", premise="A story")
    assert isinstance(p, Project)
    assert p.metadata.title == "My Film"
    assert p.story.premise == "A story"
    assert d.project is p


def test_new_project_defaults():
    d = Director()
    p = d.new_project()
    assert p.metadata.title == ""
    assert p.story.premise == ""


# ============================================================================
# load_project()
# ============================================================================

def test_load_project_loads_valid_file():
    d = Director()
    p = d.load_project("projects/the_hanging.md")
    assert isinstance(p, Project)
    assert p.metadata.title == "The Hanging"
    assert len(p.shots) == 4
    assert len(p.characters) == 3
    assert d.project is p


def test_load_project_raises_on_invalid():
    """A YAML file missing required modules should raise ValueError."""
    tmp = Path(tempfile.gettempdir()) / "_test_invalid_project.yaml"
    tmp.write_text("invalid_key: 1\n", encoding="utf-8")
    try:
        d = Director()
        with pytest.raises(ValueError, match="schema validation"):
            d.load_project(str(tmp))
    finally:
        tmp.unlink(missing_ok=True)


def test_load_project_file_not_found():
    d = Director()
    with pytest.raises(FileNotFoundError):
        d.load_project("/nonexistent/project.md")


# ============================================================================
# plan()
# ============================================================================

def test_plan_requires_project():
    d = Director()
    d.start_cycle("test")
    d.fast_forward_to(DirectorState.PLAN)
    with pytest.raises(RuntimeError, match="No project"):
        d.plan()


def test_plan_returns_intent():
    d = Director()
    d.new_project(title="Test", premise="A test")
    d.project.characters.append(Character(id="c1", role="hero"))
    d.start_cycle("test")
    d.fast_forward_to(DirectorState.PLAN)
    intent = d.plan()
    assert intent is not None
    assert intent.creative_goal is not None
    from director_os.models.production_intent import ProductionIntent
    assert isinstance(intent, ProductionIntent)


# ============================================================================
# compile()
# ============================================================================

def test_compile_requires_intent():
    d = Director()
    d.start_cycle("test")
    d.fast_forward_to(DirectorState.COMPILE)
    with pytest.raises(RuntimeError, match="No intent"):
        d.compile("seedance")


def test_compile_unknown_platform():
    d = Director()
    d.new_project(title="Test", premise="Test")
    d.project.characters.append(Character(id="c1", role="hero"))
    d.start_cycle("test")
    d.fast_forward_to(DirectorState.PLAN)
    d.plan()
    d.fast_forward_to(DirectorState.COMPILE)
    with pytest.raises(ValueError, match="Unknown compiler"):
        d.compile("nonexistent_platform")


def test_compile_seedance():
    d = Director()
    d.new_project(title="Test", premise="Test")
    d.project.characters.append(Character(id="c1", role="hero"))
    d.start_cycle("test")
    d.fast_forward_to(DirectorState.PLAN)
    d.plan()
    d.fast_forward_to(DirectorState.COMPILE)
    pkg = d.compile("seedance")
    assert pkg is not None
    assert pkg.target.get("provider") == "seedance"
    assert "prompt" in pkg.instructions


def test_compile_veo():
    d = Director()
    d.new_project(title="Test", premise="Test")
    d.project.characters.append(Character(id="c1", role="hero"))
    d.start_cycle("test")
    d.fast_forward_to(DirectorState.PLAN)
    d.plan()
    d.fast_forward_to(DirectorState.COMPILE)
    pkg = d.compile("veo")
    pkg = d.compile("veo")
    assert pkg is not None
    assert pkg.target.get("provider") == "veo"


# ============================================================================
# validate_project()
# ============================================================================

def test_validate_project_no_project():
    d = Director()
    issues = d.validate_project()
    assert issues == ["No project loaded"]


def test_validate_project_valid():
    d = Director()
    d.new_project(title="T", premise="P")
    d.project.characters.append(Character(id="c1", role="hero"))
    issues = d.validate_project()
    assert issues == []


def test_validate_project_invalid():
    d = Director()
    d.new_project()  # No title, no premise, no characters
    issues = d.validate_project()
    assert len(issues) >= 3


# ============================================================================
# library initialisation
# ============================================================================

def test_director_initialises_library():
    d = Director()
    assert d.resolver is not None
    assert d.resolver.provider_count > 0  # resolver registered in __init__
