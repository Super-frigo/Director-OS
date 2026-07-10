# Director OS
# PROJECT_SCHEMA.md

Version: 1.0.0
Status: Stable
Author: Director OS

---

# 1. Overview

Project 是 Director OS 唯一的数据源（Single Source of Truth）。

整个 AI 导演系统永远不直接修改 Prompt。

所有 Agent 都只允许修改 Project。

所有 Prompt 都由 Compiler 根据 Project 自动生成。

Workflow：

User Idea
    ↓
Creative Brief
    ↓
Project
    ↓
Story Bible
    ↓
Shot Bible
    ↓
Compiler
    ↓
Prompt

Project 描述的是"电影本身"。

而不是 Prompt。

---

# 2. Core Principles

Project 必须满足以下原则：

## 2.1 Single Source of Truth

所有内容只能存在一个地方。

例如：

角色服装

只能记录一次。

不能在 Prompt 中重复维护。

---

## 2.2 Structured

Project 必须全部采用结构化数据。

禁止长篇 Prompt。

例如：

✔

camera:
    lens: 35mm

✘

Camera uses a cinematic 35mm lens...

---

## 2.3 Immutable History

任何修改必须记录历史。

Project 永远可回滚。

---

## 2.4 Model Independent

Project 不允许出现：

Seedance

Veo

Kling

Runway

这些属于 Compiler。

Project 永远保持中立。

---

# 3. Project Structure

Project

├── Metadata
├── Creative
├── Story
├── Characters
├── World
├── Visual Language
├── Audio
├── Production
├── Story Beats
├── Shot List
├── Continuity
├── Constraints
├── Output Profile
└── History

---

# 4. Metadata

metadata:

    id:

    title:

    subtitle:

    description:

    author:

    version:

    created_at:

    updated_at:

    language:

    status:

状态：

Idea

Planning

Writing

Storyboard

Ready

Completed

Archived

---

# 5. Creative

Creative 保存导演意图。

creative:

    objective:

    audience:

    genre:

    subgenre:

    tone:

    pacing:

    emotional_arc:

    realism:

    visual_priority:

    dialogue_priority:

    action_priority:

    references:

references:

    movies:

    directors:

    cinematographers:

    animation:

    commercials:

    photography:

    artwork:

说明：

这里保存创意。

不是镜头。

---

# 6. Story

story:

    premise:

    theme:

    protagonist:

    antagonist:

    protagonist_goal:

    conflict:

    stakes:

    climax:

    ending:

    emotional_resolution:

说明：

这里保存故事。

而不是画面。

---

# 7. Characters

characters:

-

    id:

    role:

    name:

    age:

    gender:

    ethnicity:

    appearance:

    wardrobe:

    accessories:

    personality:

    motivation:

    emotion:

    voice:

    physical_state:

    continuity_lock:

physical_state：

health

injury

wetness

blood

fatigue

dirt

hair

makeup

说明：

Character State 会不断更新。

---

# 8. World

world:

    timeline:

    era:

    location:

    architecture:

    climate:

    weather:

    season:

    culture:

    technology:

    society:

说明：

World 永远独立。

以后可以生成系列作品。

---

# 9. Visual Language

visual:

    style:

    camera:

    lens:

    framing:

    composition:

    movement:

    lighting:

    color_palette:

    texture:

    atmosphere:

    environment:

说明：

摄影指导负责这里。

---

# 10. Audio

audio:

    music:

    ambience:

    dialogue:

    narration:

    sound_effects:

    silence:

    rhythm:

说明：

Audio 是独立模块。

---

# 11. Production Design

production:

    locations:

    sets:

    props:

    vehicles:

    wardrobe:

    branding:

    vfx:

说明：

美术设计。

---

# 12. Story Beats

story_beats:

-

    beat:

    objective:

    emotion:

    transition:

例如：

Opening

Conflict

Discovery

Climax

Ending

说明：

Story Beats 不等于 Shot。

一个 Beat 可以包含多个 Shot。

---

# 13. Shot List

shots:

-

    shot_id:

    beat:

    duration:

    framing:

    camera:

    lens:

    movement:

    action:

    dialogue:

    emotion:

    transition:

    notes:

说明：

Shot 是导演语言。

不是 Prompt。

---

# 14. Continuity

continuity:

    character:

    wardrobe:

    environment:

    weather:

    props:

    vehicles:

    lighting:

    color:

    camera_language:

    audio:

说明：

所有跨镜头一致性全部维护这里。

---

# 15. Constraints

constraints:

    avoid:

    required:

    safety:

    branding:

    censorship:

例如：

avoid:

extra fingers

plastic skin

floating objects

说明：

这里属于导演要求。

不是 Negative Prompt。

---

# 16. Output Profile

output:

    duration:

    aspect_ratio:

    fps:

    resolution:

    delivery:

说明：

这里只保存创作目标。

例如：

9:16

15s

24fps

不要保存模型名称。

---

# 17. History

history:

-

    version:

    timestamp:

    author:

    changes:

    notes:

说明：

所有修改全部记录。

---

# 18. Compiler Rule

Project 不允许：

×

电影描述

Prompt

自然语言模板

模型参数

Project 只保存事实。

Compiler 才负责：

Project

↓

Seedance Prompt

Project

↓

Veo Prompt

Project

↓

Kling Prompt

---

# 19. Responsibility

Creative Agent

↓

修改 Creative

Story Agent

↓

修改 Story

Character Agent

↓

修改 Characters

Camera Agent

↓

修改 Visual

Production Agent

↓

修改 Production

Shot Agent

↓

修改 Shot List

Continuity Agent

↓

修改 Continuity

Compiler

↓

只读

禁止修改 Project。

---

# 20. Design Philosophy

Director OS 不生成 Prompt。

Director OS 创作电影。

Prompt 只是电影的最终导出格式。

Project 是电影。

Prompt 只是电影的 PDF。

Project 才是真正的源文件。