"""Pipeline state machine — manages lifecycle and drives StageBar/MCP notifications."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Any

from to_vibe.pipeline.orchestrator import PipelineOrchestrator


class PipelineStage(Enum):
    """Pipeline stage enum."""

    IDLE = "idle"
    EVIDENCE = "evidence"
    PRIORITY = "priority"
    VERIFY = "verify"
    REPAIR = "repair"
    LEARN = "learn"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class StageStatus(Enum):
    """Single stage status enum."""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PipelineState:
    """Current pipeline state — published to all subscribers."""

    current_stage: PipelineStage = PipelineStage.IDLE
    current_status: StageStatus = StageStatus.PENDING
    stages: dict[PipelineStage, StageStatus] = field(default_factory=dict)
    progress: float = 0.0  # 0.0 ~ 1.0
    error_message: str | None = None
    _pause_requested: bool = field(default=False, init=False)
    _checkpoint: dict[str, Any] = field(default_factory=dict, init=False)

    _stage_order = [
        PipelineStage.EVIDENCE,
        PipelineStage.PRIORITY,
        PipelineStage.VERIFY,
        PipelineStage.REPAIR,
        PipelineStage.LEARN,
    ]

    def _init_stages(self) -> None:
        for stage in self._stage_order:
            if stage not in self.stages:
                self.stages[stage] = StageStatus.PENDING

    def advance(self, stage: PipelineStage, status: StageStatus) -> None:
        self._init_stages()
        self.stages[stage] = status
        self.current_stage = stage
        self.current_status = status
        self._update_progress()

    def _update_progress(self) -> None:
        self._init_stages()
        completed = sum(
            1 for s, status in self.stages.items()
            if status == StageStatus.COMPLETED
        )
        self.progress = completed / len(self._stage_order)

    def set_error(self, message: str, stage: PipelineStage | None = None) -> None:
        self.error_message = message
        if stage:
            self.current_stage = stage
            self.current_status = StageStatus.FAILED
            self._init_stages()
            self.stages[stage] = StageStatus.FAILED

    def pause(self) -> None:
        """Request pipeline pause at next stage boundary."""
        self._pause_requested = True
        self.current_stage = PipelineStage.PAUSED
        self.current_status = StageStatus.PENDING

    def resume(self) -> None:
        """Clear pause request — runner will continue from checkpoint."""
        self._pause_requested = False
        self._checkpoint = {}

    def reset(self) -> None:
        self.current_stage = PipelineStage.IDLE
        self.current_status = StageStatus.PENDING
        self.stages = {}
        self.progress = 0.0
        self.error_message = None
        self._pause_requested = False
        self._checkpoint = {}

    def get_stage_status(self, stage: PipelineStage) -> StageStatus:
        self._init_stages()
        return self.stages.get(stage, StageStatus.PENDING)


class PipelineStateMachine:
    """Manages pipeline lifecycle, notifies subscribers on state changes."""

    def __init__(self) -> None:
        self._state = PipelineState()
        self._subscribers: list[Callable[[PipelineState], None]] = []
        self._pause_event = asyncio.Event()
        self._pause_event.set()  # initially not paused

    def subscribe(self, callback: Callable[[PipelineState], None]) -> None:
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[PipelineState], None]) -> None:
        self._subscribers.discard(callback)

    def _emit(self) -> None:
        for cb in self._subscribers:
            try:
                cb(self._state)
            except Exception:
                pass

    def request_pause(self) -> None:
        """Request pause at next stage boundary (thread-safe)."""
        self._state.pause()
        self._pause_event.clear()
        self._emit()

    def resume(self) -> None:
        """Resume from paused state."""
        self._state.resume()
        self._pause_event.set()
        self._emit()

    def retry_stage(self, stage: PipelineStage | None = None) -> bool:
        """Mark a stage for retry. Returns True if retry was queued."""
        if stage is None:
            # find first failed stage
            for s in self._state._stage_order:
                if self._state.stages.get(s) == StageStatus.FAILED:
                    stage = s
                    break
        if stage is None or stage not in self._state.stages:
            return False
        self._state.stages[stage] = StageStatus.PENDING
        self._state.current_stage = stage
        self._state.current_status = StageStatus.PENDING
        self._emit()
        return True

    async def _run_stage_async(
        self,
        stage: PipelineStage,
        stage_coro: Callable[[], Any],
    ) -> Any:
        """Run a single stage async with pause/resume checkpoint support."""
        if self._state._pause_requested:
            await self._pause_event.wait()
            if not self._state._pause_requested:
                self._state.current_stage = stage
                self._state.current_status = StageStatus.PENDING

        self._state.advance(stage, StageStatus.ACTIVE)
        self._emit()
        try:
            result = await stage_coro()
            self._state.advance(stage, StageStatus.COMPLETED)
            self._emit()
            return result
        except Exception as e:
            self._state.set_error(str(e), stage)
            self._emit()
            raise

    def _run_stage_sync(
        self,
        stage: PipelineStage,
        stage_func: Callable[[], Any],
    ) -> Any:
        self._state.advance(stage, StageStatus.ACTIVE)
        self._emit()
        try:
            result = stage_func()
            self._state.advance(stage, StageStatus.COMPLETED)
            self._emit()
            return result
        except Exception as e:
            self._state.set_error(str(e), stage)
            self._emit()
            raise

    async def run_async(self, project_path: str | Path) -> dict[str, Any]:
        """Run the full pipeline async with pause/retry/resume support.

        Pause: call state_machine.request_pause() from any thread/task.
        Resume: call state_machine.resume() to continue from current stage.
        Retry: call state_machine.retry_stage(stage) to re-run a failed stage.
        """
        self._state.reset()
        self._state.current_stage = PipelineStage.EVIDENCE
        self._pause_event.set()

        from to_vibe.config import load_config as load_vibe_config
        from to_vibe.pipeline.evidence_ledger import EvidenceLedgerScanner
        from to_vibe.pipeline.priority_report import PriorityAnalyzer
        from to_vibe.pipeline.baseline_verify import BaselineVerifier
        from to_vibe.pipeline.repair_loop import RepairLoop
        from to_vibe.learn.learn import LegacyLearnCollector

        project_path = Path(project_path)
        config = load_vibe_config(str(project_path))

        # checkpoint for resumption
        ledger = None
        report = None
        verify_result = None
        repair_result = None
        learn_result = None

        # Stage 1: Evidence
        if self._state.stages.get(PipelineStage.EVIDENCE) != StageStatus.COMPLETED:
            if self._state._checkpoint.get("ledger"):
                ledger = self._state._checkpoint["ledger"]
                self._state.advance(PipelineStage.EVIDENCE, StageStatus.COMPLETED)
                self._emit()
            else:
                ledger = await self._run_stage_async(
                    PipelineStage.EVIDENCE,
                    lambda: EvidenceLedgerScanner(project_path, config.pipeline).scan(),
                )
                self._state._checkpoint["ledger"] = ledger

        # Stage 2: Priority
        if self._state.stages.get(PipelineStage.PRIORITY) != StageStatus.COMPLETED:
            if self._state._checkpoint.get("report"):
                report = self._state._checkpoint["report"]
                self._state.advance(PipelineStage.PRIORITY, StageStatus.COMPLETED)
                self._emit()
            else:
                report = await self._run_stage_async(
                    PipelineStage.PRIORITY,
                    lambda: PriorityAnalyzer(ledger).analyze(),
                )
                self._state._checkpoint["report"] = report

        # Stage 3: Verify
        if self._state.stages.get(PipelineStage.VERIFY) != StageStatus.COMPLETED:
            if self._state._checkpoint.get("verify_result"):
                verify_result = self._state._checkpoint["verify_result"]
                self._state.advance(PipelineStage.VERIFY, StageStatus.COMPLETED)
                self._emit()
            else:
                verifier = BaselineVerifier(project_path, config.pipeline.verify)
                verify_result = await self._run_stage_async(
                    PipelineStage.VERIFY,
                    verifier.verify,
                )
                self._state._checkpoint["verify_result"] = verify_result

        # Stage 4: Repair
        if self._state.stages.get(PipelineStage.REPAIR) != StageStatus.COMPLETED:
            if self._state._checkpoint.get("repair_result"):
                repair_result = self._state._checkpoint["repair_result"]
                self._state.advance(PipelineStage.REPAIR, StageStatus.COMPLETED)
                self._emit()
            else:
                repair_loop = RepairLoop(project_path, ledger, report, config.pipeline)
                repair_result = await self._run_stage_async(
                    PipelineStage.REPAIR,
                    repair_loop.run,
                )
                self._state._checkpoint["repair_result"] = repair_result

        # Stage 5: Learn
        if self._state.stages.get(PipelineStage.LEARN) != StageStatus.COMPLETED:
            if self._state._checkpoint.get("learn_result"):
                learn_result = self._state._checkpoint["learn_result"]
                self._state.advance(PipelineStage.LEARN, StageStatus.COMPLETED)
                self._emit()
            else:
                collector = LegacyLearnCollector(project_path, config.learn)
                learn_result = await self._run_stage_async(
                    PipelineStage.LEARN,
                    collector.collect,
                )
                self._state._checkpoint["learn_result"] = learn_result

        self._state.current_stage = PipelineStage.COMPLETED
        self._state.progress = 1.0
        self._emit()

        return {
            "ledger": ledger,
            "report": report,
            "verify_result": verify_result,
            "repair_result": repair_result,
            "learn_result": learn_result,
        }

    @property
    def state(self) -> PipelineState:
        return self._state
