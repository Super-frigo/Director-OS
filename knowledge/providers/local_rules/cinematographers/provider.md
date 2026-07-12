# Cinematographers Provider

**Type:** Local Rules
**Deterministic:** Yes
**Source:** YAML entries in this directory

## Purpose

Provides structured knowledge about notable cinematographers' visual styles, lighting philosophies, color approaches, and technical signatures for cross-reference with Camera/Lighting/Composition domains.

## Resolution Strategy

Keyword matching via jieba tokenization (ADR-007). Queries are matched against entry keywords, emotions, and genres. Category: `cinematography` — entries are retrieved alongside Director and Camera/Lighting/Composition knowledge for `cinematography_libs` candidate pools.

## When LLM Extension Is Needed

- Cinematographers not covered by the 6 canonical entries
- Cross-cinematographer technique synthesis
- Era-specific or regional cinematography movements

## Entry Count

6 YAML entries: Roger Deakins, Emmanuel Lubezki, Hoyte van Hoytema, Bradford Young, Robert Richardson, Vittorio Storaro.
