"""Pipeline event bus — pub/sub broadcast for real-time pipeline events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Any


@dataclass
class PipelineEvent:
    """Single pipeline event emitted to all subscribers."""

    timestamp: str
    level: str  # INFO / WARN / ERROR / DEBUG
    stage: str  # evidence / priority / verify / repair / learn / complete / idle
    message: str
    data: dict[str, Any] | None = None

    @classmethod
    def create(
        cls,
        level: str,
        stage: str,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> PipelineEvent:
        return cls(
            timestamp=datetime.now().strftime("%H:%M:%S"),
            level=level,
            stage=stage,
            message=message,
            data=data,
        )


class PipelineEventBus:
    """Singleton event bus — subscribers receive all events."""

    _subscribers: list[Callable[[PipelineEvent], None]] = []

    @classmethod
    def subscribe(cls, handler: Callable[[PipelineEvent], None]) -> None:
        if handler not in cls._subscribers:
            cls._subscribers.append(handler)

    @classmethod
    def unsubscribe(cls, handler: Callable[[PipelineEvent], None]) -> None:
        cls._subscribers.discard(handler)

    @classmethod
    def emit(cls, event: PipelineEvent) -> None:
        for handler in cls._subscribers:
            try:
                handler(event)
            except Exception:
                pass

    @classmethod
    def clear(cls) -> None:
        cls._subscribers.clear()

    @classmethod
    def log(cls, stage: str, message: str, level: str = "INFO") -> None:
        cls.emit(PipelineEvent.create(level=level, stage=stage, message=message))

    @classmethod
    def info(cls, stage: str, message: str) -> None:
        cls.log(stage, message, "INFO")

    @classmethod
    def warn(cls, stage: str, message: str) -> None:
        cls.log(stage, message, "WARN")

    @classmethod
    def error(cls, stage: str, message: str) -> None:
        cls.log(stage, message, "ERROR")

    @classmethod
    def stage_start(cls, stage: str) -> None:
        cls.emit(PipelineEvent.create(
            level="INFO",
            stage=stage,
            message=f"Stage '{stage}' started",
            data={"action": "stage_start", "stage": stage},
        ))

    @classmethod
    def stage_complete(cls, stage: str, result: Any = None) -> None:
        cls.emit(PipelineEvent.create(
            level="INFO",
            stage=stage,
            message=f"Stage '{stage}' completed",
            data={"action": "stage_complete", "stage": stage, "result": result},
        ))

    @classmethod
    def stage_fail(cls, stage: str, error: str) -> None:
        cls.emit(PipelineEvent.create(
            level="ERROR",
            stage=stage,
            message=f"Stage '{stage}' failed: {error}",
            data={"action": "stage_fail", "stage": stage, "error": error},
        ))

    @classmethod
    def progress(cls, stage: str, progress: float, message: str) -> None:
        cls.emit(PipelineEvent.create(
            level="INFO",
            stage=stage,
            message=message,
            data={"action": "progress", "stage": stage, "progress": progress},
        ))