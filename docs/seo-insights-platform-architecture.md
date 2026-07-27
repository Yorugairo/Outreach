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
- evidence-backed AI Readiness (AEO, GEO, and AIO), reported separately from SEO

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
11. derive a versioned AI Readiness score from the same bounded crawl without claiming AI rankings or citations

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
- `AIReadinessOutput` — deterministic AEO/GEO/AIO, cohort, completeness, and evidence output
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

#### F. AI Readiness Service
Responsibilities:
- reuse the page records from the single, host-restricted crawl
- score AEO, GEO, and AIO with versioned deterministic checks
- report unknown and inapplicable checks separately from measured failures
- preserve core/supporting page cohorts and crawl completeness
- emit versioned AI JSON/Markdown (`ai-v2` current; `ai-v1` remains readable) independently of SEO reports
- treat external corroboration as optional paid evidence, never as a zero when unavailable

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
- SEO and AI Readiness headline scores
- AEO/GEO/AIO and core/supporting score views
- crawl completeness, broken links, and AI evidence limits
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
Commercially package validated run evidence into a short, human-reviewed expertise demonstration: what was observed, why it matters, and what the owner may want to investigate. The audit is the elevator pitch. Qualified conversations route to one of three delivery paths: improve the existing website, sitemap, and SEO while leveraging the owned vertical pSEO property; add vertical-specific plugins/embeds to the existing website; or onboard the business to a custom website with an optional CRM/SaaS bundle. The owned property is **One Trade Network** or **National BJJ Registry**; the program does not offer to construct a separate client pSEO system.

This phase is packaging and activation over the existing deterministic report; it does not change target-health scoring or permit unsupported claims. It also preserves the current v1 exclusions: no automated outbound, CRM platform, competitor intelligence module, or generative content production. Subscriptions are not a primary product assumption.

### Phase E — optional competitor enrichment

The Tacoma BJJ pilot implements this as a deterministic market-evidence child
run, not an LLM judge. An approved keyword version produces a bounded organic
and Maps sample, the operator approves one to three direct competitors, and
each approved host receives an independently scoped ten-page crawl, one
provider-specific backlink summary, and optional screenshots. A deep action
creates a new immutable market-run version rather than rewriting the pilot.

Market evidence produces `market-v1` and combined `v3` reports. It is an
explanatory and outreach layer only: it never changes the target SEO or AI
Readiness arithmetic, assigns no competitor health score, and emits no causal
claim without persisted comparative evidence.

### Phase F — action layer
content recommendations, sitemap rewrites, publishing workflows

---

## 13. Bottom-line architecture decision
Redesign the system as a **platform for SEO insight runs**, not as a loose collection of scripts.

The correct product statement is:

> Given a URL or normalized entity, produce a deterministic SEO intelligence package with sitemap, crawl, metadata, keyword, and ranking insights — persisted as a first-class platform object.

Everything else, including competitor research, should be secondary to that core loop.

### Market-evidence persistence boundary

- `KeywordSet` and `KeywordTarget` preserve source hash, Tacoma market/location,
  review state, category, intent, focus, and intended page usage.
- `KeywordSetBinding` attaches an approved version to a domain/prospect without
  mutating the shared research version.
- `MarketEvidenceRun` is tied to one InsightRun attempt and one keyword-set
  version. Provider costs, SERP/Maps snapshots, approved competitor identities,
  bounded pages, screenshots, gaps, and limitations live in this child record.
- Provider, competitor, and screenshot artifacts remain beneath the originating
  run. Target `PageRecord` data and target scoring never contain competitor
  pages.
- Pilot, competitor authority, deepening, and outreach export remain explicit
  operator actions.

### Demand-to-revenue persistence boundary

P9 adds four independently versioned aggregates beneath the commercial layer:

- `DemandEvidenceSet` stores source-hashed search-occasion rows and
  operator-reviewed close-variant/intent groups.
- `BusinessEconomicsProfile` stores price, capacity, retention, funnel values,
  and field-level provenance.
- `OpportunityScenario` stores `opportunity-formula.v1` assumptions, low/base/
  high outputs, capacity clamps, sensitivity, evidence references, and approval.
- `AcquisitionCalibrationRecord` stores aggregate period outcomes without lead
  identity or PII.

Demand/economics/calibration records are prospect-scoped and survive multiple
runs. Scenario and `opportunity-v1`/`v4` artifacts live beneath the originating
run so every forecast resolves to the exact SEO, AI, market, demand, and
economics versions used. Additive SQLite JSON payload tables mirror the
file-backed artifacts; legacy objects require no backfill.

Paid market operations use `provider-calls.v1`. Required-evidence
completeness—not call count—determines whether a market run is complete. A
`resume_unresolved` action creates a successor run, reuses successful
same-context evidence by reference, and schedules only eligible unresolved
work. Authentication and payment failures stop further paid operations.

The operator UI preserves one required launcher field: URL. `Build opportunity
case` is the primary post-run action; demand upload, economics, provider
recovery, calibration, and assumption review remain secondary tools. All
forecast surfaces retain the label `Forecast, not guarantee`.

### Product-strength score stack and immutable delivery

P10 replaces the client-facing use of the legacy mixed `overall_score` with
independent, versioned surfaces:

- `seo-health.v2`
- `search-visibility.v2`
- `local-visibility.v1`
- `ai-readiness.v3`
- `ai-visibility.v1`
- `conversion-readiness.v1`
- `evidence-confidence.v1`

The legacy score remains readable for compatibility. It is never averaged with
the new surfaces.

New client output is generated from a write-once `ReportSnapshot`, an optional
validated `AgenticAssessmentSnapshot`, and a content-addressed
`ClientReportBundle`. Mutable aliases such as `latest` point to immutable
snapshots rather than overwriting a report slot.

The agentic layer receives only a bounded, hashed `SiteEvidencePack` assembled
from persisted artifacts. Runtime calls, requested and served model routes,
tokens, cost, latency, raw response references, validation, and operator review
events remain independently attributable. The layer cannot recrawl, query
search providers, change deterministic scores, or render unsupported claims.
