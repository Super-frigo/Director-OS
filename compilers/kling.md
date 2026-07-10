# Director OS — Kling Compiler

Platform: Kling (Kuaishou)
Status: Planned
Version: 0.1.0

## Overview

Kling Compiler 将 Director OS Project 编译为 Kling 可用的 Prompt。

## Kling-Specific Rules

- Use concise, action-oriented descriptions
- Physical motion and physics should be emphasized
- Camera movements should be explicitly stated
- Avoid abstract or metaphorical language

## Translation Map

| Shot Grammar         | Kling Prompt Pattern                     |
|----------------------|------------------------------------------|
| framing: CU + action | "[Subject] [action], close-up"           |
| movement: DOLLY_IN   | "Camera pushes in"                       |
| movement: TRACK_L    | "Camera moves left, following"           |
| lighting: GOLDEN_HOUR | "Shot during golden hour"              |

## Strengths

- 物理模拟效果强,适合动作/运动场景
- 对 prompt 中的运动关键词响应准确
- 支持长镜头连续运动

## Constraints

- 避免使用过多电影术语,Kling 对自然语言响应更好
- 角色一致性需要靠外观描述维持
- 镜头数量控制在合理范围

## Examples

*Coming soon.*
