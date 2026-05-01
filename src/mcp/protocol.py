"""MCP notification protocol types for to-vibe."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class NotificationType(str, Enum):
    """MCP notification types."""

    LOG = "log"
    STAGE_START = "stage_start"
    STAGE_COMPLETE = "stage_complete"
    PROGRESS = "progress"
    EVIDENCE = "evidence"
    ISSUE_FOUND = "issue_found"
    ACTION_REQUIRED = "action_required"
    ERROR = "error"


class Stage(str, Enum):
    """Pipeline stages."""

    EVIDENCE = "evidence"
    PRIORITY = "priority"
    VERIFY = "verify"
    REPAIR = "repair"
    LEARN = "learn"


class IssuePriority(str, Enum):
    """Issue priority levels."""

    BLOCKER = "blocker"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class LogNotification:
    """Log notification payload."""

    text: str
    level: str = "info"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="milliseconds"))


@dataclass
class StageStartNotification:
    """Stage start notification."""

    stage: str
    description: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="milliseconds"))


@dataclass
class StageCompleteNotification:
    """Stage complete notification."""

    stage: str
    summary: str
    results: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="milliseconds"))


@dataclass
class ProgressNotification:
    """Progress update notification."""

    current: int
    total: int
    detail: str = ""


@dataclass
class EvidenceNotification:
    """Evidence found notification."""

    file: str
    line: int
    fact: str
    status: str = "found"


@dataclass
class IssueFoundNotification:
    """Issue found notification."""

    priority: str
    type: str
    description: str


@dataclass
class ActionRequiredNotification:
    """Action required notification."""

    prompt: str
    options: list[str] = field(default_factory=list)
    default: str = ""


@dataclass
class ErrorNotification:
    """Error notification."""

    stage: str
    message: str
    recovery: str = ""


def create_notification(
    notif_type: NotificationType,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Create a notification dictionary.

    Args:
        notif_type: Type of notification
        payload: Notification payload

    Returns:
        Complete notification dictionary
    """
    return {
        "type": notif_type.value,
        "timestamp": datetime.now().isoformat(timespec="milliseconds"),
        "payload": payload,
    }
