# BJJ Registry — Programmatic SEO Research Brief

*Prepared for the National BJJ Registry pSEO content system. Evidence-first; every external claim below is sourced so operators can verify before publishing.*

## 1. Why programmatic SEO fits a registry

A registry is, by definition, a structured dataset: academies, locations, lineages, instructors, events. That dataset is the **deterministic fact layer** that makes programmatic SEO safe (per the `programmatic-growth-pipelines` skill: *deterministic before generative*). Each location page is generated from real registry facts, not spun text — which defeats the thin/duplicate-content penalty that kills most pSEO.

## 2. The thin-content trap (what to avoid)

Sources agree the #1 failure mode is templated pages that say the same thing with only the city name swapped:

- **Scopic Studios** — duplicate/thin programmatic pages get filtered; need unique value per template.
- **Hashmeta** — when generating hundreds/thousands of pages, duplicate content becomes the dominant risk; prevent via intent mapping + canonical + internal links.
- **MeshLine** — avoid duplicate pages by mapping intent, tightening templates, using canonical and internal-link discipline.
- **Palosanto (2025)** — "Programmatic SEO: from templates to systems." Quality wins; use structured data + templates as systems, not mail-merge.

**Our defense:**
1. Distinct section set + angle per tier (national / state / county / city).
2. Every page injects location-specific *facts* (counts, named academies, lineages, events) from the registry.
3. Strict parent↔child internal linking (see `SITEMAP_AND_LINKING.md`) so Google sees a coherent hub, not orphan clones.
4. JSON-LD `Article` + `BreadcrumbList` structured data on every page.

## 3. BJJ keyword + intent patterns (verified)

From Gymdesk, Cited, Wodify, Moonrank:

- **Title-tag formula** (Cited / Gymdesk): `[Discipline] Classes in City, State | [Brand]` → we adapt to `[City] Brazilian Jiu-Jitsu Academies & Classes | National BJJ Registry`.
- **High-intent local phrases**: "Brazilian Jiu Jitsu classes in [City, State]", "[City] BJJ gym", "jiu jitsu near me", "beginner jiu jitsu classes", "martial arts classes near me", "no-gi [City]".
- **Local pack matters**: Google Business Profile + reviews drive the map pack; registry pages should link out to / cite GBP-backed academies.
- **Program/service depth**: pages that explain programs (kids, adults, no-gi, competition) rank better than bare listings.

## 4. Directory/registry models that rank (competitive intel)

- **IBJJF** — "Registered Academies" is a real national registry model (affiliation + location).
- **BJJ Checkpoint** — gym directory + marketplace; "find a place to train anywhere in the world."
- **SleekRank (2026)** — explicit playbook: *"page per academy, lineage, and city."* This is the exact structure we adopt, extended to state/county tiers.
- **Gold BJJ / LetsRollBJJ / BJJ Bundle** — city-level listicles ("Best 10 BJJ in Austin TX") with named gyms, instructors, lineages. These rank because they're specific.

**Implication:** our city pages must name *real* academies from registry data (with provenance), not generic "there are many gyms here" filler.

## 5. Tiered content strategy

| Tier | Primary intent | Unique angle | Internal-link role |
|---|---|---|---|
| **National** | "BJJ academies in the US" / registry overview | Methodology, nationwide counts, regional distribution, lineage map | Hub → links to all states |
| **State** | "{State} BJJ academies" | State density, top cities, state championships, lineages present | Child of national, parent of counties |
| **County** | "BJJ in {County}, {State}" | Sub-region clustering, which cities dominate, local community/open-mats | Child of state, parent of cities |
| **City** | "{City} BJJ gym" / "near me" | Named gyms, gi vs no-gi, where to start, first-class expectations | Child of county/state, leaf (links to academy pages) |

## 6. Guardrails (do NOT fabricate)

The skill is explicit: *never fabricate prices, customer counts, certifications, or rankings.* Therefore:

- Every numeric fact (academy count, event date, lineage) carries a `source` + `verified` flag in `location_facts.py`.
- Sample data is **illustrative** and flagged `verified: false`; operators MUST replace with registry-DB values before publishing.
- Named academies in samples come from public listings (Yelp/Gold BJJ) and are marked `source: external_listing` — confirm against the registry before going live.

## 7. Recommended build order

1. Populate `LocationFacts` from the registry DB (national rollup → states → counties → cities).
2. Generate tier pages via `generate.py`.
3. Wire internal links (parent/child) + submit sitemap.
4. Add academy-level pages (SleekRank pattern) as a Phase 2 once location tiers rank.

See `README.md` for the generator workflow and `SITEMAP_AND_LINKING.md` for URL + linking architecture.
