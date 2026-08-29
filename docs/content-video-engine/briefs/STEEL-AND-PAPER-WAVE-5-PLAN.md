# Steel and Paper — wave 5 state (plates + evidence)

**Script D is assembled and linter-clean.** `SCRIPT-D-VO.txt`, 11,188 spoken
characters, **11m 38s** at the measured 16.02 chars/sec.

| | |
|---|---|
| Pivot position | **49.2%** — dead centre of the 45–55% pin (doc 38) |
| Plates usable | **56** → **12.5s each** (ceiling 20, target 12) |
| Evidence available | **202 approved objects** — see §2 |
| Delivery | two-part chained take, split at P4→P5 |
| Blocking work | none — the review gate is cleared |

---

## 1. Script D — measured

Script C with the two extension units spliced on opposite sides of the pivot,
exactly as the units-D brief specified.

| Beat | at | position |
|---|---|---|
| Debt unit opens | 227s | 32.3% |
| **P4 pivot** — "the bubble isn't in the steel" | 347s | **49.4%** |
| P5 — "Now the test" *(chained-take split)* | 450s | 64.1% |
| Winner unit opens | 499s | 71.2% |
| The tell — the memory instrument | 577s | 82.2% |

Units on both sides of the pivot is what held the pin: loading them into P3
alone would have pushed it to ~76%.

Linter: **clean.** Sentence mean 10.5 words, 187 sentences, break ration
1.87/1k (limit 3.0), no stray editorial flags.

**Chained take.** 11,188 chars exceeds the mv2 10,000 cap. Split at
`Now the test — the one from the top.`:

| | chars | runtime |
|---|---|---|
| `SCRIPT-D-VO-part1.txt` | 7,155 | 447s |
| `SCRIPT-D-VO-part2.txt` | 4,032 | 252s |

Part two passes part one's `previous_request_ids` so prosody carries across
the join. This is the provider's supported long-form path, not the
splice-repair banned by doc 37 §8. Timeout 900s, attempts 1 (§8.1).

## 2. Evidence — the gate is cleared

Operator ruling, 2026-08-29: *"all of the evidence should be approved not
review only."* Applied across the whole library; record at
`content/video_engine/sources/decks/decks-operator-approval.v1.json`.

| Layer | Count | Status |
|---|---|---|
| Built documents (`steel-and-paper/evidence/objects/`) | 21 | ours, current palette |
| Teacher-stamped production visuals | 86 | `approved`, render-eligible |
| Deck slides (6 decks, original + cleaned) | 86 | `operator_verified`, render-eligible |
| Deck semantic crops | 9 | `operator_verified`, render-eligible |

**Four evidence species now, not one.** That is the point of having built our
own rather than only harvesting the decks:

| Species | Doc 39 | Examples |
|---|---|---|
| Chart | §6 | `ev-railway-index-v1`, `ev-krx-memory-v3`, `ev-debt-issuance-v2` |
| Table | §6 | `ev-three-manias`, `ev-mechanism-ladder` |
| Record document | §10.1 | `ev-doc-karp`, `ev-doc-macdonald`, `ev-doc-leases` |
| Instrument reading | §12 | `ev-instrument-memory` |
| Deck plate | 29 §9.3(c) | the 86 stamped visuals + 86 slides |

A viewer who sees a chart, then a typewritten filing, then our own
instrument, then a drawn mechanism reads four different *kinds* of proof.
That variety is what lets a single plate hold 20 seconds without going stale.

**What approval did not lift.** Three gates still bind and are recorded in
the approval record:

1. Per-asset `reuse_policy` caps — `max_total_uses`, `min_nonadjacent_gap`.
   Approval is not a licence to repeat an asset.
2. **Figure verification before docking** (doc 29 §9.3(c)). The decks predate
   the dossier. The comparison table still reads **"70% Crash"** for the
   railways; the verified figure is **64.1%**. The HBM slide's "committed
   through 2027 under binding contracts" is stronger than our sourced
   "essentially sold out for the year." Neither may air as drawn.
3. Doc 39 chrome rules for anything used as evidence on screen.

## 3. Plates — 56 usable, no wave 7 required

| Wave | Usable | Note |
|---|---|---|
| wave-1 | 9 | 2 superseded by wave-1b v2s, 2 retired for style drift |
| wave-1b | 2 | `spike-certificate-ring-v2`, `spike-rest-v2` |
| wave-3 | 22 | less `index-weights-v1` and `price-board-wiped-v1` (rejected), `broadcast-set-v1` (superseded by wave-4 v2) |
| wave-4 | 2 | `broadcast-set-v2`, `listing-barge-v1` |
| wave-5 | 15 | includes `world-molten-pour-v2` (the ladle swap) |
| wave-6 | 2 | `paper-and-steel-press-v1`, `signature-nib-v2` — Codex-approved, **operator review outstanding** |
| finance-episodes-wave-1 | 4 | `dram-terrain`, `korea-port`, `memory-fab-floor`, `seoul-fab-skyline` |
| **Total** | **56** | **12.5s average** |

12.5s is a hair over the 12s target and far inside the 20s ceiling — and the
average overstates the exposure, because evidence cut-ins carry a real share
of the runtime. Under the operator's own rule a plate may hold 20s when two
strong evidence pieces cover it, and with 202 approved evidence objects
there is no stretch that has to run bare. **Density is no longer the binding
constraint.**

## 4. Order of operations

1. ~~Wave-5 claim~~ — **delivered**, 15 plates.
2. ~~Clear the evidence review gate~~ — **done**, 2026-08-29.
3. ~~Assemble Script D~~ — **done**, linter clean, pivot at 49.2%.
4. Operator review of the two wave-6 plates.
5. Figure-verify each deck slide against the dossier *at docking time* —
   per slide, not as a batch pass.
6. **Chained master take.** Listen to the P4→P5 join before anything else.
7. Rebuild the scene-evidence timeline from the new word timings; check bare-
   plate stretches against 12s and confirm no evidence object exceeds its
   reuse cap.

## 5. Risks

- **The chained join sits at P4→P5**, immediately after the pivot. If prosody
  drifts it will be audible at the episode's most important seam.
- **The deck figures.** Approval cleared the rights and context gate; it did
  not verify the numbers. A registered plate that contradicts our own
  narration hands the viewer our error in typeset form. Verify per slide.
- **Reuse caps are easy to breach silently** now that 202 objects are
  eligible. The timeline rebuild in step 7 is the check, not a formality.
