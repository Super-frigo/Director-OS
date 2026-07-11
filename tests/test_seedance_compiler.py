"""Tests for the Seedance Compiler — deterministic, four-stage pipeline.

Key test: run compile_project() twice on the same input and assert byte-identical output.
This is the core guarantee that the compiler is deterministic.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from compilers.seedance.compile import (
    compile_project,
    project_reader,
    context_builder,
    platform_adapter,
    prompt_assembler,
    CompileContext,
    CompileResult,
    CompileError,
    PlatformPromptParts,
    ShotPromptPart,
    StoryContext,
    VisualContext,
    CharacterContext,
    WorldContext,
    OutputContext,
)
from compilers.seedance.rules import (
    FRAMING_MAP,
    ANGLE_MAP,
    LENS_MAP,
    MOVEMENT_MAP,
    FOCUS_MAP,
    TRANSITION_MAP,
    lookup,
    lookup_composition,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def hanging_path() -> Path:
    """Path to the_hanging.md test project."""
    p = ROOT / "projects" / "the_hanging.md"
    assert p.exists(), f"Test project not found: {p}"
    return p


@pytest.fixture
def compile_result(hanging_path: Path) -> CompileResult:
    """Compile the_hanging.md once, shared across tests."""
    return compile_project(hanging_path)


# ============================================================================
# Determinism test — the core requirement
# ============================================================================

def test_determinism_two_runs(hanging_path: Path):
    """Run compiler twice on same input and assert byte-identical output.

    This is the primary test.  A non-deterministic compiler would produce
    different prompts on each run due to hash ordering, set iteration, or
    non-deterministic algorithm choices.  This test catches all of those.
    """
    r1 = compile_project(hanging_path)
    r2 = compile_project(hanging_path)

    assert r1.success, f"Run 1 failed: {r1.errors}"
    assert r2.success, f"Run 2 failed: {r2.errors}"
    assert r1.prompt == r2.prompt, (
        f"Determinism FAILED: outputs differ.\n"
        f"Run1 length={len(r1.prompt)}, Run2 length={len(r2.prompt)}"
    )


def test_determinism_three_runs(hanging_path: Path):
    """Triple-run determinism — catches odd/even cycle bugs."""
    r1 = compile_project(hanging_path)
    r2 = compile_project(hanging_path)
    r3 = compile_project(hanging_path)

    assert r1.prompt == r2.prompt == r3.prompt


# ============================================================================
# Stage 1: Project Reader tests
# ============================================================================

def test_project_reader_success(hanging_path: Path):
    """Valid project should pass validation with no errors."""
    project, errors = project_reader(hanging_path)
    assert project is not None
    error_errors = [e for e in errors if e.severity == "error"]
    assert len(error_errors) == 0, f"Unexpected errors: {error_errors}"


def test_project_reader_has_required_modules(hanging_path: Path):
    """Parsed project must contain all required top-level modules."""
    project, _ = project_reader(hanging_path)
    required = {"metadata", "creative", "story", "characters", "world",
                "visual_language", "story_beats", "shots"}
    for mod in required:
        assert mod in project, f"Missing module: {mod}"


def test_project_reader_rejects_missing_file():
    """Non-existent file should return error."""
    project, errors = project_reader(Path("/nonexistent/project.md"))
    assert project is None
    assert len(errors) > 0


def test_project_reader_detects_missing_beats():
    """Project with zero beats should fail validation."""
    from unittest.mock import patch
    import compilers.seedance.compile as mod

    fake_data = {
        "metadata": {"title": "Test", "status": "Ready"},
        "creative": {"genre": "Test"},
        "story": {"premise": "A test"},
        "characters": [{"id": "c1", "role": "hero"}],
        "world": {},
        "visual_language": {},
        "story_beats": [],
        "shots": [{
            "shot_id": "S1", "duration": 5, "framing": "MS",
            "lens": "50mm", "movement": "STATIC",
        }],
    }
    with patch.object(mod, '_load_project_yaml', return_value=fake_data):
        project, errors = mod.project_reader(Path("fake.md"))
    error_msgs = [e.message for e in errors if e.severity == "error"]
    assert any("story beat" in m.lower() for m in error_msgs)


def test_project_reader_detects_missing_shots():
    """Project with zero shots should fail validation."""
    from unittest.mock import patch
    import compilers.seedance.compile as mod

    fake_data = {
        "metadata": {"title": "Test", "status": "Ready"},
        "creative": {"genre": "Test"},
        "story": {"premise": "A test"},
        "characters": [{"id": "c1", "role": "hero"}],
        "world": {},
        "visual_language": {},
        "story_beats": [{"beat": "B1", "type": "OPENING"}],
        "shots": [],
    }
    with patch.object(mod, '_load_project_yaml', return_value=fake_data):
        project, errors = mod.project_reader(Path("fake.md"))
    error_msgs = [e.message for e in errors if e.severity == "error"]
    assert any("shot" in m.lower() for m in error_msgs)


# ============================================================================
# Stage 2: Context Builder tests
# ============================================================================

def test_context_builder_populates_all_contexts(hanging_path: Path):
    """Context builder must populate all five sub-contexts."""
    project, errors = project_reader(hanging_path)
    assert not [e for e in errors if e.severity == "error"]
    ctx = context_builder(project)

    assert isinstance(ctx.story_context, StoryContext)
    assert isinstance(ctx.visual_context, VisualContext)
    assert isinstance(ctx.character_context, CharacterContext)
    assert isinstance(ctx.world_context, WorldContext)
    assert isinstance(ctx.output_context, OutputContext)

    assert len(ctx.story_context.beats) >= 1
    assert len(ctx.visual_context.shots) >= 1
    assert len(ctx.character_context.characters) >= 1


def test_context_builder_output_parsing(hanging_path: Path):
    """Output context should parse duration, aspect_ratio, fps, resolution."""
    project, errors = project_reader(hanging_path)
    ctx = context_builder(project)

    assert ctx.output_context.duration == 15.0
    assert ctx.output_context.aspect_ratio == "16:9"
    assert ctx.output_context.fps == 24
    assert ctx.output_context.resolution == "1080p"


def test_context_builder_world_fields(hanging_path: Path):
    """World context should have era, location, weather populated."""
    project, errors = project_reader(hanging_path)
    ctx = context_builder(project)

    assert ctx.world_context.era
    assert "1930" in ctx.world_context.era
    assert ctx.world_context.weather


# ============================================================================
# Stage 3: Platform Adapter tests
# ============================================================================

def test_platform_adapter_produces_shot_parts(hanging_path: Path):
    """Platform adapter must produce one ShotPromptPart per shot."""
    project, _ = project_reader(hanging_path)
    ctx = context_builder(project)
    parts = platform_adapter(ctx)

    assert len(parts.shots) == len(ctx.visual_context.shots)
    for sp in parts.shots:
        assert isinstance(sp, ShotPromptPart)
        assert sp.shot_id
        assert sp.duration > 0


def test_platform_adapter_global_settings(hanging_path: Path):
    """Global settings should include style and output specs."""
    project, _ = project_reader(hanging_path)
    ctx = context_builder(project)
    parts = platform_adapter(ctx)

    assert any("Style:" in g for g in parts.global_settings)
    assert any("Output:" in g for g in parts.global_settings)


def test_platform_adapter_character_contexts(hanging_path: Path):
    """Character contexts should describe each character."""
    project, _ = project_reader(hanging_path)
    ctx = context_builder(project)
    parts = platform_adapter(ctx)

    assert len(parts.character_contexts) == len(ctx.character_context.characters)


def test_platform_adapter_warns_many_characters():
    """Should warn when >2 characters."""
    ctx = CompileContext()
    ctx.character_context.characters = [
        {"id": "c1"}, {"id": "c2"}, {"id": "c3"},
    ]
    ctx.visual_context.shots = [{"shot_id": "S1", "order": 1, "duration": 5}]
    ctx.project = {}
    parts = platform_adapter(ctx)
    assert any("3 characters" in w for w in parts.warnings)


def test_platform_adapter_warns_long_duration():
    """Should warn when duration > 15s."""
    ctx = CompileContext()
    ctx.output_context.duration = 20.0
    ctx.visual_context.shots = [{"shot_id": "S1", "order": 1, "duration": 20}]
    ctx.character_context.characters = [{"id": "c1"}]
    ctx.project = {}
    parts = platform_adapter(ctx)
    assert any("20" in w and "15s" in w for w in parts.warnings)


# ============================================================================
# Stage 4: Prompt Assembler tests
# ============================================================================

def test_prompt_assembler_idempotent():
    """Assembling the same parts twice should produce identical output."""
    parts = PlatformPromptParts(
        global_settings=["Style: Test."],
        shots=[
            ShotPromptPart(shot_id="S1", order=1, duration=3.0,
                           desc_lines=["Wide shot. A test."]),
        ],
    )
    p1 = prompt_assembler(parts)
    p2 = prompt_assembler(parts)
    assert p1 == p2


def test_prompt_assembler_includes_all_sections(hanging_path: Path):
    """Assembled prompt should contain all expected sections."""
    project, _ = project_reader(hanging_path)
    ctx = context_builder(project)
    parts = platform_adapter(ctx)
    prompt = prompt_assembler(parts)

    assert "=== Seedance Prompt ===" in prompt
    assert "## Global Settings" in prompt
    assert "## Characters" in prompt
    assert "## Shot List" in prompt
    assert "## Audio Design" in prompt
    assert "## Tone & Theme" in prompt


def test_prompt_assembler_shots_in_order(hanging_path: Path):
    """Shots should appear in numeric order, not insertion order."""
    project, _ = project_reader(hanging_path)
    ctx = context_builder(project)
    parts = platform_adapter(ctx)
    prompt = prompt_assembler(parts)

    # Find positions of "### Shot N:" lines
    import re
    shot_lines = re.findall(r"### Shot (\d+):", prompt)
    orders = [int(n) for n in shot_lines]
    assert orders == sorted(orders), f"Shots out of order: {orders}"


# ============================================================================
# CompileResult tests
# ============================================================================

def test_compile_result_success(hanging_path: Path):
    """compile_project should return success=True for valid project."""
    result = compile_project(hanging_path)
    assert result.success
    assert result.prompt
    assert "shots_compiled" in result.stats
    assert result.stats["shots_compiled"] == 4


def test_compile_result_stats(hanging_path: Path):
    """Stats should reflect actual project dimensions."""
    result = compile_project(hanging_path)
    assert result.stats["duration_seconds"] == 15.0
    assert result.stats["tokens_estimated"] > 0


# ============================================================================
# Rules tests — verify no TODOs or placeholders
# ============================================================================

def test_rules_no_todos():
    """Every translation map value must be a real string, not a TODO placeholder."""
    all_maps = [
        ("FRAMING_MAP", FRAMING_MAP),
        ("ANGLE_MAP", ANGLE_MAP),
        ("LENS_MAP", LENS_MAP),
        ("MOVEMENT_MAP", MOVEMENT_MAP),
        ("FOCUS_MAP", FOCUS_MAP),
        ("TRANSITION_MAP", TRANSITION_MAP),
    ]
    for name, table in all_maps:
        for key, value in table.items():
            assert value, f"{name}[{key!r}] has empty value"
            assert "TODO" not in value.upper(), (
                f"{name}[{key!r}] contains TODO: {value!r}"
            )
            assert "TBD" not in value.upper(), (
                f"{name}[{key!r}] contains TBD: {value!r}"
            )


def test_rules_framing_coverage():
    """Every valid framing from the schema must have a mapping."""
    from schemas.project_schema import VALID_FRAMING
    for f in VALID_FRAMING:
        result = lookup(FRAMING_MAP, f)
        assert result, f"FRAMING_MAP missing entry for '{f}'"


def test_rules_lens_coverage():
    """Every valid lens from the schema must have a mapping."""
    from schemas.project_schema import VALID_LENS
    for l in VALID_LENS:
        result = lookup(LENS_MAP, l)
        assert result, f"LENS_MAP missing entry for '{l}'"


def test_rules_movement_coverage():
    """Every valid movement from the schema must have a mapping."""
    from schemas.project_schema import VALID_MOVEMENT
    for m in VALID_MOVEMENT:
        result = lookup(MOVEMENT_MAP, m)
        assert result, f"MOVEMENT_MAP missing entry for '{m}'"


def test_rules_transition_coverage():
    """Every valid transition from the schema must have a mapping."""
    from schemas.project_schema import VALID_TRANSITION
    for t in VALID_TRANSITION:
        result = lookup(TRANSITION_MAP, t)
        assert result, f"TRANSITION_MAP missing entry for '{t}'"


def test_rules_focus_coverage():
    """Every valid focus from the schema must have a mapping."""
    from schemas.project_schema import VALID_FOCUS
    for f in VALID_FOCUS:
        result = lookup(FOCUS_MAP, f)
        assert result, f"FOCUS_MAP missing entry for '{f}'"


def test_rules_angle_coverage():
    """Every valid angle from the schema must have a mapping."""
    from schemas.project_schema import VALID_ANGLE
    for a in VALID_ANGLE:
        result = lookup(ANGLE_MAP, a)
        assert result, f"ANGLE_MAP missing entry for '{a}'"


def test_lookup_composition_compound():
    """Compound composition rules should be resolved correctly."""
    result = lookup_composition("RULE_OF_THIRDS + LEADING_LINES")
    assert "rule of thirds" in result
    assert "leading lines" in result


def test_lookup_empty_returns_empty():
    """Empty or None keys should return empty string, not crash."""
    assert lookup(FRAMING_MAP, "") == ""
    assert lookup(FRAMING_MAP, None) == ""
    assert lookup_composition("") == ""
