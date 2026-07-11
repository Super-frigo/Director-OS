# Director OS

**AI Director Operating System** — 一套面向 AI 视频生成的结构化电影创作系统。

Director OS 不是 Prompt 工具。它是一种以 Project 为唯一数据源、Director 为唯一入口、Compiler 为最后一层的电影创作操作系统。

---

## Philosophy

```
User Ideas
    ↓
Director (创意负责人)
    ↓
Agents (专业团队)
    ↓
Project (唯一真相)
    ↓
Compiler (适配层)
    ↓
Seedance / Veo / Kling / Runway / ...
```

**核心理念:**

- **Project 是电影，不是 Prompt** — 数据源永远中立，模型只是导出格式
- **Director 是导演，不是 Prompt Engineer** — Think like a Director, never think like a Prompt Engineer
- **Compiler 是最后一层** — Prompt 永远在最后一步自动生成
- **结构化先于生成** — 故事、角色、镜头、光线全部结构化定义，确保一致性和可复用性

---

## Repository Structure

```
DirectorOS/
│
├── README.md                 # 项目总览
├── ROADMAP.md                # 开发路线图
├── CHANGELOG.md              # 变更日志
├── SYSTEM_PROMPT.md          # 可移植的 Director 系统提示
├── pyproject.toml            # Python 包定义
│
├── director_os/              # Python 核心实现
│   ├── director.py           # Director — 唯一公共入口
│   ├── cli.py                # 命令行接口
│   ├── models/               # Project / ProductionIntent / ExecutionPackage 数据模型
│   ├── engine/               # Engine 层 (story/character/visual/shot + pipeline)
│   ├── layers/               # 6 层镜头分析 (baseline/spatial/lighting/camera/character/microtexture)
│   ├── knowledge/            # Knowledge Resolution 架构 (ADR-008)
│   └── compilers/            # 平台编译器
│       ├── seedance/         # Seedance Compiler (已实现)
│       └── veo/              # Veo Compiler (已实现)
│
├── knowledge/                # 知识库 (ADR-008 Resolution 架构)
│   └── providers/
│       ├── local_rules/      # 本地 YAML 规则 (原 libraries/ 迁移至此)
│       └── llm_cache/        # LLM 响应缓存
│
├── docs/                     # 核心规范文档
│   ├── PROJECT_SCHEMA.md
│   ├── DIRECTOR_SPEC.md
│   ├── DIRECTOR_STATE_MACHINE.md
│   ├── WORKFLOW_SPEC.md
│   ├── STORY_GRAMMAR.md
│   ├── SHOT_GRAMMAR.md
│   ├── COMPILER_SPEC.md
│   ├── adr/                  # 架构决策记录 (ADR-000 ~ ADR-008)
│   ├── architecture/         # 架构原则、设计模式、反模式
│   └── spec/                 # 详细规范 (knowledge-resolution)
│
├── schemas/                  # JSON/YAML Schema 定义
├── tests/                    # 测试套件 (241+ tests)
├── projects/                 # 创作中的项目
│   ├── the_hanging.md        # 示例: 民国黑色悬疑短片
│   ├── ballroom_rendezvous.md
│   └── template.md
└── examples/                 # 项目类型模板
```

---

## Quick Start

### CLI

```bash
# 加载已有项目并编译为平台 Prompt
python -m director_os.cli load projects/the_hanging.md --compile seedance

# 验证项目结构
python -m director_os.cli validate projects/the_hanging.md

# 新建项目
python -m director_os.cli new --title "My Film" --premise "A story about..."
```

### 创作流程

1. **提出创意** — 用自然语言告诉 Director 你的想法
2. **Director 规划** — Director 会自动规划故事、角色、视觉策略
3. **逐步深化** — 与 Director 对话完善每个环节
4. **一键生成** — 完成创作后，Compiler 自动生成目标平台 Prompt

---

## Supported Platforms

| Compiler  | Status       |
|-----------|--------------|
| Seedance  | Implemented  |
| Veo       | Implemented  |
| Kling     | Planned      |
| Runway    | Planned      |

---

## License

MIT
