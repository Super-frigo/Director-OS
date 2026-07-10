# Director OS Compiler Contract
# Version: 1.0

## Purpose

This document defines the contract between Director OS Production Intent Layer and external AI generation systems.

The Compiler Layer translates platform-independent production decisions into platform-specific execution instructions.

The Compiler Layer is responsible for:

- Translation
- Adaptation
- Formatting
- Capability mapping

The Compiler Layer is NOT responsible for:

- Creative reasoning
- Story interpretation
- Director decisions
- Knowledge management

---

# Architecture Position

```
Production Intent
        |
        v
Compiler Layer
        |
        v
Execution Package
        |
        v
AI Model
```

---

# Core Principle

Compiler answers:

"How does this platform understand this intention?"

Compiler does NOT answer:

"What should this film be?"

---

# Compiler Input Contract

Compiler receives:

```yaml
CompilerInput:
  production_intent:
    Production Intent Object
  target:
    platform
    model
  capabilities:
    optional model capability data
```

Example:

```yaml
compiler_input:
  production_intent:
    scene_id: scene_001
    camera_strategy:
      movement: slow_push
  target:
    platform: video_model
    model: target_model
```

---

# Compiler Output Contract

Compiler outputs:

```yaml
ExecutionPackage
```

Definition:

> Execution Package is a platform-specific representation ready for AI model execution.

---

# Compiler Responsibilities

## 1. Semantic Translation

Convert:

```yaml
# Production Intent
camera:
  movement: slow_push
```

into:

```yaml
# Model Instruction
camera_motion: dolly_forward
```

## 2. Capability Mapping

Different models support different capabilities.

Example:

Production Intent: `lighting: volumetric`

Model A: `supported: volumetric_lighting`

Model B: `approximation: atmospheric_effect`

Compiler handles this difference.

## 3. Format Generation

Compiler creates:

- API payloads
- Prompt formats
- Parameter structures

---

# Compiler Rules

## Rule 1: Cannot Modify Creative Intent

Wrong: Compiler changes story emotion.

Correct: Compiler translates emotion.

## Rule 2: Must Be Replaceable

Adding a new model must not modify: Project, Engine, Library, Review.

## Rule 3: Knowledge Is Platform Knowledge Only

Compiler may know: model capabilities, parameter ranges, API formats.

Compiler must not know: storytelling, emotion meaning, character development.

## Rule 4: Should Be Deterministic

Same Production Intent + same Compiler Version + same Model Version should produce comparable Execution Package.

---

# Error Handling

Compiler must expose:

- Unsupported Capability
- Approximation
- Invalid Input

---

# Compiler Does NOT Do

- Create stories
- Design shots
- Select emotions
- Modify characters
- Store creative memory
- Learn creative style

---

# Summary

Compiler is the boundary between Creative Intelligence and Machine Execution.

Project describes the film.
Engine decides how to realize it.
Production Intent describes the execution goal.
Compiler translates the goal.
AI models perform the generation.

Compiler enables Director OS to evolve independently from any single AI platform.
