# Sitemap & Internal-Linking Architecture — BJJ Registry pSEO

*Defeats the duplicate/thin-content penalty (see RESEARCH_BRIEF.md) via a coherent hub-and-spoke link graph + clean URL taxonomy.*

## 1. URL taxonomy

Deterministic, readable, no query strings:

```
/                                  -> national hub (or marketing home)
/national                          -> National BJJ Registry overview
/{state}                           -> state page           e.g. /texas
/{state}/{county}                  -> county page          e.g. /texas/travis-county-tx
/{state}/{city}                    -> city page            e.g. /texas/austin-tx
/{state}/{city}/{academy-slug}     -> academy page (Phase 2, SleekRank pattern)
```

Slug rules:
- state → lowercase, spaces to hyphens: `Texas` → `texas`
- city  → `city-state`: `Austin, TX` → `austin-tx`
- county→ `county-state`: `Travis County, TX` → `travis-county-tx`

## 2. Hub-and-spoke link graph

Every page links **up** (breadcrumb + parent) and **down/out** (children). This tells
Google the pages are part of one coherent registry, not orphan clones.

| Page | Links up to | Links down/out to |
|---|---|---|
| national | (root) | all states |
| state | national | its counties (or top cities if no county tier) |
| county | state | its cities |
| city | county (or state) | academy pages (Phase 2) |

The generator emits the breadcrumb + "Explore further" child links automatically from
`LocationFacts.parent_slug` / `child_slugs`.

## 3. Canonical & dedupe discipline

- Each page has ONE canonical URL (above). If the same academy is reachable via multiple
  paths, pick the canonical and `rel=canonical` the rest.
- No two pages share identical body text — tiers use distinct section sets (see article_template.py).
- If a city has <3 academies and thin content risk is high, MERGE into the county page and
  301-redirect the city URL. Better one strong page than ten weak ones.

## 4. Sitemap.xml (generated artifact)

Maintain `sitemap.xml` at the blog root listing every location URL with `<lastmod>`.
Regenerate on each content publish. Example:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://blog.nationalbjjregistry.com/national</loc></url>
  <url><loc>https://blog.nationalbjjregistry.com/texas</loc></url>
  <url><loc>https://blog.nationalbjjregistry.com/texas/travis-county-tx</loc></url>
  <url><loc>https://blog.nationalbjjregistry.com/texas/austin-tx</loc></url>
</urlset>
```

## 5. JSON-LD

Every article emits `Article` + `BreadcrumbList` JSON-LD (see `build_article` return).
Add `LocalBusiness`/`SportsActivityLocation` JSON-LD on academy pages in Phase 2.

## 6. Publishing guardrails

- Never publish a page where `verified=False` on academy counts or named academies.
- Run the generator, spot-check 1 page per tier, confirm internal links resolve.
- Submit `sitemap.xml` to Search Console; monitor index coverage for "Duplicate, submitted URL not selected."
