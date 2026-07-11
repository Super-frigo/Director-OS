# Visual Style Library

Status: Active

## Purpose

Visual Style Library stores signature visual aesthetics for Director and Camera Agent reference. Each entry describes a complete visual language — color palette, lighting philosophy, camera strategy, and emotional techniques.

## Entries

| Style | File | Core Appeal |
|-------|------|------------|
| **Arcane** | [style_arcane.yaml](entries/style_arcane.yaml) | Hand-painted 2D-3D hybrid, oil brushstrokes, dramatic chiaroscuro |
| **Blade Runner 2049** | [style_blade_runner_2049.yaml](entries/style_blade_runner_2049.yaml) | Deakins amber & teal, volumetric haze, brutalist megastructures |
| **Denis Villeneuve** | [style_denis_villeneuve.yaml](entries/style_denis_villeneuve.yaml) | Slow cinema, negative space, existential scale, naturalistic light |
| **Pixar** | [style_pixar.yaml](entries/style_pixar.yaml) | Arc aesthetics, squash-and-stretch, warm emotional animation |
| **Quality Guardrails** | [style_reject_list.yaml](entries/style_reject_list.yaml) | Four red lines: no game-CG, no over-sharpening, no plastic skin, no perfect skin |

## Usage

Director Agent binds a visual style during PLANNING stage. The style informs camera strategy, lighting design, color grading, and output profile. Multiple styles can be combined or referenced across scenes.

## Import Source

These entries were imported from the [AI-Director-OS](https://github.com/yykai893-hub/AI-Director-OS) stylebook — a knowledge and workflow framework for AIGC creative direction.
