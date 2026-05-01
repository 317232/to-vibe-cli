"""End-to-end integration tests for to-vibe pipeline."""

from __future__ import annotations

from pathlib import Path

import pytest


class TestEvidenceLedger:
    """Tests for Evidence Ledger module."""

    def test_scanner_detects_python_project(self, tmp_path: Path) -> None:
        """Test that scanner detects Python project structure."""
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        (tmp_path / "main.py").write_text("print('hello')")

        from to_vibe.pipeline.evidence_ledger import EvidenceLedgerScanner
        from to_vibe.config import PipelineConfig

        config = PipelineConfig()
        scanner = EvidenceLedgerScanner(tmp_path, config)
        ledger = scanner.scan()

        assert ledger.files_scanned >= 2
        assert "python" in ledger.tech_stack

    def test_scanner_respects_exclude_patterns(self, tmp_path: Path) -> None:
        """Test that scanner excludes specified directories."""
        (tmp_path / "main.py").write_text("print('hello')")
        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "package.json").write_text("{}")

        from to_vibe.pipeline.evidence_ledger import EvidenceLedgerScanner
        from to_vibe.config import PipelineConfig

        config = PipelineConfig(exclude_patterns=["node_modules"])
        scanner = EvidenceLedgerScanner(tmp_path, config)
        ledger = scanner.scan()

        assert all("node_modules" not in str(f) for f in ledger.facts)


class TestPriorityReport:
    """Tests for Priority Report module."""

    def test_analyzer_generates_report(self, tmp_path: Path) -> None:
        """Test that analyzer generates a priority report."""
        from to_vibe.pipeline.evidence_ledger import EvidenceLedger
        from to_vibe.pipeline.priority_report import PriorityAnalyzer

        ledger = EvidenceLedger(project_path=str(tmp_path))
        ledger.tech_stack = ["python"]
        ledger.files_scanned = 10

        analyzer = PriorityAnalyzer(ledger)
        report = analyzer.analyze()

        assert report.blockers == 0


class TestConfig:
    """Tests for configuration parsing."""

    def test_load_default_config(self) -> None:
        """Test loading default configuration."""
        from to_vibe.config import get_default_config

        config = get_default_config()
        assert config.version == "2.0"
        assert config.llm.provider == "anthropic"


class TestLLMClient:
    """Tests for LLM client."""

    def test_create_anthropic_client(self) -> None:
        """Test creating Anthropic client."""
        from to_vibe.config import LLMConfig
        from to_vibe.llm.client import create_client

        config = LLMConfig(provider="anthropic", api_key="test-key")
        client = create_client(config)
        assert client.config.provider == "anthropic"

    def test_create_openai_client(self) -> None:
        """Test creating OpenAI client."""
        from to_vibe.config import LLMConfig
        from to_vibe.llm.client import create_client

        config = LLMConfig(provider="openai", api_key="test-key")
        client = create_client(config)
        assert client.config.provider == "openai"


class TestLogger:
    """Tests for logger."""

    def test_log_entry_creation(self) -> None:
        """Test creating log entries."""
        from to_vibe.utils.logger import LogEntry, LogLevel

        entry = LogEntry(
            timestamp="2024-01-01T00:00:00",
            level=LogLevel.INFO,
            text="Test message",
        )

        assert entry.text == "Test message"
        assert entry.level == LogLevel.INFO

    def test_log_entry_json_serialization(self) -> None:
        """Test log entry JSON serialization."""
        from to_vibe.utils.logger import LogEntry, LogLevel

        entry = LogEntry(
            timestamp="2024-01-01T00:00:00",
            level=LogLevel.ERROR,
            text="Error occurred",
        )

        json_str = entry.to_json()
        assert "error" in json_str
        assert "Error occurred" in json_str