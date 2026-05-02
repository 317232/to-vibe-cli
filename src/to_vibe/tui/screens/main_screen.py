"""Main screen with tab navigation for to-vibe."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, Static

from to_vibe.tui.components.header import Header
from to_vibe.tui.components.footer import Footer
from to_vibe.tui.components.stage_bar import StageBar
from to_vibe.tui.screens.chat_panel import ChatPanel
from to_vibe.tui.screens.to_vibe_panel import ToVibePanel
from to_vibe.tui.screens.logs_panel import LogsPanel
from to_vibe.tui.state_store import TUIStateStore


class MainScreen(Screen):
    """Main screen with 3-tab bento grid layout."""

    BINDINGS = [
        ("tab", "switch_tab(1)", "Next Tab"),
        ("shift+tab", "switch_tab(-1)", "Prev Tab"),
    ]

    def __init__(self, store: TUIStateStore, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._store = store
        self._active_tab = 0
        self._tabs = ["chat", "to-vibe", "logs"]
        self._tab_labels = ["1: claude", "2: to-vibe", "3: logs"]

    def compose(self) -> ComposeResult:
        """Compose the main screen layout."""
        yield Header(self._store, id="app-header")
        yield TabBar(id="tab-bar", tabs=self._tabs, labels=self._tab_labels)
        yield ChatPanel(id="chat-panel")
        yield ToVibePanel(self._store, id="to-vibe-panel")
        yield LogsPanel(self._store, id="logs-panel")
        yield StageBar(self._store, id="stage-bar")
        yield Footer(self._store, id="app-footer")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle tab button clicks — route to switch_tab_to."""
        btn_id = event.button.id
        if btn_id and btn_id.startswith("tab-btn-"):
            tab_id = btn_id[len("tab-btn-"):]
            try:
                index = self._tabs.index(tab_id)
                self._apply_tab(index)
                self._active_tab = index
                tab_bar = self.query_one("#tab-bar", TabBar)
                tab_bar.set_active(index)
            except ValueError:
                pass

    def switch_tab(self, direction: int) -> None:
        """Switch to next or previous tab (keyboard shortcut)."""
        self._active_tab = (self._active_tab + direction) % len(self._tabs)
        self._apply_tab(self._active_tab)
        tab_bar = self.query_one("#tab-bar", TabBar)
        tab_bar.set_active(self._active_tab)

    def _apply_tab(self, index: int) -> None:
        tab_name = self._tabs[index]
        chat = self.query_one("#chat-panel", ChatPanel)
        to_vibe = self.query_one("#to-vibe-panel", ToVibePanel)
        logs = self.query_one("#logs-panel", LogsPanel)
        chat.display = (tab_name == "chat")
        to_vibe.display = (tab_name == "to-vibe")
        logs.display = (tab_name == "logs")


class TabBar(Horizontal):
    """Horizontal tab bar with active tab highlighted in orange.

    Active: orange border (#d29922) + orange text (#d29922)
    Inactive: muted text (#6c7086)
    """

    BINDINGS = [
        ("tab", "next_tab", ""),
        ("shift+tab", "prev_tab", ""),
    ]

    def __init__(self, tabs: list[str], labels: list[str], **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._tab_ids = tabs
        self._tab_labels = labels
        self._active = 0
        self._tab_buttons: list[Button] = []

    def compose(self) -> ComposeResult:
        """Yield tab buttons."""
        for i, (tab_id, label) in enumerate(zip(self._tab_ids, self._tab_labels)):
            btn = Button(
                label,
                id=f"tab-btn-{tab_id}",
                classes="tab-btn",
            )
            self._tab_buttons.append(btn)
            yield btn

    def on_mount(self) -> None:
        self.set_active(0)

    def set_active(self, index: int) -> None:
        """Set the active tab by index."""
        self._active = index
        for i, btn in enumerate(self._tab_buttons):
            if i == index:
                btn.variant = "primary"
                btn.styles.color = "#d29922"
                btn.styles.border = ("solid", "#d29922")
            else:
                btn.variant = "default"
                btn.styles.color = ""
                btn.styles.border = ("none", "")

    def action_next_tab(self) -> None:
        """Advance to next tab."""
        screen = self.screen
        if isinstance(screen, MainScreen):
            screen.switch_tab(1)
        else:
            self.set_active((self._active + 1) % len(self._tab_buttons))

    def action_prev_tab(self) -> None:
        """Go to previous tab."""
        screen = self.screen
        if isinstance(screen, MainScreen):
            screen.switch_tab(-1)
        else:
            self.set_active((self._active - 1) % len(self._tab_buttons))

