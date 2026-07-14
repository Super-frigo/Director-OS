# Advertising Provider

**Type:** Local Rules
**Deterministic:** Yes
**Source:** YAML entries in this directory

## Purpose

Provides structured knowledge about advertising types, formats, industry conventions, and creative strategy: brand story, product demonstration, emotional resonance, social cause/PSA, industry verticals (automotive, fashion, tech, food, luxury), viral formula analysis, CTA visual treatment, duration structures (15s/30s/60s), and platform formats (vertical social vs. horizontal).

## Resolution Strategy

Keyword matching via jieba tokenization (ADR-007). Category: `storytelling` — entries are retrieved alongside story beat types and three-act structure for narrative guidance filtered by genre.

## When LLM Extension Is Needed

- Trending platform-specific creative conventions (TikTok, YouTube Shorts, Instagram Reels format evolution)
- Category-specific sub-vertical conventions beyond the five major industries covered

## Entry Count

14 YAML entries: 4 ad types (brand story, product demonstration, emotional resonance, social cause/PSA) + 5 industry conventions (automotive, fashion, tech, food, luxury) + 2 strategy entries (viral formula, CTA visual treatment) + 2 format/platform entries (short-form duration structure, vertical social) + 1 REF reference.

## Not Yet Covered

- Trending platform-specific creative conventions (fast-moving, better suited to LLM provider)
