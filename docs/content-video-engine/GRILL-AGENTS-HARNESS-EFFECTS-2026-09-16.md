# BLUEPRINT - how agents harness the effects, the capabilities and the docs (the grill of 2026-09-16)

The question: *"how would you improve our capabilities further and ensure that agents actually harness the strength of our effects,
capabilities, and documentation?"* Asked after one-shot #3 (E99 s66 / s67): the docs existed and the parent skipped layers; the gates
measured counts and passed a regression; the authoring kit handed the agent a blank shot table. The research spike is
appendix A below (docs/research/runs/ is gitignored - the record lives here, beside GRILL-PIPELINE-VALUE-2026-09-13.md). The operator's six answers are E99 s68.

## Settled decisions

1. **The approved shape lives in the kit AND the gate (Q1 = C, A first).** A SHAPE COMPILER in `scripts/authoring/` takes the
   per-sentence beat plan (the sentence acts, the comparators, the words the numbers land on) and emits the approved skeleton: the
   page on the hook drawing on its axes, a MOUNT for any page whose number lands 7 s or more in, axes entries elsewhere, the dip for a
   world change, the suck or cut page to page, the spiral return for the ring, docks that read then park in the page's own room, a
   plate's six seconds. A parity-by-mechanism gate (M45) backstops it: present / absent / replaced by what, per approved mechanism.
2. **The compiler's output is the BASE, not the answer (Q4 = A, amended).** The compiler holds several approved skeletons per beat
   shape and chooses by the sentence act and a variety rule - no signature twice running, the approved shorts' own mix as the target
   distribution, a variety row (M46) beside the parity row. The operator: *"the compiler outcome doesn't have to be the final solution,
   the agent can use it to establish the base of the video and then modify"* - the agent edits the generated rows (the override
   sidecar and the table are already the two doors), and every departure from the base is a named decision in the ledger.
3. **The combination knowledge is built by the RECIPE LAB, batched, with approvals and denials tracked (Q2 = C, amended).** The lab
   enumerates beat shapes x the catalogue's members x the gates' clocks (M44 6 s, M16 2.5 s, M12 6 s, M11 1.5 s, the page's 7.4 s
   build), builds each on the Tokyo test bed, keeps what passes the gates and the probe, and presents the survivors to the operator
   AS BATCHES - one card per beat shape, the candidates side by side. The operator: *"present as batches, and track approvals and
   denials so agents can start learning what make combinations work."*
4. **The approval log teaches rather than freezes (Q5 = B).** Each judgement records the bit, a reason category from a short list,
   the instant of proof (the clip and the second), and a timestamp; each batch keeps a fixed exploration share of about a quarter
   drawn regardless of predicted approval; older approvals return as calibration probes; the learner is a per-feature approval-rate
   table with shrinkage over beat shape, member set and clock - no ranking model until the table is in the hundreds.
5. **Agents are held to the docs by a VERIFIED receipt and a director-critic (Q3 = C, Q6 = C).** The build refuses without a
   per-stage `Recall:` block (package, script, voice, world, evidence, motion, sound, publish, the rulings); the verifier re-reads every
   cited path and line, matches a quoted span verbatim, refuses on a miss, re-runs any zero-hit claim, and refuses a STAGE with no
   citation at all. The reviewer role reads the built cut against the mechanism list before the queue and reports two scores -
   mechanism correctness and attribution quality - never one verdict.

## Rejected alternatives
- The agent authoring every row from scratch with recall alone (Q1 B): one-shot #3 is the counter-example - the docs were read and
  the mechanisms still went unused.
- One skeleton per beat shape (Q4 B): the spike's gotcha - a compiler whose choreography vocabulary is smaller than the sentence-shape
  vocabulary converges every cut; a parity gate cannot see repetition.
- Mining the approved cuts only, no new combinations (Q2 B): the approved set is three shorts and one long; the lab is the only route
  to combinations nobody has authored.
- A bit per card as the log (Q5 A): teaches nothing about WHY; pairwise cards from the start (Q5 C): Bradley-Terry needs data the queue
  does not collect and is not required at this scale (arXiv 2411.04991).
- A text-only receipt (Q6 A): a fabrication surface; the evidence supports retrieval, not typed citations, as the behaviour change.

## Verified gotchas and their mitigations
- **Templated reads as templated** (INFERRED from the token -> preset -> choreography pattern): several skeletons per shape, the
  variety rule and M46, the agent's edits on the base.
- **Goodhart at small samples** (Gao et al. 2022): the exploration share; the reason category; the proof instant so a stale approval is
  re-judged, never trusted forever; recency-weighted fits when the table grows.
- **Taste drift, one judge over months** (INFERRED): calibration probes - a previously approved candidate re-presented now and then.
- **Citation is not grounding** (arXiv 2606.04990): the verifier matches the quoted span; the critic scores attribution separately from
  correctness; claim-level, never document-level.
- **The floors contradict the proven set** (R26-168, from the one-shot): the lab re-proves the recipes on six-second plates and built
  pages before M38 is held at 0.60 again; until then M38 prints its number and the parity row (M45) is the floor.

## Immediate build order (three plans, in this order)
1. **P65 - THE RECIPE LAB** (R26-176): the enumerator (beat shapes x members x clocks), the test-bed builder, the gate + probe filter,
   the batch cards (one per beat shape, candidates side by side, the exploration share), the approval log's four fields and the
   approval-rate table, the promotion to `docs/EFFECTS-CATALOG.jsonl` as proven recipes with offsets - and the re-proving of the
   thirteen proven recipes on today's clocks (R26-168).
2. **P66 - THE SHAPE COMPILER** (the kit): the beat plan's schema as its input; several skeletons per beat shape from the lab's proven
   set and the approved cuts; the variety rule; the generated rows as a base the agent edits through the table and the sidecar;
   M45 parity by mechanism and M46 signature variety in `gate_one_shot_floor.py`; the one-shot runbook's step 5 becomes "generate,
   then modify - and name every departure".
3. **P67 - THE VERIFIED RECEIPT AND THE CRITIC**: the per-stage `Recall:` block the build refuses without, its verifier (path, line,
   quoted span, the stage list, zero-hit re-runs) grown from `scripts/hooks/recall_receipt.py`, and the reviewer's two-score read
   before the queue; `build_caption_pages.py` and the other authoring modules added to the hook's mechanism list.

Then the Opus one-shot runs on the compiler's base (E99 s66 step 2), and Astra's after it in its own worktree (P62).

---

# Appendix A - Grill: how agents harness the effects, capabilities and docs - research spike r1 (2026-09-16)

Run by a docs_researcher lane (three web searches, read-only); the lane could not write under docs/research, so the parent
saved its report here verbatim. Tiers: CONFIRMED (a source says it), PLAUSIBLE (second-hand, the source 403'd), INFERRED.

## Three bullets
- **Gotchas** - citation is not grounding: document-level citations "hide unsupported or partially supported claims" (arXiv 2606.04990, 2026-06-03); at small approve/deny scale, optimising an imperfect preference proxy "can hinder ground truth performance" (Gao et al. 2022, Goodhart); motion tokens standardise easing and duration so only the choreography varies, and that is where templated cuts read templated.
- **Precedents** - LottieFiles Motion System: governed motion primitives applied and bulk-updated across a comp (a catalogue + compiler shipping today); motion design tokens (Gonzalez 2021) encode intent, the author keeps only the choreography; Remotion: a composition = a component + metadata (the shot table's analogue); preference side: Bradley-Terry and contextual bandits over arms-in-context.
- **Limits / costs** - Bradley-Terry wants pairwise comparisons and an approve/deny log is not that; arXiv 2411.04991 (rev. 2025-01-26): BT is "not necessarily required" - an order-consistent binary classifier suffices, cheaper at tens of labels. Receipts cost tokens and can be fabricated; they need verbatim verification and claim-level (not doc-level) attribution.

## 1. Motion as composable timed primitives; a skeleton from a script
- CONFIRMED - LottieFiles Motion System (lottiefiles.com/plugins/after-effects): "governed, centralized motion primitives" - easings, presets, brand assets; "Smart Apply" updates matching styles in bulk.
- CONFIRMED - Gonzalez, "Animation/Motion Design Tokens", 2021-03-14 (prototypr.io): a token "conveys intent" (easing + duration); the designer keeps "the choreography of the animation" - what triggers, what animates, which tokens, when.
- CONFIRMED - Remotion fundamentals: "A composition is the combination of a React component and video metadata".
- INFERRED - the industry pattern is token -> preset -> choreography. A shape compiler automates the choreography layer; the templated-reads-as-templated failure lands on the compiler, not the catalogue: if its choreography vocabulary is smaller than the sentence-shape vocabulary, every cut converges. A parity-by-mechanism gate detects a MISSING mechanism, not a REPEATED one - variety across the shot table is a separate measurement.
- Not found: a published, named script-to-skeleton generator from a studio (Bravos-style explainers are documented as output, not tooling).

## 2. Preference learning from approve/deny at tens to hundreds of judgements
- CONFIRMED - "Rethinking Bradley-Terry Models in Preference-Based Reward Modeling", arXiv 2411.04991: a reward model "only needs to preserve the correct ranking predictions through a monotonic transformation of the true reward"; an upper-bound algorithm "compatible with off-the-shelf binary classifiers", grounded in "order consistency".
  - INFERRED: at this scale skip BT/Elo - a regularised binary classifier, or a per-feature approval-rate table with shrinkage toward the prior, over recipe features (beat shape, member set, clock) is order-consistent and needs no pairwise data.
- CONFIRMED - Gao, Schulman, Hilton, "Scaling Laws for Reward Model Overoptimization", arXiv 2210.10760: "optimizing its value too much can hinder ground truth performance, in accordance with Goodhart's law"; worse at small dataset sizes.
  - INFERRED: a lab that only batches survivors of the learned model stops sampling the space and freezes the operator's early taste - keep a fixed exploration fraction (about 20-30 % of each batch) and log the denial REASON, not just the bit.
- CONFIRMED (framing) - contextual bandits: "prompts represent context, responses correspond to arms" (arXiv 2307.12975 / 2406.09574) - beat shape = context, recipe = arm, approval = reward.
- INFERRED - taste drift (a single judge over months) is unaddressed in the sources; practical mitigations: recency-weighted fits, re-presenting previously approved items as calibration probes, storing the INSTANT OF PROOF with each approval so a stale approval is re-judged, never trusted forever.
- Limit: no paper on N of 50-500 single-annotator tables; the scale-specific advice is INFERRED.

## 3. Enforced "read before you build"
- CONFIRMED - "From Agent Traces to Trust", arXiv 2606.04990 (2026-06-03): "answer correctness should be separated from evidence support and attribution quality"; "claim-level attribution is especially important because document-level citation may hide unsupported or partially supported claims".
- PLAUSIBLE (403'd) - Blackburn, "Exploring LLM Citation Generation In 2025": ~30 % of statements unsupported, ~25 % of citations not supporting the response - unverified, do not quote as measured.
- CONFIRMED (adjacent, positive) - "Documentation Retrieval Improves Planning Language Generation", arXiv 2509.19931: retrieving documentation improves the generated output - the retrieval carries the gain, not the citation text.
- INFERRED, load-bearing for decision (3): the literature supports retrieve-before-build and provenance as an AUDIT layer; it does not support "making the model type a citation" as a behaviour change. A text-only receipt is a fabrication surface; it earns its keep only if a verifier re-reads the cited span and matches it verbatim, and 0-hit claims are re-run. A director-critic pass should score mechanism correctness and attribution quality as two axes, never one verdict.

Sources: arXiv 2411.04991; arXiv 2210.10760; arXiv 2307.12975; arXiv 2406.09574; arXiv 2606.04990; arXiv 2509.19931; medium.com/@prestonblckbrn (403); prototypr.io/post/animation-design-tokens; lottiefiles.com/plugins/after-effects; remotion.dev/docs/the-fundamentals.
