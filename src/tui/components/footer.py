"""Footer component showing executor info and keyboard shortcuts."""

from __future__ import annotations

from textual.widgets import Static


class Footer(Static):
    """Footer showing executor info and shortcut hints."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)

    def on_mount(self) -> None:
        """Handle mount event."""
        self._update_content()

    def _update_content(self) -> None:
        """Update footer content."""
        shortcuts = "[Space]暂停  [R]重试  [S]跳过  [↑↓]滚动  [Tab]切换"
        executor = "executor: ready"
        self.update(f"{executor}  |  {shortcuts}")
