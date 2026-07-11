# Director OS — Anti-Patterns

> These are the specific behaviors that the [Architecture Principles](ARCHITECTURE_PRINCIPLES.md)
> forbid. Each anti-pattern maps to at least one principle.

## 1. Writing Prompts Directly

Bypassing the Project and writing platform prompts directly. This defeats
the entire purpose of Director OS — prompts become untraceable, unportable,
and unreviewable. The system exists precisely to eliminate this practice.

*Violates: [4. Last-Place Prompt](ARCHITECTURE_PRINCIPLES.md#4-last-place-prompt), [1. Single Source of Truth](ARCHITECTURE_PRINCIPLES.md#1-single-source-of-truth)*

## 2. Storing Creative Intent in Messages

Relying on chat history to remember character details, visual style, or story
decisions. The Project is the single source of truth. Information stored only
in conversation is lost when context is truncated or the session ends.

*Violates: [1. Single Source of Truth](ARCHITECTURE_PRINCIPLES.md#1-single-source-of-truth)*

## 3. Mixing Platform Concerns into the Project

Adding Seedance-specific keywords, Veo camera notations, or any platform-specific
metadata into the Project. This breaks model independence and creates migration
costs when platforms change.

*Violates: [3. Model Independence](ARCHITECTURE_PRINCIPLES.md#3-model-independence)*

## 4. Over-Specifying Before Understanding

Designing shots, lighting, and camera movements before the story is clear. This
violates the creative hierarchy (Story > Emotion > Visual > Prompt) and leads
to technically competent but emotionally empty output.

*Violates: [5. Structured Over Narrative](ARCHITECTURE_PRINCIPLES.md#5-structured-over-narrative)*

## 5. Skipping Validation

Committing design changes without running continuity checks. This inevitably
produces character mismatches, timeline contradictions, or visual inconsistencies
that are expensive to fix later.

*Violates: [6. Explicit Validation](ARCHITECTURE_PRINCIPLES.md#6-explicit-validation)*

## 6. Writing Libraries as Free-Form Notes

Storing film knowledge as unstructured text paragraphs in libraries. Libraries
must follow defined schemas so that Agents can query them programmatically.
Unstructured notes look like documentation but cannot be used by the system.

*Violates: [5. Structured Over Narrative](ARCHITECTURE_PRINCIPLES.md#5-structured-over-narrative)*

## 7. Working Without a Project

Starting a session or conversation without an associated Project file. Every
creative cycle should be grounded in a Project. Without one, there is no source
of truth, no continuity, and no path to compilation.

*Violates: [1. Single Source of Truth](ARCHITECTURE_PRINCIPLES.md#1-single-source-of-truth)*
