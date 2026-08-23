# P14 Director And Scene Board — Implementation Report

Plan: `.claude/PRPs/plans/P14-DIRECTOR-AND-SCENE-BOARD.plan.md`
Status at report time: `running` — T1–T6 complete, T7–T10 pending
Branch: `claude/content-generation-system-52f077`
Date: 2026-08-22

## What shipped

The paste-lane spine: paste a script you have already sourced, get a directed
scene breakdown, a prompt fan-out for the run agent, and a board with defaults
already picked.

| Task | Result |
| --- | --- |
| T1 Paste-entry contract and provenance attestation | ✅ complete |
| T2 Director request pack and validated proposal ingest | ✅ complete |
| T3 Provisional coverage at estimated timing | ✅ complete |
| T4 Multi-variant fan-out and slot-bound validation | ✅ complete |
| T5 Three-tier scene board renderer | ✅ complete |
| T6 Selection capture into the existing review contract | ✅ complete |
| T7 Style-pack registry for six lanes | ⛔ not started |
| T8 Character pose and expression library | ⛔ not started |
| T9 Whiteboard lane proof unit | ⛔ not started |
| T10 Three.js lane proof spike | ⛔ not started |

## Validation

```
python -m pytest content/video_engine/tests -q
421 passed, 5 failed
```

The 5 failures are all in `content/video_engine/tests/test_history_v4_pipeline.py`
and are the documented pre-existing baseline (tracked separately as
`task_5672544a`). No sixth failure, so no regression from this work. **73 new
tests** were added across six modules: 10 / 12 / 12 / 13 / 14 / 12.

```
python scripts/prp_validate.py .claude/PRPs/plans/P14-DIRECTOR-AND-SCENE-BOARD.plan.md
PASS
```

### End-to-end acceptance

Ran the full chain against `docs/content-video-engine/samples/paste-sample.txt`
(71 words, 30.429s estimated). The run agent was stood in for by a local stub
that segments the script and returns placeholder PNGs — **no provider was
called and no paid job was released.**

| Step | Result |
| --- | --- |
| `ingest-script` | brief written; `validating_research` absent from stage order |
| `compile-director-request` | 5 suggested beats; `operator_writes_on_screen_copy: true` |
| `record-director-proposal` | 6 beats, all 6 `copy_deferred` |
| `compile-provisional-coverage` | 8 slots, `timing_basis: estimated`, `duration_drift_ratio: 0.0` |
| `compile-visual-prompt-pack` | 8 groups × 3 variants = 24 requested generations |
| `validate-candidate-batch` | all 24 accepted, slot-bound |
| `render-scene-board` | 8 slots, 8 auto-selected, 0 exceptions, 13,753-byte offline page |
| `record-scene-selection` | 8 selections, 0 operator decisions, `approved: false` |

### Determinism

Ran the chain twice into separate directories from the same stored proposal.
All five artifacts byte-identical: `source_attestation.json`,
`director_brief.json`, `director_proposal.json`, `provisional_coverage.json`,
`visual_prompt_pack.json`. The model sits upstream of the pipeline, so
`content/video_engine/AGENTS.md`'s determinism rule holds.

## Decisions worth knowing

**The director may segment and direct; it may never rewrite.** Beat narration
must reconstruct the attested script exactly. A proposal that shortens, extends,
or rephrases is rejected with the specific failure named — truncated, additive,
or rewritten. This turned out to be the cheapest possible guard against a model
quietly improving the operator's copy.

**Estimated timing is contained, not hidden.** Coverage compiled before audio
carries `timing_basis: "estimated"`, and `assert_render_ready()` raises if any
render-timing consumer is handed it. Audio remains the clock.

**Selection is exception-based.** A 150-slot episode would otherwise mean 150
operator decisions. Every slot carries a deterministic auto-selected default
(operator-selected, else lowest clean variant), exceptions sort to the top of
the page with their reason, and a clean board records with zero input.

**Two art-review rules are enforced by contract, not review.** Every prompt
carries a negative clause forbidding lettering, numerals, logos and watermarks;
a candidate flagged `contains_factual_text` is refused with a message naming the
rule. Every prompt repeats the lane's `identity_anchor` — for
`stick_explainer`, the flat colour t-shirt block that the ceiling reference uses
as its whole identity system.

## Bug found and fixed during implementation

A candidate batch returned without a stamped `artifact_hash` left
`candidate_batch_hash: null` in the selection review, which the existing
`asset_selection_review` schema rightly rejected. Surfaced by
`test_scene_selection.py`. Fixed in `scene_board._bound_hash`, which derives the
digest from batch content when it is unstamped — so the review is always bound
to the exact batch that produced the board. Fixed in the service, not the test.

## Deviations

Seven, recorded in full in the plan's `## Deviations` section. The three that
matter:

- **`slot_id`/`variant_index` are optional in the shared candidate schema, not
  required as T4 specified.** Making them required would invalidate every
  existing documentary-lane batch. They are required by the paste lane in
  `visual_prompt_pack.validate_candidate_batch` instead, which is where the
  acceptance behaviour is tested. Same effect for the paste lane; the
  documentary lane keeps working.
- **Two files outside any slice write set**: `services/artifact_io.py` (shared
  canonical hashing — the alternative was duplicating it six times or importing
  Pillow) and `tests/conftest.py` (shared fixtures; none existed).
- **Named agents were not used.** The runbook routes slices to
  `implementation_luna` / `junior_developer` / `speedster`; those types are not
  registered in this session and a standing session instruction forbids invoking
  subagents unasked. The parent implemented and verified every slice.

## Standing constraints, unchanged

- Google Flow queue remains paused. No paid video job released.
- `video_intents.json` writes `provider: null`, `status: "not_requested"`.
- Generated candidates stay `render_eligible: false` and are not promoted to the
  asset catalog.
- `approved` is never set by product code — `record-scene-selection --approve`
  is an operator action.
- No provider keys were read or required; the engine makes no network calls.

## What is not done

- **T7–T10**: the six-lane style-pack registry, the character pose library, and
  the whiteboard / Three.js proofs. These are the lane work — the part that
  addresses "even Stick Trader has been hard to accomplish." The spine is what
  feeds them.
- **No real images have been generated.** Every candidate in the E2E run was a
  placeholder PNG. The contract is proven; the art is not.
- **Canonical ElevenLabs audio still does not exist**, so no paste-lane run can
  reach canonical coverage or final render. The board and selection gate were
  deliberately built to be reachable without it.

## Next

T7 then T8 is the critical path — character consistency is the capability the
reference channels actually depend on, and T8's `identity_anchor` is what the
prompt pack is already writing into every prompt.
