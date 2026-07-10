# Director OS
# SHOT_GRAMMAR.md

Version: 1.0.0
Status: Draft

---

# 1. Overview

SHOT_GRAMMAR 定义了 Director OS 中镜头语言的结构化表达语法。

目标:

- 镜头不再是自然语言描述
- Shot 是结构化、可组合、可参数化的元素
- Camera Agent 使用本语法设计和修改镜头
- Compiler 可将 Shot Grammar 编译为目标模型的镜头 Prompt
- 镜头语言可在不同影片间复用

---

# 2. Shot Container

一个 Shot List 是以下结构的组合:

```
shot_list:
    language:         <CameraLanguage>    # 统一摄影语言
    shots:            [Shot]
    coverage:         <CoverageStrategy>  # 覆盖策略
    continuity:       <ShotContinuity>    # 镜头间连续性
```

---

# 3. Shot Schema

```
shot:
    id:               <string>           # 唯一标识
    beat_ref:         <beat_id>          # 所属 Beat
    order:            <int>              # 镜头序号
    duration:         <float>            # 时长(秒)

    subject:
        character:    <char_id>          # 画面主体角色
        action:       <string>           # 主体动作
        position:     <string>           # 主体在画面中位置
        state:        <string>           # 主体状态(走/跑/坐/站)

    camera:
        framing:      <Framing>          # 景别
        angle:        <Angle>            # 拍摄角度
        height:       <Height>           # 机位高度
        lens:         <Lens>             # 镜头焦距
        movement:     <CameraMovement>   # 运镜方式
        focus:        <Focus>            # 焦点
        aperture:     <Aperture>         # 光圈

    composition:
        rule:         <CompositionRule>  # 构图法则
        depth:        <DepthLayers>      # 纵深感
        negative_space: <string>         # 留白
        leading_lines:  <string>         # 引导线

    lighting:
        key_light:    <LightSource>      # 主光
        fill_light:   <LightSource>      # 补光
        back_light:   <LightSource>      # 背光
        mood:         <string>           # 光线氛围
        color_temp:   <ColorTemp>        # 色温

    color:
        palette:      <string>           # 主色调
        accent:       <string>           # 强调色
        contrast:     <string>           # 对比度

    audio:
        dialogue:     <string>           # 对白内容(如有)
        sfx:          <string>           # 音效
        music:        <string>           # 音乐提示
        ambience:     <string>           # 环境音
        silence:      <bool>             # 是否静音

    transition_in:    <Transition>       # 进入本镜头的过渡
    transition_out:   <Transition>       # 离开本镜头的过渡

    emotion:
        target:       <string>           # 目标情绪
        intensity:    1-10               # 情绪强度

    notes:            <string>           # 导演笔记
```

---

# 4. Shot Element Definitions

## 4.1 Framing (景别)

```
Framing:
    - ECU              Extreme Close-Up     大特写
    - CU               Close-Up             特写
    - MCU              Medium Close-Up      中近景
    - MS               Medium Shot          中景
    - MLS              Medium Long Shot     中远景
    - LS               Long Shot            远景
    - ELS              Extreme Long Shot    大远景
    - EST              Establishing Shot    定场镜头
    - OTS              Over-The-Shoulder    过肩镜头
    - POV              Point of View        主观镜头
    - TWO_SHOT         双人镜头
    - GROUP_SHOT       群像镜头
    - INSERT           插入镜头
    - DETAIL           细节特写
```

## 4.2 Angle (拍摄角度)

```
Angle:
    - EYE_LEVEL        平视(中性)
    - HIGH_ANGLE       俯拍(弱势)
    - LOW_ANGLE        仰拍(强势)
    - BIRDS_EYE        鸟瞰(上帝视角)
    - WORMS_EYE        虫眼(极端仰拍)
    - DUTCH_ANGLE      斜角(不安感)
    - OVERHEAD         俯视(垂直向下)
    - CANTED           倾斜视角
```

## 4.3 Height (机位高度)

```
Height:
    - GROUND           地面
    - WAIST            腰部
    - CHEST            胸部
    - EYE              眼部
    - ABOVE_EYE        高于眼部
    - HIGH             高位
    - CEILING          天花板
```

## 4.4 Lens (镜头焦距)

```
Lens:
    type:             enum
    values:
        - 14mm          超广角
        - 18mm          广角
        - 24mm          广角
        - 35mm          标准广角
        - 50mm          标准
        - 85mm          人像
        - 100mm         中长焦
        - 135mm         长焦
        - 200mm         长焦
        - 400mm+        超长焦
    anamorphic:       <bool>             # 是否变形宽银幕
    macro:            <bool>             # 是否微距
    fisheye:          <bool>             # 是否鱼眼
    tilt_shift:       <bool>             # 是否移轴
```

## 4.5 Camera Movement (运镜)

```
CameraMovement:
    - STATIC             固定镜头
    - PAN_L              左摇
    - PAN_R              右摇
    - TILT_UP            上摇
    - TILT_DOWN          下摇
    - DOLLY_IN           推
    - DOLLY_OUT          拉
    - TRACK_L            左移
    - TRACK_R            右移
    - TRACK_F            前移
    - TRACK_B            后移
    - ARC_L              左环绕
    - ARC_R              右环绕
    - BOOM_UP            升
    - BOOM_DOWN          降
    - HANDHELD           手持
    - STEADICAM          斯坦尼康
    - GIMBAL             稳定器
    - CRANE              摇臂
    - DRONE              无人机
    - ZOOM_IN            变焦推
    - ZOOM_OUT           变焦拉
    - DUTCH_TILT         倾斜旋转
    - WHIP_PAN           甩镜头
    - SNAP_ZOOM          急推
    - RACK_FOCUS          焦点转移
```

## 4.6 Focus (焦点)

```
Focus:
    - DEEP_FOCUS         深焦(全部清晰)
    - SHALLOW_FOCUS      浅景深
    - RACK_FOCUS         焦点转移(A→B)
    - SOFT_FOCUS         柔焦
    - PULL_FOCUS         跟焦
    - MACRO_FOCUS        微距
    - INFRARED           红外
    - MOTION_BLUR        动态模糊
    - SPLIT_DIOPTER      分焦
```

## 4.7 Aperture (光圈)

```
Aperture:
    - f1.2               极浅景深
    - f1.4               极浅景深
    - f1.8               浅景深
    - f2.8               较浅景深
    - f4                 适中
    - f5.6               适中
    - f8                 深景深
    - f11                深景深
    - f16                极深景深
```

## 4.8 Composition Rule (构图法则)

```
CompositionRule:
    - RULE_OF_THIRDS          三分法
    - GOLDEN_RATIO            黄金比例
    - CENTER_COMPOSITION      中心构图
    - SYMMETRY                对称构图
    - LEADING_LINES           引导线
    - FRAME_WITHIN_FRAME      框中框
    - DIAGONAL                对角线
    - TRIANGULAR              三角构图
    - CIRCULAR                环形构图
    - NEGATIVE_SPACE          留白构图
    - RULE_OF_SPACE           视线空间
    - HEADROOM                头顶空间
    - LOOKROOM                视线引导
    - DYNAMIC_SYMMETRY        动态对称
    - GOLDEN_SPIRAL           黄金螺旋
    - BALANCED                平衡构图
    - ASYMMETRICAL            不对称构图
```

## 4.9 Depth Layers (纵深感)

```
DepthLayers:
    layers:           <int>            # 层次数量 2-5
    foreground:       <string>
    midground:        <string>
    background:       <string>
    technique:
        - FOREGROUND_FRAME          前景框
        - ATMOSPHERIC_PERSPECTIVE   大气透视
        - LINEAR_PERSPECTIVE        线性透视
        - DEPTH_OF_FIELD            景深分层
        - LEADING_LINES_DEPTH       引导线深度
```

## 4.10 Light Source (光源)

```
LightSource:
    type:             <LightType>
    position:         <LightPosition>
    intensity:        1-10
    temperature:      <ColorTemp>
    diffusion:        <string>
    color:            <string>

LightType:
    - NATURAL             自然光
    - HARD                硬光
    - SOFT                柔光
    - MOTIVATED           动机光
    - PRACTICAL           实际光源
    - CONTRAST            反差光
    - SILHOUETTE          剪影
    - RIM                 轮廓光
    - HAIR                发丝光
    - EYE_LIGHT           眼神光
    - NEGATIVE_FILL       负补光
    - CHIAROSCURO         明暗对比
    - THREE_POINT         三点布光
    - HIGH_KEY            高调
    - LOW_KEY             低调

LightPosition:
    - FRONT               正面光
    - THREE_QUARTER       三分之四
    - SIDE                侧光
    - RIM                 逆光
    - BACK                背光
    - TOP                 顶光
    - UNDER               底光
    - FRONTAL_45          正面45度
    - SIDE_90             侧面90度
    - BACK_45             背面45度
```

## 4.11 Color Temperature (色温)

```
ColorTemp:
    - 2000K              烛光/日落
    - 3200K              钨丝灯(暖)
    - 4300K              日出/日落
    - 5500K              日光(中性)
    - 6500K              阴天
    - 8000K+             阴影/冷色
    - VARIABLE           可变色温
```

---

# 5. Camera Language

Camera Language 定义了整部影片的统一摄影语言:

```
camera_language:
    name:             <string>
    description:      <string>

    primary_framing:  <Framing>        # 主要景别
    primary_angle:    <Angle>          # 主要角度
    primary_lens:     <Lens>           # 主力镜头
    primary_movement: <CameraMovement> # 主要运镜

    rhythm:
        avg_shot_length:  <float>      # 平均镜头时长
        pacing:           slow / medium / fast
        movement_style:   fluid / static / chaotic / smooth

    signature:
        trademarks:       [string]     # 标志性手法
        avoid:            [string]     # 避免的手法
```

示例 - 诺兰风格:

```
camera_language:
    name:             Nolan-esque
    primary_framing:  MS
    primary_angle:    EYE_LEVEL
    primary_lens:     50mm
    primary_movement: STATIC
    rhythm:
        avg_shot_length:  8
        pacing:           medium
        movement_style:   fluid
    signature:
        - Extreme wide establishing shots
        - Close-ups through foreground elements
        - Zero handheld camera
    avoid:
        - Dutch angles
        - Zoom
        - Snorricam
```

---

# 6. Coverage Strategy

Coverage Strategy 定义了如何用镜头覆盖一个 Beat:

```
coverage:
    beat_ref:         <beat_id>
    strategy:         <CoverageType>
    shot_count:       <int>

CoverageType:
    - MASTER_FIRST        主镜头+特写
    - OVERLAPPING         重叠覆盖
    - MINIMAL             最少镜头
    - EXHAUSTIVE          全面覆盖
    - SINGLE_SHOT         单镜头
    - MONTAGE             蒙太奇
    - SHOT_REVERSE_SHOT   正反打
```

---

# 7. Shot Continuity

```
shot_continuity:
    type:             <ContinuityType>
    rules:
        - rule:       <string>
          enforce:    strict / flexible

ContinuityType:
    - CLASSICAL           经典连续性
    - JUMP_CUT            跳切风格
    - BREAKING            打破连续性
    - THEMATIC            主题连续性
```

经典连续性规则示例:

```
- rule:               180度规则
  enforce:            strict
- rule:               视线匹配
  enforce:            strict
- rule:               动作匹配
  enforce:            strict
- rule:               位置一致性
  enforce:            strict
```

---

# 8. Shot Patterns

预定义的镜头模式,可直接引用:

## 8.1 Dialogue Pattern

```
pattern:
    name:             dialogue
    shots:            [OTS_A, CU_A, OTS_B, CU_B, TWO_SHOT]
    use_case:         双人对话场景
```

## 8.2 Chase Pattern

```
pattern:
    name:             chase
    shots:            [EST_LOCATION, TRACK_F, OTS_RUNNING, LOW_OBSTACLE, WHIP_PAN]
    use_case:         追逐场景
```

## 8.3 Revelation Pattern

```
pattern:
    name:             revelation
    shots:            [CU_REACTION, SLOW_DOLLY_TO_REVEAL, INSERT_DETAIL, ELS_CONTEXT]
    use_case:         揭示重要信息
```

## 8.4 Montage Pattern

```
pattern:
    name:             montage
    shots:            [CROSS_CUTS, DISSOLVE_SEQUENCE, DETAIL_SERIES]
    use_case:         时间压缩/蒙太奇
```

---

# 9. Shot Grammar Validation

Camera Agent 在提交镜头设计前必须验证:

```
- 每个 Shot 有 framing
- 每个 Shot 有 camera.angle
- 每个 Shot 有 lens
- 镜头过渡不冲突
- 180度规则未被破坏 (经典模式下)
- 视线匹配正确
- 动作匹配无误
- 镜头语言风格一致
- 每个 Shot 对应有效的 beat_ref
- 镜头总数匹配 Duration 要求
- 所有角色的 position 一致
- 道具位置在镜头间连续
- 天气/光线在连续镜头间一致
```

---

# 10. Shot to Prompt Mapping

Compiler 将 Shot Grammar 映射为不同模型的 Prompt 结构:

```
Shot Grammar
    │
    ├── Seedance Compiler
    │     └── Seedance-specific scene description
    │
    ├── Veo Compiler
    │     └── Veo camera movement notation
    │
    ├── Kling Compiler
    │     └── Kling action sequence format
    │
    └── Runway Compiler
          └── Runway frame-by-frame description
```

示例映射 (Seedance):

```
Shot 语法:
    framing:          CU
    angle:            LOW_ANGLE
    lens:             85mm
    movement:         DOLLY_IN
    subject.action:   character opens the box

Seedance Prompt:
    "Close-up, low angle, 85mm lens, dolly in as she opens the box"
```

Shot Grammar 确保无论目标模型如何变化,镜头设计保持一致。

---

# 11. Design Philosophy

Shot Grammar 的存在是为了:

1. 镜头语言是工程化的,而非即兴创作
2. 镜头风格可以作为独立模块被定义和复用
3. Camera Agent 可以独立工作
4. Compiler 将结构化镜头翻译为模型理解的 Prompt
5. 整部影片的连续性可被自动验证
6. 镜头库(Camera Library)可以不断积累
