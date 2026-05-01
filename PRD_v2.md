# to-vibe CLI PRD — AI 代码工程化 TUI 工具

## 1. Problem Statement

AI 辅助编程（Vibe Coding）能快速生成完整系统，但输出物充满工程化债务：能跑但不敢动、报错多不知先修哪个、代码多不知哪个有用。开发者需要花费大量时间在"修 bug 循环"里，无法专注于真正有价值的开发工作。

现有工具链缺乏：
- **事实锚定**：AI 凭记忆判断项目技术栈，导致误判
- **优先级引导**：问题清单无主次，开发者无从下手
- **验证闭环**：修复后没有系统化验证，不知道是否真正解决
- **经验积累**：重复踩坑，没有从修复历史中学习

## 2. Solution

to-vibe 是 **AI 代码生成后的项目工程化 CLI 工具**，通过"长链工程推理 + 分阶段验证 + 条件修复循环"将 vibe coding 产物转化为可维护工程资产。

用户只需要执行 `to-vibe run ./project`，工具自动完成：
1. 扫描项目文件，建立事实账本（Evidence Ledger）
2. 自动分析问题，生成优先级报告（Priority Report）
3. 5 层验证体系确保修复可验证（Baseline Verify）
4. 按优先级逐个修复问题（Repair Loop）
5. 从修复中学习，积累项目专属经验（Learn）

## 3. User Stories

### 3.1 初始化与配置

1. As a developer, I want to run `to-vibe run ./project` to start the engineering pipeline, so that I don't need to understand the internal flow
2. As a developer, I want to configure LLM provider (Anthropic/OpenAI API compatible) in `to-vibe.yaml`, so that I can use my own API keys
3. As a developer, I want to configure pipeline mode (dry-run/live) in `to-vibe.yaml`, so that I can test without making actual changes
4. As a developer, I want to see the current session status (project path, git branch, timer) in the header, so that I know what I'm working on
5. As a developer, I want to see the current execution command in the UI, so that I know what was last run

### 3.2 Pipeline 阶段管理

6. As a developer, I want to see 5-stage pipeline status (Evidence → Priority → Verify → Repair → Learn) as a chevron bar, so that I can track overall progress
7. As a developer, I want each stage to show status (completed/active/failed/skipped/pending) with distinct colors, so that I can quickly identify bottlenecks
8. As a developer, I want the pipeline to pause at `action_required` points, so that I can review and choose next action (continue/retry/skip)
9. As a developer, I want to press `Space` to pause the current flow, so that I can inspect state without losing context
10. As a developer, I want to press `R` to retry the failed step (Repair Loop re-does current step, Verify re-runs failed layer), so that I can attempt recovery
11. As a developer, I want to press `S` to skip the current stage, so that I can bypass known issues and continue
12. As a developer, I want to press `Tab` to switch between 3 views (Chat / to-vibe / Logs), so that I can navigate the interface efficiently

### 3.3 Evidence Ledger

13. As a developer, I want to see the Evidence Ledger card showing detected tech stack (e.g., Spring Boot + Thymeleaf + MySQL), so that I understand what the tool believes about the project
14. As a developer, I want to see files scanned count and ignored directories, so that I know the scan scope
15. As a developer, I want the output path to be shown (`.to-vibe/evidence-ledger.json`), so that I can manually inspect the artifact
16. As a developer, I want each fact to have evidence references (file path + line number), so that I can verify the tool's conclusions
17. As a developer, I want facts to be categorized (package_manager, framework, entry_point, dependency), so that I can understand the nature of each finding

### 3.4 Priority Report

18. As a developer, I want to see problem counts categorized by priority (Blockers/P0, High/P1, Medium/P2), so that I know the severity distribution
19. As a developer, I want to see the top issue description, so that I know what to focus on first
20. As a developer, I want to see suggested capability (Debug/Refactor/System/Simplify), so that I know which sub-system to use for fixing
21. As a developer, I want the priority report to be a ranked roadmap (not just a list), so that I can follow a clear action sequence

### 3.5 Baseline Verify

22. As a developer, I want to see 5-layer verification table (L1 Environment, L2 Dependencies, L3 Build, L4 Start, L5 Smoke Test), so that I understand what has been checked
23. As a developer, I want each row to show status icon (✅ pass / ❌ fail / ⊘ skip) and the actual command executed, so that I can reproduce the check
24. As a developer, I want L3 (Build) failure to block L4/L5 from running, so that I don't waste time on higher layers when fundamentals fail
25. As a developer, I want each layer to support configurable max retries (default 3), so that transient failures don't immediately fail the whole pipeline
26. As a developer, I want failed layers to show the command output (stdout/stderr), so that I can diagnose the failure cause

### 3.6 Repair Loop

27. As a developer, I want the Repair Loop to follow Select → Plan → Apply → Verify → Record cycle, so that each fix is systematic
28. As a developer, I want 4 sub-capabilities (Debug for bugs, Refactor for structure, System for architecture, Simplify for complexity), so that the right tool is used for each issue type
29. As a developer, I want to see the selected issue, capability, and current mode (dry-run/live), so that I understand what the loop is doing
30. As a developer, I want to see iteration count and next action hint, so that I can predict what will happen next
31. As a developer, I want exit conditions (Stabilized P0 fixed / Maintainable P0+P1 fixed / Ship-ready all fixed), so that I know when the loop will terminate

### 3.7 Learn Module

32. As a developer, I want the Learn panel to show 4 types of memory (Project Fact / Verified Fix / Issue Pattern / User Confirmed Rule), so that I understand what knowledge is being captured
33. As a developer, I want to see Status (pending/completed), Records count, Focus area, and Source, so that I know the learning state
34. As a developer, I want to click `[详情]` to expand the full Learning Details view, so that I can audit what has been learned
35. As a developer, I want the Learning Details view to show Verified Fixes with root cause and verify status, so that I can review past fixes
36. As a developer, I want the Learning Details view to show Issue Patterns with signals and recommended actions, so that I can learn from recurring problems
37. As a developer, I want the Learning Details view to show Project Facts with evidence references, so that I can verify the tool's understanding
38. As a developer, I want the Learning Details view to show User Rules (highest priority), so that I can see my explicit preferences are captured
39. As a developer, I want to press `[A]` to accept a pending rule, `[R]` to reject it, `[E]` to edit it, `[P]` to pin it, `[D]` to delete it, so that I can manage learned content
40. As a developer, I want to press `Esc` to return from detail view to main view, so that I can navigate back
41. As a developer, I want Learn to trigger automatically on pipeline completion (not during Repair Loop), so that I get fresh learnings at the end
42. As a developer, I want to manually trigger Learn via `to-vibe learn` command, so that I can get learnings without running the full pipeline
43. As a developer, I want Learn to collect candidates from repair-loop.json, baseline-verify.json, priority-report.json, so that all sources contribute
44. As a developer, I want Learn to filter out unverified, evidence-lacking, and cross-project unsafe content, so that only reliable knowledge is stored
45. As a developer, I want learned content to be stored in 3 layers: `.to-vibe/learn/` (human-readable), SQLite L0 (structured query), L1 vector (semantic retrieval), so that I can access it in multiple ways

### 3.8 Log Stream & Artifacts

46. As a developer, I want to see real-time log stream with timestamp + level + text, so that I can track what happened when
47. As a developer, I want to filter logs by level: `[info]`, `[error]`, `[warning]` buttons, so that I can focus on specific severity
48. As a developer, I want to press `[Clear]` to clear the log display, so that I can start fresh
49. As a developer, I want the log to auto-scroll to bottom as new entries appear, so that I can see the latest output
50. As a developer, I want to use `↑`/`↓` keys to scroll through log history when not at the bottom, so that I can review past logs
51. As a developer, I want to see Artifacts panel listing generated files (evidence-ledger.json, priority-report.md, baseline-verify.json, repair-plan.md, claude-tasks/), so that I know what has been produced
52. As a developer, I want directories (like claude-tasks/) to show with 📁 icon and files with ·, so that I can distinguish file types

### 3.9 LLM Chat Panel

53. As a developer, I want a Chat panel on the left tab where I can type messages to a configurable LLM, so that I can get help while working on the project
54. As a developer, I want the LLM to be configured via `to-vibe.yaml` (provider, api_key, model, base_url, max_tokens, timeout), so that I control which model I use
55. As a developer, I want to send messages with `Enter` and cancel with `Ctrl+C`, so that I can interact naturally
56. As a developer, I want to see streaming responses appear in real-time, so that I don't wait for the full reply
57. As a developer, I want to scroll through conversation history, so that I can reference past exchanges
58. As a developer, I want the Chat panel to support both Anthropic API and OpenAI API compatible endpoints, so that I can use whichever model I prefer

### 3.10 Footer & Shortcuts

59. As a developer, I want to see Executor info and sync icon in the footer, so that I know the connection state
60. As a developer, I want to see keyboard shortcut hints ([Space]暂停 [R]重试 [S]跳过 [↑↓]滚动) at the bottom, so that I know what controls are available

## 4. Implementation Decisions

### 4.1 Technology Stack

- **Language**: Python 3.11+
- **TUI Framework**: Python Textual (pure Python, complex terminal layout support)
- **LLM Integration**: Anthropic API compatible + OpenAI API compatible
- **Configuration**: `to-vibe.yaml` in project root
- **Session State**: `session-start.json`
- **Artifact Storage**: `.to-vibe/` directory (human-readable)

### 4.2 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Python Textual TUI                       │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────┐  ┌────────────────────────────────┐ │
│  │   LLM Chat Panel  │  │         to-vibe Pipeline         │ │
│  │   (Tab 1: chat)   │  │         (Tab 2: to-vibe)         │ │
│  │  [Conversation]   │  │  StageBar: Evidence→Priority→   │ │
│  │  [Input Field]   │  │  Verify→Repair→Learn             │ │
│  │                   │  │                                 │ │
│  │                   │  │  EvidenceCard │ VerifyTable    │ │
│  │                   │  │  PriorityCard │ LearnPanel     │ │
│  │                   │  │  LogStream    │ Artifacts      │ │
│  └───────────────────┘  └────────────────────────────────┘ │
│                                                             │
│                    Single Process + Internal Queue          │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 UI Layout

- **3-Tab Bento Grid**: Chat (Tab 1) / to-vibe pipeline (Tab 2) / Logs (Tab 3)
- **Header**: brand icon + path + git branch + timer
- **StageBar**: 5 chevron indicators with color-coded borders (green completed, orange active, red failed, grey skipped)
- **Right Panel**: EvidenceCard (green) + PriorityCard (orange) on left, VerifyTable (red) + LearnPanel (purple) on right
- **Bottom**: LogStream with level filters + Artifacts sidebar
- **Footer**: Executor info + keyboard shortcut hints

### 4.4 Component Data Structures

Each UI component has a dataclass defining its fields:
- `StageBar`: id, label, status, chevron_icon, border_color
- `EvidenceCard`: stack, files_scanned, ignored_dirs, output_path, border_color, icon
- `PriorityCard`: blockers, high, medium, top_issue, suggested_capability, border_color, icon
- `VerifyTable`: rows list of (id, check, status, command, icon)
- `LearnPanel`: status, records, focus, source, detail_button
- `LogEntry`: timestamp, level, text
- `Artifact`: name, is_directory, icon

### 4.5 MCP Protocol

Notifications flow from to-vibe server to client (Claude Code):
- `log`: {text, level, timestamp}
- `stage_start`: {stage, description}
- `stage_complete`: {stage, summary, results}
- `progress`: {current, total, detail}
- `evidence`: {file, line, fact, status}
- `issue_found`: {priority, type, description}
- `action_required`: {prompt, options[], default}
- `error`: {stage, message, recovery}

Invoke flows from client to to-vibe:
- `to-vibe.run`: start full pipeline
- `to-vibe.pause`: pause current flow
- `to-vibe.retry`: retry failed step
- `to-vibe.skip`: skip current stage

### 4.6 Learn Module Details

**4 Memory Types**:
- `project_fact`: Project technical stack facts (medium priority)
- `verified_fix`: Verified repair experiences (high priority)
- `issue_pattern`: Problem signal → recommended action mapping (medium priority)
- `user_confirmed_rule`: Explicit user preferences (highest priority)

**7-Step Process**: Collect → Filter → Summarize → Validate → Review → Store → Retrieve

**Storage Layers**:
- `.to-vibe/learn/` (human-readable): learn-summary.md, learned-rules.json, verified-fixes.json, issue-patterns.json, rejected-lessons.json
- SQLite L0: structured query (learn_records table)
- L1 vector: semantic similarity retrieval (future)

### 4.7 Configuration Schema

```yaml
version: "2.0"
llm:
  provider: "anthropic"  # or "openai"
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
    exclude_patterns: [...]
  verify:
    layers:
      L1: {enabled: true, max_retries: 3}
      L2: {enabled: true, max_retries: 3}
      L3: {enabled: true, max_retries: 3}
      L4: {enabled: true, max_retries: 2}
      L5: {enabled: true, max_retries: 1}
session:
  heartbeat_interval_seconds: 30
  ttl_seconds: 300
  recovery_policy: "auto"
learn:
  trigger: "on_complete"
  min_confidence: 0.5
  max_records: 1000
  retention_days: 180
ui:
  log_levels: ["info", "error", "warning"]
  auto_scroll: true
```

### 4.8 File Structure

```
src/
  cli.py                    # CLI entry point
  config.py                 # to-vibe.yaml parsing
  tui/
    app.py                 # Textual App
    screens/
      main_screen.py       # 3 Tab container
      chat_panel.py        # Tab 1: LLM Chat
      to_vibe_panel.py     # Tab 2: Pipeline
      logs_panel.py        # Tab 3: Logs
    components/
      header.py, stage_bar.py, evidence_card.py
      priority_card.py, verify_table.py, learn_panel.py
      log_stream.py, artifacts.py, footer.py
    styles.py
  mcp/
    server.py, protocol.py, handler.py
  llm/
    client.py, anthropic.py, openai.py
  pipeline/
    evidence_ledger.py, priority_report.py
    baseline_verify.py, repair_loop.py, learn.py
  learn/
    collector.py, filter.py, summarizer.py
    validator.py, reviewer.py, storage.py
  storage/
    sqlite.py, artifacts.py
  utils/
    logger.py, locks.py
```

## 5. Testing Decisions

### 5.1 Test Strategy

- **Unit tests** for pure functions (config parsing, data transformations, filters)
- **Integration tests** for pipeline stages (scan a real project, verify output)
- **Component tests** for UI components (verify correct data renders in each component)
- **E2E tests** for full pipeline run

### 5.2 Testable Modules

Deep modules that can be tested in isolation:
- `config.py`: Test YAML parsing, env variable substitution, validation
- `pipeline/evidence_ledger.py`: Test project type detection, fact extraction with mock file system
- `pipeline/priority_report.py`: Test issue prioritization algorithm
- `pipeline/baseline_verify.py`: Test L1-L5 layer execution with mocked commands
- `learn/storage.py`: Test CRUD operations on SQLite
- `mcp/protocol.py`: Test notification serialization/deserialization
- UI components: Test data structure → rendered output mapping

### 5.3 Test Principles

- Only test external behavior, not implementation details
- Use temporary directories for file system tests
- Mock external commands (git, npm, mvn) for reproducibility
- Test the 4 Learn memory types with their specific validation rules

## 6. Out of Scope

- Ship module (removed per user decision — not needed for current requirements)
- Vector/semantic retrieval (L1 layer — deferred to future)
- Multi-user / collaborative features
- VS Code extension
- Web UI (only terminal TUI)

## 7. Further Notes

- Ship and Learn are connected: Learn collects artifacts from all previous stages. Ship was removed from the pipeline, so Learn collects from: Evidence Ledger, Priority Report, Baseline Verify, Repair Loop
- The "Bento Box" layout with Claude Code chat on the left and to-vibe on the right is inspired by image.png reference design
- All shortcuts (Space/R/S/↑↓/Tab/Esc) operate on the TUI focus context, not external OS
- The 5-stage pipeline chevron bar shows all stages at once, not just current — this allows users to see the whole journey