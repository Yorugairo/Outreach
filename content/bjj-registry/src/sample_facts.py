"""sample_facts: ILLUSTRATIVE seed data for the BJJ Registry pSEO generator.

⚠️ ALL values below are SAMPLE / UNVERIFIED. They demonstrate the schema and
let the generator run end-to-end. Before publishing, replace with registry-DB
values and set verified=True (or verified per-field via LocationFacts).
Named academies are drawn from public listings (Yelp/Gold BJJ) and marked
source="external_listing" — confirm against the live registry first.
"""
from __future__ import annotations

from location_facts import AcademyRef, LocationFacts

# ---------------- NATIONAL ----------------
NATIONAL = LocationFacts(
    tier="national",
    name="USA",
    slug="national",
    academy_count=3200,
    academy_count_source="registry_sample",
    academy_count_verified=False,
    top_cities=["Austin TX", "Los Angeles CA", "New York NY", "San Diego CA", "Chicago IL",
                "Seattle WA", "Atlanta GA", "Denver CO", "Miami FL", "Portland OR"],
    lineages_present=["Gracie Barra", "Atos", "Renzo Gracie", "Alliance", "CheckMat", "10th Planet"],
    events=["the IBJJF American Nationals", "local state championships"],
    notable_facts=[
        "BJJ in the US traces heavily to the Gracie family's early 1990s introductions.",
    ],
)

# ---------------- STATES ----------------
TEXAS = LocationFacts(
    tier="state",
    name="Texas",
    slug="texas",
    state="TX",
    state_slug="texas",
    state_name="Texas",
    parent_slug="national",
    child_slugs=["austin-tx", "dallas-tx", "houston-tx", "san-antonio-tx"],
    academy_count=240,
    academy_count_verified=False,
    top_cities=["Austin", "Dallas", "Houston", "San Antonio", "Fort Worth"],
    lineages_present=["Gracie Barra", "Atos", "Renzo Gracie", "10th Planet"],
    events=["the Texas State Jiu-Jitsu Championship", "Gracie Barra Texas Open"],
    top_academies=[
        AcademyRef("Renzo Gracie Austin", city="Austin", state="TX", lineage="Renzo Gracie",
                   note="systematic curriculum with professional instructors",
                   source="external_listing", verified=False),
        AcademyRef("Paragon Jiu Jitsu Academy", city="Austin", state="TX",
                   note="long-standing Austin school with competition team",
                   source="external_listing", verified=False),
        AcademyRef("Atos Austin Brazilian Jiu Jitsu", city="Austin", state="TX", lineage="Atos",
                   source="external_listing", verified=False),
    ],
)

CALIFORNIA = LocationFacts(
    tier="state",
    name="California",
    slug="california",
    state="CA",
    state_slug="california",
    state_name="California",
    parent_slug="national",
    child_slugs=["los-angeles-ca", "san-diego-ca", "san-francisco-ca"],
    academy_count=520,
    academy_count_verified=False,
    top_cities=["Los Angeles", "San Diego", "San Francisco", "Sacramento", "San Jose"],
    lineages_present=["Gracie Barra", "CheckMat", "Atos", "10th Planet"],
    events=["the California State Championship", "IBJJF Los Angeles Open"],
    top_academies=[
        AcademyRef("Gracie Barra Long Beach", city="Long Beach", state="CA", lineage="Gracie Barra",
                   source="external_listing", verified=False),
        AcademyRef("CheckMat HQ", city="Los Angeles", state="CA", lineage="CheckMat",
                   source="external_listing", verified=False),
    ],
)

# ---------------- COUNTIES ----------------
TRAVIS_COUNTY = LocationFacts(
    tier="county",
    name="Travis County",
    slug="travis-county-tx",
    state="TX",
    state_slug="texas",
    state_name="Texas",
    county="Travis County",
    parent_slug="texas",
    child_slugs=["austin-tx"],
    academy_count=70,
    academy_count_verified=False,
    top_cities=["Austin", "Pflugerville", "Round Rock", "Cedar Park"],
    lineages_present=["Renzo Gracie", "Gracie Barra", "Atos"],
    events=["the Travis County Open Mat Series"],
    top_academies=[
        AcademyRef("Renzo Gracie Austin", city="Austin", state="TX", lineage="Renzo Gracie",
                   source="external_listing", verified=False),
    ],
)

# ---------------- CITIES ----------------
AUSTIN = LocationFacts(
    tier="city",
    name="Austin",
    slug="austin-tx",
    state="TX",
    state_slug="texas",
    state_name="Texas",
    county="Travis County",
    city="Austin",
    parent_slug="travis-county-tx",
    academy_count=58,
    academy_count_verified=False,
    lineages_present=["Renzo Gracie", "Gracie Barra", "Atos", "10th Planet"],
    top_academies=[
        AcademyRef("Renzo Gracie Austin", city="Austin", state="TX", lineage="Renzo Gracie",
                   note="systematic approach, professional instructors",
                   source="external_listing", verified=False),
        AcademyRef("Paragon Jiu Jitsu Academy", city="Austin", state="TX",
                   note="established competition-focused school",
                   source="external_listing", verified=False),
        AcademyRef("Atos Austin Brazilian Jiu Jitsu", city="Austin", state="TX", lineage="Atos",
                   source="external_listing", verified=False),
        AcademyRef("Gracie Barra Westlake", city="Austin", state="TX", lineage="Gracie Barra",
                   source="external_listing", verified=False),
    ],
)

DALLAS = LocationFacts(
    tier="city",
    name="Dallas",
    slug="dallas-tx",
    state="TX",
    state_slug="texas",
    state_name="Texas",
    county="Dallas County",
    city="Dallas",
    parent_slug="texas",
    academy_count=46,
    academy_count_verified=False,
    lineages_present=["Gracie Barra", "Alliance", "Renzo Gracie"],
    top_academies=[
        AcademyRef("Gracie Barra Dallas", city="Dallas", state="TX", lineage="Gracie Barra",
                   source="external_listing", verified=False),
    ],
)

LOS_ANGELES = LocationFacts(
    tier="city",
    name="Los Angeles",
    slug="los-angeles-ca",
    state="CA",
    state_slug="california",
    state_name="California",
    county="Los Angeles County",
    city="Los Angeles",
    parent_slug="california",
    academy_count=130,
    academy_count_verified=False,
    lineages_present=["Gracie Barra", "CheckMat", "10th Planet", "Atos"],
    top_academies=[
        AcademyRef("CheckMat HQ", city="Los Angeles", state="CA", lineage="CheckMat",
                   source="external_listing", verified=False),
        AcademyRef("10th Planet Los Angeles", city="Los Angeles", state="CA", lineage="10th Planet",
                   source="external_listing", verified=False),
    ],
)

# Ordered list the generator iterates over
ALL_SAMPLE_FACTS = [NATIONAL, TEXAS, CALIFORNIA, TRAVIS_COUNTY, AUSTIN, DALLAS, LOS_ANGELES]
