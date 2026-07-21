from __future__ import annotations

import urllib.parse

from src.config import AppConfig
from src.models import SEOTarget


class TargetIntakeService:
    def __init__(self, config: AppConfig):
        self.config = config

    def build_target(self, url: str) -> SEOTarget:
        normalized_url, normalized_domain = self._normalize(url)
        return SEOTarget(
            input_url=url,
            normalized_url=normalized_url,
            normalized_domain=normalized_domain,
            canonical_domain=normalized_domain,
            display_name=normalized_domain,
            default_location_code=self.config.dataforseo.default_location_code,
            default_language_code=self.config.dataforseo.default_language_code,
        )

    @staticmethod
    def _normalize(url: str) -> tuple[str, str]:
        candidate = url.strip()
        if not candidate.startswith(("http://", "https://")):
            candidate = f"https://{candidate}"
        parsed = urllib.parse.urlparse(candidate)
        normalized_domain = parsed.netloc.lower()
        normalized_path = parsed.path.rstrip("/")
        normalized_url = urllib.parse.urlunparse((parsed.scheme.lower(), normalized_domain, normalized_path, "", "", ""))
        if not normalized_path:
            normalized_url = normalized_url.rstrip("/")
        return normalized_url, normalized_domain
