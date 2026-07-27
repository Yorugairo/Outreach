"""Restricted one-shot Hermes adapter for the routine OpenRouter route."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

from src.services.agentic_runtime import (
    AgenticRuntimeError,
    AgenticRuntimeRequest,
    AgenticRuntimeResponse,
)


class HermesOpenRouterRuntime:
    runtime_id = "hermes-openrouter"

    def __init__(
        self,
        *,
        executable: str = "hermes",
        expected_version: str = "0.18.2",
        runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
        working_root: str | Path | None = None,
    ) -> None:
        self.executable = executable
        self.expected_version = expected_version
        self._runner = runner
        self.working_root = Path(working_root) if working_root else None

    def version_status(self) -> dict[str, Any]:
        try:
            completed = self._runner(
                [self.executable, "--version"],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return {
                "available": False,
                "expected_version": self.expected_version,
                "observed": None,
                "error": str(exc),
            }
        observed = (completed.stdout or completed.stderr or "").strip()
        return {
            "available": completed.returncode == 0
            and self.expected_version in observed,
            "expected_version": self.expected_version,
            "observed": observed[:500],
            "error": None if completed.returncode == 0 else "version command failed",
        }

    def build_command(
        self,
        request: AgenticRuntimeRequest,
        *,
        usage_file: Path,
    ) -> list[str]:
        if request.tool_policy not in {"scoped_mcp", "none"}:
            raise AgenticRuntimeError(
                "Hermes request used an unsupported tool policy",
                failure_class="policy",
            )
        command = [
            self.executable,
            "--profile",
            request.profile,
            "--oneshot",
            request.prompt,
            "--usage-file",
            str(usage_file),
            "--model",
            request.requested_model,
            "--provider",
            request.requested_provider,
            "--toolsets",
            "mcp" if request.tool_policy == "scoped_mcp" else "none",
            "--ignore-rules",
            "--no-restore-cwd",
        ]
        return command

    def analyze(self, request: AgenticRuntimeRequest) -> AgenticRuntimeResponse:
        version = self.version_status()
        if not version["available"]:
            raise AgenticRuntimeError(
                "Pinned Hermes runtime is unavailable or has a version mismatch",
                failure_class="policy",
            )
        base = self.working_root
        with tempfile.TemporaryDirectory(
            prefix="outreach-hermes-",
            dir=str(base) if base else None,
        ) as temp_dir:
            temp_path = Path(temp_dir)
            usage_file = temp_path / "usage.json"
            command = self.build_command(request, usage_file=usage_file)
            env = {
                key: value
                for key, value in os.environ.items()
                if key
                not in {
                    "PYTHONSTARTUP",
                    "PROMPT_COMMAND",
                    "BASH_ENV",
                }
            }
            started = time.perf_counter()
            try:
                completed = self._runner(
                    command,
                    cwd=temp_path,
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=request.timeout_seconds,
                    check=False,
                )
            except subprocess.TimeoutExpired as exc:
                raise AgenticRuntimeError(
                    "Hermes one-shot timed out",
                    failure_class="transient",
                ) from exc
            except OSError as exc:
                raise AgenticRuntimeError(
                    "Hermes executable could not be started",
                    failure_class="policy",
                ) from exc
            latency_ms = max(0, int((time.perf_counter() - started) * 1000))
            if completed.returncode != 0:
                message = (completed.stderr or completed.stdout or "")[:500]
                failure = self._failure_class(message)
                raise AgenticRuntimeError(
                    f"Hermes one-shot failed: {message}",
                    failure_class=failure,
                )
            try:
                payload = json.loads(completed.stdout)
            except json.JSONDecodeError as exc:
                raise AgenticRuntimeError(
                    "Hermes returned non-JSON output",
                    failure_class="validation",
                ) from exc
            usage = self._usage(usage_file)
            return AgenticRuntimeResponse(
                payload=payload,
                served_provider=str(
                    usage.get("provider") or request.requested_provider
                ),
                served_model=str(usage.get("model") or request.requested_model),
                input_tokens=int(usage.get("input_tokens") or 0),
                output_tokens=int(usage.get("output_tokens") or 0),
                reasoning_tokens=int(usage.get("reasoning_tokens") or 0),
                actual_cost_usd=self._optional_float(
                    usage.get("actual_cost_usd") or usage.get("cost_usd")
                ),
                estimated_cost_usd=self._optional_float(
                    usage.get("estimated_cost_usd")
                ),
                latency_ms=latency_ms,
                raw_response={
                    "payload": payload,
                    "usage": usage,
                    "runtime_version": version["observed"],
                },
                routing_mode="fixed-zdr",
            )

    @staticmethod
    def _usage(path: Path) -> dict[str, Any]:
        if not path.is_file():
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    @staticmethod
    def _optional_float(value: object) -> float | None:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        return float(value)

    @staticmethod
    def _failure_class(message: str) -> str:
        lowered = message.casefold()
        if any(term in lowered for term in ("401", "authentication", "api key")):
            return "authentication"
        if any(term in lowered for term in ("402", "payment", "credits")):
            return "payment"
        if any(term in lowered for term in ("429", "rate limit", "timeout", "503")):
            return "transient"
        return "unknown"
