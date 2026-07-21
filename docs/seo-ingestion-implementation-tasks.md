# SEO Ingestion Implementation Tasks

Prepared: 2026-07-06

## Phase 1 — Foundation
1. Create DB migration from `db/seo_ingestion_schema.sql`.
2. Add `src/config.py` or TS equivalent for env loading.
3. Build `src/dataforseo_client.py` with basic auth, retry, and JSON persistence.
4. Add `src/fetchers/sitemap_fetcher.py` for `robots.txt` and `sitemap.xml` discovery.
5. Add `src/fetchers/page_fetcher.py` for HTML fetch and metadata extraction.

## Phase 2 — Single-domain ingestion
6. Build `scripts/ingest_domain.py`:
   - input domain
   - discover sitemap
   - collect seed URLs
   - fetch pages
   - store `crawl_pages`
7. Build `scripts/classify_pages.py`:
   - assign page classes
   - flag thin/utility/duplicate candidates
8. Build `scripts/score_site_coverage.py`:
   - service count
   - geo count
   - service x geo coverage
   - sitemap hygiene score

## Phase 3 — Search intelligence
9. Build `scripts/pull_keyword_seeds.py` using DataForSEO.
10. Build `scripts/pull_serp_snapshots.py` for top keyword clusters by location/device.
11. Build `scripts/build_competitor_gap_report.py`.

## Phase 4 — Recommendation engine
12. Build `scripts/generate_page_recommendations.py`.
13. Build `scripts/generate_sitemap_recommendation.py`.
14. Build `scripts/generate_audit_summary.py`.

## Phase 5 — Output artifacts
15. Write machine-readable output files per domain:
   - `artifacts/<domain>/crawl-summary.json`
   - `artifacts/<domain>/keyword-clusters.json`
   - `artifacts/<domain>/competitor-gap.json`
   - `artifacts/<domain>/sitemap-recommendation.json`
   - `artifacts/<domain>/audit-summary.md`

## Initial page classification heuristics
- homepage: root URL
- service: `/services/`, service keywords, commercial terms
- location: city/state slug, `areas-served`, `locations`
- service_location: service term + geo term both present
- project_case_study: `projects`, `portfolio`, `case-study`
- blog_resource: `blog`, `resources`, `guides`, `faq`
- legal_utility: `privacy`, `terms`, `404`, `feed`, `tag`
- low_value: thin content, duplicate title/H1, utility-like structure

## MVP scoring formulas
### Coverage score
- service_page_count * 2
- location_page_count * 1.5
- service_location_page_count * 3
- project_case_study_count * 1
- blog_resource_count * 0.5
- minus duplicate_or_low_value_count * 2

### Metadata quality score
Per indexable page:
- +1 title present
- +1 meta present
- +1 h1 present
- +1 title length reasonable
- +1 title includes service or geo signal

### Sitemap hygiene score
- included_indexable_urls / candidate_indexable_urls
- penalty for utility/thin URLs included
- penalty for missing key page classes

## Recommended first real build sequence
1. schema migration
2. DataForSEO client
3. sitemap discovery/fetch
4. page fetch + metadata parser
5. single-domain ingest script
6. page classifier
7. first coverage scorer
8. keyword seed pull
9. first SERP snapshot pull
10. sitemap recommendation artifact

## Suggested first test case
Use one controlled domain first, such as a known prospect case, and verify:
- sitemap discovery works
- pages persist correctly
- classification is mostly sane
- keyword seeds store correctly
- first coverage score is human-readable

## Success criteria for MVP
- ingest one domain end-to-end in under 5 minutes
- produce at least one useful sitemap recommendation
- identify at least 5 keyword/page gaps
- store raw and normalized DataForSEO evidence
- avoid fabricating facts or pages without evidence
