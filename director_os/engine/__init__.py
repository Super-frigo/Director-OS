"""Engine layer — interprets Project and produces ProductionIntent.

Vision Step 5 pipeline:
    Project → RequirementAnalyzer → KnowledgeResolver → ProjectEnricher → Compiler
"""

from .pipeline import (
    EngineInput,
    BaseEngine,
    StoryEngine,
    CharacterEngine,
    VisualEngine,
    ShotEngine,
    EnginePipeline,
)
from .analyzer import RequirementAnalyzer, AnalysisResult
from .enricher import ProjectEnricher, EnrichmentResult

__all__ = [
    "EngineInput",
    "BaseEngine",
    "StoryEngine",
    "CharacterEngine",
    "VisualEngine",
    "ShotEngine",
    "EnginePipeline",
    "RequirementAnalyzer",
    "AnalysisResult",
    "ProjectEnricher",
    "EnrichmentResult",
]
