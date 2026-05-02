# to-vibe 开发环境配置指南

> 本文档说明 to-vibe-cli 项目的开发环境配置，适用于所有贡献者。

---

## 1. 依赖要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | >= 3.11 | 项目主语言 |
| pip / pip-tools | 最新 | 包管理 |
| Git | 任意稳定版 | 版本控制 |
| GitHub CLI | >= 2.0 | Issue 管理 |

---

## 2. 本地开发环境安装

### 2.1 克隆仓库

```bash
git clone git@github.com:317232/to-vibe-cli.git
cd to-vibe-cli
```

### 2.2 创建虚拟环境

```bash
python3.11 -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate  # Windows
```

### 2.3 安装依赖

```bash
pip install -e .           # 安装项目
pip install -e ".[dev]"    # 安装开发依赖（含 pytest、ruff、mypy）

# 或使用 uv（更快）
uv pip install -e .
uv pip install -e ".[dev]"
```

### 2.4 验证安装

```bash
to-vibe --version
```

---

## 3. 环境变量配置

### 3.1 创建 .env 文件

在项目根目录创建 `.env` 文件（禁止提交到 git）：

```bash
# LLM API Keys（根据选择的 provider 选择性填写）
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
MINIMAX_API_KEY=...

# GitHub CLI 通常通过 gh auth login 自动配置
```

### 3.2 在 to-vibe.yaml 中引用

```yaml
llm:
  api_key: "${ANTHROPIC_API_KEY}"   # 读取环境变量
  provider: "anthropic"              # 'anthropic' | 'openai'
  model: "claude-sonnet-4-7"
```

项目使用 `python-dotenv` 自动加载 `.env` 文件（已在 `config.py` 中实现）。

---

## 4. 配置文件说明

| 文件 | 用途 | 提交到 git |
|------|------|-----------|
| `pyproject.toml` | Python 包配置、依赖、构建工具 | ✅ |
| `to-vibe.yaml` | 运行时配置（LLM、Pipeline、Learn 等）示例 | ✅ |
| `.env` | 本地环境变量（API keys） | ❌ |
| `session-start.json` | Pipeline 运行状态（自动生成） | ❌ |

---

## 5. 代码质量工具

### Ruff（Lint + Format）

```bash
ruff check .           # 检查
ruff check --fix .     # 自动修复
ruff format .          # 格式化
```

### MyPy（类型检查）

```bash
mypy src/to_vibe/
```

### Pytest（测试）

```bash
pytest                 # 运行所有测试
pytest --cov=src/to_vibe --cov-report=term-missing  # 带覆盖率
```

---

## 6. 项目结构

```
to-vibe-cli/
├── src/to_vibe/
│   ├── cli.py                 # CLI 入口
│   ├── config.py              # 配置解析
│   ├── runtime/               # 运行时状态（Event Model、Session）
│   ├── pipeline/              # Pipeline Runner
│   ├── learn/                 # Learn 模块
│   ├── llm/                   # LLM 客户端
│   ├── mcp/                   # MCP Server 协议
│   ├── storage/              # 存储抽象
│   ├── tui/                   # Textual TUI
│   └── utils/                 # 日志工具
├── tests/
├── .to-vibe/                  # 运行时产出（自动生成）
├── pyproject.toml
├── to-vibe.yaml
└── SETUP.md
```

运行时产物目录 `.to-vibe/` 结构：

```
.to-vibe/
├── logs/
├── session-start.json
├── evidence-ledger.json
├── priority-report.json
├── baseline-verify.json
├── repair-loop.json
└── learn/
    ├── learn.db               # SQLite
    ├── learn-summary.md
    ├── learned-rules.json
    └── rejected-lessons.json
```

---

## 7. Git 工作流

### 7.1 提交前检查

```bash
ruff check --fix .
ruff format .
git add .
git commit -m "feat(scope): description"
```

### 7.2 分支命名

```
feature/issue-14-learn-mvp
fix/issue-12-interaction
```

---

## 8. 常见问题

| 问题 | 解决 |
|------|------|
| `ModuleNotFoundError: No module named 'to_vibe'` | `pip install -e .` |
| Ruff 报 import 未排序 | `ruff check --fix .` |
| MyPy 找不到 stub | 确认 `python_version` 为 3.11 |
| `.env` 变量未生效 | 确保 `.env` 在项目根目录 |

---

## 9. 推荐工具

| 工具 | 用途 |
|------|------|
| `uv` | 快速 Python 包管理器 |
| `pyenv` | 管理多版本 Python |
| `gh` | GitHub CLI（Issue 管理） |
| `direnv` | 自动加载 .env 文件 |