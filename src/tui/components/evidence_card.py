"""EvidenceCard component showing Evidence Ledger summary."""

from __future__ import annotations

from dataclasses import dataclass
from textual.widgets import Static
from to_vibe.tui.styles import Colors


@dataclass
class EvidenceData:
    """Evidence Ledger data."""

    stack: str = ""
    files_scanned: int = 0
    ignored_dirs: list[str] = None
    output_path: str = ""
    facts: list[dict] = None

    def __post_init__(self):
        if self.ignored_dirs is None:
            self.ignored_dirs = []
        if self.facts is None:
            self.facts = []


class EvidenceCard(Static):
    """Evidence card showing detected tech stack and scan results."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self._data: EvidenceData | None = None

    def set_data(self, data: EvidenceData) -> None:
        """Set evidence data."""
        self._data = data
        self._update_display()

    def _update_display(self) -> None:
        if not self._data:
            self.update("[Evidence Ledger]\nNo data")
            return

        lines = [
            f"[b]Evidence Ledger[/b] [{Colors.STAGE_EVIDENCE}]",
            f"",
            f"[b]Stack:[/b] {self._data.stack}",
            f"[b]Files scanned:[/b] {self._data.files_scanned}",
            f"[b]Ignored:[/b] {', '.join(self._data.ignored_dirs)}",
            f"[b]Output:[/b] {self._data.output_path}",
        ]
        self.update("\n".join(lines))

    def on_mount(self) -> None:
        self._update_display()
