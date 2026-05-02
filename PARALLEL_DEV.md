# 并行 Claude Code 开发指南

> 适用于 to-vibe-cli 项目多窗口并行开发

---

## 1. 背景

本项目 `to-vibe-cli` 使用 Claude Code 进行 AI 辅助开发。为提升协作效率或同时进行多项任务，需要在多个 Claude Code 窗口中并行开发。

---

## 2. 如何开启第二个并行窗口

### 方式一：终端命令

```bash
open -n /Applications/Claude.app
```

### 方式二：新建终端标签页

```bash
# macOS
Cmd+T

# 手动 cd 到项目目录
cd /Users/m9570/Desktop/vibecoding/to-vibe-cli
```

### 重要约束

> **不要**使用 `--project` 参数同时指向同一个目录启动两个 Claude Code 实例。Claude Code 会检测到冲突并拒绝第二个实例。

第二个窗口只需要手动 `cd` 进入项目目录即可，不需要任何特殊参数。

---

## 3. 分支策略

### 推荐：一方 main，一方 feature branch

```
当前窗口（main branch）        → 核心功能开发，直接 push
第二个窗口（feature/xxx）      → 实验性开发或大规模重构
                               → push 到独立 branch 后通过 GitHub PR 合并
```

### 在第二个窗口执行

```bash
# 从 main 新建一个 feature branch
git checkout -b feature/parallel-task-name

# 完成开发后 push
git push -u origin feature/parallel-task-name
```

### 如果两个窗口都在 main

约定：一方 push 完成后，另一方再 push。Fast-forward 冲突时先 `git pull --rebase` 再 push。

---

## 4. 共享资源说明

工作目录（`/Users/m9570/Desktop/vibecoding/to-vibe-cli`）完全共享：

| 目录/文件 | 共享影响 |
|-----------|----------|
| `.venv/` | ✅ 两个 session 跑同一个 venv，无冲突 |
| `src/` | ⚠️ 同时修改可能冲突，遵守分支策略可避免 |
| `.to-vibe/` | ⚠️ 运行时状态，可能被另一方覆盖（不影响代码） |
| `pyproject.toml` | ⚠️ 同时修改同一行会冲突 |

---

## 5. 避免冲突的习惯

### 每次开始新任务前同步

```bash
git checkout main
git pull origin main
git checkout -b feature/new-task
```

### push 前检查

```bash
git status
# 确认没有意外变更后再 push
git push
```

### 约定一方先 push

```
A 窗口: git push
B 窗口: 等 A 完成后（10-30秒），再 git push
```

---

## 6. 两个 session 的典型协作场景

### 场景一：TUI 开发和 LLM 模块并行

```
当前窗口（main）
  → 开发 tui/ 组件、pipeline 逻辑
  → commit 到 main 直接 push

第二个窗口（feature/tui-refactor）
  → 重构 tui/screens/ 结构
  → push 后通过 PR 合并到 main
```

### 场景二：调试和实现并行

```
当前窗口（main）
  → 运行 pytest / to-vibe 实际测试
  → 根据错误信息修复 bug

第二个窗口（feature/new-feature）
  → 实现新功能代码
  → 不动已通过测试的部分
```

---

## 7. 快速参考命令

```bash
# 查看当前 branch
git branch --show-current

# 新建并切换 branch
git checkout -b feature/xxx

# 切回 main
git checkout main

# 同步最新 main
git pull origin main

# 查看所有 branch
git branch -a

# 放弃本地变更（谨慎使用）
git checkout -- .
```

---

## 8. 注意事项

1. **不要同时对同一文件做冲突修改** — 一个窗口在写 `llm/client.py`，另一个同时也在写就会冲突
2. **SessionStart hook 行为** — 当前项目的 hook 可能会读取 `.to-vibe/` 状态，两个窗口同时触发可能有竞态，但不影响代码正确性
3. **commit message 风格** — 保持与项目一致的格式（conventional commits）
4. **不要在一方执行 `pip install` 时，另一方做 `git add .` 并 commit** — 可能把半安装状态的变更 commit 进去

---

## 9. 推荐的并行节奏

| 步骤 | 操作 |
|------|------|
| 1 | 第二个窗口新建 feature branch |
| 2 | 两个窗口各自明确分工（避免修改同一文件） |
| 3 | 每次 push 前 `git pull` 同步 |
| 4 | feature branch 完成 → 通过 GitHub PR 合并 |
| 5 | 合并后，当前窗口 `git checkout main && git pull` 同步 |

---

如遇冲突或不确定的情况，先 `git status` 再决定下一步操作。