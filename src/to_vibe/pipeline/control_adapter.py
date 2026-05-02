"""PipelineControlPort implementation via PipelineStateMachine."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from to_vibe.pipeline.control import ControlResult, PipelineControlPort, RetryTarget, SkipPolicy
from to_vibe.pipeline.state_machine import PipelineStateMachine, PipelineStage, StageStatus


@dataclass
class StateMachineControlAdapter(PipelineControlPort):
    """PipelineControlPort backed by PipelineStateMachine."""

    project_path: Path
    _sm: PipelineStateMachine | None = field(default=None, init=False)
    _skip_policy: SkipPolicy = field(default_factory=SkipPolicy, init=False)

    def _sm_getter(self) -> PipelineStateMachine:
        if self._sm is None:
            self._sm = PipelineStateMachine()
        return self._sm

    async def run(self, project_path: str | Path, mode: str = "dry-run") -> ControlResult:
        sm = self._sm_getter()
        try:
            await sm.run_async(project_path)
            return ControlResult(
                status="completed",
                message=f"Pipeline completed (mode={mode})",
                data={
                    "stages": [s.value for s in sm.state.stages],
                    "progress": sm.state.progress,
                    "current_stage": sm.state.current_stage.value,
                },
            )
        except Exception as e:
            return ControlResult(
                status="failed",
                message="Pipeline run failed",
                error=str(e),
                data={"current_stage": sm.state.current_stage.value},
            )

    async def pause(self) -> ControlResult:
        self._sm_getter().request_pause()
        sm = self._sm_getter()
        return ControlResult(
            status="paused",
            message=f"Paused at {sm.state.current_stage.value}",
            data={
                "current_stage": sm.state.current_stage.value,
                "progress": sm.state.progress,
            },
        )

    async def resume(self) -> ControlResult:
        sm = self._sm_getter()
        sm.resume()
        return ControlResult(
            status="resumed",
            message=f"Resumed from {sm.state.current_stage.value}",
            data={
                "current_stage": sm.state.current_stage.value,
                "progress": sm.state.progress,
            },
        )

    async def retry(self, target: RetryTarget | None = None) -> ControlResult:
        target = target or RetryTarget(kind="last_failed")
        sm = self._sm_getter()

        stage_to_retry: PipelineStage | None = None
        if target.kind == "stage" and target.stage_name:
            stage_to_retry = PipelineStage(target.stage_name)
        elif target.kind == "last_failed":
            for stage, status in sm.state.stages.items():
                if status == StageStatus.FAILED:
                    stage_to_retry = stage
                    break
        elif target.kind == "issue" and target.issue_id:
            for stage, status in sm.state.stages.items():
                if status == StageStatus.FAILED:
                    stage_to_retry = stage
                    break

        if stage_to_retry is None:
            return ControlResult(status="failed", message="No failed stage found to retry")

        success = sm.retry_stage(stage_to_retry)
        if not success:
            return ControlResult(status="failed", message=f"Could not retry {stage_to_retry.value}")

        return ControlResult(
            status="retrying",
            message=f"Retry queued for {stage_to_retry.value}",
            data={
                "retried_stage": stage_to_retry.value,
                "progress": sm.state.progress,
            },
        )

    async def skip(self, stage: str | None = None, reason: str | None = None) -> ControlResult:
        sm = self._sm_getter()
        stage_name = stage or sm.state.current_stage.value

        allowed, error = self._skip_policy.can_skip(stage_name, reason)
        if not allowed:
            return ControlResult(status="failed", message=error or f"Cannot skip {stage_name}")

        target_stage = PipelineStage(stage_name) if stage else sm.state.current_stage
        if target_stage in sm.state.stages:
            sm.state.stages[target_stage] = StageStatus.SKIPPED

        return ControlResult(
            status="skipped",
            message=f"Skipped {stage_name}",
            data={
                "skipped_stage": stage_name,
                "progress": sm.state.progress,
            },
        )

    async def learn(self, project_path: str | Path) -> ControlResult:
        from to_vibe.config import load_config
        from to_vibe.learn.learn import LegacyLearnCollector

        config = load_config(str(project_path))
        collector = LegacyLearnCollector(project_path, config.learn)
        result = collector.collect()

        return ControlResult(
            status="completed",
            message="Learn collection completed",
            data={
                "candidates_found": result.get("candidates_found", 0),
                "candidates_filtered": result.get("candidates_filtered", 0),
                "pending_review": result.get("pending_review", 0),
                "output_path": result.get("output_path", ""),
            },
        )

    def snapshot(self) -> ControlResult:
        sm = self._sm_getter()
        return ControlResult(
            status="snapshot",
            data={
                "current_stage": sm.state.current_stage.value,
                "current_status": sm.state.current_status.value,
                "stages": {s.value: st.value for s, st in sm.state.stages.items()},
                "progress": sm.state.progress,
                "error_message": sm.state.error_message,
            },
        )
