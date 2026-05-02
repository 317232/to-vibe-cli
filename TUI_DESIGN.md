# to-vibe TUI 设计文档

> 参考图片基准：`image1.1.png` → `image2.1.png` → `image3.1.png` → `image.png`

---

## 一、整体布局

### 全局结构（`image.png`）

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│  ◇ to-vibe + Claude Code Workspace        [1: claude] [2: to-vibe] [3: logs]      │ CPU 24% RAM 5.9G │ 00:25 │
├──────────────────────────────────────────┬───────────────────────────────────────────────────────────────────┤
│                                          │                                                                   │
│  Claude Code Chat                        │  to-vibe Panel                                                     │
│  左侧 40%                                 │  右侧 60%                                                           │
│                                          │                                                                   │
│  ┌─ Conversation ─────────────────────┐  │  ┌─ Session Header ─────────────────────────────────────────────┐  │
│  │ User / Claude messages             │  │  │ ◇ to-vibe | ~/dev/library_system         main  🕒 00:25:32 │  │
│  │ Streaming response                 │  │  │ $ to-vibe run ./project                                      │  │
│  │ File operation hints               │  │  │ Project : ./library_system   Mode : dry-run                  │  │
│  │                                    │  │  │ Executor: local / claude-code                                 │  │
│  └────────────────────────────────────┘  │  │ Pipeline: Evidence → Priority → Verify → Repair → Learn        │  │
│                                          │  │ Note: Learn runs on complete / manual; Ship is out of scope    │  │
│  ┌─ Input ────────────────────────────┐  │  └──────────────────────────────────────────────────────────────┘  │
│  │ > ask Claude about current issue   │  │                                                                   │
│  └────────────────────────────────────┘  │  ┌─ StageBar ───────────────────────────────────────────────────┐  │
│                                          │  │ [✔ Evidence] → [✔ Priority] → [❌ Verify] → [▶ Repair] → [◌ Learn] │
│                                          │  └──────────────────────────────────────────────────────────────┘  │
│                                          │                                                                   │
│                                          │  ┌───────────────────────┬───────────────────────────────────────┐ │
│                                          │  │ Evidence Ledger       │ Baseline Verify                       │ │
│                                          │  │ Priority Report       │ Learn Summary                         │ │
│                                          │  └───────────────────────┴───────────────────────────────────────┘ │
│                                          │                                                                   │
├──────────────────────────────────────────┴───────────────────────────────────────────────────────────────────┤
│ ./library_system | default | dry-run │ Executor: local / claude-code ⟳ │ [Space] 暂停 │ [R] 重试 │ [S] 跳过 │ [↑↓] 滚动 │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

**关键比例：**

- 左右分栏：**4:6**（左侧 Chat 40%，右侧 to-vibe 60%）
- 垂直分隔线：一条细实线贯穿 Header 和 Footer 之间
- Tab 切换：位于右侧区域 Header 位置，3 个预设 Tab + 1 个按钮
- 当前激活 Tab：`1: claude`（橙色高亮边框 + 文字）

---

## 二、组件详细规格

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ ◇ to-vibe | ~/dev/library_system                                       main  🕒 00:25:32 │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ $ to-vibe run ./project                                                                       │
│ Project     : ./library_system                                                                │
│ Mode        : dry-run                                                                         │
│ Executor    : local / claude-code                                                             │
│ Pipeline    : Evidence → Priority → Verify → Repair → Learn                                   │
│ Note        : Learn runs after pipeline completion; Ship is out of current scope               │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ [✔ Evidence] → [✔ Priority] → [❌ Verify] → [▶ Repair] → [◌ Learn]                             │
├───────────────────────────────┬──────────────────────────────────────────────────────────────┤
│ ◆ Evidence Ledger             │ 💢 Baseline Verify                                           │
│                               │                                                              │
│ Tech stack      : Spring Boot │ #  Check           Status       Details / Command            │
│                 : Thymeleaf   │ ──────────────────────────────────────────────────────────── │
│                 : MySQL       │ 1  Environment     ✅ pass      java -version                 │
│ Files scanned   : 128         │ 2  Dependencies    ✅ pass      mvn dependency:resolve        │
│ Ignored         : node_modules│ 3  Build           ❌ fail      mvn package                   │
│                 : dist,target │ 4  Start           ➡ skipped   java -jar target/app.jar       │
│ Output          : .to-vibe/   │ 5  Smoke Test      ➡ skipped   curl -f /health                │
│                 evidence.json │                                                              │
├───────────────────────────────┤                                                              │
│ ◆ Priority Report             │ ◆ Learn Summary                                               │
│                               │                                                              │
│ Blockers        : 2           │ Status          : pending                                     │
│ High            : 3           │ Records         : 0                                           │
│ Medium          : 5           │ Focus           : Patterns & fixes                            │
│ Top issue       : P1 startup  │ Source          : Verified issues                             │
│ Suggested       : Debug       │ Detail          : [详情]                                      │
└───────────────────────────────┴──────────────────────────────────────────────────────────────┘
│ ./library_system | default | dry-run │ Executor: local / claude-code ⟳ │ [Space]暂停 [R]重试 [S]跳过 │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ ◆ Learn Detail View                                                        [Esc] 返回        │
├──────────────────────────────────────────────┬───────────────────────────────────────────────┤
│ Verified Fixes                               │ Issue Patterns                                │
│ 已验证修复经验                                │ 问题模式 → 推荐动作                            │
│                                              │                                               │
│ ✅ Fix #1                                     │ • Pattern #1                                   │
│ Title       : Maven build failure             │ Signal      : mvn package exit code 1          │
│ Root cause  : missing dependency version       │ Cause       : dependency conflict              │
│ Capability  : Debug                           │ Recommend   : run dependency tree first        │
│ Verified by : L3 Build passed                 │ Confidence  : 0.82                             │
│ Source      : repair-loop.json                │ Source      : priority-report.md               │
│                                              │                                               │
│ ✅ Fix #2                                     │ • Pattern #2                                   │
│ Title       : Health endpoint missing          │ Signal      : Smoke Test skipped / failed      │
│ Verified by : L5 Smoke Test passed            │ Recommend   : check controller mapping         │
├──────────────────────────────────────────────┼───────────────────────────────────────────────┤
│ Project Facts                                │ User Rules                                    │
│ 项目事实                                      │ 用户确认规则，最高优先级                         │
│                                              │                                               │
│ ▸ Fact #1                                     │ ★ Rule #1                                      │
│ Type        : framework                       │ Rule        : dry-run before live repair       │
│ Value       : Spring Boot + Thymeleaf         │ Status      : accepted                         │
│ Evidence    : pom.xml:12, templates/*.html    │ Priority    : highest                          │
│                                              │                                               │
│ ▸ Fact #2                                     │ ★ Rule #2                                      │
│ Type        : database                        │ Rule        : never store cross-project memory │
│ Value       : MySQL                           │ Status      : pinned 📌                        │
│ Evidence    : application.yml:8               │                                               │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ Actions: [A]接受  [E]编辑  [R]拒绝  [P]固定  [D]删除  [Esc]返回                              │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

### to-vibe TUI 的目标界面结构、组件职责、数据来源和交互约束。

当前 UI 原型图主要用于确定视觉布局和信息层级；实际实现必须以 `TUIStateStore` 为唯一状态来源。所有组件只负责渲染状态快照，不允许各自维护独立业务状态，也不允许重复定义与 Store 不一致的数据结构。

整体界面采用 3 Tab Bento Grid：

- `1: claude`：左侧 Claude Code Chat，用于与 LLM 交互、查看对话历史和辅助分析。
- `2: to-vibe`：主 Pipeline 面板，用于展示 Evidence、Priority、Verify、Learn 的阶段结果。
- `3: logs`：运行日志面板，用于展示 Repair Loop、LogStream、Learn、Artifacts。

核心流程固定为：

Evidence Ledger → Priority Report → Baseline Verify → Repair Loop → Learn 其中:

- Evidence 负责事实锚定。
- Priority 负责问题排序。
- Verify 负责 5 层验证闭环。
- Repair 负责按优先级执行 Select → Plan → Apply → Verify → Record。
- Learn 负责在流程结束后沉淀已验证经验，避免跨项目污染。

### To-vibe 主面板

to-vibe 是主执行视图，用于展示当前项目工程化流程的核心状态。

该视图由四部分组成：

1. **Session Header**

   - 显示当前项目路径、Git 分支、运行时长、执行命令、模式和 Executor。
   - Header 不应硬编码 `$ to-vibe run ./project`，必须从 SessionData 或运行参数中读取真实命令。
   - `Ship` 不再作为当前阶段展示，当前版本只保留 Evidence / Priority / Verify / Repair / Learn。

2. **StageBar**

   - 展示五阶段 pipeline 状态。
   - 阶段顺序固定为：Evidence → Priority → Verify → Repair → Learn。
   - 状态包括：pending、active、completed、failed、skipped。
   - StageBar 必须订阅 `TUIStateStore.stages`，不能只在组件内部维护状态。

3. **Bento Grid**

   - 左侧 40%：EvidenceCard + PriorityCard，上下堆叠。
   - 右侧 60%：VerifyTable + Learn Summary。
   - Evidence / Priority / Verify / Learn 必须分别订阅 Store 对应 key：

     - `evidence`

     - `priority`

     - `verify`

     - `learn`

4. **Footer**
   - 显示当前 workspace、profile、mode、executor 和快捷键。
   - Footer 中的快捷键不是装饰，必须对应真实 pipeline 操作：
     - `[Space]` 调用 pause
     - `[R]` 调用 retry
     - `[S]` 调用 skip
     - `[↑↓]` 控制日志滚动

### 1. EvidenceCard（`image2.1.png` 左上）

EvidenceCard 用于展示 Evidence Ledger 的扫描结果，是整个 pipeline 的事实锚点。

**视觉样式：**

\- 标题：`◆ Evidence Ledger`
\- 主色：绿色 `#238636`
\- 边框：绿色 1px 圆角
\- 内容格式：Key-Value，冒号垂直对齐

**示例 Key-Value 格式（冒号垂直对齐，正常按实际项目为准）：**

```
Tech stack      : Spring Boot, Thymeleaf, MySQL
Files scanned   : 128
Ignored         : node_modules, dist, target, .git
Output          : .to-vibe/evidence-ledger.json
```

### 2. PriorityCard（`image2.1.png` 左下）

PriorityCard 用于展示 Priority Report 的问题统计和当前最高优先级问题。

**视觉样式：**

\- 标题：`◆ Priority Report`
\- 主色：橙黄色 `#d29922`
\- 边框：橙黄色 1px 圆角
\- 内容格式：Key-Value

**示例 Key-Value 格式（按实际项目为准）：**

```
Blockers        : 2
High            : 3
Medium          : 5
Top issue       : P1 backend fails to start
Suggested       : Debug
```

### 3. VerifyTable（`image2.1.png` 右侧）

**标题：** `💢 Baseline Verify`（红色准星/四角图标前缀）

**边框：** 红色，1px 圆角

**表格列：** `#` | `Check` | `Status` | `Details / Command`

**表格内容（按实际流程为准）：**

```
#  Check         Status       Details / Command
──────────────────────────────────────────────────
1  Environment   ✅ pass      java -version
2  Dependencies  ✅ pass      mvn dependency:resolve
3  Build         ❌ fail      mvn package
4  Start         ➡ skipped   java -jar target/app.jar
5  Smoke Test    ➡ skipped   curl -f http://localhost:8080/health
```

**Status 图标规则：**

- `✅ pass` — 绿色，环境/依赖检查通过
- `❌ fail` — 红色，Build 失败会阻塞后续 L4/L5
- `➡ skipped` — 橙色/黄色，因前置失败被跳过

### 4. Repair Loop（`image3.1.png` 上方区块）

**标题：** `◆ Repair Loop (dry-run)`（蓝色菱形图标前缀）

**边框：** 蓝色，1px 圆角

**示例 Key-Value 格式（按实际项目为准）：**

```
Selected issue  : P1 startup failure         Apply      : skipped
Capability      : Debug                      Record     : .to-vibe/repair-loop.json
Mode            : dry-run                    Next       : export Claude tasks or run verify again
```

**Latest Event 行：**

```
▷ Latest event: Baseline verification completed with failures (Build)
                                                           00:25:20
```

**过滤按钮：** `info`(蓝) `error`(红) `warning`(橙) `Clear`(灰+垃圾桶图标)

---

## 三、Logs Panel（`image3.1.png`）

### 整体布局

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ to-vibe logs  ~/dev/library_system/.to-vibe                             main  🕒 00:25:32 │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ ◆ Repair Loop (dry-run)                                                                      │
│                                                                                              │
│ Selected issue : P1 startup failure                  Apply  : skipped                        │
│ Capability     : Debug                               Record : .to-vibe/repair-loop.json      │
│ Mode           : dry-run                             Round  : 1 / 50                          │
│ Next           : export Claude tasks or retry Verify                                          │
│                                                                                              │
│ ▷ Latest event : Baseline verification completed with failures: Build              00:25:20  │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│ [info]  [error]  [warning]                                                   [Clear]         │
├──────────────────────────────────────────────┬──────────────────────┬────────────────────────┤
│ LogStream                                    │ Learn                 │ Artifacts              │
│ 宽度 60%                                      │ 宽度 20%               │ 宽度 20%                │
│                                              │                      │                        │
│ 00:25:10 [INFO]  Evidence scanned 128 files  │ Status  : pending    │ · evidence-ledger.json  │
│ 00:25:12 [INFO]  Priority generated          │ Records : 0          │ · priority-report.md    │
│ 00:25:15 [ERROR] Build failed: mvn package   │ Focus   : Patterns   │ · baseline-verify.json  │
│ 00:25:16 [WARN]  Start skipped by L3 fail    │ Source  : Verified   │ · repair-plan.md        │
│ 00:25:17 [INFO]  Repair loop entered         │          issues      │ 📁 claude-tasks/        │
│ 00:25:20 [INFO]  Next: export Claude tasks   │                      │ 📁 learn/               │
│                                              │ [详情]               │                        │
├──────────────────────────────────────────────┴──────────────────────┴────────────────────────┤
│ ./library_system | default | dry-run │ Executor: local / claude-code ⟳ │ [Space]暂停 [R]重试 [S]跳过 │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

logs 是运行过程审计视图，负责展示 Repair Loop 摘要、实时日志、Learn 状态和产物文件。

整体布局：

```
RepairPanel
LogStream | LearnPanel | Artifacts
Footer
```

### RepairPanel

RepairPanel 用于展示当前 Repair Loop 的修复状态。它不是普通日志，而是 Repair 阶段的结构化摘要。

RepairPanel 应位于 `3: logs` Tab 顶部。

**视觉样式：**

- 标题：`◆ Repair Loop (dry-run)`
- 主色：蓝色 `#1f6feb`
- 边框：蓝色 1px 圆角
- 内容格式：左右 Key-Value 网格

**展示字段（按实际项目为准）：**

```
Selected issue : P1 startup failure                  Apply  : skipped
Capability     : Debug                               Record : .to-vibe/repair-loop.json
Mode           : dry-run                             Round  : 1 / 50
Next           : export Claude tasks or retry Verify

▷ Latest event : Baseline verification completed with failures: Build    00:25:20
```

**数据来源：**

RepairPanel 必须订阅：

```
TUIStateStore.subscribe("repair", callback)
```

PipelineIntegration 在以下时机必须更新 repair state：

- 进入 Repair Loop
- 选择 issue
- 生成 repair plan
- apply 被跳过或执行
- verify 重新运行
- record 写入 repair-loop.json
- next action 发生变化

如果没有 RepairPanel，Logs Tab 将无法表达 Repair Loop 当前状态。

### LogStream 格式

**格式：** `HH:MM:SS [LEVEL] Message`

**颜色规则：**

- `[INFO]` — 绿色
- `[ERROR]` — 红色
- `[WARN]` — 橙色/黄色

```
HH:MM:SS [LEVEL] Message
```

示例：

```
00:25:10 [INFO]  Evidence ledger scanned 128 files
00:25:12 [INFO]  Priority report generated
00:25:15 [ERROR] Build failed: mvn package
00:25:16 [WARN]  Start skipped due to build failure
00:25:17 [INFO]  Repair loop entered
```

**日志过滤器：**

```
[info] [error] [warning] [Clear]
```

### LearnPanel 格式

**边框：** 紫色，1px 圆角

**字段：**

```
Status   : pending
Records  : 0
Focus    : Patterns & fixes
Source   : Verified issues
```

**数据来源：**

LearnPanel 必须订阅：

```
TUIStateStore.subscribe("learn", callback)
```

LearnData 必须包含：

```
status: str
records: int
focus: str
source: str
detail_view: LearnDetailView | None
is_detail: bool
```

`[详情]` 不是纯文本，必须触发 Learn Detail View。
可使用 Button，也可以先用键盘 action，例如 Enter 展开、Esc 返回。

### Learn Detail View

Learn Detail View 用于审计 Learn 模块沉淀的内容。

**按钮：** `[详情]`（紫色边框）

Learn Detail View 用于审计 Learn 模块沉淀的内容。

展开后显示四类记忆：

1. **Verified Fixes**

   - 已验证修复经验。
   - 必须包含 root cause、capability、verify status、source artifact。

2. **Issue Patterns**

   - 问题模式。
   - 必须包含 signal、cause、recommended action、confidence、source。

3. **Project Facts**

   - 项目事实。
   - 必须包含 fact type、value、evidence refs。

4. **User Rules**
   - 用户确认规则。
   - 优先级最高。
   - 可 accepted、rejected、pinned。

**操作：**

```
[A] 接受
[E] 编辑
[R] 拒绝
[P] 固定
[D] 删除
[Esc] 返回

```

**实现约束：**

Learn Detail View 必须来自 `LearnData.detail_view`。
PipelineIntegration 在调用 `store.update_learn(...)` 时必须传入完整的 `LearnDetailView`，不能只传 records 数量。

### Artifacts 格式

Artifacts 面板用于展示 `.to-vibe/` 目录下生成的工程产物。

**视觉样式：**

\- 标题：`Artifacts`
\- 主色：紫色或灰紫色
\- 文件使用 `·`
\- 目录使用 `📁`

**文件列表：**

```
· evidence-ledger.json
· priority-report.md
· baseline-verify.json
· repair-plan.md
📁 claude-tasks/
📁 learn/
```

---

**数据来源：**

Artifacts 必须订阅：

```
TUIStateStore.subscribe("artifacts", callback)
```

PipelineIntegration 应在每个阶段完成后扫描 `.to-vibe/`，并调用：

```
store.update_artifacts(...)
```

Artifacts 不能长期为空。即使还没有产物，也应展示明确的空状态：

```
No artifacts yet
```

## 四、Footer（`image.png` / `image3.1.png`）

Footer 用于展示当前工作区、执行配置、Executor 状态和快捷键。

**显示格式：**

```

./library_system | default | dry-run │ Executor: local / claude-code ⟳ │ [Space]暂停 [R]重试 [S]跳过 [↑↓]滚动
```

**左侧：** Workspace 路径 + profile 配置 + 当前 mode
**中间：** Executor 状态 + 循环图标 `⟳`
**右侧：** 快捷键标签（`[Space]` 暂停 / `[R]` 重试），快捷键字母为橙色，文字为白色

**字段来源：**

- workspace：当前项目路径
- profile：当前配置 profile
- mode：dry-run / live
- executor：local / claude-code
- sync icon：Executor 连接状态

**快捷键行为：**

- `[Space]`：调用 `integration.pause()`
- `[R]`：调用 `integration.retry()`
- `[S]`：调用 `integration.skip()`
- `[↑↓]`：滚动 LogStream

Footer 不能只显示提示文本。所有快捷键必须接入实际 App action。

## UI 数据流约束

TUI 所有组件必须通过统一状态总线更新。

```
PipelineIntegration
    │
    │ stage_start / stage_complete / progress / log / evidence / issue_found / error
    ▼
PipelineEventBus Adapter
    │
    │ PipelineEvent → UI Data
    ▼
TUIStateStore
    │
    ├── stages    → StageBar
    ├── evidence  → EvidenceCard
    ├── priority  → PriorityCard
    ├── verify    → VerifyTable
    ├── repair    → RepairPanel
    ├── learn     → LearnPanel / LearnDetailView
    ├── logs      → LogStream
    ├── artifacts → Artifacts
    └── session   → Header / Footer
```

设计原则：

1. App 只创建一个 `TUIStateStore`。
2. PipelineIntegration 和 MainScreen 必须共享同一个 Store。
3. 组件不允许自己 new Store。
4. 组件不允许重复定义与 Store 不一致的数据类。
5. 后台线程更新 UI 时，必须通过 Textual 安全方式回到 UI 线程。

## 数据流图

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                                      Runtime Data Flow                                       │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                              │
│  PipelineIntegration                                                                          │
│        │                                                                                     │
│        │  stage_start / stage_complete / progress / log / evidence / issue_found / error      │
│        ▼                                                                                     │
│  ┌───────────────────────────┐                                                               │
│  │ PipelineEventBus Adapter  │                                                               │
│  │ PipelineEvent → UI Data   │                                                               │
│  └─────────────┬─────────────┘                                                               │
│                │                                                                             │
│                ▼                                                                             │
│  ┌────────────────────────────────────────────────────────────────────────────────────────┐  │
│  │ TUIStateStore                                                                           │  │
│  │                                                                                        │  │
│  │ evidence  → EvidenceData                                                               │  │
│  │ priority  → PriorityData                                                               │  │
│  │ verify    → list[VerifyRow]                                                            │  │
│  │ repair    → RepairData                                                                 │  │
│  │ learn     → LearnData + LearnDetailView                                                │  │
│  │ logs      → list[LogEntry]                                                             │  │
│  │ artifacts → list[ArtifactItem]                                                         │  │
│  │ session   → SessionData                                                                │  │
│  └────────────────────────────────────────────────────────────────────────────────────────┘  │
│                │                                                                             │
│                │ subscribe(key, callback)                                                    │
│                ▼                                                                             │
│  ┌─────────────┬──────────────┬──────────────┬─────────────┬────────────┬────────────────┐  │
│  │ Header      │ StageBar     │ EvidenceCard │ VerifyTable │ LearnPanel │ Footer         │  │
│  │ Footer      │ PriorityCard │ RepairPanel  │ LogStream   │ Artifacts  │ MainScreen Tabs│  │
│  └─────────────┴──────────────┴──────────────┴─────────────┴────────────┴────────────────┘  │
│                                                                                              │
│  Rule: UI components do not own business state. They only render TUIStateStore snapshots.     │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 当前设计与实现差距

当前 UI 原型已经覆盖主要视觉结构，但实现上必须优先解决以下问题：

```
| 模块 | 设计目标 | 当前风险 | 优先级 |
|---|---|---|---|
| 数据模型 | 所有组件使用统一 dataclass | 组件内重复定义，字段不一致 | P0 |
| Store wiring | 组件订阅 TUIStateStore | 当前组件没有订阅 | P0 |
| App 集成 | App / Integration / Screen 共享同一 Store | 可能实例隔离 | P0 |
| Footer 快捷键 | Space/R/S 控制 pipeline | 可能只是 notify | P0 |
| TabBar | 使用 Textual Widget | plain class 无法渲染 | P0 |
| RepairPanel | Logs 顶部展示 Repair Loop | 当前缺失 | P1 |
| LogStream | 显示 PipelineEvent 转换后的日志 | 缺少 adapter | P1 |
| Learn Detail | 展示四类记忆并支持操作 | detail_view 未接通 | P1 |
| Artifacts | 展示 `.to-vibe/` 产物 | 当前可能为空 | P1 |
| Header/Footer | 动态显示真实 session | 存在硬编码风险 | P2 |
```

落地顺序：

```
P0：统一数据模型 → 单 Store 注入 → 组件订阅 → 快捷键接入真实 pipeline
P1：RepairPanel → LogStream adapter → Learn Detail → Artifacts
P2：Header/Footer 动态化 → 样式细节 → 交互 polish
```

---

## Pipeline StageBar（5-stage chevron）

**布局：** 横向排列 5 个箭头形状色块

```
[✔ Evidence ✔] → [✔ Priority ✔] → [✔ Verify ✔] → [✔ Repair ✔] → [◌ Learn]
```

**颜色与图标：**
| Stage | 颜色 | 完成图标 | 未完成图标 |
|---|---|---|---|
| Evidence | 绿色 `#238636` | `✔` 双勾 | — |
| Priority | 橙黄色 `#d29922` | `✔` 双勾 | — |
| Verify | 红色 `#da3633` | `✔` 双勾 | — |
| Repair | 蓝色 `#1f6feb` | `✔` 双勾 | — |
| Learn | 紫色 `#a371f7` | `◌` 虚线圆 | — |

**注意：** 最后一个 Learn 阶段在未完成时只有左侧虚线圆 `◌`，无右侧勾选框

---

## 颜色定义

| 用途               | 色值                  | 说明          |
| ------------------ | --------------------- | ------------- |
| Surface 背景       | `#0b1015` / `#0d1117` | 极深藏青/黑色 |
| Block / Header BG  | `#161b22`             | 略浅于背景    |
| Evidence 边框/标题 | `#238636`             | 绿色          |
| Priority 边框/标题 | `#d29922`             | 橙黄色        |
| Verify 边框/标题   | `#da3633`             | 红色          |
| Repair 边框/标题   | `#1f6feb`             | 蓝色          |
| Learn 边框/标题    | `#a371f7`             | 紫色          |
| Pass status        | `#238636`             | 绿色          |
| Fail status        | `#da3633`             | 红色          |
| Skip status        | `#d29922`             | 橙黄色        |
| Active 状态        | `#1f6feb`             | 蓝色          |
| INFO log           | `#238636`             | 绿色          |
| WARN log           | `#d29922`             | 橙黄色        |
| ERROR log          | `#da3633`             | 红色          |
| 快捷键字母         | `#d29922`             | 橙色高亮      |

## 组件实现文件对照

| 组件                           | 文件路径                                      |
| ------------------------------ | --------------------------------------------- |
| ToVibeApp（主应用 + BINDINGS） | `src/to_vibe/tui/app.py`                      |
| MainScreen（3-Tab 切换）       | `src/to_vibe/tui/screens/main_screen.py`      |
| Header                         | `src/to_vibe/tui/components/header.py`        |
| StageBar                       | `src/to_vibe/tui/components/stage_bar.py`     |
| EvidenceCard                   | `src/to_vibe/tui/components/evidence_card.py` |
| PriorityCard                   | `src/to_vibe/tui/components/priority_card.py` |
| VerifyTable                    | `src/to_vibe/tui/components/verify_table.py`  |
| LogStream                      | `src/to_vibe/tui/components/log_stream.py`    |
| LearnPanel                     | `src/to_vibe/tui/components/learn_panel.py`   |
| Artifacts                      | `src/to_vibe/tui/components/artifacts.py`     |
| Footer                         | `src/to_vibe/tui/components/footer.py`        |
| ChatPanel                      | `src/to_vibe/tui/screens/chat_panel.py`       |
| ToVibePanel                    | `src/to_vibe/tui/screens/to_vibe_panel.py`    |
| LogsPanel                      | `src/to_vibe/tui/screens/logs_panel.py`       |
| Styles（颜色定义）             | `src/to_vibe/tui/styles.py`                   |

---

## 图片与设计元素对应表

| 图片文件       | 设计阶段   | 覆盖内容                                                                                                      |
| -------------- | ---------- | ------------------------------------------------------------------------------------------------------------- |
| `image1.1.png` | 初始布局   | 4 层水平结构（Header → 命令行 → Key-Value → StageBar），Pipeline 5-stage chevron 样式                         |
| `image2.1.png` | Bento Grid | 2 列 40:60 布局，EvidenceCard（绿色）+ PriorityCard（橙色）左侧纵向堆叠，Baseline Verify 表格（红色）右侧贯穿 |
| `image3.1.png` | Logs 视图  | Logs Header 变体，Repair Loop Summary 区块，LogStream + LearnPanel + Artifacts 三列布局，Footer 快捷键        |
| `image.png`    | 全局整合   | 左右分栏（4:6），Tab 切换组，系统监控（CPU/RAM/Battery/Credit），整体比例与边框样式                           |

# 组件落地状态文本图

用来避免原型图和实际代码脱节。

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                                  Design → Implementation Gap                                 │
├───────────────────────────┬──────────────────────────────┬────────────────────┬─────────────┤
│ Module                    │ Design Target                │ Current Risk       │ Priority    │
├───────────────────────────┼──────────────────────────────┼────────────────────┼─────────────┤
│ Unified Data Models       │ one source of truth          │ duplicate dataclass│ P0          │
│ TUIStateStore Wiring      │ subscribe(key, callback)     │ no subscribers     │ P0          │
│ App Integration           │ one store shared by app      │ possible isolation │ P0          │
│ Footer Shortcuts          │ Space/R/S control pipeline   │ notify only risk   │ P0          │
│ TabBar                    │ real Textual widget          │ plain class risk   │ P0          │
│ RepairPanel               │ visible in Logs tab top      │ missing component  │ P1          │
│ LogStream                 │ pipeline events visible      │ adapter needed     │ P1          │
│ Learn Detail              │ 4 memory types + actions     │ detail not wired   │ P1          │
│ Artifacts                 │ scan .to-vibe outputs        │ empty list risk    │ P1          │
│ Header/Footer Dynamic     │ project/mode/executor live   │ hardcoded risk     │ P2          │
└───────────────────────────┴──────────────────────────────┴────────────────────┴─────────────┘
```

```

```
