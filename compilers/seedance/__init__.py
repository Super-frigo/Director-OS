"""Seedance Compiler package."""

from compilers.seedance.compile import (
    compile_project,
    project_reader,
    context_builder,
    platform_adapter,
    prompt_assembler,
    CompileContext,
    CompileResult,
    CompileError,
    PlatformPromptParts,
    ShotPromptPart,
)
from compilers.seedance.rules import (
    FRAMING_MAP,
    ANGLE_MAP,
    LENS_MAP,
    MOVEMENT_MAP,
    FOCUS_MAP,
    TRANSITION_MAP,
    lookup,
    lookup_composition,
)

__all__ = [
    "compile_project",
    "project_reader",
    "context_builder",
    "platform_adapter",
    "prompt_assembler",
    "CompileContext",
    "CompileResult",
    "CompileError",
    "PlatformPromptParts",
    "ShotPromptPart",
    "FRAMING_MAP",
    "ANGLE_MAP",
    "LENS_MAP",
    "MOVEMENT_MAP",
    "FOCUS_MAP",
    "TRANSITION_MAP",
    "lookup",
    "lookup_composition",
]
