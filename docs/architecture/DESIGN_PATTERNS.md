# Director OS — Design Patterns

## 1. Director Facade

Director is the single public interface to the entire system. All user interaction flows through Director. Agents, Compilers, and the Project are never exposed to the user directly. This decouples the user from internal complexity and allows the system to evolve without changing the user interface.

## 2. Agent Chain of Responsibility

Each creative concern has a dedicated Agent (Story, Character, Camera, Continuity, etc.). Director dispatches work to the relevant Agent and collects results. Agents do not communicate with each other directly — all coordination happens through Director. This keeps each Agent focused and individually testable.

## 3. Compiler Strategy

Compilers implement a common interface but each uses platform-specific translation rules. Director selects the appropriate Compiler at compile time. Adding a new platform does not require modifying existing Compilers or the core system.

## 4. State Machine Pipeline

All creative work flows through a fixed state machine (DIRECTOR_STATE_MACHINE.md). States are sequential and non-skippable. This guarantees every creative output has passed through the same quality gates.

## 5. Context Object

A single Context object accumulates data as it flows through the Creative Cycle pipeline. Each state reads from and writes to the same Context. This avoids scattered state and makes the pipeline traceable.

## 6. Immutable Project, Append-Only History

The Project is never overwritten in place. New versions are created by reading the current Project, applying a diff, and writing a new version alongside the old one. History grows monotonically.

## 7. Repository Structure as System Map

The directory layout mirrors the system architecture:

```
docs/        →  System specification
libraries/   →  Domain knowledge (read-only reference data)
engines/     →  Core logic (agent implementations)
compilers/   →  Platform adapters
projects/    →  User projects (instances of the data model)
examples/    →  Sample projects for learning and testing
```
