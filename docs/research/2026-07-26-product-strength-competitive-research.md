# Outreach Program: Product-Strength and Competitive Research

Generated: 2026-07-26  
Scope: scoring, evidence sources, client-facing output, durability, and competitive differentiation  
Confidence: high for the repository assessment and documented competitor capabilities; medium for expected conversion impact until pilot outcomes exist

## Executive conclusion

The Outreach Program is already stronger than a generic audit generator in its
most important trust mechanism: it preserves target evidence, separates
technical facts from commercial framing, treats missing evidence as unknown,
and maintains versioned market and opportunity records.

Its weakest element is the legacy **SEO overall score**. The number presents
more certainty and breadth than the formula currently contains. The next
product-strength milestone should not add more labels to that score. It should:

1. replace it with a real site-wide Technical SEO Health contract;
2. keep rankings, local visibility, AI readiness, observed AI visibility, and
   conversion readiness as separate measures;
3. add geographically distributed Maps evidence and time-series comparison;
4. generate every client report from an immutable report snapshot rather than
   hand-authoring a presentation;
5. offer owner-authorized measurement connectors after the prospect engages.

The product should be positioned as:

> A vertical-specific search opportunity brief that proves what is happening,
> shows the next three commercially relevant moves, and can later measure
> whether those moves produced visibility, trials, and revenue.

## 1. Current product assessment

### What is already unusually strong

- Evidence references resolve to persisted values rather than report
  self-claims.
- Missing enrichment is unknown, not a zero or sales claim.
- AI Readiness is explicitly separated from actual AI citation or ranking.
- Competitor evidence does not alter the target's SEO or AI scores.
- Demand evidence, economics, scenarios, corrections, and market recoveries
  use immutable predecessor/successor records.
- Revenue is kept downstream from rankings and capped by reviewed business
  capacity.
- The three actual service paths are encoded separately from technical
  findings.

These are meaningful advantages over fast lead-generation audits, which
emphasize instant scoring and white-label output. SEOptimer, for example,
advertises bulk prospect audits, CRM integration, configurable checks, and
white-label reports; WooRank similarly emphasizes instant reviews, lead
generation, and customizable reports. Their documented product strength is
scale and sales convenience, not the field-level evidence provenance used
here. [SEOptimer SEO API](https://www.seoptimer.com/seo-api/),
[WooRank for SEO agencies](https://www.woorank.com/en/solutions/seo-agencies).

### Where the current headline SEO score is weak

The implementation in
[`src/services/reporting_service.py`](../../src/services/reporting_service.py)
currently averages the known values among four dimensions:

- sitemap quality;
- metadata quality;
- page coverage;
- search visibility.

The sitemap heuristic rewards sitemap count, the metadata result is a binary
check of the primary page, page coverage is intentionally unknown, and search
visibility is optional. This creates four product problems:

1. **The score mixes health and performance.** A crawl/index problem and an
   observed ranking are different concepts.
2. **The site-wide presentation is not site-wide arithmetic.** The report can
   correctly find metadata problems across nine pages while the score's
   metadata dimension only evaluates the primary page.
3. **Evidence can change the denominator.** Adding measured search data can
   lower or raise the score because unknown dimensions are excluded and known
   ones are reweighted.
4. **Important families are absent.** Canonicals, redirects, internal
   architecture, duplicate content, performance, mobile experience, rendered
   content, structured data, and site-wide indexability do not materially
   influence the SEO headline.

This is well behind established technical-audit scoring breadth. Semrush
documents more than 140 checks and weights errors more heavily than warnings;
Ahrefs documents more than 170 predefined checks and calculates Health Score
from the proportion of crawled internal URLs without error-level issues.
[Semrush Site Health](https://www.semrush.com/kb/114-total-score),
[Ahrefs Health Score](https://help.ahrefs.com/en/articles/1424673-what-is-health-score-and-how-is-it-calculated-in-ahrefs-site-audit).

### Where the current AI score is strong

The implementation in
[`src/services/ai_readiness_service.py`](../../src/services/ai_readiness_service.py)
has several sound choices:

- versioned 40% AEO / 35% GEO / 25% AIO arithmetic;
- core and supporting cohorts;
- explicit unknown and inapplicable states;
- evidence completeness separate from score;
- no automatic FAQPage or HowTo boost;
- no claim that readiness proves citations;
- page-level evidence references.

This aligns with Google's position that existing SEO fundamentals remain
relevant to AI features and that there is no special AI schema, markup, or
machine-readable file required for inclusion.
[Google: AI features and your website](https://developers.google.com/search/docs/appearance/ai-features).

### Where the current AI score needs strengthening

Many checks are binary page ratios:

- any direct-answer block passes a page;
- any structured block passes a page;
- two question headings pass follow-up coverage;
- 100 words passes text accessibility;
- any aligned valid JSON-LD passes structured-data alignment;
- four corroborating results can max external corroboration.

That is deterministic, but not sufficiently discriminating. It measures the
presence of recognizable patterns more than their coverage, specificity, or
fit with the page's purpose. A contact page, service page, and research article
should not be evaluated with identical answer expectations.

The `customer_claim_eligible` flag is also based on completeness alone.
Complete evidence proves that checks ran; it does not prove the formula is
empirically calibrated.

## 2. Recommended score architecture

Do not create one universal score. Use a small score stack with unambiguous
semantics.

| Measure | Customer question | Source | Should rankings affect it? |
| --- | --- | --- | --- |
| Technical SEO Health | Can search systems reliably crawl, index, and understand the site? | Crawl, rendered pages, performance | No |
| Search Visibility | Is the domain currently visible for reviewed demand? | Organic SERPs and later Search Console | Yes |
| Local Visibility | Where does the business appear across its actual service area? | Maps grid and later GBP | Yes |
| AI Readiness | Is the site technically and editorially ready to be extracted and cited? | Crawl and corroboration | No |
| Observed AI Visibility | Is the brand actually mentioned or cited in reviewed AI responses? | LLM responses/mentions and owner tools | Yes |
| Conversion Readiness | Can a qualified visitor find the right program and complete the next action? | DOM, forms, schedule, signup flow | No |
| Evidence Confidence | How much of the intended evidence contract was successfully observed? | Collection ledger | No |

### Technical SEO Health v2

Start with a transparent issue-density formula:

```text
check penalty =
  severity weight
  × affected applicable page ratio
  × page-importance multiplier
  × evidence confidence

family score = 100 - normalized capped penalties
site score = weighted mean of applicable family scores
```

Recommended initial families:

- Crawl and index eligibility: 30%
- On-page/template quality: 20%
- Architecture and internal links: 20%
- Structured/local entity data: 15%
- Mobile performance and page experience: 15%

Each check should declare:

- stable check ID and formula version;
- family and severity;
- applicable page classes;
- page-level result and evidence reference;
- affected-page ratio;
- confidence and evidence limits;
- remediation mapping;
- whether it is score-affecting or informational.

Keep Search Visibility outside this score. Semrush and Ahrefs use different
health formulas, but both treat health as a crawl/issue construct rather than
an average containing rankings.

### AI Readiness v3

Retain the current customer-facing formula until calibration data justifies
changing it, but improve the checks:

- Score direct-answer **coverage of answerable sections**, not the existence of
  one answer.
- Score heading violations and orphaned sections continuously.
- Require structured blocks to be semantically useful: table headers, list
  context, definition pairs, and visible labels.
- Match conversational follow-ups to approved demand intents rather than
  counting question marks.
- Test entity consistency across visible name/address/phone, page metadata,
  schema, and approved business data.
- Evaluate author and credential evidence only where a reader would reasonably
  expect authorship.
- Distinguish first-party proof, external citations, and unsubstantiated
  claims.
- Deduplicate external corroboration by domain and record topical relevance;
  never infer authority from mere presence.
- Replace the 100-word accessibility proxy with HTTP-versus-rendered content
  parity, main-content extraction, and meaningful-text coverage.
- Make check applicability page-class specific.

Do **not** add an `llms.txt` score simply because competitors do. Semrush now
includes it in AI Search Health, but Google explicitly states that new AI text
files and special markup are not required or used for Google Search's
generative capabilities.
[Semrush AI Search Health](https://www.semrush.com/kb/1601-ai-search-health-audit),
[Google generative AI optimization guide](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide).

### Observed AI Visibility

Add this as a separate optional evidence layer:

- mention rate;
- citation rate;
- distinct cited pages;
- share of voice against approved competitors;
- prompt/topic coverage;
- platform, locale, date, and raw response reference.

Ahrefs and Semrush distinguish technical AI readiness from observed brand
visibility. Ahrefs reports mentions, citations, estimated impressions, and AI
share of voice; its methodology also acknowledges that prompt coverage is
modeled and does not represent actual audience reach.
[Ahrefs AI visibility metrics](https://help.ahrefs.com/en/articles/15501968-ai-visibility-metrics),
[Ahrefs Brand Radar methodology](https://ahrefs.com/blog/brand-radar-methodology/),
[Semrush AI Visibility Toolkit](https://www.semrush.com/kb/1493-ai-visibility-toolkit).

DataForSEO now exposes LLM mention, source, citation, and multi-target
comparison data. This is the most natural cold-prospect experiment because the
existing provider and cost ledger can contain it. Treat sparse local-brand
coverage as unknown and keep provider-modeled AI search volume out of revenue
arithmetic until validated.
[DataForSEO LLM Mentions API](https://docs.dataforseo.com/v3/ai_optimization-llm_mentions-overview/),
[DataForSEO citation retrieval](https://dataforseo.com/help-center/how-to-get-llm-citation-data-with-llm-mentions-api).

### Recommendation priority

Do not select actions only because they have the lowest check score. Rank
recommendations using:

```text
priority =
  issue severity
  × affected important pages
  × reviewed demand fit
  × conversion proximity
  × service deliverability
  × evidence confidence
  ÷ estimated effort
```

The score explains condition. The recommendation engine should explain what is
worth doing next.

## 3. Better sources

### Cold-prospect sources

Use sources that do not require owner access:

1. Current bounded website crawl and screenshots.
2. DataForSEO organic and Maps observations for approved keywords.
3. DataForSEO backlink summary and external entity corroboration.
4. A small geospatial Maps grid for the highest-value local intents.
5. Lighthouse lab diagnostics and CrUX field data when available.
6. Public business-listing facts and reviews with explicit source/date.
7. Optional DataForSEO LLM mentions/citations.

DataForSEO's SERP API supports location/language/device-specific organic and
Maps results, but the provider also notes that personalized history is not
represented. Every displayed rank must therefore retain its market, device,
timestamp, and sample limitation.
[DataForSEO SERP API](https://docs.dataforseo.com/v3/serp/overview/).

The largest immediate evidence improvement for both BJJ and trades is a Maps
grid. BrightLocal's product is built around the fact that local rankings vary
from street to street, supports 3×3 through 15×15 grids, competitor comparison,
and before/after views. A single Tacoma location is directional, not a market
map.
[BrightLocal Local Search Grid](https://www.brightlocal.com/local-seo-tools/rankings/local-search-grid/).

Recommended tiers:

- Teaser: 3×3 grid for three approved commercial terms.
- Premium: 5×5 grid for five approved terms.
- Output: top-3 coverage, top-10 coverage, median rank, competitor share of
  grid, and a color heatmap.

### Owner-authorized sources after engagement

These sources turn a persuasive estimate into an accountable growth system:

- **Google Search Console:** queries, pages, clicks, impressions, CTR, position,
  device, and country. The API returns top rows rather than a guaranteed
  complete census, so completeness must remain explicit.
  [Search Analytics API](https://developers.google.com/webmaster-tools/v1/searchanalytics/query).
- **Google Business Profile Performance:** Search/Maps impressions, website
  clicks, call clicks, direction requests, bookings, and monthly keyword
  impressions. Google documents that multiple impressions from one user in one
  day are counted once for several impression metrics. This is materially
  closer to Nova's "unique people" question than keyword-tool volume.
  [Business Profile Performance API](https://developers.google.com/my-business/reference/performance/rpc/google.mybusiness.performance.v1).
- **GA4:** source/medium, landing pages, signups, key events, and conversions.
  [Google Analytics Data API](https://developers.google.com/analytics/devguides/reporting/data/v1/api-schema).
- **CRM/SaaS:** trial booked, trial attended, enrolled, retained, and revenue.
- **Google generative AI performance:** owner-authorized Search Console reports
  are rolling out with generative-AI impressions, pages, countries, devices,
  and time trends.
  [Google Search generative AI performance reports](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports).
- **Bing AI Performance:** citations, cited pages, grounding-query samples, and
  trends from owned-site access.
  [Bing AI Performance](https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview).

This creates a clean product progression:

```text
cold prospect evidence
→ owner-approved baseline
→ implementation
→ observed visibility change
→ trial/signup change
→ retained revenue
```

## 4. What competitors do better or differently

| Product group | What they do better | What Outreach should copy | What not to copy |
| --- | --- | --- | --- |
| Semrush / Ahrefs | 140–170+ technical checks, issue severity, benchmarks, crawl comparison, history | Broader check registry, site-wide issue density, trend comparison | Opaque universal scores or special-AI-file theater |
| Screaming Frog | Deep crawl configuration, JS rendering, GSC, URL Inspection, PageSpeed/CrUX integrations, crawl comparison | Rendered-content parity, owner connectors, crawl diffs | Expert-only interface complexity |
| BrightLocal / Whitespark | Geospatial local rankings, competitor maps, repeated tracking | Maps grid, local share of visibility, before/after heatmaps | Treating rank movement as causal proof |
| Ahrefs Brand Radar / Semrush AI Visibility | Actual mention, citation, prompt, and share-of-voice evidence | Separate observed AI visibility contract | Calling modeled impressions actual audience reach |
| SEOptimer / WooRank | Fast URL audits, bulk lead generation, white-label templates, embedded forms | Template-driven client output and reusable vertical branding | Thin instant scores without attributable evidence |
| AgencyAnalytics / Semrush Reports | Stable share links, templates, scheduled reporting, many data connectors, annotations | Durable hosted reports, source widgets, change annotations | Generic KPI dashboards that bury the sales narrative |

Supporting product documentation:

- [Screaming Frog configuration and integrations](https://www.screamingfrog.co.uk/seo-spider/user-guide/configuration/)
- [Whitespark Local Rank Tracker](https://whitespark.ca/local-rank-tracker/)
- [AgencyAnalytics SEO reporting](https://agencyanalytics.com/features/seo-tools)
- [Semrush My Reports](https://www.semrush.com/kb/34-my-reports)
- [SEOptimer automated reports](https://www.seoptimer.com/automated-seo-reports/)

## 5. Client-facing design improvements

The current Nova deck is visually strong, but it is a handcrafted derivative
of the evidence rather than a productized render. The durable client output
should have three layers:

### Layer 1: 90-second owner brief

- What is already working.
- The clearest missed non-brand/local opportunity.
- Three recommended actions.
- Capacity upside, explicitly labeled as a ceiling or reviewed scenario.
- One next-step CTA.

### Layer 2: interactive evidence

- Search and Maps tabs.
- A Maps heatmap rather than only rank tables.
- Target-versus-competitor landing-page comparison.
- AI Readiness versus Observed AI Visibility.
- Expandable "show the evidence" controls.
- Every rank labeled with location, device, date, and sample depth.
- Every modeled number labeled observed, supplied, assumed, or modeled.

### Layer 3: methodology and export

- Evidence completeness by source.
- Limitations and unresolved evidence.
- Formula version.
- Source snapshot IDs.
- Print-safe PDF and structured JSON download.

Client and operator views should be separate. Provider cost, call failures,
approval mechanics, raw artifact paths, and correction queues belong in the
operator view. The client sees evidence quality and limitations in plain
language.

Add reusable design templates for:

- National BJJ Registry;
- One Trade Network;
- client-facing pitch;
- operator evidence review;
- after-engagement performance update.

Competitor reporting platforms emphasize templates, branding, stable links,
scheduled updates, and annotations. The Outreach advantage should be a better
story and stronger provenance, delivered with the same repeatability.
[Semrush report builder](https://www.semrush.com/kb/1625-creating-a-pdf-report),
[AgencyAnalytics SEO reports](https://agencyanalytics.com/solutions/seo-reporting).

## 6. Durability improvements

### Preserve the strengths

Keep:

- attempt-scoped checkpoints;
- versioned score contracts;
- evidence references;
- raw provider artifact references;
- source hashes;
- predecessor/successor records;
- append-only activation events;
- separate target, market, and modeled opportunity layers.

### Correct the remaining overwrite paths

The market layer preserves market-run-scoped report snapshots, but canonical
report persistence can still overwrite an existing `(run, report_version)`
slot:

- the file repository writes the same `reports/<version>.json` path;
- the SQLite repository uses `ON CONFLICT ... DO UPDATE`;
- checkpoints similarly update a `(run, attempt, stage)` slot.

Replace the claim of immutable reports with a truly immutable
`ReportSnapshot`:

```text
ReportSnapshot
  id
  run_id
  attempt_id
  report_contract
  source_snapshot_ids
  renderer_version
  payload_sha256
  manifest_sha256
  created_at
```

Write snapshots once. Maintain a mutable `latest` pointer separately.

### Create a portable report bundle

Every client report should be a self-contained generated bundle:

```text
manifest.json
report.html
report.pdf
data/report.json
assets/*.png
hashes.sha256
```

The manifest should record:

- report and renderer versions;
- source report IDs and hashes;
- every asset path, MIME type, size, and SHA-256;
- creation time and expiry/access policy;
- client/vertical theme version;
- evidence completeness.

The current presentation references screenshots elsewhere in the run tree and
is shared through a temporary tunnel. That is useful for prototyping, but not a
durable client artifact. Generate it from the report snapshot, copy or
content-address its assets, validate the manifest, and publish it behind an
expiring signed link or authenticated custom domain.

### Reduce report duplication

The current combined Nova `v3.json` is approximately 4.8 MB because source
reports and export payloads are embedded repeatedly. Store the canonical
evidence once and reference immutable source snapshots by ID/hash. Generate
denormalized HTML/PDF at render time. This reduces storage, API response size,
hash ambiguity, and the chance that embedded copies drift.

### Add temporal proof

Competitors repeatedly emphasize crawl comparison, rank history, and
before/after reporting. Preserve every baseline and compute deltas as new
objects:

- issue introduced/resolved;
- page added/removed/changed;
- rank and Maps-grid movement;
- AI mention/citation movement;
- trial and signup movement;
- operator correction rate.

Do not mutate a baseline to represent progress.

## 7. Recommended delivery order

### P0 — credibility and repeatability

1. Replace `overall_score` presentation with Technical SEO Health v2 while
   retaining the legacy field for compatibility.
2. Add a site-wide check registry, severity, affected-page ratios, and page
   importance.
3. Add `ReportSnapshot`, bundle manifest, generated client HTML/PDF, and stable
   access links.
4. Add 3×3 Maps-grid evidence for three high-intent terms.
5. Add report-to-report comparison for technical issues and rankings.

### P1 — stronger market proof

6. Add Conversion Readiness as a separate, deterministic score.
7. Add optional observed AI mentions/citations without changing AI Readiness.
8. Add competitor GBP category/review/profile comparisons and local-grid share.
9. Add approved owner connectors for Search Console, GBP, and GA4.

### P2 — calibration and moat

10. Calibrate severity and recommendation priority from vertical outcomes:
    corrections, replies, calls, proposals, wins, implemented fixes, rank
    movement, trials, and retained revenue.
11. Publish vertical benchmarks only after sample sizes are sufficient.
12. Use National BJJ Registry and One Trade Network data to improve taxonomy,
    demand grouping, and service-fit selection—not to fabricate prospect facts.

## Acceptance metrics

- Every client headline score has a documented, site-wide formula and evidence
  confidence.
- 100% of displayed claims resolve to a report-snapshot manifest entry.
- No report snapshot or source artifact is overwritten.
- A client report is generated from data and theme versions without manual HTML
  editing.
- Local visibility uses more than one geographic observation.
- AI Readiness and Observed AI Visibility are never conflated.
- Owner-authorized baselines can connect impressions to website actions and
  CRM outcomes.
- Median client-report review time remains below 10 minutes.
- Factual correction rate and unsupported-claim rate trend toward zero.

## Methodology

Repository behavior was inspected through the scoring, AI readiness,
provenance, market reporting, opportunity modeling, persistence, tests, and
the Nova report artifacts. External research used 36 targeted query variations
and reviewed more than 20 current official documentation or first-party
product pages across Google, Microsoft, OpenAI, DataForSEO, Semrush, Ahrefs,
Screaming Frog, BrightLocal, Whitespark, SEOptimer, WooRank, and
AgencyAnalytics. Product claims were treated as descriptions of documented
capabilities, not independent performance validation.

