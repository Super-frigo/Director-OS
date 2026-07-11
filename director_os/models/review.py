"""Review model — quality feedback loop."""

from dataclasses import dataclass, field


@dataclass
class Issue:
    id: str = ""
    severity: str = "medium"  # low / medium / high / critical
    category: str = ""
    description: str = ""
    evidence: str = ""


@dataclass
class Suggestion:
    target: str = ""
    recommendation: str = ""
    expected_improvement: str = ""


@dataclass
class Review:
    schema_version: str = "1.0"
    metadata: dict = field(default_factory=lambda: {"id": "", "reviewer": ""})
    target: dict = field(default_factory=lambda: {"type": "shot"})
    comparison: dict = field(default_factory=lambda: {"intended": "", "generated": ""})
    evaluation: dict = field(default_factory=lambda: {
        "dimensions": {
            "narrative": {},
            "character": {},
            "visual": {},
            "cinematography": {},
            "emotion": {},
            "consistency": {},
        }
    })
    issues: list[Issue] = field(default_factory=list)
    suggestions: list[Suggestion] = field(default_factory=list)
    confidence: dict = field(default_factory=lambda: {"overall": 0.0})
    knowledge_feedback: dict = field(default_factory=dict)
