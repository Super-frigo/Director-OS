# Camera Library

Status: Planned

## Purpose

Camera Library 存储镜头设计与焦距方案的知识库,供 Camera Agent 在规划和设计时参考。

## Structure

Each entry follows `SHOT_GRAMMAR.md` schema.

## Planned Categories

- Focal Length Encyclopedia — 每种焦距的视觉特征与适用场景
- Camera Movement Reference — 每种运镜的情绪效果
- Framing Guide — 景别选择与叙事意图
- Signature Lens Packages — 著名导演的镜头组合方案
- Lens Character Profiles — 镜头的光学特性(畸变/散景/呼吸效应)

## Example Entry Format

```yaml
- name: "The 35mm Standard"
  category: focal_length
  characteristics:
    - "Wide enough for context, tight enough for intimacy"
    - "Minimal distortion, natural perspective"
    - "The human eye equivalent"
  best_for:
    - dialogue scenes
    - documentary style
    - grounded, realistic narratives
  used_by:
    - Steven Soderbergh
    - Ken Loach
  notes: "The most versatile focal length. Default for neutral storytelling."
```

## Usage

Camera Agent 在 DESIGN 阶段查询此库,为每个 Shot 选择或推荐镜头配置。
