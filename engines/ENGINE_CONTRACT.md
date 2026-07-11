# Director OS Engine Contract
# Version: 1.1 (updated for ADR-008)

## Purpose

This document defines the contract between the Director OS Project Layer and Engine Layer.

The Engine Layer is responsible for interpreting creative intent and producing platform-independent production decisions.

The Engine Layer does not generate AI model prompts.

The Engine Layer does not communicate with AI providers.

Those responsibilities belong to Compiler Layer.

---

# Architecture Position

The Engine Layer exists between Project and Compiler.

```text
Creative Intent
      |
      v
Project Representation
      |
      v
Engine Layer
      |
      v
Knowledge Resolution     ← ADR-008
      |
      v
Production Intent
      |
      v
Compiler
      |
      v
AI Model
```

---

# Engine Responsibilities

## 1. Interpretation

Convert abstract creative intent into structured production decisions.

Example:

Input:
```yaml
scene:
  emotion: loneliness
```

Engine reasoning:
```text
Loneliness often benefits from:
  - visual distance
  - negative space
  - restrained movement
  - isolated composition
```

Output:
```yaml
visual_direction:
  composition: negative_space
  camera:
    movement: restrained
```

## 2. Planning

Engine creates production strategies:

- Shot recommendations
- Visual approaches
- Character continuity rules
- Scene execution plans

## 3. Knowledge Resolution Requests

Engine requests knowledge through the Knowledge Resolution layer (ADR-008).

Flow:
```text
Project
  |
  v
Engine
  |
  v
Knowledge Request (query + context)
  |
  v
Resolution Pipeline
  ├── Local Rules (deterministic fallback)
  ├── Cached LLM (coverage extension)
  └── Future Providers
  |
  v
Resolved Knowledge (source-traceable)
  |
  v
Creative Decision
```

Engine is the consumer of knowledge, not the owner. It requests knowledge
through the resolution interface and receives resolved, source-traceable
results. Engine does not call LLM directly — that is the Resolution layer's
responsibility.

When local rules lack coverage for a specific domain, the Resolution layer
can query an LLM, cache the result, and return it deterministically.

## 4. Consistency Management

Engine ensures:

- Character continuity
- Visual continuity
- Narrative continuity

---

# Engine Input Contract

Engine receives:

```yaml
EngineInput:
  project:
    Project Representation
  context:
    optional runtime context
  resolution:
    Knowledge Resolution interface (ADR-008)
```

Example:

```yaml
engine_input:
  project:
    scene_id: scene_001
    emotion: tension
  context:
    previous_scene: scene_000
  resolution:
    available_providers: [local_rules, cached_llm]
```

---

# Engine Output Contract

Engine outputs:

```yaml
ProductionIntent
```

ProductionIntent describes:

"What should be created"

It does NOT describe:

"How a specific AI model should receive it"

---

# Engine Rules

## Rule 1: Read-Only Access

Engine must never modify Project directly.

Wrong:
```
Engine
  |
  v
Change Character Definition
```

Correct:
```
Engine
  |
  v
Suggestion / Output
  |
  v
Human Approval
  |
  v
Project Update
```

## Rule 2: Model Independence

Engine output must remain model independent.

Forbidden:
```yaml
production_intent:
  veo:
    prompt_style:
```

Allowed:
```yaml
camera:
  movement: slow_push
```

## Rule 3: Determinism

Engine must be deterministic when possible.

Same Project + same Knowledge Resolution cache should produce comparable
Production Intent. The Resolution layer's caching mechanism (ADR-008)
ensures LLM-derived knowledge is deterministic on repeat queries.

## Rule 4: Modularity

Engine capabilities should be modular.

Recommended structure:
```text
engines/
  +-- story_engine
  +-- scene_engine
  +-- character_engine
  +-- visual_engine
  +-- shot_engine
  +-- consistency_engine
  +-- production_engine
```

## Rule 5: Request Knowledge, Do Not Store It

Engine requests knowledge through the Resolution interface (ADR-008).

Engine does not:
- Call LLM directly
- Manage knowledge caches
- Decide which provider to use
- Store creative rules internally

Engine only:
- Forms knowledge requests (query + context)
- Consumes resolved knowledge
- Applies knowledge to creative decisions

---

# Engine Pipeline

Full flow:

```text
Project
  |
  v
Story Engine ──→ Knowledge Resolution
  |
  v
Scene Engine ──→ Knowledge Resolution
  |
  v
Character Engine ──→ Knowledge Resolution
  |
  v
Visual Engine ──→ Knowledge Resolution
  |
  v
Shot Engine ──→ Knowledge Resolution
  |
  v
Production Intent
  |
  v
Compiler
```

Each Engine may request knowledge independently. The Resolution layer
provides consistent, cached, source-traceable results.

---

# Engine Does NOT Do

- Generate final prompts
- Call AI video APIs
- Call LLM directly (this is the Resolution layer's responsibility)
- Store project state
- Replace human creative decisions
- Contain platform-specific knowledge
- Manage knowledge caches or provider selection

---

# Summary

Project defines: "What exists"

Engine defines: "How it should be realized"

Knowledge Resolution provides: "The filmmaking knowledge needed to decide" (ADR-008)

Compiler defines: "How machines receive it"

The Engine Layer transforms Director OS from a data system into an intelligent filmmaking system.

The Knowledge Resolution layer ensures that intelligence is powered by the best available knowledge — from local rules, cached LLM, or future providers — while maintaining the determinism the Compiler depends on.
