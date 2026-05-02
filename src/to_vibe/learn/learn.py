"""Learn module — MVP: Collect → Filter → Review → Store → Detail."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from to_vibe.learn.collector import LearnCollector as _Collector
from to_vibe.learn.models import LearnCandidate, LearnRecord, LearnType, ReviewAction, VerifyStatus
from to_vibe.learn.storage import LearnStorage
from to_vibe.utils.logger import get_logger


@dataclass
class LearnResult:
    """Result of a learn collection run."""

    project_path: str
    candidates_found: int = 0
    candidates_filtered: int = 0
    pending_review: int = 0
    accepted: int = 0
    rejected: int = 0
    output_path: str = ""


@dataclass
class LearnDetailView:
    """Expanded view of learn records for the UI."""

    verified_fixes: list[dict[str, Any]] = field(default_factory=list)
    issue_patterns: list[dict[str, Any]] = field(default_factory=list)
    project_facts: list[dict[str, Any]] = field(default_factory=list)
    user_rules: list[dict[str, Any]] = field(default_factory=list)


class LearnEngine:
    """Main learn engine implementing the MVP flow."""

    def __init__(self, project_path: str | Path) -> None:
        self.project_path = Path(project_path)
        self.logger = get_logger()
        self.collector = _Collector(project_path)
        self.storage = LearnStorage(project_path)
        self._project_id = self._calc_project_id()

    def _calc_project_id(self) -> str:
        return hashlib.md5(str(self.project_path).encode()).hexdigest()[:8]

    def run(self) -> LearnResult:
        """Execute the full Collect → Filter → Review → Store flow."""
        self.logger.info("Starting Learn MVP flow", stage="learn")

        result = LearnResult(project_path=str(self.project_path))

        # Step 1: Collect
        candidates = self.collector.collect()
        result.candidates_found = len(candidates)

        # Step 2: Filter — drop records with no source_artifact or no evidence_refs
        filtered = [
            c for c in candidates
            if c.source_artifact and c.evidence_refs
        ]
        result.candidates_filtered = len(filtered)

        # Step 3: Store as pending records
        pending = []
        for candidate in filtered:
            record = candidate.to_learn_record(self._project_id)
            self.storage.save_record(record)
            pending.append(record)

        result.pending_review = len(pending)

        # Write learn-summary.md for human readability
        self._write_summary(pending)

        self.logger.info(
            f"Learn MVP: {result.candidates_found} found, "
            f"{result.candidates_filtered} stored, "
            f"{result.pending_review} pending review",
            stage="learn",
        )

        return result

    def get_detail_view(self) -> LearnDetailView:
        """Return structured detail view for TUI."""
        records = self.storage.get_records_by_project(self._project_id)

        view = LearnDetailView()
        for record in records:
            item = {
                "id": record.id,
                "title": record.title,
                "summary": record.summary,
                "source": record.source_artifact,
                "confidence": record.confidence,
                "verify_status": record.verify_status.value,
                "pinned": record.pinned,
            }

            if record.record_type == LearnType.VERIFIED_FIX:
                view.verified_fixes.append(item)
            elif record.record_type == LearnType.ISSUE_PATTERN:
                view.issue_patterns.append(item)
            elif record.record_type == LearnType.PROJECT_FACT:
                view.project_facts.append(item)
            elif record.record_type == LearnType.USER_CONFIRMED_RULE:
                view.user_rules.append(item)

        return view

    def apply_action(self, action: ReviewAction) -> LearnRecord | None:
        """Apply a user action (accept/reject/edit/pin/delete) to a record."""
        return self.storage.apply_review_action(action)

    def get_pending_count(self) -> int:
        """Return count of pending review records."""
        return len(self.storage.get_pending_records(self._project_id))

    def _write_summary(self, pending: list[LearnRecord]) -> None:
        """Write human-readable learn-summary.md."""
        learn_dir = self.project_path / ".to-vibe" / "learn"
        learn_dir.mkdir(parents=True, exist_ok=True)

        lines = ["# Learn Summary\n", f"Project: {self.project_path}\n\n"]

        by_type: dict[LearnType, list[LearnRecord]] = {}
        for rec in pending:
            by_type.setdefault(rec.record_type, []).append(rec)

        for lt, recs in by_type.items():
            lines.append(f"## {lt.value.replace('_', ' ').title()}\n")
            for rec in recs:
                lines.append(f"- **{rec.title}** (confidence: {rec.confidence})\n")
                lines.append(f"  - {rec.summary}\n")
                lines.append(f"  - source: {rec.source_artifact}\n\n")

        summary_path = learn_dir / "learn-summary.md"
        summary_path.write_text("".join(lines), encoding="utf-8")


class LearnCollector:
    """Legacy wrapper for existing LearnCollector interface."""

    def __init__(self, project_path: str | Path, config: Any | None = None) -> None:
        self._engine = LearnEngine(project_path)

    def collect(self) -> dict[str, Any]:
        result = self._engine.run()
        return {
            "project_path": result.project_path,
            "items_learned": result.pending_review,
            "items_total": result.candidates_found,
            "output_path": result.output_path,
        }


class LearnAPI:
    """Public API for Learn module — use this from TUI/pipeline."""

    def __init__(self, project_path: str | Path) -> None:
        self._engine = LearnEngine(project_path)

    def run(self) -> LearnResult:
        return self._engine.run()

    def get_detail_view(self) -> LearnDetailView:
        return self._engine.get_detail_view()

    def apply_action(self, action: ReviewAction) -> LearnRecord | None:
        return self._engine.apply_action(action)

    def get_pending_count(self) -> int:
        return self._engine.get_pending_count()