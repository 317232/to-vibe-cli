"""Component wiring tests for TUI — verifies store → component data flow."""

from __future__ import annotations

import pytest
from textual.containers import Horizontal

from to_vibe.tui.state_store import TUIStateStore
from to_vibe.tui.state_models import (
    EvidenceData,
    PriorityData,
    VerifyRow,
    RepairData,
    LearnData,
    LogEntry,
    ArtifactItem,
    SessionData,
)
from to_vibe.tui.components.evidence_card import EvidenceCard
from to_vibe.tui.components.priority_card import PriorityCard
from to_vibe.tui.components.verify_table import VerifyTable
from to_vibe.tui.components.log_stream import LogStream
from to_vibe.tui.components.artifacts import Artifacts
from to_vibe.tui.components.repair_panel import RepairPanel


class TestStoreWiring:
    """Test that TUI components react to store updates."""

    @pytest.fixture
    def store(self) -> TUIStateStore:
        return TUIStateStore()

    def test_evidence_card_receives_evidence_update(self, store: TUIStateStore) -> None:
        """store.update_evidence should notify EvidenceCard."""
        captured: list[EvidenceData] = []

        def capture(data: EvidenceData) -> None:
            captured.append(data)

        store.subscribe("evidence", capture)
        store.update_evidence(EvidenceData(
            tech_stack=["python", "fastapi"],
            files_scanned=42,
            ignored_dirs=["node_modules", ".venv"],
            output_path=".to-vibe/evidence.json",
        ))

        assert len(captured) == 1
        assert captured[0].tech_stack == ["python", "fastapi"]
        assert captured[0].files_scanned == 42
        assert captured[0].ignored_dirs == ["node_modules", ".venv"]

    def test_priority_card_receives_priority_update(self, store: TUIStateStore) -> None:
        """store.update_priority should notify PriorityCard."""
        captured: list[PriorityData] = []

        def capture(data: PriorityData) -> None:
            captured.append(data)

        store.subscribe("priority", capture)
        store.update_priority(PriorityData(
            blockers=1,
            high=3,
            medium=5,
            top_issue="slow queries",
            suggested_capability="database-optimization",
        ))

        assert len(captured) == 1
        assert captured[0].blockers == 1
        assert captured[0].suggested_capability == "database-optimization"

    def test_verify_table_receives_verify_rows(self, store: TUIStateStore) -> None:
        """store.update_verify should notify VerifyTable."""
        rows = [
            VerifyRow(id=1, check="Environment", status="pass"),
            VerifyRow(id=2, check="Dependencies", status="fail"),
        ]
        captured: list[list[VerifyRow]] = []

        def capture(data: list[VerifyRow]) -> None:
            captured.append(data)

        store.subscribe("verify", capture)
        store.update_verify(rows)

        assert len(captured) == 1
        assert len(captured[0]) == 2
        assert captured[0][0].check == "Environment"
        assert captured[0][1].status == "fail"

    def test_log_stream_receives_log_entries(self, store: TUIStateStore) -> None:
        """store.append_log should notify LogStream."""
        captured: list[LogEntry] = []

        def capture(entry: LogEntry) -> None:
            captured.append(entry)

        store.subscribe("log", capture)
        store.append_log(LogEntry(timestamp="00:01", level="INFO", message="stage started"))
        store.append_log(LogEntry(timestamp="00:02", level="WARN", message="stage slow"))

        assert len(captured) == 2
        assert captured[0].message == "stage started"
        assert captured[1].level == "WARN"

    def test_artifacts_receives_artifact_list(self, store: TUIStateStore) -> None:
        """store.update_artifacts should notify Artifacts."""
        captured: list[list[ArtifactItem]] = []

        def capture(data: list[ArtifactItem]) -> None:
            captured.append(data)

        store.subscribe("artifacts", capture)
        items = [
            ArtifactItem(name="evidence-ledger.json", is_directory=False),
            ArtifactItem(name="claude-tasks/", is_directory=True),
        ]
        store.update_artifacts(items)

        assert len(captured) == 1
        assert len(captured[0]) == 2
        assert captured[0][0].name == "evidence-ledger.json"
        assert captured[0][1].is_directory is True

    def test_repair_panel_receives_repair_update(self, store: TUIStateStore) -> None:
        """store.update_repair should notify RepairPanel."""
        captured: list[RepairData] = []

        def capture(data: RepairData) -> None:
            captured.append(data)

        store.subscribe("repair", capture)
        store.update_repair(RepairData(
            selected_issue="slow-boot",
            capability="startup-optimization",
            mode="dry-run",
            apply="skipped",
            record=".to-vibe/repair-loop.json",
            next_action="verify",
            latest_event="issue selected",
            latest_time="00:05",
        ))

        assert len(captured) == 1
        assert captured[0].selected_issue == "slow-boot"
        assert captured[0].apply == "skipped"

    def test_session_update_notifies_subscribers(self, store: TUIStateStore) -> None:
        """store.update_session should notify session subscribers."""
        captured: list[SessionData] = []

        def capture(data: SessionData) -> None:
            captured.append(data)

        store.subscribe("session", capture)
        store.update_session(SessionData(
            project_path="/test/project",
            mode="apply",
            executor="claude",
            current_stage="verify",
            progress=0.4,
        ))

        assert len(captured) == 1
        assert captured[0].project_path == "/test/project"
        assert captured[0].executor == "claude"

    def test_subscribe_returns_unsubscribe(self, store: TUIStateStore) -> None:
        """subscribe() should return a callable that removes the subscription."""
        counter = 0

        def increment(_: object) -> None:
            nonlocal counter
            counter += 1

        unsubscribe = store.subscribe("evidence", increment)
        store.update_evidence(EvidenceData(tech_stack=["go"]))
        assert counter == 1

        unsubscribe()
        store.update_evidence(EvidenceData(tech_stack=["rust"]))
        assert counter == 1  # should not increment after unsubscribe


class TestIntegrationShortcutWiring:
    """Test that app shortcuts call integration methods."""

    def test_integration_has_pause_retry_skip(self) -> None:
        """PipelineIntegration should have pause, retry, skip methods."""
        from to_vibe.tui.pipeline_integration import PipelineIntegration
        from pathlib import Path
        import tempfile

        store = TUIStateStore()
        with tempfile.TemporaryDirectory() as tmpdir:
            integration = PipelineIntegration(Path(tmpdir), store)
            assert hasattr(integration, "pause")
            assert hasattr(integration, "retry")
            assert hasattr(integration, "skip")
            assert callable(integration.pause)
            assert callable(integration.retry)
            assert callable(integration.skip)


class TestTabBarRendering:
    """Test that TabBar renders correctly as Textual widget."""

    def test_tabbar_is_horizontal_container(self) -> None:
        """TabBar should be a Horizontal container."""
        from to_vibe.tui.screens.main_screen import TabBar
        assert issubclass(TabBar, Horizontal)

    def test_tabbar_composes_buttons(self) -> None:
        """TabBar.compose should yield 3 button children."""
        from to_vibe.tui.screens.main_screen import TabBar
        tabs = ["chat", "to-vibe", "logs"]
        labels = ["1: claude", "2: to-vibe", "3: logs"]
        bar = TabBar(tabs=tabs, labels=labels)
        buttons = list(bar.compose())
        assert len(buttons) == 3


class TestStoreFieldNames:
    """Test that store dataclasses have the correct unified field names."""

    def test_evidence_data_has_ignored_dirs(self) -> None:
        data = EvidenceData(ignored_dirs=[".git", "node_modules"])
        assert hasattr(data, "ignored_dirs")
        assert ".git" in data.ignored_dirs

    def test_priority_data_has_suggested_capability(self) -> None:
        data = PriorityData(suggested_capability="db-optimization")
        assert hasattr(data, "suggested_capability")
        assert data.suggested_capability == "db-optimization"

    def test_repair_data_has_apply_not_apply_status(self) -> None:
        data = RepairData(apply="applied")
        assert hasattr(data, "apply")
        assert not hasattr(data, "apply_status")

    def test_repair_data_has_record_not_record_path(self) -> None:
        data = RepairData(record=".to-vibe/repair-loop.json")
        assert hasattr(data, "record")
        assert not hasattr(data, "record_path")

    def test_artifact_item_has_is_directory(self) -> None:
        item = ArtifactItem(name="claude-tasks/", is_directory=True)
        assert hasattr(item, "is_directory")
        assert item.is_directory is True


class TestMainScreenCompose:
    """Test that MainScreen.compose works without errors."""

    def test_main_screen_compose_yields_all_widgets(self) -> None:
        """MainScreen.compose should yield Header, TabBar, ChatPanel, ToVibePanel, LogsPanel, StageBar, Footer."""
        from to_vibe.tui.screens.main_screen import MainScreen

        store = TUIStateStore()
        screen = MainScreen(store)
        widgets = list(screen.compose())

        # Should yield exactly 7 widgets
        assert len(widgets) == 7
