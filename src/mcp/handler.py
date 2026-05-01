"""MCP command handlers for to-vibe."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from to_vibe.utils.logger import get_logger


class MCPHandler:
    """Handler for MCP invoke commands."""

    def __init__(self, project_path: str | Path) -> None:
        self.project_path = Path(project_path)
        self.logger = get_logger()

    async def handle_run(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle to-vibe.run command.

        Args:
            params: Command parameters (project_path, mode)

        Returns:
            Command result
        """
        project_path = params.get("project_path", str(self.project_path))
        mode = params.get("mode", "dry-run")

        self.logger.info(f"to-vibe.run: {project_path} (mode={mode})")
        return {"status": "started", "project_path": project_path, "mode": mode}

    async def handle_pause(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle to-vibe.pause command.

        Args:
            params: Command parameters

        Returns:
            Command result
        """
        self.logger.info("to-vibe.pause")
        return {"status": "paused"}

    async def handle_retry(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle to-vibe.retry command.

        Args:
            params: Command parameters

        Returns:
            Command result
        """
        self.logger.info("to-vibe.retry")
        return {"status": "retrying"}

    async def handle_skip(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle to-vibe.skip command.

        Args:
            params: Command parameters

        Returns:
            Command result
        """
        self.logger.info("to-vibe.skip")
        return {"status": "skipped"}

    async def handle_learn(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle to-vibe.learn command.

        Args:
            params: Command parameters

        Returns:
            Command result
        """
        self.logger.info("to-vibe.learn")
        return {"status": "learning"}
