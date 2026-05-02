"""Unified TUI data models — single source of truth for all UI dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvidenceData:
    tech_stack: list[str] = field(default_factory=list)
    files_scanned: int = 0
    ignored_dirs: list[str] = field(default_factory=list)
    output_path: str = ""


@dataclass
class PriorityData:
    blockers: int = 0
    high: int = 0
    medium: int = 0
    top_issue: str = ""
    suggested_capability: str = ""


@dataclass
class VerifyRow:
    id: int
    check: str
    status: str  # pass / fail / skipped / active
    command: str = ""
    icon: str = ""


@dataclass
class RepairData:
    selected_issue: str = ""
    capability: str = ""
    mode: str = "dry-run"
    apply: str = "skipped"
    record: str = ".to-vibe/repair-loop.json"
    next_action: str = ""
    latest_event: str = ""
    latest_time: str = ""


@dataclass
class LearnDetailView:
    """Detail view for learn panel — shown when user presses Enter on a record."""
    verified_fixes: list[dict[str, Any]] = field(default_factory=list)
    issue_patterns: list[dict[str, Any]] = field(default_factory=list)
    project_facts: list[dict[str, Any]] = field(default_factory=list)
    user_rules: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class LearnData:
    status: str = "pending"
    records: int = 0
    focus: str = "Patterns & fixes"
    source: str = "Verified issues"
    detail_view: LearnDetailView | None = None
    is_detail: bool = False


@dataclass
class LogEntry:
    timestamp: str = ""
    level: str = "INFO"  # INFO / WARN / ERROR
    message: str = ""


@dataclass
class ArtifactItem:
    name: str = ""
    is_directory: bool = False


@dataclass
class SessionData:
    project_path: str = ""
    mode: str = "dry-run"
    executor: str = "local"
    current_stage: str = "idle"
    progress: float = 0.0
    error: str | None = None


@dataclass
class StageState:
    stage_id: str
    stage_name: str
    status: str = "pending"  # pending / running / completed / failed / skipped
