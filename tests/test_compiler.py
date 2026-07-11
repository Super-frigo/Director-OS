"""Unit tests for SeedanceCompiler and PromptBuilder."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from director_os.compilers.seedance.compiler import SeedanceCompiler
from director_os.compilers.seedance.prompt_builder import PromptBuilder


def _sample_intent() -> dict:
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


def test_compiler_returns_execution_package():
    compiler = SeedanceCompiler()
    result = compiler.compile(_sample_intent())

    assert "execution_package" in result
    pkg = result["execution_package"]
    assert pkg["target"]["provider"] == "seedance"
    assert "prompt" in pkg["instructions"]
    assert pkg["instructions"]["prompt"]


def test_compiler_with_layers():
    compiler = SeedanceCompiler()
    layers = {
        "l1_baseline": {"style_anchor": "Romantic", "resolution": "4K"},
        "l4_camera": {"storyboard_summary": "ms+slow_push"},
        "l6_microtexture": {"quality_specifications": ["soft lighting", "film grain"]},
    }
    result = compiler.compile_with_layers(_sample_intent(), layers)
    prompt = result["execution_package"]["instructions"]["prompt"]
    assert prompt
    assert "4K" in prompt or "视觉定位" in prompt


def test_prompt_builder_basic():
    builder = PromptBuilder()
    prompt = builder.build(_sample_intent())
    assert prompt
    assert "Alice" in prompt or "she" in prompt or "heroine" in prompt
    assert "ARRI" in prompt
    assert "slow" in prompt.lower()


def test_prompt_builder_empty_intent():
    builder = PromptBuilder()
    prompt = builder.build({})
    assert prompt == "" or prompt is not None


def test_validate_warns_long_duration():
    compiler = SeedanceCompiler()
    intent = _sample_intent()
    intent["temporal_design"]["duration"] = "20s"
    val = compiler._validate(intent)
    assert val["warnings"]
    assert any("15s" in w for w in val["warnings"])


def test_validate_warns_many_characters():
    compiler = SeedanceCompiler()
    intent = _sample_intent()
    intent["character_direction"] = [{"id": f"c{i}"} for i in range(5)]
    val = compiler._validate(intent)
    assert val["warnings"]


def test_extract_parameters():
    compiler = SeedanceCompiler()
    params = compiler._extract_parameters(_sample_intent())
    assert "camera_motion" in params
    assert "framing" in params
    assert "lens" in params
