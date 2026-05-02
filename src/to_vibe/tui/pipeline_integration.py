"""TUI pipeline integration — wires TUI components to pipeline events."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from to_vibe.pipeline.event_bus import PipelineEventBus, PipelineEvent
from to_vibe.pipeline.state_machine import PipelineStateMachine, PipelineStage
from to_vibe.tui.state_store import (
    TUIStateStore,
    SessionData,
)
from to_vibe.tui.state_models import (
    EvidenceData,
    PriorityData,
    VerifyRow,
    RepairData,
    LearnData,
    LearnDetailView,
    LogEntry,
    ArtifactItem,
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

    def __init__(self, project_path: str | Path, store: TUIStateStore) -> None:
        self.project_path = Path(project_path)
        self._worker_task: asyncio.Task | None = None

        self.store = store
        self.state_machine = PipelineStateMachine()
        self.store.bind_pipeline(self.state_machine)

        PipelineEventBus.subscribe(_LogStreamHandler(self.store))

        # Notify session start
        self.store.update_session(SessionData(
            project_path=str(self.project_path),
            mode="dry-run",
            executor="local",
        ))

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
                ignored_dirs=ledger.ignored_dirs,
                output_path=ledger.output_path,
            ))
            self._scan_artifacts()

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
                suggested_capability=report.suggested_capability,
            ))
            self._scan_artifacts()

            # Stage 3: Verify
            PipelineEventBus.stage_start("verify")
            from to_vibe.pipeline.baseline_verify import BaselineVerifier
            verifier = BaselineVerifier(self.project_path, config.pipeline.verify)
            verify_result = await verifier.verify()
            PipelineEventBus.stage_complete("verify")

            rows = []
            for i, layer in enumerate(verify_result.layer_results, 1):
                status_str = layer.status
                rows.append(VerifyRow(id=i, check=layer.check, status=status_str, command=layer.command))
            self.store.update_verify(rows)
            self._scan_artifacts()

            # Stage 4: Repair
            PipelineEventBus.stage_start("repair")
            self.store.update_repair(RepairData(
                selected_issue=report.top_issue,
                capability=report.suggested_capability,
                mode=config.pipeline.mode,
                apply="skipped",
                record=str(self.project_path / ".to-vibe" / "repair-loop.json"),
                next_action="running repair loop...",
                latest_event="entering repair loop",
                latest_time="",
            ))
            from to_vibe.pipeline.repair_loop import RepairLoop
            repair_loop = RepairLoop(self.project_path, ledger, report, config.pipeline)
            repair_result = await repair_loop.run()
            PipelineEventBus.stage_complete("repair")

            self.store.update_repair(RepairData(
                selected_issue=report.top_issue,
                capability=report.suggested_capability,
                mode=config.pipeline.mode,
                apply="skipped" if config.pipeline.mode == "dry-run" else "applied",
                record=str(self.project_path / ".to-vibe" / "repair-loop.json"),
                next_action="completed",
                latest_event="repair loop finished",
                latest_time="",
            ))
            self._scan_artifacts()

            # Stage 5: Learn
            PipelineEventBus.stage_start("learn")
            from to_vibe.learn.learn import LearnAPI
            learn_api = LearnAPI(self.project_path)
            learn_result = learn_api.run()
            detail_view = learn_api.get_detail_view()
            PipelineEventBus.stage_complete("learn")

            self.store.update_learn(LearnData(
                status="completed",
                records=learn_result.pending_review,
                focus="Patterns & fixes",
                source="Verified issues",
                detail_view=detail_view,
                is_detail=False,
            ))
            self._scan_artifacts()

            PipelineEventBus.info("complete", "Pipeline completed successfully")

        except Exception as e:
            PipelineEventBus.stage_fail(self.store.get_current_stage(), str(e))
            raise

    def pause(self) -> None:
        self.state_machine.request_pause()

    def resume(self) -> None:
        self.state_machine.resume()

    def retry(self) -> None:
        self.state_machine.retry_stage()

    def skip(self) -> None:
        current = self.store.get_current_stage()
        from to_vibe.pipeline.control import SkipPolicy
        policy = SkipPolicy()
        allowed, _ = policy.can_skip(current, reason="user_requested")
        if allowed:
            from to_vibe.pipeline.state_machine import PipelineStage, StageStatus
            target = PipelineStage(current)
            if target in self.state_machine.state.stages:
                self.state_machine.state.stages[target] = StageStatus.SKIPPED
                self.state_machine._emit()

    def stop(self) -> None:
        if self._worker_task:
            self._worker_task.cancel()
            self._worker_task = None

    def _scan_artifacts(self) -> None:
        """Scan .to-vibe/ directory and update artifacts store."""
        to_vibe_dir = self.project_path / ".to-vibe"
        if not to_vibe_dir.exists():
            return

        items = []
        known_files = [
            "evidence-ledger.json",
            "priority-report.md",
            "baseline-verify.json",
            "repair-plan.md",
        ]
        for name in known_files:
            path = to_vibe_dir / name
            if path.exists():
                items.append(ArtifactItem(name=name, is_directory=False))

        claude_tasks = to_vibe_dir / "claude-tasks"
        if claude_tasks.exists() and claude_tasks.is_dir():
            items.append(ArtifactItem(name="claude-tasks/", is_directory=True))
            for child in claude_tasks.iterdir():
                items.append(ArtifactItem(name=f"claude-tasks/{child.name}", is_directory=child.is_dir()))

        self.store.update_artifacts(items)