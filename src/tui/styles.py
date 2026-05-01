"""Style constants and theme for to-vibe TUI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Colors:
    """Color palette for to-vibe TUI."""

    # Base colors
    SURFACE = "#1e1e2e"
    SURFACE_LIGHT = "#2a2a3e"
    TEXT = "#cdd6f4"
    TEXT_MUTED = "#6c7086"

    # Stage colors
    STAGE_EVIDENCE = "#a6e3a1"  # green
    STAGE_PRIORITY = "#f9e2af"  # yellow
    STAGE_VERIFY = "#f38ba8"  # red
    STAGE_REPAIR = "#89b4fa"  # blue
    STAGE_LEARN = "#cba6f7"  # purple

    # Status colors
    STATUS_PASS = "#a6e3a1"
    STATUS_FAIL = "#f38ba8"
    STATUS_SKIP = "#6c7086"
    STATUS_ACTIVE = "#f9e2af"

    # Priority colors
    PRIORITY_BLOCKER = "#f38ba8"
    PRIORITY_HIGH = "#fab387"
    PRIORITY_MEDIUM = "#f9e2af"
    PRIORITY_LOW = "#89b4fa"


# Border styles
BORDER_STYLES = {
    "evidence": "solid",
    "priority": "solid",
    "verify": "solid",
    "learn": "dashed",
}


def get_stage_color(stage: str) -> str:
    """Get color for a pipeline stage.

    Args:
        stage: Stage name

    Returns:
        Hex color string
    """
    colors = {
        "evidence": Colors.STAGE_EVIDENCE,
        "priority": Colors.STAGE_PRIORITY,
        "verify": Colors.STAGE_VERIFY,
        "repair": Colors.STAGE_REPAIR,
        "learn": Colors.STAGE_LEARN,
    }
    return colors.get(stage.lower(), Colors.TEXT_MUTED)


def get_priority_color(priority: str) -> str:
    """Get color for a priority level.

    Args:
        priority: Priority name (blocker, high, medium, low)

    Returns:
        Hex color string
    """
    colors = {
        "blocker": Colors.PRIORITY_BLOCKER,
        "high": Colors.PRIORITY_HIGH,
        "medium": Colors.PRIORITY_MEDIUM,
        "low": Colors.PRIORITY_LOW,
    }
    return colors.get(priority.lower(), Colors.TEXT_MUTED)
