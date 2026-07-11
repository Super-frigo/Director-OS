# Lighting Provider

**Type:** Local Rules
**Deterministic:** Yes
**Source:** YAML entries in this directory

## Purpose

Provides structured knowledge about lighting design:
- Color temperature and emotion mapping
- Light direction and emotional effect
- Lighting ratios (high-key, low-key)
- Quality (hard, soft, diffused)
- Special effects (practical, motivated, silhouette)
- Golden hour and natural light

## Resolution Strategy

Keyword + emotion matching. Mood words ("noir", "romantic", "tense") are mapped
to lighting schemes via controlled vocabulary.

## When LLM Extension Is Needed

- Complex multi-source lighting setups
- Genre-specific lighting conventions (e.g., "1980s Hong Kong neon aesthetic")
- Lighting for unusual environments (underwater, space, infrared)

## Entry Count

8 YAML entries + mood quick-reference.
