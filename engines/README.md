# Director OS — Engine Layer

## Contract

| File                  | Version | Status   |
|-----------------------|---------|----------|
| ENGINE_CONTRACT.md    | 1.0     | Accepted |

## Engine Modules (Planned)

- story_engine
- scene_engine
- character_engine
- visual_engine
- shot_engine
- consistency_engine
- production_engine

## Architecture

```text
Project
  |
  v
Engine Layer  ──► Library Query
  |
  v
Production Intent
  |
  v
Compiler
```

## Design Rules

- Engine is read-only on Project
- Engine output is model-independent
- Engine must be deterministic (same input + same library = same output)
- Engine capabilities are modular per pipeline stage
