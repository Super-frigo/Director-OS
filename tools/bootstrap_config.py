"""Configuration for Knowledge Library Bootstrap.

Defines:
- Category targets (existing + new entries to generate)
- Unified emotion / genre vocabulary (extracted from existing entries)
- Allowed category values
"""

from __future__ import annotations

from pathlib import Path


# ── Paths ──────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCAL_RULES_DIR = PROJECT_ROOT / "knowledge" / "providers" / "local_rules"
SCHEMA_PATH = PROJECT_ROOT / "schemas" / "library.schema.yaml"
PROMPTS_DIR = PROJECT_ROOT / "tools" / "prompts"
REPORTS_DIR = PROJECT_ROOT / "tools" / "reports"


# ── Allowed category values ────────────────────────────────────────────
# Note: schema lists 9 values, but existing lighting entries use "lighting"
# which is not in the schema's supported list. We include it for compat.

ALLOWED_CATEGORIES = [
    "cinematography",
    "storytelling",
    "character",
    "visual_style",
    "genre",
    "production",
    "sound",
    "editing",
    "model_capability",
    "lighting",  # used by existing entries; not in schema doc but in practice
]


# ── Unified Emotion Vocabulary ─────────────────────────────────────────
# Extracted from all existing entries' emotional_effects + applicability.emotions.
# New entries MUST use terms from this list.

EMOTION_VOCABULARY = sorted(set([
    # ── From camera/lens entries ──
    "isolation", "awe", "insignificance", "exposure",
    "grounded", "objective", "documentary",
    "honesty", "presence", "calm", "quiet",
    "intimacy", "tension", "obsession", "vulnerability",
    "urgency", "immediacy", "authenticity", "chaos",
    "intrusion", "discovery", "realization", "pressure",
    "unease", "disorientation",
    # ── From lighting entries ──
    "mystery", "danger", "moral_ambiguity", "fear", "suspicion",
    "warmth", "nostalgia", "hope", "beauty", "transience",
    "love", "peace", "melancholy",
    "truth", "drama", "romance",
    "innocence", "oppression",
    "alienation", "coldness",
    "epic", "sublime", "solitude",
    # ── From color entries ──
    "cinematic", "polished", "commercial", "blockbuster",
    "detachment", "technology", "sadness", "loneliness",
    "passion", "violence", "anger", "desire",
    "sickness", "unease", "dread",
    "energetic",
    # ── Extended (for new entries) ──
    "freedom", "contemplative", "neutral",
    "panic", "comfort", "joy", "triumph", "despair",
    "serenity", "grandeur", "claustrophobia",
    "intensity", "voyeurism", "surprise", "release", "abandonment",
    "aspiration", "grounding", "empathy", "comedy", "safety",
    "stylized", "dreamlike", "nostalgic", "whimsy", "energy",
    "disorientation",
]))


# ── Unified Genre Vocabulary ───────────────────────────────────────────

GENRE_VOCABULARY = sorted(set([
    "science_fiction", "western", "epic", "horror",
    "drama", "documentary", "noir", "realism",
    "comedy", "thriller", "romance", "psychological_drama",
    "action", "war", "coming_of_age", "commercial",
    "blockbuster", "musical", "fantasy", "mystery",
    "crime", "adventure", "animation", "family",
    "all",
    "architecture", "sports", "sitcom", "art_film",
    "cyberpunk", "music_video", "period",
]))


# ── Category Definitions ───────────────────────────────────────────────
# Each category specifies:
#   directory:   where YAML files live under local_rules/
#   category_value: value for the 'category' field in YAML
#   id_prefix:   ID naming convention prefix
#   existing:    list of existing entry IDs (for few-shot + dedup)
#   new_ids:     list of new entry IDs to generate
#   few_shot:    entry IDs to use as few-shot examples for skeleton generation

CATEGORIES = {
    # ── Camera / Lens ─────────────────────────────────────────────
    "lens": {
        "directory": "camera",
        "category_value": "cinematography",
        "id_prefix": "lens_",
        "existing": [
            "lens_24mm_wide",
            "lens_35mm_standard",
            "lens_50mm_portrait",
            "lens_85mm_compression",
        ],
        "new_ids": [
            "lens_14mm_ultrawide",
            "lens_18mm_wide",
            "lens_100mm_medium_tele",
            "lens_135mm_tele",
            "lens_200mm_long_tele",
            "lens_400mm_extreme_tele",
        ],
        "few_shot": ["lens_35mm_standard", "lens_85mm_compression"],
        "definition": (
            "Camera lens focal lengths. Each focal length produces distinct "
            "perspective compression, depth of field, and emotional character. "
            "Covers ultra-wide (14mm) through extreme telephoto (400mm+)."
        ),
    },

    # ── Camera / Movement ─────────────────────────────────────────
    "camera_movement": {
        "directory": "camera",
        "category_value": "cinematography",
        "id_prefix": "movement_",
        "existing": [
            "movement_crane",
            "movement_dolly_in",
            "movement_follow",
            "movement_handheld",
            "movement_push_pull",
            "movement_static",
            "movement_steadicam",
            "movement_tracking",
        ],
        "new_ids": [
            "movement_whip_pan",
            "movement_dolly_out",
            "movement_pedestal_up",
            "movement_pedestal_down",
            "movement_truck",
            "movement_arc",
            "movement_tilt",
        ],
        "few_shot": ["movement_dolly_in", "movement_handheld"],
        "definition": (
            "Camera movement techniques — how the camera physically moves "
            "(or doesn't) during a shot. Each movement carries distinct "
            "emotional and narrative meaning."
        ),
    },

    # ── Camera / Framing (shot size) ──────────────────────────────
    "framing": {
        "directory": "camera",
        "category_value": "cinematography",
        "id_prefix": "framing_",
        "existing": [
            "shot_size_reference",  # comprehensive entry, kept as index
        ],
        "new_ids": [
            "framing_ecu",
            "framing_cu",
            "framing_ms",
            "framing_ls",
            "framing_els",
        ],
        "few_shot": [],  # no same-prefix examples; use lens examples
        "definition": (
            "Shot size / framing distance — the physical distance between "
            "camera and subject that determines how much of the subject "
            "and environment is visible. Ranges from Extreme Close-Up "
            "to Extreme Long Shot."
        ),
    },

    # ── Lighting ──────────────────────────────────────────────────
    "lighting": {
        "directory": "lighting",
        "category_value": "lighting",
        "id_prefix": "light_",
        "existing": [
            "light_color_temperature",
            "light_direction_emotion",
            "light_emotion_mapping",
            "light_golden_hour",
            "light_low_key_noir",
            "light_quality",
            "light_ratio",
            "light_special_effects",
        ],
        "new_ids": [
            "light_high_key_bright",
            "light_silhouette",
        ],
        "few_shot": ["light_low_key_noir", "light_golden_hour"],
        "definition": (
            "Lighting setups and techniques. Each lighting approach creates "
            "specific emotional atmosphere through contrast, direction, "
            "quality, color temperature, and special effects."
        ),
    },

    # ── Color Palette ─────────────────────────────────────────────
    "color": {
        "directory": "color",
        "category_value": "visual_style",
        "id_prefix": "color_",
        "existing": [
            "color_blue_cold",
            "color_desaturated_gray",
            "color_green_sick",
            "color_red_passion",
            "color_teal_orange",
            "color_yellow_warm",
        ],
        "new_ids": [
            "color_monochrome",
            "color_pastel",
            "color_neon",
            "color_earth_tone",
        ],
        "few_shot": ["color_teal_orange", "color_blue_cold"],
        "definition": (
            "Color palette strategies for visual storytelling. Each palette "
            "communicates specific emotional tone, genre convention, and "
            "production design direction."
        ),
    },
}


# ── Deepening priority (Layer 4) ───────────────────────────────────────
# Entries most frequently queried by the Engine get examples + extra depth.

DEEPENING_PRIORITY = [
    # Lens — most queried focal lengths
    "lens_24mm_wide", "lens_35mm_standard", "lens_50mm_portrait", "lens_85mm_compression",
    # Camera movement — most common
    "movement_handheld", "movement_dolly_in", "movement_static", "movement_tracking",
    # Lighting — most referenced
    "light_low_key_noir", "light_golden_hour", "light_quality",
    # Color — most used palettes
    "color_teal_orange", "color_blue_cold", "color_red_passion",
    # Framing — narrative core
    "framing_cu", "framing_ms",
]


def get_category_dir(category_key: str) -> Path:
    """Get the filesystem directory for a category key."""
    cat = CATEGORIES[category_key]
    return LOCAL_RULES_DIR / cat["directory"]


def get_all_target_ids() -> list[str]:
    """Get all new entry IDs across all categories."""
    ids: list[str] = []
    for cat in CATEGORIES.values():
        ids.extend(cat["new_ids"])
    return ids


def get_all_existing_ids() -> list[str]:
    """Get all existing entry IDs across all categories."""
    ids: list[str] = []
    for cat in CATEGORIES.values():
        ids.extend(cat["existing"])
    return ids
