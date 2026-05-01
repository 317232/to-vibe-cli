# to-vibe CLI 实现计划

> 版本：v1.0
> 日期：2026-05-01
> 状态：规划完成

---

## 1. 任务总览

共 **29 个任务**，分为 8 个阶段，实现从零到完整 to-vibe CLI TUI 工具。

```
阶段 1: 基础设施 (P0)        ████ 3 tasks
阶段 2: MCP 通信层 (P0)     ████ 3 tasks
阶段 3: TUI 框架 (P0)        ████ 3 tasks
阶段 4: 右侧面板组件 (P1)     ████ 8 tasks
阶段 5: 左侧面板 LLM Chat (P1) ██ 2 tasks
阶段 6: Pipeline 核心逻辑 (P2) ████ 5 tasks
阶段 7: 交互系统 (P2)       ████ 3 tasks
阶段 8: 串联测试 (P2)        ██ 1 task
```

---

## 2. 依赖关系图

```
阶段 1: 基础设施
─────────────────────────────────────────
[#1] 1.1 项目脚手架初始化
      └──> [#5] 1.2 配置解析模块
      └──> [#8] 1.3 日志框架实现

阶段 2: MCP 通信层
─────────────────────────────────────────
[#8] 日志框架
      └──> [#3] 2.1 MCP Server 框架
            └──> [#6] 2.2 Notification 协议
                  └──> [#2] 2.3 命令处理器

阶段 3: TUI 框架
─────────────────────────────────────────
[#5] 配置解析 + [#8] 日志框架
      └──> [#9] 3.1 Textual App 主类
            └──> [#10] 3.3 样式系统定义
                  └──> [#4] 3.2 主屏幕 Tab 导航
                        └──> [#7] 4.2 StageBar 组件
                              └──> [#11] 4.1 Header 组件

阶段 4: 右侧面板组件
─────────────────────────────────────────
[#7] StageBar 组件
      └──> [#12] 4.5 VerifyTable 组件
            └──> [#13] 5.1 LLM API 客户端
                  └──> [#18] 4.7 LogStream + LogFilters
                        └──> [#19] 4.4 PriorityCard
                              └──> [#20] 4.6 LearnPanel

      └──> [#14] 4.8 Artifacts + Footer

[#11] Header 组件
      └──> [#15] 4.3 EvidenceCard 组件

阶段 5: Pipeline 核心逻辑
─────────────────────────────────────────
[#21] 6.2 Priority Report 模块
      └──> [#22] 7.2 暂停/重试/跳过逻辑
            └──> [#23] 8.1 端到端集成测试

[#4] 主屏幕 Tab 导航 + [#12] VerifyTable + [#15] EvidenceCard + [#16] 6.1 Evidence Ledger
      └──> [#26] 6.3 Baseline Verify (L1-L5)
            └──> [#27] 7.1 快捷键系统

阶段 6: Pipeline 核心逻辑 (续)
─────────────────────────────────────────
[#22] 暂停/重试/跳过
      └──> [#24] 7.3 Learn 详情视图操作
            └──> [#25] 6.4 Repair Loop 模块

[#18] LogStream + [#19] PriorityCard + [#20] LearnPanel
      └──> [#28] 6.5 Learn 模块 (完整实现)

阶段 7: 交互系统
─────────────────────────────────────────
[#26] Baseline Verify
      └──> [#27] 7.1 快捷键系统

阶段 8: 串联测试
─────────────────────────────────────────
所有阶段产出汇聚
      └──> [#23] 8.1 端到端集成测试
```

---

## 3. 任务详情

### 阶段 1: 基础设施 (P0)

#### [#1] 1.1 项目脚手架初始化
**依赖**：无
**文件**：`pyproject.toml`, `src/__init__.py`, `src/cli.py`
**任务**：
- 创建 `pyproject.toml`，定义依赖：textual, pyyaml, httpx, aiohttp, sqlite-utils, pydantic, click
- 建立目录结构：`src/tui/`, `src/mcp/`, `src/llm/`, `src/pipeline/`, `src/learn/`, `src/storage/`, `src/utils/`
- 创建 `src/__init__.py` 包初始化
- 创建 `src/cli.py` CLI 入口，实现 `to-vibe run` 命令框架

---

#### [#5] 1.2 配置解析模块
**依赖**：[#1] 1.1 项目脚手架初始化
**文件**：`src/config.py`
**任务**：
- 实现 `to-vibe.yaml` 解析器
- 支持环境变量引用 `${VAR}` 展开
- 验证必填字段：`llm.api_key`, `llm.model`
- 定义配置 dataclass：`LLMConfig`, `PipelineConfig`, `SessionConfig`, `LearnConfig`, `UIConfig`

---

#### [#8] 1.3 日志框架实现
**依赖**：[#1] 1.1 项目脚手架初始化
**文件**：`src/utils/logger.py`
**任务**：
- 实现 Logger 类，支持 INFO/WARN/ERROR 级别
- 日志输出到 LogStream 组件（通过回调）
- 支持 level filter（全局 + per-component）
- JSON 格式化输出供 MCP notification 使用

---

### 阶段 2: MCP 通信层 (P0)

#### [#3] 2.1 MCP Server 框架
**依赖**：[#8] 1.3 日志框架实现
**文件**：`src/mcp/server.py`
**任务**：
- 基于 asyncio 的 MCP Server
- 实现 `server_send_notification` 机制
- 处理来自 client 的 invoke 请求
- 内部队列连接 TUI renderer

---

#### [#6] 2.2 Notification 协议
**依赖**：[#3] 2.1 MCP Server 框架
**文件**：`src/mcp/protocol.py`
**任务**：
- 定义所有 Notification 类型 dataclass
- `log`, `stage_start`, `stage_complete`, `progress`, `evidence`, `issue_found`, `action_required`, `error`
- JSON 序列化/反序列化
- `action_required` 的 options 结构定义

---

#### [#2] 2.3 命令处理器
**依赖**：[#3] 2.1 MCP Server 框架
**文件**：`src/mcp/handler.py`
**任务**：
- 处理 `to-vibe.run` — 启动完整流程
- 处理 `to-vibe.pause` — 暂停当前流程
- 处理 `to-vibe.retry` — 重试失败步骤
- 处理 `to-vibe.skip` — 跳过当前阶段
- 命令路由到 Pipeline 各模块

---

### 阶段 3: TUI 框架 (P0)

#### [#9] 3.1 Textual App 主类
**依赖**：[#5] 1.2 配置解析模块, [#8] 1.3 日志框架
**文件**：`src/tui/app.py`
**任务**：
- Textual App 主类定义
- 3 Tab 结构：Chat / to-vibe / Logs
- 键盘事件处理
- 内部消息队列连接 MCP Server

---

#### [#10] 3.3 样式系统定义
**依赖**：[#9] 3.1 Textual App 主类
**文件**：`src/tui/styles.py`
**任务**：
- 深色主题定义
- 颜色常量：`GREEN` (pass), `RED` (fail), `ORANGE` (warning), `PURPLE` (learn), `BLUE` (active)
- Border 样式常量
- 字体样式常量

---

#### [#4] 3.2 主屏幕 Tab 导航
**依赖**：[#3] 2.1 MCP Server 框架, [#6] 2.2 Notification 协议
**文件**：`src/tui/screens/main_screen.py`
**任务**：
- 3 个 Tab 面板容器
- Tab 1: Chat Panel
- Tab 2: to-vibe Pipeline Panel
- Tab 3: Logs Panel
- Tab 切换快捷键绑定

---

### 阶段 4: 右侧面板组件 (P1)

#### [#7] 4.2 StageBar 组件
**依赖**：[#4] 3.2 主屏幕 Tab 导航, [#6] 2.2 Notification 协议
**文件**：`src/tui/components/stage_bar.py`
**任务**：
- 5 阶段 chevron 指示器
- 状态：completed/active/failed/skipped/pending
- 彩色边框：green/orange/red/grey/grey
- 脉冲动画 for active 状态

---

#### [#11] 4.1 Header 组件
**依赖**：[#7] 4.2 StageBar 组件, [#10] 3.3 样式系统定义
**文件**：`src/tui/components/header.py`
**任务**：
- 品牌图标 + 名称 (`◇ to-vibe`)
- 项目路径显示
- Git branch 图标 + 名称
- 运行时 timer

---

#### [#12] 4.5 VerifyTable 组件
**依赖**：[#7] 4.2 StageBar 组件, [#10] 3.3 样式系统定义
**文件**：`src/tui/components/verify_table.py`
**任务**：
- 红色边框表格
- L1-L5 五行：Environment / Dependencies / Build / Start / Smoke Test
- 状态图标：✅ pass / ❌ fail / ⊘ skip
- 命令列显示实际执行的命令

---

#### [#15] 4.3 EvidenceCard 组件
**依赖**：[#11] 4.1 Header 组件
**文件**：`src/tui/components/evidence_card.py`
**任务**：
- 绿色边框卡片
- 显示 tech stack (Spring Boot, Thymeleaf, MySQL)
- 显示 files scanned count
- 显示 ignored directories
- 显示 output path

---

#### [#14] 4.8 Artifacts + Footer 组件
**依赖**：[#7] 4.2 StageBar 组件, [#10] 3.3 样式系统定义
**文件**：`src/tui/components/artifacts.py`, `src/tui/components/footer.py`
**任务**：
- Artifacts 列表：📁 for dir, · for file
- Footer 显示 executor + sync icon
- 快捷键提示：[Space]暂停 [R]重试 [S]跳过 [↑↓]滚动

---

#### [#18] 4.7 LogStream + LogFilters 组件
**依赖**：[#13] 5.1 LLM API 客户端
**文件**：`src/tui/components/log_stream.py`
**任务**：
- LogFilters：[info] [error] [warning] 按钮 + [Clear]
- LogStream：timestamp + level + text
- 自动跟随滚动
- ↑↓ 键手动滚动

---

#### [#19] 4.4 PriorityCard 组件
**依赖**：[#18] 4.7 LogStream + LogFilters
**文件**：`src/tui/components/priority_card.py`
**任务**：
- 橙色边框卡片
- Blockers / High / Medium 计数
- Top issue 描述
- Suggested capability

---

#### [#20] 4.6 LearnPanel + LearnDetail 组件
**依赖**：[#18] 4.7 LogStream + LogFilters
**文件**：`src/tui/components/learn_panel.py`
**任务**：
- LearnPanel：紫色边框，pending/completed 状态，Records/Focus/Source，[详情]按钮
- LearnDetailView：展开后显示 verified_fixes/issue_patterns/project_facts/user_rules
- 操作按钮：[A]接受 [E]编辑 [R]拒绝 [P]固定 [D]删除 [Esc]返回

---

### 阶段 5: 左侧面板 LLM Chat (P1)

#### [#13] 5.1 LLM API 客户端 (Anthropic + OpenAI)
**依赖**：[#5] 1.2 配置解析模块
**文件**：`src/llm/client.py`, `src/llm/anthropic.py`, `src/llm/openai.py`
**任务**：
- 统一 LLM 客户端接口
- Anthropic API 兼容实现
- OpenAI API 兼容实现
- 流式输出支持
- 对话历史管理

---

#### [#17] 5.2 Chat Panel UI
**依赖**：[#12] 4.5 VerifyTable 组件
**文件**：`src/tui/screens/chat_panel.py`
**任务**：
- 对话历史显示区域
- 底部输入框
- Enter 发送，Ctrl+C 取消
- LLM 流式响应显示

---

### 阶段 6: Pipeline 核心逻辑 (P2)

#### [#16] 6.1 Evidence Ledger 模块
**依赖**：[#11] 4.1 Header 组件
**文件**：`src/pipeline/evidence_ledger.py`
**任务**：
- 扫描项目文件
- 识别技术栈 (package.json/pyproject.toml/Cargo.toml)
- 提取事实，绑定证据（file path + line number）
- 输出 `.to-vibe/evidence-ledger.json`

---

#### [#21] 6.2 Priority Report 模块
**依赖**：[#4] 3.2 主屏幕 Tab 导航
**文件**：`src/pipeline/priority_report.py`
**任务**：
- 基于 Evidence Ledger 分析问题
- 生成 P0/P1/P2 优先级
- 输出可执行路线图
- 输出 `.to-vibe/priority-report.json`

---

#### [#26] 6.3 Baseline Verify (L1-L5)
**依赖**：[#7] 4.2 StageBar 组件
**文件**：`src/pipeline/baseline_verify.py`
**任务**：
- L1 环境识别 (which node/python)
- L2 依赖检查 (npm install / pip install)
- L3 构建检查 (npm build / python setup.py)
- L4 启动检查 (服务能否启动)
- L5 Smoke Test (核心功能)
- 每层 max_retries 配置
- 失败阻断后续层

---

#### [#25] 6.4 Repair Loop 模块
**依赖**：[#24] 7.3 Learn 详情视图操作
**文件**：`src/pipeline/repair_loop.py`
**任务**：
- Select → Plan → Apply → Verify → Record 循环
- Debug/Refactor/System/Simplify 子能力
- max_iterations = 50
- 退出条件：stabilized / maintainable / ship-ready

---

#### [#28] 6.5 Learn 模块 (完整实现)
**依赖**：[#18] 4.7 LogStream + LogFilters
**文件**：`src/learn/collector.py`, `src/learn/filter.py`, `src/learn/summarizer.py`, `src/learn/validator.py`, `src/learn/reviewer.py`, `src/learn/storage.py`
**任务**：
- 4 类记忆：project_fact, verified_fix, issue_pattern, user_confirmed_rule
- 7 步流程：Collect → Filter → Summarize → Validate → Review → Store → Retrieve
- 3 层存储：.to-vibe/learn/ (human) + SQLite L0 + L1 vector (future)

---

### 阶段 7: 交互系统 (P2)

#### [#27] 7.1 快捷键系统
**依赖**：[#26] 6.3 Baseline Verify (L1-L5)
**文件**：`src/tui/app.py` (更新)
**任务**：
- [Space] 暂停：保存状态到 session-start.json
- [R] 重试：Repair Loop 重做当前 step，Verify 重做失败层
- [S] 跳过：标记跳过，进入下一阶段
- [↑↓] 滚动：LogStream 滚动
- [Tab] 切换 Tab
- [Esc] 返回详情视图

---

#### [#22] 7.2 暂停/重试/跳过逻辑
**依赖**：[#21] 6.2 Priority Report 模块
**文件**：`src/mcp/handler.py` (更新)
**任务**：
- 暂停：保存 stage, iteration, issue 到 session-start.json
- 重试：根据当前阶段选择对应 retry 行为
- 跳过：标记 skip，进入下一阶段

---

#### [#24] 7.3 Learn 详情视图操作
**依赖**：[#23] 8.1 端到端集成测试
**文件**：`src/tui/components/learn_panel.py` (更新)
**任务**：
- [A] 接受 pending rule
- [E] 编辑 rule
- [R] 拒绝 rule
- [P] 固定 rule
- [D] 删除 rule
- [Esc] 返回

---

### 阶段 8: 串联测试 (P2)

#### [#23] 8.1 端到端集成测试
**依赖**：[#22] 7.2 暂停/重试/跳过逻辑
**文件**：`tests/e2e/`
**任务**：
- 完整流程测试：`to-vibe run ./project`
- Evidence Ledger → Priority Report → Baseline Verify (L1-L5) → Repair Loop → Learn
- 验证所有组件状态更新正确
- 验证日志输出正确
- 验证交互可用（暂停/重试/跳过）

---

## 4. 实现顺序

### 第一批：基础设施 + MCP + TUI 框架
```
[#1] → [#5] → [#8]
           ↓
[#3] → [#6] → [#2]
           ↓
[#9] → [#10] → [#4]
```

### 第二批：右侧面板组件
```
[#7] → [#11] → [#15]    (Header → EvidenceCard)
        → [#12] → [#13] → [#18] → [#19] → [#20]  (VerifyTable → LLM → Log → Priority → Learn)
        → [#14]                                                    (Artifacts + Footer)
```

### 第三批：Pipeline 核心 + 交互
```
[#21] → [#22] → [#24] → [#25]    (Priority → 交互 → Detail → Repair)
[#16] → [#26] → [#27]             (Evidence → Verify → 快捷键)
        → [#28]                   (Learn 完整)
```

### 第四批：串联 + 测试
```
[#23] 端到端测试
```

---

## 5. 里程碑

| 里程碑 | 任务组合 | 产出 |
|--------|----------|------|
| **M1: 骨架** | #1 + #5 + #8 | 可运行 CLI，配置解析，日志框架 |
| **M2: 通信** | #3 + #6 + #2 | MCP Server 完整，命令处理完成 |
| **M3: TUI 框架** | #9 + #10 + #4 | 3 Tab 可切换，样式定义完成 |
| **M4: 右侧面板** | #7 + #11 + #12 + #15 + #14 + #18 + #19 + #20 | 完整 to-vibe panel 显示 |
| **M5: LLM Chat** | #13 + #17 | Chat Panel 可聊天 |
| **M6: Pipeline** | #16 + #21 + #26 + #25 + #28 | 完整 5 阶段流程跑通 |
| **M7: 交互** | #27 + #22 + #24 | 快捷键全部可用 |
| **M8: 完成** | #23 | E2E 测试通过 |

---

## 6. 文件结构

```
to-vibe-cli/
├── pyproject.toml
├── to-vibe.yaml
├── SPEC.md                          # 技术规格
├── PRD_v2.md                        # 产品需求文档
├── IMPLEMENTATION_PLAN.md           # 本文档
├── README.md
├── CLAUDE.md
├── src/
│   ├── __init__.py
│   ├── cli.py                       # CLI 入口
│   ├── config.py                    # 配置解析
│   ├── tui/
│   │   ├── __init__.py
│   │   ├── app.py                  # Textual App 主类
│   │   ├── styles.py               # 样式定义
│   │   ├── screens/
│   │   │   ├── __init__.py
│   │   │   ├── main_screen.py      # 3 Tab 容器
│   │   │   ├── chat_panel.py       # Tab 1: LLM Chat
│   │   │   ├── to_vibe_panel.py    # Tab 2: Pipeline
│   │   │   └── logs_panel.py       # Tab 3: Logs
│   │   └── components/
│   │       ├── __init__.py
│   │       ├── header.py           # Header 组件
│   │       ├── stage_bar.py        # StageBar 组件
│   │       ├── evidence_card.py     # EvidenceCard
│   │       ├── priority_card.py    # PriorityCard
│   │       ├── verify_table.py     # VerifyTable
│   │       ├── learn_panel.py      # LearnPanel + LearnDetail
│   │       ├── log_stream.py       # LogStream + LogFilters
│   │       ├── artifacts.py        # Artifacts 列表
│   │       └── footer.py          # Footer
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py              # MCP Server
│   │   ├── protocol.py            # Notification 协议
│   │   └── handler.py             # 命令处理
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── client.py              # LLM 统一客户端
│   │   ├── anthropic.py          # Anthropic API
│   │   └── openai.py             # OpenAI API
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── evidence_ledger.py     # Evidence Ledger
│   │   ├── priority_report.py    # Priority Report
│   │   ├── baseline_verify.py    # Baseline Verify (L1-L5)
│   │   ├── repair_loop.py         # Repair Loop
│   │   └── learn.py               # Learn
│   ├── learn/
│   │   ├── __init__.py
│   │   ├── collector.py          # 收集候选
│   │   ├── filter.py             # 过滤
│   │   ├── summarizer.py         # 总结
│   │   ├── validator.py          # 验证
│   │   ├── reviewer.py           # 用户审核
│   │   └── storage.py            # 存储
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── sqlite.py             # SQLite 主存
│   │   └── artifacts.py         # Artifact 读写
│   └── utils/
│       ├── __init__.py
│       ├── logger.py             # 日志
│       └── locks.py             # 文件锁
└── tests/
    ├── __init__.py
    ├── unit/
    │   ├── test_config.py
    │   ├── test_mcp_protocol.py
    │   └── test_learn_storage.py
    ├── integration/
    │   ├── test_evidence_ledger.py
    │   ├── test_priority_report.py
    │   └── test_baseline_verify.py
    └── e2e/
        └── test_full_pipeline.py
```