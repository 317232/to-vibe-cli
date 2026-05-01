"""Main Textual TUI application for to-vibe."""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding

from to_vibe.config import ToVibeConfig, load_config
from to_vibe.utils.logger import init_logger
from to_vibe.tui.screens.main_screen import MainScreen


class ToVibeApp(App):
    """Main to-vibe TUI application."""

    CSS = """
    Screen {
        background: $surface;
    }
    """

    BINDINGS = [
        Binding("tab", "switch_tab(1)", "Tab 1", show=False),
        Binding("shift+tab", "switch_tab(-1)", "Tab", show=False),
        Binding("space", "pause", "暂停", show=False),
        Binding("r", "retry", "重试", show=False),
        Binding("s", "skip", "跳过", show=False),
    ]

    def __init__(
        self,
        project_path: str | Path = ".",
        config: ToVibeConfig | None = None,
        *args: object,
        **kwargs: object,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.project_path = Path(project_path)
        self.config = config or load_config(str(self.project_path))

        # Initialize logger
        log_dir = self.project_path / ".to-vibe"
        init_logger(log_dir=log_dir, ui_config=self.config.ui)

        self.title = "to-vibe"
        self.sub_title = str(self.project_path)

    def on_mount(self) -> None:
        """Handle mount event."""
        self.push_screen(MainScreen())

    def action_switch_tab(self, direction: int) -> None:
        """Switch between tabs.

        Args:
            direction: 1 for next, -1 for previous
        """
        screen = self.screen
        if isinstance(screen, MainScreen):
            screen.switch_tab(direction)

    def action_pause(self) -> None:
        """Pause the current flow."""
        self.notify("Pipeline paused — press Space to resume")

    def action_retry(self) -> None:
        """Retry the failed step."""
        self.notify("Retrying failed step...")

    def action_skip(self) -> None:
        """Skip the current stage."""
        self.notify("Skipping current stage...")
