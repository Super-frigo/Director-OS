# Camera Provider

**Type:** Local Rules
**Deterministic:** Yes
**Source:** YAML entries in this directory

## Purpose

Provides structured knowledge about camera language:
- Shot sizes (ECU, CU, MS, LS, ELS, etc.)
- Camera angles (eye-level, high, low, Dutch, OTS, etc.)
- Lens characteristics (24mm wide, 35mm standard, 50mm portrait, 85mm compression)
- Camera movement (dolly, tracking, handheld, steadicam, crane, static)
- Camera height (bird's eye, eye-level, low angle)

## Resolution Strategy

Keyword matching via jieba tokenization (ADR-007). Queries are matched against entry keywords,
emotions, and scene types. Composite score = semantic similarity + context field match.

## When LLM Extension Is Needed

- Unusual camera movement combinations not covered by rules
- Director-specific camera styles (e.g., "Spielberg oner", "Kubrick symmetry")
- Cross-domain queries ("camera language for surrealist romance")

## Entry Count

22 YAML entries covering angle, height, movement, shot_size, and lens subcategories.
