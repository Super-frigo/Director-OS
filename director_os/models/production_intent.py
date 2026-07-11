"""Production Intent model — Engine output contract."""

from dataclasses import dataclass, field


@dataclass
class CharacterDirection:
    id: str = ""
    performance: str = ""
    emotional_state: str = ""
    action: str = ""
    name: str = ""


@dataclass
class ProductionIntent:
    schema_version: str = "1.0"
    metadata: dict = field(default_factory=lambda: {"id": "", "source_project": ""})
    scene: dict = field(default_factory=lambda: {"scene_id": "", "shot_id": ""})
    creative_goal: dict = field(default_factory=lambda: {"primary": "", "emotional_target": []})
    narrative_intent: dict = field(default_factory=dict)
    visual_direction: dict = field(default_factory=lambda: {
        "style": "", "mood": [], "composition": "", "color": "",
        "texture": "", "atmosphere": "", "camera_body": "",
        "lens_character": "", "film_stock": "", "color_grade": "",
        "render_engine": "", "render_settings": "",
    })
    camera_strategy: dict = field(default_factory=lambda: {
        "framing": "", "movement": "", "perspective": "", "lens_character": "", "focus_behavior": ""
    })
    character_direction: list[CharacterDirection] = field(default_factory=list)
    environment_direction: dict = field(default_factory=dict)
    temporal_design: dict = field(default_factory=lambda: {"pacing": "", "motion_style": "", "duration": ""})
    audio_intent: dict = field(default_factory=dict)
    consistency_requirements: dict = field(default_factory=dict)
    constraints: dict = field(default_factory=lambda: {"must": [], "avoid": [], "limitations": []})

