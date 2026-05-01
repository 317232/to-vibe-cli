"""Session state management — save/restore pipeline sessions."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from to_vibe.runtime.events import (
    PipelineSnapshot,
    StageId,
    StageState,
    StageStatus,
    now_iso,
    new_session_id,
)


@dataclass
class SessionState:
    """Persisted session state, recoverable from session-start.json."""

    session_id: str
    project_path: str
    started_at: str
    updated_at: str
    current_stage: str
    current_status: str
    stages: list[dict[str, Any]]
    progress: float
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "project_path": self.project_path,
            "started_at": self.started_at,
            "updated_at": self.updated_at,
            "current_stage": self.current_stage,
            "current_status": self.current_status,
            "stages": self.stages,
            "progress": self.progress,
            "error_message": self.error_message,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SessionState:
        return cls(
            session_id=data["session_id"],
            project_path=data["project_path"],
            started_at=data["started_at"],
            updated_at=data["updated_at"],
            current_stage=data["current_stage"],
            current_status=data["current_status"],
            stages=data.get("stages", []),
            progress=data.get("progress", 0.0),
            error_message=data.get("error_message"),
        )

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> SessionState:
        return cls.from_dict(json.loads(json_str))

    def to_pipeline_snapshot(self) -> PipelineSnapshot:
        """Convert SessionState to a PipelineSnapshot for TUI rendering."""
        return PipelineSnapshot(
            session_id=self.session_id,
            timestamp=self.updated_at,
            current_stage=StageId(self.current_stage),
            current_status=StageStatus(self.current_status),
            stages=[StageState.from_dict(s) for s in self.stages],
            progress=self.progress,
            error_message=self.error_message,
        )

    @classmethod
    def from_pipeline_snapshot(cls, snapshot: PipelineSnapshot, project_path: str) -> SessionState:
        """Create SessionState from a PipelineSnapshot."""
        return cls(
            session_id=snapshot.session_id,
            project_path=project_path,
            started_at=snapshot.timestamp,
            updated_at=now_iso(),
            current_stage=snapshot.current_stage.value,
            current_status=snapshot.current_status.value,
            stages=[s.to_dict() for s in snapshot.stages],
            progress=snapshot.progress,
            error_message=snapshot.error_message,
        )


class SessionManager:
    """Manages session state persistence to session-start.json."""

    def __init__(self, project_path: str | Path) -> None:
        self.project_path = Path(project_path)
        self.session_file = self.project_path / ".to-vibe" / "session-start.json"

    def save(self, state: SessionState) -> None:
        """Save session state to disk."""
        state.updated_at = now_iso()
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        self.session_file.write_text(state.to_json(), encoding="utf-8")

    def load(self) -> SessionState | None:
        """Load session state from disk, or None if not found."""
        if not self.session_file.exists():
            return None
        try:
            return SessionState.from_json(self.session_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, KeyError):
            return None

    def clear(self) -> None:
        """Delete the session file."""
        if self.session_file.exists():
            self.session_file.unlink()

    def new_session(self, project_path: str | Path) -> SessionState:
        """Create a brand new session state."""
        return SessionState(
            session_id=new_session_id(),
            project_path=str(project_path),
            started_at=now_iso(),
            updated_at=now_iso(),
            current_stage="evidence",
            current_status=StageStatus.PENDING.value,
            stages=[],
            progress=0.0,
            error_message=None,
        )