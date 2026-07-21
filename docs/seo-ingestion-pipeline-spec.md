# SEO Ingestion Pipeline Spec

Prepared: 2026-07-06
Workspace: `C:\Users\Snipe\Downloads\Outreach Program`

## Objective
Build a low-fixed-cost SEO intelligence and content-ingestion pipeline that maximizes:
- keyword coverage
- service/geography page coverage
- sitemap quality
- internal-linking quality
- competitor gap visibility
- audit evidence quality

without making Ahrefs/Semrush the operating system.

## Core principle
**Deterministic before generative.**

The pipeline should first collect and normalize:
- canonical business/entity facts
- page inventory
- page classifications
- metadata/H1/schema evidence
- SERP/keyword evidence
- competitor evidence

Only after that should it generate:
- keyword maps
- page briefs
- sitemap recommendations
- rewritten metadata/copy
- outreach audits

## Stack
- **Postgres/Supabase**: system of record
- **DataForSEO**: search/SERP backbone
- **Managed extraction or crawler**: page text + sitemap intake
- **Playwright/browser automation**: rendered verification, screenshots, forms, hard cases
- **Python job runners**: ingestion + scoring
- **Vercel/Next.js**: eventual surfacing/app layer

## Pipeline stages

### 1. Canonical entity intake
Input:
- business name
- domain
- phone
- trade/category
- city/state
- source provenance

Output:
- one canonical entity record with aliases and confidence

### 2. Crawl and fetch
Per domain, collect:
- homepage
- service pages
- location pages
- contact/about
- blog/resources
- project/case-study pages
- robots.txt
- sitemap.xml and child sitemaps
- title/meta/H1/schema/internal links/images

### 3. Deterministic page classification
Each URL gets one primary class:
- homepage
- service
- location
- service_location
- project_case_study
- blog_resource
- contact_about
- legal_utility
- low_value

### 4. Search intelligence
For each entity + market cluster:
- pull target SERPs
- pull keyword ideas
- identify ranking competitors
- capture local/organic features
- store raw and normalized evidence

### 5. Coverage modeling
Quantify:
- service coverage
- geo coverage
- service x geo matrix coverage
- supporting-content coverage
- low-value indexable surface area
- sitemap inclusion quality

### 6. Recommendation generation
Create:
- page gap recommendations
- sitemap diffs
- title/meta rewrite recommendations
- internal-link recommendations
- priority content briefs

## Job flow
1. `entity_intake_job`
2. `site_discovery_job`
3. `page_fetch_job`
4. `page_parse_job`
5. `page_classification_job`
6. `keyword_seed_job`
7. `serp_snapshot_job`
8. `competitor_gap_job`
9. `coverage_scoring_job`
10. `sitemap_recommendation_job`
11. `content_brief_job`
12. `audit_summary_job`

## Page-to-keyword mapping logic
Each keyword cluster should map to exactly one primary page target type:
- broad commercial category -> homepage or top-level service hub
- service intent -> service page
- service + city -> service_location page
- geography-only local intent -> location page
- proof/trust queries -> project/case-study page
- informational/problem queries -> blog/resource page

### Mapping rules
- no two pages should target the same primary cluster unless one is intentionally regional and one is local
- service_location pages only exist where there is credible commercial intent
- blog pages support service/geo pages; they do not replace them
- low-confidence keyword clusters go to backlog, not immediate page generation

## Scoring model
Compute a weighted score per domain:
- 20% service page coverage
- 20% service x geography coverage
- 15% metadata/H1 quality
- 10% sitemap hygiene
- 10% internal-link quality
- 10% schema coverage
- 10% competitor surface gap
- 5% thin/duplicate/bloat risk penalty

## Sitemap generation rules
Include only URLs that are:
- canonical
- indexable
- non-duplicate by intent
- above minimum content/evidence threshold
- mapped to a recognized page class

Exclude URLs that are:
- filtered/search/parameter pages
- thin placeholders
- staging/test pages
- redirect targets
- duplicate-intent pages
- soft 404 / utility pages

### Sitemap outputs
- `sitemap_index.xml`
- `sitemap-services.xml`
- `sitemap-locations.xml`
- `sitemap-service-locations.xml`
- `sitemap-projects.xml`
- `sitemap-blog.xml`

## Competitive model
For each target domain, compare against 3-5 competitors on:
- service page count
- location page count
- service_location page count
- blog/resource count
- project/case-study count
- observed SERP presence
- metadata quality
- sitemap breadth

## What not to depend on
Do not make these mandatory for core operation:
- Ahrefs
- Semrush
- manual operator exports
- ad hoc spreadsheet-only workflows

They can be analyst overlays later, but the pipeline must function with:
- DataForSEO
- direct crawl evidence
- your own scoring logic
- GSC once the asset is owned

## Required outputs per account
1. normalized entity
2. crawl inventory
3. page evidence bundle
4. keyword cluster set
5. competitor set
6. coverage scores
7. sitemap recommendation
8. page brief backlog
9. audit summary

## First implementation target
Implement the smallest viable path:
- single domain intake
- homepage + sitemap pull
- page metadata parsing
- 20-50 keyword seed pull via DataForSEO
- simple page classification
- first coverage score
- sitemap recommendation artifact
