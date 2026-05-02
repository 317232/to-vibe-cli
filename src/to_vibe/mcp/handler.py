"""MCP command handlers for to-vibe.

Each handler is a thin protocol adapter — it translate MCP params
into PipelineControlPort calls and translates the result into an MCP response dict.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from to_vibe.pipeline.control import PipelineControlPort, RetryTarget
from to_vibe.utils.logger import get_logger


# Lazy-loaded to avoid pulling in the heavy pipeline stack at import time
_control_port: PipelineControlPort | None = None


def _get_port(project_path: str | Path) -> PipelineControlPort:
    """Create or return the global control port."""
    global _control_port
    if _control_port is None:
        from to_vibe.pipeline.control_adapter import StateMachineControlAdapter
        _control_port = StateMachineControlAdapter(Path(project_path))
    return _control_port


class MCPHandler:
    """Handler for MCP invoke commands — thin adapter only."""

    def __init__(self, project_path: str | Path) -> None:
        self.project_path = Path(project_path)
        self.logger = get_logger()

    async def handle_run(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle to-vibe.run command."""
        project_path = params.get("project_path", str(self.project_path))
        mode = params.get("mode", "dry-run")

        self.logger.info(f"to-vibe.run: {project_path} (mode={mode})")
        port = _get_port(project_path)

        result = await port.run(project_path, mode=mode)
        return {
            "status": result.status,
            "message": result.message,
            "error": result.error,
            "project_path": project_path,
            "mode": mode,
            "data": result.data,
        }

    async def handle_pause(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle to-vibe.pause command."""
        self.logger.info("to-vibe.pause")
        port = _get_port(self.project_path)

        result = await port.pause()
        return {
            "status": result.status,
            "message": result.message,
            "error": result.error,
            "data": result.data,
        }

    async def handle_retry(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle to-vibe.retry command."""
        self.logger.info("to-vibe.retry")
        port = _get_port(self.project_path)

        # Build RetryTarget from params
        target = None
        if params.get("stage_name"):
            target = RetryTarget(kind="stage", stage_name=params["stage_name"])
        elif params.get("issue_id"):
            target = RetryTarget(kind="issue", issue_id=params["issue_id"])

        result = await port.retry(target=target)
        return {
            "status": result.status,
            "message": result.message,
            "error": result.error,
            "data": result.data,
        }

    async def handle_skip(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle to-vibe.skip command."""
        self.logger.info("to-vibe.skip")
        port = _get_port(self.project_path)

        stage = params.get("stage")
        reason = params.get("reason")

        result = await port.skip(stage=stage, reason=reason)
        return {
            "status": result.status,
            "message": result.message,
            "error": result.error,
            "data": result.data,
        }

    async def handle_learn(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle to-vibe.learn command."""
        project_path = params.get("project_path", str(self.project_path))
        self.logger.info(f"to-vibe.learn: {project_path}")
        port = _get_port(project_path)

        result = await port.learn(project_path)
        return {
            "status": result.status,
            "message": result.message,
            "error": result.error,
            "data": result.data,
        }
