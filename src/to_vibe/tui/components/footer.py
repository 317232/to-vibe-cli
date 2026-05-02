"""Footer component showing executor info and keyboard shortcuts."""

from __future__ import annotations

from textual.widgets import Static
from to_vibe.tui.state_store import TUIStateStore


class Footer(Static):
    """Footer showing executor info and shortcut hints."""

    def __init__(self, store: TUIStateStore, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._store = store
        self._unsubscribe: callable | None = None

    def on_mount(self) -> None:
        self._unsubscribe = self._store.subscribe("session", self._on_session)
        self._update_content()

    def on_unmount(self) -> None:
        if self._unsubscribe:
            self._unsubscribe()

    def _on_session(self, session) -> None:
        self.app.call_from_thread(self._update_content, session)

    def _update_content(self, session=None) -> None:
        if session is None:
            session = self._store.get_session()

        left = f"[#d29922]{session.project_path}[/] | {session.mode}"
        middle = f"[#6c7086]⟳[/] Executor: {session.executor}"
        right = "[#d29922][Space][/]暂停  [#d29922][R][/]重试  [#d29922][S][/]跳过  [↑↓]滚动"
        self.update(f"{left}  |  {middle}  |  {right}")
