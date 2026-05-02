"""LLM request parameters dataclass."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMRequest:
    """All parameters needed to build an LLM request body.

    Passed to LLMProtocol.build_request() so protocol implementations
    can access whatever fields they need without the client having to
    know which fields are relevant for which protocol.

    Extra fields (extra_body) allow provider-specific parameters without
    changing the dataclass.
    """

    model: str
    messages: list[dict[str, str]]
    stream: bool = False
    max_tokens: int = 4096
    temperature: float | None = None
    top_p: float | None = None
    stop: list[str] | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None
    # Anthropic-specific
    thinking: dict | None = None  # {"type": "enabled", "budget_tokens": 1024}
    # OpenAI-compatible / provider-specific
    tools: list[dict] | None = None
    tool_choice: dict | None = None
    response_format: dict | None = None  # {"type": "json_object"}
    # Catch-all for any provider-specific fields
    extra_body: dict[str, Any] = field(default_factory=dict)