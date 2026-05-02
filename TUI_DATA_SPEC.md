# TUI Data Specification

> 本文档描述 TUI 组件需要对接的真实数据来源、数据结构、刷新机制。

---

## 1. 数据流全景

```
Pipeline Workers (orchestrator.py)
    │
    ├── EvidenceLedgerScanner  →  evidence-ledger.json
    │                               │
    │                               ▼
    │                          TUIStateStore.update_evidence()
    │                               │
    │                               ▼
    │                          EvidenceCard (subscribes to "evidence")
    │
    ├── PriorityAnalyzer         →  priority-report.json
    │                               │
    │                               ▼
    │                          TUIStateStore.update_priority()
    │                               │
    │                               ▼
    │                          PriorityCard (subscribes to "priority")
    │
    ├── BaselineVerifier         →  baseline-verify.json
    │                               │
    │                               ▼
    │                          TUIStateStore.update_verify()
    │                               │
    │                               ▼
    │                          VerifyTable (subscribes to "verify")
    │
    ├── RepairLoop               →  repair-loop.json
    │                               │
    │                               ▼
    │                          TUIStateStore.update_repair()
    │                               │
    │                               ▼
    │                          RepairPanel (subscribes to "repair")
    │
    └── LearnCollector          →  learn/learn-summary.json
                                    │
                                    ▼
                               TUIStateStore.update_learn()
                                    │
                                    ▼
                               LearnPanel (subscribes to "learn")
```

---

## 2. 各阶段数据结构

### 2.1 Evidence（证据账本）

**来源**: `EvidenceLedgerScanner.scan()` → `.to-vibe/evidence-ledger.json`

**JSON 字段**:
```json
{
  "project_path": ".",
  "tech_stack": ["python", "react"],
  "files_scanned": 171,
  "ignored_dirs": ["node_modules", "__pycache__", ".git", ".venv", "dist", "build"],
  "output_path": ".to-vibe/evidence-ledger.json"
}
```

**TUI dataclass** (`TUIStateStore.EvidenceData`):
```python
@dataclass
class EvidenceData:
    tech_stack: list[str]       # 探测到的技术栈
    files_scanned: int          # 扫描文件总数
    ignored: list[str]          # 忽略的目录
    output_path: str            # 证据账本路径
```

**展示位置**: EvidenceCard（主屏幕 Tab1 左上）

---

### 2.2 Priority（优先级分析）

**来源**: `PriorityAnalyzer.analyze()` → `.to-vibe/priority-report.json`

**JSON 字段**:
```json
{
  "project_path": ".",
  "blockers": 0,
  "high": 2,
  "medium": 3,
  "issues": [
    {"id": 1, "type": "blocker", "severity": "blocker", "title": "...", "file": "...", "line": 0}
  ],
  "top_issue": "Missing type stubs for external deps",
  "suggested_capability": "dependency-repair",
  "output_path": ".to-vibe/priority-report.json"
}
```

**TUI dataclass** (`TUIStateStore.PriorityData`):
```python
@dataclass
class PriorityData:
    blockers: int           # blockers 数量
    high: int               # high 数量
    medium: int             # medium 数量
    top_issue: str         # 排名第一的问题
    suggested: str           # 建议的修复能力
```

**展示位置**: PriorityCard（主屏幕 Tab1 右上）

---

### 2.3 Verify（基线验证）

**来源**: `BaselineVerifier.verify()` → `.to-vibe/baseline-verify.json`

**JSON 字段**:
```json
{
  "project_path": ".",
  "layer_results": [
    {"layer_id": "L1", "check": "Environment",  "status": "pass",   "command": "python3 --version", "output": "", "retries": 0},
    {"layer_id": "L2", "check": "Dependencies",  "status": "fail",   "command": "", "output": "", "retries": 3},
    {"layer_id": "L3", "check": "Build",          "status": "fail",   "command": "", "output": "", "retries": 3},
    {"layer_id": "L4", "check": "Start",           "status": "skip",  "command": "blocked", "output": "", "retries": 0},
    {"layer_id": "L5", "check": "Smoke Test",      "status": "skip",  "command": "blocked", "output": "", "retries": 0}
  ],
  "output_path": ".to-vibe/baseline-verify.json"
}
```

**TUI dataclass** (`TUIStateStore.VerifyRow`):
```python
@dataclass
class VerifyRow:
    id: int          # 序号 (1-5)
    check: str       # 检查项名称
    status: str      # pass / fail / skipped / active
    command: str     # 执行的命令
```

**TUI 数据更新** (pipeline_integration.py lines 99-109):
```python
rows = []
for i, (check_name, status) in enumerate([
    ("Environment", verify_result.environment_status),
    ("Dependencies", verify_result.dependencies_status),
    ("Build", verify_result.build_status),
    ("Start", verify_result.start_status),
    ("Smoke Test", verify_result.smoke_test_status),
], 1):
    status_str = status.value if hasattr(status, "value") else str(status)
    rows.append(VerifyRow(id=i, check=check_name, status=status_str, command=f"L{i} check"))
self.store.update_verify(rows)
```

**展示位置**: VerifyTable（主屏幕 Tab1 下部表格）

---

### 2.4 Repair（修复循环）

**来源**: `RepairLoop.run()` → `.to-vibe/repair-loop.json`

**JSON 字段**:
```json
{
  "project_path": ".",
  "mode": "dry-run",
  "issues_fixed": 0,
  "issues_remaining": 2,
  "iterations": 0,
  "output_path": ".to-vibe/repair-loop.json"
}
```

**TUI dataclass** (`TUIStateStore.RepairData`):
```python
@dataclass
class RepairData:
    selected_issue: str    # 选定的问题（来自 priority top_issue）
    capability: str       # 修复能力（来自 priority suggested_capability）
    mode: str             # dry-run / apply
    apply_status: str     # skipped / applied
    record_path: str      # 修复记录文件路径
```

**展示位置**: RepairPanel（主屏幕 Tab2）

---

### 2.5 Learn（学习总结）

**来源**: `LearnCollector.collect()` → `.to-vibe/learn/learn-summary.json`

**JSON 字段**:
```json
{
  "project_path": ".",
  "items_learned": 2,
  "items_total": 2,
  "output_path": ""
}
```

**TUI dataclass** (`TUIStateStore.LearnData`):
```python
@dataclass
class LearnData:
    status: str        # pending / completed
    records: int       # items_learned 数量
    focus: str         # 学习重点
    source: str        # 学习来源
```

**展示位置**: LearnPanel（主屏幕 Tab3）

---

## 3. 日志数据（LogStream）

**来源**: PipelineEventBus 所有事件

**TUI dataclass** (`TUIStateStore.LogEntry`):
```python
@dataclass
class LogEntry:
    timestamp: str    # HH:MM:SS 格式
    level: str       # INFO / WARN / ERROR
    message: str    # 日志消息
```

**订阅机制**: `_LogStreamHandler` 是 PipelineEventBus 的订阅者，将所有事件转为 LogEntry 追加到 `TUIStateStore._log_entries`，最多保留 500 条。

**展示位置**: LogsPanel（主屏幕底部日志流）

---

## 4. PipelineStateMachine 状态数据

**来源**: `PipelineStateMachine` 订阅到 `TUIStateStore`

**派生状态**（由 `_on_pipeline_state()` 计算）:
- `_current_stage`: 当前阶段字符串（idle/evidence/priority/verify/repair/learn/completed/failed）
- `_stages_completed`: 已完成阶段列表
- `_progress`: 0.0-1.0 进度
- `_error`: 错误消息字符串

**订阅 key**: "stage", "progress", "error"

---

## 5. 刷新机制

| 数据类型 | 更新频率 | 更新方式 |
|---------|---------|---------|
| Evidence | 每 Pipeline 执行 1 次 | `update_evidence()` 一次性写入 |
| Priority | 每 Pipeline 执行 1 次 | `update_priority()` 一次性写入 |
| Verify | 每 Pipeline 执行 1 次 | `update_verify()` 一次性写入 |
| Repair | 每 Pipeline 执行 1 次 | `update_repair()` 一次性写入 |
| Learn | 每 Pipeline 执行 1 次 | `update_learn()` 一次性写入 |
| Log | 实时（每个 PipelineEvent 触发） | `append_log()` 增量追加 |
| Stage/Progress/Error | 实时（PipelineStateMachine 回调） | `_notify()` 广播 |

---

## 6. 文件持久化

所有 Pipeline 中间结果写入 `.to-vibe/` 目录：

| 文件 | 内容 | 写入时机 |
|------|------|---------|
| `.to-vibe/evidence-ledger.json` | 扫描结果 | Stage 1 完成时 |
| `.to-vibe/priority-report.json` | 优先级报告 | Stage 2 完成时 |
| `.to-vibe/baseline-verify.json` | 验证结果 | Stage 3 完成时 |
| `.to-vibe/repair-loop.json` | 修复记录 | Stage 4 完成时 |
| `.to-vibe/learn/learn-summary.json` | 学习总结 | Stage 5 完成时 |
| `.to-vibe/to-vibe.log` | 运行日志 | Logger 初始化时 |

TUI 重启后可读取这些文件恢复状态（暂未实现，未来可扩展）。

---

## 7. MCP 通知数据

`MCPNotificationHandler` 将 PipelineEvent 转发为 MCP 通知：

```python
payload = {
    "text": event.message,
    "level": event.level,
    "stage": event.stage,
    "timestamp": event.timestamp,
    **(event.data or {}),
}
```

MCP client（Claude Code）通过 `server_send_notification` 接收，用于实时进度同步。
