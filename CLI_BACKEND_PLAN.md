# CLI TUI 后端实现模块规划

> 本文档规划 to-vibe TUI 与后端 pipeline 之间的状态同步、事件驱动、组件协作架构。

---

## 一、现状分析

### 已实现（Stub 级别以上）

| 模块 | 文件 | 状态 |
|---|---|---|
| CLI 入口 | `src/to_vibe/cli.py` | run/learn 命令框架完成 |
| 管道编排 | `src/to_vibe/pipeline/orchestrator.py` | 5 阶段串联完成 |
| Evidence Ledger | `src/to_vibe/pipeline/evidence_ledger.py` | 完全实现 |
| Priority Report | `src/to_vibe/pipeline/priority_report.py` | 完全实现 |
| Baseline Verify | `src/to_vibe/pipeline/baseline_verify.py` | L1 实现，L2-L5 stub |
| Repair Loop | `src/to_vibe/pipeline/repair_loop.py` | 框架完成，`_apply_fix` stub |
| Learn | `src/to_vibe/learn/learn.py` | 完全实现 |
| TUI App | `src/to_vibe/tui/app.py` | 启动 + Tab 切换骨架 |
| MainScreen | `src/to_vibe/tui/screens/main_screen.py` | 3-Tab 显示/隐藏切换 |
| ChatPanel | `src/to_vibe/tui/screens/chat_panel.py` | `_stream_response` stub |
| LLM Client | `src/to_vibe/llm/client.py` | 工厂模式，支持 Anthropic/OpenAI |

### 缺失的后端模块（阻碍 TUI 真正运转）

```
PipelineOrchestrator ←→ TUI（无状态同步通道）
                     ←→ MCP（无 notification 推送）
                     ←→ ChatPanel（无流式对话）
                     ←→ LogStream（无日志实时推送）
                     ←→ StageBar（无阶段状态更新）
```

---

## 二、缺失模块详细规划

### Module 1: `pipeline/state_machine.py` — 管道状态机

**职责：** 管理管道生命周期状态，驱动 StageBar 更新，触发 MCP notification。

**状态定义：**
```python
class PipelineStage(Enum):
    IDLE = "idle"
    EVIDENCE = "evidence"
    PRIORITY = "priority"
    VERIFY = "verify"
    REPAIR = "repair"
    LEARN = "learn"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class StageStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
```

**核心接口：**
```python
class PipelineState:
    current_stage: PipelineStage
    current_status: StageStatus
    stages: dict[PipelineStage, StageStatus]
    progress: float  # 0.0 ~ 1.0
    error_message: str | None

    def advance(self, stage: PipelineStage, status: StageStatus) -> None: ...
    def set_error(self, message: str) -> None: ...
    def pause(self) -> None: ...
    def resume(self) -> None: ...
    def reset(self) -> None: ...

class PipelineStateMachine:
    _state: PipelineState
    _subscribers: list[Callable[[PipelineState], None]]

    def subscribe(self, callback: Callable[[PipelineState], None]) -> None: ...
    def emit(self, stage: PipelineStage, status: StageStatus) -> None: ...
    def run_sync(self, project_path: Path) -> PipelineContext: ...
    async def run_async(self, project_path: Path) -> PipelineContext: ...
```

**触发时机：**
- 每个阶段开始 → `emit(stage, StageStatus.ACTIVE)`
- 每个阶段完成 → `emit(stage, StageStatus.COMPLETED)`
- 阶段失败 → `emit(stage, StageStatus.FAILED)` → 停止后续阶段
- 全部完成 → `emit(COMPLETED, COMPLETED)`

**事件订阅者（待实现 Module 2）：**
```python
# 订阅者接口
on_stage_change(state: PipelineState) -> None
on_progress_update(progress: float, message: str) -> None
on_error(error: str, stage: PipelineStage) -> None
on_complete(ctx: PipelineContext) -> None
```

---

### Module 2: `tui/state_store.py` — TUI 状态响应式存储

**职责：** 作为 TUI 的状态中心，订阅 PipelineStateMachine，驱动各组件的实时更新。

**架构：** 使用 Python `asyncio.Queue` + Textual 的 `reactive` 属性驱动 UI 更新。

```python
from textual.reactive import reactive

class TUIStateStore:
    """TUI 全局状态存储，所有组件订阅此 store。"""

    # Reactive 属性 — 变更时自动触发组件 refresh
    current_stage: reactive[str] = reactive("idle")
    stages_completed: reactive[list[str]] = reactive([])
    progress: reactive[float] = reactive(0.0)

    # 各组件数据
    evidence_data: reactive[dict | None] = reactive(None)
    priority_data: reactive[dict | None] = reactive(None)
    verify_rows: reactive[list[VerifyRow]] = reactive([])
    repair_state: reactive[dict] = reactive({})
    learn_data: reactive[dict] = reactive({})
    log_entries: reactive[list[LogEntry]] = reactive([])

    # 订阅 pipeline 状态机
    def bind_pipeline(self, state_machine: PipelineStateMachine) -> None:
        state_machine.subscribe(self._on_pipeline_state)

    def _on_pipeline_state(self, state: PipelineState) -> None:
        # 将 pipeline 状态发布到 TUI 主线程
        self.call_later(lambda: self._apply_state(state))

    def _apply_state(self, state: PipelineState) -> None:
        self.current_stage = state.current_stage.value
        self.stages_completed = [s.value for s, status in state.stages.items()
                                 if status == StageStatus.COMPLETED]
        self.progress = state.progress
```

**与组件的绑定方式：**
```python
# StageBar 订阅
store.bind_pipeline(state_machine)
StageBar(store=store)  # 通过 @watch(store.current_stage) 自动更新

# LogStream 订阅
store.log_entries.subscribe(lambda entries: log_stream.refresh(entries))
```

---

### Module 3: `pipeline/event_bus.py` — 管道事件总线

**职责：** 管道内各阶段通过事件总线发布日志和状态，事件同时分发给：
1. TUI LogStream（实时日志）
2. MCP Server（推送 notification 给 Claude Code）
3. PipelineStateMachine（状态机更新）

```python
from datetime import datetime

class PipelineEvent:
    timestamp: str
    level: str  # INFO/WARN/ERROR
    stage: str
    message: str
    data: dict | None = None

class PipelineEventBus:
    _subscribers: list[Callable[[PipelineEvent], None]] = []

    @classmethod
    def subscribe(cls, handler: Callable[[PipelineEvent], None]) -> None:
        cls._subscribers.append(handler)

    @classmethod
    def emit(cls, event: PipelineEvent) -> None:
        for handler in cls._subscribers:
            try:
                handler(event)
            except Exception:
                pass  # 不因单个 handler 异常中断广播

    # 便捷方法
    @classmethod
    def log(cls, stage: str, message: str, level: str = "INFO") -> None:
        cls.emit(PipelineEvent(
            timestamp=datetime.now().strftime("%H:%M:%S"),
            level=level,
            stage=stage,
            message=message,
        ))

    @classmethod
    def stage_start(cls, stage: str) -> None: ...
    @classmethod
    def stage_complete(cls, stage: str, result: Any) -> None: ...
    @classmethod
    def stage_fail(cls, stage: str, error: str) -> None: ...
```

**订阅者类型：**
```
PipelineEventBus.subscribe(tui_log_handler)   # LogStream 实时写入
PipelineEventBus.subscribe(mcp_notify_handler) # MCP notification 推送
PipelineEventBus.subscribe(state_machine_handler) # PipelineStateMachine 状态更新
```

---

### Module 4: `tui/pipeline_integration.py` — TUI 与管道集成层

**职责：** 在 `ToVibeApp.on_mount()` 中初始化并连接所有模块，作为 wiring layer。

```python
# src/to_vibe/tui/pipeline_integration.py

class PipelineIntegration:
    """连接 TUI 与 Pipeline 的 wiring 类。"""

    def __init__(self, app: ToVibeApp, project_path: Path) -> None:
        self.app = app
        self.project_path = project_path

        # 1. 初始化事件总线
        self._setup_event_bus()

        # 2. 初始化状态机 + 绑定 TUI store
        self.state_machine = PipelineStateMachine()
        self.state_store = TUIStateStore()
        self.state_store.bind_pipeline(self.state_machine)

        # 3. 启动管道 Worker（异步）
        self._worker_task: asyncio.Task | None = None

    def _setup_event_bus(self) -> None:
        from to_vibe.tui.components.log_stream import LogStreamHandler
        from to_vibe.mcp.server import get_server

        # LogStream handler
        PipelineEventBus.subscribe(LogStreamHandler())

        # MCP notification handler
        PipelineEventBus.subscribe(lambda e: get_server().send_notification(e))

    def start(self) -> None:
        """启动管道（不阻塞 TUI 主线程）。"""
        import asyncio
        self._worker_task = asyncio.create_task(self._run_pipeline())

    async def _run_pipeline(self) -> None:
        """异步运行管道，通过事件总线实时推送状态。"""
        ctx = await self.state_machine.run_async(self.project_path)
        PipelineEventBus.emit(PipelineEvent(
            timestamp=datetime.now().strftime("%H:%M:%S"),
            level="INFO",
            stage="complete",
            message=f"Pipeline done: {ctx.stages_completed}",
        ))

    def pause(self) -> None:
        self.state_machine.pause()

    def resume(self) -> None:
        self.state_machine.resume()

    def retry(self, stage: PipelineStage) -> None:
        """重试指定阶段。"""
        ...
```

**在 `app.py` 中的集成：**
```python
def on_mount(self) -> None:
    self.push_screen(MainScreen())

    # 启动管道集成
    self.integration = PipelineIntegration(
        app=self,
        project_path=self.project_path,
    )
    self.integration.start()
```

---

### Module 5: `mcp/notification_handler.py` — MCP Notification 处理器

**职责：** 将 PipelineEventBus 的事件转换为 MCP 协议格式，推送给 Claude Code。

```python
class MCPNotificationHandler:
    """将管道事件转换为 MCP notification 并发送。"""

    def __init__(self, mcp_server: MCPServer) -> None:
        self.server = mcp_server

    def __call__(self, event: PipelineEvent) -> None:
        notification_type_map = {
            "INFO": NotificationType.LOG,
            "WARN": NotificationType.WARNING,
            "ERROR": NotificationType.ERROR,
        }

        # 构建 MCP notification payload
        payload = {
            "timestamp": event.timestamp,
            "level": event.level,
            "stage": event.stage,
            "message": event.message,
            "data": event.data,
        }

        n_type = notification_type_map.get(event.level, NotificationType.LOG)

        self.server.send_notification(
            notification_type=n_type,
            payload=payload,
        )
```

---

### Module 6: `chat/chat_integration.py` — Chat 与管道的对话集成

**职责：** ChatPanel 的 `_stream_response` 需要能够：
1. 访问当前 PipelineContext（知道项目状态）
2. 将 pipeline 结果注入到 LLM prompt 中
3. 支持中断/继续

```python
class ChatIntegration:
    """ChatPanel 与 Pipeline 的对话集成。"""

    def __init__(self, state_store: TUIStateStore) -> None:
        self.state_store = state_store

    async def stream_response(self, user_message: str) -> str:
        """构建带上下文的 prompt 并流式返回。"""

        # 构建上下文摘要
        context = self._build_pipeline_context()

        messages = [
            {"role": "system", "content": self._system_prompt(context)},
            *self._chat_history,
            {"role": "user", "content": user_message},
        ]

        client = get_client()
        if not client:
            return "LLM not configured"

        try:
            async for chunk in client.stream_complete(messages):
                yield chunk
        except Exception as e:
            yield f"Error: {e}"

    def _build_pipeline_context(self) -> dict:
        """从 state_store 获取当前 pipeline 状态摘要。"""
        return {
            "stage": self.state_store.current_stage,
            "progress": self.state_store.progress,
            "stages": self.state_store.stages_completed,
            "evidence": self.state_store.evidence_data,
            "priority": self.state_store.priority_data,
            "verify": self.state_store.verify_rows,
        }

    def _system_prompt(self, context: dict) -> str:
        return f"""你是 to-vibe 的助手。项目当前状态：
Stage: {context['stage']}
Progress: {context['progress']:.0%}
已完成阶段: {', '.join(context['stages']) or '无'}
Evidence: {context['evidence']}
Priority: {context['priority']}
"""
```

---

## 三、模块依赖关系

```
cli.py
  └── ToVibeApp.on_mount()
        └── PipelineIntegration (Module 4)
              ├── PipelineStateMachine (Module 1)
              │     └── PipelineEventBus (Module 3)
              │           ├── TUIStateStore (Module 2) → TUI 组件更新
              │           ├── MCPNotificationHandler (Module 5) → Claude Code
              │           └── LogStreamHandler (TUI)
              │
              ├── TUIStateStore (Module 2)
              │     └── Textual reactive → StageBar, EvidenceCard, PriorityCard,
              │         VerifyTable, LearnPanel, Artifacts, Footer
              │
              └── ChatIntegration (Module 6)
                    └── get_client() → LLM streaming response
```

---

## 四、实现顺序与优先级

| 优先级 | 模块 | 工作内容 | 依赖 |
|---|---|---|---|
| **P0** | Module 1: `state_machine.py` | 管道状态机，驱动 StageBar | 无 |
| **P1** | Module 3: `event_bus.py` | 事件总线，连接管道→TUI+MCP | 无 |
| **P2** | Module 2: `state_store.py` | TUI 响应式状态存储 | Module 1 |
| **P3** | Module 4: `pipeline_integration.py` | 管道+TUI wiring | Module 1, 2, 3 |
| **P4** | Module 5: `notification_handler.py` | MCP notification 推送 | Module 3 |
| **P5** | Module 6: `chat_integration.py` | Chat 带 pipeline 上下文流式对话 | Module 2 |

---

## 五、关键设计决策

### 1. 为什么用 `PipelineEventBus` 而不是直接回调？

事件总线解耦了管道和订阅者。管道不需要知道有多少订阅者（TUI、MCP、LogStream），新增订阅者只需 `PipelineEventBus.subscribe()` 而不修改管道代码。

### 2. 为什么 `TUIStateStore` 用 reactive 而不是直接修改组件？

Textual 的 `reactive` 属性在主线程上触发组件 `refresh()`，避免跨线程直接操作 Textual DOM（Textual 不是线程安全的）。所有 `PipelineStateMachine` 的回调必须通过 `call_later()` 进入 TUI 主线程。

### 3. Pipeline 在哪个线程运行？

- **TUI 主线程：** Textual 的事件循环（必须保持响应）
- **Pipeline Worker：** `asyncio.create_task()` 在 TUI 事件循环中并发运行，不阻塞 UI
- **状态同步：** Pipeline → EventBus → StateStore → UI（通过 `call_later()`）

### 4. 暂停/重试/跳过如何实现？

```
pause → PipelineStateMachine.PAUSED → PipelineWorker 检查状态并暂停
resume → PipelineStateMachine.IDLE → PipelineWorker 继续
retry → PipelineStateMachine.reset(stage) → 重新运行指定阶段
skip → PipelineStateMachine.set_skipped(stage) → 标记并跳到下一阶段
```

---

## 六、文件清单（新增 + 修改）

| 操作 | 文件路径 | 说明 |
|---|---|---|
| 新增 | `src/to_vibe/pipeline/state_machine.py` | 管道状态机 |
| 新增 | `src/to_vibe/pipeline/event_bus.py` | 事件总线 |
| 新增 | `src/to_vibe/tui/state_store.py` | TUI 响应式状态存储 |
| 新增 | `src/to_vibe/tui/pipeline_integration.py` | TUI 与管道 wiring |
| 新增 | `src/to_vibe/mcp/notification_handler.py` | MCP notification 处理器 |
| 新增 | `src/to_vibe/chat/chat_integration.py` | Chat 带上下文流式对话 |
| 修改 | `src/to_vibe/tui/app.py` | `on_mount()` 启动 PipelineIntegration |
| 修改 | `src/to_vibe/tui/components/stage_bar.py` | `@watch(store.current_stage)` 自动刷新 |
| 修改 | `src/to_vibe/tui/components/evidence_card.py` | 绑定 state_store.evidence_data |
| 修改 | `src/to_vibe/tui/components/priority_card.py` | 绑定 state_store.priority_data |
| 修改 | `src/to_vibe/tui/components/verify_table.py` | 绑定 state_store.verify_rows |
| 修改 | `src/to_vibe/tui/components/log_stream.py` | 实现 `LogStreamHandler` 接口 |
| 修改 | `src/to_vibe/tui/components/learn_panel.py` | 绑定 state_store.learn_data |
| 修改 | `src/to_vibe/tui/components/artifacts.py` | 绑定 state_store.evidence_data |
| 修改 | `src/to_vibe/tui/screens/chat_panel.py` | 替换 `_stream_response` 为 ChatIntegration |
| 修改 | `src/to_vibe/cli.py` | `run` 命令使用 PipelineStateMachine 而非 run_pipeline() |