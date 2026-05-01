# to-vibe 产品需求文档

> AI 代码生成后的项目工程化平台 — 把 vibe coding 产物转化为可维护工程资产
>
> 版本：v2.0
> 日期：2026-04-30

---

## 1. 概述

### 1.1 产品定位

to-vibe 是 **AI 代码生成后的项目工程化平台**，帮助开发者把 vibe coding 产物从"能跑的 demo"升级为"可维护的工程项目"。

**核心方程**：
```
Vibe = 快速生成整个系统
to-vibe = 把整个系统变得可靠
```

**典型 vibe coding 后的状态**：
```
能跑一点，但不敢动
报错很多，不知道先修哪个
代码很多，不知道哪个是真的有用
想上线，但不知道缺什么
想重构，但怕越改越坏
```

**to-vibe 核心能力**：
- **诊断**：通过 Evidence Ledger 建立项目事实账本，每个判断都有证据来源
- **优先级**：自动生成工程化优先级报告，不再无从下手
- **验证**：5 层基线验证，确保每次修复都可验证
- **进化**：从修复中学习，积累项目专属经验

### 1.2 目标用户

- 使用 Claude Code / Cursor 等 AI 编程工具的开发者
- 需要在 vibecoding 模式下保持高质量输出的团队
- 希望 AI 记忆项目上下文、积累经验的个人开发者

### 1.3 核心假设

- 用户已具备基本的 CLI 操作能力
- 用户使用 VS Code 作为主要编辑器
- 项目使用 Git 进行版本控制

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          to-vibe Post-Processing                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────┐     ┌──────────────┐     ┌─────────────────────────┐   │
│   │  Vibe   │────▶│   Evidence   │────▶│  Engineering Priority    │   │
│   │ (生成)   │     │   Ledger     │     │       Report             │   │
│   └─────────┘     │  (事实账本)   │     │    (优先级报告)          │   │
│                   └──────────────┘     └───────────┬─────────────┘   │
│                                                     │                  │
│                                                     ▼                  │
│                   ┌─────────────────────────────────────────────────┐ │
│                   │            Baseline Verify (5层验证)               │ │
│                   │  L1 环境识别 → L2 依赖检查 → L3 构建检查          │ │
│                   │  L4 启动检查 → L5 Smoke Test                     │ │
│                   └─────────────────────┬───────────────────────────┘ │
│                                         │                              │
│                                         ▼                              │
│                   ┌─────────────────────────────────────────────────┐ │
│                   │              Repair Loop (修复循环)                │ │
│                   │  选择问题 → 规划补丁 → 应用补丁 → 验证 → 记录     │ │
│                   │         Debug / Refactor / System / Simplify     │ │
│                   └─────────────────────┬───────────────────────────┘ │
│                                         │                              │
│                     ┌───────────────────┼───────────────────┐        │
│                     ▼                   ▼                   ▼        │
│               ┌──────────┐       ┌──────────┐       ┌──────────┐   │
│               │   Ship   │       │  Learn   │       │  Memory  │   │
│               │  (发布)   │       │  (学习)   │       │  (记忆)   │   │
│               └──────────┘       └──────────┘       └──────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.1.2 核心流程定义

**主流程**：
```
Vibe 生成整个系统
    │
    ▼
Evidence Ledger（建立项目事实账本）
    │
    ▼
Engineering Priority Report（生成可执行修复路线图）
    │
    ▼
Baseline Verify（5层验证）
    │
    ▼
Repair Loop（修复循环）
    │
    ├── Debug（调试）
    ├── Refactor（重构）
    ├── System（系统分析）
    └── Simplify（精简）
    │
    ▼
Ship（发布）
    │
    ▼
Learn（学习积累）
```

**Evidence Ledger 职责**：
- 扫描项目文件，建立事实账本
- 每个结论都有证据来源（文件路径 + 行号）
- 防止 AI 幻觉，锚定到文件系统现实

**Priority Report 职责**：
- 基于 Evidence 自动诊断
- 自动排序修复优先级
- 输出第一份可执行修复路线图

**Baseline Verify 5层**：
| 层级 | 验证内容 | 失败处理 |
|-----|---------|---------|
| L1 | 环境识别（Node/Python/包管理器） | 提示缺失依赖 |
| L2 | 依赖检查（package.json/pyproject.toml） | 提示版本冲突 |
| L3 | 构建检查（build/compile） | 阻断，优先修复 |
| L4 | 启动检查（服务能否启动） | 阻断，优先修复 |
| L5 | Smoke Test（核心功能） | 记录，不强制阻断 |

**Repair Loop 退出条件**：
- Stabilized（P0 修复完成）：可以开始开发
- Maintainable（中等问题修复）：默认目标
- Ship-ready（达到可发布状态）：最高目标

### 2.2 组件关系

```
用户输入
    │
    ▼
┌────────────────────────────────────────────────────────┐
│                    Skill 流程引擎                        │
│  ┌──────┐   ┌──────┐   ┌──────┐   ┌──────┐           │
│  │ 咨询  │──▶│上下文 │──▶│ 循环  │──▶│ 精简  │           │
│  └──────┘   └──────┘   └──┬───┘   └──────┘           │
│                           │                             │
│                    ┌──────┴──────┐                     │
│                    ▼             ▼                      │
│               ┌────────┐   ┌────────┐                  │
│               │ 系统   │   │ 调试   │   ...            │
│               └────────┘   └────────┘                  │
└────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────────────────────┐
│                     Memory 系统                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ L0: .abstract (~100 tokens)                    │   │
│  │ L1: .overview (~2k tokens)                     │   │
│  │ L2: docs/src (完整原始内容)                      │   │
│  └─────────────────────────────────────────────────┘   │
│                         │                               │
│                    ┌────┴────┐                          │
│                    ▼         ▼                          │
│              ┌─────────┐ ┌─────────┐                    │
│              │ Milvus  │ │ SQLite  │                    │
│              │ (向量)   │ │ (主存)  │                    │
│              └─────────┘ └─────────┘                    │
└────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────────────────────┐
│                   VS Code 插件                          │
│  - 记忆查看器                                            │
│  - 检索轨迹可视化                                        │
│  - 状态面板                                              │
└────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────────────────────┐
│                   FastAPI 服务                          │
│  - REST API (记忆读写)                                  │
│  - WebSocket (实时轨迹推送)                             │
└────────────────────────────────────────────────────────┘
```

### 2.3 Session 恢复架构

```
Skill 执行中断
    │
    ▼
┌────────────────────────────────────────────────────────┐
│                  崩溃检测机制                           │
│  - Heartbeat 超时 → 判断为 stale                       │
│  - Process exit → 文件锁自动释放                        │
└────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────────────────────┐
│               session-start.json                        │
│  - session_id / project_id / entry_task                │
│  - active_skill / skill_run_id                         │
│  - current_step_id / next_step_id                      │
│  - iteration / workflow_phases                         │
│  - context_refs (L0/L1/L2)                            │
│  - artifacts_paths / file_changes                      │
│  - verification_status / recovery_policy               │
│  - locks / errors                                     │
└────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────────────────────┐
│                    恢复决策规则                          │
│  - 当前步骤已完成且无上下文变化 → 下一步                 │
│  - 当前步骤无副作用但未完成 → 重跑当前步                 │
│  - 当前步骤有副作用且已写完 → 进入验证步                 │
│  - 当前步骤有副作用但中断 → 进入 reconcile_changes       │
│  - 上下文 hash 变化 → 回退到 fallback_resume_from     │
└────────────────────────────────────────────────────────┘
        │
        ▼
SkillEngine 从「下一安全步骤」继续执行
```

---

## 3. 核心流程规范

### 3.1 新流程 vs 旧 Skill 映射

**旧定位**：从零开发项目的 Skill 链
**新定位**：接管 AI 生成项目的维护链

| 新流程组件 | 旧 Skill 对应 | 职责变化 |
|-----------|-------------|---------|
| Evidence Ledger | 新增（Context 吸收） | 从"检索上下文" → "建立事实账本" |
| Priority Report | Simplify + System | 从"精简方案" → "自动生成优先级" |
| Baseline Verify | verification-before-completion | 扩展为 5 层验证体系 |
| Repair Loop | Loop + Debug + Refactor | 从"Plan→Execute→Reflect" → "Select→Plan→Apply→Verify→Record" |
| Ship | Ship | 保持不变 |
| Learn | Learn | 保持不变 |

### 3.2 流程定义

6 个核心能力模块，组成 vibe 后处理工作流：

| # | 能力 | 触发时机 | 核心职责 |
|---|-----|---------|---------|
| 1 | Evidence Ledger | 项目初始化 | 扫描文件，建立事实账本，每个结论有证据来源 |
| 2 | Priority Report | Ledger 后 | 自动诊断，排序优先级，输出可执行修复路线图 |
| 3 | Baseline Verify | Report 后 | 5 层验证（L1-L5），有限重试（1-3 次） |
| 4 | Repair Loop | 验证后 | 选择问题→规划补丁→应用→验证→记录证据 |
| 5 | Ship | Loop 退出后 | 聚焦 MVP，判断是否达到可发布状态 |
| 6 | Learn | 随时 | 从修复中提取经验，积累项目专属知识 |

### 3.2 执行顺序

```
Vibe 生成整个系统
    │
    ▼
┌──────────────────┐
│  Evidence Ledger  │ ◀── 扫描文件，建立事实账本
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Priority Report │ ◀── 自动诊断 + 排序优先级
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────┐
│         Baseline Verify (5层)          │
│  L1 环境识别 → L2 依赖 → L3 构建      │
│  → L4 启动 → L5 Smoke Test           │
└──────────────┬───────────────────────┘
               │
               │ 失败?
               ├─ 重试 1-3 次
               │ 仍失败 → 记录，跳过继续
               ▼
┌──────────────────────────────────────┐
│            Repair Loop                │
│                                      │
│  选择问题 → 规划补丁 → 应用补丁        │
│  → 验证 → 记录证据 → 下一问题         │
│                                      │
│  ┌────────┐ ┌────────┐ ┌────────┐   │
│  │ Debug  │ │Refact.│ │System  │   │
│  └────────┘ └────────┘ └────────┘   │
│  ┌────────┐                           │
│  │Simplify│                          │
│  └────────┘                          │
│                                      │
│  退出条件: Stabilized / Maintainable  │
│           / Ship-ready               │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────┐
│ Ship │ ◀── 判断是否达到可发布状态
└──┬───┘
   │
   ▼
┌──────┐
│ Learn │ ◀── 从修复中提取经验
└──┬───┘
   │
   ▼
  结束
```

### 3.3 能力详细规格

#### 能力 1: Evidence Ledger（事实账本）

**定位**：为 vibe 生成的项目建立事实账本，每个结论都有证据来源。

**核心原则**：
- 不相信猜测，只相信证据
- 每个判断都锚定到具体文件 + 行号
- 防止 AI 幻觉

**扫描范围**：
```
项目根目录/
├── 配置文件（package.json, pyproject.toml, Cargo.toml, etc.）
├── 源代码（src/, lib/, app/）
├── 文档（README.md, docs/）
├── 测试（tests/, __tests__/）
├── 构建配置（vite.config.ts, webpack.config.js, etc.）
└── 入口文件（index.js, main.ts, etc.）
```

**输出格式**：
```json
{
  "evidence_id": "uuid",
  "timestamp": "ISO8601",
  "project_type": "node | python | rust | ...",
  "facts": [
    {
      "fact_id": "uuid",
      "type": "package_manager | framework | entry_point | dependency | ...",
      "content": "具体事实描述",
      "evidence": {
        "file_path": "相对路径",
        "line_start": 10,
        "line_end": 15,
        "snippet": "关键代码片段"
      }
    }
  ],
  "confidence": 0.0-1.0
}
```

---

#### 能力 2: Engineering Priority Report（优先级报告）

**定位**：基于 Evidence Ledger 自动生成可执行修复路线图。

**生成时机**：
- Evidence Ledger 建立后自动触发
- 用户可通过 `to-vibe diagnose` 手动触发

**输出格式**：
```markdown
# 工程化优先级报告

## 1. 项目概况
- 项目类型：
- 入口文件：
- 包管理器：
- 框架：

## 2. 问题清单（按优先级排序）

### P0 - 阻断性问题（必须立即修复）
| # | 问题 | 证据 | 影响 | 建议修复 |
|---|-----|-----|-----|---------|

### P1 - 重要问题（影响开发效率）
| # | 问题 | 证据 | 影响 | 建议修复 |
|---|-----|-----|-----|---------|

### P2 - 优化建议（提升质量）
| # | 问题 | 证据 | 影响 | 建议修复 |
|---|-----|-----|-----|---------|

## 3. 第一步修复路线图
1. [P0] xxx → 预期收益：
2. [P0] xxx → 预期收益：
3. [P1] xxx → 预期收益：

## 4. 达到「可维护」状态所需的最小修复集
```

---

#### 能力 3: Baseline Verify（5层验证）

**定位**：系统化验证项目基础能力，识别阻断性问题。

**5层验证定义**：

| 层级 | 名称 | 验证内容 | 验证方式 |
|-----|-----|---------|---------|
| L1 | 环境识别 | Node/Python/包管理器是否存在 | `which node`, `node --version` |
| L2 | 依赖检查 | package.json/pyproject.toml 是否完整 | 文件解析 + 版本检测 |
| L3 | 构建检查 | `npm build` / `python setup.py` 是否成功 | 执行构建命令 |
| L4 | 启动检查 | 服务能否启动，端口是否监听 | 执行启动命令，检测端口 |
| L5 | Smoke Test | 核心功能是否正常 | 发送 HTTP 请求，验证响应 |

**失败处理策略**：
```
验证失败
  │
  ├── 重试 1-3 次（间隔 5s）
  │
  ├── 仍失败?
  │     ├── L1/L2/L3 失败 → 记录为 P0 阻断，停止验证
  │     ├── L4 失败 → 记录为 P0 阻断，停止验证
  │     └── L5 失败 → 记录为 P1，不强制阻断
  │
  └── 全部通过 → 进入 Repair Loop
```

---

#### 能力 4: Repair Loop（修复循环）

**定位**：按优先级逐个修复问题，每个修复都经过验证。

**循环结构**：
```
Select Issue → Plan Patch → Apply Patch → Verify → Record Evidence → Next Issue
```

**子能力**：

| 子能力 | 定位 | 触发场景 |
|-------|-----|---------|
| Debug | 修复 bug、报错、异常 | P0 问题为主 |
| Refactor | 清理代码结构 | P1 问题为主 |
| System | 分析组件依赖 | 大型重构前 |
| Simplify | 简化复杂代码 | P2 优化 |

**退出条件**：
- **Stabilized**：P0 全部修复完成，可以开始开发
- **Maintainable**：P0 + P1 全部修复，项目可维护（默认目标）
- **Ship-ready**：达到可发布状态

**循环限制**：
- 每个问题最多 3 次修复尝试
- 3 次仍失败 → 记录为「已知问题」，跳到下一个
- 总循环次数限制：50 次（防止无限循环）

**输出格式**：
```markdown
# Repair Loop 报告

## 当前状态
- 循环次数：N
- 已修复问题：X/Y
- 当前问题：xxx

## 修复历史
| 时间 | 问题 | 修复方案 | 结果 |
|-----|-----|---------|-----|

## 退出状态
- 退出级别：Stabilized / Maintainable / Ship-ready
- 已修复：
- 未修复（跳过）：
```

---

#### 能力 5: Ship（发布）

**定位**：判断项目是否达到可发布状态。

**发布标准检查**：

| 标准 | 要求 | 验证方式 |
|-----|-----|---------|
| 核心路径 | 主流程能跑通 | Smoke Test 通过 |
| 数据闭环 | 增删改查基本完整 | API 测试 |
| 异常处理 | 未处理异常已记录 | 日志检查 |
| 部署能力 | 能构建产物体 | 构建验证 |
| 基本体验 | 无明显体验问题 | 人工确认 |

**输出格式**：
```markdown
# Ship 报告

## 1. 发布版本
## 2. 发布标准检查
| 标准 | 状态 | 备注 |
|-----|-----|-----|
| 核心路径 | ✅/❌ | |
| 数据闭环 | ✅/❌ | |
| ... | ... | |

## 3. 已知问题
## 4. 不包含内容
## 5. 回滚方案
## 6. 结论
```

---

#### 能力 6: Learn（学习）

**定位**：从修复过程中提取经验，积累项目专属知识。

**算法**：
```
Observe（观察） → Extract（提取） → Generalize（泛化） → Validate（验证） → Store（存储）
```

**学习内容**：
- 项目结构特征
- 常见问题模式
- 有效修复方案
- 用户偏好

**写入位置**：
- Evidence Ledger（项目事实）
- Cross-project Memory（跨项目经验，仅供参考，不覆盖当前项目证据）

**Memory 层级映射**：
| Memory 层 | 来源 | 内容 |
|----------|-----|------|
| L0 | 从 Ledger 派生 | 一句话项目概括 |
| L1 | Priority Report | 工程化优先级报告 |
| L2 | Evidence Ledger | 原始事实账本 |

**输出格式**：
```markdown
# 学习报告

## 1. 本次修复提取
- 问题类型：
- 有效方案：
- 失败尝试：

## 2. 项目知识更新
- 新增事实：
- 更新事实：

## 3. 跨项目经验
- 可借鉴模式：
- 避免踩坑：
```

---

### 3.4 Skill 输出暂存机制

**暂存位置**：Redis（临时缓存）

**写入时机**：Skill 执行完成后暂存 Redis，流程结束后批量写入 L2

**L2 写入位置**：`docs/{skill-type}/` 目录下按时间存储

**L2 格式**：
```json
{
  "skill": "string",
  "timestamp": "ISO8601",
  "outcome": "success | failure | partial",
  "keywords": ["string"],
  "description": "string (L2 详细内容)",
  "lesson": "string (可选，学习用)",
  "verification": {
    "status": "passed | failed",
    "violations": ["string"]
  }
}
```

**一致性保证**：
- 写入 L2 成功 → 清空 Redis 暂存
- 写入 L2 失败 → 保留 Redis 暂存，保留 session-start.json
- 崩溃 Hook 保底：Skill 崩溃时写入 skill 日志，尝试回滚

---

## 4. Memory 系统

### 4.1 层级映射（Phase 2 重排）

| 层级 | 来源 | 内容 | 用途 |
|-----|-----|------|-----|
| L0 | 从 Ledger 派生 | 一句话项目概括 | 快速判断是否相关 |
| L1 | Priority Report | 工程化优先级报告 | 当前修复路线图 |
| L2 | Evidence Ledger | 原始事实账本 | 完整证据追溯 |

**核心变化**：
- 旧 L0 = LLM summarization → 新 L0 = 从 Evidence Ledger 派生的单句概括
- 旧 L1 = LLM summarization → 新 L1 = Engineering Priority Report
- 旧 L2 = 原始文件 → 新 L2 = Evidence Ledger 事实账本

### 4.2 分层存储架构

```
/project/
├── .to-vibe/                    # to-vibe 主目录
│   ├── evidence_ledger/         # L2: 事实账本（权威）
│   │   └── {timestamp}/         #   按时间组织
│   │       └── ledger.json
│   ├── priority_report/          # L1: 优先级报告
│   │   └── {timestamp}/         #   按时间组织
│   │       └── report.md
│   ├── .abstract/               # L0: 项目概括
│   │   └── project_summary.md
│   ├── rules.d/                 # 规则目录
│   │   ├── built-in/           # 内置规则
│   │   ├── user-confirmed/     # 用户确认规则
│   │   └── generated/          # 候选规则
│   └── repair_history/          # 修复历史
│       └── {timestamp}.md
├── .claude/                     # 系统目录
│   └── memory_index.sqlite      # SQLite 主索引
└── 原始项目文件/                 # L2 原文（由 Evidence Ledger 索引）
```

### 4.3 各层规格

| 层级 | 文件名 | 大小 | 用途 | 格式 |
|-----|-------|-----|------|-----|
| L0 | `project_summary.md` | ~100 tokens | 快速相关性判断 | Markdown |
| L1 | `report.md` | 无限制 | 当前修复路线图 | Markdown |
| L2 | `ledger.json` | 无限制 | 完整证据追溯 | JSON |

### 4.3 Evidence Ledger 生成机制

**核心原则**：每个结论都有证据来源，不相信猜测。

**生成方式**：
- L0：从 Ledger 派生，失败时基于文件类型推断
- L1：基于 Ledger + Priority Report 生成
- L2：原文完整保存 + metadata

**触发时机**：
- `to-vibe init` 时自动生成
- `to-vibe diagnose` 手动触发
- 项目文件变更时增量更新

### 4.4 两阶段索引初始化

#### 阶段一：默认快速初始化

```bash
to-vibe init
```

行为：
- 扫描项目文件
- 计算 content_hash
- 规则提取 L0/L1（不调用 LLM）
- 截断 fallback
- 写入 SQLite
- 可选生成 embedding

特点：**快、便宜、不调用 LLM，适合首次体验**

#### 阶段二：深度初始化（可选）

```bash
to-vibe init --deep
to-vibe init --deep --budget-tokens 500000 --max-files 300
```

行为：
- 高价值文件 LLM summarization
- 优先级：README > Controller > Service > API > Tests > ...
- 在预算内处理最重要的文件

#### 中断恢复

```bash
to-vibe init --resume  # 继续上次未完成任务
to-vibe init --repair  # 检查并修复索引
```

### 4.5 存储架构

| 存储位置 | 职责 | 是否权威 |
|---------|------|---------|
| SQLite | 文件索引、content_hash、L0/L1、生成状态、版本信息 | 是 |
| Milvus | 向量、检索字段、metadata、召回 | 否（副本） |
| 文件系统 (.abstract/) | 可读缓存、调试、备份、人工查看 | 否（可选） |
| 原始项目文件 | L2 原文 | 是 |

### 4.6 经验置信度机制

```
新经验 → 置信度 0.5
  │
  ├── 验证成功 1 次 → +0.1，最高 0.9
  │
  └── 验证失败 1 次 → -0.3，低于 0.3 标记为「已失效」
```

**经验冲突处理**：
- 新的 L2 vs 旧的 L1 → 共存两条矛盾记录，置信度决定优先级

### 4.7 遗忘机制

**触发条件**（满足任一）：
- L2 记录超过 1000 条
- 记录超过 180 天未访问
- 置信度低于 0.2

**归档策略**：
- 优先归档低频、低置信度记录
- 核心经验保留在 L1，删除具体案例细节
- 归档到 `.archive/` 目录
- 可通过动态检索恢复

---

## 5. 学习与进化（Learn）

### 5.1 学习触发时机

- **主动触发**：「学习」Skill 执行时
- **被动触发**：Skill 执行失败/遇到障碍时，优先查 Memory 而非直接报错

### 5.2 动态规则扩展 UX

当 LLM 观察到用户重复纠正同类问题（如命名规范），系统提示用户是否要将该规则加入 Verification。

**UX 流程**：
```
用户纠正：函数命名应该用 camelCase
    ↓
Agent 记录 correction_signal
    ↓
归类为 rule_candidate
    ↓
累计次数 / 影响范围 / 置信度
    ↓
达到阈值(默认N=3)?
  ├─ 否：继续静默记录
  └─ 是：加入 pending_rule_suggestions
    ↓
学习 Skill / 任务结束阶段统一展示
    ↓
用户选择：接受 / 忽略 / 修改范围 / 设为 warning
    ↓
写入 rules.d/user-confirmed/
    ↓
下一次 Verification 自动生效
```

### 5.3 规则存储格式

**未确认候选规则**：
```
.to-vibe/rules.d/generated/pending-suggestions.yaml
```

**确认后规则**：
```
.to-vibe/rules.d/user-confirmed/{rule_id}.yaml
```

**规则加载优先级**（高→低）：
1. 当前用户显式指令
2. 当前任务 override
3. 项目强制规则
4. 用户确认动态规则
5. 团队默认规则
6. 内置默认规则
7. 未确认候选规则

---

## 6. 验证机制（Baseline Verify）

### 6.1 5层验证体系

见 §3.2 Baseline Verify 定义。

### 6.2 验证失败处理

**流程**：
```
验证失败
  │
  ├── 重试 1-3 次（间隔 5s）
  │
  ├── 仍失败?
  │     ├── L1/L2/L3/L4 失败 → 记录为 P0 阻断
  │     └── L5 失败 → 记录为 P1，不强制阻断
  │
  └── 通过 → 进入 Repair Loop
```

### 6.3 LLM 自评 vs Verification

**Verification（必须拦）**：
- 硬编码的 API key / password / token
- 明显的 SQL injection / XSS 漏洞
- 未处理的 Promise rejection / async 异常

**LLM 自评（放行）**：
- 函数超过 50 行（可重构但不阻断）
- 命名不符合规范（可优化但不阻断）
- 缺少 try-catch（可补充但不阻断）

---

## 7. 决策机制

### 7.1 Priority Report 生成决策

**输入**：Evidence Ledger 事实账本

**输出**：优先级报告 + 可执行修复路线图

**决策逻辑**：
- 按 P0/P1/P2 排序
- P0 阻断性优先
- 最小修复集优先

### 7.2 Repair Loop 退出决策

**输入**：当前修复状态 + Baseline Verify 结果

**输出**：退出级别

**决策选项**：
- **Stabilized**：P0 全部修复完成
- **Maintainable**：P0 + P1 全部修复（默认）
- **Ship-ready**：达到发布标准

### 7.3 Cross-project Experience

**定位**：跨项目经验，仅供参考，不覆盖当前项目证据。

**使用原则**：
- 建议性引用
- 当前项目 Evidence Ledger 优先级最高
- 跨项目经验用于启发思路

---

## 8. 技术规范

### 8.1 技术栈

| 组件 | 技术选型 |
|-----|---------|
| 语言 | Python 3.11+ |
| 向量数据库 | Milvus 2.4+ (upsert) |
| 主存储 | SQLite |
| 临时缓存 | Redis |
| Embedding | sentence-transformers (all-MiniLM-L6-v2) |
| LLM 意图分析 | MiniMax API |
| CLI | Python + Click |
| API | FastAPI (REST + WebSocket) |
| 文件监控 | watchdog |
| VS Code 插件 | TypeScript |

### 8.2 项目结构

```
to-vibe/
├── src/
│   ├── __init__.py
│   ├── cli.py              # CLI 入口
│   ├── skill/              # Skill 流程引擎
│   │   ├── __init__.py
│   │   ├── engine.py       # 流程编排
│   │   ├── ask.py          # 咨询
│   │   ├── context.py      # 上下文
│   │   ├── loop.py         # 循环
│   │   ├── debug.py        # 调试
│   │   ├── refactor.py     # 重构
│   │   ├── system.py       # 系统
│   │   ├── learn.py        # 学习
│   │   ├── simplify.py     # 精简
│   │   └── ship.py         # 发布
│   ├── memory/             # Memory 系统
│   │   ├── __init__.py
│   │   ├── storage.py      # 文件系统操作
│   │   ├── sqlite.py       # SQLite 主存
│   │   ├── vector.py       # Milvus 接口
│   │   ├── retrieval.py    # 检索逻辑
│   │   ├── abstractor.py   # L0/L1 生成
│   │   └── conflict.py     # 冲突检测
│   ├── verification/       # 验证模块
│   │   ├── __init__.py
│   │   ├── rules.py        # 验证规则
│   │   └── dynamic.py      # 动态规则扩展
│   ├── arbitration/        # 仲裁 Agent
│   │   ├── __init__.py
│   │   └── agent.py        # 跳转决策
│   ├── hooks/              # Hook 系统
│   │   ├── __init__.py
│   │   ├── trigger.py      # 触发器
│   │   └── recovery.py    # 崩溃恢复
│   ├── api/                # FastAPI 服务
│   │   ├── __init__.py
│   │   ├── routes.py       # REST API
│   │   └── websocket.py    # WebSocket
│   └── utils/
│       └── __init__.py
├── vscode-extension/       # VS Code 插件
│   ├── src/
│   │   └── extension.ts
│   └── package.json
├── tests/
├── pyproject.toml
└── README.md
```

### 8.3 锁机制

| 锁类型 | 粒度 | 持有时间 | 实现 |
|-------|------|---------|------|
| session lock | session-start.json | 会话期间 | flock |
| skill_run lock | 当前 Skill 实例 | Skill 生命周期 | flock |
| file lock | 具体被修改文件 | 修改期间 | flock |
| project write lock | 高风险批量操作 | 操作期间 | flock |
| global lock | 默认不用 | - | - |

**Stale 检测**：heartbeat + ttl_seconds，进程退出自动释放。

### 8.4 配置文件

`to-vibe.yaml`（项目根目录）：

```yaml
version: "1.1"

memory:
  layers:
    L0: .abstract
    L1: .overview
    L2: docs, src

  vector:
    enabled: true
    db_path: .claude/milvus.db

  retention:
    max_records: 1000
    max_age_days: 180
    min_confidence: 0.2

  indexing:
    cheap_first: true
    deep_on_demand: true
    hash_based_skip: true

verification:
  mode: strict  # strict | lenient
  rules:
    - style
    - security
    - testing
  dynamic:
    enabled: true
    threshold: 3
    rules_dir: .to-vibe/rules.d

skills:
  loop:
    max_iterations: 10
    timeout_minutes: 60
  arbitration:
    max_context_tokens: 200000
    fallback_on_overflow: true

session:
  heartbeat_interval_seconds: 30
  ttl_seconds: 300
  recovery_policy: auto
```

---

## 9. 用户流程

### 9.1 新项目初始化

```bash
# 1. 安装
pip install to-vibe

# 2. 快速初始化（不调用 LLM）
to-vibe init

# 3. 深度初始化（可选，需要 LLM）
to-vibe init --deep

# 4. 带预算控制
to-vibe init --deep --budget-tokens 500000 --max-files 300

# 5. 查看状态
to-vibe status

# 6. 恢复中断的初始化
to-vibe init --resume
```

### 9.2 日常使用

```bash
# 开始新任务
to-vibe start "实现用户认证功能"

# 查看状态
to-vibe status

# 查询记忆
to-vibe query "上次如何实现 JWT"

# 强制跳过验证（紧急通道）
to-vibe publish --force

# 修复索引
to-vibe init --repair
```

### 9.3 VS Code 插件使用

1. 打开命令面板（Cmd+Shift+P）
2. 输入 `to-vibe: View Memory`
3. 选择查看 L0 / L1 / L2
4. 浏览或搜索记忆内容

---

## 10. 验收标准

### 10.1 功能验收

- [ ] 9 个 Skill 流程正确执行
- [ ] L0/L1 基于 content_hash 增量生成
- [ ] 两阶段 init 支持 cheap/deep 分离
- [ ] Session 断点恢复正常工作
- [ ] 动态规则扩展 UX 完整
- [ ] 仲裁 Agent 跳转决策正确
- [ ] LLM 自评优先 + Verification 安全网
- [ ] 四级锁机制正常工作
- [ ] VS Code 插件显示记忆内容

### 10.2 性能验收

- [ ] L0/L1 生成 < 1s/文件（hash 未变时跳过）
- [ ] 向量检索 < 500ms
- [ ] 记忆查询 < 200ms（L0/L1）
- [ ] CLI 响应 < 100ms
- [ ] 快速 init < 5 分钟（1000 文件）

### 10.3 质量验收

- [ ] 单元测试覆盖率 >= 80%
- [ ] 无硬编码 secrets
- [ ] 代码通过 pylint / black
- [ ] 文档完整

---

## 附录 A：代码质量规则（默认配置）

### A.1 Style References

- Java: Google Java Style Guide
- JavaScript: Airbnb JavaScript Style Guide
- TypeScript: Google TypeScript Style Guide
- REST API: Microsoft REST API Guidelines
- Security: OWASP Secure Coding Practices
- E2E Testing: Playwright Best Practices
- Commit Messages: Conventional Commits

### A.2 General Rules

- Prefer simple, readable, maintainable code
- Keep functions small and focused (< 50 lines)
- Use meaningful names reflecting business intent
- Avoid duplication and hidden side effects
- Separate concerns clearly
- Do not mix UI, business logic, persistence, infrastructure
- Validate all external input
- Handle errors explicitly
- Do not expose stack traces or sensitive info
- Add/update tests for critical logic
- Explain validation method after each change

### A.3 Backend Rules

- Follow Controller / Service / Repository / Entity / DTO separation
- Controllers: request mapping, parameter parsing, response wrapping only
- Services: business logic only
- Repositories: data access only
- Use unified API response format
- Use proper HTTP status codes
- Validate request parameters
- Avoid returning DB entities directly when DTOs more appropriate

### A.4 Frontend Rules

- Keep components focused and reusable
- Avoid overly large components (> 200 lines)
- Extract repeated logic into hooks/composables/utils
- Keep state management predictable
- Handle loading, empty, error, success states
- Avoid fragile DOM assumptions
- Use stable selectors for tests

### A.5 Testing Rules

- Cover core business paths
- Keep tests independent
- Avoid fixed waits in E2E tests
- Prefer user-visible behavior assertions
- Do not chase coverage numbers blindly

### A.6 Security Rules

- Validate and sanitize input
- Enforce authentication and authorization
- Prevent SQL injection, XSS, CSRF, path traversal
- Do not hardcode secrets
- Do not log sensitive information

---

## 附录 B：术语表

| 术语 | 定义 |
|-----|------|
| vibecoding | 依赖 AI 辅助的编程模式 |
| Skill | 独立的工作流模块 |
| L0/L1/L2 | 分层记忆的三级结构 |
| Hook | 事件触发机制 |
| content_hash | SHA-256 文件内容哈希 |
| session-start.json | Session 断点恢复状态文件 |
| 仲裁 Agent | 负责 Skill 跳转决策的模块 |
| to-vibe | 本系统名称 |

---

## 附录 C：Open Questions 状态（Phase 2）

| # | 问题 | 状态 | 结论 |
|---|-----|------|------|
| 1 | Evidence Ledger 如何防止 AI 幻觉 | ✅ 已解决 | 每个结论绑定文件路径+行号作为证据 |
| 2 | Priority Report 如何自动排序 | ✅ 已解决 | P0 阻断 > P1 重要 > P2 优化 |
| 3 | Baseline Verify 5层具体实现 | ✅ 已解决 | L1-L5 每层有明确验证方式和失败策略 |
| 4 | Repair Loop 退出条件 | ✅ 已解决 | Stabilized / Maintainable / Ship-ready |
| 5 | Memory 新层级映射 | ✅ 已解决 | L0=派生概括, L1=Priority Report, L2=Ledger |
| 6 | 旧 Skill 到新能力映射 | ✅ 已解决 | Loop→Repair Loop, Simplify→Priority Report |
| 7 | Cross-project Experience 处理 | ✅ 已解决 | 仅供参考，不覆盖当前项目证据 |
