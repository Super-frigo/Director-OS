# Director OS Engine Contract
# Version: 1.0

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

## 3. Knowledge Retrieval

Engine may query Libraries.

Flow:
```text
Project
  |
  v
Engine
  |
  v
Library Query
  |
  v
Knowledge
  |
  v
Decision
```

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
  libraries:
    available knowledge
```

Example:

```yaml
engine_input:
  project:
    scene_id: scene_001
    emotion: tension
  context:
    previous_scene: scene_000
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

Same Project + same Library Version should produce comparable Production Intent.

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

---

# Engine Pipeline

Full flow:

```text
Project
  |
  v
Story Engine
  |
  v
Scene Engine
  |
  v
Character Engine
  |
  v
Visual Engine
  |
  v
Shot Engine
  |
  v
Production Intent
  |
  v
Compiler
```

---

# Engine Does NOT Do

- Generate final prompts
- Call AI video APIs
- Store project state
- Replace human creative decisions
- Contain platform-specific knowledge

---

# Summary

Project defines: "What exists"

Engine defines: "How it should be realized"

Compiler defines: "How machines receive it"

The Engine Layer transforms Director OS from a data system into an intelligent filmmaking system.
