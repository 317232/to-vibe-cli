"""Main screen with tab navigation for to-vibe."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen

from to_vibe.tui.components.header import Header
from to_vibe.tui.screens.chat_panel import ChatPanel
from to_vibe.tui.screens.to_vibe_panel import ToVibePanel
from to_vibe.tui.screens.logs_panel import LogsPanel


class MainScreen(Screen):
    """Main screen with 3-tab bento grid layout.

    Layout:
    - Left: Chat Panel (Tab 1)
    - Right: to-vibe Pipeline Panel (Tab 2)
    - Bottom: Logs Panel (Tab 3)
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._active_tab = 0
        self._tabs = ["chat", "to-vibe", "logs"]

    def compose(self) -> ComposeResult:
        """Compose the main screen layout."""
        yield Header()
        yield ChatPanel(id="chat-panel")
        yield ToVibePanel(id="to-vibe-panel")
        yield LogsPanel(id="logs-panel")

    def switch_tab(self, direction: int) -> None:
        """Switch to next or previous tab.

        Args:
            direction: 1 for next, -1 for previous
        """
        self._active_tab = (self._active_tab + direction) % len(self._tabs)
        tab_name = self._tabs[self._active_tab]

        # Show/hide panels based on active tab
        chat = self.query_one("#chat-panel", ChatPanel)
        to_vibe = self.query_one("#to-vibe-panel", ToVibePanel)
        logs = self.query_one("#logs-panel", LogsPanel)

        chat.display = (tab_name == "chat")
        to_vibe.display = (tab_name == "to-vibe")
        logs.display = (tab_name == "logs")
