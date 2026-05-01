"""Artifacts component showing generated files and directories."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from textual.widgets import Static


@dataclass
class ArtifactItem:
    """Single artifact item."""

    name: str
    is_directory: bool = False


class Artifacts(Static):
    """Artifacts panel showing generated files."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._items: list[ArtifactItem] = []

    def set_artifacts(self, items: list[ArtifactItem]) -> None:
        """Set artifact items."""
        self._items = items
        self._update_display()

    def _update_display(self) -> None:
        lines = ["[b]Artifacts[/b]", ""]
        for item in self._items:
            icon = "[📁]" if item.is_directory else "[·]"
            lines.append(f"{icon} {item.name}")
        self.update("\n".join(lines) if lines else "No artifacts")

    def on_mount(self) -> None:
        self._update_display()
