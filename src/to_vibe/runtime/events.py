"""Runtime events and state types for to-vibe pipeline."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class StageId(str, Enum):
    """Pipeline stage identifiers."""

    EVIDENCE = "evidence"
    PRIORITY = "priority"
    VERIFY = "verify"
    REPAIR = "repair"
    LEARN = "learn"


class StageStatus(str, Enum):
    """Stage execution status."""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    PAUSED = "paused"


class LogLevel(str, Enum):
    """Log severity level."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class RuntimeAction(str, Enum):
    """User or system runtime actions."""

    CONTINUE = "continue"
    PAUSE = "pause"
    RESUME = "resume"
    RETRY = "retry"
    SKIP = "skip"
    CANCEL = "cancel"
    OPEN_DETAIL = "open_detail"
    RETURN = "return"


@dataclass
class StageState:
    """Status of a single pipeline stage."""

    stage_id: StageId
    status: StageStatus = StageStatus.PENDING
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_id": self.stage_id.value,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StageState:
        return cls(
            stage_id=StageId(data["stage_id"]),
            status=StageStatus(data.get("status", "pending")),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            error=data.get("error"),
        )


@dataclass
class PipelineSnapshot:
    """Immutable snapshot of the entire pipeline state at a point in time."""

    session_id: str
    timestamp: str
    current_stage: StageId
    current_status: StageStatus
    stages: list[StageState]
    progress: float  # 0.0 to 1.0
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "current_stage": self.current_stage.value,
            "current_status": self.current_status.value,
            "stages": [s.to_dict() for s in self.stages],
            "progress": self.progress,
            "error_message": self.error_message,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PipelineSnapshot:
        return cls(
            session_id=data["session_id"],
            timestamp=data["timestamp"],
            current_stage=StageId(data["current_stage"]),
            current_status=StageStatus(data["current_status"]),
            stages=[StageState.from_dict(s) for s in data.get("stages", [])],
            progress=data.get("progress", 0.0),
            error_message=data.get("error_message"),
        )

    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> PipelineSnapshot:
        import json
        return cls.from_dict(json.loads(json_str))


@dataclass
class LogEvent:
    """Log event emitted during pipeline execution."""

    timestamp: str
    level: LogLevel
    text: str
    session_id: str | None = None
    source: str | None = None
    stage: StageId | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "level": self.level.value,
            "text": self.text,
            "session_id": self.session_id,
            "source": self.source,
            "stage": self.stage.value if self.stage else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LogEvent:
        return cls(
            timestamp=data["timestamp"],
            level=LogLevel(data["level"]),
            text=data["text"],
            session_id=data.get("session_id"),
            source=data.get("source"),
            stage=StageId(data["stage"]) if data.get("stage") else None,
        )


@dataclass
class ArtifactEvent:
    """Artifact produced by a pipeline stage."""

    name: str
    path: str
    artifact_type: str
    is_directory: bool = False
    size_bytes: int | None = None
    content_hash: str | None = None


@dataclass
class ProgressEvent:
    """Progress update within a stage."""

    stage: StageId
    current: int
    total: int
    detail: str = ""


@dataclass
class ActionRequiredEvent:
    """Pipeline paused waiting for user decision."""

    stage: StageId
    prompt: str
    options: list[str] = field(default_factory=list)
    default: str = ""
    session_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage.value,
            "prompt": self.prompt,
            "options": self.options,
            "default": self.default,
            "session_id": self.session_id,
        }


def new_session_id() -> str:
    """Generate a new unique session ID."""
    return str(uuid.uuid4())[:8]


def now_iso() -> str:
    """Current ISO timestamp with millisecond precision."""
    return datetime.now().isoformat(timespec="milliseconds")