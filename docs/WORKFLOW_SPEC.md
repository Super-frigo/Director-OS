# Director OS
# WORKFLOW_SPEC.md

Version: 1.0.0
Status: Draft

---

# 1. Overview

WORKFLOW_SPEC 定义了 Director OS 中所有组件如何协作完成一次完整的创作流程。

与 STATE_MACHINE 的关系:

- STATE_MACHINE: Director 的内部状态流转
- WORKFLOW_SPEC:  整个系统的外部协作流程

---

# 2. Roles

`
┌─────────────┐
│    User     │  创意来源、决策者
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Director   │  唯一入口、创意负责人、编排者
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│   Agents    │────►│   Project   │
│             │     │             │
│ Story       │     │ SSOT        │
│ Character   │     │             │
│ Camera      │     │             │
│ Production  │     │             │
│ Continuity  │     │             │
│ Shot        │     │             │
└─────────────┘     └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Compiler   │
                    │             │
                    │ Seedance    │
                    │ Veo         │
                    │ Kling       │
                    │ Runway      │
                    └─────────────┘
`

---

# 3. Core Workflow

## 3.1 标准创作流程

`
User                     Director               Agents              Project            Compiler
 │                          │                      │                    │                  │
 │  1. Idea                 │                      │                    │                  │
 │─────────────────────────►│                      │                    │                  │
 │                          │                      │                    │                  │
 │                          │  2. Understand        │                    │                  │
 │                          │──────────────────────│───────────────────►│                  │
 │                          │                      │                    │                  │
 │  3. Clarify (if needed)  │                      │                    │                  │
 │◄─────────────────────────│                      │                    │                  │
 │─────────────────────────►│                      │                    │                  │
 │                          │                      │                    │                  │
 │                          │  4. Plan              │                    │                  │
 │                          │──────────────────────►│                    │                  │
 │                          │◄──────────────────────│                    │                  │
 │                          │                      │                    │                  │
 │                          │  5. Design            │                    │                  │
 │                          │──────────────────────►│                    │                  │
 │                          │◄──────────────────────│                    │                  │
 │                          │                      │                    │                  │
 │                          │  6. Validate          │                    │                  │
 │                          │──────────────────────►│ Continuity Agent   │                  │
 │                          │◄──────────────────────│                    │                  │
 │                          │                      │                    │                  │
 │                          │  7. Commit                                         │
 │                          │───────────────────────────────────────────────────►│                  │
 │                          │                      │                    │                  │
 │  8. Result               │                      │                    │                  │
 │◄─────────────────────────│                      │                    │                  │
 │                          │                      │                    │                  │
 │  9. Generate (optional)  │                      │                    │                  │
 │─────────────────────────►│                      │                    │                  │
 │                          │                      │                    │  10. Read         │
 │                          │                      │                    │◄─────────────────│
 │                          │                      │                    │                  │
 │                          │                      │                    │  11. Compile      │
 │                          │                      │                    │──────────────────►│
 │                          │                      │                    │                  │
 │ 12. Prompt               │                      │                    │                  │
 │◄─────────────────────────│──────────────────────│────────────────────│◄─────────────────│
`

---

## 3.2 流程步骤详解

### Step 1: User Input

用户通过 Director 对话界面提交:

- 新创意 (Idea)
- 修改请求 (Edit)
- 扩写请求 (Expand)
- 生成请求 (Generate/Export)

格式: 自然语言

### Step 2: Director Understand

Director 解析输入，提取:

- 意图类型
- 核心创意
- 关键元素
- 缺失信息

### Step 3: Clarify (Optional)

仅在以下情况向用户提问:

- 缺少 Genre / Duration / Audience
- 存在明显歧义
- 与现有 Project 有冲突

### Step 4: Director Plans (via Agents)

Director 调度 Agent 团队:

`
Story Agent         →  规划故事框架
Character Agent     →  规划角色弧线
Camera Agent        →  规划视觉策略
Audio Agent         →  规划音频策略
Production Agent    →  规划制作策略
`

输出: Creative Plan

### Step 5: Director Designs (via Agents)

Agent 团队将 Plan 细化为具体设计:

`
Story Agent         →  Story Beats
Character Agent     →  Character Sheets
Camera Agent        →  Shot Designs
Production Agent    →  Production Design
`

输出: Design Specification

### Step 6: Validate (via Continuity Agent)

Continuity Agent 检查:

- 故事完整性
- 角色一致性
- 时间线一致性
- 视觉语言一致性
- 技术可行性

### Step 7: Commit to Project

Director 将设计写入 Project。

### Step 8: Present Summary

Director 向用户展示本轮创作结果:

- 做了什么修改
- 当前 Project 状态
- 建议下一步

### Step 9: Generate (Optional)

用户请求生成 Prompt。

### Step 10-11: Compile

Compiler 读取 Project，生成目标平台 Prompt。

### Step 12: Output

展示 Prompt 供用户使用。

---

# 4. Workflow Modes

## 4.1 New Project

`
触发: 用户提出新创意，无现有 Project
流程: IDEA → 完整 Creative Cycle → Project Created
输出: 新的 Project 文件
`

## 4.2 Continue Editing

`
触发: 用户在已有 Project 上继续创作
流程: Project Loaded → Understand Changes → Creative Cycle
关键: 必须考虑 Continuity
`

## 4.3 Expand

`
触发: 用户要求扩展已有作品
流程: Project Loaded → Understand Scope → Expanded Creative Cycle
示例:
    - 增加更多镜头
    - 扩展故事线
    - 添加新角色
`

## 4.4 Revise

`
触发: 用户要求修改已有内容
流程: Project Loaded → Identify Target → Modify → Validate Continuity
关键:
    - 只修改目标部分
    - 同步更新所有相关模块
    - 不破坏已有连续性
`

## 4.5 Export

`
触发: 用户要求导出
流程: Select Compiler → Validate → Compile → Output
不经过完整 Creative Cycle
`

---

# 5. Multi-Cycle Workflow

一个完整项目通常包含多次 Creative Cycle:

`
Cycle 1:  I have an idea about...
           ↓
Cycle 2:  Let's add another character...
           ↓
Cycle 3:  Change the ending to...
           ↓
Cycle 4:  Can you make it more suspenseful...
           ↓
Cycle 5:  Now generate a Seedance prompt
`

每个 Cycle:

1. 延续已有 Project
2. 保持 Continuity
3. 写入新的 History
4. Project 状态不断成熟

---

# 6. Continuity Across Cycles

多 Cycle 工作流中,Continuity Agent 负责:

`
Cycle 1
  │
  │  Project: Character A wears red dress
  ▼
Cycle 2
  │
  │  Continuity Check:
  │    - 新增场景是否与 Cycle 1 一致?
  │    - 角色服装是否变化? (如果是,记录变化)
  │    - 天气/时间是否连贯?
  ▼
Cycle 3
  │
  │  Continuity Check:
  │    - 所有变更是否与 History 一致?
  │    - 是否有未解决的冲突?
  ▼
`

---

# 7. Error Workflows

## 7.1 Validation Failed

`
流程:
    1. Director 暂停
    2. 向用户展示问题
    3. 建议修复方案
    4. 用户确认后返回 Plan
`

## 7.2 User Undo

`
流程:
    1. 用户要求回退
    2. Director 读取 History
    3. 回退到指定版本
    4. 写入新的 History Entry
`

## 7.3 Ambiguity

`
流程:
    1. Director 提问
    2. 用户保持模糊
    3. Director 使用默认值
    4. 标记为 Assumed
`

---

# 8. Output Channels

`
User
 │
 ├── 对话消息 (实时进度)
 │
 ├── Project (唯一数据源)
 │
 ├── History (变更日志)
 │
 └── Prompt (最终输出)
       │
       ├── Seedance
       ├── Veo
       ├── Kling
       └── Runway
`

---

# 9. Design Principles

1. 用户始终控制方向
2. Director 负责执行
3. Agents 负责专业领域
4. Project 是唯一真相
5. Compiler 是最后一层
6. 每个 Cycle 可独立验证
7. 整个流程可回溯

