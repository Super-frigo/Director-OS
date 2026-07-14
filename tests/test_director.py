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


# ============================================================================
# apply_proposals()
# ============================================================================


def test_apply_proposals_set_simple():
    d = Director()
    d.new_project(title="Test", premise="Old premise")
    result = d.apply_proposals([
        {"module": "story", "field": "premise", "action": "set", "value": "New premise"}
    ])
    assert d.project.story.premise == "New premise"
    assert len(result["applied"]) == 1
    assert len(result["errors"]) == 0


def test_apply_proposals_set_nested():
    d = Director()
    d.new_project(title="Test")
    result = d.apply_proposals([
        {"module": "visual_language", "field": "style", "action": "set", "value": "noir"}
    ])
    assert d.project.visual_language.style == "noir"
    assert result["applied"]


def test_apply_proposals_set_deeply_nested():
    d = Director()
    d.new_project(title="Test")
    # visual_language.color is a dict by default
    result = d.apply_proposals([
        {"module": "visual_language", "field": "color.palette", "action": "set", "value": "cold gray"}
    ])
    vc = d.project.visual_language.color
    assert isinstance(vc, dict) and vc.get("palette") == "cold gray"


def test_apply_proposals_append():
    """StoryAgent proposes append to story_beats."""
    d = Director()
    d.new_project(title="Test")
    result = d.apply_proposals([
        {"module": "story_beats", "field": "", "action": "append",
         "value": {"beat": "OPENING", "type": "OPENING", "emotion": "calm"}}
    ])
    assert len(d.project.story_beats) == 1
    assert d.project.story_beats[0].beat == "OPENING"
    assert result["applied"]


def test_apply_proposals_suggest_is_skipped():
    d = Director()
    d.new_project(title="Test")
    result = d.apply_proposals([
        {"module": "story", "field": "premise", "action": "suggest", "value": "maybe this?"}
    ])
    assert d.project.story.premise == ""  # unchanged
    assert len(result["skipped"]) == 1
    assert result["skipped"][0] == "suggest story.premise"


def test_apply_proposals_errors_reported():
    d = Director()
    d.new_project(title="Test")
    result = d.apply_proposals([
        {"module": "nonexistent", "field": "x", "action": "set", "value": 1}
    ])
    assert len(result["errors"]) >= 1
    assert result["errors"][0].startswith("set nonexistent.x")


def test_apply_proposals_no_project():
    d = Director()
    with pytest.raises(RuntimeError, match="No project"):
        d.apply_proposals([])


def test_apply_proposals_complex_path_with_index():
    d = Director()
    d.new_project(title="Test")
    from director_os.models.project import Shot, Subject
    d.project.shots = [Shot(shot_id="s1"), Shot(shot_id="s2")]
    result = d.apply_proposals([
        {"module": "shots", "field": "shots[0].framing", "action": "set", "value": "CU"}
    ])
    assert d.project.shots[0].framing == "CU"
    assert d.project.shots[1].framing == ""  # unchanged
    assert result["applied"]


def test_apply_proposals_multiple_mixed():
    d = Director()
    d.new_project(title="Test", premise="old")
    result = d.apply_proposals([
        {"module": "story", "field": "premise", "action": "set", "value": "new"},
        {"module": "story", "field": "theme", "action": "suggest", "value": "justice"},
        {"module": "metadata", "field": "status", "action": "set", "value": "Draft"},
    ])
    assert d.project.story.premise == "new"
    assert d.project.metadata.status == "Draft"
    assert len(result["applied"]) == 2
    assert len(result["skipped"]) == 1
    assert len(result["errors"]) == 0


# ============================================================================
# run_agent_cycle + apply_proposals integration
# ============================================================================


def test_run_and_apply_cycle():
    d = Director()
    d.new_project(title="Test", premise="A noir detective story")
    d.start_cycle("test")
    d.fast_forward_to(DirectorState.PLAN)
    cycle = d.run_agent_cycle()
    # Story agent produces beat recommendations
    proposals = cycle["proposals"]
    assert len(proposals) > 0, "agent should produce proposals"
    # Apply them back
    result = d.apply_proposals(proposals)
    assert result["applied"], "at least one proposal should be applied"
    # The first story_beat append should have created beats
    assert d.project.story_beats, "story_beats should be populated after apply"
