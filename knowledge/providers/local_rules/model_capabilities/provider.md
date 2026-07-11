# Model Capabilities Provider

**Type:** Local Rules
**Deterministic:** Yes
**Source:** YAML entries in this directory

## Purpose

Provides structured knowledge about AI video model capabilities:
- Seedance: supported parameters, constraints, best practices
- Veo: supported parameters, constraints, best practices
- Kling: supported parameters, constraints, best practices

## Resolution Strategy

Direct model name matching. Used by Compiler to apply platform constraints.

## When LLM Extension Is Needed

- New model versions with changed capabilities
- New platforms (Runway Gen-4, Pika 2.0, etc.)
- Model-specific prompt engineering strategies

## Entry Count

3 YAML entries (one per model).
