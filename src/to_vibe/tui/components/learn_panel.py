"""LearnPanel component showing learning module status and detail view."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from textual.widgets import Static
from to_vibe.tui.styles import Colors


@dataclass
class LearnData:
    """Learn module data."""

    status: str = "pending"
    records: int = 0
    focus: str = "Patterns & fixes"
    source: str = "Verified issues"
    detail_view: Any = None
    is_detail: bool = False


class LearnPanel(Static):
    """Learn panel showing current learning state with [详情] expansion."""

    BINDINGS = [
        ("a", "accept", "Accept"),
        ("e", "edit", "Edit"),
        ("r", "reject", "Reject"),
        ("p", "pin", "Pin"),
        ("d", "delete", "Delete"),
        ("escape", "return", "Return"),
    ]

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._data: LearnData | None = None
        self._detail_view: Any = None

    def set_data(self, data: LearnData) -> None:
        """Set learn data."""
        self._data = data
        self._update_display()

    def set_detail_view(self, view: Any) -> None:
        """Set the detail view data."""
        self._detail_view = view

    def show_detail(self) -> None:
        """Switch to detail view."""
        if self._data:
            self._data.is_detail = True
        self._update_display()

    def _update_display(self) -> None:
        if self._data and self._data.is_detail:
            self._render_detail()
        else:
            self._render_summary()

    def _render_summary(self) -> None:
        if not self._data:
            self.update("[Learn Module]\nNo data")
            return

        lines = [
            f"[b]Learn Module[/b] [{Colors.STAGE_LEARN}]",
            f"",
            f"[b]Status:[/b] {self._data.status}",
            f"[b]Records:[/b] {self._data.records}",
            f"[b]Focus:[/b] {self._data.focus}",
            f"[b]Source:[/b] {self._data.source}",
            "",
            "[b][详情][/b]",
        ]
        self.update("\n".join(lines))

    def _render_detail(self) -> None:
        """Render the expanded detail view with 4 categories."""
        if not self._detail_view:
            self.update("[Learn Module]\nNo detail data")
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

        lines.extend([
            "",
            "[b]操作:[/b] [A]accept  [E]edit  [R]reject  [P]pin  [D]delete  [Esc]返回",
        ])

        self.update("\n".join(lines))

    def action_accept(self) -> None:
        self._emit_action("accept")

    def action_reject(self) -> None:
        self._emit_action("reject")

    def action_edit(self) -> None:
        self._emit_action("edit")

    def action_pin(self) -> None:
        self._emit_action("pin")

    def action_delete(self) -> None:
        self._emit_action("delete")

    def action_return(self) -> None:
        if self._data:
            self._data.is_detail = False
            self._update_display()

    def _emit_action(self, action: str) -> None:
        from textual.message import Message
        self.post_message(LearnAction(action, self))

    def on_mount(self) -> None:
        self._update_display()


class LearnAction(Message):
    """Message emitted when user takes an action on a learn record."""

    def __init__(self, action: str, panel: LearnPanel) -> None:
        super().__init__()
        self.action = action
        self.panel = panel