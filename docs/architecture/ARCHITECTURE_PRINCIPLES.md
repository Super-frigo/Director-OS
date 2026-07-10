# Director OS — Architecture Principles

## 1. Single Source of Truth

All creative decisions reside in the Project. No data is duplicated across prompts, chat logs, or agent memory. The Project is the only source that agents modify and compilers read.

## 2. Strict Layering

```
User → Director → Agents → Project → Compiler → Platform Prompt
```

Each layer depends only on the layer below it. Director never bypasses Agents to write raw data. Compiler never modifies Project. Compiler has no knowledge of creative intent.

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
