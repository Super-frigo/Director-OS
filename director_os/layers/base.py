"""Base class for all layer analyzers."""

from abc import ABC, abstractmethod


class BaseLayer(ABC):
    """Each layer extracts one dimension of cinematographic context."""

    @abstractmethod
    def analyze(self, context: dict) -> dict:
        """Analyze project/intent data and return structured layer output.

        Args:
            context: dict with keys "project", "intent", "shots"

        Returns:
            dict — structured layer-specific output
        """
        ...
