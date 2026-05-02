# CLAUDE.md

to-vibe-cli 的目标是把 vibe coding 输出压实为可验证、可恢复、可修复的工程流程,做成可视化 cli。

因此，当用户指出 pipeline、handler、TUI、Learn、Repair、Verify、Evidence、Priority、Baseline 等模块的问题时，你必须直接进入实现模式。

## 默认模块决策

- MCP handler 问题：优先查看 src/to_vibe/mcp/
- pipeline 问题：优先查看 src/to_vibe/pipeline/
- learn 问题：优先查看 src/to_vibe/learn/
- repair 问题：优先查看 src/to_vibe/repair/
- verify 问题：优先查看 src/to_vibe/verify/
- TUI 问题：优先查看 src/to_vibe/tui/ 或 src/to_vibe/ui/
- CLI 命令问题：优先查看 src/to_vibe/cli/

## 默认行为

- 已有 pipeline 未接线：直接接线；
- handler 只是 mock：替换为真实 pipeline 调用；
- UI 有占位但无数据：接入真实状态模型；
- Learn 状态存在但详情缺失：实现详情展开视图；
- log filter 缺失：实现 INFO/WARN/ERROR 过滤；
- artifacts 列表缺失：接入产物路径；
- import 错误：直接修复；
- 类型定义不一致：统一模型定义；
- 状态字段缺失：补齐 typed model。

不要询问用户这些内部实现细节。

## Project Overview

to-vibe is an AI-powered code engineering TUI tool that transforms vibe-coding outputs into maintainable engineering assets. It runs a multi-stage pipeline (Evidence → Priority → Verify → Repair → Learn) and provides real-time progress visualization via a Textual TUI.

## Commands

```bash
# Install
pip install -e .

# Run the pipeline + TUI
to-vibe run ./project

# Run standalone learn (from artifacts)
to-vibe learn

# Run tests
python -m pytest tests/ -v
python -m pytest tests/test_tui_wiring.py -v          # TUI wiring only
python -m pytest tests/test_tui_wiring.py -k test_repair  # Single test

# Type check
python -m mypy src/to_vibe/

# Lint
python -m ruff check src/to_vibe/
```

## Architecture

```
to_vibe/
├── cli.py              # Click CLI entry — `run` (TUI) and `learn` commands
├── config.py           # to-vibe.yaml loader + dataclasses (ToVibeConfig)
├── tui/
│   ├── app.py          # ToVibeApp — Textual App, CSS, BINDINGS (Space/R/S shortcuts)
│   ├── state_store.py  # TUIStateStore — central reactive bus, subscribe(key, cb) → unsubscribe fn
│   ├── state_models.py # All dataclass models (EvidenceData, PriorityData, VerifyRow, RepairData, LearnData, etc.)
│   ├── pipeline_integration.py  # PipelineIntegration — wires pipeline events → store updates
│   ├── styles.py       # Colors enum (STAGE_EVIDENCE, STAGE_REPAIR, etc.)
│   ├── components/     # Individual widgets: header, footer, stage_bar, evidence_card, priority_card, verify_table, log_stream, artifacts, repair_panel, learn_panel
│   └── screens/        # main_screen (TabBar + 3 panels), chat_panel, to_vibe_panel, logs_panel
├── pipeline/
│   ├── orchestrator.py # run_pipeline() — top-level async pipeline runner
│   ├── state_machine.py # PipelineStateMachine — stage state + transitions
│   ├── control.py      # PipelineControlPort, SkipPolicy — pause/retry/skip/can_skip
│   ├── event_bus.py   # PipelineEventBus singleton + subscribe()
│   ├── evidence_ledger.py  # Evidence collector — scans project files
│   ├── priority_report.py  # Priority analyzer
│   ├── baseline_verify.py  # Verify checks (Environment, Dependencies, Build, Start, Smoke)
│   └── repair_loop.py  # Repair loop executor
├── mcp/
│   ├── server.py       # MCP server (stdio)
│   ├── protocol.py     # MCP request/response types
│   ├── notification_handler.py  # MCP tool notifications → pipeline events
│   └── handler.py      # MCP handler routing to PipelineControlPort
├── learn/
│   ├── learn.py        # MainLearnCollector — orchestrates learning
│   └── collector.py    # LegacyLearnCollector — reads artifacts, produces LearnResult
└── llm/
    └── client.py       # LLM client (Anthropic-compatible)
```

## Key Patterns

- **TUIStateStore** is the single source of truth for all UI state. Components subscribe with `store.subscribe("key", callback)` and receive unsubscribe functions. Updates from pipeline thread use `app.call_from_thread()`.
- **State models** (`state_models.py`) are the unified dataclass definitions used by both the store and pipeline integration. Field names must be consistent: `ignored_dirs`, `suggested_capability`, `apply`, `record`, `is_directory` (not the old variants).
- **PipelineIntegration** accepts a `TUIStateStore` in `__init__` (not its own store). It wires pipeline events → store updates and provides `pause()` / `retry()` / `skip()` methods called by TUI shortcuts.
- **Component widget hierarchy**: Only `Container` subclasses (Horizontal, Vertical, Grid) can yield children. Static/Widget subclasses cannot. Use `Widget` for leaf widgets and `Container` for composing children.
- **Textual CSS**: All styling lives in `app.py` CSS string. Use `:root` variables for colors. IDs (#evidence-card, #repair-panel) target specific widgets.
- **LogStream filter**: `set_filter(level)` filters log entries by level; `clear()` empties the buffer. Filter buttons [all/info/warn/error/Clear] are composed inside the widget.

## Design Reference

TUI layout specification: `TUI_DESIGN.md`
Data model specification: `TUI_DATA_SPEC.md`
