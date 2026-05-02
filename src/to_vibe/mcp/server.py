"""MCP server implementation for to-vibe."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from to_vibe.utils.logger import get_logger


class MCPServer:
    """MCP server for bidirectional communication with Claude Code."""

    def __init__(self, project_path: str | Path) -> None:
        self.project_path = Path(project_path)
        self.logger = get_logger()
        self._handlers: dict[str, callable] = {}
        self._notification_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._running = False

    def register_handler(self, method: str, handler: callable) -> None:
        """Register a handler for an invoke method.

        Args:
            method: Method name (e.g., "to-vibe.run")
            handler: Async function to handle the method
        """
        self._handlers[method] = handler

    async def send_notification(self, notification: dict[str, Any]) -> None:
        """Send a notification to the MCP client.

        Args:
            notification: Notification payload with type field
        """
        notification["id"] = notification.get("id", "")
        notification["timestamp"] = notification.get("timestamp", "")

        await self._notification_queue.put(notification)
        self.logger.debug(f"MCP notification sent: {notification.get('type')}")

    async def handle_invoke(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        """Handle an invoke request from the MCP client.

        Args:
            method: Method name
            params: Method parameters

        Returns:
            Response payload
        """
        if method not in self._handlers:
            return {"error": {"code": -32601, "message": f"Method not found: {method}"}}

        try:
            result = await self._handlers[method](params)
            return {"result": result}
        except Exception as e:
            self.logger.error(f"MCP invoke error: {e}")
            return {"error": {"code": -32603, "message": str(e)}}

    async def start(self) -> None:
        """Start the MCP server."""
        self._running = True
        self.logger.info("MCP server started")

    async def stop(self) -> None:
        """Stop the MCP server."""
        self._running = False
        self.logger.info("MCP server stopped")

    async def run_stdin_loop(self) -> None:
        """Run the stdin/stdout communication loop.

        This reads JSON-RPC messages from stdin and writes responses to stdout.
        """
        import sys

        loop = asyncio.get_event_loop()

        while self._running:
            try:
                line = await loop.run_in_executor(None, sys.stdin.readline)
                if not line:
                    break

                message = json.loads(line.strip())
                method = message.get("method", "")
                msg_id = message.get("id")
                params = message.get("params", {})

                # Handle invoke requests
                if message.get("type") == "invoke":
                    response = await self.handle_invoke(method, params)
                    response["id"] = msg_id
                    print(json.dumps(response), flush=True)

                # Handle notification (no response expected)
                elif message.get("type") == "notification":
                    await self.send_notification(params)

            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON received: {e}")
            except Exception as e:
                self.logger.error(f"MCP server error: {e}")


# Global server instance
_server: MCPServer | None = None


def get_server() -> MCPServer | None:
    """Get the global MCP server instance."""
    return _server


def init_server(project_path: str | Path) -> MCPServer:
    """Initialize the global MCP server.

    Args:
        project_path: Path to the project

    Returns:
        Initialized MCPServer instance
    """
    global _server
    _server = MCPServer(project_path)
    return _server