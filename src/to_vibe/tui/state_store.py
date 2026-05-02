"""TUI state store — central reactive state for all TUI components."""

from __future__ import annotations

from typing import Callable, Any

from to_vibe.tui.state_models import (
    EvidenceData,
    PriorityData,
    VerifyRow,
    RepairData,
    LearnData,
    LearnDetailView,
    LogEntry,
    ArtifactItem,
    SessionData,
    StageState,
)


class TUIStateStore:
    """Central state store for TUI — components subscribe to be notified on changes.

    Usage:
        store = TUIStateStore()
        store.bind_pipeline(state_machine)

        # Component subscribes
        store.subscribe("evidence", lambda data: evidence_card.update(data))
        store.subscribe("priority", lambda data: priority_card.update(data))
        store.subscribe("log", lambda entry: log_stream.append(entry))

        # Or query current state
        evidence = store.get_evidence()
    """

    def __init__(self) -> None:
        self._evidence: EvidenceData = EvidenceData()
        self._priority: PriorityData = PriorityData()
        self._verify_rows: list[VerifyRow] = []
        self._repair: RepairData = RepairData()
        self._learn: LearnData = LearnData()
        self._log_entries: list[LogEntry] = []
        self._artifacts: list[ArtifactItem] = []
        self._session: SessionData = SessionData()
        self._stage_states: list[StageState] = []

        self._current_stage: str = "idle"
        self._stages_completed: list[str] = []
        self._progress: float = 0.0
        self._error: str | None = None

        # Per-key subscriber callbacks: key -> list of callbacks
        self._subscribers: dict[str, list[Callable[[Any], None]]] = {
            "evidence": [],
            "priority": [],
            "verify": [],
            "repair": [],
            "learn": [],
            "log": [],
            "artifacts": [],
            "session": [],
            "stages": [],
            "stage": [],
            "progress": [],
            "error": [],
        }

    def subscribe(self, key: str, callback: Callable[[Any], None]) -> Callable[[], None]:
        """Subscribe to state changes for a specific key.

        Returns an unsubscribe function to call on component unmount.
        """
        if key not in self._subscribers:
            self._subscribers[key] = []
        self._subscribers[key].append(callback)

        def unsubscribe() -> None:
            try:
                self._subscribers[key].remove(callback)
            except ValueError:
                pass

        return unsubscribe

    def unsubscribe(self, key: str, callback: Callable[[Any], None]) -> None:
        try:
            self._subscribers[key].remove(callback)
        except ValueError:
            pass

    def _notify(self, key: str, data: Any) -> None:
        for cb in self._subscribers.get(key, []):
            try:
                cb(data)
            except Exception:
                pass

    def bind_pipeline(self, state_machine: Any) -> None:
        """Bind to a PipelineStateMachine and receive state updates."""
        state_machine.subscribe(self._on_pipeline_state)

    def _on_pipeline_state(self, state: Any) -> None:
        """Callback from PipelineStateMachine — update all derived state."""
        old_stage = self._current_stage
        self._current_stage = state.current_stage.value

        # Update session
        self._session.current_stage = self._current_stage
        self._session.progress = state.progress
        self._session.error = state.error_message
        self._notify("session", self._session)

        # Update stages
        self._stage_states = [
            StageState(
                stage_id=s.value,
                stage_name=s.value.capitalize(),
                status=status.value,
            )
            for s, status in state.stages.items()
        ]
        self._notify("stages", self._stage_states)

        if old_stage != self._current_stage:
            self._notify("stage", self._current_stage)

        self._stages_completed = [
            s.value for s, status in state.stages.items()
            if status.value == "completed"
        ]

        self._progress = state.progress
        self._notify("progress", self._progress)

        if state.error_message != self._error:
            self._error = state.error_message
            if self._error:
                self._notify("error", self._error)

    # ---- Data update methods (called by PipelineIntegration) ----

    def update_evidence(self, data: EvidenceData) -> None:
        self._evidence = data
        self._notify("evidence", data)

    def update_priority(self, data: PriorityData) -> None:
        self._priority = data
        self._notify("priority", data)

    def update_verify(self, rows: list[VerifyRow]) -> None:
        self._verify_rows = rows
        self._notify("verify", rows)

    def update_repair(self, data: RepairData) -> None:
        self._repair = data
        self._notify("repair", data)

    def update_learn(self, data: LearnData) -> None:
        self._learn = data
        self._notify("learn", data)

    def append_log(self, entry: LogEntry) -> None:
        self._log_entries.append(entry)
        if len(self._log_entries) > 500:
            self._log_entries = self._log_entries[-500:]
        self._notify("log", entry)

    def update_artifacts(self, items: list[ArtifactItem]) -> None:
        self._artifacts = items
        self._notify("artifacts", items)

    def update_session(self, data: SessionData) -> None:
        self._session = data
        self._notify("session", data)

    # ---- Getters ----

    def get_evidence(self) -> EvidenceData:
        return self._evidence

    def get_priority(self) -> PriorityData:
        return self._priority

    def get_verify_rows(self) -> list[VerifyRow]:
        return self._verify_rows

    def get_repair(self) -> RepairData:
        return self._repair

    def get_learn(self) -> LearnData:
        return self._learn

    def get_log_entries(self) -> list[LogEntry]:
        return self._log_entries

    def get_artifacts(self) -> list[ArtifactItem]:
        return self._artifacts

    def get_session(self) -> SessionData:
        return self._session

    def get_stage_states(self) -> list[StageState]:
        return self._stage_states

    def get_current_stage(self) -> str:
        return self._current_stage

    def get_stages_completed(self) -> list[str]:
        return self._stages_completed

    def get_progress(self) -> float:
        return self._progress

    def get_error(self) -> str | None:
        return self._error

    def clear_error(self) -> None:
        self._error = None
