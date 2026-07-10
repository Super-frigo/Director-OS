# Director Library

Status: Planned

## Purpose

Director Library 记录著名导演的视觉风格、镜头偏好、叙事特征,供 Director Agent 参考和借鉴。

## Planned Entries

- Christopher Nolan — 结构叙事,IMAX 摄影,实际特效
- Wes Anderson — 对称构图,色彩叙事,平面运镜
- Denis Villeneuve — 广阔构图,缓慢节奏,沉浸式声音设计
- Hayao Miyazaki — 手绘美学,飞行镜头,自然崇拜
- David Fincher — 暗调,精确构图,数字摄影
- Wong Kar-wai — 手持摄影,饱和色彩,时间碎片化

## Example Entry Format

```yaml
- director: "Denis Villeneuve"
  signature:
    - "Wide, contemplative compositions"
    - "Slow pacing with intentional silence"
    - "Massive scale with intimate character moments"
  preferred:
    framing: [ELS, MS, CU]
    lens: [35mm, 50mm]
    movement: [STATIC, SLOW_DOLLY, CRANE]
    lighting: [NATURAL, MOTIVATED]
  color_palette: "Desaturated earth tones with strategic color accents"
  avoid: ["Fast cutting", "Handheld chaos", "Overhead establishing shots"]
  influence: "Architectural backgrounds, human vs nature scale"
```
