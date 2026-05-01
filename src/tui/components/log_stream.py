"""LogStream component showing real-time log entries."""

from __future__ import annotations

from textual.widgets import Static

from to_vibe.utils.logger import LogEntry, LogLevel


class LogStream(Static):
    """Log stream widget with auto-scroll and filtering."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._entries: list[LogEntry] = []
        self._filter: LogLevel | None = None

    def add_entry(self, entry: LogEntry) -> None:
        """Add a log entry."""
        self._entries.append(entry)
        if self._filter is None or entry.level == self._filter:
            self._update_display()

    def set_filter(self, level: LogLevel | None) -> None:
        """Set log level filter."""
        self._filter = level
        self._update_display()

    def clear(self) -> None:
        """Clear log entries."""
        self._entries = []
        self._update_display()

    def _update_display(self) -> None:
        lines = []
        for entry in self._entries[-100:]:
            if self._filter and entry.level != self._filter:
                continue
            level_tag = f"[{entry.level.value}]"
            lines.append(f"{entry.timestamp} {level_tag} {entry.text}")

        self.update("\n".join(lines) if lines else "No logs")

    def on_mount(self) -> None:
        self._update_display()
