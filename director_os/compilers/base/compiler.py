"""Compiler ABC — all platform compilers implement this interface."""

from abc import ABC, abstractmethod


class Compiler(ABC):
    """Each platform (Seedance, Veo, Kling, Runway) subclasses this.

    The compiler is a pure adapter — it knows nothing about:
    - What makes a good story
    - Why a shot is designed that way
    - Character motivations

    It only knows:
    > What form of information does this platform need to execute
    >   the Production Intent?
    """

    @abstractmethod
    def compile(self, production_intent: dict) -> dict:
        """Translate a Production Intent dict into an Execution Package dict."""
        ...
