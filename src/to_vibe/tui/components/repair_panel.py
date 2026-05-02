"""RepairPanel component showing Repair Loop state at top of LogsPanel."""

from __future__ import annotations

from textual.widgets import Static
from to_vibe.tui.state_store import TUIStateStore
from to_vibe.tui.state_models import RepairData


class RepairPanel(Static):
    """Repair panel showing current repair loop state.

    Displayed at the top of LogsPanel — shows selected issue,
    capability, mode, apply status, record path, next action,
    and latest event/timestamp.
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

        lines = [
            "[b]◆ Repair Loop[/b]",
            "",
            f"Issue    : {self._data.selected_issue or '—'}",
            f"Cap      : {self._data.capability or '—'}",
            f"Mode     : {self._data.mode}",
            f"Apply    : {self._data.apply}",
            f"Record   : {self._data.record}",
            f"Next     : {self._data.next_action or '—'}",
            f"Event    : {self._data.latest_event or '—'}",
            f"Time     : {self._data.latest_time or '—'}",
        ]
        self.update("\n".join(lines))
