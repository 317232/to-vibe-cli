"""LearnPanel component showing learning module status and detail view."""

from __future__ import annotations

from typing import Any
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.message import Message
from textual.widgets import Static, Button
from to_vibe.tui.styles import Colors
from to_vibe.tui.state_store import TUIStateStore
from to_vibe.tui.state_models import LearnData, LearnDetailView


class LearnPanel(Container):
    """Learn panel with summary view + [详情] button to expand detail.

    Detail view layout (per TUI_DESIGN.md 2x2 grid):
    ┌─────────────────────────┬────────────────────────────────┐
    │ Verified Fixes           │ Issue Patterns                 │
    ├─────────────────────────┼────────────────────────────────┤
    │ Project Facts           │ User Rules                     │
    └─────────────────────────┴────────────────────────────────┘
    """

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
        self._detail_grid: Container | None = None

    def compose(self) -> ComposeResult:
        self._text_widget = Static(id="learn-text")
        self._detail_button = Button("[详情]", id="learn-detail-btn", variant="primary")
        self._detail_grid = Container(id="learn-detail-grid")
        self._detail_grid.display = False
        yield Vertical(self._text_widget, self._detail_button, self._detail_grid)

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
            f"Status : {self._data.status}",
            f"Records: {self._data.records}",
            f"Focus  : {self._data.focus}",
            f"Source : {self._data.source}",
        ]
        self._text_widget.update("\n".join(lines))
        if self._detail_grid:
            self._detail_grid.display = False
        if self._text_widget:
            self._text_widget.display = True

    def _render_detail(self) -> None:
        if not self._detail_view:
            return

        if self._text_widget:
            self._text_widget.display = False
        if self._detail_grid:
            self._detail_grid.remove_children()
            self._detail_grid.display = True

            # Build 2x2 grid: Verified Fixes | Issue Patterns
            #                   Project Facts | User Rules
            fixes = self._render_section("Verified Fixes", self._detail_view.verified_fixes, Colors.STAGE_LEARN)
            patterns = self._render_section("Issue Patterns", self._detail_view.issue_patterns, Colors.STAGE_LEARN)
            facts = self._render_section("Project Facts", self._detail_view.project_facts, Colors.STAGE_LEARN)
            rules = self._render_section("User Rules", self._detail_view.user_rules, Colors.STAGE_LEARN)

            # Top row: Verified Fixes (left) | Issue Patterns (right)
            top_row = Horizontal(fixes, patterns, id="detail-top-row")
            # Bottom row: Project Facts (left) | User Rules (right)
            bottom_row = Horizontal(facts, rules, id="detail-bottom-row")

            self._detail_grid.mount(top_row, bottom_row)

    def _render_section(self, title: str, items: list[dict[str, Any]], color: str) -> Container:
        """Render a single section card with title + list items."""
        content_lines = [f"[b]{title}[/b]", ""]
        for item in items[:5]:  # Limit to 5 items per section
            pinned = " 📌" if item.get("pinned") else ""
            status_icon = ""
            if title == "Verified Fixes":
                status_icon = "✅" if item.get("verify_status") == "passed" else "⏳"
            elif title == "User Rules":
                status_icon = "★"
            else:
                status_icon = "•"
            content_lines.append(f"{status_icon} {item.get('title', '')}{pinned}")
            summary = item.get("summary", "")
            if summary:
                content_lines.append(f"   {summary[:40]}")

        card = Container(
            Static("\n".join(content_lines), id=f"section-{title.lower().replace(' ', '-')}"),
            classes="learn-section",
        )
        return card