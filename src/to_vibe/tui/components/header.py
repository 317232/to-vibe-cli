"""Header component showing session info."""

from __future__ import annotations

from datetime import datetime
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static
from to_vibe.tui.state_store import TUIStateStore


class Header(Static):
    """Header widget showing brand, path, git branch, timer, and full command info."""

    def __init__(self, store: TUIStateStore, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._store = store
        self._unsubscribe: callable | None = None
        self._start_time = datetime.now()
        self._header_text: Static | None = None

    def compose(self) -> ComposeResult:
        self._header_text = Static(id="header-text")
        yield self._header_text

    def on_mount(self) -> None:
        self._unsubscribe = self._store.subscribe("session", self._on_session)
        self._update_content()

    def on_unmount(self) -> None:
        if self._unsubscribe:
            self._unsubscribe()

    def _on_session(self, session) -> None:
        self.app.call_from_thread(self._update_content, session)

    def _update_content(self, session=None) -> None:
        if not self._header_text:
            return

        elapsed = datetime.now() - self._start_time
        total_seconds = int(elapsed.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        timer = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        if session is None:
            session = self._store.get_session()

        # Per TUI_DESIGN.md layout:
        # ◇ to-vibe | ~/dev/library_system         main  🕒 00:25:32
        # $ to-vibe run ./project
        # Project     : ./library_system
        # Mode        : dry-run
        # Executor    : local / claude-code
        # Pipeline    : Evidence → Priority → Verify → Repair → Learn
        # Note        : Learn runs after pipeline completion; Ship is out of current scope

        project_path = session.project_path or "."
        mode = session.mode or "dry-run"
        executor = session.executor or "local"

        # First line: brand + path + timer
        line1 = f"[b]◇ to-vibe[/b]  |  {project_path}  |  [b]{timer}[/b]"

        # Build header content
        lines = [
            line1,
            "",
            f"Project  : {project_path}",
            f"Mode     : {mode}",
            f"Executor : {executor}",
            "Pipeline : Evidence → Priority → Verify → Repair → Learn",
            "Note     : Learn runs after pipeline completion; Ship is out of scope",
        ]
        self._header_text.update("\n".join(lines))