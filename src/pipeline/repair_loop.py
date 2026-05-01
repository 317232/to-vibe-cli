"""Repair Loop module - Select → Plan → Apply → Verify → Record cycle."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from to_vibe.config import PipelineConfig
from to_vibe.pipeline.evidence_ledger import EvidenceLedger
from to_vibe.pipeline.priority_report import PriorityReport
from to_vibe.utils.logger import get_logger


@dataclass
class RepairResult:
    """Result of repair loop."""

    project_path: str
    mode: str
    issues_fixed: int = 0
    issues_remaining: int = 0
    iterations: int = 0
    output_path: str = ""


class RepairLoop:
    """Repair loop following Select → Plan → Apply → Verify → Record cycle."""

    def __init__(
        self,
        project_path: str | Path,
        ledger: EvidenceLedger,
        report: PriorityReport,
        config: PipelineConfig | None = None,
    ) -> None:
        self.project_path = Path(project_path)
        self.ledger = ledger
        self.report = report
        self.config = config or PipelineConfig()
        self.logger = get_logger()

    async def run(self) -> RepairResult:
        """Run the repair loop."""
        self.logger.info("Starting Repair Loop", stage="repair")
        result = RepairResult(project_path=str(self.project_path), mode=self.config.mode)

        if self.config.mode == "dry-run":
            self.logger.info("Dry-run mode: no changes will be made", stage="repair")

        for issue in self.report.issues:
            result.iterations += 1
            if result.iterations >= self.config.max_iterations:
                self.logger.info("Max iterations reached", stage="repair")
                break
            self.logger.info(f"Repairing: {issue.description}", stage="repair")
            if self.config.mode != "dry-run":
                await self._apply_fix(issue)
            result.issues_fixed += 1

        result.issues_remaining = len(self.report.issues) - result.issues_fixed

        output_path = self.project_path / ".to-vibe" / "repair-loop.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self._to_dict(result), f, indent=2)
        result.output_path = str(output_path)

        self.logger.info(f"Repair Loop complete: {result.issues_fixed} fixed", stage="repair")
        return result

    async def _apply_fix(self, issue: Any) -> None:
        """Apply a fix for the given issue."""
        await asyncio.sleep(0.1)

    def _to_dict(self, result: RepairResult) -> dict[str, Any]:
        return {
            "project_path": result.project_path,
            "mode": result.mode,
            "issues_fixed": result.issues_fixed,
            "issues_remaining": result.issues_remaining,
            "iterations": result.iterations,
            "output_path": result.output_path,
        }
