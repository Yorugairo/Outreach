"""LocationFacts: the deterministic fact layer for BJJ Registry pSEO pages.

Every field that feeds a generated article carries provenance so operators
can verify before publishing. Never fabricate — leave `verified=False` and
populate from the registry database.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AcademyRef:
    """A single academy referenced on a location page."""
    name: str
    city: Optional[str] = None
    state: Optional[str] = None
    lineage: Optional[str] = None          # e.g. "Gracie Barra", "Atos"
    note: Optional[str] = None             # one-line differentiator
    source: str = "registry"              # registry | external_listing | operator
    verified: bool = False


@dataclass
class LocationFacts:
    """Facts for one location page (national / state / county / city).

    `tier` controls which template + angle the generator uses.
    `parent_slug` / `child_slugs` drive internal linking (see SITEMAP_AND_LINKING.md).
    """
    tier: str                                   # national | state | county | city
    name: str                                   # display name, e.g. "Texas" or "Austin"
    slug: str                                   # url segment, e.g. "texas" or "austin-tx"
    state: Optional[str] = None
    state_slug: Optional[str] = None        # slug of the parent state page (for breadcrumb)
    state_name: Optional[str] = None        # full state name for breadcrumb label (e.g. "Texas")
    county: Optional[str] = None
    city: Optional[str] = None

    parent_slug: Optional[str] = None           # breadcrumb + internal link target
    child_slugs: list[str] = field(default_factory=list)

    academy_count: Optional[int] = None
    academy_count_source: str = "registry"
    academy_count_verified: bool = False

    top_cities: list[str] = field(default_factory=list)        # for state/county tiers
    top_academies: list[AcademyRef] = field(default_factory=list)
    lineages_present: list[str] = field(default_factory=list)  # e.g. ["Gracie Barra", "Atos"]
    events: list[str] = field(default_factory=list)            # notable comps/camps
    notable_facts: list[str] = field(default_factory=list)     # free-text, sourced bullets

    # Insight layer (drives the "Market Insights" section). Sourced from
    # registry_region_score_aggregates_v1 — never fabricated.
    insights: dict = field(default_factory=dict)  # e.g. {
    #   "avg_registry_score": 71.4, "median_registry_score": 70.0,
    #   "top_5_avg_registry_score": 78.1, "pct_70_plus": 18.2,
    #   "pct_85_plus": 4.0, "sample_size": 58,
    #   "national_avg": 65.0, "state_avg": 68.0 }  # parent/national baselines
    insights_source: str = ""  # which read-model produced it (provenance)
    insights_verified: bool = False

    intro_hook: Optional[str] = None            # optional operator override for the lede
    sources: dict[str, str] = field(default_factory=dict)  # field -> where it came from

    def title_tag(self, brand: str = "National BJJ Registry") -> str:
        if self.tier == "national":
            return f"Brazilian Jiu-Jitsu Academies in the USA | {brand}"
        if self.tier == "state":
            return f"{self.name} Brazilian Jiu-Jitsu Academies & Classes | {brand}"
        if self.tier == "county":
            return f"BJJ in {self.name}, {self.state} | {brand}"
        return f"Brazilian Jiu-Jitsu in {self.name}, {self.state} | {brand}"

    def meta_description(self) -> str:
        loc = self.name if self.tier == "national" else f"{self.name}, {self.state or ''}".strip()
        if self.academy_count and self.academy_count_verified:
            cnt = f"{self.academy_count} academies"
        else:
            cnt = "academies"
        base = {
            "national": f"Explore {cnt} across the United States in the National BJJ Registry — lineages, affiliations, and where to train.",
            "state": f"Find {cnt} in {loc}. Lineages, top cities, competitions, and a beginner's path to the mats.",
            "county": f"Discover BJJ training hubs across {loc}. Which cities lead, local academies, and community open mats.",
            "city": f"Where to start Brazilian Jiu-Jitsu in {loc}. Named academies, gi vs no-gi, and your first class.",
        }
        return base.get(self.tier, f"BJJ in {loc}.")

    def breadcrumb(self) -> list[tuple[str, str]]:
        """Returns (label, slug) pairs from root to this page."""
        crumbs = [("National BJJ Registry", "national")]
        if self.tier in ("state", "county", "city") and self.state:
            state_slug = self.state_slug or self.state.lower().replace(" ", "-")
            state_label = self.state_name or self.name if self.tier == "state" else (self.state_name or self.state)
            crumbs.append((state_label, state_slug))
        if self.tier == "city" and self.county:
            county_slug = self.county.lower().replace(" ", "-") + "-" + (self.state or "").lower().replace(" ", "-")
            crumbs.append((self.county, county_slug))
        crumbs.append((self.name, self.slug))
        return crumbs
