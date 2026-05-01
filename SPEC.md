# to-vibe CLI 技术规格文档

> 版本：v2.0
> 日期：2026-05-01
> 状态：初稿

---

## 1. 系统概览

### 1.1 定位

to-vibe 是 **AI 代码生成后的项目工程化 CLI 工具**，将 vibe coding 产物转化为可维护工程资产。

核心流程：

```
Vibe 生成整个系统
    ↓
Evidence Ledger → Priority Report → Baseline Verify → Repair Loop → Learn
```

### 1.2 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 语言 | Python 3.11+ | 主语言 |
| TUI 框架 | Python Textual | 复杂终端布局 |
| LLM 集成 | Anthropic/OpenAI API 兼容 | 左侧 Chat Panel |
| 配置 | to-vibe.yaml | 项目根目录 |
| 会话状态 | session-start.json | JSON 文件 |
| Artifact 存储 | .to-vibe/ | 人类可读产物 |

### 1.3 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Python Textual TUI                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────────┐  ┌────────────────────────────────┐ │
│  │   LLM Chat Panel  │  │         to-vibe Pipeline       │ │
│  │   (左侧 Tab 1)     │  │         (右侧 Tab 2/3)         │ │
│  │                   │  │                                │ │
│  │  [Conversation]   │  │  StageBar: Evidence→Priority→│ │
│  │  [Input Field]    │  │  Verify→Repair→Learn          │ │
│  │                   │  │                                │ │
│  │                   │  │  EvidenceCard │ VerifyTable   │ │
│  │                   │  │  PriorityCard │ LearnPanel   │ │
│  │                   │  │                                │ │
│  │                   │  │  LogStream │ Artifacts         │ │
│  └───────────────────┘  └────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. UI 布局规格

### 2.1 整体布局

采用 Bento 网格布局，分为 3 个 Tab：

| Tab | 标签 | 内容 |
|-----|------|------|
| 1 | `1: chat` | LLM Chat Panel |
| 2 | `2: to-vibe` | Pipeline + Cards + Table |
| 3 | `3: logs` | Log Stream + Artifacts |

### 2.2 Header

```
◇ to-vibe | ~/dev/library_system                    一目main ⏱ 00:25:32
```

| 元素 | 样式 | 说明 |
|------|------|------|
| Brand icon | 蓝色菱形 `◇` | 固定 |
| Brand name | 青色 `to-vibe` | 固定 |
| Path | 灰蓝色 | 动态，当前项目路径 |
| Git branch | 绿色 + 图标 | 来自 `git branch` |
| Timer | 灰色 + 时钟图标 | 会话运行时长 |

### 2.3 Pipeline 阶段条

```
[✅Evidence] -> [✅Priority] -> [✅Verify] -> [✅Repair] -> [◐Learn]
```

| 状态 | 符号 | 颜色 |
|------|------|------|
| completed | ✅ + 绿色边框 | 绿色 |
| active | ◐ + 脉冲动画 | 橙色 |
| failed | ❌ | 红色 |
| skipped | ⊘ | 灰色 |
| pending | `-` | 灰色 |

### 2.4 右侧面板布局 (Tab 2: to-vibe)

```
┌─────────────────────────────────────────────────────────────────┐
│ $ to-vibe run ./project                                        │
├─────────────────────────────────────────────────────────────────┤
│  Project: ./library_system  Mode: dry-run                      │
│  Executor: local / claude-code                                  │
│  Pipeline: Evidence -> Priority -> Verify -> Repair -> Learn   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────┐  ┌───────────────────────────┐  │
│  │ ◇ Evidence Ledger         │  │ ✕ Baseline Verify          │  │
│  │                           │  │                           │  │
│  │ Spring Boot, Thymeleaf,   │  │ L1 Env        ✅ pass      │  │
│  │ MySQL                      │  │ L2 Dep        ✅ pass      │  │
│  │                           │  │ L3 Build      ❌ fail      │  │
│  │ 128 files scanned          │  │ L4 Start      ⊘ skip       │  │
│  │ Ignored: node_modules,     │  │ L5 Smoke      ⊘ skip      │  │
│  │ dist, target, .git         │  │                           │  │
│  │                            │  └───────────────────────────┘  │
│  │ Output: .to-vibe/          │                                  │
│  │ evidence-ledger.json      │  ┌───────────────────────────┐  │
│  └───────────────────────────┘  │ ◇ Learn                   │  │
│  ┌───────────────────────────┐  │                           │  │
│  │ ◐ Priority Report          │  │ Status     pending        │  │
│  │                           │  │ Records    0              │  │
│  │ Blockers:  2              │  │ Focus      Patterns & fixes│  │
│  │ High:      3              │  │ Source     Verified issues │  │
│  │ Medium:    5              │  │                           │  │
│  │                           │  │                     [详情] │  │
│  │ Top issue: P1 backend      │  └───────────────────────────┘  │
│  │         fails to start     │                                  │
│  │ Suggested: Debug           │                                  │
│  └───────────────────────────┘                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.5 日志区布局 (Tab 3: logs)

```
┌─────────────────────────────────────────────────────────────────┐
│ Latest event: Baseline verification completed with failures     │
├─────────────────────────────────────────────────────────────────┤
│  [info]    [error]    [warning]                        [Clear] │
│                                                                 │
│  00:25:10 [INFO] Evidence ledger scanned 128 files...           │
│  00:25:12 [INFO] Priority report generated (2 blockers, 3 high)  │
│  00:25:15 [ERROR] Build failed: mvn package (exit code 1)         │
│  00:25:17 [WARN] Start skipped due to build failure              │
│  00:25:20 [INFO] Repair loop entered (dry-run mode)              │
│                                                                 │
│                                        ┌─────────────────────┐   │
│                                        │ 📁 Artifacts        │   │
│                                        │ · evidence-ledger   │   │
│                                        │ · priority-report   │   │
│                                        │ · baseline-verify   │   │
│                                        │ · repair-plan       │   │
│                                        │ · claude-tasks/     │   │
│                                        └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 2.6 Footer

```
Executor: local / claude-code  ⟳    [Space] 暂停  [R] 重试  [S] 跳过  [↑↓] 滚动
```

---

## 3. 组件规格

### 3.1 StageBar (阶段指示器)

```python
@dataclass
class Stage:
    id: str          # 'evidence' | 'priority' | 'verify' | 'repair' | 'learn'
    label: str
    status: str      # 'pending' | 'active' | 'completed' | 'failed' | 'skipped'
    chevron_icon: str
    border_color: str
```

### 3.2 EvidenceCard

```python
@dataclass
class EvidenceCard:
    stack: list[str]           # ['Spring Boot', 'Thymeleaf', 'MySQL']
    files_scanned: int
    ignored_dirs: list[str]
    output_path: str           # '.to-vibe/evidence-ledger.json'
    border_color: str = 'green'
    icon: str = '◇'
```

### 3.3 PriorityCard

```python
@dataclass
class PriorityCard:
    blockers: int              # P0 count
    high: int                  # P1 count
    medium: int                # P2 count
    top_issue: str
    suggested_capability: str  # 'Debug' | 'Refactor' | 'System' | 'Simplify'
    border_color: str = 'orange'
    icon: str = '◐'
```

### 3.4 VerifyTable

```python
@dataclass
class VerifyRow:
    id: int
    check: str                 # 'Environment' | 'Dependencies' | 'Build' | 'Start' | 'Smoke Test'
    status: str                # 'pass' | 'fail' | 'skip'
    command: str
    icon: str                  # ✅ | ❌ | ⊘

@dataclass
class VerifyTable:
    rows: list[VerifyRow]
    border_color: str = 'red'
    icon: str = '✕'
```

### 3.5 LearnPanel

```python
@dataclass
class LearnPanel:
    status: str                # 'pending' | 'completed'
    records: int
    focus: str                 # 'Patterns & fixes'
    source: str                # 'Verified issues'
    detail_button: bool = True

@dataclass
class LearnDetailView:
    """展开后的视图"""
    verified_fixes: list[dict]
    issue_patterns: list[dict]
    project_facts: list[dict]
    user_rules: list[dict]
    actions: list[str]        # ['A)accept', 'E)edit', 'R)reject', 'P)pin', 'D)delete', 'Esc)return']
```

### 3.6 LogStream

```python
@dataclass
class LogEntry:
    timestamp: str             # 'HH:MM:SS'
    level: str                 # 'INFO' | 'ERROR' | 'WARN'
    text: str

@dataclass
class LogFilters:
    levels: list[str]          # ['info', 'error', 'warning']
    active_filters: set[str]
    clear_button: bool = True
```

### 3.7 Artifacts

```python
@dataclass
class Artifact:
    name: str
    is_directory: bool
    icon: str                  # 📁 for dir, · for file
```

### 3.8 Footer

```python
@dataclass
class Footer:
    executor: str              # 'local / claude-code'
    sync_icon: str             # ⟳
    shortcuts: list[str]        # ['Space)暂停', 'R)重试', 'S)跳过', '↑↓)滚动']
```

---

## 4. LLM 集成规格

### 4.1 配置格式 (to-vibe.yaml)

```yaml
llm:
  provider: "anthropic"  # 'anthropic' | 'openai'
  api_key: "${ANTHROPIC_API_KEY}"  # 环境变量引用
  model: "claude-sonnet-4-7"
  base_url: ""  # 可选，自定义 endpoint
  max_tokens: 4096
  timeout: 30

pipeline:
  mode: "dry-run"  # 'dry-run' | 'live'
  max_iterations: 50
  exit_level: "maintainable"  # 'stabilized' | 'maintainable' | 'ship-ready'

session:
  heartbeat_interval_seconds: 30
  ttl_seconds: 300
  recovery_policy: "auto"
```

### 4.2 API 兼容

| Provider | API 格式 | 认证方式 |
|----------|----------|----------|
| Anthropic | `https://api.anthropic.com/v1/messages` | `x-api-key` header |
| OpenAI | `https://api.openai.com/v1/chat/completions` | `Authorization: Bearer` header |

### 4.3 Chat Panel 行为

| 行为 | 说明 |
|------|------|
| 输入 | 用户在底部输入框输入，回车发送 |
| 输出 | LLM 响应流式输出到对话区 |
| 历史 | 保留完整对话历史，可滚动查看 |
| 快捷键 | `Enter` 发送，`Ctrl+C` 取消 |

---

## 5. MCP 协议规格

### 5.1 消息类型

```python
# Invoke (Claude → to-vibe)
@dataclass
class Invoke:
    method: str               # 'to-vibe.run', 'to-vibe.pause', 'to-vibe.retry'
    params: dict
    id: str

# Notification (to-vibe → Claude)
@dataclass
class Notification:
    id: str
    type: str                 # 'log' | 'stage_update' | 'progress' | 'action_required' | 'error'
    timestamp: str
    stage: str                # 'evidence_ledger' | 'priority_report' | 'baseline_verify' | 'repair_loop' | 'learn'
    level: str                 # 'info' | 'warn' | 'error'
    session_id: str
    content: dict
```

### 5.2 Notification 类型

| type | 说明 | content 字段 |
|------|------|-------------|
| `log` | 日志行 | `{text, level, timestamp}` |
| `stage_start` | 阶段开始 | `{stage, description}` |
| `stage_complete` | 阶段结束 | `{stage, summary, results}` |
| `progress` | 进度更新 | `{current, total, detail}` |
| `evidence` | 发现证据 | `{file, line, fact, status}` |
| `issue_found` | 发现问题 | `{priority, type, description}` |
| `action_required` | 暂停等待 | `{prompt, options[], default}` |
| `error` | 错误 | `{stage, message, recovery}` |

### 5.3 Action Required 格式

```json
{
  "type": "action_required",
  "content": {
    "prompt": "Evidence Ledger 完成，发现 3 个问题",
    "options": [
      {"action": "continue", "label": "继续执行", "description": "进入 Priority Report"},
      {"action": "retry", "label": "重试", "description": "重新扫描项目"},
      {"action": "skip", "label": "跳过", "description": "跳过当前阶段"}
    ],
    "default": "continue"
  }
}
```

---

## 6. Learn 模块规格

### 6.1 4 类记忆

| 类型 | 说明 | 优先级 |
|------|------|--------|
| `project_fact` | 项目事实（技术栈、架构） | 中 |
| `verified_fix` | 已验证的修复经验 | 高 |
| `issue_pattern` | 问题模式 → 推荐处理方式 | 中 |
| `user_confirmed_rule` | 用户明确确认的规则 | 最高 |

### 6.2 触发时机

| 时机 | 行为 |
|------|------|
| 默认 | 完整流程结束后触发 |
| Repair Loop 中 | 只产生候选经验，不直接存储 |
| 手动 | `to-vibe learn` 命令触发 |

### 6.3 7 步学习流程

```
1. Collect   → 从 repair-loop.json, baseline-verify.json, priority-report.json 收集候选
2. Filter    → 过滤未验证、无证据、跨项目内容
3. Summarize → LLM 总结为可复用经验
4. Validate  → 检查 evidence_refs 和 verify_status
5. Review    → 重要规则进入 pending，等待用户 accept/reject
6. Store     → 写入 .to-vibe/learn/ + SQLite L0
7. Retrieve  → 按 scope + evidence + similarity 召回
```

### 6.4 存储层次

| 层次 | 位置 | 职责 |
|------|------|------|
| 人类可读 | `.to-vibe/learn/` | 查看、版本管理、LLM 上下文 |
| 结构化主存 | SQLite | 结构化查询 |
| 语义检索 | L1 向量 | 相似问题召回 |

### 6.5 Learn 存储目录

```
.to-vibe/
  learn/
    learn-summary.md       # 人类可读总结
    learned-rules.json     # 已确认规则
    verified-fixes.json    # 已验证修复
    issue-patterns.json    # 问题模式
    rejected-lessons.json  # 拒绝的经验
```

### 6.6 SQLite Schema

```sql
CREATE TABLE learn_records (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,              -- project_fact | verified_fix | issue_pattern | user_confirmed_rule
    project_id TEXT NOT NULL,
    session_id TEXT,
    issue_id TEXT,
    capability TEXT,
    title TEXT,
    summary TEXT,
    source_artifact TEXT,
    evidence_refs TEXT,              -- JSON array
    verify_status TEXT,              -- passed | pending | rejected
    confidence REAL DEFAULT 0.5,
    accepted_by_user BOOLEAN,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    content_hash TEXT
);
```

---

## 7. 交互规格

### 7.1 快捷键

| 按键 | 动作 | 说明 |
|------|------|------|
| `Space` | 暂停 | 暂停当前流程，保持状态 |
| `R` | 重试 | 重试当前步骤（Repair Loop 或 Verify 失败层）|
| `S` | 跳过 | 跳过当前阶段 |
| `↑` / `↓` | 滚动 | 日志区域滚动 |
| `Tab` | 切换 Tab | 在 1:chat / 2:to-vibe / 3:logs 之间切换 |
| `Esc` | 返回 | 从详情视图返回 |

### 7.2 日志过滤器

| 按钮 | 作用 |
|------|------|
| `[info]` | 显示 INFO 级别日志 |
| `[error]` | 显示 ERROR 级别日志 |
| `[warning]` | 显示 WARN 级别日志 |
| `[Clear]` | 清空日志区域 |

### 7.3 [详情] 按钮

点击后切换到 Learn 详情视图，显示：
- Verified Fixes（已验证修复）
- Issue Patterns（问题模式）
- Project Facts（项目事实）
- User Rules（用户规则）

支持操作：`[A]接受 [E]编辑 [R]拒绝 [P]固定 [D]删除 [Esc]返回`

---

## 8. 配置规格

### 8.1 to-vibe.yaml 完整格式

```yaml
version: "2.0"

llm:
  provider: "anthropic"
  api_key: "${ANTHROPIC_API_KEY}"
  model: "claude-sonnet-4-7"
  base_url: ""
  max_tokens: 4096
  timeout: 30

pipeline:
  mode: "dry-run"
  max_iterations: 50
  exit_level: "maintainable"
  evidence:
    exclude_patterns:
      - "node_modules/**"
      - ".git/**"
      - "dist/**"
      - "build/**"
      - "target/**"
  priority:
    rules:
      - "P0 阻断性问题优先"
      - "P1 影响开发效率次之"
      - "P2 优化建议最后"
  verify:
    layers:
      L1:
        enabled: true
        max_retries: 3
      L2:
        enabled: true
        max_retries: 3
      L3:
        enabled: true
        max_retries: 3
      L4:
        enabled: true
        max_retries: 2
      L5:
        enabled: true
        max_retries: 1

session:
  heartbeat_interval_seconds: 30
  ttl_seconds: 300
  recovery_policy: "auto"

learn:
  trigger: "on_complete"  # 'on_complete' | 'manual'
  min_confidence: 0.5
  max_records: 1000
  retention_days: 180

ui:
  log_levels:
    - "info"
    - "error"
    - "warning"
  auto_scroll: true
  compact_mode: false
```

---

## 9. 文件结构

```
to-vibe-cli/
├── pyproject.toml
├── to-vibe.yaml
├── README.md
├── SPEC.md
├── CLAUDE.md
├── src/
│   ├── __init__.py
│   ├── cli.py                    # CLI 入口
│   ├── config.py                 # 配置解析
│   ├── tui/
│   │   ├── __init__.py
│   │   ├── app.py               # Textual App 主类
│   │   ├── screens/
│   │   │   ├── __init__.py
│   │   │   ├── main_screen.py   # 主屏幕（3 Tab）
│   │   │   ├── chat_panel.py    # Tab 1: LLM Chat
│   │   │   ├── to_vibe_panel.py # Tab 2: Pipeline + Cards
│   │   │   └── logs_panel.py    # Tab 3: Log + Artifacts
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── header.py        # Header 组件
│   │   │   ├── stage_bar.py     # StageBar 阶段指示器
│   │   │   ├── evidence_card.py # EvidenceCard
│   │   │   ├── priority_card.py # PriorityCard
│   │   │   ├── verify_table.py  # VerifyTable
│   │   │   ├── learn_panel.py   # LearnPanel + LearnDetail
│   │   │   ├── log_stream.py    # LogStream + LogFilters
│   │   │   ├── artifacts.py     # Artifacts 列表
│   │   │   └── footer.py        # Footer + 快捷键
│   │   └── styles.py            # 样式定义
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py            # MCP Server
│   │   ├── protocol.py          # Notification/Invoke 定义
│   │   └── handler.py           # 命令处理
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── client.py            # LLM API 客户端
│   │   ├── anthropic.py         # Anthropic 兼容
│   │   └── openai.py            # OpenAI 兼容
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── evidence_ledger.py   # Evidence Ledger 模块
│   │   ├── priority_report.py   # Priority Report 模块
│   │   ├── baseline_verify.py   # Baseline Verify (L1-L5)
│   │   ├── repair_loop.py       # Repair Loop 模块
│   │   └── learn.py             # Learn 模块
│   ├── learn/
│   │   ├── __init__.py
│   │   ├── collector.py         # 收集候选经验
│   │   ├── filter.py            # 过滤
│   │   ├── summarizer.py        # LLM 总结
│   │   ├── validator.py         # 验证
│   │   ├── reviewer.py          # 用户审核
│   │   └── storage.py           # 存储（.to-vibe/learn/ + SQLite）
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── sqlite.py            # SQLite 主存
│   │   └── artifacts.py          # Artifact 读写
│   └── utils/
│       ├── __init__.py
│       ├── logger.py            # 日志
│       └── locks.py             # 文件锁
├── tests/
├── .to-vibe/                    # 运行时生成
│   ├── evidence_ledger/
│   ├── priority_report/
│   ├── baseline_verify/
│   ├── repair_loop/
│   └── learn/
└── session-start.json           # 会话状态
```

---

## 10. 实现优先级

| 阶段 | 内容 | 优先级 |
|------|------|--------|
| 1 | 配置解析 + 日志框架 + CLI 入口 | P0 |
| 2 | MCP Server + Notification 协议 | P0 |
| 3 | Textual 基础布局 + 3 Tab 导航 | P0 |
| 4 | 右侧面板：StageBar + Cards + Table | P1 |
| 5 | 右侧面板：LearnPanel + LogStream | P1 |
| 6 | 左侧面板：LLM Chat API 集成 | P1 |
| 7 | 交互系统：暂停/重试/跳过/过滤 | P2 |
| 8 | Pipeline 串联：Ledger→Report→Verify→Loop→Learn | P2 |

---

## 11. 验收标准

- [ ] to-vibe.yaml 配置可正确解析
- [ ] MCP Server 可接收 invoke 并发送 notification
- [ ] TUI 3 Tab 可切换显示
- [ ] StageBar 5 阶段正确显示
- [ ] EvidenceCard / PriorityCard / VerifyTable 正确渲染
- [ ] LogStream 支持 level 过滤
- [ ] Learn 模块 4 类记忆正确存储
- [ ] LLM Chat 可发送消息并显示响应
- [ ] 快捷键 Space/R/S/↑↓/Tab/Esc 可用
- [ ] [详情] 展开 Learn 详情视图