# to-vibe 技术规格文档

> AI 代码生成后的项目工程化平台 - 技术实现规格
>
> 版本：v2.0
> 日期：2026-04-30

---

## 1. 系统概览

### 1.1 架构原则

- **Evidence Ledger 为主**：所有判断基于文件系统事实，无证据不结论
- **SQLite 为主存**：元数据、索引、状态以 SQLite 为权威存储
- **Milvus 为向量副本**：仅用于语义检索加速，不是主存储
- **Baseline Verify 5层**：系统化验证项目基础能力
- **Repair Loop**：Select → Plan → Apply → Verify → Record 修复循环

---

## 2. 项目结构

```
to-vibe/
├── src/
│   ├── __init__.py
│   ├── cli.py                    # CLI 入口 (Click)
│   ├── evidence_ledger/          # Evidence Ledger 模块
│   │   ├── __init__.py
│   │   ├── scanner.py           # 项目文件扫描器
│   │   ├── fact_extractor.py     # 事实提取器
│   │   └── ledger_store.py       # 账本存储
│   ├── priority_report/          # Priority Report 模块
│   │   ├── __init__.py
│   │   ├── analyzer.py          # 问题分析器
│   │   ├── prioritizer.py       # 优先级排序
│   │   └── report_generator.py  # 报告生成器
│   ├── baseline_verify/          # Baseline Verify 模块
│   │   ├── __init__.py
│   │   ├── l1_env_check.py      # L1 环境识别
│   │   ├── l2_dep_check.py      # L2 依赖检查
│   │   ├── l3_build_check.py     # L3 构建检查
│   │   ├── l4_startup_check.py  # L4 启动检查
│   │   └── l5_smoke_test.py     # L5 Smoke Test
│   ├── repair_loop/              # Repair Loop 模块
│   │   ├── __init__.py
│   │   ├── issue_selector.py     # 问题选择器
│   │   ├── patch_planner.py     # 补丁规划器
│   │   ├── patch_applier.py     # 补丁应用器
│   │   ├── verifier.py           # 修复验证器
│   │   ├── debug.py             # Debug 子能力
│   │   ├── refactor.py          # Refactor 子能力
│   │   ├── system.py            # System 子能力
│   │   └── simplify.py           # Simplify 子能力
│   ├── memory/                   # Memory 系统
│   │   ├── __init__.py
│   │   ├── storage.py            # 文件系统操作
│   │   ├── sqlite_store.py       # SQLite 主存操作
│   │   ├── vector.py             # Milvus 接口
│   │   ├── retrieval.py          # 检索逻辑
│   │   └── hasher.py            # content_hash 计算
│   ├── ship/                    # Ship 模块
│   │   ├── __init__.py
│   │   └── ship_checker.py      # 发布检查器
│   ├── learn/                   # Learn 模块
│   │   ├── __init__.py
│   │   └── experience.py        # 经验提取
│   ├── hooks/                   # Hook 系统
│   │   ├── __init__.py
│   │   ├── trigger.py           # 触发器 (watchdog)
│   │   └── recovery.py          # 崩溃恢复 Hook
│   ├── api/                    # FastAPI 服务
│   │   ├── __init__.py
│   │   ├── app.py              # FastAPI 应用
│   │   ├── routes.py           # REST API 路由
│   │   └── websocket.py        # WebSocket 处理
│   └── utils/
│       ├── __init__.py
│       ├── config.py           # 配置加载
│       └── locks.py            # 文件锁工具
├── vscode-extension/            # VS Code 插件
│   ├── src/
│   │   └── extension.ts
│   └── package.json
├── tests/                       # 测试
├── pyproject.toml
└── README.md
```

---

## 3. 存储层规格

### 3.1 SQLite Schema

```sql
-- Evidence Ledger 记录
CREATE TABLE evidence_ledger (
    ledger_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    project_type TEXT,  -- node, python, rust, etc.
    created_at TEXT NOT NULL,
    confidence REAL DEFAULT 1.0,
    metadata TEXT  -- JSON for additional metadata
);

-- 事实记录
CREATE TABLE facts (
    fact_id TEXT PRIMARY KEY,
    ledger_id TEXT NOT NULL,
    fact_type TEXT NOT NULL,  -- package_manager, framework, entry_point, dependency, etc.
    content TEXT NOT NULL,
    file_path TEXT,
    line_start INTEGER,
    line_end INTEGER,
    snippet TEXT,  -- key code snippet
    confidence REAL DEFAULT 1.0,
    created_at TEXT NOT NULL,
    FOREIGN KEY (ledger_id) REFERENCES evidence_ledger(ledger_id)
);

-- Priority Report 记录
CREATE TABLE priority_reports (
    report_id TEXT PRIMARY KEY,
    ledger_id TEXT NOT NULL,
    project_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    report_content TEXT,  -- Markdown content
    p0_count INTEGER DEFAULT 0,
    p1_count INTEGER DEFAULT 0,
    p2_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'generated',  -- generated, in_progress, completed
    FOREIGN KEY (ledger_id) REFERENCES evidence_ledger(ledger_id)
);

-- Baseline Verify 记录
CREATE TABLE verify_runs (
    run_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    report_id TEXT,
    created_at TEXT NOT NULL,
    l1_status TEXT,  -- pass, fail, skip
    l1_details TEXT,
    l2_status TEXT,
    l2_details TEXT,
    l3_status TEXT,
    l3_details TEXT,
    l4_status TEXT,
    l4_details TEXT,
    l5_status TEXT,
    l5_details TEXT,
    overall_status TEXT,  -- pass, fail, partial
    FOREIGN KEY (report_id) REFERENCES priority_reports(report_id)
);

-- Repair Loop 记录
CREATE TABLE repair_runs (
    run_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    report_id TEXT,
    verify_run_id TEXT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    exit_level TEXT,  -- stabilized, maintainable, ship-ready, max_iterations
    p0_fixed INTEGER DEFAULT 0,
    p1_fixed INTEGER DEFAULT 0,
    p2_fixed INTEGER DEFAULT 0,
    p0_remaining INTEGER DEFAULT 0,
    p1_remaining INTEGER DEFAULT 0,
    p2_remaining INTEGER DEFAULT 0,
    status TEXT DEFAULT 'running',  -- running, completed, max_iterations_reached
    FOREIGN KEY (report_id) REFERENCES priority_reports(report_id),
    FOREIGN KEY (verify_run_id) REFERENCES verify_runs(run_id)
);

-- 修复历史
CREATE TABLE repair_history (
    repair_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    issue_type TEXT NOT NULL,  -- debug, refactor, system, simplify
    issue_description TEXT,
    patch_plan TEXT,
    patch_application TEXT,
    verification_result TEXT,  -- pass, fail, skip
    attempt_count INTEGER DEFAULT 1,
    created_at TEXT NOT NULL,
    FOREIGN KEY (run_id) REFERENCES repair_runs(run_id)
);

-- 文件索引（保留用于增量更新）
CREATE TABLE file_index (
    project_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    hash_algo TEXT DEFAULT 'sha256',
    discovered_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    status TEXT DEFAULT 'discovered',
    PRIMARY KEY (project_id, file_path)
);

-- Session 状态
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    entry_task TEXT,
    current_phase TEXT,  -- ledger, report, verify, repair, ship, learn
    current_step_id TEXT,
    next_step_id TEXT,
    iteration INTEGER DEFAULT 0,
    workflow_phases TEXT,  -- JSON array
    verification_status TEXT,
    recovery_policy TEXT,
    heartbeat_at TEXT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    status TEXT DEFAULT 'active'  -- active, completed, abandoned, recovered
);

-- 动态规则候选
CREATE TABLE rule_candidates (
    candidate_id TEXT PRIMARY KEY,
    project_id TEXT,
    signal_type TEXT NOT NULL,  -- user_correction, pattern_detected
    rule_scope TEXT NOT NULL,
    evidence_count INTEGER DEFAULT 1,
    confidence REAL DEFAULT 0.5,
    status TEXT DEFAULT 'pending',  -- pending, confirmed, rejected, merged
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    confirmed_rule_path TEXT,
    user_choice TEXT  -- accepted, rejected, modified
);
```

### 3.2 Milvus Collection Schema

```python
COLLECTION_NAME = "to_vibe_vectors"
DIM = 384  # all-MiniLM-L6-v2 embedding dimension
METRIC_TYPE = "IP"  # Inner Product for cosine similarity

# Collection schema
{
    "fields": [
        {"name": "vector_id", "type": "string", "is_primary": True},
        {"name": "project_id", "type": "string"},
        {"name": "file_path", "type": "string"},
        {"name": "content_hash", "type": "string"},
        {"name": "level", "type": "string"},  # L0, L1
        {"name": "summary_text", "type": "string"},
        {"name": "summary_version", "type": "string"},
        {"name": "embedding_version", "type": "string"},
        {"name": "file_type", "type": "string"},
        {"name": "keywords", "type": "array<string>"},
        {"name": "updated_at", "type": "string"}
    ]
}

# Vector ID 生成规则
# vector_id = sha256(project_id + file_path + content_hash + level + embedding_version)
# 示例: vec_7a91c4f2a3b5...
```

### 3.3 文件系统结构

```
/project/
├── .claude/                    # to-vibe 配置目录
│   ├── memory_index.sqlite     # SQLite 主数据库
│   ├── session-start.json      # Session 断点状态
│   ├── locks/                  # 锁文件
│   │   ├── session.lock
│   │   ├── skill_run_{id}.lock
│   │   └── file_{path_hash}.lock
│   └── milvus.db              # Milvus 轻量数据（可选）
├── .abstract/                  # 可读摘要缓存
│   └── by-path/
│       └── {path_to_filename}.json
├── .overview                   # 项目概览
├── .to-vibe/                  # 用户数据和规则
│   ├── rules.d/
│   │   ├── built-in/          # 内置规则
│   │   ├── user-confirmed/    # 用户确认的规则
│   │   └── generated/         # 待确认的候选规则
│   └── skills/                 # Skill 执行历史
│       └── {timestamp}/
│           ├── ask/
│           ├── context/
│           ├── loop/
│           └── ...
└── src/, docs/                 # L2 原始文件（项目本身）
```

---

## 4. session-start.json 结构

```json
{
  "version": "1.1",
  "session_id": "sess_20260429_abc123",
  "project_id": "library_system",
  "project_root": "/path/to/project",

  "entry_task": "实现用户认证功能",
  "active_skill": "loop",
  "skill_run_id": "run_loop_001",

  "workflow_phases": ["ask", "context", "loop", "simplify", "ship"],
  "current_phase": "loop",
  "iteration": 2,

  "current_step_id": "loop.execute.step_3",
  "next_step_id": "loop.reflect",

  "context_refs": {
    "L0": [".abstract/by-path/src_main_Login.java.json"],
    "L1": [".abstract/by-path/src_main.json"],
    "L2": ["src/main/java/LoginController.java"]
  },

  "artifacts_paths": {
    "ask": ".to-vibe/skills/20260429/ask/report.md",
    "context": ".to-vibe/skills/20260429/context/report.md",
    "loop": ".to-vibe/skills/20260429/loop/report.md"
  },

  "file_changes": [
    {"path": "src/main/java/LoginController.java", "hash": "sha256:xxx", "status": "modified"},
    {"path": "src/main/java/UserService.java", "hash": "sha256:yyy", "status": "created"}
  ],

  "verification_status": {
    "last_check": "2026-04-29T10:30:00Z",
    "passed": true,
    "violations": []
  },

  "recovery_policy": "auto",
  "fallback_resume_from": "loop.execute.step_2",

  "locks": {
    "session": {"held_by": "process_1234", "acquired_at": "2026-04-29T10:00:00Z"},
    "skill_run": {"held_by": "process_1234", "skill_run_id": "run_loop_001"},
    "files": ["src/main/java/LoginController.java"]
  },

  "errors": [],

  "heartbeat_at": "2026-04-29T10:35:00Z",
  "ttl_expires_at": "2026-04-29T10:40:00Z",

  "started_at": "2026-04-29T10:00:00Z",
  "last_updated_at": "2026-04-29T10:35:00Z"
}
```

---

## 5. 核心模块规格

### 5.1 EvidenceLedger（事实账本）

```python
class EvidenceLedger:
    """
    扫描项目文件，建立事实账本。
    每个结论都有证据来源（文件路径 + 行号）。
    """

    def scan(self, project_root: str) -> LedgerResult:
        """
        扫描流程：
        1. 识别项目类型（package.json, pyproject.toml, Cargo.toml, etc.）
        2. 扫描关键文件
        3. 提取事实
        4. 绑定证据
        """
        project_type = self._identify_project_type(project_root)
        scanner = self._get_scanner(project_type)

        facts = []
        for file_path in scanner.scan(project_root):
            extracted = self._extract_facts(file_path)
            facts.extend(extracted)

        ledger = self._create_ledger(project_type, facts)
        self._store_ledger(ledger)

        return LedgerResult(ledger_id=ledger.id, facts=facts)

    def _identify_project_type(self, project_root: str) -> str:
        """识别项目类型"""
        if (project_root / "package.json").exists():
            return "node"
        elif (project_root / "pyproject.toml").exists():
            return "python"
        elif (project_root / "Cargo.toml").exists():
            return "rust"
        # ... more project types
        return "unknown"

    def _extract_facts(self, file_path: Path) -> list[Fact]:
        """
        从文件中提取事实。
        每个事实必须包含 evidence（文件路径 + 行号）。
        """
        content = file_path.read_text()
        facts = []

        for extractor in self._get_extractors(file_path.suffix):
            extracted = extractor.extract(content, file_path)
            for fact in extracted:
                fact.evidence = Evidence(
                    file_path=str(file_path.relative_to(project_root)),
                    line_start=fact.line_start,
                    line_end=fact.line_end,
                    snippet=fact.snippet
                )
                facts.append(fact)

        return facts
```

### 5.2 PriorityReport（优先级报告）

```python
class PriorityReport:
    """
    基于 Evidence Ledger 生成可执行修复路线图。
    """

    def generate(self, ledger: EvidenceLedger) -> Report:
        """
        生成流程：
        1. 分析问题（P0/P1/P2）
        2. 排序优先级
        3. 生成修复路线图
        """
        facts = ledger.get_facts()

        issues = self._analyze_issues(facts)
        prioritized = self._prioritize(issues)

        report = Report(
            project_type=ledger.project_type,
            issues=prioritized,
            roadmap=self._generate_roadmap(prioritized)
        )

        self._store_report(report)
        return report

    def _analyze_issues(self, facts: list[Fact]) -> list[Issue]:
        """分析问题并分配优先级"""
        issues = []

        for fact in facts:
            if self._is_build_error(fact):
                issues.append(Issue(
                    priority=P0,
                    type="build_error",
                    description=fact.content,
                    evidence=fact.evidence
                ))
            elif self._is_missing_dependency(fact):
                issues.append(Issue(
                    priority=P0,
                    type="missing_dependency",
                    description=fact.content,
                    evidence=fact.evidence
                ))
            # ... more issue types

        return issues

    def _prioritize(self, issues: list[Issue]) -> list[Issue]:
        """按优先级排序：P0 > P1 > P2"""
        return sorted(issues, key=lambda i: (i.priority.value, i.type))
```

### 5.3 BaselineVerify（5层验证）

```python
class BaselineVerify:
    """
    5层验证体系：
    L1: 环境识别
    L2: 依赖检查
    L3: 构建检查
    L4: 启动检查
    L5: Smoke Test
    """

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.layers = [
            L1EnvCheck(),
            L2DepCheck(),
            L3BuildCheck(),
            L4StartupCheck(),
            L5SmokeTest(),
        ]

    def verify(self, report: PriorityReport) -> VerifyResult:
        """执行5层验证"""
        result = VerifyResult()

        for i, layer in enumerate(self.layers, 1):
            layer_result = layer.check(self.project_root, report)
            result.set_layer_result(i, layer_result)

            if layer_result.is_blocking() and not layer_result.can_retry():
                result.fail_at(i)
                break

            if layer_result.failed and layer_result.can_retry():
                for attempt in range(3):
                    retry_result = layer.retry(self.project_root)
                    if retry_result.passed:
                        result.set_layer_result(i, retry_result)
                        break

        return result


class L1EnvCheck:
    """L1: 环境识别"""

    def check(self, project_root: Path, report: Report) -> LayerResult:
        """
        验证 Node/Python/包管理器是否存在
        """
        checks = []

        if (project_root / "package.json").exists():
            checks.append(("node", self._check_command("node --version")))
            checks.append(("npm", self._check_command("npm --version")))
        elif (project_root / "pyproject.toml").exists():
            checks.append(("python", self._check_command("python --version")))
            checks.append(("pip", self._check_command("pip --version")))

        failed = [c for c in checks if not c[1]]
        return LayerResult(
            passed=len(failed) == 0,
            blocking=len(failed) > 0,
            details={"checks": dict(checks), "failed": failed}
        )


class L3BuildCheck:
    """L3: 构建检查"""

    def check(self, project_root: Path, report: Report) -> LayerResult:
        """
        执行构建命令，验证是否成功
        """
        build_cmd = self._get_build_command(project_root)

        try:
            result = subprocess.run(
                build_cmd,
                cwd=project_root,
                capture_output=True,
                timeout=300
            )

            return LayerResult(
                passed=result.returncode == 0,
                blocking=True,  # L3 失败是阻断性的
                details={
                    "returncode": result.returncode,
                    "stdout": result.stdout[:1000],
                    "stderr": result.stderr[:1000]
                }
            )
        except subprocess.TimeoutExpired:
            return LayerResult(passed=False, blocking=True, details={"error": "build timeout"})
```

### 5.4 RepairLoop（修复循环）

```python
class RepairLoop:
    """
    修复循环：
    Select Issue → Plan Patch → Apply Patch → Verify → Record Evidence → Next
    """

    MAX_ITERATIONS = 50
    MAX_ATTEMPTS_PER_ISSUE = 3

    def __init__(self, project_root: str, report: PriorityReport):
        self.project_root = project_root
        self.report = report
        self.sub_agents = {
            "debug": DebugAgent(),
            "refactor": RefactorAgent(),
            "system": SystemAgent(),
            "simplify": SimplifyAgent(),
        }

    def run(self) -> RepairResult:
        """执行修复循环"""
        result = RepairResult()

        for issue in self.report.get_issues_by_priority():
            if result.iteration_count >= self.MAX_ITERATIONS:
                result.exit_level = "max_iterations_reached"
                break

            patch_result = self._repair_issue(issue)
            result.add_patch(issue, patch_result)

            if patch_result.exit_level:
                result.exit_level = patch_result.exit_level
                break

        if not result.exit_level:
            result.exit_level = self._determine_exit_level(result)

        return result

    def _repair_issue(self, issue: Issue) -> PatchResult:
        """修复单个问题"""
        agent = self._select_agent(issue)

        for attempt in range(self.MAX_ATTEMPTS_PER_ISSUE):
            plan = agent.plan(issue)
            apply_result = agent.apply(plan)

            if self._verify_patch(apply_result):
                self._record_evidence(issue, apply_result)
                return PatchResult(success=True, attempt=attempt + 1)

        return PatchResult(success=False, attempt=self.MAX_ATTEMPTS_PER_ISSUE)

    def _verify_patch(self, apply_result: ApplyResult) -> bool:
        """验证补丁是否成功"""
        verify = BaselineVerify(self.project_root)
        result = verify.verify(self.report)
        return result.overall_status == "pass"
```

### 5.5 Hook 系统

```python
class FileWatcher:
    """使用 watchdog 监控文件变化"""

    WATCHED_DIRS = ["src", "docs", "tests", ".to-vibe"]
    EXCLUDED_DIRS = ["node_modules", ".git", "dist", "build", "__pycache__", "target"]

    def __init__(self, project_root: str, callback: callable):
        self.project_root = project_root
        self.callback = callback
        self.observer = watchdog.Observer()
        self._debounce_cache = {}

    def start(self):
        for dir_path in self._get_watched_dirs():
            handler = DebouncedEventHandler(self.callback, debounce_seconds=1.0)
            self.observer.schedule(handler, dir_path, recursive=True)
        self.observer.start()

    def on_file_changed(self, event: watchdog.events.FileSystemEvent):
        """
        1. Debounce（1秒内多次修改只处理一次）
        2. 计算 content_hash
        3. 判断是否需要重新提取事实
        4. 触发 EvidenceLedger 更新
        """
        if event.is_directory:
            return

        file_path = event.src_path
        if self._is_excluded(file_path):
            return

        content_hash = hasher.sha256_file(file_path)

        if not self._has_changed(file_path, content_hash):
            return

        self.callback.on_file_change(file_path, content_hash)


class RecoveryHook:
    """崩溃恢复 Hook"""

    def on_repair_crash(self, run_id: str, error: Exception):
        """
        触发时机：修复进程超时，重试3次依旧失败
        1. 写入 crash 日志
        2. 尝试回滚（根据 recovery_policy）
        3. 标记问题为「跳过」，继续下一个
        """
        self._write_crash_log(run_id, error)

        session = self._load_session_start()
        recovery_policy = session.get("recovery_policy", "auto")

        if recovery_policy == "auto":
            self._attempt_rollback(session, run_id)

        self._skip_issue_and_continue(run_id)
```

---

## 6. FastAPI 服务规格

### 6.1 REST API 路由

```python
# 记忆读取
GET /api/memory/{project_id}/L0/{file_path}
    -> 返回 L0 摘要

GET /api/memory/{project_id}/L1/{file_path}
    -> 返回 L1 摘要

GET /api/memory/{project_id}/L2/{file_path}
    -> 返回 L2 原文

# 记忆写入
POST /api/memory/{project_id}/index
    Body: {"file_path": str, "content_hash": str, "l0": str, "l1": str}
    -> 写入索引

# 检索
POST /api/memory/{project_id}/query
    Body: {"query": str, "top_k": int}
    -> 返回检索结果列表

# Session 状态
GET /api/session/{session_id}/status
    -> 返回 Session 状态

# 规则管理
GET /api/rules/{project_id}
    -> 返回所有生效规则

POST /api/rules/{project_id}/dynamic
    Body: {"candidate_id": str, "user_choice": str}
    -> 用户确认/拒绝动态规则
```

### 6.2 WebSocket 协议

```python
# 连接建立
WS /ws/{project_id}/{client_type}
    # client_type: "vscode" | "cli"

# 推送消息类型
{
    "type": "retrieval_trace",
    "data": {
        "step": "initial_search",
        "query": "...",
        "results": [...],
        "timestamp": "..."
    }
}

{
    "type": "skill_status",
    "data": {
        "skill": "loop",
        "step": "execute",
        "iteration": 2,
        "status": "running"
    }
}

{
    "type": "verification_progress",
    "data": {
        "passed": True,
        "violations": []
    }
}

# 心跳
{"type": "ping"}
```

---

## 7. 验证规则规格

### 7.1 Baseline Verify 规则结构

```yaml
# .to-vibe/rules.d/built-in/verify_l1_env.yaml
id: verify-l1-env
name: L1 环境识别规则
layer: L1
scope:
  - "package.json"
  - "pyproject.toml"
  - "Cargo.toml"
severity: error  # L1 失败是阻断性的
checks:
  - type: command_exists
    command: node
    package_manager: npm
  - type: command_exists
    command: python
    package_manager: pip
description: 验证必需的运行时环境是否存在
```

```yaml
# .to-vibe/rules.d/built-in/verify_l3_build.yaml
id: verify-l3-build
name: L3 构建检查规则
layer: L3
scope:
  - "package.json"
  - "pyproject.toml"
  - "Cargo.toml"
severity: error
build_commands:
  node: ["npm run build", "npm run build:*"]
  python: ["python setup.py build", "pip install ."]
  rust: ["cargo build --release"]
description: 验证项目能否成功构建
```

### 7.2 动态规则结构

```yaml
# .to-vibe/rules.d/user-confirmed/naming-js-function-camel-case.yaml
id: naming-js-function-camel-case
name: JS/TS 函数命名使用 camelCase
source: user_confirmed
scope:
  - "*.js"
  - "*.ts"
  - "*.jsx"
  - "*.tsx"
  - "*.vue"
severity: warning
pattern:
  - "(function\\s+[A-Z][a-zA-Z0-9_]+|const\\s+[A-Z][a-zA-Z0-9_]+\\s*=)"
description: 观察到用户多次纠正 JS/TS 函数命名应使用 camelCase
confirmed_at: "2026-04-30T10:00:00Z"
confirmed_by: user
evidence_count: 3
```

### 7.3 规则加载顺序

```
1. Baseline Verify 内置规则 (.to-vibe/rules.d/built-in/verify_*.yaml)
2. 默认规则 (to-vibe.yaml verification.rules)
3. 项目规则 (.to-vibe/rules.d/project.yaml)
4. 用户确认动态规则 (.to-vibe/rules.d/user-confirmed/*.yaml)
5. 任务 override (当前任务显式指定)
6. 当前用户指令 (运行时 --override)
```

---

## 8. 两阶段索引规格

### 8.1 阶段一：快速初始化

```python
def init_cheap(project_root: str, config: dict):
    """
    to-vibe init (默认)
    特点：快、便宜、不调用 LLM
    """
    files = _scan_project_files(project_root)

    for file in files:
        content_hash = hasher.sha256_file(file.path)
        db.upsert_file_index(file.path, content_hash, status="hashed")

        l0 = _rule_based_summary(file.content, max_tokens=100)
        l1 = _rule_based_summary(file.content, max_tokens=2000)

        db.upsert_summary(file.path, content_hash, "L0", l0, method="rule")
        db.upsert_summary(file.path, content_hash, "L1", l1, method="rule")

        print(f"[{completed}/{total}] {file.path}")

    if config.get("generate_embedding", False):
        _generate_embeddings_parallel(files)


def _rule_based_summary(content: str, max_tokens: int) -> str:
    lines = content.split('\n')
    summary_lines = [line for line in lines if _is_significant_line(line)]
    full_summary = '\n'.join(summary_lines)
    tokens = _count_tokens(full_summary)

    if tokens > max_tokens:
        return _truncate(full_summary, max_tokens)
    return full_summary
```

### 8.2 阶段二：深度初始化

```python
def init_deep(project_root: str, budget_tokens: int, max_files: int):
    """
    to-vibe init --deep
    特点：高价值文件优先，预算控制
    """
    prioritized_files = _priority_sort(
        files=_scan_project_files(project_root),
        priority_rules=[
            "README > docs",
            "Controller > Service > Repository",
            "Config > Entity > DTO",
            "Tests last",
        ]
    )

    remaining_tokens = budget_tokens

    for file in prioritized_files[:max_files]:
        estimated_tokens = _estimate_tokens(file.content)
        if estimated_tokens > remaining_tokens:
            break

        l0 = abstractor.generate(file.content, "L0")
        l1 = abstractor.generate_structured(file.content, "L1")

        db.upsert_summary(file.path, file.hash, "L0", l0, method="llm")
        db.upsert_summary(file.path, file.hash, "L1", l1, method="llm")

        vector = embedding_model.encode(l0)
        milvus.upsert(vector_id, vector, metadata)

        remaining_tokens -= estimated_tokens
        print(f"[{completed}/{max_files}] {file.path}")
```

### 8.3 中断恢复

```python
def init_resume(project_root: str):
    """
    to-vibe init --resume
    从上次中断处继续
    """
    run = db.get_last_init_run(project_id)
    if not run:
        print("No interrupted run found. Starting fresh.")
        return init_cheap(project_root)

    current_files = {f.path: f for f in _scan_project_files(project_root)}

    pending_files = []
    for record in db.get_file_records_by_status(run.run_id, ["pending", "failed", "interrupted"]):
        if record.file_path in current_files:
            pending_files.append(current_files[record.file_path])

    print(f"Resuming {len(pending_files)} pending files...")

    for file in pending_files:
        current_hash = hasher.sha256_file(file.path)
        if current_hash == record.content_hash:
            _complete_remaining_steps(file, record)
        else:
            _process_file(file, current_hash)

        db.update_file_status(run.run_id, file.path, "completed")
```

---

## 9. CLI 命令规格

```python
@click.group()
def cli():
    """to-vibe: AI 代码生成后的项目工程化平台"""
    pass


@cli.command()
@click.option("--deep", is_flag=True, help="启用 LLM 深度分析")
@click.option("--budget-tokens", default=0, help="LLM token 预算")
@click.option("--max-files", default=0, help="最大处理文件数")
@click.option("--resume", is_flag=True, help="继续上次中断的初始化")
def init(deep, budget_tokens, max_files, resume):
    """初始化项目索引并建立 Evidence Ledger"""
    if resume:
        resume_init()
    elif deep:
        deep_init(budget_tokens, max_files)
    else:
        cheap_init()


@cli.command()
def diagnose():
    """诊断项目并生成优先级报告"""
    ledger = EvidenceLedger.from_project()
    report = PriorityReport.generate(ledger)
    click.echo(report.to_markdown())


@cli.command()
@click.option("--layers", default="1,2,3,4,5", help="要执行的验证层级（逗号分隔）")
@click.option("--retry", default=3, help="每层最大重试次数")
def verify(layers, retry):
    """执行 Baseline Verify 5层验证"""
    verify = BaselineVerify.from_project()
    result = verify.run(layers=layers, max_retries=retry)

    if result.overall_status == "pass":
        click.echo("✅ 验证通过")
    else:
        click.echo("❌ 验证失败")
        for i, layer in enumerate(result.layer_results, 1):
            if not layer.passed:
                click.echo(f"  L{i}: {layer.details}")


@cli.command()
@click.option("--target", default="maintainable", type=click.Choice(["stabilized", "maintainable", "ship-ready"]), help="目标退出级别")
@click.option("--max-iterations", default=50, help="最大修复迭代次数")
def repair(target, max_iterations):
    """执行 Repair Loop 修复循环"""
    loop = RepairLoop.from_project(target=target, max_iterations=max_iterations)
    result = loop.run()

    click.echo(f"修复完成: {result.exit_level}")
    click.echo(f"  P0 修复: {result.p0_fixed}/{result.p0_fixed + result.p0_remaining}")
    click.echo(f"  P1 修复: {result.p1_fixed}/{result.p1_fixed + result.p1_remaining}")
    click.echo(f"  P2 修复: {result.p2_fixed}/{result.p2_fixed + result.p2_remaining}")


@cli.command()
def ship():
    """判断项目是否达到可发布状态"""
    checker = ShipChecker.from_project()
    result = checker.check()

    if result.is_ready:
        click.echo("✅ 项目已达到可发布状态")
    else:
        click.echo("❌ 项目未达到发布标准")
        for check in result.failed_checks:
            click.echo(f"  - {check}")


@cli.command()
def status():
    """查看当前项目状态"""
    session = load_session_start()
    if session:
        click.echo(f"Phase: {session.get('current_phase', 'unknown')}")
        click.echo(f"Status: {session.get('status', 'unknown')}")
    else:
        click.echo("No active session - run 'to-vibe init' first")


@cli.command()
def learn():
    """从历史修复中提取经验"""
    learner = ExperienceLearner.from_project()
    result = learner.extract()

    click.echo("经验提取完成")
    for exp in result.new_experiences:
        click.echo(f"  - {exp.description}")
```

---

## 10. 配置文件格式

### 10.1 to-vibe.yaml

```yaml
version: "2.0"

# Evidence Ledger 配置
evidence_ledger:
  storage_dir: .to-vibe/evidence_ledger
  scanner:
    exclude_patterns:
      - "node_modules/**"
      - ".git/**"
      - "dist/**"
      - "build/**"
      - "target/**"
      - "**/*.min.js"
      - "**/*.map"
  fact_extractors:
    - package_json
    - pyproject_toml
    - cargo_toml
    - source_code

# Priority Report 配置
priority_report:
  output_dir: .to-vibe/priority_report
  priority_rules:
    -阻断性问题优先（P0）
    -影响开发效率次之（P1）
    -优化建议最后（P2）

# Baseline Verify 配置
baseline_verify:
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

# Repair Loop 配置
repair_loop:
  max_iterations: 50
  max_attempts_per_issue: 3
  exit_levels:
    default: maintainable
    stabilized: P0全部修复
    maintainable: P0+P1全部修复（默认）
    ship_ready: 达到发布标准

# Memory 配置（Phase 2 映射）
memory:
  layers:
    L0: .to-vibe/.abstract      # 从 Ledger 派生
    L1: .to-vibe/priority_report  # 优先级报告
    L2: .to-vibe/evidence_ledger  # 事实账本

  vector:
    enabled: true
    db_path: .claude/milvus.db
    collection: to_vibe_vectors
    embedding_model: sentence-transformers/all-MiniLM-L6-v2

# 动态规则配置
dynamic_rules:
  enabled: true
  threshold: 3
  rules_dir: .to-vibe/rules.d

# Session 配置
session:
  heartbeat_interval_seconds: 30
  ttl_seconds: 300
  recovery_policy: auto

# API 配置
api:
  host: 0.0.0.0
  port: 8765
  cors_origins:
    - "vscode://"
  websocket_heartbeat: 30

# MiniMax API 配置
minimax:
  api_key: ${MINIMAX_API_KEY}
  base_url: https://api.minimax.chat
  model: MiniMax-Text-01
  timeout: 30
  max_retries: 3
```

---

## 11. 依赖规格

### 11.1 pyproject.toml

```toml
[project]
name = "to-vibe"
version = "0.1.0"
description = "AI-driven vibecoding autopilot workflow"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1.0",
    "sqlite-utils>=3.35",
    "pymilvus>=2.4.0",
    "sentence-transformers>=2.2.0",
    "openai>=1.0.0",
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "websockets>=12.0",
    "watchdog>=3.0.0",
    "redis>=5.0.0",
    "pyyaml>=6.0",
    "pydantic>=2.0.0",
    "tiktoken>=0.5.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "black>=24.0.0",
    "pylint>=3.0.0",
    "ruff>=0.1.0",
]
```

---

## 12. Open Questions 状态（Phase 2）

| # | 问题 | 状态 | 结论 |
|---|-----|------|------|
| 1 | Evidence Ledger 如何防止 AI 幻觉 | ✅ 已解决 | 每个结论绑定文件路径+行号作为证据 |
| 2 | Priority Report 如何自动排序 | ✅ 已解决 | P0 阻断 > P1 重要 > P2 优化 |
| 3 | Baseline Verify 5层具体实现 | ✅ 已解决 | L1-L5 每层有明确验证方式和失败策略 |
| 4 | Repair Loop 退出条件 | ✅ 已解决 | Stabilized / Maintainable / Ship-ready |
| 5 | Memory 新层级映射 | ✅ 已解决 | L0=派生概括, L1=Priority Report, L2=Ledger |
| 6 | 旧 Skill 到新能力映射 | ✅ 已解决 | Loop→Repair Loop, Simplify→Priority Report |
| 7 | Cross-project Experience 处理 | ✅ 已解决 | 仅供参考，不覆盖当前项目证据 |
