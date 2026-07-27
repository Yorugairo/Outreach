# Product Strength Contract: P10 Scoring Surfaces

## 1) Scope and versioning

This contract defines deterministic, surfaced scoring in P10 while preserving
legacy compatibility.

- Surface contract versions are explicit and immutable per run artifact:
  - `seo-health.v2`
  - `search-visibility.v2`
  - `local-visibility.v1`
  - `ai-readiness.v3`
  - `ai-visibility.v1`
  - `conversion-readiness.v1`
  - `evidence-confidence.v1`
- `overall_score` remains only as `legacy_surface = true`.
- Unknown evidence is emitted as `status = "unknown"` and is never treated as zero.

## 2) Product surfaces

1. Technical SEO Health (`seo-health.v2`)  
   - Purpose: crawl/indexability readiness and reliable extraction quality.
   - Output: overall score, family scores, applicability, completeness, confidence.
2. Search Visibility (`search-visibility.v2`)  
   - Purpose: domain visibility over approved demand contexts.
   - Output: tracked-keyword coverage, top-3/top-10/top-20, weighted visibility, median rank.
3. Local Visibility (`local-visibility.v1`)  
   - Purpose: geographic mention/placement coverage over immutable grid definitions.
   - Output: grid coverage, median observed rank, heatmap coverage.
4. AI Readiness (`ai-readiness.v3`)  
   - Purpose: AEO/GEO/AIO extraction readiness and citation structure.
   - Output: weighted readiness score with AEO, GEO, AIO family scores.
5. Observed AI Visibility (`ai-visibility.v1`)  
   - Purpose: actual AI-provider mentions/citations in approved prompt scenarios.
   - Output: mention/citation counts, distinct cited pages, coverage, share of voice.
6. Conversion Readiness (`conversion-readiness.v1`)  
   - Purpose: visible conversion path integrity and usability evidence.
   - Output: offer clarity, CTA/action feasibility, trust/contact clarity, mobile access checks.
7. Evidence Confidence (`evidence-confidence.v1`)  
   - Purpose: evidence quality of observed required checks.
   - Output: evidence ratio, source ledger, limitation reasons.

## 3) No universal average

- Do not produce one “overall health” average across the seven surfaces.
- `overall_score` is retained for compatibility only and displayed as legacy.

## 4) Formula and unknown/inapplicable semantics

### A. Technical SEO Health v2

- Family weights:
  - crawl/indexability: `0.30`
  - on-page/template quality: `0.20`
  - architecture/internal links: `0.20`
  - structured data/entity: `0.15`
  - mobile/performance: `0.15`
- Per-check penalty:
  - `check_penalty = severity_weight * weighted_affected_ratio * evidence_confidence`
- Family score:
  - `family_score = 100 - 100 * (sum(known_penalties) / sum(known_applicable_severity))`
- Health score:
  - `sum(family_score * family_weight for known families) / sum(known_applicable_family_weights)`
- Unknown checks do not enter arithmetic but do count toward completeness.
- Inapplicable checks are excluded from score and completeness for that family.
- Scores are clamped to `0..100` and rounded at presentation time.

### B. AI Readiness v3

- Family weights remain:
  - `aeo 40%`, `geo 35%`, `aio 25%`
- Checks are continuous and applicability-aware.
- Single observations from one mention/domain do not satisfy corroboration.
- `llms.txt`, `FAQPage`, `HowTo` are observations only; they do not auto-bias score.

### C. Search, local, and AI visibility

- Require approved market set, identity, place/grid, prompt/topic scope, and date/device context.
- Missing context => `unknown`, not penalty.
- Paid/optional visibility outputs never mutate other deterministic surfaces.

### D. Conversion readiness v1

- Deterministic evidence only from site-derived signals.
- Unknown evidence reduces confidence; it must not imply funnel outcomes or revenue lift.

## 5) Snapshot, bundle, and comparison contracts

### Report snapshots

- Reports are emitted from immutable `ReportSnapshot` records.
- Snapshot captures source IDs/hashes, schema/contract versions, renderer version,
  payload hash, and manifest hash.
- A snapshot cannot be rewritten after creation.

### Aliases

- `ReportAlias` may move pointers (e.g., `latest`), but never mutates snapshot content.

### Bundle

- Bundle layout:
  - `bundles/<bundle_id>/manifest.json`
  - `bundles/<bundle_id>/report.html`
  - `bundles/<bundle_id>/report.pdf`
  - `bundles/<bundle_id>/data/report.json`
  - `bundles/<bundle_id>/assets/<sha256>.<ext>`
  - `bundles/<bundle_id>/hashes.sha256`
- Rendered output must resolve each factual/model claim through manifest entries.

### Comparison

- Comparison runs are immutable.
- Delta output is generated only when compatible on:
  - stable check IDs
  - normalized page identity
  - keyword set
  - grid points
  - prompt/version identity
- Incompatible dimension changes produce `unknown` and suppress numeric deltas.

## 6) Legacy-read and compatibility rules

- All legacy `overall_score`, `ai-v1`, `ai-v2`, `market-v1`,
  `checkpoints`, and older run schemas remain readable.
- Legacy six-stage runs remain backward-compatible.
- Unknown or partial evidence must be explicit and traceable; no silent downgrades.

## 7) P12 decision-intelligence separation

- `decision-intelligence-v1` and combined `v6` are additive report contracts.
- Business facts, decision coverage, browser journeys, AI representation
  accuracy, owner diagnosis, and remediation blueprints are evidence or labeled
  inference, never new product-surface scores.
- Prospect reports can bind only prospect-mode snapshots. Owner-mode snapshots
  remain private even when both modes exist for the same run.
- Report snapshots and outreach packages bind exact P12 snapshot IDs and content
  hashes; aliases may advance, but historical snapshots are immutable.
- Recommendation-outcome summaries report compatible vertical/service cohorts,
  denominators, and associations only. They do not claim causality or modify
  recommendation weights before the product's explicit sample gates.
