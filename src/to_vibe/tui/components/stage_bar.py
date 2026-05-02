"""StageBar component showing 5-stage pipeline progress."""

from __future__ import annotations

from textual.widgets import Static
from to_vibe.tui.styles import get_stage_color
from to_vibe.tui.state_store import TUIStateStore


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

    def __init__(self, store: TUIStateStore, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._store = store
        self._unsubscribe: callable | None = None
        self._stage_statuses: dict[str, str] = {
            stage_id: "pending" for stage_id, _ in self.STAGES
        }

    def on_mount(self) -> None:
        self._unsubscribe = self._store.subscribe("stages", self._on_stages)
        self._update_display()

    def on_unmount(self) -> None:
        if self._unsubscribe:
            self._unsubscribe()

    def _on_stages(self, stages) -> None:
        self.app.call_from_thread(self._apply_stages, stages)

    def _apply_stages(self, stages) -> None:
        stage_map = {s.stage_id: s.status for s in stages}
        for sid, _ in self.STAGES:
            self._stage_statuses[sid] = stage_map.get(sid, "pending")
        self._update_display()

    def set_stage_status(self, stage: str, status: str) -> None:
        self._stage_statuses[stage] = status
        self._update_display()

    def set_active(self, stage: str) -> None:
        for sid, _ in self.STAGES:
            if sid == stage:
                self._stage_statuses[sid] = "active"
            elif self._stage_statuses[sid] == "active":
                self._stage_statuses[sid] = "completed"
        self._update_display()

    def _get_chevron(self, stage_id: str, label: str) -> str:
        status = self._stage_statuses.get(stage_id, "pending")
        color = get_stage_color(stage_id)
        icons = {
            "pending": "[#6c7086]◌[/]",
            "active": "[#1f6feb]▶[/]",
            "completed": "[#238636]✔[/]",
            "failed": "[#da3633]✗[/]",
            "skipped": "[#d29922]⊘[/]",
        }
        icon = icons.get(status, "[#6c7086]◌[/]")
        return f"[{color}]{icon} {label}[/{color}]"

    def _update_display(self) -> None:
        chevrons = [self._get_chevron(sid, label) for sid, label in self.STAGES]
        separator = " → "
        self.update(separator.join(chevrons))
