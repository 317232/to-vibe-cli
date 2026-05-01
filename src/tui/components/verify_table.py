"""VerifyTable component showing 5-layer verification status."""

from __future__ import annotations

from dataclasses import dataclass
from textual.widgets import Static
from to_vibe.tui.styles import Colors


@dataclass
class VerifyRow:
    """Single verification layer row."""

    id: str
    check: str
    status: str
    command: str = ""


class VerifyTable(Static):
    """5-layer verification table (L1-L5)."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._rows: list[VerifyRow] = []

    def set_rows(self, rows: list[VerifyRow]) -> None:
        """Set verification rows."""
        self._rows = rows
        self._update_display()

    def _update_display(self) -> None:
        lines = [f"[b]Baseline Verify[/b] [{Colors.STAGE_VERIFY}]", ""]

        for row in self._rows:
            icon = self._get_icon(row.status)
            lines.append(f"{icon} [b]{row.id}:[/b] {row.check}")
            if row.command:
                lines.append(f"   Command: {row.command}")

        self.update("\n".join(lines))

    def _get_icon(self, status: str) -> str:
        icons = {
            "pass": "[#a6e3a1]✓[/]",
            "fail": "[#f38ba8]✗[/]",
            "skip": "[#6c7086]⊘[/]",
            "running": "[#f9e2af]▶[/]",
        }
        return icons.get(status, "[#6c7086]?[/]")

    def on_mount(self) -> None:
        self._update_display()
