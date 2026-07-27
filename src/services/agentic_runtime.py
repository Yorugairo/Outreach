"""Provider-neutral, explicitly gated agentic analysis runtime adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Protocol


class AgenticRuntimeError(RuntimeError):
    def __init__(self, message: str, *, failure_class: str = "unknown") -> None:
        super().__init__(message)
        self.failure_class = failure_class


@dataclass(frozen=True, slots=True)
class AgenticRuntimeRequest:
    job_id: str
    evidence_pack_id: str
    evidence_pack_sha256: str
    pass_name: str
    prompt_version: str
    rubric_version: str
    schema_version: str
    requested_provider: str
    requested_model: str
    profile: str
    prompt: str
    prior_validated_output: dict[str, Any] = field(default_factory=dict)
    tool_policy: str = "scoped_mcp"
    max_output_tokens: int = 2_000
    timeout_seconds: int = 120


@dataclass(frozen=True, slots=True)
class AgenticRuntimeResponse:
    payload: dict[str, Any]
    served_provider: str
    served_model: str
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    actual_cost_usd: float | None = None
    estimated_cost_usd: float | None = None
    latency_ms: int = 0
    raw_response: dict[str, Any] = field(default_factory=dict)
    routing_mode: str = "fixed"


class AgenticAnalysisRuntime(Protocol):
    runtime_id: str

    def analyze(self, request: AgenticRuntimeRequest) -> AgenticRuntimeResponse: ...


class DirectOpenRouterRuntime:
    """Controlled adapter boundary; network transport is always injected."""

    runtime_id = "direct-openrouter"

    def __init__(
        self,
        transport: Callable[[AgenticRuntimeRequest], AgenticRuntimeResponse] | None = None,
        *,
        operator_approved: bool = False,
    ) -> None:
        self._transport = transport
        self.operator_approved = operator_approved

    def analyze(self, request: AgenticRuntimeRequest) -> AgenticRuntimeResponse:
        if not self.operator_approved:
            raise AgenticRuntimeError(
                "Direct OpenRouter inference requires explicit operator approval",
                failure_class="policy",
            )
        if self._transport is None:
            raise AgenticRuntimeError(
                "Direct OpenRouter transport is not configured",
                failure_class="authentication",
            )
        return self._transport(request)


class CodexReviewRuntime:
    """Operator-triggered exception adapter; never used as an automatic fallback."""

    runtime_id = "codex-review"

    def __init__(
        self,
        transport: Callable[[AgenticRuntimeRequest], AgenticRuntimeResponse] | None = None,
        *,
        allow_review: bool = False,
    ) -> None:
        self._transport = transport
        self.allow_review = allow_review

    def analyze(self, request: AgenticRuntimeRequest) -> AgenticRuntimeResponse:
        if not self.allow_review:
            raise AgenticRuntimeError(
                "Codex review requires an explicit operator review action",
                failure_class="policy",
            )
        if self._transport is None:
            raise AgenticRuntimeError(
                "Codex review transport is unavailable",
                failure_class="authentication",
            )
        return self._transport(request)
