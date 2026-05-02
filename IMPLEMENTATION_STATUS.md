# Implementation Status — to-vibe-cli

## Module Overview

| # | Module | Status | Depth | Notes |
|---|--------|--------|-------|-------|
| | **config** | | | |
| 1 | `src/to_vibe/config.py` | ✅ done | deep | LLMConfig, resolved_endpoint() delegates to protocol |
| | **CLI** | | | |
| 2 | `src/to_vibe/cli.py` | ✅ done | shallow | ArgumentParser, 3 commands: run/loop/learn |
| 3 | `src/to_vibe/app.py` | ✅ done | shallow | Orchestrates Pipeline + TUI |
| 4 | `src/to_vibe/main.py` | ✅ done | shallow | entry point |
| | **LLM** | | | |
| 5 | `src/to_vibe/llm/client.py` | ✅ done | deep | HTTP client with protocol abstraction |
| 6 | `src/to_vibe/llm/protocol.py` | ✅ done | deep | LLMProtocol ABC + AnthropicProtocol + OpenAICompatibleProtocol |
| 7 | `src/to_vibe/llm/request.py` | ✅ done | shallow | LLMRequest dataclass |
| | **pipeline** | | | |
| 8 | `src/to_vibe/pipeline/orchestrator.py` | ⚠️ stub | shallow | P0-P4 stages wired; learn not wired |
| 9 | `src/to_vibe/pipeline/state_machine.py` | ✅ done | shallow | PipelineStateMachine ABC |
| 10 | `src/to_vibe/pipeline/control.py` | ✅ done | shallow | PipelineControlPort ABC |
| 11 | `src/to_vibe/pipeline/control_adapter.py` | ✅ done | shallow | StateMachineControlAdapter |
| | **pipeline workers** | | | |
| 12 | `src/to_vibe/pipeline/evidence_ledger.py` | ✅ done | shallow | Evidence collector, JSON output |
| 13 | `src/to_vibe/pipeline/priority_report.py` | ✅ done | shallow | Priority report, JSON output |
| 14 | `src/to_vibe/pipeline/baseline_verify.py` | ✅ done | shallow | Baseline verifier, JSON output |
| 15 | `src/to_vibe/pipeline/repair_loop.py` | ✅ done | shallow | Repair loop with candidates |
| | **runtime** | | | |
| 16 | `src/to_vibe/runtime/events.py` | ✅ done | deep | PipelineEventBus singleton |
| 17 | `src/to_vibe/runtime/session.py` | ✅ done | shallow | Session persistence |
| 18 | `src/to_vibe/runtime/logger.py` | ✅ done | shallow | Logging setup |
| | **learn** | | | |
| 19 | `src/to_vibe/learn/learn.py` | ✅ done | shallow | Learn Orchestration |
| 20 | `src/to_vibe/learn/collector.py` | ⚠️ bug | shallow | Schema mismatch bugs |
| 21 | `src/to_vibe/learn/models.py` | ✅ done | deep | LearnData, LearnDetailView |
| 22 | `src/to_vibe/learn/storage.py` | ✅ done | deep | SQLite storage |
| | **MCP** | | | |
| 23 | `src/to_vibe/mcp/handler.py` | ✅ done | shallow | Fully implemented, delegates to PipelineControlPort |
| 24 | `src/to_vibe/mcp/protocol.py` | ⚠️ stub | shallow | — |
| | **TUI** | | | |
| 25 | `src/to_vibe/tui/app.py` | ⚠️ partial | shallow | Missing store injection |
| 26 | `src/to_vibe/tui/state_store.py` | ✅ done | deep | TUIStateStore with subscriber pattern |
| 27 | `src/to_vibe/tui/pipeline_integration.py` | ⚠️ partial | shallow | Not wired to state_store for all updates |
| 28 | `src/to_vibe/tui/styles.py` | ✅ done | shallow | All Colors match TUI_DESIGN.md |
| 29 | `src/to_vibe/tui/screens/main_screen.py` | ✅ done | shallow | Tab navigation, passes store to all panels |
| 30 | `src/to_vibe/tui/screens/chat_panel.py` | ⚠️ partial | shallow | ListView layout, NOT wired to TUIStateStore |
| 31 | `src/to_vibe/tui/screens/to_vibe_panel.py` | ✅ done | shallow | Bento Grid: 40% left \| 60% right |
| 32 | `src/to_vibe/tui/screens/logs_panel.py` | ✅ done | shallow | 3-column: LogStream(60%) \| Learn(20%) \| Artifacts(20%) |
| 33 | `src/to_vibe/tui/components/header.py` | ✅ done | shallow | brand + path + git + timer |
| 34 | `src/to_vibe/tui/components/stage_bar.py` | ✅ done | shallow | Stage indicators with colored icons |
| 35 | `src/to_vibe/tui/components/evidence_card.py` | ✅ done | shallow | Key-Value format, tech_stack list |
| 36 | `src/to_vibe/tui/components/priority_card.py` | ✅ done | shallow | Key-Value format, Suggested line |
| 37 | `src/to_vibe/tui/components/verify_table.py` | ✅ done | shallow | Table with emoji status icons |
| 38 | `src/to_vibe/tui/components/log_stream.py` | ✅ done | shallow | Colored log levels |
| 39 | `src/to_vibe/tui/components/learn_panel.py` | ✅ done | shallow | Summary + detail view, key-value format |
| 40 | `src/to_vibe/tui/components/artifacts.py` | ✅ done | shallow | Artifact list display |
| 41 | `src/to_vibe/tui/components/footer.py` | ✅ done | shallow | 3-section: path \| executor \| shortcuts |

---

## Implementation Details

### config
- `LLMConfig` dataclass: `provider`, `model`, `api_key`, `base_url`, `endpoint_path`, `extra_headers`
- `resolved_endpoint()` delegates to `to_vibe.llm.protocol.get_protocol(protocol).default_endpoint_path()`

### CLI / App
- 3 commands: `run <path>`, `loop <path>`, `learn`
- `app.py` wires Pipeline + TUI + MCP notification handler

### LLM Layer
- `protocol.py` separates HTTP envelope (client.py) from protocol logic
- `LLMProtocol` ABC: `name`, `default_endpoint_path()`, `headers()`, `build_request()`, `extract_content()`, `extract_chunk()`
- `get_protocol(name)` registry; `register_protocol()` for extension
- Currently registered: `anthropic` (AnthropicProtocol), `openai` (OpenAICompatibleProtocol), `custom` (OpenAICompatibleProtocol)

### Pipeline Orchestration
- 5 stages: Evidence → Priority → Verify → Repair → Learn
- Event bus pub/sub for stage transitions
- Control port: `run/pause/resume/retry/skip/learn/snapshot`

### Pipeline Workers (JSON artifact schemas)

**evidence_ledger.json**
```json
{
  "evidence": { "tech_stack": ["str"], "files_scanned": 0, "ignored_dirs": ["str"], "output_path": "str" }
}
```
Schema mismatch: `learn/collector.py` reads `stack` (str) but schema has `tech_stack` (list)

**priority_report.json**
```json
{
  "priority": { "suggested_capability": "str", "current_complexity": "str", "estimated_effort": "str", "blockers": ["str"] }
}
```
Schema mismatch: `learn/collector.py` reads `blockers` as list vs `priority_report.py` outputs list (OK), but collector reads `layers` dict but schema has `layer_results` list

**baseline_verify.json**
```json
{
  "verify": {
    "checks": [
      { "id": 0, "check": "str", "status": "pass|fail|skip", "details": "str" }
    ]
  }
}
```

### TUI Component Pattern
```python
class X(Static):
    def __init__(self, store: TUIStateStore, **kwargs):
        super().__init__(**kwargs)
        self._store = store
        self._unsubscribe: callable | None = None

    def on_mount(self):
        self._unsubscribe = self._store.subscribe("key", self._on_key)
        self._update_display()

    def on_unmount(self):
        if self._unsubscribe:
            self._unsubscribe()

    def _on_key(self, data):
        self.app.call_from_thread(self.set_data, data)
```

---

## Test Coverage

| Test | File | What's Covered |
|------|------|---------------|
| test_config_loading | `tests/test_config.py` | yaml loading, provider default, resolved_endpoint |
| test_evidence_card | `tests/test_components.py` | EvidenceData dataclass, key-value rendering |
| test_priority_card | `tests/test_components.py` | PriorityData, Suggested line |
| test_verify_table | `tests/test_components.py` | VerifyRow, emoji status icons |
| test_stage_bar | `tests/test_components.py` | StageState, icon rendering |
| test_learn_panel | `tests/test_components.py` | LearnData, summary rendering |
| test_log_stream | `tests/test_components.py` | LogLevel coloring |
| test_e2e | `tests/test_e2e.py` | Full pipeline run, JSON artifact creation |

**Not covered:** ChatPanel, Header, Artifacts, Footer, TabBar, MCP handler, orchestrator wired learn stage

---

## Known Bugs

### HIGH (block pipeline correctness)
| # | File | Issue | Impact |
|---|------|-------|--------|
| H1 | `orchestrator.py:185` | `LearnCollector` undefined — should be `LegacyLearnCollector` | Pipeline crashes on learn stage |
| H2 | `learn/collector.py:evidence` | Reads `stack: str` but EvidenceData has `tech_stack: list[str]` | Learn stage gets empty tech_stack |
| H3 | `learn/collector.py:priority` | Reads `layers` dict but priority_report.json has `layer_results` list | Learn stage can't parse priority data |

### MEDIUM (runtime / wiring issues)
| # | File | Issue | Impact |
|---|------|-------|--------|
| M1 | `pipeline_integration.py` | `update_evidence(ignored=...)` but EvidenceData field is `ignored_dirs` | Evidence update silently ignored |
| M2 | `tui/app.py` | `MainScreen(store=...)` not called; store not injected into screen | TUI components get no data |
| M3 | `tui/screens/chat_panel.py` | ChatPanel not wired to TUIStateStore; owns `_messages` list independently | Chat history isolated from state |
| M4 | `mcp/handler.py` | `init_server()` never called, `install_mcp_notification_handler()` never called | MCP server dead code |
| M5 | `main_screen.py` | TabBar is a plain class, not a Textual Widget — no visual rendering | Tab bar invisible |

### LOW (cosmetic / minor)
| # | File | Issue |
|---|------|-------|
| L1 | `tui/components/learn_panel.py` | Still has emoji (📌, ✅, ⏳) mixed with Textual markup |
| L2 | `mcp/protocol.py` | Stub — no real MCP server protocol implementation |

---

## Data Validation

| Data Type | Source | Format | TUI Refresh |
|-----------|--------|--------|------------|
| Evidence | `evidence_ledger.json` | JSON | PipelineEventBus → state_store |
| Priority | `priority_report.json` | JSON | PipelineEventBus → state_store |
| Verify | `baseline_verify.json` | JSON | PipelineEventBus → state_store |
| Learn | SQLite `learn.db` | SQL | PipelineEventBus → state_store |
| Logs | PipelineEventBus stream | in-memory | push to log_stream component |
| Artifacts | `artifacts/` dir | file list | directory scan on stage change |
| Session | `~/.to-vibe/session.json` | JSON | on_load in state_store |

---

## Architecture Depth (Deletion Test)

**Deep modules** — deleting would concentrate complexity elsewhere:
- `event_bus` — all pipeline comms would need rewiring
- `state_store` — all TUI components would lose data
- `pipeline_integration` — TUI loses pipeline visibility
- `llm/client` + `llm/protocol` — all LLM calls go through here
- `learn/storage` — all learn persistence
- `learn/collector` — all learn data aggregation

**Shallow modules** — can delete with localized impact:
- `orchestrator` — just coordinates, no deep state
- `state_machine` — well-defined interface
- `mcp/handler` — MCP notifications are optional
- `mcp/protocol` — stub, unused