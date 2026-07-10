# Compiler Output: The Hanging (绞刑)

Platform: Seedance
Source: projects/the_hanging.md
Compiled: 2026-07-11
Prompt Style: Seedance-optimized (concise, visual, natural language)

---

## Global Setting

```text
Style: Republican Noir, 1930s China.
Color: Desaturated cold gray with muted green undertones, high contrast.
Lighting: Early dawn light through heavy mist, hard shadows.
Texture: Matte film grain, rough cinematic quality.
Aspect Ratio: 16:9.
Duration: 15 seconds, 4 shots.
```

---

## Shot-by-Shot Prompt

### Shot 1 (0-4s)

```text
Extreme wide shot, early dawn, a mist-covered execution ground outside an old city wall. A man in a dark long gown and felt hat stands in the foreground, back to camera, his silhouette barely visible against the thick fog. Deep in the frame, the rough silhouette of a wooden gallows emerges from the mist. Static camera. Deep focus. The atmosphere is heavy, cold, silent. 35mm lens, cold gray tones.
```

### Shot 2 (4-8s)

```text
Medium shot, the gallows. A hooded prisoner in stark white prison clothes stands on the platform, the noose hanging beside his neck. An executioner's hand rests on the lever, rough knuckles visible against worn military sleeve. The white of the prisoner's clothes is the only brightness in the frame. Static camera. Objective, almost clinical composition. 50mm lens. The moment before.
```

### Shot 3 (8-12s)

```text
Close-up on the detective's face. He watches, unblinking. His face is thin, deep-set eyes, dark circles. Side light cuts across his cheekbone, leaving half his face in shadow. For a long moment he is completely still. Then the corner of his mouth twitches — barely perceptible. A single breath escapes him. Shallow focus, 85mm lens. The first crack in the mask.
```

### Shot 4 (12-15s)

```text
Medium long shot. Off-screen: the heavy thud of the trapdoor opening, the rope snapping taut. The detective does not turn. He lowers his head slightly and walks into the fog. His silhouette fades into the gray. The sound of a single low cello note begins. A man walking away from something he doesn't yet know. Fade to black. 35mm lens, static camera.
```

---

## Full Continuous Prompt (Seedance-optimized)

```text
A 15-second Republican Noir short film. 1930s China, misty dawn execution ground outside an old city wall. Desaturated cold gray palette, high contrast, film grain texture.

Shot 1 (0-4s): Extreme wide shot. A detective in dark long gown and felt hat stands foreground, back to camera. A wooden gallows emerges from the fog in the deep background. Static. Silent. 35mm, deep focus.

Shot 2 (4-8s): Medium shot. A hooded prisoner in stark white prison clothes stands on the gallows platform. An executioner's hand on the lever. The white fabric is the only brightness. Clinical, objective. 50mm.

Shot 3 (8-12s): Close-up. The detective's face. He watches unblinking. Side light cuts across his face, half in shadow. After a long stillness, the corner of his mouth twitches. A single breath. Shallow focus, 85mm.

Shot 4 (12-15s): Medium long shot. Off-screen trapdoor opens, rope snaps taut. The detective turns and walks into the fog, silhouette fading. A low cello note begins. Fade to black. 35mm.

Tone: Cold, restrained, heavy with unseen dread. Zero dialogue. Sound design: ambient wind, one breath, one mechanical thud, one cello note.
```

---

## Compiler Notes

- Seedance 镜头运动描述使用自然语言——本片全部为静态镜头,降低了 Seedance 的生成风险
- 角色一致性: 侦探在 Shot 1(背影)→ Shot 3(面部)→ Shot 4(远景背影) 形成视觉闭环
- 白色囚衣作为全局色彩锚点,在 Shot 2 中建立视觉焦点
- 全片无对话,Seedance 对纯视觉叙事响应更稳定
- 15s 时长在 Seedance 单 clip 限制内
