# Architecture Decision: SEO Insights Platform over Script-First Pipeline

Date: 2026-07-07
Status: Accepted

## Context
The initial planning artifacts framed the SEO system primarily as an ingestion pipeline with multiple standalone scripts. That was a useful bootstrap for validating crawl/search primitives, but it does not match the real product need.

The real requirement is a consistent tool that can be pointed at a URL and produce SEO, sitemap, keyword, and ranking insights in a repeatable, operator-friendly way.

## Decision
Adopt a **platform architecture** centered on persisted `SEO Insight Runs`.

Scripts and workers are allowed as execution mechanisms, but they are not the product boundary.

## Rationale
- the product surface is a run/report, not a terminal command
- the user already has broader normalization/data architecture underway
- competitor research is secondary and can be layered later
- run-state tracking, repeatability, and exports matter more than standalone entrypoints
- UI/API consumers need stable platform objects

## Consequences
### Positive
- cleaner fit with broader normalized data platform
- easier operator usage
- easier future UI/API integration
- easier later enrichment with competitors, GSC, and content generation

### Tradeoffs
- requires more up-front modeling around run lifecycle and report objects
- slightly slower than pure script-first prototyping
- requires clearer API and state design earlier

## Rule going forward
Future implementation should prefer:
- run-centric DB records
- reusable services
- orchestration layer
- exports and reports as first-class artifacts

and avoid placing core product logic only inside one-off scripts.
