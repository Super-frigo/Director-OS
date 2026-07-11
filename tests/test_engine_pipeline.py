"""Unit tests for the engine pipeline — StoryEngine, CharacterEngine, VisualEngine, ShotEngine,
EnginePipeline, and helper functions."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from director_os.engine.pipeline import (
    EngineInput,
    StoryEngine,
    CharacterEngine,
    VisualEngine,
    ShotEngine,
    EnginePipeline,
    _first_shot_field,
    _get_duration,
)
from director_os.models.project import (
    Project, Metadata, Creative, Story, World,
    Character, VisualIdentity, Shot, Subject,
    LightingSetup, VisualLanguage,
)
from director_os.models.library_entry import LibraryEntry


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def empty_project():
    return Project()


@pytest.fixture
def minimal_project():
    return Project(
        metadata=Metadata(title="Test"),
        story=Story(
            premise="A test story",
            genre=["drama"],
            theme=["redemption"],
            structure={"acts": ["act1", "act2", "act3"]},
        ),
        creative=Creative(genre="drama", tone="dark"),
    )


@pytest.fixture
def project_with_shots():
    return Project(
        metadata=Metadata(title="Shot Test"),
        story=Story(premise="A visual test", genre=["action"]),
        visual_language=VisualLanguage(
            style="Noir",
            atmosphere="tense",
            texture="film grain",
            lighting="low key",
            camera_body="ARRI Alexa Mini",
        ),
        shots=[
            Shot(
                shot_id="S1", order=1, duration=5.0,
                framing="LS", movement="DOLLY_IN", lens="35mm", angle="EYE_LEVEL",
                subject=Subject(character="c1", action="walks in"),
                lighting=LightingSetup(mood="dark", key_light="LOW_KEY"),
            ),
            Shot(
                shot_id="S2", order=2, duration=3.0,
                framing="CU", movement="STATIC", lens="85mm", angle="EYE_LEVEL",
                subject=Subject(character="c1", action="reacts"),
            ),
        ],
        characters=[
            Character(id="c1", name="Hero", role="protagonist", personality=["brave"]),
        ],
    )


@pytest.fixture
def sample_library_entry():
    return LibraryEntry(
        metadata={"id": "lib_beat_detective_arrival", "name": "Detective Arrival Beat"},
        category="storytelling",
        knowledge={"concept": "A beat where tension builds through arrival"},
        applicability={
            "emotions": ["tension", "anticipation"],
            "genres": ["drama", "noir"],
        },
    )


@pytest.fixture
def action_library_entry():
    """A library entry whose genre matches the project_with_shots genre 'action'."""
    return LibraryEntry(
        metadata={"id": "lib_beat_action", "name": "Action Beat"},
        category="storytelling",
        knowledge={"concept": "Fast-paced action beats"},
        applicability={
            "emotions": ["excitement"],
            "genres": ["action"],
        },
    )


@pytest.fixture
def engine_input(project_with_shots, sample_library_entry):
    return EngineInput(
        project=project_with_shots,
        libraries={
            "storytelling": [sample_library_entry],
            "cinematography": [
                LibraryEntry(
                    metadata={"id": "lib_cam_dolly", "name": "Dolly Shot"},
                    category="cinematography",
                    knowledge={"concept": "Dollying creates immersion"},
                ),
            ],
            "lighting": [
                LibraryEntry(
                    metadata={"id": "lib_light_noir", "name": "Noir Lighting"},
                    category="lighting",
                    knowledge={"concept": "High contrast shadows"},
                ),
            ],
            "composition": [
                LibraryEntry(
                    metadata={"id": "lib_comp_rule_thirds", "name": "Rule of Thirds"},
                    category="composition",
                    knowledge={"concept": "Classic framing rule"},
                ),
            ],
        },
    )


# ============================================================================
# EngineInput tests
# ============================================================================

def test_engine_input_construction(empty_project):
    inp = EngineInput(project=empty_project)
    assert inp.project is empty_project
    assert inp.context == {}
    assert inp.libraries == {}


def test_engine_input_with_libraries(empty_project, sample_library_entry):
    inp = EngineInput(
        project=empty_project,
        libraries={"storytelling": [sample_library_entry]},
    )
    assert len(inp.libraries["storytelling"]) == 1


# ============================================================================
# _get_duration tests
# ============================================================================

def test_get_duration_with_int():
    assert _get_duration(5) == "5"


def test_get_duration_with_str():
    assert _get_duration("5s") == "5s"


def test_get_duration_with_none():
    assert _get_duration(None) == ""


def test_get_duration_with_zero():
    """Zero is a valid duration value — must not be treated as falsy."""
    assert _get_duration(0) == "0"


def test_get_duration_with_empty():
    assert _get_duration("") == ""


# ============================================================================
# _first_shot_field tests
# ============================================================================

def test_first_shot_field_finds_value():
    shots = [{"framing": "LS"}, {"framing": "CU"}]
    assert _first_shot_field(shots, "framing") == "LS"


def test_first_shot_field_skips_empty():
    shots = [{"framing": ""}, {"framing": "CU"}]
    assert _first_shot_field(shots, "framing") == "CU"


def test_first_shot_field_returns_default():
    assert _first_shot_field([], "framing", "MS") == "MS"


def test_first_shot_field_missing_key():
    shots = [{"other": "val"}]
    assert _first_shot_field(shots, "framing", "N/A") == "N/A"


# ============================================================================
# StoryEngine tests
# ============================================================================

def test_story_engine_extracts_premise(minimal_project):
    engine = StoryEngine()
    result = engine.process(EngineInput(project=minimal_project))
    assert result["premise"] == "A test story"
    assert result["genre"] == ["drama"]
    assert result["theme"] == ["redemption"]
    assert result["acts"] == ["act1", "act2", "act3"]


def test_story_engine_creative_goal(minimal_project):
    engine = StoryEngine()
    result = engine.process(EngineInput(project=minimal_project))
    cg = result["creative_goal"]
    assert cg["primary"] == "A test story"
    assert isinstance(cg["emotional_target"], list)


def test_story_engine_empty_project(empty_project):
    engine = StoryEngine()
    result = engine.process(EngineInput(project=empty_project))
    assert result["premise"] == ""
    assert result["genre"] == []


def test_story_engine_with_library(project_with_shots, action_library_entry):
    """StoryEngine should match library entries by genre."""
    engine = StoryEngine()
    inp = EngineInput(
        project=project_with_shots,
        libraries={"storytelling": [action_library_entry]},
    )
    result = engine.process(inp)
    guidance = result["creative_goal"]["library_guidance"]
    assert len(guidance) >= 1


# ============================================================================
# CharacterEngine tests
# ============================================================================

def test_character_engine_maps_characters(project_with_shots):
    engine = CharacterEngine()
    result = engine.process(EngineInput(project=project_with_shots))
    chars = result["characters"]
    assert len(chars) == 1
    assert chars[0].id == "c1"
    assert chars[0].name == "Hero"
    assert chars[0].performance == "protagonist"


def test_character_engine_empty_project(empty_project):
    engine = CharacterEngine()
    result = engine.process(EngineInput(project=empty_project))
    assert result["characters"] == []


# ============================================================================
# VisualEngine tests
# ============================================================================

def test_visual_engine_extracts_style(project_with_shots):
    engine = VisualEngine()
    result = engine.process(EngineInput(project=project_with_shots))
    assert result["style"] == "Noir"
    assert result["atmosphere"] == "tense"
    assert result["texture"] == "film grain"


def test_visual_engine_reads_first_shot_fields(project_with_shots):
    engine = VisualEngine()
    result = engine.process(EngineInput(project=project_with_shots))
    assert result["composition"] == "LS"
    assert result["camera_body"] == "ARRI Alexa Mini"


def test_visual_engine_no_shots(empty_project):
    engine = VisualEngine()
    result = engine.process(EngineInput(project=empty_project))
    assert result["composition"] == ""


def test_visual_engine_color_as_string():
    """VisualEngine should handle vl.color as a plain string."""
    project = Project(
        visual_language=VisualLanguage(style="Anime", color="pastel palette"),
    )
    engine = VisualEngine()
    result = engine.process(EngineInput(project=project))
    assert result["color"] == "pastel palette"


def test_visual_engine_color_as_dict():
    """VisualEngine should handle vl.color as a dict with 'palette' key."""
    project = Project(
        visual_language=VisualLanguage(
            style="Noir",
            color={"palette": "monochrome", "accent": "red"},
        ),
    )
    engine = VisualEngine()
    result = engine.process(EngineInput(project=project))
    assert result["color"] == "monochrome"


def test_visual_engine_with_libraries(project_with_shots, engine_input):
    engine = VisualEngine()
    result = engine.process(engine_input)
    assert len(result["library_camera"]) >= 1
    assert len(result["library_lighting"]) >= 1
    assert len(result["library_composition"]) >= 1


# ============================================================================
# ShotEngine tests
# ============================================================================

def test_shot_engine_maps_all_shots(project_with_shots):
    engine = ShotEngine()
    result = engine.process(EngineInput(project=project_with_shots))
    assert len(result["shots"]) == 2
    assert result["shots"][0]["shot_id"] == "S1"
    assert result["shots"][1]["shot_id"] == "S2"


def test_shot_engine_extracts_fields(project_with_shots):
    engine = ShotEngine()
    result = engine.process(EngineInput(project=project_with_shots))
    s1 = result["shots"][0]
    assert s1["framing"] == "LS"
    assert s1["movement"] == "DOLLY_IN"
    assert s1["lens"] == "35mm"
    assert s1["action"] == "walks in"


def test_shot_engine_no_shots(empty_project):
    engine = ShotEngine()
    result = engine.process(EngineInput(project=empty_project))
    assert result["shots"] == []


# ============================================================================
# BaseEngine._query_library tests
# ============================================================================

def test_query_library_by_category(engine_input):
    engine = StoryEngine()
    results = engine._query_library(engine_input, category="storytelling")
    assert len(results) == 1
    assert results[0].metadata["id"] == "lib_beat_detective_arrival"


def test_query_library_with_emotion_filter():
    entry = LibraryEntry(
        metadata={"id": "lib_1"},
        category="storytelling",
        applicability={"emotions": ["tension"], "genres": []},
    )
    inp = EngineInput(
        project=Project(),
        libraries={"storytelling": [entry]},
    )
    engine = StoryEngine()
    results = engine._query_library(inp, category="storytelling", emotion="tension")
    assert len(results) == 1


def test_query_library_emotion_mismatch():
    entry = LibraryEntry(
        metadata={"id": "lib_1"},
        category="storytelling",
        applicability={"emotions": ["joy"], "genres": []},
    )
    inp = EngineInput(
        project=Project(),
        libraries={"storytelling": [entry]},
    )
    engine = StoryEngine()
    results = engine._query_library(inp, category="storytelling", emotion="tension")
    assert len(results) == 0


def test_query_library_with_genre_filter():
    entry = LibraryEntry(
        metadata={"id": "lib_1"},
        category="storytelling",
        applicability={"emotions": [], "genres": ["drama"]},
    )
    inp = EngineInput(
        project=Project(),
        libraries={"storytelling": [entry]},
    )
    engine = StoryEngine()
    results = engine._query_library(inp, category="storytelling", genre="drama")
    assert len(results) == 1


def test_query_library_no_category_searches_all():
    e1 = LibraryEntry(
        metadata={"id": "lib_1"}, category="storytelling",
        applicability={"emotions": [], "genres": []},
    )
    e2 = LibraryEntry(
        metadata={"id": "lib_2"}, category="cinematography",
        applicability={"emotions": [], "genres": []},
    )
    inp = EngineInput(
        project=Project(),
        libraries={"storytelling": [e1], "cinematography": [e2]},
    )
    engine = StoryEngine()
    results = engine._query_library(inp)
    assert len(results) == 2


# ============================================================================
# EnginePipeline.run tests
# ============================================================================

def test_engine_pipeline_run_produces_intent(project_with_shots):
    pipeline = EnginePipeline()
    inp = EngineInput(project=project_with_shots)
    intent = pipeline.run(inp)
    assert intent is not None
    assert intent.creative_goal is not None
    assert intent.narrative_intent["premise"] == "A visual test"


def test_engine_pipeline_run_populates_visual(project_with_shots):
    pipeline = EnginePipeline()
    inp = EngineInput(project=project_with_shots)
    intent = pipeline.run(inp)
    assert intent.visual_direction["style"] == "Noir"


def test_engine_pipeline_run_with_camera_strategy(project_with_shots):
    pipeline = EnginePipeline()
    inp = EngineInput(project=project_with_shots)
    intent = pipeline.run(inp)
    assert isinstance(intent.camera_strategy, dict)
    assert "framing" in intent.camera_strategy


def test_engine_pipeline_run_empty_project(empty_project):
    pipeline = EnginePipeline()
    inp = EngineInput(project=empty_project)
    intent = pipeline.run(inp)
    assert intent is not None


def test_engine_pipeline_has_all_engines():
    pipeline = EnginePipeline()
    assert set(pipeline.engines.keys()) == {"story", "character", "visual", "shot"}
