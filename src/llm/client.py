"""LLM API client supporting Anthropic and OpenAI compatible endpoints."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncIterator

import httpx

from to_vibe.config import LLMConfig


class LLMError(Exception):
    """Base exception for LLM errors."""
    pass


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    def __init__(self, config: LLMConfig) -> None:
        self.config = config

    @abstractmethod
    async def complete(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """Generate a completion.

        Args:
            messages: List of message dicts with role and content
            **kwargs: Additional provider-specific arguments

        Returns:
            Completion text
        """
        pass

    @abstractmethod
    async def stream_complete(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncIterator[str]:
        """Generate a streaming completion.

        Args:
            messages: List of message dicts with role and content
            **kwargs: Additional provider-specific arguments

        Yields:
            Completion text chunks
        """
        pass


class AnthropicClient(LLMClient):
    """Anthropic API compatible client."""

    async def complete(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """Generate a completion using Anthropic API."""
        api_key = self.config.api_key
        if not api_key:
            raise LLMError("ANTHROPIC_API_KEY not set")

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        data = {
            "model": self.config.model,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "messages": messages,
        }

        timeout = httpx.Timeout(self.config.timeout)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{self.config.base_url}/v1/messages",
                headers=headers,
                json=data,
            )

        if response.status_code != 200:
            raise LLMError(f"Anthropic API error: {response.status_code} {response.text}")

        result = response.json()
        return result["content"][0]["text"]

    async def stream_complete(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncIterator[str]:
        """Generate a streaming completion using Anthropic API."""
        api_key = self.config.api_key
        if not api_key:
            raise LLMError("ANTHROPIC_API_KEY not set")

        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        data = {
            "model": self.config.model,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "messages": messages,
            "stream": True,
        }

        timeout = httpx.Timeout(self.config.timeout)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                f"{self.config.base_url}/v1/messages",
                headers=headers,
                json=data,
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        if line == "data: [DONE]":
                            break
                        import json
                        chunk = json.loads(line[6:])
                        if chunk.get("type") == "content_block_delta":
                            yield chunk["delta"]["text"]


class OpenAIClient(LLMClient):
    """OpenAI API compatible client."""

    async def complete(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """Generate a completion using OpenAI API."""
        api_key = self.config.api_key
        if not api_key:
            raise LLMError("OPENAI_API_KEY not set")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "content-type": "application/json",
        }

        data = {
            "model": self.config.model,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "messages": messages,
        }

        timeout = httpx.Timeout(self.config.timeout)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{self.config.base_url}/v1/chat/completions",
                headers=headers,
                json=data,
            )

        if response.status_code != 200:
            raise LLMError(f"OpenAI API error: {response.status_code} {response.text}")

        result = response.json()
        return result["choices"][0]["message"]["content"]

    async def stream_complete(self, messages: list[dict[str, str]], **kwargs: Any) -> AsyncIterator[str]:
        """Generate a streaming completion using OpenAI API."""
        api_key = self.config.api_key
        if not api_key:
            raise LLMError("OPENAI_API_KEY not set")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "content-type": "application/json",
        }

        data = {
            "model": self.config.model,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "messages": messages,
            "stream": True,
        }

        timeout = httpx.Timeout(self.config.timeout)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                f"{self.config.base_url}/v1/chat/completions",
                headers=headers,
                json=data,
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        if line == "data: [DONE]":
                            break
                        import json
                        chunk = json.loads(line[6:])
                        if chunk.get("choices"):
                            delta = chunk["choices"][0].get("delta", {})
                            if delta.get("content"):
                                yield delta["content"]


def create_client(config: LLMConfig) -> LLMClient:
    """Create an LLM client based on configuration.

    Args:
        config: LLM configuration

    Returns:
        LLM client instance
    """
    if config.provider == "anthropic":
        return AnthropicClient(config)
    elif config.provider == "openai":
        return OpenAIClient(config)
    else:
        raise LLMError(f"Unknown provider: {config.provider}")


# Global client instance
_client: LLMClient | None = None


def get_client() -> LLMClient | None:
    """Get the global LLM client instance."""
    return _client


def init_client(config: LLMConfig) -> LLMClient:
    """Initialize the global LLM client.

    Args:
        config: LLM configuration

    Returns:
        Initialized LLM client
    """
    global _client
    _client = create_client(config)
    return _client
