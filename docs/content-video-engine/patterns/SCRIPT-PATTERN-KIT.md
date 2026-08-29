# SCRIPT PATTERN KIT

A portable, deterministic script-generation kit for long-form narrated
video. Classical narrative architecture carries the video; platform
retention micro-rules fill every minute inside it; a lane's voice,
persona, and evidence enter only as injected parameters. The kit runs with
zero private references — the same files drive a finance channel, a BJJ
channel, or any future lane.

## Contents (the kit is exactly these files)

| File | Role |
| --- | --- |
| `LLM-CONTEXT-CLASSICAL.md` | Layer 1 — the timeless craft context (broadcast mechanics, story machinery, rhetoric, documentary VO, ring composition), densified for LLM injection |
| `INJECTION.md` | Layer 3 — the parameter surface: everything channel-specific, one block per script |
| `phase-guides/P1.md` … `P6.md` | The six generation contracts — beat templates, mandatory device slots, hard gates, QC lines, worked micro-examples |
| `STRENGTH-LOOP.md` | **The loop**: gates at every scale L0-L6, the cross-scale checks, the fixpoint protocol, precedence, the rewrite budget |
| `SENTENCE-STRENGTH-CHECK.md` | The L0 line gate: ten per-sentence strength checks run after structure conforms, before audio; every failing sentence is rewritten until it passes, with a logged audit trail |
| this file | The binder: flow, geometry, duty roster, changelog |

Layer 2 (the platform micro-rules) is not a separate file: it is already
fused INTO the phase guides — that fusion is the kit's entire point.

## The generation flow

```
1. ASSEMBLE the injection block (INJECTION.md) — editorial decisions,
   standing voice/persona blocks, verified evidence.
2. RUN P1 → P6 in order. Each phase consumes: the injection block, the
   previous phase's LEDGER, and its own guide. Each emits: its script
   section + the updated ledger. Never let a phase read ahead or behind.
3. ASSEMBLE the six sections. The final ledger audit (P6) must show every
   loop closed, the ring sealed, and the CTA budget respected.
4. LINT the assembled script (mechanical gates: sentence stats, passive
   scan, CTA count, pause-mark ration, tautology, ring check). Fix and
   re-run until clean.
5. STRENGTH LOOP (STRENGTH-LOOP.md): run every scale L0-L6 AND the
   cross-scale checks X1-X5, apply fixes, and repeat to a FIXPOINT — a
   round that fires no gates but made an edit runs again, because the edit
   is what may have broken something nothing checked yet. Sentence
   strength (L0) is one scale of seven; phrase (L1), beat (L2) and section
   (L3) gates live in the loop doc. Log every rewrite.
6. JUDGE BY EAR: synthesize a scratch voiceover and listen before
   production. Page-conformance is necessary, never sufficient.
```

The ledger is the determinism mechanism: ring token, foreshadow schedule
(F1/F2/F3), open-loop list, head-fake, anaphora arc, and emotional track
travel as explicit state, so any writer — human, fresh LLM session, or a
different model — continues the same video.

## Geometry (the scaling law)

- **Absolute, every runtime:** the OPEN is 60–90 seconds (60 at 8 min);
  the true CLOSE is 60–90 seconds plus a 20-second end screen; the
  MIDPOINT PIVOT is pinned at 45–55% of runtime.
- **Elastic:** P3's pattern unit (2:00–2:30) is the runtime knob.
  Unit count ≈ `ceil((runtime_min − 9) / 2.5)`, minimum 1.
- **Beyond 30 minutes:** repeat the process — extra P3 blocks alternate
  with mini-pivots every ~12–15 minutes; ONE true midpoint, one grand
  payoff, one ring.
- **Short runtimes MERGE systems, never drop them:** at 3:00, the
  reversal, the mid-video rehook, and the head-fake demolition are one
  construction; the promise, the paradox, and the ring are never cut.

| Phase | Owns | @30:00 | @16:00 | @8:00 |
| --- | --- | --- | --- | --- |
| P1 OPEN | microhook · paradox · dated promise (F1) · map · ring plant | 0:00–1:30 | 0:00–1:15 | 0:00–1:00 |
| P2 ENGINE | catalyst · head-fake plant · A3+F2 · macro-1 close · only micro-CTA slot | 1:30–5:00 | 1:15–3:00 | 1:00–2:15 |
| P3 GAP | pattern units · F3 · anaphora arc · best evidence banked→spent | 5:00–13:30 | 3:00–7:15 | 2:15–3:30 |
| P4 PIVOT | reversal=A4 · head-fake demolition · token recontextualized | 13:30–16:30 | 7:15–8:45 | 3:30–4:30 |
| P5 REFLECTION | thesis · grand payoff (60–70%) · loops closed LIFO · the tell | 16:30–26:00 | 8:45–14:00 | 4:30–6:45 |
| P6 CLOSE | ring echo · final triad · one CTA · assignment · hard stop | 26:00–30:00 | 14:00–16:00 | 6:45–8:00 |

## The duty roster (what must exist, counted, @30:00)

| System | Count | Placement |
| --- | --- | --- |
| Rehooks | 4 anchors + 1/unit (≈8) | A1 ~0:30 · A2 ~1:00 · A3 ~10% · A4 = pivot · unit exits |
| Foreshadows | 3 → 1 delivery | F1 hook · F2 ~10% · F3 ~27% → payoff 60–70% |
| Macro loops | 5–8, closed LIFO | open P1–P3 · close P5 in reverse |
| Micro story loops | ~20–30 | every phase, 30–60s cadence |
| Callback tokens | 2–4; ring anchor closes LAST | plant P1–P2 · touch P3 · recontextualize P4 · close P5–P6 |
| Head-fake | ≥1 | planted P2 straight · demolished at the pivot |
| CTAs | ≤1 micro + 1 outro (0 in serialized segments) | P2 post-payoff window · P6 action window |
| Breathing dips | 1/unit + post-macro-1 | P2–P5 |
| Savor beats | ≥2 | P5 |
| Tricolons | **terminal, not rationed** | the P6 triad lands last and hardest; no tricolon after it; none decorative |
| Anaphora arc | 1 — constant opening, evolving tails | debut P1/P3 · recur ≥3× · resolve ONLY in P6's triad |
| The tell | exactly 1, four parts | P5, post-payoff |
| Ring echo | exactly 1, token-verifiable | P6 |
| Glass ratio | stated per phase | 80/20 → 70/30 → 60/40-in-unit → 50/50 → 30/70 → 40/60 |

**Tricolon gate — corrected 2026-08-29.** This was "≤3 total," which was
gating the wrong thing. The count existed to protect the closing triad's
impact, but a cap does not do that: an episode whose *content* is triadic
(a three-question test, "scarce, cash, used") burns the budget on substance
and reads as a violation while the close is untouched.

The real rule is **terminal placement and escalation**, not scarcity:

- Structural tricolons are unlimited. If the idea has three parts, say three.
- **The P6 triad lands last and hardest.** Nothing triadic follows it.
- No decorative tricolons — a three-beat list that would read the same as
  two is padding, and padding anywhere lowers the ceiling at the close.

Gate the close, not the count.

## Hard gates (fail the script, not the line)

1. **Attribution-first** — source before assertion, every claim, every
   phase. Unverified claims carry `[verify]` and are banned from hook,
   promise, reversal, payoff, and tell.
2. **The score** — one idea per sentence · active S-V-O · **10–15 word
   average in a wave** (corrected 2026-08-29: 15–16 was a written-prose
   figure; 15–20 is where listener comprehension falls off. Gate the
   SPREAD too — stdev ≥3.5, ≤12% of sentences past 20 words) · terminal
   stress on beat-final lines · punctuation as performance notation ·
   `[pre-key]`/`[post-key]` rationed ≈3/min.
3. **Counterpoint** — narration never captions its own visual. Per-phase
   modes: irony → contextual mapping → subtext → register shift →
   abstract synthesis → ring symmetry.
4. **CTA budget** — see roster. Three asks is zero conversions.
5. **The triple test** — every line answers: which structural node am I
   serving, which retention duty am I discharging, at what scale does my
   device repeat. Lines that answer none get cut.

## Output contract (what a finished script contains)

- Narration with pause marks (`[pre-key]` / `[post-key]`) and `[verify]`
  flags — nothing else in square brackets.
- Stage/visual directions in `**[...]**` blocks, one per beat cluster —
  the tautology lint compares these against their narration.
- Figures written out as speech ("two hundred and forty five thousand");
  verbatim strings and exact numerals live on on-screen badges only.
- A sources block: every figure → its source.
- The final ledger audit from P6.

## CHANGELOG

- v1 — kit assembled: binder + injection surface + six phase guides.
  Fresh-context P1 generation test passed on an unseen topic (correct
  geometry, original ring token, budgets held, complete ledger).
- v1.1 — SENTENCE-STRENGTH-CHECK added as flow step 5. Validated by A/B
  ear test on the first production script: matched segment pairs (open,
  pivot, close), identical voice/settings/seed — the strength-passed arm
  won by ear and ran ~4% shorter at identical content. The pass is
  standing, not optional.
