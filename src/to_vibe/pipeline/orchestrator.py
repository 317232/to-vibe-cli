"""Pipeline orchestrator - runs all 5 stages in sequence."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from to_vibe.utils.logger import LogEmitter

from to_vibe.config import PipelineConfig, VerifyConfig, LearnConfig, load_config as load_vibe_config
from to_vibe.pipeline.evidence_ledger import EvidenceLedgerScanner, EvidenceLedger
from to_vibe.pipeline.priority_report import PriorityAnalyzer, PriorityReport
from to_vibe.pipeline.baseline_verify import BaselineVerifier, BaselineVerifyResult
from to_vibe.pipeline.repair_loop import RepairLoop, RepairResult
from to_vibe.learn.learn import LegacyLearnCollector, LearnResult
from to_vibe.utils.logger import get_logger


@dataclass
class PipelineContext:
    """Context passed through all pipeline stages."""

    project_path: Path
    config: PipelineConfig
    verify_config: VerifyConfig
    learn_config: LearnConfig
    logger: "LogEmitter | None" = field(default=None, init=False)

    # Stage outputs
    ledger: EvidenceLedger | None = None
    report: PriorityReport | None = None
    verify_result: BaselineVerifyResult | None = None
    repair_result: RepairResult | None = None
    learn_result: LearnResult | None = None

    # Stage metadata
    current_stage: str = "evidence"
    stages_completed: list[str] = field(default_factory=list)
    stages_failed: list[str] = field(default_factory=list)


class PipelineOrchestrator:
    """Runs the full 5-stage to-vibe pipeline."""

    def __init__(self, project_path: str | Path) -> None:
        self.project_path = Path(project_path)
        self.logger = get_logger()
        self._config = load_vibe_config(str(self.project_path))

        self._ctx = PipelineContext(
            project_path=self.project_path,
            config=self._config.pipeline,
            verify_config=self._config.pipeline.verify,
            learn_config=self._config.learn,
        )
        self._ctx.logger = self.logger

    def run(self) -> PipelineContext:
        """Run the full pipeline synchronously.

        Returns:
            PipelineContext with all stage results filled in
        """
        self.logger.info("Starting to-vibe pipeline", stage="evidence")

        # Stage 1: Evidence Ledger
        self._run_evidence()

        # Stage 2: Priority Report
        self._run_priority()

        # Stage 3: Baseline Verify
        self._run_verify()

        # Stage 4: Repair Loop
        self._run_repair()

        # Stage 5: Learn
        self._run_learn()

        self.logger.info("Pipeline complete", stage="learn")
        return self._ctx

    async def run_async(self) -> PipelineContext:
        """Run the full pipeline with async stages.

        Returns:
            PipelineContext with all stage results filled in
        """
        self.logger.info("Starting to-vibe pipeline (async)", stage="evidence")

        # Stage 1: Evidence Ledger (sync)
        self._run_evidence()

        # Stage 2: Priority Report (sync)
        self._run_priority()

        # Stage 3: Baseline Verify (async)
        await self._run_verify_async()

        # Stage 4: Repair Loop (async)
        await self._run_repair_async()

        # Stage 5: Learn (sync)
        self._run_learn()

        self.logger.info("Pipeline complete", stage="learn")
        return self._ctx

    def _run_evidence(self) -> None:
        """Run Evidence Ledger stage."""
        self._ctx.current_stage = "evidence"
        self.logger.info("Running Evidence Ledger scan", stage="evidence")

        scanner = EvidenceLedgerScanner(self.project_path, self._ctx.config)
        self._ctx.ledger = scanner.scan()
        self._ctx.stages_completed.append("evidence")

    def _run_priority(self) -> None:
        """Run Priority Report stage."""
        self._ctx.current_stage = "priority"
        self.logger.info("Running Priority Report analysis", stage="priority")

        analyzer = PriorityAnalyzer(self._ctx.ledger)
        self._ctx.report = analyzer.analyze()
        self._ctx.stages_completed.append("priority")

    def _run_verify(self) -> None:
        """Run Baseline Verify stage (sync wrapper)."""
        self._ctx.current_stage = "verify"
        self.logger.info("Running Baseline Verify", stage="verify")

        verifier = BaselineVerifier(self.project_path, self._ctx.verify_config)
        # sync wrapper for the async verify
        self._ctx.verify_result = asyncio.get_event_loop().run_until_complete(
            verifier.verify()
        )
        self._ctx.stages_completed.append("verify")

    async def _run_verify_async(self) -> None:
        """Run Baseline Verify stage (async)."""
        self._ctx.current_stage = "verify"
        self.logger.info("Running Baseline Verify", stage="verify")

        verifier = BaselineVerifier(self.project_path, self._ctx.verify_config)
        self._ctx.verify_result = await verifier.verify()
        self._ctx.stages_completed.append("verify")

    def _run_repair(self) -> None:
        """Run Repair Loop stage (sync wrapper)."""
        self._ctx.current_stage = "repair"
        self.logger.info("Running Repair Loop", stage="repair")

        loop = RepairLoop(
            self.project_path,
            self._ctx.ledger,
            self._ctx.report,
            self._ctx.config,
        )
        self._ctx.repair_result = asyncio.get_event_loop().run_until_complete(loop.run())
        self._ctx.stages_completed.append("repair")

    async def _run_repair_async(self) -> None:
        """Run Repair Loop stage (async)."""
        self._ctx.current_stage = "repair"
        self.logger.info("Running Repair Loop", stage="repair")

        loop = RepairLoop(
            self.project_path,
            self._ctx.ledger,
            self._ctx.report,
            self._ctx.config,
        )
        self._ctx.repair_result = await loop.run()
        self._ctx.stages_completed.append("repair")

    def _run_learn(self) -> None:
        """Run Learn stage."""
        self._ctx.current_stage = "learn"
        self.logger.info("Running Learn module", stage="learn")

        collector = LearnCollector(self.project_path, self._ctx.learn_config)
        self._ctx.learn_result = collector.collect()
        self._ctx.stages_completed.append("learn")


def run_pipeline(project_path: str | Path) -> PipelineContext:
    """Convenience function to run the full pipeline.

    Args:
        project_path: Path to the project root

    Returns:
        PipelineContext with all stage results
    """
    orchestrator = PipelineOrchestrator(project_path)
    return orchestrator.run()


async def run_pipeline_async(project_path: str | Path) -> PipelineContext:
    """Convenience function to run the full pipeline async.

    Args:
        project_path: Path to the project root

    Returns:
        PipelineContext with all stage results
    """
    orchestrator = PipelineOrchestrator(project_path)
    return await orchestrator.run_async()