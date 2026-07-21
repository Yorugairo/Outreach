from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent


def load_dotenv(path: str | Path | None = None) -> None:
    env_path = Path(path) if path else ROOT_DIR / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


@dataclass(slots=True)
class DataForSEOSettings:
    login: str | None
    password: str | None
    default_location_code: int = 2840
    default_language_code: str = "en"
    api_base: str = "https://api.dataforseo.com"
    timeout_seconds: int = 30

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
    load_dotenv(dotenv_path)
    location_code = int(os.getenv("DATAFORSEO_DEFAULT_LOCATION_CODE", "2840"))
    timeout_seconds = int(os.getenv("DATAFORSEO_TIMEOUT_SECONDS", "30"))
    allow_paid_api_calls = os.getenv("SEO_INSIGHTS_ALLOW_PAID_API_CALLS", "false").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    return AppConfig(
        dataforseo=DataForSEOSettings(
            login=os.getenv("DATAFORSEO_LOGIN"),
            password=os.getenv("DATAFORSEO_PASSWORD"),
            default_location_code=location_code,
            default_language_code=os.getenv("DATAFORSEO_DEFAULT_LANGUAGE_CODE", "en"),
            api_base=os.getenv("DATAFORSEO_API_BASE", "https://api.dataforseo.com").rstrip("/"),
            timeout_seconds=timeout_seconds,
        ),
        approval=ApprovalPolicy(allow_paid_api_calls=allow_paid_api_calls),
    )
