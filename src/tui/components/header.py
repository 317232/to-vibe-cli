"""Header component showing session info."""

from __future__ import annotations

from datetime import datetime

from textual.widgets import Static


class Header(Static):
    """Header widget showing brand, path, git branch, and timer."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._start_time = datetime.now()

    def on_mount(self) -> None:
        """Handle mount event to set initial content."""
        self._update_content()

    def _update_content(self) -> None:
        """Update the header content."""
        elapsed = datetime.now() - self._start_time
        minutes = int(elapsed.total_seconds() // 60)
        seconds = int(elapsed.total_seconds() % 60)
        timer = f"{minutes:02d}:{seconds:02d}"

        self.update(f"[b]to-vibe[/b]  |  session: active  |  timer: {timer}")

    def watch_time(self) -> None:
        """Update timer display."""
        self._update_content()
