# Composition Provider

**Type:** Local Rules
**Deterministic:** Yes
**Source:** YAML entries + composition query library

## Purpose

Provides structured knowledge about frame composition:
- Rule of thirds
- Leading lines
- Negative space
- Symmetry / Asymmetry
- Frame within frame
- Depth layering
- Balance / Dynamic tension

## Resolution Strategy

ADR-007: jieba tokenizer + controlled emotion vocabulary (`_EMOTION_MAP`).
Emotion words are resolved to standardized keywords, then matched against
entry `emotions`/`scene_types`/`keywords` fields. Composite scoring with
semantic weight (0.5) and shot-param weight (0.5).

This is the most mature local rules provider — 14 entries with a dedicated
composition query engine (`query.py`) and 45 regression tests.

## Entry Count

14 YAML entries.
