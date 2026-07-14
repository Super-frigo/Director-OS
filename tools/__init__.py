"""Director OS — Knowledge Library Bootstrap tools.

Four-layer generation pipeline with quality gates.

Layers:
  1. Taxonomy     — entry checklist per category
  2. Skeleton     — full schema-compliant YAML
  3. Relationship — cross-entry relationship graph
  4. Deepening    — examples + extra depth for priority entries

Gates:
  1. Schema       — YAML structure validation
  2. Consistency  — LLM-based review (accuracy/completeness/practicality)
  3. Crossref     — bidirectional relationship validation + auto-fix
  4. Spotcheck    — human review report generation
"""
