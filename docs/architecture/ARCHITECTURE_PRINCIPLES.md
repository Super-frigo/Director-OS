# Director OS — Architecture Principles

## 1. Single Source of Truth

All creative decisions reside in the Project. No data is duplicated across prompts, chat logs, or agent memory. The Project is the only source that agents modify and compilers read.

## 2. Strict Layering

```
User → Director → Agents → Project → Engine → Knowledge Resolution → Compiler → Platform Prompt
```

Each layer depends only on the layer below it. Director never bypasses Agents to write raw data. Compiler never modifies Project. Compiler has no knowledge of creative intent. Knowledge Resolution is the boundary between creative intelligence and deterministic compilation.

## 3. Model Independence

The Project must never reference any AI video platform (Seedance, Veo, Kling, Runway). Platform-specific details belong exclusively in the Compiler layer. A Project created today must compile into any platform tomorrow without modification.

## 4. Last-Place Prompt

Prompt generation is always the final step in the pipeline. No creative work should ever be done in prompt space. The prompt is an export format, not a creative medium.

## 5. Structured Over Narrative

All creative data is stored as structured fields (YAML schemas), not natural language paragraphs. Structure enables validation, diffing, merging, and automated compilation.

## 6. Explicit Validation

Each Creative Cycle concludes with a validation step before committing. Consistency rules are defined upfront and checked automatically. Failed validation blocks commit, not creativity.

## 7. Immutable History

All changes to the Project are versioned. Every commit records what changed, when, and why. The Project can always be rolled back to any previous state.

## 8. Plugin Compilers

Each AI video platform has its own independent Compiler. Adding a new platform means writing a new Compiler — no changes to the core system, the Project schema, or existing Compilers.

## 9. Knowledge Resolution over Knowledge Storage

Director OS does not own filmmaking knowledge — it defines how knowledge is requested and resolved.

Knowledge can come from local rules (YAML), cached LLM responses, or future providers. The system's responsibility is the resolution pipeline: query → providers → merge → resolved knowledge. The compiler layer never sees unresolved or non-deterministic knowledge.

See [ADR-008: Knowledge Resolution Architecture](../adr/ADR-008.md).
