"""Style constants and theme for to-vibe TUI."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Colors:
    """Color palette for to-vibe TUI."""

    # Base colors — dark theme per TUI_DESIGN.md
    SURFACE = "#0b1015"
    SURFACE_LIGHT = "#161b22"
    TEXT = "#cdd6f4"
    TEXT_MUTED = "#6c7086"

    # Stage colors
    STAGE_EVIDENCE = "#238636"   # green per design spec
    STAGE_PRIORITY = "#d29922"   # yellow per design spec
    STAGE_VERIFY = "#da3633"     # red per design spec
    STAGE_REPAIR = "#1f6feb"     # blue per design spec
    STAGE_LEARN = "#a371f7"      # purple per design spec

    # Status colors
    STATUS_PASS = "#238636"
    STATUS_FAIL = "#da3633"
    STATUS_SKIP = "#d29922"
    STATUS_ACTIVE = "#1f6feb"

    # Priority colors
    PRIORITY_BLOCKER = "#da3633"
    PRIORITY_HIGH = "#d29922"
    PRIORITY_MEDIUM = "#d29922"
    PRIORITY_LOW = "#1f6feb"

    # Log level colors
    LOG_INFO = "#238636"
    LOG_WARN = "#d29922"
    LOG_ERROR = "#da3633"


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
