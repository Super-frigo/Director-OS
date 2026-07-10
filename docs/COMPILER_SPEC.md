# Director OS
# COMPILER_SPEC.md

Version: 1.0.0
Status: Draft

---

# 1. Overview

Compiler 是 Director OS 的最后一层——将结构化的 Project 编译为目标 AI 视频平台的 Prompt。

核心原则:

- Compiler **只读** Project,永不修改
- Compiler **不知道** 电影创作——它只负责翻译
- 每个平台有独立的 Compiler 实现
- 新的平台 = 新的 Compiler,无需修改系统其他部分

---

# 2. Compiler Architecture

```
Project (Structured Data)
    │
    ▼
┌─────────────────────────────────────┐
│           Compiler Pipeline         │
│                                     │
│  Project Reader                     │
│       │                             │
│       ▼                             │
│  Context Builder                    │
│       │                             │
│       ▼                             │
│  Platform Adapter  ───►  Rules      │
│       │                             │
│       ▼                             │
│  Prompt Assembler                   │
│                                     │
└─────────────────┬───────────────────┘
                  │
                  ▼
      Platform-Specific Prompt
```

---

# 3. Pipeline Stages

## Stage 1: Project Reader

读取 Project 并验证完整性。

```
Input:  Project file path
Output: Parsed Project object

Validation:
    - 必须存在 Metadata
    - 必须存在 Creative
    - 至少 1 个 Story Beat
    - 至少 1 个 Shot
    - Continuity 无冲突

如果验证失败:
    - 返回错误列表
    - 不进入下一阶段
```

## Stage 2: Context Builder

从 Project 构建统一的编译上下文.

```
Input:  Parsed Project
Output: CompileContext

CompileContext:
    project:          <Project>

    story_context:
        beats:        [Beat]
        arcs:         [CharacterArc]
        themes:       [Theme]

    visual_context:
        language:     <CameraLanguage>
        shots:        [Shot]
        continuity:   <Continuity>

    character_context:
        characters:   [Character]
        current_state: <CharacterStateMap>

    world_context:
        timeline:     <Timeline>
        location:     <Location>
        weather:      <Weather>

    output_context:
        duration:     <float>
        aspect_ratio: <string>
        fps:          <int>
        resolution:   <string>
```

## Stage 3: Platform Adapter

根据目标平台,应用平台特定的翻译规则。

```
Input:  CompileContext
Output: PlatformPromptParts

Platform Adapter 负责:
    - 将 Shot Grammar 翻译为目标平台的镜头描述格式
    - 应用平台的语法约束
    - 处理平台特有的参数
    - 遵循平台的最佳实践
```

## Stage 4: Prompt Assembler

将翻译后的 Parts 组装为最终 Prompt 字符串。

```
Input:  PlatformPromptParts
Output: Final Prompt String

Assembly Rules:
    - 镜头按 Shot List 顺序排列
    - 全局设置(风格/光线/色彩)放在开头
    - 角色状态在对应镜头前声明
    - 一致性描述在需要处穿插
```

---

# 4. Compiler Interface

```
compile(
    project_path:   string,      # Project 文件路径
    platform:       Platform,    # 目标平台
    options?:       CompileOptions
) -> CompileResult

CompileOptions:
    verbose:        bool         # 是否输出编译过程
    strict:         bool         # 是否严格模式
    style:          concise / detailed  # Prompt 风格

CompileResult:
    success:        bool
    prompt:         string       # 最终 Prompt
    warnings:       [Warning]
    errors:         [Error]
    stats:
        shots_compiled:  int
        tokens_estimated: int
        duration_seconds: float
```

---

# 5. Platform Translation Rules

## 5.1 Shot to Prompt

```
Shot Grammar                  →   Platform Prompt
──────────────────────────────────────────────────
framing: CU                   →   "close-up shot"
framing: ELS + movement       →   "wide establishing shot with"
lens: 85mm                    →   "85mm lens"
movement: DOLLY_IN + CU       →   "slow dolly in on"
movement: TRACK_L + MS        →   "tracking left past"
lighting: LOW_KEY + mood      →   "low-key lighting, moody"
transition: FADE_TO_BLACK     →   "fade to black"
```

## 5.2 Context Insertion Rules

```
- 首次出现的角色:          全描述 + 状态
- 后续出现的角色:          仅状态变化
- 首次出现的场景:          全场景描述
- 后续出现的场景:          仅变化描述
- 天气/光线变化:          在对应镜头前插入
```

---

# 6. Compiler Validation

编译完成后,Compiler 必须自检:

```
- 所有 Shot 已被编译
- 无重复内容
- 角色名一致
- 镜头顺序正确
- 时长与 Output Profile 匹配
- 无平台不支持的特性
```

---

# 7. Adding a New Platform

1. 创建 `compilers/<platform>.md` 规范文档
2. 实现 Platform Adapter
3. 定义 Prompt Assembly 规则
4. 注册到 Compiler Registry

Compiler 架构确保平台适配是插件化的——核心系统无需修改。

---

# 8. Design Philosophy

Compiler 的存在是为了确保:

1. Project 永远保持模型中立
2. Prompt 是自动生成的,而非手写的
3. 新模型支持 = 新 Compiler,不影响既有 Project
4. 输出质量可通过优化 Compiler 规则持续提升
5. 整个系统可扩展,不绑定任何单一平台
