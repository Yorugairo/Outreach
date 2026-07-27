"""Built-in vertical contracts used by prospect intake and coverage services."""

from __future__ import annotations

from copy import deepcopy

from src.models import VerticalPack


_COMMON_REQUIRED_FIELDS = [
    "business_name",
    "website_url",
    "category",
    "location",
    "contact_route",
    "source_provenance",
]


ONE_TRADE_NETWORK_V1 = VerticalPack(
    vertical_id="one_trade_network",
    version="v1",
    display_name="One Trade Network",
    allowed_business_categories=[
        "appliance repair",
        "carpenter",
        "cleaning service",
        "electrician",
        "general contractor",
        "handyman",
        "hvac",
        "landscaper",
        "locksmith",
        "painter",
        "pest control",
        "plumber",
        "roofer",
        "tree service",
        "window and door",
    ],
    required_fields=list(_COMMON_REQUIRED_FIELDS),
    service_taxonomy={
        "core_services": [
            "emergency service",
            "installation",
            "maintenance",
            "repair",
            "replacement",
        ],
        "commercial_packages": [
            "website_seo_vertical_visibility",
            "vertical_plugin_embed",
            "custom_website_crm_saas",
        ],
        "funnel_stages": [
            "visit",
            "lead",
            "qualified_appointment",
            "won_job",
        ],
    },
    location_taxonomy=["city", "county", "service_area", "neighborhood"],
    qualification_rules={
        "unknown_category_status": "needs_review",
        "missing_required_status": "rejected",
        "required_contact_route": True,
        "require_http_website": True,
    },
    offer_mappings={
        "website_seo_vertical_visibility": (
            "improve the existing website, sitemap, and SEO while leveraging "
            "One Trade Network visibility"
        ),
        "vertical_plugin_embed": (
            "add trade-specific One Trade Network plugins or embeds to the existing website"
        ),
        "custom_website_crm_saas": (
            "onboard to a custom trade website with an optional CRM/SaaS bundle"
        ),
    },
    outreach_constraints={"manual_approval_required": True, "automated_sending": False},
)


NATIONAL_BJJ_REGISTRY_V1 = VerticalPack(
    vertical_id="national_bjj_registry",
    version="v1",
    display_name="National BJJ Registry",
    allowed_business_categories=[
        "bjj academy",
        "brazilian jiu-jitsu academy",
        "brazilian jiu jitsu academy",
        "martial arts school",
        "martial arts gym",
        "jiu-jitsu gym",
    ],
    required_fields=list(_COMMON_REQUIRED_FIELDS),
    service_taxonomy={
        "core_services": [
            "adult classes",
            "kids classes",
            "beginner program",
            "private lessons",
            "open mat",
        ],
        "commercial_packages": [
            "website_seo_vertical_visibility",
            "vertical_plugin_embed",
            "custom_website_crm_saas",
        ],
        "funnel_stages": [
            "visit",
            "signup",
            "attended_trial",
            "member",
        ],
    },
    location_taxonomy=["city", "county", "service_area", "neighborhood"],
    qualification_rules={
        "unknown_category_status": "needs_review",
        "missing_required_status": "rejected",
        "required_contact_route": True,
        "require_http_website": True,
    },
    offer_mappings={
        "website_seo_vertical_visibility": (
            "improve the existing academy website, sitemap, and SEO while "
            "leveraging National BJJ Registry visibility"
        ),
        "vertical_plugin_embed": (
            "add BJJ-specific National BJJ Registry plugins or embeds to the academy website"
        ),
        "custom_website_crm_saas": (
            "onboard to a custom academy website with an optional CRM/SaaS bundle"
        ),
    },
    outreach_constraints={"manual_approval_required": True, "automated_sending": False},
)


BUILTIN_VERTICAL_PACKS: dict[str, VerticalPack] = {
    ONE_TRADE_NETWORK_V1.pack_id: ONE_TRADE_NETWORK_V1,
    NATIONAL_BJJ_REGISTRY_V1.pack_id: NATIONAL_BJJ_REGISTRY_V1,
}


def list_vertical_packs() -> list[VerticalPack]:
    """Return copies so callers cannot mutate the built-in contracts."""

    return [deepcopy(pack) for pack in BUILTIN_VERTICAL_PACKS.values()]


def get_vertical_pack(pack_id: str) -> VerticalPack:
    """Resolve a ``vertical_id.vN`` identifier or raise a useful error."""

    try:
        return deepcopy(BUILTIN_VERTICAL_PACKS[pack_id])
    except KeyError as exc:
        available = ", ".join(sorted(BUILTIN_VERTICAL_PACKS))
        raise ValueError(f"unknown vertical pack {pack_id!r}; available: {available}") from exc


def resolve_vertical_pack(value: str | VerticalPack) -> VerticalPack:
    if isinstance(value, VerticalPack):
        return value
    return get_vertical_pack(value)
