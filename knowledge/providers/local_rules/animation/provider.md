# Animation Provider

**Type:** Local Rules
**Deterministic:** Yes
**Source:** YAML entries in this directory

## Purpose

Provides structured knowledge about animation styles and techniques for animation-class projects: 2D hand-drawn, 3D cel-shaded (三渲二), stop-motion, motion graphics, the twelve principles of animation, and frame rate conventions.

## Resolution Strategy

Keyword matching via jieba tokenization (ADR-007). Category: `visual_style` — entries are retrieved alongside visual style references for style guidance.

## When LLM Extension Is Needed

- VFX animation (particles, fluids, cloth simulation) — planned but not yet covered
- Hybrid techniques combining multiple animation styles
- Project-specific animation pipeline decisions beyond style guidance

## Entry Count

5 YAML entries (2D hand-drawn, 3D cel-shaded, stop-motion, motion graphics, twelve principles) + 1 REF reference (frame rate quick reference, excluded from Engine retrieval).

## Not Yet Covered

- Visual Effects Animation (particles, fluids, cloth simulation)
