"""Library Entry model — reusable creative knowledge."""

from dataclasses import dataclass, field


@dataclass
class LibraryEntry:
    schema_version: str = "1.0"
    metadata: dict = field(default_factory=lambda: {"id": "", "name": ""})
    category: str = ""
    knowledge: dict = field(default_factory=lambda: {
        "concept": "", "principles": [], "emotional_effects": []
    })
    applicability: dict = field(default_factory=lambda: {
        "emotions": [], "genres": [], "keywords": []
    })
    engine_guidance: dict = field(default_factory=lambda: {
        "when_to_use": "", "recommended_actions": [], "avoid": []
    })
    relationships: dict = field(default_factory=lambda: {"related": [], "conflicts": []})
    examples: dict = field(default_factory=lambda: {"successful": [], "failure": []})
    references: dict = field(default_factory=dict)
    version: str = "1.0"
