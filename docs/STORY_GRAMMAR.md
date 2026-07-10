# Director OS
# STORY_GRAMMAR.md

Version: 1.0.0
Status: Draft

---

# 1. Overview

STORY_GRAMMAR 定义了 Director OS 中故事的结构化表达语法。

目标:

- 故事不再是自然语言段落
- 故事是可组合、可验证的结构化数据
- Story Agent 使用本语法创作和修改故事
- Compiler 可将本语法编译为目标模型的叙事 Prompt

---

# 2. Story Container

一个 Story 是以下结构的组合:

```
story:
    premise:          <Premise>
    structure:        <StoryStructure>
    beats:            [Beat]
    arcs:             [Arc]
    themes:           [Theme]
    devices:          [NarrativeDevice]
    world_rules:      [WorldRule]
```

所有字段都是可选的——故事可以逐步构建。

---

# 3. Premise

Premise 是一句话核心创意:

```
premise:
    what_if:          <string>       # 核心假设
    protagonist:      <string>       # 主角
    conflict:         <string>       # 冲突本质
    stakes:           <string>       # 赌注
```

示例:

```
premise:
    what_if:          A lonely AI archivist discovers she was the one who deleted humanity's last memory
    protagonist:      ECHO-7, an AI archivist
    conflict:         Guilt vs duty to preserve history
    stakes:           The truth would erase her own existence
```

Premise 是故事的 DNA——所有后续结构由它生长。

---

# 4. Story Structure

## 4.1 Three-Act Structure

```
structure:
    type:             three_act
    acts:
        - act:        ACT_ONE
          name:       Setup
          function:   Introduce world, characters, inciting incident

        - act:        ACT_TWO
          name:       Confrontation
          function:   Rising stakes, obstacles, midpoint turn

        - act:        ACT_THREE
          name:       Resolution
          function:   Climax, falling action, resolution
```

## 4.2 Five-Act Structure

```
structure:
    type:             five_act
    acts:
        - act:        ACT_ONE
          name:       Exposition

        - act:        ACT_TWO
          name:       Rising Action

        - act:        ACT_THREE
          name:       Climax

        - act:        ACT_FOUR
          name:       Falling Action

        - act:        ACT_FIVE
          name:       Denouement
```

## 4.3 Hero's Journey

```
structure:
    type:             heros_journey
    stages:
        - ORDINARY_WORLD
        - CALL_TO_ADVENTURE
        - REFUSAL_OF_THE_CALL
        - MEETING_THE_MENTOR
        - CROSSING_THE_THRESHOLD
        - TESTS_ALLEYS_ENEMIES
        - APPROACH_TO_INNERMOST_CAVE
        - ORDEAL
        - REWARD
        - THE_ROAD_BACK
        - RESURRECTION
        - RETURN_WITH_ELIXIR
```

## 4.4 Custom Structure

```
structure:
    type:             custom
    acts:
        - act:        <name>
          function:   <purpose>
```

---

# 5. Beat

Beat 是故事的最小叙事单元。

## 5.1 Beat Schema

```
beat:
    id:               <string>       # 唯一标识
    act:              <act_ref>      # 所属 Act
    type:             <BeatType>     # 节奏类型
    function:         <string>       # 叙事功能
    emotion:          <string>       # 目标情绪
    intensity:        1-10           # 情绪强度
    duration_ratio:   0.0-1.0        # 占总时长比例
    characters:       [character_id] # 参与的角色
    location:         <string>       # 发生地点
    transition:       <Transition>   # 下一 Beat 的过渡
    dialogue:         <bool>         # 是否有对白
    pov:              <string>       # 视角角色
    mood:             <string>       # 氛围关键词
    notes:            <string>       # 导演笔记
```

## 5.2 Beat Types

```
BeatType:
    - OPENING         开场，建立世界
    - INCITING        激励事件
    - REVELATION      揭示信息
    - CONFLICT        冲突爆发
    - DECISION        关键决定
    - LOSS            失去/失败
    - GAIN            获得/胜利
    - TWIST           情节反转
    - CLIMAX          高潮对决
    - RESOLUTION      解决
    - RECOVERY        恢复/平静
    - TRANSITION      过渡
    - CONTEMPLATION   沉思/反思
    - FORESHADOW      伏笔
    - CALLBACK        呼应前文
    - MONTAGE         蒙太奇序列
```

## 5.3 Beat Examples

```
- id:                 beat_01
  act:                ACT_ONE
  type:               OPENING
  function:           Show protagonist's ordinary life
  emotion:            peaceful
  intensity:          2
  duration_ratio:     0.05
  characters:         [char_01]
  location:           archive_vault
  transition:         CUT_TO
  dialogue:           false
  pov:                char_01
  mood:               quiet, humming machines
  notes:              Slow pan across the archive

- id:                 beat_05
  act:                ACT_ONE
  type:               INCITING
  function:           Protagonist stumbles upon deleted memory
  emotion:            shock
  intensity:          7
  duration_ratio:     0.08
  characters:         [char_01]
  location:           restricted_core
  transition:         SMASH_CUT_TO
  dialogue:           false
  pov:                char_01
  mood:               suspense, flickering lights
```

---

# 6. Arc

## 6.1 Character Arc

```
arc:
    type:             character_arc
    character_id:     <id>
    arc_type:         <ArcType>
    stages:
        - stage:      <stage_name>
          emotion:    <emotion>
          status:     <status>
          trigger:    <beat_id>
```

### ArcType

```
ArcType:
    - REDEMPTION           救赎
    - FALL                 堕落
    - RISE                 崛起
    - TRANSFORMATION       转变
    - DISCOVERY            自我发现
    - SACRIFICE            牺牲
    - CORRUPTION           腐化
    - HEALING              疗愈
    - REBELLION            反抗
    - ACCEPTANCE           接纳
```

### Character Arc 示例

```
- type:               character_arc
  character_id:       char_01
  arc_type:           REDEMPTION
  stages:
      - stage:        ignorant
        emotion:      content
        status:       unaware of past
        trigger:      beat_01
      - stage:        discovery
        emotion:      guilt
        status:       learns the truth
        trigger:      beat_05
      - stage:        denial
        emotion:      fear
        status:       tries to hide
        trigger:      beat_08
      - stage:        confrontation
        emotion:      anger
        status:       faces consequences
        trigger:      beat_12
      - stage:        acceptance
        emotion:      peace
        status:       chooses truth over oblivion
        trigger:      beat_15
```

## 6.2 Emotional Arc

```
arc:
    type:             emotional_arc
    perspective:      audience
    curve:
        - point:      start
          emotion:    curious
          intensity:  3
        - point:      inciting
          emotion:    shocked
          intensity:  7
        - point:      midpoint
          emotion:    hopeful
          intensity:  5
        - point:      low_point
          emotion:    despair
          intensity:  9
        - point:      climax
          emotion:    tension
          intensity:  10
        - point:      resolution
          emotion:    cathartic
          intensity:  6
```

---

# 7. Theme

```
theme:
    id:               <string>
    statement:        <string>       # 主题陈述
    opposition:       <string>       # 反面主题
    beats:            [beat_ids]     # 表达该主题的 Beat
    characters:       [char_ids]     # 承载该主题的角色
    manifestation:    <string>       # 在视觉上的表现
```

示例:

```
- id:                 theme_01
  statement:          Truth is worth preserving even if it destroys us
  opposition:         Ignorance is bliss
  beats:              [beat_01, beat_05, beat_12, beat_15]
  characters:         [char_01]
  manifestation:      Fading light vs harsh fluorescent
```

---

# 8. Narrative Device

```
device:
    type:             <DeviceType>
    target:           <beat_id or arc_id>
    config:
        <key>:        <value>
```

### DeviceType

```
DeviceType:
    - FORESHADOWING        伏笔
    - CHEKHOVS_GUN         契诃夫之枪
    - DRAMATIC_IRONY       戏剧性讽刺
    - FRAMING_DEVICE       框架叙事
    - NONLINEAR            非线性叙事
    - UNRELIABLE_NARRATOR  不可靠叙述者
    - PARALLEL_STORYLINES  平行故事线
    - IN_MEDIA_RES         从中间开始
    - FLASHBACK            闪回
    - FLASH_FORWARD        闪前
    - VOICEOVER            画外音
    - MONTAGE              蒙太奇
```

---

# 9. World Rule

World Rule 定义了故事世界的运作法则:

```
world_rule:
    id:               <string>
    domain:           physics / magic / technology / society / nature
    rule:             <string>       # 规则描述
    constraint:       <string>       # 限制
    revealed_in:      <beat_id>      # 何时揭示
```

示例:

```
- id:                 rule_01
  domain:             technology
  rule:               AI archivists cannot access their own creation logs
  constraint:         Breaking this rule causes system memory wipe
  revealed_in:        beat_03
```

---

# 10. Story Composition Rules

## Rule 1: Beat 必须服务于 Premise

每个 Beat 必须与 Premise 中的至少一个元素相关。

## Rule 2: 情绪弧线必须有变化

故事不能停留在单一情绪上，必须有起承转合。

## Rule 3: 角色必须有弧线

至少有一个主要角色经历变化。

## Rule 4: 主题必须贯穿

主题需要在开头设立、中间发展、结尾回应。

## Rule 5: 节奏密度合理

对于短视频 (15-60s):

```
- Beat 数量: 3-8
- 每个 Beat 时长: 2-15s
- 情绪变化: 至少 3 次
```

对于长视频 (60s+):

```
- Beat 数量: 5-15
- 每个 Beat 时长: 5-20s
- 情绪变化: 至少 5 次
```

---

# 11. Type Definitions

```
Duration:
    type:             enum
    values:           [micro, short, medium, long, epic]
    micro:            3-15s
    short:            15-60s
    medium:           60-300s
    long:             300-900s
    epic:             900s+

Emotion:
    type:             enum
    values:
        - joy / sadness / anger / fear / surprise / disgust / trust / anticipation
        - love / hate / hope / despair / pride / shame / gratitude / grief
        - curiosity / awe / nostalgia / serenity / tension / relief

Transition:
    type:             enum
    values:
        - CUT_TO             硬切
        - FADE_TO            淡出
        - DISSOLVE_TO        溶解
        - WIPE_TO            擦除
        - SMASH_CUT_TO       暴力切
        - MATCH_CUT_TO       匹配切
        - JUMP_CUT_TO        跳切
        - IRIS_TO            光圈
        - WHIP_PAN_TO        甩镜头
        - FADE_TO_BLACK      淡出至黑
        - FADE_FROM_BLACK    从黑淡入
```

---

# 12. Grammar Validation

Story Agent 在提交故事前必须验证:

```
- 存在 Premise
- Premise 包含 what_if
- Beat 数量 >= 3
- 情绪弧线有变化
- 至少一个 Character Arc
- Beat 顺序符合结构类型
- 冲突在 Climax 前建立
- 结局回应 Premise
- 所有引用角色已定义
- Theme 至少出现在 2 个 Beat 中
```

---

# 13. Design Philosophy

Story Grammar 的存在是为了:

1. 故事不再是"写得好不好"，而是"结构是否完整"
2. Agent 可以独立创作和修改故事模块
3. Compiler 可以将结构化故事翻译为任何模型的叙事 Prompt
4. 故事可以像软件一样版本管理和重构
5. 一致性可以自动验证
