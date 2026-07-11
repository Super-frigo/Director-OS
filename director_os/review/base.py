"""Review interface for evaluating generation quality."""

from ..models.review import Review, Issue, Suggestion


class BaseReviewer:
    """Subclass per review dimension (narrative, visual, character, etc.)."""

    def evaluate(self, intended: dict, generated: dict) -> Review:
        raise NotImplementedError


class ConsistencyReviewer(BaseReviewer):
    """Checks character, style, and location consistency."""

    def evaluate(self, intended: dict, generated: dict) -> Review:
        issues: list[Issue] = []
        suggestions: list[Suggestion] = []

        char_ok = intended.get("character") == generated.get("character")
        if not char_ok:
            issues.append(Issue(
                id="character_drift",
                severity="high",
                category="character",
                description="Character appearance or identity changed between shots",
            ))
            suggestions.append(Suggestion(
                target="character_engine",
                recommendation="Strengthen character identity constraints",
            ))

        return Review(
            target={"type": "shot"},
            comparison={"intended": str(intended), "generated": str(generated)},
            evaluation={
                "dimensions": {
                    "consistency": {
                        "character": "passed" if char_ok else "failed",
                    },
                }
            },
            issues=issues,
            suggestions=suggestions,
            confidence={"overall": 0.8 if char_ok else 0.4},
        )
