---
id: P33-FIRST-FIVE-MINUTE-PLATE-AND-EVIDENCE-REPAIR
title: Repair first-five-minute plate directness and evidence coverage
status: review
operation: feature
risk: high
owner: parent
branch: codex/p31-semantic-evidence-and-word-timed-captions
created: 2026-08-16
updated: 2026-08-16
---

# First-Five-Minute Plate And Evidence Repair

## Summary

Replace weak opening world plates, bind whole teacher-stamped slides to the
remaining factual holds over six seconds through 5:00, and record the narrow
analogy exemption. World plates remain the hero; one evidence surface enters
at a time and remains on screen for up to five seconds.

## Intent And Acceptance

- The opening no longer renders `wrong-bubble-elevators-v2` or
  `belief-versus-support-v2`.
- Every factual world hold longer than six seconds that starts before 300s is
  covered by a whole approved teacher-stamped slide, or a recorded exemption.
- The bakery plate is an explanatory analogy and is explicitly exempt; its
  only future source-card match is the full Antidote capacity-penalty slide.
- Source cards are subordinate, uncropped, one at a time, mobile-safe, and do
  not display a source label.

## Scope

- Reuse `hero-wrong-bubble-v1` at 0.0–2.4s and
  `sentence-native-beat-02-003-next-buyer-belief-v1` at 64.876–70.901s.
- Produce a review-only `two-elevator-mechanism-v1` for 70.901–89.803s:
  cable-and-drive elevator versus an elevator moved by jumping passengers.
- Add the exact four approved whole-slide bindings: Reality Gap s12 at #07,
  Antidote s14 at #08, Antidote s02 at #09, and Memory Supercycle s06 at #23.
- Build a versioned 0–300s evidence-obligation report and grouped review sheet.

## Not Building

- No change to canonical narration, transcript timing, source-deck pixels, or
  factual approvals.
- No crop, generated factual text, publication, or Korea–Italy evidence work.

## Human Gates

- **Gate A:** approve the generated elevator contact sheet before it is
  registered as render eligible or inserted into the demo.
- **Gate B:** approve the revised 0–90s review render before extending the
  policy beyond the first five minutes.

## Mandatory Reads

- `docs/runbooks/PRP_EXECUTION.md`
- `P32-FULL-EPISODE-EVIDENCE-COVERAGE-AND-GENERATION.plan.md`
- `build_current_bubble_six_minute_p32_demo.py`
- `world-plate-evidence-caption-grammar.v1.md`

## Execution Path

1. Preserve the generated elevator plate as review-only and obtain Gate A.
2. Register approved world-plate substitutions with hashes, then compile the
   exact source-card bindings and first-five-minute obligation report.
3. Render only the Gate A-accepted asset map; retain a separate evidence and
   mobile contact sheet for Gate B.

## Patterns To Mirror

- P32's immutable review-cut props, whole teacher-stamped slide staging, and
  grouped plate audit.
- The world/evidence/caption hierarchy in
  `world-plate-evidence-caption-grammar.v1.md`.
- Existing sentence-native review manifests for candidate provenance and
  composition approval boundaries.

## Task Slices

### T1: Candidate plate and Gate A review packet
- Status: complete
- Owner: parent
- Depends on: none
- Write set: P33 candidate asset, candidate manifest, contact sheet
- Acceptance: a wordless, direct cable-versus-jumpers elevator plate retains a
  quiet off-center source-card slot and is clearly `review_only`.
- Validate: image dimensions/hash, no generated text, contact-sheet readability.
- Evidence: Gate A approved 2026-08-16. Candidate is bound to
  `32909801c43fb76c6eb16d8dcf1215a2a18f98f89cacf1d5390c6d53ddca03fc`
  by `p33-gate-a-two-elevator-review/two-elevator-mechanism-approval.v1.json`.

### T2: First-five-minute obligation contract and test
- Status: complete
- Owner: parent
- Depends on: T1
- Write set: six-minute review builder, obligation compiler, focused tests
- Acceptance: every >6s factual beat that starts before 300s is covered or has
  a named exemption; a missing card fails validation.
- Validate: focused Python tests and deterministic audit recompile.
- Evidence: 29 world beats / 34 evidence beats; all factual >6s holds starting
  before 300 seconds are `covered`, and the fixed-oven plate is `exempt`.
  Focused P33 tests: 3 passed.

### T3: Gate A-dependent cut binding and review render
- Status: complete
- Owner: parent
- Depends on: T1 Gate A, T2
- Write set: derived review props, staged assets, render/audit artifacts only
- Acceptance: the four explicit card bindings and both replacement worlds are
  visible in the review cut; no two evidence cards overlap.
- Validate: render hash, frame review, obligation report, mobile contact sheet.
- Evidence: `current-bubble-six-minute-p33-first-five-review.mp4`
  (360.043s, SHA-256
  `ACE2975D9FF7344CD011D74976E73B54189CB9AAE734DC7466BACEA5A092BCD1`),
  `p33-gate-b-review/p33-first-five-minute-review.html`, and
  `p33-first-five-minute-evidence-obligation.v1.json`. Five focused tests
  passed and the PRP validator passed on 2026-08-16.

## Verification

- Focused obligation tests: covered, analogy-exempt, missing-factual failure,
  no-overlap, whole-stamped source enforcement.
- Recompile audit twice and compare bytes.
- Validate 0–300 second cut has no weak-plate asset IDs and no unresolved
  factual hold over six seconds.

## Evidence And Handoff

- 2026-08-16: user approved the P33 implementation route: reuse approved
  plates where direct, generate only the elevator diagnostic, require first
  five-minute factual evidence coverage, and retain the bakery analogy
  exemption. Gate A remains required before the generated candidate enters a
  renderer.

- 2026-08-16: Gate A approved `two-elevator-mechanism-v1`. It is now
  hash-bound and composition eligible; the first-five-minute cut replaces both
  weak plate families, binds the four declared whole-slide evidence surfaces,
  and emits `p33-first-five-minute-evidence-obligation.v1.json`.

- 2026-08-16: Gate B packet is ready. The 0-90 second portion includes the
  three opening source-card reveals; the fourth explicit evidence binding is
  shown at 230.164 seconds. The first-five policy will not be extended past
  300 seconds until Gate B is reviewed.
