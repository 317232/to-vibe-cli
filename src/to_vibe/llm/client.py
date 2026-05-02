"""LLM API client — endpoint-centric, supports any OpenAI-compatible or Anthropic-compatible endpoint."""

from __future__ import annotations

import json
from typing import Any, AsyncIterator

import httpx

from to_vibe.config import LLMConfig


class LLMError(Exception):
    """Base exception for LLM errors."""
    pass


class GenericLLMClient:
    """Single LLM client driven by LLMConfig.protocol and base_url.

    Protocol determines:
      - auth header name/value format
      - chat endpoint path
      - request body shape
      - response parsing
    """

    def __init__(self, config: LLMConfig) -> None:
        self.config = config

    # ------------------------------------------------------------------
    # URL / headers helpers — delegated to LLMConfig
    # ------------------------------------------------------------------

    def _url(self) -> str:
        """Full URL for chat completions."""
        base = self.config.resolved_base_url()
        path = self.config.chat_endpoint()
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
            headers[self.config.auth_header_name()] = self.config.auth_header_value(
                self.config.api_key
            )
        else:
            # openai-compatible
            headers[self.config.auth_header_name()] = self.config.auth_header_value(
                self.config.api_key
            )
        return headers

    def _body(self, messages: list[dict[str, str]], stream: bool, **kwargs: Any) -> dict[str, Any]:
        """Build request body — protocol shapes the structure."""
        body: dict[str, str] = {
            "model": self.config.model,
            "messages": messages,
        }

        if self.config.protocol == "anthropic":
            body["max_tokens"] = kwargs.get("max_tokens", self.config.max_tokens)
            body["stream"] = stream
        else:
            # openai-compatible
            body["max_tokens"] = kwargs.get("max_tokens", self.config.max_tokens)
            if self.config.temperature:
                body["temperature"] = self.config.temperature
            body["stream"] = stream

        return body

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

        body = self._body(messages, stream=False, max_tokens=max_tokens)
        headers = self._headers()

        timeout = httpx.Timeout(self.config.timeout)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(self._url(), headers=headers, json=body)

        if response.status_code != 200:
            raise LLMError(f"LLM API error {response.status_code}: {response.text}")

        result = response.json()
        return self._extract_content(result)

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

        body = self._body(messages, stream=True, max_tokens=max_tokens)
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
                        text = self._extract_chunk(chunk)
                        if text:
                            yield text

    # ------------------------------------------------------------------
    # Response parsing — protocol-specific
    # ------------------------------------------------------------------

    def _extract_content(self, result: Any) -> str:
        """Extract message content from non-streaming response."""
        if self.config.protocol == "anthropic":
            return result["content"][0]["text"]
        # openai-compatible
        return result["choices"][0]["message"]["content"]

    def _extract_chunk(self, chunk: Any) -> str:
        """Extract text delta from streaming chunk."""
        if self.config.protocol == "anthropic":
            if chunk.get("type") == "content_block_delta":
                return chunk["delta"]["text"]
        else:
            # openai-compatible
            if choices := chunk.get("choices"):
                delta = choices[0].get("delta", {})
                return delta.get("content", "")
        return ""


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