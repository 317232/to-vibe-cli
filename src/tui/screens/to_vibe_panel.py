"""to-vibe pipeline panel (Tab 2)."""

from __future__ import annotations

from textual.widget import Widget


class ToVibePanel(Widget):
    """to-vibe pipeline panel with stage bar and cards."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
