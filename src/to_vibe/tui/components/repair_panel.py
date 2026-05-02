"""RepairPanel component showing Repair Loop state at top of LogsPanel."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from to_vibe.tui.state_store import TUIStateStore
from to_vibe.tui.state_models import RepairData


class RepairPanel(Widget):
    """Repair panel showing current repair loop state.

    Displayed at the top of LogsPanel — shows selected issue,
    capability, mode, apply status, record path, next action,
    and latest event/timestamp.

    Layout (per TUI_DESIGN.md):
    ┌──────────────────────────────────────────────────────────┐
    │ ▶ Selected : issue  | Cap : capability                   │
    │   Mode : mode      | Apply : status                     │
    │   Record : path    | Next : action                      │
    │ ▶ Latest : event @ timestamp                            │
    └──────────────────────────────────────────────────────────┘
    """

    def __init__(self, store: TUIStateStore, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._store = store
        self._unsubscribe: callable | None = None
        self._data: RepairData | None = None

    def on_mount(self) -> None:
        self._unsubscribe = self._store.subscribe("repair", self._on_repair)

    def on_unmount(self) -> None:
        if self._unsubscribe:
            self._unsubscribe()

    def _on_repair(self, data: RepairData) -> None:
        self.app.call_from_thread(self._apply_data, data)

    def _apply_data(self, data: RepairData) -> None:
        self._data = data
        self._update_display()

    def _update_display(self) -> None:
        if not self._data:
            self.update("[Repair Loop]\nNo data")
            return

        # Key-value pairs in 2-column grid layout
        issue = self._data.selected_issue or "—"
        cap = self._data.capability or "—"
        mode = self._data.mode
        apply = self._data.apply
        record = self._data.record
        next_action = self._data.next_action or "—"
        latest_event = self._data.latest_event or "—"
        latest_time = self._data.latest_time or "—"

        lines = [
            "[b]◆ Repair Loop[/b]",
            "",
            f"▶  Selected  : {issue}  |  Cap : {cap}",
            f"   Mode      : {mode}   |  Apply : {apply}",
            f"   Record    : {record}  |  Next : {next_action}",
            f"▶  Latest    : {latest_event}  @ {latest_time}",
        ]
        self.update("\n".join(lines))