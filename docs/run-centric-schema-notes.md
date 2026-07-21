# Run-Centric Schema Notes

Prepared: 2026-07-07

## Purpose
This refactor changes the SEO database model from an entity-centric crawl schema into a run-centric platform schema.

The core product object is now:
- `insight_runs`

Everything operational should tie back to a run so the platform can support:
- ad hoc URL analysis
- entity-backed analysis
- stateful orchestration
- repeatable exports
- run history and debugging

## New anchor tables
- `seo_targets` — normalized URL/domain targets independent of whether a canonical business entity exists
- `insight_runs` — one execution of the SEO insights engine
- `run_stage_events` — stage-by-stage lifecycle and retry history
- `run_artifacts` — raw payloads, exports, screenshots, sitemap XML, JSON blobs
- `discovered_assets` — robots, sitemap files, pages, and other discovered URLs
- `page_records` — normalized page objects for a specific run
- `coverage_scorecards` — deterministic per-run scores
- `insight_reports` — final operator-facing report bundles

## Important modeling changes
### Before
Most tables were anchored directly to `business_entities`.

### After
Most tables are anchored to `insight_runs`, with `seo_target_id` attached where useful and `business_entity_id` optional.

This allows:
- analyzing a raw URL before entity resolution exists
- keeping multiple historical runs per target
- preserving run-specific evidence even when the target changes later

## Design rule
If a record exists because a specific analysis run happened, it should reference `insight_runs`.

Examples:
- page evidence
- SERP snapshots
- scorecards
- sitemap recommendations
- findings
- reports

## What remains entity-centric
- `business_entities`
- `entity_aliases`
- `entity_domains`

These remain useful as upstream normalized data sources, but they are no longer the main operational anchor for the SEO platform.
