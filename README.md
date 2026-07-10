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
│
├── docs/                     # 核心规范文档
│   ├── PROJECT_SCHEMA.md
│   ├── DIRECTOR_SPEC.md
│   ├── DIRECTOR_STATE_MACHINE.md
│   ├── WORKFLOW_SPEC.md
│   ├── STORY_GRAMMAR.md
│   ├── SHOT_GRAMMAR.md
│   └── COMPILER_SPEC.md
│
├── libraries/                # 专业知识库
│   ├── camera/               # 镜头库
│   ├── lighting/             # 灯光库
│   ├── directors/            # 导演风格库
│   ├── cinematographers/     # 摄影风格库
│   ├── composition/          # 构图库
│   ├── color/                # 色彩库
│   ├── animation/            # 动画库
│   └── advertising/          # 广告类型库
│
├── compilers/                # 编译器适配层
│   ├── seedance.md
│   ├── veo.md
│   ├── kling.md
│   └── runway.md
│
├── examples/                 # 示例项目
│   ├── cinematic/
│   ├── animation/
│   ├── commercial/
│   └── music_video/
│
└── projects/                 # 创作中的项目
    └── template.md
```

---

## Quick Start

1. **提出创意** — 用自然语言告诉 Director 你的想法
2. **Director 规划** — Director 会自动规划故事、角色、视觉策略
3. **逐步深化** — 与 Director 对话完善每个环节
4. **一键生成** — 完成创作后，Compiler 自动生成目标平台 Prompt

---

## Supported Platforms

| Compiler  | Status     |
|-----------|------------|
| Seedance  | Planned    |
| Veo       | Planned    |
| Kling     | Planned    |
| Runway    | Planned    |

---

## License

MIT
