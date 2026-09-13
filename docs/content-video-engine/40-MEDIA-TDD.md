# 40 — MEDIA TDD (operator decision, 2026-08-31)

RED-GREEN discipline translated for a production repo whose outputs are
judged by eye and ear. ECC's TDD core survives; its software-delivery
surface (coverage percentages, unit/integration/E2E taxonomy) is
explicitly OUT OF SCOPE here — the discipline is what transfers, not
the taxonomy.

## The three laws

1. **Every defect that reaches the operator ships its GATE in the fix
   commit.** A gate is any check that would have caught the defect:
   a preflight assertion, a drift threshold, a choreography clash rule,
   a template-enforced layout constraint, a recap-fill rule. The fix
   without the gate is half a fix — the same class WILL recur.
2. **Nothing is trusted until it fails-then-passes a KNOWN-REAL case.**
   A detector must re-find the defect we know exists (the stutter
   scanners died here — three plausible detectors, zero could re-find
   the one confirmed case). An effect/fix must be verified on the
   FINAL deliverable, not an intermediate (the "fixed" stutter that
   still shipped). This is RED before GREEN: no green without having
   seen the red.
3. **Negative results are doctrine.** An approach that fails validation
   gets its failure recorded in the owning doc in the same commit —
   what was tried, why it failed, what signal would be needed to retry
   (doc 37 §23b is the model). Un-recorded failures get expensively
   re-walked.

## The test pyramid, media edition

| Layer | Software analog | Ours |
|---|---|---|
| Deterministic gates | unit tests | recorder preflight (16 gates), join drift ≤0.15s, whisper diff (insertions/deletions FAIL), choreography clash gates, badge-chart sync, caption/timeline duration match |
| Ground-truth cases | regression tests | the known stutter (23.95s), the zero-tail join, the 46ms fake gap, the empty recap — each now permanently encoded in a gate or doctrine |
| Structural checks | integration tests | retime anchor coverage (41/41 verbatim), topic-exit audit, filmstrip boundary classes vs the locked reference build |
| The operator's eye/ear | E2E / acceptance | the ONLY instrument for perceptual classes (envelope analysis is blind <100ms). Protocol: cheap preview candidates, source untouched until the pick; verification clip cut from the finished master |

## The loop for any new tool or fix

```
RED    reproduce or isolate the defect on a known-real case
GREEN  fix it; validate on the FINAL deliverable
GATE   add the check that would have caught it (same commit)
DOC    if anything failed along the way, record the negative result
```

## Tests that bite — the author's blind spot

Tests written beside the code share its assumptions: a fresh read-only
review found 16 confirmed defects in self-authored P15 T1/T2 work
(2026-08-23, LEDGER `d4bfcb21ab5e`). Four habits close the gap:

- **Break the code and watch the test fail.** A new test passed with the
  bug present (`e436831bec02`) — law 2 applies to our own tests too.
- **Fixture from real assets.** All 34 tests passed because the synthetic
  fixtures sat at alpha exactly 255; the real asset tops out at 254.
- **Assert on the written artifact the consumer reads, not stdout.** The
  gates runner printed the viewer's FAIL while the written report — the
  file that blocks a take — computed its VERDICT without it (2026-09-03,
  `fc5f3c4a6ed2`).
- **Verify a join by reading its output, never its count.** Keyed on
  `chapter_index` instead of `beat_id`, a join gave every plate the next
  chapter's excerpt; the labels read plausibly and the count was identical.
  An exact-id match silently dropped 180 of 192 semantics. Cross-check
  sample output against an independent key (the plate's own name)
  (2026-08-29, `39c2082750a7`, `05a581ea4c1e`).

## Standing gate inventory

The chain's gates are the suite; run state is the build state. All
FAILs block. Inventory lives in CAPABILITIES.md (same-commit update
rule applies to gates exactly as to capabilities).

## Chart/visual acceptance

Doc 29 §9.23's mute test is this doc's acceptance tier for evidence
visuals: mute the narration, screenshot, hand to a stranger — any ink
needing the voiceover fails. Template-enforced constraints are
preferred over checklist items (a rule in code cannot be forgotten).
