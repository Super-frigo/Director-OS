# Directors Provider

**Type:** Local Rules
**Deterministic:** Yes
**Source:** YAML entries in this directory

## Purpose

Provides structured knowledge about notable directors' visual styles, lens preferences, narrative signatures, and technical approaches for Director Agent reference and cross-domain style borrowing.

## Resolution Strategy

Keyword matching via jieba tokenization (ADR-007). Queries are matched against entry keywords, emotions, and genres. Category: `cinematography` — entries are retrieved alongside Camera/Lighting/Composition knowledge for `cinematography_libs` candidate pools.

## When LLM Extension Is Needed

- Directors not covered by the 6 canonical entries
- Cross-director style fusion queries (e.g., "Nolan structure with Anderson color")
- Director-specific shot language beyond the current engine guidance

## Entry Count

6 YAML entries: Christopher Nolan, Wes Anderson, Denis Villeneuve, Hayao Miyazaki, David Fincher, Wong Kar-wai.

## Known Limitation

Engine Pipeline currently retrieves by `category` granularity only; precise matching against Project `creative.references.directors` (e.g., `[Wong Kar-wai]` → automatic priority boost for `director_wong_kar_wai`) is a Phase 5/6 Engine enhancement candidate.
