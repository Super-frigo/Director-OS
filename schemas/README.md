# Director OS — YAML Schema Definitions

## Schemas

| File                          | Version | Status   |
|-------------------------------|---------|----------|
| project.schema.yaml           | 1.0     | Accepted |
| production_intent.schema.yaml | 1.0     | Accepted |
| execution_package.schema.yaml | 1.0     | Accepted |

## Purpose

All YAML schemas define the canonical data representation used across Director OS layers. These schemas are platform-independent and compiler-agnostic per ADR-001 and ADR-006.

## Pipeline

```
project.schema.yaml
        |
        v
production_intent.schema.yaml  (Engine Output)
        |
        v
execution_package.schema.yaml  (Compiler Output)
        |
        v
AI Model
```

## Design Principles

- **Project owns meaning** — "What is this film?"
- **Engine owns interpretation** — "How should this film be realized?"
- **Compiler owns translation** — "How does this model understand it?"
- **Review owns evaluation** — "Does the result match the intention?"
