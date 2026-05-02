"""VerifyTable component showing 5-layer verification status."""

from __future__ import annotations

from textual.widgets import Static
from to_vibe.tui.styles import Colors
from to_vibe.tui.state_store import VerifyRow, TUIStateStore


class VerifyTable(Static):
    """5-layer verification table (L1-L5)."""

    def __init__(self, store: TUIStateStore, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._store = store
        self._unsubscribe: callable | None = None
        self._rows: list[VerifyRow] = []

    def on_mount(self) -> None:
        self._unsubscribe = self._store.subscribe("verify", self._on_verify)
        self.set_rows(self._store.get_verify_rows())

    def on_unmount(self) -> None:
        if self._unsubscribe:
            self._unsubscribe()

    def _on_verify(self, rows: list[VerifyRow]) -> None:
        self.app.call_from_thread(self.set_rows, rows)

    def set_rows(self, rows: list[VerifyRow]) -> None:
        self._rows = rows
        self._update_display()

    def _update_display(self) -> None:
        lines = [
            f"[b]💢 Baseline Verify[/b] [{Colors.STAGE_VERIFY}]",
            "",
            f"[b]# Check         Status       Details / Command[/b]",
            f"{'─' * 60}",
        ]

        for row in self._rows:
            icon = self._get_icon(row.status)
            lines.append(f"{row.id}  {row.check:<14} {icon} {row.status:<8} {row.command}")

        self.update("\n".join(lines))

    def _get_icon(self, status: str) -> str:
        icons = {
            "pass": "[#238636]✅[/]",
            "fail": "[#da3633]❌[/]",
            "skip": "[#d29922]➡[/]",
            "running": "[#1f6feb]▶[/]",
        }
        return icons.get(status, "[#6c7086]?[/]")
