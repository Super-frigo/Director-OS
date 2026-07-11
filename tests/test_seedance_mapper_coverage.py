"""Tests for Seedance mapper — schema coverage, determinism, and zero-placeholders.

These tests verify that the merged mapper (director_os/compilers/seedance/mapper.py)
covers every schema enum value defined in schemas/project_schema.py, contains no
TODO/TBD placeholders, and that the SeedanceCompiler produces deterministic output.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from director_os.compilers.seedance.compiler import SeedanceCompiler
from director_os.compilers.seedance.mapper import (
    SEEDANCE_FRAMING_MAP,
    SEEDANCE_ANGLE_MAP,
    SEEDANCE_HEIGHT_MAP,
    SEEDANCE_LENS_MAP,
    SEEDANCE_CAMERA_MAP,
    SEEDANCE_FOCUS_MAP,
    SEEDANCE_LIGHTING_TYPE_MAP,
    SEEDANCE_LIGHTING_POSITION_MAP,
    SEEDANCE_COLOR_TEMP_MAP,
    SEEDANCE_COMPOSITION_MAP,
    SEEDANCE_TRANSITION_MAP,
    SEEDANCE_BEAT_TYPE_MAP,
    SEEDANCE_APERTURE_MAP,
    _lookup,
)

from schemas.project_schema import (
    VALID_FRAMING,
    VALID_ANGLE,
    VALID_HEIGHT,
    VALID_LENS,
    VALID_MOVEMENT,
    VALID_FOCUS,
    VALID_LIGHT_TYPE,
    VALID_LIGHT_POSITION,
    VALID_COLOR_TEMP,
    VALID_COMPOSITION_RULE,
    VALID_TRANSITION,
    VALID_BEAT_TYPE,
    VALID_APERTURE,
)


# ============================================================================
# Fixtures
# ============================================================================

def _sample_intent() -> dict:
    """A minimal but complete production intent for determinism testing."""
    return {
        "creative_goal": {"primary": "A romantic meeting"},
        "visual_direction": {
            "style": "Romantic",
            "mood": ["warm", "dreamy"],
            "composition": "medium shot",
            "color": "warm tones",
            "texture": "film grain",
            "atmosphere": "romantic",
            "lighting": "soft golden",
            "camera_body": "ARRI Alexa65",
            "lens_character": "",
            "film_stock": "Kodak Portra 400",
            "color_grade": "",
            "render_engine": "",
            "render_settings": "",
        },
        "camera_strategy": {
            "framing": "ms",
            "movement": "slow_push",
            "perspective": "eye_level",
            "lens_character": "50mm",
            "focus_behavior": "",
        },
        "character_direction": [
            {"id": "heroine", "name": "Alice", "action": "descends staircase",
             "performance": "elegant", "emotional_state": ""},
        ],
        "narrative_intent": {
            "premise": "Alice walks down a grand staircase to meet her lover",
        },
        "temporal_design": {"pacing": "slow", "motion_style": "fluid", "duration": "15s"},
        "constraints": {},
        "environment_direction": {},
        "audio_intent": {},
        "consistency_requirements": {},
        "target_model": "seedance-v1",
    }


# ============================================================================
# Determinism tests — SeedanceCompiler
# ============================================================================

def test_determinism_two_runs():
    """Run SeedanceCompiler.compile() twice on same intent — byte-identical output."""
    compiler = SeedanceCompiler()
    r1 = compiler.compile(_sample_intent())
    r2 = compiler.compile(_sample_intent())

    p1 = r1["execution_package"]["instructions"]["prompt"]
    p2 = r2["execution_package"]["instructions"]["prompt"]

    assert p1, "Run 1 produced empty prompt"
    assert p1 == p2, (
        f"Determinism FAILED: outputs differ.\n"
        f"Run1 length={len(p1)}, Run2 length={len(p2)}"
    )


def test_determinism_three_runs():
    """Triple-run determinism — catches odd/even cycle bugs."""
    compiler = SeedanceCompiler()
    r1 = compiler.compile(_sample_intent())
    r2 = compiler.compile(_sample_intent())
    r3 = compiler.compile(_sample_intent())

    p1 = r1["execution_package"]["instructions"]["prompt"]
    p2 = r2["execution_package"]["instructions"]["prompt"]
    p3 = r3["execution_package"]["instructions"]["prompt"]

    assert p1 == p2 == p3


def test_determinism_with_layers():
    """compile_with_layers() must also be deterministic."""
    compiler = SeedanceCompiler()
    layers = {
        "l1_baseline": {"style_anchor": "Romantic", "resolution": "4K"},
        "l4_camera": {"storyboard_summary": "ms+slow_push"},
    }
    r1 = compiler.compile_with_layers(_sample_intent(), layers)
    r2 = compiler.compile_with_layers(_sample_intent(), layers)

    p1 = r1["execution_package"]["instructions"]["prompt"]
    p2 = r2["execution_package"]["instructions"]["prompt"]
    assert p1 == p2


# ============================================================================
# No-TODO tests — every map value must be a real string
# ============================================================================

ALL_SCHEMA_MAPS = [
    ("SEEDANCE_FRAMING_MAP", SEEDANCE_FRAMING_MAP),
    ("SEEDANCE_ANGLE_MAP", SEEDANCE_ANGLE_MAP),
    ("SEEDANCE_HEIGHT_MAP", SEEDANCE_HEIGHT_MAP),
    ("SEEDANCE_LENS_MAP", SEEDANCE_LENS_MAP),
    ("SEEDANCE_CAMERA_MAP", SEEDANCE_CAMERA_MAP),
    ("SEEDANCE_FOCUS_MAP", SEEDANCE_FOCUS_MAP),
    ("SEEDANCE_LIGHTING_TYPE_MAP", SEEDANCE_LIGHTING_TYPE_MAP),
    ("SEEDANCE_LIGHTING_POSITION_MAP", SEEDANCE_LIGHTING_POSITION_MAP),
    ("SEEDANCE_COLOR_TEMP_MAP", SEEDANCE_COLOR_TEMP_MAP),
    ("SEEDANCE_COMPOSITION_MAP", SEEDANCE_COMPOSITION_MAP),
    ("SEEDANCE_TRANSITION_MAP", SEEDANCE_TRANSITION_MAP),
    ("SEEDANCE_BEAT_TYPE_MAP", SEEDANCE_BEAT_TYPE_MAP),
    ("SEEDANCE_APERTURE_MAP", SEEDANCE_APERTURE_MAP),
]


def test_rules_no_todos():
    """Every translation map value must be a real string, not a TODO/TBD placeholder."""
    for name, table in ALL_SCHEMA_MAPS:
        for key, value in table.items():
            assert value, f"{name}[{key!r}] has empty value"
            assert "TODO" not in value.upper(), (
                f"{name}[{key!r}] contains TODO: {value!r}"
            )
            assert "TBD" not in value.upper(), (
                f"{name}[{key!r}] contains TBD: {value!r}"
            )


# ============================================================================
# Schema coverage tests — every VALID_* enum must map to a non-empty string
# ============================================================================

def test_rules_framing_coverage():
    """Every VALID_FRAMING value must produce a non-empty mapping via _lookup."""
    for f in VALID_FRAMING:
        result = _lookup(SEEDANCE_FRAMING_MAP, f)
        assert result, f"SEEDANCE_FRAMING_MAP missing or empty entry for '{f}'"


def test_rules_angle_coverage():
    """Every VALID_ANGLE value must produce a non-empty mapping."""
    for a in VALID_ANGLE:
        result = _lookup(SEEDANCE_ANGLE_MAP, a)
        assert result, f"SEEDANCE_ANGLE_MAP missing or empty entry for '{a}'"


def test_rules_height_coverage():
    """Every VALID_HEIGHT value must produce a non-empty mapping."""
    for h in VALID_HEIGHT:
        result = _lookup(SEEDANCE_HEIGHT_MAP, h)
        assert result, f"SEEDANCE_HEIGHT_MAP missing or empty entry for '{h}'"


def test_rules_lens_coverage():
    """Every VALID_LENS value must produce a non-empty mapping."""
    for l in VALID_LENS:
        result = _lookup(SEEDANCE_LENS_MAP, l)
        assert result, f"SEEDANCE_LENS_MAP missing or empty entry for '{l}'"


def test_rules_movement_coverage():
    """Every VALID_MOVEMENT value must produce a non-empty mapping."""
    for m in VALID_MOVEMENT:
        result = _lookup(SEEDANCE_CAMERA_MAP, m)
        assert result, f"SEEDANCE_CAMERA_MAP missing or empty entry for '{m}'"


def test_rules_focus_coverage():
    """Every VALID_FOCUS value must produce a non-empty mapping."""
    for f in VALID_FOCUS:
        result = _lookup(SEEDANCE_FOCUS_MAP, f)
        assert result, f"SEEDANCE_FOCUS_MAP missing or empty entry for '{f}'"


def test_rules_lighting_type_coverage():
    """Every VALID_LIGHT_TYPE value must produce a non-empty mapping."""
    for lt in VALID_LIGHT_TYPE:
        result = _lookup(SEEDANCE_LIGHTING_TYPE_MAP, lt)
        assert result, f"SEEDANCE_LIGHTING_TYPE_MAP missing or empty entry for '{lt}'"


def test_rules_lighting_position_coverage():
    """Every VALID_LIGHT_POSITION value must produce a non-empty mapping."""
    for lp in VALID_LIGHT_POSITION:
        result = _lookup(SEEDANCE_LIGHTING_POSITION_MAP, lp)
        assert result, f"SEEDANCE_LIGHTING_POSITION_MAP missing or empty entry for '{lp}'"


def test_rules_color_temp_coverage():
    """Every VALID_COLOR_TEMP value must produce a non-empty mapping."""
    for ct in VALID_COLOR_TEMP:
        result = _lookup(SEEDANCE_COLOR_TEMP_MAP, ct)
        assert result, f"SEEDANCE_COLOR_TEMP_MAP missing or empty entry for '{ct}'"


def test_rules_composition_coverage():
    """Every VALID_COMPOSITION_RULE value must produce a non-empty mapping."""
    for cr in VALID_COMPOSITION_RULE:
        result = SEEDANCE_COMPOSITION_MAP.get(cr, "")
        assert result, f"SEEDANCE_COMPOSITION_MAP missing or empty entry for '{cr}'"


def test_rules_transition_coverage():
    """Every VALID_TRANSITION value must produce a non-empty mapping."""
    for t in VALID_TRANSITION:
        result = _lookup(SEEDANCE_TRANSITION_MAP, t)
        assert result, f"SEEDANCE_TRANSITION_MAP missing or empty entry for '{t}'"


def test_rules_beat_type_coverage():
    """Every VALID_BEAT_TYPE value must produce a non-empty mapping."""
    for bt in VALID_BEAT_TYPE:
        result = _lookup(SEEDANCE_BEAT_TYPE_MAP, bt)
        assert result, f"SEEDANCE_BEAT_TYPE_MAP missing or empty entry for '{bt}'"


def test_rules_aperture_coverage():
    """Every VALID_APERTURE value must produce a non-empty mapping."""
    for ap in VALID_APERTURE:
        result = _lookup(SEEDANCE_APERTURE_MAP, ap)
        assert result, f"SEEDANCE_APERTURE_MAP missing or empty entry for '{ap}'"
