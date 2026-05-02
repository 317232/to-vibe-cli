"""Baseline Verify module - 5-layer verification (L1-L5)."""

from __future__ import annotations

import asyncio
import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from to_vibe.config import VerifyConfig, VerifyLayerConfig
from to_vibe.utils.logger import get_logger


@dataclass
class VerifyLayerResult:
    """Result of a single verification layer."""

    layer_id: str
    check: str
    status: str
    command: str
    output: str = ""
    retries: int = 0


@dataclass
class BaselineVerifyResult:
    """Result of all verification layers."""

    project_path: str
    layer_results: list[VerifyLayerResult] = field(default_factory=list)
    output_path: str = ""


class BaselineVerifier:
    """Runs 5-layer baseline verification."""

    def __init__(self, project_path: str | Path, config: VerifyConfig | None = None) -> None:
        self.project_path = Path(project_path)
        self.config = config or VerifyConfig()
        self.logger = get_logger()

    async def verify(self) -> BaselineVerifyResult:
        """Run all verification layers."""
        self.logger.info("Starting Baseline Verify", stage="verify")
        result = BaselineVerifyResult(project_path=str(self.project_path))

        layer_defs = [
            ("L1", "Environment", self._check_environment),
            ("L2", "Dependencies", self._check_dependencies),
            ("L3", "Build", self._check_build),
            ("L4", "Start", self._check_start),
            ("L5", "Smoke Test", self._check_smoke),
        ]

        prev_failed = False
        for layer_id, check_name, check_fn in layer_defs:
            layer_cfg = getattr(self.config, layer_id)
            if not layer_cfg.enabled:
                result.layer_results.append(VerifyLayerResult(
                    layer_id=layer_id, check=check_name, status="skip", command="disabled"))
                continue
            if prev_failed and layer_id in ("L4", "L5"):
                result.layer_results.append(VerifyLayerResult(
                    layer_id=layer_id, check=check_name, status="skip", command="blocked"))
                continue

            layer_result = await self._run_layer(layer_id, check_name, check_fn, layer_cfg)
            result.layer_results.append(layer_result)
            if layer_result.status == "fail":
                prev_failed = True

        output_path = self.project_path / ".to-vibe" / "baseline-verify.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self._to_dict(result), f, indent=2, ensure_ascii=False)
        result.output_path = str(output_path)

        self.logger.info("Baseline Verify complete", stage="verify")
        return result

    async def _run_layer(self, layer_id: str, check: str, check_fn: Any, cfg: VerifyLayerConfig) -> VerifyLayerResult:
        """Run a single layer with retries."""
        for attempt in range(cfg.max_retries):
            try:
                status, output, cmd = await check_fn()
                if status == "pass":
                    return VerifyLayerResult(layer_id=layer_id, check=check, status=status, command=cmd, retries=attempt)
            except Exception as e:
                if attempt == cfg.max_retries - 1:
                    return VerifyLayerResult(layer_id=layer_id, check=check, status="fail", command=cmd or "", output=str(e), retries=attempt + 1)
        return VerifyLayerResult(layer_id=layer_id, check=check, status="fail", command="", retries=cfg.max_retries)

    async def _check_environment(self) -> tuple[str, str, str]:
        cmd = "python3 --version"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return ("pass", result.stdout.strip(), cmd)
        except Exception:
            pass
        return ("fail", "Environment check failed", cmd)

    async def _check_dependencies(self) -> tuple[str, str, str]:
        return ("skip", "Dependencies check skipped", "N/A")

    async def _check_build(self) -> tuple[str, str, str]:
        return ("skip", "Build check skipped", "N/A")

    async def _check_start(self) -> tuple[str, str, str]:
        return ("skip", "Start check skipped", "N/A")

    async def _check_smoke(self) -> tuple[str, str, str]:
        return ("skip", "Smoke test skipped", "N/A")

    def _to_dict(self, result: BaselineVerifyResult) -> dict[str, Any]:
        return {
            "project_path": result.project_path,
            "layer_results": [
                {"layer_id": r.layer_id, "check": r.check, "status": r.status,
                 "command": r.command, "output": r.output, "retries": r.retries}
                for r in result.layer_results
            ],
            "output_path": result.output_path,
        }
