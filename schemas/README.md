# Director OS — YAML Schema Definitions

## Schemas

| File                          | Version | Status   |
|-------------------------------|---------|----------|
| project.schema.yaml           | 1.0     | Accepted |
| production_intent.schema.yaml | 1.0     | Accepted |
| library.schema.yaml           | 1.0     | Accepted |
| execution_package.schema.yaml | 1.0     | Accepted |
| review.schema.yaml            | 1.0     | Accepted |

## Purpose

All YAML schemas define the canonical data representation used across Director OS layers. These schemas are platform-independent and compiler-agnostic per ADR-001 and ADR-006.

## Pipeline

```
project.schema.yaml  (Project Layer)
        |
        v
production_intent.schema.yaml  (Engine Output)
        |
        v
execution_package.schema.yaml  (Compiler Output)
        |
        v
AI Model
        |
        v
review.schema.yaml  (Review Feedback)
        |
        v
Improvement Loop
```

Library (`library.schema.yaml`) is queried by Engine during interpretation and receives feedback from Review.

## Design Principles

- **Project owns meaning** — "What is this film?"
- **Library owns knowledge** — "What is known about filmmaking?"
- **Engine owns interpretation** — "Which knowledge applies here?"
- **Compiler owns translation** — "How does this model understand it?"
- **Review owns evaluation** — "Does the result match the intention?"
