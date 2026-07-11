# Project: Ballroom Rendezvous (舞会重逢)

metadata:
  id: proj_002
  title: Ballroom Rendezvous
  subtitle: 舞会重逢
  description: 公主般的女子从弧形楼梯优雅走下，大厅中男子等候，胶片质感的浪漫重逢。
  author: Director OS
  version: 1.0.0
  status: Ready
  created_at: 2026-07-11
  updated_at: 2026-07-11
  language: zh-CN

---

## Creative

creative:
  objective: 用15秒构建浪漫柔刚反差的沉浸瞬间——胶片复古与超写实肌理的碰撞。
  audience: 电影级AI视频、奢侈品牌、情感短片
  genre: 浪漫剧情
  subgenre: 复古写实 / Retro Realism
  tone: 松弛丝滑、柔中带刚、温暖期待
  pacing: 温柔优雅、舒缓
  emotional_arc: 期待 → 喜悦收敛 → 心动呼应
  realism: 超写实 + 胶片复古融合
  visual_priority: 10
  dialogue_priority: 0
  action_priority: 8
  references:
    movies:
      - 了不起的盖茨比 (舞会场面与构图)
      - 花样年华 (色彩与旗袍质感)
      - 罗马假日 (公主气质)
    directors:
      - 王家卫 (色彩与情绪)
      - 巴兹·鲁赫曼 (华丽运镜)
    cinematographers:
      - 杜可风 (光影质感)
      - 罗德里戈·普列托 (胶片色彩)

---

## Story

story:
  premise: 女生犹如公主般优雅地从弧形楼梯上下来，表情愉悦收敛，仿佛看到了梦中期待的王子忍不住期待的样子，大厅中男生在等候。
  theme:
    - 浪漫重逢
    - 瞬间的永恒
    - 期待与回应的张力
  genre:
    - 浪漫
    - 复古写实
    - 情感

---

## Characters

characters:
  - id: female_lead
    role: 女主角
    name: 她
    gender: 女
    age: ~25
    appearance: 精致五官，雪白肌肤，长发盘起
    wardrobe: 优雅晚礼服，丝绸质感
    personality: 优雅、喜悦中带着收敛
    motivation: 期待见到他
    physical_state: 优雅、容光焕发

  - id: male_lead
    role: 男主角
    name: 他
    gender: 男
    age: ~28
    appearance: 英俊正装，挺拔身姿
    wardrobe: 深色西装，领结
    personality: 期待、深情凝望
    motivation: 等待她到来
    physical_state: 静立、期待

---

## World

world:
  era: 当代/复古融合
  location: 豪华庄园大厅
  architecture: 欧式古典，弧形大理石楼梯，水晶吊灯
  climate: 室内，温暖
  weather: 晴夜

---

## Visual Language

visual:
  style: Retro Realism — 胶片复古颗粒与超写实肌理融合
  camera:
    primary_framing: MS
    primary_angle: EYE_LEVEL
    primary_lens: 24mm
    primary_movement: GIMBAL
    rhythm:
      avg_shot_length: 3.75s
      pacing: smooth
      movement_style: fluid
  camera_body: ARRI Alexa65
  lens_character: 旋焦散景、轻微色差，通透无过度锐化
  lighting: 全局光照+SSS，还原超写实毛孔、绒毛、衣物纹理，高光不溢出
  color_palette: Kodak Portra 400 暖棕基底+冷青灰调，红/绿/黑豪车形成视觉冲击
  film_stock: Kodak Portra 400
  color_grade: 暖棕基底+冷青灰调
  texture: 胶片颗粒柔化锐利感，色调随光影自然过渡
  atmosphere: 柔和、梦幻、温暖
  render_engine: PBR 物理渲染
  render_settings: 全局光照+SSS，8K输出，超写实毛孔、绒毛、衣物纹理，高光不溢出

---

## Story Beats

story_beats:
  - beat: DESCENT
    type: OPENING
    objective: 女生从弧形楼梯上往下走，展现优雅气质
    emotion: 期待
    transition: FADE_IN

  - beat: MEETING_GAZE
    type: INCITING
    objective: 男女主目光交汇，情绪升温
    emotion: 心动
    transition: CUT_TO

  - beat: THE_WAIT
    type: RESOLUTION
    objective: 男生注视女生走来，情绪收敛但深情
    emotion: 温暖
    transition: FADE_TO_WHITE

---

## Shot List

shots:
  - shot_id: SHOT_01
    beat_ref: DESCENT
    order: 1
    duration: 5.0
    subject:
      character: female_lead
      action: 从弧形楼梯上优雅走下，手轻轻扶着楼梯扶手
    camera:
      framing: MLS
      angle: LOW_ANGLE
      height: GROUND
      lens: 24mm
      movement: GIMBAL
      focus: DEEP_FOCUS
    composition:
      rule: CENTER_COMPOSITION
      depth: 3
      foreground: 楼梯扶手(虚化)
      midground: 女生从楼梯走下(焦点)
      background: 水晶吊灯与大厅
    lighting:
      key_light: MOTIVATED
      position: TOP
      intensity: 7
      temperature: 4300K
      mood: 柔和顶光勾勒轮廓
    color:
      palette: 暖棕基底+冷青灰调
      contrast: 柔和
    transition_in: FADE_FROM_BLACK
    transition_out: CUT_TO
    emotion:
      target: 期待
      intensity: 7

  - shot_id: SHOT_02
    beat_ref: MEETING_GAZE
    order: 2
    duration: 5.0
    subject:
      character: female_lead
      action: 走完最后一级台阶，抬头看向大厅中的男生，表情愉悦收敛
    camera:
      framing: CU
      angle: EYE_LEVEL
      height: EYE
      lens: 85mm
      movement: STATIC
      focus: SHALLOW_FOCUS
    composition:
      rule: RULE_OF_THIRDS
      depth: 2
    lighting:
      key_light: SOFT
      position: FRONTAL_45
      intensity: 6
      temperature: 4300K
      mood: 柔光映照脸庞，眼神明亮
    color:
      palette: 暖棕基底
      contrast: 柔和
    transition_in: CUT_TO
    transition_out: CUT_TO
    emotion:
      target: 心动的喜悦
      intensity: 8

  - shot_id: SHOT_03
    beat_ref: THE_WAIT
    order: 3
    duration: 5.0
    subject:
      character: male_lead
      action: 静立在大厅，深情凝望走来的女生，嘴角微扬
    camera:
      framing: MS
      angle: EYE_LEVEL
      height: EYE
      lens: 50mm
      movement: STATIC
      focus: SHALLOW_FOCUS
    composition:
      rule: RULE_OF_THIRDS
      depth: 2
      background: 大厅背景(虚化)
    lighting:
      key_light: MOTIVATED
      position: BACK_45
      intensity: 5
      temperature: 3200K
      mood: 暖色背景光勾勒
    color:
      palette: 暖棕
      contrast: 柔和
    transition_in: CUT_TO
    transition_out: FADE_TO_WHITE
    emotion:
      target: 深情期待
      intensity: 7

---

## Production

production:
  locations:
    - 豪华欧式庄园大厅：大理石弧形楼梯，水晶吊灯，古典陈设
  props:
    - 弧形楼梯(大理石材质)
    - 水晶吊灯
    - 豪车(红/绿/黑)
  vehicles:
    - 红色跑车
    - 绿色豪华轿车
    - 黑色轿车
  vfx: 胶片颗粒叠加，暖色调色，柔光效果

---

## Audio

audio:
  music: 舒缓古典钢琴/弦乐，渐强至相遇瞬间
  ambience: 大厅空旷的脚步声，水晶灯轻响
  silence: false

---

## Continuity

continuity:
  character:
    - 女生服装位置始终一致
    - 男生始终在大厅同一位置
  environment:
    - 同一大厅，灯光从亮到柔渐变换
  lighting:
    - 整体暖色调基调维持一致
    - 光影随女生下楼自然过渡

---

## Output Profile

output:
  duration: 15
  aspect_ratio: 16:9
  fps: 24
  resolution: 8K
  delivery: digital

---

## Constraints

constraints:
  avoid:
    - 过度锐化
    - 塑料感皮肤
    - 过度曝光
    - 人物变形
  required:
    - 毛孔细节清晰
    - 衣物纹理真实
    - 光影自然过渡
    - 胶片颗粒质感
