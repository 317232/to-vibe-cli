"""to-vibe pipeline panel (Tab 2) — Bento Grid with Evidence + Priority + Verify."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget

from to_vibe.tui.components.evidence_card import EvidenceCard
from to_vibe.tui.components.priority_card import PriorityCard
from to_vibe.tui.components.verify_table import VerifyTable
from to_vibe.tui.state_store import TUIStateStore


class ToVibePanel(Widget):
    """to-vibe pipeline panel with Bento Grid layout.

    Layout (per TUI_DESIGN.md image2.1.png):
    ┌─────────────────────────┬────────────────────────────────┐
    │ EvidenceCard (green)   │                                │
    │                         │                                │
    ├─────────────────────────┤       VerifyTable (red)      │
    │ PriorityCard (yellow)  │                                │
    │                         │                                │
    └─────────────────────────┴────────────────────────────────┘
    Ratio: 40% left | 60% right
    """

    def __init__(self, store: TUIStateStore, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._store = store

    def compose(self) -> ComposeResult:
        """Compose the Bento Grid layout."""
        left_col = Vertical(
            EvidenceCard(self._store, id="evidence-card"),
            PriorityCard(self._store, id="priority-card"),
            id="left-col",
        )
        right_col = VerifyTable(self._store, id="verify-table")
        yield Horizontal(left_col, right_col, id="bento-grid")
