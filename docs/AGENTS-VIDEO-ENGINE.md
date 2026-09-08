# AGENTS — Content video engine (the doctrine section)

Moved out of the always-loaded `AGENTS.md` on 2026-09-05 (P45 grill: the dispatch floor). Every subagent dispatch re-paid this section; the parent and any agent doing script, visual, evidence or channel work loads it once via the pointer in `AGENTS.md`. Nothing here changed.

## Content video engine (second workstream)

This repo also hosts a faceless YouTube production operation (three
channels: Money Physics, Building Money, Martial Matters). It is a
separate workstream from the SEO platform above and has its own doctrine.

**Any agent doing script, visual, evidence, or channel work loads these
two files first — they are model-agnostic and are the source of truth:**

- [`docs/portable/DOCTRINE-CORE.md`](docs/portable/DOCTRINE-CORE.md) —
  ~10k chars, always loaded: channels, narrator, retention clock,
  six-phase architecture, sentence gates, packaging, production
  standards, never-list. Sized to paste into any system-instruction box.
- [`docs/portable/OPERATOR-RULINGS.md`](docs/portable/OPERATOR-RULINGS.md)
  — the standing corrections ledger; each ruling carries the reason it
  was made, because the reason is what generalizes.

- [`docs/portable/VOICE-PACK.md`](docs/portable/VOICE-PACK.md) — loaded
  before writing any narration, title, or description. Voice transfers by
  exemplar, not description: a rejected/accepted hook pair, the five
  hardest lines from an approved script, and the ear-judgments converted
  to text-checkable rules.

Task routing into the deeper doctrine, plus the work-order interop
contract, is in [`GEMINI.md`](GEMINI.md) — that routing table applies to
every agent, not just Google-side ones.

**The assembly process itself is one page:
[`docs/content-video-engine/PIPELINE.md`](docs/content-video-engine/PIPELINE.md)
— the eight stages (write → strength loop → lint → audit → record → word
timeline → shot table → render), what owns each, what consumes what, and
the capability index it opens with. Read it before building anything;
the renderer, the player and the gates already exist. Enumerate before
you grep. Lane capabilities are stated from the docs and the template,
never from memory - cite the file (CHECK-RESPONSIBILITIES R9).**

**Three spine documents sit behind that table. Know they exist before
doing script, review, or motion work — they were unrouted until
2026-09-02 and lived on one branch only:**

- [`docs/content-video-engine/patterns/FULL-VIDEO-MAP.md`](docs/content-video-engine/patterns/FULL-VIDEO-MAP.md)
  — **the script spine.** The classical six-phase architecture (Truby /
  McKee / Snyder / Glass / ring composition — the integral) fused with the
  platform retention micro-rules (the differentials) at every 15–90s
  interval. The phase guides `P1–P6` and the strength loop derive from it;
  `patterns/KNOWLEDGE-GRAPH.md` is the same graph laid out by relation.
- [`docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md`](docs/content-video-engine/patterns/CHECK-RESPONSIBILITIES.md)
  — **who checks what.** Three verdict kinds (mechanical / declared /
  JUDGE) decide whether a tool or the runtime agent owns a verdict; §2
  tables the four checkers (`lint_script_pattern.py`,
  `audit_script_doctrine.py`, `gate_opening_structure.py`,
  `enumerate_strength_screens.py`); §3 names everything the agent must
  verdict by hand; §5 fixes the report format. A tool's verdict is final;
  a declared tag is a claim the agent verifies; a report missing a block is
  not a review.
- [`docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md`](docs/content-video-engine/29-EVIDENCE-MOTION-STANDARDS.md)
  — **motion and evidence choreography, the production bar for every
  channel.** Part 3 is the linked-evidence choreography (the chain is the
  transition), Part 8 the scene-evidence lane that ships, Part 9 the
  operator corrections, §9.15 the cross-reveal wipe and caption safe zone.
  Docs 15 (living-scene language) and 16 (editorial motion system) were
  COMPRESSED into it (2026-09-05 ruling: compression, not supersession -
  `docs/DOC-OVERLAP.md` lists what 29 does not carry); where they disagree on
  motion, 29 wins, and the lifted rules are 29 §9.32. The renderer is
  `samples/scene-evidence-player.template.html`; do not write another.

Three rules bind agents generating assets here:

1. A dispatched `WORK-ORDER.md` is **frozen**. Corrections open a new
   claim; never patch an order a running agent already holds.
2. Output stays in **review quarantine** until the operator approves a
   contact sheet. Free generation does not remove the review step.
3. `approved` is set by the operator, never by product code, and figures
   are never fabricated — unverified claims go under SOURCES-TO-VERIFY.
4. **Recall before you build** (2026-09-08): a proposal, a "try", an iteration or a "review
   the docs" opens with `Recall:` lines from `docs_find` before anything is built - the order
   (docs_find → rulings → capabilities/registries → the research bundle → a Gemini research
   WORK-ORDER over the bridge, scoped as a QUESTION, never a design, its answer quarantined)
   and the commit hook are in `docs/runbooks/RECALL-RECEIPT.md`. Inspect AND measure the
   output before delivering it. Subjective media edits: 2-3 cheap preview candidates first;
   image generation is cheap.
