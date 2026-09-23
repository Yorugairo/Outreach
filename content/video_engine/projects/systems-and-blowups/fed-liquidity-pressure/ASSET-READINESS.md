# Asset readiness — MP-FED-LIQUIDITY pilot (T4 preparation)

**Date:** 2026-09-18  
**State:** inventory/readiness only. No claim opened, generation, login, paid action, contact sheet, approval, or promotion was performed. HG2 remains open in `docs/content-video-engine/review-queue.v1.json` (`mp-fed-liquidity-hg2-assets`).

## Semantic inventory

No manifest-recorded approved asset is a direct fit for W2 owner/workshop, W4 repo-clearing counter, or P2 matching transparent loan folio.

Closest `state: approved`, `render_eligible: true` records in `content/video_engine/sources/PLATE-LIBRARY.json` (local SHA-256 verified; **near-matches only**):

- `world-workbench-triad-v1` — `content/video_engine/projects/systems-and-blowups/review/claims/steel-and-paper-plates-wave-1/objects/world-workbench-triad-v1.png` — `01d08817c8e2a0d0a1e3ede3ba56cf98a792991824f8defbe1e52618ba22830c`; flat, no owner/machinery/expansion bay/document space.
- `world-adviser-signature-v1` — `content/video_engine/projects/systems-and-blowups/review/claims/steel-and-paper-plates-wave-3/objects/world-adviser-signature-v1.png` — `02516ddf660bda77b9dc5cfa1956f056cc72d3ed8ea54910010df6f292a948a3`; form-on-desk, not a blank W2-matched folio.
- `world-exchange-floor-1845` — `content/video_engine/projects/systems-and-blowups/review/claims/steel-and-paper-plates-wave-5/objects/world-exchange-floor-1845.png` — `e8f7f361d46600bc9fb6c762caaea4e42edfa60b79b95910f4443ac37ddd2bf5`; historical floor, not two-sided dealer/fund counter.

Episode catalog near-misses are explicitly non-reusable: `content/video_engine/projects/systems-and-blowups/asset-catalog.v1.json` records `building-neighborhood-workshop-v1` (`5348461973dbb55286276216571b159c16f5d2b41e11e1a8b245f1aac587a783`), `world-exchange-floor-v1` (`70d9bab2f15b3021edc15c337ed377250a0a01a85e3a8ccc6e42c4f6a45a3303`), and `world-office-desk-v1` (`42b5da725c66d96ca65c0e5ec5053d1a76a52c6592ecab849553bf74ad12da69`) as `review_only`/`render_eligible:false`.

Supporting approved props exist, but are not direct fits: `content/video_engine/assets/props/manifest.json` + `CATALOGUE.md` — Fed building `aebc6e5962659ce4fafefe30923500453d374cb91c0d247418cc83ebf865d45b`, liquidity pump `e5fb648721d04c6d6944867f2c942839c151a1eca84e68d0db8d17da24ae0520`.

## Minimum missing-asset claim inputs

Use the installed `generation_claim.v1` API in `content/video_engine/src/services/generation_claim.py` (`open_claim`, then `render_work_order`), not a handmade work order. Required: unique lowercase-kebab `claim_id` (for example `mp-fed-liquidity-pilot-worlds-v1`), operator-selected `style_family`, project root, and **seven unique slots**: `w2-owner-workshop-{background,mid,subject}-v1`, `w4-repo-counter-{background,mid,subject}-v1`, and `p2-owner-loan-folio-v1`. Each slot needs `prompt`, `kind`, and semantic; prompts must keep labels/numbers in code, W2 owner continuity, W4 dealer/fund sides plus clear lane, and P2 transparent blank sleeve. Provide existing read-only `reference_images` or explicit none; `model` is optional and `model_effort` defaults to `low`.

## Route, layer constraint, blockers

`python -m content.video_engine.cli --help` is read-only and exposes `claim-resume` only; no claim-create CLI. Opening a claim would write `~/.video-engine/claims/<id>.json` and `review/claims/<id>/`, so it was not run. Flow is isolated through `.agents/agents/flow-asset-producer.md` and `.mcp.json` (`tools/google-flow-driver/mcp/server.mjs`); this session exposes no `invoke_subagent`, so producer dispatch is blocked here. Later worker gate: `python content/video_engine/scripts/prepare_props.py --check <delivery_dir>`.

`docs/content-video-engine/PIPELINE.md` requires NEW layers to be separately generated, never sliced from a new composite; existing flat plates are only a depth-split fallback after semantic acceptance. No browser loop was used.
