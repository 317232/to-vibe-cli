"""LLM API client — endpoint-centric, supports any OpenAI-compatible or Anthropic-compatible endpoint."""

from __future__ import annotations

import json
from typing import Any, AsyncIterator

import httpx

from to_vibe.config import LLMConfig
from to_vibe.llm.protocol import get_protocol


class LLMError(Exception):
    """Base exception for LLM errors."""
    pass


class GenericLLMClient:
    """LLM client that delegates protocol-specific behavior to LLMProtocol.

    Responsibilities:
      - HTTP transport (connection, timeouts, streaming)
      - Building the full URL from base_url + endpoint
      - Wiring auth headers

    Protocol-specific behavior lives in LLMProtocol:
      - auth header name/value format
      - chat endpoint path
      - request body shape
      - response parsing
    """

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self._protocol = get_protocol(config.protocol)

    # ------------------------------------------------------------------
    # URL / headers — build the HTTP request envelope
    # ------------------------------------------------------------------

    def _url(self) -> str:
        """Full URL for chat completions."""
        base = self.config.resolved_base_url()
        path = self._protocol.chat_endpoint()
        if base:
            return f"{base}{path}"
        return path

    def _headers(self) -> dict[str, str]:
        """HTTP headers including auth."""
        headers: dict[str, str] = {
            "content-type": "application/json",
        }
        if self.config.protocol == "anthropic":
            headers["anthropic-version"] = "2023-06-01"
        headers[self._protocol.auth_header_name()] = self._protocol.auth_header_value(
            self.config.api_key
        )
        return headers

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def complete(
        self,
        messages: list[dict[str, str]],
        *,
        max_tokens: int | None = None,
    ) -> str:
        """Non-streaming completion — returns full response text."""
        api_key = self.config.api_key
        if not api_key:
            raise LLMError("API key not set (check api_key in to-vibe.yaml)")

        body = self._protocol.build_body(
            model=self.config.model,
            messages=messages,
            stream=False,
            max_tokens=max_tokens or self.config.max_tokens,
            temperature=self.config.temperature if self.config.temperature else None,
        )
        headers = self._headers()

        timeout = httpx.Timeout(self.config.timeout)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(self._url(), headers=headers, json=body)

        if response.status_code != 200:
            raise LLMError(f"LLM API error {response.status_code}: {response.text}")

        result = response.json()
        return self._protocol.extract_content(result)

    async def stream_complete(
        self,
        messages: list[dict[str, str]],
        *,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        """Streaming completion — yields text chunks as they arrive."""
        api_key = self.config.api_key
        if not api_key:
            raise LLMError("API key not set (check api_key in to-vibe.yaml)")

        body = self._protocol.build_body(
            model=self.config.model,
            messages=messages,
            stream=True,
            max_tokens=max_tokens or self.config.max_tokens,
            temperature=self.config.temperature if self.config.temperature else None,
        )
        headers = self._headers()

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
    """Create an LLM client — always returns GenericLLMClient.

    Args:
        config: LLM configuration with endpoint, credentials, and protocol

    Returns:
        GenericLLMClient instance
    """
    return GenericLLMClient(config)


# Global client instance
_client: GenericLLMClient | None = None


def get_client() -> GenericLLMClient | None:
    """Get the global LLM client instance."""
    return _client


def init_client(config: LLMConfig) -> GenericLLMClient:
    """Initialize the global LLM client.

    Args:
        config: LLM configuration

    Returns:
        Initialized GenericLLMClient
    """
    global _client
    _client = create_client(config)
    return _client