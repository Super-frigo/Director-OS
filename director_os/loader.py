"""Load and save Director OS project YAML files.

Raises ValueError if the project file fails schema validation.
Uses schemas/project_schema.validate_yaml() as the canonical gate before
mapping to dataclass models.

Symmetric save path preserves round-trip fidelity:
- camera_raw → reconstructed camera: sub-dict
- LightingSetup → lighting: sub-dict (incl. position/intensity per ADR-009)
- Subject / ShotColor / ShotAudio / EmotionTarget → nested sub-dicts
"""

from __future__ import annotations

from pathlib import Path
import re

from schemas.project_schema import validate_yaml

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
        if re.match(r"^#{2,}\s+", line):
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

    # --- Schema validation gate ---
    validation_errors = validate_yaml(raw)
    if validation_errors:
        err_list = "\n  - ".join(validation_errors)
        raise ValueError(
            f"Project file '{path}' failed schema validation with "
            f"{len(validation_errors)} error(s):\n  - {err_list}"
        )

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


# -- individual section mappers ------------------------------------------

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
        # duration: try shot-level first, then camera sub-dict (schema accepts both)
        duration=float(d.get("duration") or cam.get("duration", 0)),
        subject=Subject(
            character=subj.get("character", ""),
            action=subj.get("action", ""),
            position=subj.get("position", ""),
            state=subj.get("state", ""),
        ),
        # Camera fields: read from camera sub-dict first, fall back to shot-level (schema accepts both)
        framing=cam.get("framing") or d.get("framing", ""),
        angle=cam.get("angle") or d.get("angle", ""),
        height=cam.get("height") or d.get("height", ""),
        lens=cam.get("lens") or d.get("lens", ""),
        movement=cam.get("movement") or d.get("movement", ""),
        focus=cam.get("focus") or d.get("focus", ""),
        aperture=cam.get("aperture") or d.get("aperture", ""),
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


# ============================================================================
# Serializer — Project → YAML (symmetric to loader above)
# ============================================================================

import yaml
from datetime import datetime, timezone


def _omit(val, default) -> bool:
    """True when *val* equals its default and can be omitted from output YAML."""
    if isinstance(default, list):
        return isinstance(val, list) and len(val) == 0
    if isinstance(default, dict):
        return isinstance(val, dict) and len(val) == 0
    if val == default:
        return True
    return False


def _omit_empty_str(val: str) -> bool:
    return val == ""


def _omit_zero(val) -> bool:
    return val == 0 or val == 0.0


def _serialize_dict(d: dict[str, str]) -> dict[str, str] | None:
    """Filter: omit entries whose value is an empty string."""
    out = {k: v for k, v in d.items() if not _omit_empty_str(v)}
    return out if out else None


def _serialize_lighting(lt: LightingSetup) -> dict | None:
    """LightingSetup → lighting: sub-dict."""
    out: dict[str, object] = {}
    if not _omit_empty_str(lt.key_light):
        out["key_light"] = lt.key_light
    if not _omit_empty_str(lt.fill_light):
        out["fill_light"] = lt.fill_light
    if not _omit_empty_str(lt.back_light):
        out["back_light"] = lt.back_light
    if not _omit_empty_str(lt.mood):
        out["mood"] = lt.mood
    if not _omit_empty_str(lt.color_temp):
        out["color_temp"] = lt.color_temp
    if not _omit_empty_str(lt.position):
        out["position"] = lt.position
    if not _omit_zero(lt.intensity):
        out["intensity"] = lt.intensity
    return out if out else None


def _serialize_shot(shot: Shot) -> dict:
    """Shot dataclass → dict with camera:/lighting:/subject: etc. sub-dicts."""

    # camera: sub-dict — prefer camera_raw for fidelity, merge typed fields
    cam = dict(shot.camera_raw) if shot.camera_raw else {}
    # Reconcile typed fields into camera dict (typed values take precedence)
    if not _omit_empty_str(shot.framing):
        cam["framing"] = shot.framing
    if not _omit_empty_str(shot.angle):
        cam["angle"] = shot.angle
    if not _omit_empty_str(shot.height):
        cam["height"] = shot.height
    if not _omit_empty_str(shot.lens):
        cam["lens"] = shot.lens
    if not _omit_empty_str(shot.movement):
        cam["movement"] = shot.movement
    if not _omit_empty_str(shot.focus):
        cam["focus"] = shot.focus
    if not _omit_empty_str(shot.aperture):
        cam["aperture"] = shot.aperture

    d: dict[str, object] = {}
    d["shot_id"] = shot.shot_id
    if not _omit_empty_str(shot.beat_ref):
        d["beat_ref"] = shot.beat_ref
    if shot.order != 1:
        d["order"] = shot.order
    if not _omit_zero(shot.duration):
        d["duration"] = shot.duration

    if cam:
        d["camera"] = cam

    # subject:
    subj = _serialize_dict({
        "character": shot.subject.character,
        "action": shot.subject.action,
        "position": shot.subject.position,
        "state": shot.subject.state,
    })
    if subj:
        d["subject"] = subj

    # composition:
    if shot.composition and not _omit(shot.composition, {}):
        d["composition"] = shot.composition

    # lighting:
    lt = _serialize_lighting(shot.lighting)
    if lt:
        d["lighting"] = lt

    # color:
    col = _serialize_dict({
        "palette": shot.color.palette,
        "accent": shot.color.accent,
        "contrast": shot.color.contrast,
    })
    if col:
        d["color"] = col

    # audio:
    aud: dict[str, object] = {}
    if shot.audio.silence:
        aud["silence"] = True
    if not _omit_empty_str(shot.audio.dialogue):
        aud["dialogue"] = shot.audio.dialogue
    if not _omit_empty_str(shot.audio.ambience):
        aud["ambience"] = shot.audio.ambience
    if not _omit_empty_str(shot.audio.sound_effects):
        aud["sound_effects"] = shot.audio.sound_effects
    if not _omit_empty_str(shot.audio.music):
        aud["music"] = shot.audio.music
    if aud:
        d["audio"] = aud

    # transition:
    if not _omit_empty_str(shot.transition_in):
        d["transition_in"] = shot.transition_in
    if not _omit_empty_str(shot.transition_out):
        d["transition_out"] = shot.transition_out

    # emotion:
    emo: dict[str, object] = {}
    if not _omit_empty_str(shot.emotion.target):
        emo["target"] = shot.emotion.target
    if shot.emotion.intensity != 5:
        emo["intensity"] = shot.emotion.intensity
    if emo:
        d["emotion"] = emo

    if not _omit_empty_str(shot.notes):
        d["notes"] = shot.notes

    return d


def _serialize_history(he: HistoryEntry) -> dict:
    d: dict[str, object] = {}
    if not _omit_empty_str(he.version):
        d["version"] = he.version
    if not _omit_empty_str(he.timestamp):
        d["timestamp"] = he.timestamp
    if not _omit_empty_str(he.author):
        d["author"] = he.author
    if he.changes and not _omit(he.changes, []):
        d["changes"] = he.changes
    if not _omit_empty_str(he.notes):
        d["notes"] = he.notes
    return d


def dump_project(project: Project) -> str:
    """Serialize a Project object to a YAML string (without Markdown envelope).

    This is the symmetric opposite of load_project().  The output is compatible
    with load_project() and preserves all typed fields including camera_raw,
    LightingSetup position/intensity, and nested sub-dicts.
    """
    out: dict[str, object] = {}
    if project.schema_version and project.schema_version != "1.0":
        out["schema_version"] = project.schema_version

    # metadata:
    meta = project.metadata
    out["metadata"] = _serialize_dict({
        "id": meta.id,
        "title": meta.title,
        "subtitle": meta.subtitle,
        "description": meta.description,
        "author": meta.author,
        "version": meta.version,
        "status": meta.status if meta.status != "Idea" else "",
        "created_at": meta.created_at,
        "updated_at": meta.updated_at,
        "language": meta.language if meta.language != "zh-CN" else "",
    })

    # creative:
    cr = project.creative
    out["creative"] = _serialize_dict({
        "objective": cr.objective,
        "audience": cr.audience,
        "genre": cr.genre,
        "subgenre": cr.subgenre,
        "tone": cr.tone,
        "pacing": cr.pacing,
        "emotional_arc": cr.emotional_arc,
        "realism": cr.realism,
    }) or {}
    if cr.visual_priority != 5:
        out["creative"]["visual_priority"] = cr.visual_priority  # type: ignore[index]
    if cr.dialogue_priority != 5:
        out["creative"]["dialogue_priority"] = cr.dialogue_priority  # type: ignore[index]
    if cr.action_priority != 5:
        out["creative"]["action_priority"] = cr.action_priority  # type: ignore[index]
    if cr.references and not _omit(cr.references, {}):
        out["creative"]["references"] = cr.references  # type: ignore[index]
    if not out["creative"]:
        del out["creative"]

    # story:
    st = project.story
    story: dict[str, object] = {}
    if not _omit_empty_str(st.premise):
        story["premise"] = st.premise
    if st.theme and not _omit(st.theme, []):
        story["theme"] = st.theme
    if st.genre and not _omit(st.genre, []):
        story["genre"] = st.genre
    if st.structure and st.structure != {"acts": []}:
        story["structure"] = st.structure
    if story:
        out["story"] = story

    # world:
    w = project.world
    world: dict[str, object] = {}
    for key, val in [
        ("timeline", w.timeline), ("era", w.era), ("location", w.location),
        ("architecture", w.architecture), ("climate", w.climate),
        ("weather", w.weather), ("season", w.season), ("culture", w.culture),
        ("technology", w.technology), ("society", w.society),
    ]:
        if isinstance(val, str) and val:
            world[key] = val
    if w.locations:
        world["locations"] = [
            _serialize_dict({
                "id": loc.id, "name": loc.name, "description": loc.description,
                "atmosphere": loc.atmosphere, "visual_identity": loc.visual_identity,
            }) or {}
            for loc in w.locations
        ]
    if world:
        out["world"] = world

    # characters:
    if project.characters:
        out["characters"] = []
        for ch in project.characters:
            cd: dict[str, object] = _serialize_dict({
                "id": ch.id, "name": ch.name, "role": ch.role, "age": ch.age,
                "gender": ch.gender, "ethnicity": ch.ethnicity,
                "appearance": ch.appearance, "wardrobe": ch.wardrobe,
                "accessories": ch.accessories,
            }) or {}
            if ch.personality:
                cd["personality"] = ch.personality
            if not _omit_empty_str(ch.motivation):
                cd["motivation"] = ch.motivation
            if not _omit_empty_str(ch.physical_state):
                cd["physical_state"] = ch.physical_state
            if ch.continuity_lock:
                cd["continuity_lock"] = True
            vi = ch.visual_identity
            vi_d = _serialize_dict({
                "age_range": vi.age_range, "appearance": vi.appearance,
                "clothing": vi.clothing, "accessories": vi.accessories,
            })
            if vi_d:
                cd["visual_identity"] = vi_d
            out["characters"].append(cd)  # type: ignore[union-attr]

    # visual_language:
    vl = project.visual_language
    vld: dict[str, object] = _serialize_dict({
        "style": vl.style, "lighting": vl.lighting,
        "camera_philosophy": vl.camera_philosophy,
        "atmosphere": vl.atmosphere, "texture": vl.texture,
        "camera_body": vl.camera_body, "lens_character": vl.lens_character,
        "film_stock": vl.film_stock, "color_grade": vl.color_grade,
        "render_engine": vl.render_engine, "render_settings": vl.render_settings,
    }) or {}
    if vl.color and not _omit(vl.color, {}):
        vld["color"] = vl.color
    if vl.references and not _omit(vl.references, []):
        vld["references"] = vl.references
    if vld:
        out["visual_language"] = vld

    # story_beats:
    if project.story_beats:
        out["story_beats"] = []
        for beat in project.story_beats:
            bd: dict[str, object] = _serialize_dict({
                "beat": beat.beat, "type": beat.type,
                "objective": beat.objective, "emotion": beat.emotion,
                "transition": beat.transition, "location": beat.location,
                "mood": beat.mood, "notes": beat.notes,
            }) or {}
            if beat.duration_ratio:
                bd["duration_ratio"] = beat.duration_ratio
            if beat.characters:
                bd["characters"] = beat.characters
            if beat.dialogue:
                bd["dialogue"] = True
            out["story_beats"].append(bd)  # type: ignore[union-attr]

    # shots:
    if project.shots:
        out["shots"] = [_serialize_shot(s) for s in project.shots]

    # scenes:
    if project.scenes:
        out["scenes"] = []
        for sc in project.scenes:
            sd: dict[str, object] = _serialize_dict({
                "id": sc.id, "title": sc.title, "location": sc.location,
                "time": sc.time, "emotion": sc.emotion,
                "narrative_goal": sc.narrative_goal,
            }) or {}
            if sc.characters:
                sd["characters"] = sc.characters
            if sc.shots:
                sd["shots"] = [_serialize_shot(s) for s in sc.shots]
            out["scenes"].append(sd)  # type: ignore[union-attr]

    # audio:
    au = project.audio
    aud: dict[str, object] = {}
    if au.music:
        aud["music"] = au.music
    if au.ambience:
        aud["ambience"] = au.ambience
    if not _omit_empty_str(au.dialogue):
        aud["dialogue"] = au.dialogue
    if not _omit_empty_str(au.narration):
        aud["narration"] = au.narration
    if au.sound_effects:
        aud["sound_effects"] = au.sound_effects
    if au.silence:
        aud["silence"] = True
    if not _omit_empty_str(au.rhythm):
        aud["rhythm"] = au.rhythm
    if aud:
        out["audio"] = aud

    # production:
    pr = project.production
    prod: dict[str, object] = {}
    for key, val in [
        ("locations", pr.locations), ("sets", pr.sets), ("props", pr.props),
        ("vehicles", pr.vehicles), ("wardrobe", pr.wardrobe),
    ]:
        if val and not _omit(val, []):
            prod[key] = val
    if not _omit_empty_str(pr.branding):
        prod["branding"] = pr.branding
    if not _omit_empty_str(pr.vfx):
        prod["vfx"] = pr.vfx
    if prod:
        out["production"] = prod

    # continuity:
    cont = project.continuity
    cd2: dict[str, object] = {}
    for key, val in [
        ("character", cont.character), ("wardrobe", cont.wardrobe),
        ("environment", cont.environment), ("weather", cont.weather),
        ("props", cont.props), ("vehicles", cont.vehicles),
        ("lighting", cont.lighting), ("color", cont.color),
        ("camera_language", cont.camera_language), ("audio", cont.audio),
    ]:
        if val and not _omit(val, []):
            cd2[key] = val
    if cd2:
        out["continuity"] = cd2

    # constraints:
    cn = project.constraints
    constr: dict[str, object] = {}
    for key, val in [
        ("avoid", cn.avoid), ("required", cn.required),
        ("safety", cn.safety), ("branding", cn.branding),
        ("censorship", cn.censorship),
    ]:
        if val and not _omit(val, []):
            constr[key] = val
    if constr:
        out["constraints"] = constr

    # output:
    op = project.output_profile
    outd: dict[str, object] = {}
    if op.duration:
        outd["duration"] = op.duration
    if op.aspect_ratio != "16:9":
        outd["aspect_ratio"] = op.aspect_ratio
    if op.fps != 24:
        outd["fps"] = op.fps
    if op.resolution != "1080p":
        outd["resolution"] = op.resolution
    if op.delivery != "digital":
        outd["delivery"] = op.delivery
    if outd:
        out["output"] = outd

    # history:
    if project.history:
        out["history"] = [_serialize_history(h) for h in project.history]

    return yaml.dump(out, allow_unicode=True, sort_keys=False, default_flow_style=False)


_MARKDOWN_SECTIONS = [
    "metadata", "Creative", "Story", "Characters", "World",
    "Visual Language", "Story Beats", "Shot List", "Audio",
    "Production", "Continuity", "Constraints", "Output Profile", "History",
]


def dump_project_with_markdown(project: Project) -> str:
    """Serialize Project to the same Markdown-enveloped YAML format as the_hanging.md.

    The YAML body is generated by dump_project().  Markdown ## Section headers are
    regenerated from canonical section names (the original headers are not preserved
    by the loader).
    """
    body = dump_project(project)
    lines: list[str] = []
    # Title line matching project naming convention
    title = project.metadata.title or "Untitled"
    subtitle = project.metadata.subtitle
    header = f"# Project: {title}"
    if subtitle:
        header += f" ({subtitle})"
    lines.append(header)
    lines.append("")

    # Insert ## Section markers between YAML top-level blocks
    # Strategy: split at top-level key lines, insert section headers
    yaml_lines = body.splitlines()
    section_map = {
        "metadata:": "## Metadata",
        "creative:": "## Creative",
        "story:": "## Story",
        "characters:": "## Characters",
        "world:": "## World",
        "visual_language:": "## Visual Language",
        "story_beats:": "## Story Beats",
        "shots:": "## Shot List",
        "scenes:": "## Scenes",
        "audio:": "## Audio",
        "production:": "## Production",
        "continuity:": "## Continuity",
        "constraints:": "## Constraints",
        "output:": "## Output Profile",
        "history:": "## History",
    }

    last_was_separator = False
    for line in yaml_lines:
        stripped = line.strip()
        section = section_map.get(stripped)
        if section:
            if not last_was_separator:
                lines.append("")
            lines.append("---")
            lines.append("")
            lines.append(section)
            lines.append("")
            last_was_separator = True
        lines.append(line)
        if stripped and not stripped.startswith(("metadata:", "creative:", "story:",
            "characters:", "world:", "visual_language:", "story_beats:", "shots:",
            "scenes:", "audio:", "production:", "continuity:", "constraints:",
            "output:", "history:")):
            last_was_separator = False

    lines.append("")
    return "\n".join(lines) + "\n"


def save_project_file(project: Project, path: str | Path) -> None:
    """Write project to disk in Markdown-enveloped YAML format.

    The output is compatible with load_project() — loading the saved file
    will reproduce the same typed Project structure.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = dump_project_with_markdown(project)
    path.write_text(content, encoding="utf-8")
