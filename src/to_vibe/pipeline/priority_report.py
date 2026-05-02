"""Priority Report module - analyzes issues and generates priority roadmap."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from to_vibe.pipeline.evidence_ledger import EvidenceLedger
from to_vibe.utils.logger import get_logger


@dataclass
class Issue:
    """Single issue with priority."""

    priority: str
    issue_type: str
    description: str
    suggested_capability: str


@dataclass
class PriorityReport:
    """Priority report with ranked issue roadmap."""

    project_path: str
    blockers: int = 0
    high: int = 0
    medium: int = 0
    issues: list[Issue] = field(default_factory=list)
    top_issue: str = ""
    suggested_capability: str = ""
    output_path: str = ""


class PriorityAnalyzer:
    """Analyzes evidence ledger and generates priority report."""

    def __init__(self, ledger: EvidenceLedger) -> None:
        self.ledger = ledger
        self.logger = get_logger()

    def analyze(self) -> PriorityReport:
        """Analyze evidence and generate priority report."""
        self.logger.info("Analyzing priorities", stage="priority")

        report = PriorityReport(project_path=self.ledger.project_path)
        issues = []

        if not self.ledger.tech_stack:
            issues.append(Issue("blocker", "config", "No tech stack detected", "Debug"))
            report.blockers = 1

        if self.ledger.files_scanned == 0:
            issues.append(Issue("high", "structure", "No files scanned", "System"))
            report.high = 1

        report.issues = issues
        if issues:
            report.top_issue = issues[0].description
            report.suggested_capability = issues[0].suggested_capability

        output_path = Path(self.ledger.project_path) / ".to-vibe" / "priority-report.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self._to_dict(report), f, indent=2, ensure_ascii=False)
        report.output_path = str(output_path)

        self.logger.info(f"Priority analysis complete: {report.blockers} blockers", stage="priority")
        return report

    def _to_dict(self, report: PriorityReport) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "project_path": report.project_path,
            "blockers": report.blockers,
            "high": report.high,
            "medium": report.medium,
            "issues": [
                {"priority": i.priority, "type": i.issue_type,
                 "description": i.description, "suggested_capability": i.suggested_capability}
                for i in report.issues
            ],
            "top_issue": report.top_issue,
            "suggested_capability": report.suggested_capability,
            "output_path": report.output_path,
        }
