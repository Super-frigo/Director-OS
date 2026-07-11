# Visual Style Provider

**Type:** Local Rules
**Deterministic:** Yes
**Source:** YAML entries + reference docs

## Purpose

Provides structured knowledge about visual aesthetics:
- Director styles (Denis Villeneuve, Pixar)
- Film references (Blade Runner 2049, Arcane)
- Style attributes (color, texture, lighting, composition)
- Reject lists (styles NOT to apply in certain contexts)

## Resolution Strategy

Style name matching + genre filtering.

## When LLM Extension Is Needed

- Expanding director/style library (hundreds of directors)
- Living directors with evolving styles
- Animation studio-specific aesthetics (Ghibli, Cartoon Saloon, etc.)

## Entry Count

4 style YAML entries + 4 reference docs.
