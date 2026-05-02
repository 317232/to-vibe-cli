"""MCP notification handler — converts PipelineEventBus events to MCP notifications."""

from __future__ import annotations

from to_vibe.pipeline.event_bus import PipelineEvent, PipelineEventBus
from to_vibe.mcp.server import get_server
from to_vibe.mcp.protocol import NotificationType, create_notification


class MCPNotificationHandler:
    """PipelineEventBus subscriber that sends events as MCP notifications."""

    def __call__(self, event: PipelineEvent) -> None:
        server = get_server()
        if not server:
            return

        notif_type_map = {
            "INFO": NotificationType.LOG,
            "WARN": NotificationType.LOG,
            "ERROR": NotificationType.ERROR,
            "DEBUG": NotificationType.LOG,
        }
        n_type = notif_type_map.get(event.level, NotificationType.LOG)

        if event.data:
            action = event.data.get("action")
            if action == "stage_start":
                n_type = NotificationType.STAGE_START
            elif action == "stage_complete":
                n_type = NotificationType.STAGE_COMPLETE
            elif action == "stage_fail":
                n_type = NotificationType.ERROR

        payload = {
            "text": event.message,
            "level": event.level,
            "stage": event.stage,
            "timestamp": event.timestamp,
            **(event.data or {}),
        }

        notification = create_notification(n_type, payload)

        try:
            server._notification_queue.put_nowait(notification)
        except Exception:
            pass


def install_mcp_notification_handler() -> None:
    """Install the MCP notification handler into the PipelineEventBus."""
    PipelineEventBus.subscribe(MCPNotificationHandler())