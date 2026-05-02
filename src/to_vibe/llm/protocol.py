"""Protocol definitions for LLM clients."""

from __future__ import annotations

from to_vibe.llm.request import LLMRequest


class LLMProtocol:
    """Single place for protocol behavior — auth format, endpoint path, body shape.

    Extend this class to add new protocols (e.g. vertex-ai, bedrock, etc.)
    without touching client.py or LLMConfig.
    """

    @property
    def name(self) -> str:
        """Unique identifier for this protocol."""
        raise NotImplementedError

    def chat_endpoint(self) -> str:
        """Return the chat completions endpoint path."""
        raise NotImplementedError

    def auth_header_name(self) -> str:
        """Return the auth header key name."""
        raise NotImplementedError

    def auth_header_value(self, api_key: str) -> str:
        """Return the formatted auth header value given the raw api_key."""
        raise NotImplementedError

    def build_request(self, req: LLMRequest) -> dict:
        """Build the request body for this protocol from an LLMRequest."""
        raise NotImplementedError

    def extract_content(self, result: dict) -> str:
        """Extract text content from a non-streaming response."""
        raise NotImplementedError

    def extract_chunk(self, chunk: dict) -> str:
        """Extract text delta from a streaming chunk."""
        raise NotImplementedError


# ----------------------------------------------------------------------
# Concrete protocol implementations
# ----------------------------------------------------------------------


class AnthropicProtocol(LLMProtocol):
    """Anthropic API protocol — uses x-api-key, /v1/messages, thinking blocks."""

    @property
    def name(self) -> str:
        return "anthropic"

    def chat_endpoint(self) -> str:
        return "/v1/messages"

    def auth_header_name(self) -> str:
        return "x-api-key"

    def auth_header_value(self, api_key: str) -> str:
        return api_key  # raw, no Bearer

    def build_request(self, req: LLMRequest) -> dict:
        body: dict = {
            "model": req.model,
            "messages": req.messages,
            "max_tokens": req.max_tokens,
            "stream": req.stream,
        }
        if req.thinking is not None:
            body["thinking"] = req.thinking
        if req.stop:
            body["stop_sequences"] = req.stop
        # Merge extra_body for provider-specific fields (e.g. vertex-ai extensions)
        body.update(req.extra_body)
        return body

    def extract_content(self, result: dict) -> str:
        """Extract — skips thinking blocks, finds first text block (MiniMax compatible)."""
        for item in result.get("content", []):
            if isinstance(item, dict) and item.get("type") == "text":
                return item.get("text", "")
        return ""

    def extract_chunk(self, chunk: dict) -> str:
        if chunk.get("type") == "content_block_delta":
            return chunk.get("delta", {}).get("text", "")
        return ""


class OpenAICompatibleProtocol(LLMProtocol):
    """OpenAI-compatible protocol — uses Authorization: Bearer, /v1/chat/completions."""

    @property
    def name(self) -> str:
        return "openai-compatible"

    def chat_endpoint(self) -> str:
        return "/v1/chat/completions"

    def auth_header_name(self) -> str:
        return "Authorization"

    def auth_header_value(self, api_key: str) -> str:
        return f"Bearer {api_key}"

    def build_request(self, req: LLMRequest) -> dict:
        body: dict = {
            "model": req.model,
            "messages": req.messages,
            "max_tokens": req.max_tokens,
            "stream": req.stream,
        }
        if req.temperature is not None:
            body["temperature"] = req.temperature
        if req.top_p is not None:
            body["top_p"] = req.top_p
        if req.stop:
            body["stop"] = req.stop
        if req.presence_penalty is not None:
            body["presence_penalty"] = req.presence_penalty
        if req.frequency_penalty is not None:
            body["frequency_penalty"] = req.frequency_penalty
        if req.tools:
            body["tools"] = req.tools
        if req.tool_choice:
            body["tool_choice"] = req.tool_choice
        if req.response_format:
            body["response_format"] = req.response_format
        # Merge extra_body last so it can override standard fields
        body.update(req.extra_body)
        return body

    def extract_content(self, result: dict) -> str:
        return result["choices"][0]["message"]["content"]

    def extract_chunk(self, chunk: dict) -> str:
        if choices := chunk.get("choices"):
            return choices[0].get("delta", {}).get("content", "")
        return ""


# ----------------------------------------------------------------------
# Registry — maps protocol name to implementation
# ----------------------------------------------------------------------

_PROTOCOLS: dict[str, LLMProtocol] = {
    "anthropic": AnthropicProtocol(),
    "openai-compatible": OpenAICompatibleProtocol(),
}


def get_protocol(name: str) -> LLMProtocol:
    """Return the protocol implementation for the given name.

    Raises KeyError if unknown.
    """
    return _PROTOCOLS[name]


def register_protocol(impl: LLMProtocol) -> None:
    """Register a custom protocol implementation."""
    _PROTOCOLS[impl.name] = impl