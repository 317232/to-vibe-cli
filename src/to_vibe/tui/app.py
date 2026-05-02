"""Main Textual TUI application for to-vibe."""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding

from to_vibe.config import ToVibeConfig, load_config
from to_vibe.utils.logger import init_logger
from to_vibe.tui.screens.main_screen import MainScreen
from to_vibe.tui.state_store import TUIStateStore


# Textual theme variable defaults — exposed as $color-name in CSS
APP_THEME_VARIABLES = {
    "color-surface": "#0b1015",
    "color-surface-light": "#161b22",
    "color-text": "#cdd6f4",
    "color-text-muted": "#6c7086",
    "color-evidence": "#238636",
    "color-priority": "#d29922",
    "color-verify": "#da3633",
    "color-repair": "#1f6feb",
    "color-learn": "#a371f7",
    "color-pass": "#238636",
    "color-fail": "#da3633",
    "color-skip": "#d29922",
    "color-active": "#1f6feb",
    "color-info": "#238636",
    "color-warn": "#d29922",
    "color-error": "#da3633",
    "color-shortcut": "#d29922",
}


class ToVibeApp(App):
    """Main to-vibe TUI application."""

    CSS = """
    /* === Base === */
    Screen {
        background: $color-surface;
        color: $color-text;
    }

    /* === Main Layout === */
    #app-header {
        height: auto;
        padding: 0 8;
        background: $color-surface-light;
        border-bottom: solid $color-text-muted;
    }

    /* Tab bar below header */
    #tab-bar {
        height: 3;
        padding: 0 8;
        background: $color-surface-light;
        border-bottom: solid #30363d;
    }

    /* Tab buttons */
    .tab-btn {
        margin: 0 2;
        min-width: 16;
    }

    /* === Main 4:6 Split === */
    #chat-panel {
        width: 40%;
        border-right: solid #30363d;
    }

    #to-vibe-panel {
        width: 60%;
    }

    /* === ToVibe Bento Grid === */
    #bento-grid {
        height: 100%;
        layout: horizontal;
    }

    #left-col {
        width: 40%;
        layout: vertical;
        height: 100%;
    }

    #right-col {
        width: 60%;
        layout: vertical;
        height: 100%;
    }

    /* === Card Borders === */
    #evidence-card {
        border: solid $color-evidence;
        padding: 4 8;
        margin: 4;
        height: 1fr;
    }

    #priority-card {
        border: solid $color-priority;
        padding: 4 8;
        margin: 4;
        height: 1fr;
    }

    #verify-table {
        border: solid $color-verify;
        padding: 4 8;
        margin: 4;
        height: 1fr;
    }

    #learn-summary {
        border: solid $color-learn;
        padding: 4 8;
        margin: 4;
        height: auto;
    }

    /* === Stage Bar === */
    #stage-bar {
        height: 3;
        padding: 0 8;
        background: $color-surface-light;
        border-top: solid #30363d;
        border-bottom: solid #30363d;
    }

    /* === Logs Panel 3-Column === */
    #repair-panel {
        border: solid $color-repair;
        padding: 4 8;
        margin: 4;
        height: auto;
    }

    #logs-content {
        layout: horizontal;
        height: 1fr;
    }

    #log-stream {
        width: 60%;
        padding: 4 8;
        border-top: solid #30363d;
    }

    #log-filters {
        height: 3;
        padding: 0 8;
    }

    .log-filter-btn {
        margin: 0 2;
        min-width: 10;
    }

    #learn-panel {
        width: 20%;
        border: solid $color-learn;
        padding: 4 8;
        margin: 4;
        height: 100%;
    }

    #artifacts-panel {
        width: 20%;
        border: solid $color-learn;
        padding: 4 8;
        margin: 4;
        height: 100%;
    }

    /* === Learn Detail View === */
    #learn-detail {
        layout: grid;
        grid-size: 2 3;
        grid-columns: 1fr 1fr;
        padding: 4 8;
        height: 100%;
    }

    .learn-section {
        padding: 4;
        border: solid $color-learn;
        margin: 2;
    }

    /* === Footer === */
    #app-footer {
        height: 3;
        padding: 0 8;
        background: $color-surface-light;
        border-top: solid #30363d;
    }

    /* === Repair Panel Key-Value Grid === */
    .repair-grid {
        layout: grid;
        grid-size: 2 3;
        grid-columns: 1fr 1fr;
        width: 100%;
    }

    .repair-kv {
        padding: 0 4;
    }

    .repair-event {
        column-span: 2;
        padding: 0 4;
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

        # One shared store for all components
        self._store = TUIStateStore()

        self.title = "to-vibe"
        self.sub_title = str(self.project_path)

    def get_theme_variable_defaults(self) -> dict[str, str]:
        """Expose app-specific color variables to CSS via $color-name syntax."""
        return APP_THEME_VARIABLES

    def on_mount(self) -> None:
        """Handle mount event."""
        from to_vibe.tui.pipeline_integration import PipelineIntegration
        self.push_screen(MainScreen(self._store))
        self.integration = PipelineIntegration(project_path=self.project_path, store=self._store)
        self.integration.start()

    def action_switch_tab(self, direction: int) -> None:
        """Switch between tabs."""
        screen = self.screen
        if isinstance(screen, MainScreen):
            screen.switch_tab(direction)

    def action_pause(self) -> None:
        """Pause the pipeline."""
        if hasattr(self, 'integration'):
            self.integration.pause()
        self.notify("Pipeline paused — press Space to resume")

    def action_retry(self) -> None:
        """Retry the failed step."""
        if hasattr(self, 'integration'):
            self.integration.retry()
        self.notify("Retrying failed step...")

    def action_skip(self) -> None:
        """Skip the current stage."""
        if hasattr(self, 'integration'):
            self.integration.skip()
        self.notify("Skipping current stage...")
