# Director OS — Veo Compiler

Platform: Veo (Google DeepMind)
Status: Planned
Version: 0.1.0

## Overview

Veo Compiler 将 Director OS Project 编译为 Veo 平台可用的 Prompt。

## Veo-Specific Rules

- Use structured scene descriptions
- Support longer-form video (60s+)
- Camera movement notation should be explicit
- Cinematic terminology strongly supported

## Translation Map

| Shot Grammar     | Veo Prompt Pattern                        |
|------------------|-------------------------------------------|
| framing: CU      | "Close-up"                                |
| framing: ELS     | "Extreme wide shot"                       |
| angle: LOW_ANGLE | "Low angle camera"                        |
| movement: CRANE  | "Crane shot rising"                       |

## Strengths

- Veo 对电影术语理解较好,可以使用更专业的摄影语言
- 支持更长的视频时长(60s+)
- 镜头运动模拟更流畅

## Constraints

- 角色一致性需要 describe appearance in each scene
- 光线变化描述需逐镜明确

## Examples

*Coming soon.*
