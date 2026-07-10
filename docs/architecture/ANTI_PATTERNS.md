# Director OS — Anti-Patterns

## 1. Writing Prompts Directly

Bypassing the Project and writing platform prompts directly. This defeats the entire purpose of Director OS — prompts become untraceable, unportable, and unreviewable. The system exists precisely to eliminate this practice.

## 2. Storing Creative Intent in Messages

Relying on chat history to remember character details, visual style, or story decisions. The Project is the single source of truth. Information stored only in conversation is lost when context is truncated or the session ends.

## 3. Mixing Platform Concerns into the Project

Adding Seedance-specific keywords, Veo camera notations, or any platform-specific metadata into the Project. This breaks model independence and creates migration costs when platforms change.

## 4. Over-Specifying Before Understanding

Designing shots, lighting, and camera movements before the story is clear. This violates the creative hierarchy (Story > Emotion > Visual > Prompt) and leads to technically competent but emotionally empty output.

## 5. Skipping Validation

Committing design changes without running continuity checks. This inevitably produces character mismatches, timeline contradictions, or visual inconsistencies that are expensive to fix later.

## 6. Writing Libraries as Free-Form Notes

Storing film knowledge as unstructured text paragraphs in libraries. Libraries must follow defined schemas so that Agents can query them programmatically. Unstructured notes look like documentation but cannot be used by the system.

## 7. Working Without a Project

Starting a session or a conversation without an associated Project file. Every creative cycle should be grounded in a Project. Without one, there is no source of truth, no continuity, and no path to compilation.
