"""Project Enricher — applies resolved knowledge to Production Intent.

Vision Step 5: The Enricher sits between Knowledge Resolver and Compiler,
taking resolved knowledge and mapping it to concrete creative decisions
in the Production Intent.
"""

from dataclasses import dataclass, field
from typing import Any

from ..knowledge import ResolvedKnowledge, KnowledgeEntry


@dataclass
class EnrichmentResult:
    """Output of ProjectEnricher: enriched data + traceability."""
    enriched: dict = field(default_factory=dict)
    applied: list[dict] = field(default_factory=list)   # which entries were used
    skipped: list[dict] = field(default_factory=list)    # which entries couldn't be applied


class ProjectEnricher:
    """Maps resolved knowledge onto creative decisions.

    Usage:
        enricher = ProjectEnricher()
        result = enricher.enrich(production_intent_dict, resolved_knowledge)
        # result.enriched → dict ready for Compiler
        # result.applied → traceability log
    """

    # Maps knowledge domains to production intent fields
    DOMAIN_TARGETS = {
        "composition": "visual_direction.composition_guidance",
        "lighting": "visual_direction.lighting_guidance",
        "cinematography": "visual_direction.camera_guidance",
        "visual_style": "visual_direction.style_guidance",
        "storytelling": "narrative_intent.story_guidance",
        "color": "visual_direction.color_guidance",
        "model_capabilities": "constraints.model_guidance",
    }

    def enrich(self, intent: dict, resolved: ResolvedKnowledge) -> EnrichmentResult:
        """Apply resolved knowledge to a production intent dict.

        Args:
            intent: ProductionIntent as dict (or any dict with creative fields)
            resolved: ResolvedKnowledge from the resolver pipeline

        Returns:
            EnrichmentResult with enriched dict and traceability
        """
        enriched = dict(intent)  # shallow copy — we add new keys
        applied: list[dict] = []
        skipped: list[dict] = []

        # Ensure guidance containers exist
        enriched.setdefault("knowledge_sources", [])

        for entry in resolved.entries:
            target = self.DOMAIN_TARGETS.get(entry.domain)
            if not target:
                skipped.append({
                    "entry_id": entry.entry_id,
                    "domain": entry.domain,
                    "reason": "no target field mapped",
                })
                continue

            # Navigate dotted path and set guidance
            self._set_nested(enriched, target, self._build_guidance(entry))

            applied.append({
                "entry_id": entry.entry_id,
                "domain": entry.domain,
                "source": entry.source,
                "confidence": entry.confidence,
                "target": target,
            })

            # Traceability
            enriched["knowledge_sources"].append({
                "entry_id": entry.entry_id,
                "domain": entry.domain,
                "source": entry.source,
                "source_detail": entry.source_detail,
                "confidence": entry.confidence,
                "rules_applied": len(entry.rules),
            })

        return EnrichmentResult(
            enriched=enriched,
            applied=applied,
            skipped=skipped,
        )

    def _build_guidance(self, entry: KnowledgeEntry) -> dict:
        """Build a guidance dict from a knowledge entry."""
        return {
            "description": entry.description,
            "rules": entry.rules,
            "examples": entry.examples[:3] if entry.examples else [],
            "source": entry.source,
            "confidence": entry.confidence,
        }

    @staticmethod
    def _set_nested(data: dict, path: str, value: Any) -> None:
        """Set a value at a dotted path, creating intermediate dicts as needed."""
        keys = path.split(".")
        for key in keys[:-1]:
            if key not in data or not isinstance(data[key], dict):
                data[key] = {}
            data = data[key]
        data[keys[-1]] = value
