# Director OS — Architecture Decision Records

This directory documents all Architecture Decision Records (ADR) for Director OS.

## Index

| ADR       | Title                                | Status    |
|-----------|--------------------------------------|-----------|
| ADR-000   | Why Director OS Exists               | Accepted  |
| ADR-001   | Project Is The Single Source Of Truth| Accepted  |
| ADR-002   | Compiler Must Be Isolated            | Accepted  |
| ADR-003   | Engine Layer Introduction            | Accepted  |
| ADR-004   | Library Driven Knowledge System      | Superseded by ADR-008 |
| ADR-005   | Architecture Review System           | Accepted  |
| ADR-006   | Canonical Project Representation     | Accepted  |
| ADR-007   | Retrieval Strategy for Library System| Context note in ADR-008 |
| ADR-008   | Knowledge Resolution Architecture    | Accepted  |
| ADR-009   | Agent Implementation Strategy        | Accepted  |

## Template

Each ADR follows this structure:

- Context
- Decision
- Consequences
- Scope
- Non-Goals
- Alternatives Considered
- Compliance
- Design Principle

## Rules

- One ADR addresses exactly one architectural concern.
- ADRs are immutable once Accepted. Superseded ADRs are explicitly replaced by a newer ADR.

## Related

- [ARCHITECTURE_PRINCIPLES.md](../architecture/ARCHITECTURE_PRINCIPLES.md) — the canonical principles underlying these decisions
