from __future__ import annotations

import os
from dataclasses import asdict, dataclass, field
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
APP_RUNTIME_DOTENV = ROOT_DIR / "docs" / "local.env"


def load_dotenv(path: str | Path | None = None) -> None:
    env_path = Path(path) if path else ROOT_DIR / ".env"
    if not env_path.exists():
        return

    for key, value in _dotenv_values(env_path).items():
        os.environ.setdefault(key, value)


def _dotenv_values(path: str | Path) -> dict[str, str]:
    env_path = Path(path)
    if not env_path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


@dataclass(slots=True)
class DataForSEOSettings:
    login: str | None
    password: str | None
    default_location_code: int = 2840
    default_language_code: str = "en"
    api_base: str = "https://api.dataforseo.com"
    timeout_seconds: int = 30
    max_paid_calls: int = 6
    premium_warning_threshold_usd: float = 1.50
    keyword_metrics_call_ceiling_usd: float = 0.10
    serp_call_ceiling_usd: float = 0.02
    authority_call_ceiling_usd: float = 0.05

    @property
    def configured(self) -> bool:
        return bool(self.login and self.password)

    def require_credentials(self) -> None:
        if not self.configured:
            raise RuntimeError(
                "Missing DataForSEO credentials. Set DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD."
            )


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 10.0


@dataclass
class ApprovalPolicy:
    allow_paid_api_calls: bool = False


@dataclass(slots=True)
class AgenticAnalysisSettings:
    """Sanitized, operator-gated policy for optional agentic analysis.

    Credentials are intentionally not represented here.  Provider adapters may
    load their own secrets at the protected runtime boundary, while this
    snapshot is safe to persist and expose in diagnostics.
    """

    enabled: bool = False
    operator_approved: bool = False
    promotion_approved: bool = False
    runtime: str = "hermes-openrouter"
    provider: str = "openrouter"
    model: str = "deepseek/deepseek-v4-flash"
    profile: str = "outreach-analysis"
    prompt_version: str = "outreach-analysis.prompt.v1"
    rubric_version: str = "outreach-analysis.rubric.v1"
    schema_version: str = "agentic-assessment.v1"
    max_calls: int = 4
    max_cost_usd: float = 0.10
    max_output_tokens: int = 8_000
    timeout_seconds: int = 120
    retry_limit: int = 2
    hermes_executable: str = "hermes"
    hermes_version: str = "0.18.2"
    max_evidence_pack_bytes: int = 250_000
    require_structured_output: bool = True
    require_zdr: bool = True
    allow_codex_review: bool = False

    def __post_init__(self) -> None:
        required = (
            self.runtime, self.provider, self.model, self.profile,
            self.prompt_version, self.rubric_version, self.schema_version,
            self.hermes_executable, self.hermes_version,
        )
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError("agentic settings require complete route and contract identity")
        if self.max_calls < 1 or self.max_calls > 4:
            raise ValueError("agentic settings permit one to four model calls")
        if not 0 < self.max_cost_usd <= 0.10:
            raise ValueError("agentic settings cost ceiling must be positive and no more than $0.10")
        if self.max_output_tokens < 1 or self.timeout_seconds < 1:
            raise ValueError("agentic settings token and time ceilings must be positive")
        if not 0 <= self.retry_limit <= 2:
            raise ValueError("agentic settings transient retry limit cannot exceed two")
        if self.max_evidence_pack_bytes < 10_000:
            raise ValueError("agentic evidence-pack byte ceiling is too small")

    @property
    def available(self) -> bool:
        return (
            self.enabled
            and self.operator_approved
            and self.promotion_approved
        )

    def to_dict(self) -> dict[str, object]:
        # Keep this explicit so future secret-bearing adapter settings cannot
        # accidentally leak into persisted policy snapshots.
        return asdict(self)

    redacted = to_dict


@dataclass(slots=True)
class AppConfig:
    dataforseo: DataForSEOSettings
    retry: "RetryPolicy" = field(default_factory=RetryPolicy)
    approval: "ApprovalPolicy" = field(default_factory=ApprovalPolicy)
    agentic: AgenticAnalysisSettings = field(default_factory=AgenticAnalysisSettings)

    @property
    def agentic_analysis(self) -> AgenticAnalysisSettings:
        return self.agentic


def load_config(dotenv_path: str | Path | None = None) -> AppConfig:
    dotenv_values = _dotenv_values(dotenv_path or ROOT_DIR / ".env")
    values = {**dotenv_values, **os.environ}
    location_code = int(values.get("DATAFORSEO_DEFAULT_LOCATION_CODE", "2840"))
    timeout_seconds = int(values.get("DATAFORSEO_TIMEOUT_SECONDS", "30"))
    max_paid_calls = max(0, int(values.get("DATAFORSEO_MAX_CALLS", "6")))
    premium_warning_threshold_usd = max(
        0.0,
        float(values.get("DATAFORSEO_PREMIUM_WARNING_THRESHOLD_USD", "1.50")),
    )
    allow_paid_api_calls = values.get("SEO_INSIGHTS_ALLOW_PAID_API_CALLS", "false").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    agentic_enabled = values.get(
        "AGENTIC_ANALYSIS_ENABLED", values.get("SEO_INSIGHTS_ALLOW_AGENTIC_ANALYSIS", "false")
    ).lower() in {"1", "true", "yes", "on"}
    agentic_approved = values.get(
        "AGENTIC_ANALYSIS_OPERATOR_APPROVED", values.get("AGENTIC_ANALYSIS_APPROVED", "false")
    ).lower() in {
        "1", "true", "yes", "on"
    }
    agentic_promotion_approved = values.get(
        "AGENTIC_ANALYSIS_PROMOTION_APPROVED",
        "false",
    ).lower() in {"1", "true", "yes", "on"}
    return AppConfig(
        dataforseo=DataForSEOSettings(
            login=values.get("DATAFORSEO_LOGIN"),
            password=values.get("DATAFORSEO_PASSWORD"),
            default_location_code=location_code,
            default_language_code=values.get("DATAFORSEO_DEFAULT_LANGUAGE_CODE", "en"),
            api_base=values.get("DATAFORSEO_API_BASE", "https://api.dataforseo.com").rstrip("/"),
            timeout_seconds=timeout_seconds,
            max_paid_calls=max_paid_calls,
            premium_warning_threshold_usd=premium_warning_threshold_usd,
            keyword_metrics_call_ceiling_usd=max(
                0.0,
                float(values.get("DATAFORSEO_KEYWORD_METRICS_CALL_CEILING_USD", "0.10")),
            ),
            serp_call_ceiling_usd=max(
                0.0,
                float(values.get("DATAFORSEO_SERP_CALL_CEILING_USD", "0.02")),
            ),
            authority_call_ceiling_usd=max(
                0.0,
                float(values.get("DATAFORSEO_AUTHORITY_CALL_CEILING_USD", "0.05")),
            ),
        ),
        approval=ApprovalPolicy(allow_paid_api_calls=allow_paid_api_calls),
        agentic=AgenticAnalysisSettings(
            enabled=agentic_enabled,
            operator_approved=agentic_approved,
            promotion_approved=agentic_promotion_approved,
            runtime=values.get("AGENTIC_ANALYSIS_RUNTIME", "hermes-openrouter"),
            provider=values.get("AGENTIC_ANALYSIS_PROVIDER", "openrouter"),
            model=values.get("AGENTIC_ANALYSIS_MODEL", "deepseek/deepseek-v4-flash"),
            profile=values.get("AGENTIC_ANALYSIS_PROFILE", "outreach-analysis"),
            prompt_version=values.get("AGENTIC_ANALYSIS_PROMPT_VERSION", "outreach-analysis.prompt.v1"),
            rubric_version=values.get("AGENTIC_ANALYSIS_RUBRIC_VERSION", "outreach-analysis.rubric.v1"),
            schema_version=values.get("AGENTIC_ANALYSIS_SCHEMA_VERSION", "agentic-assessment.v1"),
            max_calls=max(1, min(4, int(values.get("AGENTIC_ANALYSIS_MAX_CALLS", "4")))),
            max_cost_usd=max(0.000001, min(0.10, float(values.get("AGENTIC_ANALYSIS_MAX_COST_USD", "0.10")))),
            max_output_tokens=max(1, int(values.get("AGENTIC_ANALYSIS_MAX_OUTPUT_TOKENS", "8000"))),
            timeout_seconds=max(1, int(values.get("AGENTIC_ANALYSIS_TIMEOUT_SECONDS", "120"))),
            retry_limit=max(0, min(2, int(values.get("AGENTIC_ANALYSIS_RETRY_LIMIT", "2")))),
            hermes_executable=values.get(
                "AGENTIC_ANALYSIS_HERMES_EXECUTABLE",
                "hermes",
            ),
            hermes_version=values.get(
                "AGENTIC_ANALYSIS_HERMES_VERSION",
                "0.18.2",
            ),
            max_evidence_pack_bytes=max(
                10_000,
                int(
                    values.get(
                        "AGENTIC_ANALYSIS_MAX_EVIDENCE_PACK_BYTES",
                        "250000",
                    )
                ),
            ),
            require_structured_output=values.get(
                "AGENTIC_ANALYSIS_REQUIRE_STRUCTURED_OUTPUT",
                "true",
            ).lower()
            in {"1", "true", "yes", "on"},
            require_zdr=values.get(
                "AGENTIC_ANALYSIS_REQUIRE_ZDR",
                "true",
            ).lower()
            in {"1", "true", "yes", "on"},
            allow_codex_review=values.get(
                "ALLOW_CODEX_REVIEW",
                "false",
            ).lower()
            in {"1", "true", "yes", "on"},
        ),
    )
