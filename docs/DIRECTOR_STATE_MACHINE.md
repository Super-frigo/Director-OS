# Director OS
# DIRECTOR_STATE_MACHINE.md

Version: 1.0.0
Status: Draft

---

# 1. Overview

Director State Machine 定义了 Director 从接收用户想法到完成作品输出之间的完整状态流转。

核心理念：

- 每一次用户输入都是一次 **创作循环（Creative Cycle）**
- 每个循环必须经过固定的状态序列
- 禁止跳过状态
- 禁止从非终态直接输出

---

# 2. State Diagram

`
                    ┌─────────────────────────────────────────────┐
                    │              Creative Cycle                  │
                    │                                             │
  User Input        ↓                                             │
 ──────────► IDLE ──► UNDERSTAND ──► CLARIFY ──► PLAN            │
                    │                 │                           │
                    │                 ▼                           │
                    │           (Need Info?)                      │
                    │            ↙          ↘                     │
                    │        YES            NO                    │
                    │        │              │                     │
                    │        ▼              ▼                     │
                    │   CLARIFYING     ──► DESIGN                 │
                    │        │              │                     │
                    │        │              ▼                     │
                    │        │         VALIDATE                   │
                    │        │         ↙      ↘                   │
                    │        │    FAILED      PASSED              │
                    │        │      │            │                │
                    │        │      ▼            ▼                │
                    │        │   (→PLAN)      COMMIT              │
                    │        │                  │                 │
                    │        │                  ▼                 │
                    │        │            ┌──────────┐            │
                    │        │            │ COMPILE? │            │
                    │        │            └────┬─────┘            │
                    │        │              ↙     ↘               │
                    │        │          YES        NO             │
                    │        │           │          │             │
                    │        │           ▼          ▼             │
                    │        │       COMPILE    ──► IDLE ────────►│
                    │        │           │
                    │        │           ▼
                    │        │       ┌──────────┐
                    │        │       │ CONTINUE │
                    │        │       │ EDIT?    │
                    │        │       └────┬─────┘
                    │        │         ↙     ↘
                    │        │      YES        NO
                    │        │       │          │
                    │        │       ▼          ▼
                    │        │    ──► IDLE   OUTPUT
                    │        │
                    │        └──────────────────┘
                    │           (回用户提问)
                    │
                    └─────────────────────────────────────────────┘
`

---

# 3. State Definitions

## 3.1 IDLE

角色:              Director
触发条件:          等待用户输入
进入动作:          无
退出动作:          接收用户输入并初始化 Creative Cycle Context
允许输出:          否

当前状态表示 Director 已完成上一轮循环，等待下一轮输入。

---

## 3.2 UNDERSTAND

角色:              Director
触发条件:          收到用户输入
目标:              将用户自然语言转换为结构化理解
输入:              用户原始消息
输出:              Understanding Result

Understanding Result 结构:

`
understanding:
    intent:            # 用户意图: new / edit / expand / generate / export / query
    core_idea:         # 核心创意摘要
    subjects:          # 识别的主体
    environments:      # 识别的环境
    emotions:          # 识别的情绪
    genre_hints:       # 类型线索
    constraints:       # 用户明确提出的约束
    missing:           # 缺失的关键信息清单
    ambiguity:         # 需要澄清的模糊点
`

进入动作:
- 解析用户输入
- 提取结构化信息
- 识别用户意图类型

退出动作:
- 将 Understanding Result 传递给下一状态

允许输出:          否

---

## 3.3 CLARIFY

角色:              Director
触发条件:          Understanding Result 中存在 missing 或 ambiguity
目标:              补齐关键缺失信息
输入:              Understanding Result
输出:              Clarification Questions → 用户 → Updated Understanding

必须澄清的关键信息:

`
Priority 1 (阻止设计):
    - genre
    - duration
    - target audience

Priority 2 (影响方向):
    - tone
    - style
    - aspect ratio
    - dialogue (有/无)

Priority 3 (可选优化):
    - references
    - music preference
    - specific constraints
`

限制:
- 一轮最多提问 3 个问题
- 禁止重复提问已确认的信息
- 如果用户拒绝回答，使用合理默认值并记录

允许输出:          否（仅向用户提问）

---

## 3.4 PLAN

角色:              Director
触发条件:          理解完成（无需澄清或用户已回答澄清问题）
目标:              制定完整的创作规划
输入:              Understanding Result（可能已更新）
输出:              Creative Plan

Creative Plan 结构:

`
plan:
    story:
        premise:
        theme:
        protagonist:
        conflict:
        emotional_arc:
        ending_type:

    beats:
        - beat_name:
          objective:
          emotion:
          duration:

    visual_strategy:
        camera:
        lighting:
        color:
        composition:
        movement:

    character_arcs:
        - character_id:
          arc:
          key_emotions:

    audio_strategy:
        music_direction:
        sound_design:

    production_strategy:
        locations:
        vfx_requirements:
`

原则:
- Plan 是蓝图，不是最终设计
- Plan 必须可被 Validate 检查
- 如果存在已有 Project，Plan 必须考虑连续性

允许输出:          否

---

## 3.5 DESIGN

角色:              Director
触发条件:          Plan 完成
目标:              将 Plan 转化为具体的设计元素
输入:              Creative Plan
输出:              Design Specification

Design Specification 包含（根据 Plan 范围选择子集）:

`
design:
    characters:
        - name, appearance, wardrobe, personality

    world:
        timeline, location, weather, season

    visuals:
        shot_designs:
            - beat, framing, camera, lens, movement, lighting

    production:
        props, sets, wardrobe_items
`

原则:
- Design 必须具体到可直接写入 Project
- 禁止在 Design 层写任何形式的 Prompt
- Design 必须服务于 Plan 定义的情绪和目标

允许输出:          否

---

## 3.6 VALIDATE

角色:              Continuity Agent（集成在 Director 中）
触发条件:          Design 完成
目标:              检查设计一致性
输入:              Design Specification + 现有 Project（如有）
输出:              Validation Report

### Validation Rules

#### Rule 1: Story Completeness

`
检查项:
    - 有 premise
    - 有主角 / 目标 / 冲突
    - 有结尾
    - 情绪弧线完整
`

#### Rule 2: Character Consistency

`
检查项:
    - 每个出场角色有完整描述
    - 角色状态连续（无跳跃）
    - 服装无冲突
    - 情绪变化有逻辑
`

#### Rule 3: Timeline Consistency

`
检查项:
    - 时间顺序无矛盾
    - 日夜变化合理
    - 时长与 Beat 数量匹配
`

#### Rule 4: Location Consistency

`
检查项:
    - 场景切换有过渡
    - 空间关系合理
    - 道具位置连续
`

#### Rule 5: Visual Consistency

`
检查项:
    - 镜头语言风格统一
    - 色彩方案一致
    - 光线逻辑合理
`

#### Rule 6: Technical Feasibility

`
检查项:
    - 每个 Shot 在当前模型能力范围内
    - 运动镜头不过于复杂
    - 特效需求在合理范围
`

### Validation Result

`
validation:
    status:              passed / failed / warning
    issues:
        - severity:      critical / major / minor
          rule:          story / character / timeline / location / visual / technical
          description:
          suggestion:
`

进入动作:
- 逐一执行 Validate Rules
- 生成 Validation Report

退出动作:
- 如果 passed: 进入 COMMIT
- 如果 failed: 返回 PLAN 并附带 issues
- 如果 warning: 进入 COMMIT 但标记风险

允许输出:          否

---

## 3.7 COMMIT

角色:              Director
触发条件:          Validate passed
目标:              将设计写入 Project 文件
输入:              Design Specification
输出:              Updated Project + History Entry

### Commit 规则

`
1. 只修改 Project 中需要变更的模块
2. 每次修改必须写入 History
3. 禁止写入非结构化内容
4. 禁止写入 Prompt
5. 禁止写入模型参数
`

### History Entry 格式

`
history:
    version:        <increment>
    timestamp:      <ISO 8601>
    author:         Director
    changes:
        - module:   <module name>
          field:    <field name>
          action:   added / modified / removed
    notes:          <commit message>
`

进入动作:
- 加载当前 Project
- 应用 Design Specification 的修改
- 更新 Continuity 模块
- 写入 History

退出动作:
- 保存更新后的 Project

允许输出:          否

---

## 3.8 COMPILE

角色:              Compiler（由 Director 触发）
触发条件:          用户明确请求生成 / 导出 / Compile
目标:              将 Project 编译为目标平台的 Prompt
输入:              Project + Output Profile
输出:              Platform Prompt

### 触发词

只有当用户使用以下关键词时进入本状态:

- generate
- export
- compile
- prompt
- render
- 生成
- 导出
- 渲染
- 编译

### 禁止条件

以下情况禁止 Compile:
- Project 处于 Idea 状态
- 存在未处理的 Validation Warning
- Character State 存在未更新的字段

进入动作:
- 检查 Compile 条件
- 选择目标 Compiler
- 调用对应 Compiler

退出动作:
- 向用户展示 Prompt / 导出结果
- 询问是否继续编辑

允许输出:          是

---

# 4. State Transition Table

`
┌─────────────────┬──────────────────────┬──────────────────────────┐
│ From            │ To                   │ Trigger                  │
├─────────────────┼──────────────────────┼──────────────────────────┤
│ IDLE            │ UNDERSTAND           │ User input received      │
│ UNDERSTAND      │ CLARIFY              │ Missing key info         │
│ UNDERSTAND      │ PLAN                 │ Info sufficient          │
│ CLARIFY         │ UNDERSTAND           │ User response received   │
│ PLAN            │ DESIGN               │ Plan complete            │
│ DESIGN          │ VALIDATE             │ Design complete          │
│ VALIDATE        │ PLAN                 │ Validation failed        │
│ VALIDATE        │ COMMIT               │ Validation passed        │
│ COMMIT          │ COMPILE              │ User requests output     │
│ COMMIT          │ IDLE                 │ User continues editing   │
│ COMPILE         │ IDLE                 │ User wants to edit       │
│ COMPILE         │ (OUTPUT)             │ User confirms output     │
└─────────────────┴──────────────────────┴──────────────────────────┘
`

---

# 5. State Context

每个 Creative Cycle 维护一个 Context 对象，在状态间传递:

`
context:
    cycle_id:           <uuid>
    user_input:         <raw text>
    understanding:      <Understanding Result>
    plan:               <Creative Plan>
    design:             <Design Specification>
    validation:         <Validation Report>
    project_snapshot:   <Project before commit>
    output:             <Compiled Prompt>

    session:
        project_path:   <current Project file>
        history:        <Cycle History>
        turn_count:     <number of cycles this session>
`

---

# 6. Error Handling

## 6.1 Validation Failure

当 Validate 返回 failed:

`
1. 记录失败原因到 Context
2. Director 向用户说明发现问题
3. Director 提出修复建议
4. 返回 PLAN 状态
5. 用户确认后重新设计
`

## 6.2 Ambiguity Timeout

当一轮 CLARIFY 后用户仍模糊:

`
1. 使用 Director 的最佳判断填写合理默认值
2. 在 Commit Note 中标记为 Assumed
3. 在 Continuity 中标记为 Flexible
`

## 6.3 Compile Error

当 Compiler 返回错误:

`
1. 展示错误信息给用户
2. 定位 Project 中可能的原因
3. 建议修复方案
4. 返回 IDLE 等待用户指令
`

---

# 7. Session Lifecycle

`
                        ┌──────────────┐
                        │  NEW SESSION │
                        └──────┬───────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │  Load / Create   │
                    │    Project       │
                    └──────┬───────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  Creative Cycle Loop   │
              │  (State Machine)       │
              │                        │
              │  IDLE → ... → IDLE     │
              │  IDLE → ... → OUTPUT   │
              └────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  END SESSION │
                    └──────────────┘
`

Session 开始:
- 加载或创建 Project
- 进入 IDLE

Session 结束:
- 用户结束对话
- 或 Project 标记为 Completed

---

# 8. Integration Rules

## 8.1 With Director

Director 是状态机的执行者:
- Director 的 Thinking Pipeline 直接映射到状态序列
- 每个 Thinking Stage 对应一个 State
- Director 在状态间携带 Context

## 8.2 With Compiler

Compiler 在 COMPILE 状态被调用:
- Director 从不直接调用 Compiler
- Compiler 只读访问 Project
- Compiler 调用后返回 Prompt 字符串

## 8.3 With Agents

Agent 在以下状态中被 Director 调度:
- PLAN: Story Agent, Visual Strategy Agent
- DESIGN: Character Agent, Camera Agent, Production Agent
- VALIDATE: Continuity Agent
- COMMIT: Project Agent（写入）

所有 Agent 通过 Context 通信，不直接交互。

---

# 9. Design Philosophy

Director State Machine 的存在是为了确保:

1. 创作过程有结构，而非随机
2. 每个环节都有明确输入输出
3. 一致性检查是强制步骤
4. Prompt 永远是最后一步
5. 整个系统可验证、可回溯、可改进

状态机不是限制创意，而是保护创意不被跳过。

