"""Structured logging for to-vibe."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, TextIO

from to_vibe.config import UIConfig


class LogLevel(Enum):
    """Log level enumeration."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

    def __lt__(self, other: LogLevel) -> bool:
        order = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR]
        return order.index(self) < order.index(other)


@dataclass
class LogEntry:
    """Single log entry."""

    timestamp: str
    level: LogLevel
    text: str
    stage: str | None = None
    session_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "level": self.level.value,
            "text": self.text,
            "stage": self.stage,
            "session_id": self.session_id,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LogEntry:
        """Create from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            level=LogLevel(data["level"]),
            text=data["text"],
            stage=data.get("stage"),
            session_id=data.get("session_id"),
        )


class LogEmitter:
    """Central log emitter that broadcasts to multiple destinations."""

    def __init__(
        self,
        output: TextIO | None = None,
        log_dir: Path | None = None,
        ui_config: UIConfig | None = None,
    ) -> None:
        self._output = output or sys.stdout
        self._log_dir = log_dir
        self._session_id: str | None = None
        self._current_stage: str | None = None
        self._ui_config = ui_config or UIConfig()
        self._handlers: list[callable] = []

    def set_session_id(self, session_id: str) -> None:
        """Set the current session ID."""
        self._session_id = session_id

    def set_stage(self, stage: str | None) -> None:
        """Set the current pipeline stage."""
        self._current_stage = stage

    def add_handler(self, handler: callable) -> None:
        """Add a handler function to receive log entries."""
        self._handlers.append(handler)

    def emit(
        self,
        text: str,
        level: LogLevel = LogLevel.INFO,
        stage: str | None = None,
    ) -> LogEntry:
        """Emit a log entry.

        Args:
            text: Log message text
            level: Log severity level
            stage: Optional pipeline stage name

        Returns:
            Created LogEntry instance
        """
        entry = LogEntry(
            timestamp=datetime.now().isoformat(timespec="milliseconds"),
            level=level,
            text=text,
            stage=stage or self._current_stage,
            session_id=self._session_id,
        )

        # Write to output
        self._output.write(entry.to_json() + "\n")
        self._output.flush()

        # Write to file if log_dir is set
        if self._log_dir is not None:
            self._write_to_file(entry)

        # Notify handlers
        for handler in self._handlers:
            handler(entry)

        return entry

    def debug(self, text: str, stage: str | None = None) -> LogEntry:
        """Emit debug log."""
        return self.emit(text, LogLevel.DEBUG, stage)

    def info(self, text: str, stage: str | None = None) -> LogEntry:
        """Emit info log."""
        return self.emit(text, LogLevel.INFO, stage)

    def warning(self, text: str, stage: str | None = None) -> LogEntry:
        """Emit warning log."""
        return self.emit(text, LogLevel.WARNING, stage)

    def error(self, text: str, stage: str | None = None) -> LogEntry:
        """Emit error log."""
        return self.emit(text, LogLevel.ERROR, stage)

    def _write_to_file(self, entry: LogEntry) -> None:
        """Write log entry to file."""
        if self._log_dir is None:
            return

        self._log_dir.mkdir(parents=True, exist_ok=True)
        log_file = self._log_dir / "to-vibe.log"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry.to_json() + "\n")


# Global logger instance
_logger: LogEmitter | None = None


def get_logger() -> LogEmitter:
    """Get the global logger instance.

    Returns:
        Global LogEmitter instance
    """
    global _logger
    if _logger is None:
        _logger = LogEmitter()
    return _logger


def init_logger(
    output: TextIO | None = None,
    log_dir: Path | None = None,
    ui_config: UIConfig | None = None,
) -> LogEmitter:
    """Initialize the global logger.

    Args:
        output: Output stream (defaults to stdout)
        log_dir: Directory for log files
        ui_config: UI configuration for log levels

    Returns:
        Initialized LogEmitter instance
    """
    global _logger
    _logger = LogEmitter(output=output, log_dir=log_dir, ui_config=ui_config)
    return _logger