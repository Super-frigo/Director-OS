"""Unit tests for director_os/models — dataclass defaults, from_dict conversions, validate()."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from director_os.models.project import (
    Project, Metadata, Creative, Story, StoryBeat, World, Location,
    Character, VisualIdentity, Scene, Shot, Subject,
    LightingSetup, ShotColor, ShotAudio, EmotionTarget,
    VisualLanguage, AudioDesign, ProductionDesign, Continuity,
    Constraints, OutputProfile, HistoryEntry,
)
from director_os.models.production_intent import ProductionIntent, CharacterDirection
from director_os.models.execution_package import ExecutionPackage
from director_os.models.library_entry import LibraryEntry
from director_os.models.review import Review, Issue, Suggestion


# ============================================================================
# Project dataclass — default values
# ============================================================================

def test_project_defaults():
    p = Project()
    assert p.schema_version == "1.0"
    assert p.metadata.title == ""
    assert p.story.premise == ""
    assert p.characters == []
    assert p.shots == []
    assert p.story_beats == []
    assert p.scenes == []


def test_metadata_defaults():
    m = Metadata()
    assert m.status == "Idea"
    assert m.language == "zh-CN"
    assert m.title == ""


def test_creative_defaults():
    c = Creative()
    assert c.visual_priority == 5
    assert c.dialogue_priority == 5
    assert c.action_priority == 5
    assert c.references == {}


def test_story_defaults():
    s = Story()
    assert s.premise == ""
    assert s.theme == []
    assert s.genre == []
    assert s.structure == {"acts": []}


def test_storybeat_defaults():
    sb = StoryBeat()
    assert sb.duration_ratio == 0.0
    assert sb.dialogue is False
    assert sb.characters == []


def test_world_defaults():
    w = World()
    assert w.timeline == ""
    assert w.locations == []


def test_character_defaults():
    c = Character()
    assert c.continuity_lock is False
    assert c.personality == []
    assert isinstance(c.visual_identity, VisualIdentity)


def test_visual_identity_defaults():
    vi = VisualIdentity()
    assert vi.age_range == ""
    assert vi.appearance == ""


def test_shot_defaults():
    s = Shot()
    assert s.order == 1
    assert s.duration == 0.0
    assert isinstance(s.subject, Subject)
    assert isinstance(s.lighting, LightingSetup)
    assert isinstance(s.color, ShotColor)
    assert isinstance(s.audio, ShotAudio)
    assert isinstance(s.emotion, EmotionTarget)


def test_visual_language_defaults():
    vl = VisualLanguage()
    assert vl.style == ""
    assert vl.color == {}
    assert vl.camera_philosophy == ""
    assert vl.references == []


def test_output_profile_defaults():
    op = OutputProfile()
    assert op.aspect_ratio == "16:9"
    assert op.fps == 24
    assert op.resolution == "1080p"
    assert op.delivery == "digital"


# ============================================================================
# Project.validate()
# ============================================================================

def test_validate_empty_project():
    """An empty project should have validation issues."""
    p = Project()
    issues = p.validate()
    assert len(issues) >= 3  # title, premise, characters
    assert any("title" in i.lower() for i in issues)
    assert any("premise" in i.lower() for i in issues)
    assert any("character" in i.lower() for i in issues)


def test_validate_valid_project():
    """A project with required fields should be valid."""
    p = Project(
        metadata=Metadata(title="Test"),
        story=Story(premise="A test story"),
        characters=[Character(id="c1", role="hero")],
    )
    issues = p.validate()
    assert issues == []


def test_validate_shots_without_beats():
    """Shots without story_beats should warn."""
    p = Project(
        metadata=Metadata(title="Test"),
        story=Story(premise="Test"),
        characters=[Character(id="c1", role="hero")],
        shots=[Shot(shot_id="S1")],
    )
    issues = p.validate()
    assert any("story_beats" in i.lower() for i in issues)


def test_validate_scene_character_ref():
    """Scene referencing an undefined character should error."""
    p = Project(
        metadata=Metadata(title="Test"),
        story=Story(premise="Test"),
        characters=[Character(id="c1", role="hero")],
        scenes=[Scene(id="sc1", title="Scene 1", characters=["c2"])],
    )
    issues = p.validate()
    assert any("c2" in i for i in issues)


def test_is_valid():
    p = Project(
        metadata=Metadata(title="T"),
        story=Story(premise="P"),
        characters=[Character(id="c1", role="hero")],
    )
    assert p.is_valid() is True

    empty = Project()
    assert empty.is_valid() is False


def test_validate_with_beats_and_shots():
    """Project with both beats and shots passes that check."""
    p = Project(
        metadata=Metadata(title="T"),
        story=Story(premise="P"),
        characters=[Character(id="c1", role="hero")],
        story_beats=[StoryBeat(beat="b1", type="OPENING")],
        shots=[Shot(shot_id="S1")],
    )
    issues = p.validate()
    # Should NOT have the story_beats warning since both exist
    assert not any("story_beats" in i.lower() for i in issues)


def test_validate_duration_mismatch():
    """Total shot duration diverging from output.duration should warn."""
    p = Project(
        metadata=Metadata(title="T"),
        story=Story(premise="P"),
        characters=[Character(id="c1", role="hero")],
        story_beats=[StoryBeat(beat="b1", type="OPENING")],
        shots=[
            Shot(shot_id="S1", duration=5.0),
            Shot(shot_id="S2", duration=5.0),
            Shot(shot_id="S3", duration=5.0),
        ],
        output_profile=OutputProfile(duration=10),  # 15s of shots vs 10s target
    )
    issues = p.validate()
    assert any("output.duration" in i and "15" in i for i in issues)


def test_validate_duration_match():
    """Matching shot total and output.duration should not warn."""
    p = Project(
        metadata=Metadata(title="T"),
        story=Story(premise="P"),
        characters=[Character(id="c1", role="hero")],
        story_beats=[StoryBeat(beat="b1", type="OPENING")],
        shots=[
            Shot(shot_id="S1", duration=5.0),
            Shot(shot_id="S2", duration=5.0),
        ],
        output_profile=OutputProfile(duration=10),
    )
    issues = p.validate()
    assert not any("output.duration" in i for i in issues)


def test_validate_duration_within_tolerance():
    """A 1s difference is tolerated (rounding margin)."""
    p = Project(
        metadata=Metadata(title="T"),
        story=Story(premise="P"),
        characters=[Character(id="c1", role="hero")],
        story_beats=[StoryBeat(beat="b1", type="OPENING")],
        shots=[
            Shot(shot_id="S1", duration=5.5),
            Shot(shot_id="S2", duration=4.5),
        ],
        output_profile=OutputProfile(duration=10),
    )
    issues = p.validate()
    assert not any("output.duration" in i for i in issues)


# ============================================================================
# LightingSetup.from_dict()
# ============================================================================

def test_lighting_setup_from_dict_standard_keys():
    ls = LightingSetup.from_dict({
        "key_light": "SOFT",
        "fill_light": "NATURAL",
        "back_light": "RIM",
        "mood": "dark",
        "color_temp": "5500K",
    })
    assert ls.key_light == "SOFT"
    assert ls.fill_light == "NATURAL"
    assert ls.back_light == "RIM"
    assert ls.mood == "dark"
    assert ls.color_temp == "5500K"


def test_lighting_setup_from_dict_alias_keys():
    """Short key aliases: 'key' → key_light, 'fill' → fill_light, 'back' → back_light."""
    ls = LightingSetup.from_dict({
        "key": "HARD",
        "fill": "SOFT",
        "back": "NATURAL",
        "temperature": "3200K",
    })
    assert ls.key_light == "HARD"
    assert ls.fill_light == "SOFT"
    assert ls.back_light == "NATURAL"
    assert ls.color_temp == "3200K"


def test_lighting_setup_from_dict_empty():
    ls = LightingSetup.from_dict({})
    assert ls.key_light == ""
    assert ls.fill_light == ""
    assert ls.back_light == ""
    assert ls.mood == ""
    assert ls.color_temp == ""
    assert ls.position == ""
    assert ls.intensity == 0


def test_lighting_setup_from_dict_position_intensity():
    """position and intensity fields (added ADR-009) survive round-trip."""
    ls = LightingSetup.from_dict({
        "key_light": "NATURAL",
        "position": "BACK_45",
        "intensity": 3,
    })
    assert ls.key_light == "NATURAL"
    assert ls.position == "BACK_45"
    assert ls.intensity == 3


def test_lighting_setup_from_dict_partial():
    """Only some keys provided, rest default to empty."""
    ls = LightingSetup.from_dict({"mood": "romantic"})
    assert ls.mood == "romantic"
    assert ls.key_light == ""
    assert ls.color_temp == ""


# ============================================================================
# ProductionIntent defaults
# ============================================================================

def test_production_intent_defaults():
    pi = ProductionIntent()
    assert pi.schema_version == "1.0"
    assert isinstance(pi.visual_direction, dict)
    assert "style" in pi.visual_direction
    assert isinstance(pi.camera_strategy, dict)
    assert "framing" in pi.camera_strategy
    assert pi.character_direction == []
    assert pi.constraints == {"must": [], "avoid": [], "limitations": []}


def test_character_direction_defaults():
    cd = CharacterDirection()
    assert cd.id == ""
    assert cd.performance == ""
    assert cd.emotional_state == ""
    assert cd.action == ""
    assert cd.name == ""


# ============================================================================
# ExecutionPackage defaults
# ============================================================================

def test_execution_package_defaults():
    ep = ExecutionPackage()
    assert ep.schema_version == "1.0"
    assert ep.target["provider"] == ""
    assert "prompt" in ep.instructions
    assert isinstance(ep.validation["warnings"], list)


# ============================================================================
# LibraryEntry defaults
# ============================================================================

def test_library_entry_defaults():
    le = LibraryEntry()
    assert le.schema_version == "1.0"
    assert le.category == ""
    assert le.metadata["id"] == ""
    assert isinstance(le.applicability["emotions"], list)
    assert isinstance(le.knowledge["principles"], list)


# ============================================================================
# Review model defaults
# ============================================================================

def test_review_defaults():
    r = Review()
    assert r.schema_version == "1.0"
    assert r.issues == []
    assert r.suggestions == []
    assert r.confidence["overall"] == 0.0
    assert "narrative" in r.evaluation["dimensions"]


def test_issue_defaults():
    i = Issue()
    assert i.severity == "medium"
    assert i.category == ""


def test_suggestion_defaults():
    s = Suggestion()
    assert s.target == ""
    assert s.recommendation == ""


# ============================================================================
# Shot dataclass — nested defaults
# ============================================================================

def test_subject_defaults():
    s = Subject()
    assert s.character == ""
    assert s.action == ""
    assert s.position == ""
    assert s.state == ""


def test_shot_color_defaults():
    sc = ShotColor()
    assert sc.palette == ""
    assert sc.accent == ""
    assert sc.contrast == ""


def test_shot_audio_defaults():
    sa = ShotAudio()
    assert sa.silence is False
    assert sa.dialogue == ""
    assert sa.music == ""


def test_emotion_target_defaults():
    et = EmotionTarget()
    assert et.target == ""
    assert et.intensity == 5
