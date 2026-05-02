"""Learn collector — extracts candidates from pipeline artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from to_vibe.learn.models import LearnCandidate, LearnType
from to_vibe.utils.logger import get_logger


class ArtifactCollector:
    """Collects learning candidates from pipeline artifacts.

    Follows the 7-step flow: Collect → Filter → Summarize → Validate → Review → Store → Retrieve
    MVP only implements Collect → Filter → Review → Store.
    """

    def __init__(self, project_path: str | Path) -> None:
        self.project_path = Path(project_path)
        self.logger = get_logger()

    def collect(self) -> list[LearnCandidate]:
        """Collect learning candidates from all available artifacts.

        Returns:
            List of LearnCandidate objects ready for review
        """
        self.logger.info("Collecting learn candidates", stage="learn")

        candidates: list[LearnCandidate] = []

        # 1. Collect from Evidence Ledger
        evidence_path = self.project_path / ".to-vibe" / "evidence-ledger.json"
        if evidence_path.exists():
            candidates.extend(self._collect_from_evidence(evidence_path))

        # 2. Collect from Priority Report
        priority_path = self.project_path / ".to-vibe" / "priority-report.json"
        if priority_path.exists():
            candidates.extend(self._collect_from_priority(priority_path))

        # 3. Collect from Baseline Verify
        verify_path = self.project_path / ".to-vibe" / "baseline-verify.json"
        if verify_path.exists():
            candidates.extend(self._collect_from_verify(verify_path))

        # 4. Collect from Repair Loop
        repair_path = self.project_path / ".to-vibe" / "repair-loop.json"
        if repair_path.exists():
            candidates.extend(self._collect_from_repair(repair_path))

        self.logger.info(f"Collected {len(candidates)} candidates", stage="learn")
        return candidates

    def _collect_from_evidence(self, path: Path) -> list[LearnCandidate]:
        """Extract project facts from evidence ledger."""
        candidates = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            project_id = hashlib.md5(str(self.project_path).encode()).hexdigest()[:8]

            # Tech stack facts
            for tech in data.get("tech_stack", []):
                candidates.append(LearnCandidate(
                    record_type=LearnType.PROJECT_FACT,
                    title=f"Uses {tech}",
                    summary=f"Project uses {tech} as package manager or framework",
                    source_artifact="evidence-ledger.json",
                    evidence_refs=[f"tech_stack: {tech}"],
                    confidence=0.8,
                    project_id=project_id,
                ))

            # File structure facts
            for fact in data.get("facts", [])[:20]:
                if fact.get("category") == "framework":
                    candidates.append(LearnCandidate(
                        record_type=LearnType.PROJECT_FACT,
                        title=fact.get("fact", "")[:80],
                        summary=fact.get("fact", ""),
                        source_artifact="evidence-ledger.json",
                        evidence_refs=[fact.get("file_path", "")],
                        confidence=fact.get("confidence", 0.7),
                        project_id=project_id,
                    ))

        except (json.JSONDecodeError, OSError) as e:
            self.logger.warning(f"Failed to read evidence ledger: {e}", stage="learn")

        return candidates

    def _collect_from_priority(self, path: Path) -> list[LearnCandidate]:
        """Extract issue patterns from priority report."""
        candidates = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            project_id = hashlib.md5(str(self.project_path).encode()).hexdigest()[:8]

            # P0 blockers become high-priority issue patterns
            for blocker in data.get("blockers", []):
                candidates.append(LearnCandidate(
                    record_type=LearnType.ISSUE_PATTERN,
                    title=f"[P0] {blocker.get('title', 'Blocker')[:80]}",
                    summary=blocker.get("description", ""),
                    source_artifact="priority-report.json",
                    evidence_refs=blocker.get("evidence_refs", []),
                    confidence=0.9,
                    project_id=project_id,
                ))

            # P1 issues
            for issue in data.get("high_priority", []):
                candidates.append(LearnCandidate(
                    record_type=LearnType.ISSUE_PATTERN,
                    title=f"[P1] {issue.get('title', 'Issue')[:80]}",
                    summary=issue.get("description", ""),
                    source_artifact="priority-report.json",
                    evidence_refs=issue.get("evidence_refs", []),
                    confidence=0.7,
                    project_id=project_id,
                ))

        except (json.JSONDecodeError, OSError) as e:
            self.logger.warning(f"Failed to read priority report: {e}", stage="learn")

        return candidates

    def _collect_from_verify(self, path: Path) -> list[LearnCandidate]:
        """Extract verified fixes from baseline verify results."""
        candidates = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            project_id = hashlib.md5(str(self.project_path).encode()).hexdigest()[:8]

            for layer in ["L1", "L2", "L3", "L4", "L5"]:
                layer_data = data.get("layers", {}).get(layer, {})
                if layer_data.get("status") == "fail":
                    candidates.append(LearnCandidate(
                        record_type=LearnType.ISSUE_PATTERN,
                        title=f"Verify {layer} failed",
                        summary=layer_data.get("error", "Build verification failed"),
                        source_artifact="baseline-verify.json",
                        evidence_refs=[f"layer: {layer}", f"command: {layer_data.get('command', '')}"],
                        confidence=0.8,
                        project_id=project_id,
                    ))
                elif layer_data.get("status") == "pass":
                    candidates.append(LearnCandidate(
                        record_type=LearnType.VERIFIED_FIX,
                        title=f"Verify {layer} passed",
                        summary=f"Layer {layer} verification succeeded",
                        source_artifact="baseline-verify.json",
                        evidence_refs=[f"layer: {layer}"],
                        confidence=0.9,
                        project_id=project_id,
                    ))

        except (json.JSONDecodeError, OSError) as e:
            self.logger.warning(f"Failed to read baseline verify: {e}", stage="learn")

        return candidates

    def _collect_from_repair(self, path: Path) -> list[LearnCandidate]:
        """Extract verified fixes from repair loop."""
        candidates = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            project_id = hashlib.md5(str(self.project_path).encode()).hexdigest()[:8]

            for repair in data.get("repairs", []):
                if repair.get("status") == "verified":
                    candidates.append(LearnCandidate(
                        record_type=LearnType.VERIFIED_FIX,
                        title=f"Fixed: {repair.get('issue_title', 'Repair')[:80]}",
                        summary=repair.get("description", ""),
                        source_artifact="repair-loop.json",
                        evidence_refs=repair.get("evidence_refs", []),
                        confidence=0.9,
                        project_id=project_id,
                    ))

        except (json.JSONDecodeError, OSError) as e:
            self.logger.warning(f"Failed to read repair loop: {e}", stage="learn")

        return candidates