"""Learn data models — 4 types of memory records."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class LearnType(str, Enum):
    """Types of learning records."""

    PROJECT_FACT = "project_fact"
    VERIFIED_FIX = "verified_fix"
    ISSUE_PATTERN = "issue_pattern"
    USER_CONFIRMED_RULE = "user_confirmed_rule"


class VerifyStatus(str, Enum):
    """Verification status for learn records."""

    PENDING = "pending"
    PASSED = "passed"
    REJECTED = "rejected"


@dataclass
class LearnRecord:
    """Single learning record, stored in SQLite."""

    id: str
    record_type: LearnType
    project_id: str
    session_id: str | None = None
    issue_id: str | None = None
    capability: str | None = None
    title: str = ""
    summary: str = ""
    source_artifact: str = ""
    evidence_refs: list[str] = field(default_factory=list)
    verify_status: VerifyStatus = VerifyStatus.PENDING
    confidence: float = 0.5
    accepted_by_user: bool = False
    pinned: bool = False
    created_at: str = ""
    updated_at: str = ""
    content_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "record_type": self.record_type.value,
            "project_id": self.project_id,
            "session_id": self.session_id,
            "issue_id": self.issue_id,
            "capability": self.capability,
            "title": self.title,
            "summary": self.summary,
            "source_artifact": self.source_artifact,
            "evidence_refs": self.evidence_refs,
            "verify_status": self.verify_status.value,
            "confidence": self.confidence,
            "accepted_by_user": self.accepted_by_user,
            "pinned": self.pinned,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "content_hash": self.content_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LearnRecord:
        return cls(
            id=data["id"],
            record_type=LearnType(data["record_type"]),
            project_id=data["project_id"],
            session_id=data.get("session_id"),
            issue_id=data.get("issue_id"),
            capability=data.get("capability"),
            title=data.get("title", ""),
            summary=data.get("summary", ""),
            source_artifact=data.get("source_artifact", ""),
            evidence_refs=data.get("evidence_refs", []),
            verify_status=VerifyStatus(data.get("verify_status", "pending")),
            confidence=data.get("confidence", 0.5),
            accepted_by_user=data.get("accepted_by_user", False),
            pinned=data.get("pinned", False),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            content_hash=data.get("content_hash", ""),
        )

    @classmethod
    def new(
        cls,
        record_type: LearnType,
        project_id: str,
        title: str = "",
        summary: str = "",
        source_artifact: str = "",
        evidence_refs: list[str] | None = None,
        confidence: float = 0.5,
    ) -> LearnRecord:
        now = datetime.now().isoformat(timespec="milliseconds")
        return cls(
            id=str(uuid.uuid4())[:12],
            record_type=record_type,
            project_id=project_id,
            title=title,
            summary=summary,
            source_artifact=source_artifact,
            evidence_refs=evidence_refs or [],
            confidence=confidence,
            verify_status=VerifyStatus.PENDING,
            created_at=now,
            updated_at=now,
        )


@dataclass
class LearnCandidate:
    """Pre-review candidate extracted from pipeline artifacts."""

    record_type: LearnType
    title: str
    summary: str
    source_artifact: str
    evidence_refs: list[str] = field(default_factory=list)
    confidence: float = 0.5
    project_id: str = ""
    session_id: str | None = None
    issue_id: str | None = None

    def to_learn_record(self, project_id: str) -> LearnRecord:
        return LearnRecord.new(
            record_type=self.record_type,
            project_id=project_id,
            title=self.title,
            summary=self.summary,
            source_artifact=self.source_artifact,
            evidence_refs=self.evidence_refs,
            confidence=self.confidence,
        )


@dataclass
class ReviewAction:
    """User action on a learn record."""

    record_id: str
    action: str  # "accept" | "reject" | "edit" | "pin" | "delete"
    edited_summary: str | None = None
    edited_title: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat(timespec="milliseconds"))