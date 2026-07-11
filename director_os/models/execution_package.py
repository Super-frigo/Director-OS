"""Execution Package model — Compiler output contract."""

from dataclasses import dataclass, field


@dataclass
class ExecutionPackage:
    schema_version: str = "1.0"
    target: dict = field(default_factory=lambda: {"provider": "", "model": "", "version": ""})
    instructions: dict = field(default_factory=lambda: {"prompt": "", "actions": [], "camera": ""})
    parameters: dict = field(default_factory=lambda: {
        "duration": "", "resolution": "", "motion_strength": "", "style_preset": ""
    })
    assets: dict = field(default_factory=lambda: {"references": []})
    validation: dict = field(default_factory=lambda: {
        "warnings": [], "unsupported_features": [], "transformations": []
    })
