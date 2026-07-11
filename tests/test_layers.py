"""Unit tests for the 6-layer analysis pipeline — enhanced coverage for L3-L6."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from director_os.layers import LayerPipeline
from director_os.layers.l1_baseline import BaselineLayer
from director_os.layers.l2_spatial import SpatialLayer
from director_os.layers.l3_lighting import LightingLayer
from director_os.layers.l4_camera import CameraLayer
from director_os.layers.l5_character import CharacterLayer
from director_os.layers.l6_microtexture import MicroTextureLayer
from director_os.models.project import (
    Project, Metadata, Character, VisualIdentity,
    VisualLanguage, Shot, Subject, LightingSetup, ShotColor, Story,
)


# ============================================================================
# Shared fixtures
# ============================================================================

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


def _make_shot_dict(sid, framing="ms", movement="static", duration=4.0, action=""):
    """Create a shot dict matching the format the layers receive from ShotEngine."""
    return {
        "shot_id": sid,
        "order": 1,
        "framing": framing,
        "movement": movement,
        "duration": f"{duration}s",
        "action": action,
    }


# ============================================================================
# Existing layer tests (kept as-is)
# ============================================================================

def test_layer_pipeline_runs():
    project = Project(
        metadata=Metadata(title="Test", description="\u4e00\u4e2a\u73b0\u4ee3\u6d6a\u6f2b\u573a\u666f"),
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

    l1 = result["l1_baseline"]
    assert "contemporary" in l1.get("era_candidates", []) or "modern" in l1.get("era_anchor", "").lower()

    l2 = result["l2_spatial"]
    assert l2["depth_layers"]

    l4 = result["l4_camera"]
    assert l4["shot_count"] == 1
    assert l4["storyboard_summary"]

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


# ============================================================================
# L1: BaselineLayer — enhanced tests
# ============================================================================

def test_l1_era_detection_from_description():
    """Era should be detected from metadata.description text."""
    layer = BaselineLayer()
    project = Project(
        metadata=Metadata(description="\u4e00\u4e2a\u5510\u671d\u7684\u53e4\u88c5\u6545\u4e8b"),
    )
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    assert "tang_dynasty" in result["era_candidates"]


def test_l1_style_from_visual_language():
    """Style anchor comes from visual_language.style."""
    layer = BaselineLayer()
    project = Project(
        visual_language=VisualLanguage(style="Retro Realism"),
    )
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    assert "Retro Realism" in result["style_candidates"]


def test_l1_resolution_from_render_settings():
    """Resolution should be detected from render_settings text."""
    layer = BaselineLayer()
    project = Project(
        visual_language=VisualLanguage(render_settings="8K output, high detail"),
    )
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    assert result["resolution"] == "8K"


def test_l1_default_resolution():
    """Default resolution is HD when nothing specified."""
    layer = BaselineLayer()
    project = Project()
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    assert result["resolution"] == "HD"


def test_l1_fallback_era_from_style():
    """When description has no era, detect from visual_language.style."""
    layer = BaselineLayer()
    project = Project(
        metadata=Metadata(description="A story"),
        visual_language=VisualLanguage(style="\u6c11\u56fd noir"),
    )
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    assert "republican_era" in result["era_candidates"]


# ============================================================================
# L2: SpatialLayer — enhanced tests
# ============================================================================

def test_l2_environment_detection():
    """Should detect indoor/outdoor from location text."""
    layer = SpatialLayer()
    project = Project(
        metadata=Metadata(description="\u5ba4\u5185\u573a\u666f"),
    )
    project.world.location = "\u4e00\u4e2a\u660f\u6697\u7684\u623f\u95f4"
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    # Either "indoor" or "room" is valid — both indicate an interior
    assert result["environment_type"] in ("indoor", "room")


def test_l2_depth_from_shots():
    """Depth layers should be extracted from shot composition data."""
    layer = SpatialLayer()
    project = Project(metadata=Metadata(title="T"))
    shots = [{
        "composition": {
            "foreground": "desk",
            "midground": "character",
            "background": "window",
        },
    }]
    result = layer.analyze({"project": project, "intent": {}, "shots": shots})
    dl = result["depth_layers"]
    assert "foreground" in dl
    assert "midground" in dl
    assert "background" in dl


def test_l2_default_depth_layers():
    """When no depth cues, should return default 3 layers (sorted alphabetically)."""
    layer = SpatialLayer()
    project = Project()
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    assert set(result["depth_layers"]) == {"foreground", "midground", "background"}
    assert len(result["depth_layers"]) == 3


def test_l2_directional_from_action():
    """Directional keywords should be extracted from shot actions."""
    layer = SpatialLayer()
    project = Project(metadata=Metadata(title="T"))
    shots = [{"action": "\u5979\u8d70\u4e0b\u697c\u68af"}]
    result = layer.analyze({"project": project, "intent": {}, "shots": shots})
    assert "staircase" in result["directional_anchors"]


# ============================================================================
# L3: LightingLayer — new tests
# ============================================================================

def test_l3_detects_light_sources():
    """Should detect light source keywords in project text."""
    layer = LightingLayer()
    project = Project(
        visual_language=VisualLanguage(lighting="\u70db\u706b\u6447\u66f3"),
    )
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    assert "\u70db\u706b" in result["sources_detected"]
    assert len(result["light_topology"]) >= 1


def test_l3_detects_mood_lighting():
    """Should detect mood keywords and map to lighting config."""
    layer = LightingLayer()
    project = Project(
        visual_language=VisualLanguage(atmosphere="\u9ed1\u6697\u538b\u6291"),
    )
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    assert result["lighting_mood"] in ("dark", "oppressive")


def test_l3_color_temperature_scheme():
    """Should build color temp string from detected sources."""
    layer = LightingLayer()
    project = Project(
        visual_language=VisualLanguage(lighting="\u65e5\u5149 \u6708\u5149"),
    )
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    assert "5500K" in result["color_temperature_scheme"]
    assert "6500K" in result["color_temperature_scheme"]


def test_l3_no_sources_empty_topology():
    """When no light keywords detected, topology should be empty dict."""
    layer = LightingLayer()
    project = Project()
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    assert result["light_topology"] == {}
    assert result["lighting_mood"] == ""


def test_l3_topology_roles_assigned():
    """First detected source = key, second = fill, etc."""
    layer = LightingLayer()
    project = Project(
        visual_language=VisualLanguage(lighting="\u70db\u706b \u6708\u5149 \u65e5\u5149 \u7a97\u6237\u5916"),
    )
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    topo = result["light_topology"]
    assert "key" in topo
    if len(result["sources_detected"]) >= 2:
        assert "fill" in topo


# ============================================================================
# L4: CameraLayer — enhanced tests
# ============================================================================

def test_l4_coverage_pattern_close_up():
    """Coverage should be close_up_dominated when more close shots than wide."""
    layer = CameraLayer()
    shots = [
        _make_shot_dict("S1", "cu", "static", 3.0),
        _make_shot_dict("S2", "ecu", "static", 2.0),
        _make_shot_dict("S3", "mcu", "static", 3.0),
        _make_shot_dict("S4", "ls", "static", 2.0),
    ]
    result = layer.analyze({"project": None, "intent": {}, "shots": shots})
    assert result["coverage_pattern"] == "close_up_dominated"


def test_l4_coverage_pattern_wide():
    """Coverage should be wide when more wide shots."""
    layer = CameraLayer()
    shots = [
        _make_shot_dict("S1", "els", "static", 5.0),
        _make_shot_dict("S2", "ls", "static", 4.0),
        _make_shot_dict("S3", "cu", "static", 2.0),
    ]
    result = layer.analyze({"project": None, "intent": {}, "shots": shots})
    assert result["coverage_pattern"] == "wide_establishing_dominated"


def test_l4_pacing_fast():
    """Pacing should be fast when avg duration < 3s."""
    layer = CameraLayer()
    shots = [
        _make_shot_dict("S1", "cu", "static", 2.0),
        _make_shot_dict("S2", "cu", "static", 2.0),
    ]
    result = layer.analyze({"project": None, "intent": {}, "shots": shots})
    assert result["pacing"] == "fast"


def test_l4_pacing_slow():
    """Pacing should be slow when avg duration > 6s."""
    layer = CameraLayer()
    shots = [
        _make_shot_dict("S1", "ls", "static", 8.0),
    ]
    result = layer.analyze({"project": None, "intent": {}, "shots": shots})
    assert result["pacing"] == "slow"


def test_l4_summary_format():
    """Storyboard summary should contain arrow separators."""
    layer = CameraLayer()
    shots = [
        _make_shot_dict("S1", "ls", "dolly_in", 5.0),
        _make_shot_dict("S2", "cu", "static", 3.0),
    ]
    result = layer.analyze({"project": None, "intent": {}, "shots": shots})
    assert "ls+dolly_in" in result["storyboard_summary"]
    assert "\u2192" in result["storyboard_summary"]


def test_l4_tension_mapping():
    """Movement should map to tension values."""
    layer = CameraLayer()
    shots = [
        _make_shot_dict("S1", "ms", "handheld", 4.0),
        _make_shot_dict("S2", "cu", "dolly_in", 3.0),
    ]
    result = layer.analyze({"project": None, "intent": {}, "shots": shots})
    assert result["shot_sequence"][0]["tension"] == "unstable"
    assert result["shot_sequence"][1]["tension"] == "intensifying"


# ============================================================================
# L5: CharacterLayer — enhanced tests
# ============================================================================

def test_l5_main_and_supporting():
    """Should separate main from supporting characters."""
    layer = CharacterLayer()
    project = Project(
        characters=[
            Character(id="c1", name="Hero", role="protagonist",
                      visual_identity=VisualIdentity(appearance="tall")),
            Character(id="c2", name="Villain", role="antagonist",
                      visual_identity=VisualIdentity(appearance="dark")),
        ],
    )
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    assert result["character_count"] == 2
    assert result["main_character"]["id"] == "c1"
    assert len(result["supporting_characters"]) == 1


def test_l5_no_characters():
    """Should handle empty character list gracefully."""
    layer = CharacterLayer()
    project = Project()
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    assert result["character_count"] == 0
    assert result["main_character"] == {}


def test_l5_presence_in_shots():
    """Should map which shots each character appears in."""
    layer = CharacterLayer()
    project = Project(
        characters=[
            Character(id="c1", name="Alice", role="protagonist"),
            Character(id="c2", name="Bob", role="supporting"),
        ],
    )
    shots = [
        _make_shot_dict("S1", action="Alice walks in"),
        _make_shot_dict("S2", action="Bob reacts"),
    ]
    result = layer.analyze({"project": project, "intent": {}, "shots": shots})
    presence = result["presence_in_shots"]
    assert len(presence) == 2
    assert presence[0]["character"] == "c1"
    assert presence[1]["character"] == "c2"


def test_l5_differentiation_keys():
    """Differentiation should contain visual keys per character."""
    layer = CharacterLayer()
    project = Project(
        characters=[
            Character(id="c1", name="Hero", role="protagonist",
                      visual_identity=VisualIdentity(appearance="scarred", clothing="armor")),
        ],
    )
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    diff = result["differentiation"]
    assert len(diff) == 1
    assert "armor" in diff[0]["visual_key"]


# ============================================================================
# L6: MicroTextureLayer — new tests
# ============================================================================

def test_l6_detects_pore_detail():
    """Should detect pore-level skin detail keywords."""
    layer = MicroTextureLayer()
    project = Project(
        visual_language=VisualLanguage(texture="\u6bdb\u5b54visible"),
    )
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    assert result["has_pore_detail"] is True
    assert "\u6bdb\u5b54" in result["texture_features"]


def test_l6_detects_fabric_texture():
    """Should detect fabric-related texture keywords."""
    layer = MicroTextureLayer()
    project = Project(
        visual_language=VisualLanguage(texture="\u4e1d\u7ef8\u5e03\u6599"),
    )
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    assert result["has_clothing_texture"] is True


def test_l6_detects_optical_features():
    """Should detect optical keywords like lens artifacts."""
    layer = MicroTextureLayer()
    project = Project(
        visual_language=VisualLanguage(texture="\u6563\u666f \u7729\u5149"),
    )
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    assert "\u6563\u666f" in result["optical_features"]
    assert "\u7729\u5149" in result["optical_features"]


def test_l6_quality_specs_from_render_settings():
    """Quality specs should be parsed from comma-separated render_settings."""
    layer = MicroTextureLayer()
    project = Project(
        visual_language=VisualLanguage(render_settings="8K\uff0c\u5168\u5c40\u5149\u7167\uff0csubsurface scattering"),
    )
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    assert len(result["quality_specifications"]) >= 2


def test_l6_no_texture_features():
    """Empty project should produce empty texture results."""
    layer = MicroTextureLayer()
    project = Project()
    result = layer.analyze({"project": project, "intent": {}, "shots": []})
    assert result["texture_features"] == {}
    assert result["optical_features"] == {}
    assert result["has_pore_detail"] is False
