"""TUI pipeline integration — wires TUI components to pipeline events."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from to_vibe.pipeline.event_bus import PipelineEventBus, PipelineEvent
from to_vibe.pipeline.state_machine import PipelineStateMachine, PipelineStage
from to_vibe.tui.state_store import (
    TUIStateStore,
    EvidenceData,
    PriorityData,
    VerifyRow,
    RepairData,
    LearnData,
    LogEntry,
)


class _LogStreamHandler:
    """PipelineEventBus subscriber that writes logs to TUIStateStore."""

    def __init__(self, store: TUIStateStore) -> None:
        self._store = store

    def __call__(self, event: PipelineEvent) -> None:
        self._store.append_log(LogEntry(
            timestamp=event.timestamp,
            level=event.level,
            message=event.message,
        ))


class PipelineIntegration:
    """Wires TUI + pipeline + event bus together.

    Created in ToVibeApp.on_mount() and lives as app.integration.
    """

    def __init__(self, project_path: str | Path) -> None:
        self.project_path = Path(project_path)
        self._worker_task: asyncio.Task | None = None

        self.store = TUIStateStore()
        self.state_machine = PipelineStateMachine()
        self.store.bind_pipeline(self.state_machine)

        PipelineEventBus.subscribe(_LogStreamHandler(self.store))

    def start(self) -> None:
        """Start pipeline worker (non-blocking)."""
        self._worker_task = asyncio.create_task(self._run_pipeline())

    async def _run_pipeline(self) -> None:
        """Run pipeline with event bus notifications at each stage."""
        from to_vibe.config import load_config as load_vibe_config

        config = load_vibe_config(str(self.project_path))

        try:
            # Stage 1: Evidence
            PipelineEventBus.stage_start("evidence")
            from to_vibe.pipeline.evidence_ledger import EvidenceLedgerScanner
            scanner = EvidenceLedgerScanner(self.project_path, config.pipeline)
            ledger = scanner.scan()
            PipelineEventBus.stage_complete("evidence")

            self.store.update_evidence(EvidenceData(
                tech_stack=ledger.tech_stack,
                files_scanned=ledger.files_scanned,
                ignored=ledger.ignored_dirs,
                output_path=ledger.output_path,
            ))

            # Stage 2: Priority
            PipelineEventBus.stage_start("priority")
            from to_vibe.pipeline.priority_report import PriorityAnalyzer
            analyzer = PriorityAnalyzer(ledger)
            report = analyzer.analyze()
            PipelineEventBus.stage_complete("priority")

            self.store.update_priority(PriorityData(
                blockers=report.blockers,
                high=report.high,
                medium=report.medium,
                top_issue=report.top_issue,
                suggested=report.suggested_capability,
            ))

            # Stage 3: Verify
            PipelineEventBus.stage_start("verify")
            from to_vibe.pipeline.baseline_verify import BaselineVerifier
            verifier = BaselineVerifier(self.project_path, config.pipeline.verify)
            verify_result = await verifier.verify()
            PipelineEventBus.stage_complete("verify")

            rows = []
            for i, (check_name, status) in enumerate([
                ("Environment", verify_result.environment_status),
                ("Dependencies", verify_result.dependencies_status),
                ("Build", verify_result.build_status),
                ("Start", verify_result.start_status),
                ("Smoke Test", verify_result.smoke_test_status),
            ], 1):
                status_str = status.value if hasattr(status, "value") else str(status)
                rows.append(VerifyRow(id=i, check=check_name, status=status_str, command=f"L{i} check"))
            self.store.update_verify(rows)

            # Stage 4: Repair
            PipelineEventBus.stage_start("repair")
            from to_vibe.pipeline.repair_loop import RepairLoop
            repair_loop = RepairLoop(self.project_path, ledger, report, config.pipeline)
            repair_result = await repair_loop.run()
            PipelineEventBus.stage_complete("repair")

            self.store.update_repair(RepairData(
                selected_issue=report.top_issue,
                capability=report.suggested_capability,
                mode=config.pipeline.mode,
                apply_status="skipped" if config.pipeline.mode == "dry-run" else "applied",
                record_path=str(self.project_path / ".to-vibe" / "repair-loop.json"),
            ))

            # Stage 5: Learn
            PipelineEventBus.stage_start("learn")
            from to_vibe.learn.learn import LegacyLearnCollector
            collector = LegacyLearnCollector(self.project_path, config.learn)
            learn_result = collector.collect()
            PipelineEventBus.stage_complete("learn")

            self.store.update_learn(LearnData(
                status="completed",
                records=learn_result.items_learned,
                focus="Patterns & fixes",
                source="Verified issues",
            ))

            PipelineEventBus.info("complete", "Pipeline completed successfully")

        except Exception as e:
            PipelineEventBus.stage_fail(self.store.get_current_stage(), str(e))
            raise

    def pause(self) -> None:
        self.state_machine.pause()

    def resume(self) -> None:
        self.state_machine.resume()

    def stop(self) -> None:
        if self._worker_task:
            self._worker_task.cancel()
            self._worker_task = None