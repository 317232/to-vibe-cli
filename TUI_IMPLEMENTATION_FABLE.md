# to-vibe TUI 寓言·续

## —— 闸门未竟的最后一公里

---

### 闸门之城的现状

河流穿城而过，五道闸门已经建成。

远远望去：绿色守望者、黄色指挥官、红色验收官、蓝色整修工、紫色学习殿堂——全部在运转。

但走近一看，**城墙上还有四处缺口**。

守城的工匠们说：这四处在设计图上早就画好了，只是赶工时没来得及建。现在河流已经通航，这些缺口必须补上，否则**船只看不见航标，整修工不知道在哪里上岗，学习殿堂的门也没完全打开**。

---

## 缺口一：城墙上的旗杆

**模块：** `src/to_vibe/tui/screens/main_screen.py` — TabBar 改造

**故事：**

城墙上有三个凹槽，本来应该插**旗帜**——`1: claude`、`2: to-vibe`、`3: logs`。

但工匠们赶工时，用的是纸糊的旗子。远远看去好像有旗，但风吹就倒（实际渲染时完全看不见）。这三个凹槽叫 `TabBar`，用的是普通 Python 类，不是 Textual 认可的旗杆（Widget）。

船到港口，船员想："走哪条航道？" 却看不到任何旗帜告诉他们现在在哪条河段。

**修复方案：**

把纸糊的旗子换成真正的旗杆——继承 `textual.widget.Widget`，让它成为 Textual 认可的 UI 组件。旗帜应该有三种状态：

| 状态 | 样子 |
|------|------|
| 未激活 | 灰色文字 |
| 激活 | 橙色边框 + 橙色文字（`#d29922`） |
| 按下 `tab` | 切换到下一面旗 |

代码上，就是把：

```python
class TabBar:  # ← 普通类，不发光
    def __init__(self, tabs, labels): ...
```

改成：

```python
class TabBar(Static):  # ← 真正的 Widget，在 TUI 里发光
    BINDINGS = [("tab", "next_tab", "")]
    def compose(self): yield Tabs(...)  # 或自己画
```

> **寓言点睛：** 旗帜不是装饰，是**导航信号**。没有旗杆的旗帜等于没有旗帜。架构上这叫"**空有数据结构，没有 UI 实体**"。

---

## 缺口二：蓝色整修工的岗亭

**模块：** `src/to_vibe/tui/components/repair_panel.py`（新建）

**故事：**

蓝色整修工（`Repair Loop`）已经上岗了，但它**没有岗亭**。

验收官发现水质不合格，整修工就得动手。但它站在露天地里，没有结构化的位置牌告诉船员：
- 现在在整修什么问题（Selected issue）
- 用什么工具（Capability）
- 当前是试运行还是正式施工（Mode）
- 进行到第几轮了（Round）
- 下一步往哪走（Next）

船员们只能靠猜。

**岗亭设计方案（per TUI_DESIGN.md image3.1.png）：**

```
┌─ ◆ Repair Loop (dry-run) ─────────────────────────────────────┐
│                                                              │
│  Selected issue : P1 startup failure        Apply  : skipped │
│  Capability     : Debug                    Record : .to-vibe/ │
│  Mode           : dry-run                  Round  : 1 / 50    │
│  Next           : export Claude tasks or retry Verify         │
│                                                              │
│  ▷ Latest event : Baseline verification completed...  00:25:20 │
└──────────────────────────────────────────────────────────────┘
```

岗亭的职责是**展示 `RepairData`**，不负责施工——施工是 `RepairLoop` 的事。

岗亭订阅 `"repair"` 频道，一旦整修工更新状态，岗亭就刷新显示。

岗亭建在 **Logs Tab 的最顶部**，而不是 to-vibe 主面板——因为 Logs Tab 本来就是"过程审计视图"，整修过程属于审计范围。

> **寓言点睛：** 整修工不能没有岗亭，就如同验收结果不能没有整改记录。没有岗亭的整修工，是游兵散勇；没有 RepairPanel 的 Logs，是没有脊梁的视图。

---

## 缺口三：日志河流的入河口

**模块：** `src/to_vibe/tui/pipeline_integration.py` — `_LogStreamHandler` 接入

**故事：**

日志河流（`LogStream`）早就修好了，河道笔直、颜色分明——绿色的 INFO、红色的 ERROR、黄色的 WARN。

但问题是：**这条河还没有水**。

`LogStream` 订阅了 `TUIStateStore` 的 `"log"` 频道，但没有人往里面倒水。`PipelineEventBus` 里的 `info/warn/error` 调用像天上的雨，云层已经聚好，但还没有落到河里。

**问题出在哪里？**

`PipelineIntegration.__init__` 里有这行代码：

```python
PipelineEventBus.subscribe(_LogStreamHandler(self.store))
```

这行代码是对的——但它只在 `PipelineIntegration` 创建时订阅一次。关键是 `PipelineEventBus` **本身有没有真的发送事件**。

验证方法：运行 pipeline，看 `LogStream` 里有没有内容。如果全是空的，说明 `PipelineEventBus.stage_start/complete/info()` 调用了但**没有真正广播**。

两个可能的故障点：
1. `PipelineEventBus` 的 subscriber 列表是空的（没订阅成功）
2. 事件发了但 `_LogStreamHandler.__call__` 没被触发

**另一个缺口：** LogStream 上的**过滤按钮**（`[info]` `[error]` `[warning]` `[Clear]`）在设计图上有，但 `LogStream` 组件里没有实现。过滤按钮用来只显示特定级别的日志，这是船员排查问题时的得力工具。

> **寓言点睛：** 河道修好但没有水，叫**干河**。干河不是水利枢纽，是摆设。架构上这叫"**组件有了，但数据流没通**"。

---

## 缺口四：学习殿堂的门缝

**模块：** `src/to_vibe/tui/pipeline_integration.py` — learn stage 的 `detail_view` 传递

**故事：**

紫色学习殿堂（`LearnPanel`）有两扇门：

- **正门**（摘要视图）：永远开着，显示"来了多少人、积累了多少经验"
- **侧门**（详情视图）：按 `[详情]` 进去，里面有四间房——已验证修复、问题模式、项目事实、用户规则

问题是：**侧门是锁着的**。

船员走到侧门前，往里一看——门缝里透不出光。因为 `pipeline_integration.py` 里给侧门的钥匙是 `None`：

```python
self.store.update_learn(LearnData(
    status="completed",
    records=learn_result.items_learned,
    detail_view=None,  # ← 钥匙丢了，侧门打不开
    ...
))
```

工匠 `LegacyLearnCollector` 其实收集了完整的四间房数据，但把钥匙（`LearnDetailView`）装在口袋里没交出来。

**修复方案：**

在 learn stage 调用后，把 `collector.collect()` 的结果**展开成四间房**，再交给 store：

```python
collector = LegacyLearnCollector(self.project_path, config.learn)
learn_result = collector.collect()  # 有 verified_fixes, issue_patterns, ...

detail_view = LearnDetailView(
    verified_fixes=learn_result.verified_fixes or [],
    issue_patterns=learn_result.issue_patterns or [],
    project_facts=learn_result.project_facts or [],
    user_rules=learn_result.user_rules or [],
)
self.store.update_learn(LearnData(
    status="completed",
    records=learn_result.items_learned,
    detail_view=detail_view,  # ← 钥匙插进锁孔
    ...
))
```

这样，侧门就开了，船员可以按 `[A]` accept / `[E]` edit / `[R]` reject / `[P]` pin / `[D]` delete 来管理记忆。

> **寓言点睛：** 殿堂的门锁着，里面的宝贝再丰富也无人知晓。架构上这叫"**数据在，但传递路径断了**"。Learn Detail View 是人机协作闭环的关键——人必须能编辑机器生成的知识。

---

## 还差两步：Header 动态化 + Artifacts 空状态

这两件事不在 P0 核心路径上，但影响用户体验。

### Header：真实数据取代占位文字

当前 Header 可能是这样的：
```
◇ to-vibe | ~/dev/project         main  🕒 00:25:32
```

如果 `SessionData` 已经通过 `TUIStateStore` 的 `"session"` 频道注入了，这个应该自动变成真实数据。但需要确认 `Header.on_mount()` 里有没有写：

```python
self._unsubscribe = self._store.subscribe("session", self._on_session)
```

### Artifacts：空状态显示

`.to-vibe/` 目录还没有产物时，当前可能显示空白。应该显示：

```
No artifacts yet
```

让船员知道"还没有产物"，而不是误以为组件坏了。

---

## 竣工验收：四道缺口补完后

```bash
# 检查 TabBar 是否变成可见的 Widget（无报错即通过）
python -c "from textual.widgets import Static; from to_vibe.tui.screens.main_screen import TabBar; print('TabBar is Widget:', issubclass(TabBar, Static))"

# 检查 RepairPanel 是否存在
ls src/to_vibe/tui/components/repair_panel.py

# 检查 LogStream 是否有日志流入（需要实际运行）
to-vibe run /tmp/test-project 2>&1 | grep -c "\[INFO\]"

# 检查 Learn Detail View 是否传入了 detail_view
grep -n "detail_view=detail_view" src/to_vibe/tui/pipeline_integration.py

# 运行全部组件测试
pytest tests/test_components.py -v
```

**全部绿灯时，闸门之城就真正竣工了。**

---

## 五道闸门 · 全景回顾

补完四处缺口后，整座枢纽才算真正交付：

| 闸门 | 组件 | 状态 | 缺失 |
|------|------|------|------|
| 守望者 | EvidenceCard | ✅ | — |
| 指挥官 | PriorityCard | ✅ | — |
| 验收官 | VerifyTable | ✅ | — |
| 整修工 | RepairPanel | ❌ | **岗亭没建** |
| 学习殿堂 | LearnPanel | ✅ | **侧门锁着** |
| 日志河 | LogStream | ✅ | **河道干涸** |
| 阶段灯 | StageBar | ✅ | — |
| 导航旗 | TabBar | ⚠️ | **纸糊的** |

---

*闸门未竟，河流不畅。*
*补完这四道缺口，船只便能昼夜通行。*