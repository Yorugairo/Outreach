"""Reviewed buyer-question and journey contracts for the P12 verticals.

The ordinary :mod:`src.vertical_packs` module describes intake and offer
taxonomy.  This module is intentionally separate: agentic packs describe only
what a bounded worker may ask, observe, and test.  They are immutable inputs to
the worker and never change deterministic scoring.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

from src.models import VerticalAgenticPack, VerticalPack, canonical_sha256


AGENTIC_PACK_VERSION = "agentic.v1"
ACTION_HOST_POLICY_VERSION = "known-hosts.v1"

# These are the three actual offers.  Keep the identifiers in one place so a
# model cannot invent an offer name that is not present in the product.
SERVICE_PACKAGE_IDS = (
    "website_seo_vertical_visibility",
    "vertical_plugin_embed",
    "custom_website_crm_saas",
)


def _applicability(*, categories: tuple[str, ...] | None = None, requires_facts: tuple[str, ...] = ()) -> dict[str, Any]:
    payload: dict[str, Any] = {"all": True}
    if categories:
        payload["categories"] = list(categories)
    if requires_facts:
        payload["requires_facts"] = list(requires_facts)
    return payload


def _oracle(
    *required: str,
    optional: tuple[str, ...] = (),
    required_any_text: tuple[str, ...] = (),
    required_any_url_fragments: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Return a machine-checkable, non-mutating success oracle."""

    return {
        "required_evidence": list(required),
        "optional_evidence": list(optional),
        "evidence_kinds": ["persisted_field", "source_span", "dom", "screenshot"],
        "requires_form_submission": False,
        "requires_personal_data": False,
        "failure_if": ["evidence_not_persisted", "action_host_not_approved"],
        "required_any_text": list(required_any_text),
        "required_any_url_fragments": list(required_any_url_fragments),
    }


def _journeys(vertical_id: str) -> list[dict[str, Any]]:
    """The exact three automatic target journeys required by P12."""

    if vertical_id == "national_bjj_registry":
        offer_terms = ("program", "class", "jiu jitsu", "bjj")
        decision_terms = ("schedule", "beginner", "trial", "pricing", "faq")
        cta_terms = ("contact", "trial", "join", "book", "start")
    else:
        offer_terms = ("service", "repair", "installation", "replacement")
        decision_terms = ("estimate", "quote", "service area", "schedule", "pricing", "faq")
        cta_terms = ("contact", "quote", "estimate", "book", "schedule")
    return [
        {
            "task_id": f"{vertical_id}.offer-discovery.v1",
            "task_kind": "offer_discovery",
            "viewport": "desktop",
            "objective": "Find the primary programs or services without guessing from generic copy.",
            "allowed_actions": ["navigate_candidate", "activate_candidate", "scroll", "wait", "capture"],
            "success_oracle": _oracle(
                "primary_offer",
                "offer_destination",
                required_any_text=offer_terms,
                required_any_url_fragments=("service", "program", "class"),
            ),
            "applicability": _applicability(),
            "max_model_decisions": 12,
            "max_browser_actions": 30,
            "timeout_seconds": 90,
        },
        {
            "task_id": f"{vertical_id}.decision-resolution.v1",
            "task_kind": "decision_resolution",
            "viewport": "mobile",
            "objective": "Resolve the most important first-visit, fit, availability, or service-area questions.",
            "allowed_actions": ["navigate_candidate", "activate_candidate", "scroll", "go_back", "wait", "capture"],
            "success_oracle": _oracle(
                "decision_answer",
                optional=("trust_signal", "schedule_or_availability"),
                required_any_text=decision_terms,
                required_any_url_fragments=("schedule", "faq", "pricing", "beginner", "service-area"),
            ),
            "applicability": _applicability(),
            "max_model_decisions": 12,
            "max_browser_actions": 30,
            "timeout_seconds": 90,
        },
        {
            "task_id": f"{vertical_id}.ready-to-convert-cta.v1",
            "task_kind": "ready_to_convert_cta",
            "viewport": "mobile",
            "objective": "Reach a clear, non-submitting contact or trial/quote action and record its destination.",
            "allowed_actions": ["navigate_candidate", "activate_candidate", "scroll", "go_back", "wait", "capture"],
            "success_oracle": _oracle(
                "cta_destination",
                optional=("contact_route",),
                required_any_text=cta_terms,
                required_any_url_fragments=("contact", "trial", "quote", "book", "schedule"),
            ),
            "applicability": _applicability(),
            "max_model_decisions": 12,
            "max_browser_actions": 30,
            "timeout_seconds": 90,
        },
    ]


def _question(
    question_id: str,
    text: str,
    buyer_stage: str,
    *,
    fact_keys: tuple[str, ...] = (),
    sensitive: bool = False,
    services: tuple[str, ...] = SERVICE_PACKAGE_IDS,
    categories: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    return {
        "question_id": question_id,
        "question": text,
        "buyer_stage": buyer_stage,
        "applicability": _applicability(categories=categories),
        "expected_fact_keys": list(fact_keys),
        "sensitivity_class": "sensitive" if sensitive else "public",
        "service_mappings": list(services),
        "reviewed": True,
        "answer_policy": {
            "positive_requires_exact_evidence": True,
            "unknown_on_missing_evidence": True,
            "operator_review_required": sensitive,
        },
    }


def _pack_payload(vertical_id: str, display_name: str, questions: list[dict[str, Any]]) -> dict[str, Any]:
    payload = {
        "contract_version": "vertical-agentic-pack.v1",
        "vertical_id": vertical_id,
        "version": f"{vertical_id}.agentic.v1",
        "display_name": display_name,
        "buyer_questions": questions,
        "journey_tasks": _journeys(vertical_id),
        # Values are question IDs, matching the typed ``dict[str, list[str]]``
        # contract.  Human-facing offer descriptions live in the ordinary
        # vertical pack and are deliberately not model-generated here.
        "service_mappings": {
            "website_seo_vertical_visibility": [item["question_id"] for item in questions],
            "vertical_plugin_embed": [
                item["question_id"]
                for item in questions
                if item["question_id"] in {"programs", "schedule", "cta", "services", "estimate", "service-area"}
            ],
            "custom_website_crm_saas": ["cta", "schedule", "estimate", "contact_route"],
        },
        "action_host_policy_version": ACTION_HOST_POLICY_VERSION,
    }
    return payload


def _build_pack(vertical_id: str, display_name: str, questions: list[dict[str, Any]]) -> VerticalAgenticPack:
    payload = _pack_payload(vertical_id, display_name, questions)
    source_sha256 = canonical_sha256(payload)
    return VerticalAgenticPack(
        id=f"vertical-agentic-pack-{vertical_id}-v1",
        vertical_id=vertical_id,
        version=payload["version"],
        display_name=display_name,
        buyer_questions=questions,
        journey_tasks=payload["journey_tasks"],
        service_mappings=payload["service_mappings"],
        action_host_policy_version=ACTION_HOST_POLICY_VERSION,
        source_sha256=source_sha256,
        state="approved",
        approved_by="operator-reviewed-pack",
        approved_at="2026-07-26T00:00:00+00:00",
    )


_BJJ_QUESTIONS = [
    _question("programs", "What programs and class formats are available?", "discovery", fact_keys=("programs",)),
    _question("beginner-fit", "Can a new student start safely without prior grappling experience?", "consideration", fact_keys=("beginner_path",)),
    _question("kids-fit", "Are kids, family, or youth classes available and for which ages?", "consideration", fact_keys=("kids_program",)),
    _question("schedule", "When can a prospective student attend, and is a first visit or trial explained?", "decision", fact_keys=("schedule", "trial_path")),
    _question("location", "Where is the academy, and what Tacoma-area location details are confirmed?", "decision", fact_keys=("location",)),
    _question("instructor", "Who teaches the academy and what credentials or lineage are explicitly documented?", "consideration", fact_keys=("instructor", "lineage"), sensitive=True),
    _question("pricing", "What membership, trial, or introductory pricing is explicitly published?", "decision", fact_keys=("pricing",), sensitive=True),
    _question("cta", "What is the clearest next step to contact, book, or start a trial?", "conversion", fact_keys=("contact_route", "trial_path")),
]

_TRADE_QUESTIONS = [
    _question("services", "Which home-service jobs and service types does the business explicitly handle?", "discovery", fact_keys=("services",)),
    _question("emergency", "Is emergency, same-day, or after-hours availability clearly explained?", "consideration", fact_keys=("emergency_availability",)),
    _question("service-area", "Which cities, neighborhoods, or service areas are explicitly covered?", "decision", fact_keys=("service_area",)),
    _question("estimate", "Can a prospective customer understand how to request an estimate or quote?", "decision", fact_keys=("quote_path",)),
    _question("schedule", "What scheduling, response-time, or appointment expectations are documented?", "decision", fact_keys=("schedule",)),
    _question("credentials", "Which licenses, insurance, warranties, or experience claims are explicitly supported?", "consideration", fact_keys=("credentials",), sensitive=True),
    _question("pricing", "Is pricing or a pricing range published, and is it clearly qualified?", "decision", fact_keys=("pricing",), sensitive=True),
    _question("cta", "What is the clearest next step to call, request a quote, or book service?", "conversion", fact_keys=("contact_route", "quote_path")),
]


NATIONAL_BJJ_REGISTRY_AGENTIC_V1 = _build_pack(
    "national_bjj_registry", "National BJJ Registry — Agentic v1", _BJJ_QUESTIONS
)
ONE_TRADE_NETWORK_AGENTIC_V1 = _build_pack(
    "one_trade_network", "One Trade Network — Agentic v1", _TRADE_QUESTIONS
)

BUILTIN_VERTICAL_AGENTIC_PACKS: dict[str, VerticalAgenticPack] = {
    NATIONAL_BJJ_REGISTRY_AGENTIC_V1.version: NATIONAL_BJJ_REGISTRY_AGENTIC_V1,
    ONE_TRADE_NETWORK_AGENTIC_V1.version: ONE_TRADE_NETWORK_AGENTIC_V1,
}


@dataclass(frozen=True, slots=True)
class AgenticPackResolution:
    """Reconciliation result used by automatic enqueueing and operator tools."""

    pack: VerticalAgenticPack | None
    eligible: bool
    reason: str


def list_vertical_agentic_packs() -> list[VerticalAgenticPack]:
    return [deepcopy(item) for item in BUILTIN_VERTICAL_AGENTIC_PACKS.values()]


def get_vertical_agentic_pack(version: str) -> VerticalAgenticPack:
    """Load one reviewed pack by its immutable version identifier."""

    aliases = {
        "national_bjj_registry.v1": NATIONAL_BJJ_REGISTRY_AGENTIC_V1.version,
        "one_trade_network.v1": ONE_TRADE_NETWORK_AGENTIC_V1.version,
        "national_bjj_registry": NATIONAL_BJJ_REGISTRY_AGENTIC_V1.version,
        "one_trade_network": ONE_TRADE_NETWORK_AGENTIC_V1.version,
    }
    key = aliases.get(str(version).strip(), str(version).strip())
    try:
        return deepcopy(BUILTIN_VERTICAL_AGENTIC_PACKS[key])
    except KeyError as exc:
        available = ", ".join(sorted(BUILTIN_VERTICAL_AGENTIC_PACKS))
        raise ValueError(f"unknown vertical agentic pack {version!r}; available: {available}") from exc


def resolve_vertical_agentic_pack(value: str | VerticalPack | VerticalAgenticPack) -> VerticalAgenticPack:
    if isinstance(value, VerticalAgenticPack):
        return deepcopy(value)
    if isinstance(value, VerticalPack):
        return get_vertical_agentic_pack(value.vertical_id)
    return get_vertical_agentic_pack(str(value))


def reconcile_vertical_agentic_pack(
    value: str | VerticalPack | VerticalAgenticPack | None,
    *,
    qualified: bool = True,
    operator_enabled: bool = True,
    require_approved: bool = True,
) -> AgenticPackResolution:
    """Resolve the pack while preserving the exact reason automatic work is skipped."""

    if value is None:
        return AgenticPackResolution(None, False, "no vertical agentic pack was bound")
    try:
        pack = resolve_vertical_agentic_pack(value)
    except (TypeError, ValueError) as exc:
        return AgenticPackResolution(None, False, str(exc))
    if require_approved and pack.state != "approved":
        return AgenticPackResolution(pack, False, "vertical agentic pack is not operator-approved")
    if not qualified:
        return AgenticPackResolution(pack, False, "prospect is not qualified for automatic agentic work")
    if not operator_enabled:
        return AgenticPackResolution(pack, False, "agentic runtime is not operator-enabled")
    return AgenticPackResolution(pack, True, "eligible")


__all__ = [
    "AGENTIC_PACK_VERSION",
    "ACTION_HOST_POLICY_VERSION",
    "SERVICE_PACKAGE_IDS",
    "AgenticPackResolution",
    "BUILTIN_VERTICAL_AGENTIC_PACKS",
    "NATIONAL_BJJ_REGISTRY_AGENTIC_V1",
    "ONE_TRADE_NETWORK_AGENTIC_V1",
    "list_vertical_agentic_packs",
    "get_vertical_agentic_pack",
    "resolve_vertical_agentic_pack",
    "reconcile_vertical_agentic_pack",
]
