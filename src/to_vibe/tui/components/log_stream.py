"""LogStream component showing real-time log entries."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static, Button
from to_vibe.tui.state_store import TUIStateStore
from to_vibe.tui.state_models import LogEntry


class LogStream(Static):
    """Log stream widget with auto-scroll and filtering."""

    def __init__(self, store: TUIStateStore, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._store = store
        self._unsubscribe: callable | None = None
        self._entries: list[LogEntry] = []
        self._filter: str | None = None
        self._log_text: Static | None = None

    def compose(self) -> ComposeResult:
        """Yield filter bar + log content."""
        filter_bar = Horizontal(
            Button("all", id="filter-all", classes="log-filter-btn", variant="primary"),
            Button("info", id="filter-info", classes="log-filter-btn"),
            Button("warn", id="filter-warn", classes="log-filter-btn"),
            Button("error", id="filter-error", classes="log-filter-btn"),
            Button("Clear", id="filter-clear", classes="log-filter-btn"),
            id="log-filters",
        )
        self._log_text = Static(id="log-text")
        yield filter_bar
        yield self._log_text

    def on_mount(self) -> None:
        self._unsubscribe = self._store.subscribe("log", self._on_log)
        self._update_display()

    def on_unmount(self) -> None:
        if self._unsubscribe:
            self._unsubscribe()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle filter button presses."""
        btn_id = event.button.id
        if btn_id == "filter-all":
            self._filter = None
            self._set_active("filter-all")
        elif btn_id == "filter-info":
            self._filter = "INFO"
            self._set_active("filter-info")
        elif btn_id == "filter-warn":
            self._filter = "WARN"
            self._set_active("filter-warn")
        elif btn_id == "filter-error":
            self._filter = "ERROR"
            self._set_active("filter-error")
        elif btn_id == "filter-clear":
            self._entries = []
        self._update_display()

    def _set_active(self, active_id: str) -> None:
        for btn in self.query("Button"):
            btn.variant = "primary" if btn.id == active_id else "default"

    def _on_log(self, entry: LogEntry) -> None:
        self.app.call_from_thread(self._add_entry, entry)

    def _add_entry(self, entry: LogEntry) -> None:
        self._entries.append(entry)
        if len(self._entries) > 500:
            self._entries = self._entries[-500:]
        self._update_display()

    def _update_display(self) -> None:
        if not self._log_text:
            return
        lines = []
        for entry in self._entries[-100:]:
            if self._filter and entry.level != self._filter:
                continue
            level_tag = self._get_level_tag(entry.level)
            lines.append(f"{entry.timestamp} {level_tag} {entry.message}")

        self._log_text.update("\n".join(lines) if lines else "No logs")

    def _get_level_tag(self, level: str) -> str:
        colors = {
            "INFO": "[#238636][INFO][/]",
            "WARN": "[#d29922][WARN][/]",
            "ERROR": "[#da3633][ERROR][/]",
        }
        return colors.get(level, f"[{level}]")