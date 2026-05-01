"""Chat panel for LLM interaction (Tab 1)."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widgets import Static, Input, ScrollView
from textual.widget import Widget

from to_vibe.llm.client import get_client


class ChatMessage(Static):
    """Single chat message."""

    def __init__(self, role: str, text: str, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.role = role
        self.text = text

    def compose(self) -> ComposeResult:
        """Compose the message."""
        prefix = "[b]You[/b]:" if self.role == "user" else "[b]LLM[/b]:"
        yield Static(f"{prefix} {self.text}")


class ChatPanel(Widget):
    """Chat panel for LLM conversation with streaming support."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._messages: list[tuple[str, str]] = []

    def compose(self) -> ComposeResult:
        """Compose the chat panel."""
        yield ScrollView(id="chat-history", classes="chat-history")
        yield Input(placeholder="Type a message...", id="chat-input", classes="chat-input")

    def on_mount(self) -> None:
        """Handle mount event."""
        history = self.query_one("#chat-history", ScrollView)
        history_mount = history
        self._history = history

    def add_message(self, role: str, text: str) -> None:
        """Add a message to the chat history."""
        self._messages.append((role, text))
        if hasattr(self, "_history"):
            self._history.mount(ChatMessage(role, text))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        text = event.value.strip()
        if not text:
            return

        self.add_message("user", text)
        event.input.value = ""

        # Send to LLM
        client = get_client()
        if client:
            import asyncio
            asyncio.create_task(self._stream_response(text))

    async def _stream_response(self, user_text: str) -> None:
        """Stream LLM response."""
        client = get_client()
        if not client:
            self.add_message("assistant", "LLM not configured")
            return

        try:
            messages = [{"role": "user" if r == "user" else "assistant", "content": t} for r, t in self._messages]
            response = await client.complete(messages)
            self.add_message("assistant", response)
        except Exception as e:
            self.add_message("assistant", f"Error: {e}")
