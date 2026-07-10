# Director OS — Seedance Compiler

Platform: Seedance
Status: Planned
Version: 0.1.0

## Overview

Seedance Compiler 将 Director OS Project 编译为 Seedance 平台可用的 Prompt。

## Seedance-Specific Rules

- Describe visual composition in natural language
- Maintain aspect ratio: 9:16 (default), 16:9, 1:1
- Maximum duration: 15s per clip
- Character descriptions should be detailed for consistency

## Translation Map

| Shot Grammar     | Seedance Prompt Pattern                   |
|------------------|-------------------------------------------|
| framing: CU      | "Close-up shot of"                        |
| framing: LS      | "Wide shot showing"                       |
| movement: DOLLY  | "Camera slowly moves toward"              |
| lighting: LOW_KEY | "Low-key lighting atmosphere"            |

## Constraints

- Seedance 对镜头运动的描述采用自然语言
- 角色一致性需要在前几个镜头中建立足够描述
- 避免复杂的光线变化,Seedance 在连续镜头中保持光线更稳定

## Examples

*Coming soon.*
