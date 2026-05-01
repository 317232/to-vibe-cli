"""LearnPanel component showing learning module status."""

from __future__ import annotations

from dataclasses import dataclass
from textual.widgets import Static
from to_vibe.tui.styles import Colors


@dataclass
class LearnData:
    """Learn module data."""

    status: str = "pending"
    records: int = 0
    focus: str = ""
    source: str = ""


class LearnPanel(Static):
    """Learn panel showing current learning state."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._data: LearnData | None = None

    def set_data(self, data: LearnData) -> None:
        """Set learn data."""
        self._data = data
        self._update_display()

    def _update_display(self) -> None:
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

    def on_mount(self) -> None:
        self._update_display()
