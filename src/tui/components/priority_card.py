"""PriorityCard component showing Priority Report summary."""

from __future__ import annotations

from dataclasses import dataclass
from textual.widgets import Static
from to_vibe.tui.styles import Colors


@dataclass
class PriorityData:
    """Priority Report data."""

    blockers: int = 0
    high: int = 0
    medium: int = 0
    top_issue: str = ""
    suggested_capability: str = ""


class PriorityCard(Static):
    """Priority card showing issue counts and top issue."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._data: PriorityData | None = None

    def set_data(self, data: PriorityData) -> None:
        """Set priority data."""
        self._data = data
        self._update_display()

    def _update_display(self) -> None:
        if not self._data:
            self.update("[Priority Report]\nNo data")
            return

        lines = [
            f"[b]Priority Report[/b] [{Colors.STAGE_PRIORITY}]",
            f"",
            f"[b]Blockers:[/b] {self._data.blockers}",
            f"[b]High:[/b] {self._data.high}",
            f"[b]Medium:[/b] {self._data.medium}",
            f"",
            f"[b]Top Issue:[/b] {self._data.top_issue}",
            f"[b]Capability:[/b] {self._data.suggested_capability}",
        ]
        self.update("\n".join(lines))

    def on_mount(self) -> None:
        self._update_display()
