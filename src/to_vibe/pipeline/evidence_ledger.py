"""Evidence Ledger module - scans project and builds fact ledger."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from to_vibe.config import PipelineConfig
from to_vibe.utils.logger import get_logger


@dataclass
class ProjectFact:
    """Single project fact with evidence."""

    category: str
    fact: str
    file_path: str
    line_number: int
    confidence: float = 1.0


@dataclass
class EvidenceLedger:
    """Evidence ledger containing all project facts."""

    project_path: str
    tech_stack: list[str] = field(default_factory=list)
    files_scanned: int = 0
    ignored_dirs: list[str] = field(default_factory=list)
    facts: list[ProjectFact] = field(default_factory=list)
    output_path: str = ""


class EvidenceLedgerScanner:
    """Scans project files to build evidence ledger."""

    def __init__(self, project_path: str | Path, config: PipelineConfig | None = None) -> None:
        self.project_path = Path(project_path)
        self.config = config or PipelineConfig()
        self.logger = get_logger()

    def scan(self) -> EvidenceLedger:
        """Scan project and build evidence ledger."""
        self.logger.info("Starting Evidence Ledger scan", stage="evidence")

        ledger = EvidenceLedger(project_path=str(self.project_path))
        ledger.ignored_dirs = self.config.exclude_patterns

        files = self._scan_files()
        ledger.files_scanned = len(files)
        ledger.tech_stack = self._detect_tech_stack(files)
        ledger.facts = self._extract_facts(files)

        output_path = self.project_path / ".to-vibe" / "evidence-ledger.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self._to_dict(ledger), f, indent=2, ensure_ascii=False)
        ledger.output_path = str(output_path)

        self.logger.info(f"Evidence Ledger complete: {len(ledger.facts)} facts", stage="evidence")
        return ledger

    def _scan_files(self) -> list[Path]:
        """Scan project files respecting exclude patterns."""
        files = []
        for path in self.project_path.rglob("*"):
            if path.is_file():
                rel_path = path.relative_to(self.project_path)
                if not any(p in rel_path.parts for p in self.config.exclude_patterns):
                    files.append(path)
        return files

    def _detect_tech_stack(self, files: list[Path]) -> list[str]:
        """Detect technology stack from scanned files."""
        stack = []
        file_names = {f.name for f in files}

        pm_map = {
            "package.json": "npm", "pyproject.toml": "python",
            "requirements.txt": "python", "Cargo.toml": "rust",
            "pom.xml": "java", "build.gradle": "java", "go.mod": "go",
        }
        for filename, pm in pm_map.items():
            if filename in file_names and pm not in stack:
                stack.append(pm)

        return stack

    def _extract_facts(self, files: list[Path]) -> list[ProjectFact]:
        """Extract facts from project files."""
        facts = []
        for f in files[:100]:
            try:
                rel_path = f.relative_to(self.project_path)
                facts.append(ProjectFact(
                    category="file",
                    fact=f"Found: {rel_path}",
                    file_path=str(rel_path),
                    line_number=1,
                    confidence=1.0,
                ))
            except OSError:
                pass
        return facts

    def _to_dict(self, ledger: EvidenceLedger) -> dict[str, Any]:
        """Convert ledger to dictionary."""
        return {
            "project_path": ledger.project_path,
            "tech_stack": ledger.tech_stack,
            "files_scanned": ledger.files_scanned,
            "ignored_dirs": ledger.ignored_dirs,
            "facts": [
                {"category": f.category, "fact": f.fact, "file_path": f.file_path,
                 "line_number": f.line_number, "confidence": f.confidence}
                for f in ledger.facts
            ],
            "output_path": ledger.output_path,
        }
