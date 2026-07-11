"""Layer Analyzers — Six-layer structured analysis pipeline.

Extracts rich structured data from Project/ProductionIntent
to feed the Compiler with cinematographic-grade context.

Architecture:
    Project → ProductionIntent → LayerPipeline → LayerPack (6 layers)
                                                        ↓
                                              Compiler uses layers
                                              to generate rich prompt

Each layer is independent and produces typed dict output.
"""

from typing import Any

from .base import BaseLayer


class LayerPipeline:
    """Runs all 6 layer analyzers and produces a merged LayerPack."""

    def __init__(self):
        from .l1_baseline import BaselineLayer
        from .l2_spatial import SpatialLayer
        from .l3_lighting import LightingLayer
        from .l4_camera import CameraLayer
        from .l5_character import CharacterLayer
        from .l6_microtexture import MicroTextureLayer

        self.layers: dict[str, BaseLayer] = {
            "l1_baseline": BaselineLayer(),
            "l2_spatial": SpatialLayer(),
            "l3_lighting": LightingLayer(),
            "l4_camera": CameraLayer(),
            "l5_character": CharacterLayer(),
            "l6_microtexture": MicroTextureLayer(),
        }

    def analyze(self, project, intent: dict, shots: list[dict]) -> dict:
        """Run all 6 layer analyzers.

        Args:
            project: Project dataclass (raw project data)
            intent: ProductionIntent as dict (engine output)
            shots: Extracted shot data from engine

        Returns:
            dict with keys "l1_baseline" … "l6_microtexture"
        """
        context = {
            "project": project,
            "intent": intent,
            "shots": shots,
        }
        pack = {}
        for name, layer in self.layers.items():
            pack[name] = layer.analyze(context)
        return pack
