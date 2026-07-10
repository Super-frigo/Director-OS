# Lighting Library

Status: Planned

## Purpose

Lighting Library 存储灯光方案的知识库,为 Shot Design 提供光线参考。

## Planned Categories

- Three-Point Lighting Variations — 三点布光的变体
- Mood Lighting Schemes — 情绪光线方案( noir / romantic / suspense / dream )
- Natural Light Scenarios — 自然光场景( golden hour / blue hour / overcast )
- Practical Light Guide — 实际光源利用技巧
- Color Temperature Reference — 色温的情绪映射表
- High Key / Low Key Reference — 高调与低调光方案

## Example Entry Format

```yaml
- name: "Film Noir Key Light"
  scheme: low_key
  setup:
    key: "Hard light from 45-degree upper side"
    fill: "Minimal fill, 1:8 ratio"
    back: "Rim light for silhouette separation"
  mood: "Mysterious, tense, dramatic"
  best_for:
    - detective scenes
    - psychological tension
    - character reveal moments
  color_temp: 3200K
  notes: "The darker the shadows, the more hidden the truth."
```
