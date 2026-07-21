"""TechniqueFacts: deterministic fact layer for technique-video pSEO pages.

Mirrors location_facts.py conventions (plain dataclass, provenance on every field,
never fabricate). The transcript is the PRIMARY fact source — same role the
`academies` table plays for location pages. Rendered steps must trace to it.

NOTE: academy attribution ("where to train this") is intentionally NOT part of this
model. It was removed because it cannot be derived from the corpus alone without
asserting provenance we don't have. It stays out until a real join to the registry
exists (publisher match / curriculum table / signed-off lineage map).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TechniqueRef:
    """A related technique, referenced for internal linking / "related" sections."""
    name: str
    slug: str
    position: Optional[str] = None
    belt: Optional[str] = None
    source: str = "corpus"
    verified: bool = False


@dataclass
class TechniqueFacts:
    """Facts for one technique page (axis 2), seeded by a corpus video + metadata."""
    name: str                                   # "Armbar from Guard"
    slug: str                                   # "armbar-from-guard"
    position: Optional[str] = None              # "guard", "mount", "side control"
    belt: Optional[str] = None                  # "white", "blue", "all levels"
    category: Optional[str] = None              # "submission", "sweep", "escape", "takedown"
    summary: Optional[str] = None               # short description (from metadata/transcript head)

    transcript: Optional[str] = None            # full transcript — the fact source
    transcript_source: str = "corpus"           # corpus | youtube | operator
    transcript_verified: bool = False

    # Extracted/expanded from the transcript. Each step must trace to the transcript.
    steps: list[str] = field(default_factory=list)
    common_errors: list[str] = field(default_factory=list)
    key_terms: list[str] = field(default_factory=list)

    related_techniques: list[TechniqueRef] = field(default_factory=list)

    sources: dict[str, str] = field(default_factory=dict)

    # ---- SEO helpers ----
    def title_tag(self, brand: str = "National BJJ Registry") -> str:
        head = f"How to {self.name}"
        if self.position and self.position.lower() not in self.name.lower():
            head += f" from {self.position.title()}"
        if self.belt and self.belt != "all levels":
            head += f" | {self.belt.title()} Belt BJJ"
        return f"{head} | {brand}"

    def meta_description(self) -> str:
        base = f"Learn {self.name.lower()}"
        if self.transcript_verified:
            base += " with a step-by-step breakdown from a full instructional transcript"
        base += "."
        return base

    def breadcrumb(self) -> list[tuple[str, str]]:
        crumbs = [("Techniques", "techniques")]
        if self.position:
            crumbs.append((self.position.title(), f"techniques/{self.position}"))
        crumbs.append((self.name, self.slug))
        return crumbs

    def to_dict(self) -> dict:
        return {
            "name": self.name, "slug": self.slug, "position": self.position,
            "belt": self.belt, "category": self.category, "summary": self.summary,
            "transcript_verified": self.transcript_verified,
            "steps": self.steps, "common_errors": self.common_errors,
            "key_terms": self.key_terms,
            "related": [{"name": r.name, "slug": r.slug} for r in self.related_techniques],
        }
