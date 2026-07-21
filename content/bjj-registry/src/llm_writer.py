"""llm_writer.py — model-agnostic flash-LLM renderer for pSEO articles.

Design:
  - The LLM is a RENDERER, not an author. It only turns the fact_bundle into prose.
  - Default model is the free Hy3 (tencent/hy3:free) available here + on OpenRouter.
  - Future model (DeepSeek V4 Flash) is a one-line swap via env vars — no code change.
  - OpenRouter is the preferred provider; falls back to a direct OpenAI-compatible base URL.
  - On any failure (no key, network, bad response) it returns None so the caller can
    fall back to the deterministic template writer.

Env / config (all optional; sane defaults provided):
  LLM_PROVIDER   openrouter | openai        (default: openrouter)
  LLM_MODEL      e.g. tencent/hy3:free | deepseek/deepseek-v4-flash:free
  LLM_API_KEY    OpenRouter/OpenAI key      (default: OPENROUTER_API_KEY or OPENAI_API_KEY)
  LLM_BASE_URL   override for self-hosted / compatible endpoints
  LLM_MAX_TOKENS output cap (default 900)
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

# Sane defaults: free now, cheap later. Swap by setting LLM_MODEL.
DEFAULT_MODEL = "tencent/hy3:free"
FUTURE_MODEL = "deepseek/deepseek-v4-flash:free"
DEFAULT_PROVIDER = "openrouter"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


@dataclass
class LLMConfig:
    provider: str = DEFAULT_PROVIDER
    model: str = DEFAULT_MODEL
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 900
    temperature: float = 0.4

    @classmethod
    def from_env(cls) -> "LLMConfig":
        provider = os.environ.get("LLM_PROVIDER", DEFAULT_PROVIDER).lower()
        model = os.environ.get("LLM_MODEL", DEFAULT_MODEL)
        key = os.environ.get("LLM_API_KEY") or os.environ.get(
            "OPENROUTER_API_KEY" if provider == "openrouter" else "OPENAI_API_KEY"
        )
        base = os.environ.get("LLM_BASE_URL")
        if provider == "openrouter" and not base:
            base = OPENROUTER_URL
        return cls(
            provider=provider,
            model=model,
            api_key=key,
            base_url=base,
            max_tokens=int(os.environ.get("LLM_MAX_TOKENS", "900")),
            temperature=float(os.environ.get("LLM_TEMPERATURE", "0.4")),
        )


SECTION_SYSTEM = (
    "You are a black-belt Brazilian Jiu-Jitsu practitioner ghostwriting helpful, honest "
    "location guide articles for the National BJJ Registry. You receive a strict fact bundle. "
    "Rules you MUST obey:\n"
    "1. Use ONLY the provided facts and signals. Never invent academy names, counts, ranks, or quotes.\n"
    "2. Do NOT print any numeric registry scores or percentages. Express quality qualitatively "
    "(e.g. 'a strong training market', 'above the state average', 'a deep elite tier').\n"
    "3. Voice: an expert who's been on the mats 15 years — concrete, plain-spoken, opinionated but "
    "never arrogant, never marketing fluff. Tell beginners what they'd actually want to know.\n"
    "4. Mirror the H2 section headings given; write 2-4 natural sentences per section. No extra headings.\n"
    "5. If a section's facts are empty, write a brief honest placeholder, do not fabricate."
)


def _build_user_prompt(bundle: dict, headings: list[str]) -> str:
    import json
    return (
        "FACT BUNDLE (use only this):\n"
        + json.dumps(bundle, indent=2, ensure_ascii=False)
        + "\n\nSECTIONS TO WRITE (return each as '## Heading\\n<prose>'):\n"
        + "\n".join(headings)
    )


def render_sections(bundle: dict, headings: list[str], cfg: Optional[LLMConfig] = None) -> Optional[str]:
    """Return LLM-written markdown for the given headings, or None on any failure."""
    cfg = cfg or LLMConfig.from_env()
    if not cfg.api_key or not cfg.base_url:
        return None  # no credentials -> caller uses template fallback
    try:
        import urllib.request
        import json

        payload = {
            "model": cfg.model,
            "messages": [
                {"role": "system", "content": SECTION_SYSTEM},
                {"role": "user", "content": _build_user_prompt(bundle, headings)},
            ],
            "max_tokens": cfg.max_tokens,
            "temperature": cfg.temperature,
        }
        req = urllib.request.Request(
            cfg.base_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {cfg.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://nationalbjjregistry.org",
                "X-Title": "BJJ Registry pSEO",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:  # noqa: BLE001 — any failure => template fallback
        print(f"[llm_writer] render failed ({e}); falling back to template.")
        return None
