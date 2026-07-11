"""Unit tests for the 6-layer analysis pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from director_os.layers import LayerPipeline
from director_os.models.project import (
    Project, Metadata, Character, VisualIdentity,
    VisualLanguage, Shot, Subject, LightingSetup, ShotColor, Story,
)


def _make_minimal_shot(framing: str = "ms", movement: str = "static", duration: float = 4.0) -> Shot:
    return Shot(
        shot_id="shot_01",
        order=1,
        duration=duration,
        framing=framing,
        movement=movement,
        subject=Subject(character="char_01", action="walks slowly"),
        lighting=LightingSetup(mood="soft lighting"),
    )


def test_layer_pipeline_runs():
    project = Project(
        metadata=Metadata(title="Test", description="一个现代浪漫场景"),
        story=Story(premise="A woman walks down stairs", genre=["romance"]),
        visual_language=VisualLanguage(
            style="Retro Realism",
            atmosphere="warm and dreamy",
            texture="film grain",
        ),
        characters=[
            Character(id="char_01", name="Alice", role="protagonist",
                      visual_identity=VisualIdentity(appearance="tall", clothing="evening gown")),
        ],
    )
    project.characters[0].personality = ["elegant"]

    intent = {
        "creative_goal": {"primary": "test"},
        "visual_direction": {
            "style": "Retro Realism",
            "mood": ["warm"],
            "atmosphere": "dreamy",
            "lighting": "soft",
        },
        "camera_strategy": {"framing": "ms", "movement": "tracking"},
        "character_direction": [{"id": "char_01", "name": "Alice", "action": "walks"}],
        "constraints": {},
        "narrative_intent": {},
        "temporal_design": {},
    }

    shots = [_make_minimal_shot().__dict__]

    pipeline = LayerPipeline()
    result = pipeline.analyze(project, intent, shots)

    assert "l1_baseline" in result
    assert "l2_spatial" in result
    assert "l3_lighting" in result
    assert "l4_camera" in result
    assert "l5_character" in result
    assert "l6_microtexture" in result

    # L1 checks
    l1 = result["l1_baseline"]
    assert "contemporary" in l1.get("era_candidates", []) or "modern" in l1.get("era_anchor", "").lower()

    # L2 checks
    l2 = result["l2_spatial"]
    assert l2["depth_layers"]

    # L4 checks
    l4 = result["l4_camera"]
    assert l4["shot_count"] == 1
    assert l4["storyboard_summary"]

    # L5 checks
    l5 = result["l5_character"]
    assert l5["character_count"] == 1
    assert l5["main_character"]["id"] == "char_01"


def test_l1_era_detection():
    project = Project(
        metadata=Metadata(description="A 1930s republican era detective story"),
        visual_language=VisualLanguage(style="Noir"),
    )
    intent = {"creative_goal": {}, "visual_direction": {}, "camera_strategy": {},
              "character_direction": [], "constraints": {}, "narrative_intent": {},
              "temporal_design": {}}
    pipeline = LayerPipeline()
    result = pipeline.analyze(project, intent, [])
    assert "republican_era" in result["l1_baseline"].get("era_candidates", [])


def test_l4_shot_sequence():
    shots = [
        _make_minimal_shot(framing="els", movement="static", duration=4.0),
        _make_minimal_shot(framing="cu", movement="dolly_in", duration=3.0),
    ]
    shots[1].shot_id = "shot_02"
    shots[1].order = 2
    shots[1].subject = Subject(character="char_01", action="reacts")

    project = Project(metadata=Metadata(title="T"))
    intent = {"creative_goal": {}, "visual_direction": {}, "camera_strategy": {},
              "character_direction": [], "constraints": {}, "narrative_intent": {},
              "temporal_design": {}}

    pipeline = LayerPipeline()
    result = pipeline.analyze(project, intent, [s.__dict__ for s in shots])

    l4 = result["l4_camera"]
    assert l4["shot_count"] == 2
    seq = l4["shot_sequence"]
    assert seq[0]["framing"] == "els"
    assert seq[1]["framing"] == "cu"
    assert seq[1]["movement"] == "dolly_in"

