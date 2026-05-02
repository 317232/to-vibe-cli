"""Artifacts component showing generated files and directories."""

from __future__ import annotations

from textual.widgets import Static
from to_vibe.tui.state_store import ArtifactItem, TUIStateStore


class Artifacts(Static):
    """Artifacts panel showing generated files."""

    def __init__(self, store: TUIStateStore, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._store = store
        self._unsubscribe: callable | None = None
        self._items: list[ArtifactItem] = []

    def on_mount(self) -> None:
        self._unsubscribe = self._store.subscribe("artifacts", self._on_artifacts)

    def on_unmount(self) -> None:
        if self._unsubscribe:
            self._unsubscribe()

    def _on_artifacts(self, items: list[ArtifactItem]) -> None:
        self.app.call_from_thread(self._apply_items, items)

    def _apply_items(self, items: list[ArtifactItem]) -> None:
        self._items = items
        self._update_display()

    def _update_display(self) -> None:
        lines = ["[b]Artifacts[/b]", ""]
        for item in self._items:
            icon = "[📁]" if item.is_directory else "[·]"
            lines.append(f"{icon} {item.name}")
        self.update("\n".join(lines) if lines else "No artifacts")
