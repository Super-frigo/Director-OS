"""Project Schema - canonical definition and validator for Director OS project files.

This module is the single authority for what constitutes a valid Project YAML.
Use validate_yaml() to check any project file before feeding it into the pipeline.

Usage:
    from schemas.project_schema import validate_yaml
    errors = validate_yaml(yaml_dict)
    if errors:
        for e in errors:
            print(f"  - {e}")
    else:
        print("Valid project")

Schema version: 2.0.0
Corresponds to: docs/PROJECT_SCHEMA.md
"""

from dataclasses import dataclass, field
from datetime import date as date_type
from typing import Any
import re

# --- Shot Grammar enums (from docs/SHOT_GRAMMAR.md) --------------------------

VALID_FRAMING = {"ECU", "CU", "MCU", "MS", "MLS", "LS", "ELS", "EST", "OTS", "POV",
                 "TWO_SHOT", "GROUP_SHOT", "INSERT", "DETAIL"}

VALID_ANGLE = {"EYE_LEVEL", "HIGH_ANGLE", "LOW_ANGLE", "BIRDS_EYE", "WORMS_EYE",
               "DUTCH_ANGLE", "OVERHEAD", "CANTED"}

VALID_HEIGHT = {"GROUND", "WAIST", "CHEST", "EYE", "ABOVE_EYE", "HIGH", "CEILING"}

VALID_LENS = {"14mm", "18mm", "24mm", "35mm", "50mm", "85mm", "100mm", "135mm",
              "200mm", "400mm+"}

VALID_MOVEMENT = {"STATIC", "PAN_L", "PAN_R", "TILT_UP", "TILT_DOWN", "DOLLY_IN",
                  "DOLLY_OUT", "TRACK_L", "TRACK_R", "TRACK_F", "TRACK_B", "ARC_L",
                  "ARC_R", "BOOM_UP", "BOOM_DOWN", "HANDHELD", "STEADICAM", "GIMBAL",
                  "CRANE", "DRONE", "ZOOM_IN", "ZOOM_OUT", "DUTCH_TILT", "WHIP_PAN",
                  "SNAP_ZOOM", "RACK_FOCUS"}

VALID_FOCUS = {"DEEP_FOCUS", "SHALLOW_FOCUS", "RACK_FOCUS", "SOFT_FOCUS",
               "PULL_FOCUS", "MACRO_FOCUS", "INFRARED", "MOTION_BLUR", "SPLIT_DIOPTER"}

VALID_APERTURE = {"f1.2", "f1.4", "f1.8", "f2.8", "f4", "f5.6", "f8", "f11", "f16"}

VALID_LIGHT_TYPE = {"NATURAL", "HARD", "SOFT", "MOTIVATED", "PRACTICAL", "CONTRAST",
                    "SILHOUETTE", "RIM", "HAIR", "EYE_LIGHT", "NEGATIVE_FILL",
                    "CHIAROSCURO", "THREE_POINT", "HIGH_KEY", "LOW_KEY"}

VALID_LIGHT_POSITION = {"FRONT", "THREE_QUARTER", "SIDE", "RIM", "BACK", "TOP",
                        "UNDER", "FRONTAL_45", "SIDE_90", "BACK_45"}

VALID_COLOR_TEMP = {"2000K", "3200K", "4300K", "5500K", "6500K", "8000K+", "VARIABLE"}

VALID_COMPOSITION_RULE = {"RULE_OF_THIRDS", "GOLDEN_RATIO", "CENTER_COMPOSITION",
                          "SYMMETRY", "LEADING_LINES", "FRAME_WITHIN_FRAME", "DIAGONAL",
                          "TRIANGULAR", "CIRCULAR", "NEGATIVE_SPACE", "RULE_OF_SPACE",
                          "HEADROOM", "LOOKROOM", "DYNAMIC_SYMMETRY", "GOLDEN_SPIRAL",
                          "BALANCED", "ASYMMETRICAL"}

VALID_TRANSITION = {"CUT_TO", "FADE_TO", "FADE_TO_BLACK", "FADE_FROM_BLACK",
                    "FADE_TO_WHITE", "FADE_FROM_WHITE",
                    "DISSOLVE_TO", "SLOW_DISSOLVE_TO", "SMASH_CUT_TO", "MATCH_CUT_TO",
                    "WIPE_TO", "IRIS_TO"}

VALID_STATUS = {"Idea", "Planning", "Writing", "Storyboard", "Ready", "Completed", "Archived"}

VALID_ASPECT = {"16:9", "9:16", "4:3", "1:1", "1.85:1", "2.39:1", "21:9"}

VALID_DELIVERY = {"digital", "film", "broadcast", "streaming", "social"}

VALID_BEAT_TYPE = {"OPENING", "INCITING", "REVELATION", "CONFLICT", "DECISION",
                   "LOSS", "GAIN", "TWIST", "CLIMAX", "RESOLUTION", "THE_RITUAL",
                   "THE_FACE", "AFTERMATH"}

# --- Required top-level modules -----------------------------------------------

REQUIRED_MODULES = {"metadata", "creative", "story", "characters", "world",
                    "visual_language", "story_beats", "shots"}

# Aliases: project files may use 'visual' instead of 'visual_language'
MODULE_ALIASES = {"visual": "visual_language"}

REQUIRED_METADATA = {"title", "status"}
REQUIRED_CREATIVE = {"genre"}
REQUIRED_STORY = {"premise"}
REQUIRED_SHOT = {"shot_id", "duration", "framing", "lens", "movement"}
REQUIRED_BEAT = {"beat", "type"}

# --- Validator ----------------------------------------------------------------

def validate_yaml(data: dict, path: str = "") -> list[str]:
    """Validate a project YAML dict. Returns list of error strings (empty = valid)."""
    errors: list[str] = []

    p = _p(path)

    # Top-level must be a dict
    if not isinstance(data, dict):
        return [f"{p}: expected a mapping, got {type(data).__name__}"]

    # Resolve module aliases (e.g. 'visual' -> 'visual_language')
    for alias, canonical in MODULE_ALIASES.items():
        if alias in data and canonical not in data:
            data[canonical] = data.pop(alias)

    # Check for required top-level modules
    for mod in REQUIRED_MODULES:
        if mod not in data:
            errors.append(f"{p}: missing required module '{mod}'")

    # --- metadata ---
    if "metadata" in data:
        meta = data["metadata"]
        if isinstance(meta, dict):
            for f in REQUIRED_METADATA:
                if f not in meta or not meta[f]:
                    errors.append(f"{p}metadata.{f}: required")
            if meta.get("status") and meta["status"] not in VALID_STATUS:
                errors.append(f"{p}metadata.status: invalid '{meta['status']}', must be one of {sorted(VALID_STATUS)}")
            for f in ["id", "title", "subtitle", "description", "author",
                       "version", "created_at", "updated_at", "language"]:
                if f in meta and meta[f] is not None:
                    if isinstance(meta[f], date_type):
                        meta[f] = meta[f].isoformat()  # normalize YAML date
                    elif not isinstance(meta[f], str):
                        errors.append(f"{p}metadata.{f}: expected string, got {type(meta[f]).__name__}")
        else:
            errors.append(f"{p}metadata: expected mapping, got {type(meta).__name__}")

    # --- creative ---
    if "creative" in data:
        cr = data["creative"]
        if isinstance(cr, dict):
            for f in REQUIRED_CREATIVE:
                if f not in cr or not cr[f]:
                    errors.append(f"{p}creative.{f}: required")
        else:
            errors.append(f"{p}creative: expected mapping")

    # --- story ---
    if "story" in data:
        st = data["story"]
        if isinstance(st, dict):
            for f in REQUIRED_STORY:
                if f not in st or not st[f]:
                    errors.append(f"{p}story.{f}: required")
        else:
            errors.append(f"{p}story: expected mapping")

    # --- characters ---
    char_ids = set()
    if "characters" in data:
        chars = data["characters"]
        if isinstance(chars, list):
            for i, c in enumerate(chars):
                if isinstance(c, dict):
                    cid = c.get("id", "")
                    if not cid:
                        errors.append(f"{p}characters[{i}].id: required")
                    elif cid in char_ids:
                        errors.append(f"{p}characters[{i}].id: duplicate '{cid}'")
                    else:
                        char_ids.add(cid)
                    if not c.get("role"):
                        errors.append(f"{p}characters[{i}].role: required")
                else:
                    errors.append(f"{p}characters[{i}]: expected mapping")
        else:
            errors.append(f"{p}characters: expected list")

    # --- story_beats ---
    beat_ids = set()
    if "story_beats" in data:
        beats = data["story_beats"]
        if isinstance(beats, list):
            for i, b in enumerate(beats):
                if isinstance(b, dict):
                    for f in REQUIRED_BEAT:
                        if f not in b or not b[f]:
                            errors.append(f"{p}story_beats[{i}].{f}: required")
                    bid = b.get("beat", "")
                    if bid and bid in beat_ids:
                        errors.append(f"{p}story_beats[{i}].beat: duplicate '{bid}'")
                    elif bid:
                        beat_ids.add(bid)
                    if b.get("type") and b["type"] not in VALID_BEAT_TYPE:
                        errors.append(f"{p}story_beats[{i}].type: invalid '{b['type']}'")
                else:
                    errors.append(f"{p}story_beats[{i}]: expected mapping")
        else:
            errors.append(f"{p}story_beats: expected list")

    # --- shots ---
    shot_ids = set()
    if "shots" in data:
        shots = data["shots"]
        if isinstance(shots, list):
            for i, s in enumerate(shots):
                if isinstance(s, dict):
                    _validate_shot(s, i, char_ids, beat_ids, p, errors, shot_ids)
                else:
                    errors.append(f"{p}shots[{i}]: expected mapping")
        else:
            errors.append(f"{p}shots: expected list")

    # --- output ---
    if "output_profile" in data:
        out = data["output_profile"]
    elif "output" in data:
        out = data["output"]
    else:
        out = {}
    if isinstance(out, dict):
        # Handle YAML sexagesimal parsing: 16:9 becomes 969
        ar = out.get("aspect_ratio")
        if ar is not None and isinstance(ar, (int, float)):
            out["aspect_ratio"] = _decode_aspect_ratio(ar)
        if out.get("aspect_ratio") and out["aspect_ratio"] not in VALID_ASPECT:
            errors.append(f"{p}output.aspect_ratio: invalid '{out['aspect_ratio']}'")
        if out.get("delivery") and out["delivery"] not in VALID_DELIVERY:
            errors.append(f"{p}output.delivery: invalid '{out['delivery']}'")

    return errors


def _validate_shot(shot: dict, i: int, char_ids: set, beat_ids: set,
                   p: str, errors: list, shot_ids: set) -> None:
    """Validate a single shot dict."""
    # Required fields: also look inside camera sub-dict
    cam_for_req = shot.get("camera", {})
    for f in REQUIRED_SHOT:
        val = shot.get(f) or (cam_for_req.get(f) if isinstance(cam_for_req, dict) else None)
        if f == "duration":
            if val is None:
                errors.append(f"{p}shots[{i}].{f}: required")
        elif not val:
            errors.append(f"{p}shots[{i}].{f}: required")

    sid = shot.get("shot_id", shot.get("id", ""))
    if sid and sid in shot_ids:
        errors.append(f"{p}shots[{i}].shot_id: duplicate '{sid}'")
    elif sid:
        shot_ids.add(sid)

    # Cross-reference checks
    bref = shot.get("beat_ref", shot.get("beat", ""))
    if bref and beat_ids and bref not in beat_ids:
        errors.append(f"{p}shots[{i}].beat_ref: '{bref}' not found in story_beats")

    subj = shot.get("subject", {})
    if isinstance(subj, dict) and subj.get("character"):
        cid = subj["character"]
        if char_ids and cid not in char_ids:
            errors.append(f"{p}shots[{i}].subject.character: '{cid}' not found in characters")

    # Camera fields (supports both camelCase and flat structures)
    cam = shot.get("camera", {})
    if isinstance(cam, dict):
        _check_enum(cam, "framing", VALID_FRAMING, f"{p}shots[{i}].camera", errors)
        _check_enum(cam, "angle", VALID_ANGLE, f"{p}shots[{i}].camera", errors)
        _check_enum(cam, "height", VALID_HEIGHT, f"{p}shots[{i}].camera", errors)
        _check_enum(cam, "lens", VALID_LENS, f"{p}shots[{i}].camera", errors)
        _check_enum(cam, "movement", VALID_MOVEMENT, f"{p}shots[{i}].camera", errors)
        _check_enum(cam, "focus", VALID_FOCUS, f"{p}shots[{i}].camera", errors)
        _check_enum(cam, "aperture", VALID_APERTURE, f"{p}shots[{i}].camera", errors)
    elif shot.get("framing") and not cam:
        _check_enum(shot, "framing", VALID_FRAMING, f"{p}shots[{i}]", errors)
        _check_enum(shot, "angle", VALID_ANGLE, f"{p}shots[{i}]", errors)
        _check_enum(shot, "height", VALID_HEIGHT, f"{p}shots[{i}]", errors)
        _check_enum(shot, "lens", VALID_LENS, f"{p}shots[{i}]", errors)
        _check_enum(shot, "movement", VALID_MOVEMENT, f"{p}shots[{i}]", errors)
        _check_enum(shot, "focus", VALID_FOCUS, f"{p}shots[{i}]", errors)
        _check_enum(shot, "aperture", VALID_APERTURE, f"{p}shots[{i}]", errors)

    # Lighting fields
    lighting = shot.get("lighting", {})
    if isinstance(lighting, dict):
        _check_enum(lighting, "key_light", VALID_LIGHT_TYPE, f"{p}shots[{i}].lighting", errors)
        _check_enum(lighting, "position", VALID_LIGHT_POSITION, f"{p}shots[{i}].lighting", errors)
        _check_enum(lighting, "color_temp", VALID_COLOR_TEMP, f"{p}shots[{i}].lighting", errors)
        _check_enum(lighting, "temperature", VALID_COLOR_TEMP, f"{p}shots[{i}].lighting", errors)
        if "intensity" in lighting:
            intensity = lighting["intensity"]
            if isinstance(intensity, str):
                try:
                    intensity = int(intensity)
                except ValueError:
                    errors.append(f"{p}shots[{i}].lighting.intensity: not a number: '{intensity}'")
            if isinstance(intensity, (int, float)):
                if not 1 <= intensity <= 10:
                    errors.append(f"{p}shots[{i}].lighting.intensity: must be 1-10, got {intensity}")

    # Composition fields (supports compound rules like 'RULE_OF_THIRDS + LEADING_LINES')
    comp = shot.get("composition", {})
    if isinstance(comp, dict):
        _check_composition_rule(comp, "rule", f"{p}shots[{i}].composition", errors)
        if "depth" in comp:
            depth = comp["depth"]
            if isinstance(depth, str):
                try:
                    depth = int(depth)
                except ValueError:
                    errors.append(f"{p}shots[{i}].composition.depth: not a number")
            if isinstance(depth, (int, float)) and not 1 <= depth <= 5:
                errors.append(f"{p}shots[{i}].composition.depth: expected 1-5, got {depth}")

    # Transition fields
    for fld in ("transition_in", "transition_out"):
        val = shot.get(fld, "")
        if val and val not in VALID_TRANSITION:
            errors.append(f"{p}shots[{i}].{fld}: invalid '{val}'")

    # Emotion fields
    emo = shot.get("emotion", {})
    if isinstance(emo, dict):
        if "intensity" in emo:
            intensity = emo["intensity"]
            if isinstance(intensity, str):
                try:
                    intensity = int(intensity)
                except ValueError:
                    errors.append(f"{p}shots[{i}].emotion.intensity: not a number: '{intensity}'")
            if isinstance(intensity, (int, float)) and not 1 <= intensity <= 10:
                errors.append(f"{p}shots[{i}].emotion.intensity: must be 1-10, got {intensity}")

    # Duration check
    dur = shot.get("duration")
    if dur is not None:
        try:
            float(dur)
        except (ValueError, TypeError):
            errors.append(f"{p}shots[{i}].duration: not a number: '{dur}'")


def _check_enum(d: dict, key: str, valid: set, prefix: str, errors: list) -> None:
    """Check a dict value against an enum set."""
    val = d.get(key, "")
    if val and val not in valid:
        errors.append(f"{prefix}.{key}: invalid '{val}', expected one of {sorted(valid)}")


def _check_composition_rule(d: dict, key: str, prefix: str, errors: list) -> None:
    """Check composition rule, allowing compound rules like 'RULE_OF_THIRDS + LEADING_LINES'."""
    val = d.get(key, "")
    if not val:
        return
    parts = [p.strip() for p in re.split(r"\+", val)]
    for part in parts:
        if part not in VALID_COMPOSITION_RULE:
            errors.append(f"{prefix}.{key}: invalid component '{part}' in compound rule '{val}'")


def _decode_aspect_ratio(ar) -> str:
    """Decode YAML sexagesimal (16:9 -> 969) back to aspect ratio string."""
    known = {969: "16:9", 870: "14:9", 144: "2:24", 95: "1:35", 706: "11:46"}
    if isinstance(ar, (int, float)):
        ar_int = int(ar)
        return known.get(ar_int, str(ar_int))
    return str(ar)


def _p(path: str) -> str:
    """Format a path prefix for error messages."""
    return f"{path}:" if path else ""
