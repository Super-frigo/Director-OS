"""Project model ? canonical representation of a film.

Maps every section of the Director OS project YAML format.
"""

from dataclasses import dataclass, field


@dataclass
class Metadata:
    id: str = ""
    title: str = ""
    subtitle: str = ""
    description: str = ""
    author: str = ""
    version: str = ""
    status: str = "Idea"
    created_at: str = ""
    updated_at: str = ""
    language: str = "zh-CN"


@dataclass
class Creative:
    objective: str = ""
    audience: str = ""
    genre: str = ""
    subgenre: str = ""
    tone: str = ""
    pacing: str = ""
    emotional_arc: str = ""
    realism: str = ""
    visual_priority: int = 5
    dialogue_priority: int = 5
    action_priority: int = 5
    references: dict = field(default_factory=dict)


@dataclass
class Story:
    premise: str = ""
    theme: list[str] = field(default_factory=list)
    genre: list[str] = field(default_factory=list)
    structure: dict = field(default_factory=lambda: {"acts": []})


@dataclass
class StoryBeat:
    beat: str = ""
    type: str = ""
    objective: str = ""
    emotion: str = ""
    transition: str = ""
    duration_ratio: float = 0.0
    characters: list[str] = field(default_factory=list)
    location: str = ""
    dialogue: bool = False
    mood: str = ""
    notes: str = ""


@dataclass
class Location:
    id: str = ""
    name: str = ""
    description: str = ""
    atmosphere: str = ""
    visual_identity: str = ""


@dataclass
class World:
    timeline: str = ""
    era: str = ""
    location: str = ""
    architecture: str = ""
    climate: str = ""
    weather: str = ""
    season: str = ""
    culture: str = ""
    technology: str = ""
    society: str = ""
    locations: list[Location] = field(default_factory=list)


@dataclass
class VisualIdentity:
    age_range: str = ""
    appearance: str = ""
    clothing: str = ""
    accessories: str = ""


@dataclass
class Character:
    id: str = ""
    name: str = ""
    role: str = ""
    age: str = ""
    gender: str = ""
    ethnicity: str = ""
    appearance: str = ""
    wardrobe: str = ""
    accessories: str = ""
    personality: list[str] = field(default_factory=list)
    motivation: str = ""
    physical_state: str = ""
    continuity_lock: bool = False
    visual_identity: VisualIdentity = field(default_factory=VisualIdentity)


@dataclass
class Subject:
    character: str = ""
    action: str = ""
    position: str = ""
    state: str = ""


@dataclass
class LightingSetup:
    key_light: str = ""
    fill_light: str = ""
    back_light: str = ""
    mood: str = ""
    color_temp: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "LightingSetup":
        return cls(
            key_light=d.get("key_light", d.get("key", "")),
            fill_light=d.get("fill_light", d.get("fill", "")),
            back_light=d.get("back_light", d.get("back", "")),
            mood=d.get("mood", ""),
            color_temp=d.get("color_temp", d.get("temperature", "")),
        )


@dataclass
class ShotColor:
    palette: str = ""
    accent: str = ""
    contrast: str = ""


@dataclass
class ShotAudio:
    silence: bool = False
    dialogue: str = ""
    ambience: str = ""
    sound_effects: str = ""
    music: str = ""


@dataclass
class EmotionTarget:
    target: str = ""
    intensity: int = 5


@dataclass
class Shot:
    shot_id: str = ""
    beat_ref: str = ""
    order: int = 1
    duration: float = 0.0
    subject: Subject = field(default_factory=Subject)
    framing: str = ""
    angle: str = ""
    height: str = ""
    lens: str = ""
    movement: str = ""
    focus: str = ""
    aperture: str = ""
    composition: dict = field(default_factory=dict)
    lighting: LightingSetup = field(default_factory=LightingSetup)
    color: ShotColor = field(default_factory=ShotColor)
    audio: ShotAudio = field(default_factory=ShotAudio)
    transition_in: str = ""
    transition_out: str = ""
    emotion: EmotionTarget = field(default_factory=EmotionTarget)
    notes: str = ""
    camera_raw: dict = field(default_factory=dict)


@dataclass
class Scene:
    id: str = ""
    title: str = ""
    location: str = ""
    time: str = ""
    emotion: str = ""
    narrative_goal: str = ""
    characters: list[str] = field(default_factory=list)
    shots: list[Shot] = field(default_factory=list)


@dataclass
class VisualLanguage:
    style: str = ""
    color: dict = field(default_factory=dict)
    lighting: str = ""
    camera_philosophy: str = ""
    references: list[str] = field(default_factory=list)
    atmosphere: str = ""
    texture: str = ""
    camera_body: str = ""
    lens_character: str = ""
    film_stock: str = ""
    color_grade: str = ""
    render_engine: str = ""
    render_settings: str = ""


@dataclass
class AudioDesign:
    music: list = field(default_factory=list)
    ambience: list = field(default_factory=list)
    dialogue: str = ""
    narration: str = ""
    sound_effects: list = field(default_factory=list)
    silence: bool = False
    rhythm: str = ""


@dataclass
class ProductionDesign:
    locations: list = field(default_factory=list)
    sets: list = field(default_factory=list)
    props: list = field(default_factory=list)
    vehicles: list = field(default_factory=list)
    wardrobe: list = field(default_factory=list)
    branding: str = ""
    vfx: str = ""


@dataclass
class Continuity:
    character: list = field(default_factory=list)
    wardrobe: list = field(default_factory=list)
    environment: list = field(default_factory=list)
    weather: list = field(default_factory=list)
    props: list = field(default_factory=list)
    vehicles: list = field(default_factory=list)
    lighting: list = field(default_factory=list)
    color: list = field(default_factory=list)
    camera_language: list = field(default_factory=list)
    audio: list = field(default_factory=list)


@dataclass
class Constraints:
    avoid: list = field(default_factory=list)
    required: list = field(default_factory=list)
    safety: list = field(default_factory=list)
    branding: list = field(default_factory=list)
    censorship: list = field(default_factory=list)


@dataclass
class OutputProfile:
    duration: int = 0
    aspect_ratio: str = "16:9"
    fps: int = 24
    resolution: str = "1080p"
    delivery: str = "digital"


@dataclass
class HistoryEntry:
    version: str = ""
    timestamp: str = ""
    author: str = ""
    changes: list = field(default_factory=list)
    notes: str = ""


@dataclass
class Project:
    schema_version: str = "1.0"
    metadata: Metadata = field(default_factory=Metadata)
    creative: Creative = field(default_factory=Creative)
    story: Story = field(default_factory=Story)
    world: World = field(default_factory=World)
    characters: list[Character] = field(default_factory=list)
    scenes: list[Scene] = field(default_factory=list)
    shots: list[Shot] = field(default_factory=list)
    visual_language: VisualLanguage = field(default_factory=VisualLanguage)
    audio: AudioDesign = field(default_factory=AudioDesign)
    production: ProductionDesign = field(default_factory=ProductionDesign)
    continuity: Continuity = field(default_factory=Continuity)
    constraints: Constraints = field(default_factory=Constraints)
    output_profile: OutputProfile = field(default_factory=OutputProfile)
    history: list[HistoryEntry] = field(default_factory=list)
    story_beats: list[StoryBeat] = field(default_factory=list)
    production_intent: ProductionDesign = field(default_factory=ProductionDesign)

    def validate(self) -> list[str]:
        issues: list[str] = []
        if not self.metadata.title:
            issues.append("metadata.title is required")
        if not self.story.premise:
            issues.append("story.premise is required")
        if not self.characters:
            issues.append("at least one character is required")
        if self.shots and not self.story_beats:
            issues.append("story_beats should be defined when shots exist")

        # Cross-check: sum of shot durations vs declared output duration.
        # Tolerates a 1s rounding margin (e.g. 15s target, 15.x s of shots).
        shot_total = sum(s.duration for s in self.shots if s.duration)
        target = self.output_profile.duration
        if shot_total and target and abs(shot_total - target) > 1:
            issues.append(
                f"output.duration ({target}s) differs from total shot duration "
                f"({shot_total:g}s) by {abs(shot_total - target):g}s"
            )

        char_ids = {c.id for c in self.characters}
        for scene in self.scenes:
            for cid in scene.characters:
                if cid not in char_ids:
                    issues.append(f"scene {scene.id}: character {cid!r} not defined")
        return issues

    def is_valid(self) -> bool:
        return len(self.validate()) == 0


