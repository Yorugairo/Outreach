from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


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
class AppConfig:
    dataforseo: DataForSEOSettings
    retry: "RetryPolicy" = field(default_factory=RetryPolicy)
    approval: "ApprovalPolicy" = field(default_factory=ApprovalPolicy)


def load_config(dotenv_path: str | Path | None = None) -> AppConfig:
    dotenv_values = _dotenv_values(dotenv_path or ROOT_DIR / ".env")
    values = {**dotenv_values, **os.environ}
    location_code = int(values.get("DATAFORSEO_DEFAULT_LOCATION_CODE", "2840"))
    timeout_seconds = int(values.get("DATAFORSEO_TIMEOUT_SECONDS", "30"))
    max_paid_calls = max(0, int(values.get("DATAFORSEO_MAX_CALLS", "6")))
    allow_paid_api_calls = values.get("SEO_INSIGHTS_ALLOW_PAID_API_CALLS", "false").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    return AppConfig(
        dataforseo=DataForSEOSettings(
            login=values.get("DATAFORSEO_LOGIN"),
            password=values.get("DATAFORSEO_PASSWORD"),
            default_location_code=location_code,
            default_language_code=values.get("DATAFORSEO_DEFAULT_LANGUAGE_CODE", "en"),
            api_base=values.get("DATAFORSEO_API_BASE", "https://api.dataforseo.com").rstrip("/"),
            timeout_seconds=timeout_seconds,
            max_paid_calls=max_paid_calls,
        ),
        approval=ApprovalPolicy(allow_paid_api_calls=allow_paid_api_calls),
    )
