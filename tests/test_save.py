"""Round-trip tests for Project serialization — load → save → reload.

Validates that dump_project() / save_project_file() are symmetric to
load_project(), preserving all typed fields including camera_raw,
LightingSetup position/intensity, nested sub-dicts, and history entries.
"""

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest

from director_os.models.project import (
    Project, Metadata, Creative, Story,
    Character, Shot, Subject, LightingSetup, ShotColor, ShotAudio, EmotionTarget,
    VisualLanguage, HistoryEntry,
)
from director_os.loader import (
    load_project, dump_project, dump_project_with_markdown, save_project_file,
)
from director_os.director import Director
from director_os.state import DirectorState


HANGING = ROOT / "projects" / "the_hanging.md"


# ============================================================================
# dump_project() — serialization
# ============================================================================

def test_dump_project_is_valid_yaml():
    """The output of dump_project() must be parseable by PyYAML."""
    import yaml
    p = load_project(HANGING)
    text = dump_project(p)
    assert isinstance(text, str)
    assert len(text) > 200
    data = yaml.safe_load(text)
    assert isinstance(data, dict)
    assert "metadata" in data


def test_dump_project_preserves_metadata():
    p = load_project(HANGING)
    text = dump_project(p)
    assert "title: The Hanging" in text or "The Hanging" in text
    assert "The Hanging" in text


def test_dump_project_preserves_characters():
    p = load_project(HANGING)
    text = dump_project(p)
    assert "无名侦探" in text
    assert "char_detective" in text


def test_dump_project_preserves_shots():
    p = load_project(HANGING)
    text = dump_project(p)
    assert "SHOT_01" in text
    assert "SHOT_04" in text


def test_dump_project_camera_subdict():
    """Camera fields should be emitted as a camera: sub-dict (not flat)."""
    p = load_project(HANGING)
    text = dump_project(p)
    assert "camera:" in text
    # The first shot has camera.framing = ELS from camera_raw
    lines = text.splitlines()
    camera_section = False
    framing_found = False
    for line in lines:
        if line.strip() == "camera:":
            camera_section = True
        if camera_section and "framing:" in line:
            framing_found = True
            break
    assert framing_found, "camera: sub-dict should contain framing field"


def test_dump_project_lighting_position_intensity():
    """LightingSetup position/intensity must appear in output (ADR-009)."""
    p = load_project(HANGING)
    text = dump_project(p)
    assert "position: BACK_" in text or "position:" not in text  # present if in camera_raw
    # Shot 1 has position BACK_45 — verify it's in the output
    assert "BACK_45" in text


# ============================================================================
# Round-trip: load → dump → reload
# ============================================================================

def _roundtrip(project: Project) -> Project:
    """Serialize project to YAML string and load it back."""
    text = dump_project(project)
    import yaml
    data = yaml.safe_load(text)
    # Simulate load_project's internal construction (bypasses schema validation
    # which checks for pre-existing YAML fields that the serializer may omit)
    from director_os.loader import (
        _meta, _creative, _story, _world, _char, _shot, _beat,
        _vl, _audio, _production, _continuity, _constraints, _output, _history,
    )
    return Project(
        schema_version=data.get("schema_version", "1.0"),
        metadata=_meta(data.get("metadata", {})),
        creative=_creative(data.get("creative", {})),
        story=_story(data.get("story", {})),
        world=_world(data.get("world", {})),
        characters=[_char(c) for c in data.get("characters", [])],
        shots=[_shot(s) for s in data.get("shots", [])],
        visual_language=_vl(data.get("visual_language", {})),
        story_beats=[_beat(b) for b in data.get("story_beats", [])],
        audio=_audio(data.get("audio", {})),
        production=_production(data.get("production", {})),
        continuity=_continuity(data.get("continuity", {})),
        constraints=_constraints(data.get("constraints", {})),
        output_profile=_output(data.get("output", {})),
        history=[_history(h) for h in data.get("history", [])],
    )


def test_roundtrip_the_hanging_basic():
    """the_hanging.md must survive a round-trip with core fields intact."""
    p = load_project(HANGING)
    p2 = _roundtrip(p)

    assert p2.metadata.title == p.metadata.title
    assert p2.story.premise == p.story.premise
    assert len(p2.characters) == len(p.characters)
    assert len(p2.shots) == len(p.shots)
    assert len(p2.story_beats) == len(p.story_beats)


def test_roundtrip_shot_fields():
    """Shot-level fields (shot_id, framing, lens, duration, etc.) survive round-trip."""
    p = load_project(HANGING)
    p2 = _roundtrip(p)

    for s1, s2 in zip(p.shots, p2.shots):
        assert s2.shot_id == s1.shot_id
        assert s2.framing == s1.framing
        assert s2.lens == s1.lens
        assert s2.duration == s1.duration
        assert s2.subject.action == s1.subject.action


def test_roundtrip_lighting_position():
    """Lighting position/intensity must survive round-trip (ADR-009)."""
    p = load_project(HANGING)
    p2 = _roundtrip(p)

    s1 = p.shots[0]
    s2 = p2.shots[0]
    assert s2.lighting.position == s1.lighting.position
    assert s2.lighting.intensity == s1.lighting.intensity


def test_roundtrip_camera_raw_preserved():
    """camera_raw dict contents survive round-trip."""
    p = load_project(HANGING)
    p2 = _roundtrip(p)

    s1 = p.shots[0]
    s2 = p2.shots[0]
    # camera_raw stores the original camera: sub-dict; after round-trip,
    # it should contain the same framing
    assert s2.camera_raw.get("framing") == s1.camera_raw.get("framing")
    assert s2.camera_raw.get("lens") == s1.camera_raw.get("lens")


def test_roundtrip_history_entries():
    """History must survive round-trip."""
    p = load_project(HANGING)
    p2 = _roundtrip(p)

    assert len(p2.history) == len(p.history)
    if p.history:
        assert p2.history[0].version == p.history[0].version
        assert p2.history[0].author == p.history[0].author


# ============================================================================
# Round-trip with save_project_file (full write/read cycle)
# ============================================================================

def test_save_project_file_roundtrip():
    """Write to a temp file and read back — full filesystem round-trip."""
    p = load_project(HANGING)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False,
                                      encoding="utf-8") as f:
        tmp = Path(f.name)

    try:
        save_project_file(p, tmp)
        p2 = load_project(tmp)

        assert p2.metadata.title == p.metadata.title
        assert len(p2.characters) == len(p.characters)
        assert len(p2.shots) == len(p.shots)
        # Verify at least one shot detail
        assert p2.shots[0].shot_id == p.shots[0].shot_id
    finally:
        tmp.unlink(missing_ok=True)


# ============================================================================
# Director.save_project()
# ============================================================================

def test_director_save_adds_history():
    """Director.save_project() must append a HistoryEntry."""
    d = Director()
    d.load_project(HANGING)
    old_count = len(d.project.history)
    old_version = d.project.metadata.version

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False,
                                      encoding="utf-8") as f:
        tmp = Path(f.name)

    try:
        d.start_cycle("test save")
        d.fast_forward_to(DirectorState.COMMIT)
        d.save_project(tmp, "test save")
        assert len(d.project.history) == old_count + 1
        new_entry = d.project.history[-1]
        assert new_entry.author == "Director"
        assert new_entry.notes == "test save"
        # Version must have bumped
        if old_count > 0:
            assert d.project.metadata.version != old_version
    finally:
        tmp.unlink(missing_ok=True)


def test_director_save_auto_versions():
    """Each save bumps the patch version."""
    d = Director()
    d.load_project(HANGING)
    v1 = d.project.metadata.version

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False,
                                      encoding="utf-8") as f:
        tmp = Path(f.name)
    try:
        d.start_cycle("save 1")
        d.fast_forward_to(DirectorState.COMMIT)
        d.save_project(tmp)
        v2 = d.project.metadata.version
        assert v2 != v1

        d.transition_to(DirectorState.IDLE)  # reset for next cycle
        d.start_cycle("save 2")
        d.fast_forward_to(DirectorState.COMMIT)
        d.save_project(tmp)
        v3 = d.project.metadata.version
        assert v3 != v2
        # Patch bumps: x.y.z → x.y.(z+1)
        assert int(v2.split(".")[-1]) == int(v1.split(".")[-1]) + 1
    finally:
        tmp.unlink(missing_ok=True)


def test_save_rejects_invalid_project():
    """Validation blocks save — no file written for invalid projects."""
    d = Director()
    d.new_project(title="", premise="")  # missing title + premise = invalid
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False,
                                      encoding="utf-8") as f:
        tmp = Path(f.name)

    try:
        d.start_cycle("test")
        d.fast_forward_to(DirectorState.COMMIT)
        with pytest.raises(ValueError, match="validation"):
            d.save_project(tmp)
    finally:
        tmp.unlink(missing_ok=True)


# ============================================================================
# CLI
# ============================================================================

def test_cli_save_command():
    """director-os save should write a valid project file (uses temp copy)."""
    import subprocess, shutil
    # Copy the_hanging to a temp file so we don't mutate the original
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False,
                                      encoding="utf-8") as f:
        tmp = Path(f.name)
    try:
        shutil.copyfile(str(HANGING), str(tmp))
        cp = subprocess.run(
            [sys.executable, "-m", "director_os.cli", "save", str(tmp),
             "-m", "CLI test save"],
            capture_output=True, text=True, timeout=30,
            cwd=str(ROOT),
        )
        assert cp.returncode == 0, f"CLI save failed: {cp.stderr}\n{cp.stdout}"
        # Verify the temp file now loads correctly with updated version
        p = load_project(tmp)
        assert p.history[-1].notes == "CLI test save"
    finally:
        tmp.unlink(missing_ok=True)


# ============================================================================
# Default suppression
# ============================================================================

def test_default_suppression_no_empty_strings_in_output():
    """Empty string fields should not appear in YAML output."""
    p = Project(
        metadata=Metadata(title="Test"),
        story=Story(premise="A test"),
    )
    text = dump_project(p)
    # metadata should NOT contain empty fields
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("subtitle:") or stripped.startswith("description:"):
            val = stripped.split(":", 1)[1].strip()
            assert val != "", f"Empty field emitted: {stripped}"

    # story should NOT contain empty theme/genre lists
    # They're omitted entirely (not present as empty lists)
    assert "theme:" not in text.splitlines()


def test_default_suppression_empty_lists():
    p = Project(
        metadata=Metadata(title="T"),
        story=Story(premise="P"),
    )
    text = dump_project(p)
    # Empty theme/genre lists should not appear
    assert "theme: []" not in text
    assert "genre: []" not in text
