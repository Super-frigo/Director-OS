# CHANGELOG

## 1.1.0 (2026-07-12)

### Added

- **knowledge/providers/local_rules/directors/** — 6 director style entries (Christopher Nolan / Wes Anderson / Denis Villeneuve / Hayao Miyazaki / David Fincher / Wong Kar-wai), `category: cinematography`
- **knowledge/providers/local_rules/cinematographers/** — 6 cinematographer style entries (Roger Deakins / Emmanuel Lubezki / Hoyte van Hoytema / Bradford Young / Robert Richardson / Vittorio Storaro), `category: cinematography`
- **knowledge/providers/local_rules/animation/** — 5 animation style/technique entries (2D hand-drawn / cel-shaded / stop motion / motion graphics / 12 principles + 1 REF frame rate quick reference, excluded from retrieval), `category: visual_style`
- **knowledge/providers/local_rules/advertising/** — 6 ad type & format entries (brand story / product demonstration / emotional resonance / social cause PSA / duration structure / vertical vs horizontal platform), `category: storytelling`
- Phase 2 knowledge libraries now complete (all 11 domains populated)

### Known Gaps (documented in provider.md files)

- Animation Library: VFX Animation (particles/fluids/cloth) not yet covered
- Advertising Library: Industry Conventions, Viral Formula Analysis, CTA refinement not yet covered
- Engine Pipeline: precise matching by Project `creative.references` named directors/cinematographers not yet implemented (Phase 5/6 candidate)

## 1.0.0 (2026-07-11)

### Added

- **PROJECT_SCHEMA.md** — 完整 Project 数据模型定义,包含 18 个模块
- **DIRECTOR_SPEC.md** — Director 角色规范与 7 阶段思维管线
- **DIRECTOR_STATE_MACHINE.md** — 8 状态状态机定义,完整转换表与验证规则
- **WORKFLOW_SPEC.md** — 五方协作流程,5 种工作模式定义
- **STORY_GRAMMAR.md** — 故事结构化语法,16 种 BeatType,10 种 ArcType
- **SHOT_GRAMMAR.md** — 镜头语言结构化语法,11 大类参数定义
- **README.md** — 项目总览
- **ROADMAP.md** — 6 阶段开发路线图
- **Directory Structure** — 完整目录骨架(docs/libraries/compilers/examples/projects)
- **libraries/** — 8 个知识库目录及规范说明
- **compilers/** — 4 个编译器目录及规范说明
- **examples/** — 4 个示例项目目录及模板
- **projects/template.md** — 项目模板
