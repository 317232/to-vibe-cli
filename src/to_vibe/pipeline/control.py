"""Pipeline control port — single control entry point for CLI, TUI, and MCP.

All control surfaces (CLI, TUI, MCP) SHOULD only talk to PipelineControlPort.
Concrete implementations delegate to actual pipeline executors.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RetryTarget:
    """What to retry."""

    kind: str = "last_failed"  # "last_failed" | "stage:<name>" | "issue:<id>"
    stage_name: str | None = None
    issue_id: str | None = None


@dataclass
class SkipPolicy:
    """Skip permission rules per stage."""

    forbidden: set[str] = field(default_factory=lambda: {"evidence", "priority"})
    reason_required: set[str] = field(default_factory=lambda: {"verify", "repair"})
    always_allowed: set[str] = field(default_factory=lambda: {"learn"})

    def can_skip(self, stage: str, reason: str | None = None) -> tuple[bool, str | None]:
        """Returns (allowed, error_message)."""
        if stage in self.forbidden:
            return False, f"{stage} cannot be skipped"
        if stage in self.reason_required and not reason:
            return False, f"{stage} requires a reason to skip"
        return True, None


@dataclass
class ControlResult:
    """Standard return type for all control operations."""

    status: str  # "completed" | "paused" | "resumed" | "retrying" | "skipped" | "failed"
    message: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class PipelineControlPort(ABC):
    """Abstract port for pipeline control.

    All control surfaces (CLI, TUI, MCP) should talk only to this interface.
    """

    @abstractmethod
    async def run(self, project_path: str | Path, mode: str = "dry-run") -> ControlResult:
        raise NotImplementedError

    @abstractmethod
    async def pause(self) -> ControlResult:
        raise NotImplementedError

    @abstractmethod
    async def resume(self) -> ControlResult:
        raise NotImplementedError

    @abstractmethod
    async def retry(self, target: RetryTarget | None = None) -> ControlResult:
        raise NotImplementedError

    @abstractmethod
    async def skip(self, stage: str | None = None, reason: str | None = None) -> ControlResult:
        raise NotImplementedError

    @abstractmethod
    async def learn(self, project_path: str | Path) -> ControlResult:
        raise NotImplementedError

    @abstractmethod
    def snapshot(self) -> ControlResult:
        raise NotImplementedError
