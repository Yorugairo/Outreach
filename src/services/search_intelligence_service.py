from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.config import AppConfig
from src.dataforseo_client import DataForSEOClient


@dataclass(slots=True)
class SearchIntelligenceOutput:
    configured: bool
    skipped_reason: str | None
    payload: dict[str, Any]
    approved: bool = False


class SearchIntelligenceService:
    def __init__(self, config: AppConfig, artifact_dir: str | None = None):
        self.config = config
        self.artifact_dir = artifact_dir

    def gather(self) -> SearchIntelligenceOutput:
        if not self.config.dataforseo.configured:
            return SearchIntelligenceOutput(
                configured=False,
                skipped_reason="DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD not configured",
                payload={},
                approved=False,
            )

        if not self.config.approval.allow_paid_api_calls:
            return SearchIntelligenceOutput(
                configured=True,
                skipped_reason="Paid DataForSEO enrichment requires explicit operator approval",
                payload={},
                approved=False,
            )

        client = DataForSEOClient(self.config.dataforseo, artifact_dir=self.artifact_dir)
        response = client.get_errors_reference()
        tasks_error = response.get("tasks_error")
        status_code = response.get("status_code")
        return SearchIntelligenceOutput(
            configured=True,
            skipped_reason=None,
            payload={
                "status_code": status_code,
                "tasks_error": tasks_error,
                "raw_excerpt_keys": list(response.keys())[:10],
            },
            approved=True,
        )
