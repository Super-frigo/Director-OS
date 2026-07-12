# Advertising Provider

**Type:** Local Rules
**Deterministic:** Yes
**Source:** YAML entries in this directory

## Purpose

Provides structured knowledge about advertising types, formats, and creative conventions: brand story, product demonstration, emotional resonance, social cause/PSA, duration structures (15s/30s/60s), and platform formats (vertical social vs. horizontal).

## Resolution Strategy

Keyword matching via jieba tokenization (ADR-007). Category: `storytelling` — entries are retrieved alongside story beat types and three-act structure for narrative guidance filtered by genre.

## When LLM Extension Is Needed

- Industry conventions (automotive, fashion, tech, food, luxury) — planned but not yet covered
- Viral formula analysis
- Call-to-action visual treatment refinement

## Entry Count

6 YAML entries: 4 ad types (brand story, product demonstration, emotional resonance, social cause/PSA) + 2 format/platform entries (short-form duration structure, vertical social).

## Not Yet Covered

- Industry Conventions (automotive, fashion, tech, food, luxury)
- Viral Formula Analysis
- CTA visual treatment refinement
