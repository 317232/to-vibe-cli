"""LLM API client — endpoint-centric, supports any OpenAI-compatible or Anthropic-compatible endpoint."""

from __future__ import annotations

import json
from typing import Any, AsyncIterator

import httpx

from to_vibe.config import LLMConfig
from to_vibe.llm.protocol import get_protocol
from to_vibe.llm.request import LLMRequest


class LLMError(Exception):
    """Base exception for LLM errors."""
    pass


class GenericLLMClient:
    """LLM client that delegates protocol-specific behavior to LLMProtocol.

    Responsibilities:
      - HTTP transport (connection, timeouts, streaming)
      - Building the full URL from base_url + endpoint

    Protocol-specific behavior lives in LLMProtocol:
      - headers(config) — all HTTP headers including auth + extra_headers
      - chat_endpoint() — path component of the URL
      - build_request(req: LLMRequest) — request body
      - extract_content / extract_chunk — response parsing
    """

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self._protocol = get_protocol(config.protocol)

    # ------------------------------------------------------------------
    # URL — build the HTTP request envelope
    # ------------------------------------------------------------------

    def _url(self) -> str:
        """Full URL for chat completions."""
        base = self.config.resolved_base_url()
        path = self._protocol.chat_endpoint()
        if base:
            return f"{base}{path}"
        return path

    # ------------------------------------------------------------------
    # Request assembly
    # ------------------------------------------------------------------

    def _build_request(self, messages: list[dict[str, str]], **kwargs: Any) -> LLMRequest:
        """Build an LLMRequest from config + caller kwargs."""
        return LLMRequest(
            model=self.config.model,
            messages=messages,
            stream=kwargs.pop("stream", self.config.stream),
            max_tokens=kwargs.pop("max_tokens", self.config.max_tokens),
            temperature=kwargs.pop("temperature", self.config.temperature),
            top_p=kwargs.pop("top_p", None),
            stop=kwargs.pop("stop", None),
            presence_penalty=kwargs.pop("presence_penalty", None),
            frequency_penalty=kwargs.pop("frequency_penalty", None),
            thinking=kwargs.pop("thinking", None),
            tools=kwargs.pop("tools", None),
            tool_choice=kwargs.pop("tool_choice", None),
            response_format=kwargs.pop("response_format", None),
            extra_body=kwargs.pop("extra_body", {}),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def complete(
        self,
        messages: list[dict[str, str]],
        *,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> str:
        """Non-streaming completion — returns full response text."""
        if not self.config.api_key:
            raise LLMError("API key not set (check api_key in to-vibe.yaml)")

        # Force stream=False so body is correct for non-streaming response
        req = self._build_request(messages, stream=False, max_tokens=max_tokens, **kwargs)
        body = self._protocol.build_request(req)
        headers = self._protocol.headers(self.config)

        timeout = httpx.Timeout(self.config.timeout)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(self._url(), headers=headers, json=body)

        if response.status_code != 200:
            raise LLMError(f"LLM API error {response.status_code}: {response.text}")

        return self._protocol.extract_content(response.json())

    async def stream_complete(
        self,
        messages: list[dict[str, str]],
        *,
        max_tokens: int | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Streaming completion — yields text chunks as they arrive."""
        if not self.config.api_key:
            raise LLMError("API key not set (check api_key in to-vibe.yaml)")

        # Force stream=True so body is correct for streaming response
        req = self._build_request(messages, stream=True, max_tokens=max_tokens, **kwargs)
        body = self._protocol.build_request(req)
        headers = self._protocol.headers(self.config)

        timeout = httpx.Timeout(self.config.timeout)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", self._url(), headers=headers, json=body) as response:
                if response.status_code != 200:
                    text = await response.aread()
                    raise LLMError(f"LLM API error {response.status_code}: {text.decode()}")

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        if line == "data: [DONE]":
                            break
                        chunk = json.loads(line[6:])
                        text = self._protocol.extract_chunk(chunk)
                        if text:
                            yield text


# ------------------------------------------------------------------
# Backward-compatible factory
# ------------------------------------------------------------------

def create_client(config: LLMConfig) -> GenericLLMClient:
    """Create an LLM client — always returns GenericLLMClient."""
    return GenericLLMClient(config)


_client: GenericLLMClient | None = None


def get_client() -> GenericLLMClient | None:
    """Get the global LLM client instance."""
    return _client


def init_client(config: LLMConfig) -> GenericLLMClient:
    """Initialize the global LLM client."""
    global _client
    _client = create_client(config)
    return _client