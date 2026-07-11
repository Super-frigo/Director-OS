"""Seedance Compiler — deterministic, four-stage pipeline.

Stages (per docs/COMPILER_SPEC.md):
  Stage 1: project_reader()   — parse + validate project YAML
  Stage 2: context_builder()  — build CompileContext from validated project
  Stage 3: platform_adapter() — apply Seedance translation rules
  Stage 4: prompt_assembler() — assemble final prompt string

Usage:
    python -m compilers.seedance.compile projects/the_hanging.md
    python -m compilers.seedance.compile projects/the_hanging.md -o prompt.txt
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Ensure project root is on sys.path so schemas are importable
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compilers.seedance.rules import (
    FRAMING_MAP,
    ANGLE_MAP,
    HEIGHT_MAP,
    LENS_MAP,
    MOVEMENT_MAP,
    FOCUS_MAP,
    LIGHTING_TYPE_MAP,
    LIGHTING_POSITION_MAP,
    COLOR_TEMP_MAP,
    COMPOSITION_MAP,
    TRANSITION_MAP,
    BEAT_TYPE_MAP,
    APERTURE_MAP,
    lookup,
    lookup_composition,
    lookup_with_fallback,
)


# ============================================================================
# Data types
# ============================================================================

@dataclass
class CompileError:
    """A structured compilation error (not an exception)."""
    stage: str
    field: str
    message: str
    severity: str = "error"


@dataclass
class StoryContext:
    beats: List[Dict[str, Any]] = field(default_factory=list)
    arcs: List[Dict[str, Any]] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)


@dataclass
class VisualContext:
    language: Dict[str, Any] = field(default_factory=dict)
    shots: List[Dict[str, Any]] = field(default_factory=list)
    continuity: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CharacterContext:
    characters: List[Dict[str, Any]] = field(default_factory=list)
    current_state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorldContext:
    timeline: str = ""
    location: str = ""
    weather: str = ""
    era: str = ""
    architecture: str = ""
    climate: str = ""
    season: str = ""
    culture: str = ""
    technology: str = ""


@dataclass
class OutputContext:
    duration: float = 15.0
    aspect_ratio: str = "16:9"
    fps: int = 24
    resolution: str = "1080p"


@dataclass
class CompileContext:
    """Unified compilation context (Stage 2 output)."""
    project: Dict[str, Any] = field(default_factory=dict)
    story_context: StoryContext = field(default_factory=StoryContext)
    visual_context: VisualContext = field(default_factory=VisualContext)
    character_context: CharacterContext = field(default_factory=CharacterContext)
    world_context: WorldContext = field(default_factory=WorldContext)
    output_context: OutputContext = field(default_factory=OutputContext)


@dataclass
class ShotPromptPart:
    """A single shot translated into Seedance prompt fragments."""
    shot_id: str = ""
    order: int = 0
    duration: float = 0.0
    beat_ref: str = ""
    desc_lines: List[str] = field(default_factory=list)


@dataclass
class PlatformPromptParts:
    """Stage 3 output: translated prompt parts for assembly."""
    global_settings: List[str] = field(default_factory=list)
    shots: List[ShotPromptPart] = field(default_factory=list)
    character_contexts: List[str] = field(default_factory=list)
    audio_notes: List[str] = field(default_factory=list)
    tone_notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class CompileResult:
    """Final compilation result."""
    success: bool
    prompt: str = ""
    errors: List[CompileError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# YAML loader (mirrors scripts/validate_project.py)
# ============================================================================

def _load_project_yaml(path: Path) -> Dict[str, Any]:
    """Load a project YAML file, stripping Markdown headers and --- separators."""
    try:
        import yaml
    except ImportError:
        sys.exit("PyYAML is required: pip install pyyaml")

    raw = path.read_text(encoding="utf-8-sig")
    cleaned: List[str] = []
    for line in raw.splitlines():
        if re.match(r"^#{2,}\s+", line):
            continue
        if line.strip() == "---":
            continue
        cleaned.append(line)
    clean_text = "\n".join(cleaned)
    data = yaml.safe_load(clean_text)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a YAML mapping, got {type(data).__name__}")
    return data


# ============================================================================
# Stage 1: Project Reader
# ============================================================================

def project_reader(project_path: Path) -> Tuple[Optional[Dict[str, Any]], List[CompileError]]:
    """Read and validate a project YAML file.

    Args:
        project_path: Path to a .md or .yaml project file.

    Returns:
        (parsed_project_dict, list_of_CompileErrors).
        If errors are present, the caller should NOT proceed to Stage 2.
    """
    errors: List[CompileError] = []

    # Parse
    try:
        data = _load_project_yaml(project_path)
    except Exception as exc:
        errors.append(CompileError(
            stage="stage1", field="(file)",
            message=f"Failed to parse project YAML: {exc}",
        ))
        return None, errors

    # Resolve module aliases (e.g. 'visual' -> 'visual_language')
    _resolve_aliases(data)

    # Required top-level modules
    required = ["metadata", "creative", "story", "characters", "world",
                "visual_language", "story_beats", "shots"]
    for mod in required:
        if mod not in data or not data[mod]:
            errors.append(CompileError(
                stage="stage1", field=mod,
                message=f"Missing required module '{mod}'",
            ))

    # Sub-validations
    meta = data.get("metadata", {})
    if not meta.get("title"):
        errors.append(CompileError(
            stage="stage1", field="metadata.title",
            message="metadata.title is required",
        ))
    if not meta.get("status"):
        errors.append(CompileError(
            stage="stage1", field="metadata.status",
            message="metadata.status is required",
        ))

    creative = data.get("creative", {})
    if not creative.get("genre"):
        errors.append(CompileError(
            stage="stage1", field="creative.genre",
            message="creative.genre is required",
        ))

    story = data.get("story", {})
    if not story.get("premise"):
        errors.append(CompileError(
            stage="stage1", field="story.premise",
            message="story.premise is required",
        ))

    beats = data.get("story_beats", [])
    if isinstance(beats, list) and len(beats) == 0:
        errors.append(CompileError(
            stage="stage1", field="story_beats",
            message="At least 1 story beat is required",
        ))
    elif not isinstance(beats, list):
        errors.append(CompileError(
            stage="stage1", field="story_beats",
            message="story_beats must be a list",
        ))

    shots = data.get("shots", [])
    if isinstance(shots, list) and len(shots) == 0:
        errors.append(CompileError(
            stage="stage1", field="shots",
            message="At least 1 shot is required",
        ))
    elif not isinstance(shots, list):
        errors.append(CompileError(
            stage="stage1", field="shots",
            message="shots must be a list",
        ))

    # Validate shot-level required fields
    shot_ids_seen: set = set()
    beat_ids = {b.get("beat", "") for b in beats if isinstance(b, dict)}
    char_ids = {c.get("id", "") for c in data.get("characters", []) if isinstance(c, dict)}

    if isinstance(shots, list):
        for i, shot in enumerate(shots):
            if not isinstance(shot, dict):
                errors.append(CompileError(
                    stage="stage1", field=f"shots[{i}]",
                    message="Each shot must be a mapping",
                ))
                continue

            sid = shot.get("shot_id", "")
            if not sid:
                errors.append(CompileError(
                    stage="stage1", field=f"shots[{i}].shot_id",
                    message="shot_id is required",
                ))
            elif sid in shot_ids_seen:
                errors.append(CompileError(
                    stage="stage1", field=f"shots[{i}].shot_id",
                    message=f"Duplicate shot_id '{sid}'",
                ))
            else:
                shot_ids_seen.add(sid)

            # Check required shot fields (in camera sub-dict or flat)
            cam = shot.get("camera", {}) if isinstance(shot.get("camera"), dict) else {}
            for rf in ("duration", "framing", "lens", "movement"):
                val = shot.get(rf) or (cam.get(rf) if isinstance(cam, dict) else None)
                if val is None and rf == "duration":
                    errors.append(CompileError(
                        stage="stage1", field=f"shots[{i}].{rf}",
                        message=f"Shot '{sid or i}' missing required '{rf}'",
                    ))
                elif not val and rf != "duration":
                    errors.append(CompileError(
                        stage="stage1", field=f"shots[{i}].{rf}",
                        message=f"Shot '{sid or i}' missing required '{rf}'",
                    ))

            # Cross-reference beat_ref
            bref = shot.get("beat_ref", "")
            if bref and beat_ids and bref not in beat_ids:
                errors.append(CompileError(
                    stage="stage1", field=f"shots[{i}].beat_ref",
                    message=f"beat_ref '{bref}' not found in story_beats",
                    severity="warning",
                ))

            # Cross-reference character
            subj = shot.get("subject", {})
            if isinstance(subj, dict) and subj.get("character"):
                cid = subj["character"]
                if char_ids and cid not in char_ids:
                    errors.append(CompileError(
                        stage="stage1", field=f"shots[{i}].subject.character",
                        message=f"Character '{cid}' not found in characters list",
                        severity="warning",
                    ))

    # Continuity check
    if "continuity" in data:
        cont = data["continuity"]
        if isinstance(cont, dict) and "character" in cont:
            if not isinstance(cont["character"], list):
                errors.append(CompileError(
                    stage="stage1", field="continuity.character",
                    message="continuity.character must be a list",
                ))

    return data, errors


def _resolve_aliases(data: Dict[str, Any]) -> None:
    """Resolve module aliases in-place (e.g. 'visual' -> 'visual_language')."""
    aliases = {"visual": "visual_language"}
    for alias, canonical in aliases.items():
        if alias in data and canonical not in data:
            data[canonical] = data.pop(alias)


# ============================================================================
# Stage 2: Context Builder
# ============================================================================

# YAML sexagesimal decode: "16:9" gets parsed as integer 969
_ASPECT_RATIO_DECODE = {
    969: "16:9", 870: "14:9", 688: "11:28",
    144: "2:24", 95: "1:35", 706: "11:46",
}


def _decode_aspect(raw: Any) -> str:
    """Decode YAML sexagesimal aspect ratio back to a string."""
    if isinstance(raw, (int, float)):
        return _ASPECT_RATIO_DECODE.get(int(raw), str(int(raw)))
    return str(raw) if raw else "16:9"


def context_builder(project: Dict[str, Any]) -> CompileContext:
    """Build a unified CompileContext from a validated project dict.

    Args:
        project: Validated project dictionary from Stage 1.

    Returns:
        CompileContext with all sub-contexts populated.
    """
    ctx = CompileContext(project=project)

    # --- Story context ---
    story = project.get("story", {})
    ctx.story_context.beats = project.get("story_beats", [])
    theme = story.get("theme")
    if isinstance(theme, str) and theme:
        ctx.story_context.themes = [theme]
    elif isinstance(theme, list):
        ctx.story_context.themes = theme
    ctx.story_context.arcs = [
        {"id": c.get("id"), "role": c.get("role", ""), "motivation": c.get("motivation", "")}
        for c in project.get("characters", []) if isinstance(c, dict)
    ]

    # --- Visual context ---
    ctx.visual_context.language = project.get("visual_language", project.get("visual", {}))
    ctx.visual_context.shots = project.get("shots", [])
    ctx.visual_context.continuity = project.get("continuity", {})

    # --- Character context ---
    chars = project.get("characters", [])
    ctx.character_context.characters = chars
    ctx.character_context.current_state = {
        c.get("id", ""): {
            "physical_state": c.get("physical_state", ""),
            "wardrobe": c.get("wardrobe", ""),
            "accessories": c.get("accessories", ""),
            "appearance": c.get("appearance", ""),
        }
        for c in chars if isinstance(c, dict) and c.get("id")
    }

    # --- World context ---
    world = project.get("world", {})
    ctx.world_context.timeline = str(world.get("timeline", ""))
    ctx.world_context.location = str(world.get("location", ""))
    ctx.world_context.weather = str(world.get("weather", ""))
    ctx.world_context.era = str(world.get("era", ""))
    ctx.world_context.architecture = str(world.get("architecture", ""))
    ctx.world_context.climate = str(world.get("climate", ""))
    ctx.world_context.season = str(world.get("season", ""))
    ctx.world_context.culture = str(world.get("culture", ""))
    ctx.world_context.technology = str(world.get("technology", ""))

    # --- Output context ---
    out = project.get("output_profile", project.get("output", {}))
    if isinstance(out, dict):
        dur = out.get("duration", 15)
        try:
            ctx.output_context.duration = float(dur)
        except (ValueError, TypeError):
            ctx.output_context.duration = 15.0
        ctx.output_context.aspect_ratio = _decode_aspect(out.get("aspect_ratio", "16:9"))
        ctx.output_context.resolution = str(out.get("resolution", "1080p"))
        try:
            ctx.output_context.fps = int(out.get("fps", 24))
        except (ValueError, TypeError):
            ctx.output_context.fps = 24

    return ctx


# ============================================================================
# Stage 3: Platform Adapter
# ============================================================================

def platform_adapter(ctx: CompileContext) -> PlatformPromptParts:
    """Apply Seedance-specific translation rules to the compile context.

    Args:
        ctx: CompileContext from Stage 2.

    Returns:
        PlatformPromptParts with all elements translated to Seedance strings.
    """
    parts = PlatformPromptParts()
    visual = ctx.visual_context.language
    world = ctx.world_context
    chars = ctx.character_context.characters
    creative = ctx.project.get("creative", {})
    story = ctx.project.get("story", {})
    audio = ctx.project.get("audio", {})
    constraints = ctx.project.get("constraints", {})

    # --- Global settings ---
    style = visual.get("style", "")
    if style:
        parts.global_settings.append(f"Style: {style}.")

    if world.era:
        parts.global_settings.append(f"Setting: {world.era}.")

    color_palette = visual.get("color_palette", visual.get("color", ""))
    if color_palette:
        parts.global_settings.append(f"Color palette: {color_palette}.")

    lighting_desc = visual.get("lighting", "")
    if lighting_desc:
        parts.global_settings.append(f"Lighting: {lighting_desc}.")

    texture = visual.get("texture", "")
    if texture:
        parts.global_settings.append(f"Texture: {texture}.")

    atmosphere = visual.get("atmosphere", "")
    if atmosphere:
        parts.global_settings.append(f"Atmosphere: {atmosphere}.")

    cam_style = visual.get("camera", {})
    if isinstance(cam_style, dict):
        rhy = cam_style.get("rhythm", {})
        if isinstance(rhy, dict):
            pacing = rhy.get("pacing", "")
            if pacing:
                parts.global_settings.append(f"Pacing: {pacing}.")

    parts.global_settings.append(
        f"Output: {ctx.output_context.duration}s, "
        f"{ctx.output_context.aspect_ratio}, "
        f"{ctx.output_context.fps}fps, "
        f"{ctx.output_context.resolution}."
    )

    genre = creative.get("genre", "")
    if genre:
        parts.global_settings.append(f"Genre: {genre}.")
    tone = creative.get("tone", "")
    if tone:
        parts.global_settings.append(f"Tone: {tone}.")

    avoid_list = constraints.get("avoid", [])
    if avoid_list:
        parts.global_settings.append(f"Avoid: {', '.join(avoid_list)}.")
    req_list = constraints.get("required", [])
    if req_list:
        parts.global_settings.append(f"Required: {', '.join(req_list)}.")

    # --- Character contexts ---
    for c in chars:
        if not isinstance(c, dict):
            continue
        desc_parts = []
        name = c.get("name", c.get("id", ""))
        role = c.get("role", "")
        appearance = c.get("appearance", "")
        wardrobe = c.get("wardrobe", "")
        accessories = c.get("accessories", "")
        personality = c.get("personality", "")
        physical = c.get("physical_state", "")

        if name and role:
            desc_parts.append(f"{name} ({role})")
        elif name:
            desc_parts.append(name)
        if appearance:
            desc_parts.append(appearance)
        if wardrobe:
            desc_parts.append(f"Wears {wardrobe}")
        if accessories:
            desc_parts.append(f"Carries {accessories}")
        if physical:
            desc_parts.append(physical)
        if personality:
            desc_parts.append(personality)

        if desc_parts:
            parts.character_contexts.append(". ".join(desc_parts) + ".")

    # --- Shot-by-shot translation ---
    shots = ctx.visual_context.shots

    for shot in shots:
        if not isinstance(shot, dict):
            continue

        sp = ShotPromptPart(
            shot_id=shot.get("shot_id", ""),
            order=int(shot.get("order", 0)),
            duration=float(shot.get("duration", 0)),
            beat_ref=shot.get("beat_ref", ""),
        )

        cam = shot.get("camera", {}) if isinstance(shot.get("camera"), dict) else {}
        framing = shot.get("framing") or cam.get("framing", "")
        angle = shot.get("angle") or cam.get("angle", "")
        height = shot.get("height") or cam.get("height", "")
        lens = shot.get("lens") or cam.get("lens", "")
        movement = shot.get("movement") or cam.get("movement", "")
        focus = shot.get("focus") or cam.get("focus", "")

        lines: List[str] = []

        # Framing + subject
        framing_text = lookup(FRAMING_MAP, framing)
        framing_label = framing_text if framing_text else framing

        subj = shot.get("subject", {})
        if isinstance(subj, dict):
            action = subj.get("action", "")
            char_ref = subj.get("character", "")

            if framing_label:
                if action:
                    lines.append(f"{framing_label.capitalize()}. {action}.")
                elif char_ref:
                    char_name = _find_char_name(chars, char_ref)
                    lines.append(f"{framing_label.capitalize()} of {char_name}.")
                else:
                    lines.append(f"{framing_label.capitalize()}.")
            else:
                if action:
                    lines.append(f"{action}.")
        elif framing_label:
            lines.append(f"{framing_label.capitalize()}.")

        # Camera tech details
        cam_details = []
        if lens:
            lens_text = lookup(LENS_MAP, lens)
            cam_details.append(lens_text if lens_text else lens)
        if angle and angle != "EYE_LEVEL":
            angle_text = lookup(ANGLE_MAP, angle)
            if angle_text:
                cam_details.append(angle_text)
        if height:
            height_text = lookup(HEIGHT_MAP, height)
            if height_text:
                cam_details.append(height_text)
        if movement:
            mov_text = lookup(MOVEMENT_MAP, movement)
            cam_details.append(mov_text if mov_text else movement)
        if focus:
            focus_text = lookup(FOCUS_MAP, focus)
            cam_details.append(focus_text if focus_text else focus)

        if cam_details:
            lines.append("Camera: " + ", ".join(cam_details) + ".")

        # Composition
        comp = shot.get("composition", {})
        if isinstance(comp, dict):
            comp_rule = comp.get("rule", "")
            if comp_rule:
                comp_text = lookup_composition(comp_rule)
                if comp_text:
                    lines.append(f"Composition: {comp_text}.")
            depth = comp.get("depth", "")
            if depth:
                lines.append(f"Depth layers: {depth}.")
            for plane in ("foreground", "midground", "background"):
                val = comp.get(plane, "")
                if val:
                    lines.append(f"{plane.capitalize()}: {val}.")

        # Lighting
        light = shot.get("lighting", {})
        if isinstance(light, dict):
            light_parts = []
            key_light = light.get("key_light", "")
            if key_light:
                lt = lookup(LIGHTING_TYPE_MAP, key_light)
                light_parts.append(lt if lt else key_light)
            position = light.get("position", "")
            if position:
                lp = lookup(LIGHTING_POSITION_MAP, position)
                light_parts.append(lp if lp else position)
            intensity = light.get("intensity", "")
            if intensity:
                light_parts.append(f"intensity {intensity}")
            temperature = light.get("temperature", "")
            if temperature:
                ct = lookup(COLOR_TEMP_MAP, temperature)
                light_parts.append(ct if ct else temperature)
            mood = light.get("mood", "")
            if mood:
                light_parts.append(mood)
            if light_parts:
                lines.append("Lighting: " + ", ".join(light_parts) + ".")

        # Color
        color = shot.get("color", {})
        if isinstance(color, dict):
            color_parts = []
            for ck in ("palette", "accent", "contrast"):
                cv = color.get(ck, "")
                if cv:
                    color_parts.append(f"{ck}: {cv}")
            if color_parts:
                lines.append("Color: " + ", ".join(color_parts) + ".")

        # Audio
        aud = shot.get("audio", {})
        if isinstance(aud, dict):
            audio_parts = []
            if aud.get("silence"):
                audio_parts.append("silence")
            ambience = aud.get("ambience", "")
            if ambience:
                audio_parts.append(f"ambience: {ambience}")
            sfx = aud.get("sound_effects", "")
            if sfx:
                audio_parts.append(f"sound: {sfx}")
            music = aud.get("music", "")
            if music:
                audio_parts.append(f"music: {music}")
            if audio_parts:
                lines.append("Audio: " + ", ".join(audio_parts) + ".")

        # Emotion
        emo = shot.get("emotion", {})
        if isinstance(emo, dict):
            emo_parts = []
            target = emo.get("target", "")
            if target:
                emo_parts.append(target)
            eint = emo.get("intensity", "")
            if eint:
                emo_parts.append(f"intensity {eint}")
            if emo_parts:
                lines.append("Emotion: " + ", ".join(emo_parts) + ".")

        # Notes
        notes = shot.get("notes", "")
        if notes:
            lines.append(f"Note: {notes}")

        # Transitions
        t_in = shot.get("transition_in", "")
        t_out = shot.get("transition_out", "")
        if t_in:
            lines.append(f"Transition in: {lookup(TRANSITION_MAP, t_in)}.")
        if t_out:
            lines.append(f"Transition out: {lookup(TRANSITION_MAP, t_out)}.")

        sp.desc_lines = lines
        parts.shots.append(sp)

    # --- Audio notes ---
    if isinstance(audio, dict):
        audio_notes = []
        music = audio.get("music", [])
        if music:
            audio_notes.append("Music: " + (
                "; ".join(str(m) for m in music) if isinstance(music, list) else str(music)
            ))
        amb = audio.get("ambience", [])
        if amb:
            audio_notes.append("Ambience: " + (
                "; ".join(str(a) for a in amb) if isinstance(amb, list) else str(amb)
            ))
        dialogue = audio.get("dialogue", "")
        if dialogue:
            audio_notes.append(f"Dialogue: {dialogue}")
        silence_note = audio.get("silence", "")
        if silence_note:
            audio_notes.append(f"Silence: {silence_note}")
        rhythm = audio.get("rhythm", "")
        if rhythm:
            audio_notes.append(f"Rhythm: {rhythm}")
        parts.audio_notes = audio_notes

    # --- Tone notes ---
    tone_creative = creative.get("tone", "")
    emotional_arc = creative.get("emotional_arc", "")
    pacing = creative.get("pacing", "")
    if tone_creative:
        parts.tone_notes.append(f"Tone: {tone_creative}.")
    if emotional_arc:
        parts.tone_notes.append(f"Emotional arc: {emotional_arc}.")
    if pacing:
        parts.tone_notes.append(f"Pacing: {pacing}.")
    story_theme = story.get("theme", "")
    if story_theme:
        parts.tone_notes.append(f"Theme: {story_theme}.")

    # --- Warnings ---
    if ctx.output_context.duration > 15:
        parts.warnings.append(
            f"Duration {ctx.output_context.duration}s exceeds Seedance 15s clip limit"
        )
    if len(chars) > 2:
        parts.warnings.append(
            f"{len(chars)} characters may reduce Seedance consistency"
        )
    for shot in shots:
        cam = shot.get("camera", {}) if isinstance(shot.get("camera"), dict) else {}
        mov = shot.get("movement") or cam.get("movement", "")
        if mov in ("WHIP_PAN", "SNAP_ZOOM"):
            parts.warnings.append(
                f"Shot {shot.get('shot_id', '?')}: '{mov}' may be unreliable on Seedance"
            )

    return parts


def _find_char_name(chars: List[Dict[str, Any]], char_id: str) -> str:
    """Find a character's display name by id."""
    for c in chars:
        if isinstance(c, dict) and c.get("id") == char_id:
            return c.get("name", char_id)
    return char_id


# ============================================================================
# Stage 4: Prompt Assembler
# ============================================================================

def prompt_assembler(parts: PlatformPromptParts) -> str:
    """Assemble translated parts into a final deterministic prompt string.

    Args:
        parts: PlatformPromptParts from Stage 3.

    Returns:
        Final prompt string suitable for Seedance.
    """
    sections: List[str] = []

    sections.append("=== Seedance Prompt ===")
    sections.append("")

    # Global Settings
    if parts.global_settings:
        sections.append("## Global Settings")
        sections.append("")
        for gs in parts.global_settings:
            sections.append(f"- {gs}")
        sections.append("")

    # Character Contexts
    if parts.character_contexts:
        sections.append("## Characters")
        sections.append("")
        for cc in parts.character_contexts:
            sections.append(f"- {cc}")
        sections.append("")

    # Shot-by-Shot
    if parts.shots:
        sections.append("## Shot List")
        sections.append("")

        for sp in sorted(parts.shots, key=lambda s: s.order):
            t_start = sum(
                s2.duration for s2 in parts.shots
                if s2.order < sp.order
            )
            t_end = t_start + sp.duration
            beat_label = f" [{sp.beat_ref}]" if sp.beat_ref else ""
            sections.append(
                f"### Shot {sp.order}: {sp.shot_id}{beat_label} "
                f"({t_start:.1f}s-{t_end:.1f}s)"
            )
            sections.append("")
            for line in sp.desc_lines:
                sections.append(line)
            sections.append("")

    # Audio Design
    if parts.audio_notes:
        sections.append("## Audio Design")
        sections.append("")
        for an in parts.audio_notes:
            sections.append(f"- {an}")
        sections.append("")

    # Tone & Theme
    if parts.tone_notes:
        sections.append("## Tone & Theme")
        sections.append("")
        for tn in parts.tone_notes:
            sections.append(f"- {tn}")
        sections.append("")

    # Warnings
    if parts.warnings:
        sections.append("## Warnings")
        sections.append("")
        for w in parts.warnings:
            sections.append(f"- [WARNING] {w}")
        sections.append("")

    return "\n".join(sections)


# ============================================================================
# Top-level compile() — ties the pipeline together
# ============================================================================

def compile_project(
    project_path: Path,
    *,
    verbose: bool = False,
) -> CompileResult:
    """Run the full four-stage Seedance compilation pipeline.

    Args:
        project_path: Path to a project .md or .yaml file.
        verbose: If True, print pipeline progress to stderr.

    Returns:
        CompileResult with success flag, prompt string, errors, and warnings.
    """
    errors: List[CompileError] = []
    warnings: List[str] = []

    # Stage 1
    if verbose:
        print("[Stage 1] project_reader...", file=sys.stderr)
    project, stage1_errors = project_reader(project_path)
    errors.extend(stage1_errors)

    error_errors = [e for e in stage1_errors if e.severity == "error"]
    if error_errors or project is None:
        return CompileResult(
            success=False,
            errors=errors,
            stats={"stage": "stage1_failed"},
        )

    # Stage 2
    if verbose:
        print("[Stage 2] context_builder...", file=sys.stderr)
    ctx = context_builder(project)

    # Stage 3
    if verbose:
        print("[Stage 3] platform_adapter...", file=sys.stderr)
    parts = platform_adapter(ctx)
    warnings.extend(parts.warnings)

    # Stage 4
    if verbose:
        print("[Stage 4] prompt_assembler...", file=sys.stderr)
    prompt = prompt_assembler(parts)

    # Stats
    total_dur = sum(
        float(s.get("duration", 0)) for s in ctx.visual_context.shots
        if isinstance(s, dict)
    )
    stats = {
        "shots_compiled": len(parts.shots),
        "tokens_estimated": len(prompt.split()),
        "duration_seconds": total_dur,
    }

    return CompileResult(
        success=True,
        prompt=prompt,
        errors=errors,
        warnings=warnings,
        stats=stats,
    )


# ============================================================================
# CLI entry point
# ============================================================================

def main() -> None:
    """CLI entry point for the Seedance compiler."""
    parser = argparse.ArgumentParser(
        description="Seedance Compiler — deterministic project-to-prompt pipeline",
    )
    parser.add_argument(
        "project", type=Path,
        help="Path to project .md or .yaml file",
    )
    parser.add_argument(
        "-o", "--output", type=Path, default=None,
        help="Write prompt to file instead of stdout",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Show pipeline stage progress",
    )
    args = parser.parse_args()

    if not args.project.exists():
        print(f"Error: file not found: {args.project}", file=sys.stderr)
        sys.exit(1)

    result = compile_project(args.project, verbose=args.verbose)

    if not result.success:
        print("Compilation FAILED:", file=sys.stderr)
        for e in result.errors:
            print(f"  [{e.stage}] {e.field}: {e.message}", file=sys.stderr)
        sys.exit(1)

    if result.warnings:
        for w in result.warnings:
            print(f"Warning: {w}", file=sys.stderr)

    if args.output:
        args.output.write_text(result.prompt, encoding="utf-8")
        print(f"Prompt written to {args.output}", file=sys.stderr)
    else:
        print(result.prompt)

    if args.verbose:
        print(file=sys.stderr)
        print(f"Shots compiled: {result.stats.get('shots_compiled', 0)}", file=sys.stderr)
        print(f"Total duration: {result.stats.get('duration_seconds', 0)}s", file=sys.stderr)
        print(f"Est. tokens: {result.stats.get('tokens_estimated', 0)}", file=sys.stderr)


if __name__ == "__main__":
    main()
