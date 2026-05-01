"""Logs panel for log stream view (Tab 3)."""

from __future__ import annotations

from textual.widget import Widget


class LogsPanel(Widget):
    """Logs panel for log stream and artifact view."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
