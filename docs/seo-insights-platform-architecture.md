# SEO Insights Platform Architecture

Prepared: 2026-07-07
Workspace: `C:\Users\Snipe\Downloads\Outreach Program`

## Product goal
Build a consistent platform where an operator can point the system at a URL/domain and receive a normalized, repeatable SEO intelligence package focused on:
- sitemap discovery and quality
- current-page metadata and structural SEO
- indexability / crawlability signals
- keyword opportunity mapping
- Google ranking / SERP visibility snapshots
- page coverage gaps
- recommended sitemap/page actions

Competitor research is **not** the primary product surface in v1. It is a downstream enrichment that can be run later by an LLM or analyst using the already-collected SEO evidence.

## Product thesis
The core product is not "scripts that fetch pages." The core product is a **URL -> SEO intelligence report engine** with a stable data model, deterministic pipeline, repeatable scoring, and operator-facing surfaces.

That means:
- scripts/workers are implementation details
- the enduring design should be a platform with services, jobs, DB records, artifacts, and UI/API surfaces
- every run should produce the same object model regardless of whether triggered from UI, API, cron, or CLI

---

## 1. Product boundary

### In scope for v1
Given a URL/domain, the platform should:
1. normalize the domain
2. discover robots and sitemap inventory
3. crawl or fetch key pages
4. extract title/meta/H1/canonical/schema/internal-link/image evidence
5. classify pages by search role
6. score only evidence-backed dimensions and report unknown/completeness separately
7. collect keyword seeds + SERP snapshots via DataForSEO
8. generate a prioritized SEO insight package
9. persist all raw and normalized evidence
10. expose the results in a consistent operator-facing format

### Explicitly out of scope for v1
- competitor intelligence as a platform module
- automated outbound or follow-up delivery
- generative content production or publishing
- CRM/contact-pipeline workflowing
- video/creative upsells

Later modules may consume validated `InsightReport` evidence, but none of these capabilities may weaken or block the v1 SEO insight engine.

---

## 2. User-facing product model

### Primary workflow
**Input:** operator pastes a domain or URL

**System output:** one `SEO Insight Run`

Each run should yield:
- run status + timings
- discovered sitemap set
- crawl inventory summary
- page class distribution
- metadata coverage summary
- sitemap hygiene summary
- keyword cluster summary
- SERP/ranking snapshot summary
- recommended page backlog
- recommended sitemap include/exclude actions
- downloadable JSON/markdown artifacts

### Operator expectations
The operator should not have to think in terms of scripts. They should think in terms of:
- target
- run
- evidence
- score
- recommendations
- export

---

## 3. Platform architecture

### 3.1 Core domain objects
- `Target` — canonical business/site target
- `InsightRun` — one execution against a target
- `DiscoveredAsset` — robots, sitemap files, pages, images
- `PageRecord` — normalized page object
- `PageEvidence` — extracted page-level facts with provenance
- `KeywordCluster` — grouped search intents
- `SerpSnapshot` — rank and SERP result evidence
- `CoverageScorecard` — deterministic score output
- `SitemapRecommendation` — include/exclude + child sitemap structure
- `InsightReport` — operator-ready result bundle

### 3.2 Service boundaries
The platform should be split into five product services:

#### A. Target Intake Service
Responsibilities:
- normalize domain/URL
- create/update canonical target records
- validate scope
- enqueue insight runs

#### B. Crawl Discovery Service
Responsibilities:
- fetch robots.txt
- discover sitemap.xml and child sitemaps
- fetch pages
- store raw fetch artifacts
- emit normalized page records

#### C. SEO Analysis Service
Responsibilities:
- parse metadata/H1/canonical/schema
- classify pages
- score primary-requested-page metadata quality without allowing `max_pages` to change target health
- score crawl/indexability signals
- score sitemap quality only from conclusive persisted evidence
- produce page-coverage model
- emit sampled secondary-page facts as findings rather than target-level score inputs

#### D. Search Intelligence Service
Responsibilities:
- call DataForSEO
- generate keyword seeds
- pull SERP snapshots
- attach search volume / rank evidence
- maintain raw + normalized search artifacts
- bind accepted evidence to the run target, snapshot date, market/location, language, device, source, and observed target ranking URLs
- report missing or mismatched context as unknown rather than scoring it

#### E. Reporting Service
Responsibilities:
- assemble final scorecard
- generate deterministic `prospect_issue` recommendations from independently persisted evidence
- separate unrouted `evidence_limit` records into an operator-review section
- export JSON/markdown
- provide report-friendly objects to UI/API

### 3.3 Infrastructure layer
- Postgres/Supabase for state
- object/artifact storage for raw payloads
- background job queue for runs and stages
- API layer for starting runs and fetching results
- Next.js/Vercel operator app for UI

---

## 4. Recommended UI modules

### 4.1 Run Launcher
Minimal form:
- URL/domain
- optional market/location
- optional device type
- optional depth level (`quick`, `standard`, `full`)

### 4.2 Run Detail View
Sections:
- overview/status
- discovered sitemaps
- crawl inventory
- metadata coverage
- page classification matrix
- keyword clusters
- SERP snapshots
- recommendation backlog
- export panel

### 4.3 Page Explorer
For each page:
- URL
- class
- title/meta/H1/canonical
- indexability flags
- schema types
- internal links count
- image count
- evidence snippets

### 4.4 Sitemap Workbench
Show:
- discovered sitemaps
- included URLs
- excluded URLs
- missing key URLs
- low-value URLs that should be removed
- recommended child sitemap grouping

### 4.5 Insight Summary / Scorecard
Top-level answer for the operator:
- overall SEO health score
- sitemap quality score
- crawl/indexability issues
- coverage gaps
- search opportunity summary
- next 5 highest-value actions

---

## 5. Run lifecycle

A platform run should move through these states:
1. `queued`
2. `normalizing_target`
3. `discovering_sitemaps`
4. `fetching_pages`
5. `extracting_page_evidence`
6. `classifying_pages`
7. `pulling_search_intelligence`
8. `scoring`
9. `assembling_report`
10. `completed` or `failed`

This should be modeled in DB, not implied by script logs.

---

## 6. Deterministic scoring surfaces

### 6.1 Sitemap quality
Score components:
- discovered sitemap presence
- valid child sitemap structure
- canonical/indexable URL coverage
- thin/utility URL exclusion
- class-aware inclusion (services, locations, service-location pages, projects, blogs)

### 6.2 Metadata quality
Per indexable page:
- title present
- meta description present
- H1 present
- title length sanity
- title includes service/geo relevance where appropriate
- canonical sanity

### 6.3 Page coverage quality
Measure:
- service page coverage
- location page coverage
- service x geography coverage
- supporting-content coverage
- orphan/weak page surface

### 6.4 Search visibility surface
Measure:
- keyword cluster count
- mapped cluster count
- observed ranking presence
- unmapped high-intent query opportunities

---

## 7. Why competitor research moves later
Competitor analysis is useful, but it is not the irreducible core.

The irreducible core is:
- understanding the target site
- understanding its crawl/index/map state
- understanding its query/page coverage
- understanding its ranking evidence

Once those are collected, a competitor module is much easier to add later because the evidence model is already there.

In practice, this means:
- do not add competitor snapshots or research workflows to the v1 runtime/data contract
- do not make competitor research block the platform architecture
- after v1, an optional analyst layer may consume the existing insight report without changing target evidence or scoring

---

## 8. Data architecture fit
This platform fits directly with a broader normalized data architecture.

Your existing data/normalization work should remain upstream and authoritative for:
- entity resolution
- category/taxonomy mapping
- geography normalization
- ownership / provenance

The SEO insights platform becomes a specialized product surface on top of that normalized foundation.

The important design rule is:
**the platform should consume normalized entities, but it should also be runnable against a standalone URL when entity context is missing.**

That means two intake modes:
- `entity-backed run`
- `ad hoc URL run`

---

## 9. Recommended API surface

### Create run
`POST /api/seo-insights/runs`

Payload:
```json
{
  "url": "https://example.com",
  "location_code": 2840,
  "language_code": "en",
  "mode": "standard"
}
```

### Get run status
`GET /api/seo-insights/runs/:runId`

### Get report bundle
`GET /api/seo-insights/runs/:runId/report`

### Get page inventory
`GET /api/seo-insights/runs/:runId/pages`

### Get sitemap recommendations
`GET /api/seo-insights/runs/:runId/sitemap`

### Export artifacts
`GET /api/seo-insights/runs/:runId/export?format=json|md`

---

## 10. Recommended implementation shape
Do not think of the worker entrypoints as the product. Think of them as adapters around platform services.

### Good shape
- reusable Python or TS service modules in `src/`
- job handlers that call those modules
- API endpoints that create runs and read results
- UI pages that display persisted run objects

### Avoid
- logic living only in one-off scripts
- scores computed only in terminal output
- artifacts existing only on disk without DB linkage
- pipeline stages with no run-state tracking

---

## 11. Productized MVP
The MVP should still be small, but platform-shaped.

### MVP capability
Paste one URL -> get one persisted SEO insight report.

### MVP includes
- run creation
- run state tracking
- sitemap discovery
- page fetch + evidence extraction
- page classification
- keyword seed pull via DataForSEO
- SERP snapshot pull
- coverage + sitemap scorecards
- report assembly
- JSON/markdown export

### MVP excludes
- multi-tenant permissions sophistication
- deep competitor intelligence
- automated content publishing
- complex collaboration workflows

---

## 12. Product roadmap

### Phase A — SEO insight engine
URL -> persisted run -> scorecard/report

### Phase B — operator app
UI for runs, evidence, and recommendations

### Phase C — entity-integrated mode
attach runs to canonical businesses and normalized categories

### Phase D — outreach activation
Commercially package validated run evidence into a human-reviewed outreach asset that answers: what is wrong, why it matters, and what we would fix. Route supported opportunities into **web development / rebuild**, **profile management / reputation**, and **pSEO / search architecture** service offers, then support operator-led movement from outreach to booked call and proposal.

This phase is packaging and activation over the existing deterministic report; it does not change target-health scoring or permit unsupported claims. It also preserves the current v1 exclusions: no automated outbound, CRM platform, competitor intelligence module, or generative content production. Subscriptions are not a primary product assumption.

### Phase E — optional competitor enrichment
LLM/analyst layer driven by the existing insight report

### Phase F — action layer
content recommendations, sitemap rewrites, publishing workflows

---

## 13. Bottom-line architecture decision
Redesign the system as a **platform for SEO insight runs**, not as a loose collection of scripts.

The correct product statement is:

> Given a URL or normalized entity, produce a deterministic SEO intelligence package with sitemap, crawl, metadata, keyword, and ranking insights — persisted as a first-class platform object.

Everything else, including competitor research, should be secondary to that core loop.
