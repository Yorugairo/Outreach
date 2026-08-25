---
id: P10-PORTABLE-SCRIPT-PATTERN
title: Portable script pattern + prompt guides (full 30-minute map)
status: draft
operation: feature
risk: standard
owner: parent
branch: claude/content-generation-system-52f077
created: 2026-08-24
updated: 2026-08-24
---

# Portable Script Pattern + Prompt Guides

## Summary

Turn the fused doctrine (classical spine from doc 32 + platform fill from
doc 31 + voice/persona 33/36 + delivery 37, first assembled in doc 38) into a
**portable, deterministic script-generation kit**: a full-video pattern map
scaling to 30 minutes, per-phase prompt guides with fill-in slots, and
mechanical QC lints. Portable means the kit runs with zero repo-private
references — persona, voice, evidence, and runtime are injected parameters,
so the same kit drives this channel, the BJJ lane, or any future lane.

Operator scaling rule, adopted as the kit's core geometry: **the map is
ratio-based, not minute-based**. A 30-minute reference timeline is the
worked example; anything longer "we just repeat the process or increase
pattern ratio" — Act-II gap/reflection pairs repeat, phase boundaries hold
as percentages.

## Intent And Acceptance

- A writer (human, this session, a fresh session, or `write_script_v2` +
  persona pass) can produce a doctrine-conformant script of any length
  8–30 min from the kit alone, without reading docs 31–38.
- Phase 1 (doc 38 §2) is the quality bar: every phase reaches that beat-level
  specificity, with timing, craft citations, voice constraints, pause marks,
  visual counterpoint directives, and a QC line.
- Mechanical QC gates run as code and fail loudly (same pattern as the pause
  compiler).
- Accepted when: the map retro-fits the two existing scripts (Alicia v2
  3:00; the 16:21 p34 cut) with deviations *explained*, and one new
  work-order-driven script passes all lints.

## Scope

1. **Full-video map** — six phases, ratio-based with a 30:00 reference
   timeline, beat-level throughout:
   - P1 THE OPEN (0–5%; 0:00–1:30 @30min) — already specified (doc 38 §2);
     port into the kit with ratios.
   - P2 THE ENGINE (5–17%; 1:30–5:00) — Catalyst & Debate; anecdote engine
     dominant; rehook slot at the 3:00 positional mark; STR micro loops
     begin; tricolon momentum.
   - P3 THE GAP (17–45%; 5:00–13:30) — the repeatable **pattern unit**:
     macro STR loop = anecdote run → gap opens (BUT) → partial resolve
     (THEREFORE) → reflection beat → rehook. 2–4 units depending on runtime;
     this is the block that repeats for longer formats. Point ordering
     (best evidence mid-video), anaphora across progressive points,
     breathing-room dip once per unit.
   - P4 MIDPOINT PIVOT (45–55%; ~13:30–16:30) — false peak or false
     collapse; stakes raise; sentence-length contraction; pre-key pause
     before the reversal; visual register shift; mid-video positional
     rehook.
   - P5 REFLECTION & CONVERGENCE (55–85%; 16:30–25:30) — reflection engine
     dominant; chiastic center (the transformative thesis); foreshadowed
     payoff (hook → ~20% → ~55%) culminates; second gap unit if T3 runtime;
     savor beats carry post-key silence.
   - P6 THE CLOSE (85–100%; 25:30–30:00) — ring echo (opening image
     transformed); Self-Revelation → New Equilibrium; final anaphoric
     triad; Peak-End; Action Window; ONE CTA; falsifiable tell restated
     with its threshold.
2. **Per-phase prompt guides** — for each phase: inputs consumed, beat
   template with slots, craft rules inline (no doc references), QC line,
   worked micro-example.
3. **Kit packaging** — `docs/content-video-engine/patterns/SCRIPT-PATTERN-KIT.md`
   plus per-phase guide files; an INJECTION.md defining the parameter
   surface (voice profile block, persona theses, evidence refs, runtime
   tier, format, entity seed, falsifiable tell).
4. **QC lint script** — mechanical gates: sentence-length stats, passive
   scan, fragment-stack detection, CTA count, pause-mark placement, rehook
   positional presence, tautology heuristic (narration token overlap with
   shot direction), ring check (opening-image tokens recur in close).
5. **Validation retro-fit** — map both existing scripts; record deviations
   in the kit's CHANGELOG section.

## Not Building

- No new video production; no TTS spend beyond existing standards.
- No fine-tuning or model training; the kit is prompts + lints.
- No skill-registry packaging yet (a `script-pattern` skill is a possible
  follow-on once the kit stabilizes).
- No changes to `scene_evidence_timeline.v1` (macro-loop encoding remains
  the separate open follow-up in doc 28).

## Human Gates

1. **Brainstorm session BEFORE T1 freeze** — operator requested a working
   session over the published research
   (https://claude.ai/code/artifact/bda7ae5b-bee8-43f6-9bc4-fbb95bc2c7c3).
   Learnings land in the map before ratios are fixed.
2. Operator approves the phase ratios and the repeat rule after T1.
3. Operator eyeballs one full generated beat sheet before T4 lints are
   treated as the gate of record.

## Mandatory Reads

- docs/content-video-engine/38-SCRIPT-ARCHITECTURE.md (phase-1 bar, work order v1)
- docs/content-video-engine/31-FACELESS-CHANNEL-DOCTRINE.md · 32-WRITING-FOR-THE-EAR.md
- docs/content-video-engine/33-VOICE-PROFILE.md · 36-WRITER-PERSONA.md · 37-TTS-DELIVERY-STANDARDS.md
- docs/research/2026-08-24-writing-for-the-ear-craft-source.md (blueprint table)

## Execution Path

Parent-led, inline (docs + one small python lint). Brainstorm (gate 1) →
T1 → gate 2 → T2–T3 in sequence (T2 depends on T1 ratios; T3 packages) →
T4 in parallel with T3 → T5 validation → gate 3 → complete.

## Patterns To Mirror

- Beat-level spec style: doc 38 §2 (function + rules cited + QC line).
- Deterministic contract style: registration WORK-ORDER.md (inputs table,
  per-item rules, self-check list, honest-empty allowance).
- Lint style: `compile_pause_marks` ration warning; validator style:
  `validate_slide_registration.py` (reject loudly, list errors, exit code).

## Task Slices

### T1: Full-video map (ratio-based, 30:00 reference)
- Status: done (pending gate-2 ratio approval)
- Owner: parent
- Depends on: brainstorm gate — SATISFIED via highlighter session (12 marked
  passages) + operator direction: "fill in the Macro 6 with ALL of the
  expected micro hook/callback/CTA rules… extending McKee to the YouTube era"
- Write set: `docs/content-video-engine/patterns/FULL-VIDEO-MAP.md`
- Acceptance: all six phases at doc 38 §2 beat-level; ratios + repeat rule
  explicit; every beat carries craft citation, voice constraint, pause
  marks, counterpoint directive
- Validate: manual read against doc 38 §2 bar; gate 2 approval
- Evidence: FULL-VIDEO-MAP.md v1 committed 2026-08-24 — 6 phases at micro
  density, extended unit hierarchy (line→beat→loop→unit→phase→video→
  catalogue), duty roster with counts, scaling law (open/close absolute,
  midpoint pinned 45–55%, P3 units elastic, >30min mini-pivot rule)

### T2: Per-phase prompt guides
- Status: pending
- Owner: parent
- Depends on: T1
- Write set: `docs/content-video-engine/patterns/phase-guides/P1..P6.md`
- Acceptance: each guide is self-contained (no doc references in the
  operative text), slotted, with a worked micro-example
- Validate: a fresh-context generation test on P1 alone produces a
  conformant 90-second open
- Evidence: pending

### T3: Kit packaging + injection surface
- Status: pending
- Owner: parent
- Depends on: T2
- Write set: `docs/content-video-engine/patterns/SCRIPT-PATTERN-KIT.md`,
  `docs/content-video-engine/patterns/INJECTION.md`
- Acceptance: kit references zero repo-private paths; injection parameters
  fully enumerated with examples for two lanes (finance, BJJ)
- Validate: grep for repo paths in kit files returns none
- Evidence: pending

### T4: QC lint script
- Status: pending
- Owner: parent
- Depends on: T1 (gate list), parallel with T3
- Write set: `content/video_engine/scripts/lint_script_pattern.py`,
  `content/video_engine/tests/test_lint_script_pattern.py`
- Acceptance: TDD; lints per Scope §4; exit 0/1 with listed findings
- Validate: `python -m pytest content/video_engine/tests/test_lint_script_pattern.py -q`
- Evidence: pending

### T5: Retro-fit validation
- Status: pending
- Owner: parent
- Depends on: T1, T4
- Write set: `docs/content-video-engine/patterns/FULL-VIDEO-MAP.md` (CHANGELOG section)
- Acceptance: Alicia v2 and the 16:21 p34 cut mapped; every deviation
  explained or logged as a map fix; lints run on Alicia v2
- Validate: lint output attached as evidence
- Evidence: pending

## Verification

- T4 pytest suite green; lint run on Alicia v2 recorded.
- Fresh-context P1 generation test (T2 validate) reviewed by operator.
- Grep portability check (T3) clean.

## Evidence And Handoff

Evidence accumulates in this file per slice. Handoff artifact is the
`patterns/` directory; first consumer is the next script (answer-format
video, doc 35), which should be produced from the kit rather than by hand.
