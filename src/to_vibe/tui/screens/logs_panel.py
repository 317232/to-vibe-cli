"""Logs panel (Tab 3) — RepairPanel + 3-column: LogStream + LearnPanel + Artifacts."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget

from to_vibe.tui.components.log_stream import LogStream
from to_vibe.tui.components.learn_panel import LearnPanel
from to_vibe.tui.components.artifacts import Artifacts
from to_vibe.tui.components.repair_panel import RepairPanel
from to_vibe.tui.state_store import TUIStateStore


class LogsPanel(Widget):
    """Logs panel with RepairPanel on top + 3-column layout below.

    Layout:
    ┌──────────────────────────────────────────────────────────┐
    │  RepairPanel (full width, collapsible)                    │
    ├──────────────────────────┬──────────────┬───────────────┤
    │ LogStream (60%)          │ Learn (20%)  │ Artifacts(20%)│
    └──────────────────────────┴──────────────┴───────────────┘
    """

    def __init__(self, store: TUIStateStore, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._store = store

    def compose(self) -> ComposeResult:
        """Compose RepairPanel at top, then 3-column layout."""
        yield RepairPanel(self._store, id="repair-panel")
        yield LogStream(self._store, id="log-stream")
        yield LearnPanel(self._store, id="learn-panel")
        yield Artifacts(self._store, id="artifacts-panel")
