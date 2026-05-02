"""LearnPanel component showing learning module status and detail view."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.message import Message
from textual.widgets import Static, Button
from to_vibe.tui.styles import Colors
from to_vibe.tui.state_store import TUIStateStore
from to_vibe.tui.state_models import LearnData, LearnDetailView


class LearnPanel(Container):
    """Learn panel with summary view + [详情] button to expand detail."""

    BINDINGS = [
        ("escape", "return", "Return"),
    ]

    def __init__(self, store: TUIStateStore, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._store = store
        self._unsubscribe: callable | None = None
        self._data: LearnData | None = None
        self._detail_view: LearnDetailView | None = None
        self._text_widget: Static | None = None
        self._detail_button: Button | None = None

    def compose(self) -> ComposeResult:
        self._text_widget = Static(id="learn-text")
        self._detail_button = Button("[详情]", id="learn-detail-btn", variant="primary")
        yield Vertical(self._text_widget, self._detail_button)

    def on_mount(self) -> None:
        self._unsubscribe = self._store.subscribe("learn", self._on_learn)
        self.set_data(self._store.get_learn())

    def on_unmount(self) -> None:
        if self._unsubscribe:
            self._unsubscribe()

    def _on_learn(self, data: LearnData) -> None:
        self.app.call_from_thread(self.set_data, data)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle [详情] button press."""
        if event.button.id == "learn-detail-btn":
            self._show_detail()

    def set_data(self, data: LearnData) -> None:
        self._data = data
        self._detail_view = data.detail_view
        self._update_display()

    def _show_detail(self) -> None:
        if self._data:
            self._data.is_detail = True
        if self._detail_button:
            self._detail_button.display = False
        self._update_display()

    def action_return(self) -> None:
        if self._data:
            self._data.is_detail = False
            if self._detail_button:
                self._detail_button.display = True
            self._update_display()

    def _update_display(self) -> None:
        if self._data and self._data.is_detail:
            self._render_detail()
        else:
            self._render_summary()

    def _render_summary(self) -> None:
        if not self._data or not self._text_widget:
            return
        lines = [
            f"[b]◆ Learn Module[/b] [{Colors.STAGE_LEARN}]",
            "",
            f"Status          : {self._data.status}",
            f"Records         : {self._data.records}",
            f"Focus           : {self._data.focus}",
            f"Source          : {self._data.source}",
        ]
        self._text_widget.update("\n".join(lines))

    def _render_detail(self) -> None:
        if not self._detail_view or not self._text_widget:
            return
        lines = [
            f"[b]Learn Detail View[/b] [{Colors.STAGE_LEARN}]",
            "",
            "[b]Verified Fixes[/b]",
        ]
        for item in self._detail_view.verified_fixes:
            pinned = " 📌" if item.get("pinned") else ""
            status_icon = "✅" if item.get("verify_status") == "passed" else "⏳"
            lines.append(f"  {status_icon} {item.get('title', '')}{pinned}")
            lines.append(f"      {item.get('summary', '')}")
        lines.extend(["", "[b]Issue Patterns[/b]"])
        for item in self._detail_view.issue_patterns:
            pinned = " 📌" if item.get("pinned") else ""
            lines.append(f"  • {item.get('title', '')}{pinned}")
            lines.append(f"      {item.get('summary', '')}")
        lines.extend(["", "[b]Project Facts[/b]"])
        for item in self._detail_view.project_facts:
            lines.append(f"  ▸ {item.get('title', '')}")
        lines.extend(["", "[b]User Rules[/b]"])
        for item in self._detail_view.user_rules:
            pinned = " 📌" if item.get("pinned") else ""
            lines.append(f"  ★ {item.get('title', '')}{pinned}")
        lines.extend(["", "[Esc] 返回"])
        self._text_widget.update("\n".join(lines))


class LearnAction(Message):
    """Message emitted when user takes an action on a learn record."""

    def __init__(self, action: str, panel: LearnPanel) -> None:
        super().__init__()
        self.action = action
        self.panel = panel





class LearnAction(Message):
    """Message emitted when user takes an action on a learn record."""

    def __init__(self, action: str, panel: LearnPanel) -> None:
        super().__init__()
        self.action = action
        self.panel = panel
