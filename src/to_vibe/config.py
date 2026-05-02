"""Configuration parsing for to-vibe."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class LLMConfig:
    """LLM provider configuration — endpoint-centric, provider is optional preset.

    Protocol-specific behavior is delegated to LLMProtocol (see llm/protocol.py).
    """

    provider: str = "anthropic"
    base_url: str = ""
    api_key: str = ""
    model: str = ""
    protocol: str = "openai-compatible"
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30
    stream: bool = True
    # Extra headers merged into every request (e.g. HTTP-Referer, X-Title for OpenRouter)
    extra_headers: dict[str, str] = field(default_factory=dict)

    def resolved_base_url(self) -> str:
        """Get the base URL, using provider preset if base_url is empty."""
        if self.base_url:
            return self.base_url.rstrip("/")
        if self.provider == "anthropic":
            return "https://api.anthropic.com/v1"
        if self.provider in ("openai", "deepseek", "openrouter", "siliconflow", "ollama", "lm-studio", "custom"):
            return ""
        return ""


@dataclass
class VerifyLayerConfig:
    """Single verification layer configuration."""

    enabled: bool = True
    max_retries: int = 3


@dataclass
class VerifyConfig:
    """Baseline verify layer configurations."""

    L1: VerifyLayerConfig = field(default_factory=lambda: VerifyLayerConfig(enabled=True, max_retries=3))
    L2: VerifyLayerConfig = field(default_factory=lambda: VerifyLayerConfig(enabled=True, max_retries=3))
    L3: VerifyLayerConfig = field(default_factory=lambda: VerifyLayerConfig(enabled=True, max_retries=3))
    L4: VerifyLayerConfig = field(default_factory=lambda: VerifyLayerConfig(enabled=True, max_retries=2))
    L5: VerifyLayerConfig = field(default_factory=lambda: VerifyLayerConfig(enabled=True, max_retries=1))


@dataclass
class PipelineConfig:
    """Pipeline execution configuration."""

    mode: str = "dry-run"
    max_iterations: int = 50
    exit_level: str = "maintainable"
    exclude_patterns: list[str] = field(
        default_factory=lambda: [
            "node_modules",
            ".git",
            "__pycache__",
            ".venv",
            "venv",
            ".to-vibe",
        ]
    )
    verify: VerifyConfig = field(default_factory=VerifyConfig)


@dataclass
class SessionConfig:
    """Session management configuration."""

    heartbeat_interval_seconds: int = 30
    ttl_seconds: int = 300
    recovery_policy: str = "auto"


@dataclass
class LearnConfig:
    """Learn module configuration."""

    trigger: str = "on_complete"
    min_confidence: float = 0.5
    max_records: int = 1000
    retention_days: int = 180


@dataclass
class UIConfig:
    """UI/TUI configuration."""

    log_levels: list[str] = field(default_factory=lambda: ["info", "error", "warning"])
    auto_scroll: bool = True
    compact_mode: bool = False


@dataclass
class ToVibeConfig:
    """Root configuration for to-vibe."""

    version: str = "2.0"
    llm: LLMConfig = field(default_factory=LLMConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    session: SessionConfig = field(default_factory=SessionConfig)
    learn: LearnConfig = field(default_factory=LearnConfig)
    ui: UIConfig = field(default_factory=UIConfig)


def _resolve_env_vars(value: Any) -> Any:
    """Resolve environment variables in string values.

    Supports ${VAR_NAME} syntax.
    """
    if isinstance(value, str):
        return os.path.expandvars(value)
    if isinstance(value, dict):
        return {k: _resolve_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_env_vars(item) for item in value]
    return value


def load_config(project_path: str | Path = ".") -> ToVibeConfig:
    """Load to-vibe configuration from project root.

    Looks for to-vibe.yaml in the project directory.
    Supports environment variable substitution in values.

    Args:
        project_path: Path to the project root (where to-vibe.yaml is located)

    Returns:
        ToVibeConfig instance with loaded configuration

    Raises:
        FileNotFoundError: If to-vibe.yaml does not exist in project path
        yaml.YAMLError: If to-vibe.yaml is malformed
    """
    config_path = Path(project_path) / "to-vibe.yaml"

    if not config_path.exists():
        # Return default configuration if no config file exists
        return ToVibeConfig()

    with open(config_path, "r", encoding="utf-8") as f:
        raw_config = yaml.safe_load(f)

    if raw_config is None:
        return ToVibeConfig()

    # Resolve environment variables
    raw_config = _resolve_env_vars(raw_config)

    # Build nested config objects
    llm_cfg = LLMConfig(**raw_config.get("llm", {}))
    pipeline_raw = raw_config.get("pipeline", {})
    verify_raw = pipeline_raw.get("verify", {})
    verify_layers = verify_raw.get("layers", {})

    verify_cfg = VerifyConfig(
        L1=VerifyLayerConfig(**verify_layers.get("L1", {})),
        L2=VerifyLayerConfig(**verify_layers.get("L2", {})),
        L3=VerifyLayerConfig(**verify_layers.get("L3", {})),
        L4=VerifyLayerConfig(**verify_layers.get("L4", {})),
        L5=VerifyLayerConfig(**verify_layers.get("L5", {})),
    )

    pipeline_cfg = PipelineConfig(
        mode=pipeline_raw.get("mode", "dry-run"),
        max_iterations=pipeline_raw.get("max_iterations", 50),
        exit_level=pipeline_raw.get("exit_level", "maintainable"),
        exclude_patterns=pipeline_raw.get("exclude_patterns", []),
        verify=verify_cfg,
    )

    session_cfg = SessionConfig(**raw_config.get("session", {}))
    learn_cfg = LearnConfig(**raw_config.get("learn", {}))
    ui_cfg = UIConfig(**raw_config.get("ui", {}))

    return ToVibeConfig(
        version=raw_config.get("version", "2.0"),
        llm=llm_cfg,
        pipeline=pipeline_cfg,
        session=session_cfg,
        learn=learn_cfg,
        ui=ui_cfg,
    )


def get_default_config() -> ToVibeConfig:
    """Get default configuration.

    Returns:
        ToVibeConfig with all default values
    """
    return ToVibeConfig()