"""EvidenceCard component showing Evidence Ledger summary."""

from __future__ import annotations

from textual.widgets import Static
from to_vibe.tui.styles import Colors
from to_vibe.tui.state_store import EvidenceData, TUIStateStore


class EvidenceCard(Static):
    """Evidence card showing detected tech stack and scan results."""

    def __init__(self, store: TUIStateStore, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._store = store
        self._unsubscribe: callable | None = None
        self._data: EvidenceData | None = None

    def on_mount(self) -> None:
        self._unsubscribe = self._store.subscribe("evidence", self._on_evidence)
        self.set_data(self._store.get_evidence())

    def on_unmount(self) -> None:
        if self._unsubscribe:
            self._unsubscribe()

    def _on_evidence(self, data: EvidenceData) -> None:
        self.app.call_from_thread(self.set_data, data)

    def set_data(self, data: EvidenceData) -> None:
        self._data = data
        self._update_display()

    def _update_display(self) -> None:
        if not self._data:
            self.update("[Evidence Ledger]\nNo data")
            return

        stack_str = ", ".join(self._data.tech_stack) if self._data.tech_stack else "—"
        ignored_str = ", ".join(self._data.ignored_dirs) if self._data.ignored_dirs else "—"

        lines = [
            f"[b]◆ Evidence Ledger[/b] [{Colors.STAGE_EVIDENCE}]",
            "",
            f"Tech stack      : {stack_str}",
            f"Files scanned   : {self._data.files_scanned}",
            f"Ignored         : {ignored_str}",
            f"Output          : {self._data.output_path}",
        ]
        self.update("\n".join(lines))
