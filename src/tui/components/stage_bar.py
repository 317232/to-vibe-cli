"""StageBar component showing 5-stage pipeline progress."""

from __future__ import annotations

from textual.widgets import Static

from to_vibe.mcp.protocol import Stage
from to_vibe.tui.styles import get_stage_color


class StageStatus:
    """Stage status enumeration."""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StageBar(Static):
    """5-stage chevron bar showing pipeline progress.

    Stages: Evidence → Priority → Verify → Repair → Learn
    """

    STAGES = [
        ("evidence", "Evidence"),
        ("priority", "Priority"),
        ("verify", "Verify"),
        ("repair", "Repair"),
        ("learn", "Learn"),
    ]

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._stage_statuses: dict[str, str] = {
            stage_id: StageStatus.PENDING for stage_id, _ in self.STAGES
        }
        self._active_index = 0

    def set_stage_status(self, stage: str, status: str) -> None:
        """Set the status of a stage."""
        self._stage_statuses[stage] = status
        self._update_display()

    def set_active(self, stage: str) -> None:
        """Set the active stage."""
        self._active_index = next(
            (i for i, (sid, _) in enumerate(self.STAGES) if sid == stage), 0
        )
        for sid, _ in self.STAGES:
            if sid == stage:
                self._stage_statuses[sid] = StageStatus.ACTIVE
            elif self._stage_statuses[sid] == StageStatus.ACTIVE:
                self._stage_statuses[sid] = StageStatus.COMPLETED
        self._update_display()

    def _get_chevron(self, stage_id: str, label: str) -> str:
        """Get chevron representation for a stage."""
        status = self._stage_statuses.get(stage_id, StageStatus.PENDING)
        color = get_stage_color(stage_id)
        icons = {
            StageStatus.PENDING: "○",
            StageStatus.ACTIVE: "▶",
            StageStatus.COMPLETED: "✓",
            StageStatus.FAILED: "✗",
            StageStatus.SKIPPED: "⊘",
        }
        icon = icons.get(status, "○")
        return f"[{color}]{icon} {label}[/{color}]"

    def _update_display(self) -> None:
        """Update the displayed chevron bar."""
        chevrons = [self._get_chevron(sid, label) for sid, label in self.STAGES]
        separator = " → "
        self.update(separator.join(chevrons))

    def on_mount(self) -> None:
        """Handle mount event."""
        self._update_display()
