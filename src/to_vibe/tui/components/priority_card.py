"""PriorityCard component showing Priority Report summary."""

from __future__ import annotations

from textual.widgets import Static
from to_vibe.tui.styles import Colors
from to_vibe.tui.state_store import PriorityData, TUIStateStore


class PriorityCard(Static):
    """Priority card showing issue counts and top issue."""

    def __init__(self, store: TUIStateStore, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._store = store
        self._unsubscribe: callable | None = None
        self._data: PriorityData | None = None

    def on_mount(self) -> None:
        self._unsubscribe = self._store.subscribe("priority", self._on_priority)
        self.set_data(self._store.get_priority())

    def on_unmount(self) -> None:
        if self._unsubscribe:
            self._unsubscribe()

    def _on_priority(self, data: PriorityData) -> None:
        self.app.call_from_thread(self.set_data, data)

    def set_data(self, data: PriorityData) -> None:
        self._data = data
        self._update_display()

    def _update_display(self) -> None:
        if not self._data:
            self.update("[Priority Report]\nNo data")
            return

        lines = [
            f"[b]◆ Priority Report[/b] [{Colors.STAGE_PRIORITY}]",
            "",
            f"Blockers        : {self._data.blockers}",
            f"High            : {self._data.high}",
            f"Medium          : {self._data.medium}",
            f"Top issue       : {self._data.top_issue}",
            f"Suggested       : {self._data.suggested_capability}",
        ]
        self.update("\n".join(lines))
