"""Load Director OS project YAML files into Python models."""

from pathlib import Path
import re

from .models.project import (
    Project, Metadata, Creative, Story, StoryBeat, World, Location,
    Character, VisualIdentity, Scene, Shot, Subject,
    LightingSetup, ShotColor, ShotAudio, EmotionTarget,
    VisualLanguage, AudioDesign, ProductionDesign, Continuity,
    Constraints, OutputProfile, HistoryEntry,
)


def _load_yaml_with_markdown(path: Path) -> dict:
    """Load a project file that mixes markdown headers with YAML blocks."""
    import yaml
    raw = path.read_text(encoding="utf-8-sig")
    cleaned_lines = []
    for line in raw.splitlines():
        if re.match(r"^#{2,}\\s+", line):
            continue
        if line.strip() == "---":
            continue
        cleaned_lines.append(line)
    clean_text = "\n".join(cleaned_lines)
    data = yaml.safe_load(clean_text)
    return data if isinstance(data, dict) else {}


def load_project(path: str | Path) -> Project:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Project file not found: {path}")
    try:
        data = _load_yaml_with_markdown(path)
    except ImportError:
        raise ImportError("PyYAML is required. Install with: pip install pyyaml")

    raw = data.get("project", data) if isinstance(data, dict) else {}

    project = Project(
        schema_version=raw.get("schema_version", "1.0"),
        metadata=_meta(raw.get("metadata", {})),
        creative=_creative(raw.get("creative", {})),
        story=_story(raw.get("story", {})),
        world=_world(raw.get("world", {})),
        characters=[_char(c) for c in raw.get("characters", [])],
        scenes=[_scene(s) for s in raw.get("scenes", [])],
        shots=[_shot(s) for s in raw.get("shots", [])],
        visual_language=_vl(raw.get("visual_language", raw.get("visual", {}))),
        audio=_audio(raw.get("audio", {})),
        production=_production(raw.get("production", {})),
        continuity=_continuity(raw.get("continuity", {})),
        constraints=_constraints(raw.get("constraints", {})),
        output_profile=_output(raw.get("output", {})),
        history=[_history(h) for h in raw.get("history", [])],
        story_beats=[_beat(b) for b in raw.get("story_beats", [])],
        production_intent=_production(raw.get("production_intent", {})),
    )
    return project


# ?? individual section mappers ??????????????????????????????????????

def _meta(d: dict) -> Metadata:
    return Metadata(
        id=d.get("id", ""),
        title=d.get("title", ""),
        subtitle=d.get("subtitle", ""),
        description=d.get("description", ""),
        author=d.get("author", ""),
        version=d.get("version", "0.1.0"),
        status=d.get("status", "Idea"),
        created_at=d.get("created_at", ""),
        updated_at=d.get("updated_at", ""),
        language=d.get("language", "zh-CN"),
    )


def _creative(d: dict) -> Creative:
    return Creative(
        objective=d.get("objective", ""),
        audience=d.get("audience", ""),
        genre=d.get("genre", ""),
        subgenre=d.get("subgenre", ""),
        tone=d.get("tone", ""),
        pacing=d.get("pacing", ""),
        emotional_arc=d.get("emotional_arc", ""),
        realism=d.get("realism", ""),
        visual_priority=d.get("visual_priority", 5),
        dialogue_priority=d.get("dialogue_priority", 5),
        action_priority=d.get("action_priority", 5),
        references=d.get("references", {}),
    )


def _story(d: dict) -> Story:
    return Story(
        premise=d.get("premise", ""),
        theme=d.get("theme", []),
        genre=d.get("genre", []),
        structure=d.get("structure", {"acts": []}),
    )


def _beat(d: dict) -> StoryBeat:
    return StoryBeat(
        beat=d.get("beat", ""),
        type=d.get("type", ""),
        objective=d.get("objective", ""),
        emotion=d.get("emotion", ""),
        transition=d.get("transition", ""),
        duration_ratio=d.get("duration_ratio", 0.0),
        characters=d.get("characters", []),
        location=d.get("location", ""),
        dialogue=d.get("dialogue", False),
        mood=d.get("mood", ""),
        notes=d.get("notes", ""),
    )


def _world(d: dict) -> World:
    locs = []
    for ld in d.get("locations", []):
        locs.append(Location(
            id=ld.get("id", ""),
            name=ld.get("name", ""),
            description=ld.get("description", ""),
            atmosphere=ld.get("atmosphere", ""),
            visual_identity=ld.get("visual_identity", ""),
        ))
    return World(
        timeline=d.get("timeline", ""),
        era=d.get("era", ""),
        location=d.get("location", ""),
        architecture=d.get("architecture", ""),
        climate=d.get("climate", ""),
        weather=d.get("weather", ""),
        season=d.get("season", ""),
        culture=d.get("culture", ""),
        technology=d.get("technology", ""),
        society=d.get("society", ""),
        locations=locs,
    )


def _char(d: dict) -> Character:
    vi = d.get("visual_identity", {})
    return Character(
        id=d.get("id", ""),
        name=d.get("name", ""),
        role=d.get("role", ""),
        age=str(d.get("age", "")),
        gender=d.get("gender", ""),
        ethnicity=d.get("ethnicity", ""),
        appearance=d.get("appearance", ""),
        wardrobe=d.get("wardrobe", ""),
        accessories=d.get("accessories", ""),
        personality=d.get("personality", []),
        motivation=str(d.get("motivation", "")),
        physical_state=d.get("physical_state", ""),
        continuity_lock=d.get("continuity_lock", False),
        visual_identity=VisualIdentity(
            age_range=vi.get("age_range", ""),
            appearance=vi.get("appearance", ""),
            clothing=vi.get("clothing", ""),
            accessories=vi.get("accessories", ""),
        ),
    )


def _shot(d: dict) -> Shot:
    subj = d.get("subject", {})
    cam = d.get("camera", {})
    lt = d.get("lighting", {})
    co = d.get("color", {})
    aud = d.get("audio", {})
    emo = d.get("emotion", {})

    return Shot(
        shot_id=d.get("shot_id", d.get("id", "")),
        beat_ref=d.get("beat_ref", d.get("beat", "")),
        order=d.get("order", 1),
        duration=float(d.get("duration", d.get("duration", 0))),
        subject=Subject(
            character=subj.get("character", ""),
            action=subj.get("action", ""),
            position=subj.get("position", ""),
            state=subj.get("state", ""),
        ),
        framing=cam.get("framing", ""),
        angle=cam.get("angle", cam.get("angle", "")),
        height=cam.get("height", ""),
        lens=cam.get("lens", ""),
        movement=cam.get("movement", ""),
        focus=cam.get("focus", ""),
        aperture=cam.get("aperture", ""),
        composition=d.get("composition", {}),
        lighting=LightingSetup.from_dict(lt),
        color=ShotColor(
            palette=co.get("palette", ""),
            accent=co.get("accent", ""),
            contrast=co.get("contrast", ""),
        ),
        audio=ShotAudio(
            silence=aud.get("silence", False),
            dialogue=aud.get("dialogue", ""),
            ambience=aud.get("ambience", ""),
            sound_effects=aud.get("sound_effects", ""),
            music=aud.get("music", ""),
        ),
        transition_in=d.get("transition_in", ""),
        transition_out=d.get("transition_out", ""),
        emotion=EmotionTarget(
            target=emo.get("target", ""),
            intensity=emo.get("intensity", 5),
        ),
        notes=d.get("notes", ""),
        camera_raw=cam,
    )


def _scene(d: dict) -> Scene:
    return Scene(
        id=d.get("id", ""),
        title=d.get("title", ""),
        location=d.get("location", ""),
        time=d.get("time", ""),
        emotion=d.get("emotion", ""),
        narrative_goal=d.get("narrative_goal", ""),
        characters=d.get("characters", []),
        shots=[_shot(s) for s in d.get("shots", [])],
    )


def _vl(d: dict) -> VisualLanguage:
    return VisualLanguage(
        style=d.get("style", ""),
        color=d.get("color", {}),
        lighting=d.get("lighting", ""),
        camera_philosophy=d.get("camera_philosophy", ""),
        references=d.get("references", []),
        atmosphere=d.get("atmosphere", ""),
        texture=d.get("texture", ""),
        camera_body=d.get("camera_body", ""),
        lens_character=d.get("lens_character", ""),
        film_stock=d.get("film_stock", ""),
        color_grade=d.get("color_grade", ""),
        render_engine=d.get("render_engine", ""),
        render_settings=d.get("render_settings", ""),
    )


def _audio(d: dict) -> AudioDesign:
    return AudioDesign(
        music=d.get("music", []),
        ambience=d.get("ambience", []),
        dialogue=d.get("dialogue", ""),
        narration=d.get("narration", ""),
        sound_effects=d.get("sound_effects", []),
        silence=d.get("silence", False),
        rhythm=d.get("rhythm", ""),
    )


def _production(d: dict) -> ProductionDesign:
    return ProductionDesign(
        locations=d.get("locations", []),
        sets=d.get("sets", []),
        props=d.get("props", []),
        vehicles=d.get("vehicles", []),
        wardrobe=d.get("wardrobe", []),
        branding=d.get("branding", ""),
        vfx=d.get("vfx", ""),
    )


def _continuity(d: dict) -> Continuity:
    return Continuity(
        character=d.get("character", []),
        wardrobe=d.get("wardrobe", []),
        environment=d.get("environment", []),
        weather=d.get("weather", []),
        props=d.get("props", []),
        vehicles=d.get("vehicles", []),
        lighting=d.get("lighting", []),
        color=d.get("color", []),
        camera_language=d.get("camera_language", []),
        audio=d.get("audio", []),
    )


def _constraints(d: dict) -> Constraints:
    return Constraints(
        avoid=d.get("avoid", []),
        required=d.get("required", []),
        safety=d.get("safety", []),
        branding=d.get("branding", []),
        censorship=d.get("censorship", []),
    )


def _output(d: dict) -> OutputProfile:
    return OutputProfile(
        duration=int(d.get("duration", 0)),
        aspect_ratio=d.get("aspect_ratio", "16:9"),
        fps=int(d.get("fps", 24)),
        resolution=d.get("resolution", "1080p"),
        delivery=d.get("delivery", "digital"),
    )


def _history(d: dict) -> HistoryEntry:
    return HistoryEntry(
        version=d.get("version", ""),
        timestamp=d.get("timestamp", ""),
        author=d.get("author", ""),
        changes=d.get("changes", []),
        notes=d.get("notes", ""),
    )


