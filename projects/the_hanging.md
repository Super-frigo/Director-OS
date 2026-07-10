# Project: The Hanging (绞刑)

metadata:
  id: proj_001
  title: The Hanging
  subtitle: 绞刑
  description: 一个民国侦探目睹了他亲手送上的绞刑，但此刻他不知死者是无辜的。
  author: Director OS
  version: 1.0.0
  status: Ready
  created_at: 2026-07-11
  updated_at: 2026-07-11
  language: zh-CN

---

## Creative

creative:
  objective: 用15秒构建一个黑色悬疑的瞬间——观众知道真相，主角不知道。
  audience: 黑色电影、悬疑短片爱好者
  genre: 黑色悬疑
  subgenre: 时代悬疑 / Republican Noir
  tone: 压抑、克制、冷峻
  pacing: 缓慢、凝重
  emotional_arc: 压抑 → 隐隐不安 → 细密的裂痕
  realism: 历史写实主义
  visual_priority: 9
  dialogue_priority: 0
  action_priority: 2
  references:
    movies:
      - 罗曼蒂克消亡史
      - 影
      - 霸王别姬 (色彩与时代感)
    directors:
      - 张艺谋 (色彩与构图)
      - 程耳 (克制叙事)
    cinematographers:
      - 杜可风 (光影质感)

---

## Story

story:
  premise: 一个民国侦探奉命监刑，绞死了一个他亲手定罪的男人，但那个男人是无辜的。
  theme: 正义的偶然性与职业面具下的裂痕
  protagonist: 无名侦探
  protagonist_goal: 完成一次例行公事的监刑
  conflict: 职业责任 vs 内心正在滋生的怀疑
  stakes: 他的整个正义信念
  climax: 机关打开的那一刻——他的脸上闪过一丝无法解释的不安
  ending: 他转身走入雾中，但有些东西已经不一样了

---

## Characters

characters:
  - id: char_detective
    role: 主角
    name: 无名侦探
    age: ~35
    gender: 男
    ethnicity: 汉族
    appearance: 瘦削面孔,深陷的眼窝,细长眉毛,薄唇
    wardrobe: 深灰长衫,黑色围巾,旧呢帽,布鞋
    accessories: 怀表,烟卷
    personality: 寡言,职业化,习惯性压抑情绪
    motivation: 他认为自己在维护正义
    physical_state: 睡眠不足,眼白有血丝
    continuity_lock: true

  - id: char_condemned
    role: 死囚
    name: 无名氏
    age: ~40
    gender: 男
    appearance: 头蒙黑布,不见面容,身形瘦弱
    wardrobe: 白色囚衣,在晨雾中显得刺眼
    physical_state: 被缚,站立
    continuity_lock: true

  - id: char_executioner
    role: 刽子手
    name: 无名氏
    appearance: 只露出一双手和半边肩膀的老旧军服袖口
    physical_state: 手按在机关上,指节粗大,布满老茧

---

## World

world:
  timeline: 民国某年,深秋
  era: 1930s Republican China
  location: 城郊刑场,一片雾中的空地,远处有老城墙轮廓
  architecture: 低矮城墙,泥土刑台,粗糙木制绞刑架
  climate: 深秋,寒冷
  weather: 晨雾,能见度低,空气潮湿
  season: 深秋/初冬
  culture: 民国末期,动荡前的平静
  technology: 绞刑架 —— 手工粗木结构,绳索

---

## Visual Language

visual:
  style: Republican Noir
  camera:
    primary_framing: MS
    primary_angle: EYE_LEVEL
    primary_lens: 50mm
    primary_movement: STATIC
    rhythm:
      avg_shot_length: 3.75s
      pacing: slow
      movement_style: static
  lighting: 黎明自然光 + 雾散射,高反差
  color_palette: 低饱和度冷灰,暗绿强调,囚衣白作为点位
  texture: 粗粝的胶片颗粒感,哑光
  atmosphere: 寒冷,潮湿,无声的压迫

---

## Story Beats

story_beats:
  - beat: OPENING
    type: OPENING
    objective: 建立空间与时代感,揭示主角位置
    emotion: 压抑的日常
    transition: CUT_TO

  - beat: THE_RITUAL
    type: INCITING
    objective: 展示绞刑执行过程
    emotion: 冰冷的仪式感
    transition: SLOW_DISSOLVE_TO

  - beat: THE_FACE
    type: REVELATION
    objective: 揭示侦探的面部反应
    emotion: 不安的初现
    transition: CUT_TO

  - beat: AFTERMATH
    type: RESOLUTION
    objective: 行刑完成,侦探离去
    emotion: 挥之不去的异样感
    transition: FADE_TO_BLACK

---

## Shot List

shots:
  - shot_id: SHOT_01
    beat_ref: OPENING
    order: 1
    duration: 4.0

    subject:
      action: 站立,背对镜头,烟卷的烟雾在雾中几乎不可分辨

    camera:
      framing: ELS
      angle: EYE_LEVEL
      height: EYE
      lens: 35mm
      movement: STATIC
      focus: DEEP_FOCUS

    composition:
      rule: RULE_OF_THIRDS
      depth: 3
      foreground: 侦探的肩部与帽沿轮廓(虚焦)
      midground: 绞刑架剪影(焦点)
      background: 城墙的模糊轮廓,雾气弥漫

    lighting:
      key_light: NATURAL
      position: BACK_45
      intensity: 3
      temperature: 6500K
      mood: 黎明前最后的暗

    color:
      palette: 冷灰 + 暗绿
      contrast: 高反差

    audio:
      silence: true
      ambience: 远处风声,几乎听不到

    transition_in: FADE_FROM_BLACK
    transition_out: CUT_TO

    emotion:
      target: 压抑
      intensity: 3

    notes: 固定机位,长焦空间压缩感。侦探站在前景偏左,绞刑架在画面深处偏右。观众一开始不一定看到绞刑架。

  - shot_id: SHOT_02
    beat_ref: THE_RITUAL
    order: 2
    duration: 4.0

    subject:
      character: char_condemned
      action: 站立等待,白色囚衣在灰暗中极为醒目

    camera:
      framing: MS
      angle: EYE_LEVEL
      height: CHEST
      lens: 50mm
      movement: STATIC
      focus: DEEP_FOCUS

    composition:
      rule: CENTER_COMPOSITION
      depth: 2
      foreground: 无
      midground: 蒙头囚犯,绞索垂在颈侧
      background: 刽子手的半身(景深中)

    lighting:
      key_light: NATURAL
      position: FRONTAL_45
      intensity: 4
      temperature: 5500K
      mood: 无情的、几乎日常化的光线

    color:
      accent: 囚衣白,画面中唯一的高明度

    audio:
      silence: true
      ambience: 布料摩擦声,木架微响

    transition_in: CUT_TO
    transition_out: SLOW_DISSOLVE_TO

    emotion:
      target: 冰冷
      intensity: 5

    notes: 客观视角,不加任何渲染。构图一丝不苟——这正是侦探眼中的例行公事。

  - shot_id: SHOT_03
    beat_ref: THE_FACE
    order: 3
    duration: 4.0

    subject:
      character: char_detective
      action: 注视着绞刑架,面无表情,但嘴角轻微抽动了一下

    camera:
      framing: CU
      angle: EYE_LEVEL
      height: EYE
      lens: 85mm
      movement: STATIC
      focus: SHALLOW_FOCUS

    composition:
      rule: CENTER_COMPOSITION
      depth: 2
      foreground: 无
      midground: 侦探的脸(焦点)
      background: 虚化的雾色背景

    lighting:
      key_light: NATURAL
      position: SIDE_90
      intensity: 5
      temperature: 5500K
      mood: 侧光凸显颧骨与眼窝的阴影

    color:
      palette: 铁灰 + 阴影蓝
      accent: 眼白血丝(暗红)
      contrast: 高反差,半边脸在暗处

    audio:
      silence: true
      ambience: 呼吸声——只有一次

    transition_in: SLOW_DISSOLVE_TO
    transition_out: CUT_TO

    emotion:
      target: 不安
      intensity: 6

    notes: 最关键的一个镜头。观众在寻找侦探的反应——他在看,但不眨眼。然后那一下极细微的嘴角抽动,快到自己都意识不到。85mm压缩面孔,侧光撕开面具。

  - shot_id: SHOT_04
    beat_ref: AFTERMATH
    order: 4
    duration: 3.0

    subject:
      character: char_detective
      action: 转身,低头,走入雾中

    camera:
      framing: MLS
      angle: EYE_LEVEL
      height: WAIST
      lens: 35mm
      movement: STATIC
      focus: DEEP_FOCUS

    composition:
      rule: RULE_OF_THIRDS + LEADING_LINES
      depth: 3

    lighting:
      key_light: NATURAL
      position: BACK
      intensity: 2
      temperature: 6500K
      mood: 人物融入背景,轮廓渐失

    color:
      palette: 全线冷灰
      contrast: 低

    audio:
      sound_effects: 机关巨响(off-screen),绳索绷直声
      music: 一声极低沉的大提琴长音(起始)
      silence: true

    transition_in: CUT_TO
    transition_out: FADE_TO_BLACK

    emotion:
      target: 沉重
      intensity: 7

    notes: 机关声来自画外。第一声也是最后一声。侦探没有回头。他走入雾中,背影越来越淡。黑色悬疑的核心——他还不知道,但观众知道,而他的一生已经变了。

---

## Audio

audio:
  music:
    - 极简,仅一声大提琴长音在片尾起,持续到黑屏后渐隐
  ambience:
    - 全程极低的环境底噪,风声,远处可能有一声乌鸦
  dialogue: 无
  silence: 全片以沉默为主,声音被当作武器使用
  rhythm: 四拍 —— 静 / 静 / 一次呼吸 / 机关声响

---

## Production

production:
  locations:
    - 城郊刑场: 开阔场地,泥土地,有老城墙背景
  props:
    - 木制绞刑架(粗糙,手工质感)
    - 黑色头罩
    - 麻绳
    - 烟卷(道具,无需点燃)
  vfx: 雾效(实拍可用烟雾机)

---

## Continuity

continuity:
  character:
    - 侦探始终戴帽,围巾位置不变
    - 白色囚衣在 Shot 2 干净,Shot 4 声效后暗示变化
  environment:
    - 全程同一地点,雾的浓度微妙变化(晨光渐亮)
  weather:
    - 有雾,无风(除环境音中的风声外)
  props:
    - 绞刑架结构始终一致
  lighting:
    - 黎明光线,从 Shot 1 到 Shot 4 微妙变亮但不明显

---

## Constraints

constraints:
  avoid:
    - 过度血腥
    - 露骨暴力
    - 历史符号滥用(避免直白的政治指向)
    - 画外解说
  required:
    - 时代细节准确
    - 情绪全靠画面传达

---

## Output Profile

output:
  duration: 15
  aspect_ratio: 16:9
  fps: 24
  resolution: 1080p
  delivery: digital

---

## History

history:
  - version: 0.1.0
    timestamp: 2026-07-11T00:00:00Z
    author: Director
    changes:
      - module: all
        action: created
    notes: 初始创意: "一个男人目睹了一场绞刑，背景是民国时代"。黑色悬疑,15s,侦探视角。完成第一版全部设计。

  - version: 1.0.0
    timestamp: 2026-07-11T00:10:00Z
    author: Director
    changes:
      - module: all
        action: completed
    notes: VALIDATE passed。Continuity 检查通过。项目状态: Ready。
