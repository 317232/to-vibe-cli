"""Learn storage — SQLite + human-readable files."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from to_vibe.learn.models import LearnRecord, LearnType, ReviewAction, VerifyStatus
from to_vibe.utils.logger import get_logger


class LearnStorage:
    """Stores learn records in SQLite and .to-vibe/learn/ files."""

    def __init__(self, project_path: str | Path) -> None:
        self.project_path = Path(project_path)
        self.learn_dir = self.project_path / ".to-vibe" / "learn"
        self.db_path = self.learn_dir / "learn.db"
        self._logger = get_logger()
        self._init_db()

    def _init_db(self) -> None:
        """Initialize SQLite database and tables."""
        self.learn_dir.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS learn_records (
                id TEXT PRIMARY KEY,
                record_type TEXT NOT NULL,
                project_id TEXT NOT NULL,
                session_id TEXT,
                issue_id TEXT,
                capability TEXT,
                title TEXT,
                summary TEXT,
                source_artifact TEXT,
                evidence_refs TEXT,
                verify_status TEXT,
                confidence REAL DEFAULT 0.5,
                accepted_by_user INTEGER DEFAULT 0,
                pinned INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                content_hash TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_project ON learn_records(project_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON learn_records(record_type)")
        conn.commit()
        conn.close()

    def save_record(self, record: LearnRecord) -> None:
        """Save a learn record to SQLite."""
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            INSERT OR REPLACE INTO learn_records
            (id, record_type, project_id, session_id, issue_id, capability, title, summary,
             source_artifact, evidence_refs, verify_status, confidence, accepted_by_user,
             pinned, created_at, updated_at, content_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.id,
            record.record_type.value,
            record.project_id,
            record.session_id,
            record.issue_id,
            record.capability,
            record.title,
            record.summary,
            record.source_artifact,
            json.dumps(record.evidence_refs),
            record.verify_status.value,
            record.confidence,
            int(record.accepted_by_user),
            int(record.pinned),
            record.created_at,
            record.updated_at,
            record.content_hash,
        ))
        conn.commit()
        conn.close()
        self._logger.debug(f"Saved learn record {record.id}", stage="learn")

    def get_records_by_project(self, project_id: str) -> list[LearnRecord]:
        """Get all learn records for a project."""
        conn = sqlite3.connect(str(self.db_path))
        rows = conn.execute(
            "SELECT * FROM learn_records WHERE project_id = ? ORDER BY created_at DESC",
            (project_id,),
        ).fetchall()
        conn.close()
        return [self._row_to_record(row) for row in rows]

    def get_pending_records(self, project_id: str) -> list[LearnRecord]:
        """Get all pending (not yet reviewed) records."""
        conn = sqlite3.connect(str(self.db_path))
        rows = conn.execute(
            "SELECT * FROM learn_records WHERE project_id = ? AND verify_status = ? ORDER BY created_at DESC",
            (project_id, VerifyStatus.PENDING.value),
        ).fetchall()
        conn.close()
        return [self._row_to_record(row) for row in rows]

    def get_records_by_type(self, project_id: str, rec_type: LearnType) -> list[LearnRecord]:
        """Get learn records filtered by type."""
        conn = sqlite3.connect(str(self.db_path))
        rows = conn.execute(
            "SELECT * FROM learn_records WHERE project_id = ? AND record_type = ? ORDER BY created_at DESC",
            (project_id, rec_type.value),
        ).fetchall()
        conn.close()
        return [self._row_to_record(row) for row in rows]

    def apply_review_action(self, action: ReviewAction) -> LearnRecord | None:
        """Apply a user review action to a record.

        Args:
            action: ReviewAction with record_id and action (accept/reject/edit/pin/delete)

        Returns:
            Updated LearnRecord or None if deleted
        """
        conn = sqlite3.connect(str(self.db_path))
        row = conn.execute(
            "SELECT * FROM learn_records WHERE id = ?", (action.record_id,)
        ).fetchone()
        if not row:
            conn.close()
            return None

        record = self._row_to_record(row)

        if action.action == "accept":
            record.verify_status = VerifyStatus.PASSED
            record.accepted_by_user = True
        elif action.action == "reject":
            record.verify_status = VerifyStatus.REJECTED
            self._append_to_file("rejected-lessons.json", record)
        elif action.action == "edit":
            if action.edited_title is not None:
                record.title = action.edited_title
            if action.edited_summary is not None:
                record.summary = action.edited_summary
        elif action.action == "pin":
            record.pinned = not record.pinned
        elif action.action == "delete":
            conn.execute("DELETE FROM learn_records WHERE id = ?", (action.record_id,))
            conn.commit()
            conn.close()
            return None

        record.updated_at = action.timestamp
        conn.execute(
            "UPDATE learn_records SET verify_status=?, accepted_by_user=?, pinned=?, "
            "title=?, summary=?, updated_at=? WHERE id=?",
            (
                record.verify_status.value,
                int(record.accepted_by_user),
                int(record.pinned),
                record.title,
                record.summary,
                record.updated_at,
                record.id,
            )
        )
        conn.commit()
        conn.close()

        if record.accepted_by_user:
            self._append_to_file("learned-rules.json", record)

        return record

    def _append_to_file(self, filename: str, record: LearnRecord) -> None:
        """Append a record to a JSON file."""
        file_path = self.learn_dir / filename
        items = []
        if file_path.exists():
            try:
                items = json.loads(file_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                items = []
        items.append(record.to_dict())
        file_path.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")

    def _row_to_record(self, row: tuple[Any, ...]) -> LearnRecord:
        """Convert SQLite row to LearnRecord."""
        return LearnRecord(
            id=row[0],
            record_type=LearnType(row[1]),
            project_id=row[2],
            session_id=row[3],
            issue_id=row[4],
            capability=row[5],
            title=row[6],
            summary=row[7],
            source_artifact=row[8],
            evidence_refs=json.loads(row[9]) if row[9] else [],
            verify_status=VerifyStatus(row[10]),
            confidence=row[11],
            accepted_by_user=bool(row[12]),
            pinned=bool(row[13]),
            created_at=row[14],
            updated_at=row[15],
            content_hash=row[16] or "",
        )

    def count_records(self, project_id: str) -> int:
        """Count total records for a project."""
        conn = sqlite3.connect(str(self.db_path))
        count = conn.execute(
            "SELECT COUNT(*) FROM learn_records WHERE project_id = ?",
            (project_id,),
        ).fetchone()[0]
        conn.close()
        return count