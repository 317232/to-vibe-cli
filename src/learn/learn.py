"""Learn module - extracts and stores learnings from pipeline artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from to_vibe.config import LearnConfig
from to_vibe.utils.logger import get_logger


@dataclass
class LearnedItem:
    """Single learned item."""

    item_type: str
    content: str
    source: str
    confidence: float = 0.5
    verified: bool = False


@dataclass
class LearnResult:
    """Result of learn operation."""

    project_path: str
    items_learned: int = 0
    items_total: int = 0
    output_path: str = ""


class LearnCollector:
    """Collects learnings from pipeline artifacts."""

    def __init__(self, project_path: str | Path, config: LearnConfig | None = None) -> None:
        self.project_path = Path(project_path)
        self.config = config or LearnConfig()
        self.logger = get_logger()

    def collect(self) -> LearnResult:
        """Collect learnings from all pipeline artifacts."""
        self.logger.info("Starting Learn collection", stage="learn")
        result = LearnResult(project_path=str(self.project_path))
        items: list[LearnedItem] = []

        # Collect from Evidence Ledger
        evidence_path = self.project_path / ".to-vibe" / "evidence-ledger.json"
        if evidence_path.exists():
            with open(evidence_path, "r", encoding="utf-8") as f:
                evidence = json.load(f)
                for fact in evidence.get("tech_stack", []):
                    items.append(LearnedItem(
                        item_type="project_fact",
                        content=f"Tech stack: {fact}",
                        source="evidence-ledger.json",
                        confidence=0.8,
                    ))

        # Collect from Priority Report
        priority_path = self.project_path / ".to-vibe" / "priority-report.json"
        if priority_path.exists():
            with open(priority_path, "r", encoding="utf-8") as f:
                priority = json.load(f)
                for issue in priority.get("issues", []):
                    items.append(LearnedItem(
                        item_type="issue_pattern",
                        content=f"Issue: {issue.get('description')}",
                        source="priority-report.json",
                        confidence=0.6,
                    ))

        # Collect from Repair Loop
        repair_path = self.project_path / ".to-vibe" / "repair-loop.json"
        if repair_path.exists():
            with open(repair_path, "r", encoding="utf-8") as f:
                repair = json.load(f)
                items.append(LearnedItem(
                    item_type="verified_fix",
                    content=f"Fixed {repair.get('issues_fixed')} issues",
                    source="repair-loop.json",
                    confidence=0.9,
                    verified=True,
                ))

        items = [i for i in items if i.confidence >= self.config.min_confidence]
        result.items_learned = len(items)
        result.items_total = len(items)

        learn_dir = self.project_path / ".to-vibe" / "learn"
        learn_dir.mkdir(parents=True, exist_ok=True)
        output_path = learn_dir / "learn-summary.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self._to_dict(result), f, indent=2)
        result.output_path = str(output_path)

        self.logger.info(f"Learn complete: {result.items_learned} items", stage="learn")
        return result

    def _to_dict(self, result: LearnResult) -> dict[str, Any]:
        return {
            "project_path": result.project_path,
            "items_learned": result.items_learned,
            "items_total": result.items_total,
            "output_path": result.output_path,
        }
